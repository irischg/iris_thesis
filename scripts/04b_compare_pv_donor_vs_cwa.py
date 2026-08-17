from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7-pv-cwa-headtohead-validation-r3-2026-08-16"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760

DAYLIGHT_GHI_THRESHOLD = 0.01
RATIO_FIT_GHI_THRESHOLD = 0.05

DONOR_WINDOW_DAYS = 30
DONOR_K = 5
DONOR_AGGREGATION = "mean"

# Keep CWA models intentionally simple/interpretable.
MODEL_NAMES = (
    "ghi_proportional",
    "ghi_temperature",
    "hourly_ghi_ratio_median",
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()

    parser = argparse.ArgumentParser(
        description=(
            "Compare CWA-based short-gap PV reconstruction against the "
            "validated donor method on the exact Script-04 pseudo-gap set. "
            "No production PV values are changed."
        )
    )

    parser.add_argument(
        "--observed-parquet",
        type=Path,
        default=(
            root
            / "data"
            / "processed"
            / "ntust_case_year_observed.parquet"
        ),
    )
    parser.add_argument(
        "--observed-csv",
        type=Path,
        default=(
            root
            / "data"
            / "processed"
            / "ntust_case_year_observed.csv"
        ),
    )

    parser.add_argument(
        "--cwa-input",
        type=Path,
        default=(
            root
            / "data"
            / "raw"
            / "cwa_codis"
            / "466920"
            / "cwa_466920_formal_8760_ghi_temperature.csv"
        ),
    )

    parser.add_argument(
        "--pseudogap-targets",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pv_pseudogap_targets_v7.csv"
        ),
    )

    parser.add_argument(
        "--donor-event-metrics",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pv_pseudogap_event_metrics_v7.csv"
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "results" / "data_audit",
    )

    return parser.parse_args()


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


def numeric_clean(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string")
        .str.strip()
        .replace(
            {
                "": pd.NA,
                "--": pd.NA,
                "/": pd.NA,
                "x": pd.NA,
                "X": pd.NA,
                "T": pd.NA,
            }
        ),
        errors="coerce",
    )


def read_observed(
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


def prepare_observed(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "timestamp",
        "observed_pv_kw",
        "pv_status",
        "outage_contaminated_flag",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Observed input missing columns: {sorted(missing)}"
        )

    result = df.copy()
    result["timestamp"] = parse_timestamp(result["timestamp"])
    result["observed_pv_kw"] = numeric_clean(
        result["observed_pv_kw"]
    )

    if result["timestamp"].isna().any():
        raise ValueError("Observed input has invalid timestamps.")

    result = result.loc[
        (result["timestamp"] >= FORMAL_START)
        & (result["timestamp"] < FORMAL_END_EXCLUSIVE)
    ].copy()

    result = (
        result.sort_values("timestamp")
        .reset_index(drop=True)
    )

    if len(result) != EXPECTED_HOURS:
        raise ValueError(
            f"Observed formal rows={len(result):,}; expected 8,760."
        )

    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )
    if not pd.DatetimeIndex(result["timestamp"]).equals(expected):
        raise ValueError(
            "Observed timeline is not the exact v7 8,760-hour timeline."
        )

    if result["observed_pv_kw"].isna().any():
        raise ValueError("Observed PV contains missing values.")

    return result


