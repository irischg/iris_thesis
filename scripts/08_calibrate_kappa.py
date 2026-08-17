#!/usr/bin/env python3
"""
08_calibrate_kappa.py

NTUST thesis v7.1 — site-specific hourly-to-billing-demand calibration.

Mainline role
-------------
Reproduce the thesis billing-demand proxy coefficient kappa from:

    data/processed/annual_input_v7_1.parquet or .csv
    data/reference/billing_demand_registry.csv

Historical calibration boundary:
    P_grid,hist(t) = observed_load_kw(t) - observed_pv_kw(t)

For each calibration usage period m:
    H_m = max_t P_grid,hist(t)
    B_m = max_q billed 15-min maximum demand from the Taipower bill

Mainline calibration sample:
    2025-01 through 2025-10

Estimator:
    kappa = sum_m(H_m * B_m) / sum_m(H_m^2)

This script deliberately does NOT use:
- baseline_load_kw;
- pv_available_kw;
- planning residual load;
- bill-title month as the join key;
- a hard-coded kappa as the fitted value.

The previously audited kappa ~= 1.01037 is used only as a reproducibility
regression target after the coefficient has been recomputed from source data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-kappa-calibration-2026-08-17"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760

CALIBRATION_START = "2025-01"
CALIBRATION_END = "2025-10"
EXPECTED_CALIBRATION_MONTHS = 10

EXPECTED_SEP_2025_H_KW = 4985.0
EXPECTED_SEP_2025_B_KW = 5016.0
EXPECTED_KAPPA_ROUNDED_5DP = 1.01037

ANNUAL_REQUIRED = {
    "timestamp",
    "observed_load_kw",
    "observed_pv_kw",
    "pv_status",
    "integration_status",
}

REGISTRY_REQUIRED = {
    "usage_period_id",
    "usage_period_start",
    "usage_period_end_exclusive",
    "bill_title_month",
    "billed_peak_max_kw",
    "billed_half_max_kw",
    "billed_sat_half_max_kw",
    "billed_offpeak_max_kw",
    "billed_overall_max_kw",
    "is_kappa_calibration_month",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Calibrate the NTUST v7.1 hourly billing-demand proxy kappa."
    )
    parser.add_argument(
        "--annual-parquet",
        type=Path,
        default=root / "data" / "processed" / "annual_input_v7_1.parquet",
    )
    parser.add_argument(
        "--annual-csv",
        type=Path,
        default=root / "data" / "processed" / "annual_input_v7_1.csv",
    )
    parser.add_argument(
        "--billing-registry",
        type=Path,
        default=root / "data" / "reference" / "billing_demand_registry.csv",
    )
    parser.add_argument(
        "--pairs-output",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "kappa_calibration_pairs_v7_1.csv"
        ),
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "kappa_calibration_v7_1_audit.txt"
        ),
    )
    return parser.parse_args()


def read_annual(parquet_path: Path, csv_path: Path) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        "Final integrated annual input not found. Expected either:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}"
    )


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{label}: missing required columns {missing}")


def normalize_bool(series: pd.Series, label: str) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)

    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }
    out = series.astype(str).str.strip().str.lower().map(mapping)
    if out.isna().any():
        bad = series.loc[out.isna()].astype(str).drop_duplicates().tolist()
        raise ValueError(f"{label}: cannot parse boolean values {bad[:10]}")
    return out.astype(bool)


def validate_annual_input(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, ANNUAL_REQUIRED, "Annual input")
    out = df.copy()

    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    if out["timestamp"].isna().any():
        raise ValueError("Annual input contains unparsable timestamps.")

    if len(out) != EXPECTED_ROWS:
        raise ValueError(
            f"Annual input must contain exactly {EXPECTED_ROWS} rows; found {len(out)}."
        )

    if out["timestamp"].duplicated().any():
        raise ValueError("Annual input contains duplicate timestamps.")

    out = out.sort_values("timestamp").reset_index(drop=True)

    expected = pd.date_range(FORMAL_START, periods=EXPECTED_ROWS, freq="h")
    actual = pd.DatetimeIndex(out["timestamp"])
    if not actual.equals(expected):
        raise ValueError(
            "Annual input timeline is not the exact v7.1 case-year "
            "2024-11-01 00:00 through 2025-10-31 23:00."
        )

    statuses = set(out["integration_status"].astype(str).str.strip())
    if statuses != {"passed"}:
        raise ValueError(
            "Annual input integration_status must be exactly {'passed'} for "
            f"production kappa calibration; found {sorted(statuses)}."
        )

    for col in ["observed_load_kw", "observed_pv_kw"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if out[col].isna().any():
            raise ValueError(f"{col} contains missing/non-numeric values.")

    # Historical meter-boundary quantity. Do not clip and do not use planning columns.
    out["observed_grid_import_kw"] = (
        out["observed_load_kw"] - out["observed_pv_kw"]
    )

    out["usage_period_id_from_timestamp"] = (
        out["timestamp"].dt.to_period("M").astype(str)
    )

    return out


def validate_registry(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(df, REGISTRY_REQUIRED, "Billing registry")
    reg = df.copy()

    reg["usage_period_start"] = pd.to_datetime(
        reg["usage_period_start"], errors="coerce"
    )
    reg["usage_period_end_exclusive"] = pd.to_datetime(
        reg["usage_period_end_exclusive"], errors="coerce"
    )
    if reg[["usage_period_start", "usage_period_end_exclusive"]].isna().any().any():
        raise ValueError("Billing registry contains unparsable usage-period dates.")

    if reg["usage_period_id"].duplicated().any():
        dupes = reg.loc[
            reg["usage_period_id"].duplicated(), "usage_period_id"
        ].tolist()
        raise ValueError(f"Billing registry has duplicate usage periods: {dupes}")

    reg["is_kappa_calibration_month"] = normalize_bool(
        reg["is_kappa_calibration_month"],
        "is_kappa_calibration_month",
    )

    demand_cols = [
        "billed_peak_max_kw",
        "billed_half_max_kw",
        "billed_sat_half_max_kw",
        "billed_offpeak_max_kw",
        "billed_overall_max_kw",
    ]
    for col in demand_cols:
        reg[col] = pd.to_numeric(reg[col], errors="coerce")

    if reg["billed_overall_max_kw"].isna().any():
        raise ValueError("Billing registry contains missing billed_overall_max_kw.")

    calibration = reg.loc[reg["is_kappa_calibration_month"]].copy()

    expected_months = [
        str(p)
        for p in pd.period_range(CALIBRATION_START, CALIBRATION_END, freq="M")
    ]
    actual_months = calibration["usage_period_id"].sort_values().tolist()

    if actual_months != expected_months:
        raise ValueError(
            "Billing registry calibration sample must be exactly 2025-01..2025-10. "
            f"Found: {actual_months}"
        )

    if len(calibration) != EXPECTED_CALIBRATION_MONTHS:
        raise ValueError(
            f"Expected {EXPECTED_CALIBRATION_MONTHS} calibration months; "
            f"found {len(calibration)}."
        )

    return reg


def build_pairs(annual: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    cal = (
        registry.loc[registry["is_kappa_calibration_month"]]
        .sort_values("usage_period_start")
        .reset_index(drop=True)
    )

    rows: list[dict[str, object]] = []

    for _, bill in cal.iterrows():
        start = bill["usage_period_start"]
        end_exclusive = bill["usage_period_end_exclusive"]
        usage_id = str(bill["usage_period_id"])

        mask = (
            annual["timestamp"].ge(start)
            & annual["timestamp"].lt(end_exclusive)
        )
        month = annual.loc[mask].copy()

        expected_hours = int(
            (end_exclusive - start) / pd.Timedelta(hours=1)
        )
        if len(month) != expected_hours:
            raise ValueError(
                f"{usage_id}: hourly rows do not match exact billing usage period. "
                f"expected={expected_hours}, actual={len(month)}"
            )

        month_ids = set(month["usage_period_id_from_timestamp"])
        if month_ids != {usage_id}:
            raise ValueError(
                f"{usage_id}: hourly timestamps do not align to registry usage period; "
                f"found month IDs {sorted(month_ids)}"
            )

        pv_statuses = set(
            month["pv_status"].astype(str).str.strip().str.lower()
        )
        if pv_statuses != {"valid"}:
            raise ValueError(
                f"{usage_id}: calibration month is not homogeneous pv_status=valid; "
                f"found {sorted(pv_statuses)}."
            )

        h_kw = float(month["observed_grid_import_kw"].max())
        gross_load_max_kw = float(month["observed_load_kw"].max())
        b_kw = float(bill["billed_overall_max_kw"])

        rows.append(
            {
                "usage_period_id": usage_id,
                "usage_period_start": start,
                "usage_period_end_exclusive": end_exclusive,
                "bill_title_month": bill["bill_title_month"],
                "hour_count": len(month),
                "pv_status_set": "|".join(sorted(pv_statuses)),
                "hourly_observed_grid_max_kw_Hm": h_kw,
                "hourly_observed_gross_load_max_kw": gross_load_max_kw,
                "gross_minus_grid_peak_kw": gross_load_max_kw - h_kw,
                "billed_peak_max_kw": bill["billed_peak_max_kw"],
                "billed_half_max_kw": bill["billed_half_max_kw"],
                "billed_sat_half_max_kw": bill["billed_sat_half_max_kw"],
                "billed_offpeak_max_kw": bill["billed_offpeak_max_kw"],
                "billed_overall_max_kw_Bm": b_kw,
                "monthly_ratio_Bm_over_Hm": b_kw / h_kw,
            }
        )

    pairs = pd.DataFrame(rows)

    if len(pairs) != EXPECTED_CALIBRATION_MONTHS:
        raise ValueError(
            f"Expected {EXPECTED_CALIBRATION_MONTHS} Hm/Bm pairs; "
            f"built {len(pairs)}."
        )

    return pairs


def fit_kappa(pairs: pd.DataFrame) -> tuple[float, dict[str, float]]:
    h = pairs["hourly_observed_grid_max_kw_Hm"].to_numpy(dtype=float)
    b = pairs["billed_overall_max_kw_Bm"].to_numpy(dtype=float)

    denominator = float(np.dot(h, h))
    if denominator <= 0:
        raise ValueError("Kappa denominator sum(Hm^2) is non-positive.")

    numerator = float(np.dot(h, b))
    kappa = numerator / denominator

    fitted = kappa * h
    residual = b - fitted

    pairs["fitted_billed_max_kw"] = fitted
    pairs["residual_kw_Bm_minus_fitted"] = residual
    pairs["absolute_residual_kw"] = np.abs(residual)
    pairs["relative_residual_pct"] = np.where(
        b != 0.0,
        residual / b * 100.0,
        np.nan,
    )

    metrics = {
        "numerator_sum_HmBm": numerator,
        "denominator_sum_Hm2": denominator,
        "mae_kw": float(np.mean(np.abs(residual))),
        "rmse_kw": float(np.sqrt(np.mean(residual**2))),
        "mean_residual_kw": float(np.mean(residual)),
        "max_abs_residual_kw": float(np.max(np.abs(residual))),
        "ratio_mean": float(pairs["monthly_ratio_Bm_over_Hm"].mean()),
        "ratio_median": float(pairs["monthly_ratio_Bm_over_Hm"].median()),
        "ratio_min": float(pairs["monthly_ratio_Bm_over_Hm"].min()),
        "ratio_max": float(pairs["monthly_ratio_Bm_over_Hm"].max()),
    }
    return kappa, metrics


def assert_reproducibility(pairs: pd.DataFrame, kappa: float) -> None:
    sep = pairs.loc[pairs["usage_period_id"].eq("2025-09")]
    if len(sep) != 1:
        raise ValueError("Missing unique 2025-09 calibration pair.")

    sep = sep.iloc[0]
    h_sep = float(sep["hourly_observed_grid_max_kw_Hm"])
    b_sep = float(sep["billed_overall_max_kw_Bm"])

    if not np.isclose(h_sep, EXPECTED_SEP_2025_H_KW, rtol=0.0, atol=1e-9):
        raise ValueError(
            "2025-09 hourly-grid reproducibility anchor failed: "
            f"H_sep={h_sep}, expected={EXPECTED_SEP_2025_H_KW}."
        )

    if not np.isclose(b_sep, EXPECTED_SEP_2025_B_KW, rtol=0.0, atol=1e-9):
        raise ValueError(
            "2025-09 billed-demand reproducibility anchor failed: "
            f"B_sep={b_sep}, expected={EXPECTED_SEP_2025_B_KW}."
        )

    if round(float(kappa), 5) != EXPECTED_KAPPA_ROUNDED_5DP:
        raise ValueError(
            "Kappa scripted reproduction target failed: "
            f"computed={kappa:.10f}, rounded_5dp={kappa:.5f}, "
            f"expected_5dp={EXPECTED_KAPPA_ROUNDED_5DP:.5f}."
        )


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        args.pairs_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)

        annual_raw, annual_path = read_annual(
            args.annual_parquet,
            args.annual_csv,
        )
        annual = validate_annual_input(annual_raw)

        if not args.billing_registry.exists():
            raise FileNotFoundError(
                f"Billing registry not found: {args.billing_registry}. "
                "Run Script 07 first."
            )

        registry_raw = pd.read_csv(args.billing_registry)
        registry = validate_registry(registry_raw)

        pairs = build_pairs(annual, registry)
        kappa, metrics = fit_kappa(pairs)

        # Regression anchors are checked only after recomputing from source data.
        assert_reproducibility(pairs, kappa)

        pairs.to_csv(
            args.pairs_output,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d",
        )

        sep = pairs.loc[pairs["usage_period_id"].eq("2025-09")].iloc[0]

        lines = [
            "NTUST v7.1 Kappa Calibration Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Inputs",
            f"- Final integrated annual input: {annual_path}",
            f"- Billing-demand registry: {args.billing_registry}",
            "",
            "Historical calibration boundary",
            "- P_grid,hist = observed_load_kw - observed_pv_kw",
            "- baseline_load_kw / pv_available_kw were NOT used: PASSED",
            "- Hourly grid import was NOT clipped before monthly maximum: PASSED",
            "- Billing join uses actual usage-period start/end, not bill-title month: PASSED",
            "",
            "Calibration sample",
            "- Usage months: 2025-01 through 2025-10",
            f"- Calibration pairs: {len(pairs)} / {EXPECTED_CALIBRATION_MONTHS}",
            "- All calibration hourly rows have pv_status=valid: PASSED",
            "- 2024-11 and 2024-12 remain in annual simulation but are excluded "
            "from coefficient estimation: PASSED",
            "",
            "Estimator",
            "- Model: B_m ≈ kappa * H_m",
            "- Estimator: through-origin least squares",
            f"- Sum(H_m * B_m): {metrics['numerator_sum_HmBm']:.6f}",
            f"- Sum(H_m^2): {metrics['denominator_sum_Hm2']:.6f}",
            f"- kappa: {kappa:.10f}",
            f"- kappa (5 d.p.): {kappa:.5f}",
            "",
            "Monthly-ratio diagnostics",
            f"- Mean B_m/H_m: {metrics['ratio_mean']:.10f}",
            f"- Median B_m/H_m: {metrics['ratio_median']:.10f}",
            f"- Min B_m/H_m: {metrics['ratio_min']:.10f}",
            f"- Max B_m/H_m: {metrics['ratio_max']:.10f}",
            "",
            "Fit diagnostics",
            f"- MAE: {metrics['mae_kw']:.6f} kW",
            f"- RMSE: {metrics['rmse_kw']:.6f} kW",
            f"- Mean residual (B_m - fitted): {metrics['mean_residual_kw']:.6f} kW",
            f"- Max absolute residual: {metrics['max_abs_residual_kw']:.6f} kW",
            "",
            "Reproducibility anchors",
            f"- 2025-09 H_m: "
            f"{float(sep['hourly_observed_grid_max_kw_Hm']):.6f} kW "
            f"(expected {EXPECTED_SEP_2025_H_KW:.0f})",
            f"- 2025-09 B_m: "
            f"{float(sep['billed_overall_max_kw_Bm']):.6f} kW "
            f"(expected {EXPECTED_SEP_2025_B_KW:.0f})",
            f"- 2025-09 B_m/H_m: "
            f"{float(sep['monthly_ratio_Bm_over_Hm']):.10f}",
            "- September reproducibility anchor: PASSED",
            f"- Prior audited kappa target at 5 d.p.: "
            f"{EXPECTED_KAPPA_ROUNDED_5DP:.5f}",
            "- Kappa scripted reproduction target: PASSED",
            "",
            "Outputs",
            f"- Calibration-pair audit table: {args.pairs_output}",
            f"- Audit summary: {args.audit_output}",
            "",
            "Interpretation guardrail",
            "- kappa is an NTUST site-specific empirical multiplicative calibration.",
            "- It is a calibrated hourly proxy for Taipower 15-minute billing demand.",
            "- It is NOT an exact reconstruction of the 15-minute metering profile.",
            "",
            "Gate",
            "- Script 08 kappa-calibration gate: PASSED",
            "- The fitted kappa was computed from canonical hourly data + billing registry; "
            "it was not used as a hard-coded fit input.",
        ]

        args.audit_output.write_text("\n".join(lines), encoding="utf-8-sig")
        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(f"Script 08 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
