#!/usr/bin/env python3
"""Build-gated single-case diagnostic runner for SOC2080 ``a0.80_b08``.

The default invocation performs read-only static validation only.  It imports
no Gurobi package, constructs no model, and performs no optimization.  The
single diagnostic solve is behind ``--execute-diagnostic`` and additionally
requires a clean, synchronized repository in which this runner and its tests
are tracked.  A result from this runner is diagnostic evidence only and can
never complete the SOC2080 production study.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping


ROOT = Path(__file__).resolve().parents[1]
RUNNER_RELATIVE = Path("scripts/17f_run_soc2080_a080_b08_diagnostic.py")
TEST_RELATIVE = Path("tests/test_17f_soc2080_a080_b08_diagnostic_v7_2.py")
ACCEPTED_17E_RELATIVE = Path("scripts/17e_run_soc_window_sensitivity.py")
DIAGNOSTIC_CASE_ID = "a0.80_b08"
EXPECTED_DIAGNOSTIC_OPTIMIZE_CALLS = 1
MAXIMUM_DIAGNOSTIC_OPTIMIZE_CALLS = 1
EXPECTED_COMPARATOR_OPTIMIZE_CALLS = 0
OUTPUT_ROOT_RELATIVE = Path("results/diagnostics/soc2080_a080_b08/runs")
SCRIPT_VERSION = "v7.2-soc2080-a080-b08-diagnostic-candidate-2026-09-22-r1"

HISTORICAL_CLAIM_BOUNDARY = (
    "This is a newly solved a0.80_b08 diagnostic under the corrected frozen "
    "SOC2080 implementation. It does not reconstruct the exact internal "
    "rainflow state of the historical 2026-09-21 a0.80_b08 solve, which "
    "remains UNRESOLVED / UNRECOVERABLE FROM PRESERVED EVIDENCE."
)
TERMINAL_STATES = {
    "PASS": "DIAGNOSTIC_PASS",
    "REVIEW": "DIAGNOSTIC_REVIEW_REQUIRED",
    "FAIL": "DIAGNOSTIC_GATE_FAILED",
}

DEPENDENCY_PINS: tuple[tuple[str, Path, str], ...] = (
    (
        "annual_core",
        Path("src/annual_design_model_v7_2.py"),
        "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
    ),
    (
        "rainflow_validator",
        Path("src/rainflow_validation_v7_2.py"),
        "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2",
    ),
    (
        "soc2080_adapter",
        Path("src/soc_window_sensitivity_adapter_v7_2.py"),
        "11cfc8167683d7204955f7b0b583ed026889b3ca0629902ff08dc92be3bb6304",
    ),
    (
        "representative_helper_16a_r12",
        Path("scripts/16a_preflight_layer_a_representative_binary_cases.py"),
        "5813119e258e83a45a245ec715ade4536bf9dbf880687f6d3f1e978cce8b06a0",
    ),
    (
        "accepted_soc2080_runner_17e_r2",
        ACCEPTED_17E_RELATIVE,
        "2d8cc520a499851b2cfdc85dafa655accace5aee05d74dc31b851af75c5ffe5d",
    ),
    (
        "correction_authority_freeze",
        Path(
            "docs/checkpoints/"
            "soc2080_rainflow_failure_handling_correction_authority_freeze_"
            "v7_2_2026-09-22.json"
        ),
        "f8f74f4281187d67115c2e66abb942ccafebe237ae68d7ea6ad7af65d4724116",
    ),
    (
        "soc2080_reference_eob_reuse_only",
        Path(
            "results/sensitivity/soc_20_80/runs/"
            "20260921T153546259891Z_2e03707743/cases/EOB/artifacts/result.json"
        ),
        "adff87a99061b4869817969ce3f9530ef0dddf71a902652963fc3b5153b33cdb",
    ),
)


class DiagnosticAuthorityError(RuntimeError):
    """Fail-closed static, repository, scientific, or execution error."""


class DiagnosticTerminalOutcome(DiagnosticAuthorityError):
    """A solved case was serialized but is not a diagnostic PASS."""

    def __init__(self, state: str, terminal_state: str, manifest_path: Path) -> None:
        super().__init__(f"{DIAGNOSTIC_CASE_ID} ended {terminal_state} ({state}).")
        self.state = state
        self.terminal_state = terminal_state
        self.manifest_path = manifest_path


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


def load_accepted_17e(root: Path) -> Any:
    path = root / ACCEPTED_17E_RELATIVE
    expected = dict(
        (relative.as_posix(), digest) for _, relative, digest in DEPENDENCY_PINS
    )[
        ACCEPTED_17E_RELATIVE.as_posix()
    ]
    actual = sha256_file(path) if path.is_file() else None
    if actual != expected:
        raise DiagnosticAuthorityError(
            f"Accepted 17e hash mismatch: expected={expected}, actual={actual}"
        )
    module_name = f"_iris_accepted_soc2080_17e_{uuid.uuid4().hex}"
    try:
        return _load_module(path, module_name)
    except Exception as exc:
        sys.modules.pop(module_name, None)
        raise DiagnosticAuthorityError(f"Accepted 17e could not be loaded: {exc}") from exc


def _load_module(path: Path, name: str) -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DiagnosticAuthorityError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def validate_dependency_pins(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for label, relative, expected in DEPENDENCY_PINS:
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        if actual != expected:
            raise DiagnosticAuthorityError(
                f"Dependency pin mismatch for {label}: expected={expected}, actual={actual}"
            )
        records[label] = {
            "path": relative.as_posix(),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "status": "PASS",
        }
    return records


def accepted_diagnostic_case(authority: Any) -> Any:
    matches = tuple(
        case for case in authority.ALLOWED_CASES if case.case_id == DIAGNOSTIC_CASE_ID
    )
    if len(matches) != 1:
        raise DiagnosticAuthorityError("Accepted 17e does not define exactly one a0.80_b08.")
    case = matches[0]
    if case.alpha != 0.80 or case.beta_h != 8:
        raise DiagnosticAuthorityError("Accepted 17e a0.80_b08 definition changed.")
    return case


def diagnostic_output_root(root: Path) -> Path:
    output = (root / OUTPUT_ROOT_RELATIVE).resolve()
    diagnostic_parent = (root / "results/diagnostics/soc2080_a080_b08").resolve()
    protected = (
        (root / "results/sensitivity/soc_20_80").resolve(),
        (
            root
            / "results/sensitivity/soc_20_80/runs/"
            "20260921T153546259891Z_2e03707743"
        ).resolve(),
        (
            root
            / "results/sensitivity/soc_20_80/runs/"
            "20260921T154716421273Z_cdc64658b8"
        ).resolve(),
    )
    if diagnostic_parent not in output.parents and output != diagnostic_parent:
        raise DiagnosticAuthorityError("Diagnostic output escaped its dedicated namespace.")
    if any(output == item or item in output.parents or output in item.parents for item in protected):
        raise DiagnosticAuthorityError("Diagnostic output overlaps protected SOC2080 output.")
    return output


def read_reference_eob(root: Path, authority: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    relative = next(
        relative
        for label, relative, _ in DEPENDENCY_PINS
        if label == "soc2080_reference_eob_reuse_only"
    )
    record = authority.read_json(root / relative)
    result = record.get("result")
    if (
        record.get("case_id") != "EOB"
        or not isinstance(result, Mapping)
        or result.get("status") != "OPTIMAL"
        or result.get("mode") != "binary"
        or result.get("has_solution") is not True
    ):
        raise DiagnosticAuthorityError("Pinned SOC2080 EOB reference is not usable.")
    metadata = {
        "role": "SOC2080_REFERENCE_EOB_REUSE_ONLY",
        "path": relative.as_posix(),
        "sha256": sha256_file(root / relative),
        "run_id": "20260921T153546259891Z_2e03707743",
        "new_optimize_calls": 0,
        "not_a_new_comparator_solve": True,
    }
    return dict(result), metadata


def verify_one_factor_contract_from_pinned_inputs(
    root: Path, authority: Any, accepted_pins: Mapping[str, Any]
) -> dict[str, Any]:
    """Verify the accepted interface without decoding or constructing annual data."""

    interface = authority.read_json(
        root / "data/reference/production_economic_interface_v7_2.json"
    )
    package = interface["package_selector"]["mainline"]
    if (
        package.get("package_id") != authority.EXPECTED_MAINLINE_PACKAGE_ID
        or authority.canonical_object_sha256(package)
        != authority.EXPECTED_MAINLINE_PACKAGE_SHA256
    ):
        raise DiagnosticAuthorityError("Accepted mainline 10 MW package changed.")
    canonical_input = accepted_pins.get("canonical_annual_input", {})
    if canonical_input.get("actual_sha256") != authority.EXPECTED_CANONICAL_INPUT_SHA256:
        raise DiagnosticAuthorityError("Canonical annual input pin changed.")
    return {
        "status": "PASS_PINNED_ACCEPTED_17E_CONTRACT",
        "only_changed_factor": authority.ONE_FACTOR_CONTRACT["only_changed_factor"],
        "soc_window": authority.SOC2080_SPEC.metadata(),
        "one_factor_contract": dict(authority.ONE_FACTOR_CONTRACT),
        "mainline_package": package,
        "mainline_package_object_sha256": authority.EXPECTED_MAINLINE_PACKAGE_SHA256,
        "canonical_input_sha256": authority.EXPECTED_CANONICAL_INPUT_SHA256,
        "canonical_input_verified_by_sha256_pin": True,
        "annual_data_decoded_during_build_validation": False,
        "alternative_winter_input_used": False,
        "cost_scale_sensitivity_package_used": False,
        "variable_reserve_floor_used": False,
    }


def validate_static_authority(root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pins = validate_dependency_pins(root)
    authority = load_accepted_17e(root)
    try:
        case = accepted_diagnostic_case(authority)
        accepted_pins = authority.verify_file_pins(root)
        one_factor = verify_one_factor_contract_from_pinned_inputs(
            root, authority, accepted_pins
        )
        reference_eob, reference_metadata = read_reference_eob(root, authority)
        if reference_eob.get("objective_ntd2023_per_year") is None:
            raise DiagnosticAuthorityError("Pinned SOC2080 EOB objective is absent.")
        if authority.SOC2080_SPEC.metadata() != one_factor["soc_window"]:
            raise DiagnosticAuthorityError("Accepted SOC2080 metadata is inconsistent.")
        active_widths = authority.derive_active_segment_widths(
            authority.TECHNICAL_BREAKPOINTS,
            authority.SOC2080_SPEC.usable_fraction,
        )
        if active_widths != (0.30, 0.30, 0.0):
            raise DiagnosticAuthorityError("Accepted SOC2080 active widths changed.")
        output_root = diagnostic_output_root(root)
        return {
            "status": "DIAGNOSTIC_BUILD_STATIC_AUTHORITY_PASS_NO_MODEL_NO_SOLVE",
            "authority_state": "CANDIDATE_PENDING_INDEPENDENT_READ_ONLY_AUDIT",
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "candidate_test_sha256": sha256_file(root / TEST_RELATIVE),
            "accepted_17e_version": authority.SCRIPT_VERSION,
            "accepted_17e_sha256": pins["accepted_soc2080_runner_17e_r2"][
                "actual_sha256"
            ],
            "case": {
                "case_id": case.case_id,
                "alpha": case.alpha,
                "beta_h": case.beta_h,
                "definition_source": ACCEPTED_17E_RELATIVE.as_posix(),
                "only_executable_case": True,
            },
            "soc_window": authority.SOC2080_SPEC.metadata(),
            "active_segment_widths": list(active_widths),
            "solver_contract": dict(authority.SOLVER_CONTRACT),
            "rainflow_validator": pins["rainflow_validator"],
            "one_factor_authority": one_factor,
            "dependency_pins": pins,
            "accepted_17e_transitive_pins": accepted_pins,
            "reference_eob": reference_metadata,
            "solve_count_contract": {
                "expected_diagnostic_optimize_calls": EXPECTED_DIAGNOSTIC_OPTIMIZE_CALLS,
                "maximum_diagnostic_optimize_calls": MAXIMUM_DIAGNOSTIC_OPTIMIZE_CALLS,
                "comparator_optimize_calls": EXPECTED_COMPARATOR_OPTIMIZE_CALLS,
                "actual_optimize_calls_this_validation": 0,
            },
            "output_namespace": output_root.relative_to(root).as_posix() + "/<run_id>",
            "eligible_for_production_completion": False,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
            "default_mode": "READ_ONLY_STATIC_NO_MODEL_NO_SOLVE_NO_WRITE",
            "diagnostic_execution_authorized_by_build_pass": False,
            "future_execution_freeze_support": {
                "runner_path": RUNNER_RELATIVE.as_posix(),
                "test_path": TEST_RELATIVE.as_posix(),
                "runner_self_hash_is_not_pinned": True,
                "execution_requires_both_files_tracked_in_clean_synchronized_HEAD": True,
            },
            "repository_snapshot_non_authorizing": authority.repository_snapshot(root),
        }
    finally:
        sys.modules.pop(authority.__name__, None)


def execution_repository_authority(root: Path, authority: Any) -> dict[str, Any]:
    repository = authority.production_repository_authority(root)
    for relative in (RUNNER_RELATIVE, TEST_RELATIVE):
        tracked = authority.git_text(
            root, "ls-files", "--error-unmatch", relative.as_posix()
        )
        if tracked.replace("\\", "/") != relative.as_posix():
            raise DiagnosticAuthorityError(f"Execution file is not tracked: {relative}")
    return repository


class SingleDiagnosticOptimizeGuard(AbstractContextManager["SingleDiagnosticOptimizeGuard"]):
    """Reuse accepted 17e guarding with an immutable one-call ceiling."""

    def __init__(self, accepted_17e: Any, gp_module: Any) -> None:
        self._delegate = accepted_17e.OptimizeCallGuard(
            gp_module, MAXIMUM_DIAGNOSTIC_OPTIMIZE_CALLS
        )

    @property
    def count(self) -> int:
        return int(self._delegate.count)

    def __enter__(self) -> "SingleDiagnosticOptimizeGuard":
        self._delegate.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._delegate.__exit__(exc_type, exc_value, traceback)
        return None

    def assert_one_new_call(self, before: int) -> None:
        self._delegate.assert_one_new_call(before, DIAGNOSTIC_CASE_ID)

    def assert_exact_total(self) -> None:
        if self.count != EXPECTED_DIAGNOSTIC_OPTIMIZE_CALLS:
            raise DiagnosticAuthorityError(
                f"Diagnostic optimize count={self.count}; expected exactly one."
            )


def classify_and_serialize_diagnostic(
    gates: Mapping[str, str],
    classifier: Callable[[Mapping[str, str]], str],
    serializer: Callable[[str, str], None],
    terminal_manifest_path: Path,
) -> str:
    """Serialize PASS/REVIEW/FAIL evidence before enforcing terminal authority."""

    state = classifier(gates)
    terminal_state = TERMINAL_STATES.get(state, TERMINAL_STATES["FAIL"])
    if state not in TERMINAL_STATES:
        state = "FAIL"
    serializer(terminal_state, state)
    if state != "PASS":
        raise DiagnosticTerminalOutcome(state, terminal_state, terminal_manifest_path)
    return terminal_state


def normalize_diagnostic_artifacts(
    authority: Any,
    artifacts_dir: Path,
    *,
    live: Mapping[str, Any],
    terminal_state: str,
    validation_state: str,
    billing: Mapping[str, Any],
    result: Mapping[str, Any],
    reference_eob: Mapping[str, Any],
) -> None:
    """Relabel newly written 17e-compatible artifacts as diagnostic-only."""

    result_path = artifacts_dir / "result.json"
    record = authority.read_json(result_path)
    accepted_serializer = {
        "runner_version": record.get("runner_version"),
        "runner_sha256": record.get("runner_sha256"),
        "schema_reused": True,
    }
    record.update(
        {
            "status": terminal_state,
            "authority_state": terminal_state,
            "post_solve_authority_state": validation_state,
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": live["runner_sha256"],
            "diagnostic_runner_version": SCRIPT_VERSION,
            "diagnostic_runner_sha256": live["runner_sha256"],
            "accepted_17e_serializer": accepted_serializer,
            "solve_count_contract": {
                "expected_diagnostic_optimize_calls": 1,
                "maximum_diagnostic_optimize_calls": 1,
                "actual_diagnostic_optimize_calls": 1,
                "comparator_optimize_calls": 0,
            },
            "soc2080_reference_eob_reuse_only": dict(reference_eob),
            "eligible_for_production_completion": False,
            "not_production_acceptance": True,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
        }
    )
    record.pop("accepted_comparator", None)
    authority.write_json(result_path, record, exclusive=False)

    gates_path = artifacts_dir / "post_solve_gates.json"
    gate_record = authority.read_json(gates_path)
    gate_record.update(
        {
            "status": terminal_state,
            "authority_state": terminal_state,
            "validation_state": validation_state,
            "eligible_for_run_completion": False,
            "eligible_for_production_completion": False,
            "not_production_acceptance": True,
        }
    )
    authority.write_json(gates_path, gate_record, exclusive=False)
    authority.write_json(
        artifacts_dir / "billing_audit.json",
        {"status": "RECORDED", "audit": dict(billing)},
    )
    authority.write_json(
        artifacts_dir / "transition_settlement_audit.json",
        {
            "status": "RECORDED",
            "audit": dict(result.get("transition_settlement", {})),
        },
    )
    authority.write_json(
        artifacts_dir / "diagnostic_authority.json",
        {
            "status": terminal_state,
            "validation_state": validation_state,
            "case_id": DIAGNOSTIC_CASE_ID,
            "eligible_for_production_completion": False,
            "not_production_acceptance": True,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
            "complete_post_solve_gates_path": "post_solve_gates.json",
            "complete_rainflow_audit_path": "rainflow_audit.json",
            "complete_dispatch_path": "dispatch.csv",
            "complete_soc_trajectory_column": "dispatch.csv:soc_fraction",
            "billing_audit_path": "billing_audit.json",
            "transition_settlement_audit_path": "transition_settlement_audit.json",
            "outage_audit_path": "outage_replay_audit.json",
        },
    )


def allocate_diagnostic_run_directory(root: Path, run_id: str) -> Path:
    run_root = diagnostic_output_root(root)
    run_dir = run_root / run_id
    if run_dir.exists():
        raise DiagnosticAuthorityError(f"Diagnostic run directory exists: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def execute_diagnostic(root: Path, static_authority: Mapping[str, Any]) -> Path:
    """Future one-solve path; this build-only pass must never call it."""

    authority = load_accepted_17e(root)
    helper_name = f"_iris_diagnostic_helper16a_{uuid.uuid4().hex}"
    run_id = authority.new_run_id()
    run_dir: Path | None = None
    guard: SingleDiagnosticOptimizeGuard | None = None
    try:
        repository = execution_repository_authority(root, authority)
        live = validate_static_authority(root)
        if live["runner_sha256"] != static_authority.get("runner_sha256"):
            raise DiagnosticAuthorityError("Runner changed between validation and execution.")
        case = accepted_diagnostic_case(authority)
        reference_eob_result, reference_eob = read_reference_eob(root, authority)

        import gurobipy as gp

        isolated = authority.load_isolated_r10_soc_core(root)
        if isolated.active_segment_widths != (0.30, 0.30, 0.0):
            raise DiagnosticAuthorityError("Isolated core active domain is not SOC2080.")
        core = isolated.module
        helper = authority.load_module(
            root / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            helper_name,
        )
        inputs = core.load_annual_design_inputs(
            root,
            annual_parquet=root / "data/processed/annual_input_v7_1.parquet",
            annual_csv=root / "data/processed/annual_input_v7_1.csv",
            economic_interface_path=root
            / "data/reference/production_economic_interface_v7_2.json",
            normalized_tariff_path=root
            / "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
            settlement_interface_path=root
            / "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
            settlement_matrix_path=root
            / "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
        )
        if (
            inputs.mainline_package.get("package_id")
            != authority.EXPECTED_MAINLINE_PACKAGE_ID
            or authority.canonical_object_sha256(inputs.mainline_package)
            != authority.EXPECTED_MAINLINE_PACKAGE_SHA256
        ):
            raise DiagnosticAuthorityError("Solver-facing package is not pinned mainline 10 MW.")
        surface, _starts, analytical_audit = helper.analytical_surface(
            inputs.annual,
            eta_d=float(authority.ONE_FACTOR_CONTRACT["eta_d"]),
            soc_min=authority.SOC2080_SPEC.soc_min,
            soc_max=authority.SOC2080_SPEC.soc_max,
        )
        if analytical_audit.get("status") != "PASS":
            raise DiagnosticAuthorityError("SOC2080 analytical requirements failed.")
        rows = surface.loc[surface["case_id"].eq(DIAGNOSTIC_CASE_ID)]
        if len(rows) != 1:
            raise DiagnosticAuthorityError("Exactly one a0.80_b08 requirement was not found.")
        requirement = rows.iloc[0].to_dict()
        expected_minimum = authority.required_nameplate_energy_kwh(
            float(requirement["R_kwh_battery"])
        )
        if abs(float(requirement["analytical_E_N_min_kwh"]) - expected_minimum) > authority.TOL:
            raise DiagnosticAuthorityError("a0.80_b08 R/0.60 analytical bound mismatch.")
        layer_requirement = core.LayerAResilienceRequirements(
            alpha=float(case.alpha),
            beta_h=int(case.beta_h),
            reserve_kwh_battery=float(requirement["R_kwh_battery"]),
            power_requirement_kw_ac=float(requirement["P_out_kw_ac"]),
        )

        run_dir = allocate_diagnostic_run_directory(root, run_id)
        case_dir = run_dir / "case" / DIAGNOSTIC_CASE_ID
        case_dir.mkdir(parents=True, exist_ok=False)
        authority.write_json(
            run_dir / "diagnostic_run_manifest.json",
            {
                "schema_version": "v7.2-soc2080-a080-b08-diagnostic-run-1",
                "status": "DIAGNOSTIC_EXECUTION_STARTED_NOT_PRODUCTION",
                "run_id": run_id,
                "started_utc": utc_text(),
                "case_id": DIAGNOSTIC_CASE_ID,
                "case_definition_source": ACCEPTED_17E_RELATIVE.as_posix(),
                "runner_version": SCRIPT_VERSION,
                "runner_sha256": live["runner_sha256"],
                "accepted_17e_version": authority.SCRIPT_VERSION,
                "accepted_17e_sha256": live["accepted_17e_sha256"],
                "soc_window": authority.SOC2080_SPEC.metadata(),
                "solver_contract": authority.SOLVER_CONTRACT,
                "expected_diagnostic_optimize_calls": 1,
                "maximum_diagnostic_optimize_calls": 1,
                "comparator_optimize_calls": 0,
                "eligible_for_production_completion": False,
                "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
                "repository_authority": repository,
            },
        )
        settings = core.SolveSettings(
            mode="binary",
            mip_gap=authority.MIP_GAP,
            time_limit_sec=authority.TIME_LIMIT_SEC,
            output_flag=authority.OUTPUT_FLAG,
            numeric_focus=authority.NUMERIC_FOCUS,
            log_file=str(case_dir / "gurobi.log"),
            telemetry_callback=authority.telemetry_writer(
                case_dir / "solver_telemetry.jsonl", DIAGNOSTIC_CASE_ID
            ),
        )
        started = time.perf_counter()
        with SingleDiagnosticOptimizeGuard(authority, gp) as guard:
            before = guard.count
            result = core.solve_eob(inputs, settings, layer_requirement)
            guard.assert_one_new_call(before)
            guard.assert_exact_total()
        result["soc_window_configuration"] = isolated.metadata()
        result["lineage_id"] = authority.LINEAGE_ID
        result["parent_lineage"] = authority.PARENT_LINEAGE_ID
        rainflow = authority.validate_soc_rainflow(root, inputs, result)
        billing = helper.billing_structure_audit(result["billing_exact"], inputs.annual)
        gates = authority.base_post_solve_gates(result, billing, rainflow)
        representative = helper.representative_gate(
            result,
            requirement,
            reference_eob_result,
            soc_min=authority.SOC2080_SPEC.soc_min,
            soc_max=authority.SOC2080_SPEC.soc_max,
            rainflow_validation=rainflow,
            billing_audit=billing,
        )
        gates.update({f"representative__{key}": value for key, value in representative.items()})
        outage_audit, outage_starts = authority.outage_replay_audit(
            inputs.annual, requirement, result["sizing"]
        )
        gates["all_start_outage_replay"] = outage_audit["status"]
        terminal_manifest = run_dir / "diagnostic_terminal_manifest.json"

        def persist_diagnostics(terminal_state: str, validation_state: str) -> None:
            artifacts_dir = case_dir / "artifacts"
            authority.write_case_artifacts(
                artifacts_dir,
                case,
                result,
                inputs.mainline_package,
                gates,
                rainflow,
                reference_eob,
                requirement,
                outage_audit,
                outage_starts,
                terminal_state,
                terminal_state,
            )
            normalize_diagnostic_artifacts(
                authority,
                artifacts_dir,
                live=live,
                terminal_state=terminal_state,
                validation_state=validation_state,
                billing=billing,
                result=result,
                reference_eob=reference_eob,
            )
            registry = authority.build_artifact_registry(run_dir)
            authority.write_json(
                terminal_manifest,
                {
                    "schema_version": "v7.2-soc2080-a080-b08-diagnostic-terminal-1",
                    "status": terminal_state,
                    "validation_state": validation_state,
                    "run_id": run_id,
                    "completed_utc": utc_text(),
                    "case_id": DIAGNOSTIC_CASE_ID,
                    "elapsed_wall_seconds": time.perf_counter() - started,
                    "actual_diagnostic_optimize_calls": guard.count,
                    "comparator_optimize_calls": 0,
                    "artifact_registry": registry,
                    "manifest_self_hash_omitted": True,
                    "eligible_for_production_completion": False,
                    "not_production_acceptance": True,
                    "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
                },
            )

        classify_and_serialize_diagnostic(
            gates,
            authority.classify_post_solve_authority,
            persist_diagnostics,
            terminal_manifest,
        )
        return terminal_manifest
    except DiagnosticTerminalOutcome:
        raise
    except Exception as exc:
        if run_dir is not None and run_dir.exists():
            failure_path = run_dir / "diagnostic_failure_manifest.json"
            terminal_path = run_dir / "diagnostic_terminal_manifest.json"
            if not failure_path.exists() and not terminal_path.exists():
                authority.write_json(
                    failure_path,
                    {
                        "schema_version": "v7.2-soc2080-a080-b08-diagnostic-failure-1",
                        "status": "DIAGNOSTIC_EXECUTION_ERROR",
                        "failed_utc": utc_text(),
                        "run_id": run_id,
                        "case_id": DIAGNOSTIC_CASE_ID,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "actual_optimize_calls": 0 if guard is None else guard.count,
                        "eligible_for_production_completion": False,
                        "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
                    },
                )
        raise
    finally:
        sys.modules.pop(helper_name, None)
        sys.modules.pop(authority.__name__, None)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-diagnostic",
        action="store_true",
        help=(
            "Enter the one-case diagnostic solve path. Unauthorized during this "
            "build pass; later use requires independent audit and a clean, tracked, "
            "origin-synchronized execution authority state."
        ),
    )
    return parser.parse_args(argv)


def run(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    validator: Callable[[Path], dict[str, Any]] = validate_static_authority,
    executor: Callable[[Path, Mapping[str, Any]], Path] = execute_diagnostic,
) -> int:
    args = parse_args(argv)
    root = (root or project_root()).resolve()
    authority = validator(root)
    if not args.execute_diagnostic:
        print(json.dumps(authority, indent=2, allow_nan=False))
        return 0
    try:
        terminal_manifest = executor(root, authority)
    except DiagnosticTerminalOutcome as outcome:
        print(outcome.manifest_path)
        return 2 if outcome.state == "REVIEW" else 3
    print(terminal_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
