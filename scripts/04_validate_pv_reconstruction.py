from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7-pv-pseudogap-validation-2026-08-16"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760

# ±30 days / K=5 is intentionally only one candidate.
WINDOW_DAYS = (7, 14, 21, 30, 45, 60)
K_VALUES = (1, 3, 5, 7)
AGGREGATIONS = ("median", "mean")

V7_CANDIDATE_WINDOW_DAYS = 30
V7_CANDIDATE_K = 5
DAYLIGHT_THRESHOLD_KW = 0.0
MIN_CONTEXT_POINTS = 2


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description=(
            "Validate PV donor-reconstruction hyperparameters using "
            "artificial pseudo-gaps on intact observed PV days. "
            "This script does NOT reconstruct the real outage hours or "
            "the prolonged pre_system/missing_winter intervals."
        )
    )
    parser.add_argument(
        "--input-parquet",
        type=Path,
        default=(root / "data" / "processed" / "ntust_case_year_observed.parquet"),
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=(root / "data" / "processed" / "ntust_case_year_observed.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "results" / "data_audit",
    )
    return parser.parse_args()


def read_input(parquet_path: Path, csv_path: Path) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (ImportError, ModuleNotFoundError, ValueError):
            pass
    if csv_path.exists():
        return pd.read_csv(csv_path), csv_path
    raise FileNotFoundError(
        "Cannot find Script-01 observed dataset:\n"
        f"- {parquet_path}\n- {csv_path}"
    )


def parse_timestamp(series: pd.Series) -> pd.Series:
    result = pd.to_datetime(series, errors="coerce")
    try:
        if result.dt.tz is not None:
            result = result.dt.tz_convert("Asia/Taipei").dt.tz_localize(None)
    except AttributeError:
        pass
    return result


def parse_bool(series: pd.Series, *, fallback: pd.Series | None = None) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    mapped = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
    )
    if fallback is not None:
        mapped = mapped.fillna(fallback)
    if mapped.isna().any():
        raise ValueError(f"Cannot parse {int(mapped.isna().sum())} boolean values.")
    return mapped.astype(bool)


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Script-01 input is missing required columns: {missing}")


