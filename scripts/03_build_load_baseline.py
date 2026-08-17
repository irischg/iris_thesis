from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7-load-baseline-2026-08-16"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760

# Locked by Script 02 site-specific pseudo-gap validation.
WINDOW_WEEKS = 6
K = 1
MATCHING_METRIC = "same_day_outside_gap_rmse"
RECONSTRUCTION_METHOD = "same_weekday_pm6weeks_top1_context_rmse"

# Expected observed outage structure from Script 01.
EXPECTED_RECONSTRUCTED_HOURS = 10


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()

    parser = argparse.ArgumentParser(
        description=(
            "Build the v7 NTUST planning-baseline Load series by "
            "reconstructing only outage-contaminated Load intervals. "
            "The reconstruction rule is locked by Script 02 validation: "
            "same weekday, ±6 weeks, K=1, donor selected by context RMSE."
        )
    )
    parser.add_argument(
        "--input-parquet",
        type=Path,
        default=(
            root
            / "data"
            / "processed"
            / "ntust_case_year_observed.parquet"
        ),
        help="Preferred Script-01 observed input (Parquet).",
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=(
            root
            / "data"
            / "processed"
            / "ntust_case_year_observed.csv"
        ),
        help="Fallback Script-01 observed input (CSV).",
    )
    parser.add_argument(
        "--validation-ranking",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "load_pseudogap_validation_ranking_v7.csv"
        ),
        help=(
            "Script-02 aggregate validation ranking used to verify "
            "that the production rule matches the empirical winner."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Directory for formal Load baseline outputs.",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=root / "results" / "data_audit",
        help="Directory for reconstruction audit outputs.",
    )
    return parser.parse_args()


def read_parquet_or_csv(
    parquet_path: Path,
    csv_path: Path,
) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError, ValueError):
            pass

    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path

    raise FileNotFoundError(
        "Cannot find Script-01 observed dataset:\n"
        f"- {parquet_path}\n"
        f"- {csv_path}"
    )


def parse_timestamp(series: pd.Series) -> pd.Series:
    result = pd.to_datetime(series, errors="coerce")

    try:
        if result.dt.tz is not None:
            result = (
                result.dt.tz_convert("Asia/Taipei")
                .dt.tz_localize(None)
            )
    except AttributeError:
        pass

    return result


def parse_bool(
    series: pd.Series,
    *,
    fallback: pd.Series | None = None,
) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)

    mapped = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
            }
        )
    )

    if fallback is not None:
        mapped = mapped.fillna(fallback)

    if mapped.isna().any():
        count = int(mapped.isna().sum())
        raise ValueError(
            f"Cannot parse {count} boolean flag values."
        )

    return mapped.astype(bool)


def require_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    missing = [
        column
        for column in columns
        if column not in df.columns
    ]
    if missing:
        raise ValueError(
            f"Script-01 input is missing required columns: {missing}"
        )


def prepare_input(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        df,
        [
            "timestamp",
            "observed_load_kw",
            "load_status",
            "outage_contaminated_flag",
        ],
    )

    result = df.copy()
    result["timestamp"] = parse_timestamp(
        result["timestamp"]
    )

    if result["timestamp"].isna().any():
        count = int(result["timestamp"].isna().sum())
        raise ValueError(
            f"{count} timestamps cannot be parsed."
        )

    result = result.loc[
        (result["timestamp"] >= FORMAL_START)
        & (result["timestamp"] < FORMAL_END_EXCLUSIVE)
    ].copy()

    result = (
        result.sort_values("timestamp")
        .reset_index(drop=True)
    )

    result["observed_load_kw"] = pd.to_numeric(
        result["observed_load_kw"],
        errors="coerce",
    )

    if result["observed_load_kw"].isna().any():
        count = int(
            result["observed_load_kw"].isna().sum()
        )
        raise ValueError(
            f"observed_load_kw contains {count} missing values."
        )

    fallback_flag = (
        result["load_status"]
        .astype("string")
        .ne("normal")
    )

    result["outage_contaminated_flag"] = parse_bool(
        result["outage_contaminated_flag"],
        fallback=fallback_flag,
    )

    return result


