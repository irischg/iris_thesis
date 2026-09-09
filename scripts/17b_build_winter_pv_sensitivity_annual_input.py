from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from types import ModuleType
from typing import Any
import uuid

import numpy as np
import pandas as pd


SCRIPT_VERSION = "v7.2-winter-pv-sensitivity-annual-input-build-2026-09-09-r1"
METHODOLOGY = "v7.2"
ARTIFACT_ROLE = "winter_pv_sensitivity_only"
SENSITIVITY_METHOD = "cwa_hourly_ghi_ratio_median_all_eligible_v7_2"

EXPECTED_BRANCH = "thesis-v7"
EXPECTED_HEAD = "2b353c4caabc9f81229445fa2683f0053c2c528d"
EXPECTED_CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9"
)
EXPECTED_SCRIPT_16A_VERSION = (
    "v7.2-layer-a-analytical-representative-binary-preflight-transition-candidate1-"
    "reduced-native-max-provenance-2026-09-06-r10"
)
EXPECTED_SCRIPT_17A_VERSION = (
    "v7.2-winter-pv-longblock-holdout-validation-2026-09-09-r2"
)
EXPECTED_CWA_REFERENCE_VERSION = "v7-pv-cwa-headtohead-validation-r3-2026-08-16"
FORMAL_17A_RUN_ID = "20260909T042957292822Z_7de1c7a4f4"

EXPECTED_SHA256 = {
    "framework_v7_2": "bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5",
    "registry_v7_2": "8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e",
    "production_checkpoint": "ebe619b440f011e525f0b9c43a0b4512f44b6f9efa049c787e8049e8c1f51b73",
    "annual_core": "d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0",
    "script_16a": "c9e01022a7596b2fdf2f42e1a84855585c7901b06af100f0cb8d189852ee502f",
    "script_15b": "9a5f61d19bc279920f51f67294ef96ddcd7623ffe240482ff66b88e029eafc60",
    "script_15c": "14fd9f3363979dd6af6f50723a75477e1525b9330265a0a820d11eec1774f408",
    "script_17a": "c8bb665fb607b129df2187435c5454e49dbf6faff3ca25013a3eda7d26670c91",
    "script_04b": "c9259d7792e4e60713bb8b7eb79df39ef51fab9837730efab73011fb7a6130e7",
    "canonical_annual_input": "e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e",
    "protocol": "630c9c20a388fde31d424d8b1e43d99cd05c5d2c9cf51b17e2d36f90fb50f525",
    "observed_parquet": "fdf930f2dde9ea4461610752920d6659d42be42d3ac3981aa744c22482117e30",
    "observed_csv": "c5039b55049f28bd4b99d2dfb0dcd0c5f9a26790e90c8d6c6947e3d4c8ba05d3",
    "cwa_input": "3697f7d0d56bc55da119cbfc6854cb358cc0b1ee029f503d2f49ad03258f51c8",
    "17a_run_manifest": "374a52ebc2db0ad0b4c26a05b51a6ed50273dd1dc803164e99da4560ac14d14b",
    "17a_completion_manifest": "678a11d8acd0dec10020f39c011917a998d75c0055fd568fe14d75a7226f34f6",
    "17a_final_decision": "454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594",
}

TARGET_START = pd.Timestamp("2024-11-01 00:00:00")
TARGET_END_EXCLUSIVE = pd.Timestamp("2024-12-31 23:00:00")
EXPECTED_TARGET_COUNT = 1_463
EXPECTED_TARGET_TIMESTAMP_SHA256 = (
    "98d635c9578b9118d066dce2e0bf718c70ed5517005439cd7ee473aba14db2ad"
)
EXPECTED_TARGET_STATUS_COUNTS = {"pre_system": 600, "missing_winter": 863}
EXPECTED_TRAINING_COUNT = 7_287
EXPECTED_TRAINING_START = pd.Timestamp("2024-12-31 23:00:00")
EXPECTED_TRAINING_END = pd.Timestamp("2025-10-31 23:00:00")
EXPECTED_TRAINING_TIMESTAMP_SHA256 = (
    "10d627e68f1c785e1010df76ec76e1f5ba32fcb95decd379a1b6566f316b6051"
)
EXPECTED_TRAINING_SET_SHA256 = (
    "209577c448cca07e008d889b2ce360bf5f9c90251c00ba2b02c76999b4c52b01"
)
EXPECTED_RATIO_FIT_COUNT = 3_011
EXPECTED_GLOBAL_RATIO = 312.81553398058253
EXPECTED_PV_CAP_KW = 357.0
EXPECTED_RATIO_FIT_GHI_THRESHOLD = 0.05
EXPECTED_DAYLIGHT_GHI_THRESHOLD = 0.01
EXPECTED_DAYLIGHT_COUNT = 619
EXPECTED_NIGHT_COUNT = 844
EXPECTED_HOD_COUNTS = {
    5: 1,
    6: 173,
    7: 236,
    8: 267,
    9: 285,
    10: 290,
    11: 293,
    12: 294,
    13: 293,
    14: 284,
    15: 265,
    16: 223,
    17: 107,
}
EXPECTED_HOD_MEDIANS = {
    5: 208.42105263157896,
    6: 204.54545454545456,
    7: 259.6932084309134,
    8: 308.0597014925374,
    9: 326.42487046632124,
    10: 331.7678637541651,
    11: 334.2089552238806,
    12: 333.11244979919684,
    13: 333.33333333333337,
    14: 321.9742905651225,
    15: 303.87096774193543,
    16: 258.75,
    17: 223.44827586206898,
}

