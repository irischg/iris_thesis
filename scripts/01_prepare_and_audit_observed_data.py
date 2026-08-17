from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


SCRIPT_VERSION = "v7-observed-input-2026-08-15"
FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760
LONG_PV_UNAVAILABLE_STATUSES = {"pre_system", "missing_winter"}


def project_root() -> Path:
    # Expected location: <project>/scripts/01_prepare_and_audit_observed_data.py
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description=(
            "Prepare and audit the v7 NTUST observed case-year dataset from "
            "data/interim/load_solar_cleaned.csv. The source file is never modified."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=root / "data" / "interim" / "load_solar_cleaned.csv",
        help="Cleaned observed input CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Directory for normalized observed case-year outputs.",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=root / "results" / "data_audit",
        help="Directory for audit outputs.",
    )
    return parser.parse_args()


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")


def parse_hour_ending_timestamp(df: pd.DataFrame) -> pd.Series:
    """Rebuild canonical source timestamp from Date + Time; do not trust DateTime."""
    combined = (
        df["Date"].astype("string").str.strip()
        + " "
        + df["Time"].astype("string").str.strip()
    )
    timestamp = pd.to_datetime(combined, errors="coerce")
    if timestamp.isna().any():
        bad = int(timestamp.isna().sum())
        examples = combined.loc[timestamp.isna()].head(10).tolist()
        raise ValueError(
            f"{bad} Date+Time values cannot be parsed. Examples: {examples}"
        )
    return timestamp


def numeric_clean(series: pd.Series, name: str) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any():
        bad = int(values.isna().sum())
        raise ValueError(f"{name} contains {bad} non-numeric/missing values.")
    return values.astype("float64")


def validate_formal_timeline(df: pd.DataFrame) -> None:
    if len(df) != EXPECTED_HOURS:
        raise ValueError(
            f"Formal case-year contains {len(df):,} rows; expected {EXPECTED_HOURS:,}."
        )

    if df["timestamp_start"].duplicated().any():
        count = int(df["timestamp_start"].duplicated().sum())
        raise ValueError(f"Formal case-year contains {count} duplicate timestamps.")

    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )
    actual = pd.DatetimeIndex(df["timestamp_start"])

    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise ValueError(
            "Formal case-year is not the exact consecutive v7 hourly timeline: "
            f"missing={len(missing)}, extra={len(extra)}."
        )


def classify_data_status(row: pd.Series) -> str:
    if row["load_status"] != "normal":
        return "outage_contaminated"
    if row["pv_status"] in LONG_PV_UNAVAILABLE_STATUSES:
        return "pv_unavailable"
    if row["pv_status"] == "valid":
        return "observed_valid"
    return "other_observed_status"


