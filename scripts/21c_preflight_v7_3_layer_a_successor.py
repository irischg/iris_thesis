#!/usr/bin/env python3
"""V7.3 Layer-A successor analytical preflight; no model is built or solved.

This entrypoint plans the **representative** Layer-A analytical case sets.  It
is deliberately *not* a Main Full81 gate.

N-05 (MAJOR, independent audit).  An earlier revision of this script defaulted
``selected_case_set`` to ``full81`` and also accepted ``--case-set full81``; it
then selected all 81 cases out of ``stack["final81"]`` and emitted a zero-solve
``PASS`` with no Main Full81 scope authorization anywhere on the path.  That
made this script a second, *unguarded* Main Full81 no-solve preflight
entrypoint, indistinguishable from the guarded one at the operational PASS
layer.

The remediation is **exclusivity, not a second guard**.  Adding the
authorization guard here would have left two independently valid Full81
no-solve PASS routes, which is the same defect in a different place.  Instead
the Full81 scope is now mechanically unroutable through this script:
:func:`reject_full81_scope` refuses it on every path, before any case plan is
selected, before any model is constructed, and before any optimization.
``scripts/21d_preflight_v7_3_final81_successor.py`` -- the one runner
``EXPECTED_RUNNER_RELATIVE_PATH`` permits an authorization to name -- remains
the sole Main Full81 no-solve production preflight entrypoint.

A Main Full81 scope authorization therefore cannot turn this script into a
second Full81 gate: no authorization is resolved, consulted, or even reachable
here, so granting one changes nothing about this refusal.

The legitimate non-Full81 Layer-A case sets are unaffected and still require no
authorization of any kind.  Because ``full81`` was also this script's implicit
default, removing it leaves no accepted default behind; rather than invent a
representative selection that no accepted artifact designates, an explicit case
scope is now required, exactly as the deployment gate has always required one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.production_successor_stack_v7_3 import (  # noqa: E402
    PRODUCTION_CASE_SETS,
    ProductionAuthorityError,
    ProductionExecutionNotAuthorized,
    console_json_default,
    run_layer_a_production,
    run_successor_stack,
    select_production_cases,
)


#: The Main Full81 scope name, spelled as ``PRODUCTION_CASE_SETS`` spells it.
FULL81_CASE_SET = "full81"

#: N-05.  The one entrypoint the Main Full81 no-solve production preflight is
#: routed through.  This is not a new designation: the authorization mechanism's
#: ``EXPECTED_RUNNER_RELATIVE_PATH`` already names exactly this path as the only
#: runner an authorization may target.  It is deliberately a literal rather than
#: an import, so that refusing Full81 here creates no dependency on the
#: authorization layer; a test asserts the two strings agree, so a lawful rename
#: of the runner cannot leave a stale path behind in this message.
FULL81_EXCLUSIVE_ENTRYPOINT = "scripts/21d_preflight_v7_3_final81_successor.py"

#: The case sets this Layer-A entrypoint may plan: every closed production case
#: set except the Main Full81 scope.  Derived from ``PRODUCTION_CASE_SETS``
#: rather than enumerated, so a lawfully added or renamed analytical case set
#: cannot silently fall out of the permitted set.
LAYER_A_PERMITTED_CASE_SETS: tuple[str, ...] = tuple(
    name for name in PRODUCTION_CASE_SETS if name != FULL81_CASE_SET
)


def reject_full81_scope(case_set: str | None) -> None:
    """Refuse the Main Full81 scope outright; this script is not its gate.

    Called before every other check in :func:`main`, on both the no-solve and
    the deployment-gated path, so the Full81 scope is refused identically
    whatever flags accompany it.  The refusal is unconditional: it consults no
    authorization, no lifecycle, and no repository state, because none of those
    could make this script the Main Full81 entrypoint.
    """

    if case_set is None:
        return
    if str(case_set).strip().lower() != FULL81_CASE_SET:
        return
    raise ProductionAuthorityError(
        "FULL81_REQUIRES_21D_ENTRYPOINT",
        "The Main Full81 no-solve production preflight is exclusively routed "
        f"through {FULL81_EXCLUSIVE_ENTRYPOINT}, which requires a separate, "
        "published Main Full81 scope authorization. This Layer-A analytical "
        "preflight is not a Main Full81 gate and cannot represent one, with or "
        "without a lawful authorization. Permitted case sets here: "
        f"{', '.join(LAYER_A_PERMITTED_CASE_SETS)}. No case plan was selected, "
        "no model was constructed, and no optimization ran.",
    )


def require_layer_a_case_scope(case_set: str | None) -> str:
    """Resolve the zero-solve Layer-A case scope, fail-closed.

    ``full81`` was this script's implicit default before N-05, so there is no
    accepted non-Full81 default to fall back to.  Selecting one here would be
    inventing a representative scope on this script's own authority, so an
    explicit scope is required instead -- the same fail-closed treatment, and
    the same ``CASE_SCOPE_REQUIRED`` status, that the deployment gate in
    ``src/production_successor_stack_v7_3.py`` already applies to an absent
    production case scope.
    """

    reject_full81_scope(case_set)
    if case_set is None:
        raise ProductionAuthorityError(
            "CASE_SCOPE_REQUIRED",
            "An explicit fixed production case scope is required. This Layer-A "
            "analytical preflight no longer defaults to the Main Full81 scope, "
            "which is exclusively routed through "
            f"{FULL81_EXCLUSIVE_ENTRYPOINT}, and no other case set is an "
            "accepted default for it. Pass --case-set with one of: "
            f"{', '.join(LAYER_A_PERMITTED_CASE_SETS)}. No case plan was "
            "selected, no model was constructed, and no optimization ran.",
        )
    return case_set


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case-set",
        # N-05: the full closed vocabulary is retained here deliberately, so
        # that --case-set full81 is refused by this script's own typed,
        # fail-closed status, in a JSON payload that records zero execution
        # counters, rather than by an argparse usage error that could not.
        choices=tuple(PRODUCTION_CASE_SETS),
        default=None,
        help=(
            "Closed case set; required. The Main Full81 scope is not available "
            "from this entrypoint. Permitted: "
            f"{', '.join(LAYER_A_PERMITTED_CASE_SETS)}."
        ),
    )
    parser.add_argument(
        "--execute-production",
        action="store_true",
        help="Future explicit execution interface; rejected until Macro Gate 2E-B.",
    )
    parser.add_argument(
        "--confirm-native-solve",
        action="store_true",
        help=(
            "Second explicit interlock. Required in addition to --execute-production "
            "before any native model may be constructed."
        ),
    )
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        # N-05 REMEDIATION. Routing precedes every interlock: whether this
        # script may represent the Main Full81 scope at all is prior to, and
        # independent of, whether execution is armed. Refusing here keeps the
        # refusal identical on the no-solve and the deployment-gated path.
        reject_full81_scope(args.case_set)
        if args.confirm_native_solve and not args.execute_production:
            raise ProductionAuthorityError(
                "EXECUTION_DISABLED",
                "--confirm-native-solve requires --execute-production; no model "
                "was constructed and no optimization ran.",
            )
        if args.execute_production:
            payload = run_layer_a_production(
                ROOT,
                execute_production=True,
                case_set=args.case_set,
                confirm_native_solve=args.confirm_native_solve,
            )
        else:
            # N-05: an explicit non-Full81 scope, resolved before the preflight
            # plan is built, so no Full81 case plan can be selected here.
            selected_case_set = require_layer_a_case_scope(args.case_set)
            stack = run_successor_stack(ROOT)
            selected = select_production_cases(stack["final81"], selected_case_set)
            payload = {
                "status": "PASS",
                "verdict": "V7.3 LAYER-A SUCCESSOR ZERO-SOLVE PREFLIGHT PASS",
                "case_set": selected_case_set,
                "selected_case_count": len(selected),
                "selected_case_plan": selected,
                "layer_a": stack["layer_a"],
                # N-05: this PASS is a Layer-A analytical preflight PASS only.
                # It is not, and can never be, a Main Full81 no-solve production
                # preflight PASS; that one act belongs exclusively to the
                # guarded entrypoint named here.
                "main_full81_scope_routable_here": False,
                "main_full81_no_solve_preflight_entrypoint": (
                    FULL81_EXCLUSIVE_ENTRYPOINT
                ),
                "permitted_case_sets": list(LAYER_A_PERMITTED_CASE_SETS),
                "execution_counters": stack["execution_counters"],
                "execution_boundary": stack["execution_boundary"],
            }
        code = 0
    except ProductionAuthorityError as exc:
        payload = {
            "status": exc.status,
            "error": str(exc),
            "production_execution_attempted": False,
            "execution_counters": {
                "model_constructions": 0,
                "optimization_calls": 0,
                "economic_evaluations": 0,
            },
        }
        code = 2
    except ProductionExecutionNotAuthorized as exc:
        payload = {
            "status": "NOT_AUTHORIZED",
            "error": str(exc),
            "production_execution_attempted": False,
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
            "production_execution_attempted": False,
        }
        code = 1
    print(
        json.dumps(
            payload,
            default=console_json_default,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
