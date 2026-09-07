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

For mixed-season billing periods, Class-A and Class-B billing demand uses the
audited hourly demand epigraph. Only a Class-C different-rate component keeps
two exact native seasonal MAX resultants because their endogenous ordering
selects the settlement rate. Every billing-period TOU maximum, source event,
and timestamp is recomputed exactly from the solved hourly dispatch for
diagnostics and reconciliation. Sequential non-duplication applies to that
global billing maximum. Each positive incremental overage is priced at the
basic-charge rate for the season containing the canonical maximum event. A
documented solver-scale numerical tie band uses the earliest seasonal maximum
event. A tiny unresolved guard is rejected for a Class-C different-rate
component; a Class-B equal-rate component retains that raw source status as a
non-cost-facing diagnostic. The May/October 50/50 treatment remains limited to
regular basic charges and is not used for over-contract settlement.

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
from typing import Any, Callable

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


CORE_VERSION = "v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9"

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
SIMULTANEOUS_TOL_KW = 1e-5
TRANSITION_OVERAGE_TOL_KW = 1e-6
BALANCE_TOL = 1e-5
# This is a numerical implementation convention, not a tariff parameter.  It
# is deliberately tied to the model's actual primal-feasibility tolerance and
# the pre-existing post-solve balance tolerance, rather than to a one-ULP
# floating-point distinction.  With Gurobi's default FeasibilityTol=1e-6 it
# evaluates to 1e-4 kW (0.1 W): 100 feasibility-tolerance units and less than
# two parts per billion of the derived campus-demand upper bound.
TRANSITION_TIE_BAND_MIN_KW = 1e-4
TRANSITION_TIE_BAND_FEASIBILITY_MULTIPLIER = 100.0
TRANSITION_TIE_BAND_FLOATING_MULTIPLIER = 100.0
# A second, explicitly documented guard separates the closed canonical-tie
# region from the later-source disjunct.  It is only a numerical-solver
# convention: an exact mathematical strict inequality cannot be encoded by a
# finite-tolerance MILP.  A solve that lands inside this guard is rejected by
# the post-solve provenance gate instead of being silently priced.
TRANSITION_TIE_SELECTION_GUARD_FEASIBILITY_MULTIPLIER = 10.0
TRANSITION_RATE_EQUALITY_TOL_NTD2023_PER_KW_MONTH = 1e-9
COST_RECONCILIATION_TOL_NTD = 1e-3


def transition_tie_band_kw(
    feasibility_tol: float,
    demand_scale_kw: float = 1.0,
) -> float:
    """Return the documented solver-safe transition numerical-tie band.

    The retained tariff semantics need a deterministic earliest-event source
    for numerical ties, but a continuous MILP cannot robustly encode an open
    ``difference > tolerance`` boundary with a one-ULP offset.  The band is
    therefore explicitly numerical and is never used as a tariff rate or an
    engineering demand tolerance.
    """
    tolerance = float(feasibility_tol)
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError(f"Feasibility tolerance must be finite and positive: {feasibility_tol!r}")
    scale = float(demand_scale_kw)
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError(f"Demand scale must be finite and positive: {demand_scale_kw!r}")
    return float(
        max(
            TRANSITION_TIE_BAND_MIN_KW,
            TRANSITION_TIE_BAND_FEASIBILITY_MULTIPLIER * tolerance,
            TRANSITION_TIE_BAND_FLOATING_MULTIPLIER * np.finfo(float).eps * scale,
        )
    )


def transition_tie_selection_guard_kw(feasibility_tol: float) -> float:
    """Return the solver-separation guard after the closed tie band.

    The guard is deliberately several primal-feasibility tolerances wide.  It
    is not a tariff tolerance; a realized value in the guard is an explicit
    provenance failure, rather than an invitation to select the cheaper rate.
    """
    tolerance = float(feasibility_tol)
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError(f"Feasibility tolerance must be finite and positive: {feasibility_tol!r}")
    return float(TRANSITION_TIE_SELECTION_GUARD_FEASIBILITY_MULTIPLIER * tolerance)


def classify_transition_source_with_guard(
    difference_later_minus_earlier_kw: float,
    tie_band_kw: float,
    selection_guard_kw: float,
) -> str:
    """Classify the Candidate-1 source disjunction including its fail-safe gap.

    ``d <= tie_band`` is the closed deterministic earliest-event region.  The
    later-season branch starts at ``tie_band + selection_guard``.  Values in
    between are deliberately not silently settled: they are too close to the
    non-representable strict boundary for a provenance-safe finite MILP.
    """
    difference = float(difference_later_minus_earlier_kw)
    band = float(tie_band_kw)
    guard = float(selection_guard_kw)
    if not math.isfinite(difference):
        raise ValueError("Transition maximum difference must be finite.")
    if not math.isfinite(band) or band <= 0.0:
        raise ValueError("Transition tie band must be finite and positive.")
    if not math.isfinite(guard) or guard <= 0.0:
        raise ValueError("Transition source-selection guard must be finite and positive.")
    if abs(difference) <= band:
        return "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP"
    if difference < -band:
        return "EARLIER_SEASON_CLEARLY_LARGER"
    if difference < band + guard:
        return "NUMERICAL_BOUNDARY_UNRESOLVED"
    return "LATER_SEASON_CLEARLY_LARGER"


def transition_boundary_settlement_accounting(
    settlement_class: str,
    source_policy_status: str,
    incremental_overage_kw: float,
) -> dict[str, bool | int | float]:
    """Classify whether a numerical-source guard affects settlement validity.

    A Class-B component may retain an unresolved source label for provenance,
    but identical audited rates mean that label cannot affect either its bill
    or the transition settlement certificate.  A Class-C unresolved source is
    rate-relevant and therefore remains a strict certificate failure.
    """
    affects_settlement = bool(
        settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
        and source_policy_status == "NUMERICAL_BOUNDARY_UNRESOLVED"
    )
    return {
        "boundary_affects_settlement": affects_settlement,
        "certificate_failure_count_increment": int(affects_settlement),
        "ambiguous_incremental_overage_kw": float(incremental_overage_kw)
        if affects_settlement
        else 0.0,
    }


def transition_tie_band_static_audit(
    feasibility_tol: float = 1e-6,
) -> dict[str, Any]:
    """Test source-level tie-band policy only; this is not a MILP solve."""
    band = transition_tie_band_kw(feasibility_tol)
    guard = transition_tie_selection_guard_kw(feasibility_tol)
    cases = (
        ("difference_eq_zero", 0.0, "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP"),
        (
            "difference_within_tie_band",
            0.5 * band,
            "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP",
        ),
        (
            "difference_eq_tie_band",
            band,
            "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP",
        ),
        (
            "difference_inside_selection_guard",
            band + 0.5 * guard,
            "NUMERICAL_BOUNDARY_UNRESOLVED",
        ),
        (
            "difference_eq_later_selection_threshold",
            band + guard,
            "LATER_SEASON_CLEARLY_LARGER",
        ),
        (
            "earlier_clearly_larger",
            -2.0 * band,
            "EARLIER_SEASON_CLEARLY_LARGER",
        ),
        (
            "later_clearly_larger",
            2.0 * band,
            "LATER_SEASON_CLEARLY_LARGER",
        ),
    )
    rows = [
        {
            "case": label,
            "difference_later_minus_earlier_kw": float(difference),
            "classification": classify_transition_source_with_guard(
                difference, band, guard
            ),
            "expected_classification": expected,
            "pass": classify_transition_source_with_guard(difference, band, guard)
            == expected,
        }
        for label, difference, expected in cases
    ]
    return {
        "status": "PASS" if all(bool(row["pass"]) for row in rows) else "FAIL",
        "feasibility_tol": float(feasibility_tol),
        "tie_band_kw": band,
        "selection_guard_kw": guard,
        "cases": rows,
        "scope": (
            "PYTHON_POLICY_ONLY_NOT_GUROBI_FEASIBILITY_PROOF; "
            "the production MILP rejects the open numerical guard "
            "(tie_band, tie_band + selection_guard)."
        ),
    }


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
    telemetry_callback: Callable[[dict[str, Any]], None] | None = None


