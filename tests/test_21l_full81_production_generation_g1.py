#!/usr/bin/env python3
"""Current Full81 Production Generation G1: generation, contract, phase, guard.

What this suite proves
----------------------
* G1 is the ONE current production-authority generation, with its own content
  contract, change ledger and predeclared governance paths, and the R8
  generation is an unchanged historical predecessor that can never authorise.
* The G1 candidate content contract is closed-world: every embedded identity is
  bound to one role whose value is established independently of the candidate
  artifacts, in both validation modes, and the validation generation is
  separated from the runtime generation exactly as the contract declares.
* The candidate phase is explicit and fail-closed: every future governance
  artifact is named, absence is reported, and absence never authorizes.
* The Main Full81 scope-authorization slot moved to G1 without touching the
  published R8-bound ``r3`` authorization.
* The G1 execution-authorization GUARD refuses everything in the real
  repository, refuses every malformed, stale or out-of-order chain, and grants
  only a complete lawful chain built in a DISPOSABLE repository.
* The raw-byte consumer universe is exactly covered by exact-path EOL rules.
* The three G1 identities are deterministic and their binding graph is acyclic.

Fixture discipline
------------------
Every positive control runs in a throwaway Git repository under the system temp
directory.  It shares the real object store READ-ONLY through ``alternates`` so
published history is genuinely in its ancestry; nothing is ever written to the
real repository.  No real lifecycle record, scope authorization, preflight
evidence or execution authorization is created.

ZERO SOLVE.  ``setUpModule`` replaces every real Gurobi entry point, no model is
constructed, no optimizer is called, and ``scripts/21d`` is never invoked.
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
from typing import Any, Mapping
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import main_full81_authorization_v7_4 as auth  # noqa: E402
from src import production_authority_bundle_v7_4 as bundle  # noqa: E402
from src import production_authority_lifecycle_u06 as lc  # noqa: E402


GEN = lc.CURRENT_GENERATION
R8_GEN = lc.GENERATIONS_BY_ID["MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1"]
AUTH_MECH_R2_GEN = lc.GENERATIONS_BY_ID["MAIN_FULL81_AUTHORIZATION_MECHANISM_R2"]
U06_R3_GEN = lc.GENERATIONS_BY_ID["U06_V7_4_PRODUCTION_AUTHORITY_R3"]
FIXTURE_PREFIX = "g1_fixture_"
FIXTURE_DATE = "2026-10-07"

_TRIPWIRE_PATCHES: list[Any] = []


class NativeSolverTripwire(RuntimeError):
    """Raised if any test in this module reaches a real native solver entry."""


def setUpModule() -> None:
    """Make real native solver entry structurally impossible for this module."""

    def _forbidden(name: str):
        def _raise(*args, **kwargs):
            raise NativeSolverTripwire(f"G1 suite reached native solver entry: {name}")

        return _raise

    try:
        import gurobipy as gp
    except Exception:  # pragma: no cover - gurobipy absent is already safe
        return
    for attribute in ("__init__", "optimize", "optimizeAsync", "optimizeBatch", "tune"):
        if hasattr(gp.Model, attribute):
            patcher = patch.object(gp.Model, attribute, _forbidden(attribute))
            patcher.start()
            _TRIPWIRE_PATCHES.append(patcher)


def tearDownModule() -> None:
    while _TRIPWIRE_PATCHES:
        _TRIPWIRE_PATCHES.pop().stop()


# ---------------------------------------------------------------------------
# Git and file helpers
# ---------------------------------------------------------------------------


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


def _json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# The G1 candidate-package builder (also used by tests 21g and 21h)
# ---------------------------------------------------------------------------


def g1_predecessor_commit() -> str:
    """The commit a G1 change ledger compares against.

    Once the real candidate ledger exists it records that commit; before it
    exists the predecessor is the repository HEAD the candidate is built on.
    Read, never restated: no commit is hard-coded in this suite.
    """

    ledger = ROOT / GEN.candidate_change_ledger_path
    if ledger.is_file():
        try:
            return json.loads(ledger.read_text(encoding="utf-8"))["predecessor"][
                "repository_head_commit"
            ]
        except Exception:
            pass
    return _git_text(ROOT, "rev-parse", "HEAD")


def g1_historical_evidence() -> list[dict[str, str]]:
    """Typed predecessor evidence, each proved by its blob in a published commit."""

    out: list[dict[str, str]] = []
    for role, path in sorted(lc.g1_historical_evidence_roles(GEN).items()):
        commit = lc.last_modifying_commit(ROOT, path)
        out.append(
            {
                "role": role,
                "path": path,
                "publication_commit": str(commit),
                "raw_sha256": str(lc.blob_sha256_at(ROOT, str(commit), path)),
                "evidence_class": lc.G1_HISTORICAL_EVIDENCE_CLASS,
            }
        )
    return out


def g1_publication_source(relative: str, candidate_sha: str) -> dict[str, str] | None:
    """Published evidence that ``relative`` was already authenticated, if any.

    The published R8 change ledger recorded the exact raw SHA-256 of every
    suite it executed.  A G1 path absent from the predecessor commit whose
    bytes equal such a record is published UNCHANGED, not created.
    """

    ledger_path = R8_GEN.candidate_change_ledger_path or ""
    commit = lc.last_modifying_commit(ROOT, ledger_path)
    if not commit:
        return None
    blob = _git(ROOT, "cat-file", "blob", f"{commit}:{ledger_path}")
    if blob.returncode != 0:
        return None
    for index, entry in enumerate(json.loads(blob.stdout).get("tests_executed", [])):
        if entry.get("suite") == relative and entry.get("raw_sha256") == candidate_sha:
            return {
                "evidence_path": ledger_path,
                "evidence_commit": commit,
                "evidence_pointer": f"/tests_executed/{index}/raw_sha256",
            }
    return None


def g1_membership(root: Path) -> dict[str, tuple[str, str]]:
    """Every G1 identity member -> (identity class, established raw SHA-256)."""

    out: dict[str, tuple[str, str]] = {}
    for relative, digest in lc.implementation_identity(root).items():
        out[relative] = (lc.G1_IDENTITY_CLASS_RUNTIME, digest)
    for relative, digest in lc.validation_identity_strict(root).items():
        out[relative] = (lc.G1_IDENTITY_CLASS_VALIDATION, digest)
    for relative, digest in lc.governance_authority_identity(root).items():
        out[relative] = (lc.G1_IDENTITY_CLASS_GOVERNANCE, digest)
    return out


def _role_labels() -> dict[str, str]:
    labels = {pin.relative_path: pin.label for pin in bundle.all_pins()}
    for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS:
        labels.setdefault(pin.relative_path, f"execution_input:{pin.label}")
    return labels


_DEFAULT_JUSTIFICATION = {
    lc.G1_IDENTITY_CLASS_RUNTIME: (
        "Member of G1_RUNTIME_IDENTITY: imported, loaded, executed or "
        "gate-protected on the Full81 production path."
    ),
    lc.G1_IDENTITY_CLASS_VALIDATION: (
        "Member of G1_VALIDATION_IDENTITY: an acceptance-critical validation "
        "suite of the G1 validation generation."
    ),
    lc.G1_IDENTITY_CLASS_GOVERNANCE: (
        "Member of G1_GOVERNANCE_AUTHORITY_IDENTITY: its exact bytes are pinned "
        "by the production-authority bundle or the FULLSTACK-01 execution-input "
        "authority."
    ),
}


def synthetic_tests_executed() -> list[dict[str, Any]]:
    return [
        {
            "suite": suite,
            "command": f"fixture: {suite}",
            "ran": 1,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "result": "OK",
        }
        for suite in lc.VALIDATION_IDENTITY_PATHS
    ]


def build_g1_ledger(
    root: Path,
    *,
    base_commit: str,
    tests_executed: list[dict[str, Any]],
    summaries: Mapping[str, str] | None = None,
    justifications: Mapping[str, str] | None = None,
    fullstack_reference: Mapping[str, Any] | None = None,
    known_inconsistency: str | None = None,
) -> dict[str, Any]:
    """A G1 change ledger for the live bytes under ``root``."""

    root = Path(root)
    members = g1_membership(root)
    surface = sorted(members)
    predecessor = lc._blob_sha256_map(root, base_commit, surface, label="G1 builder")
    labels = _role_labels()
    modified: list[dict[str, Any]] = []
    change_by_path: dict[str, str] = {}
    for relative in surface:
        live = members[relative][1]
        if predecessor[relative] == live:
            continue
        source = None
        if predecessor[relative] is None:
            source = g1_publication_source(relative, live)
            change = "PUBLISH_UNCHANGED" if source else "CREATE"
        else:
            change = "MODIFY"
        change_by_path[relative] = change
        modified.append(
            {
                "path": relative,
                "change_class": change,
                "predecessor_raw_sha256": predecessor[relative]
                or lc.G1_LEDGER_ABSENT_SENTINEL,
                "candidate_raw_sha256": live,
                "publication_source": source or lc.G1_LEDGER_NOT_APPLICABLE,
                "summary": (summaries or {}).get(
                    relative, f"{change} in the G1 candidate."
                ),
            }
        )
    live_roles = [
        {
            "role": labels.get(relative, f"{members[relative][0]}:{relative}"),
            "path": relative,
            "raw_sha256": members[relative][1],
            "identity_class": members[relative][0],
            "lifecycle_status": lc.G1_LIVE_ROLE_STATUS_BY_CHANGE[
                change_by_path.get(relative)
            ],
            "authority_justification": (justifications or {}).get(
                relative, _DEFAULT_JUSTIFICATION[members[relative][0]]
            ),
        }
        for relative in surface
    ]
    validation = {r: d for r, (c, d) in members.items() if c == lc.G1_IDENTITY_CLASS_VALIDATION}
    predecessor_gen = lc.GENERATIONS_BY_ID[str(GEN.predecessor_generation_id)]
    return {
        "schema_version": GEN.schema_prefix + lc.CANDIDATE_CHANGE_LEDGER_SCHEMA_SUFFIX,
        "artifact_type": GEN.artifact_type_prefix
        + lc.CANDIDATE_CHANGE_LEDGER_ARTIFACT_TYPE_SUFFIX,
        "ledger_semantics": lc.CANDIDATE_CHANGE_LEDGER_SEMANTICS,
        "generation_id": GEN.generation_id,
        "lineage_id": GEN.lineage_id,
        "candidate_id": GEN.candidate_id,
        "candidate_artifact_paths": {
            "checkpoint": GEN.candidate_checkpoint_path,
            "manifest": GEN.candidate_manifest_path,
            "change_ledger": GEN.candidate_change_ledger_path,
        },
        "predecessor": {
            "generation_id": predecessor_gen.generation_id,
            "lineage_id": predecessor_gen.lineage_id,
            "candidate_id": predecessor_gen.candidate_id,
            "relationship": lc.G1_PREDECESSOR_RELATIONSHIP,
            "repository_head_commit": base_commit,
            "historical_evidence": g1_historical_evidence(),
            "fullstack_01_reference": dict(fullstack_reference or {"note": "fixture"}),
            "known_historical_inconsistency": known_inconsistency
            or "Recorded in the candidate checkpoint.",
        },
        "modified_files": modified,
        "identity_digests": {
            "runtime": lc.canonical_identity_digest(lc.implementation_identity(root)),
            "validation": lc.canonical_identity_digest(validation),
            "governance_authority": lc.canonical_identity_digest(
                lc.governance_authority_identity(root)
            ),
        },
        "live_roles": live_roles,
        "tests_executed": [
            {**entry, "raw_sha256": validation[entry["suite"]]} for entry in tests_executed
        ],
        "execution_status": dict(lc.G1_EXECUTION_COUNTERS),
        "lifecycle_status": dict(lc.G1_CANDIDATE_LIFECYCLE_STATE),
    }


def build_g1_checkpoint_text(root: Path, *, ledger_sha: str, body: str | None = None) -> str:
    """A checkpoint whose ONLY raw identities are canonical claims."""

    root = Path(root)
    claims = {
        "/runtime_identity/digest": lc.implementation_identity_digest(root),
        "/validation_identity/digest": lc.validation_identity_digest(root),
        "/governance_authority_identity/digest": lc.governance_authority_identity_digest(root),
        "/candidate_change_ledger/sha256": ledger_sha,
    }
    lines = [f"{pointer} {digest}" for pointer, digest in claims.items()]
    return (
        (body or "# G1 candidate checkpoint (disposable fixture)\n\nSynthetic.\n")
        + "\n"
        + lc.CHECKPOINT_CLAIM_FENCE_OPEN
        + "\n"
        + "\n".join(lines)
        + "\n"
        + lc.CHECKPOINT_CLAIM_FENCE_CLOSE
        + "\n"
    )


def _identity_section(identity_class: str, paths: Mapping[str, str]) -> dict[str, Any]:
    return {
        "identity_class": identity_class,
        "path_count": len(paths),
        "digest_algorithm": lc.IMPLEMENTATION_DIGEST_ALGORITHM,
        "digest": lc.canonical_identity_digest(paths),
        "paths": dict(sorted(paths.items())),
    }


def build_g1_manifest(
    root: Path,
    *,
    checkpoint_sha: str,
    ledger_sha: str,
    head: str,
    date: str = FIXTURE_DATE,
    scope: str = "Disposable G1 fixture.",
    carried_findings: list[Any] | None = None,
    next_legal_gate: str = "FRESH_INDEPENDENT_READ_ONLY_AUDIT",
) -> dict[str, Any]:
    root = Path(root)
    contract = GEN.role_contracts["implementation_candidate"]
    pins = bundle.all_pins()
    durable_entries: dict[str, Any] = {}
    for relative in lc._required_durable_paths_for(GEN):
        if relative in lc.REQUIRED_DURABLE_PUBLICATION_PIN_LABELS:
            label = lc.REQUIRED_DURABLE_PUBLICATION_PIN_LABELS[relative]
            durable_entries[relative] = {
                "identity_source": lc.DURABLE_IDENTITY_SOURCE_PIN,
                "pin_label": label,
                "expected_raw_sha256": bundle._pin(label).sha256,
            }
        elif relative == GEN.candidate_checkpoint_path:
            durable_entries[relative] = {
                "identity_source": lc.DURABLE_IDENTITY_SOURCE_CHECKPOINT_FIELD,
                "identity_field": lc.DURABLE_CHECKPOINT_IDENTITY_FIELD,
            }
        elif relative == GEN.candidate_change_ledger_path:
            durable_entries[relative] = {
                "identity_source": lc.DURABLE_IDENTITY_SOURCE_LEDGER_FIELD,
                "identity_field": lc.DURABLE_LEDGER_IDENTITY_FIELD,
            }
        else:
            durable_entries[relative] = {
                "identity_source": lc.DURABLE_IDENTITY_SOURCE_EXTERNAL,
                "external_binding_fields": list(
                    lc.candidate_manifest_external_binding_fields(GEN)
                ),
            }
    register = lc.CANDIDATE_AUDIT_REGISTERS[GEN.generation_id][GEN.candidate_id]
    return {
        "schema_version": contract.schema_version,
        "artifact_type": contract.artifact_type,
        "role": "implementation_candidate",
        "candidate_manifest_contract": lc.G1_CANDIDATE_MANIFEST_CONTRACT,
        "date": date,
        "generation_id": GEN.generation_id,
        "lineage_id": GEN.lineage_id,
        "candidate_id": GEN.candidate_id,
        "target_candidate_id": GEN.candidate_id,
        "candidate_revision": GEN.candidate_id.rsplit("_", 1)[-1],
        "scope": scope,
        "disposition": register["disposition"],
        "self_accepted": False,
        "package_binding": {
            "scheme": lc.PACKAGE_BINDING_SCHEME,
            "direction": lc.PACKAGE_BINDING_DIRECTION,
            "manifest_self_identity": lc.DURABLE_IDENTITY_SOURCE_EXTERNAL,
            "rationale": (
                "The ledger is finalized first, then the checkpoint, then this "
                "manifest, which binds both; its own identity is bound only by "
                "later lifecycle role records."
            ),
        },
        "candidate_checkpoint_path": GEN.candidate_checkpoint_path,
        "candidate_checkpoint": {"path": GEN.candidate_checkpoint_path, "sha256": checkpoint_sha},
        "candidate_manifest_path": GEN.candidate_manifest_path,
        "candidate_change_ledger": {
            "path": GEN.candidate_change_ledger_path,
            "sha256": ledger_sha,
        },
        "accepted_lifecycle_record_path": GEN.accepted_lifecycle_record_path,
        "predecessor_generation": lc._g1_predecessor_constant(GEN),
        "implementation_identity_digest": lc.implementation_identity_digest(root),
        "runtime_identity": _identity_section(
            lc.G1_IDENTITY_CLASS_RUNTIME, lc.implementation_identity(root)
        ),
        "validation_identity": _identity_section(
            lc.G1_IDENTITY_CLASS_VALIDATION, lc.validation_identity_strict(root)
        ),
        "governance_authority_identity": _identity_section(
            lc.G1_IDENTITY_CLASS_GOVERNANCE, lc.governance_authority_identity(root)
        ),
        "intentional_runtime_validation_coupling": (
            lc.g1_intentional_runtime_validation_coupling()
        ),
        "authority_bundle": {
            "declared_pin_groups": len(bundle.PIN_GROUPS),
            "declared_pin_count": len(pins),
            "pins": {pin.label: {"path": pin.relative_path, "sha256": pin.sha256} for pin in pins},
        },
        "durable_publication_declaration": {
            "semantics": lc.DURABLE_DECLARATION_SEMANTICS,
            "live_status_source": lc.DURABLE_DECLARATION_LIVE_STATUS_SOURCE,
            "required_paths": list(lc._required_durable_paths_for(GEN)),
            "entries": durable_entries,
        },
        "predeclared_governance_paths": lc.g1_predeclared_governance_paths(GEN),
        "lifecycle_state": dict(lc.G1_CANDIDATE_LIFECYCLE_STATE),
        "execution_counters": dict(lc.G1_EXECUTION_COUNTERS),
        "repository_head_at_authoring": head,
        "carried_findings": list(carried_findings or []),
        "next_legal_gate": next_legal_gate,
    }


def _write_inside(root: Path, relative: str, data: bytes) -> str:
    """Write ``data`` at ``relative`` strictly inside ``root``; return its SHA-256."""

    root = Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise RuntimeError(f"refusing to write outside {root}: {relative}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return _sha(data)


def write_g1_candidate_package(
    root: Path,
    *,
    base_commit: str,
    tests_executed: list[dict[str, Any]] | None = None,
    checkpoint_body: str | None = None,
    summaries: Mapping[str, str] | None = None,
    justifications: Mapping[str, str] | None = None,
    fullstack_reference: Mapping[str, Any] | None = None,
    known_inconsistency: str | None = None,
    date: str = FIXTURE_DATE,
    scope: str = "Disposable G1 fixture.",
    carried_findings: list[Any] | None = None,
    next_legal_gate: str = "FRESH_INDEPENDENT_READ_ONLY_AUDIT",
) -> dict[str, str]:
    """Write ledger -> checkpoint -> manifest, in that order, under ``root``."""

    ledger = build_g1_ledger(
        root,
        base_commit=base_commit,
        tests_executed=tests_executed or synthetic_tests_executed(),
        summaries=summaries,
        justifications=justifications,
        fullstack_reference=fullstack_reference,
        known_inconsistency=known_inconsistency,
    )
    ledger_sha = _write_inside(root, GEN.candidate_change_ledger_path or "", _json_bytes(ledger))
    text = build_g1_checkpoint_text(root, ledger_sha=ledger_sha, body=checkpoint_body)
    checkpoint_sha = _write_inside(root, GEN.candidate_checkpoint_path, text.encode("utf-8"))
    manifest = build_g1_manifest(
        root,
        checkpoint_sha=checkpoint_sha,
        ledger_sha=ledger_sha,
        head=base_commit,
        date=date,
        scope=scope,
        carried_findings=carried_findings,
        next_legal_gate=next_legal_gate,
    )
    manifest_sha = _write_inside(root, GEN.candidate_manifest_path, _json_bytes(manifest))
    return {"ledger": ledger_sha, "checkpoint": checkpoint_sha, "manifest": manifest_sha}


# ---------------------------------------------------------------------------
# The disposable G1 repository fixture
# ---------------------------------------------------------------------------


def g1_fixture_paths(extra: tuple[str, ...] = ()) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            [
                *lc.ACCEPTED_IMPLEMENTATION_PATHS,
                *lc.VALIDATION_IDENTITY_PATHS,
                *lc.governance_authority_identity_paths(),
                R8_GEN.accepted_lifecycle_record_path,
                U06_R3_GEN.accepted_lifecycle_record_path,
                *extra,
            ]
        )
    )


def _is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def safe_dispose(root: Path) -> None:
    """Remove a disposable fixture root, and nothing that is not one."""

    root = Path(root)
    temp = Path(tempfile.gettempdir()).resolve()
    if _is_link(root) or root.resolve().parent != temp or not root.name.startswith(
        FIXTURE_PREFIX
    ):
        raise RuntimeError(f"refusing to remove a non-disposable path: {root}")

    def _force(func, target, _exc) -> None:
        try:
            Path(target).chmod(stat.S_IWRITE)
            func(target)
        except OSError:
            pass

    shutil.rmtree(root.resolve(), onexc=_force)


class G1Fixture:
    """A throwaway Git repository carrying a G1 promotion chain.

    Stages, each a separate commit so publication containment is honest:
    ``package`` (G1 candidate package) -> ``promote`` (Phases A, B, C) ->
    ``scope`` (G1 scope authorization) -> ``evidence`` (captured 21d no-solve
    payload) -> ``execution`` (G1 execution authorization).
    """

    STAGES = ("package", "promote", "scope", "evidence", "execution")

    def __init__(self, *, stage: str = "package", extra_paths: tuple[str, ...] = ()) -> None:
        if stage not in self.STAGES:
            raise ValueError(stage)
        self.root = Path(tempfile.mkdtemp(prefix=FIXTURE_PREFIX)).resolve()
        self.roles: dict[str, dict[str, str]] = {}
        self.commits: dict[str, str] = {}
        try:
            for relative in g1_fixture_paths(extra_paths):
                source = ROOT / relative
                if source.is_file():
                    target = self.root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
            _git_ok(self.root, "init", "--quiet")
            _git_ok(self.root, "config", "user.email", "fixture@example.invalid")
            _git_ok(self.root, "config", "user.name", "fixture")
            _git_ok(self.root, "config", "commit.gpgsign", "false")
            alternates = self.root / ".git" / "objects" / "info" / "alternates"
            alternates.parent.mkdir(parents=True, exist_ok=True)
            alternates.write_bytes(
                ((ROOT / ".git" / "objects").resolve().as_posix() + "\n").encode("utf-8")
            )
            _git_ok(
                self.root, "update-ref", "refs/heads/thesis-v7",
                _git_text(ROOT, "rev-parse", "HEAD"),
            )
            _git_ok(self.root, "symbolic-ref", "HEAD", "refs/heads/thesis-v7")
            self.base_commit = g1_predecessor_commit()
            self.package = write_g1_candidate_package(self.root, base_commit=self.base_commit)
            self.commits["package"] = self.commit("fixture: G1 candidate package")
            self.live_digest = lc.implementation_identity_digest(self.root)
            for name in self.STAGES[1 : self.STAGES.index(stage) + 1]:
                getattr(self, f"_stage_{name}")()
        except BaseException:
            self.dispose()
            raise

    # -- helpers -----------------------------------------------------------

    def head(self) -> str:
        return _git_text(self.root, "rev-parse", "HEAD")

    def commit(self, message: str) -> str:
        _git_ok(self.root, "add", "-A")
        _git_ok(self.root, "commit", "--quiet", "-m", message)
        head = self.head()
        _git_ok(self.root, "update-ref", f"refs/remotes/{lc.EXPECTED_UPSTREAM}", head)
        return head

    def write(self, relative: str, payload: Any) -> str:
        data = payload.encode("utf-8") if isinstance(payload, str) else (
            payload if isinstance(payload, bytes) else _json_bytes(payload)
        )
        return _write_inside(self.root, relative, data)

    def read_json(self, relative: str) -> dict[str, Any]:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def dispose(self) -> None:
        if self.root.exists():
            safe_dispose(self.root)

    # -- promotion ----------------------------------------------------------

    def _envelope(self, role: str) -> dict[str, Any]:
        contract = GEN.role_contracts[role]
        payload = {
            "artifact_type": contract.artifact_type,
            "schema_version": contract.schema_version,
            "lineage_id": GEN.lineage_id,
            "target_candidate_id": GEN.candidate_id,
            "candidate_checkpoint": {
                "path": GEN.candidate_checkpoint_path,
                "sha256": self.package["checkpoint"],
            },
            "implementation_identity_digest": self.live_digest,
        }
        if contract.declares_candidate_manifest:
            payload["candidate_manifest"] = {
                "path": GEN.candidate_manifest_path,
                "sha256": self.package["manifest"],
            }
        for earlier in contract.binds_roles:
            if earlier != "implementation_candidate":
                payload[earlier] = dict(self.roles[earlier])
        return payload

    def _write_role(self, role: str, payload: dict[str, Any]) -> None:
        relative = GEN.role_record_path_map[role]
        self.roles[role] = {"path": relative, "sha256": self.write(relative, payload)}

    def lawful_lifecycle_record(self) -> dict[str, Any]:
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
            "roles": {role: dict(entry) for role, entry in self.roles.items()},
        }

    def _stage_promote(self) -> None:
        self.roles["implementation_candidate"] = {
            "path": GEN.candidate_manifest_path,
            "sha256": self.package["manifest"],
        }
        audit = self._envelope("independent_audit_pass")
        audit.update(
            verdict="PASS", blocking_critical=0, blocking_major=0,
            independent_audit=True, candidate_author_is_not_self_accepting=True,
        )
        self._write_role("independent_audit_pass", audit)
        self.commits["phase_a"] = self.commit("fixture: phase A")
        closure = self._envelope("acceptance_closure")
        closure.update(
            acceptance_status=lc.ACCEPTED_ACCEPTANCE_STATUS,
            audit_verdict="PASS",
            audit_publication_commit=self.commits["phase_a"],
        )
        self._write_role("acceptance_closure", closure)
        manifest = self._envelope("acceptance_manifest")
        manifest["acceptance_status"] = lc.ACCEPTED_ACCEPTANCE_STATUS
        self._write_role("acceptance_manifest", manifest)
        self.commits["phase_b"] = self.commit("fixture: phase B")
        refreeze = self._envelope("production_authority_re_freeze")
        refreeze.update(
            production_authority_status_intended=lc.FROZEN_STATUS,
            authorizes_main_full81=False,
            acceptance_publication_commit=self.commits["phase_b"],
        )
        self._write_role("production_authority_re_freeze", refreeze)
        self.write(GEN.accepted_lifecycle_record_path, self.lawful_lifecycle_record())
        self.commits["promote"] = self.commit("fixture: phase C")

    # -- scope authorization -------------------------------------------------

    def resolve_lifecycle(self) -> dict[str, Any]:
        return lc.resolve_u06_lifecycle(self.root)

    def resolve_scope(self) -> dict[str, Any]:
        return auth.resolve_full81_authorization(self.root, self.resolve_lifecycle())

    def lawful_scope_authorization(self) -> dict[str, Any]:
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
            "production_authority_generation_id": GEN.generation_id,
            "production_authority_lineage_id": GEN.lineage_id,
            "production_authority_accepted_lifecycle_record": {
                "path": GEN.accepted_lifecycle_record_path,
                "sha256": lc.sha256_file(self.root / GEN.accepted_lifecycle_record_path),
            },
            "production_authority_publication_commit": self.commits["promote"],
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

    def _stage_scope(self) -> None:
        self.write(auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(), self.lawful_scope_authorization())
        self.commits["scope"] = self.commit("fixture: G1 scope authorization")

    # -- no-solve evidence and execution authorization ------------------------

    def lawful_evidence(self) -> dict[str, Any]:
        """What 21d prints on its no-solve PASS path, for this fixture's state."""

        lifecycle = self.resolve_lifecycle()
        scope = auth.resolve_full81_authorization(self.root, lifecycle)
        return {
            "status": auth.NO_SOLVE_PREFLIGHT_EVIDENCE_STATUS,
            "verdict": auth.NO_SOLVE_PREFLIGHT_EVIDENCE_VERDICT,
            "case_set": auth.EXPECTED_EXECUTION_CASE_SET,
            "selected_case_count": auth.EXPECTED_CASE_COUNT,
            "selected_case_plan": [f"fixture_case_{i:02d}" for i in range(81)],
            "main_full81_no_solve_preflight_authorized": True,
            "runner_version": auth.EXPECTED_RUNNER_VERSION,
            "production_authority_generation_id": GEN.generation_id,
            "u06_accepted_lifecycle": lc.lifecycle_summary(lifecycle),
            "main_full81_authorization": auth.authorization_summary(scope),
            "execution_counters": {
                "model_constructions": 0,
                "optimization_calls": 0,
                "economic_evaluations": 0,
            },
        }

    def _stage_evidence(self) -> None:
        self.write(auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix(), self.lawful_evidence())
        self.commits["evidence"] = self.commit("fixture: captured 21d no-solve evidence")

    def lawful_execution_authorization(self) -> dict[str, Any]:
        runner = auth.EXPECTED_RUNNER_RELATIVE_PATH
        scope = auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        evidence = auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix()
        return {
            "artifact_type": auth.EXECUTION_AUTHORIZATION_ARTIFACT_TYPE,
            "schema_version": auth.EXECUTION_AUTHORIZATION_SCHEMA_VERSION,
            "lineage_id": auth.LINEAGE_ID,
            "candidate_id": auth.CANDIDATE_ID,
            "execution_authorization_status": auth.EXECUTION_REQUIRED_DECLARED_STATUS,
            "authorization_scope": auth.AUTHORIZATION_SCOPE,
            "authorizes": [auth.EXECUTION_AUTHORIZED_ACT],
            "case_set": auth.EXPECTED_EXECUTION_CASE_SET,
            "authorizes_a2": False,
            "authorizes_sensitivity_solves": False,
            "restart_policy": auth.REQUIRED_RESTART_POLICY,
            "required_execution_interlock_flags": list(auth.REQUIRED_EXECUTION_INTERLOCK_FLAGS),
            "production_authority_generation_id": GEN.generation_id,
            "production_authority_lineage_id": GEN.lineage_id,
            "production_authority_accepted_lifecycle_record": {
                "path": GEN.accepted_lifecycle_record_path,
                "sha256": lc.sha256_file(self.root / GEN.accepted_lifecycle_record_path),
            },
            "production_authority_publication_commit": self.commits["promote"],
            "implementation_identity_digest": self.live_digest,
            "scope_authorization": {"path": scope, "sha256": lc.sha256_file(self.root / scope)},
            "scope_authorization_publication_commit": self.commits["scope"],
            "no_solve_preflight_evidence": {
                "path": evidence,
                "sha256": lc.sha256_file(self.root / evidence),
            },
            "no_solve_preflight_publication_commit": self.commits["evidence"],
            "target_runner": {
                "path": runner,
                "version": auth.EXPECTED_RUNNER_VERSION,
                "sha256": lc.sha256_file(self.root / runner),
            },
            "alpha_universe": list(auth.EXPECTED_ALPHA_UNIVERSE),
            "beta_universe_h": list(auth.EXPECTED_BETA_UNIVERSE_H),
            "case_count": auth.EXPECTED_CASE_COUNT,
            "solver_parameter_fingerprint": auth.solver_parameter_fingerprint(),
            "execution_input_authority": {
                pin.relative_path: pin.sha256 for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS
            },
            "excluded_scopes": list(auth.REQUIRED_DECLARED_EXCLUSIONS),
            "a2_excluded": True,
        }

    def _stage_execution(self) -> None:
        self.write(
            auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
            self.lawful_execution_authorization(),
        )
        self.commits["execution"] = self.commit("fixture: G1 execution authorization")

    def validate_execution(self, payload: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
        lifecycle = kwargs.pop("lifecycle", None) or self.resolve_lifecycle()
        return auth.validate_execution_authorization_payload(
            self.root,
            payload,
            record_relative=kwargs.pop(
                "record_relative", auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
            ),
            lifecycle=lifecycle,
            scope_authorization=kwargs.pop("scope_authorization", None),
        )


# ---------------------------------------------------------------------------
# A. The G1 generation, and R8 as a historical predecessor
# ---------------------------------------------------------------------------


class G1GenerationContractTests(unittest.TestCase):
    def test_g1_is_the_unique_current_generation(self) -> None:
        self.assertIs(GEN, lc.G1_GENERATION)
        current = [g for g in lc.AUTHORITY_GENERATIONS if g is lc.CURRENT_GENERATION]
        self.assertEqual(current, [lc.G1_GENERATION])
        self.assertNotIn(GEN, lc.HISTORICAL_GENERATIONS)
        self.assertEqual(GEN.generation_id, "CURRENT_FULL81_PRODUCTION_GENERATION_G1")
        self.assertEqual(GEN.lineage_id, GEN.generation_id)
        self.assertEqual(GEN.candidate_id, "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1")
        self.assertEqual(GEN.candidate_audit_state, "NOT_YET_PERFORMED")
        self.assertEqual(lc.ACTIVE_CANDIDATE_ID, GEN.candidate_id)
        self.assertEqual(auth.LINEAGE_ID, GEN.lineage_id)
        self.assertEqual(auth.CANDIDATE_ID, GEN.candidate_id)

    def test_g1_owns_its_contract_ledger_and_predeclared_paths(self) -> None:
        self.assertEqual(GEN.candidate_manifest_contract, lc.G1_CANDIDATE_MANIFEST_CONTRACT)
        self.assertIn(lc.G1_CANDIDATE_MANIFEST_CONTRACT, lc.KNOWN_CANDIDATE_MANIFEST_CONTRACTS)
        self.assertTrue(GEN.candidate_change_ledger_path)
        roles = GEN.role_record_path_map
        self.assertEqual(set(roles), set(lc.NON_SELF_ACCEPTABLE_ROLES))
        self.assertEqual(len(set(roles.values())), 4)
        prefix = "results/provenance/current_full81_production_generation_g1_"
        for path in (
            *roles.values(),
            GEN.accepted_lifecycle_record_path,
            GEN.candidate_manifest_path,
            GEN.candidate_change_ledger_path,
        ):
            self.assertTrue(path.startswith(prefix), path)
        self.assertTrue(
            GEN.candidate_checkpoint_path.startswith(
                "docs/checkpoints/current_full81_production_generation_g1_candidate_r1_"
            )
        )
        self.assertEqual(
            lc.CANDIDATE_MANIFEST_CONTRACT_VALIDATORS[lc.G1_CANDIDATE_MANIFEST_CONTRACT],
            lc.validate_g1_candidate_manifest_contract,
        )

    def test_r8_generation_values_are_byte_stable_and_historical(self) -> None:
        self.assertIn(R8_GEN, lc.HISTORICAL_GENERATIONS)
        self.assertEqual(R8_GEN.lineage_id, "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1")
        self.assertEqual(R8_GEN.candidate_id, "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8")
        self.assertEqual(
            R8_GEN.candidate_manifest_contract,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4,
        )
        self.assertEqual(
            R8_GEN.candidate_change_ledger_path,
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH,
        )
        self.assertEqual(
            R8_GEN.accepted_lifecycle_record_path,
            "results/provenance/main_full81_preflight_authorization_guard_accepted_lifecycle_r1/"
            "accepted_lifecycle_record.json",
        )
        self.assertEqual(R8_GEN.disposition, "CURRENT_GENERATION_CANDIDATE_NOT_ACCEPTED_NOT_FROZEN")
        for historical in lc.HISTORICAL_GENERATIONS:
            with self.subTest(generation=historical.generation_id):
                self.assertIsNone(historical.predeclared_role_record_paths)
        for older in (AUTH_MECH_R2_GEN, U06_R3_GEN):
            self.assertIsNone(older.candidate_manifest_contract)
            self.assertIsNone(older.candidate_change_ledger_path)

    def test_predecessor_chain_is_g1_r8_r2_r3(self) -> None:
        chain = [GEN]
        while chain[-1].predecessor_generation_id:
            chain.append(lc.GENERATIONS_BY_ID[chain[-1].predecessor_generation_id])
        self.assertEqual(
            [g.generation_id for g in chain],
            [
                GEN.generation_id,
                R8_GEN.generation_id,
                AUTH_MECH_R2_GEN.generation_id,
                U06_R3_GEN.generation_id,
            ],
        )
        for successor, ancestor in zip(chain, chain[1:]):
            self.assertEqual(successor.predecessor_lineage_id, ancestor.lineage_id)
            self.assertEqual(
                successor.predecessor_accepted_lifecycle_record_path,
                ancestor.accepted_lifecycle_record_path,
            )

    def test_every_predecessor_candidate_is_barred_from_g1(self) -> None:
        barred = set(GEN.superseded_candidate_ids)
        self.assertIn(R8_GEN.candidate_id, barred)
        self.assertTrue(set(R8_GEN.superseded_candidate_ids) <= barred)
        self.assertNotIn(GEN.candidate_id, barred)
        for path in R8_GEN.candidate_artifact_paths:
            self.assertIn(path, GEN.candidate_artifact_paths)

    def test_g1_audit_register_is_separate_and_truthful(self) -> None:
        register = lc.CANDIDATE_AUDIT_REGISTERS[GEN.generation_id]
        self.assertIs(register, lc.CURRENT_CANDIDATE_AUDIT_HISTORY)
        entry = register[GEN.candidate_id]
        self.assertEqual(entry["independent_audit"], "NOT_YET_PERFORMED")
        self.assertEqual(entry["publication"], "NOT_YET_AUTHORIZED")
        self.assertEqual(entry["acceptance"], "NOT_YET_ACCEPTED")
        self.assertNotIn(GEN.candidate_id, lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY)
        self.assertIs(
            lc.CANDIDATE_AUDIT_REGISTERS[R8_GEN.generation_id],
            lc.PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY,
        )

    def test_contract_validators_never_judge_each_other(self) -> None:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_candidate_manifest_identity_contract(
                ROOT, generation=GEN, mode=lc.CANDIDATE_MANIFEST_MODE_GATE,
                manifest_bytes=b"{}",
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_SCHEMA_INVALID")
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_g1_candidate_manifest_contract(
                ROOT, generation=R8_GEN, mode=lc.CANDIDATE_MANIFEST_MODE_GATE,
                manifest_bytes=b"{}",
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_SCHEMA_INVALID")


# ---------------------------------------------------------------------------
# B. The candidate phase is explicit and fail-closed (phase-aware)
# ---------------------------------------------------------------------------


class CandidatePhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.phase = lc.current_generation_phase(ROOT)
        cls.lifecycle = lc.resolve_u06_lifecycle(ROOT)

    def test_phase_is_deterministic_ordered_and_never_authorizes(self) -> None:
        again = lc.current_generation_phase(ROOT)
        self.assertEqual(self.phase, again)
        self.assertNotEqual(self.phase["phase"], lc.G1_PHASE_OUT_OF_ORDER)
        self.assertEqual(self.phase["out_of_order_present"], [])
        self.assertFalse(self.phase["authorizes_anything"])
        self.assertTrue(self.phase["presence_is_not_validity"])
        self.assertEqual(self.phase["paths"], lc.g1_predeclared_governance_paths(GEN))
        self.assertEqual(len(self.phase["paths"]), 11)

    def test_every_future_artifact_is_named_and_absent_beyond_the_phase(self) -> None:
        reached = [stage for stage, _ in lc.G1_GOVERNANCE_STAGES]
        index = reached.index(self.phase["phase"]) if self.phase["phase"] in reached else -1
        for position, (stage, keys) in enumerate(lc.G1_GOVERNANCE_STAGES):
            for key in keys:
                with self.subTest(stage=stage, key=key):
                    self.assertEqual(self.phase["presence"][key], position <= index)

    def test_real_lifecycle_matches_the_phase(self) -> None:
        if not self.phase["presence"]["accepted_lifecycle_record"]:
            self.assertEqual(self.lifecycle["accepted_lifecycle_overlay"], "ABSENT")
            self.assertEqual(self.lifecycle["production_authority_freeze_status"], "NOT_FROZEN")
            self.assertFalse(lc.is_frozen(self.lifecycle))
            with self.assertRaises(lc.U06LifecycleError) as caught:
                lc.require_frozen_lifecycle(self.lifecycle)
            self.assertEqual(caught.exception.status, "U06_ACCEPTED_LIFECYCLE_ABSENT")
        else:
            # A present record must be a VALID acceptance of the current
            # generation; presence alone is never accepted.
            self.assertEqual(self.lifecycle["accepted_lifecycle_overlay"], "PRESENT_VALID")
            self.assertTrue(lc.is_frozen(self.lifecycle))
        self.assertEqual(self.lifecycle["generation_id"], GEN.generation_id)

    def test_real_scope_authorization_matches_the_phase(self) -> None:
        scope = auth.resolve_full81_authorization(ROOT, self.lifecycle)
        if not self.phase["presence"]["main_full81_scope_authorization"]:
            self.assertEqual(scope["full81_authorization_status"], auth.NOT_GRANTED)
            self.assertEqual(scope["authorization_overlay"], auth.ABSENT)
            self.assertFalse(auth.is_authorized_for_preflight(ROOT, scope))
            with self.assertRaises(bundle.Full81AuthorizationNotGranted):
                bundle.require_full81_scope_authorization(
                    "full81", root=ROOT, lifecycle=self.lifecycle
                )
        else:
            self.assertEqual(
                scope["full81_authorization_status"], auth.AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT
            )

    def test_real_execution_authorization_matches_the_phase(self) -> None:
        state = auth.resolve_full81_execution_authorization(ROOT, self.lifecycle)
        if not self.phase["presence"]["main_full81_execution_authorization"]:
            self.assertEqual(state["execution_authorization_status"], auth.NOT_GRANTED)
            self.assertEqual(state["execution_authorization_overlay"], auth.ABSENT)
            for supplied in (None, auth.resolve_full81_authorization(ROOT, self.lifecycle)):
                with self.subTest(supplied=supplied is not None):
                    with self.assertRaises(auth.Full81AuthorizationError) as caught:
                        auth.require_full81_execution_authorization(supplied)
                    self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")
        else:
            self.assertEqual(
                state["execution_authorization_status"], auth.AUTHORIZED_FOR_FULL81_EXECUTION
            )

    def test_absence_is_represented_and_is_never_authorization(self) -> None:
        absent = lc.absent_lifecycle()
        self.assertFalse(lc.is_frozen(absent))
        self.assertEqual(absent["accepted_lifecycle_overlay"], "ABSENT")
        scope = auth.absent_authorization()
        self.assertEqual(scope["full81_authorization_status"], auth.NOT_GRANTED)
        execution = auth.absent_execution_authorization()
        self.assertEqual(execution["execution_authorization_status"], auth.NOT_GRANTED)
        self.assertEqual(execution["execution_authorization_overlay"], auth.ABSENT)
        self.assertIn(
            auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
            execution["execution_blocked_reason"],
        )
        requirements = auth.future_execution_authorization_requirements()
        self.assertFalse(requirements["historical_authority_accepted_as_placeholder"])
        self.assertFalse(requirements["future_hashes_fabricated_now"])

    def test_resolvers_write_nothing_to_the_real_repository(self) -> None:
        before = _git(ROOT, "status", "--porcelain=v1", "-uall", "-z").stdout
        live = lc.resolve_u06_lifecycle(ROOT)
        auth.resolve_full81_authorization(ROOT, live)
        auth.resolve_full81_execution_authorization(ROOT, live)
        lc.current_generation_phase(ROOT)
        after = _git(ROOT, "status", "--porcelain=v1", "-uall", "-z").stdout
        self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# C. The G1 content contract and change ledger
# ---------------------------------------------------------------------------


class G1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(stage="package")
        cls.manifest = cls.fixture.read_json(GEN.candidate_manifest_path)
        cls.ledger = cls.fixture.read_json(GEN.candidate_change_ledger_path or "")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def status_of(self, manifest: Mapping[str, Any], mode: str = lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE) -> str:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_g1_candidate_manifest_contract(
                self.fixture.root, mode=mode, manifest_bytes=_json_bytes(manifest)
            )
        return caught.exception.status

    def ledger_status(self, ledger: Mapping[str, Any]) -> str:
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_g1_candidate_change_ledger(
                self.fixture.root,
                _json_bytes(ledger),
                self.manifest,
                GEN,
                mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE,
            )
        return caught.exception.status

    def test_the_lawful_package_passes_in_both_modes(self) -> None:
        for mode in lc.CANDIDATE_MANIFEST_MODES:
            with self.subTest(mode=mode):
                report = lc.validate_candidate_manifest_content_contract(
                    self.fixture.root, generation=GEN, mode=mode
                )
                self.assertEqual(report["contract"], lc.G1_CANDIDATE_MANIFEST_CONTRACT)
                self.assertEqual(report["structural_identity_count"], 0)
                self.assertEqual(
                    report["collected_identity_count"], report["role_bound_identity_count"]
                )
                self.assertEqual(report["change_ledger"]["structural_identity_count"], 0)
                self.assertFalse(report["computed_binding_facts"]["manifest_records_own_sha256"])
                self.assertEqual(
                    report["identity_digests"][lc.G1_IDENTITY_CLASS_RUNTIME],
                    lc.implementation_identity_digest(ROOT),
                )
        gate = lc.validate_g1_candidate_manifest_contract(
            self.fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE
        )
        self.assertEqual(gate["validation_identity_authority"], "PUBLISHED_WITH_CANDIDATE_MANIFEST")
        self.assertEqual(gate["validation_reference_commit"], self.fixture.commits["package"])

    def test_the_package_reproduces_the_real_change_set(self) -> None:
        listed = {e["path"]: e["change_class"] for e in self.ledger["modified_files"]}
        # 21i is absent from the predecessor commit, and its class is DERIVED
        # from published evidence, never declared: PUBLISH_UNCHANGED holds only
        # while its bytes equal the raw SHA-256 the published R8 ledger recorded
        # for it.  G1 made its N-04 control phase-aware, so G1 CREATES it; the
        # R8 record stays published byte-identical, as historical evidence only.
        suite = "tests/test_21i_main_full81_preflight_authorization_guard.py"
        r8_ledger = R8_GEN.candidate_change_ledger_path or ""
        self.assertEqual(lc.blob_sha256_at(ROOT, "HEAD", r8_ledger), lc.sha256_file(ROOT / r8_ledger))
        r8_commit = lc.last_modifying_commit(ROOT, r8_ledger)
        recorded = {
            entry["suite"]: entry["raw_sha256"]
            for entry in json.loads(
                _git(ROOT, "cat-file", "blob", f"{r8_commit}:{r8_ledger}").stdout
            )["tests_executed"]
        }
        self.assertIn(suite, recorded)
        self.assertNotEqual(lc.sha256_file(ROOT / suite), recorded[suite])
        self.assertIsNone(g1_publication_source(suite, lc.sha256_file(ROOT / suite)))
        self.assertEqual(listed.get(suite), "CREATE")
        self.assertNotIn("PUBLISH_UNCHANGED", set(listed.values()))
        self.assertEqual(listed.get("tests/test_21l_full81_production_generation_g1.py"), "CREATE")
        for path in (
            "src/production_authority_lifecycle_u06.py",
            "src/main_full81_authorization_v7_4.py",
            "src/production_authority_bundle_v7_4.py",
        ):
            self.assertEqual(listed.get(path), "MODIFY")
        for unchanged in (
            "scripts/21c_preflight_v7_3_layer_a_successor.py",
            "scripts/21d_preflight_v7_3_final81_successor.py",
            "src/annual_design_model_v7_2.py",
            "src/production_successor_stack_v7_3.py",
            "data/reference/parameter_registry_v7_2.csv",
        ):
            self.assertNotIn(unchanged, listed)

    def test_forbidden_self_label_and_own_identity_fail(self) -> None:
        labelled = copy.deepcopy(self.manifest)
        labelled["scope"] = {"placeholder_or_stale_sha_used": False}
        self.assertEqual(self.status_of(labelled), "U06_ROLE_SCHEMA_INVALID")
        own = copy.deepcopy(self.manifest)
        own["carried_findings"] = [
            {"path": GEN.candidate_manifest_path, "sha256": "a" * 64}
        ]
        self.assertEqual(self.status_of(own), "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED")

    def test_unclassified_field_and_hidden_identity_fail(self) -> None:
        extra = copy.deepcopy(self.manifest)
        extra["unclassified"] = "x"
        self.assertEqual(self.status_of(extra), "U06_ROLE_SCHEMA_INVALID")
        hidden = copy.deepcopy(self.manifest)
        hidden["scope"] = "see " + "b" * 64 + " for details"
        self.assertEqual(self.status_of(hidden), "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED")

    def test_duplicate_keys_and_wrong_contract_marker_fail(self) -> None:
        raw = _json_bytes(self.manifest).replace(
            b'"date":', b'"date": "2026-01-01",\n  "date":', 1
        )
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_g1_candidate_manifest_contract(
                self.fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE, manifest_bytes=raw
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_SCHEMA_INVALID")
        marker = copy.deepcopy(self.manifest)
        marker["candidate_manifest_contract"] = (
            lc.FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4
        )
        self.assertEqual(self.status_of(marker), "U06_ROLE_SCHEMA_INVALID")

    def test_superseded_candidate_or_wrong_generation_fail(self) -> None:
        for field, value, status in (
            ("candidate_id", R8_GEN.candidate_id, "U06_SUPERSEDED_CANDIDATE_REJECTED"),
            ("generation_id", R8_GEN.generation_id, "U06_LINEAGE_MISMATCH"),
            ("artifact_type", R8_GEN.role_contracts["implementation_candidate"].artifact_type, "U06_ROLE_ARTIFACT_TYPE_MISMATCH"),
        ):
            with self.subTest(field=field):
                payload = copy.deepcopy(self.manifest)
                payload[field] = value
                self.assertEqual(self.status_of(payload), status)

    def test_every_identity_section_is_bound_to_its_own_role(self) -> None:
        # Paths no bundle pin restates, so the swap reaches the section's own
        # obligation rather than the same-path conflict guard.
        pinned = {pin.relative_path for pin in bundle.all_pins()}

        def unpinned(section: str) -> list[str]:
            return [p for p in sorted(self.manifest[section]["paths"]) if p not in pinned][:2]

        cases = {
            "runtime_path_swapped": ("runtime_identity", *unpinned("runtime_identity"), "U06_IMPLEMENTATION_IDENTITY_DRIFT"),
            "validation_path_swapped": ("validation_identity", *unpinned("validation_identity"), "U06_VALIDATION_IDENTITY_DRIFT"),
            "governance_path_swapped": ("governance_authority_identity", *unpinned("governance_authority_identity"), "U06_GOVERNANCE_IDENTITY_DRIFT"),
        }
        for name, (section, a, b, status) in cases.items():
            with self.subTest(case=name):
                payload = copy.deepcopy(self.manifest)
                paths = payload[section]["paths"]
                paths[a], paths[b] = paths[b], paths[a]
                payload[section]["digest"] = lc.canonical_identity_digest(paths)
                self.assertEqual(self.status_of(payload), status)
        stale_digest = copy.deepcopy(self.manifest)
        stale_digest["runtime_identity"]["digest"] = "c" * 64
        self.assertEqual(self.status_of(stale_digest), "U06_IMPLEMENTATION_IDENTITY_DRIFT")

    def test_a_restated_bundle_pin_must_equal_the_bundle_and_live_bytes(self) -> None:
        payload = copy.deepcopy(self.manifest)
        label = "framework_v7_4"
        payload["authority_bundle"]["pins"][label]["sha256"] = self.manifest[
            "authority_bundle"
        ]["pins"]["registry_v7_4"]["sha256"]
        self.assertIn(self.status_of(payload), {"U06_ROLE_TARGET_MISMATCH"})

    def test_checkpoint_claims_are_role_bound(self) -> None:
        checkpoint = self.fixture.root / GEN.candidate_checkpoint_path
        original = checkpoint.read_bytes()
        try:
            text = original.decode("utf-8")
            runtime = self.manifest["runtime_identity"]["digest"]
            governance = self.manifest["governance_authority_identity"]["digest"]
            for name, mutated, status in (
                (
                    "lawful_value_under_wrong_role",
                    text.replace(
                        f"/runtime_identity/digest {runtime}",
                        f"/runtime_identity/digest {governance}",
                    ),
                    "U06_ROLE_TARGET_MISMATCH",
                ),
                (
                    "digest_outside_claims",
                    text.replace("Synthetic.", f"Synthetic {runtime}."),
                    "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
                ),
                (
                    "own_identity_claimed",
                    text.replace(
                        lc.CHECKPOINT_CLAIM_FENCE_CLOSE + "\n",
                        f"{lc.CHECKPOINT_SELF_IDENTITY_POINTER} {'d' * 64}\n"
                        + lc.CHECKPOINT_CLAIM_FENCE_CLOSE + "\n",
                        1,
                    ),
                    "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
                ),
            ):
                with self.subTest(case=name):
                    checkpoint.write_bytes(mutated.encode("utf-8"))
                    payload = copy.deepcopy(self.manifest)
                    payload["candidate_checkpoint"]["sha256"] = lc.sha256_file(checkpoint)
                    self.assertEqual(self.status_of(payload), status)
        finally:
            checkpoint.write_bytes(original)

    def test_r8_manifest_bytes_can_never_fill_the_g1_role(self) -> None:
        r8_manifest = (ROOT / R8_GEN.candidate_manifest_path).read_bytes()
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_g1_candidate_manifest_contract(
                self.fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE,
                manifest_bytes=r8_manifest,
            )
        self.assertEqual(caught.exception.status, "U06_ROLE_SCHEMA_INVALID")

    @staticmethod
    def _restatus(ledger: dict[str, Any], path: str, change: str | None) -> None:
        for row in ledger["live_roles"]:
            if row["path"] == path:
                row["lifecycle_status"] = lc.G1_LIVE_ROLE_STATUS_BY_CHANGE[change]

    def test_the_ledger_is_closed_world(self) -> None:
        # Each mutation is kept internally consistent (the live-role status
        # follows it), so the CLOSED-WORLD change-set check is what refuses it.
        dropped = copy.deepcopy(self.ledger)
        removed = dropped["modified_files"].pop(0)
        self._restatus(dropped, removed["path"], None)
        self.assertEqual(self.ledger_status(dropped), "U06_ROLE_TARGET_MISMATCH")
        extra = copy.deepcopy(self.ledger)
        fake = dict(extra["modified_files"][0])
        fake.update(path="scripts/21d_preflight_v7_3_final81_successor.py", change_class="MODIFY")
        extra["modified_files"] = sorted(extra["modified_files"] + [fake], key=lambda e: e["path"])
        self._restatus(extra, fake["path"], "MODIFY")
        self.assertEqual(self.ledger_status(extra), "U06_ROLE_TARGET_MISMATCH")
        # PUBLISH_UNCHANGED is derived and the real G1 change set has none, so
        # the publication-source attacks run on a synthetic entry that the
        # production validator first ACCEPTS: a disposable repository publishes
        # evidence recording the exact raw SHA-256 of a suite the ledger
        # CREATES, and only then is that suite reclassified.
        fixture = G1Fixture(stage="package")
        try:
            suite = "tests/test_21i_main_full81_preflight_authorization_guard.py"
            other = "tests/test_21l_full81_production_generation_g1.py"
            evidence = "results/provenance/g1_fixture_publication_evidence/tests_executed.json"
            fixture.write(evidence, {"tests_executed": [
                {"suite": other, "raw_sha256": lc.sha256_file(fixture.root / other)},
                {"suite": suite, "raw_sha256": lc.sha256_file(fixture.root / suite)},
            ]})
            evidence_commit = fixture.commit("fixture: published evidence of exact suite bytes")
            manifest = fixture.read_json(GEN.candidate_manifest_path)
            lawful = fixture.read_json(GEN.candidate_change_ledger_path or "")
            by_path = {entry["path"]: entry for entry in lawful["modified_files"]}
            self.assertEqual(by_path[suite]["change_class"], "CREATE")
            by_path[suite].update(
                change_class="PUBLISH_UNCHANGED",
                publication_source={
                    "evidence_path": evidence,
                    "evidence_commit": evidence_commit,
                    "evidence_pointer": "/tests_executed/1/raw_sha256",
                },
            )
            self._restatus(lawful, suite, "PUBLISH_UNCHANGED")

            def validate(ledger: Mapping[str, Any]) -> dict[str, Any]:
                return lc.validate_g1_candidate_change_ledger(
                    fixture.root, _json_bytes(ledger), manifest, GEN,
                    mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE,
                )

            def status(ledger: Mapping[str, Any]) -> str:
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    validate(ledger)
                return caught.exception.status

            accepted = validate(lawful)
            self.assertEqual(accepted["unaccounted_identity_count"], 0)

            def source_variant(**change: Any) -> dict[str, Any]:
                variant = copy.deepcopy(lawful)
                for entry in variant["modified_files"]:
                    if entry["path"] == suite:
                        entry["publication_source"].update(change)
                return variant

            self.assertEqual(
                status(source_variant(evidence_pointer="/tests_executed/0/raw_sha256")),
                "U06_ROLE_TARGET_MISMATCH",
            )
            self.assertEqual(
                status(source_variant(evidence_commit="0" * 40)), "U06_PUBLICATION_PROOF_INVALID"
            )
            self.assertEqual(
                status(source_variant(evidence_path=evidence.replace("tests_executed", "absent"))),
                "U06_PUBLICATION_PROOF_INVALID",
            )
            incomplete = copy.deepcopy(lawful)
            for entry in incomplete["modified_files"]:
                if entry["path"] == suite:
                    del entry["publication_source"]["evidence_pointer"]
            self.assertEqual(status(incomplete), "U06_ROLE_SCHEMA_INVALID")
            # Wrong role: a path present at the predecessor commit can never be
            # published unchanged, whatever evidence it cites.
            wrong_role = copy.deepcopy(lawful)
            target = "src/production_authority_bundle_v7_4.py"
            for entry in wrong_role["modified_files"]:
                if entry["path"] == target:
                    self.assertEqual(entry["change_class"], "MODIFY")
                    entry.update(
                        change_class="PUBLISH_UNCHANGED",
                        publication_source=dict(by_path[suite]["publication_source"]),
                    )
            self._restatus(wrong_role, target, "PUBLISH_UNCHANGED")
            self.assertEqual(status(wrong_role), "U06_ROLE_TARGET_MISMATCH")
            # A CREATE entry may not carry a publication source.
            created_with_source = copy.deepcopy(lawful)
            for entry in created_with_source["modified_files"]:
                if entry["path"] == suite:
                    entry["change_class"] = "CREATE"
            self._restatus(created_with_source, suite, "CREATE")
            self.assertEqual(status(created_with_source), "U06_ROLE_SCHEMA_INVALID")
        finally:
            fixture.dispose()

    def test_historical_evidence_must_be_proved_by_a_published_blob(self) -> None:
        wrong_sha = copy.deepcopy(self.ledger)
        wrong_sha["predecessor"]["historical_evidence"][0]["raw_sha256"] = "e" * 64
        self.assertEqual(self.ledger_status(wrong_sha), "U06_ROLE_TARGET_MISMATCH")
        not_ancestor = copy.deepcopy(self.ledger)
        not_ancestor["predecessor"]["historical_evidence"][0]["publication_commit"] = "0" * 40
        self.assertEqual(self.ledger_status(not_ancestor), "U06_PUBLICATION_PROOF_INVALID")
        swapped = copy.deepcopy(self.ledger)
        a, b = swapped["predecessor"]["historical_evidence"]
        a["raw_sha256"], b["raw_sha256"] = b["raw_sha256"], a["raw_sha256"]
        self.assertEqual(self.ledger_status(swapped), "U06_ROLE_TARGET_MISMATCH")

    def test_ledger_tests_roles_and_later_artifacts(self) -> None:
        missing = copy.deepcopy(self.ledger)
        missing["tests_executed"] = missing["tests_executed"][1:]
        self.assertEqual(self.ledger_status(missing), "U06_ROLE_SCHEMA_INVALID")
        failed = copy.deepcopy(self.ledger)
        failed["tests_executed"][0].update(failures=1, result="FAILED")
        self.assertEqual(self.ledger_status(failed), "U06_ROLE_SCHEMA_INVALID")
        wrong_class = copy.deepcopy(self.ledger)
        wrong_class["live_roles"][0]["identity_class"] = lc.G1_IDENTITY_CLASS_VALIDATION
        self.assertEqual(self.ledger_status(wrong_class), "U06_ROLE_SCHEMA_INVALID")
        later = copy.deepcopy(self.ledger)
        later["predecessor"]["fullstack_01_reference"] = {
            "path": GEN.candidate_checkpoint_path,
            "sha256": "f" * 64,
        }
        self.assertIn(
            self.ledger_status(later),
            {"U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED", "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED"},
        )


class ValidationGenerationSeparationTests(unittest.TestCase):
    """The validation generation is separate; runtime-pinned suites are not."""

    def test_unpinned_validation_change_does_not_move_the_gate(self) -> None:
        fixture = G1Fixture(stage="package")
        try:
            target = fixture.root / "tests/test_21i_main_full81_preflight_authorization_guard.py"
            target.write_bytes(target.read_bytes() + b"\n# later validation-only edit\n")
            fixture.commit("fixture: validation-only edit")
            gate = lc.validate_g1_candidate_manifest_contract(
                fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE
            )
            self.assertEqual(gate["validation_reference_commit"], fixture.commits["package"])
            with self.assertRaises(lc.U06LifecycleError) as caught:
                lc.validate_g1_candidate_manifest_contract(
                    fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
                )
            self.assertEqual(caught.exception.status, "U06_VALIDATION_IDENTITY_DRIFT")
        finally:
            fixture.dispose()

    def test_runtime_pinned_validation_and_runtime_changes_move_the_gate(self) -> None:
        for relative, statuses in (
            ("tests/test_21e_v7_4_production_authority_bundle.py", {"U06_ROLE_TARGET_MISMATCH"}),
            ("src/rainflow_validation_v7_2.py", {"U06_IMPLEMENTATION_IDENTITY_DRIFT"}),
        ):
            with self.subTest(path=relative):
                fixture = G1Fixture(stage="package")
                try:
                    target = fixture.root / relative
                    target.write_bytes(target.read_bytes() + b"\n# later edit\n")
                    fixture.commit("fixture: edit")
                    with self.assertRaises(lc.U06LifecycleError) as caught:
                        lc.validate_g1_candidate_manifest_contract(
                            fixture.root, mode=lc.CANDIDATE_MANIFEST_MODE_GATE
                        )
                    self.assertIn(caught.exception.status, statuses)
                finally:
                    fixture.dispose()


# ---------------------------------------------------------------------------
# D. The G1 lifecycle, and R8 isolation
# ---------------------------------------------------------------------------


class G1LifecyclePromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(stage="promote")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def test_a_complete_promotion_freezes_g1_in_the_fixture_only(self) -> None:
        resolved = self.fixture.resolve_lifecycle()
        self.assertEqual(resolved["accepted_lifecycle_overlay"], "PRESENT_VALID", resolved.get("freeze_blocked_reason"))
        self.assertEqual(resolved["generation_id"], GEN.generation_id)
        self.assertTrue(lc.is_frozen(resolved))
        lc.require_frozen_lifecycle_against_live_implementation(self.fixture.root, resolved)
        # The fixture's Phase C commit is never part of the real repository.
        self.assertNotEqual(
            _git(ROOT, "cat-file", "-e", self.fixture.commits["promote"] + "^{commit}").returncode, 0
        )
        # G1: phase-aware, from the source contract.  The real lifecycle is
        # decided by the real phase alone, never by this fixture: before Phase
        # C the real record is absent and nothing is frozen; from Phase C on it
        # must be a VALID frozen acceptance of G1 that binds every role at its
        # predeclared path with the live bytes - presence alone is never enough.
        phase = lc.current_generation_phase(ROOT)
        self.assertEqual(phase["out_of_order_present"], [], phase["phase"])
        self.assertNotEqual(phase["phase"], lc.G1_PHASE_OUT_OF_ORDER)
        real = lc.resolve_u06_lifecycle(ROOT)
        self.assertEqual(real["generation_id"], GEN.generation_id)
        self.assertEqual(real["record_path"], GEN.accepted_lifecycle_record_path)
        if not phase["presence"]["accepted_lifecycle_record"]:
            self.assertFalse((ROOT / GEN.accepted_lifecycle_record_path).exists())
            self.assertEqual(real["accepted_lifecycle_overlay"], "ABSENT")
            self.assertEqual(real["production_authority_freeze_status"], "NOT_FROZEN")
            self.assertFalse(lc.is_frozen(real))
        else:
            self.assertEqual(real["accepted_lifecycle_overlay"], "PRESENT_VALID", real.get("freeze_blocked_reason"))
            self.assertTrue(lc.is_frozen(real))
            lc.require_frozen_lifecycle_against_live_implementation(ROOT, real)
            expected = {
                "implementation_candidate": GEN.candidate_manifest_path,
                **{role: GEN.role_record_path_map[role] for role in lc.NON_SELF_ACCEPTABLE_ROLES},
            }
            self.assertEqual(set(real["satisfied_roles"]), set(lc.REQUIRED_ACCEPTED_ROLES))
            for role, entry in real["satisfied_roles"].items():
                with self.subTest(real_role=role):
                    self.assertEqual(entry["path"], expected[role])
                    self.assertEqual(entry["sha256"], lc.sha256_file(ROOT / entry["path"]))

    def test_a_role_off_its_predeclared_path_is_rejected(self) -> None:
        for role in lc.NON_SELF_ACCEPTABLE_ROLES:
            with self.subTest(role=role):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc._validate_role_path(
                        role,
                        "results/provenance/elsewhere/record.json",
                        GEN.accepted_lifecycle_record_path,
                        GEN,
                    )
                self.assertEqual(caught.exception.status, "U06_ROLE_TARGET_MISMATCH")

    def test_r8_records_can_never_fill_g1_roles(self) -> None:
        r8_record = json.loads((ROOT / R8_GEN.accepted_lifecycle_record_path).read_text(encoding="utf-8"))
        for role, entry in r8_record["roles"].items():
            with self.subTest(role=role):
                with self.assertRaises(lc.U06LifecycleError) as caught:
                    lc._validate_role_path(role, entry["path"], GEN.accepted_lifecycle_record_path, GEN)
                self.assertIn(
                    caught.exception.status,
                    {"U06_ROLE_TARGET_MISMATCH", "U06_SELF_ACCEPTANCE_REJECTED"},
                )
        record = copy.deepcopy(r8_record)
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.validate_accepted_lifecycle_payload(
                self.fixture.root, record,
                record_relative=GEN.accepted_lifecycle_record_path, generation=GEN,
            )
        self.assertIn(caught.exception.status, {"U06_ROLE_ARTIFACT_TYPE_MISMATCH", "U06_ROLE_SCHEMA_MISMATCH"})

    def test_a_superseded_r8_lifecycle_can_never_freeze(self) -> None:
        superseded = {
            **self.fixture.resolve_lifecycle(),
            "generation_id": R8_GEN.generation_id,
            "is_current_generation": False,
            "lineage_id": R8_GEN.lineage_id,
            "target_candidate_id": R8_GEN.candidate_id,
        }
        with self.assertRaises(lc.U06LifecycleError) as caught:
            lc.require_frozen_lifecycle(superseded)
        self.assertEqual(caught.exception.status, "U06_SUPERSEDED_GENERATION_REJECTED")
        live_r8 = lc.validate_accepted_lifecycle_payload
        with self.assertRaises(lc.U06LifecycleError):
            live_r8(
                ROOT,
                json.loads((ROOT / R8_GEN.accepted_lifecycle_record_path).read_text(encoding="utf-8")),
                record_relative=R8_GEN.accepted_lifecycle_record_path,
            )

    def test_post_acceptance_runtime_drift_unfreezes(self) -> None:
        fixture = G1Fixture(stage="promote")
        try:
            self.assertTrue(lc.is_frozen(fixture.resolve_lifecycle()))
            target = fixture.root / "src/rainflow_validation_v7_2.py"
            target.write_bytes(target.read_bytes() + b"\n# post-acceptance edit\n")
            fixture.commit("fixture: runtime drift")
            resolved = fixture.resolve_lifecycle()
            self.assertEqual(resolved["accepted_lifecycle_overlay"], "PRESENT_INVALID")
            self.assertEqual(resolved["rejected_status"], "U06_IMPLEMENTATION_IDENTITY_DRIFT")
        finally:
            fixture.dispose()


# ---------------------------------------------------------------------------
# E. The G1 scope-authorization slot, isolated from the R8 r3 authorization
# ---------------------------------------------------------------------------


class ScopeSlotIsolationTests(unittest.TestCase):
    def test_the_g1_slot_is_new_and_the_r3_slot_is_superseded(self) -> None:
        g1 = auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        self.assertEqual(g1, "results/provenance/main_full81_authorization_g1/main_full81_authorization.json")
        self.assertIn(auth.SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH, auth.SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM)
        self.assertNotIn(g1, auth.SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM)
        self.assertIn(R8_GEN.lineage_id, auth.REJECTED_LINEAGE_IDS)
        self.assertIn(R8_GEN.lineage_id, auth.SUPERSEDED_LINEAGE_IDS_THIS_MECHANISM)
        self.assertIn(R8_GEN.candidate_id, auth.SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM)
        self.assertEqual(bundle.MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH, g1)

    def test_the_published_r3_and_r2_authorizations_are_untouched(self) -> None:
        for relative in auth.SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM:
            with self.subTest(path=relative):
                tracked, _ = lc.is_tracked_and_clean(ROOT, relative)
                self.assertTrue(tracked)
                self.assertEqual(lc.blob_sha256_at(ROOT, "HEAD", relative), lc.sha256_file(ROOT / relative))

    def test_r3_bytes_can_never_authorize_g1(self) -> None:
        r3 = json.loads((ROOT / auth.SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH).read_text(encoding="utf-8"))
        fixture = G1Fixture(stage="promote")
        try:
            for record in (auth.SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH, auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()):
                with self.subTest(record=record):
                    with self.assertRaises(auth.Full81AuthorizationError) as caught:
                        auth.validate_authorization_payload(
                            fixture.root, r3, record_relative=record,
                            lifecycle=fixture.resolve_lifecycle(),
                        )
                    self.assertIn(
                        caught.exception.status,
                        {
                            "FULL81_AUTHORIZATION_SUPERSEDED_GENERATION_PATH_REJECTED",
                            "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
                        },
                    )
            fixture.write(auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(), r3)
            fixture.commit("fixture: r3 bytes at the G1 slot")
            resolved = fixture.resolve_scope()
            self.assertEqual(resolved["authorization_overlay"], auth.PRESENT_INVALID)
            self.assertEqual(resolved["rejected_status"], "FULL81_AUTHORIZATION_LINEAGE_REJECTED")
        finally:
            fixture.dispose()


# ---------------------------------------------------------------------------
# F. The G1 execution-authorization guard
# ---------------------------------------------------------------------------


class ExecutionGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = G1Fixture(stage="execution")
        cls.lifecycle = cls.fixture.resolve_lifecycle()
        cls.scope = auth.resolve_full81_authorization(cls.fixture.root, cls.lifecycle)
        cls.lawful = cls.fixture.lawful_execution_authorization()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.dispose()

    def rejected(self, payload: Mapping[str, Any], status: str, **kwargs: Any) -> None:
        with self.assertRaises(auth.Full81AuthorizationError) as caught:
            self.fixture.validate_execution(payload, lifecycle=kwargs.pop("lifecycle", self.lifecycle), **kwargs)
        self.assertEqual(caught.exception.status, status)

    def mutated(self, **changes: Any) -> dict[str, Any]:
        payload = copy.deepcopy(self.lawful)
        payload.update(changes)
        return payload

    def test_a_complete_lawful_chain_is_granted_only_in_the_fixture(self) -> None:
        self.assertEqual(self.scope["full81_authorization_status"], auth.AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT)
        state = auth.resolve_full81_execution_authorization(self.fixture.root, self.lifecycle, self.scope)
        self.assertEqual(state["execution_authorization_status"], auth.AUTHORIZED_FOR_FULL81_EXECUTION, state.get("execution_blocked_reason"))
        with patch.object(auth, "REPOSITORY_ROOT", self.fixture.root):
            granted = auth.require_full81_execution_authorization(self.scope)
        self.assertEqual(granted["execution_authorization_overlay"], "PRESENT_VALID")
        self.assertEqual(granted["authorizes"], [auth.EXECUTION_AUTHORIZED_ACT])
        self.assertEqual(granted["implementation_identity_digest"], self.fixture.live_digest)
        # The real repository is never moved by the fixture.
        if not (ROOT / auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH).exists():
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(self.scope)
            self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")

    def test_the_guard_requires_a_supplied_scope_authorization(self) -> None:
        with patch.object(auth, "REPOSITORY_ROOT", self.fixture.root):
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                auth.require_full81_execution_authorization(None)
        self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")
        self.assertIn("FULL81_EXECUTION_INPUT_AUTHORITY_PASS", str(caught.exception))

    def test_envelope_generation_and_stale_authority_fail(self) -> None:
        self.rejected(self.mutated(artifact_type=auth.AUTHORIZATION_ARTIFACT_TYPE), "FULL81_EXECUTION_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH")
        self.rejected(self.mutated(schema_version="iris-thesis-full81-authorization-v2"), "FULL81_EXECUTION_AUTHORIZATION_SCHEMA_MISMATCH")
        for field in auth.EXECUTION_AUTHORIZATION_REQUIRED_FIELDS[2:]:
            with self.subTest(missing=field):
                payload = copy.deepcopy(self.lawful)
                payload.pop(field)
                self.rejected(payload, "FULL81_EXECUTION_AUTHORIZATION_SCHEMA_INVALID")
        self.rejected(self.mutated(candidate_id="CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R2"), "FULL81_EXECUTION_AUTHORIZATION_GENERATION_MISMATCH")
        self.rejected(
            self.mutated(lineage_id=R8_GEN.lineage_id, candidate_id=R8_GEN.candidate_id),
            "FULL81_EXECUTION_AUTHORIZATION_STALE_HISTORICAL_AUTHORITY_REJECTED",
        )
        self.rejected(
            self.lawful,
            "FULL81_EXECUTION_AUTHORIZATION_STALE_HISTORICAL_AUTHORITY_REJECTED",
            record_relative=auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        )

    def test_scope_of_what_is_authorized_is_closed(self) -> None:
        for change in (
            {"execution_authorization_status": "PENDING"},
            {"authorizes": [auth.EXECUTION_AUTHORIZED_ACT, "A2_VARIABLE_FLOOR"]},
            {"case_set": "core-three"},
            {"authorizes_a2": True},
            {"authorizes_sensitivity_solves": True},
            {"restart_policy": "RESUME_PARTIAL"},
            {"required_execution_interlock_flags": ["--execute-production"]},
            {"a2_excluded": False},
        ):
            with self.subTest(change=change):
                status = (
                    "FULL81_EXECUTION_AUTHORIZATION_STATUS_NOT_GRANTED"
                    if "execution_authorization_status" in change
                    else "FULL81_EXECUTION_AUTHORIZATION_SCOPE_INVALID"
                )
                self.rejected(self.mutated(**change), status)

    def test_a_candidate_only_or_non_frozen_lifecycle_fails(self) -> None:
        candidate_only = G1Fixture(stage="package")
        try:
            # A genuinely candidate-only G1 lifecycle, whatever the real phase.
            candidate_lifecycle = candidate_only.resolve_lifecycle()
            self.assertEqual(candidate_lifecycle["generation_id"], GEN.generation_id)
            self.assertEqual(candidate_lifecycle["accepted_lifecycle_overlay"], "ABSENT")
            self.assertFalse(lc.is_frozen(candidate_lifecycle))
            non_frozen = [
                ("absent", lc.absent_lifecycle()),
                ("candidate_only_g1", candidate_lifecycle),
                ("optimistic_field", {"production_authority_freeze_status": "FROZEN"}),
            ]
            # G1: phase-aware, from the source contract.  The real lifecycle is
            # a candidate-phase lifecycle only until Phase C publishes the
            # accepted-lifecycle record; from then on it must be a VALID frozen
            # acceptance of G1 for the live runtime, and is no candidate.
            phase = lc.current_generation_phase(ROOT)
            self.assertEqual(phase["out_of_order_present"], [], phase["phase"])
            real = lc.resolve_u06_lifecycle(ROOT)
            self.assertEqual(real["generation_id"], GEN.generation_id)
            if not phase["presence"]["accepted_lifecycle_record"]:
                self.assertFalse(lc.is_frozen(real))
                non_frozen.append(("real_candidate_phase", real))
            else:
                self.assertEqual(real["accepted_lifecycle_overlay"], "PRESENT_VALID", real.get("freeze_blocked_reason"))
                self.assertTrue(lc.is_frozen(real))
                lc.require_frozen_lifecycle_against_live_implementation(ROOT, real)
            for label, lifecycle in non_frozen:
                with self.subTest(lifecycle=label):
                    self.rejected(self.lawful, "FULL81_EXECUTION_AUTHORIZATION_LIFECYCLE_NOT_FROZEN", lifecycle=lifecycle)
            state = auth.resolve_full81_execution_authorization(candidate_only.root)
            self.assertEqual(state["execution_authorization_overlay"], auth.ABSENT)
            candidate_only.write(auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(), self.lawful)
            candidate_only.commit("fixture: execution record over a candidate-only G1")
            state = auth.resolve_full81_execution_authorization(candidate_only.root)
            self.assertEqual(state["execution_authorization_overlay"], auth.PRESENT_INVALID)
            self.assertEqual(state["rejected_status"], "FULL81_EXECUTION_AUTHORIZATION_LIFECYCLE_NOT_FROZEN")
        finally:
            candidate_only.dispose()

    def test_wrong_runtime_digest_and_lifecycle_binding_fail(self) -> None:
        self.rejected(self.mutated(implementation_identity_digest="1" * 64), "FULL81_EXECUTION_AUTHORIZATION_RUNTIME_DIGEST_DRIFT")
        self.rejected(
            self.mutated(production_authority_accepted_lifecycle_record={
                "path": R8_GEN.accepted_lifecycle_record_path,
                "sha256": lc.sha256_file(self.fixture.root / R8_GEN.accepted_lifecycle_record_path),
            }),
            "FULL81_EXECUTION_AUTHORIZATION_LIFECYCLE_BINDING_INVALID",
        )
        self.rejected(
            self.mutated(production_authority_publication_commit=self.fixture.commits["package"]),
            "FULL81_EXECUTION_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
        )

    def test_wrong_or_stale_scope_authorization_fails(self) -> None:
        r3 = auth.SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH
        self.rejected(
            self.mutated(scope_authorization={"path": r3, "sha256": lc.sha256_file(ROOT / r3)}),
            "FULL81_EXECUTION_AUTHORIZATION_STALE_HISTORICAL_AUTHORITY_REJECTED",
        )
        self.rejected(
            self.mutated(scope_authorization={"path": auth.AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(), "sha256": "2" * 64}),
            "FULL81_EXECUTION_AUTHORIZATION_SCOPE_AUTHORIZATION_INVALID",
        )
        self.rejected(
            self.lawful,
            "FULL81_EXECUTION_AUTHORIZATION_SCOPE_AUTHORIZATION_INVALID",
            scope_authorization=auth.absent_authorization(),
        )
        no_scope = G1Fixture(stage="promote")
        try:
            payload = copy.deepcopy(self.lawful)
            with self.assertRaises(auth.Full81AuthorizationError) as caught:
                no_scope.validate_execution(payload)
            self.assertIn(
                caught.exception.status,
                {
                    "FULL81_EXECUTION_AUTHORIZATION_LIFECYCLE_BINDING_INVALID",
                    "FULL81_EXECUTION_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
                    "FULL81_EXECUTION_AUTHORIZATION_SCOPE_AUTHORIZATION_INVALID",
                },
            )
        finally:
            no_scope.dispose()

    def test_wrong_or_missing_no_solve_preflight_evidence_fails(self) -> None:
        self.rejected(
            self.mutated(no_solve_preflight_evidence={"path": auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix(), "sha256": "3" * 64}),
            "FULL81_EXECUTION_AUTHORIZATION_PREFLIGHT_EVIDENCE_INVALID",
        )
        self.rejected(
            self.mutated(no_solve_preflight_publication_commit=self.fixture.commits["scope"]),
            "FULL81_EXECUTION_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
        )
        evidence = self.fixture.read_json(auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix())
        for name, change in (
            ("nonzero_counters", {"execution_counters": {"model_constructions": 1, "optimization_calls": 1, "economic_evaluations": 0}}),
            ("not_full81", {"case_set": "core-three"}),
            ("not_pass", {"status": "NOT_AUTHORIZED"}),
            ("wrong_runner", {"runner_version": "v7.4-main-full81-no-solve-preflight-runner-2026-10-02-candidate-r2"}),
            ("wrong_generation", {"production_authority_generation_id": R8_GEN.generation_id}),
            ("eighty_cases", {"selected_case_count": 80}),
        ):
            with self.subTest(evidence=name):
                bad = copy.deepcopy(evidence)
                bad.update(change)
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth._validate_no_solve_preflight_evidence(
                        self.fixture.root, bad, live_digest=self.fixture.live_digest
                    )
                self.assertEqual(caught.exception.status, "FULL81_EXECUTION_AUTHORIZATION_PREFLIGHT_EVIDENCE_INVALID")
        with self.assertRaises(auth.Full81AuthorizationError):
            auth._validate_no_solve_preflight_evidence(self.fixture.root, evidence, live_digest="4" * 64)

    def test_wrong_runner_universe_or_inputs_fail(self) -> None:
        runner = copy.deepcopy(self.lawful["target_runner"])
        for change in ({"sha256": "5" * 64}, {"version": "v7.4-other"}, {"path": "scripts/19b_run_final_layer_a_81_cases.py"}):
            with self.subTest(runner=change):
                self.rejected(self.mutated(target_runner={**runner, **change}), "FULL81_EXECUTION_AUTHORIZATION_RUNNER_MISMATCH")
        for change in ({"case_count": 80}, {"alpha_universe": [0.6]}, {"beta_universe_h": [4, 5]}, {"case_count": True}):
            with self.subTest(universe=change):
                self.rejected(self.mutated(**change), "FULL81_EXECUTION_AUTHORIZATION_CASE_UNIVERSE_MISMATCH")
        self.rejected(self.mutated(solver_parameter_fingerprint="6" * 64), "FULL81_EXECUTION_AUTHORIZATION_SOLVER_FINGERPRINT_MISMATCH")
        inputs = dict(self.lawful["execution_input_authority"])
        inputs[next(iter(inputs))] = "7" * 64
        self.rejected(self.mutated(execution_input_authority=inputs), "FULL81_EXECUTION_AUTHORIZATION_EXECUTION_INPUT_MISMATCH")

    def test_malformed_dirty_or_unpublished_records_never_authorize(self) -> None:
        fixture = G1Fixture(stage="evidence")
        try:
            relative = auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
            fixture.write(relative, fixture.lawful_execution_authorization())
            state = auth.resolve_full81_execution_authorization(fixture.root)
            self.assertEqual(state["execution_authorization_overlay"], auth.PRESENT_INVALID)
            self.assertEqual(state["rejected_status"], "FULL81_EXECUTION_AUTHORIZATION_NOT_PUBLISHED")
            fixture.write(relative, "{ not json")
            fixture.commit("fixture: malformed execution record")
            state = auth.resolve_full81_execution_authorization(fixture.root)
            self.assertEqual(state["execution_authorization_overlay"], auth.PRESENT_INVALID)
            self.assertEqual(state["rejected_status"], "FULL81_EXECUTION_AUTHORIZATION_RECORD_INVALID")
            with patch.object(auth, "REPOSITORY_ROOT", fixture.root):
                with self.assertRaises(auth.Full81AuthorizationError) as caught:
                    auth.require_full81_execution_authorization(fixture.resolve_scope())
            self.assertEqual(caught.exception.status, "FULL81_EXECUTION_NOT_AUTHORIZED")
        finally:
            fixture.dispose()

    def test_the_mechanism_knows_no_future_identity(self) -> None:
        source = (ROOT / "src/main_full81_authorization_v7_4.py").read_text(encoding="utf-8")
        lawful_digests = re.findall(r"\b[0-9a-f]{64}\b", source)
        # G1: phase-aware, from the source contract.  A slot exists in the real
        # repository only once the real phase lawfully reached it, and nothing
        # is present out of order.  A present slot is decided VALID by its live
        # resolver, and its identity is never known to the mechanism source.
        phase = lc.current_generation_phase(ROOT)
        self.assertEqual(phase["out_of_order_present"], [], phase["phase"])
        self.assertNotEqual(phase["phase"], lc.G1_PHASE_OUT_OF_ORDER)
        live_digest = lc.implementation_identity_digest(ROOT)
        lifecycle = lc.resolve_u06_lifecycle(ROOT)
        scope = auth.resolve_full81_authorization(ROOT, lifecycle)
        for key, path in (
            ("main_full81_execution_authorization", auth.EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH),
            ("main_full81_no_solve_preflight_evidence", auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH),
            ("main_full81_scope_authorization", auth.AUTHORIZATION_RECORD_RELATIVE_PATH),
        ):
            with self.subTest(slot=key):
                self.assertEqual(phase["paths"][key], path.as_posix())
                self.assertEqual((ROOT / path).exists(), phase["presence"][key], path)
                if not phase["presence"][key]:
                    continue
                self.assertNotIn(lc.sha256_file(ROOT / path), lawful_digests)
                if key == "main_full81_scope_authorization":
                    self.assertTrue(lc.is_frozen(lifecycle))
                    self.assertEqual(scope["authorization_overlay"], "PRESENT_VALID", scope.get("rejected_status"))
                    self.assertEqual(scope["full81_authorization_status"], auth.AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT)
                elif key == "main_full81_no_solve_preflight_evidence":
                    auth._validate_no_solve_preflight_evidence(
                        ROOT, json.loads((ROOT / path).read_text(encoding="utf-8")), live_digest=live_digest
                    )
                else:
                    state = auth.resolve_full81_execution_authorization(ROOT, lifecycle, scope)
                    self.assertEqual(state["execution_authorization_overlay"], "PRESENT_VALID", state.get("rejected_status"))
                    self.assertEqual(state["execution_authorization_status"], auth.AUTHORIZED_FOR_FULL81_EXECUTION)
        allowed = {
            auth.EXPECTED_ANNUAL_MODEL_SHA256,
            auth.EXPECTED_PARAMETER_REGISTRY_SHA256,
            *(pin.sha256 for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS),
            *re.findall(r"\b[0-9a-f]{64}\b", json.dumps(auth.historical_design_precedent())),
            *re.findall(
                r"\b[0-9a-f]{64}\b",
                auth.__doc__ or "",
            ),
        }
        self.assertEqual(set(lawful_digests) - allowed, set())


# ---------------------------------------------------------------------------
# G. Raw-byte / EOL authority
# ---------------------------------------------------------------------------


class RawByteEolCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.universe = lc.authority_raw_byte_consumer_universe(ROOT)
        cls.coverage = lc.eol_policy_coverage(ROOT)
        cls.rules = lc._parse_eol_policy((ROOT / ".gitattributes").read_text(encoding="utf-8"))

    def test_every_g1_governance_path_is_a_raw_byte_consumer(self) -> None:
        r8_roles = json.loads(
            (ROOT / R8_GEN.accepted_lifecycle_record_path).read_text(encoding="utf-8")
        )["roles"]
        required = {
            *lc.g1_predeclared_governance_paths(GEN).values(),
            *lc.VALIDATION_IDENTITY_PATHS,
            *lc.HISTORICAL_VALIDATION_IDENTITY_PATHS,
            *(pin.relative_path for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS),
            *(entry["path"] for entry in r8_roles.values()),
        }
        missing = sorted(required - set(self.universe))
        self.assertEqual(missing, [])
        self.assertFalse(any(path.startswith("<") for path in self.universe))

    def test_coverage_is_exact(self) -> None:
        self.assertTrue(self.coverage["satisfied"], self.coverage["blocking_reason"])
        self.assertEqual(self.coverage["uncovered"], [])
        self.assertEqual(self.coverage["wrongly_treated"], [])
        self.assertEqual(self.coverage["overreaching_rules"], [])
        self.assertEqual(self.coverage["unused_rules"], [])
        self.assertEqual(self.coverage["universe_path_count"], self.coverage["rule_count"])

    def test_every_rule_is_one_exact_path(self) -> None:
        patterns = [pattern for pattern, _ in self.rules]
        self.assertEqual(len(patterns), len(set(patterns)))
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                self.assertFalse(set(pattern) & set("*?[]!"))
                self.assertTrue(pattern == ".gitattributes" or "/" in pattern)

    def test_canonical_non_lf_paths_stay_byte_preserving(self) -> None:
        for relative in lc.CANONICAL_NON_LF_AUTHORITY_PATHS:
            entry = self.coverage["entries"][relative]
            self.assertTrue(set(entry["rule_attributes"]) & {"-text", "binary"})

    def test_the_future_evidence_slot_preserves_bytes_in_either_eol_form(self) -> None:
        relative = auth.NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix()
        rule = lc.effective_eol_rule(self.rules, relative)
        self.assertIsNotNone(rule)
        self.assertIn("-text", rule[1])

    def test_coverage_fails_closed_without_a_rule(self) -> None:
        fixture = G1Fixture(stage="package")
        try:
            policy = fixture.root / ".gitattributes"
            text = policy.read_text(encoding="utf-8")
            target = GEN.candidate_change_ledger_path
            kept = "\n".join(line for line in text.split("\n") if not line.startswith(target + " "))
            self.assertNotEqual(kept, text)
            policy.write_text(kept, encoding="utf-8", newline="\n")
            report = lc.eol_policy_coverage(fixture.root)
            self.assertFalse(report["satisfied"])
            self.assertIn(target, report["uncovered"])
        finally:
            fixture.dispose()


# ---------------------------------------------------------------------------
# H. The three G1 identities
# ---------------------------------------------------------------------------


class IdentityAxesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.axes = lc.g1_identity_axes(ROOT)

    def test_identities_are_deterministic_and_disjoint(self) -> None:
        again = lc.g1_identity_axes(ROOT)
        for cls_name in lc.G1_IDENTITY_CLASSES:
            self.assertEqual(self.axes[cls_name]["digest"], again[cls_name]["digest"])
        self.assertTrue(self.axes["member_sets_disjoint"])
        self.assertEqual(self.axes[lc.G1_IDENTITY_CLASS_RUNTIME]["member_count"], 21)
        self.assertEqual(self.axes[lc.G1_IDENTITY_CLASS_VALIDATION]["member_count"], 9)
        self.assertEqual(
            self.axes[lc.G1_IDENTITY_CLASS_RUNTIME]["digest"], lc.implementation_identity_digest(ROOT)
        )
        shuffled = dict(reversed(list(lc.validation_identity_strict(ROOT).items())))
        self.assertEqual(lc.canonical_identity_digest(shuffled), lc.validation_identity_digest(ROOT))

    def test_governance_identity_is_derived_from_runtime_pin_tables(self) -> None:
        pinned = {pin.relative_path for pin in bundle.all_pins()} | {
            pin.relative_path for pin in auth.FULL81_EXECUTION_INPUT_AUTHORITY_PINS
        }
        expected = pinned - set(lc.ACCEPTED_IMPLEMENTATION_PATHS) - set(lc.VALIDATION_IDENTITY_PATHS)
        self.assertEqual(set(lc.governance_authority_identity_paths()), expected)
        for path in (
            ".gitattributes",
            "docs/research_framework_v7_4_2026-09-26_r2.md",
            "docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md",
            "data/reference/parameter_registry_v7_2.csv",
            "data/reference/production_economic_interface_v7_2.json",
        ):
            self.assertIn(path, expected)

    def test_runtime_validation_coupling_is_exactly_declared(self) -> None:
        from src import production_successor_stack_v7_3 as stack

        coupling = lc.g1_intentional_runtime_validation_coupling()
        declared = {entry["path"] for entry in coupling}
        bundle_pinned = {pin.relative_path for pin in bundle.all_pins()} & set(lc.VALIDATION_IDENTITY_PATHS)
        stack_pinned = {
            relative.as_posix()
            for relative, _ in stack.ADDITIONAL_AUTHORITY_FILES.values()
            if relative.as_posix().startswith("tests/")
        }
        self.assertEqual(set(lc.G1_STACK_PINNED_VALIDATION_PATHS), stack_pinned)
        self.assertEqual(declared, bundle_pinned | stack_pinned)
        for entry in coupling:
            self.assertEqual(entry["coupling"], lc.INTENTIONAL_RUNTIME_VALIDATION_COUPLING)

    def test_historical_validation_suites_are_retained_byte_identical(self) -> None:
        for relative in lc.HISTORICAL_VALIDATION_IDENTITY_PATHS:
            with self.subTest(path=relative):
                self.assertNotIn(relative, lc.VALIDATION_IDENTITY_PATHS)
                self.assertEqual(lc.blob_sha256_at(ROOT, "HEAD", relative), lc.sha256_file(ROOT / relative))
        self.assertIn("tests/test_21i_main_full81_preflight_authorization_guard.py", lc.VALIDATION_IDENTITY_PATHS)
        self.assertIn("tests/test_fullstack_01_execution_input_authority.py", lc.VALIDATION_IDENTITY_PATHS)


# ---------------------------------------------------------------------------
# I. Acyclic binding
# ---------------------------------------------------------------------------


class AcyclicBindingTests(unittest.TestCase):
    def test_no_runtime_or_policy_file_embeds_a_downstream_identity(self) -> None:
        overlay = (ROOT / "src/production_authority_lifecycle_u06.py").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", overlay), [])
        # The policy's RULES name paths only (its comments may cite history).
        for pattern, attributes in lc._parse_eol_policy(
            (ROOT / ".gitattributes").read_text(encoding="utf-8")
        ):
            self.assertEqual(re.findall(r"[0-9a-f]{64}", " ".join((pattern, *attributes))), [])
        runtime_digest = lc.implementation_identity_digest(ROOT)
        bundle_sha = lc.sha256_file(ROOT / "src/production_authority_bundle_v7_4.py")
        for relative in (*lc.ACCEPTED_IMPLEMENTATION_PATHS, *lc.VALIDATION_IDENTITY_PATHS, ".gitattributes"):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_bytes()
                self.assertNotIn(runtime_digest.encode(), text)
                self.assertNotIn(bundle_sha.encode(), text)
        self.assertNotIn(
            "src/production_authority_bundle_v7_4.py",
            {pin.relative_path for pin in bundle.all_pins()},
        )

    def test_the_real_candidate_package_is_valid_when_present(self) -> None:
        manifest = ROOT / GEN.candidate_manifest_path
        if not manifest.is_file():
            # Candidate phase before packaging: the checkpoint may not exist
            # without the manifest, and the absent manifest binds nothing.
            self.assertFalse((ROOT / GEN.candidate_checkpoint_path).exists())
            entry = lc.durable_publication_requirements(ROOT)["entries"][
                GEN.candidate_checkpoint_path
            ]
            self.assertIsNone(entry["expected_sha256"])
            self.assertFalse(entry["live_content_matches_canonical"])
            return
        report = lc.validate_g1_candidate_manifest_contract(
            ROOT, mode=lc.CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE
        )
        self.assertEqual(report["structural_identity_count"], 0)
        raw = manifest.read_bytes()
        self.assertNotIn(lc.sha256_file(manifest).encode(), raw)
        ledger = (ROOT / str(GEN.candidate_change_ledger_path)).read_bytes()
        for later in (GEN.candidate_checkpoint_path, GEN.candidate_manifest_path, str(GEN.candidate_change_ledger_path)):
            self.assertNotIn(lc.sha256_file(ROOT / later).encode(), ledger)


class NoSolveSurfaceTests(unittest.TestCase):
    def test_authority_modules_contain_no_solver_entry_point(self) -> None:
        forbidden = {"optimize", "optimizeAsync", "optimizeBatch", "tune"}
        for relative in (
            "src/production_authority_lifecycle_u06.py",
            "src/main_full81_authorization_v7_4.py",
            "src/production_authority_bundle_v7_4.py",
        ):
            with self.subTest(path=relative):
                tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
                calls = [
                    node for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in forbidden
                ]
                self.assertEqual(calls, [])
                self.assertNotIn("import gurobipy", (ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
