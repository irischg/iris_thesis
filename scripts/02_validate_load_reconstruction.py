from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7-load-pseudogap-validation-2026-08-15"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760

# Validation grid. ±8 weeks / K=3 is intentionally only one candidate.
WINDOW_WEEKS = tuple(range(3, 13))   # 3, 4, ..., 12 weeks
K_VALUES = (1, 2, 3, 4, 5)
AGGREGATIONS = ("median", "mean")

V7_CANDIDATE_WINDOW_WEEKS = 8
V7_CANDIDATE_K = 3


def project_root() -> Path:
    # Expected location:
    # <project>/scripts/02_validate_load_reconstruction.py
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()

    parser = argparse.ArgumentParser(
        description=(
            "Validate Load donor-reconstruction hyperparameters using "
            "artificial pseudo-gaps on the v7 observed NTUST case-year. "
            "This script does NOT reconstruct the real outage hours."
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
        "--output-dir",
        type=Path,
        default=root / "results" / "data_audit",
        help="Directory for pseudo-gap validation outputs.",
    )
    return parser.parse_args()


def read_input(
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
    result["timestamp"] = parse_timestamp(result["timestamp"])

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

    result["outage_contaminated_flag"] = (
        result["outage_contaminated_flag"]
        .astype("string")
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
            }
        )
        .fillna(
            result["load_status"].astype("string").ne("normal")
        )
        .astype(bool)
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


def identify_outage_events(
    df: pd.DataFrame,
) -> pd.DataFrame:
    outage = df.loc[
        df["outage_contaminated_flag"]
    ][
        [
            "timestamp",
            "load_status",
        ]
    ].copy()

    if outage.empty:
        raise ValueError(
            "No outage-contaminated Load hours were found."
        )

    outage = outage.sort_values("timestamp").reset_index(drop=True)

    new_group = (
        outage["timestamp"]
        .diff()
        .ne(pd.Timedelta(hours=1))
    )
    outage["_group"] = new_group.cumsum()

    rows: list[dict[str, object]] = []

    for event_number, (_, group) in enumerate(
        outage.groupby("_group", sort=False),
        start=1,
    ):
        start = group["timestamp"].iloc[0]
        end = group["timestamp"].iloc[-1]
        duration = len(group)

        if start.normalize() != end.normalize():
            raise ValueError(
                "Current Script 02 uses same-day pseudo-gap templates, "
                "but an observed outage crosses midnight: "
                f"{start} to {end}."
            )

        rows.append(
            {
                "source_event_id": event_number,
                "source_start": start,
                "source_end_inclusive": end,
                "duration_hours": duration,
                "weekday": int(start.weekday()),
                "start_hour": int(start.hour),
                "load_statuses": "|".join(
                    sorted(
                        group["load_status"]
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                ),
            }
        )

    return pd.DataFrame(rows)


def build_unique_templates(
    outage_events: pd.DataFrame,
) -> pd.DataFrame:
    templates = (
        outage_events[
            [
                "weekday",
                "start_hour",
                "duration_hours",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "weekday",
                "start_hour",
                "duration_hours",
            ]
        )
        .reset_index(drop=True)
    )

    templates.insert(
        0,
        "template_id",
        [
            f"T{index:02d}"
            for index in range(1, len(templates) + 1)
        ],
    )

    return templates


class LoadDayCache:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.indexed = df.set_index(
            "timestamp",
            drop=False,
        )
        self._valid_day_cache: dict[pd.Timestamp, bool] = {}
        self._day_load_cache: dict[pd.Timestamp, np.ndarray] = {}

    def has_full_valid_day(
        self,
        day_start: pd.Timestamp,
    ) -> bool:
        day_start = pd.Timestamp(day_start).normalize()

        if day_start in self._valid_day_cache:
            return self._valid_day_cache[day_start]

        timestamps = pd.date_range(
            day_start,
            periods=24,
            freq="h",
        )

        if not timestamps.isin(self.indexed.index).all():
            self._valid_day_cache[day_start] = False
            return False

        day = self.indexed.loc[timestamps]

        status_ok = day["load_status"].astype(str).eq("normal").all()
        load = pd.to_numeric(
            day["observed_load_kw"],
            errors="coerce",
        )
        load_ok = (
            load.notna().all()
            and (load > 0).all()
        )

        valid = bool(status_ok and load_ok)
        self._valid_day_cache[day_start] = valid

        if valid:
            self._day_load_cache[day_start] = (
                load.to_numpy(dtype="float64")
            )

        return valid

    def day_load(
        self,
        day_start: pd.Timestamp,
    ) -> np.ndarray:
        day_start = pd.Timestamp(day_start).normalize()

        if not self.has_full_valid_day(day_start):
            raise ValueError(
                f"Day is not fully valid for donor use: {day_start}"
            )

        return self._day_load_cache[day_start].copy()


def gap_hours(
    start_hour: int,
    duration_hours: int,
) -> list[int]:
    hours = list(
        range(
            start_hour,
            start_hour + duration_hours,
        )
    )

    if not hours:
        raise ValueError("Pseudo-gap duration must be positive.")

    if min(hours) < 0 or max(hours) > 23:
        raise ValueError(
            "Current same-day pseudo-gap implementation cannot "
            "cross midnight."
        )

    return hours


def context_hours_for_gap(
    start_hour: int,
    duration_hours: int,
) -> list[int]:
    gap = set(
        gap_hours(
            start_hour,
            duration_hours,
        )
    )
    return [
        hour
        for hour in range(24)
        if hour not in gap
    ]


def candidate_donors_for_target(
    cache: LoadDayCache,
    *,
    target_start: pd.Timestamp,
    start_hour: int,
    duration_hours: int,
    max_window_weeks: int,
) -> pd.DataFrame:
    target_day = target_start.normalize()
    target_load = cache.day_load(target_day)

    gap_idx = gap_hours(
        start_hour,
        duration_hours,
    )
    context_idx = context_hours_for_gap(
        start_hour,
        duration_hours,
    )

    target_context = target_load[context_idx]

    rows: list[dict[str, object]] = []

    for week_offset in range(
        -max_window_weeks,
        max_window_weeks + 1,
    ):
        if week_offset == 0:
            continue

        donor_start = (
            target_start
            + pd.Timedelta(weeks=week_offset)
        )
        donor_day = donor_start.normalize()

        if not cache.has_full_valid_day(donor_day):
            continue

        donor_load = cache.day_load(donor_day)
        donor_context = donor_load[context_idx]

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
                "gap_values_kw": donor_load[gap_idx],
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "week_offset",
                "donor_start",
                "donor_day",
                "context_rmse_kw",
                "gap_values_kw",
            ]
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
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
        )
        .reset_index(drop=True)
    )


