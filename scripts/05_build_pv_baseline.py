from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7-pv-baseline-cwa-shortgap-2026-08-16"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_HOURS = 8760

SELECTED_CWA_MODEL = "hourly_ghi_ratio_median"

DAYLIGHT_GHI_THRESHOLD = 0.01
RATIO_FIT_GHI_THRESHOLD = 0.05

LONG_UNAVAILABLE_STATUSES = {
    "pre_system",
    "missing_winter",
}

EXPECTED_SHORT_RECONSTRUCTED_HOURS = 10
EXPECTED_LONG_UNAVAILABLE_HOURS = 1463

RECONSTRUCTION_METHOD = (
    "cwa_hourly_ghi_ratio_median_leave_target_day_out"
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()

    parser = argparse.ArgumentParser(
        description=(
            "Build the v7 NTUST planning PV baseline. "
            "Short outage-contaminated PV intervals are reconstructed "
            "using the CWA hourly-GHI ratio-median method selected by "
            "Script 04b. Long pre_system/missing_winter intervals remain "
            "zero-availability in the mainline."
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
        "--cwa-model-ranking",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pv_cwa_shortgap_model_ranking_v7.csv"
        ),
    )

    parser.add_argument(
        "--donor-vs-cwa-summary",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pv_donor_vs_cwa_shortgap_summary_v7.csv"
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


def parse_timestamp(series: pd.Series) -> pd.Series:
    result = pd.to_datetime(
        series,
        errors="coerce",
    )

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


def read_observed(
    parquet_path: Path,
    csv_path: Path,
) -> tuple[pd.DataFrame, Path]:
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path), parquet_path
        except (
            ImportError,
            ModuleNotFoundError,
            ValueError,
        ):
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
            "Observed input missing required columns: "
            f"{sorted(missing)}"
        )

    result = df.copy()

    result["timestamp"] = parse_timestamp(
        result["timestamp"]
    )

    result["observed_pv_kw"] = numeric_clean(
        result["observed_pv_kw"]
    )

    if result["timestamp"].isna().any():
        raise ValueError(
            "Observed input has unparseable timestamps."
        )

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
            f"Observed formal rows={len(result):,}; "
            f"expected {EXPECTED_HOURS:,}."
        )

    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )

    if not pd.DatetimeIndex(
        result["timestamp"]
    ).equals(expected):
        raise ValueError(
            "Observed timeline is not the exact v7 "
            "8,760-hour interval-start timeline."
        )

    if result["observed_pv_kw"].isna().any():
        count = int(
            result["observed_pv_kw"].isna().sum()
        )
        raise ValueError(
            f"observed_pv_kw has {count} missing values."
        )

    if (result["observed_pv_kw"] < 0).any():
        count = int(
            (result["observed_pv_kw"] < 0).sum()
        )
        raise ValueError(
            f"observed_pv_kw has {count} negative values."
        )

    result["outage_contaminated_flag"] = parse_bool(
        result["outage_contaminated_flag"],
        fallback=pd.Series(
            False,
            index=result.index,
        ),
    )

    return result


def read_cwa(
    path: Path,
) -> tuple[pd.DataFrame, dict[str, object]]:
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

    missing = required.difference(
        weather.columns
    )

    if missing:
        raise ValueError(
            f"CWA input missing columns: {sorted(missing)}"
        )

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
            "CWA contains unexpected non-hourly timestamps, "
            f"e.g. {examples}"
        )

    weather["timestamp_raw_end"] = (
        weather["timestamp_raw"]
    )

    weather.loc[
        mask_2359,
        "timestamp_raw_end",
    ] = (
        weather.loc[
            mask_2359,
            "timestamp_raw",
        ]
        + pd.Timedelta(minutes=1)
    )

    weather["timestamp"] = (
        weather["timestamp_raw_end"]
        - pd.Timedelta(hours=1)
    )

    weather["ghi_mj_m2"] = numeric_clean(
        weather[
            "global_solar_radiation_raw"
        ]
    )

    weather.loc[
        weather["ghi_mj_m2"] < 0,
        "ghi_mj_m2",
    ] = np.nan

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
        .drop_duplicates(
            "timestamp",
            keep="last",
        )
        .reset_index(drop=True)
    )

    if len(weather) != EXPECTED_HOURS:
        raise ValueError(
            f"CWA formal rows={len(weather):,}; "
            f"expected {EXPECTED_HOURS:,}."
        )

    expected = pd.date_range(
        FORMAL_START,
        FORMAL_END_EXCLUSIVE,
        freq="h",
        inclusive="left",
    )

    if not pd.DatetimeIndex(
        weather["timestamp"]
    ).equals(expected):
        raise ValueError(
            "CWA timeline is not aligned to the exact "
            "v7 interval-start 8,760-hour timeline."
        )

    if weather["ghi_kwh_m2"].isna().any():
        count = int(
            weather["ghi_kwh_m2"].isna().sum()
        )
        raise ValueError(
            f"CWA GHI has {count} missing formal hours."
        )

    metadata = {
        "adjusted_2359_count":
            int(mask_2359.sum()),
        "timestamp_start":
            weather["timestamp"].min(),
        "timestamp_end":
            weather["timestamp"].max(),
    }

    return weather, metadata


