"""Main Full81 authorization-mechanism Candidate R2: fail-closed suite.

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


MECHANISM_SOURCE = ROOT / "src/main_full81_authorization_v7_4.py"
OVERLAY_SOURCE = ROOT / "src/production_authority_lifecycle_u06.py"

HISTORICAL_V7_2_TAG = "v7.2-final81-runner-ready-r3"
HISTORICAL_V7_2_MANIFEST = (
    "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json"
)

GEN = lc.CURRENT_GENERATION
PRED = lc.U06_R3_GENERATION


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
            + [
                auth.EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
                auth.EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
                auth.EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
                GEN.candidate_checkpoint_path,
                GEN.candidate_manifest_path,
                PRED.accepted_lifecycle_record_path,
                PRED.candidate_manifest_path,
                PRED.candidate_checkpoint_path,
            ]
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
        self, *, promote: bool = True, publish_authorization: bool = True
    ) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="full81_r2_fixture_")).resolve()
        self.auth_relative = auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        self.record_relative = GEN.accepted_lifecycle_record_path
        self.role_dir = "results/provenance/full81_auth_mech_r2_lifecycle"

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
        _git_ok(self.root, "checkout", "--quiet", "-B", "thesis-v7")
        self._commit("fixture: accepted surface + R2 candidate")
        self.commit_base = self.head()

        self.live_digest = lc.implementation_identity_digest(self.root)
        self.ckpt_sha = lc.sha256_file(self.root / GEN.candidate_checkpoint_path)
        self.manifest_sha = lc.sha256_file(
            self.root / GEN.candidate_manifest_path
        )

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
        rel = f"{self.role_dir}/independent_audit_pass_record.json"
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
        rel = f"{self.role_dir}/acceptance_closure.json"
        self.roles["acceptance_closure"] = {
            "path": rel,
            "sha256": self.write(rel, closure),
        }

        manifest = self._bind(
            self._envelope("acceptance_manifest"),
            ("independent_audit_pass", "acceptance_closure"),
        )
        manifest["acceptance_status"] = lc.ACCEPTED_ACCEPTANCE_STATUS
        rel = f"{self.role_dir}/acceptance_manifest.json"
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
        rel = f"{self.role_dir}/production_authority_re_freeze_record.json"
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

    def test_current_generation_targets_candidate_r2(self) -> None:
        self.assertEqual(
            GEN.generation_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_R2"
        )
        self.assertEqual(GEN.lineage_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_R1")
        self.assertEqual(
            GEN.candidate_id, "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2"
        )
        self.assertEqual(
            GEN.candidate_manifest_path,
            "results/provenance/"
            "main_full81_authorization_mechanism_candidate_r2_2026-10-02/"
            "authorization_mechanism_manifest.json",
        )
        self.assertEqual(
            GEN.accepted_lifecycle_record_path,
            "results/provenance/"
            "main_full81_authorization_mechanism_accepted_lifecycle_r2/"
            "accepted_lifecycle_record.json",
        )
        self.assertEqual(GEN.schema_prefix, "iris-thesis-full81-auth-mech-r2-")

    def test_u06_r3_is_an_immutable_historical_predecessor(self) -> None:
        self.assertEqual(PRED.generation_id, "U06_V7_4_PRODUCTION_AUTHORITY_R3")
        self.assertEqual(PRED.lineage_id, lc.LINEAGE_ID)
        self.assertEqual(PRED.candidate_id, lc.R3_CANDIDATE_ID)
        self.assertEqual(
            PRED.accepted_lifecycle_record_path,
            lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        )
        self.assertEqual(PRED.schema_prefix, "iris-thesis-u06-r3-")
        self.assertIn(PRED, lc.HISTORICAL_GENERATIONS)
        self.assertNotIn(GEN, lc.HISTORICAL_GENERATIONS)
        self.assertEqual(GEN.predecessor_generation_id, PRED.generation_id)
        self.assertEqual(GEN.predecessor_lineage_id, PRED.lineage_id)
        self.assertEqual(
            GEN.predecessor_accepted_lifecycle_record_path,
            PRED.accepted_lifecycle_record_path,
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
        self.assertIn(
            caught.exception.status,
            {
                "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
                "U06_CROSS_GENERATION_ROLE_REJECTED",
                "U06_ROLE_SCHEMA_MISMATCH",
            },
        )

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
        source = MECHANISM_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("e10f8f12", source)
        # The only permitted 40-hex literal is the historical V7.2 design-
        # precedent tag commit: recorded provenance, explicitly rejected as
        # current authority, and never a publication target.
        self.assertEqual(
            set(re.findall(r"\b[0-9a-f]{40}\b", source)),
            {"b03721275c73b05d45517bdf84c1e0bd03833376"},
        )
        self.assertEqual(
            auth.historical_design_precedent()["historical_tag_peeled_commit"],
            "b03721275c73b05d45517bdf84c1e0bd03833376",
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

            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(resolved)
            self.assertEqual(
                caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED"
            )
        finally:
            f.dispose()

    def test_execution_interlock_rejects_under_every_state(self) -> None:
        f = _Fixture()
        try:
            for label, candidate in (
                ("absent", None),
                ("lawfully_authorized", f.resolve_authorization()),
            ):
                with self.subTest(authorization=label):
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


class RealRepositoryRemainsUnauthorizedTests(unittest.TestCase):
    """Nothing a temporary fixture simulates may move the real gate."""

    def test_no_real_lifecycle_or_authorization_artifact_exists(self) -> None:
        for relative in (
            GEN.accepted_lifecycle_record_path,
            auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        ):
            with self.subTest(path=relative):
                self.assertFalse((ROOT / relative).exists())
                self.assertFalse((ROOT / relative).parent.exists())

    def test_real_lifecycle_is_absent_and_not_frozen(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        self.assertEqual(live["generation_id"], GEN.generation_id)
        self.assertTrue(live["is_current_generation"])
        self.assertEqual(live["accepted_lifecycle_overlay"], "ABSENT")
        self.assertEqual(
            live["production_authority_freeze_status"], "NOT_FROZEN"
        )
        self.assertFalse(lc.is_frozen(live))

    def test_real_full81_is_not_authorized(self) -> None:
        live = lc.resolve_u06_lifecycle(ROOT)
        resolved = auth.resolve_full81_authorization(ROOT, live)
        self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
        self.assertFalse(auth.is_authorized_for_preflight(ROOT, resolved))
        with self.assertRaises(bundle.Full81AuthorizationNotGranted) as caught:
            bundle.require_full81_scope_authorization(
                "full81", root=ROOT, lifecycle=live
            )
        self.assertEqual(
            caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED"
        )

    def test_real_gate_rejects_full81_and_a2(self) -> None:
        snapshot = stack.inspect_deployment_snapshot(ROOT)
        for scope, expected in (
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
