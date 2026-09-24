#!/usr/bin/env python
"""Step 2D Candidate R3 — clean additive successor construction.

Builds V7_3_RECONSTRUCTED_PV_MAINLINE_CANDIDATE_R3 from primary repository bytes.

Numerical authority
-------------------
* historical zero-winter artifact  : data/processed/annual_input_v7_1.parquet
* corrected Sep-18 promotion source: data/processed/alternatives/
  annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet

Step 2D Candidate R1 (frozen, failed immutable provenance) and Step 2D Candidate R2
(abandoned immutable provenance, scripts/20b_...) are NEVER used as numerical authority
and are never read for construction input. They are hashed only as immutability controls.

Lifecycle
---------
This script constructs a CANDIDATE only. It never self-accepts, never routes, never
commits/pushes/tags, and performs ZERO optimization solves and ZERO model constructions.
The only authorized successor step is an independent read-only Step 2D-A audit performed
by a different agent.

"Step 2D Candidate R3" is a DATA-ARTIFACT candidate revision. It is unrelated to
Registry v7.3 R3, which remains the current evidence source of truth.
"""

from __future__ import annotations

import ast
import csv
import datetime as dt
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# --------------------------------------------------------------------------------------
# Repository geometry
# --------------------------------------------------------------------------------------

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

# --------------------------------------------------------------------------------------
# Step 2D Candidate R3 identity and EXACT authorized final paths
# --------------------------------------------------------------------------------------

CANDIDATE_IDENTITY = "V7_3_RECONSTRUCTED_PV_MAINLINE_CANDIDATE_R3"
CANDIDATE_LABEL = "Step 2D Candidate R3"
LIFECYCLE_STATUS = "CANDIDATE_PASS_PENDING_INDEPENDENT_2D_A_AUDIT"

EPISTEMIC_BOUNDARY = (
    "Reconstructed long-unavailable PV values are model-based/weather-informed "
    "planning estimates and are not observed truth, ground truth, or exact "
    "historical recovery."
)

NON_CLAIM_SENTENCE = (
    "Step 2D Candidate R3 is a candidate artifact revision only: it is not accepted, "
    "not canonical, and not production-authorized; only a later independent Step 2D-A "
    "audit performed by a different agent may externally accept these exact bytes."
)

BUILDER_REL = "scripts/20c_build_v7_3_reconstructed_pv_mainline_candidate_r3.py"
CANDIDATE_PARQUET_REL = (
    "data/processed/"
    "annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet"
)
CANDIDATE_MANIFEST_REL = (
    "data/processed/"
    "annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23_manifest.json"
)
EVIDENCE_DIR_REL = "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3"

EVID_RUN_MANIFEST = "run_manifest.json"
EVID_HIST_DIFF = "historical_canonical_to_candidate_column_diff.csv"
EVID_PROMO_DIFF = "promotion_source_to_candidate_column_diff.csv"
EVID_COMPLETION = "completion_manifest.json"
EVID_PACKAGE = "package_manifest.json"

REQUIRED_EVIDENCE_FILENAMES = (
    EVID_RUN_MANIFEST,
    EVID_HIST_DIFF,
    EVID_PROMO_DIFF,
    EVID_COMPLETION,
    EVID_PACKAGE,
)

# The three filename defects statically detected in the abandoned 20b R2 builder.
FORBIDDEN_EVIDENCE_FILENAMES = (
    "diff_vs_historical_canonical.csv",
    "diff_vs_promotion_source.csv",
    "evidence_package_manifest.json",
)

R3_FINAL_PATHS = (
    BUILDER_REL,
    CANDIDATE_PARQUET_REL,
    CANDIDATE_MANIFEST_REL,
    *(f"{EVIDENCE_DIR_REL}/{name}" for name in REQUIRED_EVIDENCE_FILENAMES),
)

# R1 / R2 final paths that must never be reused, overwritten, or written to.
R1_R2_FINAL_PATHS = (
    "scripts/20a_build_v7_3_reconstructed_pv_mainline_candidate_r1.py",
    "scripts/20b_build_v7_3_reconstructed_pv_mainline_candidate_r2.py",
    "data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.parquet",
    "data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.manifest.json",
    "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/run_manifest.json",
    "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_historical_canonical.csv",
    "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_promotion_source.csv",
    "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/completion_manifest.json",
    "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/evidence_package_manifest.json",
)

# --------------------------------------------------------------------------------------
# Numerical authority — required SHA-256 of primary sources
# --------------------------------------------------------------------------------------

HISTORICAL_CANONICAL_REL = "data/processed/annual_input_v7_1.parquet"
HISTORICAL_CANONICAL_SHA256 = (
    "9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e"
)

PROMOTION_SOURCE_REL = (
    "data/processed/alternatives/"
    "annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet"
)
PROMOTION_SOURCE_SHA256 = (
    "1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9"
)

# --------------------------------------------------------------------------------------
# Immutability set (Section 13 of the authorization)
# --------------------------------------------------------------------------------------

IMMUTABLE_TRACKED = {
    "provenance_protocol":
        "docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md",
    "framework_v7_3": "docs/research_framework_v7_3_2026-09-23.md",
    "registry_v7_3_r3": "docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md",
    "authority_freeze_v7_3": "docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md",
    "historical_canonical_parquet": HISTORICAL_CANONICAL_REL,
    "promotion_source_parquet": PROMOTION_SOURCE_REL,
    "evidence_17b_run_manifest":
        "results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/run_manifest.json",
    "evidence_17b_completion_manifest":
        "results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/completion_manifest.json",
    "evidence_17b_column_diff_audit":
        "results/data_audit/winter_pv_17b/20260918T143929009039Z_8f11437d44/"
        "annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18"
        "_column_diff_audit.csv",
    "script_06": "scripts/06_build_final_annual_input.py",
    "script_15d": "scripts/15d_run_corrected_eob_v7_2.py",
    "script_17b": "scripts/17b_build_winter_pv_sensitivity_annual_input.py",
    "script_17c": "scripts/17c_run_winter_pv_economic_sensitivity.py",
    "annual_design_core": "src/annual_design_model_v7_2.py",
}

IMMUTABLE_FROZEN_R1 = {
    "r1_builder": "scripts/20a_build_v7_3_reconstructed_pv_mainline_candidate_r1.py",
    "r1_parquet":
        "data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.parquet",
    "r1_adjacent_manifest":
        "data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.manifest.json",
    "r1_run_manifest":
        "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/run_manifest.json",
    "r1_historical_diff":
        "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_historical_canonical.csv",
    "r1_promotion_diff":
        "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_promotion_source.csv",
    "r1_completion_manifest":
        "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/completion_manifest.json",
    "r1_package_manifest":
        "results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/evidence_package_manifest.json",
}

IMMUTABLE_ABANDONED_R2 = {
    "r2_builder_abandoned":
        "scripts/20b_build_v7_3_reconstructed_pv_mainline_candidate_r2.py",
}
R2_BUILDER_EXPECTED_SHA256 = (
    "6f30660c5de9442aafccb8085fd26d994a1438b816a7ca9e4797fc23e572e3b9"
)

IMMUTABLE_PREEXISTING_UNTRACKED = {
    "untracked_meeting_transcript_docx": "0629開會逐字稿Iris.docx",
    "untracked_progress_slides_outline_md":
        "Claude outputs/0930_進度報告_投影片架構"
        "與逐頁講稿_v7.2.md",
    "untracked_literature_positioning_pptx":
        "Claude outputs/P2_Literature_Positioning_v7.2.pptx",
    "untracked_independent_audit_md":
        "Claude outputs/iris_thesis_independent_audit_2026-09-13.md",
    "untracked_repo_audit_md": "Claude outputs/iris_thesis_repo_audit_2026-09-13.md",
    "untracked_esgc_cost_pdf": "docs/ESGC Cost Performance Report 2022 PNNL-33283.pdf",
}

IMMUTABLE_SET = {
    **IMMUTABLE_TRACKED,
    **IMMUTABLE_FROZEN_R1,
    **IMMUTABLE_ABANDONED_R2,
    **IMMUTABLE_PREEXISTING_UNTRACKED,
}

# Untracked baseline expected at runtime: six unrelated originals + 20a + 20b + this
# builder (20c, the single authorized script addition).
EXPECTED_UNTRACKED_BASELINE = frozenset(
    list(IMMUTABLE_PREEXISTING_UNTRACKED.values())
    + [
        "scripts/20a_build_v7_3_reconstructed_pv_mainline_candidate_r1.py",
        "scripts/20b_build_v7_3_reconstructed_pv_mainline_candidate_r2.py",
        BUILDER_REL,
    ]
)

# --------------------------------------------------------------------------------------
# Scientific transformation constants (Framework v7.3 CLOSED decision — unchanged here)
# --------------------------------------------------------------------------------------

TARGET_PV_STATUS = ("pre_system", "missing_winter")
TARGET_RANGE_START = pd.Timestamp("2024-11-01 00:00:00")
TARGET_RANGE_END_EXCLUSIVE = pd.Timestamp("2024-12-31 23:00:00")

EXPECTED_TARGET_ROWS = 1_463
EXPECTED_TARGET_STATUS_COUNTS = {"pre_system": 600, "missing_winter": 863}
EXPECTED_POSITIVE_HOURS = 619
EXPECTED_ZERO_NIGHT_HOURS = 844
EXPECTED_RECONSTRUCTED_ENERGY_KWH = 39484.422494085295
EXPECTED_MAX_KW = 234.10402721999108
EXPECTED_TARGET_TIMESTAMP_SHA256 = (
    "98d635c9578b9118d066dce2e0bf718c70ed5517005439cd7ee473aba14db2ad"
)

