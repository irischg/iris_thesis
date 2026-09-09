from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from types import ModuleType
from typing import Any
import uuid

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-winter-pv-longblock-holdout-validation-2026-09-09-r2"
EXPECTED_PROTOCOL_SHA256 = (
    "630c9c20a388fde31d424d8b1e43d99cd05c5d2c9cf51b17e2d36f90fb50f525"
)
EXPECTED_CWA_REFERENCE_VERSION = (
    "v7-pv-cwa-headtohead-validation-r3-2026-08-16"
)

BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_907
PERCENTILES = (2.5, 97.5)

HOLDOUTS: tuple[dict[str, Any], ...] = (
    {
        "holdout": "H1",
        "start": "2025-01-01 00:00:00",
        "end_exclusive": "2025-02-01 00:00:00",
        "expected_timestamps": 744,
        "expected_complete_days": 31,
        "expected_partial_hours": 0,
        "role": "January full-month observed winter proxy",
    },
    {
        "holdout": "H2",
        "start": "2025-02-01 00:00:00",
        "end_exclusive": "2025-03-01 00:00:00",
        "expected_timestamps": 672,
        "expected_complete_days": 28,
        "expected_partial_hours": 0,
        "role": "February full-month observed winter proxy",
    },
    {
        "holdout": "H3",
        "start": "2025-01-01 00:00:00",
        "end_exclusive": "2025-03-02 23:00:00",
        "expected_timestamps": 1463,
        "expected_complete_days": 60,
        "expected_partial_hours": 23,
        "role": "Primary exact-length contiguous long-block holdout",
    },
)