def verify_script04b_selection(
    ranking_path: Path,
    comparison_path: Path,
) -> dict[str, float]:
    if not ranking_path.exists():
        raise FileNotFoundError(
            "Script-04b CWA ranking is required:\n"
            f"{ranking_path}"
        )

    if not comparison_path.exists():
        raise FileNotFoundError(
            "Script-04b donor-vs-CWA summary is required:\n"
            f"{comparison_path}"
        )

    ranking = pd.read_csv(
        ranking_path
    )

    required_ranking = {
        "model",
        "mae_kw",
        "rmse_kw",
        "signed_energy_bias_pct",
        "mean_event_abs_energy_bias_kwh",
        "diagnostic_mean_rank",
    }

    missing = required_ranking.difference(
        ranking.columns
    )

    if missing:
        raise ValueError(
            "CWA ranking missing columns: "
            f"{sorted(missing)}"
        )

    ranking = ranking.copy()

    for column in [
        "mae_kw",
        "rmse_kw",
        "signed_energy_bias_pct",
        "mean_event_abs_energy_bias_kwh",
        "diagnostic_mean_rank",
    ]:
        ranking[column] = pd.to_numeric(
            ranking[column],
            errors="coerce",
        )

    if ranking[
        [
            "mae_kw",
            "rmse_kw",
            "signed_energy_bias_pct",
            "mean_event_abs_energy_bias_kwh",
            "diagnostic_mean_rank",
        ]
    ].isna().any().any():
        raise ValueError(
            "CWA ranking contains invalid numeric values."
        )

    best_rank = float(
        ranking[
            "diagnostic_mean_rank"
        ].min()
    )

    best_rows = ranking.loc[
        np.isclose(
            ranking[
                "diagnostic_mean_rank"
            ],
            best_rank,
            rtol=0.0,
            atol=1e-12,
        )
    ].copy()

    if len(best_rows) != 1:
        raise ValueError(
            "Script-04b does not identify one unique "
            "best CWA model."
        )

    best_model = str(
        best_rows.iloc[0]["model"]
    )

    if best_model != SELECTED_CWA_MODEL:
        raise ValueError(
            "Production CWA model does not match "
            "Script-04b empirical selection: "
            f"ranking best={best_model}, "
            f"script selected={SELECTED_CWA_MODEL}."
        )

    comparison = pd.read_csv(
        comparison_path
    )

    required_comparison = {
        "method",
        "model",
        "mae_kw",
        "rmse_kw",
        "signed_energy_bias_pct",
        "mean_event_abs_energy_bias_kwh",
    }

    missing = required_comparison.difference(
        comparison.columns
    )

    if missing:
        raise ValueError(
            "Donor-vs-CWA summary missing columns: "
            f"{sorted(missing)}"
        )

    for column in [
        "mae_kw",
        "rmse_kw",
        "signed_energy_bias_pct",
        "mean_event_abs_energy_bias_kwh",
    ]:
        comparison[column] = pd.to_numeric(
            comparison[column],
            errors="coerce",
        )

    cwa_rows = comparison.loc[
        comparison["method"].astype(str).eq("cwa")
        & comparison["model"].astype(str).eq(
            SELECTED_CWA_MODEL
        )
    ]

    donor_rows = comparison.loc[
        comparison["method"].astype(str).eq(
            "donor"
        )
    ]

    if (
        len(cwa_rows) != 1
        or len(donor_rows) != 1
    ):
        raise ValueError(
            "Cannot uniquely identify the CWA and donor "
            "head-to-head summary rows."
        )

    cwa = cwa_rows.iloc[0]
    donor = donor_rows.iloc[0]

    primary_metrics = (
        "mae_kw",
        "rmse_kw",
        "mean_event_abs_energy_bias_kwh",
    )

    if not all(
        float(cwa[metric])
        < float(donor[metric])
        for metric in primary_metrics
    ):
        raise ValueError(
            "Selected CWA model does not outperform donor "
            "on all three primary Script-04b error metrics."
        )

    return {
        "cwa_mae_kw":
            float(cwa["mae_kw"]),
        "cwa_rmse_kw":
            float(cwa["rmse_kw"]),
        "cwa_signed_energy_bias_pct":
            float(
                cwa[
                    "signed_energy_bias_pct"
                ]
            ),
        "cwa_mean_event_abs_energy_bias_kwh":
            float(
                cwa[
                    "mean_event_abs_energy_bias_kwh"
                ]
            ),
        "donor_mae_kw":
            float(donor["mae_kw"]),
        "donor_rmse_kw":
            float(donor["rmse_kw"]),
        "donor_signed_energy_bias_pct":
            float(
                donor[
                    "signed_energy_bias_pct"
                ]
            ),
        "donor_mean_event_abs_energy_bias_kwh":
            float(
                donor[
                    "mean_event_abs_energy_bias_kwh"
                ]
            ),
    }


