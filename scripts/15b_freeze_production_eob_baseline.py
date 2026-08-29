#!/usr/bin/env python3
"""
15b_freeze_production_eob_baseline.py

NTUST thesis v7.2 — production Economic-Only Benchmark (EOB) freeze.

Purpose
-------
Freeze the production EOB baseline after Script 15a has completed the
binary-vs-relaxed formulation benchmark.

Production decisions frozen here
--------------------------------
- The production formulation is BINARY charge/discharge exclusivity.
- The same shared annual-design core used by Script 15a is reused; economics
  and billing are not reimplemented here.
- EOB contains NO resilience constraints and NO alpha/beta requirement.
- The 10 MW PNNL package remains an ex-ante cost-scale selection, not a BESS
  power bound.
- Monetary basis remains constant NTD-2023.
- May/October transition over-contract treatment uses billing-period TOU
  maxima + sequential non-duplication. Only genuinely rate-ambiguous
  incremental overage would make the EOB provisional.
- Production EOB precision target is MIPGap <= 1e-6.

Why this is a freeze script instead of another benchmark
---------------------------------------------------------
Script 15a answered the formulation question. This script no longer compares
binary and relaxed formulations. It:
1) verifies the case-year billing-period boundaries against observed NTUST bills;
2) verifies annual hourly billing_usage_period_id tags match those boundaries;
3) verifies the binary-mainline decision checkpoint is present;
4) solves one production binary EOB;
5) enforces post-solve physical, billing, transition, and numerical gates;
6) performs an audit-only regression against the exact Script-15a binary
   benchmark. Those reference values are NEVER used as model inputs,
   constraints, bounds, or objective coefficients;
7) writes the frozen production EOB outputs for later Layer A denominators.

This script does NOT run Layer A.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-production-eob-freeze-2026-08-30-r1"

EXPECTED_CORE_VERSION = (
    "v7.2-annual-design-core-transition-rate-audit-2026-08-29-r1"
)

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760
EXPECTED_CASE_MONTHS = pd.period_range(
    "2024-11", "2025-10", freq="M"
).astype(str).tolist()

PRODUCTION_MIP_GAP_MAX = 1e-6

# Audit-only regression reference from the exact Script-15a binary solve:
# MIPGap target 1e-6, final best objective == best bound, final MIP gap = 0.
# These values are never passed into the optimization model.
BENCHMARK_REFERENCE = {
    "source": "Script 15a exact binary benchmark, 2026-08-29",
    "objective_ntd2023_per_year": 66738326.341512,
    "E_N_kwh": 86.111111,
    "P_B_kw_ac": 62.000000,
    "CC_regular_kw": 4399.137306,
}

BENCHMARK_TOL = {
    # Regression tolerances detect material model/input drift; solver accuracy
    # itself is enforced separately by the production MIP-gap gate.
    "objective_ntd2023_per_year": 100.0,  # NTD/year, ~1.5e-6 of annual objective
    "E_N_kwh": 0.10,
    "P_B_kw_ac": 0.10,
    "CC_regular_kw": 0.10,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Freeze the audited v7.2 production Economic-Only Benchmark."
    )
    parser.add_argument(
        "--mip-gap",
        type=float,
        default=1e-6,
        help=(
            "Binary relative MIP-gap target. Production freeze requires <=1e-6 "
            "(default 1e-6)."
        ),
    )
    parser.add_argument(
        "--time-limit-sec",
        type=float,
        default=None,
        help=(
            "Optional Gurobi time limit. Omitted by default. A time-limited "
            "incumbent will NOT pass the production freeze unless solver status "
            "is OPTIMAL and all gates pass."
        ),
    )
    parser.add_argument(
        "--quiet-gurobi",
        action="store_true",
        help="Suppress Gurobi console output; solver log is still written.",
    )
    parser.add_argument(
        "--bill-csv",
        type=Path,
        default=root / "data" / "reference" / "taipower_bills_final_clean.csv",
        help="Observed NTUST bill table used only for billing-boundary validation.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=(
            root
            / "docs"
            / "checkpoints"
            / "15a_formulation_decision_checkpoint_2026-08-29.md"
        ),
        help="15a formulation-decision checkpoint.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "results" / "eob_production",
        help="Production EOB output directory.",
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
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def sha256_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Cannot hash missing file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def write_parquet_if_available(df: pd.DataFrame, path: Path) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def expected_month_starts() -> pd.DatetimeIndex:
    return pd.date_range(
        FORMAL_START.normalize(),
        FORMAL_END_EXCLUSIVE.normalize() - pd.offsets.MonthBegin(1),
        freq="MS",
    )


def audit_observed_billing_boundaries(
    bill_csv: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Verify that the 12 case-year NTUST observed bill periods are exact
    calendar months.

    This is a CASE-SPECIFIC validation. It does not claim that all Taipower
    customers universally have calendar-month billing periods.
    """
    if not bill_csv.exists():
        raise FileNotFoundError(f"Observed bill CSV not found: {bill_csv}")

    bills = pd.read_csv(bill_csv)
    required = {"Period Start", "Period End"}
    missing = sorted(required - set(bills.columns))
    if missing:
        raise RuntimeError(
            f"Observed bill CSV missing billing-boundary columns: {missing}"
        )

    work = bills.copy()
    work["Period Start"] = pd.to_datetime(
        work["Period Start"], errors="coerce"
    ).dt.normalize()
    work["Period End"] = pd.to_datetime(
        work["Period End"], errors="coerce"
    ).dt.normalize()

    if work[["Period Start", "Period End"]].isna().any().any():
        raise RuntimeError("Observed bill Period Start/End contains unparsable dates.")

    expected_starts = expected_month_starts()
    rows: list[dict[str, Any]] = []

    for start in expected_starts:
        matched = work.loc[work["Period Start"].eq(start)]
        if len(matched) != 1:
            raise RuntimeError(
                "Expected exactly one observed bill row for case-year period start "
                f"{start.date()}; found {len(matched)}."
            )

        actual_end = pd.Timestamp(matched.iloc[0]["Period End"]).normalize()
        expected_end = (start + pd.offsets.MonthEnd(0)).normalize()
        period_id = start.to_period("M").strftime("%Y-%m")
        calendar_aligned = bool(actual_end == expected_end)

        rows.append(
            {
                "billing_usage_period_id": period_id,
                "observed_period_start": start,
                "observed_period_end_inclusive": actual_end,
                "expected_calendar_start": start,
                "expected_calendar_end_inclusive": expected_end,
                "calendar_month_boundary_match": calendar_aligned,
            }
        )

    audit_df = pd.DataFrame(rows)
    observed_period_ids = audit_df["billing_usage_period_id"].tolist()
    expected_period_ids = EXPECTED_CASE_MONTHS

    all_aligned = bool(audit_df["calendar_month_boundary_match"].all())
    exact_period_set = observed_period_ids == expected_period_ids

    if not all_aligned:
        bad = audit_df.loc[
            ~audit_df["calendar_month_boundary_match"]
        ].to_dict(orient="records")
        raise RuntimeError(
            "Observed NTUST case-year billing periods are not all exact calendar "
            f"months. Mismatches={bad}"
        )

    if not exact_period_set:
        raise RuntimeError(
            "Observed case-year bill period IDs do not equal the formal case-year "
            f"months. observed={observed_period_ids}, expected={expected_period_ids}"
        )

    summary = {
        "status": "PASS",
        "case_specific": True,
        "claim_scope": (
            "NTUST case-year bills only; not a universal Taipower billing-cycle rule"
        ),
        "expected_case_periods": 12,
        "observed_case_periods": int(len(audit_df)),
        "all_calendar_month_aligned": all_aligned,
        "period_ids_exact": exact_period_set,
    }
    return audit_df, summary