def read_cwa(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find CWA input:\n{path}"
        )

    weather = pd.read_csv(path)

    required = {
        "timestamp",
        "air_temperature_c",
        "global_solar_radiation_raw",
    }
    missing = required.difference(weather.columns)
    if missing:
        raise ValueError(
            f"CWA input missing columns: {sorted(missing)}"
        )

    # CODiS daily hourly reports use hour-ending labels, but the
    # final hourly interval of each calendar day is commonly labelled
    # 23:59 rather than next-day 00:00. Normalize that label FIRST,
    # then convert hour-ending -> v7 interval-start by subtracting 1 h.
    weather["timestamp_raw"] = parse_timestamp(
        weather["timestamp"]
    )

    if weather["timestamp_raw"].isna().any():
        raise ValueError(
            "CWA input contains unparseable timestamps."
        )

    mask_2359 = (
        weather["timestamp_raw"].dt.hour.eq(23)
        & weather["timestamp_raw"].dt.minute.eq(59)
        & weather["timestamp_raw"].dt.second.eq(0)
    )

    other_off_hour = (
        ~weather["timestamp_raw"].dt.minute.eq(0)
        & ~mask_2359
    )

    if other_off_hour.any():
        examples = (
            weather.loc[
                other_off_hour,
                "timestamp_raw",
            ]
            .head(10)
            .astype(str)
            .tolist()
        )
        raise ValueError(
            "CWA contains non-hourly timestamps other than "
            f"the expected 23:59 labels, e.g. {examples}"
        )

    weather["timestamp_adjusted_end"] = weather[
        "timestamp_raw"
    ].copy()

    weather.loc[
        mask_2359,
        "timestamp_adjusted_end",
    ] = (
        weather.loc[
            mask_2359,
            "timestamp_raw",
        ]
        + pd.Timedelta(minutes=1)
    )

    weather["timestamp_raw_end"] = weather[
        "timestamp_adjusted_end"
    ]

    weather["timestamp"] = (
        weather["timestamp_raw_end"]
        - pd.Timedelta(hours=1)
    )

    weather["ghi_mj_m2"] = numeric_clean(
        weather["global_solar_radiation_raw"]
    )

    # Negative radiation is not physically meaningful here and is
    # treated as missing/sentinel.
    weather.loc[
        weather["ghi_mj_m2"] < 0,
        "ghi_mj_m2",
    ] = np.nan

    # CODiS hourly accumulated global solar radiation:
    # MJ/m² per hour -> kWh/m² per hour.
    weather["ghi_kwh_m2"] = (
        weather["ghi_mj_m2"] / 3.6
    )

    weather["air_temperature_c"] = numeric_clean(
        weather["air_temperature_c"]
    )

    invalid_temp = (
        (weather["air_temperature_c"] <= -90)
        | (weather["air_temperature_c"] > 60)
    )
    weather.loc[
        invalid_temp,
        "air_temperature_c",
    ] = np.nan

    weather = weather.loc[
        (weather["timestamp"] >= FORMAL_START)
        & (weather["timestamp"] < FORMAL_END_EXCLUSIVE)
    ][
        [
            "timestamp",
            "timestamp_raw_end",
            "ghi_kwh_m2",
            "air_temperature_c",
        ]
    ].copy()

    weather = (
        weather.sort_values("timestamp")
        .drop_duplicates("timestamp", keep="last")
        .reset_index(drop=True)
    )

    if len(weather) != EXPECTED_HOURS:
        raise ValueError(
            f"CWA formal rows={len(weather):,}; expected 8,760."
        )

    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )
    if not pd.DatetimeIndex(weather["timestamp"]).equals(expected):
        raise ValueError(
            "CWA timeline is not aligned to the v7 interval-start "
            "8,760-hour timeline."
        )

    # Temperature is only an explanatory variable.
    weather["air_temperature_c"] = (
        weather["air_temperature_c"]
        .interpolate(
            method="linear",
            limit_direction="both",
        )
    )

    if weather["air_temperature_c"].isna().any():
        weather["air_temperature_c"] = (
            weather["air_temperature_c"]
            .fillna(
                weather["air_temperature_c"].median()
            )
        )

    weather.attrs["adjusted_2359_count"] = int(mask_2359.sum())
    return weather


def prepare_targets(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            "Script-04 pseudo-gap target file not found:\n"
            f"{path}"
        )

    targets = pd.read_csv(path)

    required = {
        "pseudo_event_id",
        "template_id",
        "target_start",
        "duration_hours",
    }
    missing = required.difference(targets.columns)
    if missing:
        raise ValueError(
            f"Pseudo-gap target file missing columns: {sorted(missing)}"
        )

    targets["target_start"] = parse_timestamp(
        targets["target_start"]
    )
    targets["duration_hours"] = pd.to_numeric(
        targets["duration_hours"],
        errors="coerce",
    )

    if (
        targets["target_start"].isna().any()
        or targets["duration_hours"].isna().any()
    ):
        raise ValueError(
            "Pseudo-gap targets contain invalid start/duration."
        )

    return (
        targets.sort_values("pseudo_event_id")
        .reset_index(drop=True)
    )


