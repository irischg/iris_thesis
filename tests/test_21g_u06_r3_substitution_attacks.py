"""A-01 regression suite: arbitrary-artifact substitution must be rejected.

U-06 Candidate R2 received ``NO-GO — CRITICAL GOVERNANCE DEFECT`` because
arbitrary unrelated tracked / clean / hash-correct historical artifacts could
satisfy the five lifecycle roles and produce ``PRODUCTION_AUTHORITY_FROZEN``.
R2 proved only **file identity**; it never proved **artifact role
authenticity**.

Every attack below uses **real repository artifacts** — genuinely tracked,
genuinely clean, genuinely hash-correct, genuinely published in
``origin/thesis-v7`` ancestry — that are simply not the U-06 R3 lifecycle. The
headline test reproduces the independent auditor's exact attack: five distinct
such artifacts, each individually above suspicion, assembled into a lifecycle.

Nothing here writes a file. Every payload is an in-memory mapping handed to the
pure validator, so no fake acceptance artifact is created in the repository and
the live gate is unaffected. No model is constructed, no optimizer is called,
no subprocess is spawned beyond read-only Git queries, and the production
execution flag is never written as a literal.

Implementing these defences does **not** close A-01. Only a fresh independent
audit can do that.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402


RECORD_REL = lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()

#: Real, tracked, clean, published governance artifacts that have nothing to do
#: with the U-06 R3 lifecycle. Deliberately chosen to *look* like the roles they
#: are being substituted into: a closure document for the closure role, an audit
#: document for the audit role, an acceptance manifest for the manifest role,
#: and a content-freeze document for the re-freeze role.
UNRELATED_HISTORICAL = {
    "checkpoint": "docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md",
    "audit": (
        "docs/checkpoints/"
        "literature_evidence_registry_v7_4_independent_audit_2026-09-26.md"
    ),
    "closure": (
        "docs/checkpoints/"
        "literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md"
    ),
    "manifest": (
        "results/provenance/"
        "literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/"
        "acceptance_manifest.json"
    ),
    "freeze": "docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md",
    "other_manifest": (
        "results/provenance/"
        "framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json"
    ),
    "other_closure": (
        "docs/checkpoints/"
        "layer_a_robustness_preregistration_candidate_r2_acceptance_closure_"
        "2026-09-27.md"
    ),
    "other_json": (
        "results/provenance/"
        "layer_a_robustness_preregistration_candidate_r2_acceptance_closure_"
        "2026-09-27/acceptance_manifest.json"
    ),
}

#: Statuses that mean "rejected for being the wrong artifact", as distinct from
#: "rejected for a bad digest". A-01 closure requires the former.
SUBSTITUTION_STATUSES = {
    "U06_ROLE_ARTIFACT_NOT_JSON",
    "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
    "U06_ROLE_SCHEMA_MISMATCH",
    "U06_ROLE_SCHEMA_INVALID",
    "U06_LINEAGE_MISMATCH",
    "U06_ROLE_TARGET_MISMATCH",
    "U06_SUPERSEDED_CANDIDATE_REJECTED",
    "U06_SELF_ACCEPTANCE_REJECTED",
    "U06_ROLE_ALIASING_REJECTED",
}


def sha(rel: str) -> str:
    return authority.sha256_file(ROOT / rel)


def git_ok(*args: str) -> bool:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True
    ).returncode == 0


class UnrelatedArtifactPremiseTests(unittest.TestCase):
    """The attack is only meaningful if the substitutes are genuinely credible."""

    def test_every_substitute_is_real_tracked_clean_and_published(self) -> None:
        upstream = "origin/thesis-v7"
        for label, rel in UNRELATED_HISTORICAL.items():
            with self.subTest(artifact=label):
                path = ROOT / rel
                self.assertTrue(path.is_file(), rel)
                tracked, clean = lc.is_tracked_and_clean(ROOT, rel)
                self.assertTrue(tracked, f"{rel} must be tracked")
                self.assertTrue(clean, f"{rel} must be clean")
                # Present in HEAD with bytes matching the working tree.
                self.assertEqual(lc.blob_sha256_at(ROOT, "HEAD", rel), sha(rel))
                # And genuinely published.
                introduced = lc.last_modifying_commit(ROOT, rel)
                self.assertIsNotNone(introduced)
                self.assertTrue(git_ok("merge-base", "--is-ancestor", introduced, upstream))

    def test_substitutes_are_not_u06_r3_artifacts(self) -> None:
        for rel in UNRELATED_HISTORICAL.values():
            self.assertNotIn(rel, lc.CANDIDATE_ARTIFACT_PATHS)
            self.assertNotEqual(rel, lc.R3_CANDIDATE_CHECKPOINT_PATH)
            self.assertNotEqual(rel, lc.R3_CANDIDATE_MANIFEST_PATH)


def role_entry(rel: str) -> dict:
    return {"path": rel, "sha256": sha(rel)}


def lifecycle_payload(roles: dict) -> dict:
    """An otherwise maximally cooperative accepted-lifecycle record."""

    return {
        "artifact_type": lc.ACCEPTED_LIFECYCLE_ARTIFACT_TYPE,
        "schema_version": lc.LIFECYCLE_RECORD_SCHEMA_VERSION,
        "lineage_id": lc.LINEAGE_ID,
        "target_candidate_id": lc.R3_CANDIDATE_ID,
        "u06_alignment_status": "ACCEPTED",
        "u06_independent_audit_status": "PASS",
        "u06_acceptance_status": "CLOSED_ACCEPTED",
        "production_authority_freeze_status": "FROZEN",
        "authorizes_main_full81": False,
        "implementation_identity_digest": lc.implementation_identity_digest(ROOT),
        "roles": roles,
    }


def reject(testcase, payload) -> str:
    with testcase.assertRaises(lc.U06LifecycleError) as caught:
        lc.validate_accepted_lifecycle_payload(
            ROOT, payload, record_relative=RECORD_REL
        )
    return caught.exception.status


class FiveArtifactAttackTests(unittest.TestCase):
    """The independent auditor's exact attack, as a regression test."""

    def test_five_unrelated_published_historical_artifacts_are_rejected(self) -> None:
        """Five distinct, tracked, clean, hash-correct, published artifacts.

        Each is a genuine accepted governance document. None is U-06 R3. The
        lifecycle must be rejected for lineage/schema/target reasons, not for a
        digest mismatch.
        """

        roles = {
            "implementation_candidate": role_entry(
                UNRELATED_HISTORICAL["checkpoint"]
            ),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": role_entry(UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": role_entry(
                UNRELATED_HISTORICAL["freeze"]
            ),
        }
        payload = lifecycle_payload(roles)

        # Every declared digest is genuinely correct — this is not a hash attack.
        for role, entry in roles.items():
            with self.subTest(role=role):
                self.assertEqual(entry["sha256"], sha(entry["path"]))

        status = reject(self, payload)
        self.assertIn(status, SUBSTITUTION_STATUSES)
        self.assertNotIn("HASH_FAIL", status)

    def test_attack_with_a_correct_candidate_role_still_fails_at_the_audit(
        self,
    ) -> None:
        """Even granting the real R3 candidate, unrelated later roles fail."""

        roles = {
            "implementation_candidate": role_entry(lc.R3_CANDIDATE_MANIFEST_PATH),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": role_entry(UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": role_entry(
                UNRELATED_HISTORICAL["freeze"]
            ),
        }
        status = reject(self, lifecycle_payload(roles))
        self.assertIn(status, SUBSTITUTION_STATUSES)

    def test_all_json_substitution_is_rejected_on_artifact_type(self) -> None:
        """Using only real JSON manifests removes the not-JSON escape hatch."""

        roles = {
            "implementation_candidate": role_entry(lc.R3_CANDIDATE_MANIFEST_PATH),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["manifest"]),
            "acceptance_closure": role_entry(
                UNRELATED_HISTORICAL["other_manifest"]
            ),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["other_json"]),
            "production_authority_re_freeze": role_entry(
                UNRELATED_HISTORICAL["closure"]
            ),
        }
        status = reject(self, lifecycle_payload(roles))
        self.assertIn(
            status,
            {"U06_ROLE_ARTIFACT_TYPE_MISMATCH", "U06_ROLE_SCHEMA_MISMATCH"},
        )


