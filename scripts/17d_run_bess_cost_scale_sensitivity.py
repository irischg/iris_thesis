#!/usr/bin/env python3
"""Controlled v7.2 PNNL 1 MW BESS cost-scale sensitivity runner.

The default invocation is a read-only authority/pre-solve validation.  The
six-case solve path is reachable only through ``--execute-production`` and is
still candidate implementation until independently audited and authorized.

The accepted corrected annual core is intentionally not generalized here.  A
runner-local copy-style adapter replaces the frozen ``mainline_package`` field
with the verified complete 1 MW package before any model is constructed.
"""

from __future__ import annotations

import argparse
import ast
import copy
import dataclasses
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


SCRIPT_VERSION = "v7.2-bess-cost-scale-1mw-sensitivity-candidate-2026-09-19-r1"
EXPECTED_BRANCH = "thesis-v7"
EXPECTED_COMMIT = "b03721275c73b05d45517bdf84c1e0bd03833376"
EXPECTED_CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
)
EXPECTED_CORE_SHA256 = "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8"
EXPECTED_FRAMEWORK_SHA256 = "bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5"
EXPECTED_REGISTRY_SHA256 = "8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e"
EXPECTED_MAINLINE_PACKAGE_SHA256 = "b8c461eb3513a2f6f05739a824d124e797aa7f59d12b1cf28b066bc391bcd5e2"
EXPECTED_SENSITIVITY_PACKAGE_SHA256 = "38432cb791dccc95c4c178def34bb0fb97651802953338adb0397cb883fafac7"
EXPECTED_SENSITIVITY_PACKAGE_ID = "pnnl_v2024_lfp_2023_point_1mw_4to10h"
EXPECTED_MAINLINE_PACKAGE_ID = "pnnl_v2024_lfp_2023_point_10mw_4to10h"
EXPECTED_KAPPA = 1.0103668594376984
EXPECTED_CRF = 0.08024258719069129
MIP_GAP = 1e-6
NUMERIC_FOCUS = 1
OUTPUT_FLAG = 1
TIME_LIMIT_SEC = None
EXPECTED_FUTURE_OPTIMIZE_CALLS = 6
OUTPUT_ROOT_RELATIVE = Path("results/sensitivity/bess_cost_scale_1mw/runs")

EXPECTED_TRACKED_MODIFIED = {
    "scripts/06a_build_taipower_tou_calendar.py",
    "scripts/13c_regress_taipower_core_bill_components.py",
    "scripts/16a_preflight_layer_a_representative_binary_cases.py",
    "scripts/17b_build_winter_pv_sensitivity_annual_input.py",
    "scripts/17c_run_winter_pv_economic_sensitivity.py",
    "scripts/19a_preflight_final_layer_a_81_cases.py",
    "src/annual_design_model_v7_2.py",
    "tests/test_transition_candidate1_static_v7_2.py",
}

EXPECTED_UNTRACKED = {
    "0629\u958b\u6703\u9010\u5b57\u7a3fIris.docx",
    "Claude outputs/0930_\u9032\u5ea6\u5831\u544a_\u6295\u5f71\u7247\u67b6\u69cb\u8207\u9010\u9801\u8b1b\u7a3f_v7.2.md",
    "Claude outputs/P2_Literature_Positioning_v7.2.pptx",
    "Claude outputs/iris_thesis_independent_audit_2026-09-13.md",
    "Claude outputs/iris_thesis_repo_audit_2026-09-13.md",
    "docs/ESGC Cost Performance Report 2022 PNNL-33283.pdf",
    "docs/checkpoints/16a_current_authority_comparator_update_v7_2_2026-09-17.md",
    "docs/checkpoints/bess_cost_scale_1mw_implementation_candidate_v7_2_2026-09-19.md",
    "docs/checkpoints/core_authority_root_node_preflight_v7_2_2026-09-16.md",
    "docs/checkpoints/corrected_eob_accepted_authority_v7_2_2026-09-17.md",
    "docs/checkpoints/corrected_eob_authorization_v7_2_2026-09-17.md",
    "docs/checkpoints/corrected_eob_driver_implementation_v7_2_2026-09-17.md",
    "docs/checkpoints/corrected_eob_driver_runtime_import_repair_v7_2_2026-09-17.md",
    "docs/checkpoints/corrected_eob_reauthorization_v7_2_2026-09-17.md",
    "docs/checkpoints/post_eob_delta_freeze_r2_authority_v7_2_2026-09-17.md",
    "docs/checkpoints/post_eob_delta_freeze_r3_authority_v7_2_2026-09-17.md",
    "docs/checkpoints/pre_corrected_rerun_version_lineage_v7_2_2026-09-15.md",
    "docs/checkpoints/pre_corrected_rerun_version_lineage_v7_2_2026-09-16.md",
    "scripts/06b_validate_hourly_to_bill_v7_2.py",
    "scripts/15d_run_corrected_eob_v7_2.py",
    "scripts/17d_run_bess_cost_scale_sensitivity.py",
    "tests/test_15d_corrected_eob_driver_v7_2.py",
    "tests/test_16a_current_eob_authority_v7_2.py",
    "tests/test_17c_corrected_authority_alignment_v7_2.py",
    "tests/test_17d_bess_cost_scale_sensitivity_v7_2.py",
    "tests/test_w07_overcontract_tier_allocation.py",
    "tests/test_w07_surface1_solver_integration_v7_2.py",
    "tests/test_w18_hourly_to_bill_v7_2.py",
}

REQUIRED_PACKAGE_FIELDS = (
    "package_id",
    "power_scale_bracket_mw",
    "role",
    "cost_scale_label_only_not_power_bound",
    "duration_window_hr",
    "currency",
    "currency_base_year",
    "fx_ntd_per_usd",
    "capex_C_E_ntd2023_per_kwh",
    "capex_C_P_ntd2023_per_kw",
    "annualized_capex_C_E_ntd2023_per_kwh_year",
    "annualized_capex_C_P_ntd2023_per_kw_year",
    "fom_E_ntd2023_per_kwh_year",
    "fom_P_ntd2023_per_kw_year",
    "crep_ntd2023_per_kwh",
    "production_breakpoints",
    "lambda_1_ntd2023_per_battery_side_discharged_kwh",
    "lambda_2_ntd2023_per_battery_side_discharged_kwh",
    "lambda_3_ntd2023_per_battery_side_discharged_kwh",
    "lambda_ratio",
    "package_selection_timing",
)

PACKAGE_FIELDS_THAT_MUST_CHANGE = {
    "package_id",
    "power_scale_bracket_mw",
    "role",
    "capex_C_E_ntd2023_per_kwh",
    "capex_C_P_ntd2023_per_kw",
    "annualized_capex_C_E_ntd2023_per_kwh_year",
    "annualized_capex_C_P_ntd2023_per_kw_year",
    "fom_E_ntd2023_per_kwh_year",
    "fom_P_ntd2023_per_kw_year",
    "crep_ntd2023_per_kwh",
    "lambda_1_ntd2023_per_battery_side_discharged_kwh",
    "lambda_2_ntd2023_per_battery_side_discharged_kwh",
    "lambda_3_ntd2023_per_battery_side_discharged_kwh",
}

PACKAGE_FIELDS_THAT_MUST_MATCH = set(REQUIRED_PACKAGE_FIELDS) - PACKAGE_FIELDS_THAT_MUST_CHANGE

EXPECTED_1MW_VALUES = {
    "capex_C_E_ntd2023_per_kwh": 12537.90615,
    "capex_C_P_ntd2023_per_kw": 7246.985199999963,
    "annualized_capex_C_E_ntd2023_per_kwh_year": 1006.0740274300796,
    "annualized_capex_C_P_ntd2023_per_kw_year": 581.5168417806464,
    "fom_E_ntd2023_per_kwh_year": 26.695550000000004,
    "fom_P_ntd2023_per_kw_year": 60.77364999999988,
    "crep_ntd2023_per_kwh": 6677.78125,
    "lambda_1_ntd2023_per_battery_side_discharged_kwh": 0.6956022135416666,
    "lambda_2_ntd2023_per_battery_side_discharged_kwh": 2.0868066406250003,
    "lambda_3_ntd2023_per_battery_side_discharged_kwh": 2.7824088541666656,
}