def audit_annual_billing_tags(
    annual: pd.DataFrame,
    bill_boundary_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Confirm that every annual hourly billing_usage_period_id equals the timestamp
    calendar month, and that the 12 resulting IDs are exactly the observed
    case-year bill periods.
    """
    required = {"timestamp", "billing_usage_period_id"}
    missing = sorted(required - set(annual.columns))
    if missing:
        raise RuntimeError(
            f"Annual input missing billing-tag columns required by 15b: {missing}"
        )

    work = annual.copy()
    ts = pd.to_datetime(work["timestamp"], errors="coerce")
    if ts.isna().any():
        raise RuntimeError("Annual input contains unparsable timestamps in 15b audit.")

    timestamp_period = ts.dt.to_period("M").astype(str)
    stored_period = work["billing_usage_period_id"].astype(str)

    mismatch = stored_period.ne(timestamp_period)
    mismatch_count = int(mismatch.sum())
    if mismatch_count:
        sample = work.loc[mismatch, ["timestamp", "billing_usage_period_id"]].head(10)
        raise RuntimeError(
            "Annual billing_usage_period_id does not match timestamp calendar month. "
            f"mismatch_count={mismatch_count}, sample={sample.to_dict(orient='records')}"
        )

    expected_ids = bill_boundary_df["billing_usage_period_id"].astype(str).tolist()
    annual_ids = sorted(stored_period.unique().tolist())
    if annual_ids != expected_ids:
        raise RuntimeError(
            "Annual hourly billing period IDs do not match observed NTUST case-year "
            f"bill periods. annual={annual_ids}, observed={expected_ids}"
        )

    rows: list[dict[str, Any]] = []
    for period_id in expected_ids:
        mask = stored_period.eq(period_id)
        period_ts = ts.loc[mask]
        if period_ts.empty:
            raise RuntimeError(f"No annual hourly rows for billing period {period_id}.")
        rows.append(
            {
                "billing_usage_period_id": period_id,
                "annual_hour_count": int(mask.sum()),
                "annual_first_timestamp": period_ts.min(),
                "annual_last_timestamp": period_ts.max(),
                "stored_id_equals_timestamp_month": True,
            }
        )

    detail = pd.DataFrame(rows)
    summary = {
        "status": "PASS",
        "row_count": int(len(work)),
        "expected_row_count": EXPECTED_ROWS,
        "hourly_period_id_mismatch_count": mismatch_count,
        "annual_period_ids": annual_ids,
        "observed_bill_period_ids": expected_ids,
        "period_id_sets_match": True,
    }
    return detail, summary


def audit_formulation_checkpoint(
    checkpoint: Path,
) -> dict[str, Any]:
    if not checkpoint.exists():
        raise FileNotFoundError(
            "15a formulation-decision checkpoint not found. Expected: "
            f"{checkpoint}"
        )

    text = checkpoint.read_text(encoding="utf-8")
    required_markers = [
        "Production mainline formulation: **Binary charge/discharge exclusivity**",
        "## MANDATORY CHECK BEFORE FULL 81-CASE RUN",
        "Mainline: **Binary**",
        "Relaxed: **Benchmark / fallback candidate only**",
    ]
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        raise RuntimeError(
            "15a formulation checkpoint does not contain the expected frozen "
            f"decision markers: {missing}"
        )

    return {
        "status": "PASS",
        "path": str(checkpoint),
        "sha256": sha256_file(checkpoint),
        "production_mainline": "binary",
        "relaxed_role": "benchmark_fallback_candidate_only",
        "mandatory_layer_a_runtime_checkpoint_present": True,
    }


def benchmark_regression(
    result: dict[str, Any],
) -> dict[str, Any]:
    """
    Audit-only comparison to the exact 15a binary benchmark.

    Nothing in BENCHMARK_REFERENCE is used to build or solve the model.
    """
    sizing = result["sizing"]
    observed = {
        "objective_ntd2023_per_year": float(
            result["objective_ntd2023_per_year"]
        ),
        "E_N_kwh": float(sizing["E_N_kwh"]),
        "P_B_kw_ac": float(sizing["P_B_kw_ac"]),
        "CC_regular_kw": float(sizing["CC_regular_kw"]),
    }

    detail: dict[str, Any] = {}
    all_pass = True
    for key, expected in BENCHMARK_REFERENCE.items():
        if key == "source":
            continue
        actual = observed[key]
        abs_diff = abs(actual - float(expected))
        tol = float(BENCHMARK_TOL[key])
        passed = abs_diff <= tol
        all_pass = all_pass and passed
        detail[key] = {
            "expected": float(expected),
            "actual": actual,
            "absolute_difference": abs_diff,
            "tolerance": tol,
            "gate": "PASS" if passed else "FAIL",
        }

    return {
        "status": "PASS" if all_pass else "FAIL",
        "audit_only_not_model_input": True,
        "reference_source": BENCHMARK_REFERENCE["source"],
        "detail": detail,
    }


def build_production_gates(
    result: dict[str, Any],
    *,
    requested_mip_gap: float,
    bill_boundary_summary: dict[str, Any],
    annual_billing_summary: dict[str, Any],
    checkpoint_summary: dict[str, Any],
    benchmark_summary: dict[str, Any],
) -> dict[str, Any]:
    has_solution = bool(result.get("has_solution"))
    status = str(result.get("status"))
    mip_gap = result.get("mip_gap")

    if not has_solution:
        return {
            "solver_has_solution": "FAIL",
            "solver_optimal": "FAIL",
            "binary_formulation": "NOT_TESTABLE",
            "mip_gap": "NOT_TESTABLE",
            "billing_period_boundaries": bill_boundary_summary.get("status", "FAIL"),
            "annual_billing_tags": annual_billing_summary.get("status", "FAIL"),
            "formulation_checkpoint": checkpoint_summary.get("status", "FAIL"),
            "benchmark_regression": "NOT_TESTABLE",
            "transition_rate_ambiguity": "NOT_TESTABLE",
            "simultaneous_charge_discharge": "NOT_TESTABLE",
            "physical_residuals": "NOT_TESTABLE",
            "cost_reconciliation": "NOT_TESTABLE",
        }

    phys = result["physical_diagnostics"]
    transition = result["transition_settlement"]
    cost_resid = abs(float(result["cost_reconciliation_residual_ntd"]))

    residual_pass = (
        abs(float(phys["max_ac_balance_residual_kw"])) <= 1e-5
        and abs(float(phys["max_segment_dynamics_residual_kwh"])) <= 1e-5
        and abs(float(phys["max_segment_cyclic_residual_kwh"])) <= 1e-5
    )

    actual_mip_gap = float(mip_gap) if mip_gap is not None else math.inf
    mip_pass = (
        requested_mip_gap <= PRODUCTION_MIP_GAP_MAX
        and actual_mip_gap <= PRODUCTION_MIP_GAP_MAX
    )

    transition_pass = (
        transition.get("nonbinding_certificate")
        == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
        and transition.get("eob_finality")
        == "EXACT_WITH_RESPECT_TO_TRANSITION_RATE_AMBIGUITY"
        and not bool(
            transition.get("rate_ambiguous_incremental_overage_detected")
        )
        and float(
            transition.get(
                "rate_ambiguous_incremental_overage_total_kw", math.inf
            )
        )
        <= 1e-6
    )

    scd_pass = (
        str(result.get("mode")) == "binary"
        and int(phys.get("simultaneous_hours_above_tol", -1)) == 0
        and float(phys.get("max_simultaneous_charge_discharge_kw", math.inf))
        <= float(phys.get("simultaneous_tolerance_kw", 1e-5))
    )

    return {
        "solver_has_solution": "PASS",
        "solver_optimal": "PASS" if status == "OPTIMAL" else "FAIL",
        "binary_formulation": (
            "PASS" if str(result.get("mode")) == "binary" else "FAIL"
        ),
        "mip_gap": "PASS" if mip_pass else "FAIL",
        "billing_period_boundaries": bill_boundary_summary.get("status", "FAIL"),
        "annual_billing_tags": annual_billing_summary.get("status", "FAIL"),
        "formulation_checkpoint": checkpoint_summary.get("status", "FAIL"),
        "benchmark_regression": benchmark_summary.get("status", "FAIL"),
        "transition_rate_ambiguity": "PASS" if transition_pass else "FAIL",
        "simultaneous_charge_discharge": "PASS" if scd_pass else "FAIL",
        "physical_residuals": "PASS" if residual_pass else "FAIL",
        "cost_reconciliation": (
            "PASS" if cost_resid <= 1e-3 else "FAIL"
        ),
    }


def all_gates_pass(gates: dict[str, Any]) -> bool:
    return all(str(value).startswith("PASS") for value in gates.values())


def source_hash_registry(
    *,
    root: Path,
    inputs: Any,
    bill_csv: Path,
    checkpoint: Path,
) -> dict[str, Any]:
    paths: dict[str, Path] = {
        "script_15b": Path(__file__).resolve(),
        "shared_core": root / "src" / "annual_design_model_v7_2.py",
        "observed_bill_csv": bill_csv,
        "formulation_checkpoint": checkpoint,
    }

    for key, value in inputs.source_paths.items():
        paths[key] = Path(value)

    registry: dict[str, Any] = {}
    for label, path in paths.items():
        registry[label] = {
            "path": str(path),
            "sha256": sha256_file(path),
        }
    return registry


def stripped_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {
            "dispatch",
            "billing_exact",
            "transition_settlement_detail",
        }
    }


def main() -> int:
    args = parse_args()
    root = project_root()

    if not np.isfinite(args.mip_gap) or args.mip_gap <= 0:
        raise ValueError("--mip-gap must be finite and positive.")
    if args.mip_gap > PRODUCTION_MIP_GAP_MAX:
        raise ValueError(
            "Production EOB freeze requires --mip-gap <= "
            f"{PRODUCTION_MIP_GAP_MAX:g}. Requested={args.mip_gap:g}"
        )
    if args.time_limit_sec is not None and args.time_limit_sec <= 0:
        raise ValueError("--time-limit-sec must be positive when provided.")

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
    print("NTUST v7.2 Production Economic-Only Benchmark Freeze")
    print(f"Shared core: {CORE_VERSION}")
    print("- Production formulation: BINARY")
    print("- Layer A resilience constraints: NOT EXECUTED")
    print()

    if CORE_VERSION != EXPECTED_CORE_VERSION:
        raise RuntimeError(
            "Shared-core version drift detected before production freeze. "
            f"expected={EXPECTED_CORE_VERSION!r}, actual={CORE_VERSION!r}. "
            "Re-audit before changing the frozen EOB."
        )

    # ------------------------------------------------------------------
    # Pre-solve provenance and billing-boundary gates.
    # ------------------------------------------------------------------
    print("Pre-solve production gates")

    checkpoint_summary = audit_formulation_checkpoint(args.checkpoint)
    print("- 15a binary-mainline checkpoint: PASS")

    bill_boundary_df, bill_boundary_summary = (
        audit_observed_billing_boundaries(args.bill_csv)
    )
    print(
        "- Observed NTUST billing-period boundaries: PASS "
        "(12/12 exact calendar months)"
    )

    inputs = load_annual_design_inputs(root)
    annual_billing_df, annual_billing_summary = audit_annual_billing_tags(
        inputs.annual,
        bill_boundary_df,
    )
    print("- Annual hourly billing-period tags vs observed bills: PASS")
    print("- 14a / 14b / annual-input shared-core input gates: PASS")
    print()

    print("Production inputs")
    for key, value in inputs.source_paths.items():
        print(f"- {key}: {value}")
    print(f"- observed_bill_boundaries: {args.bill_csv}")
    print(f"- formulation_checkpoint: {args.checkpoint}")
    print(f"- kappa: {inputs.kappa:.10f}")
    print("- PNNL mainline cost package: 10 MW scale (ex ante; not a power bound)")
    print("- Monetary basis: constant NTD-2023")
    print(f"- Production MIPGap target: {args.mip_gap:g}")
    print()

    # ------------------------------------------------------------------
    # One production solve: BINARY only.
    # ------------------------------------------------------------------
    log_path = (
        args.output_dir / "gurobi_eob_production_binary_v7_2.log"
    )
    settings = SolveSettings(
        mode="binary",
        mip_gap=float(args.mip_gap),
        time_limit_sec=args.time_limit_sec,
        output_flag=0 if args.quiet_gurobi else 1,
        numeric_focus=1,
        log_file=str(log_path),
    )

    print("Running production binary EOB")
    result = solve_eob(inputs, settings)
    print()

    if not result.get("has_solution"):
        benchmark_summary = {
            "status": "NOT_TESTABLE",
            "reason": "no_solution",
        }
    else:
        benchmark_summary = benchmark_regression(result)

    gates = build_production_gates(
        result,
        requested_mip_gap=float(args.mip_gap),
        bill_boundary_summary=bill_boundary_summary,
        annual_billing_summary=annual_billing_summary,
        checkpoint_summary=checkpoint_summary,
        benchmark_summary=benchmark_summary,
    )
    freeze_pass = all_gates_pass(gates)
    freeze_status = (
        "PRODUCTION_EOB_FREEZE_PASS"
        if freeze_pass
        else "PRODUCTION_EOB_FREEZE_FAIL"
    )

    # ------------------------------------------------------------------
    # Outputs.
    # ------------------------------------------------------------------
    bill_boundary_path = (
        args.output_dir
        / "eob_production_billing_period_boundary_audit_v7_2.csv"
    )
    annual_billing_path = (
        args.output_dir
        / "eob_production_annual_billing_tag_audit_v7_2.csv"
    )
    summary_path = (
        args.output_dir / "eob_production_summary_v7_2.csv"
    )
    audit_path = (
        args.output_dir / "eob_production_freeze_audit_v7_2.json"
    )
    result_path = (
        args.output_dir / "eob_production_result_v7_2.json"
    )
    dispatch_csv = (
        args.output_dir / "eob_production_dispatch_v7_2.csv"
    )
    dispatch_parquet = (
        args.output_dir / "eob_production_dispatch_v7_2.parquet"
    )
    billing_csv = (
        args.output_dir / "eob_production_billing_exact_v7_2.csv"
    )
    transition_csv = (
        args.output_dir
        / "eob_production_transition_settlement_detail_v7_2.csv"
    )

    bill_boundary_df.to_csv(
        bill_boundary_path, index=False, encoding="utf-8-sig"
    )
    annual_billing_df.to_csv(
        annual_billing_path, index=False, encoding="utf-8-sig"
    )

    if result.get("has_solution"):
        sizing = result["sizing"]
        costs = result["cost_components_ntd2023_per_year"]
        phys = result["physical_diagnostics"]
        transition = result["transition_settlement"]

        summary_df = pd.DataFrame(
            [
                {
                    "freeze_status": freeze_status,
                    "formulation": "binary",
                    "solver_status": result["status"],
                    "runtime_sec_gurobi": result["runtime_sec_gurobi"],
                    "mip_gap": result["mip_gap"],
                    "E_N_kwh": sizing["E_N_kwh"],
                    "P_B_kw_ac": sizing["P_B_kw_ac"],
                    "CC_regular_kw": sizing["CC_regular_kw"],
                    "objective_ntd2023_per_year": result[
                        "objective_ntd2023_per_year"
                    ],
                    "annualized_capex_ntd2023_per_year": costs[
                        "annualized_capex"
                    ],
                    "fom_ntd2023_per_year": costs["fom"],
                    "energy_charge_ntd2023_per_year": costs["energy"],
                    "basic_charge_ntd2023_per_year": costs["basic"],
                    "pure_season_overcontract_ntd2023_per_year": costs[
                        "overcontract_pure_season"
                    ],
                    "transition_resolved_overcontract_ntd2023_per_year": costs[
                        "overcontract_transition_resolved"
                    ],
                    "degradation_ntd2023_per_year": costs["degradation"],
                    "max_simultaneous_charge_discharge_kw": phys[
                        "max_simultaneous_charge_discharge_kw"
                    ],
                    "simultaneous_hours_above_tol": phys[
                        "simultaneous_hours_above_tol"
                    ],
                    "transition_certificate": transition[
                        "nonbinding_certificate"
                    ],
                    "eob_finality": transition["eob_finality"],
                    "layer_a_resilience_constraints_executed": False,
                }
            ]
        )
        summary_df.to_csv(
            summary_path, index=False, encoding="utf-8-sig"
        )

        result_path.write_text(
            json.dumps(
                json_safe(stripped_result(result)),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        result["dispatch"].to_csv(
            dispatch_csv, index=False, encoding="utf-8-sig"
        )
        write_parquet_if_available(
            result["dispatch"], dispatch_parquet
        )
        result["billing_exact"].to_csv(
            billing_csv, index=False, encoding="utf-8-sig"
        )
        result["transition_settlement_detail"].to_csv(
            transition_csv, index=False, encoding="utf-8-sig"
        )
    else:
        pd.DataFrame(
            [
                {
                    "freeze_status": freeze_status,
                    "formulation": "binary",
                    "solver_status": result.get("status"),
                    "layer_a_resilience_constraints_executed": False,
                }
            ]
        ).to_csv(summary_path, index=False, encoding="utf-8-sig")

        result_path.write_text(
            json.dumps(
                json_safe(stripped_result(result)),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    hashes = source_hash_registry(
        root=root,
        inputs=inputs,
        bill_csv=args.bill_csv,
        checkpoint=args.checkpoint,
    )

    audit = {
        "script_version": SCRIPT_VERSION,
        "core_version": CORE_VERSION,
        "freeze_status": freeze_status,
        "production_formulation": "binary",
        "production_mip_gap_target": float(args.mip_gap),
        "layer_a_resilience_constraints_executed": False,
        "eob_role": (
            "Economic-Only Benchmark denominator; same annual economics as "
            "Layer A but no resilience constraints"
        ),
        "pre_solve": {
            "observed_billing_period_boundaries": bill_boundary_summary,
            "annual_billing_tags": annual_billing_summary,
            "formulation_checkpoint": checkpoint_summary,
        },
        "benchmark_regression": benchmark_summary,
        "production_gates": gates,
        "source_hashes": hashes,
        "solver_result": json_safe(stripped_result(result)),
        "output_paths": {
            "summary_csv": str(summary_path),
            "result_json": str(result_path),
            "billing_period_boundary_audit_csv": str(
                bill_boundary_path
            ),
            "annual_billing_tag_audit_csv": str(annual_billing_path),
            "dispatch_csv": str(dispatch_csv),
            "dispatch_parquet": str(dispatch_parquet),
            "billing_exact_csv": str(billing_csv),
            "transition_settlement_detail_csv": str(transition_csv),
            "gurobi_log": str(log_path),
        },
        "next_step_if_pass": (
            "Use the frozen production EOB as the economic denominator, then "
            "build representative binary Layer A cases. Before the full 9x9 "
            "grid, obey the mandatory binary-runtime checkpoint recorded after 15a."
        ),
    }

    audit_path.write_text(
        json.dumps(json_safe(audit), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # ------------------------------------------------------------------
    # Terminal report.
    # ------------------------------------------------------------------
    print("Production EOB result")
    print(f"- Freeze status: {freeze_status}")
    print(f"- Solver status: {result.get('status')}")
    print(f"- Formulation: binary")
    print(f"- Gurobi runtime: {float(result.get('runtime_sec_gurobi', math.nan)):.3f} s")

    if result.get("has_solution"):
        sizing = result["sizing"]
        costs = result["cost_components_ntd2023_per_year"]
        phys = result["physical_diagnostics"]
        transition = result["transition_settlement"]

        print(f"- E_N: {float(sizing['E_N_kwh']):.6f} kWh")
        print(f"- P_B: {float(sizing['P_B_kw_ac']):.6f} kW AC")
        print(f"- CC: {float(sizing['CC_regular_kw']):.6f} kW")
        print(
            "- Objective: "
            f"{float(result['objective_ntd2023_per_year']):.6f} "
            "NTD-2023/year"
        )
        print(
            "- Energy charge: "
            f"{float(costs['energy']):.6f}"
        )
        print(
            "- Basic charge: "
            f"{float(costs['basic']):.6f}"
        )
        print(
            "- Pure-season over-contract: "
            f"{float(costs['overcontract_pure_season']):.6f}"
        )
        print(
            "- Resolved transition over-contract: "
            f"{float(costs['overcontract_transition_resolved']):.6f}"
        )
        print(
            "- Degradation: "
            f"{float(costs['degradation']):.6f}"
        )
        print(
            "- Max simultaneous charge/discharge: "
            f"{float(phys['max_simultaneous_charge_discharge_kw']):.10f} kW"
        )
        print(
            "- Simultaneous hours above tolerance: "
            f"{int(phys['simultaneous_hours_above_tol'])}"
        )
        print(
            "- Transition certificate: "
            f"{transition['nonbinding_certificate']}"
        )
        print(
            "- EOB finality: "
            f"{transition['eob_finality']}"
        )
        print(f"- MIP gap: {float(result['mip_gap']):.8g}")
        print(
            "- 15a exact-benchmark regression: "
            f"{benchmark_summary['status']}"
        )

    print()
    print("Production gates")
    for key, value in gates.items():
        print(f"- {key}: {value}")

    print()
    print("Outputs")
    print(f"- Summary: {summary_path}")
    print(f"- Freeze audit: {audit_path}")
    print(f"- Production result: {result_path}")
    print(f"- Billing boundary audit: {bill_boundary_path}")
    print(f"- Annual billing tag audit: {annual_billing_path}")
    if result.get("has_solution"):
        print(f"- Dispatch CSV: {dispatch_csv}")
        print(f"- Billing exact CSV: {billing_csv}")
        print(f"- Transition detail CSV: {transition_csv}")
    print(f"- Gurobi log: {log_path}")
    print()

    if freeze_pass:
        print("FINAL VERDICT")
        print("PRODUCTION EOB FREEZE PASS")
        print(
            "- Frozen denominator is ready for representative Layer A binary cases."
        )
        print(
            "- Do not launch the full 81-case grid before the mandatory "
            "Layer A runtime/convergence checkpoint."
        )
        return 0

    print("FINAL VERDICT")
    print("PRODUCTION EOB FREEZE FAIL")
    print("- Do not use this result as the Layer A economic denominator.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
