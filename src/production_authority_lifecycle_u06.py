"""U-06 R3 accepted-lifecycle overlay for V7.4 production authority.

Audit history this module answers to
------------------------------------
``R1`` — independent audit ``FAIL``, finding ``F-01``: the gate could reach
``PRODUCTION_AUTHORITY_FROZEN`` once candidate bytes were merely committed and
pushed.  ``R2`` added a lifecycle overlay, and then received
``NO-GO — CRITICAL GOVERNANCE DEFECT``:

``A-01`` (CRITICAL)
    Arbitrary unrelated tracked / clean / hash-correct historical artifacts
    could satisfy the five lifecycle roles and produce a freeze.  R2 proved only
    **file identity** (path + SHA-256 + tracked + clean) and never **artifact
    role authenticity**.

``A-02`` (MAJOR)
    The accepted implementation identity covered seven files and omitted real
    runtime-loaded production dependencies.

``A-03`` (MAJOR)
    ``publication_commit`` only had to be some ancestor of ``HEAD``, which does
    not prove the claimed artifacts were published *in that commit*.

Neither ``F-01`` nor ``A-01``–``A-03`` is closed by this module existing.  This
module is a **remediation implementation**; closure requires a fresh independent
audit.

The R3 principle: identity is not authenticity
----------------------------------------------
A path, a digest, and a clean Git status say *which bytes* a file has.  They say
nothing about whether that file **is** the U-06 R3 independent audit, the U-06 R3
acceptance closure, its manifest, or its re-freeze authority.  So every lifecycle
role here must additionally prove, mechanically:

* ``artifact_type`` — a role-specific type string;
* ``schema_version`` — a role-specific schema identity;
* ``lineage_id`` — exactly :data:`LINEAGE_ID`;
* ``target_candidate_id`` — exactly :data:`R3_CANDIDATE_ID`;
* the exact R3 candidate checkpoint and manifest identities, cross-checked
  against live bytes at the fixed R3 candidate paths;
* an ``implementation_identity_digest`` equal to the live digest over the audited
  runtime production dependency surface;
* for the later roles, the exact identities of the **earlier** roles, so the
  chain cannot be assembled from five individually plausible but unrelated
  files.

Boolean self-labels are never trusted on their own: every claimed identity is
re-resolved from live bytes, and every claimed publication is re-proved from Git.

Five independent states, none implying another
----------------------------------------------
``PRODUCTION_AUTHORITY_ALIGNMENT_STATUS``  (base bundle)   implementation aligned
``U06_INDEPENDENT_AUDIT_STATUS``           (here)          audit outcome
``U06_ACCEPTANCE_STATUS``                  (here)          acceptance / closure
``PRODUCTION_AUTHORITY_FREEZE_STATUS``     (here)          freeze
``MAIN_FULL81_AUTHORIZATION_STATUS``       (base bundle)   Full81 authorization

A frozen production authority still does not authorize Main Full81.

Nothing accepted exists yet
---------------------------
No lifecycle artifact named below exists, and **no digest for any future
artifact is hard-coded, reserved, or stubbed anywhere in this module**.  Only
the lineage/schema/type identifiers and the fixed R3 candidate paths are
hard-coded, which is what makes substitution detectable.  The overlay therefore
resolves to ``ABSENT`` / ``NOT_FROZEN`` and the production gate fails closed.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.production_input_authority_v7_3 import sha256_file


LIFECYCLE_MODULE_VERSION = "v7.4-u06-accepted-lifecycle-overlay-2026-10-02-r3"

#: The one stable lineage identity every R3 lifecycle artifact must declare.
#: Hard-coding this is the point: it is the anchor that makes an unrelated
#: artifact detectably unrelated.
LINEAGE_ID = "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3"

#: The candidate this lineage is about.
R3_CANDIDATE_ID = "U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R3"

#: Fixed R3 candidate artifact paths.  A lifecycle role may not nominate some
#: other file as "the candidate".
R3_CANDIDATE_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02.md"
)
R3_CANDIDATE_MANIFEST_PATH = (
    "results/provenance/"
    "u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02/"
    "alignment_manifest.json"
)

#: Where a FUTURE accepted-lifecycle record must live.  Absent today.
ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH = Path(
    "results/provenance/u_06_v7_4_production_authority_accepted_lifecycle_r3/"
    "accepted_lifecycle_record.json"
)

#: Upstream whose head must equal HEAD before any freeze.
EXPECTED_UPSTREAM = "origin/thesis-v7"


# ---------------------------------------------------------------------------
# Role contracts (§6 of the remediation brief)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoleContract:
    """Machine-readable contract one lifecycle role must satisfy."""

    role: str
    artifact_type: str
    schema_version: str
    #: Earlier roles whose exact identity this role must itself bind.
    binds_roles: tuple[str, ...]
    #: Must this record declare the candidate manifest identity?  The
    #: implementation-candidate role IS that manifest, so it does not (an
    #: artifact never declares its own digest; the validator hashes it).
    declares_candidate_manifest: bool
    #: Extra required fields, documented for a future author.
    required_fields: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "artifact_type": self.artifact_type,
            "schema_version": self.schema_version,
            "binds_roles": list(self.binds_roles),
            "declares_candidate_manifest": self.declares_candidate_manifest,
            "required_fields": list(self.required_fields),
        }


_SCHEMA_PREFIX = "iris-thesis-u06-r3-"

ROLE_CONTRACTS: Mapping[str, RoleContract] = {
    "implementation_candidate": RoleContract(
        role="implementation_candidate",
        artifact_type="U06_IMPLEMENTATION_CANDIDATE",
        schema_version=_SCHEMA_PREFIX + "implementation-candidate-v1",
        binds_roles=(),
        declares_candidate_manifest=False,
        required_fields=("candidate_checkpoint", "implementation_identity_digest"),
    ),
    "independent_audit_pass": RoleContract(
        role="independent_audit_pass",
        artifact_type="U06_INDEPENDENT_AUDIT_PASS",
        schema_version=_SCHEMA_PREFIX + "independent-audit-pass-v1",
        binds_roles=("implementation_candidate",),
        declares_candidate_manifest=True,
        required_fields=(
            "verdict",
            "blocking_critical",
            "blocking_major",
            "independent_audit",
            "candidate_author_is_not_self_accepting",
        ),
    ),
    "acceptance_closure": RoleContract(
        role="acceptance_closure",
        artifact_type="U06_ACCEPTANCE_CLOSURE",
        schema_version=_SCHEMA_PREFIX + "acceptance-closure-v1",
        binds_roles=("implementation_candidate", "independent_audit_pass"),
        declares_candidate_manifest=True,
        required_fields=("acceptance_status", "audit_publication_commit"),
    ),
    "acceptance_manifest": RoleContract(
        role="acceptance_manifest",
        artifact_type="U06_ACCEPTANCE_MANIFEST",
        schema_version=_SCHEMA_PREFIX + "acceptance-manifest-v1",
        binds_roles=(
            "implementation_candidate",
            "independent_audit_pass",
            "acceptance_closure",
        ),
        declares_candidate_manifest=True,
        required_fields=("acceptance_status",),
    ),
    "production_authority_re_freeze": RoleContract(
        role="production_authority_re_freeze",
        artifact_type="U06_PRODUCTION_AUTHORITY_RE_FREEZE",
        schema_version=_SCHEMA_PREFIX + "production-authority-re-freeze-v1",
        binds_roles=(
            "implementation_candidate",
            "independent_audit_pass",
            "acceptance_closure",
            "acceptance_manifest",
        ),
        declares_candidate_manifest=True,
        required_fields=(
            "production_authority_status_intended",
            "authorizes_main_full81",
            "acceptance_publication_commit",
        ),
    ),
}

#: Role order is the lifecycle order; later roles bind earlier ones.
REQUIRED_ACCEPTED_ROLES: tuple[str, ...] = tuple(ROLE_CONTRACTS)

ACCEPTED_LIFECYCLE_ARTIFACT_TYPE = "U06_ACCEPTED_LIFECYCLE"
LIFECYCLE_RECORD_SCHEMA_VERSION = _SCHEMA_PREFIX + "accepted-lifecycle-v1"

#: Roles a candidate may never fill for itself.
NON_SELF_ACCEPTABLE_ROLES: tuple[str, ...] = tuple(
    role for role in REQUIRED_ACCEPTED_ROLES if role != "implementation_candidate"
)

#: Superseded candidate lineages/artifacts. A lifecycle role naming any of them
#: is rejected: R1 failed and R2 is NO-GO, and neither may be revived.
SUPERSEDED_CANDIDATE_IDS: tuple[str, ...] = (
    "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE",
    "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R2",
)

CANDIDATE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_2026-10-02.md",
    "results/provenance/u_06_v7_4_production_authority_alignment_candidate_2026-10-02/"
    "alignment_manifest.json",
    "docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02.md",
    "results/provenance/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02/"
    "alignment_manifest.json",
    R3_CANDIDATE_CHECKPOINT_PATH,
    R3_CANDIDATE_MANIFEST_PATH,
)

#: Directory prefixes that can never hold an acceptance-decision artifact.
NON_GOVERNANCE_PREFIXES: tuple[str, ...] = ("src/", "scripts/", "tests/")


# ---------------------------------------------------------------------------
# A-02: the audited production runtime dependency surface
# ---------------------------------------------------------------------------

#: Every module actually imported, dynamically loaded, or executed on a
#: production path, reconstructed by tracing the real entrypoints rather than
#: assuming a list.  Entrypoints traced: ``scripts/21b``, ``scripts/21c``,
#: ``scripts/21d`` (EOB / Layer A / Main Full81) and ``scripts/21e``.  Followed:
#: real imports (including function-level), ``__import__`` arguments, and paths
#: handed to ``_load_helper`` / ``_load_module`` / ``load_module`` / ``load`` /
#: ``spec_from_file_location``.  Provenance *citations* (lineage lists, pin
#: tables) were deliberately not followed and are not listed here.
RUNTIME_PRODUCTION_DEPENDENCY_PATHS: tuple[str, ...] = (
    # production entrypoints
    "scripts/21b_preflight_v7_3_eob_successor.py",
    "scripts/21c_preflight_v7_3_layer_a_successor.py",
    "scripts/21d_preflight_v7_3_final81_successor.py",
    "scripts/21e_preflight_v7_4_production_authority_alignment.py",
    # authority layer
    "src/production_successor_stack_v7_3.py",
    "src/production_authority_bundle_v7_4.py",
    "src/production_authority_lifecycle_u06.py",
    "src/production_input_authority_v7_3.py",
    # loaded by the stack through STEP2E1_PREFLIGHT
    "scripts/21a_preflight_v7_3_production_routing.py",
    # scientific / execution layer reached by NativeProductionBackend and by
    # the Step-2E-1 preflight
    "src/annual_design_model_v7_2.py",
    "src/rainflow_validation_v7_2.py",
    "scripts/09_build_valid_outage_start_sets.py",
    "scripts/15d_run_corrected_eob_v7_2.py",
    "scripts/16a_preflight_layer_a_representative_binary_cases.py",
    "scripts/19a_preflight_final_layer_a_81_cases.py",
    "scripts/19b_run_final_layer_a_81_cases.py",
)

#: Not executed on a production path, but required tracked and clean by the
#: gate's own ``verify_protected_methodology``, so a swap would change whether
#: production may run.  Bound by hash for the same reason.
GATE_PROTECTED_DEPENDENCY_PATHS: tuple[str, ...] = (
    "scripts/08_calibrate_kappa.py",
    "scripts/15a_benchmark_eob_charge_discharge_formulations.py",
    "scripts/15b_freeze_production_eob_baseline.py",
    "scripts/15c_validate_production_eob_rainflow.py",
)

#: The accepted implementation identity: what an acceptance is bound to.
ACCEPTED_IMPLEMENTATION_PATHS: tuple[str, ...] = tuple(
    sorted(set(RUNTIME_PRODUCTION_DEPENDENCY_PATHS + GATE_PROTECTED_DEPENDENCY_PATHS))
)

#: Validation identity, tracked separately.  Tests are **not** runtime
#: production authority and must never be confused with it.
VALIDATION_IDENTITY_PATHS: tuple[str, ...] = (
    "tests/test_21a_v7_3_production_routing_preflight.py",
    "tests/test_21b_21d_v7_3_production_successor_stack.py",
    "tests/test_21e_v7_4_production_authority_bundle.py",
    "tests/test_21f_u06_accepted_lifecycle_gate.py",
    "tests/test_21g_u06_r3_substitution_attacks.py",
)

#: Retained for continuity of the R2 name; it is now the full accepted surface.
IMPLEMENTATION_CANDIDATE_SURFACE = ACCEPTED_IMPLEMENTATION_PATHS


# --- Pre-acceptance constants -------------------------------------------------
# Current factual pre-acceptance state only.  Every emitted field is read from
# the resolved lifecycle mapping, which replaces all of these with
# record-derived values once a valid accepted-lifecycle record exists.

PRE_ACCEPTANCE_ALIGNMENT_STATUS = "CANDIDATE"
PRE_ACCEPTANCE_AUDIT_STATUS = "R1_FAILED_R2_NO_GO_R3_PENDING"
PRE_ACCEPTANCE_ACCEPTANCE_STATUS = "NOT_ACCEPTED"
PRE_ACCEPTANCE_OVERLAY_STATUS = "ABSENT"
PRE_ACCEPTANCE_FREEZE_STATUS = "NOT_FROZEN"

ACCEPTED_ALIGNMENT_STATUS = "ACCEPTED"
ACCEPTED_AUDIT_STATUS = "PASS"
ACCEPTED_ACCEPTANCE_STATUS = "CLOSED_ACCEPTED"
PRESENT_VALID_OVERLAY_STATUS = "PRESENT_VALID"
PRESENT_INVALID_OVERLAY_STATUS = "PRESENT_INVALID"
FROZEN_STATUS = "FROZEN"

#: Candidate R1 outcome, recorded so the failure is never erased.
CANDIDATE_R1_AUDIT_RECORD = {
    "candidate": "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE",
    "candidate_revision": "R1",
    "independent_audit_verdict": "FAIL_REMEDIATION_REQUIRED",
    "blocking_finding": "F-01",
    "blocking_finding_class": "LIFECYCLE_ANCHORING_DEFECT",
    "blocking_finding_summary": (
        "The live production-authority gate could reach PRODUCTION_AUTHORITY_FROZEN "
        "after candidate implementation bytes were merely committed and pushed, "
        "without mechanically requiring the U-06 independent audit, acceptance "
        "closure, accepted lifecycle / re-freeze record, checkpoint/manifest, or "
        "accepted lifecycle identity."
    ),
    "lifecycle": "IMMUTABLE_HISTORICAL_FAILED_CANDIDATE_PROVENANCE",
    "superseded_by": "R2",
    "f_01_closed": False,
    "f_01_status": (
        "REMEDIATION_TARGET_IMPLEMENTED_CLOSURE_REQUIRES_FRESH_INDEPENDENT_AUDIT"
    ),
}

#: Candidate R2 outcome, recorded so the NO-GO is never erased.
CANDIDATE_R2_AUDIT_RECORD = {
    "candidate": "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R2",
    "candidate_revision": "R2",
    "independent_audit_verdict": "NO_GO_CRITICAL_GOVERNANCE_DEFECT",
    "must_not_be_accepted_closed_frozen_or_committed_as_authority": True,
    "findings": {
        "A-01": {
            "severity": "CRITICAL",
            "summary": (
                "Arbitrary unrelated tracked/clean/hash-correct historical "
                "artifacts could satisfy the five lifecycle roles and produce "
                "PRODUCTION_AUTHORITY_FROZEN."
            ),
            "remediation_status": (
                "REMEDIATION_IMPLEMENTED_PENDING_FRESH_INDEPENDENT_VERIFICATION"
            ),
        },
        "A-02": {
            "severity": "MAJOR",
            "summary": (
                "The seven-file accepted implementation identity omitted actual "
                "runtime-loaded production dependencies."
            ),
            "remediation_status": (
                "REMEDIATION_IMPLEMENTED_PENDING_FRESH_INDEPENDENT_VERIFICATION"
            ),
        },
        "A-03": {
            "severity": "MAJOR",
            "summary": (
                "publication_commit only needed to be an arbitrary HEAD ancestor "
                "and therefore did not prove the claimed lifecycle artifacts were "
                "actually published in that commit."
            ),
            "remediation_status": (
                "REMEDIATION_IMPLEMENTED_PENDING_FRESH_INDEPENDENT_VERIFICATION"
            ),
        },
        "A-04": {
            "severity": "MINOR",
            "summary": "Test-quality weakness.",
            "remediation_status": "PARTIALLY_ADDRESSED_BY_R3_ATTACK_SUITE",
        },
        "A-05": {
            "severity": "MINOR",
            "summary": "LF/CRLF hash portability.",
            "remediation_status": "RECORDED_NOT_REMEDIATED_BY_INSTRUCTION",
        },
        "A-06": {
            "severity": "INFORMATIONAL",
            "summary": "R1 source non-durability.",
            "remediation_status": (
                "R2_SOURCE_PRESERVED_UNDER_R3_PROVENANCE_R1_SOURCE_NOT_RECOVERABLE"
            ),
        },
    },
    "lifecycle": "IMMUTABLE_HISTORICAL_NO_GO_CANDIDATE_PROVENANCE",
    "superseded_by": "R3",
}

#: Statements that must never be collapsed into one another.
LIFECYCLE_DISTINCTIONS = (
    "ZERO_SOLVE_PREFLIGHT_PASS",
    "BASE_AUTHORITY_CANDIDATE_ALIGNED",
    "U06_INDEPENDENT_AUDIT_PASS",
    "U06_ACCEPTANCE_CLOSED_ACCEPTED",
    "U06_PRODUCTION_AUTHORITY_RE_FREEZE",
    "PRODUCTION_AUTHORITY_FROZEN",
    "MAIN_FULL81_AUTHORIZED",
    "MAIN_FULL81_EXECUTED",
)

#: The one lawful ordering.  Each arrow is a separately authorized act, and the
#: three publication phases are what make A-03 provable without a hash cycle.
REQUIRED_LIFECYCLE_SEQUENCE = (
    "IMPLEMENTATION_CANDIDATE",
    "FRESH_INDEPENDENT_AUDIT_PASS",
    "PHASE_A_AUDIT_PUBLICATION_COMMIT",
    "ACCEPTANCE_CLOSURE_AND_ACCEPTANCE_MANIFEST",
    "PHASE_B_ACCEPTANCE_PUBLICATION_COMMIT",
    "PRODUCTION_AUTHORITY_RE_FREEZE_AND_ACCEPTED_LIFECYCLE_RECORD",
    "PHASE_C_LIFECYCLE_PUBLICATION_VERIFIED_FROM_LIVE_GIT",
    "READ_ONLY_FROZEN_AUTHORITY_VERIFICATION",
    "SEPARATE_MAIN_FULL81_AUTHORIZATION",
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class U06LifecycleError(RuntimeError):
    """Fail-closed U-06 accepted-lifecycle error with a stable status."""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def _require(condition: bool, status: str, message: str) -> None:
    if not condition:
        raise U06LifecycleError(status, message)


# ---------------------------------------------------------------------------
# Git helpers (A-03): containment, not mere ancestry
# ---------------------------------------------------------------------------


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=False
    )


def _git_text(root: Path, *args: str) -> str | None:
    done = _git(root, *args)
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "replace").strip()


def blob_sha256_at(root: Path, commit: str, relative: str) -> str | None:
    """SHA-256 of the file's bytes as they exist in `commit`, or None.

    The repository's pin convention is SHA-256 over working-tree bytes.  Git
    stores blobs with LF, and the pinned sources are LF on disk, so the two
    agree today.  If they ever diverge, every check below fails closed rather
    than silently accepting — see the A-05 limitation note.
    """

    done = _git(root, "cat-file", "-e", f"{commit}:{relative}")
    if done.returncode != 0:
        return None
    blob = _git(root, "cat-file", "blob", f"{commit}:{relative}")
    if blob.returncode != 0:
        return None
    return hashlib.sha256(blob.stdout).hexdigest()


def is_tracked_and_clean(root: Path, relative: str) -> tuple[bool, bool]:
    tracked = _git(root, "ls-files", "--error-unmatch", "--", relative).returncode == 0
    if not tracked:
        return False, False
    clean = _git(root, "diff", "--quiet", "HEAD", "--", relative).returncode == 0
    return True, clean


def is_ancestor(root: Path, commit: str, of: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", commit, of).returncode == 0


def last_modifying_commit(root: Path, relative: str) -> str | None:
    return _git_text(root, "rev-list", "-1", "HEAD", "--", relative) or None


def upstream_synchronized(root: Path) -> tuple[bool, str]:
    """HEAD must equal the configured upstream before any freeze."""

    head = _git_text(root, "rev-parse", "HEAD")
    upstream = _git_text(root, "rev-parse", EXPECTED_UPSTREAM)
    if not head or not upstream:
        return False, f"Could not resolve HEAD or {EXPECTED_UPSTREAM}."
    if head != upstream:
        return False, (
            f"HEAD {head} does not equal {EXPECTED_UPSTREAM} {upstream}; an "
            "unpublished HEAD confers no production authority."
        )
    return True, ""


def require_published_in_commit(
    root: Path, commit: str, relative: str, expected_sha256: str, *, label: str
) -> None:
    """Prove `relative` exists **in that exact commit** with `expected_sha256`.

    This is the A-03 fix.  Being "some ancestor of HEAD" is not accepted as
    proof that a file was published there: the blob must be present in that
    commit and must hash to the expected value.
    """

    _require(
        bool(_COMMIT_RE.match(commit)),
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: publication commit is not a full SHA-1: {commit!r}",
    )
    _require(
        is_ancestor(root, commit, "HEAD"),
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: publication commit {commit} is not an ancestor of HEAD.",
    )
    actual = blob_sha256_at(root, commit, relative)
    _require(
        actual is not None,
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: {relative} does not exist in commit {commit}. An ancestor "
        "commit that never contained the artifact is not proof of publication.",
    )
    _require(
        actual == expected_sha256,
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: {relative} exists in commit {commit} but with different bytes: "
        f"expected={expected_sha256}, in-commit={actual}",
    )


def require_published_in_head(
    root: Path, relative: str, expected_sha256: str, *, label: str
) -> None:
    """Phase C: prove the artifact is in HEAD, matches live bytes, and is clean."""

    tracked, clean = is_tracked_and_clean(root, relative)
    _require(
        tracked,
        "U06_LIFECYCLE_NOT_PUBLISHED",
        f"{label}: {relative} is not tracked in Git.",
    )
    _require(
        clean,
        "U06_LIFECYCLE_NOT_PUBLISHED",
        f"{label}: {relative} has working-tree drift against HEAD.",
    )
    in_head = blob_sha256_at(root, "HEAD", relative)
    _require(
        in_head is not None,
        "U06_LIFECYCLE_NOT_PUBLISHED",
        f"{label}: {relative} is not present in the HEAD tree.",
    )
    _require(
        in_head == expected_sha256,
        "U06_LIFECYCLE_NOT_PUBLISHED",
        f"{label}: HEAD blob for {relative} does not match live bytes: "
        f"head={in_head}, live={expected_sha256}",
    )
    introduced = last_modifying_commit(root, relative)
    _require(
        introduced is not None and is_ancestor(root, introduced, EXPECTED_UPSTREAM),
        "U06_LIFECYCLE_NOT_PUBLISHED",
        f"{label}: the commit last modifying {relative} ({introduced}) is not in "
        f"the published ancestry of {EXPECTED_UPSTREAM}.",
    )


# ---------------------------------------------------------------------------
# A-02: live implementation identity and its digest
# ---------------------------------------------------------------------------


def implementation_identity(root: Path) -> dict[str, str]:
    """Live SHA-256 of every accepted implementation path. Missing => raise."""

    root = root.resolve()
    identity: dict[str, str] = {}
    for relative in ACCEPTED_IMPLEMENTATION_PATHS:
        path = root / relative
        _require(
            path.is_file(),
            "U06_IMPLEMENTATION_IDENTITY_INCOMPLETE",
            f"Accepted implementation dependency is missing: {relative}",
        )
        identity[relative] = sha256_file(path)
    return identity


def canonical_identity_digest(identity: Mapping[str, str]) -> str:
    """Stable digest over a {path: sha256} map; order-independent."""

    payload = json.dumps(
        {str(k): str(v) for k, v in identity.items()},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def implementation_identity_digest(root: Path) -> str:
    return canonical_identity_digest(implementation_identity(root))


def validation_identity(root: Path) -> dict[str, str]:
    """Live SHA-256 of the test/validation surface, tracked separately."""

    root = root.resolve()
    out: dict[str, str] = {}
    for relative in VALIDATION_IDENTITY_PATHS:
        path = root / relative
        out[relative] = sha256_file(path) if path.is_file() else ""
    return out


# ---------------------------------------------------------------------------
# Role envelope validation (A-01): authenticity, not just identity
# ---------------------------------------------------------------------------


def _read_json(root: Path, relative: str, *, label: str) -> Mapping[str, Any]:
    path = root / relative
    _require(
        path.is_file(),
        "U06_ROLE_ARTIFACT_MISSING",
        f"{label}: artifact is missing: {relative}",
    )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise U06LifecycleError(
            "U06_ROLE_ARTIFACT_NOT_JSON",
            f"{label}: {relative} is not a machine-readable JSON role record "
            f"({exc}). An arbitrary document cannot fill a lifecycle role.",
        ) from exc
    _require(
        isinstance(payload, Mapping),
        "U06_ROLE_ARTIFACT_NOT_JSON",
        f"{label}: {relative} is not a JSON object.",
    )
    return payload


def _validate_role_path(role: str, relative: str, record_relative: str) -> None:
    normalized = relative.replace("\\", "/").strip()
    _require(
        bool(normalized) and not normalized.startswith("/"),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"Role {role!r} has an unusable path: {relative!r}",
    )
    if role == "implementation_candidate":
        _require(
            normalized == R3_CANDIDATE_MANIFEST_PATH,
            "U06_ROLE_TARGET_MISMATCH",
            f"The implementation-candidate role must be the R3 candidate manifest "
            f"{R3_CANDIDATE_MANIFEST_PATH}; observed {normalized}.",
        )
        return
    _require(
        normalized not in CANDIDATE_ARTIFACT_PATHS,
        "U06_SELF_ACCEPTANCE_REJECTED",
        f"Role {role!r} may not be filled by a candidate artifact: {normalized}",
    )
    _require(
        normalized != record_relative,
        "U06_SELF_ACCEPTANCE_REJECTED",
        f"Role {role!r} may not be filled by the lifecycle record itself.",
    )
    _require(
        not normalized.startswith(NON_GOVERNANCE_PREFIXES),
        "U06_SELF_ACCEPTANCE_REJECTED",
        f"Role {role!r} may not be filled by candidate code or a test fixture: "
        f"{normalized}",
    )


def _declared_identity(
    payload: Mapping[str, Any], field: str, *, label: str
) -> tuple[str, str]:
    entry = payload.get(field)
    _require(
        isinstance(entry, Mapping),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: field {field!r} must be an object with path and sha256.",
    )
    relative = str(entry.get("path", "")).replace("\\", "/").strip()
    digest = str(entry.get("sha256", "")).lower()
    _require(
        bool(relative),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: field {field!r} has no path.",
    )
    _require(
        bool(_SHA256_RE.match(digest)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: field {field!r} has no usable SHA-256.",
    )
    return relative, digest


def _require_live_match(
    root: Path, relative: str, declared: str, *, label: str, field: str
) -> str:
    path = root / relative
    _require(
        path.is_file(),
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: {field} names a file that does not exist: {relative}",
    )
    actual = sha256_file(path)
    _require(
        actual == declared,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: {field} declares SHA-256 {declared} for {relative} but live "
        f"bytes hash to {actual}.",
    )
    return actual


def validate_role_envelope(
    root: Path,
    role: str,
    relative: str,
    payload: Mapping[str, Any],
    *,
    live_digest: str,
) -> dict[str, Any]:
    """Validate the common lineage/type/target envelope of one role record."""

    contract = ROLE_CONTRACTS[role]
    label = f"role {role!r} ({relative})"

    _require(
        payload.get("artifact_type") == contract.artifact_type,
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type must be {contract.artifact_type!r}; observed "
        f"{payload.get('artifact_type')!r}. An unrelated artifact cannot fill "
        "this role.",
    )
    _require(
        payload.get("schema_version") == contract.schema_version,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version must be {contract.schema_version!r}; observed "
        f"{payload.get('schema_version')!r}",
    )
    _require(
        payload.get("lineage_id") == LINEAGE_ID,
        "U06_LINEAGE_MISMATCH",
        f"{label}: lineage_id must be {LINEAGE_ID!r}; observed "
        f"{payload.get('lineage_id')!r}",
    )
    target = payload.get("target_candidate_id")
    _require(
        target not in SUPERSEDED_CANDIDATE_IDS,
        "U06_SUPERSEDED_CANDIDATE_REJECTED",
        f"{label}: target_candidate_id {target!r} names a superseded candidate. "
        "R1 failed its audit and R2 is NO-GO; neither may be revived.",
    )
    _require(
        target == R3_CANDIDATE_ID,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: target_candidate_id must be {R3_CANDIDATE_ID!r}; observed "
        f"{target!r}",
    )

    checkpoint_rel, checkpoint_sha = _declared_identity(
        payload, "candidate_checkpoint", label=label
    )
    _require(
        checkpoint_rel == R3_CANDIDATE_CHECKPOINT_PATH,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_checkpoint must be {R3_CANDIDATE_CHECKPOINT_PATH}; "
        f"observed {checkpoint_rel}",
    )
    _require_live_match(
        root, checkpoint_rel, checkpoint_sha, label=label, field="candidate_checkpoint"
    )

    manifest_sha: str | None = None
    if contract.declares_candidate_manifest:
        manifest_rel, manifest_sha = _declared_identity(
            payload, "candidate_manifest", label=label
        )
        _require(
            manifest_rel == R3_CANDIDATE_MANIFEST_PATH,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: candidate_manifest must be {R3_CANDIDATE_MANIFEST_PATH}; "
            f"observed {manifest_rel}",
        )
        _require_live_match(
            root,
            manifest_rel,
            manifest_sha,
            label=label,
            field="candidate_manifest",
        )

    declared_digest = str(payload.get("implementation_identity_digest", "")).lower()
    _require(
        bool(_SHA256_RE.match(declared_digest)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: implementation_identity_digest is missing or malformed.",
    )
    _require(
        declared_digest == live_digest,
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        f"{label}: implementation_identity_digest {declared_digest} does not match "
        f"the live accepted implementation surface digest {live_digest}. An "
        "acceptance never carries forward to changed production code.",
    )

    missing = [f for f in contract.required_fields if f not in payload]
    _require(
        not missing,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: missing required fields {missing}",
    )

    return {
        "role": role,
        "path": relative,
        "artifact_type": contract.artifact_type,
        "schema_version": contract.schema_version,
        "lineage_id": LINEAGE_ID,
        "target_candidate_id": R3_CANDIDATE_ID,
        "candidate_checkpoint_sha256": checkpoint_sha,
        "candidate_manifest_sha256": manifest_sha,
        "implementation_identity_digest": declared_digest,
    }


def _validate_bound_roles(
    root: Path,
    role: str,
    relative: str,
    payload: Mapping[str, Any],
    resolved: Mapping[str, Mapping[str, Any]],
) -> None:
    """Require this role to bind the exact identity of every earlier role."""

    contract = ROLE_CONTRACTS[role]
    label = f"role {role!r} ({relative})"
    for earlier in contract.binds_roles:
        if earlier == "implementation_candidate":
            # Bound through candidate_checkpoint / candidate_manifest already.
            continue
        field = earlier
        declared_rel, declared_sha = _declared_identity(payload, field, label=label)
        actual = resolved.get(earlier)
        _require(
            actual is not None,
            "U06_ROLE_CHAIN_BROKEN",
            f"{label}: binds {earlier!r} but that role was not resolved.",
        )
        _require(
            declared_rel == actual["path"],
            "U06_ROLE_CHAIN_MISMATCH",
            f"{label}: binds {earlier!r} at {declared_rel}, but the lifecycle "
            f"record supplies that role at {actual['path']}. A chain assembled "
            "from unrelated artifacts is rejected.",
        )
        _require(
            declared_sha == actual["sha256"],
            "U06_ROLE_CHAIN_MISMATCH",
            f"{label}: binds {earlier!r} with SHA-256 {declared_sha}, but the "
            f"resolved role hashes to {actual['sha256']}.",
        )


def validate_role_specifics(
    root: Path,
    role: str,
    relative: str,
    payload: Mapping[str, Any],
    resolved: Mapping[str, Mapping[str, Any]],
) -> None:
    """Role-specific semantics, beyond the shared envelope."""

    label = f"role {role!r} ({relative})"

    if role == "independent_audit_pass":
        _require(
            str(payload.get("verdict")).upper() == "PASS",
            "U06_AUDIT_VERDICT_NOT_PASS",
            f"{label}: verdict must be PASS; observed {payload.get('verdict')!r}",
        )
        for field in ("blocking_critical", "blocking_major"):
            value = payload.get(field)
            _require(
                isinstance(value, int) and not isinstance(value, bool) and value == 0,
                "U06_AUDIT_VERDICT_NOT_PASS",
                f"{label}: {field} must be the integer 0; observed {value!r}",
            )
        _require(
            payload.get("independent_audit") is True,
            "U06_AUDIT_NOT_INDEPENDENT",
            f"{label}: independent_audit must be true.",
        )
        _require(
            payload.get("candidate_author_is_not_self_accepting") is True,
            "U06_SELF_ACCEPTANCE_REJECTED",
            f"{label}: candidate_author_is_not_self_accepting must be true.",
        )

    elif role == "acceptance_closure":
        _require(
            payload.get("acceptance_status") == ACCEPTED_ACCEPTANCE_STATUS,
            "U06_LIFECYCLE_NOT_ACCEPTED",
            f"{label}: acceptance_status must be {ACCEPTED_ACCEPTANCE_STATUS!r}; "
            f"observed {payload.get('acceptance_status')!r}",
        )
        audit = resolved["independent_audit_pass"]
        _require(
            str(payload.get("audit_verdict", "PASS")).upper() == "PASS",
            "U06_AUDIT_VERDICT_NOT_PASS",
            f"{label}: audit_verdict must be PASS.",
        )
        commit = str(payload.get("audit_publication_commit", ""))
        # Phase A: candidate + audit must actually exist in that exact commit.
        require_published_in_commit(
            root,
            commit,
            R3_CANDIDATE_CHECKPOINT_PATH,
            str(payload["candidate_checkpoint"]["sha256"]).lower(),
            label=f"{label} audit_publication_commit",
        )
        require_published_in_commit(
            root,
            commit,
            audit["path"],
            audit["sha256"],
            label=f"{label} audit_publication_commit",
        )

    elif role == "acceptance_manifest":
        _require(
            payload.get("acceptance_status") == ACCEPTED_ACCEPTANCE_STATUS,
            "U06_LIFECYCLE_NOT_ACCEPTED",
            f"{label}: acceptance_status must be {ACCEPTED_ACCEPTANCE_STATUS!r}.",
        )

    elif role == "production_authority_re_freeze":
        _require(
            payload.get("production_authority_status_intended") == FROZEN_STATUS,
            "U06_RE_FREEZE_INVALID",
            f"{label}: production_authority_status_intended must be "
            f"{FROZEN_STATUS!r}; observed "
            f"{payload.get('production_authority_status_intended')!r}",
        )
        _require(
            payload.get("authorizes_main_full81") is False,
            "U06_RE_FREEZE_OVERREACH",
            f"{label}: authorizes_main_full81 must be false. A production-authority "
            "re-freeze never authorizes Main Full81.",
        )
        closure = resolved["acceptance_closure"]
        manifest = resolved["acceptance_manifest"]
        commit = str(payload.get("acceptance_publication_commit", ""))
        # Phase B: closure + manifest must actually exist in that exact commit.
        for bound in (closure, manifest):
            require_published_in_commit(
                root,
                commit,
                bound["path"],
                bound["sha256"],
                label=f"{label} acceptance_publication_commit",
            )


# ---------------------------------------------------------------------------
# Accepted-lifecycle aggregation (§11)
# ---------------------------------------------------------------------------


def validate_accepted_lifecycle_payload(
    root: Path, payload: Mapping[str, Any], *, record_relative: str
) -> dict[str, Any]:
    """Validate an accepted-lifecycle record and its whole role chain.

    Fail-closed, and ordered so the reported status names the real governance
    problem: envelope, then role authenticity, then chain consistency, then
    publication containment.
    """

    root = root.resolve()
    label = f"accepted lifecycle record ({record_relative})"

    _require(
        isinstance(payload, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"{label}: not a JSON object.",
    )
    _require(
        payload.get("artifact_type") == ACCEPTED_LIFECYCLE_ARTIFACT_TYPE,
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type must be {ACCEPTED_LIFECYCLE_ARTIFACT_TYPE!r}.",
    )
    _require(
        payload.get("schema_version") == LIFECYCLE_RECORD_SCHEMA_VERSION,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version must be {LIFECYCLE_RECORD_SCHEMA_VERSION!r}.",
    )
    _require(
        payload.get("lineage_id") == LINEAGE_ID,
        "U06_LINEAGE_MISMATCH",
        f"{label}: lineage_id must be {LINEAGE_ID!r}.",
    )
    _require(
        payload.get("target_candidate_id") == R3_CANDIDATE_ID,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: target_candidate_id must be {R3_CANDIDATE_ID!r}.",
    )
    for field, expected in (
        ("u06_alignment_status", ACCEPTED_ALIGNMENT_STATUS),
        ("u06_independent_audit_status", ACCEPTED_AUDIT_STATUS),
        ("u06_acceptance_status", ACCEPTED_ACCEPTANCE_STATUS),
        ("production_authority_freeze_status", FROZEN_STATUS),
    ):
        _require(
            payload.get(field) == expected,
            "U06_LIFECYCLE_NOT_ACCEPTED",
            f"{label}: {field} must be {expected!r}; observed "
            f"{payload.get(field)!r}",
        )
    _require(
        payload.get("authorizes_main_full81") is False,
        "U06_RE_FREEZE_OVERREACH",
        f"{label}: authorizes_main_full81 must be false.",
    )

    live_digest = implementation_identity_digest(root)
    declared_digest = str(payload.get("implementation_identity_digest", "")).lower()
    _require(
        declared_digest == live_digest,
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        f"{label}: implementation_identity_digest {declared_digest} does not match "
        f"the live digest {live_digest}.",
    )

    roles = payload.get("roles")
    _require(
        isinstance(roles, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"{label}: no roles object.",
    )
    missing = [r for r in REQUIRED_ACCEPTED_ROLES if r not in roles]
    _require(
        not missing,
        "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
        f"{label}: missing required roles {missing}",
    )
    unexpected = sorted(set(roles) - set(REQUIRED_ACCEPTED_ROLES))
    _require(
        not unexpected,
        "U06_LIFECYCLE_RECORD_INVALID",
        f"{label}: unknown roles declared {unexpected}",
    )

    # Pass 1 — structural only, no bytes read. Substitution by location must be
    # detected for EVERY role before any role's content is inspected, so that an
    # earlier role's content failure cannot mask a later role's violation.
    declared_roles: dict[str, tuple[str, str]] = {}
    seen_paths: dict[str, str] = {}
    for role in REQUIRED_ACCEPTED_ROLES:
        entry = roles[role]
        _require(
            isinstance(entry, Mapping),
            "U06_LIFECYCLE_RECORD_INVALID",
            f"{label}: role {role!r} is not an object.",
        )
        relative = str(entry.get("path", "")).replace("\\", "/").strip()
        declared = str(entry.get("sha256", "")).lower()
        _require(
            bool(_SHA256_RE.match(declared)),
            "U06_LIFECYCLE_RECORD_INVALID",
            f"{label}: role {role!r} has no usable SHA-256.",
        )
        _validate_role_path(role, relative, record_relative)
        _require(
            relative not in seen_paths,
            "U06_ROLE_ALIASING_REJECTED",
            f"{label}: roles {seen_paths.get(relative)!r} and {role!r} name the "
            f"same artifact {relative}; one file may not fill two roles.",
        )
        seen_paths[relative] = role
        declared_roles[role] = (relative, declared)

    # Pass 2 — content and role authenticity, in lifecycle order so each role
    # can bind the exact identity of the roles before it.
    resolved: dict[str, dict[str, Any]] = {}
    for role in REQUIRED_ACCEPTED_ROLES:
        relative, declared = declared_roles[role]
        actual = _require_live_match(
            root, relative, declared, label=f"{label} role {role!r}", field="sha256"
        )
        record = _read_json(root, relative, label=f"role {role!r}")
        envelope = validate_role_envelope(
            root, role, relative, record, live_digest=live_digest
        )
        _validate_bound_roles(root, role, relative, record, resolved)
        validate_role_specifics(root, role, relative, record, resolved)
        resolved[role] = {
            "path": relative,
            "sha256": actual,
            **envelope,
        }

    # Pass 3 — the whole chain must agree on lineage, candidate, and identity.
    lineages = {r["lineage_id"] for r in resolved.values()}
    targets = {r["target_candidate_id"] for r in resolved.values()}
    digests = {r["implementation_identity_digest"] for r in resolved.values()}
    checkpoints = {r["candidate_checkpoint_sha256"] for r in resolved.values()}
    _require(
        lineages == {LINEAGE_ID},
        "U06_LINEAGE_MISMATCH",
        f"{label}: roles disagree on lineage_id: {sorted(lineages)}",
    )
    _require(
        targets == {R3_CANDIDATE_ID},
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: roles disagree on target_candidate_id: {sorted(targets)}",
    )
    _require(
        digests == {live_digest},
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        f"{label}: roles disagree on implementation_identity_digest: "
        f"{sorted(digests)}",
    )
    _require(
        len(checkpoints) == 1,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: roles disagree on the candidate checkpoint identity.",
    )

    # Pass 4 — Phase C publication, proved from live Git, not self-declared.
    synced, reason = upstream_synchronized(root)
    _require(synced, "U06_LIFECYCLE_NOT_PUBLISHED", f"{label}: {reason}")
    re_freeze = resolved["production_authority_re_freeze"]
    require_published_in_head(
        root,
        record_relative,
        sha256_file(root / record_relative),
        label=f"{label} phase C",
    )
    require_published_in_head(
        root,
        re_freeze["path"],
        re_freeze["sha256"],
        label=f"{label} phase C re-freeze",
    )
    for role in REQUIRED_ACCEPTED_ROLES:
        entry = resolved[role]
        require_published_in_head(
            root, entry["path"], entry["sha256"], label=f"{label} role {role!r}"
        )

    return {
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
        "lineage_id": LINEAGE_ID,
        "target_candidate_id": R3_CANDIDATE_ID,
        "record_path": record_relative,
        "record_present": True,
        "record_committed": True,
        "record_published": True,
        "self_accepted": False,
        "u06_alignment_status": ACCEPTED_ALIGNMENT_STATUS,
        "u06_independent_audit_status": ACCEPTED_AUDIT_STATUS,
        "u06_acceptance_status": ACCEPTED_ACCEPTANCE_STATUS,
        "accepted_lifecycle_overlay": PRESENT_VALID_OVERLAY_STATUS,
        "production_authority_freeze_status": FROZEN_STATUS,
        "authorizes_main_full81": False,
        "freeze_blocked_reason": None,
        "implementation_identity_digest": live_digest,
        "required_future_roles": list(REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {
            role: {"path": r["path"], "sha256": r["sha256"]}
            for role, r in resolved.items()
        },
        "missing_roles": [],
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def absent_lifecycle(
    *, reason: str | None = None, record_path: str | None = None
) -> dict[str, Any]:
    """The most restrictive lifecycle state: nothing accepted, nothing frozen."""

    return {
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
        "lineage_id": LINEAGE_ID,
        "target_candidate_id": R3_CANDIDATE_ID,
        "record_path": record_path
        or ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "record_present": False,
        "record_committed": False,
        "record_published": False,
        "self_accepted": False,
        "u06_alignment_status": PRE_ACCEPTANCE_ALIGNMENT_STATUS,
        "u06_independent_audit_status": PRE_ACCEPTANCE_AUDIT_STATUS,
        "u06_acceptance_status": PRE_ACCEPTANCE_ACCEPTANCE_STATUS,
        "accepted_lifecycle_overlay": PRE_ACCEPTANCE_OVERLAY_STATUS,
        "production_authority_freeze_status": PRE_ACCEPTANCE_FREEZE_STATUS,
        "authorizes_main_full81": False,
        "freeze_blocked_reason": reason
        or (
            "No accepted U-06 R3 lifecycle record exists. Production authority "
            "cannot be frozen by an unaccepted candidate, by clean Git state, by "
            "matching authority hashes, by publishing candidate bytes, or by any "
            "set of unrelated historical artifacts."
        ),
        "implementation_identity_digest": None,
        "required_future_roles": list(REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {},
        "missing_roles": list(REQUIRED_ACCEPTED_ROLES),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def resolve_u06_lifecycle(root: Path) -> dict[str, Any]:
    """Resolve U-06 lifecycle state from live bytes and Git. Read-only.

    Never raises: anything invalid resolves to a NOT_FROZEN state carrying the
    reason, so callers report the blocker instead of crashing. Writes nothing.
    """

    root = root.resolve()
    record_relative = ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()
    path = root / ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH

    if not path.is_file():
        return absent_lifecycle(record_path=record_relative)

    tracked, clean = is_tracked_and_clean(root, record_relative)
    if not tracked or not clean:
        state = absent_lifecycle(
            record_path=record_relative,
            reason=(
                "An accepted-lifecycle record exists in the working tree but is "
                f"{'untracked' if not tracked else 'modified relative to HEAD'}. "
                "A working-tree file confers no acceptance."
            ),
        )
        state["record_present"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        return state

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        state = absent_lifecycle(
            record_path=record_relative,
            reason=f"Accepted-lifecycle record is not readable JSON: {exc}",
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        return state

    try:
        return validate_accepted_lifecycle_payload(
            root, payload, record_relative=record_relative
        )
    except U06LifecycleError as exc:
        state = absent_lifecycle(
            record_path=record_relative, reason=f"{exc.status}: {exc}"
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        state["rejected_status"] = exc.status
        return state


#: Invariants a resolved lifecycle mapping must satisfy before any freeze.
_FROZEN_INVARIANTS: Mapping[str, Any] = {
    "accepted_lifecycle_overlay": PRESENT_VALID_OVERLAY_STATUS,
    "lineage_id": LINEAGE_ID,
    "target_candidate_id": R3_CANDIDATE_ID,
    "u06_alignment_status": ACCEPTED_ALIGNMENT_STATUS,
    "u06_independent_audit_status": ACCEPTED_AUDIT_STATUS,
    "u06_acceptance_status": ACCEPTED_ACCEPTANCE_STATUS,
    "production_authority_freeze_status": FROZEN_STATUS,
    "record_present": True,
    "record_committed": True,
    "record_published": True,
    "self_accepted": False,
    "authorizes_main_full81": False,
}


def require_frozen_lifecycle(lifecycle: Mapping[str, Any] | None) -> dict[str, Any]:
    """Gate guard. Raise unless an accepted U-06 R3 lifecycle authorizes a freeze."""

    if lifecycle is None:
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_ABSENT",
            "No U-06 accepted lifecycle was resolved. Production authority cannot "
            "be frozen without an accepted U-06 R3 lifecycle record.",
        )
    for field, expected in _FROZEN_INVARIANTS.items():
        observed = lifecycle.get(field)
        if observed != expected:
            status = (
                "U06_ACCEPTED_LIFECYCLE_ABSENT"
                if lifecycle.get("accepted_lifecycle_overlay")
                == PRE_ACCEPTANCE_OVERLAY_STATUS
                else "U06_ACCEPTED_LIFECYCLE_INVALID"
            )
            reason = lifecycle.get("freeze_blocked_reason") or (
                f"{field} must be {expected!r}; observed {observed!r}"
            )
            raise U06LifecycleError(
                status,
                "U-06 accepted lifecycle does not authorize a production-authority "
                f"freeze. Blocking field={field}, expected={expected!r}, "
                f"observed={observed!r}. {reason}",
            )

    satisfied = lifecycle.get("satisfied_roles")
    if not isinstance(satisfied, Mapping) or set(satisfied) != set(
        REQUIRED_ACCEPTED_ROLES
    ):
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
            "U-06 accepted lifecycle does not satisfy every required role: "
            f"required={list(REQUIRED_ACCEPTED_ROLES)}, "
            f"satisfied={sorted(satisfied) if isinstance(satisfied, Mapping) else satisfied}",
        )
    missing: Sequence[Any] = lifecycle.get("missing_roles") or []
    if list(missing):
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
            f"U-06 accepted lifecycle reports missing roles: {list(missing)}",
        )
    digest = lifecycle.get("implementation_identity_digest")
    if not isinstance(digest, str) or not _SHA256_RE.match(digest):
        raise U06LifecycleError(
            "U06_IMPLEMENTATION_IDENTITY_DRIFT",
            "U-06 accepted lifecycle carries no usable accepted implementation "
            f"identity digest: {digest!r}",
        )
    return dict(lifecycle)


def require_frozen_lifecycle_against_live_implementation(
    root: Path, lifecycle: Mapping[str, Any] | None
) -> dict[str, Any]:
    """`require_frozen_lifecycle` plus a live re-check of the code identity.

    A committed, clean, pushed change to any accepted runtime dependency makes
    the live digest differ from the accepted one, and this fails closed.
    """

    resolved = require_frozen_lifecycle(lifecycle)
    live = implementation_identity_digest(root)
    if resolved["implementation_identity_digest"] != live:
        raise U06LifecycleError(
            "U06_IMPLEMENTATION_IDENTITY_DRIFT",
            "Accepted implementation identity "
            f"{resolved['implementation_identity_digest']} does not match the live "
            f"production dependency surface {live}. Production authority is not "
            "frozen for changed code, even when the change is committed, the "
            "working tree is clean, and HEAD equals the upstream.",
        )
    return resolved


def lifecycle_summary(lifecycle: Mapping[str, Any] | None) -> dict[str, Any]:
    """Compact, emission-ready lifecycle view, sourced entirely from `lifecycle`."""

    resolved = dict(lifecycle) if lifecycle is not None else absent_lifecycle()
    return {
        "lifecycle_module_version": resolved.get("lifecycle_module_version"),
        "lineage_id": resolved.get("lineage_id"),
        "target_candidate_id": resolved.get("target_candidate_id"),
        "u06_alignment_status": resolved.get("u06_alignment_status"),
        "u06_independent_audit_status": resolved.get("u06_independent_audit_status"),
        "u06_acceptance_status": resolved.get("u06_acceptance_status"),
        "accepted_lifecycle_overlay": resolved.get("accepted_lifecycle_overlay"),
        "production_authority_freeze_status": resolved.get(
            "production_authority_freeze_status"
        ),
        "authorizes_main_full81": resolved.get("authorizes_main_full81", False),
        "freeze_blocked_reason": resolved.get("freeze_blocked_reason"),
        "implementation_identity_digest": resolved.get(
            "implementation_identity_digest"
        ),
        "record_path": resolved.get("record_path"),
        "record_present": resolved.get("record_present"),
        "record_committed": resolved.get("record_committed"),
        "record_published": resolved.get("record_published"),
        "missing_roles": list(resolved.get("missing_roles") or []),
        "satisfied_roles": sorted(resolved.get("satisfied_roles") or {}),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
    }


def is_frozen(lifecycle: Mapping[str, Any] | None) -> bool:
    """True only when `lifecycle` authorizes a production-authority freeze."""

    try:
        require_frozen_lifecycle(lifecycle)
    except U06LifecycleError:
        return False
    return True


def future_acceptance_requirements() -> dict[str, Any]:
    """What a future acceptance pass must create. No digest is invented here."""

    return {
        "lineage_id": LINEAGE_ID,
        "target_candidate_id": R3_CANDIDATE_ID,
        "candidate_checkpoint_path": R3_CANDIDATE_CHECKPOINT_PATH,
        "candidate_manifest_path": R3_CANDIDATE_MANIFEST_PATH,
        "accepted_lifecycle_record_path":
            ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "accepted_lifecycle_artifact_type": ACCEPTED_LIFECYCLE_ARTIFACT_TYPE,
        "accepted_lifecycle_schema_version": LIFECYCLE_RECORD_SCHEMA_VERSION,
        "record_exists_today": False,
        "role_contracts": {
            role: contract.as_dict() for role, contract in ROLE_CONTRACTS.items()
        },
        "roles_a_candidate_may_never_fill": list(NON_SELF_ACCEPTABLE_ROLES),
        "forbidden_role_paths": list(CANDIDATE_ARTIFACT_PATHS),
        "forbidden_role_prefixes": list(NON_GOVERNANCE_PREFIXES),
        "superseded_candidate_ids_rejected": list(SUPERSEDED_CANDIDATE_IDS),
        "runtime_production_dependency_paths": list(
            RUNTIME_PRODUCTION_DEPENDENCY_PATHS
        ),
        "gate_protected_dependency_paths": list(GATE_PROTECTED_DEPENDENCY_PATHS),
        "accepted_implementation_paths": list(ACCEPTED_IMPLEMENTATION_PATHS),
        "validation_identity_paths": list(VALIDATION_IDENTITY_PATHS),
        "tests_are_runtime_production_authority": False,
        "every_role_record_must_be": [
            "a machine-readable JSON object",
            "of the role-specific artifact_type",
            "of the role-specific schema_version",
            f"declaring lineage_id = {LINEAGE_ID}",
            f"declaring target_candidate_id = {R3_CANDIDATE_ID}",
            "declaring the exact R3 candidate checkpoint path and live SHA-256",
            "declaring the live accepted implementation identity digest",
            "binding the exact identity of every earlier role",
            "present on disk, hash-identical, tracked, and clean",
            "published in HEAD, with the HEAD blob matching live bytes",
        ],
        "publication_phases": {
            "phase_a": (
                "candidate + independent audit PASS published; later acceptance "
                "artifacts record audit_publication_commit = A, and validation "
                "proves both blobs exist in exactly A."
            ),
            "phase_b": (
                "acceptance closure + acceptance manifest published; the re-freeze "
                "record records acceptance_publication_commit = B, and validation "
                "proves both blobs exist in exactly B."
            ),
            "phase_c": (
                "re-freeze + accepted lifecycle record published; their own "
                "containing commit is never self-hard-coded. The live gate proves "
                "from Git that each artifact is in HEAD, that HEAD blobs match live "
                "bytes, that HEAD equals the upstream, that paths are clean, and "
                "that the last modifying commit is in published ancestry."
            ),
        },
        "arbitrary_ancestor_accepted_as_publication_proof": False,
        "self_referential_commit_hash_required": False,
        "future_hashes_fabricated_now": False,
        "placeholder_digests_present": False,
        "note": (
            "None of these artifacts exists. The overlay resolves to ABSENT / "
            "NOT_FROZEN and the production gate fails closed. No future digest is "
            "guessed, reserved, or stubbed in this module."
        ),
    }


def runtime_dependency_report(root: Path) -> dict[str, Any]:
    """Read-only report of the accepted implementation and validation surfaces."""

    root = root.resolve()
    identity = implementation_identity(root)
    return {
        "lineage_id": LINEAGE_ID,
        "runtime_production_dependency_count": len(
            RUNTIME_PRODUCTION_DEPENDENCY_PATHS
        ),
        "gate_protected_dependency_count": len(GATE_PROTECTED_DEPENDENCY_PATHS),
        "accepted_implementation_count": len(ACCEPTED_IMPLEMENTATION_PATHS),
        "runtime_production_dependency_paths": list(
            RUNTIME_PRODUCTION_DEPENDENCY_PATHS
        ),
        "gate_protected_dependency_paths": list(GATE_PROTECTED_DEPENDENCY_PATHS),
        "accepted_implementation_identity": identity,
        "implementation_identity_digest": canonical_identity_digest(identity),
        "validation_identity": validation_identity(root),
        "tests_counted_as_runtime_production_authority": False,
    }
