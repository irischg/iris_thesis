#!/usr/bin/env python3
"""R7-AUD-01: the RECOMPUTING adversary versus the external historical authority.

Candidate R7 received ``FAIL / NO-GO`` on ``R7-AUD-01`` (CRITICAL).  Its
production GATE took every historical role's expected value from
``HISTORICAL_ROLE_IDENTITIES``, a table in candidate source covered only by a
recomputable implementation identity.  Four independently constructed attacks
restored GATE PASS after every candidate-controlled identity was recomputed:

1. two historical roles swapped;
2. a three-role cyclic permutation;
3. one historical pin replaced with another lawful historical digest;
4. the authority-bundle digest substituted into a historical role.

Candidate R8 (contract V4) derives historical semantic truth from EXTERNAL,
pre-R8 evidence: the Git-frozen pre-R8 historical trust root -> the accepted R7
Preservation Authority Binding it pins -> the authenticated R7 preservation
package.  This suite attacks that with the strongest adversary the audit
described.  For every attack the adversary rewrites EVERY R8-controlled
artifact - the bundle's historical table (candidate source), the manifest, the
change ledger and every checkpoint claim - and RECOMPUTES every R8-controlled
identity: the implementation identity (paths and digest), the ledger's
candidate-side hashes, the ledger and checkpoint digests bound by the manifest.

Each attack runs the REAL production GATE in a separate interpreter whose
``src`` package is the adversary's rewritten copy, so the attacker's own source
is what executes.  Three facts are asserted per attack:

* the GATE result is FAIL with ``U06_EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH``,
  the status raised only where a candidate claim meets the external derivation;
* the identical attacked package reaches PASS when the probe substitutes R7's
  semantics (historical values read from the candidate table), so the package
  is complete and internally consistent - no stale hash exists for the GATE to
  find - and the external authority is the only thing refusing it;
* a semantically null rewrite run through the same recomputation reaches PASS
  under the real GATE, so the recomputation itself never leaves a stale hash.

The trust-root, binding and package controls then prove the chain fails closed
when any external link is missing, altered, redirected or substituted, and
that nothing falls back to candidate-controlled material.

ZERO SOLVE.  No production model is constructed, no ``optimize()`` is
reachable, no case runs, nothing is staged or committed, and the source
repository is only read.  Every fixture is a disposable copy built and torn
down through the R6-AUD-02 containment primitive; its Git object store is the
source repository's, shared READ-ONLY through ``objects/info/alternates``, so
no Git object is ever written.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402
from tests.test_21j_authority_raw_byte_eol_coverage import (  # noqa: E402
    _DisposableCandidateRoot,
    _DisposableExternalAuthorityRoot,
    _encode,
)

GEN = lc.CURRENT_GENERATION
R2_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2"
R3_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3"
R5_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5"
R6_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6"
R7_ID = lc.R7_CANDIDATE_ID
BUNDLE_REL = "src/production_authority_bundle_v7_4.py"
FROZEN = bundle.PRE_R8_HISTORICAL_TRUST_ROOT
TAG_NAME = FROZEN.tag_ref.removeprefix("refs/tags/")
FAILED_SELECTOR = (
    "results/provenance/"
    "main_full81_preflight_guard_r7_preservation_binding_runtime_selection_authority_2026-10-06/"
    "r7_preservation_binding_runtime_selection_authority.json"
)

MISMATCH = lc.EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH
UNAVAILABLE = lc.EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE
EVIDENCE = lc.EXTERNAL_HISTORICAL_EVIDENCE_INVALID
TRUST_ROOT = lc.TRUST_ROOT_GIT_AUTHORITY_INVALID

#: The real GATE, run in a fresh interpreter whose ``src`` is the FIXTURE's own
#: (possibly adversary-rewritten) source.  ``R7_SEMANTICS`` replaces the two
#: external-authority methods with R7's behaviour - historical values read from
#: the candidate table - and is used ONLY to prove an attacked package is
#: internally consistent.  It is never a production path.
GATE_PROBE = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
import src.production_authority_lifecycle_u06 as lc
import src.production_authority_bundle_v7_4 as bundle
for module in (lc, bundle):
    if not Path(module.__file__).resolve().is_relative_to(root):
        raise SystemExit(f"probe imported {module.__file__} from outside the fixture")
if sys.argv[2] == "R7_SEMANTICS":
    prefix = lc.PREDECESSOR_MODIFIED_FILE_ROLE_PREFIX
    def local_roles(self):
        return lc.historical_role_identities(label=self.label)
    def local_change_set(self):
        return {
            role[len(prefix):]: entry[1]
            for role, entry in lc.historical_role_identities(label=self.label).items()
            if role.startswith(prefix)
        }
    lc._RoleBinding.historical_roles = local_roles
    lc._RoleBinding.predecessor_change_set = local_change_set
try:
    report = lc.validate_candidate_manifest_identity_contract(
        root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE
    )
except lc.U06LifecycleError as exc:
    print(json.dumps({"result": "FAIL", "status": exc.status, "message": str(exc)}))
else:
    print(json.dumps({
        "result": "PASS",
        "role_bound": report["role_bound_identity_count"],
        "collected": report["collected_identity_count"],
        "module": str(Path(lc.__file__).resolve()),
    }))
'''


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_gate(root: Path, semantics: str = "V4") -> dict:
    """Run the production GATE in a separate, isolated interpreter."""

    done = subprocess.run(
        [sys.executable, "-I", "-B", "-c", GATE_PROBE, str(root), semantics],
        cwd=root,
        capture_output=True,
        check=False,
        timeout=900,
    )
    lines = done.stdout.decode("utf-8", "replace").strip().splitlines()
    if done.returncode != 0 or not lines:
        raise AssertionError(
            f"GATE probe crashed (rc={done.returncode}): "
            f"{done.stderr.decode('utf-8', 'replace')[-2000:]}"
        )
    return json.loads(lines[-1])


def gate_in_process(root: Path, mode: str = lc.CANDIDATE_MANIFEST_MODE_GATE) -> str:
    """The production validator in this process, against ``root``."""

    try:
        lc.validate_candidate_manifest_identity_contract(root, mode=mode)
    except lc.U06LifecycleError as exc:
        return exc.status
    return "PASS"


# ---------------------------------------------------------------------------
# The recomputing adversary
# ---------------------------------------------------------------------------


def manifest_role_pointers(manifest: dict) -> dict[tuple, str]:
    """Every historical identity pointer of the manifest -> its role."""

    out: dict[tuple, str] = {}
    for candidate in manifest["candidate_preservation_packages"]:
        for field in lc.HISTORICAL_ROLE_PRESERVATION_FIELDS:
            out[("candidate_preservation_packages", candidate, f"{field}_sha256")] = (
                lc.preservation_role(candidate, field)
            )
    out[("implementation_identity", "predecessor_digest")] = (
        lc.PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST
    )
    defect = ("package_binding", "predecessor_defect")
    out[defect + ("predecessor_candidate_checkpoint", "raw_sha256")] = lc.PREDECESSOR_ROLE_CHECKPOINT
    out[defect + ("predecessor_candidate_manifest", "raw_sha256")] = lc.PREDECESSOR_ROLE_MANIFEST
    return out


def ledger_role_pointers(ledger: dict) -> dict[tuple, str]:
    """Every historical identity pointer of the change ledger -> its role."""

    base = ("predecessor", "preserved_identity")
    out: dict[tuple, str] = {
        base + ("implementation_digest",): lc.PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST,
        base + ("checkpoint", "raw_sha256"): lc.PREDECESSOR_ROLE_CHECKPOINT,
        base + ("manifest", "raw_sha256"): lc.PREDECESSOR_ROLE_MANIFEST,
        base + ("repository_eol_policy", "raw_sha256"): lc.PREDECESSOR_ROLE_EOL_POLICY,
    }
    for field in lc.HISTORICAL_ROLE_PRESERVATION_FIELDS:
        out[base + ("stop_package", f"{field}_sha256")] = lc.preservation_role(R7_ID, field)
    for index, entry in enumerate(ledger["modified_files"]):
        out[("modified_files", index, "predecessor_raw_sha256")] = (
            lc.predecessor_modified_file_role(entry["path"])
        )
    return out


def _set(payload: dict, pointer: tuple, value: str) -> None:
    node = payload
    for token in pointer[:-1]:
        node = node[token]
    node[pointer[-1]] = value


def _get(payload: dict, pointer: tuple):
    node = payload
    for token in pointer:
        node = node[token]
    return node


class Adversary:
    """Rewrites every R8-controlled artifact and recomputes every R8 hash."""

    def __init__(self, fixture: _DisposableExternalAuthorityRoot) -> None:
        self.fixture = fixture
        self.root = fixture.dir

    def read(self, relative: str) -> bytes:
        return (self.root / relative).read_bytes()

    def rewrite_table(self, values: dict[str, str], *, extra_line: str = "") -> None:
        """Rewrite the bundle's historical table IN CANDIDATE SOURCE."""

        text = self.read(BUNDLE_REL).decode("utf-8")
        for role, digest in values.items():
            pattern = re.compile(
                r'(    HistoricalRoleIdentity\(\n        "'
                + re.escape(role)
                + r'",\n        (?:None|"[^"\n]*"),\n        ")[0-9a-f]{64}(")'
            )
            text, count = pattern.subn(lambda m: m.group(1) + digest + m.group(2), text)
            if count != 1:
                raise AssertionError(f"table role {role!r} matched {count} times")
        self.fixture.contained_write(BUNDLE_REL, (text + extra_line).encode("utf-8"))

    def reassign(self, values: dict[str, str], *, rewrite_table: bool, extra_line: str = "") -> None:
        """Give each historical ROLE in ``values`` a new digest EVERYWHERE, then
        recompute every candidate-controlled identity so nothing is stale."""

        if rewrite_table or extra_line:
            self.rewrite_table(values if rewrite_table else {}, extra_line=extra_line)
        manifest = json.loads(self.read(GEN.candidate_manifest_path))
        ledger = json.loads(self.read(GEN.candidate_change_ledger_path))
        for pointer, role in manifest_role_pointers(manifest).items():
            if role in values:
                _set(manifest, pointer, values[role])
        for pointer, role in ledger_role_pointers(ledger).items():
            if role in values:
                _set(ledger, pointer, values[role])
        # Recompute the implementation identity from the (rewritten) bytes.
        identity = {
            relative: _sha(self.read(relative)) for relative in lc.ACCEPTED_IMPLEMENTATION_PATHS
        }
        digest = lc.canonical_identity_digest(identity)
        manifest["implementation_identity"]["paths"] = dict(sorted(identity.items()))
        manifest["implementation_identity"]["implementation_digest"] = digest
        manifest["implementation_identity_digest"] = digest
        ledger["implementation_identity"]["paths"] = dict(sorted(identity.items()))
        ledger["implementation_identity"]["digest"] = digest
        for entry in ledger["modified_files"]:
            entry["candidate_raw_sha256"] = _sha(self.read(entry["path"]))
        # Ledger -> manifest binding.
        ledger_bytes = _encode(ledger)
        manifest["candidate_change_ledger"]["sha256"] = self.fixture.contained_write(
            GEN.candidate_change_ledger_path, ledger_bytes
        )
        # Every checkpoint claim rebound to the rewritten manifest's value.
        lines = self.read(GEN.candidate_checkpoint_path).decode("utf-8").split("\n")
        claim = re.compile(r"^(/\S*) [0-9a-f]{64}$")
        for number, line in enumerate(lines):
            match = claim.match(line)
            if match:
                pointer = lc.parse_rfc6901_pointer(match.group(1))
                lines[number] = f"{match.group(1)} {_get(manifest, pointer)}"
        checkpoint_bytes = "\n".join(lines).encode("utf-8")
        manifest["candidate_checkpoint"]["sha256"] = self.fixture.contained_write(
            GEN.candidate_checkpoint_path, checkpoint_bytes
        )
        self.fixture.contained_write(GEN.candidate_manifest_path, _encode(manifest))