LEGACY_VALUES = {
    "legacy_annualized_C_E": 813.75,
    "legacy_annualized_C_P": 694.4,
    "legacy_C_rep": 5107.57,
    "legacy_lambda_1": 0.532,
    "legacy_lambda_2": 1.596,
    "legacy_lambda_3": 2.128,
    "legacy_c_deg": 0.55,
}


class SensitivityAuthorityError(RuntimeError):
    """Fail-closed authority, routing, or artifact-contract error."""


@dataclass(frozen=True)
class FilePin:
    label: str
    path: str
    sha256: str


AUTHORITY_PINS = (
    FilePin("framework", "docs/research_framework_v7_2_2026-08-24.md", EXPECTED_FRAMEWORK_SHA256),
    FilePin("registry", "docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md", EXPECTED_REGISTRY_SHA256),
    FilePin("corrected_core", "src/annual_design_model_v7_2.py", EXPECTED_CORE_SHA256),
    FilePin("canonical_annual_input", "data/processed/annual_input_v7_1.parquet", "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e"),
    FilePin("economic_interface", "data/reference/production_economic_interface_v7_2.json", "9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9"),
    FilePin("optimization_tariff", "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv", "5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395"),
    FilePin("settlement_interface", "data/reference/taipower_transition_period_settlement_interface_v7_2.json", "f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88"),
    FilePin("settlement_matrix", "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv", "ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79"),
    FilePin("pnnl_cost_packages", "results/parameter_audit/pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv", "f0c167001cf554804152d5f5eb114ee9403c784bb7937f3c5c90bf000203b3e7"),
    FilePin("pnnl_degradation_packages", "results/parameter_audit/pnnl_calibrated_pwl_degradation_candidate_packages.csv", "6921ae2171da8318945a48280b41780a9c26ce70a15b373088f6dfb486a1eff3"),
    FilePin("pnnl_cyclelife_provenance", "results/parameter_audit/pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv", "1172963521fbc4b646394cb2df6947ade9f961211bf608c5928ef4de215644f6"),
    FilePin("rainflow_validator", "src/rainflow_validation_v7_2.py", "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2"),
    FilePin("representative_helper", "scripts/16a_preflight_layer_a_representative_binary_cases.py", "3f62fa290e1c8e1699c34d4b1bc78b9af0e716387b251afb4ada2b3198d7524f"),
    FilePin("corrected_eob_acceptance", "docs/checkpoints/corrected_eob_accepted_authority_v7_2_2026-09-17.md", "e71401ec3562b0803e52e3d054f8d7a69a1528fd197a03c6a7d42df629ab32a2"),
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


COMPARATOR_PINS = (
    ComparatorPin(
        "EOB",
        "20260917T082758521112Z_a4b6383308",
        "results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_result.json",
        "d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022",
        "results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/run_manifest.json",
        "9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a",
    ),
    ComparatorPin(
        "a0.60_b04",
        "20260918T054012682911Z_54b3624894",
        "results/layer_a/preflight/runs/20260918T054012682911Z_54b3624894/representative_cases/a0.60_b04/a0.60_b04_result_v7_2.json",
        "2e5710835b9a882a4978fda39990f493020418b34cd0d386d6f1399301fa23c5",
        "results/layer_a/preflight/runs/20260918T054012682911Z_54b3624894/run_manifest_v7_2.json",
        "85d52a9a81badcb5cf726caf3cff8f52249011e4b29740be4cba7827f9eddcac",
        "results/layer_a/preflight/runs/20260918T054012682911Z_54b3624894/run_completion_v7_2.json",
        "de6db45c44cfa00c684f90026cbfcbf083ce24a1ac2229e85316cb6df21aec93",
    ),
    ComparatorPin(
        "a0.60_b12",
        "20260918T063627414306Z_c114929d2c",
        "results/layer_a/preflight/runs/20260918T063627414306Z_c114929d2c/representative_cases/a0.60_b12/a0.60_b12_result_v7_2.json",
        "6372608d847b8498c7b819bddd8e59a707cf4fbecb311496d27787e52205df3d",
        "results/layer_a/preflight/runs/20260918T063627414306Z_c114929d2c/run_manifest_v7_2.json",
        "fd93211fcae15e47ef29362b4e7afc1724ca09c82317348a8134da42c549f921",
        "results/layer_a/preflight/runs/20260918T063627414306Z_c114929d2c/run_completion_v7_2.json",
        "923750d5b7c0da1fd6773e7b89a365797ad058a6126fcb2460712ce8993df0d1",
    ),
    ComparatorPin(
        "a0.80_b08",
        "20260918T085202453195Z_755e01dfb2",
        "results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_result_v7_2.json",
        "8a9bc67fc541ea682f9360e6063ededdb5bc0e2c6340c43c10c1fde86ab155f6",
        "results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/run_manifest_v7_2.json",
        "1a331faaf2d079bfd0d70d46d400e29eeeb8ee1edc67a566b096926ed1202118",
        "results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/run_completion_v7_2.json",
        "06a794588623d1658cec1bb2196279915a5a77ad251e4ebc6899ef3d9c829aac",
    ),
    ComparatorPin(
        "a1.00_b04",
        "20260918T105101058616Z_a75a268198",
        "results/layer_a/preflight/runs/20260918T105101058616Z_a75a268198/representative_cases/a1.00_b04/a1.00_b04_result_v7_2.json",
        "9fa5506db13681df0dd86b91bf3f9729b47f7a874fe57909b422dea7a6dfa628",
        "results/layer_a/preflight/runs/20260918T105101058616Z_a75a268198/run_manifest_v7_2.json",
        "9751bec3e53826b886974cfd0f6321425aaf5996fd802b0e61e3db169a8f117c",
        "results/layer_a/preflight/runs/20260918T105101058616Z_a75a268198/run_completion_v7_2.json",
        "be0ce2429ae680fe229408898cd9150a854bcfe08fce0317742fbfa2afcaf8a9",
    ),
    ComparatorPin(
        "a1.00_b12",
        "20260918T123936526903Z_82e3bc3214",
        "results/layer_a/preflight/runs/20260918T123936526903Z_82e3bc3214/representative_cases/a1.00_b12/a1.00_b12_result_v7_2.json",
        "6ea1dce9c951d11f3129c8654057c33df97030e54241f367123cfb6776590321",
        "results/layer_a/preflight/runs/20260918T123936526903Z_82e3bc3214/run_manifest_v7_2.json",
        "a6e962664550ce55add658bd4b6026c800f35085b3af844d5ecf0e19b4509881",
        "results/layer_a/preflight/runs/20260918T123936526903Z_82e3bc3214/run_completion_v7_2.json",
        "c2f88ded9b0b153825b15364faf78ea7b1759a62b9646fb11242755164c42a89",
    ),
)

SOLVER_CONTRACT = {
    "mode": "binary",
    "MIPGap": MIP_GAP,
    "NumericFocus": NUMERIC_FOCUS,
    "OutputFlag": OUTPUT_FLAG,
    "TimeLimit": "INFINITY_UNSET",
    "NodeLimit": "INFINITY_UNSET",
    "tuning": False,
    "warm_start": False,
    "feasibility_relaxation": False,
    "retry": False,
    "one_optimize_call_per_case": True,
    "expected_total_optimize_calls": EXPECTED_FUTURE_OPTIMIZE_CALLS,
    "mainline_comparator_solves": 0,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_text(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).isoformat().replace("+00:00", "Z")


def json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_object_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        json_safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SensitivityAuthorityError(f"Required JSON is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Mapping[str, Any], *, exclusive: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8") as handle:
        json.dump(json_safe(payload), handle, indent=2, allow_nan=False)
        handle.write("\n")


def git_output(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise SensitivityAuthorityError(
            f"git {' '.join(args)} failed: {completed.stderr.strip()}"
        )
    # Preserve leading porcelain status columns; only trailing line endings are noise.
    return completed.stdout.rstrip()


def repository_authority(root: Path) -> dict[str, Any]:
    branch = git_output(root, "branch", "--show-current")
    head = git_output(root, "rev-parse", "HEAD")
    origin = git_output(root, "rev-parse", "origin/thesis-v7")
    porcelain = git_output(root, "status", "--porcelain=v1", "-uall").splitlines()
    staged = git_output(root, "diff", "--cached", "--name-only").splitlines()
    untracked = {
        path.replace("\\", "/")
        for path in git_output(
            root, "ls-files", "--others", "--exclude-standard", "-z"
        ).strip("\0").split("\0")
        if path
    }
    tracked_modified = {
        line[3:].replace("\\", "/")
        for line in porcelain
        if not line.startswith("??") and len(line) >= 4
    }
    gates = {
        "branch": branch == EXPECTED_BRANCH,
        "head": head == EXPECTED_COMMIT,
        "origin": origin == EXPECTED_COMMIT,
        "staged_empty": staged == [],
        "tracked_modified_boundary": tracked_modified == EXPECTED_TRACKED_MODIFIED,
        "untracked_boundary": untracked == EXPECTED_UNTRACKED,
    }
    if not all(gates.values()):
        raise SensitivityAuthorityError(f"Repository authority mismatch: {gates}")
    return {
        "status": "PASS",
        "branch": branch,
        "head": head,
        "origin_tracking": origin,
        "staged": staged,
        "tracked_modified": sorted(tracked_modified),
        "untracked": sorted(untracked),
        "complete_porcelain": porcelain,
        "gates": gates,
    }


def verify_file_pins(root: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for pin in AUTHORITY_PINS:
        path = root / pin.path
        if not path.is_file():
            raise SensitivityAuthorityError(f"Missing authority file: {pin.path}")
        actual = sha256_file(path)
        if actual != pin.sha256:
            raise SensitivityAuthorityError(
                f"Authority hash mismatch for {pin.label}: expected={pin.sha256}, actual={actual}"
            )
        records[pin.label] = {
            "path": pin.path,
            "expected_sha256": pin.sha256,
            "actual_sha256": actual,
            "match": True,
        }
    return records


def _assert_close(actual: Any, expected: float, label: str, tolerance: float = 1e-10) -> None:
    try:
        number = float(actual)
    except (TypeError, ValueError) as exc:
        raise SensitivityAuthorityError(f"{label} is not numeric: {actual!r}") from exc
    if not math.isfinite(number) or not math.isclose(
        number, expected, rel_tol=0.0, abs_tol=tolerance
    ):
        raise SensitivityAuthorityError(
            f"{label} mismatch: expected={expected!r}, actual={number!r}"
        )


def reject_legacy_contamination(package: Mapping[str, Any]) -> None:
    """Reject known superseded coefficients before normal value validation."""
    active_values: list[float] = []
    for field in EXPECTED_1MW_VALUES:
        try:
            active_values.append(float(package[field]))
        except (KeyError, TypeError, ValueError):
            continue
    for legacy_label, legacy_value in LEGACY_VALUES.items():
        if any(
            math.isclose(value, legacy_value, rel_tol=0.0, abs_tol=1e-9)
            for value in active_values
        ):
            raise SensitivityAuthorityError(
                f"Legacy contamination detected: {legacy_label}"
            )


def validate_sensitivity_package(
    sensitivity: Mapping[str, Any],
    mainline: Mapping[str, Any],
    *,
    expected_hash: str = EXPECTED_SENSITIVITY_PACKAGE_SHA256,
) -> dict[str, Any]:
    missing = sorted(set(REQUIRED_PACKAGE_FIELDS) - set(sensitivity))
    if missing:
        raise SensitivityAuthorityError(f"1 MW package is incomplete: {missing}")
    if canonical_object_sha256(sensitivity) != expected_hash:
        raise SensitivityAuthorityError("1 MW package object hash mismatch.")
    if canonical_object_sha256(mainline) != EXPECTED_MAINLINE_PACKAGE_SHA256:
        raise SensitivityAuthorityError("10 MW mainline package object hash mismatch.")
    if sensitivity.get("package_id") != EXPECTED_SENSITIVITY_PACKAGE_ID:
        raise SensitivityAuthorityError("Wrong 1 MW sensitivity package ID.")
    if sensitivity.get("role") != "sensitivity":
        raise SensitivityAuthorityError("1 MW package role must be sensitivity.")
    _assert_close(sensitivity.get("power_scale_bracket_mw"), 1.0, "1 MW bracket")
    if mainline.get("package_id") != EXPECTED_MAINLINE_PACKAGE_ID:
        raise SensitivityAuthorityError("Wrong 10 MW mainline package ID.")
    if mainline.get("role") != "mainline":
        raise SensitivityAuthorityError("10 MW package role must be mainline.")
    _assert_close(mainline.get("power_scale_bracket_mw"), 10.0, "10 MW bracket")

    actual_differences = {
        field
        for field in REQUIRED_PACKAGE_FIELDS
        if sensitivity.get(field) != mainline.get(field)
    }
    if actual_differences != PACKAGE_FIELDS_THAT_MUST_CHANGE:
        raise SensitivityAuthorityError(
            "Full-package atomicity failure: "
            f"expected differences={sorted(PACKAGE_FIELDS_THAT_MUST_CHANGE)}, "
            f"actual={sorted(actual_differences)}"
        )
    for field in PACKAGE_FIELDS_THAT_MUST_MATCH:
        if sensitivity.get(field) != mainline.get(field):
            raise SensitivityAuthorityError(f"Frozen package metadata drift: {field}")
    reject_legacy_contamination(sensitivity)
    for field, expected in EXPECTED_1MW_VALUES.items():
        _assert_close(sensitivity.get(field), expected, field)

    if sensitivity.get("duration_window_hr") != "4,6,8,10":
        raise SensitivityAuthorityError("Sensitivity duration window is not 4,6,8,10 h.")
    if sensitivity.get("currency") != "NTD" or sensitivity.get("currency_base_year") != 2023:
        raise SensitivityAuthorityError("Sensitivity monetary basis is not NTD-2023.")
    _assert_close(sensitivity.get("fx_ntd_per_usd"), 31.15, "FX")
    if sensitivity.get("production_breakpoints") != "0,0.30,0.60,0.80":
        raise SensitivityAuthorityError("Sensitivity degradation breakpoints drifted.")
    if sensitivity.get("lambda_ratio") != "1:3:4":
        raise SensitivityAuthorityError("Sensitivity lambda ratio drifted.")
    if sensitivity.get("cost_scale_label_only_not_power_bound") is not True:
        raise SensitivityAuthorityError("1 MW label was incorrectly treated as a power bound.")
    if sensitivity.get("package_selection_timing") != "ex_ante_before_eob_or_layer_a":
        raise SensitivityAuthorityError("Package selection is not explicitly ex ante.")

    c_rep = float(sensitivity["crep_ntd2023_per_kwh"])
    expected_lambdas = (
        (c_rep / 32000.0) / 0.30,
        (c_rep / 8000.0 - c_rep / 32000.0) / 0.30,
        (c_rep / 4800.0 - c_rep / 8000.0) / 0.20,
    )
    lambda_fields = (
        "lambda_1_ntd2023_per_battery_side_discharged_kwh",
        "lambda_2_ntd2023_per_battery_side_discharged_kwh",
        "lambda_3_ntd2023_per_battery_side_discharged_kwh",
    )
    for field, expected in zip(lambda_fields, expected_lambdas, strict=True):
        _assert_close(sensitivity[field], expected, f"{field} C_rep lineage", 1e-12)

    return {
        "status": "PASS",
        "package_id": sensitivity["package_id"],
        "role": sensitivity["role"],
        "power_scale_bracket_mw": float(sensitivity["power_scale_bracket_mw"]),
        "package_object_sha256": canonical_object_sha256(sensitivity),
        "mainline_package_object_sha256": canonical_object_sha256(mainline),
        "atomic_swap_fields": sorted(PACKAGE_FIELDS_THAT_MUST_CHANGE),
        "frozen_metadata_fields": sorted(PACKAGE_FIELDS_THAT_MUST_MATCH),
        "lambda_lineage": "PASS_CREP_AND_LOCKED_0.30_0.60_0.80_CYCLE_LIFE",
        "legacy_contamination": "BLOCKED",
    }


def require_authorized_case(case_id: str) -> CaseSpec:
    """Return the exact authorized case specification or fail closed."""
    matches = tuple(case for case in ALLOWED_CASES if case.case_id == case_id)
    if len(matches) != 1:
        raise SensitivityAuthorityError(f"Unauthorized sensitivity case: {case_id}")
    return matches[0]


def verify_source_package_rows(
    root: Path, sensitivity: Mapping[str, Any]
) -> dict[str, Any]:
    costs = pd.read_csv(root / "results/parameter_audit/pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv")
    degradation = pd.read_csv(root / "results/parameter_audit/pnnl_calibrated_pwl_degradation_candidate_packages.csv")
    cost_row = costs.loc[costs["package_id"].eq(EXPECTED_SENSITIVITY_PACKAGE_ID)]
    deg_row = degradation.loc[degradation["package_id"].eq(EXPECTED_SENSITIVITY_PACKAGE_ID)]
    if len(cost_row) != 1 or len(deg_row) != 1:
        raise SensitivityAuthorityError("The 1 MW source package must resolve one-to-one in 11g/11h.")
    cost_row = cost_row.iloc[0]
    deg_row = deg_row.iloc[0]
    mappings = {
        "capex_C_E_ntd2023_per_kwh": (cost_row, "capex_C_E_ntd_per_kwh"),
        "capex_C_P_ntd2023_per_kw": (cost_row, "capex_C_P_ntd_per_kw"),
        "annualized_capex_C_E_ntd2023_per_kwh_year": (cost_row, "annualized_capex_C_E_ntd_per_kwh_year"),
        "annualized_capex_C_P_ntd2023_per_kw_year": (cost_row, "annualized_capex_C_P_ntd_per_kw_year"),
        "fom_E_ntd2023_per_kwh_year": (cost_row, "fom_E_ntd_per_kwh_year"),
        "fom_P_ntd2023_per_kw_year": (cost_row, "fom_P_ntd_per_kw_year"),
        "crep_ntd2023_per_kwh": (cost_row, "crep_ntd_per_kwh"),
        "lambda_1_ntd2023_per_battery_side_discharged_kwh": (deg_row, "lambda_1_ntd_per_battery_side_kwh"),
        "lambda_2_ntd2023_per_battery_side_discharged_kwh": (deg_row, "lambda_2_ntd_per_battery_side_kwh"),
        "lambda_3_ntd2023_per_battery_side_discharged_kwh": (deg_row, "lambda_3_ntd_per_battery_side_kwh"),
    }
    for package_field, (row, source_field) in mappings.items():
        _assert_close(
            sensitivity[package_field],
            float(row[source_field]),
            f"source row {package_field}",
            1e-10,
        )
    _assert_close(deg_row["crep_ntd_per_kwh"], sensitivity["crep_ntd2023_per_kwh"], "11h C_rep")
    return {
        "status": "PASS",
        "cost_package_sha256": sha256_file(root / AUTHORITY_PINS[8].path),
        "degradation_package_sha256": sha256_file(root / AUTHORITY_PINS[9].path),
        "join": "ONE_TO_ONE_BY_PACKAGE_ID_AND_1MW_BRACKET",
    }


def load_and_verify_package_authority(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    interface = read_json(root / "data/reference/production_economic_interface_v7_2.json")
    selector = interface.get("package_selector", {})
    if selector.get("outcome_dependent_switching_allowed") is not False:
        raise SensitivityAuthorityError("Outcome-dependent package switching is not blocked.")
    if selector.get("labels_are_power_bounds") is not False:
        raise SensitivityAuthorityError("Package labels were incorrectly treated as power bounds.")
    sensitivity = selector.get("cost_scale_sensitivity")
    mainline = selector.get("mainline")
    if not isinstance(sensitivity, dict) or not isinstance(mainline, dict):
        raise SensitivityAuthorityError("Economic interface does not contain both complete packages.")
    package_audit = validate_sensitivity_package(sensitivity, mainline)
    source_audit = verify_source_package_rows(root, sensitivity)
    monetary = interface.get("monetary_basis", {})
    if monetary.get("basis_label") != "constant NTD-2023":
        raise SensitivityAuthorityError("Monetary basis drifted from constant NTD-2023.")
    _assert_close(monetary.get("discount_rate"), 0.05, "real discount rate")
    if monetary.get("analysis_horizon_years") != 20:
        raise SensitivityAuthorityError("Analysis horizon drifted from 20 years.")
    _assert_close(monetary.get("crf"), EXPECTED_CRF, "CRF", 1e-12)
    _assert_close(interface.get("billing_demand_proxy", {}).get("kappa"), EXPECTED_KAPPA, "kappa")
    return copy.deepcopy(sensitivity), {
        **package_audit,
        "source_package_audit": source_audit,
        "monetary_basis": monetary,
        "economic_interface_sha256": sha256_file(
            root / "data/reference/production_economic_interface_v7_2.json"
        ),
    }


def adapt_inputs_to_1mw(inputs: Any, selected_package: Mapping[str, Any]) -> tuple[Any, dict[str, Any]]:
    if not dataclasses.is_dataclass(inputs):
        raise SensitivityAuthorityError("AnnualDesignInputs adapter requires a dataclass instance.")
    if not hasattr(inputs, "mainline_package"):
        raise SensitivityAuthorityError("AnnualDesignInputs has no mainline_package field.")
    original = inputs.mainline_package
    if canonical_object_sha256(original) != EXPECTED_MAINLINE_PACKAGE_SHA256:
        raise SensitivityAuthorityError("Loaded inputs do not contain the accepted 10 MW mainline package.")
    replacement = copy.deepcopy(dict(selected_package))
    if canonical_object_sha256(replacement) != EXPECTED_SENSITIVITY_PACKAGE_SHA256:
        raise SensitivityAuthorityError("Adapter received a non-authoritative sensitivity package.")
    adapted = dataclasses.replace(inputs, mainline_package=replacement)
    if adapted is inputs or adapted.mainline_package is original:
        raise SensitivityAuthorityError("Sensitivity adapter mutated or reused the canonical package object.")
    if canonical_object_sha256(inputs.mainline_package) != EXPECTED_MAINLINE_PACKAGE_SHA256:
        raise SensitivityAuthorityError("Canonical inputs were mutated by the sensitivity adapter.")
    if adapted.mainline_package is not replacement:
        raise SensitivityAuthorityError("Adapter lost single-object selected-package identity.")
    return adapted, replacement


def _literal_constants_from_core(core_path: Path) -> dict[str, Any]:
    source = core_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    values: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id in {
            "CORE_VERSION", "SOC_MIN", "SOC_MAX", "ETA_C", "ETA_D"
        }:
            values[target.id] = ast.literal_eval(node.value)
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    solve_node = functions["solve_eob"]
    optimize_calls = [
        node
        for node in ast.walk(solve_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "optimize"
    ]
    load_source = ast.get_source_segment(source, functions["load_annual_design_inputs"]) or ""
    build_source = ast.get_source_segment(source, functions["build_eob_model"]) or ""
    values.update(
        {
            "solve_eob_optimize_call_count": len(optimize_calls),
            "loader_is_mainline_only": "cost_scale_sensitivity" not in load_source,
            "builder_reads_inputs_package": "inputs.mainline_package" in build_source,
            "optimized_P_B_selector_absent": "P_B" not in load_source,
            "exact_d_present": "demand_exact_link_" in build_source,
            "constant_reserve_floor_present": "layer_a_reserve_floor_t" in build_source,
        }
    )
    return values


def verify_canonical_input(root: Path) -> dict[str, Any]:
    path = root / "data/processed/annual_input_v7_1.parquet"
    annual = pd.read_parquet(
        path,
        columns=[
            "timestamp",
            "baseline_load_kw",
            "pv_available_kw",
            "pv_long_unavailable_assumption",
            "pv_reconstruction_method",
        ],
    )
    if len(annual) != 8760:
        raise SensitivityAuthorityError("Canonical annual input is not 8,760 hours.")
    if (annual["baseline_load_kw"] < 0).any() or (annual["pv_available_kw"] < 0).any():
        raise SensitivityAuthorityError("Canonical Load/PV baseline contains negative values.")
    unavailable = annual["pv_long_unavailable_assumption"].astype(bool)
    if not unavailable.any():
        raise SensitivityAuthorityError("Canonical input has no conservative winter-PV interval.")
    if not np.allclose(annual.loc[unavailable, "pv_available_kw"].astype(float), 0.0):
        raise SensitivityAuthorityError("Mainline long-unavailable PV interval is not zero.")
    methods = set(annual.loc[unavailable, "pv_reconstruction_method"].astype(str))
    if methods != {"unavailable_zero_mainline"}:
        raise SensitivityAuthorityError(f"Unexpected mainline winter-PV methods: {methods}")
    return {
        "status": "PASS",
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "rows": len(annual),
        "long_unavailable_zero_hours": int(unavailable.sum()),
        "winter_pv_treatment": "MAINLINE_CONSERVATIVE_ZERO",
        "alternative_input_used": False,
    }


def verify_comparators(root: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for pin in COMPARATOR_PINS:
        result_path = root / pin.result_path
        manifest_path = root / pin.run_manifest_path
        if sha256_file(result_path) != pin.result_sha256:
            raise SensitivityAuthorityError(f"Comparator result hash mismatch: {pin.case_id}")
        if sha256_file(manifest_path) != pin.run_manifest_sha256:
            raise SensitivityAuthorityError(f"Comparator manifest hash mismatch: {pin.case_id}")
        result_record = read_json(result_path)
        result = result_record if pin.case_id == "EOB" else result_record.get("result", {})
        if result.get("status") != "OPTIMAL" or result.get("mode") != "binary":
            raise SensitivityAuthorityError(f"Comparator is not accepted optimal binary: {pin.case_id}")
        manifest = read_json(manifest_path)
        if manifest.get("run_id") != pin.run_id:
            raise SensitivityAuthorityError(f"Comparator run ID mismatch: {pin.case_id}")
        if pin.case_id == "EOB":
            if manifest.get("core_sha256") != EXPECTED_CORE_SHA256:
                raise SensitivityAuthorityError("EOB comparator is not corrected-core r10.")
            completion_status = "ACCEPTED_BY_ADDITIVE_CHECKPOINT"
        else:
            if manifest.get("source_hashes_at_start", {}).get("annual_core") != EXPECTED_CORE_SHA256:
                raise SensitivityAuthorityError(f"Representative core mismatch: {pin.case_id}")
            if manifest.get("requested_time_limit_sec") is not None:
                raise SensitivityAuthorityError(f"Representative TimeLimit mismatch: {pin.case_id}")
            completion_path = root / str(pin.completion_path)
            if sha256_file(completion_path) != pin.completion_sha256:
                raise SensitivityAuthorityError(f"Comparator completion hash mismatch: {pin.case_id}")
            completion = read_json(completion_path)
            if completion.get("status") != "REPRESENTATIVE_PASS" or completion.get("all_gates_pass") is not True:
                raise SensitivityAuthorityError(f"Representative completion rejected: {pin.case_id}")
            completion_status = completion["status"]
        records[pin.case_id] = {
            "run_id": pin.run_id,
            "result_path": pin.result_path,
            "result_sha256": pin.result_sha256,
            "run_manifest_path": pin.run_manifest_path,
            "run_manifest_sha256": pin.run_manifest_sha256,
            "completion_status": completion_status,
            "reuse_only": True,
            "future_mainline_solve_count": 0,
        }
    if tuple(records) != ALLOWED_CASE_IDS:
        raise SensitivityAuthorityError("Comparator map does not exactly match the six-case allow-list.")
    return records


def validate_authority(root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    repository = repository_authority(root)
    hashes = verify_file_pins(root)
    selected_package, package_audit = load_and_verify_package_authority(root)
    canonical = verify_canonical_input(root)
    comparators = verify_comparators(root)
    core_static = _literal_constants_from_core(root / "src/annual_design_model_v7_2.py")
    expected_core_static = {
        "CORE_VERSION": EXPECTED_CORE_VERSION,
        "SOC_MIN": 0.10,
        "SOC_MAX": 0.90,
        "ETA_C": 0.90,
        "ETA_D": 0.90,
        "solve_eob_optimize_call_count": 1,
        "loader_is_mainline_only": True,
        "builder_reads_inputs_package": True,
        "optimized_P_B_selector_absent": True,
        "exact_d_present": True,
        "constant_reserve_floor_present": True,
    }
    if core_static != expected_core_static:
        raise SensitivityAuthorityError(
            f"Corrected-core static contract mismatch: {core_static}"
        )
    output_root = (root / OUTPUT_ROOT_RELATIVE).resolve()
    protected_roots = [
        (root / "results/eob_production").resolve(),
        (root / "results/eob_production_corrected").resolve(),
        (root / "results/layer_a").resolve(),
        (root / "results/sensitivity/winter_pv_17c").resolve(),
    ]
    if output_root in protected_roots or any(
        output_root == protected or protected in output_root.parents for protected in protected_roots
    ):
        raise SensitivityAuthorityError("Sensitivity output namespace collides with protected results.")

    return {
        "status": "PASS",
        "mode": "READ_ONLY_NO_SOLVE_NO_WRITE",
        "script_version": SCRIPT_VERSION,
        "sensitivity_type": "PNNL_1MW_BESS_COST_SCALE_FULL_PACKAGE",
        "repository": repository,
        "authority_hashes": hashes,
        "package": {**package_audit, "selected_package": selected_package},
        "canonical_input": canonical,
        "core_static_contract": core_static,
        "fair_comparison": {
            "only_changed_factor": "COMPLETE_PNNL_1MW_COST_AND_DEGRADATION_PACKAGE",
            "winter_pv": "MAINLINE_CONSERVATIVE_ZERO",
            "soc_window": [0.10, 0.90],
            "efficiency": {"eta_c": 0.90, "eta_d": 0.90},
            "reserve_floor": "CONSTANT_WORST_CASE_CASE_SPECIFIC_REQUIREMENT",
            "outage_start_enumeration": "VALID_NONCIRCULAR_STARTS_ONLY",
            "monetary_basis": "constant NTD-2023",
            "discount_rate_real": 0.05,
            "analysis_horizon_years": 20,
        },
        "allowed_cases": [asdict(case) for case in ALLOWED_CASES],
        "comparators": comparators,
        "solver_contract": SOLVER_CONTRACT,
        "output_contract": {
            "namespace": OUTPUT_ROOT_RELATIVE.as_posix() + "/<run_id>",
            "terminal_state": "exactly one of completion_manifest.json or failure_manifest.json",
            "artifact_registry_fields": ["path", "sha256", "bytes", "role"],
        },
        "execution_counters": {
            "model_constructions": 0,
            "optimization_calls": 0,
            "solve_eob_calls": 0,
            "new_1mw_cases": 0,
            "mainline_comparator_solves": 0,
        },
    }


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SensitivityAuthorityError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class OptimizeCallGuard(AbstractContextManager["OptimizeCallGuard"]):
    """Count the sole allowed optimize method and block alternate solver paths."""

    def __init__(self, gp_module: Any, maximum_calls: int) -> None:
        self.gp = gp_module
        self.maximum_calls = maximum_calls
        self.count = 0
        self._originals: dict[str, Any] = {}

    def __enter__(self) -> "OptimizeCallGuard":
        model_type = self.gp.Model
        for method_name in (
            "optimize", "optimizeAsync", "optimizeBatch", "tune", "feasRelax", "feasRelaxS"
        ):
            if hasattr(model_type, method_name):
                self._originals[method_name] = getattr(model_type, method_name)
        original_optimize = self._originals["optimize"]

        def guarded_optimize(model: Any, *args: Any, **kwargs: Any) -> Any:
            if self.count >= self.maximum_calls:
                raise SensitivityAuthorityError("Optimize-call contract exceeded six calls.")
            self.count += 1
            return original_optimize(model, *args, **kwargs)

        def forbidden(*_: Any, **__: Any) -> None:
            raise SensitivityAuthorityError("Forbidden alternate solver method reached.")

        setattr(model_type, "optimize", guarded_optimize)
        for method_name in self._originals:
            if method_name != "optimize":
                setattr(model_type, method_name, forbidden)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        for method_name, original in self._originals.items():
            setattr(self.gp.Model, method_name, original)
        return None

    def assert_one_new_call(self, before: int, case_id: str) -> None:
        if self.count != before + 1:
            raise SensitivityAuthorityError(
                f"Case {case_id} made {self.count - before} optimize calls; expected exactly one."
            )


def new_run_id() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:10]}"


def allocate_run_directory(root: Path, run_id: str) -> Path:
    output_root = (root / OUTPUT_ROOT_RELATIVE).resolve()
    expected_parent = (root / "results/sensitivity/bess_cost_scale_1mw").resolve()
    if expected_parent not in output_root.parents:
        raise SensitivityAuthorityError("Output root escaped dedicated sensitivity namespace.")
    run_dir = output_root / run_id
    if run_dir.exists():
        raise SensitivityAuthorityError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    if (run_dir / "completion_manifest.json").exists() or (run_dir / "failure_manifest.json").exists():
        raise SensitivityAuthorityError("New run directory already has a terminal manifest.")
    return run_dir


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


def strip_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {"dispatch", "billing_exact", "transition_settlement_detail"}
    }


def base_post_solve_gates(
    result: Mapping[str, Any], billing_audit: Mapping[str, Any], rainflow: Mapping[str, Any]
) -> dict[str, str]:
    physical = result.get("physical_diagnostics", {})
    rainflow_pass = (
        rainflow.get("summary", {}).get("verdict") == "RAINFLOW_VALIDATION_PASS"
        and all(value == "PASS" for value in rainflow.get("gates", {}).values())
    )
    return {
        "solver_optimal": "PASS" if result.get("status") == "OPTIMAL" else "FAIL",
        "binary_formulation": "PASS" if result.get("mode") == "binary" else "FAIL",
        "mip_gap": "PASS" if result.get("mip_gap") is not None and float(result["mip_gap"]) <= MIP_GAP else "FAIL",
        "ac_balance": "PASS" if float(physical.get("max_ac_balance_residual_kw", math.inf)) <= 1e-5 else "FAIL",
        "segment_dynamics": "PASS" if float(physical.get("max_segment_dynamics_residual_kwh", math.inf)) <= 1e-5 else "FAIL",
        "segment_cyclic": "PASS" if float(physical.get("max_segment_cyclic_residual_kwh", math.inf)) <= 1e-5 else "FAIL",
        "technical_soc": "PASS" if float(physical.get("soc_min_realized", -math.inf)) >= 0.10 - 1e-6 and float(physical.get("soc_max_realized", math.inf)) <= 0.90 + 1e-6 else "FAIL",
        "simultaneous_charge_discharge": "PASS" if int(physical.get("simultaneous_hours_above_tol", -1)) == 0 else "FAIL",
        "cost_reconciliation": "PASS" if abs(float(result.get("cost_reconciliation_residual_ntd", math.inf))) <= 1e-3 else "FAIL",
        "transition_ambiguity": "PASS" if result.get("transition_settlement", {}).get("nonbinding_certificate") == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE" else "FAIL",
        "billing_structure": "PASS" if all(value == "PASS" for key, value in billing_audit.items() if key in {"period_ids", "detail_columns", "valid_detail_keys", "duplicate_detail_keys", "tariff_calendar_structure"}) else "FAIL",
        "rainflow_validation": "PASS" if rainflow_pass else "FAIL",
    }


def selected_package_cost_audit(
    result: Mapping[str, Any], selected_package: Mapping[str, Any], eta_d: float
) -> dict[str, Any]:
    sizing = result["sizing"]
    costs = result["cost_components_ntd2023_per_year"]
    energy = float(sizing["E_N_kwh"])
    power = float(sizing["P_B_kw_ac"])
    expected_capex = (
        energy * float(selected_package["annualized_capex_C_E_ntd2023_per_kwh_year"])
        + power * float(selected_package["annualized_capex_C_P_ntd2023_per_kw_year"])
    )
    expected_fom = (
        energy * float(selected_package["fom_E_ntd2023_per_kwh_year"])
        + power * float(selected_package["fom_P_ntd2023_per_kw_year"])
    )
    dispatch = result["dispatch"]
    expected_degradation = 0.0
    for index in range(1, 4):
        column = f"p_discharge_seg_{index}_kw_ac"
        expected_degradation += (
            float(selected_package[f"lambda_{index}_ntd2023_per_battery_side_discharged_kwh"])
            * float(dispatch[column].sum())
            / eta_d
        )
    residuals = {
        "annualized_capex_ntd": float(costs["annualized_capex"]) - expected_capex,
        "fom_ntd": float(costs["fom"]) - expected_fom,
        "degradation_ntd": float(costs["degradation"]) - expected_degradation,
    }
    status = "PASS" if max(abs(value) for value in residuals.values()) <= 1e-3 else "FAIL"
    if status != "PASS":
        raise SensitivityAuthorityError(f"Selected-package cost audit failed: {residuals}")
    return {
        "status": status,
        "package_id": selected_package["package_id"],
        "package_object_sha256": canonical_object_sha256(selected_package),
        "C_rep_ntd2023_per_kwh": selected_package["crep_ntd2023_per_kwh"],
        "lambdas": [
            selected_package[f"lambda_{index}_ntd2023_per_battery_side_discharged_kwh"]
            for index in range(1, 4)
        ],
        "reconciliation_residuals": residuals,
    }


def write_case_artifacts(
    case_dir: Path,
    case_id: str,
    result: Mapping[str, Any],
    billing_audit: Mapping[str, Any],
    gates: Mapping[str, str],
    cost_audit: Mapping[str, Any],
    rainflow: Mapping[str, Any],
    analytical_requirement: Mapping[str, Any] | None,
) -> None:
    write_json(case_dir / "result.json", strip_result(result))
    result["dispatch"].to_parquet(case_dir / "dispatch.parquet", index=False)
    result["billing_exact"].to_csv(case_dir / "billing_exact.csv", index=False, encoding="utf-8-sig")
    result["transition_settlement_detail"].to_csv(
        case_dir / "transition_settlement_detail.csv", index=False, encoding="utf-8-sig"
    )
    write_json(case_dir / "billing_audit.json", {"status": "PASS", **billing_audit})
    write_json(
        case_dir / "exact_demand_audit.json",
        {
            "status": gates.get("billing_structure"),
            "cost_facing_exact_d": True,
            "postsolve_recomputed": True,
            "physical_diagnostics": result.get("physical_diagnostics", {}),
        },
    )
    write_json(
        case_dir / "transition_settlement_audit.json",
        {"status": gates.get("transition_ambiguity"), **result.get("transition_settlement", {})},
    )
    write_json(
        case_dir / "physical_balance_audit.json",
        {"status": "PASS" if all(gates.get(key) == "PASS" for key in ("ac_balance", "segment_dynamics", "segment_cyclic", "technical_soc", "simultaneous_charge_discharge")) else "FAIL", "gates": dict(gates), "diagnostics": result.get("physical_diagnostics", {})},
    )
    write_json(case_dir / "degradation_cost_audit.json", cost_audit)
    write_json(
        case_dir / "rainflow_audit.json",
        {
            "summary": rainflow.get("summary", {}),
            "gates": rainflow.get("gates", {}),
            "algorithm_self_test": rainflow.get("algorithm_self_test", {}),
        },
    )
    for name in ("cycles", "turning_points", "depth_bins", "pwl_segments", "g_curve"):
        rainflow[name].to_csv(case_dir / f"rainflow_{name}.csv", index=False, encoding="utf-8-sig")
    write_json(
        case_dir / "analytical_adequacy_audit.json",
        {
            "status": "NOT_APPLICABLE_EOB" if analytical_requirement is None else "PASS",
            "case_id": case_id,
            "requirement": analytical_requirement,
            "layer_a_resilience": result.get("layer_a_resilience"),
        },
    )
    write_json(case_dir / "post_solve_gate.json", {"status": "PASS", "gates": dict(gates)})


def scenario_metrics(result: Mapping[str, Any]) -> dict[str, float]:
    costs = result["cost_components_ntd2023_per_year"]
    sizing = result["sizing"]
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


def artifact_role(path: Path) -> str:
    name = path.name
    if name.endswith(".log"):
        return "solver_log"
    if "manifest" in name:
        return "manifest"
    if "audit" in name or "gate" in name:
        return "audit"
    if "comparison" in name:
        return "paired_comparison"
    if "telemetry" in name:
        return "solver_telemetry"
    if name == "result.json":
        return "solve_result"
    if "dispatch" in name:
        return "dispatch"
    return "supporting_evidence"


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
            "role": artifact_role(path),
        }
    return registry


def run_manifest_payload(
    root: Path, run_id: str, authority: Mapping[str, Any]
) -> dict[str, Any]:
    package = authority["package"]["selected_package"]
    return {
        "schema_version": "v7.2-bess-cost-scale-1mw-run-manifest-1",
        "status": "CANDIDATE_EXECUTION_STARTED_NOT_ACCEPTED",
        "run_id": run_id,
        "started_utc": utc_text(),
        "script_version": SCRIPT_VERSION,
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "sensitivity_type": "PNNL_1MW_BESS_COST_SCALE_FULL_PACKAGE",
        "one_factor_change": "FULL_1MW_PACKAGE_ONLY",
        "selected_package": {
            "role": package["role"],
            "package_id": package["package_id"],
            "package_object_sha256": EXPECTED_SENSITIVITY_PACKAGE_SHA256,
            **{field: package[field] for field in REQUIRED_PACKAGE_FIELDS if field not in {"role", "package_id"}},
        },
        "monetary_basis": authority["package"]["monetary_basis"],
        "canonical_annual_input_sha256": authority["canonical_input"]["sha256"],
        "core_sha256": EXPECTED_CORE_SHA256,
        "interface_hashes": {
            key: authority["authority_hashes"][key]["actual_sha256"]
            for key in ("economic_interface", "optimization_tariff", "settlement_interface", "settlement_matrix")
        },
        "solver_settings": SOLVER_CONTRACT,
        "authorized_cases": [asdict(case) for case in ALLOWED_CASES],
        "accepted_comparators": authority["comparators"],
        "solve_count_contract": {
            "new_1mw": EXPECTED_FUTURE_OPTIMIZE_CALLS,
            "reused_10mw": len(COMPARATOR_PINS),
            "new_10mw": 0,
        },
        "output_namespace": OUTPUT_ROOT_RELATIVE.as_posix(),
        "acceptance_status": "CANDIDATE_PENDING_INDEPENDENT_POST_RUN_AUDIT",
    }


def execute_production(root: Path, authority: Mapping[str, Any]) -> Path:
    """Execute six future candidate solves; never called by the default mode."""
    if authority.get("status") != "PASS":
        raise SensitivityAuthorityError("Execution requires a passing pre-solve authority gate.")
    # Re-run every read-only authority check immediately before allocating output.
    live = validate_authority(root)
    if canonical_object_sha256(live["package"]["selected_package"]) != EXPECTED_SENSITIVITY_PACKAGE_SHA256:
        raise SensitivityAuthorityError("Live selected package changed before execution.")

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import gurobipy as gp
    from src.annual_design_model_v7_2 import (
        CORE_VERSION,
        ETA_D,
        SOC_MAX,
        SOC_MIN,
        LayerAResilienceRequirements,
        SolveSettings,
        load_annual_design_inputs,
        solve_eob,
    )

    if CORE_VERSION != EXPECTED_CORE_VERSION or sha256_file(root / "src/annual_design_model_v7_2.py") != EXPECTED_CORE_SHA256:
        raise SensitivityAuthorityError("Corrected core changed at runtime.")
    helper = load_module(
        root / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
        "script16a_cost_scale_helpers",
    )
    canonical_inputs = load_annual_design_inputs(
        root,
        annual_parquet=root / "data/processed/annual_input_v7_1.parquet",
        annual_csv=root / "data/processed/annual_input_v7_1.csv",
        economic_interface_path=root / "data/reference/production_economic_interface_v7_2.json",
        normalized_tariff_path=root / "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
        settlement_interface_path=root / "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
        settlement_matrix_path=root / "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
    )
    sensitivity_inputs, selected_package = adapt_inputs_to_1mw(
        canonical_inputs, live["package"]["selected_package"]
    )
    if sensitivity_inputs.mainline_package is not selected_package:
        raise SensitivityAuthorityError("Solver/reporting package object identity diverged.")
    surface, _starts, analytical_audit = helper.analytical_surface(
        sensitivity_inputs.annual,
        eta_d=float(ETA_D),
        soc_min=float(SOC_MIN),
        soc_max=float(SOC_MAX),
    )
    if analytical_audit.get("status") != "PASS":
        raise SensitivityAuthorityError("Accepted analytical outage semantics did not reproduce.")

    run_id = new_run_id()
    run_dir: Path | None = None
    completed_cases: dict[str, dict[str, Any]] = {}
    try:
        run_dir = allocate_run_directory(root, run_id)
        write_json(run_dir / "pre_solve_gate.json", live)
        write_json(run_dir / "run_manifest.json", run_manifest_payload(root, run_id, live))

        sensitivity_eob: dict[str, Any] | None = None
        with OptimizeCallGuard(gp, EXPECTED_FUTURE_OPTIMIZE_CALLS) as guard:
            for case in ALLOWED_CASES:
                require_authorized_case(case.case_id)
                case_dir = run_dir / "cases" / case.case_id
                case_dir.mkdir(parents=True, exist_ok=False)
                log_path = case_dir / "gurobi.log"
                telemetry_path = case_dir / "solver_telemetry.jsonl"
                requirement: dict[str, Any] | None = None
                layer_requirement = None
                if case.case_id != "EOB":
                    rows = surface.loc[surface["case_id"].eq(case.case_id)]
                    if len(rows) != 1:
                        raise SensitivityAuthorityError(f"Analytical case identity mismatch: {case.case_id}")
                    requirement = rows.iloc[0].to_dict()
                    layer_requirement = LayerAResilienceRequirements(
                        alpha=float(case.alpha),
                        beta_h=int(case.beta_h),
                        reserve_kwh_battery=float(requirement["R_kwh_battery"]),
                        power_requirement_kw_ac=float(requirement["P_out_kw_ac"]),
                    )
                write_json(
                    case_dir / "case_manifest.json",
                    {
                        "run_id": run_id,
                        "case": asdict(case),
                        "selected_package_id": selected_package["package_id"],
                        "selected_package_object_sha256": canonical_object_sha256(selected_package),
                        "accepted_comparator": live["comparators"][case.case_id],
                        "solver_settings": SOLVER_CONTRACT,
                        "analytical_requirement": requirement,
                    },
                )
                settings = SolveSettings(
                    mode="binary",
                    mip_gap=MIP_GAP,
                    time_limit_sec=TIME_LIMIT_SEC,
                    output_flag=OUTPUT_FLAG,
                    numeric_focus=NUMERIC_FOCUS,
                    log_file=str(log_path),
                    telemetry_callback=telemetry_writer(telemetry_path, case.case_id),
                )
                before = guard.count
                started = time.perf_counter()
                result = solve_eob(sensitivity_inputs, settings, layer_requirement)
                guard.assert_one_new_call(before, case.case_id)
                if sensitivity_inputs.mainline_package is not selected_package:
                    raise SensitivityAuthorityError("Selected package object changed during solve.")
                result["selected_economic_package"] = selected_package
                if result["selected_economic_package"] is not selected_package:
                    raise SensitivityAuthorityError(
                        "Result metadata diverged from the solver-facing package object."
                    )
                rainflow = helper.validate_representative_rainflow(
                    root, sensitivity_inputs, result
                )
                billing = helper.billing_structure_audit(
                    result["billing_exact"], sensitivity_inputs.annual
                )
                if case.case_id == "EOB":
                    gates = base_post_solve_gates(result, billing, rainflow)
                    sensitivity_eob = result
                else:
                    if sensitivity_eob is None:
                        raise SensitivityAuthorityError("Layer-A case reached before sensitivity EOB.")
                    gates = helper.representative_gate(
                        result,
                        requirement,
                        sensitivity_eob,
                        soc_min=float(SOC_MIN),
                        soc_max=float(SOC_MAX),
                        rainflow_validation=rainflow,
                        billing_audit=billing,
                    )
                    gates["all_start_enumeration"] = (
                        "PASS" if bool(requirement.get("valid_start_count")) else "FAIL"
                    )
                    gates["exact_case_identity"] = (
                        "PASS"
                        if result.get("layer_a_resilience", {}).get("alpha") == float(case.alpha)
                        and result.get("layer_a_resilience", {}).get("beta_h") == int(case.beta_h)
                        else "FAIL"
                    )
                cost_audit = selected_package_cost_audit(result, selected_package, float(ETA_D))
                gates["selected_package_cost_consistency"] = cost_audit["status"]
                gates["selected_package_identity"] = (
                    "PASS"
                    if cost_audit["package_object_sha256"] == EXPECTED_SENSITIVITY_PACKAGE_SHA256
                    else "FAIL"
                )
                if not all(value == "PASS" for value in gates.values()):
                    raise SensitivityAuthorityError(
                        f"Post-solve gate failed for {case.case_id}: {gates}"
                    )
                write_case_artifacts(
                    case_dir,
                    case.case_id,
                    result,
                    billing,
                    gates,
                    cost_audit,
                    rainflow,
                    requirement,
                )
                completed_cases[case.case_id] = {
                    "result": strip_result(result),
                    "elapsed_wall_seconds": time.perf_counter() - started,
                    "gates": gates,
                }
            if guard.count != EXPECTED_FUTURE_OPTIMIZE_CALLS:
                raise SensitivityAuthorityError(
                    f"Final optimize count={guard.count}; expected={EXPECTED_FUTURE_OPTIMIZE_CALLS}."
                )

        rows: list[dict[str, Any]] = []
        comparison_json: dict[str, Any] = {
            "status": "PASS",
            "sensitivity_type": "PNNL_1MW_BESS_COST_SCALE_FULL_PACKAGE",
            "selected_package_id": selected_package["package_id"],
            "selected_package_object_sha256": EXPECTED_SENSITIVITY_PACKAGE_SHA256,
            "selected_package": selected_package,
            "mainline_package_object_sha256": EXPECTED_MAINLINE_PACKAGE_SHA256,
            "cases": {},
            "claim_boundary": "Targeted EOB plus five representative cases; not a complete alternative 81-point response surface.",
        }
        for pin in COMPARATOR_PINS:
            mainline_metrics = scenario_metrics(load_comparator_result(root, pin))
            sensitivity_metrics = scenario_metrics(completed_cases[pin.case_id]["result"])
            metrics: dict[str, Any] = {}
            for metric in mainline_metrics:
                main_value = mainline_metrics[metric]
                sensitivity_value = sensitivity_metrics[metric]
                delta = sensitivity_value - main_value
                metrics[metric] = {
                    "mainline_10mw": main_value,
                    "sensitivity_1mw": sensitivity_value,
                    "delta_1mw_minus_10mw": delta,
                    "delta_pct_of_mainline": None if main_value == 0 else 100.0 * delta / main_value,
                }
                rows.append({"case_id": pin.case_id, "metric": metric, **metrics[metric]})
            comparison_json["cases"][pin.case_id] = {
                "accepted_comparator": live["comparators"][pin.case_id],
                "metrics": metrics,
            }
        write_json(run_dir / "paired_sensitivity_comparison.json", comparison_json)
        pd.DataFrame(rows).to_csv(
            run_dir / "paired_sensitivity_comparison.csv", index=False, encoding="utf-8-sig"
        )
        registry = build_artifact_registry(run_dir)
        completion = {
            "schema_version": "v7.2-bess-cost-scale-1mw-completion-manifest-1",
            "run_id": run_id,
            "status": "CANDIDATE_PASS_PENDING_INDEPENDENT_POST_RUN_AUDIT",
            "completed_utc": utc_text(),
            "script_version": SCRIPT_VERSION,
            "script_sha256": sha256_file(Path(__file__).resolve()),
            "solve_count": EXPECTED_FUTURE_OPTIMIZE_CALLS,
            "new_1mw_cases": list(ALLOWED_CASE_IDS),
            "mainline_comparator_solves": 0,
            "selected_package_id": selected_package["package_id"],
            "selected_package_object_sha256": EXPECTED_SENSITIVITY_PACKAGE_SHA256,
            "artifact_registry": registry,
            "completion_is_not_self_acceptance": True,
        }
        write_json(run_dir / "completion_manifest.json", completion)
        if (run_dir / "failure_manifest.json").exists():
            raise SensitivityAuthorityError("Both terminal manifests exist.")
        return run_dir / "completion_manifest.json"
    except Exception as exc:
        if run_dir is not None and run_dir.exists() and not (run_dir / "completion_manifest.json").exists():
            failure_path = run_dir / "failure_manifest.json"
            if not failure_path.exists():
                write_json(
                    failure_path,
                    {
                        "schema_version": "v7.2-bess-cost-scale-1mw-failure-manifest-1",
                        "run_id": run_id,
                        "status": "FAIL",
                        "failed_utc": utc_text(),
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "completed_cases": list(completed_cases),
                        "completion_manifest_written": False,
                    },
                )
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-production",
        action="store_true",
        help=(
            "Explicitly enter the six-case solve path. This flag must not be used "
            "until a separate independent no-solve audit authorizes execution."
        ),
    )
    return parser.parse_args(argv)


def run(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    validator: Callable[[Path], dict[str, Any]] = validate_authority,
    executor: Callable[[Path, Mapping[str, Any]], Path] = execute_production,
) -> int:
    args = parse_args(argv)
    root = (root or project_root()).resolve()
    authority = validator(root)
    if not args.execute_production:
        print(json.dumps(json_safe(authority), indent=2, allow_nan=False))
        return 0
    if authority.get("status") != "PASS":
        raise SensitivityAuthorityError(
            "Explicit execution was requested without a passing pre-solve gate."
        )
    completion = executor(root, authority)
    print(
        json.dumps(
            {
                "status": "CANDIDATE_EXECUTION_COMPLETE_PENDING_INDEPENDENT_AUDIT",
                "completion_manifest": str(completion),
            },
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