def identify_outage_events(
    df: pd.DataFrame,
) -> list[pd.DataFrame]:
    outage = df.loc[
        df[
            "outage_contaminated_flag"
        ]
    ].copy()

    if outage.empty:
        raise ValueError(
            "No outage-contaminated PV hours were found."
        )

    outage = (
        outage.sort_values("timestamp")
        .copy()
    )

    new_group = (
        outage["timestamp"]
        .diff()
        .ne(
            pd.Timedelta(hours=1)
        )
    )

    outage[
        "_outage_group"
    ] = new_group.cumsum()

    groups: list[
        pd.DataFrame
    ] = []

    for _, group in outage.groupby(
        "_outage_group",
        sort=False,
    ):
        event = (
            group.drop(
                columns=[
                    "_outage_group",
                ]
            )
            .copy()
            .reset_index()
            .rename(
                columns={
                    "index":
                        "source_row_index"
                }
            )
        )

        start = event[
            "timestamp"
        ].iloc[0]
        end = event[
            "timestamp"
        ].iloc[-1]

        if (
            start.normalize()
            != end.normalize()
        ):
            raise ValueError(
                "Current validated short-gap CWA method "
                "assumes a same-day outage block, but an "
                f"event crosses midnight: {start} to {end}."
            )

        groups.append(event)

    return groups


def fit_hourly_ratio_model(
    data: pd.DataFrame,
    *,
    target_day: pd.Timestamp,
) -> dict[str, object]:
    target_day = pd.Timestamp(
        target_day
    ).normalize()

    train = data.loc[
        data["pv_status"].astype(str).eq(
            "valid"
        )
        & (
            ~data[
                "outage_contaminated_flag"
            ].astype(bool)
        )
        & data["observed_pv_kw"].notna()
        & data["ghi_kwh_m2"].notna()
        & data["timestamp"].dt.normalize().ne(
            target_day
        )
    ].copy()

    train["hour"] = (
        train["timestamp"].dt.hour
    )

    fit = train.loc[
        train["ghi_kwh_m2"]
        > RATIO_FIT_GHI_THRESHOLD
    ].copy()

    if fit.empty:
        raise ValueError(
            f"No valid GHI-to-PV ratio rows remain "
            f"for target day {target_day}."
        )

    fit["pv_per_ghi"] = (
        fit["observed_pv_kw"]
        / fit["ghi_kwh_m2"]
    )

    global_ratio = float(
        fit["pv_per_ghi"].median()
    )

    hourly_ratio = (
        fit.groupby("hour")[
            "pv_per_ghi"
        ]
        .median()
        .to_dict()
    )

    pv_cap_kw = float(
        train[
            "observed_pv_kw"
        ].max()
    )

    return {
        "target_day":
            target_day,
        "training_rows":
            int(len(train)),
        "ratio_fit_rows":
            int(len(fit)),
        "global_ratio":
            global_ratio,
        "hourly_ratio":
            hourly_ratio,
        "pv_cap_kw":
            pv_cap_kw,
    }


