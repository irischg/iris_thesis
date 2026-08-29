#!/usr/bin/env python3
"""
15c_validate_production_eob_rainflow.py

NTUST thesis v7.2 — ex-post rainflow / cycle-depth validation of the frozen
production Economic-Only Benchmark (EOB).

Purpose
-------
Close the v7.2 post-solve degradation-validation gate before Layer A.

This script is deliberately POST-SOLVE ONLY:
- it reads the already-frozen Script-15b EOB dispatch/result;
- it does NOT call Gurobi;
- it does NOT change E_N, P_B, CC, dispatch, objective, or lambda_k;
- it does NOT replace the production intertemporal PWL degradation model;
- it does NOT invent a second nonlinear PNNL cycle-life interpolation.

Validation design
-----------------
The rainflow validator holds the degradation calibration fixed and changes only
cycle accounting:

Production optimization:
    Xu-derived intertemporal PWL segment discharge cost

Ex-post validation:
    closed annual SOC trajectory
    -> periodic rainflow cycle counting
    -> cycle DOD distribution
    -> same locked PNNL-calibrated G(delta) curve
    -> rainflow-implied annual degradation cost

This allows an independent check of cycle-depth accounting while preserving
the exact v7.2 PNNL + C_rep calibration lineage.

Future Layer A drivers should reuse:
    src.rainflow_validation_v7_2.validate_dispatch_rainflow
rather than reimplementing rainflow logic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-production-eob-rainflow-validation-2026-08-30-r1"

EXPECTED_FREEZE_STATUS = "PRODUCTION_EOB_FREEZE_PASS"
EXPECTED_MAINLINE_POWER_BRACKET_MW = 10.0
EXPECTED_PRODUCTION_BREAKPOINTS = (0.0, 0.30, 0.60, 0.80)
EXPECTED_TECHNICAL_DOD = (0.05, 0.30, 0.60, 0.70, 0.80)
EXPECTED_TECHNICAL_CYCLES = (
    192000.0,
    32000.0,
    8000.0,
    6000.0,
    4800.0,
)

EXPECTED_EOB_REFERENCE = {
    "E_N_kwh": 86.111111,
    "P_B_kw_ac": 62.0,
    "CC_regular_kw": 4399.137306,
    "objective_ntd2023_per_year": 66738326.341512,
    "degradation_ntd2023_per_year": 16168.568638,
}

EOB_REFERENCE_TOL = {
    "E_N_kwh": 0.10,
    "P_B_kw_ac": 0.10,
    "CC_regular_kw": 0.10,
    "objective_ntd2023_per_year": 100.0,
    "degradation_ntd2023_per_year": 0.10,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description=(
            "Validate the frozen v7.2 production EOB degradation ex post "
            "with periodic rainflow cycle counting."
        )
    )
    parser.add_argument(
        "--dispatch",
        type=Path,
        default=(
            root
            / "results"
            / "eob_production"
            / "eob_production_dispatch_v7_2.csv"
        ),
    )
    parser.add_argument(
        "--result-json",
        type=Path,
        default=(
            root
            / "results"
            / "eob_production"
            / "eob_production_result_v7_2.json"
        ),
    )
    parser.add_argument(
        "--freeze-audit",
        type=Path,
        default=(
            root
            / "results"
            / "eob_production"
            / "eob_production_freeze_audit_v7_2.json"
        ),
    )
    parser.add_argument(
        "--economic-interface",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "production_economic_interface_v7_2.json"
        ),
    )
    parser.add_argument(
        "--technical-provenance",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv"
        ),
        help=(
            "Script-11h retained PNNL Table 4.2 five-point technical "
            "cycle-life/G(delta) provenance."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "results" / "degradation_validation",
    )
    return parser.parse_args()


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def sha256_file(path: Path) -> str:
    require_file(path, "SHA-256 input")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    require_file(path, label)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc


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
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def all_freeze_gates_pass(audit: dict[str, Any]) -> bool:
    gates = audit.get("production_gates", {})
    return bool(gates) and all(
        str(value).startswith("PASS") for value in gates.values()
    )


def validate_15b_freeze_artifacts(
    result: dict[str, Any],
    freeze_audit: dict[str, Any],
) -> dict[str, Any]:
    gates: dict[str, str] = {}

    gates["15b_freeze_status"] = (
        "PASS"
        if freeze_audit.get("freeze_status") == EXPECTED_FREEZE_STATUS
        else "FAIL"
    )
    gates["15b_production_gates"] = (
        "PASS" if all_freeze_gates_pass(freeze_audit) else "FAIL"
    )

    gates["15b_result_has_solution"] = (
        "PASS" if bool(result.get("has_solution")) else "FAIL"
    )
    gates["15b_result_optimal"] = (
        "PASS" if result.get("status") == "OPTIMAL" else "FAIL"
    )
    gates["15b_result_binary"] = (
        "PASS" if result.get("mode") == "binary" else "FAIL"
    )

    mip_gap = result.get("mip_gap")
    gates["15b_mip_gap"] = (
        "PASS"
        if mip_gap is not None and float(mip_gap) <= 1e-6
        else "FAIL"
    )

    transition = result.get("transition_settlement", {})
    gates["15b_transition_finality"] = (
        "PASS"
        if transition.get("nonbinding_certificate")
        == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
        and transition.get("eob_finality")
        == "EXACT_WITH_RESPECT_TO_TRANSITION_RATE_AMBIGUITY"
        else "FAIL"
    )

    return gates


def validate_frozen_eob_reference(
    result: dict[str, Any],
) -> tuple[dict[str, str], dict[str, Any]]:
    sizing = result.get("sizing", {})
    costs = result.get("cost_components_ntd2023_per_year", {})

    actual = {
        "E_N_kwh": float(sizing.get("E_N_kwh", np.nan)),
        "P_B_kw_ac": float(sizing.get("P_B_kw_ac", np.nan)),
        "CC_regular_kw": float(sizing.get("CC_regular_kw", np.nan)),
        "objective_ntd2023_per_year": float(
            result.get("objective_ntd2023_per_year", np.nan)
        ),
        "degradation_ntd2023_per_year": float(
            costs.get("degradation", np.nan)
        ),
    }

    gates: dict[str, str] = {}
    detail: dict[str, Any] = {}

    for key, expected in EXPECTED_EOB_REFERENCE.items():
        value = actual[key]
        diff = abs(value - float(expected))
        tol = float(EOB_REFERENCE_TOL[key])
        passed = np.isfinite(value) and diff <= tol
        gates[f"frozen_reference_{key}"] = (
            "PASS" if passed else "FAIL"
        )
        detail[key] = {
            "expected": float(expected),
            "actual": value,
            "absolute_difference": diff,
            "tolerance": tol,
        }

    return gates, detail


def validate_source_hash_against_freeze(
    *,
    freeze_audit: dict[str, Any],
    label: str,
    current_path: Path,
) -> dict[str, Any]:
    """
    Verify a current upstream source still matches the file hashed by 15b.

    This is applied to the shared core and 14a economic interface. It is not
    applied to the 15b script itself, avoiding irrelevant Windows line-ending
    churn in a post-solve validator.
    """
    frozen = freeze_audit.get("source_hashes", {}).get(label)
    if not isinstance(frozen, dict):
        return {
            "status": "FAIL",
            "reason": f"15b freeze audit missing source hash label {label}",
        }

    expected = str(frozen.get("sha256", "")).lower()
    actual = sha256_file(current_path).lower()

    return {
        "status": "PASS" if actual == expected else "FAIL",
        "path": str(current_path),
        "sha256_frozen_15b": expected,
        "sha256_current": actual,
    }


def load_mainline_degradation_package(
    economic_interface: dict[str, Any],
) -> dict[str, Any]:
    if economic_interface.get("status") != "READY_FOR_EOB_OBJECTIVE_WIRING":
        raise RuntimeError(
            "14a production economic interface is not EOB-ready."
        )

    selector = economic_interface.get("package_selector", {})
    if selector.get("outcome_dependent_switching_allowed") is not False:
        raise RuntimeError(
            "14a interface does not block outcome-dependent cost-package switching."
        )

    mainline = selector.get("mainline")
    if not isinstance(mainline, dict):
        raise RuntimeError("14a mainline package is missing.")

    power = float(mainline.get("power_scale_bracket_mw", np.nan))
    if not np.isclose(
        power,
        EXPECTED_MAINLINE_POWER_BRACKET_MW,
        atol=1e-12,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"Expected 10 MW mainline package; observed {power}."
        )

    breakpoints = str(mainline.get("production_breakpoints", ""))
    if breakpoints != "0,0.30,0.60,0.80":
        raise RuntimeError(
            f"Unexpected production breakpoints in 14a: {breakpoints}"
        )

    required_numeric = [
        "crep_ntd2023_per_kwh",
        "lambda_1_ntd2023_per_battery_side_discharged_kwh",
        "lambda_2_ntd2023_per_battery_side_discharged_kwh",
        "lambda_3_ntd2023_per_battery_side_discharged_kwh",
    ]
    for key in required_numeric:
        value = float(mainline.get(key, np.nan))
        if not np.isfinite(value) or value <= 0.0:
            raise RuntimeError(
                f"Invalid/missing 14a mainline degradation field {key}: {value}"
            )

    return mainline


def load_technical_provenance(
    path: Path,
    *,
    mainline_package: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    require_file(path, "Script-11h PNNL technical provenance")
    df = pd.read_csv(path)

    required = {
        "power_scale_bracket_mw",
        "crep_ntd_per_kwh",
        "effective_dod",
        "cycles_to_eol",
        "G_ntd_per_installed_kwh",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(
            f"PNNL technical provenance missing columns: {missing}"
        )

    power = float(mainline_package["power_scale_bracket_mw"])
    selected = df.loc[
        np.isclose(
            pd.to_numeric(
                df["power_scale_bracket_mw"], errors="coerce"
            ).to_numpy(dtype=float),
            power,
            atol=1e-12,
            rtol=0.0,
        )
    ].copy()

    if len(selected) != len(EXPECTED_TECHNICAL_DOD):
        raise RuntimeError(
            "Expected exactly five retained PNNL Table 4.2 technical points "
            f"for {power:g} MW; found {len(selected)}."
        )

    selected["effective_dod"] = pd.to_numeric(
        selected["effective_dod"], errors="raise"
    )
    selected["cycles_to_eol"] = pd.to_numeric(
        selected["cycles_to_eol"], errors="raise"
    )
    selected["crep_ntd_per_kwh"] = pd.to_numeric(
        selected["crep_ntd_per_kwh"], errors="raise"
    )

    selected = selected.sort_values("effective_dod").reset_index(drop=True)

    dod = tuple(selected["effective_dod"].astype(float).tolist())
    cycles = tuple(selected["cycles_to_eol"].astype(float).tolist())

    dod_pass = np.allclose(
        np.asarray(dod),
        np.asarray(EXPECTED_TECHNICAL_DOD),
        atol=1e-12,
        rtol=0.0,
    )
    cycles_pass = np.allclose(
        np.asarray(cycles),
        np.asarray(EXPECTED_TECHNICAL_CYCLES),
        atol=1e-9,
        rtol=0.0,
    )

    crep_interface = float(
        mainline_package["crep_ntd2023_per_kwh"]
    )
    crep_values = selected["crep_ntd_per_kwh"].to_numpy(dtype=float)
    crep_pass = np.allclose(
        crep_values,
        crep_interface,
        atol=1e-9,
        rtol=0.0,
    )

    audit = {
        "status": (
            "PASS"
            if dod_pass and cycles_pass and crep_pass
            else "FAIL"
        ),
        "mainline_power_scale_bracket_mw": power,
        "technical_dod_exact": bool(dod_pass),
        "technical_cycles_exact": bool(cycles_pass),
        "crep_matches_14a_mainline": bool(crep_pass),
        "crep_ntd2023_per_kwh": crep_interface,
    }

    if audit["status"] != "PASS":
        raise RuntimeError(
            "PNNL Table 4.2 technical provenance does not match the locked "
            f"v7.2 calibration: {audit}"
        )

    return selected, audit


def write_outputs(
    output_dir: Path,
    validation: dict[str, Any],
    audit: dict[str, Any],
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "cycles_csv": output_dir / "eob_rainflow_cycles_v7_2.csv",
        "turning_points_csv": (
            output_dir / "eob_rainflow_turning_points_v7_2.csv"
        ),
        "depth_bins_csv": (
            output_dir / "eob_rainflow_depth_bins_v7_2.csv"
        ),
        "pwl_segments_csv": (
            output_dir / "eob_pwl_segment_degradation_reconciliation_v7_2.csv"
        ),
        "g_curve_csv": (
            output_dir / "eob_rainflow_g_curve_v7_2.csv"
        ),
        "summary_csv": (
            output_dir / "eob_rainflow_validation_summary_v7_2.csv"
        ),
        "audit_json": (
            output_dir / "eob_rainflow_validation_audit_v7_2.json"
        ),
    }

    validation["cycles"].to_csv(
        paths["cycles_csv"], index=False, encoding="utf-8-sig"
    )
    validation["turning_points"].to_csv(
        paths["turning_points_csv"], index=False, encoding="utf-8-sig"
    )
    validation["depth_bins"].to_csv(
        paths["depth_bins_csv"], index=False, encoding="utf-8-sig"
    )
    validation["pwl_segments"].to_csv(
        paths["pwl_segments_csv"], index=False, encoding="utf-8-sig"
    )
    validation["g_curve"].to_csv(
        paths["g_curve_csv"], index=False, encoding="utf-8-sig"
    )

    summary_row = dict(validation["summary"])
    for gate, status in validation["gates"].items():
        summary_row[f"gate__{gate}"] = status
    pd.DataFrame([summary_row]).to_csv(
        paths["summary_csv"], index=False, encoding="utf-8-sig"
    )

    audit["output_paths"] = {
        key: str(path) for key, path in paths.items()
    }
    paths["audit_json"].write_text(
        json.dumps(json_safe(audit), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {key: str(path) for key, path in paths.items()}


def main() -> int:
    args = parse_args()
    root = project_root()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Import physical constants from the exact shared production core so 15c
    # does not create a second independent set of BESS state semantics.
    from src.annual_design_model_v7_2 import (  # noqa: E402
        BREAKPOINTS,
        CORE_VERSION,
        ETA_C,
        ETA_D,
        SOC_MAX,
        SOC_MIN,
    )
    from src.rainflow_validation_v7_2 import (  # noqa: E402
        VALIDATOR_VERSION,
        run_internal_self_test,
        validate_dispatch_rainflow,
    )

    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.2 Production EOB Ex-Post Rainflow Validation")
    print(f"Shared annual-design core: {CORE_VERSION}")
    print(f"Rainflow validator: {VALIDATOR_VERSION}")
    print("- Gurobi optimization: NOT RUN")
    print("- EOB sizing/dispatch: READ-ONLY")
    print()

    for path, label in [
        (args.dispatch, "15b production dispatch"),
        (args.result_json, "15b production result"),
        (args.freeze_audit, "15b freeze audit"),
        (args.economic_interface, "14a economic interface"),
        (args.technical_provenance, "11h technical provenance"),
    ]:
        require_file(path, label)

    result = read_json(args.result_json, "15b production result")
    freeze_audit = read_json(args.freeze_audit, "15b freeze audit")
    economic_interface = read_json(
        args.economic_interface,
        "14a economic interface",
    )
    dispatch = pd.read_csv(args.dispatch)

    print("Preflight")

    freeze_gates = validate_15b_freeze_artifacts(
        result,
        freeze_audit,
    )
    for gate, status in freeze_gates.items():
        print(f"- {gate}: {status}")

    if any(value == "FAIL" for value in freeze_gates.values()):
        raise RuntimeError(
            "15b frozen EOB preflight failed; rainflow validation aborted."
        )

    reference_gates, reference_detail = validate_frozen_eob_reference(
        result
    )
    for gate, status in reference_gates.items():
        print(f"- {gate}: {status}")

    if any(value == "FAIL" for value in reference_gates.values()):
        raise RuntimeError(
            "15b EOB result no longer matches the frozen reference."
        )

    source_hash_core = validate_source_hash_against_freeze(
        freeze_audit=freeze_audit,
        label="shared_core",
        current_path=root / "src" / "annual_design_model_v7_2.py",
    )
    source_hash_economic = validate_source_hash_against_freeze(
        freeze_audit=freeze_audit,
        label="economic_interface_14a",
        current_path=args.economic_interface,
    )

    print(f"- shared_core_hash_vs_15b: {source_hash_core['status']}")
    print(
        "- economic_interface_hash_vs_15b: "
        f"{source_hash_economic['status']}"
    )

    if (
        source_hash_core["status"] != "PASS"
        or source_hash_economic["status"] != "PASS"
    ):
        raise RuntimeError(
            "A 15b source artifact changed after the frozen EOB solve."
        )

    mainline = load_mainline_degradation_package(
        economic_interface
    )
    technical, technical_audit = load_technical_provenance(
        args.technical_provenance,
        mainline_package=mainline,
    )

    print("- 10 MW mainline degradation package: PASS")
    print("- PNNL Table 4.2 technical provenance: PASS")

    algorithm_test = run_internal_self_test()
    print(
        "- rainflow algorithm internal self-test: "
        f"{algorithm_test['status']}"
    )
    if algorithm_test["status"] != "PASS":
        raise RuntimeError("Rainflow algorithm internal self-test failed.")

    if len(dispatch) != 8760:
        raise RuntimeError(
            f"15b dispatch rows={len(dispatch)}; expected 8760."
        )

    if "timestamp" not in dispatch.columns:
        raise RuntimeError("15b dispatch is missing timestamp.")
    timestamps = pd.to_datetime(
        dispatch["timestamp"],
        errors="coerce",
    )
    if timestamps.isna().any():
        raise RuntimeError("15b dispatch contains invalid timestamps.")

    expected_timeline = pd.date_range(
        "2024-11-01 00:00:00",
        periods=8760,
        freq="h",
    )
    if not pd.DatetimeIndex(timestamps).equals(expected_timeline):
        raise RuntimeError(
            "15b dispatch is not the exact formal 8760-hour case timeline."
        )
    print("- dispatch formal timeline: PASS")
    print()

    e_n = float(result["sizing"]["E_N_kwh"])
    degradation_cost = float(
        result["cost_components_ntd2023_per_year"]["degradation"]
    )
    battery_discharge_reference = float(
        result["annual_energy"]["battery_side_discharge_kwh"]
    )

    lambdas = [
        float(
            mainline[
                "lambda_1_ntd2023_per_battery_side_discharged_kwh"
            ]
        ),
        float(
            mainline[
                "lambda_2_ntd2023_per_battery_side_discharged_kwh"
            ]
        ),
        float(
            mainline[
                "lambda_3_ntd2023_per_battery_side_discharged_kwh"
            ]
        ),
    ]

    if not np.allclose(
        np.asarray(BREAKPOINTS, dtype=float),
        np.asarray(EXPECTED_PRODUCTION_BREAKPOINTS, dtype=float),
        atol=1e-12,
        rtol=0.0,
    ):
        raise RuntimeError(
            "Shared-core production breakpoints drifted from v7.2."
        )

    print("Running ex-post rainflow validation")
    validation = validate_dispatch_rainflow(
        dispatch,
        e_n_kwh=e_n,
        eta_c=float(ETA_C),
        eta_d=float(ETA_D),
        soc_min=float(SOC_MIN),
        soc_max=float(SOC_MAX),
        production_breakpoints=BREAKPOINTS,
        lambdas=lambdas,
        technical_points=technical,
        crep_ntd_per_kwh=float(
            mainline["crep_ntd2023_per_kwh"]
        ),
        pwl_cost_reference_ntd=degradation_cost,
        battery_side_discharge_reference_kwh=(
            battery_discharge_reference
        ),
        timestamps=timestamps,
    )

    summary = validation["summary"]
    gates = validation["gates"]

    print()
    print("Rainflow cycle-depth results")
    print(
        "- Turning points: "
        f"{summary['turning_point_count']}"
    )
    print(
        "- Rainflow records: "
        f"{summary['rainflow_record_count']}"
    )
    print(
        "- Weighted cycle count: "
        f"{summary['weighted_cycle_count']:.6f}"
    )
    print(
        "- Equivalent full cycles (nameplate-normalized): "
        f"{summary['equivalent_full_cycles_nameplate']:.6f}"
    )
    print(
        "- Equivalent full cycles (0.80 usable-window normalized): "
        f"{summary['equivalent_full_cycles_usable_window']:.6f}"
    )
    print(
        "- Maximum rainflow DOD: "
        f"{100.0 * summary['maximum_rainflow_DOD_fraction_nameplate']:.4f}%"
    )
    median = summary["median_rainflow_DOD_fraction_nameplate"]
    if median is not None:
        print(
            "- Weighted-median rainflow DOD: "
            f"{100.0 * median:.4f}%"
        )
    ewd = summary[
        "energy_weighted_rainflow_DOD_fraction_nameplate"
    ]
    if ewd is not None:
        print(
            "- Energy-weighted rainflow DOD: "
            f"{100.0 * ewd:.4f}%"
        )

    print()
    print("Energy reconciliation")
    print(
        "- Battery-side discharge from dispatch: "
        f"{summary['battery_side_discharge_from_dispatch_kwh']:.6f} kWh"
    )
    print(
        "- Battery-side discharge from PWL segments: "
        f"{summary['battery_side_discharge_from_segments_kwh']:.6f} kWh"
    )
    print(
        "- Rainflow-accounted discharge: "
        f"{summary['rainflow_accounted_discharge_kwh']:.6f} kWh"
    )
    print(
        "- Rainflow minus dispatch discharge: "
        f"{summary['rainflow_minus_dispatch_discharge_kwh']:.10f} kWh"
    )

    print()
    print("Degradation-cost validation")
    print(
        "- 15b PWL degradation reference: "
        f"{summary['PWL_degradation_cost_reference_15b_ntd2023']:.6f} "
        "NTD-2023/year"
    )
    print(
        "- PWL cost reconstructed from dispatch segments: "
        f"{summary['PWL_degradation_cost_from_dispatch_segments_ntd2023']:.6f} "
        "NTD-2023/year"
    )
    print(
        "- Rainflow-implied cost on locked G(delta): "
        f"{summary['rainflow_degradation_cost_ntd2023']:.6f} "
        "NTD-2023/year"
    )
    print(
        "- PWL minus rainflow: "
        f"{summary['PWL_minus_rainflow_cost_ntd2023']:.6f} NTD/year"
    )
    print(
        "- Absolute relative difference: "
        f"{100.0 * summary['PWL_vs_rainflow_absolute_relative_difference']:.8f}%"
    )

    print()
    print("Validation gates")
    for gate, status in gates.items():
        print(f"- {gate}: {status}")

    preflight_all = {
        **freeze_gates,
        **reference_gates,
        "shared_core_hash_vs_15b": source_hash_core["status"],
        "economic_interface_hash_vs_15b": (
            source_hash_economic["status"]
        ),
        "technical_provenance": technical_audit["status"],
        "dispatch_timeline": "PASS",
    }

    hard_preflight_fail = any(
        value == "FAIL" for value in preflight_all.values()
    )
    hard_validation_fail = any(
        value == "FAIL" for value in gates.values()
    )

    if hard_preflight_fail or hard_validation_fail:
        final_verdict = "EOB_RAINFLOW_VALIDATION_FAIL"
        exit_code = 2
    elif (
        gates["pwl_vs_rainflow_cost_numerical_equivalence"]
        == "REVIEW"
    ):
        final_verdict = (
            "EOB_RAINFLOW_VALIDATION_REVIEW_REQUIRED"
        )
        exit_code = 3
    else:
        final_verdict = "EOB_RAINFLOW_VALIDATION_PASS"
        exit_code = 0

    audit = {
        "script_version": SCRIPT_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "shared_core_version": CORE_VERSION,
        "final_verdict": final_verdict,
        "methodological_role": (
            "EX_POST_VALIDATION_ONLY; does not alter EOB/Layer A sizing objective"
        ),
        "rainflow_cost_basis": (
            "Same locked PNNL Table 4.2 + C_rep G(delta) calibration used to "
            "derive production lambda_k; piecewise-linear interpolation in G; "
            "no new nonlinear interpolation invented."
        ),
        "preflight_gates": preflight_all,
        "rainflow_validation_gates": gates,
        "frozen_eob_reference_detail": reference_detail,
        "source_hash_checks": {
            "shared_core": source_hash_core,
            "economic_interface_14a": source_hash_economic,
        },
        "technical_provenance_audit": technical_audit,
        "algorithm_self_test": validation["algorithm_self_test"],
        "summary": summary,
        "input_paths_and_hashes": {
            "dispatch": {
                "path": str(args.dispatch),
                "sha256": sha256_file(args.dispatch),
            },
            "result_json": {
                "path": str(args.result_json),
                "sha256": sha256_file(args.result_json),
            },
            "freeze_audit": {
                "path": str(args.freeze_audit),
                "sha256": sha256_file(args.freeze_audit),
            },
            "economic_interface": {
                "path": str(args.economic_interface),
                "sha256": sha256_file(args.economic_interface),
            },
            "technical_provenance": {
                "path": str(args.technical_provenance),
                "sha256": sha256_file(args.technical_provenance),
            },
            "rainflow_validator_module": {
                "path": str(
                    root / "src" / "rainflow_validation_v7_2.py"
                ),
                "sha256": sha256_file(
                    root / "src" / "rainflow_validation_v7_2.py"
                ),
            },
            "script_15c": {
                "path": str(Path(__file__).resolve()),
                "sha256": sha256_file(Path(__file__).resolve()),
            },
        },
        "interpretation": {
            "if_PASS": (
                "Frozen EOB cycle-depth accounting is independently reconciled "
                "by rainflow on the same locked degradation calibration. The "
                "callable validator is ready to be reused in representative "
                "Layer A post-solve audits."
            ),
            "if_REVIEW_REQUIRED": (
                "All hard lineage/physics/energy gates passed, but PWL and "
                "rainflow cost are not numerically equivalent. The v7.2 "
                "framework does not freeze a materiality threshold, so inspect "
                "the quantified difference before authorizing 16a."
            ),
            "if_FAIL": (
                "A hard provenance, SOC/energy, technical-domain, or cost "
                "reconciliation gate failed. Do not proceed to 16a."
            ),
        },
        "next_step_if_pass": (
            "Freeze the 15c validator/checkpoint, then implement only the "
            "representative binary Layer A batch. Reuse the same validator "
            "for every solved Layer A case. Full 81-case grid remains "
            "unauthorized until the representative runtime/convergence review."
        ),
    }

    output_paths = write_outputs(
        args.output_dir,
        validation,
        audit,
    )

    print()
    print("Outputs")
    for key, value in output_paths.items():
        print(f"- {key}: {value}")

    print()
    print("FINAL VERDICT")
    print(final_verdict)

    if final_verdict == "EOB_RAINFLOW_VALIDATION_PASS":
        print(
            "- Ex-post rainflow/DOD validation gate is closed for the frozen EOB."
        )
        print(
            "- Callable validator is ready for reuse in representative Layer A."
        )
        print(
            "- Full 81-case grid is still NOT authorized before the mandatory "
            "binary runtime/convergence checkpoint."
        )
    elif final_verdict == "EOB_RAINFLOW_VALIDATION_REVIEW_REQUIRED":
        print(
            "- Hard validation gates passed, but PWL-vs-rainflow cost difference "
            "requires methodological review before 16a."
        )
    else:
        print(
            "- Do not proceed to 16a until the failed gate is diagnosed."
        )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
