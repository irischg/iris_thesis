"""Main Full81 authorization-mechanism successor: fail-closed suite.

What this module proves
-----------------------
The accepted U-06 R3 architecture named ``SEPARATE_MAIN_FULL81_AUTHORIZATION``
but supplied no lawful mechanism for it: the only mechanical artefact was
``MAIN_FULL81_AUTHORIZATION_ARTIFACT = None``.  This suite exercises the
successor mechanism in ``src/main_full81_authorization_v7_4.py`` and proves:

* every one of 27 required failure modes is rejected with a stable status;
* a lawful authorization reaches ``AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT`` and
  nothing further — the execution interlock still refuses;
* the retired module constant remains ``None`` and is never consulted;
* no future authorization digest is hard-coded, reserved, or stubbed.

Fixture discipline
------------------
Negative controls that concern *payload content* are handed to the pure
validator as in-memory mappings, exactly as the accepted
``tests/test_21f_u06_accepted_lifecycle_gate.py`` hands synthetic lifecycle
mappings to the pure lifecycle validator.  Negative controls that concern
*repository state* (absent, malformed, untracked, dirty, unpublished) are run
against **isolated throwaway Git repositories** under the system temp
directory.

The synthetic frozen lifecycle mapping here is a test fixture handed to a pure
validator.  It is never written into the real repository and cannot move the
real gate, which resolves its lifecycle only from live bytes and Git.

No real Main Full81 authorization artifact is created in this repository.  Every
test is static / build-only: no model construction, no optimizer, no solver, no
production output directory, no Full81 case, and no A2 case.
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

#: Historical V7.2 Full81 runner-authority manifest, used as real attack bytes.
HISTORICAL_V7_2_TAG = "v7.2-final81-runner-ready-r3"
HISTORICAL_V7_2_MANIFEST = (
    "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json"
)


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
    done = _git(root, *args)
    return done.stdout.decode("utf-8", "replace").strip()


def _fixture_paths() -> tuple[str, ...]:
    """Every path an isolated authorization fixture must carry."""

    return tuple(
        dict.fromkeys(
            list(lc.ACCEPTED_IMPLEMENTATION_PATHS)
            + list(lc.VALIDATION_IDENTITY_PATHS)
            + [
                auth.EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
                auth.EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
                auth.EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
                lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
            ]
        )
    )


class _Fixture:
    """An isolated throwaway Git repository carrying the accepted surface.

    Three commits, so that publication containment can be attacked honestly:

    ``commit_pre``   the accepted implementation surface, WITHOUT the U-06
                     accepted-lifecycle record — an ancestor of HEAD in which
                     that record does not exist.
    ``commit_u06``   adds the U-06 accepted-lifecycle record.
    ``HEAD``         adds the Main Full81 authorization (when published).
    """

    def __init__(self, *, publish_authorization: bool = True) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="full81_auth_fixture_")).resolve()
        self.record_relative = auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        self.u06_relative = lc.ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()

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

        # commit_pre: everything except the U-06 accepted-lifecycle record.
        staged = self.root / self.u06_relative
        held = staged.read_bytes()
        staged.unlink()
        _git_ok(self.root, "add", "-A")
        _git_ok(self.root, "commit", "--quiet", "-m", "fixture: accepted surface")
        self.commit_pre = _git_text(self.root, "rev-parse", "HEAD")

        # commit_u06: publish the accepted-lifecycle record.
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(held)
        _git_ok(self.root, "add", "-A")
        _git_ok(self.root, "commit", "--quiet", "-m", "fixture: u06 lifecycle")
        self.commit_u06 = _git_text(self.root, "rev-parse", "HEAD")

        self.live_digest = lc.implementation_identity_digest(self.root)
        self.u06_sha256 = lc.sha256_file(self.root / self.u06_relative)
        self.lifecycle = self._synthetic_frozen_lifecycle()

        self.write_authorization(self.lawful_payload())
        if publish_authorization:
            self.publish()

    # -- lifecycle fixture --------------------------------------------------

    def _synthetic_frozen_lifecycle(self) -> dict:
        """A structurally complete FROZEN resolved lifecycle — fixture only.

        Mirrors the accepted ``test_21f`` idiom: it exercises the positive
        branch of the pure U-06 guard inside an isolated tree. It confers no
        acceptance; the real gate never reads it.
        """

        return {
            "lifecycle_module_version": lc.LIFECYCLE_MODULE_VERSION,
            "lineage_id": lc.LINEAGE_ID,
            "target_candidate_id": lc.R3_CANDIDATE_ID,
            "record_path": self.u06_relative,
            "record_present": True,
            "record_committed": True,
            "record_published": True,
            "self_accepted": False,
            "u06_alignment_status": lc.ACCEPTED_ALIGNMENT_STATUS,
            "u06_independent_audit_status": lc.ACCEPTED_AUDIT_STATUS,
            "u06_acceptance_status": lc.ACCEPTED_ACCEPTANCE_STATUS,
            "accepted_lifecycle_overlay": lc.PRESENT_VALID_OVERLAY_STATUS,
            "production_authority_freeze_status": lc.FROZEN_STATUS,
            "authorizes_main_full81": False,
            "freeze_blocked_reason": None,
            "implementation_identity_digest": self.live_digest,
            "required_future_roles": list(lc.REQUIRED_ACCEPTED_ROLES),
            "satisfied_roles": {
                role: {"path": f"results/fixture/{role}.json", "sha256": "0" * 64}
                for role in lc.REQUIRED_ACCEPTED_ROLES
            },
            "missing_roles": [],
            "required_lifecycle_sequence": list(lc.REQUIRED_LIFECYCLE_SEQUENCE),
            "lifecycle_distinctions": list(lc.LIFECYCLE_DISTINCTIONS),
            "candidate_r1_audit": dict(lc.CANDIDATE_R1_AUDIT_RECORD),
            "candidate_r2_audit": dict(lc.CANDIDATE_R2_AUDIT_RECORD),
        }

    # -- lawful authorization ----------------------------------------------

    def lawful_payload(self) -> dict:
        """The one lawful authorization shape, built from live fixture bytes."""

        runner_relative = auth.EXPECTED_RUNNER_RELATIVE_PATH
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
            "u06_lineage_id": auth.REQUIRED_U06_LINEAGE_ID,
            "u06_accepted_lifecycle_record": {
                "path": self.u06_relative,
                "sha256": self.u06_sha256,
            },
            "u06_publication_commit": self.commit_u06,
            "production_authority_freeze_status": "FROZEN",
            "implementation_identity_digest": self.live_digest,
            "target_runner": {
                "path": runner_relative,
                "version": auth.EXPECTED_RUNNER_VERSION,
                "sha256": lc.sha256_file(self.root / runner_relative),
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

    # -- fixture mutation ---------------------------------------------------

    def write_authorization(self, payload) -> None:
        path = self.root / self.record_relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8", newline="\n")
        else:
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )

    def publish(self) -> None:
        """Commit the authorization and synchronize the simulated upstream."""

        _git_ok(self.root, "add", "-A")
        _git_ok(
            self.root, "commit", "--quiet", "-m", "fixture: full81 authorization"
        )
        _git_ok(
            self.root,
            "update-ref",
            f"refs/remotes/{auth.EXPECTED_UPSTREAM}",
            _git_text(self.root, "rev-parse", "HEAD"),
        )

    def sync_upstream(self) -> None:
        _git_ok(
            self.root,
            "update-ref",
            f"refs/remotes/{auth.EXPECTED_UPSTREAM}",
            _git_text(self.root, "rev-parse", "HEAD"),
        )

    def validate(self, payload, *, lifecycle=...) -> dict:
        return auth.validate_authorization_payload(
            self.root,
            payload,
            record_relative=self.record_relative,
            lifecycle=self.lifecycle if lifecycle is ... else lifecycle,
        )

    def resolve(self) -> dict:
        return auth.resolve_full81_authorization(self.root, self.lifecycle)

    def dispose(self) -> None:
        """Remove the throwaway repository, clearing read-only Git object bits."""

        def _force(func, path, _exc) -> None:
            try:
                Path(path).chmod(stat.S_IWRITE)
                func(path)
            except OSError:
                pass

        shutil.rmtree(self.root, onexc=_force)
        if self.root.exists():  # pragma: no cover - defensive on locked trees
            shutil.rmtree(self.root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Section 1 — the mechanism's own contract
# ---------------------------------------------------------------------------


class MechanismContractTests(unittest.TestCase):
    """The role must be semantic, deterministic, and not constant-driven."""

    def test_role_contract_is_explicit_and_complete(self) -> None:
        contract = auth.AUTHORIZATION_ROLE_CONTRACT
        self.assertEqual(contract.role, "main_full81_scope_authorization")
        self.assertEqual(contract.artifact_type, "MAIN_FULL81_SCOPE_AUTHORIZATION")
        self.assertEqual(
            contract.schema_version, "iris-thesis-full81-authorization-v1"
        )
        self.assertEqual(contract.lineage_id, auth.LINEAGE_ID)
        self.assertEqual(contract.scope, "MAIN_FULL81")
        self.assertEqual(
            contract.lawful_path,
            "results/provenance/main_full81_authorization_r1/"
            "main_full81_authorization.json",
        )
        self.assertEqual(contract.authorizes, auth.AUTHORIZED_NEXT_ACT)
        self.assertEqual(
            set(auth.ROLE_CONTRACTS), {"main_full81_scope_authorization"}
        )

    def test_lineage_is_not_u06_and_not_u07(self) -> None:
        self.assertEqual(auth.LINEAGE_ID, "MAIN_FULL81_AUTHORIZATION_MECHANISM_R1")
        self.assertNotEqual(auth.LINEAGE_ID, lc.LINEAGE_ID)
        self.assertNotIn("U-07", auth.LINEAGE_ID)
        self.assertNotIn("U_07", auth.LINEAGE_ID)
        self.assertIn(lc.LINEAGE_ID, auth.REJECTED_LINEAGE_IDS)

    def test_authorized_universe_matches_the_live_production_grid(self) -> None:
        self.assertEqual(
            tuple(round(float(a), 2) for a in auth.EXPECTED_ALPHA_UNIVERSE),
            tuple(round(float(a), 2) for a in stack.ALPHAS),
        )
        self.assertEqual(auth.EXPECTED_BETA_UNIVERSE_H, stack.BETAS_H)
        self.assertEqual(auth.EXPECTED_CASE_COUNT, stack.EXPECTED_CASES)
        self.assertEqual(auth.EXPECTED_CASE_COUNT, 81)
        self.assertEqual(
            len(auth.EXPECTED_ALPHA_UNIVERSE) * len(auth.EXPECTED_BETA_UNIVERSE_H),
            81,
        )

    def test_solver_settings_match_the_live_accepted_layer_a_settings(self) -> None:
        self.assertEqual(
            dict(auth.EXPECTED_LAYER_A_SOLVER_SETTINGS),
            dict(stack.LAYER_A_SOLVER_SETTINGS),
        )
        self.assertRegex(auth.solver_parameter_fingerprint(), r"^[0-9a-f]{64}$")

    def test_accepted_identities_match_the_bundle_pins(self) -> None:
        pins = {pin.label: pin for pin in bundle.all_pins()}
        self.assertEqual(
            auth.EXPECTED_ANNUAL_MODEL_SHA256, pins["model_core"].sha256
        )
        self.assertEqual(
            auth.EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
            pins["model_core"].relative_path,
        )
        self.assertEqual(
            auth.EXPECTED_PARAMETER_REGISTRY_SHA256,
            pins["parameter_registry"].sha256,
        )
        self.assertEqual(
            auth.EXPECTED_ANNUAL_INPUT_SHA256,
            pins["canonical_planning_input"].sha256,
        )
        self.assertEqual(
            auth.EXPECTED_RUNNER_RELATIVE_PATH, pins["full81_runner"].relative_path
        )

    def test_live_runner_declares_the_authorized_runner_version(self) -> None:
        source = (ROOT / auth.EXPECTED_RUNNER_RELATIVE_PATH).read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            auth.declared_module_constant(source, "RUNNER_VERSION"),
            auth.EXPECTED_RUNNER_VERSION,
        )
        self.assertIsNone(
            auth.declared_module_constant(source, "NO_SUCH_CONSTANT_HERE")
        )
        self.assertIsNone(auth.declared_module_constant("def (", "RUNNER_VERSION"))

    def test_no_future_authorization_digest_is_hard_coded(self) -> None:
        """Only identities of already-accepted artifacts may be pinned here."""

        source = MECHANISM_SOURCE.read_text(encoding="utf-8")
        permitted = {
            auth.EXPECTED_ANNUAL_INPUT_SHA256,
            auth.EXPECTED_ANNUAL_MODEL_SHA256,
            auth.EXPECTED_PARAMETER_REGISTRY_SHA256,
            # Historical V7.2 design-precedent identities, recorded as
            # provenance and explicitly rejected as current authority.
            "4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe",
            "4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9",
        }
        found = set(re.findall(r"\b[0-9a-f]{64}\b", source))
        self.assertEqual(
            found - permitted,
            set(),
            "The mechanism must not hard-code, reserve, or stub any future "
            "authorization digest.",
        )
        requirements = auth.future_authorization_requirements()
        self.assertFalse(requirements["record_exists_today"])
        self.assertFalse(requirements["future_hashes_fabricated_now"])
        self.assertFalse(requirements["placeholder_digests_present"])
        self.assertFalse(requirements["mutable_python_constant_can_authorize"])
        self.assertFalse(requirements["authorization_implies_execution"])
        self.assertFalse(
            requirements["arbitrary_ancestor_accepted_as_publication_proof"]
        )

    def test_mechanism_contains_no_solver_entry_point(self) -> None:
        forbidden = {"optimize", "optimizeAsync", "optimizeBatch", "tune"}
        tree = ast.parse(MECHANISM_SOURCE.read_text(encoding="utf-8"))
        offenders = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in forbidden
        ]
        self.assertEqual(offenders, [])

    def test_retired_constant_is_none_and_never_consulted(self) -> None:
        self.assertIsNone(bundle.MAIN_FULL81_AUTHORIZATION_ARTIFACT)
        self.assertEqual(
            bundle.MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH,
            auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        )
        record = bundle.alignment_is_not_full81_authorization(None, None)
        self.assertTrue(record["main_full81_authorization_artifact_constant_is_retired"])
        self.assertEqual(record["main_full81_authorization"], "NOT_AUTHORIZED")
        self.assertFalse(record["authorization_implies_execution"])
        self.assertTrue(record["separate_execution_authorization_required"])

    def test_no_real_authorization_artifact_exists_in_this_repository(self) -> None:
        self.assertFalse(
            (ROOT / auth.AUTHORIZATION_RECORD_RELATIVE_PATH).exists(),
            "This pass must leave no real Main Full81 authorization behind.",
        )
        resolved = auth.resolve_full81_authorization(
            ROOT, lc.resolve_u06_lifecycle(ROOT)
        )
        self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
        self.assertEqual(resolved["authorization_overlay"], "ABSENT")
        self.assertFalse(auth.is_authorized_for_preflight(ROOT, resolved))


# ---------------------------------------------------------------------------
# Section 2 — the 27 required negative controls
# ---------------------------------------------------------------------------


class _FixtureCase(unittest.TestCase):
    fixture: _Fixture

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = _Fixture()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def mutated(self, **changes) -> dict:
        payload = copy.deepcopy(self.fixture.lawful_payload())
        payload.update(changes)
        return payload

    def assertRejected(self, payload, status, *, lifecycle=...) -> None:
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate(payload, lifecycle=lifecycle)
        self.assertEqual(caught.exception.status, status)


class PayloadNegativeControlTests(_FixtureCase):
    """N-03 .. N-21, N-25, N-26, N-27 — payload-content rejections."""

    def test_n03_wrong_artifact_type(self) -> None:
        self.assertRejected(
            self.mutated(artifact_type="U06_ACCEPTANCE_CLOSURE"),
            "FULL81_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH",
        )

    def test_n04_wrong_schema_version(self) -> None:
        self.assertRejected(
            self.mutated(schema_version="iris-thesis-full81-authorization-v2"),
            "FULL81_AUTHORIZATION_SCHEMA_MISMATCH",
        )

    def test_n05_wrong_role_path(self) -> None:
        for wrong in (
            "results/provenance/elsewhere/main_full81_authorization.json",
            "src/main_full81_authorization_v7_4.py",
            "docs/checkpoints/main_full81_authorization.json",
        ):
            with self.subTest(path=wrong):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.validate_authorization_payload(
                        self.fixture.root,
                        self.fixture.lawful_payload(),
                        record_relative=wrong,
                        lifecycle=self.fixture.lifecycle,
                    )
                self.assertEqual(
                    caught.exception.status,
                    "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
                )

    def test_n06_wrong_lineage(self) -> None:
        self.assertRejected(
            self.mutated(lineage_id="SOME_OTHER_LINEAGE"),
            "FULL81_AUTHORIZATION_LINEAGE_MISMATCH",
        )
        self.assertRejected(
            self.mutated(candidate_id="SOME_OTHER_CANDIDATE"),
            "FULL81_AUTHORIZATION_LINEAGE_MISMATCH",
        )

    def test_n06b_superseded_or_unrelated_lineage_is_named_and_rejected(self) -> None:
        for rejected in auth.REJECTED_LINEAGE_IDS:
            with self.subTest(lineage=rejected):
                self.assertRejected(
                    self.mutated(lineage_id=rejected),
                    "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
                )

    def test_n07_wrong_target_runner_path(self) -> None:
        payload = self.mutated()
        payload["target_runner"]["path"] = (
            "scripts/19b_run_final_layer_a_81_cases.py"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_TARGET_MISMATCH")

    def test_n08_authorization_status_not_granted(self) -> None:
        for status in ("PENDING", "CANDIDATE", "NOT_GRANTED", "REVOKED", True):
            with self.subTest(status=status):
                self.assertRejected(
                    self.mutated(authorization_status=status),
                    "FULL81_AUTHORIZATION_STATUS_NOT_GRANTED",
                )

    def test_n09_wrong_scope(self) -> None:
        self.assertRejected(
            self.mutated(authorization_scope="CORE_THREE"),
            "FULL81_AUTHORIZATION_SCOPE_MISMATCH",
        )

    def test_n10_a2_scope_smuggling(self) -> None:
        payload = self.mutated(
            authorizes=[
                auth.AUTHORIZED_NEXT_ACT,
                "A2_VARIABLE_FLOOR_TREATMENT_EFFECT",
            ]
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_SCOPE_BROADENED")
        self.assertRejected(
            self.mutated(a2_excluded=False),
            "FULL81_AUTHORIZATION_A2_SMUGGLING_REJECTED",
        )
        smuggled = self.mutated(authorization_scope="MAIN_FULL81")
        smuggled["excluded_scopes"] = [
            item
            for item in auth.REQUIRED_DECLARED_EXCLUSIONS
            if not item.startswith("A2")
        ]
        self.assertRejected(smuggled, "FULL81_AUTHORIZATION_EXCLUSIONS_INCOMPLETE")

    def test_n11_alpha_universe_altered(self) -> None:
        for alphas in (
            [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
            [0.55, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00],
            [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05],
            [],
        ):
            with self.subTest(alphas=alphas):
                self.assertRejected(
                    self.mutated(alpha_universe=alphas),
                    "FULL81_AUTHORIZATION_ALPHA_UNIVERSE_MISMATCH",
                )

    def test_n12_beta_universe_altered(self) -> None:
        for betas in (
            [4, 5, 6, 7, 8, 9, 10, 11],
            [3, 5, 6, 7, 8, 9, 10, 11, 12],
            [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            [],
        ):
            with self.subTest(betas=betas):
                self.assertRejected(
                    self.mutated(beta_universe_h=betas),
                    "FULL81_AUTHORIZATION_BETA_UNIVERSE_MISMATCH",
                )

    def test_n13_case_count_is_not_81(self) -> None:
        for count in (80, 82, 3, 0, "81", True, None):
            with self.subTest(count=count):
                self.assertRejected(
                    self.mutated(case_count=count),
                    "FULL81_AUTHORIZATION_CASE_COUNT_MISMATCH",
                )

    def test_n14_wrong_canonical_input(self) -> None:
        payload = self.mutated()
        payload["canonical_annual_input"] = {
            "path": "data/processed/annual_input_v7_1.parquet",
            "sha256": "e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e",
        }
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_CANONICAL_INPUT_MISMATCH"
        )
        wrong_hash = self.mutated()
        wrong_hash["canonical_annual_input"]["sha256"] = "a" * 64
        self.assertRejected(
            wrong_hash, "FULL81_AUTHORIZATION_CANONICAL_INPUT_MISMATCH"
        )

    def test_n15_wrong_annual_model(self) -> None:
        payload = self.mutated()
        payload["accepted_annual_model"]["path"] = "src/rainflow_validation_v7_2.py"
        self.assertRejected(payload, "FULL81_AUTHORIZATION_ANNUAL_MODEL_MISMATCH")
        wrong_hash = self.mutated()
        wrong_hash["accepted_annual_model"]["sha256"] = "b" * 64
        self.assertRejected(
            wrong_hash, "FULL81_AUTHORIZATION_ANNUAL_MODEL_MISMATCH"
        )

    def test_n16_wrong_parameter_registry(self) -> None:
        payload = self.mutated()
        payload["parameter_registry"]["path"] = (
            "data/reference/taipower_tariff_registry_v7_1.csv"
        )
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_PARAMETER_REGISTRY_MISMATCH"
        )
        wrong_hash = self.mutated()
        wrong_hash["parameter_registry"]["sha256"] = "c" * 64
        self.assertRejected(
            wrong_hash, "FULL81_AUTHORIZATION_PARAMETER_REGISTRY_MISMATCH"
        )

    def test_n17_wrong_runner_version(self) -> None:
        payload = self.mutated()
        payload["target_runner"]["version"] = (
            "v7.2-final-layer-a-81-production-runner-2026-09-11-r3"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_TARGET_MISMATCH")

    def test_n18_wrong_runner_hash(self) -> None:
        payload = self.mutated()
        payload["target_runner"]["sha256"] = (
            "4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_RUNNER_HASH_MISMATCH")

    def test_n19_wrong_implementation_identity(self) -> None:
        self.assertRejected(
            self.mutated(implementation_identity_digest="d" * 64),
            "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        )

    def test_n20_production_authority_not_frozen(self) -> None:
        self.assertRejected(
            self.mutated(production_authority_freeze_status="NOT_FROZEN"),
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
        )
        not_frozen = dict(self.fixture.lifecycle)
        not_frozen["production_authority_freeze_status"] = "NOT_FROZEN"
        self.assertRejected(
            self.fixture.lawful_payload(),
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
            lifecycle=not_frozen,
        )

    def test_n21_accepted_lifecycle_invalid_or_absent(self) -> None:
        for label, lifecycle in (
            ("omitted", None),
            ("absent", lc.absent_lifecycle()),
            ("single_optimistic_field", {"production_authority_freeze_status": "FROZEN"}),
            ("incomplete_roles", {**self.fixture.lifecycle, "satisfied_roles": {}}),
            ("self_accepted", {**self.fixture.lifecycle, "self_accepted": True}),
            (
                "overreaching",
                {**self.fixture.lifecycle, "authorizes_main_full81": True},
            ),
        ):
            with self.subTest(lifecycle=label):
                self.assertRejected(
                    self.fixture.lawful_payload(),
                    "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
                    lifecycle=lifecycle,
                )

    def test_n21b_wrong_u06_lineage_or_record(self) -> None:
        self.assertRejected(
            self.mutated(u06_lineage_id="U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R2"),
            "FULL81_AUTHORIZATION_U06_BINDING_INVALID",
        )
        payload = self.mutated()
        payload["u06_accepted_lifecycle_record"]["path"] = (
            "results/provenance/elsewhere/accepted_lifecycle_record.json"
        )
        self.assertRejected(payload, "FULL81_AUTHORIZATION_U06_BINDING_INVALID")
        wrong_hash = self.mutated()
        wrong_hash["u06_accepted_lifecycle_record"]["sha256"] = "e" * 64
        self.assertRejected(wrong_hash, "FULL81_AUTHORIZATION_U06_BINDING_INVALID")

    def test_n24_stale_predecessor_authorization(self) -> None:
        """An authorization bound to the predecessor implementation is stale."""

        predecessor = (
            "b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a"
        )
        self.assertNotEqual(self.fixture.live_digest, predecessor)
        self.assertRejected(
            self.mutated(implementation_identity_digest=predecessor),
            "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        )

    def test_n25_historical_v7_2_authorization_is_not_current_authority(self) -> None:
        blob = subprocess.run(
            ["git", "cat-file", "blob", f"{HISTORICAL_V7_2_TAG}^{{}}:{HISTORICAL_V7_2_MANIFEST}"],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if blob.returncode != 0:
            self.skipTest("historical V7.2 manifest is not reachable in this clone")
        historical = json.loads(blob.stdout.decode("utf-8"))
        self.assertEqual(
            hashlib.sha256(blob.stdout).hexdigest(),
            "4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9",
        )
        # Attack 1: the real historical manifest, presented as an authorization.
        self.assertRejected(
            historical, "FULL81_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH"
        )
        # Attack 2: its lineage label, carried into a correctly shaped envelope.
        self.assertRejected(
            self.mutated(lineage_id=historical["authority_manifest_version"]),
            "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
        )
        # Attack 3: its own path nominated as the lawful authorization path.
        for path in auth.REJECTED_HISTORICAL_AUTHORIZATION_PATHS:
            with self.subTest(path=path):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.validate_authorization_payload(
                        self.fixture.root,
                        self.fixture.lawful_payload(),
                        record_relative=path,
                        lifecycle=self.fixture.lifecycle,
                    )
                self.assertEqual(
                    caught.exception.status,
                    "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
                )
        # Attack 4: the historical v7_1 routing input.
        self.assertEqual(
            historical["routing"]["annual_input_consumed"],
            "data/processed/annual_input_v7_1.parquet",
        )
        self.assertNotEqual(
            historical["routing"]["annual_input_consumed"],
            auth.EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
        )

    def test_n26_arbitrary_ancestor_is_not_publication_proof(self) -> None:
        """A real ancestor that never contained the record proves nothing."""

        payload = self.mutated(u06_publication_commit=self.fixture.commit_pre)
        self.assertRejected(
            payload, "FULL81_AUTHORIZATION_PUBLICATION_PROOF_INVALID"
        )
        for bad in ("", "HEAD", "deadbeef", "z" * 40):
            with self.subTest(commit=bad):
                self.assertRejected(
                    self.mutated(u06_publication_commit=bad),
                    "FULL81_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
                )

    def test_n27_authorization_broadening_to_unrelated_scopes(self) -> None:
        for field, value, status in (
            ("authorizes", ["MAIN_FULL81_EXECUTION"], "FULL81_AUTHORIZATION_SCOPE_BROADENED"),
            ("authorizes", [], "FULL81_AUTHORIZATION_SCOPE_BROADENED"),
            (
                "authorizes_optimize_calls",
                True,
                "FULL81_AUTHORIZATION_SCOPE_BROADENED",
            ),
            (
                "authorizes_full81_execution",
                True,
                "FULL81_AUTHORIZATION_SCOPE_BROADENED",
            ),
            (
                "requires_no_solve_preflight_before_execution",
                False,
                "FULL81_AUTHORIZATION_SCOPE_BROADENED",
            ),
            (
                "authorization_scope",
                "MAIN_FULL81_AND_PERFECT_INFORMATION",
                "FULL81_AUTHORIZATION_SCOPE_MISMATCH",
            ),
            (
                "restart_policy",
                "RESUME_PARTIAL",
                "FULL81_AUTHORIZATION_RESTART_POLICY_INVALID",
            ),
            (
                "solver_parameter_fingerprint",
                "f" * 64,
                "FULL81_AUTHORIZATION_SOLVER_FINGERPRINT_MISMATCH",
            ),
            (
                "u_01_blocks_main_full81",
                True,
                "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
            ),
            (
                "u_01_status",
                "RESOLVED",
                "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
            ),
            (
                "u_01_must_be_frozen_before",
                ["A2_EXECUTION"],
                "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
            ),
        ):
            with self.subTest(field=field, value=value):
                self.assertRejected(self.mutated(**{field: value}), status)

    def test_missing_required_fields_are_rejected(self) -> None:
        for field in auth.AUTHORIZATION_REQUIRED_FIELDS:
            if field in ("artifact_type", "schema_version"):
                continue  # checked before the completeness sweep
            payload = copy.deepcopy(self.fixture.lawful_payload())
            payload.pop(field)
            with self.subTest(missing=field):
                self.assertRejected(
                    payload, "FULL81_AUTHORIZATION_SCHEMA_INVALID"
                )


class RepositoryStateNegativeControlTests(unittest.TestCase):
    """N-01, N-02, N-22, N-23 — repository-state rejections."""

    def test_n01_no_authorization_artifact(self) -> None:
        fixture = _Fixture(publish_authorization=False)
        try:
            (fixture.root / fixture.record_relative).unlink()
            resolved = fixture.resolve()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertEqual(resolved["authorization_overlay"], "ABSENT")
            self.assertFalse(resolved["record_present"])
            self.assertFalse(
                auth.is_authorized_for_preflight(fixture.root, resolved)
            )
        finally:
            fixture.dispose()

    def test_n02_malformed_json(self) -> None:
        fixture = _Fixture(publish_authorization=False)
        try:
            fixture.write_authorization("{ this is not json")
            fixture.publish()
            resolved = fixture.resolve()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertEqual(resolved["authorization_overlay"], "PRESENT_INVALID")
            self.assertIn("not readable JSON", resolved["authorization_blocked_reason"])
        finally:
            fixture.dispose()

    def test_n22_unpublished_authorization(self) -> None:
        for label, mutate in (
            ("untracked", lambda f: None),
            (
                "committed_but_upstream_behind",
                lambda f: (
                    _git_ok(f.root, "add", "-A"),
                    _git_ok(f.root, "commit", "--quiet", "-m", "local only"),
                ),
            ),
        ):
            fixture = _Fixture(publish_authorization=False)
            try:
                mutate(fixture)
                resolved = fixture.resolve()
                with self.subTest(case=label):
                    self.assertEqual(
                        resolved["full81_authorization_status"], "NOT_GRANTED"
                    )
                    self.assertFalse(
                        auth.is_authorized_for_preflight(fixture.root, resolved)
                    )
            finally:
                fixture.dispose()

    def test_n23_dirty_authorization(self) -> None:
        fixture = _Fixture()
        try:
            self.assertEqual(
                fixture.resolve()["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            payload = fixture.lawful_payload()
            payload["note"] = "edited after publication"
            fixture.write_authorization(payload)
            resolved = fixture.resolve()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertEqual(resolved["authorization_overlay"], "PRESENT_INVALID")
            self.assertIn("modified relative to HEAD", resolved["authorization_blocked_reason"])
        finally:
            fixture.dispose()

    def test_n24b_published_authorization_dies_on_live_code_drift(self) -> None:
        """A committed, clean, pushed code change revokes the authorization."""

        fixture = _Fixture()
        try:
            self.assertTrue(
                auth.is_authorized_for_preflight(fixture.root, fixture.resolve())
            )
            drifted = fixture.root / "src/rainflow_validation_v7_2.py"
            drifted.write_text(
                drifted.read_text(encoding="utf-8") + "\n# post-authorization edit\n",
                encoding="utf-8",
                newline="\n",
            )
            _git_ok(fixture.root, "add", "-A")
            _git_ok(fixture.root, "commit", "--quiet", "-m", "post-auth code change")
            fixture.sync_upstream()
            resolved = fixture.resolve()
            self.assertEqual(resolved["full81_authorization_status"], "NOT_GRANTED")
            self.assertFalse(
                auth.is_authorized_for_preflight(fixture.root, resolved)
            )
        finally:
            fixture.dispose()


# ---------------------------------------------------------------------------
# Section 3 — the guards at the production boundary
# ---------------------------------------------------------------------------


class GuardSeparationTests(unittest.TestCase):
    """Authorization, preflight, execution, and A2 remain separate states."""

    def test_scope_guard_rejects_without_a_root(self) -> None:
        with self.assertRaises(bundle.Full81AuthorizationNotGranted) as caught:
            bundle.require_full81_scope_authorization("full81")
        self.assertEqual(caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED")

    def test_scope_guard_rejects_against_the_live_repository(self) -> None:
        with self.assertRaises(bundle.Full81AuthorizationNotGranted) as caught:
            bundle.require_full81_scope_authorization(
                "full81", root=ROOT, lifecycle=lc.resolve_u06_lifecycle(ROOT)
            )
        self.assertEqual(caught.exception.status, "FULL81_AUTHORIZATION_NOT_GRANTED")

    def test_non_full81_scopes_are_not_newly_restricted(self) -> None:
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
                bundle.require_full81_scope_authorization(scope, root=ROOT)

    def test_execution_interlock_always_rejects(self) -> None:
        fixture = _Fixture()
        try:
            resolved = fixture.resolve()
            self.assertEqual(
                resolved["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            for label, candidate in (
                ("absent", None),
                ("lawfully_authorized_for_preflight", resolved),
            ):
                with self.subTest(authorization=label):
                    with self.assertRaises(auth.Full81AuthorizationError) as caught:
                        auth.require_full81_execution_authorization(candidate)
                    self.assertEqual(
                        caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED"
                    )
        finally:
            fixture.dispose()

    def test_live_production_gate_rejects_full81_and_a2(self) -> None:
        snapshot = stack.inspect_deployment_snapshot(ROOT)
        self.assertEqual(
            snapshot.full81_authorization["full81_authorization_status"],
            "NOT_GRANTED",
        )
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

    def test_authorization_is_reported_separately_from_every_other_state(
        self,
    ) -> None:
        summary = auth.authorization_summary(None)
        self.assertEqual(summary["main_full81_authorization"], "NOT_GRANTED")
        self.assertFalse(summary["authorizes_optimize_calls"])
        self.assertFalse(summary["authorizes_full81_execution"])
        self.assertEqual(
            summary["execution_authorization"], "NOT_GRANTED_BY_THIS_MECHANISM"
        )
        self.assertEqual(
            list(auth.AUTHORIZATION_DISTINCTIONS),
            [
                "PRODUCTION_AUTHORITY_FROZEN",
                "MAIN_FULL81_AUTHORIZED",
                "FULL81_NO_SOLVE_PREFLIGHT_PASS",
                "FULL81_EXECUTION_AUTHORIZED",
                "FULL81_EXECUTED",
            ],
        )

    def test_resolver_writes_nothing_to_the_real_repository(self) -> None:
        before = _git_text(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
        auth.resolve_full81_authorization(ROOT, lc.resolve_u06_lifecycle(ROOT))
        auth.resolve_full81_authorization(ROOT, None)
        after = _git_text(ROOT, "status", "--porcelain=v1", "--untracked-files=all")
        self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# Section 4 — the positive control
# ---------------------------------------------------------------------------


class PositiveControlTests(unittest.TestCase):
    """A lawful authorization must reach exactly one state, and no further.

    Runs entirely inside an isolated throwaway Git repository. It performs zero
    optimization, zero annual MILP solves, zero Full81 cases, and zero A2 cases,
    and leaves no real production authorization artifact behind.
    """

    def test_lawful_authorization_reaches_preflight_authorization_only(self) -> None:
        fixture = _Fixture()
        try:
            resolved = fixture.resolve()
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
            self.assertEqual(resolved["implementation_identity_digest"], fixture.live_digest)
            self.assertEqual(
                resolved["target_runner"]["path"],
                auth.EXPECTED_RUNNER_RELATIVE_PATH,
            )
            self.assertEqual(
                resolved["target_runner"]["version"], auth.EXPECTED_RUNNER_VERSION
            )
            self.assertTrue(resolved["record_published"])
            self.assertFalse(resolved["self_authorized"])
            self.assertFalse(resolved["authorizes_optimize_calls"])
            self.assertFalse(resolved["authorizes_full81_execution"])
            self.assertTrue(resolved["a2_excluded"])
            self.assertIsNone(resolved["authorization_blocked_reason"])

            # The guard it unlocks, and the guard it does not.
            granted = auth.require_full81_preflight_authorization(
                fixture.root, resolved
            )
            self.assertEqual(
                granted["full81_authorization_status"],
                "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT",
            )
            self.assertTrue(
                auth.is_authorized_for_preflight(fixture.root, resolved)
            )
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(resolved)
            self.assertEqual(
                caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED"
            )
        finally:
            fixture.dispose()

    def test_positive_control_leaves_no_real_authorization_behind(self) -> None:
        self.assertFalse((ROOT / auth.AUTHORIZATION_RECORD_RELATIVE_PATH).exists())
        self.assertFalse(
            (ROOT / auth.AUTHORIZATION_RECORD_RELATIVE_PATH).parent.exists()
        )
        self.assertEqual(
            auth.resolve_full81_authorization(
                ROOT, lc.resolve_u06_lifecycle(ROOT)
            )["full81_authorization_status"],
            "NOT_GRANTED",
        )

    def test_the_guard_is_not_vacuous(self) -> None:
        """Proof the positive branch is reachable, so rejections mean something."""

        fixture = _Fixture()
        try:
            self.assertTrue(
                auth.is_authorized_for_preflight(fixture.root, fixture.resolve())
            )
        finally:
            fixture.dispose()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