class PerRoleSubstitutionTests(unittest.TestCase):
    """Each role individually must resist substitution."""

    def base_roles(self) -> dict:
        return {
            "implementation_candidate": role_entry(lc.R3_CANDIDATE_MANIFEST_PATH),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": role_entry(UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": role_entry(
                UNRELATED_HISTORICAL["freeze"]
            ),
        }

    def test_unrelated_checkpoint_as_candidate_is_rejected(self) -> None:
        roles = self.base_roles()
        roles["implementation_candidate"] = role_entry(
            UNRELATED_HISTORICAL["checkpoint"]
        )
        self.assertEqual(
            reject(self, lifecycle_payload(roles)), "U06_ROLE_TARGET_MISMATCH"
        )

    def test_superseded_r1_and_r2_candidates_are_rejected(self) -> None:
        for rel in (
            "docs/checkpoints/"
            "u_06_v7_4_production_authority_alignment_candidate_2026-10-02.md",
            "docs/checkpoints/"
            "u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02.md",
        ):
            with self.subTest(candidate=rel):
                roles = self.base_roles()
                roles["implementation_candidate"] = {
                    "path": rel,
                    "sha256": sha(rel),
                }
                self.assertEqual(
                    reject(self, lifecycle_payload(roles)),
                    "U06_ROLE_TARGET_MISMATCH",
                )

    def test_candidate_artifacts_cannot_fill_later_roles(self) -> None:
        for role in lc.NON_SELF_ACCEPTABLE_ROLES:
            for rel in lc.CANDIDATE_ARTIFACT_PATHS:
                if not (ROOT / rel).is_file():
                    continue
                with self.subTest(role=role, path=rel):
                    roles = self.base_roles()
                    roles[role] = {"path": rel, "sha256": sha(rel)}
                    self.assertEqual(
                        reject(self, lifecycle_payload(roles)),
                        "U06_SELF_ACCEPTANCE_REJECTED",
                    )

    def test_production_code_and_tests_cannot_fill_later_roles(self) -> None:
        for role in lc.NON_SELF_ACCEPTABLE_ROLES:
            for rel in (
                "src/production_authority_lifecycle_u06.py",
                "scripts/21e_preflight_v7_4_production_authority_alignment.py",
                "tests/test_21g_u06_r3_substitution_attacks.py",
            ):
                with self.subTest(role=role, path=rel):
                    roles = self.base_roles()
                    roles[role] = {"path": rel, "sha256": sha(rel)}
                    self.assertEqual(
                        reject(self, lifecycle_payload(roles)),
                        "U06_SELF_ACCEPTANCE_REJECTED",
                    )

    def test_role_aliasing_is_rejected(self) -> None:
        roles = self.base_roles()
        shared = role_entry(UNRELATED_HISTORICAL["closure"])
        roles["acceptance_closure"] = dict(shared)
        roles["acceptance_manifest"] = dict(shared)
        self.assertEqual(
            reject(self, lifecycle_payload(roles)), "U06_ROLE_ALIASING_REJECTED"
        )

    def test_a_declared_digest_that_does_not_match_live_bytes_is_rejected(
        self,
    ) -> None:
        roles = self.base_roles()
        roles["independent_audit_pass"] = {
            "path": UNRELATED_HISTORICAL["audit"],
            "sha256": "0" * 64,
        }
        self.assertEqual(
            reject(self, lifecycle_payload(roles)), "U06_ROLE_TARGET_MISMATCH"
        )

    def test_missing_role_and_unknown_role_are_rejected(self) -> None:
        roles = self.base_roles()
        roles.pop("acceptance_manifest")
        self.assertEqual(
            reject(self, lifecycle_payload(roles)),
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
        )
        roles = self.base_roles()
        roles["something_else"] = role_entry(UNRELATED_HISTORICAL["freeze"])
        self.assertEqual(
            reject(self, lifecycle_payload(roles)), "U06_LIFECYCLE_RECORD_INVALID"
        )


