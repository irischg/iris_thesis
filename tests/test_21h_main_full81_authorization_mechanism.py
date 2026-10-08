"""Main Full81 authorization-mechanism Candidate R2: fail-closed suite.

Current Full81 Production Generation G1: the current generation is G1, whose
candidate package the promotion fixture SYNTHESIZES for its own live bytes and
whose role records it publishes at the G1 predeclared paths.  The R8 generation
and its contract V4 are asserted only as explicitly HISTORICAL controls, and
every assertion about the REAL repository is phase-aware.

What Candidate R1 got wrong, and what this suite now proves
-----------------------------------------------------------
Candidate R1 FAILED its read-only audit on two findings:

``H-01`` (CRITICAL)
    The production-authority lifecycle overlay was single-generation and
    hard-bound to U-06 R3, so no lawful path existed from CANDIDATE to
    INDEPENDENTLY AUDITED to ACCEPTED to RE-FROZEN for changed implementation
    bytes.  Every lifecycle role rejected a successor lineage, the
    implementation-candidate role was path-pinned to the R3 alignment manifest,
    and the single accepted-lifecycle slot was already occupied by a committed
    record declaring the predecessor digest.

``H-02`` (MAJOR)
    The Full81 authorization validator statically bound
    ``REQUIRED_U06_LINEAGE_ID`` to the predecessor R3 lineage, so even after a
    lawful generation advance every authorization would have failed.

Candidate R2 remediates both.  This suite proves it, and in particular proves
the whole future promotion sequence T1..T7 is representable **with no further
production-code edit and without mutating any U-06 R3 artifact**.

Fixture discipline
------------------
Payload-content negative controls are handed to pure validators as in-memory
mappings, exactly as the accepted ``tests/test_21f_u06_accepted_lifecycle_gate``
hands synthetic lifecycle mappings to the pure lifecycle validator.
Repository-state controls and the promotion control run inside **isolated
throwaway Git repositories** under the system temp directory.

No real lifecycle role artifact, accepted-lifecycle record, re-freeze record, or
Main Full81 authorization is created in this repository.  Every test is static /
build-only: no model construction, no optimizer, no solver, no production output
directory, no Full81 case, no A2 case, and ``scripts/21d`` is never invoked.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import main_full81_authorization_v7_4 as auth  # noqa: E402
from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from src import production_successor_stack_v7_3 as stack  # noqa: E402
from tests.test_21l_full81_production_generation_g1 import (  # noqa: E402
    g1_predecessor_commit,
    write_g1_candidate_package,
)


MECHANISM_SOURCE = ROOT / "src/main_full81_authorization_v7_4.py"
OVERLAY_SOURCE = ROOT / "src/production_authority_lifecycle_u06.py"

HISTORICAL_V7_2_TAG = "v7.2-final81-runner-ready-r3"
HISTORICAL_V7_2_MANIFEST = (
    "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json"
)

GEN = lc.CURRENT_GENERATION
PRED = lc.U06_R3_GENERATION

#: R3-AUD-04. Two tests in this suite assert the exact contract of a specific
#: HISTORICAL generation. They used to reach those generations through
#: ``GEN`` / ``PRED``, which are relative to whatever generation happens to be
#: current, so a lawful generation advance silently re-aimed them at the wrong
#: object and they failed on a predecessor premise. A historical assertion must
#: select its generation explicitly by id; these two names do that, and they
#: cannot drift.
AUTH_MECHANISM_R2_GEN = lc.GENERATIONS_BY_ID["MAIN_FULL81_AUTHORIZATION_MECHANISM_R2"]
U06_R3_GEN = lc.GENERATIONS_BY_ID["U06_V7_4_PRODUCTION_AUTHORITY_R3"]
#: Current Full81 Production Generation G1: the R8 preflight-authorization-
#: guard generation is historical, and is selected by id wherever a historical
#: R8 property is asserted.
R8_GEN = lc.GENERATIONS_BY_ID["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1"]


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)


def _git_ok(root: Path, *args: str) -> None:
    done = _git(root, *args)
    if done.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {root}: "
            f"{done.stderr.decode('utf-8', 'replace')}"
        )


def _git_text(root: Path, *args: str) -> str:
    return _git(root, *args).stdout.decode("utf-8", "replace").strip()


def _rmtree(path: Path) -> None:
    """Remove a throwaway repository, clearing read-only Git object bits."""

    def _force(func, target, _exc) -> None:
        try:
            Path(target).chmod(stat.S_IWRITE)
            func(target)
        except OSError:
            pass

    shutil.rmtree(path, onexc=_force)
    if path.exists():  # pragma: no cover - defensive on locked trees
        shutil.rmtree(path, ignore_errors=True)


def _fixture_paths() -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            list(lc.ACCEPTED_IMPLEMENTATION_PATHS)
            + list(lc.VALIDATION_IDENTITY_PATHS)
            # Candidate R3: the authority files a reconstruction must contain
            # for the bundle to verify at all. This fixture is a miniature
            # repository reconstruction, so a newly pinned authority file has to
            # be present here or the bundle correctly reports it missing and
            # every positive control resolves NOT_GRANTED.
            #
            # Deriving this from the declared requirement rather than restating
            # a literal path is deliberate: it is exactly the R2-AUD-01 class of
            # defect - a required authority file absent from a reconstruction -
            # and a derived list cannot silently fall behind a new pin.
            + list(lc.REQUIRED_DURABLE_PUBLICATION_PATHS)
            # G1: the governance-authority identity the G1 contract binds is
            # derived, so a reconstruction carries exactly those members.
            + list(lc.governance_authority_identity_paths())
            + [
                auth.EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
                auth.EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
                auth.EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
                PRED.accepted_lifecycle_record_path,
                PRED.candidate_manifest_path,
                PRED.candidate_checkpoint_path,
                # Historical controls: the R8 accepted record and candidate.
                R8_GEN.accepted_lifecycle_record_path,
                R8_GEN.candidate_manifest_path,
                R8_GEN.candidate_checkpoint_path,
            ]
            # Contract V4 (historical): the Git-frozen trust root is tracked
            # and published, so every published checkout carries it.  The
            # IGNORED R1-R7 evidence V4 additionally reads is deliberately NOT
            # copied: the G1 contract does not consume it, and the historical
            # control below proves V4 still fails closed without it.
            + [bundle.PRE_R8_HISTORICAL_TRUST_ROOT.path]
        )
    )


# ---------------------------------------------------------------------------
# The isolated promotion fixture
# ---------------------------------------------------------------------------


class _Fixture:
    """An isolated throwaway repository that can carry a FULL R2 promotion.

    Commit layout, so publication containment can be attacked honestly:

    ``commit_base``        accepted implementation surface + R2 candidate
                           artifacts, WITHOUT any R2 lifecycle role artifact.
    ``commit_phase_a``     + independent-audit PASS role.
    ``commit_phase_b``     + acceptance closure and acceptance manifest.
    ``commit_phase_c``     + re-freeze record and accepted-lifecycle record.
    ``HEAD``               + the Main Full81 authorization, when published.
    """

    def __init__(
        self,
        *,
        promote: bool = True,
        publish_authorization: bool = True,
    ) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="full81_r2_fixture_")).resolve()
        try:
            self._build(promote=promote, publish_authorization=publish_authorization)
        except BaseException:
            # A fixture that fails to build never leaks its temp directory.
            self.dispose()
            raise

    def _build(self, *, promote: bool, publish_authorization: bool) -> None:
        self.auth_relative = auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        self.record_relative = GEN.accepted_lifecycle_record_path

        for relative in _fixture_paths():
            source = ROOT / relative
            if not source.is_file():
                continue
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        _git_ok(self.root, "init", "--quiet")
        _git_ok(self.root, "config", "user.email", "fixture@example.invalid")
        _git_ok(self.root, "config", "user.name", "fixture")
        _git_ok(self.root, "config", "commit.gpgsign", "false")
        # Candidate R8 (contract V4): the fixture's commits descend from the
        # REAL published history, so the Git-frozen pre-R8 trust root is in
        # their ancestry exactly as it is in a lawful repository.  The source
        # object store is shared READ-ONLY through alternates; the published
        # branch head and the frozen tag are copied as refs.  Nothing is
        # checked out from that history and nothing is written to the source.
        alternates = self.root / ".git" / "objects" / "info" / "alternates"
        alternates.parent.mkdir(parents=True, exist_ok=True)
        alternates.write_text(
            (ROOT / ".git" / "objects").resolve().as_posix() + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _git_ok(self.root, "update-ref", "refs/heads/thesis-v7", _git_text(ROOT, "rev-parse", "HEAD"))
        _git_ok(self.root, "symbolic-ref", "HEAD", "refs/heads/thesis-v7")
        frozen = bundle.PRE_R8_HISTORICAL_TRUST_ROOT
        _git_ok(self.root, "update-ref", frozen.tag_ref, _git_text(ROOT, "rev-parse", frozen.tag_ref))
        # G1: the current candidate package is SYNTHESIZED for this fixture's
        # own live bytes (ledger -> checkpoint -> manifest, the lawful order),
        # never copied from the real repository, so the promotion control is
        # meaningful in every phase - including before the real package exists.
        package = write_g1_candidate_package(
            self.root, base_commit=g1_predecessor_commit()
        )
        self._commit("fixture: accepted surface + G1 candidate")
        self.commit_base = self.head()

        self.live_digest = lc.implementation_identity_digest(self.root)
        self.ckpt_sha = package["checkpoint"]
        self.manifest_sha = package["manifest"]
        self.package = package

        self.roles: dict[str, dict] = {}
        self.commit_phase_a = None
        self.commit_phase_b = None
        self.commit_phase_c = None
        if promote:
            self.promote()
            self.write_authorization(self.lawful_authorization())
            if publish_authorization:
                self._commit("fixture: full81 authorization")
                self.sync_upstream()

    # -- git helpers --------------------------------------------------------

    def head(self) -> str:
        return _git_text(self.root, "rev-parse", "HEAD")

    def _commit(self, message: str) -> str:
        _git_ok(self.root, "add", "-A")
        _git_ok(self.root, "commit", "--quiet", "-m", message)
        return self.head()

    def sync_upstream(self) -> None:
        _git_ok(
            self.root,
            "update-ref",
            f"refs/remotes/{lc.EXPECTED_UPSTREAM}",
            self.head(),
        )

    def write(self, relative: str, payload) -> str:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8", newline="\n")
        else:
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        return lc.sha256_file(path)

    # -- the R2 lifecycle roles --------------------------------------------

    def _envelope(self, role: str) -> dict:
        contract = GEN.role_contracts[role]
        payload = {
            "artifact_type": contract.artifact_type,
            "schema_version": contract.schema_version,
            "lineage_id": GEN.lineage_id,
            "target_candidate_id": GEN.candidate_id,
            "candidate_checkpoint": {
                "path": GEN.candidate_checkpoint_path,
                "sha256": self.ckpt_sha,
            },
            "implementation_identity_digest": self.live_digest,
        }
        if contract.declares_candidate_manifest:
            payload["candidate_manifest"] = {
                "path": GEN.candidate_manifest_path,
                "sha256": self.manifest_sha,
            }
        return payload

    def _bind(self, payload: dict, roles: tuple[str, ...]) -> dict:
        for earlier in roles:
            if earlier == "implementation_candidate":
                continue
            payload[earlier] = {
                "path": self.roles[earlier]["path"],
                "sha256": self.roles[earlier]["sha256"],
            }
        return payload

    def promote(self) -> None:
        """Build and publish the full R2 promotion chain, Phases A, B and C."""

        # T1 implementation candidate role IS the R2 candidate manifest.
        self.roles["implementation_candidate"] = {
            "path": GEN.candidate_manifest_path,
            "sha256": self.manifest_sha,
        }

        # T2 independent audit PASS -> Phase A.
        audit = self._envelope("independent_audit_pass")
        audit.update(
            {
                "verdict": "PASS",
                "blocking_critical": 0,
                "blocking_major": 0,
                "independent_audit": True,
                "candidate_author_is_not_self_accepting": True,
                "findings_closed": ["H-01", "H-02"],
            }
        )
        rel = GEN.role_record_path_map["independent_audit_pass"]
        self.roles["independent_audit_pass"] = {
            "path": rel,
            "sha256": self.write(rel, audit),
        }
        self.commit_phase_a = self._commit("fixture: phase A audit PASS")

        # T3 acceptance closure + T4 acceptance manifest -> Phase B.
        closure = self._bind(
            self._envelope("acceptance_closure"), ("independent_audit_pass",)
        )
        closure.update(
            {
                "acceptance_status": lc.ACCEPTED_ACCEPTANCE_STATUS,
                "audit_verdict": "PASS",
                "audit_publication_commit": self.commit_phase_a,
            }
        )
        rel = GEN.role_record_path_map["acceptance_closure"]
        self.roles["acceptance_closure"] = {
            "path": rel,
            "sha256": self.write(rel, closure),
        }

        manifest = self._bind(
            self._envelope("acceptance_manifest"),
            ("independent_audit_pass", "acceptance_closure"),
        )
        manifest["acceptance_status"] = lc.ACCEPTED_ACCEPTANCE_STATUS
        rel = GEN.role_record_path_map["acceptance_manifest"]
        self.roles["acceptance_manifest"] = {
            "path": rel,
            "sha256": self.write(rel, manifest),
        }
        self.commit_phase_b = self._commit("fixture: phase B acceptance")

        # T5 re-freeze + T6 accepted-lifecycle aggregator -> Phase C.
        refreeze = self._bind(
            self._envelope("production_authority_re_freeze"),
            ("independent_audit_pass", "acceptance_closure", "acceptance_manifest"),
        )
        refreeze.update(
            {
                "production_authority_status_intended": lc.FROZEN_STATUS,
                "authorizes_main_full81": False,
                "acceptance_publication_commit": self.commit_phase_b,
                "predecessor_generation_id": GEN.predecessor_generation_id,
                "predecessor_lineage_id": GEN.predecessor_lineage_id,
            }
        )
        rel = GEN.role_record_path_map["production_authority_re_freeze"]
        self.roles["production_authority_re_freeze"] = {
            "path": rel,
            "sha256": self.write(rel, refreeze),
        }

        self.write(self.record_relative, self.lawful_lifecycle_record())
        self.commit_phase_c = self._commit("fixture: phase C re-freeze")
        self.sync_upstream()

    def lawful_lifecycle_record(self) -> dict:
        return {
            "artifact_type": GEN.lifecycle_record_artifact_type,
            "schema_version": GEN.lifecycle_record_schema_version,
            "lineage_id": GEN.lineage_id,
            "target_candidate_id": GEN.candidate_id,
            "u06_alignment_status": lc.ACCEPTED_ALIGNMENT_STATUS,
            "u06_independent_audit_status": lc.ACCEPTED_AUDIT_STATUS,
            "u06_acceptance_status": lc.ACCEPTED_ACCEPTANCE_STATUS,
            "production_authority_freeze_status": lc.FROZEN_STATUS,
            "authorizes_main_full81": False,
            "implementation_identity_digest": self.live_digest,
            "predecessor_generation_id": GEN.predecessor_generation_id,
            "predecessor_accepted_lifecycle_record": (
                GEN.predecessor_accepted_lifecycle_record_path
            ),
            "roles": {
                role: {"path": e["path"], "sha256": e["sha256"]}
                for role, e in self.roles.items()
            },
        }

    # -- the R2 authorization ---------------------------------------------

    def resolve_lifecycle(self) -> dict:
        return lc.resolve_u06_lifecycle(self.root)

    def lawful_authorization(self) -> dict:
        resolved = self.resolve_lifecycle()
        runner = auth.EXPECTED_RUNNER_RELATIVE_PATH
        return {
            "artifact_type": auth.AUTHORIZATION_ARTIFACT_TYPE,
            "schema_version": auth.AUTHORIZATION_SCHEMA_VERSION,
            "lineage_id": auth.LINEAGE_ID,
            "candidate_id": auth.CANDIDATE_ID,
            "authorization_status": auth.REQUIRED_DECLARED_STATUS,
            "authorization_scope": auth.AUTHORIZATION_SCOPE,
            "authorizes": [auth.AUTHORIZED_NEXT_ACT],
            "authorizes_optimize_calls": False,
            "authorizes_full81_execution": False,
            "requires_no_solve_preflight_before_execution": True,
            "production_authority_generation_id": resolved["generation_id"],
            "production_authority_lineage_id": resolved["lineage_id"],
            "production_authority_accepted_lifecycle_record": {
                "path": resolved["record_path"],
                "sha256": lc.sha256_file(self.root / resolved["record_path"]),
            },
            "production_authority_publication_commit": self.commit_phase_c,
            "production_authority_freeze_status": "FROZEN",
            "implementation_identity_digest": self.live_digest,
            "target_runner": {
                "path": runner,
                "version": auth.EXPECTED_RUNNER_VERSION,
                "sha256": lc.sha256_file(self.root / runner),
            },
            "canonical_annual_input": {
                "path": auth.EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
                "sha256": auth.EXPECTED_ANNUAL_INPUT_SHA256,
            },
            "accepted_annual_model": {
                "path": auth.EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
                "sha256": auth.EXPECTED_ANNUAL_MODEL_SHA256,
            },
            "parameter_registry": {
                "path": auth.EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
                "sha256": auth.EXPECTED_PARAMETER_REGISTRY_SHA256,
            },
            "alpha_universe": list(auth.EXPECTED_ALPHA_UNIVERSE),
            "beta_universe_h": list(auth.EXPECTED_BETA_UNIVERSE_H),
            "case_count": auth.EXPECTED_CASE_COUNT,
            "solver_parameter_fingerprint": auth.solver_parameter_fingerprint(),
            "restart_policy": auth.REQUIRED_RESTART_POLICY,
            "excluded_scopes": list(auth.REQUIRED_DECLARED_EXCLUSIONS),
            "a2_excluded": True,
            "u_01_status": auth.U_01_STATUS,
            "u_01_blocks_main_full81": False,
            "u_01_must_be_frozen_before": list(auth.U_01_MUST_BE_FROZEN_BEFORE),
        }

    def write_authorization(self, payload) -> None:
        self.write(self.auth_relative, payload)

    def resolve_authorization(self) -> dict:
        return auth.resolve_full81_authorization(
            self.root, self.resolve_lifecycle()
        )

    def validate_authorization(self, payload, *, lifecycle=...) -> dict:
        return auth.validate_authorization_payload(
            self.root,
            payload,
            record_relative=self.auth_relative,
            lifecycle=self.resolve_lifecycle() if lifecycle is ... else lifecycle,
        )

    def dispose(self) -> None:
        _rmtree(self.root)


# ---------------------------------------------------------------------------
# A. LIFECYCLE GENERATION - the H-01 remediation
# ---------------------------------------------------------------------------


class GenerationContractTests(unittest.TestCase):
    """The overlay is generation-parameterised, and R2 is the current one."""

    def test_authorization_mechanism_r2_generation_contract_is_byte_stable(
        self,
    ) -> None:
        """HISTORICAL: the accepted auth-mechanism R2 contract never drifts.

        R3-AUD-04. This asserted the values above of ``GEN``, i.e. of whatever
        generation is CURRENT. Auth-mechanism R2 was lawfully accepted, frozen
        and superseded, so once the current generation advanced the test
        compared the new generation against R2's accepted values and failed on
        a predecessor premise. It now selects auth-mechanism R2 explicitly by
        id, which is what a historical assertion must do, and it keeps every
        accepted value pinned so none of them can be rewritten.
        """

        gen = AUTH_MECHANISM_R2_GEN
        self.assertEqual(gen.generation_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_R2")
        self.assertEqual(gen.lineage_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_R1")
        self.assertEqual(
            gen.candidate_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2"
        )
        self.assertEqual(
            gen.candidate_manifest_path,
            "results/provenance/"
            "main_full81_authorization_mechanism_candidate_r2_2026-10-02/"
            "authorization_mechanism_manifest.json",
        )
        self.assertEqual(
            gen.accepted_lifecycle_record_path,
            "results/provenance/"
            "main_full81_authorization_mechanism_accepted_lifecycle_r2/"
            "accepted_lifecycle_record.json",
        )
        self.assertEqual(gen.schema_prefix, "iris-thesis-full81-auth-mech-r2-")
        # And it is historical, not current.
        self.assertIn(gen, lc.HISTORICAL_GENERATIONS)
        self.assertIsNot(gen, lc.CURRENT_GENERATION)

    def test_current_generation_is_g1_candidate_r1(self) -> None:
        """CURRENT: the active generation, derived from primary contracts.

        CURRENT POINTER, advanced from the R8 preflight-authorization-guard
        generation to Current Full81 Production Generation G1.  The G1 content
        contract, change ledger and predeclared role paths belong to G1; R8
        keeps exactly the V4 contract and ledger it was accepted under, and
        the earlier generations keep the envelope-only contract.
        """

        self.assertIs(GEN, lc.CURRENT_GENERATION)
        self.assertEqual(GEN.generation_id, "CURRENT_FULL81_PRODUCTION_GENERATION_G1")
        self.assertEqual(GEN.lineage_id, "CURRENT_FULL81_PRODUCTION_GENERATION_G1")
        self.assertEqual(
            GEN.candidate_id, "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1"
        )
        self.assertEqual(GEN.candidate_audit_state, "NOT_YET_PERFORMED")
        self.assertEqual(GEN.candidate_manifest_contract, lc.G1_CANDIDATE_MANIFEST_CONTRACT)
        for superseded_contract in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V1,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V2,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V3,
        ):
            self.assertNotIn(superseded_contract, lc.KNOWN_CANDIDATE_MANIFEST_CONTRACTS)
        self.assertTrue(GEN.candidate_change_ledger_path)
        self.assertEqual(set(GEN.role_record_path_map), set(lc.NON_SELF_ACCEPTABLE_ROLES))
        # HISTORICAL, selected by id: R8 keeps its accepted contract and ledger.
        self.assertIn(R8_GEN, lc.HISTORICAL_GENERATIONS)
        self.assertEqual(
            R8_GEN.candidate_manifest_contract,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4,
        )
        self.assertEqual(
            R8_GEN.candidate_change_ledger_path,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH,
        )
        for historical in (AUTH_MECHANISM_R2_GEN, U06_R3_GEN):
            with self.subTest(generation=historical.generation_id):
                self.assertIsNone(historical.candidate_manifest_contract)
                self.assertIsNone(historical.candidate_change_ledger_path)
        for historical in lc.HISTORICAL_GENERATIONS:
            self.assertIsNone(historical.predeclared_role_record_paths)
        self.assertEqual(auth.CANDIDATE_ID, GEN.candidate_id)
        self.assertEqual(auth.LINEAGE_ID, GEN.lineage_id)
        self.assertNotIn(GEN, lc.HISTORICAL_GENERATIONS)
        # Exactly one generation is current.
        self.assertEqual(
            len(lc.AUTHORITY_GENERATIONS) - len(lc.HISTORICAL_GENERATIONS), 1
        )
        # Its predecessor chain is read from the generation itself.
        predecessor = lc.GENERATIONS_BY_ID[GEN.predecessor_generation_id]
        self.assertIs(predecessor, R8_GEN)
        self.assertEqual(GEN.predecessor_lineage_id, predecessor.lineage_id)
        self.assertEqual(
            GEN.predecessor_accepted_lifecycle_record_path,
            predecessor.accepted_lifecycle_record_path,
        )
        # Phase-aware: until G1 is accepted its own slot does not exist; the
        # R8 slot it supersedes stays published.
        if not (ROOT / GEN.accepted_lifecycle_record_path).exists():
            self.assertFalse(lc.is_frozen(lc.resolve_u06_lifecycle(ROOT)))
        self.assertTrue((ROOT / R8_GEN.accepted_lifecycle_record_path).is_file())

    def test_r8_candidate_is_superseded_not_rejected(self) -> None:
        """HISTORICAL: R8 was accepted and re-frozen; it is superseded by G1."""

        r8 = R8_GEN.candidate_id
        self.assertIn(r8, GEN.superseded_candidate_ids)
        self.assertIn(r8, auth.SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM)
        self.assertNotIn(r8, auth.REJECTED_CANDIDATE_IDS)
        self.assertIn(R8_GEN.lineage_id, auth.SUPERSEDED_LINEAGE_IDS_THIS_MECHANISM)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH,
        ):
            self.assertIn(path, GEN.candidate_artifact_paths)
            self.assertNotEqual(path, GEN.candidate_manifest_path)

    def test_u06_r3_is_an_immutable_historical_predecessor(self) -> None:
        """HISTORICAL: U-06 R3 keeps its accepted identity and stays historical.

        R3-AUD-04. The predecessor-chain half of this test asserted that U-06
        R3 is the DIRECT predecessor of the current generation. That was true
        of auth-mechanism R2 and is no longer true of the preflight-guard
        generation, so it failed on a predecessor premise. U-06 R3's own
        accepted contract is unchanged and is still asserted in full; the chain
        assertion now walks the registry instead of assuming a fixed depth.
        """

        pred = U06_R3_GEN
        self.assertIs(pred, PRED)
        self.assertEqual(pred.generation_id, "U06_V7_4_PRODUCTION_AUTHORITY_R3")
        self.assertEqual(pred.lineage_id, lc.LINEAGE_ID)
        self.assertEqual(pred.candidate_id, lc.R3_CANDIDATE_ID)
        self.assertEqual(
            pred.accepted_lifecycle_record_path,
            lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        )
        self.assertEqual(pred.schema_prefix, "iris-thesis-u06-r3-")
        self.assertIn(pred, lc.HISTORICAL_GENERATIONS)
        self.assertNotIn(GEN, lc.HISTORICAL_GENERATIONS)
        # U-06 R3 is the ROOT of the chain: it has no predecessor, and the
        # current generation reaches it by walking predecessor links.
        self.assertIsNone(pred.predecessor_generation_id)
        chain = [GEN]
        while chain[-1].predecessor_generation_id:
            chain.append(lc.GENERATIONS_BY_ID[chain[-1].predecessor_generation_id])
        self.assertIs(chain[-1], pred)
        self.assertEqual(
            [g.generation_id for g in chain],
            [
                "CURRENT_FULL81_PRODUCTION_GENERATION_G1",
                "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1",
                "MAIN_FULL81_AUTHORIZATION_MECHANISM_R2",
                "U06_V7_4_PRODUCTION_AUTHORITY_R3",
            ],
        )
        # Every link is consistent in both lineage and record path.
        for successor, ancestor in zip(chain, chain[1:]):
            self.assertEqual(successor.predecessor_lineage_id, ancestor.lineage_id)
            self.assertEqual(
                successor.predecessor_accepted_lifecycle_record_path,
                ancestor.accepted_lifecycle_record_path,
            )

    def test_accepted_r3_constants_are_byte_stable(self) -> None:
        """The accepted R3 names keep their accepted values."""

        self.assertEqual(
            lc.LINEAGE_ID, "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3"
        )
        self.assertEqual(
            lc.R3_CANDIDATE_ID,
            "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R3",
        )
        self.assertEqual(
            lc.LIFECYCLE_RECORD_SCHEMA_VERSION,
            "iris-thesis-u06-r3-accepted-lifecycle-v1",
        )
        for role, contract in lc.ROLE_CONTRACTS.items():
            with self.subTest(role=role):
                self.assertTrue(
                    contract.schema_version.startswith("iris-thesis-u06-r3-")
                )

    def test_generations_have_disjoint_schema_namespaces(self) -> None:
        a = {c.schema_version for c in GEN.role_contracts.values()}
        b = {c.schema_version for c in PRED.role_contracts.values()}
        self.assertEqual(a & b, set())
        at = {c.artifact_type for c in GEN.role_contracts.values()}
        bt = {c.artifact_type for c in PRED.role_contracts.values()}
        self.assertEqual(at & bt, set())
        self.assertNotEqual(
            GEN.lifecycle_record_artifact_type,
            PRED.lifecycle_record_artifact_type,
        )
        self.assertEqual(
            PRED.lifecycle_record_artifact_type,
            lc.ACCEPTED_LIFECYCLE_ARTIFACT_TYPE,
        )
        self.assertNotEqual(
            GEN.lifecycle_record_schema_version,
            PRED.lifecycle_record_schema_version,
        )
        self.assertNotEqual(GEN.lineage_id, PRED.lineage_id)
        self.assertNotEqual(GEN.candidate_id, PRED.candidate_id)
        self.assertNotEqual(
            GEN.accepted_lifecycle_record_path,
            PRED.accepted_lifecycle_record_path,
        )
        self.assertNotEqual(
            GEN.candidate_manifest_path, PRED.candidate_manifest_path
        )

    def test_failed_candidate_r1_is_on_the_rejection_lists(self) -> None:
        self.assertIn(
            "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1",
            GEN.superseded_candidate_ids,
        )
        self.assertIn(
            "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1",
            auth.REJECTED_CANDIDATE_IDS,
        )
        for path in (
            lc.FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_CHECKPOINT_PATH,
            lc.FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_MANIFEST_PATH,
        ):
            with self.subTest(path=path):
                self.assertIn(path, GEN.candidate_artifact_paths)

    def test_failed_candidate_r4_is_on_the_rejection_lists(self) -> None:
        """HISTORICAL: Candidate R4 failed R4-AUD-01 and is barred everywhere."""

        r4 = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4"
        self.assertIn(r4, GEN.superseded_candidate_ids)
        self.assertIn(r4, auth.REJECTED_CANDIDATE_IDS)
        self.assertNotEqual(auth.CANDIDATE_ID, r4)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH,
        ):
            with self.subTest(path=path):
                self.assertIn(path, GEN.candidate_artifact_paths)
                self.assertNotEqual(path, GEN.candidate_manifest_path)
                self.assertNotEqual(path, GEN.candidate_checkpoint_path)

    def test_failed_candidate_r5_is_on_the_rejection_lists(self) -> None:
        """HISTORICAL: Candidate R5 failed R5-AUD-01 / R5-AUD-02; barred everywhere."""

        r5 = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5"
        self.assertIn(r5, GEN.superseded_candidate_ids)
        self.assertIn(r5, auth.REJECTED_CANDIDATE_IDS)
        self.assertNotEqual(auth.CANDIDATE_ID, r5)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_MANIFEST_PATH,
        ):
            with self.subTest(path=path):
                self.assertIn(path, GEN.candidate_artifact_paths)
                self.assertNotEqual(path, GEN.candidate_manifest_path)
                self.assertNotEqual(path, GEN.candidate_checkpoint_path)

    def test_failed_candidate_r6_is_on_the_rejection_lists(self) -> None:
        """HISTORICAL: Candidate R6 failed R6-AUD-01 / R6-AUD-02; barred everywhere."""

        r6 = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6"
        self.assertIn(r6, GEN.superseded_candidate_ids)
        self.assertIn(r6, auth.REJECTED_CANDIDATE_IDS)
        self.assertNotEqual(auth.CANDIDATE_ID, r6)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHANGE_LEDGER_PATH,
        ):
            with self.subTest(path=path):
                self.assertIn(path, GEN.candidate_artifact_paths)
                self.assertNotEqual(path, GEN.candidate_manifest_path)
                self.assertNotEqual(path, GEN.candidate_checkpoint_path)

    def test_failed_candidate_r7_is_on_the_rejection_lists(self) -> None:
        """HISTORICAL: Candidate R7 failed R7-AUD-01; barred everywhere."""

        r7 = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7"
        self.assertIn(r7, GEN.superseded_candidate_ids)
        self.assertIn(r7, auth.REJECTED_CANDIDATE_IDS)
        self.assertNotEqual(auth.CANDIDATE_ID, r7)
        for path in (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHANGE_LEDGER_PATH,
        ):
            with self.subTest(path=path):
                self.assertIn(path, GEN.candidate_artifact_paths)
                self.assertNotEqual(path, GEN.candidate_manifest_path)
                self.assertNotEqual(path, GEN.candidate_checkpoint_path)

    def test_overlay_still_contains_no_digest_literal(self) -> None:
        source = OVERLAY_SOURCE.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", source), [])

    def test_advancing_a_generation_is_declarative(self) -> None:
        requirements = lc.future_acceptance_requirements()
        self.assertEqual(requirements["generation_id"], GEN.generation_id)
        self.assertFalse(
            requirements["advancing_a_generation_requires_a_validator_rewrite"]
        )
        self.assertFalse(
            requirements["advancing_a_generation_mutates_a_predecessor_artifact"]
        )
        self.assertFalse(
            requirements["superseded_generation_can_freeze_live_authority"]
        )
        self.assertFalse(requirements["record_exists_today"])


class PromotionPathControlTests(unittest.TestCase):
    """T1..T7: the whole future promotion sequence must be representable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def test_t1_implementation_candidate_role_is_the_r2_manifest(self) -> None:
        entry = self.fixture.roles["implementation_candidate"]
        self.assertEqual(entry["path"], GEN.candidate_manifest_path)
        lc._validate_role_path(
            "implementation_candidate",
            entry["path"],
            self.fixture.record_relative,
            GEN,
        )

    def test_t2_to_t5_each_role_validates_under_the_r2_generation(self) -> None:
        resolved: dict = {}
        for role in lc.REQUIRED_ACCEPTED_ROLES:
            entry = self.fixture.roles[role]
            with self.subTest(role=role):
                record = json.loads(
                    (self.fixture.root / entry["path"]).read_text(encoding="utf-8")
                )
                envelope = lc.validate_role_envelope(
                    self.fixture.root,
                    role,
                    entry["path"],
                    record,
                    live_digest=self.fixture.live_digest,
                    generation=GEN,
                )
                self.assertEqual(envelope["generation_id"], GEN.generation_id)
                self.assertEqual(envelope["lineage_id"], GEN.lineage_id)
                self.assertEqual(
                    envelope["target_candidate_id"], GEN.candidate_id
                )
                self.assertEqual(
                    envelope["schema_version"],
                    GEN.role_contracts[role].schema_version,
                )
                lc._validate_bound_roles(
                    self.fixture.root, role, entry["path"], record, resolved, GEN
                )
                lc.validate_role_specifics(
                    self.fixture.root, role, entry["path"], record, resolved, GEN
                )
                resolved[role] = {
                    "path": entry["path"],
                    "sha256": entry["sha256"],
                    **envelope,
                }

    def test_t6_accepted_lifecycle_aggregator_validates(self) -> None:
        resolved = self.fixture.resolve_lifecycle()
        self.assertEqual(resolved["generation_id"], GEN.generation_id)
        self.assertTrue(resolved["is_current_generation"])
        self.assertEqual(
            resolved["accepted_lifecycle_overlay"], "PRESENT_VALID"
        )
        self.assertEqual(
            set(resolved["satisfied_roles"]), set(lc.REQUIRED_ACCEPTED_ROLES)
        )
        self.assertEqual(resolved["missing_roles"], [])
        self.assertFalse(resolved["authorizes_main_full81"])

    def test_t7_production_authority_is_frozen_under_the_r2_digest(self) -> None:
        resolved = self.fixture.resolve_lifecycle()
        self.assertEqual(
            resolved["production_authority_freeze_status"], "FROZEN"
        )
        self.assertTrue(lc.is_frozen(resolved))
        granted = lc.require_frozen_lifecycle_against_live_implementation(
            self.fixture.root, resolved
        )
        self.assertEqual(
            granted["implementation_identity_digest"], self.fixture.live_digest
        )
        self.assertNotEqual(
            self.fixture.live_digest,
            "b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a",
        )

    def test_promotion_mutated_no_u06_r3_artifact(self) -> None:
        for relative in (
            PRED.accepted_lifecycle_record_path,
            PRED.candidate_manifest_path,
            PRED.candidate_checkpoint_path,
        ):
            with self.subTest(path=relative):
                inside = self.fixture.root / relative
                if not inside.is_file():
                    continue
                self.assertEqual(
                    lc.sha256_file(inside), lc.sha256_file(ROOT / relative)
                )
                self.assertEqual(
                    _git_text(
                        self.fixture.root,
                        "diff",
                        "--name-only",
                        self.fixture.commit_base,
                        "HEAD",
                        "--",
                        relative,
                    ),
                    "",
                )