@dataclass(frozen=True)
class LayerAResilienceRequirements:
    """Explicit, optional Layer A constraints for the shared annual core.

    The EOB calls the core with ``None`` and therefore retains its original
    economic formulation.  Layer A supplies the analytical worst-window
    reserve and AC-side power requirement derived outside the MILP.
    """

    alpha: float
    beta_h: int
    reserve_kwh_battery: float
    power_requirement_kw_ac: float


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
    max_timestamp_season: str | None = None,
) -> dict[str, Any]:
    """Resolve a transition over-contract rate from its maximum's season."""
    seasons = sorted(set(str(x) for x in active_seasons))
    if not seasons:
        raise RuntimeError(f"No active seasons for {month}/{tou_period}.")

    rates = {
        season: _matrix_rate(inputs.settlement_matrix, month, season, tou_period)
        for season in seasons
    }
    if max_timestamp_season is not None:
        selected_season = str(max_timestamp_season)
        if selected_season not in rates:
            raise RuntimeError(
                f"Maximum timestamp season {selected_season!r} is not active for "
                f"{month}/{tou_period}."
            )
        return {
            "rate_unambiguous": True,
            "resolved_rate": float(rates[selected_season]),
            "candidate_rates": {k: float(v) for k, v in rates.items()},
            "active_seasons": seasons,
            "selected_season": selected_season,
            "resolution_reason": "max_timestamp_season",
        }
    values = list(rates.values())
    unique = all(np.isclose(v, values[0], rtol=0.0, atol=1e-9) for v in values[1:])
    return {
        "rate_unambiguous": bool(unique),
        "resolved_rate": float(values[0]) if unique else None,
        "candidate_rates": {k: float(v) for k, v in rates.items()},
        "active_seasons": seasons,
        "selected_season": None,
        "resolution_reason": (
            "single_active_season"
            if len(seasons) == 1
            else "equal_rates_across_active_seasons"
            if unique
            else "different_rates_across_active_seasons"
        ),
    }


def classify_transition_component(
    active_seasons: list[str] | tuple[str, ...],
    candidate_rates: dict[str, float],
) -> str:
    """Classify a mixed-period TOU component from live calendar/rate data.

    The result intentionally depends only on the active seasonal calendar rows
    and audited settlement rates.  It is not a statement about a particular
    load/PV realization or an assumed May/October layout.
    """
    seasons = tuple(sorted({str(season) for season in active_seasons}))
    if not seasons or len(seasons) > 2:
        raise RuntimeError(f"Transition component must contain one or two seasons, got {seasons}.")
    if set(candidate_rates) != set(seasons):
        raise RuntimeError(
            "Transition component rate keys do not match active seasons: "
            f"seasons={seasons}, rate_keys={sorted(candidate_rates)}."
        )
    values = [float(candidate_rates[season]) for season in seasons]
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise RuntimeError(f"Transition component has invalid settlement rates: {candidate_rates}.")
    if len(seasons) == 1:
        return "CLASS_A_SINGLE_SEASON"
    # A Class-B shortcut is permitted only for identical audited tariff
    # values.  A merely-close but genuinely different rate must remain Class
    # C so it cannot become an inadvertent averaging rule.
    if values[0] == values[1]:
        return "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE"
    return "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"


def _transition_component_spec(
    inputs: AnnualDesignInputs,
    month: str,
    month_indices: np.ndarray,
    tou_period: str,
) -> dict[str, Any]:
    """Derive one transition TOU component from the production calendar.

    The chronological ordering guard is essential: the deterministic tie rule
    is defined by the earliest maximum *event*, not alphabetic season labels.
    The production calendar must therefore expose non-interleaving seasonal
    portions for a two-season transition component.
    """
    annual = inputs.annual
    month_df = annual.iloc[month_indices]
    period_mask = month_df["tou_period"].astype(str).to_numpy() == str(tou_period)
    period_indices = np.asarray(month_indices[period_mask], dtype=int)
    if len(period_indices) == 0:
        raise RuntimeError(f"No active timestamps for transition component {month}/{tou_period}.")

    season_values = month_df["season"].astype(str).to_numpy()
    active_seasons = tuple(sorted(set(season_values[period_mask].tolist())))
    season_indices: dict[str, np.ndarray] = {}
    for season in active_seasons:
        indices = np.asarray(
            month_indices[period_mask & (season_values == season)], dtype=int
        )
        if len(indices) == 0:
            raise RuntimeError(
                f"Empty season slice constructed for transition component {month}/{tou_period}/{season}."
            )
        season_indices[season] = indices

        matrix_rows = inputs.settlement_matrix.loc[
            inputs.settlement_matrix["billing_usage_period_id"].astype(str).eq(str(month))
            & inputs.settlement_matrix["season"].astype(str).eq(season)
            & inputs.settlement_matrix["tou_period"].astype(str).eq(str(tou_period))
        ]
        if len(matrix_rows) != 1:
            raise RuntimeError(
                "Expected exactly one active settlement-matrix row for transition "
                f"component {month}/{tou_period}/{season}; found {len(matrix_rows)}."
            )
        matrix_row = matrix_rows.iloc[0]
        if not bool(matrix_row["active_in_hourly_case"]):
            raise RuntimeError(
                f"Transition matrix row is inactive in the hourly case: {month}/{tou_period}/{season}."
            )
        if str(matrix_row["billing_period_role"]) != "transition":
            raise RuntimeError(
                f"Transition matrix row has invalid billing-period role: {month}/{tou_period}/{season}."
            )
        matrix_hour_count = int(pd.to_numeric(pd.Series([matrix_row["hour_count"]]), errors="raise").iloc[0])
        if matrix_hour_count != int(len(indices)):
            raise RuntimeError(
                "Transition matrix hour-count mismatch for "
                f"{month}/{tou_period}/{season}: matrix={matrix_hour_count}, calendar={len(indices)}."
            )

    candidate_rates = {
        season: _matrix_rate(inputs.settlement_matrix, month, season, tou_period)
        for season in active_seasons
    }
    settlement_class = classify_transition_component(
        list(active_seasons), candidate_rates
    )
    chronological_seasons = tuple(
        sorted(active_seasons, key=lambda season: int(season_indices[season][0]))
    )
    if len(chronological_seasons) == 2:
        early, later = chronological_seasons
        if int(season_indices[early][-1]) >= int(season_indices[later][0]):
            raise RuntimeError(
                "Transition calendar has interleaving seasonal timestamps and cannot "
                "apply the earliest-maximum-event rule with one seasonal selector: "
                f"{month}/{tou_period}, early={early}, later={later}."
            )

    return {
        "month": str(month),
        "tou_period": str(tou_period),
        "settlement_class": settlement_class,
        "active_seasons": active_seasons,
        "chronological_seasons": chronological_seasons,
        "period_indices": period_indices,
        "season_indices": season_indices,
        "candidate_rates": {season: float(rate) for season, rate in candidate_rates.items()},
    }


def transition_component_classification(
    inputs: AnnualDesignInputs,
) -> list[dict[str, Any]]:
    """Return serializable live-calendar classifications for all transitions."""
    rows: list[dict[str, Any]] = []
    for month, month_indices in _month_groups(inputs.annual).items():
        if _pure_month_season(inputs.annual, month_indices) is not None:
            continue
        for tou_period in TOU_ORDER:
            period_mask = (
                inputs.annual.iloc[month_indices]["tou_period"].astype(str).to_numpy()
                == tou_period
            )
            if not bool(np.any(period_mask)):
                continue
            spec = _transition_component_spec(inputs, month, month_indices, tou_period)
            rows.append(
                {
                    "billing_usage_period_id": month,
                    "tou_period": tou_period,
                    "settlement_class": spec["settlement_class"],
                    "active_seasons": list(spec["active_seasons"]),
                    "chronological_seasons": list(spec["chronological_seasons"]),
                    "candidate_rates_ntd2023_per_kw_month": dict(spec["candidate_rates"]),
                    "period_hour_count": int(len(spec["period_indices"])),
                    "season_hour_counts": {
                        season: int(len(indices))
                        for season, indices in spec["season_indices"].items()
                    },
                    "season_first_timestamp": {
                        season: str(inputs.annual.iloc[int(indices[0])]["timestamp"])
                        for season, indices in spec["season_indices"].items()
                    },
                    "season_last_timestamp": {
                        season: str(inputs.annual.iloc[int(indices[-1])]["timestamp"])
                        for season, indices in spec["season_indices"].items()
                    },
                }
            )
    return rows


def transition_formulation_metadata(inputs: AnnualDesignInputs) -> dict[str, Any]:
    """Summarize reduced-native-MAX topology from live calendar data."""
    components = transition_component_classification(inputs)
    class_a = "CLASS_A_SINGLE_SEASON"
    class_b = "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE"
    class_c = "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
    class_counts = {
        label: int(sum(row["settlement_class"] == label for row in components))
        for label in (
            class_a,
            class_b,
            class_c,
        )
    }
    exact_seasonal_max_count = int(
        sum(
            len(row["active_seasons"])
            for row in components
            if row["settlement_class"] == class_c
        )
    )
    native_max_hourly_operands_by_class = {
        label: int(
            sum(
                sum(int(count) for count in row["season_hour_counts"].values())
                for row in components
                if row["settlement_class"] == label
            )
            if label == class_c
            else 0
        )
        for label in (class_a, class_b, class_c)
    }
    billing_epigraph_rows_by_class = {
        label: int(
            sum(
                int(row["period_hour_count"])
                for row in components
                if row["settlement_class"] == label
            )
        )
        if label in (class_a, class_b)
        else 0
        for label in (class_a, class_b, class_c)
    }
    class_c_demand_link_rows = int(
        sum(
            len(row["active_seasons"])
            for row in components
            if row["settlement_class"] == class_c
        )
    )
    return {
        "component_count": int(len(components)),
        "class_counts": class_counts,
        "exact_seasonal_max_constraints": exact_seasonal_max_count,
        "exact_global_max_constraints": 0,
        "exact_max_general_constraints_total": exact_seasonal_max_count,
        "native_max_hourly_operands_by_class": native_max_hourly_operands_by_class,
        "native_max_hourly_operands": int(
            sum(native_max_hourly_operands_by_class.values())
        ),
        "billing_epigraph_rows_by_class": billing_epigraph_rows_by_class,
        "billing_epigraph_rows_total": int(
            sum(billing_epigraph_rows_by_class.values())
        ),
        "class_c_demand_link_rows": class_c_demand_link_rows,
        "economically_necessary_class_c_source_binaries": class_counts[class_c],
        "transition_indicator_constraints": 0,
        "class_c_bounded_product_auxiliaries": class_counts[class_c],
    }


