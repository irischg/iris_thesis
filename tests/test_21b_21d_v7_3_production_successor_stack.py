"""Macro Gate 2E-A tests for the additive v7.3 successor stack."""

from __future__ import annotations

import ast
import builtins
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


NEW_SOURCES = (
    ROOT / "src/production_successor_stack_v7_3.py",
    ROOT / "scripts/21b_preflight_v7_3_eob_successor.py",
    ROOT / "scripts/21c_preflight_v7_3_layer_a_successor.py",
    ROOT / "scripts/21d_preflight_v7_3_final81_successor.py",
)


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


class MockProductionBackend:
    """Solver-free double that records the real orchestration contract."""

    def __init__(self, identity: authority.AnnualInputIdentity) -> None:
        self.annual_identity = identity
        self.model_constructions = 0
        self.optimization_calls = 0
        self.events: list[tuple[str, object]] = []

    def solve_eob(self, settings):
        self.model_constructions += 1
        self.optimization_calls += 1
        self.events.append(("solve_eob", dict(settings)))
        return {"kind": "eob", "has_solution": True}

    def solve_layer_a(self, case, settings):
        self.model_constructions += 1
        self.optimization_calls += 1
        self.events.append(
            (
                "solve_layer_a",
                {
                    "case_id": case["case_id"],
                    "alpha": case["alpha"],
                    "beta_h": case["beta_h"],
                    "R_kwh_battery": case["R_kwh_battery"],
                    "P_out_kw_ac": case["P_out_kw_ac"],
                    "annual_identities": deepcopy(case["annual_identities"]),
                    "settings": dict(settings),
                },
            )
        )
        return {"kind": "layer_a", "case_id": case["case_id"], "has_solution": True}

    def _pass(self, name, result):
        self.events.append((name, result["kind"]))
        return {"status": "PASS", "adapter": name}

    def solver_acceptance(self, result):
        return self._pass("solver", result)

    def audit_physical(self, result, case):
        return self._pass("physical", result)

    def audit_resilience(self, result, case):
        return self._pass("resilience", result)

    def audit_billing(self, result):
        return self._pass("billing", result)

    def audit_transition(self, result):
        return self._pass("transition", result)

    def audit_cost_degradation(self, result):
        self.events.append(("cost", result["kind"]))
        self.events.append(("degradation", result["kind"]))
        return {"status": "PASS", "adapter": "cost"}, {
            "status": "PASS",
            "adapter": "degradation",
        }

    def audit_rainflow(self, result):
        return self._pass("rainflow", result)


class MockProductionPublisher:
    def __init__(self) -> None:
        self.events: list[tuple[str, object]] = []

    def publish_eob(self, record):
        self.events.append(("publish_eob", deepcopy(record)))
        return "mock://eob"

    def begin_layer_run(self, record):
        self.events.append(("begin_layer_run", deepcopy(record)))
        return {"published": []}

    def publish_layer_case(self, run, record):
        case_id = record["case"]["case_id"]
        run["published"].append(case_id)
        self.events.append(("publish_layer_case", deepcopy(record)))
        return f"mock://layer/{case_id}"

    def complete_layer_run(self, run, record):
        self.events.append(("complete_layer_run", deepcopy(record)))
        return "mock://layer/run"


class FailingBillingBackend(MockProductionBackend):
    def audit_billing(self, result):
        self.events.append(("billing", result["kind"]))
        return {"status": "FAIL", "adapter": "billing"}


class FakeSolverModel:
    def __init__(self) -> None:
        self.native_calls = 0

    def optimize(self):
        self.native_calls += 1

    def optimizeAsync(self):
        raise AssertionError("native optimizeAsync must never run")

    def optimizeBatch(self):
        raise AssertionError("native optimizeBatch must never run")

    def tune(self):
        raise AssertionError("native tune must never run")


