"""Additive v7.3 EOB, Layer-A, and Final81 zero-solve successor contract.

This module composes the accepted Step-2E-1 routing preflight.  It contains no
optimization formulation, model construction, economic evaluation, or output
publication.  The historical v7.2 formulation and audit adapters remain the
methodological implementation authority; this layer replaces only the annual
planning-input route with the accepted v7.3 R3 authority.

``execute_production=True`` is deliberately rejected until a separately
audited Macro Gate 2E-B authorizes production execution.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import subprocess
import sys
import uuid
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.production_input_authority_v7_3 import (
    ACCEPTED_ANNUAL_RELATIVE_PATH,
    ACCEPTED_ANNUAL_SHA256,
    ACCEPTED_ARTIFACT_ROLE,
    AnnualInputIdentity,
    IMPOSSIBLE_CSV_RELATIVE_PATH,
    annual_dataframe_fingerprint,
    impossible_csv_path,
    load_accepted_v7_3_annual_input,
    require_same_annual_identity,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
STACK_VERSION = "v7.3-macro-gate-2e-a-zero-solve-successor-stack-2026-09-24-r1"
AUTHORITY_MODULE = "src.production_input_authority_v7_3"
STEP2E1_PREFLIGHT = Path("scripts/21a_preflight_v7_3_production_routing.py")
STEP2E1_TEST = Path("tests/test_21a_v7_3_production_routing_preflight.py")
CORE_MODULE = "src/annual_design_model_v7_2.py"
CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
)

ALPHAS = tuple(round(0.60 + 0.05 * index, 2) for index in range(9))
BETAS_H = tuple(range(4, 13))
ETA_D = 0.90
EXPECTED_CASES = 81

REPRESENTATIVE_SELECTIONS: Mapping[str, tuple[str, ...]] = {
    "low": ("a0.60_b04",),
    "central": ("a0.80_b08",),
    "high": ("a1.00_b12",),
    "core3": ("a0.60_b04", "a0.80_b08", "a1.00_b12"),
    "historical5": (
        "a0.60_b04",
        "a0.60_b12",
        "a0.80_b08",
        "a1.00_b04",
        "a1.00_b12",
    ),
}

PRODUCTION_CASE_SETS: Mapping[str, tuple[str, ...] | None] = {
    "low": REPRESENTATIVE_SELECTIONS["low"],
    "central": REPRESENTATIVE_SELECTIONS["central"],
    "high": REPRESENTATIVE_SELECTIONS["high"],
    "core-three": REPRESENTATIVE_SELECTIONS["core3"],
    "historical-five": REPRESENTATIVE_SELECTIONS["historical5"],
    "full81": None,
}

SUCCESSOR_RELATIVE_PATHS = (
    Path("src/production_successor_stack_v7_3.py"),
    Path("scripts/21b_preflight_v7_3_eob_successor.py"),
    Path("scripts/21c_preflight_v7_3_layer_a_successor.py"),
    Path("scripts/21d_preflight_v7_3_final81_successor.py"),
    Path("tests/test_21b_21d_v7_3_production_successor_stack.py"),
)

STEP2E1_ACCEPTED_COMMIT = "d52d9584b22da2a41b51c8ce3e99a0335e39da2b"
EXPECTED_BRANCH = "thesis-v7"
EOB_PRODUCTION_ROOT = Path("results/eob_production_v7_3/runs")
LAYER_A_PRODUCTION_ROOT = Path("results/layer_a/final_81_v7_3/runs")
MANDATORY_EOB_AUDITS = (
    "solver",
    "physical",
    "billing",
    "transition",
    "cost",
    "degradation",
    "rainflow",
)
MANDATORY_LAYER_A_AUDITS = (
    "solver",
    "physical",
    "resilience",
    "billing",
    "transition",
    "cost",
    "degradation",
    "rainflow",
)

EOB_SOLVER_SETTINGS = {
    "source": "scripts/15d_run_corrected_eob_v7_2.py::PRODUCTION_SOLVER_POLICY",
    "mode": "binary",
    "MIPGap": 1e-6,
    "OutputFlag": 1,
    "NumericFocus": 1,
    "TimeLimit": "INFINITY_UNSET",
    "NodeLimit": "INFINITY_UNSET",
    "automatic_retry_with_changed_parameters": False,
}

LAYER_A_SOLVER_SETTINGS = {
    "source": "scripts/19a_preflight_final_layer_a_81_cases.py",
    "mode": "binary",
    "MIPGap": 1e-6,
    "OutputFlag": 0,
    "NumericFocus": 1,
    "TimeLimit": "INFINITY_UNSET",
    "MIPFocus": 0,
    "Threads": 0,
}

ADDITIONAL_AUTHORITY_FILES: Mapping[str, tuple[Path, str]] = {
    "provenance_protocol": (
        Path(
            "docs/protocols/"
            "Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md"
        ),
        "c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696",
    ),
    "production_input_authority_v7_3": (
        Path("src/production_input_authority_v7_3.py"),
        "f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1",
    ),
    "step2e1_preflight": (
        STEP2E1_PREFLIGHT,
        "3d99a4200dce93cd00db94727f72489d9be497eb52c74270a1c49b17fc8a7e95",
    ),
    "step2e1_test": (
        STEP2E1_TEST,
        "a039ae6620be859dfc7279e35b0b6bf0630e553f1e130fd27a330f9d337f22a6",
    ),
}

PROTECTED_METHODOLOGY_PATHS = (
    Path("src/annual_design_model_v7_2.py"),
    Path("src/production_input_authority_v7_3.py"),
    Path("scripts/08_calibrate_kappa.py"),
    Path("scripts/09_build_valid_outage_start_sets.py"),
    Path("scripts/15a_benchmark_eob_charge_discharge_formulations.py"),
    Path("scripts/15b_freeze_production_eob_baseline.py"),
    Path("scripts/15c_validate_production_eob_rainflow.py"),
    Path("scripts/15d_run_corrected_eob_v7_2.py"),
    Path("scripts/16a_preflight_layer_a_representative_binary_cases.py"),
    Path("scripts/19a_preflight_final_layer_a_81_cases.py"),
    Path("scripts/19b_run_final_layer_a_81_cases.py"),
    STEP2E1_PREFLIGHT,
    STEP2E1_TEST,
)


class SuccessorPreflightError(RuntimeError):
    """Fail-closed v7.3 successor-stack validation error."""


class ProductionExecutionNotAuthorized(SuccessorPreflightError):
    """Raised before any production path when Macro Gate 2E-B is absent."""


class ProductionAuthorityError(SuccessorPreflightError):
    """Fail-closed production deployment or execution error with stable status."""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def require_native_solve_confirmation(confirm_native_solve: bool) -> None:
    """Second explicit interlock guarding every native-solve-capable path.

    ``--execute-production`` alone is not sufficient: an automated caller (a test
    harness, a script, a scheduler) can supply it without a human ever intending a
    multi-hour native optimization.  This guard must be satisfied in addition to the
    deployment-authority gate, and is enforced both at the production entry points
    and at ``NativeProductionBackend`` construction so that bypassing the CLI does
    not silently remove it.  It is a safety interlock, not a scientific authority.
    """

    if not confirm_native_solve:
        raise ProductionAuthorityError(
            "NATIVE_SOLVE_CONFIRMATION_REQUIRED",
            "Explicit --confirm-native-solve is required in addition to "
            "--execute-production before any native model may be constructed. "
            "No model was constructed and no optimization ran.",
        )


def reject_unauthorized_execution(execute_production: bool) -> None:
    """Enforce the 2E-A/2E-B boundary before any build or solve-capable path."""

    if execute_production:
        raise ProductionExecutionNotAuthorized(
            "Macro Gate 2E-B is not authorized; --execute-production is an explicit "
            "future interface only. No model was constructed and no optimization ran."
        )


def _load_step2e1(root: Path) -> Any:
    path = root / STEP2E1_PREFLIGHT
    spec = importlib.util.spec_from_file_location("macro_gate_2e_a_step2e1", path)
    if spec is None or spec.loader is None:
        raise SuccessorPreflightError(f"Could not load accepted preflight: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SuccessorPreflightError(message)


def _identity_from_mapping(value: Mapping[str, Any], *, context: str) -> AnnualInputIdentity:
    fields = ("path", "sha256", "artifact_role", "row_count", "fingerprint_sha256")
    missing = [field for field in fields if field not in value]
    if missing:
        raise SuccessorPreflightError(
            f"{context} annual identity is incomplete; missing={missing}"
        )
    return AnnualInputIdentity(
        path=str(value["path"]),
        sha256=str(value["sha256"]),
        artifact_role=str(value["artifact_role"]),
        row_count=int(value["row_count"]),
        fingerprint_sha256=str(value["fingerprint_sha256"]),
    )


def _accepted_identity(preflight: Mapping[str, Any]) -> AnnualInputIdentity:
    identity = _identity_from_mapping(
        preflight["accepted_annual_input"], context="accepted Step-2E-1"
    )
    _require(
        identity.path == ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        "Step-2E-1 returned a nonaccepted annual path.",
    )
    _require(identity.sha256 == ACCEPTED_ANNUAL_SHA256, "Accepted R3 SHA drift.")
    _require(
        identity.artifact_role == ACCEPTED_ARTIFACT_ROLE,
        "Accepted R3 artifact_role drift.",
    )
    _require(identity.row_count == 8760, "Accepted R3 row-count drift.")
    return identity


def verify_protected_methodology(root: Path) -> dict[str, dict[str, Any]]:
    """Prove that every reused historical/accepted dependency matches HEAD."""

    root = root.resolve()
    evidence: dict[str, dict[str, Any]] = {}
    for relative in PROTECTED_METHODOLOGY_PATHS:
        path = root / relative
        _require(path.is_file(), f"Protected methodology dependency is missing: {relative}")
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative.as_posix()],
            cwd=root,
            capture_output=True,
            text=True,
        )
        _require(tracked.returncode == 0, f"Protected dependency is not tracked: {relative}")
        clean = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative.as_posix()],
            cwd=root,
            capture_output=True,
            text=True,
        )
        _require(
            clean.returncode == 0,
            f"Protected methodology dependency has working-tree drift: {relative}",
        )
        evidence[relative.as_posix()] = {
            "sha256": sha256_file(path),
            "matches_head": True,
        }
    return evidence


def verify_additional_authorities(root: Path) -> dict[str, dict[str, str]]:
    """Verify accepted protocol and Step-2E-1 control bytes by exact SHA-256."""

    root = root.resolve()
    verified: dict[str, dict[str, str]] = {}
    for label, (relative, expected) in ADDITIONAL_AUTHORITY_FILES.items():
        path = root / relative
        _require(path.is_file(), f"Required accepted authority is missing: {relative}")
        actual = sha256_file(path)
        _require(
            actual == expected,
            f"Accepted authority SHA256 mismatch for {relative}: "
            f"expected={expected}, actual={actual}",
        )
        verified[label] = {"path": relative.as_posix(), "sha256": actual}
    return verified


def run_accepted_routing_preflight(root: Path = ROOT) -> dict[str, Any]:
    """Run the closed Step-2E-1 preflight and require its strict zero counters."""

    module = _load_step2e1(root.resolve())
    payload = module.run_preflight(root.resolve())
    counters = payload.get("execution_counters", {})
    _require(payload.get("status") == "PASS", "Accepted Step-2E-1 preflight failed.")
    for counter in ("model_constructions", "optimization_calls", "economic_evaluations"):
        _require(counters.get(counter) == 0, f"Nonzero Step-2E-1 counter: {counter}")
    _require(not counters.get("forbidden_attempts"), "A forbidden solver API was attempted.")
    _accepted_identity(payload)
    return payload


def build_eob_successor_preflight(
    base: Mapping[str, Any],
    dependency_evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    identity = _accepted_identity(base)
    loader = base["unchanged_core_loader_integration"]
    _require(loader.get("status") == "PASS", "Unchanged core loader integration failed.")
    _require(loader.get("legacy_default_used") is False, "Legacy annual default was used.")
    _require(loader.get("csv_fallback_occurred") is False, "CSV fallback occurred.")
    _require(loader.get("csv_argument_exists") is False, "Impossible CSV sentinel exists.")
    _require(loader.get("core_version") == CORE_VERSION, "Shared core version drift.")

    return {
        "status": "PASS",
        "successor": "V7.3_EOB_ZERO_SOLVE_SUCCESSOR",
        "annual_identity": identity.as_dict(),
        "authority_module": AUTHORITY_MODULE,
        "core_module": CORE_MODULE,
        "core_version": CORE_VERSION,
        "explicit_annual_parquet": ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        "explicit_impossible_csv": IMPOSSIBLE_CSV_RELATIVE_PATH.as_posix(),
        "csv_fallback": False,
        "legacy_annual_default": False,
        "historical_methodology": {
            "lineage": [
                "scripts/15a_benchmark_eob_charge_discharge_formulations.py",
                "scripts/15b_freeze_production_eob_baseline.py",
                "scripts/15c_validate_production_eob_rainflow.py",
                "scripts/15d_run_corrected_eob_v7_2.py",
            ],
            "tariff_billing_economics": "UNCHANGED_SHARED_CORE_AND_ACCEPTED_ADAPTERS",
            "degradation_rainflow": "UNCHANGED_ACCEPTED_EOB_LINEAGE",
            "eob_decision_semantics": "UNCHANGED",
            "kappa_recalibrated": False,
            "dependency_evidence": {
                path: dependency_evidence[path]
                for path in dependency_evidence
                if path.startswith("scripts/15") or path == CORE_MODULE
            },
        },
        "solver_settings_future_contract": dict(EOB_SOLVER_SETTINGS),
        "execution": {
            "default_mode": "PREFLIGHT_ONLY",
            "explicit_future_flag": "--execute-production",
            "production_mode": "IMPLEMENTED_DEPLOYMENT_GATED_NOT_CURRENTLY_AUTHORIZED",
            "future_execution_entrypoint": "run_eob_production",
            "future_native_solve_route": "NativeProductionBackend.solve_eob -> core.solve_eob",
            "model_constructed": False,
            "optimization_executed": False,
            "economic_evaluation_executed": False,
        },
    }


def _case_identity_contexts(identity: AnnualInputIdentity) -> dict[str, dict[str, Any]]:
    return {
        context: identity.as_dict()
        for context in (
            "requirements",
            "model_input",
            "analytical_replay",
            "billing_economics_context",
        )
    }


def build_layer_a_successor_preflight(base: Mapping[str, Any]) -> dict[str, Any]:
    identity = _accepted_identity(base)
    analytical = base["analytical_surface_audit"]
    replay = base["analytical_replay_audit"]
    starts = base["valid_start_identity_audit"]
    _require(analytical.get("status") == "PASS", "Layer-A analytical audit failed.")
    _require(replay.get("status") == "PASS", "Layer-A replay audit failed.")
    _require(starts.get("status") == "PASS", "Valid-start audit failed.")
    _require(analytical.get("case_count") == EXPECTED_CASES, "Layer-A case count drift.")
    _require(analytical.get("eta_d") == ETA_D, "Layer-A eta_d drift.")
    _require(replay.get("surplus_pv_recharge") is False, "Surplus-PV recharge drift.")

    cases: list[dict[str, Any]] = []
    for source in analytical["cases"]:
        case = deepcopy(source)
        case["annual_identities"] = _case_identity_contexts(identity)
        case["authority_module"] = AUTHORITY_MODULE
        case["surplus_pv_recharge"] = False
        cases.append(case)

    valid_counts = {
        int(row["beta_h"]): int(row["valid_start_count"])
        for row in starts["rows"]
    }
    binding_windows_present = all(
        "binding_historical_start" in case
        and "binding_historical_end_exclusive" in case
        and "binding_start_index" in case
        for case in cases
    )
    _require(binding_windows_present, "Layer-A binding-window evidence is incomplete.")
    return {
        "status": "PASS",
        "successor": "V7.3_LAYER_A_ZERO_SOLVE_SUCCESSOR",
        "annual_identity": identity.as_dict(),
        "authority_module": AUTHORITY_MODULE,
        "equation_source": (
            "scripts/16a_preflight_layer_a_representative_binary_cases.py::"
            "analytical_surface"
        ),
        "alpha_grid": list(ALPHAS),
        "beta_grid_h": list(BETAS_H),
        "case_count": len(cases),
        "eta_d": ETA_D,
        "deficit_equation": "max(alpha * baseline_load_kw - pv_available_kw, 0)",
        "p_out_equation": "max_t(deficit_t)",
        "reserve_equation": (
            "max_valid_non_circular_beta_hour_ac_deficit_energy / eta_d"
        ),
        "valid_start_counts": valid_counts,
        "non_circular": all(bool(row["no_circular_wrap"]) for row in starts["rows"]),
        "binding_windows_present": binding_windows_present,
        "monotonicity": {
            "power": analytical.get("power_monotonicity"),
            "reserve_over_beta": analytical.get("reserve_monotonicity_over_beta"),
            "reserve_over_alpha": analytical.get("reserve_monotonicity_over_alpha"),
        },
        "surplus_pv_recharge": False,
        "representative_selections": {
            key: list(value) for key, value in REPRESENTATIVE_SELECTIONS.items()
        },
        "cases": cases,
        "execution": {
            "default_mode": "ANALYTICAL_PREFLIGHT_ONLY",
            "explicit_future_flag": "--execute-production",
            "production_mode": "IMPLEMENTED_DEPLOYMENT_GATED_NOT_CURRENTLY_AUTHORIZED",
            "future_execution_entrypoint": "run_layer_a_production",
            "representative_cases_solved": 0,
        },
    }


def validate_final81_case_plan(
    cases: Sequence[Mapping[str, Any]],
    expected_identity: AnnualInputIdentity,
) -> None:
    """Validate grid, authority route, contexts, and replay semantics fail closed."""

    _require(len(cases) == EXPECTED_CASES, f"Final81 requires exactly {EXPECTED_CASES} cases.")
    case_ids = [str(case.get("case_id")) for case in cases]
    _require(len(set(case_ids)) == EXPECTED_CASES, "Final81 case IDs are duplicated.")
    coordinates = {(float(case["alpha"]), int(case["beta_h"])) for case in cases}
    expected = {(alpha, beta) for alpha in ALPHAS for beta in BETAS_H}
    _require(coordinates == expected, "Final81 alpha/beta grid is incomplete or altered.")
    _require(
        all(case.get("authority_module") == AUTHORITY_MODULE for case in cases),
        "Final81 production-input authority was bypassed.",
    )
    for case in cases:
        _require(
            case.get("surplus_pv_recharge") is False,
            f"Final81 analytical replay changed surplus-PV semantics: {case.get('case_id')}",
        )
        contexts = case.get("annual_identities")
        _require(isinstance(contexts, Mapping), "Final81 annual identity contexts are missing.")
        expected_contexts = {
            "requirements",
            "model_input",
            "analytical_replay",
            "billing_economics_context",
        }
        _require(set(contexts) == expected_contexts, "Final81 identity contexts differ.")
        for context in sorted(expected_contexts):
            received = _identity_from_mapping(
                contexts[context], context=f"{case['case_id']}:{context}"
            )
            try:
                require_same_annual_identity(
                    expected_identity,
                    received,
                    consumer=f"final81:{case['case_id']}:{context}",
                )
            except Exception as exc:
                raise SuccessorPreflightError(str(exc)) from exc


def build_final81_successor_preflight(
    layer_a: Mapping[str, Any],
    dependency_evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    identity = _identity_from_mapping(layer_a["annual_identity"], context="Layer-A")
    cases = deepcopy(layer_a["cases"])
    validate_final81_case_plan(cases, identity)
    settings = dict(LAYER_A_SOLVER_SETTINGS)
    _require(settings["MIPGap"] == 1e-6, "Final81 production MIPGap drift.")
    return {
        "status": "PASS",
        "successor": "V7.3_FINAL81_ZERO_SOLVE_SUCCESSOR",
        "annual_identity": identity.as_dict(),
        "authority_module": AUTHORITY_MODULE,
        "case_count": len(cases),
        "unique_case_count": len({case["case_id"] for case in cases}),
        "cases": cases,
        "representative_selections": deepcopy(layer_a["representative_selections"]),
        "production_case_sets": {
            name: (list(case_ids) if case_ids is not None else "ALL_81")
            for name, case_ids in PRODUCTION_CASE_SETS.items()
        },
        "solver_settings_future_contract": settings,
        "accepted_future_adapters": {
            "sources": [
                "scripts/19b_run_final_layer_a_81_cases.py",
                "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            ],
            "names": [
                "physical_audit",
                "all_start_audit",
                "billing_audit",
                "transition_audit",
                "cost_degradation_audit",
                "validate_representative_rainflow",
                "representative_comparison",
                "surface_audit",
            ],
            "methodology_status": "UNCHANGED_FUTURE_EXECUTION_CONTRACT",
            "dependency_evidence": {
                path: dependency_evidence[path]
                for path in (
                    "scripts/16a_preflight_layer_a_representative_binary_cases.py",
                    "scripts/19a_preflight_final_layer_a_81_cases.py",
                    "scripts/19b_run_final_layer_a_81_cases.py",
                    CORE_MODULE,
                )
            },
        },
        "billing_boundary": {
            "historical_kappa_calibration_reused": True,
            "kappa_recalibrated": False,
            "planning_pv_source": ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        },
        "execution": {
            "default_mode": "BUILD_PLAN_PREFLIGHT_ONLY",
            "explicit_future_flag": "--execute-production",
            "production_mode": "IMPLEMENTED_DEPLOYMENT_GATED_NOT_CURRENTLY_AUTHORIZED",
            "future_execution_entrypoint": "run_layer_a_production",
            "future_native_solve_route": (
                "NativeProductionBackend.solve_layer_a -> core.solve_eob"
            ),
            "future_case_capacity": EXPECTED_CASES,
            "cases_solved": 0,
            "production_artifacts_created": 0,
        },
    }


def validate_stack_same_artifact(
    eob: Mapping[str, Any],
    layer_a: Mapping[str, Any],
    final81: Mapping[str, Any],
) -> None:
    expected = _identity_from_mapping(eob["annual_identity"], context="EOB")
    for consumer, payload in (("layer_a", layer_a), ("final81", final81)):
        received = _identity_from_mapping(payload["annual_identity"], context=consumer)
        try:
            require_same_annual_identity(expected, received, consumer=consumer)
        except Exception as exc:
            raise SuccessorPreflightError(str(exc)) from exc
    validate_final81_case_plan(final81["cases"], expected)


def select_cases(payload: Mapping[str, Any], selection: str) -> list[dict[str, Any]]:
    if selection == "all81":
        return deepcopy(payload["cases"])
    if selection not in REPRESENTATIVE_SELECTIONS:
        raise SuccessorPreflightError(f"Unknown representative selection: {selection}")
    wanted = set(REPRESENTATIVE_SELECTIONS[selection])
    selected = [deepcopy(case) for case in payload["cases"] if case["case_id"] in wanted]
    _require({case["case_id"] for case in selected} == wanted, "Representative plan is incomplete.")
    return selected


def run_successor_stack(
    root: Path = ROOT,
    *,
    execute_production: bool = False,
) -> dict[str, Any]:
    """Build the complete in-memory successor plan under the zero-solve guard."""

    reject_unauthorized_execution(execute_production)
    root = root.resolve()
    additional_authorities = verify_additional_authorities(root)
    dependencies = verify_protected_methodology(root)
    base = run_accepted_routing_preflight(root)
    eob = build_eob_successor_preflight(base, dependencies)
    layer_a = build_layer_a_successor_preflight(base)
    final81 = build_final81_successor_preflight(layer_a, dependencies)
    validate_stack_same_artifact(eob, layer_a, final81)
    counters = deepcopy(base["execution_counters"])
    _require(
        counters["model_constructions"] == 0
        and counters["optimization_calls"] == 0
        and counters["economic_evaluations"] == 0,
        "Macro Gate 2E-A zero-solve counters are not zero.",
    )
    accepted = base["accepted_annual_input"]
    base_authorities = accepted["authority_hashes"]
    authority_integrity = {
        "framework": base_authorities["methodology"],
        "registry": base_authorities["evidence"],
        "lifecycle": base_authorities["lifecycle"],
        **additional_authorities,
        "accepted_r3_parquet": {
            "path": accepted["path"],
            "sha256": accepted["sha256"],
        },
    }
    return {
        "status": "PASS",
        "verdict": "MACRO GATE 2E-A SUCCESSOR STACK PREFLIGHT PASS",
        "stack_version": STACK_VERSION,
        "authority_module": AUTHORITY_MODULE,
        "authority_integrity": authority_integrity,
        "protected_methodology": dependencies,
        "eob": eob,
        "layer_a": layer_a,
        "final81": final81,
        "execution_counters": counters,
        "execution_boundary": {
            "EOB": "NOT EXECUTED",
            "Representative Layer A": "NOT EXECUTED",
            "Final81": "NOT EXECUTED",
            "Layer B": "NOT EXECUTED",
            "Macro Gate 2E-B": "NOT AUTHORIZED",
            "Production optimization": "NOT AUTHORIZED",
        },
    }


@dataclass(frozen=True)
class DeploymentSnapshot:
    """Read-only repository/deployment state used by the production gate."""

    branch: str
    head: str
    origin_head: str
    step2e1_is_ancestor: bool
    successor_bytes_committed: bool
    tracked_unstaged_changes: bool
    staged_changes: bool
    authority_hashes_valid: bool
    authority_error: str | None
    accepted_identity: AnnualInputIdentity | None
    csv_fallback_possible: bool
    authority_untracked_paths: tuple[str, ...]


def _git_completed(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _git_text(root: Path, *args: str) -> str:
    completed = _git_completed(root, *args)
    if completed.returncode != 0:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            f"git {' '.join(args)} failed: {completed.stderr.strip()}",
        )
    return completed.stdout.strip()


def _successor_bytes_committed(root: Path) -> bool:
    for relative in SUCCESSOR_RELATIVE_PATHS:
        tracked = _git_completed(
            root, "ls-files", "--error-unmatch", "--", relative.as_posix()
        )
        if tracked.returncode != 0:
            return False
        clean = _git_completed(root, "diff", "--quiet", "HEAD", "--", relative.as_posix())
        if clean.returncode != 0:
            return False
    return True


def _authority_untracked_paths(root: Path) -> tuple[str, ...]:
    status = _git_completed(
        root,
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status.returncode != 0:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            f"Could not inspect untracked paths: {status.stderr.strip()}",
        )
    protected_prefixes = ("src/", "scripts/", "tests/", "data/", "results/")
    paths: list[str] = []
    for line in status.stdout.splitlines():
        if not line.startswith("?? "):
            continue
        path = line[3:].strip().strip('"').replace("\\", "/")
        if path.startswith(protected_prefixes):
            paths.append(path)
    return tuple(sorted(paths))


def inspect_deployment_snapshot(root: Path = ROOT) -> DeploymentSnapshot:
    """Inspect production authority without importing or constructing a model."""

    root = root.resolve()
    branch = _git_text(root, "branch", "--show-current")
    head = _git_text(root, "rev-parse", "HEAD")
    origin_head = _git_text(root, "rev-parse", "origin/thesis-v7")
    ancestor = _git_completed(
        root, "merge-base", "--is-ancestor", STEP2E1_ACCEPTED_COMMIT, head
    ).returncode == 0
    tracked_unstaged = _git_completed(root, "diff", "--quiet").returncode != 0
    staged = _git_completed(root, "diff", "--cached", "--quiet").returncode != 0
    authority_valid = False
    authority_error: str | None = None
    identity: AnnualInputIdentity | None = None
    csv_fallback_possible = True
    try:
        verify_additional_authorities(root)
        accepted = load_accepted_v7_3_annual_input(root)
        identity = accepted.identity
        csv_fallback_possible = (root / IMPOSSIBLE_CSV_RELATIVE_PATH).exists()
        authority_valid = True
    except Exception as exc:
        authority_error = str(exc)
    return DeploymentSnapshot(
        branch=branch,
        head=head,
        origin_head=origin_head,
        step2e1_is_ancestor=ancestor,
        successor_bytes_committed=_successor_bytes_committed(root),
        tracked_unstaged_changes=tracked_unstaged,
        staged_changes=staged,
        authority_hashes_valid=authority_valid,
        authority_error=authority_error,
        accepted_identity=identity,
        csv_fallback_possible=csv_fallback_possible,
        authority_untracked_paths=_authority_untracked_paths(root),
    )


def validate_deployment_snapshot(
    snapshot: DeploymentSnapshot,
    *,
    execute_production: bool,
    selected_scope: str | None,
) -> dict[str, Any]:
    """Apply the deployment gate in a stable, fail-closed order."""

    if not execute_production:
        raise ProductionAuthorityError(
            "EXECUTION_DISABLED", "Explicit --execute-production is required."
        )
    if selected_scope is None:
        raise ProductionAuthorityError(
            "CASE_SCOPE_REQUIRED", "An explicit fixed production case scope is required."
        )
    if selected_scope != "eob" and selected_scope not in PRODUCTION_CASE_SETS:
        raise ProductionAuthorityError(
            "CASE_SCOPE_REJECTED", f"Uncontrolled production scope: {selected_scope!r}"
        )
    if snapshot.branch != EXPECTED_BRANCH:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            f"Expected branch {EXPECTED_BRANCH}; observed {snapshot.branch}.",
        )
    if not snapshot.step2e1_is_ancestor:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "Accepted Step-2E-1 commit is not an ancestor of HEAD.",
        )
    if not snapshot.successor_bytes_committed:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "Current v7.3 successor bytes are not committed in HEAD.",
        )
    if snapshot.tracked_unstaged_changes:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "Tracked unstaged changes are present.",
        )
    if snapshot.staged_changes:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN", "Staged changes are present."
        )
    if snapshot.head != snapshot.origin_head:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "HEAD does not equal origin/thesis-v7.",
        )
    if not snapshot.authority_hashes_valid or snapshot.accepted_identity is None:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_HASH_FAIL",
            snapshot.authority_error or "Accepted authority identity is unavailable.",
        )
    expected = AnnualInputIdentity(
        path=ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        sha256=ACCEPTED_ANNUAL_SHA256,
        artifact_role=ACCEPTED_ARTIFACT_ROLE,
        row_count=8760,
        fingerprint_sha256=snapshot.accepted_identity.fingerprint_sha256,
    )
    try:
        require_same_annual_identity(
            expected, snapshot.accepted_identity, consumer="production_deployment_gate"
        )
    except Exception as exc:
        raise ProductionAuthorityError("PRODUCTION_INPUT_AUTHORITY_FAIL", str(exc)) from exc
    if snapshot.csv_fallback_possible:
        raise ProductionAuthorityError(
            "PRODUCTION_INPUT_AUTHORITY_FAIL", "CSV fallback sentinel exists."
        )
    if snapshot.authority_untracked_paths:
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "Untracked authority-surface paths are present: "
            f"{list(snapshot.authority_untracked_paths)}",
        )
    return {
        "status": "PRODUCTION_AUTHORITY_FROZEN",
        "branch": snapshot.branch,
        "head": snapshot.head,
        "origin_head": snapshot.origin_head,
        "step2e1_commit": STEP2E1_ACCEPTED_COMMIT,
        "selected_scope": selected_scope,
        "annual_identity": snapshot.accepted_identity.as_dict(),
        "successor_paths": [path.as_posix() for path in SUCCESSOR_RELATIVE_PATHS],
    }


def require_production_authority(
    root: Path,
    *,
    execute_production: bool,
    selected_scope: str | None,
) -> dict[str, Any]:
    return validate_deployment_snapshot(
        inspect_deployment_snapshot(root),
        execute_production=execute_production,
        selected_scope=selected_scope,
    )


def select_production_cases(
    final81: Mapping[str, Any], case_set: str
) -> list[dict[str, Any]]:
    if case_set not in PRODUCTION_CASE_SETS:
        raise ProductionAuthorityError(
            "CASE_SCOPE_REJECTED", f"Unknown fixed case set: {case_set!r}"
        )
    cases = deepcopy(final81["cases"])
    expected_identity = _identity_from_mapping(final81["annual_identity"], context="Final81")
    validate_final81_case_plan(cases, expected_identity)
    wanted = PRODUCTION_CASE_SETS[case_set]
    if wanted is not None:
        wanted_set = set(wanted)
        cases = [case for case in cases if case["case_id"] in wanted_set]
        _require(
            {case["case_id"] for case in cases} == wanted_set,
            f"Fixed case set {case_set} is incomplete.",
        )
    return cases


def build_execution_schedule(
    cases: Sequence[Mapping[str, Any]], expected_identity: AnnualInputIdentity
) -> list[dict[str, Any]]:
    """Create one deterministic future solve slot per accepted case."""

    case_ids: set[str] = set()
    coordinates: set[tuple[float, int]] = set()
    schedule: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("case_id"))
        coordinate = (float(case.get("alpha")), int(case.get("beta_h")))
        if coordinate not in {(alpha, beta) for alpha in ALPHAS for beta in BETAS_H}:
            raise ProductionAuthorityError(
                "CASE_SCOPE_REJECTED", f"Case outside accepted grid: {coordinate}"
            )
        if case_id in case_ids or coordinate in coordinates:
            raise ProductionAuthorityError(
                "CASE_SCOPE_REJECTED", f"Duplicate production case request: {case_id}"
            )
        for required in (
            "R_kwh_battery",
            "P_out_kw_ac",
            "binding_start_index",
            "binding_historical_start",
            "binding_historical_end_exclusive",
            "valid_start_count",
        ):
            if required not in case:
                raise ProductionAuthorityError(
                    "CASE_REQUIREMENT_MISSING", f"{case_id} lacks {required}."
                )
        contexts = case.get("annual_identities", {})
        for context in (
            "requirements",
            "model_input",
            "analytical_replay",
            "billing_economics_context",
        ):
            received = _identity_from_mapping(
                contexts.get(context, {}), context=f"{case_id}:{context}"
            )
            try:
                require_same_annual_identity(
                    expected_identity,
                    received,
                    consumer=f"production_schedule:{case_id}:{context}",
                )
            except Exception as exc:
                raise ProductionAuthorityError(
                    "PRODUCTION_INPUT_AUTHORITY_FAIL", str(exc)
                ) from exc
        case_ids.add(case_id)
        coordinates.add(coordinate)
        schedule.append(
            {
                "solve_slot": index,
                "case": deepcopy(dict(case)),
                "annual_identity": expected_identity.as_dict(),
                "expected_native_optimizations": 1,
            }
        )
    return schedule


class OneSolveExecutionGuard:
    """Allow one armed synchronous optimize call per model; block all alternatives."""

    def __init__(self, model_type: type, native_optimize: Callable[..., Any]) -> None:
        self.model_type = model_type
        self.native_optimize = native_optimize
        self.calls = 0
        self.forbidden_attempts: list[str] = []
        self._armed: Any | None = None
        self._used: set[int] = set()
        self._stack = ExitStack()
        self._installed: dict[str, Callable[..., Any]] = {}

    def arm(self, model: Any) -> None:
        if self._armed is not None:
            raise ProductionAuthorityError(
                "EXECUTION_GUARD_FAIL", "A different model is already armed."
            )
        if not isinstance(model, self.model_type) or id(model) in self._used:
            raise ProductionAuthorityError(
                "EXECUTION_GUARD_FAIL", "Model is invalid or has already optimized."
            )
        self._armed = model

    def release(self, model: Any) -> None:
        if self._armed is model:
            self._armed = None

    def assert_intact(self) -> None:
        for name, installed in self._installed.items():
            if getattr(self.model_type, name) is not installed:
                raise ProductionAuthorityError(
                    "EXECUTION_GUARD_DISPLACED",
                    f"Execution guard displacement detected for {name}.",
                )

    def __enter__(self) -> "OneSolveExecutionGuard":
        def optimize(model: Any, *args: Any, **kwargs: Any) -> Any:
            self.assert_intact()
            if args or kwargs or model is not self._armed or id(model) in self._used:
                self.forbidden_attempts.append("unauthorized_optimize")
                raise ProductionAuthorityError(
                    "EXECUTION_GUARD_FAIL", "Unauthorized or repeated optimize attempt."
                )
            self._used.add(id(model))
            self.calls += 1
            return self.native_optimize(model)

        def blocked(*_args: Any, **_kwargs: Any) -> None:
            self.forbidden_attempts.append("async_batch_or_tune")
            raise ProductionAuthorityError(
                "EXECUTION_GUARD_FAIL",
                "optimizeAsync, optimizeBatch, and tune are forbidden.",
            )

        for name, replacement in (
            ("optimize", optimize),
            ("optimizeAsync", blocked),
            ("optimizeBatch", blocked),
            ("tune", blocked),
        ):
            if not hasattr(self.model_type, name):
                raise ProductionAuthorityError(
                    "EXECUTION_GUARD_FAIL", f"Required solver method is absent: {name}"
                )
            self._installed[name] = replacement
            self._stack.enter_context(patch.object(self.model_type, name, replacement))
        self.assert_intact()
        return self

    def __exit__(self, *args: Any) -> bool:
        return bool(self._stack.__exit__(*args))


class ProductionBackend(Protocol):
    annual_identity: AnnualInputIdentity
    model_constructions: int
    optimization_calls: int

    def solve_eob(self, settings: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def solve_layer_a(
        self, case: Mapping[str, Any], settings: Mapping[str, Any]
    ) -> Mapping[str, Any]: ...

    def solver_acceptance(self, result: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def audit_physical(
        self, result: Mapping[str, Any], case: Mapping[str, Any] | None
    ) -> Mapping[str, Any]: ...

    def audit_resilience(
        self, result: Mapping[str, Any], case: Mapping[str, Any]
    ) -> Mapping[str, Any]: ...

    def audit_billing(self, result: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def audit_transition(self, result: Mapping[str, Any]) -> Mapping[str, Any]: ...

    def audit_cost_degradation(
        self, result: Mapping[str, Any]
    ) -> tuple[Mapping[str, Any], Mapping[str, Any]]: ...

    def audit_rainflow(self, result: Mapping[str, Any]) -> Mapping[str, Any]: ...


class ProductionPublisher(Protocol):
    def publish_eob(self, record: Mapping[str, Any]) -> Any: ...

    def begin_layer_run(self, record: Mapping[str, Any]) -> Any: ...

    def publish_layer_case(self, run: Any, record: Mapping[str, Any]) -> Any: ...

    def complete_layer_run(self, run: Any, record: Mapping[str, Any]) -> Any: ...


def _load_helper(root: Path, relative: str, name: str) -> Any:
    return _load_step2e1(root)._load_module(root / relative, name)


class NativeProductionBackend:
    """Real future core/solver/audit adapter; constructed only after deployment PASS."""

    def __init__(
        self,
        root: Path,
        expected_identity: AnnualInputIdentity,
        *,
        confirm_native_solve: bool = False,
    ) -> None:
        require_native_solve_confirmation(confirm_native_solve)
        self.root = root.resolve()
        self.core = __import__(
            "src.annual_design_model_v7_2", fromlist=["annual_design_model_v7_2"]
        )
        self.gp = __import__("gurobipy")
        self.h16 = _load_helper(
            self.root,
            "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            "v73_production_h16",
        )
        self.h15d = _load_helper(
            self.root,
            "scripts/15d_run_corrected_eob_v7_2.py",
            "v73_production_h15d",
        )
        self.h19 = _load_helper(
            self.root,
            "scripts/19a_preflight_final_layer_a_81_cases.py",
            "v73_production_h19",
        )
        self.runner19 = _load_helper(
            self.root,
            "scripts/19b_run_final_layer_a_81_cases.py",
            "v73_production_runner19",
        )
        self.h09 = _load_helper(
            self.root,
            "scripts/09_build_valid_outage_start_sets.py",
            "v73_production_h09",
        )
        eob_policy = self.h15d.PRODUCTION_SOLVER_POLICY
        _require(
            eob_policy["mode"] == "binary"
            and eob_policy["MIPGap"] == 1e-6
            and eob_policy["OutputFlag"] == 1
            and eob_policy["NumericFocus"] == 1
            and eob_policy["TimeLimit"]["driver_sets_parameter"] is False
            and eob_policy["MIPFocus"]["uses_solver_default"] is True,
            "Historical 15d EOB solver policy differs from the v7.3 successor.",
        )
        _require(
            self.h19.MIP_GAP == 1e-6
            and tuple(self.h19.ALPHAS) == ALPHAS
            and tuple(self.h19.BETAS) == BETAS_H,
            "Historical 19a Layer-A production settings/grid drift.",
        )
        accepted = load_accepted_v7_3_annual_input(self.root)
        require_same_annual_identity(
            expected_identity, accepted.identity, consumer="native_production_backend"
        )
        self.annual_identity = accepted.identity
        self.inputs = self.core.load_annual_design_inputs(
            self.root,
            annual_parquet=accepted.resolved_path,
            annual_csv=impossible_csv_path(self.root),
        )
        used = Path(self.inputs.source_paths["annual_input"]).resolve()
        _require(used == accepted.resolved_path, "Native backend used a nonaccepted input.")
        fingerprint = annual_dataframe_fingerprint(self.inputs.annual)
        _require(
            fingerprint["fingerprint_sha256"] == accepted.identity.fingerprint_sha256,
            "Native backend dataframe identity drift.",
        )
        self.starts = pd.concat(
            [
                self.h09.build_valid_start_rows(self.inputs.annual["timestamp"], beta)
                for beta in BETAS_H
            ],
            ignore_index=True,
        )
        self.context = {
            "core": self.core,
            "inputs": self.inputs,
            "h16": self.h16,
            "h09": self.h09,
            "starts": self.starts,
        }
        self.model_constructions = 0
        self.optimization_calls = 0

    @staticmethod
    def _settings_kwargs(settings: Mapping[str, Any]) -> dict[str, Any]:
        required = {
            "mode": "binary",
            "MIPGap": 1e-6,
            "TimeLimit": None,
            "NumericFocus": 1,
            "MIPFocus": 0,
            "Threads": 0,
        }
        observed = {key: settings.get(key) for key in required}
        if observed != required:
            raise ProductionAuthorityError(
                "SOLVER_SETTINGS_DRIFT",
                f"Production solver settings differ: expected={required}, observed={observed}",
            )
        return {
            "mode": "binary",
            "mip_gap": 1e-6,
            "time_limit_sec": None,
            "output_flag": int(settings["OutputFlag"]),
            "numeric_focus": 1,
        }

    def _solve_once(
        self,
        settings: Mapping[str, Any],
        requirements: Any | None,
        *,
        layer_a: bool,
    ) -> Mapping[str, Any]:
        solve_settings = self.core.SolveSettings(**self._settings_kwargs(settings))
        native_build = self.core.build_eob_model
        held: dict[str, Any] = {}
        guard = OneSolveExecutionGuard(self.gp.Model, self.gp.Model.optimize)

        def audited_build(inputs: Any, configured: Any, received: Any) -> tuple[Any, Any]:
            if held:
                raise ProductionAuthorityError(
                    "MODEL_BUILD_FAIL", "Duplicate model construction."
                )
            model, handles = native_build(inputs, configured, received)
            self.model_constructions += 1
            held.update(model=model, handles=handles)
            if layer_a:
                audit = self.h19.audit_model(
                    model, handles, requirements, self.inputs, self.core
                )
                _require(audit.get("status") == "BUILD_PASS", "Layer-A build audit failed.")
            else:
                model.update()
                _require(
                    model.Status == self.gp.GRB.LOADED and model.SolCount == 0,
                    "EOB model was not loaded-unsolved.",
                )
                _require(
                    model.Params.MIPGap == 1e-6
                    and model.Params.NumericFocus == 1
                    and model.Params.OutputFlag == int(settings["OutputFlag"])
                    and math.isinf(model.Params.TimeLimit)
                    and model.Params.MIPFocus == 0
                    and model.Params.Threads == 0,
                    "EOB production solver settings drift.",
                )
            guard.arm(model)
            return model, handles

        result: Mapping[str, Any] | None = None
        try:
            with guard, patch.object(self.core, "build_eob_model", audited_build):
                result = self.core.solve_eob(
                    self.inputs,
                    solve_settings,
                    layer_a_requirements=requirements,
                )
                guard.assert_intact()
            if guard.calls != 1 or guard.forbidden_attempts:
                raise ProductionAuthorityError(
                    "EXECUTION_GUARD_FAIL",
                    f"Expected exactly one optimize; calls={guard.calls}, "
                    f"forbidden={guard.forbidden_attempts}",
                )
            handles = held["handles"]
            result = dict(result)
            result["terminal_e_seg_kwh"] = [
                float(handles["e_seg"][8760, segment].X) for segment in range(3)
            ]
            if layer_a:
                result["dispatch"] = result["dispatch"].copy()
                result["dispatch"]["u_mode"] = [
                    float(handles["u_mode"][hour].X) for hour in range(8760)
                ]
            return result
        finally:
            self.optimization_calls += guard.calls
            model = held.get("model")
            if model is not None:
                guard.release(model)
                model.dispose()

    def solve_eob(self, settings: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._solve_once(settings, None, layer_a=False)

    def solve_layer_a(
        self, case: Mapping[str, Any], settings: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        requirement = self.core.LayerAResilienceRequirements(
            alpha=float(case["alpha"]),
            beta_h=int(case["beta_h"]),
            reserve_kwh_battery=float(case["R_kwh_battery"]),
            power_requirement_kw_ac=float(case["P_out_kw_ac"]),
        )
        return self._solve_once(settings, requirement, layer_a=True)

    def solver_acceptance(self, result: Mapping[str, Any]) -> Mapping[str, Any]:
        status = self.runner19.solver_acceptance(result)
        _require(status == "COMPLETE_SOLVER_PASS", f"Solver result rejected: {status}")
        return {"status": "PASS", "accepted_status": status}

    def audit_physical(
        self, result: Mapping[str, Any], case: Mapping[str, Any] | None
    ) -> Mapping[str, Any]:
        if case is not None:
            return self.runner19.physical_audit(self.context, case, result)
        diagnostics = result["physical_diagnostics"]
        checks = {
            "ac_balance": diagnostics["max_ac_balance_residual_kw"]
            <= self.core.BALANCE_TOL,
            "segment_dynamics": diagnostics["max_segment_dynamics_residual_kwh"]
            <= self.core.BALANCE_TOL,
            "cyclic": diagnostics["max_segment_cyclic_residual_kwh"]
            <= self.core.BALANCE_TOL,
            "exclusive": diagnostics["max_simultaneous_charge_discharge_kw"]
            <= self.core.SIMULTANEOUS_TOL_KW,
        }
        _require(all(checks.values()), f"EOB physical audit failed: {checks}")
        return {"status": "PASS", "checks": checks, "diagnostics": diagnostics}

    def audit_resilience(
        self, result: Mapping[str, Any], case: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        audit, _table = self.runner19.all_start_audit(
            self.context, case, result["sizing"]
        )
        return audit

    def audit_billing(self, result: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.runner19.billing_audit(self.context, result)

    def audit_transition(self, result: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.runner19.transition_audit(self.context, result)

    def audit_cost_degradation(
        self, result: Mapping[str, Any]
    ) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        return self.runner19.cost_degradation_audit(self.context, result)

    def audit_rainflow(self, result: Mapping[str, Any]) -> Mapping[str, Any]:
        rain = self.h16.validate_representative_rainflow(
            self.root, self.inputs, result
        )
        _require(
            rain["summary"]["verdict"] == "RAINFLOW_VALIDATION_PASS"
            and all(value == "PASS" for value in rain["gates"].values()),
            "Rainflow validation failed.",
        )
        return {
            "status": "PASS",
            "summary": rain["summary"],
            "gates": rain["gates"],
        }


def _json_safe(value: Any) -> Any:
    """Historical accepted serialization semantics (see scripts/15d_run_corrected_eob_v7_2.py)."""
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


def _exclusive_json(path: Path, payload: Mapping[str, Any]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(_json_safe(dict(payload)), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _new_staging_directory(root: Path, prefix: str) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:10]
    final = root / run_id
    staging = root / f".{prefix}_{run_id}"
    if final.exists() or staging.exists():
        raise ProductionAuthorityError("ARTIFACT_PUBLICATION_FAIL", "Run ID collision.")
    staging.mkdir()
    return staging, final


def _write_result_bundle(directory: Path, result: Mapping[str, Any]) -> None:
    scalar = {key: value for key, value in result.items() if not isinstance(value, pd.DataFrame)}
    _exclusive_json(directory / "result.json", scalar)
    for key, value in result.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(directory / f"{key}.csv", index=False, encoding="utf-8-sig")


def _artifact_registry(
    directory: Path, *, exclude: Sequence[str] = ()
) -> dict[str, dict[str, Any]]:
    excluded = set(exclude)
    return {
        path.relative_to(directory).as_posix(): {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.relative_to(directory).as_posix() not in excluded
    }


def _verify_artifact_registry(
    directory: Path, registry: Mapping[str, Mapping[str, Any]]
) -> None:
    for relative, identity in registry.items():
        path = (directory / relative).resolve()
        _require(path.is_relative_to(directory.resolve()), "Artifact path escaped run root.")
        _require(path.is_file(), f"Registered artifact is missing: {relative}")
        _require(
            sha256_file(path) == identity["sha256"]
            and path.stat().st_size == identity["bytes"],
            f"Artifact identity mismatch: {relative}",
        )


class FilesystemProductionPublisher:
    """Exclusive staging/publication adapter used only after deployment authority PASS."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def publish_eob(self, record: Mapping[str, Any]) -> str:
        staging, final = _new_staging_directory(
            self.root / EOB_PRODUCTION_ROOT, "pending_eob"
        )
        try:
            _exclusive_json(staging / "authority.json", record["authority"])
            _exclusive_json(staging / "solver_settings.json", record["solver_settings"])
            _write_result_bundle(staging, record["result"])
            _exclusive_json(staging / "mandatory_audits.json", record["audits"])
            registry = _artifact_registry(staging)
            _verify_artifact_registry(staging, registry)
            _exclusive_json(
                staging / "completion_manifest.json",
                {
                    "status": "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE",
                    "annual_identity": record["annual_identity"],
                    "mandatory_audits": list(record["audits"]),
                    "optimization_calls": 1,
                    "artifact_registry": registry,
                },
            )
            os.rename(staging, final)
            return str(final)
        except BaseException:
            if staging.exists() and not (staging / "failure_manifest.json").exists():
                _exclusive_json(
                    staging / "failure_manifest.json",
                    {"status": "PUBLICATION_FAILED", "authoritative": False},
                )
            raise

    def begin_layer_run(self, record: Mapping[str, Any]) -> dict[str, Any]:
        staging, final = _new_staging_directory(
            self.root / LAYER_A_PRODUCTION_ROOT, "pending_layer_a"
        )
        _exclusive_json(staging / "authority.json", record["authority"])
        _exclusive_json(staging / "case_schedule.json", {"cases": record["schedule"]})
        (staging / "cases").mkdir()
        return {"staging": staging, "final": final, "published_cases": []}

    def publish_layer_case(self, run: Any, record: Mapping[str, Any]) -> str:
        case_id = str(record["case"]["case_id"])
        case_dir = Path(run["staging"]) / "cases" / case_id
        case_dir.mkdir()
        _exclusive_json(case_dir / "case_definition.json", record["case"])
        _exclusive_json(case_dir / "solver_settings.json", record["solver_settings"])
        _write_result_bundle(case_dir, record["result"])
        _exclusive_json(case_dir / "mandatory_audits.json", record["audits"])
        registry = _artifact_registry(case_dir)
        _verify_artifact_registry(case_dir, registry)
        _exclusive_json(
            case_dir / "completion_manifest.json",
            {
                "status": "COMPLETE_PASS",
                "case_id": case_id,
                "optimization_calls": 1,
                "mandatory_audits": list(record["audits"]),
                "artifact_registry": registry,
            },
        )
        run["published_cases"].append(case_id)
        return str(case_dir)

    def complete_layer_run(self, run: Any, record: Mapping[str, Any]) -> str:
        expected = list(record["case_ids"])
        _require(run["published_cases"] == expected, "Layer-A publication order/surface drift.")
        registry = _artifact_registry(Path(run["staging"]))
        _verify_artifact_registry(Path(run["staging"]), registry)
        _exclusive_json(
            Path(run["staging"]) / "completion_manifest.json",
            {
                "status": "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE",
                "case_set": record["case_set"],
                "case_count": len(expected),
                "case_ids": expected,
                "optimization_calls": len(expected),
                "artifact_registry": registry,
            },
        )
        os.rename(run["staging"], run["final"])
        return str(run["final"])