def prepare_donor_metrics(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            "Script-04 event metrics not found:\n"
            f"{path}"
        )

    metrics = pd.read_csv(path)

    required = {
        "pseudo_event_id",
        "aggregation",
        "window_days",
        "k",
        "event_mae_kw",
        "event_rmse_kw",
        "event_energy_bias_kwh",
        "event_abs_energy_bias_kwh",
        "n_hours",
        "abs_error_sum",
        "squared_error_sum",
        "error_sum",
        "actual_energy_kwh",
        "predicted_energy_kwh",
    }
    missing = required.difference(metrics.columns)
    if missing:
        raise ValueError(
            f"Donor metrics missing columns: {sorted(missing)}"
        )

    donor = metrics.loc[
        metrics["aggregation"].astype(str).eq(
            DONOR_AGGREGATION
        )
        & pd.to_numeric(
            metrics["window_days"],
            errors="coerce",
        ).eq(DONOR_WINDOW_DAYS)
        & pd.to_numeric(
            metrics["k"],
            errors="coerce",
        ).eq(DONOR_K)
    ].copy()

    if donor.empty:
        raise ValueError(
            "Cannot find Script-04 donor rule "
            f"±{DONOR_WINDOW_DAYS} days/K={DONOR_K}/"
            f"{DONOR_AGGREGATION}."
        )

    if donor["pseudo_event_id"].duplicated().any():
        raise ValueError(
            "Donor event metrics have duplicate pseudo_event_id rows."
        )

    return donor


def training_rows(
    data: pd.DataFrame,
    *,
    target_day: pd.Timestamp,
) -> pd.DataFrame:
    train = data.loc[
        data["pv_status"].astype(str).eq("valid")
        & (~data["outage_contaminated_flag"].astype(bool))
        & data["observed_pv_kw"].notna()
        & data["ghi_kwh_m2"].notna()
        & data["air_temperature_c"].notna()
    ].copy()

    # Leave the entire target calendar day out. This prevents the CWA
    # model from using any PV truth from the pseudo-gap target day.
    train = train.loc[
        train["timestamp"].dt.normalize().ne(
            pd.Timestamp(target_day).normalize()
        )
    ].copy()

    if train.empty:
        raise ValueError(
            f"No CWA-PV training rows remain for target day {target_day}."
        )

    train["hour"] = train["timestamp"].dt.hour
    return train


def cap_prediction(
    prediction: np.ndarray,
    ghi: np.ndarray,
    pv_cap: float,
) -> np.ndarray:
    result = np.asarray(
        prediction,
        dtype="float64",
    )
    result = np.where(
        np.isfinite(result),
        result,
        0.0,
    )
    result = np.maximum(result, 0.0)
    result = np.minimum(result, pv_cap)

    result = np.where(
        np.asarray(ghi) <= DAYLIGHT_GHI_THRESHOLD,
        0.0,
        result,
    )

    return result


def predict_ghi_proportional(
    train: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, float]]:
    fit = train.loc[
        train["ghi_kwh_m2"] > DAYLIGHT_GHI_THRESHOLD
    ].copy()

    x = fit["ghi_kwh_m2"].to_numpy(
        dtype="float64"
    )
    y = fit["observed_pv_kw"].to_numpy(
        dtype="float64"
    )

    denominator = float(np.dot(x, x))
    if denominator <= 0:
        raise ValueError(
            "GHI proportional denominator is zero."
        )

    slope = float(np.dot(x, y) / denominator)
    pv_cap = float(
        train["observed_pv_kw"].max()
    )

    ghi = target["ghi_kwh_m2"].to_numpy(
        dtype="float64"
    )

    prediction = cap_prediction(
        slope * ghi,
        ghi,
        pv_cap,
    )

    return prediction, {
        "parameter_1": slope,
        "parameter_2": np.nan,
        "pv_cap_kw": pv_cap,
    }


def predict_ghi_temperature(
    train: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, float]]:
    fit = train.loc[
        train["ghi_kwh_m2"] > DAYLIGHT_GHI_THRESHOLD
    ].copy()

    ghi = fit["ghi_kwh_m2"].to_numpy(
        dtype="float64"
    )
    temp = fit["air_temperature_c"].to_numpy(
        dtype="float64"
    )
    y = fit["observed_pv_kw"].to_numpy(
        dtype="float64"
    )

    # Interpretable linear form:
    # PV = a*GHI + b*GHI*(25 - T)
    x = np.column_stack(
        [
            ghi,
            ghi * (25.0 - temp),
        ]
    )

    coefficients, *_ = np.linalg.lstsq(
        x,
        y,
        rcond=None,
    )

    pv_cap = float(
        train["observed_pv_kw"].max()
    )

    target_ghi = target["ghi_kwh_m2"].to_numpy(
        dtype="float64"
    )
    target_temp = target["air_temperature_c"].to_numpy(
        dtype="float64"
    )

    x_target = np.column_stack(
        [
            target_ghi,
            target_ghi * (25.0 - target_temp),
        ]
    )

    prediction = cap_prediction(
        x_target @ coefficients,
        target_ghi,
        pv_cap,
    )

    return prediction, {
        "parameter_1": float(coefficients[0]),
        "parameter_2": float(coefficients[1]),
        "pv_cap_kw": pv_cap,
    }


