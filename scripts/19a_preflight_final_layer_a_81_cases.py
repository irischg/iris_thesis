#!/usr/bin/env python3
"""Frozen v7.2 final Layer-A grid: provenance, routing, BUILD/AUDIT/DISPOSE only.

No solving mode, case overrides, input overrides, resume or production writes.
The accepted Script-09 and Script-16a callables supply all requirements.
Process-wide Gurobi guards remain installed through validation and completion.
"""
from __future__ import annotations

import ast
from collections import Counter
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from dataclasses import asdict
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import runpy
import subprocess
import sys
import time
import traceback
from unittest.mock import patch
import uuid

import numpy as np
import pandas as pd
import gurobipy as gp

SCRIPT_VERSION = "v7.2-final-layer-a-81-preproduction-2026-09-09-r1"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve().relative_to(ROOT).as_posix()
CHECKPOINT = "docs/checkpoints/production_checkpoint_manifest_v7_2_post17c_2026-09-09.json"
CHECKPOINT_SHA = "9ad301e891bb8e794b11a6f8ebac632d96cf59fecf38d402f72bd9b0bdd32921"
HEAD = "b09f078c4ad8f2323af7135e2ade82f59f167f5e"
TAG_OBJECT = "1aa834bef65328651add441d1b5c076a3c6ae183"
CANONICAL = "data/processed/annual_input_v7_1.parquet"
CANONICAL_SHA = "e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e"
CORE = "src/annual_design_model_v7_2.py"
CORE_SHA = "d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0"
CORE_VERSION = "v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9"
ALPHAS = (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00)
BETAS = tuple(range(4, 13))
MIP_GAP = 1e-6
TOL = 1e-6
PASS_VERDICT = "FINAL 81 PRE-PRODUCTION GATE PASS — 81/81 CASES READY FOR CONTROLLED PRODUCTION SOLVE"
FAIL_VERDICT = "FINAL 81 PRE-PRODUCTION GATE FAIL — CORRECTION REQUIRED"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe(value):
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return safe(value.tolist())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def digest(value):
    return hashlib.sha256(json.dumps(safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, payload):
    # Exclusive creation; no overwrite of prior evidence, including completion.
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(safe(payload), handle, indent=2, allow_nan=False)
        handle.write("\n")


def controlled(path):
    resolved = (ROOT / path).resolve()
    require(resolved.is_relative_to(ROOT), f"Path escapes repository: {path}")
    return resolved


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.rstrip("\r\n")


def repository_gate():
    status = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    allowed = {"?? docs/protocols/iris_thesis_rigorous_audit_skill.md", f"?? {SCRIPT_PATH}"}
    local = {
        "branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
        "origin": git("rev-parse", "origin/thesis-v7"),
        "tag_type": git("cat-file", "-t", "v7.2-post17c"),
        "tag_object": git("rev-parse", "v7.2-post17c"),
        "tag_peeled": git("rev-parse", "v7.2-post17c^{}"),
        "working_tree": status, "staged": git("diff", "--cached", "--name-status"),
    }
    require(local["branch"] == "thesis-v7" and local["head"] == local["origin"] == local["tag_peeled"] == HEAD,
            "FINAL 81 PRE-PRODUCTION BLOCKED — REPOSITORY LINEAGE MISMATCH")
    require(local["tag_type"] == "tag" and local["tag_object"] == TAG_OBJECT and not local["staged"] and set(status) <= allowed,
            "FINAL 81 PRE-PRODUCTION BLOCKED — REPOSITORY LINEAGE MISMATCH")
    refs = dict(line.split()[::-1] for line in git("ls-remote", "--heads", "--tags", "origin",
                "refs/heads/thesis-v7", "refs/tags/v7.2-post17c", "refs/tags/v7.2-post17c^{}").splitlines())
    require(refs == {"refs/heads/thesis-v7": HEAD, "refs/tags/v7.2-post17c": TAG_OBJECT,
                     "refs/tags/v7.2-post17c^{}": HEAD}, "Live remote checkpoint mismatch")
    return {"status": "PASS", "local": local, "live_remote": refs, "verified_utc": now()}


def verify_identity(path, expected, identities):
    p = controlled(path)
    relative = p.relative_to(ROOT).as_posix()
    require(p.is_file(), f"Missing immutable artifact: {relative}")
    actual = sha(p)
    require(actual == expected, f"Immutable hash mismatch: {relative}: {actual} != {expected}")
    require(relative not in identities or identities[relative] == actual, f"Conflicting authority: {relative}")
    identities[relative] = actual


def identity_pairs(node):
    if isinstance(node, dict):
        if isinstance(node.get("path"), str) and isinstance(node.get("sha256"), str):
            yield node["path"], node["sha256"]
        for key, value in node.items():
            if key.endswith("_path") and key[:-5] + "_sha256" in node:
                yield value, node[key[:-5] + "_sha256"]
            yield from identity_pairs(value)
    elif isinstance(node, list):
        for value in node:
            yield from identity_pairs(value)


def lineage_gate():
    identities = {}
    verify_identity(CHECKPOINT, CHECKPOINT_SHA, identities)
    checkpoint = read(ROOT / CHECKPOINT)
    require(checkpoint["checkpoint_role"] == "POST_17C_PRE_FINAL_81_LAYER_A_FREEZE"
            and checkpoint["status"] == "FROZEN_POST_17C_PRE_FINAL_81", "Checkpoint role/status mismatch")
    require(checkpoint["experimental_closure"]["WINTER_PV_P1"] == "CLOSED"
            and checkpoint["experimental_closure"]["FINAL_81_LAYER_A"] == "NOT_YET_RUN", "Pipeline boundary mismatch")
    for path, expected in identity_pairs(checkpoint):
        verify_identity(path, expected, identities)
    prior = read(ROOT / checkpoint["prior_checkpoints"]["production_checkpoint"]["path"])
    for path, expected in identity_pairs(prior):
        verify_identity(path, expected, identities)
    run17 = checkpoint["accepted_script_17c_lineage"]
    completion = read(ROOT / run17["completion_manifest"]["path"])
    require(completion["status"] == "PASS" and completion["run_id"] == run17["run_id"], "17C status/ID mismatch")
    require(len(completion["artifact_registry"]) == 30, "17C registry cardinality mismatch")
    for name, item in completion["artifact_registry"].items():
        require(controlled(item["path"]) == controlled(run17["run_directory"]) / name, "17C path substitution")
        verify_identity(item["path"], item["sha256"], identities)
    # 17C pre-solve registry also freezes comparator dispatch and validation inputs.
    pre17 = read(ROOT / run17["pre_solve_gate"]["path"])
    for item in pre17["frozen_hashes"].values():
        verify_identity(item["path"], item["expected_sha256"], identities)
    verify_identity(CANONICAL, CANONICAL_SHA, identities)
    verify_identity(CORE, CORE_SHA, identities)
    return checkpoint, prior, identities


def load_module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class NoOptimization:
    def __init__(self):
        self.calls = []
        self.stack = ExitStack()
        self.guards = {}

    def __enter__(self):
        for name in ("optimize", "optimizeAsync", "optimizeBatch", "tune"):
            if not hasattr(gp.Model, name):
                continue
            def reject(*args, _name=name, **kwargs):
                self.calls.append({"method": _name, "utc": now()})
                raise RuntimeError(f"ABSOLUTE SOLVE PROHIBITION: Model.{_name}")
            self.guards[name] = reject
            self.stack.enter_context(patch.object(gp.Model, name, reject))
        self.check()
        return self

    def check(self):
        require(all(getattr(gp.Model, key) is value for key, value in self.guards.items()), "Solve guard displaced")
        require(not self.calls, f"Forbidden optimization/tuning attempt: {self.calls}")

    def __exit__(self, *args):
        return self.stack.__exit__(*args)


def existing_validator(script):
    # Run the unmodified main in this guarded process; there is no solver subprocess.
    stdout, stderr = io.StringIO(), io.StringIO()
    code = 0
    with patch.object(sys, "argv", [str(ROOT / script)]), redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            runpy.run_path(str(ROOT / script), run_name="__main__")
        except SystemExit as exc:
            code = exc.code or 0
    require(code == 0, f"{script} failed: {stderr.getvalue()} {stdout.getvalue()}")
    payload = json.loads(stdout.getvalue())
    require(payload["status"] == "PASS", f"{script} non-PASS")
    return {"script": script, "result": payload, "stderr": stderr.getvalue(), "execution": "GUARDED_IN_PROCESS_MAIN"}


def snapshot_sources(identities):
    for relative in git("ls-files").splitlines():
        identities.setdefault(relative, sha(ROOT / relative))
    identities[SCRIPT_PATH] = sha(ROOT / SCRIPT_PATH)
    unrelated = "docs/protocols/iris_thesis_rigorous_audit_skill.md"
    if (ROOT / unrelated).exists():
        identities[unrelated] = sha(ROOT / unrelated)


def requirements_gate(inputs, helper, indexer, checkpoint, prior, identities):
    require(tuple(helper.ALPHAS) == ALPHAS and tuple(helper.BETAS_H) == BETAS, "Accepted grid convention differs")
    canonical = indexer.validate_annual_input(inputs.annual)
    pd.testing.assert_series_equal(canonical.timestamp, inputs.annual.timestamp, check_names=False)
    surface, starts, audit = helper.analytical_surface(
        inputs.annual, eta_d=0.9, soc_min=0.1, soc_max=0.9)
    require(audit["status"] == "PASS", f"Analytical audit failed: {audit}")
    expected = {(a, b) for a in ALPHAS for b in BETAS}
    actual = {(float(r.alpha), int(r.beta_h)) for r in surface.itertuples()}
    require(len(surface) == len(actual) == surface.case_id.nunique() == 81 and actual == expected, "Grid mismatch")
    require(all(r.case_id == f"a{r.alpha:.2f}_b{int(r.beta_h):02d}" for r in surface.itertuples()), "Case ID mismatch")
    require(surface.groupby("alpha").P_out_kw_ac.nunique().eq(1).all(), "Pout varies across beta")
    stored_path = "data/processed/valid_outage_starts_v7_1.parquet"
    stored = pd.read_parquet(ROOT / stored_path)
    identities[stored_path] = sha(ROOT / stored_path)
    count_path = "results/data_audit/valid_outage_start_counts_v7_1.csv"
    stored_counts = pd.read_csv(ROOT / count_path)
    identities[count_path] = sha(ROOT / count_path)
    index_records = []
    all_frames = []
    for beta in BETAS:
        frame = indexer.build_valid_start_rows(canonical.timestamp, beta)
        report = indexer.audit_one_beta(frame, beta)
        reference = stored.loc[stored.beta_hours.eq(beta)].reset_index(drop=True)
        pd.testing.assert_frame_equal(frame, reference, check_dtype=False)
        accepted_count = stored_counts.loc[stored_counts.beta_hours.eq(beta), "valid_start_count"]
        require(len(accepted_count) == 1 and int(accepted_count.iloc[0]) == len(frame) == 8760 - beta + 1,
                f"Script-09 valid-start authority mismatch beta={beta}")
        require(surface.loc[surface.beta_h.eq(beta), "valid_start_count"].eq(len(frame)).all(), "Case start counts differ")
        index_records.append({**report, "exact_existing_start_set_match": True})
        all_frames.append(frame)
    require(len(stored) == sum(len(f) for f in all_frames) == 78777, "Extra/missing stored starts")
    representatives = prior["current_representative_validation"]
    accepted_run = read(ROOT / representatives["run_manifest"]["path"])
    require({r["case_id"] for r in accepted_run["selected_cases"]} == set(representatives["expected_case_ids"]), "Representative ID mismatch")
    reconciliation = []
    numeric = ("alpha", "beta_h", "P_out_kw_ac", "R_kwh_battery", "analytical_E_N_min_kwh", "valid_start_count", "binding_start_index")
    for selected in accepted_run["selected_cases"]:
        case_id = selected["case_id"]
        path = Path(representatives["run_manifest"]["path"]).parent / "representative_cases" / case_id / f"{case_id}_result_v7_2.json"
        record = read(ROOT / path)
        require(record["run_id"] == representatives["run_id"] and record["case_id"] == case_id, "Representative routing mismatch")
        require(record["gates"] and all(v == "PASS" for v in record["gates"].values()), "Representative gates failed")
        previous = record["analytical_requirement"]
        current = surface.loc[surface.case_id.eq(case_id)].iloc[0].to_dict()
        deltas = {key: float(current[key]) - float(previous[key]) for key in numeric}
        require(all(abs(v) <= TOL for v in deltas.values()), f"Representative requirements differ: {case_id}: {deltas}")
        for key in ("binding_historical_start", "binding_historical_end_inclusive", "binding_historical_end_exclusive"):
            require(pd.Timestamp(current[key]) == pd.Timestamp(previous[key]), f"Representative binding window differs: {case_id}")
        identities[path.as_posix()] = sha(ROOT / path)
        reconciliation.append({"case_id": case_id, "path": path.as_posix(), "sha256": identities[path.as_posix()], "numeric_deltas": deltas, "binding_window_match": True, "status": "PASS"})
    surface["canonical_input_path"] = CANONICAL
    surface["canonical_input_sha256"] = CANONICAL_SHA
    surface["core_path"] = CORE
    surface["core_sha256"] = CORE_SHA
    audit.update({"generated_count": len(surface), "unique_ids": int(surface.case_id.nunique()),
                  "duplicate_count": 0, "missing_pairs": [], "extra_pairs": [],
                  "pout_constant_across_beta": "PASS", "script09_start_sets": index_records,
                  "representative_reconciliation": reconciliation, "numerical_tolerance": TOL})
    return surface, audit, pd.concat(all_frames, ignore_index=True)


def parameter_audit(model):
    values, changes, exclusions = {}, {}, []
    # License/server credentials are neither model parameters nor reportable evidence.
    environment_prefixes = ("CS", "WLS", "Cloud", "Server", "Token", "Compute", "Worker", "Job", "License", "Username")
    for name in sorted(n for n in dir(gp.GRB.Param) if not n.startswith("_")):
        if name.lower().startswith(tuple(prefix.lower() for prefix in environment_prefixes)):
            exclusions.append(name)
            continue
        info = model.getParamInfo(name)
        require(info is not None, f"Unknown solver parameter: {name}")
        _, kind, current, _, _, default = info
        values[name] = safe(current)
        if current != default:
            changes[name] = {"current": safe(current), "gurobi_default": safe(default)}
    require(set(changes) <= {"MIPGap", "NumericFocus", "OutputFlag"}, f"Hidden solver tuning: {changes}")
    require(model.Params.MIPGap == MIP_GAP and model.Params.NumericFocus == 1 and model.Params.OutputFlag == 0,
            "Production parameter mismatch")
    require(math.isinf(model.Params.TimeLimit) and model.Params.MIPFocus == 0 and model.Params.Threads == 0,
            "TimeLimit/MIPFocus/thread drift")
    require(model.Params.LogFile == "" and model.Params.ResultFile == "", "External solver output routing")
    return {"parameters": values, "nondefault_parameters": changes,
            "environment_only_exclusions": exclusions, "sha256": digest(values)}


def input_fingerprint(inputs):
    return digest({
        "annual_values": hashlib.sha256(pd.util.hash_pandas_object(inputs.annual, index=True).values.tobytes()).hexdigest(),
        "annual_dtypes": inputs.annual.dtypes.astype(str).to_dict(),
        "rates": hashlib.sha256(np.asarray(inputs.energy_rate_ntd2023_per_kwh).tobytes()).hexdigest(),
        "package": inputs.mainline_package, "kappa": inputs.kappa,
        "economic": inputs.economic_interface, "settlement": inputs.settlement_interface,
        "matrix": hashlib.sha256(pd.util.hash_pandas_object(inputs.settlement_matrix, index=True).values.tobytes()).hexdigest(),
        "paths": inputs.source_paths,
    })


def audit_model(model, handles, req, inputs, core):
    model.update()
    require(model.Status == gp.GRB.LOADED and model.SolCount == 0, "Model has been optimized")
    require(model.ModelSense == gp.GRB.MINIMIZE and model.IsMIP == 1, "Model sense/formulation mismatch")
    require(handles["mode"] == "binary" and handles["layer_a_requirements"] == req, "Model received wrong case")
    require(digest(handles["coefficients"]) == digest(core._mainline_cost_coefficients(inputs.mainline_package)), "Economic package drift")
    variables, constraints, general = model.getVars(), model.getConstrs(), model.getGenConstrs()
    require(model.NumStart == 0 and all(v == gp.GRB.UNDEFINED for v in model.getAttr("Start", variables)), "Warm-start drift")
    require(len(handles["u_mode"]) == 8760 and all(v.VType == gp.GRB.BINARY for v in handles["u_mode"].values()), "Binary exclusivity missing")
    con_by_name = {c.ConstrName: c for c in constraints}
    reserve = [c for n, c in con_by_name.items() if n.startswith("layer_a_reserve_floor_t")]
    require(len(reserve) == 8761, "Missing annual reserve-floor rows")
    for t in range(8761):
        c = con_by_name[f"layer_a_reserve_floor_t{t}"]
        require(c.Sense == ">" and abs(c.RHS - req.reserve_kwh_battery) <= TOL, "Reserve-floor routing mismatch")
        row = model.getRow(c)
        require(row.size() == 3, "Reserve-floor segment count mismatch")
        require({row.getVar(i).index: row.getCoeff(i) for i in range(row.size())}
                == {handles["e_seg"][t, k].index: 1.0 for k in range(3)}, "Reserve-floor state semantics differ")
    power = con_by_name["layer_a_power_adequacy"]
    require(power.Sense == ">" and abs(power.RHS - req.power_requirement_kw_ac) <= TOL, "Power requirement routing mismatch")
    power_row = model.getRow(power)
    require(power_row.size() == 1 and power_row.getVar(0).sameAs(handles["P_B"]) and power_row.getCoeff(0) == 1, "Power adequacy variable mismatch")
    bus = np.array([con_by_name[f"ac_balance_t{t}"].RHS for t in range(8760)])
    expected_bus = inputs.annual.baseline_load_kw.to_numpy(float) - inputs.annual.pv_available_kw.to_numpy(float)
    require(np.allclose(bus, expected_bus, atol=1e-9, rtol=0), "AC-bus input mismatch")
    require(np.allclose([handles["p_grid"][t].Obj for t in range(8760)], inputs.energy_rate_ntd2023_per_kwh, atol=1e-12, rtol=0), "TOU objective mismatch")
    require(sum(n.startswith("seg_dyn_t") for n in con_by_name) == 26280, "Intertemporal state rows missing")
    require(sum(n.startswith("cyclic_seg_k") for n in con_by_name) == 3, "Annual cyclic segment rows missing")
    types = Counter(int(c.GenConstrType) for c in general)
    require(types == {gp.GRB.GENCONSTR_MAX: 8, gp.GRB.GENCONSTR_INDICATOR: 17520}, f"General constraint drift: {types}")
    require(model.NumBinVars == 8764, "Unexpected binary count")
    require(set(handles["cost_expr"]) == {"annualized_capex", "fom", "energy", "basic", "overcontract_pure_season", "overcontract_transition_resolved", "degradation"}, "Cost component missing/extra")
    max_operands = sum(len(model.getGenConstrMax(c)[1]) for c in general if c.GenConstrType == gp.GRB.GENCONSTR_MAX)
    require(max_operands == 858, "Reduced-native-MAX operand routing mismatch")
    params = parameter_audit(model)
    counts = {"variables": model.NumVars, "linear_constraints": model.NumConstrs, "binary_variables": model.NumBinVars,
              "integer_variables_including_binary": model.NumIntVars, "general_constraints": model.NumGenConstrs,
              "indicator_constraints": types[gp.GRB.GENCONSTR_INDICATOR], "max_constraints": types[gp.GRB.GENCONSTR_MAX],
              "max_operands": max_operands, "sos_constraints": model.NumSOS, "reserve_floor_rows": len(reserve),
              "segment_dynamics_rows": 26280, "cyclic_segment_rows": 3}
    return {"status": "BUILD_PASS", "counts": counts, "model_status": model.Status, "solution_count": model.SolCount,
            "model_sense": "MINIMIZE", "mode": "binary", "parameters": params,
            "model_fingerprint": int(model.Fingerprint), "layer_a_requirements": asdict(req),
            "finite_design_bounds": handles["finite_design_bounds"],
            "transition_formulation_metadata": handles["transition_formulation_metadata"],
            "routing_gates": {name: "PASS" for name in (
                "canonical_ac_bus", "canonical_tou_objective", "reserve_rhs_all_8761_states", "reserve_segment_state_identity",
                "power_rhs", "binary_exclusivity", "no_warm_start", "intertemporal_degradation", "cyclic_segments",
                "all_cost_components", "reduced_native_max", "production_parameters", "model_loaded_unsolved")}}


def runner_design(helper, core):
    required_helpers = ("representative_gate", "billing_structure_audit", "validate_representative_rainflow", "eob_comparison")
    require(all(callable(getattr(helper, n, None)) for n in required_helpers), "Post-solve helper unavailable")
    from src.rainflow_validation_v7_2 import validate_dispatch_rainflow
    require(callable(validate_dispatch_rainflow) and callable(core.solve_eob), "Production callable unavailable")
    return {
        "status": "PASS_DESIGN_AUDIT_ONLY", "future_runner": "scripts/19b_run_final_layer_a_81_cases.py",
        "solving_runner_created": False, "post_solve_gates_executed_in_this_pass": False,
        "output_root": "results/layer_a/final_81/runs/<RUN_ID>/",
        "hierarchy": ["run_manifest.json", "pre_solve_gate.json", "case_matrix.csv",
                      "cases/<CASE_ID>/case_manifest.json", "cases/<CASE_ID>/result.json",
                      "cases/<CASE_ID>/dispatch.parquet", "cases/<CASE_ID>/billing_exact.csv",
                      "cases/<CASE_ID>/transition_detail.csv", "cases/<CASE_ID>/rainflow_audit.json",
                      "cases/<CASE_ID>/post_solve_audit.json", "cases/<CASE_ID>/gurobi.log",
                      "cases/<CASE_ID>/solver_telemetry.jsonl", "cases/<CASE_ID>/completion_manifest.json",
                      "final_surface_summary.csv", "final_validation_registry.json", "completion_manifest.json"],
        "routing": "exact run ID + case ID + frozen manifest/SHA-256; exclusive new directories; never top-level 16a convenience copies",
        "architecture": [
            "Validate exact accepted preflight/checkpoint, repository and environment before creating solver models.",
            "Load canonical parquet explicitly; reject CSV fallback and any alternative input path/hash.",
            "Use Script-16a analytical_surface and Script-09 valid-start authority; freeze the 81-row case matrix.",
            "For each exact case use core.solve_eob with LayerAResilienceRequirements and the common parameter fingerprint.",
            "Preserve returned dispatch, billing and transition details before validation; failed evidence remains diagnostic.",
            "Use existing representative_gate, billing_structure_audit and rainflow helpers on each new result.",
            "Write case completion last after all gate and artifact hashes pass; aggregate only exact-manifest accepted cases.",
        ],
        "failure_states": ["BUILD_FAIL", "SOLVER_NO_SOLUTION", "NON_OPTIMAL", "MIP_GAP_FAIL",
                           "PHYSICAL_GATE_FAIL", "RESILIENCE_GATE_FAIL", "BILLING_GATE_FAIL",
                           "TRANSITION_GATE_FAIL", "DEGRADATION_GATE_FAIL", "RAINFLOW_GATE_FAIL",
                           "ARTIFACT_HASH_FAIL", "COMPLETE_PASS"],
        "failure_policy": "Persist case/run failure evidence and all diagnostics, stop at first failing case, retain 81-row registry with unattempted cases explicitly NOT_RUN; never omit a failure or write success completion.",
        "resume_policy": "FRESH_RUN_ONLY",
        "resume_reason": "Existing wrapper has no complete identity-and-artifact-verified resume transaction. Each submission creates a new run ID; no completed-case reuse is implemented or promised.",
        "possible_future_resume_prerequisites": ["explicit protocol authorization", "exact run and case IDs", "alpha/beta match",
            "canonical/core/economic/tariff/settlement/degradation hashes", "identical solver settings", "accepted complete case manifest",
            "all output hashes verified", "never infer completion from a result file or mtime"],
        "post_solve_gates": {
            "solver": "has_solution, OPTIMAL, binary, MIPGap <= 1e-6, finite nonnegative E_N/P_B/CC",
            "physics": "core physical_diagnostics and representative_gate; SOC, AC balance, power rating, cyclic state, no simultaneous charge/discharge",
            "resilience": "representative_gate analytical E_N lower bound, Pout and annual reserve floor; binding requirement from exact case matrix",
            "all_start_consistency": "Future minimal non-optimizing adapter: every Script-09 valid window, initial energy SOCmin*E_N+R, supply positive deficits at discharge efficiency, no PV-surplus recharge, technical SOC bounds and terminal SOCmin; check hourly power and energy across every step; no circular wrap. No reusable complete replay callable currently exists.",
            "accounting": "sum all seven cost components vs objective within existing 1e-3 NTD tolerance; pure/transition solver-vs-exact residuals",
            "billing": "core billing_exact plus billing_structure_audit, dispatch-derived kappa maxima by usage-period/TOU and overall; retain exact maxima not epigraph auxiliaries",
            "transition": "current core postsolve_invariants_pass, empty failures, zero unresolved boundary count and PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE",
            "degradation": "intertemporal segment link/dynamic/cyclic/PWL residual checks; full 10 MW package",
            "rainflow": "validate_representative_rainflow -> validate_dispatch_rainflow; all gates PASS; REVIEW never promoted automatically",
        },
        "output_mapping": {
            "R_Pout_binding_window": "case_matrix: R_kwh_battery, P_out_kw_ac, binding_historical_start/end_exclusive",
            "E_N_P_B_CC": "result.sizing: E_N_kwh, P_B_kw_ac, CC_regular_kw",
            "E_U": "(SOC_MAX-SOC_MIN)*E_N; usable energy is distinct from economic headroom E_U-R",
            "annual_total_cost": "result.objective_ntd2023_per_year",
            "resilience_premium": "helper.eob_comparison against exact frozen historical EOB comparator, never a re-solve",
            "TOU_basic_overcontract_FOM_degradation_CAPEX": "all seven result.cost_components_ntd2023_per_year fields; optional energy/power CAPEX splits reconcile to aggregate",
            "exact_demand_diagnostics": "result.billing_exact: exact_billing_demand_kw, overall_exact_billing_demand_kw by usage period/TOU",
            "degradation_diagnostics": "rainflow.pwl_segments: battery-side discharge and cost per segment; total degradation share of annual cost",
            "SOC_and_headroom": "physical_diagnostics; dispatch.e_physical_kwh - (SOC_MIN*E_N+R), min/max/mean and reserve-floor binding frequency using existing numerical tolerance",
            "maximum_hourly_discharge_fraction": "max(dispatch.p_discharge_kw_ac)*DELTA_T_HR/(ETA_D*E_N); intensity diagnostic, never labelled DOD",
            "rainflow_diagnostics": "rainflow.summary, cycles, turning_points, depth_bins, pwl_segments, g_curve, gates and algorithm_self_test",
            "runtime_MIPgap": "result.runtime_sec_gurobi, runtime_sec_wall, mip_gap, status, plus construction/solve telemetry",
        },
        "surface_completion": "81 unique expected grid coordinates, 81 COMPLETE_PASS case manifests, verified artifact hashes and matching common identities/parameters, then final summary and validation registry, then completion last",
        "future_surface_gates": ["81/81 accepted cases; no duplicates/missing/extras", "E_N >= R/(SOCmax-SOCmin)",
            "P_B >= Pout", "R nondecreasing in alpha and beta", "Pout nondecreasing in alpha and constant across beta",
            "same canonical input and full 10 MW package", "constant NTD-2023 costs and exact frozen EOB premiums",
            "review unexpected discontinuities and verify routing/configuration; never smooth/force monotonic optimal sizing or CC"],
        "scope_limit": "Build readiness is not a feasibility or optimality certificate. Future production runner and post-solve reporting adapters require implementation and validation before authorized solving.",
    }


def main():
    require(len(sys.argv) == 1, "Preflight accepts no input, case, solver or resume overrides")
    sys.path.insert(0, str(ROOT))
    run_dir = None
    completed_cases = []
    attempted = 0
    current_case = None
    guard = NoOptimization()
    started = now()
    try:
        with guard:
            repo = repository_gate()
            checkpoint, prior, identities = lineage_gate()
            snapshot_sources(identities)
            controls = {"18a": existing_validator("scripts/18a_validate_production_checkpoint.py"),
                        "18b": existing_validator("scripts/18b_preflight_production_environment.py")}
            guard.check()
            from src import annual_design_model_v7_2 as core
            helper = load_module("scripts/16a_preflight_layer_a_representative_binary_cases.py", "preflight19a_helper16a")
            indexer = load_module("scripts/09_build_valid_outage_start_sets.py", "preflight19a_indexer09")
            require(core.CORE_VERSION == CORE_VERSION, "Core version mismatch")
            require((core.SOC_MIN, core.SOC_MAX, core.ETA_C, core.ETA_D) == (0.1, 0.9, 0.9, 0.9), "BESS physics drift")
            inputs = core.load_annual_design_inputs(ROOT, annual_parquet=ROOT / CANONICAL,
                                                   annual_csv=ROOT / "data/processed/NO_CSV_FALLBACK_ALLOWED.csv")
            require(controlled(inputs.source_paths["annual_input"]) == ROOT / CANONICAL, "Noncanonical annual input routed")
            require("artifact_role" not in inputs.annual.columns, "Sensitivity artifact routed")
            package = inputs.mainline_package
            require(package == inputs.economic_interface["package_selector"]["mainline"] and package["power_scale_bracket_mw"] == 10,
                    "Full 10 MW package mismatch")
            monetary = inputs.economic_interface["monetary_basis"]
            require(monetary["currency_base_year"] == 2023 and monetary["discount_rate"] == 0.05
                    and monetary["analysis_horizon_years"] == 20 and monetary["crf"] == 0.08024258719069129,
                    "Monetary-basis drift")
            require(inputs.kappa == inputs.economic_interface["billing_demand_proxy"]["kappa"] == 1.0103668594376984, "Kappa drift")
            for path, expected in identity_pairs(inputs.economic_interface):
                verify_identity(path, expected, identities)
            input_ids = {key: {"path": controlled(value).relative_to(ROOT).as_posix(), "sha256": sha(controlled(value))}
                         for key, value in inputs.source_paths.items()}
            for item in input_ids.values():
                require(identities.get(item["path"]) == item["sha256"], f"Unfrozen routed input: {item['path']}")
            routing = {"inputs": input_ids, "core_path": CORE, "core_sha256": CORE_SHA, "core_version": CORE_VERSION,
                       "package": package, "package_sha256": digest(package), "monetary_basis": monetary,
                       "kappa": inputs.kappa, "rainflow_sha256": identities["src/rainflow_validation_v7_2.py"],
                       "bess": {"chemistry": "stationary LFP", "E_N": "nameplate_kwh", "energy_state": "battery_side",
                                "power": "AC_PCS_side", "SOC_MIN": core.SOC_MIN, "SOC_MAX": core.SOC_MAX,
                                "ETA_C": core.ETA_C, "ETA_D": core.ETA_D, "breakpoints": core.BREAKPOINTS},
                       "reserve_policy": "constant annual worst-case reserve above technical SOCmin",
                       "annual_input_consumed": CANONICAL, "winter_pv_consumption": False}
            surface, cross, start_sets = requirements_gate(inputs, helper, indexer, checkpoint, prior, identities)
            design = runner_design(helper, core)
            settings = core.SolveSettings(mode="binary", mip_gap=MIP_GAP, time_limit_sec=None, output_flag=0, numeric_focus=1)
            base_fingerprint = input_fingerprint(inputs)
            run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:10]
            run_dir = ROOT / "results/layer_a/final_81_preflight" / run_id
            run_dir.mkdir(parents=True, exist_ok=False)
            (run_dir / "cases").mkdir()
            write(run_dir / "run_manifest.json", {"run_id": run_id, "script_version": SCRIPT_VERSION,
                  "script_sha256": sha(ROOT / SCRIPT_PATH), "started_utc": started, "mode": "BUILD_ONLY_NO_OPTIMIZE",
                  "repository": repo, "checkpoint": {"path": CHECKPOINT, "sha256": CHECKPOINT_SHA},
                  "source_and_artifact_hashes_before": identities, "routing": routing, "settings": asdict(settings),
                  "settings_qualification": "No TimeLimit: accepted core/16a default and post-17C production setting. The historical five-case validation explicitly used 900 seconds; that run cap is not inherited. OutputFlag=0 follows accepted 16a build-only diagnostics; no solve tuning changed.",
                  "optimization_guards": list(guard.guards), "case_order": surface.case_id.tolist()})
            write(run_dir / "pre_solve_gate.json", {"status": "PASS", "meaning": "permission_to_build_only",
                  "controls": controls, "repository": repo, "routing": routing,
                  "protected_identity_count": len(identities), "optimization_calls": len(guard.calls)})
            write(run_dir / "grid_definition.json", {"alpha_values": ALPHAS, "beta_values_h": BETAS, "count": 81,
                  "case_id_convention": "Script-16a a{alpha:.2f}_b{beta:02d}", "missing": [], "extra": [], "duplicates": 0})
            write(run_dir / "cross_case_structural_audit.json", cross)
            write(run_dir / "production_runner_design_audit.json", design)
            surface.to_csv(run_dir / "case_matrix.csv", index=False)
            surface.pivot(index="alpha", columns="beta_h", values="R_kwh_battery").to_csv(run_dir / "reserve_matrix.csv")
            binding = surface.copy()
            binding["window"] = binding.binding_historical_start.astype(str) + "/" + binding.binding_historical_end_exclusive.astype(str)
            binding.pivot(index="alpha", columns="beta_h", values="window").to_csv(run_dir / "binding_window_matrix.csv")
            start_sets.to_parquet(run_dir / "valid_start_sets.parquet", index=False)
            common_parameters = None
            common_structure = None
            for case in surface.to_dict("records"):
                current_case = case["case_id"]
                attempted += 1
                guard.check()
                require(input_fingerprint(inputs) == base_fingerprint, "Shared production inputs mutated between cases")
                for item in input_ids.values():
                    require(sha(ROOT / item["path"]) == item["sha256"], "Routed source drift between cases")
                require(sha(ROOT / CORE) == CORE_SHA, "Core drift between cases")
                req = core.LayerAResilienceRequirements(alpha=float(case["alpha"]), beta_h=int(case["beta_h"]),
                        reserve_kwh_battery=float(case["R_kwh_battery"]), power_requirement_kw_ac=float(case["P_out_kw_ac"]))
                model = None
                handles = None
                build_started = time.perf_counter()
                try:
                    model, handles = core.build_eob_model(inputs, settings, req)
                    record = audit_model(model, handles, req, inputs, core)
                    guard.check()
                    require(input_fingerprint(inputs) == base_fingerprint, "Core mutated shared production inputs")
                    if common_parameters is None:
                        common_parameters = record["parameters"]
                        common_structure = record["counts"]
                    require(record["parameters"] == common_parameters, f"Case-dependent solver settings: {current_case}")
                    require(record["counts"] == common_structure, f"Unexplained structural difference: {current_case}")
                    record.update({"run_id": run_id, "case_id": current_case, "requirement": case,
                                   "routing": routing, "production_settings": asdict(settings),
                                   "shared_input_fingerprint": base_fingerprint, "optimization_calls": 0,
                                   "build_and_audit_seconds": time.perf_counter() - build_started})
                finally:
                    if model is not None:
                        model.dispose()
                    handles = None
                    model = None
                    gc.collect()
                record["model_disposed"] = True
                write(run_dir / "cases" / f"{current_case}_build_audit.json", record)
                completed_cases.append({**case, **record["counts"], "build_status": "PASS",
                    "model_sense": "MINIMIZE", "charge_discharge_formulation": "binary", "MIPGap": MIP_GAP,
                    "TimeLimit": "infinity_unset", "MIPFocus": 0, "Threads": 0, "NumericFocus": 1,
                    "solver_parameter_sha256": common_parameters["sha256"], "package_sha256": routing["package_sha256"],
                    "economic_sha256": input_ids["economic_interface_14a"]["sha256"],
                    "tariff_sha256": input_ids["normalized_tariff_14a"]["sha256"],
                    "settlement_interface_sha256": input_ids["settlement_interface_14b"]["sha256"],
                    "settlement_matrix_sha256": input_ids["settlement_matrix_14b"]["sha256"],
                    "degradation_package_sha256": routing["package_sha256"], "rainflow_sha256": routing["rainflow_sha256"],
                    "optimization_calls": 0, "model_disposed": True,
                    "build_and_audit_seconds": record["build_and_audit_seconds"]})
                print(f"BUILD {attempted:02d}/81 {current_case} PASS; disposed; optimize_calls={len(guard.calls)}", flush=True)
            pd.DataFrame(completed_cases).to_csv(run_dir / "per_case_build_audit.csv", index=False)
            write(run_dir / "solver_parameter_fingerprint.json", {"status": "PASS", "unique_fingerprints": 1,
                  "case_count": 81, **common_parameters,
                  "structural_counts": common_structure,
                  "structure_explanation": "Same case-year, 8761 reserve rows, one power-adequacy row and fixed tariff calendar. Alpha/beta change R/Pout RHS and derived safe finite bounds, not constraint counts. Model fingerprints may differ."})
            after = repository_gate()
            for path, expected in identities.items():
                require(sha(ROOT / path) == expected, f"Protected artifact changed during preflight: {path}")
            require(attempted == len(completed_cases) == 81, "Incomplete builds")
            guard.check()
            write(run_dir / "post_build_immutability_audit.json", {"status": "PASS", "repository": after,
                  "verified_identity_count": len(identities), "source_and_artifact_hashes_after": identities,
                  "all_unchanged": True, "optimization_calls": len(guard.calls)})
            registry = {p.relative_to(run_dir).as_posix(): {"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size}
                        for p in sorted(run_dir.rglob("*")) if p.is_file()}
            for record in registry.values():
                require(sha(ROOT / record["path"]) == record["sha256"], "Preflight output hash mismatch")
            write(run_dir / "completion_manifest.json", {"run_id": run_id, "script_version": SCRIPT_VERSION,
                  "script_sha256": sha(ROOT / SCRIPT_PATH), "completed_utc": now(), "status": "PASS",
                  "final_verdict": PASS_VERDICT, "checkpoint_sha256": CHECKPOINT_SHA,
                  "case_definitions_valid": 81, "builds_attempted": attempted, "builds_passed": 81, "builds_failed": 0,
                  "optimization_calls": len(guard.calls), "optimization_guard_methods": list(guard.guards),
                  "solver_parameter_fingerprint": common_parameters["sha256"], "unique_parameter_fingerprints": 1,
                  "artifact_registry": registry, "all_structural_provenance_gates_pass": True,
                  "final_81_production_solves": "NOT_YET_RUN", "WINTER_PV_P1": "CLOSED"})
            print(json.dumps({"verdict": PASS_VERDICT, "run_id": run_id, "directory": str(run_dir),
                              "completion_sha256": sha(run_dir / "completion_manifest.json"), "optimization_calls": len(guard.calls)}, indent=2))
        return 0
    except BaseException as exc:
        failure = {"status": "FAIL", "verdict": FAIL_VERDICT, "utc": now(), "case_id": current_case,
                   "attempted": attempted, "completed": len(completed_cases), "optimization_calls": len(guard.calls),
                   "forbidden_calls": guard.calls, "exception": f"{type(exc).__name__}: {exc}",
                   "traceback": traceback.format_exc(), "success_completion_written": False}
        if run_dir is not None:
            write(run_dir / "failure_manifest.json", failure)
            pd.DataFrame(completed_cases).to_csv(run_dir / "partial_build_audit.csv", index=False)
        print(json.dumps(failure, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
