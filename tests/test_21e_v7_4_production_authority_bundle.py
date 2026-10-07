"""Static, no-solve tests for the additive V7.4 production-authority bundle.

Every test here is import-only / build-only / byte-verification.  No test in this
module constructs a model, calls an optimizer, runs a case, spawns a subprocess,
or creates a production run directory.  The production execution flag is never
written as a literal anywhere in this file, so no path here can be read as an
execution request.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lifecycle_mod  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


ALIGNMENT_SOURCES = (
    ROOT / "src/production_authority_bundle_v7_4.py",
    ROOT / "scripts/21e_preflight_v7_4_production_authority_alignment.py",
    ROOT / "src/production_authority_lifecycle_u06.py",
)


def live_lifecycle():
    """The live U-06 lifecycle state: currently ABSENT / NOT_FROZEN."""

    return lifecycle_mod.resolve_u06_lifecycle(ROOT)


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


class BundleIdentityTests(unittest.TestCase):
    """Section 1 — every claimed identity must reproduce from live bytes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.before = worktree_status()
        cls.lifecycle = live_lifecycle()
        cls.payload = bundle.verify_v7_4_authority_bundle(ROOT, cls.lifecycle)
        cls.after = worktree_status()

    def test_bundle_verifies_and_reports_candidate_alignment_only(self) -> None:
        self.assertEqual(self.payload["status"], "PASS")
        self.assertEqual(self.payload["alignment_status"], "CANDIDATE_ALIGNED")
        self.assertEqual(self.payload["bundle_version"], bundle.BUNDLE_VERSION)
        # Base identity never carries lifecycle authority (audit finding F-01).
        self.assertFalse(self.payload["lifecycle_authority_held_by_this_bundle"])
        self.assertEqual(
            self.payload["lifecycle_authority_module"],
            "src/production_authority_lifecycle_u06.py",
        )
        self.assertEqual(
            self.payload["u06_lifecycle"]["production_authority_freeze_status"],
            "NOT_FROZEN",
        )

    def test_every_pinned_hash_reproduces_from_live_bytes(self) -> None:
        report = bundle.verify_pin_table_against_live_bytes(ROOT)
        self.assertEqual(len(report), len(bundle.all_pins()))
        failures = {
            label: record
            for label, record in report.items()
            if not record["matches"]
        }
        self.assertEqual(failures, {})

    def test_pin_labels_are_unique(self) -> None:
        labels = [pin.label for pin in bundle.all_pins()]
        self.assertEqual(len(labels), len(set(labels)))

    def test_framework_and_registry_v7_4_are_exactly_bound(self) -> None:
        framework = self.payload["methodology_evidence_authority"]["framework_v7_4"]
        registry = self.payload["methodology_evidence_authority"]["registry_v7_4"]
        self.assertEqual(
            framework["path"], "docs/research_framework_v7_4_2026-09-26_r2.md"
        )
        self.assertEqual(
            framework["sha256"],
            "36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273",
        )
        self.assertEqual(
            registry["path"],
            "docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md",
        )
        self.assertEqual(
            registry["sha256"],
            "5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433",
        )

    def test_task_3_and_governance_successor_chains_are_bound(self) -> None:
        task_3 = self.payload["task_3_authority"]
        self.assertEqual(
            set(task_3),
            {
                "task_3_preregistration_candidate_r2",
                "task_3_preregistration_machine_record",
                "task_3_preregistration_acceptance_closure",
                "task_3_preregistration_acceptance_manifest",
            },
        )
        governance = self.payload["governance_sequencing_successor"]
        self.assertEqual(
            set(governance),
            {
                "governance_sequencing_successor_candidate_r2",
                "governance_sequencing_successor_acceptance_closure",
                "governance_sequencing_successor_acceptance_manifest",
                "governance_sequencing_successor_original_candidate",
            },
        )
        self.assertEqual(
            governance["governance_sequencing_successor_acceptance_closure"][
                "lifecycle"
            ],
            "CLOSED_ACCEPTED_PUBLISHED",
        )
        self.assertEqual(
            self.payload["governance_sequencing_successor_published_commit"],
            "fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0",
        )

    def test_canonical_input_model_core_registry_and_runner_are_bound(self) -> None:
        contract = self.payload["canonical_planning_input"]
        self.assertEqual(
            contract["path"],
            "data/processed/annual_input_v7_3_reconstructed_pv_mainline_"
            "candidate_r3_2026-09-23.parquet",
        )
        self.assertEqual(
            contract["sha256"],
            "3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428",
        )
        self.assertEqual(contract["expected_rows"], 8760)
        self.assertEqual(contract["expected_columns"], 51)
        self.assertEqual(contract["window_start"], "2024-11-01 00:00:00")
        self.assertEqual(contract["window_end_inclusive"], "2025-10-31 23:00:00")

        core = self.payload["model_core"]
        self.assertEqual(core["path"], "src/annual_design_model_v7_2.py")
        self.assertEqual(core["core_version"], stack.CORE_VERSION)
        self.assertFalse(core["equations_changed"])

        implementation = self.payload["implementation_authority"]
        self.assertEqual(
            implementation["parameter_registry"]["path"],
            "data/reference/parameter_registry_v7_2.csv",
        )
        surface = self.payload["alignment_surface"]
        self.assertEqual(
            surface["production_successor_stack"]["path"],
            "src/production_successor_stack_v7_3.py",
        )
        self.assertEqual(
            surface["full81_runner"]["path"],
            "scripts/21d_preflight_v7_3_final81_successor.py",
        )

    def test_declared_record_matches_the_verified_pins(self) -> None:
        declared = self.payload["declared_authority_record"]
        self.assertEqual(
            declared["framework"]["sha256"],
            self.payload["methodology_evidence_authority"]["framework_v7_4"]["sha256"],
        )
        self.assertEqual(
            declared["registry"]["sha256"],
            self.payload["methodology_evidence_authority"]["registry_v7_4"]["sha256"],
        )
        self.assertEqual(declared["framework"]["formal_name"], "Framework v7.4")
        self.assertEqual(declared["registry"]["formal_name"], "Registry v7.4")

    def test_declared_record_is_json_serializable_for_production_artifacts(self) -> None:
        encoded = json.dumps(
            stack._json_safe(bundle.declared_authority_record(self.lifecycle)),
            sort_keys=True,
        )
        self.assertIn("36dd1803", encoded)
        self.assertIn("5cc5d091", encoded)
        json.dumps(
            stack._json_safe(bundle.case_level_provenance(self.lifecycle)),
            sort_keys=True,
        )

    def test_verification_creates_or_changes_no_worktree_path(self) -> None:
        self.assertEqual(self.before, self.after)

    def test_missing_or_drifted_authority_fails_closed(self) -> None:
        with self.assertRaises(bundle.ProductionAuthorityBundleError):
            bundle.verify_v7_4_authority_bundle(ROOT / "tests", self.lifecycle)
        drifted = replace(bundle._pin("framework_v7_4"), sha256="f" * 64)
        with self.assertRaises(bundle.ProductionAuthorityBundleError) as caught:
            bundle._verify_pins(ROOT, (drifted,))
        self.assertEqual(caught.exception.status, "V7_4_AUTHORITY_HASH_FAIL")