def validate_timeline(df: pd.DataFrame) -> None:
    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )
    actual = pd.DatetimeIndex(df["timestamp"])

    if len(df) != EXPECTED_HOURS:
        raise ValueError(
            f"Input contains {len(df):,} rows; "
            f"expected {EXPECTED_HOURS:,}."
        )

    if df["timestamp"].duplicated().any():
        count = int(
            df["timestamp"].duplicated().sum()
        )
        raise ValueError(
            f"Input contains {count} duplicate timestamps."
        )

    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise ValueError(
            "Input is not the exact v7 case-year timeline: "
            f"missing={len(missing)}, extra={len(extra)}."
        )


def verify_validation_rule(
    ranking_path: Path,
) -> dict[str, object]:
    if not ranking_path.exists():
        raise FileNotFoundError(
            "Script-02 validation ranking is required before "
            "production reconstruction:\n"
            f"{ranking_path}"
        )

    ranking = pd.read_csv(ranking_path)

    required = {
        "aggregation",
        "window_weeks",
        "k",
        "diagnostic_mean_rank",
        "mae_kw",
        "rmse_kw",
        "signed_energy_bias_pct",
        "mean_event_abs_energy_bias_kwh",
    }

    missing = required.difference(ranking.columns)
    if missing:
        raise ValueError(
            "Validation ranking is missing required columns: "
            f"{sorted(missing)}"
        )

    ranking["window_weeks"] = pd.to_numeric(
        ranking["window_weeks"],
        errors="coerce",
    )
    ranking["k"] = pd.to_numeric(
        ranking["k"],
        errors="coerce",
    )
    ranking["diagnostic_mean_rank"] = pd.to_numeric(
        ranking["diagnostic_mean_rank"],
        errors="coerce",
    )

    if ranking[
        [
            "window_weeks",
            "k",
            "diagnostic_mean_rank",
        ]
    ].isna().any().any():
        raise ValueError(
            "Validation ranking contains non-numeric rule/rank fields."
        )

    best_rank = float(
        ranking["diagnostic_mean_rank"].min()
    )

    winners = ranking.loc[
        np.isclose(
            ranking["diagnostic_mean_rank"],
            best_rank,
            rtol=0.0,
            atol=1e-12,
        )
    ].copy()

    # K=1 makes mean and median mathematically identical, so two
    # aggregation-labelled rows are expected for the same rule.
    winner_rules = (
        winners[
            [
                "window_weeks",
                "k",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if len(winner_rules) != 1:
        raise ValueError(
            "Script-02 ranking does not identify one unique "
            "window/K winning rule. Do not run production reconstruction."
        )

    winner_window = int(
        winner_rules.loc[0, "window_weeks"]
    )
    winner_k = int(
        winner_rules.loc[0, "k"]
    )

    if (
        winner_window != WINDOW_WEEKS
        or winner_k != K
    ):
        raise ValueError(
            "Production rule does not match Script-02 empirical winner: "
            f"ranking winner=±{winner_window} weeks/K={winner_k}, "
            f"script rule=±{WINDOW_WEEKS} weeks/K={K}."
        )

    representative = (
        winners.sort_values("aggregation")
        .iloc[0]
    )

    return {
        "best_diagnostic_mean_rank": best_rank,
        "winner_window_weeks": winner_window,
        "winner_k": winner_k,
        "validation_mae_kw": float(
            representative["mae_kw"]
        ),
        "validation_rmse_kw": float(
            representative["rmse_kw"]
        ),
        "validation_signed_energy_bias_pct": float(
            representative[
                "signed_energy_bias_pct"
            ]
        ),
        "validation_mean_event_abs_energy_bias_kwh": float(
            representative[
                "mean_event_abs_energy_bias_kwh"
            ]
        ),
    }


def identify_outage_events(
    df: pd.DataFrame,
) -> list[pd.DataFrame]:
    outage = df.loc[
        df["outage_contaminated_flag"]
    ].copy()

    if outage.empty:
        raise ValueError(
            "No outage-contaminated Load hours were found."
        )

    outage = (
        outage.sort_values("timestamp")
        .copy()
    )

    new_group = (
        outage["timestamp"]
        .diff()
        .ne(pd.Timedelta(hours=1))
    )
    outage["_outage_group"] = new_group.cumsum()

    groups: list[pd.DataFrame] = []

    for _, group in outage.groupby(
        "_outage_group",
        sort=False,
    ):
        event = (
            group.drop(columns=["_outage_group"])
            .copy()
            .reset_index()
            .rename(columns={"index": "source_row_index"})
        )

        start = event["timestamp"].iloc[0]
        end = event["timestamp"].iloc[-1]

        if start.normalize() != end.normalize():
            raise ValueError(
                "Current validated Load donor rule assumes "
                "same-day outage blocks, but an event crosses midnight: "
                f"{start} to {end}."
            )

        groups.append(event)

    return groups


class LoadDayCache:
    def __init__(self, df: pd.DataFrame):
        self.indexed = df.set_index(
            "timestamp",
            drop=False,
        )
        self._valid_day_cache: dict[
            pd.Timestamp,
            bool,
        ] = {}
        self._day_load_cache: dict[
            pd.Timestamp,
            np.ndarray,
        ] = {}

    def has_full_valid_day(
        self,
        day_start: pd.Timestamp,
    ) -> bool:
        day_start = pd.Timestamp(
            day_start
        ).normalize()

        if day_start in self._valid_day_cache:
            return self._valid_day_cache[
                day_start
            ]

        timestamps = pd.date_range(
            day_start,
            periods=24,
            freq="h",
        )

        if not timestamps.isin(
            self.indexed.index
        ).all():
            self._valid_day_cache[
                day_start
            ] = False
            return False

        day = self.indexed.loc[timestamps]

        load = pd.to_numeric(
            day["observed_load_kw"],
            errors="coerce",
        )

        valid = bool(
            day["load_status"]
            .astype(str)
            .eq("normal")
            .all()
            and load.notna().all()
            and (load > 0).all()
        )

        self._valid_day_cache[
            day_start
        ] = valid

        if valid:
            self._day_load_cache[
                day_start
            ] = load.to_numpy(
                dtype="float64"
            )

        return valid

    def day_load(
        self,
        day_start: pd.Timestamp,
    ) -> np.ndarray:
        day_start = pd.Timestamp(
            day_start
        ).normalize()

        if not self.has_full_valid_day(
            day_start
        ):
            raise ValueError(
                "Day is not a fully valid donor day: "
                f"{day_start}"
            )

        return self._day_load_cache[
            day_start
        ].copy()


def candidate_donors(
    cache: LoadDayCache,
    *,
    outage_start: pd.Timestamp,
    outage_duration_hours: int,
) -> pd.DataFrame:
    target_day = outage_start.normalize()
    target_timestamps = pd.date_range(
        target_day,
        periods=24,
        freq="h",
    )

    # The target day itself may contain outage zeros, so read it
    # directly rather than requiring a fully-valid target day.
    target_day_frame = cache.indexed.loc[
        target_timestamps
    ]
    target_load = pd.to_numeric(
        target_day_frame["observed_load_kw"],
        errors="coerce",
    ).to_numpy(dtype="float64")

    start_hour = int(outage_start.hour)

    gap_hours = list(
        range(
            start_hour,
            start_hour + outage_duration_hours,
        )
    )

    if (
        not gap_hours
        or min(gap_hours) < 0
        or max(gap_hours) > 23
    ):
        raise ValueError(
            "Validated donor rule cannot handle an outage "
            "that crosses midnight."
        )

    context_hours = [
        hour
        for hour in range(24)
        if hour not in set(gap_hours)
    ]

    target_context = target_load[
        context_hours
    ]

    if not np.isfinite(
        target_context
    ).all():
        raise ValueError(
            "Target-day context contains missing Load values."
        )

    if np.any(
        target_context <= 0
    ):
        raise ValueError(
            "Target-day context contains non-positive Load "
            "outside the outage block."
        )

    rows: list[dict[str, object]] = []

    for week_offset in range(
        -WINDOW_WEEKS,
        WINDOW_WEEKS + 1,
    ):
        if week_offset == 0:
            continue

        donor_start = (
            outage_start
            + pd.Timedelta(
                weeks=week_offset
            )
        )
        donor_day = donor_start.normalize()

        if not cache.has_full_valid_day(
            donor_day
        ):
            continue

        donor_load = cache.day_load(
            donor_day
        )

        donor_context = donor_load[
            context_hours
        ]

        context_rmse = float(
            np.sqrt(
                np.mean(
                    (
                        donor_context
                        - target_context
                    )
                    ** 2
                )
            )
        )

        rows.append(
            {
                "week_offset": week_offset,
                "donor_start": donor_start,
                "donor_day": donor_day,
                "context_rmse_kw": context_rmse,
                "gap_values_kw": donor_load[
                    gap_hours
                ],
            }
        )

    if len(rows) < K:
        raise ValueError(
            f"{outage_start}: only {len(rows)} valid donors "
            f"within ±{WINDOW_WEEKS} weeks; K={K} required."
        )

    donors = pd.DataFrame(rows)

    donors = donors.sort_values(
        [
            "context_rmse_kw",
            "week_offset",
            "donor_start",
        ],
        key=lambda s: (
            s.abs()
            if s.name == "week_offset"
            else s
        ),
    ).reset_index(drop=True)

    return donors


def write_parquet_if_available(
    df: pd.DataFrame,
    path: Path,
) -> bool:
    try:
        df.to_parquet(
            path,
            index=False,
        )
        return True
    except (
        ImportError,
        ModuleNotFoundError,
    ):
        return False


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        args.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.audit_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        validation = verify_validation_rule(
            args.validation_ranking
        )

        raw, input_path = read_parquet_or_csv(
            args.input_parquet,
            args.input_csv,
        )

        data = prepare_input(raw)
        validate_timeline(data)

        output = data.copy()
        output["baseline_load_kw"] = (
            output["observed_load_kw"]
            .astype("float64")
        )
        output["load_reconstructed"] = False
        output["load_reconstruction_method"] = "observed"
        output["load_donor_timestamp"] = pd.NaT
        output["load_donor_week_offset"] = pd.Series(
            pd.NA,
            index=output.index,
            dtype="Int64",
        )
        output["load_donor_context_rmse_kw"] = np.nan

        cache = LoadDayCache(data)
        outage_events = identify_outage_events(
            data
        )

        audit_rows: list[
            dict[str, object]
        ] = []

        for event_id, event in enumerate(
            outage_events,
            start=1,
        ):
            outage_start = event[
                "timestamp"
            ].iloc[0]
            outage_end = event[
                "timestamp"
            ].iloc[-1]
            duration = len(event)

            donors = candidate_donors(
                cache,
                outage_start=outage_start,
                outage_duration_hours=duration,
            )

            selected = donors.head(K).iloc[0]
            replacement = np.asarray(
                selected["gap_values_kw"],
                dtype="float64",
            )

            if len(replacement) != duration:
                raise RuntimeError(
                    "Selected donor block length does not match "
                    "outage duration."
                )

            if not np.isfinite(
                replacement
            ).all():
                raise RuntimeError(
                    "Selected donor block contains missing values."
                )

            if np.any(
                replacement <= 0
            ):
                raise RuntimeError(
                    "Selected donor block contains non-positive Load."
                )

            target_indices = (
                event["source_row_index"]
                .astype(int)
                .to_numpy()
            )

            output.loc[
                target_indices,
                "baseline_load_kw",
            ] = replacement
            output.loc[
                target_indices,
                "load_reconstructed",
            ] = True
            output.loc[
                target_indices,
                "load_reconstruction_method",
            ] = RECONSTRUCTION_METHOD
            output.loc[
                target_indices,
                "load_donor_timestamp",
            ] = pd.Timestamp(
                selected["donor_start"]
            )
            output.loc[
                target_indices,
                "load_donor_week_offset",
            ] = int(
                selected["week_offset"]
            )
            output.loc[
                target_indices,
                "load_donor_context_rmse_kw",
            ] = float(
                selected["context_rmse_kw"]
            )

            for hour_in_event, row_index in enumerate(
                target_indices
            ):
                audit_rows.append(
                    {
                        "event_id": event_id,
                        "outage_start": outage_start,
                        "outage_end_inclusive": outage_end,
                        "duration_hours": duration,
                        "target_timestamp": output.at[
                            row_index,
                            "timestamp",
                        ],
                        "observed_load_kw": output.at[
                            row_index,
                            "observed_load_kw",
                        ],
                        "baseline_load_kw": output.at[
                            row_index,
                            "baseline_load_kw",
                        ],
                        "donor_timestamp": pd.Timestamp(
                            selected["donor_start"]
                        ),
                        "donor_week_offset": int(
                            selected["week_offset"]
                        ),
                        "donor_context_rmse_kw": float(
                            selected["context_rmse_kw"]
                        ),
                        "hour_in_event": hour_in_event,
                        "method": RECONSTRUCTION_METHOD,
                    }
                )

        reconstructed_count = int(
            output["load_reconstructed"].sum()
        )

        if (
            reconstructed_count
            != EXPECTED_RECONSTRUCTED_HOURS
        ):
            raise ValueError(
                f"Reconstructed {reconstructed_count} Load hours; "
                f"expected {EXPECTED_RECONSTRUCTED_HOURS}."
            )

        if output[
            "baseline_load_kw"
        ].isna().any():
            count = int(
                output[
                    "baseline_load_kw"
                ].isna().sum()
            )
            raise ValueError(
                f"baseline_load_kw still has {count} missing values."
            )

        if (
            output["baseline_load_kw"]
            <= 0
        ).any():
            count = int(
                (
                    output["baseline_load_kw"]
                    <= 0
                ).sum()
            )
            raise ValueError(
                f"baseline_load_kw still has {count} "
                "non-positive values."
            )

        normal_mask = ~output[
            "outage_contaminated_flag"
        ]

        normal_difference = np.abs(
            output.loc[
                normal_mask,
                "baseline_load_kw",
            ].to_numpy(dtype=float)
            - output.loc[
                normal_mask,
                "observed_load_kw",
            ].to_numpy(dtype=float)
        )

        if (
            len(normal_difference)
            and float(
                normal_difference.max()
            ) > 0.0
        ):
            raise ValueError(
                "Production reconstruction changed Load values "
                "outside outage-contaminated intervals."
            )

        # 1-hour intervals: interval energy kWh and average kW are
        # numerically identical. Keep both names for provenance.
        output[
            "baseline_load_kwh"
        ] = output[
            "baseline_load_kw"
        ]
        output[
            "observed_load_kwh"
        ] = output[
            "observed_load_kw"
        ]

        preferred_columns = [
            "timestamp_raw_end",
            "timestamp_start",
            "timestamp",
            "observed_load_kwh",
            "observed_load_kw",
            "baseline_load_kwh",
            "baseline_load_kw",
            "load_status",
            "event_flag",
            "outage_contaminated_flag",
            "load_reconstructed",
            "load_reconstruction_method",
            "load_donor_timestamp",
            "load_donor_week_offset",
            "load_donor_context_rmse_kw",
            "year",
            "month",
            "day",
            "hour",
            "weekday",
            "is_weekend",
        ]

        final_columns = [
            column
            for column in preferred_columns
            if column in output.columns
        ]

        # Preserve any additional Script-01 provenance columns after
        # the core Load-baseline fields.
        additional_columns = [
            column
            for column in output.columns
            if column not in final_columns
            and column
            not in {
                "baseline_load_kwh",
                "observed_load_kwh",
            }
        ]

        final_output = output[
            final_columns
            + additional_columns
        ].copy()

        csv_path = (
            args.output_dir
            / "load_annual_baseline.csv"
        )
        parquet_path = (
            args.output_dir
            / "load_annual_baseline.parquet"
        )
        audit_path = (
            args.audit_dir
            / "load_reconstruction_applied_v7.csv"
        )
        summary_path = (
            args.audit_dir
            / "load_reconstruction_summary_v7.txt"
        )

        final_output.to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig",
        )

        parquet_written = (
            write_parquet_if_available(
                final_output,
                parquet_path,
            )
        )

        audit = pd.DataFrame(
            audit_rows
        )
        audit.to_csv(
            audit_path,
            index=False,
            encoding="utf-8-sig",
        )

        event_summary = (
            audit.groupby(
                [
                    "event_id",
                    "outage_start",
                    "outage_end_inclusive",
                    "duration_hours",
                    "donor_timestamp",
                    "donor_week_offset",
                    "donor_context_rmse_kw",
                    "method",
                ],
                as_index=False,
            )
            .agg(
                observed_event_energy_kwh=(
                    "observed_load_kw",
                    "sum",
                ),
                reconstructed_event_energy_kwh=(
                    "baseline_load_kw",
                    "sum",
                ),
            )
        )

        summary_lines = [
            "NTUST v7 Load Baseline Reconstruction",
            f"Script version: {SCRIPT_VERSION}",
            f"Observed input: {input_path}",
            f"Validation ranking: {args.validation_ranking}",
            "",
            "Locked production rule",
            f"- Same weekday: yes",
            f"- Candidate window: ±{WINDOW_WEEKS} weeks",
            f"- K: {K}",
            f"- Matching metric: {MATCHING_METRIC}",
            f"- Reconstruction method label: {RECONSTRUCTION_METHOD}",
            "- K=1 means no mean/median aggregation choice remains.",
            "",
            "Script-02 validation evidence",
            f"- Best diagnostic mean rank: "
            f"{validation['best_diagnostic_mean_rank']:.3f}",
            f"- Validation MAE: "
            f"{validation['validation_mae_kw']:.6f} kW",
            f"- Validation RMSE: "
            f"{validation['validation_rmse_kw']:.6f} kW",
            f"- Validation signed energy bias: "
            f"{validation['validation_signed_energy_bias_pct']:.6f} %",
            f"- Validation mean event absolute energy bias: "
            f"{validation['validation_mean_event_abs_energy_bias_kwh']:.6f} kWh",
            "",
            "Formal case year",
            f"- Rows: {len(final_output):,}",
            f"- Start: {final_output['timestamp'].min()}",
            f"- End: {final_output['timestamp'].max()}",
            f"- Reconstructed Load hours: {reconstructed_count}",
            "- Observed Load is preserved unchanged.",
            "- Only baseline_load_kw is replaced at outage-contaminated hours.",
            "",
            "Applied outage events",
            event_summary.to_string(index=False),
            "",
            "Validation checks",
            "- Formal 8,760-hour timeline: PASSED",
            "- baseline_load_kw missing values: 0",
            "- baseline_load_kw non-positive values: 0",
            "- Non-outage baseline/observed differences: 0",
            f"- Expected reconstructed hours ({EXPECTED_RECONSTRUCTED_HOURS}): PASSED",
            "",
            "Outputs",
            f"- {csv_path}",
            (
                f"- {parquet_path}"
                if parquet_written
                else "- Parquet skipped (pyarrow/fastparquet unavailable)"
            ),
            f"- {audit_path}",
            f"- {summary_path}",
        ]

        summary_path.write_text(
            "\n".join(summary_lines)
            + "\n",
            encoding="utf-8",
        )

        print(
            "\n".join(
                summary_lines
            )
        )
        print()
        print(
            "Script 03 completed. "
            "The observed Load series remains unchanged; "
            "only the planning-baseline Load is reconstructed."
        )

        return 0

    except Exception as exc:
        print(
            f"Script 03 failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
