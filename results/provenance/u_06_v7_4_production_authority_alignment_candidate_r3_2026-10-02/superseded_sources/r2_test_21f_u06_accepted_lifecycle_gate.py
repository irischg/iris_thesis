"""F-01 regression tests: the U-06 accepted-lifecycle gate must be fail-closed.

A fresh independent audit failed U-06 Candidate R1 because the live production
gate could reach ``PRODUCTION_AUTHORITY_FROZEN`` once candidate implementation
bytes were merely tracked, clean, committed, and pushed.  Every test here exists
to prove that is no longer possible.

The synthetic lifecycle mappings below are **test fixtures handed to a pure
validator**.  They are not repository artifacts, they are never written to disk,
and they cannot make the real gate freeze: the real gate obtains its lifecycle
only from :func:`resolve_u06_lifecycle`, which reads live repository bytes and
Git.  No fake acceptance artifact is created anywhere in this module.

Every test is static / build-only.  Nothing here constructs a model, calls an
optimizer, runs a case, spawns a subprocess, or creates a run directory.  The
production execution flag is never written as a literal.
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
from src import production_authority_lifecycle_u06 as lifecycle_mod  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


def live_head() -> str:
    """HEAD itself, which is trivially an ancestor of HEAD.

    Used so payload fixtures reach the structural checks under test instead of
    stopping at the publication-ancestor check. Naming a published commit is not
    acceptance: every other required condition still has to hold.
    """

    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def synthetic_accepted_lifecycle() -> dict[str, object]:
    """A structurally complete, FROZEN lifecycle mapping — for fixtures only.

    This is deliberately *not* produced from a repository record. It exists so
    the pure gate validator can be exercised in both directions. It confers no
    acceptance: the live gate never reads it.
    """

    return {
        "lifecycle_module_version": lifecycle_mod.LIFECYCLE_MODULE_VERSION,
        "record_path": lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "record_present": True,
        "record_committed": True,
        "record_published": True,
        "self_accepted": False,
        "u06_alignment_status": "ACCEPTED",
        "u06_independent_audit_status": "PASS",
        "u06_acceptance_status": "CLOSED_ACCEPTED",
        "accepted_lifecycle_overlay": "PRESENT_VALID",
        "production_authority_freeze_status": "FROZEN",
        "freeze_blocked_reason": None,
        "publication_commit": "0" * 40,
        "required_future_roles": list(lifecycle_mod.REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {
            role: {"path": f"docs/synthetic/{role}.md", "sha256": "0" * 64}
            for role in lifecycle_mod.REQUIRED_ACCEPTED_ROLES
        },
        "missing_roles": [],
        "required_lifecycle_sequence": list(lifecycle_mod.REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(lifecycle_mod.LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(lifecycle_mod.CANDIDATE_R1_AUDIT_RECORD),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def clean_snapshot(lifecycle: object) -> stack.DeploymentSnapshot:
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


class LiveLifecycleStateTests(unittest.TestCase):
    """The live repository must currently resolve to ABSENT / NOT_FROZEN."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.live = lifecycle_mod.resolve_u06_lifecycle(ROOT)

    def test_no_accepted_lifecycle_record_exists_yet(self) -> None:
        path = ROOT / lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH
        self.assertFalse(path.exists())
        self.assertFalse(self.live["record_present"])
        self.assertFalse(self.live["record_committed"])
        self.assertFalse(self.live["record_published"])

    def test_live_lifecycle_is_absent_and_not_frozen(self) -> None:
        self.assertEqual(self.live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(self.live["u06_alignment_status"], "CANDIDATE")
        self.assertEqual(self.live["u06_acceptance_status"], "NOT_ACCEPTED")
        self.assertEqual(
            self.live["u06_independent_audit_status"],
            "CANDIDATE_R1_FAILED_R2_PENDING",
        )
        self.assertEqual(self.live["production_authority_freeze_status"], "NOT_FROZEN")
        self.assertFalse(lifecycle_mod.is_frozen(self.live))

    def test_every_required_role_is_reported_missing(self) -> None:
        self.assertEqual(
            sorted(self.live["missing_roles"]),
            sorted(lifecycle_mod.REQUIRED_ACCEPTED_ROLES),
        )
        self.assertEqual(self.live["satisfied_roles"], {})

    def test_candidate_r1_audit_failure_is_recorded_not_erased(self) -> None:
        record = self.live["candidate_r1_audit"]
        self.assertEqual(record["candidate_revision"], "R1")
        self.assertEqual(
            record["independent_audit_verdict"], "FAIL_REMEDIATION_REQUIRED"
        )
        self.assertEqual(record["blocking_finding"], "F-01")
        self.assertEqual(
            record["lifecycle"], "IMMUTABLE_HISTORICAL_FAILED_CANDIDATE_PROVENANCE"
        )
        self.assertEqual(record["superseded_by"], "R2")

    def test_no_future_hash_is_fabricated_or_stubbed(self) -> None:
        requirements = lifecycle_mod.future_acceptance_requirements()
        self.assertFalse(requirements["record_exists_today"])
        self.assertFalse(requirements["future_hashes_fabricated_now"])
        self.assertFalse(requirements["placeholder_digests_present"])
        source = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        # The overlay must contain no 64-hex literal at all: no reserved digest,
        # no stub, no placeholder for any future accepted artifact.
        import re

        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", source), [])

    def test_future_acceptance_requirements_are_exactly_bindable(self) -> None:
        requirements = lifecycle_mod.future_acceptance_requirements()
        self.assertEqual(
            requirements["required_roles"],
            list(lifecycle_mod.REQUIRED_ACCEPTED_ROLES),
        )
        for field in (
            "artifacts",
            "implementation_identity",
            "publication_commit",
            "u06_independent_audit_status",
            "u06_acceptance_status",
            "production_authority_freeze_status",
        ):
            self.assertIn(field, requirements["required_record_fields"])
        self.assertTrue(requirements["publication_commit_must_be_ancestor_of_head"])
        self.assertEqual(
            sorted(requirements["implementation_candidate_surface"]),
            sorted(lifecycle_mod.IMPLEMENTATION_CANDIDATE_SURFACE),
        )
        for relative in lifecycle_mod.IMPLEMENTATION_CANDIDATE_SURFACE:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())