class HistoricalV73PreservationTests(unittest.TestCase):
    """Section 2 — the historical v7.3 authority layer must stay intact."""

    def test_v7_3_module_still_pins_its_own_v7_3_methodology_trio(self) -> None:
        self.assertEqual(
            set(authority.AUTHORITY_FILES), {"methodology", "evidence", "lifecycle"}
        )
        self.assertEqual(
            authority.AUTHORITY_FILES["methodology"][0].as_posix(),
            "docs/research_framework_v7_3_2026-09-23.md",
        )
        self.assertEqual(
            authority.AUTHORITY_VERSION,
            "v7.3-production-input-authority-2026-09-24-r1",
        )

    def test_inherited_v7_3_pins_are_verified_as_historical_not_current(self) -> None:
        inherited = bundle.verify_v7_4_authority_bundle(ROOT, live_lifecycle())[
            "inherited_v7_3_historical_authority"
        ]
        self.assertEqual(
            set(inherited), {"v7_3_methodology", "v7_3_evidence", "v7_3_lifecycle"}
        )
        for record in inherited.values():
            self.assertEqual(record["lifecycle"], "CLOSED_ACCEPTED_HISTORICAL")
            self.assertIn("HISTORICAL_ACCEPTED_PREDECESSOR", record["role"])

    def test_accepted_frozen_v7_3_authority_integrity_surface_is_unchanged(self) -> None:
        """The frozen Macro-Gate-2E-A eight-key surface must not be rewritten."""

        observed = stack.run_successor_stack(ROOT)["authority_integrity"]
        self.assertEqual(
            set(observed),
            {
                "framework",
                "registry",
                "lifecycle",
                "provenance_protocol",
                "accepted_r3_parquet",
                "production_input_authority_v7_3",
                "step2e1_preflight",
                "step2e1_test",
            },
        )
        self.assertEqual(
            observed["framework"]["sha256"],
            "44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a",
        )


