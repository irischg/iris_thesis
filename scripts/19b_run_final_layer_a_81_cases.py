#!/usr/bin/env python3
"""Frozen Layer-A orchestration. Default: non-solving implementation audit.

Only --execute-production enables the existing core's single solve per case.
No resume, grid overrides, input overrides, solver overrides or EOB re-solve.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack
from dataclasses import replace
from datetime import datetime, timezone
import copy
import gc
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
from unittest.mock import patch
import uuid

sys.dont_write_bytecode = True

import gurobipy as gp
import numpy as np
import pandas as pd

SCRIPT_VERSION = "v7.2-final-layer-a-81-production-runner-2026-09-10-r2"
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).resolve()
CHECKPOINT = "docs/checkpoints/production_checkpoint_manifest_v7_2_pre81_ready_2026-09-10.json"
CHECKPOINT_SHA = "08b1fef4e39e164336b9b890901869c6c265cb42975f44f85d21ade861a64a61"
START_HEAD = "b2acdf28cf1459aee5da44e4407c225f5d3c68a6"
TAG_OBJECT = "2aeccf585e2ff8f1e8bc67d09f1648e6556ff325"
RUNNER_AUTHORITY = "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-10.json"
PRODUCTION_TAG = "v7.2-final81-runner-ready"
AUTHORITY_VERSION = "v7.2-final81-runner-authority-1"
PREFLIGHT = "results/layer_a/final_81_preflight/20260909T170841521430Z_55cc09a45f"
PREFLIGHT_SHA = "9dcaaf00e1dc5fe7b9fcee9709fab1a81d8c32f2eb520eedda677f2081573fa0"
HELPER19 = "scripts/19a_preflight_final_layer_a_81_cases.py"
HELPER19_SHA = "ad4f041a0727ef7091e000a73eac9955466293fdfa88cfad2c072cb32e9a65ed"
PARAM_SHA = "205d5a9ce5ddad4d9f5d316546d6efcc0047a75add4c4c064838e111476e1fbf"
PRODUCTION_ROOT = ROOT / "results/layer_a/final_81/runs"
AUDIT_ROOT = ROOT / "results/layer_a/final_81_runner_audit"
PASS_VERDICT = "SCRIPT 19B IMPLEMENTATION GATE PASS — READY FOR INDEPENDENT PRE-SOLVE AUDIT"
MANDATORY = ("solver", "physical", "resilience", "billing", "transition", "cost", "degradation", "rainflow", "accepted_helper")
FAILURE_STATES = ("BUILD_FAIL", "SOLVER_NO_SOLUTION", "NON_OPTIMAL", "MIP_GAP_FAIL",
                  "PHYSICAL_GATE_FAIL", "RESILIENCE_GATE_FAIL", "BILLING_GATE_FAIL",
                  "TRANSITION_GATE_FAIL", "COST_GATE_FAIL", "DEGRADATION_GATE_FAIL",
                  "RAINFLOW_GATE_FAIL", "ARTIFACT_HASH_FAIL", "REPRESENTATIVE_CONSISTENCY_FAIL",
                  "SURFACE_GATE_FAIL", "AUTHORITY_GATE_FAIL", "EXECUTION_DISABLED", "INTERRUPTED")


class GateFailure(RuntimeError):
    def __init__(self, status, message, evidence=None):
        super().__init__(message)
        self.status, self.evidence = status, evidence


def require(ok, message, status="AUTHORITY_GATE_FAIL"):
    if not ok:
        raise GateFailure(status, message)


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [safe(v) for v in value]
    if isinstance(value, np.generic):
        return safe(value.item())
    if isinstance(value, (Path, datetime, pd.Timestamp)):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def digest(value):
    return hashlib.sha256(json.dumps(safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write(path, value):
    """Windows same-directory rename consumes the temporary; no post-commit unlink.

    This runner deliberately fails closed on other platforms: POSIX rename can
    overwrite an existing destination, unlike the required Windows primitive.
    """
    require(os.name == "nt", "Atomic no-replace publication requires Windows", "ARTIFACT_HASH_FAIL")
    path = Path(path)
    if path.exists():
        raise FileExistsError(str(path))
    fd, temporary = tempfile.mkstemp(prefix=".pending_", suffix=".json", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(safe(value), f, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        expected = sha(temporary)
        try:
            os.rename(temporary, path)
        except BaseException:
            # An interrupt may be delivered after the OS committed the rename.
            if not temporary.exists() and path.is_file() and sha(path) == expected:
                return
            raise
    except BaseException:
        # Pre-publication only. Preserve the original error and failed temporary
        # evidence if cleanup also fails; no success manifest has been published.
        try:
            temporary.unlink(missing_ok=True)
        except BaseException as cleanup_error:
            warning_only(f"Unpublished temporary retained: {temporary}: {cleanup_error}")
        raise


def warning_only(message):
    """Optional console output cannot change any published terminal verdict."""
    try:
        print(f"WARNING_ONLY: {message}", file=sys.stderr, flush=True)
    except BaseException:
        pass


def mandatory_cleanup(directory):
    pending = [str(p) for p in Path(directory).rglob(".pending_*")]
    require(not pending, f"Unfinished temporary state: {pending}", "ARTIFACT_HASH_FAIL")


def publish_case(staging, final):
    """Only cases/<ID>/ is authoritative; .staging/ is never a terminal verdict."""
    staging, final = Path(staging), Path(final)
    require(os.name == "nt" and staging.parent.parent == final.parent,
            "Case publication must use same-volume Windows staging", "ARTIFACT_HASH_FAIL")
    require(not final.exists(), "Authoritative case path already exists", "ARTIFACT_HASH_FAIL")
    require(not (final.parent / ".failures" / final.name).exists(), "Case already failed", "ARTIFACT_HASH_FAIL")
    completion = read(staging / "completion_manifest.json")
    verify_registry(staging, completion["artifact_registry"])
    mandatory_cleanup(staging)
    seal = sha(staging / "completion_manifest.json")
    try:
        os.rename(staging, final)
    except BaseException:
        if not staging.exists() and (final / "completion_manifest.json").is_file() and sha(final / "completion_manifest.json") == seal:
            return  # Committed publication, including an interrupt after rename.
        raise


def csv(path, frame):
    with Path(path).open("x", encoding="utf-8", newline="") as f:
        frame.to_csv(f, index=False)


def new_directory(parent):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:10]
    directory = Path(parent) / run_id
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").rstrip("\r\n")


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_hash(path, expected):
    path = Path(path).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(), f"Missing/outside authority path: {path}", "ARTIFACT_HASH_FAIL")
    require(sha(path) == expected, f"SHA-256 mismatch: {path}", "ARTIFACT_HASH_FAIL")


def registry(directory):
    return {p.relative_to(directory).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
            for p in sorted(Path(directory).rglob("*")) if p.is_file()}


def verify_registry(directory, entries, completion_name="completion_manifest.json"):
    directory = Path(directory).resolve()
    for name, item in entries.items():
        path = (directory / name).resolve()
        require(path.is_relative_to(directory) and path.is_file(), f"Missing/outside registered artifact: {name}", "ARTIFACT_HASH_FAIL")
        if "path" in item:
            require((ROOT / item["path"]).resolve() == path, "Registry path substitution", "ARTIFACT_HASH_FAIL")
        verify_hash(path, item["sha256"])
        require(path.stat().st_size == item["bytes"], f"Byte count mismatch: {name}", "ARTIFACT_HASH_FAIL")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    require(actual - {completion_name} == set(entries), "Incomplete artifact registry", "ARTIFACT_HASH_FAIL")


def publish_completion(directory, payload):
    require(not (Path(directory) / "failure_manifest.json").exists(), "Failed directory cannot complete", "ARTIFACT_HASH_FAIL")
    mandatory_cleanup(directory)
    entries = registry(directory)
    verify_registry(directory, entries)
    write(Path(directory) / "completion_manifest.json", {**payload, "artifact_registry": entries})


class ExecutionGuard:
    """One armed model at a time. All asynchronous solving and tuning forbidden."""
    def __init__(self, execute=False):
        self.execute = execute
        self.calls = 0
        self.forbidden_attempts = []
        self.armed = None
        self.used_models = set()
        self.after_optimize = None
        self.stack = ExitStack()
        self.methods = {}
        self.native = gp.Model.optimize

    def permit(self, model):
        require(self.execute, "Explicit --execute-production required", "EXECUTION_DISABLED")
        require(model is not None and model is self.armed and id(model) not in self.used_models,
                "Model must pass its build/parameter gate and may optimize once", "EXECUTION_DISABLED")

    def __enter__(self):
        def optimize(model, *args, **kwargs):
            try:
                self.permit(model)
            except GateFailure:
                self.forbidden_attempts.append("unauthorized_Model.optimize")
                raise
            require(not args and not kwargs, "Unexpected optimize arguments", "EXECUTION_DISABLED")
            self.used_models.add(id(model))
            self.calls += 1
            try:
                return self.native(model)
            finally:
                if self.after_optimize is not None:
                    self.after_optimize(model)

        def blocked(*args, **kwargs):
            self.forbidden_attempts.append("asynchronous_optimization_or_tuning")
            raise GateFailure("EXECUTION_DISABLED", "Asynchronous solving and tuning are forbidden")

        self.methods["optimize"] = optimize
        for name in ("optimizeAsync", "optimizeBatch", "tune"):
            if hasattr(gp.Model, name):
                self.methods[name] = blocked
        for name, method in self.methods.items():
            self.stack.enter_context(patch.object(gp.Model, name, method))
        if not self.execute:
            # Env-only environment validation remains possible; no Model can be built.
            self.stack.enter_context(patch.object(gp.Model, "__init__", blocked))
        return self

    def check(self):
        require(all(getattr(gp.Model, n) is m for n, m in self.methods.items()), "Execution guard displaced")
        require(not self.forbidden_attempts, "Forbidden model/solver/tuning attempt")

    def __exit__(self, *args):
        return self.stack.__exit__(*args)


def committed_bytes(relative):
    git("ls-files", "--error-unmatch", "--", relative)
    blob = subprocess.check_output(["git", "show", f"HEAD:{relative}"], cwd=ROOT)
    require(blob == (ROOT / relative).read_bytes(), f"Uncommitted bytes: {relative}")
    return hashlib.sha256(blob).hexdigest()


def repository_authority(execute):
    """Ancestor + external manifest + annotated current-HEAD tag, never own HEAD."""
    repo = {"branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
            "origin_tracking": git("rev-parse", "origin/thesis-v7"),
            "tag_object": git("rev-parse", "v7.2-pre81-ready"),
            "tag_peeled": git("rev-parse", "v7.2-pre81-ready^{}"),
            "worktree": git("status", "--porcelain=v1", "--untracked-files=all").splitlines(),
            "untracked_files": git("ls-files", "--others", "--exclude-standard", "-z").strip("\0").split("\0")}
    repo["untracked_files"] = [p for p in repo["untracked_files"] if p]
    require(repo["branch"] == "thesis-v7" and repo["head"] == repo["origin_tracking"], "Branch/tracking mismatch")
    require(repo["tag_object"] == TAG_OBJECT and repo["tag_peeled"] == START_HEAD
            and git("cat-file", "-t", "v7.2-pre81-ready") == "tag", "Frozen ancestor tag mismatch")
    git("merge-base", "--is-ancestor", START_HEAD, repo["head"])
    repo["frozen_ancestor_verified"] = True
    mutable = {SOURCE.relative_to(ROOT).as_posix(), RUNNER_AUTHORITY}
    changed = set(git("diff", "--name-only").splitlines()) | set(git("diff", "--cached", "--name-only").splitlines())
    require(not changed if execute else changed <= mutable, "Unapproved tracked/staged changes")
    allowed_untracked = {"docs/protocols/iris_thesis_rigorous_audit_skill.md"}
    if not execute:
        allowed_untracked |= mutable
    require(set(repo["untracked_files"]) <= allowed_untracked, "Unapproved untracked files")
    manifest = read(ROOT / RUNNER_AUTHORITY)
    require(manifest["authority_manifest_version"] == AUTHORITY_VERSION and
            manifest["required_production_tag"] == PRODUCTION_TAG and manifest["restart_policy"] == "FRESH_RUN_ONLY", "Authority schema/policy mismatch")
    require(manifest["frozen_base"] == {"tag": "v7.2-pre81-ready", "tag_object": TAG_OBJECT, "peeled_commit": START_HEAD}
            and manifest["pre81_checkpoint"] == {"path": CHECKPOINT, "sha256": CHECKPOINT_SHA}, "External base authority mismatch")
    require(manifest["runner"] == {"path": SOURCE.relative_to(ROOT).as_posix(), "version": SCRIPT_VERSION, "sha256": sha(SOURCE)}, "Runner/manifest byte identity mismatch")
    require(manifest["solver_parameter_fingerprint"] == PARAM_SHA, "External solver fingerprint mismatch")
    for path, expected in manifest["protected_identities"].items():
        verify_hash(ROOT / path, expected)
    # data/ is intentionally ignored by Git. Pin existing archives explicitly;
    # never admit arbitrary new ignored data or importable files by directory.
    ignored = [p for p in git("ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", "scripts", "src", "data").strip("\0").split("\0") if p]
    repo["ignored_runtime_files"] = ignored
    require(set(ignored) == set(manifest["ignored_runtime_inventory"]), "Unapproved ignored runtime/data file")
    for path, item in manifest["ignored_runtime_inventory"].items():
        verify_hash(ROOT / path, item["sha256"])
    refs_args = ["refs/heads/thesis-v7", "refs/tags/v7.2-pre81-ready", "refs/tags/v7.2-pre81-ready^{}"]
    expected_refs = {refs_args[0]: repo["head"], refs_args[1]: TAG_OBJECT, refs_args[2]: START_HEAD}
    ready = False
    try:
        repo["runner_committed_sha256"] = committed_bytes(SOURCE.relative_to(ROOT).as_posix())
        repo["manifest_committed_sha256"] = committed_bytes(RUNNER_AUTHORITY)
        require(git("cat-file", "-t", PRODUCTION_TAG) == "tag", "Production tag is not annotated")
        require(git("rev-parse", PRODUCTION_TAG + "^{}") == repo["head"], "Production tag/HEAD mismatch")
        repo["production_tag_object"] = git("rev-parse", PRODUCTION_TAG)
        ready = not changed
    except (GateFailure, subprocess.CalledProcessError) as exc:
        if execute:
            raise GateFailure("PRODUCTION_AUTHORITY_NOT_YET_FROZEN", str(exc)) from exc
        repo["not_yet_frozen_reason"] = str(exc)
    if ready:
        refs_args += ["refs/tags/" + PRODUCTION_TAG, "refs/tags/" + PRODUCTION_TAG + "^{}"]
        expected_refs.update({refs_args[-2]: repo["production_tag_object"], refs_args[-1]: repo["head"]})
    refs = dict(line.split()[::-1] for line in git("ls-remote", "origin", *refs_args).splitlines())
    require(refs == expected_refs, "Live remote authority mismatch")
    repo["live_remote"] = refs
    repo["deployment_status"] = "PRODUCTION_AUTHORITY_FROZEN" if ready else "PRODUCTION_AUTHORITY_NOT_YET_FROZEN"
    require(not execute or ready, "Committed/tagged production authority required", "PRODUCTION_AUTHORITY_NOT_YET_FROZEN")
    return repo, manifest


def authority_gate(guard):
    verify_hash(ROOT / CHECKPOINT, CHECKPOINT_SHA)
    verify_hash(ROOT / HELPER19, HELPER19_SHA)
    h19 = load(HELPER19, "runner19b_h19")
    checkpoint = read(ROOT / CHECKPOINT)
    require(checkpoint["checkpoint_role"] == "FINAL_81_BUILD_READY_PRE_PRODUCTION_SOLVE_FREEZE"
            and checkpoint["status"] == "FROZEN_PRE81_READY", "Wrong checkpoint role/status")
    repo, runner_authority = repository_authority(guard.execute)
    post17, prior, identities = h19.lineage_gate()
    for path, expected in h19.identity_pairs(checkpoint):
        h19.verify_identity(path, expected, identities)
    accepted = ROOT / PREFLIGHT
    verify_hash(accepted / "completion_manifest.json", PREFLIGHT_SHA)
    complete = read(accepted / "completion_manifest.json")
    require(complete["status"] == "PASS" and complete["run_id"] == accepted.name
            and complete["optimization_calls"] == 0 and complete["builds_passed"] == 81
            and complete["script_sha256"] == HELPER19_SHA, "19a completion rejected")
    verify_registry(accepted, complete["artifact_registry"])
    for item in complete["artifact_registry"].values():
        identities[item["path"]] = item["sha256"]
    identities[f"{PREFLIGHT}/completion_manifest.json"] = PREFLIGHT_SHA
    old_run = read(accepted / "run_manifest.json")
    identities.update(old_run["source_and_artifact_hashes_before"])
    for path, expected in identities.items():
        verify_hash(ROOT / path, expected)
    identities[CHECKPOINT] = CHECKPOINT_SHA
    identities[SOURCE.relative_to(ROOT).as_posix()] = sha(SOURCE)
    identities[RUNNER_AUTHORITY] = sha(ROOT / RUNNER_AUTHORITY)
    controls = {key: h19.existing_validator(path) for key, path in (
        ("18a", "scripts/18a_validate_production_checkpoint.py"),
        ("18b", "scripts/18b_preflight_production_environment.py"))}
    sys.path.insert(0, str(ROOT))
    from src import annual_design_model_v7_2 as core
    h16 = h19.load_module("scripts/16a_preflight_layer_a_representative_binary_cases.py", "runner19b_h16")
    h09 = h19.load_module("scripts/09_build_valid_outage_start_sets.py", "runner19b_h09")
    require(core.CORE_VERSION == h19.CORE_VERSION, "Core version mismatch")
    inputs = core.load_annual_design_inputs(ROOT, annual_parquet=ROOT / h19.CANONICAL,
                                          annual_csv=ROOT / "data/processed/NO_FALLBACK_ALLOWED.csv")
    require(Path(inputs.source_paths["annual_input"]).resolve() == ROOT / h19.CANONICAL, "Noncanonical input")
    require(digest(inputs.mainline_package) == old_run["routing"]["package_sha256"], "Package drift")
    require(inputs.kappa == old_run["routing"]["kappa"], "Kappa drift")
    require((core.SOC_MIN, core.SOC_MAX, core.ETA_C, core.ETA_D) == (0.1, 0.9, 0.9, 0.9), "Physics drift")
    matrix = pd.read_csv(accepted / "case_matrix.csv", float_precision="round_trip")
    grid = read(accepted / "grid_definition.json")
    require(grid["alpha_values"] == checkpoint["grid_closure"]["alpha_values"] and
            grid["beta_values_h"] == checkpoint["grid_closure"]["beta_values_h"], "Grid definition drift")
    expected = {(a, b) for a in grid["alpha_values"] for b in grid["beta_values_h"]}
    require(len(matrix) == matrix.case_id.nunique() == 81 and
            set(zip(matrix.alpha, matrix.beta_h)) == expected, "Grid coverage mismatch")
    require(matrix.case_id.tolist() == old_run["case_order"], "Case order drift")
    recomputed, cross, starts = h19.requirements_gate(inputs, h16, h09, post17, prior, identities)
    for name in recomputed.columns:
        if "historical" in name:
            require(pd.to_datetime(matrix[name]).equals(pd.to_datetime(recomputed[name])), f"Window drift: {name}")
        elif pd.api.types.is_numeric_dtype(recomputed[name]):
            require(np.allclose(matrix[name], recomputed[name], atol=1e-6, rtol=0), f"Requirement drift: {name}")
        else:
            require(matrix[name].tolist() == recomputed[name].tolist(), f"Routing drift: {name}")
    pd.testing.assert_frame_equal(starts, pd.read_parquet(accepted / "valid_start_sets.parquet"))
    parameters = read(accepted / "solver_parameter_fingerprint.json")
    require(runner_authority["routing"] == old_run["routing"] and
            runner_authority["accepted_19a"] == {"script_path": HELPER19, "script_sha256": HELPER19_SHA,
                "run_directory": PREFLIGHT, "completion_sha256": PREFLIGHT_SHA} and
            runner_authority["grid_authority"] == {"path": PREFLIGHT + "/case_matrix.csv", "sha256": sha(accepted / "case_matrix.csv"),
                "alpha_values": grid["alpha_values"], "beta_values_h": grid["beta_values_h"], "count": 81}, "External routing/grid/19a mismatch")
    require(parameters["sha256"] == digest(parameters["parameters"]) == PARAM_SHA, "Parameter fingerprint mismatch")
    for case in matrix.to_dict("records"):
        record = read(accepted / "cases" / f"{case['case_id']}_build_audit.json")
        require(record["parameters"]["sha256"] == digest(record["parameters"]["parameters"]) == PARAM_SHA,
                "Per-case parameter mismatch")
        require(record["model_status"] == gp.GRB.LOADED and record["solution_count"] == 0
                and record["optimization_calls"] == 0 and record["model_disposed"], "Unaccepted prior build")
        require(record["routing"] == old_run["routing"], "Per-case routing differs")
        require(record["counts"] == parameters["structural_counts"], "Per-case structure differs")
    eob_identity = prior["frozen_eob_comparator"]
    eob_record = read(ROOT / eob_identity["result"]["path"])
    eob = eob_record.get("result", eob_record)
    require(eob["has_solution"] and eob["status"] == "OPTIMAL" and eob["objective_ntd2023_per_year"] > 0, "EOB comparator rejected")
    design = read(accepted / "production_runner_design_audit.json")
    require(design["resume_policy"] == "FRESH_RUN_ONLY", "Restart policy differs")
    guard.check()
    ctx = dict(h19=h19, h16=h16, h09=h09, core=core, inputs=inputs, matrix=matrix, starts=starts,
               cross=cross, parameters=parameters, identities=identities, routing=old_run["routing"],
               eob=eob, eob_identity=eob_identity, prior=prior, checkpoint=checkpoint,
               settings=core.SolveSettings(mode="binary", mip_gap=1e-6, time_limit_sec=None,
                                           output_flag=0, numeric_focus=1),
               input_fingerprint=h19.input_fingerprint(inputs))
    ctx["authority"] = {"status": "PASS", "repository": repo, "controls": controls,
                        "runner_authority": {"path": RUNNER_AUTHORITY, "sha256": sha(ROOT / RUNNER_AUTHORITY)},
                        "deployment_status": repo["deployment_status"],
                        "checkpoint_sha256": CHECKPOINT_SHA, "accepted_19a_completion_sha256": PREFLIGHT_SHA,
                        "registered_19a_artifacts": len(complete["artifact_registry"]), "routing": ctx["routing"],
                        "frozen_eob": eob_identity, "verified_hashes": identities}
    ctx["execute"] = guard.execute
    return ctx


def solver_acceptance(result):
    if not result.get("has_solution"):
        return "SOLVER_NO_SOLUTION"
    if result.get("status") != "OPTIMAL" or result.get("status_code") != gp.GRB.OPTIMAL:
        return "NON_OPTIMAL"
    gap = result.get("mip_gap")
    if gap is None or not math.isfinite(float(gap)) or not 0 <= float(gap) <= 1e-6:
        return "MIP_GAP_FAIL"
    if not math.isfinite(float(result.get("objective_ntd2023_per_year", math.nan))):
        return "SOLVER_NO_SOLUTION"
    return "COMPLETE_SOLVER_PASS"


def all_start_audit(ctx, case, sizing):
    """Framework 7.10: post-solve replay, not an optimization formulation.

    Stored R/Pout come from the accepted 16a callable. This adapter independently
    applies discharge-only state transitions over the exact Script-09 windows.
    """
    c, annual = ctx["core"], ctx["inputs"].annual
    en, pb = float(sizing["E_N_kwh"]), float(sizing["P_B_kw_ac"])
    beta, reserve = int(case["beta_h"]), float(case["R_kwh_battery"])
    starts = ctx["starts"].loc[ctx["starts"].beta_hours.eq(beta)].reset_index(drop=True)
    expected = ctx["h09"].build_valid_start_rows(annual.timestamp, beta)
    try:
        pd.testing.assert_frame_equal(starts, expected, check_dtype=False)
    except AssertionError as exc:
        raise GateFailure("RESILIENCE_GATE_FAIL", "Script-09 window identity mismatch") from exc
    index = starts.start_index.to_numpy(int)
    d = np.maximum(float(case["alpha"]) * annual.baseline_load_kw.to_numpy(float) - annual.pv_available_kw.to_numpy(float), 0)
    windows = np.lib.stride_tricks.sliding_window_view(d, beta)[index]
    consumption = np.cumsum(windows * c.DELTA_T_HR / c.ETA_D, axis=1)
    state = c.SOC_MIN * en + reserve - consumption
    initial = c.SOC_MIN * en + reserve
    terminal_margin = state[:, -1] - c.SOC_MIN * en
    power_margin = pb - windows.max(axis=1)
    binding = int(np.argmax(consumption[:, -1]))
    maximum_reserve = float(consumption[binding, -1])
    checks = {
        "finite_nonnegative_sizing": math.isfinite(en) and math.isfinite(pb) and en >= 0 and pb >= 0,
        "initial_preparedness_within_socmax": initial <= c.SOC_MAX * en + c.BALANCE_TOL,
        "all_start_technical_socmin": bool(np.min(state) >= c.SOC_MIN * en - c.BALANCE_TOL),
        "all_start_socmax": bool(np.max(state) <= c.SOC_MAX * en + c.BALANCE_TOL),
        "all_start_power": bool(power_margin.min() >= -1e-6),
        "accepted_reserve": abs(maximum_reserve - reserve) <= 1e-6,
        "accepted_pout": abs(float(d.max()) - float(case["P_out_kw_ac"])) <= 1e-6,
        "nameplate_lower_bound": en + 1e-6 >= float(case["analytical_E_N_min_kwh"]),
        "binding_start": int(index[binding]) == int(case["binding_start_index"]),
        "binding_timestamp": pd.Timestamp(starts.iloc[binding].start_timestamp) == pd.Timestamp(case["binding_historical_start"]),
        "binding_end": pd.Timestamp(starts.iloc[binding].end_timestamp_exclusive) == pd.Timestamp(case["binding_historical_end_exclusive"]),
        "valid_count": len(starts) == int(case["valid_start_count"]),
        "binding_ends_at_technical_socmin": abs(float(terminal_margin[binding])) <= c.BALANCE_TOL,
    }
    evidence = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
                "valid_start_count": len(starts), "binding_start_index": int(index[binding]),
                "binding_start": starts.iloc[binding].start_timestamp,
                "binding_end_exclusive": starts.iloc[binding].end_timestamp_exclusive,
                "initial_energy_kwh": initial, "minimum_terminal_margin_kwh": float(terminal_margin.min()),
                "minimum_power_margin_kw": float(power_margin.min()), "circular_wrap": False,
                "surplus_pv_recharge": False, "terminal_rule": "technical SOCmin only; no reserve restoration",
                "annual_floor": "SOCmin*E_N + R", "outage_floor": "SOCmin*E_N"}
    table = starts.copy()
    table["consumed_battery_kwh"] = consumption[:, -1]
    table["terminal_margin_kwh"] = terminal_margin
    table["minimum_power_margin_kw"] = power_margin
    if not all(checks.values()):
        raise GateFailure("RESILIENCE_GATE_FAIL", "All-start consistency failed", evidence)
    return evidence, table


def physical_audit(ctx, case, result):
    c, a, d = ctx["core"], ctx["inputs"].annual, result["dispatch"]
    en, pb, cc = (float(result["sizing"][k]) for k in ("E_N_kwh", "P_B_kw_ac", "CC_regular_kw"))
    require(len(d) == len(a) and pd.DatetimeIndex(pd.to_datetime(d.timestamp)).equals(pd.DatetimeIndex(a.timestamp)),
            "Dispatch chronology mismatch", "PHYSICAL_GATE_FAIL")
    state = d[[f"e_seg_{k}_kwh" for k in range(1, 4)]].to_numpy(float)
    ch = d[[f"p_charge_seg_{k}_kw_ac" for k in range(1, 4)]].to_numpy(float)
    dis = d[[f"p_discharge_seg_{k}_kw_ac" for k in range(1, 4)]].to_numpy(float)
    end = np.array(result.get("terminal_e_seg_kwh", state[-1] + c.ETA_C * ch[-1] - dis[-1] / c.ETA_D), float)
    all_state = np.vstack([state, end])
    physical = c.SOC_MIN * en + all_state.sum(axis=1)
    pc, pd_, pg, curtail = (d[k].to_numpy(float) for k in ("p_charge_kw_ac", "p_discharge_kw_ac", "p_grid_kw", "pv_curtailment_kw"))
    numeric = np.column_stack([d.select_dtypes(include="number").to_numpy(float)])
    residuals = {
        "ac_balance_kw": float(np.max(np.abs(pg + a.pv_available_kw.to_numpy(float) - curtail + pd_ - a.baseline_load_kw.to_numpy(float) - pc))),
        "segment_dynamics_kwh": float(np.max(np.abs(np.diff(all_state, axis=0) - c.ETA_C * ch + dis / c.ETA_D))),
        "cyclic_kwh": float(np.max(np.abs(end - state[0]))),
        "physical_state_identity_kwh": float(np.max(np.abs(d.e_physical_kwh.to_numpy(float) - physical[:-1]))),
        "charge_link_kw": float(np.max(np.abs(ch.sum(axis=1) - pc))),
        "discharge_link_kw": float(np.max(np.abs(dis.sum(axis=1) - pd_))),
        "soc_identity": float(np.max(np.abs(d.soc_fraction.to_numpy(float) * en - physical[:-1]))),
    }
    checks = {"finite": bool(np.isfinite(numeric).all() and all(math.isfinite(v) for v in (en, pb, cc))),
              "sizing": en > 0 and pb >= 0 and cc >= 0,
              "binary": result["mode"] == "binary",
              "state_bounds": bool(all_state.min() >= -c.BALANCE_TOL and np.all(all_state <= en * np.array(c.SEGMENT_WIDTHS) + c.BALANCE_TOL)),
              "soc_bounds": bool(physical.min() >= c.SOC_MIN * en - c.BALANCE_TOL and physical.max() <= c.SOC_MAX * en + c.BALANCE_TOL),
              "reserve_floor": bool(physical.min() >= c.SOC_MIN * en + float(case["R_kwh_battery"]) - c.BALANCE_TOL),
              "power_bounds": bool(min(pc.min(), pd_.min(), pg.min(), curtail.min(), ch.min(), dis.min()) >= -c.BALANCE_TOL and max(pc.max(), pd_.max()) <= pb + c.BALANCE_TOL),
              "pv_curtailment_bounds": bool(np.all(curtail <= a.pv_available_kw.to_numpy(float) + c.BALANCE_TOL)),
              "exclusivity": bool(np.minimum(pc, pd_).max() <= c.SIMULTANEOUS_TOL_KW),
              "residuals": all(v <= c.BALANCE_TOL for v in residuals.values())}
    if "u_mode" in d:
        u = d.u_mode.to_numpy(float)
        checks["binary_values"] = bool(np.all(np.abs(u - np.round(u)) <= 1e-5) and np.all((u >= -1e-5) & (u <= 1+1e-5)))
    annual_totals = {"grid_import_kwh": float(pg.sum()), "charge_ac_kwh": float(pc.sum()),
                     "discharge_ac_kwh": float(pd_.sum()), "pv_curtailment_kwh": float(curtail.sum()),
                     "battery_side_discharge_kwh": float(pd_.sum()/c.ETA_D)}
    checks["annual_energy_totals"] = all(abs(value-result["annual_energy"][key]) <= .001
                                         for key, value in annual_totals.items())
    require(all(checks.values()), f"Physical audit: {checks}; {residuals}", "PHYSICAL_GATE_FAIL")
    headroom = physical - (c.SOC_MIN * en + float(case["R_kwh_battery"]))
    return {"status": "PASS", "checks": checks, "residuals": residuals,
            "terminal_e_seg_kwh": end.tolist(), "soc_min": float(physical.min()/en), "soc_max": float(physical.max()/en),
            "minimum_headroom_kwh": float(headroom.min()), "mean_headroom_kwh": float(headroom.mean()),
            "reserve_floor_binding_state_count": int(np.sum(np.abs(headroom) <= c.BALANCE_TOL)),
            "maximum_hourly_discharge_fraction_nameplate": float(pd_.max()/c.ETA_D/en)}


def billing_audit(ctx, result):
    c, inputs = ctx["core"], ctx["inputs"]
    a, b, d = inputs.annual, result["billing_exact"], result["dispatch"]
    structure = ctx["h16"].billing_structure_audit(b, a)
    require(all(v == "PASS" for v in structure.values() if isinstance(v, str)), "Billing keys/calendar", "BILLING_GATE_FAIL")
    residuals = []
    for row in b.itertuples():
        month = a.billing_usage_period_id.astype(str).eq(str(row.billing_usage_period_id)).to_numpy()
        active = month & a.season.eq(row.season).to_numpy() & a.tou_period.eq(row.tou_period).to_numpy()
        exact = float(inputs.kappa * d.loc[active, "p_grid_kw"].max())
        overall = float(inputs.kappa * d.loc[month, "p_grid_kw"].max())
        residuals.extend([abs(exact-row.exact_billing_demand_kw), abs(overall-row.overall_exact_billing_demand_kw),
                          abs(row.cc_regular_kw-result["sizing"]["CC_regular_kw"]),
                          abs(max(0, exact-row.cc_regular_kw)-row.raw_overage_kw)])
    require(max(residuals) <= c.BALANCE_TOL, "Exact hourly proxy maxima mismatch", "BILLING_GATE_FAIL")
    costs = result["cost_components_ntd2023_per_year"]
    require(abs(costs["overcontract_pure_season"]-result["pure_season_overcontract_exact_ntd"]) <= .05
            and abs(costs["overcontract_transition_resolved"]-result["transition_resolved_overcontract_exact_ntd"]) <= .05,
            "Core exact overcontract reconstruction mismatch", "BILLING_GATE_FAIL")
    basic = sum(c._regular_basic_rate(inputs, month, c._pure_month_season(a, indices))
                for month, indices in c._month_groups(a).items()) * float(result["sizing"]["CC_regular_kw"])
    energy = float(np.dot(d.p_grid_kw, inputs.energy_rate_ntd2023_per_kwh))
    require(abs(basic-costs["basic"]) <= .001 and abs(energy-costs["energy"]) <= .001,
            "Basic/TOU cost mismatch", "BILLING_GATE_FAIL")
    return {"status": "PASS", "structure": structure, "max_demand_residual_kw": max(residuals),
            "exact_definition": "maximum optimized hourly calibrated proxy; not physical 15-minute reconstruction",
            "basic_reconstructed_ntd2023": basic, "energy_reconstructed_ntd2023": energy}


def transition_audit(ctx, result):
    t, detail = result["transition_settlement"], result["transition_settlement_detail"]
    require(t["postsolve_invariants_pass"] and not t["postsolve_invariant_failures"] and
            t["numerical_boundary_unresolved_count"] == 0 and
            t["nonbinding_certificate"] == "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE",
            "Transition certificate rejected", "TRANSITION_GATE_FAIL")
    require(len(detail) > 0 and abs(float(detail.resolved_exact_charge_ntd2023.sum()) -
            result["cost_components_ntd2023_per_year"]["overcontract_transition_resolved"]) <= .05,
            "Transition detail cost mismatch", "TRANSITION_GATE_FAIL")
    flags = [n for n in detail.columns if n.endswith("_pass")]
    require(all(detail[n].map(lambda v: str(v).lower() == "true").all() for n in flags),
            "Transition detail invariant failed", "TRANSITION_GATE_FAIL")
    return {"status": "PASS", "certificate": t["nonbinding_certificate"], "invariant_columns": flags,
            "claim_boundary": "frozen project-specific settlement interpretation; not a universally published Taipower optimization formula"}


def cost_degradation_audit(ctx, result):
    c, p, d = ctx["core"], ctx["inputs"].mainline_package, result["dispatch"]
    en, pb = result["sizing"]["E_N_kwh"], result["sizing"]["P_B_kw_ac"]
    costs = result["cost_components_ntd2023_per_year"]
    expected = {"annualized_capex", "fom", "energy", "basic", "overcontract_pure_season", "overcontract_transition_resolved", "degradation"}
    require(set(costs) == expected and all(math.isfinite(float(v)) for v in costs.values()), "Cost schema mismatch", "COST_GATE_FAIL")
    split = {"annualized_energy_capex": en*p["annualized_capex_C_E_ntd2023_per_kwh_year"],
             "annualized_power_capex": pb*p["annualized_capex_C_P_ntd2023_per_kw_year"],
             "fom": en*p["fom_E_ntd2023_per_kwh_year"]+pb*p["fom_P_ntd2023_per_kw_year"]}
    require(abs(sum(costs.values())-result["objective_ntd2023_per_year"]) <= c.COST_RECONCILIATION_TOL_NTD
            and abs(split["annualized_energy_capex"]+split["annualized_power_capex"]-costs["annualized_capex"]) <= .001
            and abs(split["fom"]-costs["fom"]) <= .001, "Objective decomposition mismatch", "COST_GATE_FAIL")
    segment = []
    for k in range(1, 4):
        energy = float(d[f"p_discharge_seg_{k}_kw_ac"].sum()/c.ETA_D)
        segment.append({"segment": k, "battery_side_discharge_kwh": energy,
                        "cost_ntd2023": energy*p[f"lambda_{k}_ntd2023_per_battery_side_discharged_kwh"]})
    total = float(d.p_discharge_kw_ac.sum()/c.ETA_D)
    require(abs(sum(r["battery_side_discharge_kwh"] for r in segment)-total) <= .001
            and abs(total-result["annual_energy"]["battery_side_discharge_kwh"]) <= .001
            and abs(sum(r["cost_ntd2023"] for r in segment)-costs["degradation"]) <= .001,
            "Segment throughput/cost reconciliation failed", "DEGRADATION_GATE_FAIL")
    # Persistent state, linkage, cyclicity and efficiencies are checked by physical_audit.
    return ({"status": "PASS", "components": costs, "capex_split": split,
             "objective_residual_ntd2023": sum(costs.values())-result["objective_ntd2023_per_year"]},
            {"status": "PASS", "segments": segment, "battery_side_discharge_kwh": total,
             "persistent_segment_chronology_gate": "physical", "rainflow_is_ex_post_only": True})


def postsolve(ctx, case, result, output=None):
    gates, evidence = {}, {}
    status = solver_acceptance(result)
    require(status == "COMPLETE_SOLVER_PASS", "Solver outcome rejected", status)
    gates["solver"] = "PASS"
    # Save each passed adapter immediately; failure retains prior evidence.
    def save(name, value):
        evidence[name] = value
        gates[name] = "PASS"
        if output is not None:
            write(output / f"{name}_audit.json", value)
    def checked(name, function):
        try:
            return function()
        except GateFailure:
            raise
        except Exception as exc:
            raise GateFailure(f"{name.upper()}_GATE_FAIL", f"{name} adapter exception: {exc}") from exc
    save("physical", checked("physical", lambda: physical_audit(ctx, case, result)))
    replay, table = checked("resilience", lambda: all_start_audit(ctx, case, result["sizing"]))
    if output is not None:
        csv(output / "all_start_replay.csv", table)
    save("resilience", replay)
    billing = checked("billing", lambda: billing_audit(ctx, result))
    save("billing", billing)
    save("transition", checked("transition", lambda: transition_audit(ctx, result)))
    costs, degradation = checked("cost", lambda: cost_degradation_audit(ctx, result))
    save("cost", costs)
    save("degradation", degradation)
    rain = checked("rainflow", lambda: ctx["h16"].validate_representative_rainflow(ROOT, ctx["inputs"], result))
    if output is not None:
        for key, value in rain.items():
            if isinstance(value, pd.DataFrame):
                csv(output / f"rainflow_{key}.csv", value)
        write(output / "rainflow_diagnostics.json", {k: v for k, v in rain.items() if not isinstance(v, pd.DataFrame)})
    require(rain["summary"]["verdict"] == "RAINFLOW_VALIDATION_PASS" and all(v == "PASS" for v in rain["gates"].values()),
            "Required rainflow gate failed", "RAINFLOW_GATE_FAIL")
    save("rainflow", {"status": "PASS", "summary": rain["summary"], "gates": rain["gates"]})
    accepted = ctx["h16"].representative_gate(result, case, ctx["eob"], soc_min=.1, soc_max=.9,
                                             rainflow_validation=rain, billing_audit=billing["structure"])
    require(all(v == "PASS" for v in accepted.values()), f"Accepted helper gates: {accepted}", "PHYSICAL_GATE_FAIL")
    save("accepted_helper", {"status": "PASS", "gates": accepted})
    return gates, evidence


def representative_comparison(ctx, case, result):
    records = {r["case_id"]: r for r in ctx["cross"]["representative_reconciliation"]}
    if case["case_id"] not in records:
        return {"status": "NOT_A_REPRESENTATIVE_COORDINATE"}
    item = records[case["case_id"]]
    verify_hash(ROOT / item["path"], item["sha256"])
    old = read(ROOT / item["path"])["result"]
    require(old["core_version"] == result["core_version"] and old["mode"] == result["mode"] == "binary",
            "Representative methodology mismatch", "REPRESENTATIVE_CONSISTENCY_FAIL")
    delta_cost = result["objective_ntd2023_per_year"] - old["objective_ntd2023_per_year"]
    # Objective differences covered by the two certified gap intervals are explained.
    allowance = max(.001, abs(old["objective_ntd2023_per_year"])*old["mip_gap"] +
                    abs(result["objective_ntd2023_per_year"])*result["mip_gap"])
    deltas = {k: float(result["sizing"][k])-float(old["sizing"][k]) for k in old["sizing"]}
    # No new methodological materiality threshold: non-numerical sizing changes
    # conservatively block for explicit academic investigation (alternative optima possible).
    unexplained = abs(delta_cost) > allowance or any(abs(v) > ctx["core"].BALANCE_TOL for v in deltas.values())
    return {"status": "BLOCKER_REQUIRES_INVESTIGATION" if unexplained else "PASS", "reference": item,
            "objective_difference_ntd2023": delta_cost, "certified_gap_allowance_ntd2023": allowance,
            "sizing_differences": deltas, "trajectory_identity_required": False,
            "policy": "Changes beyond numerical sizing tolerance require review; no automatic materiality threshold or alternate-optimum waiver."}


def case_summary(ctx, case, result, evidence, gates, run_id):
    premium = ctx["h16"].eob_comparison(result, ctx["eob"])
    return {**case, **result["sizing"], "run_id": run_id, "status": "COMPLETE_PASS",
            "E_U_kwh": .8*result["sizing"]["E_N_kwh"],
            "annual_objective_ntd2023": result["objective_ntd2023_per_year"],
            "absolute_premium_ntd2023": premium["delta_objective_ntd2023_per_year"],
            "relative_premium_pct": premium["resilience_premium_pct"],
            "cost_components": evidence["cost"], "annual_energy": result["annual_energy"],
            "physical": evidence["physical"], "degradation": evidence["degradation"],
            "rainflow": evidence["rainflow"]["summary"], "solver_status": result["status"],
            "runtime_sec_gurobi": result["runtime_sec_gurobi"], "runtime_sec_wall": result["runtime_sec_wall"],
            "mip_gap": result["mip_gap"], "best_bound": result.get("best_bound"), "node_count": result.get("node_count"),
            "canonical_sha256": ctx["h19"].CANONICAL_SHA, "core_sha256": ctx["h19"].CORE_SHA,
            "parameter_fingerprint": PARAM_SHA, "routing_fingerprint": digest(ctx["routing"]),
            "eob_sha256": ctx["eob_identity"]["result"]["sha256"], "currency": "constant NTD-2023", "gates": gates}


def finish_case(directory, run_id, case, summary, gates, calls):
    require(set(gates) == set(MANDATORY) and all(v == "PASS" for v in gates.values()), "Missing/failed case gate", "PHYSICAL_GATE_FAIL")
    require(calls == 1 and summary["status"] == "COMPLETE_PASS" and summary["run_id"] == run_id
            and summary["case_id"] == case["case_id"], "Case completion identity/count mismatch", "ARTIFACT_HASH_FAIL")
    required_files = {"case_manifest.json", "build_audit.json", "solver_outcome.json", "solver_primal.npz",
                      "solver_telemetry.jsonl", "result.json", "dispatch.csv", "billing_exact.csv",
                      "transition_settlement_detail.csv", "case_summary.json", "all_start_replay.csv",
                      "rainflow_diagnostics.json", "representative_comparison.json"}
    required_files.update(f"{name}_audit.json" for name in MANDATORY if name != "solver")
    require(all((Path(directory)/name).is_file() for name in required_files),
            "Mandatory case evidence missing", "ARTIFACT_HASH_FAIL")
    publish_completion(directory, {"status": "COMPLETE_PASS", "run_id": run_id, "case_id": case["case_id"],
                                  "alpha": case["alpha"], "beta_h": case["beta_h"], "optimization_calls": calls,
                                  "gates": gates, "parameter_fingerprint": PARAM_SHA,
                                  "routing_fingerprint": summary["routing_fingerprint"],
                                  "eob_sha256": summary["eob_sha256"]})


def failure_evidence(directory, exc, case_id=None, statuses=None, calls=0):
    # Terminal completion is irreversible. This also handles an interrupt just
    # after a run's atomic completion rename but before the caller returns.
    if (Path(directory) / "completion_manifest.json").exists():
        warning_only(f"Post-publication exception; terminal completion retained: {exc}")
        return {"status": "WARNING_ONLY", "terminal_state_changed": False}
    payload = {"status": getattr(exc, "status", "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "BUILD_FAIL"),
               "case_id": case_id, "reason": str(exc), "exception_type": type(exc).__name__,
               "traceback": traceback.format_exc(), "optimization_calls": calls,
               "case_states": statuses, "success": False, "evidence": getattr(exc, "evidence", None)}
    try:
        write(Path(directory) / "failure_manifest.json", payload)
    except BaseException as write_error:
        print(json.dumps(safe({"failure_evidence": payload, "failure_write_error": str(write_error)})), file=sys.stderr, flush=True)
    return payload


def recheck(ctx):
    for path, expected in ctx["identities"].items():
        verify_hash(ROOT / path, expected)
    require(ctx["h19"].input_fingerprint(ctx["inputs"]) == ctx["input_fingerprint"], "Shared inputs mutated")
    repo, _ = repository_authority(ctx["execute"])
    original = ctx["authority"]["repository"]
    require(all(repo.get(k) == original.get(k) for k in (
        "head", "branch", "tag_object", "tag_peeled", "origin_tracking", "production_tag_object",
        "runner_committed_sha256", "manifest_committed_sha256", "deployment_status", "live_remote")), "Repository changed during run")


def execute_case(ctx, guard, case, directory, run_id):
    require(guard.execute, "Explicit --execute-production required", "EXECUTION_DISABLED")
    require(ctx["execute"] and ctx["authority"]["deployment_status"] == "PRODUCTION_AUTHORITY_FROZEN",
            "Committed/tagged production authority required", "PRODUCTION_AUTHORITY_NOT_YET_FROZEN")
    recheck(ctx)
    final = Path(directory)
    require(not final.exists(), "Fresh authoritative case path required", "ARTIFACT_HASH_FAIL")
    staging_parent = final.parent / ".staging"
    staging_parent.mkdir(exist_ok=True)
    directory = staging_parent / (case["case_id"] + "_" + uuid.uuid4().hex)
    directory.mkdir(exist_ok=False)
    c, h19 = ctx["core"], ctx["h19"]
    req = c.LayerAResilienceRequirements(float(case["alpha"]), int(case["beta_h"]), float(case["R_kwh_battery"]), float(case["P_out_kw_ac"]))
    held, events = {}, []
    initial_calls = guard.calls
    native_build = c.build_eob_model

    def close_model():
        guard.armed = None
        guard.after_optimize = None
        if "model" in held and not held.get("disposal_attempted"):
            held["disposal_attempted"] = True
            model = held["model"]
            try:
                model.dispose()
            finally:
                guard.used_models.discard(id(model))

    def build(inputs, settings, requirements):
        require(not held, "Duplicate construction", "BUILD_FAIL")
        model, handles = native_build(inputs, settings, requirements)
        held.update(model=model, handles=handles)
        audit = h19.audit_model(model, handles, req, inputs, c)
        require(audit["parameters"]["sha256"] == PARAM_SHA and
                audit["counts"] == ctx["parameters"]["structural_counts"], "Pre-optimize parameter/structure drift", "BUILD_FAIL")
        write(directory / "build_audit.json", audit)
        recheck(ctx)
        guard.armed = model
        return model, handles

    def after_optimize(model):
        stats = c._model_optimize_telemetry(model)
        stats.update(status=c._model_status_name(int(model.Status)), status_code=int(model.Status),
                     has_solution=int(model.SolCount)>0)
        for key, attribute in (("objective_ntd2023_per_year", "ObjVal"), ("best_bound", "ObjBound"),
                               ("mip_gap", "MIPGap"), ("node_count", "NodeCount"), ("runtime_sec_gurobi", "Runtime")):
            stats[key] = c._safe_gurobi_telemetry_attribute(model, attribute)
        held["solver"] = stats
        write(directory / "solver_outcome.json", stats)
        if stats["has_solution"]:
            variables = model.getVars()
            with (directory / "solver_primal.npz").open("xb") as f:
                np.savez_compressed(f, names=np.array(model.getAttr("VarName", variables)), values=np.array(model.getAttr("X", variables)))
        status = solver_acceptance(stats)
        require(status == "COMPLETE_SOLVER_PASS", "Solver outcome rejected before postprocessing", status)

    def telemetry(event):
        events.append(event)
        with (directory / "solver_telemetry.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(safe(event), allow_nan=False)+"\n")
            f.flush()

    settings = replace(ctx["settings"], telemetry_callback=telemetry)
    guard.after_optimize = after_optimize
    try:
        write(directory / "case_manifest.json", {"run_id": run_id, "case": case, "routing": ctx["routing"],
              "parameter_fingerprint": PARAM_SHA, "script_sha256": sha(SOURCE), "resume": False,
              "authority_rule": "Only cases/<CASE_ID>/ is authoritative; .staging/ is diagnostic only."})
        with patch.object(c, "build_eob_model", build):
            result = c.solve_eob(ctx["inputs"], settings, req)
        require(guard.calls-initial_calls == 1, "Optimization count mismatch", "BUILD_FAIL")
        handles = held["handles"]
        result["terminal_e_seg_kwh"] = [float(handles["e_seg"][8760, k].X) for k in range(3)]
        result["dispatch"]["u_mode"] = [float(handles["u_mode"][t].X) for t in range(8760)]
        result["best_bound"] = held["solver"]["best_bound"]
        for name, value in result.items():
            if isinstance(value, pd.DataFrame):
                csv(directory / f"{name}.csv", value)
        write(directory / "result.json", {k: v for k, v in result.items() if not isinstance(v, pd.DataFrame)})
        gates, evidence = postsolve(ctx, case, result, directory)
        comparison = representative_comparison(ctx, case, result)
        write(directory / "representative_comparison.json", comparison)
        require(comparison["status"] != "BLOCKER_REQUIRES_INVESTIGATION", "Representative result differs; investigation required", "REPRESENTATIVE_CONSISTENCY_FAIL")
        summary = case_summary(ctx, case, result, evidence, gates, run_id)
        write(directory / "case_summary.json", summary)
        recheck(ctx)
        guard.check()
        verify_registry(directory, registry(directory))
        close_model()  # Mandatory and fallible: always BEFORE any completion.
        held.clear()
        gc.collect()
        mandatory_cleanup(directory)
        finish_case(directory, run_id, case, summary, gates, guard.calls-initial_calls)
        publish_case(directory, final)
        return summary
    except BaseException as exc:
        # If the OS published the entire completed case, no later exception can
        # manufacture a competing case failure. The run may stop independently.
        if (final / "completion_manifest.json").is_file() and not directory.exists():
            warning_only(f"Case publication already committed: {case['case_id']}: {exc}")
            return summary
        cleanup_failure = None
        try:
            close_model()
        except BaseException as cleanup_error:
            cleanup_failure = {"type": type(cleanup_error).__name__, "reason": str(cleanup_error)}
        if not isinstance(exc, GateFailure):
            message = str(exc).lower()
            kind = ("TRANSITION_GATE_FAIL" if "transition" in message else "BILLING_GATE_FAIL" if "over-contract" in message or "demand" in message
                    else "DEGRADATION_GATE_FAIL" if "segment" in message else "COST_GATE_FAIL" if "cost" in message
                    else "PHYSICAL_GATE_FAIL" if "balance" in message else "BUILD_FAIL" if guard.calls == initial_calls else "PHYSICAL_GATE_FAIL")
            exc = GateFailure("INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else
                              "ARTIFACT_HASH_FAIL" if isinstance(exc, OSError) else kind, str(exc))
        if cleanup_failure:
            exc.evidence = {"original_evidence": exc.evidence, "additional_cleanup_failure": cleanup_failure}
        failures = final.parent / ".failures" / case["case_id"]
        failures.mkdir(parents=True, exist_ok=False)
        failure_evidence(failures, exc, case["case_id"], calls=guard.calls-initial_calls)
        raise exc
    finally:
        guard.armed = None
        guard.after_optimize = None
        held.clear()


def surface_audit(ctx, directory, summaries):
    expected = ctx["matrix"]
    require(not (Path(directory) / "cases" / ".failures").exists(), "Surface contains failed cases", "SURFACE_GATE_FAIL")
    staging = Path(directory) / "cases" / ".staging"
    require(not staging.exists() or not any(staging.iterdir()), "Surface contains unpublished cases", "SURFACE_GATE_FAIL")
    require(len(summaries) == 81 and len({s["case_id"] for s in summaries}) == 81 and
            {s["case_id"] for s in summaries} == set(expected.case_id), "Incomplete surface", "SURFACE_GATE_FAIL")
    require(len({(s["alpha"], s["beta_h"]) for s in summaries}) == 81, "Duplicate coordinates", "SURFACE_GATE_FAIL")
    for s in summaries:
        source_case = expected.loc[expected.case_id.eq(s["case_id"])].iloc[0].to_dict()
        require(all(s[key] == source_case[key] for key in source_case),
                "Surface row does not match frozen case definition", "SURFACE_GATE_FAIL")
        require(s["status"] == "COMPLETE_PASS" and s["run_id"] == directory.name, "Unaccepted case", "SURFACE_GATE_FAIL")
        p = directory / "cases" / s["case_id"]
        completion = read(p / "completion_manifest.json")
        verify_registry(p, completion["artifact_registry"])
        require(read(p / "case_summary.json") == safe(s), "In-memory/persisted summary mismatch", "ARTIFACT_HASH_FAIL")
        require(completion["status"] == "COMPLETE_PASS" and completion["run_id"] == directory.name
                and completion["case_id"] == s["case_id"] and completion["optimization_calls"] == 1,
                "Case completion identity mismatch", "SURFACE_GATE_FAIL")
        require(completion["alpha"] == s["alpha"] and completion["beta_h"] == s["beta_h"]
                and completion["parameter_fingerprint"] == PARAM_SHA
                and completion["routing_fingerprint"] == digest(ctx["routing"])
                and completion["eob_sha256"] == s["eob_sha256"], "Case completion configuration mismatch", "SURFACE_GATE_FAIL")
        require(set(completion["gates"]) == set(MANDATORY) and all(v == "PASS" for v in completion["gates"].values()), "Incomplete gates", "SURFACE_GATE_FAIL")
        require(s["E_N_kwh"] + 1e-6 >= s["analytical_E_N_min_kwh"] and s["P_B_kw_ac"]+1e-6 >= s["P_out_kw_ac"], "Sizing lower bound", "SURFACE_GATE_FAIL")
        require(s["parameter_fingerprint"] == PARAM_SHA and s["routing_fingerprint"] == digest(ctx["routing"])
                and s["eob_sha256"] == ctx["eob_identity"]["result"]["sha256"] and s["currency"] == "constant NTD-2023", "Surface identity drift", "SURFACE_GATE_FAIL")
        require(abs(s["absolute_premium_ntd2023"]-(s["annual_objective_ntd2023"]-ctx["eob"]["objective_ntd2023_per_year"])) <= .001, "Premium drift", "SURFACE_GATE_FAIL")
        require(abs(s["relative_premium_pct"]-100*s["absolute_premium_ntd2023"]/ctx["eob"]["objective_ntd2023_per_year"]) <= 1e-9,
                "Relative premium drift", "SURFACE_GATE_FAIL")
    frame = pd.DataFrame(summaries)
    _, _, analytical = ctx["h16"].analytical_surface(ctx["inputs"].annual, eta_d=.9, soc_min=.1, soc_max=.9)
    require(analytical["status"] == "PASS", "Surface analytical consistency", "SURFACE_GATE_FAIL")
    # Preserve neighbor changes for academic review; do not impose monotone optima.
    neighbors = []
    for axis, fixed in (("alpha", "beta_h"), ("beta_h", "alpha")):
        for fixed_value, group in frame.groupby(fixed):
            rows = group.sort_values(axis).to_dict("records")
            for previous, current in zip(rows, rows[1:]):
                neighbors.append({"from": previous["case_id"], "to": current["case_id"], "axis": axis,
                    "academic_review": True, **{f"delta_{k}": current[k]-previous[k] for k in ("E_N_kwh", "P_B_kw_ac", "CC_regular_kw", "annual_objective_ntd2023")}})
    csv(directory / "neighbor_changes_for_academic_review.csv", pd.DataFrame(neighbors))
    return {"status": "PASS", "accepted_cases": 81, "missing": 0, "duplicates": 0, "failed": 0,
            "unattempted": 0, "analytical": analytical, "neighbor_changes_flagged_for_review": len(neighbors),
            "monotone_optimal_design_or_cost_required": False}


def production(ctx, guard):
    require(guard.execute, "Explicit --execute-production required", "EXECUTION_DISABLED")
    require(ctx["execute"] and ctx["authority"]["deployment_status"] == "PRODUCTION_AUTHORITY_FROZEN",
            "Committed/tagged production authority required", "PRODUCTION_AUTHORITY_NOT_YET_FROZEN")
    directory = new_directory(PRODUCTION_ROOT)
    statuses = {case_id: "NOT_RUN" for case_id in ctx["matrix"].case_id}
    summaries, current = [], None
    try:
        write(directory / "run_manifest.json", {"run_id": directory.name, "script_version": SCRIPT_VERSION,
              "script_sha256": sha(SOURCE), "mode": "PRODUCTION", "restart_policy": "FRESH_RUN_ONLY",
              "authority": ctx["authority"], "case_states_initial": statuses, "execution_flag": True,
              "terminal_authority": {"case_success": "cases/<ID>/completion_manifest.json",
                "case_failure": "cases/.failures/<ID>/failure_manifest.json", "staging": "NON_AUTHORITATIVE",
                "run": "exactly one of completion_manifest.json or failure_manifest.json"}})
        write(directory / "pre_solve_gate.json", ctx["authority"])
        csv(directory / "case_matrix.csv", ctx["matrix"])
        (directory / "cases").mkdir()
        for case in ctx["matrix"].to_dict("records"):
            current = case["case_id"]
            statuses[current] = "IN_PROGRESS"
            target = directory / "cases" / current
            summaries.append(execute_case(ctx, guard, case, target, directory.name))
            statuses[current] = "COMPLETE_PASS"
            try:
                print(f"{current}: COMPLETE_PASS ({len(summaries)}/81)", flush=True)
            except BaseException as output_error:
                warning_only(f"Optional progress output unavailable: {output_error}")
        audit = surface_audit(ctx, directory, summaries)
        write(directory / "surface_validation_audit.json", audit)
        write(directory / "surface_summary.json", summaries)
        flat = [{k: json.dumps(safe(v), sort_keys=True) if isinstance(v, dict) else v for k, v in s.items()} for s in summaries]
        csv(directory / "surface_summary.csv", pd.DataFrame(flat))
        write(directory / "case_states.json", statuses)
        recheck(ctx)
        guard.check()
        require(guard.calls == 81 and all(s == "COMPLETE_PASS" for s in statuses.values()), "Surface count mismatch", "SURFACE_GATE_FAIL")
        publish_completion(directory, {"status": "COMPLETE_PASS", "run_id": directory.name, "script_version": SCRIPT_VERSION,
                                       "cases": 81, "optimization_calls": guard.calls, "surface_solved": True})
        return directory
    except BaseException as exc:
        if (directory / "completion_manifest.json").is_file():
            warning_only(f"Run publication already committed: {exc}")
            return directory
        if current is not None and statuses[current] == "IN_PROGRESS":
            # A committed case never becomes failed because its caller was
            # interrupted before updating the in-memory progress dictionary.
            published = directory / "cases" / current / "completion_manifest.json"
            statuses[current] = "COMPLETE_PASS" if published.is_file() else getattr(exc, "status", "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "BUILD_FAIL")
        failure_evidence(directory, exc, current, statuses, guard.calls)
        raise


def must_fail(name, function, expected_status=None):
    try:
        function()
    except (GateFailure, FileExistsError) as exc:
        if expected_status is not None:
            require(getattr(exc, "status", None) == expected_status, f"Wrong negative-test classification: {name}: {exc}")
        return {"test": name, "status": "PASS", "observed": getattr(exc, "status", type(exc).__name__)}
    raise RuntimeError(f"Negative test did not reject: {name}")


def adapter_tests(ctx, audit_dir, guard):
    tests, historical = [], []
    # All 81 definitions exercised using analytical boundary sizing, explicitly fixtures.
    for case in ctx["matrix"].to_dict("records"):
        sizing = {"E_N_kwh": case["analytical_E_N_min_kwh"], "P_B_kw_ac": case["P_out_kw_ac"]}
        report, _ = all_start_audit(ctx, case, sizing)
        require(report["status"] == "PASS", "Boundary fixture failed")
    tests.append({"test": "all_81_analytical_boundary_fixtures", "status": "PASS", "count": 81, "solved": False})
    center = ctx["matrix"].loc[ctx["matrix"].case_id.eq("a0.80_b08")].iloc[0].to_dict()
    sizing = {"E_N_kwh": center["analytical_E_N_min_kwh"], "P_B_kw_ac": center["P_out_kw_ac"]}
    for key in sizing:
        bad = dict(sizing)
        bad[key] -= 1
        tests.append(must_fail(f"undersized_{key}", lambda bad=bad: all_start_audit(ctx, center, bad), "RESILIENCE_GATE_FAIL"))
    bad_ctx = dict(ctx, starts=ctx["starts"].copy())
    bad_ctx["starts"].loc[bad_ctx["starts"].beta_hours.eq(8).idxmax(), "start_index"] = 8759
    tests.append(must_fail("circular_wrap_index", lambda: all_start_audit(bad_ctx, center, sizing), "RESILIENCE_GATE_FAIL"))
    bad_case = dict(center, binding_start_index=int(center["binding_start_index"])+1)
    tests.append(must_fail("binding_window_substitution", lambda: all_start_audit(ctx, bad_case, sizing), "RESILIENCE_GATE_FAIL"))
    tests.append(must_fail("default_execution_disabled", lambda: guard.permit(object()), "EXECUTION_DISABLED"))
    require(parse_args([]).execute_production is False and parse_args(["--execute-production"]).execute_production is True,
            "CLI opt-in boundary failed")
    tests.append({"test": "cli_default_and_explicit_opt_in", "status": "PASS"})
    permission_fixture = ExecutionGuard(True)  # Predicate tests only: never enter or invoke any optimizer.
    token = object()
    tests.append(must_fail("unarmed_model_rejected", lambda: permission_fixture.permit(token), "EXECUTION_DISABLED"))
    permission_fixture.armed = token
    permission_fixture.permit(token)
    permission_fixture.used_models.add(id(token))
    tests.append(must_fail("second_optimization_permission_rejected", lambda: permission_fixture.permit(token), "EXECUTION_DISABLED"))
    for field, value in (("TimeLimit", 900), ("MIPGap", 1e-4), ("NumericFocus", 2), ("MIPFocus", 1), ("Threads", 4)):
        parameters = dict(ctx["parameters"]["parameters"], **{field: value})
        require(digest(parameters) != PARAM_SHA, f"Parameter mutation undetected: {field}")
        tests.append({"test": f"parameter_drift_{field}", "status": "PASS"})
    fixtures = [({}, "SOLVER_NO_SOLUTION"), ({"has_solution": True, "status": "TIME_LIMIT"}, "NON_OPTIMAL"),
                ({"has_solution": True, "status": "OPTIMAL", "status_code": 2, "mip_gap": .00001}, "MIP_GAP_FAIL")]
    for value, expected in fixtures:
        require(solver_acceptance(value) == expected, "Solver classifier failed")
        tests.append({"test": expected, "status": "PASS"})
    stored_results = {}
    for reference in ctx["cross"]["representative_reconciliation"]:
        cid = reference["case_id"]
        p = ROOT / reference["path"]
        verify_hash(p, reference["sha256"])
        wrapper = read(p)
        result = copy.deepcopy(wrapper["result"])
        input_files = {}
        for key, suffix in (("dispatch", "dispatch"), ("billing_exact", "billing_exact"), ("transition_settlement_detail", "transition_detail")):
            file = p.parent / f"{cid}_{suffix}_v7_2.csv"
            input_files[file.relative_to(ROOT).as_posix()] = sha(file)
            ctx["identities"].setdefault(file.relative_to(ROOT).as_posix(), sha(file))
            result[key] = pd.read_csv(file, float_precision="round_trip")
        case = ctx["matrix"].loc[ctx["matrix"].case_id.eq(cid)].iloc[0].to_dict()
        gates, evidence = postsolve(ctx, case, result)
        require(representative_comparison(ctx, case, result)["status"] == "PASS", "Self-comparison failed")
        stored_results[cid] = result
        historical.append({"case_id": cid, "classification": "STORED_REPRESENTATIVE_VALIDATION_ONLY",
                           "source": reference, "dispatch_file_hashes_observed_now": input_files,
                           "gates": gates, "resilience": evidence["resilience"], "rainflow": evidence["rainflow"]["summary"]})
    result = stored_results["a0.80_b08"]
    bad = copy.deepcopy(result)
    bad["dispatch"].loc[0, "e_physical_kwh"] += 100
    tests.append(must_fail("corrupted_physical_state", lambda: physical_audit(ctx, center, bad), "PHYSICAL_GATE_FAIL"))
    bad = copy.deepcopy(result)
    bad["billing_exact"].loc[0, "exact_billing_demand_kw"] += 1
    tests.append(must_fail("corrupted_demand_maximum", lambda: billing_audit(ctx, bad), "BILLING_GATE_FAIL"))
    bad = copy.deepcopy(result)
    bad["transition_settlement"]["postsolve_invariants_pass"] = False
    tests.append(must_fail("failed_transition_certificate", lambda: transition_audit(ctx, bad), "TRANSITION_GATE_FAIL"))
    bad = copy.deepcopy(result)
    bad["cost_components_ntd2023_per_year"]["energy"] += 1
    tests.append(must_fail("corrupted_cost", lambda: cost_degradation_audit(ctx, bad), "COST_GATE_FAIL"))
    bad = copy.deepcopy(result)
    bad["dispatch"].loc[0, "p_discharge_seg_1_kw_ac"] += 10
    tests.append(must_fail("corrupted_segment_throughput", lambda: cost_degradation_audit(ctx, bad), "DEGRADATION_GATE_FAIL"))
    bad = copy.deepcopy(result)
    bad["annual_energy"]["grid_import_kwh"] += 10
    tests.append(must_fail("corrupted_annual_energy_total", lambda: physical_audit(ctx, center, bad), "PHYSICAL_GATE_FAIL"))
    # Inject only the validator return value. Production and test both consume the
    # same required gate result; no new rainflow algorithm or optimized solution.
    with patch.object(ctx["h16"], "validate_representative_rainflow",
                      return_value={"summary": {"verdict": "REVIEW"}, "gates": {"required": "FAIL"}}):
        tests.append(must_fail("failed_rainflow_not_promoted", lambda: postsolve(ctx, center, result), "RAINFLOW_GATE_FAIL"))
    with patch.object(ctx["h16"], "validate_representative_rainflow", side_effect=ValueError("TEST_ONLY malformed validator input")):
        tests.append(must_fail("rainflow_exception_classification", lambda: postsolve(ctx, center, result), "RAINFLOW_GATE_FAIL"))
    changed = copy.deepcopy(result)
    changed["sizing"]["E_N_kwh"] += 100
    require(representative_comparison(ctx, center, changed)["status"] == "BLOCKER_REQUIRES_INVESTIGATION",
            "Unexplained representative change accepted")
    tests.append({"test": "representative_difference_blocks", "status": "PASS"})
    fixture = audit_dir / "lifecycle_fixture"
    fixture.mkdir()
    write(fixture / "evidence.json", {"classification": "TEST_ONLY", "solved": False})
    entries = registry(fixture)
    verify_registry(fixture, entries)
    wrong = copy.deepcopy(entries)
    wrong["evidence.json"]["sha256"] = "0"*64
    tests.append(must_fail("corrupted_artifact_hash", lambda: verify_registry(fixture, wrong), "ARTIFACT_HASH_FAIL"))
    tests.append(must_fail("exclusive_no_overwrite", lambda: write(fixture / "evidence.json", {})))
    tests.append(must_fail("missing_case_gate_no_completion", lambda: finish_case(fixture, "fixture", center, {}, {}, 0), "PHYSICAL_GATE_FAIL"))
    for name in MANDATORY:
        failed_gates = {key: "PASS" for key in MANDATORY}
        failed_gates[name] = "FAIL"
        tests.append(must_fail(f"failed_{name}_blocks_completion", lambda g=failed_gates: finish_case(fixture, "fixture", center, {}, g, 1), "PHYSICAL_GATE_FAIL"))
    summary_fixture = {"run_id": "fixture", "case_id": center["case_id"], "status": "COMPLETE_PASS"}
    tests.append(must_fail("pass_labels_without_evidence_rejected", lambda: finish_case(fixture, "fixture", center,
                          summary_fixture, {key: "PASS" for key in MANDATORY}, 1), "ARTIFACT_HASH_FAIL"))
    tests.append(must_fail("partial_surface_rejected", lambda: surface_audit(ctx, fixture, []), "SURFACE_GATE_FAIL"))
    states = {cid: "NOT_RUN" for cid in ctx["matrix"].case_id}
    states[center["case_id"]] = "RESILIENCE_GATE_FAIL"
    failure_evidence(fixture, GateFailure("RESILIENCE_GATE_FAIL", "TEST_ONLY injected failure"), center["case_id"], states, 0)
    failure = read(fixture / "failure_manifest.json")
    require(len(failure["case_states"]) == 81 and list(failure["case_states"].values()).count("NOT_RUN") == 80,
            "Unattempted cases lost from failure evidence")
    tests.append(must_fail("failed_directory_cannot_complete", lambda: publish_completion(fixture, {"status": "TEST_ONLY"}), "ARTIFACT_HASH_FAIL"))
    require(not (fixture / "completion_manifest.json").exists(), "Fixture falsely completed")
    require(guard.calls == 0 and not guard.forbidden_attempts, "Non-solving audit invoked solver")
    return {"status": "PASS", "tests": tests, "historical_validation": historical,
            "gurobi_models_constructed": 0, "optimization_calls": 0,
            "production_optimize_hook_executed": False,
            "historical_cases_counted_as_production": 0, "all_start_81_boundary_fixtures_solved": False}


def static_audit():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    calls = [(n.lineno, n.func.attr) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr in ("optimize", "optimizeAsync", "optimizeBatch", "tune", "solve_eob")]
    require(len(calls) == 1 and calls[0][1] == "solve_eob", "Unexpected solver call site")
    require(not git("diff", "--name-only"), "Protected tracked sources changed")
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    return {"status": "PASS", "ast_syntax": "PASS", "import_without_main": "PASS",
            "solver_call_sites": calls, "solve_call_control": "execute_case -> guard permit; production() checks explicit flag",
            "default": "audit only; Model construction blocked", "core_equations_duplicated": False,
            "postsolve_state_equations": "diagnostic reconstruction only", "git_diff_check": "PASS",
            "protected_tracked_changes": [], "known_boundary": "Production requires frozen ancestor, committed runner/manifest bytes and annotated production tag at current HEAD; default audit may remain not-yet-frozen."}


def audit_only(ctx, guard):
    require(not guard.execute, "Audit cannot enable production")
    before = registry(PRODUCTION_ROOT) if PRODUCTION_ROOT.exists() else {}
    directory = new_directory(AUDIT_ROOT)
    try:
        write(directory / "run_manifest.json", {"run_id": directory.name, "script_version": SCRIPT_VERSION,
              "script_sha256": sha(SOURCE), "mode": "NON_SOLVING_IMPLEMENTATION_AUDIT", "production_solved": False,
              "deployment_status": ctx["authority"]["deployment_status"]})
        write(directory / "authority_gate.json", ctx["authority"])
        routing = {"status": "PASS", "case_count": 81, "case_definitions": ctx["matrix"].to_dict("records"),
                   "parameter_fingerprint": PARAM_SHA, "future_paths": [f"results/layer_a/final_81/runs/<RUN_ID>/cases/{cid}/" for cid in ctx["matrix"].case_id]}
        write(directory / "grid_routing_audit.json", routing)
        adapters = adapter_tests(ctx, directory, guard)
        write(directory / "postsolve_adapter_audit.json", adapters)
        write(directory / "execution_guard_audit.json", {"status": "PASS", "default_solve_disabled": True,
              "explicit_flag_required": "--execute-production", "optimization_calls": guard.calls,
              "guard_methods": list(guard.methods), "model_construction_blocked": True, "production_results_created": 0})
        write(directory / "artifact_lifecycle_audit.json", {"status": "PASS", "atomic_exclusive_completion": True,
              "case_completion_last": True, "run_completion_last": True, "production_completion_written": False,
              "audit_completion_meaning": "SCRIPT_19B_IMPLEMENTATION_READY", "restart_policy": "FRESH_RUN_ONLY",
              "failure_and_hash_tests": [t for t in adapters["tests"] if any(s in t["test"] for s in ("artifact", "completion", "overwrite", "surface", "directory"))]})
        write(directory / "failure_semantics_audit.json", {"status": "PASS", "failure_states": FAILURE_STATES,
              "solver_pass_state": "COMPLETE_SOLVER_PASS", "case_pass_state": "COMPLETE_PASS",
              "fail_first": True, "remaining_cases": "NOT_RUN", "required_surface_count": 81,
              "representative_policy": "No replay of old solutions as production; new solve compared by method, objective gap interval and numerical sizing tolerance; unexplained change blocks for review."})
        write(directory / "runner_static_audit.json", static_audit())
        recheck(ctx)
        after = registry(PRODUCTION_ROOT) if PRODUCTION_ROOT.exists() else {}
        require(before == after, "Production artifacts changed in audit mode")
        guard.check()
        publish_completion(directory, {"status": "SCRIPT_19B_IMPLEMENTATION_READY", "run_id": directory.name,
              "script_version": SCRIPT_VERSION, "script_sha256": sha(SOURCE), "verdict": PASS_VERDICT,
              "deployment_status": ctx["authority"]["deployment_status"],
              "optimization_calls": guard.calls, "production_surface_solved": False, "production_cases_completed": 0})
        return directory
    except BaseException as exc:
        failure_evidence(directory, exc, calls=guard.calls)
        raise


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-production", action="store_true", help="Explicitly authorize a fresh 81-case production invocation.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    sys.path.insert(0, str(ROOT))
    target = None
    try:
        with ExecutionGuard(args.execute_production) as guard:
            ctx = authority_gate(guard)
            target = production(ctx, guard) if args.execute_production else audit_only(ctx, guard)
            print(json.dumps({"directory": str(target), "optimization_calls": guard.calls,
                              "completion_sha256": sha(target / "completion_manifest.json")}, indent=2))
        return 0
    except BaseException as exc:
        if target is not None and (target / "completion_manifest.json").is_file():
            warning_only(f"Completed invocation retained despite optional reporting/guard-exit error: {exc}")
            return 0
        print(json.dumps({"status": getattr(exc, "status", "IMPLEMENTATION_AUDIT_FAIL"), "reason": str(exc),
                          "traceback": traceback.format_exc()}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
