"""A-01 regression suite: arbitrary-artifact substitution must be rejected.

U-06 Candidate R2 received ``NO-GO — CRITICAL GOVERNANCE DEFECT`` because
arbitrary unrelated tracked / clean / hash-correct historical artifacts could
satisfy the five lifecycle roles and produce ``PRODUCTION_AUTHORITY_FROZEN``.
R2 proved only **file identity**; it never proved **artifact role
authenticity**.

Every attack below uses **real repository artifacts** — genuinely tracked,
genuinely clean, genuinely hash-correct, genuinely published in
``origin/thesis-v7`` ancestry — that are simply not the current lifecycle. The
headline test reproduces the independent auditor's exact attack: five distinct
such artifacts, each individually above suspicion, assembled into a lifecycle.

Current Full81 Production Generation G1.  G1 predeclares the exact path of every
future role record, so an unrelated artifact offered at any OTHER path is now
refused structurally (pass 1) before its content is read.  That is an additional
defence, and it must not hide the role-authenticity layer A-01 is about.  The
attacks are therefore run at BOTH layers:

* structural attacks run against the real repository, as before;
* authenticity attacks place the unrelated published artifacts AT the G1
  predeclared role paths, inside a disposable repository that carries a valid
  G1 candidate package (``tests/test_21l``), so the candidate role validates and
  the chain is forced through to the role-authenticity checks.

Nothing here writes to the real repository. Every real-repository payload is an
in-memory mapping handed to the pure validator; every written file lives in a
throwaway fixture under the system temp directory. No model is constructed, no
optimizer is called, and the production execution flag is never written as a
literal.

Implementing these defences does **not** close A-01. Only a fresh independent
audit can do that.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from contextlib import contextmanager
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import main_full81_authorization_v7_4 as auth  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from src import production_input_authority_v7_3 as authority  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402
from tests.test_21l_full81_production_generation_g1 import G1Fixture  # noqa: E402


#: R3-AUD-04. This suite was written when U-06 R3 was the CURRENT generation,
#: so it drove the validator with a U-06 R3 payload and compared against the
#: U-06 R3 record slot. U-06 R3 has since been lawfully audited, accepted,
#: frozen, published and superseded. Replaying the A-01 attack against it can
#: no longer reach the role-authenticity layer the attack exists to test: the
#: accepted U-06 R3 candidate manifest declares the implementation digest it
#: was accepted with, the live implementation surface has lawfully advanced,
#: and the chain now stops at ``U06_IMPLEMENTATION_IDENTITY_DRIFT`` first. The
#: attack was still rejected — but on a different, earlier ground, so the
#: assertions no longer proved what they claim to prove.
#:
#: The remedy is to aim the attack at the generation it is about. A-01 is a
#: property of the CURRENT lifecycle, so the attack payload is now built from
#: ``lc.CURRENT_GENERATION``, whose candidate manifest declares the live
#: implementation digest and therefore lets the chain reach the role checks.
#: The U-06 R3 variants are retained below as explicitly HISTORICAL controls
#: proving a superseded generation can never authorise. No negative control
#: was deleted, no guard was weakened, and no validator is mocked.
#:
#: G1: ``GEN`` is now Current Full81 Production Generation G1, and the R8
#: generation joins U-06 R3 as an explicitly historical control.
GEN = lc.CURRENT_GENERATION
HISTORICAL_GEN = lc.U06_R3_GENERATION
R8_GEN = lc.GENERATIONS_BY_ID["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1"]

RECORD_REL = GEN.accepted_lifecycle_record_path
HISTORICAL_RECORD_REL = lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()

#: Real, tracked, clean, published governance artifacts that have nothing to do
#: with the current lifecycle. Deliberately chosen to *look* like the roles they
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

#: Statuses of the role-AUTHENTICITY layer (pass 2), as distinct from the
#: structural path layer (pass 1).  The fixture attacks must stop here.
AUTHENTICITY_STATUSES = {
    "U06_ROLE_ARTIFACT_NOT_JSON",
    "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
    "U06_ROLE_SCHEMA_MISMATCH",
    "U06_LINEAGE_MISMATCH",
}


def sha(rel: str, root: Path = ROOT) -> str:
    return authority.sha256_file(root / rel)


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

    def test_substitutes_are_not_current_or_historical_lifecycle_artifacts(self) -> None:
        for rel in UNRELATED_HISTORICAL.values():
            self.assertNotIn(rel, lc.CANDIDATE_ARTIFACT_PATHS)
            self.assertNotIn(rel, GEN.candidate_artifact_paths)
            self.assertNotIn(rel, (GEN.role_record_path_map or {}).values())
            self.assertNotEqual(rel, lc.R3_CANDIDATE_CHECKPOINT_PATH)
            self.assertNotEqual(rel, lc.R3_CANDIDATE_MANIFEST_PATH)


def role_entry(rel: str, root: Path = ROOT) -> dict:
    return {"path": rel, "sha256": sha(rel, root)}


def candidate_entry() -> dict:
    """The current candidate-role entry, for STRUCTURAL (pass-1) attacks only.

    Pass 1 validates every role's PATH before any role's bytes are read, so a
    structural attack is decided without the candidate manifest's content.
    Before the G1 package exists the digest is a syntactically valid
    stand-in; the attacks that need the candidate role to VALIDATE run in the
    disposable fixture below instead.
    """

    path = ROOT / GEN.candidate_manifest_path
    return {
        "path": GEN.candidate_manifest_path,
        "sha256": sha(GEN.candidate_manifest_path) if path.is_file() else "0" * 64,
    }


def lifecycle_payload(roles: dict, generation=GEN, root: Path = ROOT) -> dict:
    """An otherwise maximally cooperative accepted-lifecycle record.

    Every envelope field is derived from ``generation``, so the payload is a
    *credible* acceptance of that generation and the attack is forced through
    to the role-authenticity layer rather than bouncing off the envelope.
    """

    return {
        "artifact_type": generation.lifecycle_record_artifact_type,
        "schema_version": generation.lifecycle_record_schema_version,
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
        "u06_alignment_status": "ACCEPTED",
        "u06_independent_audit_status": "PASS",
        "u06_acceptance_status": "CLOSED_ACCEPTED",
        "production_authority_freeze_status": "FROZEN",
        "authorizes_main_full81": False,
        "implementation_identity_digest": lc.implementation_identity_digest(root),
        "roles": roles,
    }


def reject(testcase, payload, *, generation=GEN, record_relative=None, root: Path = ROOT) -> str:
    with testcase.assertRaises(lc.U06LifecycleError) as caught:
        lc.validate_accepted_lifecycle_payload(
            root,
            payload,
            record_relative=record_relative
            or generation.accepted_lifecycle_record_path,
            generation=generation,
        )
    return caught.exception.status


def base_roles() -> dict:
    """The STRUCTURAL attack base: every role at its lawful G1 path.

    Pass 1 accepts or refuses on path alone, in role order, before any byte is
    read.  The base therefore puts roles 2-5 at their predeclared paths with
    distinct stand-in digests, so the ONE substituted role an attack changes is
    the first role pass 1 can refuse - and the refusal names that attack.
    Content-level substitution is attacked separately, in the fixture.
    """

    roles = {"implementation_candidate": candidate_entry()}
    for index, (role, path) in enumerate(GEN.role_record_path_map.items(), start=1):
        roles[role] = {"path": path, "sha256": str(index) * 64}
    return roles


class _AuthenticityFixture(unittest.TestCase):
    """A disposable repository with a VALID G1 candidate package.

    The unrelated published artifacts are copied in, and an attack places
    their exact bytes at the G1 PREDECLARED role paths, so pass 1 accepts the
    paths and the candidate role validates; only role authenticity can refuse.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(
            stage="package", extra_paths=tuple(UNRELATED_HISTORICAL.values())
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def place(self, role: str, source: str) -> dict:
        target = GEN.role_record_path_map[role]
        destination = self.fixture.root / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.fixture.root / source, destination)
        return role_entry(target, self.fixture.root)

    def candidate(self) -> dict:
        return role_entry(GEN.candidate_manifest_path, self.fixture.root)

    def reject_here(self, roles: dict) -> str:
        return reject(self, lifecycle_payload(roles, root=self.fixture.root), root=self.fixture.root)