def transition_class_c_cost_from_product(
    rate_early: float,
    rate_later: float,
    overcontract_quantity_kw: float,
    source_later_binary: int,
    product_later_kw: float,
) -> float:
    """Evaluate the bounded Class-C rate product for static algebra tests."""
    if int(source_later_binary) not in {0, 1}:
        raise ValueError("source_later_binary must be 0 or 1.")
    quantity = float(overcontract_quantity_kw)
    product = float(product_later_kw)
    if quantity < -BALANCE_TOL or product < -BALANCE_TOL:
        raise ValueError("Transition cost quantities must be non-negative.")
    if not np.isclose(
        product,
        int(source_later_binary) * quantity,
        rtol=0.0,
        atol=BALANCE_TOL,
    ):
        raise ValueError("Product does not satisfy w = y * W within the static tolerance.")
    return float(rate_early * quantity + (rate_later - rate_early) * product)


def _transition_reference_overcontract_cost(
    inputs: AnnualDesignInputs,
    p_grid_reference_kw: np.ndarray,
    tie_band_kw: float,
    selection_guard_kw: float,
) -> float:
    """Upper-bound a feasible idle-BESS schedule's transition/pure overcharge.

    The reference uses zero regular contract capacity.  Pricing a transition
    component at the larger active rate is conservative for the finite-objective
    bound; source feasibility is separately checked so the reference schedule
    remains available to the Candidate-1 disjunction.
    """
    annual = inputs.annual
    over_rule = inputs.settlement_interface["overcontract_rule"]
    tier1_mult = float(over_rule["tier1_multiplier"])
    tier2_mult = float(over_rule["tier2_multiplier"])
    total = 0.0
    for month, month_indices in _month_groups(annual).items():
        month_season = _pure_month_season(annual, month_indices)
        prior_raw = 0.0
        applicable = (
            PURE_APPLICABLE_PERIODS[month_season]
            if month_season is not None
            else TOU_ORDER
        )
        for tou_period in applicable:
            mask = annual.iloc[month_indices]["tou_period"].astype(str).to_numpy() == tou_period
            period_indices = np.asarray(month_indices[mask], dtype=int)
            if len(period_indices) == 0:
                continue
            demand = float(inputs.kappa * np.max(p_grid_reference_kw[period_indices]))
            raw = demand  # reference CC = 0
            lower = min(prior_raw, raw)
            tier1_kw = 0.0
            tier2_kw = max(0.0, raw - lower)
            if month_season is None:
                spec = _transition_component_spec(inputs, month, month_indices, tou_period)
                if spec["settlement_class"] == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":
                    early, later = spec["chronological_seasons"]
                    seasonal = {
                        season: float(inputs.kappa * np.max(p_grid_reference_kw[indices]))
                        for season, indices in spec["season_indices"].items()
                    }
                    difference = seasonal[later] - seasonal[early]
                    if tie_band_kw < difference < tie_band_kw + selection_guard_kw:
                        raise RuntimeError(
                            "The finite-bound idle reference lies in the documented "
                            "Candidate-1 numerical source-selection guard for "
                            f"{month}/{tou_period}; no conservative finite bound is "
                            "claimed until the calendar/data case is resolved."
                        )
                rate = max(float(value) for value in spec["candidate_rates"].values())
            else:
                rate = _matrix_rate(inputs.settlement_matrix, month, month_season, tou_period)
            total += float(rate) * (tier1_mult * tier1_kw + tier2_mult * tier2_kw)
            prior_raw = max(prior_raw, raw)
    return float(total)


def _finite_design_bounds(
    inputs: AnnualDesignInputs,
    coeff: dict[str, Any],
    layer_a_requirements: LayerAResilienceRequirements | None,
    tie_band_kw: float,
    selection_guard_kw: float,
) -> dict[str, Any]:
    """Derive valid finite design bounds from an explicit idle reference plan.

    The plan has zero battery dispatch, zero regular contract capacity and
    grid import ``max(load - pv, 0)`` with excess PV curtailed.  If Layer A is
    active it carries its analytical reserve in the Xu segments and installs
    its required power, while remaining idle.  All objective terms are
    non-negative, so this feasible plan's cost is a valid upper bound on the
    optimum and hence on the design decisions with strictly positive annual
    unit cost coefficients.
    """
    annual = inputs.annual
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    reference_grid = np.maximum(load - pv, 0.0)
    reserve = (
        0.0
        if layer_a_requirements is None
        else float(layer_a_requirements.reserve_kwh_battery)
    )
    power_requirement = (
        0.0
        if layer_a_requirements is None
        else float(layer_a_requirements.power_requirement_kw_ac)
    )
    reference_energy = reserve / float(SOC_MAX - SOC_MIN)
    reference_power = power_requirement
    c_e = float(coeff["annualized_C_E"] + coeff["fom_E"])
    c_p = float(coeff["annualized_C_P"] + coeff["fom_P"])
    if c_e <= 0.0 or c_p <= 0.0:
        raise RuntimeError("Strictly positive annual energy/power design costs are required for finite bounds.")
    energy_cost = float(
        np.dot(inputs.energy_rate_ntd2023_per_kwh, reference_grid) * DELTA_T_HR
    )
    over_cost = _transition_reference_overcontract_cost(
        inputs, reference_grid, tie_band_kw, selection_guard_kw
    )
    reference_objective = float(
        c_e * reference_energy + c_p * reference_power + energy_cost + over_cost
    )
    if not math.isfinite(reference_objective) or reference_objective < 0.0:
        raise RuntimeError("Idle reference objective is not finite and non-negative.")
    basic_total = sum(
        _regular_basic_rate(inputs, month, _pure_month_season(annual, indices))
        for month, indices in _month_groups(annual).items()
    )
    if not math.isfinite(basic_total) or basic_total <= 0.0:
        raise RuntimeError("Strictly positive annual regular-basic charge is required for a finite CC bound.")
    minimum_grid_import_kwh = float(
        max(0.0, float(np.sum(load) - np.sum(pv))) * DELTA_T_HR
    )
    minimum_energy_rate = float(np.min(inputs.energy_rate_ntd2023_per_kwh))
    if not math.isfinite(minimum_energy_rate) or minimum_energy_rate < 0.0:
        raise RuntimeError("Hourly energy rates must have a finite non-negative minimum.")
    energy_cost_lower = float(minimum_energy_rate * minimum_grid_import_kwh)
    residual_budget = float(
        reference_objective
        - energy_cost_lower
        - c_e * reference_energy
        - c_p * reference_power
    )
    if residual_budget < -COST_RECONCILIATION_TOL_NTD:
        raise RuntimeError(
            "Idle-reference finite-bound residual is negative; the non-negative "
            "objective proof does not hold."
        )
    residual_budget_safe = float(max(0.0, residual_budget) + COST_RECONCILIATION_TOL_NTD)
    return {
        "reference_objective_upper_ntd2023_per_year": reference_objective,
        "reference_idle_grid_energy_cost_ntd2023_per_year": energy_cost,
        "reference_idle_overcontract_cost_upper_ntd2023_per_year": over_cost,
        "annual_grid_import_lower_kwh": minimum_grid_import_kwh,
        "annual_energy_cost_lower_ntd2023_per_year": energy_cost_lower,
        "residual_design_budget_upper_ntd2023_per_year": residual_budget_safe,
        "E_N_ub_kwh": float(reference_energy + residual_budget_safe / c_e),
        "P_B_ub_kw_ac": float(reference_power + residual_budget_safe / c_p),
        "CC_ub_kw": float(residual_budget_safe / basic_total),
        "reference_E_N_kwh": float(reference_energy),
        "reference_P_B_kw_ac": float(reference_power),
        "reference_CC_kw": 0.0,
        "basic_charge_sum_ntd2023_per_kw_year": float(basic_total),
        "derivation": {
            "reference_schedule": (
                "idle BESS; p_grid=max(load-pv,0); surplus PV curtailed; "
                "CC=0; Layer-A reserve/power installed when requested"
            ),
            "design_budget": (
                "reference objective minus annual energy lower bound and "
                "mandatory Layer-A energy/power cost, plus reconciliation padding"
            ),
            "E_N_ub_kwh": "E_min + residual_design_budget / (annualized_C_E + fom_E)",
            "P_B_ub_kw_ac": "P_min + residual_design_budget / (annualized_C_P + fom_P)",
            "CC_ub_kw": "residual_design_budget / sum(monthly regular basic rates)",
        },
    }


