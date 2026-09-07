#!/usr/bin/env python3
"""v7.2 Layer A analytical requirements and representative binary preflight.

This is deliberately not the 81-case Layer A production sweep.  It first
computes the complete inexpensive analytical alpha/beta requirement grid, then
optionally solves only five representative binary cases using the same shared
annual economic core as the frozen EOB.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-layer-a-analytical-representative-binary-preflight-transition-candidate1-reduced-native-max-provenance-2026-09-06-r10"
EXPECTED_CORE_VERSION = "v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9"
ALPHAS = tuple(round(0.60 + 0.05 * i, 2) for i in range(9))
BETAS_H = tuple(range(4, 13))
REPRESENTATIVE_CASES = ((0.60, 4), (0.60, 12), (0.80, 8), (1.00, 4), (1.00, 12))
REPRESENTATIVE_CASES_BY_ID = {
    f"a{alpha:.2f}_b{beta:02d}": (alpha, beta)
    for alpha, beta in REPRESENTATIVE_CASES
}
PRODUCTION_MIP_GAP_MAX = 1e-6
EOB_OBJECTIVE_TOL_NTD = 100.0
TOL = 1e-6


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("analytical-only", "representative", "build-only"),
        default="analytical-only",
        help=(
            "Default performs no MILP solve; representative solves only five "
            "binary cases; build-only constructs one diagnostic model without optimize()."
        ),
    )
    parser.add_argument("--mip-gap", type=float, default=1e-6)
    parser.add_argument("--time-limit-sec", type=float, default=None)
    parser.add_argument("--quiet-gurobi", action="store_true")
    parser.add_argument(
        "--case-id",
        choices=tuple(REPRESENTATIVE_CASES_BY_ID),
        default=None,
        help=(
            "Solve exactly one canonical representative case; build-only accepts "
            "only a0.60_b04."
        ),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=root / "results" / "layer_a" / "preflight"
    )
    args = parser.parse_args()
    if args.case_id is not None and args.mode not in {"representative", "build-only"}:
        parser.error("--case-id requires --mode representative or build-only")
    if args.mode == "build-only" and args.case_id not in {None, "a0.60_b04"}:
        parser.error("build-only is intentionally limited to a0.60_b04")
    return args


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def new_run_id(started_utc: datetime) -> str:
    return f"{started_utc.strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:10]}"


def write_json(path: Path, payload: dict[str, Any], *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8") as handle:
        json.dump(json_safe(payload), handle, indent=2)
        handle.write("\n")


def selected_representative_cases(case_id: str | None) -> tuple[tuple[float, int], ...]:
    if case_id is None:
        return REPRESENTATIVE_CASES
    return (REPRESENTATIVE_CASES_BY_ID[case_id],)


def representative_case_records(
    cases: tuple[tuple[float, int], ...],
) -> list[dict[str, Any]]:
    return [
        {"case_id": f"a{alpha:.2f}_b{beta:02d}", "alpha": float(alpha), "beta_h": int(beta)}
        for alpha, beta in cases
    ]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_value(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_eob(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    # Actual repository convention is results/eob_production, not a duplicate
    # results/eob/production directory.
    paths = {
        "result": root / "results" / "eob_production" / "eob_production_result_v7_2.json",
        "freeze_audit": root / "results" / "eob_production" / "eob_production_freeze_audit_v7_2.json",
    }
    result = read_json(paths["result"], "canonical 15b EOB result")
    audit = read_json(paths["freeze_audit"], "canonical 15b EOB freeze audit")
    if audit.get("freeze_status") != "PRODUCTION_EOB_FREEZE_PASS":
        raise RuntimeError("Canonical EOB freeze status is not PASS.")
    if result.get("status") != "OPTIMAL" or result.get("mode") != "binary":
        raise RuntimeError("Canonical EOB is not an optimal binary production result.")
    return result, audit, paths


def analytical_surface(
    annual: pd.DataFrame,
    *,
    eta_d: float,
    soc_min: float,
    soc_max: float,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    timestamps = pd.to_datetime(annual["timestamp"], errors="raise").reset_index(drop=True)
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    rows: list[dict[str, Any]] = []
    valid_rows: list[dict[str, Any]] = []
    for beta in BETAS_H:
        valid_count = len(load) - beta + 1
        if valid_count <= 0:
            raise RuntimeError(f"No valid starts for beta={beta}.")
        valid_rows.append(
            {
                "beta_h": beta,
                "valid_start_count": valid_count,
                "first_valid_start": timestamps.iloc[0],
                "last_valid_start": timestamps.iloc[valid_count - 1],
                "last_window_end_exclusive": timestamps.iloc[valid_count - 1]
                + pd.Timedelta(hours=beta),
                "no_circular_wrap": True,
            }
        )
    for alpha in ALPHAS:
        deficit = np.maximum(alpha * load - pv, 0.0)
        p_out = float(np.max(deficit))
        for beta in BETAS_H:
            windows = np.convolve(deficit, np.ones(beta, dtype=float), mode="valid")
            binding_index = int(np.argmax(windows))
            max_ac_energy = float(windows[binding_index])
            reserve = max_ac_energy / float(eta_d)
            rows.append(
                {
                    "case_id": f"a{alpha:.2f}_b{beta:02d}",
                    "alpha": alpha,
                    "beta_h": beta,
                    "P_out_kw_ac": p_out,
                    "R_kwh_battery": reserve,
                    "binding_historical_start": timestamps.iloc[binding_index],
                    "binding_historical_end_inclusive": timestamps.iloc[binding_index + beta - 1],
                    "binding_historical_end_exclusive": timestamps.iloc[binding_index]
                    + pd.Timedelta(hours=beta),
                    "binding_start_index": binding_index,
                    "valid_start_count": len(windows),
                    "max_ac_deficit_window_energy_kwh": max_ac_energy,
                    "eta_d": float(eta_d),
                    "analytical_E_N_min_kwh": reserve / float(soc_max - soc_min),
                    "binding_alpha_load_energy_kwh": float(alpha * load[binding_index:binding_index + beta].sum()),
                    "binding_pv_energy_kwh": float(pv[binding_index:binding_index + beta].sum()),
                    "binding_positive_deficit_hours": int(np.count_nonzero(deficit[binding_index:binding_index + beta] > 0.0)),
                }
            )
    surface = pd.DataFrame(rows).sort_values(["alpha", "beta_h"]).reset_index(drop=True)
    starts = pd.DataFrame(valid_rows)
    audit = analytical_audit(surface, starts, timestamps, soc_min=soc_min, soc_max=soc_max)
    return surface, starts, audit


def analytical_audit(
    surface: pd.DataFrame,
    starts: pd.DataFrame,
    timestamps: pd.Series,
    *,
    soc_min: float,
    soc_max: float,
) -> dict[str, Any]:
    failures: list[str] = []
    expected_pairs = {(a, b) for a in ALPHAS for b in BETAS_H}
    actual_pairs = {(float(r.alpha), int(r.beta_h)) for r in surface.itertuples()}
    if len(surface) != 81 or actual_pairs != expected_pairs or surface.duplicated(["alpha", "beta_h"]).any():
        failures.append("grid_pairs")
    p_values = surface.drop_duplicates("alpha").sort_values("alpha")["P_out_kw_ac"].to_numpy()
    if np.any(np.diff(p_values) < -TOL):
        failures.append("power_monotonicity")
    for alpha in ALPHAS:
        values = surface.loc[surface.alpha.eq(alpha)].sort_values("beta_h")["R_kwh_battery"].to_numpy()
        if np.any(np.diff(values) < -TOL):
            failures.append(f"reserve_beta_monotonicity_alpha_{alpha:.2f}")
    for beta in BETAS_H:
        values = surface.loc[surface.beta_h.eq(beta)].sort_values("alpha")["R_kwh_battery"].to_numpy()
        if np.any(np.diff(values) < -TOL):
            failures.append(f"reserve_alpha_monotonicity_beta_{beta}")
    if (surface[["P_out_kw_ac", "R_kwh_battery", "analytical_E_N_min_kwh"]] < -TOL).any().any():
        failures.append("negative_requirement")
    if not (surface["binding_historical_start"] >= timestamps.iloc[0]).all() or not (
        surface["binding_historical_end_exclusive"] <= timestamps.iloc[-1] + pd.Timedelta(hours=1)
    ).all():
        failures.append("binding_window_outside_case_year")
    expected_counts = {beta: len(timestamps) - beta + 1 for beta in BETAS_H}
    observed_counts = dict(zip(starts.beta_h.astype(int), starts.valid_start_count.astype(int)))
    if observed_counts != expected_counts or not starts["no_circular_wrap"].all():
        failures.append("valid_start_rule")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "alpha_values": list(ALPHAS),
        "beta_values_h": list(BETAS_H),
        "case_count": int(len(surface)),
        "power_monotonicity": "PASS" if "power_monotonicity" not in failures else "FAIL",
        "reserve_monotonicity_over_beta": "PASS" if not any("reserve_beta" in x for x in failures) else "FAIL",
        "reserve_monotonicity_over_alpha": "PASS" if not any("reserve_alpha" in x for x in failures) else "FAIL",
        "valid_start_counts": observed_counts,
        "soc_limits": {"soc_min": float(soc_min), "soc_max": float(soc_max)},
    }


def source_manifest(root: Path, inputs: Any, eob_paths: dict[str, Path]) -> dict[str, Any]:
    paths = {**{f"production_{k}": Path(v) for k, v in inputs.source_paths.items()}, **eob_paths}
    paths.update(
        {
            "annual_core": root / "src" / "annual_design_model_v7_2.py",
            "rainflow_validator": root / "src" / "rainflow_validation_v7_2.py",
            "script_16a": Path(__file__).resolve(),
            "historical_valid_start_audit_v7_1": root / "results" / "data_audit" / "valid_outage_starts_v7_1_audit.txt",
        }
    )
    return {
        key: {"path": str(path), "sha256": sha256_file(path)}
        for key, path in paths.items()
        if path.exists()
    }


def write_run_completion(
    run_dir: Path,
    *,
    run_id: str,
    status: str,
    selected_cases: tuple[tuple[float, int], ...],
    **details: Any,
) -> Path:
    path = run_dir / "run_completion_v7_2.json"
    write_json(
        path,
        {
            "run_id": run_id,
            "status": status,
            "ended_utc": utc_text(utc_now()),
            "selected_cases": representative_case_records(selected_cases),
            **details,
        },
    )
    return path


def append_case_telemetry(path: Path, record: dict[str, Any]) -> None:
    payload = {"timestamp_utc": utc_text(utc_now()), **record}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(json_safe(payload), sort_keys=True))
        handle.write("\n")
        handle.flush()


def billing_structure_audit(
    billing_exact: pd.DataFrame,
    annual: pd.DataFrame,
) -> dict[str, Any]:
    """Validate the detailed billing rows against the production tariff calendar."""
    from src.annual_design_model_v7_2 import PURE_APPLICABLE_PERIODS

    required = {
        "billing_usage_period_id",
        "billing_period_role",
        "season",
        "tou_period",
    }
    expected_periods = set(annual["billing_usage_period_id"].astype(str))
    if not required.issubset(billing_exact.columns):
        return {
            "period_ids": "FAIL",
            "detail_columns": "FAIL",
            "valid_detail_keys": "FAIL",
            "duplicate_detail_keys": "FAIL",
            "tariff_calendar_structure": "FAIL",
            "actual_row_count": int(len(billing_exact)),
            "expected_row_count": None,
        }

    expected_keys: set[tuple[str, str, str, str]] = set()
    for month, month_df in annual.groupby("billing_usage_period_id", sort=True):
        month_id = str(month)
        seasons = sorted(month_df["season"].astype(str).unique().tolist())
        role = "transition" if len(seasons) == 2 else f"pure_{seasons[0]}"
        for season in seasons:
            for tou_period in PURE_APPLICABLE_PERIODS[season]:
                if (
                    month_df["season"].astype(str).eq(season)
                    & month_df["tou_period"].astype(str).eq(tou_period)
                ).any():
                    expected_keys.add((month_id, role, season, tou_period))

    actual_keys = [
        tuple(row)
        for row in billing_exact[
            ["billing_usage_period_id", "billing_period_role", "season", "tou_period"]
        ].astype(str).itertuples(index=False, name=None)
    ]
    actual_key_set = set(actual_keys)
    duplicate_count = len(actual_keys) - len(actual_key_set)
    return {
        "period_ids": "PASS" if set(billing_exact["billing_usage_period_id"].astype(str)) == expected_periods else "FAIL",
        "detail_columns": "PASS",
        "valid_detail_keys": "PASS" if actual_key_set.issubset(expected_keys) else "FAIL",
        "duplicate_detail_keys": "PASS" if duplicate_count == 0 else "FAIL",
        "tariff_calendar_structure": "PASS" if actual_key_set == expected_keys else "FAIL",
        "actual_row_count": int(len(actual_keys)),
        "expected_row_count": int(len(expected_keys)),
        "duplicate_detail_key_count": int(duplicate_count),
    }


def representative_gate(
    result: dict[str, Any],
    requirement: dict[str, Any],
    eob: dict[str, Any],
    *,
    soc_min: float,
    soc_max: float,
    rainflow_validation: dict[str, Any] | None,
    billing_audit: dict[str, Any],
) -> dict[str, str]:
    if not result.get("has_solution"):
        return {"solver_solution": "FAIL"}
    sizing, phys = result["sizing"], result["physical_diagnostics"]
    layer = result.get("layer_a_resilience", {})
    rainflow_pass = (
        rainflow_validation is not None
        and rainflow_validation["summary"].get("verdict") == "RAINFLOW_VALIDATION_PASS"
        and all(value == "PASS" for value in rainflow_validation["gates"].values())
    )
    return {
        "solver_optimal": "PASS" if result["status"] == "OPTIMAL" else "FAIL",
        "binary_formulation": "PASS" if result["mode"] == "binary" else "FAIL",
        "mip_gap": "PASS" if result.get("mip_gap") is not None and float(result["mip_gap"]) <= PRODUCTION_MIP_GAP_MAX else "FAIL",
        "analytical_energy_lower_bound": "PASS" if float(sizing["E_N_kwh"]) + TOL >= float(requirement["analytical_E_N_min_kwh"]) else "FAIL",
        "power_adequacy": "PASS" if float(sizing["P_B_kw_ac"]) + TOL >= float(requirement["P_out_kw_ac"]) else "FAIL",
        "annual_reserve_floor": "PASS" if layer.get("annual_reserve_floor", {}).get("violating_hours") == 0 else "FAIL",
        "technical_soc": "PASS" if float(phys["soc_min_realized"]) >= soc_min - TOL and float(phys["soc_max_realized"]) <= soc_max + TOL else "FAIL",
        "simultaneous_charge_discharge": "PASS" if int(phys["simultaneous_hours_above_tol"]) == 0 else "FAIL",
        "cost_reconciliation": "PASS" if abs(float(result["cost_reconciliation_residual_ntd"])) <= 1e-3 else "FAIL",
        "eob_objective_lower_bound": "PASS" if float(result["objective_ntd2023_per_year"]) + EOB_OBJECTIVE_TOL_NTD >= float(eob["objective_ntd2023_per_year"]) else "RED_FLAG",
        "billing_period_ids": billing_audit["period_ids"],
        "billing_detail_columns": billing_audit["detail_columns"],
        "billing_detail_key_validity": billing_audit["valid_detail_keys"],
        "billing_detail_key_duplicates": billing_audit["duplicate_detail_keys"],
        "billing_tariff_calendar_structure": billing_audit["tariff_calendar_structure"],
        "billing_row_count": "PASS" if billing_audit["actual_row_count"] == billing_audit["expected_row_count"] else "FAIL",
        "transition_ambiguity": "PASS" if result["transition_settlement"]["nonbinding_certificate"] == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE" else "FAIL",
        "rainflow_validation": "PASS" if rainflow_pass else "FAIL",
    }


def eob_comparison(result: dict[str, Any], eob: dict[str, Any]) -> dict[str, float | None]:
    """Calculate representative-case premiums from the canonical EOB JSON."""
    if not result.get("has_solution"):
        return {
            "delta_E_N_kwh": None,
            "delta_P_B_kw_ac": None,
            "delta_CC_regular_kw": None,
            "delta_objective_ntd2023_per_year": None,
            "resilience_premium_pct": None,
        }
    sizing = result["sizing"]
    eob_sizing = eob["sizing"]
    delta_objective = float(result["objective_ntd2023_per_year"]) - float(eob["objective_ntd2023_per_year"])
    return {
        "delta_E_N_kwh": float(sizing["E_N_kwh"]) - float(eob_sizing["E_N_kwh"]),
        "delta_P_B_kw_ac": float(sizing["P_B_kw_ac"]) - float(eob_sizing["P_B_kw_ac"]),
        "delta_CC_regular_kw": float(sizing["CC_regular_kw"]) - float(eob_sizing["CC_regular_kw"]),
        "delta_objective_ntd2023_per_year": delta_objective,
        "resilience_premium_pct": 100.0 * delta_objective / float(eob["objective_ntd2023_per_year"]),
    }


def validate_representative_rainflow(
    root: Path,
    inputs: Any,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Apply the same reusable post-solve rainflow validator used by 15c."""
    from src.annual_design_model_v7_2 import BREAKPOINTS, ETA_C, ETA_D, SOC_MAX, SOC_MIN
    from src.rainflow_validation_v7_2 import validate_dispatch_rainflow

    technical_path = (
        root / "results" / "parameter_audit" / "pnnl_table4_2_cyclelife_g_provenance_by_bracket.csv"
    )
    technical = pd.read_csv(technical_path)
    power_bracket = float(inputs.mainline_package["power_scale_bracket_mw"])
    selected = technical.loc[
        np.isclose(
            pd.to_numeric(technical["power_scale_bracket_mw"], errors="coerce"),
            power_bracket,
            atol=1e-12,
            rtol=0.0,
        )
    ].copy()
    if selected.empty:
        raise RuntimeError(f"No PNNL technical points for mainline {power_bracket:g} MW package.")
    lambdas = [
        float(inputs.mainline_package[f"lambda_{k}_ntd2023_per_battery_side_discharged_kwh"])
        for k in range(1, 4)
    ]
    return validate_dispatch_rainflow(
        result["dispatch"],
        e_n_kwh=float(result["sizing"]["E_N_kwh"]),
        eta_c=float(ETA_C),
        eta_d=float(ETA_D),
        soc_min=float(SOC_MIN),
        soc_max=float(SOC_MAX),
        production_breakpoints=BREAKPOINTS,
        lambdas=lambdas,
        technical_points=selected,
        crep_ntd_per_kwh=float(inputs.mainline_package["crep_ntd2023_per_kwh"]),
        pwl_cost_reference_ntd=float(result["cost_components_ntd2023_per_year"]["degradation"]),
        battery_side_discharge_reference_kwh=float(result["annual_energy"]["battery_side_discharge_kwh"]),
        timestamps=pd.to_datetime(result["dispatch"]["timestamp"], errors="raise"),
    )