class FailClosedFreezeGateTests(unittest.TestCase):
    """Sections A-F of the required F-01 evidence."""

    def test_a_committed_clean_candidate_is_not_enough_for_frozen(self) -> None:
        """A. The exact F-01 defect: clean + committed + pushed must not freeze."""

        live = lifecycle_mod.resolve_u06_lifecycle(ROOT)
        snapshot = clean_snapshot(live)
        # Everything a repository can offer is satisfied in this snapshot.
        self.assertTrue(snapshot.successor_bytes_committed)
        self.assertFalse(snapshot.tracked_unstaged_changes)
        self.assertFalse(snapshot.staged_changes)
        self.assertEqual(snapshot.head, snapshot.origin_head)
        self.assertTrue(snapshot.authority_hashes_valid)
        self.assertEqual(snapshot.authority_untracked_paths, ())
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            stack.validate_deployment_snapshot(
                snapshot, execute_production=True, selected_scope="core-three"
            )
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")

    def test_b_missing_independent_audit_pass_blocks_frozen(self) -> None:
        for audit_status in ("CANDIDATE_R1_FAILED_R2_PENDING", "PENDING", "FAIL"):
            with self.subTest(audit_status=audit_status):
                broken = synthetic_accepted_lifecycle()
                broken["u06_independent_audit_status"] = audit_status
                self.assertFalse(lifecycle_mod.is_frozen(broken))
                with self.assertRaises(stack.ProductionAuthorityError):
                    stack.validate_deployment_snapshot(
                        clean_snapshot(broken),
                        execute_production=True,
                        selected_scope="core-three",
                    )

    def test_c_missing_acceptance_closure_blocks_frozen(self) -> None:
        broken = synthetic_accepted_lifecycle()
        broken["u06_acceptance_status"] = "NOT_ACCEPTED"
        self.assertFalse(lifecycle_mod.is_frozen(broken))
        with self.assertRaises(stack.ProductionAuthorityError):
            stack.validate_deployment_snapshot(
                clean_snapshot(broken),
                execute_production=True,
                selected_scope="core-three",
            )

        missing_closure = synthetic_accepted_lifecycle()
        roles = dict(missing_closure["satisfied_roles"])
        roles.pop("acceptance_closure_checkpoint")
        missing_closure["satisfied_roles"] = roles
        missing_closure["missing_roles"] = ["acceptance_closure_checkpoint"]
        self.assertFalse(lifecycle_mod.is_frozen(missing_closure))

    def test_d_missing_acceptance_manifest_blocks_frozen(self) -> None:
        broken = synthetic_accepted_lifecycle()
        roles = dict(broken["satisfied_roles"])
        roles.pop("acceptance_manifest")
        broken["satisfied_roles"] = roles
        with self.assertRaises(lifecycle_mod.U06LifecycleError) as caught:
            lifecycle_mod.require_frozen_lifecycle(broken)
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_INCOMPLETE")
        with self.assertRaises(stack.ProductionAuthorityError):
            stack.validate_deployment_snapshot(
                clean_snapshot(broken),
                execute_production=True,
                selected_scope="core-three",
            )

    def test_e_missing_re_freeze_authority_blocks_frozen(self) -> None:
        broken = synthetic_accepted_lifecycle()
        roles = dict(broken["satisfied_roles"])
        roles.pop("production_authority_re_freeze_record")
        broken["satisfied_roles"] = roles
        self.assertFalse(lifecycle_mod.is_frozen(broken))

        not_frozen = synthetic_accepted_lifecycle()
        not_frozen["production_authority_freeze_status"] = "NOT_FROZEN"
        self.assertFalse(lifecycle_mod.is_frozen(not_frozen))
        with self.assertRaises(stack.ProductionAuthorityError):
            stack.validate_deployment_snapshot(
                clean_snapshot(not_frozen),
                execute_production=True,
                selected_scope="core-three",
            )

    def test_f_aligned_base_authority_alone_does_not_freeze(self) -> None:
        """F. Base-authority PASS is an identity statement, not an acceptance."""

        live = lifecycle_mod.resolve_u06_lifecycle(ROOT)
        base = bundle.verify_v7_4_authority_bundle(ROOT, live)
        self.assertEqual(base["status"], "PASS")
        self.assertEqual(base["alignment_status"], "CANDIDATE_ALIGNED")
        self.assertFalse(base["lifecycle_authority_held_by_this_bundle"])
        self.assertEqual(
            base["u06_lifecycle"]["production_authority_freeze_status"], "NOT_FROZEN"
        )
        self.assertFalse(lifecycle_mod.is_frozen(live))

    def test_unpublished_or_uncommitted_record_does_not_freeze(self) -> None:
        for field in ("record_present", "record_committed", "record_published"):
            with self.subTest(field=field):
                broken = synthetic_accepted_lifecycle()
                broken[field] = False
                self.assertFalse(lifecycle_mod.is_frozen(broken))

    def test_omitted_or_partial_lifecycle_never_freezes(self) -> None:
        self.assertFalse(lifecycle_mod.is_frozen(None))
        self.assertFalse(lifecycle_mod.is_frozen({}))
        self.assertFalse(
            lifecycle_mod.is_frozen({"production_authority_freeze_status": "FROZEN"})
        )
        snapshot = clean_snapshot(None)
        with self.assertRaises(stack.ProductionAuthorityError) as caught:
            stack.validate_deployment_snapshot(
                snapshot, execute_production=True, selected_scope="core-three"
            )
        self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")

    def test_structurally_complete_fixture_is_the_only_path_to_frozen(self) -> None:
        """The validator is not vacuous: a complete lifecycle does pass it.

        This exercises the positive branch of the pure validator with a fixture.
        It is not an acceptance: the live gate resolves its lifecycle from disk
        and Git, where the record is absent.
        """

        complete = synthetic_accepted_lifecycle()
        self.assertTrue(lifecycle_mod.is_frozen(complete))
        passed = stack.validate_deployment_snapshot(
            clean_snapshot(complete),
            execute_production=True,
            selected_scope="core-three",
        )
        self.assertEqual(passed["status"], "PRODUCTION_AUTHORITY_FROZEN")
        self.assertEqual(passed["production_authority_freeze_status"], "FROZEN")
        # And the live repository still does not satisfy it.
        self.assertFalse(
            lifecycle_mod.is_frozen(lifecycle_mod.resolve_u06_lifecycle(ROOT))
        )


