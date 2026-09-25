#!/usr/bin/env python3
"""V7.3 EOB successor preflight; default and current gate are strictly zero-solve."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.production_successor_stack_v7_3 import (  # noqa: E402
    ProductionAuthorityError,
    ProductionExecutionNotAuthorized,
    console_json_default,
    run_eob_production,
    run_successor_stack,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
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
            payload = run_eob_production(
                ROOT,
                execute_production=True,
                confirm_native_solve=args.confirm_native_solve,
            )
        else:
            stack = run_successor_stack(ROOT)
            payload = {
                "status": "PASS",
                "verdict": "V7.3 EOB SUCCESSOR ZERO-SOLVE PREFLIGHT PASS",
                "eob": stack["eob"],
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
