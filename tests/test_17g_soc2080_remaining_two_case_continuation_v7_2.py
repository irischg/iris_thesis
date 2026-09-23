"""Build-only tests for the fixed two-case SOC2080 continuation runner.

The suite uses AST inspection, accepted-hash reads, synthetic dictionaries,
temporary directories, in-memory artifact stores, and a fake solver API.  It
constructs no real optimization model and invokes no real solver.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import inspect
import io
import sys
import unittest
import uuid
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    ROOT / "scripts/17g_run_soc2080_remaining_two_case_continuation.py"
)


def load_runner():
    name = f"_test_soc2080_remaining_two_continuation_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load continuation runner.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


class TestFixedCaseAuthority(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.static = cls.runner.validate_static_authority(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.runner.__name__, None)

    def test_exact_two_case_universe_comes_from_accepted_17e(self) -> None:
        accepted, diagnostic = self.runner.load_accepted_modules(ROOT)
        try:
            cases = self.runner.accepted_continuation_cases(accepted)
            self.assertEqual(tuple(case.case_id for case in cases), self.runner.FIXED_CASE_IDS)
            self.assertEqual(len(cases), 2)
        finally:
            sys.modules.pop(diagnostic.__name__, None)
            sys.modules.pop(accepted.__name__, None)

    def test_exact_alpha_beta_identities(self) -> None:
        observed = {
            item["case_id"]: (item["alpha"], item["beta_h"])
            for item in self.static["fixed_case_universe"]
        }
        self.assertEqual(observed, {"a1.00_b04": (1.00, 4), "a1.00_b12": (1.00, 12)})

    def test_order_is_fixed(self) -> None:
        self.assertEqual(self.runner.FIXED_CASE_IDS, ("a1.00_b04", "a1.00_b12"))
        self.assertEqual(self.static["attempt_order"], ["a1.00_b04", "a1.00_b12"])

    def test_cli_has_no_case_alpha_beta_list_or_output_selector(self) -> None:
        args = self.runner.parse_args([])
        self.assertFalse(args.execute_continuation)
        forbidden = (
            "--case",
            "--cases",
            "--alpha",
            "--beta",
            "--beta-h",
            "--output-root",
            "--config",
            "--eob",
            "--comparator",
        )
        for option in forbidden:
            with self.subTest(option=option):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        self.runner.parse_args([option, "anything"])

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

    def test_all_direct_dependency_pins_match_live_bytes(self) -> None:
        records = self.runner.validate_dependency_pins(ROOT)
        expected = {
            "annual_core": "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
            "rainflow_validator": "4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2",
            "soc2080_adapter": "11cfc8167683d7204955f7b0b583ed026889b3ca0629902ff08dc92be3bb6304",
            "representative_helper_16a_r12": "5813119e258e83a45a245ec715ade4536bf9dbf880687f6d3f1e978cce8b06a0",
            "accepted_soc2080_runner_17e_r2": "2d8cc520a499851b2cfdc85dafa655accace5aee05d74dc31b851af75c5ffe5d",
            "accepted_a080_b08_diagnostic_17f_r1": "a8ec2250ed4a4bffcd79e2e57c93df29b1762c07baa9b109a1e0e2b3f02e30b0",
            "rainflow_review_gate_owner_adjudication": "d26198c3afa147bac2cb0d3f0ec75defbf1f0e6922fbfe13c35d4e319032c253",
        }
        for label, digest in expected.items():
            with self.subTest(label=label):
                self.assertEqual(records[label]["expected_sha256"], digest)
                self.assertEqual(records[label]["actual_sha256"], digest)
                self.assertEqual(records[label]["status"], "PASS")

    def test_static_authority_is_zero_model_zero_solve(self) -> None:
        self.assertEqual(
            self.static["status"],
            "CONTINUATION_BUILD_STATIC_AUTHORITY_PASS_NO_MODEL_NO_SOLVE",
        )
        contract = self.static["solve_count_contract"]
        self.assertEqual(contract["actual_optimize_calls_this_validation"], 0)
        self.assertFalse(self.static["continuation_execution_authorized_by_build_pass"])
        self.assertFalse(self.static["eligible_for_production_completion"])

    def test_transitive_authority_covers_17d_input_package_and_freezes(self) -> None:
        transitive = self.static["accepted_17e_transitive_pins"]
        self.assertIn("authoritative_comparator_pin_source", transitive)
        self.assertIn("canonical_annual_input", transitive)
        self.assertIn("economic_interface", transitive)
        self.assertIn("pnnl_cyclelife_provenance", transitive)
        self.assertEqual(
            set(self.static["accepted_17d_comparator_pins"]),
            set(self.runner.FIXED_CASE_IDS),
        )
        self.assertEqual(
            self.static["parent_adjudication_authority"]["actual_sha256"],
            "d26198c3afa147bac2cb0d3f0ec75defbf1f0e6922fbfe13c35d4e319032c253",
        )


class TestOptimizeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.source = RUNNER_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.accepted, cls.diagnostic = cls.runner.load_accepted_modules(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.diagnostic.__name__, None)
        sys.modules.pop(cls.accepted.__name__, None)
        sys.modules.pop(cls.runner.__name__, None)

    @staticmethod
    def fake_gurobi():
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

        return FakeGurobi, FakeModel

    def test_budget_constants_are_exact(self) -> None:
        self.assertEqual(self.runner.EXPECTED_CONTINUATION_OPTIMIZE_CALLS, 2)
        self.assertEqual(self.runner.MAXIMUM_CONTINUATION_OPTIMIZE_CALLS, 2)
        self.assertEqual(self.runner.MAXIMUM_OPTIMIZE_CALLS_PER_CASE, 1)

    def test_fake_guard_allows_exactly_two_in_order(self) -> None:
        fake_gp, fake_model = self.fake_gurobi()
        first = fake_model()
        second = fake_model()
        with self.runner.RemainingTwoOptimizeGuard(self.accepted, fake_gp) as guard:
            guard.solve_once("a1.00_b04", first.optimize)
            guard.solve_once("a1.00_b12", second.optimize)
            guard.assert_exact_total()
            self.assertEqual(guard.count, 2)
            self.assertEqual(guard.attempted_case_ids, self.runner.FIXED_CASE_IDS)
        self.assertEqual(first.synthetic_calls, 1)
        self.assertEqual(second.synthetic_calls, 1)

    def test_third_fake_optimize_is_structurally_rejected(self) -> None:
        fake_gp, fake_model = self.fake_gurobi()
        with self.runner.RemainingTwoOptimizeGuard(self.accepted, fake_gp) as guard:
            guard.solve_once("a1.00_b04", fake_model().optimize)
            guard.solve_once("a1.00_b12", fake_model().optimize)
            with self.assertRaises(self.runner.ContinuationAuthorityError):
                guard.solve_once("a1.00_b04", fake_model().optimize)
            self.assertEqual(guard.count, 2)

    def test_repeated_or_out_of_order_case_is_rejected_before_fake_solve(self) -> None:
        fake_gp, fake_model = self.fake_gurobi()
        model = fake_model()
        with self.runner.RemainingTwoOptimizeGuard(self.accepted, fake_gp) as guard:
            with self.assertRaises(self.runner.ContinuationAuthorityError):
                guard.solve_once("a1.00_b12", model.optimize)
            self.assertEqual(model.synthetic_calls, 0)
            guard.solve_once("a1.00_b04", model.optimize)
            with self.assertRaises(self.runner.ContinuationAuthorityError):
                guard.solve_once("a1.00_b04", model.optimize)
            self.assertEqual(model.synthetic_calls, 1)

    def test_alternate_solver_methods_are_forbidden(self) -> None:
        fake_gp, fake_model = self.fake_gurobi()
        model = fake_model()
        with self.runner.RemainingTwoOptimizeGuard(self.accepted, fake_gp):
            with self.assertRaises(Exception):
                model.tune()
            with self.assertRaises(Exception):
                model.optimizeAsync()
        self.assertEqual(model.synthetic_calls, 0)

    def test_comparator_and_reference_eob_optimize_budgets_are_zero(self) -> None:
        self.assertEqual(self.runner.EXPECTED_COMPARATOR_OPTIMIZE_CALLS, 0)
        self.assertEqual(self.runner.EXPECTED_REFERENCE_EOB_OPTIMIZE_CALLS, 0)

    def test_execution_ast_has_one_solve_site_inside_fixed_sequence(self) -> None:
        execute = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "execute_continuation"
        )
        solve_calls = [
            node
            for node in ast.walk(execute)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "solve_eob"
        ]
        self.assertEqual(len(solve_calls), 1)
        segment = ast.get_source_segment(self.source, execute) or ""
        self.assertIn("execute_fixed_case_sequence(cases, attempt_case)", segment)
        self.assertNotIn("while ", segment)

    def test_no_module_level_gurobi_import_or_direct_optimize_call(self) -> None:
        top_imports: list[str] = []
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                top_imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                top_imports.append(node.module)
        self.assertNotIn("gurobipy", top_imports)
        direct_calls = [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "optimize"
        ]
        self.assertEqual(direct_calls, [])

    def test_no_retry_fallback_tuning_or_feasibility_relaxation_path(self) -> None:
        lowered = self.source.lower()
        self.assertNotIn("retry_solver", lowered)
        self.assertNotIn("fallback_solver", lowered)
        self.assertNotIn("feasrelax(", lowered)
        self.assertNotIn("feasrelaxs(", lowered)
        self.assertNotIn(".tune(", lowered)

    def test_fixed_sequence_stops_on_execution_exception_without_retry(self) -> None:
        cases = [SimpleNamespace(case_id=item) for item in self.runner.FIXED_CASE_IDS]
        calls: list[str] = []

        def attempt(case):
            calls.append(case.case_id)
            if case.case_id == "a1.00_b12":
                raise RuntimeError("synthetic infrastructure failure")
            return case.case_id

        with self.assertRaises(RuntimeError):
            self.runner.execute_fixed_case_sequence(cases, attempt)
        self.assertEqual(calls, ["a1.00_b04", "a1.00_b12"])


class TestCaseLocalTriStatePolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.accepted, cls.diagnostic = cls.runner.load_accepted_modules(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.diagnostic.__name__, None)
        sys.modules.pop(cls.accepted.__name__, None)
        sys.modules.pop(cls.runner.__name__, None)

    def exercise(self, gates: dict[str, str]):
        events: list[tuple[str, str]] = []
        raw = self.runner.serialize_case_validation(
            gates,
            self.accepted.classify_post_solve_authority,
            lambda status, state: events.append((status, state)),
        )
        return events, raw

    def test_pass_is_serialized_and_retained(self) -> None:
        events, raw = self.exercise({"rainflow": "PASS", "other": "PASS"})
        self.assertEqual(raw, "PASS")
        self.assertEqual(events, [(self.runner.CASE_EVIDENCE_STATUS["PASS"], "PASS")])

    def test_review_is_serialized_without_promotion(self) -> None:
        events, raw = self.exercise({"rainflow": "REVIEW", "other": "PASS"})
        self.assertEqual(raw, "REVIEW")
        self.assertEqual(events, [(self.runner.CASE_EVIDENCE_STATUS["REVIEW"], "REVIEW")])

    def test_hard_fail_overrides_review_and_is_serialized(self) -> None:
        events, raw = self.exercise({"rainflow": "REVIEW", "other": "FAIL"})
        self.assertEqual(raw, "FAIL")
        self.assertEqual(events, [(self.runner.CASE_EVIDENCE_STATUS["FAIL"], "FAIL")])

    def test_unknown_state_fails_closed_and_is_serialized(self) -> None:
        events, raw = self.exercise({"rainflow": "UNKNOWN"})
        self.assertEqual(raw, "FAIL")
        self.assertEqual(events, [(self.runner.CASE_EVIDENCE_STATUS["FAIL"], "FAIL")])

    def test_case_one_review_does_not_cancel_case_two_attempt(self) -> None:
        gates = [
            {"rainflow": "REVIEW", "other": "PASS"},
            {"rainflow": "PASS", "other": "PASS"},
        ]
        states = [self.exercise(item)[1] for item in gates]
        self.assertEqual(states, ["REVIEW", "PASS"])

    def test_case_one_hard_validation_fail_does_not_cancel_case_two_attempt(self) -> None:
        gates = [
            {"rainflow": "REVIEW", "other": "FAIL"},
            {"rainflow": "PASS", "other": "PASS"},
        ]
        states = [self.exercise(item)[1] for item in gates]
        self.assertEqual(states, ["FAIL", "PASS"])

    def test_classifier_hard_fail_precedence_is_accepted_17e_behavior(self) -> None:
        state = self.accepted.classify_post_solve_authority(
            {"review_gate": "REVIEW", "hard_gate": "FAIL"}
        )
        self.assertEqual(state, "FAIL")

    def test_recognized_outage_validation_fail_becomes_raw_fail_evidence(self) -> None:
        class FakeAuthority:
            class SocSensitivityAuthorityError(RuntimeError):
                pass

            @staticmethod
            def outage_replay_audit(_annual, _requirement, _sizing):
                raise FakeAuthority.SocSensitivityAuthorityError(
                    "SOC2080 outage replay failed: "
                    "{'all_start_power': False, 'no_circular_wrap': True}"
                )

        audit, starts = self.runner.capture_outage_replay_evidence(
            FakeAuthority(), object(), {}, {}
        )
        self.assertEqual(audit["status"], "FAIL")
        self.assertFalse(audit["checks"]["all_start_power"])
        self.assertFalse(audit["scientific_formula_reimplemented_by_17g"])
        self.assertIsNone(starts)

    def test_unrecognized_outage_exception_remains_whole_run_failure(self) -> None:
        class FakeAuthority:
            class SocSensitivityAuthorityError(RuntimeError):
                pass

            @staticmethod
            def outage_replay_audit(_annual, _requirement, _sizing):
                raise FakeAuthority.SocSensitivityAuthorityError(
                    "unexpected authority state"
                )

        with self.assertRaises(FakeAuthority.SocSensitivityAuthorityError):
            self.runner.capture_outage_replay_evidence(
                FakeAuthority(), object(), {}, {}
            )


class TestScientificReuseAndArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()
        cls.source = RUNNER_PATH.read_text(encoding="utf-8")
        cls.static = cls.runner.validate_static_authority(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.runner.__name__, None)

    def test_soc_and_solver_contract_are_reused_exactly(self) -> None:
        self.assertEqual(self.static["soc_window"]["soc_min"], 0.20)
        self.assertEqual(self.static["soc_window"]["soc_max"], 0.80)
        self.assertEqual(self.static["soc_window"]["usable_fraction"], 0.60)
        self.assertEqual(self.static["active_segment_widths"], [0.30, 0.30, 0.0])
        self.assertEqual(self.static["solver_contract"]["MIPGap"], 1e-6)
        self.assertFalse(self.static["solver_contract"]["automatic_retry"])

    def test_scientific_functions_are_delegated_to_accepted_authority(self) -> None:
        required = (
            "accepted_continuation_cases(accepted_17e)",
            "accepted_17e.load_isolated_r10_soc_core",
            "helper.analytical_surface",
            "accepted_17e.required_nameplate_energy_kwh",
            "accepted_17e.validate_soc_rainflow",
            "helper.billing_structure_audit",
            "accepted_17e.base_post_solve_gates",
            "helper.representative_gate",
            "capture_outage_replay_evidence",
            "accepted_17e.write_case_artifacts",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.source)

    def test_solver_settings_use_accepted_17e_contract_values(self) -> None:
        required = (
            "mip_gap=accepted_17e.MIP_GAP",
            "time_limit_sec=accepted_17e.TIME_LIMIT_SEC",
            "output_flag=accepted_17e.OUTPUT_FLAG",
            "numeric_focus=accepted_17e.NUMERIC_FOCUS",
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_normalized_case_artifacts_are_never_production_complete(self) -> None:
        artifacts = Path("synthetic-artifacts")

        class MemoryAuthority:
            def __init__(self) -> None:
                self.records = {
                    artifacts / "result.json": {
                        "runner_version": "accepted-17e",
                        "runner_sha256": "accepted-17e-hash",
                    },
                    artifacts / "post_solve_gates.json": {
                        "status": "PASS",
                        "eligible_for_run_completion": True,
                    },
                }

            def read_json(self, path: Path):
                return deepcopy(self.records[path])

            def write_json(self, path: Path, payload, *, exclusive: bool = True):
                if exclusive and path in self.records:
                    raise AssertionError(f"synthetic exclusive overwrite: {path}")
                self.records[path] = deepcopy(payload)

        for raw in ("PASS", "REVIEW", "FAIL"):
            with self.subTest(raw=raw):
                memory = MemoryAuthority()
                case = SimpleNamespace(case_id="a1.00_b04", alpha=1.00, beta_h=4)
                self.runner.normalize_continuation_artifacts(
                    memory,
                    artifacts,
                    case=case,
                    live={
                        "runner_sha256": "candidate-hash",
                        "parent_adjudication_authority": {"actual_sha256": "parent"},
                    },
                    evidence_status=self.runner.CASE_EVIDENCE_STATUS[raw],
                    raw_state=raw,
                    billing={"period_ids": "PASS"},
                    result={"transition_settlement": {"certificate": "PASS"}},
                    reference_eob={"role": "SOC2080_REFERENCE_EOB_REUSE_ONLY"},
                )
                result = memory.records[artifacts / "result.json"]
                gates = memory.records[artifacts / "post_solve_gates.json"]
                boundary = memory.records[artifacts / "continuation_authority.json"]
                self.assertEqual(result["raw_validation_state"], raw)
                self.assertFalse(result["eligible_for_production_completion"])
                self.assertFalse(gates["eligible_for_run_completion"])
                self.assertFalse(gates["eligible_for_production_completion"])
                self.assertFalse(boundary["eligible_for_production_completion"])
                self.assertFalse(boundary["step_11c_completion"])

    def test_run_manifest_has_attempt_and_production_boundaries(self) -> None:
        fake_17e = SimpleNamespace(SCRIPT_VERSION="accepted-17e")
        live = {
            "runner_sha256": "runner",
            "accepted_17e_sha256": "17e",
            "parent_adjudication_authority": {"actual_sha256": "parent"},
            "dependency_pins": {},
            "accepted_17e_transitive_pins": {},
            "accepted_17d_comparator_pins": {},
            "reference_eob": {},
        }
        payload = self.runner._run_manifest_payload(
            run_id="synthetic",
            live=live,
            repository={"status": "PASS"},
            accepted_17e=fake_17e,
            case_records=self.runner.initial_case_records(),
            actual_optimize_calls=0,
            status="EVIDENCE_CAPTURE_STARTED_NOT_PRODUCTION_ACCEPTED",
            execution_level_failure=False,
        )
        self.assertEqual(payload["fixed_case_universe"], list(self.runner.FIXED_CASE_IDS))
        self.assertEqual(payload["expected_optimize_calls"], 2)
        self.assertEqual(payload["maximum_optimize_calls"], 2)
        self.assertFalse(payload["eligible_for_production_completion"])
        self.assertFalse(payload["step_11c_completion"])

    def test_complete_primary_artifact_family_is_declared(self) -> None:
        accepted, diagnostic = self.runner.load_accepted_modules(ROOT)
        try:
            accepted_serializer_source = inspect.getsource(
                accepted.write_case_artifacts
            )
        finally:
            sys.modules.pop(diagnostic.__name__, None)
            sys.modules.pop(accepted.__name__, None)
        required = (
            "gurobi.log",
            "solver_telemetry.jsonl",
            "dispatch.csv",
            "billing_audit.json",
            "transition_settlement_audit.json",
            "rainflow_audit.json",
            "rainflow_cycles.csv",
            "rainflow_turning_points.csv",
            "outage_replay_audit.json",
            "post_solve_gates.json",
            "continuation_authority.json",
            "continuation_run_manifest.json",
            "continuation_evidence_capture_manifest.json",
        )
        for marker in required:
            with self.subTest(marker=marker):
                if marker in {"rainflow_cycles.csv", "rainflow_turning_points.csv"}:
                    self.assertIn(
                        '("cycles", "turning_points", "depth_bins", "pwl_segments", "g_curve")',
                        accepted_serializer_source,
                    )
                    self.assertIn('rainflow_{name}.csv', accepted_serializer_source)
                else:
                    self.assertTrue(
                        marker in self.source or marker in accepted_serializer_source,
                        marker,
                    )

    def test_historical_claim_boundary_is_exactly_non_retrospective(self) -> None:
        claim = self.runner.HISTORICAL_CLAIM_BOUNDARY
        self.assertIn("does not rewrite old runs", claim)
        self.assertIn("retroactively repair", claim)
        self.assertIn("UNRESOLVED / UNRECOVERABLE FROM PRESERVED EVIDENCE", claim)


class TestRepositoryAndNamespaceIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_runner()

    @classmethod
    def tearDownClass(cls) -> None:
        sys.modules.pop(cls.runner.__name__, None)

    def test_output_namespace_is_isolated(self) -> None:
        output = self.runner.continuation_output_root(ROOT)
        self.assertEqual(
            output,
            (ROOT / "results/continuation/soc2080_remaining_two/runs").resolve(),
        )

    def test_protected_historical_and_diagnostic_namespaces_are_rejected(self) -> None:
        original = self.runner.OUTPUT_ROOT_RELATIVE
        protected = (
            "results/sensitivity/soc_20_80/runs",
            "results/diagnostics/soc2080_a080_b08/runs",
            "results/layer_a/final_81",
        )
        try:
            for relative in protected:
                with self.subTest(relative=relative):
                    self.runner.OUTPUT_ROOT_RELATIVE = Path(relative)
                    with self.assertRaises(self.runner.ContinuationAuthorityError):
                        self.runner.continuation_output_root(ROOT)
        finally:
            self.runner.OUTPUT_ROOT_RELATIVE = original

    def test_run_directory_is_exclusive_no_resume_or_overwrite(self) -> None:
        class FakeRunPath:
            def __init__(self, exists: bool) -> None:
                self._exists = exists
                self.mkdir_calls: list[dict[str, bool]] = []

            def exists(self) -> bool:
                return self._exists

            def mkdir(self, *, parents: bool, exist_ok: bool) -> None:
                self.mkdir_calls.append({"parents": parents, "exist_ok": exist_ok})

            def __str__(self) -> str:
                return "synthetic-run-path"

        new_path = FakeRunPath(False)
        self.runner.create_exclusive_run_directory(new_path)
        self.assertEqual(
            new_path.mkdir_calls, [{"parents": True, "exist_ok": False}]
        )
        existing_path = FakeRunPath(True)
        with self.assertRaises(self.runner.ContinuationAuthorityError):
            self.runner.create_exclusive_run_directory(existing_path)
        self.assertEqual(existing_path.mkdir_calls, [])

    def test_current_untracked_build_state_cannot_receive_execution_authority(self) -> None:
        accepted, diagnostic = self.runner.load_accepted_modules(ROOT)
        try:
            tracked = []
            for relative in (self.runner.RUNNER_RELATIVE, self.runner.TEST_RELATIVE):
                try:
                    accepted.git_text(ROOT, "ls-files", "--error-unmatch", relative.as_posix())
                    tracked.append(True)
                except Exception:
                    tracked.append(False)
            if all(tracked):
                self.skipTest("candidate files are already tracked; build-state gate no longer applies")
            with self.assertRaises(self.runner.ContinuationAuthorityError):
                self.runner.execution_repository_authority(ROOT, accepted)
        finally:
            sys.modules.pop(diagnostic.__name__, None)
            sys.modules.pop(accepted.__name__, None)

    def test_synthetic_authority_mismatch_stops_before_any_execution_action(self) -> None:
        events: list[str] = []

        class RejectingAuthority:
            def production_repository_authority(self, _root):
                events.append("authority_checked")
                raise RuntimeError("synthetic mismatch")

            def git_text(self, *_args):
                events.append("tracked_check")
                return ""

        with self.assertRaises(self.runner.ContinuationAuthorityError):
            self.runner.execution_repository_authority(ROOT, RejectingAuthority())
        self.assertEqual(events, ["authority_checked"])


if __name__ == "__main__":
    unittest.main()