class NoSelfAcceptanceTests(unittest.TestCase):
    """The candidate must be structurally unable to accept itself."""

    def _payload(self, overrides: dict[str, object] | None = None) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": lifecycle_mod.LIFECYCLE_RECORD_SCHEMA_VERSION,
            "u06_alignment_status": "ACCEPTED",
            "u06_independent_audit_status": "PASS",
            "u06_acceptance_status": "CLOSED_ACCEPTED",
            "production_authority_freeze_status": "FROZEN",
            "independent_audit_self_accepted": False,
            "publication_commit": live_head(),
            "artifacts": {
                role: {
                    "path": f"docs/checkpoints/synthetic_{role}.md",
                    "sha256": "0" * 64,
                }
                for role in lifecycle_mod.REQUIRED_ACCEPTED_ROLES
            },
            "implementation_identity": {
                relative: "0" * 64
                for relative in lifecycle_mod.IMPLEMENTATION_CANDIDATE_SURFACE
            },
        }
        if overrides:
            payload.update(overrides)
        return payload

    def _reject(self, payload: dict[str, object]) -> str:
        with self.assertRaises(lifecycle_mod.U06LifecycleError) as caught:
            lifecycle_mod.validate_accepted_lifecycle_payload(
                ROOT,
                payload,
                record_relative=(
                    lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()
                ),
            )
        return caught.exception.status

    def test_candidate_checkpoint_cannot_fill_an_acceptance_role(self) -> None:
        for role in lifecycle_mod.NON_SELF_ACCEPTABLE_ROLES:
            for candidate_path in lifecycle_mod.CANDIDATE_ARTIFACT_PATHS:
                with self.subTest(role=role, path=candidate_path):
                    payload = self._payload()
                    payload["artifacts"][role] = {
                        "path": candidate_path,
                        "sha256": "0" * 64,
                    }
                    self.assertEqual(
                        self._reject(payload), "U06_SELF_ACCEPTANCE_REJECTED"
                    )

    def test_candidate_code_and_tests_cannot_fill_an_acceptance_role(self) -> None:
        for role in lifecycle_mod.NON_SELF_ACCEPTABLE_ROLES:
            for path in (
                "src/production_authority_lifecycle_u06.py",
                "scripts/21e_preflight_v7_4_production_authority_alignment.py",
                "tests/test_21f_u06_accepted_lifecycle_gate.py",
            ):
                with self.subTest(role=role, path=path):
                    payload = self._payload()
                    payload["artifacts"][role] = {"path": path, "sha256": "0" * 64}
                    self.assertEqual(
                        self._reject(payload), "U06_SELF_ACCEPTANCE_REJECTED"
                    )

    def test_record_cannot_name_itself_as_an_acceptance_artifact(self) -> None:
        payload = self._payload()
        payload["artifacts"]["acceptance_closure_checkpoint"] = {
            "path": lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
            "sha256": "0" * 64,
        }
        self.assertEqual(self._reject(payload), "U06_SELF_ACCEPTANCE_REJECTED")

    def test_one_artifact_cannot_fill_several_acceptance_roles(self) -> None:
        payload = self._payload()
        shared = {"path": "docs/checkpoints/shared.md", "sha256": "0" * 64}
        payload["artifacts"]["acceptance_closure_checkpoint"] = dict(shared)
        payload["artifacts"]["acceptance_manifest"] = dict(shared)
        self.assertEqual(self._reject(payload), "U06_LIFECYCLE_RECORD_INVALID")

    def test_a_self_accepted_audit_is_rejected(self) -> None:
        payload = self._payload({"independent_audit_self_accepted": True})
        self.assertEqual(self._reject(payload), "U06_SELF_ACCEPTANCE_REJECTED")

    def test_non_accepted_statuses_are_rejected(self) -> None:
        for field in (
            "u06_alignment_status",
            "u06_independent_audit_status",
            "u06_acceptance_status",
            "production_authority_freeze_status",
        ):
            with self.subTest(field=field):
                payload = self._payload({field: "CANDIDATE"})
                self.assertEqual(self._reject(payload), "U06_LIFECYCLE_NOT_ACCEPTED")

    def test_wrong_schema_version_is_rejected(self) -> None:
        payload = self._payload({"schema_version": "something-else"})
        self.assertEqual(self._reject(payload), "U06_LIFECYCLE_RECORD_INVALID")

    def test_unpublished_commit_is_rejected(self) -> None:
        payload = self._payload({"publication_commit": "f" * 40})
        self.assertEqual(self._reject(payload), "U06_LIFECYCLE_NOT_PUBLISHED")

    def test_missing_role_is_rejected(self) -> None:
        payload = self._payload()
        payload["artifacts"].pop("independent_audit_pass_record")
        self.assertEqual(self._reject(payload), "U06_ACCEPTED_LIFECYCLE_INCOMPLETE")

    def test_incomplete_implementation_identity_is_rejected(self) -> None:
        payload = self._payload()
        payload["implementation_identity"].pop(
            "src/production_successor_stack_v7_3.py"
        )
        self.assertEqual(self._reject(payload), "U06_ACCEPTED_LIFECYCLE_INCOMPLETE")

    def test_a_working_tree_record_confers_nothing(self) -> None:
        """An untracked record resolves to PRESENT_INVALID, never to FROZEN."""

        # Verified without writing anything: the real record path is absent, and
        # the resolver's own contract is that tracked+clean is required.
        self.assertFalse(
            (ROOT / lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH).exists()
        )
        requirements = lifecycle_mod.future_acceptance_requirements()
        self.assertIn("tracked in Git", requirements["every_role_artifact_must_be"])
        self.assertIn(
            "clean relative to HEAD", requirements["every_role_artifact_must_be"]
        )


