#!/usr/bin/env python3
"""
07_build_billing_demand_registry.py

NTUST thesis v7.1 — billing-demand registry builder.

Mainline role
-------------
Convert the audited consolidated Taipower bill table:

    data/reference/taipower_bills_final_clean.csv

into a machine-readable billing-demand registry for the next kappa-calibration
gate.

This script:
- uses actual usage-period start/end from the bill table;
- derives bill-title month from the ROC bill ID only as bill metadata;
- preserves the four billed TOU maximum-demand values;
- defines billed overall maximum B_m as the maximum of the available TOU maxima;
- fixes NTUST supplementary contract capacities at 0 kW per the v7.1 case boundary;
- identifies the ten calibration usage months 2025-01 through 2025-10;
- checks known 2025-09 and 2025-10 reproducibility anchors;
- optionally discovers original bill PDF filenames only when an exact ROC bill-ID
  token occurs in exactly one PDF filename under data/raw.

It does NOT calibrate kappa and does NOT run EOB, Layer A, Layer B, or any
optimization.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-billing-demand-registry-2026-08-17"

CALIBRATION_START = "2025-01"
CALIBRATION_END = "2025-10"
CASE_YEAR_FIRST_USAGE = "2024-11"
CASE_YEAR_LAST_USAGE = "2025-10"

REQUIRED_COLUMNS = {
    "Bill ID (ROC)",
    "Period Start",
    "Period End",
    "Customer Number",
    "Contract Capacity CP (kW)",
    "Max Demand - Peak (kW)",
    "Max Demand - Semi-peak (kW)",
    "Max Demand - Sat Semi-peak (kW)",
    "Max Demand - Off-peak (kW)",
    "Max Demand (kW) [calc]",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Build the NTUST v7.1 billing-demand registry."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "data" / "reference" / "taipower_bills_final_clean.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data" / "reference" / "billing_demand_registry.csv",
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "billing_demand_registry_v7_1_audit.txt"
        ),
    )
    parser.add_argument(
        "--raw-bill-dir",
        type=Path,
        default=root / "data" / "raw",
        help=(
            "Optional directory searched recursively for original bill PDFs. "
            "A filename is recorded only if exactly one PDF contains the exact "
            "ROC bill-ID token."
        ),
    )
    return parser.parse_args()


def require_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing:
        raise ValueError(f"Missing required bill-table columns: {missing}")


def parse_roc_bill_id(value: object) -> tuple[str, str]:
    """
    Example:
        11411 -> ROC 114 / month 11 -> Gregorian bill-title month 2025-11.
    """
    if pd.isna(value):
        raise ValueError("Bill ID (ROC) contains missing value.")

    raw = str(value).strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    raw = re.sub(r"\D", "", raw)

    if len(raw) != 5:
        raise ValueError(f"Unexpected ROC bill ID format: {value!r}")

    roc_year = int(raw[:3])
    month = int(raw[3:])
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid bill month in ROC bill ID: {value!r}")

    gregorian_year = roc_year + 1911
    return raw, f"{gregorian_year:04d}-{month:02d}"


def exact_bill_pdf_match(raw_bill_dir: Path, bill_id_roc: str) -> str | None:
    """
    Preserve source-bill filenames without guessing.

    Only accept a match when exactly one PDF filename contains the exact numeric
    bill-ID token, e.g. 11411 but not 114110.
    """
    if not raw_bill_dir.exists():
        return None

    pattern = re.compile(rf"(?<!\d){re.escape(bill_id_roc)}(?!\d)")
    matches = [
        p
        for p in raw_bill_dir.rglob("*.pdf")
        if pattern.search(p.stem)
    ]

    if len(matches) != 1:
        return None

    try:
        return str(matches[0].relative_to(project_root()))
    except ValueError:
        return str(matches[0])


def assert_full_calendar_month(start: pd.Timestamp, end_inclusive: pd.Timestamp) -> None:
    expected_start = start.to_period("M").start_time.normalize()
    expected_end = start.to_period("M").end_time.normalize()

    if start.normalize() != expected_start:
        raise ValueError(f"Usage period does not begin on month start: {start}")
    if end_inclusive.normalize() != expected_end:
        raise ValueError(
            f"Usage period does not end on calendar-month end: "
            f"{start.date()} to {end_inclusive.date()}"
        )


def validate_anchor(
    reg: pd.DataFrame,
    usage_period_id: str,
    expected: dict[str, float],
) -> None:
    row = reg.loc[reg["usage_period_id"].eq(usage_period_id)]
    if len(row) != 1:
        raise ValueError(
            f"Expected exactly one registry row for anchor {usage_period_id}; "
            f"found {len(row)}."
        )

    row = row.iloc[0]
    for column, expected_value in expected.items():
        actual = row[column]
        if pd.isna(actual) or not np.isclose(
            float(actual), float(expected_value), rtol=0.0, atol=1e-9
        ):
            raise ValueError(
                f"Anchor mismatch for {usage_period_id} / {column}: "
                f"actual={actual}, expected={expected_value}"
            )


def build_registry(df: pd.DataFrame, input_path: Path, raw_bill_dir: Path) -> pd.DataFrame:
    require_columns(df)
    src = df.copy()

    src["Period Start"] = pd.to_datetime(src["Period Start"], errors="coerce")
    src["Period End"] = pd.to_datetime(src["Period End"], errors="coerce")
    if src[["Period Start", "Period End"]].isna().any().any():
        raise ValueError("Period Start/End contains unparsable dates.")

    if src["Bill ID (ROC)"].duplicated().any():
        dupes = src.loc[src["Bill ID (ROC)"].duplicated(), "Bill ID (ROC)"].tolist()
        raise ValueError(f"Duplicate Bill ID (ROC): {dupes}")

    if src["Period Start"].duplicated().any():
        dupes = src.loc[src["Period Start"].duplicated(), "Period Start"].tolist()
        raise ValueError(f"Duplicate usage-period start: {dupes}")

    parsed = src["Bill ID (ROC)"].apply(parse_roc_bill_id)
    src["bill_id_roc"] = [x[0] for x in parsed]
    src["bill_title_month"] = [x[1] for x in parsed]

    for start, end in zip(src["Period Start"], src["Period End"]):
        if start > end:
            raise ValueError(f"Usage period start is after end: {start} > {end}")
        assert_full_calendar_month(start, end)

    src["usage_period_id"] = src["Period Start"].dt.to_period("M").astype(str)
    src["usage_period_start"] = src["Period Start"].dt.normalize()
    src["usage_period_end_inclusive"] = src["Period End"].dt.normalize()
    src["usage_period_end_exclusive"] = (
        src["usage_period_end_inclusive"] + pd.Timedelta(days=1)
    )

    # Bill-title month is metadata only. For the current monthly NTUST bills,
    # verify that it is the month immediately following the usage period.
    expected_bill_title = (
        src["usage_period_start"] + pd.offsets.MonthBegin(1)
    ).dt.to_period("M").astype(str)
    mismatch = ~src["bill_title_month"].eq(expected_bill_title)
    if mismatch.any():
        bad = src.loc[
            mismatch,
            ["bill_id_roc", "usage_period_id", "bill_title_month"],
        ]
        raise ValueError(
            "Bill-title month / usage-period alignment mismatch:\n"
            + bad.to_string(index=False)
        )

    reg = pd.DataFrame(
        {
            "bill_id_roc": src["bill_id_roc"],
            "bill_title_month": src["bill_title_month"],
            "usage_period_id": src["usage_period_id"],
            "usage_period_start": src["usage_period_start"],
            "usage_period_end_inclusive": src["usage_period_end_inclusive"],
            "usage_period_end_exclusive": src["usage_period_end_exclusive"],
            "customer_number": src["Customer Number"].astype(str),
            "regular_cc_kw": pd.to_numeric(
                src["Contract Capacity CP (kW)"], errors="coerce"
            ),
            # A3 CLOSED: NTUST supplementary contracts are fixed at 0.
            "supplementary_half_cc_kw": 0.0,
            "supplementary_sat_half_cc_kw": 0.0,
            "supplementary_offpeak_cc_kw": 0.0,
            "billed_peak_max_kw": pd.to_numeric(
                src["Max Demand - Peak (kW)"], errors="coerce"
            ),
            "billed_half_max_kw": pd.to_numeric(
                src["Max Demand - Semi-peak (kW)"], errors="coerce"
            ),
            "billed_sat_half_max_kw": pd.to_numeric(
                src["Max Demand - Sat Semi-peak (kW)"], errors="coerce"
            ),
            "billed_offpeak_max_kw": pd.to_numeric(
                src["Max Demand - Off-peak (kW)"], errors="coerce"
            ),
            "source_calc_overall_max_kw": pd.to_numeric(
                src["Max Demand (kW) [calc]"], errors="coerce"
            ),
        }
    )

    numeric_required = [
        "regular_cc_kw",
        "billed_half_max_kw",
        "billed_sat_half_max_kw",
        "billed_offpeak_max_kw",
        "source_calc_overall_max_kw",
    ]
    if reg[numeric_required].isna().any().any():
        bad = reg.loc[
            reg[numeric_required].isna().any(axis=1),
            ["bill_id_roc", "usage_period_id"] + numeric_required,
        ]
        raise ValueError(
            "Required billing-demand values contain missing/non-numeric data:\n"
            + bad.to_string(index=False)
        )

    demand_cols = [
        "billed_peak_max_kw",
        "billed_half_max_kw",
        "billed_sat_half_max_kw",
        "billed_offpeak_max_kw",
    ]

    if (reg[demand_cols].dropna() < 0).any().any():
        raise ValueError("Negative billed maximum-demand value found.")

    reg["billed_overall_max_kw"] = reg[demand_cols].max(axis=1, skipna=True)

    if not np.allclose(
        reg["billed_overall_max_kw"].to_numpy(float),
        reg["source_calc_overall_max_kw"].to_numpy(float),
        rtol=0.0,
        atol=1e-9,
    ):
        bad = reg.loc[
            ~np.isclose(
                reg["billed_overall_max_kw"],
                reg["source_calc_overall_max_kw"],
                rtol=0.0,
                atol=1e-9,
            ),
            [
                "bill_id_roc",
                "usage_period_id",
                "billed_overall_max_kw",
                "source_calc_overall_max_kw",
            ],
        ]
        raise ValueError(
            "Recomputed billed overall maximum does not match source [calc]:\n"
            + bad.to_string(index=False)
        )

    # The peak period is not applicable in some non-summer months; preserve NaN
    # instead of inventing a zero billed value.
    reg["peak_max_reported"] = reg["billed_peak_max_kw"].notna()

    reg["in_case_year"] = reg["usage_period_id"].between(
        CASE_YEAR_FIRST_USAGE, CASE_YEAR_LAST_USAGE
    )
    reg["is_kappa_calibration_month"] = reg["usage_period_id"].between(
        CALIBRATION_START, CALIBRATION_END
    )

    expected_calibration_months = {
        str(p)
        for p in pd.period_range(
            CALIBRATION_START, CALIBRATION_END, freq="M"
        )
    }
    actual_calibration_months = set(
        reg.loc[reg["is_kappa_calibration_month"], "usage_period_id"]
    )
    if actual_calibration_months != expected_calibration_months:
        missing = sorted(expected_calibration_months - actual_calibration_months)
        extra = sorted(actual_calibration_months - expected_calibration_months)
        raise ValueError(
            "Calibration-month coverage is not exactly 2025-01..2025-10. "
            f"missing={missing}, extra={extra}"
        )

    case_year_months = {
        str(p)
        for p in pd.period_range(
            CASE_YEAR_FIRST_USAGE, CASE_YEAR_LAST_USAGE, freq="M"
        )
    }
    actual_case_year_months = set(
        reg.loc[reg["in_case_year"], "usage_period_id"]
    )
    if actual_case_year_months != case_year_months:
        missing = sorted(case_year_months - actual_case_year_months)
        extra = sorted(actual_case_year_months - case_year_months)
        raise ValueError(
            "Case-year bill coverage is not exactly 2024-11..2025-10. "
            f"missing={missing}, extra={extra}"
        )

    if not reg["regular_cc_kw"].eq(5000.0).all():
        bad = reg.loc[
            ~reg["regular_cc_kw"].eq(5000.0),
            ["bill_id_roc", "usage_period_id", "regular_cc_kw"],
        ]
        raise ValueError(
            "Unexpected NTUST regular contract capacity:\n"
            + bad.to_string(index=False)
        )

    # Required reproducibility anchors.
    validate_anchor(
        reg,
        "2025-09",
        {
            "billed_peak_max_kw": 4896.0,
            "billed_half_max_kw": 5016.0,
            "billed_sat_half_max_kw": 3352.0,
            "billed_offpeak_max_kw": 3776.0,
            "billed_overall_max_kw": 5016.0,
        },
    )
    validate_anchor(
        reg,
        "2025-10",
        {
            "billed_peak_max_kw": 4752.0,
            "billed_half_max_kw": 4904.0,
            "billed_sat_half_max_kw": 3336.0,
            "billed_offpeak_max_kw": 4752.0,
            "billed_overall_max_kw": 4904.0,
        },
    )

    reg["source_bill_filename"] = [
        exact_bill_pdf_match(raw_bill_dir, bill_id)
        for bill_id in reg["bill_id_roc"]
    ]
    reg["source_registry_file"] = input_path.name
    reg["supplementary_cc_source"] = (
        "NTUST v7.1 A3 case boundary: supplementary contracts fixed at 0 kW"
    )

    reg = reg.sort_values("usage_period_start").reset_index(drop=True)
    return reg


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        if not args.input.exists():
            raise FileNotFoundError(
                f"Input bill table not found: {args.input}"
            )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.audit.parent.mkdir(parents=True, exist_ok=True)

        src = pd.read_csv(args.input)
        reg = build_registry(src, args.input, args.raw_bill_dir)

        reg.to_csv(
            args.output,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d",
        )

        matched_source_files = int(reg["source_bill_filename"].notna().sum())
        missing_source_files = int(reg["source_bill_filename"].isna().sum())

        cal = reg.loc[reg["is_kappa_calibration_month"]].copy()
        case_year = reg.loc[reg["in_case_year"]].copy()

        lines = [
            "NTUST v7.1 Billing-Demand Registry Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Input",
            f"- Consolidated bill table: {args.input}",
            f"- Input rows: {len(src)}",
            "",
            "Registry",
            f"- Output: {args.output}",
            f"- Registry rows: {len(reg)}",
            f"- Usage-period range: "
            f"{reg['usage_period_id'].min()} to {reg['usage_period_id'].max()}",
            "- Usage-period uniqueness: PASSED",
            "- Full-calendar-month usage periods: PASSED",
            "- Bill-title month is metadata; join basis is usage period: PASSED",
            "",
            "Contract-capacity boundary",
            "- Regular CC = 5000 kW for all registry rows: PASSED",
            "- Supplementary half / sat-half / off-peak CC = 0 kW: LOCKED v7.1 CASE",
            "",
            "Billed demand",
            "- Four TOU billed-max fields preserved.",
            "- Non-applicable peak-period maxima remain missing; they are not "
            "invented as zero.",
            "- billed_overall_max_kw = max of available TOU billed maxima: PASSED",
            "- Recomputed overall maxima match source Max Demand (kW) [calc]: PASSED",
            "",
            "Case-year / calibration coverage",
            f"- Case-year usage months 2024-11..2025-10: {len(case_year)} / 12",
            "- Case-year bill coverage: PASSED",
            f"- Kappa calibration usage months 2025-01..2025-10: {len(cal)} / 10",
            "- Calibration-month coverage: PASSED",
            "",
            "Regression anchors",
            "- 2025-09 billed maxima = 4896 / 5016 / 3352 / 3776 kW; "
            "overall = 5016 kW: PASSED",
            "- 2025-10 billed maxima = 4752 / 4904 / 3336 / 4752 kW; "
            "overall = 4904 kW: PASSED",
            "",
            "Source-bill filename provenance",
            f"- Exact PDF filename matches found under {args.raw_bill_dir}: "
            f"{matched_source_files}",
            f"- Registry rows without an exact PDF filename match: "
            f"{missing_source_files}",
        ]

        if missing_source_files:
            lines.extend(
                [
                    "- NOTE: No PDF filename was guessed. The consolidated CSV "
                    "remains the immediate source artifact.",
                    "- Before final thesis provenance freeze, populate/rename raw "
                    "bill PDFs with exact ROC bill-ID tokens if original PDF "
                    "filename traceability is required.",
                ]
            )
        else:
            lines.append("- Original bill PDF filename traceability: PASSED")

        lines.extend(
            [
                "",
                "Gate",
                "- Script 07 billing-demand registry gate: PASSED",
                "- Next step: Script 08 calibrate_kappa.py using observed_load_kw "
                "- observed_pv_kw from data/processed/annual_input_v7_1.*",
                "- No kappa coefficient was calibrated by Script 07.",
            ]
        )

        args.audit.write_text("\n".join(lines), encoding="utf-8-sig")
        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(f"Script 07 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