class ProductionSuccessorStackV73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.before = worktree_status()
        cls.payload = stack.run_successor_stack(ROOT)
        cls.after = worktree_status()
        cls.expected_identity = authority.load_accepted_v7_3_annual_input(ROOT).identity
        cls.frozen_authority = {
            "status": "PRODUCTION_AUTHORITY_FROZEN",
            "branch": "thesis-v7",
            "head": "mock-committed-and-pushed-head",
            "origin_head": "mock-committed-and-pushed-head",
            "annual_identity": cls.expected_identity.as_dict(),
        }

    def passing_snapshot(self) -> stack.DeploymentSnapshot:
        return stack.DeploymentSnapshot(
            branch="thesis-v7",
            head="future-2e-a-commit",
            origin_head="future-2e-a-commit",
            step2e1_is_ancestor=True,
            successor_bytes_committed=True,
            tracked_unstaged_changes=False,
            staged_changes=False,
            authority_hashes_valid=True,
            authority_error=None,
            accepted_identity=self.expected_identity,
            csv_fallback_possible=False,
            authority_untracked_paths=(),
        )

    def test_complete_stack_passes_with_exact_zero_solve_counters(self) -> None:
        self.assertEqual(self.payload["status"], "PASS")
        self.assertEqual(
            self.payload["verdict"],
            "MACRO GATE 2E-A SUCCESSOR STACK PREFLIGHT PASS",
        )
        counters = self.payload["execution_counters"]
        self.assertEqual(counters["model_constructions"], 0)
        self.assertEqual(counters["optimization_calls"], 0)
        self.assertEqual(counters["economic_evaluations"], 0)
        self.assertEqual(counters["forbidden_attempts"], [])

    def test_all_eight_accepted_authority_hashes_are_exact(self) -> None:
        observed = self.payload["authority_integrity"]
        expected = {
            "framework": "44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a",
            "registry": "e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d",
            "lifecycle": "23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d",
            "provenance_protocol": "c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696",
            "accepted_r3_parquet": "3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428",
            "production_input_authority_v7_3": "f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1",
            "step2e1_preflight": "3d99a4200dce93cd00db94727f72489d9be497eb52c74270a1c49b17fc8a7e95",
            "step2e1_test": "a039ae6620be859dfc7279e35b0b6bf0630e553f1e130fd27a330f9d337f22a6",
        }
        self.assertEqual(set(observed), set(expected))
        self.assertEqual(
            {label: record["sha256"] for label, record in observed.items()},
            expected,
        )

    def test_preflight_does_not_create_or_change_worktree_paths(self) -> None:
        self.assertEqual(self.before, self.after)

    def test_eob_successor_uses_only_explicit_r3_authority_and_unchanged_core(self) -> None:
        eob = self.payload["eob"]
        self.assertEqual(eob["annual_identity"], self.expected_identity.as_dict())
        self.assertEqual(eob["authority_module"], stack.AUTHORITY_MODULE)
        self.assertEqual(
            eob["explicit_annual_parquet"],
            authority.ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
        )
        self.assertEqual(
            eob["explicit_impossible_csv"],
            authority.IMPOSSIBLE_CSV_RELATIVE_PATH.as_posix(),
        )
        self.assertFalse(eob["csv_fallback"])
        self.assertFalse(eob["legacy_annual_default"])
        self.assertFalse(eob["historical_methodology"]["kappa_recalibrated"])
        self.assertEqual(eob["core_version"], stack.CORE_VERSION)
        self.assertFalse((ROOT / eob["explicit_impossible_csv"]).exists())

    def test_reused_eob_layer_a_and_final81_dependencies_match_head(self) -> None:
        evidence = self.payload["protected_methodology"]
        expected = {path.as_posix() for path in stack.PROTECTED_METHODOLOGY_PATHS}
        self.assertEqual(set(evidence), expected)
        self.assertTrue(all(item["matches_head"] for item in evidence.values()))
        for required in (
            "scripts/15a_benchmark_eob_charge_discharge_formulations.py",
            "scripts/15b_freeze_production_eob_baseline.py",
            "scripts/15c_validate_production_eob_rainflow.py",
            "scripts/15d_run_corrected_eob_v7_2.py",
            "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            "scripts/19a_preflight_final_layer_a_81_cases.py",
            "scripts/19b_run_final_layer_a_81_cases.py",
        ):
            self.assertIn(required, evidence)

    def test_layer_a_exact_grid_equations_bindings_and_valid_starts(self) -> None:
        layer = self.payload["layer_a"]
        self.assertEqual(layer["alpha_grid"], list(stack.ALPHAS))
        self.assertEqual(layer["beta_grid_h"], list(stack.BETAS_H))
        self.assertEqual(layer["case_count"], 81)
        self.assertEqual(layer["eta_d"], 0.90)
        self.assertEqual(
            layer["deficit_equation"],
            "max(alpha * baseline_load_kw - pv_available_kw, 0)",
        )
        self.assertEqual(layer["p_out_equation"], "max_t(deficit_t)")
        self.assertEqual(
            layer["valid_start_counts"],
            {beta: 8760 - beta + 1 for beta in range(4, 13)},
        )
        self.assertTrue(layer["non_circular"])
        self.assertTrue(layer["binding_windows_present"])
        self.assertEqual(
            layer["monotonicity"],
            {"power": "PASS", "reserve_over_beta": "PASS", "reserve_over_alpha": "PASS"},
        )
        self.assertFalse(layer["surplus_pv_recharge"])
        self.assertTrue(
            all(case["valid_start_count"] == 8760 - case["beta_h"] + 1 for case in layer["cases"])
        )

    def test_representative_plan_supports_core_three_and_historical_boundaries(self) -> None:
        final81 = self.payload["final81"]
        self.assertEqual(
            [case["case_id"] for case in stack.select_cases(final81, "core3")],
            ["a0.60_b04", "a0.80_b08", "a1.00_b12"],
        )
        self.assertEqual(
            {case["case_id"] for case in stack.select_cases(final81, "historical5")},
            {"a0.60_b04", "a0.60_b12", "a0.80_b08", "a1.00_b04", "a1.00_b12"},
        )
        self.assertEqual(
            [case["case_id"] for case in stack.select_production_cases(final81, "core-three")],
            ["a0.60_b04", "a0.80_b08", "a1.00_b12"],
        )

    def test_final81_has_complete_unique_grid_and_same_identity_in_every_context(self) -> None:
        final81 = self.payload["final81"]
        cases = final81["cases"]
        self.assertEqual(final81["case_count"], 81)
        self.assertEqual(final81["unique_case_count"], 81)
        self.assertEqual(len({case["case_id"] for case in cases}), 81)
        self.assertEqual(
            {(case["alpha"], case["beta_h"]) for case in cases},
            {(alpha, beta) for alpha in stack.ALPHAS for beta in stack.BETAS_H},
        )
        for case in cases:
            self.assertEqual(case["authority_module"], stack.AUTHORITY_MODULE)
            self.assertFalse(case["surplus_pv_recharge"])
            self.assertEqual(
                set(case["annual_identities"]),
                {"requirements", "model_input", "analytical_replay", "billing_economics_context"},
            )
            self.assertTrue(
                all(
                    identity == self.expected_identity.as_dict()
                    for identity in case["annual_identities"].values()
                )
            )

    def test_future_solver_settings_and_historical_adapters_are_frozen_not_executed(self) -> None:
        final81 = self.payload["final81"]
        self.assertEqual(
            final81["solver_settings_future_contract"], stack.LAYER_A_SOLVER_SETTINGS
        )
        self.assertEqual(final81["solver_settings_future_contract"]["MIPGap"], 1e-6)
        self.assertEqual(final81["solver_settings_future_contract"]["TimeLimit"], "INFINITY_UNSET")
        self.assertEqual(final81["solver_settings_future_contract"]["MIPFocus"], 0)
        self.assertEqual(final81["solver_settings_future_contract"]["Threads"], 0)
        self.assertEqual(final81["execution"]["cases_solved"], 0)
        definitions = set()
        for source in final81["accepted_future_adapters"]["sources"]:
            tree = ast.parse((ROOT / source).read_text(encoding="utf-8"))
            definitions.update(
                node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            )
        for name in final81["accepted_future_adapters"]["names"]:
            self.assertIn(name, definitions)

    def test_execute_production_rejects_before_any_preflight_or_dependency_check(self) -> None:
        with patch.object(stack, "verify_protected_methodology") as dependencies, patch.object(
            stack, "run_accepted_routing_preflight"
        ) as accepted:
            with self.assertRaises(stack.ProductionExecutionNotAuthorized):
                stack.run_successor_stack(ROOT, execute_production=True)
            dependencies.assert_not_called()
            accepted.assert_not_called()

    def test_current_real_execution_fails_before_native_backend_creation(self) -> None:
        with patch.object(stack, "NativeProductionBackend") as native_backend:
            with self.assertRaisesRegex(
                stack.ProductionAuthorityError, "not committed in HEAD"
            ) as caught:
                stack.run_eob_production(ROOT, execute_production=True)
            self.assertEqual(caught.exception.status, "PRODUCTION_AUTHORITY_NOT_YET_FROZEN")
            native_backend.assert_not_called()

    def test_mock_eob_future_path_executes_exactly_one_complete_wiring_chain(self) -> None:
        backend = MockProductionBackend(self.expected_identity)
        publisher = MockProductionPublisher()
        result = stack._execute_eob_authorized(
            authority=self.frozen_authority,
            eob_preflight=self.payload["eob"],
            backend=backend,
            publisher=publisher,
        )
        self.assertEqual(result["optimization_calls"], 1)
        self.assertEqual(backend.model_constructions, 1)
        self.assertEqual(backend.optimization_calls, 1)
        self.assertEqual(
            backend.events[0],
            (
                "solve_eob",
                {
                    "mode": "binary",
                    "MIPGap": 1e-6,
                    "TimeLimit": None,
                    "NumericFocus": 1,
                    "MIPFocus": 0,
                    "Threads": 0,
                    "OutputFlag": 1,
                },
            ),
        )
        self.assertEqual(
            [event[0] for event in backend.events[1:]],
            ["solver", "physical", "billing", "transition", "cost", "degradation", "rainflow"],
        )
        self.assertEqual([event[0] for event in publisher.events], ["publish_eob"])
        published = publisher.events[0][1]
        self.assertEqual(published["annual_identity"], self.expected_identity.as_dict())
        self.assertEqual(set(published["audits"]), set(stack.MANDATORY_EOB_AUDITS))

    def test_mock_core_three_path_executes_three_complete_case_chains(self) -> None:
        backend = MockProductionBackend(self.expected_identity)
        publisher = MockProductionPublisher()
        result = stack._execute_layer_a_authorized(
            authority=self.frozen_authority,
            final81=self.payload["final81"],
            case_set="core-three",
            backend=backend,
            publisher=publisher,
        )
        self.assertEqual(result["case_count"], 3)
        self.assertEqual(result["unique_case_count"], 3)
        self.assertEqual(result["optimization_calls"], 3)
        self.assertEqual(backend.model_constructions, 3)
        self.assertEqual(backend.optimization_calls, 3)
        solves = [event[1] for event in backend.events if event[0] == "solve_layer_a"]
        self.assertEqual(
            [(item["alpha"], item["beta_h"]) for item in solves],
            [(0.60, 4), (0.80, 8), (1.00, 12)],
        )
        accepted_cases = {
            case["case_id"]: case
            for case in stack.select_production_cases(
                self.payload["final81"], "core-three"
            )
        }
        for request in solves:
            self.assertEqual(
                request["settings"],
                {
                    "mode": "binary",
                    "MIPGap": 1e-6,
                    "TimeLimit": None,
                    "NumericFocus": 1,
                    "MIPFocus": 0,
                    "Threads": 0,
                    "OutputFlag": 0,
                },
            )
            self.assertEqual(
                set(request["annual_identities"]),
                {"requirements", "model_input", "analytical_replay", "billing_economics_context"},
            )
            self.assertTrue(
                all(
                    identity == self.expected_identity.as_dict()
                    for identity in request["annual_identities"].values()
                )
            )
            accepted = accepted_cases[request["case_id"]]
            self.assertEqual(request["R_kwh_battery"], accepted["R_kwh_battery"])
            self.assertEqual(request["P_out_kw_ac"], accepted["P_out_kw_ac"])
        audit_event_names = [event[0] for event in backend.events]
        for name in stack.MANDATORY_LAYER_A_AUDITS:
            self.assertEqual(audit_event_names.count(name), 3)
        self.assertEqual(
            [event[0] for event in publisher.events],
            [
                "begin_layer_run",
                "publish_layer_case",
                "publish_layer_case",
                "publish_layer_case",
                "complete_layer_run",
            ],
        )
        for _, record in [event for event in publisher.events if event[0] == "publish_layer_case"]:
            self.assertEqual(set(record["audits"]), set(stack.MANDATORY_LAYER_A_AUDITS))

    def test_full81_future_schedule_has_one_slot_per_unique_accepted_case(self) -> None:
        cases = stack.select_production_cases(self.payload["final81"], "full81")
        schedule = stack.build_execution_schedule(cases, self.expected_identity)
        self.assertEqual(len(schedule), 81)
        self.assertEqual(len({item["case"]["case_id"] for item in schedule}), 81)
        self.assertEqual(
            {(item["case"]["alpha"], item["case"]["beta_h"]) for item in schedule},
            {(alpha, beta) for alpha in stack.ALPHAS for beta in stack.BETAS_H},
        )
        self.assertTrue(all(item["expected_native_optimizations"] == 1 for item in schedule))
        self.assertTrue(
            all(item["annual_identity"] == self.expected_identity.as_dict() for item in schedule)
        )

    def test_deployment_gate_pass_fixture_and_all_repository_failures(self) -> None:
        passed = stack.validate_deployment_snapshot(
            self.passing_snapshot(), execute_production=True, selected_scope="core-three"
        )
        self.assertEqual(passed["status"], "PRODUCTION_AUTHORITY_FROZEN")
        cases = (
            ("no_execute", {}, False, "core-three", "Explicit --execute-production"),
            ("missing_scope", {}, True, None, "explicit fixed production case scope"),
            ("wrong_branch", {"branch": "main"}, True, "core-three", "Expected branch"),
            ("missing_ancestor", {"step2e1_is_ancestor": False}, True, "core-three", "not an ancestor"),
            ("uncommitted", {"successor_bytes_committed": False}, True, "core-three", "not committed"),
            ("tracked_dirty", {"tracked_unstaged_changes": True}, True, "core-three", "Tracked unstaged"),
            ("staged", {"staged_changes": True}, True, "core-three", "Staged changes"),
            ("not_pushed", {"origin_head": "older"}, True, "core-three", "does not equal"),
            ("hash_failure", {"authority_hashes_valid": False, "authority_error": "hash mismatch"}, True, "core-three", "hash mismatch"),
            ("csv", {"csv_fallback_possible": True}, True, "core-three", "CSV fallback"),
            ("untracked_authority", {"authority_untracked_paths": ("scripts/untracked.py",)}, True, "core-three", "Untracked authority-surface"),
        )
        for name, changes, execute, scope, message in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(stack.ProductionAuthorityError, message):
                    stack.validate_deployment_snapshot(
                        replace(self.passing_snapshot(), **changes),
                        execute_production=execute,
                        selected_scope=scope,
                    )

    def test_deployment_gate_rejects_r3_sha_role_and_legacy_path(self) -> None:
        for name, changed in (
            ("wrong_sha", replace(self.expected_identity, sha256="f" * 64)),
            ("wrong_role", replace(self.expected_identity, artifact_role="sensitivity_only")),
            (
                "legacy_path",
                replace(
                    self.expected_identity,
                    path="data/processed/annual_input_v7_1.parquet",
                ),
            ),
        ):
            with self.subTest(name=name):
                snapshot = replace(self.passing_snapshot(), accepted_identity=changed)
                with self.assertRaises(stack.ProductionAuthorityError):
                    stack.validate_deployment_snapshot(
                        snapshot,
                        execute_production=True,
                        selected_scope="core-three",
                    )

    def test_execution_schedule_rejects_outside_duplicate_missing_and_mismatch(self) -> None:
        original = stack.select_production_cases(self.payload["final81"], "core-three")
        outside = deepcopy(original)
        outside[0]["alpha"] = 1.05
        with self.assertRaisesRegex(stack.ProductionAuthorityError, "outside accepted grid"):
            stack.build_execution_schedule(outside, self.expected_identity)

        duplicate = [deepcopy(original[0]), deepcopy(original[0])]
        with self.assertRaisesRegex(stack.ProductionAuthorityError, "Duplicate"):
            stack.build_execution_schedule(duplicate, self.expected_identity)

        missing = deepcopy(original)
        del missing[0]["R_kwh_battery"]
        with self.assertRaisesRegex(stack.ProductionAuthorityError, "lacks R_kwh_battery"):
            stack.build_execution_schedule(missing, self.expected_identity)

        mismatched = deepcopy(original)
        mismatched[0]["annual_identities"]["model_input"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(stack.ProductionAuthorityError, "different annual artifact"):
            stack.build_execution_schedule(mismatched, self.expected_identity)

    def test_one_solve_guard_blocks_repeats_async_batch_tune_and_displacement(self) -> None:
        native = FakeSolverModel.optimize
        model = FakeSolverModel()
        guard = stack.OneSolveExecutionGuard(FakeSolverModel, native)
        with guard:
            with self.assertRaisesRegex(stack.ProductionAuthorityError, "Unauthorized"):
                model.optimize()
            guard.arm(model)
            model.optimize()
            self.assertEqual(model.native_calls, 1)
            with self.assertRaisesRegex(stack.ProductionAuthorityError, "Unauthorized"):
                model.optimize()
            for name in ("optimizeAsync", "optimizeBatch", "tune"):
                with self.subTest(name=name):
                    with self.assertRaisesRegex(stack.ProductionAuthorityError, "forbidden"):
                        getattr(model, name)()
            with patch.object(FakeSolverModel, "optimize", lambda self: None):
                with self.assertRaisesRegex(stack.ProductionAuthorityError, "displacement"):
                    guard.assert_intact()
        self.assertEqual(guard.calls, 1)

    def test_publication_is_not_reached_when_mandatory_audit_fails(self) -> None:
        backend = FailingBillingBackend(self.expected_identity)
        publisher = MockProductionPublisher()
        with self.assertRaisesRegex(stack.ProductionAuthorityError, "Mandatory audits failed"):
            stack._execute_eob_authorized(
                authority=self.frozen_authority,
                eob_preflight=self.payload["eob"],
                backend=backend,
                publisher=publisher,
            )
        self.assertEqual(publisher.events, [])

    def test_requirements_model_replay_and_billing_identity_mismatches_fail_closed(self) -> None:
        for context, field, value in (
            ("requirements", "path", "data/processed/annual_input_v7_1.parquet"),
            ("model_input", "sha256", authority.HISTORICAL_ANNUAL_SHA256),
            ("analytical_replay", "artifact_role", authority.WINTER_SENSITIVITY_ROLE),
            ("billing_economics_context", "row_count", 8759),
            ("requirements", "fingerprint_sha256", "f" * 64),
        ):
            cases = deepcopy(self.payload["final81"]["cases"])
            cases[0]["annual_identities"][context][field] = value
            with self.subTest(context=context, field=field):
                with self.assertRaisesRegex(
                    stack.SuccessorPreflightError,
                    "different annual artifact identity",
                ):
                    stack.validate_final81_case_plan(cases, self.expected_identity)

    def test_authority_bypass_missing_role_and_surplus_recharge_fail_closed(self) -> None:
        cases = deepcopy(self.payload["final81"]["cases"])
        cases[0]["authority_module"] = "direct_parquet_loader"
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "authority was bypassed"):
            stack.validate_final81_case_plan(cases, self.expected_identity)

        cases = deepcopy(self.payload["final81"]["cases"])
        del cases[0]["annual_identities"]["requirements"]["artifact_role"]
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "identity is incomplete"):
            stack.validate_final81_case_plan(cases, self.expected_identity)

        cases = deepcopy(self.payload["final81"]["cases"])
        cases[0]["surplus_pv_recharge"] = True
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "surplus-PV semantics"):
            stack.validate_final81_case_plan(cases, self.expected_identity)

    def test_arbitrary_altered_r3_path_is_rejected_by_accepted_authority(self) -> None:
        altered = ROOT / "data/processed/renamed_r3.parquet"
        with self.assertRaisesRegex(
            authority.ProductionInputAuthorityError,
            "requires the exact accepted parquet path",
        ):
            authority.load_accepted_v7_3_annual_input(ROOT, parquet_path=altered)

    def test_missing_duplicate_or_altered_grid_cases_fail_closed(self) -> None:
        cases = deepcopy(self.payload["final81"]["cases"])
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "exactly 81"):
            stack.validate_final81_case_plan(cases[:-1], self.expected_identity)

        cases[-1] = deepcopy(cases[0])
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "duplicated"):
            stack.validate_final81_case_plan(cases, self.expected_identity)

    def test_eob_layer_a_or_final81_top_level_identity_mismatch_fails_closed(self) -> None:
        altered_layer = deepcopy(self.payload["layer_a"])
        altered_layer["annual_identity"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(stack.SuccessorPreflightError, "different annual artifact identity"):
            stack.validate_stack_same_artifact(
                self.payload["eob"], altered_layer, self.payload["final81"]
            )

    def test_real_future_solve_route_exists_only_in_shared_guarded_backend(self) -> None:
        forbidden_native_entries = {
            "optimize",
            "optimizeAsync",
            "optimizeBatch",
            "tune",
        }
        for path in NEW_SOURCES:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            forbidden_calls = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and (
                    (isinstance(node.func, ast.Name) and node.func.id in forbidden_native_entries)
                    or (
                        isinstance(node.func, ast.Attribute)
                        and node.func.attr in forbidden_native_entries
                    )
                )
            ]
            with self.subTest(path=path.name):
                self.assertEqual(forbidden_calls, [])
                self.assertNotIn("annual_input_v7_1", source)
                self.assertNotIn("read_csv", source)
        shared = NEW_SOURCES[0].read_text(encoding="utf-8")
        self.assertIn("self.core.solve_eob", shared)
        self.assertIn("OneSolveExecutionGuard", shared)
        self.assertIn("NativeProductionBackend", shared)

    def test_all_cli_defaults_are_non_solving_and_explicit_flag_is_required(self) -> None:
        for index, path in enumerate(NEW_SOURCES[1:], start=1):
            module = load_script(path, f"successor_cli_{index}")
            self.assertFalse(module.parse_args([]).execute_production)
            self.assertTrue(module.parse_args(["--execute-production"]).execute_production)
            if path.name.startswith(("21c", "21d")):
                self.assertEqual(
                    module.parse_args(["--case-set", "core-three"]).case_set,
                    "core-three",
                )
                with self.assertRaises(SystemExit):
                    module.parse_args(["--alpha", "0.8", "--beta", "8"])

    def test_all_cli_execute_requests_fail_closed_without_changing_worktree(self) -> None:
        before = worktree_status()
        for path in NEW_SOURCES[1:]:
            command = [sys.executable, "-B", str(path), "--execute-production"]
            if path.name.startswith(("21c", "21d")):
                command.extend(["--case-set", "core-three"])
            command.append("--compact")
            completed = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            with self.subTest(path=path.name):
                self.assertEqual(completed.returncode, 2)
                payload = json.loads(completed.stdout)
                self.assertEqual(
                    payload["status"], "PRODUCTION_AUTHORITY_NOT_YET_FROZEN"
                )
                self.assertIn("not committed in HEAD", payload["error"])
                self.assertFalse(payload["production_execution_attempted"])
                self.assertEqual(payload["execution_counters"]["model_constructions"], 0)
                self.assertEqual(payload["execution_counters"]["optimization_calls"], 0)
                self.assertEqual(payload["execution_counters"]["economic_evaluations"], 0)
        self.assertEqual(before, worktree_status())

    def test_direct_same_identity_guard_rejects_eob_layer_a_difference(self) -> None:
        changed = replace(self.expected_identity, sha256="0" * 64)
        with self.assertRaises(authority.ProductionInputAuthorityError):
            authority.require_same_annual_identity(
                self.expected_identity,
                changed,
                consumer="eob_layer_a",
            )


