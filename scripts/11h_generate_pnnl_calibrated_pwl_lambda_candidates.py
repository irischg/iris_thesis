from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-pnnl-calibrated-pwl-lambda-candidates-2026-08-22"

# Full technical provenance from PNNL Table 4.2 as locked by v7.1 registry.
FULL_TECHNICAL_POINTS = (
    # effective_DOD, cycles_to_EOL
    (0.05, 192000.0),
    (0.30, 32000.0),
    (0.60, 8000.0),
    (0.70, 6000.0),
    (0.80, 4800.0),
)

# Production merged breakpoint set allowed by v7.1 because adjacent
# intervals have equal slopes under the fixed technical calibration.
PRODUCTION_BREAKPOINTS = (0.0, 0.30, 0.60, 0.80)

EXPECTED_POWER_BRACKETS_MW = (1.0, 10.0)
EXPECTED_CURRENCY = "NTD"
EXPECTED_BASE_YEAR = 2023
EXPECTED_FX_RATE = 31.150


def g_value(crep_ntd_per_kwh: float, dod: float) -> float:
    """
    G(delta) = C_rep / N(delta), for delta > 0.
    Units: NTD per installed battery-side kWh for a cycle reaching delta.
    """
    n_lookup = {d: n for d, n in FULL_TECHNICAL_POINTS}
    if dod == 0.0:
        return 0.0
    if dod not in n_lookup:
        raise KeyError(f"No cycle-life calibration point for DOD={dod}")
    return crep_ntd_per_kwh / n_lookup[dod]


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 PNNL-Calibrated PWL Degradation Lambda Audit")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = Path(__file__).resolve().parents[1]

    input_path = (
        root
        / "results"
        / "parameter_audit"
        / "pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv"
    )

    output_dir = root / "results" / "parameter_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            "Script 11g NTD-2023 candidate package output not found:\n"
            f"{input_path}"
        )

    df = pd.read_csv(input_path)

    required_columns = {
        "package_id",
        "power_scale_bracket_mw",
        "normalized_currency",
        "normalized_currency_base_year",
        "fx_ntd_per_usd",
        "crep_ntd_per_kwh",
        "mainline_selected",
    }

    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise RuntimeError(
            f"11g output is missing required columns: {missing}"
        )

    if len(df) != 2:
        raise RuntimeError(
            f"Expected exactly 2 candidate brackets; found {len(df)}."
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

    if not (
        df["normalized_currency"].astype(str) == EXPECTED_CURRENCY
    ).all():
        raise RuntimeError("Expected normalized currency = NTD.")

    if not (
        df["normalized_currency_base_year"].astype(int)
        == EXPECTED_BASE_YEAR
    ).all():
        raise RuntimeError("Expected normalized currency base year = 2023.")

    if not np.allclose(
        df["fx_ntd_per_usd"].astype(float).to_numpy(),
        EXPECTED_FX_RATE,
        atol=1e-12,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"Expected FX rate {EXPECTED_FX_RATE:.3f} NTD/USD."
        )

    print("Technical cycle-life calibration")
    for dod, cycles in FULL_TECHNICAL_POINTS:
        print(
            f"- effective DOD={dod:.2f} | cycles to EOL={cycles:,.0f}"
        )

    print()
    print("Production breakpoint rule")
    print("- Full five-point technical provenance is preserved.")
    print("- Equal-slope adjacent intervals are mathematically merged.")
    print("- Effective production breakpoints: 0, 0.30, 0.60, 0.80")
    print("- lambda_k units: NTD per battery-side discharged kWh")
    print(
        "- AC-side discharge must later be converted to battery-side "
        "using p_dis * dt / eta_d."
    )
    print("- eta_d must NOT be embedded again inside lambda_k.")

    full_rows: list[dict] = []
    segment_rows: list[dict] = []
    package_rows: list[dict] = []

    for _, row in df.sort_values("power_scale_bracket_mw").iterrows():
        power = float(row["power_scale_bracket_mw"])
        crep = float(row["crep_ntd_per_kwh"])
        package_id = str(row["package_id"])

        print()
        print(f"{power:g} MW bracket")
        print(f"- C_rep={crep:.6f} NTD/kWh")

        # Full technical G(delta) provenance.
        g_full = {0.0: 0.0}
        for dod, cycles in FULL_TECHNICAL_POINTS:
            g = crep / cycles
            g_full[dod] = g
            full_rows.append(
                {
                    "package_id": package_id,
                    "power_scale_bracket_mw": power,
                    "crep_ntd_per_kwh": crep,
                    "effective_dod": dod,
                    "cycles_to_eol": cycles,
                    "G_ntd_per_installed_kwh": g,
                    "source_role": "PNNL_TABLE_4_2_TECHNICAL_PROVENANCE",
                }
            )
            print(
                f"  G({dod:.2f})={g:.9f} NTD/installed-kWh"
            )

        # Verify exact equal slopes that justify merging:
        original_intervals = (
            (0.0, 0.05),
            (0.05, 0.30),
            (0.30, 0.60),
            (0.60, 0.70),
            (0.70, 0.80),
        )

        original_slopes = []
        for lo, hi in original_intervals:
            slope = (g_full[hi] - g_full[lo]) / (hi - lo)
            original_slopes.append(slope)

        if not np.isclose(
            original_slopes[0],
            original_slopes[1],
            atol=1e-12,
            rtol=0.0,
        ):
            raise RuntimeError(
                f"{power:g} MW: 0-0.05 and 0.05-0.30 slopes "
                "are not equal; merge is invalid."
            )

        if not np.isclose(
            original_slopes[3],
            original_slopes[4],
            atol=1e-12,
            rtol=0.0,
        ):
            raise RuntimeError(
                f"{power:g} MW: 0.60-0.70 and 0.70-0.80 slopes "
                "are not equal; merge is invalid."
            )

        production_intervals = (
            (0.0, 0.30),
            (0.30, 0.60),
            (0.60, 0.80),
        )

        lambdas = []

        for k, (lo, hi) in enumerate(production_intervals, start=1):
            lambda_k = (g_full[hi] - g_full[lo]) / (hi - lo)
            lambdas.append(lambda_k)

            segment_rows.append(
                {
                    "package_id": package_id,
                    "power_scale_bracket_mw": power,
                    "segment_k": k,
                    "dod_lower": lo,
                    "dod_upper": hi,
                    "segment_width_fraction": hi - lo,
                    "lambda_ntd_per_battery_side_discharged_kwh": lambda_k,
                    "crep_ntd_per_kwh": crep,
                    "currency_base_year": 2023,
                    "mainline_selected": False,
                    "status": "BRACKET_SPECIFIC_CANDIDATE_NOT_MAINLINE_SELECTED",
                }
            )

            print(
                f"- lambda_{k} [{lo:.2f},{hi:.2f}] "
                f"= {lambda_k:.9f} "
                "NTD/battery-side discharged kWh"
            )

        # Under this locked technical calibration, ratios should be 1:3:4.
        ratio_2 = lambdas[1] / lambdas[0]
        ratio_3 = lambdas[2] / lambdas[0]

        if not np.isclose(ratio_2, 3.0, atol=1e-12, rtol=0.0):
            raise RuntimeError(
                f"{power:g} MW lambda_2/lambda_1 != 3."
            )

        if not np.isclose(ratio_3, 4.0, atol=1e-12, rtol=0.0):
            raise RuntimeError(
                f"{power:g} MW lambda_3/lambda_1 != 4."
            )

        package_rows.append(
            {
                "package_id": package_id,
                "power_scale_bracket_mw": power,
                "crep_ntd_per_kwh": crep,
                "lambda_1_ntd_per_battery_side_kwh": lambdas[0],
                "lambda_2_ntd_per_battery_side_kwh": lambdas[1],
                "lambda_3_ntd_per_battery_side_kwh": lambdas[2],
                "lambda_ratio": "1:3:4",
                "production_breakpoints": "0,0.30,0.60,0.80",
                "currency": "NTD",
                "currency_base_year": 2023,
                "mainline_selected": False,
                "status": "PWL_CANDIDATE_PACKAGE_READY_BRACKET_NOT_SELECTED",
            }
        )

    full_df = pd.DataFrame(full_rows)
    segment_df = pd.DataFrame(segment_rows)
    package_df = pd.DataFrame(package_rows)

    full_path = (
        output_dir
        / "pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv"
    )
    full_df.to_csv(full_path, index=False, encoding="utf-8-sig")

    segment_path = (
        output_dir
        / "pnnl_calibrated_pwl_lambda_candidates_by_bracket.csv"
    )
    segment_df.to_csv(segment_path, index=False, encoding="utf-8-sig")

    package_path = (
        output_dir
        / "pnnl_calibrated_pwl_degradation_candidate_packages.csv"
    )
    package_df.to_csv(package_path, index=False, encoding="utf-8-sig")

    audit_path = (
        output_dir
        / "pnnl_calibrated_pwl_lambda_candidate_audit.txt"
    )

    audit_lines = [
        f"Script version: {SCRIPT_VERSION}",
        "NTUST v7.1 PNNL-Calibrated PWL Degradation Lambda Audit",
        "",
        f"Input: {input_path}",
        "",
        "Technical calibration source locked by v7.1:",
        "- effective DOD 0.05 -> 192,000 cycles",
        "- effective DOD 0.30 -> 32,000 cycles",
        "- effective DOD 0.60 -> 8,000 cycles",
        "- effective DOD 0.70 -> 6,000 cycles",
        "- effective DOD 0.80 -> 4,800 cycles",
        "",
        "Economic derivation:",
        "- G(0)=0",
        "- G(delta)=C_rep/N(delta), delta>0",
        "- lambda_k=[G(b_k)-G(b_{k-1})]/[b_k-b_{k-1}]",
        "- production b=(0,0.30,0.60,0.80)",
        "",
        "Unit convention:",
        "- lambda_k = NTD per battery-side discharged kWh",
        "- objective later applies lambda_k * p_dis * dt / eta_d",
        "- do not embed eta_d into lambda_k and divide by eta_d again",
        "",
        "Guardrails:",
        "- lambda_k values are thesis-derived, not PNNL-published coefficients.",
        "- full five-point PNNL technical provenance is preserved.",
        "- equal-slope adjacent intervals are merged mathematically only.",
        "- 1 MW and 10 MW remain separate candidate cost brackets.",
        "- no mainline bracket is selected here.",
        "- Harry-era hard-coded lambda values are not used.",
        "",
        "Gate interpretation:",
        "- PWL technical calibration: FROZEN",
        "- bracket-specific lambda candidates: GENERATED",
        "- battery-side unit convention: FROZEN",
        "- mainline 1 MW vs 10 MW bracket: NOT SELECTED",
        "- next phase: implement intertemporal segment-energy states and unit tests",
    ]

    audit_path.write_text(
        "\n".join(audit_lines),
        encoding="utf-8",
    )

    print()
    print("Outputs")
    print(f"- Full G(delta) provenance: {full_path}")
    print(f"- Segment lambda candidates: {segment_path}")
    print(f"- Candidate degradation packages: {package_path}")
    print(f"- Audit summary: {audit_path}")

    print()
    print("Gate interpretation")
    print("- PWL lambda derivation: PASS")
    print("- Full PNNL technical provenance: PRESERVED")
    print("- Effective production breakpoints: 0, 0.30, 0.60, 0.80")
    print("- Mainline 1 MW vs 10 MW bracket: NOT SELECTED")
    print("- Next step: Xu-adapted intertemporal segment-state implementation.")


if __name__ == "__main__":
    main()
