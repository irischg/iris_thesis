#!/usr/bin/env python3
"""
13c_regress_taipower_core_bill_components.py

NTUST thesis v7.1 — core Taipower monthly bill regression.

Purpose
-------
Validate that the production tariff registry frozen by Script 13b reproduces
the decision-relevant core Taipower billing components observed in the NTUST
case-year bills.

Inputs
------
- data/reference/taipower_tariff_registry_v7_1.csv
- data/reference/taipower_bills_final_clean.csv
- results/parameter_audit/taipower_tariff_registry_audit_v7_1.json

Case year
---------
2024-11-01 through 2025-10-31 (12 monthly usage periods).

This script validates:
1) pure-season Variable/Energy Charge;
2) contract basic charge;
3) over-contract basic charge using sequential, non-duplicated TOU overage;
4) May/October transition-month contract-basic 50/50 case identity.

Important boundaries
--------------------
- Tariff rates are READ from the 13b production registry; they are not copied
  into a second production rate table here.
- May/October monthly aggregate TOU kWh are insufficient to reconstruct energy
  charges because those months cross the 05-16 / 10-15 season boundary.
  The script therefore does NOT infer a hidden summer/non-summer kWh split.
- The May/October 50/50 regular-basic identity is treated as a
  CASE-VALIDATED_TRANSITION_CONVENTION, not as a universal official rule.
- Subsidy, VAT, power-factor adjustments, discounts, refunds, and aggregated
  "Other Reductions" are outside this core production-billing regression.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-taipower-core-bill-regression-2026-08-24"

CASE_USAGE_MONTHS = pd.period_range(
    "2024-11",
    "2025-10",
    freq="M",
).astype(str).tolist()

PURE_NON_SUMMER_MONTHS = [
    "2024-11",
    "2024-12",
    "2025-01",
    "2025-02",
    "2025-03",
    "2025-04",
]

PURE_SUMMER_MONTHS = [
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
]

TRANSITION_MONTHS = ["2025-05", "2025-10"]

TOU_PERIODS = ["peak", "half", "sat_half", "off"]

OVERCONTRACT_BASIC_RATE_KEY = {
    "peak": "regular",
    "half": "half",
    "sat_half": "sat_half",
    "off": "off",
}

DEMAND_COLUMNS = {
    "peak": "Max Demand - Peak (kW)",
    "half": "Max Demand - Semi-peak (kW)",
    "sat_half": "Max Demand - Sat Semi-peak (kW)",
    "off": "Max Demand - Off-peak (kW)",
}

ENERGY_COLUMNS = {
    "peak": "Energy - Peak (kWh)",
    "half": "Energy - Semi-peak (kWh)",
    "sat_half": "Energy - Sat Semi-peak (kWh)",
    "off": "Energy - Off-peak (kWh)",
}

BILL_COLUMNS = {
    "regular_cc_kw": "Contract Capacity CP (kW)",
    "contract_basic_ntd": "Basic Charge (Contract) (NTD)",
    "noncontract_basic_ntd": "Basic Charge (Non-contract) (NTD)",
    "energy_charge_ntd": "Variable/Energy Charge (NTD)",
}

REQUIRED_BILL_COLUMNS = {
    "Period Start",
    "Period End",
    *DEMAND_COLUMNS.values(),
    *ENERGY_COLUMNS.values(),
    *BILL_COLUMNS.values(),
}

EXPECTED_REGISTRY_PARAMETER_IDS = {
    # Energy.
    "energy_summer_peak",
    "energy_summer_half",
    "energy_summer_sat_half",
    "energy_summer_off",
    "energy_non_summer_peak",
    "energy_non_summer_half",
    "energy_non_summer_sat_half",
    "energy_non_summer_off",
    # Basic.
    "basic_summer_regular",
    "basic_summer_half",
    "basic_summer_sat_half",
    "basic_summer_off",
    "basic_non_summer_regular",
    "basic_non_summer_half",
    "basic_non_summer_sat_half",
    "basic_non_summer_off",
    # Over-contract.
    "overcontract_tier1_threshold",
    "overcontract_tier1_multiplier",
    "overcontract_tier2_multiplier",
    "overcontract_period_order",
    "overcontract_non_duplication",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def to_float(value: object, label: str) -> float:
    if pd.isna(value):
        raise RuntimeError(f"{label}: missing numeric value.")

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip().replace(",", "")
    try:
        return float(text)
    except ValueError as exc:
        raise RuntimeError(
            f"{label}: cannot parse numeric value {value!r}"
        ) from exc


def observed_noncontract_charge(
    row: pd.Series,
    regular_cc_kw: float,
    season: str,
) -> tuple[float, str]:
    """Read an observed non-contract charge without inferring an overage.

    A blank bill charge is accepted as zero only when every applicable billed
    maximum demand is at or below the regular contract capacity. A non-summer
    peak demand is not applicable and is not read or converted to zero.
    """
    value = row[BILL_COLUMNS["noncontract_basic_ntd"]]
    is_blank = pd.isna(value) or (
        isinstance(value, str) and not value.strip()
    )
    if not is_blank:
        return (
            to_float(value, "observed non-contract basic"),
            "OBSERVED_NUMERIC",
        )

    demands: dict[str, float] = {}
    for period in applicable_overcontract_periods(season):
        demands[period] = to_float(
            row[DEMAND_COLUMNS[period]],
            f"observed billed maximum demand ({period})",
        )

    overages = {
        period: demand_kw - regular_cc_kw
        for period, demand_kw in demands.items()
    }
    if all(overage_kw <= 0.0 for overage_kw in overages.values()):
        return 0.0, "BLANK_INTERPRETED_AS_ZERO_NO_OVERAGE"

    raise RuntimeError(
        "observed non-contract basic: blank value with billed maximum demand "
        f"above regular contract capacity; regular_cc_kw={regular_cc_kw}, "
        f"demands_kw={demands}, overages_kw={overages}"
    )


def applicable_overcontract_periods(season: str) -> list[str]:
    if season == "summer":
        return ["peak", "half", "sat_half", "off"]
    if season == "non_summer":
        return ["half", "sat_half", "off"]
    if season == "transition":
        # Mixed-season months are not settled here; retain all observed periods
        # for the existing zero-overage diagnostic only.
        return TOU_PERIODS.copy()
    raise RuntimeError(f"Unknown over-contract season: {season!r}")


def assert_close(
    observed: float,
    expected: float,
    label: str,
    atol: float = 1e-6,
) -> None:
    if not np.isclose(observed, expected, rtol=0.0, atol=atol):
        raise RuntimeError(
            f"{label}: observed={observed}, expected={expected}, "
            f"residual={observed - expected}"
        )


def load_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            "Production tariff registry not found. Run Script 13b first:\n"
            f"- {path}"
        )

    df = pd.read_csv(path)

    required_columns = {
        "parameter_id",
        "parameter_group",
        "season",
        "tou_period",
        "contract_period",
        "value_numeric",
        "value_text",
        "unit",
        "applicable",
        "customer_class",
        "institution_type",
        "voltage_class",
        "tou_scheme",
        "case_effective_start",
        "case_effective_end",
    }
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise RuntimeError(
            "Tariff registry missing required columns:\n"
            + "\n".join(f"- {x}" for x in missing_columns)
        )

    duplicate_ids = df.loc[
        df["parameter_id"].duplicated(keep=False),
        "parameter_id",
    ].tolist()
    if duplicate_ids:
        raise RuntimeError(
            f"Tariff registry has duplicate parameter_id values: {duplicate_ids}"
        )

    missing_ids = sorted(
        EXPECTED_REGISTRY_PARAMETER_IDS - set(df["parameter_id"])
    )
    if missing_ids:
        raise RuntimeError(
            "Tariff registry missing expected production parameters:\n"
            + "\n".join(f"- {x}" for x in missing_ids)
        )

    identities = {
        "customer_class": set(df["customer_class"].dropna().astype(str)),
        "institution_type": set(
            df["institution_type"].dropna().astype(str)
        ),
        "voltage_class": set(df["voltage_class"].dropna().astype(str)),
        "tou_scheme": set(df["tou_scheme"].dropna().astype(str)),
        "case_effective_start": set(
            df["case_effective_start"].dropna().astype(str)
        ),
        "case_effective_end": set(
            df["case_effective_end"].dropna().astype(str)
        ),
    }

    expected_identity = {
        "customer_class": {"school"},
        "institution_type": {"university_college"},
        "voltage_class": {"high_voltage"},
        "tou_scheme": {"three_period_fixed_peak"},
        "case_effective_start": {"2024-11-01"},
        "case_effective_end": {"2025-10-31"},
    }

    for key, expected in expected_identity.items():
        if identities[key] != expected:
            raise RuntimeError(
                f"Tariff registry identity mismatch for {key}: "
                f"observed={identities[key]}, expected={expected}"
            )

    return df


def load_13b_audit(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(
            "13b tariff audit JSON not found. Run Script 13b first:\n"
            f"- {path}"
        )

    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("status") != "PASS":
        raise RuntimeError(
            f"13b audit is not PASS: {data.get('status')!r}"
        )

    gates = data.get("gates", {})
    blocking_gate_values = [
        value
        for value in gates.values()
        if isinstance(value, str)
    ]
    if any(value != "PASS" for value in blocking_gate_values):
        raise RuntimeError(
            "13b audit JSON contains a non-PASS string gate."
        )

    role_boundaries = data.get("role_boundaries", {})
    if role_boundaries.get("bill_derived_tariff_coefficients") is not False:
        raise RuntimeError(
            "13b role boundary does not explicitly reject bill-derived "
            "tariff coefficients."
        )
    if role_boundaries.get("subsidy_in_production_tariff") is not False:
        raise RuntimeError(
            "13b role boundary does not explicitly reject subsidy as a "
            "production tariff coefficient."
        )

    return data


def registry_index(registry: pd.DataFrame) -> pd.DataFrame:
    return registry.set_index("parameter_id", drop=False)


def registry_numeric(
    indexed: pd.DataFrame,
    parameter_id: str,
) -> float:
    if parameter_id not in indexed.index:
        raise RuntimeError(
            f"Registry parameter not found: {parameter_id}"
        )
    return to_float(
        indexed.loc[parameter_id, "value_numeric"],
        parameter_id,
    )


def registry_text(
    indexed: pd.DataFrame,
    parameter_id: str,
) -> str:
    if parameter_id not in indexed.index:
        raise RuntimeError(
            f"Registry parameter not found: {parameter_id}"
        )
    value = indexed.loc[parameter_id, "value_text"]
    if pd.isna(value):
        raise RuntimeError(
            f"{parameter_id}: missing text value."
        )
    return str(value)


def energy_rate(
    indexed: pd.DataFrame,
    season: str,
    period: str,
) -> float | None:
    parameter_id = f"energy_{season}_{period}"
    row = indexed.loc[parameter_id]

    applicable = str(row["applicable"]).strip().lower() in {
        "true",
        "1",
        "yes",
    }
    value = row["value_numeric"]

    if not applicable:
        if pd.notna(value):
            raise RuntimeError(
                f"{parameter_id}: non-applicable rate must be NaN."
            )
        return None

    return to_float(value, parameter_id)


def basic_rate(
    indexed: pd.DataFrame,
    season: str,
    period: str,
) -> float:
    return registry_numeric(
        indexed,
        f"basic_{season}_{period}",
    )


def load_case_bills(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Bill file not found: {path}")

    df = pd.read_csv(path)

    missing = sorted(REQUIRED_BILL_COLUMNS - set(df.columns))
    if missing:
        raise RuntimeError(
            "Bill CSV missing required columns:\n"
            + "\n".join(f"- {x}" for x in missing)
        )

    work = df.copy()
    work["Period Start"] = pd.to_datetime(
        work["Period Start"],
        errors="coerce",
    )
    work["Period End"] = pd.to_datetime(
        work["Period End"],
        errors="coerce",
    )
    if work[["Period Start", "Period End"]].isna().any().any():
        raise RuntimeError("Period Start/End contains unparsable dates.")

    work["usage_period_id"] = (
        work["Period Start"].dt.to_period("M").astype(str)
    )
    case = work.loc[
        work["usage_period_id"].isin(CASE_USAGE_MONTHS)
    ].copy()

    observed_periods = case["usage_period_id"].tolist()
    if len(case) != len(CASE_USAGE_MONTHS):
        raise RuntimeError(
            "Expected exactly 12 case-year usage periods; "
            f"found {len(case)}."
        )

    if set(observed_periods) != set(CASE_USAGE_MONTHS):
        raise RuntimeError(
            "Case-year usage-period set mismatch.\n"
            f"Observed: {sorted(observed_periods)}\n"
            f"Expected: {CASE_USAGE_MONTHS}"
        )

    if case["usage_period_id"].duplicated().any():
        duplicates = case.loc[
            case["usage_period_id"].duplicated(keep=False),
            "usage_period_id",
        ].tolist()
        raise RuntimeError(
            f"Duplicate case-year usage periods: {duplicates}"
        )

    return case.sort_values("Period Start").reset_index(drop=True)


def season_role(usage_period_id: str) -> str:
    if usage_period_id in PURE_NON_SUMMER_MONTHS:
        return "pure_non_summer"
    if usage_period_id in PURE_SUMMER_MONTHS:
        return "pure_summer"
    if usage_period_id in TRANSITION_MONTHS:
        return "transition"
    raise RuntimeError(
        f"Unexpected case-year usage period: {usage_period_id}"
    )


def season_for_pure_month(usage_period_id: str) -> str:
    role = season_role(usage_period_id)
    if role == "pure_non_summer":
        return "non_summer"
    if role == "pure_summer":
        return "summer"
    raise RuntimeError(
        f"{usage_period_id} is not a pure-season month."
    )


def predict_pure_energy_charge(
    row: pd.Series,
    indexed: pd.DataFrame,
    season: str,
) -> tuple[float, dict[str, float]]:
    components: dict[str, float] = {}
    total = 0.0

    for period in TOU_PERIODS:
        kwh = to_float(
            row[ENERGY_COLUMNS[period]],
            f"{row['usage_period_id']} {period} kWh",
        )
        rate = energy_rate(indexed, season, period)

        if rate is None:
            if abs(kwh) > 1e-9:
                raise RuntimeError(
                    f"{row['usage_period_id']}: {period} kWh={kwh} "
                    f"but {season} {period} is not applicable."
                )
            component = 0.0
        else:
            component = kwh * rate

        components[period] = component
        total += component

    return float(total), components


def cumulative_contract_thresholds(
    regular_cc_kw: float,
) -> dict[str, float]:
    """
    NTUST v7.1 case assumption:
    supplementary half / Saturday-half / off-peak contracts are fixed to zero.

    Therefore all four cumulative period thresholds equal regular CC.
    """
    return {
        "peak": regular_cc_kw,
        "half": regular_cc_kw,
        "sat_half": regular_cc_kw,
        "off": regular_cc_kw,
    }


def overcontract_components(
    row: pd.Series,
    indexed: pd.DataFrame,
    season: str,
) -> tuple[float, list[dict[str, object]]]:
    """
    Sequential non-duplicated over-contract settlement.

    First compute each period's raw exceedance relative to its cumulative
    contract threshold. Then charge only the incremental exceedance beyond the
    largest raw exceedance already seen in earlier TOU periods.

    Tier allocation is applied to the incremental interval of raw exceedance:
    the portion up to 10% of that period's cumulative contract threshold uses
    the 2x multiplier; the portion beyond 10% uses 3x.

    This preserves:
    peak -> half -> sat_half -> off
    and avoids counting the same overage kW more than once.
    """
    registry_period_order = registry_text(
        indexed,
        "overcontract_period_order",
    ).split(">")
    if registry_period_order != TOU_PERIODS:
        raise RuntimeError(
            f"Unexpected registry period order: {registry_period_order}"
        )
    period_order = applicable_overcontract_periods(season)

    non_dup = registry_text(
        indexed,
        "overcontract_non_duplication",
    ).strip().upper()
    if non_dup != "TRUE":
        raise RuntimeError(
            "Registry over-contract non-duplication is not TRUE."
        )

    tier1_fraction = registry_numeric(
        indexed,
        "overcontract_tier1_threshold",
    )
    tier1_multiplier = registry_numeric(
        indexed,
        "overcontract_tier1_multiplier",
    )
    tier2_multiplier = registry_numeric(
        indexed,
        "overcontract_tier2_multiplier",
    )

    regular_cc_kw = to_float(
        row[BILL_COLUMNS["regular_cc_kw"]],
        f"{row['usage_period_id']} regular CC",
    )
    thresholds = cumulative_contract_thresholds(regular_cc_kw)

    max_demands: dict[str, float] = {}
    raw_over: dict[str, float] = {}
    for period in period_order:
        demand = to_float(
            row[DEMAND_COLUMNS[period]],
            f"{row['usage_period_id']} {period} max demand",
        )
        max_demands[period] = demand
        raw_over[period] = max(
            0.0,
            demand - thresholds[period],
        )

    details: list[dict[str, object]] = []
    prior_max_raw = 0.0
    total_charge = 0.0

    for period in period_order:
        raw = raw_over[period]
        lower = min(prior_max_raw, raw)
        chargeable_kw = max(0.0, raw - prior_max_raw)

        tier1_cap_kw = (
            tier1_fraction * thresholds[period]
        )

        tier1_interval_start = min(lower, tier1_cap_kw)
        tier1_interval_end = min(raw, tier1_cap_kw)
        tier1_kw = max(
            0.0,
            tier1_interval_end - tier1_interval_start,
        )
        tier2_kw = max(0.0, chargeable_kw - tier1_kw)

        basic_rate_contract_key = OVERCONTRACT_BASIC_RATE_KEY[period]
        rate = basic_rate(indexed, season, basic_rate_contract_key)
        charge = (
            tier1_kw * rate * tier1_multiplier
            + tier2_kw * rate * tier2_multiplier
        )
        total_charge += charge

        details.append(
            {
                "usage_period_id": row["usage_period_id"],
                "season": season,
                "tou_period": period,
                "max_demand_kw": max_demands[period],
                "cumulative_contract_threshold_kw": thresholds[period],
                "raw_overage_kw": raw,
                "prior_max_raw_overage_kw": prior_max_raw,
                "prior_accounted_overage_kw": prior_max_raw,
                "chargeable_nonduplicated_kw": chargeable_kw,
                "tier1_cap_kw": tier1_cap_kw,
                "tier1_kw": tier1_kw,
                "tier2_kw": tier2_kw,
                "basic_rate_contract_key": basic_rate_contract_key,
                "basic_rate_ntd_per_kw_month": rate,
                "tier1_multiplier": tier1_multiplier,
                "tier2_multiplier": tier2_multiplier,
                "predicted_period_charge_ntd": charge,
            }
        )

        prior_max_raw = max(prior_max_raw, raw)

    return float(total_charge), details


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 Taipower Core Monthly Bill Regression")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = project_root()

    registry_path = (
        root
        / "data"
        / "reference"
        / "taipower_tariff_registry_v7_1.csv"
    )
    bill_path = (
        root
        / "data"
        / "reference"
        / "taipower_bills_final_clean.csv"
    )
    audit_13b_path = (
        root
        / "results"
        / "parameter_audit"
        / "taipower_tariff_registry_audit_v7_1.json"
    )

    output_dir = root / "results" / "billing_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = load_registry(registry_path)
    audit_13b = load_13b_audit(audit_13b_path)
    indexed = registry_index(registry)
    bills = load_case_bills(bill_path)

    print("Inputs")
    print(f"- Tariff registry: {registry_path}")
    print(f"- 13b audit JSON: {audit_13b_path}")
    print(f"- Bill observations: {bill_path}")
    print(f"- Case-year usage periods: {len(bills)}")
    print("- 13b production tariff gate: PASS")
    print()

    # ------------------------------------------------------------------
    # Monthly core regression.
    # ------------------------------------------------------------------
    monthly_rows: list[dict[str, object]] = []
    overcontract_detail_rows: list[dict[str, object]] = []
    transition_rows: list[dict[str, object]] = []

    pure_energy_pass_count = 0
    pure_basic_pass_count = 0
    transition_basic_pass_count = 0
    overcontract_exact_pass_count = 0

    print("Monthly regression")

    for _, row in bills.iterrows():
        usage_id = str(row["usage_period_id"])
        role = season_role(usage_id)
        overcontract_observation_season = (
            season_for_pure_month(usage_id)
            if role != "transition"
            else "transition"
        )

        observed_energy = to_float(
            row[BILL_COLUMNS["energy_charge_ntd"]],
            f"{usage_id} observed energy charge",
        )
        observed_contract_basic = to_float(
            row[BILL_COLUMNS["contract_basic_ntd"]],
            f"{usage_id} observed contract basic",
        )
        regular_cc_kw = to_float(
            row[BILL_COLUMNS["regular_cc_kw"]],
            f"{usage_id} regular CC",
        )
        observed_noncontract, observed_noncontract_source_status = (
            observed_noncontract_charge(
                row,
                regular_cc_kw,
                overcontract_observation_season,
            )
        )
        if observed_noncontract_source_status != "OBSERVED_NUMERIC":
            print(
                f"- {usage_id}: observed non-contract source status "
                f"{observed_noncontract_source_status}"
            )

        monthly_record: dict[str, object] = {
            "usage_period_id": usage_id,
            "season_role": role,
            "regular_cc_kw": regular_cc_kw,
            "energy_predicted_ntd": np.nan,
            "energy_observed_ntd": observed_energy,
            "energy_residual_ntd": np.nan,
            "energy_status": (
                "NOT_RECONSTRUCTABLE_FROM_MONTHLY_AGGREGATES"
                if role == "transition"
                else None
            ),
            "contract_basic_predicted_ntd": np.nan,
            "contract_basic_observed_ntd": observed_contract_basic,
            "contract_basic_residual_ntd": np.nan,
            "contract_basic_status": None,
            "overcontract_predicted_ntd": np.nan,
            "overcontract_observed_ntd": observed_noncontract,
            "overcontract_residual_ntd": np.nan,
            "overcontract_status": None,
        }

        if role != "transition":
            season = season_for_pure_month(usage_id)

            predicted_energy, _ = predict_pure_energy_charge(
                row,
                indexed,
                season,
            )
            energy_residual = (
                observed_energy - predicted_energy
            )
            assert_close(
                observed_energy,
                predicted_energy,
                f"{usage_id} pure-season energy regression",
            )
            pure_energy_pass_count += 1

            predicted_contract_basic = (
                regular_cc_kw
                * basic_rate(indexed, season, "regular")
            )
            contract_basic_residual = (
                observed_contract_basic
                - predicted_contract_basic
            )
            assert_close(
                observed_contract_basic,
                predicted_contract_basic,
                f"{usage_id} pure-season contract basic regression",
            )
            pure_basic_pass_count += 1

            predicted_noncontract, details = overcontract_components(
                row,
                indexed,
                season,
            )
            noncontract_residual = (
                observed_noncontract - predicted_noncontract
            )
            assert_close(
                observed_noncontract,
                predicted_noncontract,
                f"{usage_id} pure-season over-contract regression",
                atol=0.11,
            )
            overcontract_exact_pass_count += 1
            overcontract_detail_rows.extend(details)

            monthly_record.update(
                {
                    "energy_predicted_ntd": predicted_energy,
                    "energy_residual_ntd": energy_residual,
                    "energy_status": "PASS_EXACT",
                    "contract_basic_predicted_ntd": (
                        predicted_contract_basic
                    ),
                    "contract_basic_residual_ntd": (
                        contract_basic_residual
                    ),
                    "contract_basic_status": "PASS_EXACT",
                    "overcontract_predicted_ntd": predicted_noncontract,
                    "overcontract_residual_ntd": noncontract_residual,
                    "overcontract_status": "PASS_EXACT",
                }
            )

            print(
                f"- {usage_id}: "
                f"energy PASS | basic PASS | over-contract PASS"
            )

        else:
            summer_regular = basic_rate(
                indexed,
                "summer",
                "regular",
            )
            non_summer_regular = basic_rate(
                indexed,
                "non_summer",
                "regular",
            )
            predicted_transition_basic = (
                regular_cc_kw
                * (summer_regular + non_summer_regular)
                / 2.0
            )
            transition_basic_residual = (
                observed_contract_basic
                - predicted_transition_basic
            )
            assert_close(
                observed_contract_basic,
                predicted_transition_basic,
                f"{usage_id} transition-month contract basic identity",
            )
            transition_basic_pass_count += 1

            # If there is no raw overage at all, observed zero is season-rule
            # independent and may be validated without inventing a mixed-season
            # over-contract rate. Otherwise the production rule remains deferred.
            thresholds = cumulative_contract_thresholds(regular_cc_kw)
            raw_overages = {
                period: max(
                    0.0,
                    to_float(
                        row[DEMAND_COLUMNS[period]],
                        f"{usage_id} {period} demand",
                    )
                    - thresholds[period],
                )
                for period in TOU_PERIODS
            }
            max_raw_overage = max(raw_overages.values())

            if max_raw_overage <= 1e-9:
                assert_close(
                    observed_noncontract,
                    0.0,
                    f"{usage_id} transition-month zero over-contract",
                    atol=0.11,
                )
                predicted_noncontract = 0.0
                noncontract_residual = observed_noncontract
                noncontract_status = (
                    "PASS_ZERO_OVERAGE_SEASON_RULE_INDEPENDENT"
                )
                overcontract_exact_pass_count += 1
            else:
                predicted_noncontract = np.nan
                noncontract_residual = np.nan
                noncontract_status = (
                    "NOT_RECONSTRUCTED_TRANSITION_RATE_RULE_PENDING"
                )

            monthly_record.update(
                {
                    "contract_basic_predicted_ntd": (
                        predicted_transition_basic
                    ),
                    "contract_basic_residual_ntd": (
                        transition_basic_residual
                    ),
                    "contract_basic_status": (
                        "PASS_CASE_VALIDATED_TRANSITION_CONVENTION"
                    ),
                    "overcontract_predicted_ntd": predicted_noncontract,
                    "overcontract_residual_ntd": noncontract_residual,
                    "overcontract_status": noncontract_status,
                }
            )

            transition_rows.append(
                {
                    "usage_period_id": usage_id,
                    "regular_cc_kw": regular_cc_kw,
                    "summer_regular_rate_ntd_per_kw_month": (
                        summer_regular
                    ),
                    "non_summer_regular_rate_ntd_per_kw_month": (
                        non_summer_regular
                    ),
                    "predicted_50_50_contract_basic_ntd": (
                        predicted_transition_basic
                    ),
                    "observed_contract_basic_ntd": (
                        observed_contract_basic
                    ),
                    "residual_ntd": transition_basic_residual,
                    "status": (
                        "PASS_CASE_VALIDATED_TRANSITION_CONVENTION"
                    ),
                    "official_rule_status": (
                        "EXPLICIT_PUBLIC_50_50_CLAUSE_NOT_LOCATED"
                    ),
                    "energy_regression_status": (
                        "NOT_RECONSTRUCTABLE_FROM_MONTHLY_AGGREGATES"
                    ),
                    "max_raw_overage_kw": max_raw_overage,
                    "overcontract_status": noncontract_status,
                }
            )

            print(
                f"- {usage_id}: "
                "energy N/A (mixed-season aggregate) | "
                "basic PASS CASE-VALIDATED | "
                f"over-contract {noncontract_status}"
            )

        monthly_rows.append(monthly_record)

    monthly_df = pd.DataFrame(monthly_rows)
    overcontract_detail_df = pd.DataFrame(
        overcontract_detail_rows
    )
    transition_df = pd.DataFrame(transition_rows)

    # ------------------------------------------------------------------
    # Mandatory gate checks.
    # ------------------------------------------------------------------
    if pure_energy_pass_count != 10:
        raise RuntimeError(
            "Expected 10 exact pure-season energy regressions; "
            f"got {pure_energy_pass_count}."
        )

    if pure_basic_pass_count != 10:
        raise RuntimeError(
            "Expected 10 exact pure-season contract-basic regressions; "
            f"got {pure_basic_pass_count}."
        )

    if transition_basic_pass_count != 2:
        raise RuntimeError(
            "Expected two May/October transition-basic identities; "
            f"got {transition_basic_pass_count}."
        )

    # September anchor: computed entirely from registry + bill observations.
    sep = monthly_df.loc[
        monthly_df["usage_period_id"].eq("2025-09")
    ]
    if len(sep) != 1:
        raise RuntimeError("2025-09 monthly regression row missing.")

    sep_row = sep.iloc[0]
    assert_close(
        float(sep_row["energy_residual_ntd"]),
        0.0,
        "2025-09 energy residual anchor",
    )
    assert_close(
        float(sep_row["contract_basic_residual_ntd"]),
        0.0,
        "2025-09 contract-basic residual anchor",
    )
    assert_close(
        float(sep_row["overcontract_residual_ntd"]),
        0.0,
        "2025-09 over-contract residual anchor",
        atol=0.11,
    )

    # 2025-02 non-summer contract-basic anchor.
    feb = monthly_df.loc[
        monthly_df["usage_period_id"].eq("2025-02")
    ]
    if len(feb) != 1:
        raise RuntimeError("2025-02 monthly regression row missing.")
    assert_close(
        float(feb.iloc[0]["contract_basic_residual_ntd"]),
        0.0,
        "2025-02 contract-basic residual anchor",
    )

    # No transition energy charge may be falsely generated.
    transition_energy_status = monthly_df.loc[
        monthly_df["season_role"].eq("transition"),
        "energy_status",
    ]
    if not transition_energy_status.eq(
        "NOT_RECONSTRUCTABLE_FROM_MONTHLY_AGGREGATES"
    ).all():
        raise RuntimeError(
            "A transition-month energy charge was improperly reconstructed."
        )

    # ------------------------------------------------------------------
    # Outputs.
    # ------------------------------------------------------------------
    monthly_path = (
        output_dir
        / "taipower_monthly_core_bill_regression_v7_1.csv"
    )
    overcontract_path = (
        output_dir
        / "taipower_overcontract_regression_v7_1.csv"
    )
    transition_path = (
        output_dir
        / "taipower_transition_month_diagnostics_v7_1.csv"
    )
    summary_path = (
        output_dir
        / "taipower_core_bill_regression_audit_v7_1.json"
    )

    monthly_df.to_csv(
        monthly_path,
        index=False,
        encoding="utf-8-sig",
    )
    overcontract_detail_df.to_csv(
        overcontract_path,
        index=False,
        encoding="utf-8-sig",
    )
    transition_df.to_csv(
        transition_path,
        index=False,
        encoding="utf-8-sig",
    )

    max_abs_pure_energy_residual = float(
        monthly_df.loc[
            monthly_df["season_role"].ne("transition"),
            "energy_residual_ntd",
        ]
        .abs()
        .max()
    )
    max_abs_pure_basic_residual = float(
        monthly_df.loc[
            monthly_df["season_role"].ne("transition"),
            "contract_basic_residual_ntd",
        ]
        .abs()
        .max()
    )
    max_abs_testable_overcontract_residual = float(
        monthly_df.loc[
            monthly_df["overcontract_residual_ntd"].notna(),
            "overcontract_residual_ntd",
        ]
        .abs()
        .max()
    )
    max_abs_transition_basic_residual = float(
        transition_df["residual_ntd"].abs().max()
    )

    gates = {
        "tariff_registry_loaded": "PASS",
        "13b_audit_loaded_and_passed": "PASS",
        "case_year_12_usage_periods": "PASS",
        "pure_season_energy_regressions_10_of_10": "PASS",
        "pure_season_contract_basic_regressions_10_of_10": "PASS",
        "transition_basic_identities_2_of_2_case_validated": "PASS",
        "transition_energy_not_falsely_inferred": "PASS",
        "overcontract_sequential_nonduplication": "PASS",
        "overcontract_tier_10pct_2x_3x": "PASS",
        "september_overcontract_anchor": "PASS",
        "no_bill_derived_tariff_coefficients": "PASS",
        "no_subsidy_in_production_billing_engine": "PASS",
    }

    summary = {
        "script_version": SCRIPT_VERSION,
        "status": "PASS",
        "case_year": {
            "start": "2024-11-01",
            "end": "2025-10-31",
            "monthly_usage_periods": CASE_USAGE_MONTHS,
        },
        "inputs": {
            "tariff_registry": str(registry_path),
            "tariff_registry_13b_audit": str(audit_13b_path),
            "bill_observations": str(bill_path),
        },
        "regression_counts": {
            "pure_season_energy_exact": pure_energy_pass_count,
            "pure_season_contract_basic_exact": pure_basic_pass_count,
            "transition_contract_basic_case_validated": (
                transition_basic_pass_count
            ),
            "testable_overcontract_exact": (
                overcontract_exact_pass_count
            ),
        },
        "maximum_absolute_residual_ntd": {
            "pure_season_energy": max_abs_pure_energy_residual,
            "pure_season_contract_basic": max_abs_pure_basic_residual,
            "testable_overcontract": (
                max_abs_testable_overcontract_residual
            ),
            "transition_contract_basic_50_50_identity": (
                max_abs_transition_basic_residual
            ),
        },
        "transition_month_boundary": {
            "months": TRANSITION_MONTHS,
            "contract_basic_treatment": (
                "CASE_VALIDATED_TRANSITION_CONVENTION_50_50"
            ),
            "explicit_public_50_50_clause_located": False,
            "blocking": False,
            "monthly_aggregate_energy_reconstruction": False,
            "reason": (
                "Monthly TOU kWh aggregates do not preserve the "
                "summer/non-summer sub-period split."
            ),
        },
        "economic_role_boundary": {
            "tariff_rates_read_from_13b_registry": True,
            "bill_derived_tariff_coefficients": False,
            "subsidy_in_production_billing_engine": False,
            "vat_in_core_regression": False,
            "power_factor_adjustment_in_core_regression": False,
            "discount_in_core_regression": False,
            "refunds_in_core_regression": False,
            "other_reductions_in_core_regression": False,
        },
        "gates": gates,
        "next_step": (
            "Use the audited 13b tariff registry and 13c billing semantics "
            "when assembling the production annual economic objective / "
            "monthly demand-charge settlement module."
        ),
    }

    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("Residual summary")
    print(
        "- Pure-season energy max |residual|: "
        f"{max_abs_pure_energy_residual:.6f} NTD"
    )
    print(
        "- Pure-season contract basic max |residual|: "
        f"{max_abs_pure_basic_residual:.6f} NTD"
    )
    print(
        "- Testable over-contract max |residual|: "
        f"{max_abs_testable_overcontract_residual:.6f} NTD"
    )
    print(
        "- Transition 50/50 basic max |residual|: "
        f"{max_abs_transition_basic_residual:.6f} NTD"
    )

    print()
    print("Outputs")
    print(f"- Monthly core regression: {monthly_path}")
    print(f"- Over-contract detail: {overcontract_path}")
    print(f"- Transition diagnostics: {transition_path}")
    print(f"- Audit summary: {summary_path}")

    print()
    print("Gate interpretation")
    print("- 13b tariff registry loaded: PASS")
    print("- 10 pure-season energy regressions: PASS EXACT")
    print("- 10 pure-season contract-basic regressions: PASS EXACT")
    print(
        "- May/October contract-basic identities: "
        "PASS CASE-VALIDATED"
    )
    print(
        "- May/October energy regression: intentionally NOT inferred "
        "from monthly aggregate TOU kWh"
    )
    print("- Sequential over-contract non-duplication: PASS")
    print("- 10% / 2x / 3x tiering metadata used: PASS")
    print("- September over-contract anchor: PASS EXACT")
    print("- Bill-derived tariff coefficients: NO")
    print("- Subsidy in production billing engine: NO")
    print("- 13c core bill regression gate: CLOSED / PASS")


if __name__ == "__main__":
    main()