def eob_result_fixture() -> dict:
    """Solver-free stand-in for a solved EOB result bundle (no Gurobi, no model)."""
    return {
        "kind": "eob",
        "has_solution": True,
        "objective": 66_623_000.0,
        "mip_gap": 0.0,
        "unbounded_probe": float("inf"),
        "status_name": "OPTIMAL",
        "schedule": pd.DataFrame({"t": [0, 1], "p_kw": [1.5, -2.5]}),
    }


def passing_audits(names) -> dict:
    return {name: {"status": "PASS", "adapter": name} for name in names}


class JsonSafeSerializationTests(unittest.TestCase):
    """Section 6A — historical accepted serialization semantics."""

    def test_scalars_paths_containers_and_numpy_round_trip(self) -> None:
        self.assertIsNone(stack._json_safe(None))
        self.assertEqual(stack._json_safe("text"), "text")
        self.assertIs(stack._json_safe(True), True)
        self.assertIs(stack._json_safe(False), False)
        self.assertEqual(stack._json_safe(7), 7)
        self.assertEqual(stack._json_safe(1.25), 1.25)
        self.assertIsNone(stack._json_safe(float("nan")))
        self.assertIsNone(stack._json_safe(float("inf")))
        self.assertIsNone(stack._json_safe(float("-inf")))
        self.assertEqual(stack._json_safe(Path("a/b.json")), str(Path("a/b.json")))
        self.assertEqual(
            stack._json_safe({"k": Path("x"), 2: [1.0, float("nan")]}),
            {"k": str(Path("x")), "2": [1.0, None]},
        )
        self.assertEqual(stack._json_safe((1, "a", None)), [1, "a", None])
        self.assertEqual(stack._json_safe([{"n": float("inf")}]), [{"n": None}])

    def test_numpy_scalars_are_unwrapped_and_non_finite_becomes_null(self) -> None:
        self.assertEqual(stack._json_safe(np.int64(5)), 5)
        self.assertEqual(stack._json_safe(np.float64(2.5)), 2.5)
        self.assertIs(stack._json_safe(np.bool_(True)), True)
        self.assertIsNone(stack._json_safe(np.float64("nan")))
        self.assertIsNone(stack._json_safe(np.float64("inf")))

    def test_unknown_objects_degrade_to_string_never_raise(self) -> None:
        class Opaque:
            def __repr__(self) -> str:
                return "<opaque>"

        self.assertEqual(stack._json_safe(Opaque()), "<opaque>")

    def test_every_json_safe_output_is_json_serialisable(self) -> None:
        payload = stack._json_safe(eob_result_fixture() | {"path": Path("p")})
        json.loads(json.dumps(payload))


