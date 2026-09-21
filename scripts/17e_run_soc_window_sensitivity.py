#!/usr/bin/env python3
"""Candidate runner for the v7.2 20--80 percent SOC-window sensitivity.

The default invocation performs read-only static authority validation and never
constructs a Gurobi model.  The six-case production path is reachable only via
``--execute-production`` and remains unauthorized until a separate independent
audit closes the implementation/build-only gates.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
import uuid
from contextlib import AbstractContextManager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.soc_window_sensitivity_adapter_v7_2 import (
    ADAPTER_VERSION,
    EXPECTED_R10_CORE_SHA256,
    EXPECTED_R10_CORE_VERSION,
    LINEAGE_ID,
    PARENT_LINEAGE_ID,
    SOC2080_SPEC,
    TECHNICAL_BREAKPOINTS,
    TECHNICAL_SEGMENT_WIDTHS,
    derive_active_segment_widths,
    load_isolated_r10_soc_core,
    required_nameplate_energy_kwh,
)


SCRIPT_VERSION = "v7.2-soc2080-sensitivity-runner-candidate-2026-09-21-r1"
EXPECTED_BRANCH = "thesis-v7"
EXPECTED_FUTURE_SENSITIVITY_OPTIMIZE_CALLS = 6
EXPECTED_FUTURE_COMPARATOR_OPTIMIZE_CALLS = 0
OUTPUT_ROOT_RELATIVE = Path("results/sensitivity/soc_20_80/runs")
EXPECTED_MAINLINE_PACKAGE_ID = "pnnl_v2024_lfp_2023_point_10mw_4to10h"
EXPECTED_MAINLINE_PACKAGE_SHA256 = "b8c461eb3513a2f6f05739a824d124e797aa7f59d12b1cf28b066bc391bcd5e2"
EXPECTED_CANONICAL_INPUT_SHA256 = "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e"
EXPECTED_17D_SHA256 = "9899bc0e2a24bbf6d01d8b2c5dd976142975eb48c7f05933a46b43477eabdb55"
EXPECTED_HELPER_SHA256 = "3f62fa290e1c8e1699c34d4b1bc78b9af0e716387b251afb4ada2b3198d7524f"
EXPECTED_RAINFLOW_SHA256 = "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2"
MIP_GAP = 1e-6
NUMERIC_FOCUS = 1
OUTPUT_FLAG = 1
TIME_LIMIT_SEC = None
TOL = 1e-6

SOLVER_CONTRACT = {
    "solver": "Gurobi",
    "mode": "binary",
    "MIPGap": MIP_GAP,
    "NumericFocus": NUMERIC_FOCUS,
    "OutputFlag": OUTPUT_FLAG,
    "TimeLimit": "INFINITY_UNSET",
    "NodeLimit": "INFINITY_UNSET",
    "automatic_retry": False,
    "tuning": False,
    "feasibility_relaxation": False,
    "warm_start": False,
}

ONE_FACTOR_CONTRACT = {
    "only_changed_factor": "SOC_WINDOW_10_90_TO_20_80",
    "package_id": EXPECTED_MAINLINE_PACKAGE_ID,
    "power_scale_bracket_mw": 10.0,
    "winter_pv_treatment": "MAINLINE_CONSERVATIVE_ZERO",
    "reserve_policy": "CONSTANT_WORST_CASE_CASE_SPECIFIC_REQUIREMENT",
    "outage_starts": "ALL_VALID_HISTORICAL_NONCIRCULAR",
    "outage_pv_surplus_recharge": False,
    "eta_c": 0.90,
    "eta_d": 0.90,
    "contract_capacity": "REGULAR_ONLY_SUPPLEMENTARY_ZERO",
    "monetary_basis": "constant NTD-2023",
    "discount_rate_real": 0.05,
    "analysis_horizon_years": 20,
    "tariff": "UNCHANGED_TAIPOWER_V7_2",
    "exact_d": "UNCHANGED_ACTIVE",
    "transition_settlement": "UNCHANGED_CANDIDATE1_EXACT_D",
    "degradation_calibration": "UNCHANGED_PNNL_XU_DERIVED",
    "rainflow_method": "UNCHANGED_EX_POST_VALIDATION",
}

PREEXISTING_ALLOWED_UNTRACKED = {
    "0629開會逐字稿Iris.docx",
    "Claude outputs/0930_進度報告_投影片架構與逐頁講稿_v7.2.md",
    "Claude outputs/P2_Literature_Positioning_v7.2.pptx",
    "Claude outputs/iris_thesis_independent_audit_2026-09-13.md",
    "Claude outputs/iris_thesis_repo_audit_2026-09-13.md",
    "docs/ESGC Cost Performance Report 2022 PNNL-33283.pdf",
}


class SocSensitivityAuthorityError(RuntimeError):
    """Fail-closed authority or acceptance error."""


@dataclass(frozen=True)
class FilePin:
    label: str
    path: str
    sha256: str


AUTHORITY_PINS = (
    FilePin(
        "framework",
        "docs/research_framework_v7_2_2026-08-24.md",
        "bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5",
    ),
    FilePin(
        "registry",
        "docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md",
        "8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e",
    ),
    FilePin("corrected_r10_core", "src/annual_design_model_v7_2.py", EXPECTED_R10_CORE_SHA256),
    FilePin("rainflow_validator", "src/rainflow_validation_v7_2.py", EXPECTED_RAINFLOW_SHA256),
    FilePin(
        "representative_helper",
        "scripts/16a_preflight_layer_a_representative_binary_cases.py",
        EXPECTED_HELPER_SHA256,
    ),
    FilePin(
        "authoritative_comparator_pin_source",
        "scripts/17d_run_bess_cost_scale_sensitivity.py",
        EXPECTED_17D_SHA256,
    ),
    FilePin(
        "canonical_annual_input",
        "data/processed/annual_input_v7_1.parquet",
        EXPECTED_CANONICAL_INPUT_SHA256,
    ),
    FilePin(
        "economic_interface",
        "data/reference/production_economic_interface_v7_2.json",
        "9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9",
    ),
    FilePin(
        "optimization_tariff",
        "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
        "5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395",
    ),
    FilePin(
        "settlement_interface",
        "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
        "f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88",
    ),
    FilePin(
        "settlement_matrix",
        "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
        "ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79",
    ),
    FilePin(
        "pnnl_cyclelife_provenance",
        "results/parameter_audit/pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv",
        "1172963521fbc4b646394cb2df6947ade9f961211bf608c5928ef4de215644f6",
    ),
)


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    alpha: float | None
    beta_h: int | None


ALLOWED_CASES = (
    CaseSpec("EOB", None, None),
    CaseSpec("a0.60_b04", 0.60, 4),
    CaseSpec("a0.60_b12", 0.60, 12),
    CaseSpec("a0.80_b08", 0.80, 8),
    CaseSpec("a1.00_b04", 1.00, 4),
    CaseSpec("a1.00_b12", 1.00, 12),
)
ALLOWED_CASE_IDS = tuple(case.case_id for case in ALLOWED_CASES)


@dataclass(frozen=True)
class ComparatorPin:
    case_id: str
    run_id: str
    result_path: str
    result_sha256: str
    run_manifest_path: str
    run_manifest_sha256: str
    completion_path: str | None = None
    completion_sha256: str | None = None


def project_root() -> Path:
    return ROOT


def utc_text() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def canonical_object_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        json_safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SocSensitivityAuthorityError(f"Required JSON is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Mapping[str, Any], *, exclusive: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as handle:
        json.dump(json_safe(payload), handle, indent=2, allow_nan=False)
        handle.write("\n")


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SocSensitivityAuthorityError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def git_text(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SocSensitivityAuthorityError(
            f"git {' '.join(args)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}"
        )
    return completed.stdout.decode("utf-8", errors="strict").rstrip("\r\n")


def repository_snapshot(root: Path) -> dict[str, Any]:
    porcelain = git_text(
        root,
        "-c",
        "core.quotePath=false",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).splitlines()
    untracked_raw = git_text(
        root, "-c", "core.quotePath=false", "ls-files", "--others", "--exclude-standard", "-z"
    )
    untracked = sorted(path for path in untracked_raw.strip("\0").split("\0") if path)
    staged = git_text(root, "diff", "--cached", "--name-only").splitlines()
    tracked_modified = sorted(
        line[3:] for line in porcelain if len(line) >= 4 and not line.startswith("??")
    )
    return {
        "branch": git_text(root, "branch", "--show-current"),
        "head": git_text(root, "rev-parse", "HEAD"),
        "origin_tracking": git_text(root, "rev-parse", "origin/thesis-v7"),
        "porcelain": porcelain,
        "staged": staged,
        "tracked_modified": tracked_modified,
        "untracked": untracked,
    }


def production_repository_authority(root: Path) -> dict[str, Any]:
    snapshot = repository_snapshot(root)
    gates = {
        "branch": snapshot["branch"] == EXPECTED_BRANCH,
        "head_equals_origin": snapshot["head"] == snapshot["origin_tracking"],
        "staged_empty": snapshot["staged"] == [],
        "tracked_modified_empty": snapshot["tracked_modified"] == [],
        "untracked_exactly_preexisting_boundary": set(snapshot["untracked"])
        == PREEXISTING_ALLOWED_UNTRACKED,
    }
    if not all(gates.values()):
        raise SocSensitivityAuthorityError(
            f"Production repository authority mismatch: {gates}"
        )
    return {"status": "PASS", **snapshot, "gates": gates}


def verify_file_pins(root: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for pin in AUTHORITY_PINS:
        path = root / pin.path
        actual = sha256_file(path) if path.is_file() else None
        if actual != pin.sha256:
            raise SocSensitivityAuthorityError(
                f"Authority pin mismatch for {pin.label}: expected={pin.sha256}, actual={actual}"
            )
        records[pin.label] = {
            "path": pin.path,
            "expected_sha256": pin.sha256,
            "actual_sha256": actual,
        }
    return records


def recover_authoritative_comparator_pins(root: Path) -> tuple[ComparatorPin, ...]:
    source = root / "scripts" / "17d_run_bess_cost_scale_sensitivity.py"
    if sha256_file(source) != EXPECTED_17D_SHA256:
        raise SocSensitivityAuthorityError("Authoritative 17d comparator-pin source changed.")
    module_name = f"_iris_soc2080_pin_source_{uuid.uuid4().hex}"
    module = load_module(source, module_name)
    try:
        pins = tuple(
            ComparatorPin(
                case_id=str(pin.case_id),
                run_id=str(pin.run_id),
                result_path=str(pin.result_path),
                result_sha256=str(pin.result_sha256),
                run_manifest_path=str(pin.run_manifest_path),
                run_manifest_sha256=str(pin.run_manifest_sha256),
                completion_path=(
                    None if pin.completion_path is None else str(pin.completion_path)
                ),
                completion_sha256=(
                    None if pin.completion_sha256 is None else str(pin.completion_sha256)
                ),
            )
            for pin in module.COMPARATOR_PINS
        )
    finally:
        sys.modules.pop(module_name, None)
    if tuple(pin.case_id for pin in pins) != ALLOWED_CASE_IDS:
        raise SocSensitivityAuthorityError(
            "Recovered comparator pins do not match the six-case SOC allowlist."
        )
    return pins


def verify_comparators(root: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for pin in recover_authoritative_comparator_pins(root):
        result_path = root / pin.result_path
        manifest_path = root / pin.run_manifest_path
        if sha256_file(result_path) != pin.result_sha256:
            raise SocSensitivityAuthorityError(f"Comparator result mismatch: {pin.case_id}")
        if sha256_file(manifest_path) != pin.run_manifest_sha256:
            raise SocSensitivityAuthorityError(f"Comparator manifest mismatch: {pin.case_id}")
        record = read_json(result_path)
        result = record if pin.case_id == "EOB" else record.get("result", {})
        if (
            result.get("status") != "OPTIMAL"
            or result.get("mode") != "binary"
            or result.get("has_solution") is not True
        ):
            raise SocSensitivityAuthorityError(
                f"Comparator is not accepted optimal binary: {pin.case_id}"
            )
        manifest = read_json(manifest_path)
        if manifest.get("run_id") != pin.run_id:
            raise SocSensitivityAuthorityError(f"Comparator run ID mismatch: {pin.case_id}")
        completion_status = "ACCEPTED_BY_ADDITIVE_CHECKPOINT"
        if pin.case_id != "EOB":
            if not pin.completion_path or not pin.completion_sha256:
                raise SocSensitivityAuthorityError(f"Comparator completion pin absent: {pin.case_id}")
            completion_path = root / pin.completion_path
            if sha256_file(completion_path) != pin.completion_sha256:
                raise SocSensitivityAuthorityError(
                    f"Comparator completion mismatch: {pin.case_id}"
                )
            completion = read_json(completion_path)
            if (
                completion.get("status") != "REPRESENTATIVE_PASS"
                or completion.get("all_gates_pass") is not True
            ):
                raise SocSensitivityAuthorityError(
                    f"Comparator completion is not accepted: {pin.case_id}"
                )
            completion_status = "REPRESENTATIVE_PASS"
        records[pin.case_id] = {
            **asdict(pin),
            "completion_status": completion_status,
            "reuse_only": True,
            "future_comparator_optimize_calls": 0,
        }
    return records


def verify_one_factor_contract(root: Path) -> dict[str, Any]:
    interface = read_json(root / "data/reference/production_economic_interface_v7_2.json")
    package = interface["package_selector"]["mainline"]
    if package.get("package_id") != EXPECTED_MAINLINE_PACKAGE_ID:
        raise SocSensitivityAuthorityError("SOC branch is not routed to the 10 MW package.")
    if float(package.get("power_scale_bracket_mw")) != 10.0:
        raise SocSensitivityAuthorityError("SOC branch package scale is not 10 MW.")
    if canonical_object_sha256(package) != EXPECTED_MAINLINE_PACKAGE_SHA256:
        raise SocSensitivityAuthorityError("Mainline 10 MW package object changed.")
    if package.get("production_breakpoints") != "0,0.30,0.60,0.80":
        raise SocSensitivityAuthorityError("Technical degradation calibration changed.")
    monetary = interface["monetary_basis"]
    if (
        monetary.get("basis_label") != "constant NTD-2023"
        or float(monetary.get("discount_rate")) != 0.05
        or int(monetary.get("analysis_horizon_years")) != 20
    ):
        raise SocSensitivityAuthorityError("Monetary-basis contract changed.")

    annual_path = root / "data/processed/annual_input_v7_1.parquet"
    annual = pd.read_parquet(annual_path)
    if len(annual) != 8760:
        raise SocSensitivityAuthorityError("Canonical annual input is not 8,760 hours.")
    unavailable = annual["pv_long_unavailable_assumption"].astype(bool)
    if not unavailable.any() or not np.allclose(
        annual.loc[unavailable, "pv_available_kw"].astype(float), 0.0
    ):
        raise SocSensitivityAuthorityError("Conservative-zero winter-PV treatment changed.")
    if set(annual.loc[unavailable, "pv_reconstruction_method"].astype(str)) != {
        "unavailable_zero_mainline"
    }:
        raise SocSensitivityAuthorityError("Unexpected winter-PV reconstruction method.")
    return {
        "status": "PASS",
        "only_changed_factor": "SOC_WINDOW_10_90_TO_20_80",
        "soc_window": SOC2080_SPEC.metadata(),
        "one_factor_contract": dict(ONE_FACTOR_CONTRACT),
        "mainline_package": package,
        "mainline_package_object_sha256": EXPECTED_MAINLINE_PACKAGE_SHA256,
        "canonical_input_sha256": EXPECTED_CANONICAL_INPUT_SHA256,
        "long_unavailable_zero_hours": int(unavailable.sum()),
        "alternative_winter_input_used": False,
        "cost_scale_sensitivity_package_used": False,
        "variable_reserve_floor_used": False,
    }


def validate_static_authority(root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pins = verify_file_pins(root)
    comparators = verify_comparators(root)
    one_factor = verify_one_factor_contract(root)
    active_widths = derive_active_segment_widths(
        TECHNICAL_BREAKPOINTS, SOC2080_SPEC.usable_fraction
    )
    if active_widths != (0.30, 0.30, 0.0):
        raise SocSensitivityAuthorityError("Active segment widths are not SOC2080.")
    output_root = (root / OUTPUT_ROOT_RELATIVE).resolve()
    forbidden = tuple(
        (root / relative).resolve()
        for relative in (
            "results/eob_production",
            "results/eob_production_corrected",
            "results/layer_a",
            "results/sensitivity/winter_pv_17c",
            "results/sensitivity/bess_cost_scale_1mw",
        )
    )
    if any(output_root == path or path in output_root.parents for path in forbidden):
        raise SocSensitivityAuthorityError("SOC sensitivity namespace collides with protected output.")
    return {
        "status": "CANDIDATE_STATIC_AUTHORITY_PASS_NO_MODEL_NO_SOLVE",
        "authority_state": "CANDIDATE_PENDING_INDEPENDENT_IMPLEMENTATION_AUDIT",
        "runner_version": SCRIPT_VERSION,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "adapter_version": ADAPTER_VERSION,
        "adapter_sha256": sha256_file(
            root / "src/soc_window_sensitivity_adapter_v7_2.py"
        ),
        "lineage_id": LINEAGE_ID,
        "parent_lineage": PARENT_LINEAGE_ID,
        "soc_contract": SOC2080_SPEC.metadata(),
        "technical_degradation_breakpoints": list(TECHNICAL_BREAKPOINTS),
        "technical_segment_widths": list(TECHNICAL_SEGMENT_WIDTHS),
        "active_segment_widths": list(active_widths),
        "third_segment_inactive": active_widths[2] == 0.0,
        "r10_core_version": EXPECTED_R10_CORE_VERSION,
        "r10_core_sha256": EXPECTED_R10_CORE_SHA256,
        "canonical_core_mutation": False,
        "file_pins": pins,
        "one_factor_authority": one_factor,
        "comparators": comparators,
        "allowed_cases": [asdict(case) for case in ALLOWED_CASES],
        "solver_contract": dict(SOLVER_CONTRACT),
        "solve_count_contract": {
            "expected_future_sensitivity_optimize_calls": EXPECTED_FUTURE_SENSITIVITY_OPTIMIZE_CALLS,
            "expected_future_comparator_optimize_calls": EXPECTED_FUTURE_COMPARATOR_OPTIMIZE_CALLS,
            "actual_optimize_calls_this_validation": 0,
        },
        "output_namespace": OUTPUT_ROOT_RELATIVE.as_posix() + "/<run_id>",
        "default_mode": "READ_ONLY_STATIC_NO_MODEL_NO_SOLVE_NO_WRITE",
        "production_execution_authorized": False,
        "production_authorization_rule": (
            "Separate independent implementation/build-only audit and explicit execution authorization required."
        ),
        "repository_snapshot_non_authorizing": repository_snapshot(root),
    }


class OptimizeCallGuard(AbstractContextManager["OptimizeCallGuard"]):
    """Future-run guard: exactly one standard optimize call per allowed case."""

    def __init__(self, gp_module: Any, maximum_calls: int) -> None:
        self.gp = gp_module
        self.maximum_calls = maximum_calls
        self.count = 0
        self._originals: dict[str, Any] = {}

    def __enter__(self) -> "OptimizeCallGuard":
        model_type = self.gp.Model
        for name in (
            "optimize",
            "optimizeAsync",
            "optimizeBatch",
            "tune",
            "feasRelax",
            "feasRelaxS",
        ):
            if hasattr(model_type, name):
                self._originals[name] = getattr(model_type, name)
        original_optimize = self._originals["optimize"]

        def guarded(model: Any, *args: Any, **kwargs: Any) -> Any:
            if self.count >= self.maximum_calls:
                raise SocSensitivityAuthorityError("Six-call optimize contract exceeded.")
            self.count += 1
            return original_optimize(model, *args, **kwargs)

        def forbidden(*_: Any, **__: Any) -> None:
            raise SocSensitivityAuthorityError("Forbidden alternate solver method reached.")

        setattr(model_type, "optimize", guarded)
        for name in self._originals:
            if name != "optimize":
                setattr(model_type, name, forbidden)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        for name, original in self._originals.items():
            setattr(self.gp.Model, name, original)
        return None

    def assert_one_new_call(self, before: int, case_id: str) -> None:
        if self.count != before + 1:
            raise SocSensitivityAuthorityError(
                f"Case {case_id} made {self.count - before} optimize calls; expected one."
            )


def telemetry_writer(path: Path, case_id: str) -> Callable[[dict[str, Any]], None]:
    def write(record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    json_safe({"timestamp_utc": utc_text(), "case_id": case_id, **record}),
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n"
            )
            handle.flush()

    return write


def validate_soc_rainflow(
    root: Path, inputs: Any, result: dict[str, Any]
) -> dict[str, Any]:
    from src.rainflow_validation_v7_2 import validate_dispatch_rainflow

    technical_path = (
        root
        / "results/parameter_audit/pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv"
    )
    technical = pd.read_csv(technical_path)
    bracket = float(inputs.mainline_package["power_scale_bracket_mw"])
    selected = technical.loc[
        np.isclose(
            pd.to_numeric(technical["power_scale_bracket_mw"], errors="coerce"),
            bracket,
            atol=1e-12,
            rtol=0.0,
        )
    ].copy()
    if selected.empty or bracket != 10.0:
        raise SocSensitivityAuthorityError("10 MW PNNL technical points are unavailable.")
    lambdas = [
        float(
            inputs.mainline_package[
                f"lambda_{k}_ntd2023_per_battery_side_discharged_kwh"
            ]
        )
        for k in range(1, 4)
    ]
    return validate_dispatch_rainflow(
        result["dispatch"],
        e_n_kwh=float(result["sizing"]["E_N_kwh"]),
        eta_c=0.90,
        eta_d=0.90,
        soc_min=SOC2080_SPEC.soc_min,
        soc_max=SOC2080_SPEC.soc_max,
        production_breakpoints=TECHNICAL_BREAKPOINTS,
        lambdas=lambdas,
        technical_points=selected,
        crep_ntd_per_kwh=float(inputs.mainline_package["crep_ntd2023_per_kwh"]),
        pwl_cost_reference_ntd=float(
            result["cost_components_ntd2023_per_year"]["degradation"]
        ),
        battery_side_discharge_reference_kwh=float(
            result["annual_energy"]["battery_side_discharge_kwh"]
        ),
        timestamps=pd.to_datetime(result["dispatch"]["timestamp"], errors="raise"),
    )


def outage_replay_audit(
    annual: pd.DataFrame,
    requirement: Mapping[str, Any],
    sizing: Mapping[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    alpha = float(requirement["alpha"])
    beta = int(requirement["beta_h"])
    reserve = float(requirement["R_kwh_battery"])
    e_n = float(sizing["E_N_kwh"])
    p_b = float(sizing["P_B_kw_ac"])
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    deficit = np.maximum(alpha * load - pv, 0.0)
    windows = np.lib.stride_tricks.sliding_window_view(deficit, beta)
    consumption = np.cumsum(windows / 0.90, axis=1)
    initial = SOC2080_SPEC.soc_min * e_n + reserve
    states = initial - consumption
    technical_min = SOC2080_SPEC.soc_min * e_n
    technical_max = SOC2080_SPEC.soc_max * e_n
    terminal = states[:, -1]
    power_margin = p_b - windows.max(axis=1)
    maximum_reserve = float(consumption[:, -1].max())
    binding = int(np.argmax(consumption[:, -1]))
    analytical_minimum = required_nameplate_energy_kwh(reserve)
    checks = {
        "initial_within_technical_bounds": technical_min - TOL <= initial <= technical_max + TOL,
        "all_start_technical_soc_min": bool(states.min() >= technical_min - TOL),
        "all_start_technical_soc_max": bool(states.max() <= technical_max + TOL),
        "terminal_requires_only_technical_soc_min": bool(terminal.min() >= technical_min - TOL),
        "reserve_restoration_not_required": True,
        "reserve_consumable_during_outage": bool(states.min() < initial - TOL),
        "no_pv_surplus_recharge": True,
        "all_start_power": bool(power_margin.min() >= -TOL),
        "accepted_reserve_reproduced": abs(maximum_reserve - reserve) <= TOL,
        "analytical_nameplate_bound_r_over_point60": e_n + TOL >= analytical_minimum,
        "no_circular_wrap": len(windows) == len(annual) - beta + 1,
    }
    audit = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "soc_min": SOC2080_SPEC.soc_min,
        "soc_max": SOC2080_SPEC.soc_max,
        "usable_fraction": SOC2080_SPEC.usable_fraction,
        "initial_energy_kwh": initial,
        "technical_min_kwh": technical_min,
        "technical_max_kwh": technical_max,
        "minimum_terminal_margin_kwh": float((terminal - technical_min).min()),
        "minimum_power_margin_kw": float(power_margin.min()),
        "valid_start_count": int(len(windows)),
        "binding_start_index": binding,
        "reserve_policy": "CONSUMABLE_AFTER_OUTAGE_ONSET",
        "terminal_policy": "TECHNICAL_SOC_MIN_ONLY_NO_R_RESTORATION",
        "outage_pv_surplus_recharge": False,
    }
    starts = pd.DataFrame(
        {
            "start_index": np.arange(len(windows), dtype=int),
            "start_timestamp": pd.to_datetime(annual["timestamp"].iloc[: len(windows)]),
            "consumed_battery_kwh": consumption[:, -1],
            "terminal_energy_kwh": terminal,
            "terminal_margin_above_soc_min_kwh": terminal - technical_min,
            "minimum_power_margin_kw": power_margin,
        }
    )
    if audit["status"] != "PASS":
        raise SocSensitivityAuthorityError(f"SOC2080 outage replay failed: {checks}")
    return audit, starts


def base_post_solve_gates(
    result: Mapping[str, Any],
    billing: Mapping[str, Any],
    rainflow: Mapping[str, Any],
) -> dict[str, str]:
    physical = result.get("physical_diagnostics", {})
    dispatch = result["dispatch"]
    third_columns = (
        "e_seg_3_kwh",
        "p_charge_seg_3_kw_ac",
        "p_discharge_seg_3_kw_ac",
    )
    third_max = max(
        float(np.max(np.abs(pd.to_numeric(dispatch[column], errors="raise"))))
        for column in third_columns
    )
    realized_depth = float(dispatch["soc_fraction"].max() - dispatch["soc_fraction"].min())
    rainflow_pass = (
        rainflow.get("summary", {}).get("verdict") == "RAINFLOW_VALIDATION_PASS"
        and all(value == "PASS" for value in rainflow.get("gates", {}).values())
    )
    return {
        "solver_optimal": "PASS" if result.get("status") == "OPTIMAL" else "FAIL",
        "binary_formulation": "PASS" if result.get("mode") == "binary" else "FAIL",
        "mip_gap": "PASS"
        if result.get("mip_gap") is not None and float(result["mip_gap"]) <= MIP_GAP
        else "FAIL",
        "technical_soc_20_80": "PASS"
        if float(physical.get("soc_min_realized", -math.inf)) >= 0.20 - TOL
        and float(physical.get("soc_max_realized", math.inf)) <= 0.80 + TOL
        else "FAIL",
        "realized_operating_depth_at_most_point60": "PASS"
        if realized_depth <= 0.60 + TOL
        and float(
            rainflow.get("summary", {}).get(
                "maximum_rainflow_DOD_fraction_nameplate", math.inf
            )
        )
        <= 0.60 + TOL
        else "FAIL",
        "third_segment_state_charge_discharge_zero": "PASS"
        if third_max <= TOL
        else "FAIL",
        "ac_balance": "PASS"
        if float(physical.get("max_ac_balance_residual_kw", math.inf)) <= 1e-5
        else "FAIL",
        "segment_dynamics": "PASS"
        if float(physical.get("max_segment_dynamics_residual_kwh", math.inf)) <= 1e-5
        else "FAIL",
        "segment_cyclic": "PASS"
        if float(physical.get("max_segment_cyclic_residual_kwh", math.inf)) <= 1e-5
        else "FAIL",
        "simultaneous_charge_discharge": "PASS"
        if int(physical.get("simultaneous_hours_above_tol", -1)) == 0
        else "FAIL",
        "cost_reconciliation": "PASS"
        if abs(float(result.get("cost_reconciliation_residual_ntd", math.inf))) <= 1e-3
        else "FAIL",
        "transition_ambiguity": "PASS"
        if result.get("transition_settlement", {}).get("nonbinding_certificate")
        == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
        else "FAIL",
        "billing_structure": "PASS"
        if all(
            value == "PASS"
            for key, value in billing.items()
            if key
            in {
                "period_ids",
                "detail_columns",
                "valid_detail_keys",
                "duplicate_detail_keys",
                "tariff_calendar_structure",
            }
        )
        else "FAIL",
        "rainflow_validation": "PASS" if rainflow_pass else "FAIL",
    }


def strip_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {"dispatch", "billing_exact", "transition_settlement_detail"}
    }


def scenario_metrics(result: Mapping[str, Any]) -> dict[str, float]:
    sizing = result["sizing"]
    costs = result["cost_components_ntd2023_per_year"]
    return {
        "objective_ntd2023_per_year": float(result["objective_ntd2023_per_year"]),
        "E_N_kwh": float(sizing["E_N_kwh"]),
        "P_B_kw_ac": float(sizing["P_B_kw_ac"]),
        "CC_regular_kw": float(sizing["CC_regular_kw"]),
        **{str(key): float(value) for key, value in costs.items()},
    }


def load_comparator_result(root: Path, pin: ComparatorPin) -> dict[str, Any]:
    record = read_json(root / pin.result_path)
    return record if pin.case_id == "EOB" else record["result"]


def new_run_id() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:10]}"


def allocate_run_directory(root: Path, run_id: str) -> Path:
    parent = (root / "results/sensitivity/soc_20_80").resolve()
    run_root = (root / OUTPUT_ROOT_RELATIVE).resolve()
    if parent not in run_root.parents:
        raise SocSensitivityAuthorityError("SOC2080 output escaped its dedicated namespace.")
    run_dir = run_root / run_id
    if run_dir.exists():
        raise SocSensitivityAuthorityError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_case_artifacts(
    case_dir: Path,
    case: CaseSpec,
    result: Mapping[str, Any],
    mainline_package: Mapping[str, Any],
    gates: Mapping[str, str],
    rainflow: Mapping[str, Any],
    comparator: Mapping[str, Any],
    analytical_requirement: Mapping[str, Any] | None,
    outage_audit: Mapping[str, Any] | None,
    outage_starts: pd.DataFrame | None,
) -> None:
    case_dir.mkdir(parents=True, exist_ok=False)
    write_json(
        case_dir / "result.json",
        {
            "status": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
            "case_id": case.case_id,
            "alpha": case.alpha,
            "beta_h": case.beta_h,
            "lineage_id": LINEAGE_ID,
            "parent_lineage": PARENT_LINEAGE_ID,
            "authority_state": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "adapter_version": ADAPTER_VERSION,
            "adapter_sha256": sha256_file(
                project_root() / "src/soc_window_sensitivity_adapter_v7_2.py"
            ),
            "r10_core_identity": {
                "version": EXPECTED_R10_CORE_VERSION,
                "sha256": EXPECTED_R10_CORE_SHA256,
                "canonical_source_mutated": False,
            },
            "soc_window": SOC2080_SPEC.metadata(),
            "technical_degradation_breakpoints": list(TECHNICAL_BREAKPOINTS),
            "active_segment_widths": list(
                derive_active_segment_widths(
                    TECHNICAL_BREAKPOINTS, SOC2080_SPEC.usable_fraction
                )
            ),
            "degradation_lambda_provenance": {
                "status": "UNCHANGED_10MW_MAINLINE_PACKAGE",
                "package_id": EXPECTED_MAINLINE_PACKAGE_ID,
                "package_object_sha256": EXPECTED_MAINLINE_PACKAGE_SHA256,
                "lambda_1_ntd2023_per_battery_side_discharged_kwh": mainline_package[
                    "lambda_1_ntd2023_per_battery_side_discharged_kwh"
                ],
                "lambda_2_ntd2023_per_battery_side_discharged_kwh": mainline_package[
                    "lambda_2_ntd2023_per_battery_side_discharged_kwh"
                ],
                "lambda_3_ntd2023_per_battery_side_discharged_kwh": mainline_package[
                    "lambda_3_ntd2023_per_battery_side_discharged_kwh"
                ],
            },
            "canonical_annual_input": {
                "path": "data/processed/annual_input_v7_1.parquet",
                "sha256": EXPECTED_CANONICAL_INPUT_SHA256,
            },
            "pnnl_package": {
                "package_id": EXPECTED_MAINLINE_PACKAGE_ID,
                "power_scale_bracket_mw": 10.0,
                "package_object_sha256": EXPECTED_MAINLINE_PACKAGE_SHA256,
                "one_mw_package_used": False,
            },
            "winter_pv_treatment": "MAINLINE_CONSERVATIVE_ZERO",
            "alternative_winter_input_used": False,
            "reserve_policy": "CONSTANT_WORST_CASE_CASE_SPECIFIC_REQUIREMENT",
            "variable_reserve_floor_used": False,
            "eta_c": 0.90,
            "eta_d": 0.90,
            "solver_contract": SOLVER_CONTRACT,
            "solve_count_contract": {
                "expected_sensitivity_optimize_calls": 6,
                "expected_comparator_optimize_calls": 0,
                "actual_optimize_calls": "RECORDED_IN_RUN_COMPLETION_MANIFEST",
            },
            "accepted_comparator": dict(comparator),
            "analytical_requirement": analytical_requirement,
            "result": strip_result(result),
        },
    )
    result["dispatch"].to_csv(case_dir / "dispatch.csv", index=False, encoding="utf-8-sig")
    result["billing_exact"].to_csv(
        case_dir / "billing_exact.csv", index=False, encoding="utf-8-sig"
    )
    result["transition_settlement_detail"].to_csv(
        case_dir / "transition_settlement_detail.csv", index=False, encoding="utf-8-sig"
    )
    write_json(case_dir / "post_solve_gates.json", {"status": "PASS", "gates": gates})
    write_json(
        case_dir / "rainflow_audit.json",
        {
            "summary": rainflow["summary"],
            "gates": rainflow["gates"],
            "algorithm_self_test": rainflow["algorithm_self_test"],
        },
    )
    for name in ("cycles", "turning_points", "depth_bins", "pwl_segments", "g_curve"):
        rainflow[name].to_csv(
            case_dir / f"rainflow_{name}.csv", index=False, encoding="utf-8-sig"
        )
    write_json(
        case_dir / "outage_replay_audit.json",
        outage_audit or {"status": "NOT_APPLICABLE_EOB"},
    )
    if outage_starts is not None:
        outage_starts.to_csv(
            case_dir / "outage_all_start_replay.csv", index=False, encoding="utf-8-sig"
        )


def build_artifact_registry(run_dir: Path) -> dict[str, Any]:
    excluded = {"completion_manifest.json", "failure_manifest.json"}
    registry: dict[str, Any] = {}
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(run_dir).as_posix()
        if relative in excluded:
            continue
        registry[relative] = {
            "path": relative,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return registry


def execute_production(root: Path, static_authority: Mapping[str, Any]) -> Path:
    """Future six-case execution path; never entered without the explicit flag."""

    repository = production_repository_authority(root)
    live = validate_static_authority(root)
    if live["runner_sha256"] != static_authority["runner_sha256"]:
        raise SocSensitivityAuthorityError("Runner changed between validation and execution.")

    import gurobipy as gp

    isolated = load_isolated_r10_soc_core(root)
    core = isolated.module
    if isolated.active_segment_widths != (0.30, 0.30, 0.0):
        raise SocSensitivityAuthorityError("Isolated core active domain is not SOC2080.")
    helper_name = f"_iris_soc2080_helper16a_{uuid.uuid4().hex}"
    helper = load_module(
        root / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
        helper_name,
    )
    inputs = core.load_annual_design_inputs(
        root,
        annual_parquet=root / "data/processed/annual_input_v7_1.parquet",
        annual_csv=root / "data/processed/annual_input_v7_1.csv",
        economic_interface_path=root / "data/reference/production_economic_interface_v7_2.json",
        normalized_tariff_path=root / "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
        settlement_interface_path=root
        / "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
        settlement_matrix_path=root
        / "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
    )
    if (
        inputs.mainline_package.get("package_id") != EXPECTED_MAINLINE_PACKAGE_ID
        or canonical_object_sha256(inputs.mainline_package)
        != EXPECTED_MAINLINE_PACKAGE_SHA256
    ):
        raise SocSensitivityAuthorityError("Solver-facing package is not the pinned 10 MW package.")
    surface, _starts, analytical_audit = helper.analytical_surface(
        inputs.annual,
        eta_d=0.90,
        soc_min=SOC2080_SPEC.soc_min,
        soc_max=SOC2080_SPEC.soc_max,
    )
    if analytical_audit.get("status") != "PASS":
        raise SocSensitivityAuthorityError("SOC2080 analytical requirements failed.")

    comparator_pins = recover_authoritative_comparator_pins(root)
    comparator_records = live["comparators"]
    run_id = new_run_id()
    run_dir: Path | None = None
    completed: dict[str, dict[str, Any]] = {}
    try:
        run_dir = allocate_run_directory(root, run_id)
        write_json(
            run_dir / "run_manifest.json",
            {
                "schema_version": "v7.2-soc2080-run-manifest-1",
                "status": "CANDIDATE_EXECUTION_STARTED_NOT_ACCEPTED",
                "run_id": run_id,
                "started_utc": utc_text(),
                "lineage_id": LINEAGE_ID,
                "parent_lineage": PARENT_LINEAGE_ID,
                "runner_version": SCRIPT_VERSION,
                "runner_sha256": live["runner_sha256"],
                "adapter_version": ADAPTER_VERSION,
                "adapter_sha256": live["adapter_sha256"],
                "core_version": EXPECTED_R10_CORE_VERSION,
                "core_sha256": EXPECTED_R10_CORE_SHA256,
                "soc_window": SOC2080_SPEC.metadata(),
                "technical_degradation_breakpoints": list(TECHNICAL_BREAKPOINTS),
                "technical_segment_widths": list(TECHNICAL_SEGMENT_WIDTHS),
                "active_segment_widths": list(isolated.active_segment_widths),
                "one_factor_contract": ONE_FACTOR_CONTRACT,
                "canonical_annual_input_sha256": EXPECTED_CANONICAL_INPUT_SHA256,
                "pnnl_package_id": EXPECTED_MAINLINE_PACKAGE_ID,
                "pnnl_package_object_sha256": EXPECTED_MAINLINE_PACKAGE_SHA256,
                "solver_contract": SOLVER_CONTRACT,
                "authorized_cases": [asdict(case) for case in ALLOWED_CASES],
                "accepted_comparators": comparator_records,
                "expected_sensitivity_optimize_calls": 6,
                "expected_comparator_optimize_calls": 0,
                "authority_state": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
                "repository_authority": repository,
            },
        )

        sensitivity_eob: dict[str, Any] | None = None
        with OptimizeCallGuard(gp, EXPECTED_FUTURE_SENSITIVITY_OPTIMIZE_CALLS) as guard:
            for case in ALLOWED_CASES:
                requirement: dict[str, Any] | None = None
                layer_requirement = None
                if case.case_id != "EOB":
                    requirement = (
                        surface.loc[surface["case_id"].eq(case.case_id)].iloc[0].to_dict()
                    )
                    expected_minimum = required_nameplate_energy_kwh(
                        float(requirement["R_kwh_battery"])
                    )
                    if abs(
                        float(requirement["analytical_E_N_min_kwh"]) - expected_minimum
                    ) > TOL:
                        raise SocSensitivityAuthorityError(
                            f"R/0.60 analytical bound mismatch: {case.case_id}"
                        )
                    layer_requirement = core.LayerAResilienceRequirements(
                        alpha=float(requirement["alpha"]),
                        beta_h=int(requirement["beta_h"]),
                        reserve_kwh_battery=float(requirement["R_kwh_battery"]),
                        power_requirement_kw_ac=float(requirement["P_out_kw_ac"]),
                    )
                case_dir = run_dir / "cases" / case.case_id
                settings = core.SolveSettings(
                    mode="binary",
                    mip_gap=MIP_GAP,
                    time_limit_sec=TIME_LIMIT_SEC,
                    output_flag=OUTPUT_FLAG,
                    numeric_focus=NUMERIC_FOCUS,
                    log_file=str(case_dir / "gurobi.log"),
                    telemetry_callback=telemetry_writer(
                        case_dir / "solver_telemetry.jsonl", case.case_id
                    ),
                )
                case_dir.mkdir(parents=True, exist_ok=False)
                before = guard.count
                started = time.perf_counter()
                result = core.solve_eob(inputs, settings, layer_requirement)
                guard.assert_one_new_call(before, case.case_id)
                result["soc_window_configuration"] = isolated.metadata()
                result["lineage_id"] = LINEAGE_ID
                result["parent_lineage"] = PARENT_LINEAGE_ID
                rainflow = validate_soc_rainflow(root, inputs, result)
                billing = helper.billing_structure_audit(
                    result["billing_exact"], inputs.annual
                )
                gates = base_post_solve_gates(result, billing, rainflow)
                outage_audit = None
                outage_starts = None
                if case.case_id == "EOB":
                    sensitivity_eob = result
                else:
                    if sensitivity_eob is None or requirement is None:
                        raise SocSensitivityAuthorityError("Layer-A case reached before SOC EOB.")
                    representative = helper.representative_gate(
                        result,
                        requirement,
                        sensitivity_eob,
                        soc_min=SOC2080_SPEC.soc_min,
                        soc_max=SOC2080_SPEC.soc_max,
                        rainflow_validation=rainflow,
                        billing_audit=billing,
                    )
                    gates.update({f"representative__{k}": v for k, v in representative.items()})
                    outage_audit, outage_starts = outage_replay_audit(
                        inputs.annual, requirement, result["sizing"]
                    )
                    gates["all_start_outage_replay"] = outage_audit["status"]
                if not all(value == "PASS" for value in gates.values()):
                    raise SocSensitivityAuthorityError(
                        f"Post-solve gate failed for {case.case_id}: {gates}"
                    )
                comparator = comparator_records[case.case_id]
                write_case_artifacts(
                    case_dir / "artifacts",
                    case,
                    result,
                    inputs.mainline_package,
                    gates,
                    rainflow,
                    comparator,
                    requirement,
                    outage_audit,
                    outage_starts,
                )
                completed[case.case_id] = {
                    "result": strip_result(result),
                    "gates": gates,
                    "elapsed_wall_seconds": time.perf_counter() - started,
                }
            if guard.count != EXPECTED_FUTURE_SENSITIVITY_OPTIMIZE_CALLS:
                raise SocSensitivityAuthorityError(
                    f"Optimize count={guard.count}; expected exactly six."
                )
            actual_optimize_calls = guard.count

        comparison_rows: list[dict[str, Any]] = []
        comparison_payload: dict[str, Any] = {
            "status": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
            "lineage_id": LINEAGE_ID,
            "parent_lineage": PARENT_LINEAGE_ID,
            "claim_boundary": (
                "Targeted EOB plus five representative cases; not a statistical sample "
                "and not the complete 81-point Layer-A response surface."
            ),
            "cases": {},
        }
        for pin in comparator_pins:
            mainline_metrics = scenario_metrics(load_comparator_result(root, pin))
            sensitivity_metrics = scenario_metrics(completed[pin.case_id]["result"])
            metrics: dict[str, Any] = {}
            for metric, mainline_value in mainline_metrics.items():
                sensitivity_value = sensitivity_metrics[metric]
                delta = sensitivity_value - mainline_value
                metrics[metric] = {
                    "mainline_10_90": mainline_value,
                    "sensitivity_20_80": sensitivity_value,
                    "delta_20_80_minus_10_90": delta,
                    "delta_pct_of_mainline": (
                        None
                        if mainline_value == 0.0
                        else 100.0 * delta / mainline_value
                    ),
                }
                comparison_rows.append(
                    {"case_id": pin.case_id, "metric": metric, **metrics[metric]}
                )
            comparison_payload["cases"][pin.case_id] = {
                "accepted_comparator": comparator_records[pin.case_id],
                "metrics": metrics,
            }
        write_json(run_dir / "paired_sensitivity_comparison.json", comparison_payload)
        pd.DataFrame(comparison_rows).to_csv(
            run_dir / "paired_sensitivity_comparison.csv",
            index=False,
            encoding="utf-8-sig",
        )
        registry = build_artifact_registry(run_dir)
        completion = {
            "schema_version": "v7.2-soc2080-completion-manifest-1",
            "run_id": run_id,
            "status": "CANDIDATE_PASS_PENDING_INDEPENDENT_POST_RUN_AUDIT",
            "completed_utc": utc_text(),
            "lineage_id": LINEAGE_ID,
            "parent_lineage": PARENT_LINEAGE_ID,
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": live["runner_sha256"],
            "adapter_version": ADAPTER_VERSION,
            "adapter_sha256": live["adapter_sha256"],
            "configured_soc_min": 0.20,
            "configured_soc_max": 0.80,
            "usable_fraction": 0.60,
            "technical_degradation_breakpoints": list(TECHNICAL_BREAKPOINTS),
            "active_segment_widths": list(isolated.active_segment_widths),
            "completed_cases": list(completed),
            "expected_optimize_calls": 6,
            "actual_optimize_calls": actual_optimize_calls,
            "comparator_optimize_calls": 0,
            "artifact_registry": registry,
            "completion_is_not_self_acceptance": True,
            "acceptance_status": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
        }
        write_json(run_dir / "completion_manifest.json", completion)
        return run_dir / "completion_manifest.json"
    except Exception as exc:
        if run_dir is not None and run_dir.exists():
            completion_path = run_dir / "completion_manifest.json"
            failure_path = run_dir / "failure_manifest.json"
            if not completion_path.exists() and not failure_path.exists():
                write_json(
                    failure_path,
                    {
                        "schema_version": "v7.2-soc2080-failure-manifest-1",
                        "run_id": run_id,
                        "status": "FAIL",
                        "failed_utc": utc_text(),
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "completed_cases": list(completed),
                        "completion_manifest_written": False,
                    },
                )
        raise
    finally:
        sys.modules.pop(helper_name, None)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-production",
        action="store_true",
        help=(
            "Explicitly enter the six-case solve path. Do not use until a separate "
            "independent implementation/build-only audit and execution authorization."
        ),
    )
    return parser.parse_args(argv)


def run(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    validator: Callable[[Path], dict[str, Any]] = validate_static_authority,
    executor: Callable[[Path, Mapping[str, Any]], Path] = execute_production,
) -> int:
    args = parse_args(argv)
    root = (root or project_root()).resolve()
    authority = validator(root)
    if not args.execute_production:
        print(json.dumps(json_safe(authority), indent=2, allow_nan=False))
        return 0
    completion = executor(root, authority)
    print(completion)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
