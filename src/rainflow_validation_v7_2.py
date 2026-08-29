#!/usr/bin/env python3
"""
rainflow_validation_v7_2.py

Reusable ex-post rainflow / cycle-depth validator for the NTUST thesis v7.2
BESS degradation model.

Methodological role
-------------------
The production optimization remains the PNNL-calibrated adaptation of
Xu et al.'s intertemporal convex PWL cycle-aging formulation. This module does
NOT alter sizing, dispatch, objective coefficients, or constraints.

It independently:
1) reconstructs the closed annual battery stored-energy/SOC trajectory;
2) extracts turning points and rainflow cycles;
3) evaluates each rainflow cycle on the SAME locked PNNL-calibrated G(delta)
   piecewise-linear curve used to derive production lambda_k;
4) reconciles rainflow-accounted discharged energy against annual
   battery-side discharged energy;
5) compares rainflow cycle cost against the production PWL degradation cost.

Important boundary
------------------
The v7.2 Framework/Registry does not freeze a separate nonlinear interpolation
between PNNL Table 4.2 cycle-life points. Therefore this validator MUST NOT
invent one. It uses:
    G(0) = 0
    G(delta_i) = C_rep / N(delta_i)
and piecewise-linear interpolation in G between the retained technical points.

This changes the cycle-accounting method (rainflow vs intertemporal PWL) while
holding the technical/economic degradation calibration fixed.

No Gurobi optimization is performed here.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd


VALIDATOR_VERSION = "v7.2-rainflow-validator-2026-08-30-r1"

DEFAULT_STATE_TOL = 1e-8
DEFAULT_ENERGY_RECONCILIATION_ATOL_KWH = 1e-3
DEFAULT_COST_RECONCILIATION_ATOL_NTD = 0.05
DEFAULT_COST_EQUIVALENCE_RTOL = 1e-6


@dataclass(frozen=True)
class RainflowCycle:
    """One rainflow-counted cycle or half-cycle."""

    range_fraction: float
    mean_soc_fraction: float
    count: float
    start_rotated_state_index: int
    end_rotated_state_index: int
    start_original_state_index: int
    end_original_state_index: int


def _as_finite_1d(values: Sequence[float], label: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{label} must be one-dimensional.")
    if len(arr) == 0:
        raise ValueError(f"{label} must not be empty.")
    if not np.isfinite(arr).all():
        raise ValueError(f"{label} contains non-finite values.")
    return arr


def _remove_consecutive_duplicates(
    values: np.ndarray,
    original_indices: np.ndarray,
    *,
    tol: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(values) != len(original_indices):
        raise ValueError("values/original_indices length mismatch.")

    kept_values = [float(values[0])]
    kept_indices = [int(original_indices[0])]

    for value, original_idx in zip(values[1:], original_indices[1:]):
        if abs(float(value) - kept_values[-1]) <= tol:
            # Keep the latest index of a plateau. This preserves the turning
            # point value while attaching it to the end of the flat section.
            kept_values[-1] = float(value)
            kept_indices[-1] = int(original_idx)
        else:
            kept_values.append(float(value))
            kept_indices.append(int(original_idx))

    return np.asarray(kept_values), np.asarray(kept_indices, dtype=int)


def turning_points(
    values: Sequence[float],
    original_indices: Sequence[int] | None = None,
    *,
    tol: float = DEFAULT_STATE_TOL,
) -> pd.DataFrame:
    """
    Extract reversal points from a scalar history.

    The first and last samples are retained. Consecutive near-equal values are
    compressed before reversal detection.
    """
    arr = _as_finite_1d(values, "rainflow state history")
    if original_indices is None:
        idx = np.arange(len(arr), dtype=int)
    else:
        idx = np.asarray(original_indices, dtype=int)
        if idx.ndim != 1 or len(idx) != len(arr):
            raise ValueError("original_indices must match values length.")

    vals, ids = _remove_consecutive_duplicates(arr, idx, tol=tol)

    if len(vals) == 1:
        return pd.DataFrame(
            {
                "turning_point_order": [0],
                "state_value": [float(vals[0])],
                "original_state_index": [int(ids[0])],
            }
        )

    positions = [0]
    prev_diff = float(vals[1] - vals[0])

    for j in range(1, len(vals) - 1):
        next_diff = float(vals[j + 1] - vals[j])
        if prev_diff * next_diff < 0.0:
            positions.append(j)
        prev_diff = next_diff

    positions.append(len(vals) - 1)

    out = pd.DataFrame(
        {
            "turning_point_order": np.arange(len(positions), dtype=int),
            "state_value": vals[positions],
            "original_state_index": ids[positions],
        }
    )
    return out


def rotate_periodic_history_to_global_max(
    values: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Rotate a periodic state history to start at one global maximum.

    The input contains one sample per unique annual state time (e.g. t=0..8759)
    and does NOT repeat the terminal state. The returned history appends its
    first state at the end so rainflow sees a closed periodic path.

    Starting at a global extremum avoids arbitrary case-year endpoint
    half-cycle artifacts.
    """
    arr = _as_finite_1d(values, "periodic state history")
    start = int(np.argmax(arr))

    rotated = np.concatenate([arr[start:], arr[:start]])
    original_idx = np.concatenate(
        [
            np.arange(start, len(arr), dtype=int),
            np.arange(0, start, dtype=int),
        ]
    )

    closed = np.concatenate([rotated, rotated[:1]])
    closed_original_idx = np.concatenate(
        [original_idx, original_idx[:1]]
    )

    return closed, closed_original_idx, start