def predict_hourly_ghi_ratio_median(
    train: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, float]]:
    fit = train.loc[
        train["ghi_kwh_m2"] > RATIO_FIT_GHI_THRESHOLD
    ].copy()

    fit["pv_per_ghi"] = (
        fit["observed_pv_kw"]
        / fit["ghi_kwh_m2"]
    )

    global_ratio = float(
        fit["pv_per_ghi"].median()
    )

    hourly_ratio = (
        fit.groupby("hour")["pv_per_ghi"]
        .median()
        .to_dict()
    )

    target_hour = target["timestamp"].dt.hour

    ratios = (
        target_hour.map(hourly_ratio)
        .fillna(global_ratio)
        .to_numpy(dtype="float64")
    )

    ghi = target["ghi_kwh_m2"].to_numpy(
        dtype="float64"
    )

    pv_cap = float(
        train["observed_pv_kw"].max()
    )

    prediction = cap_prediction(
        ratios * ghi,
        ghi,
        pv_cap,
    )

    return prediction, {
        "parameter_1": global_ratio,
        "parameter_2": float(len(hourly_ratio)),
        "pv_cap_kw": pv_cap,
    }


MODEL_FUNCTIONS = {
    "ghi_proportional":
        predict_ghi_proportional,
    "ghi_temperature":
        predict_ghi_temperature,
    "hourly_ghi_ratio_median":
        predict_hourly_ghi_ratio_median,
}


def event_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    actual = np.asarray(
        actual,
        dtype="float64",
    )
    predicted = np.asarray(
        predicted,
        dtype="float64",
    )

    valid = (
        np.isfinite(actual)
        & np.isfinite(predicted)
    )

    actual = actual[valid]
    predicted = predicted[valid]

    if len(actual) == 0:
        raise ValueError(
            "No valid CWA predictions for pseudo-event."
        )

    error = predicted - actual

    actual_energy = float(actual.sum())
    predicted_energy = float(predicted.sum())

    return {
        "n_hours": int(len(actual)),
        "abs_error_sum": float(
            np.abs(error).sum()
        ),
        "squared_error_sum": float(
            np.square(error).sum()
        ),
        "error_sum": float(
            error.sum()
        ),
        "event_mae_kw": float(
            np.mean(np.abs(error))
        ),
        "event_rmse_kw": float(
            np.sqrt(
                np.mean(
                    np.square(error)
                )
            )
        ),
        "actual_energy_kwh": actual_energy,
        "predicted_energy_kwh": predicted_energy,
        "event_energy_bias_kwh": float(
            predicted_energy - actual_energy
        ),
        "event_abs_energy_bias_kwh": float(
            abs(
                predicted_energy
                - actual_energy
            )
        ),
    }