class LifecycleEnvelopeAttackTests(unittest.TestCase):
    """The aggregating record itself must carry the right identity."""

    def roles(self) -> dict:
        return {
            "implementation_candidate": role_entry(lc.R3_CANDIDATE_MANIFEST_PATH),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": role_entry(UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": role_entry(
                UNRELATED_HISTORICAL["freeze"]
            ),
        }

    def test_wrong_artifact_type_is_rejected(self) -> None:
        payload = lifecycle_payload(self.roles())
        payload["artifact_type"] = "U06_ACCEPTANCE_CLOSURE"
        self.assertEqual(reject(self, payload), "U06_ROLE_ARTIFACT_TYPE_MISMATCH")

    def test_wrong_schema_version_is_rejected(self) -> None:
        payload = lifecycle_payload(self.roles())
        payload["schema_version"] = "iris-thesis-u06-r2-accepted-lifecycle-v1"
        self.assertEqual(reject(self, payload), "U06_ROLE_SCHEMA_MISMATCH")

    def test_wrong_lineage_is_rejected(self) -> None:
        for lineage in (
            "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R2",
            "SOMETHING_ELSE",
            None,
        ):
            with self.subTest(lineage=lineage):
                payload = lifecycle_payload(self.roles())
                payload["lineage_id"] = lineage
                self.assertEqual(reject(self, payload), "U06_LINEAGE_MISMATCH")

    def test_superseded_target_candidate_is_rejected(self) -> None:
        for target in lc.SUPERSEDED_CANDIDATE_IDS:
            with self.subTest(target=target):
                payload = lifecycle_payload(self.roles())
                payload["target_candidate_id"] = target
                self.assertEqual(reject(self, payload), "U06_ROLE_TARGET_MISMATCH")

    def test_non_accepted_statuses_are_rejected(self) -> None:
        for field in (
            "u06_alignment_status",
            "u06_independent_audit_status",
            "u06_acceptance_status",
            "production_authority_freeze_status",
        ):
            with self.subTest(field=field):
                payload = lifecycle_payload(self.roles())
                payload[field] = "CANDIDATE"
                self.assertEqual(reject(self, payload), "U06_LIFECYCLE_NOT_ACCEPTED")

    def test_a_lifecycle_claiming_full81_authority_is_rejected(self) -> None:
        payload = lifecycle_payload(self.roles())
        payload["authorizes_main_full81"] = True
        self.assertEqual(reject(self, payload), "U06_RE_FREEZE_OVERREACH")

    def test_stale_implementation_identity_digest_is_rejected(self) -> None:
        payload = lifecycle_payload(self.roles())
        payload["implementation_identity_digest"] = "0" * 64
        self.assertEqual(
            reject(self, payload), "U06_IMPLEMENTATION_IDENTITY_DRIFT"
        )