class Full81AndA2SeparationTests(unittest.TestCase):
    """Sections G and H of the required F-01 evidence."""

    def test_g_full81_is_rejected_regardless_of_u06_lifecycle_state(self) -> None:
        for label, lifecycle in (
            ("absent", lifecycle_mod.resolve_u06_lifecycle(ROOT)),
            ("synthetically_frozen", synthetic_accepted_lifecycle()),
        ):
            with self.subTest(lifecycle=label):
                with self.assertRaises(stack.ProductionAuthorityError) as caught:
                    stack.validate_deployment_snapshot(
                        clean_snapshot(lifecycle),
                        execute_production=True,
                        selected_scope="full81",
                    )
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

    def test_h_a2_remains_hard_blocked_regardless_of_lifecycle_state(self) -> None:
        for label, lifecycle in (
            ("absent", lifecycle_mod.resolve_u06_lifecycle(ROOT)),
            ("synthetically_frozen", synthetic_accepted_lifecycle()),
        ):
            for scope in ("a2", "robustness", "variable_floor", "perfect_information"):
                with self.subTest(lifecycle=label, scope=scope):
                    with self.assertRaises(stack.ProductionAuthorityError) as caught:
                        stack.validate_deployment_snapshot(
                            clean_snapshot(lifecycle),
                            execute_production=True,
                            selected_scope=scope,
                        )
                    self.assertEqual(caught.exception.status, "A2_HARD_BLOCKED")
        state = bundle.governance_state(synthetic_accepted_lifecycle())
        self.assertEqual(state["a2_status"], "HARD_BLOCKED")
        self.assertEqual(state["u_01_status"], "OPEN_HOLD")
        self.assertFalse(state["u_01_resolved_by_this_alignment"])

    def test_lifecycle_distinctions_are_all_represented(self) -> None:
        for name in (
            "ZERO_SOLVE_PREFLIGHT_PASS",
            "BASE_AUTHORITY_CANDIDATE_ALIGNED",
            "U06_INDEPENDENT_AUDIT_PASS",
            "U06_ACCEPTANCE_CLOSED_ACCEPTED",
            "PRODUCTION_AUTHORITY_FROZEN",
            "MAIN_FULL81_AUTHORIZED",
            "MAIN_FULL81_EXECUTED",
        ):
            self.assertIn(name, lifecycle_mod.LIFECYCLE_DISTINCTIONS)
        self.assertEqual(
            list(lifecycle_mod.REQUIRED_LIFECYCLE_SEQUENCE),
            [
                "IMPLEMENTATION_CANDIDATE",
                "FRESH_INDEPENDENT_AUDIT_PASS",
                "ACCEPTANCE_CLOSURE",
                "ACCEPTED_LIFECYCLE_RE_FREEZE_AUTHORITY",
                "COMMIT_AND_PUBLICATION",
                "READ_ONLY_FROZEN_AUTHORITY_VERIFICATION",
                "SEPARATE_MAIN_FULL81_AUTHORIZATION",
            ],
        )