def extract_rainflow_cycles(
    values: Sequence[float],
    original_indices: Sequence[int] | None = None,
    *,
    tol: float = DEFAULT_STATE_TOL,
) -> tuple[list[RainflowCycle], pd.DataFrame]:
    """
    ASTM-style stack rainflow extraction.

    This implementation follows the standard four-point/stack logic:
    - compare the two newest adjacent reversal ranges;
    - close the older range when it is no larger than the newer range;
    - count a full cycle when enclosed by prior history;
    - retain boundary residues as half cycles.

    For a periodic history, call rotate_periodic_history_to_global_max() first.
    """
    arr = _as_finite_1d(values, "rainflow values")
    if original_indices is None:
        original_idx = np.arange(len(arr), dtype=int)
    else:
        original_idx = np.asarray(original_indices, dtype=int)
        if original_idx.ndim != 1 or len(original_idx) != len(arr):
            raise ValueError("original_indices must match rainflow values.")

    tp = turning_points(arr, original_idx, tol=tol)

    stack: deque[tuple[int, float, int]] = deque()
    cycles: list[RainflowCycle] = []

    for _, row in tp.iterrows():
        point = (
            int(row["turning_point_order"]),
            float(row["state_value"]),
            int(row["original_state_index"]),
        )
        stack.append(point)

        while len(stack) >= 3:
            x = abs(stack[-2][1] - stack[-3][1])
            y = abs(stack[-1][1] - stack[-2][1])

            # The older range remains open while it is materially larger.
            if x > y + tol:
                break

            if x <= tol:
                # Degenerate reversal; remove the oldest redundant point.
                stack.popleft()
                continue

            if len(stack) == 3:
                p0 = stack[0]
                p1 = stack[1]
                cycles.append(
                    RainflowCycle(
                        range_fraction=float(x),
                        mean_soc_fraction=0.5 * (p0[1] + p1[1]),
                        count=0.5,
                        start_rotated_state_index=int(p0[0]),
                        end_rotated_state_index=int(p1[0]),
                        start_original_state_index=int(p0[2]),
                        end_original_state_index=int(p1[2]),
                    )
                )
                stack.popleft()
            else:
                p0 = stack[-3]
                p1 = stack[-2]
                cycles.append(
                    RainflowCycle(
                        range_fraction=float(x),
                        mean_soc_fraction=0.5 * (p0[1] + p1[1]),
                        count=1.0,
                        start_rotated_state_index=int(p0[0]),
                        end_rotated_state_index=int(p1[0]),
                        start_original_state_index=int(p0[2]),
                        end_original_state_index=int(p1[2]),
                    )
                )

                last = stack.pop()
                stack.pop()
                stack.pop()
                stack.append(last)

    # Remaining open ranges are boundary half cycles.
    while len(stack) > 1:
        p0 = stack[0]
        p1 = stack[1]
        rng = abs(p1[1] - p0[1])
        if rng > tol:
            cycles.append(
                RainflowCycle(
                    range_fraction=float(rng),
                    mean_soc_fraction=0.5 * (p0[1] + p1[1]),
                    count=0.5,
                    start_rotated_state_index=int(p0[0]),
                    end_rotated_state_index=int(p1[0]),
                    start_original_state_index=int(p0[2]),
                    end_original_state_index=int(p1[2]),
                )
            )
        stack.popleft()

    return cycles, tp


def weighted_quantile(
    values: Sequence[float],
    weights: Sequence[float],
    quantile: float,
) -> float | None:
    vals = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)

    if len(vals) == 0:
        return None
    if len(vals) != len(w):
        raise ValueError("values and weights must have equal length.")
    if not (0.0 <= quantile <= 1.0):
        raise ValueError("quantile must be within [0,1].")
    if not np.isfinite(vals).all() or not np.isfinite(w).all():
        raise ValueError("weighted_quantile inputs must be finite.")
    if (w < 0).any():
        raise ValueError("weights must be non-negative.")

    total = float(w.sum())
    if total <= 0.0:
        return None

    order = np.argsort(vals)
    vals = vals[order]
    w = w[order]
    cumulative = np.cumsum(w)
    cutoff = quantile * total
    pos = int(np.searchsorted(cumulative, cutoff, side="left"))
    pos = min(pos, len(vals) - 1)
    return float(vals[pos])


