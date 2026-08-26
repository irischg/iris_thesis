#!/usr/bin/env python3
"""
14a_build_production_economic_interface.py

NTUST thesis v7.2 — production economic-interface preflight.

Purpose
-------
Convert the methodologically closed v7.2 economic/tariff decisions into one
machine-readable pre-EOB interface without running any sizing optimization.

This script consumes already-audited upstream artifacts and:

1) routes the PNNL 10 MW full package to MAINLINE;
2) routes the PNNL 1 MW full package to COST-SCALE SENSITIVITY;
3) preserves the audited Taipower tariff registry in raw nominal NTD;
4) creates a separate optimization-facing Taipower tariff layer in constant
   NTD-2023 using DGBAS annual-average CPI normalization;
5) derives CRF from r=5% and n=20 years (never hard-codes CRF as the source);
6) recomputes kappa from Script-08 H_m/B_m calibration pairs;
7) creates the v7.2 12-field production parameter registry;
8) blocks known legacy cost/degradation contamination;
9) writes a JSON/TXT preflight audit and exits non-zero on any failed gate.

It deliberately DOES NOT:
- run Gurobi or solve EOB / Layer A;
- choose the cost bracket from optimized BESS power;
- alter the raw 13b Taipower tariff registry;
- re-run bill regression;
- apply CRF to annual FOM or C_rep;
- treat non-summer peak as a zero-price period;
- add a separate subsidy cash-flow term;
- use legacy 813.75 / 694.4 / CRF=0.07 / c_deg=0.55 /
  C_rep=5107.57 / lambda=(0.532,1.596,2.128) in production.

DGBAS CPI normalization used here
---------------------------------
Framework v7.2 freezes the optimization monetary basis as constant NTD-2023.
This script therefore reads the official DGBAS source artifact directly from:

    data/reference/cpispl.xls

The CPI worksheet is expected to be the DGBAS "消費者物價指數銜接表" with
index base 民國110年=100 (2021=100). Script 14a extracts the annual-average
("累計平均") CPI levels for ROC years 112, 113, and 114, corresponding to
2023, 2024, and 2025. It does NOT source those index levels from hard-coded
constants. The source workbook is fingerprinted with SHA-256 for provenance.

A nominal tariff/cash-flow value occurring in usage year y is converted by:

    value_constant_NTD2023 = value_nominal_NTD_y * CPI_2023 / CPI_y

CPI is used only for monetary-vintage normalization; it is separate from the
fixed 5% real modeling discount rate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-production-economic-interface-cpi-sourcefile-2026-08-26-r1"

# ---------------------------------------------------------------------------
# v7.2 locked economic decisions.
# ---------------------------------------------------------------------------
DISCOUNT_RATE = 0.05
ANALYSIS_HORIZON_YEARS = 20
DISCOUNT_RATE_ROLE = "real_modeling_discount_rate"
MONETARY_CURRENCY = "NTD"
MONETARY_BASE_YEAR = 2023

MAINLINE_POWER_BRACKET_MW = 10.0
SENSITIVITY_POWER_BRACKET_MW = 1.0
EXPECTED_POWER_BRACKETS_MW = (1.0, 10.0)
EXPECTED_DURATION_WINDOW = "4,6,8,10"
EXPECTED_FX_NTD_PER_USD = 31.150
EXPECTED_PRODUCTION_BREAKPOINTS = "0,0.30,0.60,0.80"

EXPECTED_KAPPA_ROUNDED_5DP = 1.01037
EXPECTED_KAPPA_PAIR_COUNT = 10

# ---------------------------------------------------------------------------
# DGBAS annual-average CPI evidence used for the v7.2 tariff deflator.
# The numerical CPI index levels are read from the official source workbook,
# not hard-coded here. Expected annual percentage changes are retained only as
# secondary regression checks against the extracted official index levels.
# ---------------------------------------------------------------------------
CPI_SOURCE = "Directorate-General of Budget, Accounting and Statistics (DGBAS), Taiwan"
CPI_SERIES = "Consumer Price Index (CPI), annual average; 2021=100"
CPI_SOURCE_SHEET = "CPI"
CPI_SOURCE_TABLE_TITLE = "消費者物價指數銜接表"
CPI_EXPECTED_BASE_TEXT = "民國110年 =100"
CPI_REFERENCE_PAGE = "https://www.stat.gov.tw/cpi2.aspx?n=4583"
CPI_RETRIEVED_DATE = "2026-08-26"
CPI_REQUIRED_GREGORIAN_YEARS = (2023, 2024, 2025)
CPI_REQUIRED_ROC_YEARS = {2023: 112, 2024: 113, 2025: 114}
EXPECTED_CPI_ANNUAL_CHANGE_PCT = {
    2024: 2.18,
    2025: 1.66,
}

# Known legacy anchors. They are allowed to exist in historical files, but they
# must never become values in the generated production interface.
LEGACY_ANNUALIZED_C_E = 813.75
LEGACY_ANNUALIZED_C_P = 694.4
LEGACY_CRF = 0.07
LEGACY_C_DEG = 0.55
LEGACY_C_REP = 5107.57
LEGACY_LAMBDAS = (0.532, 1.596, 2.128)

PARAMETER_REGISTRY_COLUMNS = [
    "parameter_name",
    "value",
    "unit",
    "currency",
    "currency_base_year",
    "source",
    "source_version",
    "capacity_basis",
    "annualized",
    "annualization_method",
    "mainline_or_legacy",
    "notes",
]

COST_REQUIRED_COLUMNS = {
    "package_id",
    "power_scale_bracket_mw",
    "duration_window_hr",
    "normalized_currency",
    "normalized_currency_base_year",
    "fx_ntd_per_usd",
    "capex_C_E_ntd_per_kwh",
    "capex_C_P_ntd_per_kw",
    "fom_E_ntd_per_kwh_year",
    "fom_P_ntd_per_kw_year",
    "crep_ntd_per_kwh",
    "discount_rate",
    "analysis_horizon_years",
    "crf",
    "annualized_capex_C_E_ntd_per_kwh_year",
    "annualized_capex_C_P_ntd_per_kw_year",
    "mainline_selected",
}

DEGRADATION_REQUIRED_COLUMNS = {
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

TARIFF_REQUIRED_COLUMNS = {
    "parameter_id",
    "parameter_group",
    "season",
    "tou_period",
    "contract_period",
    "value_numeric",
    "value_text",
    "unit",
    "applicable",
    "customer_class",
    "institution_type",
    "voltage_class",
    "tou_scheme",
    "case_effective_start",
    "case_effective_end",
    "source_file",
    "source_role",
    "mainline_or_legacy",
    "notes",
}

KAPPA_REQUIRED_COLUMNS = {
    "usage_period_id",
    "hourly_observed_grid_max_kw_Hm",
    "billed_overall_max_kw_Bm",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Build and audit the NTUST v7.2 production economic interface."
    )

    parser.add_argument(
        "--cost-packages",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv"
        ),
    )
    parser.add_argument(
        "--degradation-packages",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "pnnl_calibrated_pwl_degradation_candidate_packages.csv"
        ),
    )
    parser.add_argument(
        "--tariff-registry",
        type=Path,
        default=root / "data" / "reference" / "taipower_tariff_registry_v7_1.csv",
    )
    parser.add_argument(
        "--tariff-audit-13b",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "taipower_tariff_registry_audit_v7_1.json"
        ),
    )
    parser.add_argument(
        "--bill-audit-13c",
        type=Path,
        default=(
            root
            / "results"
            / "billing_audit"
            / "taipower_core_bill_regression_audit_v7_1.json"
        ),
    )
    parser.add_argument(
        "--kappa-pairs",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "kappa_calibration_pairs_v7_1.csv"
        ),
    )

    parser.add_argument(
        "--cpi-source",
        type=Path,
        default=root / "data" / "reference" / "cpispl.xls",
        help=(
            "Official DGBAS CPI source workbook. Default: data/reference/cpispl.xls"
        ),
    )

    parser.add_argument(
        "--cpi-output",
        type=Path,
        default=root / "data" / "reference" / "taiwan_cpi_annual_registry_v7_2.csv",
    )
    parser.add_argument(
        "--normalized-tariff-output",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "taipower_tariff_optimization_ntd2023_v7_2.csv"
        ),
    )
    parser.add_argument(
        "--parameter-registry-output",
        type=Path,
        default=root / "data" / "reference" / "parameter_registry_v7_2.csv",
    )
    parser.add_argument(
        "--interface-output",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / "production_economic_interface_v7_2.json"
        ),
    )
    parser.add_argument(
        "--audit-json-output",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "production_economic_interface_preflight_v7_2.json"
        ),
    )
    parser.add_argument(
        "--audit-text-output",
        type=Path,
        default=(
            root
            / "results"
            / "parameter_audit"
            / "production_economic_interface_preflight_v7_2.txt"
        ),
    )
    return parser.parse_args()


def crf(rate: float, years: int) -> float:
    if rate <= -1.0:
        raise ValueError("Discount rate must be greater than -1.")
    if years <= 0:
        raise ValueError("Analysis horizon must be positive.")
    if np.isclose(rate, 0.0, atol=0.0, rtol=0.0):
        return 1.0 / years
    return rate * (1.0 + rate) ** years / ((1.0 + rate) ** years - 1.0)


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise RuntimeError(f"{label}: missing required columns {missing}")


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found:\n{path}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    require_file(path, label)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc


def normalize_bool_scalar(value: Any, label: str) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise RuntimeError(f"{label}: missing boolean value")
    text = str(value).strip().lower()
    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }
    if text not in mapping:
        raise RuntimeError(f"{label}: cannot parse boolean value {value!r}")
    return mapping[text]


def normalize_bool_series(series: pd.Series, label: str) -> pd.Series:
    return series.map(lambda x: normalize_bool_scalar(x, label)).astype(bool)


def assert_close(
    observed: float,
    expected: float,
    label: str,
    *,
    atol: float = 1e-9,
) -> None:
    if not np.isclose(float(observed), float(expected), rtol=0.0, atol=atol):
        raise RuntimeError(
            f"{label} mismatch: observed={observed}, expected={expected}"
        )


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, Path):
        return str(value)
    return value


def read_official_cpi_workbook(path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read and validate the official DGBAS CPI workbook.

    The production default is the legacy Excel .xls file cpispl.xls. Pandas
    requires the optional xlrd package to read .xls files. A clear error is
    raised rather than silently falling back to hard-coded CPI values.
    """
    require_file(path, "Official DGBAS CPI workbook")

    suffix = path.suffix.lower()
    engine: str | None
    if suffix == ".xls":
        try:
            import xlrd  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "Reading the official DGBAS .xls workbook requires xlrd. "
                "Install it once in the project environment with: "
                "python -m pip install 'xlrd>=2.0.1'"
            ) from exc
        engine = "xlrd"
    elif suffix in {".xlsx", ".xlsm"}:
        engine = "openpyxl"
    else:
        raise RuntimeError(
            f"Unsupported CPI workbook format {suffix!r}; expected .xls or .xlsx."
        )

    try:
        raw = pd.read_excel(
            path,
            sheet_name=CPI_SOURCE_SHEET,
            header=None,
            engine=engine,
        )
    except ValueError as exc:
        raise RuntimeError(
            f"Official CPI workbook does not contain required sheet {CPI_SOURCE_SHEET!r}: {path}"
        ) from exc

    text_cells = raw.fillna("").astype(str)
    flattened = " | ".join(text_cells.to_numpy().ravel().tolist())
    if CPI_SOURCE_TABLE_TITLE not in flattened:
        raise RuntimeError(
            f"CPI workbook sheet {CPI_SOURCE_SHEET!r} does not contain expected table title "
            f"{CPI_SOURCE_TABLE_TITLE!r}."
        )

    normalized_flattened = flattened.replace(" ", "")
    if CPI_EXPECTED_BASE_TEXT.replace(" ", "") not in normalized_flattened:
        raise RuntimeError(
            "CPI workbook does not declare the expected fixed-index base 民國110年=100 (2021=100)."
        )

    header_row: int | None = None
    for i in range(len(raw)):
        vals = [str(v).strip() for v in raw.iloc[i].tolist()]
        if "民國年" in vals and "累計平均" in vals:
            header_row = i
            break
    if header_row is None:
        raise RuntimeError(
            "Could not locate CPI table header containing both '民國年' and '累計平均'."
        )

    headers = [str(v).strip() if pd.notna(v) else "" for v in raw.iloc[header_row]]
    year_col = headers.index("民國年")
    annual_col = headers.index("累計平均")

    month_columns: list[int] = []
    expected_month_labels = [f"{m}月" for m in range(1, 13)]
    for label in expected_month_labels:
        if label not in headers:
            raise RuntimeError(f"CPI workbook is missing monthly column {label!r}.")
        month_columns.append(headers.index(label))

    extracted_rows: list[dict[str, Any]] = []
    data = raw.iloc[header_row + 1 :].copy()

    for gregorian_year, roc_year in CPI_REQUIRED_ROC_YEARS.items():
        year_numeric = pd.to_numeric(data.iloc[:, year_col], errors="coerce")
        matches = data.loc[year_numeric.eq(roc_year)]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected exactly one CPI row for ROC year {roc_year} / {gregorian_year}; "
                f"found {len(matches)}."
            )

        row = matches.iloc[0]
        annual_index = pd.to_numeric(pd.Series([row.iloc[annual_col]]), errors="coerce").iloc[0]
        if pd.isna(annual_index) or float(annual_index) <= 0:
            raise RuntimeError(
                f"Invalid annual-average CPI for ROC year {roc_year} / {gregorian_year}: {row.iloc[annual_col]!r}"
            )

        monthly = pd.to_numeric(
            pd.Series([row.iloc[j] for j in month_columns]),
            errors="coerce",
        )
        if monthly.isna().any():
            raise RuntimeError(
                f"CPI row for {gregorian_year} does not contain all 12 monthly indices."
            )

        monthly_mean = float(monthly.mean())
        # The official annual-average field is published to two decimals, so
        # allow only a small rounding difference from the arithmetic mean.
        if not np.isclose(
            float(annual_index),
            monthly_mean,
            rtol=0.0,
            atol=0.011,
        ):
            raise RuntimeError(
                f"{gregorian_year} annual CPI is inconsistent with the 12-month arithmetic mean: "
                f"published={float(annual_index):.6f}, monthly_mean={monthly_mean:.6f}."
            )

        extracted_rows.append(
            {
                "usage_year": gregorian_year,
                "roc_year": roc_year,
                "annual_average_cpi_index_2021_eq_100": float(annual_index),
                "monthly_mean_recomputed": monthly_mean,
            }
        )

    extracted = pd.DataFrame(extracted_rows).sort_values("usage_year").reset_index(drop=True)

    metadata = {
        "source_path": str(path),
        "source_file": path.name,
        "source_sha256": sha256_file(path),
        "source_size_bytes": path.stat().st_size,
        "sheet": CPI_SOURCE_SHEET,
        "table_title": CPI_SOURCE_TABLE_TITLE,
        "index_base": "2021=100 (ROC 110=100)",
        "retrieved_date": CPI_RETRIEVED_DATE,
        "reference_page": CPI_REFERENCE_PAGE,
    }
    return extracted, metadata