def write_analytical_outputs(output_dir: Path, surface: pd.DataFrame, starts: pd.DataFrame, audit: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "requirements_csv": output_dir / "layer_a_analytical_requirements_v7_2.csv",
        "valid_starts_csv": output_dir / "layer_a_valid_start_audit_v7_2.csv",
        "audit_json": output_dir / "layer_a_analytical_audit_v7_2.json",
    }
    surface.to_csv(paths["requirements_csv"], index=False, encoding="utf-8-sig")
    starts.to_csv(paths["valid_starts_csv"], index=False, encoding="utf-8-sig")
    payload = {
        "script_version": SCRIPT_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "analytical_audit": audit,
        "provenance": manifest,
        "output_paths": {k: str(v) for k, v in paths.items()},
    }
    paths["audit_json"].write_text(json.dumps(json_safe(payload), indent=2), encoding="utf-8")
    return paths


def run_representative_cases(
    *,
    root: Path,
    output_dir: Path,
    run_id: str,
    selected_cases: tuple[tuple[float, int], ...],
    inputs: Any,
    surface: pd.DataFrame,
    eob: dict[str, Any],
    args: argparse.Namespace,
) -> pd.DataFrame:
    from src.annual_design_model_v7_2 import (
        SOC_MAX,
        SOC_MIN,
        LayerAResilienceRequirements,
        SolveSettings,
        solve_eob,
    )

    representative_dir = output_dir / "representative_cases"
    representative_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for alpha, beta in selected_cases:
        req = surface.loc[(surface.alpha.eq(alpha)) & (surface.beta_h.eq(beta))].iloc[0].to_dict()
        case_id = str(req["case_id"])
        case_dir = representative_dir / case_id
        case_dir.mkdir(parents=True, exist_ok=False)
        log_path = case_dir / "gurobi.log"
        telemetry_path = case_dir / "solver_telemetry.jsonl"
        case_manifest_path = case_dir / "case_manifest_v7_2.json"
        case_started_utc = utc_now()
        write_json(
            case_manifest_path,
            {
                "run_id": run_id,
                "case_id": case_id,
                "python_case_started_utc": utc_text(case_started_utc),
                "analytical_requirement": req,
                "mode": "binary",
                "mip_gap": float(args.mip_gap),
                "time_limit_sec": args.time_limit_sec,
                "gurobi_output_enabled": not bool(args.quiet_gurobi),
                "gurobi_log_path": str(log_path),
                "solver_telemetry_path": str(telemetry_path),
            },
            exclusive=True,
        )
        config = LayerAResilienceRequirements(
            alpha=float(alpha), beta_h=int(beta), reserve_kwh_battery=float(req["R_kwh_battery"]), power_requirement_kw_ac=float(req["P_out_kw_ac"])
        )
        result = solve_eob(
            inputs,
            SolveSettings(
                mode="binary",
                mip_gap=float(args.mip_gap),
                time_limit_sec=args.time_limit_sec,
                output_flag=0 if args.quiet_gurobi else 1,
                log_file=str(log_path),
                telemetry_callback=lambda record, path=telemetry_path: append_case_telemetry(path, record),
            ),
            config,
        )
        rainflow: dict[str, Any] | None = None
        rainflow_error: str | None = None
        if result.get("has_solution"):
            try:
                rainflow = validate_representative_rainflow(root, inputs, result)
            except Exception as exc:
                rainflow_error = f"{type(exc).__name__}: {exc}"
        billing_audit = billing_structure_audit(result["billing_exact"], inputs.annual) if result.get("has_solution") else {
            "period_ids": "FAIL",
            "detail_columns": "FAIL",
            "valid_detail_keys": "FAIL",
            "duplicate_detail_keys": "FAIL",
            "tariff_calendar_structure": "FAIL",
            "actual_row_count": 0,
            "expected_row_count": None,
        }
        comparison = eob_comparison(result, eob)
        gates = representative_gate(
            result,
            req,
            eob,
            soc_min=float(SOC_MIN),
            soc_max=float(SOC_MAX),
            rainflow_validation=rainflow,
            billing_audit=billing_audit,
        )
        serializable = {k: v for k, v in result.items() if k not in {"dispatch", "billing_exact", "transition_settlement_detail"}}
        rainflow_record = None if rainflow is None else {
            "summary": rainflow["summary"],
            "gates": rainflow["gates"],
            "algorithm_self_test": rainflow["algorithm_self_test"],
        }
        write_json(
            case_dir / f"{case_id}_result_v7_2.json",
            {
                "run_id": run_id,
                "case_id": case_id,
                "python_case_finished_utc": utc_text(utc_now()),
                "case_manifest_path": str(case_manifest_path),
                "solver_telemetry_path": str(telemetry_path),
                "gurobi_log_path": str(log_path),
                "analytical_requirement": req,
                "result": serializable,
                "eob_comparison": comparison,
                "billing_structure_audit": billing_audit,
                "gates": gates,
                "rainflow_validation": rainflow_record,
                "rainflow_error": rainflow_error,
            },
        )
        if result.get("has_solution"):
            result["dispatch"].to_csv(case_dir / f"{case_id}_dispatch_v7_2.csv", index=False, encoding="utf-8-sig")
            result["billing_exact"].to_csv(case_dir / f"{case_id}_billing_exact_v7_2.csv", index=False, encoding="utf-8-sig")
            result["transition_settlement_detail"].to_csv(case_dir / f"{case_id}_transition_detail_v7_2.csv", index=False, encoding="utf-8-sig")
        if rainflow is not None:
            pd.DataFrame([rainflow["summary"]]).to_csv(
                case_dir / f"{case_id}_rainflow_summary_v7_2.csv",
                index=False,
                encoding="utf-8-sig",
            )
            rainflow["cycles"].to_csv(case_dir / f"{case_id}_rainflow_cycles_v7_2.csv", index=False, encoding="utf-8-sig")
        rainflow_summary = {} if rainflow is None else rainflow["summary"]
        rows.append({**req, "solver_status": result.get("status"), "runtime_sec_gurobi": result.get("runtime_sec_gurobi"), "mip_gap": result.get("mip_gap"), **result.get("sizing", {}), "objective_ntd2023_per_year": result.get("objective_ntd2023_per_year"), **comparison, "billing_detail_row_count": billing_audit["actual_row_count"], "billing_expected_detail_row_count": billing_audit["expected_row_count"], "billing_duplicate_detail_key_count": billing_audit.get("duplicate_detail_key_count"), "rainflow_verdict": rainflow_summary.get("verdict"), "rainflow_pwl_minus_rainflow_cost_ntd2023": rainflow_summary.get("PWL_minus_rainflow_cost_ntd2023"), "rainflow_error": rainflow_error, **{f"gate__{k}": v for k, v in gates.items()}})
    summary = pd.DataFrame(rows)
    summary.to_csv(output_dir / "layer_a_representative_preflight_summary_v7_2.csv", index=False, encoding="utf-8-sig")
    return summary


