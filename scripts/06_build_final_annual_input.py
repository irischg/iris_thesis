#!/usr/bin/env python3
"""
06_build_final_annual_input.py

NTUST thesis v7.1 — final annual input integration.

Mainline role
-------------
Combine the current v7.1 preprocessing outputs:

    data/processed/load_annual_baseline.*
    data/processed/pv_annual_baseline.*

into one audited 8,760-hour annual input while preserving:
- observed Load/PV exactly;
- planning-baseline Load/PV;
- reconstruction provenance;
- long-unavailable-PV provenance.

This script regenerates calendar / summer / TOU / billing-period tags from the
canonical interval-start timestamp. It does NOT calibrate kappa and does NOT run
EOB, Layer A, Layer B, or any optimization.

Important TOU-calendar guardrail
--------------------------------
The hourly TOU band can be generated from season + clock time, but whether a
calendar date is treated as an ordinary weekday, Saturday, or Taipower
off-peak/holiday day must come from an audited case-year calendar.

Expected optional file:
    data/reference/taipower_tou_day_calendar_case_year_v7_1.csv

Required columns:
    date,tou_day_type

Allowed tou_day_type:
    weekday
    saturday
    offpeak_day

If the audited calendar is absent, Script 06 still performs the full data merge
and data-lineage audit, but the output is explicitly marked:

    conditional_tou_calendar_unverified

and MUST NOT be treated as the final canonical input for EOB / Layer A / Layer B.
A review template is written to results/data_audit/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-final-annual-input-2026-08-17"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760

EXPECTED_LOAD_RECONSTRUCTED_HOURS = 10
EXPECTED_PV_RECONSTRUCTED_HOURS = 10
EXPECTED_LONG_UNAVAILABLE_PV_HOURS = 1463

LOCKED_LOAD_METHOD = "same_weekday_pm6weeks_top1_context_rmse"
LOCKED_PV_METHOD = "cwa_hourly_ghi_ratio_median_leave_target_day_out"
LONG_PV_METHOD = "unavailable_zero_mainline"

ALLOWED_LOAD_METHODS = {"observed", LOCKED_LOAD_METHOD}
ALLOWED_PV_METHODS = {"observed", LOCKED_PV_METHOD, LONG_PV_METHOD}
LONG_PV_STATUSES = {"pre_system", "missing_winter"}
ALLOWED_TOU_DAY_TYPES = {"weekday", "saturday", "offpeak_day"}
ALLOWED_TOU_PERIODS = {"peak", "half", "sat_half", "off"}

REGENERATED_COLUMNS = {
    "time_index",
    "year",
    "month",
    "day",
    "date",
    "hour",
    "weekday",
    "weekday_name",
    "is_weekend",
    "is_summer",
    "season",
    "tou_day_type",
    "tou_period",
    "tou_calendar_source",
    "tou_calendar_verified",
    "billing_usage_period_id",
    "usage_period_start",
    "usage_period_end_exclusive",
    "integration_status",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Build the v7.1 final integrated NTUST annual input."
    )

    parser.add_argument(
        "--load-parquet",
        type=Path,
        default=root / "data" / "processed" / "load_annual_baseline.parquet",
    )
    parser.add_argument(
        "--load-csv",
        type=Path,
        default=root / "data" / "processed" / "load_annual_baseline.csv",
    )
    parser.add_argument(
        "--pv-parquet",
        type=Path,
        default=root / "data" / "processed" / "pv_annual_baseline.parquet",
    )
    parser.add_argument(
        "--pv-csv",
        type=Path,
        default=root / "data" / "processed" / "pv_annual_baseline.csv",
    )
    parser.add_argument(
        "--tou-calendar",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "taipower_tou_day_calendar_case_year_v7_1.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "data" / "processed",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=root / "results" / "data_audit",
    )
    parser.add_argument(
        "--require-audited-tou-calendar",
        action="store_true",
        help=(
            "Fail if the audited Taipower day calendar is absent. "
            "Without this flag, a conditional output and review template "
            "are written instead."
        ),
    )
    parser.add_argument(
        "--write-compat-alias",
        action="store_true",
        help=(
            "When integration_status=passed, also write "
            "annual_input_existing_pv.* as a regenerated compatibility alias."
        ),
    )
    return parser.parse_args()


def read_parquet_or_csv(
    parquet_path: Path,
    csv_path: Path,
    label: str,
) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        f"{label} not found. Expected either:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}"
    )


def write_parquet_if_available(df: pd.DataFrame, path: Path) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def expected_timeline() -> pd.DatetimeIndex:
    return pd.date_range(FORMAL_START, periods=EXPECTED_ROWS, freq="h")


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
    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
    )

    if normalized.isna().any():
        bad = (
            series.loc[normalized.isna()]
            .astype(str)
            .drop_duplicates()
            .tolist()
        )
        raise ValueError(
            f"{label}: cannot interpret boolean values {bad[:10]}."
        )
    return normalized.astype(bool)


def require_columns(
    df: pd.DataFrame,
    required: set[str],
    label: str,
) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{label}: missing required columns {missing}")


def prepare_timestamp(df: pd.DataFrame, label: str) -> pd.DataFrame:
    out = df.copy()

    if "timestamp" not in out.columns:
        if "timestamp_start" not in out.columns:
            raise ValueError(
                f"{label}: missing canonical timestamp/timestamp_start."
            )
        out["timestamp"] = out["timestamp_start"]

    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    if out["timestamp"].isna().any():
        raise ValueError(
            f"{label}: {int(out['timestamp'].isna().sum())} timestamps "
            "could not be parsed."
        )

    # The project stores local Asia/Taipei wall-clock timestamps without
    # timezone offsets. If an offset-aware series appears, remove the timezone
    # only after preserving the represented local clock.
    if out["timestamp"].dt.tz is not None:
        out["timestamp"] = out["timestamp"].dt.tz_localize(None)

    if "timestamp_start" in out.columns:
        ts_start = pd.to_datetime(
            out["timestamp_start"],
            errors="coerce",
        )
        if ts_start.isna().any():
            raise ValueError(
                f"{label}: timestamp_start contains unparsable values."
            )
        if ts_start.dt.tz is not None:
            ts_start = ts_start.dt.tz_localize(None)

        mismatch = int((ts_start != out["timestamp"]).sum())
        if mismatch:
            raise ValueError(
                f"{label}: timestamp_start differs from timestamp in "
                f"{mismatch} rows."
            )

    return out.sort_values("timestamp").reset_index(drop=True)


def validate_timeline(df: pd.DataFrame, label: str) -> None:
    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"{label}: rows={len(df):,}; expected {EXPECTED_ROWS:,}."
        )

    duplicates = int(df["timestamp"].duplicated().sum())
    if duplicates:
        raise ValueError(
            f"{label}: {duplicates} duplicate timestamps."
        )

    actual = pd.DatetimeIndex(df["timestamp"])
    expected = expected_timeline()

    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise ValueError(
            f"{label}: not the exact formal v7.1 timeline. "
            f"missing={len(missing)}, extra={len(extra)}, "
            f"first={actual.min()}, last={actual.max()}."
        )


def assert_series_equal_exact(
    left: pd.Series,
    right: pd.Series,
    label: str,
) -> None:
    try:
        pd.testing.assert_series_equal(
            left.reset_index(drop=True),
            right.reset_index(drop=True),
            check_names=False,
            check_dtype=False,
            check_exact=True,
        )
    except AssertionError as exc:
        raise ValueError(
            f"Equality check failed: {label}"
        ) from exc


def assert_shared_immutable_columns(
    load: pd.DataFrame,
    pv: pd.DataFrame,
) -> list[str]:
    candidates = [
        "timestamp_raw_end",
        "timestamp_start",
        "timestamp",
        "observed_load_kw",
        "observed_pv_kw",
        "load_status",
        "pv_status",
        "event_flag",
        "data_status",
        "outage_contaminated_flag",
        "source_row_index",
    ]

    checked: list[str] = []

    for column in candidates:
        if column not in load.columns or column not in pv.columns:
            continue

        if column.startswith("timestamp"):
            left = pd.to_datetime(load[column], errors="coerce")
            right = pd.to_datetime(pv[column], errors="coerce")
        elif column == "outage_contaminated_flag":
            left = normalize_bool(load[column], f"Load {column}")
            right = normalize_bool(pv[column], f"PV {column}")
        else:
            left = load[column]
            right = pv[column]

        assert_series_equal_exact(left, right, column)
        checked.append(column)

    return checked


def merge_current_v7_outputs(
    load: pd.DataFrame,
    pv: pd.DataFrame,
) -> pd.DataFrame:
    """
    Script 03 controls Load-baseline fields.
    Script 05 controls PV-baseline and weather fields.
    Both descend from Script 01; immutable overlap is checked beforehand.
    """
    out = load.copy()

    for column in REGENERATED_COLUMNS:
        if column in out.columns:
            out = out.drop(columns=column)

    pv_authoritative = [
        "observed_pv_kwh",
        "observed_pv_kw",
        "pv_available_kwh",
        "pv_available_kw",
        "pv_status",
        "pv_reconstructed",
        "pv_reconstruction_method",
        "pv_long_unavailable_assumption",
        "pv_cwa_model",
        "ghi_kwh_m2",
        "air_temperature_c",
    ]

    for column in pv_authoritative:
        if column in pv.columns:
            out[column] = pv[column].reset_index(drop=True)

    # Keep extra Script-05 provenance that is not a regenerated calendar field.
    for column in pv.columns:
        if column in {"timestamp", *REGENERATED_COLUMNS}:
            continue
        if column not in out.columns:
            out[column] = pv[column].reset_index(drop=True)

    for column in [
        "outage_contaminated_flag",
        "load_reconstructed",
        "pv_reconstructed",
        "pv_long_unavailable_assumption",
    ]:
        if column in out.columns:
            out[column] = normalize_bool(out[column], column)

    return out


def audit_preprocessing_lineage(
    df: pd.DataFrame,
) -> dict[str, object]:
    required = {
        "timestamp",
        "observed_load_kw",
        "baseline_load_kw",
        "observed_pv_kw",
        "pv_available_kw",
        "load_status",
        "pv_status",
        "outage_contaminated_flag",
        "load_reconstructed",
        "load_reconstruction_method",
        "pv_reconstructed",
        "pv_reconstruction_method",
        "pv_long_unavailable_assumption",
    }
    require_columns(df, required, "Integrated annual input")

    for column in [
        "observed_load_kw",
        "baseline_load_kw",
        "observed_pv_kw",
        "pv_available_kw",
    ]:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.isna().any():
            raise ValueError(
                f"{column}: {int(values.isna().sum())} missing/non-numeric."
            )
        df[column] = values.astype("float64")

    if (df["observed_load_kw"] < 0).any():
        raise ValueError("observed_load_kw contains negative values.")
    if (df["baseline_load_kw"] <= 0).any():
        raise ValueError("baseline_load_kw contains non-positive values.")
    if (df["observed_pv_kw"] < 0).any():
        raise ValueError("observed_pv_kw contains negative values.")
    if (df["pv_available_kw"] < 0).any():
        raise ValueError("pv_available_kw contains negative values.")

    load_reconstructed = int(df["load_reconstructed"].sum())
    pv_reconstructed = int(df["pv_reconstructed"].sum())
    pv_long = int(df["pv_long_unavailable_assumption"].sum())

    if load_reconstructed != EXPECTED_LOAD_RECONSTRUCTED_HOURS:
        raise ValueError(
            f"Load reconstructed hours={load_reconstructed}; "
            f"expected {EXPECTED_LOAD_RECONSTRUCTED_HOURS}."
        )

    if pv_reconstructed != EXPECTED_PV_RECONSTRUCTED_HOURS:
        raise ValueError(
            f"PV reconstructed hours={pv_reconstructed}; "
            f"expected {EXPECTED_PV_RECONSTRUCTED_HOURS}."
        )

    if pv_long != EXPECTED_LONG_UNAVAILABLE_PV_HOURS:
        raise ValueError(
            f"Long-unavailable PV hours={pv_long}; "
            f"expected {EXPECTED_LONG_UNAVAILABLE_PV_HOURS}."
        )

    load_methods = set(
        df["load_reconstruction_method"].astype(str).unique()
    )
    bad_load_methods = sorted(load_methods - ALLOWED_LOAD_METHODS)
    if bad_load_methods:
        raise ValueError(
            "Unexpected Load reconstruction methods "
            f"(possible legacy contamination): {bad_load_methods}"
        )

    pv_methods = set(
        df["pv_reconstruction_method"].astype(str).unique()
    )
    bad_pv_methods = sorted(pv_methods - ALLOWED_PV_METHODS)
    if bad_pv_methods:
        raise ValueError(
            "Unexpected PV reconstruction methods "
            f"(possible legacy contamination): {bad_pv_methods}"
        )

    outage_mask = df["outage_contaminated_flag"]

    normal_load_diff = np.abs(
        df.loc[~outage_mask, "baseline_load_kw"].to_numpy(dtype=float)
        - df.loc[~outage_mask, "observed_load_kw"].to_numpy(dtype=float)
    )
    max_normal_load_diff = (
        float(normal_load_diff.max()) if len(normal_load_diff) else 0.0
    )
    if max_normal_load_diff > 0.0:
        raise ValueError(
            "baseline_load_kw changed outside outage-contaminated hours."
        )

    long_status_mask = (
        df["pv_status"].astype(str).isin(LONG_PV_STATUSES)
    )
    if int(long_status_mask.sum()) != pv_long:
        raise ValueError(
            "pv_status count for pre_system/missing_winter does not match "
            "pv_long_unavailable_assumption."
        )

    if not df.loc[long_status_mask, "pv_available_kw"].eq(0.0).all():
        raise ValueError(
            "Long-unavailable PV intervals are not all zero in mainline."
        )

    unchanged_pv_mask = ~outage_mask & ~long_status_mask
    normal_pv_diff = np.abs(
        df.loc[unchanged_pv_mask, "pv_available_kw"].to_numpy(dtype=float)
        - df.loc[unchanged_pv_mask, "observed_pv_kw"].to_numpy(dtype=float)
    )
    max_normal_pv_diff = (
        float(normal_pv_diff.max()) if len(normal_pv_diff) else 0.0
    )
    if max_normal_pv_diff > 0.0:
        raise ValueError(
            "pv_available_kw changed outside short-outage or "
            "long-unavailable intervals."
        )

    # Historical billing-calibration boundary: observed only.
    df["observed_net_load_kw"] = (
        df["observed_load_kw"] - df["observed_pv_kw"]
    )

    # Planning-side quantities: counterfactual baseline + availability.
    df["residual_load_kw"] = (
        df["baseline_load_kw"] - df["pv_available_kw"]
    )
    df["grid_demand_before_bess_kw"] = (
        df["residual_load_kw"].clip(lower=0.0)
    )
    df["pv_surplus_before_bess_kw"] = (
        (-df["residual_load_kw"]).clip(lower=0.0)
    )

    return {
        "load_reconstructed_hours": load_reconstructed,
        "pv_reconstructed_hours": pv_reconstructed,
        "long_unavailable_pv_hours": pv_long,
        "load_methods": sorted(load_methods),
        "pv_methods": sorted(pv_methods),
        "max_normal_load_difference_kw": max_normal_load_diff,
        "max_normal_pv_difference_kw": max_normal_pv_diff,
    }


def summer_flag(timestamp: pd.Series) -> pd.Series:
    month_day = timestamp.dt.month * 100 + timestamp.dt.day
    return month_day.between(516, 1015)


def provisional_tou_day_calendar() -> pd.DataFrame:
    dates = pd.date_range(
        FORMAL_START.normalize(),
        FORMAL_END_EXCLUSIVE.normalize() - pd.Timedelta(days=1),
        freq="D",
    )
    frame = pd.DataFrame({"date": dates})
    weekday = frame["date"].dt.weekday

    frame["tou_day_type"] = np.select(
        [weekday.eq(5), weekday.eq(6)],
        ["saturday", "offpeak_day"],
        default="weekday",
    )
    frame["source_note"] = (
        "PROVISIONAL weekday/Saturday/Sunday classification only; "
        "Taipower holiday/off-peak-day overrides not audited"
    )
    return frame


def write_tou_calendar_template(
    provisional: pd.DataFrame,
    audit_dir: Path,
) -> Path:
    template = provisional.rename(
        columns={"tou_day_type": "provisional_day_type"}
    ).copy()
    template["tou_day_type"] = ""
    template["source_note"] = ""
    template["review_note"] = (
        "Fill tou_day_type with weekday/saturday/offpeak_day using the "
        "audited case-year Taipower TOU calendar."
    )

    path = (
        audit_dir
        / "taipower_tou_day_calendar_template_v7_1.csv"
    )
    template[
        [
            "date",
            "provisional_day_type",
            "tou_day_type",
            "source_note",
            "review_note",
        ]
    ].to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d",
    )
    return path


def load_tou_day_calendar(
    path: Path,
    audit_dir: Path,
) -> tuple[pd.DataFrame, bool, str, Path | None]:
    provisional = provisional_tou_day_calendar()

    if not path.exists():
        template_path = write_tou_calendar_template(
            provisional,
            audit_dir,
        )
        return (
            provisional,
            False,
            "provisional_weekday_rule_no_holiday_override",
            template_path,
        )

    calendar = pd.read_csv(path)
    require_columns(
        calendar,
        {"date", "tou_day_type"},
        "Audited TOU day calendar",
    )

    calendar["date"] = pd.to_datetime(
        calendar["date"],
        errors="coerce",
    ).dt.normalize()
    if calendar["date"].isna().any():
        raise ValueError(
            "Audited TOU day calendar contains unparsable dates."
        )

    if calendar["date"].duplicated().any():
        raise ValueError(
            "Audited TOU day calendar contains duplicate dates."
        )

    calendar["tou_day_type"] = (
        calendar["tou_day_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    invalid = sorted(
        set(calendar["tou_day_type"]) - ALLOWED_TOU_DAY_TYPES
    )
    if invalid:
        raise ValueError(
            f"Invalid tou_day_type values: {invalid}. "
            f"Allowed={sorted(ALLOWED_TOU_DAY_TYPES)}"
        )

    expected_dates = pd.DatetimeIndex(provisional["date"])
    actual_dates = pd.DatetimeIndex(
        calendar["date"].sort_values()
    )
    missing = expected_dates.difference(actual_dates)
    extra = actual_dates.difference(expected_dates)

    if len(missing) or len(extra):
        raise ValueError(
            "Audited TOU day calendar does not cover exactly the case year. "
            f"missing_dates={len(missing)}, extra_dates={len(extra)}."
        )

    if "source_note" not in calendar.columns:
        calendar["source_note"] = "audited case-year Taipower TOU calendar"

    calendar = (
        calendar[
            ["date", "tou_day_type", "source_note"]
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )

    return calendar, True, f"audited_calendar:{path}", None


def assign_tou_period(
    hour: int,
    is_summer: bool,
    day_type: str,
) -> str:
    """
    High-voltage three-period fixed time bands.

    Summer weekday:
      off 00-09; half 09-16; peak 16-22; half 22-24.
    Summer Saturday:
      off 00-09; sat_half 09-24.

    Non-summer weekday:
      off 00-06 and 11-14; half otherwise.
    Non-summer Saturday:
      off 00-06 and 11-14; sat_half otherwise.

    offpeak_day:
      off all day.
    """
    if day_type == "offpeak_day":
        return "off"

    if is_summer:
        if day_type == "saturday":
            return "off" if hour < 9 else "sat_half"

        if hour < 9:
            return "off"
        if hour < 16:
            return "half"
        if hour < 22:
            return "peak"
        return "half"

    # Non-summer
    in_off = (hour < 6) or (11 <= hour < 14)
    if day_type == "saturday":
        return "off" if in_off else "sat_half"
    return "off" if in_off else "half"


def regenerate_calendar_tags(
    df: pd.DataFrame,
    day_calendar: pd.DataFrame,
    calendar_verified: bool,
    calendar_source: str,
) -> pd.DataFrame:
    out = df.copy()

    for column in REGENERATED_COLUMNS:
        if column in out.columns:
            out = out.drop(columns=column)

    out["time_index"] = np.arange(len(out), dtype=int)
    out["year"] = out["timestamp"].dt.year
    out["month"] = out["timestamp"].dt.month
    out["day"] = out["timestamp"].dt.day
    out["date"] = out["timestamp"].dt.normalize()
    out["hour"] = out["timestamp"].dt.hour
    out["weekday"] = out["timestamp"].dt.weekday
    out["weekday_name"] = out["timestamp"].dt.day_name()
    out["is_weekend"] = out["weekday"].ge(5)

    out["is_summer"] = summer_flag(out["timestamp"])
    out["season"] = np.where(
        out["is_summer"],
        "summer",
        "non_summer",
    )

    lookup = day_calendar.set_index("date")["tou_day_type"]
    out["tou_day_type"] = out["date"].map(lookup)

    if out["tou_day_type"].isna().any():
        raise ValueError(
            f"TOU day calendar left "
            f"{int(out['tou_day_type'].isna().sum())} hourly rows unmatched."
        )

    out["tou_period"] = [
        assign_tou_period(
            int(hour),
            bool(is_summer),
            str(day_type),
        )
        for hour, is_summer, day_type in zip(
            out["hour"],
            out["is_summer"],
            out["tou_day_type"],
        )
    ]

    invalid = sorted(
        set(out["tou_period"]) - ALLOWED_TOU_PERIODS
    )
    if invalid:
        raise ValueError(f"Invalid TOU periods generated: {invalid}")

    out["tou_calendar_source"] = calendar_source
    out["tou_calendar_verified"] = calendar_verified

    # Usage-period group is the electricity-consumption month, not the
    # bill-title month. The later billing registry stores actual bill metadata.
    month_period = out["timestamp"].dt.to_period("M")
    out["billing_usage_period_id"] = month_period.astype(str)
    out["usage_period_start"] = month_period.dt.start_time
    out["usage_period_end_exclusive"] = (
        month_period.dt.end_time
        + pd.Timedelta(nanoseconds=1)
    )

    return out


def final_column_order(df: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "timestamp_raw_end",
        "timestamp_start",
        "timestamp",
        "time_index",
        "year",
        "month",
        "day",
        "date",
        "hour",
        "weekday",
        "weekday_name",
        "is_weekend",
        "is_summer",
        "season",
        "tou_day_type",
        "tou_period",
        "tou_calendar_source",
        "tou_calendar_verified",
        "billing_usage_period_id",
        "usage_period_start",
        "usage_period_end_exclusive",
        "integration_status",
        "observed_load_kwh",
        "observed_load_kw",
        "baseline_load_kwh",
        "baseline_load_kw",
        "load_status",
        "event_flag",
        "outage_contaminated_flag",
        "load_reconstructed",
        "load_reconstruction_method",
        "load_donor_timestamp",
        "load_donor_week_offset",
        "load_donor_context_rmse_kw",
        "observed_pv_kwh",
        "observed_pv_kw",
        "pv_available_kwh",
        "pv_available_kw",
        "pv_status",
        "pv_reconstructed",
        "pv_reconstruction_method",
        "pv_long_unavailable_assumption",
        "pv_cwa_model",
        "ghi_kwh_m2",
        "air_temperature_c",
        "observed_net_load_kw",
        "residual_load_kw",
        "grid_demand_before_bess_kw",
        "pv_surplus_before_bess_kw",
        "data_status",
        "source_row_index",
    ]

    first = [c for c in preferred if c in df.columns]
    rest = [c for c in df.columns if c not in first]
    return df[first + rest].copy()


def build_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    descriptions = {
        "timestamp_raw_end":
            "Original source hour-ending electricity timestamp, if retained.",
        "timestamp_start":
            "Canonical interval-start timestamp inherited from Script 01.",
        "timestamp":
            "Canonical v7.1 interval-start model timestamp.",
        "time_index":
            "Zero-based hourly model index 0..8759.",
        "observed_load_kw":
            "Immutable observed campus Load.",
        "baseline_load_kw":
            "Planning Load after locked 10-hour short-gap reconstruction.",
        "observed_pv_kw":
            "Immutable observed PV.",
        "pv_available_kw":
            "Planning PV availability after locked short-gap reconstruction "
            "and long-unavailable zero assignment.",
        "load_status":
            "Observed Load status/provenance.",
        "pv_status":
            "Observed PV status: valid/pre_system/missing_winter.",
        "outage_contaminated_flag":
            "True for historical outage-contaminated short-gap hours.",
        "load_reconstructed":
            "True only where baseline Load was reconstructed.",
        "load_reconstruction_method":
            "Load reconstruction method label.",
        "load_donor_timestamp":
            "Selected donor timestamp for reconstructed Load rows.",
        "load_donor_week_offset":
            "Selected donor week offset.",
        "load_donor_context_rmse_kw":
            "Same-day outside-gap RMSE used to select Load donor.",
        "pv_reconstructed":
            "True only where short-gap PV was reconstructed.",
        "pv_reconstruction_method":
            "PV reconstruction / availability method label.",
        "pv_long_unavailable_assumption":
            "True for pre_system/missing_winter hours conservatively assigned "
            "zero mainline PV availability.",
        "pv_cwa_model":
            "CWA short-gap PV model label where applicable.",
        "ghi_kwh_m2":
            "Hourly CWA GHI retained from Script 05.",
        "air_temperature_c":
            "Hourly CWA air temperature retained from Script 05.",
        "is_summer":
            "High-voltage summer flag: May 16 through October 15.",
        "tou_day_type":
            "weekday/saturday/offpeak_day tariff-day class.",
        "tou_period":
            "peak/half/sat_half/off hourly tariff class.",
        "tou_calendar_verified":
            "True only if an audited case-year TOU day calendar was supplied.",
        "billing_usage_period_id":
            "Electricity-usage month YYYY-MM; not bill-title month.",
        "observed_net_load_kw":
            "Observed Load minus observed PV; later kappa calibration boundary.",
        "residual_load_kw":
            "Planning baseline Load minus planning PV availability.",
        "grid_demand_before_bess_kw":
            "Positive planning residual demand before BESS.",
        "pv_surplus_before_bess_kw":
            "Positive planning PV surplus before BESS.",
        "integration_status":
            "passed or conditional_tou_calendar_unverified.",
    }

    source_map = {
        "observed_load_kw": "Script 01 -> Script 03",
        "baseline_load_kw": "Script 03",
        "observed_pv_kw": "Script 01 -> Script 05",
        "pv_available_kw": "Script 05",
        "ghi_kwh_m2": "Script 05 / CWA",
        "air_temperature_c": "Script 05 / CWA",
        "tou_period": "Script 06 regenerated",
        "observed_net_load_kw": "Script 06 derived from observed columns",
        "residual_load_kw": "Script 06 derived from planning columns",
    }

    rows = []
    for column in df.columns:
        rows.append(
            {
                "column": column,
                "dtype": str(df[column].dtype),
                "description": descriptions.get(
                    column,
                    "Preserved upstream provenance or Script-06 derived field.",
                ),
                "source": source_map.get(
                    column,
                    "upstream-preserved or Script 06 derived",
                ),
            }
        )
    return pd.DataFrame(rows)


def flagged_intervals(df: pd.DataFrame) -> pd.DataFrame:
    flag = (
        df["outage_contaminated_flag"]
        | df["load_reconstructed"]
        | df["pv_reconstructed"]
        | df["pv_long_unavailable_assumption"]
    )

    wanted = [
        "timestamp",
        "observed_load_kw",
        "baseline_load_kw",
        "load_status",
        "load_reconstructed",
        "load_reconstruction_method",
        "observed_pv_kw",
        "pv_available_kw",
        "pv_status",
        "pv_reconstructed",
        "pv_reconstruction_method",
        "pv_long_unavailable_assumption",
        "ghi_kwh_m2",
        "tou_day_type",
        "tou_period",
        "billing_usage_period_id",
        "integration_status",
    ]
    columns = [c for c in wanted if c in df.columns]
    return df.loc[flag, columns].copy()


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.audit_dir.mkdir(parents=True, exist_ok=True)

        load_raw, load_path = read_parquet_or_csv(
            args.load_parquet,
            args.load_csv,
            "Load baseline",
        )
        pv_raw, pv_path = read_parquet_or_csv(
            args.pv_parquet,
            args.pv_csv,
            "PV baseline",
        )

        load = prepare_timestamp(load_raw, "Load baseline")
        pv = prepare_timestamp(pv_raw, "PV baseline")

        validate_timeline(load, "Load baseline")
        validate_timeline(pv, "PV baseline")
        assert_series_equal_exact(
            load["timestamp"],
            pv["timestamp"],
            "Load/PV canonical timestamps",
        )

        shared_checked = assert_shared_immutable_columns(load, pv)

        annual = merge_current_v7_outputs(load, pv)
        lineage = audit_preprocessing_lineage(annual)

        (
            day_calendar,
            calendar_verified,
            calendar_source,
            calendar_template_path,
        ) = load_tou_day_calendar(
            args.tou_calendar,
            args.audit_dir,
        )

        if args.require_audited_tou_calendar and not calendar_verified:
            raise FileNotFoundError(
                "Audited Taipower TOU day calendar is required but missing: "
                f"{args.tou_calendar}. Review template: "
                f"{calendar_template_path}"
            )

        annual = regenerate_calendar_tags(
            annual,
            day_calendar,
            calendar_verified,
            calendar_source,
        )

        integration_status = (
            "passed"
            if calendar_verified
            else "conditional_tou_calendar_unverified"
        )
        annual["integration_status"] = integration_status

        # 1-hour interval power/energy aliases are numerically identical.
        annual["observed_load_kwh"] = annual["observed_load_kw"]
        annual["baseline_load_kwh"] = annual["baseline_load_kw"]
        annual["observed_pv_kwh"] = annual["observed_pv_kw"]
        annual["pv_available_kwh"] = annual["pv_available_kw"]

        validate_timeline(annual, "Integrated annual input")

        # Final equality against authoritative current v7.1 component outputs.
        assert_series_equal_exact(
            annual["observed_load_kw"],
            load["observed_load_kw"],
            "final observed_load_kw vs Script 03",
        )
        assert_series_equal_exact(
            annual["baseline_load_kw"],
            load["baseline_load_kw"],
            "final baseline_load_kw vs Script 03",
        )
        assert_series_equal_exact(
            annual["observed_pv_kw"],
            pv["observed_pv_kw"],
            "final observed_pv_kw vs Script 05",
        )
        assert_series_equal_exact(
            annual["pv_available_kw"],
            pv["pv_available_kw"],
            "final pv_available_kw vs Script 05",
        )

        annual = final_column_order(annual)

        csv_path = args.output_dir / "annual_input_v7_1.csv"
        parquet_path = args.output_dir / "annual_input_v7_1.parquet"
        dictionary_path = (
            args.audit_dir
            / "annual_input_v7_1_data_dictionary.csv"
        )
        flagged_path = (
            args.audit_dir
            / "annual_input_v7_1_flagged_intervals.csv"
        )
        audit_path = (
            args.audit_dir
            / "annual_input_v7_1_integration_audit.txt"
        )
        tou_count_path = (
            args.audit_dir
            / "annual_input_v7_1_tou_hour_counts.csv"
        )

        annual.to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig",
        )
        parquet_written = write_parquet_if_available(
            annual,
            parquet_path,
        )

        build_data_dictionary(annual).to_csv(
            dictionary_path,
            index=False,
            encoding="utf-8-sig",
        )
        flagged_intervals(annual).to_csv(
            flagged_path,
            index=False,
            encoding="utf-8-sig",
        )

        tou_counts = (
            annual.groupby(
                ["season", "tou_day_type", "tou_period"],
                observed=True,
            )
            .size()
            .rename("hours")
            .reset_index()
        )
        tou_counts.to_csv(
            tou_count_path,
            index=False,
            encoding="utf-8-sig",
        )

        observed_load_mwh = (
            float(annual["observed_load_kw"].sum()) / 1000.0
        )
        baseline_load_mwh = (
            float(annual["baseline_load_kw"].sum()) / 1000.0
        )
        observed_pv_mwh = (
            float(annual["observed_pv_kw"].sum()) / 1000.0
        )
        available_pv_mwh = (
            float(annual["pv_available_kw"].sum()) / 1000.0
        )

        parquet_summary = (
            str(parquet_path)
            if parquet_written
            else "not written (pyarrow/fastparquet unavailable)"
        )

        lines = [
            "NTUST v7.1 Final Annual Input Integration Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Inputs",
            f"- Load baseline: {load_path}",
            f"- PV baseline: {pv_path}",
            f"- TOU calendar requested: {args.tou_calendar}",
            f"- TOU calendar source used: {calendar_source}",
            f"- TOU calendar verified: {calendar_verified}",
            "",
            "Formal timeline",
            f"- Rows: {len(annual):,}",
            f"- Start: {annual['timestamp'].min()}",
            f"- End: {annual['timestamp'].max()}",
            f"- End-exclusive boundary: {FORMAL_END_EXCLUSIVE}",
            "- Exact 8,760 consecutive interval-start hours: PASSED",
            "",
            "Cross-input equality",
            f"- Shared immutable columns checked: {', '.join(shared_checked)}",
            "- observed_load_kw preserved: PASSED",
            "- baseline_load_kw preserved from Script 03: PASSED",
            "- observed_pv_kw preserved: PASSED",
            "- pv_available_kw preserved from Script 05: PASSED",
            "",
            "Preprocessing lineage",
            f"- Load reconstructed hours: "
            f"{lineage['load_reconstructed_hours']}",
            f"- PV short-gap reconstructed hours: "
            f"{lineage['pv_reconstructed_hours']}",
            f"- Long-unavailable PV zero-assumption hours: "
            f"{lineage['long_unavailable_pv_hours']}",
            f"- Load methods: {lineage['load_methods']}",
            f"- PV methods: {lineage['pv_methods']}",
            "- Unexpected legacy method labels: NONE",
            f"- Max normal-hour Load baseline difference: "
            f"{lineage['max_normal_load_difference_kw']:.12f} kW",
            f"- Max normal-hour PV availability difference: "
            f"{lineage['max_normal_pv_difference_kw']:.12f} kW",
            "",
            "Annual energy diagnostics",
            f"- Observed Load: {observed_load_mwh:.3f} MWh",
            f"- Planning baseline Load: {baseline_load_mwh:.3f} MWh",
            f"- Observed PV: {observed_pv_mwh:.3f} MWh",
            f"- Planning PV availability: {available_pv_mwh:.3f} MWh",
            "",
            "Calendar / billing tags",
            "- Summer rule: May 16 through October 15 inclusive",
            "- billing_usage_period_id uses usage month YYYY-MM, "
            "not bill-title month",
            "- TOU labels regenerated from interval-start timestamps",
            "- TOU classes: peak / half / sat_half / off",
            "",
            "Integration gate",
            f"- integration_status: {integration_status}",
        ]

        if calendar_verified:
            lines.extend(
                [
                    "- Final Script-06 integration gate: PASSED",
                    "- This artifact can be used by the next v7.1 "
                    "billing-calibration gate.",
                ]
            )
        else:
            lines.extend(
                [
                    "- Final Script-06 integration gate: CONDITIONAL",
                    "- Data merge / chronology / provenance audits passed.",
                    "- Audited Taipower holiday/off-peak-day calendar is "
                    "still missing.",
                    "- Do NOT use this conditional file for final EOB, "
                    "Layer A, or Layer B.",
                    f"- TOU calendar review template: "
                    f"{calendar_template_path}",
                ]
            )

        lines.extend(
            [
                "",
                "Outputs",
                f"- CSV: {csv_path}",
                f"- Parquet: {parquet_summary}",
                f"- Data dictionary: {dictionary_path}",
                f"- Flagged intervals: {flagged_path}",
                f"- TOU hour counts: {tou_count_path}",
                f"- Audit summary: {audit_path}",
            ]
        )

        audit_path.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )

        if args.write_compat_alias:
            if not calendar_verified:
                print(
                    "Compatibility alias NOT written because "
                    "integration_status is conditional.",
                    file=sys.stderr,
                )
            else:
                alias_csv = (
                    args.output_dir / "annual_input_existing_pv.csv"
                )
                alias_parquet = (
                    args.output_dir / "annual_input_existing_pv.parquet"
                )
                annual.to_csv(
                    alias_csv,
                    index=False,
                    encoding="utf-8-sig",
                )
                write_parquet_if_available(
                    annual,
                    alias_parquet,
                )
                lines.append("")
                lines.append(
                    f"- Regenerated compatibility alias: {alias_csv}"
                )
                audit_path.write_text(
                    "\n".join(lines),
                    encoding="utf-8-sig",
                )

        print("\n".join(lines))
        print("")
        print(
            "Script 06 completed. No kappa calibration or optimization "
            "was performed."
        )
        return 0

    except Exception as exc:
        print(f"Script 06 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