def build_audit_lines(
    source: pd.DataFrame,
    formal: pd.DataFrame,
    datetime_mismatch_count: int | None,
) -> list[str]:
    load = formal["observed_load_kw"]
    pv = formal["observed_pv_kw"]

    outage_mask = formal["outage_contaminated_flag"]
    long_pv_mask = formal["pv_long_unavailable_flag"]
    normal_load_zero = formal["load_status"].eq("normal") & load.eq(0)

    lines = [
        "NTUST v7 Cleaned Observed Data Audit",
        f"Script version: {SCRIPT_VERSION}",
        "",
        "Source input",
        f"- Rows: {len(source):,}",
        f"- Rebuilt hour-ending range: {source['timestamp_raw_end'].min()} to "
        f"{source['timestamp_raw_end'].max()}",
        "- Canonical source timestamp: rebuilt from Date + Time",
        "- Legacy DateTime column: diagnostic only; never used as canonical time",
    ]

    if datetime_mismatch_count is not None:
        lines.append(
            f"- Legacy DateTime vs rebuilt Date+Time mismatches: "
            f"{datetime_mismatch_count:,}"
        )

    lines.extend(
        [
            "",
            "v7 timestamp convention",
            "- Source electricity timestamp: hour-ending",
            "- Conversion: timestamp_start = timestamp_raw_end - 1 hour",
            f"- Formal interval: [{FORMAL_START}, {FORMAL_END_EXCLUSIVE})",
            f"- Formal rows: {len(formal):,}",
            f"- First timestamp_start: {formal['timestamp_start'].min()}",
            f"- Last timestamp_start: {formal['timestamp_start'].max()}",
            "- Formal 8,760-hour consecutive timeline: PASSED",
            "",
            "Observed Load",
            f"- Missing: {int(load.isna().sum()):,}",
            f"- Negative: {int((load < 0).sum()):,}",
            f"- Zero: {int(load.eq(0).sum()):,}",
            f"- Zero while load_status=normal: {int(normal_load_zero.sum()):,}",
            f"- Min / mean / max kW: {load.min():.3f} / {load.mean():.3f} / {load.max():.3f}",
            "",
            "Observed PV",
            f"- Missing: {int(pv.isna().sum()):,}",
            f"- Negative: {int((pv < 0).sum()):,}",
            f"- Zero: {int(pv.eq(0).sum()):,}",
            f"- Min / mean / max kW: {pv.min():.3f} / {pv.mean():.3f} / {pv.max():.3f}",
            "",
            "Provenance/status",
            f"- Outage-contaminated hours: {int(outage_mask.sum()):,}",
            f"- Long PV-unavailable hours (pre_system/missing_winter): "
            f"{int(long_pv_mask.sum()):,}",
            "- No reconstruction is performed in Script 01.",
            "- Original observed values are preserved even when outage-contaminated.",
            "",
            "load_status counts",
        ]
    )

    for key, value in formal["load_status"].value_counts(dropna=False).items():
        lines.append(f"- {key}: {int(value):,}")

    lines.append("")
    lines.append("pv_status counts")
    for key, value in formal["pv_status"].value_counts(dropna=False).items():
        lines.append(f"- {key}: {int(value):,}")

    lines.append("")
    lines.append("data_status counts")
    for key, value in formal["data_status"].value_counts(dropna=False).items():
        lines.append(f"- {key}: {int(value):,}")

    return lines


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")

        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.audit_dir.mkdir(parents=True, exist_ok=True)

        source = pd.read_csv(args.input)
        require_columns(
            source,
            [
                "Date",
                "Time",
                "Load_kWh",
                "Solar_kWh",
                "event_flag",
                "solar_status",
            ],
        )

        source = source.copy()
        source["timestamp_raw_end"] = parse_hour_ending_timestamp(source)
        source["timestamp_start"] = (
            source["timestamp_raw_end"] - pd.Timedelta(hours=1)
        )

        if source["timestamp_raw_end"].duplicated().any():
            count = int(source["timestamp_raw_end"].duplicated().sum())
            raise ValueError(f"Source contains {count} duplicate Date+Time timestamps.")

        source = source.sort_values("timestamp_raw_end").reset_index(drop=True)

        datetime_mismatch_count: int | None = None
        if "DateTime" in source.columns:
            legacy_datetime = pd.to_datetime(source["DateTime"], errors="coerce")
            comparable = legacy_datetime.notna()
            datetime_mismatch_count = int(
                (
                    legacy_datetime.loc[comparable]
                    != source.loc[comparable, "timestamp_raw_end"]
                ).sum()
            ) + int((~comparable).sum())

        source["observed_load_kwh"] = numeric_clean(
            source["Load_kWh"], "Load_kWh"
        )
        source["observed_pv_kwh"] = numeric_clean(
            source["Solar_kWh"], "Solar_kWh"
        )

        if (source["observed_load_kwh"] < 0).any():
            count = int((source["observed_load_kwh"] < 0).sum())
            raise ValueError(f"Observed Load contains {count} negative values.")

        if (source["observed_pv_kwh"] < 0).any():
            count = int((source["observed_pv_kwh"] < 0).sum())
            raise ValueError(f"Observed PV contains {count} negative values.")

        formal = source.loc[
            (source["timestamp_start"] >= FORMAL_START)
            & (source["timestamp_start"] < FORMAL_END_EXCLUSIVE)
        ].copy()
        formal = formal.sort_values("timestamp_start").reset_index(drop=True)

        validate_formal_timeline(formal)

        # Because Delta t = 1 h, interval energy in kWh is numerically equal
        # to average interval power in kW. Both are retained for provenance.
        formal["observed_load_kw"] = formal["observed_load_kwh"]
        formal["observed_pv_kw"] = formal["observed_pv_kwh"]

        formal["load_status"] = formal["event_flag"].astype("string")
        formal["pv_status"] = formal["solar_status"].astype("string")

        formal["outage_contaminated_flag"] = formal["load_status"].ne("normal")
        formal["pv_long_unavailable_flag"] = formal["pv_status"].isin(
            LONG_PV_UNAVAILABLE_STATUSES
        )
        formal["data_status"] = formal.apply(classify_data_status, axis=1)

        # Downstream compatibility: timestamp always means interval start.
        formal["timestamp"] = formal["timestamp_start"]
        formal["time_index"] = range(len(formal))

        # Regenerate all basic calendar fields from interval-start time.
        formal["year"] = formal["timestamp_start"].dt.year
        formal["month"] = formal["timestamp_start"].dt.month
        formal["day"] = formal["timestamp_start"].dt.day
        formal["hour"] = formal["timestamp_start"].dt.hour
        formal["weekday"] = formal["timestamp_start"].dt.weekday
        formal["is_weekend"] = formal["weekday"].isin([5, 6])

        normal_load_zero = (
            formal["load_status"].eq("normal")
            & formal["observed_load_kw"].eq(0)
        )
        if normal_load_zero.any():
            examples = formal.loc[
                normal_load_zero,
                ["timestamp_start", "observed_load_kw", "load_status"],
            ].head(10)
            raise ValueError(
                "Observed Load contains zero values labelled as normal. "
                "Inspect before proceeding. Examples:\n"
                + examples.to_string(index=False)
            )

        output_columns = [
            "timestamp_raw_end",
            "timestamp_start",
            "timestamp",
            "time_index",
            "observed_load_kwh",
            "observed_load_kw",
            "observed_pv_kwh",
            "observed_pv_kw",
            "load_status",
            "pv_status",
            "data_status",
            "outage_contaminated_flag",
            "pv_long_unavailable_flag",
            "year",
            "month",
            "day",
            "hour",
            "weekday",
            "is_weekend",
        ]
        output = formal[output_columns].copy()

        csv_path = args.output_dir / "ntust_case_year_observed.csv"
        parquet_path = args.output_dir / "ntust_case_year_observed.parquet"
        audit_path = args.audit_dir / "cleaned_observed_audit_v7.txt"
        flagged_path = args.audit_dir / "observed_flagged_intervals_v7.csv"

        output.to_csv(csv_path, index=False, encoding="utf-8-sig")

        parquet_written = False
        parquet_warning: str | None = None
        try:
            output.to_parquet(parquet_path, index=False)
            parquet_written = True
        except (ImportError, ModuleNotFoundError, ValueError) as exc:
            parquet_warning = (
                "Parquet output skipped because no usable parquet engine is "
                f"available: {exc}"
            )

        flagged = output.loc[
            output["outage_contaminated_flag"]
            | output["pv_long_unavailable_flag"]
        ].copy()
        flagged.to_csv(flagged_path, index=False, encoding="utf-8-sig")

        audit_lines = build_audit_lines(
            source=source,
            formal=output,
            datetime_mismatch_count=datetime_mismatch_count,
        )
        audit_path.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

        print("\n".join(audit_lines))
        print()
        print("Outputs:")
        print(f"- {csv_path}")
        if parquet_written:
            print(f"- {parquet_path}")
        elif parquet_warning is not None:
            print(f"- WARNING: {parquet_warning}")
        print(f"- {flagged_path}")
        print(f"- {audit_path}")
        print()
        print(
            "Script 01 completed. No Load/PV reconstruction has been applied. "
            "Use ntust_case_year_observed.* as the input to subsequent v7 "
            "inspection and reconstruction-validation scripts."
        )
        return 0

    except Exception as exc:
        print(f"Script 01 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
