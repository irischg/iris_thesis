#!/usr/bin/env python3
"""
12a_audit_xu_intertemporal_segment_states.py

NTUST thesis v7.1 — synthetic unit-test / semantics audit for the
PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL cycle-aging
formulation.

Purpose
-------
Before integrating degradation into the full 8760-hour sizing/dispatch model,
verify on small synthetic LPs that the production semantics are correct:

1. segment stored-energy states persist across time;
2. segment capacities are proportional to endogenous-style E^N semantics
   (tested here at a fixed synthetic E^N);
3. aggregate charge/discharge equals the sum of segment flows;
4. AC-side power is converted to battery-side energy exactly once;
5. convex marginal costs reproduce the correct aggregate depth allocation
   and degradation cost; chronological segment identity may be non-unique
   among degenerate LP optima;
6. annual-style cyclic segment boundaries are feasible and enforced;
7. a multi-hour deep cycle costs more than a Harry-style hourly-reset proxy;
8. an idle gap does not reset the segment depth history.

This is a synthetic validation script only. It does NOT run the annual EOB,
does NOT select the 1 MW vs 10 MW mainline cost bracket, and does NOT replace
the later ex-post rainflow validation required by v7.1.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import gurobipy as gp
import numpy as np
import pandas as pd
from gurobipy import GRB


SCRIPT_VERSION = "v7.1-xu-intertemporal-segment-audit-2026-08-22-r1"

SOC_MIN = 0.10
SOC_MAX = 0.90
ETA_C = 0.90
ETA_D = 0.90
DELTA_T_HR = 1.0

BREAKPOINTS = (0.0, 0.30, 0.60, 0.80)
SEGMENT_WIDTHS = (
    BREAKPOINTS[1] - BREAKPOINTS[0],
    BREAKPOINTS[2] - BREAKPOINTS[1],
    BREAKPOINTS[3] - BREAKPOINTS[2],
)

TEST_E_N_KWH = 1000.0
USABLE_KWH = (SOC_MAX - SOC_MIN) * TEST_E_N_KWH
EXPECTED_SEGMENT_CAPACITY_KWH = np.array(SEGMENT_WIDTHS) * TEST_E_N_KWH

# 90 kW AC discharge for 1 h removes exactly 100 kWh battery-side.
TEST_DISCHARGE_AC_KW = 90.0

# 111.111... kW AC charge for 1 h restores exactly 100 kWh battery-side.
TEST_CHARGE_AC_KW = 100.0 / ETA_C

TOL = 1e-6

EXPECTED_POWER_BRACKETS_MW = (1.0, 10.0)


@dataclass(frozen=True)
class SyntheticCase:
    name: str
    p_ch_ac_kw: tuple[float, ...]
    p_dis_ac_kw: tuple[float, ...]
    expected_battery_discharge_by_segment_kwh: tuple[float, float, float]
    expected_total_battery_discharge_kwh: float
    compare_hourly_reset: bool = True


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_cases() -> list[SyntheticCase]:
    zero = 0.0
    ch = TEST_CHARGE_AC_KW
    dis = TEST_DISCHARGE_AC_KW

    return [
        SyntheticCase(
            name="shallow_200kwh_cycle",
            p_ch_ac_kw=(zero, zero, ch, ch),
            p_dis_ac_kw=(dis, dis, zero, zero),
            expected_battery_discharge_by_segment_kwh=(200.0, 0.0, 0.0),
            expected_total_battery_discharge_kwh=200.0,
        ),
        SyntheticCase(
            name="deep_400kwh_cycle",
            p_ch_ac_kw=(zero, zero, zero, zero, ch, ch, ch, ch),
            p_dis_ac_kw=(dis, dis, dis, dis, zero, zero, zero, zero),
            expected_battery_discharge_by_segment_kwh=(300.0, 100.0, 0.0),
            expected_total_battery_discharge_kwh=400.0,
        ),
        SyntheticCase(
            name="idle_gap_persistence_400kwh",
            p_ch_ac_kw=(
                zero, zero, zero, zero, zero, ch, ch, ch, ch
            ),
            p_dis_ac_kw=(
                dis, dis, zero, dis, dis, zero, zero, zero, zero
            ),
            expected_battery_discharge_by_segment_kwh=(300.0, 100.0, 0.0),
            expected_total_battery_discharge_kwh=400.0,
        ),
        SyntheticCase(
            name="deep_700kwh_cycle",
            p_ch_ac_kw=(
                zero, zero, zero, zero, zero, zero, zero,
                ch, ch, ch, ch, ch, ch, ch,
            ),
            p_dis_ac_kw=(
                dis, dis, dis, dis, dis, dis, dis,
                zero, zero, zero, zero, zero, zero, zero,
            ),
            expected_battery_discharge_by_segment_kwh=(300.0, 300.0, 100.0),
            expected_total_battery_discharge_kwh=700.0,
        ),
    ]


def read_lambda_packages(root: Path) -> pd.DataFrame:
    path = (
        root
        / "results"
        / "parameter_audit"
        / "pnnl_calibrated_pwl_degradation_candidate_packages.csv"
    )

    if not path.exists():
        raise FileNotFoundError(
            "Script 11h degradation candidate package not found:\n"
            f"{path}"
        )

    df = pd.read_csv(path)

    required = {
        "package_id",
        "power_scale_bracket_mw",
        "crep_ntd_per_kwh",
        "lambda_1_ntd_per_battery_side_kwh",
        "lambda_2_ntd_per_battery_side_kwh",
        "lambda_3_ntd_per_battery_side_kwh",
        "lambda_ratio",
        "production_breakpoints",
        "currency",
        "currency_base_year",
        "mainline_selected",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(
            f"11h package is missing required columns: {missing}"
        )

    if len(df) != 2:
        raise RuntimeError(
            f"Expected exactly 2 bracket packages; found {len(df)}."
        )

    observed_brackets = tuple(
        sorted(df["power_scale_bracket_mw"].astype(float).tolist())
    )
    if observed_brackets != EXPECTED_POWER_BRACKETS_MW:
        raise RuntimeError(
            "Unexpected 11h power-scale brackets.\n"
            f"Expected: {EXPECTED_POWER_BRACKETS_MW}\n"
            f"Observed: {observed_brackets}"
        )

    if not (
        df["production_breakpoints"].astype(str) == "0,0.30,0.60,0.80"
    ).all():
        raise RuntimeError(
            "11h production breakpoints do not match v7.1."
        )

    if not (df["currency"].astype(str) == "NTD").all():
        raise RuntimeError("11h lambda packages must be in NTD.")

    if not (df["currency_base_year"].astype(int) == 2023).all():
        raise RuntimeError("11h lambda packages must use 2023 currency base year.")

    return df.sort_values("power_scale_bracket_mw").reset_index(drop=True)


def hourly_reset_proxy_cost_ntd(
    p_dis_ac_kw: tuple[float, ...],
    lambdas: np.ndarray,
) -> float:
    """
    Legacy-style diagnostic proxy only.

    Each hour independently restarts at segment 1 and allocates that hour's
    battery-side discharged energy from cheapest to deepest segment.

    This is intentionally NOT the production formulation.
    """
    caps = EXPECTED_SEGMENT_CAPACITY_KWH
    total = 0.0

    for p_dis in p_dis_ac_kw:
        remaining = p_dis * DELTA_T_HR / ETA_D

        for k in range(3):
            take = min(remaining, caps[k])
            total += lambdas[k] * take
            remaining -= take
            if remaining <= TOL:
                break

        if remaining > TOL:
            raise RuntimeError(
                "Synthetic hourly-reset proxy discharge exceeds usable energy."
            )

    return float(total)


def solve_case(
    case: SyntheticCase,
    lambdas: np.ndarray,
) -> dict[str, object]:
    T = len(case.p_ch_ac_kw)

    if len(case.p_dis_ac_kw) != T:
        raise ValueError(f"{case.name}: charge/discharge series length mismatch.")

    p_ch_total = np.asarray(case.p_ch_ac_kw, dtype=float)
    p_dis_total = np.asarray(case.p_dis_ac_kw, dtype=float)

    if np.any(p_ch_total < -TOL) or np.any(p_dis_total < -TOL):
        raise ValueError(f"{case.name}: negative synthetic power.")

    # Aggregate synthetic trajectory is intentionally non-simultaneous.
    if np.any((p_ch_total > TOL) & (p_dis_total > TOL)):
        raise ValueError(
            f"{case.name}: synthetic case contains simultaneous aggregate "
            "charge and discharge."
        )

    model = gp.Model(f"xu_segment_audit_{case.name}")
    model.Params.OutputFlag = 0
    model.Params.LogToConsole = 0
    model.Params.NumericFocus = 1

    K = range(3)
    TT = range(T)
    STATES = range(T + 1)

    seg_caps = EXPECTED_SEGMENT_CAPACITY_KWH

    e = model.addVars(
        STATES,
        K,
        lb=0.0,
        name="e_seg",
    )
    p_ch = model.addVars(
        TT,
        K,
        lb=0.0,
        name="p_ch_seg_ac",
    )
    p_dis = model.addVars(
        TT,
        K,
        lb=0.0,
        name="p_dis_seg_ac",
    )

    # Segment energy capacity bounds.
    for t in STATES:
        for k in K:
            model.addConstr(
                e[t, k] <= float(seg_caps[k]),
                name=f"seg_cap_t{t}_k{k+1}",
            )

    # Start at fully charged usable range. Since total usable energy equals
    # the sum of all segment capacities, this also pins every segment full.
    model.addConstr(
        gp.quicksum(e[0, k] for k in K) == USABLE_KWH,
        name="initial_shifted_usable_state",
    )

    # Aggregate charge/discharge linkage.
    for t in TT:
        model.addConstr(
            gp.quicksum(p_ch[t, k] for k in K)
            == float(p_ch_total[t]),
            name=f"agg_charge_t{t}",
        )
        model.addConstr(
            gp.quicksum(p_dis[t, k] for k in K)
            == float(p_dis_total[t]),
            name=f"agg_discharge_t{t}",
        )

    # Cross-time segment dynamics.
    for t in TT:
        for k in K:
            model.addConstr(
                e[t + 1, k]
                == e[t, k]
                + ETA_C * p_ch[t, k] * DELTA_T_HR
                - p_dis[t, k] * DELTA_T_HR / ETA_D,
                name=f"seg_dyn_t{t}_k{k+1}",
            )

    # Annual-style cyclic boundary adapted to the synthetic horizon.
    for k in K:
        model.addConstr(
            e[T, k] == e[0, k],
            name=f"cyclic_seg_k{k+1}",
        )

    # Discharge-only degradation objective with lambda on battery-side energy.
    cycling_cost = gp.quicksum(
        float(lambdas[k])
        * p_dis[t, k]
        * DELTA_T_HR
        / ETA_D
        for t in TT
        for k in K
    )

    model.setObjective(cycling_cost, GRB.MINIMIZE)
    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"{case.name}: Gurobi did not return OPTIMAL. "
            f"Status={model.Status}"
        )

    e_val = np.array(
        [[e[t, k].X for k in K] for t in STATES],
        dtype=float,
    )
    p_ch_val = np.array(
        [[p_ch[t, k].X for k in K] for t in TT],
        dtype=float,
    )
    p_dis_val = np.array(
        [[p_dis[t, k].X for k in K] for t in TT],
        dtype=float,
    )

    battery_discharge_by_segment = (
        p_dis_val.sum(axis=0) * DELTA_T_HR / ETA_D
    )
    battery_charge_by_segment = (
        p_ch_val.sum(axis=0) * DELTA_T_HR * ETA_C
    )

    expected_by_segment = np.asarray(
        case.expected_battery_discharge_by_segment_kwh,
        dtype=float,
    )

    if not np.allclose(
        battery_discharge_by_segment,
        expected_by_segment,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"{case.name}: shallow-to-deep discharge allocation failed.\n"
            f"Expected battery-side segment discharge: {expected_by_segment}\n"
            f"Observed: {battery_discharge_by_segment}"
        )

    total_battery_discharge = float(battery_discharge_by_segment.sum())

    if not np.isclose(
        total_battery_discharge,
        case.expected_total_battery_discharge_kwh,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"{case.name}: total battery-side discharge mismatch. "
            f"Expected={case.expected_total_battery_discharge_kwh}, "
            f"Observed={total_battery_discharge}"
        )

    # Check aggregate power linkage exactly.
    if not np.allclose(
        p_ch_val.sum(axis=1),
        p_ch_total,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(f"{case.name}: aggregate charge linkage failed.")

    if not np.allclose(
        p_dis_val.sum(axis=1),
        p_dis_total,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(f"{case.name}: aggregate discharge linkage failed.")

    # Check state dynamics numerically.
    dyn_residual_max = 0.0
    for t in TT:
        lhs = e_val[t + 1, :]
        rhs = (
            e_val[t, :]
            + ETA_C * p_ch_val[t, :] * DELTA_T_HR
            - p_dis_val[t, :] * DELTA_T_HR / ETA_D
        )
        dyn_residual_max = max(
            dyn_residual_max,
            float(np.max(np.abs(lhs - rhs))),
        )

    if dyn_residual_max > TOL:
        raise RuntimeError(
            f"{case.name}: segment dynamics residual too large: "
            f"{dyn_residual_max}"
        )

    # Check segment capacity and nonnegativity.
    if np.min(e_val) < -TOL:
        raise RuntimeError(f"{case.name}: negative segment energy state.")

    if np.any(e_val - seg_caps[np.newaxis, :] > TOL):
        raise RuntimeError(f"{case.name}: segment capacity violated.")

    # Check cyclic segment boundary.
    cyclic_residual_max = float(
        np.max(np.abs(e_val[-1, :] - e_val[0, :]))
    )
    if cyclic_residual_max > TOL:
        raise RuntimeError(
            f"{case.name}: cyclic segment-state boundary failed."
        )

    # Check aggregate shifted-state consistency against the total-battery
    # dynamics implied by the fixed aggregate powers.
    x_from_segments = e_val.sum(axis=1)

    x_expected = np.empty(T + 1, dtype=float)
    x_expected[0] = USABLE_KWH

    for t in TT:
        x_expected[t + 1] = (
            x_expected[t]
            + ETA_C * p_ch_total[t] * DELTA_T_HR
            - p_dis_total[t] * DELTA_T_HR / ETA_D
        )

    aggregate_state_residual_max = float(
        np.max(np.abs(x_from_segments - x_expected))
    )

    if aggregate_state_residual_max > TOL:
        raise RuntimeError(
            f"{case.name}: aggregate shifted-state consistency failed."
        )

    # Minimum state reached should correspond to the requested depth.
    expected_min_x = (
        USABLE_KWH - case.expected_total_battery_discharge_kwh
    )
    observed_min_x = float(np.min(x_from_segments))

    if not np.isclose(
        observed_min_x,
        expected_min_x,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"{case.name}: minimum shifted usable state mismatch. "
            f"Expected={expected_min_x}, observed={observed_min_x}"
        )

    expected_cost = float(
        np.dot(lambdas, expected_by_segment)
    )
    observed_cost = float(model.ObjVal)

    if not np.isclose(
        observed_cost,
        expected_cost,
        atol=TOL,
        rtol=0.0,
    ):
        raise RuntimeError(
            f"{case.name}: degradation cost mismatch. "
            f"Expected={expected_cost}, observed={observed_cost}"
        )

    reset_cost = hourly_reset_proxy_cost_ntd(
        case.p_dis_ac_kw,
        lambdas,
    )

    if case.expected_total_battery_discharge_kwh <= seg_caps[0] + TOL:
        # A genuinely shallow cycle should be equivalent to the reset proxy.
        if not np.isclose(
            observed_cost,
            reset_cost,
            atol=TOL,
            rtol=0.0,
        ):
            raise RuntimeError(
                f"{case.name}: shallow-cycle equivalence check failed."
            )
        reset_relation = "EQUAL_AS_EXPECTED_FOR_SHALLOW_CYCLE"
    else:
        # A multi-hour deep cycle must cost strictly more than hourly reset.
        if not observed_cost > reset_cost + TOL:
            raise RuntimeError(
                f"{case.name}: deep-cycle intertemporal cost did not exceed "
                "hourly-reset proxy."
            )
        reset_relation = "INTERTEMPORAL_GREATER_THAN_HOURLY_RESET"

    # Explicit idle-gap persistence check for the designated case.
    idle_gap_check = "NOT_APPLICABLE"
    idle_state_before = None
    idle_state_after = None

    if case.name == "idle_gap_persistence_400kwh":
        # The third interval is idle. Cross-time segment dynamics therefore
        # require the COMPLETE segment-state vector to remain unchanged.
        #
        # Do NOT assert a unique vector such as [100, 300, 200] here.
        # With a linear convex segment-cost objective, multiple chronological
        # segment schedules can be cost-equivalent (LP degeneracy) while still
        # producing the same correct total depth allocation and degradation
        # cost over the whole cycle. The v7.1 requirement is persistence
        # across the idle interval, not uniqueness of an intermediate optimum.
        before_idle = e_val[2, :].copy()
        after_idle = e_val[3, :].copy()

        idle_state_before = before_idle.tolist()
        idle_state_after = after_idle.tolist()

        if not np.allclose(
            before_idle,
            after_idle,
            atol=TOL,
            rtol=0.0,
        ):
            raise RuntimeError(
                "idle_gap_persistence_400kwh: segment states changed during "
                "the idle interval."
            )

        # The whole case already separately verifies:
        # - total battery-side discharge = 400 kWh;
        # - aggregate segment discharge = 300/100/0 kWh;
        # - intertemporal wear cost > hourly-reset proxy.
        # Together with e_before_idle == e_after_idle, this demonstrates that
        # the idle hour does not reset cycle-depth accounting.
        idle_gap_check = "PASS_NO_RESET_ACROSS_IDLE_INTERVAL"

    return {
        "case_name": case.name,
        "horizon_intervals": T,
        "objective_ntd": observed_cost,
        "expected_objective_ntd": expected_cost,
        "hourly_reset_proxy_ntd": reset_cost,
        "reset_relation": reset_relation,
        "battery_discharge_seg1_kwh": float(
            battery_discharge_by_segment[0]
        ),
        "battery_discharge_seg2_kwh": float(
            battery_discharge_by_segment[1]
        ),
        "battery_discharge_seg3_kwh": float(
            battery_discharge_by_segment[2]
        ),
        "battery_charge_seg1_kwh": float(
            battery_charge_by_segment[0]
        ),
        "battery_charge_seg2_kwh": float(
            battery_charge_by_segment[1]
        ),
        "battery_charge_seg3_kwh": float(
            battery_charge_by_segment[2]
        ),
        "total_battery_discharge_kwh": total_battery_discharge,
        "minimum_shifted_state_kwh": observed_min_x,
        "max_segment_dynamics_residual": dyn_residual_max,
        "max_aggregate_state_residual": aggregate_state_residual_max,
        "max_cyclic_segment_residual": cyclic_residual_max,
        "idle_gap_check": idle_gap_check,
        "idle_state_before_kwh": idle_state_before,
        "idle_state_after_kwh": idle_state_after,
        "status": "PASS",
        "e_val": e_val,
        "p_ch_val": p_ch_val,
        "p_dis_val": p_dis_val,
    }


def main() -> None:
    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.1 Xu-Adapted Intertemporal Segment-State Synthetic Audit")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    root = project_root()
    lambda_df = read_lambda_packages(root)

    output_dir = root / "results" / "model_audit"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Locked technical semantics")
    print(f"- SOC_min={SOC_MIN:.2f}")
    print(f"- SOC_max={SOC_MAX:.2f}")
    print(f"- eta_c={ETA_C:.2f}")
    print(f"- eta_d={ETA_D:.2f}")
    print(f"- delta_t={DELTA_T_HR:.1f} h")
    print(f"- synthetic E^N={TEST_E_N_KWH:.1f} kWh")
    print(f"- shifted usable energy={USABLE_KWH:.1f} kWh")
    print(
        "- segment capacities="
        + ", ".join(
            f"{x:.1f}" for x in EXPECTED_SEGMENT_CAPACITY_KWH
        )
        + " kWh"
    )
    print("- breakpoints=0, 0.30, 0.60, 0.80")
    print("- segment states are cross-time states, not hourly reset buckets")
    print("- lambda units are NTD per battery-side discharged kWh")
    print("- cycling cost uses AC discharge / eta_d exactly once")
    print("- synthetic horizons enforce cyclic segment boundaries")
    print()

    cases = build_cases()
    summary_rows: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []

    for _, package in lambda_df.iterrows():
        power_bracket = float(package["power_scale_bracket_mw"])
        package_id = str(package["package_id"])

        lambdas = np.array(
            [
                float(
                    package[
                        "lambda_1_ntd_per_battery_side_kwh"
                    ]
                ),
                float(
                    package[
                        "lambda_2_ntd_per_battery_side_kwh"
                    ]
                ),
                float(
                    package[
                        "lambda_3_ntd_per_battery_side_kwh"
                    ]
                ),
            ],
            dtype=float,
        )

        if not (
            lambdas[0] <= lambdas[1] + TOL
            and lambdas[1] <= lambdas[2] + TOL
        ):
            raise RuntimeError(
                f"{power_bracket:g} MW: lambda ordering is not convex "
                "shallow-to-deep."
            )

        print(f"{power_bracket:g} MW bracket")
        print(
            "- lambda="
            + ", ".join(f"{x:.9f}" for x in lambdas)
            + " NTD/battery-kWh"
        )

        for case in cases:
            result = solve_case(case, lambdas)

            summary_record = {
                "package_id": package_id,
                "power_scale_bracket_mw": power_bracket,
                **{
                    k: v
                    for k, v in result.items()
                    if k not in {"e_val", "p_ch_val", "p_dis_val"}
                },
            }

            for state_key in (
                "idle_state_before_kwh",
                "idle_state_after_kwh",
            ):
                if summary_record.get(state_key) is not None:
                    summary_record[state_key] = json.dumps(
                        summary_record[state_key]
                    )

            summary_rows.append(summary_record)

            e_val = result["e_val"]
            p_ch_val = result["p_ch_val"]
            p_dis_val = result["p_dis_val"]

            T = len(case.p_ch_ac_kw)

            for t in range(T + 1):
                trace_rows.append(
                    {
                        "package_id": package_id,
                        "power_scale_bracket_mw": power_bracket,
                        "case_name": case.name,
                        "state_index": t,
                        "e_seg1_kwh": float(e_val[t, 0]),
                        "e_seg2_kwh": float(e_val[t, 1]),
                        "e_seg3_kwh": float(e_val[t, 2]),
                        "shifted_usable_state_kwh": float(
                            e_val[t, :].sum()
                        ),
                        "p_ch_total_ac_kw": (
                            float(case.p_ch_ac_kw[t])
                            if t < T
                            else np.nan
                        ),
                        "p_dis_total_ac_kw": (
                            float(case.p_dis_ac_kw[t])
                            if t < T
                            else np.nan
                        ),
                        "p_ch_seg1_ac_kw": (
                            float(p_ch_val[t, 0])
                            if t < T
                            else np.nan
                        ),
                        "p_ch_seg2_ac_kw": (
                            float(p_ch_val[t, 1])
                            if t < T
                            else np.nan
                        ),
                        "p_ch_seg3_ac_kw": (
                            float(p_ch_val[t, 2])
                            if t < T
                            else np.nan
                        ),
                        "p_dis_seg1_ac_kw": (
                            float(p_dis_val[t, 0])
                            if t < T
                            else np.nan
                        ),
                        "p_dis_seg2_ac_kw": (
                            float(p_dis_val[t, 1])
                            if t < T
                            else np.nan
                        ),
                        "p_dis_seg3_ac_kw": (
                            float(p_dis_val[t, 2])
                            if t < T
                            else np.nan
                        ),
                    }
                )

            print(
                f"- {case.name}: PASS | "
                f"battery discharge="
                f"{result['total_battery_discharge_kwh']:.1f} kWh | "
                f"segment split="
                f"{result['battery_discharge_seg1_kwh']:.1f}/"
                f"{result['battery_discharge_seg2_kwh']:.1f}/"
                f"{result['battery_discharge_seg3_kwh']:.1f} | "
                f"cost={result['objective_ntd']:.6f} NTD | "
                f"hourly-reset={result['hourly_reset_proxy_ntd']:.6f} NTD"
            )

        print()

    summary_df = pd.DataFrame(summary_rows)
    trace_df = pd.DataFrame(trace_rows)

    summary_path = (
        output_dir
        / "xu_intertemporal_segment_synthetic_audit_summary.csv"
    )
    trace_path = (
        output_dir
        / "xu_intertemporal_segment_synthetic_state_traces.csv"
    )

    summary_df.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig",
    )
    trace_df.to_csv(
        trace_path,
        index=False,
        encoding="utf-8-sig",
    )

    # Global acceptance checks.
    if set(summary_df["status"].astype(str)) != {"PASS"}:
        raise RuntimeError("At least one synthetic Xu audit case failed.")

    if not (
        summary_df.loc[
            summary_df["case_name"] == "deep_400kwh_cycle",
            "reset_relation",
        ]
        == "INTERTEMPORAL_GREATER_THAN_HOURLY_RESET"
    ).all():
        raise RuntimeError(
            "Deep-cycle hourly-reset contrast did not pass for both brackets."
        )

    if not (
        summary_df.loc[
            summary_df["case_name"] == "idle_gap_persistence_400kwh",
            "idle_gap_check",
        ]
        == "PASS_NO_RESET_ACROSS_IDLE_INTERVAL"
    ).all():
        raise RuntimeError(
            "Idle-gap persistence did not pass for both brackets."
        )

    max_dyn = float(
        summary_df["max_segment_dynamics_residual"].max()
    )
    max_agg = float(
        summary_df["max_aggregate_state_residual"].max()
    )
    max_cyclic = float(
        summary_df["max_cyclic_segment_residual"].max()
    )

    audit_path = (
        output_dir
        / "xu_intertemporal_segment_synthetic_audit.txt"
    )

    audit = {
        "script_version": SCRIPT_VERSION,
        "status": "PASS",
        "method_name": (
            "PNNL-calibrated adaptation of Xu et al.'s intertemporal "
            "PWL cycle-aging formulation"
        ),
        "synthetic_E_N_kWh": TEST_E_N_KWH,
        "segment_capacities_kWh": (
            EXPECTED_SEGMENT_CAPACITY_KWH.tolist()
        ),
        "eta_c": ETA_C,
        "eta_d": ETA_D,
        "delta_t_hr": DELTA_T_HR,
        "power_scale_brackets_tested_MW": [1.0, 10.0],
        "cases_tested": [case.name for case in cases],
        "max_segment_dynamics_residual": max_dyn,
        "max_aggregate_state_residual": max_agg,
        "max_cyclic_segment_residual": max_cyclic,
        "acceptance": {
            "cross_time_segment_states": "PASS",
            "segment_capacity_bounds": "PASS",
            "aggregate_power_linkage": "PASS",
            "battery_side_efficiency_placement": "PASS",
            "convex_depth_allocation_and_cost": "PASS",
            "cyclic_segment_boundary": "PASS",
            "deep_cycle_exceeds_hourly_reset_proxy": "PASS",
            "idle_gap_does_not_reset_depth_history": "PASS",
        },
        "guardrails": [
            "Synthetic audit only; no annual EOB solved.",
            "1 MW vs 10 MW mainline bracket remains unselected.",
            "No binary charge/discharge exclusivity is added here.",
            "No claim that Xu theorem directly proves the endogenous sizing extension.",
            "Rainflow ex-post validation remains pending.",
        ],
        "next_step": (
            "integrate the tested segment-state block into the production "
            "economic-only benchmark / annual optimization and audit "
            "simultaneous charge-discharge before adding binaries"
        ),
    }

    audit_path.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Outputs")
    print(f"- Synthetic summary: {summary_path}")
    print(f"- Segment state traces: {trace_path}")
    print(f"- Audit summary: {audit_path}")
    print()
    print("Gate interpretation")
    print("- Cross-time segment-state semantics: PASS")
    print("- Convex aggregate depth allocation / cost semantics: PASS")
    print("- AC/battery-side efficiency placement: PASS")
    print("- Cyclic segment-state boundary: PASS")
    print("- Harry-style hourly-reset contrast: PASS")
    print("- Idle-gap persistence: PASS")
    print("- Mainline 1 MW vs 10 MW bracket: NOT SELECTED")
    print("- Rainflow ex-post validation: STILL PENDING")
    print(
        "- Next step: integrate this tested block into the production EOB / "
        "annual optimization."
    )


if __name__ == "__main__":
    main()