# ---------------------------------------------------------------------------
# B. CROSS-GENERATION NEGATIVE CONTROLS
# ---------------------------------------------------------------------------


class CrossGenerationNegativeControlTests(unittest.TestCase):
    """No generation may satisfy another, in either direction."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def _role_record(self, role: str) -> dict:
        entry = self.fixture.roles[role]
        return json.loads(
            (self.fixture.root / entry["path"]).read_text(encoding="utf-8")
        )

    def test_r2_role_rejected_by_the_r3_predecessor_contract(self) -> None:
        for role in lc.REQUIRED_ACCEPTED_ROLES:
            with self.subTest(role=role):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.validate_role_envelope(
                        self.fixture.root,
                        role,
                        self.fixture.roles[role]["path"],
                        self._role_record(role),
                        live_digest=self.fixture.live_digest,
                        generation=PRED,
                    )
                self.assertIn(
                    caught.exception.status,
                    {
                        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
                        "U06_ROLE_SCHEMA_MISMATCH",
                        "U06_LINEAGE_MISMATCH",
                        "U06_ROLE_TARGET_MISMATCH",
                    },
                )

    def test_r3_lineage_role_rejected_by_the_current_r2_contract(self) -> None:
        for role in lc.REQUIRED_ACCEPTED_ROLES:
            payload = self._role_record(role)
            payload["lineage_id"] = PRED.lineage_id
            payload["target_candidate_id"] = PRED.candidate_id
            payload["schema_version"] = PRED.role_contracts[role].schema_version
            with self.subTest(role=role):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.validate_role_envelope(
                        self.fixture.root,
                        role,
                        self.fixture.roles[role]["path"],
                        payload,
                        live_digest=self.fixture.live_digest,
                        generation=GEN,
                    )
                self.assertIn(
                    caught.exception.status,
                    {
                        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
                        "U06_ROLE_SCHEMA_MISMATCH",
                    },
                )

    def test_predecessor_candidate_manifest_cannot_fill_the_r2_role(self) -> None:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc._validate_role_path(
                "implementation_candidate",
                PRED.candidate_manifest_path,
                self.fixture.record_relative,
                GEN,
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")

    def test_failed_r1_candidate_artifacts_cannot_fill_r2_roles(self) -> None:
        for path in (
            lc.FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_CHECKPOINT_PATH,
            lc.FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_MANIFEST_PATH,
        ):
            for role in lc.NON_SELF_ACCEPTABLE_ROLES:
                with self.subTest(path=path, role=role):
                    with self.assertRaises(lc.U06LifecycleError) as caught:
                        lc._validate_role_path(
                            role, path, self.fixture.record_relative, GEN
                        )
                    self.assertEqual(
                        caught.exception.status, "U06_SELF_ACCEPTANCE_REJECTED"
                    )

    def test_failed_r1_candidate_id_is_rejected_in_a_role(self) -> None:
        payload = self._role_record("independent_audit_pass")
        payload["target_candidate_id"] = (
            "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1"
        )
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_role_envelope(
                self.fixture.root,
                "independent_audit_pass",
                self.fixture.roles["independent_audit_pass"]["path"],
                payload,
                live_digest=self.fixture.live_digest,
                generation=GEN,
            )
        self.assertEqual(
            caught.exception.status, "U06_SUPERSEDED_CANDIDATE_REJECTED"
        )

    def test_cross_generation_role_mixing_is_rejected(self) -> None:
        # G1, structural layer: a predecessor generation's artifact offered at
        # its own path is refused because G1 roles are lawful only at their
        # predeclared paths.
        record = self.fixture.lawful_lifecycle_record()
        record["roles"]["independent_audit_pass"] = {
            "path": PRED.accepted_lifecycle_record_path,
            "sha256": lc.sha256_file(
                self.fixture.root / PRED.accepted_lifecycle_record_path
            ),
        }
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_accepted_lifecycle_payload(
                self.fixture.root,
                record,
                record_relative=self.fixture.record_relative,
                generation=GEN,
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")

        # Content layer: the SAME predecessor bytes placed AT the predeclared
        # path still never fill a G1 role - the cross-generation guard refuses
        # them on type / schema, which is what this control has always proved.
        target = self.fixture.root / self.fixture.roles["independent_audit_pass"]["path"]
        original = target.read_bytes()
        try:
            target.write_bytes(
                (self.fixture.root / PRED.accepted_lifecycle_record_path).read_bytes()
            )
            record = self.fixture.lawful_lifecycle_record()
            record["roles"]["independent_audit_pass"]["sha256"] = lc.sha256_file(target)
            with self.assertRaises(lc.U06LifecycleError) as caught:
                lc.validate_accepted_lifecycle_payload(
                    self.fixture.root,
                    record,
                    record_relative=self.fixture.record_relative,
                    generation=GEN,
                )
            self.assertIn(
                caught.exception.status,
                {
                    "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
                    "U06_CROSS_GENERATION_ROLE_REJECTED",
                    "U06_ROLE_SCHEMA_MISMATCH",
                },
            )
        finally:
            target.write_bytes(original)

    def test_predecessor_digest_in_an_r2_role_is_rejected(self) -> None:
        payload = self._role_record("independent_audit_pass")
        payload["implementation_identity_digest"] = (
            "b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a"
        )
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_role_envelope(
                self.fixture.root,
                "independent_audit_pass",
                self.fixture.roles["independent_audit_pass"]["path"],
                payload,
                live_digest=self.fixture.live_digest,
                generation=GEN,
            )
        self.assertEqual(
            caught.exception.status, "U06_IMPLEMENTATION_IDENTITY_DRIFT"
        )

    def test_superseded_generation_lifecycle_cannot_freeze(self) -> None:
        """Even a structurally perfect predecessor lifecycle cannot freeze."""

        superseded = {
            **self.fixture.resolve_lifecycle(),
            "generation_id": PRED.generation_id,
            "is_current_generation": False,
            "lineage_id": PRED.lineage_id,
            "target_candidate_id": PRED.candidate_id,
        }
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_frozen_lifecycle(superseded)
        self.assertEqual(
            caught.exception.status, "U06_SUPERSEDED_GENERATION_REJECTED"
        )

    def test_wrong_audit_publication_commit_is_rejected(self) -> None:
        closure = json.loads(
            (
                self.fixture.root
                / self.fixture.roles["acceptance_closure"]["path"]
            ).read_text(encoding="utf-8")
        )
        closure["audit_publication_commit"] = self.fixture.commit_base
        resolved = {
            "independent_audit_pass": {
                "path": self.fixture.roles["independent_audit_pass"]["path"],
                "sha256": self.fixture.roles["independent_audit_pass"]["sha256"],
            }
        }
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_role_specifics(
                self.fixture.root,
                "acceptance_closure",
                self.fixture.roles["acceptance_closure"]["path"],
                closure,
                resolved,
                GEN,
            )
        self.assertEqual(
            caught.exception.status, "U06_PUBLICATION_PROOF_INVALID"
        )


# ---------------------------------------------------------------------------
# B2. R4-AUD-01 - the candidate manifest is bound from OUTSIDE itself
# ---------------------------------------------------------------------------


R4_MANIFEST_PATH = lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH


class CandidateManifestExternalBindingTests(unittest.TestCase):
    """R4-AUD-01: the lifecycle binds the manifest's identity; it never does.

    A candidate manifest cannot carry its own final SHA-256, so its identity
    is bound by the later lifecycle role records and the accepted-lifecycle
    record. These controls drive the REAL production validators against a
    fully promoted throwaway repository; nothing is mocked into success.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def _record(self, role: str) -> dict:
        entry = self.fixture.roles[role]
        return json.loads(
            (self.fixture.root / entry["path"]).read_text(encoding="utf-8")
        )

    def _envelope_status(self, role: str, record: dict) -> str:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_role_envelope(
                self.fixture.root,
                role,
                self.fixture.roles[role]["path"],
                record,
                live_digest=self.fixture.live_digest,
                generation=GEN,
            )
        return caught.exception.status

    def test_nc10_gate_mode_contract_passes_in_a_clean_promoted_checkout(self) -> None:
        """Positive control: GATE binds every identity, history externally.

        R6-AUD-01: this control used to REQUIRE a non-zero structural count -
        it encoded the defect as expected behaviour. R7-AUD-01: it then passed
        WITHOUT any historical evidence, because V3 took historical values from
        the candidate's own table. Under contract V4 the promoted checkout
        carries the external historical evidence, the GATE authenticates the
        Git-frozen trust root through the fixture's published ancestry, and
        every historical identity binds to the externally derived value. The
        same checkout WITHOUT that evidence fails closed (next control).
        """

        # G1: the current generation's own content contract, dispatched by the
        # generation (never V4), binds every identity in GATE mode.
        report = lc.validate_candidate_manifest_content_contract(
            self.fixture.root,
            GEN.candidate_manifest_path,
            generation=GEN,
            mode=lc.CANDIDATE_MANIFEST_MODE_GATE,
        )
        self.assertEqual(report["contract"], lc.G1_CANDIDATE_MANIFEST_CONTRACT)
        self.assertEqual(report["unaccounted_identity_count"], 0)
        self.assertEqual(report["structural_identity_count"], 0)
        self.assertEqual(
            report["collected_identity_count"], report["verified_identity_count"]
        )
        self.assertEqual(
            report["collected_identity_count"], report["role_bound_identity_count"]
        )
        self.assertEqual(report["change_ledger"]["structural_identity_count"], 0)
        self.assertFalse(
            report["computed_binding_facts"]["manifest_records_own_sha256"]
        )
        self.assertFalse(
            report["computed_binding_facts"]["historical_identity_used_as_live_binding"]
        )
        self.assertEqual(
            report["validation_identity_authority"], "PUBLISHED_WITH_CANDIDATE_MANIFEST"
        )

    def test_nc10_neither_mode_skips_absent_historical_provenance(
        self,
    ) -> None:
        """HISTORICAL control: without its external evidence, V4 fails closed.

        R7-AUD-01: under V3 only CANDIDATE_PACKAGE failed here; GATE passed on
        the candidate's own table.  Under V4 there is no candidate-local
        fallback in either mode.  G1: V4 is R8's contract, so it is driven
        against the R8 generation explicitly, in a reconstruction that carries
        no ignored R1-R7 evidence; and the G1 lifecycle, which does not
        consume that evidence, resolves valid in the very same checkout.
        """

        fixture = self.fixture
        for package in lc.CANDIDATE_PRESERVATION_PACKAGES.values():
            self.assertFalse((fixture.root / package["directory"]).exists())
        for mode in lc.CANDIDATE_MANIFEST_MODES:
            with self.subTest(mode=mode):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.validate_candidate_manifest_identity_contract(
                        fixture.root,
                        R8_GEN.candidate_manifest_path,
                        generation=R8_GEN,
                        mode=mode,
                    )
                self.assertEqual(
                    caught.exception.status,
                    lc.EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE,
                )
        self.assertEqual(
            lc.resolve_u06_lifecycle(fixture.root)["accepted_lifecycle_overlay"],
            "PRESENT_VALID",
        )

    def test_nc07_every_later_role_must_carry_the_external_manifest_binding(
        self,
    ) -> None:
        roles = [
            role
            for role, contract in GEN.role_contracts.items()
            if contract.declares_candidate_manifest
        ]
        self.assertEqual(len(roles), 4)
        for role in roles:
            with self.subTest(role=role):
                record = self._record(role)
                self.assertIn("candidate_manifest", record)
                del record["candidate_manifest"]
                self.assertEqual(
                    self._envelope_status(role, record), "U06_ROLE_SCHEMA_INVALID"
                )

    def test_nc07_lifecycle_without_the_implementation_candidate_binding_fails(
        self,
    ) -> None:
        record = self.fixture.lawful_lifecycle_record()
        del record["roles"]["implementation_candidate"]
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_accepted_lifecycle_payload(
                self.fixture.root,
                record,
                record_relative=self.fixture.record_relative,
                generation=GEN,
            )
        self.assertEqual(
            caught.exception.status, "U06_ACCEPTED_LIFECYCLE_INCOMPLETE"
        )

    def test_nc07_declared_binding_fields_are_exactly_what_the_lifecycle_enforces(
        self,
    ) -> None:
        manifest = json.loads(
            (self.fixture.root / GEN.candidate_manifest_path).read_text(
                encoding="utf-8"
            )
        )
        own = manifest["durable_publication_declaration"]["entries"][
            GEN.candidate_manifest_path
        ]
        self.assertEqual(own["identity_source"], "EXTERNAL_LIFECYCLE_ROLE_BINDING")
        self.assertEqual(
            own["external_binding_fields"],
            list(lc.candidate_manifest_external_binding_fields(GEN)),
        )
        declared = {
            field.split(".", 1)[0]
            for field in own["external_binding_fields"]
            if field.endswith(".candidate_manifest.sha256")
        }
        enforced = {
            role
            for role, contract in GEN.role_contracts.items()
            if contract.declares_candidate_manifest
        }
        self.assertEqual(declared, enforced)

    def test_nc14_external_binding_to_the_wrong_manifest_bytes_is_rejected(
        self,
    ) -> None:
        live = lc.sha256_file(self.fixture.root / GEN.candidate_manifest_path)
        stale = hashlib.sha256(
            (self.fixture.root / GEN.candidate_manifest_path).read_bytes() + b"\n"
        ).hexdigest()
        r4 = lc.sha256_file(ROOT / R4_MANIFEST_PATH)
        for label, binding in (
            ("stale_r5_bytes", {"path": GEN.candidate_manifest_path, "sha256": stale}),
            ("r4_digest_at_r5_path", {"path": GEN.candidate_manifest_path, "sha256": r4}),
            ("r4_path_and_digest", {"path": R4_MANIFEST_PATH, "sha256": r4}),
        ):
            with self.subTest(binding=label):
                self.assertNotEqual(binding["sha256"], live)
                record = self._record("independent_audit_pass")
                record["candidate_manifest"] = binding
                self.assertEqual(
                    self._envelope_status("independent_audit_pass", record),
                    "U06_ROLE_TARGET_MISMATCH",
                )

    def test_nc09_r4_manifest_cannot_fill_the_r5_candidate_role(self) -> None:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc._validate_role_path(
                "implementation_candidate",
                R4_MANIFEST_PATH,
                self.fixture.record_relative,
                GEN,
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")
        r4 = json.loads((ROOT / R4_MANIFEST_PATH).read_text(encoding="utf-8"))
        # G1: an R4 (or R8) manifest belongs to ANOTHER generation, so it is
        # refused as the wrong artifact TYPE before its candidate id is read.
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_role_envelope(
                self.fixture.root,
                "implementation_candidate",
                GEN.candidate_manifest_path,
                r4,
                live_digest=self.fixture.live_digest,
                generation=GEN,
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_ARTIFACT_TYPE_MISMATCH")
        # And re-typed into the G1 namespace, a superseded candidate id is
        # still never revived.
        contract = GEN.role_contracts["implementation_candidate"]
        for superseded in (r4["candidate_id"], R8_GEN.candidate_id):
            with self.subTest(target=superseded):
                retyped = dict(
                    r4,
                    artifact_type=contract.artifact_type,
                    schema_version=contract.schema_version,
                    lineage_id=GEN.lineage_id,
                    target_candidate_id=superseded,
                )
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc.validate_role_envelope(
                        self.fixture.root,
                        "implementation_candidate",
                        GEN.candidate_manifest_path,
                        retyped,
                        live_digest=self.fixture.live_digest,
                        generation=GEN,
                    )
                self.assertEqual(
                    caught.exception.status, "U06_SUPERSEDED_CANDIDATE_REJECTED"
                )


class CandidateManifestPostBindingMutationTests(unittest.TestCase):
    """Bytes that change after the external binding exists can never freeze.

    Each control mutates its OWN throwaway promoted repository, so no other
    test observes the mutation.
    """

    def test_nc08_one_byte_change_after_external_binding_breaks_the_freeze(
        self,
    ) -> None:
        fixture = _Fixture()
        try:
            self.assertTrue(lc.is_frozen(fixture.resolve_lifecycle()))
            path = fixture.root / GEN.candidate_manifest_path
            path.write_bytes(path.read_bytes() + b"\n")
            resolved = fixture.resolve_lifecycle()
            self.assertEqual(resolved["accepted_lifecycle_overlay"], "PRESENT_INVALID")
            self.assertEqual(resolved["rejected_status"], "U06_ROLE_TARGET_MISMATCH")
            self.assertFalse(lc.is_frozen(resolved))
        finally:
            fixture.dispose()

    def test_nc09_r4_bytes_at_the_r5_manifest_path_never_freeze(self) -> None:
        fixture = _Fixture()
        try:
            path = fixture.root / GEN.candidate_manifest_path
            # G1: the R4 bytes AND the accepted-and-superseded R8 bytes.
            for label, source in (
                ("r4", R4_MANIFEST_PATH),
                ("r8", R8_GEN.candidate_manifest_path),
            ):
                with self.subTest(predecessor=label):
                    path.write_bytes((ROOT / source).read_bytes())
                    resolved = fixture.resolve_lifecycle()
                    self.assertEqual(resolved["accepted_lifecycle_overlay"], "PRESENT_INVALID")
                    self.assertEqual(resolved["rejected_status"], "U06_ROLE_TARGET_MISMATCH")
                    self.assertFalse(lc.is_frozen(resolved))
                    # Even a lifecycle record re-declared to those exact bytes
                    # cannot accept them: they are another generation's
                    # artifact, refused on TYPE before their superseded
                    # candidate id is reached (see nc09 above).
                    record = fixture.lawful_lifecycle_record()
                    record["roles"]["implementation_candidate"]["sha256"] = (
                        lc.sha256_file(path)
                    )
                    with self.assertRaises(lc.U06LifecycleError) as caught:
                        lc.validate_accepted_lifecycle_payload(
                            fixture.root,
                            record,
                            record_relative=fixture.record_relative,
                            generation=GEN,
                        )
                    self.assertEqual(
                        caught.exception.status, "U06_ROLE_ARTIFACT_TYPE_MISMATCH"
                    )
        finally:
            fixture.dispose()


# ---------------------------------------------------------------------------
# C. H-02 - the authorization binds the RESOLVED current generation
# ---------------------------------------------------------------------------


class DynamicProductionAuthorityBindingTests(unittest.TestCase):
    """H-02: no static predecessor-lineage dependency may remain."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def test_no_static_expected_lineage_constant_exists(self) -> None:
        self.assertFalse(hasattr(auth, "REQUIRED_U06_LINEAGE_ID"))
        tree = ast.parse(MECHANISM_SOURCE.read_text(encoding="utf-8"))
        assigned = {
            t.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for t in node.targets
            if isinstance(t, ast.Name)
        }
        self.assertNotIn("REQUIRED_U06_LINEAGE_ID", assigned)
        requirements = auth.future_authorization_requirements()
        self.assertTrue(
            requirements["production_authority_binding_is_resolved_not_static"]
        )
        self.assertFalse(
            requirements["expected_production_authority_lineage_constant_exists"]
        )

    def test_authorization_binds_the_resolved_r2_generation(self) -> None:
        resolved_auth = self.fixture.resolve_authorization()
        resolved_lc = self.fixture.resolve_lifecycle()
        self.assertEqual(
            resolved_auth["production_authority_generation_id"],
            resolved_lc["generation_id"],
        )
        self.assertEqual(
            resolved_auth["production_authority_lineage_id"],
            resolved_lc["lineage_id"],
        )
        self.assertEqual(
            resolved_auth["production_authority_accepted_lifecycle_record"],
            resolved_lc["record_path"],
        )
        self.assertEqual(
            resolved_auth["production_authority_publication_commit"],
            self.fixture.commit_phase_c,
        )

    def test_predecessor_r3_lineage_in_the_authorization_is_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["production_authority_lineage_id"] = PRED.lineage_id
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        )

    def test_predecessor_r3_generation_id_is_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["production_authority_generation_id"] = PRED.generation_id
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        )

    def test_predecessor_lifecycle_record_is_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["production_authority_accepted_lifecycle_record"] = {
            "path": PRED.accepted_lifecycle_record_path,
            "sha256": lc.sha256_file(
                self.fixture.root / PRED.accepted_lifecycle_record_path
            ),
        }
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        )

    def test_publication_commit_is_resolved_not_hard_coded(self) -> None:
        """No commit hash is CONSUMED as authority by this mechanism.

        R3-AUD-04. This asserted that the module's whole source text contains
        exactly one 40-hex literal. A later candidate documented, in a comment,
        the publication commit of the superseded ``r2`` authorization artifact
        — provenance prose that no code reads — and the test failed although
        nothing had become hard-coded. Counting characters in a file was the
        wrong instrument for the invariant.

        The invariant is now tested directly, and more strictly: the module is
        parsed, every 40-hex literal that appears in EXECUTABLE code is
        collected separately from those that appear only in comments and
        docstrings, and the executable set must be exactly the one recorded
        historical precedent. A commit hash newly consumed by any code path
        fails this, and a commit hash merely cited in prose does not.
        """

        source = MECHANISM_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("e10f8f12", source)

        precedent = "b03721275c73b05d45517bdf84c1e0bd03833376"
        pattern = re.compile(r"\b[0-9a-f]{40}\b")
        tree = ast.parse(source)

        # Docstrings are string expressions in a module/class/function body;
        # they are documentation, not consumed values.
        docstring_nodes = set()
        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                body = getattr(node, "body", [])
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    docstring_nodes.add(id(body[0].value))

        executable_hex: set[str] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and id(node) not in docstring_nodes
            ):
                executable_hex.update(pattern.findall(node.value))

        self.assertEqual(
            executable_hex,
            {precedent},
            "a 40-hex commit literal is consumed by executable code",
        )

        # Every other 40-hex literal in the file must be documentation only.
        all_hex = set(pattern.findall(source))
        documentation_only = all_hex - executable_hex
        for literal in documentation_only:
            with self.subTest(literal=literal):
                # It must not appear in any executable string constant...
                self.assertNotIn(literal, executable_hex)
                # ...and it must not be reachable as any module attribute.
                for name in dir(auth):
                    value = getattr(auth, name)
                    if isinstance(value, str):
                        self.assertNotEqual(value, literal)

        self.assertEqual(
            auth.historical_design_precedent()["historical_tag_peeled_commit"],
            precedent,
        )
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["production_authority_publication_commit"] = (
            self.fixture.commit_base
        )
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
        )

    def test_schema_version_advanced_for_changed_semantics(self) -> None:
        self.assertEqual(
            auth.AUTHORIZATION_SCHEMA_VERSION,
            "iris-thesis-full81-authorization-v2",
        )
        self.assertIn(
            "iris-thesis-full81-authorization-v1",
            auth.SUPERSEDED_AUTHORIZATION_SCHEMA_VERSIONS,
        )
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["schema_version"] = "iris-thesis-full81-authorization-v1"
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status, "FULL81_AUTHORIZATION_SCHEMA_MISMATCH"
        )

    def test_failed_candidate_r1_cannot_authorize(self) -> None:
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload["candidate_id"] = (
            "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1"
        )
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload)
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_SUPERSEDED_CANDIDATE_REJECTED",
        )

    def test_r1_authorization_path_is_barred(self) -> None:
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            auth.validate_authorization_payload(
                self.fixture.root,
                self.fixture.lawful_authorization(),
                record_relative=(
                    "results/provenance/main_full81_authorization_r1/"
                    "main_full81_authorization.json"
                ),
                lifecycle=self.fixture.resolve_lifecycle(),
            )
        self.assertEqual(
            caught.exception.status,
            "FULL81_AUTHORIZATION_SUPERSEDED_CANDIDATE_REJECTED",
        )


# ---------------------------------------------------------------------------
# D. RETAINED AUTHORIZATION CONTROLS
# ---------------------------------------------------------------------------


class RetainedAuthorizationControlTests(unittest.TestCase):
    """Every control Candidate R1 got right must still hold."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def mutated(self, **changes) -> dict:
        payload = copy.deepcopy(self.fixture.lawful_authorization())
        payload.update(changes)
        return payload

    def assertRejected(self, payload, status, *, lifecycle=...) -> None:
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_authorization(payload, lifecycle=lifecycle)
        self.assertEqual(caught.exception.status, status)

    def test_wrong_artifact_type_and_schema(self) -> None:
        self.assertRejected(
            self.mutated(artifact_type="U06_ACCEPTANCE_CLOSURE"),
            "FULL81_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH",
        )
        self.assertRejected(
            self.mutated(schema_version="something-else"),
            "FULL81_AUTHORIZATION_SCHEMA_MISMATCH",
        )

    def test_wrong_role_path(self) -> None:
        for wrong in (
            "results/provenance/elsewhere/main_full81_authorization.json",
            "src/main_full81_authorization_v7_4.py",
            "docs/checkpoints/main_full81_authorization.json",
        ):
            with self.subTest(path=wrong):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.validate_authorization_payload(
                        self.fixture.root,
                        self.fixture.lawful_authorization(),
                        record_relative=wrong,
                        lifecycle=self.fixture.resolve_lifecycle(),
                    )
                self.assertEqual(
                    caught.exception.status,
                    "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
                )

    def test_wrong_lineage(self) -> None:
        self.assertRejected(
            self.mutated(lineage_id="SOMETHING_ELSE"),
            "FULL81_AUTHORIZATION_LINEAGE_MISMATCH",
        )
        for rejected in auth.REJECTED_LINEAGE_IDS:
            with self.subTest(lineage=rejected):
                self.assertRejected(
                    self.mutated(lineage_id=rejected),
                    "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
                )

    def test_status_scope_and_broadening(self) -> None:
        self.assertRejected(
            self.mutated(authorization_status="PENDING"),
            "FULL81_AUTHORIZATION_STATUS_NOT_GRANTED",
        )
        self.assertRejected(
            self.mutated(authorization_scope="CORE_THREE"),
            "FULL81_AUTHORIZATION_SCOPE_MISMATCH",
        )
        for field, value in (
            ("authorizes", ["MAIN_FULL81_EXECUTION"]),
            ("authorizes_optimize_calls", True),
            ("authorizes_full81_execution", True),
            ("requires_no_solve_preflight_before_execution", False),
        ):
            with self.subTest(field=field):
                self.assertRejected(
                    self.mutated(**{field: value}),
                    "FULL81_AUTHORIZATION_SCOPE_BROADENED",
                )

    def test_a2_smuggling(self) -> None:
        self.assertRejected(
            self.mutated(
                authorizes=[auth.AUTHORIZED_NEXT_ACT, "A2_VARIABLE_FLOOR"]
            ),
            "FULL81_AUTHORIZATION_SCOPE_BROADENED",
        )
        self.assertRejected(
            self.mutated(a2_excluded=False),
            "FULL81_AUTHORIZATION_A2_SMUGGLING_REJECTED",
        )
        trimmed = self.mutated()
        trimmed["excluded_scopes"] = [
            i for i in auth.REQUIRED_DECLARED_EXCLUSIONS if not i.startswith("A2")
        ]
        self.assertRejected(
            trimmed, "FULL81_AUTHORIZATION_EXCLUSIONS_INCOMPLETE"
        )

    def test_grid_and_case_count(self) -> None:
        self.assertRejected(
            self.mutated(alpha_universe=[0.6, 0.65]),
            "FULL81_AUTHORIZATION_ALPHA_UNIVERSE_MISMATCH",
        )
        self.assertRejected(
            self.mutated(beta_universe_h=[4, 5, 6]),
            "FULL81_AUTHORIZATION_BETA_UNIVERSE_MISMATCH",
        )
        for count in (80, 82, "81", True, None):
            with self.subTest(count=count):
                self.assertRejected(
                    self.mutated(case_count=count),
                    "FULL81_AUTHORIZATION_CASE_COUNT_MISMATCH",
                )

    def test_wrong_runner_input_model_registry(self) -> None:
        payload = self.mutated()
        payload["target_runner"]["path"] = (
            "scripts/19b_run_final_layer_a_81_cases.py"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_TARGET_MISMATCH")
        payload = self.mutated()
        payload["target_runner"]["sha256"] = "a" * 64
        self.assertRejected(payload, "FULL81_AUTHORIZATION_RUNNER_HASH_MISMATCH")
        payload = self.mutated()
        payload["target_runner"]["version"] = (
            "v7.4-main-full81-no-solve-preflight-runner-2026-10-02-candidate-r1"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_TARGET_MISMATCH")
        payload = self.mutated()
        payload["canonical_annual_input"] = {
            "path": "data/processed/annual_input_v7_1.parquet",
            "sha256": "e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e",
        }
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_CANONICAL_INPUT_MISMATCH"
        )
        payload = self.mutated()
        payload["accepted_annual_model"]["sha256"] = "b" * 64
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_ANNUAL_MODEL_MISMATCH"
        )
        payload = self.mutated()
        payload["parameter_registry"]["sha256"] = "c" * 64
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_PARAMETER_REGISTRY_MISMATCH"
        )

    def test_solver_fingerprint_restart_policy_and_u_01(self) -> None:
        self.assertRejected(
            self.mutated(solver_parameter_fingerprint="d" * 64),
            "FULL81_AUTHORIZATION_SOLVER_FINGERPRINT_MISMATCH",
        )
        self.assertRejected(
            self.mutated(restart_policy="RESUME_PARTIAL"),
            "FULL81_AUTHORIZATION_RESTART_POLICY_INVALID",
        )
        for field, value in (
            ("u_01_blocks_main_full81", True),
            ("u_01_status", "RESOLVED"),
            ("u_01_must_be_frozen_before", ["A2_EXECUTION"]),
        ):
            with self.subTest(field=field):
                self.assertRejected(
                    self.mutated(**{field: value}),
                    "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
                )

    def test_implementation_identity_drift(self) -> None:
        self.assertRejected(
            self.mutated(implementation_identity_digest="e" * 64),
            "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        )
        self.assertRejected(
            self.mutated(
                implementation_identity_digest=(
                    "b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a"
                )
            ),
            "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        )

    def test_not_frozen_or_absent_lifecycle(self) -> None:
        for label, lifecycle in (
            ("omitted", None),
            ("absent", lc.absent_lifecycle()),
            (
                "one_optimistic_field",
                {"production_authority_freeze_status": "FROZEN"},
            ),
        ):
            with self.subTest(lifecycle=label):
                self.assertRejected(
                    self.fixture.lawful_authorization(),
                    "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
                    lifecycle=lifecycle,
                )

    def test_historical_v7_2_manifest_is_not_current_authority(self) -> None:
        blob = subprocess.run(
            [
                "git", "cat-file", "blob",
                f"{HISTORICAL_V7_2_TAG}^{{}}:{HISTORICAL_V7_2_MANIFEST}",
            ],
            cwd=ROOT, capture_output=True, check=False,
        )
        if blob.returncode != 0:
            self.skipTest("historical V7.2 manifest unreachable in this clone")
        historical = json.loads(blob.stdout.decode("utf-8"))
        self.assertEqual(
            hashlib.sha256(blob.stdout).hexdigest(),
            "4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9",
        )
        self.assertRejected(
            historical, "FULL81_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH"
        )
        self.assertRejected(
            self.mutated(lineage_id=historical["authority_manifest_version"]),
            "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
        )
        for path in auth.REJECTED_HISTORICAL_AUTHORIZATION_PATHS:
            with self.subTest(path=path):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.validate_authorization_payload(
                        self.fixture.root,
                        self.fixture.lawful_authorization(),
                        record_relative=path,
                        lifecycle=self.fixture.resolve_lifecycle(),
                    )
                self.assertEqual(
                    caught.exception.status,
                    "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
                )
        self.assertEqual(
            historical["routing"]["annual_input_consumed"],
            "data/processed/annual_input_v7_1.parquet",
        )

    def test_every_required_field_is_required(self) -> None:
        for field in auth.AUTHORIZATION_REQUIRED_FIELDS:
            if field in ("artifact_type", "schema_version"):
                continue
            payload = copy.deepcopy(self.fixture.lawful_authorization())
            payload.pop(field)
            with self.subTest(missing=field):
                self.assertRejected(
                    payload, "FULL81_AUTHORIZATION_SCHEMA_INVALID"
                )


class RepositoryStateControlTests(unittest.TestCase):
    """Absent, malformed, untracked, dirty, and post-authorization drift."""

    def test_absent_authorization(self) -> None:
        f = _Fixture(publish_authorization=False)
        try:
            (f.root / f.auth_relative).unlink()
            resolved = f.resolve_authorization()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertEqual(resolved["authorization_overlay"], "ABSENT")
            self.assertFalse(
                auth.is_authorized_for_preflight(f.root, resolved)
            )
        finally:
            f.dispose()

    def test_malformed_authorization(self) -> None:
        f = _Fixture(publish_authorization=False)
        try:
            f.write(f.auth_relative, "{ not json")
            f._commit("fixture: malformed")
            f.sync_upstream()
            resolved = f.resolve_authorization()
            self.assertEqual(resolved["authorization_overlay"], "PRESENT_INVALID")
            self.assertIn(
                "not readable JSON", resolved["authorization_blocked_reason"]
            )
        finally:
            f.dispose()

    def test_unpublished_authorization(self) -> None:
        f = _Fixture(publish_authorization=False)
        try:
            resolved = f.resolve_authorization()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertFalse(
                auth.is_authorized_for_preflight(f.root, resolved)
            )
        finally:
            f.dispose()

    def test_dirty_authorization(self) -> None:
        f = _Fixture()
        try:
            self.assertEqual(
                f.resolve_authorization()["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            payload = f.lawful_authorization()
            payload["note"] = "edited after publication"
            f.write_authorization(payload)
            resolved = f.resolve_authorization()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertEqual(resolved["authorization_overlay"], "PRESENT_INVALID")
            self.assertIn(
                "modified relative to HEAD",
                resolved["authorization_blocked_reason"],
            )
        finally:
            f.dispose()

    def test_post_authorization_code_drift_revokes_everything(self) -> None:
        f = _Fixture()
        try:
            self.assertTrue(
                auth.is_authorized_for_preflight(
                    f.root, f.resolve_authorization()
                )
            )
            drifted = f.root / "src/rainflow_validation_v7_2.py"
            drifted.write_text(
                drifted.read_text(encoding="utf-8") + "\n# post-auth edit\n",
                encoding="utf-8",
                newline="\n",
            )
            f._commit("fixture: post-auth code change")
            f.sync_upstream()
            self.assertFalse(lc.is_frozen(f.resolve_lifecycle()))
            resolved = f.resolve_authorization()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertFalse(
                auth.is_authorized_for_preflight(f.root, resolved)
            )
        finally:
            f.dispose()


# ---------------------------------------------------------------------------
# E. POSITIVE CONTROL AND EXECUTION SEPARATION
# ---------------------------------------------------------------------------


class PositiveControlTests(unittest.TestCase):
    """A lawful R2 authorization reaches exactly one state, and no further."""

    def test_lawful_authorization_reaches_preflight_authorization_only(self) -> None:
        f = _Fixture()
        try:
            resolved = f.resolve_authorization()
            self.assertEqual(
                resolved["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            self.assertEqual(resolved["authorization_overlay"], "PRESENT_VALID")
            self.assertEqual(resolved["authorization_scope"], "MAIN_FULL81")
            self.assertEqual(
                resolved["authorizes"],
                ["MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT"],
            )
            self.assertEqual(resolved["case_count"], 81)
            self.assertEqual(resolved["restart_policy"], "FRESH_RUN_ONLY")
            self.assertTrue(resolved["record_published"])
            self.assertFalse(resolved["self_authorized"])
            self.assertFalse(resolved["authorizes_optimize_calls"])
            self.assertFalse(resolved["authorizes_full81_execution"])
            self.assertTrue(resolved["a2_excluded"])
            self.assertIsNone(resolved["authorization_blocked_reason"])
            self.assertEqual(
                resolved["production_authority_generation_id"],
                GEN.generation_id,
            )

            granted = auth.require_full81_preflight_authorization(f.root, resolved)
            self.assertEqual(
                granted["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            self.assertTrue(auth.is_authorized_for_preflight(f.root, resolved))

            # G1: the execution guard decides on the repository whose scope
            # authorization this is.  The fixture holds no execution
            # authorization in any phase of the real repository (checked, not
            # assumed), so the lawful scope authorization reaches no further.
            from unittest.mock import patch

            self.assertEqual(
                auth.resolve_full81_execution_authorization(f.root)[
                    "execution_authorization_overlay"
                ],
                auth.ABSENT,
            )
            with patch.object(auth, "REPOSITORY_ROOT", f.root):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.require_full81_execution_authorization(resolved)
            self.assertEqual(
                caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED"
            )
        finally:
            f.dispose()

    def test_execution_interlock_rejects_under_every_state(self) -> None:
        from unittest.mock import patch

        f = _Fixture()
        try:
            # G1: decided on the fixture's own state, which holds no execution
            # authorization in any phase of the real repository.
            self.assertEqual(
                auth.resolve_full81_execution_authorization(f.root)[
                    "execution_authorization_overlay"
                ],
                auth.ABSENT,
            )
            for label, candidate in (
                ("absent", None),
                ("lawfully_authorized", f.resolve_authorization()),
            ):
                with self.subTest(authorization=label):
                    with patch.object(auth, "REPOSITORY_ROOT", f.root):
                        with self.assertRaises(auth.Full81AuthorizationError) as caught:
                            auth.require_full81_execution_authorization(candidate)
                    self.assertEqual(
                        caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED"
                    )
        finally:
            f.dispose()


# ---------------------------------------------------------------------------
# F. THE REAL REPOSITORY MUST REMAIN UNAUTHORIZED
# ---------------------------------------------------------------------------


def _no_native_solver_entry():
    """Refuse and record every native solver entry and native-backend creation.

    A deployment-gate decision is validation only: even an AUTHORIZED decision
    must construct no model, call no solver and create no production backend.
    """

    import contextlib
    from unittest.mock import patch

    @contextlib.contextmanager
    def guard():
        hits: list[str] = []

        def refuse(name: str):
            def _refuse(*args, **kwargs):
                hits.append(name)
                raise AssertionError(f"a gate decision reached {name}")

            return _refuse

        with contextlib.ExitStack() as guards:
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


class RealRepositoryRemainsUnauthorizedTests(unittest.TestCase):
    """Nothing a temporary fixture simulates may move the real gate."""

    def test_no_real_lifecycle_or_authorization_artifact_exists(self) -> None:
        # G1: phase-aware.  Every governance artifact beyond the reached phase
        # is absent (with its directory), and nothing is present out of order.
        phase = lc.current_generation_phase(ROOT)
        self.assertEqual(phase["out_of_order_present"], [])
        for key in (
            "accepted_lifecycle_record",
            "main_full81_scope_authorization",
            "main_full81_execution_authorization",
        ):
            relative = phase["paths"][key]
            with self.subTest(path=relative):
                if not phase["presence"][key]:
                    self.assertFalse((ROOT / relative).exists())
                    self.assertFalse((ROOT / relative).parent.exists())

    def test_real_lifecycle_is_absent_and_not_frozen(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        self.assertEqual(live["generation_id"], GEN.generation_id)
        self.assertTrue(live["is_current_generation"])
        if (ROOT / GEN.accepted_lifecycle_record_path).exists():
            self.assertEqual(live["accepted_lifecycle_overlay"], "PRESENT_VALID")
            self.assertTrue(lc.is_frozen(live))
            return
        self.assertEqual(live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(
            live["production_authority_freeze_status"], "NOT_FROZEN"
        )
        self.assertFalse(lc.is_frozen(live))

    def test_real_full81_is_not_authorized(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        resolved = auth.resolve_full81_authorization(ROOT, live)
        if (ROOT / auth.AUTHORIZATION_RECORD_RELATIVE_PATH).exists():
            self.assertEqual(
                resolved["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
        else:
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertFalse(auth.is_authorized_for_preflight(ROOT, resolved))
            with self.assertRaises(bundle.Full81AuthorizationNotGranted) as caught:
                bundle.require_full81_scope_authorization(
                    "full81", root=ROOT, lifecycle=live
                )
            self.assertEqual(
                caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED"
            )
        # Execution is a separate act in every phase but the last.
        if not (ROOT / auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH).exists():
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(resolved)
            self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")

    def test_real_gate_rejects_full81_and_a2(self) -> None:
        snapshot = stack.inspect_deployment_snapshot(ROOT)
        # G1: phase-aware, from the source contract (current_generation_phase
        # over G1_GOVERNANCE_STAGES); nothing may be present out of order.
        phase = lc.current_generation_phase(ROOT)
        self.assertEqual(phase["out_of_order_present"], [], phase["phase"])
        cases = [("a2_variable_floor", {"A2_HARD_BLOCKED"})]
        if not phase["presence"]["main_full81_execution_authorization"]:
            full81 = {"FULL81_AUTHORIZATION_NOT_GRANTED"}
            if phase["presence"]["main_full81_scope_authorization"]:
                full81.add("FULL81_EXECUTION_NOT_AUTHORIZED")
            cases.append(("full81", full81))
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
        if not phase["presence"]["main_full81_execution_authorization"]:
            return
        # Execution-authorized phase: the gate admits Full81 only because the
        # real G1 chain is VALID end to end (frozen lifecycle, valid scope
        # authorization, valid execution authorization), and the decision makes
        # no native solver entry.  Admission is not execution.
        lifecycle = snapshot.u06_accepted_lifecycle
        self.assertTrue(lc.is_frozen(lifecycle))
        scope = auth.resolve_full81_authorization(ROOT, lifecycle)
        execution = auth.resolve_full81_execution_authorization(ROOT, lifecycle, scope)
        self.assertEqual(scope["full81_authorization_status"], "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT")
        self.assertEqual(
            execution["execution_authorization_overlay"], "PRESENT_VALID",
            execution.get("rejected_status"),
        )
        self.assertEqual(
            execution["execution_authorization_status"], auth.AUTHORIZED_FOR_FULL81_EXECUTION
        )
        with _no_native_solver_entry() as native_hits:
            decision = stack.validate_deployment_snapshot(
                snapshot,
                execute_production=True,
                selected_scope="full81",
                root=ROOT,
            )
        self.assertEqual(native_hits, [])
        self.assertEqual(decision["status"], "PRODUCTION_AUTHORITY_FROZEN")

    def test_candidate_r1_provenance_is_unmodified(self) -> None:
        for relative, expected in (
            (
                "docs/checkpoints/"
                "main_full81_authorization_mechanism_candidate_r1_2026-10-02.md",
                "6ee0d67d34174070a63a7f5034957de6103c5fce47917e3893ea48966cb384a1",
            ),
            (
                "results/provenance/"
                "main_full81_authorization_mechanism_candidate_r1_2026-10-02/"
                "authorization_mechanism_manifest.json",
                "563ffa467cfac298cd3de3a1ee63976ebe98537c2d7169714636736c18205303",
            ),
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertEqual(lc.sha256_file(ROOT / relative), expected)

    def test_candidate_r1_source_bytes_are_preserved(self) -> None:
        snap = ROOT / (
            "results/provenance/"
            "main_full81_authorization_mechanism_candidate_r2_2026-10-02/"
            "superseded_sources"
        )
        self.assertTrue(snap.is_dir())
        for name, expected in (
            (
                "r1_main_full81_authorization_v7_4.py",
                "94d82d44dcabc5a6584facd5edf5647c9cd63240ef791194713f9a20a214359f",
            ),
            (
                "r1_production_authority_lifecycle_u06.py",
                "eabef43f66e94524c1fcbd87302da72229a97a0d70d0cb5ce9f9d3a230ff8660",
            ),
            (
                "r1_production_authority_bundle_v7_4.py",
                "15ac4f474357958816a4ed82d96a095807bf622228b9d2a49ec938200af43db4",
            ),
            (
                "r1_production_successor_stack_v7_3.py",
                "e37587ea1247775a350317ef5cc970fc7ea67f3ef2bc4e4673fdd3d9aaa8eaa7",
            ),
            (
                "r1_21d_preflight_v7_3_final81_successor.py",
                "489399bf7a39e5f35ac945444767f91f9277769bbeb1797a06b16a31a3f07d35",
            ),
            (
                "r1_test_21h_main_full81_authorization_mechanism.py",
                "81b8cd6c4a5fc57cdf270fadb18fcb0b5717ff22fecf1f9d021dcc53f755d519",
            ),
        ):
            with self.subTest(snapshot=name):
                self.assertEqual(lc.sha256_file(snap / name), expected)

    def test_u06_r3_accepted_artifacts_are_unmodified(self) -> None:
        for relative in (
            PRED.accepted_lifecycle_record_path,
            PRED.candidate_manifest_path,
            PRED.candidate_checkpoint_path,
        ):
            with self.subTest(path=relative):
                self.assertEqual(
                    _git_text(ROOT, "diff", "--name-only", "HEAD", "--", relative),
                    "",
                )

    def test_mechanism_and_overlay_contain_no_solver_entry_point(self) -> None:
        forbidden = {"optimize", "optimizeAsync", "optimizeBatch", "tune"}
        for source in (MECHANISM_SOURCE, OVERLAY_SOURCE):
            with self.subTest(source=source.name):
                tree = ast.parse(source.read_text(encoding="utf-8"))
                offenders = [
                    n
                    for n in ast.walk(tree)
                    if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr in forbidden
                ]
                self.assertEqual(offenders, [])

    def test_resolvers_write_nothing_to_the_real_repository(self) -> None:
        before = _git_text(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
        live = lc.resolve_u06_lifecycle(ROOT)
        auth.resolve_full81_authorization(ROOT, live)
        auth.resolve_full81_authorization(ROOT, None)
        after = _git_text(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
        self.assertEqual(before, after)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
