"""Build-only tests for the single-case SOC2080 a0.80_b08 diagnostic runner.

These tests use source inspection, synthetic dictionaries, temporary JSON,
and a fake solver class.  They construct no optimization model and invoke no
real solver.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import sys
import unittest
import uuid
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts/17f_run_soc2080_a080_b08_diagnostic.py"


def load_runner():
    name = f"_test_soc2080_a080_b08_diagnostic_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load diagnostic runner.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


class TestDiagnosticCaseAndAuthority(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.runner.__name__, None)

    def test_case_identity_comes_from_accepted_17e_and_is_unique(self) -> None:
        accepted = self.runner.load_accepted_17e(ROOT)
        try:
            case = self.runner.accepted_diagnostic_case(accepted)
            self.assertEqual(case.case_id, "a0.80_b08")
            self.assertEqual(case.alpha, 0.80)
            self.assertEqual(case.beta_h, 8)
            self.assertEqual(self.runner.DIAGNOSTIC_CASE_ID, case.case_id)
        finally:
            sys.modules.pop(accepted.__name__, None)

    def test_cli_has_no_arbitrary_case_or_alpha_beta_selector(self) -> None:
        args = self.runner.parse_args([])
        self.assertFalse(args.execute_diagnostic)
        for forbidden in ("--case", "--alpha", "--beta", "--beta-h"):
            with self.subTest(forbidden=forbidden):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        self.runner.parse_args([forbidden, "anything"])

    def test_default_path_never_calls_executor(self) -> None:
        events: list[str] = []

        def validator(_root: Path) -> dict[str, object]:
            events.append("validated")
            return {"status": "STATIC", "eligible_for_production_completion": False}

        def executor(_root: Path, _authority: dict[str, object]) -> Path:
            events.append("executed")
            raise AssertionError("default build-only path reached executor")

        with contextlib.redirect_stdout(io.StringIO()):
            code = self.runner.run([], root=ROOT, validator=validator, executor=executor)
        self.assertEqual(code, 0)
        self.assertEqual(events, ["validated"])

    def test_all_required_dependency_pins_match_current_bytes(self) -> None:
        records = self.runner.validate_dependency_pins(ROOT)
        expected = {
            "annual_core": "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
            "rainflow_validator": "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2",
            "soc2080_adapter": "11cfc8167683d7204955f7b0b583ed026889b3ca0629902ff08dc92be3bb6304",
            "representative_helper_16a_r12": "5813119e258e83a45a245ec715ade4536bf9dbf880687f6d3f1e978cce8b06a0",
            "accepted_soc2080_runner_17e_r2": "2d8cc520a499851b2cfdc85dafa655accace5aee05d74dc31b851af75c5ffe5d",
            "correction_authority_freeze": "f8f74f4281187d67115c2e66abb942ccafebe237ae68d7ea6ad7af65d4724116",
        }
        for label, digest in expected.items():
            with self.subTest(label=label):
                self.assertEqual(records[label]["expected_sha256"], digest)
                self.assertEqual(records[label]["actual_sha256"], digest)
                self.assertEqual(records[label]["status"], "PASS")

    def test_static_authority_reuses_exact_scientific_contract(self) -> None:
        record = self.runner.validate_static_authority(ROOT)
        self.assertEqual(
            record["status"], "DIAGNOSTIC_BUILD_STATIC_AUTHORITY_PASS_NO_MODEL_NO_SOLVE"
        )
        self.assertEqual(record["case"]["case_id"], "a0.80_b08")
        self.assertEqual(record["case"]["definition_source"], "scripts/17e_run_soc_window_sensitivity.py")
        self.assertEqual(record["soc_window"]["soc_min"], 0.20)
        self.assertEqual(record["soc_window"]["soc_max"], 0.80)
        self.assertEqual(record["soc_window"]["usable_fraction"], 0.60)
        self.assertEqual(record["active_segment_widths"], [0.30, 0.30, 0.0])
        self.assertEqual(record["solver_contract"]["MIPGap"], 1e-6)
        self.assertFalse(record["solver_contract"]["automatic_retry"])
        self.assertEqual(record["solve_count_contract"]["actual_optimize_calls_this_validation"], 0)
        self.assertFalse(record["eligible_for_production_completion"])


class TestOptimizeAndSingleSolveStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.source = RUNNER_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.runner.__name__, None)

    def test_future_guard_allows_one_fake_call_and_blocks_more(self) -> None:
        class FakeModel:
            def __init__(self) -> None:
                self.synthetic_calls = 0

            def optimize(self) -> None:
                self.synthetic_calls += 1

            def optimizeAsync(self) -> None:
                raise AssertionError("original alternate method must not run")

            def tune(self) -> None:
                raise AssertionError("original tuning method must not run")

        class FakeGurobi:
            Model = FakeModel

        accepted = self.runner.load_accepted_17e(ROOT)
        try:
            model = FakeModel()
            with self.runner.SingleDiagnosticOptimizeGuard(accepted, FakeGurobi) as guard:
                before = guard.count
                model.optimize()
                guard.assert_one_new_call(before)
                guard.assert_exact_total()
                self.assertEqual(model.synthetic_calls, 1)
                with self.assertRaises(Exception):
                    model.optimize()
                with self.assertRaises(Exception):
                    model.tune()
                self.assertEqual(guard.count, 1)
                self.assertEqual(model.synthetic_calls, 1)
        finally:
            sys.modules.pop(accepted.__name__, None)

    def test_execution_ast_has_one_solve_call_and_no_comparator_path(self) -> None:
        execute = next(
            node
            for node in self.tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "execute_diagnostic"
        )
        calls = [node for node in ast.walk(execute) if isinstance(node, ast.Call)]
        solve_calls = [
            node
            for node in calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "solve_eob"
        ]
        self.assertEqual(len(solve_calls), 1)
        forbidden = {
            "recover_authoritative_comparator_pins",
            "verify_comparators",
            "load_comparator_result",
            "execute_production",
        }
        called_names = {
            node.func.attr
            for node in calls
            if isinstance(node.func, ast.Attribute)
        } | {node.func.id for node in calls if isinstance(node.func, ast.Name)}
        self.assertTrue(forbidden.isdisjoint(called_names))
        self.assertNotIn("for case in", ast.get_source_segment(self.source, execute) or "")

    def test_no_module_level_gurobi_import_or_direct_optimize_call(self) -> None:
        top_imports = []
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                top_imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                top_imports.append(node.module)
        self.assertNotIn("gurobipy", top_imports)
        direct_optimize_calls = [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "optimize"
        ]
        self.assertEqual(direct_optimize_calls, [])

    def test_constants_encode_exact_budget(self) -> None:
        self.assertEqual(self.runner.EXPECTED_DIAGNOSTIC_OPTIMIZE_CALLS, 1)
        self.assertEqual(self.runner.MAXIMUM_DIAGNOSTIC_OPTIMIZE_CALLS, 1)
        self.assertEqual(self.runner.EXPECTED_COMPARATOR_OPTIMIZE_CALLS, 0)


class TestTriStateSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.accepted = cls.runner.load_accepted_17e(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.accepted.__name__, None)
        sys.modules.pop(cls.runner.__name__, None)

    def _exercise(self, gates: dict[str, str]) -> tuple[list[tuple[str, str]], object]:
        events: list[tuple[str, str]] = []

        def serializer(terminal: str, state: str) -> None:
            events.append((terminal, state))

        try:
            value: object = self.runner.classify_and_serialize_diagnostic(
                gates,
                self.accepted.classify_post_solve_authority,
                serializer,
                Path("diagnostic_terminal_manifest.json"),
            )
        except self.runner.DiagnosticTerminalOutcome as exc:
            value = exc
        return events, value

    def test_pass_is_serialized_and_preserved(self) -> None:
        events, outcome = self._exercise({"rainflow": "PASS", "other": "PASS"})
        self.assertEqual(events, [("DIAGNOSTIC_PASS", "PASS")])
        self.assertEqual(outcome, "DIAGNOSTIC_PASS")

    def test_review_is_serialized_before_enforcement(self) -> None:
        events, outcome = self._exercise({"rainflow": "REVIEW", "other": "PASS"})
        self.assertEqual(events, [("DIAGNOSTIC_REVIEW_REQUIRED", "REVIEW")])
        self.assertIsInstance(outcome, self.runner.DiagnosticTerminalOutcome)

    def test_hard_fail_overrides_review_and_is_serialized(self) -> None:
        events, outcome = self._exercise({"rainflow": "REVIEW", "other": "FAIL"})
        self.assertEqual(events, [("DIAGNOSTIC_GATE_FAILED", "FAIL")])
        self.assertIsInstance(outcome, self.runner.DiagnosticTerminalOutcome)

    def test_unknown_state_fails_closed_after_serialization(self) -> None:
        events, outcome = self._exercise({"rainflow": "UNKNOWN"})
        self.assertEqual(events, [("DIAGNOSTIC_GATE_FAILED", "FAIL")])
        self.assertIsInstance(outcome, self.runner.DiagnosticTerminalOutcome)


class TestDiagnosticArtifactsAndIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.accepted = cls.runner.load_accepted_17e(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.accepted.__name__, None)
        sys.modules.pop(cls.runner.__name__, None)

    def test_normalized_artifacts_can_never_be_production_complete(self) -> None:
        for validation, terminal in self.runner.TERMINAL_STATES.items():
            with self.subTest(validation=validation):
                artifacts = Path("synthetic-artifacts")

                class MemoryAuthority:
                    def __init__(self) -> None:
                        self.records = {
                            artifacts / "result.json": {
                                "runner_version": "accepted-17e",
                                "runner_sha256": "accepted-serializer-hash",
                                "accepted_comparator": {"should": "be removed"},
                            },
                            artifacts / "post_solve_gates.json": {
                                "status": validation,
                                "eligible_for_run_completion": True,
                            },
                        }

                    def read_json(self, path: Path) -> dict[str, object]:
                        return deepcopy(self.records[path])

                    def write_json(
                        self,
                        path: Path,
                        payload: dict[str, object],
                        *,
                        exclusive: bool = True,
                    ) -> None:
                        if exclusive and path in self.records:
                            raise AssertionError(f"synthetic exclusive overwrite: {path}")
                        self.records[path] = deepcopy(payload)

                memory = MemoryAuthority()
                self.runner.normalize_diagnostic_artifacts(
                    memory,
                    artifacts,
                    live={"runner_sha256": "diagnostic-runner-hash"},
                    terminal_state=terminal,
                    validation_state=validation,
                    billing={"period_ids": "PASS"},
                    result={
                        "transition_settlement": {
                            "nonbinding_certificate": "PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE"
                        }
                    },
                    reference_eob={"role": "SOC2080_REFERENCE_EOB_REUSE_ONLY"},
                )
                result = memory.records[artifacts / "result.json"]
                gates = memory.records[artifacts / "post_solve_gates.json"]
                diagnostic = memory.records[artifacts / "diagnostic_authority.json"]
                self.assertFalse(result["eligible_for_production_completion"])
                self.assertFalse(gates["eligible_for_run_completion"])
                self.assertFalse(gates["eligible_for_production_completion"])
                self.assertFalse(diagnostic["eligible_for_production_completion"])
                self.assertNotIn("accepted_comparator", result)
                self.assertIn("UNRESOLVED / UNRECOVERABLE", result["historical_claim_boundary"])

    def test_output_is_dedicated_and_protected_namespaces_are_rejected(self) -> None:
        output = self.runner.diagnostic_output_root(ROOT)
        self.assertEqual(
            output,
            (ROOT / "results/diagnostics/soc2080_a080_b08/runs").resolve(),
        )
        original = self.runner.OUTPUT_ROOT_RELATIVE
        try:
            self.runner.OUTPUT_ROOT_RELATIVE = Path("results/sensitivity/soc_20_80/runs")
            with self.assertRaises(self.runner.DiagnosticAuthorityError):
                self.runner.diagnostic_output_root(ROOT)
        finally:
            self.runner.OUTPUT_ROOT_RELATIVE = original

    def test_no_production_completion_manifest_is_written(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertNotIn('"completion_manifest.json"', source)
        self.assertNotIn("'completion_manifest.json'", source)
        self.assertIn("diagnostic_terminal_manifest.json", source)
        self.assertIn('"eligible_for_production_completion": False', source)

    def test_complete_evidence_paths_and_accepted_serializer_are_present(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        required = (
            "write_case_artifacts",
            "solver_telemetry.jsonl",
            "gurobi.log",
            "dispatch.csv",
            "rainflow_audit.json",
            "billing_audit.json",
            "transition_settlement_audit.json",
            "outage_replay_audit.json",
            "post_solve_gates.json",
            "diagnostic_authority.json",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, source)

    def test_claim_boundary_is_explicit_and_non_retrospective(self) -> None:
        claim = self.runner.HISTORICAL_CLAIM_BOUNDARY
        self.assertIn("newly solved", claim)
        self.assertIn("does not reconstruct", claim)
        self.assertIn("UNRESOLVED / UNRECOVERABLE FROM PRESERVED EVIDENCE", claim)


if __name__ == "__main__":
    unittest.main()