def build_eob_model(
    inputs: AnnualDesignInputs,
    settings: SolveSettings,
    layer_a_requirements: LayerAResilienceRequirements | None = None,
) -> tuple[gp.Model, dict[str, Any]]:
    mode = settings.mode.strip().lower()
    if mode not in {"binary", "relaxed"}:
        raise ValueError("SolveSettings.mode must be 'binary' or 'relaxed'.")
    if layer_a_requirements is not None:
        if isinstance(layer_a_requirements.alpha, (bool, np.bool_)):
            raise ValueError("Layer A alpha must be a numeric fraction, not boolean.")
        alpha = float(layer_a_requirements.alpha)
        if not np.isfinite(alpha) or not (0.0 < alpha <= 1.0):
            raise ValueError("Layer A alpha must be finite and within (0, 1].")
        if isinstance(layer_a_requirements.beta_h, (bool, np.bool_)):
            raise ValueError("Layer A beta_h must be a whole-hour integer, not boolean.")
        beta_h = float(layer_a_requirements.beta_h)
        if not np.isfinite(beta_h) or not beta_h.is_integer() or beta_h <= 0.0:
            raise ValueError("Layer A beta_h must be a positive whole-hour integer.")
        for label, value in {
            "reserve_kwh_battery": layer_a_requirements.reserve_kwh_battery,
            "power_requirement_kw_ac": layer_a_requirements.power_requirement_kw_ac,
        }.items():
            if not np.isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"Layer A {label} must be finite and non-negative.")

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

    feasibility_tol = float(model.Params.FeasibilityTol)
    observed_demand_scale_kw = float(max(1.0, float(np.max(load))))
    tie_band_kw = transition_tie_band_kw(
        feasibility_tol, observed_demand_scale_kw
    )
    selection_guard_kw = transition_tie_selection_guard_kw(feasibility_tol)
    model_bounds = _finite_design_bounds(
        inputs,
        coeff,
        layer_a_requirements,
        tie_band_kw,
        selection_guard_kw,
    )
    E_N_ub = float(model_bounds["E_N_ub_kwh"])
    P_B_ub = float(model_bounds["P_B_ub_kw_ac"])
    CC_ub = float(model_bounds["CC_ub_kw"])
    if layer_a_requirements is not None:
        E_N_ub = max(
            E_N_ub,
            float(layer_a_requirements.reserve_kwh_battery) / float(SOC_MAX - SOC_MIN),
        )
        P_B_ub = max(P_B_ub, float(layer_a_requirements.power_requirement_kw_ac))
    reserve_floor_kwh = (
        0.0
        if layer_a_requirements is None
        else float(layer_a_requirements.reserve_kwh_battery)
    )
    if mode == "binary":
        # In a charge-mode hour p_dis=0, and the reserve/capacity interval
        # gives eta_c*p_ch <= 0.8*E_N - reserve.  In discharge mode p_ch=0,
        # the same interval gives p_dis/eta_d <= 0.8*E_N - reserve; non-export
        # AC balance also gives p_dis <= load.  These are valid tightening
        # bounds for the binary formulation, not new operating assumptions.
        available_storage_swing_kwh = max(
            0.0,
            float((SOC_MAX - SOC_MIN) * E_N_ub - reserve_floor_kwh),
        )
        p_charge_ub_kw = min(P_B_ub, available_storage_swing_kwh / ETA_C)
        p_discharge_ub_by_hour_kw = {
            t: min(
                P_B_ub,
                ETA_D * available_storage_swing_kwh,
                float(load[t]),
            )
            for t in TT
        }
    else:
        available_storage_swing_kwh = None
        p_charge_ub_kw = P_B_ub
        p_discharge_ub_by_hour_kw = {t: P_B_ub for t in TT}
    p_grid_ub_by_hour_kw = {
        t: float(load[t] + p_charge_ub_kw) for t in TT
    }
    model_bounds.update(
        {
            "E_N_ub_kwh": float(E_N_ub),
            "P_B_ub_kw_ac": float(P_B_ub),
            "CC_ub_kw": float(CC_ub),
            "gurobi_feasibility_tol": feasibility_tol,
            "observed_demand_scale_kw": observed_demand_scale_kw,
            "transition_tie_band_kw": tie_band_kw,
            "transition_tie_selection_guard_kw": selection_guard_kw,
            "reserve_floor_for_operating_bound_kwh": reserve_floor_kwh,
            "available_storage_swing_upper_kwh": available_storage_swing_kwh,
            "p_charge_ub_kw": float(p_charge_ub_kw),
            "p_discharge_ub_max_kw": float(max(p_discharge_ub_by_hour_kw.values())),
            "p_grid_ub_max_kw": float(max(p_grid_ub_by_hour_kw.values())),
            "operating_bound_derivation": (
                "binary mode: eta_c*p_ch <= (SOC_MAX-SOC_MIN)*E_N_ub-reserve; "
                "p_dis/eta_d <= the same swing and p_dis<=load; "
                "p_grid<=load+p_ch. Relaxed mode retains the safe P_B upper bound."
            ),
        }
    )

    # Sizing decisions.
    E_N = model.addVar(lb=0.0, ub=E_N_ub, name="E_N_kwh")
    P_B = model.addVar(lb=0.0, ub=P_B_ub, name="P_B_kw_ac")
    CC = model.addVar(lb=0.0, ub=CC_ub, name="CC_regular_kw")
    if layer_a_requirements is not None:
        model.addConstr(
            P_B >= float(layer_a_requirements.power_requirement_kw_ac),
            name="layer_a_power_adequacy",
        )

    # Hourly aggregate operating variables.
    p_grid = model.addVars(
        TT,
        lb=0.0,
        ub=p_grid_ub_by_hour_kw,
        name="p_grid_kw",
    )
    p_ch = model.addVars(TT, lb=0.0, ub=p_charge_ub_kw, name="p_ch_kw_ac")
    p_dis = model.addVars(
        TT, lb=0.0, ub=p_discharge_ub_by_hour_kw, name="p_dis_kw_ac"
    )
    pv_curt = model.addVars(
        TT, lb=0.0, ub={t: float(pv[t]) for t in TT}, name="pv_curt_kw"
    )

    # Xu-derived intertemporal segment states / flows.
    e_seg = model.addVars(
        STATES,
        K,
        lb=0.0,
        ub={
            (t, k): float(SEGMENT_WIDTHS[k] * E_N_ub)
            for t in STATES
            for k in K
        },
        name="e_seg_kwh",
    )
    p_ch_seg = model.addVars(
        TT, K, lb=0.0, ub=p_charge_ub_kw, name="p_ch_seg_kw_ac"
    )
    p_dis_seg = model.addVars(
        TT,
        K,
        lb=0.0,
        ub={(t, k): p_discharge_ub_by_hour_kw[t] for t in TT for k in K},
        name="p_dis_seg_kw_ac",
    )

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
        if layer_a_requirements is not None:
            # physical_e = SOC_MIN * E_N + sum(e_seg). Therefore this is
            # exactly the locked floor physical_e >= SOC_MIN*E_N + R.
            model.addConstr(
                gp.quicksum(e_seg[t, k] for k in K)
                >= float(layer_a_requirements.reserve_kwh_battery),
                name=f"layer_a_reserve_floor_t{t}",
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

    # Over-contract settlement. Pure-season periods retain the audited standard
    # rule. Transition Class A/B components use the billing-demand epigraph;
    # only Class C keeps exact native seasonal MAX resultants because their
    # ordering is economically necessary for the different-rate source choice.
    over_rule = inputs.settlement_interface.get("overcontract_rule", {})
    tier1_frac = float(over_rule.get("tier1_threshold_fraction", np.nan))
    tier1_mult = float(over_rule.get("tier1_multiplier", np.nan))
    tier2_mult = float(over_rule.get("tier2_multiplier", np.nan))
    if not np.isclose(tier1_frac, 0.10) or not np.isclose(tier1_mult, 2.0) or not np.isclose(tier2_mult, 3.0):
        raise RuntimeError("Unexpected 14b over-contract tier metadata.")
    tier_threshold = model.addVar(
        lb=0.0,
        ub=tier1_frac * CC_ub,
        name="over_tier1_threshold_kw",
    )
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

        period_demand_upper_kw: dict[str, float] = {}
        for period_for_bound in applicable:
            period_mask_for_bound = (
                month_df["tou_period"].astype(str).to_numpy() == period_for_bound
            )
            period_idx_for_bound = np.asarray(idx[period_mask_for_bound], dtype=int)
            if len(period_idx_for_bound) == 0:
                continue
            period_demand_upper_kw[period_for_bound] = float(
                inputs.kappa
                * max(float(p_grid_ub_by_hour_kw[int(t)]) for t in period_idx_for_bound)
            )
        cumulative_demand_upper_kw = 0.0

        for period in applicable:
            period_mask = month_df["tou_period"].astype(str).to_numpy() == period
            active_idx = idx[period_mask]
            if len(active_idx) == 0:
                continue
            demand_ub = float(period_demand_upper_kw[period])
            cumulative_demand_upper_kw = max(cumulative_demand_upper_kw, demand_ub)
            tier_cumulative_ub = min(cumulative_demand_upper_kw, tier1_frac * CC_ub)
            D = model.addVar(
                lb=0.0, ub=demand_ub, name=f"D_{month}_{period}_kw"
            )
            raw = model.addVar(
                lb=0.0, ub=demand_ub, name=f"raw_over_{month}_{period}_kw"
            )
            z = model.addVar(
                lb=0.0,
                ub=cumulative_demand_upper_kw,
                name=f"cum_over_{month}_{period}_kw",
            )
            s_tier = model.addVar(
                lb=0.0,
                ub=tier_cumulative_ub,
                name=f"cum_tier1_{month}_{period}_kw",
            )

            transition_spec: dict[str, Any] | None = None
            transition_seasonal_max_grid: dict[str, gp.Var] = {}
            transition_seasonal_max_grid_ub: dict[str, float] = {}
            transition_source_later: gp.Var | None = None
            transition_product_later: gp.Var | None = None
            transition_w_upper_kw: float | None = None
            transition_difference_bounds_kw: dict[str, float] | None = None
            if season is None:
                transition_spec = _transition_component_spec(
                    inputs, month, idx, period
                )
                settlement_class = str(transition_spec["settlement_class"])
                if settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":
                    # Rate selection is endogenous only for Class C. Preserve an
                    # exact seasonal resultant for each active season, then use
                    # two billing-demand links instead of a redundant global MAX.
                    for season_component, season_idx in transition_spec["season_indices"].items():
                        seasonal_grid_ub = max(
                            float(p_grid_ub_by_hour_kw[int(t)])
                            for t in season_idx.tolist()
                        )
                        max_grid = model.addVar(
                            lb=0.0,
                            ub=seasonal_grid_ub,
                            name=f"transition_max_grid_{month}_{period}_{season_component}_kw",
                        )
                        model.addGenConstrMax(
                            max_grid,
                            [p_grid[int(t)] for t in season_idx.tolist()],
                            name=f"transition_exact_max_{month}_{period}_{season_component}",
                        )
                        transition_seasonal_max_grid[season_component] = max_grid
                        transition_seasonal_max_grid_ub[season_component] = float(
                            seasonal_grid_ub
                        )
                    for season_component, max_grid in transition_seasonal_max_grid.items():
                        model.addConstr(
                            D >= inputs.kappa * max_grid,
                            name=(
                                "transition_demand_ge_seasonal_max_"
                                f"{month}_{period}_{season_component}"
                            ),
                        )
                elif settlement_class in {
                    "CLASS_A_SINGLE_SEASON",
                    "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE",
                }:
                    # A/B have no cost-facing seasonal source distinction. The
                    # standard billing epigraph preserves their in-model demand
                    # quantity; exact maxima/timestamps are recomputed ex-post.
                    for t in active_idx.tolist():
                        model.addConstr(
                            D >= inputs.kappa * p_grid[int(t)],
                            name=f"transition_demand_epi_{month}_{period}_t{int(t)}",
                        )
                else:
                    raise RuntimeError(
                        "Unknown transition settlement class for demand formulation: "
                        f"{settlement_class!r}."
                    )
            else:
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
                rate = float(rate_info["resolved_rate"])
                month_cost += rate * (
                    tier1_mult * delta_s + tier2_mult * (delta_z - delta_s)
                )
            else:
                if transition_spec is None:
                    raise RuntimeError("Transition specification was not constructed.")
                W = 3.0 * delta_z - delta_s
                settlement_class = str(transition_spec["settlement_class"])
                active_seasons = list(transition_spec["active_seasons"])
                candidate_rates = dict(transition_spec["candidate_rates"])
                if settlement_class == "CLASS_A_SINGLE_SEASON":
                    selected_season = active_seasons[0]
                    rate = float(candidate_rates[selected_season])
                    rate_info = {
                        "rate_unambiguous": True,
                        "resolved_rate": rate,
                        "candidate_rates": candidate_rates,
                        "active_seasons": active_seasons,
                        "resolution_reason": "class_a_single_active_season",
                    }
                    month_cost += rate * W
                elif settlement_class == "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE":
                    rate_values = list(candidate_rates.values())
                    if rate_values[0] != rate_values[1]:
                        raise RuntimeError(f"Class-B rate equality failed for {month}/{period}.")
                    rate = float(rate_values[0])
                    rate_info = {
                        "rate_unambiguous": True,
                        "resolved_rate": rate,
                        "candidate_rates": candidate_rates,
                        "active_seasons": active_seasons,
                        "resolution_reason": "class_b_equal_settlement_rates",
                    }
                    month_cost += rate * W
                elif settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":
                    early, later = transition_spec["chronological_seasons"]
                    early_demand_ub = float(
                        inputs.kappa * transition_seasonal_max_grid_ub[early]
                    )
                    later_demand_ub = float(
                        inputs.kappa * transition_seasonal_max_grid_ub[later]
                    )
                    difference_lower = -early_demand_ub
                    difference_upper = later_demand_ub
                    if difference_upper < tie_band_kw + selection_guard_kw:
                        raise RuntimeError(
                            "Derived later-season maximum bound cannot support a solver-safe "
                            f"Class-C source selection for {month}/{period}."
                        )
                    transition_source_later = model.addVar(
                        vtype=GRB.BINARY,
                        name=f"transition_source_later_{month}_{period}",
                    )
                    difference_expr = inputs.kappa * (
                        transition_seasonal_max_grid[later]
                        - transition_seasonal_max_grid[early]
                    )
                    model.addConstr(
                        difference_expr
                        <= tie_band_kw
                        + (difference_upper - tie_band_kw) * transition_source_later,
                        name=f"transition_source_early_or_tie_{month}_{period}",
                    )
                    model.addConstr(
                        difference_expr
                        >= difference_lower * (1.0 - transition_source_later)
                        + (tie_band_kw + selection_guard_kw) * transition_source_later,
                        name=f"transition_source_later_clear_{month}_{period}",
                    )
                    transition_w_upper_kw = float(3.0 * cumulative_demand_upper_kw)
                    transition_product_later = model.addVar(
                        lb=0.0,
                        ub=transition_w_upper_kw,
                        name=f"transition_rate_product_later_{month}_{period}_kw",
                    )
                    model.addConstr(
                        W >= 0.0,
                        name=f"transition_overcontract_quantity_nonnegative_{month}_{period}",
                    )
                    model.addConstr(
                        W <= transition_w_upper_kw,
                        name=f"transition_overcontract_quantity_bound_{month}_{period}",
                    )
                    model.addConstr(
                        transition_product_later <= W,
                        name=f"transition_rate_product_le_quantity_{month}_{period}",
                    )
                    model.addConstr(
                        transition_product_later
                        <= transition_w_upper_kw * transition_source_later,
                        name=f"transition_rate_product_le_selector_{month}_{period}",
                    )
                    model.addConstr(
                        transition_product_later
                        >= W - transition_w_upper_kw * (1.0 - transition_source_later),
                        name=f"transition_rate_product_ge_hull_{month}_{period}",
                    )
                    rate_early = float(candidate_rates[early])
                    rate_later = float(candidate_rates[later])
                    month_cost += rate_early * W + (
                        rate_later - rate_early
                    ) * transition_product_later
                    transition_difference_bounds_kw = {
                        "lower": difference_lower,
                        "upper": difference_upper,
                    }
                    rate_info = {
                        "rate_unambiguous": True,
                        "resolved_rate": None,
                        "candidate_rates": candidate_rates,
                        "active_seasons": active_seasons,
                        "resolution_reason": "class_c_exact_max_source_selector",
                    }
                else:
                    raise RuntimeError(
                        f"Unknown transition settlement class for {month}/{period}: {settlement_class}."
                    )

            aux_periods[period] = {
                "D": D,
                "raw": raw,
                "z": z,
                "s": s_tier,
                "rate": float(rate_info["resolved_rate"]) if rate_info["resolved_rate"] is not None else None,
                "rate_unambiguous": True,
                "candidate_rates": rate_info["candidate_rates"],
                "active_seasons": rate_info["active_seasons"],
                "resolution_reason": rate_info["resolution_reason"],
                "objective_included": True,
                "settlement_class": None if transition_spec is None else transition_spec["settlement_class"],
                "transition_spec": transition_spec,
                "transition_seasonal_max_grid": transition_seasonal_max_grid,
                "transition_seasonal_max_grid_ub": transition_seasonal_max_grid_ub,
                "transition_source_later": transition_source_later,
                "transition_product_later": transition_product_later,
                "transition_w_upper_kw": transition_w_upper_kw,
                "transition_difference_bounds_kw": transition_difference_bounds_kw,
                "transition_tie_band_kw": tie_band_kw if transition_spec is not None else None,
                "transition_selection_guard_kw": selection_guard_kw if transition_spec is not None else None,
                "demand_upper_kw": demand_ub,
                "cumulative_demand_upper_kw": cumulative_demand_upper_kw,
                "bound_derivation": (
                    "D and seasonal MAX upper bounds derive from hourly p_grid upper "
                    "bounds; raw/z/s use the existing sequential cumulative-demand "
                    "structure; Class-C W uses 3 times the cumulative demand bound; "
                    "difference bounds are [-D_early_bar, D_later_bar]."
                ),
            }
            z_prev = z
            s_prev = s_tier

        over_month_terms[month] = month_cost
        if season is None:
            transition_resolved_terms.append(month_cost)
            billing_aux[month] = {
                "season": "transition",
                "transition_overcontract_in_objective": True,
                "max_timestamp_season_rate_increments_included": True,
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
        "finite_design_bounds": model_bounds,
        "transition_component_classification": transition_component_classification(inputs),
        "transition_formulation_metadata": transition_formulation_metadata(inputs),
        "layer_a_requirements": layer_a_requirements,
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


def _safe_gurobi_telemetry_attribute(model: gp.Model, attribute: str) -> int | float | None:
    """Read an optional Gurobi attribute without masking solver outcomes."""
    try:
        value = getattr(model, attribute)
    except (AttributeError, gp.GurobiError):
        return None
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    return None


def _emit_solve_telemetry(
    settings: SolveSettings,
    event: str,
    **payload: Any,
) -> None:
    """Emit optional solve-boundary telemetry without changing model behavior."""
    callback = settings.telemetry_callback
    if callback is None:
        return
    callback(
        {
            "event": event,
            "monotonic_seconds": float(time.perf_counter()),
            **payload,
        }
    )


def _model_structure_telemetry(model: gp.Model) -> dict[str, int | float | None]:
    return {
        "rows": _safe_gurobi_telemetry_attribute(model, "NumConstrs"),
        "columns": _safe_gurobi_telemetry_attribute(model, "NumVars"),
        "binary_variables": _safe_gurobi_telemetry_attribute(model, "NumBinVars"),
        "integer_variables": _safe_gurobi_telemetry_attribute(model, "NumIntVars"),
        "general_constraints": _safe_gurobi_telemetry_attribute(model, "NumGenConstrs"),
    }


def _model_optimize_telemetry(model: gp.Model) -> dict[str, int | float | str | None]:
    status_code = _safe_gurobi_telemetry_attribute(model, "Status")
    status_name = (
        _model_status_name(int(status_code)) if status_code is not None else None
    )
    solution_count = _safe_gurobi_telemetry_attribute(model, "SolCount")
    has_solution = solution_count is not None and int(solution_count) > 0
    return {
        "status_code": status_code,
        "status": status_name,
        "gurobi_runtime_sec": _safe_gurobi_telemetry_attribute(model, "Runtime"),
        "solution_count": solution_count,
        "node_count": _safe_gurobi_telemetry_attribute(model, "NodeCount"),
        "iteration_count": _safe_gurobi_telemetry_attribute(model, "IterCount"),
        "best_bound": _safe_gurobi_telemetry_attribute(model, "ObjBound"),
        "mip_gap": (
            _safe_gurobi_telemetry_attribute(model, "MIPGap") if has_solution else None
        ),
        "incumbent_objective": (
            _safe_gurobi_telemetry_attribute(model, "ObjVal") if has_solution else None
        ),
    }


def solve_eob(
    inputs: AnnualDesignInputs,
    settings: SolveSettings,
    layer_a_requirements: LayerAResilienceRequirements | None = None,
) -> dict[str, Any]:
    construction_started = time.perf_counter()
    _emit_solve_telemetry(settings, "model_construction_started")
    try:
        model, h = build_eob_model(inputs, settings, layer_a_requirements)
        if settings.telemetry_callback is not None:
            model.update()
        construction_wall = time.perf_counter() - construction_started
        _emit_solve_telemetry(
            settings,
            "model_construction_finished",
            wall_seconds=float(construction_wall),
            model_structure=_model_structure_telemetry(model),
        )
    except Exception as exc:
        _emit_solve_telemetry(
            settings,
            "model_construction_failed",
            wall_seconds=float(time.perf_counter() - construction_started),
            exception_type=type(exc).__name__,
            exception_message=str(exc),
        )
        raise

    optimize_started = time.perf_counter()
    _emit_solve_telemetry(settings, "gurobi_optimize_started")
    try:
        model.optimize()
    finally:
        wall = time.perf_counter() - optimize_started
        _emit_solve_telemetry(
            settings,
            "gurobi_optimize_finished",
            wall_seconds=float(wall),
            model_optimize=_model_optimize_telemetry(model),
        )

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

    layer_a_diagnostics: dict[str, Any] | None = None
    if layer_a_requirements is not None:
        reserve = float(layer_a_requirements.reserve_kwh_battery)
        power_requirement = float(layer_a_requirements.power_requirement_kw_ac)
        reserve_margin = physical_e - (SOC_MIN * E_N + reserve)
        layer_a_diagnostics = {
            "alpha": float(layer_a_requirements.alpha),
            "beta_h": int(layer_a_requirements.beta_h),
            "reserve_kwh_battery": reserve,
            "power_requirement_kw_ac": power_requirement,
            "annual_reserve_floor": {
                "minimum_margin_kwh": float(np.min(reserve_margin)),
                "maximum_violation_kwh": float(max(0.0, -np.min(reserve_margin))),
                "violating_hours": int(np.sum(reserve_margin < -BALANCE_TOL)),
            },
            "power_adequacy": {
                "margin_kw_ac": float(P_B - power_requirement),
                "violation_kw_ac": float(max(0.0, power_requirement - P_B)),
            },
        }

    # Cost reconciliation.
    cost_components = {
        name: _expr_value(expr) for name, expr in h["cost_expr"].items()
    }
    objective = float(model.ObjVal)
    reconstructed_cost = float(sum(cost_components.values()))
    cost_residual = objective - reconstructed_cost

    # Exact post-solve billing maxima and reduced-native-MAX provenance. The
    # dispatch-derived global TOU maximum fixes non-duplicated quantity; the
    # canonical seasonal source fixes only the transition settlement rate.
    billing_rows: list[dict[str, Any]] = []
    transition_detail_rows: list[dict[str, Any]] = []
    transition_positive_raw = False
    transition_ambiguous_incremental_total_kw = 0.0
    transition_boundary_unresolved_count = 0
    transition_resolved_exact_cost = 0.0
    transition_invariant_failures: list[str] = []
    min_solver_aux_margin = math.inf
    max_transition_native_max_error_kw = 0.0
    over_rule = inputs.settlement_interface["overcontract_rule"]
    tier1_frac = float(over_rule["tier1_threshold_fraction"])
    tier1_mult = float(over_rule["tier1_multiplier"])
    tier2_mult = float(over_rule["tier2_multiplier"])
    native_max_tolerance_kw = float(
        max(
            BALANCE_TOL,
            10.0 * float(h["finite_design_bounds"]["gurobi_feasibility_tol"]),
        )
    )
    month_groups = _month_groups(annual)
    for month, idx in month_groups.items():
        month_df = annual.iloc[idx]
        role_seasons = sorted(month_df["season"].astype(str).unique().tolist())
        role = "transition" if len(role_seasons) == 2 else f"pure_{role_seasons[0]}"
        overall_exact = float(np.max(inputs.kappa * p_grid[idx]))
        month_aux = h["billing_aux"].get(month, {})
        for season_component in role_seasons:
            season_idx = idx[month_df["season"].astype(str).to_numpy() == season_component]
            for period in PURE_APPLICABLE_PERIODS[season_component]:
                mask = annual.iloc[season_idx]["tou_period"].astype(str).to_numpy() == period
                active_idx = season_idx[mask]
                if len(active_idx) == 0:
                    continue
                exact = float(np.max(inputs.kappa * p_grid[active_idx]))
                raw_over = max(0.0, exact - CC)
                period_aux = month_aux.get("periods", {}).get(period)
                solver_aux = None
                solver_margin = None
                if period_aux is not None:
                    settlement_class = period_aux.get("settlement_class")
                    if (
                        role == "transition"
                        and settlement_class
                        == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
                    ):
                        seasonal_max = period_aux["transition_seasonal_max_grid"].get(
                            season_component
                        )
                        if seasonal_max is None:
                            raise RuntimeError(
                                "Class-C seasonal native MAX is absent for "
                                f"{month}/{period}/{season_component}."
                            )
                        solver_aux = float(inputs.kappa * seasonal_max.X)
                    else:
                        if role != "transition":
                            solver_aux = float(period_aux["D"].X)
                    if solver_aux is not None:
                        solver_margin = float(solver_aux - exact)
                        min_solver_aux_margin = min(min_solver_aux_margin, solver_margin)
                        if (
                            role == "transition"
                            and settlement_class
                            == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
                        ):
                            max_transition_native_max_error_kw = max(
                                max_transition_native_max_error_kw,
                                abs(solver_margin),
                            )
                            if abs(solver_margin) > native_max_tolerance_kw:
                                transition_invariant_failures.append(
                                    "native_seasonal_max"
                                    f":{month}/{period}/{season_component}"
                                )

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
                active_idx = np.asarray(idx[period_mask], dtype=int)
                if len(active_idx) == 0:
                    continue
                period_aux = month_aux.get("periods", {}).get(period)
                if period_aux is None or period_aux.get("transition_spec") is None:
                    raise RuntimeError(
                        f"Candidate-1 transition handles are absent for {month}/{period}."
                    )
                spec = period_aux["transition_spec"]
                active_seasons = list(spec["active_seasons"])
                candidate_rates = dict(spec["candidate_rates"])
                settlement_class = str(spec["settlement_class"])
                seasonal_maxima: dict[str, float] = {}
                season_max_indices: dict[str, int] = {}
                has_native_seasonal_max = bool(
                    settlement_class
                    == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE"
                )
                native_seasonal_max_pass = True
                native_seasonal_max_validation_status = (
                    "APPLICABLE_CLASS_C"
                    if has_native_seasonal_max
                    else "NOT_APPLICABLE_CLASS_A_OR_B_EPIGRAPH"
                )
                solver_seasonal_maxima: dict[str, float] = {}
                for season_component, season_idx in spec["season_indices"].items():
                    values = inputs.kappa * p_grid[season_idx]
                    local_argmax = int(np.argmax(values))
                    seasonal_maxima[season_component] = float(values[local_argmax])
                    season_max_indices[season_component] = int(season_idx[local_argmax])
                    if has_native_seasonal_max:
                        seasonal_max = period_aux["transition_seasonal_max_grid"].get(
                            season_component
                        )
                        if seasonal_max is None:
                            raise RuntimeError(
                                "Class-C seasonal native MAX is absent for "
                                f"{month}/{period}/{season_component}."
                            )
                        solver_seasonal = float(inputs.kappa * seasonal_max.X)
                        solver_seasonal_maxima[season_component] = solver_seasonal
                        seasonal_error = abs(
                            solver_seasonal - seasonal_maxima[season_component]
                        )
                        max_transition_native_max_error_kw = max(
                            max_transition_native_max_error_kw, seasonal_error
                        )
                        native_seasonal_max_pass = bool(
                            native_seasonal_max_pass
                            and seasonal_error <= native_max_tolerance_kw
                        )

                period_values = inputs.kappa * p_grid[active_idx]
                physical_local_argmax = int(np.argmax(period_values))
                physical_max_timestamp_index = int(active_idx[physical_local_argmax])
                global_exact = float(period_values[physical_local_argmax])
                physical_global_max_season = str(
                    annual.iloc[physical_max_timestamp_index]["season"]
                )
                solver_global = float(period_aux["D"].X)
                solver_global_margin = float(solver_global - global_exact)
                # The reduced formulation deliberately has no transition global
                # native MAX. D is a billing epigraph, so it must not understate
                # dispatch demand but need not be an exact resultant when the
                # corresponding sequential charge is economically inactive.
                billing_demand_epigraph_pass = bool(
                    solver_global + native_max_tolerance_kw >= global_exact
                )
                native_global_max_pass = True
                native_global_max_validation_status = (
                    "NOT_APPLICABLE_REDUCED_NATIVE_MAX_FORMULATION"
                )
                min_solver_aux_margin = min(min_solver_aux_margin, solver_global_margin)

                source_policy_status = "SINGLE_SEASON"
                source_expected: str | None = None
                selected_source: str | None = None
                source_selection_model_value: int | None = None
                source_selection_pass = True
                mc_cormick_product_pass = True
                source_selection_reason = "class_a_single_active_season"
                tie_candidate_seasons: list[str] = list(active_seasons)
                difference_later_minus_earlier_kw: float | None = None
                early_season: str | None = None
                later_season: str | None = None
                if settlement_class == "CLASS_A_SINGLE_SEASON":
                    source_expected = active_seasons[0]
                    selected_source = source_expected
                    tie_candidate_seasons = [source_expected]
                else:
                    early_season, later_season = spec["chronological_seasons"]
                    difference_later_minus_earlier_kw = float(
                        seasonal_maxima[later_season] - seasonal_maxima[early_season]
                    )
                    source_policy_status = classify_transition_source_with_guard(
                        difference_later_minus_earlier_kw,
                        float(period_aux["transition_tie_band_kw"]),
                        float(period_aux["transition_selection_guard_kw"]),
                    )
                    if source_policy_status == "NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP":
                        source_expected = early_season
                        tie_candidate_seasons = [early_season, later_season]
                        source_selection_reason = "numerical_tie_earliest_maximum_event_timestamp"
                    elif source_policy_status == "EARLIER_SEASON_CLEARLY_LARGER":
                        source_expected = early_season
                        tie_candidate_seasons = [early_season]
                        source_selection_reason = "earlier_season_exact_maximum_clearly_larger"
                    elif source_policy_status == "LATER_SEASON_CLEARLY_LARGER":
                        source_expected = later_season
                        tie_candidate_seasons = [later_season]
                        source_selection_reason = "later_season_exact_maximum_clearly_larger"
                    else:
                        tie_candidate_seasons = [early_season, later_season]
                        source_selection_reason = "numerical_source_selection_guard_unresolved"

                    if settlement_class == "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE":
                        if source_expected is None:
                            # The source is non-cost-facing in Class B.  Keep the
                            # physical maximum event for diagnostic provenance and
                            # retain the explicit guard status rather than inventing
                            # a source rate distinction.
                            source_expected = physical_global_max_season
                            source_selection_reason = (
                                "class_b_equal_rate_guard_non_cost_facing_physical_maximum"
                            )
                        selected_source = source_expected
                    elif settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":
                        selector = period_aux["transition_source_later"]
                        if selector is None:
                            raise RuntimeError(
                                f"Class-C source binary missing for {month}/{period}."
                            )
                        source_selection_model_value = (
                            1 if float(selector.X) >= 0.5 else 0
                        )
                        selected_source = (
                            later_season
                            if source_selection_model_value == 1
                            else early_season
                        )
                        source_selection_pass = bool(
                            source_expected is not None
                            and selected_source == source_expected
                        )
                        W_exact = 0.0  # assigned after sequential increments below
                    else:
                        raise RuntimeError(
                            f"Unknown transition settlement class: {settlement_class}."
                        )

                raw = max(0.0, global_exact - CC)
                transition_positive_raw = transition_positive_raw or raw > TRANSITION_OVERAGE_TOL_KW
                lower = min(prior_max, raw)
                incremental = max(0.0, raw - prior_max)
                cap = tier1_frac * CC
                tier1_kw = max(0.0, min(raw, cap) - min(lower, cap))
                tier2_kw = max(0.0, incremental - tier1_kw)
                W_exact = float(3.0 * incremental - tier1_kw)

                if settlement_class == "CLASS_C_TWO_SEASON_DIFFERENT_SETTLEMENT_RATE":
                    product = period_aux["transition_product_later"]
                    if product is None or source_selection_model_value is None:
                        raise RuntimeError(f"Class-C bounded product missing for {month}/{period}.")
                    product_value = float(product.X)
                    expected_product = float(source_selection_model_value * W_exact)
                    mc_cormick_product_pass = bool(
                        abs(product_value - expected_product) <= native_max_tolerance_kw
                        and product_value >= -native_max_tolerance_kw
                        and product_value
                        <= float(period_aux["transition_w_upper_kw"])
                        + native_max_tolerance_kw
                    )
                else:
                    product_value = None

                if selected_source is None:
                    raise RuntimeError(f"Transition source was not resolved for {month}/{period}.")
                resolved_rate = float(candidate_rates[selected_source])
                expected_rate = _matrix_rate(
                    inputs.settlement_matrix, month, selected_source, period
                )
                resolved_rate_consistency_pass = bool(
                    np.isclose(
                        resolved_rate,
                        expected_rate,
                        rtol=0.0,
                        atol=TRANSITION_RATE_EQUALITY_TOL_NTD2023_PER_KW_MONTH,
                    )
                )
                if settlement_class == "CLASS_B_TWO_SEASON_EQUAL_SETTLEMENT_RATE":
                    resolved_rate_consistency_pass = bool(
                        resolved_rate_consistency_pass
                        and len(set(candidate_rates.values())) == 1
                    )
                settlement_source_timestamp_index = season_max_indices[selected_source]
                max_timestamp_consistency_pass = bool(
                    selected_source
                    == str(annual.iloc[settlement_source_timestamp_index]["season"])
                )
                boundary_accounting = transition_boundary_settlement_accounting(
                    settlement_class,
                    source_policy_status,
                    incremental,
                )
                # This counter is intentionally Class-C/rate-relevant only.
                # Class-B keeps its raw source status for diagnostics, but its
                # identical rate makes that status non-cost-facing.
                transition_boundary_unresolved_count += int(
                    boundary_accounting["certificate_failure_count_increment"]
                )
                transition_ambiguous_incremental_total_kw += float(
                    boundary_accounting["ambiguous_incremental_overage_kw"]
                )

                if has_native_seasonal_max and not native_seasonal_max_pass:
                    transition_invariant_failures.append(
                        f"native_seasonal_max:{month}/{period}"
                    )
                if not billing_demand_epigraph_pass:
                    transition_invariant_failures.append(
                        f"billing_demand_epigraph:{month}/{period}"
                    )
                if not source_selection_pass:
                    transition_invariant_failures.append(
                        f"source_selection:{month}/{period}"
                    )
                if not mc_cormick_product_pass:
                    transition_invariant_failures.append(
                        f"bounded_product:{month}/{period}"
                    )
                if not max_timestamp_consistency_pass:
                    transition_invariant_failures.append(
                        f"source_timestamp:{month}/{period}"
                    )
                if not resolved_rate_consistency_pass:
                    transition_invariant_failures.append(
                        f"resolved_rate:{month}/{period}"
                    )

                resolved_cost = resolved_rate * W_exact
                transition_resolved_exact_cost += resolved_cost
                transition_detail_rows.append(
                    {
                        "billing_usage_period_id": month,
                        "tou_period": period,
                        "settlement_class": settlement_class,
                        "active_seasons": "+".join(active_seasons),
                        "chronological_seasons": "+".join(spec["chronological_seasons"]),
                        "seasonal_maxima_kw": json.dumps(
                            seasonal_maxima, ensure_ascii=False, sort_keys=True
                        ),
                        "exact_billing_period_tou_max_kw": global_exact,
                        "global_billing_period_tou_max_kw": global_exact,
                        "physical_global_max_timestamp": str(
                            annual.iloc[physical_max_timestamp_index]["timestamp"]
                        ),
                        "physical_global_max_timestamp_season": physical_global_max_season,
                        # Legacy names are intentionally canonical settlement
                        # source fields, not necessarily the literal global event
                        # inside the documented numerical tie band.
                        "max_timestamp": str(
                            annual.iloc[settlement_source_timestamp_index]["timestamp"]
                        ),
                        "max_timestamp_season": selected_source,
                        "settlement_source_max_timestamp": str(
                            annual.iloc[settlement_source_timestamp_index]["timestamp"]
                        ),
                        "settlement_source_max_timestamp_season": selected_source,
                        "cc_regular_kw": CC,
                        "raw_overage_kw": raw,
                        "prior_max_raw_overage_kw": prior_max,
                        "incremental_nonduplicated_overage_kw": incremental,
                        "tier1_increment_kw": tier1_kw,
                        "tier2_increment_kw": tier2_kw,
                        "equivalent_overcontract_quantity_W_kw": W_exact,
                        "rate_unambiguous": True,
                        "rate_resolution_reason": source_selection_reason,
                        "selected_max_source_season": selected_source,
                        "source_selection_expected_season": source_expected,
                        "source_selection_model_value_later": source_selection_model_value,
                        "source_selection_consistency_pass": source_selection_pass,
                        "max_timestamp_consistency_pass": max_timestamp_consistency_pass,
                        "resolved_rate_consistency_pass": resolved_rate_consistency_pass,
                        "native_seasonal_max_pass": native_seasonal_max_pass,
                        "native_seasonal_max_validation_status": native_seasonal_max_validation_status,
                        "native_global_max_pass": native_global_max_pass,
                        "native_global_max_validation_status": native_global_max_validation_status,
                        "billing_demand_epigraph_pass": billing_demand_epigraph_pass,
                        "mcCormick_product_pass": mc_cormick_product_pass,
                        "cross_season_tie_status": source_policy_status,
                        "tie_candidate_seasons": "+".join(tie_candidate_seasons),
                        "later_minus_earlier_max_kw": difference_later_minus_earlier_kw,
                        "transition_tie_band_kw": period_aux["transition_tie_band_kw"],
                        "transition_selection_guard_kw": period_aux["transition_selection_guard_kw"],
                        "candidate_rates_ntd2023_per_kw_month": json.dumps(
                            candidate_rates, ensure_ascii=False, sort_keys=True
                        ),
                        "resolved_rate_ntd2023_per_kw_month": resolved_rate,
                        "resolved_exact_charge_ntd2023": resolved_cost,
                        "boundary_affects_settlement": bool(
                            boundary_accounting["boundary_affects_settlement"]
                        ),
                        "ambiguous_incremental_overage_kw": float(
                            boundary_accounting["ambiguous_incremental_overage_kw"]
                        ),
                        "solver_demand_aux_kw": solver_global,
                        "solver_aux_minus_exact_kw": solver_global_margin,
                        "solver_seasonal_maxima_kw": json.dumps(
                            solver_seasonal_maxima,
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "seasonal_max_grid_upper_kw": json.dumps(
                            period_aux["transition_seasonal_max_grid_ub"],
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "global_demand_upper_kw": period_aux["demand_upper_kw"],
                        "cumulative_demand_upper_kw": period_aux[
                            "cumulative_demand_upper_kw"
                        ],
                        "class_c_difference_bounds_kw": json.dumps(
                            period_aux["transition_difference_bounds_kw"],
                            ensure_ascii=False,
                            sort_keys=True,
                        )
                        if period_aux["transition_difference_bounds_kw"] is not None
                        else None,
                        "class_c_W_upper_kw": period_aux["transition_w_upper_kw"],
                        "solver_product_later_kw": product_value,
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
    elif transition_boundary_unresolved_count > 0:
        transition_certificate = "FAIL_NUMERICAL_TIE_BOUNDARY_UNRESOLVED"
        eob_finality = "PROVISIONAL_NUMERICAL_SOURCE_BOUNDARY_UNRESOLVED"
    elif transition_invariant_failures:
        transition_certificate = "FAIL_TRANSITION_POSTSOLVE_INVARIANT"
        eob_finality = "PROVISIONAL_TRANSITION_INVARIANT_FAILURE"
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
            "A cost-facing solver demand auxiliary is below the exact post-solve "
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
            "min_solver_demand_aux_minus_exact_kw": (
                float(min_solver_aux_margin) if np.isfinite(min_solver_aux_margin) else None
            ),
        },
        "finite_design_bounds": dict(h["finite_design_bounds"]),
        "transition_settlement": {
            "objective_treatment": (
                "BILLING_PERIOD_TOU_MAX_PLUS_SEQUENTIAL_NONDUPLICATION; "
                "DISPATCH_EXACT_GLOBAL_MAX_DETERMINES_INCREMENT; "
                "CANONICAL_MAX_EVENT_SEASON_DETERMINES_TRANSITION_RATE"
            ),
            "fabricated_cross_season_rate_rule": False,
            "component_classification": h["transition_component_classification"],
            "formulation_metadata": h["transition_formulation_metadata"],
            "gurobi_feasibility_tol": float(
                h["finite_design_bounds"]["gurobi_feasibility_tol"]
            ),
            "numerical_tie_band_kw": float(
                h["finite_design_bounds"]["transition_tie_band_kw"]
            ),
            "numerical_source_selection_guard_kw": float(
                h["finite_design_bounds"]["transition_tie_selection_guard_kw"]
            ),
            "native_max_validation_tolerance_kw": native_max_tolerance_kw,
            "max_native_max_error_kw": max_transition_native_max_error_kw,
            "positive_transition_raw_overage_detected": bool(transition_positive_raw),
            "rate_ambiguous_incremental_overage_detected": bool(
                transition_ambiguous_incremental_total_kw > TRANSITION_OVERAGE_TOL_KW
            ),
            "rate_ambiguous_incremental_overage_total_kw": float(
                transition_ambiguous_incremental_total_kw
            ),
            "numerical_boundary_unresolved_count": int(
                transition_boundary_unresolved_count
            ),
            "postsolve_invariant_failures": transition_invariant_failures,
            "postsolve_invariants_pass": not bool(transition_invariant_failures),
            "resolved_transition_overcontract_exact_ntd2023": float(
                transition_resolved_exact_cost
            ),
            "nonbinding_certificate": transition_certificate,
            "eob_finality": eob_finality,
            "proof_note": (
                "The reduced-native-MAX formulation uses the billing-demand epigraph "
                "for Class A/B and two native exact seasonal MAX resultants only for "
                "each Class-C different-rate component. Dispatch-derived exact global "
                "maxima supply sequential non-duplicated reconciliation. A bounded "
                "Class-C source binary selects the audited rate; within the documented "
                "numerical tie band the canonical source is the earliest seasonal "
                "maximum event. The open solver guard is rejected rather than silently "
                "repriced."
            ),
        },
        "dispatch": dispatch,
        "billing_exact": billing_exact,
        "transition_settlement_detail": transition_detail,
    }
    if layer_a_diagnostics is not None:
        result["layer_a_resilience"] = layer_a_diagnostics
    return result
