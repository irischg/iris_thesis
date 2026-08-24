#!/usr/bin/env python3
"""
13a_profile_taipower_bill_economic_fields_r1.py

NTUST thesis v7.1 — corrected Taipower bill economic-field /
subsidy-boundary audit.

Revision purpose
----------------
The first 13a used broad regex matching and therefore produced false
AMBIGUOUS/MISSING flags even though the current clean CSV already contains
the relevant exact fields.

This revision uses the audited clean-CSV schema directly.

It DOES:
- verify the exact 31-column economic/billing schema needed here;
- extract the 2025-09 usage-period row;
- reproduce known audited 2025-09 bill anchors from exact columns;
- distinguish core tariff/billing fields from realized-payment/subsidy fields;
- report whether subsidy alone reconciles Original Total Amount to Total Amount;
- explicitly flag that "Other Reductions" is aggregated in the clean CSV.

It DOES NOT:
- create production Taipower tariff coefficients;
- treat bill observations as tariff rates;
- decide an inflation/monetary-basis harmonization rule;
- place subsidy inside the optimization objective.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-taipower-bill-economic-field-profile-2026-08-22-r1"

SEP_USAGE_START = pd.Timestamp("2025-09-01")
SEP_USAGE_END = pd.Timestamp("2025-09-30")

EXACT_FIELD_MAP = {
    "regular_cc_kw": "Contract Capacity CP (kW)",
    "billed_peak_max_kw": "Max Demand - Peak (kW)",
    "billed_half_max_kw": "Max Demand - Semi-peak (kW)",
    "billed_sat_half_max_kw": "Max Demand - Sat Semi-peak (kW)",
    "billed_offpeak_max_kw": "Max Demand - Off-peak (kW)",
    "basic_charge_contract_ntd": "Basic Charge (Contract) (NTD)",
    "basic_charge_noncontract_ntd": "Basic Charge (Non-contract) (NTD)",
    "energy_charge_ntd": "Variable/Energy Charge (NTD)",
    "discount_ntd": "Discount (NTD)",
    "power_factor_adjust_ntd": "Power Factor Adjust (NTD)",
    "adjustments_refunds_ntd": "Adjustments/Refunds (NTD)",
    "other_reductions_ntd": "Other Reductions (NTD)",
    "subtotal_excl_vat_ntd": "Subtotal (excl. VAT) (NTD)",
    "vat_ntd": "VAT (NTD)",
    "total_amount_ntd": "Total Amount (NTD)",
    "original_total_amount_ntd": "Original Total Amount (NTD)",
    "subsidy_amount_ntd": "Subsidy Amount (NTD)",
    "notes": "Notes",
}

# Audited September 2025 usage-period anchors.
# These are observed bill values, NOT production tariff coefficients.
SEP_ANCHORS = {
    "regular_cc_kw": 5000.0,
    "billed_peak_max_kw": 4896.0,
    "billed_half_max_kw": 5016.0,
    "billed_sat_half_max_kw": 3352.0,
    "billed_offpeak_max_kw": 3776.0,
    "basic_charge_contract_ntd": 1118000.0,
    "basic_charge_noncontract_ntd": 5340.8,
    "energy_charge_ntd": 7309144.0,
    "discount_ntd": -255290.0,
    "power_factor_adjust_ntd": -122520.5,
    "adjustments_refunds_ntd": 169712.8,
    "subtotal_excl_vat_ntd": 7826648.0,
    "vat_ntd": 391332.0,
    "total_amount_ntd": 8217980.0,
    "original_total_amount_ntd": 12861131.0,
    "subsidy_amount_ntd": 4690426.0,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def to_float(value: object, label: str) -> float:
    if pd.isna(value):
        raise RuntimeError(f"{label}: missing value.")

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip().replace(",", "")
    try:
        return float(text)
    except ValueError as exc:
        raise RuntimeError(
            f"{label}: cannot parse numeric value {value!r}"
        ) from exc


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 Taipower Bill Economic-Field / Subsidy-Boundary Audit r1")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = project_root()
    input_path = root / "data" / "reference" / "taipower_bills_final_clean.csv"
    output_dir = root / "results" / "data_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Bill source not found: {input_path}")

    df = pd.read_csv(input_path)

    required = {
        "Period Start",
        "Period End",
        *EXACT_FIELD_MAP.values(),
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(
            "Current clean bill CSV is missing expected exact columns:\n"
            + "\n".join(f"- {x}" for x in missing)
        )

    print("Source")
    print(f"- File: {input_path}")
    print(f"- Rows: {len(df)}")
    print(f"- Columns: {len(df.columns)}")
    print("- Exact schema mapping: PASS")

    work = df.copy()
    work["Period Start"] = pd.to_datetime(work["Period Start"], errors="coerce")
    work["Period End"] = pd.to_datetime(work["Period End"], errors="coerce")

    if work[["Period Start", "Period End"]].isna().any().any():
        raise RuntimeError("Period Start/End contains unparsable dates.")

    sep = work.loc[
        work["Period Start"].eq(SEP_USAGE_START)
        & work["Period End"].eq(SEP_USAGE_END)
    ]

    if len(sep) != 1:
        raise RuntimeError(
            "Expected exactly one 2025-09 usage-period row; "
            f"found {len(sep)}."
        )

    row = sep.iloc[0]

    print()
    print("Exact field mapping")
    mapping_rows: list[dict[str, object]] = []

    for semantic, column in EXACT_FIELD_MAP.items():
        observed = row[column]

        if semantic == "notes":
            print(f"- {semantic}: column={column} | value={observed!r}")
            mapping_rows.append(
                {
                    "semantic_field": semantic,
                    "source_column": column,
                    "observed_2025_09": observed,
                    "anchor": None,
                    "anchor_status": "NOT_APPLICABLE",
                }
            )
            continue

        value = to_float(observed, semantic)
        expected = SEP_ANCHORS.get(semantic)

        if expected is None:
            status = "OBSERVED_NO_FIXED_ANCHOR"
        else:
            if not np.isclose(value, expected, rtol=0.0, atol=1e-6):
                raise RuntimeError(
                    f"{semantic}: September anchor mismatch. "
                    f"observed={value}, expected={expected}"
                )
            status = "PASS"

        print(
            f"- {semantic}: column={column} | "
            f"observed={value}"
            + (f" | anchor={expected} | {status}" if expected is not None
               else f" | {status}")
        )

        mapping_rows.append(
            {
                "semantic_field": semantic,
                "source_column": column,
                "observed_2025_09": value,
                "anchor": expected,
                "anchor_status": status,
            }
        )

    # Key payment/accounting fields.
    subtotal = to_float(
        row[EXACT_FIELD_MAP["subtotal_excl_vat_ntd"]],
        "subtotal_excl_vat_ntd",
    )
    vat = to_float(
        row[EXACT_FIELD_MAP["vat_ntd"]],
        "vat_ntd",
    )
    total = to_float(
        row[EXACT_FIELD_MAP["total_amount_ntd"]],
        "total_amount_ntd",
    )
    original = to_float(
        row[EXACT_FIELD_MAP["original_total_amount_ntd"]],
        "original_total_amount_ntd",
    )
    subsidy = to_float(
        row[EXACT_FIELD_MAP["subsidy_amount_ntd"]],
        "subsidy_amount_ntd",
    )
    other_reductions = to_float(
        row[EXACT_FIELD_MAP["other_reductions_ntd"]],
        "other_reductions_ntd",
    )

    print()
    print("Accounting identity diagnostics")

    subtotal_plus_vat = subtotal + vat
    print(
        f"- subtotal + VAT = {subtotal_plus_vat:.3f} NTD "
        f"| Total Amount = {total:.3f} NTD "
        f"| diff={subtotal_plus_vat - total:.3f}"
    )

    if not np.isclose(
        subtotal_plus_vat,
        total,
        rtol=0.0,
        atol=1.0,
    ):
        raise RuntimeError(
            "Subtotal + VAT does not reconcile to Total Amount "
            "within 1 NTD rounding tolerance."
        )

    simple_subsidy_net = original - subsidy
    subsidy_reconciliation_gap = total - simple_subsidy_net

    print(
        f"- Original Total - Subsidy = {simple_subsidy_net:.3f} NTD"
    )
    print(
        f"- Total Amount = {total:.3f} NTD"
    )
    print(
        "- Total - (Original - Subsidy) = "
        f"{subsidy_reconciliation_gap:.3f} NTD"
    )

    simple_subsidy_reconciles = bool(
        np.isclose(
            simple_subsidy_net,
            total,
            rtol=0.0,
            atol=1.0,
        )
    )

    if simple_subsidy_reconciles:
        print("- Subsidy-alone reconciliation: PASS")
    else:
        print(
            "- Subsidy-alone reconciliation: DOES NOT RECONCILE "
            "(diagnostic only; do not infer missing policy logic)"
        )

    print()
    print("Clean-CSV aggregation boundary")
    print(
        f"- Other Reductions (aggregated field) = "
        f"{other_reductions:.3f} NTD"
    )
    print(
        "- Separate demand-response / e-bill / meter-rental lines are NOT "
        "represented as separate columns in this clean CSV."
    )
    print(
        "- Therefore 13a-r1 will not reconstruct or invent those components."
    )

    print()
    print("Economic-role interpretation")
    print("- Core bill/tariff-observation fields: PRESERVED")
    print("- Total realized amount field: PRESERVED")
    print("- Original total amount field: PRESERVED")
    print("- Subsidy amount field: PRESERVED")
    print(
        "- Subsidy is NOT a TOU tariff coefficient and is NOT automatically "
        "placed in the optimization objective."
    )
    print(
        "- Official effective-date Taipower tariff evidence remains the "
        "source for production energy/basic/over-contract pricing."
    )
    print(
        "- Bill totals/subsidy remain validation and case-study accounting "
        "evidence unless a documented decision-dependent subsidy rule is found."
    )

    mapping_path = (
        output_dir
        / "taipower_bill_economic_field_exact_mapping_v7_1_r1.csv"
    )
    pd.DataFrame(mapping_rows).to_csv(
        mapping_path,
        index=False,
        encoding="utf-8-sig",
    )

    sep_source_path = (
        output_dir
        / "taipower_bill_2025_09_exact_economic_row_v7_1_r1.csv"
    )
    sep[[
        "Period Start",
        "Period End",
        *EXACT_FIELD_MAP.values(),
    ]].to_csv(
        sep_source_path,
        index=False,
        encoding="utf-8-sig",
    )

    summary = {
        "script_version": SCRIPT_VERSION,
        "status": "PASS",
        "source_file": str(input_path),
        "usage_period_anchor": "2025-09",
        "exact_schema_mapping": "PASS",
        "bill_anchor_reproduction": "PASS",
        "accounting_identity": {
            "subtotal_plus_vat_minus_total_ntd": (
                subtotal_plus_vat - total
            ),
            "simple_original_minus_subsidy_ntd": simple_subsidy_net,
            "total_amount_ntd": total,
            "total_minus_original_minus_subsidy_ntd": (
                subsidy_reconciliation_gap
            ),
            "subsidy_alone_reconciles": simple_subsidy_reconciles,
        },
        "aggregation_boundary": {
            "other_reductions_ntd": other_reductions,
            "separate_dr_ebill_meter_fields_preserved": False,
        },
        "role_boundary": {
            "production_tariff_source": (
                "official effective-date Taipower tariff evidence"
            ),
            "bill_observations_role": (
                "regression / validation / realized accounting"
            ),
            "subsidy_role": (
                "ex-post accounting / interpretation unless an explicit "
                "decision-dependent rule is independently documented"
            ),
            "subsidy_in_optimization_objective": False,
        },
        "pending_gates": [
            "production tariff coefficient registry",
            "September 2025 tariff bill regression",
            "2023 BESS cost vs case-year Taipower tariff monetary-basis harmonization",
        ],
    }

    summary_path = (
        output_dir
        / "taipower_bill_economic_boundary_v7_1_r1.json"
    )
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("Outputs")
    print(f"- Exact field mapping: {mapping_path}")
    print(f"- 2025-09 exact economic row: {sep_source_path}")
    print(f"- Boundary summary: {summary_path}")

    print()
    print("Gate interpretation")
    print("- Economic-field schema / anchor reproduction: PASS")
    print("- False MISSING/AMBIGUOUS results from old 13a: RESOLVED")
    print("- Subsidy accounting field: PRESERVED")
    print("- Subsidy in production objective: NO")
    print("- Production tariff coefficients: STILL PENDING")
    print("- Monetary-basis harmonization gate: STILL PENDING")
    print("- Next step: build/audit effective-date Taipower tariff registry.")


if __name__ == "__main__":
    main()