def build_g_curve(
    technical_points: pd.DataFrame,
    *,
    crep_ntd_per_kwh: float,
    dod_column: str = "effective_dod",
    cycles_column: str = "cycles_to_eol",
    g_column: str | None = "G_ntd_per_installed_kwh",
    tol: float = 1e-9,
) -> pd.DataFrame:
    """
    Build the locked PNNL-calibrated cycle-cost curve.

    Output includes (0,0) plus the retained PNNL Table 4.2 technical points.
    G(delta_i) is recomputed from C_rep/N(delta_i). If an upstream G column is
    supplied, it is checked rather than trusted blindly.
    """
    if not np.isfinite(crep_ntd_per_kwh) or crep_ntd_per_kwh <= 0.0:
        raise ValueError("C_rep must be finite and positive.")

    required = {dod_column, cycles_column}
    missing = sorted(required - set(technical_points.columns))
    if missing:
        raise ValueError(f"technical_points missing columns: {missing}")

    work = technical_points.copy()
    work[dod_column] = pd.to_numeric(work[dod_column], errors="coerce")
    work[cycles_column] = pd.to_numeric(work[cycles_column], errors="coerce")

    if work[[dod_column, cycles_column]].isna().any().any():
        raise ValueError("technical cycle-life points contain non-numeric values.")
    if (work[dod_column] <= 0).any() or (work[dod_column] > 1.0).any():
        raise ValueError("technical DOD points must be within (0,1].")
    if (work[cycles_column] <= 0).any():
        raise ValueError("cycles_to_eol must be positive.")
    if work[dod_column].duplicated().any():
        raise ValueError("technical DOD points contain duplicates.")

    work = work.sort_values(dod_column).reset_index(drop=True)
    work["G_recomputed_ntd_per_installed_kwh"] = (
        float(crep_ntd_per_kwh) / work[cycles_column].astype(float)
    )

    if g_column and g_column in work.columns:
        g_upstream = pd.to_numeric(work[g_column], errors="coerce")
        if g_upstream.isna().any():
            raise ValueError("upstream G column contains non-numeric values.")
        diff = np.abs(
            g_upstream.to_numpy(dtype=float)
            - work["G_recomputed_ntd_per_installed_kwh"].to_numpy(dtype=float)
        )
        if float(diff.max()) > tol:
            raise ValueError(
                "Upstream G(delta) provenance does not reconcile with C_rep/N(delta). "
                f"max_abs_diff={float(diff.max())}"
            )

    zero = pd.DataFrame(
        {
            dod_column: [0.0],
            cycles_column: [np.inf],
            "G_recomputed_ntd_per_installed_kwh": [0.0],
        }
    )
    out = pd.concat(
        [
            zero,
            work[
                [
                    dod_column,
                    cycles_column,
                    "G_recomputed_ntd_per_installed_kwh",
                ]
            ],
        ],
        ignore_index=True,
    )

    # Convexity guardrail: marginal G slopes must be nondecreasing.
    x = out[dod_column].to_numpy(dtype=float)
    y = out["G_recomputed_ntd_per_installed_kwh"].to_numpy(dtype=float)
    slopes = np.diff(y) / np.diff(x)
    if np.any(np.diff(slopes) < -1e-10):
        raise ValueError(
            "PNNL-calibrated G(delta) curve is not convex/nondecreasing in slope."
        )

    out["interval_marginal_slope_ntd_per_battery_kwh"] = np.nan
    out.loc[1:, "interval_marginal_slope_ntd_per_battery_kwh"] = slopes

    return out


def g_piecewise_linear(
    dod: float | np.ndarray,
    g_curve: pd.DataFrame,
    *,
    tol: float = DEFAULT_STATE_TOL,
) -> float | np.ndarray:
    """Evaluate the locked piecewise-linear G(delta) curve."""
    x = g_curve["effective_dod"].to_numpy(dtype=float)
    y = g_curve["G_recomputed_ntd_per_installed_kwh"].to_numpy(dtype=float)

    q = np.asarray(dod, dtype=float)
    if not np.isfinite(q).all():
        raise ValueError("DOD query contains non-finite values.")
    if np.any(q < -tol):
        raise ValueError("DOD query contains negative values.")
    if np.any(q > x[-1] + tol):
        raise ValueError(
            f"DOD query exceeds locked technical domain {x[-1]:.6f}."
        )

    q_clip = np.clip(q, 0.0, x[-1])
    result = np.interp(q_clip, x, y)

    if np.ndim(dod) == 0:
        return float(result)
    return result