def aggregate_metrics(
    events: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for model, group in events.groupby(
        "model",
        sort=False,
    ):
        total_hours = int(
            group["n_hours"].sum()
        )

        actual_energy = float(
            group["actual_energy_kwh"].sum()
        )
        predicted_energy = float(
            group["predicted_energy_kwh"].sum()
        )

        rows.append(
            {
                "method": "cwa",
                "model": model,
                "n_events": len(group),
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
                "signed_energy_bias_pct": (
                    (
                        predicted_energy
                        - actual_energy
                    )
                    / actual_energy
                    * 100.0
                    if actual_energy > 0
                    else np.nan
                ),
                "mean_event_abs_energy_bias_kwh":
                    float(
                        group[
                            "event_abs_energy_bias_kwh"
                        ].mean()
                    ),
                "median_event_abs_energy_bias_kwh":
                    float(
                        group[
                            "event_abs_energy_bias_kwh"
                        ].median()
                    ),
            }
        )

    result = pd.DataFrame(rows)

    result["rank_rmse"] = result[
        "rmse_kw"
    ].rank(
        method="min",
        ascending=True,
    )
    result["rank_mae"] = result[
        "mae_kw"
    ].rank(
        method="min",
        ascending=True,
    )
    result["rank_event_abs_energy_bias"] = result[
        "mean_event_abs_energy_bias_kwh"
    ].rank(
        method="min",
        ascending=True,
    )
    result["rank_abs_signed_energy_bias"] = (
        result["signed_energy_bias_pct"]
        .abs()
        .rank(
            method="min",
            ascending=True,
        )
    )

    result["diagnostic_mean_rank"] = (
        result[
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
        result.sort_values(
            [
                "diagnostic_mean_rank",
                "rmse_kw",
                "mae_kw",
            ]
        )
        .reset_index(drop=True)
    )


def aggregate_donor(
    donor: pd.DataFrame,
) -> dict[str, object]:
    total_hours = int(
        pd.to_numeric(
            donor["n_hours"],
            errors="coerce",
        ).sum()
    )

    actual_energy = float(
        pd.to_numeric(
            donor["actual_energy_kwh"],
            errors="coerce",
        ).sum()
    )
    predicted_energy = float(
        pd.to_numeric(
            donor["predicted_energy_kwh"],
            errors="coerce",
        ).sum()
    )

    return {
        "method": "donor",
        "model": (
            f"pm{DONOR_WINDOW_DAYS}days_"
            f"k{DONOR_K}_{DONOR_AGGREGATION}"
        ),
        "n_events": len(donor),
        "n_hours": total_hours,
        "mae_kw": float(
            donor["abs_error_sum"].sum()
            / total_hours
        ),
        "rmse_kw": float(
            np.sqrt(
                donor["squared_error_sum"].sum()
                / total_hours
            )
        ),
        "signed_bias_kw": float(
            donor["error_sum"].sum()
            / total_hours
        ),
        "signed_energy_bias_pct": (
            (
                predicted_energy
                - actual_energy
            )
            / actual_energy
            * 100.0
            if actual_energy > 0
            else np.nan
        ),
        "mean_event_abs_energy_bias_kwh": float(
            donor[
                "event_abs_energy_bias_kwh"
            ].mean()
        ),
        "median_event_abs_energy_bias_kwh": float(
            donor[
                "event_abs_energy_bias_kwh"
            ].median()
        ),
    }


def paired_event_comparison(
    cwa_events: pd.DataFrame,
    donor: pd.DataFrame,
    *,
    best_model: str,
) -> pd.DataFrame:
    cwa_best = cwa_events.loc[
        cwa_events["model"].eq(best_model)
    ][
        [
            "pseudo_event_id",
            "template_id",
            "target_start",
            "duration_hours",
            "event_mae_kw",
            "event_rmse_kw",
            "event_abs_energy_bias_kwh",
            "event_energy_bias_kwh",
        ]
    ].rename(
        columns={
            "event_mae_kw":
                "cwa_event_mae_kw",
            "event_rmse_kw":
                "cwa_event_rmse_kw",
            "event_abs_energy_bias_kwh":
                "cwa_event_abs_energy_bias_kwh",
            "event_energy_bias_kwh":
                "cwa_event_energy_bias_kwh",
        }
    )

    donor_subset = donor[
        [
            "pseudo_event_id",
            "event_mae_kw",
            "event_rmse_kw",
            "event_abs_energy_bias_kwh",
            "event_energy_bias_kwh",
        ]
    ].rename(
        columns={
            "event_mae_kw":
                "donor_event_mae_kw",
            "event_rmse_kw":
                "donor_event_rmse_kw",
            "event_abs_energy_bias_kwh":
                "donor_event_abs_energy_bias_kwh",
            "event_energy_bias_kwh":
                "donor_event_energy_bias_kwh",
        }
    )

    paired = cwa_best.merge(
        donor_subset,
        on="pseudo_event_id",
        how="inner",
        validate="one_to_one",
    )

    paired["winner_mae"] = np.where(
        paired["cwa_event_mae_kw"]
        < paired["donor_event_mae_kw"],
        "cwa",
        np.where(
            paired["cwa_event_mae_kw"]
            > paired["donor_event_mae_kw"],
            "donor",
            "tie",
        ),
    )

    paired["winner_rmse"] = np.where(
        paired["cwa_event_rmse_kw"]
        < paired["donor_event_rmse_kw"],
        "cwa",
        np.where(
            paired["cwa_event_rmse_kw"]
            > paired["donor_event_rmse_kw"],
            "donor",
            "tie",
        ),
    )

    paired[
        "winner_event_abs_energy_bias"
    ] = np.where(
        paired[
            "cwa_event_abs_energy_bias_kwh"
        ]
        < paired[
            "donor_event_abs_energy_bias_kwh"
        ],
        "cwa",
        np.where(
            paired[
                "cwa_event_abs_energy_bias_kwh"
            ]
            > paired[
                "donor_event_abs_energy_bias_kwh"
            ],
            "donor",
            "tie",
        ),
    )

    return paired


def main() -> int:
    args = parse_args()

    print(
        f"Script version: {SCRIPT_VERSION}"
    )

    try:
        args.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        observed_raw, observed_path = read_observed(
            args.observed_parquet,
            args.observed_csv,
        )
        observed = prepare_observed(
            observed_raw
        )

        weather = read_cwa(
            args.cwa_input
        )

        data = observed.merge(
            weather[
                [
                    "timestamp",
                    "ghi_kwh_m2",
                    "air_temperature_c",
                ]
            ],
            on="timestamp",
            how="left",
            validate="one_to_one",
        )

        if data["ghi_kwh_m2"].isna().any():
            count = int(
                data["ghi_kwh_m2"].isna().sum()
            )
            raise ValueError(
                f"CWA GHI has {count} missing formal hours. "
                "Resolve weather normalization before head-to-head validation."
            )

        targets = prepare_targets(
            args.pseudogap_targets
        )

        donor = prepare_donor_metrics(
            args.donor_event_metrics
        )

        if set(targets["pseudo_event_id"]) != set(
            donor["pseudo_event_id"]
        ):
            raise ValueError(
                "Script-04 target IDs and locked donor event IDs differ. "
                "Head-to-head comparison would not be fair."
            )

        indexed = data.set_index(
            "timestamp",
            drop=False,
        )

        event_rows: list[
            dict[str, object]
        ] = []
        prediction_rows: list[
            dict[str, object]
        ] = []
        parameter_rows: list[
            dict[str, object]
        ] = []

        # Cache each leave-one-day-out fit result because both outage
        # templates on the same date use the same training day exclusion.
        model_cache: dict[
            tuple[pd.Timestamp, str],
            tuple[object, dict[str, float]],
        ] = {}

        for target in targets.itertuples(
            index=False
        ):
            target_start = pd.Timestamp(
                target.target_start
            )
            duration = int(
                target.duration_hours
            )
            target_day = target_start.normalize()

            target_timestamps = pd.date_range(
                target_start,
                periods=duration,
                freq="h",
            )

            if not target_timestamps.isin(
                indexed.index
            ).all():
                raise ValueError(
                    f"Target pseudo-gap incomplete: {target_start}"
                )

            target_frame = indexed.loc[
                target_timestamps
            ].copy()

            actual = target_frame[
                "observed_pv_kw"
            ].to_numpy(
                dtype="float64"
            )

            train = training_rows(
                data,
                target_day=target_day,
            )

            for model_name in MODEL_NAMES:
                model_function = MODEL_FUNCTIONS[
                    model_name
                ]

                prediction, parameters = (
                    model_function(
                        train,
                        target_frame,
                    )
                )

                metrics = event_metrics(
                    actual,
                    prediction,
                )

                row: dict[str, object] = {
                    "pseudo_event_id":
                        target.pseudo_event_id,
                    "template_id":
                        target.template_id,
                    "target_start":
                        target_start,
                    "target_day":
                        target_day,
                    "duration_hours":
                        duration,
                    "model":
                        model_name,
                    "training_rows":
                        len(train),
                }
                row.update(metrics)
                event_rows.append(row)

                parameter_rows.append(
                    {
                        "pseudo_event_id":
                            target.pseudo_event_id,
                        "target_day":
                            target_day,
                        "model":
                            model_name,
                        **parameters,
                    }
                )

                for timestamp, actual_value, predicted_value, ghi_value, temp_value in zip(
                    target_timestamps,
                    actual,
                    prediction,
                    target_frame[
                        "ghi_kwh_m2"
                    ].to_numpy(
                        dtype="float64"
                    ),
                    target_frame[
                        "air_temperature_c"
                    ].to_numpy(
                        dtype="float64"
                    ),
                ):
                    prediction_rows.append(
                        {
                            "pseudo_event_id":
                                target.pseudo_event_id,
                            "template_id":
                                target.template_id,
                            "model":
                                model_name,
                            "timestamp":
                                timestamp,
                            "actual_pv_kw":
                                actual_value,
                            "predicted_pv_kw":
                                predicted_value,
                            "ghi_kwh_m2":
                                ghi_value,
                            "air_temperature_c":
                                temp_value,
                        }
                    )

        cwa_events = pd.DataFrame(
            event_rows
        )
        predictions = pd.DataFrame(
            prediction_rows
        )
        parameters = pd.DataFrame(
            parameter_rows
        )

        cwa_ranking = aggregate_metrics(
            cwa_events
        )

        best_model = str(
            cwa_ranking.iloc[0]["model"]
        )

        donor_summary = aggregate_donor(
            donor
        )

        best_cwa_summary = (
            cwa_ranking.loc[
                cwa_ranking[
                    "model"
                ].eq(best_model)
            ]
            .iloc[0]
            .to_dict()
        )

        comparison = pd.DataFrame(
            [
                donor_summary,
                {
                    key: value
                    for key, value
                    in best_cwa_summary.items()
                    if not str(key).startswith(
                        "rank_"
                    )
                    and key
                    != "diagnostic_mean_rank"
                },
            ]
        )

        paired = paired_event_comparison(
            cwa_events,
            donor,
            best_model=best_model,
        )

        paired_summary = (
            paired.groupby(
                "template_id",
                as_index=False,
            )
            .agg(
                n_events=(
                    "pseudo_event_id",
                    "count",
                ),
                cwa_mae_wins=(
                    "winner_mae",
                    lambda s: int(
                        (s == "cwa").sum()
                    ),
                ),
                donor_mae_wins=(
                    "winner_mae",
                    lambda s: int(
                        (s == "donor").sum()
                    ),
                ),
                cwa_rmse_wins=(
                    "winner_rmse",
                    lambda s: int(
                        (s == "cwa").sum()
                    ),
                ),
                donor_rmse_wins=(
                    "winner_rmse",
                    lambda s: int(
                        (s == "donor").sum()
                    ),
                ),
                cwa_energy_wins=(
                    "winner_event_abs_energy_bias",
                    lambda s: int(
                        (s == "cwa").sum()
                    ),
                ),
                donor_energy_wins=(
                    "winner_event_abs_energy_bias",
                    lambda s: int(
                        (s == "donor").sum()
                    ),
                ),
            )
        )

        overall_paired = pd.DataFrame(
            [
                {
                    "template_id": "ALL",
                    "n_events": len(paired),
                    "cwa_mae_wins": int(
                        (
                            paired["winner_mae"]
                            == "cwa"
                        ).sum()
                    ),
                    "donor_mae_wins": int(
                        (
                            paired["winner_mae"]
                            == "donor"
                        ).sum()
                    ),
                    "cwa_rmse_wins": int(
                        (
                            paired["winner_rmse"]
                            == "cwa"
                        ).sum()
                    ),
                    "donor_rmse_wins": int(
                        (
                            paired["winner_rmse"]
                            == "donor"
                        ).sum()
                    ),
                    "cwa_energy_wins": int(
                        (
                            paired[
                                "winner_event_abs_energy_bias"
                            ]
                            == "cwa"
                        ).sum()
                    ),
                    "donor_energy_wins": int(
                        (
                            paired[
                                "winner_event_abs_energy_bias"
                            ]
                            == "donor"
                        ).sum()
                    ),
                }
            ]
        )

        paired_summary = pd.concat(
            [
                paired_summary,
                overall_paired,
            ],
            ignore_index=True,
        )

        # Main decision diagnostics.
        donor_mae = float(
            donor_summary["mae_kw"]
        )
        donor_rmse = float(
            donor_summary["rmse_kw"]
        )
        donor_energy = float(
            donor_summary[
                "mean_event_abs_energy_bias_kwh"
            ]
        )

        cwa_mae = float(
            best_cwa_summary["mae_kw"]
        )
        cwa_rmse = float(
            best_cwa_summary["rmse_kw"]
        )
        cwa_energy = float(
            best_cwa_summary[
                "mean_event_abs_energy_bias_kwh"
            ]
        )

        cwa_better_count = sum(
            [
                cwa_mae < donor_mae,
                cwa_rmse < donor_rmse,
                cwa_energy < donor_energy,
            ]
        )

        if cwa_better_count == 3:
            decision_flag = (
                "CWA_BETTER_ON_ALL_PRIMARY_ERROR_METRICS"
            )
        elif cwa_better_count == 0:
            decision_flag = (
                "DONOR_BETTER_ON_ALL_PRIMARY_ERROR_METRICS"
            )
        else:
            decision_flag = (
                "MIXED_TRADEOFF_REQUIRES_REVIEW"
            )

        cwa_ranking_path = (
            args.output_dir
            / "pv_cwa_shortgap_model_ranking_v7.csv"
        )
        cwa_event_path = (
            args.output_dir
            / "pv_cwa_shortgap_event_metrics_v7.csv"
        )
        prediction_path = (
            args.output_dir
            / "pv_cwa_shortgap_predictions_v7.csv"
        )
        parameter_path = (
            args.output_dir
            / "pv_cwa_shortgap_fit_parameters_v7.csv"
        )
        comparison_path = (
            args.output_dir
            / "pv_donor_vs_cwa_shortgap_summary_v7.csv"
        )
        paired_path = (
            args.output_dir
            / "pv_donor_vs_cwa_shortgap_paired_events_v7.csv"
        )
        paired_summary_path = (
            args.output_dir
            / "pv_donor_vs_cwa_shortgap_paired_summary_v7.csv"
        )
        summary_path = (
            args.output_dir
            / "pv_donor_vs_cwa_shortgap_validation_summary_v7.txt"
        )

        cwa_ranking.to_csv(
            cwa_ranking_path,
            index=False,
            encoding="utf-8-sig",
        )
        cwa_events.to_csv(
            cwa_event_path,
            index=False,
            encoding="utf-8-sig",
        )
        predictions.to_csv(
            prediction_path,
            index=False,
            encoding="utf-8-sig",
        )
        parameters.to_csv(
            parameter_path,
            index=False,
            encoding="utf-8-sig",
        )
        comparison.to_csv(
            comparison_path,
            index=False,
            encoding="utf-8-sig",
        )
        paired.to_csv(
            paired_path,
            index=False,
            encoding="utf-8-sig",
        )
        paired_summary.to_csv(
            paired_summary_path,
            index=False,
            encoding="utf-8-sig",
        )

        summary_lines = [
            "NTUST v7 PV Short-Gap Donor vs CWA Validation",
            f"Script version: {SCRIPT_VERSION}",
            f"Observed input: {observed_path}",
            f"CWA input: {args.cwa_input}",
            f"Script-04 pseudo-gap targets: {args.pseudogap_targets}",
            "",
            "Purpose",
            "- Compare CWA-based short-gap PV reconstruction with the "
            "validated donor method on the EXACT SAME Script-04 pseudo-events.",
            "- No production PV values are changed.",
            "- Long pre_system/missing_winter PV is outside this test.",
            "",
            "Leakage guardrail",
            "- For every pseudo-event, the entire target calendar day is "
            "excluded from CWA-to-PV model fitting.",
            "- CODiS exact 23:59 daily-end labels are first normalized "
            "to next-day 00:00, then hour-ending timestamps are shifted "
            "back one hour to the v7 interval-start convention.",
            f"- CODiS 23:59 labels adjusted: {int(weather.attrs.get('adjusted_2359_count', 0)):,}",
            f"- Final CWA interval-start range: "
            f"{weather['timestamp'].min()} to {weather['timestamp'].max()}",
            "",
            "CWA models tested",
            cwa_ranking.to_string(index=False),
            "",
            f"Best CWA model by diagnostic mean rank: {best_model}",
            "",
            "Head-to-head aggregate comparison",
            comparison.to_string(index=False),
            "",
            "Paired event wins",
            paired_summary.to_string(index=False),
            "",
            "Decision flag",
            f"- {decision_flag}",
            "",
            "Interpretation rule",
            "- Primary short-gap accuracy metrics are MAE, RMSE, and mean "
            "event absolute energy bias.",
            "- Signed energy bias is also reported and must be checked for "
            "systematic over/under-estimation.",
            "- Do not replace the donor method solely because one metric is "
            "slightly better; review aggregate errors, paired-event wins, "
            "template-specific behavior, and bias together.",
            "- If CWA is clearly better across the same pseudo-gap set, "
            "production short-gap reconstruction can be reconsidered.",
            "- If donor remains better or the trade-off is mixed with only "
            "small CWA gains, retain donor and keep CWA for the winter "
            "sensitivity branch.",
            "",
            "Outputs",
            f"- {cwa_ranking_path}",
            f"- {cwa_event_path}",
            f"- {prediction_path}",
            f"- {parameter_path}",
            f"- {comparison_path}",
            f"- {paired_path}",
            f"- {paired_summary_path}",
            f"- {summary_path}",
        ]

        summary_path.write_text(
            "\n".join(summary_lines) + "\n",
            encoding="utf-8",
        )

        print(
            "\n".join(summary_lines)
        )
        print()
        print(
            "Script 04b completed. No real PV values were changed."
        )
        print(
            "Next step: use the donor-vs-CWA results to decide the "
            "short-gap production rule before Script 05."
        )

        return 0

    except Exception as exc:
        print(
            f"Script 04b failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