class PublicationProofAttackTests(unittest.TestCase):
    """A-03: an arbitrary ancestor is not proof of publication."""

    def test_arbitrary_ancestor_is_not_proof_for_a_file_absent_there(self) -> None:
        """The R3 candidate did not exist in any published commit."""

        head = lc._git_text(ROOT, "rev-parse", "HEAD")
        self.assertIsNotNone(head)
        # HEAD is a genuine ancestor of HEAD, yet the R3 candidate is untracked
        # and therefore absent from that commit: containment must fail.
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_published_in_commit(
                ROOT,
                head,
                lc.R3_CANDIDATE_CHECKPOINT_PATH,
                sha(lc.R3_CANDIDATE_CHECKPOINT_PATH),
                label="attack",
            )
        self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")
        self.assertIn("does not exist in commit", str(caught.exception))

    def test_a_commit_predating_an_artifact_is_rejected(self) -> None:
        """A real older ancestor cannot vouch for a later artifact."""

        target = UNRELATED_HISTORICAL["manifest"]
        introduced = lc.last_modifying_commit(ROOT, target)
        self.assertIsNotNone(introduced)
        parent = lc._git_text(ROOT, "rev-parse", f"{introduced}^")
        if not parent:
            self.skipTest("no parent commit available")
        self.assertTrue(git_ok("merge-base", "--is-ancestor", parent, "HEAD"))
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_published_in_commit(
                ROOT, parent, target, sha(target), label="attack"
            )
        self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")

    def test_wrong_bytes_in_the_named_commit_are_rejected(self) -> None:
        target = UNRELATED_HISTORICAL["manifest"]
        introduced = lc.last_modifying_commit(ROOT, target)
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_published_in_commit(
                ROOT, introduced, target, "0" * 64, label="attack"
            )
        self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")

    def test_a_genuinely_contained_artifact_is_accepted(self) -> None:
        """The containment check is not vacuous."""

        target = UNRELATED_HISTORICAL["manifest"]
        introduced = lc.last_modifying_commit(ROOT, target)
        lc.require_published_in_commit(
            ROOT, introduced, target, sha(target), label="premise"
        )

    def test_untracked_r3_artifacts_are_not_published_in_head(self) -> None:
        for rel in (
            lc.R3_CANDIDATE_CHECKPOINT_PATH,
            "src/production_authority_lifecycle_u06.py",
        ):
            with self.subTest(path=rel):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.require_published_in_head(
                        ROOT, rel, sha(rel), label="attack"
                    )
                self.assertEqual(
                    caught.exception.status, "U06_LIFECYCLE_NOT_PUBLISHED"
                )

    def test_upstream_synchronization_is_checked(self) -> None:
        synced, reason = lc.upstream_synchronized(ROOT)
        self.assertTrue(synced, reason)
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_published_in_commit(
                ROOT, "f" * 40, UNRELATED_HISTORICAL["manifest"],
                sha(UNRELATED_HISTORICAL["manifest"]), label="attack",
            )
        self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")