# ---------------------------------------------------------------------------
# The four R7-AUD-01 attacks, reproduced against Candidate R8
# ---------------------------------------------------------------------------


class RecomputingAdversaryAttackTests(unittest.TestCase):
    """All four attacks, each with every R8-controlled hash recomputed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.roles = lc.resolve_external_historical_authority(ROOT)["roles"]
        cls.lawful_manifest = json.loads((ROOT / GEN.candidate_manifest_path).read_bytes())

    def value(self, role: str) -> str:
        return self.roles[role][1]

    def attacks(self) -> dict[str, dict[str, str]]:
        archive = lc.preservation_role(R5_ID, "archive")
        index = lc.preservation_role(R5_ID, "index")
        cycle = [lc.preservation_role(R7_ID, f) for f in ("archive", "index", "stop_record")]
        return {
            # 1. two lawful historical identities exchanged between roles.
            "1_two_role_swap": {archive: self.value(index), index: self.value(archive)},
            # 2. three lawful identities cycled among roles (the immediate
            #    predecessor's package: manifest, ledger, claims and table).
            "2_three_role_cycle": {
                cycle[0]: self.value(cycle[1]),
                cycle[1]: self.value(cycle[2]),
                cycle[2]: self.value(cycle[0]),
            },
            # 3. one role given another historical role's lawful digest.
            "3_lawful_historical_substitution": {
                lc.preservation_role(R3_ID, "stop_record"): self.value(
                    lc.preservation_role(R2_ID, "stop_record")
                ),
            },
            # 4. the authority-bundle digest placed in a historical role.
            "4_authority_bundle_digest_substitution": {
                lc.PREDECESSOR_ROLE_MANIFEST: self.lawful_manifest["implementation_identity"][
                    "paths"
                ][BUNDLE_REL],
            },
        }

    def test_the_null_recomputation_reaches_pass(self) -> None:
        """Control: the adversary's recomputation never leaves a stale hash.

        A semantically null rewrite of the candidate source (a comment line in
        the bundle) changes the implementation identity, and the adversary
        recomputes everything.  The real GATE must reach PASS, so any FAIL
        below is caused by the attack's semantics, not by a stale hash.
        """

        with _DisposableExternalAuthorityRoot() as fixture:
            Adversary(fixture).reassign(
                {}, rewrite_table=False, extra_line="# semantically null adversary edit\n"
            )
            self.assertNotEqual(
                _sha((fixture.dir / BUNDLE_REL).read_bytes()), _sha((ROOT / BUNDLE_REL).read_bytes())
            )
            outcome = run_gate(fixture.dir)
            self.assertEqual(outcome["result"], "PASS", outcome)
            self.assertEqual(outcome["role_bound"], outcome["collected"])

    def test_each_recomputed_wrong_role_attack_fails_on_external_authority(self) -> None:
        for label, values in self.attacks().items():
            for distinct in values.values():
                self.assertRegex(distinct, r"^[0-9a-f]{64}$")
            self.assertTrue(
                any(self.value(role) != digest for role, digest in values.items()), label
            )
            for variant, rewrite_table in (("table_rewritten", True), ("table_untouched", False)):
                with self.subTest(attack=label, variant=variant):
                    with _DisposableExternalAuthorityRoot() as fixture:
                        Adversary(fixture).reassign(values, rewrite_table=rewrite_table)
                        outcome = run_gate(fixture.dir)
                        self.assertEqual(outcome["result"], "FAIL", outcome)
                        self.assertEqual(outcome["status"], MISMATCH, outcome)
                        self.assertIn("externally", outcome["message"])
                        if rewrite_table:
                            # The SAME attacked package passes a GATE that trusts
                            # the candidate table (R7 semantics): it is complete
                            # and consistent, so only the external authority
                            # refuses it - not a stale candidate hash.
                            r7 = run_gate(fixture.dir, "R7_SEMANTICS")
                            self.assertEqual(r7["result"], "PASS", r7)


# ---------------------------------------------------------------------------
# The external chain fails closed, and nothing falls back
# ---------------------------------------------------------------------------


class ExternalAuthorityChainTests(unittest.TestCase):
    """Trust root, binding and package: every link is required and exact."""

    def test_lawful_chain_reaches_pass_in_the_real_gate(self) -> None:
        with _DisposableExternalAuthorityRoot() as fixture:
            self.assertFalse((fixture.dir / FAILED_SELECTOR).exists())
            outcome = run_gate(fixture.dir)
            self.assertEqual(outcome["result"], "PASS", outcome)
            self.assertEqual(outcome["role_bound"], outcome["collected"])
            for mode in lc.CANDIDATE_MANIFEST_MODES:
                with self.subTest(mode=mode):
                    self.assertEqual(gate_in_process(fixture.dir, mode), "PASS")

    def test_live_repository_resolves_the_frozen_chain(self) -> None:
        authority = lc.resolve_external_historical_authority(ROOT)
        trust = authority["trust_root"]
        self.assertEqual(trust["tag_ref"], FROZEN.tag_ref)
        self.assertEqual(trust["tag_object"], FROZEN.tag_object)
        self.assertEqual(trust["commit"], FROZEN.commit)
        self.assertEqual(trust["blob"], FROZEN.blob)
        # The binding locator and SHA are read from the frozen Git blob.
        blob = json.loads(
            subprocess.run(
                ["git", "cat-file", "blob", FROZEN.blob], cwd=ROOT, capture_output=True, check=True
            ).stdout
        )
        self.assertEqual(authority["binding"]["path"], blob["canonical_r7_binding"]["locator"])
        self.assertEqual(authority["binding"]["sha256"], blob["canonical_r7_binding"]["sha256"])
        self.assertEqual(
            _sha((ROOT / authority["binding"]["path"]).read_bytes()), authority["binding"]["sha256"]
        )
        self.assertEqual(
            sorted(authority["preservation_packages"]),
            sorted(lc.CANDIDATE_PRESERVATION_PACKAGES),
        )
        self.assertEqual(len(authority["roles"]), 3 * 7 + 4)
        # The failed selector is never a link of the chain.
        self.assertNotIn(FAILED_SELECTOR, json.dumps(authority))

    def assert_gate(self, mutate, status: str, *, probe: bool = False) -> None:
        with _DisposableExternalAuthorityRoot() as fixture:
            mutate(fixture)
            if probe:
                outcome = run_gate(fixture.dir)
                self.assertEqual(outcome["result"], "FAIL", outcome)
                self.assertEqual(outcome["status"], status, outcome)
            else:
                self.assertEqual(gate_in_process(fixture.dir), status)

    # -- the Git-frozen trust root ------------------------------------------------

    def test_trust_root_git_authority_mismatches_fail_closed(self) -> None:
        tag_ref = f".git/refs/tags/{TAG_NAME}"
        other_tag = subprocess.run(
            ["git", "rev-parse", "v7.3-step2d-r3-accepted-2026-09-24"],
            cwd=ROOT, capture_output=True, check=True,
        ).stdout.strip() + b"\n"
        parent = subprocess.run(
            ["git", "rev-parse", f"{FROZEN.commit}^"], cwd=ROOT, capture_output=True, check=True
        ).stdout.strip() + b"\n"
        self.assertTrue((ROOT / tag_ref).is_file())

        def tag_deleted(fx):
            fx.contained_unlink(tag_ref)

        def tag_moved(fx):
            fx.contained_write(tag_ref, other_tag)

        def head_before_freeze(fx):
            fx.contained_write(".git/HEAD", parent)

        def upstream_before_freeze(fx):
            fx.contained_write(".git/refs/remotes/origin/thesis-v7", parent)

        def working_copy_altered(fx):
            fx.contained_write(FROZEN.path, (ROOT / FROZEN.path).read_bytes() + b" ")

        for label, mutate in (
            ("tag_deleted", tag_deleted),
            ("tag_moved_to_another_lawful_tag", tag_moved),
            ("head_before_the_freeze", head_before_freeze),
            ("upstream_before_the_freeze", upstream_before_freeze),
            ("working_copy_altered", working_copy_altered),
        ):
            with self.subTest(attack=label):
                self.assert_gate(mutate, TRUST_ROOT)

    def test_redirecting_the_trust_root_to_another_lawful_ref_fails(self) -> None:
        """The adversary repoints the CONSUMED frozen identity, in candidate
        source, at another lawful published tag and a lawful tracked artifact
        with its true blob and SHA-256.  It is not the trust root, so the chain
        refuses it."""

        tag = "v7.3-step2d-r3-accepted-2026-09-24"
        path = "docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.json"

        def git(*args):
            return subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, check=True
            ).stdout.strip().decode()

        commit = git("rev-parse", f"{tag}^{{commit}}")
        blob = git("rev-parse", f"{commit}:{path}")
        data = subprocess.run(
            ["git", "cat-file", "blob", blob], cwd=ROOT, capture_output=True, check=True
        ).stdout

        def redirect(fx):
            text = (fx.dir / BUNDLE_REL).read_bytes().decode("utf-8")
            for old, new in (
                (FROZEN.tag_ref, f"refs/tags/{tag}"),
                (FROZEN.tag_object, git("rev-parse", tag)),
                (FROZEN.commit, commit),
                (FROZEN.path, path),
                (FROZEN.blob, blob),
                (FROZEN.raw_sha256, _sha(data)),
                (f"byte_count={FROZEN.byte_count}", f"byte_count={len(data)}"),
            ):
                self.assertEqual(text.count(old), 1, old)
                text = text.replace(old, new)
            fx.contained_write(BUNDLE_REL, text.encode("utf-8"))
            fx.contained_copy_in(ROOT / path, path)
            Adversary(fx).reassign({}, rewrite_table=False)

        self.assert_gate(redirect, EVIDENCE, probe=True)

    # -- the accepted R7 binding ---------------------------------------------------

    def test_binding_absent_altered_or_substituted_fails_closed(self) -> None:
        binding = lc.resolve_external_historical_authority(ROOT)["binding"]["path"]
        stop_record = (
            f"{lc.CANDIDATE_PRESERVATION_PACKAGES[R7_ID]['directory']}/"
            f"{lc.CANDIDATE_PRESERVATION_PACKAGES[R7_ID]['stop_record']}"
        )

        def absent(fx):
            fx.contained_unlink(binding)

        def altered(fx):
            raw = bytearray((ROOT / binding).read_bytes())
            raw[-2] = ord("x") if raw[-2] != ord("x") else ord("y")
            fx.contained_write(binding, bytes(raw))

        def another_lawful_artifact(fx):
            fx.contained_write(binding, (ROOT / stop_record).read_bytes())

        def the_failed_selector(fx):
            fx.contained_write(binding, (ROOT / FAILED_SELECTOR).read_bytes())

        def byte_identical_copy_elsewhere_only(fx):
            fx.contained_write(
                "results/provenance/alternate_binding/r7_preservation_authority_binding.json",
                (ROOT / binding).read_bytes(),
            )
            fx.contained_unlink(binding)

        for label, mutate, status in (
            ("binding_absent", absent, UNAVAILABLE),
            ("binding_altered", altered, EVIDENCE),
            ("binding_replaced_by_r7_stop_record", another_lawful_artifact, EVIDENCE),
            ("binding_replaced_by_failed_selector", the_failed_selector, EVIDENCE),
            ("alternate_copy_is_never_consulted", byte_identical_copy_elsewhere_only, UNAVAILABLE),
        ):
            with self.subTest(attack=label):
                self.assert_gate(mutate, status)

    # -- the authenticated R7 preservation package ---------------------------------

    def test_r7_package_absent_altered_or_substituted_fails_closed(self) -> None:
        package = lc.CANDIDATE_PRESERVATION_PACKAGES[R7_ID]
        r6 = lc.CANDIDATE_PRESERVATION_PACKAGES[R6_ID]
        rel = {f: f"{package['directory']}/{package[f]}" for f in ("archive", "index", "stop_record")}

        def archive_absent(fx):
            fx.contained_unlink(rel["archive"])

        def index_altered(fx):
            fx.contained_write(rel["index"], (ROOT / rel["index"]).read_bytes() + b"\n")

        def stop_record_from_r6(fx):
            fx.contained_write(
                rel["stop_record"],
                (ROOT / f"{r6['directory']}/{r6['stop_record']}").read_bytes(),
            )

        for label, mutate, status in (
            ("r7_archive_absent", archive_absent, UNAVAILABLE),
            ("r7_index_altered", index_altered, EVIDENCE),
            ("r7_stop_record_replaced_by_r6", stop_record_from_r6, EVIDENCE),
        ):
            with self.subTest(attack=label):
                self.assert_gate(mutate, status)

    # -- no candidate-local fallback, no redirection surface -----------------------

    def test_no_candidate_local_fallback_exists(self) -> None:
        # A lawful package and an intact, lawful candidate table, but no external
        # evidence: the GATE fails closed; it never falls back to the table.
        with _DisposableCandidateRoot() as clean:
            self.assertIn(gate_in_process(clean.dir), {TRUST_ROOT, UNAVAILABLE})
        with _DisposableExternalAuthorityRoot() as fixture:
            binding = lc.resolve_external_historical_authority(ROOT)["binding"]["path"]
            fixture.contained_unlink(binding)
            self.assertEqual(gate_in_process(fixture.dir), UNAVAILABLE)
            local = lc.historical_role_identities(label="fallback control")
            self.assertTrue(local)
        # The binding layer never reads a value from the candidate table.
        for method in (lc._RoleBinding.historical, lc._RoleBinding.historical_roles):
            source = inspect.getsource(method)
            self.assertNotIn("HISTORICAL_ROLE_IDENTITIES", source)
        self.assertIn("_require_local_table_agrees", inspect.getsource(lc._RoleBinding.historical_roles))

    def test_a_candidate_table_disagreeing_with_external_truth_fails(self) -> None:
        original = bundle.HISTORICAL_ROLE_IDENTITIES
        archive = lc.preservation_role(R5_ID, "archive")
        index = lc.preservation_role(R5_ID, "index")
        by_role = {e.role: e for e in original}
        swapped = tuple(
            bundle.HistoricalRoleIdentity(e.role, e.relative_path, by_role[index].sha256)
            if e.role == archive
            else bundle.HistoricalRoleIdentity(e.role, e.relative_path, by_role[archive].sha256)
            if e.role == index
            else e
            for e in original
        )
        try:
            for label, table in (
                ("swapped", swapped),
                ("role_removed", tuple(e for e in original if e.role != archive)),
                ("role_added", original + (
                    bundle.HistoricalRoleIdentity(
                        lc.predecessor_modified_file_role("scripts/08_calibrate_kappa.py"),
                        "scripts/08_calibrate_kappa.py",
                        "0" * 64,
                    ),
                )),
            ):
                bundle.HISTORICAL_ROLE_IDENTITIES = table  # type: ignore[assignment]
                with self.subTest(table=label):
                    self.assertEqual(gate_in_process(ROOT), MISMATCH)
        finally:
            bundle.HISTORICAL_ROLE_IDENTITIES = original  # type: ignore[assignment]
        self.assertEqual(gate_in_process(ROOT), "PASS")

    def test_no_caller_can_name_another_path_ref_or_binding(self) -> None:
        for function in (
            lc.authenticate_pre_r8_trust_root,
            lc.resolve_external_historical_authority,
        ):
            with self.subTest(function=function.__name__):
                self.assertEqual(list(inspect.signature(function).parameters), ["root"])
        parameters = inspect.signature(lc.validate_candidate_manifest_identity_contract).parameters
        for name in parameters:
            self.assertNotIn("binding", name)
            self.assertNotIn("trust", name)
            self.assertNotIn("authority", name)
        # The binding locator and SHA are not restated in candidate source.
        authority = lc.resolve_external_historical_authority(ROOT)
        for relative in (BUNDLE_REL, "src/production_authority_lifecycle_u06.py"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(source=relative):
                self.assertNotIn(authority["binding"]["sha256"], source)
                self.assertNotIn(authority["binding"]["path"].rsplit("/", 1)[-1], source)

    def test_declared_package_schema_must_equal_the_evidence(self) -> None:
        original = lc.CANDIDATE_PRESERVATION_PACKAGES
        renamed = {k: dict(v) for k, v in original.items()}
        renamed[R5_ID]["index"] = renamed[R5_ID]["archive"]
        try:
            lc.CANDIDATE_PRESERVATION_PACKAGES = renamed  # type: ignore[assignment]
            self.assertEqual(gate_in_process(ROOT), MISMATCH)
        finally:
            lc.CANDIDATE_PRESERVATION_PACKAGES = original  # type: ignore[assignment]
        self.assertEqual(gate_in_process(ROOT), "PASS")


class ZeroSolveTests(unittest.TestCase):
    def test_this_suite_constructs_no_model_and_calls_no_solver(self) -> None:
        """Zero-solve control on EXECUTABLE code (and the GATE probe), not prose."""

        trees = [
            ast.parse(Path(__file__).read_text(encoding="utf-8")),
            ast.parse(GATE_PROBE),
        ]
        imported: set[str] = set()
        called: set[str] = set()
        attributes: set[str] = set()
        for tree in trees:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
                elif isinstance(node, ast.Attribute):
                    attributes.add(node.attr)
                elif isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name):
                        called.add(func.id)
                    elif isinstance(func, ast.Attribute):
                        called.add(func.attr)
        for solver_module in ("gurobipy", "pyomo", "pulp"):
            self.assertNotIn(solver_module, imported)
        for solver_call in (
            "optimize",
            "Model",
            "run_layer_a_production",
            "build_annual_model",
            "run_annual_design_model",
        ):
            with self.subTest(symbol=solver_call):
                self.assertNotIn(solver_call, called)
                self.assertNotIn(solver_call, attributes)


if __name__ == "__main__":
    unittest.main()
