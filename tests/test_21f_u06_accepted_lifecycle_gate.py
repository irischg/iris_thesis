"""U-06 R3 lifecycle-gate tests: fail-closed states, code drift, separation.

Companion to ``tests/test_21g_u06_r3_substitution_attacks.py``, which carries the
``A-01`` arbitrary-artifact attack suite. This module covers the lifecycle state
machine itself: that nothing accepted exists, that committing and pushing
candidate bytes is not a freeze, that a post-acceptance runtime-code change
breaks the freeze, and that Full81 and A2 stay separate from every U-06 state.

The synthetic lifecycle mappings here are **test fixtures handed to a pure
validator**. They are never written to disk, and they cannot move the real gate,
which resolves its lifecycle only from :func:`resolve_u06_lifecycle` reading live
repository bytes and Git. No fake acceptance artifact is created anywhere.

Implementing these defences does not close ``F-01`` or ``A-01``–``A-03``. Only a
fresh independent audit can do that.

Every test is static / build-only: no model construction, no optimizer, no
production output, and the production execution flag never appears as a literal.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from dataclasses import replace
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


def synthetic_accepted_lifecycle() -> dict:
    """A structurally complete, FROZEN resolved-lifecycle mapping — fixture only.

    Deliberately not produced from a repository record. It exercises the positive
    branch of the pure gate guard so the guard is demonstrably not vacuous. It
    confers no acceptance: the live gate never reads it.
    """

    return {
        "lifecycle_module_version": lc.LIFECYCLE_MODULE_VERSION,
        "lineage_id": lc.LINEAGE_ID,
        "target_candidate_id": lc.R3_CANDIDATE_ID,
        "record_path": lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "record_present": True,
        "record_committed": True,
        "record_published": True,
        "self_accepted": False,
        "u06_alignment_status": "ACCEPTED",
        "u06_independent_audit_status": "PASS",
        "u06_acceptance_status": "CLOSED_ACCEPTED",
        "accepted_lifecycle_overlay": "PRESENT_VALID",
        "production_authority_freeze_status": "FROZEN",
        "authorizes_main_full81": False,
        "freeze_blocked_reason": None,
        "implementation_identity_digest": lc.implementation_identity_digest(ROOT),
        "required_future_roles": list(lc.REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {
            role: {"path": f"docs/fixture/{role}.json", "sha256": "0" * 64}
            for role in lc.REQUIRED_ACCEPTED_ROLES
        },
        "missing_roles": [],
        "required_lifecycle_sequence": list(lc.REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(lc.LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(lc.CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(lc.CANDIDATE_R2_AUDIT_RECORD),
    }


def clean_snapshot(lifecycle) -> stack.DeploymentSnapshot:
    """A maximally clean repository snapshot: committed, pushed, nothing dirty."""

    identity = authority.load_accepted_v7_3_annual_input(ROOT).identity
    return stack.DeploymentSnapshot(
        branch="thesis-v7",
        head="committed-and-pushed-head",
        origin_head="committed-and-pushed-head",
        step2e1_is_ancestor=True,
        successor_bytes_committed=True,
        tracked_unstaged_changes=False,
        staged_changes=False,
        authority_hashes_valid=True,
        authority_error=None,
        accepted_identity=identity,
        csv_fallback_possible=False,
        authority_untracked_paths=(),
        u06_accepted_lifecycle=lifecycle,
    )


def gate(snapshot, scope="core-three"):
    return stack.validate_deployment_snapshot(
        snapshot, execute_production=True, selected_scope=scope, root=ROOT
    )


class LiveLifecycleStateTests(unittest.TestCase):
    """The live repository must resolve to ABSENT / NOT_FROZEN."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.live = lc.resolve_u06_lifecycle(ROOT)

    def test_no_accepted_lifecycle_record_exists_yet(self) -> None:
        self.assertFalse(
            (ROOT / lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH).exists()
        )
        self.assertFalse(self.live["record_present"])
        self.assertFalse(self.live["record_committed"])
        self.assertFalse(self.live["record_published"])

    def test_live_lifecycle_is_absent_and_not_frozen(self) -> None:
        self.assertEqual(self.live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(self.live["u06_alignment_status"], "CANDIDATE")
        self.assertEqual(self.live["u06_acceptance_status"], "NOT_ACCEPTED")
        self.assertEqual(
            self.live["u06_independent_audit_status"],
            "R1_FAILED_R2_NO_GO_R3_PENDING",
        )
        self.assertEqual(self.live["production_authority_freeze_status"], "NOT_FROZEN")
        self.assertFalse(self.live["authorizes_main_full81"])
        self.assertFalse(lc.is_frozen(self.live))

    def test_lineage_identity_is_r3(self) -> None:
        self.assertEqual(
            lc.LINEAGE_ID, "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3"
        )
        self.assertEqual(self.live["lineage_id"], lc.LINEAGE_ID)
        self.assertEqual(self.live["target_candidate_id"], lc.R3_CANDIDATE_ID)

    def test_every_required_role_is_reported_missing(self) -> None:
        self.assertEqual(
            sorted(self.live["missing_roles"]),
            sorted(lc.REQUIRED_ACCEPTED_ROLES),
        )
        self.assertEqual(self.live["satisfied_roles"], {})

    def test_r1_failure_and_r2_no_go_are_recorded_not_erased(self) -> None:
        r1 = self.live["candidate_r1_audit"]
        self.assertEqual(r1["independent_audit_verdict"], "FAIL_REMEDIATION_REQUIRED")
        self.assertEqual(r1["blocking_finding"], "F-01")
        self.assertFalse(r1["f_01_closed"])

        r2 = self.live["candidate_r2_audit"]
        self.assertEqual(
            r2["independent_audit_verdict"], "NO_GO_CRITICAL_GOVERNANCE_DEFECT"
        )
        self.assertTrue(
            r2["must_not_be_accepted_closed_frozen_or_committed_as_authority"]
        )
        self.assertEqual(r2["findings"]["A-01"]["severity"], "CRITICAL")
        self.assertEqual(r2["findings"]["A-02"]["severity"], "MAJOR")
        self.assertEqual(r2["findings"]["A-03"]["severity"], "MAJOR")
        self.assertEqual(r2["findings"]["A-04"]["severity"], "MINOR")
        self.assertEqual(r2["findings"]["A-05"]["severity"], "MINOR")
        self.assertEqual(r2["findings"]["A-06"]["severity"], "INFORMATIONAL")
        self.assertEqual(r2["superseded_by"], "R3")


class FailClosedFreezeGateTests(unittest.TestCase):
    """Committing and pushing candidate bytes is not a governance decision."""

    def test_committed_clean_pushed_candidate_is_not_enough_for_frozen(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        snapshot = clean_snapshot(live)
        self.assertTrue(snapshot.successor_bytes_committed)
        self.assertFalse(snapshot.tracked_unstaged_changes)
        self.assertFalse(snapshot.staged_changes)
        self.assertEqual(snapshot.head, snapshot.origin_head)
        self.assertTrue(snapshot.authority_hashes_valid)
        self.assertEqual(snapshot.authority_untracked_paths, ())
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            gate(snapshot)
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")

    def test_each_missing_lifecycle_stage_blocks_the_freeze(self) -> None:
        cases = {
            "audit_not_pass": {"u06_independent_audit_status": "PENDING"},
            "audit_failed": {"u06_independent_audit_status": "FAIL"},
            "not_accepted": {"u06_acceptance_status": "NOT_ACCEPTED"},
            "not_frozen": {"production_authority_freeze_status": "NOT_FROZEN"},
            "alignment_not_accepted": {"u06_alignment_status": "CANDIDATE"},
            "overlay_absent": {"accepted_lifecycle_overlay": "ABSENT"},
            "overlay_invalid": {"accepted_lifecycle_overlay": "PRESENT_INVALID"},
            "record_absent": {"record_present": False},
            "record_uncommitted": {"record_committed": False},
            "record_unpublished": {"record_published": False},
            "self_accepted": {"self_accepted": True},
            "claims_full81": {"authorizes_main_full81": True},
            "wrong_lineage": {"lineage_id": "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R2"},
            "wrong_candidate": {"target_candidate_id": "SOMETHING_ELSE"},
            "no_identity_digest": {"implementation_identity_digest": None},
        }
        for name, overrides in cases.items():
            with self.subTest(case=name):
                broken = synthetic_accepted_lifecycle()
                broken.update(overrides)
                self.assertFalse(lc.is_frozen(broken))
                with self.assertRaises(stack.ProductionAuthorityError):
                    gate(clean_snapshot(broken))

    def test_missing_or_aliased_roles_block_the_freeze(self) -> None:
        for role in lc.REQUIRED_ACCEPTED_ROLES:
            with self.subTest(missing_role=role):
                broken = synthetic_accepted_lifecycle()
                roles = dict(broken["satisfied_roles"])
                roles.pop(role)
                broken["satisfied_roles"] = roles
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.require_frozen_lifecycle(broken)
                self.assertEqual(
                    caught.exception.status, "U06_ACCEPTED_LIFECYCLE_INCOMPLETE"
                )

        broken = synthetic_accepted_lifecycle()
        broken["missing_roles"] = ["acceptance_closure"]
        self.assertFalse(lc.is_frozen(broken))

    def test_aligned_base_authority_alone_does_not_freeze(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        base = bundle.verify_v7_4_authority_bundle(ROOT, live)
        self.assertEqual(base["status"], "PASS")
        self.assertEqual(base["alignment_status"], "CANDIDATE_ALIGNED")
        self.assertFalse(base["lifecycle_authority_held_by_this_bundle"])
        self.assertFalse(lc.is_frozen(live))

    def test_omitted_or_partial_lifecycle_never_freezes(self) -> None:
        self.assertFalse(lc.is_frozen(None))
        self.assertFalse(lc.is_frozen({}))
        self.assertFalse(
            lc.is_frozen({"production_authority_freeze_status": "FROZEN"})
        )
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            gate(clean_snapshot(None))
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")

    def test_the_guard_is_not_vacuous(self) -> None:
        """A complete fixture passes, while the live repository still does not."""

        complete = synthetic_accepted_lifecycle()
        self.assertTrue(lc.is_frozen(complete))
        passed = gate(clean_snapshot(complete))
        self.assertEqual(passed["status"], "PRODUCTION_AUTHORITY_FROZEN")
        self.assertEqual(passed["production_authority_freeze_status"], "FROZEN")
        self.assertFalse(lc.is_frozen(lc.resolve_u06_lifecycle(ROOT)))


class RuntimeDependencyIdentityTests(unittest.TestCase):
    """A-02: the accepted implementation identity is the real runtime surface."""

    def test_every_dependency_the_audit_named_is_bound(self) -> None:
        for relative in (
            "scripts/21b_preflight_v7_3_eob_successor.py",
            "scripts/21c_preflight_v7_3_layer_a_successor.py",
            "scripts/09_build_valid_outage_start_sets.py",
            "scripts/15d_run_corrected_eob_v7_2.py",
            "scripts/16a_preflight_layer_a_representative_binary_cases.py",
            "scripts/19a_preflight_final_layer_a_81_cases.py",
            "scripts/19b_run_final_layer_a_81_cases.py",
        ):
            with self.subTest(path=relative):
                self.assertIn(relative, lc.RUNTIME_PRODUCTION_DEPENDENCY_PATHS)
                self.assertIn(relative, lc.ACCEPTED_IMPLEMENTATION_PATHS)

    def test_the_surface_also_covers_what_the_audit_did_not_enumerate(self) -> None:
        for relative in (
            "scripts/21a_preflight_v7_3_production_routing.py",
            "scripts/21d_preflight_v7_3_final81_successor.py",
            "src/annual_design_model_v7_2.py",
            "src/rainflow_validation_v7_2.py",
            "src/production_input_authority_v7_3.py",
            "src/production_successor_stack_v7_3.py",
            "src/production_authority_bundle_v7_4.py",
            "src/production_authority_lifecycle_u06.py",
        ):
            with self.subTest(path=relative):
                self.assertIn(relative, lc.RUNTIME_PRODUCTION_DEPENDENCY_PATHS)

    def test_gate_protected_dependencies_are_bound_too(self) -> None:
        for relative in (
            "scripts/08_calibrate_kappa.py",
            "scripts/15a_benchmark_eob_charge_discharge_formulations.py",
            "scripts/15b_freeze_production_eob_baseline.py",
            "scripts/15c_validate_production_eob_rainflow.py",
        ):
            with self.subTest(path=relative):
                self.assertIn(relative, lc.GATE_PROTECTED_DEPENDENCY_PATHS)
                self.assertIn(relative, lc.ACCEPTED_IMPLEMENTATION_PATHS)

    def test_the_r2_seven_file_surface_was_not_merely_preserved(self) -> None:
        self.assertGreater(len(lc.ACCEPTED_IMPLEMENTATION_PATHS), 7)
        self.assertEqual(
            len(lc.ACCEPTED_IMPLEMENTATION_PATHS),
            len(set(lc.ACCEPTED_IMPLEMENTATION_PATHS)),
        )

    def test_every_bound_dependency_exists_and_hashes(self) -> None:
        identity = lc.implementation_identity(ROOT)
        self.assertEqual(set(identity), set(lc.ACCEPTED_IMPLEMENTATION_PATHS))
        for relative, digest in identity.items():
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertEqual(digest, authority.sha256_file(ROOT / relative))

    def test_tests_are_validation_identity_not_runtime_authority(self) -> None:
        for relative in lc.VALIDATION_IDENTITY_PATHS:
            with self.subTest(path=relative):
                self.assertTrue(relative.startswith("tests/"))
                self.assertNotIn(relative, lc.RUNTIME_PRODUCTION_DEPENDENCY_PATHS)
                self.assertNotIn(relative, lc.ACCEPTED_IMPLEMENTATION_PATHS)
        for relative in lc.ACCEPTED_IMPLEMENTATION_PATHS:
            self.assertFalse(relative.startswith("tests/"))
        self.assertFalse(
            lc.future_acceptance_requirements()[
                "tests_are_runtime_production_authority"
            ]
        )

    def test_digest_is_order_independent_and_change_sensitive(self) -> None:
        identity = lc.implementation_identity(ROOT)
        shuffled = dict(reversed(list(identity.items())))
        self.assertEqual(
            lc.canonical_identity_digest(identity),
            lc.canonical_identity_digest(shuffled),
        )
        drifted = dict(identity)
        key = sorted(drifted)[0]
        drifted[key] = "0" * 64
        self.assertNotEqual(
            lc.canonical_identity_digest(identity),
            lc.canonical_identity_digest(drifted),
        )


class PostAcceptanceCodeDriftTests(unittest.TestCase):
    """A committed, clean, pushed runtime-code change must break the freeze."""

    def test_stale_accepted_identity_fails_closed_against_live_code(self) -> None:
        stale = synthetic_accepted_lifecycle()
        stale["implementation_identity_digest"] = lc.canonical_identity_digest(
            {"src/production_successor_stack_v7_3.py": "0" * 64}
        )
        # The pure guard accepts the shape; the live re-check does not.
        lc.require_frozen_lifecycle(stale)
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_frozen_lifecycle_against_live_implementation(ROOT, stale)
        self.assertEqual(
            caught.exception.status, "U06_IMPLEMENTATION_IDENTITY_DRIFT"
        )

    def test_the_gate_applies_the_live_drift_recheck(self) -> None:
        stale = synthetic_accepted_lifecycle()
        stale["implementation_identity_digest"] = "a" * 64
        snapshot = clean_snapshot(stale)
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            gate(snapshot)
        self.assertEqual(
            caught.exception.status, "U06_IMPLEMENTATION_IDENTITY_DRIFT"
        )
        self.assertIn("even when the change is committed", str(caught.exception))

    def test_drift_in_any_single_dependency_is_detected(self) -> None:
        live = lc.implementation_identity(ROOT)
        for relative in sorted(live):
            with self.subTest(path=relative):
                drifted = dict(live)
                drifted[relative] = "b" * 64
                stale = synthetic_accepted_lifecycle()
                stale["implementation_identity_digest"] = (
                    lc.canonical_identity_digest(drifted)
                )
                with self.assertRaises(lc.U06LifecycleError):
                    lc.require_frozen_lifecycle_against_live_implementation(
                        ROOT, stale
                    )

    def test_a_record_declaring_a_stale_digest_is_rejected_at_resolution(
        self,
    ) -> None:
        payload = {
            "artifact_type": lc.ACCEPTED_LIFECYCLE_ARTIFACT_TYPE,
            "schema_version": lc.LIFECYCLE_RECORD_SCHEMA_VERSION,
            "lineage_id": lc.LINEAGE_ID,
            "target_candidate_id": lc.R3_CANDIDATE_ID,
            "u06_alignment_status": "ACCEPTED",
            "u06_independent_audit_status": "PASS",
            "u06_acceptance_status": "CLOSED_ACCEPTED",
            "production_authority_freeze_status": "FROZEN",
            "authorizes_main_full81": False,
            "implementation_identity_digest": "c" * 64,
            "roles": {},
        }
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_accepted_lifecycle_payload(
                ROOT,
                payload,
                record_relative=lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
            )
        self.assertEqual(
            caught.exception.status, "U06_IMPLEMENTATION_IDENTITY_DRIFT"
        )


class Full81AndA2SeparationTests(unittest.TestCase):
    """Full81 and A2 remain separate from every U-06 state."""

    def test_full81_is_rejected_even_under_a_synthetic_frozen_lifecycle(
        self,
    ) -> None:
        for label, lifecycle in (
            ("absent", lc.resolve_u06_lifecycle(ROOT)),
            ("synthetically_frozen", synthetic_accepted_lifecycle()),
        ):
            with self.subTest(lifecycle=label):
                with self.assertRaises(stack.ProductionAuthorityError) as caught:
                    gate(clean_snapshot(lifecycle), scope="full81")
                self.assertEqual(
                    caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED"
                )
        self.assertIsNone(bundle.MAIN_FULL81_AUTHORIZATION_ARTIFACT)
        record = bundle.alignment_is_not_full81_authorization(
            synthetic_accepted_lifecycle()
        )
        self.assertEqual(record["main_full81_authorization"], "NOT_AUTHORIZED")
        self.assertFalse(record["alignment_implies_authorization"])
        self.assertFalse(record["acceptance_implies_authorization"])
        self.assertFalse(record["freeze_implies_authorization"])

    def test_a2_remains_hard_blocked_under_every_lifecycle_state(self) -> None:
        for label, lifecycle in (
            ("absent", lc.resolve_u06_lifecycle(ROOT)),
            ("synthetically_frozen", synthetic_accepted_lifecycle()),
        ):
            for scope in ("a2", "robustness", "variable_floor", "perfect_information"):
                with self.subTest(lifecycle=label, scope=scope):
                    with self.assertRaises(stack.ProductionAuthorityError) as caught:
                        gate(clean_snapshot(lifecycle), scope=scope)
                    self.assertEqual(caught.exception.status, "A2_HARD_BLOCKED")
        state = bundle.governance_state(synthetic_accepted_lifecycle())
        self.assertEqual(state["a2_status"], "HARD_BLOCKED")
        self.assertEqual(state["u_01_status"], "OPEN_HOLD")

    def test_u_01_and_u_07_are_unchanged(self) -> None:
        state = bundle.governance_state(synthetic_accepted_lifecycle())
        self.assertEqual(state["u_01_status"], "OPEN_HOLD")
        self.assertFalse(state["u_01_blocks_main_full81"])
        self.assertFalse(state["u_01_resolved_by_this_alignment"])
        self.assertNotIn(
            "FULL81_AUTHORIZATION", state["u_01_must_be_frozen_before"]
        )
        u_07 = state["u_07"]
        self.assertEqual(u_07["status"], "UNRESOLVED_CLASSIFICATION")
        self.assertEqual(u_07["scope"], "A2_ONLY")
        self.assertFalse(u_07["blocks_main_full81"])
        self.assertFalse(u_07["variable_floor_support_implemented"])
        self.assertFalse(u_07["annual_model_accepts_time_varying_reserve_floor"])

    def test_lifecycle_distinctions_and_sequence_are_represented(self) -> None:
        for name in (
            "ZERO_SOLVE_PREFLIGHT_PASS",
            "BASE_AUTHORITY_CANDIDATE_ALIGNED",
            "U06_INDEPENDENT_AUDIT_PASS",
            "U06_ACCEPTANCE_CLOSED_ACCEPTED",
            "U06_PRODUCTION_AUTHORITY_RE_FREEZE",
            "PRODUCTION_AUTHORITY_FROZEN",
            "MAIN_FULL81_AUTHORIZED",
            "MAIN_FULL81_EXECUTED",
        ):
            self.assertIn(name, lc.LIFECYCLE_DISTINCTIONS)
        sequence = list(lc.REQUIRED_LIFECYCLE_SEQUENCE)
        self.assertEqual(sequence[0], "IMPLEMENTATION_CANDIDATE")
        self.assertEqual(sequence[-1], "SEPARATE_MAIN_FULL81_AUTHORIZATION")
        self.assertLess(
            sequence.index("FRESH_INDEPENDENT_AUDIT_PASS"),
            sequence.index("ACCEPTANCE_CLOSURE_AND_ACCEPTANCE_MANIFEST"),
        )
        self.assertLess(
            sequence.index("PHASE_A_AUDIT_PUBLICATION_COMMIT"),
            sequence.index("PHASE_B_ACCEPTANCE_PUBLICATION_COMMIT"),
        )
        self.assertLess(
            sequence.index("PHASE_B_ACCEPTANCE_PUBLICATION_COMMIT"),
            sequence.index("PHASE_C_LIFECYCLE_PUBLICATION_VERIFIED_FROM_LIVE_GIT"),
        )


class ProvenanceIsLifecycleDerivedTests(unittest.TestCase):
    """U-06 provenance must come from the overlay, never a compile-time constant."""

    def test_u06_register_entry_tracks_lifecycle_state(self) -> None:
        absent = lc.absent_lifecycle()
        self.assertEqual(
            bundle.u06_register_entry(absent),
            "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT",
        )
        audited = lc.absent_lifecycle()
        audited["u06_independent_audit_status"] = "PASS"
        self.assertEqual(
            bundle.u06_register_entry(audited),
            "INDEPENDENT_AUDIT_PASS_PENDING_ACCEPTANCE",
        )
        accepted = synthetic_accepted_lifecycle()
        accepted["production_authority_freeze_status"] = "NOT_FROZEN"
        self.assertEqual(
            bundle.u06_register_entry(accepted),
            "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_NOT_YET_FROZEN",
        )
        self.assertEqual(
            bundle.u06_register_entry(synthetic_accepted_lifecycle()),
            "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_FROZEN",
        )

    def test_u06_is_not_a_static_register_constant(self) -> None:
        self.assertNotIn("U-06", bundle.STATIC_UNRESOLVED_REGISTER)

    def test_run_and_case_provenance_track_lifecycle(self) -> None:
        for lifecycle, acceptance, freeze in (
            (lc.absent_lifecycle(), "NOT_ACCEPTED", "NOT_FROZEN"),
            (synthetic_accepted_lifecycle(), "CLOSED_ACCEPTED", "FROZEN"),
        ):
            with self.subTest(acceptance=acceptance):
                case = bundle.case_level_provenance(lifecycle)
                run = bundle.declared_authority_record(lifecycle)
                self.assertEqual(case["u06_acceptance_status"], acceptance)
                self.assertEqual(case["production_authority_freeze_status"], freeze)
                self.assertEqual(run["u06_acceptance_status"], acceptance)
                self.assertEqual(run["production_authority_freeze_status"], freeze)
                self.assertEqual(case["main_full81_authorization"], "NOT_AUTHORIZED")
                json.dumps(stack._json_safe(run), sort_keys=True)

    def test_omitted_lifecycle_emits_the_most_restrictive_state(self) -> None:
        for record in (
            bundle.declared_authority_record(),
            bundle.case_level_provenance(),
        ):
            self.assertEqual(record["u06_acceptance_status"], "NOT_ACCEPTED")
            self.assertEqual(
                record["production_authority_freeze_status"], "NOT_FROZEN"
            )


class StackIntegrationTests(unittest.TestCase):
    """The live route must carry the R3 lineage and the dependency report."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = stack.run_successor_stack(ROOT)

    def test_stack_payload_reports_r3_lineage_and_absent_lifecycle(self) -> None:
        self.assertEqual(self.payload["u06_lineage_id"], lc.LINEAGE_ID)
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
            self.payload["v7_4_authority_alignment"]["alignment_status"],
            "CANDIDATE_ALIGNED",
        )

    def test_stack_payload_carries_the_audited_dependency_report(self) -> None:
        report = self.payload["u06_runtime_dependency_report"]
        self.assertEqual(report["lineage_id"], lc.LINEAGE_ID)
        self.assertEqual(
            report["runtime_production_dependency_count"],
            len(lc.RUNTIME_PRODUCTION_DEPENDENCY_PATHS),
        )
        self.assertEqual(
            report["accepted_implementation_count"],
            len(lc.ACCEPTED_IMPLEMENTATION_PATHS),
        )
        self.assertFalse(report["tests_counted_as_runtime_production_authority"])
        self.assertEqual(
            report["implementation_identity_digest"],
            lc.implementation_identity_digest(ROOT),
        )

    def test_grid_solver_contract_and_namespace_unchanged(self) -> None:
        self.assertEqual(len(stack.ALPHAS), 9)
        self.assertEqual(len(stack.BETAS_H), 9)
        self.assertEqual(stack.EXPECTED_CASES, 81)
        self.assertEqual(stack.ETA_D, 0.90)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["MIPGap"], 1e-6)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["NumericFocus"], 1)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["MIPFocus"], 0)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["Threads"], 0)
        self.assertEqual(stack.LAYER_A_SOLVER_SETTINGS["OutputFlag"], 0)
        self.assertEqual(stack.EOB_SOLVER_SETTINGS["MIPGap"], 1e-6)
        self.assertEqual(
            stack.LAYER_A_PRODUCTION_ROOT.as_posix(),
            "results/layer_a/final_81_v7_3/runs",
        )
        self.assertEqual(
            sorted(stack.PRODUCTION_CASE_SETS),
            ["central", "core-three", "full81", "high", "historical-five", "low"],
        )

    def test_full_81_plan_remains_the_nine_by_nine_grid(self) -> None:
        final81 = self.payload["final81"]
        self.assertEqual(final81["case_count"], 81)
        self.assertEqual(final81["unique_case_count"], 81)
        self.assertEqual(
            {
                (round(float(c["alpha"]), 2), int(c["beta_h"]))
                for c in final81["cases"]
            },
            {(a, b) for a in stack.ALPHAS for b in stack.BETAS_H},
        )

    def test_zero_solve_counters_hold(self) -> None:
        counters = self.payload["execution_counters"]
        self.assertEqual(counters["model_constructions"], 0)
        self.assertEqual(counters["optimization_calls"], 0)
        self.assertEqual(counters["economic_evaluations"], 0)

    def test_historical_v7_3_authority_is_unchanged(self) -> None:
        self.assertEqual(
            set(authority.AUTHORITY_FILES),
            {"methodology", "evidence", "lifecycle"},
        )
        self.assertEqual(
            authority.AUTHORITY_FILES["methodology"][0].as_posix(),
            "docs/research_framework_v7_3_2026-09-23.md",
        )
        self.assertEqual(
            authority.AUTHORITY_VERSION,
            "v7.3-production-input-authority-2026-09-24-r1",
        )
        self.assertEqual(
            bundle._pin("production_input_authority_v7_3").sha256,
            "f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1",
        )

    def test_snapshot_lifecycle_defaults_to_the_safe_value(self) -> None:
        identity = authority.load_accepted_v7_3_annual_input(ROOT).identity
        snapshot = stack.DeploymentSnapshot(
            branch="thesis-v7",
            head="h",
            origin_head="h",
            step2e1_is_ancestor=True,
            successor_bytes_committed=True,
            tracked_unstaged_changes=False,
            staged_changes=False,
            authority_hashes_valid=True,
            authority_error=None,
            accepted_identity=identity,
            csv_fallback_possible=False,
            authority_untracked_paths=(),
        )
        self.assertIsNone(snapshot.u06_accepted_lifecycle)
        with self.assertRaises(stack.ProductionAuthorityError):
            gate(snapshot)
        revived = replace(
            snapshot, u06_accepted_lifecycle=synthetic_accepted_lifecycle()
        )
        self.assertEqual(gate(revived)["status"], "PRODUCTION_AUTHORITY_FROZEN")

    def test_no_production_run_directory_was_created(self) -> None:
        runs = sorted(
            p.name for p in (ROOT / "results/layer_a/final_81_v7_3/runs").iterdir()
        )
        self.assertEqual(runs, ["20260925T062317399837Z_bb564f7b55"])

    def test_overlay_contains_no_solver_or_scientific_content(self) -> None:
        source = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("gurobipy", "optimize(", "read_csv", "annual_design_model_v7_2 import"):
            self.assertNotIn(forbidden, source)

    def test_worktree_is_not_mutated_by_resolution(self) -> None:
        def status():
            return subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                errors="replace",
            ).stdout

        before = status()
        lc.resolve_u06_lifecycle(ROOT)
        lc.runtime_dependency_report(ROOT)
        self.assertEqual(before, status())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