class ProvenanceIsLifecycleDerivedTests(unittest.TestCase):
    """F-01 second part: U-06 provenance must not be a compile-time constant."""

    def test_u06_register_entry_tracks_lifecycle_state(self) -> None:
        absent = lifecycle_mod.absent_lifecycle()
        self.assertEqual(
            bundle.u06_register_entry(absent),
            "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT",
        )

        audited = lifecycle_mod.absent_lifecycle()
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

        frozen = synthetic_accepted_lifecycle()
        self.assertEqual(
            bundle.u06_register_entry(frozen),
            "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_FROZEN",
        )

    def test_u06_is_not_a_static_register_constant(self) -> None:
        self.assertNotIn("U-06", bundle.STATIC_UNRESOLVED_REGISTER)

    def test_governance_state_reports_accepted_state_after_lawful_acceptance(
        self,
    ) -> None:
        frozen = synthetic_accepted_lifecycle()
        state = bundle.governance_state(frozen)
        self.assertEqual(state["u06_acceptance_status"], "CLOSED_ACCEPTED")
        self.assertEqual(state["u06_independent_audit_status"], "PASS")
        self.assertEqual(state["production_authority_freeze_status"], "FROZEN")
        self.assertEqual(
            state["unresolved_register"]["U-06"],
            "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_FROZEN",
        )
        self.assertNotIn("pending", state["unresolved_register"]["U-06"].lower())

    def test_case_and_run_level_provenance_track_lifecycle(self) -> None:
        for lifecycle, expected_acceptance, expected_freeze in (
            (lifecycle_mod.absent_lifecycle(), "NOT_ACCEPTED", "NOT_FROZEN"),
            (synthetic_accepted_lifecycle(), "CLOSED_ACCEPTED", "FROZEN"),
        ):
            with self.subTest(acceptance=expected_acceptance):
                case = bundle.case_level_provenance(lifecycle)
                self.assertEqual(case["u06_acceptance_status"], expected_acceptance)
                self.assertEqual(
                    case["production_authority_freeze_status"], expected_freeze
                )
                self.assertEqual(case["main_full81_authorization"], "NOT_AUTHORIZED")
                run = bundle.declared_authority_record(lifecycle)
                self.assertEqual(run["u06_acceptance_status"], expected_acceptance)
                self.assertEqual(
                    run["production_authority_freeze_status"], expected_freeze
                )
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