def _finite_range(values: list[float]) -> dict[str, float | None]:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return {
        "min": min(finite) if finite else None,
        "max": max(finite) if finite else None,
        "finite_count": len(finite),
        "input_count": len(values),
    }


def build_only_case_audit(
    *,
    run_dir: Path,
    run_id: str,
    inputs: Any,
    surface: pd.DataFrame,
) -> dict[str, Any]:
    """Construct a0.60_b04 once and collect raw user-model statistics.

    This deliberately calls ``build_eob_model`` directly rather than
    ``solve_eob`` and never invokes ``Model.optimize()``.
    """
    from gurobipy import GRB
    from src.annual_design_model_v7_2 import (
        LayerAResilienceRequirements,
        SolveSettings,
        build_eob_model,
    )

    case_id = "a0.60_b04"
    req = surface.loc[surface["case_id"].eq(case_id)].iloc[0].to_dict()
    build_dir = run_dir / "build_only" / case_id
    build_dir.mkdir(parents=True, exist_ok=False)
    case_started_utc = utc_now()
    case_manifest_path = build_dir / "case_manifest_v7_2.json"
    write_json(
        case_manifest_path,
        {
            "run_id": run_id,
            "case_id": case_id,
            "mode": "build-only",
            "python_model_construction_started_utc": utc_text(case_started_utc),
            "analytical_requirement": req,
            "optimize_called": False,
        },
        exclusive=True,
    )
    requirements = LayerAResilienceRequirements(
        alpha=float(req["alpha"]),
        beta_h=int(req["beta_h"]),
        reserve_kwh_battery=float(req["R_kwh_battery"]),
        power_requirement_kw_ac=float(req["P_out_kw_ac"]),
    )
    wall_started = datetime.now(timezone.utc)
    perf_started = time.perf_counter()
    model, handles = build_eob_model(
        inputs,
        SolveSettings(mode="binary", mip_gap=PRODUCTION_MIP_GAP_MAX, output_flag=0),
        requirements,
    )
    model.update()
    elapsed = float(time.perf_counter() - perf_started)
    wall_finished = utc_now()
    variables = model.getVars()
    linear_constraints = model.getConstrs()
    general_constraints = model.getGenConstrs()
    transition_billing_epigraph_rows = [
        constraint
        for constraint in linear_constraints
        if str(constraint.ConstrName).startswith("transition_demand_epi_")
    ]
    class_c_demand_link_rows = [
        constraint
        for constraint in linear_constraints
        if str(constraint.ConstrName).startswith("transition_demand_ge_seasonal_max_")
    ]
    max_records: list[dict[str, Any]] = []
    indicator_count = 0
    for constraint in general_constraints:
        constraint_type = int(constraint.GenConstrType)
        if constraint_type == GRB.GENCONSTR_INDICATOR:
            indicator_count += 1
        if constraint_type == GRB.GENCONSTR_MAX:
            record: dict[str, Any] = {
                "name": str(constraint.GenConstrName),
                "type": "MAX",
            }
            try:
                result_var, operand_vars, constant = model.getGenConstrMax(constraint)
                record.update(
                    {
                        "result_var": str(result_var.VarName),
                        "result_lb": float(result_var.LB),
                        "result_ub": float(result_var.UB),
                        "operand_count": int(len(operand_vars)),
                        "operand_lb_range": _finite_range(
                            [float(var.LB) for var in operand_vars]
                        ),
                        "operand_ub_range": _finite_range(
                            [float(var.UB) for var in operand_vars]
                        ),
                        "constant": float(constant) if constant is not None else None,
                    }
                )
            except Exception as exc:  # Gurobi API-version diagnostic only
                record["operand_query_error"] = f"{type(exc).__name__}: {exc}"
            max_records.append(record)

    matrix_range: dict[str, Any]
    try:
        matrix = model.getA()
        matrix_range = _finite_range([float(value) for value in matrix.data])
    except Exception as exc:
        matrix_range = {"error": f"{type(exc).__name__}: {exc}"}
    finite_bound_variables = [
        variable
        for variable in variables
        if math.isfinite(float(variable.LB)) and math.isfinite(float(variable.UB))
    ]
    payload = {
        "run_id": run_id,
        "case_id": case_id,
        "mode": "build-only",
        "optimize_called": False,
        "python_model_construction_started_utc": utc_text(wall_started),
        "python_model_construction_finished_utc": utc_text(wall_finished),
        "model_construction_wall_seconds": elapsed,
        "analytical_requirement": req,
        "raw_user_model": {
            "rows_linear_constraints": int(model.NumConstrs),
            "columns_variables": int(model.NumVars),
            "binary_variables": int(sum(var.VType == GRB.BINARY for var in variables)),
            "integer_variables": int(sum(var.VType == GRB.INTEGER for var in variables)),
            "sos_constraints": int(model.NumSOS),
            "general_constraints": int(model.NumGenConstrs),
            "indicator_constraints": int(indicator_count),
            "max_general_constraints": int(len(max_records)),
            "max_operand_total": int(
                sum(
                    int(record["operand_count"])
                    for record in max_records
                    if "operand_count" in record
                )
            ),
            "transition_billing_epigraph_rows": int(
                len(transition_billing_epigraph_rows)
            ),
            "class_c_demand_link_rows": int(len(class_c_demand_link_rows)),
            "max_constraints": max_records,
            "linear_matrix_coefficient_range": matrix_range,
            "objective_coefficient_range": _finite_range(
                [float(variable.Obj) for variable in variables]
            ),
            "linear_rhs_range": _finite_range(
                [float(constraint.RHS) for constraint in linear_constraints]
            ),
            "general_constraint_rhs_range": {
                "status": "NOT_APPLICABLE_NATIVE_MAX_AND_INDICATOR_API",
                "max_result_bound_range": _finite_range(
                    [
                        float(record["result_ub"])
                        for record in max_records
                        if "result_ub" in record
                    ]
                ),
            },
            "variable_lower_bound_range": _finite_range(
                [float(variable.LB) for variable in variables]
            ),
            "variable_upper_bound_range": _finite_range(
                [float(variable.UB) for variable in variables]
            ),
            "finite_bounded_variable_count": int(len(finite_bound_variables)),
            "unbounded_or_partially_bounded_variable_count": int(
                len(variables) - len(finite_bound_variables)
            ),
        },
        "transition_component_classification": handles[
            "transition_component_classification"
        ],
        "transition_formulation_metadata": handles[
            "transition_formulation_metadata"
        ],
        "finite_design_bounds": handles["finite_design_bounds"],
        "historical_comparison": {
            "pre_change": {
                "rows": 122907,
                "columns": 122815,
                "binaries": 8760,
                "indicators": 17520,
                "native_max_constraints": 0,
                "native_max_operands": 0,
            },
            "r5_diagnostic": {
                "rows": 122929,
                "columns": 122871,
                "binaries": 8774,
                "indicators": 17596,
                "native_max_constraints": 0,
                "native_max_operands": 0,
            },
            "candidate1_pre_reduction": {
                "rows": 121455,
                "columns": 122843,
                "binaries": 8764,
                "indicators": 17520,
                "native_max_constraints": 20,
                "native_max_operands": 1500,
            },
        },
        "case_manifest_path": str(case_manifest_path),
    }
    output_path = build_dir / f"{case_id}_build_audit_v7_2.json"
    write_json(output_path, payload)
    model.dispose()
    return {"path": output_path, **payload}


