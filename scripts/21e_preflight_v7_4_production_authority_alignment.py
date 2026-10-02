#!/usr/bin/env python3
"""V7.4 production-authority alignment verifier (strictly no-solve, read-only).

This script proves that the live repository bytes match every identity the
additive V7.4 production-authority bundle claims, and that the accepted
canonical planning input still satisfies its contract through the unmodified
accepted v7.3 input-authority loader.

It deliberately exposes **no** execution interface:

* there is no ``--execute-production`` flag and no ``--confirm-native-solve``
  flag; this script cannot reach a production path;
* no model is constructed, no optimization is called, no case is solved;
* no production run directory is created and nothing is written anywhere;
* verifying the alignment is **not** Main Full81 authorization.  The emitted
  ``full81_authorization`` block states ``NOT_AUTHORIZED`` and names the
  remaining lifecycle gates, the first of which is a fresh independent audit of
  this alignment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.production_authority_bundle_v7_4 import (  # noqa: E402
    BUNDLE_VERSION,
    MAIN_FULL81_AUTHORIZATION_STATUS,
    PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
    A2ExecutionHardBlocked,
    Full81AuthorizationNotGranted,
    ProductionAuthorityBundleError,
    alignment_is_not_full81_authorization,
    expected_pin_table,
    require_a2_hard_block,
    require_full81_scope_authorization,
    verify_pin_table_against_live_bytes,
    verify_v7_4_authority_bundle,
)
from src.production_authority_lifecycle_u06 import (  # noqa: E402
    LIFECYCLE_MODULE_VERSION,
    U06LifecycleError,
    future_acceptance_requirements,
    is_frozen,
    lifecycle_summary,
    require_frozen_lifecycle,
    resolve_u06_lifecycle,
)
from src.production_input_authority_v7_3 import (  # noqa: E402
    load_accepted_v7_3_annual_input,
)


SCRIPT_VERSION = "v7.4-production-authority-alignment-no-solve-verifier-2026-10-02-r1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pin-table",
        action="store_true",
        help="Also emit the per-pin expected-versus-live hash agreement report.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of indented JSON; no files are written.",
    )
    return parser.parse_args(argv)


def verify_guards() -> dict[str, object]:
    """Prove the two fail-closed guards actually reject, rather than asserting it."""

    results: dict[str, object] = {}

    try:
        require_full81_scope_authorization("full81")
    except Full81AuthorizationNotGranted as exc:
        results["full81_scope_guard"] = {"rejected": True, "status": exc.status}
    else:  # pragma: no cover - a pass here is a governance failure
        raise ProductionAuthorityBundleError(
            "FULL81_GUARD_DID_NOT_REJECT",
            "The Full81 scope guard failed to reject an unauthorized Full81 scope.",
        )

    a2_rejected: dict[str, str] = {}
    for scope in ("a2", "robustness", "variable_floor", "a2-variable-floor"):
        try:
            require_a2_hard_block(scope)
        except A2ExecutionHardBlocked as exc:
            a2_rejected[scope] = exc.status
        else:  # pragma: no cover - a pass here is a governance failure
            raise ProductionAuthorityBundleError(
                "A2_GUARD_DID_NOT_REJECT",
                f"The A2 hard-block guard failed to reject scope {scope!r}.",
            )
    results["a2_scope_guard"] = {"rejected": True, "statuses": a2_rejected}

    # The accepted non-A2 scopes must remain reachable by the guards, so the
    # alignment adds no restriction to already-accepted production scopes.
    for scope in ("eob", "low", "central", "high", "core-three", "historical-five"):
        require_a2_hard_block(scope)
        require_full81_scope_authorization(scope)
    results["accepted_non_full81_scopes_unaffected"] = True
    return results


def verify_lifecycle_gate(root: Path) -> dict[str, object]:
    """Prove the U-06 lifecycle gate is fail-closed while acceptance is absent."""

    lifecycle = resolve_u06_lifecycle(root)
    report: dict[str, object] = {"resolved": lifecycle_summary(lifecycle)}

    try:
        require_frozen_lifecycle(lifecycle)
    except U06LifecycleError as exc:
        report["freeze_rejected"] = True
        report["freeze_rejection_status"] = exc.status
        report["freeze_rejection_reason"] = str(exc)
    else:  # pragma: no cover - a pass here is a governance failure
        raise ProductionAuthorityBundleError(
            "U06_LIFECYCLE_GATE_DID_NOT_REJECT",
            "The U-06 lifecycle gate authorized a production-authority freeze "
            "although no accepted U-06 lifecycle record exists.",
        )

    # An omitted lifecycle, and a lifecycle carrying one optimistic field, must
    # both be rejected: absence is never acceptance.
    for label, candidate in (
        ("omitted", None),
        ("single_optimistic_field", {"production_authority_freeze_status": "FROZEN"}),
    ):
        try:
            require_frozen_lifecycle(candidate)
        except U06LifecycleError:
            report[label + "_rejected"] = True
        else:  # pragma: no cover - a pass here is a governance failure
            raise ProductionAuthorityBundleError(
                "U06_LIFECYCLE_GATE_DID_NOT_REJECT",
                "The U-06 lifecycle gate accepted a " + label + " lifecycle.",
            )

    report["is_frozen"] = is_frozen(lifecycle)
    report["future_acceptance_requirements"] = future_acceptance_requirements()
    return report


def run_alignment_verification(
    root: Path = ROOT, *, pin_table: bool = False
) -> dict[str, object]:
    root = root.resolve()
    lifecycle = resolve_u06_lifecycle(root)
    bundle = verify_v7_4_authority_bundle(root, lifecycle)
    lifecycle_gate = verify_lifecycle_gate(root)

    # Re-prove the canonical planning input through the unmodified accepted
    # v7.3 loader: exact path, exact SHA-256, 8,760 ordered formal hours,
    # mainline role, passed integration status. No value is altered.
    accepted = load_accepted_v7_3_annual_input(root)
    contract = bundle["canonical_planning_input"]
    live_input = {
        "path": accepted.identity.path,
        "sha256": accepted.identity.sha256,
        "artifact_role": accepted.identity.artifact_role,
        "row_count": accepted.identity.row_count,
        "column_count": int(accepted.dataframe.shape[1]),
        "window_start": str(accepted.dataframe["timestamp"].iloc[0]),
        "window_end_inclusive": str(accepted.dataframe["timestamp"].iloc[-1]),
        "fingerprint_sha256": accepted.identity.fingerprint_sha256,
    }
    mismatches = [
        field
        for field, expected in (
            ("path", contract["path"]),
            ("sha256", contract["sha256"]),
            ("artifact_role", contract["artifact_role"]),
            ("row_count", contract["expected_rows"]),
            ("column_count", contract["expected_columns"]),
            ("window_start", contract["window_start"]),
            ("window_end_inclusive", contract["window_end_inclusive"]),
        )
        if live_input[field] != expected
    ]
    if mismatches:
        raise ProductionAuthorityBundleError(
            "CANONICAL_INPUT_CONTRACT_FAIL",
            f"Canonical planning input contract mismatch: {mismatches}",
        )

    payload: dict[str, object] = {
        "status": "PASS",
        "verdict": (
            "V7.4 BASE AUTHORITY CANDIDATE-ALIGNED — U-06 LIFECYCLE NOT "
            "ACCEPTED, PRODUCTION AUTHORITY NOT FROZEN, MAIN FULL81 NOT AUTHORIZED"
        ),
        "script_version": SCRIPT_VERSION,
        "bundle_version": BUNDLE_VERSION,
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
        "production_authority_alignment": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "u06_independent_audit_status": lifecycle["u06_independent_audit_status"],
        "u06_acceptance_status": lifecycle["u06_acceptance_status"],
        "accepted_lifecycle_overlay": lifecycle["accepted_lifecycle_overlay"],
        "production_authority_freeze_status": lifecycle[
            "production_authority_freeze_status"
        ],
        "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
        "full81_authorization": alignment_is_not_full81_authorization(lifecycle),
        "u06_lifecycle_gate": lifecycle_gate,
        "authority_bundle": bundle,
        "canonical_planning_input_live": live_input,
        "canonical_planning_input_contract": contract,
        "guards": verify_guards(),
        "execution_counters": bundle["execution_counters"],
        "execution_boundary": bundle["execution_boundary"],
    }
    if pin_table:
        payload["expected_pin_table"] = expected_pin_table()
        payload["live_pin_agreement"] = verify_pin_table_against_live_bytes(root)
    return payload


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload: dict[str, object] = run_alignment_verification(
            ROOT, pin_table=args.pin_table
        )
        code = 0
    except ProductionAuthorityBundleError as exc:
        payload = {
            "status": exc.status,
            "error": str(exc),
            "production_authority_alignment": "NOT_VERIFIED",
            "production_authority_freeze_status": "NOT_FROZEN",
            "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
            "execution_counters": {
                "model_constructions": 0,
                "optimization_calls": 0,
                "economic_evaluations": 0,
            },
        }
        code = 2
    except Exception as exc:
        payload = {
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "production_authority_alignment": "NOT_VERIFIED",
            "production_authority_freeze_status": "NOT_FROZEN",
            "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
        }
        code = 1
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
