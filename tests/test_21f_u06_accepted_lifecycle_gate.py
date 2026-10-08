"""U-06 lifecycle-gate tests: fail-closed states, code drift, separation.

Current Full81 Production Generation G1: the current generation is G1, the R8
preflight-authorization-guard generation is historical, and every assertion
about the LIVE lifecycle is phase-aware (see :func:`current_record_present`).

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

from src import main_full81_authorization_v7_4 as auth  # noqa: E402
from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


#: Current Full81 Production Generation G1: the live assertions below are
#: PHASE-AWARE.  R8 was accepted after its suites hard-coded the pre-acceptance
#: state, and its own validation surface then failed on a correct repository.
#: Each live assertion here therefore reads the phase from primary state: while
#: the current generation's accepted-lifecycle slot is absent it requires the
#: most restrictive state; once the slot exists it requires a VALID, frozen
#: acceptance of the current generation - presence alone is never accepted.
def current_record_present() -> bool:
    return (ROOT / lc.CURRENT_GENERATION.accepted_lifecycle_record_path).is_file()


def current_scope_authorization_present() -> bool:
    return (ROOT / auth.AUTHORIZATION_RECORD_RELATIVE_PATH).is_file()


def synthetic_accepted_lifecycle() -> dict:
    """A structurally complete, FROZEN resolved-lifecycle mapping — fixture only.

    Deliberately not produced from a repository record. It exercises the positive
    branch of the pure gate guard so the guard is demonstrably not vacuous. It
    confers no acceptance: the live gate never reads it.

    R3-AUD-04. This fixture used to be hard-bound to the U-06 R3 generation
    (``lc.LINEAGE_ID`` / ``lc.R3_CANDIDATE_ID`` / the U-06 accepted-lifecycle
    path) and omitted ``generation_id`` entirely. Once the current generation
    advanced past U-06 R3 the gate guard correctly rejected it on
    ``generation_id``, and four tests that depend on the guard reaching its
    positive branch failed or errored. The guard was right; the fixture was a
    predecessor-generation premise.

    It is now derived from ``lc.CURRENT_GENERATION``, so it describes whatever
    generation is current and cannot fall behind another advance. Nothing is
    relaxed: every field the guard checks is still supplied, and the guard
    still rejects this mapping the moment any one of them is wrong.
    """

    generation = lc.CURRENT_GENERATION
    return {
        "lifecycle_module_version": lc.LIFECYCLE_MODULE_VERSION,
        "generation_id": generation.generation_id,
        "is_current_generation": True,
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
        "record_path": generation.accepted_lifecycle_record_path,
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
        """The CURRENT generation has no accepted-lifecycle record.

        R3-AUD-04. This asserted that the *U-06 R3* accepted-lifecycle record
        does not exist. That record was lawfully created, audited, accepted and
        frozen, so the premise became false and the test failed on a fact that
        is correct. The live state it is actually about is the current
        generation's own slot, which is read from the generation rather than
        from the U-06 constant.
        """

        # G1: phase-aware.  Absent slot -> nothing recorded; present slot ->
        # recorded, committed and published.
        present = current_record_present()
        self.assertEqual(self.live["record_present"], present)
        self.assertEqual(self.live["record_committed"], present)
        self.assertEqual(self.live["record_published"], present)

    def test_historical_u06_record_exists_and_is_not_current(self) -> None:
        """The historical U-06 R3 record is retained, and is not the current one.

        The companion of the test above: the historical accepted record must
        still be on disk (nothing accepted was deleted), must belong to a
        HISTORICAL generation, and must not be the current generation's slot.
        """

        historical = ROOT / lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH
        self.assertTrue(historical.is_file(), "accepted U-06 R3 record was deleted")
        self.assertIn(lc.U06_R3_GENERATION, lc.HISTORICAL_GENERATIONS)
        self.assertNotIn(lc.CURRENT_GENERATION, lc.HISTORICAL_GENERATIONS)
        self.assertNotEqual(
            lc.CURRENT_GENERATION.accepted_lifecycle_record_path,
            lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        )
        # And the live resolver reads the CURRENT slot, never the historical one.
        self.assertEqual(
            self.live["record_path"],
            lc.CURRENT_GENERATION.accepted_lifecycle_record_path,
        )

    def test_live_lifecycle_is_absent_and_not_frozen(self) -> None:
        if current_record_present():
            # Accepted phase: the record must be a valid acceptance.
            self.assertEqual(self.live["accepted_lifecycle_overlay"], "PRESENT_VALID")
            self.assertTrue(lc.is_frozen(self.live))
            self.assertFalse(self.live["authorizes_main_full81"])
            return
        self.assertEqual(self.live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(self.live["u06_alignment_status"], "CANDIDATE")
        self.assertEqual(self.live["u06_acceptance_status"], "NOT_ACCEPTED")
        # R2-AUD-03. This assertion previously required the audit state of the
        # ACTIVE candidate to be "R1_FAILED_R2_NO_GO_R3_PENDING", which is the
        # audit history of the HISTORICAL U-06 ALIGNMENT generation. That stale
        # premise is exactly the defect the independent audit of Candidate R2
        # reported, so the test encoded the defect rather than catching it. The
        # active candidate is R3 and its independent audit has not been
        # performed.
        self.assertEqual(
            self.live["u06_independent_audit_status"],
            "NOT_YET_PERFORMED",
        )
        self.assertEqual(self.live["production_authority_freeze_status"], "NOT_FROZEN")
        self.assertFalse(self.live["authorizes_main_full81"])
        self.assertFalse(lc.is_frozen(self.live))

    def test_historical_u06_audit_cannot_masquerade_as_current_candidate(
        self,
    ) -> None:
        """R2-AUD-03 regression guard.

        The historical U-06 alignment audit history must remain retrievable and
        must never be presented as the active candidate's audit state.
        """

        historical = "R1_FAILED_R2_NO_GO_R3_PENDING"

        # 1. The historical string is retained, under an explicitly historical
        #    name, and still carries the U-06 alignment records.
        self.assertEqual(lc.HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS, historical)
        hist = self.live["historical_u06_alignment_audit"]
        self.assertEqual(hist["audit_status"], historical)
        self.assertEqual(
            hist["scope"], "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_GENERATION"
        )
        self.assertFalse(hist["is_current_candidate_audit_state"])

        # 2. It is NOT the active candidate's audit state, anywhere it is
        #    emitted.
        self.assertNotEqual(self.live["u06_independent_audit_status"], historical)
        self.assertNotEqual(lc.PRE_ACCEPTANCE_AUDIT_STATUS, historical)
        summary = lc.lifecycle_summary(self.live)
        self.assertNotEqual(summary["u06_independent_audit_status"], historical)
        self.assertFalse(summary["historical_u06_alignment_audit_status_is_current"])
        self.assertEqual(
            summary["historical_u06_alignment_audit_status"], historical
        )

        # 3. The generic field is scoped to the active candidate and agrees with
        #    that candidate's own register entry.
        self.assertEqual(
            summary["u06_independent_audit_status_scope"],
            "ACTIVE_GENERATION_CURRENT_CANDIDATE_ONLY",
        )
        # R3-AUD-04: derived from the current generation rather than pinned to
        # one candidate revision, so a lawful candidate advance does not make
        # this regression guard assert a predecessor's identity.
        # G1: the active candidate belongs to the CURRENT generation and is
        # read from that generation's own register, never from the R8
        # (preflight-authorization-guard) register, which is now historical.
        active = lc.ACTIVE_CANDIDATE_ID
        self.assertEqual(active, lc.CURRENT_GENERATION.candidate_id)
        self.assertIn(active, lc.CURRENT_CANDIDATE_AUDIT_HISTORY)
        self.assertNotIn(active, lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY)
        self.assertEqual(summary["u06_independent_audit_status_candidate_id"], active)
        if not current_record_present():
            self.assertEqual(
                self.live["active_candidate_audit"]["independent_audit"],
                self.live["u06_independent_audit_status"],
            )

        # 4. The R8 generation's candidate history is retained, truthful and
        #    separate from the U-06 alignment history.
        history = self.live["preflight_authorization_guard_candidate_audit_history"]
        r1 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1"]
        self.assertEqual(r1["independent_audit"], "PASS_WITH_NONBLOCKING_FINDINGS")
        self.assertEqual(r1["publication"], "STOP")
        self.assertEqual(r1["acceptance"], "NOT_ACCEPTED")

        r2 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2"]
        self.assertEqual(r2["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r2["publication"], "NOT_PERFORMED")
        self.assertEqual(r2["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(
            tuple(r2["blocking_findings"]),
            ("R2-AUD-01", "R2-AUD-02", "R2-AUD-03"),
        )

        r3 = self.live["current_generation_candidate_audit_history"][active]
        self.assertEqual(r3, dict(lc.CURRENT_CANDIDATE_AUDIT_HISTORY[active]))
        self.assertEqual(r3["independent_audit"], "NOT_YET_PERFORMED")
        self.assertEqual(r3["publication"], "NOT_YET_AUTHORIZED")
        self.assertEqual(r3["acceptance"], "NOT_YET_ACCEPTED")

        # 5. No audit PASS is fabricated for the active candidate, and the
        #    active generation does not self-declare one.
        self.assertNotEqual(r3["independent_audit"], lc.ACCEPTED_AUDIT_STATUS)
        self.assertNotEqual(
            lc.CURRENT_GENERATION.candidate_audit_state, lc.ACCEPTED_AUDIT_STATUS
        )

    def test_parameter_registry_durable_publication_is_required(self) -> None:
        """R2-AUD-01 regression guard: the pin target must be publishable."""

        registry = "data/reference/parameter_registry_v7_2.csv"
        self.assertIn(registry, lc.REQUIRED_DURABLE_PUBLICATION_PATHS)
        # Stale premise corrected: the registry WAS force-added and published
        # (R2-AUD-01), so it is tracked and no longer needs a force-add.  The
        # guard is that it stays published with exactly its pinned bytes.
        tracked, clean = lc.is_tracked_and_clean(ROOT, registry)
        self.assertTrue(tracked and clean)
        self.assertNotIn(registry, lc.required_durable_publication_force_add_paths(ROOT))
        # The canonical digest is read from the authority bundle pin, never
        # restated here: this module must contain no 64-hex digest literal.
        self.assertEqual(
            lc._required_durable_publication_sha256()[registry],
            bundle._pin("parameter_registry").sha256,
        )
        # The current candidate's checkpoint and manifest are required too: a
        # future acceptance's role validators read them by path.
        self.assertIn(
            lc.CURRENT_GENERATION.candidate_checkpoint_path,
            lc.REQUIRED_DURABLE_PUBLICATION_PATHS,
        )
        self.assertIn(
            lc.CURRENT_GENERATION.candidate_manifest_path,
            lc.REQUIRED_DURABLE_PUBLICATION_PATHS,
        )

        report = self.live["durable_publication"]
        entry = report["entries"][registry]
        # Canonical content is unchanged, and the requirement is declared.
        self.assertTrue(entry["live_content_matches_canonical"])
        self.assertFalse(report["gitignore_modified"])
        self.assertFalse(report["canonical_content_modified"])
        # Published durably: present in HEAD with exactly the pinned bytes.
        self.assertTrue(entry["present_in_head"])
        self.assertTrue(entry["published_durably"])
        self.assertEqual(entry["head_sha256"], bundle._pin("parameter_registry").sha256)
        self.assertFalse(entry["force_add_required"])
        self.assertNotIn(registry, report["missing_required_authority_files"])
        # The current candidate package is phase-aware: until it is published
        # it is truthfully reported missing, never assumed present.
        for relative in (
            lc.CURRENT_GENERATION.candidate_checkpoint_path,
            lc.CURRENT_GENERATION.candidate_manifest_path,
        ):
            published = lc.blob_sha256_at(ROOT, "HEAD", relative) is not None
            self.assertEqual(relative in report["missing_required_authority_files"], not published)

    def test_live_lineage_identity_is_the_current_generation(self) -> None:
        """The live lifecycle reports the CURRENT generation's identity.

        R3-AUD-04. This asserted the live lineage equals ``lc.LINEAGE_ID``, the
        U-06 R3 lineage. Once the current generation advanced, the live
        resolver correctly reported the new lineage and the test failed on a
        predecessor premise. Expected values are now derived from the current
        generation, so a future lawful advance does not re-break this.
        """

        generation = lc.CURRENT_GENERATION
        self.assertEqual(self.live["lineage_id"], generation.lineage_id)
        self.assertEqual(self.live["target_candidate_id"], generation.candidate_id)
        self.assertEqual(self.live["generation_id"], generation.generation_id)

    def test_accepted_u06_r3_identity_constants_are_byte_stable(self) -> None:
        """The accepted U-06 R3 names keep their accepted values, forever.

        Retained as an explicitly HISTORICAL assertion. It is what stops the
        test above from being a licence to rewrite accepted identity: the U-06
        constants must not drift just because they are no longer current.
        """

        self.assertEqual(
            lc.LINEAGE_ID, "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3"
        )
        self.assertEqual(
            lc.R3_CANDIDATE_ID,
            "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R3",
        )
        self.assertEqual(lc.U06_R3_GENERATION.lineage_id, lc.LINEAGE_ID)
        self.assertEqual(lc.U06_R3_GENERATION.candidate_id, lc.R3_CANDIDATE_ID)
        self.assertNotEqual(lc.CURRENT_GENERATION.lineage_id, lc.LINEAGE_ID)

    def test_every_required_role_is_reported_missing(self) -> None:
        if current_record_present():
            self.assertEqual(self.live["missing_roles"], [])
            self.assertEqual(
                sorted(self.live["satisfied_roles"]), sorted(lc.REQUIRED_ACCEPTED_ROLES)
            )
            return
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
        if current_record_present():
            # Accepted phase: the freeze comes from the accepted lifecycle,
            # which this snapshot carries, not from the clean repository.
            self.assertTrue(lc.is_frozen(live))
            return
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
        # The bundle PASS never decides the freeze; only the record does.
        self.assertEqual(lc.is_frozen(live), current_record_present())

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
        self.assertEqual(
            lc.is_frozen(lc.resolve_u06_lifecycle(ROOT)), current_record_present()
        )


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
                # G1: without a lawful scope authorization the scope guard
                # refuses; once one exists, the separate execution guard does.
                expected = {"FULL81_AUTHORIZATION_NOT_GRANTED"}
                if current_scope_authorization_present():
                    expected.add("FULL81_EXECUTION_NOT_AUTHORIZED")
                self.assertIn(caught.exception.status, expected)
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
            bundle.ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY,
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

    # -- R2-AUD-03 -------------------------------------------------------

    def test_pre_acceptance_register_entry_is_candidate_neutral(self) -> None:
        """R2-AUD-03: the entry may not name the historical U-06 candidate.

        Candidate R3 corrected most audit fields but left this function
        returning ``V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT``
        — the ownership string of the HISTORICAL U-06 *alignment* generation —
        as the register entry of the active preflight-authorization-guard
        candidate. The pre-acceptance entry must now name no generation and no
        candidate at all.
        """

        entry = bundle.u06_register_entry(lc.absent_lifecycle())
        self.assertEqual(
            entry, bundle.ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY
        )
        self.assertNotEqual(
            entry, bundle.HISTORICAL_U06_ALIGNMENT_REGISTER_ENTRY
        )
        for forbidden in ("V7_4_ALIGNMENT", "U06_V7_4", "ALIGNMENT_CANDIDATE"):
            self.assertNotIn(forbidden, entry)
        # And it names no candidate revision of any generation.
        for generation in lc.AUTHORITY_GENERATIONS:
            self.assertNotIn(generation.candidate_id, entry)
            self.assertNotIn(generation.generation_id, entry)

    def test_register_state_carries_explicit_current_ownership(self) -> None:
        """Ownership is explicit fields, not a string a reader must decode."""

        state = bundle.u06_register_state(lc.resolve_u06_lifecycle(ROOT))
        generation = lc.CURRENT_GENERATION
        self.assertEqual(state["generation_id"], generation.generation_id)
        self.assertEqual(state["lineage_id"], generation.lineage_id)
        self.assertEqual(state["candidate_id"], generation.candidate_id)
        self.assertEqual(
            state["candidate_audit_status"],
            "PASS" if current_record_present() else "NOT_YET_PERFORMED",
        )
        self.assertEqual(
            state["candidate_audit_status_candidate_id"], generation.candidate_id
        )
        self.assertTrue(state["entry_is_candidate_neutral"])
        self.assertFalse(state["historical_u06_alignment_is_current"])
        self.assertFalse(
            state["historical_u06_alignment_register_entry_is_current"]
        )

    def test_historical_u06_status_cannot_masquerade_as_current(self) -> None:
        """Substitution control: historical audit state is never the active one."""

        state = bundle.u06_register_state(lc.resolve_u06_lifecycle(ROOT))
        self.assertEqual(
            state["historical_u06_alignment_audit_status"],
            lc.HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
        )
        self.assertNotEqual(
            state["candidate_audit_status"],
            lc.HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
        )
        # Injecting the historical string as the active audit status must not
        # make the current candidate read as audited.
        forged = lc.absent_lifecycle()
        forged["u06_independent_audit_status"] = (
            lc.HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS
        )
        self.assertEqual(
            bundle.u06_register_entry(forged),
            bundle.ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY,
        )
        self.assertFalse(lc.is_frozen(forged))
        # And the historical records themselves are retained, not erased.
        summary = lc.lifecycle_summary(lc.resolve_u06_lifecycle(ROOT))
        self.assertEqual(
            summary["historical_u06_alignment_audit"]["audit_status"],
            lc.HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
        )
        self.assertFalse(
            summary["historical_u06_alignment_audit"][
                "is_current_candidate_audit_state"
            ]
        )
        self.assertEqual(
            summary["candidate_r1_audit"]["independent_audit_verdict"],
            "FAIL_REMEDIATION_REQUIRED",
        )

    def test_active_candidate_register_entry_is_g1_candidate_r1(self) -> None:
        """The active register entry is G1 Candidate R1 of the current generation.

        CURRENT POINTER, advanced from the R8 generation to G1.  The R8 entry
        is asserted separately and historically below; nothing is relaxed.
        """

        summary = lc.lifecycle_summary(lc.resolve_u06_lifecycle(ROOT))
        self.assertEqual(
            summary["active_candidate_id"],
            "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
        )
        self.assertEqual(
            summary["active_candidate_id"], lc.CURRENT_GENERATION.candidate_id
        )
        active = summary["active_candidate_audit"]
        self.assertEqual(active["candidate_revision"], "R1")
        self.assertEqual(active["independent_audit"], "NOT_YET_PERFORMED")
        self.assertEqual(active["publication"], "NOT_YET_AUTHORIZED")
        self.assertEqual(active["acceptance"], "NOT_YET_ACCEPTED")
        self.assertEqual(
            active["disposition"], "ACTIVE_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT"
        )

    def test_r8_register_entry_is_retained_as_historical_candidate_time_state(
        self,
    ) -> None:
        """HISTORICAL: R8's register entry is byte-stable; R8 is superseded.

        The entry records R8's CANDIDATE-time state (the V4 contract replays
        R8's artifacts against it); R8's later acceptance is proved by its
        published accepted-lifecycle record, and R8 can never authorise G1.
        """

        r8_id = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8"
        r8 = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[r8_id]
        self.assertEqual(r8["candidate_revision"], "R8")
        self.assertEqual(r8["independent_audit"], "NOT_YET_PERFORMED")
        self.assertEqual(tuple(r8["remediates"]), ("R6-AUD-01", "R7-AUD-01"))
        self.assertIn(r8_id, lc.CURRENT_GENERATION.superseded_candidate_ids)
        self.assertNotEqual(lc.ACTIVE_CANDIDATE_ID, r8_id)
        r8_generation = lc.GENERATIONS_BY_ID["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1"]
        self.assertIn(r8_generation, lc.HISTORICAL_GENERATIONS)
        self.assertTrue((ROOT / r8_generation.accepted_lifecycle_record_path).is_file())

    def test_r7_is_a_truthful_rejected_historical_candidate(self) -> None:
        """HISTORICAL: Candidate R7 failed its audit and may never authorise."""

        r7_id = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7"
        r7 = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[r7_id]
        self.assertEqual(r7["candidate_revision"], "R7")
        self.assertEqual(r7["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r7["publication"], "NOT_PERFORMED")
        self.assertEqual(r7["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r7["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")
        self.assertEqual(tuple(r7["blocking_findings"]), ("R7-AUD-01",))
        self.assertEqual(
            r7["preservation_package"],
            lc.CANDIDATE_PRESERVATION_PACKAGES[r7_id]["directory"],
        )
        self.assertIn(r7_id, lc.CURRENT_GENERATION.superseded_candidate_ids)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHANGE_LEDGER_PATH,
        ):
            self.assertIn(path, lc.CURRENT_GENERATION.candidate_artifact_paths)

    def test_r6_is_a_truthful_rejected_historical_candidate(self) -> None:
        """HISTORICAL: Candidate R6 failed its audit and may never authorise."""

        r6_id = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6"
        r6 = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[r6_id]
        self.assertEqual(r6["candidate_revision"], "R6")
        self.assertEqual(r6["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r6["publication"], "NOT_PERFORMED")
        self.assertEqual(r6["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r6["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")
        self.assertEqual(tuple(r6["blocking_findings"]), ("R6-AUD-01", "R6-AUD-02"))
        self.assertEqual(
            r6["preservation_package"],
            lc.CANDIDATE_PRESERVATION_PACKAGES[r6_id]["directory"],
        )
        self.assertIn(r6_id, lc.CURRENT_GENERATION.superseded_candidate_ids)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHANGE_LEDGER_PATH,
        ):
            self.assertIn(path, lc.CURRENT_GENERATION.candidate_artifact_paths)

    def test_r5_is_a_truthful_rejected_historical_candidate(self) -> None:
        """HISTORICAL: Candidate R5 failed its audit and may never authorise."""

        r5_id = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5"
        r5 = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[r5_id]
        self.assertEqual(r5["candidate_revision"], "R5")
        self.assertEqual(r5["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r5["publication"], "NOT_PERFORMED")
        self.assertEqual(r5["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r5["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")
        self.assertEqual(tuple(r5["blocking_findings"]), ("R5-AUD-01", "R5-AUD-02"))
        self.assertEqual(
            r5["preservation_package"],
            lc.CANDIDATE_PRESERVATION_PACKAGES[r5_id]["directory"],
        )
        self.assertIn(r5_id, lc.CURRENT_GENERATION.superseded_candidate_ids)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_MANIFEST_PATH,
        ):
            self.assertIn(path, lc.CURRENT_GENERATION.candidate_artifact_paths)

    def test_r4_is_a_truthful_rejected_historical_candidate(self) -> None:
        """HISTORICAL: Candidate R4 failed its audit and may never authorise."""

        history = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY
        r4 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"]
        self.assertEqual(r4["candidate_revision"], "R4")
        self.assertEqual(r4["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r4["publication"], "NOT_PERFORMED")
        self.assertEqual(r4["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r4["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")
        self.assertEqual(tuple(r4["blocking_findings"]), ("R4-AUD-01",))
        self.assertEqual(
            r4["preservation_package"],
            lc.CANDIDATE_PRESERVATION_PACKAGES[
                "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"
            ]["directory"],
        )
        self.assertIn(
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
            lc.CURRENT_GENERATION.superseded_candidate_ids,
        )
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH,
        ):
            self.assertIn(path, lc.CURRENT_GENERATION.candidate_artifact_paths)

    def test_live_durable_publication_report_never_equates_presence_with_content(
        self,
    ) -> None:
        """R4-AUD-01: ``live_content_matches_canonical`` is a real comparison.

        R4's live report set it to ``True`` for any unpinned path that merely
        existed, and R4 froze that into its manifest. Every entry must now name
        its canonical identity source, and the candidate manifest's own entry
        must be not-applicable rather than ``True``.
        """

        report = lc.resolve_u06_lifecycle(ROOT)["durable_publication"]
        generation = lc.CURRENT_GENERATION
        manifest_path = ROOT / generation.candidate_manifest_path
        if not manifest_path.is_file():
            # G1 candidate phase before packaging: with no manifest there is no
            # binding, and the report must say so rather than equate presence
            # (or absence) with content.
            for relative in (
                generation.candidate_checkpoint_path,
                generation.candidate_change_ledger_path,
            ):
                entry = report["entries"][relative]
                self.assertIsNone(entry["expected_sha256"])
                self.assertFalse(entry["live_content_matches_canonical"])
            own = report["entries"][generation.candidate_manifest_path]
            self.assertIsNone(own["live_content_matches_canonical"])
            self.assertFalse(own["live_present"])
            return
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for relative, entry in report["entries"].items():
            with self.subTest(path=relative):
                if relative in lc.REQUIRED_DURABLE_PUBLICATION_PIN_LABELS:
                    self.assertEqual(
                        entry["canonical_identity_source"], "AUTHORITY_BUNDLE_PIN"
                    )
                    self.assertEqual(
                        entry["live_content_matches_canonical"],
                        entry["live_sha256"] == entry["expected_sha256"],
                    )
                elif relative == generation.candidate_checkpoint_path:
                    self.assertEqual(
                        entry["canonical_identity_source"],
                        "MANIFEST_CANDIDATE_CHECKPOINT_FIELD",
                    )
                    self.assertEqual(
                        entry["expected_sha256"],
                        manifest["candidate_checkpoint"]["sha256"],
                    )
                    self.assertEqual(
                        entry["live_content_matches_canonical"],
                        entry["live_sha256"] == entry["expected_sha256"],
                    )
                    self.assertTrue(entry["live_content_matches_canonical"])
                elif relative == generation.candidate_change_ledger_path:
                    self.assertEqual(
                        entry["canonical_identity_source"],
                        "MANIFEST_CANDIDATE_CHANGE_LEDGER_FIELD",
                    )
                    self.assertEqual(
                        entry["expected_sha256"],
                        manifest["candidate_change_ledger"]["sha256"],
                    )
                    self.assertTrue(entry["live_content_matches_canonical"])
                else:
                    self.assertEqual(relative, generation.candidate_manifest_path)
                    self.assertEqual(
                        entry["canonical_identity_source"],
                        "EXTERNAL_LIFECYCLE_ROLE_BINDING",
                    )
                    self.assertIsNone(entry["expected_sha256"])
                    self.assertIsNone(entry["live_content_matches_canonical"])
                # Presence alone is never reported as content equality.
                if entry["live_content_matches_canonical"] is True:
                    self.assertEqual(entry["live_sha256"], entry["expected_sha256"])

    def test_r1_r2_r3_remain_truthful_historical_candidates(self) -> None:
        """No predecessor candidate's recorded outcome may be rewritten."""

        history = lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY
        r1 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1"]
        self.assertEqual(r1["independent_audit"], "PASS_WITH_NONBLOCKING_FINDINGS")
        self.assertEqual(r1["publication"], "STOP")
        self.assertEqual(r1["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(
            r1["disposition"], "SUPERSEDED_HISTORICAL_PREDECESSOR_IMMUTABLE"
        )

        r2 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2"]
        self.assertEqual(r2["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r2["publication"], "NOT_PERFORMED")
        self.assertEqual(r2["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r2["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")

        r3 = history["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3"]
        self.assertEqual(r3["independent_audit"], "FAIL_NO_GO")
        self.assertEqual(r3["publication"], "NOT_PERFORMED")
        self.assertEqual(r3["acceptance"], "NOT_ACCEPTED")
        self.assertEqual(r3["disposition"], "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE")
        self.assertEqual(
            tuple(r3["blocking_findings"]),
            ("R3-AUD-01", "R3-AUD-02", "R3-AUD-03", "R2-AUD-03", "R3-AUD-04"),
        )

        # Every predecessor is barred from filling a role of this generation.
        barred = set(lc.CURRENT_GENERATION.superseded_candidate_ids)
        for candidate in (
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1",
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2",
            "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3",
        ):
            self.assertIn(candidate, barred)
        self.assertNotIn(lc.CURRENT_GENERATION.candidate_id, barred)

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
        # G1: phase-aware; the stack reports the current generation's state.
        self.assertEqual(
            self.payload["production_authority_generation_id"],
            lc.CURRENT_GENERATION.generation_id,
        )
        accepted = current_record_present()
        self.assertEqual(
            self.payload["u06_accepted_lifecycle"]["accepted_lifecycle_overlay"],
            "PRESENT_VALID" if accepted else "ABSENT",
        )
        self.assertEqual(
            self.payload["u06_accepted_lifecycle"][
                "production_authority_freeze_status"
            ],
            "FROZEN" if accepted else "NOT_FROZEN",
        )
        self.assertEqual(
            self.payload["v7_4_authority_alignment"]["alignment_status"],
            "CANDIDATE_ALIGNED",
        )

    def test_stack_payload_carries_the_audited_dependency_report(self) -> None:
        report = self.payload["u06_runtime_dependency_report"]
        # R3-AUD-04: derived from the current generation, not the U-06 R3
        # constant this previously compared against.
        self.assertEqual(report["lineage_id"], lc.CURRENT_GENERATION.lineage_id)
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
