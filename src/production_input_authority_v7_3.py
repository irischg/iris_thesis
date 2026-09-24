"""Fail-closed v7.3 production annual-input authority.

This module does not contain optimization equations.  It establishes the one
annual planning-input identity accepted for prospective v7.3 production
routing and validates its scientific/data contract before any consumer can use
it.  Historical v7.1 inputs and winter-PV sensitivity artifacts are rejected
even when their numerical columns would otherwise satisfy the legacy loader.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


AUTHORITY_VERSION = "v7.3-production-input-authority-2026-09-24-r1"

ACCEPTED_ANNUAL_RELATIVE_PATH = Path(
    "data/processed/"
    "annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet"
)
ACCEPTED_ANNUAL_SHA256 = (
    "3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428"
)
ACCEPTED_ARTIFACT_ROLE = "reconstructed_pv_mainline"

HISTORICAL_ANNUAL_RELATIVE_PATHS = (
    Path("data/processed/annual_input_v7_1.parquet"),
    Path("data/processed/annual_input_v7_1.csv"),
)
HISTORICAL_ANNUAL_SHA256 = (
    "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e"
)
WINTER_SENSITIVITY_RELATIVE_PATH = Path(
    "data/processed/alternatives/"
    "annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_"
    "2026-09-18.parquet"
)
WINTER_SENSITIVITY_ROLE = "winter_pv_sensitivity_only"

FORMAL_START = pd.Timestamp("2024-11-01 00:00:00")
FORMAL_END_EXCLUSIVE = pd.Timestamp("2025-11-01 00:00:00")
EXPECTED_ROWS = 8760
EXPECTED_FREQUENCY = "h"

AUTHORITY_FILES: Mapping[str, tuple[Path, str]] = {
    "methodology": (
        Path("docs/research_framework_v7_3_2026-09-23.md"),
        "44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a",
    ),
    "evidence": (
        Path("docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md"),
        "e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d",
    ),
    "lifecycle": (
        Path("docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md"),
        "23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d",
    ),
}

IMPOSSIBLE_CSV_RELATIVE_PATH = Path(
    "data/processed/__V7_3_PRODUCTION_CSV_FALLBACK_FORBIDDEN__.csv"
)


class ProductionInputAuthorityError(RuntimeError):
    """Raised whenever the accepted v7.3 input contract cannot be proven."""


@dataclass(frozen=True)
class AnnualInputIdentity:
    path: str
    sha256: str
    artifact_role: str
    row_count: int
    fingerprint_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "artifact_role": self.artifact_role,
            "row_count": self.row_count,
            "fingerprint_sha256": self.fingerprint_sha256,
        }


@dataclass(frozen=True)
class AuthorizedAnnualInput:
    dataframe: pd.DataFrame
    resolved_path: Path
    identity: AnnualInputIdentity
    dataframe_fingerprint: Mapping[str, Any]
    authority_hashes: Mapping[str, Mapping[str, str]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def accepted_annual_path(root: Path) -> Path:
    return (root.resolve() / ACCEPTED_ANNUAL_RELATIVE_PATH).resolve()


def impossible_csv_path(root: Path) -> Path:
    path = (root.resolve() / IMPOSSIBLE_CSV_RELATIVE_PATH).resolve()
    if path.exists():
        raise ProductionInputAuthorityError(
            "The v7.3 no-fallback CSV sentinel unexpectedly exists: " f"{path}"
        )
    return path


def verify_authority_files(root: Path) -> dict[str, dict[str, str]]:
    verified: dict[str, dict[str, str]] = {}
    for label, (relative, expected_sha256) in AUTHORITY_FILES.items():
        path = root.resolve() / relative
        if not path.is_file():
            raise ProductionInputAuthorityError(
                f"Required v7.3 {label} authority is missing: {relative.as_posix()}"
            )
        actual = sha256_file(path)
        if actual != expected_sha256:
            raise ProductionInputAuthorityError(
                f"V7.3 {label} authority SHA256 mismatch: "
                f"expected={expected_sha256}, actual={actual}, path={relative.as_posix()}"
            )
        verified[label] = {
            "path": relative.as_posix(),
            "sha256": actual,
        }
    return verified


def _numeric_vector_sha256(series: pd.Series) -> str:
    values = np.ascontiguousarray(series.to_numpy(dtype=np.float64), dtype="<f8")
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def _timestamp_vector_sha256(series: pd.Series) -> str:
    timestamps = pd.DatetimeIndex(pd.to_datetime(series, errors="raise"))
    values = np.ascontiguousarray(timestamps.asi8, dtype="<i8")
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def _text_vector_sha256(series: pd.Series) -> str:
    payload = "\n".join(series.astype(str).tolist()).encode("utf-8") + b"\n"
    return hashlib.sha256(payload).hexdigest()


def annual_dataframe_fingerprint(dataframe: pd.DataFrame) -> dict[str, Any]:
    required = {
        "timestamp",
        "baseline_load_kw",
        "pv_available_kw",
        "artifact_role",
        "integration_status",
    }
    missing = sorted(required - set(dataframe.columns))
    if missing:
        raise ProductionInputAuthorityError(
            f"Cannot fingerprint annual input; missing columns: {missing}"
        )
    components: dict[str, Any] = {
        "row_count": int(len(dataframe)),
        "timestamp_sha256": _timestamp_vector_sha256(dataframe["timestamp"]),
        "baseline_load_kw_float64_sha256": _numeric_vector_sha256(
            dataframe["baseline_load_kw"]
        ),
        "pv_available_kw_float64_sha256": _numeric_vector_sha256(
            dataframe["pv_available_kw"]
        ),
        "artifact_role_utf8_sha256": _text_vector_sha256(dataframe["artifact_role"]),
        "integration_status_utf8_sha256": _text_vector_sha256(
            dataframe["integration_status"]
        ),
    }
    encoded = json.dumps(
        components, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    components["fingerprint_sha256"] = hashlib.sha256(encoded).hexdigest()
    components["fingerprint_contract"] = (
        "ordered timestamp int64-ns + baseline_load_kw/pv_available_kw little-endian "
        "float64 + UTF-8 artifact_role/integration_status"
    )
    return components


def validate_accepted_annual_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    required = {
        "timestamp",
        "baseline_load_kw",
        "pv_available_kw",
        "artifact_role",
        "integration_status",
    }
    missing = sorted(required - set(dataframe.columns))
    if missing:
        raise ProductionInputAuthorityError(
            f"Accepted v7.3 annual input missing required columns: {missing}"
        )

    out = dataframe.copy()
    if len(out) != EXPECTED_ROWS:
        raise ProductionInputAuthorityError(
            f"Accepted v7.3 annual input rows={len(out)}; expected {EXPECTED_ROWS}."
        )

    timestamps = pd.to_datetime(out["timestamp"], errors="coerce")
    if timestamps.isna().any():
        raise ProductionInputAuthorityError(
            "Accepted v7.3 annual input contains unparsable timestamps."
        )
    if getattr(timestamps.dt, "tz", None) is not None:
        raise ProductionInputAuthorityError(
            "Accepted v7.3 annual input timestamps must be timezone-naive "
            "Asia/Taipei interval-start labels."
        )
    expected = pd.date_range(FORMAL_START, periods=EXPECTED_ROWS, freq=EXPECTED_FREQUENCY)
    if not pd.DatetimeIndex(timestamps).equals(expected):
        raise ProductionInputAuthorityError(
            "Accepted v7.3 annual input is not the exact ordered formal 8,760-hour timeline."
        )
    if timestamps.iloc[-1] + pd.Timedelta(hours=1) != FORMAL_END_EXCLUSIVE:
        raise ProductionInputAuthorityError(
            "Accepted v7.3 annual input does not end at the formal case-year boundary."
        )
    out["timestamp"] = timestamps

    roles = out["artifact_role"].astype("string")
    if roles.isna().any() or not roles.eq(ACCEPTED_ARTIFACT_ROLE).all():
        observed = sorted(roles.dropna().astype(str).unique().tolist())
        raise ProductionInputAuthorityError(
            "Accepted v7.3 artifact_role must be reconstructed_pv_mainline on every "
            f"row; observed={observed}. Sensitivity role {WINTER_SENSITIVITY_ROLE!r} "
            "is never production mainline."
        )

    integration = out["integration_status"].astype("string")
    if integration.isna().any() or not integration.eq("passed").all():
        observed = sorted(integration.dropna().astype(str).unique().tolist())
        raise ProductionInputAuthorityError(
            "Accepted v7.3 integration_status must be passed on every row; "
            f"observed={observed}."
        )

    for column in ("baseline_load_kw", "pv_available_kw"):
        values = pd.to_numeric(out[column], errors="coerce")
        array = values.to_numpy(dtype=float)
        if not np.isfinite(array).all() or (array < 0.0).any():
            raise ProductionInputAuthorityError(
                f"Accepted v7.3 {column} must be finite and non-negative."
            )
        out[column] = values

    return out


def _reject_nonaccepted_path(root: Path, requested: Path, accepted: Path) -> None:
    if requested.suffix.lower() != ".parquet":
        raise ProductionInputAuthorityError(
            "V7.3 production mainline is parquet-only; CSV fallback is forbidden."
        )
    for historical in HISTORICAL_ANNUAL_RELATIVE_PATHS:
        if _same_path(requested, root.resolve() / historical):
            raise ProductionInputAuthorityError(
                "Historical annual_input_v7_1.* is a conservative stress/predecessor "
                "artifact and is forbidden for v7.3 production mainline."
            )
    if _same_path(requested, root.resolve() / WINTER_SENSITIVITY_RELATIVE_PATH):
        raise ProductionInputAuthorityError(
            "winter_pv_sensitivity_only/promotion-source artifacts are not accepted "
            "v7.3 production mainline inputs."
        )
    if not _same_path(requested, accepted):
        raise ProductionInputAuthorityError(
            "V7.3 production mainline requires the exact accepted parquet path: "
            f"{ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix()}"
        )


def load_accepted_v7_3_annual_input(
    root: Path,
    *,
    parquet_path: Path | None = None,
    claimed_sha256: str | None = None,
) -> AuthorizedAnnualInput:
    root = root.resolve()
    accepted = accepted_annual_path(root)
    requested = (parquet_path or accepted).resolve()
    _reject_nonaccepted_path(root, requested, accepted)

    if claimed_sha256 is not None and claimed_sha256.lower() != ACCEPTED_ANNUAL_SHA256:
        raise ProductionInputAuthorityError(
            "Supplied annual-input SHA256 is not the accepted v7.3 identity: "
            f"{claimed_sha256}"
        )
    if not requested.is_file():
        raise ProductionInputAuthorityError(
            f"Accepted v7.3 parquet is missing: {ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix()}"
        )

    authority_hashes = verify_authority_files(root)
    actual_sha256 = sha256_file(requested)
    if actual_sha256 != ACCEPTED_ANNUAL_SHA256:
        raise ProductionInputAuthorityError(
            "Accepted v7.3 parquet SHA256 mismatch: "
            f"expected={ACCEPTED_ANNUAL_SHA256}, actual={actual_sha256}"
        )

    try:
        raw = pd.read_parquet(requested)
    except Exception as exc:
        raise ProductionInputAuthorityError(
            "Accepted v7.3 parquet could not be read; CSV fallback is forbidden."
        ) from exc
    validated = validate_accepted_annual_dataframe(raw)
    fingerprint = annual_dataframe_fingerprint(validated)
    identity = AnnualInputIdentity(
        path=ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        sha256=actual_sha256,
        artifact_role=ACCEPTED_ARTIFACT_ROLE,
        row_count=EXPECTED_ROWS,
        fingerprint_sha256=str(fingerprint["fingerprint_sha256"]),
    )
    return AuthorizedAnnualInput(
        dataframe=validated,
        resolved_path=requested,
        identity=identity,
        dataframe_fingerprint=fingerprint,
        authority_hashes=authority_hashes,
    )


def require_same_annual_identity(
    expected: AnnualInputIdentity,
    received: AnnualInputIdentity,
    *,
    consumer: str,
) -> None:
    if expected != received:
        raise ProductionInputAuthorityError(
            f"{consumer} received a different annual artifact identity: "
            f"expected={expected.as_dict()}, received={received.as_dict()}"
        )