def predict_event(
    event_frame: pd.DataFrame,
    model: dict[str, object],
) -> np.ndarray:
    target_hours = (
        event_frame[
            "timestamp"
        ]
        .dt.hour
    )

    global_ratio = float(
        model["global_ratio"]
    )

    hourly_ratio = model[
        "hourly_ratio"
    ]

    ratios = (
        target_hours
        .map(hourly_ratio)
        .fillna(global_ratio)
        .to_numpy(
            dtype="float64"
        )
    )

    ghi = event_frame[
        "ghi_kwh_m2"
    ].to_numpy(
        dtype="float64"
    )

    prediction = (
        ratios * ghi
    )

    prediction = np.where(
        np.isfinite(prediction),
        prediction,
        0.0,
    )

    prediction = np.maximum(
        prediction,
        0.0,
    )

    prediction = np.minimum(
        prediction,
        float(
            model["pv_cap_kw"]
        ),
    )

    prediction = np.where(
        ghi <= DAYLIGHT_GHI_THRESHOLD,
        0.0,
        prediction,
    )

    return prediction


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

    print(
        f"Script version: {SCRIPT_VERSION}"
    )

    try:
        args.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        args.audit_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        validation = (
            verify_script04b_selection(
                args.cwa_model_ranking,
                args.donor_vs_cwa_summary,
            )
        )

        observed_raw, observed_path = (
            read_observed(
                args.observed_parquet,
                args.observed_csv,
            )
        )

        observed = prepare_observed(
            observed_raw
        )

        weather, weather_meta = (
            read_cwa(
                args.cwa_input
            )
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

        if data[
            "ghi_kwh_m2"
        ].isna().any():
            count = int(
                data[
                    "ghi_kwh_m2"
                ].isna().sum()
            )
            raise ValueError(
                f"Merged CWA GHI has {count} missing hours."
            )

        output = data.copy()

        output[
            "pv_available_kw"
        ] = output[
            "observed_pv_kw"
        ].astype(
            "float64"
        )

        output[
            "pv_reconstructed"
        ] = False

        output[
            "pv_reconstruction_method"
        ] = "observed"

        output[
            "pv_long_unavailable_assumption"
        ] = False

        output[
            "pv_cwa_model"
        ] = pd.NA

        long_mask = (
            output[
                "pv_status"
            ]
            .astype(str)
            .isin(
                LONG_UNAVAILABLE_STATUSES
            )
        )

        output.loc[
            long_mask,
            "pv_available_kw",
        ] = 0.0

        output.loc[
            long_mask,
            "pv_reconstruction_method",
        ] = "unavailable_zero_mainline"

        output.loc[
            long_mask,
            "pv_long_unavailable_assumption",
        ] = True

        outage_events = (
            identify_outage_events(
                output
            )
        )

        applied_rows: list[
            dict[str, object]
        ] = []

        fit_rows: list[
            dict[str, object]
        ] = []

        for event_id, event in enumerate(
            outage_events,
            start=1,
        ):
            outage_start = pd.Timestamp(
                event[
                    "timestamp"
                ].iloc[0]
            )

            outage_end = pd.Timestamp(
                event[
                    "timestamp"
                ].iloc[-1]
            )

            target_day = (
                outage_start.normalize()
            )

            model = (
                fit_hourly_ratio_model(
                    output,
                    target_day=target_day,
                )
            )

            target_indices = (
                event[
                    "source_row_index"
                ]
                .astype(int)
                .to_numpy()
            )

            event_frame = (
                output.loc[
                    target_indices
                ]
                .copy()
            )

            prediction = (
                predict_event(
                    event_frame,
                    model,
                )
            )

            if (
                len(prediction)
                != len(event)
            ):
                raise RuntimeError(
                    "CWA prediction length does not match "
                    "outage duration."
                )

            if not np.isfinite(
                prediction
            ).all():
                raise RuntimeError(
                    "CWA PV reconstruction contains "
                    "non-finite values."
                )

            if np.any(
                prediction < 0
            ):
                raise RuntimeError(
                    "CWA PV reconstruction contains "
                    "negative values."
                )

            output.loc[
                target_indices,
                "pv_available_kw",
            ] = prediction

            output.loc[
                target_indices,
                "pv_reconstructed",
            ] = True

            output.loc[
                target_indices,
                "pv_reconstruction_method",
            ] = RECONSTRUCTION_METHOD

            output.loc[
                target_indices,
                "pv_cwa_model",
            ] = SELECTED_CWA_MODEL

            fit_rows.append(
                {
                    "event_id":
                        event_id,
                    "target_day":
                        target_day,
                    "outage_start":
                        outage_start,
                    "outage_end_inclusive":
                        outage_end,
                    "duration_hours":
                        len(event),
                    "model":
                        SELECTED_CWA_MODEL,
                    "training_rows":
                        model[
                            "training_rows"
                        ],
                    "ratio_fit_rows":
                        model[
                            "ratio_fit_rows"
                        ],
                    "global_ratio":
                        model[
                            "global_ratio"
                        ],
                    "pv_cap_kw":
                        model[
                            "pv_cap_kw"
                        ],
                }
            )

            for row_index, predicted_value in zip(
                target_indices,
                prediction,
            ):
                applied_rows.append(
                    {
                        "event_id":
                            event_id,
                        "outage_start":
                            outage_start,
                        "outage_end_inclusive":
                            outage_end,
                        "duration_hours":
                            len(event),
                        "target_timestamp":
                            output.at[
                                row_index,
                                "timestamp",
                            ],
                        "observed_pv_kw":
                            output.at[
                                row_index,
                                "observed_pv_kw",
                            ],
                        "ghi_kwh_m2":
                            output.at[
                                row_index,
                                "ghi_kwh_m2",
                            ],
                        "air_temperature_c":
                            output.at[
                                row_index,
                                "air_temperature_c",
                            ],
                        "pv_available_kw":
                            float(
                                predicted_value
                            ),
                        "model":
                            SELECTED_CWA_MODEL,
                        "method":
                            RECONSTRUCTION_METHOD,
                    }
                )

        reconstructed_count = int(
            output[
                "pv_reconstructed"
            ].sum()
        )

        long_count = int(
            output[
                "pv_long_unavailable_assumption"
            ].sum()
        )

        if (
            reconstructed_count
            != EXPECTED_SHORT_RECONSTRUCTED_HOURS
        ):
            raise ValueError(
                f"Short reconstructed PV hours="
                f"{reconstructed_count}; expected "
                f"{EXPECTED_SHORT_RECONSTRUCTED_HOURS}."
            )

        if (
            long_count
            != EXPECTED_LONG_UNAVAILABLE_HOURS
        ):
            raise ValueError(
                f"Long unavailable PV hours="
                f"{long_count}; expected "
                f"{EXPECTED_LONG_UNAVAILABLE_HOURS}."
            )

        if output[
            "pv_available_kw"
        ].isna().any():
            count = int(
                output[
                    "pv_available_kw"
                ].isna().sum()
            )
            raise ValueError(
                f"pv_available_kw has {count} missing values."
            )

        if (
            output[
                "pv_available_kw"
            ] < 0
        ).any():
            count = int(
                (
                    output[
                        "pv_available_kw"
                    ]
                    < 0
                ).sum()
            )
            raise ValueError(
                f"pv_available_kw has {count} negative values."
            )

        if not (
            output.loc[
                long_mask,
                "pv_available_kw",
            ]
            .eq(0.0)
            .all()
        ):
            raise ValueError(
                "Long unavailable PV intervals are not all "
                "zero in the mainline."
            )

        unchanged_mask = (
            ~output[
                "outage_contaminated_flag"
            ]
            & ~long_mask
        )

        max_difference = float(
            np.abs(
                output.loc[
                    unchanged_mask,
                    "pv_available_kw",
                ].to_numpy(
                    dtype=float
                )
                - output.loc[
                    unchanged_mask,
                    "observed_pv_kw",
                ].to_numpy(
                    dtype=float
                )
            ).max()
        )

        if max_difference > 0.0:
            raise ValueError(
                "PV baseline differs from observed PV outside "
                "short-outage/long-unavailable intervals."
            )

        output[
            "observed_pv_kwh"
        ] = output[
            "observed_pv_kw"
        ]

        output[
            "pv_available_kwh"
        ] = output[
            "pv_available_kw"
        ]

        csv_path = (
            args.output_dir
            / "pv_annual_baseline.csv"
        )

        parquet_path = (
            args.output_dir
            / "pv_annual_baseline.parquet"
        )

        applied_path = (
            args.audit_dir
            / "pv_reconstruction_applied_v7.csv"
        )

        fit_path = (
            args.audit_dir
            / "pv_cwa_production_fit_v7.csv"
        )

        summary_path = (
            args.audit_dir
            / "pv_reconstruction_summary_v7.txt"
        )

        output.to_csv(
            csv_path,
            index=False,
            encoding="utf-8-sig",
        )

        parquet_written = (
            write_parquet_if_available(
                output,
                parquet_path,
            )
        )

        applied = pd.DataFrame(
            applied_rows
        )

        fits = pd.DataFrame(
            fit_rows
        )

        applied.to_csv(
            applied_path,
            index=False,
            encoding="utf-8-sig",
        )

        fits.to_csv(
            fit_path,
            index=False,
            encoding="utf-8-sig",
        )

        event_summary = (
            applied.groupby(
                [
                    "event_id",
                    "outage_start",
                    "outage_end_inclusive",
                    "duration_hours",
                    "model",
                    "method",
                ],
                as_index=False,
            )
            .agg(
                observed_event_energy_kwh=(
                    "observed_pv_kw",
                    "sum",
                ),
                reconstructed_event_energy_kwh=(
                    "pv_available_kw",
                    "sum",
                ),
                mean_event_ghi_kwh_m2=(
                    "ghi_kwh_m2",
                    "mean",
                ),
            )
        )

        summary_lines = [
            "NTUST v7 PV Planning-Baseline Reconstruction",
            f"Script version: {SCRIPT_VERSION}",
            f"Observed input: {observed_path}",
            f"CWA input: {args.cwa_input}",
            "",
            "Locked short-gap production method",
            f"- Model: {SELECTED_CWA_MODEL}",
            f"- Method label: {RECONSTRUCTION_METHOD}",
            "- For each real outage event, the entire target calendar day "
            "is excluded from CWA-to-PV fitting, matching Script 04b.",
            "- Hour-specific median PV/GHI ratios are estimated from valid "
            "non-outage observations; a global median ratio is the fallback.",
            "",
            "Script-04b head-to-head evidence",
            f"- CWA MAE: {validation['cwa_mae_kw']:.6f} kW",
            f"- Donor MAE: {validation['donor_mae_kw']:.6f} kW",
            f"- CWA RMSE: {validation['cwa_rmse_kw']:.6f} kW",
            f"- Donor RMSE: {validation['donor_rmse_kw']:.6f} kW",
            f"- CWA signed energy bias: "
            f"{validation['cwa_signed_energy_bias_pct']:.6f} %",
            f"- Donor signed energy bias: "
            f"{validation['donor_signed_energy_bias_pct']:.6f} %",
            f"- CWA mean event absolute energy bias: "
            f"{validation['cwa_mean_event_abs_energy_bias_kwh']:.6f} kWh",
            f"- Donor mean event absolute energy bias: "
            f"{validation['donor_mean_event_abs_energy_bias_kwh']:.6f} kWh",
            "",
            "CWA timestamp normalization",
            f"- CODiS 23:59 labels adjusted: "
            f"{weather_meta['adjusted_2359_count']:,}",
            f"- Final interval-start range: "
            f"{weather_meta['timestamp_start']} to "
            f"{weather_meta['timestamp_end']}",
            "",
            "Formal case year",
            f"- Rows: {len(output):,}",
            f"- Start: {output['timestamp'].min()}",
            f"- End: {output['timestamp'].max()}",
            f"- Short outage-reconstructed PV hours: "
            f"{reconstructed_count}",
            f"- Long unavailable PV hours assigned zero: "
            f"{long_count}",
            "- Original observed_pv_kw is preserved unchanged.",
            "",
            "Applied short outage events",
            event_summary.to_string(index=False),
            "",
            "Long unavailable mainline treatment",
            "- pv_status in {pre_system, missing_winter}: "
            "pv_available_kw = 0.",
            "- These hours are NOT classified as reconstructed PV.",
            "- CWA long-block reconstruction remains a separate "
            "winter sensitivity question and is not inferred from "
            "the short-gap validation.",
            "",
            "Validation checks",
            "- Formal 8,760-hour timeline: PASSED",
            "- pv_available_kw missing values: 0",
            "- pv_available_kw negative values: 0",
            "- Valid non-outage observed PV preserved: PASSED",
            f"- Expected short reconstructed hours "
            f"({EXPECTED_SHORT_RECONSTRUCTED_HOURS}): PASSED",
            f"- Expected long-unavailable zero hours "
            f"({EXPECTED_LONG_UNAVAILABLE_HOURS}): PASSED",
            "",
            "Outputs",
            f"- {csv_path}",
            (
                f"- {parquet_path}"
                if parquet_written
                else "- Parquet skipped "
                "(pyarrow/fastparquet unavailable)"
            ),
            f"- {applied_path}",
            f"- {fit_path}",
            f"- {summary_path}",
        ]

        summary_path.write_text(
            "\n".join(
                summary_lines
            )
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
            "Script 05 completed. "
            "Short outage PV uses the empirically selected "
            "CWA method; long unavailable PV remains zero "
            "in the mainline."
        )

        return 0

    except Exception as exc:
        print(
            f"Script 05 failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