def _require_pass_audits(
    audits: Mapping[str, Mapping[str, Any]], mandatory: Sequence[str]
) -> None:
    if set(audits) != set(mandatory):
        raise ProductionAuthorityError(
            "POSTSOLVE_AUDIT_FAIL",
            f"Mandatory audit set differs: expected={list(mandatory)}, "
            f"observed={sorted(audits)}",
        )
    failed = [name for name, value in audits.items() if value.get("status") != "PASS"]
    if failed:
        raise ProductionAuthorityError(
            "POSTSOLVE_AUDIT_FAIL", f"Mandatory audits failed: {failed}"
        )


def _require_authority_recheck(
    original: Mapping[str, Any], observed: Mapping[str, Any]
) -> None:
    for field in ("status", "branch", "head", "origin_head", "annual_identity"):
        if observed.get(field) != original.get(field):
            raise ProductionAuthorityError(
                "PRODUCTION_AUTHORITY_CHANGED_DURING_RUN",
                f"Production authority changed during execution: {field}",
            )


def _execute_eob_authorized(
    *,
    authority: Mapping[str, Any],
    eob_preflight: Mapping[str, Any],
    backend: ProductionBackend,
    publisher: ProductionPublisher,
    authority_recheck: Callable[[], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if authority.get("status") != "PRODUCTION_AUTHORITY_FROZEN":
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN", "EOB authority record is not frozen."
        )
    expected_identity = _identity_from_mapping(
        eob_preflight["annual_identity"], context="EOB production"
    )
    require_same_annual_identity(
        expected_identity, backend.annual_identity, consumer="eob_production_backend"
    )
    settings = {
        "mode": "binary",
        "MIPGap": 1e-6,
        "TimeLimit": None,
        "NumericFocus": 1,
        "MIPFocus": 0,
        "Threads": 0,
        "OutputFlag": 1,
    }
    before = backend.optimization_calls
    result = backend.solve_eob(settings)
    if backend.optimization_calls != before + 1:
        raise ProductionAuthorityError(
            "EXECUTION_GUARD_FAIL", "EOB did not use exactly one optimization slot."
        )
    audits: dict[str, Mapping[str, Any]] = {}
    audits["solver"] = backend.solver_acceptance(result)
    audits["physical"] = backend.audit_physical(result, None)
    audits["billing"] = backend.audit_billing(result)
    audits["transition"] = backend.audit_transition(result)
    cost, degradation = backend.audit_cost_degradation(result)
    audits["cost"] = cost
    audits["degradation"] = degradation
    audits["rainflow"] = backend.audit_rainflow(result)
    _require_pass_audits(audits, MANDATORY_EOB_AUDITS)
    if authority_recheck is not None:
        _require_authority_recheck(authority, authority_recheck())
    output = publisher.publish_eob(
        {
            "authority": authority,
            "annual_identity": expected_identity.as_dict(),
            "solver_settings": settings,
            "result": result,
            "audits": audits,
        }
    )
    return {
        "status": "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE",
        "annual_identity": expected_identity.as_dict(),
        "solver_settings": settings,
        "optimization_calls": 1,
        "model_constructions": backend.model_constructions,
        "audits": audits,
        "publication": output,
    }


def _execute_layer_a_authorized(
    *,
    authority: Mapping[str, Any],
    final81: Mapping[str, Any],
    case_set: str,
    backend: ProductionBackend,
    publisher: ProductionPublisher,
    authority_recheck: Callable[[], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if authority.get("status") != "PRODUCTION_AUTHORITY_FROZEN":
        raise ProductionAuthorityError(
            "PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
            "Layer-A authority record is not frozen.",
        )
    expected_identity = _identity_from_mapping(
        final81["annual_identity"], context="Final81 production"
    )
    require_same_annual_identity(
        expected_identity,
        backend.annual_identity,
        consumer="layer_a_production_backend",
    )
    cases = select_production_cases(final81, case_set)
    schedule = build_execution_schedule(cases, expected_identity)
    settings = {
        "mode": "binary",
        "MIPGap": 1e-6,
        "TimeLimit": None,
        "NumericFocus": 1,
        "MIPFocus": 0,
        "Threads": 0,
        "OutputFlag": 0,
    }
    run = publisher.begin_layer_run(
        {
            "authority": authority,
            "case_set": case_set,
            "schedule": schedule,
            "solver_settings": settings,
        }
    )
    completed: list[dict[str, Any]] = []
    for slot in schedule:
        if authority_recheck is not None:
            _require_authority_recheck(authority, authority_recheck())
        case = slot["case"]
        before = backend.optimization_calls
        result = backend.solve_layer_a(case, settings)
        if backend.optimization_calls != before + 1:
            raise ProductionAuthorityError(
                "EXECUTION_GUARD_FAIL",
                f"{case['case_id']} did not use exactly one optimization slot.",
            )
        audits: dict[str, Mapping[str, Any]] = {}
        audits["solver"] = backend.solver_acceptance(result)
        audits["physical"] = backend.audit_physical(result, case)
        audits["resilience"] = backend.audit_resilience(result, case)
        audits["billing"] = backend.audit_billing(result)
        audits["transition"] = backend.audit_transition(result)
        cost, degradation = backend.audit_cost_degradation(result)
        audits["cost"] = cost
        audits["degradation"] = degradation
        audits["rainflow"] = backend.audit_rainflow(result)
        _require_pass_audits(audits, MANDATORY_LAYER_A_AUDITS)
        if authority_recheck is not None:
            _require_authority_recheck(authority, authority_recheck())
        publication = publisher.publish_layer_case(
            run,
            {
                "case": case,
                "annual_identity": expected_identity.as_dict(),
                "solver_settings": settings,
                "result": result,
                "audits": audits,
            },
        )
        completed.append(
            {
                "case_id": case["case_id"],
                "solve_slot": slot["solve_slot"],
                "optimization_calls": 1,
                "audits": audits,
                "publication": publication,
            }
        )
    if authority_recheck is not None:
        _require_authority_recheck(authority, authority_recheck())
    final = publisher.complete_layer_run(
        run,
        {
            "case_set": case_set,
            "case_ids": [item["case_id"] for item in completed],
        },
    )
    return {
        "status": "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE",
        "case_set": case_set,
        "case_count": len(completed),
        "unique_case_count": len({item["case_id"] for item in completed}),
        "annual_identity": expected_identity.as_dict(),
        "solver_settings": settings,
        "optimization_calls": len(completed),
        "model_constructions": backend.model_constructions,
        "cases": completed,
        "publication": final,
    }


def run_eob_production(
    root: Path = ROOT,
    *,
    execute_production: bool,
    confirm_native_solve: bool = False,
) -> dict[str, Any]:
    """Real EOB entry point; both explicit interlocks precede any backend creation."""

    if not execute_production:
        raise ProductionAuthorityError(
            "EXECUTION_DISABLED", "Explicit --execute-production is required."
        )
    require_native_solve_confirmation(confirm_native_solve)
    authority = require_production_authority(
        root, execute_production=execute_production, selected_scope="eob"
    )
    preflight = run_successor_stack(root)
    identity = _identity_from_mapping(preflight["eob"]["annual_identity"], context="EOB")
    backend = NativeProductionBackend(root, identity, confirm_native_solve=True)
    publisher = FilesystemProductionPublisher(root)
    return _execute_eob_authorized(
        authority=authority,
        eob_preflight=preflight["eob"],
        backend=backend,
        publisher=publisher,
        authority_recheck=lambda: require_production_authority(
            root, execute_production=True, selected_scope="eob"
        ),
    )


def run_layer_a_production(
    root: Path = ROOT,
    *,
    execute_production: bool,
    case_set: str | None,
    confirm_native_solve: bool = False,
) -> dict[str, Any]:
    """Real Layer-A/Final81 entry point with closed fixed case-set selection."""

    if not execute_production:
        raise ProductionAuthorityError(
            "EXECUTION_DISABLED", "Explicit --execute-production is required."
        )
    require_native_solve_confirmation(confirm_native_solve)
    authority = require_production_authority(
        root, execute_production=execute_production, selected_scope=case_set
    )
    if case_set is None:
        raise ProductionAuthorityError("CASE_SCOPE_REQUIRED", "Explicit case set required.")
    preflight = run_successor_stack(root)
    identity = _identity_from_mapping(
        preflight["final81"]["annual_identity"], context="Final81"
    )
    backend = NativeProductionBackend(root, identity, confirm_native_solve=True)
    publisher = FilesystemProductionPublisher(root)
    return _execute_layer_a_authorized(
        authority=authority,
        final81=preflight["final81"],
        case_set=case_set,
        backend=backend,
        publisher=publisher,
        authority_recheck=lambda: require_production_authority(
            root, execute_production=True, selected_scope=case_set
        ),
    )
