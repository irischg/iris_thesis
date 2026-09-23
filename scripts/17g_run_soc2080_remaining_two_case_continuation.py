#!/usr/bin/env python3
"""Build-gated SOC2080 continuation for exactly a1.00_b04 and a1.00_b12.

The default invocation performs read-only static validation.  It imports no
Gurobi package, constructs no model, writes no research artifact, and performs
no optimization.  The two-case continuation path is behind
``--execute-continuation`` and additionally requires a clean, synchronized
repository in which this runner and its tests are tracked.  Future execution
captures evidence only; it can never complete Step 11C or accept production
results.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import time
import uuid
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
RUNNER_RELATIVE = Path(
    "scripts/17g_run_soc2080_remaining_two_case_continuation.py"
)
TEST_RELATIVE = Path(
    "tests/test_17g_soc2080_remaining_two_case_continuation_v7_2.py"
)
ACCEPTED_17E_RELATIVE = Path("scripts/17e_run_soc_window_sensitivity.py")
ACCEPTED_17F_RELATIVE = Path(
    "scripts/17f_run_soc2080_a080_b08_diagnostic.py"
)
PARENT_ADJUDICATION_RELATIVE = Path(
    "docs/checkpoints/"
    "soc2080_a080_b08_rainflow_review_gate_owner_adjudication_"
    "v7_2_2026-09-22.json"
)
FIXED_CASE_IDS = ("a1.00_b04", "a1.00_b12")
EXPECTED_CASE_IDENTITIES = {
    "a1.00_b04": (1.00, 4),
    "a1.00_b12": (1.00, 12),
}
EXPECTED_CONTINUATION_OPTIMIZE_CALLS = 2
MAXIMUM_CONTINUATION_OPTIMIZE_CALLS = 2
MAXIMUM_OPTIMIZE_CALLS_PER_CASE = 1
EXPECTED_COMPARATOR_OPTIMIZE_CALLS = 0
EXPECTED_REFERENCE_EOB_OPTIMIZE_CALLS = 0
OUTPUT_ROOT_RELATIVE = Path("results/continuation/soc2080_remaining_two/runs")
SCRIPT_VERSION = (
    "v7.2-soc2080-remaining-two-continuation-candidate-2026-09-22-r1"
)

HISTORICAL_CLAIM_BOUNDARY = (
    "Earlier evidence may later be assembled case-by-case under common frozen "
    "scientific authority. This continuation does not rewrite old runs, copy "
    "new results into old namespaces, retroactively repair historical "
    "a0.80_b08, or treat the 2026-09-22 diagnostic as historical production "
    "completion. Historical 2026-09-21 a0.80_b08 internal rainflow state "
    "remains UNRESOLVED / UNRECOVERABLE FROM PRESERVED EVIDENCE."
)

CASE_EVIDENCE_STATUS = {
    "PASS": "CONTINUATION_EVIDENCE_CAPTURED_RAW_PASS",
    "REVIEW": "CONTINUATION_EVIDENCE_CAPTURED_RAW_REVIEW",
    "FAIL": "CONTINUATION_EVIDENCE_CAPTURED_RAW_FAIL",
}

PRODUCTION_BOUNDARY = {
    "eligible_for_production_completion": False,
    "step_11c_completion": False,
    "step_12_authorized": False,
    "final81_authorized": False,
    "execution_equals_result_acceptance": False,
    "acceptance_gate": "LATER_COMMON_STEP_11C_RESULT_ACCEPTANCE_CLOSURE",
}

DEPENDENCY_PINS: tuple[tuple[str, Path, str], ...] = (
    (
        "framework",
        Path("docs/research_framework_v7_2_2026-08-24.md"),
        "bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5",
    ),
    (
        "registry",
        Path("docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md"),
        "8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e",
    ),
    (
        "provenance_protocol",
        Path(
            "docs/protocols/"
            "Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md"
        ),
        "c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696",
    ),
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
        "accepted_a080_b08_diagnostic_17f_r1",
        ACCEPTED_17F_RELATIVE,
        "a8ec2250ed4a4bffcd79e2e57c93df29b1762c07baa9b109a1e0e2b3f02e30b0",
    ),
    (
        "rainflow_correction_authority_freeze",
        Path(
            "docs/checkpoints/"
            "soc2080_rainflow_failure_handling_correction_authority_freeze_"
            "v7_2_2026-09-22.json"
        ),
        "f8f74f4281187d67115c2e66abb942ccafebe237ae68d7ea6ad7af65d4724116",
    ),
    (
        "diagnostic_preexecution_authority_freeze",
        Path(
            "docs/checkpoints/"
            "soc2080_a080_b08_single_case_diagnostic_preexecution_"
            "authority_freeze_v7_2_2026-09-22.json"
        ),
        "146ba010ca9fbc7cfd76c36f93d6cebea6b9398e1e03c2923f0ac839c54351e2",
    ),
    (
        "rainflow_review_gate_owner_adjudication",
        PARENT_ADJUDICATION_RELATIVE,
        "d26198c3afa147bac2cb0d3f0ec75defbf1f0e6922fbfe13c35d4e319032c253",
    ),
)


class ContinuationAuthorityError(RuntimeError):
    """Fail-closed static, repository, scientific, or execution error."""


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


def _load_module(path: Path, name: str) -> Any:
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContinuationAuthorityError(f"Cannot load module: {path}")
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
            raise ContinuationAuthorityError(
                f"Dependency pin mismatch for {label}: "
                f"expected={expected}, actual={actual}"
            )
        records[label] = {
            "path": relative.as_posix(),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "status": "PASS",
        }
    return records


def load_accepted_modules(root: Path) -> tuple[Any, Any]:
    expected = {relative: digest for _, relative, digest in DEPENDENCY_PINS}
    modules: list[Any] = []
    try:
        for label, relative in (
            ("17e", ACCEPTED_17E_RELATIVE),
            ("17f", ACCEPTED_17F_RELATIVE),
        ):
            path = root / relative
            actual = sha256_file(path) if path.is_file() else None
            if actual != expected[relative]:
                raise ContinuationAuthorityError(
                    f"Accepted {label} hash mismatch: "
                    f"expected={expected[relative]}, actual={actual}"
                )
            name = f"_iris_accepted_soc2080_{label}_{uuid.uuid4().hex}"
            modules.append(_load_module(path, name))
        return modules[0], modules[1]
    except Exception as exc:
        for module in modules:
            sys.modules.pop(module.__name__, None)
        if isinstance(exc, ContinuationAuthorityError):
            raise
        raise ContinuationAuthorityError(
            f"Accepted SOC2080 authority could not be loaded: {exc}"
        ) from exc


def accepted_continuation_cases(authority: Any) -> tuple[Any, Any]:
    selected: list[Any] = []
    for case_id in FIXED_CASE_IDS:
        matches = tuple(
            case for case in authority.ALLOWED_CASES if case.case_id == case_id
        )
        if len(matches) != 1:
            raise ContinuationAuthorityError(
                f"Accepted 17e does not define exactly one {case_id}."
            )
        case = matches[0]
        expected_alpha, expected_beta = EXPECTED_CASE_IDENTITIES[case_id]
        if case.alpha != expected_alpha or case.beta_h != expected_beta:
            raise ContinuationAuthorityError(
                f"Accepted 17e identity changed for {case_id}."
            )
        selected.append(case)
    if tuple(case.case_id for case in selected) != FIXED_CASE_IDS:
        raise ContinuationAuthorityError("Continuation case order changed.")
    return selected[0], selected[1]


def _paths_overlap(left: Path, right: Path) -> bool:
    return (
        left == right
        or left in right.parents
        or right in left.parents
    )


def continuation_output_root(root: Path) -> Path:
    output = (root / OUTPUT_ROOT_RELATIVE).resolve()
    parent = (root / "results/continuation/soc2080_remaining_two").resolve()
    if parent not in output.parents:
        raise ContinuationAuthorityError(
            "Continuation output escaped its dedicated namespace."
        )
    protected_relatives = (
        "results/sensitivity/soc_20_80",
        "results/diagnostics/soc2080_a080_b08",
        "results/sensitivity/soc_20_80/runs/"
        "20260921T153546259891Z_2e03707743",
        "results/sensitivity/soc_20_80/runs/"
        "20260921T154716421273Z_cdc64658b8",
        "results/eob_production",
        "results/eob_production_corrected",
        "results/layer_a",
        "results/layer_a/final_81",
    )
    protected = tuple((root / relative).resolve() for relative in protected_relatives)
    if any(_paths_overlap(output, item) for item in protected):
        raise ContinuationAuthorityError(
            "Continuation output overlaps a protected result namespace."
        )
    return output


def validate_static_authority(root: Path | None = None) -> dict[str, Any]:
    """Validate all live pins without model construction, solve, or output."""

    root = (root or project_root()).resolve()
    pins = validate_dependency_pins(root)
    accepted_17e, accepted_17f = load_accepted_modules(root)
    try:
        cases = accepted_continuation_cases(accepted_17e)
        transitive_pins = accepted_17e.verify_file_pins(root)
        comparators = accepted_17e.verify_comparators(root)
        target_comparators = {
            case_id: comparators[case_id] for case_id in FIXED_CASE_IDS
        }
        one_factor = accepted_17f.verify_one_factor_contract_from_pinned_inputs(
            root, accepted_17e, transitive_pins
        )
        reference_eob_result, reference_eob = accepted_17f.read_reference_eob(
            root, accepted_17e
        )
        if reference_eob_result.get("objective_ntd2023_per_year") is None:
            raise ContinuationAuthorityError(
                "Pinned SOC2080 reference EOB objective is absent."
            )
        active_widths = accepted_17e.derive_active_segment_widths(
            accepted_17e.TECHNICAL_BREAKPOINTS,
            accepted_17e.SOC2080_SPEC.usable_fraction,
        )
        if active_widths != (0.30, 0.30, 0.0):
            raise ContinuationAuthorityError(
                "Accepted SOC2080 active segment widths changed."
            )
        output_root = continuation_output_root(root)
        if not (root / TEST_RELATIVE).is_file():
            raise ContinuationAuthorityError(
                f"Continuation test file is missing: {TEST_RELATIVE}"
            )
        return {
            "status": "CONTINUATION_BUILD_STATIC_AUTHORITY_PASS_NO_MODEL_NO_SOLVE",
            "authority_state": "CANDIDATE_PENDING_INDEPENDENT_READ_ONLY_AUDIT",
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "candidate_test_sha256": sha256_file(root / TEST_RELATIVE),
            "accepted_17e_version": accepted_17e.SCRIPT_VERSION,
            "accepted_17e_sha256": pins[
                "accepted_soc2080_runner_17e_r2"
            ]["actual_sha256"],
            "accepted_17f_version": accepted_17f.SCRIPT_VERSION,
            "accepted_17f_sha256": pins[
                "accepted_a080_b08_diagnostic_17f_r1"
            ]["actual_sha256"],
            "parent_adjudication_authority": pins[
                "rainflow_review_gate_owner_adjudication"
            ],
            "fixed_case_universe": [
                {
                    "case_id": case.case_id,
                    "alpha": case.alpha,
                    "beta_h": case.beta_h,
                    "definition_source": ACCEPTED_17E_RELATIVE.as_posix(),
                }
                for case in cases
            ],
            "attempt_order": list(FIXED_CASE_IDS),
            "soc_window": accepted_17e.SOC2080_SPEC.metadata(),
            "active_segment_widths": list(active_widths),
            "solver_contract": dict(accepted_17e.SOLVER_CONTRACT),
            "one_factor_authority": one_factor,
            "dependency_pins": pins,
            "accepted_17e_transitive_pins": transitive_pins,
            "accepted_17d_comparator_pins": target_comparators,
            "reference_eob": reference_eob,
            "solve_count_contract": {
                "expected_continuation_optimize_calls": (
                    EXPECTED_CONTINUATION_OPTIMIZE_CALLS
                ),
                "maximum_continuation_optimize_calls": (
                    MAXIMUM_CONTINUATION_OPTIMIZE_CALLS
                ),
                "maximum_optimize_calls_per_case": (
                    MAXIMUM_OPTIMIZE_CALLS_PER_CASE
                ),
                "comparator_optimize_calls": EXPECTED_COMPARATOR_OPTIMIZE_CALLS,
                "reference_eob_optimize_calls": (
                    EXPECTED_REFERENCE_EOB_OPTIMIZE_CALLS
                ),
                "actual_optimize_calls_this_validation": 0,
            },
            "output_namespace": (
                output_root.relative_to(root).as_posix() + "/<run_id>"
            ),
            "output_override_supported": False,
            "resume_supported": False,
            "overwrite_supported": False,
            **PRODUCTION_BOUNDARY,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
            "default_mode": "READ_ONLY_STATIC_NO_MODEL_NO_SOLVE_NO_WRITE",
            "continuation_execution_authorized_by_build_pass": False,
            "future_execution_freeze_support": {
                "runner_path": RUNNER_RELATIVE.as_posix(),
                "test_path": TEST_RELATIVE.as_posix(),
                "runner_self_hash_is_not_pinned": True,
                "execution_requires_both_files_tracked": True,
                "execution_requires_clean_synchronized_head": True,
                "execution_requires_exact_untracked_boundary": True,
            },
            "repository_snapshot_non_authorizing": (
                accepted_17e.repository_snapshot(root)
            ),
        }
    finally:
        sys.modules.pop(accepted_17f.__name__, None)
        sys.modules.pop(accepted_17e.__name__, None)


def execution_repository_authority(root: Path, authority: Any) -> dict[str, Any]:
    """Require accepted 17e repository authority plus tracked 17g/test files."""

    try:
        repository = authority.production_repository_authority(root)
    except Exception as exc:
        raise ContinuationAuthorityError(
            f"Continuation repository authority mismatch: {exc}"
        ) from exc
    for relative in (RUNNER_RELATIVE, TEST_RELATIVE):
        tracked = authority.git_text(
            root, "ls-files", "--error-unmatch", relative.as_posix()
        )
        if tracked.replace("\\", "/") != relative.as_posix():
            raise ContinuationAuthorityError(
                f"Continuation execution file is not tracked: {relative}"
            )
    return repository


class RemainingTwoOptimizeGuard(
    AbstractContextManager["RemainingTwoOptimizeGuard"]
):
    """Reuse accepted guarding with fixed order, uniqueness, and a two-call ceiling."""

    def __init__(self, accepted_17e: Any, gp_module: Any) -> None:
        self._delegate = accepted_17e.OptimizeCallGuard(
            gp_module, MAXIMUM_CONTINUATION_OPTIMIZE_CALLS
        )
        self._attempted_case_ids: list[str] = []

    @property
    def count(self) -> int:
        return int(self._delegate.count)

    @property
    def attempted_case_ids(self) -> tuple[str, ...]:
        return tuple(self._attempted_case_ids)

    def __enter__(self) -> "RemainingTwoOptimizeGuard":
        self._delegate.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._delegate.__exit__(exc_type, exc_value, traceback)
        return None

    def solve_once(self, case_id: str, solve: Callable[[], Any]) -> Any:
        if len(self._attempted_case_ids) >= len(FIXED_CASE_IDS):
            raise ContinuationAuthorityError(
                "A third continuation case attempt is forbidden."
            )
        expected = FIXED_CASE_IDS[len(self._attempted_case_ids)]
        if case_id != expected:
            raise ContinuationAuthorityError(
                f"Continuation order mismatch: expected={expected}, actual={case_id}"
            )
        if case_id in self._attempted_case_ids:
            raise ContinuationAuthorityError(
                f"Repeated continuation attempt is forbidden: {case_id}"
            )
        before = self.count
        result = solve()
        self._delegate.assert_one_new_call(before, case_id)
        self._attempted_case_ids.append(case_id)
        return result

    def assert_exact_total(self) -> None:
        if self.count != EXPECTED_CONTINUATION_OPTIMIZE_CALLS:
            raise ContinuationAuthorityError(
                f"Continuation optimize count={self.count}; expected exactly two."
            )
        if self.attempted_case_ids != FIXED_CASE_IDS:
            raise ContinuationAuthorityError(
                "Continuation did not attempt the exact fixed case universe in order."
            )


def serialize_case_validation(
    gates: Mapping[str, str],
    classifier: Callable[[Mapping[str, str]], str],
    serializer: Callable[[str, str], None],
) -> str:
    """Serialize one solved case before retaining its raw tri-state."""

    raw_state = classifier(gates)
    if raw_state not in CASE_EVIDENCE_STATUS:
        raw_state = "FAIL"
    evidence_status = CASE_EVIDENCE_STATUS[raw_state]
    serializer(evidence_status, raw_state)
    return raw_state


def capture_outage_replay_evidence(
    authority: Any,
    annual: Any,
    requirement: Mapping[str, Any],
    sizing: Mapping[str, Any],
) -> tuple[dict[str, Any], Any | None]:
    """Preserve a recognized accepted-helper validation FAIL as raw evidence.

    Accepted 17e returns full PASS evidence but raises its authority exception
    after computing a FAIL.  This adapter does not reproduce any scientific
    formula.  It calls the pinned helper unchanged and converts only that
    helper's exact fail-closed message into a structured FAIL record.  Every
    other exception remains an execution-level failure and stops the run.
    """

    try:
        audit, starts = authority.outage_replay_audit(
            annual, requirement, sizing
        )
    except authority.SocSensitivityAuthorityError as exc:
        prefix = "SOC2080 outage replay failed: "
        message = str(exc)
        if not message.startswith(prefix):
            raise
        try:
            checks = ast.literal_eval(message[len(prefix) :])
        except (SyntaxError, ValueError) as parse_exc:
            raise ContinuationAuthorityError(
                "Accepted outage FAIL evidence could not be parsed."
            ) from parse_exc
        if (
            not isinstance(checks, dict)
            or not checks
            or any(not isinstance(value, bool) for value in checks.values())
            or all(checks.values())
        ):
            raise ContinuationAuthorityError(
                "Accepted outage FAIL evidence is incomplete or inconsistent."
            )
        return (
            {
                "status": "FAIL",
                "checks": checks,
                "accepted_helper": "17e.outage_replay_audit",
                "accepted_helper_exception_type": type(exc).__name__,
                "accepted_helper_exception_message": message,
                "scientific_formula_reimplemented_by_17g": False,
                "per_start_table_available": False,
                "per_start_table_absence_reason": (
                    "PINNED_17E_HELPER_FAILS_CLOSED_BEFORE_RETURN"
                ),
            },
            None,
        )
    if not isinstance(audit, Mapping) or audit.get("status") != "PASS":
        raise ContinuationAuthorityError(
            "Accepted outage helper returned an unknown non-PASS state."
        )
    return dict(audit), starts


def execute_fixed_case_sequence(
    cases: Sequence[Any], attempt: Callable[[Any], Any]
) -> list[Any]:
    """Attempt each fixed case once; any execution exception stops the sequence."""

    case_ids = tuple(case.case_id for case in cases)
    if case_ids != FIXED_CASE_IDS or len(set(case_ids)) != len(case_ids):
        raise ContinuationAuthorityError(
            "Execution sequence is not the exact unique fixed case universe."
        )
    return [attempt(case) for case in cases]


def initial_case_records() -> dict[str, dict[str, Any]]:
    return {
        case_id: {
            "case_id": case_id,
            "alpha": EXPECTED_CASE_IDENTITIES[case_id][0],
            "beta_h": EXPECTED_CASE_IDENTITIES[case_id][1],
            "attempt_status": "NOT_ATTEMPTED",
            "optimize_attempts": 0,
            "solver_status": None,
            "raw_validation_state": None,
            "complete_artifacts_serialized": False,
            "eligible_for_production_completion": False,
        }
        for case_id in FIXED_CASE_IDS
    }


def normalize_continuation_artifacts(
    authority: Any,
    artifacts_dir: Path,
    *,
    case: Any,
    live: Mapping[str, Any],
    evidence_status: str,
    raw_state: str,
    billing: Mapping[str, Any],
    result: Mapping[str, Any],
    reference_eob: Mapping[str, Any],
) -> None:
    """Relabel accepted 17e artifacts as continuation evidence only."""

    result_path = artifacts_dir / "result.json"
    record = authority.read_json(result_path)
    accepted_serializer = {
        "runner_version": record.get("runner_version"),
        "runner_sha256": record.get("runner_sha256"),
        "schema_reused": True,
    }
    record.update(
        {
            "status": evidence_status,
            "authority_state": evidence_status,
            "raw_validation_state": raw_state,
            "runner_version": SCRIPT_VERSION,
            "runner_sha256": live["runner_sha256"],
            "continuation_runner_version": SCRIPT_VERSION,
            "continuation_runner_sha256": live["runner_sha256"],
            "accepted_17e_serializer": accepted_serializer,
            "fixed_case_universe": list(FIXED_CASE_IDS),
            "solve_count_contract": {
                "expected_continuation_optimize_calls": 2,
                "maximum_continuation_optimize_calls": 2,
                "maximum_optimize_calls_per_case": 1,
                "actual_optimize_calls_for_this_case": 1,
                "comparator_optimize_calls": 0,
                "reference_eob_optimize_calls": 0,
            },
            "soc2080_reference_eob_reuse_only": dict(reference_eob),
            "parent_adjudication_authority": dict(
                live["parent_adjudication_authority"]
            ),
            **PRODUCTION_BOUNDARY,
            "case_result_acceptance_deferred": True,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
        }
    )
    authority.write_json(result_path, record, exclusive=False)

    gates_path = artifacts_dir / "post_solve_gates.json"
    gate_record = authority.read_json(gates_path)
    gate_record.update(
        {
            "status": evidence_status,
            "authority_state": evidence_status,
            "raw_validation_state": raw_state,
            "evidence_serialized": True,
            "eligible_for_run_completion": False,
            "eligible_for_production_completion": False,
            "case_result_acceptance_deferred": True,
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
        artifacts_dir / "continuation_authority.json",
        {
            "status": evidence_status,
            "raw_validation_state": raw_state,
            "case_id": case.case_id,
            "alpha": case.alpha,
            "beta_h": case.beta_h,
            "fixed_case_universe": list(FIXED_CASE_IDS),
            **PRODUCTION_BOUNDARY,
            "case_result_acceptance_deferred": True,
            "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
            "complete_post_solve_gates_path": "post_solve_gates.json",
            "complete_rainflow_audit_path": "rainflow_audit.json",
            "complete_dispatch_path": "dispatch.csv",
            "complete_soc_trajectory_column": "dispatch.csv:soc_fraction",
            "billing_audit_path": "billing_audit.json",
            "transition_settlement_audit_path": (
                "transition_settlement_audit.json"
            ),
            "outage_audit_path": "outage_replay_audit.json",
        },
    )


def allocate_continuation_run_directory(root: Path, run_id: str) -> Path:
    run_root = continuation_output_root(root)
    run_dir = run_root / run_id
    create_exclusive_run_directory(run_dir)
    return run_dir


def create_exclusive_run_directory(run_dir: Path) -> None:
    """Create one new run directory; resume, reuse, and overwrite are forbidden."""

    if run_dir.exists():
        raise ContinuationAuthorityError(
            f"Continuation run directory exists: {run_dir}"
        )
    run_dir.mkdir(parents=True, exist_ok=False)


def _run_manifest_payload(
    *,
    run_id: str,
    live: Mapping[str, Any],
    repository: Mapping[str, Any],
    accepted_17e: Any,
    case_records: Mapping[str, Mapping[str, Any]],
    actual_optimize_calls: int,
    status: str,
    execution_level_failure: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "v7.2-soc2080-remaining-two-continuation-run-1",
        "status": status,
        "run_id": run_id,
        "updated_utc": utc_text(),
        "runner_version": SCRIPT_VERSION,
        "runner_sha256": live["runner_sha256"],
        "accepted_17e_version": accepted_17e.SCRIPT_VERSION,
        "accepted_17e_sha256": live["accepted_17e_sha256"],
        "parent_adjudication_authority": dict(
            live["parent_adjudication_authority"]
        ),
        "fixed_case_universe": list(FIXED_CASE_IDS),
        "attempt_order": list(FIXED_CASE_IDS),
        "expected_optimize_calls": 2,
        "maximum_optimize_calls": 2,
        "maximum_optimize_calls_per_case": 1,
        "actual_optimize_calls": actual_optimize_calls,
        "comparator_optimize_calls": 0,
        "reference_eob_optimize_calls": 0,
        "per_case": dict(case_records),
        "execution_level_failure": execution_level_failure,
        "dependency_authority_bundle": {
            "direct_pins": live["dependency_pins"],
            "accepted_17e_transitive_pins": (
                live["accepted_17e_transitive_pins"]
            ),
            "accepted_17d_comparator_pins": (
                live["accepted_17d_comparator_pins"]
            ),
            "reference_eob": live["reference_eob"],
        },
        "repository_authority": dict(repository),
        **PRODUCTION_BOUNDARY,
        "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
    }


def execute_continuation(
    root: Path, static_authority: Mapping[str, Any]
) -> Path:
    """Future two-solve evidence path; this build-only pass must never reach it."""

    accepted_17e, accepted_17f = load_accepted_modules(root)
    helper_name = f"_iris_continuation_helper16a_{uuid.uuid4().hex}"
    run_id = accepted_17e.new_run_id()
    run_dir: Path | None = None
    guard: RemainingTwoOptimizeGuard | None = None
    case_records = initial_case_records()
    current_case_id: str | None = None
    try:
        repository = execution_repository_authority(root, accepted_17e)
        live = validate_static_authority(root)
        if live["runner_sha256"] != static_authority.get("runner_sha256"):
            raise ContinuationAuthorityError(
                "Runner changed between static validation and execution."
            )
        if live["candidate_test_sha256"] != static_authority.get(
            "candidate_test_sha256"
        ):
            raise ContinuationAuthorityError(
                "Test authority changed between validation and execution."
            )
        cases = accepted_continuation_cases(accepted_17e)
        reference_eob_result, reference_eob = accepted_17f.read_reference_eob(
            root, accepted_17e
        )

        import gurobipy as gp

        isolated = accepted_17e.load_isolated_r10_soc_core(root)
        if isolated.active_segment_widths != (0.30, 0.30, 0.0):
            raise ContinuationAuthorityError(
                "Isolated core active domain is not SOC2080."
            )
        core = isolated.module
        helper = accepted_17e.load_module(
            root / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            helper_name,
        )
        inputs = core.load_annual_design_inputs(
            root,
            annual_parquet=root / "data/processed/annual_input_v7_1.parquet",
            annual_csv=root / "data/processed/annual_input_v7_1.csv",
            economic_interface_path=(
                root / "data/reference/production_economic_interface_v7_2.json"
            ),
            normalized_tariff_path=(
                root
                / "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv"
            ),
            settlement_interface_path=(
                root
                / "data/reference/"
                "taipower_transition_period_settlement_interface_v7_2.json"
            ),
            settlement_matrix_path=(
                root
                / "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv"
            ),
        )
        if (
            inputs.mainline_package.get("package_id")
            != accepted_17e.EXPECTED_MAINLINE_PACKAGE_ID
            or accepted_17e.canonical_object_sha256(inputs.mainline_package)
            != accepted_17e.EXPECTED_MAINLINE_PACKAGE_SHA256
        ):
            raise ContinuationAuthorityError(
                "Solver-facing package is not the pinned mainline 10 MW package."
            )
        surface, _starts, analytical_audit = helper.analytical_surface(
            inputs.annual,
            eta_d=float(accepted_17e.ONE_FACTOR_CONTRACT["eta_d"]),
            soc_min=accepted_17e.SOC2080_SPEC.soc_min,
            soc_max=accepted_17e.SOC2080_SPEC.soc_max,
        )
        if analytical_audit.get("status") != "PASS":
            raise ContinuationAuthorityError(
                "SOC2080 analytical requirements failed."
            )

        requirements: dict[str, dict[str, Any]] = {}
        for case in cases:
            rows = surface.loc[surface["case_id"].eq(case.case_id)]
            if len(rows) != 1:
                raise ContinuationAuthorityError(
                    f"Exactly one analytical requirement was not found: {case.case_id}"
                )
            requirement = rows.iloc[0].to_dict()
            if (
                float(requirement["alpha"]) != float(case.alpha)
                or int(requirement["beta_h"]) != int(case.beta_h)
            ):
                raise ContinuationAuthorityError(
                    f"Analytical case identity mismatch: {case.case_id}"
                )
            expected_minimum = accepted_17e.required_nameplate_energy_kwh(
                float(requirement["R_kwh_battery"])
            )
            if (
                abs(
                    float(requirement["analytical_E_N_min_kwh"])
                    - expected_minimum
                )
                > accepted_17e.TOL
            ):
                raise ContinuationAuthorityError(
                    f"R/0.60 analytical bound mismatch: {case.case_id}"
                )
            requirements[case.case_id] = requirement

        run_dir = allocate_continuation_run_directory(root, run_id)
        manifest_path = run_dir / "continuation_run_manifest.json"

        def write_manifest(status: str, execution_failure: bool) -> None:
            accepted_17e.write_json(
                manifest_path,
                _run_manifest_payload(
                    run_id=run_id,
                    live=live,
                    repository=repository,
                    accepted_17e=accepted_17e,
                    case_records=case_records,
                    actual_optimize_calls=0 if guard is None else guard.count,
                    status=status,
                    execution_level_failure=execution_failure,
                ),
                exclusive=not manifest_path.exists(),
            )

        write_manifest("EVIDENCE_CAPTURE_STARTED_NOT_PRODUCTION_ACCEPTED", False)

        with RemainingTwoOptimizeGuard(accepted_17e, gp) as guard:

            def attempt_case(case: Any) -> dict[str, Any]:
                nonlocal current_case_id
                current_case_id = case.case_id
                requirement = requirements[case.case_id]
                case_records[case.case_id].update(
                    {
                        "attempt_status": "ATTEMPT_STARTED",
                        "optimize_attempts": 0,
                    }
                )
                write_manifest(
                    "EVIDENCE_CAPTURE_IN_PROGRESS_NOT_PRODUCTION_ACCEPTED",
                    False,
                )
                case_dir = run_dir / "cases" / case.case_id
                case_dir.mkdir(parents=True, exist_ok=False)
                layer_requirement = core.LayerAResilienceRequirements(
                    alpha=float(case.alpha),
                    beta_h=int(case.beta_h),
                    reserve_kwh_battery=float(requirement["R_kwh_battery"]),
                    power_requirement_kw_ac=float(requirement["P_out_kw_ac"]),
                )
                settings = core.SolveSettings(
                    mode="binary",
                    mip_gap=accepted_17e.MIP_GAP,
                    time_limit_sec=accepted_17e.TIME_LIMIT_SEC,
                    output_flag=accepted_17e.OUTPUT_FLAG,
                    numeric_focus=accepted_17e.NUMERIC_FOCUS,
                    log_file=str(case_dir / "gurobi.log"),
                    telemetry_callback=accepted_17e.telemetry_writer(
                        case_dir / "solver_telemetry.jsonl", case.case_id
                    ),
                )
                started = time.perf_counter()
                result = guard.solve_once(
                    case.case_id,
                    lambda: core.solve_eob(inputs, settings, layer_requirement),
                )
                case_records[case.case_id]["optimize_attempts"] = 1
                result["soc_window_configuration"] = isolated.metadata()
                result["lineage_id"] = accepted_17e.LINEAGE_ID
                result["parent_lineage"] = accepted_17e.PARENT_LINEAGE_ID
                rainflow = accepted_17e.validate_soc_rainflow(root, inputs, result)
                billing = helper.billing_structure_audit(
                    result["billing_exact"], inputs.annual
                )
                gates = accepted_17e.base_post_solve_gates(
                    result, billing, rainflow
                )
                representative = helper.representative_gate(
                    result,
                    requirement,
                    reference_eob_result,
                    soc_min=accepted_17e.SOC2080_SPEC.soc_min,
                    soc_max=accepted_17e.SOC2080_SPEC.soc_max,
                    rainflow_validation=rainflow,
                    billing_audit=billing,
                )
                gates.update(
                    {
                        f"representative__{key}": value
                        for key, value in representative.items()
                    }
                )
                outage_audit, outage_starts = capture_outage_replay_evidence(
                    accepted_17e,
                    inputs.annual,
                    requirement,
                    result["sizing"],
                )
                gates["all_start_outage_replay"] = outage_audit["status"]

                def persist_case(
                    evidence_status: str, raw_state: str
                ) -> None:
                    artifacts_dir = case_dir / "artifacts"
                    accepted_17e.write_case_artifacts(
                        artifacts_dir,
                        case,
                        result,
                        inputs.mainline_package,
                        gates,
                        rainflow,
                        live["accepted_17d_comparator_pins"][case.case_id],
                        requirement,
                        outage_audit,
                        outage_starts,
                        evidence_status,
                        raw_state,
                    )
                    normalize_continuation_artifacts(
                        accepted_17e,
                        artifacts_dir,
                        case=case,
                        live=live,
                        evidence_status=evidence_status,
                        raw_state=raw_state,
                        billing=billing,
                        result=result,
                        reference_eob=reference_eob,
                    )

                raw_state = serialize_case_validation(
                    gates,
                    accepted_17e.classify_post_solve_authority,
                    persist_case,
                )
                case_records[case.case_id].update(
                    {
                        "attempt_status": "SOLVED_EVIDENCE_SERIALIZED",
                        "solver_status": result.get("status"),
                        "raw_validation_state": raw_state,
                        "complete_artifacts_serialized": True,
                        "artifacts_path": (
                            Path("cases") / case.case_id / "artifacts"
                        ).as_posix(),
                        "elapsed_wall_seconds": time.perf_counter() - started,
                        "eligible_for_production_completion": False,
                    }
                )
                write_manifest(
                    "EVIDENCE_CAPTURE_IN_PROGRESS_NOT_PRODUCTION_ACCEPTED",
                    False,
                )
                current_case_id = None
                return {
                    "case_id": case.case_id,
                    "raw_validation_state": raw_state,
                }

            execute_fixed_case_sequence(cases, attempt_case)
            guard.assert_exact_total()
            actual_optimize_calls = guard.count

        write_manifest(
            "EVIDENCE_CAPTURE_COMPLETE_NOT_PRODUCTION_ACCEPTED", False
        )
        registry = accepted_17e.build_artifact_registry(run_dir)
        completion_path = run_dir / "continuation_evidence_capture_manifest.json"
        accepted_17e.write_json(
            completion_path,
            {
                "schema_version": (
                    "v7.2-soc2080-remaining-two-continuation-evidence-capture-1"
                ),
                "status": "EVIDENCE_CAPTURE_COMPLETE_NOT_PRODUCTION_ACCEPTED",
                "run_id": run_id,
                "completed_utc": utc_text(),
                "fixed_case_universe": list(FIXED_CASE_IDS),
                "attempt_order": list(FIXED_CASE_IDS),
                "expected_optimize_calls": 2,
                "maximum_optimize_calls": 2,
                "actual_optimize_calls": actual_optimize_calls,
                "comparator_optimize_calls": 0,
                "reference_eob_optimize_calls": 0,
                "per_case": case_records,
                "execution_level_failure": False,
                "evidence_capture_complete": True,
                "artifact_registry": registry,
                "manifest_self_hash_omitted": True,
                **PRODUCTION_BOUNDARY,
                "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
            },
        )
        return completion_path
    except Exception as exc:
        if current_case_id is not None:
            completed_other_calls = sum(
                int(record.get("optimize_attempts", 0))
                for case_id, record in case_records.items()
                if case_id != current_case_id
            )
            current_case_calls = (
                0
                if guard is None
                else max(0, min(1, guard.count - completed_other_calls))
            )
            current_record = case_records[current_case_id]
            evidence_was_serialized = bool(
                current_record.get("complete_artifacts_serialized")
            )
            current_record.update(
                {
                    "attempt_status": (
                        "SOLVED_EVIDENCE_SERIALIZED_BEFORE_LATER_EXECUTION_FAILURE"
                        if evidence_was_serialized
                        else "EXECUTION_LEVEL_FAILURE"
                    ),
                    "optimize_attempts": current_case_calls,
                    "complete_artifacts_serialized": evidence_was_serialized,
                    "execution_exception_type": type(exc).__name__,
                    "execution_exception_message": str(exc),
                }
            )
        if run_dir is not None and run_dir.exists():
            manifest_path = run_dir / "continuation_run_manifest.json"
            failure_path = run_dir / "continuation_execution_failure_manifest.json"
            if "live" in locals() and "repository" in locals():
                accepted_17e.write_json(
                    manifest_path,
                    _run_manifest_payload(
                        run_id=run_id,
                        live=live,
                        repository=repository,
                        accepted_17e=accepted_17e,
                        case_records=case_records,
                        actual_optimize_calls=(
                            0 if guard is None else guard.count
                        ),
                        status="EXECUTION_LEVEL_FAILURE_RUN_STOPPED",
                        execution_level_failure=True,
                    ),
                    exclusive=not manifest_path.exists(),
                )
            if not failure_path.exists():
                accepted_17e.write_json(
                    failure_path,
                    {
                        "schema_version": (
                            "v7.2-soc2080-remaining-two-continuation-failure-1"
                        ),
                        "status": "EXECUTION_LEVEL_FAILURE_RUN_STOPPED",
                        "failed_utc": utc_text(),
                        "run_id": run_id,
                        "failed_case_id": current_case_id,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "actual_optimize_calls": (
                            0 if guard is None else guard.count
                        ),
                        "per_case": case_records,
                        "retry_attempted": False,
                        "preserve_previously_serialized_cases": True,
                        **PRODUCTION_BOUNDARY,
                        "historical_claim_boundary": HISTORICAL_CLAIM_BOUNDARY,
                    },
                )
        raise
    finally:
        sys.modules.pop(helper_name, None)
        sys.modules.pop(accepted_17f.__name__, None)
        sys.modules.pop(accepted_17e.__name__, None)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-continuation",
        action="store_true",
        help=(
            "Enter the fixed two-case continuation evidence path. Unauthorized "
            "during this build pass; later use requires independent audit and "
            "a clean, tracked, origin-synchronized execution authority state."
        ),
    )
    return parser.parse_args(argv)


def run(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    validator: Callable[[Path], dict[str, Any]] = validate_static_authority,
    executor: Callable[[Path, Mapping[str, Any]], Path] = execute_continuation,
) -> int:
    args = parse_args(argv)
    root = (root or project_root()).resolve()
    authority = validator(root)
    if not args.execute_continuation:
        print(json.dumps(authority, indent=2, allow_nan=False))
        return 0
    completion = executor(root, authority)
    print(completion)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