class GovernanceSemanticsTests(unittest.TestCase):
    """Section 3 — encoded governance state must match accepted authority."""

    def setUp(self) -> None:
        self.lifecycle = live_lifecycle()
        self.state = bundle.governance_state(self.lifecycle)

    def test_u_01_is_open_hold_and_does_not_block_main_full81(self) -> None:
        self.assertEqual(self.state["u_01_status"], "OPEN_HOLD")
        self.assertFalse(self.state["u_01_blocks_main_full81"])
        self.assertFalse(self.state["u_01_resolved_by_this_alignment"])
        self.assertEqual(
            self.state["u_01_must_be_frozen_before"],
            [
                "A2_EXECUTION",
                "A2_RESULT_EXPOSURE",
                "A2_INTERPRETATION",
                "A2_CONDITIONAL_EXTENSION_AUTHORIZATION",
            ],
        )
        self.assertNotIn("FULL81_AUTHORIZATION", self.state["u_01_must_be_frozen_before"])
        for event in (
            "MAIN_FULL81_AUTHORIZATION",
            "MAIN_FULL81_EXECUTION",
            "MAIN_FULL81_INTEGRITY_INSPECTION",
            "MAIN_FULL81_SCIENTIFIC_INSPECTION",
            "MAIN_FULL81_RESPONSE_SURFACE_ANALYSIS",
            "SUPERVISOR_DISCUSSION_OF_MAIN_FULL81",
        ):
            self.assertIn(event, self.state["u_01_does_not_block"])

    def test_a2_is_hard_blocked_with_zero_exposure(self) -> None:
        self.assertEqual(self.state["a2_status"], "HARD_BLOCKED")
        self.assertEqual(
            self.state["a2_result_exposure"],
            "ZERO_A2_RESULT_EXPOSURE_FIREWALL_INTACT",
        )
        self.assertFalse(self.state["a2_authorized_by_this_alignment"])
        self.assertFalse(self.state["a2_paired_difference_exposed"])
        self.assertFalse(self.state["a2_conditional_beta8_escalation_authorized"])

    def test_main_full81_is_not_authorized_by_this_alignment(self) -> None:
        self.assertEqual(self.state["main_full81_authorization"], "NOT_AUTHORIZED")
        self.assertFalse(self.state["main_full81_authorized_by_this_alignment"])
        self.assertEqual(
            self.state["main_full81_remaining_lifecycle"][0],
            "V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE",
        )

    def test_unresolved_register_and_u_07_are_not_silently_resolved(self) -> None:
        register = self.state["unresolved_register"]
        self.assertEqual(register["U-01"], "OPEN_HOLD")
        for item in ("U-02", "U-03", "U-04", "U-05"):
            self.assertEqual(register[item], "UNRESOLVED")
        self.assertEqual(register["U-07"], "UNRESOLVED_CLASSIFICATION")
        # R2-AUD-03 / R3-AUD-04. This asserted the pre-acceptance U-06 entry
        # was "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT" — the
        # ownership string of the HISTORICAL U-06 *alignment* generation. The
        # independent audit of Candidate R3 found that string being reported as
        # the ownership of the active preflight-authorization-guard candidate,
        # so this assertion was requiring the defect rather than catching it.
        # The entry is now candidate-neutral, and the historical string must
        # never be emitted as the active one.
        self.assertEqual(
            register["U-06"],
            bundle.ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY,
        )
        self.assertNotEqual(
            register["U-06"], bundle.HISTORICAL_U06_ALIGNMENT_REGISTER_ENTRY
        )
        # Ownership is carried in explicit fields, not inside the entry string.
        ownership = self.state["u06_register_state"]
        self.assertEqual(ownership["entry"], register["U-06"])
        self.assertTrue(ownership["entry_is_candidate_neutral"])
        self.assertEqual(ownership["candidate_audit_status"], "NOT_YET_PERFORMED")
        self.assertFalse(ownership["historical_u06_alignment_is_current"])
        self.assertFalse(
            ownership["historical_u06_alignment_register_entry_is_current"]
        )
        u_07 = self.state["u_07"]
        self.assertEqual(u_07["status"], "UNRESOLVED_CLASSIFICATION")
        self.assertEqual(u_07["scope"], "A2_ONLY")
        self.assertFalse(u_07["blocks_main_full81"])
        self.assertFalse(u_07["variable_floor_support_implemented"])
        self.assertFalse(u_07["annual_model_accepts_time_varying_reserve_floor"])
        self.assertFalse(u_07["resolved_by_this_alignment"])

    def test_no_threshold_is_selected(self) -> None:
        threshold = self.state["materiality_threshold"]
        self.assertIsNone(threshold["accepted_numerical_threshold"])
        self.assertIsNone(threshold["selected_threshold_option"])
        self.assertFalse(threshold["selected_by_this_alignment"])

    def test_cross_case_aggregation_is_recorded_not_implemented(self) -> None:
        aggregation = self.state["cross_case_aggregation"]
        self.assertFalse(aggregation["implemented_by_this_alignment"])
        self.assertFalse(aggregation["prerequisite_for_full81_execution"])
        self.assertIn("GAP_RECORDED", aggregation["status"])

    def test_alignment_is_mechanically_distinct_from_authorization(self) -> None:
        record = bundle.alignment_is_not_full81_authorization(self.lifecycle)
        self.assertEqual(
            record["production_authority_alignment"], "CANDIDATE_ALIGNED"
        )
        self.assertEqual(record["main_full81_authorization"], "NOT_AUTHORIZED")
        self.assertIsNone(record["main_full81_authorization_artifact"])
        self.assertFalse(record["alignment_implies_authorization"])
        self.assertTrue(record["separate_authorization_required"])
        self.assertEqual(
            record["next_required_gate"],
            "FRESH_INDEPENDENT_AUDIT_OF_THE_U_06_R2_CANDIDATE",
        )

    def test_output_namespace_is_preserved_not_renamed(self) -> None:
        self.assertEqual(
            bundle.ACCEPTED_OUTPUT_NAMESPACE,
            "results/layer_a/final_81_v7_3/runs/<unique-run-id>",
        )
        self.assertFalse(
            bundle.verify_v7_4_authority_bundle(ROOT, live_lifecycle())[
                "output_namespace"
            ]["renamed"]
        )