EXPECTED_ROWS = 8_760
EXPECTED_CANDIDATE_COLUMNS = 51

ARTIFACT_ROLE_VALUE = "reconstructed_pv_mainline"
TARGET_PV_RECONSTRUCTION_METHOD = "cwa_hourly_ghi_ratio_median_all_eligible_v7_2"
TARGET_PV_CWA_MODEL = "hourly_ghi_ratio_median"

AUTHORIZED_NUMERICAL_CHANGES = {
    "pv_available_kwh": (619, +39484.422494085295),
    "pv_available_kw": (619, +39484.422494085295),
    "residual_load_kw": (619, -39484.422494085295),
    "grid_demand_before_bess_kw": (619, -39484.422494085295),
    "pv_surplus_before_bess_kw": (0, 0.0),
}

PRESERVED_PROVENANCE_COLUMNS = ("pv_status", "data_status", "pv_long_unavailable_flag")

REMOVED_COLUMNS = (
    "winter_pv_sensitivity_applied",
    "winter_pv_sensitivity_method",
    "winter_pv_sensitivity_protocol_sha256",
)

SHORT_GAP_METHOD = "cwa_hourly_ghi_ratio_median_leave_target_day_out"
EXPECTED_SHORT_GAP_ROWS = 10

# --------------------------------------------------------------------------------------
# Zero-solve boundary
# --------------------------------------------------------------------------------------

FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "gurobipy",
        "gurobi",
        "gurobipy_pandas",
        "annual_design_model_v7_2",
        "src.annual_design_model_v7_2",
        "pyomo",
        "pulp",
        "cvxpy",
        "mip",
        "highspy",
    }
)
FORBIDDEN_CALL_NAMES = frozenset(
    {
        "optimize",
        "optimizeAsync",
        "optimizeBatch",
        "setParam",
        "addVar",
        "addVars",
        "addConstr",
        "addConstrs",
        "addGenConstrIndicator",
        "tune",
        "build_annual_model",
        "solve_annual_model",
        "run_eob",
        "run_layer_a",
        "run_layer_b",
        "run_final_81",
    }
)

# --------------------------------------------------------------------------------------
# Self-classification wording gate
# --------------------------------------------------------------------------------------

SELF_CLASSIFICATION_PATTERN = re.compile(
    r"\b(accepted|canonical|production[-_ ]authorized)\b", re.IGNORECASE
)
# Token-bearing strings that are structurally required and carry no self-classification
# claim: the mandated diff filename family (which names the upstream historical source),
# and the explicit negative lifecycle statement.
ALLOWED_TOKEN_EXACT = frozenset({NON_CLAIM_SENTENCE})
ALLOWED_TOKEN_PREFIX = "historical_canonical"
# The immutability-hash subtrees are pure path/digest records of upstream authorities and
# of frozen R1/R2 provenance. Those foreign paths legitimately carry the tokens and make
# no claim about this candidate, so they are recorded verbatim and excluded from the
# self-classification wording scan (their exact bytes are gated separately).
WORDING_SCAN_EXCLUDED_KEYS = frozenset(
    {
        "immutable_hashes_before",
        "immutable_hashes_after",
        "immutable_hashes_after_publication",
    }
)


# --------------------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------------------


class BuildStop(RuntimeError):
    """Raised on any construction-gate failure. Halts before final publication."""


GATES: dict[str, bool] = {}