class NoFabricatedFutureIdentityTests(unittest.TestCase):
    """Nothing about the future is invented, and nothing accepted exists."""

    def test_overlay_module_contains_no_digest_literal(self) -> None:
        import re

        source = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", source), [])

    def test_no_lifecycle_artifact_exists_yet(self) -> None:
        self.assertFalse(
            (ROOT / lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH).exists()
        )
        requirements = lc.future_acceptance_requirements()
        self.assertFalse(requirements["record_exists_today"])
        self.assertFalse(requirements["future_hashes_fabricated_now"])
        self.assertFalse(requirements["placeholder_digests_present"])
        self.assertFalse(
            requirements["arbitrary_ancestor_accepted_as_publication_proof"]
        )
        self.assertFalse(requirements["self_referential_commit_hash_required"])

    def test_role_contracts_have_distinct_types_and_schemas(self) -> None:
        types = [c.artifact_type for c in lc.ROLE_CONTRACTS.values()]
        schemas = [c.schema_version for c in lc.ROLE_CONTRACTS.values()]
        self.assertEqual(len(types), len(set(types)))
        self.assertEqual(len(schemas), len(set(schemas)))
        self.assertNotIn(lc.ACCEPTED_LIFECYCLE_ARTIFACT_TYPE, types)
        self.assertNotIn(lc.LIFECYCLE_RECORD_SCHEMA_VERSION, schemas)
        self.assertEqual(
            list(lc.REQUIRED_ACCEPTED_ROLES),
            [
                "implementation_candidate",
                "independent_audit_pass",
                "acceptance_closure",
                "acceptance_manifest",
                "production_authority_re_freeze",
            ],
        )

    def test_a_01_is_not_claimed_closed(self) -> None:
        record = lc.CANDIDATE_R2_AUDIT_RECORD
        self.assertEqual(
            record["independent_audit_verdict"], "NO_GO_CRITICAL_GOVERNANCE_DEFECT"
        )
        for finding in ("A-01", "A-02", "A-03"):
            with self.subTest(finding=finding):
                status = record["findings"][finding]["remediation_status"]
                self.assertIn("PENDING_FRESH_INDEPENDENT_VERIFICATION", status)
                self.assertNotIn("CLOSED", status)
        self.assertFalse(lc.CANDIDATE_R1_AUDIT_RECORD["f_01_closed"])
        self.assertIn(
            "CLOSURE_REQUIRES_FRESH_INDEPENDENT_AUDIT",
            lc.CANDIDATE_R1_AUDIT_RECORD["f_01_status"],
        )


class GateStillFailsClosedTests(unittest.TestCase):
    """No substitution attempt can move the live gate."""

    def test_live_gate_rejects_every_production_scope(self) -> None:
        snapshot = stack.inspect_deployment_snapshot(ROOT)
        self.assertFalse(lc.is_frozen(snapshot.u06_accepted_lifecycle))
        for scope, expected in (
            ("core-three", "U06_ACCEPTED_LIFECYCLE_ABSENT"),
            ("eob", "U06_ACCEPTED_LIFECYCLE_ABSENT"),
            ("full81", "FULL81_AUTHORIZATION_NOT_GRANTED"),
            ("a2_variable_floor", "A2_HARD_BLOCKED"),
        ):
            with self.subTest(scope=scope):
                with self.assertRaises(stack.ProductionAuthorityError) as caught:
                    stack.validate_deployment_snapshot(
                        snapshot,
                        execute_production=True,
                        selected_scope=scope,
                        root=ROOT,
                    )
                self.assertEqual(caught.exception.status, expected)

    def test_resolver_writes_nothing_and_never_raises(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace",
        ).stdout
        resolved = lc.resolve_u06_lifecycle(ROOT)
        after = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace",
        ).stdout
        self.assertEqual(before, after)
        self.assertEqual(resolved["accepted_lifecycle_overlay"], "ABSENT")
        json.dumps(stack._json_safe(resolved), sort_keys=True)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