class FiveArtifactAttackTests(_AuthenticityFixture):
    """The independent auditor's exact attack, as a regression test."""

    def test_five_unrelated_published_historical_artifacts_are_rejected(self) -> None:
        """Five distinct, tracked, clean, hash-correct, published artifacts.

        Each is a genuine accepted governance document. None is a current
        lifecycle artifact. The lifecycle must be rejected for lineage/schema/
        target reasons, not for a digest mismatch.
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
        """Even granting the real candidate, unrelated later roles fail.

        G1: the unrelated bytes sit AT the predeclared role paths, so the
        refusal comes from role authenticity, not from the path.
        """

        roles = {
            "implementation_candidate": self.candidate(),
            "independent_audit_pass": self.place("independent_audit_pass", UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": self.place("acceptance_closure", UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": self.place("acceptance_manifest", UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": self.place(
                "production_authority_re_freeze", UNRELATED_HISTORICAL["freeze"]
            ),
        }
        status = self.reject_here(roles)
        self.assertIn(status, AUTHENTICITY_STATUSES)

    def test_all_json_substitution_is_rejected_on_artifact_type(self) -> None:
        """Using only real JSON manifests removes the not-JSON escape hatch."""

        roles = {
            "implementation_candidate": self.candidate(),
            "independent_audit_pass": self.place("independent_audit_pass", UNRELATED_HISTORICAL["manifest"]),
            "acceptance_closure": self.place("acceptance_closure", UNRELATED_HISTORICAL["other_manifest"]),
            "acceptance_manifest": self.place("acceptance_manifest", UNRELATED_HISTORICAL["other_json"]),
            "production_authority_re_freeze": self.place(
                "production_authority_re_freeze", UNRELATED_HISTORICAL["closure"]
            ),
        }
        status = self.reject_here(roles)
        self.assertIn(
            status,
            {"U06_ROLE_ARTIFACT_TYPE_MISMATCH", "U06_ROLE_SCHEMA_MISMATCH"},
        )

    def test_the_candidate_role_itself_validates_in_the_fixture(self) -> None:
        """Premise of the two attacks above: the chain reaches role 2."""

        record = json.loads(
            (self.fixture.root / GEN.candidate_manifest_path).read_text(encoding="utf-8")
        )
        lc.validate_role_envelope(
            self.fixture.root,
            "implementation_candidate",
            GEN.candidate_manifest_path,
            record,
            live_digest=lc.implementation_identity_digest(self.fixture.root),
            generation=GEN,
        )
        lc.validate_role_specifics(
            self.fixture.root, "implementation_candidate", GEN.candidate_manifest_path,
            record, {}, GEN,
        )


class PerRoleSubstitutionTests(unittest.TestCase):
    """Each role individually must resist substitution."""

    def base_roles(self) -> dict:
        return base_roles()

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
            # G1: the accepted-and-superseded R8 candidate manifest too.
            R8_GEN.candidate_manifest_path,
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
        # R3-AUD-04: the barred set is the CURRENT generation's own cumulative
        # list, which already contains every U-06 R3 candidate artifact this
        # previously used plus every later candidate's. Strictly more coverage.
        # G1: it now also contains every R8-generation candidate artifact.
        for role in lc.NON_SELF_ACCEPTABLE_ROLES:
            for rel in GEN.candidate_artifact_paths:
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

    def test_unrelated_artifacts_off_the_predeclared_paths_are_rejected(self) -> None:
        """G1 structural defence: a role is lawful only at its predeclared path."""

        for role, source in (
            ("independent_audit_pass", UNRELATED_HISTORICAL["audit"]),
            ("acceptance_closure", UNRELATED_HISTORICAL["closure"]),
            ("acceptance_manifest", UNRELATED_HISTORICAL["manifest"]),
            ("production_authority_re_freeze", UNRELATED_HISTORICAL["freeze"]),
        ):
            with self.subTest(role=role):
                roles = self.base_roles()
                roles[role] = role_entry(source)
                self.assertEqual(
                    reject(self, lifecycle_payload(roles)), "U06_ROLE_TARGET_MISMATCH"
                )

    def test_role_aliasing_is_rejected(self) -> None:
        # G1: aliasing one file into two roles is refused even earlier, because
        # two roles can never share one predeclared path.
        roles = self.base_roles()
        shared = {"path": GEN.role_record_path_map["acceptance_closure"], "sha256": "1" * 64}
        roles["acceptance_closure"] = dict(shared)
        roles["acceptance_manifest"] = dict(shared)
        self.assertEqual(
            reject(self, lifecycle_payload(roles)), "U06_ROLE_TARGET_MISMATCH"
        )

    def test_role_aliasing_is_rejected_by_the_generation_independent_guard(self) -> None:
        """HISTORICAL control: the aliasing guard itself, on a generation that
        predeclares no role paths (R8), so nothing earlier can mask it."""

        roles = {
            "implementation_candidate": role_entry(R8_GEN.candidate_manifest_path),
            "independent_audit_pass": role_entry(UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": role_entry(UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": role_entry(UNRELATED_HISTORICAL["closure"]),
            "production_authority_re_freeze": role_entry(UNRELATED_HISTORICAL["freeze"]),
        }
        self.assertEqual(
            reject(self, lifecycle_payload(roles, R8_GEN), generation=R8_GEN),
            "U06_ROLE_ALIASING_REJECTED",
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


class DeclaredDigestAttackTests(_AuthenticityFixture):
    """A declared digest that does not match the bytes at the path is refused."""

    def test_a_declared_digest_that_does_not_match_live_bytes_is_rejected(
        self,
    ) -> None:
        roles = {
            "implementation_candidate": self.candidate(),
            "independent_audit_pass": self.place("independent_audit_pass", UNRELATED_HISTORICAL["audit"]),
            "acceptance_closure": self.place("acceptance_closure", UNRELATED_HISTORICAL["closure"]),
            "acceptance_manifest": self.place("acceptance_manifest", UNRELATED_HISTORICAL["manifest"]),
            "production_authority_re_freeze": self.place(
                "production_authority_re_freeze", UNRELATED_HISTORICAL["freeze"]
            ),
        }
        roles["independent_audit_pass"] = {
            "path": roles["independent_audit_pass"]["path"],
            "sha256": "0" * 64,
        }
        self.assertEqual(self.reject_here(roles), "U06_ROLE_TARGET_MISMATCH")


class LifecycleEnvelopeAttackTests(unittest.TestCase):
    """The aggregating record itself must carry the right identity."""

    def roles(self) -> dict:
        return base_roles()

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
            R8_GEN.lineage_id,
            "SOMETHING_ELSE",
            None,
        ):
            with self.subTest(lineage=lineage):
                payload = lifecycle_payload(self.roles())
                payload["lineage_id"] = lineage
                self.assertEqual(reject(self, payload), "U06_LINEAGE_MISMATCH")

    def test_superseded_target_candidate_is_rejected(self) -> None:
        for target in (*lc.SUPERSEDED_CANDIDATE_IDS, R8_GEN.candidate_id):
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

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(stage="package")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def test_arbitrary_ancestor_is_not_proof_for_a_file_absent_there(self) -> None:
        """An artifact absent from a genuine ancestor is not published there.

        R3-AUD-04 / G1: this used whichever candidate artifact happened to be
        untracked in the real repository, so each lawful publication turned the
        premise false.  The attack now authors a live, unpublished role record
        in a disposable repository, where the premise holds in every phase.
        """

        root = self.fixture.root
        head = self.fixture.head()
        candidate = GEN.role_record_path_map["independent_audit_pass"]
        self.fixture.write(candidate, {"artifact_type": "UNPUBLISHED"})
        try:
            # Premise: it really is absent from HEAD right now.
            self.assertIsNone(lc.blob_sha256_at(root, "HEAD", candidate))
            # HEAD is a genuine ancestor of HEAD, yet the artifact is absent
            # from that commit: containment must fail.
            with self.assertRaises(lc.U06LifecycleError) as caught:
                lc.require_published_in_commit(
                    root, head, candidate, sha(candidate, root), label="attack"
                )
            self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")
            self.assertIn("does not exist in commit", str(caught.exception))
        finally:
            (root / candidate).unlink()

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

    def test_untracked_candidate_artifacts_are_not_published_in_head(self) -> None:
        # R3-AUD-04 / G1: three controls in a disposable repository, so the
        # premise cannot be turned false by a lawful real publication: an
        # untracked future role record, a candidate checkpoint edited after its
        # commit, and a live-modified overlay.
        root = self.fixture.root
        untracked = GEN.role_record_path_map["acceptance_closure"]
        edited = (
            GEN.candidate_checkpoint_path,
            "src/production_authority_lifecycle_u06.py",
        )
        originals = {rel: (root / rel).read_bytes() for rel in edited}
        self.fixture.write(untracked, {"artifact_type": "UNPUBLISHED"})
        try:
            for rel in edited:
                (root / rel).write_bytes(originals[rel] + b"\n# drift\n")
            for rel in (untracked, *edited):
                with self.subTest(path=rel):
                    with self.assertRaises(lc.U06LifecycleError) as caught:
                        lc.require_published_in_head(
                            root, rel, sha(rel, root), label="attack"
                        )
                    self.assertEqual(
                        caught.exception.status, "U06_LIFECYCLE_NOT_PUBLISHED"
                    )
        finally:
            (root / untracked).unlink()
            for rel, data in originals.items():
                (root / rel).write_bytes(data)

    def test_upstream_synchronization_is_checked(self) -> None:
        synced, reason = lc.upstream_synchronized(self.fixture.root)
        self.assertTrue(synced, reason)
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_published_in_commit(
                ROOT, "f" * 40, UNRELATED_HISTORICAL["manifest"],
                sha(UNRELATED_HISTORICAL["manifest"]), label="attack",
            )
        self.assertEqual(caught.exception.status, "U06_PUBLICATION_PROOF_INVALID")


def assert_lawful_governance_phase(testcase, root: Path = ROOT) -> dict:
    """The current generation's governance artifacts are present only in lawful order.

    The phase contract is the SOURCE's: ``lc.current_generation_phase`` over
    ``lc.G1_GOVERNANCE_STAGES``; nothing here restates the stage order.  Every
    slot of a stage the phase has reached is present, every slot of a later
    stage is absent, and any out-of-order presence fails.  Once the accepted-
    lifecycle record is present it must be a VALID acceptance of the current
    generation - presence alone is never accepted.
    """

    phase = lc.current_generation_phase(root)
    testcase.assertEqual(phase["out_of_order_present"], [], phase["phase"])
    testcase.assertNotEqual(phase["phase"], lc.G1_PHASE_OUT_OF_ORDER)
    stages = [stage for stage, _ in lc.G1_GOVERNANCE_STAGES]
    reached = stages.index(phase["phase"]) if phase["phase"] in stages else -1
    for position, (stage, keys) in enumerate(lc.G1_GOVERNANCE_STAGES):
        for key in keys:
            relative = phase["paths"][key]
            testcase.assertEqual(
                (root / relative).exists(), position <= reached,
                f"{phase['phase']}: {stage} slot {key} at {relative}",
            )
    if phase["presence"]["accepted_lifecycle_record"]:
        resolved = lc.resolve_u06_lifecycle(root)
        testcase.assertEqual(resolved["accepted_lifecycle_overlay"], "PRESENT_VALID")
    return phase


def keys_through(stage_name: str) -> set[str]:
    """Every governance key of ``lc.G1_GOVERNANCE_STAGES`` up to ``stage_name``."""

    keys: set[str] = set()
    for stage, stage_keys in lc.G1_GOVERNANCE_STAGES:
        keys.update(stage_keys)
        if stage == stage_name:
            return keys
    raise KeyError(stage_name)


class NoFabricatedFutureIdentityTests(unittest.TestCase):
    """Nothing about the future is invented, and nothing accepted exists."""

    def test_overlay_module_contains_no_digest_literal(self) -> None:
        import re

        source = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", source), [])

    def test_no_lifecycle_artifact_exists_yet(self) -> None:
        """No accepted-lifecycle record exists for the CURRENT generation yet.

        R3-AUD-04. This asserted the *U-06 R3* record does not exist. That
        record was lawfully created, audited, accepted and frozen, so the
        premise became false. What must be absent is the current generation's
        own slot. The companion assertion below keeps the historical record
        provably present, so this correction cannot be used to erase it.

        G1: phase-aware, from the live source contract.  While G1's own record
        is absent, the earlier role records are lawfully published one phase
        at a time (independent audit, then acceptance), so absence of the
        record does not imply absence of every role record.  What must hold
        is that no governance artifact exists beyond the phase reached, none
        is out of order, and a present record is a VALID acceptance of G1.
        """

        assert_lawful_governance_phase(self, ROOT)
        for historical in (HISTORICAL_RECORD_REL, R8_GEN.accepted_lifecycle_record_path):
            self.assertTrue(
                (ROOT / historical).is_file(),
                "an accepted historical lifecycle record must not be deleted",
            )
            self.assertNotEqual(GEN.accepted_lifecycle_record_path, historical)
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


class GovernancePhaseMatrixTests(unittest.TestCase):
    """The phase-aware premise accepts every lawful phase, and only those.

    A disposable repository carrying a lawful G1 chain through Phase C
    (``tests/test_21l``) is reshaped, by presence only, into each lawful
    intermediate phase and into each out-of-order state.  The check is the one
    ``test_no_lifecycle_artifact_exists_yet`` applies to the real repository.
    """

    STUB = b'{"artifact_type": "OUT_OF_ORDER_STUB"}\n'

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(stage="promote")
        cls.paths = lc.g1_predeclared_governance_paths(GEN)
        cls.lawful = {
            key: (cls.fixture.root / relative).read_bytes()
            for key, relative in cls.paths.items()
            if (cls.fixture.root / relative).is_file()
        }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def _reshape(self, present: set[str]) -> None:
        for key, relative in self.paths.items():
            target = self.fixture.root / relative
            if key in present:
                data = self.lawful.get(key, self.STUB)
                if not target.is_file() or target.read_bytes() != data:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            elif target.exists():
                target.unlink()

    @contextmanager
    def presence(self, present: set[str]):
        self.assertFalse(set(present) - set(self.paths), "unknown governance key")
        try:
            self._reshape(set(present))
            yield self.fixture.root
        finally:
            self._reshape(set(self.lawful))

    def test_the_fixture_is_a_lawful_phase_c_chain(self) -> None:
        self.assertEqual(
            set(self.lawful), keys_through("RE_FREEZE_AND_LIFECYCLE_RECORDS_PRESENT")
        )

    def test_lawful_phases_pass(self) -> None:
        for label, stage in (
            ("LAW-1 candidate packaged", "CANDIDATE_PACKAGED"),
            ("LAW-2 audit published", "INDEPENDENT_AUDIT_RECORD_PRESENT"),
            ("LAW-3 acceptance published", "ACCEPTANCE_RECORDS_PRESENT"),
            ("LAW-4 re-freeze and accepted lifecycle",
             "RE_FREEZE_AND_LIFECYCLE_RECORDS_PRESENT"),
        ):
            with self.subTest(state=label):
                with self.presence(keys_through(stage)) as root:
                    phase = assert_lawful_governance_phase(self, root)
                    self.assertEqual(phase["phase"], stage)
                    self.assertEqual(
                        lc.is_frozen(lc.resolve_u06_lifecycle(root)),
                        phase["presence"]["accepted_lifecycle_record"],
                    )

    def test_out_of_order_phases_fail_closed(self) -> None:
        packaged = keys_through("CANDIDATE_PACKAGED")
        audited = keys_through("INDEPENDENT_AUDIT_RECORD_PRESENT")
        accepted = keys_through("ACCEPTANCE_RECORDS_PRESENT")
        frozen = keys_through("RE_FREEZE_AND_LIFECYCLE_RECORDS_PRESENT")
        scoped = keys_through("SCOPE_AUTHORIZATION_RECORD_PRESENT")
        cases = (
            ("NEG-1 audit before candidate package",
             {"independent_audit_pass"}, ["independent_audit_pass"]),
            ("NEG-2 acceptance before audit",
             packaged | {"acceptance_closure", "acceptance_manifest"},
             ["acceptance_closure", "acceptance_manifest"]),
            ("NEG-3 re-freeze before acceptance",
             audited | {"production_authority_re_freeze"},
             ["production_authority_re_freeze"]),
            ("NEG-4a lifecycle before audit and acceptance",
             packaged | {"accepted_lifecycle_record"}, ["accepted_lifecycle_record"]),
            ("NEG-4b lifecycle before re-freeze",
             accepted | {"accepted_lifecycle_record"}, ["accepted_lifecycle_record"]),
            ("NEG-5 scope authorization before accepted lifecycle",
             accepted | {"main_full81_scope_authorization"},
             ["main_full81_scope_authorization"]),
            ("NEG-6a execution authorization before scope authorization",
             frozen | {"main_full81_execution_authorization"},
             ["main_full81_execution_authorization"]),
            ("NEG-6b execution authorization before no-solve evidence",
             scoped | {"main_full81_execution_authorization"},
             ["main_full81_execution_authorization"]),
        )
        for label, present, early in cases:
            with self.subTest(state=label):
                with self.presence(present) as root:
                    phase = lc.current_generation_phase(root)
                    self.assertEqual(phase["phase"], lc.G1_PHASE_OUT_OF_ORDER)
                    self.assertEqual(phase["out_of_order_present"], early)
                    with self.assertRaises(self.failureException):
                        assert_lawful_governance_phase(self, root)


def no_native_solver_entry():
    """Refuse and record every native solver entry and native-backend creation.

    A deployment-gate decision is validation only: even an AUTHORIZED decision
    must construct no model, call no solver and create no production backend.
    """

    from contextlib import ExitStack
    from unittest.mock import patch

    @contextmanager
    def guard():
        hits: list[str] = []

        def refuse(name: str):
            def _refuse(*args, **kwargs):
                hits.append(name)
                raise AssertionError(f"a gate decision reached {name}")

            return _refuse

        with ExitStack() as guards:
            guards.enter_context(
                patch.object(
                    stack, "NativeProductionBackend",
                    side_effect=refuse("NativeProductionBackend"),
                )
            )
            try:
                import gurobipy as gp
            except Exception:  # pragma: no cover - gurobipy absent is already safe
                gp = None
            if gp is not None:
                for attribute in ("__init__", "optimize", "optimizeAsync", "optimizeBatch", "tune"):
                    if hasattr(gp.Model, attribute):
                        guards.enter_context(
                            patch.object(gp.Model, attribute, refuse(f"gurobipy.Model.{attribute}"))
                        )
            yield hits

    return guard()


class GateStillFailsClosedTests(unittest.TestCase):
    """No substitution attempt can move the live gate."""

    def test_live_gate_rejects_every_production_scope(self) -> None:
        snapshot = stack.inspect_deployment_snapshot(ROOT)
        # G1: phase-aware, from the source contract; nothing out of order, and
        # a present lifecycle record must be a VALID acceptance.
        phase = assert_lawful_governance_phase(self, ROOT)
        accepted = phase["presence"]["accepted_lifecycle_record"]
        self.assertEqual(lc.is_frozen(snapshot.u06_accepted_lifecycle), accepted)
        scope_present = phase["presence"]["main_full81_scope_authorization"]
        execution_present = phase["presence"]["main_full81_execution_authorization"]
        cases = [("a2_variable_floor", {"A2_HARD_BLOCKED"})]
        if not execution_present:
            cases.append(
                ("full81", {"FULL81_AUTHORIZATION_NOT_GRANTED"} | (
                    {"FULL81_EXECUTION_NOT_AUTHORIZED"} if scope_present else set()
                ))
            )
        else:
            # Execution-authorized phase: the gate admits Full81 only because
            # the real G1 chain is VALID end to end, and the decision makes no
            # native solver entry.  Admission is not execution.
            lifecycle = snapshot.u06_accepted_lifecycle
            scope = auth.resolve_full81_authorization(ROOT, lifecycle)
            execution = auth.resolve_full81_execution_authorization(ROOT, lifecycle, scope)
            self.assertEqual(scope["full81_authorization_status"], auth.AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT)
            self.assertEqual(
                execution["execution_authorization_overlay"], "PRESENT_VALID",
                execution.get("rejected_status"),
            )
            self.assertEqual(
                execution["execution_authorization_status"], auth.AUTHORIZED_FOR_FULL81_EXECUTION
            )
            with no_native_solver_entry() as native_hits:
                decision = stack.validate_deployment_snapshot(
                    snapshot,
                    execute_production=True,
                    selected_scope="full81",
                    root=ROOT,
                )
            self.assertEqual(native_hits, [])
            self.assertEqual(decision["status"], "PRODUCTION_AUTHORITY_FROZEN")
        if not accepted:
            # Candidate phase: no production scope reaches a freeze.
            cases += [
                ("core-three", {"U06_ACCEPTED_LIFECYCLE_ABSENT"}),
                ("eob", {"U06_ACCEPTED_LIFECYCLE_ABSENT"}),
            ]
        for scope, expected in cases:
            with self.subTest(scope=scope):
                with self.assertRaises(stack.ProductionAuthorityError) as caught:
                    stack.validate_deployment_snapshot(
                        snapshot,
                        execute_production=True,
                        selected_scope=scope,
                        root=ROOT,
                    )
                self.assertIn(caught.exception.status, expected)

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
        accepted = (ROOT / GEN.accepted_lifecycle_record_path).exists()
        self.assertEqual(
            resolved["accepted_lifecycle_overlay"],
            "PRESENT_VALID" if accepted else "ABSENT",
        )
        json.dumps(stack._json_safe(resolved), sort_keys=True)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