def aggregate_prediction(
    donor_blocks: np.ndarray,
    aggregation: str,
) -> np.ndarray:
    if aggregation == "median":
        return np.median(
            donor_blocks,
            axis=0,
        )

    if aggregation == "mean":
        return np.mean(
            donor_blocks,
            axis=0,
        )

    raise ValueError(
        f"Unknown aggregation: {aggregation}"
    )


def build_pseudogap_targets(
    df: pd.DataFrame,
    templates: pd.DataFrame,
    cache: LoadDayCache,
) -> pd.DataFrame:
    min_window = min(WINDOW_WEEKS)
    max_k = max(K_VALUES)

    timestamp_set = set(df["timestamp"].tolist())
    rows: list[dict[str, object]] = []

    for template in templates.itertuples(index=False):
        start_hour = int(template.start_hour)
        duration = int(template.duration_hours)
        weekday = int(template.weekday)

        # Loop over calendar days in the formal year.
        days = pd.date_range(
            FORMAL_START.normalize(),
            (FORMAL_END_EXCLUSIVE - pd.Timedelta(days=1)).normalize(),
            freq="D",
        )

        for day_start in days:
            if int(day_start.weekday()) != weekday:
                continue

            target_start = (
                day_start
                + pd.Timedelta(hours=start_hour)
            )

            if target_start not in timestamp_set:
                continue

            if not cache.has_full_valid_day(day_start):
                continue

            donors = candidate_donors_for_target(
                cache,
                target_start=target_start,
                start_hour=start_hour,
                duration_hours=duration,
                max_window_weeks=min_window,
            )

            if len(donors) < max_k:
                # Common evaluation-set rule:
                # every retained pseudo-gap must be evaluable for every
                # tested K even at the narrowest tested window.
                continue

            rows.append(
                {
                    "template_id": template.template_id,
                    "target_start": target_start,
                    "target_day": day_start,
                    "weekday": weekday,
                    "start_hour": start_hour,
                    "duration_hours": duration,
                    "min_window_candidate_count": len(donors),
                }
            )

    targets = pd.DataFrame(rows)

    if targets.empty:
        raise ValueError(
            "No pseudo-gap targets satisfy the common evaluation-set rule."
        )

    targets = (
        targets.sort_values(
            [
                "template_id",
                "target_start",
            ]
        )
        .reset_index(drop=True)
    )

    targets.insert(
        0,
        "pseudo_event_id",
        [
            f"P{index:04d}"
            for index in range(1, len(targets) + 1)
        ],
    )

    return targets


