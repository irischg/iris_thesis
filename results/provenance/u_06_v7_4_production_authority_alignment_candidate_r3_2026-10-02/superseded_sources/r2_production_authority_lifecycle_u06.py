"""U-06 accepted-lifecycle overlay for V7.4 production authority.

Why this module exists
----------------------
U-06 Candidate R1 bound the accepted V7.4 **identities** into the live production
gate, but it left the gate able to reach ``PRODUCTION_AUTHORITY_FROZEN`` as soon
as the candidate's own implementation bytes were tracked, clean, committed, and
pushed.  A fresh independent read-only audit classified that as a MAJOR
acceptance-blocking defect (``F-01``): committing an *unaccepted candidate* is
not acceptance, and a clean Git state is not a governance decision.

This overlay closes that.  It is a **separate object** from the base V7.4
authority bundle, so lifecycle-acceptance bytes never have to be injected into
the object whose hash the acceptance itself names — there is no circular
hashing.  The split is deliberate:

``src/production_authority_bundle_v7_4.py``
    scientific / evidence / implementation **identity** — what the route is.

``src/production_authority_lifecycle_u06.py`` (this module)
    accepted-lifecycle **authority** — whether that route has been independently
    audited, accepted, closed, re-frozen, and published.

Five states, kept mechanically independent
------------------------------------------
``PRODUCTION_AUTHORITY_ALIGNMENT_STATUS``  (base bundle)   implementation aligned
``U06_INDEPENDENT_AUDIT_STATUS``           (this overlay)  audit outcome
``U06_ACCEPTANCE_STATUS``                  (this overlay)  acceptance / closure
``PRODUCTION_AUTHORITY_FREEZE_STATUS``     (this overlay)  freeze
``MAIN_FULL81_AUTHORIZATION_STATUS``       (base bundle)   Full81 authorization

No state implicitly promotes another.  In particular ``CANDIDATE_ALIGNED`` never
implies ``PASS``, ``PASS`` never implies ``CLOSED_ACCEPTED``,
``CLOSED_ACCEPTED`` never implies ``FROZEN``, and ``FROZEN`` never implies
Full81 authorization.

No self-acceptance
------------------
The accepted-lifecycle record this overlay consumes
(:data:`ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH`) **does not exist yet**, and no
placeholder digest for it or for any future accepted artifact is hard-coded
anywhere.  The overlay therefore currently resolves to
``ACCEPTED_LIFECYCLE_OVERLAY = ABSENT`` and
``PRODUCTION_AUTHORITY_FREEZE_STATUS = NOT_FROZEN``, and the production gate
fails closed on that.

When a future, separately authorized acceptance pass creates the record, it must
name — by exact path and SHA-256, verified here against live bytes — a set of
accepted artifacts that the candidate cannot supply for itself:

* the accepted implementation candidate checkpoint;
* an **independent audit PASS** record;
* the acceptance / closure checkpoint;
* the acceptance manifest;
* the production-authority re-freeze / accepted-lifecycle record.

The four non-candidate roles may never be filled by a candidate checkpoint, a
candidate manifest, this record itself, or any file under ``src/``, ``scripts/``,
or ``tests/`` — so candidate code, candidate documents, and test fixtures are all
structurally incapable of conferring acceptance.  Every one of those artifacts,
and the record itself, must additionally be tracked and clean in ``HEAD``, and
the record's declared publication commit must be an ancestor of ``HEAD``: a
working-tree file confers nothing.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.production_input_authority_v7_3 import sha256_file


LIFECYCLE_MODULE_VERSION = "v7.4-u06-accepted-lifecycle-overlay-2026-10-02-r1"
LIFECYCLE_RECORD_SCHEMA_VERSION = (
    "iris-thesis-u06-v7-4-production-authority-accepted-lifecycle-record-v1"
)

#: Where a FUTURE accepted-lifecycle record must live.  Absent today, by design.
ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH = Path(
    "results/provenance/u_06_v7_4_production_authority_accepted_lifecycle/"
    "accepted_lifecycle_record.json"
)

#: Roles the accepted-lifecycle record must supply, each by exact path + SHA-256.
REQUIRED_ACCEPTED_ROLES: tuple[str, ...] = (
    "accepted_implementation_candidate_checkpoint",
    "independent_audit_pass_record",
    "acceptance_closure_checkpoint",
    "acceptance_manifest",
    "production_authority_re_freeze_record",
)

#: Roles that a candidate may never fill for itself.  The accepted implementation
#: candidate checkpoint is excluded because the thing being accepted is, by
#: definition, a candidate document.
NON_SELF_ACCEPTABLE_ROLES: tuple[str, ...] = tuple(
    role
    for role in REQUIRED_ACCEPTED_ROLES
    if role != "accepted_implementation_candidate_checkpoint"
)

#: Candidate artifacts that can never stand in for an acceptance decision.
CANDIDATE_ARTIFACT_PATHS: tuple[str, ...] = (
    "docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_2026-10-02.md",
    "results/provenance/u_06_v7_4_production_authority_alignment_candidate_2026-10-02/"
    "alignment_manifest.json",
    "docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02.md",
    "results/provenance/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02/"
    "alignment_manifest.json",
)

#: Directory prefixes that can never hold an acceptance-decision artifact.
NON_GOVERNANCE_PREFIXES: tuple[str, ...] = ("src/", "scripts/", "tests/")

#: Exactly the implementation bytes an acceptance must bind.  A post-acceptance
#: edit to any of these breaks the freeze closed rather than silently inheriting
#: the old acceptance.
IMPLEMENTATION_CANDIDATE_SURFACE: tuple[str, ...] = (
    "src/production_authority_bundle_v7_4.py",
    "src/production_authority_lifecycle_u06.py",
    "src/production_successor_stack_v7_3.py",
    "scripts/21d_preflight_v7_3_final81_successor.py",
    "scripts/21e_preflight_v7_4_production_authority_alignment.py",
    "tests/test_21e_v7_4_production_authority_bundle.py",
    "tests/test_21f_u06_accepted_lifecycle_gate.py",
)

# --- Pre-acceptance constants -------------------------------------------------
# These describe the CURRENT, factual pre-acceptance state only.  Every field
# emitted downstream is read from the resolved lifecycle mapping, which replaces
# all of them with record-derived values once a valid accepted-lifecycle record
# exists.  Nothing here is a permanent compile-time claim about U-06.

PRE_ACCEPTANCE_ALIGNMENT_STATUS = "CANDIDATE"
PRE_ACCEPTANCE_AUDIT_STATUS = "CANDIDATE_R1_FAILED_R2_PENDING"
PRE_ACCEPTANCE_ACCEPTANCE_STATUS = "NOT_ACCEPTED"
PRE_ACCEPTANCE_OVERLAY_STATUS = "ABSENT"
PRE_ACCEPTANCE_FREEZE_STATUS = "NOT_FROZEN"

ACCEPTED_ALIGNMENT_STATUS = "ACCEPTED"
ACCEPTED_AUDIT_STATUS = "PASS"
ACCEPTED_ACCEPTANCE_STATUS = "CLOSED_ACCEPTED"
PRESENT_VALID_OVERLAY_STATUS = "PRESENT_VALID"
PRESENT_INVALID_OVERLAY_STATUS = "PRESENT_INVALID"
FROZEN_STATUS = "FROZEN"

#: Candidate R1 independent-audit outcome, recorded so the failure is never
#: erased or quietly rewritten.
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
}

#: Statements that must never be collapsed into one another.
LIFECYCLE_DISTINCTIONS = (
    "ZERO_SOLVE_PREFLIGHT_PASS",
    "BASE_AUTHORITY_CANDIDATE_ALIGNED",
    "U06_INDEPENDENT_AUDIT_PASS",
    "U06_ACCEPTANCE_CLOSED_ACCEPTED",
    "PRODUCTION_AUTHORITY_FROZEN",
    "MAIN_FULL81_AUTHORIZED",
    "MAIN_FULL81_EXECUTED",
)

#: The one lawful ordering.  Each arrow is a separately authorized act.
REQUIRED_LIFECYCLE_SEQUENCE = (
    "IMPLEMENTATION_CANDIDATE",
    "FRESH_INDEPENDENT_AUDIT_PASS",
    "ACCEPTANCE_CLOSURE",
    "ACCEPTED_LIFECYCLE_RE_FREEZE_AUTHORITY",
    "COMMIT_AND_PUBLICATION",
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


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _is_tracked_and_clean(root: Path, relative: str) -> tuple[bool, bool]:
    tracked = _git(root, "ls-files", "--error-unmatch", "--", relative).returncode == 0
    if not tracked:
        return False, False
    clean = _git(root, "diff", "--quiet", "HEAD", "--", relative).returncode == 0
    return True, clean


def _is_ancestor_of_head(root: Path, commit: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", commit, "HEAD").returncode == 0


def absent_lifecycle(
    *, reason: str | None = None, record_path: str | None = None
) -> dict[str, Any]:
    """The most restrictive lifecycle state: nothing accepted, nothing frozen.

    This is the default everywhere.  A caller that supplies no lifecycle gets
    this, so an omission can never read as acceptance.
    """

    return {
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
        "record_path": record_path or ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "record_present": False,
        "record_committed": False,
        "record_published": False,
        "self_accepted": False,
        "u06_alignment_status": PRE_ACCEPTANCE_ALIGNMENT_STATUS,
        "u06_independent_audit_status": PRE_ACCEPTANCE_AUDIT_STATUS,
        "u06_acceptance_status": PRE_ACCEPTANCE_ACCEPTANCE_STATUS,
        "accepted_lifecycle_overlay": PRE_ACCEPTANCE_OVERLAY_STATUS,
        "production_authority_freeze_status": PRE_ACCEPTANCE_FREEZE_STATUS,
        "freeze_blocked_reason": reason
        or (
            "No accepted U-06 lifecycle record exists. Production authority cannot "
            "be frozen by an unaccepted candidate, by clean Git state, by matching "
            "authority hashes, or by publishing candidate bytes."
        ),
        "required_future_roles": list(REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {},
        "missing_roles": list(REQUIRED_ACCEPTED_ROLES),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def _require(condition: bool, status: str, message: str) -> None:
    if not condition:
        raise U06LifecycleError(status, message)


def _validate_role_path(role: str, relative: str, record_relative: str) -> None:
    normalized = relative.replace("\\", "/").strip()
    _require(
        bool(normalized) and not normalized.startswith("/"),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"Role {role!r} has an unusable path: {relative!r}",
    )
    if role not in NON_SELF_ACCEPTABLE_ROLES:
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


def validate_accepted_lifecycle_payload(
    root: Path, payload: Mapping[str, Any], *, record_relative: str
) -> dict[str, Any]:
    """Strictly validate a candidate accepted-lifecycle record. Fail-closed.

    Checks run in a deliberate order so the reported status names the real
    governance problem: schema, then declared statuses, then structural
    self-acceptance, then publication, then live bytes.  A self-acceptance
    attempt is therefore reported as self-acceptance whatever else is wrong.
    """

    root = root.resolve()

    # 1. Schema.
    _require(
        isinstance(payload, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        "The accepted-lifecycle record is not a JSON object.",
    )
    _require(
        payload.get("schema_version") == LIFECYCLE_RECORD_SCHEMA_VERSION,
        "U06_LIFECYCLE_RECORD_INVALID",
        "Accepted-lifecycle record schema_version mismatch: expected "
        f"{LIFECYCLE_RECORD_SCHEMA_VERSION!r}, observed "
        f"{payload.get('schema_version')!r}",
    )

    # 2. Declared lifecycle statuses. Every one must be the accepted value.
    for field, expected in (
        ("u06_alignment_status", ACCEPTED_ALIGNMENT_STATUS),
        ("u06_independent_audit_status", ACCEPTED_AUDIT_STATUS),
        ("u06_acceptance_status", ACCEPTED_ACCEPTANCE_STATUS),
        ("production_authority_freeze_status", FROZEN_STATUS),
    ):
        _require(
            payload.get(field) == expected,
            "U06_LIFECYCLE_NOT_ACCEPTED",
            f"Accepted-lifecycle record {field} must be {expected!r}; observed "
            f"{payload.get(field)!r}",
        )

    # 3. An audit PASS is never self-acceptance.
    _require(
        payload.get("independent_audit_self_accepted") is False,
        "U06_SELF_ACCEPTANCE_REJECTED",
        "The accepted-lifecycle record must assert "
        "independent_audit_self_accepted = false. An audit PASS is never "
        "self-acceptance.",
    )

    # 4. Role completeness.
    artifacts = payload.get("artifacts")
    _require(
        isinstance(artifacts, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        "Accepted-lifecycle record has no artifacts object.",
    )
    missing = [role for role in REQUIRED_ACCEPTED_ROLES if role not in artifacts]
    _require(
        not missing,
        "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
        f"Accepted-lifecycle record is missing required roles: {missing}",
    )
    unexpected = sorted(set(artifacts) - set(REQUIRED_ACCEPTED_ROLES))
    _require(
        not unexpected,
        "U06_LIFECYCLE_RECORD_INVALID",
        f"Accepted-lifecycle record declares unknown roles: {unexpected}",
    )

    # 5. Structural, filesystem-free: shape, digest format, self-acceptance,
    #    and role distinctness. No candidate artifact, candidate source file,
    #    test file, or the record itself may fill an acceptance role, and two
    #    roles may never share one artifact.
    declared_roles: dict[str, tuple[str, str]] = {}
    seen_paths: dict[str, str] = {}
    for role in REQUIRED_ACCEPTED_ROLES:
        entry = artifacts[role]
        _require(
            isinstance(entry, Mapping),
            "U06_LIFECYCLE_RECORD_INVALID",
            f"Role {role!r} is not an object.",
        )
        relative = str(entry.get("path", "")).replace("\\", "/").strip()
        declared = str(entry.get("sha256", "")).lower()
        _require(
            bool(_SHA256_RE.match(declared)),
            "U06_LIFECYCLE_RECORD_INVALID",
            f"Role {role!r} has no usable SHA-256.",
        )
        _validate_role_path(role, relative, record_relative)
        _require(
            relative not in seen_paths,
            "U06_LIFECYCLE_RECORD_INVALID",
            f"Roles {seen_paths.get(relative)!r} and {role!r} name the same path "
            f"{relative}; acceptance roles must be structurally distinct artifacts.",
        )
        seen_paths[relative] = role
        declared_roles[role] = (relative, declared)

    # 6. Publication. An unpublished acceptance confers nothing.
    publication_commit = str(payload.get("publication_commit", ""))
    _require(
        bool(_COMMIT_RE.match(publication_commit)),
        "U06_LIFECYCLE_RECORD_INVALID",
        "Accepted-lifecycle publication_commit is not a full SHA-1: "
        f"{publication_commit!r}",
    )
    _require(
        _is_ancestor_of_head(root, publication_commit),
        "U06_LIFECYCLE_NOT_PUBLISHED",
        "Accepted-lifecycle publication_commit is not an ancestor of HEAD; an "
        "unpublished acceptance confers no production authority.",
    )

    # 7. The acceptance is bound to exact implementation bytes. A post-acceptance
    #    edit to any of them breaks the freeze closed instead of inheriting it.
    identity = payload.get("implementation_identity")
    _require(
        isinstance(identity, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        "Accepted-lifecycle record has no implementation_identity object.",
    )
    expected_surface = set(IMPLEMENTATION_CANDIDATE_SURFACE)
    declared_surface = {str(key).replace("\\", "/") for key in identity}
    _require(
        declared_surface == expected_surface,
        "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
        "Accepted-lifecycle implementation_identity must cover exactly the "
        "implementation candidate surface; missing="
        f"{sorted(expected_surface - declared_surface)}, "
        f"unexpected={sorted(declared_surface - expected_surface)}",
    )
    for relative in IMPLEMENTATION_CANDIDATE_SURFACE:
        declared = str(identity[relative]).lower()
        path = root / relative
        _require(
            path.is_file(),
            "U06_ACCEPTED_LIFECYCLE_HASH_FAIL",
            f"Accepted implementation file is missing: {relative}",
        )
        actual = sha256_file(path)
        _require(
            actual == declared,
            "U06_ACCEPTED_LIFECYCLE_HASH_FAIL",
            "Live implementation bytes differ from the accepted implementation "
            f"identity for {relative}: accepted={declared}, actual={actual}. An "
            "acceptance never carries forward to edited implementation bytes.",
        )

    # 8. Live bytes for every accepted artifact: present, hash-identical,
    #    tracked, and clean.
    satisfied: dict[str, dict[str, Any]] = {}
    for role in REQUIRED_ACCEPTED_ROLES:
        relative, declared = declared_roles[role]
        path = root / relative
        _require(
            path.is_file(),
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
            f"Accepted artifact for role {role!r} is missing: {relative}",
        )
        actual = sha256_file(path)
        _require(
            actual == declared,
            "U06_ACCEPTED_LIFECYCLE_HASH_FAIL",
            f"Accepted artifact for role {role!r} does not match its declared "
            f"SHA-256: expected={declared}, actual={actual}, path={relative}",
        )
        tracked, clean = _is_tracked_and_clean(root, relative)
        _require(
            tracked,
            "U06_LIFECYCLE_NOT_PUBLISHED",
            f"Accepted artifact for role {role!r} is not tracked in Git: {relative}",
        )
        _require(
            clean,
            "U06_LIFECYCLE_NOT_PUBLISHED",
            f"Accepted artifact for role {role!r} has working-tree drift: {relative}",
        )
        satisfied[role] = {"path": relative, "sha256": actual}

    return {
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
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
        "freeze_blocked_reason": None,
        "publication_commit": publication_commit,
        "required_future_roles": list(REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": satisfied,
        "missing_roles": [],
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def resolve_u06_lifecycle(root: Path) -> dict[str, Any]:
    """Resolve U-06 lifecycle state from live repository bytes and Git. Read-only.

    Never raises: an absent, malformed, uncommitted, unpublished, or otherwise
    invalid record resolves to a NOT_FROZEN state carrying the reason, so callers
    can report the blocker instead of crashing.  Nothing is written.
    """

    root = root.resolve()
    record_relative = ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()
    path = root / ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH

    if not path.is_file():
        return absent_lifecycle(record_path=record_relative)

    tracked, clean = _is_tracked_and_clean(root, record_relative)
    if not tracked or not clean:
        state = absent_lifecycle(
            record_path=record_relative,
            reason=(
                "An accepted-lifecycle record exists in the working tree but is "
                f"{'untracked' if not tracked else 'modified relative to HEAD'}. A "
                "working-tree file confers no acceptance and no production "
                "authority."
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
            record_path=record_relative,
            reason=f"{exc.status}: {exc}",
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        state["rejected_status"] = exc.status
        return state


#: Invariants a resolved lifecycle mapping must satisfy before any freeze.
_FROZEN_INVARIANTS: Mapping[str, Any] = {
    "accepted_lifecycle_overlay": PRESENT_VALID_OVERLAY_STATUS,
    "u06_alignment_status": ACCEPTED_ALIGNMENT_STATUS,
    "u06_independent_audit_status": ACCEPTED_AUDIT_STATUS,
    "u06_acceptance_status": ACCEPTED_ACCEPTANCE_STATUS,
    "production_authority_freeze_status": FROZEN_STATUS,
    "record_present": True,
    "record_committed": True,
    "record_published": True,
    "self_accepted": False,
}


def require_frozen_lifecycle(lifecycle: Mapping[str, Any] | None) -> dict[str, Any]:
    """Gate guard. Raise unless an accepted U-06 lifecycle authorizes a freeze.

    Pure: it re-checks every invariant on the mapping handed to it, so a partial
    or hand-built mapping cannot slip through by carrying one optimistic field.
    """

    if lifecycle is None:
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_ABSENT",
            "No U-06 accepted lifecycle was resolved. Production authority cannot "
            "be frozen without an accepted U-06 lifecycle record.",
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
    return dict(lifecycle)


def lifecycle_summary(lifecycle: Mapping[str, Any] | None) -> dict[str, Any]:
    """Compact, emission-ready lifecycle view, sourced entirely from `lifecycle`.

    Downstream provenance reads U-06 state from here, never from a compile-time
    constant, so a lawful future acceptance changes the emitted state without any
    code edit and without rewriting historical artifacts.
    """

    resolved = dict(lifecycle) if lifecycle is not None else absent_lifecycle()
    return {
        "lifecycle_module_version": resolved.get("lifecycle_module_version"),
        "u06_alignment_status": resolved.get("u06_alignment_status"),
        "u06_independent_audit_status": resolved.get("u06_independent_audit_status"),
        "u06_acceptance_status": resolved.get("u06_acceptance_status"),
        "accepted_lifecycle_overlay": resolved.get("accepted_lifecycle_overlay"),
        "production_authority_freeze_status": resolved.get(
            "production_authority_freeze_status"
        ),
        "freeze_blocked_reason": resolved.get("freeze_blocked_reason"),
        "record_path": resolved.get("record_path"),
        "record_present": resolved.get("record_present"),
        "record_committed": resolved.get("record_committed"),
        "record_published": resolved.get("record_published"),
        "missing_roles": list(resolved.get("missing_roles") or []),
        "satisfied_roles": sorted(resolved.get("satisfied_roles") or {}),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
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
        "accepted_lifecycle_record_path":
            ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix(),
        "accepted_lifecycle_record_schema_version": LIFECYCLE_RECORD_SCHEMA_VERSION,
        "record_exists_today": False,
        "required_roles": list(REQUIRED_ACCEPTED_ROLES),
        "roles_a_candidate_may_never_fill": list(NON_SELF_ACCEPTABLE_ROLES),
        "forbidden_role_paths": list(CANDIDATE_ARTIFACT_PATHS),
        "forbidden_role_prefixes": list(NON_GOVERNANCE_PREFIXES),
        "implementation_candidate_surface": list(IMPLEMENTATION_CANDIDATE_SURFACE),
        "required_record_fields": [
            "schema_version",
            "u06_alignment_status",
            "u06_independent_audit_status",
            "u06_acceptance_status",
            "production_authority_freeze_status",
            "independent_audit_self_accepted",
            "publication_commit",
            "artifacts",
            "implementation_identity",
        ],
        "every_role_artifact_must_be": [
            "present on disk",
            "hash-identical to its declared SHA-256",
            "tracked in Git",
            "clean relative to HEAD",
        ],
        "publication_commit_must_be_ancestor_of_head": True,
        "future_hashes_fabricated_now": False,
        "placeholder_digests_present": False,
        "note": (
            "These accepted artifacts do not exist yet. The overlay therefore "
            "resolves to ABSENT / NOT_FROZEN and the production gate fails closed. "
            "No future digest is guessed, reserved, or stubbed anywhere in this "
            "module."
        ),
    }
