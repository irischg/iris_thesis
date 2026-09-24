#!/usr/bin/env python3
"""Step 2E-1 v7.3 production-input routing preflight (strictly zero-solve).

The preflight proves input identity and analytical same-artifact routing.  It
does not build a Gurobi model, call an optimization API, execute EOB, run a
Layer A case, create Final81 output, or authorize a later production step.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.production_input_authority_v7_3 import (  # noqa: E402
    ACCEPTED_ANNUAL_RELATIVE_PATH,
    AnnualInputIdentity,
    annual_dataframe_fingerprint,
    impossible_csv_path,
    load_accepted_v7_3_annual_input,
    require_same_annual_identity,
    sha256_file,
)


SCRIPT_VERSION = "v7.3-step2e1-production-routing-zero-solve-preflight-2026-09-24-r1"
EXPECTED_BRANCH = "thesis-v7"
FREEZE_COMMIT = "07200697d0da7567715ec77edf3d853acbc53918"
FREEZE_TAG = "v7.3-step2d-r3-accepted-2026-09-24"
ALPHAS = tuple(round(0.60 + 0.05 * index, 2) for index in range(9))
BETAS_H = tuple(range(4, 13))
ETA_D = 0.90
SOC_MIN = 0.10
SOC_MAX = 0.90
TOL = 1e-6

IMMUTABLE_DEPENDENCIES = (
    Path("src/annual_design_model_v7_2.py"),
    Path("scripts/09_build_valid_outage_start_sets.py"),
    Path("scripts/16a_preflight_layer_a_representative_binary_cases.py"),
    Path("scripts/20c_build_v7_3_reconstructed_pv_mainline_candidate_r3.py"),
)

ROUTING_CONSUMERS = (
    "prospective_eob",
    "prospective_layer_a_annual_economics",
    "layer_a_R_alpha_beta",
    "layer_a_P_out_alpha",
    "layer_a_binding_classification",
    "layer_a_analytical_replay",
    "prospective_baseline_layer_b",
)


class RoutingPreflightError(RuntimeError):
    """Fail-closed Step 2E-1 preflight error."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of indented JSON; no files are written.",
    )
    return parser.parse_args()