class FailClosedGuardTests(unittest.TestCase):
    """Section 4 — the guards must actually reject, not merely be documented."""

    def test_full81_scope_is_rejected_by_the_bundle_guard(self) -> None:
        with self.assertRaises(bundle.Full81AuthorizationNotGranted) as caught:
            bundle.require_full81_scope_authorization("full81")
        self.assertEqual(caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED")

    def test_every_a2_scope_token_is_rejected(self) -> None:
        for scope in (
            "a2",
            "A2",
            "robustness",
            "variable_floor",
            "variable-floor",
            "varfloor",
            "perfect_information",
            "a2_variable_floor_six_point",
        ):
            with self.subTest(scope=scope):
                with self.assertRaises(bundle.A2ExecutionHardBlocked) as caught:
                    bundle.require_a2_hard_block(scope)
                self.assertEqual(caught.exception.status, "A2_HARD_BLOCKED")

    def test_accepted_non_full81_scopes_are_not_newly_restricted(self) -> None:
        for scope in (
            "eob",
            "low",
            "central",
            "high",
            "core-three",
            "historical-five",
            None,
        ):
            with self.subTest(scope=scope):
                bundle.require_a2_hard_block(scope)
                bundle.require_full81_scope_authorization(scope)

    def test_production_gate_rejects_full81_and_a2_before_any_repository_check(
        self,
    ) -> None:
        """A fully clean repository must still not yield Full81 authority."""

        identity = authority.load_accepted_v7_3_annual_input(ROOT).identity
        clean = stack.DeploymentSnapshot(
            branch="thesis-v7",
            head="clean-head",
            origin_head="clean-head",
            step2e1_is_ancestor=True,
            successor_bytes_committed=True,
            tracked_unstaged_changes=False,
            staged_changes=False,
            authority_hashes_valid=True,
            authority_error=None,
            accepted_identity=identity,
            csv_fallback_possible=False,
            authority_untracked_paths=(),
            u06_accepted_lifecycle=live_lifecycle(),
        )
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            stack.validate_deployment_snapshot(
                clean, execute_production=True, selected_scope="full81"
            )
        self.assertEqual(caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED")

        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            stack.validate_deployment_snapshot(
                clean, execute_production=True, selected_scope="a2_variable_floor"
            )
        self.assertEqual(caught.exception.status, "A2_HARD_BLOCKED")

        # Audit finding F-01: even the accepted core-three scope must NOT reach
        # PRODUCTION_AUTHORITY_FROZEN on a clean, committed, pushed repository
        # while no accepted U-06 lifecycle exists. Detailed F-01 evidence lives
        # in tests/test_21f_u06_accepted_lifecycle_gate.py.
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            stack.validate_deployment_snapshot(
                clean, execute_production=True, selected_scope="core-three"
            )
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")


class StackAndRunnerBindingTests(unittest.TestCase):
    """Section 5 — the live route must carry the V7.4 identities."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = stack.run_successor_stack(ROOT)

    def test_stack_payload_carries_the_v7_4_alignment(self) -> None:
        self.assertEqual(
            self.payload["v7_4_authority_bundle_version"], bundle.BUNDLE_VERSION
        )
        alignment = self.payload["v7_4_authority_alignment"]
        self.assertEqual(alignment["status"], "PASS")
        self.assertEqual(alignment["alignment_status"], "CANDIDATE_ALIGNED")
        self.assertEqual(
            self.payload["u06_accepted_lifecycle"]["accepted_lifecycle_overlay"],
            "ABSENT",
        )
        self.assertEqual(
            self.payload["u06_accepted_lifecycle"][
                "production_authority_freeze_status"
            ],
            "NOT_FROZEN",
        )
        self.assertEqual(
            alignment["full81_authorization"]["main_full81_authorization"],
            "NOT_AUTHORIZED",
        )

    def test_grid_solver_settings_and_namespace_are_unchanged(self) -> None:
        self.assertEqual(len(stack.ALPHAS), 9)
        self.assertEqual(len(stack.BETAS_H), 9)
        self.assertEqual(stack.EXPECTED_CASES, 81)
        self.assertEqual(
            stack.ALPHAS,
            (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00),
        )
        self.assertEqual(stack.BETAS_H, (4, 5, 6, 7, 8, 9, 10, 11, 12))
        self.assertEqual(stack.ETA_D, 0.90)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["MIPGap"], 1e-6)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["NumericFocus"], 1)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["MIPFocus"], 0)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["Threads"], 0)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["OutputFlag"], 0)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["TimeLimit"], "INFINITY_UNSET")
        self.assertEqual(stack.EOB_SOLVER_SETTINGS["MIPGap"], 1e-6)
        self.assertEqual(
            stack.LAYER_A_PRODUCTION_ROOT.as_posix(),
            "results/layer_a/final_81_v7_3/runs",
        )
        self.assertEqual(
            sorted(stack.PRODUCTION_CASE_SETS),
            ["central", "core-three", "full81", "high", "historical-five", "low"],
        )

    def test_full_81_case_plan_remains_exactly_the_nine_by_nine_grid(self) -> None:
        final81 = self.payload["final81"]
        self.assertEqual(final81["case_count"], 81)
        self.assertEqual(final81["unique_case_count"], 81)
        coordinates = {
            (round(float(case["alpha"]), 2), int(case["beta_h"]))
            for case in final81["cases"]
        }
        self.assertEqual(
            coordinates,
            {(alpha, beta) for alpha in stack.ALPHAS for beta in stack.BETAS_H},
        )

    def test_every_case_carries_case_level_v7_4_provenance(self) -> None:
        for case in self.payload["final81"]["cases"]:
            with self.subTest(case=case["case_id"]):
                record = case["v7_4_authority"]
                self.assertEqual(record["bundle_version"], bundle.BUNDLE_VERSION)
                self.assertEqual(record["alignment_status"], "CANDIDATE_ALIGNED")
                self.assertEqual(record["u06_acceptance_status"], "NOT_ACCEPTED")
                self.assertEqual(
                    record["production_authority_freeze_status"], "NOT_FROZEN"
                )
                self.assertEqual(
                    record["framework"]["sha256"],
                    "36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541"
                    "ad2f273",
                )
                self.assertEqual(
                    record["registry"]["sha256"],
                    "5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe8"
                    "6029433",
                )
                self.assertEqual(record["main_full81_authorization"], "NOT_AUTHORIZED")
                self.assertEqual(record["a2_status"], "HARD_BLOCKED")
                self.assertEqual(record["u_01_status"], "OPEN_HOLD")
                self.assertIs(case["surplus_pv_recharge"], False)

    def test_zero_solve_counters_and_execution_boundary_hold(self) -> None:
        counters = self.payload["execution_counters"]
        self.assertEqual(counters["model_constructions"], 0)
        self.assertEqual(counters["optimization_calls"], 0)
        self.assertEqual(counters["economic_evaluations"], 0)
        boundary = self.payload["execution_boundary"]
        self.assertEqual(boundary["Final81"], "NOT EXECUTED")
        self.assertEqual(boundary["Production optimization"], "NOT AUTHORIZED")

    def test_alignment_surface_is_registered_for_the_deployment_gate(self) -> None:
        registered = {path.as_posix() for path in stack.SUCCESSOR_RELATIVE_PATHS}
        for relative in (
            "src/production_authority_bundle_v7_4.py",
            "src/production_authority_lifecycle_u06.py",
            "scripts/21e_preflight_v7_4_production_authority_alignment.py",
            "tests/test_21e_v7_4_production_authority_bundle.py",
            "tests/test_21f_u06_accepted_lifecycle_gate.py",
            "tests/test_21g_u06_r3_substitution_attacks.py",
        ):
            self.assertIn(relative, registered)


class NoSolveSourceAuditTests(unittest.TestCase):
    """Section 6 — the alignment sources must be structurally unable to solve."""

    FORBIDDEN_CALLS = {"optimize", "optimizeAsync", "optimizeBatch", "tune"}

    def test_alignment_sources_contain_no_solver_entry_point(self) -> None:
        for path in ALIGNMENT_SOURCES:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            offenders = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and (
                    (
                        isinstance(node.func, ast.Name)
                        and node.func.id in self.FORBIDDEN_CALLS
                    )
                    or (
                        isinstance(node.func, ast.Attribute)
                        and node.func.attr in self.FORBIDDEN_CALLS
                    )
                )
            ]
            with self.subTest(path=path.name):
                self.assertEqual(offenders, [])
                self.assertNotIn("gurobipy", source)
                self.assertNotIn("read_csv", source)

    def test_alignment_verifier_exposes_no_execution_interface(self) -> None:
        source = ALIGNMENT_SOURCES[1].read_text(encoding="utf-8")
        self.assertNotIn("add_argument(\n        \"--execute", source)
        self.assertNotIn("run_layer_a_production", source)
        self.assertNotIn("run_eob_production", source)
        self.assertNotIn("NativeProductionBackend", source)

    def test_bundle_module_imports_but_does_not_rebind_v7_3_authority(self) -> None:
        """The bundle may read the v7.3 authority; it must never rebind it."""

        source = ALIGNMENT_SOURCES[0].read_text(encoding="utf-8")
        tree = ast.parse(source)
        v7_3_imports: set[str] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "src.production_input_authority_v7_3"
            ):
                v7_3_imports.update(
                    alias.asname or alias.name for alias in node.names
                )
        self.assertIn("sha256_file", v7_3_imports)
        self.assertIn("V7_3_AUTHORITY_FILES", v7_3_imports)

        rebound: list[str] = []
        for node in ast.walk(tree):
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in v7_3_imports:
                    rebound.append(target.id)
                if isinstance(target, ast.Attribute) and isinstance(
                    target.value, ast.Name
                ):
                    if target.value.id in v7_3_imports:
                        rebound.append(f"{target.value.id}.{target.attr}")
        self.assertEqual(rebound, [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
