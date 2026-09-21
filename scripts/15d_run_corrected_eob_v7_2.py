#!/usr/bin/env python3
"""Provenance-gated driver for one future corrected production EOB run.

``--validate-only`` is intentionally implemented with the Python standard
library plus a Parquet metadata reader.  It never imports the annual model or
Gurobi.  ``--runtime-import-check`` imports the accepted production runtime
behind guards that prohibit model construction and optimization.  Only
``--execute-production`` calls ``solve_eob``; that path requires a separate
authorization.

This file contains orchestration, provenance checks, output allocation, and
serialization only.  The optimization formulation remains exclusively in
``src/annual_design_model_v7_2.py``.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as dt
import hashlib
import json
import math
import re
import subprocess
import sys
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo


SCRIPT_VERSION = "v7.2-corrected-eob-production-driver-2026-09-17-r2-runtime-import-repair"
DRIVER_RELATIVE_PATH = Path("scripts/15d_run_corrected_eob_v7_2.py")
EXPECTED_BRANCH = "thesis-v7"
EXPECTED_CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
)
EXPECTED_CORE_SHA256 = (
    "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8"
)
CORE_RELATIVE_PATH = Path("src/annual_design_model_v7_2.py")

GATE6_RELATIVE_DIR = Path(
    "results/provenance/production_rerun_v7_2_20260915/"
    "gate6_corrected_eob_authorization"
)
EXECUTION_CONTRACT_RELATIVE_PATH = (
    GATE6_RELATIVE_DIR / "gate6_eob_execution_contract_2026-09-17.json"
)
EXECUTION_CONTRACT_SHA256 = (
    "94c251a93356870c978acb97c25ee64680b1f40eee0680ef121483d9aa51e601"
)
ACCEPTANCE_CONTRACT_RELATIVE_PATH = (
    GATE6_RELATIVE_DIR / "gate6_eob_acceptance_contract_2026-09-17.json"
)
ACCEPTANCE_CONTRACT_SHA256 = (
    "dca4c62dfde4db3747582d152a6ca05fe3cfcd0d7a19f51fa115a8d870bc776e"
)

CORRECTED_OUTPUT_ROOT_RELATIVE_PATH = Path(
    "results/eob_production_corrected/runs"
)
HISTORICAL_OUTPUT_RELATIVE_PATH = Path("results/eob_production")
CANDIDATE_AUTHORITY = "CORRECTED_EOB_CANDIDATE_PENDING_AUDIT"
EXPECTED_ANNUAL_ROWS = 8760
EXPECTED_KAPPA = 1.0103668594376984
RUN_ID_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{12}Z_[0-9a-f]{10}$")


@dataclass(frozen=True)
class DependencyPin:
    label: str
    path: str
    sha256: str


DEPENDENCY_PINS: tuple[DependencyPin, ...] = (
    DependencyPin(
        "canonical_annual_input",
        "data/processed/annual_input_v7_1.parquet",
        "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e",
    ),
    DependencyPin(
        "companion_annual_input_csv",
        "data/processed/annual_input_v7_1.csv",
        "6ab785081d6ca99c81a8c4b7083deb130a6372a00fa1532ff32247c543e75ef4",
    ),
    DependencyPin(
        "economic_interface_14a",
        "data/reference/production_economic_interface_v7_2.json",
        "9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9",
    ),
    DependencyPin(
        "normalized_tariff_14a",
        "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
        "5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395",
    ),
    DependencyPin(
        "settlement_interface_14b",
        "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
        "f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88",
    ),
    DependencyPin(
        "settlement_matrix_14b",
        "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
        "ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79",
    ),
    DependencyPin(
        "tariff_registry_13b",
        "data/reference/taipower_tariff_registry_v7_1.csv",
        "20333b3c521ed77ebbc38cc427dd58a6c3acd61047ac95befdf3d3223f8226dd",
    ),
    DependencyPin(
        "parameter_registry",
        "data/reference/parameter_registry_v7_2.csv",
        "c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1",
    ),
    DependencyPin(
        "pnnl_cost_package",
        "results/parameter_audit/pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv",
        "f0c167001cf554804152d5f5eb114ee9403c784bb7937f3c5c90bf000203b3e7",
    ),
    DependencyPin(
        "pnnl_technical_provenance",
        "results/parameter_audit/pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv",
        "1172963521fbc4b646394cb2df6947ade9f961211bf608c5928ef4de215644f6",
    ),
    DependencyPin(
        "degradation_package",
        "results/parameter_audit/pnnl_calibrated_pwl_degradation_candidate_packages.csv",
        "6921ae2171da8318945a48280b41780a9c26ce70a15b373088f6dfb486a1eff3",
    ),
    DependencyPin(
        "kappa_calibration_pairs_08",
        "results/data_audit/kappa_calibration_pairs_v7_1.csv",
        "c8e32a279f7f3c1b16cda6254831621147d03a9ccaadc4190fb44a7a7ba30020",
    ),
    DependencyPin(
        "observed_bills_clean",
        "data/reference/taipower_bills_final_clean.csv",
        "e18d05a1cec3917b0f69f9a769e549ab50228f060ac7bf6bd06361a4b247f34d",
    ),
)

PRODUCTION_SOLVER_POLICY: dict[str, Any] = {
    "solver": "Gurobi",
    "mode": "binary",
    "MIPGap": 1e-6,
    "OutputFlag": 1,
    "NumericFocus": 1,
    "TimeLimit": {
        "driver_sets_parameter": False,
        "required_readback_for_gate7": "INFINITY",
    },
    "NodeLimit": {
        "driver_sets_parameter": False,
        "required_readback_for_gate7": "INFINITY",
    },
    "Cuts": {"driver_sets_parameter": False, "uses_solver_default": True},
    "Heuristics": {"driver_sets_parameter": False, "uses_solver_default": True},
    "MIPFocus": {"driver_sets_parameter": False, "uses_solver_default": True},
    "Method": {"driver_sets_parameter": False, "uses_solver_default": True},
    "Presolve": {"driver_sets_parameter": False, "uses_solver_default": True},
    "automatic_retry_with_changed_parameters": False,
    "layer_a_requirements": None,
}


class ProvenanceError(RuntimeError):
    """A hard authority or output-safety mismatch detected before a solve."""


@dataclass(frozen=True)
class RuntimeBindings:
    core_version: str
    solve_settings_type: Any
    load_inputs: Callable[..., Any]
    solve_eob: Callable[..., dict[str, Any]]
    solver_name: str
    solver_version: str


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _bootstrap_repository_import_path(root: Path) -> None:
    """Make sibling repository packages importable for ``python scripts/...``."""

    resolved = str(root.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProvenanceError(f"Expected a JSON object: {path}")
    return value


def _within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _repo_path(root: Path, relative: str | Path) -> Path:
    candidate = root / Path(relative)
    if not _within(root, candidate):
        raise ProvenanceError(f"Repository path escapes the project root: {relative}")
    return candidate


def _git_repository_state(root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return completed.stdout.strip()

    return {
        "branch": run("branch", "--show-current"),
        "HEAD": run("rev-parse", "HEAD"),
        "working_tree_status": run("status", "--short"),
    }


def _core_version_from_source(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == "CORE_VERSION" for target in targets):
                value_node = node.value
                value = ast.literal_eval(value_node)
                if isinstance(value, str):
                    return value
    raise ProvenanceError(f"CORE_VERSION string not found in {path}")


def _parquet_row_count(path: Path) -> int:
    try:
        import pyarrow.parquet as parquet  # type: ignore
    except ImportError as exc:  # pragma: no cover - production environment gate
        raise ProvenanceError(
            "pyarrow is required to validate the canonical Parquet row count."
        ) from exc
    return int(parquet.ParquetFile(path).metadata.num_rows)


def _pin_map() -> dict[str, DependencyPin]:
    return {pin.label: pin for pin in DEPENDENCY_PINS}


def _assert_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise ProvenanceError(
            f"Gate-6 contract mismatch for {label}: expected={expected!r}, actual={actual!r}"
        )


def _validate_contract_alignment(execution: Mapping[str, Any]) -> None:
    pins = _pin_map()
    core = execution.get("A_core", {})
    _assert_equal("A_core.core_version", core.get("core_version"), EXPECTED_CORE_VERSION)
    _assert_equal("A_core.core_sha256", core.get("core_sha256"), EXPECTED_CORE_SHA256)

    annual = pins["canonical_annual_input"]
    companion = pins["companion_annual_input_csv"]
    input_contract = execution.get("B_input", {})
    _assert_equal(
        "B_input.canonical_annual_input_path",
        input_contract.get("canonical_annual_input_path"),
        annual.path,
    )
    _assert_equal(
        "B_input.canonical_annual_input_sha256",
        input_contract.get("canonical_annual_input_sha256"),
        annual.sha256,
    )
    _assert_equal("B_input.companion_csv_path", input_contract.get("companion_csv_path"), companion.path)
    _assert_equal(
        "B_input.companion_csv_sha256",
        input_contract.get("companion_csv_sha256"),
        companion.sha256,
    )
    _assert_equal("B_input.rows_expected", input_contract.get("rows_expected"), EXPECTED_ANNUAL_ROWS)

    interface_keys = {
        "economic_interface_14a": "economic_interface_14a",
        "normalized_tariff_14a": "normalized_tariff_14a",
        "settlement_interface_14b": "settlement_interface_14b",
        "settlement_matrix_14b": "settlement_matrix_14b",
        "tariff_registry_13b": "tariff_registry_13b",
        "parameter_registry": "parameter_registry",
        "pnnl_cost_package": "pnnl_cost_package",
        "pnnl_technical_provenance": "pnnl_technical_provenance",
        "degradation_package": "degradation_package",
        "kappa_calibration_pairs_08": "kappa_calibration_pairs_08",
        "observed_bills_clean": "observed_bills_clean",
    }
    interfaces = execution.get("C_interfaces", {})
    for contract_key, pin_label in interface_keys.items():
        pin = pins[pin_label]
        record = interfaces.get(contract_key, {})
        _assert_equal(f"C_interfaces.{contract_key}.path", record.get("path"), pin.path)
        _assert_equal(f"C_interfaces.{contract_key}.sha256", record.get("sha256"), pin.sha256)

    kappa = execution.get("C_kappa", {})
    _assert_equal("C_kappa.value", kappa.get("value"), EXPECTED_KAPPA)
    _assert_equal("C_kappa.source", kappa.get("source"), pins["economic_interface_14a"].path)
    _assert_equal("C_kappa.source_sha256", kappa.get("source_sha256"), pins["economic_interface_14a"].sha256)

    solver = execution.get("D_solver_policy", {})
    _assert_equal("D_solver_policy.mode", solver.get("mode"), "binary")
    _assert_equal("D_solver_policy.mip_gap", solver.get("mip_gap"), 1e-6)
    _assert_equal("D_solver_policy.time_limit_sec", solver.get("time_limit_sec"), None)
    _assert_equal("D_solver_policy.numeric_focus", solver.get("numeric_focus"), 1)
    _assert_equal("D_solver_policy.node_limit", solver.get("node_limit"), "MUST_NOT_BE_SET")
    _assert_equal("D_solver_policy.layer_a_requirements", solver.get("layer_a_requirements"), None)
    _assert_equal(
        "F_authority_policy.initial_authority_on_completion",
        execution.get("F_authority_policy", {}).get("initial_authority_on_completion"),
        CANDIDATE_AUTHORITY,
    )


def validate_output_root(root: Path, output_root: Path | None = None) -> Path:
    expected = _repo_path(root, CORRECTED_OUTPUT_ROOT_RELATIVE_PATH).resolve()
    selected = (output_root or expected).resolve()
    historical = _repo_path(root, HISTORICAL_OUTPUT_RELATIVE_PATH).resolve()
    if selected == historical or historical in selected.parents:
        raise ProvenanceError(
            f"Historical output namespace is immutable and rejected: {selected}"
        )
    if selected != expected:
        raise ProvenanceError(
            f"Corrected production output root is fixed at {expected}; requested={selected}"
        )
    if not _within(root, selected):
        raise ProvenanceError(f"Corrected output root escapes the repository: {selected}")
    return selected


def validate_run_directory(output_root: Path, run_id: str) -> Path:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ProvenanceError(f"Invalid corrected-EOB run ID: {run_id!r}")
    run_directory = output_root / run_id
    if run_directory.parent.resolve() != output_root.resolve():
        raise ProvenanceError(f"Run directory escapes corrected output root: {run_directory}")
    if run_directory.exists():
        state = "non-empty" if run_directory.is_dir() and any(run_directory.iterdir()) else "existing"
        raise ProvenanceError(f"Refusing to overwrite {state} run directory: {run_directory}")
    return run_directory


def validate_authority(
    root: Path,
    *,
    output_root: Path | None = None,
    hash_reader: Callable[[Path], str] = sha256_file,
    row_counter: Callable[[Path], int] = _parquet_row_count,
    git_probe: Callable[[Path], dict[str, Any]] = _git_repository_state,
) -> dict[str, Any]:
    """Validate every Gate-6 pin without importing or calling the model."""

    root = root.resolve()
    execution_path = _repo_path(root, EXECUTION_CONTRACT_RELATIVE_PATH)
    acceptance_path = _repo_path(root, ACCEPTANCE_CONTRACT_RELATIVE_PATH)
    for label, path, expected in (
        ("Gate-6 execution contract", execution_path, EXECUTION_CONTRACT_SHA256),
        ("Gate-6 acceptance contract", acceptance_path, ACCEPTANCE_CONTRACT_SHA256),
    ):
        if not path.is_file():
            raise ProvenanceError(f"Missing {label}: {path}")
        actual = hash_reader(path)
        if actual != expected:
            raise ProvenanceError(f"{label} SHA-256 mismatch: expected={expected}, actual={actual}")

    execution = _read_json(execution_path)
    acceptance = _read_json(acceptance_path)
    _validate_contract_alignment(execution)

    core_path = _repo_path(root, CORE_RELATIVE_PATH)
    if not core_path.is_file():
        raise ProvenanceError(f"Missing accepted core: {core_path}")
    source_version = _core_version_from_source(core_path)
    if source_version != EXPECTED_CORE_VERSION:
        raise ProvenanceError(
            f"CORE_VERSION mismatch: expected={EXPECTED_CORE_VERSION!r}, actual={source_version!r}"
        )
    core_hash = hash_reader(core_path)
    if core_hash != EXPECTED_CORE_SHA256:
        raise ProvenanceError(
            f"Core SHA-256 mismatch: expected={EXPECTED_CORE_SHA256}, actual={core_hash}"
        )

    pin_records: dict[str, dict[str, Any]] = {}
    for pin in DEPENDENCY_PINS:
        path = _repo_path(root, pin.path)
        if not path.is_file():
            raise ProvenanceError(f"Missing pinned dependency {pin.label}: {path}")
        actual = hash_reader(path)
        if actual != pin.sha256:
            raise ProvenanceError(
                f"Dependency SHA-256 mismatch for {pin.label}: expected={pin.sha256}, actual={actual}"
            )
        pin_records[pin.label] = {
            "path": pin.path,
            "expected_sha256": pin.sha256,
            "actual_sha256": actual,
            "match": True,
        }

    annual_path = _repo_path(root, _pin_map()["canonical_annual_input"].path)
    row_count = row_counter(annual_path)
    if row_count != EXPECTED_ANNUAL_ROWS:
        raise ProvenanceError(
            f"Canonical annual input row-count mismatch: expected={EXPECTED_ANNUAL_ROWS}, actual={row_count}"
        )

    economic_path = _repo_path(root, _pin_map()["economic_interface_14a"].path)
    economic = _read_json(economic_path)
    actual_kappa = economic.get("billing_demand_proxy", {}).get("kappa")
    if actual_kappa != EXPECTED_KAPPA:
        raise ProvenanceError(
            f"Kappa mismatch: expected={EXPECTED_KAPPA!r}, actual={actual_kappa!r}"
        )

    repository = git_probe(root)
    if repository.get("branch") != EXPECTED_BRANCH:
        raise ProvenanceError(
            f"Production branch mismatch: expected={EXPECTED_BRANCH!r}, actual={repository.get('branch')!r}"
        )
    corrected_root = validate_output_root(root, output_root)

    return {
        "validation_status": "PASS",
        "validation_mode": "NO_MODEL_IMPORT_NO_SOLVE",
        "core": {
            "path": CORE_RELATIVE_PATH.as_posix(),
            "CORE_VERSION": source_version,
            "sha256": core_hash,
        },
        "contracts": {
            "execution": {
                "path": EXECUTION_CONTRACT_RELATIVE_PATH.as_posix(),
                "sha256": EXECUTION_CONTRACT_SHA256,
                "schema_version": execution.get("schema_version"),
            },
            "acceptance": {
                "path": ACCEPTANCE_CONTRACT_RELATIVE_PATH.as_posix(),
                "sha256": ACCEPTANCE_CONTRACT_SHA256,
                "schema_version": acceptance.get("schema_version"),
            },
        },
        "dependencies": pin_records,
        "canonical_annual_rows": row_count,
        "kappa": {"value": actual_kappa, "source": _pin_map()["economic_interface_14a"].path},
        "repository": repository,
        "output_policy": {
            "corrected_output_root": corrected_root.relative_to(root).as_posix(),
            "historical_output_root_rejected": HISTORICAL_OUTPUT_RELATIVE_PATH.as_posix(),
            "overwrite_existing_run_directory": False,
        },
        "production_solver_policy": PRODUCTION_SOLVER_POLICY,
        "future_result_authority": CANDIDATE_AUTHORITY,
    }


def intended_contract(authority: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "script_version": SCRIPT_VERSION,
        "mode": "VALIDATE_ONLY_NO_MODEL_NO_SOLVE",
        "authority_validation": authority,
        "future_flow": [
            "provenance_validation",
            "unique_additive_output_allocation",
            "existing_accepted_solve_eob_with_layer_a_requirements_none",
            "lossless_audit_serialization",
            "candidate_manifest_pending_independent_audit",
        ],
        "execution_authorized_by_this_mode": False,
        "real_solver_model_creations": 0,
        "real_optimization_calls": 0,
    }


def make_run_id(now_utc: dt.datetime, authority: Mapping[str, Any]) -> str:
    if now_utc.tzinfo is None:
        raise ValueError("Run timestamp must be timezone-aware.")
    canonical = json.dumps(
        {
            "core": authority["core"],
            "contracts": authority["contracts"],
            "dependencies": authority["dependencies"],
            "driver_version": SCRIPT_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    fingerprint = hashlib.sha256(canonical).hexdigest()[:10]
    timestamp = now_utc.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{timestamp}_{fingerprint}"


def allocate_run_directory(output_root: Path, run_id: str) -> Path:
    run_directory = validate_run_directory(output_root, run_id)
    output_root.mkdir(parents=True, exist_ok=True)
    run_directory.mkdir(exist_ok=False)
    return run_directory


def _load_runtime() -> RuntimeBindings:
    """Import production dependencies only after execute mode is selected."""

    _bootstrap_repository_import_path(project_root())
    from src import annual_design_model_v7_2 as core
    import gurobipy as gp

    version = ".".join(str(part) for part in gp.gurobi.version())
    return RuntimeBindings(
        core_version=core.CORE_VERSION,
        solve_settings_type=core.SolveSettings,
        load_inputs=core.load_annual_design_inputs,
        solve_eob=core.solve_eob,
        solver_name="Gurobi",
        solver_version=version,
    )


def _output_registry(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()
    return tuple(
        sorted(
            candidate.relative_to(path).as_posix()
            for candidate in path.rglob("*")
        )
    )


def validate_runtime_import(
    root: Path,
    authority: Mapping[str, Any],
    *,
    runtime_loader: Callable[[], RuntimeBindings] = _load_runtime,
) -> dict[str, Any]:
    """Import the real runtime while blocking every model/optimization entry."""

    import gurobipy as gp
    from unittest.mock import patch

    output_root = _repo_path(root, CORRECTED_OUTPUT_ROOT_RELATIVE_PATH)
    before = _output_registry(output_root)
    counters = {
        "model_construction_attempts": 0,
        "optimization_attempts": 0,
        "solve_eob_calls": 0,
    }

    def block_model(*_: Any, **__: Any) -> None:
        counters["model_construction_attempts"] += 1
        raise ProvenanceError("Runtime-import check forbids annual model construction.")

    def block_optimization(*_: Any, **__: Any) -> None:
        counters["optimization_attempts"] += 1
        raise ProvenanceError("Runtime-import check forbids optimization.")

    with ExitStack() as stack:
        stack.enter_context(patch.object(gp.Model, "__init__", block_model))
        for name in ("optimize", "optimizeAsync", "optimizeBatch", "tune"):
            if hasattr(gp.Model, name):
                stack.enter_context(patch.object(gp.Model, name, block_optimization))
        runtime = runtime_loader()

    if runtime.core_version != EXPECTED_CORE_VERSION:
        raise ProvenanceError(
            "Imported CORE_VERSION mismatch during runtime check: "
            f"expected={EXPECTED_CORE_VERSION!r}, actual={runtime.core_version!r}"
        )
    bindings = {
        "SolveSettings": callable(runtime.solve_settings_type),
        "load_inputs": callable(runtime.load_inputs),
        "solve_eob": callable(runtime.solve_eob),
    }
    if not all(bindings.values()):
        raise ProvenanceError(f"Required runtime binding is not callable: {bindings}")
    after = _output_registry(output_root)
    if after != before:
        raise ProvenanceError(
            "Runtime-import check changed the corrected production output registry."
        )
    if counters["model_construction_attempts"] or counters["optimization_attempts"]:
        raise ProvenanceError(f"Runtime-import guard recorded a forbidden attempt: {counters}")

    return {
        "runtime_import_status": "PASS",
        "mode": "RUNTIME_IMPORT_CHECK_NO_MODEL_NO_SOLVE",
        "authority_validation_status": authority.get("validation_status"),
        "core": {
            "module": "src.annual_design_model_v7_2",
            "CORE_VERSION": runtime.core_version,
            "sha256": EXPECTED_CORE_SHA256,
        },
        "runtime_bindings": bindings,
        "solver": {"name": runtime.solver_name, "version": runtime.solver_version},
        "execution_guard": counters,
        "production_output_registry": {
            "before": list(before),
            "after": list(after),
            "unchanged": True,
            "run_directories_allocated": 0,
        },
    }


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    return str(value)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(_json_safe(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _stripped_result(result: Mapping[str, Any]) -> dict[str, Any]:
    omitted = {"dispatch", "billing_exact", "transition_settlement_detail"}
    return {key: value for key, value in result.items() if key not in omitted}


def _write_summary_csv(path: Path, result: Mapping[str, Any]) -> None:
    row: dict[str, Any] = {
        "result_authority": CANDIDATE_AUTHORITY,
        "formulation": "binary",
        "solver_status": result.get("status"),
        "status_code": result.get("status_code"),
        "has_solution": result.get("has_solution"),
        "runtime_sec_gurobi": result.get("runtime_sec_gurobi"),
        "runtime_sec_wall": result.get("runtime_sec_wall"),
        "node_count": result.get("node_count"),
        "iteration_count": result.get("iteration_count"),
        "solution_count": result.get("solution_count"),
        "mip_gap": result.get("mip_gap"),
        "objective_ntd2023_per_year": result.get("objective_ntd2023_per_year"),
    }
    sizing = result.get("sizing", {})
    costs = result.get("cost_components_ntd2023_per_year", {})
    row.update(
        {
            "E_N_kwh": sizing.get("E_N_kwh"),
            "P_B_kw_ac": sizing.get("P_B_kw_ac"),
            "CC_regular_kw": sizing.get("CC_regular_kw"),
            "energy_charge_ntd2023_per_year": costs.get("energy"),
            "basic_charge_ntd2023_per_year": costs.get("basic"),
            "pure_season_overcontract_ntd2023_per_year": costs.get("overcontract_pure_season"),
            "transition_overcontract_ntd2023_per_year": costs.get("overcontract_transition_resolved"),
            "degradation_ntd2023_per_year": costs.get("degradation"),
            "annualized_capex_ntd2023_per_year": costs.get("annualized_capex"),
            "fom_ntd2023_per_year": costs.get("fom"),
            "cost_reconciliation_residual_ntd": result.get("cost_reconciliation_residual_ntd"),
        }
    )
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(_json_safe(row))


def _warning_summary(log_path: Path) -> dict[str, Any]:
    if not log_path.is_file():
        return {
            "log_present": False,
            "warnings": [],
            "numerical_warnings": [],
            "work_units": None,
            "parameter_assignments_from_log": [],
        }
    warnings: list[str] = []
    numerical: list[str] = []
    work_units: float | None = None
    parameter_assignments: list[str] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        lowered = line.lower()
        if "warning" in lowered:
            warnings.append(line.strip())
        if any(token in lowered for token in ("numerical", "ill-conditioned", "large matrix coefficient")):
            numerical.append(line.strip())
        work_match = re.search(r"\bwork units\s*:\s*([0-9.eE+\-]+)", line, re.IGNORECASE)
        if work_match:
            work_units = float(work_match.group(1))
        if line.lstrip().lower().startswith("set parameter "):
            parameter_assignments.append(line.strip())
    return {
        "log_present": True,
        "warnings": warnings,
        "numerical_warnings": numerical,
        "work_units": work_units,
        "parameter_assignments_from_log": parameter_assignments,
    }


def _last_optimize_telemetry(events: list[dict[str, Any]]) -> dict[str, Any]:
    for event in reversed(events):
        if event.get("event") == "gurobi_optimize_finished":
            model = event.get("model_optimize")
            return dict(model) if isinstance(model, Mapping) else {}
    return {}


def _artifact_hashes(run_directory: Path, *, exclude: set[str] | None = None) -> dict[str, Any]:
    excluded = exclude or set()
    records: dict[str, Any] = {}
    for path in sorted(run_directory.iterdir(), key=lambda item: item.name.lower()):
        if path.is_file() and path.name not in excluded:
            records[path.name] = {
                "path": path.name,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    return records


def _validate_loaded_inputs(root: Path, inputs: Any) -> None:
    if float(inputs.kappa) != EXPECTED_KAPPA:
        raise ProvenanceError(
            f"Loaded-input kappa mismatch: expected={EXPECTED_KAPPA}, actual={inputs.kappa}"
        )
    expected_paths = {
        "economic_interface_14a": _pin_map()["economic_interface_14a"].path,
        "normalized_tariff_14a": _pin_map()["normalized_tariff_14a"].path,
        "settlement_interface_14b": _pin_map()["settlement_interface_14b"].path,
        "settlement_matrix_14b": _pin_map()["settlement_matrix_14b"].path,
    }
    for label, relative in expected_paths.items():
        actual = Path(inputs.source_paths[label]).resolve()
        expected = _repo_path(root, relative).resolve()
        if actual != expected:
            raise ProvenanceError(
                f"Loaded-input source substitution for {label}: expected={expected}, actual={actual}"
            )
    annual_actual = Path(inputs.source_paths["annual_input"]).resolve()
    allowed = {
        _repo_path(root, _pin_map()["canonical_annual_input"].path).resolve(),
        _repo_path(root, _pin_map()["companion_annual_input_csv"].path).resolve(),
    }
    if annual_actual not in allowed:
        raise ProvenanceError(
            f"Loaded annual input is outside the two corrected pinned artifacts: {annual_actual}"
        )


def execute_production(
    root: Path,
    authority: Mapping[str, Any],
    *,
    runtime_loader: Callable[[], RuntimeBindings] = _load_runtime,
    now_utc: dt.datetime | None = None,
) -> Path:
    """Execute exactly one future solve after a caller has validated authority."""

    if authority.get("validation_status") != "PASS":
        raise ProvenanceError("Production execution requires a passing authority record.")
    root = root.resolve()
    output_root = validate_output_root(root)
    timestamp_utc = now_utc or dt.datetime.now(dt.timezone.utc)
    run_id = make_run_id(timestamp_utc, authority)
    run_directory = allocate_run_directory(output_root, run_id)

    runtime = runtime_loader()
    if runtime.core_version != EXPECTED_CORE_VERSION:
        raise ProvenanceError(
            f"Imported CORE_VERSION mismatch: expected={EXPECTED_CORE_VERSION!r}, actual={runtime.core_version!r}"
        )

    pins = _pin_map()
    inputs = runtime.load_inputs(
        root,
        annual_parquet=_repo_path(root, pins["canonical_annual_input"].path),
        annual_csv=_repo_path(root, pins["companion_annual_input_csv"].path),
        economic_interface_path=_repo_path(root, pins["economic_interface_14a"].path),
        normalized_tariff_path=_repo_path(root, pins["normalized_tariff_14a"].path),
        settlement_interface_path=_repo_path(root, pins["settlement_interface_14b"].path),
        settlement_matrix_path=_repo_path(root, pins["settlement_matrix_14b"].path),
    )
    _validate_loaded_inputs(root, inputs)

    telemetry: list[dict[str, Any]] = []
    log_path = run_directory / "gurobi_corrected_eob.log"
    settings = runtime.solve_settings_type(
        mode="binary",
        mip_gap=1e-6,
        time_limit_sec=None,
        output_flag=1,
        numeric_focus=1,
        log_file=str(log_path),
        telemetry_callback=telemetry.append,
    )

    # Exactly one call, no retry, and no Layer A resilience requirements.
    result = runtime.solve_eob(inputs, settings, layer_a_requirements=None)

    result_path = run_directory / "corrected_eob_result.json"
    summary_path = run_directory / "corrected_eob_summary.csv"
    dispatch_csv = run_directory / "corrected_eob_dispatch.csv"
    dispatch_parquet = run_directory / "corrected_eob_dispatch.parquet"
    billing_csv = run_directory / "corrected_eob_billing_exact.csv"
    transition_csv = run_directory / "corrected_eob_transition_settlement_detail.csv"
    verification_path = run_directory / "corrected_eob_postsolve_verification_inputs.json"
    telemetry_path = run_directory / "corrected_eob_solver_telemetry.json"
    manifest_path = run_directory / "run_manifest.json"

    _write_json(result_path, _stripped_result(result))
    _write_summary_csv(summary_path, result)
    _write_json(telemetry_path, {"events": telemetry})

    postsolve_paths: dict[str, str | None] = {
        "dispatch_csv": None,
        "dispatch_parquet": None,
        "billing_exact_csv": None,
        "transition_settlement_detail_csv": None,
    }
    if result.get("has_solution"):
        result["dispatch"].to_csv(dispatch_csv, index=False, encoding="utf-8-sig")
        result["dispatch"].to_parquet(dispatch_parquet, index=False)
        result["billing_exact"].to_csv(billing_csv, index=False, encoding="utf-8-sig")
        result["transition_settlement_detail"].to_csv(
            transition_csv, index=False, encoding="utf-8-sig"
        )
        postsolve_paths = {
            "dispatch_csv": dispatch_csv.name,
            "dispatch_parquet": dispatch_parquet.name,
            "billing_exact_csv": billing_csv.name,
            "transition_settlement_detail_csv": transition_csv.name,
        }

    verification = {
        "schema_version": "corrected-eob-postsolve-verification-inputs-1",
        "status": "INPUTS_ONLY_PENDING_INDEPENDENT_GATE7_AUDIT",
        "does_not_accept_result": True,
        "kappa": EXPECTED_KAPPA,
        "artifact_paths": postsolve_paths,
        "supported_checks": {
            "exact_d": "Recompute kappa times applicable hourly grid maximum and compare with solver_demand_aux_kw in billing_exact.",
            "w07": "Recompute raw, running z, delta_z/q, q_2x, q_3x, and charge from billing/transition primitives under the frozen Gate-6 equations.",
            "cost_decomposition": "Reconcile result JSON components with objective and cost_reconciliation_residual_ntd.",
        },
        "checker_status": "EXTERNAL_CHECKER_REQUIRED_BY_GATE7_NOT_IMPLEMENTED_IN_DRIVER",
    }
    _write_json(verification_path, verification)

    optimize = _last_optimize_telemetry(telemetry)
    warnings = _warning_summary(log_path)
    taipei = timestamp_utc.astimezone(ZoneInfo("Asia/Taipei"))
    sizing = result.get("sizing", {})
    costs = result.get("cost_components_ntd2023_per_year", {})
    output_hashes = _artifact_hashes(run_directory, exclude={manifest_path.name})
    manifest = {
        "schema_version": "corrected-eob-candidate-run-manifest-1",
        "run_id": run_id,
        "created_at_utc": timestamp_utc.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "created_at_asia_taipei": taipei.isoformat(),
        "execution_script": DRIVER_RELATIVE_PATH.as_posix(),
        "execution_script_sha256": sha256_file(_repo_path(root, DRIVER_RELATIVE_PATH)),
        "branch": authority["repository"]["branch"],
        "HEAD": authority["repository"]["HEAD"],
        "working_tree_status": authority["repository"]["working_tree_status"],
        "CORE_VERSION": EXPECTED_CORE_VERSION,
        "core_sha256": EXPECTED_CORE_SHA256,
        "canonical_input_path": pins["canonical_annual_input"].path,
        "canonical_input_sha256": pins["canonical_annual_input"].sha256,
        "dependency_identities": authority["dependencies"],
        "kappa": {"value": EXPECTED_KAPPA, "identity": authority["kappa"]},
        "solver": {"name": runtime.solver_name, "version": runtime.solver_version},
        "production_solver_settings": PRODUCTION_SOLVER_POLICY,
        "same_model_parameter_readback": {
            "status": "NOT_EXPOSED_BY_ACCEPTED_SOLVE_EOB_CALLABLE",
            "must_be_completed_by": "Gate-7 independent post-solve audit",
            "values_are_not_invented": True,
        },
        "result_authority": CANDIDATE_AUTHORITY,
        "solver_completion": {
            "status": result.get("status", optimize.get("status")),
            "status_code": result.get("status_code", optimize.get("status_code")),
            "runtime_sec_gurobi": result.get("runtime_sec_gurobi", optimize.get("gurobi_runtime_sec")),
            "runtime_sec_wall": result.get("runtime_sec_wall"),
            "node_count": result.get("node_count", optimize.get("node_count")),
            "iteration_count": result.get("iteration_count", optimize.get("iteration_count")),
            "solution_count": result.get("solution_count", optimize.get("solution_count")),
            "incumbent_objective": optimize.get("incumbent_objective", result.get("objective_ntd2023_per_year")),
            "best_bound": optimize.get("best_bound"),
            "mip_gap": result.get("mip_gap", optimize.get("mip_gap")),
            "work_units": warnings.get("work_units"),
            "work_units_status": (
                "PARSED_FROM_GUROBI_LOG"
                if warnings.get("work_units") is not None
                else "NOT_PRESENT_IN_GUROBI_LOG"
            ),
            **warnings,
        },
        "design_outputs": {
            "E_N_kwh": sizing.get("E_N_kwh"),
            "P_B_kw_ac": sizing.get("P_B_kw_ac"),
            "CC_regular_kw": sizing.get("CC_regular_kw"),
        },
        "objective_ntd2023_per_year": result.get("objective_ntd2023_per_year"),
        "cost_decomposition_ntd2023_per_year": costs,
        "cost_reconciliation_residual_ntd": result.get("cost_reconciliation_residual_ntd"),
        "postsolve_verification_artifact_paths": {
            **postsolve_paths,
            "verification_inputs_json": verification_path.name,
            "solver_telemetry_json": telemetry_path.name,
            "result_json": result_path.name,
            "summary_csv": summary_path.name,
        },
        "output_artifacts": output_hashes,
        "acceptance_status": "NOT_AUDITED_DRIVER_DOES_NOT_ACCEPT_ITS_OWN_RESULT",
    }
    _write_json(manifest_path, manifest)
    return manifest_path


def run(
    *,
    root: Path,
    validate_only: bool,
    runtime_import_check: bool = False,
    validator: Callable[[Path], dict[str, Any]] = validate_authority,
    executor: Callable[[Path, Mapping[str, Any]], Path] = execute_production,
    runtime_loader: Callable[[], RuntimeBindings] = _load_runtime,
) -> int:
    authority = validator(root)
    if validate_only:
        print(json.dumps(_json_safe(intended_contract(authority)), indent=2, ensure_ascii=False))
        return 0
    if runtime_import_check:
        report = validate_runtime_import(
            root,
            authority,
            runtime_loader=runtime_loader,
        )
        print(json.dumps(_json_safe(report), indent=2, ensure_ascii=False))
        return 0
    manifest_path = executor(root, authority)
    print(f"Corrected EOB candidate manifest: {manifest_path}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate all Gate-6 pins and output safety without importing or solving the model.",
    )
    mode.add_argument(
        "--runtime-import-check",
        action="store_true",
        help=(
            "Validate all pins, import the accepted runtime, and prove that no model, "
            "solve, optimization, or production run allocation occurs."
        ),
    )
    mode.add_argument(
        "--execute-production",
        action="store_true",
        help="Execute one corrected EOB candidate. Requires a separate execution authorization.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run(
        root=project_root(),
        validate_only=bool(args.validate_only),
        runtime_import_check=bool(args.runtime_import_check),
    )


if __name__ == "__main__":
    raise SystemExit(main())
