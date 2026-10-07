#!/usr/bin/env python3
"""V7.3 Final81 preflight and deployment-gated future production entry point.

``RUNNER_VERSION`` below is the identity a Main Full81 scope authorization must
name.  The authorization mechanism re-derives this runner's SHA-256 from live
bytes *and* requires the live source to declare exactly this version string, so
an authorization can never name a runner version the runner does not carry.

N-04 (MAJOR, independent audit).  Reporting the authorization state is not
authorization, and an earlier revision of this runner only *reported* it: the
zero-solve path resolved ``main_full81_authorization`` as provenance and then
emitted ``PASS`` regardless.  A safe negative control showed
``verify_v7_4_authority_bundle(..., authorization=None)`` returning ``PASS``
while reporting Full81 as ``NOT_AUTHORIZED``, so this entrypoint was fail-open
against its own prerequisite.

The no-solve path below now **requires** the authorization through the canonical
guard :func:`~src.production_authority_bundle_v7_4.require_full81_scope_authorization`
before any preflight plan is built.  The mandatory no-solve production preflight
is itself a gated act: a PASSing authority bundle, a frozen production
authority, an accepted lifecycle and a clean repository are each insufficient,
alone or together.  The guard is scope-aware, so the non-Full81 case sets this
runner can also plan are unaffected.

Authorization for the no-solve preflight remains strictly separate from Full81
*execution*, from ``optimize()``, and from A2, each of which stays blocked.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: Advanced for the N-04 remediation.  The predecessor string
#: ``...2026-10-02-candidate-r2`` names the fail-open revision of this runner and
#: must never be reused for these semantics: the authorization contract changed
#: from "reports authorization" to "requires authorization".  Keeping the old
#: string would let the historical R2 authorization satisfy the version check
#: against a runner carrying a different contract, leaving only the SHA-256 to
#: separate them.
RUNNER_VERSION = (
    "v7.4-main-full81-no-solve-preflight-runner-2026-10-03-candidate-r3"
)

from src.main_full81_authorization_v7_4 import (  # noqa: E402
    resolve_full81_authorization,
)
from src.production_authority_bundle_v7_4 import (  # noqa: E402
    Full81AuthorizationNotGranted,
    require_full81_scope_authorization,
)
from src.production_authority_lifecycle_u06 import (  # noqa: E402
    resolve_u06_lifecycle,
)
from src.production_successor_stack_v7_3 import (  # noqa: E402
    PRODUCTION_CASE_SETS,
    ProductionAuthorityError,
    ProductionExecutionNotAuthorized,
    console_json_default,
    run_layer_a_production,
    run_successor_stack,
    select_production_cases,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case-set",
        choices=tuple(PRODUCTION_CASE_SETS),
        default=None,
        help=(
            "Closed future production case set. Required with --execute-production; "
            "default preflight validates full81."
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
            selected_case_set = args.case_set or "full81"
            # N-04 REMEDIATION. The mandatory no-solve production preflight is
            # itself a gated act, so it is REQUIRED here, not merely reported.
            # Fail-closed resolution order:
            #   1. resolve the accepted production-authority lifecycle;
            #   2. resolve the Main Full81 scope authorization from live bytes
            #      and Git (read-only; never raises; absence is NOT_GRANTED);
            #   3. REQUIRE that it lawfully grants
            #      MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT;
            #   4. only then build the zero-solve preflight plan.
            # Both resolvers are re-run here against live bytes rather than read
            # from the stack payload, which carries compact *summaries*: the
            # guard must prove the authorization itself, not trust a report of
            # it. The guard re-derives the live implementation identity, so an
            # authorization published against predecessor production code fails
            # closed even when committed, clean and pushed. It is scope-aware,
            # so a non-Full81 case set passes through it untouched.
            lifecycle = resolve_u06_lifecycle(ROOT)
            authorization = resolve_full81_authorization(ROOT, lifecycle)
            require_full81_scope_authorization(
                selected_case_set,
                root=ROOT,
                lifecycle=lifecycle,
                authorization=authorization,
            )
            stack = run_successor_stack(ROOT)
            final81 = stack["final81"]
            selected = select_production_cases(final81, selected_case_set)
            payload = {
                "status": "PASS",
                "verdict": "V7.3 FINAL81 SUCCESSOR ZERO-SOLVE PREFLIGHT PASS",
                "case_set": selected_case_set,
                "selected_case_count": len(selected),
                "selected_case_plan": selected,
                "final81": final81,
                # U-06: bind this preflight report to the accepted V7.4
                # production authority. Reporting the alignment is not Full81
                # authorization; the separate authorization gate that N-04
                # required has already been passed above to reach this point.
                "v7_4_authority_bundle_version": stack["v7_4_authority_bundle_version"],
                "v7_4_authority_alignment": stack["v7_4_authority_alignment"],
                # A ZERO-SOLVE PREFLIGHT PASS is not PRODUCTION_AUTHORITY_FROZEN,
                # is not FULL81 AUTHORIZED, and is not FULL81 EXECUTED. The
                # lifecycle block below reports each of those states separately.
                "u06_accepted_lifecycle": stack["u06_accepted_lifecycle"],
                "u06_lifecycle_module_version": stack["u06_lifecycle_module_version"],
                "u06_lineage_id": stack["u06_lineage_id"],
                "production_authority_generation_id": stack[
                    "production_authority_generation_id"
                ],
                "production_authority_lineage_id": stack[
                    "production_authority_lineage_id"
                ],
                "production_authority_generation": stack[
                    "production_authority_generation"
                ],
                "production_authority_historical_generations": stack[
                    "production_authority_historical_generations"
                ],
                "u06_runtime_dependency_report": stack[
                    "u06_runtime_dependency_report"
                ],
                "u06_future_acceptance_requirements": stack[
                    "u06_future_acceptance_requirements"
                ],
                # Main Full81 authorization is a SEPARATE state from this
                # zero-solve PASS, from PRODUCTION_AUTHORITY_FROZEN, and from
                # Full81 execution. It is resolved from an external, published
                # authorization artifact, never from a constant in this file.
                # Reaching this payload proves only that the authorization
                # granted the no-solve preflight; execution remains refused.
                "main_full81_no_solve_preflight_authorized": True,
                "runner_version": RUNNER_VERSION,
                "main_full81_authorization": stack["main_full81_authorization"],
                "full81_authorization_module_version": stack[
                    "full81_authorization_module_version"
                ],
                "full81_authorization_lineage_id": stack[
                    "full81_authorization_lineage_id"
                ],
                "full81_future_authorization_requirements": stack[
                    "full81_future_authorization_requirements"
                ],
                "full81_historical_design_precedent": stack[
                    "full81_historical_design_precedent"
                ],
                "execution_counters": stack["execution_counters"],
                "execution_boundary": stack["execution_boundary"],
            }
        code = 0
    except Full81AuthorizationNotGranted as exc:
        # N-04: the no-solve preflight was refused for want of a lawful Main
        # Full81 scope authorization. No preflight plan was built, no model was
        # constructed, and no optimization ran.
        payload = {
            "status": "NOT_AUTHORIZED",
            "error": str(exc),
            "main_full81_no_solve_preflight_authorized": False,
            "production_execution_attempted": False,
            "execution_counters": {
                "model_constructions": 0,
                "optimization_calls": 0,
                "economic_evaluations": 0,
            },
        }
        code = 2
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
