#!/usr/bin/env python3
"""
annual_design_model_v7_2.py

Shared NTUST thesis v7.2 annual BESS/contract-capacity optimization core.

This module is intentionally a shared model core rather than an experiment
script. Script 15a uses it for the EOB charge/discharge formulation benchmark;
later Layer A drivers should reuse the same core and add the locked resilience
requirements rather than reimplementing the annual economics.

Model boundary
--------------
- 8,760 hourly planning-baseline Load/PV chronology from Script 06.
- One endogenous regular contract capacity CC; supplementary contracts are 0.
- BESS nameplate energy E_N (battery-side kWh) and AC/PCS power P_B (kW).
- 10--90% SOC usable range represented by three intertemporal Xu-derived
  segment-energy states with breakpoints 0, 0.30, 0.60, 0.80 of nameplate E_N.
- eta_c = eta_d = 0.90; AC-side charge/discharge power, battery-side energy.
- Constant NTD-2023 economic inputs from Script 14a.
- Season-specific settlement masks/rates from Script 14b.
- Pure-season over-contract settlement uses the audited 10% / 2x / 3x,
  sequential non-duplication semantics.

Transition-period boundary
--------------------------
The retained evidence supports billing-period TOU maximum demand, sequential
non-duplication, and the official 10% / 2x / 3x over-contract tiers, but does
not freeze a universal summer/non-summer rate-selection rule for every possible
May/October corner case. The model therefore does NOT fabricate one.

For mixed-season billing periods, the solver first forms one billing-period
maximum demand for each TOU period (peak -> half -> sat_half -> off) and applies
sequential non-duplication. A transition over-contract increment is included in
the objective whenever its applicable basic-charge rate is unambiguous: either
only one season can supply that TOU period, or the summer/non-summer rates are
equal. Only a genuinely rate-ambiguous incremental overage is omitted as a
non-negative LOWER-BOUND RELAXATION. Post-solve diagnostics recompute exact
monthly TOU maxima and certify the EOB whenever the omitted ambiguous increment
is zero. Raw May/October overage alone is therefore NOT a failure condition.

Charge/discharge exclusivity
----------------------------
The core supports both:
- mode='binary': explicit hourly charge/discharge exclusivity via Gurobi
  indicator constraints;
- mode='relaxed': LP-compatible formulation with no exclusivity binary.

Script 15a compares the two using exactly the same physical/economic model.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import gurobipy as gp
    from gurobipy import GRB
except ImportError as exc:  # pragma: no cover - user environment dependency
    raise ImportError(
        "gurobipy is required for the annual design model. Activate the project "
        "environment containing Gurobi before running Script 15a."
    ) from exc


CORE_VERSION = "v7.2-annual-design-core-transition-rate-audit-2026-08-29-r1"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760
DELTA_T_HR = 1.0

SOC_MIN = 0.10
SOC_MAX = 0.90
ETA_C = 0.90
ETA_D = 0.90
BREAKPOINTS = (0.0, 0.30, 0.60, 0.80)
SEGMENT_WIDTHS = tuple(
    BREAKPOINTS[i + 1] - BREAKPOINTS[i]
    for i in range(len(BREAKPOINTS) - 1)
)
N_SEGMENTS = len(SEGMENT_WIDTHS)

TOU_ORDER = ("peak", "half", "sat_half", "off")
PURE_APPLICABLE_PERIODS = {
    "summer": ("peak", "half", "sat_half", "off"),
    "non_summer": ("half", "sat_half", "off"),
}
TRANSITION_PERIODS = ("2025-05", "2025-10")

SIMULTANEOUS_TOL_KW = 1e-5
TRANSITION_OVERAGE_TOL_KW = 1e-6
BALANCE_TOL = 1e-5
COST_RECONCILIATION_TOL_NTD = 1e-3


@dataclass(frozen=True)
class AnnualDesignInputs:
    annual: pd.DataFrame
    energy_rate_ntd2023_per_kwh: np.ndarray
    economic_interface: dict[str, Any]
    settlement_interface: dict[str, Any]
    settlement_matrix: pd.DataFrame
    kappa: float
    mainline_package: dict[str, Any]
    source_paths: dict[str, str]


@dataclass(frozen=True)
class SolveSettings:
    mode: str
    mip_gap: float = 1e-4
    time_limit_sec: float | None = None
    output_flag: int = 1
    numeric_focus: int = 1
    log_file: str | None = None


def _require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    _require_file(path, label)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc


def _normalize_bool_series(series: pd.Series, label: str) -> pd.Series:
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
        raise RuntimeError(f"{label}: unparseable boolean values {bad[:10]}")
    return out.astype(bool)


def _read_annual_input(parquet_path: Path, csv_path: Path) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError):
            pass
    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path
    raise FileNotFoundError(
        "Canonical annual input not found. Expected either:\n"
        f"- {parquet_path}\n- {csv_path}\nRun Script 06 first."
    )


def _validate_annual(df_raw: pd.DataFrame) -> pd.DataFrame:
    required = {
        "timestamp",
        "baseline_load_kw",
        "pv_available_kw",
        "season",
        "tou_period",
        "tou_calendar_verified",
        "billing_usage_period_id",
        "integration_status",
    }
    missing = sorted(required - set(df_raw.columns))
    if missing:
        raise RuntimeError(f"Annual input missing required columns: {missing}")

    df = df_raw.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().any():
        raise RuntimeError("Annual input contains unparsable timestamps.")
    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df = df.sort_values("timestamp").reset_index(drop=True)

    if len(df) != EXPECTED_ROWS:
        raise RuntimeError(f"Annual input rows={len(df)}; expected {EXPECTED_ROWS}.")
    expected = pd.date_range(FORMAL_START, periods=EXPECTED_ROWS, freq="h")
    if not pd.DatetimeIndex(df["timestamp"]).equals(expected):
        raise RuntimeError("Annual input is not the exact formal 8,760-hour timeline.")
    if not _normalize_bool_series(
        df["tou_calendar_verified"], "tou_calendar_verified"
    ).all():
        raise RuntimeError("Annual input TOU calendar is not fully audited.")
    if set(df["integration_status"].astype(str)) != {"passed"}:
        raise RuntimeError("Annual input integration_status is not passed-only.")

    for column in ["baseline_load_kw", "pv_available_kw"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any() or (df[column] < 0).any():
            raise RuntimeError(f"{column} must be finite and non-negative.")

    allowed_seasons = {"summer", "non_summer"}
    if not set(df["season"].astype(str)).issubset(allowed_seasons):
        raise RuntimeError("Annual input contains unexpected season labels.")
    if not set(df["tou_period"].astype(str)).issubset(set(TOU_ORDER)):
        raise RuntimeError("Annual input contains unexpected TOU labels.")

    bad_ns_peak = df.loc[
        df["season"].eq("non_summer") & df["tou_period"].eq("peak")
    ]
    if not bad_ns_peak.empty:
        raise RuntimeError("Non-summer peak appears in annual input; expected N/A.")

    return df


def _load_normalized_tariff(path: Path) -> pd.DataFrame:
    _require_file(path, "14a normalized tariff")
    df = pd.read_csv(path)
    required = {
        "parameter_id",
        "parameter_group",
        "season",
        "tou_period",
        "contract_period",
        "applicable",
        "usage_year",
        "value_constant_ntd2023",
        "optimization_currency",
        "optimization_currency_base_year",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"Normalized tariff missing columns: {missing}")
    df = df.copy()
    df["applicable"] = _normalize_bool_series(df["applicable"], "tariff applicable")
    df["usage_year"] = pd.to_numeric(df["usage_year"], errors="raise").astype(int)
    df["optimization_currency_base_year"] = pd.to_numeric(
        df["optimization_currency_base_year"], errors="raise"
    ).astype(int)
    if set(df["optimization_currency"].astype(str)) != {"NTD"}:
        raise RuntimeError("Optimization tariff currency must be NTD.")
    if set(df["optimization_currency_base_year"]) != {2023}:
        raise RuntimeError("Optimization tariff must be constant NTD-2023.")
    return df


def _tariff_value(
    tariff: pd.DataFrame,
    parameter_id: str,
    usage_year: int,
) -> float:
    rows = tariff.loc[
        tariff["parameter_id"].eq(parameter_id)
        & tariff["usage_year"].eq(int(usage_year))
    ]
    if len(rows) != 1:
        raise RuntimeError(
            f"Expected one tariff row for {parameter_id}, year={usage_year}; "
            f"found {len(rows)}."
        )
    row = rows.iloc[0]
    if not bool(row["applicable"]):
        raise RuntimeError(f"Requested tariff parameter is N/A: {parameter_id}")
    value = pd.to_numeric(
        pd.Series([row["value_constant_ntd2023"]]), errors="coerce"
    ).iloc[0]
    if pd.isna(value) or float(value) < 0:
        raise RuntimeError(f"Invalid tariff value: {parameter_id}, year={usage_year}")
    return float(value)


def _build_hourly_energy_rates(annual: pd.DataFrame, tariff: pd.DataFrame) -> np.ndarray:
    rates = np.zeros(len(annual), dtype=float)
    for i, row in annual.iterrows():
        year = int(row["timestamp"].year)
        season = str(row["season"])
        period = str(row["tou_period"])
        parameter_id = f"energy_{season}_{period}"
        rates[i] = _tariff_value(tariff, parameter_id, year)
    if not np.isfinite(rates).all() or (rates < 0).any():
        raise RuntimeError("Hourly energy-rate vector is invalid.")
    return rates


def load_annual_design_inputs(
    root: Path,
    *,
    annual_parquet: Path | None = None,
    annual_csv: Path | None = None,
    economic_interface_path: Path | None = None,
    normalized_tariff_path: Path | None = None,
    settlement_interface_path: Path | None = None,
    settlement_matrix_path: Path | None = None,
) -> AnnualDesignInputs:
    annual_parquet = annual_parquet or root / "data" / "processed" / "annual_input_v7_1.parquet"
    annual_csv = annual_csv or root / "data" / "processed" / "annual_input_v7_1.csv"
    economic_interface_path = economic_interface_path or root / "data" / "reference" / "production_economic_interface_v7_2.json"
    normalized_tariff_path = normalized_tariff_path or root / "data" / "reference" / "taipower_tariff_optimization_ntd2023_v7_2.csv"
    settlement_interface_path = settlement_interface_path or root / "data" / "reference" / "taipower_transition_period_settlement_interface_v7_2.json"
    settlement_matrix_path = settlement_matrix_path or root / "data" / "reference" / "taipower_seasonal_settlement_matrix_v7_2.csv"

    annual_raw, annual_used = _read_annual_input(annual_parquet, annual_csv)
    annual = _validate_annual(annual_raw)
    tariff = _load_normalized_tariff(normalized_tariff_path)
    economic = _read_json(economic_interface_path, "14a economic interface")
    settlement = _read_json(settlement_interface_path, "14b settlement interface")
    _require_file(settlement_matrix_path, "14b seasonal settlement matrix")
    matrix = pd.read_csv(settlement_matrix_path)

    if economic.get("status") != "READY_FOR_EOB_OBJECTIVE_WIRING":
        raise RuntimeError("14a economic interface is not ready for EOB wiring.")
    if settlement.get("status") != "READY_FOR_EOB_SEASONAL_SETTLEMENT_WIRING":
        raise RuntimeError("14b settlement interface is not ready for EOB wiring.")

    monetary = economic.get("monetary_basis", {})
    if monetary.get("currency") != "NTD" or monetary.get("currency_base_year") != 2023:
        raise RuntimeError("14a monetary basis is not constant NTD-2023.")

    selector = economic.get("package_selector", {})
    if selector.get("outcome_dependent_switching_allowed") is not False:
        raise RuntimeError("Outcome-dependent PNNL package switching is not blocked.")
    mainline = selector.get("mainline")
    if not isinstance(mainline, dict):
        raise RuntimeError("14a mainline 10 MW package is missing.")
    if not np.isclose(float(mainline.get("power_scale_bracket_mw", np.nan)), 10.0):
        raise RuntimeError("14a mainline package is not the 10 MW cost-scale package.")

    billing = economic.get("billing_demand_proxy", {})
    kappa = float(billing.get("kappa", np.nan))
    if not np.isfinite(kappa) or kappa <= 0:
        raise RuntimeError("Invalid kappa in 14a economic interface.")

    tariff_meta = economic.get("taipower_tariff", {})
    if tariff_meta.get("non_summer_peak_semantics") != "N/A_not_zero":
        raise RuntimeError("14a did not preserve non-summer peak N/A semantics.")
    if tariff_meta.get("separate_subsidy_cashflow") is not False:
        raise RuntimeError("14a unexpectedly permits separate subsidy cash flow.")
    if tariff_meta.get("may_october_basic_charge_transition") != "case_validated_empirical_50_50":
        raise RuntimeError("Unexpected May/October regular-basic transition label.")

    mixed = settlement.get("mixed_season_positive_overcontract_aggregation", {})
    if mixed.get("fabricated_default_allowed") is not False:
        raise RuntimeError("14b unexpectedly permits a fabricated mixed-season default.")
    if mixed.get("final_cross_season_aggregation_formula_frozen") is not False:
        raise RuntimeError("14b unexpectedly claims a frozen cross-season formula.")

    required_matrix = {
        "billing_usage_period_id",
        "usage_year",
        "billing_period_role",
        "season",
        "tou_period",
        "contract_period",
        "hour_count",
        "active_in_hourly_case",
        "basic_rate_constant_ntd2023_per_kw_month",
        "cross_season_positive_overcontract_aggregation",
    }
    missing = sorted(required_matrix - set(matrix.columns))
    if missing:
        raise RuntimeError(f"14b settlement matrix missing columns: {missing}")
    matrix = matrix.copy()
    matrix["active_in_hourly_case"] = _normalize_bool_series(
        matrix["active_in_hourly_case"], "settlement active_in_hourly_case"
    )

    energy_rates = _build_hourly_energy_rates(annual, tariff)

    return AnnualDesignInputs(
        annual=annual,
        energy_rate_ntd2023_per_kwh=energy_rates,
        economic_interface=economic,
        settlement_interface=settlement,
        settlement_matrix=matrix,
        kappa=kappa,
        mainline_package=mainline,
        source_paths={
            "annual_input": str(annual_used),
            "economic_interface_14a": str(economic_interface_path),
            "normalized_tariff_14a": str(normalized_tariff_path),
            "settlement_interface_14b": str(settlement_interface_path),
            "settlement_matrix_14b": str(settlement_matrix_path),
        },
    )


def _package_float(package: dict[str, Any], key: str) -> float:
    value = float(package.get(key, np.nan))
    if not np.isfinite(value) or value < 0:
        raise RuntimeError(f"Invalid mainline economic-package field {key}: {value}")
    return value


def _mainline_cost_coefficients(package: dict[str, Any]) -> dict[str, Any]:
    breakpoints = str(package.get("production_breakpoints", ""))
    if breakpoints != "0,0.30,0.60,0.80":
        raise RuntimeError(f"Unexpected degradation breakpoints: {breakpoints}")

    lambdas = np.array(
        [
            _package_float(package, "lambda_1_ntd2023_per_battery_side_discharged_kwh"),
            _package_float(package, "lambda_2_ntd2023_per_battery_side_discharged_kwh"),
            _package_float(package, "lambda_3_ntd2023_per_battery_side_discharged_kwh"),
        ],
        dtype=float,
    )
    if np.any(np.diff(lambdas) < -1e-12):
        raise RuntimeError("Degradation marginal lambdas must be nondecreasing.")

    return {
        "annualized_C_E": _package_float(
            package, "annualized_capex_C_E_ntd2023_per_kwh_year"
        ),
        "annualized_C_P": _package_float(
            package, "annualized_capex_C_P_ntd2023_per_kw_year"
        ),
        "fom_E": _package_float(package, "fom_E_ntd2023_per_kwh_year"),
        "fom_P": _package_float(package, "fom_P_ntd2023_per_kw_year"),
        "lambdas": lambdas,
    }


def _month_groups(annual: pd.DataFrame) -> dict[str, np.ndarray]:
    groups: dict[str, np.ndarray] = {}
    for month, idx in annual.groupby("billing_usage_period_id", sort=True).groups.items():
        groups[str(month)] = np.asarray(sorted(idx), dtype=int)
    return groups


def _pure_month_season(annual: pd.DataFrame, month_indices: np.ndarray) -> str | None:
    seasons = sorted(annual.iloc[month_indices]["season"].astype(str).unique().tolist())
    if len(seasons) == 1:
        return seasons[0]
    if len(seasons) == 2:
        return None
    raise RuntimeError(f"Unexpected season count in billing period: {seasons}")


def _regular_basic_rate(
    inputs: AnnualDesignInputs,
    usage_period_id: str,
    season: str | None,
) -> float:
    year = int(usage_period_id[:4])
    tariff_path = Path(inputs.source_paths["normalized_tariff_14a"])
    tariff = _load_normalized_tariff(tariff_path)
    if season is not None:
        return _tariff_value(tariff, f"basic_{season}_regular", year)
    # Locked upstream case-validated transition treatment for regular basic charge.
    su = _tariff_value(tariff, "basic_summer_regular", year)
    ns = _tariff_value(tariff, "basic_non_summer_regular", year)
    return 0.5 * (su + ns)


def _matrix_rate(
    matrix: pd.DataFrame,
    month: str,
    season: str,
    tou_period: str,
) -> float:
    rows = matrix.loc[
        matrix["billing_usage_period_id"].astype(str).eq(month)
        & matrix["season"].astype(str).eq(season)
        & matrix["tou_period"].astype(str).eq(tou_period)
    ]
    if len(rows) != 1:
        raise RuntimeError(
            f"Expected one 14b settlement row for {month}/{season}/{tou_period}; "
            f"found {len(rows)}."
        )
    value = pd.to_numeric(
        pd.Series([rows.iloc[0]["basic_rate_constant_ntd2023_per_kw_month"]]),
        errors="coerce",
    ).iloc[0]
    if pd.isna(value) or float(value) < 0:
        raise RuntimeError(f"Invalid 14b basic rate for {month}/{season}/{tou_period}.")
    return float(value)


def _transition_rate_resolution(
    inputs: AnnualDesignInputs,
    month: str,
    active_seasons: list[str],
    tou_period: str,
) -> dict[str, Any]:
    """Resolve whether a transition-period over-contract increment has one rate.

    This does not invent a cross-season settlement formula. It only recognizes
    cases where no rate choice is required because exactly one season is active
    for the TOU period or every active season has the same audited basic rate.
    """
    seasons = sorted(set(str(x) for x in active_seasons))
    if not seasons:
        raise RuntimeError(f"No active seasons for {month}/{tou_period}.")

    rates = {
        season: _matrix_rate(inputs.settlement_matrix, month, season, tou_period)
        for season in seasons
    }
    values = list(rates.values())
    unique = all(np.isclose(v, values[0], rtol=0.0, atol=1e-9) for v in values[1:])
    return {
        "rate_unambiguous": bool(unique),
        "resolved_rate": float(values[0]) if unique else None,
        "candidate_rates": {k: float(v) for k, v in rates.items()},
        "active_seasons": seasons,
        "resolution_reason": (
            "single_active_season"
            if len(seasons) == 1
            else "equal_rates_across_active_seasons"
            if unique
            else "different_rates_across_active_seasons"
        ),
    }


def build_eob_model(
    inputs: AnnualDesignInputs,
    settings: SolveSettings,
) -> tuple[gp.Model, dict[str, Any]]:
    mode = settings.mode.strip().lower()
    if mode not in {"binary", "relaxed"}:
        raise ValueError("SolveSettings.mode must be 'binary' or 'relaxed'.")

    annual = inputs.annual
    T = len(annual)
    K = range(N_SEGMENTS)
    TT = range(T)
    STATES = range(T + 1)

    coeff = _mainline_cost_coefficients(inputs.mainline_package)
    lambdas = coeff["lambdas"]
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    energy_rates = np.asarray(inputs.energy_rate_ntd2023_per_kwh, dtype=float)

    model = gp.Model(f"ntust_v7_2_eob_{mode}")
    model.Params.OutputFlag = int(settings.output_flag)
    model.Params.NumericFocus = int(settings.numeric_focus)
    if settings.time_limit_sec is not None:
        if settings.time_limit_sec <= 0:
            raise ValueError("time_limit_sec must be positive when provided.")
        model.Params.TimeLimit = float(settings.time_limit_sec)
    if mode == "binary":
        model.Params.MIPGap = float(settings.mip_gap)
    if settings.log_file:
        Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
        model.Params.LogFile = str(settings.log_file)

    # Sizing decisions.
    E_N = model.addVar(lb=0.0, name="E_N_kwh")
    P_B = model.addVar(lb=0.0, name="P_B_kw_ac")
    CC = model.addVar(lb=0.0, name="CC_regular_kw")

    # Hourly aggregate operating variables.
    p_grid = model.addVars(TT, lb=0.0, name="p_grid_kw")
    p_ch = model.addVars(TT, lb=0.0, name="p_ch_kw_ac")
    p_dis = model.addVars(TT, lb=0.0, name="p_dis_kw_ac")
    pv_curt = model.addVars(TT, lb=0.0, name="pv_curt_kw")

    # Xu-derived intertemporal segment states / flows.
    e_seg = model.addVars(STATES, K, lb=0.0, name="e_seg_kwh")
    p_ch_seg = model.addVars(TT, K, lb=0.0, name="p_ch_seg_kw_ac")
    p_dis_seg = model.addVars(TT, K, lb=0.0, name="p_dis_seg_kw_ac")

    u_mode = None
    if mode == "binary":
        u_mode = model.addVars(TT, vtype=GRB.BINARY, name="u_charge_mode")

    # Segment capacities are endogenous fractions of nameplate E_N.
    for t in STATES:
        for k, width in enumerate(SEGMENT_WIDTHS):
            model.addConstr(
                e_seg[t, k] <= float(width) * E_N,
                name=f"seg_cap_t{t}_k{k+1}",
            )

    # Physical AC-bus balance, power rating, PV curtailment and segment linkage.
    for t in TT:
        model.addConstr(
            p_grid[t] + float(pv[t]) - pv_curt[t] + p_dis[t]
            == float(load[t]) + p_ch[t],
            name=f"ac_balance_t{t}",
        )
        model.addConstr(pv_curt[t] <= float(pv[t]), name=f"pv_curt_cap_t{t}")
        model.addConstr(p_ch[t] <= P_B, name=f"charge_power_cap_t{t}")
        model.addConstr(p_dis[t] <= P_B, name=f"discharge_power_cap_t{t}")
        model.addConstr(
            p_ch[t] == gp.quicksum(p_ch_seg[t, k] for k in K),
            name=f"charge_segment_link_t{t}",
        )
        model.addConstr(
            p_dis[t] == gp.quicksum(p_dis_seg[t, k] for k in K),
            name=f"discharge_segment_link_t{t}",
        )

        if mode == "binary":
            # u=1 => charge mode (discharge forced to zero)
            # u=0 => discharge mode (charge forced to zero)
            model.addGenConstrIndicator(
                u_mode[t], True, p_dis[t] == 0.0, name=f"ind_charge_t{t}"
            )
            model.addGenConstrIndicator(
                u_mode[t], False, p_ch[t] == 0.0, name=f"ind_discharge_t{t}"
            )

        for k in K:
            model.addConstr(
                e_seg[t + 1, k]
                == e_seg[t, k]
                + ETA_C * p_ch_seg[t, k] * DELTA_T_HR
                - p_dis_seg[t, k] * DELTA_T_HR / ETA_D,
                name=f"seg_dyn_t{t}_k{k+1}",
            )

    # Annual cyclic segment boundary. Aggregate physical stored energy is
    # SOC_MIN*E_N + sum(e_seg), so segment cyclicity also gives e_T=e_0.
    for k in K:
        model.addConstr(e_seg[T, k] == e_seg[0, k], name=f"cyclic_seg_k{k+1}")

    # Cost components.
    cost_capex = coeff["annualized_C_E"] * E_N + coeff["annualized_C_P"] * P_B
    cost_fom = coeff["fom_E"] * E_N + coeff["fom_P"] * P_B
    cost_energy = gp.quicksum(
        float(energy_rates[t]) * p_grid[t] * DELTA_T_HR for t in TT
    )
    cost_deg = gp.quicksum(
        float(lambdas[k]) * p_dis_seg[t, k] * DELTA_T_HR / ETA_D
        for t in TT
        for k in K
    )

    month_groups = _month_groups(annual)
    basic_month_terms: dict[str, gp.LinExpr] = {}
    over_month_terms: dict[str, gp.LinExpr] = {}
    billing_aux: dict[str, Any] = {}

    # Regular basic charge for all 12 usage periods.
    for month, idx in month_groups.items():
        season = _pure_month_season(annual, idx)
        rate = _regular_basic_rate(inputs, month, season)
        basic_month_terms[month] = float(rate) * CC

    # Over-contract settlement. Pure-season periods use the audited standard
    # rule. Mixed-season periods use one billing-period maximum per TOU period;
    # resolved-rate increments enter the objective, while only genuinely
    # rate-ambiguous increments are omitted as a lower-bound diagnostic.
    over_rule = inputs.settlement_interface.get("overcontract_rule", {})
    tier1_frac = float(over_rule.get("tier1_threshold_fraction", np.nan))
    tier1_mult = float(over_rule.get("tier1_multiplier", np.nan))
    tier2_mult = float(over_rule.get("tier2_multiplier", np.nan))
    if not np.isclose(tier1_frac, 0.10) or not np.isclose(tier1_mult, 2.0) or not np.isclose(tier2_mult, 3.0):
        raise RuntimeError("Unexpected 14b over-contract tier metadata.")
    tier_threshold = model.addVar(lb=0.0, name="over_tier1_threshold_kw")
    model.addConstr(tier_threshold == tier1_frac * CC, name="tier1_threshold_link")

    pure_over_terms: list[gp.LinExpr] = []
    transition_resolved_terms: list[gp.LinExpr] = []

    for month, idx in month_groups.items():
        season = _pure_month_season(annual, idx)
        month_df = annual.iloc[idx]
        z_prev: gp.Var | None = None
        s_prev: gp.Var | None = None
        month_cost = gp.LinExpr(0.0)
        aux_periods: dict[str, Any] = {}

        applicable = list(PURE_APPLICABLE_PERIODS[season]) if season is not None else list(TOU_ORDER)

        for period in applicable:
            period_mask = month_df["tou_period"].astype(str).to_numpy() == period
            active_idx = idx[period_mask]
            if len(active_idx) == 0:
                continue

            D = model.addVar(lb=0.0, name=f"D_{month}_{period}_kw")
            raw = model.addVar(lb=0.0, name=f"raw_over_{month}_{period}_kw")
            z = model.addVar(lb=0.0, name=f"cum_over_{month}_{period}_kw")
            s_tier = model.addVar(lb=0.0, name=f"cum_tier1_{month}_{period}_kw")

            for t in active_idx.tolist():
                model.addConstr(
                    D >= inputs.kappa * p_grid[int(t)],
                    name=f"demand_epi_{month}_{period}_t{int(t)}",
                )
            model.addConstr(raw >= D - CC, name=f"raw_over_link_{month}_{period}")
            model.addConstr(z >= raw, name=f"cum_ge_raw_{month}_{period}")
            if z_prev is not None:
                model.addConstr(z >= z_prev, name=f"cum_monotone_{month}_{period}")
            model.addConstr(s_tier <= z, name=f"tier1_le_cum_{month}_{period}")
            model.addConstr(s_tier <= tier_threshold, name=f"tier1_le_cap_{month}_{period}")

            if z_prev is None:
                delta_z = z
                delta_s = s_tier
            else:
                model.addConstr(s_tier >= s_prev, name=f"tier1_monotone_{month}_{period}")
                model.addConstr(
                    s_tier - s_prev <= z - z_prev,
                    name=f"tier1_increment_le_total_{month}_{period}",
                )
                delta_z = z - z_prev
                delta_s = s_tier - s_prev

            if season is not None:
                rate_info = {
                    "rate_unambiguous": True,
                    "resolved_rate": _matrix_rate(inputs.settlement_matrix, month, season, period),
                    "candidate_rates": {season: _matrix_rate(inputs.settlement_matrix, month, season, period)},
                    "active_seasons": [season],
                    "resolution_reason": "pure_season",
                }
            else:
                active_seasons = sorted(
                    month_df.loc[period_mask, "season"].astype(str).unique().tolist()
                )
                rate_info = _transition_rate_resolution(inputs, month, active_seasons, period)

            objective_included = bool(rate_info["rate_unambiguous"])
            if objective_included:
                rate = float(rate_info["resolved_rate"])
                month_cost += rate * (
                    tier1_mult * delta_s + tier2_mult * (delta_z - delta_s)
                )
            else:
                rate = None

            aux_periods[period] = {
                "D": D,
                "raw": raw,
                "z": z,
                "s": s_tier,
                "rate": rate,
                "rate_unambiguous": bool(rate_info["rate_unambiguous"]),
                "candidate_rates": rate_info["candidate_rates"],
                "active_seasons": rate_info["active_seasons"],
                "resolution_reason": rate_info["resolution_reason"],
                "objective_included": objective_included,
            }
            z_prev = z
            s_prev = s_tier

        over_month_terms[month] = month_cost
        if season is None:
            transition_resolved_terms.append(month_cost)
            billing_aux[month] = {
                "season": "transition",
                "transition_overcontract_in_objective": True,
                "only_unambiguous_rate_increments_included": True,
                "periods": aux_periods,
            }
        else:
            pure_over_terms.append(month_cost)
            billing_aux[month] = {
                "season": season,
                "transition_overcontract_in_objective": False,
                "periods": aux_periods,
            }

    cost_over_pure = gp.quicksum(pure_over_terms)
    cost_over_transition_resolved = gp.quicksum(transition_resolved_terms)
    cost_basic = gp.quicksum(basic_month_terms.values())
    cost_over = cost_over_pure + cost_over_transition_resolved

    objective = cost_capex + cost_fom + cost_energy + cost_basic + cost_over + cost_deg
    model.setObjective(objective, GRB.MINIMIZE)

    handles = {
        "mode": mode,
        "E_N": E_N,
        "P_B": P_B,
        "CC": CC,
        "p_grid": p_grid,
        "p_ch": p_ch,
        "p_dis": p_dis,
        "pv_curt": pv_curt,
        "e_seg": e_seg,
        "p_ch_seg": p_ch_seg,
        "p_dis_seg": p_dis_seg,
        "u_mode": u_mode,
        "cost_expr": {
            "annualized_capex": cost_capex,
            "fom": cost_fom,
            "energy": cost_energy,
            "basic": cost_basic,
            "overcontract_pure_season": cost_over_pure,
            "overcontract_transition_resolved": cost_over_transition_resolved,
            "degradation": cost_deg,
        },
        "billing_aux": billing_aux,
        "coefficients": coeff,
    }
    return model, handles


def _model_status_name(status: int) -> str:
    # Use getattr for newer optional status constants so the core remains
    # compatible with multiple installed Gurobi versions.
    names = [
        ("LOADED", "LOADED"),
        ("OPTIMAL", "OPTIMAL"),
        ("INFEASIBLE", "INFEASIBLE"),
        ("INF_OR_UNBD", "INF_OR_UNBD"),
        ("UNBOUNDED", "UNBOUNDED"),
        ("CUTOFF", "CUTOFF"),
        ("ITERATION_LIMIT", "ITERATION_LIMIT"),
        ("NODE_LIMIT", "NODE_LIMIT"),
        ("TIME_LIMIT", "TIME_LIMIT"),
        ("SOLUTION_LIMIT", "SOLUTION_LIMIT"),
        ("INTERRUPTED", "INTERRUPTED"),
        ("NUMERIC", "NUMERIC"),
        ("SUBOPTIMAL", "SUBOPTIMAL"),
        ("USER_OBJ_LIMIT", "USER_OBJ_LIMIT"),
        ("WORK_LIMIT", "WORK_LIMIT"),
        ("MEM_LIMIT", "MEM_LIMIT"),
    ]
    mapping = {}
    for attr, label in names:
        value = getattr(GRB, attr, None)
        if value is not None:
            mapping[value] = label
    return mapping.get(status, f"STATUS_{status}")


def _expr_value(expr: Any) -> float:
    try:
        return float(expr.getValue())
    except AttributeError:
        return float(expr)


def solve_eob(
    inputs: AnnualDesignInputs,
    settings: SolveSettings,
) -> dict[str, Any]:
    model, h = build_eob_model(inputs, settings)
    started = time.perf_counter()
    model.optimize()
    wall = time.perf_counter() - started

    status = int(model.Status)
    status_name = _model_status_name(status)
    has_solution = int(model.SolCount) > 0
    if not has_solution:
        return {
            "core_version": CORE_VERSION,
            "mode": settings.mode,
            "status": status_name,
            "status_code": status,
            "has_solution": False,
            "runtime_sec_gurobi": float(model.Runtime),
            "runtime_sec_wall": float(wall),
        }

    annual = inputs.annual
    T = len(annual)
    K = range(N_SEGMENTS)

    E_N = float(h["E_N"].X)
    P_B = float(h["P_B"].X)
    CC = float(h["CC"].X)
    p_grid = np.array([h["p_grid"][t].X for t in range(T)], dtype=float)
    p_ch = np.array([h["p_ch"][t].X for t in range(T)], dtype=float)
    p_dis = np.array([h["p_dis"][t].X for t in range(T)], dtype=float)
    pv_curt = np.array([h["pv_curt"][t].X for t in range(T)], dtype=float)
    e_seg = np.array(
        [[h["e_seg"][t, k].X for k in K] for t in range(T + 1)], dtype=float
    )
    p_ch_seg = np.array(
        [[h["p_ch_seg"][t, k].X for k in K] for t in range(T)], dtype=float
    )
    p_dis_seg = np.array(
        [[h["p_dis_seg"][t, k].X for k in K] for t in range(T)], dtype=float
    )

    # Physical state/SOC diagnostics.
    shifted = e_seg.sum(axis=1)
    physical_e = SOC_MIN * E_N + shifted
    soc = np.full(T + 1, np.nan, dtype=float)
    if E_N > 1e-9:
        soc = physical_e / E_N

    # Exact post-solve AC-bus residual.
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    balance_resid = p_grid + pv - pv_curt + p_dis - load - p_ch
    max_balance_resid = float(np.max(np.abs(balance_resid)))

    # Exact segment dynamics residual.
    dyn_resid = np.zeros((T, N_SEGMENTS), dtype=float)
    for k in K:
        dyn_resid[:, k] = (
            e_seg[1:, k]
            - e_seg[:-1, k]
            - ETA_C * p_ch_seg[:, k] * DELTA_T_HR
            + p_dis_seg[:, k] * DELTA_T_HR / ETA_D
        )
    max_dyn_resid = float(np.max(np.abs(dyn_resid)))
    cyclic_resid = float(np.max(np.abs(e_seg[-1, :] - e_seg[0, :])))

    simultaneous = np.minimum(p_ch, p_dis)
    max_simultaneous = float(simultaneous.max())
    simultaneous_hours = int(np.sum(simultaneous > SIMULTANEOUS_TOL_KW))

    # Cost reconciliation.
    cost_components = {
        name: _expr_value(expr) for name, expr in h["cost_expr"].items()
    }
    objective = float(model.ObjVal)
    reconstructed_cost = float(sum(cost_components.values()))
    cost_residual = objective - reconstructed_cost

    # Exact post-solve billing maxima. Season-component rows are retained for
    # provenance, while transition_settlement_detail performs the actual
    # billing-period-TOU non-duplication/rate-ambiguity audit.
    billing_rows: list[dict[str, Any]] = []
    transition_detail_rows: list[dict[str, Any]] = []
    transition_positive_raw = False
    transition_ambiguous_incremental_total_kw = 0.0
    transition_resolved_exact_cost = 0.0
    min_solver_aux_margin = math.inf
    over_rule = inputs.settlement_interface["overcontract_rule"]
    tier1_frac = float(over_rule["tier1_threshold_fraction"])
    tier1_mult = float(over_rule["tier1_multiplier"])
    tier2_mult = float(over_rule["tier2_multiplier"])
    month_groups = _month_groups(annual)
    for month, idx in month_groups.items():
        month_df = annual.iloc[idx]
        role_seasons = sorted(month_df["season"].astype(str).unique().tolist())
        role = "transition" if len(role_seasons) == 2 else f"pure_{role_seasons[0]}"
        overall_exact = float(np.max(inputs.kappa * p_grid[idx]))
        for season_component in role_seasons:
            season_idx = idx[month_df["season"].astype(str).to_numpy() == season_component]
            for period in PURE_APPLICABLE_PERIODS[season_component]:
                mask = annual.iloc[season_idx]["tou_period"].astype(str).to_numpy() == period
                active_idx = season_idx[mask]
                if len(active_idx) == 0:
                    continue
                exact = float(np.max(inputs.kappa * p_grid[active_idx]))
                raw_over = max(0.0, exact - CC)

                solver_aux = None
                solver_margin = None
                month_aux = h["billing_aux"].get(month, {})
                period_aux = month_aux.get("periods", {}).get(period)
                if role != "transition" and period_aux is not None:
                    solver_aux = float(period_aux["D"].X)
                    solver_margin = solver_aux - exact
                    min_solver_aux_margin = min(min_solver_aux_margin, solver_margin)

                billing_rows.append(
                    {
                        "billing_usage_period_id": month,
                        "billing_period_role": role,
                        "season": season_component,
                        "tou_period": period,
                        "hour_count": int(len(active_idx)),
                        "exact_billing_demand_kw": exact,
                        "overall_exact_billing_demand_kw": overall_exact,
                        "solver_demand_aux_kw": solver_aux,
                        "solver_aux_minus_exact_kw": solver_margin,
                        "cc_regular_kw": CC,
                        "raw_overage_kw": raw_over,
                        "transition_positive_overage_flag": bool(
                            role == "transition" and raw_over > TRANSITION_OVERAGE_TOL_KW
                        ),
                    }
                )

        if role == "transition":
            prior_max = 0.0
            for period in TOU_ORDER:
                period_mask = month_df["tou_period"].astype(str).to_numpy() == period
                active_idx = idx[period_mask]
                if len(active_idx) == 0:
                    continue
                values = inputs.kappa * p_grid[active_idx]
                arg_local = int(np.argmax(values))
                exact = float(values[arg_local])
                max_t = int(active_idx[arg_local])
                max_season = str(annual.iloc[max_t]["season"])
                raw = max(0.0, exact - CC)
                transition_positive_raw = transition_positive_raw or raw > TRANSITION_OVERAGE_TOL_KW
                lower = min(prior_max, raw)
                incremental = max(0.0, raw - prior_max)
                cap = tier1_frac * CC
                tier1_kw = max(0.0, min(raw, cap) - min(lower, cap))
                tier2_kw = max(0.0, incremental - tier1_kw)
                active_seasons = sorted(
                    month_df.loc[period_mask, "season"].astype(str).unique().tolist()
                )
                rate_info = _transition_rate_resolution(inputs, month, active_seasons, period)
                ambiguous_increment = (
                    incremental if not bool(rate_info["rate_unambiguous"]) else 0.0
                )
                transition_ambiguous_incremental_total_kw += ambiguous_increment
                resolved_cost = 0.0
                if bool(rate_info["rate_unambiguous"]):
                    rate = float(rate_info["resolved_rate"])
                    resolved_cost = rate * (tier1_mult * tier1_kw + tier2_mult * tier2_kw)
                    transition_resolved_exact_cost += resolved_cost
                else:
                    rate = None

                period_aux = h["billing_aux"].get(month, {}).get("periods", {}).get(period)
                solver_aux = float(period_aux["D"].X) if period_aux is not None else None
                solver_margin = solver_aux - exact if solver_aux is not None else None
                if period_aux is not None and bool(period_aux.get("objective_included", False)):
                    min_solver_aux_margin = min(min_solver_aux_margin, float(solver_margin))

                transition_detail_rows.append(
                    {
                        "billing_usage_period_id": month,
                        "tou_period": period,
                        "active_seasons": "+".join(active_seasons),
                        "exact_billing_period_tou_max_kw": exact,
                        "max_timestamp": str(annual.iloc[max_t]["timestamp"]),
                        "max_timestamp_season": max_season,
                        "cc_regular_kw": CC,
                        "raw_overage_kw": raw,
                        "prior_max_raw_overage_kw": prior_max,
                        "incremental_nonduplicated_overage_kw": incremental,
                        "tier1_increment_kw": tier1_kw,
                        "tier2_increment_kw": tier2_kw,
                        "rate_unambiguous": bool(rate_info["rate_unambiguous"]),
                        "rate_resolution_reason": rate_info["resolution_reason"],
                        "candidate_rates_ntd2023_per_kw_month": json.dumps(
                            rate_info["candidate_rates"], ensure_ascii=False, sort_keys=True
                        ),
                        "resolved_rate_ntd2023_per_kw_month": rate,
                        "resolved_exact_charge_ntd2023": resolved_cost,
                        "ambiguous_incremental_overage_kw": ambiguous_increment,
                        "solver_demand_aux_kw": solver_aux,
                        "solver_aux_minus_exact_kw": solver_margin,
                    }
                )
                prior_max = max(prior_max, raw)

    billing_exact = pd.DataFrame(billing_rows)
    transition_detail = pd.DataFrame(transition_detail_rows)
    if math.isinf(min_solver_aux_margin):
        min_solver_aux_margin = math.nan

    # Exact pure-season over-contract cost reconstructed from the optimized grid
    # profile using the same 13c semantics.
    pure_exact_cost = 0.0
    for month, idx in month_groups.items():
        season = _pure_month_season(annual, idx)
        if season is None:
            continue
        prior_max = 0.0
        for period in PURE_APPLICABLE_PERIODS[season]:
            rows = billing_exact.loc[
                billing_exact["billing_usage_period_id"].eq(month)
                & billing_exact["season"].eq(season)
                & billing_exact["tou_period"].eq(period)
            ]
            if rows.empty:
                continue
            raw = float(rows.iloc[0]["raw_overage_kw"])
            lower = min(prior_max, raw)
            chargeable = max(0.0, raw - prior_max)
            cap = tier1_frac * CC
            tier1_kw = max(0.0, min(raw, cap) - min(lower, cap))
            tier2_kw = max(0.0, chargeable - tier1_kw)
            rate = _matrix_rate(inputs.settlement_matrix, month, season, period)
            pure_exact_cost += rate * (tier1_mult * tier1_kw + tier2_mult * tier2_kw)
            prior_max = max(prior_max, raw)

    solver_pure_over = cost_components["overcontract_pure_season"]
    pure_over_resid = float(solver_pure_over - pure_exact_cost)
    solver_transition_resolved = cost_components["overcontract_transition_resolved"]
    transition_resolved_resid = float(
        solver_transition_resolved - transition_resolved_exact_cost
    )

    solver_optimal = status == GRB.OPTIMAL
    if not solver_optimal:
        transition_certificate = "NOT_CERTIFIED_SOLVER_NOT_OPTIMAL"
        eob_finality = "BENCHMARK_INCUMBENT_NOT_FINAL_OPTIMUM"
    elif transition_ambiguous_incremental_total_kw <= TRANSITION_OVERAGE_TOL_KW:
        transition_certificate = "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
        eob_finality = "EXACT_WITH_RESPECT_TO_TRANSITION_RATE_AMBIGUITY"
    else:
        transition_certificate = "FAIL_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
        eob_finality = "PROVISIONAL_TRANSITION_RATE_AMBIGUITY_BINDING"

    if abs(pure_over_resid) > 0.05:
        raise RuntimeError(
            "Pure-season over-contract exact-vs-solver residual too large: "
            f"{pure_over_resid} NTD"
        )
    if abs(transition_resolved_resid) > 0.05:
        raise RuntimeError(
            "Resolved transition over-contract exact-vs-solver residual too large: "
            f"{transition_resolved_resid} NTD"
        )
    if np.isfinite(min_solver_aux_margin) and min_solver_aux_margin < -1e-5:
        raise RuntimeError(
            "A cost-facing solver demand epigraph is below the exact post-solve "
            f"maximum by {-min_solver_aux_margin} kW."
        )

    if max_balance_resid > BALANCE_TOL:
        raise RuntimeError(f"Post-solve AC balance residual too large: {max_balance_resid}")
    if max_dyn_resid > BALANCE_TOL or cyclic_resid > BALANCE_TOL:
        raise RuntimeError(
            "Post-solve segment-state residual too large: "
            f"dyn={max_dyn_resid}, cyclic={cyclic_resid}"
        )
    if abs(cost_residual) > COST_RECONCILIATION_TOL_NTD:
        raise RuntimeError(
            f"Objective cost decomposition residual too large: {cost_residual} NTD"
        )

    dispatch = pd.DataFrame(
        {
            "timestamp": annual["timestamp"],
            "billing_usage_period_id": annual["billing_usage_period_id"].astype(str),
            "season": annual["season"].astype(str),
            "tou_period": annual["tou_period"].astype(str),
            "baseline_load_kw": load,
            "pv_available_kw": pv,
            "energy_rate_ntd2023_per_kwh": inputs.energy_rate_ntd2023_per_kwh,
            "p_grid_kw": p_grid,
            "p_charge_kw_ac": p_ch,
            "p_discharge_kw_ac": p_dis,
            "pv_curtailment_kw": pv_curt,
            "e_physical_kwh": physical_e[:-1],
            "soc_fraction": soc[:-1],
            "simultaneous_charge_discharge_kw": simultaneous,
        }
    )
    for k in K:
        dispatch[f"e_seg_{k+1}_kwh"] = e_seg[:-1, k]
        dispatch[f"p_charge_seg_{k+1}_kw_ac"] = p_ch_seg[:, k]
        dispatch[f"p_discharge_seg_{k+1}_kw_ac"] = p_dis_seg[:, k]

    result = {
        "core_version": CORE_VERSION,
        "mode": settings.mode,
        "status": status_name,
        "status_code": status,
        "has_solution": True,
        "runtime_sec_gurobi": float(model.Runtime),
        "runtime_sec_wall": float(wall),
        "node_count": float(model.NodeCount) if settings.mode == "binary" else 0.0,
        "iteration_count": float(model.IterCount),
        "solution_count": int(model.SolCount),
        "mip_gap": (
            float(model.MIPGap)
            if settings.mode == "binary" and int(model.SolCount) > 0
            else None
        ),
        "objective_ntd2023_per_year": objective,
        "sizing": {
            "E_N_kwh": E_N,
            "P_B_kw_ac": P_B,
            "CC_regular_kw": CC,
        },
        "cost_components_ntd2023_per_year": cost_components,
        "cost_reconciliation_residual_ntd": float(cost_residual),
        "pure_season_overcontract_exact_ntd": float(pure_exact_cost),
        "pure_season_overcontract_solver_residual_ntd": pure_over_resid,
        "transition_resolved_overcontract_exact_ntd": float(transition_resolved_exact_cost),
        "transition_resolved_overcontract_solver_residual_ntd": transition_resolved_resid,
        "annual_energy": {
            "grid_import_kwh": float(p_grid.sum() * DELTA_T_HR),
            "charge_ac_kwh": float(p_ch.sum() * DELTA_T_HR),
            "discharge_ac_kwh": float(p_dis.sum() * DELTA_T_HR),
            "battery_side_discharge_kwh": float(p_dis.sum() * DELTA_T_HR / ETA_D),
            "pv_curtailment_kwh": float(pv_curt.sum() * DELTA_T_HR),
        },
        "physical_diagnostics": {
            "max_ac_balance_residual_kw": max_balance_resid,
            "max_segment_dynamics_residual_kwh": max_dyn_resid,
            "max_segment_cyclic_residual_kwh": cyclic_resid,
            "soc_min_realized": float(np.nanmin(soc)) if E_N > 1e-9 else None,
            "soc_max_realized": float(np.nanmax(soc)) if E_N > 1e-9 else None,
            "max_simultaneous_charge_discharge_kw": max_simultaneous,
            "simultaneous_hours_above_tol": simultaneous_hours,
            "simultaneous_tolerance_kw": SIMULTANEOUS_TOL_KW,
            "min_pure_season_solver_demand_aux_minus_exact_kw": (
                float(min_solver_aux_margin) if np.isfinite(min_solver_aux_margin) else None
            ),
        },
        "transition_settlement": {
            "objective_treatment": (
                "BILLING_PERIOD_TOU_MAX_PLUS_SEQUENTIAL_NONDUPLICATION; "
                "UNAMBIGUOUS_RATE_INCREMENTS_INCLUDED; ONLY_GENUINELY_RATE_AMBIGUOUS_"
                "INCREMENTS_OMITTED_AS_NONNEGATIVE_LOWER_BOUND"
            ),
            "fabricated_cross_season_rate_rule": False,
            "positive_transition_raw_overage_detected": bool(transition_positive_raw),
            "rate_ambiguous_incremental_overage_detected": bool(
                transition_ambiguous_incremental_total_kw > TRANSITION_OVERAGE_TOL_KW
            ),
            "rate_ambiguous_incremental_overage_total_kw": float(
                transition_ambiguous_incremental_total_kw
            ),
            "resolved_transition_overcontract_exact_ntd2023": float(
                transition_resolved_exact_cost
            ),
            "nonbinding_certificate": transition_certificate,
            "eob_finality": eob_finality,
            "proof_note": (
                "The benchmark omits only non-negative transition increments whose "
                "summer/non-summer basic rate is genuinely unresolved. If every such "
                "omitted incremental overage is zero at the lower-bound optimum, the "
                "full objective equals that lower bound at the same solution, so the "
                "transition rate ambiguity cannot improve or change the optimum."
            ),
        },
        "dispatch": dispatch,
        "billing_exact": billing_exact,
        "transition_settlement_detail": transition_detail,
    }
    return result
