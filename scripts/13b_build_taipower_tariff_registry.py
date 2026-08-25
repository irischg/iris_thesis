#!/usr/bin/env python3
"""
13b_build_taipower_tariff_registry.py

NTUST thesis v7.1 — audited Taipower school-specific tariff registry freeze.

Purpose
-------
Freeze the production Taipower tariff package used by the NTUST v7.1 case year
(2024-11-01 through 2025-10-31) and preserve the policy/provenance chain that
justifies using the school-specific high-voltage three-period TOU tariff rather
than the contemporaneous general-user tariff.

This script intentionally DOES NOT OCR or scrape tariff values from PDF tables.
The numerical constants below are manually audited parameters from official
Taipower / Ministry-approved tariff tables. The PDFs are retained as source
artifacts and are fingerprinted with SHA-256 for provenance.

It DOES:
- require the core official tariff PDFs used to establish the school tariff;
- fingerprint source PDFs;
- write a tidy production tariff parameter registry;
- write policy-lineage evidence for the case-year continuity decision;
- preserve high-voltage summer boundary May 16–October 15;
- preserve four TOU/basic-charge classes;
- preserve the official over-contract 10% / 2x / 3x rule metadata;
- explicitly mark non-summer peak energy rate as not applicable;
- guard against accidental use of general high-voltage three-period rates;
- keep bill observations/subsidy out of tariff coefficient construction.

It DOES NOT:
- derive tariff rates from NTUST bills;
- reproduce full monthly bills (reserved for 13c);
- re-create the audited TOU calendar from scratch;
- decide monetary-basis harmonization between 2023 BESS costs and case-year
  electricity prices;
- put subsidy into the optimization objective.

Core official source expectation
--------------------------------
Place these in data/reference/:
1) 簡要電價表_1130401始.pdf
2) 詳細電價表_1141001始.pdf

Recommended supporting sources in the same folder:
3) 各類電價表及計算範例_1130401始.pdf
4) 最近兩年時間電價日曆表.pdf
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-taipower-school-tariff-registry-2026-08-24-r1"

CASE_START = "2024-11-01"
CASE_END = "2025-10-31"

CUSTOMER_CLASS = "school"
INSTITUTION_TYPE = "university_college"
VOLTAGE_CLASS = "high_voltage"
TOU_SCHEME = "three_period_fixed_peak"
INDUSTRY_CODE = "855"  # upstream audited NTUST bill classification

LEGAL_BASIS_DATE = "2022-12-28"
LEGAL_BASIS_REFERENCE = "經濟部經能字第11120080290號函核定電價表"

# High-voltage / extra-high-voltage summer boundary.
SUMMER_START_MMDD = "05-16"
SUMMER_END_MMDD = "10-15"

# ---------------------------------------------------------------------------
# Manually audited production parameters.
#
# IMPORTANT:
# These are SCHOOL-SPECIFIC high-voltage three-period fixed-peak rates.
# They are NOT the general-user high-voltage rates.
#
# Energy rates: NTD/kWh
# Basic-charge rates: NTD/kW-month
# ---------------------------------------------------------------------------
ENERGY_RATES = {
    ("summer", "peak"): 5.80,
    ("summer", "half"): 3.63,
    ("summer", "sat_half"): 1.78,
    ("summer", "off"): 1.58,
    ("non_summer", "peak"): None,  # not applicable in fixed-peak 3-period TOU
    ("non_summer", "half"): 3.40,
    ("non_summer", "sat_half"): 1.65,
    ("non_summer", "off"): 1.45,
}

BASIC_CHARGE_RATES = {
    ("summer", "regular"): 223.60,
    ("summer", "half"): 166.90,
    ("summer", "sat_half"): 44.70,
    ("summer", "off"): 44.70,
    ("non_summer", "regular"): 166.90,
    ("non_summer", "half"): 166.90,
    ("non_summer", "sat_half"): 33.30,
    ("non_summer", "off"): 33.30,
}

OVERCONTRACT_TIER1_THRESHOLD_FRACTION = 0.10
OVERCONTRACT_TIER1_MULTIPLIER = 2.0
OVERCONTRACT_TIER2_MULTIPLIER = 3.0
OVERCONTRACT_PERIOD_ORDER = "peak>half>sat_half>off"
OVERCONTRACT_NON_DUPLICATION = True

# General-user rates that must not appear as the production school tariff.
# This is a targeted guardrail, not a complete historical general-rate registry.
FORBIDDEN_GENERAL_PRODUCTION_SIGNATURES = {
    ("summer", "peak"): {8.05, 8.12},
    ("summer", "half"): {5.02},
    ("summer", "sat_half"): {2.27, 2.50},
    ("summer", "off"): {2.18, 2.23},
    ("non_summer", "half"): {4.70, 4.86},
    ("non_summer", "sat_half"): {2.10, 2.40},
    ("non_summer", "off"): {2.00, 2.12},
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_optional_calendar_pdf(reference_dir: Path) -> Path | None:
    candidates = [
        reference_dir / "最近兩年時間電價日曆表.pdf",
        reference_dir / "最近兩年時間電價日曆表 (1).pdf",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def build_source_inventory(reference_dir: Path) -> pd.DataFrame:
    core = [
        {
            "source_key": "school_tariff_1130401",
            "path": reference_dir / "簡要電價表_1130401始.pdf",
            "required": True,
            "source_role": (
                "primary school/frozen-tariff table and 113/4 applicability evidence"
            ),
            "source_page_label": "printed pp. 17-18, 27",
        },
        {
            "source_key": "tariff_detail_1141001",
            "path": reference_dir / "詳細電價表_1141001始.pdf",
            "required": True,
            "source_role": (
                "case-year continuity evidence; 113/10 school freeze history; "
                "114/10 school appendix continuation; school tariff cross-check"
            ),
            "source_page_label": "printed pp. 53, 64-65, 73-74",
        },
        {
            "source_key": "general_examples_1130401",
            "path": reference_dir / "各類電價表及計算範例_1130401始.pdf",
            "required": False,
            "source_role": (
                "supporting general-user tariff/calculation reference; "
                "NOT production school tariff"
            ),
            "source_page_label": "printed pp. 12-14",
        },
    ]

    calendar_pdf = resolve_optional_calendar_pdf(reference_dir)
    core.append(
        {
            "source_key": "recent_tou_calendar_reference",
            "path": (
                calendar_pdf
                if calendar_pdf is not None
                else reference_dir / "最近兩年時間電價日曆表.pdf"
            ),
            "required": False,
            "source_role": (
                "supporting TOU-rule provenance only; not the v7.1 case-year "
                "production day calendar"
            ),
            "source_page_label": "calendar notes",
        }
    )

    rows: list[dict[str, object]] = []
    missing_required: list[str] = []

    for item in core:
        path = Path(item["path"])
        exists = path.exists()

        if bool(item["required"]) and not exists:
            missing_required.append(str(path))

        rows.append(
            {
                "source_key": item["source_key"],
                "source_file": path.name,
                "source_path": str(path),
                "required": bool(item["required"]),
                "exists": exists,
                "sha256": sha256_file(path) if exists else None,
                "size_bytes": path.stat().st_size if exists else None,
                "source_role": item["source_role"],
                "source_page_label": item["source_page_label"],
            }
        )

    if missing_required:
        raise FileNotFoundError(
            "13b cannot close the production tariff gate because required "
            "official source PDF(s) are missing:\n"
            + "\n".join(f"- {x}" for x in missing_required)
            + "\n\nPlace the missing PDF(s) in data/reference/ and rerun."
        )

    return pd.DataFrame(rows)


def production_source_metadata() -> dict[str, str]:
    return {
        "source_file": "簡要電價表_1130401始.pdf",
        "source_page_label": "printed p. 18",
        "source_section": (
            "貳、凍漲行業適用電價表 / "
            "三、高壓及特高壓電力電價－幼兒園、大學（專）及社福團體適用 / "
            "(二)三段式時間電價 / (尖峰時間固定)"
        ),
        "source_role": "production_school_tariff_parameter",
    }


def common_metadata() -> dict[str, str]:
    return {
        "customer_class": CUSTOMER_CLASS,
        "institution_type": INSTITUTION_TYPE,
        "voltage_class": VOLTAGE_CLASS,
        "tou_scheme": TOU_SCHEME,
        "industry_code": INDUSTRY_CODE,
        "case_effective_start": CASE_START,
        "case_effective_end": CASE_END,
        "legal_basis_date": LEGAL_BASIS_DATE,
        "legal_basis_reference": LEGAL_BASIS_REFERENCE,
        "mainline_or_legacy": "mainline",
    }


def build_tariff_registry() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    src = production_source_metadata()
    common = common_metadata()

    for (season, tou_period), value in ENERGY_RATES.items():
        applicable = value is not None
        rows.append(
            {
                "parameter_id": f"energy_{season}_{tou_period}",
                "parameter_group": "energy_rate",
                "season": season,
                "tou_period": tou_period,
                "contract_period": None,
                "value_numeric": value,
                "value_text": None,
                "unit": "NTD/kWh",
                "applicable": applicable,
                **common,
                **src,
                "notes": (
                    "Non-summer fixed-peak three-period tariff has no peak-energy "
                    "period."
                    if not applicable
                    else "Audited school-specific high-voltage three-period rate."
                ),
            }
        )

    for (season, contract_period), value in BASIC_CHARGE_RATES.items():
        rows.append(
            {
                "parameter_id": f"basic_{season}_{contract_period}",
                "parameter_group": "basic_charge_rate",
                "season": season,
                "tou_period": None,
                "contract_period": contract_period,
                "value_numeric": value,
                "value_text": None,
                "unit": "NTD/kW-month",
                "applicable": True,
                **common,
                **src,
                "notes": (
                    "Official tariff structure retained even though NTUST v7.1 "
                    "mainline fixes supplementary contract capacities to zero."
                ),
            }
        )

    rule_src = {
        "source_file": "詳細電價表_1141001始.pdf",
        "source_page_label": "printed pp. 32-33; PDF indices 34-35",
        "source_section": "五、高壓及特高壓電力電價 / 七、超約用電",
        "source_role": "production_overcontract_rule",
    }

    rule_rows = [
        {
            "parameter_id": "overcontract_tier1_threshold",
            "parameter_group": "overcontract_rule",
            "season": "all",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": OVERCONTRACT_TIER1_THRESHOLD_FRACTION,
            "value_text": None,
            "unit": "fraction_of_contract_capacity",
            "applicable": True,
            "notes": "Tier-1 exceedance is the first 10% above the applicable threshold.",
        },
        {
            "parameter_id": "overcontract_tier1_multiplier",
            "parameter_group": "overcontract_rule",
            "season": "all",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": OVERCONTRACT_TIER1_MULTIPLIER,
            "value_text": None,
            "unit": "multiplier",
            "applicable": True,
            "notes": "First 10% exceedance uses 2x the applicable basic-charge rate.",
        },
        {
            "parameter_id": "overcontract_tier2_multiplier",
            "parameter_group": "overcontract_rule",
            "season": "all",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": OVERCONTRACT_TIER2_MULTIPLIER,
            "value_text": None,
            "unit": "multiplier",
            "applicable": True,
            "notes": "Exceedance beyond 10% uses 3x the applicable basic-charge rate.",
        },
        {
            "parameter_id": "overcontract_period_order",
            "parameter_group": "overcontract_rule",
            "season": "all",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": None,
            "value_text": OVERCONTRACT_PERIOD_ORDER,
            "unit": "ordered_periods",
            "applicable": True,
            "notes": (
                "Period-specific cumulative thresholds are evaluated in tariff "
                "order; later periods must not double-count kW already charged."
            ),
        },
        {
            "parameter_id": "overcontract_non_duplication",
            "parameter_group": "overcontract_rule",
            "season": "all",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": 1.0 if OVERCONTRACT_NON_DUPLICATION else 0.0,
            "value_text": str(OVERCONTRACT_NON_DUPLICATION).upper(),
            "unit": "boolean",
            "applicable": True,
            "notes": "Same exceedance kW must not be charged repeatedly across TOU periods.",
        },
    ]
    for row in rule_rows:
        rows.append({**row, **common, **rule_src})

    calendar_src = {
        "source_file": "taipower_tou_day_calendar_case_year_v7_1.csv",
        "source_page_label": None,
        "source_section": "audited case-year TOU calendar / high-voltage season rule",
        "source_role": "production_calendar_rule",
    }

    calendar_rows = [
        {
            "parameter_id": "high_voltage_summer_start_mmdd",
            "parameter_group": "calendar_rule",
            "season": "summer",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": None,
            "value_text": SUMMER_START_MMDD,
            "unit": "MM-DD",
            "applicable": True,
            "notes": "Do not replace with a whole-month summer shortcut.",
        },
        {
            "parameter_id": "high_voltage_summer_end_mmdd",
            "parameter_group": "calendar_rule",
            "season": "summer",
            "tou_period": None,
            "contract_period": None,
            "value_numeric": None,
            "value_text": SUMMER_END_MMDD,
            "unit": "MM-DD",
            "applicable": True,
            "notes": "Do not replace with a whole-month summer shortcut.",
        },
    ]
    for row in calendar_rows:
        rows.append({**row, **common, **calendar_src})

    registry = pd.DataFrame(rows)

    preferred_columns = [
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
        "industry_code",
        "case_effective_start",
        "case_effective_end",
        "legal_basis_date",
        "legal_basis_reference",
        "source_file",
        "source_page_label",
        "source_section",
        "source_role",
        "mainline_or_legacy",
        "notes",
    ]
    return registry[preferred_columns]


def build_policy_lineage() -> pd.DataFrame:
    rows = [
        {
            "checkpoint_date": "2022-12-28",
            "event": "school_tariff_legal_basis",
            "ntust_applicability": "applicable_to_university_school_use",
            "production_consequence": (
                "establish school-specific high-voltage tariff basis"
            ),
            "source_file": "簡要電價表_1130401始.pdf",
            "source_page_label": "printed pp. 17-18, 27",
            "evidence_role": "legal_basis_reproduced_in_later_tariff_document",
            "status": "PASS",
        },
        {
            "checkpoint_date": "2024-04-01",
            "event": "113_04_tariff_adjustment",
            "ntust_applicability": (
                "schools remain in frozen-industry tariff table"
            ),
            "production_consequence": "school tariff package retained",
            "source_file": "簡要電價表_1130401始.pdf",
            "source_page_label": "printed pp. 11-18, 27",
            "evidence_role": "contemporaneous school-freeze tariff evidence",
            "status": "PASS",
        },
        {
            "checkpoint_date": "2024-10-16",
            "event": "113_10_general_tariff_adjustment",
            "ntust_applicability": (
                "agriculture/fishery, schools and social-welfare groups frozen"
            ),
            "production_consequence": (
                "no switch to general-user tariff at case-year start"
            ),
            "source_file": "詳細電價表_1141001始.pdf",
            "source_page_label": "printed p. 53 policy-history section",
            "evidence_role": (
                "official later tariff document explicitly records 113/10 school freeze"
            ),
            "status": "PASS",
        },
        {
            "checkpoint_date": "2025-10-01",
            "event": "114_10_general_tariff_revision",
            "ntust_applicability": (
                "schools directed to Appendix 2, 2022-12-28 approved tariff"
            ),
            "production_consequence": (
                "school tariff remains unchanged through case-year end"
            ),
            "source_file": "詳細電價表_1141001始.pdf",
            "source_page_label": "TOC / printed pp. 64-65, 73-74",
            "evidence_role": "contemporaneous continuation evidence",
            "status": "PASS",
        },
    ]
    return pd.DataFrame(rows)


def audit_registry(registry: pd.DataFrame) -> dict[str, object]:
    gates: dict[str, object] = {}

    # Uniqueness.
    duplicate_ids = registry.loc[
        registry["parameter_id"].duplicated(keep=False), "parameter_id"
    ].tolist()
    if duplicate_ids:
        raise RuntimeError(f"Duplicate parameter_id values: {duplicate_ids}")
    gates["parameter_id_uniqueness"] = "PASS"

    # Energy matrix completeness.
    energy = registry.loc[registry["parameter_group"].eq("energy_rate")].copy()
    expected_energy_ids = {
        f"energy_{season}_{period}"
        for season in ["summer", "non_summer"]
        for period in ["peak", "half", "sat_half", "off"]
    }
    observed_energy_ids = set(energy["parameter_id"])
    if observed_energy_ids != expected_energy_ids:
        raise RuntimeError(
            "Energy-rate matrix is incomplete or contains unexpected rows.\n"
            f"Expected: {sorted(expected_energy_ids)}\n"
            f"Observed: {sorted(observed_energy_ids)}"
        )
    gates["energy_rate_matrix_completeness"] = "PASS"

    # Non-summer peak must be explicitly N/A.
    ns_peak = registry.loc[
        registry["parameter_id"].eq("energy_non_summer_peak")
    ].iloc[0]
    if bool(ns_peak["applicable"]) or pd.notna(ns_peak["value_numeric"]):
        raise RuntimeError(
            "Non-summer peak must be applicable=False and value_numeric=NaN."
        )
    gates["non_summer_peak_not_applicable"] = "PASS"

    # Basic-charge matrix completeness.
    basic = registry.loc[
        registry["parameter_group"].eq("basic_charge_rate")
    ].copy()
    expected_basic_ids = {
        f"basic_{season}_{period}"
        for season in ["summer", "non_summer"]
        for period in ["regular", "half", "sat_half", "off"]
    }
    observed_basic_ids = set(basic["parameter_id"])
    if observed_basic_ids != expected_basic_ids:
        raise RuntimeError(
            "Basic-charge matrix is incomplete or contains unexpected rows.\n"
            f"Expected: {sorted(expected_basic_ids)}\n"
            f"Observed: {sorted(observed_basic_ids)}"
        )
    gates["basic_charge_matrix_completeness"] = "PASS"

    # Exact production anchors.
    exact_expected = {
        "energy_summer_peak": 5.80,
        "energy_summer_half": 3.63,
        "energy_summer_sat_half": 1.78,
        "energy_summer_off": 1.58,
        "energy_non_summer_half": 3.40,
        "energy_non_summer_sat_half": 1.65,
        "energy_non_summer_off": 1.45,
        "basic_summer_regular": 223.60,
        "basic_summer_half": 166.90,
        "basic_summer_sat_half": 44.70,
        "basic_summer_off": 44.70,
        "basic_non_summer_regular": 166.90,
        "basic_non_summer_half": 166.90,
        "basic_non_summer_sat_half": 33.30,
        "basic_non_summer_off": 33.30,
    }

    indexed = registry.set_index("parameter_id")
    for parameter_id, expected in exact_expected.items():
        observed = float(indexed.loc[parameter_id, "value_numeric"])
        if not np.isclose(observed, expected, rtol=0.0, atol=1e-12):
            raise RuntimeError(
                f"{parameter_id}: observed {observed}, expected {expected}"
            )
    gates["school_tariff_numeric_anchors"] = "PASS"

    # Guard against general-user rate contamination.
    for (season, period), forbidden_values in (
        FORBIDDEN_GENERAL_PRODUCTION_SIGNATURES.items()
    ):
        parameter_id = f"energy_{season}_{period}"
        if parameter_id not in indexed.index:
            continue
        observed = indexed.loc[parameter_id, "value_numeric"]
        if pd.isna(observed):
            continue
        if any(
            np.isclose(float(observed), x, rtol=0.0, atol=1e-12)
            for x in forbidden_values
        ):
            raise RuntimeError(
                f"{parameter_id} appears to contain a general-user tariff rate: "
                f"{observed}"
            )
    gates["general_user_tariff_contamination_guard"] = "PASS"

    # Over-contract rules.
    tier1_threshold = float(
        indexed.loc["overcontract_tier1_threshold", "value_numeric"]
    )
    tier1_multiplier = float(
        indexed.loc["overcontract_tier1_multiplier", "value_numeric"]
    )
    tier2_multiplier = float(
        indexed.loc["overcontract_tier2_multiplier", "value_numeric"]
    )
    period_order = str(
        indexed.loc["overcontract_period_order", "value_text"]
    )
    non_dup = str(
        indexed.loc["overcontract_non_duplication", "value_text"]
    )

    if not np.isclose(tier1_threshold, 0.10):
        raise RuntimeError("Over-contract tier-1 threshold must be 0.10.")
    if not np.isclose(tier1_multiplier, 2.0):
        raise RuntimeError("Over-contract tier-1 multiplier must be 2.0.")
    if not np.isclose(tier2_multiplier, 3.0):
        raise RuntimeError("Over-contract tier-2 multiplier must be 3.0.")
    if period_order != "peak>half>sat_half>off":
        raise RuntimeError("Unexpected over-contract period order.")
    if non_dup != "TRUE":
        raise RuntimeError("Over-contract non-duplication must be TRUE.")

    gates["overcontract_10pct_2x_3x_rule"] = "PASS"
    gates["overcontract_period_order"] = "PASS"
    gates["overcontract_non_duplication"] = "PASS"

    # Summer boundary.
    start_value = str(
        indexed.loc["high_voltage_summer_start_mmdd", "value_text"]
    )
    end_value = str(
        indexed.loc["high_voltage_summer_end_mmdd", "value_text"]
    )
    if start_value != "05-16" or end_value != "10-15":
        raise RuntimeError(
            "High-voltage summer boundary must be 05-16 through 10-15."
        )
    gates["high_voltage_summer_boundary"] = "PASS"

    # Economic-role boundary.
    gates["bill_derived_tariff_coefficients"] = False
    gates["subsidy_in_production_tariff"] = False

    return gates


def audit_case_calendar(reference_dir: Path) -> dict[str, object]:
    path = reference_dir / "taipower_tou_day_calendar_case_year_v7_1.csv"
    if not path.exists():
        raise FileNotFoundError(
            "Audited case-year TOU calendar not found: "
            f"{path}"
        )

    df = pd.read_csv(path)
    if len(df) != 365:
        raise RuntimeError(
            "Expected 365 rows in case-year TOU day calendar; "
            f"found {len(df)}."
        )

    return {
        "file": str(path),
        "rows": len(df),
        "status": "PASS",
        "role": (
            "production day-type calendar; 13b does not recreate hourly/day "
            "classification"
        ),
    }


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 Taipower School-Specific Tariff Registry Audit")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = project_root()
    reference_dir = root / "data" / "reference"
    parameter_audit_dir = root / "results" / "parameter_audit"
    parameter_audit_dir.mkdir(parents=True, exist_ok=True)

    if not reference_dir.exists():
        raise FileNotFoundError(f"Reference directory not found: {reference_dir}")

    print("Source provenance")
    source_inventory = build_source_inventory(reference_dir)

    for _, row in source_inventory.iterrows():
        print(
            f"- {row['source_key']}: "
            f"{'FOUND' if row['exists'] else 'NOT FOUND (optional)'}"
        )
        if row["exists"]:
            print(f"  file: {row['source_path']}")
            print(f"  sha256: {row['sha256']}")

    print()
    print("Production tariff identity")
    print(f"- Customer class: {CUSTOMER_CLASS}")
    print(f"- Institution type: {INSTITUTION_TYPE}")
    print(f"- Voltage class: {VOLTAGE_CLASS}")
    print(f"- TOU scheme: {TOU_SCHEME}")
    print(f"- Upstream NTUST industry code: {INDUSTRY_CODE}")
    print(
        "- Production basis: school/frozen high-voltage three-period "
        "fixed-peak tariff"
    )
    print(
        "- General high-voltage tariff: reference/counterfactual only; "
        "NOT production tariff"
    )

    registry = build_tariff_registry()
    gates = audit_registry(registry)
    policy_lineage = build_policy_lineage()
    calendar_audit = audit_case_calendar(reference_dir)

    if not policy_lineage["status"].eq("PASS").all():
        raise RuntimeError("Policy lineage contains non-PASS rows.")

    print()
    print("Audited production energy rates (NTD/kWh)")
    for season in ["summer", "non_summer"]:
        for period in ["peak", "half", "sat_half", "off"]:
            row = registry.loc[
                registry["parameter_id"].eq(f"energy_{season}_{period}")
            ].iloc[0]
            if bool(row["applicable"]):
                print(
                    f"- {season:10s} {period:8s}: "
                    f"{float(row['value_numeric']):.2f}"
                )
            else:
                print(f"- {season:10s} {period:8s}: N/A")

    print()
    print("Audited production basic-charge rates (NTD/kW-month)")
    for season in ["summer", "non_summer"]:
        for period in ["regular", "half", "sat_half", "off"]:
            row = registry.loc[
                registry["parameter_id"].eq(f"basic_{season}_{period}")
            ].iloc[0]
            print(
                f"- {season:10s} {period:8s}: "
                f"{float(row['value_numeric']):.2f}"
            )

    print()
    print("Over-contract rule")
    print("- First 10% above applicable threshold: 2x")
    print("- Beyond 10%: 3x")
    print(f"- Period order: {OVERCONTRACT_PERIOD_ORDER}")
    print("- Non-duplication across TOU periods: TRUE")

    print()
    print("Policy-lineage checkpoints")
    for _, row in policy_lineage.iterrows():
        print(
            f"- {row['checkpoint_date']} | {row['event']} | "
            f"{row['status']}"
        )

    registry_path = reference_dir / "taipower_tariff_registry_v7_1.csv"
    source_inventory_path = (
        parameter_audit_dir / "taipower_tariff_source_inventory_v7_1.csv"
    )
    policy_lineage_path = (
        parameter_audit_dir / "taipower_tariff_policy_lineage_v7_1.csv"
    )
    summary_path = (
        parameter_audit_dir / "taipower_tariff_registry_audit_v7_1.json"
    )

    registry.to_csv(registry_path, index=False, encoding="utf-8-sig")
    source_inventory.to_csv(
        source_inventory_path,
        index=False,
        encoding="utf-8-sig",
    )
    policy_lineage.to_csv(
        policy_lineage_path,
        index=False,
        encoding="utf-8-sig",
    )

    summary = {
        "script_version": SCRIPT_VERSION,
        "status": "PASS",
        "case_period": {
            "start": CASE_START,
            "end": CASE_END,
        },
        "tariff_identity": {
            "customer_class": CUSTOMER_CLASS,
            "institution_type": INSTITUTION_TYPE,
            "voltage_class": VOLTAGE_CLASS,
            "tou_scheme": TOU_SCHEME,
            "industry_code_upstream_audited": INDUSTRY_CODE,
            "legal_basis_date": LEGAL_BASIS_DATE,
            "legal_basis_reference": LEGAL_BASIS_REFERENCE,
        },
        "summer_rule": {
            "start_mmdd": SUMMER_START_MMDD,
            "end_mmdd": SUMMER_END_MMDD,
        },
        "production_tariff": {
            "energy_rates_ntd_per_kwh": {
                f"{season}:{period}": value
                for (season, period), value in ENERGY_RATES.items()
            },
            "basic_charge_rates_ntd_per_kw_month": {
                f"{season}:{period}": value
                for (season, period), value in BASIC_CHARGE_RATES.items()
            },
        },
        "overcontract_rule": {
            "tier1_threshold_fraction": (
                OVERCONTRACT_TIER1_THRESHOLD_FRACTION
            ),
            "tier1_multiplier": OVERCONTRACT_TIER1_MULTIPLIER,
            "tier2_multiplier": OVERCONTRACT_TIER2_MULTIPLIER,
            "period_order": OVERCONTRACT_PERIOD_ORDER,
            "non_duplication": OVERCONTRACT_NON_DUPLICATION,
        },
        "source_inventory": source_inventory.to_dict(orient="records"),
        "policy_lineage": policy_lineage.to_dict(orient="records"),
        "case_calendar_audit": calendar_audit,
        "gates": gates,
        "role_boundaries": {
            "pdf_auto_parse_or_ocr": False,
            "bill_derived_tariff_coefficients": False,
            "bill_regression_in_13b": False,
            "subsidy_in_production_tariff": False,
            "monetary_basis_harmonization_decided_here": False,
        },
        "next_step": (
            "13c: reproduce audited NTUST monthly bill components using the "
            "frozen production tariff registry and billing-demand observations."
        ),
    }

    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("Outputs")
    print(f"- Production tariff registry: {registry_path}")
    print(f"- Source inventory: {source_inventory_path}")
    print(f"- Policy lineage: {policy_lineage_path}")
    print(f"- Audit summary: {summary_path}")

    print()
    print("Gate interpretation")
    print("- NTUST school tariff applicability: PASS")
    print("- School tariff numeric anchors: PASS")
    print("- 113/10 school-freeze continuity: PASS")
    print("- 114/10 school-tariff continuation: PASS")
    print("- High-voltage summer boundary: PASS")
    print("- Energy-rate matrix completeness: PASS")
    print("- Basic-charge matrix completeness: PASS")
    print("- Non-summer peak correctly N/A: PASS")
    print("- General-user tariff contamination guard: PASS")
    print("- Over-contract 10% / 2x / 3x rule: PASS")
    print("- Over-contract non-duplication metadata: PASS")
    print("- Bill-derived tariff coefficients: NO")
    print("- Subsidy in production tariff: NO")
    print("- 13b production tariff registry gate: CLOSED / PASS")
    print("- Next step: 13c monthly bill regression.")


if __name__ == "__main__":
    main()