def metric_row(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    error = predicted - actual

    actual_energy = float(actual.sum())
    predicted_energy = float(predicted.sum())
    energy_bias = predicted_energy - actual_energy

    return {
        "n_hours": int(len(actual)),
        "abs_error_sum": float(
            np.abs(error).sum()
        ),
        "squared_error_sum": float(
            np.square(error).sum()
        ),
        "error_sum": float(error.sum()),
        "event_mae_kw": float(
            np.mean(np.abs(error))
        ),
        "event_rmse_kw": float(
            np.sqrt(np.mean(np.square(error)))
        ),
        "event_signed_bias_kw": float(
            np.mean(error)
        ),
        "actual_energy_kwh": actual_energy,
        "predicted_energy_kwh": predicted_energy,
        "event_energy_bias_kwh": energy_bias,
        "event_abs_energy_bias_kwh": abs(energy_bias),
        "event_energy_bias_pct": (
            energy_bias / actual_energy * 100.0
            if actual_energy > 0
            else np.nan
        ),
        "event_abs_energy_bias_pct": (
            abs(energy_bias) / actual_energy * 100.0
            if actual_energy > 0
            else np.nan
        ),
    }


def aggregate_metrics(
    event_metrics: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    group_columns = [
        "aggregation",
        "window_weeks",
        "k",
    ]

    for keys, group in event_metrics.groupby(
        group_columns,
        sort=False,
    ):
        aggregation, window_weeks, k = keys

        total_hours = int(group["n_hours"].sum())
        total_actual_energy = float(
            group["actual_energy_kwh"].sum()
        )
        total_predicted_energy = float(
            group["predicted_energy_kwh"].sum()
        )

        signed_energy_bias_pct = (
            (
                total_predicted_energy
                - total_actual_energy
            )
            / total_actual_energy
            * 100.0
            if total_actual_energy > 0
            else np.nan
        )

        rows.append(
            {
                "aggregation": aggregation,
                "window_weeks": int(window_weeks),
                "k": int(k),
                "n_events": int(len(group)),
                "n_templates": int(
                    group["template_id"].nunique()
                ),
                "n_hours": total_hours,
                "mae_kw": float(
                    group["abs_error_sum"].sum()
                    / total_hours
                ),
                "rmse_kw": float(
                    np.sqrt(
                        group["squared_error_sum"].sum()
                        / total_hours
                    )
                ),
                "signed_bias_kw": float(
                    group["error_sum"].sum()
                    / total_hours
                ),
                "signed_energy_bias_pct": signed_energy_bias_pct,
                "mean_event_abs_energy_bias_kwh": float(
                    group[
                        "event_abs_energy_bias_kwh"
                    ].mean()
                ),
                "mean_event_abs_energy_bias_pct": float(
                    group[
                        "event_abs_energy_bias_pct"
                    ].mean()
                ),
                "median_event_abs_energy_bias_pct": float(
                    group[
                        "event_abs_energy_bias_pct"
                    ].median()
                ),
                "is_v7_candidate": bool(
                    int(window_weeks)
                    == V7_CANDIDATE_WINDOW_WEEKS
                    and int(k)
                    == V7_CANDIDATE_K
                ),
            }
        )

    ranking = pd.DataFrame(rows)

    # Diagnostic ranks only. They are not a literature-derived
    # decision rule and do not automatically lock production settings.
    ranking["rank_rmse"] = ranking["rmse_kw"].rank(
        method="min",
        ascending=True,
    )
    ranking["rank_mae"] = ranking["mae_kw"].rank(
        method="min",
        ascending=True,
    )
    ranking[
        "rank_event_abs_energy_bias"
    ] = ranking[
        "mean_event_abs_energy_bias_kwh"
    ].rank(
        method="min",
        ascending=True,
    )
    ranking[
        "rank_abs_signed_energy_bias"
    ] = ranking[
        "signed_energy_bias_pct"
    ].abs().rank(
        method="min",
        ascending=True,
    )

    ranking["diagnostic_mean_rank"] = (
        ranking[
            [
                "rank_rmse",
                "rank_mae",
                "rank_event_abs_energy_bias",
                "rank_abs_signed_energy_bias",
            ]
        ]
        .mean(axis=1)
    )

    return (
        ranking.sort_values(
            [
                "diagnostic_mean_rank",
                "rmse_kw",
                "mae_kw",
                "mean_event_abs_energy_bias_kwh",
            ],
            ascending=True,
        )
        .reset_index(drop=True)
    )


def build_legacy_benchmark(
    targets: pd.DataFrame,
    cache: LoadDayCache,
) -> pd.DataFrame:
    """
    Optional regression benchmark that mirrors the old pre-v7 idea:
    same weekday ±4 weeks, use all valid same-hour donors and take the
    hour-by-hour median. It is NOT included in the v7 hyperparameter ranking.
    """
    rows: list[dict[str, object]] = []

    for event in targets.itertuples(index=False):
        target_load = cache.day_load(
            pd.Timestamp(event.target_day)
        )
        gap_idx = gap_hours(
            int(event.start_hour),
            int(event.duration_hours),
        )
        actual = target_load[gap_idx]

        donor_rows = candidate_donors_for_target(
            cache,
            target_start=pd.Timestamp(event.target_start),
            start_hour=int(event.start_hour),
            duration_hours=int(event.duration_hours),
            max_window_weeks=4,
        )

        if donor_rows.empty:
            continue

        blocks = np.vstack(
            donor_rows["gap_values_kw"].tolist()
        )
        prediction = np.median(
            blocks,
            axis=0,
        )

        metrics = metric_row(
            actual,
            prediction,
        )

        row: dict[str, object] = {
            "pseudo_event_id": event.pseudo_event_id,
            "template_id": event.template_id,
            "target_start": event.target_start,
            "duration_hours": event.duration_hours,
            "candidate_count": len(donor_rows),
        }
        row.update(metrics)
        rows.append(row)

    return pd.DataFrame(rows)


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        args.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        raw, input_path = read_input(
            args.input_parquet,
            args.input_csv,
        )

        data = prepare_input(raw)
        validate_timeline(data)

        outage_events = identify_outage_events(data)
        templates = build_unique_templates(outage_events)

        cache = LoadDayCache(data)

        targets = build_pseudogap_targets(
            data,
            templates,
            cache,
        )

        event_rows: list[dict[str, object]] = []
        donor_rows_all: list[dict[str, object]] = []

        max_window = max(WINDOW_WEEKS)

        for event in targets.itertuples(index=False):
            target_day = pd.Timestamp(event.target_day)
            target_start = pd.Timestamp(event.target_start)

            target_load = cache.day_load(
                target_day
            )

            gap_idx = gap_hours(
                int(event.start_hour),
                int(event.duration_hours),
            )
            actual = target_load[gap_idx]

            donors_all = candidate_donors_for_target(
                cache,
                target_start=target_start,
                start_hour=int(event.start_hour),
                duration_hours=int(event.duration_hours),
                max_window_weeks=max_window,
            )

            for window_weeks in WINDOW_WEEKS:
                donors_window = donors_all.loc[
                    donors_all["week_offset"]
                    .abs()
                    .le(window_weeks)
                ].copy()

                for k in K_VALUES:
                    if len(donors_window) < k:
                        raise RuntimeError(
                            "Common evaluation-set invariant failed: "
                            f"{event.pseudo_event_id}, "
                            f"window={window_weeks}, k={k}, "
                            f"candidates={len(donors_window)}."
                        )

                    selected = (
                        donors_window
                        .sort_values(
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
                        )
                        .head(k)
                        .copy()
                    )

                    blocks = np.vstack(
                        selected[
                            "gap_values_kw"
                        ].tolist()
                    )

                    for aggregation in AGGREGATIONS:
                        prediction = aggregate_prediction(
                            blocks,
                            aggregation,
                        )

                        metrics = metric_row(
                            actual,
                            prediction,
                        )

                        event_row: dict[str, object] = {
                            "pseudo_event_id": event.pseudo_event_id,
                            "template_id": event.template_id,
                            "target_start": target_start,
                            "weekday": int(event.weekday),
                            "start_hour": int(event.start_hour),
                            "duration_hours": int(
                                event.duration_hours
                            ),
                            "aggregation": aggregation,
                            "window_weeks": window_weeks,
                            "k": k,
                            "candidate_count": len(
                                donors_window
                            ),
                            "selected_mean_context_rmse_kw": float(
                                selected[
                                    "context_rmse_kw"
                                ].mean()
                            ),
                            "selected_max_context_rmse_kw": float(
                                selected[
                                    "context_rmse_kw"
                                ].max()
                            ),
                            "is_v7_candidate": bool(
                                window_weeks
                                == V7_CANDIDATE_WINDOW_WEEKS
                                and k
                                == V7_CANDIDATE_K
                            ),
                        }
                        event_row.update(metrics)
                        event_rows.append(event_row)

                    # Selected donors do not depend on mean vs median,
                    # so store them once per window/K.
                    for donor_rank, donor in enumerate(
                        selected.itertuples(index=False),
                        start=1,
                    ):
                        donor_rows_all.append(
                            {
                                "pseudo_event_id":
                                    event.pseudo_event_id,
                                "template_id":
                                    event.template_id,
                                "target_start":
                                    target_start,
                                "duration_hours":
                                    int(event.duration_hours),
                                "window_weeks":
                                    window_weeks,
                                "k":
                                    k,
                                "donor_rank":
                                    donor_rank,
                                "donor_start":
                                    donor.donor_start,
                                "week_offset":
                                    int(donor.week_offset),
                                "context_rmse_kw":
                                    float(
                                        donor.context_rmse_kw
                                    ),
                                "is_v7_candidate":
                                    bool(
                                        window_weeks
                                        == V7_CANDIDATE_WINDOW_WEEKS
                                        and k
                                        == V7_CANDIDATE_K
                                    ),
                            }
                        )

        event_metrics = pd.DataFrame(event_rows)
        selected_donors = pd.DataFrame(donor_rows_all)
        ranking = aggregate_metrics(event_metrics)
        legacy = build_legacy_benchmark(
            targets,
            cache,
        )

        outage_path = (
            args.output_dir
            / "load_observed_outage_events_v7.csv"
        )
        template_path = (
            args.output_dir
            / "load_pseudogap_templates_v7.csv"
        )
        target_path = (
            args.output_dir
            / "load_pseudogap_targets_v7.csv"
        )
        event_metrics_path = (
            args.output_dir
            / "load_pseudogap_event_metrics_v7.csv"
        )
        ranking_path = (
            args.output_dir
            / "load_pseudogap_validation_ranking_v7.csv"
        )
        donors_path = (
            args.output_dir
            / "load_pseudogap_selected_donors_v7.csv"
        )
        legacy_path = (
            args.output_dir
            / "load_pseudogap_legacy_pm4_median_benchmark_v7.csv"
        )
        summary_path = (
            args.output_dir
            / "load_pseudogap_validation_summary_v7.txt"
        )

        outage_events.to_csv(
            outage_path,
            index=False,
            encoding="utf-8-sig",
        )
        templates.to_csv(
            template_path,
            index=False,
            encoding="utf-8-sig",
        )
        targets.to_csv(
            target_path,
            index=False,
            encoding="utf-8-sig",
        )
        event_metrics.to_csv(
            event_metrics_path,
            index=False,
            encoding="utf-8-sig",
        )
        ranking.to_csv(
            ranking_path,
            index=False,
            encoding="utf-8-sig",
        )
        selected_donors.to_csv(
            donors_path,
            index=False,
            encoding="utf-8-sig",
        )
        legacy.to_csv(
            legacy_path,
            index=False,
            encoding="utf-8-sig",
        )

        target_counts = (
            targets.groupby(
                [
                    "template_id",
                    "weekday",
                    "start_hour",
                    "duration_hours",
                ],
                as_index=False,
            )
            .agg(
                pseudo_events=(
                    "pseudo_event_id",
                    "count",
                )
            )
        )

        v7_rows = ranking.loc[
            ranking["is_v7_candidate"]
        ].copy()

        summary_lines = [
            "NTUST v7 Load Pseudo-Gap Validation",
            f"Script version: {SCRIPT_VERSION}",
            f"Input: {input_path}",
            "",
            "Purpose",
            "- Validate Load donor-reconstruction settings before production use.",
            "- The real outage-contaminated Load values are NOT reconstructed here.",
            "- ±8 weeks / K=3 is evaluated as a candidate, not hard-coded as the winner.",
            "",
            "Observed outage templates",
            outage_events.to_string(index=False),
            "",
            "Unique pseudo-gap templates",
            templates.to_string(index=False),
            "",
            "Validation design",
            f"- Window grid: {WINDOW_WEEKS}",
            f"- K grid: {K_VALUES}",
            f"- Aggregations: {AGGREGATIONS}",
            "- Candidate donors: same weekday by integer-week offsets.",
            "- Donor/target eligibility: full 24-hour day must be observed, "
            "load_status=normal, and observed_load_kw>0.",
            "- Pseudo-gap shapes copy the observed outage weekday/start-hour/duration.",
            "- Context matching metric: RMSE over all hours of the same calendar day "
            "outside the artificial gap.",
            "- Reconstruction: hour-by-hour aggregation of the top-K donor gap blocks.",
            "- Common evaluation set: every retained pseudo-event must have at least "
            f"K={max(K_VALUES)} donors even at the narrowest ±{min(WINDOW_WEEKS)}-week window.",
            "- No extra statistical anomaly filter is invented because Script 01 does "
            "not contain an explicit anomaly flag; only available provenance flags are used.",
            "",
            "Pseudo-gap target counts",
            target_counts.to_string(index=False),
            f"- Total pseudo-events: {len(targets):,}",
            "",
            "Top 15 configurations by diagnostic mean rank",
            ranking.head(15).to_string(index=False),
            "",
            "v7 candidate rows (±8 weeks / K=3)",
            (
                v7_rows.to_string(index=False)
                if not v7_rows.empty
                else "ERROR: v7 candidate rows not found."
            ),
            "",
            "Interpretation guardrail",
            "- rank_rmse / rank_mae / energy-bias ranks are diagnostics, not a "
            "literature-derived decision rule.",
            "- Do NOT lock ±8/K3 merely because it is the framework candidate.",
            "- Review whether ±8/K3 is competitive/stable across RMSE, MAE, signed "
            "energy bias, and event-level absolute energy bias before Script 03.",
            "- If the empirical ranking materially contradicts ±8/K3, update the "
            "site-specific P1 evidence/framework rather than forcing the result.",
            "",
            "Outputs",
            f"- {outage_path}",
            f"- {template_path}",
            f"- {target_path}",
            f"- {event_metrics_path}",
            f"- {ranking_path}",
            f"- {donors_path}",
            f"- {legacy_path}",
            f"- {summary_path}",
        ]

        summary_path.write_text(
            "\n".join(summary_lines) + "\n",
            encoding="utf-8",
        )

        print("\n".join(summary_lines))
        print()
        print(
            "Script 02 completed. No real outage Load values were changed."
        )
        print(
            "Next step: inspect the ranking and v7-candidate rows before "
            "creating the production reconstruction script."
        )

        return 0

    except Exception as exc:
        print(
            f"Script 02 failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