def _git(root: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def verify_repository_lineage(root: Path) -> dict[str, Any]:
    branch = _git(root, "branch", "--show-current")
    head = _git(root, "rev-parse", "HEAD")
    tag_commit = _git(root, "rev-parse", f"{FREEZE_TAG}^{{}}")
    if branch != EXPECTED_BRANCH:
        raise RoutingPreflightError(
            f"Expected branch {EXPECTED_BRANCH!r}; observed {branch!r}."
        )
    if tag_commit != FREEZE_COMMIT:
        raise RoutingPreflightError(
            f"Freeze tag peels to {tag_commit}, not accepted commit {FREEZE_COMMIT}."
        )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", FREEZE_COMMIT, head],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if ancestor.returncode != 0:
        raise RoutingPreflightError(
            "Accepted Step 2D freeze commit is not an ancestor of live HEAD."
        )
    for relative in IMMUTABLE_DEPENDENCIES:
        changed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative.as_posix()],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if changed.returncode != 0:
            raise RoutingPreflightError(
                f"Historical/accepted dependency has uncommitted drift: {relative.as_posix()}"
            )
    return {
        "status": "PASS",
        "branch": branch,
        "head": head,
        "freeze_commit": FREEZE_COMMIT,
        "freeze_tag": FREEZE_TAG,
        "freeze_tag_peeled_commit": tag_commit,
        "freeze_commit_is_ancestor": True,
        "immutable_dependencies_clean_against_head": [
            relative.as_posix() for relative in IMMUTABLE_DEPENDENCIES
        ],
    }


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RoutingPreflightError(f"Could not import required helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ZeroSolveGuard:
    """Block model construction and every Gurobi optimization entry point."""

    def __init__(self) -> None:
        self._stack = ExitStack()
        self._gp: Any | None = None
        self.forbidden_attempts: list[str] = []
        self.model_constructions = 0
        self.optimization_calls = 0
        self.guarded_methods: list[str] = []

    def _blocker(self, name: str, *, construction: bool = False):
        def blocked(*_args: Any, **_kwargs: Any) -> None:
            self.forbidden_attempts.append(name)
            if construction:
                self.model_constructions += 1
            else:
                self.optimization_calls += 1
            raise RoutingPreflightError(
                f"ZERO-SOLVE guard blocked forbidden Gurobi API: {name}"
            )

        return blocked

    def __enter__(self) -> "ZeroSolveGuard":
        self._gp = importlib.import_module("gurobipy")
        targets = (
            ("__init__", True),
            ("optimize", False),
            ("optimizeAsync", False),
            ("optimizeBatch", False),
            ("tune", False),
        )
        for name, construction in targets:
            if not hasattr(self._gp.Model, name):
                raise RoutingPreflightError(
                    f"Cannot install required ZERO-SOLVE guard; gp.Model.{name} is absent."
                )
            self._stack.enter_context(
                patch.object(
                    self._gp.Model,
                    name,
                    self._blocker(
                        f"Model.{name}", construction=construction
                    ),
                )
            )
            self.guarded_methods.append(f"Model.{name}")
        return self

    def __exit__(self, *args: Any) -> bool:
        return bool(self._stack.__exit__(*args))

    def require_zero(self) -> None:
        if self.model_constructions != 0 or self.optimization_calls != 0:
            raise RoutingPreflightError(
                "ZERO-SOLVE contract violated: "
                f"model_constructions={self.model_constructions}, "
                f"optimization_calls={self.optimization_calls}, "
                f"attempts={self.forbidden_attempts}"
            )

    def counters(self) -> dict[str, Any]:
        return {
            "model_constructions": self.model_constructions,
            "optimization_calls": self.optimization_calls,
            "economic_evaluations": 0,
            "eob_runs": 0,
            "layer_a_solves": 0,
            "final81_runs": 0,
            "layer_b_runs": 0,
            "forbidden_attempts": list(self.forbidden_attempts),
            "guarded_methods": list(self.guarded_methods),
        }


def load_through_unchanged_core(
    root: Path,
    accepted: Any,
) -> tuple[Any, dict[str, Any]]:
    core = importlib.import_module("src.annual_design_model_v7_2")
    forbidden_csv = impossible_csv_path(root)
    inputs = core.load_annual_design_inputs(
        root,
        annual_parquet=accepted.resolved_path,
        annual_csv=forbidden_csv,
    )
    used = Path(inputs.source_paths["annual_input"]).resolve()
    if used != accepted.resolved_path:
        raise RoutingPreflightError(
            f"Core loader did not use accepted R3 parquet: used={used}"
        )
    core_fingerprint = annual_dataframe_fingerprint(inputs.annual)
    if core_fingerprint["fingerprint_sha256"] != accepted.identity.fingerprint_sha256:
        raise RoutingPreflightError(
            "Unchanged annual core returned a dataframe with a different routing fingerprint."
        )
    if forbidden_csv.exists():
        raise RoutingPreflightError("Forbidden CSV fallback sentinel was created or used.")
    return inputs, {
        "status": "PASS",
        "core_module": "src/annual_design_model_v7_2.py",
        "core_version": core.CORE_VERSION,
        "accepted_parquet_supplied_explicitly": ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        "core_reported_annual_input": str(used),
        "csv_argument": str(forbidden_csv),
        "csv_argument_exists": False,
        "csv_fallback_occurred": False,
        "legacy_default_used": False,
        "core_dataframe_fingerprint": core_fingerprint,
    }


def valid_start_identity_audit(
    root: Path,
    annual: pd.DataFrame,
    script16_starts: pd.DataFrame,
) -> dict[str, Any]:
    script09 = _load_module(
        root / "scripts/09_build_valid_outage_start_sets.py",
        "step2e1_script09_valid_starts",
    )
    timestamps = pd.to_datetime(annual["timestamp"], errors="raise").reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    script16_by_beta = script16_starts.set_index("beta_h")
    for beta in BETAS_H:
        frame = script09.build_valid_start_rows(timestamps, beta)
        audit = script09.audit_one_beta(frame, beta)
        expected_count = len(annual) - beta + 1
        script16_count = int(script16_by_beta.loc[beta, "valid_start_count"])
        if len(frame) != expected_count or script16_count != expected_count:
            raise RoutingPreflightError(
                f"Valid-start identity mismatch for beta={beta}: "
                f"script09={len(frame)}, script16={script16_count}, expected={expected_count}"
            )
        if bool(frame["circular_wrap_used"].any()):
            raise RoutingPreflightError(f"Circular wrap detected for beta={beta}.")
        rows.append(
            {
                "beta_h": beta,
                "valid_start_count": len(frame),
                "first_valid_start": frame.iloc[0]["start_timestamp"],
                "last_valid_start": frame.iloc[-1]["start_timestamp"],
                "last_end_exclusive": frame.iloc[-1]["end_timestamp_exclusive"],
                "no_circular_wrap": True,
                "script09_audit": audit,
            }
        )
    return {
        "status": "PASS",
        "method": "recomputed from accepted R3 timestamps using unchanged Script-09 helpers",
        "pv_values_used_in_start_set": False,
        "timestamp_identity_source": ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        "rows": rows,
    }


def analytical_replay_consistency(
    annual: pd.DataFrame,
    surface: pd.DataFrame,
    *,
    expected_identity: AnnualInputIdentity,
    replay_identity: AnnualInputIdentity,
) -> dict[str, Any]:
    require_same_annual_identity(
        expected_identity,
        replay_identity,
        consumer="layer_a_analytical_replay",
    )
    load = annual["baseline_load_kw"].to_numpy(dtype=float)
    pv = annual["pv_available_kw"].to_numpy(dtype=float)
    timestamps = pd.to_datetime(annual["timestamp"], errors="raise").reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    for alpha in ALPHAS:
        deficit = np.maximum(alpha * load - pv, 0.0)
        replay_p_out = float(np.max(deficit))
        prefix = np.concatenate(([0.0], np.cumsum(deficit, dtype=float)))
        for beta in BETAS_H:
            requirement = surface.loc[
                surface["alpha"].eq(alpha) & surface["beta_h"].eq(beta)
            ]
            if len(requirement) != 1:
                raise RoutingPreflightError(
                    f"Analytical surface lacks unique case alpha={alpha}, beta={beta}."
                )
            record = requirement.iloc[0]
            window_energy = prefix[beta:] - prefix[:-beta]
            replay_binding_index = int(np.argmax(window_energy))
            replay_max_ac_energy = float(window_energy[replay_binding_index])
            replay_reserve = replay_max_ac_energy / ETA_D
            accepted_binding_index = int(record["binding_start_index"])
            accepted_binding_energy = float(window_energy[accepted_binding_index])
            accepted_reserve = float(record["R_kwh_battery"])
            ending_energy = accepted_reserve - accepted_binding_energy / ETA_D
            checks = {
                "p_out": bool(np.isclose(replay_p_out, record["P_out_kw_ac"], atol=TOL)),
                "reserve": bool(np.isclose(replay_reserve, accepted_reserve, atol=TOL)),
                "binding_is_maximum": bool(
                    np.isclose(accepted_binding_energy, replay_max_ac_energy, atol=TOL)
                ),
                "binding_terminal_energy": bool(np.isclose(ending_energy, 0.0, atol=TOL)),
                "all_starts_within_reserve": bool(
                    np.min(accepted_reserve - window_energy / ETA_D) >= -TOL
                ),
            }
            if not all(checks.values()):
                raise RoutingPreflightError(
                    f"Analytical replay mismatch for alpha={alpha}, beta={beta}: {checks}"
                )
            rows.append(
                {
                    "case_id": str(record["case_id"]),
                    "binding_start": timestamps.iloc[accepted_binding_index],
                    "binding_end_exclusive": timestamps.iloc[accepted_binding_index]
                    + pd.Timedelta(hours=beta),
                    "replay_binding_index": replay_binding_index,
                    "accepted_binding_index": accepted_binding_index,
                    "ending_battery_energy_above_technical_min_kwh": ending_energy,
                    "checks": checks,
                }
            )
    return {
        "status": "PASS",
        "case_count": len(rows),
        "annual_identity": replay_identity.as_dict(),
        "eta_d": ETA_D,
        "surplus_pv_recharge": False,
        "method": (
            "independent cumulative-sum replay over every valid non-circular start; "
            "positive deficit only"
        ),
        "cases": rows,
    }


def build_routing_map(identity: AnnualInputIdentity) -> dict[str, dict[str, Any]]:
    routing: dict[str, dict[str, Any]] = {}
    for consumer in ROUTING_CONSUMERS:
        routing[consumer] = {
            **identity.as_dict(),
            "routing_status": "PREFLIGHT_ONLY_NOT_PRODUCTION_AUTHORIZATION",
            "execution_status": "NOT_EXECUTED",
        }
    return routing


def validate_routing_map(
    routing: Mapping[str, Mapping[str, Any]],
    expected_identity: AnnualInputIdentity,
) -> None:
    if set(routing) != set(ROUTING_CONSUMERS):
        raise RoutingPreflightError(
            f"Routing map consumers differ from required set: {sorted(routing)}"
        )
    expected = expected_identity.as_dict()
    for consumer in ROUTING_CONSUMERS:
        observed = {key: routing[consumer].get(key) for key in expected}
        if observed != expected:
            raise RoutingPreflightError(
                f"Same-artifact routing failure for {consumer}: "
                f"expected={expected}, observed={observed}"
            )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat(sep=" ")
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        raise RoutingPreflightError("Non-finite value cannot be serialized in preflight output.")
    return value


def _surface_records(surface: pd.DataFrame) -> list[dict[str, Any]]:
    return [_json_safe(record) for record in surface.to_dict(orient="records")]


def run_preflight(root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    lineage = verify_repository_lineage(root)
    with ZeroSolveGuard() as guard:
        accepted = load_accepted_v7_3_annual_input(root)
        core_inputs, core_audit = load_through_unchanged_core(root, accepted)

        script16 = _load_module(
            root / "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            "step2e1_script16a_analytical",
        )
        if tuple(script16.ALPHAS) != ALPHAS or tuple(script16.BETAS_H) != BETAS_H:
            raise RoutingPreflightError("Script-16a alpha/beta grid differs from v7.3 gate.")
        surface, script16_starts, analytical_audit = script16.analytical_surface(
            core_inputs.annual,
            eta_d=ETA_D,
            soc_min=SOC_MIN,
            soc_max=SOC_MAX,
        )
        if analytical_audit.get("status") != "PASS" or len(surface) != 81:
            raise RoutingPreflightError(
                f"Script-16a analytical surface audit failed: {analytical_audit}"
            )
        valid_starts = valid_start_identity_audit(
            root, core_inputs.annual, script16_starts
        )
        replay = analytical_replay_consistency(
            core_inputs.annual,
            surface,
            expected_identity=accepted.identity,
            replay_identity=accepted.identity,
        )
        routing = build_routing_map(accepted.identity)
        validate_routing_map(routing, accepted.identity)
        guard.require_zero()
        counters = guard.counters()

    if counters["model_constructions"] != 0 or counters["optimization_calls"] != 0:
        raise RoutingPreflightError("Zero-solve counters are not zero.")

    return {
        "status": "PASS",
        "verdict": "STEP 2E-1 ROUTING PREFLIGHT PASS",
        "script_version": SCRIPT_VERSION,
        "scope": "ADDITIVE_V7_3_PRODUCTION_INPUT_AUTHORITY_AND_ZERO_SOLVE_PREFLIGHT",
        "repository_lineage": lineage,
        "accepted_annual_input": {
            **accepted.identity.as_dict(),
            "resolved_path": str(accepted.resolved_path),
            "dataframe_fingerprint": accepted.dataframe_fingerprint,
            "authority_hashes": accepted.authority_hashes,
        },
        "unchanged_core_loader_integration": core_audit,
        "routing_map": routing,
        "analytical_surface_audit": {
            **analytical_audit,
            "equation_source": (
                "scripts/16a_preflight_layer_a_representative_binary_cases.py::"
                "analytical_surface"
            ),
            "deficit_equation": "max(alpha * baseline_load_kw - pv_available_kw, 0)",
            "reserve_equation": "max_valid_non_circular_beta_hour_deficit_energy / eta_d",
            "eta_d": ETA_D,
            "case_count": int(len(surface)),
            "cases": _surface_records(surface),
        },
        "valid_start_identity_audit": valid_starts,
        "analytical_replay_audit": replay,
        "source_dependencies": {
            relative.as_posix(): sha256_file(root / relative)
            for relative in IMMUTABLE_DEPENDENCIES
        },
        "execution_counters": counters,
        "execution_boundary": {
            "EOB": "NOT EXECUTED",
            "Layer A solves": "NOT EXECUTED",
            "Final81": "NOT EXECUTED",
            "Layer B": "NOT EXECUTED",
            "production_routing_authorized": False,
            "step_2e_2_authorized": False,
        },
    }


def main() -> int:
    args = parse_args()
    try:
        payload = run_preflight(ROOT)
    except Exception as exc:
        failure = {
            "status": "FAIL",
            "verdict": "STEP 2E-1 ROUTING PREFLIGHT FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "optimization_calls": None,
            "zero_solve_status": "NOT_ESTABLISHED_DUE_TO_PREFLIGHT_FAILURE",
            "production_execution_attempted": False,
        }
        print(json.dumps(failure, indent=None if args.compact else 2, sort_keys=True))
        return 1
    print(
        json.dumps(
            _json_safe(payload),
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