METHOD_CWA = "cwa_hourly_ghi_ratio_median"
METHOD_CLIMATOLOGY = "training_only_hod_mean_pv_climatology"
METHODS = (METHOD_CWA, METHOD_CLIMATOLOGY)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description=(
            "Execute only the frozen Winter-PV H1/H2/H3 holdout validation. "
            "This script does not build an alternative annual input or solve a MILP."
        )
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=root / "results" / "data_audit" / "winter_pv_holdouts",
    )
    return parser.parse_args()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def new_run_id(started_utc: datetime) -> str:
    return f"{started_utc.strftime('%Y%m%dT%H%M%S%fZ')}_{uuid.uuid4().hex[:10]}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def write_json(path: Path, payload: dict[str, Any], *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8", newline="\n") as handle:
        json.dump(json_safe(payload), handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")


def write_csv(data: pd.DataFrame, path: Path) -> None:
    data.to_csv(
        path,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        float_format="%.17g",
        date_format="%Y-%m-%d %H:%M:%S",
    )


def git_value(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def stable_frame_sha256(data: pd.DataFrame, columns: list[str]) -> str:
    frame = data.loc[:, columns].copy()
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = frame[column].dt.strftime("%Y-%m-%d %H:%M:%S")
    text = frame.to_csv(
        index=False,
        lineterminator="\n",
        float_format="%.17g",
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_reference_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("winter_pv_cwa_reference", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load CWA reference module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual_version = getattr(module, "SCRIPT_VERSION", None)
    if actual_version != EXPECTED_CWA_REFERENCE_VERSION:
        raise RuntimeError(
            "CWA reference version mismatch: "
            f"expected={EXPECTED_CWA_REFERENCE_VERSION!r}, actual={actual_version!r}."
        )
    return module


def normalize_bool(series: pd.Series, *, label: str) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        if series.isna().any():
            raise ValueError(f"{label} contains missing Boolean values.")
        return series.astype(bool)
    mapped = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
    )
    if mapped.isna().any():
        values = sorted(series.loc[mapped.isna()].astype(str).unique().tolist())
        raise ValueError(f"{label} contains invalid Boolean values: {values[:10]}")
    return mapped.astype(bool)


def load_controlled_data(
    root: Path,
    reference: ModuleType,
) -> tuple[pd.DataFrame, Path, Path]:
    observed_parquet = root / "data" / "processed" / "ntust_case_year_observed.parquet"
    observed_csv = root / "data" / "processed" / "ntust_case_year_observed.csv"
    cwa_path = (
        root
        / "data"
        / "raw"
        / "cwa_codis"
        / "466920"
        / "cwa_466920_formal_8760_ghi_temperature.csv"
    )
    observed_raw, observed_path = reference.read_observed(observed_parquet, observed_csv)
    observed = reference.prepare_observed(observed_raw)
    observed["outage_contaminated_flag"] = normalize_bool(
        observed["outage_contaminated_flag"],
        label="outage_contaminated_flag",
    )
    weather = reference.read_cwa(cwa_path)
    data = observed.merge(
        weather[["timestamp", "ghi_kwh_m2", "air_temperature_c"]],
        on="timestamp",
        how="left",
        validate="one_to_one",
    )
    if data["ghi_kwh_m2"].isna().any():
        raise ValueError(
            f"CWA GHI has {int(data['ghi_kwh_m2'].isna().sum())} missing formal hours."
        )
    return data, Path(observed_path), cwa_path


def validate_holdout_target(
    data: pd.DataFrame,
    definition: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    start = pd.Timestamp(definition["start"])
    end = pd.Timestamp(definition["end_exclusive"])
    expected_count = int(definition["expected_timestamps"])
    expected_index = pd.date_range(start, end, freq="h", inclusive="left")
    target = data.loc[data["timestamp"].ge(start) & data["timestamp"].lt(end)].copy()
    target = target.sort_values("timestamp").reset_index(drop=True)

    gates = {
        "timestamp_count_pass": len(target) == expected_count,
        "unique_timestamp_pass": target["timestamp"].nunique() == expected_count,
        "exact_timeline_pass": pd.DatetimeIndex(target["timestamp"]).equals(expected_index),
        "observed_truth_complete_pass": target["observed_pv_kw"].notna().all(),
        "eligible_target_status_pass": target["pv_status"].astype(str).eq("valid").all(),
        "outage_free_target_pass": (~target["outage_contaminated_flag"]).all(),
        "required_ghi_complete_pass": target["ghi_kwh_m2"].notna().all(),
    }
    gates = {key: bool(value) for key, value in gates.items()}
    if not all(gates.values()):
        failures = [key for key, value in gates.items() if not value]
        raise RuntimeError(
            f"{definition['holdout']} target pre-prediction gate failed: {failures}"
        )
    gates["overall_target_input_gate_pass"] = True
    return target, gates


def eligible_training_rows(
    data: pd.DataFrame,
    definition: dict[str, Any],
) -> pd.DataFrame:
    start = pd.Timestamp(definition["start"])
    end = pd.Timestamp(definition["end_exclusive"])
    target_mask = data["timestamp"].ge(start) & data["timestamp"].lt(end)
    eligible_pv = (
        data["pv_status"].astype(str).eq("valid")
        & (~data["outage_contaminated_flag"])
        & data["observed_pv_kw"].notna()
    )
    train = data.loc[eligible_pv & (~target_mask)].copy()
    if train.empty:
        raise RuntimeError(f"{definition['holdout']} has no eligible training rows.")
    if train["ghi_kwh_m2"].isna().any():
        raise RuntimeError(
            f"{definition['holdout']} cannot use one common training set because GHI is missing."
        )
    train = train.sort_values("timestamp").reset_index(drop=True)
    train["hour"] = train["timestamp"].dt.hour.astype(int)
    return train


def cwa_prediction(
    reference: ModuleType,
    train: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, Any]]:
    fit = train.loc[
        train["ghi_kwh_m2"].gt(float(reference.RATIO_FIT_GHI_THRESHOLD))
    ].copy()
    if fit.empty:
        raise RuntimeError("No eligible CWA ratio-fit rows remain.")
    fit["pv_per_ghi"] = fit["observed_pv_kw"] / fit["ghi_kwh_m2"]
    if not np.isfinite(fit["pv_per_ghi"].to_numpy(dtype=float)).all():
        raise RuntimeError("CWA ratio-fit values are not finite.")

    global_ratio = float(fit["pv_per_ghi"].median())
    ratios_by_hour = fit.groupby("hour")["pv_per_ghi"].median().to_dict()
    fit_counts = fit.groupby("hour").size().reindex(range(24), fill_value=0)

    # Pass only the explanatory target fields consumed by the validated candidate.
    candidate_target = target[["timestamp", "ghi_kwh_m2"]].copy()
    prediction, reference_parameters = reference.predict_hourly_ghi_ratio_median(
        train,
        candidate_target,
    )
    prediction = np.asarray(prediction, dtype="float64")
    pv_cap_kw = float(train["observed_pv_kw"].max())
    if float(reference_parameters["parameter_1"]) != global_ratio:
        raise RuntimeError("CWA global-ratio diagnostic disagrees with the reference function.")
    if float(reference_parameters["pv_cap_kw"]) != pv_cap_kw:
        raise RuntimeError("CWA capacity diagnostic disagrees with the reference function.")

    target_hours = candidate_target["timestamp"].dt.hour
    fallback_mask = ~target_hours.isin(ratios_by_hour)
    daylight_mask = candidate_target["ghi_kwh_m2"].gt(
        float(reference.DAYLIGHT_GHI_THRESHOLD)
    )
    hod_rows = []
    for hour in range(24):
        ratio = ratios_by_hour.get(hour)
        hod_rows.append(
            {
                "hour_of_day": hour,
                "ratio_fit_rows": int(fit_counts.loc[hour]),
                "hourly_pv_per_ghi_ratio_median": (
                    float(ratio) if ratio is not None and math.isfinite(float(ratio)) else np.nan
                ),
            }
        )
    parameters = {
        "eligible_training_rows": int(len(train)),
        "ratio_fit_rows": int(len(fit)),
        "global_pv_per_ghi_ratio_median": global_ratio,
        "hourly_ratio_count": int(len(ratios_by_hour)),
        "pv_cap_kw": pv_cap_kw,
        "daylight_target_count": int(daylight_mask.sum()),
        "global_fallback_target_count": int(fallback_mask.sum()),
        "daylight_fallback_count": int((fallback_mask & daylight_mask).sum()),
        "complete_prediction_count": int(len(prediction)),
        "target_features_used": ["timestamp.hour", "ghi_kwh_m2"],
    }
    return prediction, pd.DataFrame(hod_rows), parameters


def climatology_prediction(
    train: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, Any]]:
    counts = train.groupby("hour").size().reindex(range(24), fill_value=0)
    means = train.groupby("hour")["observed_pv_kw"].mean().reindex(range(24))
    if (counts <= 0).any():
        missing_hours = counts.index[counts <= 0].astype(int).tolist()
        raise RuntimeError(f"HOD mean climatology has empty training hours: {missing_hours}")
    if means.isna().any() or not np.isfinite(means.to_numpy(dtype=float)).all():
        raise RuntimeError("HOD mean climatology contains a missing or non-finite mean.")

    # The baseline target path deliberately receives timestamp only: no PV or weather.
    target_hours = target[["timestamp"]]["timestamp"].dt.hour
    prediction = target_hours.map(means.to_dict()).to_numpy(dtype="float64")
    pv_cap_kw = float(train["observed_pv_kw"].max())
    prediction = np.minimum(np.maximum(prediction, 0.0), pv_cap_kw)

    hod_rows = pd.DataFrame(
        {
            "hour_of_day": range(24),
            "eligible_training_rows": counts.to_numpy(dtype=int),
            "climatology_mean_pv_kw": means.to_numpy(dtype=float),
        }
    )
    parameters = {
        "eligible_training_rows": int(len(train)),
        "hourly_mean_count": 24,
        "pv_cap_kw": pv_cap_kw,
        "complete_prediction_count": int(len(prediction)),
        "target_features_used": ["timestamp.hour"],
        "fallback": None,
    }
    return prediction, hod_rows, parameters


def metric_record(
    holdout: str,
    method: str,
    observed: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, Any]:
    error = predicted - observed
    observed_energy = float(observed.sum())
    predicted_energy = float(predicted.sum())
    if observed_energy <= 0.0:
        raise RuntimeError(f"{holdout} observed energy is non-positive.")
    signed_bias_pct = 100.0 * float(error.sum()) / observed_energy
    return {
        "holdout": holdout,
        "method": method,
        "timestamp_count": int(len(observed)),
        "mae_kw": float(np.mean(np.abs(error))),
        "rmse_kw": float(np.sqrt(np.mean(error**2))),
        "observed_total_energy_kwh": observed_energy,
        "predicted_total_energy_kwh": predicted_energy,
        "signed_aggregate_energy_bias_pct": signed_bias_pct,
        "absolute_aggregate_energy_bias_pct": abs(signed_bias_pct),
    }


def daily_metric_records(predictions: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for (holdout, method, date), group in predictions.groupby(
        ["holdout", "method", "calendar_date"], sort=True
    ):
        observed = group["observed_pv_kw"].to_numpy(dtype=float)
        predicted = group["predicted_pv_kw"].to_numpy(dtype=float)
        error = predicted - observed
        observed_energy = float(observed.sum())
        signed_error = float(error.sum())
        records.append(
            {
                "holdout": holdout,
                "method": method,
                "calendar_date": date,
                "hours": int(len(group)),
                "observed_energy_kwh": observed_energy,
                "predicted_energy_kwh": float(predicted.sum()),
                "signed_energy_error_kwh": signed_error,
                "signed_energy_error_pct": (
                    100.0 * signed_error / observed_energy
                    if observed_energy > 0.0
                    else np.nan
                ),
                "mae_kw": float(np.mean(np.abs(error))),
                "rmse_kw": float(np.sqrt(np.mean(error**2))),
            }
        )
    return pd.DataFrame(records)


def physical_leakage_record(
    *,
    definition: dict[str, Any],
    method: str,
    target: pd.DataFrame,
    train: pd.DataFrame,
    predicted: np.ndarray,
    pv_cap_kw: float,
    reference: ModuleType,
    truth_hash_before: str,
    truth_hash_after: str,
) -> dict[str, Any]:
    timestamps = target["timestamp"].reset_index(drop=True)
    target_set = set(timestamps.tolist())
    train_set = set(train["timestamp"].tolist())
    predicted_series = pd.Series(predicted)
    count_pass = len(predicted) == int(definition["expected_timestamps"])
    unique_pass = timestamps.nunique() == int(definition["expected_timestamps"])
    complete_pass = len(predicted_series) == len(target) and predicted_series.notna().all()
    finite_pass = np.isfinite(predicted).all()
    nonnegative_pass = bool(np.all(predicted >= 0.0))
    capacity_pass = bool(np.all(predicted <= pv_cap_kw))
    leakage_pass = target_set.isdisjoint(train_set)
    truth_unchanged_pass = truth_hash_before == truth_hash_after

    if method == METHOD_CWA:
        night_mask = target["ghi_kwh_m2"].le(float(reference.DAYLIGHT_GHI_THRESHOLD))
        night_behavior_pass = bool(np.all(predicted[night_mask.to_numpy()] == 0.0))
        night_behavior_rule = (
            f"prediction=0 when GHI <= {float(reference.DAYLIGHT_GHI_THRESHOLD):.17g}"
        )
    else:
        night_behavior_pass = True
        night_behavior_rule = (
            "PASS_NOT_APPLICABLE: frozen HOD-mean baseline is prohibited from "
            "using target GHI; training-derived HOD means and physical bounds apply"
        )

    gates = {
        "prediction_count_pass": bool(count_pass),
        "unique_target_timestamp_pass": bool(unique_pass),
        "prediction_complete_pass": bool(complete_pass),
        "prediction_finite_pass": bool(finite_pass),
        "prediction_nonnegative_pass": nonnegative_pass,
        "prediction_capacity_bound_pass": capacity_pass,
        "night_daylight_behavior_pass": night_behavior_pass,
        "observed_truth_unchanged_pass": truth_unchanged_pass,
        "zero_target_leakage_pass": bool(leakage_pass),
    }
    return {
        "holdout": definition["holdout"],
        "method": method,
        "target_count": int(len(target)),
        "prediction_count": int(len(predicted)),
        "unique_target_timestamps": int(timestamps.nunique()),
        "missing_predictions": int(predicted_series.isna().sum()),
        "minimum_prediction_kw": float(np.min(predicted)),
        "maximum_prediction_kw": float(np.max(predicted)),
        "pv_cap_kw": float(pv_cap_kw),
        "training_target_timestamp_intersection": int(len(target_set.intersection(train_set))),
        "night_daylight_rule": night_behavior_rule,
        **gates,
        "overall_physical_leakage_gate_pass": bool(all(gates.values())),
    }


def bootstrap_outputs(
    predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    replicate_frames: list[pd.DataFrame] = []
    summary_records: list[dict[str, Any]] = []
    block_records: list[dict[str, Any]] = []

    for definition in HOLDOUTS:
        holdout = str(definition["holdout"])
        expected_complete = int(definition["expected_complete_days"])
        expected_partial_hours = int(definition["expected_partial_hours"])
        base = predictions.loc[
            (predictions["holdout"] == holdout)
            & (predictions["method"] == METHOD_CWA)
        ].copy()
        block_sizes = base.groupby("calendar_date").size().sort_index()
        complete_dates = block_sizes.index[block_sizes.eq(24)].tolist()
        partial_dates = block_sizes.index[block_sizes.ne(24)].tolist()
        if len(complete_dates) != expected_complete:
            raise RuntimeError(
                f"{holdout} complete bootstrap blocks={len(complete_dates)}; "
                f"expected={expected_complete}."
            )
        if expected_partial_hours == 0:
            if partial_dates:
                raise RuntimeError(f"{holdout} unexpectedly has partial bootstrap blocks.")
            partial_date = None
        else:
            if len(partial_dates) != 1:
                raise RuntimeError(f"{holdout} must have exactly one partial block.")
            partial_date = partial_dates[0]
            if int(block_sizes.loc[partial_date]) != expected_partial_hours:
                raise RuntimeError(
                    f"{holdout} partial block has {int(block_sizes.loc[partial_date])} hours; "
                    f"expected={expected_partial_hours}."
                )

        draws = rng.integers(
            0,
            len(complete_dates),
            size=(BOOTSTRAP_REPLICATES, len(complete_dates)),
        )
        block_records.append(
            {
                "holdout": holdout,
                "complete_daily_blocks": len(complete_dates),
                "sampled_complete_blocks_per_replicate": len(complete_dates),
                "partial_date": partial_date,
                "partial_hours": expected_partial_hours,
                "partial_block_included_once_per_replicate": bool(partial_date is not None),
                "replicates": BOOTSTRAP_REPLICATES,
                "seed": BOOTSTRAP_SEED,
            }
        )

        for method in METHODS:
            method_rows = predictions.loc[
                (predictions["holdout"] == holdout)
                & (predictions["method"] == method)
            ].copy()
            grouped = []
            for date, group in method_rows.groupby("calendar_date", sort=True):
                observed = group["observed_pv_kw"].to_numpy(dtype=float)
                predicted = group["predicted_pv_kw"].to_numpy(dtype=float)
                error = predicted - observed
                grouped.append(
                    {
                        "calendar_date": date,
                        "hours": int(len(group)),
                        "absolute_error_sum_kw": float(np.abs(error).sum()),
                        "signed_error_sum_kwh": float(error.sum()),
                        "observed_energy_kwh": float(observed.sum()),
                    }
                )
            daily = pd.DataFrame(grouped).set_index("calendar_date")
            complete = daily.loc[complete_dates]
            abs_sums = complete["absolute_error_sum_kw"].to_numpy(dtype=float)[draws].sum(axis=1)
            signed_sums = complete["signed_error_sum_kwh"].to_numpy(dtype=float)[draws].sum(axis=1)
            observed_sums = complete["observed_energy_kwh"].to_numpy(dtype=float)[draws].sum(axis=1)
            sampled_hours = np.full(
                BOOTSTRAP_REPLICATES,
                len(complete_dates) * 24,
                dtype=int,
            )
            if partial_date is not None:
                partial = daily.loc[partial_date]
                abs_sums = abs_sums + float(partial["absolute_error_sum_kw"])
                signed_sums = signed_sums + float(partial["signed_error_sum_kwh"])
                observed_sums = observed_sums + float(partial["observed_energy_kwh"])
                sampled_hours = sampled_hours + int(partial["hours"])
            if np.any(observed_sums <= 0.0):
                raise RuntimeError(f"{holdout}/{method} bootstrap sampled non-positive energy.")

            mae = abs_sums / sampled_hours
            signed_bias = 100.0 * signed_sums / observed_sums
            replicate_frames.append(
                pd.DataFrame(
                    {
                        "holdout": holdout,
                        "method": method,
                        "replicate": np.arange(1, BOOTSTRAP_REPLICATES + 1),
                        "sampled_complete_blocks": len(complete_dates),
                        "fixed_partial_hours": expected_partial_hours,
                        "sampled_hours": sampled_hours,
                        "mae_kw": mae,
                        "signed_aggregate_energy_bias_pct": signed_bias,
                    }
                )
            )
            mae_ci = np.percentile(mae, PERCENTILES)
            bias_ci = np.percentile(signed_bias, PERCENTILES)
            summary_records.append(
                {
                    "holdout": holdout,
                    "method": method,
                    "replicates": BOOTSTRAP_REPLICATES,
                    "seed": BOOTSTRAP_SEED,
                    "percentile_method": "numpy_default_linear",
                    "lower_percentile": PERCENTILES[0],
                    "upper_percentile": PERCENTILES[1],
                    "mae_kw_ci_lower": float(mae_ci[0]),
                    "mae_kw_ci_upper": float(mae_ci[1]),
                    "signed_energy_bias_pct_ci_lower": float(bias_ci[0]),
                    "signed_energy_bias_pct_ci_upper": float(bias_ci[1]),
                    "pass_fail_role": "REPORT_ONLY",
                }
            )

    return (
        pd.concat(replicate_frames, ignore_index=True),
        pd.DataFrame(summary_records),
        pd.DataFrame(block_records),
    )


def comparison_record(left: float, right: float, *, operation: str) -> dict[str, Any]:
    if not math.isfinite(left) or not math.isfinite(right):
        raise RuntimeError("Acceptance comparison received a non-finite operand.")
    ulp_band = max(math.ulp(left), math.ulp(right))
    difference = left - right
    # The frozen rule authorizes no comparison tolerance. Exact binary64
    # equality is therefore reported as ambiguous and stops the decision;
    # every nonzero difference uses the literal strict comparison below.
    ambiguous = difference == 0.0
    if operation == "lt":
        result = left < right
    elif operation == "gt":
        result = left > right
    else:
        raise ValueError(f"Unsupported comparison operation: {operation}")
    return {
        "left": left,
        "right": right,
        "left_minus_right": difference,
        "operation": operation,
        "machine_precision_ulp_band": ulp_band,
        "machine_precision_ambiguous": ambiguous,
        "result": bool(result),
    }


def acceptance_decision(
    metrics: pd.DataFrame,
    physical_audit: pd.DataFrame,
) -> dict[str, Any]:
    indexed = metrics.set_index(["holdout", "method"])
    comparisons: dict[str, Any] = {}
    for holdout in ("H1", "H2", "H3"):
        cwa = indexed.loc[(holdout, METHOD_CWA)]
        baseline = indexed.loc[(holdout, METHOD_CLIMATOLOGY)]
        operation = "lt" if holdout == "H3" else "gt"
        comparisons[holdout] = {
            "rmse": comparison_record(
                float(cwa["rmse_kw"]),
                float(baseline["rmse_kw"]),
                operation=operation,
            ),
            "absolute_energy_bias": comparison_record(
                float(cwa["absolute_aggregate_energy_bias_pct"]),
                float(baseline["absolute_aggregate_energy_bias_pct"]),
                operation=operation,
            ),
        }

    ambiguous = [
        f"{holdout}.{metric}"
        for holdout, values in comparisons.items()
        for metric, record in values.items()
        if record["machine_precision_ambiguous"]
    ]
    all_gates_pass = bool(physical_audit["overall_physical_leakage_gate_pass"].all())
    h3_pass = bool(
        comparisons["H3"]["rmse"]["result"]
        and comparisons["H3"]["absolute_energy_bias"]["result"]
    )
    h1_strictly_worse_on_both = bool(
        comparisons["H1"]["rmse"]["result"]
        and comparisons["H1"]["absolute_energy_bias"]["result"]
    )
    h2_strictly_worse_on_both = bool(
        comparisons["H2"]["rmse"]["result"]
        and comparisons["H2"]["absolute_energy_bias"]["result"]
    )
    if ambiguous:
        decision = "FAIL"
        execution_status = "STOP_NUMERIC_COMPARISON_AMBIGUOUS"
    else:
        passed = bool(
            all_gates_pass
            and h3_pass
            and not h1_strictly_worse_on_both
            and not h2_strictly_worse_on_both
        )
        decision = "PASS_FOR_SENSITIVITY" if passed else "FAIL"
        execution_status = "COMPLETED"
    return {
        "WINTER_PV_RECONSTRUCTION_VALIDATION": decision,
        "execution_status": execution_status,
        "comparison_semantics": {
            "H3": "CWA RMSE < HOD-mean RMSE AND CWA absolute bias < HOD-mean absolute bias",
            "H1": "FAIL secondary gate only if CWA RMSE > HOD-mean RMSE AND CWA absolute bias > HOD-mean absolute bias",
            "H2": "FAIL secondary gate only if CWA RMSE > HOD-mean RMSE AND CWA absolute bias > HOD-mean absolute bias",
            "numerical_tolerance": None,
            "ambiguity_policy": (
                "Stop on exact binary64 equality; apply no numerical tolerance "
                "to any nonzero difference."
            ),
        },
        "comparisons": comparisons,
        "machine_precision_ambiguous_comparisons": ambiguous,
        "all_physical_leakage_completeness_gates_pass": all_gates_pass,
        "H3_primary_pass": h3_pass,
        "H1_cwa_strictly_worse_on_both": h1_strictly_worse_on_both,
        "H1_secondary_pass": not h1_strictly_worse_on_both,
        "H2_cwa_strictly_worse_on_both": h2_strictly_worse_on_both,
        "H2_secondary_pass": not h2_strictly_worse_on_both,
        "bootstrap_used_for_pass_fail": False,
        "absolute_accuracy_threshold": None,
    }


def artifact_hashes(run_dir: Path, *, exclude: set[str] | None = None) -> dict[str, Any]:
    excluded = exclude or set()
    return {
        path.name: {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in sorted(run_dir.iterdir())
        if path.is_file() and path.name not in excluded
    }


def main() -> int:
    args = parse_args()
    root = project_root()
    script_path = Path(__file__).resolve()
    protocol_path = root / "docs" / "winter_pv_longblock_sensitivity_protocol_v7_2_2026-09-07.md"
    cwa_reference_path = root / "scripts" / "04b_compare_pv_donor_vs_cwa.py"
    annual_input_path = root / "data" / "processed" / "annual_input_v7_1.parquet"
    observed_parquet = root / "data" / "processed" / "ntust_case_year_observed.parquet"
    observed_csv = root / "data" / "processed" / "ntust_case_year_observed.csv"
    cwa_path = root / "data" / "raw" / "cwa_codis" / "466920" / "cwa_466920_formal_8760_ghi_temperature.csv"
    required_paths = (
        protocol_path,
        cwa_reference_path,
        annual_input_path,
        observed_parquet,
        observed_csv,
        cwa_path,
    )
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Required controlled inputs are missing: {missing}")

    protocol_hash = sha256_file(protocol_path)
    if protocol_hash.lower() != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(
            "Frozen protocol hash mismatch; Script 17a must stop before creating artifacts: "
            f"expected={EXPECTED_PROTOCOL_SHA256}, actual={protocol_hash}."
        )

    started = utc_now()
    run_id = new_run_id(started)
    output_root = args.output_root.resolve()
    allowed_root = (root / "results" / "data_audit" / "winter_pv_holdouts").resolve()
    if output_root != allowed_root:
        raise RuntimeError(
            "Script 17a may write only to the controlled run-specific validation root: "
            f"{allowed_root}"
        )
    run_dir = output_root / run_id

    # Capture repository state before any run-specific artifact is created.
    git_status_at_start = git_value(root, "status", "--porcelain=v1") or ""
    source_commit_at_start = git_value(root, "rev-parse", "HEAD")
    git_branch_at_start = git_value(root, "branch", "--show-current")
    reference = load_reference_module(cwa_reference_path)
    source_hashes_at_start = {
        "protocol": sha256_file(protocol_path),
        "observed_parquet": sha256_file(observed_parquet),
        "observed_csv": sha256_file(observed_csv),
        "cwa": sha256_file(cwa_path),
        "canonical_annual_input": sha256_file(annual_input_path),
        "script_17a": sha256_file(script_path),
        "cwa_reference_script_04b": sha256_file(cwa_reference_path),
    }
    run_dir.mkdir(parents=True, exist_ok=False)
    run_manifest_path = run_dir / "run_manifest.json"
    write_json(
        run_manifest_path,
        {
            "run_id": run_id,
            "run_started_utc": utc_text(started),
            "mode": "WINTER_PV_HOLDOUT_VALIDATION_ONLY_NO_MILP",
            "script_version": SCRIPT_VERSION,
            "frozen_protocol_sha256_expected": EXPECTED_PROTOCOL_SHA256,
            "frozen_protocol_sha256_actual": protocol_hash,
            "cwa_reference_version_expected": EXPECTED_CWA_REFERENCE_VERSION,
            "cwa_reference_version_actual": reference.SCRIPT_VERSION,
            "paths": {
                "protocol": protocol_path,
                "observed_parquet": observed_parquet,
                "observed_csv_reference": observed_csv,
                "cwa": cwa_path,
                "canonical_annual_input": annual_input_path,
                "script_17a": script_path,
                "cwa_reference_script_04b": cwa_reference_path,
                "run_directory": run_dir,
            },
            "source_hashes_at_start": source_hashes_at_start,
            "git": {
                "commit": source_commit_at_start,
                "branch": git_branch_at_start,
                "dirty": bool(git_status_at_start),
                "status_porcelain_at_start": git_status_at_start.splitlines(),
            },
            "software": {
                "python": platform.python_version(),
                "python_executable": sys.executable,
                "pandas": pd.__version__,
                "numpy": np.__version__,
            },
            "holdouts": list(HOLDOUTS),
            "bootstrap": {
                "replicates": BOOTSTRAP_REPLICATES,
                "seed": BOOTSTRAP_SEED,
                "percentiles": list(PERCENTILES),
                "role": "REPORT_ONLY",
            },
        },
        exclusive=True,
    )

    try:
        data, observed_path_used, cwa_path_used = load_controlled_data(root, reference)
        if observed_path_used.resolve() != observed_parquet.resolve():
            raise RuntimeError(
                f"Controlled observed input changed unexpectedly: {observed_path_used}"
            )
        if cwa_path_used.resolve() != cwa_path.resolve():
            raise RuntimeError(f"Controlled CWA input changed unexpectedly: {cwa_path_used}")

        definition_rows: list[dict[str, Any]] = []
        training_rows: list[dict[str, Any]] = []
        cwa_hod_frames: list[pd.DataFrame] = []
        climatology_hod_frames: list[pd.DataFrame] = []
        prediction_frames: list[pd.DataFrame] = []
        metric_rows: list[dict[str, Any]] = []
        physical_rows: list[dict[str, Any]] = []

        for definition in HOLDOUTS:
            holdout = str(definition["holdout"])
            target, target_gates = validate_holdout_target(data, definition)
            train = eligible_training_rows(data, definition)
            target_timestamps = set(target["timestamp"].tolist())
            train_timestamps = set(train["timestamp"].tolist())
            intersection = target_timestamps.intersection(train_timestamps)
            if intersection:
                raise RuntimeError(f"{holdout} target timestamps leaked into training.")

            truth_columns = ["timestamp", "observed_pv_kw", "pv_status", "outage_contaminated_flag"]
            truth_hash_before = stable_frame_sha256(target, truth_columns)
            training_hash = stable_frame_sha256(
                train,
                [
                    "timestamp",
                    "observed_pv_kw",
                    "pv_status",
                    "outage_contaminated_flag",
                    "ghi_kwh_m2",
                ],
            )
            pv_cap_kw = float(train["observed_pv_kw"].max())
            if not math.isfinite(pv_cap_kw) or pv_cap_kw < 0.0:
                raise RuntimeError(f"{holdout} resolved an invalid pv_cap_kw={pv_cap_kw}.")

            cwa_pred, cwa_hod, cwa_parameters = cwa_prediction(reference, train, target)
            climatology_pred, climatology_hod, climatology_parameters = (
                climatology_prediction(train, target)
            )
            if float(cwa_parameters["pv_cap_kw"]) != pv_cap_kw:
                raise RuntimeError(f"{holdout} CWA pv_cap_kw mismatch.")
            if float(climatology_parameters["pv_cap_kw"]) != pv_cap_kw:
                raise RuntimeError(f"{holdout} climatology pv_cap_kw mismatch.")

            truth_hash_after = stable_frame_sha256(target, truth_columns)
            observed = target["observed_pv_kw"].to_numpy(dtype=float)
            for method, prediction in (
                (METHOD_CWA, cwa_pred),
                (METHOD_CLIMATOLOGY, climatology_pred),
            ):
                frame = pd.DataFrame(
                    {
                        "holdout": holdout,
                        "method": method,
                        "timestamp": target["timestamp"].to_numpy(),
                        "calendar_date": target["timestamp"].dt.strftime("%Y-%m-%d"),
                        "hour_of_day": target["timestamp"].dt.hour.to_numpy(dtype=int),
                        "observed_pv_kw": observed,
                        "ghi_kwh_m2": target["ghi_kwh_m2"].to_numpy(dtype=float),
                        "predicted_pv_kw": prediction,
                        "signed_error_kw": prediction - observed,
                        "absolute_error_kw": np.abs(prediction - observed),
                    }
                )
                prediction_frames.append(frame)
                metric_rows.append(metric_record(holdout, method, observed, prediction))
                physical_rows.append(
                    physical_leakage_record(
                        definition=definition,
                        method=method,
                        target=target,
                        train=train,
                        predicted=prediction,
                        pv_cap_kw=pv_cap_kw,
                        reference=reference,
                        truth_hash_before=truth_hash_before,
                        truth_hash_after=truth_hash_after,
                    )
                )

            cwa_hod.insert(0, "holdout", holdout)
            cwa_hod["global_pv_per_ghi_ratio_median"] = cwa_parameters[
                "global_pv_per_ghi_ratio_median"
            ]
            cwa_hod["pv_cap_kw"] = pv_cap_kw
            cwa_hod_frames.append(cwa_hod)
            climatology_hod.insert(0, "holdout", holdout)
            climatology_hod["pv_cap_kw"] = pv_cap_kw
            climatology_hod_frames.append(climatology_hod)

            hod_counts = train.groupby("hour").size().reindex(range(24), fill_value=0)
            training_rows.append(
                {
                    "holdout": holdout,
                    "eligible_training_rows": int(len(train)),
                    "training_set_sha256": training_hash,
                    "training_target_timestamp_intersection": len(intersection),
                    "minimum_training_rows_per_hod": int(hod_counts.min()),
                    "maximum_training_rows_per_hod": int(hod_counts.max()),
                    "all_24_hod_present": bool((hod_counts > 0).all()),
                    "pv_cap_kw": pv_cap_kw,
                    "cwa_ratio_fit_rows": cwa_parameters["ratio_fit_rows"],
                    "cwa_hourly_ratio_count": cwa_parameters["hourly_ratio_count"],
                    "cwa_global_ratio_median": cwa_parameters[
                        "global_pv_per_ghi_ratio_median"
                    ],
                    "cwa_daylight_target_count": cwa_parameters["daylight_target_count"],
                    "cwa_global_fallback_target_count": cwa_parameters[
                        "global_fallback_target_count"
                    ],
                    "cwa_daylight_fallback_count": cwa_parameters[
                        "daylight_fallback_count"
                    ],
                    "cwa_complete_prediction_count": cwa_parameters[
                        "complete_prediction_count"
                    ],
                    "climatology_hourly_mean_count": climatology_parameters[
                        "hourly_mean_count"
                    ],
                    "climatology_complete_prediction_count": climatology_parameters[
                        "complete_prediction_count"
                    ],
                }
            )
            definition_rows.append(
                {
                    **definition,
                    "actual_timestamps": int(len(target)),
                    "first_timestamp": target["timestamp"].min(),
                    "last_timestamp": target["timestamp"].max(),
                    **target_gates,
                }
            )

        predictions = pd.concat(prediction_frames, ignore_index=True)
        metrics = pd.DataFrame(metric_rows)
        physical_audit = pd.DataFrame(physical_rows)
        daily_metrics = daily_metric_records(predictions)
        bootstrap_replicates, bootstrap_summary, bootstrap_blocks = bootstrap_outputs(
            predictions
        )
        decision = acceptance_decision(metrics, physical_audit)

        write_csv(pd.DataFrame(definition_rows), run_dir / "holdout_definitions.csv")
        write_csv(pd.DataFrame(training_rows), run_dir / "training_set_audit.csv")
        write_csv(pd.concat(cwa_hod_frames, ignore_index=True), run_dir / "cwa_hod_parameters.csv")
        write_csv(
            pd.concat(climatology_hod_frames, ignore_index=True),
            run_dir / "climatology_hod_mean_parameters.csv",
        )
        write_csv(predictions, run_dir / "predictions.csv")
        write_csv(metrics, run_dir / "holdout_metrics.csv")
        write_csv(daily_metrics, run_dir / "daily_metrics.csv")
        write_csv(bootstrap_summary, run_dir / "bootstrap_summary.csv")
        write_csv(bootstrap_blocks, run_dir / "bootstrap_block_audit.csv")
        bootstrap_replicates.to_csv(
            run_dir / "bootstrap_replicates.csv.gz",
            index=False,
            encoding="utf-8",
            lineterminator="\n",
            float_format="%.17g",
            compression={"method": "gzip", "compresslevel": 9, "mtime": 0},
        )
        write_csv(physical_audit, run_dir / "physical_leakage_audit.csv")
        write_json(run_dir / "final_validation_decision.json", decision)

        source_hashes_at_end = {
            "protocol": sha256_file(protocol_path),
            "observed_parquet": sha256_file(observed_parquet),
            "observed_csv": sha256_file(observed_csv),
            "cwa": sha256_file(cwa_path),
            "canonical_annual_input": sha256_file(annual_input_path),
            "script_17a": sha256_file(script_path),
            "cwa_reference_script_04b": sha256_file(cwa_reference_path),
        }
        source_unchanged = {
            key: source_hashes_at_end[key] == source_hashes_at_start[key]
            for key in source_hashes_at_start
        }
        if not all(source_unchanged.values()):
            raise RuntimeError(f"Controlled source changed during validation: {source_unchanged}")

        completion_status = (
            "COMPLETED_PASS_FOR_SENSITIVITY"
            if decision["WINTER_PV_RECONSTRUCTION_VALIDATION"] == "PASS_FOR_SENSITIVITY"
            else "COMPLETED_FAIL"
        )
        completion_path = run_dir / "completion_manifest.json"
        write_json(
            completion_path,
            {
                "run_id": run_id,
                "status": completion_status,
                "run_started_utc": utc_text(started),
                "run_completed_utc": utc_text(utc_now()),
                "script_version": SCRIPT_VERSION,
                "source_commit": source_commit_at_start,
                "git_branch": git_branch_at_start,
                "git_status_porcelain_at_start": git_status_at_start.splitlines(),
                "decision": decision["WINTER_PV_RECONSTRUCTION_VALIDATION"],
                "holdout_status": {
                    "H1": "PASS" if decision["H1_secondary_pass"] else "FAIL",
                    "H2": "PASS" if decision["H2_secondary_pass"] else "FAIL",
                    "H3": "PASS" if decision["H3_primary_pass"] else "FAIL",
                },
                "paths": {
                    "frozen_protocol": protocol_path,
                    "script_17a": script_path,
                    "cwa_reference_script_04b": cwa_reference_path,
                    "observed_parquet": observed_parquet,
                    "observed_csv_reference": observed_csv,
                    "cwa": cwa_path,
                    "canonical_annual_input": annual_input_path,
                },
                "source_hashes_at_start": source_hashes_at_start,
                "source_hashes_at_end": source_hashes_at_end,
                "controlled_sources_unchanged": source_unchanged,
                "all_controlled_sources_unchanged": all(source_unchanged.values()),
                "artifacts": artifact_hashes(
                    run_dir,
                    exclude={"completion_manifest.json"},
                ),
            },
        )

        print(f"Run ID: {run_id}")
        print(f"Run directory: {run_dir}")
        print(f"Script version: {SCRIPT_VERSION}")
        print(f"Protocol SHA-256: {protocol_hash}")
        print(metrics.to_string(index=False))
        print(
            "WINTER_PV_RECONSTRUCTION_VALIDATION = "
            f"{decision['WINTER_PV_RECONSTRUCTION_VALIDATION']}"
        )
        return (
            0
            if decision["WINTER_PV_RECONSTRUCTION_VALIDATION"] == "PASS_FOR_SENSITIVITY"
            else 2
        )
    except Exception as exc:
        write_json(
            run_dir / "run_failure.json",
            {
                "run_id": run_id,
                "status": "FAILED_TO_EXECUTE",
                "failed_utc": utc_text(utc_now()),
                "exception_type": type(exc).__name__,
                "message": str(exc),
            },
        )
        write_json(
            run_dir / "completion_manifest.json",
            {
                "run_id": run_id,
                "status": "FAILED_TO_EXECUTE",
                "run_started_utc": utc_text(started),
                "run_completed_utc": utc_text(utc_now()),
                "script_version": SCRIPT_VERSION,
                "artifacts": artifact_hashes(
                    run_dir,
                    exclude={"completion_manifest.json"},
                ),
            },
        )
        print(f"Script 17a failed: {exc}", file=sys.stderr)
        print(f"Run directory: {run_dir}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
