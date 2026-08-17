#!/usr/bin/env python3
"""
10_audit_bess_state_semantics.py

NTUST thesis v7.1 — BESS state / SOC / efficiency / replay-semantics audit.

Purpose
-------
Lock and executable-test the v7.1 battery state conventions before economic
parameter population and before the production optimization model is built.

v7.1 mainline technical semantics:
- stationary LFP;
- SOC_min = 0.10;
- SOC_max = 0.90;
- usable energy = 0.80 E^N;
- p_ch and p_dis are AC/PCS-side power;
- e_t is battery-side stored energy;
- eta_c = eta_d = 0.90;
- one-step transition:
      e_{t+1} = e_t + eta_c p_ch dt - p_dis dt / eta_d
- annual normal-operation reserve floor:
      e_t >= SOC_min E^N + R(alpha,beta)
- outage replay initial state:
      e_0 = SOC_min E^N + R
- outage replay technical bound:
      SOC_min E^N <= e_tau <= SOC_max E^N
  (the annual reserve floor is NOT enforced during the outage)
- outage terminal:
      e_beta >= SOC_min E^N
  with no requirement to restore R immediately.
- annual model uses periodic state semantics e_T = e_0.
- Layer A consistency replay does not use outage PV surplus for recharging.

This script does NOT compute the production R(alpha,beta), size the BESS,
populate PNNL costs, implement degradation, or run optimization.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-bess-state-semantics-2026-08-17"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_INTERVALS = 8760
EXPECTED_STATE_POINTS = 8761
DELTA_T_HOURS = 1.0

SOC_MIN = 0.10
SOC_MAX = 0.90
USABLE_FRACTION = SOC_MAX - SOC_MIN
ETA_C = 0.90
ETA_D = 0.90
ROUND_TRIP_EFFICIENCY = ETA_C * ETA_D

# Synthetic audit only. These values do not become thesis sizing parameters.
TEST_E_N_KWH = 1000.0
TEST_R_KWH = 300.0
TEST_AC_CHARGE_KW = 100.0
TEST_AC_DISCHARGE_KW = 90.0

EXPECTED_MAINLINE_BETAS = tuple(range(4, 13))


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Audit NTUST v7.1 BESS state and replay semantics."
    )
    parser.add_argument(
        "--annual-parquet",
        type=Path,
        default=root / "data" / "processed" / "annual_input_v7_1.parquet",
    )
    parser.add_argument(
        "--annual-csv",
        type=Path,
        default=root / "data" / "processed" / "annual_input_v7_1.csv",
    )
    parser.add_argument(
        "--valid-starts-parquet",
        type=Path,
        default=root / "data" / "processed" / "valid_outage_starts_v7_1.parquet",
    )
    parser.add_argument(
        "--valid-starts-csv",
        type=Path,
        default=root / "data" / "processed" / "valid_outage_starts_v7_1.csv",
    )
    parser.add_argument(
        "--state-index-output",
        type=Path,
        default=root / "data" / "processed" / "bess_state_index_v7_1.csv",
    )
    parser.add_argument(
        "--semantics-output",
        type=Path,
        default=root / "results" / "data_audit" / "bess_state_semantics_v7_1.json",
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=root / "results" / "data_audit" / "bess_state_semantics_v7_1_audit.txt",
    )
    return parser.parse_args()


def read_with_parquet_fallback(
    parquet_path: Path,
    csv_path: Path,
    label: str,
) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        f"{label} not found. Expected either:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}"
    )


def validate_annual(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "integration_status"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Annual input missing required columns: {missing}")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")

    if out["timestamp"].isna().any():
        raise ValueError("Annual input contains unparsable timestamps.")

    if len(out) != EXPECTED_INTERVALS:
        raise ValueError(
            f"Annual input must contain {EXPECTED_INTERVALS} intervals; "
            f"found {len(out)}."
        )

    if out["timestamp"].duplicated().any():
        raise ValueError("Annual input contains duplicate timestamps.")

    out = out.sort_values("timestamp").reset_index(drop=True)

    expected = pd.date_range(
        FORMAL_START,
        periods=EXPECTED_INTERVALS,
        freq="h",
    )
    if not pd.DatetimeIndex(out["timestamp"]).equals(expected):
        raise ValueError(
            "Annual input is not the exact v7.1 interval-start chronology."
        )

    statuses = set(out["integration_status"].astype(str).str.strip())
    if statuses != {"passed"}:
        raise ValueError(
            "Annual input integration_status must be exactly {'passed'}; "
            f"found {sorted(statuses)}."
        )

    return out


def build_state_index(annual: pd.DataFrame) -> pd.DataFrame:
    interval_starts = pd.DatetimeIndex(annual["timestamp"])
    terminal = pd.DatetimeIndex([FORMAL_END_EXCLUSIVE])
    state_times = interval_starts.append(terminal)

    if len(state_times) != EXPECTED_STATE_POINTS:
        raise ValueError(
            f"Expected {EXPECTED_STATE_POINTS} state boundaries; "
            f"found {len(state_times)}."
        )

    if state_times[0] != FORMAL_START:
        raise ValueError("State index does not begin at formal start.")

    if state_times[-1] != FORMAL_END_EXCLUSIVE:
        raise ValueError("State index does not end at formal end-exclusive.")

    deltas = state_times[1:] - state_times[:-1]
    if not np.all(deltas == pd.Timedelta(hours=1)):
        raise ValueError("State boundaries are not exactly hourly.")

    return pd.DataFrame(
        {
            "state_index": np.arange(EXPECTED_STATE_POINTS, dtype=np.int64),
            "state_timestamp": state_times,
            "is_initial_state": np.arange(EXPECTED_STATE_POINTS) == 0,
            "is_terminal_state": np.arange(EXPECTED_STATE_POINTS)
            == EXPECTED_INTERVALS,
        }
    )


def validate_valid_starts(
    df: pd.DataFrame,
    state_index: pd.DataFrame,
) -> dict[str, object]:
    required = {
        "beta_hours",
        "start_index",
        "start_timestamp",
        "end_index_exclusive",
        "end_timestamp_exclusive",
        "circular_wrap_used",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"Valid-start artifact missing required columns: {missing}"
        )

    vs = df.copy()
    for col in ["start_timestamp", "end_timestamp_exclusive"]:
        vs[col] = pd.to_datetime(vs[col], errors="coerce")
    if vs[["start_timestamp", "end_timestamp_exclusive"]].isna().any().any():
        raise ValueError("Valid-start artifact contains unparsable timestamps.")

    for col in ["beta_hours", "start_index", "end_index_exclusive"]:
        vs[col] = pd.to_numeric(vs[col], errors="coerce")
        if vs[col].isna().any():
            raise ValueError(f"Valid-start column {col} is not numeric.")

    betas = tuple(sorted(vs["beta_hours"].astype(int).unique().tolist()))
    if betas != EXPECTED_MAINLINE_BETAS:
        raise ValueError(
            "Valid-start beta set does not match v7.1 mainline 4..12 h. "
            f"Found: {betas}"
        )

    # Robust boolean parse for circular-wrap flag.
    circ = vs["circular_wrap_used"]
    if pd.api.types.is_bool_dtype(circ):
        circ_bool = circ.astype(bool)
    else:
        mapping = {
            "true": True, "false": False, "1": True, "0": False,
            "yes": True, "no": False,
        }
        circ_bool = circ.astype(str).str.strip().str.lower().map(mapping)
        if circ_bool.isna().any():
            raise ValueError("Cannot parse circular_wrap_used as boolean.")

    if circ_bool.any():
        raise ValueError("Valid-start artifact contains circular-wrap windows.")

    if not np.all(
        vs["end_index_exclusive"].to_numpy(dtype=int)
        == vs["start_index"].to_numpy(dtype=int)
        + vs["beta_hours"].to_numpy(dtype=int)
    ):
        raise ValueError(
            "Off-by-one audit failed: end_index_exclusive != start + beta."
        )

    state_times = pd.Series(
        pd.DatetimeIndex(state_index["state_timestamp"]).to_numpy()
    )

    start_idx = vs["start_index"].to_numpy(dtype=int)
    end_idx = vs["end_index_exclusive"].to_numpy(dtype=int)

    expected_start_ts = pd.DatetimeIndex(state_times.iloc[start_idx].to_numpy())
    expected_end_ts = pd.DatetimeIndex(state_times.iloc[end_idx].to_numpy())

    if not np.array_equal(
        expected_start_ts.to_numpy(),
        pd.DatetimeIndex(vs["start_timestamp"]).to_numpy(),
    ):
        raise ValueError(
            "Valid-start start timestamps do not align with state boundaries."
        )

    if not np.array_equal(
        expected_end_ts.to_numpy(),
        pd.DatetimeIndex(vs["end_timestamp_exclusive"]).to_numpy(),
    ):
        raise ValueError(
            "Valid-start end-exclusive timestamps do not align with terminal "
            "state boundaries."
        )

    counts = (
        vs.groupby("beta_hours", as_index=False)
        .size()
        .rename(columns={"size": "valid_start_count"})
    )
    for _, row in counts.iterrows():
        beta = int(row["beta_hours"])
        actual = int(row["valid_start_count"])
        expected = EXPECTED_INTERVALS - beta + 1
        if actual != expected:
            raise ValueError(
                f"beta={beta}: expected {expected} valid starts; got {actual}."
            )

    return {
        "rows": int(len(vs)),
        "betas": list(betas),
        "off_by_one_mapping": "PASSED",
        "state_boundary_alignment": "PASSED",
        "circular_wrap": False,
    }


def transition(
    e_kwh: float,
    p_ch_kw: float,
    p_dis_kw: float,
    dt_h: float = DELTA_T_HOURS,
) -> float:
    if p_ch_kw < 0 or p_dis_kw < 0:
        raise ValueError("Charge/discharge powers must be nonnegative.")
    return (
        e_kwh
        + ETA_C * p_ch_kw * dt_h
        - p_dis_kw * dt_h / ETA_D
    )


def synthetic_semantics_audit() -> dict[str, object]:
    e_min = SOC_MIN * TEST_E_N_KWH
    e_max = SOC_MAX * TEST_E_N_KWH
    usable = e_max - e_min
    reserve_floor = e_min + TEST_R_KWH

    if not np.isclose(usable, USABLE_FRACTION * TEST_E_N_KWH):
        raise ValueError("Usable-energy derivation failed.")

    if TEST_R_KWH < 0 or TEST_R_KWH > usable:
        raise ValueError("Synthetic reserve is outside feasible usable energy.")

    # Charge boundary: 100 kW AC for 1 h -> +90 kWh battery.
    e0_charge = 200.0
    e1_charge = transition(
        e0_charge,
        TEST_AC_CHARGE_KW,
        0.0,
    )
    expected_charge = e0_charge + 90.0
    if not np.isclose(e1_charge, expected_charge):
        raise ValueError("AC-to-battery charge efficiency test failed.")

    # Discharge boundary: 90 kW AC for 1 h -> -100 kWh battery.
    e0_dis = 500.0
    e1_dis = transition(
        e0_dis,
        0.0,
        TEST_AC_DISCHARGE_KW,
    )
    expected_dis = e0_dis - 100.0
    if not np.isclose(e1_dis, expected_dis):
        raise ValueError("Battery-to-AC discharge efficiency test failed.")

    # Exact two-interval round-trip state test:
    # +100 kWh AC charge -> +90 battery; 81 kWh AC discharge -> -90 battery.
    e_round0 = 500.0
    e_round1 = transition(e_round0, 100.0, 0.0)
    e_round2 = transition(e_round1, 0.0, 81.0)
    if not np.isclose(e_round2, e_round0):
        raise ValueError("Synthetic periodic round-trip state test failed.")

    rte = 81.0 / 100.0
    if not np.isclose(rte, ROUND_TRIP_EFFICIENCY):
        raise ValueError("Round-trip efficiency derivation failed.")

    # Annual normal-operation preparedness state.
    outage_initial = reserve_floor
    if outage_initial < e_min or outage_initial > e_max:
        raise ValueError("Outage initial preparedness state is infeasible.")

    # Demonstrate reserve consumption during a 3-hour outage.
    # R=300 battery-side kWh exactly supports 3 x 90 kW AC = 270 kWh AC.
    outage_states = [outage_initial]
    for _ in range(3):
        outage_states.append(
            transition(
                outage_states[-1],
                0.0,
                TEST_AC_DISCHARGE_KW,
            )
        )

    if not np.isclose(outage_states[-1], e_min):
        raise ValueError(
            "Synthetic outage terminal did not reach technical SOC_min."
        )

    if min(outage_states) < e_min - 1e-9:
        raise ValueError("Synthetic outage violated technical SOC_min.")

    if max(outage_states) > e_max + 1e-9:
        raise ValueError("Synthetic outage violated technical SOC_max.")

    # The annual reserve floor should intentionally become violated during
    # reserve consumption. If it never does, replay semantics were not tested.
    below_annual_floor_during_outage = any(
        state < reserve_floor - 1e-9
        for state in outage_states[1:]
    )
    if not below_annual_floor_during_outage:
        raise ValueError(
            "Synthetic outage did not demonstrate reserve-floor consumption."
        )

    # Terminal only needs technical minimum, not restoration of R.
    if outage_states[-1] >= reserve_floor - 1e-9:
        raise ValueError(
            "Synthetic terminal incorrectly restored the reserve floor."
        )

    return {
        "test_nameplate_energy_kwh": TEST_E_N_KWH,
        "soc_min": SOC_MIN,
        "soc_max": SOC_MAX,
        "technical_min_energy_kwh": e_min,
        "technical_max_energy_kwh": e_max,
        "usable_energy_kwh": usable,
        "test_reserve_kwh": TEST_R_KWH,
        "annual_reserve_floor_kwh": reserve_floor,
        "outage_initial_energy_kwh": outage_initial,
        "outage_state_trajectory_kwh": outage_states,
        "outage_terminal_energy_kwh": outage_states[-1],
        "eta_c": ETA_C,
        "eta_d": ETA_D,
        "derived_round_trip_efficiency": ROUND_TRIP_EFFICIENCY,
        "charge_test_ac_kwh": 100.0,
        "charge_test_battery_gain_kwh": e1_charge - e0_charge,
        "discharge_test_ac_kwh": 90.0,
        "discharge_test_battery_loss_kwh": e0_dis - e1_dis,
        "periodic_round_trip_initial_kwh": e_round0,
        "periodic_round_trip_terminal_kwh": e_round2,
        "annual_floor_consumed_during_outage": below_annual_floor_during_outage,
        "status": "PASSED",
    }


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        annual_raw, annual_path = read_with_parquet_fallback(
            args.annual_parquet,
            args.annual_csv,
            "Canonical annual input",
        )
        annual = validate_annual(annual_raw)
        state_index = build_state_index(annual)

        starts_raw, starts_path = read_with_parquet_fallback(
            args.valid_starts_parquet,
            args.valid_starts_csv,
            "Script 09 valid-start artifact",
        )
        valid_start_audit = validate_valid_starts(
            starts_raw,
            state_index,
        )

        synthetic = synthetic_semantics_audit()

        args.state_index_output.parent.mkdir(parents=True, exist_ok=True)
        args.semantics_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)

        state_index.to_csv(
            args.state_index_output,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d %H:%M:%S",
        )

        semantics = {
            "script_version": SCRIPT_VERSION,
            "formal_start": str(FORMAL_START),
            "formal_end_exclusive": str(FORMAL_END_EXCLUSIVE),
            "interval_count": EXPECTED_INTERVALS,
            "state_point_count": EXPECTED_STATE_POINTS,
            "delta_t_hours": DELTA_T_HOURS,
            "battery_chemistry": "stationary LFP",
            "power_boundary": "AC/PCS-side",
            "stored_energy_boundary": "battery-side",
            "soc_min": SOC_MIN,
            "soc_max": SOC_MAX,
            "usable_fraction": USABLE_FRACTION,
            "eta_c": ETA_C,
            "eta_d": ETA_D,
            "derived_round_trip_efficiency": ROUND_TRIP_EFFICIENCY,
            "state_transition": (
                "e[t+1] = e[t] + eta_c*p_ch[t]*dt "
                "- p_dis[t]*dt/eta_d"
            ),
            "annual_state_boundary": "e[T] = e[0]",
            "annual_normal_reserve_floor": (
                "e[t] >= SOC_min*E_N + R(alpha,beta)"
            ),
            "outage_initial_state": (
                "e_out[0] = SOC_min*E_N + R(alpha,beta)"
            ),
            "outage_state_bounds": (
                "SOC_min*E_N <= e_out[tau] <= SOC_max*E_N"
            ),
            "outage_terminal_requirement": (
                "e_out[beta] >= SOC_min*E_N"
            ),
            "outage_restore_reserve_at_terminal": False,
            "layer_a_consistency_outage_pv_surplus_recharge": False,
            "valid_start_cross_audit": valid_start_audit,
            "synthetic_unit_audit": synthetic,
            "production_R_computed_here": False,
        }
        args.semantics_output.write_text(
            json.dumps(semantics, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        lines = [
            "NTUST v7.1 BESS State-Semantics Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Inputs",
            f"- Canonical annual input: {annual_path}",
            f"- Script 09 valid-start artifact: {starts_path}",
            "",
            "Annual interval/state indexing",
            f"- Hourly operating intervals: {EXPECTED_INTERVALS:,}",
            f"- Stored-energy state boundaries: {EXPECTED_STATE_POINTS:,}",
            f"- State 0 timestamp: {state_index['state_timestamp'].iloc[0]}",
            f"- State T timestamp: {state_index['state_timestamp'].iloc[-1]}",
            "- Every hourly interval t maps state t -> state t+1: PASSED",
            "- Annual periodic boundary semantics e_T = e_0: LOCKED",
            "",
            "Script 09 cross-audit",
            f"- Valid-start records: {valid_start_audit['rows']:,}",
            f"- Mainline beta set: {valid_start_audit['betas']}",
            "- end_index_exclusive = start_index + beta: PASSED",
            "- Outage start/end timestamps align to state boundaries: PASSED",
            "- No circular wrap: PASSED",
            "",
            "Mainline BESS technical boundary",
            "- Battery chemistry: stationary LFP",
            f"- SOC_min: {SOC_MIN:.2f}",
            f"- SOC_max: {SOC_MAX:.2f}",
            f"- Usable fraction: {USABLE_FRACTION:.2f} E^N",
            "- p_ch, p_dis, P^B: AC/PCS-side",
            "- e_t: battery-side stored energy",
            f"- eta_c: {ETA_C:.2f}",
            f"- eta_d: {ETA_D:.2f}",
            f"- Derived AC-to-AC round-trip efficiency: "
            f"{ROUND_TRIP_EFFICIENCY:.4f}",
            "- State transition: e[t+1] = e[t] + eta_c*p_ch*dt "
            "- p_dis*dt/eta_d",
            "",
            "Synthetic unit checks",
            "- 100 kWh AC charge -> +90 kWh battery: PASSED",
            "- 90 kWh AC discharge -> -100 kWh battery: PASSED",
            "- 100 kWh AC charge followed by 81 kWh AC discharge "
            "returns to the same stored-energy state: PASSED",
            "",
            "Reserve / outage semantics",
            "- Annual normal operation: e_t >= SOC_min*E^N + R: LOCKED",
            "- Outage initial state = SOC_min*E^N + R: LOCKED",
            "- During outage, reserve may be consumed: PASSED",
            "- During outage, only technical 10-90% SOC bounds apply: LOCKED",
            "- Outage terminal requires only e_beta >= SOC_min*E^N: LOCKED",
            "- Immediate restoration of R at outage terminal: NOT REQUIRED",
            "- Layer A consistency replay outage PV-surplus recharge: DISABLED",
            "",
            "Synthetic reserve-consumption demonstration",
            f"- Test E^N: {TEST_E_N_KWH:.1f} kWh",
            f"- Test R: {TEST_R_KWH:.1f} battery-side kWh",
            f"- Annual reserve floor / outage initial state: "
            f"{synthetic['annual_reserve_floor_kwh']:.1f} kWh",
            "- Three hours x 90 kW AC discharge consumes exactly "
            "300 battery-side kWh",
            f"- Outage state trajectory: "
            f"{[round(x, 3) for x in synthetic['outage_state_trajectory_kwh']]}",
            f"- Terminal state: {synthetic['outage_terminal_energy_kwh']:.1f} kWh "
            "= technical SOC_min for the synthetic 1000-kWh battery: PASSED",
            "- The trajectory falls below the annual reserve floor after "
            "outage begins, as intended: PASSED",
            "",
            "Outputs",
            f"- State-boundary index: {args.state_index_output}",
            f"- Machine-readable semantics: {args.semantics_output}",
            f"- Audit summary: {args.audit_output}",
            "",
            "Scope guardrail",
            "- This script does NOT compute production R(alpha,beta).",
            "- This script does NOT size E^N or P^B.",
            "- This script does NOT populate PNNL cost/degradation parameters.",
            "- This script does NOT run annual optimization or outage replay.",
            "",
            "Gate",
            "- Script 10 BESS state-semantics gate: PASSED",
            "- Next v7.1 gate: populate PNNL v2024-derived "
            "C_E, C_P, FOM, C_rep; derive CRF and PWL lambda_k.",
        ]

        args.audit_output.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )
        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(f"Script 10 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