def main() -> int:
    args = parse_args()
    root = project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.annual_design_model_v7_2 import CORE_VERSION, ETA_D, SOC_MAX, SOC_MIN, load_annual_design_inputs
    from src.rainflow_validation_v7_2 import VALIDATOR_VERSION

    if CORE_VERSION != EXPECTED_CORE_VERSION:
        raise RuntimeError(
            "Script 16a requires the current transition-settlement core version; "
            f"expected={EXPECTED_CORE_VERSION!r}, actual={CORE_VERSION!r}."
        )

    if args.mode == "representative":
        selected_cases = selected_representative_cases(args.case_id)
    elif args.mode == "build-only":
        selected_cases = selected_representative_cases("a0.60_b04")
    else:
        selected_cases = ()
    run_started_utc = utc_now()
    run_id = new_run_id(run_started_utc)
    run_dir = args.output_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    run_manifest_path = run_dir / "run_manifest_v7_2.json"
    write_json(
        run_manifest_path,
        {
            "run_id": run_id,
            "run_started_utc": utc_text(run_started_utc),
            "script_version": SCRIPT_VERSION,
            "expected_core_version": EXPECTED_CORE_VERSION,
            "core_version": CORE_VERSION,
            "mode": args.mode,
            "selected_cases": representative_case_records(selected_cases),
            "requested_mip_gap": float(args.mip_gap),
            "requested_time_limit_sec": args.time_limit_sec,
            "gurobi_output_enabled": not bool(args.quiet_gurobi),
            "requested_output_root": str(args.output_dir),
            "git": {
                "branch": git_value(root, "branch", "--show-current"),
                "head": git_value(root, "rev-parse", "HEAD"),
            },
            "source_hashes_at_start": {
                "script_16a": sha256_file(Path(__file__).resolve()),
                "annual_core": sha256_file(root / "src" / "annual_design_model_v7_2.py"),
            },
        },
        exclusive=True,
    )

    try:
        inputs = load_annual_design_inputs(root)
        eob, _freeze_audit, eob_paths = canonical_eob(root)
        surface, starts, audit = analytical_surface(
            inputs.annual, eta_d=ETA_D, soc_min=SOC_MIN, soc_max=SOC_MAX
        )
        manifest = source_manifest(root, inputs, eob_paths)
        manifest["git"] = {
            "branch": git_value(root, "branch", "--show-current"),
            "head": git_value(root, "rev-parse", "HEAD"),
        }
        manifest["run"] = {
            "run_id": run_id,
            "run_started_utc": utc_text(run_started_utc),
            "run_manifest_path": str(run_manifest_path),
        }
        paths = write_analytical_outputs(run_dir / "analytical", surface, starts, audit, manifest)

        print(f"Run ID: {run_id}")
        print(f"Run manifest: {run_manifest_path}")
        print(f"Script version: {SCRIPT_VERSION}")
        print(f"Shared core: {CORE_VERSION}")
        print(f"Rainflow validator available: {VALIDATOR_VERSION}")
        print(f"Analytical surface: {len(surface)} cases; audit={audit['status']}")
        print(f"Analytical output: {paths['requirements_csv']}")
        if audit["status"] != "PASS":
            write_run_completion(
                run_dir,
                run_id=run_id,
                status="ANALYTICAL_AUDIT_FAIL",
                selected_cases=selected_cases,
            )
            return 2
        if args.mode == "analytical-only":
            completion = write_run_completion(
                run_dir,
                run_id=run_id,
                status="ANALYTICAL_ONLY_PASS",
                selected_cases=selected_cases,
                analytical_output_paths={key: str(value) for key, value in paths.items()},
            )
            print("MILP solves: NOT RUN (analytical-only mode)")
            print(f"Run completion: {completion}")
            return 0
        if args.mode == "build-only":
            build_audit = build_only_case_audit(
                run_dir=run_dir,
                run_id=run_id,
                inputs=inputs,
                surface=surface,
            )
            completion = write_run_completion(
                run_dir,
                run_id=run_id,
                status="BUILD_ONLY_PASS",
                selected_cases=selected_cases,
                optimize_called=False,
                build_audit_path=str(build_audit["path"]),
            )
            print("MILP solves: NOT RUN (build-only mode)")
            print(f"Build-only audit: {build_audit['path']}")
            print(f"Run completion: {completion}")
            return 0
        summary = run_representative_cases(
            root=root,
            output_dir=run_dir,
            run_id=run_id,
            selected_cases=selected_cases,
            inputs=inputs,
            surface=surface,
            eob=eob,
            args=args,
        )
        all_pass = all(
            value == "PASS"
            for col in summary.columns
            if col.startswith("gate__")
            for value in summary[col].tolist()
        )
        completion = write_run_completion(
            run_dir,
            run_id=run_id,
            status="REPRESENTATIVE_PASS" if all_pass else "REPRESENTATIVE_GATE_FAIL",
            selected_cases=selected_cases,
            representative_summary_path=str(
                run_dir / "layer_a_representative_preflight_summary_v7_2.csv"
            ),
            all_gates_pass=bool(all_pass),
        )
        print(f"Representative binary cases solved: {len(summary)}; all_gates_pass={all_pass}")
        print(f"Run completion: {completion}")
        return 0 if all_pass else 2
    except Exception as exc:
        write_run_completion(
            run_dir,
            run_id=run_id,
            status="ERROR",
            selected_cases=selected_cases,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
