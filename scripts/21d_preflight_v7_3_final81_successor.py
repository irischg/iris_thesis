#!/usr/bin/env python3
"""V7.3 Final81 preflight and deployment-gated future production entry point."""

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
    print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