def build_cpi_registry(source_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build annual CPI normalization factors from the official source file."""
    extracted, metadata = read_official_cpi_workbook(source_path)
    idx = extracted.set_index("usage_year")

    missing_years = [
        year for year in CPI_REQUIRED_GREGORIAN_YEARS if year not in idx.index
    ]
    if missing_years:
        raise RuntimeError(f"Official CPI source is missing required years: {missing_years}")

    base_index = float(idx.loc[MONETARY_BASE_YEAR, "annual_average_cpi_index_2021_eq_100"])
    if base_index <= 0:
        raise RuntimeError("2023 CPI base index must be positive.")

    rows: list[dict[str, Any]] = []
    for year in CPI_REQUIRED_GREGORIAN_YEARS:
        index_level = float(idx.loc[year, "annual_average_cpi_index_2021_eq_100"])
        previous = (
            float(idx.loc[year - 1, "annual_average_cpi_index_2021_eq_100"])
            if year - 1 in idx.index
            else np.nan
        )
        annual_change = (
            (index_level / previous - 1.0) * 100.0
            if np.isfinite(previous)
            else np.nan
        )
        relative = index_level / base_index
        deflator = base_index / index_level

        rows.append(
            {
                "usage_year": int(year),
                "roc_year": int(idx.loc[year, "roc_year"]),
                "annual_average_cpi_index_2021_eq_100": index_level,
                "monthly_mean_recomputed": float(idx.loc[year, "monthly_mean_recomputed"]),
                "annual_average_cpi_change_pct_implied": annual_change,
                "published_annual_change_pct_2dp": EXPECTED_CPI_ANNUAL_CHANGE_PCT.get(year, np.nan),
                "relative_price_level_2023_eq_1": relative,
                "deflator_to_constant_ntd2023": deflator,
                "source": CPI_SOURCE,
                "series": CPI_SERIES,
                "source_file": metadata["source_file"],
                "source_sha256": metadata["source_sha256"],
                "source_sheet": metadata["sheet"],
                "source_table_title": metadata["table_title"],
                "source_index_base": metadata["index_base"],
                "reference_page": CPI_REFERENCE_PAGE,
                "retrieved_date": CPI_RETRIEVED_DATE,
                "status": "REFERENCE_BASE_YEAR" if year == 2023 else "OFFICIAL_ANNUAL_AVERAGE_INDEX",
                "notes": (
                    "Annual CPI level extracted directly from official DGBAS source workbook. "
                    "Deflator = CPI_2023 / CPI_usage_year. CPI normalization is separate "
                    "from the 5% real modeling discount rate."
                ),
            }
        )

    cpi = pd.DataFrame(rows)

    # Secondary cross-check only: verify the extracted annual index levels
    # reproduce DGBAS-published annual-average percentage changes to 2 dp.
    for year, expected_pct in EXPECTED_CPI_ANNUAL_CHANGE_PCT.items():
        implied = float(
            cpi.loc[
                cpi["usage_year"].eq(year),
                "annual_average_cpi_change_pct_implied",
            ].iloc[0]
        )
        if round(implied, 2) != expected_pct:
            raise RuntimeError(
                f"{year} CPI annual-change cross-check failed: "
                f"implied={implied:.6f}%, published={expected_pct:.2f}%"
            )

    # Structural direction check for this case period.
    for year in (2024, 2025):
        factor = float(
            cpi.loc[
                cpi["usage_year"].eq(year),
                "deflator_to_constant_ntd2023",
            ].iloc[0]
        )
        if not (0.0 < factor < 1.0):
            raise RuntimeError(
                f"Expected {year}->2023 CPI deflator to lie in (0,1); got {factor}."
            )

    return cpi, metadata

def load_and_validate_cost_packages(path: Path, derived_crf: float) -> pd.DataFrame:
    require_file(path, "11g NTD-2023 cost package")
    df = pd.read_csv(path)
    require_columns(df, COST_REQUIRED_COLUMNS, "11g cost package")

    if len(df) != 2:
        raise RuntimeError(f"Expected exactly 2 cost packages; found {len(df)}")

    brackets = tuple(sorted(df["power_scale_bracket_mw"].astype(float).tolist()))
    if brackets != EXPECTED_POWER_BRACKETS_MW:
        raise RuntimeError(
            f"Unexpected cost brackets: expected={EXPECTED_POWER_BRACKETS_MW}, observed={brackets}"
        )

    if df["package_id"].duplicated().any():
        raise RuntimeError("11g package_id must be unique.")

    if not (df["duration_window_hr"].astype(str) == EXPECTED_DURATION_WINDOW).all():
        raise RuntimeError("11g duration window must be exactly 4,6,8,10.")

    if not (df["normalized_currency"].astype(str) == MONETARY_CURRENCY).all():
        raise RuntimeError("All 11g packages must be normalized to NTD.")

    if not (
        df["normalized_currency_base_year"].astype(int) == MONETARY_BASE_YEAR
    ).all():
        raise RuntimeError("All 11g packages must use currency base year 2023.")

    if not np.allclose(
        df["fx_ntd_per_usd"].astype(float).to_numpy(),
        EXPECTED_FX_NTD_PER_USD,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("11g FX must be 31.150 NTD/USD for both packages.")

    if not np.allclose(
        df["discount_rate"].astype(float).to_numpy(),
        DISCOUNT_RATE,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("11g discount rate must be 5%.")

    if not (
        df["analysis_horizon_years"].astype(int) == ANALYSIS_HORIZON_YEARS
    ).all():
        raise RuntimeError("11g analysis horizon must be 20 years.")

    if not np.allclose(
        df["crf"].astype(float).to_numpy(),
        derived_crf,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("11g CRF is inconsistent with r=5%, n=20.")

    upstream_selected = normalize_bool_series(
        df["mainline_selected"], "11g mainline_selected"
    )
    if upstream_selected.any():
        raise RuntimeError(
            "11g candidate packages must not pre-select a mainline bracket; "
            "v7.2 routing occurs in Script 14a."
        )

    for _, row in df.iterrows():
        ce = float(row["capex_C_E_ntd_per_kwh"])
        cp = float(row["capex_C_P_ntd_per_kw"])
        ann_ce = float(row["annualized_capex_C_E_ntd_per_kwh_year"])
        ann_cp = float(row["annualized_capex_C_P_ntd_per_kw_year"])
        assert_close(ann_ce, ce * derived_crf, "Annualized C_E identity", atol=1e-8)
        assert_close(ann_cp, cp * derived_crf, "Annualized C_P identity", atol=1e-8)

        for field in [
            "capex_C_E_ntd_per_kwh",
            "capex_C_P_ntd_per_kw",
            "fom_E_ntd_per_kwh_year",
            "fom_P_ntd_per_kw_year",
            "crep_ntd_per_kwh",
        ]:
            value = float(row[field])
            if not np.isfinite(value) or value < 0:
                raise RuntimeError(f"Invalid 11g value {field}={value}")

    return df.copy()


def load_and_validate_degradation_packages(path: Path) -> pd.DataFrame:
    require_file(path, "11h degradation package")
    df = pd.read_csv(path)
    require_columns(df, DEGRADATION_REQUIRED_COLUMNS, "11h degradation package")

    if len(df) != 2:
        raise RuntimeError(f"Expected exactly 2 degradation packages; found {len(df)}")

    brackets = tuple(sorted(df["power_scale_bracket_mw"].astype(float).tolist()))
    if brackets != EXPECTED_POWER_BRACKETS_MW:
        raise RuntimeError(
            "Unexpected degradation brackets: "
            f"expected={EXPECTED_POWER_BRACKETS_MW}, observed={brackets}"
        )

    if df["package_id"].duplicated().any():
        raise RuntimeError("11h package_id must be unique.")

    if not (df["currency"].astype(str) == MONETARY_CURRENCY).all():
        raise RuntimeError("11h degradation packages must be NTD.")

    if not (df["currency_base_year"].astype(int) == MONETARY_BASE_YEAR).all():
        raise RuntimeError("11h degradation packages must use base year 2023.")

    if not (
        df["production_breakpoints"].astype(str) == EXPECTED_PRODUCTION_BREAKPOINTS
    ).all():
        raise RuntimeError(
            "11h production breakpoints must be 0,0.30,0.60,0.80."
        )

    if not (df["lambda_ratio"].astype(str) == "1:3:4").all():
        raise RuntimeError("11h lambda ratio must be 1:3:4.")

    upstream_selected = normalize_bool_series(
        df["mainline_selected"], "11h mainline_selected"
    )
    if upstream_selected.any():
        raise RuntimeError(
            "11h candidate packages must not pre-select a mainline bracket; "
            "v7.2 routing occurs in Script 14a."
        )

    for _, row in df.iterrows():
        l1 = float(row["lambda_1_ntd_per_battery_side_kwh"])
        l2 = float(row["lambda_2_ntd_per_battery_side_kwh"])
        l3 = float(row["lambda_3_ntd_per_battery_side_kwh"])
        if not (l1 > 0 and l2 > 0 and l3 > 0):
            raise RuntimeError("All PWL lambda values must be positive.")
        assert_close(l2 / l1, 3.0, "lambda_2/lambda_1", atol=1e-10)
        assert_close(l3 / l1, 4.0, "lambda_3/lambda_1", atol=1e-10)

    return df.copy()


def merge_full_packages(cost: pd.DataFrame, deg: pd.DataFrame) -> pd.DataFrame:
    merged = cost.merge(
        deg,
        on=["package_id", "power_scale_bracket_mw"],
        how="inner",
        validate="one_to_one",
        suffixes=("_cost", "_deg"),
    )

    if len(merged) != 2:
        raise RuntimeError("Cost and degradation packages did not merge one-to-one.")

    for _, row in merged.iterrows():
        assert_close(
            float(row["crep_ntd_per_kwh_cost"]),
            float(row["crep_ntd_per_kwh_deg"]),
            f"C_rep consistency for {row['package_id']}",
            atol=1e-9,
        )

    roles = []
    for power in merged["power_scale_bracket_mw"].astype(float):
        if np.isclose(power, MAINLINE_POWER_BRACKET_MW, rtol=0.0, atol=1e-12):
            roles.append("mainline")
        elif np.isclose(power, SENSITIVITY_POWER_BRACKET_MW, rtol=0.0, atol=1e-12):
            roles.append("sensitivity")
        else:
            raise RuntimeError(f"Unexpected power-scale bracket {power}")

    merged["v7_2_role"] = roles

    if (merged["v7_2_role"] == "mainline").sum() != 1:
        raise RuntimeError("Exactly one mainline package must be selected.")
    if (merged["v7_2_role"] == "sensitivity").sum() != 1:
        raise RuntimeError("Exactly one sensitivity package must be selected.")

    mainline_power = float(
        merged.loc[merged["v7_2_role"].eq("mainline"), "power_scale_bracket_mw"].iloc[0]
    )
    sensitivity_power = float(
        merged.loc[merged["v7_2_role"].eq("sensitivity"), "power_scale_bracket_mw"].iloc[0]
    )
    assert_close(mainline_power, 10.0, "v7.2 mainline bracket")
    assert_close(sensitivity_power, 1.0, "v7.2 sensitivity bracket")

    return merged


def load_passed_upstream_audits(path_13b: Path, path_13c: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    audit_13b = read_json(path_13b, "13b tariff audit")
    audit_13c = read_json(path_13c, "13c bill regression audit")

    if str(audit_13b.get("status", "")).upper() != "PASS":
        raise RuntimeError("13b tariff audit status is not PASS.")
    if str(audit_13c.get("status", "")).upper() != "PASS":
        raise RuntimeError("13c bill regression audit status is not PASS.")

    tariff_identity = audit_13b.get("tariff_identity", {})
    if tariff_identity.get("customer_class") != "school":
        raise RuntimeError("13b customer_class must be school.")
    if tariff_identity.get("voltage_class") != "high_voltage":
        raise RuntimeError("13b voltage_class must be high_voltage.")
    if tariff_identity.get("tou_scheme") != "three_period_fixed_peak":
        raise RuntimeError("13b TOU scheme must be three_period_fixed_peak.")

    overcontract = audit_13b.get("overcontract_rule", {})
    assert_close(overcontract.get("tier1_threshold_fraction"), 0.10, "13b tier1 threshold")
    assert_close(overcontract.get("tier1_multiplier"), 2.0, "13b tier1 multiplier")
    assert_close(overcontract.get("tier2_multiplier"), 3.0, "13b tier2 multiplier")
    if overcontract.get("period_order") != "peak>half>sat_half>off":
        raise RuntimeError("13b period order mismatch.")
    if overcontract.get("non_duplication") is not True:
        raise RuntimeError("13b over-contract non-duplication must be true.")

    return audit_13b, audit_13c


def load_and_validate_tariff(path: Path) -> pd.DataFrame:
    require_file(path, "13b raw nominal tariff registry")
    df = pd.read_csv(path)
    require_columns(df, TARIFF_REQUIRED_COLUMNS, "13b raw nominal tariff registry")

    if df["parameter_id"].duplicated().any():
        dupes = df.loc[df["parameter_id"].duplicated(), "parameter_id"].tolist()
        raise RuntimeError(f"13b tariff registry has duplicate parameter IDs: {dupes}")

    roles = set(df["mainline_or_legacy"].astype(str).str.strip().str.lower())
    if roles != {"mainline"}:
        raise RuntimeError(f"13b tariff registry must be mainline-only; found roles={roles}")

    applicable = normalize_bool_series(df["applicable"], "tariff applicable")
    df = df.copy()
    df["applicable"] = applicable

    ns_peak = df.loc[df["parameter_id"].eq("energy_non_summer_peak")]
    if len(ns_peak) != 1:
        raise RuntimeError("Unique energy_non_summer_peak row is required.")
    ns_peak_row = ns_peak.iloc[0]
    if bool(ns_peak_row["applicable"]):
        raise RuntimeError("Non-summer peak must remain not applicable.")
    if pd.notna(ns_peak_row["value_numeric"]):
        raise RuntimeError("Non-summer peak value_numeric must remain NaN, not zero.")

    monetary = df["parameter_group"].isin(["energy_rate", "basic_charge_rate"])
    expected_monetary_count = 8 + 8
    if int(monetary.sum()) != expected_monetary_count:
        raise RuntimeError(
            f"Expected {expected_monetary_count} monetary tariff rows; found {int(monetary.sum())}."
        )

    return df


def build_normalized_tariff(raw: pd.DataFrame, cpi: pd.DataFrame) -> pd.DataFrame:
    cpi_idx = cpi.set_index("usage_year")
    rows: list[dict[str, Any]] = []

    monetary = raw.loc[
        raw["parameter_group"].isin(["energy_rate", "basic_charge_rate"])
    ].copy()

    for _, row in monetary.iterrows():
        for usage_year in (2024, 2025):
            factor = float(cpi_idx.loc[usage_year, "deflator_to_constant_ntd2023"])
            relative_level = float(
                cpi_idx.loc[usage_year, "relative_price_level_2023_eq_1"]
            )
            applicable = bool(row["applicable"])
            nominal = (
                float(row["value_numeric"])
                if applicable and pd.notna(row["value_numeric"])
                else np.nan
            )
            normalized = nominal * factor if np.isfinite(nominal) else np.nan

            rows.append(
                {
                    "parameter_id": row["parameter_id"],
                    "parameter_group": row["parameter_group"],
                    "season": row["season"],
                    "tou_period": row["tou_period"],
                    "contract_period": row["contract_period"],
                    "applicable": applicable,
                    "usage_year": usage_year,
                    "nominal_value": nominal,
                    "nominal_unit": row["unit"],
                    "nominal_currency": "NTD",
                    "nominal_cashflow_year": usage_year,
                    "relative_cpi_2023_eq_1": relative_level,
                    "deflator_to_constant_ntd2023": factor,
                    "value_constant_ntd2023": normalized,
                    "optimization_unit": row["unit"].replace("NTD", "NTD-2023"),
                    "optimization_currency": "NTD",
                    "optimization_currency_base_year": 2023,
                    "normalization_formula": (
                        "value_constant_NTD2023 = nominal_value * CPI_2023 / CPI_usage_year"
                    ),
                    "deflator_source": CPI_SOURCE,
                    "deflator_series": CPI_SERIES,
                    "deflator_source_file": str(cpi_idx.loc[usage_year, "source_file"]),
                    "deflator_source_sha256": str(cpi_idx.loc[usage_year, "source_sha256"]),
                    "deflator_source_sheet": str(cpi_idx.loc[usage_year, "source_sheet"]),
                    "deflator_retrieved_date": CPI_RETRIEVED_DATE,
                    "raw_tariff_source_file": row["source_file"],
                    "raw_tariff_source_role": row["source_role"],
                    "raw_mainline_or_legacy": row["mainline_or_legacy"],
                    "notes": (
                        "Optimization-facing copy only; raw 13b nominal tariff row is preserved."
                        if applicable
                        else "N/A preserved; not converted to a zero-rate period."
                    ),
                }
            )

    out = pd.DataFrame(rows)

    if len(out) != len(monetary) * 2:
        raise RuntimeError("Normalized tariff row-count mismatch.")

    ns_peak = out.loc[out["parameter_id"].eq("energy_non_summer_peak")]
    if len(ns_peak) != 2:
        raise RuntimeError("Normalized tariff must contain two N/A non-summer peak rows.")
    if ns_peak["applicable"].any():
        raise RuntimeError("Normalized non-summer peak must remain not applicable.")
    if ns_peak["value_constant_ntd2023"].notna().any():
        raise RuntimeError("Normalized non-summer peak must remain NaN, not zero.")

    applicable_rows = out.loc[out["applicable"]].copy()
    if applicable_rows["value_constant_ntd2023"].isna().any():
        raise RuntimeError("Applicable normalized tariff rows contain missing values.")
    if (applicable_rows["value_constant_ntd2023"] < 0).any():
        raise RuntimeError("Normalized tariff contains negative monetary rates.")

    # Every positive nominal 2024/2025 value must deflate downward to 2023 terms.
    positive = applicable_rows["nominal_value"] > 0
    if not (
        applicable_rows.loc[positive, "value_constant_ntd2023"]
        < applicable_rows.loc[positive, "nominal_value"]
    ).all():
        raise RuntimeError("Expected 2024/2025 positive nominal tariff values to deflate to lower NTD-2023 values.")

    return out


def load_and_recompute_kappa(path: Path) -> tuple[float, pd.DataFrame]:
    require_file(path, "Script-08 kappa calibration pairs")
    pairs = pd.read_csv(path)
    require_columns(pairs, KAPPA_REQUIRED_COLUMNS, "Script-08 kappa calibration pairs")

    if len(pairs) != EXPECTED_KAPPA_PAIR_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_KAPPA_PAIR_COUNT} kappa pairs; found {len(pairs)}"
        )

    expected_months = [f"2025-{m:02d}" for m in range(1, 11)]
    observed_months = sorted(pairs["usage_period_id"].astype(str).tolist())
    if observed_months != expected_months:
        raise RuntimeError(
            f"Kappa calibration months must be 2025-01..2025-10; found {observed_months}"
        )

    h = pd.to_numeric(
        pairs["hourly_observed_grid_max_kw_Hm"], errors="coerce"
    ).to_numpy(dtype=float)
    b = pd.to_numeric(
        pairs["billed_overall_max_kw_Bm"], errors="coerce"
    ).to_numpy(dtype=float)

    if not np.isfinite(h).all() or not np.isfinite(b).all():
        raise RuntimeError("Kappa H_m/B_m pairs contain non-finite values.")
    if (h <= 0).any() or (b <= 0).any():
        raise RuntimeError("Kappa H_m/B_m pairs must be positive.")

    denominator = float(np.dot(h, h))
    if denominator <= 0:
        raise RuntimeError("Kappa denominator sum(H_m^2) is non-positive.")
    kappa = float(np.dot(h, b) / denominator)

    if round(kappa, 5) != EXPECTED_KAPPA_ROUNDED_5DP:
        raise RuntimeError(
            "Kappa regression anchor failed: "
            f"computed={kappa:.10f}, rounded_5dp={kappa:.5f}, "
            f"expected={EXPECTED_KAPPA_ROUNDED_5DP:.5f}"
        )

    return kappa, pairs


def package_to_dict(row: pd.Series) -> dict[str, Any]:
    return {
        "package_id": str(row["package_id"]),
        "power_scale_bracket_mw": float(row["power_scale_bracket_mw"]),
        "role": str(row["v7_2_role"]),
        "cost_scale_label_only_not_power_bound": True,
        "duration_window_hr": str(row["duration_window_hr"]),
        "currency": "NTD",
        "currency_base_year": 2023,
        "fx_ntd_per_usd": float(row["fx_ntd_per_usd"]),
        "capex_C_E_ntd2023_per_kwh": float(row["capex_C_E_ntd_per_kwh"]),
        "capex_C_P_ntd2023_per_kw": float(row["capex_C_P_ntd_per_kw"]),
        "annualized_capex_C_E_ntd2023_per_kwh_year": float(
            row["annualized_capex_C_E_ntd_per_kwh_year"]
        ),
        "annualized_capex_C_P_ntd2023_per_kw_year": float(
            row["annualized_capex_C_P_ntd_per_kw_year"]
        ),
        "fom_E_ntd2023_per_kwh_year": float(row["fom_E_ntd_per_kwh_year"]),
        "fom_P_ntd2023_per_kw_year": float(row["fom_P_ntd_per_kw_year"]),
        "crep_ntd2023_per_kwh": float(row["crep_ntd_per_kwh_cost"]),
        "production_breakpoints": str(row["production_breakpoints"]),
        "lambda_1_ntd2023_per_battery_side_discharged_kwh": float(
            row["lambda_1_ntd_per_battery_side_kwh"]
        ),
        "lambda_2_ntd2023_per_battery_side_discharged_kwh": float(
            row["lambda_2_ntd_per_battery_side_kwh"]
        ),
        "lambda_3_ntd2023_per_battery_side_discharged_kwh": float(
            row["lambda_3_ntd_per_battery_side_kwh"]
        ),
        "lambda_ratio": str(row["lambda_ratio"]),
        "package_selection_timing": "ex_ante_before_eob_or_layer_a",
    }


def parameter_row(
    name: str,
    value: Any,
    unit: str,
    currency: str | None,
    currency_base_year: int | None,
    source: str,
    source_version: str,
    capacity_basis: str,
    annualized: str,
    annualization_method: str,
    role: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "parameter_name": name,
        "value": value,
        "unit": unit,
        "currency": currency,
        "currency_base_year": currency_base_year,
        "source": source,
        "source_version": source_version,
        "capacity_basis": capacity_basis,
        "annualized": annualized,
        "annualization_method": annualization_method,
        "mainline_or_legacy": role,
        "notes": notes,
    }


def build_parameter_registry(
    full_packages: pd.DataFrame,
    derived_crf: float,
    kappa: float,
    cpi: pd.DataFrame,
    normalized_tariff_path: Path,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    rows.extend(
        [
            parameter_row(
                "discount_rate_real",
                DISCOUNT_RATE,
                "fraction",
                None,
                None,
                "Research Framework v7.2 / Gate 2",
                "v7.2-2026-08-24",
                "financial",
                "no",
                "none",
                "mainline",
                "Fixed real modeling discount rate; not claimed as NTUST WACC.",
            ),
            parameter_row(
                "analysis_horizon_years",
                ANALYSIS_HORIZON_YEARS,
                "year",
                None,
                None,
                "Research Framework v7.2 / Gate 2",
                "v7.2-2026-08-24",
                "financial",
                "no",
                "none",
                "mainline",
                "Financial analysis horizon; not a physical battery-life hard gate.",
            ),
            parameter_row(
                "capital_recovery_factor",
                derived_crf,
                "1/year",
                None,
                None,
                "Script 14a derived from r and n",
                SCRIPT_VERSION,
                "financial",
                "yes",
                "CRF(r=0.05,n=20)",
                "mainline",
                "Derived by code; CRF is not independently hard-coded as a source value.",
            ),
            parameter_row(
                "billing_demand_kappa",
                kappa,
                "dimensionless",
                None,
                None,
                "Script 08 kappa calibration pairs",
                "v7.1-kappa-calibration-2026-08-17",
                "billing_proxy",
                "no",
                "none",
                "mainline",
                "NTUST site-specific through-origin LS coefficient; not a universal Taipower coefficient.",
            ),
        ]
    )

    cpi_idx = cpi.set_index("usage_year")
    for usage_year in (2024, 2025):
        rows.append(
            parameter_row(
                f"taipower_deflator_{usage_year}_to_ntd2023",
                float(cpi_idx.loc[usage_year, "deflator_to_constant_ntd2023"]),
                "multiplier",
                "NTD",
                2023,
                CPI_SOURCE,
                (
                    f"{str(cpi_idx.loc[usage_year, 'source_file'])}; "
                    f"sha256={str(cpi_idx.loc[usage_year, 'source_sha256'])[:12]}...; "
                    f"annual-average CPI {usage_year}"
                ),
                "tariff_cashflow",
                "no",
                "annual-average CPI index deflation",
                "mainline",
                f"Applied to usage-year {usage_year} nominal Taipower monetary rates; normalized layer={normalized_tariff_path.name}.",
            )
        )

    for _, row in full_packages.sort_values("power_scale_bracket_mw").iterrows():
        role = str(row["v7_2_role"])
        scale = int(round(float(row["power_scale_bracket_mw"])))
        prefix = f"bess_{scale}mw"
        source = "PNNL v2024 LFP package via Scripts 11f/11g/11h"
        source_version = "11g/11h audited package chain"

        package_parameters = [
            (
                f"{prefix}_capex_C_E",
                float(row["capex_C_E_ntd_per_kwh"]),
                "NTD/kWh",
                "nameplate_energy",
                "no",
                "none",
                "Raw normalized CAPEX energy coefficient; CRF not yet applied.",
            ),
            (
                f"{prefix}_capex_C_P",
                float(row["capex_C_P_ntd_per_kw"]),
                "NTD/kW",
                "ac_power_rating",
                "no",
                "none",
                "Raw normalized CAPEX power coefficient; CRF not yet applied.",
            ),
            (
                f"{prefix}_annualized_capex_C_E",
                float(row["annualized_capex_C_E_ntd_per_kwh_year"]),
                "NTD/kWh-year",
                "nameplate_energy",
                "yes",
                "CRF",
                "Annualized CAPEX energy coefficient = raw C_E * code-derived CRF.",
            ),
            (
                f"{prefix}_annualized_capex_C_P",
                float(row["annualized_capex_C_P_ntd_per_kw_year"]),
                "NTD/kW-year",
                "ac_power_rating",
                "yes",
                "CRF",
                "Annualized CAPEX power coefficient = raw C_P * code-derived CRF.",
            ),
            (
                f"{prefix}_fom_E",
                float(row["fom_E_ntd_per_kwh_year"]),
                "NTD/kWh-year",
                "nameplate_energy",
                "yes",
                "source-defined annual FOM",
                "Annual FOM; must NOT receive CRF again.",
            ),
            (
                f"{prefix}_fom_P",
                float(row["fom_P_ntd_per_kw_year"]),
                "NTD/kW-year",
                "ac_power_rating",
                "yes",
                "source-defined annual FOM",
                "Annual FOM; must NOT receive CRF again.",
            ),
            (
                f"{prefix}_C_rep",
                float(row["crep_ntd_per_kwh_cost"]),
                "NTD/kWh",
                "battery_side_nameplate_energy",
                "no",
                "none",
                "Cycling-wear replacement-cost basis; not CRF-annualized.",
            ),
            (
                f"{prefix}_lambda_1",
                float(row["lambda_1_ntd_per_battery_side_kwh"]),
                "NTD/battery-side-discharged-kWh",
                "battery_side_discharge",
                "no",
                "PNNL-calibrated PWL",
                "Bracket-specific lambda; use with Xu-derived intertemporal segment states.",
            ),
            (
                f"{prefix}_lambda_2",
                float(row["lambda_2_ntd_per_battery_side_kwh"]),
                "NTD/battery-side-discharged-kWh",
                "battery_side_discharge",
                "no",
                "PNNL-calibrated PWL",
                "Bracket-specific lambda; use with Xu-derived intertemporal segment states.",
            ),
            (
                f"{prefix}_lambda_3",
                float(row["lambda_3_ntd_per_battery_side_kwh"]),
                "NTD/battery-side-discharged-kWh",
                "battery_side_discharge",
                "no",
                "PNNL-calibrated PWL",
                "Bracket-specific lambda; use with Xu-derived intertemporal segment states.",
            ),
        ]

        for name, value, unit, basis, annualized, ann_method, notes in package_parameters:
            rows.append(
                parameter_row(
                    name,
                    value,
                    unit,
                    "NTD",
                    2023,
                    source,
                    source_version,
                    basis,
                    annualized,
                    ann_method,
                    role,
                    notes
                    + (
                        " 10 MW is the ex-ante thesis mainline cost-scale package."
                        if role == "mainline"
                        else " 1 MW is the ex-ante cost-scale sensitivity package."
                    ),
                )
            )

    registry = pd.DataFrame(rows, columns=PARAMETER_REGISTRY_COLUMNS)

    if registry["parameter_name"].duplicated().any():
        dupes = registry.loc[
            registry["parameter_name"].duplicated(), "parameter_name"
        ].tolist()
        raise RuntimeError(f"Parameter registry contains duplicate keys: {dupes}")

    allowed_roles = {"mainline", "sensitivity", "validation", "legacy_or_replication"}
    bad_roles = sorted(set(registry["mainline_or_legacy"].astype(str)) - allowed_roles)
    if bad_roles:
        raise RuntimeError(f"Unexpected parameter role labels: {bad_roles}")

    return registry


def audit_legacy_contamination(
    parameter_registry: pd.DataFrame,
    mainline_package: dict[str, Any],
    sensitivity_package: dict[str, Any],
    derived_crf: float,
) -> dict[str, str]:
    assert_close(derived_crf, 0.08024258719069129, "CRF regression anchor", atol=1e-12)
    if np.isclose(derived_crf, LEGACY_CRF, rtol=0.0, atol=1e-12):
        raise RuntimeError("Legacy CRF=0.07 contaminated production.")

    def reject_close(value: float, legacy: float, label: str, atol: float = 1e-9) -> None:
        if np.isclose(float(value), float(legacy), rtol=0.0, atol=atol):
            raise RuntimeError(f"Legacy contamination detected: {label}={legacy}")

    for pkg_label, pkg in [
        ("mainline", mainline_package),
        ("sensitivity", sensitivity_package),
    ]:
        reject_close(
            pkg["annualized_capex_C_E_ntd2023_per_kwh_year"],
            LEGACY_ANNUALIZED_C_E,
            f"{pkg_label} annualized C_E",
        )
        reject_close(
            pkg["annualized_capex_C_P_ntd2023_per_kw_year"],
            LEGACY_ANNUALIZED_C_P,
            f"{pkg_label} annualized C_P",
        )
        reject_close(
            pkg["crep_ntd2023_per_kwh"],
            LEGACY_C_REP,
            f"{pkg_label} C_rep",
        )

        current_lambdas = [
            pkg["lambda_1_ntd2023_per_battery_side_discharged_kwh"],
            pkg["lambda_2_ntd2023_per_battery_side_discharged_kwh"],
            pkg["lambda_3_ntd2023_per_battery_side_discharged_kwh"],
        ]
        if np.allclose(
            np.asarray(current_lambdas, dtype=float),
            np.asarray(LEGACY_LAMBDAS, dtype=float),
            rtol=0.0,
            atol=1e-9,
        ):
            raise RuntimeError(f"Legacy Harry lambda set contaminated {pkg_label} package.")

    names_lower = parameter_registry["parameter_name"].astype(str).str.lower()
    if names_lower.eq("c_deg").any() or names_lower.str.contains("legacy", regex=False).any():
        raise RuntimeError("Legacy-named parameter appeared in production registry.")

    # Explicitly ensure the standalone legacy c_deg value is not introduced.
    numeric = pd.to_numeric(parameter_registry["value"], errors="coerce")
    if (
        names_lower.str.contains("degradation", regex=False)
        & np.isclose(numeric, LEGACY_C_DEG, rtol=0.0, atol=1e-12)
    ).any():
        raise RuntimeError("Legacy c_deg=0.55 contaminated production registry.")

    return {
        "legacy_crf_0_07": "BLOCKED",
        "legacy_annualized_C_E_813_75": "BLOCKED",
        "legacy_annualized_C_P_694_4": "BLOCKED",
        "legacy_c_deg_0_55": "BLOCKED",
        "legacy_C_rep_5107_57": "BLOCKED",
        "legacy_harry_lambda_set": "BLOCKED",
    }


def build_audit_text(summary: dict[str, Any]) -> str:
    mainline = summary["package_routing"]["mainline_10mw"]
    sensitivity = summary["package_routing"]["sensitivity_1mw"]
    factors = summary["tariff_normalization"]["deflator_to_constant_ntd2023"]

    lines = [
        f"Script version: {SCRIPT_VERSION}",
        "NTUST v7.2 Production Economic-Interface Preflight",
        "",
        "Gate 1 — cost-scale routing",
        f"- Mainline package: {mainline['package_id']} ({mainline['power_scale_bracket_mw']:g} MW source scale)",
        f"- Sensitivity package: {sensitivity['package_id']} ({sensitivity['power_scale_bracket_mw']:g} MW source scale)",
        "- Package choice occurs ex ante; optimized BESS power cannot switch the bracket.",
        "- 1 MW / 10 MW labels are cost-scale source cases, not BESS power bounds.",
        "",
        "Gate 2 — monetary basis",
        "- Optimization currency: constant NTD-2023",
        f"- Discount rate: {summary['monetary_basis']['discount_rate']:.4f} (real modeling rate)",
        f"- Analysis horizon: {summary['monetary_basis']['analysis_horizon_years']} years",
        f"- Derived CRF: {summary['monetary_basis']['crf']:.10f}",
        "- Raw 13b Taipower tariff remains nominal and unchanged.",
        f"- Official CPI source: {summary['tariff_normalization']['official_source_file']}",
        f"- Official CPI source SHA-256: {summary['tariff_normalization']['official_source_sha256']}",
        f"- 2024 nominal -> NTD-2023 factor: {float(factors['2024']):.12f}",
        f"- 2025 nominal -> NTD-2023 factor: {float(factors['2025']):.12f}",
        "- CPI method: DGBAS annual-average CPI, extracted from cpispl workbook; 2023 relative price level = 1.",
        "",
        "Billing-demand proxy",
        f"- kappa recomputed from Script-08 pairs: {summary['billing_proxy']['kappa']:.10f}",
        "- Estimator: through-origin least squares on 2025-01..2025-10 H_m/B_m pairs.",
        "",
        "Tariff semantics",
        "- Customer treatment: SCHOOL/FROZEN high-voltage project label.",
        "- Non-summer peak: N/A, never zero-rate.",
        "- Over-contract: first 10% = 2x; beyond = 3x; sequential non-duplication preserved.",
        "- May/October 50/50 basic-charge convention remains case-validated empirical.",
        "- No separate subsidy cash-flow item is added.",
        "",
        "Legacy contamination guards",
    ]
    for key, value in summary["legacy_guards"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "Outputs",
            f"- Official CPI source (read-only): {summary['outputs']['official_cpi_source']}",
            f"- CPI registry: {summary['outputs']['cpi_registry']}",
            f"- Optimization tariff: {summary['outputs']['normalized_tariff']}",
            f"- Parameter registry: {summary['outputs']['parameter_registry']}",
            f"- Solver-facing economic interface: {summary['outputs']['economic_interface']}",
            "",
            "Final verdict",
            f"- Script 14a production-interface preflight: {summary['status']}",
            "- No optimization was executed.",
            "- Next step after PASS: wire the EOB / Layer A objective to this interface.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    print(f"Script version: {SCRIPT_VERSION}")
    print("NTUST v7.2 Production Economic-Interface Preflight")
    print(f"Script version: {SCRIPT_VERSION}")
    print()

    for output_path in [
        args.cpi_output,
        args.normalized_tariff_output,
        args.parameter_registry_output,
        args.interface_output,
        args.audit_json_output,
        args.audit_text_output,
    ]:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Upstream artifact presence + hashes.
    # ------------------------------------------------------------------
    input_paths = {
        "cost_packages_11g": args.cost_packages,
        "degradation_packages_11h": args.degradation_packages,
        "raw_tariff_registry_13b": args.tariff_registry,
        "tariff_audit_13b": args.tariff_audit_13b,
        "bill_audit_13c": args.bill_audit_13c,
        "kappa_pairs_08": args.kappa_pairs,
        "official_cpi_source": args.cpi_source,
    }
    for label, path in input_paths.items():
        require_file(path, label)

    input_hashes = {
        label: {
            "path": str(path),
            "sha256": sha256_file(path),
        }
        for label, path in input_paths.items()
    }

    print("Inputs")
    for label, meta in input_hashes.items():
        print(f"- {label}: {meta['path']}")
    print()

    # ------------------------------------------------------------------
    # CRF / cost package / degradation package.
    # ------------------------------------------------------------------
    derived_crf = crf(DISCOUNT_RATE, ANALYSIS_HORIZON_YEARS)
    assert_close(
        derived_crf,
        0.08024258719069129,
        "v7.2 CRF regression anchor",
        atol=1e-12,
    )

    cost = load_and_validate_cost_packages(args.cost_packages, derived_crf)
    deg = load_and_validate_degradation_packages(args.degradation_packages)
    full = merge_full_packages(cost, deg)

    mainline_row = full.loc[full["v7_2_role"].eq("mainline")].iloc[0]
    sensitivity_row = full.loc[full["v7_2_role"].eq("sensitivity")].iloc[0]
    mainline_package = package_to_dict(mainline_row)
    sensitivity_package = package_to_dict(sensitivity_row)

    # ------------------------------------------------------------------
    # Taipower upstream audits + raw tariff.
    # ------------------------------------------------------------------
    audit_13b, audit_13c = load_passed_upstream_audits(
        args.tariff_audit_13b,
        args.bill_audit_13c,
    )
    raw_tariff = load_and_validate_tariff(args.tariff_registry)

    # ------------------------------------------------------------------
    # CPI registry and constant-NTD-2023 tariff layer.
    # ------------------------------------------------------------------
    cpi, cpi_metadata = build_cpi_registry(args.cpi_source)
    cpi.to_csv(args.cpi_output, index=False, encoding="utf-8-sig")

    normalized_tariff = build_normalized_tariff(raw_tariff, cpi)
    normalized_tariff.to_csv(
        args.normalized_tariff_output,
        index=False,
        encoding="utf-8-sig",
    )

    # ------------------------------------------------------------------
    # Kappa — recompute from Script-08 output, do not source from a constant.
    # ------------------------------------------------------------------
    kappa, kappa_pairs = load_and_recompute_kappa(args.kappa_pairs)

    # ------------------------------------------------------------------
    # 12-field machine-readable parameter registry.
    # ------------------------------------------------------------------
    parameter_registry = build_parameter_registry(
        full,
        derived_crf,
        kappa,
        cpi,
        args.normalized_tariff_output,
    )

    if list(parameter_registry.columns) != PARAMETER_REGISTRY_COLUMNS:
        raise RuntimeError("Parameter registry schema does not match the v7.2 12-field schema.")

    legacy_guards = audit_legacy_contamination(
        parameter_registry,
        mainline_package,
        sensitivity_package,
        derived_crf,
    )

    parameter_registry.to_csv(
        args.parameter_registry_output,
        index=False,
        encoding="utf-8-sig",
    )

    cpi_idx = cpi.set_index("usage_year")
    deflator_map = {
        str(year): float(cpi_idx.loc[year, "deflator_to_constant_ntd2023"])
        for year in (2024, 2025)
    }

    # ------------------------------------------------------------------
    # Solver-facing interface JSON.
    # ------------------------------------------------------------------
    economic_interface = {
        "interface_version": "v7.2",
        "generated_by": SCRIPT_VERSION,
        "status": "READY_FOR_EOB_OBJECTIVE_WIRING",
        "monetary_basis": {
            "currency": "NTD",
            "currency_base_year": 2023,
            "basis_label": "constant NTD-2023",
            "discount_rate": DISCOUNT_RATE,
            "discount_rate_role": DISCOUNT_RATE_ROLE,
            "analysis_horizon_years": ANALYSIS_HORIZON_YEARS,
            "crf": derived_crf,
            "consistency_rule": "constant-dollar cash flows + real discount rate",
        },
        "package_selector": {
            "mainline_role": "10 MW PNNL full economic package",
            "sensitivity_role": "1 MW PNNL full economic package",
            "selection_timing": "ex ante before EOB / Layer A optimization",
            "outcome_dependent_switching_allowed": False,
            "labels_are_power_bounds": False,
            "mainline": mainline_package,
            "cost_scale_sensitivity": sensitivity_package,
        },
        "billing_demand_proxy": {
            "kappa": kappa,
            "estimator": "through-origin least squares",
            "calibration_usage_periods": [f"2025-{m:02d}" for m in range(1, 11)],
            "source_pairs_file": str(args.kappa_pairs),
            "source_pairs_sha256": input_hashes["kappa_pairs_08"]["sha256"],
            "site_specific": True,
            "universal_taipower_coefficient": False,
        },
        "taipower_tariff": {
            "raw_nominal_registry": str(args.tariff_registry),
            "raw_nominal_registry_sha256": input_hashes["raw_tariff_registry_13b"]["sha256"],
            "raw_nominal_registry_preserved": True,
            "optimization_registry": str(args.normalized_tariff_output),
            "optimization_currency": "constant NTD-2023",
            "deflator_registry": str(args.cpi_output),
            "deflator_source_file": str(args.cpi_source),
            "deflator_source_sha256": cpi_metadata["source_sha256"],
            "deflator_source_sheet": cpi_metadata["sheet"],
            "deflator_source_index_base": cpi_metadata["index_base"],
            "deflator_method": "DGBAS annual-average CPI; chained relative to 2023=1",
            "deflator_to_constant_ntd2023": deflator_map,
            "non_summer_peak_semantics": "N/A_not_zero",
            "school_frozen_label_scope": "NTUST project institutional-treatment label",
            "may_october_basic_charge_transition": "case_validated_empirical_50_50",
            "separate_subsidy_cashflow": False,
        },
        "parameter_registry": {
            "path": str(args.parameter_registry_output),
            "schema_fields": PARAMETER_REGISTRY_COLUMNS,
            "allowed_role_labels": [
                "mainline",
                "sensitivity",
                "validation",
                "legacy_or_replication",
            ],
        },
        "degradation_accounting_boundary": {
            "mainline_formulation": "PNNL-calibrated Xu-derived intertemporal PWL",
            "lambda_unit": "NTD-2023 per battery-side discharged kWh",
            "annual_fom_receives_crf": False,
            "c_rep_receives_crf": False,
            "second_full_replacement_cashflow": False,
        },
        "preflight_guards": {
            "legacy_values_blocked": True,
            "dynamic_cost_bracket_switching_blocked": True,
            "raw_tariff_overwrite_blocked": True,
            "non_summer_peak_zero_fill_blocked": True,
            "double_crf_on_fom_blocked": True,
            "subsidy_double_counting_blocked": True,
        },
        "inputs": input_hashes,
    }

    args.interface_output.write_text(
        json.dumps(json_safe(economic_interface), indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )

    # ------------------------------------------------------------------
    # Final audit summary.
    # ------------------------------------------------------------------
    summary = {
        "script_version": SCRIPT_VERSION,
        "status": "PASS",
        "scope": "production economic-interface preflight only; no optimization",
        "monetary_basis": {
            "currency": "NTD",
            "base_year": 2023,
            "discount_rate": DISCOUNT_RATE,
            "discount_rate_role": DISCOUNT_RATE_ROLE,
            "analysis_horizon_years": ANALYSIS_HORIZON_YEARS,
            "crf": derived_crf,
        },
        "package_routing": {
            "mainline_10mw": mainline_package,
            "sensitivity_1mw": sensitivity_package,
            "optimized_power_can_switch_package": False,
        },
        "tariff_normalization": {
            "raw_registry_preserved": True,
            "optimization_basis": "constant NTD-2023",
            "method": "DGBAS annual-average CPI chained from 2023=1",
            "official_source_file": str(args.cpi_source),
            "official_source_sha256": cpi_metadata["source_sha256"],
            "official_source_sheet": cpi_metadata["sheet"],
            "official_source_index_base": cpi_metadata["index_base"],
            "published_annual_average_changes_pct": {
                "2024_vs_2023": EXPECTED_CPI_ANNUAL_CHANGE_PCT[2024],
                "2025_vs_2024": EXPECTED_CPI_ANNUAL_CHANGE_PCT[2025],
            },
            "deflator_to_constant_ntd2023": deflator_map,
            "non_summer_peak": "N/A preserved",
        },
        "billing_proxy": {
            "kappa": kappa,
            "pair_count": len(kappa_pairs),
            "status": "PASS",
        },
        "upstream_audits": {
            "13b_status": audit_13b.get("status"),
            "13c_status": audit_13c.get("status"),
        },
        "legacy_guards": legacy_guards,
        "gates": {
            "10mw_mainline_full_package": "PASS",
            "1mw_sensitivity_full_package": "PASS",
            "outcome_dependent_bracket_switching": "BLOCKED",
            "constant_ntd2023_basis": "PASS",
            "real_5pct_discount_rate": "PASS",
            "crf_code_derived": "PASS",
            "raw_nominal_tariff_preserved": "PASS",
            "normalized_tariff_layer_generated": "PASS",
            "dgbas_cpi_provenance": "PASS",
            "kappa_recomputed_from_script08_pairs": "PASS",
            "13b_upstream_audit": "PASS",
            "13c_upstream_audit": "PASS",
            "non_summer_peak_na_semantics": "PASS",
            "subsidy_non_double_counting": "PASS",
            "parameter_registry_12_field_schema": "PASS",
            "legacy_contamination": "PASS",
        },
        "inputs": input_hashes,
        "outputs": {
            "official_cpi_source": str(args.cpi_source),
            "cpi_registry": str(args.cpi_output),
            "normalized_tariff": str(args.normalized_tariff_output),
            "parameter_registry": str(args.parameter_registry_output),
            "economic_interface": str(args.interface_output),
            "audit_json": str(args.audit_json_output),
            "audit_text": str(args.audit_text_output),
        },
        "next_step": (
            "After PASS, wire the EOB / Layer A objective to the generated "
            "production_economic_interface_v7_2.json and normalized tariff layer; "
            "do not re-select the cost bracket inside the solver."
        ),
    }

    args.audit_json_output.write_text(
        json.dumps(json_safe(summary), indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    args.audit_text_output.write_text(build_audit_text(summary), encoding="utf-8")

    print("Gate interpretation")
    for gate, status in summary["gates"].items():
        print(f"- {gate}: {status}")

    print()
    print("Key values")
    print(f"- r = {DISCOUNT_RATE:.4f} (real modeling discount rate)")
    print(f"- n = {ANALYSIS_HORIZON_YEARS} years")
    print(f"- CRF = {derived_crf:.10f}")
    print(f"- kappa = {kappa:.10f}")
    print(
        "- CPI annual averages from official source: "
        f"2023={float(cpi_idx.loc[2023, 'annual_average_cpi_index_2021_eq_100']):.2f}, "
        f"2024={float(cpi_idx.loc[2024, 'annual_average_cpi_index_2021_eq_100']):.2f}, "
        f"2025={float(cpi_idx.loc[2025, 'annual_average_cpi_index_2021_eq_100']):.2f}"
    )
    print(f"- CPI source SHA-256 = {cpi_metadata['source_sha256']}")
    print(f"- 2024 nominal -> NTD-2023 factor = {deflator_map['2024']:.12f}")
    print(f"- 2025 nominal -> NTD-2023 factor = {deflator_map['2025']:.12f}")
    print(f"- Mainline cost package = {mainline_package['power_scale_bracket_mw']:g} MW scale")
    print(f"- Sensitivity cost package = {sensitivity_package['power_scale_bracket_mw']:g} MW scale")

    print()
    print("Outputs")
    print(f"- Official CPI source (read-only): {args.cpi_source}")
    print(f"- CPI registry: {args.cpi_output}")
    print(f"- Optimization tariff: {args.normalized_tariff_output}")
    print(f"- Parameter registry: {args.parameter_registry_output}")
    print(f"- Economic interface: {args.interface_output}")
    print(f"- Audit JSON: {args.audit_json_output}")
    print(f"- Audit TXT: {args.audit_text_output}")

    print()
    print("Final verdict: SCRIPT 14a PRODUCTION-INTERFACE PREFLIGHT PASS")
    print("No EOB / Layer A optimization was executed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print()
        print("Final verdict: SCRIPT 14a PRODUCTION-INTERFACE PREFLIGHT FAIL")
        print(f"ERROR: {type(exc).__name__}: {exc}")
        sys.exit(1)
