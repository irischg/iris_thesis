from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-pnnl-v2024-lfp-fx-normalization-2026-08-22"

FX_NTD_PER_USD = 31.150
FX_YEAR = 2023
FX_SOURCE = "Central Bank of the Republic of China (Taiwan)"
FX_SOURCE_SERIES = (
    "Exchange Rates of the N.T. Dollar Against the U.S. Dollar, "
    "Interbank Spot Market Closing Rates, Annual Average"
)
FX_SOURCE_URL = "https://www.cbc.gov.tw/en/cp-480-1879-66035-2.html"
FX_RETRIEVED_DATE = "2026-08-22"

EXPECTED_SOURCE_YEAR = 2023
EXPECTED_CURRENCY = "USD"
EXPECTED_DURATION_WINDOW = "4,6,8,10"
EXPECTED_POWER_BRACKETS_MW = (1.0, 10.0)

DISCOUNT_RATE = 0.05
ANALYSIS_HORIZON_YR = 20


def crf(rate: float, years: int) -> float:
    return rate * (1.0 + rate) ** years / ((1.0 + rate) ** years - 1.0)


def assert_close(
    observed: float,
    expected: float,
    label: str,
    tol: float = 1e-9,
) -> None:
    if not np.isclose(observed, expected, atol=tol, rtol=0.0):
        raise RuntimeError(
            f"{label} mismatch: observed={observed}, expected={expected}"
        )


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 PNNL v2024 LFP USD->NTD FX Normalization Audit")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = Path(__file__).resolve().parents[1]

    input_path = (
        root
        / "results"
        / "parameter_audit"
        / "pnnl_v2024_lfp_usd2023_candidate_cost_packages.csv"
    )

    output_dir = root / "results" / "parameter_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            "Script 11f candidate-package output not found:\n"
            f"{input_path}"
        )

    df = pd.read_csv(input_path)

    required_columns = {
        "package_id",
        "source_year",
        "power_scale_bracket_mw",
        "duration_window_hr",
        "currency",
        "currency_base_year",
        "capex_C_E_usd_per_kwh",
        "capex_C_P_usd_per_kw",
        "fom_E_usd_per_kwh_year",
        "fom_P_usd_per_kw_year",
        "crep_usd_per_kwh",
        "discount_rate",
        "analysis_horizon_years",
        "annualized",
        "fx_normalized",
        "mainline_selected",
    }

    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise RuntimeError(
            f"11f candidate package is missing required columns: {missing}"
        )

    if len(df) != 2:
        raise RuntimeError(
            f"Expected exactly 2 candidate brackets from 11f; found {len(df)}."
        )

    observed_brackets = tuple(
        sorted(df["power_scale_bracket_mw"].astype(float).tolist())
    )
    if observed_brackets != EXPECTED_POWER_BRACKETS_MW:
        raise RuntimeError(
            "Unexpected power-scale brackets.\n"
            f"Expected: {EXPECTED_POWER_BRACKETS_MW}\n"
            f"Observed: {observed_brackets}"
        )

    if not (df["source_year"].astype(int) == EXPECTED_SOURCE_YEAR).all():
        raise RuntimeError("All source_year values must be 2023.")

    if not (df["currency"].astype(str) == EXPECTED_CURRENCY).all():
        raise RuntimeError("11f inputs must remain raw USD values.")

    if not (
        df["currency_base_year"].astype(int) == EXPECTED_SOURCE_YEAR
    ).all():
        raise RuntimeError("11f currency_base_year must be 2023.")

    if not (
        df["duration_window_hr"].astype(str) == EXPECTED_DURATION_WINDOW
    ).all():
        raise RuntimeError("11f duration window must be 4,6,8,10.")

    if df["annualized"].astype(bool).any():
        raise RuntimeError("11f input values must not already be annualized.")

    if df["fx_normalized"].astype(bool).any():
        raise RuntimeError("11f input values must not already be FX-normalized.")

    derived_crf = crf(DISCOUNT_RATE, ANALYSIS_HORIZON_YR)

    assert_close(
        derived_crf,
        0.08024258719069129,
        "CRF regression anchor",
        tol=1e-12,
    )

    print("FX normalization rule")
    print(f"- Source: {FX_SOURCE}")
    print(f"- Series: {FX_SOURCE_SERIES}")
    print(f"- Source URL: {FX_SOURCE_URL}")
    print(f"- Retrieved: {FX_RETRIEVED_DATE}")
    print(f"- FX year: {FX_YEAR}")
    print(f"- Annual average: {FX_NTD_PER_USD:.3f} NTD/USD")
    print("- PNNL cost vintage: 2023 USD")
    print("- Output monetary vintage: 2023 NTD")
    print("- Inflation/escalation adjustment: NONE")
    print(
        "- Rationale: preserve the PNNL 2023 monetary vintage and convert "
        "using the matching 2023 annual-average official FX rate."
    )
    print(
        "- This is a thesis normalization rule; the Central Bank supplies "
        "the FX data, not the thesis cost-model choice."
    )

    out = df.copy()

    # Preserve original USD values and add normalized NTD values.
    out["fx_source"] = FX_SOURCE
    out["fx_source_series"] = FX_SOURCE_SERIES
    out["fx_source_url"] = FX_SOURCE_URL
    out["fx_retrieved_date"] = FX_RETRIEVED_DATE
    out["fx_year"] = FX_YEAR
    out["fx_ntd_per_usd"] = FX_NTD_PER_USD
    out["fx_rule"] = "2023 annual-average NTD/USD matched to PNNL 2023 cost vintage"
    out["inflation_adjustment"] = "none"
    out["normalized_currency"] = "NTD"
    out["normalized_currency_base_year"] = 2023

    out["capex_C_E_ntd_per_kwh"] = (
        out["capex_C_E_usd_per_kwh"].astype(float) * FX_NTD_PER_USD
    )
    out["capex_C_P_ntd_per_kw"] = (
        out["capex_C_P_usd_per_kw"].astype(float) * FX_NTD_PER_USD
    )
    out["fom_E_ntd_per_kwh_year"] = (
        out["fom_E_usd_per_kwh_year"].astype(float) * FX_NTD_PER_USD
    )
    out["fom_P_ntd_per_kw_year"] = (
        out["fom_P_usd_per_kw_year"].astype(float) * FX_NTD_PER_USD
    )
    out["crep_ntd_per_kwh"] = (
        out["crep_usd_per_kwh"].astype(float) * FX_NTD_PER_USD
    )

    # CRF is applied only to CAPEX coefficients.
    # Keep both raw normalized CAPEX and annualized CAPEX coefficients explicit.
    out["crf"] = derived_crf
    out["annualized_capex_C_E_ntd_per_kwh_year"] = (
        out["capex_C_E_ntd_per_kwh"] * derived_crf
    )
    out["annualized_capex_C_P_ntd_per_kw_year"] = (
        out["capex_C_P_ntd_per_kw"] * derived_crf
    )

    out["fx_normalized"] = True
    out["annualized"] = False
    out["status"] = (
        "NTD2023_CANDIDATE_PACKAGE_FX_FROZEN_BRACKET_NOT_SELECTED"
    )

    output_path = (
        output_dir
        / "pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv"
    )
    out.to_csv(output_path, index=False, encoding="utf-8-sig")

    print()
    print("Normalized candidate packages")

    for _, row in out.sort_values("power_scale_bracket_mw").iterrows():
        p = float(row["power_scale_bracket_mw"])

        print()
        print(f"{p:g} MW bracket")
        print(
            f"- Raw CAPEX: "
            f"C_E={row['capex_C_E_ntd_per_kwh']:.6f} NTD/kWh, "
            f"C_P={row['capex_C_P_ntd_per_kw']:.6f} NTD/kW"
        )
        print(
            f"- Annualized CAPEX coefficients: "
            f"C_E={row['annualized_capex_C_E_ntd_per_kwh_year']:.6f} "
            f"NTD/kWh-yr, "
            f"C_P={row['annualized_capex_C_P_ntd_per_kw_year']:.6f} "
            f"NTD/kW-yr"
        )
        print(
            f"- Annual FOM: "
            f"FOM_E={row['fom_E_ntd_per_kwh_year']:.6f} NTD/kWh-yr, "
            f"FOM_P={row['fom_P_ntd_per_kw_year']:.6f} NTD/kW-yr"
        )
        print(
            f"- C_rep={row['crep_ntd_per_kwh']:.6f} NTD/kWh"
        )

    audit_path = (
        output_dir
        / "pnnl_v2024_lfp_ntd2023_fx_normalization_audit.txt"
    )

    audit_lines = [
        f"Script version: {SCRIPT_VERSION}",
        "NTUST v7.1 PNNL v2024 LFP USD->NTD FX Normalization Audit",
        "",
        f"Input: {input_path}",
        "",
        "Official FX evidence:",
        f"- Source: {FX_SOURCE}",
        f"- Series: {FX_SOURCE_SERIES}",
        f"- URL: {FX_SOURCE_URL}",
        f"- Retrieved: {FX_RETRIEVED_DATE}",
        f"- Year: {FX_YEAR}",
        f"- Annual average: {FX_NTD_PER_USD:.3f} NTD/USD",
        "",
        "Normalization rule:",
        "- PNNL v2024 cost values represent 2023 values.",
        "- Convert raw 2023 USD cost coefficients to 2023 NTD.",
        "- Use the official 2023 annual-average NTD/USD exchange rate.",
        "- No inflation/escalation adjustment is introduced.",
        "- Preserve both original USD fields and converted NTD fields.",
        "- 1 MW and 10 MW remain separate candidate brackets.",
        "- No interpolation and no mainline bracket selection occurs here.",
        "",
        "Annualization rule:",
        f"- discount rate r={DISCOUNT_RATE}",
        f"- analysis horizon n={ANALYSIS_HORIZON_YR} yr",
        f"- derived CRF={derived_crf:.10f}",
        "- CRF applies to normalized raw CAPEX only.",
        "- Annual FOM is NOT multiplied by CRF.",
        "- C_rep is NOT multiplied by CRF; it remains the cycling-wear economic basis.",
        "",
        "Gate interpretation:",
        "- USD->NTD source: FROZEN",
        "- FX numerical value: FROZEN AT 31.150 NTD/USD",
        "- Currency base year: FROZEN AS 2023",
        "- Inflation adjustment: NONE",
        "- Raw NTD-2023 CAPEX/FOM/C_rep packages: GENERATED",
        "- Annualized CAPEX coefficients: GENERATED",
        "- Mainline 1 MW vs 10 MW bracket: NOT SELECTED",
        "- lambda_k generation: NEXT",
    ]

    audit_path.write_text(
        "\n".join(audit_lines),
        encoding="utf-8",
    )

    print()
    print("Outputs")
    print(f"- NTD-2023 candidate packages: {output_path}")
    print(f"- FX audit summary: {audit_path}")

    print()
    print("Gate interpretation")
    print("- USD->NTD source/rule: FROZEN")
    print(f"- FX rate: {FX_NTD_PER_USD:.3f} NTD/USD")
    print("- Currency/base year: NTD-2023")
    print("- Inflation adjustment: NONE")
    print("- CAPEX annualization: GENERATED WITH CODE-DERIVED CRF")
    print("- Annual FOM: CONVERTED, NOT CRF-ANNUALIZED")
    print("- C_rep: CONVERTED, NOT CRF-ANNUALIZED")
    print("- Mainline 1 MW vs 10 MW bracket: NOT SELECTED")
    print("- Next step: generate bracket-specific PWL lambda_k candidates.")


if __name__ == "__main__":
    main()