class ExclusiveJsonTests(unittest.TestCase):
    """Section 6B — the exact helper whose missing dependency broke publication."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_writes_non_empty_parsable_json(self) -> None:
        target = self.tmp / "authority.json"
        stack._exclusive_json(target, {"status": "PRODUCTION_AUTHORITY_FROZEN"})
        self.assertGreater(target.stat().st_size, 0)
        self.assertEqual(
            json.loads(target.read_text(encoding="utf-8")),
            {"status": "PRODUCTION_AUTHORITY_FROZEN"},
        )

    def test_regression_zero_byte_file_is_never_left_behind(self) -> None:
        target = self.tmp / "regression.json"
        stack._exclusive_json(target, {"a": float("inf"), "b": np.float64(1.5)})
        self.assertNotEqual(target.stat().st_size, 0)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"a": None, "b": 1.5})

    def test_exclusive_create_semantics_reject_overwrite(self) -> None:
        target = self.tmp / "once.json"
        stack._exclusive_json(target, {"first": True})
        with self.assertRaises(FileExistsError):
            stack._exclusive_json(target, {"second": True})
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"first": True})


class FilesystemPublisherEobTests(unittest.TestCase):
    """Section 6C/6D — the REAL publisher, never exercised by the 2E-A stub."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.publisher = stack.FilesystemProductionPublisher(self.root)
        self.runs = self.root / stack.EOB_PRODUCTION_ROOT
        self.record = {
            "authority": {"status": "PRODUCTION_AUTHORITY_FROZEN", "branch": "thesis-v7"},
            "annual_identity": {"artifact_role": authority.ACCEPTED_ARTIFACT_ROLE},
            "solver_settings": {"MIPGap": 1e-6, "TimeLimit": None, "NumericFocus": 1},
            "result": eob_result_fixture(),
            "audits": passing_audits(stack.MANDATORY_EOB_AUDITS),
        }

    def pending(self) -> list[Path]:
        return sorted(self.runs.glob(".pending_eob_*")) if self.runs.exists() else []

    def test_publish_eob_writes_complete_authoritative_bundle(self) -> None:
        final = Path(self.publisher.publish_eob(self.record))

        self.assertTrue(final.is_dir())
        self.assertEqual(self.pending(), [], "staging directory must not survive success")
        for name in (
            "authority.json",
            "solver_settings.json",
            "result.json",
            "mandatory_audits.json",
            "completion_manifest.json",
            "schedule.csv",
        ):
            with self.subTest(artifact=name):
                self.assertTrue((final / name).is_file())
                self.assertGreater((final / name).stat().st_size, 0)

        manifest = json.loads((final / "completion_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE")
        self.assertEqual(manifest["optimization_calls"], 1)
        self.assertEqual(sorted(manifest["mandatory_audits"]), sorted(stack.MANDATORY_EOB_AUDITS))

        audits = json.loads((final / "mandatory_audits.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(audits), sorted(stack.MANDATORY_EOB_AUDITS))
        self.assertTrue(all(entry["status"] == "PASS" for entry in audits.values()))

        result = json.loads((final / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["objective"], 66_623_000.0)
        self.assertIsNone(result["unbounded_probe"], "non-finite floats must serialize as null")
        self.assertNotIn("schedule", result, "DataFrames belong in the CSV bundle")

    def test_published_artifact_registry_matches_bytes_on_disk(self) -> None:
        final = Path(self.publisher.publish_eob(self.record))
        manifest = json.loads((final / "completion_manifest.json").read_text(encoding="utf-8"))
        registry = manifest["artifact_registry"]

        self.assertNotIn("completion_manifest.json", registry)
        self.assertEqual(
            sorted(registry),
            sorted(
                path.relative_to(final).as_posix()
                for path in final.rglob("*")
                if path.is_file() and path.name != "completion_manifest.json"
            ),
        )
        for relative, identity in registry.items():
            with self.subTest(artifact=relative):
                self.assertEqual(authority.sha256_file(final / relative), identity["sha256"])
                self.assertEqual((final / relative).stat().st_size, identity["bytes"])
        stack._verify_artifact_registry(final, registry)

    def test_registry_verification_detects_post_publication_mutation(self) -> None:
        final = Path(self.publisher.publish_eob(self.record))
        registry = json.loads(
            (final / "completion_manifest.json").read_text(encoding="utf-8")
        )["artifact_registry"]
        (final / "result.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(stack.SuccessorPreflightError):
            stack._verify_artifact_registry(final, registry)

    def test_failed_publication_leaves_valid_failure_manifest_and_no_authority(self) -> None:
        def boom(directory, result):
            raise RuntimeError("injected publication failure")

        with patch.object(stack, "_write_result_bundle", boom):
            with self.assertRaises(RuntimeError):
                self.publisher.publish_eob(self.record)

        staging = self.pending()
        self.assertEqual(len(staging), 1, "failed staging evidence must be retained")
        self.assertEqual(
            [path for path in self.runs.iterdir() if not path.name.startswith(".pending_eob_")],
            [],
            "a failed publication must never produce an authoritative run directory",
        )

        failure = staging[0] / "failure_manifest.json"
        self.assertGreater(failure.stat().st_size, 0, "failure manifest must not be zero bytes")
        payload = json.loads(failure.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "PUBLICATION_FAILED")
        self.assertFalse(payload["authoritative"])
        self.assertFalse((staging[0] / "completion_manifest.json").exists())
        self.assertFalse((staging[0] / "result.json").exists())
        self.assertGreater((staging[0] / "authority.json").stat().st_size, 0)

    def test_two_publications_never_collide_or_share_a_directory(self) -> None:
        first = Path(self.publisher.publish_eob(self.record))
        second = Path(self.publisher.publish_eob(deepcopy(self.record)))
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_dir() and second.is_dir())
        self.assertEqual(self.pending(), [])


class FilesystemPublisherLayerATests(unittest.TestCase):
    """Section 6E — the same serializer defect blocked Layer-A publication."""

    CASE_IDS = ("LOW", "CENTRAL", "HIGH")

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.publisher = stack.FilesystemProductionPublisher(self.root)
        self.runs = self.root / stack.LAYER_A_PRODUCTION_ROOT

    def case_record(self, case_id: str, alpha: float, beta_h: int) -> dict:
        return {
            "case": {"case_id": case_id, "alpha": alpha, "beta_h": beta_h, "eta_d": stack.ETA_D},
            "solver_settings": {"MIPGap": 1e-6, "TimeLimit": None},
            "result": {
                "kind": "layer_a",
                "case_id": case_id,
                "has_solution": True,
                "objective": 1.0e6 + beta_h,
                "dispatch": pd.DataFrame({"t": [0, 1], "soc": [0.5, 0.6]}),
            },
            "audits": passing_audits(stack.MANDATORY_LAYER_A_AUDITS),
        }

    def test_full_core_three_run_publishes_and_clears_staging(self) -> None:
        run = self.publisher.begin_layer_run(
            {
                "authority": {"status": "PRODUCTION_AUTHORITY_FROZEN"},
                "schedule": [{"case_id": case_id} for case_id in self.CASE_IDS],
            }
        )
        staging = Path(run["staging"])
        self.assertGreater((staging / "authority.json").stat().st_size, 0)
        self.assertGreater((staging / "case_schedule.json").stat().st_size, 0)

        for case_id, alpha, beta_h in (("LOW", 0.60, 4), ("CENTRAL", 0.80, 8), ("HIGH", 1.00, 12)):
            case_dir = Path(self.publisher.publish_layer_case(run, self.case_record(case_id, alpha, beta_h)))
            case_manifest = json.loads(
                (case_dir / "completion_manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(case_manifest["status"], "COMPLETE_PASS")
            self.assertEqual(case_manifest["case_id"], case_id)
            self.assertEqual(case_manifest["optimization_calls"], 1)
            self.assertEqual(
                sorted(case_manifest["mandatory_audits"]), sorted(stack.MANDATORY_LAYER_A_AUDITS)
            )
            for relative, identity in case_manifest["artifact_registry"].items():
                self.assertEqual(authority.sha256_file(case_dir / relative), identity["sha256"])

        final = Path(
            self.publisher.complete_layer_run(
                run, {"case_ids": list(self.CASE_IDS), "case_set": "core_three"}
            )
        )

        self.assertTrue(final.is_dir())
        self.assertEqual(sorted(self.runs.glob(".pending_layer_a_*")), [])
        manifest = json.loads((final / "completion_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE")
        self.assertEqual(manifest["case_set"], "core_three")
        self.assertEqual(manifest["case_count"], 3)
        self.assertEqual(manifest["case_ids"], list(self.CASE_IDS))
        self.assertEqual(manifest["optimization_calls"], 3)
        stack._verify_artifact_registry(final, manifest["artifact_registry"])
        for case_id in self.CASE_IDS:
            self.assertTrue((final / "cases" / case_id / "result.json").is_file())

    def test_case_surface_drift_fails_closed_without_publishing_run(self) -> None:
        run = self.publisher.begin_layer_run(
            {"authority": {}, "schedule": [{"case_id": case_id} for case_id in self.CASE_IDS]}
        )
        self.publisher.publish_layer_case(run, self.case_record("LOW", 0.60, 4))
        with self.assertRaises(stack.SuccessorPreflightError):
            self.publisher.complete_layer_run(
                run, {"case_ids": list(self.CASE_IDS), "case_set": "core_three"}
            )
        self.assertEqual(len(sorted(self.runs.glob(".pending_layer_a_*"))), 1)
        self.assertFalse(Path(run["final"]).exists())


class PublicationDefectRegressionTests(unittest.TestCase):
    """Guards the exact 2026-09-24 failure mode against reintroduction."""

    def test_stack_module_has_no_undefined_module_level_names(self) -> None:
        source = (ROOT / "src/production_successor_stack_v7_3.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        defined: set[str] = set(dir(builtins))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    defined.add((alias.asname or alias.name).split(".")[0])
            elif isinstance(node, (ast.arg,)):
                defined.add(node.arg)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                defined.add(node.name)
            elif isinstance(node, ast.Global):
                defined.update(node.names)

        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        missing = sorted(name for name in called if name not in defined)
        self.assertEqual(missing, [], f"undefined called names in successor stack: {missing}")

    def test_json_safe_is_defined_in_the_publication_module(self) -> None:
        self.assertTrue(callable(getattr(stack, "_json_safe", None)))

    def test_math_isfinite_contract_matches_historical_15d_helper(self) -> None:
        historical = load_script(
            ROOT / "scripts/15d_run_corrected_eob_v7_2.py", "historical_15d_for_serializer_parity"
        )
        for value in (
            None, "s", True, False, 0, 13, 1.5, -0.0,
            float("nan"), float("inf"), float("-inf"),
            Path("a/b"), {"k": [1, (2, 3)]}, (1, 2), [Path("p")],
            np.float64(3.5), np.int64(4), np.float64("nan"),
        ):
            with self.subTest(value=repr(value)):
                self.assertEqual(stack._json_safe(value), historical._json_safe(value))
        self.assertTrue(math.isfinite(1.0))


if __name__ == "__main__":
    unittest.main()