def prepare_input(df: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        df,
        [
            "timestamp",
            "observed_pv_kw",
            "pv_status",
            "outage_contaminated_flag",
        ],
    )
    result = df.copy()
    result["timestamp"] = parse_timestamp(result["timestamp"])
    if result["timestamp"].isna().any():
        raise ValueError(f"{int(result['timestamp'].isna().sum())} timestamps cannot be parsed.")
    result = result.loc[
        (result["timestamp"] >= FORMAL_START)
        & (result["timestamp"] < FORMAL_END_EXCLUSIVE)
    ].copy()
    result = result.sort_values("timestamp").reset_index(drop=True)
    result["observed_pv_kw"] = pd.to_numeric(result["observed_pv_kw"], errors="coerce")
    if result["observed_pv_kw"].isna().any():
        raise ValueError(
            f"observed_pv_kw contains {int(result['observed_pv_kw'].isna().sum())} missing values."
        )
    if (result["observed_pv_kw"] < 0).any():
        raise ValueError("observed_pv_kw contains negative values.")
    result["outage_contaminated_flag"] = parse_bool(
        result["outage_contaminated_flag"],
        fallback=pd.Series(False, index=result.index),
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
        raise ValueError(f"Input contains {len(df):,} rows; expected {EXPECTED_HOURS:,}.")
    if df["timestamp"].duplicated().any():
        raise ValueError(f"Input contains {int(df['timestamp'].duplicated().sum())} duplicate timestamps.")
    if not actual.equals(expected):
        missing = expected.difference(actual)
        extra = actual.difference(expected)
        raise ValueError(
            "Input is not the exact v7 case-year timeline: "
            f"missing={len(missing)}, extra={len(extra)}."
        )


def identify_outage_events(df: pd.DataFrame) -> pd.DataFrame:
    outage = df.loc[df["outage_contaminated_flag"], ["timestamp"]].copy()
    if outage.empty:
        raise ValueError("No outage-contaminated intervals were found.")
    outage = outage.sort_values("timestamp").reset_index(drop=True)
    new_group = outage["timestamp"].diff().ne(pd.Timedelta(hours=1))
    outage["_group"] = new_group.cumsum()
    rows = []
    for event_id, (_, group) in enumerate(outage.groupby("_group", sort=False), start=1):
        start = group["timestamp"].iloc[0]
        end = group["timestamp"].iloc[-1]
        duration = len(group)
        if start.normalize() != end.normalize():
            raise ValueError(
                "Current PV pseudo-gap validation assumes same-day outage blocks, "
                f"but an observed event crosses midnight: {start} to {end}."
            )
        rows.append(
            {
                "source_event_id": event_id,
                "source_start": start,
                "source_end_inclusive": end,
                "duration_hours": duration,
                "start_hour": int(start.hour),
            }
        )
    return pd.DataFrame(rows)


def build_unique_templates(outage_events: pd.DataFrame) -> pd.DataFrame:
    templates = (
        outage_events[["start_hour", "duration_hours"]]
        .drop_duplicates()
        .sort_values(["start_hour", "duration_hours"])
        .reset_index(drop=True)
    )
    templates.insert(
        0,
        "template_id",
        [f"T{idx:02d}" for idx in range(1, len(templates) + 1)],
    )
    return templates


class PVDayCache:
    def __init__(self, df: pd.DataFrame):
        self.indexed = df.set_index("timestamp", drop=False)
        self._valid_cache: dict[pd.Timestamp, bool] = {}
        self._pv_cache: dict[pd.Timestamp, np.ndarray] = {}

    def has_full_valid_day(self, day_start: pd.Timestamp) -> bool:
        day_start = pd.Timestamp(day_start).normalize()
        if day_start in self._valid_cache:
            return self._valid_cache[day_start]
        timestamps = pd.date_range(day_start, periods=24, freq="h")
        if not timestamps.isin(self.indexed.index).all():
            self._valid_cache[day_start] = False
            return False
        day = self.indexed.loc[timestamps]
        pv = pd.to_numeric(day["observed_pv_kw"], errors="coerce")
        valid = bool(
            day["pv_status"].astype(str).eq("valid").all()
            and (~day["outage_contaminated_flag"].astype(bool)).all()
            and pv.notna().all()
            and (pv >= 0).all()
        )
        self._valid_cache[day_start] = valid
        if valid:
            self._pv_cache[day_start] = pv.to_numpy(dtype="float64")
        return valid

    def day_pv(self, day_start: pd.Timestamp) -> np.ndarray:
        day_start = pd.Timestamp(day_start).normalize()
        if not self.has_full_valid_day(day_start):
            raise ValueError(f"Day is not fully valid for PV donor use: {day_start}")
        return self._pv_cache[day_start].copy()


def gap_hours(start_hour: int, duration_hours: int) -> list[int]:
    hours = list(range(start_hour, start_hour + duration_hours))
    if not hours or min(hours) < 0 or max(hours) > 23:
        raise ValueError("Pseudo-gap cannot cross midnight in the current implementation.")
    return hours


def candidate_donors_for_target(
    cache: PVDayCache,
    *,
    target_day: pd.Timestamp,
    start_hour: int,
    duration_hours: int,
    max_window_days: int,
) -> pd.DataFrame:
    target_day = pd.Timestamp(target_day).normalize()
    target_pv = cache.day_pv(target_day)
    gap_idx = gap_hours(start_hour, duration_hours)
    gap_set = set(gap_idx)
    outside_gap = np.array([hour not in gap_set for hour in range(24)], dtype=bool)

    rows: list[dict[str, object]] = []

    for day_offset in range(-max_window_days, max_window_days + 1):
        if day_offset == 0:
            continue
        donor_day = target_day + pd.Timedelta(days=day_offset)
        if not cache.has_full_valid_day(donor_day):
            continue
        donor_pv = cache.day_pv(donor_day)

        # Daylight/context matching: compare only outside-gap hours where
        # either target or donor shows positive PV. This prevents nighttime
        # zeros from dominating the similarity score while preserving both
        # level and shape information in the observed PV context.
        daylight_context = (
            outside_gap
            & (
                (target_pv > DAYLIGHT_THRESHOLD_KW)
                | (donor_pv > DAYLIGHT_THRESHOLD_KW)
            )
        )
        context_points = int(daylight_context.sum())
        if context_points < MIN_CONTEXT_POINTS:
            continue

        diff = donor_pv[daylight_context] - target_pv[daylight_context]
        context_rmse = float(np.sqrt(np.mean(diff**2)))

        rows.append(
            {
                "day_offset": day_offset,
                "donor_day": donor_day,
                "context_points": context_points,
                "context_rmse_kw": context_rmse,
                "gap_values_kw": donor_pv[gap_idx],
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "day_offset",
                "donor_day",
                "context_points",
                "context_rmse_kw",
                "gap_values_kw",
            ]
        )

    donors = pd.DataFrame(rows)
    donors = donors.sort_values(
        ["context_rmse_kw", "day_offset", "donor_day"],
        key=lambda s: s.abs() if s.name == "day_offset" else s,
    ).reset_index(drop=True)
    return donors


def build_pseudogap_targets(
    df: pd.DataFrame,
    templates: pd.DataFrame,
    cache: PVDayCache,
) -> pd.DataFrame:
    min_window = min(WINDOW_DAYS)
    max_k = max(K_VALUES)
    days = pd.date_range(
        FORMAL_START.normalize(),
        (FORMAL_END_EXCLUSIVE - pd.Timedelta(days=1)).normalize(),
        freq="D",
    )
    rows: list[dict[str, object]] = []

    for template in templates.itertuples(index=False):
        for day in days:
            if not cache.has_full_valid_day(day):
                continue
            donors = candidate_donors_for_target(
                cache,
                target_day=day,
                start_hour=int(template.start_hour),
                duration_hours=int(template.duration_hours),
                max_window_days=min_window,
            )
            if len(donors) < max_k:
                continue
            actual = cache.day_pv(day)[
                gap_hours(int(template.start_hour), int(template.duration_hours))
            ]
            rows.append(
                {
                    "template_id": template.template_id,
                    "target_day": day,
                    "target_start": day + pd.Timedelta(hours=int(template.start_hour)),
                    "start_hour": int(template.start_hour),
                    "duration_hours": int(template.duration_hours),
                    "actual_gap_energy_kwh": float(actual.sum()),
                    "min_window_candidate_count": int(len(donors)),
                }
            )

    targets = pd.DataFrame(rows)
    if targets.empty:
        raise ValueError("No PV pseudo-gap targets satisfy the common evaluation-set rule.")
    targets = targets.sort_values(["template_id", "target_start"]).reset_index(drop=True)
    targets.insert(
        0,
        "pseudo_event_id",
        [f"P{idx:04d}" for idx in range(1, len(targets) + 1)],
    )
    return targets


def aggregate_prediction(donor_blocks: np.ndarray, aggregation: str) -> np.ndarray:
    if aggregation == "median":
        return np.median(donor_blocks, axis=0)
    if aggregation == "mean":
        return np.mean(donor_blocks, axis=0)
    raise ValueError(f"Unknown aggregation: {aggregation}")


def metric_row(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    error = predicted - actual
    actual_energy = float(actual.sum())
    predicted_energy = float(predicted.sum())
    energy_bias = predicted_energy - actual_energy
    return {
        "n_hours": int(len(actual)),
        "abs_error_sum": float(np.abs(error).sum()),
        "squared_error_sum": float(np.square(error).sum()),
        "error_sum": float(error.sum()),
        "event_mae_kw": float(np.mean(np.abs(error))),
        "event_rmse_kw": float(np.sqrt(np.mean(np.square(error)))),
        "event_signed_bias_kw": float(np.mean(error)),
        "actual_energy_kwh": actual_energy,
        "predicted_energy_kwh": predicted_energy,
        "event_energy_bias_kwh": energy_bias,
        "event_abs_energy_bias_kwh": abs(energy_bias),
        "event_energy_bias_pct": (
            energy_bias / actual_energy * 100.0 if actual_energy > 0 else np.nan
        ),
    }


def aggregate_metrics(event_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in event_metrics.groupby(
        ["aggregation", "window_days", "k"], sort=False
    ):
        aggregation, window_days, k = keys
        total_hours = int(group["n_hours"].sum())
        total_actual = float(group["actual_energy_kwh"].sum())
        total_pred = float(group["predicted_energy_kwh"].sum())
        signed_energy_bias_pct = (
            (total_pred - total_actual) / total_actual * 100.0
            if total_actual > 0
            else np.nan
        )
        rows.append(
            {
                "aggregation": aggregation,
                "window_days": int(window_days),
                "k": int(k),
                "n_events": int(len(group)),
                "n_templates": int(group["template_id"].nunique()),
                "n_hours": total_hours,
                "mae_kw": float(group["abs_error_sum"].sum() / total_hours),
                "rmse_kw": float(
                    np.sqrt(group["squared_error_sum"].sum() / total_hours)
                ),
                "signed_bias_kw": float(group["error_sum"].sum() / total_hours),
                "signed_energy_bias_pct": signed_energy_bias_pct,
                "mean_event_abs_energy_bias_kwh": float(
                    group["event_abs_energy_bias_kwh"].mean()
                ),
                "median_event_abs_energy_bias_kwh": float(
                    group["event_abs_energy_bias_kwh"].median()
                ),
                "is_v7_candidate": bool(
                    int(window_days) == V7_CANDIDATE_WINDOW_DAYS
                    and int(k) == V7_CANDIDATE_K
                ),
            }
        )

    ranking = pd.DataFrame(rows)
    ranking["rank_rmse"] = ranking["rmse_kw"].rank(method="min", ascending=True)
    ranking["rank_mae"] = ranking["mae_kw"].rank(method="min", ascending=True)
    ranking["rank_event_abs_energy_bias"] = ranking[
        "mean_event_abs_energy_bias_kwh"
    ].rank(method="min", ascending=True)
    ranking["rank_abs_signed_energy_bias"] = ranking[
        "signed_energy_bias_pct"
    ].abs().rank(method="min", ascending=True)
    ranking["diagnostic_mean_rank"] = ranking[
        [
            "rank_rmse",
            "rank_mae",
            "rank_event_abs_energy_bias",
            "rank_abs_signed_energy_bias",
        ]
    ].mean(axis=1)

    return ranking.sort_values(
        [
            "diagnostic_mean_rank",
            "rmse_kw",
            "mae_kw",
            "mean_event_abs_energy_bias_kwh",
        ],
        ascending=True,
    ).reset_index(drop=True)


def build_linear_interpolation_benchmark(
    targets: pd.DataFrame,
    cache: PVDayCache,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for event in targets.itertuples(index=False):
        day = pd.Timestamp(event.target_day)
        pv = cache.day_pv(day)
        start = int(event.start_hour)
        duration = int(event.duration_hours)
        gap_idx = gap_hours(start, duration)
        before_hour = start - 1
        after_hour = start + duration
        if before_hour < 0 or after_hour > 23:
            continue
        actual = pv[gap_idx]
        left = float(pv[before_hour])
        right = float(pv[after_hour])
        predicted = np.linspace(left, right, duration + 2)[1:-1]
        predicted = np.maximum(predicted, 0.0)
        metrics = metric_row(actual, predicted)
        row = {
            "pseudo_event_id": event.pseudo_event_id,
            "template_id": event.template_id,
            "target_start": event.target_start,
            "duration_hours": duration,
            "before_pv_kw": left,
            "after_pv_kw": right,
        }
        row.update(metrics)
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        raw, input_path = read_input(args.input_parquet, args.input_csv)
        data = prepare_input(raw)
        validate_timeline(data)

        outage_events = identify_outage_events(data)
        templates = build_unique_templates(outage_events)
        cache = PVDayCache(data)
        targets = build_pseudogap_targets(data, templates, cache)

        event_rows: list[dict[str, object]] = []
        donor_rows: list[dict[str, object]] = []
        max_window = max(WINDOW_DAYS)

        for event in targets.itertuples(index=False):
            day = pd.Timestamp(event.target_day)
            start = int(event.start_hour)
            duration = int(event.duration_hours)
            actual = cache.day_pv(day)[gap_hours(start, duration)]
            donors_all = candidate_donors_for_target(
                cache,
                target_day=day,
                start_hour=start,
                duration_hours=duration,
                max_window_days=max_window,
            )

            for window_days in WINDOW_DAYS:
                donors_window = donors_all.loc[
                    donors_all["day_offset"].abs().le(window_days)
                ].copy()
                for k in K_VALUES:
                    if len(donors_window) < k:
                        raise RuntimeError(
                            "Common evaluation-set invariant failed: "
                            f"{event.pseudo_event_id}, window={window_days}, "
                            f"k={k}, candidates={len(donors_window)}."
                        )
                    selected = donors_window.head(k).copy()
                    blocks = np.vstack(selected["gap_values_kw"].tolist())

                    for aggregation in AGGREGATIONS:
                        predicted = aggregate_prediction(blocks, aggregation)
                        metrics = metric_row(actual, predicted)
                        row: dict[str, object] = {
                            "pseudo_event_id": event.pseudo_event_id,
                            "template_id": event.template_id,
                            "target_start": event.target_start,
                            "start_hour": start,
                            "duration_hours": duration,
                            "aggregation": aggregation,
                            "window_days": window_days,
                            "k": k,
                            "candidate_count": int(len(donors_window)),
                            "selected_mean_context_rmse_kw": float(
                                selected["context_rmse_kw"].mean()
                            ),
                            "selected_min_context_points": int(
                                selected["context_points"].min()
                            ),
                            "is_v7_candidate": bool(
                                window_days == V7_CANDIDATE_WINDOW_DAYS
                                and k == V7_CANDIDATE_K
                            ),
                        }
                        row.update(metrics)
                        event_rows.append(row)

                    for donor_rank, donor in enumerate(
                        selected.itertuples(index=False), start=1
                    ):
                        donor_rows.append(
                            {
                                "pseudo_event_id": event.pseudo_event_id,
                                "template_id": event.template_id,
                                "target_start": event.target_start,
                                "duration_hours": duration,
                                "window_days": window_days,
                                "k": k,
                                "donor_rank": donor_rank,
                                "donor_day": donor.donor_day,
                                "day_offset": int(donor.day_offset),
                                "context_points": int(donor.context_points),
                                "context_rmse_kw": float(donor.context_rmse_kw),
                                "is_v7_candidate": bool(
                                    window_days == V7_CANDIDATE_WINDOW_DAYS
                                    and k == V7_CANDIDATE_K
                                ),
                            }
                        )

        event_metrics = pd.DataFrame(event_rows)
        selected_donors = pd.DataFrame(donor_rows)
        ranking = aggregate_metrics(event_metrics)
        linear = build_linear_interpolation_benchmark(targets, cache)

        outage_path = args.output_dir / "pv_observed_outage_events_v7.csv"
        template_path = args.output_dir / "pv_pseudogap_templates_v7.csv"
        target_path = args.output_dir / "pv_pseudogap_targets_v7.csv"
        event_path = args.output_dir / "pv_pseudogap_event_metrics_v7.csv"
        ranking_path = args.output_dir / "pv_pseudogap_validation_ranking_v7.csv"
        donors_path = args.output_dir / "pv_pseudogap_selected_donors_v7.csv"
        linear_path = args.output_dir / "pv_pseudogap_linear_interpolation_benchmark_v7.csv"
        summary_path = args.output_dir / "pv_pseudogap_validation_summary_v7.txt"

        outage_events.to_csv(outage_path, index=False, encoding="utf-8-sig")
        templates.to_csv(template_path, index=False, encoding="utf-8-sig")
        targets.to_csv(target_path, index=False, encoding="utf-8-sig")
        event_metrics.to_csv(event_path, index=False, encoding="utf-8-sig")
        ranking.to_csv(ranking_path, index=False, encoding="utf-8-sig")
        selected_donors.to_csv(donors_path, index=False, encoding="utf-8-sig")
        linear.to_csv(linear_path, index=False, encoding="utf-8-sig")

        target_counts = (
            targets.groupby(["template_id", "start_hour", "duration_hours"], as_index=False)
            .agg(pseudo_events=("pseudo_event_id", "count"))
        )
        v7_rows = ranking.loc[ranking["is_v7_candidate"]].copy()

        if not linear.empty:
            total_hours = int(linear["n_hours"].sum())
            linear_mae = float(linear["abs_error_sum"].sum() / total_hours)
            linear_rmse = float(np.sqrt(linear["squared_error_sum"].sum() / total_hours))
            linear_actual = float(linear["actual_energy_kwh"].sum())
            linear_pred = float(linear["predicted_energy_kwh"].sum())
            linear_bias_pct = (
                (linear_pred - linear_actual) / linear_actual * 100.0
                if linear_actual > 0 else np.nan
            )
            linear_abs_event = float(linear["event_abs_energy_bias_kwh"].mean())
            linear_summary = (
                f"- Linear interpolation benchmark: MAE={linear_mae:.6f} kW, "
                f"RMSE={linear_rmse:.6f} kW, signed energy bias={linear_bias_pct:.6f} %, "
                f"mean event absolute energy bias={linear_abs_event:.6f} kWh"
            )
        else:
            linear_summary = "- Linear interpolation benchmark: unavailable"

        summary_lines = [
            "NTUST v7 PV Pseudo-Gap Validation",
            f"Script version: {SCRIPT_VERSION}",
            f"Input: {input_path}",
            "",
            "Purpose",
            "- Validate short-gap PV donor settings before production use.",
            "- The real 10 outage-contaminated PV hours are NOT reconstructed here.",
            "- pre_system/missing_winter intervals are NOT reconstructed here.",
            "- ±30 days / K=5 is evaluated as a candidate, not hard-coded as the winner.",
            "",
            "Observed outage templates",
            outage_events.to_string(index=False),
            "",
            "Unique pseudo-gap templates",
            templates.to_string(index=False),
            "",
            "Validation design",
            f"- Window grid: {WINDOW_DAYS} days",
            f"- K grid: {K_VALUES}",
            f"- Aggregations: {AGGREGATIONS}",
            "- Candidate donors: calendar days within ±window; NO weekday restriction.",
            "- Eligible target/donor day: all 24 h pv_status=valid, no outage contamination, no missing/negative observed PV.",
            "- Pseudo-gap shapes copy the observed outage start hour and duration.",
            "- Context matching: raw PV RMSE outside the artificial gap, using daylight-relevant hours where target or donor PV > 0.",
            "- Reconstruction: hour-by-hour aggregation of top-K donor gap blocks.",
            f"- Common evaluation set: at least K={max(K_VALUES)} donors even at ±{min(WINDOW_DAYS)} days.",
            "- Long unavailable winter PV is deliberately excluded from donor validation.",
            "- No extra anomaly filter is invented because Script 01 has no explicit PV anomaly flag.",
            "",
            "Pseudo-gap target counts",
            target_counts.to_string(index=False),
            f"- Total pseudo-events: {len(targets):,}",
            "",
            "Top 15 donor configurations by diagnostic mean rank",
            ranking.head(15).to_string(index=False),
            "",
            "v7 candidate rows (±30 days / K=5)",
            v7_rows.to_string(index=False) if not v7_rows.empty else "ERROR: candidate rows not found.",
            "",
            "Non-donor benchmark",
            linear_summary,
            "",
            "Interpretation guardrail",
            "- The four ranks are diagnostics, not a literature-derived universal selection rule.",
            "- Do NOT lock ±30/K5 merely because it is the framework candidate.",
            "- Review competitiveness/stability across RMSE, MAE, signed energy bias, and event-level absolute energy bias before production reconstruction.",
            "- If the empirical evidence materially contradicts ±30/K5, update P1/framework rather than forcing the old setting.",
            "",
            "Outputs",
            f"- {outage_path}",
            f"- {template_path}",
            f"- {target_path}",
            f"- {event_path}",
            f"- {ranking_path}",
            f"- {donors_path}",
            f"- {linear_path}",
            f"- {summary_path}",
        ]
        summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
        print("\n".join(summary_lines))
        print()
        print("Script 04 completed. No real PV values were changed.")
        print("Next step: inspect the ranking and ±30/K5 candidate rows before production PV reconstruction.")
        return 0

    except Exception as exc:
        print(f"Script 04 failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