def gate(name: str, condition: bool, message: str) -> None:
    """Record a named build gate and halt on failure."""
    ok = bool(condition)
    GATES[name] = ok
    if not ok:
        raise BuildStop(f"{name}: {message}")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_set(mapping: dict[str, str], measurement_point: str) -> dict[str, Any]:
    entries: dict[str, Any] = {}
    for label, rel in sorted(mapping.items()):
        path = REPO_ROOT / rel
        if not path.is_file():
            raise BuildStop(f"Immutability-set member missing: {rel}")
        entries[label] = {
            "path": rel,
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
    return {"measurement_point": measurement_point, "members": entries}


def stable_frame_sha256(frame: pd.DataFrame, columns: list[str]) -> str:
    """Byte-stable frame digest, identical in definition to script 17b."""
    work = frame.loc[:, columns].copy()
    for column in work.columns:
        if pd.api.types.is_datetime64_any_dtype(work[column]):
            work[column] = work[column].dt.strftime("%Y-%m-%d %H:%M:%S")
    text = work.to_csv(index=False, lineterminator="\n", float_format="%.17g")
    return sha256_bytes(text.encode("utf-8"))


def json_bytes(payload: Any) -> bytes:
    # allow_nan=False makes any non-finite float a hard build failure rather than
    # emitting non-standard JSON into a provenance artifact.
    return (
        json.dumps(
            payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if value is pd.NA:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if pd.isna(value) else float(value)
    return value


def git_raw(*args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise BuildStop(
            f"git {' '.join(args)} failed ({result.returncode}): "
            f"{result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout.decode("utf-8")


def git(*args: str) -> str:
    return git_raw(*args).strip()


def git_status_entries() -> list[tuple[str, str]]:
    """(status_code, path) pairs from NUL-separated porcelain output.

    -z is required: the default porcelain format wraps any path containing a space
    (or non-ASCII byte) in quotes, which would corrupt path identity comparisons.
    """
    raw = git_raw("status", "--porcelain=v1", "-uall", "-z")
    entries: list[tuple[str, str]] = []
    fields = [field for field in raw.split("\0") if field]
    index = 0
    while index < len(fields):
        field = fields[index]
        code, path = field[:2], field[3:]
        # Renames/copies emit the origin path as a separate following field.
        if code[0] in {"R", "C"} or code[1] in {"R", "C"}:
            index += 1
        entries.append((code, path))
        index += 1
    return entries


def collect_strings(node: Any, out: list[str], exclude_keys: frozenset[str] = frozenset()) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in exclude_keys:
                continue
            out.append(str(key))
            collect_strings(value, out, exclude_keys)
    elif isinstance(node, list):
        for value in node:
            collect_strings(value, out, exclude_keys)
    elif isinstance(node, str):
        out.append(node)


def token_violations(strings: list[str]) -> list[str]:
    bad: list[str] = []
    for text in strings:
        if not SELF_CLASSIFICATION_PATTERN.search(text):
            continue
        if text in ALLOWED_TOKEN_EXACT:
            continue
        # Bare label/key form, e.g. "historical_canonical_to_candidate".
        if text.startswith(ALLOWED_TOKEN_PREFIX):
            continue
        # Repository-relative path whose basename is the mandated diff filename,
        # e.g. ".../historical_canonical_to_candidate_column_diff.csv".
        if text.rsplit("/", 1)[-1].startswith(ALLOWED_TOKEN_PREFIX):
            continue
        bad.append(text)
    return bad


# --------------------------------------------------------------------------------------
# Phase A — pre-construction gates
# --------------------------------------------------------------------------------------


def gate_r3_path_absence() -> None:
    present = [
        rel
        for rel in R3_FINAL_PATHS
        if rel != BUILDER_REL and (REPO_ROOT / rel).exists()
    ]
    evidence_dir = REPO_ROOT / EVIDENCE_DIR_REL
    if evidence_dir.exists():
        present.append(EVIDENCE_DIR_REL)
    gate(
        "gate_01_r3_final_path_absence",
        not present,
        "Step 2D Candidate R3 final path(s) already exist; refusing to overwrite and "
        f"refusing to auto-create R4: {present}",
    )
    gate(
        "gate_02_builder_is_authorized_r3_path",
        SCRIPT_PATH == (REPO_ROOT / BUILDER_REL).resolve(),
        f"Builder must run from {BUILDER_REL}.",
    )


def gate_repository_state() -> dict[str, Any]:
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    origin_head = git("rev-parse", "origin/thesis-v7")
    entries = git_status_entries()
    untracked = {path for code, path in entries if code == "??"}
    non_untracked = [f"{code} {path}" for code, path in entries if code != "??"]

    gate("gate_03_branch_identity", branch == "thesis-v7", f"branch={branch!r}")
    gate(
        "gate_04_head_matches_origin",
        head == origin_head,
        f"HEAD={head} origin/thesis-v7={origin_head}",
    )
    gate(
        "gate_05_tracked_worktree_and_index_clean",
        not non_untracked,
        f"tracked modifications/staged entries present: {non_untracked}",
    )
    gate(
        "gate_06_untracked_baseline_exact",
        untracked == set(EXPECTED_UNTRACKED_BASELINE),
        "untracked baseline drift: "
        f"unexpected={sorted(untracked - set(EXPECTED_UNTRACKED_BASELINE))} "
        f"missing={sorted(set(EXPECTED_UNTRACKED_BASELINE) - untracked)}",
    )
    return {
        "branch": branch,
        "head": head,
        "origin_ref": "origin/thesis-v7",
        "origin_head": origin_head,
        "head_equals_origin": head == origin_head,
        "tracked_worktree_clean": not non_untracked,
        "index_clean": not non_untracked,
        "untracked_baseline": sorted(untracked),
        "untracked_classification": {
            "preexisting_original_artifacts": sorted(
                IMMUTABLE_PREEXISTING_UNTRACKED.values()
            ),
            "frozen_step_2d_candidate_r1_failed_provenance": [
                "scripts/20a_build_v7_3_reconstructed_pv_mainline_candidate_r1.py"
            ],
            "frozen_step_2d_candidate_r2_abandoned_provenance": [
                "scripts/20b_build_v7_3_reconstructed_pv_mainline_candidate_r2.py"
            ],
            "authorized_step_2d_candidate_r3_additions": [BUILDER_REL],
            "unexpected_drift": [],
        },
        "note": (
            "Frozen Step 2D Candidate R1 data/evidence artifacts and the candidate R3 "
            "data/evidence artifacts live under gitignored data/ and results/ trees and "
            "therefore do not appear in git status; they are tracked here by explicit "
            "path hashing instead."
        ),
    }


def gate_zero_solve_static() -> dict[str, Any]:
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    forbidden_imports = sorted(
        name
        for name in imports
        if name in FORBIDDEN_IMPORT_ROOTS
        or name.split(".")[0] in FORBIDDEN_IMPORT_ROOTS
    )

    forbidden_calls: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name in FORBIDDEN_CALL_NAMES:
            forbidden_calls.append(f"{name}@line{node.lineno}")

    loaded_forbidden = sorted(
        mod
        for mod in sys.modules
        if mod in FORBIDDEN_IMPORT_ROOTS or mod.split(".")[0] in FORBIDDEN_IMPORT_ROOTS
    )

    gate(
        "gate_07_zero_solve_static_guard",
        not forbidden_imports and not forbidden_calls and not loaded_forbidden,
        f"imports={forbidden_imports} calls={forbidden_calls} loaded={loaded_forbidden}",
    )

    return {
        "ast_parsed": True,
        "builder_import_names": sorted(imports),
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
        "forbidden_modules_loaded_at_runtime": loaded_forbidden,
        "gurobi_imported": False,
        "annual_optimization_core_imported": False,
        "model_constructions": 0,
        "optimization_calls": 0,
        "economic_evaluations": 0,
        "eob_runs": 0,
        "representative_case_runs": 0,
        "layer_a_runs": 0,
        "layer_b_runs": 0,
        "final81_runs": 0,
        "production_routing_actions": 0,
        "candidate_csv_written": False,
        "commits": 0,
        "pushes": 0,
        "tags": 0,
    }


def gate_no_r1_r2_reuse() -> None:
    overlap = sorted(set(R3_FINAL_PATHS) & set(R1_R2_FINAL_PATHS))
    gate("gate_08_no_r1_r2_final_path_reuse", not overlap, f"overlap={overlap}")
    gate(
        "gate_09_r2_builder_expected_identity",
        sha256_file(REPO_ROOT / IMMUTABLE_ABANDONED_R2["r2_builder_abandoned"])
        == R2_BUILDER_EXPECTED_SHA256,
        "Abandoned 20b R2 builder does not match its expected frozen SHA-256.",
    )


# --------------------------------------------------------------------------------------
# Phase A2 — source loading and verification
# --------------------------------------------------------------------------------------


def parquet_physical(path: Path) -> dict[str, Any]:
    handle = pq.ParquetFile(path)
    meta = handle.metadata
    schema = handle.schema_arrow
    extra_keys = sorted(
        key.decode("utf-8") for key in (schema.metadata or {}).keys()
    )
    pandas_meta = json.loads((schema.metadata or {})[b"pandas"].decode("utf-8"))
    compressions = sorted(
        {
            meta.row_group(rg).column(col).compression
            for rg in range(meta.num_row_groups)
            for col in range(meta.num_columns)
        }
    )
    return {
        "num_rows": meta.num_rows,
        "num_columns": meta.num_columns,
        "num_row_groups": meta.num_row_groups,
        "created_by": meta.created_by,
        "compression": compressions,
        "schema_metadata_keys": extra_keys,
        "custom_key_value_metadata_present": [
            key for key in extra_keys if key != "pandas"
        ] != [],
        "pandas_index_columns": pandas_meta.get("index_columns", []),
        "serialized_index_present": bool(pandas_meta.get("index_columns")),
        "arrow_types": {field.name: str(field.type) for field in schema},
    }


def load_sources() -> dict[str, Any]:
    hist_path = REPO_ROOT / HISTORICAL_CANONICAL_REL
    promo_path = REPO_ROOT / PROMOTION_SOURCE_REL

    hist_sha = sha256_file(hist_path)
    promo_sha = sha256_file(promo_path)
    gate(
        "gate_10_historical_source_sha256",
        hist_sha == HISTORICAL_CANONICAL_SHA256,
        f"historical zero-winter source SHA mismatch: {hist_sha}",
    )
    gate(
        "gate_11_promotion_source_sha256",
        promo_sha == PROMOTION_SOURCE_SHA256,
        f"Sep-18 promotion source SHA mismatch: {promo_sha}",
    )

    hist = pd.read_parquet(hist_path)
    promo = pd.read_parquet(promo_path)

    hist_phys = parquet_physical(hist_path)
    promo_phys = parquet_physical(promo_path)

    gate(
        "gate_12_source_row_counts",
        len(hist) == EXPECTED_ROWS and len(promo) == EXPECTED_ROWS,
        f"rows hist={len(hist)} promo={len(promo)}",
    )
    gate(
        "gate_13_source_column_counts",
        hist.shape[1] == 50 and promo.shape[1] == 54,
        f"columns hist={hist.shape[1]} promo={promo.shape[1]}",
    )
    gate(
        "gate_14_promotion_prefix_is_historical_order",
        list(promo.columns[:50]) == list(hist.columns),
        "Promotion source does not carry the historical 50-column ordered prefix.",
    )
    gate(
        "gate_15_promotion_extra_columns_exact",
        list(promo.columns[50:]) == ["artifact_role", *REMOVED_COLUMNS],
        f"Unexpected promotion-only columns: {list(promo.columns[50:])}",
    )
    gate(
        "gate_16_source_dtype_identity",
        all(str(hist[c].dtype) == str(promo[c].dtype) for c in hist.columns),
        "Historical/promotion dtype divergence on the shared 50 columns.",
    )
    gate(
        "gate_17_source_time_axis_exact",
        hist["timestamp"].equals(promo["timestamp"])
        and pd.to_datetime(hist["timestamp"]).is_unique
        and pd.to_datetime(hist["timestamp"]).is_monotonic_increasing,
        "Source time axes are not identical, unique and monotonic.",
    )
    gate(
        "gate_18_source_no_serialized_index",
        not hist_phys["serialized_index_present"]
        and not promo_phys["serialized_index_present"],
        "A source parquet carries a serialized index.",
    )
    gate(
        "gate_19_source_no_custom_metadata",
        not hist_phys["custom_key_value_metadata_present"]
        and not promo_phys["custom_key_value_metadata_present"],
        "A source parquet carries custom key/value metadata.",
    )

    return {
        "historical_canonical": {
            "path": HISTORICAL_CANONICAL_REL,
            "sha256": hist_sha,
            "size_bytes": hist_path.stat().st_size,
            "role": (
                "historical zero-winter artifact; conservative stress/sensitivity "
                "treatment; retained-value and diff baseline"
            ),
            "physical": hist_phys,
        },
        "promotion_source": {
            "path": PROMOTION_SOURCE_REL,
            "sha256": promo_sha,
            "size_bytes": promo_path.stat().st_size,
            "role": (
                "corrected Sep-18 promotion source; sole numerical source for every "
                "retained value in Step 2D Candidate R3"
            ),
            "physical": promo_phys,
        },
        "evidence_17b": {
            label: {
                "path": rel,
                "sha256": sha256_file(REPO_ROOT / rel),
                "size_bytes": (REPO_ROOT / rel).stat().st_size,
            }
            for label, rel in IMMUTABLE_TRACKED.items()
            if label.startswith("evidence_17b")
        },
        "excluded_from_numerical_authority": {
            "step_2d_candidate_r1": (
                "frozen failed immutable provenance; hashed as an immutability control "
                "only; never read as construction input"
            ),
            "step_2d_candidate_r2_builder": (
                "abandoned immutable provenance; hashed as an immutability control only; "
                "never edited, renamed, deleted, overwritten or executed"
            ),
        },
        "_frames": (hist, promo),
    }


# --------------------------------------------------------------------------------------
# Phase A3 — target mask
# --------------------------------------------------------------------------------------


def derive_target(promo: pd.DataFrame, hist: pd.DataFrame) -> dict[str, Any]:
    status = promo["pv_status"].astype("string")
    primary_mask = status.isin(list(TARGET_PV_STATUS)) & (
        promo["pv_long_unavailable_flag"] == True  # noqa: E712 - explicit flag equality
    )
    timestamps = pd.to_datetime(promo["timestamp"])
    range_mask = timestamps.ge(TARGET_RANGE_START) & timestamps.lt(
        TARGET_RANGE_END_EXCLUSIVE
    )

    gate(
        "gate_20_target_row_count",
        int(primary_mask.sum()) == EXPECTED_TARGET_ROWS,
        f"target rows={int(primary_mask.sum())}",
    )
    status_counts = {
        str(k): int(v) for k, v in status[primary_mask].value_counts().items()
    }
    gate(
        "gate_21_target_status_counts",
        status_counts == EXPECTED_TARGET_STATUS_COUNTS,
        f"status counts={status_counts}",
    )
    gate(
        "gate_22_target_mask_redundant_range_consistency",
        bool((primary_mask.values == range_mask.values).all()),
        "Primary pv_status/flag mask and the redundant date-range assertion disagree.",
    )
    gate(
        "gate_23_target_mask_identical_on_historical_source",
        bool(
            (
                (
                    hist["pv_status"].astype("string").isin(list(TARGET_PV_STATUS))
                    & (hist["pv_long_unavailable_flag"] == True)  # noqa: E712
                ).values
                == primary_mask.values
            ).all()
        ),
        "Target mask differs between the historical source and the promotion source.",
    )

    target = (
        promo.loc[primary_mask].copy().sort_values("timestamp").reset_index(drop=True)
    )
    ts_sha = stable_frame_sha256(target, ["timestamp"])
    gate(
        "gate_24_target_timestamp_sha256",
        ts_sha == EXPECTED_TARGET_TIMESTAMP_SHA256,
        f"ordered target timestamp SHA-256={ts_sha}",
    )

    expected_index = pd.date_range(
        TARGET_RANGE_START, TARGET_RANGE_END_EXCLUSIVE, freq="h", inclusive="left"
    )
    gate(
        "gate_25_target_timeline_contiguous_hourly",
        pd.DatetimeIndex(target["timestamp"]).equals(expected_index),
        "Target timeline is not an exact contiguous hourly range.",
    )

    pv = target["pv_available_kwh"].astype(float)
    positive = int((pv > 0).sum())
    zero_night = int((pv == 0).sum())
    energy = float(pv.sum())
    maximum = float(target["pv_available_kw"].astype(float).max())

    gate(
        "gate_26_target_positive_hours",
        positive == EXPECTED_POSITIVE_HOURS,
        f"positive hours={positive}",
    )
    gate(
        "gate_27_target_zero_night_hours",
        zero_night == EXPECTED_ZERO_NIGHT_HOURS,
        f"zero/night hours={zero_night}",
    )
    gate(
        "gate_28_target_no_negative_reconstruction",
        int((pv < 0).sum()) == 0,
        "Negative reconstructed PV present in the target block.",
    )
    gate(
        "gate_29_target_reconstructed_energy",
        energy == EXPECTED_RECONSTRUCTED_ENERGY_KWH,
        f"reconstructed energy={energy!r}",
    )
    gate("gate_30_target_max_kw", maximum == EXPECTED_MAX_KW, f"max={maximum!r}")
    gate(
        "gate_31_historical_target_block_is_zero",
        float(hist.loc[primary_mask.values, "pv_available_kwh"].abs().max()) == 0.0,
        "Historical target block is not zero-winter.",
    )

    return {
        "mask": primary_mask,
        "record": {
            "primary_predicate": (
                'pv_status in {"pre_system", "missing_winter"} '
                "AND pv_long_unavailable_flag == True"
            ),
            "redundant_range_assertion": {
                "role": "redundant consistency assertion only, not the selector",
                "start": TARGET_RANGE_START.strftime("%Y-%m-%d %H:%M:%S"),
                "end_exclusive": TARGET_RANGE_END_EXCLUSIVE.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "agrees_with_primary_predicate": True,
                "contiguous_hourly_timeline": True,
            },
            "row_count": EXPECTED_TARGET_ROWS,
            "status_counts": status_counts,
            "positive_reconstructed_hours": positive,
            "zero_night_hours": zero_night,
            "negative_hours": 0,
            "reconstructed_energy_kwh": energy,
            "max_kw": maximum,
            "ordered_timestamp_sha256": ts_sha,
            "ordered_timestamp_sha256_method": (
                "sha256 of the ordered single-column timestamp CSV rendered with "
                'strftime "%Y-%m-%d %H:%M:%S", lineterminator "\\n", float_format '
                '"%.17g", no index'
            ),
            "mask_identical_on_both_sources": True,
        },
    }


# --------------------------------------------------------------------------------------
# Phase B — candidate construction
# --------------------------------------------------------------------------------------


def changed_mask(left: pd.Series, right: pd.Series) -> pd.Series:
    """Row-wise inequality with NA-aware semantics (NA vs NA counts as unchanged)."""
    both_na = left.isna().to_numpy(dtype=bool)
    equal = left.eq(right).fillna(False).to_numpy(dtype=bool) & ~(
        left.isna().to_numpy(dtype=bool) ^ right.isna().to_numpy(dtype=bool)
    )
    both_na = both_na & right.isna().to_numpy(dtype=bool)
    return pd.Series(~(both_na | equal), index=left.index, dtype=bool)


def numeric_delta(left: pd.Series, right: pd.Series) -> tuple[int, float, float]:
    """Changed-row count plus, for numeric non-boolean columns, the signed delta."""
    changed = changed_mask(left, right)
    n = int(changed.sum())
    numeric = (
        pd.api.types.is_numeric_dtype(left)
        and pd.api.types.is_numeric_dtype(right)
        and not pd.api.types.is_bool_dtype(left)
        and not pd.api.types.is_bool_dtype(right)
    )
    if not numeric or n == 0:
        return n, 0.0, 0.0
    delta = right.astype("float64") - left.astype("float64")
    selected = delta[changed.to_numpy()]
    return n, float(selected.sum()), float(selected.abs().max())


def build_candidate(
    hist: pd.DataFrame, promo: pd.DataFrame, target_mask: pd.Series
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    # 1. Numerical inheritance is established by construction: the candidate starts as an
    #    exact copy of the corrected Sep-18 promotion source.
    candidate = promo.copy(deep=True)

    # 2. Drop the three sensitivity-only provenance columns from the successor schema.
    candidate = candidate.drop(columns=list(REMOVED_COLUMNS))

    # 3. Row-level provenance transformation (no numerical field is touched).
    candidate.loc[:, "artifact_role"] = ARTIFACT_ROLE_VALUE
    candidate.loc[target_mask, "pv_reconstructed"] = True
    candidate.loc[target_mask, "pv_reconstruction_method"] = (
        TARGET_PV_RECONSTRUCTION_METHOD
    )
    candidate.loc[target_mask, "pv_long_unavailable_assumption"] = False
    candidate.loc[target_mask, "pv_cwa_model"] = TARGET_PV_CWA_MODEL

    expected_order = list(hist.columns) + ["artifact_role"]
    candidate = candidate.loc[:, expected_order]

    # ---- schema gates -----------------------------------------------------------------
    gate(
        "gate_32_candidate_row_count",
        len(candidate) == EXPECTED_ROWS,
        f"rows={len(candidate)}",
    )
    gate(
        "gate_33_candidate_column_count",
        candidate.shape[1] == EXPECTED_CANDIDATE_COLUMNS,
        f"columns={candidate.shape[1]}",
    )
    gate(
        "gate_34_candidate_historical_prefix_exact",
        list(candidate.columns[:50]) == list(hist.columns)
        and list(candidate.columns[50:]) == ["artifact_role"],
        "Candidate column order is not the historical 50-column prefix + artifact_role.",
    )
    gate(
        "gate_35_removed_columns_absent",
        not set(REMOVED_COLUMNS) & set(candidate.columns),
        "A sensitivity-only column survived into the successor schema.",
    )
    gate(
        "gate_36_candidate_dtype_preservation",
        all(
            str(candidate[c].dtype) == str(promo[c].dtype) for c in candidate.columns
        ),
        "Candidate dtypes diverge from the promotion source.",
    )

    # ---- numerical gates --------------------------------------------------------------
    numeric_columns = [
        c
        for c in hist.columns
        if pd.api.types.is_numeric_dtype(hist[c]) and not pd.api.types.is_bool_dtype(hist[c])
    ]
    promo_identity = {
        c: bool(candidate[c].equals(promo[c])) for c in candidate.columns[:50]
    }
    gate(
        "gate_37_numerical_identity_to_promotion_source",
        all(promo_identity[c] for c in numeric_columns),
        "A retained numeric field differs from the corrected Sep-18 promotion source: "
        f"{[c for c in numeric_columns if not promo_identity[c]]}",
    )

    # Numerical change set (numeric, non-boolean fields only). Boolean and string
    # provenance fields are governed by the separate provenance gates below.
    hist_changes: dict[str, Any] = {}
    for column in numeric_columns:
        n, total, max_abs = numeric_delta(hist[column], candidate[column])
        if n:
            hist_changes[column] = {
                "changed_rows": n,
                "sum_delta": total,
                "max_absolute_delta": max_abs,
            }

    authorized = {k: v[0] for k, v in AUTHORIZED_NUMERICAL_CHANGES.items() if v[0]}
    gate(
        "gate_38_authorized_change_set_exact",
        set(hist_changes) == set(authorized),
        f"numerically changed columns vs historical source = {sorted(hist_changes)}; "
        f"authorized = {sorted(authorized)}",
    )
    non_numeric_changed = {
        column
        for column in hist.columns
        if column not in numeric_columns
        and int(changed_mask(hist[column], candidate[column]).sum())
    }
    gate(
        "gate_38b_non_numerical_change_set_is_authorized_provenance",
        non_numeric_changed
        == {
            "pv_reconstructed",
            "pv_reconstruction_method",
            "pv_long_unavailable_assumption",
            "pv_cwa_model",
        },
        "Non-numerical change set vs the historical source is not exactly the "
        f"authorized provenance relabel: {sorted(non_numeric_changed)}",
    )
    for column, (rows, delta) in AUTHORIZED_NUMERICAL_CHANGES.items():
        if rows == 0:
            gate(
                f"gate_39_{column}_unchanged",
                column not in hist_changes,
                f"{column} must have 0 changed rows.",
            )
            continue
        observed = hist_changes[column]
        gate(
            f"gate_40_{column}_row_count",
            observed["changed_rows"] == rows,
            f"{column} changed rows={observed['changed_rows']}",
        )
        gate(
            f"gate_41_{column}_delta",
            observed["sum_delta"] == delta,
            f"{column} sum delta={observed['sum_delta']!r}",
        )

    outside = candidate.loc[~target_mask.values, numeric_columns]
    gate(
        "gate_42_no_numerical_change_outside_target",
        outside.equals(hist.loc[~target_mask.values, numeric_columns]),
        "Numerical change detected outside the authorized target block.",
    )
    gate(
        "gate_43_observed_columns_exact",
        all(
            candidate[c].equals(hist[c])
            for c in ("observed_load_kwh", "observed_load_kw", "observed_pv_kwh",
                      "observed_pv_kw", "observed_net_load_kw", "ghi_kwh_m2",
                      "air_temperature_c")
        ),
        "An observed column was mutated.",
    )

    # ---- provenance gates -------------------------------------------------------------
    gate(
        "gate_44_artifact_role_complete",
        bool((candidate["artifact_role"] == ARTIFACT_ROLE_VALUE).all())
        and int(candidate["artifact_role"].isna().sum()) == 0,
        "artifact_role is not uniformly set for all 8,760 rows.",
    )
    tgt = candidate.loc[target_mask]
    gate(
        "gate_45_target_pv_reconstructed_true",
        bool((tgt["pv_reconstructed"] == True).all()),  # noqa: E712
        "pv_reconstructed is not True on every target row.",
    )
    gate(
        "gate_46_target_reconstruction_method",
        bool((tgt["pv_reconstruction_method"] == TARGET_PV_RECONSTRUCTION_METHOD).all()),
        "pv_reconstruction_method relabel incomplete on the target block.",
    )
    gate(
        "gate_47_target_long_unavailable_assumption_false",
        bool((tgt["pv_long_unavailable_assumption"] == False).all()),  # noqa: E712
        "pv_long_unavailable_assumption is not False on every target row.",
    )
    gate(
        "gate_48_target_cwa_model",
        bool((tgt["pv_cwa_model"] == TARGET_PV_CWA_MODEL).all()),
        "pv_cwa_model relabel incomplete on the target block.",
    )
    gate(
        "gate_49_preserved_provenance_fields",
        all(candidate[c].equals(promo[c]) for c in PRESERVED_PROVENANCE_COLUMNS)
        and all(candidate[c].equals(hist[c]) for c in PRESERVED_PROVENANCE_COLUMNS),
        f"A preserved field changed: {PRESERVED_PROVENANCE_COLUMNS}",
    )

    short_gap = promo["pv_reconstruction_method"].eq(SHORT_GAP_METHOD)
    gate(
        "gate_50_short_gap_row_count",
        int(short_gap.sum()) == EXPECTED_SHORT_GAP_ROWS,
        f"short-gap rows={int(short_gap.sum())}",
    )
    gate(
        "gate_51_short_gap_disjoint_from_target",
        int((short_gap & target_mask).sum()) == 0,
        "Short-gap rows intersect the long-unavailable target block.",
    )
    gate(
        "gate_52_short_gap_provenance_protected",
        candidate.loc[short_gap, list(hist.columns)].equals(
            promo.loc[short_gap, list(hist.columns)]
        ),
        "Accepted short-gap provenance was mutated.",
    )

    non_target_non_relabelled = ~target_mask.values
    prov_cols = [
        "pv_reconstructed",
        "pv_reconstruction_method",
        "pv_long_unavailable_assumption",
        "pv_cwa_model",
    ]
    gate(
        "gate_53_no_provenance_change_outside_target",
        candidate.loc[non_target_non_relabelled, prov_cols].equals(
            promo.loc[non_target_non_relabelled, prov_cols]
        ),
        "Provenance relabelling leaked outside the target block.",
    )

    numerical_inheritance = {
        "numerical_source": PROMOTION_SOURCE_REL,
        "retained_value_identity_to_promotion_source": promo_identity,
        "all_retained_numeric_fields_identical": True,
        "refit_performed": False,
        "recomputation_performed": False,
        "historical_canonical_to_candidate_authorized_changes": {
            column: {
                "changed_rows": rows,
                "sum_delta": delta,
                "observed_changed_rows": hist_changes.get(column, {}).get(
                    "changed_rows", 0
                ),
                "observed_sum_delta": hist_changes.get(column, {}).get("sum_delta", 0.0),
            }
            for column, (rows, delta) in AUTHORIZED_NUMERICAL_CHANGES.items()
        },
        "other_numerical_fields_changed": [],
        "numerical_change_confined_to_target_block": True,
    }

    provenance_transformation = {
        "all_rows": {"artifact_role": ARTIFACT_ROLE_VALUE, "row_count": EXPECTED_ROWS},
        "target_rows": {
            "row_count": EXPECTED_TARGET_ROWS,
            "pv_reconstructed": True,
            "pv_reconstruction_method": TARGET_PV_RECONSTRUCTION_METHOD,
            "pv_long_unavailable_assumption": False,
            "pv_cwa_model": TARGET_PV_CWA_MODEL,
        },
        "preserved_unchanged": list(PRESERVED_PROVENANCE_COLUMNS),
        "short_gap_protection": {
            "method": SHORT_GAP_METHOD,
            "row_count": EXPECTED_SHORT_GAP_ROWS,
            "disjoint_from_target_block": True,
            "bytes_preserved": True,
        },
        "removed_from_successor_schema": list(REMOVED_COLUMNS),
        "provenance_change_confined_to_target_block": True,
        "methodology_changed": False,
        "closed_decision_reopened": False,
    }

    return candidate, numerical_inheritance, provenance_transformation


# --------------------------------------------------------------------------------------
# Phase C — diffs
# --------------------------------------------------------------------------------------

DIFF_HEADER = [
    "comparison",
    "column",
    "source_artifact",
    "candidate_artifact",
    "source_present",
    "candidate_present",
    "classification",
    "source_dtype",
    "candidate_dtype",
    "changed_row_count",
    "unchanged_row_count",
    "source_missing_count",
    "candidate_missing_count",
    "max_absolute_numeric_difference",
    "sum_numeric_delta",
    "first_changed_timestamp",
    "last_changed_timestamp",
]


def build_column_diff(
    comparison: str,
    source: pd.DataFrame,
    source_rel: str,
    candidate: pd.DataFrame,
    timestamps: pd.Series,
) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(DIFF_HEADER)

    columns: list[str] = list(source.columns)
    for column in candidate.columns:
        if column not in columns:
            columns.append(column)

    for column in columns:
        in_source = column in source.columns
        in_candidate = column in candidate.columns
        row: dict[str, Any] = {
            "comparison": comparison,
            "column": column,
            "source_artifact": source_rel,
            "candidate_artifact": CANDIDATE_PARQUET_REL,
            "source_present": in_source,
            "candidate_present": in_candidate,
            "source_dtype": str(source[column].dtype) if in_source else "",
            "candidate_dtype": str(candidate[column].dtype) if in_candidate else "",
            "changed_row_count": "",
            "unchanged_row_count": "",
            "source_missing_count": int(source[column].isna().sum()) if in_source else "",
            "candidate_missing_count": (
                int(candidate[column].isna().sum()) if in_candidate else ""
            ),
            "max_absolute_numeric_difference": "",
            "sum_numeric_delta": "",
            "first_changed_timestamp": "",
            "last_changed_timestamp": "",
        }

        if in_source and not in_candidate:
            row["classification"] = "removed_from_successor_schema"
        elif in_candidate and not in_source:
            row["classification"] = "added_in_successor_schema"
        else:
            diff = changed_mask(source[column], candidate[column])
            n = int(diff.sum())
            row["changed_row_count"] = n
            row["unchanged_row_count"] = int(len(candidate) - n)
            if n == 0:
                row["classification"] = "unchanged"
            elif pd.api.types.is_numeric_dtype(source[column]) and not (
                pd.api.types.is_bool_dtype(source[column])
            ):
                row["classification"] = "numerical_change"
            else:
                row["classification"] = "provenance_relabel"
            if (
                pd.api.types.is_numeric_dtype(source[column])
                and pd.api.types.is_numeric_dtype(candidate[column])
                and not pd.api.types.is_bool_dtype(source[column])
            ):
                delta = candidate[column].astype(float) - source[column].astype(float)
                row["max_absolute_numeric_difference"] = repr(
                    float(delta.abs().max()) if len(delta) else 0.0
                )
                row["sum_numeric_delta"] = repr(float(delta.sum()))
            if n:
                changed_ts = timestamps[diff.values]
                row["first_changed_timestamp"] = changed_ts.min().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                row["last_changed_timestamp"] = changed_ts.max().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        writer.writerow([row[key] for key in DIFF_HEADER])

    return buffer.getvalue().encode("utf-8")


def summarize_diff(
    source: pd.DataFrame, candidate: pd.DataFrame
) -> dict[str, Any]:
    changed: dict[str, Any] = {}
    unchanged = 0
    for column in source.columns:
        if column not in candidate.columns:
            continue
        n = int(changed_mask(source[column], candidate[column]).sum())
        if n:
            entry: dict[str, Any] = {"changed_rows": n}
            if pd.api.types.is_numeric_dtype(source[column]) and not (
                pd.api.types.is_bool_dtype(source[column])
            ):
                delta = candidate[column].astype(float) - source[column].astype(float)
                entry["sum_delta"] = float(delta.sum())
                entry["max_absolute_delta"] = float(delta.abs().max())
            changed[column] = entry
        else:
            unchanged += 1
    return {
        "changed_columns": changed,
        "unchanged_shared_column_count": unchanged,
        "removed_columns": [c for c in source.columns if c not in candidate.columns],
        "added_columns": [c for c in candidate.columns if c not in source.columns],
    }


# --------------------------------------------------------------------------------------
# Phase D — contract validator
# --------------------------------------------------------------------------------------

REQUIRED_MANIFEST_KEYS = (
    "schema_version",
    "candidate_identity",
    "authority",
    "repository_state",
    "sources",
    "artifact_schema",
    "target_mask",
    "numerical_inheritance",
    "provenance_transformation",
    "parquet_metadata",
    "mutation_audit",
    "outputs",
    "software",
    "immutable_hashes_before",
    "immutable_hashes_after",
    "no_solve_assertions",
    "build_gates",
    "all_build_gates_pass",
)


def validate_contract(
    adjacent_manifest: dict[str, Any],
    run_manifest: dict[str, Any],
    staged_names: set[str],
    label: str,
) -> None:
    keys = tuple(sorted(adjacent_manifest.keys()))
    gate(
        f"gate_60_manifest_top_level_keys_exact_{label}",
        keys == tuple(sorted(REQUIRED_MANIFEST_KEYS)),
        f"adjacent-manifest top-level keys={keys}",
    )
    gate(
        f"gate_61_lifecycle_status_exact_{label}",
        adjacent_manifest["candidate_identity"].get("status") == LIFECYCLE_STATUS,
        "candidate_identity.status is not the required lifecycle value.",
    )
    gate(
        f"gate_62_candidate_identity_exact_{label}",
        adjacent_manifest["candidate_identity"].get("identity") == CANDIDATE_IDENTITY,
        "candidate_identity.identity mismatch.",
    )
    gate(
        f"gate_63_epistemic_boundary_present_{label}",
        EPISTEMIC_BOUNDARY
        in str(adjacent_manifest["candidate_identity"].get("epistemic_boundary", "")),
        "Mandatory epistemic boundary missing from candidate_identity.",
    )
    gate(
        f"gate_64_epistemic_boundary_in_run_manifest_{label}",
        EPISTEMIC_BOUNDARY in json.dumps(run_manifest, ensure_ascii=False),
        "Mandatory epistemic boundary missing from run_manifest.json.",
    )
    gate(
        f"gate_65_all_build_gates_pass_top_level_{label}",
        adjacent_manifest.get("all_build_gates_pass") is True
        and run_manifest.get("all_build_gates_pass") is True,
        "all_build_gates_pass is not true at top level.",
    )
    gate(
        f"gate_66_exact_evidence_filenames_{label}",
        staged_names == set(REQUIRED_EVIDENCE_FILENAMES),
        f"planned evidence filenames={sorted(staged_names)}",
    )
    gate(
        f"gate_67_forbidden_filenames_absent_{label}",
        not (staged_names & set(FORBIDDEN_EVIDENCE_FILENAMES)),
        "A 20b-class defective evidence filename is present.",
    )
    # Scoped to this candidate's OWN output declarations. References to frozen R1
    # provenance paths inside the immutability record legitimately carry the old
    # defective names and must not be rewritten; they are not R3 outputs.
    output_blob = json.dumps(
        adjacent_manifest["outputs"], ensure_ascii=False
    ) + json.dumps(run_manifest["outputs"], ensure_ascii=False)
    gate(
        f"gate_68_no_forbidden_filename_in_output_declarations_{label}",
        not any(name in output_blob for name in FORBIDDEN_EVIDENCE_FILENAMES),
        "A 20b-class defective evidence filename string appears in an R3 output "
        "declaration.",
    )
    gate(
        f"gate_69_no_r1_r2_path_reuse_in_outputs_{label}",
        not (
            {entry["path"] for entry in adjacent_manifest["outputs"]["files"]}
            & set(R1_R2_FINAL_PATHS)
        ),
        "An output path collides with a frozen R1/R2 final path.",
    )
    strings: list[str] = []
    collect_strings(adjacent_manifest, strings, WORDING_SCAN_EXCLUDED_KEYS)
    collect_strings(run_manifest, strings, WORDING_SCAN_EXCLUDED_KEYS)
    violations = token_violations(strings)
    gate(
        f"gate_70_no_self_classification_wording_{label}",
        not violations,
        f"Self-classification wording detected: {violations[:5]}",
    )
    gate(
        f"gate_71_no_solve_assertions_zero_{label}",
        adjacent_manifest["no_solve_assertions"]["model_constructions"] == 0
        and adjacent_manifest["no_solve_assertions"]["optimization_calls"] == 0,
        "no_solve_assertions are not zero.",
    )
    gate(
        f"gate_72_output_namespace_exact_{label}",
        all(
            entry["path"].startswith(EVIDENCE_DIR_REL + "/")
            or entry["path"] in (CANDIDATE_PARQUET_REL, CANDIDATE_MANIFEST_REL)
            for entry in adjacent_manifest["outputs"]["files"]
        ),
        "An output lies outside the authorized Step 2D Candidate R3 namespace.",
    )


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------


def main(dry_run: bool = False) -> int:
    created_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    run_id = "v7_3_reconstructed_pv_mainline_candidate_r3"

    print("=" * 78)
    print("STEP 2D CANDIDATE R3 — CLEAN SUCCESSOR CONSTRUCTION")
    if dry_run:
        print("MODE: --dry-run  (construct + validate in staging; publish NOTHING)")
    print("=" * 78)

    # ---------------- Phase A ----------------------------------------------------------
    gate_r3_path_absence()
    repository_state = gate_repository_state()
    no_solve = gate_zero_solve_static()
    gate_no_r1_r2_reuse()

    immutable_before = hash_set(IMMUTABLE_SET, "script_start_before_construction")

    sources = load_sources()
    hist, promo = sources.pop("_frames")

    target = derive_target(promo, hist)
    target_mask = target["mask"]

    candidate, numerical_inheritance, provenance_transformation = build_candidate(
        hist, promo, target_mask
    )

    # ---------------- Phase C: staging -------------------------------------------------
    staging = Path(tempfile.mkdtemp(prefix="step2d_candidate_r3_"))
    try:
        staged_parquet = staging / "candidate.parquet"
        table = pa.Table.from_pandas(candidate, preserve_index=False)
        pq.write_table(table, staged_parquet, compression="snappy")

        reloaded = pd.read_parquet(staged_parquet)
        gate(
            "gate_54_parquet_roundtrip_identity",
            reloaded.equals(candidate)
            and list(reloaded.columns) == list(candidate.columns)
            and all(
                str(reloaded[c].dtype) == str(candidate[c].dtype)
                for c in candidate.columns
            ),
            "Candidate parquet does not round-trip byte-faithfully.",
        )
        candidate_physical = parquet_physical(staged_parquet)
        gate(
            "gate_55_candidate_no_serialized_index",
            not candidate_physical["serialized_index_present"],
            "Candidate parquet carries a serialized index.",
        )
        gate(
            "gate_56_candidate_no_custom_metadata",
            not candidate_physical["custom_key_value_metadata_present"],
            "Candidate parquet carries custom key/value metadata.",
        )
        gate(
            "gate_57_candidate_physical_shape",
            candidate_physical["num_rows"] == EXPECTED_ROWS
            and candidate_physical["num_columns"] == EXPECTED_CANDIDATE_COLUMNS,
            "Candidate parquet physical shape mismatch.",
        )

        parquet_payload = staged_parquet.read_bytes()
        parquet_sha = sha256_bytes(parquet_payload)

        timestamps = pd.to_datetime(candidate["timestamp"])
        hist_diff_payload = build_column_diff(
            "historical_canonical_to_candidate",
            hist,
            HISTORICAL_CANONICAL_REL,
            candidate,
            timestamps,
        )
        promo_diff_payload = build_column_diff(
            "promotion_source_to_candidate",
            promo,
            PROMOTION_SOURCE_REL,
            candidate,
            timestamps,
        )
        hist_diff_sha = sha256_bytes(hist_diff_payload)
        promo_diff_sha = sha256_bytes(promo_diff_payload)

        gate(
            "gate_58_candidate_csv_not_produced",
            True,
            "No candidate CSV is produced by this builder.",
        )

        mutation_audit = {
            "historical_canonical_to_candidate": summarize_diff(hist, candidate),
            "promotion_source_to_candidate": summarize_diff(promo, candidate),
        }
        gate(
            "gate_59_promotion_mutation_is_provenance_only",
            not any(
                "sum_delta" in entry
                for entry in mutation_audit["promotion_source_to_candidate"][
                    "changed_columns"
                ].values()
            ),
            "A numeric mutation exists between the promotion source and the candidate.",
        )

        immutable_after = hash_set(
            IMMUTABLE_SET, "after_construction_before_publication"
        )
        gate(
            "gate_73_immutability_preserved_through_construction",
            immutable_before["members"] == immutable_after["members"],
            "An immutability-set member changed during construction.",
        )

        artifact_schema = {
            "row_count": EXPECTED_ROWS,
            "column_count": EXPECTED_CANDIDATE_COLUMNS,
            "column_order": list(candidate.columns),
            "historical_50_column_ordered_prefix_exact": True,
            "added_columns": ["artifact_role"],
            "removed_columns": list(REMOVED_COLUMNS),
            "pandas_dtypes": {c: str(candidate[c].dtype) for c in candidate.columns},
            "arrow_types": candidate_physical["arrow_types"],
            "null_counts": {
                c: int(candidate[c].isna().sum()) for c in candidate.columns
            },
            "candidate_csv_written": False,
        }

        parquet_metadata = {
            "engine": "pyarrow",
            "compression": candidate_physical["compression"],
            "num_rows": candidate_physical["num_rows"],
            "num_columns": candidate_physical["num_columns"],
            "num_row_groups": candidate_physical["num_row_groups"],
            "created_by": candidate_physical["created_by"],
            "schema_metadata_keys": candidate_physical["schema_metadata_keys"],
            "custom_key_value_metadata_present": candidate_physical[
                "custom_key_value_metadata_present"
            ],
            "serialized_index_present": candidate_physical["serialized_index_present"],
            "preserve_index": False,
            "roundtrip_verified": True,
            "sha256": parquet_sha,
            "size_bytes": len(parquet_payload),
        }

        software = {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "pyarrow": pa.__version__,
            "numpy": np.__version__,
            "builder_path": BUILDER_REL,
            "builder_sha256": sha256_file(SCRIPT_PATH),
            "builder_size_bytes": SCRIPT_PATH.stat().st_size,
        }

        candidate_identity = {
            "identity": CANDIDATE_IDENTITY,
            "label": CANDIDATE_LABEL,
            "status": LIFECYCLE_STATUS,
            "epistemic_boundary": EPISTEMIC_BOUNDARY,
            "non_claim": NON_CLAIM_SENTENCE,
            "revision_disambiguation": (
                "Step 2D Candidate R3 is a data-artifact candidate revision and is "
                "unrelated to the Registry v7.3 R3 revision number; Registry v7.3 R3 "
                "remains the current evidence source of truth."
            ),
            "predecessors": {
                "step_2d_candidate_r1": "STOP / FAILED IMMUTABLE PROVENANCE",
                "step_2d_candidate_r2": "STOP / ABANDONED IMMUTABLE PROVENANCE",
            },
            "self_acceptance_performed": False,
            "routing_performed": False,
            "only_authorized_successor_step": (
                "independent read-only Step 2D-A audit of these exact bytes by a "
                "different agent"
            ),
        }

        authority = {
            "methodology": {
                "path": IMMUTABLE_TRACKED["framework_v7_3"],
                "sha256": immutable_before["members"]["framework_v7_3"]["sha256"],
            },
            "evidence": {
                "path": IMMUTABLE_TRACKED["registry_v7_3_r3"],
                "sha256": immutable_before["members"]["registry_v7_3_r3"]["sha256"],
            },
            "lifecycle_closure": {
                "path": IMMUTABLE_TRACKED["authority_freeze_v7_3"],
                "sha256": immutable_before["members"]["authority_freeze_v7_3"]["sha256"],
            },
            "provenance_procedure": {
                "path": IMMUTABLE_TRACKED["provenance_protocol"],
                "sha256": immutable_before["members"]["provenance_protocol"]["sha256"],
            },
            "research_lineage_branch": "thesis-v7",
            "methodology_changed": False,
            "closed_decision_reopened": False,
            "scientific_transformation": (
                "Reconstructed full-year PV is the best-estimate planning mainline; the "
                "historical zero-winter treatment is a conservative stress/sensitivity "
                "case. This construction step implements that already-closed Framework "
                "v7.3 decision and does not alter it."
            ),
        }

        evidence_rel = {
            name: f"{EVIDENCE_DIR_REL}/{name}" for name in REQUIRED_EVIDENCE_FILENAMES
        }
        outputs = {
            "namespace": EVIDENCE_DIR_REL,
            "candidate_parquet": CANDIDATE_PARQUET_REL,
            "candidate_adjacent_manifest": CANDIDATE_MANIFEST_REL,
            "required_evidence_filenames": list(REQUIRED_EVIDENCE_FILENAMES),
            "publication_order": [
                CANDIDATE_PARQUET_REL,
                CANDIDATE_MANIFEST_REL,
                evidence_rel[EVID_HIST_DIFF],
                evidence_rel[EVID_PROMO_DIFF],
                evidence_rel[EVID_RUN_MANIFEST],
                evidence_rel[EVID_PACKAGE],
                evidence_rel[EVID_COMPLETION],
            ],
            "completion_manifest_written_last": True,
            "files": [
                {
                    "path": CANDIDATE_PARQUET_REL,
                    "sha256": parquet_sha,
                    "size_bytes": len(parquet_payload),
                },
                {
                    "path": evidence_rel[EVID_HIST_DIFF],
                    "sha256": hist_diff_sha,
                    "size_bytes": len(hist_diff_payload),
                },
                {
                    "path": evidence_rel[EVID_PROMO_DIFF],
                    "sha256": promo_diff_sha,
                    "size_bytes": len(promo_diff_payload),
                },
                {
                    "path": CANDIDATE_MANIFEST_REL,
                    "sha256": None,
                    "sha256_registered_in": EVID_PACKAGE,
                    "note": "self-referential; hash registered in the package manifest",
                },
                {
                    "path": evidence_rel[EVID_RUN_MANIFEST],
                    "sha256": None,
                    "sha256_registered_in": EVID_PACKAGE,
                    "note": "written after this manifest; hash registered in the package manifest",
                },
                {
                    "path": evidence_rel[EVID_COMPLETION],
                    "sha256": None,
                    "sha256_registered_in": EVID_PACKAGE,
                    "note": "written last; hash registered in the package manifest",
                },
                {
                    "path": evidence_rel[EVID_PACKAGE],
                    "sha256": None,
                    "sha256_registered_in": None,
                    "note": "package manifest self-hash is omitted by design",
                },
            ],
        }

        gates_snapshot = dict(sorted(GATES.items()))
        all_pass = all(gates_snapshot.values())
        gate("gate_74_all_construction_gates_pass", all_pass, "A construction gate failed.")
        gates_snapshot = dict(sorted(GATES.items()))
        all_pass = all(gates_snapshot.values())

        adjacent_manifest = {
            "schema_version": "iris-thesis-v7.3-step2d-candidate-r3-adjacent-manifest-v1",
            "candidate_identity": candidate_identity,
            "authority": authority,
            "repository_state": repository_state,
            "sources": json_safe(sources),
            "artifact_schema": json_safe(artifact_schema),
            "target_mask": json_safe(target["record"]),
            "numerical_inheritance": json_safe(numerical_inheritance),
            "provenance_transformation": json_safe(provenance_transformation),
            "parquet_metadata": json_safe(parquet_metadata),
            "mutation_audit": json_safe(mutation_audit),
            "outputs": json_safe(outputs),
            "software": software,
            "immutable_hashes_before": immutable_before,
            "immutable_hashes_after": immutable_after,
            "no_solve_assertions": no_solve,
            "build_gates": {
                "scope": (
                    "construction gates evaluated before this manifest was serialized; "
                    "the complete gate set, including the pre-publication contract "
                    "gates and the post-publication verification gates, is recorded in "
                    "completion_manifest.json"
                ),
                "gates": gates_snapshot,
                "gate_count": len(gates_snapshot),
                "failed_gates": [k for k, v in gates_snapshot.items() if not v],
            },
            "all_build_gates_pass": all_pass,
        }
        adjacent_payload = json_bytes(adjacent_manifest)
        adjacent_sha = sha256_bytes(adjacent_payload)

        run_manifest = {
            "schema_version": "iris-thesis-v7.3-step2d-candidate-r3-run-manifest-v1",
            "run_id": run_id,
            "created_utc": created_utc,
            "candidate_identity": candidate_identity,
            "epistemic_boundary": EPISTEMIC_BOUNDARY,
            "authority": authority,
            "repository_state": repository_state,
            "sources": json_safe(sources),
            "artifact_schema": json_safe(artifact_schema),
            "target_mask": json_safe(target["record"]),
            "numerical_inheritance": json_safe(numerical_inheritance),
            "provenance_transformation": json_safe(provenance_transformation),
            "parquet_metadata": json_safe(parquet_metadata),
            "mutation_audit": json_safe(mutation_audit),
            "outputs": json_safe(outputs),
            "software": software,
            "immutable_hashes_before": immutable_before,
            "immutable_hashes_after": immutable_after,
            "no_solve_assertions": no_solve,
            "build_gates": adjacent_manifest["build_gates"],
            "all_build_gates_pass": all_pass,
            "adjacent_manifest": {
                "path": CANDIDATE_MANIFEST_REL,
                "sha256": adjacent_sha,
                "size_bytes": len(adjacent_payload),
            },
            "validation_not_performed": [
                "NO optimization solve",
                "NO EOB",
                "NO representative cases",
                "NO Layer A",
                "NO Layer B",
                "NO Final81",
                "NO production routing",
                "NO independent 2D-A acceptance",
                "NO commit",
                "NO push",
                "NO tag",
            ],
        }
        run_payload = json_bytes(run_manifest)
        run_sha = sha256_bytes(run_payload)

        # ---------------- Phase D: pre-publication contract validator ------------------
        # Derived from the manifest's own declared publication plan, not from the
        # constant, so a drifted plan fails the gate instead of passing tautologically.
        staged_names = {
            rel.rsplit("/", 1)[-1]
            for rel in adjacent_manifest["outputs"]["publication_order"]
            if rel.startswith(EVIDENCE_DIR_REL + "/")
        }
        validate_contract(adjacent_manifest, run_manifest, staged_names, "staged")
        print("[contract] pre-publication contract validation PASS")

        if dry_run:
            print()
            print("=" * 78)
            print("DRY RUN COMPLETE — NOTHING PUBLISHED")
            print("=" * 78)
            print(f"candidate parquet sha256 (staged) : {parquet_sha}")
            print(f"adjacent manifest sha256 (staged) : {adjacent_sha}")
            print(f"run manifest sha256 (staged)      : {run_sha}")
            print(f"historical diff sha256 (staged)   : {hist_diff_sha}")
            print(f"promotion diff sha256 (staged)    : {promo_diff_sha}")
            print(f"gates evaluated                   : {len(GATES)}")
            print(f"all gates pass                    : {all(GATES.values())}")
            print(f"planned evidence filenames        : {sorted(staged_names)}")
            for rel in R3_FINAL_PATHS:
                if rel == BUILDER_REL:
                    continue
                print(f"  still absent: {not (REPO_ROOT / rel).exists()}  {rel}")
            print(f"  evidence dir still absent: "
                  f"{not (REPO_ROOT / EVIDENCE_DIR_REL).exists()}")
            return 0

        # ---------------- Phase E: publication ----------------------------------------
        evidence_dir = REPO_ROOT / EVIDENCE_DIR_REL
        for rel in R3_FINAL_PATHS:
            if rel == BUILDER_REL:
                continue
            if (REPO_ROOT / rel).exists():
                raise BuildStop(f"Late path collision detected: {rel}")
        evidence_dir.mkdir(parents=True, exist_ok=False)

        published: list[tuple[str, str, int]] = []

        def publish(rel: str, payload: bytes) -> None:
            path = REPO_ROOT / rel
            path.write_bytes(payload)
            published.append((rel, sha256_bytes(payload), len(payload)))
            print(f"[publish] {rel}  sha256={sha256_bytes(payload)}  bytes={len(payload)}")

        publish(CANDIDATE_PARQUET_REL, parquet_payload)
        publish(CANDIDATE_MANIFEST_REL, adjacent_payload)
        publish(evidence_rel[EVID_HIST_DIFF], hist_diff_payload)
        publish(evidence_rel[EVID_PROMO_DIFF], promo_diff_payload)
        publish(evidence_rel[EVID_RUN_MANIFEST], run_payload)

        # ---------------- Phase F: post-publication verification -----------------------
        on_disk_ok = all(
            sha256_file(REPO_ROOT / rel) == sha for rel, sha, _ in published
        )
        immutable_post = hash_set(IMMUTABLE_SET, "after_publication_of_first_five_files")
        immutability_ok = immutable_post["members"] == immutable_before["members"]
        gate("gate_75_published_bytes_match_staging", on_disk_ok, "Published bytes drift.")
        gate(
            "gate_76_immutability_preserved_through_publication",
            immutability_ok,
            "An immutability-set member changed during publication.",
        )

        gates_final = dict(sorted(GATES.items()))
        all_pass_final = all(gates_final.values())

        completion_manifest = {
            "schema_version":
                "iris-thesis-v7.3-step2d-candidate-r3-completion-manifest-v1",
            "run_id": run_id,
            "created_utc": created_utc,
            "completed_utc": dt.datetime.now(dt.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "candidate_identity": CANDIDATE_IDENTITY,
            "status": LIFECYCLE_STATUS,
            "epistemic_boundary": EPISTEMIC_BOUNDARY,
            "non_claim": NON_CLAIM_SENTENCE,
            "semantics": (
                "This completion manifest is written last and records ONLY that the "
                "Step 2D Candidate R3 construction gates completed. It does not mean "
                "the candidate has been independently audited or externally approved."
            ),
            "published_before_this_file": [
                {"path": rel, "sha256": sha, "size_bytes": size}
                for rel, sha, size in published
            ],
            "post_publication_verification": {
                "published_bytes_match_staging": on_disk_ok,
                "immutability_set_unchanged": immutability_ok,
                "immutable_hashes_after_publication": immutable_post,
            },
            "build_gates": gates_final,
            "gate_count": len(gates_final),
            "failed_gates": [k for k, v in gates_final.items() if not v],
            "all_build_gates_pass": all_pass_final,
            "no_solve_assertions": no_solve,
            "validation_not_performed": run_manifest["validation_not_performed"],
            "next_authorized_step": (
                "INDEPENDENT READ-ONLY STEP 2D-A AUDIT OF THE EXACT STEP 2D CANDIDATE "
                "R3 BY A DIFFERENT AGENT"
            ),
        }
        completion_payload = json_bytes(completion_manifest)
        completion_sha = sha256_bytes(completion_payload)

        package_manifest = {
            "schema_version": "iris-thesis-v7.3-step2d-candidate-r3-package-manifest-v1",
            "run_id": run_id,
            "created_utc": created_utc,
            "candidate_identity": CANDIDATE_IDENTITY,
            "status": LIFECYCLE_STATUS,
            "epistemic_boundary": EPISTEMIC_BOUNDARY,
            "self_hash_omitted": True,
            "self_hash_omission_statement": (
                "package_manifest.json registers every required Step 2D Candidate R3 "
                "package file except itself; its own SHA-256 is deliberately omitted "
                "because a manifest cannot contain its own digest."
            ),
            "package_files": {
                CANDIDATE_PARQUET_REL: {
                    "sha256": parquet_sha,
                    "size_bytes": len(parquet_payload),
                },
                CANDIDATE_MANIFEST_REL: {
                    "sha256": adjacent_sha,
                    "size_bytes": len(adjacent_payload),
                },
                evidence_rel[EVID_RUN_MANIFEST]: {
                    "sha256": run_sha,
                    "size_bytes": len(run_payload),
                },
                evidence_rel[EVID_HIST_DIFF]: {
                    "sha256": hist_diff_sha,
                    "size_bytes": len(hist_diff_payload),
                },
                evidence_rel[EVID_PROMO_DIFF]: {
                    "sha256": promo_diff_sha,
                    "size_bytes": len(promo_diff_payload),
                },
                evidence_rel[EVID_COMPLETION]: {
                    "sha256": completion_sha,
                    "size_bytes": len(completion_payload),
                },
            },
            "omitted_file": evidence_rel[EVID_PACKAGE],
            "builder": {
                "path": BUILDER_REL,
                "sha256": software["builder_sha256"],
                "size_bytes": software["builder_size_bytes"],
            },
            "all_build_gates_pass": all_pass_final,
        }
        package_payload = json_bytes(package_manifest)

        # Final wording / filename validation over the last two staged payloads.
        tail_strings: list[str] = []
        collect_strings(completion_manifest, tail_strings, WORDING_SCAN_EXCLUDED_KEYS)
        collect_strings(package_manifest, tail_strings, WORDING_SCAN_EXCLUDED_KEYS)
        gate(
            "gate_77_no_self_classification_wording_tail",
            not token_violations(tail_strings),
            f"Self-classification wording: {token_violations(tail_strings)[:5]}",
        )
        tail_blob = json.dumps(
            {
                "published": completion_manifest["published_before_this_file"],
                "package": sorted(package_manifest["package_files"]),
            },
            ensure_ascii=False,
        )
        gate(
            "gate_78_no_forbidden_filenames_tail",
            not any(name in tail_blob for name in FORBIDDEN_EVIDENCE_FILENAMES),
            "A 20b-class defective evidence filename appears in a tail manifest's own "
            "file registry.",
        )
        gate(
            "gate_79_package_registers_all_but_itself",
            set(package_manifest["package_files"])
            == {
                CANDIDATE_PARQUET_REL,
                CANDIDATE_MANIFEST_REL,
                evidence_rel[EVID_RUN_MANIFEST],
                evidence_rel[EVID_HIST_DIFF],
                evidence_rel[EVID_PROMO_DIFF],
                evidence_rel[EVID_COMPLETION],
            },
            "Package manifest does not register exactly the six non-self package files.",
        )

        publish(evidence_rel[EVID_PACKAGE], package_payload)
        publish(evidence_rel[EVID_COMPLETION], completion_payload)

        # ---------------- Phase G: final verification ---------------------------------
        final_ok = all(sha256_file(REPO_ROOT / rel) == sha for rel, sha, _ in published)
        immutable_final = hash_set(IMMUTABLE_SET, "final_post_publication")
        final_immutability = immutable_final["members"] == immutable_before["members"]

        actual_evidence = sorted(p.name for p in evidence_dir.iterdir())
        print()
        print("=" * 78)
        print("FINAL VERIFICATION")
        print("=" * 78)
        print(f"published files on disk match staged bytes : {final_ok}")
        print(f"immutability set byte-identical            : {final_immutability}")
        print(f"evidence namespace filenames               : {actual_evidence}")
        print(f"exact filenames required                   : {sorted(REQUIRED_EVIDENCE_FILENAMES)}")
        print(f"filenames exact                            : "
              f"{actual_evidence == sorted(REQUIRED_EVIDENCE_FILENAMES)}")
        print(f"lifecycle status                           : {LIFECYCLE_STATUS}")
        print(f"all_build_gates_pass                       : {all_pass_final}")
        print(f"gate count                                 : {len(gates_final)}")
        print(f"completion manifest sha256                 : {completion_sha}")
        print(f"package manifest sha256                    : {sha256_bytes(package_payload)}")
        print()
        for rel, sha, size in published:
            print(f"  {sha}  {size:>10}  {rel}")
        print()
        print("VERDICT: CANDIDATE_R3_BUILT_PENDING_INDEPENDENT_2D_A")

        if not (final_ok and final_immutability and all_pass_final
                and actual_evidence == sorted(REQUIRED_EVIDENCE_FILENAMES)):
            print("VERDICT OVERRIDE: STOP — final verification failed.")
            return 3
        return 0
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    argv = set(sys.argv[1:])
    unknown = argv - {"--dry-run"}
    if unknown:
        print(f"STOP: unknown argument(s): {sorted(unknown)}")
        sys.exit(2)
    try:
        sys.exit(main(dry_run="--dry-run" in argv))
    except BuildStop as exc:
        print()
        print("=" * 78)
        print("STOP")
        print("=" * 78)
        print(str(exc))
        sys.exit(2)
