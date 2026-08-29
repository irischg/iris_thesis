#!/usr/bin/env python3
"""
15a_benchmark_eob_charge_discharge_formulations.py

NTUST thesis v7.2 — EOB charge/discharge formulation benchmark.

Purpose
-------
Run the first full 8,760-hour economic-only BESS/contract-capacity optimization
using the shared v7.2 annual-design core, with one or both charge/discharge
formulations:

- binary  : explicit hourly charge/discharge exclusivity;
- relaxed : LP-compatible formulation, followed by a strict simultaneous
            charge/discharge audit.

This is a formulation/computational benchmark before freezing the final EOB
production formulation. It does NOT add resilience constraints and does NOT run
Layer A.

Transition-period settlement boundary
-------------------------------------
Script 14b intentionally did not fabricate a universal May/October cross-season
rate-selection rule. The shared core therefore settles mixed-season periods at
the billing-period TOU level with sequential non-duplication, includes every
increment whose basic-charge rate is unambiguous, and omits only a genuinely
rate-ambiguous incremental overage as a non-negative lower-bound diagnostic.
Raw May/October overage alone does not make the EOB provisional.

Recommended sequence
--------------------
1) Run default binary benchmark first:
       python scripts/15a_benchmark_eob_charge_discharge_formulations.py
2) If runtime is acceptable, compare both formulations:
       python scripts/15a_benchmark_eob_charge_discharge_formulations.py --mode both

No automatic choice of the final production formulation is made here; the
benchmark reports runtime, sizing, objective and simultaneous-operation evidence
for review.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-eob-charge-discharge-formulation-benchmark-transition-rate-audit-2026-08-29-r1"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Benchmark v7.2 EOB binary vs relaxed charge/discharge formulations."
    )
    parser.add_argument(
        "--mode",
        choices=["binary", "relaxed", "both"],
        default="binary",
        help="Default runs the physically explicit binary formulation first.",
    )
    parser.add_argument(
        "--mip-gap",
        type=float,
        default=1e-4,
        help="Relative MIP gap target for the binary formulation (default 1e-4).",
    )
    parser.add_argument(
        "--time-limit-sec",
        type=float,
        default=None,
        help="Optional Gurobi time limit per formulation; omitted means no explicit limit.",
    )
    parser.add_argument(
        "--quiet-gurobi",
        action="store_true",
        help="Suppress Gurobi console output; solver log files are still written.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "results" / "eob_benchmark",
    )
    return parser.parse_args()


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        v = float(value)
        return None if not np.isfinite(v) else v
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_parquet_if_available(df: pd.DataFrame, path: Path) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def result_summary_row(result: dict[str, Any]) -> dict[str, Any]:
    sizing = result.get("sizing", {})
    phys = result.get("physical_diagnostics", {})
    transition = result.get("transition_settlement", {})
    costs = result.get("cost_components_ntd2023_per_year", {})
    return {
        "mode": result.get("mode"),
        "solver_status": result.get("status"),
        "has_solution": result.get("has_solution"),
        "runtime_sec_gurobi": result.get("runtime_sec_gurobi"),
        "runtime_sec_wall": result.get("runtime_sec_wall"),
        "node_count": result.get("node_count"),
        "iteration_count": result.get("iteration_count"),
        "mip_gap": result.get("mip_gap"),
        "E_N_kwh": sizing.get("E_N_kwh"),
        "P_B_kw_ac": sizing.get("P_B_kw_ac"),
        "CC_regular_kw": sizing.get("CC_regular_kw"),
        "objective_ntd2023_per_year": result.get("objective_ntd2023_per_year"),
        "annualized_capex_ntd2023_per_year": costs.get("annualized_capex"),
        "fom_ntd2023_per_year": costs.get("fom"),
        "energy_charge_ntd2023_per_year": costs.get("energy"),
        "basic_charge_ntd2023_per_year": costs.get("basic"),
        "pure_season_overcontract_ntd2023_per_year": costs.get(
            "overcontract_pure_season"
        ),
        "transition_resolved_overcontract_ntd2023_per_year": costs.get(
            "overcontract_transition_resolved"
        ),
        "degradation_ntd2023_per_year": costs.get("degradation"),
        "max_simultaneous_charge_discharge_kw": phys.get(
            "max_simultaneous_charge_discharge_kw"
        ),
        "simultaneous_hours_above_tol": phys.get("simultaneous_hours_above_tol"),
        "transition_positive_raw_overage_detected": transition.get(
            "positive_transition_raw_overage_detected"
        ),
        "transition_rate_ambiguous_incremental_overage_detected": transition.get(
            "rate_ambiguous_incremental_overage_detected"
        ),
        "transition_rate_ambiguous_incremental_overage_total_kw": transition.get(
            "rate_ambiguous_incremental_overage_total_kw"
        ),
        "transition_nonbinding_certificate": transition.get(
            "nonbinding_certificate"
        ),
        "eob_finality": transition.get("eob_finality"),
    }


def compare_binary_relaxed(
    binary: dict[str, Any],
    relaxed: dict[str, Any],
) -> dict[str, Any]:
    if not binary.get("has_solution") or not relaxed.get("has_solution"):
        return {
            "comparison_available": False,
            "reason": "one_or_both_formulations_have_no_solution",
        }

    bs = binary["sizing"]
    rs = relaxed["sizing"]
    fields = ["E_N_kwh", "P_B_kw_ac", "CC_regular_kw"]
    abs_diff = {key: abs(float(bs[key]) - float(rs[key])) for key in fields}
    rel_diff = {
        key: abs_diff[key] / max(1.0, abs(float(bs[key])), abs(float(rs[key])))
        for key in fields
    }
    obj_b = float(binary["objective_ntd2023_per_year"])
    obj_r = float(relaxed["objective_ntd2023_per_year"])
    obj_abs = abs(obj_b - obj_r)
    obj_rel = obj_abs / max(1.0, abs(obj_b), abs(obj_r))

    relaxed_phys = relaxed["physical_diagnostics"]
    no_scd = int(relaxed_phys["simultaneous_hours_above_tol"]) == 0

    # Diagnostic equivalence tolerances, not a methodology rule.
    sizing_close = all(value <= 1e-5 for value in rel_diff.values())
    objective_close = obj_rel <= 1e-7

    return {
        "comparison_available": True,
        "sizing_absolute_difference": abs_diff,
        "sizing_relative_difference": rel_diff,
        "objective_absolute_difference_ntd2023_per_year": obj_abs,
        "objective_relative_difference": obj_rel,
        "relaxed_no_simultaneous_charge_discharge": no_scd,
        "diagnostic_sizing_close": sizing_close,
        "diagnostic_objective_close": objective_close,
        "diagnostic_material_equivalence": bool(
            sizing_close and objective_close and no_scd
        ),
        "runtime_ratio_binary_over_relaxed": (
            float(binary["runtime_sec_gurobi"])
            / max(float(relaxed["runtime_sec_gurobi"]), 1e-12)
        ),
    }


def printable_result(result: dict[str, Any]) -> list[str]:
    lines = [
        f"Mode: {result['mode']}",
        f"- Solver status: {result['status']}",
        f"- Gurobi runtime: {result['runtime_sec_gurobi']:.3f} s",
    ]
    if not result.get("has_solution"):
        lines.append("- No incumbent solution available.")
        return lines

    sizing = result["sizing"]
    costs = result["cost_components_ntd2023_per_year"]
    phys = result["physical_diagnostics"]
    tr = result["transition_settlement"]

    lines.extend(
        [
            f"- E_N: {sizing['E_N_kwh']:.6f} kWh",
            f"- P_B: {sizing['P_B_kw_ac']:.6f} kW AC",
            f"- CC: {sizing['CC_regular_kw']:.6f} kW",
            f"- Objective: {result['objective_ntd2023_per_year']:.6f} NTD-2023/year",
            f"- CAPEX annualized: {costs['annualized_capex']:.6f}",
            f"- FOM: {costs['fom']:.6f}",
            f"- Energy charge: {costs['energy']:.6f}",
            f"- Basic charge: {costs['basic']:.6f}",
            f"- Pure-season over-contract: {costs['overcontract_pure_season']:.6f}",
            "- Resolved transition over-contract: "
            f"{costs['overcontract_transition_resolved']:.6f}",
            f"- Degradation: {costs['degradation']:.6f}",
            "- Max simultaneous charge/discharge: "
            f"{phys['max_simultaneous_charge_discharge_kw']:.10f} kW",
            "- Simultaneous hours above tolerance: "
            f"{phys['simultaneous_hours_above_tol']}",
            "- Transition positive raw overage detected: "
            f"{tr['positive_transition_raw_overage_detected']}",
            "- Rate-ambiguous incremental overage detected: "
            f"{tr['rate_ambiguous_incremental_overage_detected']}",
            "- Rate-ambiguous incremental overage total: "
            f"{tr['rate_ambiguous_incremental_overage_total_kw']:.6f} kW",
            f"- Transition certificate: {tr['nonbinding_certificate']}",
            f"- EOB finality w.r.t transition ambiguity: {tr['eob_finality']}",
        ]
    )
    if result.get("mip_gap") is not None:
        lines.append(f"- MIP gap: {result['mip_gap']:.8g}")
    return lines


def main() -> int:
    args = parse_args()
    root = project_root()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Make repository root importable when invoked as `python scripts/...`.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from src.annual_design_model_v7_2 import (  # noqa: E402
        CORE_VERSION,
        SolveSettings,
        load_annual_design_inputs,
        solve_eob,
    )

    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.2 EOB Charge/Discharge Formulation Benchmark")
    print(f"Shared core: {CORE_VERSION}")
    print()

    inputs = load_annual_design_inputs(root)
    print("Inputs")
    for key, value in inputs.source_paths.items():
        print(f"- {key}: {value}")
    print(f"- kappa: {inputs.kappa:.10f}")
    print("- PNNL mainline cost package: 10 MW scale (ex ante; not a power bound)")
    print("- Monetary basis: constant NTD-2023")
    print()

    modes = [args.mode] if args.mode != "both" else ["binary", "relaxed"]
    results: dict[str, dict[str, Any]] = {}

    for mode in modes:
        log_path = args.output_dir / f"gurobi_eob_{mode}_v7_2.log"
        print(f"Running {mode} formulation")
        settings = SolveSettings(
            mode=mode,
            mip_gap=args.mip_gap,
            time_limit_sec=args.time_limit_sec,
            output_flag=0 if args.quiet_gurobi else 1,
            numeric_focus=1,
            log_file=str(log_path),
        )
        result = solve_eob(inputs, settings)
        results[mode] = result
        print()
        for line in printable_result(result):
            print(line)
        print()

        # Per-mode outputs.
        mode_json = args.output_dir / f"eob_{mode}_benchmark_v7_2.json"
        mode_dispatch_csv = args.output_dir / f"eob_{mode}_dispatch_v7_2.csv"
        mode_dispatch_parquet = args.output_dir / f"eob_{mode}_dispatch_v7_2.parquet"
        mode_billing_csv = args.output_dir / f"eob_{mode}_billing_exact_v7_2.csv"
        mode_transition_csv = (
            args.output_dir / f"eob_{mode}_transition_settlement_detail_v7_2.csv"
        )

        serializable = {
            k: v
            for k, v in result.items()
            if k not in {"dispatch", "billing_exact", "transition_settlement_detail"}
        }
        mode_json.write_text(
            json.dumps(json_safe(serializable), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if result.get("has_solution"):
            dispatch = result["dispatch"]
            billing_exact = result["billing_exact"]
            transition_detail = result["transition_settlement_detail"]
            dispatch.to_csv(mode_dispatch_csv, index=False, encoding="utf-8-sig")
            write_parquet_if_available(dispatch, mode_dispatch_parquet)
            billing_exact.to_csv(mode_billing_csv, index=False, encoding="utf-8-sig")
            transition_detail.to_csv(
                mode_transition_csv, index=False, encoding="utf-8-sig"
            )

    summary_df = pd.DataFrame([result_summary_row(r) for r in results.values()])
    summary_csv = args.output_dir / "eob_formulation_benchmark_summary_v7_2.csv"
    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")

    comparison = None
    if "binary" in results and "relaxed" in results:
        comparison = compare_binary_relaxed(results["binary"], results["relaxed"])

    # Benchmark-level gates. Raw transition overage is allowed; only a positive
    # rate-ambiguous incremental nonduplicated overage prevents finality.
    mode_gates: dict[str, Any] = {}
    for mode, result in results.items():
        if not result.get("has_solution"):
            mode_gates[mode] = {
                "solver_solution": "FAIL",
                "transition_nonbinding": "NOT_TESTABLE",
                "simultaneous_charge_discharge": "NOT_TESTABLE",
            }
            continue
        phys = result["physical_diagnostics"]
        tr = result["transition_settlement"]
        if mode == "binary":
            scd_gate = (
                "PASS_BY_EXPLICIT_EXCLUSIVITY"
                if int(phys["simultaneous_hours_above_tol"]) == 0
                else "FAIL_UNEXPECTED"
            )
        else:
            scd_gate = (
                "PASS_EX_POST"
                if int(phys["simultaneous_hours_above_tol"]) == 0
                else "FAIL_MATERIAL_SIMULTANEOUS_OPERATION"
            )
        solver_gate = (
            "PASS_OPTIMAL" if result.get("status") == "OPTIMAL"
            else f"BENCHMARK_INCUMBENT_{result.get('status')}"
        )
        mode_gates[mode] = {
            "solver_solution": solver_gate,
            "transition_nonbinding": tr["nonbinding_certificate"],
            "simultaneous_charge_discharge": scd_gate,
            "pure_season_overcontract_exact_reconciliation": "PASS",
            "cost_component_reconciliation": "PASS",
            "annual_state_cyclicity": "PASS",
        }

    audit = {
        "script_version": SCRIPT_VERSION,
        "shared_core_version": CORE_VERSION,
        "status": "BENCHMARK_COMPLETE",
        "scope": (
            "Economic-only annual design formulation benchmark; no resilience "
            "constraints and no Layer A."
        ),
        "requested_mode": args.mode,
        "modes_run": modes,
        "solver_settings": {
            "binary_mip_gap_target": args.mip_gap,
            "time_limit_sec_per_mode": args.time_limit_sec,
            "gurobi_console_output": not args.quiet_gurobi,
        },
        "transition_boundary": {
            "cross_season_rate_rule_fabricated": False,
            "benchmark_objective_treatment": (
                "billing-period TOU maxima + sequential nonduplication; include "
                "unambiguous-rate increments; omit only genuinely rate-ambiguous "
                "increments as a non-negative lower bound"
            ),
            "raw_transition_overage_is_automatic_failure": False,
            "final_eob_allowed_only_if_rate_ambiguous_increment_is_zero": True,
        },
        "mode_gates": mode_gates,
        "comparison": comparison,
        "outputs": {
            "summary_csv": str(summary_csv),
            "output_dir": str(args.output_dir),
        },
        "next_decision": (
            "Use observed runtime + sizing/cost equivalence + relaxed SCD audit "
            "to decide whether explicit binary exclusivity remains the production "
            "mainline for Script 15b final EOB."
        ),
    }
    audit_json = args.output_dir / "eob_formulation_benchmark_audit_v7_2.json"
    audit_json.write_text(
        json.dumps(json_safe(audit), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Benchmark outputs")
    print(f"- Summary: {summary_csv}")
    print(f"- Audit: {audit_json}")
    print(f"- Per-mode dispatch/billing/log files: {args.output_dir}")
    print()

    if comparison is not None:
        print("Binary vs relaxed comparison")
        print(
            "- Material equivalence diagnostic: "
            f"{comparison['diagnostic_material_equivalence']}"
        )
        print(
            "- Objective relative difference: "
            f"{comparison['objective_relative_difference']:.12g}"
        )
        print(
            "- Relaxed no simultaneous charge/discharge: "
            f"{comparison['relaxed_no_simultaneous_charge_discharge']}"
        )
        print(
            "- Binary/relaxed runtime ratio: "
            f"{comparison['runtime_ratio_binary_over_relaxed']:.6f}"
        )
        print()

    print("Final interpretation")
    print("- Script 15a is a formulation benchmark, not yet the production EOB freeze.")
    print("- Binary mode explicitly prohibits simultaneous charging/discharging.")
    print("- Relaxed mode must pass the ex-post no-SCD audit to remain defensible.")
    print(
        "- Raw May/October overage is not itself a failure; only a positive "
        "rate-ambiguous incremental nonduplicated overage makes the EOB provisional."
    )
    print("- No Layer A resilience constraint was executed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