PRIMARY_COLUMN = "pv_available_kw"
DERIVED_COLUMNS = (
    "pv_available_kwh",
    "residual_load_kw",
    "grid_demand_before_bess_kw",
    "pv_surplus_before_bess_kw",
)
ADDITIVE_COLUMNS = (
    "artifact_role",
    "winter_pv_sensitivity_applied",
    "winter_pv_sensitivity_method",
    "winter_pv_sensitivity_protocol_sha256",
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build only the isolated v7.2 Winter-PV sensitivity annual input. "
            "This script never invokes an optimizer or computes economic results."
        )
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=project_root() / "data" / "processed" / "alternatives",
    )
    parser.add_argument(
        "--audit-root",
        type=Path,
        default=project_root() / "results" / "data_audit" / "winter_pv_17b",
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


def stable_frame_sha256(data: pd.DataFrame, columns: list[str]) -> str:
    frame = data.loc[:, columns].copy()
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            frame[column] = frame[column].dt.strftime("%Y-%m-%d %H:%M:%S")
    text = frame.to_csv(index=False, lineterminator="\n", float_format="%.17g")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_safe(value: Any) -> Any:
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
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


def temporary_path(final_path: Path) -> Path:
    return final_path.with_name(f".{final_path.name}.{uuid.uuid4().hex}.tmp")


def promote_non_overwriting(temp_path: Path, final_path: Path) -> None:
    if final_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing artifact: {final_path}")
    os.link(temp_path, final_path)
    temp_path.unlink()


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = temporary_path(path)
    try:
        with temp_path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(json_safe(payload), handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        promote_non_overwriting(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def write_csv_temp(data: pd.DataFrame, final_path: Path) -> Path:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = temporary_path(final_path)
    data.to_csv(
        temp_path,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        float_format="%.17g",
        date_format="%Y-%m-%d %H:%M:%S",
    )
    return temp_path


def write_parquet_temp(data: pd.DataFrame, final_path: Path) -> Path:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = temporary_path(final_path)
    data.to_parquet(temp_path, index=False, engine="pyarrow")
    return temp_path


def git_value(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise RuntimeError(message)


def require_hash(path: Path, expected: str, label: str) -> str:
    require(path.is_file(), f"Required {label} is missing: {path}")
    actual = sha256_file(path)
    require(
        actual == expected,
        f"{label} SHA-256 mismatch: expected={expected}, actual={actual}",
    )
    return actual


def assignment_value(path: Path, name: str) -> str:
    pattern = re.compile(rf'^\s*{re.escape(name)}\s*=\s*[\"\']([^\"\']+)[\"\']')
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)
    raise RuntimeError(f"Cannot find {name} in {path}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"Expected a JSON object: {path}")
    return value


def load_reference_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("winter_pv_cwa_reference_17b", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load CWA reference module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(
        getattr(module, "SCRIPT_VERSION", None) == EXPECTED_CWA_REFERENCE_VERSION,
        "Script 04b version does not match the accepted CWA reference version.",
    )
    return module


def normalize_bool(series: pd.Series, *, label: str) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        require(not series.isna().any(), f"{label} contains missing Boolean values.")
        return series.astype(bool)
    mapped = (
        series.astype("string")
        .str.strip()
        .str.lower()
        .map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
    )
    if mapped.isna().any():
        invalid = sorted(series.loc[mapped.isna()].astype(str).unique().tolist())
        raise RuntimeError(f"{label} contains invalid Boolean values: {invalid[:10]}")
    return mapped.astype(bool)


def series_equal(left: pd.Series, right: pd.Series) -> pd.Series:
    require(len(left) == len(right), "Cannot compare series with different lengths.")
    paired_missing = left.isna().to_numpy() & right.isna().to_numpy()
    compared = left.reset_index(drop=True).eq(right.reset_index(drop=True))
    equal_values = compared.fillna(False).to_numpy(dtype=bool)
    return pd.Series(paired_missing | equal_values, index=left.index, dtype=bool)


def changed_mask(left: pd.Series, right: pd.Series) -> pd.Series:
    return ~series_equal(left, right)


def max_numeric_difference(left: pd.Series, right: pd.Series) -> float | None:
    if not (
        pd.api.types.is_numeric_dtype(left.dtype)
        and pd.api.types.is_numeric_dtype(right.dtype)
    ):
        return None
    valid = left.notna() & right.notna()
    if not valid.any():
        return 0.0
    difference = np.abs(
        left.loc[valid].to_numpy(dtype="float64")
        - right.loc[valid].to_numpy(dtype="float64")
    )
    return float(difference.max(initial=0.0))


def scripts_through_17a(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "scripts").glob("*.py")):
        match = re.match(r"^(\d+)([a-z]?)_", path.name)
        if match is None:
            continue
        number = int(match.group(1))
        suffix = match.group(2)
        if number < 17 or (number == 17 and suffix <= "a"):
            result[relative_path(path, root)] = sha256_file(path)
    return result


def validate_no_solve_source(script_path: Path) -> dict[str, Any]:
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    forbidden_calls: list[str] = []
    forbidden_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name: str | None = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in {"optimize", "solve", "run_eob", "run_layer_a"}:
                forbidden_calls.append(f"{name}@{node.lineno}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                if name == "gurobipy" or name.startswith("src.annual_design_model_v7_2"):
                    forbidden_imports.append(f"{name}@{node.lineno}")
    require(not forbidden_calls, f"No-solve source gate found calls: {forbidden_calls}")
    require(not forbidden_imports, f"No-solve source gate found imports: {forbidden_imports}")
    return {
        "ast_parse_pass": True,
        "forbidden_solver_calls": forbidden_calls,
        "forbidden_solver_or_core_imports": forbidden_imports,
        "annual_optimizer_invoked": False,
        "eob_run": False,
        "layer_a_run": False,
        "representative_cases_run": False,
        "matrix_81_point_run": False,
        "script_17c_run": False,
    }


def build_diff_audit(
    canonical: pd.DataFrame,
    alternative: pd.DataFrame,
    target_mask: pd.Series,
) -> pd.DataFrame:
    timestamps = pd.to_datetime(canonical["timestamp"])
    rows: list[dict[str, Any]] = []
    for column in canonical.columns:
        classification = (
            "B"
            if column == PRIMARY_COLUMN
            else "C"
            if column in DERIVED_COLUMNS
            else "A"
        )
        left = canonical[column]
        right = alternative[column]
        changed = changed_mask(left, right)
        changed_count = int(changed.sum())
        outside_count = int((changed & ~target_mask).sum())
        changed_times = timestamps.loc[changed]
        dtype_same = str(left.dtype) == str(right.dtype)
        gate_pass = dtype_same and (
            changed_count == 0 if classification == "A" else outside_count == 0
        )
        rows.append(
            {
                "column": column,
                "classification": classification,
                "dtype_canonical": str(left.dtype),
                "dtype_alternative": str(right.dtype),
                "changed_row_count": changed_count,
                "unchanged_row_count": int(len(canonical) - changed_count),
                "max_absolute_numeric_difference": max_numeric_difference(left, right),
                "first_changed_timestamp": changed_times.min() if changed_count else None,
                "last_changed_timestamp": changed_times.max() if changed_count else None,
                "changed_outside_target_count": outside_count,
                "gate_status": "PASS" if gate_pass else "FAIL",
                "is_new": False,
                "non_null_count": int(right.notna().sum()),
                "unique_values": None,
                "true_count": None,
                "false_count": None,
                "target_true_count": None,
                "outside_target_true_count": None,
            }
        )

    for column in ADDITIVE_COLUMNS:
        values = alternative[column]
        unique_values = sorted(values.dropna().unique().tolist(), key=lambda item: str(item))
        is_bool = pd.api.types.is_bool_dtype(values.dtype)
        true_mask = values.astype(bool) if is_bool else pd.Series(False, index=values.index)
        rows.append(
            {
                "column": column,
                "classification": "D",
                "dtype_canonical": None,
                "dtype_alternative": str(values.dtype),
                "changed_row_count": int(len(alternative)),
                "unchanged_row_count": 0,
                "max_absolute_numeric_difference": None,
                "first_changed_timestamp": timestamps.min(),
                "last_changed_timestamp": timestamps.max(),
                "changed_outside_target_count": None,
                "gate_status": "PASS",
                "is_new": True,
                "non_null_count": int(values.notna().sum()),
                "unique_values": json.dumps(json_safe(unique_values), ensure_ascii=False),
                "true_count": int(true_mask.sum()) if is_bool else None,
                "false_count": int((~true_mask).sum()) if is_bool else None,
                "target_true_count": int((true_mask & target_mask).sum()) if is_bool else None,
                "outside_target_true_count": (
                    int((true_mask & ~target_mask).sum()) if is_bool else None
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    args = parse_args()
    root = project_root()
    script_path = Path(__file__).resolve()
    started_utc = utc_now()
    run_id = new_run_id(started_utc)

    paths = {
        "framework_v7_2": root / "docs" / "research_framework_v7_2_2026-08-24.md",
        "registry_v7_2": root / "docs" / "thesis_literature_evidence_registry_v7_2_2026-08-24.md",
        "production_checkpoint": root / "docs" / "checkpoints" / "production_checkpoint_manifest_v7_2_2026-09-09.json",
        "checkpoint_validator": root / "scripts" / "18a_validate_production_checkpoint.py",
        "annual_core": root / "src" / "annual_design_model_v7_2.py",
        "script_16a": root / "scripts" / "16a_preflight_layer_a_representative_binary_cases.py",
        "script_15b": root / "scripts" / "15b_freeze_production_eob_baseline.py",
        "script_15c": root / "scripts" / "15c_validate_production_eob_rainflow.py",
        "script_17a": root / "scripts" / "17a_validate_winter_pv_longblock_holdouts.py",
        "script_04b": root / "scripts" / "04b_compare_pv_donor_vs_cwa.py",
        "canonical_annual_input": root / "data" / "processed" / "annual_input_v7_1.parquet",
        "protocol": root / "docs" / "winter_pv_longblock_sensitivity_protocol_v7_2_2026-09-07.md",
        "observed_parquet": root / "data" / "processed" / "ntust_case_year_observed.parquet",
        "observed_csv": root / "data" / "processed" / "ntust_case_year_observed.csv",
        "cwa_input": root / "data" / "raw" / "cwa_codis" / "466920" / "cwa_466920_formal_8760_ghi_temperature.csv",
    }
    accepted_run_dir = (
        root / "results" / "data_audit" / "winter_pv_holdouts" / FORMAL_17A_RUN_ID
    )
    paths.update(
        {
            "17a_run_manifest": accepted_run_dir / "run_manifest.json",
            "17a_completion_manifest": accepted_run_dir / "completion_manifest.json",
            "17a_final_decision": accepted_run_dir / "final_validation_decision.json",
        }
    )

    allowed_output_root = (root / "data" / "processed" / "alternatives").resolve()
    allowed_audit_root = (root / "results" / "data_audit" / "winter_pv_17b").resolve()
    output_root = args.output_root.resolve()
    audit_root = args.audit_root.resolve()
    require(output_root == allowed_output_root, f"17b output root must be {allowed_output_root}")
    require(audit_root == allowed_audit_root, f"17b audit root must be {allowed_audit_root}")

    basename = "annual_input_v7_2_winter_pv_sensitivity_protocol_2026-09-07"
    output_parquet = output_root / f"{basename}.parquet"
    output_manifest = output_root / f"{basename}_manifest.json"
    output_csv = output_root / f"{basename}.csv"
    run_dir = audit_root / run_id
    diff_audit_path = run_dir / f"{basename}_column_diff_audit.csv"
    run_manifest_path = run_dir / "run_manifest.json"
    completion_path = run_dir / "completion_manifest.json"
    failure_path = run_dir / "failure_manifest.json"

    for collision_path in (output_parquet, output_manifest, output_csv):
        require(not collision_path.exists(), f"Refusing path collision: {collision_path}")
    require(not run_dir.exists(), f"Refusing run-directory collision: {run_dir}")

    branch = git_value(root, "branch", "--show-current")
    head = git_value(root, "rev-parse", "HEAD")
    origin_head = git_value(root, "rev-parse", "origin/thesis-v7")
    tracked_diff = git_value(root, "diff", "--name-only") or ""
    staged_diff = git_value(root, "diff", "--cached", "--name-only") or ""
    require(branch == EXPECTED_BRANCH, f"Expected branch {EXPECTED_BRANCH}, found {branch}")
    require(head == EXPECTED_HEAD, f"Expected HEAD {EXPECTED_HEAD}, found {head}")
    require(origin_head == EXPECTED_HEAD, f"Expected origin/thesis-v7 {EXPECTED_HEAD}, found {origin_head}")
    require(not tracked_diff, f"Tracked worktree divergence exists: {tracked_diff.splitlines()}")
    require(not staged_diff, f"Staged worktree divergence exists: {staged_diff.splitlines()}")

    source_hashes_at_start = {
        label: require_hash(path, EXPECTED_SHA256[label], label)
        for label, path in paths.items()
        if label in EXPECTED_SHA256
    }
    require(
        assignment_value(paths["annual_core"], "CORE_VERSION") == EXPECTED_CORE_VERSION,
        "Annual core version mismatch.",
    )
    require(
        assignment_value(paths["script_16a"], "SCRIPT_VERSION")
        == EXPECTED_SCRIPT_16A_VERSION,
        "Script 16a version mismatch.",
    )
    require(
        assignment_value(paths["script_17a"], "SCRIPT_VERSION")
        == EXPECTED_SCRIPT_17A_VERSION,
        "Script 17a version mismatch.",
    )
    protocol_text = paths["protocol"].read_text(encoding="utf-8")
    require(
        "Protocol status:** FROZEN / APPROVED FOR IMPLEMENTATION" in protocol_text,
        "Winter-PV protocol is not frozen/approved for implementation.",
    )

    checkpoint = load_json(paths["production_checkpoint"])
    require(
        checkpoint.get("status") == "FROZEN_PRODUCTION_LINEAGE",
        "Production checkpoint status is not FROZEN_PRODUCTION_LINEAGE.",
    )
    validator = subprocess.run(
        [sys.executable, str(paths["checkpoint_validator"])],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    require(validator.returncode == 0, f"Checkpoint validator failed: {validator.stderr}")
    validator_payload = json.loads(validator.stdout)
    require(validator_payload.get("status") == "PASS", "Checkpoint validator did not PASS.")
    require(
        int(validator_payload.get("artifact_hash_checks", -1)) == 22,
        "Checkpoint validator did not verify exactly 22 controlled artifact hashes.",
    )

    run17a = load_json(paths["17a_run_manifest"])
    completion17a = load_json(paths["17a_completion_manifest"])
    decision17a = load_json(paths["17a_final_decision"])
    require(run17a.get("run_id") == FORMAL_17A_RUN_ID, "Formal 17a run ID mismatch.")
    require(
        run17a.get("script_version") == EXPECTED_SCRIPT_17A_VERSION,
        "Formal 17a run used an unexpected Script 17a version.",
    )
    require(
        run17a.get("source_hashes_at_start", {}).get("cwa_reference_script_04b")
        == EXPECTED_SHA256["script_04b"],
        "Formal 17a provenance does not identify the current full Script 04b hash.",
    )
    require(
        completion17a.get("status") == "COMPLETED_PASS_FOR_SENSITIVITY"
        and completion17a.get("decision") == "PASS_FOR_SENSITIVITY",
        "Formal 17a completion status is not accepted for sensitivity.",
    )
    require(
        completion17a.get("holdout_status") == {"H1": "PASS", "H2": "PASS", "H3": "PASS"},
        "Formal 17a H1/H2/H3 status mismatch.",
    )
    require(
        decision17a.get("WINTER_PV_RECONSTRUCTION_VALIDATION") == "PASS_FOR_SENSITIVITY",
        "Formal 17a final decision is not PASS_FOR_SENSITIVITY.",
    )

    script_sha256 = sha256_file(script_path)
    no_solve_assertions = validate_no_solve_source(script_path)
    protected_scripts_at_start = scripts_through_17a(root)
    core_sha256_before = sha256_file(paths["annual_core"])
    canonical_sha256_before = sha256_file(paths["canonical_annual_input"])
    git_status_at_start = git_value(root, "status", "--porcelain=v1") or ""

    run_dir.mkdir(parents=True, exist_ok=False)
    write_json_atomic(
        run_manifest_path,
        {
            "run_id": run_id,
            "run_started_utc": utc_text(started_utc),
            "mode": "WINTER_PV_SENSITIVITY_ANNUAL_INPUT_BUILD_ONLY_NO_SOLVE",
            "methodology": METHODOLOGY,
            "role": ARTIFACT_ROLE,
            "script_version": SCRIPT_VERSION,
            "script_sha256": script_sha256,
            "git": {
                "commit": head,
                "branch": branch,
                "origin_thesis_v7": origin_head,
                "origin_comparison_basis": "local_origin_tracking_reference",
                "dirty": bool(git_status_at_start),
                "status_porcelain_at_start": git_status_at_start.splitlines(),
            },
            "expected_outputs": {
                "parquet": relative_path(output_parquet, root),
                "csv": None,
                "sensitivity_manifest": relative_path(output_manifest, root),
                "diff_audit": relative_path(diff_audit_path, root),
                "completion_manifest": relative_path(completion_path, root),
            },
            "no_solve_assertions": no_solve_assertions,
        },
    )

    staged_paths: list[Path] = []
    try:
        reference = load_reference_module(paths["script_04b"])
        require(
            float(reference.RATIO_FIT_GHI_THRESHOLD) == EXPECTED_RATIO_FIT_GHI_THRESHOLD,
            "Script 04b ratio-fit GHI threshold mismatch.",
        )
        require(
            float(reference.DAYLIGHT_GHI_THRESHOLD) == EXPECTED_DAYLIGHT_GHI_THRESHOLD,
            "Script 04b daylight GHI threshold mismatch.",
        )
        source_function = reference.predict_hourly_ghi_ratio_median
        source_function_identity = (
            f"scripts/04b_compare_pv_donor_vs_cwa.py::{source_function.__name__}"
        )
        source_function_sha256 = hashlib.sha256(
            inspect.getsource(source_function).encode("utf-8")
        ).hexdigest()

        canonical = pd.read_parquet(paths["canonical_annual_input"])
        canonical_columns = canonical.columns.tolist()
        require(len(canonical) == 8_760, "Canonical annual input does not have 8,760 rows.")
        required_columns = {
            "timestamp",
            "baseline_load_kw",
            "pv_available_kw",
            "pv_status",
            "pv_reconstructed",
            "pv_reconstruction_method",
            "pv_long_unavailable_assumption",
            "pv_long_unavailable_flag",
            "ghi_kwh_m2",
            "outage_contaminated_flag",
            *DERIVED_COLUMNS,
        }
        require(
            required_columns.issubset(canonical.columns),
            f"Canonical input is missing columns: {sorted(required_columns - set(canonical.columns))}",
        )
        require(
            not set(ADDITIVE_COLUMNS).intersection(canonical.columns),
            "Canonical input already contains a 17b additive provenance column.",
        )
        canonical_timestamps = pd.to_datetime(canonical["timestamp"])
        require(canonical_timestamps.notna().all(), "Canonical timestamps contain missing values.")
        require(canonical_timestamps.is_unique, "Canonical timestamps are not unique.")
        canonical_timestamp_sha256 = stable_frame_sha256(canonical, ["timestamp"])

        target_mask = (
            canonical["pv_status"].astype("string").isin(["pre_system", "missing_winter"])
            & canonical_timestamps.ge(TARGET_START)
            & canonical_timestamps.lt(TARGET_END_EXCLUSIVE)
        )
        target = canonical.loc[target_mask].copy().sort_values("timestamp").reset_index(drop=True)
        expected_target_index = pd.date_range(
            TARGET_START, TARGET_END_EXCLUSIVE, freq="h", inclusive="left"
        )
        require(len(target) == EXPECTED_TARGET_COUNT, "Winter target row count mismatch.")
        require(target["timestamp"].nunique() == EXPECTED_TARGET_COUNT, "Winter target has duplicate timestamps.")
        require(
            pd.DatetimeIndex(target["timestamp"]).equals(expected_target_index),
            "Winter target timeline is not exact.",
        )
        target_timestamp_sha256 = stable_frame_sha256(target, ["timestamp"])
        require(
            target_timestamp_sha256 == EXPECTED_TARGET_TIMESTAMP_SHA256,
            "Winter target timestamp SHA-256 mismatch.",
        )
        target_status_counts = {
            str(key): int(value)
            for key, value in target["pv_status"].value_counts().sort_index().items()
        }
        require(target_status_counts == EXPECTED_TARGET_STATUS_COUNTS, "Winter target status counts mismatch.")

        short_gap_mask = (
            canonical_timestamps.between(
                pd.Timestamp("2025-04-19 14:00:00"),
                pd.Timestamp("2025-04-19 16:00:00"),
                inclusive="both",
            )
            | canonical_timestamps.between(
                pd.Timestamp("2025-08-02 09:00:00"),
                pd.Timestamp("2025-08-02 15:00:00"),
                inclusive="both",
            )
        )
        require(int(short_gap_mask.sum()) == 10, "Protected short-gap timestamp count mismatch.")
        require(not (short_gap_mask & target_mask).any(), "Winter target intersects protected short-gap rows.")
        require(
            canonical.loc[short_gap_mask, "pv_reconstruction_method"]
            .astype(str)
            .eq("cwa_hourly_ghi_ratio_median_leave_target_day_out")
            .all(),
            "Protected short-gap method identity mismatch.",
        )

        observed_raw, observed_path_used = reference.read_observed(
            paths["observed_parquet"], paths["observed_csv"]
        )
        require(
            Path(observed_path_used).resolve() == paths["observed_parquet"].resolve(),
            "17b did not use the controlled observed Parquet input.",
        )
        observed = reference.prepare_observed(observed_raw)
        observed["outage_contaminated_flag"] = normalize_bool(
            observed["outage_contaminated_flag"], label="outage_contaminated_flag"
        )
        weather = reference.read_cwa(paths["cwa_input"])
        controlled = observed.merge(
            weather[["timestamp", "ghi_kwh_m2", "air_temperature_c"]],
            on="timestamp",
            how="left",
            validate="one_to_one",
        )
        require(len(controlled) == 8_760, "Controlled observed/CWA merge is not 8,760 rows.")
        controlled_timestamps = pd.to_datetime(controlled["timestamp"])
        controlled_target_mask = (
            controlled["pv_status"].astype("string").isin(["pre_system", "missing_winter"])
            & controlled_timestamps.ge(TARGET_START)
            & controlled_timestamps.lt(TARGET_END_EXCLUSIVE)
        )
        controlled_target = (
            controlled.loc[controlled_target_mask]
            .copy()
            .sort_values("timestamp")
            .reset_index(drop=True)
        )
        require(
            pd.DatetimeIndex(controlled_target["timestamp"]).equals(
                pd.DatetimeIndex(target["timestamp"])
            ),
            "Controlled target timestamps differ from canonical target timestamps.",
        )
        require(
            controlled_target["pv_status"].astype("string").reset_index(drop=True).equals(
                target["pv_status"].astype("string").reset_index(drop=True)
            ),
            "Controlled target statuses differ from canonical target statuses.",
        )
        canonical_target_ghi = pd.to_numeric(target["ghi_kwh_m2"], errors="coerce")
        controlled_target_ghi = pd.to_numeric(
            controlled_target["ghi_kwh_m2"], errors="coerce"
        )
        require(
            canonical_target_ghi.notna().all()
            and controlled_target_ghi.notna().all()
            and np.isfinite(controlled_target_ghi.to_numpy(dtype="float64")).all(),
            "Target GHI is incomplete or non-finite.",
        )
        require(
            np.array_equal(
                canonical_target_ghi.to_numpy(dtype="float64"),
                controlled_target_ghi.to_numpy(dtype="float64"),
            ),
            "Canonical target GHI differs from the controlled Script 04b CWA normalization.",
        )

        explicit_long_target = (
            controlled["pv_status"].astype("string").isin(["pre_system", "missing_winter"])
            & controlled_timestamps.ge(TARGET_START)
            & controlled_timestamps.lt(TARGET_END_EXCLUSIVE)
        )
        eligible_mask = (
            controlled["pv_status"].astype("string").eq("valid")
            & (~controlled["outage_contaminated_flag"])
            & controlled["observed_pv_kw"].notna()
            & controlled["ghi_kwh_m2"].notna()
            & (~explicit_long_target)
        )
        train = controlled.loc[eligible_mask].copy().sort_values("timestamp").reset_index(drop=True)
        train["hour"] = train["timestamp"].dt.hour.astype(int)
        target_training_intersection = set(train["timestamp"]).intersection(
            set(controlled_target["timestamp"])
        )
        require(not target_training_intersection, "Winter target timestamps leaked into training.")
        require(len(train) == EXPECTED_TRAINING_COUNT, "Eligible training-row count mismatch.")
        require(
            train["timestamp"].min() == EXPECTED_TRAINING_START
            and train["timestamp"].max() == EXPECTED_TRAINING_END,
            "Eligible training range mismatch.",
        )
        training_timestamp_sha256 = stable_frame_sha256(train, ["timestamp"])
        training_set_sha256 = stable_frame_sha256(
            train,
            [
                "timestamp",
                "observed_pv_kw",
                "pv_status",
                "outage_contaminated_flag",
                "ghi_kwh_m2",
            ],
        )
        require(
            training_timestamp_sha256 == EXPECTED_TRAINING_TIMESTAMP_SHA256,
            "Training timestamp SHA-256 mismatch.",
        )
        require(
            training_set_sha256 == EXPECTED_TRAINING_SET_SHA256,
            "Full Script-17a-style training-set SHA-256 mismatch.",
        )

        fit = train.loc[
            train["ghi_kwh_m2"].gt(float(reference.RATIO_FIT_GHI_THRESHOLD))
        ].copy()
        fit["pv_per_ghi"] = fit["observed_pv_kw"] / fit["ghi_kwh_m2"]
        require(len(fit) == EXPECTED_RATIO_FIT_COUNT, "CWA ratio-fit row count mismatch.")
        require(
            np.isfinite(fit["pv_per_ghi"].to_numpy(dtype="float64")).all(),
            "CWA ratio-fit values are not finite.",
        )
        global_ratio = float(fit["pv_per_ghi"].median())
        hod_counts = {int(k): int(v) for k, v in fit.groupby("hour").size().items()}
        hod_medians = {
            int(k): float(v) for k, v in fit.groupby("hour")["pv_per_ghi"].median().items()
        }
        require(global_ratio == EXPECTED_GLOBAL_RATIO, "Global median PV/GHI ratio mismatch.")
        require(hod_counts == EXPECTED_HOD_COUNTS, "HOD ratio-fit counts mismatch.")
        require(hod_medians == EXPECTED_HOD_MEDIANS, "HOD median PV/GHI ratios mismatch.")

        candidate_target = controlled_target[["timestamp", "ghi_kwh_m2"]].copy()
        prediction, reference_parameters = source_function(train, candidate_target)
        prediction = np.asarray(prediction, dtype="float64")
        pv_cap_kw = float(train["observed_pv_kw"].max())
        require(pv_cap_kw == EXPECTED_PV_CAP_KW, "Training-derived PV cap mismatch.")
        require(
            float(reference_parameters["parameter_1"]) == global_ratio
            and float(reference_parameters["pv_cap_kw"]) == pv_cap_kw,
            "Script 04b prediction parameters differ from independently fitted values.",
        )
        target_ghi = candidate_target["ghi_kwh_m2"].to_numpy(dtype="float64")
        daylight_mask = target_ghi > EXPECTED_DAYLIGHT_GHI_THRESHOLD
        night_mask = ~daylight_mask
        target_hod = candidate_target["timestamp"].dt.hour
        fallback_mask = ~target_hod.isin(hod_medians)
        require(int(daylight_mask.sum()) == EXPECTED_DAYLIGHT_COUNT, "Target daylight count mismatch.")
        require(int(night_mask.sum()) == EXPECTED_NIGHT_COUNT, "Target night count mismatch.")
        require(
            int((fallback_mask.to_numpy() & daylight_mask).sum()) == 0,
            "A daylight target row unexpectedly needs the global ratio fallback.",
        )
        require(len(prediction) == EXPECTED_TARGET_COUNT, "Prediction count mismatch.")
        require(np.isfinite(prediction).all(), "Predictions contain a non-finite value.")
        require(
            bool(((prediction >= 0.0) & (prediction <= pv_cap_kw)).all()),
            "Predictions violate the physical 0-to-cap range.",
        )
        require(
            bool((prediction[night_mask] == 0.0).all()),
            "GHI <= daylight threshold does not imply zero prediction.",
        )

        alternative = canonical.copy(deep=True)
        alternative.loc[target_mask, PRIMARY_COLUMN] = prediction
        alternative.loc[target_mask, "pv_available_kwh"] = alternative.loc[
            target_mask, PRIMARY_COLUMN
        ]
        alternative.loc[target_mask, "residual_load_kw"] = (
            alternative.loc[target_mask, "baseline_load_kw"]
            - alternative.loc[target_mask, PRIMARY_COLUMN]
        )
        alternative.loc[target_mask, "grid_demand_before_bess_kw"] = np.maximum(
            alternative.loc[target_mask, "residual_load_kw"].to_numpy(dtype="float64"),
            0.0,
        )
        alternative.loc[target_mask, "pv_surplus_before_bess_kw"] = np.maximum(
            -alternative.loc[target_mask, "residual_load_kw"].to_numpy(dtype="float64"),
            0.0,
        )
        alternative["artifact_role"] = pd.Series(
            [ARTIFACT_ROLE] * len(alternative), dtype="string"
        )
        alternative["winter_pv_sensitivity_applied"] = target_mask.to_numpy(dtype=bool)
        alternative["winter_pv_sensitivity_method"] = pd.Series(
            [SENSITIVITY_METHOD] * len(alternative), dtype="string"
        )
        alternative["winter_pv_sensitivity_protocol_sha256"] = pd.Series(
            [EXPECTED_SHA256["protocol"]] * len(alternative), dtype="string"
        )

        diff_audit = build_diff_audit(canonical, alternative, target_mask)
        require(diff_audit["gate_status"].eq("PASS").all(), "Full-column diff audit failed.")
        require(
            alternative.loc[:, canonical_columns].dtypes.astype(str).equals(
                canonical.dtypes.astype(str)
            ),
            "A canonical column dtype changed in memory.",
        )
        immutable_columns = [
            column
            for column in canonical_columns
            if column != PRIMARY_COLUMN and column not in DERIVED_COLUMNS
        ]
        require(
            all(
                series_equal(canonical[column], alternative[column]).all()
                for column in immutable_columns
            ),
            "An immutable canonical column changed.",
        )
        for column in (PRIMARY_COLUMN, *DERIVED_COLUMNS):
            require(
                series_equal(
                    canonical.loc[~target_mask, column],
                    alternative.loc[~target_mask, column],
                ).all(),
                f"{column} changed outside the Winter target.",
            )

        expected_pv_kwh = alternative[PRIMARY_COLUMN]
        expected_residual = alternative["baseline_load_kw"] - alternative[PRIMARY_COLUMN]
        expected_grid = pd.Series(np.maximum(expected_residual.to_numpy(), 0.0), index=alternative.index)
        expected_surplus = pd.Series(np.maximum(-expected_residual.to_numpy(), 0.0), index=alternative.index)
        equation_checks = {
            "pv_available_kwh_equals_pv_available_kw": series_equal(
                alternative["pv_available_kwh"], expected_pv_kwh
            ).all(),
            "residual_load_kw_equation": series_equal(
                alternative["residual_load_kw"], expected_residual
            ).all(),
            "grid_demand_before_bess_kw_equation": series_equal(
                alternative["grid_demand_before_bess_kw"], expected_grid
            ).all(),
            "pv_surplus_before_bess_kw_equation": series_equal(
                alternative["pv_surplus_before_bess_kw"], expected_surplus
            ).all(),
        }
        require(all(equation_checks.values()), f"Derived planning equation gate failed: {equation_checks}")
        require(
            all(
                series_equal(
                    canonical.loc[short_gap_mask, column],
                    alternative.loc[short_gap_mask, column],
                ).all()
                for column in canonical_columns
            ),
            "A protected short-gap canonical value or null pattern changed.",
        )
        require(
            int(alternative["winter_pv_sensitivity_applied"].sum()) == EXPECTED_TARGET_COUNT
            and not alternative.loc[~target_mask, "winter_pv_sensitivity_applied"].any(),
            "Sensitivity-application provenance count/scope mismatch.",
        )
        require(
            alternative["artifact_role"].eq(ARTIFACT_ROLE).all()
            and alternative["winter_pv_sensitivity_method"].eq(SENSITIVITY_METHOD).all()
            and alternative["winter_pv_sensitivity_protocol_sha256"]
            .eq(EXPECTED_SHA256["protocol"])
            .all(),
            "Additive sensitivity provenance values are inconsistent.",
        )
        no_new_missing = {
            column: int(alternative[column].isna().sum())
            <= int(canonical[column].isna().sum())
            for column in canonical_columns
        }
        require(all(no_new_missing.values()), "A canonical column acquired new missing values.")
        require(
            all(not alternative[column].isna().any() for column in ADDITIVE_COLUMNS),
            "An additive provenance column contains missing values.",
        )

        hod5_mask = target_hod.eq(5).to_numpy()
        hod5_daylight_mask = hod5_mask & daylight_mask
        hod5_energy = float(prediction[hod5_daylight_mask].sum())
        total_energy = float(prediction.sum())
        hod5_capped_timestamps = candidate_target.loc[
            hod5_mask & np.isclose(prediction, pv_cap_kw, rtol=0.0, atol=0.0), "timestamp"
        ].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
        hod5_diagnostic = {
            "all_target_rows_at_hod_5": int(hod5_mask.sum()),
            "daylight_target_rows_at_hod_5": int(hod5_daylight_mask.sum()),
            "reconstructed_pv_energy_hod_5_daylight_kwh": hod5_energy,
            "total_reconstructed_target_pv_energy_kwh": total_energy,
            "hod_5_share_of_total_reconstructed_target_energy_percent": (
                100.0 * hod5_energy / total_energy if total_energy > 0.0 else 0.0
            ),
            "maximum_hod_5_reconstructed_kw": (
                float(prediction[hod5_mask].max()) if hod5_mask.any() else 0.0
            ),
            "hod_5_cap_hit_count": len(hod5_capped_timestamps),
            "hod_5_cap_hit_timestamps": hod5_capped_timestamps,
            "diagnostic_only_model_unchanged": True,
        }

        prediction_summary = {
            "target_rows": EXPECTED_TARGET_COUNT,
            "finite_prediction_rows": int(np.isfinite(prediction).sum()),
            "zero_prediction_rows": int((prediction == 0.0).sum()),
            "nonzero_prediction_rows": int((prediction != 0.0).sum()),
            "minimum_prediction_kw": float(prediction.min()),
            "maximum_prediction_kw": float(prediction.max()),
            "mean_prediction_kw": float(prediction.mean()),
            "median_prediction_kw": float(np.median(prediction)),
            "total_reconstructed_target_pv_energy_kwh": total_energy,
            "capped_row_count": int((prediction == pv_cap_kw).sum()),
        }

        parquet_temp = write_parquet_temp(alternative, output_parquet)
        staged_paths.append(parquet_temp)
        reloaded = pd.read_parquet(parquet_temp)
        require(len(reloaded) == 8_760, "Reloaded output does not have 8,760 rows.")
        require(reloaded.columns.tolist() == alternative.columns.tolist(), "Reloaded output columns/order changed.")
        require(
            pd.DatetimeIndex(pd.to_datetime(reloaded["timestamp"])).equals(
                pd.DatetimeIndex(canonical_timestamps)
            ),
            "Reloaded output timestamp vector differs from canonical.",
        )
        require(
            stable_frame_sha256(reloaded, ["timestamp"]) == canonical_timestamp_sha256,
            "Reloaded output timestamp SHA-256 differs from canonical.",
        )
        require(
            reloaded.loc[:, canonical_columns].dtypes.astype(str).equals(
                canonical.dtypes.astype(str)
            ),
            "Parquet serialization changed a canonical dtype.",
        )
        reloaded_diff_audit = build_diff_audit(canonical, reloaded, target_mask)
        require(
            reloaded_diff_audit["gate_status"].eq("PASS").all(),
            "Reloaded Parquet full-column diff audit failed.",
        )
        require(
            all(
                series_equal(alternative[column], reloaded[column]).all()
                for column in alternative.columns
            ),
            "Parquet round-trip changed at least one value or null pattern.",
        )

        diff_temp = write_csv_temp(reloaded_diff_audit, diff_audit_path)
        staged_paths.append(diff_temp)
        output_parquet_sha256 = sha256_file(parquet_temp)
        diff_audit_sha256 = sha256_file(diff_temp)

        canonical_sha256_after = sha256_file(paths["canonical_annual_input"])
        core_sha256_after = sha256_file(paths["annual_core"])
        protected_scripts_at_end = scripts_through_17a(root)
        source_hashes_at_end = {
            label: sha256_file(path)
            for label, path in paths.items()
            if label in EXPECTED_SHA256
        }
        source_unchanged = {
            label: source_hashes_at_start[label] == source_hashes_at_end[label]
            for label in source_hashes_at_start
        }
        require(all(source_unchanged.values()), f"A controlled source changed: {source_unchanged}")
        require(
            canonical_sha256_before == canonical_sha256_after == EXPECTED_SHA256["canonical_annual_input"],
            "Canonical annual input changed during Script 17b.",
        )
        require(
            core_sha256_before == core_sha256_after == EXPECTED_SHA256["annual_core"],
            "Annual optimization core changed during Script 17b.",
        )
        require(
            protected_scripts_at_start == protected_scripts_at_end,
            "A Script 01-through-17a source file changed during Script 17b.",
        )

        change_counts = {
            row["column"]: int(row["changed_row_count"])
            for row in reloaded_diff_audit.loc[
                reloaded_diff_audit["column"].isin([PRIMARY_COLUMN, *DERIVED_COLUMNS])
            ].to_dict("records")
        }
        gates = {
            "output_row_count_8760": True,
            "timestamp_vector_exactly_canonical": True,
            "timestamp_sha256_unchanged": True,
            "timestamps_unique": True,
            "sensitivity_application_count_1463": True,
            "all_target_predictions_finite": True,
            "no_prediction_outside_target": True,
            "target_training_intersection_zero": True,
            "predictions_within_physical_bounds": True,
            "night_guard_exact": True,
            "protected_short_gap_rows_unchanged": True,
            "canonical_observation_fields_unchanged": True,
            "canonical_load_fields_unchanged": True,
            "pv_status_and_long_unavailability_provenance_unchanged": True,
            "forbidden_canonical_column_changes_zero": True,
            "pv_available_kw_changes_target_only": True,
            "derived_fields_change_target_only_and_reconcile": True,
            "derived_equations_independently_validated": True,
            "canonical_dtypes_unchanged": True,
            "required_fields_no_new_missing_values": True,
            "all_authority_and_controlled_source_hashes_match": True,
            "canonical_input_hash_before_after_identical": True,
            "annual_core_hash_before_after_identical": True,
            "scripts_01_through_17a_unchanged": True,
            "no_optimizer_or_economic_solve_invoked": True,
            "output_namespaces_isolated": True,
            "completion_manifest_written_only_after_all_gates": True,
        }

        sensitivity_manifest_payload = {
            "role": ARTIFACT_ROLE,
            "methodology": METHODOLOGY,
            "status": "17B_BUILD_PASS",
            "script_17b": {
                "path": relative_path(script_path, root),
                "version": SCRIPT_VERSION,
                "sha256": script_sha256,
            },
            "run": {
                "run_id": run_id,
                "started_utc": utc_text(started_utc),
                "git_commit": head,
                "branch": branch,
                "origin_thesis_v7": origin_head,
                "origin_comparison_basis": "local_origin_tracking_reference",
                "dirty": bool(git_status_at_start),
                "git_status_porcelain_at_start": git_status_at_start.splitlines(),
            },
            "authority": {
                "framework_v7_2": {
                    "path": relative_path(paths["framework_v7_2"], root),
                    "sha256": source_hashes_at_start["framework_v7_2"],
                    "status": "CURRENT_METHODOLOGY_AUTHORITY_VERIFIED",
                },
                "registry_v7_2": {
                    "path": relative_path(paths["registry_v7_2"], root),
                    "sha256": source_hashes_at_start["registry_v7_2"],
                    "status": "CURRENT_CLAIM_BOUNDARY_AUTHORITY_VERIFIED",
                },
                "production_checkpoint": {
                    "path": relative_path(paths["production_checkpoint"], root),
                    "sha256": source_hashes_at_start["production_checkpoint"],
                    "status": checkpoint["status"],
                    "validator_status": validator_payload["status"],
                    "validator_artifact_hash_checks": validator_payload["artifact_hash_checks"],
                },
                "current_v7_2_pipeline_through_accepted_script_17a_used": True,
            },
            "canonical_annual_input": {
                "path": relative_path(paths["canonical_annual_input"], root),
                "sha256_before_build": canonical_sha256_before,
                "sha256_after_build": canonical_sha256_after,
                "canonical_input_unchanged": canonical_sha256_before == canonical_sha256_after,
                "row_count": int(len(canonical)),
                "timestamp_sha256": canonical_timestamp_sha256,
            },
            "protocol": {
                "path": relative_path(paths["protocol"], root),
                "sha256": source_hashes_at_start["protocol"],
                "status": "FROZEN / APPROVED FOR IMPLEMENTATION",
                "claim_boundary": (
                    "Sensitivity-only planning availability; not observed or recovered historical truth."
                ),
            },
            "accepted_script_17a": {
                "path": relative_path(paths["script_17a"], root),
                "version": EXPECTED_SCRIPT_17A_VERSION,
                "sha256": source_hashes_at_start["script_17a"],
                "formal_run_id": FORMAL_17A_RUN_ID,
                "run_manifest_path": relative_path(paths["17a_run_manifest"], root),
                "run_manifest_sha256": source_hashes_at_start["17a_run_manifest"],
                "completion_manifest_path": relative_path(paths["17a_completion_manifest"], root),
                "completion_manifest_sha256": source_hashes_at_start["17a_completion_manifest"],
                "final_decision_path": relative_path(paths["17a_final_decision"], root),
                "final_decision_sha256": source_hashes_at_start["17a_final_decision"],
                "decision": "PASS_FOR_SENSITIVITY",
                "holdout_status": {"H1": "PASS", "H2": "PASS", "H3": "PASS"},
            },
            "controlled_sources": {
                "script_04b": {
                    "path": relative_path(paths["script_04b"], root),
                    "version": EXPECTED_CWA_REFERENCE_VERSION,
                    "sha256": source_hashes_at_start["script_04b"],
                    "reused_function_identity": source_function_identity,
                    "reused_function_source_sha256": source_function_sha256,
                },
                "observed_input": {
                    "path": relative_path(paths["observed_parquet"], root),
                    "sha256": source_hashes_at_start["observed_parquet"],
                },
                "cwa_input": {
                    "path": relative_path(paths["cwa_input"], root),
                    "sha256": source_hashes_at_start["cwa_input"],
                },
            },
            "training_and_model": {
                "eligible_training_count": int(len(train)),
                "training_start": train["timestamp"].min(),
                "training_end": train["timestamp"].max(),
                "target_training_intersection_count": len(target_training_intersection),
                "training_timestamp_sha256": training_timestamp_sha256,
                "full_training_set_sha256": training_set_sha256,
                "ratio_fit_condition": "ghi_kwh_m2 > 0.05",
                "ratio_fit_count": int(len(fit)),
                "hod_counts": hod_counts,
                "hod_median_ratios": hod_medians,
                "global_median_ratio": global_ratio,
                "pv_cap_kw": pv_cap_kw,
                "daylight_threshold_kwh_m2": EXPECTED_DAYLIGHT_GHI_THRESHOLD,
                "target_features_used": ["timestamp.hour", "ghi_kwh_m2"],
                "temperature_used": False,
            },
            "target_and_prediction": {
                "target_start": TARGET_START,
                "target_end_exclusive": TARGET_END_EXCLUSIVE,
                "target_count": int(len(target)),
                "target_unique_timestamp_count": int(target["timestamp"].nunique()),
                "target_timestamp_sha256": target_timestamp_sha256,
                "target_status_breakdown": target_status_counts,
                "target_daylight_count": int(daylight_mask.sum()),
                "target_night_guarded_count": int(night_mask.sum()),
                "target_all_hour_global_fallback_count": int(fallback_mask.sum()),
                "target_daylight_global_fallback_count": int(
                    (fallback_mask.to_numpy() & daylight_mask).sum()
                ),
                **prediction_summary,
            },
            "hod_5_sparse_support_diagnostic": hod5_diagnostic,
            "mutation_audit": {
                "canonical_column_count": len(canonical_columns),
                "primary_and_derived_changed_row_counts": change_counts,
                "forbidden_mutation_count": 0,
                "outside_target_mutation_count": 0,
                "short_gap_rows_checked": int(short_gap_mask.sum()),
                "short_gap_preserved": True,
                "canonical_dtypes_preserved": True,
                "derived_equation_checks": equation_checks,
            },
            "additive_provenance": {
                "artifact_role": ARTIFACT_ROLE,
                "winter_pv_sensitivity_applied_true_count": int(target_mask.sum()),
                "winter_pv_sensitivity_applied_false_count": int((~target_mask).sum()),
                "winter_pv_sensitivity_method": SENSITIVITY_METHOD,
                "winter_pv_sensitivity_protocol_sha256": EXPECTED_SHA256["protocol"],
            },
            "outputs": {
                "parquet_path": relative_path(output_parquet, root),
                "parquet_sha256": output_parquet_sha256,
                "csv_path": None,
                "csv_sha256": None,
                "diff_audit_path": relative_path(diff_audit_path, root),
                "diff_audit_sha256": diff_audit_sha256,
                "completion_manifest_path": relative_path(completion_path, root),
            },
            "software": {
                "python": platform.python_version(),
                "python_executable": sys.executable,
                "pandas": pd.__version__,
                "numpy": np.__version__,
            },
            "controlled_source_hashes_at_start": source_hashes_at_start,
            "controlled_source_hashes_at_end": source_hashes_at_end,
            "controlled_sources_unchanged": source_unchanged,
            "scripts_01_through_17a_sha256_at_start": protected_scripts_at_start,
            "scripts_01_through_17a_sha256_at_end": protected_scripts_at_end,
            "no_solve_assertions": no_solve_assertions,
            "build_gates": gates,
            "all_build_gates_pass": all(gates.values()),
        }

        manifest_temp = temporary_path(output_manifest)
        staged_paths.append(manifest_temp)
        with manifest_temp.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(
                json_safe(sensitivity_manifest_payload),
                handle,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        sensitivity_manifest_sha256 = sha256_file(manifest_temp)

        promote_non_overwriting(parquet_temp, output_parquet)
        staged_paths.remove(parquet_temp)
        promote_non_overwriting(diff_temp, diff_audit_path)
        staged_paths.remove(diff_temp)
        promote_non_overwriting(manifest_temp, output_manifest)
        staged_paths.remove(manifest_temp)

        completion_payload = {
            "run_id": run_id,
            "status": "17B_BUILD_PASS",
            "final_verdict": "17B BUILD PASS — READY FOR INDEPENDENT PRE-17C AUDIT",
            "run_started_utc": utc_text(started_utc),
            "run_completed_utc": utc_text(utc_now()),
            "script_version": SCRIPT_VERSION,
            "script_sha256": script_sha256,
            "source_commit": head,
            "git_branch": branch,
            "all_build_gates_pass": True,
            "build_gates": gates,
            "artifacts": {
                "run_manifest": {
                    "path": relative_path(run_manifest_path, root),
                    "sha256": sha256_file(run_manifest_path),
                },
                "output_parquet": {
                    "path": relative_path(output_parquet, root),
                    "sha256": sha256_file(output_parquet),
                },
                "sensitivity_manifest": {
                    "path": relative_path(output_manifest, root),
                    "sha256": sensitivity_manifest_sha256,
                },
                "diff_audit": {
                    "path": relative_path(diff_audit_path, root),
                    "sha256": sha256_file(diff_audit_path),
                },
            },
            "canonical_annual_input_unchanged": True,
            "annual_core_unchanged": True,
            "scripts_01_through_17a_unchanged": True,
            "no_solve_assertions": no_solve_assertions,
        }
        write_json_atomic(completion_path, completion_payload)

        print(f"Run ID: {run_id}")
        print(f"Script version: {SCRIPT_VERSION}")
        print(f"Script SHA-256: {script_sha256}")
        print(f"Output Parquet: {output_parquet}")
        print(f"Output Parquet SHA-256: {sha256_file(output_parquet)}")
        print(f"Sensitivity manifest: {output_manifest}")
        print(f"Sensitivity manifest SHA-256: {sha256_file(output_manifest)}")
        print(f"Diff audit: {diff_audit_path}")
        print(f"Diff audit SHA-256: {sha256_file(diff_audit_path)}")
        print(f"Completion manifest: {completion_path}")
        print(f"Completion manifest SHA-256: {sha256_file(completion_path)}")
        print(json.dumps(json_safe(prediction_summary), indent=2, ensure_ascii=False))
        print(json.dumps(json_safe(hod5_diagnostic), indent=2, ensure_ascii=False))
        print("17B BUILD PASS — READY FOR INDEPENDENT PRE-17C AUDIT")
        return 0
    except Exception as exc:
        for temp_path in staged_paths:
            if temp_path.exists():
                temp_path.unlink()
        if run_dir.exists() and not failure_path.exists():
            write_json_atomic(
                failure_path,
                {
                    "run_id": run_id,
                    "status": "17B_BUILD_FAIL",
                    "final_verdict": "17B BUILD FAIL — DO NOT PROCEED TO 17C",
                    "failed_utc": utc_text(utc_now()),
                    "script_version": SCRIPT_VERSION,
                    "script_sha256": script_sha256,
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "completion_manifest_written": False,
                    "no_methodological_auto_fix_attempted": True,
                },
            )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
