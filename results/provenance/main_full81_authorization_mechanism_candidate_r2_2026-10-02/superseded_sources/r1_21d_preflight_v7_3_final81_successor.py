#!/usr/bin/env python3
"""V7.3 Final81 preflight and deployment-gated future production entry point.

``RUNNER_VERSION`` below is the identity a Main Full81 scope authorization must
name.  The authorization mechanism re-derives this runner's SHA-256 from live
bytes *and* requires the live source to declare exactly this version string, so
an authorization can never name a runner version the runner does not carry.

Reporting the authorization state is not authorization.  The zero-solve
preflight below emits ``main_full81_authorization`` purely as provenance; while
no lawful authorization artifact exists it reads ``NOT_GRANTED``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNNER_VERSION = (
    "v7.4-main-full81-no-solve-preflight-runner-2026-10-02-candidate-r1"
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
            stack = run_successor_stack(ROOT)
            final81 = stack["final81"]
            selected_case_set = args.case_set or "full81"
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
                # authorization; `full81_authorization` inside the record states
                # NOT_AUTHORIZED and a separate authorization gate is required.
                "v7_4_authority_bundle_version": stack["v7_4_authority_bundle_version"],
                "v7_4_authority_alignment": stack["v7_4_authority_alignment"],
                # A ZERO-SOLVE PREFLIGHT PASS is not PRODUCTION_AUTHORITY_FROZEN,
                # is not FULL81 AUTHORIZED, and is not FULL81 EXECUTED. The
                # lifecycle block below reports each of those states separately.
                "u06_accepted_lifecycle": stack["u06_accepted_lifecycle"],
                "u06_lifecycle_module_version": stack["u06_lifecycle_module_version"],
                "u06_lineage_id": stack["u06_lineage_id"],
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
