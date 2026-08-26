#!/usr/bin/env python3
"""
14b_build_transition_period_settlement_interface.py

NTUST thesis v7.2 — transition-period seasonal settlement preflight.

Purpose
-------
Prepare the tariff-season / billing-period interface required by the later EOB
and Layer A models without running any optimization and without inventing an
unsupported mixed-season positive-overcontract rule.

This script sits downstream of Scripts 06, 13b, 13c, and 14a. It:

1) validates the canonical 8,760-hour case-year timeline and audited TOU
   calendar from Script 06;
2) independently re-checks the official high-voltage summer boundary
   (May 16 through October 15) against every hourly season tag;
3) validates that the production tariff registry preserves the official
   season-specific basic-charge rates and over-contract metadata
   (10% threshold, 2x/3x, peak>half>sat_half>off, non-duplication);
4) validates that Script 14a produced a constant-NTD-2023 optimization tariff
   and a READY_FOR_EOB_OBJECTIVE_WIRING economic interface;
5) identifies pure-season versus mixed-season billing usage periods directly
   from the hourly calendar (expected mixed-season periods: 2025-05, 2025-10);
6) builds a solver-facing SEASONAL settlement matrix for every billing usage
   period, season, and applicable TOU/contract-period demand class;
7) preserves the distinction between:
      - season-specific tariff applicability (supported), and
      - how positive over-contract charges from two seasonal sub-periods are
        finally aggregated into one mixed-season bill (not explicitly located
        in the currently retained official evidence);
8) writes a machine-readable interface plus JSON/TXT audit artifacts.

Important evidence boundary
---------------------------
The production tariff coefficients come from the audited Script-13b registry,
not from NTUST bills. Script 13c is used as an upstream implementation check:
pure-season billing components reproduce observed bills, while May/October
positive over-contract settlement remains unidentifiable because the available
transition-month observations have zero raw overage.

The official Taipower public explanation supplied during the v7.2 audit states
that when a billing interval crosses different tariff-applicability periods,
energy consumption (kWh) is allocated by the applicable periods. That source is
retained here as provenance for date-sensitive tariff applicability, but this
script DOES NOT extend that kWh statement into an unsupported universal rule for
positive over-contract aggregation.

Official public reference reviewed for this gate:
https://www.taipower.com.tw/2289/2363/2388/2389/10732/normalPost

This script deliberately DOES NOT:
- run Gurobi or solve EOB / Layer A;
- re-run full monthly bill-cost regression;
- derive tariff coefficients from bills;
- hard-code a 50/50 positive-overcontract rule;
- hard-code a summer-only or non-summer-only mixed-period overcontract rule;
- set an unresolved tariff coefficient to zero and call it an official rate;
- change the case-validated May/October regular-basic treatment frozen upstream;
- change the 13b/14a tariff files.

Downstream requirement
----------------------
The EOB / Layer A billing engine must use this script's seasonal partition and
season-specific rates. If a solved design creates positive over-contract demand
inside a mixed-season billing period, the run must surface that condition. It
must not silently label an unverified cross-season aggregation rule as official.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-transition-period-seasonal-settlement-preflight-2026-08-26"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760
EXPECTED_USAGE_PERIODS = [
    "2024-11",
    "2024-12",
    "2025-01",
    "2025-02",
    "2025-03",
    "2025-04",
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
]
EXPECTED_TRANSITION_PERIODS = ["2025-05", "2025-10"]

SUMMER_START_MMDD = (5, 16)
SUMMER_END_MMDD = (10, 15)

TOU_PERIODS = ["peak", "half", "sat_half", "off"]
CONTRACT_PERIOD_BY_TOU = {
    "peak": "regular",
    "half": "half",
    "sat_half": "sat_half",
    "off": "off",
}
APPLICABLE_OVERCONTRACT_PERIODS = {
    "summer": ["peak", "half", "sat_half", "off"],
    "non_summer": ["half", "sat_half", "off"],
}

EXPECTED_OVERCONTRACT = {
    "tier1_threshold_fraction": 0.10,
    "tier1_multiplier": 2.0,
    "tier2_multiplier": 3.0,
    "period_order": "peak>half>sat_half>off",
    "non_duplication": True,
}

TAIPOWER_CROSS_PERIOD_PUBLIC_REFERENCE = (
    "https://www.taipower.com.tw/2289/2363/2388/2389/10732/normalPost"
)
TAIPOWER_CROSS_PERIOD_REFERENCE_SCOPE = (
    "Official Taipower public explanation of date-sensitive tariff applicability "
    "when a billing interval crosses different tariff-applicability periods; "
    "the published example expressly addresses allocation of electricity "
    "consumption (kWh), not a universal mixed-season positive-overcontract "
    "aggregation formula."
)

RAW_TARIFF_REQUIRED_COLUMNS = {
    "parameter_id",
    "parameter_group",
    "season",
    "tou_period",
    "contract_period",
    "value_numeric",
    "value_text",
    "unit",
    "applicable",
    "source_file",
    "source_role",
    "mainline_or_legacy",
}

NORMALIZED_TARIFF_REQUIRED_COLUMNS = {
    "parameter_id",
    "parameter_group",
    "season",
    "tou_period",
    "contract_period",
    "applicable",
    "usage_year",
    "nominal_value",
    "nominal_unit",
    "value_constant_ntd2023",
    "optimization_unit",
    "optimization_currency",
    "optimization_currency_base_year",
    "raw_tariff_source_file",
    "raw_tariff_source_role",
}

ANNUAL_REQUIRED_COLUMNS = {
    "timestamp",
    "is_summer",
    "season",
    "tou_period",
    "tou_calendar_verified",
    "billing_usage_period_id",
    "integration_status",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description=(
            "Build and audit the NTUST v7.2 transition-period seasonal "
            "settlement interface."
        )
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
        "--raw-tariff-registry",
        type=Path,
        default=root / "data" / "reference" / "taipower_tariff_registry_v7_1.csv",
    )
    parser.add_argument(
        "--normalized-tariff-registry",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "taipower_tariff_optimization_ntd2023_v7_2.csv"
        ),
    )
    parser.add_argument(
        "--economic-interface-14a",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "production_economic_interface_v7_2.json"
        ),
    )
    parser.add_argument(
        "--bill-audit-13c",
        type=Path,
        default=(
            root
            / "results"
            / "billing_audit"
            / "taipower_core_bill_regression_audit_v7_1.json"
        ),
    )
    parser.add_argument(
        "--settlement-matrix-output",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "taipower_seasonal_settlement_matrix_v7_2.csv"
        ),
    )
    parser.add_argument(
        "--transition-summary-output",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "taipower_transition_period_partition_v7_2.csv"
        ),
    )
    parser.add_argument(
        "--interface-output",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "taipower_transition_period_settlement_interface_v7_2.json"
        ),
    )
    parser.add_argument(
        "--audit-json-output",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "taipower_transition_period_settlement_preflight_v7_2.json"
        ),
    )
    parser.add_argument(
        "--audit-text-output",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "taipower_transition_period_settlement_preflight_v7_2.txt"
        ),
    )
    return parser.parse_args()


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"{label} missing required columns: {missing}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def normalize_bool_series(series: pd.Series, label: str) -> pd.Series:
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
        raise RuntimeError(f"{label}: cannot parse boolean values {bad[:10]}")
    return out.astype(bool)


def read_annual_input(parquet_path: Path, csv_path: Path) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
            return df, parquet_path
        except (ImportError, ModuleNotFoundError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        "Canonical annual input not found. Expected either:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}\n"
        "Run Script 06 first."
    )


def expected_timeline() -> pd.DatetimeIndex:
    return pd.date_range(FORMAL_START, periods=EXPECTED_ROWS, freq="h")


def expected_summer_flag(ts: pd.Timestamp) -> bool:
    md = (ts.month, ts.day)
    return SUMMER_START_MMDD <= md <= SUMMER_END_MMDD


def validate_annual_input(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    require_columns(df_raw, ANNUAL_REQUIRED_COLUMNS, "Annual input")
    df = df_raw.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().any():
        raise RuntimeError("Annual input contains unparsable timestamps.")
    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)

    df = df.sort_values("timestamp").reset_index(drop=True)
    if len(df) != EXPECTED_ROWS:
        raise RuntimeError(
            f"Annual input rows={len(df):,}; expected {EXPECTED_ROWS:,}."
        )
    if df["timestamp"].duplicated().any():
        raise RuntimeError("Annual input contains duplicate timestamps.")

    actual = pd.DatetimeIndex(df["timestamp"])
    expected = expected_timeline()
    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise RuntimeError(
            "Annual input timeline mismatch: "
            f"missing={len(missing)}, extra={len(extra)}, "
            f"first={actual.min()}, last={actual.max()}."
        )

    verified = normalize_bool_series(
        df["tou_calendar_verified"], "tou_calendar_verified"
    )
    if not verified.all():
        raise RuntimeError(
            "Annual input is not fully backed by the audited TOU day calendar."
        )
    df["tou_calendar_verified"] = verified

    statuses = set(df["integration_status"].astype(str))
    if statuses != {"passed"}:
        raise RuntimeError(
            f"Annual input integration_status must be passed-only; found {statuses}."
        )

    is_summer = normalize_bool_series(df["is_summer"], "is_summer")
    df["is_summer"] = is_summer
    expected_flags = df["timestamp"].map(expected_summer_flag).astype(bool)
    mismatch = int((is_summer != expected_flags).sum())
    if mismatch:
        sample = df.loc[
            is_summer != expected_flags,
            ["timestamp", "is_summer", "season"],
        ].head(10)
        raise RuntimeError(
            "Hourly summer tags do not match May16-Oct15 rule. "
            f"mismatch_rows={mismatch}; sample={sample.to_dict('records')}"
        )

    expected_season = np.where(expected_flags, "summer", "non_summer")
    season_mismatch = int(
        (df["season"].astype(str).to_numpy() != expected_season).sum()
    )
    if season_mismatch:
        raise RuntimeError(
            f"season labels disagree with is_summer in {season_mismatch} rows."
        )

    invalid_tou = sorted(set(df["tou_period"].astype(str)) - set(TOU_PERIODS))
    if invalid_tou:
        raise RuntimeError(f"Unexpected TOU periods in annual input: {invalid_tou}")

    periods = df["billing_usage_period_id"].astype(str)
    observed_periods = sorted(periods.unique().tolist())
    if observed_periods != EXPECTED_USAGE_PERIODS:
        raise RuntimeError(
            "Unexpected billing usage-period set.\n"
            f"Observed: {observed_periods}\n"
            f"Expected: {EXPECTED_USAGE_PERIODS}"
        )
    df["billing_usage_period_id"] = periods

    period_season_counts = (
        df.groupby("billing_usage_period_id", observed=True)["season"]
        .nunique()
        .astype(int)
    )
    transition_periods = sorted(
        period_season_counts.loc[period_season_counts.gt(1)].index.astype(str).tolist()
    )
    if transition_periods != EXPECTED_TRANSITION_PERIODS:
        raise RuntimeError(
            "Mixed-season usage periods do not match expected May/October. "
            f"Observed={transition_periods}, expected={EXPECTED_TRANSITION_PERIODS}"
        )

    return df, {
        "rows": len(df),
        "start": df["timestamp"].min(),
        "end": df["timestamp"].max(),
        "tou_calendar_verified_all": True,
        "integration_status": "passed",
        "summer_tag_mismatch_rows": 0,
        "usage_periods": observed_periods,
        "transition_periods": transition_periods,
    }


def load_raw_tariff(path: Path) -> pd.DataFrame:
    require_file(path, "Raw 13b tariff registry")
    df = pd.read_csv(path)
    require_columns(df, RAW_TARIFF_REQUIRED_COLUMNS, "Raw 13b tariff registry")

    if df["parameter_id"].duplicated().any():
        dupes = df.loc[df["parameter_id"].duplicated(), "parameter_id"].tolist()
        raise RuntimeError(f"Raw tariff registry duplicate parameter IDs: {dupes}")

    roles = set(df["mainline_or_legacy"].astype(str).str.strip().str.lower())
    if roles != {"mainline"}:
        raise RuntimeError(f"Raw tariff registry must be mainline-only; found {roles}")

    df = df.copy()
    df["applicable"] = normalize_bool_series(df["applicable"], "raw tariff applicable")
    return df


def raw_numeric(indexed: pd.DataFrame, parameter_id: str) -> float:
    if parameter_id not in indexed.index:
        raise RuntimeError(f"Raw tariff parameter missing: {parameter_id}")
    value = pd.to_numeric(pd.Series([indexed.loc[parameter_id, "value_numeric"]]), errors="coerce").iloc[0]
    if pd.isna(value):
        raise RuntimeError(f"Raw tariff parameter is not numeric: {parameter_id}")
    return float(value)


def raw_text(indexed: pd.DataFrame, parameter_id: str) -> str:
    if parameter_id not in indexed.index:
        raise RuntimeError(f"Raw tariff parameter missing: {parameter_id}")
    value = indexed.loc[parameter_id, "value_text"]
    if pd.isna(value):
        raise RuntimeError(f"Raw tariff text parameter missing: {parameter_id}")
    return str(value)


def extract_overcontract_rules(raw_tariff: pd.DataFrame) -> dict[str, Any]:
    idx = raw_tariff.set_index("parameter_id", drop=False)

    tier1_fraction = raw_numeric(idx, "overcontract_tier1_threshold")
    tier1_multiplier = raw_numeric(idx, "overcontract_tier1_multiplier")
    tier2_multiplier = raw_numeric(idx, "overcontract_tier2_multiplier")
    period_order = raw_text(idx, "overcontract_period_order")
    non_dup_text = raw_text(idx, "overcontract_non_duplication").strip().upper()
    non_dup = non_dup_text == "TRUE"

    observed = {
        "tier1_threshold_fraction": tier1_fraction,
        "tier1_multiplier": tier1_multiplier,
        "tier2_multiplier": tier2_multiplier,
        "period_order": period_order,
        "non_duplication": non_dup,
    }

    for key in ["tier1_threshold_fraction", "tier1_multiplier", "tier2_multiplier"]:
        if not np.isclose(
            float(observed[key]),
            float(EXPECTED_OVERCONTRACT[key]),
            rtol=0.0,
            atol=1e-12,
        ):
            raise RuntimeError(
                f"Over-contract rule mismatch for {key}: "
                f"observed={observed[key]}, expected={EXPECTED_OVERCONTRACT[key]}"
            )
    if period_order != EXPECTED_OVERCONTRACT["period_order"]:
        raise RuntimeError(
            f"Over-contract period order mismatch: observed={period_order}"
        )
    if non_dup is not True:
        raise RuntimeError("Over-contract non-duplication must be TRUE.")

    return observed


def load_normalized_tariff(path: Path) -> pd.DataFrame:
    require_file(path, "14a normalized optimization tariff")
    df = pd.read_csv(path)
    require_columns(
        df,
        NORMALIZED_TARIFF_REQUIRED_COLUMNS,
        "14a normalized optimization tariff",
    )

    df = df.copy()
    df["applicable"] = normalize_bool_series(
        df["applicable"], "normalized tariff applicable"
    )
    df["usage_year"] = pd.to_numeric(df["usage_year"], errors="raise").astype(int)
    df["optimization_currency_base_year"] = pd.to_numeric(
        df["optimization_currency_base_year"], errors="raise"
    ).astype(int)

    if set(df["usage_year"].unique().tolist()) != {2024, 2025}:
        raise RuntimeError("Normalized tariff must contain usage years 2024 and 2025.")
    if set(df["optimization_currency"].astype(str)) != {"NTD"}:
        raise RuntimeError("Normalized tariff optimization currency must be NTD.")
    if set(df["optimization_currency_base_year"].unique().tolist()) != {2023}:
        raise RuntimeError("Normalized tariff must use currency base year 2023.")

    applicable = df.loc[df["applicable"]].copy()
    applicable_values = pd.to_numeric(
        applicable["value_constant_ntd2023"], errors="coerce"
    )
    if applicable_values.isna().any() or (applicable_values < 0).any():
        raise RuntimeError(
            "Applicable normalized tariff rows must have non-negative finite NTD-2023 values."
        )

    return df


def load_14a_interface(path: Path) -> dict[str, Any]:
    require_file(path, "14a production economic interface")
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("status") != "READY_FOR_EOB_OBJECTIVE_WIRING":
        raise RuntimeError(
            "14a interface is not READY_FOR_EOB_OBJECTIVE_WIRING: "
            f"{data.get('status')!r}"
        )

    basis = data.get("monetary_basis", {})
    if basis.get("currency") != "NTD" or basis.get("currency_base_year") != 2023:
        raise RuntimeError("14a monetary basis is not constant NTD-2023.")
    if basis.get("discount_rate_role") != "real_modeling_discount_rate":
        raise RuntimeError("14a discount-rate role is not real_modeling_discount_rate.")

    tariff = data.get("taipower_tariff", {})
    if tariff.get("non_summer_peak_semantics") != "N/A_not_zero":
        raise RuntimeError("14a did not preserve non-summer peak N/A semantics.")
    if tariff.get("separate_subsidy_cashflow") is not False:
        raise RuntimeError("14a unexpectedly allows separate subsidy cash flow.")

    return data


def load_13c_audit(path: Path) -> dict[str, Any]:
    require_file(path, "13c billing audit")
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("status") != "PASS":
        raise RuntimeError(f"13c audit is not PASS: {data.get('status')!r}")

    gates = data.get("gates", {})
    if any(
        isinstance(v, str) and v != "PASS"
        for v in gates.values()
    ):
        raise RuntimeError("13c audit contains a non-PASS string gate.")

    boundary = data.get("transition_month_boundary", {})
    months = boundary.get("months")
    if months != EXPECTED_TRANSITION_PERIODS:
        raise RuntimeError(
            "13c transition-month set mismatch: "
            f"observed={months}, expected={EXPECTED_TRANSITION_PERIODS}"
        )

    economic_role = data.get("economic_role_boundary", {})
    if economic_role.get("bill_derived_tariff_coefficients") is not False:
        raise RuntimeError("13c does not explicitly reject bill-derived tariff coefficients.")
    if economic_role.get("subsidy_in_production_billing_engine") is not False:
        raise RuntimeError("13c does not explicitly reject subsidy in production billing.")

    return data


def normalized_basic_rate_lookup(
    normalized: pd.DataFrame,
    usage_year: int,
    season: str,
    contract_period: str,
) -> dict[str, Any]:
    parameter_id = f"basic_{season}_{contract_period}"
    rows = normalized.loc[
        normalized["parameter_id"].eq(parameter_id)
        & normalized["usage_year"].eq(usage_year)
    ]
    if len(rows) != 1:
        raise RuntimeError(
            f"Expected exactly one normalized tariff row for {parameter_id}, "
            f"usage_year={usage_year}; found {len(rows)}."
        )

    row = rows.iloc[0]
    if not bool(row["applicable"]):
        raise RuntimeError(f"Basic-charge rate unexpectedly not applicable: {parameter_id}")

    rate = pd.to_numeric(pd.Series([row["value_constant_ntd2023"]]), errors="coerce").iloc[0]
    if pd.isna(rate):
        raise RuntimeError(f"Missing normalized basic rate: {parameter_id}")

    return {
        "parameter_id": parameter_id,
        "rate_constant_ntd2023_per_kw_month": float(rate),
        "optimization_unit": str(row["optimization_unit"]),
        "raw_tariff_source_file": str(row["raw_tariff_source_file"]),
        "raw_tariff_source_role": str(row["raw_tariff_source_role"]),
    }


def build_settlement_matrix(
    annual: pd.DataFrame,
    normalized: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for usage_period_id in EXPECTED_USAGE_PERIODS:
        month_df = annual.loc[
            annual["billing_usage_period_id"].eq(usage_period_id)
        ].copy()
        if month_df.empty:
            raise RuntimeError(f"No annual-input rows for {usage_period_id}")

        usage_years = sorted(month_df["timestamp"].dt.year.unique().tolist())
        if len(usage_years) != 1:
            raise RuntimeError(
                f"{usage_period_id}: expected one usage year, found {usage_years}"
            )
        usage_year = int(usage_years[0])

        seasons = [s for s in ["non_summer", "summer"] if (month_df["season"] == s).any()]
        period_role = "transition" if len(seasons) == 2 else f"pure_{seasons[0]}"

        for season in seasons:
            season_df = month_df.loc[month_df["season"].eq(season)].copy()
            if season_df.empty:
                continue

            for tou_period in APPLICABLE_OVERCONTRACT_PERIODS[season]:
                period_df = season_df.loc[season_df["tou_period"].eq(tou_period)]
                contract_period = CONTRACT_PERIOD_BY_TOU[tou_period]
                rate_info = normalized_basic_rate_lookup(
                    normalized,
                    usage_year,
                    season,
                    contract_period,
                )

                rows.append(
                    {
                        "billing_usage_period_id": usage_period_id,
                        "usage_year": usage_year,
                        "billing_period_role": period_role,
                        "season": season,
                        "tou_period": tou_period,
                        "contract_period": contract_period,
                        "hour_count": int(len(period_df)),
                        "active_in_hourly_case": bool(len(period_df) > 0),
                        "first_timestamp": (
                            period_df["timestamp"].min().isoformat()
                            if len(period_df) > 0
                            else None
                        ),
                        "last_timestamp": (
                            period_df["timestamp"].max().isoformat()
                            if len(period_df) > 0
                            else None
                        ),
                        "basic_rate_parameter_id": rate_info["parameter_id"],
                        "basic_rate_constant_ntd2023_per_kw_month": (
                            rate_info["rate_constant_ntd2023_per_kw_month"]
                        ),
                        "basic_rate_unit": rate_info["optimization_unit"],
                        "raw_tariff_source_file": rate_info["raw_tariff_source_file"],
                        "raw_tariff_source_role": rate_info["raw_tariff_source_role"],
                        "overcontract_rate_semantics": (
                            "Use the basic-charge rate applicable to this season and "
                            "contract-period demand class."
                        ),
                        "cross_season_positive_overcontract_aggregation": (
                            "DEFERRED_NOT_SILENTLY_ASSUMED"
                            if period_role == "transition"
                            else "NOT_APPLICABLE_PURE_SEASON"
                        ),
                    }
                )

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("Settlement matrix unexpectedly empty.")

    # Non-summer peak must never appear as an applicable settlement row.
    bad_ns_peak = out.loc[
        out["season"].eq("non_summer") & out["tou_period"].eq("peak")
    ]
    if not bad_ns_peak.empty:
        raise RuntimeError("Non-summer peak was incorrectly added to settlement matrix.")

    return out


def build_transition_summary(annual: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for usage_period_id in EXPECTED_USAGE_PERIODS:
        month_df = annual.loc[
            annual["billing_usage_period_id"].eq(usage_period_id)
        ].copy()
        season_counts = month_df["season"].value_counts().to_dict()
        seasons = sorted(season_counts)
        role = "transition" if len(seasons) > 1 else f"pure_{seasons[0]}"

        ns = month_df.loc[month_df["season"].eq("non_summer")]
        su = month_df.loc[month_df["season"].eq("summer")]

        rows.append(
            {
                "billing_usage_period_id": usage_period_id,
                "billing_period_role": role,
                "non_summer_hours": int(len(ns)),
                "summer_hours": int(len(su)),
                "non_summer_first_timestamp": (
                    ns["timestamp"].min().isoformat() if len(ns) else None
                ),
                "non_summer_last_timestamp": (
                    ns["timestamp"].max().isoformat() if len(ns) else None
                ),
                "summer_first_timestamp": (
                    su["timestamp"].min().isoformat() if len(su) else None
                ),
                "summer_last_timestamp": (
                    su["timestamp"].max().isoformat() if len(su) else None
                ),
                "cross_season_positive_overcontract_aggregation_status": (
                    "UNRESOLVED_OFFICIAL_AGGREGATION_RULE"
                    if role == "transition"
                    else "NOT_APPLICABLE"
                ),
            }
        )

    out = pd.DataFrame(rows)
    transitions = out.loc[out["billing_period_role"].eq("transition")]
    if transitions["billing_usage_period_id"].tolist() != EXPECTED_TRANSITION_PERIODS:
        raise RuntimeError("Transition summary does not identify exactly May and October.")
    return out


def build_audit_text(summary: dict[str, Any]) -> str:
    lines = [
        "NTUST v7.2 Transition-Period Seasonal Settlement Preflight",
        f"Script version: {summary['script_version']}",
        "",
        "Inputs",
    ]
    for key, value in summary["inputs"].items():
        if isinstance(value, dict) and "path" in value:
            lines.append(f"- {key}: {value['path']}")

    lines += [
        "",
        "Gate interpretation",
    ]
    for key, value in summary["gates"].items():
        lines.append(f"- {key}: {value}")

    lines += [
        "",
        "Seasonal settlement interpretation",
        "- Official high-voltage summer boundary: May 16 through October 15.",
        "- Tariff coefficients are sourced from 13b / 14a, not from bills.",
        "- Pure-season over-contract structure: 10% threshold, 2x / 3x, sequential non-duplication.",
        "- Mixed-season usage periods detected: 2025-05 and 2025-10.",
        "- Season-specific demand classes and basic rates are exported for downstream EOB / Layer A wiring.",
        "- Cross-season positive-overcontract aggregation is NOT fabricated in 14b.",
        "- 13c bills remain validation evidence, not the source of tariff coefficients.",
        "",
        "Transition-period rule status",
        f"- Institutional status: {summary['transition_rule_status']['institutional_status']}",
        f"- EOB coding status: {summary['transition_rule_status']['eob_coding_status']}",
        f"- Required downstream behavior: {summary['transition_rule_status']['downstream_behavior']}",
        "",
        "Outputs",
        f"- Seasonal settlement matrix: {summary['outputs']['settlement_matrix']}",
        f"- Transition partition summary: {summary['outputs']['transition_summary']}",
        f"- Settlement interface: {summary['outputs']['interface']}",
        f"- Audit JSON: {summary['outputs']['audit_json']}",
        f"- Audit TXT: {summary['outputs']['audit_txt']}",
        "",
        f"Final verdict: {summary['final_verdict']}",
        "No EOB / Layer A optimization was executed.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()

    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.2 Transition-Period Seasonal Settlement Preflight")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    try:
        for path in [
            args.settlement_matrix_output,
            args.transition_summary_output,
            args.interface_output,
            args.audit_json_output,
            args.audit_text_output,
        ]:
            path.parent.mkdir(parents=True, exist_ok=True)

        annual_raw, annual_path = read_annual_input(
            args.annual_parquet,
            args.annual_csv,
        )
        annual, annual_audit = validate_annual_input(annual_raw)

        raw_tariff = load_raw_tariff(args.raw_tariff_registry)
        overcontract_rules = extract_overcontract_rules(raw_tariff)
        normalized_tariff = load_normalized_tariff(args.normalized_tariff_registry)
        interface_14a = load_14a_interface(args.economic_interface_14a)
        audit_13c = load_13c_audit(args.bill_audit_13c)

        input_hashes = {
            "annual_input": {
                "path": str(annual_path),
                "sha256": sha256_file(annual_path),
            },
            "raw_tariff_registry_13b": {
                "path": str(args.raw_tariff_registry),
                "sha256": sha256_file(args.raw_tariff_registry),
            },
            "normalized_tariff_registry_14a": {
                "path": str(args.normalized_tariff_registry),
                "sha256": sha256_file(args.normalized_tariff_registry),
            },
            "economic_interface_14a": {
                "path": str(args.economic_interface_14a),
                "sha256": sha256_file(args.economic_interface_14a),
            },
            "bill_audit_13c": {
                "path": str(args.bill_audit_13c),
                "sha256": sha256_file(args.bill_audit_13c),
            },
        }

        settlement_matrix = build_settlement_matrix(annual, normalized_tariff)
        transition_summary = build_transition_summary(annual)

        settlement_matrix.to_csv(
            args.settlement_matrix_output,
            index=False,
            encoding="utf-8-sig",
        )
        transition_summary.to_csv(
            args.transition_summary_output,
            index=False,
            encoding="utf-8-sig",
        )

        # Confirm the 13c empirical boundary remains exactly the intended one.
        boundary_13c = audit_13c.get("transition_month_boundary", {})
        if boundary_13c.get("explicit_public_50_50_clause_located") is not False:
            raise RuntimeError(
                "13c transition boundary unexpectedly claims an explicit public 50/50 clause."
            )

        # 14a retains a case-validated basic-charge transition convention; 14b
        # does not reinterpret that as the positive-overcontract aggregation rule.
        tariff_14a = interface_14a.get("taipower_tariff", {})
        basic_transition_14a = tariff_14a.get("may_october_basic_charge_transition")

        settlement_interface = {
            "interface_version": "v7.2",
            "generated_by": SCRIPT_VERSION,
            "status": "READY_FOR_EOB_SEASONAL_SETTLEMENT_WIRING",
            "case_year": {
                "start": FORMAL_START.isoformat(),
                "end_exclusive": FORMAL_END_EXCLUSIVE.isoformat(),
                "hours": EXPECTED_ROWS,
                "billing_usage_periods": EXPECTED_USAGE_PERIODS,
            },
            "season_rule": {
                "summer_start_mmdd": "05-16",
                "summer_end_mmdd": "10-15",
                "assignment_basis": "hourly timestamp applicability",
                "hourly_calendar_audit": "PASS",
                "transition_periods": EXPECTED_TRANSITION_PERIODS,
            },
            "overcontract_rule": {
                **overcontract_rules,
                "basic_rate_mapping": CONTRACT_PERIOD_BY_TOU,
                "summer_applicable_periods": APPLICABLE_OVERCONTRACT_PERIODS["summer"],
                "non_summer_applicable_periods": APPLICABLE_OVERCONTRACT_PERIODS["non_summer"],
                "non_summer_peak_semantics": "N/A_not_zero",
            },
            "monetary_basis": {
                "currency": "NTD",
                "currency_base_year": 2023,
                "basis_label": "constant NTD-2023",
                "normalized_tariff_registry": str(args.normalized_tariff_registry),
            },
            "transition_regular_basic_boundary": {
                "upstream_14a_label": basic_transition_14a,
                "upstream_13c_role": "case validation only",
                "positive_overcontract_rule_inferred_from_basic_charge": False,
            },
            "mixed_season_positive_overcontract_aggregation": {
                "institutional_status": "OFFICIAL_CROSS_SEASON_AGGREGATION_NOT_EXPLICITLY_LOCATED",
                "fabricated_default_allowed": False,
                "season_specific_tariff_applicability_available": True,
                "season_specific_demand_masks_available": True,
                "final_cross_season_aggregation_formula_frozen": False,
                "eob_requirement": (
                    "Use the exported season-specific masks/rates. After solve, "
                    "report whether any mixed-season billing period has positive "
                    "over-contract demand. Do not silently label an unverified "
                    "cross-season aggregation formula as official."
                ),
            },
            "official_reference": {
                "url": TAIPOWER_CROSS_PERIOD_PUBLIC_REFERENCE,
                "claim_scope": TAIPOWER_CROSS_PERIOD_REFERENCE_SCOPE,
            },
            "artifacts": {
                "seasonal_settlement_matrix": str(args.settlement_matrix_output),
                "transition_partition_summary": str(args.transition_summary_output),
            },
            "inputs": input_hashes,
        }
        args.interface_output.write_text(
            json.dumps(
                json_safe(settlement_interface),
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            ),
            encoding="utf-8",
        )

        gates = {
            "annual_input_8760_exact_timeline": "PASS",
            "audited_tou_calendar_required": "PASS",
            "may16_oct15_hourly_season_tags": "PASS",
            "transition_periods_may_october_detected": "PASS",
            "13b_season_specific_basic_rates_loaded": "PASS",
            "13b_overcontract_10pct_2x_3x_nonduplication": "PASS",
            "14a_constant_ntd2023_tariff_loaded": "PASS",
            "14a_ready_for_eob_objective_wiring": "PASS",
            "13c_upstream_bill_regression": "PASS",
            "bill_derived_tariff_coefficients_blocked": "PASS",
            "non_summer_peak_na_semantics": "PASS",
            "unsupported_transition_overcontract_rule_not_fabricated": "PASS",
            "seasonal_settlement_matrix_generated": "PASS",
        }

        summary = {
            "script_version": SCRIPT_VERSION,
            "status": "PASS",
            "inputs": input_hashes,
            "annual_input_audit": annual_audit,
            "overcontract_rule": overcontract_rules,
            "transition_rule_status": {
                "institutional_status": (
                    "PARTIALLY_RESOLVED: season-specific applicability is "
                    "defined; cross-season positive-overcontract aggregation "
                    "is not explicitly located in retained official evidence"
                ),
                "eob_coding_status": "READY_WITH_EXPLICIT_TRANSITION_FLAG",
                "downstream_behavior": (
                    "EOB/Layer A must preserve season-specific settlement "
                    "components and surface any positive May/October overage."
                ),
            },
            "evidence_boundary": {
                "tariff_coefficients_source": "13b official tariff registry",
                "bills_role": "validation only; not coefficient construction",
                "13c_transition_contract_basic_case_validated": True,
                "13c_positive_transition_overcontract_observed": False,
                "taipower_cross_period_public_reference": (
                    TAIPOWER_CROSS_PERIOD_PUBLIC_REFERENCE
                ),
                "public_reference_claim_scope": (
                    TAIPOWER_CROSS_PERIOD_REFERENCE_SCOPE
                ),
            },
            "gates": gates,
            "outputs": {
                "settlement_matrix": str(args.settlement_matrix_output),
                "transition_summary": str(args.transition_summary_output),
                "interface": str(args.interface_output),
                "audit_json": str(args.audit_json_output),
                "audit_txt": str(args.audit_text_output),
            },
            "final_verdict": (
                "SCRIPT 14b SEASONAL-SETTLEMENT PREFLIGHT PASS / "
                "READY FOR EOB WIRING WITH TRANSITION FLAG"
            ),
        }

        args.audit_json_output.write_text(
            json.dumps(
                json_safe(summary),
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            ),
            encoding="utf-8",
        )
        args.audit_text_output.write_text(build_audit_text(summary), encoding="utf-8")

        print("Inputs")
        print(f"- annual_input: {annual_path}")
        print(f"- raw_tariff_registry_13b: {args.raw_tariff_registry}")
        print(f"- normalized_tariff_registry_14a: {args.normalized_tariff_registry}")
        print(f"- economic_interface_14a: {args.economic_interface_14a}")
        print(f"- bill_audit_13c: {args.bill_audit_13c}")
        print()

        print("Gate interpretation")
        for key, value in gates.items():
            print(f"- {key}: {value}")
        print()

        print("Transition-period interpretation")
        print("- Transition usage periods: 2025-05, 2025-10")
        print("- Season assignment: hourly May16-Oct15 applicability")
        print("- Tariff coefficients: official 13b/14a registries, not bills")
        print("- 13c role: validation only")
        print("- Cross-season positive-overcontract aggregation: NOT FABRICATED")
        print("- EOB/Layer A requirement: preserve seasonal components and flag any positive transition overage")
        print()

        print("Outputs")
        print(f"- Seasonal settlement matrix: {args.settlement_matrix_output}")
        print(f"- Transition partition summary: {args.transition_summary_output}")
        print(f"- Settlement interface: {args.interface_output}")
        print(f"- Audit JSON: {args.audit_json_output}")
        print(f"- Audit TXT: {args.audit_text_output}")
        print()
        print(summary["final_verdict"])
        print("No EOB / Layer A optimization was executed.")
        return 0

    except Exception as exc:
        print()
        print("14b PRE-FLIGHT FAILED", file=sys.stderr)
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
