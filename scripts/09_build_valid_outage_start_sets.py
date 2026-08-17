#!/usr/bin/env python3
"""
09_build_valid_outage_start_sets.py

NTUST thesis v7.1 — valid historical outage-start set builder.

Mainline role
-------------
Build the formal valid-start sets S_beta for Layer A from the canonical
8,760-hour interval-start annual input.

For hourly resolution (Delta t = 1 h), the v7.1 definition is:

    S_beta = {s : s + beta <= T}

where T = 8760.

Therefore a beta-hour outage window is valid only when every hourly interval
from s through s + beta - 1 lies inside the formal case year:

    2024-11-01 00:00 <= t < 2025-11-01 00:00

Mainline beta values:
    4, 5, 6, 7, 8, 9, 10, 11, 12 hours

This script deliberately does NOT:
- circularly wrap year-end windows back to the beginning of the case year;
- select a single design-basis outage anchor;
- calculate R(alpha, beta);
- calculate P_out(alpha);
- run outage replay;
- run EOB / Layer A / Layer B optimization.

The output is a reusable audited indexing artifact for later Layer A
precomputation and consistency replay.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.1-valid-outage-starts-2026-08-17"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760
DELTA_T_HOURS = 1

DEFAULT_BETAS = tuple(range(4, 13))


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()

    parser = argparse.ArgumentParser(
        description="Build v7.1 valid historical outage-start sets S_beta."
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
        "--betas",
        nargs="+",
        type=int,
        default=list(DEFAULT_BETAS),
        help=(
            "Outage durations in hours. "
            "Default mainline set is 4 5 6 7 8 9 10 11 12."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "data" / "processed",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=root / "results" / "data_audit",
    )
    return parser.parse_args()


def read_annual(
    parquet_path: Path,
    csv_path: Path,
) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        "Final integrated annual input not found. Expected either:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}"
    )


def validate_annual_input(df: pd.DataFrame) -> pd.DataFrame:
    required = {"timestamp", "integration_status"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"Annual input missing required columns: {missing}"
        )

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")

    if out["timestamp"].isna().any():
        raise ValueError("Annual input contains unparsable timestamps.")

    if len(out) != EXPECTED_ROWS:
        raise ValueError(
            f"Annual input must contain exactly {EXPECTED_ROWS} rows; "
            f"found {len(out)}."
        )

    if out["timestamp"].duplicated().any():
        raise ValueError("Annual input contains duplicate timestamps.")

    out = out.sort_values("timestamp").reset_index(drop=True)

    expected = pd.date_range(
        FORMAL_START,
        periods=EXPECTED_ROWS,
        freq="h",
    )
    actual = pd.DatetimeIndex(out["timestamp"])

    if not actual.equals(expected):
        raise ValueError(
            "Annual input is not the exact v7.1 interval-start case year: "
            "2024-11-01 00:00 through 2025-10-31 23:00."
        )

    statuses = set(
        out["integration_status"].astype(str).str.strip()
    )
    if statuses != {"passed"}:
        raise ValueError(
            "Production valid-start indexing requires "
            "integration_status='passed'. "
            f"Found: {sorted(statuses)}"
        )

    if len(actual) > 1:
        deltas = actual[1:] - actual[:-1]
        expected_delta = pd.Timedelta(hours=DELTA_T_HOURS)
        if not np.all(deltas == expected_delta):
            raise ValueError(
                "Annual input contains a non-hourly or missing timestep."
            )

    if actual[0] != FORMAL_START:
        raise ValueError(
            f"Unexpected first timestamp: {actual[0]}"
        )

    expected_last = FORMAL_END_EXCLUSIVE - pd.Timedelta(hours=1)
    if actual[-1] != expected_last:
        raise ValueError(
            f"Unexpected last timestamp: {actual[-1]}"
        )

    return out


def validate_betas(betas: list[int]) -> list[int]:
    if not betas:
        raise ValueError("At least one beta must be supplied.")

    cleaned = sorted(set(int(x) for x in betas))

    for beta in cleaned:
        if beta <= 0:
            raise ValueError(
                f"beta must be a positive integer number of hours; got {beta}."
            )
        if beta > EXPECTED_ROWS:
            raise ValueError(
                f"beta cannot exceed the case-year length; got {beta}."
            )

    return cleaned


def build_valid_start_rows(
    timestamps: pd.Series,
    beta: int,
) -> pd.DataFrame:
    """
    For T rows and beta hourly intervals:
        valid integer starts = 0 .. T-beta
        count = T-beta+1

    No modulo arithmetic is used anywhere.
    """
    t_count = len(timestamps)
    valid_count = t_count - beta + 1

    if valid_count <= 0:
        raise ValueError(
            f"beta={beta}: no valid starts in T={t_count}."
        )

    start_index = np.arange(valid_count, dtype=np.int64)
    end_index_inclusive = start_index + beta - 1
    end_index_exclusive = start_index + beta

    start_ts = timestamps.iloc[start_index].reset_index(drop=True)
    end_ts_inclusive = (
        timestamps.iloc[end_index_inclusive]
        .reset_index(drop=True)
    )
    end_ts_exclusive = start_ts + pd.to_timedelta(beta, unit="h")

    frame = pd.DataFrame(
        {
            "beta_hours": beta,
            "start_index": start_index,
            "start_timestamp": start_ts,
            "end_index_inclusive": end_index_inclusive,
            "end_timestamp_inclusive": end_ts_inclusive,
            "end_index_exclusive": end_index_exclusive,
            "end_timestamp_exclusive": end_ts_exclusive,
            "window_hours": beta,
        }
    )

    frame["is_first_valid_start"] = frame["start_index"].eq(0)
    frame["is_last_valid_start"] = frame["start_index"].eq(
        valid_count - 1
    )

    # Explicit anti-wrap diagnostics.
    frame["within_case_year"] = (
        frame["start_timestamp"].ge(FORMAL_START)
        & frame["end_timestamp_exclusive"].le(
            FORMAL_END_EXCLUSIVE
        )
    )
    frame["circular_wrap_used"] = False

    return frame


def audit_one_beta(frame: pd.DataFrame, beta: int) -> dict[str, object]:
    expected_count = EXPECTED_ROWS - beta + 1

    if len(frame) != expected_count:
        raise ValueError(
            f"beta={beta}: valid-start count mismatch. "
            f"expected={expected_count}, actual={len(frame)}"
        )

    if frame["start_index"].iloc[0] != 0:
        raise ValueError(
            f"beta={beta}: first start index is not 0."
        )

    expected_last_start_index = EXPECTED_ROWS - beta
    if frame["start_index"].iloc[-1] != expected_last_start_index:
        raise ValueError(
            f"beta={beta}: last start index mismatch. "
            f"expected={expected_last_start_index}, "
            f"actual={frame['start_index'].iloc[-1]}"
        )

    expected_first_start = FORMAL_START
    if frame["start_timestamp"].iloc[0] != expected_first_start:
        raise ValueError(
            f"beta={beta}: first valid start timestamp mismatch."
        )

    expected_last_start = (
        FORMAL_END_EXCLUSIVE - pd.Timedelta(hours=beta)
    )
    if frame["start_timestamp"].iloc[-1] != expected_last_start:
        raise ValueError(
            f"beta={beta}: last valid start timestamp mismatch. "
            f"expected={expected_last_start}, "
            f"actual={frame['start_timestamp'].iloc[-1]}"
        )

    if not frame["within_case_year"].all():
        bad = frame.loc[~frame["within_case_year"]].head()
        raise ValueError(
            f"beta={beta}: found window outside case year:\n"
            + bad.to_string(index=False)
        )

    if frame["circular_wrap_used"].any():
        raise ValueError(
            f"beta={beta}: circular-wrap flag unexpectedly true."
        )

    # The final valid window must end exactly at the case-year boundary.
    if (
        frame["end_timestamp_exclusive"].iloc[-1]
        != FORMAL_END_EXCLUSIVE
    ):
        raise ValueError(
            f"beta={beta}: final valid window does not end "
            "exactly at formal end-exclusive boundary."
        )

    # Each window must contain exactly beta hourly rows.
    index_width = (
        frame["end_index_inclusive"]
        - frame["start_index"]
        + 1
    )
    if not index_width.eq(beta).all():
        raise ValueError(
            f"beta={beta}: index window width is not exactly beta."
        )

    timestamp_width_hours = (
        (
            frame["end_timestamp_exclusive"]
            - frame["start_timestamp"]
        )
        / pd.Timedelta(hours=1)
    )
    if not np.allclose(
        timestamp_width_hours.to_numpy(dtype=float),
        float(beta),
        rtol=0.0,
        atol=0.0,
    ):
        raise ValueError(
            f"beta={beta}: timestamp window width is not exactly beta."
        )

    return {
        "beta_hours": beta,
        "valid_start_count": len(frame),
        "expected_valid_start_count": expected_count,
        "first_valid_start_index": int(
            frame["start_index"].iloc[0]
        ),
        "last_valid_start_index": int(
            frame["start_index"].iloc[-1]
        ),
        "first_valid_start_timestamp": (
            frame["start_timestamp"].iloc[0]
        ),
        "last_valid_start_timestamp": (
            frame["start_timestamp"].iloc[-1]
        ),
        "final_window_end_exclusive": (
            frame["end_timestamp_exclusive"].iloc[-1]
        ),
        "circular_wrap_used": False,
        "status": "PASSED",
    }


def write_parquet_if_available(
    df: pd.DataFrame,
    path: Path,
) -> bool:
    try:
        df.to_parquet(path, index=False)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.audit_dir.mkdir(parents=True, exist_ok=True)

        annual_raw, annual_path = read_annual(
            args.annual_parquet,
            args.annual_csv,
        )
        annual = validate_annual_input(annual_raw)
        betas = validate_betas(args.betas)

        frames: list[pd.DataFrame] = []
        summary_rows: list[dict[str, object]] = []

        for beta in betas:
            frame = build_valid_start_rows(
                annual["timestamp"],
                beta,
            )
            summary = audit_one_beta(frame, beta)

            frames.append(frame)
            summary_rows.append(summary)

        valid_starts = pd.concat(
            frames,
            axis=0,
            ignore_index=True,
        )
        summary_df = pd.DataFrame(summary_rows)

        # Global anti-wrap guardrail.
        if valid_starts["circular_wrap_used"].any():
            raise ValueError(
                "Global audit failed: circular wrap was used."
            )

        if not valid_starts["within_case_year"].all():
            raise ValueError(
                "Global audit failed: at least one window "
                "extends beyond the case year."
            )

        csv_path = (
            args.output_dir
            / "valid_outage_starts_v7_1.csv"
        )
        parquet_path = (
            args.output_dir
            / "valid_outage_starts_v7_1.parquet"
        )
        summary_path = (
            args.audit_dir
            / "valid_outage_start_counts_v7_1.csv"
        )
        audit_path = (
            args.audit_dir
            / "valid_outage_starts_v7_1_audit.txt"
        )

        valid_starts.to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d %H:%M:%S",
        )
        parquet_written = write_parquet_if_available(
            valid_starts,
            parquet_path,
        )

        summary_df.to_csv(
            summary_path,
            index=False,
            encoding="utf-8-sig",
            date_format="%Y-%m-%d %H:%M:%S",
        )

        parquet_summary = (
            str(parquet_path)
            if parquet_written
            else "not written (pyarrow/fastparquet unavailable)"
        )

        lines = [
            "NTUST v7.1 Valid Outage-Start Set Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Input",
            f"- Canonical annual input: {annual_path}",
            f"- Rows: {len(annual):,}",
            f"- Formal start: {FORMAL_START}",
            f"- Formal end-exclusive: {FORMAL_END_EXCLUSIVE}",
            "- Exact hourly chronology: PASSED",
            "- integration_status='passed': PASSED",
            "",
            "Formal valid-start rule",
            "- S_beta = {s : s + beta <= T}, with Delta t = 1 hour",
            "- No modulo indexing: PASSED",
            "- No year-end circular wrap: PASSED",
            "- Only full beta-hour trajectories inside the case year are retained.",
            "",
            "Beta set",
            f"- Requested betas: {betas}",
            f"- Mainline default: {list(DEFAULT_BETAS)}",
            "",
            "Per-beta counts",
        ]

        for row in summary_rows:
            lines.append(
                f"- beta={row['beta_hours']:>2} h: "
                f"{row['valid_start_count']:,} starts; "
                f"first={row['first_valid_start_timestamp']}; "
                f"last={row['last_valid_start_timestamp']}; "
                f"final end-exclusive={row['final_window_end_exclusive']} "
                "[PASSED]"
            )

        lines.extend(
            [
                "",
                "Global checks",
                f"- Total start-window records: {len(valid_starts):,}",
                "- Every end_timestamp_exclusive <= formal boundary: PASSED",
                "- Every final valid window ends exactly at 2025-11-01 00:00: PASSED",
                "- No artificial next-year continuation data used: PASSED",
                "- No legacy single-anchor logic used: PASSED",
                "",
                "Outputs",
                f"- CSV: {csv_path}",
                f"- Parquet: {parquet_summary}",
                f"- Count summary: {summary_path}",
                f"- Audit summary: {audit_path}",
                "",
                "Gate",
                "- Script 09 valid-start indexing gate: PASSED",
                "- This artifact defines indexing only.",
                "- R(alpha,beta), P_out(alpha), binding critical windows, "
                "outage replay, and optimization were NOT computed here.",
                "- Next implementation gate: battery state semantics "
                "(e_t, 10-90% SOC, reserve above SOCmin, eta_c=eta_d=0.90).",
            ]
        )

        audit_path.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )

        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(
            f"Script 09 failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