def _cycle_records(
    cycles: list[RainflowCycle],
    *,
    e_n_kwh: float,
    g_curve: pd.DataFrame,
    timestamps: Sequence[Any] | None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if timestamps is not None:
        ts = pd.to_datetime(pd.Series(timestamps), errors="coerce")
        if ts.isna().any():
            raise ValueError("timestamps contain unparsable values.")
        if len(ts) == 0:
            raise ValueError("timestamps must not be empty when provided.")
    else:
        ts = None

    n_states = len(ts) if ts is not None else None

    for i, cycle in enumerate(cycles, start=1):
        depth = float(cycle.range_fraction)
        count = float(cycle.count)
        g_value = float(g_piecewise_linear(depth, g_curve))
        discharged_kwh = count * depth * e_n_kwh
        cost = count * e_n_kwh * g_value

        start_ts = None
        end_ts = None
        if ts is not None:
            s = cycle.start_original_state_index % n_states
            e = cycle.end_original_state_index % n_states
            start_ts = str(ts.iloc[s])
            end_ts = str(ts.iloc[e])

        rows.append(
            {
                "cycle_id": i,
                "depth_fraction_nameplate": depth,
                "depth_percent_nameplate": 100.0 * depth,
                "mean_soc_fraction": float(cycle.mean_soc_fraction),
                "count": count,
                "equivalent_discharged_energy_kwh": discharged_kwh,
                "G_ntd_per_installed_kwh_per_cycle": g_value,
                "rainflow_cost_ntd2023": cost,
                "start_original_state_index": int(
                    cycle.start_original_state_index
                ),
                "end_original_state_index": int(
                    cycle.end_original_state_index
                ),
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
            }
        )

    return pd.DataFrame(rows)


def _depth_bin_summary(
    cycle_df: pd.DataFrame,
    g_curve: pd.DataFrame,
) -> pd.DataFrame:
    x = g_curve["effective_dod"].to_numpy(dtype=float)

    rows: list[dict[str, Any]] = []
    for lo, hi in zip(x[:-1], x[1:]):
        # Use (lo, hi] except the first interval includes zero by convention.
        if np.isclose(lo, 0.0):
            mask = (
                cycle_df["depth_fraction_nameplate"].gt(0.0)
                & cycle_df["depth_fraction_nameplate"].le(hi + 1e-12)
            )
        else:
            mask = (
                cycle_df["depth_fraction_nameplate"].gt(lo + 1e-12)
                & cycle_df["depth_fraction_nameplate"].le(hi + 1e-12)
            )

        selected = cycle_df.loc[mask]
        rows.append(
            {
                "depth_bin_lower_exclusive_fraction": float(lo),
                "depth_bin_upper_inclusive_fraction": float(hi),
                "weighted_cycle_count": float(selected["count"].sum()),
                "rainflow_record_count": int(len(selected)),
                "equivalent_discharged_energy_kwh": float(
                    selected["equivalent_discharged_energy_kwh"].sum()
                ),
                "rainflow_cost_ntd2023": float(
                    selected["rainflow_cost_ntd2023"].sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def _segment_pwl_reconciliation(
    dispatch: pd.DataFrame,
    lambdas: Sequence[float],
    *,
    eta_d: float,
) -> tuple[pd.DataFrame, float]:
    lambda_arr = _as_finite_1d(lambdas, "lambda coefficients")
    rows: list[dict[str, Any]] = []
    total = 0.0

    for k, lambda_k in enumerate(lambda_arr, start=1):
        col = f"p_discharge_seg_{k}_kw_ac"
        if col not in dispatch.columns:
            raise ValueError(f"dispatch missing required segment discharge column {col}")

        ac_kwh = float(
            pd.to_numeric(dispatch[col], errors="coerce").sum()
        )
        battery_kwh = ac_kwh / float(eta_d)
        cost = float(lambda_k) * battery_kwh
        total += cost

        rows.append(
            {
                "segment_k": k,
                "lambda_ntd2023_per_battery_side_discharged_kwh": float(
                    lambda_k
                ),
                "ac_side_discharged_energy_kwh": ac_kwh,
                "battery_side_discharged_energy_kwh": battery_kwh,
                "pwl_segment_cost_ntd2023": cost,
            }
        )

    return pd.DataFrame(rows), float(total)


def _self_test_rainflow_algorithm() -> dict[str, Any]:
    """Small deterministic unit tests independent of project data."""

    tests: list[dict[str, Any]] = []

    # One simple closed 20%-depth cycle. The stack emits two 0.5 residues,
    # which together equal one full cycle.
    seq1 = np.array([0.90, 0.70, 0.90])
    cyc1, _ = extract_rainflow_cycles(seq1)
    eq_count_02 = sum(
        c.count
        for c in cyc1
        if np.isclose(c.range_fraction, 0.20, atol=1e-12)
    )
    t1 = np.isclose(eq_count_02, 1.0, atol=1e-12)
    tests.append(
        {
            "test": "single_closed_20pct_cycle",
            "pass": bool(t1),
            "observed_weighted_count": float(eq_count_02),
            "expected_weighted_count": 1.0,
        }
    )

    # One 20%-depth full cycle plus one nested/separate 10%-depth full cycle.
    seq2 = np.array([0.90, 0.70, 0.90, 0.80, 0.90])
    cyc2, _ = extract_rainflow_cycles(seq2)
    count_02 = sum(
        c.count
        for c in cyc2
        if np.isclose(c.range_fraction, 0.20, atol=1e-12)
    )
    count_01 = sum(
        c.count
        for c in cyc2
        if np.isclose(c.range_fraction, 0.10, atol=1e-12)
    )
    t2 = (
        np.isclose(count_02, 1.0, atol=1e-12)
        and np.isclose(count_01, 1.0, atol=1e-12)
    )
    tests.append(
        {
            "test": "closed_20pct_plus_10pct_cycles",
            "pass": bool(t2),
            "observed_20pct_count": float(count_02),
            "observed_10pct_count": float(count_01),
            "expected_each": 1.0,
        }
    )

    # Closed-history rainflow weighted depth must equal total downward movement.
    seq3_unique = np.array([0.90, 0.70, 0.80, 0.60])
    closed3, orig3, _ = rotate_periodic_history_to_global_max(seq3_unique)
    cyc3, _ = extract_rainflow_cycles(closed3, orig3)
    rf_down = sum(c.count * c.range_fraction for c in cyc3)
    physical_down = float(
        np.maximum(0.0, -(np.diff(closed3))).sum()
    )
    t3 = np.isclose(rf_down, physical_down, atol=1e-12)
    tests.append(
        {
            "test": "closed_history_depth_energy_identity",
            "pass": bool(t3),
            "rainflow_weighted_depth": float(rf_down),
            "physical_total_downward_depth": physical_down,
        }
    )

    all_pass = all(bool(x["pass"]) for x in tests)
    return {
        "status": "PASS" if all_pass else "FAIL",
        "tests": tests,
    }


def validate_dispatch_rainflow(
    dispatch: pd.DataFrame,
    *,
    e_n_kwh: float,
    eta_c: float,
    eta_d: float,
    soc_min: float,
    soc_max: float,
    production_breakpoints: Sequence[float],
    lambdas: Sequence[float],
    technical_points: pd.DataFrame,
    crep_ntd_per_kwh: float,
    pwl_cost_reference_ntd: float,
    battery_side_discharge_reference_kwh: float | None = None,
    timestamps: Sequence[Any] | None = None,
    state_tol: float = DEFAULT_STATE_TOL,
    energy_atol_kwh: float = DEFAULT_ENERGY_RECONCILIATION_ATOL_KWH,
    cost_atol_ntd: float = DEFAULT_COST_RECONCILIATION_ATOL_NTD,
    cost_equivalence_rtol: float = DEFAULT_COST_EQUIVALENCE_RTOL,
) -> dict[str, Any]:
    """
    Validate one solved dispatch ex post using periodic rainflow counting.

    Returns a dictionary containing:
    - summary
    - gates
    - cycles DataFrame
    - turning_points DataFrame
    - depth_bins DataFrame
    - pwl_segments DataFrame
    - g_curve DataFrame
    - algorithm_self_test
    """
    if not np.isfinite(e_n_kwh) or e_n_kwh <= 0.0:
        raise ValueError("E_N must be finite and positive for rainflow validation.")
    if not (0.0 < eta_c <= 1.0 and 0.0 < eta_d <= 1.0):
        raise ValueError("eta_c/eta_d must lie in (0,1].")
    if not (0.0 <= soc_min < soc_max <= 1.0):
        raise ValueError("Invalid SOC bounds.")

    required = {
        "soc_fraction",
        "e_physical_kwh",
        "p_charge_kw_ac",
        "p_discharge_kw_ac",
    }
    missing = sorted(required - set(dispatch.columns))
    if missing:
        raise ValueError(f"dispatch missing required columns: {missing}")

    lambda_arr = _as_finite_1d(lambdas, "lambdas")
    bp = _as_finite_1d(production_breakpoints, "production breakpoints")
    if len(bp) != len(lambda_arr) + 1:
        raise ValueError(
            "Production breakpoints must have exactly one more point than lambdas."
        )
    if not np.all(np.diff(bp) > 0):
        raise ValueError("Production breakpoints must be strictly increasing.")
    if not np.isclose(bp[0], 0.0, atol=1e-12):
        raise ValueError("Production breakpoints must begin at 0.")

    work = dispatch.copy()
    for col in required:
        work[col] = pd.to_numeric(work[col], errors="coerce")
        if work[col].isna().any():
            raise ValueError(f"dispatch column {col} contains non-numeric values.")

    soc = work["soc_fraction"].to_numpy(dtype=float)
    e_phys = work["e_physical_kwh"].to_numpy(dtype=float)
    p_ch = work["p_charge_kw_ac"].to_numpy(dtype=float)
    p_dis = work["p_discharge_kw_ac"].to_numpy(dtype=float)

    if not np.isfinite(soc).all():
        raise ValueError("SOC history contains non-finite values.")

    algorithm_test = _self_test_rainflow_algorithm()
    if algorithm_test["status"] != "PASS":
        raise RuntimeError("Internal rainflow algorithm self-test failed.")

    # Basic SOC / energy consistency.
    soc_from_energy = e_phys / e_n_kwh
    max_soc_energy_residual = float(np.max(np.abs(soc - soc_from_energy)))

    soc_lower_violation = max(0.0, soc_min - float(np.min(soc)))
    soc_upper_violation = max(0.0, float(np.max(soc)) - soc_max)

    # Reconstruct terminal state from the last interval and verify annual cycle.
    e_terminal_reconstructed = float(
        e_phys[-1]
        + eta_c * p_ch[-1]
        - p_dis[-1] / eta_d
    )
    terminal_soc_reconstructed = e_terminal_reconstructed / e_n_kwh
    cyclic_energy_residual = float(
        e_terminal_reconstructed - e_phys[0]
    )
    cyclic_soc_residual = float(
        terminal_soc_reconstructed - soc[0]
    )

    # Aggregate discharge semantics.
    battery_side_discharge_kwh = float(p_dis.sum() / eta_d)

    # Segment-level PWL cost reconciliation and intertemporal-state audit.
    segment_df, pwl_dispatch_cost = _segment_pwl_reconciliation(
        work,
        lambda_arr,
        eta_d=eta_d,
    )

    aggregate_segment_discharge = float(
        segment_df["battery_side_discharged_energy_kwh"].sum()
    )
    aggregate_segment_minus_total_kwh = (
        aggregate_segment_discharge - battery_side_discharge_kwh
    )

    # Recheck the serialized 15b segment chronology rather than relying only
    # on the solver's own post-solve diagnostics. This independently verifies:
    #   sum_k p_ch,k = p_ch
    #   sum_k p_dis,k = p_dis
    #   e_{t+1,k} = e_{t,k} + eta_c p_ch,t,k - p_dis,t,k/eta_d
    #   e_{T,k} = e_{0,k}
    # and the physical-state identity
    #   e_physical = SOC_MIN*E_N + sum_k e_seg,k.
    seg_e_cols = [
        f"e_seg_{k}_kwh" for k in range(1, len(lambda_arr) + 1)
    ]
    seg_ch_cols = [
        f"p_charge_seg_{k}_kw_ac"
        for k in range(1, len(lambda_arr) + 1)
    ]
    seg_dis_cols = [
        f"p_discharge_seg_{k}_kw_ac"
        for k in range(1, len(lambda_arr) + 1)
    ]
    for col in [*seg_e_cols, *seg_ch_cols, *seg_dis_cols]:
        if col not in work.columns:
            raise ValueError(
                f"dispatch missing required intertemporal segment column {col}"
            )
        work[col] = pd.to_numeric(work[col], errors="coerce")
        if work[col].isna().any():
            raise ValueError(
                f"dispatch segment column {col} contains non-numeric values."
            )

    seg_e = work[seg_e_cols].to_numpy(dtype=float)
    seg_ch = work[seg_ch_cols].to_numpy(dtype=float)
    seg_dis = work[seg_dis_cols].to_numpy(dtype=float)

    hourly_charge_link_residual = (
        seg_ch.sum(axis=1) - p_ch
    )
    hourly_discharge_link_residual = (
        seg_dis.sum(axis=1) - p_dis
    )
    max_hourly_segment_charge_link_residual = float(
        np.max(np.abs(hourly_charge_link_residual))
    )
    max_hourly_segment_discharge_link_residual = float(
        np.max(np.abs(hourly_discharge_link_residual))
    )

    if len(work) > 1:
        expected_next_seg = (
            seg_e[:-1, :]
            + eta_c * seg_ch[:-1, :]
            - seg_dis[:-1, :] / eta_d
        )
        internal_seg_resid = (
            seg_e[1:, :] - expected_next_seg
        )
        max_internal_segment_dynamics_residual = float(
            np.max(np.abs(internal_seg_resid))
        )
    else:
        max_internal_segment_dynamics_residual = 0.0

    reconstructed_terminal_seg = (
        seg_e[-1, :]
        + eta_c * seg_ch[-1, :]
        - seg_dis[-1, :] / eta_d
    )
    segment_cyclic_residual_vector = (
        reconstructed_terminal_seg - seg_e[0, :]
    )
    max_segment_cyclic_residual = float(
        np.max(np.abs(segment_cyclic_residual_vector))
    )

    shifted_state_identity = (
        soc_min * e_n_kwh + seg_e.sum(axis=1)
    )
    max_physical_vs_segment_state_residual = float(
        np.max(np.abs(e_phys - shifted_state_identity))
    )

    pwl_cost_reference_residual = float(
        pwl_dispatch_cost - float(pwl_cost_reference_ntd)
    )

    # Technical G(delta) curve.
    g_curve = build_g_curve(
        technical_points,
        crep_ntd_per_kwh=crep_ntd_per_kwh,
    )

    max_technical_dod = float(
        g_curve["effective_dod"].max()
    )
    if bp[-1] > max_technical_dod + 1e-12:
        raise ValueError(
            "Production breakpoint domain exceeds retained technical DOD domain."
        )

    # Periodic rainflow.
    closed_soc, closed_original_idx, rotation_start = (
        rotate_periodic_history_to_global_max(soc)
    )
    cycles, tp_rotated = extract_rainflow_cycles(
        closed_soc,
        closed_original_idx,
        tol=state_tol,
    )

    cycle_df = _cycle_records(
        cycles,
        e_n_kwh=e_n_kwh,
        g_curve=g_curve,
        timestamps=timestamps,
    )

    if cycle_df.empty:
        rainflow_discharged_kwh = 0.0
        rainflow_cost = 0.0
        max_dod = 0.0
        median_dod = None
        energy_weighted_dod = None
        weighted_cycle_count = 0.0
        eq_full_cycles_nameplate = 0.0
    else:
        rainflow_discharged_kwh = float(
            cycle_df["equivalent_discharged_energy_kwh"].sum()
        )
        rainflow_cost = float(
            cycle_df["rainflow_cost_ntd2023"].sum()
        )
        max_dod = float(
            cycle_df["depth_fraction_nameplate"].max()
        )
        median_dod = weighted_quantile(
            cycle_df["depth_fraction_nameplate"],
            cycle_df["count"],
            0.5,
        )
        energy_weights = (
            cycle_df["equivalent_discharged_energy_kwh"].to_numpy(dtype=float)
        )
        depths = (
            cycle_df["depth_fraction_nameplate"].to_numpy(dtype=float)
        )
        energy_weighted_dod = (
            float(np.average(depths, weights=energy_weights))
            if float(energy_weights.sum()) > 0.0
            else None
        )
        weighted_cycle_count = float(cycle_df["count"].sum())
        eq_full_cycles_nameplate = float(
            np.sum(
                cycle_df["count"].to_numpy(dtype=float)
                * cycle_df["depth_fraction_nameplate"].to_numpy(dtype=float)
            )
        )

    usable_window = soc_max - soc_min
    eq_full_cycles_usable_window = (
        eq_full_cycles_nameplate / usable_window
        if usable_window > 0.0
        else None
    )

    rainflow_energy_residual = float(
        rainflow_discharged_kwh - battery_side_discharge_kwh
    )

    reference_discharge_residual = None
    if battery_side_discharge_reference_kwh is not None:
        reference_discharge_residual = float(
            battery_side_discharge_kwh
            - float(battery_side_discharge_reference_kwh)
        )

    pwl_minus_rainflow = float(
        pwl_dispatch_cost - rainflow_cost
    )
    denominator = max(
        abs(pwl_dispatch_cost),
        abs(rainflow_cost),
        1.0,
    )
    pwl_rainflow_relative_difference = float(
        abs(pwl_minus_rainflow) / denominator
    )
    cost_equivalence_tol = max(
        float(cost_atol_ntd),
        float(cost_equivalence_rtol) * denominator,
    )

    depth_bins = _depth_bin_summary(cycle_df, g_curve)

    # Map rotated turning-point order back to original state/timestamp.
    tp_out = tp_rotated.copy()
    tp_out = tp_out.rename(
        columns={"state_value": "soc_fraction"}
    )
    if timestamps is not None:
        ts = pd.to_datetime(pd.Series(timestamps), errors="coerce")
        tp_out["timestamp"] = [
            str(ts.iloc[int(i) % len(ts)])
            for i in tp_out["original_state_index"]
        ]

    max_cycle_depth_violation = max(
        0.0,
        max_dod - max_technical_dod,
    )

    gates = {
        "algorithm_self_test": (
            "PASS" if algorithm_test["status"] == "PASS" else "FAIL"
        ),
        "soc_energy_identity": (
            "PASS" if max_soc_energy_residual <= 1e-7 else "FAIL"
        ),
        "soc_bounds": (
            "PASS"
            if soc_lower_violation <= 1e-7
            and soc_upper_violation <= 1e-7
            else "FAIL"
        ),
        "annual_cyclic_state": (
            "PASS"
            if abs(cyclic_energy_residual) <= energy_atol_kwh
            else "FAIL"
        ),
        "segment_vs_aggregate_discharge": (
            "PASS"
            if abs(aggregate_segment_minus_total_kwh) <= energy_atol_kwh
            else "FAIL"
        ),
        "hourly_segment_power_linkage": (
            "PASS"
            if max_hourly_segment_charge_link_residual <= energy_atol_kwh
            and max_hourly_segment_discharge_link_residual <= energy_atol_kwh
            else "FAIL"
        ),
        "intertemporal_segment_state_dynamics": (
            "PASS"
            if max_internal_segment_dynamics_residual <= energy_atol_kwh
            and max_segment_cyclic_residual <= energy_atol_kwh
            else "FAIL"
        ),
        "physical_vs_segment_state_identity": (
            "PASS"
            if max_physical_vs_segment_state_residual <= energy_atol_kwh
            else "FAIL"
        ),
        "pwl_dispatch_vs_15b_cost": (
            "PASS"
            if abs(pwl_cost_reference_residual) <= cost_atol_ntd
            else "FAIL"
        ),
        "rainflow_vs_dispatch_discharge_energy": (
            "PASS"
            if abs(rainflow_energy_residual) <= energy_atol_kwh
            else "FAIL"
        ),
        "rainflow_depth_within_technical_domain": (
            "PASS"
            if max_cycle_depth_violation <= 1e-8
            else "FAIL"
        ),
        # This is intentionally a numerical-equivalence diagnostic, not a
        # thesis-wide materiality threshold. If it does not pass, the caller
        # should report REVIEW_REQUIRED rather than invent a new acceptable
        # degradation-error percentage.
        "pwl_vs_rainflow_cost_numerical_equivalence": (
            "PASS"
            if abs(pwl_minus_rainflow) <= cost_equivalence_tol
            else "REVIEW"
        ),
    }

    if reference_discharge_residual is not None:
        gates["dispatch_vs_15b_battery_discharge_energy"] = (
            "PASS"
            if abs(reference_discharge_residual) <= energy_atol_kwh
            else "FAIL"
        )

    hard_fail = any(value == "FAIL" for value in gates.values())
    cost_review = (
        gates["pwl_vs_rainflow_cost_numerical_equivalence"] == "REVIEW"
    )

    if hard_fail:
        verdict = "RAINFLOW_VALIDATION_FAIL"
    elif cost_review:
        verdict = (
            "RAINFLOW_VALIDATION_REVIEW_REQUIRED_PWL_COST_DIFFERENCE"
        )
    else:
        verdict = "RAINFLOW_VALIDATION_PASS"

    summary = {
        "validator_version": VALIDATOR_VERSION,
        "verdict": verdict,
        "E_N_kwh": float(e_n_kwh),
        "SOC_min_model": float(soc_min),
        "SOC_max_model": float(soc_max),
        "SOC_min_realized": float(np.min(soc)),
        "SOC_max_realized": float(np.max(soc)),
        "max_soc_vs_energy_identity_residual": max_soc_energy_residual,
        "annual_cyclic_energy_residual_kwh": cyclic_energy_residual,
        "annual_cyclic_soc_residual_fraction": cyclic_soc_residual,
        "periodic_rotation_start_original_state_index": int(rotation_start),
        "turning_point_count": int(len(tp_out)),
        "rainflow_record_count": int(len(cycle_df)),
        "weighted_cycle_count": float(weighted_cycle_count),
        "equivalent_full_cycles_nameplate": float(eq_full_cycles_nameplate),
        "equivalent_full_cycles_usable_window": (
            float(eq_full_cycles_usable_window)
            if eq_full_cycles_usable_window is not None
            else None
        ),
        "maximum_rainflow_DOD_fraction_nameplate": float(max_dod),
        "median_rainflow_DOD_fraction_nameplate": (
            float(median_dod) if median_dod is not None else None
        ),
        "energy_weighted_rainflow_DOD_fraction_nameplate": (
            float(energy_weighted_dod)
            if energy_weighted_dod is not None
            else None
        ),
        "battery_side_discharge_from_dispatch_kwh": float(
            battery_side_discharge_kwh
        ),
        "battery_side_discharge_from_segments_kwh": float(
            aggregate_segment_discharge
        ),
        "max_hourly_segment_charge_link_residual_kw": float(
            max_hourly_segment_charge_link_residual
        ),
        "max_hourly_segment_discharge_link_residual_kw": float(
            max_hourly_segment_discharge_link_residual
        ),
        "max_internal_segment_dynamics_residual_kwh": float(
            max_internal_segment_dynamics_residual
        ),
        "max_segment_cyclic_residual_kwh": float(
            max_segment_cyclic_residual
        ),
        "max_physical_vs_segment_state_residual_kwh": float(
            max_physical_vs_segment_state_residual
        ),
        "rainflow_accounted_discharge_kwh": float(
            rainflow_discharged_kwh
        ),
        "rainflow_minus_dispatch_discharge_kwh": float(
            rainflow_energy_residual
        ),
        "PWL_degradation_cost_from_dispatch_segments_ntd2023": float(
            pwl_dispatch_cost
        ),
        "PWL_degradation_cost_reference_15b_ntd2023": float(
            pwl_cost_reference_ntd
        ),
        "PWL_dispatch_minus_15b_cost_ntd2023": float(
            pwl_cost_reference_residual
        ),
        "rainflow_degradation_cost_ntd2023": float(rainflow_cost),
        "PWL_minus_rainflow_cost_ntd2023": float(
            pwl_minus_rainflow
        ),
        "PWL_vs_rainflow_absolute_relative_difference": float(
            pwl_rainflow_relative_difference
        ),
        "numerical_cost_equivalence_tolerance_ntd": float(
            cost_equivalence_tol
        ),
        "C_rep_ntd2023_per_kwh": float(crep_ntd_per_kwh),
        "max_technical_DOD_fraction": float(max_technical_dod),
        "cost_curve_interpolation": (
            "piecewise_linear_in_G_between_locked_PNNL_Table4.2_points"
        ),
        "materiality_threshold_for_nonzero_PWL_rainflow_error": (
            "NOT_FROZEN_BY_FRAMEWORK; non-numerical-equivalence triggers review"
        ),
    }

    return {
        "summary": summary,
        "gates": gates,
        "cycles": cycle_df,
        "turning_points": tp_out,
        "depth_bins": depth_bins,
        "pwl_segments": segment_df,
        "g_curve": g_curve,
        "algorithm_self_test": algorithm_test,
    }


def run_internal_self_test() -> dict[str, Any]:
    """Public callable wrapper used by Script 15c and future tests."""
    return _self_test_rainflow_algorithm()