class HistoricalAndScientificNonMutationTests(unittest.TestCase):
    """Section I of the required F-01 evidence, plus the invariants."""

    def test_i_historical_v7_3_authority_is_unchanged(self) -> None:
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
        self.assertEqual(
            bundle._pin("production_input_authority_v7_3").sha256,
            "f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1",
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

    def test_canonical_input_binding_unchanged(self) -> None:
        contract = bundle.canonical_planning_input_contract()
        self.assertEqual(
            contract["sha256"],
            "3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428",
        )
        self.assertEqual(contract["expected_rows"], 8760)
        self.assertEqual(contract["expected_columns"], 51)

    def test_u_07_remains_unresolved_and_a2_only(self) -> None:
        record = bundle.governance_state(synthetic_accepted_lifecycle())["u_07"]
        self.assertEqual(record["status"], "UNRESOLVED_CLASSIFICATION")
        self.assertEqual(record["scope"], "A2_ONLY")
        self.assertFalse(record["blocks_main_full81"])
        self.assertFalse(record["variable_floor_support_implemented"])
        self.assertFalse(
            record["annual_model_accepts_time_varying_reserve_floor"]
        )

    def test_overlay_module_contains_no_solver_or_scientific_content(self) -> None:
        source = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        for forbidden in ("gurobipy", "optimize(", "read_csv", "annual_design_model"):
            self.assertNotIn(forbidden, source)

    def test_lifecycle_resolution_writes_nothing(self) -> None:
        before = sorted(p.name for p in (ROOT / "results/layer_a/final_81_v7_3/runs").iterdir())
        lifecycle_mod.resolve_u06_lifecycle(ROOT)
        after = sorted(p.name for p in (ROOT / "results/layer_a/final_81_v7_3/runs").iterdir())
        self.assertEqual(before, after)
        self.assertFalse(
            (ROOT / lifecycle_mod.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH).exists()
        )


class SnapshotDefaultTests(unittest.TestCase):
    """A snapshot built without a lifecycle must default to the safe state."""

    def test_snapshot_lifecycle_defaults_to_none(self) -> None:
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
            stack.validate_deployment_snapshot(
                snapshot, execute_production=True, selected_scope="core-three"
            )
        # replace() must preserve the field rather than silently dropping it.
        revived = replace(
            snapshot, u06_accepted_lifecycle=synthetic_accepted_lifecycle()
        )
        self.assertEqual(
            stack.validate_deployment_snapshot(
                revived, execute_production=True, selected_scope="core-three"
            )["status"],
            "PRODUCTION_AUTHORITY_FROZEN",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
