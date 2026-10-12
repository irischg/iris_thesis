"""Read-only verifier for the Iris Thesis current-mainline pointer (interface v1).

The pointer is a verified ROUTING INDEX.  It answers one question for Claude
Code, Codex, PowerShell, the future Pipeline Manager notebook and downstream
analysis code:

    Which methodology, evidence authority, production implementation,
    canonical input and formally accepted result set are current, and can
    their identities be verified?

It is not a governance authority of its own.  Every identity it carries is
re-derived here from live bytes and from Git objects, and cross-checked against
the accepted primary artifacts it routes to.  It grants no production
execution authority: production authority is determined live by the production
runner's own gate, and this module is never an input to that gate.

Two modes, never interchangeable:

``CANDIDATE``
    Reads a candidate pointer under ``configs/candidates/`` and reports whether
    it is internally consistent.  A candidate PASS is never an acceptance and
    never confers authority.

``CANONICAL``
    Looks only at :data:`CANONICAL_POINTER_RELATIVE_PATH`.  An absent,
    candidate-only, unpublished, mismatched or stale pointer yields a
    machine-readable ``FAIL_CLOSED`` result.  No other route is ever guessed.

Two hash axes are reported separately and never conflated:

* the raw-byte SHA-256 of the working-tree file, and
* the Git blob identity (blob id at the anchor commit and at ``HEAD``, and the
  SHA-256 of the blob bytes).

On Windows a checkout under ``core.autocrlf=true`` may convert an LF blob to
CRLF for a path the pinned ``.gitattributes`` does not cover.  That is reported
as ``RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY`` and still fails closed.

This module is standard-library only.  It imports no solver, builds no
optimization model, calls no ``optimize()``, writes no file and runs only
read-only Git subcommands.  It never parses or prints a case-level result
value: result files are hashed as opaque bytes.

It contains no identity literal.  Every expected hash, commit and status lives
in the pointer, so this module can never become a second, competing pointer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

INTERFACE_VERSION = "iris-thesis-current-mainline-pointer-verifier-v1"
POINTER_ARTIFACT_TYPE = "IRIS_THESIS_CURRENT_MAINLINE_POINTER"
POINTER_SCHEMA_VERSION = "iris-thesis-current-mainline-pointer-v1"

#: The one stable path a canonical pointer may ever occupy.
CANONICAL_POINTER_RELATIVE_PATH = "configs/current_mainline_pointer.json"
#: Candidates live here and nowhere else.
CANDIDATE_DIRECTORY_RELATIVE_PATH = "configs/candidates"
#: Scanned for competing pointer-typed files.
POINTER_SEARCH_ROOT_RELATIVE_PATH = "configs"

MODE_CANDIDATE = "CANDIDATE"
MODE_CANONICAL = "CANONICAL"

RESULTS_POLICY_NONE = "NOT_CHECKED"
RESULTS_POLICY_METADATA = "METADATA_ONLY"
RESULTS_POLICY_STRICT = "STRICT_FULL_REHASH"
RESULTS_POLICIES = (RESULTS_POLICY_NONE, RESULTS_POLICY_METADATA, RESULTS_POLICY_STRICT)

RESULTS_NOT_CHECKED = "NOT_CHECKED"
#: A metadata check is never full integrity and is never labelled as such.
RESULTS_METADATA_ONLY = "METADATA_ONLY_NOT_FULL_INTEGRITY"
RESULTS_STRICT_PASS = "STRICT_FULL_INTEGRITY_PASS"
RESULTS_FAIL = "FAIL"

VERDICT_CANDIDATE_CONSISTENT = "CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY"
VERDICT_CANONICAL_VERIFIED = "CANONICAL_POINTER_VERIFIED"
VERDICT_FAIL_CLOSED = "FAIL_CLOSED"

LIFECYCLE_CANDIDATE = "CANDIDATE"
LIFECYCLE_CANONICAL = "ACCEPTED_CANONICAL"
CANDIDATE_LIFECYCLE_LABEL = "CANDIDATE / NOT ACCEPTED / NOT CURRENT AUTHORITY"
ACTIVATION_NOT_ACTIVATED = "NOT_ACTIVATED"
ACTIVATION_ACCEPTED_PUBLISHED = "ACCEPTED_PUBLISHED"

#: What a tracked identity's anchor commit asserts.  ``ADDED``: the commit that
#: introduced the file, i.e. its publication commit (the path is absent from
#: every parent).  ``CONTENT``: the file's content as of that commit.
ANCHOR_ADDED = "ADDED_BY_THIS_COMMIT"
ANCHOR_CONTENT = "CONTENT_AT_THIS_COMMIT"

#: Lifecycle envelope.  Everything else is the authority payload, which must be
#: byte-for-byte the same content in an audited candidate and in the canonical
#: pointer activated from it (see :func:`pointer_payload_digest`).
ENVELOPE_KEYS = ("pointer_identity", "activation_basis")

#: PROPOSED activation contract.  It is part of the candidate and is itself
#: subject to independent audit.  No activation artifact exists and no digest
#: of one is stated, reserved or stubbed anywhere.
ACTIVATION_ROLES = (
    "audited_candidate",
    "independent_audit_record",
    "acceptance_closure",
    "acceptance_manifest",
)
ACTIVATION_AUDIT_ARTIFACT_TYPE = "CURRENT_MAINLINE_POINTER_INDEPENDENT_AUDIT_RECORD"
ACTIVATION_CLOSURE_ARTIFACT_TYPE = "CURRENT_MAINLINE_POINTER_ACCEPTANCE_CLOSURE"
ACTIVATION_MANIFEST_ARTIFACT_TYPE = "CURRENT_MAINLINE_POINTER_ACCEPTANCE_MANIFEST"

PURPOSE_TECHNICAL_IDENTITY_VERIFICATION = "TECHNICAL_IDENTITY_VERIFICATION"
PURPOSE_SCIENTIFIC_INSPECTION = "SCIENTIFIC_INSPECTION"
PURPOSE_RESULTS_ANALYSIS = "RESULTS_ANALYSIS"
PURPOSE_SUPERVISOR_DISCUSSION = "SUPERVISOR_DISCUSSION"
#: The only consumption purposes this interface knows.  Anything else is refused.
KNOWN_PURPOSES = (
    PURPOSE_TECHNICAL_IDENTITY_VERIFICATION,
    PURPOSE_SCIENTIFIC_INSPECTION,
    PURPOSE_RESULTS_ANALYSIS,
    PURPOSE_SUPERVISOR_DISCUSSION,
)

VERIFIER_MODULE_RELATIVE_PATH = "src/current_mainline_pointer_v1.py"
ACCEPTANCE_STATUS_CLOSED_ACCEPTED = "CLOSED_ACCEPTED"
#: The current governance status of a result set whose acceptance record says
#: CLOSED_ACCEPTED and whose publication is proven from Git.
GOVERNANCE_STATUS_PUBLISHED = "CLOSED / ACCEPTED / PUBLISHED"
RESULT_DURABILITY_LOCAL_ONLY = "LOCALLY_RETAINED_NOT_GIT_DURABLE"

#: Boundaries that follow from what a pointer is, stated by every pointer in
#: addition to the ones it carries from the accepted results acceptance.
POINTER_OWN_NON_AUTHORIZATIONS = (
    "NEW_FULL81_EXECUTION_OR_RERUN",
    "LAYER_B",
    "DG_EXTENSION",
    "U_01_RESOLUTION_OR_CALIBRATION",
    "DEPENDENCY_GRAPH",
    "SELECTIVE_RERUN_PLANNER",
    "CONTROLLED_EXECUTOR",
    "RENAMING_OF_HISTORICAL_VERSION_LABELS_OR_DIRECTORIES",
)

#: How a blocking flag of an open finding in the accepted results-acceptance
#: closure maps to consumption purposes the pointer must keep blocked.
CLOSURE_BLOCKING_FLAG_PURPOSES: Mapping[str, tuple[str, ...]] = {
    "blocking_for_first_scientific_inspection_of_full81_results": (
        PURPOSE_SCIENTIFIC_INSPECTION,
        PURPOSE_RESULTS_ANALYSIS,
    ),
    "blocking_for_supervisor_discussion_of_full81_results": (
        PURPOSE_SUPERVISOR_DISCUSSION,
    ),
}

#: Where the accepted results acceptance lists its open findings, and under
#: which keys it records their severity and disposition.
ACCEPTED_FINDING_LISTS = (
    ("new_findings_and_observations", "severity", "lifecycle_disposition"),
    ("findings_carried_not_closed", "severity_as_reported", "disposition_as_reported"),
)

#: The closure that accepted the results did not authorize a pointer.  This
#: step exists under a separate owner authorization, so that single item is not
#: carried forward as a boundary of the pointer itself; every other item is.
NON_AUTHORIZATION_ITEMS_NOT_CARRIED = frozenset({"CURRENT_MAINLINE_POINTER"})

#: The one case-id rule this interface implements (alpha outer, beta inner).
CASE_ID_RULE = "a{alpha:.2f}_b{beta_h:02d} over the Cartesian product"

#: Same algorithm as the accepted G1 identity digests.
IDENTITY_DIGEST_ALGORITHM = (
    "sha256 over json.dumps({path: sha256}, sort_keys=True, "
    "separators=(',',':')) encoded utf-8"
)
#: Same algorithm as the run-file aggregate recorded by the results acceptance.
RUN_FILE_AGGREGATE_ALGORITHM = (
    "sha256 over the UTF-8 concatenation of '<relative posix path>\\t<sha256>\\t<bytes>\\n' "
    "for every file under the run root, sorted by relative path (code-point order)"
)

CHECK_SCHEMA = "C01_SCHEMA"
CHECK_LIFECYCLE = "C02_POINTER_LIFECYCLE_AND_MODE"
CHECK_PATHS = "C03_PATH_CONTAINMENT"
CHECK_GIT = "C04_GIT_PROVENANCE"
CHECK_FILES = "C05_FILE_IDENTITIES_RAW_BYTES_AND_GIT_BLOBS"
CHECK_AXES = "C06_G1_IDENTITY_AXES"
CHECK_BINDINGS = "C07_GOVERNANCE_STATUS_AND_CROSS_BINDINGS"
CHECK_UNIVERSE = "C08_CASE_UNIVERSE_AND_RUN_BINDING"
CHECK_ROLES = "C09_ROLES_AND_CONFLICTING_CLAIMS"
CHECK_FINDINGS = "C10_OPEN_FINDINGS_AND_SCIENTIFIC_EXPOSURE"
CHECK_NON_AUTHORIZATION = "C11_NON_AUTHORIZATION_BOUNDARIES"
CHECK_RESULTS = "C12_LOCAL_RESULT_REGISTRATIONS"
CHECK_ACTIVATION = "C13_CANONICAL_ACTIVATION_BASIS"
CHECK_IDS = (
    CHECK_SCHEMA,
    CHECK_LIFECYCLE,
    CHECK_PATHS,
    CHECK_GIT,
    CHECK_FILES,
    CHECK_AXES,
    CHECK_BINDINGS,
    CHECK_UNIVERSE,
    CHECK_ROLES,
    CHECK_FINDINGS,
    CHECK_NON_AUTHORIZATION,
    CHECK_RESULTS,
    CHECK_ACTIVATION,
)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_NOT_RUN = "NOT_RUN"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{12}Z_[0-9a-f]{10}$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_MISSING: Any = object()


class PointerPathError(ValueError):
    """A pointer path is not a safe repository-relative POSIX path."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class CurrentMainlinePointerError(RuntimeError):
    """Raised by :func:`require_current_mainline`.  Carries the full result."""

    def __init__(self, code: str, result: Mapping[str, Any]) -> None:
        super().__init__(code)
        self.code = code
        self.result = dict(result)


# ---------------------------------------------------------------------------
# Hashing and path containment
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_identity_digest(identity: Mapping[str, str]) -> str:
    """Stable digest over a ``{path: sha256}`` map; order-independent."""

    payload = json.dumps(
        {str(k): str(v) for k, v in identity.items()},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def pointer_payload_digest(pointer: Mapping[str, Any]) -> str:
    """Digest of the authority payload: the pointer minus its lifecycle envelope.

    A canonical pointer must carry exactly the payload that was independently
    audited as a candidate.  The envelope is excluded so that neither file has
    to embed the other's hash.
    """

    payload = {k: v for k, v in pointer.items() if k not in ENVELOPE_KEYS}
    return sha256_bytes(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    )


def resolve_repository_path(root: Path, relative: Any) -> Path:
    """Resolve a repository-relative POSIX path, refusing every escape.

    Rejected: non-strings, absolute paths, drive letters, backslashes, empty,
    ``.`` and ``..`` segments, Windows alias forms, and any path whose real
    location differs from its lexical one (symlink, junction, case alias).
    """

    if not isinstance(relative, str) or not relative:
        raise PointerPathError("PATH_NOT_A_NONEMPTY_STRING", repr(relative))
    if "\\" in relative or "\x00" in relative or relative != relative.strip():
        raise PointerPathError("PATH_NOT_POSIX", relative)
    if relative.startswith(("/", "~")) or _WINDOWS_DRIVE_RE.match(relative):
        raise PointerPathError("PATH_ABSOLUTE", relative)
    segments = relative.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        raise PointerPathError("PATH_TRAVERSAL_SEGMENT", relative)
    if any(":" in segment or segment.endswith((".", " ")) for segment in segments):
        raise PointerPathError("PATH_UNSAFE_SEGMENT", relative)
    root_resolved = Path(root).resolve()
    lexical = root_resolved.joinpath(*segments)
    resolved = lexical.resolve()
    if str(resolved) != str(lexical):
        try:
            resolved.relative_to(root_resolved)
        except ValueError:
            raise PointerPathError("PATH_ESCAPES_REPOSITORY", relative) from None
        raise PointerPathError("PATH_REDIRECTED_OR_CASE_ALIASED", relative)
    return lexical


def expected_case_ids(
    alpha_universe: Sequence[Any], beta_universe_h: Sequence[Any]
) -> list[str]:
    """The case ids of the declared grid under :data:`CASE_ID_RULE`."""

    for alpha in alpha_universe:
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
            raise ValueError(f"alpha is not a number: {alpha!r}")
    for beta in beta_universe_h:
        if isinstance(beta, bool) or not isinstance(beta, int):
            raise ValueError(f"beta is not an integer: {beta!r}")
    return [
        f"a{float(alpha):.2f}_b{beta:02d}"
        for alpha in alpha_universe
        for beta in beta_universe_h
    ]


def _lookup(node: Any, path: Sequence[Any]) -> Any:
    for key in path:
        if isinstance(key, int):
            if not isinstance(node, list) or not 0 <= key < len(node):
                return _MISSING
            node = node[key]
        else:
            if not isinstance(node, Mapping) or key not in node:
                return _MISSING
            node = node[key]
    return node


def _show(value: Any) -> str:
    text = "<missing>" if value is _MISSING else repr(value)
    return text if len(text) <= 200 else text[:200] + "..."


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_FILE = "<file identity>"
_SHA = "<sha256>"
_COMMIT = "<commit>"
_AXIS = {"identity_class": str, "manifest_key": str, "digest": _SHA, "path_count": int}

#: Top level is closed-world: an unknown top-level key is refused.  Nested
#: objects are open-world: every listed key is required, extras are allowed.
POINTER_SCHEMA: Mapping[str, Any] = {
    "artifact_type": str,
    "schema_version": str,
    "pointer_revision": str,
    "documentation": {"purpose": str, "serialization": str, "path_convention": str},
    "pointer_identity": {
        "pointer_id": str,
        "lifecycle": str,
        "lifecycle_state": str,
        "is_candidate": bool,
        "is_accepted": bool,
        "is_canonical": bool,
        "is_current_authority": bool,
        "self_accepted": bool,
        "this_file_path": str,
        "proposed_canonical_path": str,
    },
    "activation_basis": {
        "status": str,
        "audited_candidate": (_FILE, None),
        "independent_audit_record": (_FILE, None),
        "acceptance_closure": (_FILE, None),
        "acceptance_manifest": (_FILE, None),
    },
    "methodology_authority": {
        "formal_name": str,
        "role": str,
        "lifecycle": str,
        "acceptance_commit": _COMMIT,
        "document": _FILE,
        "acceptance_closure": _FILE,
        "acceptance_manifest": _FILE,
    },
    "evidence_authority": {
        "formal_name": str,
        "role": str,
        "lifecycle": str,
        "acceptance_commit": _COMMIT,
        "document": _FILE,
        "independent_audit": _FILE,
        "acceptance_closure": _FILE,
        "acceptance_manifest": _FILE,
    },
    "production_generation": {
        "generation_id": str,
        "lineage_id": str,
        "candidate_id": str,
        "production_authority_freeze_status": str,
        "acceptance_status": str,
        "independent_audit_status": str,
        "accepted_lifecycle_record": _FILE,
        "lifecycle_roles": {
            "implementation_candidate": _FILE,
            "independent_audit_pass": _FILE,
            "acceptance_closure": _FILE,
            "acceptance_manifest": _FILE,
            "production_authority_re_freeze": _FILE,
        },
        "candidate_checkpoint": _FILE,
        "candidate_change_ledger": _FILE,
        "identity_axes": {
            "digest_algorithm": str,
            "path_list_source": _FILE,
            "runtime": _AXIS,
            "validation": _AXIS,
            "governance_authority": _AXIS,
        },
    },
    "full81_authorizations": {
        "scope_authorization": _FILE,
        "no_solve_preflight_evidence": _FILE,
        "execution_authorization": _FILE,
        "pointer_grants_execution_authority": bool,
    },
    "canonical_annual_input": _FILE,
    "implementation": {
        "scientific_model_core": _FILE,
        "production_successor_stack": _FILE,
        "production_runner": _FILE,
    },
    "economic_parameter_interfaces": {
        "parameter_registry": _FILE,
        "execution_input_authority": [_FILE],
        "solver_parameter_fingerprint": _SHA,
    },
    "accepted_result_set": {
        "result_namespace": str,
        "namespace_disposition": str,
        "run_id": str,
        "run_path": str,
        "case_set": str,
        "case_count": int,
        "case_universe": {
            "alpha_universe": [float],
            "beta_universe_h": [int],
            "case_id_rule": str,
            "grid_authority": str,
        },
        "root_artifacts": {
            "completion_manifest": _FILE,
            "authority": _FILE,
            "case_schedule": _FILE,
        },
        "registrations": {
            "files_under_run_root": int,
            "total_bytes": int,
            "root_registered_artifacts": int,
            "case_registered_artifacts": int,
            "unregistered_by_design": [str],
        },
        "run_file_aggregate": {"sha256": _SHA, "algorithm": str},
        "status_layers": {
            "execution_time_completion_manifest_status": str,
            "execution_time_case_status": str,
            "execution_time_authority_status": str,
            "execution_time_optimization_calls": int,
            "current_governance_status": str,
        },
        "git_durability": {"result_files_git_tracked": int, "status": str},
    },
    "independent_audit_evidence_publication": {
        "package_id": str,
        "publication_commit": _COMMIT,
        "result_acceptance_status_recorded_at_publication": str,
        "independent_audit_report": _FILE,
        "audit_evidence_record": _FILE,
        "publication_manifest": _FILE,
        "checkpoint": _FILE,
    },
    "formal_results_acceptance": {
        "package_id": str,
        "acceptance_status": str,
        "acceptance_subject": str,
        "governance_status": str,
        "publication_commit": _COMMIT,
        "acceptance_closure": _FILE,
        "acceptance_manifest": _FILE,
        "checkpoint": _FILE,
    },
    "git_provenance": {
        "branch": str,
        "upstream_ref": str,
        "historical_execution_commit": _COMMIT,
        "audit_evidence_publication_commit": _COMMIT,
        "results_acceptance_publication_commit": _COMMIT,
        "ancestry_chain_oldest_to_newest": [_COMMIT],
        "direct_parent_links": [[_COMMIT]],
        "live_head_must_equal_a_recorded_commit": bool,
    },
    "roles": {
        "accepted_current": [{"role": str, "path": str}],
        "accepted_other_scope_not_bound_by_this_pointer": [{"role": str, "path": str}],
        "historical_only": [{"role": str, "path": str}],
    },
    "open_findings_and_limitations": {
        "findings": [
            {
                "id": str,
                "accepted_list": str,
                "severity": str,
                "disposition": str,
                "closed": bool,
                "blocks_purposes": [str],
                "resolution_evidence": (_FILE, None),
            }
        ],
        "unresolved_register": {
            "U-01": {
                "status": str,
                "blocks_main_full81": bool,
                "must_be_frozen_before": [str],
            }
        },
        "limitations_carried_from_results_acceptance": [{"id": str, "statement": str}],
        "fixture_control_limitation": {"id": str, "passed": int, "total": int, "not_claimed": str},
        "closed_or_remediated_by_this_pointer": [str],
    },
    "scientific_exposure_restrictions": {
        "governing_finding": str,
        "governing_clause": _FILE,
        "exposure_log": {
            "established": bool,
            "path": (str, None),
            "entries_created_by_this_pointer": int,
            "this_pointer_is_an_exposure_log": bool,
        },
        "blocked_purposes": [str],
        "permitted_purposes": [str],
        "carry_forward_conditions": [str],
    },
    "non_authorization_boundaries": {
        "pointer_grants_execution_authority": bool,
        "authorizes": [str],
        "not_authorized_by_this_pointer": [str],
        "a2_variable_floor_status": str,
    },
    "validation_contract": {
        "verifier_module": str,
        "verifier_interface_version": str,
        "required_checks": [str],
    },
}


def _schema_problems(node: Any, spec: Any, where: str, problems: list[str]) -> None:
    if isinstance(spec, tuple):
        trial: list[str] = []
        for alternative in spec:
            trial = []
            if alternative is None:
                if node is None:
                    return
                trial.append(f"{where}: expected null")
                continue
            _schema_problems(node, alternative, where, trial)
            if not trial:
                return
        problems.append(f"{where}: matches no permitted form")
    elif isinstance(spec, Mapping):
        if not isinstance(node, Mapping):
            problems.append(f"{where}: expected an object")
            return
        for key, sub in spec.items():
            if key not in node:
                problems.append(f"{where}.{key}: missing")
            else:
                _schema_problems(node[key], sub, f"{where}.{key}", problems)
    elif isinstance(spec, list):
        if not isinstance(node, list):
            problems.append(f"{where}: expected a list")
            return
        for index, item in enumerate(node):
            _schema_problems(item, spec[0], f"{where}[{index}]", problems)
    elif spec == _FILE:
        _file_identity_problems(node, where, problems)
    elif spec == _SHA:
        if not isinstance(node, str) or not _SHA256_RE.match(node):
            problems.append(f"{where}: expected a lowercase SHA-256")
    elif spec == _COMMIT:
        if not isinstance(node, str) or not _COMMIT_RE.match(node):
            problems.append(f"{where}: expected a full 40-hex commit id")
    elif spec is float:
        if isinstance(node, bool) or not isinstance(node, (int, float)):
            problems.append(f"{where}: expected a number")
    elif spec is int:
        if isinstance(node, bool) or not isinstance(node, int):
            problems.append(f"{where}: expected an integer")
    elif not isinstance(node, spec):
        problems.append(f"{where}: expected {spec.__name__}")


def _file_identity_problems(node: Any, where: str, problems: list[str]) -> None:
    if not isinstance(node, Mapping):
        problems.append(f"{where}: expected a file identity object")
        return
    if not isinstance(node.get("path"), str) or not node.get("path"):
        problems.append(f"{where}.path: missing")
    sha = node.get("sha256")
    if not isinstance(sha, str) or not _SHA256_RE.match(sha):
        problems.append(f"{where}.sha256: expected a lowercase SHA-256")
    size = node.get("bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        problems.append(f"{where}.bytes: expected a non-negative integer")
    tracked = node.get("git_tracked")
    if not isinstance(tracked, bool):
        problems.append(f"{where}.git_tracked: expected a boolean")
        return
    blob, anchor = node.get("git_blob_id", _MISSING), node.get("git_anchor_commit", _MISSING)
    if tracked:
        if not isinstance(blob, str) or not _COMMIT_RE.match(blob):
            problems.append(f"{where}.git_blob_id: expected a 40-hex blob id")
        if not isinstance(anchor, str) or not _COMMIT_RE.match(anchor):
            problems.append(f"{where}.git_anchor_commit: expected a full commit id")
        if node.get("git_anchor_role") not in (ANCHOR_ADDED, ANCHOR_CONTENT):
            problems.append(f"{where}.git_anchor_role: expected an anchor role")
    elif blob is not None or anchor is not None or node.get("git_anchor_role") is not None:
        problems.append(f"{where}: an untracked identity must carry null Git fields")


def _is_file_identity(node: Any) -> bool:
    return isinstance(node, Mapping) and "path" in node and "sha256" in node


def _walk(node: Any, where: str = "") -> Iterator[tuple[str, str, Any, Any]]:
    """Yield ``(location, key, value, parent)`` for every mapping entry."""

    if isinstance(node, Mapping):
        for key, value in node.items():
            location = f"{where}.{key}" if where else str(key)
            yield location, str(key), value, node
            yield from _walk(value, location)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            location = f"{where}[{index}]"
            yield location, "", value, node
            yield from _walk(value, location)


def is_descriptive_key(key: Any) -> bool:
    """Explanatory text for human readers; nothing under such a key is verified.

    Every other leaf of the authority payload is checked against a primary
    artifact, a Git object or this interface.
    """

    return isinstance(key, str) and (key in ("note", "documentation") or key.endswith("_note"))


#: Keys whose string values are repository paths even though they are not named
#: ``path`` and do not end in ``_path``.
_EXTRA_PATH_KEYS = frozenset({"result_namespace", "verifier_module"})


def _is_path_key(key: str) -> bool:
    return key == "path" or key.endswith("_path") or key in _EXTRA_PATH_KEYS


# ---------------------------------------------------------------------------
# Read-only Git access
# ---------------------------------------------------------------------------

#: The only Git subcommands this module may run.  None of them writes a ref,
#: an object, the index or the working tree.
_GIT_READ_ONLY_SUBCOMMANDS = frozenset(
    {"rev-parse", "cat-file", "merge-base", "ls-tree", "ls-files", "rev-list", "symbolic-ref"}
)


class _Git:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._trees: dict[str, dict[str, str]] = {}
        self._blobs: dict[str, tuple[str, int] | None] = {}
        self._reachable: dict[str, frozenset[str]] = {}
        self._parents: dict[str, list[str]] = {}

    def run(self, *args: str, stdin: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
        if not args or args[0] not in _GIT_READ_ONLY_SUBCOMMANDS:
            raise RuntimeError(f"refused non-read-only git subcommand: {args[:1]!r}")
        environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        command = ["git", "-c", "core.quotepath=false", *args]
        if stdin is None:
            return subprocess.run(
                command,
                cwd=self.root,
                env=environment,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                check=False,
            )
        return subprocess.run(
            command, cwd=self.root, env=environment, input=stdin, capture_output=True, check=False
        )

    def rev(self, spec: str) -> str | None:
        done = self.run("rev-parse", "--verify", "--quiet", spec)
        text = done.stdout.decode("utf-8", "replace").strip()
        return text if done.returncode == 0 and text else None

    def is_commit(self, sha: str) -> bool:
        return self.rev(f"{sha}^{{commit}}") == sha

    def is_ancestor(self, older: str, newer: str) -> bool:
        return self.run("merge-base", "--is-ancestor", older, newer).returncode == 0

    def reachable_from(self, revision: str) -> frozenset[str]:
        """Every commit reachable from ``revision``, itself included."""

        if revision not in self._reachable:
            done = self.run("rev-list", revision)
            listed = done.stdout.decode("utf-8", "replace").split() if done.returncode == 0 else []
            self._reachable[revision] = frozenset(listed)
        return self._reachable[revision]

    def parents(self, sha: str) -> list[str]:
        if sha not in self._parents:
            done = self.run("rev-list", "--parents", "-n", "1", sha)
            listed = done.stdout.decode("utf-8", "replace").split() if done.returncode == 0 else []
            self._parents[sha] = listed[1:]
        return list(self._parents[sha])

    def last_commit_touching(self, relative: str) -> str | None:
        done = self.run("rev-list", "-1", "HEAD", "--", relative)
        text = done.stdout.decode("utf-8", "replace").strip()
        return text if done.returncode == 0 and text else None

    def branch(self) -> str | None:
        done = self.run("symbolic-ref", "--short", "-q", "HEAD")
        text = done.stdout.decode("utf-8", "replace").strip()
        return text or None

    def tree(self, commit: str) -> dict[str, str]:
        """``{path: blob id}`` of every blob in ``commit``'s tree."""

        if commit not in self._trees:
            done = self.run("ls-tree", "-r", "-z", "--full-tree", commit)
            blobs: dict[str, str] = {}
            if done.returncode == 0:
                for record in done.stdout.split(b"\0"):
                    meta, _, path = record.partition(b"\t")
                    fields = meta.split()
                    if len(fields) == 3 and fields[1] == b"blob":
                        blobs[path.decode("utf-8", "surrogateescape")] = fields[2].decode()
            self._trees[commit] = blobs
        return self._trees[commit]

    def blob_digests(self, blob_ids: Sequence[str]) -> dict[str, tuple[str, int] | None]:
        """``{blob id: (sha256 of blob bytes, size)}``; ``None`` if not a blob."""

        wanted = [b for b in dict.fromkeys(blob_ids) if b not in self._blobs]
        if wanted:
            done = self.run("cat-file", "--batch", stdin=("\n".join(wanted) + "\n").encode())
            data, position = done.stdout, 0
            for blob_id in wanted:
                self._blobs[blob_id] = None
                newline = data.find(b"\n", position)
                if newline < 0:
                    break
                header = data[position:newline].split(b" ")
                position = newline + 1
                if len(header) == 3 and header[1] in (b"blob", b"tree", b"commit", b"tag"):
                    size = int(header[2])
                    content = data[position : position + size]
                    position += size + 1
                    if header[1] == b"blob" and len(content) == size:
                        self._blobs[blob_id] = (sha256_bytes(content), size)
        return {b: self._blobs.get(b) for b in blob_ids}

    def blob_bytes(self, blob_id: str) -> bytes | None:
        done = self.run("cat-file", "blob", blob_id)
        return done.stdout if done.returncode == 0 else None

    def tracked_under(self, relative: str) -> list[str]:
        done = self.run("ls-files", "-z", "--", relative)
        return [p.decode("utf-8", "surrogateescape") for p in done.stdout.split(b"\0") if p]


# ---------------------------------------------------------------------------
# Cross-bindings: what each accepted record must say, and where the pointer
# says the same thing.  One row = one equality.
# ---------------------------------------------------------------------------


class _Literal:
    """An expected value fixed by the meaning of the record, not by the pointer."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


_GENERATION = ("production_generation",)
_LIFECYCLE = (*_GENERATION, "accepted_lifecycle_record")
_ROLES = (*_GENERATION, "lifecycle_roles")
_AXES = (*_GENERATION, "identity_axes")
_SCOPE = ("full81_authorizations", "scope_authorization")
_PREFLIGHT = ("full81_authorizations", "no_solve_preflight_evidence")
_EXECUTION = ("full81_authorizations", "execution_authorization")
_INPUT = ("canonical_annual_input",)
_CORE = ("implementation", "scientific_model_core")
_STACK = ("implementation", "production_successor_stack")
_RUNNER = ("implementation", "production_runner")
_ECONOMIC = ("economic_parameter_interfaces",)
_RESULTS = ("accepted_result_set",)
_UNIVERSE = (*_RESULTS, "case_universe")
_ROOT = (*_RESULTS, "root_artifacts")
_REGISTRATIONS = (*_RESULTS, "registrations")
_LAYERS = (*_RESULTS, "status_layers")
_AUDIT = ("independent_audit_evidence_publication",)
_ACCEPTANCE = ("formal_results_acceptance",)
_PROVENANCE = ("git_provenance",)
_FRAMEWORK = ("methodology_authority", "document")
_REGISTRY = ("evidence_authority", "document")
_U01 = ("open_findings_and_limitations", "unresolved_register", "U-01")
_LIMITATION = ("open_findings_and_limitations", "fixture_control_limitation")

#: Tracked JSON records the cross-bindings read, by pointer location.
TRACKED_RECORDS: Mapping[str, tuple[str, ...]] = {
    "g1_candidate_manifest": (*_AXES, "path_list_source"),
    "g1_accepted_lifecycle": _LIFECYCLE,
    "scope_authorization": _SCOPE,
    "execution_authorization": _EXECUTION,
    "audit_publication_manifest": (*_AUDIT, "publication_manifest"),
    "results_acceptance_closure": (*_ACCEPTANCE, "acceptance_closure"),
    "results_acceptance_manifest": (*_ACCEPTANCE, "acceptance_manifest"),
}
#: Local, gitignored run records; read only under a results policy.
LOCAL_RECORDS: Mapping[str, tuple[str, ...]] = {
    "run_authority": (*_ROOT, "authority"),
    "run_completion_manifest": (*_ROOT, "completion_manifest"),
}


def _same_file(
    record: str, keys: tuple, pointer: tuple, fields: Sequence[str] = ("path", "sha256")
) -> list[tuple]:
    return [(record, (*keys, field), (*pointer, field)) for field in fields]


def _axis_rows(record: str, keys_for: Mapping[str, tuple]) -> list[tuple]:
    rows: list[tuple] = []
    for axis, keys in keys_for.items():
        rows.append((record, (*keys, "digest"), (*_AXES, axis, "digest")))
        rows.append((record, (*keys, "path_count"), (*_AXES, axis, "path_count")))
    return rows


def _build_cross_bindings() -> tuple[tuple[str, tuple, Any], ...]:
    rows: list[tuple[str, tuple, Any]] = []

    record = "g1_candidate_manifest"
    rows += [
        (record, ("artifact_type",), (*_AXES, "path_list_source", "artifact_type")),
        (record, ("generation_id",), (*_GENERATION, "generation_id")),
        (record, ("candidate_id",), (*_GENERATION, "candidate_id")),
        (record, ("self_accepted",), _Literal(False)),
        (record, ("implementation_identity_digest",), (*_AXES, "runtime", "digest")),
    ]
    for axis in ("runtime", "validation", "governance_authority"):
        key = f"{axis}_identity"
        rows += [
            (record, (key, "digest"), (*_AXES, axis, "digest")),
            (record, (key, "path_count"), (*_AXES, axis, "path_count")),
            (record, (key, "identity_class"), (*_AXES, axis, "identity_class")),
            (record, (key, "digest_algorithm"), (*_AXES, "digest_algorithm")),
        ]

    record = "g1_accepted_lifecycle"
    rows += [
        (record, ("artifact_type",), (*_LIFECYCLE, "artifact_type")),
        (record, ("generation_id",), (*_GENERATION, "generation_id")),
        (record, ("lineage_id",), (*_GENERATION, "lineage_id")),
        (record, ("target_candidate_id",), (*_GENERATION, "candidate_id")),
        (
            record,
            ("production_authority_freeze_status",),
            (*_GENERATION, "production_authority_freeze_status"),
        ),
        (record, ("u06_acceptance_status",), (*_GENERATION, "acceptance_status")),
        (record, ("u06_independent_audit_status",), (*_GENERATION, "independent_audit_status")),
        (record, ("authorizes_main_full81",), _Literal(False)),
        (record, ("implementation_identity_digest",), (*_AXES, "runtime", "digest")),
        (record, ("implementation_identity_path_count",), (*_AXES, "runtime", "path_count")),
    ]
    rows += _axis_rows(
        record,
        {
            axis: ("g1_identity_axes", axis)
            for axis in ("runtime", "validation", "governance_authority")
        },
    )
    for role in (
        "implementation_candidate",
        "independent_audit_pass",
        "acceptance_closure",
        "acceptance_manifest",
        "production_authority_re_freeze",
    ):
        rows += _same_file(record, ("roles", role), (*_ROLES, role))
    rows += _same_file(record, ("candidate_checkpoint",), (*_GENERATION, "candidate_checkpoint"))
    rows += _same_file(
        record, ("candidate_change_ledger",), (*_GENERATION, "candidate_change_ledger")
    )
    rows += _same_file(record, ("candidate_manifest",), (*_AXES, "path_list_source"))

    record = "scope_authorization"
    rows += [
        (record, ("artifact_type",), (*_SCOPE, "artifact_type")),
        (record, ("authorization_status",), (*_SCOPE, "authorization_status")),
        (record, ("authorizes",), (*_SCOPE, "authorized_historically_by_this_record")),
        (record, ("authorizes_full81_execution",), (*_SCOPE, "authorizes_full81_execution")),
        (record, ("authorizes_optimize_calls",), _Literal(False)),
        (record, ("production_authority_generation_id",), (*_GENERATION, "generation_id")),
        (record, ("candidate_id",), (*_GENERATION, "candidate_id")),
        (
            record,
            ("production_authority_freeze_status",),
            (*_GENERATION, "production_authority_freeze_status"),
        ),
        (
            record,
            ("production_authority_publication_commit",),
            (*_LIFECYCLE, "git_anchor_commit"),
        ),
        (record, ("implementation_identity_digest",), (*_AXES, "runtime", "digest")),
        (record, ("target_runner", "version"), (*_RUNNER, "version")),
        (record, ("alpha_universe",), (*_UNIVERSE, "alpha_universe")),
        (record, ("beta_universe_h",), (*_UNIVERSE, "beta_universe_h")),
        (record, ("case_count",), (*_RESULTS, "case_count")),
        (
            record,
            ("solver_parameter_fingerprint",),
            (*_ECONOMIC, "solver_parameter_fingerprint"),
        ),
        (record, ("u_01_status",), (*_U01, "status")),
        (record, ("u_01_blocks_main_full81",), (*_U01, "blocks_main_full81")),
        (record, ("u_01_must_be_frozen_before",), (*_U01, "must_be_frozen_before")),
        (
            record,
            ("reserve_floor_methodology_boundary", "excluded_extension_status"),
            ("non_authorization_boundaries", "a2_variable_floor_status"),
        ),
    ]
    rows += _same_file(record, ("production_authority_accepted_lifecycle_record",), _LIFECYCLE)
    rows += _same_file(record, ("canonical_annual_input",), _INPUT)
    rows += _same_file(record, ("accepted_annual_model",), _CORE)
    rows += _same_file(record, ("parameter_registry",), (*_ECONOMIC, "parameter_registry"))
    rows += _same_file(record, ("target_runner",), _RUNNER)

    record = "execution_authorization"
    rows += [
        (record, ("artifact_type",), (*_EXECUTION, "artifact_type")),
        (
            record,
            ("execution_authorization_status",),
            (*_EXECUTION, "execution_authorization_status"),
        ),
        (
            record,
            ("authorization_semantic_boundary",),
            (*_EXECUTION, "authorization_semantic_boundary"),
        ),
        (record, ("restart_policy",), (*_EXECUTION, "restart_policy")),
        (record, ("authorizes",), (*_EXECUTION, "authorized_historically_by_this_record")),
        (record, ("excluded_scopes",), (*_EXECUTION, "excluded_scopes")),
        (record, ("authorizes_a2",), _Literal(False)),
        (record, ("authorizes_sensitivity_solves",), _Literal(False)),
        (record, ("case_set",), (*_RESULTS, "case_set")),
        (record, ("case_count",), (*_RESULTS, "case_count")),
        (record, ("production_authority_generation_id",), (*_GENERATION, "generation_id")),
        (record, ("candidate_id",), (*_GENERATION, "candidate_id")),
        (
            record,
            ("production_authority_publication_commit",),
            (*_LIFECYCLE, "git_anchor_commit"),
        ),
        (record, ("scope_authorization_publication_commit",), (*_SCOPE, "git_anchor_commit")),
        (
            record,
            ("no_solve_preflight_publication_commit",),
            (*_PREFLIGHT, "git_anchor_commit"),
        ),
        (record, ("implementation_identity_digest",), (*_AXES, "runtime", "digest")),
        (record, ("target_runner", "version"), (*_RUNNER, "version")),
        (record, ("alpha_universe",), (*_UNIVERSE, "alpha_universe")),
        (record, ("beta_universe_h",), (*_UNIVERSE, "beta_universe_h")),
        (
            record,
            ("solver_parameter_fingerprint",),
            (*_ECONOMIC, "solver_parameter_fingerprint"),
        ),
    ]
    rows += _same_file(record, ("production_authority_accepted_lifecycle_record",), _LIFECYCLE)
    rows += _same_file(record, ("scope_authorization",), _SCOPE)
    rows += _same_file(record, ("no_solve_preflight_evidence",), _PREFLIGHT)
    rows += _same_file(record, ("target_runner",), _RUNNER)

    record = "audit_publication_manifest"
    rows += [
        (record, ("artifact_type",), (*_AUDIT, "publication_manifest", "artifact_type")),
        (record, ("package_id",), (*_AUDIT, "package_id")),
        (
            record,
            ("result_acceptance_status",),
            (*_AUDIT, "result_acceptance_status_recorded_at_publication"),
        ),
        (record, ("is_result_acceptance",), _Literal(False)),
        (record, ("target_run", "path"), (*_RESULTS, "run_path")),
        (
            record,
            ("target_run", "root_completion_manifest_sha256"),
            (*_ROOT, "completion_manifest", "sha256"),
        ),
    ]
    triple = ("path", "sha256", "bytes")
    rows += _same_file(
        record, ("internal_package_files", 0), (*_AUDIT, "independent_audit_report"), triple
    )
    rows += _same_file(
        record, ("internal_package_files", 1), (*_AUDIT, "audit_evidence_record"), triple
    )
    rows += _same_file(
        record, ("external_registered_artifacts", 0), (*_AUDIT, "checkpoint"), triple
    )

    record = "results_acceptance_manifest"
    references = ("accepted_evidence_references",)
    rows += [
        (record, ("artifact_type",), (*_ACCEPTANCE, "acceptance_manifest", "artifact_type")),
        (record, ("package_id",), (*_ACCEPTANCE, "package_id")),
        (record, ("acceptance_status",), (*_ACCEPTANCE, "acceptance_status")),
        (record, ("acceptance_subject",), (*_ACCEPTANCE, "acceptance_subject")),
        (record, ("is_current_mainline_pointer",), _Literal(False)),
        (record, ("is_exposure_log_or_exposure_event",), _Literal(False)),
        (record, ("target_run", "path"), (*_RESULTS, "run_path")),
        (
            record,
            ("target_run", "root_completion_manifest_sha256"),
            (*_ROOT, "completion_manifest", "sha256"),
        ),
        (record, (*references, "phase_a_publication_commit"), (*_AUDIT, "publication_commit")),
        (record, (*references, "execution_head"), (*_PROVENANCE, "historical_execution_commit")),
        (record, (*references, "g1_runtime_identity_digest"), (*_AXES, "runtime", "digest")),
        (
            record,
            (*references, "target_run_root_completion_manifest", "git_tracked"),
            _Literal(False),
        ),
    ]
    rows += _same_file(
        record, ("internal_package_files", 0), (*_ACCEPTANCE, "acceptance_closure"), triple
    )
    rows += _same_file(
        record, ("external_registered_artifacts", 0), (*_ACCEPTANCE, "checkpoint"), triple
    )
    rows += _same_file(
        record,
        (*references, "target_run_root_completion_manifest"),
        (*_ROOT, "completion_manifest"),
        triple,
    )
    rows += _same_file(record, (*references, "g1_accepted_lifecycle_record"), _LIFECYCLE)
    rows += _same_file(record, (*references, "main_full81_execution_authorization"), _EXECUTION)
    rows += _same_file(record, (*references, "framework_v7_4"), _FRAMEWORK)
    rows += _same_file(record, (*references, "registry_v7_4"), _REGISTRY)
    rows += _same_file(record, (*references, "canonical_annual_input"), _INPUT)

    record = "results_acceptance_closure"
    run = ("target_run",)
    rows += [
        (record, ("artifact_type",), (*_ACCEPTANCE, "acceptance_closure", "artifact_type")),
        (record, ("package_id",), (*_ACCEPTANCE, "package_id")),
        (record, ("acceptance_status",), (*_ACCEPTANCE, "acceptance_status")),
        (record, ("acceptance_subject",), (*_ACCEPTANCE, "acceptance_subject")),
        (record, ("record_distinctions", "is_current_mainline_pointer"), _Literal(False)),
        (record, ("record_distinctions", "is_exposure_log_or_exposure_event"), _Literal(False)),
        (
            record,
            ("lifecycle_status", "results_governance_status_decided"),
            (*_ACCEPTANCE, "acceptance_status"),
        ),
        (
            record,
            ("lifecycle_status", "run_completion_manifest_status_unchanged"),
            (*_LAYERS, "execution_time_completion_manifest_status"),
        ),
        (record, (*run, "run_id"), (*_RESULTS, "run_id")),
        (record, (*run, "path"), (*_RESULTS, "run_path")),
        (record, (*run, "case_set"), (*_RESULTS, "case_set")),
        (record, (*run, "file_count"), (*_REGISTRATIONS, "files_under_run_root")),
        (record, (*run, "total_bytes"), (*_REGISTRATIONS, "total_bytes")),
        (
            record,
            (*run, "root_registered_artifacts"),
            (*_REGISTRATIONS, "root_registered_artifacts"),
        ),
        (record, (*run, "case_registry_entries"), (*_REGISTRATIONS, "case_registered_artifacts")),
        (
            record,
            (*run, "files_not_registered_in_root_manifest"),
            (*_REGISTRATIONS, "unregistered_by_design"),
        ),
        (
            record,
            (*run, "run_file_aggregate_sha256_at_authoring"),
            (*_RESULTS, "run_file_aggregate", "sha256"),
        ),
        (
            record,
            (*run, "run_file_aggregate_algorithm"),
            (*_RESULTS, "run_file_aggregate", "algorithm"),
        ),
        (
            record,
            (*run, "files_tracked_by_git"),
            (*_RESULTS, "git_durability", "result_files_git_tracked"),
        ),
        (
            record,
            ("execution_identity", "execution_head"),
            (*_PROVENANCE, "historical_execution_commit"),
        ),
        (record, ("execution_identity", "execution_branch"), (*_PROVENANCE, "branch")),
        (
            record,
            ("execution_identity", "production_generation_id"),
            (*_GENERATION, "generation_id"),
        ),
        (record, ("execution_identity", "candidate_id"), (*_GENERATION, "candidate_id")),
        (record, ("execution_identity", "core_version"), (*_CORE, "version")),
        (record, ("execution_identity", "stack_version"), (*_STACK, "version")),
        (
            record,
            ("execution_identity", "run_authority_status"),
            (*_LAYERS, "execution_time_authority_status"),
        ),
        (
            record,
            ("methodology_evidence_authority", "framework", "formal_name"),
            ("methodology_authority", "formal_name"),
        ),
        (
            record,
            ("methodology_evidence_authority", "framework", "role"),
            ("methodology_authority", "role"),
        ),
        (
            record,
            ("methodology_evidence_authority", "framework", "lifecycle"),
            ("methodology_authority", "lifecycle"),
        ),
        (
            record,
            ("methodology_evidence_authority", "registry", "formal_name"),
            ("evidence_authority", "formal_name"),
        ),
        (
            record,
            ("methodology_evidence_authority", "registry", "role"),
            ("evidence_authority", "role"),
        ),
        (
            record,
            ("methodology_evidence_authority", "registry", "lifecycle"),
            ("evidence_authority", "lifecycle"),
        ),
        (
            record,
            ("implementation_identities", "digest_algorithm"),
            (*_AXES, "digest_algorithm"),
        ),
        (
            record,
            ("full81_contract_coverage", "expected_case_count"),
            (*_RESULTS, "case_count"),
        ),
        (record, ("full81_contract_coverage", "alpha_grid"), (*_UNIVERSE, "alpha_universe")),
        (record, ("full81_contract_coverage", "beta_grid_h"), (*_UNIVERSE, "beta_universe_h")),
        (record, ("full81_contract_coverage", "case_id_rule"), (*_UNIVERSE, "case_id_rule")),
        (
            record,
            ("methodology_evidence_authority", "grid_authority"),
            (*_UNIVERSE, "grid_authority"),
        ),
        (
            record,
            ("evidence_classifications", "independent_numerical_acceptance"),
            (*_AUDIT, "evidence_grade"),
        ),
        (
            record,
            ("binding_carry_forward_conditions",),
            ("scientific_exposure_restrictions", "carry_forward_conditions"),
        ),
        (
            record,
            ("implementation_identities", "canonical_annual_input", "row_count_as_stored"),
            (*_INPUT, "rows"),
        ),
        *(
            (record, ("fixture_control_limitation", field), (*_LIMITATION, field))
            for field in ("id", "passed", "total", "not_claimed")
        ),
        (
            record,
            ("phase_a_publication_verification", "publication_commit"),
            (*_AUDIT, "publication_commit"),
        ),
    ]
    rows += _axis_rows(
        record,
        {
            axis: ("implementation_identities", axis)
            for axis in ("runtime", "validation", "governance_authority")
        },
    )
    rows += _same_file(
        record, ("methodology_evidence_authority", "framework"), _FRAMEWORK, triple
    )
    rows += _same_file(record, ("methodology_evidence_authority", "registry"), _REGISTRY, triple)
    rows += _same_file(
        record, ("implementation_identities", "canonical_annual_input"), _INPUT, triple
    )
    rows += _same_file(
        record,
        ("g1_authority_chain", "governing_sequencing_authority"),
        ("scientific_exposure_restrictions", "governing_clause"),
    )

    record = "run_authority"
    authority = ("v7_4_production_authority",)
    rows += [
        (record, ("head",), (*_PROVENANCE, "historical_execution_commit")),
        (record, ("origin_head",), (*_PROVENANCE, "historical_execution_commit")),
        (record, ("branch",), (*_PROVENANCE, "branch")),
        (record, ("selected_scope",), (*_RESULTS, "case_set")),
        (record, ("status",), (*_LAYERS, "execution_time_authority_status")),
        (record, ("expected_full_surface_cases",), (*_RESULTS, "case_count")),
        (record, ("alpha_grid",), (*_UNIVERSE, "alpha_universe")),
        (record, ("beta_grid_h",), (*_UNIVERSE, "beta_universe_h")),
        (record, ("core_module",), (*_CORE, "path")),
        (record, (*authority, "model_core", "role"), (*_CORE, "role")),
        (record, (*authority, "production_successor_stack", "role"), (*_STACK, "role")),
        (record, (*authority, "full81_runner", "role"), (*_RUNNER, "role")),
        (
            record,
            (*authority, "parameter_registry", "role"),
            (*_ECONOMIC, "parameter_registry", "role"),
        ),
        (record, ("core_version",), (*_CORE, "version")),
        (record, ("stack_version",), (*_STACK, "version")),
        (
            record,
            ("production_authority_freeze_status",),
            (*_GENERATION, "production_authority_freeze_status"),
        ),
        (record, ("annual_identity", "artifact_role"), (*_INPUT, "role")),
        (record, ("annual_identity", "row_count"), (*_INPUT, "rows")),
        (record, ("u06_accepted_lifecycle", "generation_id"), (*_GENERATION, "generation_id")),
        (record, ("u06_accepted_lifecycle", "record_path"), (*_LIFECYCLE, "path")),
        (
            record,
            ("u06_accepted_lifecycle", "implementation_identity_digest"),
            (*_AXES, "runtime", "digest"),
        ),
        (
            record,
            (*authority, "output_namespace", "disposition"),
            (*_RESULTS, "namespace_disposition"),
        ),
        (
            record,
            (*authority, "registry", "acceptance_commit"),
            ("evidence_authority", "acceptance_commit"),
        ),
    ]
    rows += _same_file(record, ("annual_identity",), _INPUT)
    rows += _same_file(record, (*authority, "framework"), _FRAMEWORK)
    rows += _same_file(record, (*authority, "registry"), _REGISTRY)
    rows += _same_file(record, (*authority, "canonical_planning_input"), _INPUT)
    rows += _same_file(record, (*authority, "model_core"), _CORE)
    rows += _same_file(record, (*authority, "production_successor_stack"), _STACK)
    rows += _same_file(record, (*authority, "full81_runner"), _RUNNER)
    rows += _same_file(
        record, (*authority, "parameter_registry"), (*_ECONOMIC, "parameter_registry")
    )

    record = "run_completion_manifest"
    rows += [
        (record, ("status",), (*_LAYERS, "execution_time_completion_manifest_status")),
        (record, ("case_set",), (*_RESULTS, "case_set")),
        (record, ("case_count",), (*_RESULTS, "case_count")),
        (record, ("optimization_calls",), (*_LAYERS, "execution_time_optimization_calls")),
    ]
    return tuple(rows)


#: ``(record, key path inside the record, pointer path or literal)``.
CROSS_BINDINGS = _build_cross_bindings()

#: The complete, ordered accepted-current role list: each label and the pointer
#: location whose path carries it.  Nothing else is current (default deny).
ACCEPTED_CURRENT_ROLES: tuple[tuple[str, tuple], ...] = (
    ("CURRENT_METHODOLOGY_AUTHORITY", (*_FRAMEWORK, "path")),
    ("CURRENT_EVIDENCE_AUTHORITY", (*_REGISTRY, "path")),
    ("CURRENT_PRODUCTION_GENERATION_ACCEPTED_LIFECYCLE", (*_LIFECYCLE, "path")),
    ("CANONICAL_ANNUAL_PLANNING_INPUT", (*_INPUT, "path")),
    ("ACCEPTED_SCIENTIFIC_MODEL_CORE", (*_CORE, "path")),
    ("PRODUCTION_SUCCESSOR_STACK", (*_STACK, "path")),
    ("PRODUCTION_RUNNER", (*_RUNNER, "path")),
    ("ACCEPTED_CURRENT_FULL81_LAYER_A_RESULT_SET", (*_RESULTS, "run_path")),
    ("FORMAL_FULL81_RESULTS_ACCEPTANCE", (*_ACCEPTANCE, "acceptance_closure", "path")),
)

#: Pairs of pointer locations that must agree with each other.
INTERNAL_EQUALITIES: tuple[tuple[tuple, tuple], ...] = (
    ((*_EXECUTION, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_AUDIT, "publication_commit"), (*_PROVENANCE, "audit_evidence_publication_commit")),
    (
        (*_ACCEPTANCE, "publication_commit"),
        (*_PROVENANCE, "results_acceptance_publication_commit"),
    ),
    ((*_AUDIT, "independent_audit_report", "git_anchor_commit"), (*_AUDIT, "publication_commit")),
    ((*_AUDIT, "audit_evidence_record", "git_anchor_commit"), (*_AUDIT, "publication_commit")),
    ((*_AUDIT, "publication_manifest", "git_anchor_commit"), (*_AUDIT, "publication_commit")),
    ((*_AUDIT, "checkpoint", "git_anchor_commit"), (*_AUDIT, "publication_commit")),
    (
        (*_ACCEPTANCE, "acceptance_closure", "git_anchor_commit"),
        (*_ACCEPTANCE, "publication_commit"),
    ),
    (
        (*_ACCEPTANCE, "acceptance_manifest", "git_anchor_commit"),
        (*_ACCEPTANCE, "publication_commit"),
    ),
    ((*_ACCEPTANCE, "checkpoint", "git_anchor_commit"), (*_ACCEPTANCE, "publication_commit")),
    ((*_ROLES, "implementation_candidate", "path"), (*_AXES, "path_list_source", "path")),
    ((*_ROLES, "implementation_candidate", "sha256"), (*_AXES, "path_list_source", "sha256")),
    ((*_INPUT, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_CORE, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_STACK, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_RUNNER, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_FRAMEWORK, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    ((*_REGISTRY, "git_anchor_commit"), (*_PROVENANCE, "historical_execution_commit")),
    *(
        pair
        for section in ("methodology_authority", "evidence_authority")
        for record in ("acceptance_closure", "acceptance_manifest")
        for pair in (
            ((section, record, "git_anchor_commit"), (section, "acceptance_commit")),
            ((section, record, "git_anchor_role"), ("__interface__", "ANCHOR_ADDED")),
        )
    ),
    *(
        ((*section, record, "git_anchor_role"), ("__interface__", "ANCHOR_ADDED"))
        for section, record in (
            (_GENERATION, "accepted_lifecycle_record"),
            (("full81_authorizations",), "scope_authorization"),
            (("full81_authorizations",), "no_solve_preflight_evidence"),
            (("full81_authorizations",), "execution_authorization"),
            (_AUDIT, "independent_audit_report"),
            (_AUDIT, "audit_evidence_record"),
            (_AUDIT, "publication_manifest"),
            (_AUDIT, "checkpoint"),
            (_ACCEPTANCE, "acceptance_closure"),
            (_ACCEPTANCE, "acceptance_manifest"),
            (_ACCEPTANCE, "checkpoint"),
        )
    ),
    ((*_AXES, "digest_algorithm"), ("__interface__", "IDENTITY_DIGEST_ALGORITHM")),
    (
        (*_RESULTS, "run_file_aggregate", "algorithm"),
        ("__interface__", "RUN_FILE_AGGREGATE_ALGORITHM"),
    ),
    ((*_UNIVERSE, "case_id_rule"), ("__interface__", "CASE_ID_RULE")),
    (("artifact_type",), ("__interface__", "POINTER_ARTIFACT_TYPE")),
    (("schema_version",), ("__interface__", "POINTER_SCHEMA_VERSION")),
    (
        ("validation_contract", "verifier_interface_version"),
        ("__interface__", "INTERFACE_VERSION"),
    ),
    (
        ("validation_contract", "verifier_module"),
        ("__interface__", "VERIFIER_MODULE_RELATIVE_PATH"),
    ),
    (
        (*_ACCEPTANCE, "acceptance_status"),
        ("__interface__", "ACCEPTANCE_STATUS_CLOSED_ACCEPTED"),
    ),
    ((*_ACCEPTANCE, "governance_status"), ("__interface__", "GOVERNANCE_STATUS_PUBLISHED")),
    (
        (*_LAYERS, "current_governance_status"),
        ("__interface__", "GOVERNANCE_STATUS_PUBLISHED"),
    ),
    (
        (*_RESULTS, "git_durability", "status"),
        ("__interface__", "RESULT_DURABILITY_LOCAL_ONLY"),
    ),
    (
        ("pointer_identity", "proposed_canonical_path"),
        ("__interface__", "CANONICAL_POINTER_RELATIVE_PATH"),
    ),
)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


class _Verification:
    def __init__(
        self, root: Path, mode: str, results_policy: str, pointer_relative_path: str
    ) -> None:
        self.root = Path(root).resolve()
        self.mode = mode
        self.results_policy = results_policy
        self.pointer_relative_path = pointer_relative_path
        self.git = _Git(self.root)
        self.checks: dict[str, str] = {check: STATUS_NOT_RUN for check in CHECK_IDS}
        self.failures: list[dict[str, str]] = []
        self.notes: list[str] = []
        self.info: dict[str, Any] = {}
        self.results_integrity = RESULTS_NOT_CHECKED
        self.pointer: Mapping[str, Any] = {}
        self.records: dict[str, Any] = {}

    def start(self, check: str) -> None:
        if self.checks[check] == STATUS_NOT_RUN:
            self.checks[check] = STATUS_PASS

    def fail(self, check: str, code: str, detail: str) -> None:
        self.checks[check] = STATUS_FAIL
        self.failures.append({"check": check, "code": code, "detail": detail})

    def require(self, check: str, code: str, condition: bool, detail: str) -> bool:
        if not condition:
            self.fail(check, code, detail)
        return bool(condition)

    def equal(self, check: str, code: str, actual: Any, expected: Any, what: str) -> bool:
        same = (
            actual is not _MISSING
            and expected is not _MISSING
            and isinstance(actual, bool) == isinstance(expected, bool)
            and actual == expected
        )
        if not same:
            self.fail(check, code, f"{what}: found {_show(actual)}, expected {_show(expected)}")
        return same

    def value(self, path: Sequence[Any]) -> Any:
        if path and path[0] == "__interface__":
            return globals()[path[1]]
        return _lookup(self.pointer, path)

    def resolve(self, relative: Any) -> Path | None:
        try:
            return resolve_repository_path(self.root, relative)
        except PointerPathError:
            return None

    def result(self) -> dict[str, Any]:
        failed = bool(self.failures)
        if failed:
            verdict = VERDICT_FAIL_CLOSED
        elif self.mode == MODE_CANONICAL:
            verdict = VERDICT_CANONICAL_VERIFIED
        else:
            verdict = VERDICT_CANDIDATE_CONSISTENT
        authority = self.mode == MODE_CANONICAL and not failed
        restrictions = _lookup(self.pointer, ("scientific_exposure_restrictions",))
        exposure = {
            "blocked_purposes": [],
            "permitted_purposes": [],
            "exposure_log_established": None,
        }
        if isinstance(restrictions, Mapping):
            exposure = {
                "governing_finding": restrictions.get("governing_finding"),
                "blocked_purposes": list(restrictions.get("blocked_purposes") or []),
                "permitted_purposes": list(restrictions.get("permitted_purposes") or []),
                "exposure_log_established": _lookup(restrictions, ("exposure_log", "established")),
            }
        return {
            "verifier": {
                "module": VERIFIER_MODULE_RELATIVE_PATH,
                "interface_version": INTERFACE_VERSION,
            },
            "mode": self.mode,
            "pointer_path": self.pointer_relative_path,
            "verdict": verdict,
            "is_current_authority": authority,
            "authority_conferred_by_this_verification": False,
            "candidate_promoted": False,
            "results_policy": self.results_policy,
            "results_integrity": self.results_integrity,
            "results_consumption_permitted": (
                authority and self.results_integrity == RESULTS_STRICT_PASS
            ),
            "checks": dict(self.checks),
            "failure_codes": sorted({failure["code"] for failure in self.failures}),
            "failures": list(self.failures),
            "notes": list(self.notes),
            "scientific_exposure": exposure,
            "grants_execution_authority": False,
            "zero_execution_counters": {
                "solver_library_imports": 0,
                "model_constructions": 0,
                "optimize_calls": 0,
                "files_written": 0,
                "git_write_subcommands": 0,
            },
            **self.info,
        }


def _check_schema(v: _Verification, pointer: Any) -> bool:
    v.start(CHECK_SCHEMA)
    if not isinstance(pointer, Mapping):
        v.fail(CHECK_SCHEMA, "SCHEMA_NOT_AN_OBJECT", "the pointer is not a JSON object")
        return False
    problems: list[str] = []
    _schema_problems(pointer, POINTER_SCHEMA, "pointer", problems)
    for key in pointer:
        if key not in POINTER_SCHEMA:
            problems.append(f"pointer.{key}: unknown top-level key")
    for problem in problems:
        v.fail(CHECK_SCHEMA, "SCHEMA_VIOLATION", problem)
    return not problems


def _check_lifecycle(v: _Verification) -> None:
    v.start(CHECK_LIFECYCLE)
    identity = v.pointer["pointer_identity"]
    activation = v.pointer["activation_basis"]
    state = identity["lifecycle_state"]
    v.equal(
        CHECK_LIFECYCLE,
        "POINTER_PATH_FIELD_MISMATCH",
        identity["this_file_path"],
        v.pointer_relative_path,
        "pointer_identity.this_file_path",
    )
    v.require(
        CHECK_LIFECYCLE,
        "POINTER_SELF_ACCEPTED",
        identity["self_accepted"] is False,
        "a pointer may never declare itself self-accepted",
    )
    if v.mode == MODE_CANDIDATE:
        v.require(
            CHECK_LIFECYCLE,
            "CANDIDATE_NOT_UNDER_CANDIDATE_DIRECTORY",
            v.pointer_relative_path.startswith(CANDIDATE_DIRECTORY_RELATIVE_PATH + "/"),
            f"candidate mode reads only {CANDIDATE_DIRECTORY_RELATIVE_PATH}/",
        )
        v.equal(
            CHECK_LIFECYCLE,
            "CANDIDATE_LIFECYCLE_STATE",
            state,
            LIFECYCLE_CANDIDATE,
            "lifecycle_state",
        )
        v.equal(
            CHECK_LIFECYCLE,
            "CANDIDATE_LIFECYCLE_LABEL",
            identity["lifecycle"],
            CANDIDATE_LIFECYCLE_LABEL,
            "lifecycle",
        )
        flags = (
            identity["is_candidate"] is True
            and identity["is_accepted"] is False
            and identity["is_canonical"] is False
            and identity["is_current_authority"] is False
        )
        v.require(
            CHECK_LIFECYCLE,
            "CANDIDATE_CLAIMS_AUTHORITY",
            flags,
            "a candidate must be is_candidate and none of accepted / canonical / current authority",
        )
        v.equal(
            CHECK_LIFECYCLE,
            "CANDIDATE_CLAIMS_ACTIVATION",
            activation["status"],
            ACTIVATION_NOT_ACTIVATED,
            "activation_basis.status",
        )
        v.require(
            CHECK_LIFECYCLE,
            "CANDIDATE_CLAIMS_ACTIVATION",
            all(activation[role] is None for role in ACTIVATION_ROLES),
            "a candidate carries no activation artifact",
        )
    else:
        v.equal(
            CHECK_LIFECYCLE,
            "CANONICAL_PATH_MISMATCH",
            v.pointer_relative_path,
            CANONICAL_POINTER_RELATIVE_PATH,
            "canonical pointer path",
        )
        if state == LIFECYCLE_CANDIDATE or identity["is_candidate"] is not False:
            v.fail(
                CHECK_LIFECYCLE,
                "CANONICAL_POINTER_IS_CANDIDATE_ONLY",
                "the file at the canonical path still carries a candidate lifecycle",
            )
        v.equal(
            CHECK_LIFECYCLE,
            "CANONICAL_LIFECYCLE_STATE",
            state,
            LIFECYCLE_CANONICAL,
            "lifecycle_state",
        )
        flags = (
            identity["is_accepted"] is True
            and identity["is_canonical"] is True
            and identity["is_current_authority"] is True
        )
        v.require(
            CHECK_LIFECYCLE,
            "CANONICAL_LIFECYCLE_FLAGS",
            flags,
            "a canonical pointer must be accepted, canonical and current authority",
        )


def _check_paths(v: _Verification) -> None:
    v.start(CHECK_PATHS)
    for location, key, value, _parent in _walk(v.pointer):
        if not _is_path_key(key) or value is None:
            continue
        try:
            resolve_repository_path(v.root, value)
        except PointerPathError as error:
            v.fail(CHECK_PATHS, error.code, f"{location}: {error.detail}")


def _recorded_commits(pointer: Mapping[str, Any]) -> dict[str, str]:
    commits: dict[str, str] = {}
    for location, key, value, _parent in _walk(pointer):
        if isinstance(value, str) and (key.endswith("_commit") or key == "git_anchor_commit"):
            commits.setdefault(value, location)
    for index, sha in enumerate(pointer["git_provenance"]["ancestry_chain_oldest_to_newest"]):
        commits.setdefault(sha, f"git_provenance.ancestry_chain_oldest_to_newest[{index}]")
    return commits


def _check_git(v: _Verification) -> bool:
    v.start(CHECK_GIT)
    provenance = v.pointer["git_provenance"]
    try:
        head = v.git.rev("HEAD")
    except OSError as error:
        v.fail(CHECK_GIT, "GIT_UNAVAILABLE", f"git could not be run: {error}")
        return False
    if not v.require(CHECK_GIT, "GIT_HEAD_UNRESOLVED", head is not None, "HEAD does not resolve"):
        return False
    upstream_ref = provenance["upstream_ref"]
    upstream = v.git.rev(upstream_ref) if upstream_ref.startswith("refs/") else None
    v.require(
        CHECK_GIT,
        "UPSTREAM_REF_ABSENT",
        upstream is not None,
        f"{upstream_ref} does not resolve, so publication cannot be proven",
    )
    v.require(
        CHECK_GIT,
        "LIVE_HEAD_EQUALITY_REQUIREMENT_FORBIDDEN",
        provenance["live_head_must_equal_a_recorded_commit"] is False,
        "the pointer must not require the live HEAD to equal a historical commit",
    )
    in_head = v.git.reachable_from(head)
    published = v.git.reachable_from(upstream) if upstream is not None else frozenset()
    for sha, location in _recorded_commits(v.pointer).items():
        if sha not in in_head:
            known = v.git.is_commit(sha)
            v.fail(
                CHECK_GIT,
                "GIT_COMMIT_NOT_IN_HEAD_ANCESTRY" if known else "GIT_COMMIT_ABSENT",
                f"{location}: {sha} is not in the ancestry of the live HEAD {head}",
            )
        elif upstream is not None:
            v.require(
                CHECK_GIT,
                "GIT_COMMIT_NOT_PUBLISHED_UPSTREAM",
                sha in published,
                f"{location}: {sha} is not reachable from {upstream_ref}",
            )
    chain = provenance["ancestry_chain_oldest_to_newest"]
    v.require(CHECK_GIT, "GIT_ANCESTRY_CHAIN_EMPTY", len(chain) >= 2, "ancestry chain too short")
    for older, newer in zip(chain, chain[1:]):
        v.require(
            CHECK_GIT,
            "GIT_ANCESTRY_ORDER_VIOLATED",
            older != newer and v.git.is_ancestor(older, newer),
            f"{older} is not a strict ancestor of {newer}",
        )
    for link in provenance["direct_parent_links"]:
        if not v.require(
            CHECK_GIT, "GIT_PARENT_LINK_MALFORMED", len(link) == 2, f"malformed link {link!r}"
        ):
            continue
        v.equal(
            CHECK_GIT,
            "GIT_PARENT_LINK_VIOLATED",
            v.git.parents(link[1]),
            [link[0]],
            f"parents of {link[1]}",
        )
    for name in (
        "historical_execution_commit",
        "audit_evidence_publication_commit",
        "results_acceptance_publication_commit",
    ):
        v.require(
            CHECK_GIT,
            "GIT_COMMIT_NOT_IN_ANCESTRY_CHAIN",
            provenance[name] in chain,
            f"git_provenance.{name} is absent from the ancestry chain",
        )
    v.info["git"] = {
        "live_head": head,
        "live_branch": v.git.branch(),
        "upstream_ref": upstream_ref,
        "upstream_head": upstream,
        "live_head_equals_upstream": head == upstream,
        "live_head_equals_results_acceptance_publication_commit": (
            head == provenance["results_acceptance_publication_commit"]
        ),
        "live_head_equality_is_not_required": True,
    }
    return True


def _classify_raw_mismatch(
    v: _Verification, path: Path, blob_id: str | None, recorded_sha256: str
) -> str:
    """Why a tracked file's raw bytes differ from the recorded identity.

    An EOL conversion is reported only when the HEAD blob still carries the
    recorded bytes and the working-tree file differs from that blob in line
    endings alone.  Everything else is a content difference.
    """

    blob = v.git.blob_bytes(blob_id) if blob_id else None
    if blob is not None and sha256_bytes(blob) == recorded_sha256:
        live = path.read_bytes()
        if live != blob and live.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"):
            return "RAW_BYTES_DIFFER_BY_EOL_CONVERSION_ONLY"
    return "RAW_BYTES_DIFFER_IN_CONTENT"


def _check_files(v: _Verification, git_ok: bool) -> None:
    v.start(CHECK_FILES)
    identities = [
        (location, value)
        for location, _key, value, _parent in _walk(v.pointer)
        if _is_file_identity(value)
    ]
    by_path: dict[str, Mapping[str, Any]] = {}
    for location, identity in identities:
        first = by_path.setdefault(identity["path"], identity)
        fields = (
            "sha256", "bytes", "git_tracked", "git_blob_id", "git_anchor_commit", "git_anchor_role",
        )
        v.require(
            CHECK_FILES,
            "INCONSISTENT_DUPLICATE_IDENTITY",
            all(first.get(f) == identity.get(f) for f in fields),
            f"{location}: {identity['path']} is bound twice with different identities",
        )
    head_tree = v.git.tree("HEAD") if git_ok else {}
    tracked = [i for i in by_path.values() if i["git_tracked"]]
    blob_digests = v.git.blob_digests([i["git_blob_id"] for i in tracked]) if git_ok else {}
    counts = {"tracked": 0, "local_only_checked": 0, "local_only_deferred": 0}
    for relative, identity in by_path.items():
        path = v.resolve(relative)
        if path is None:
            continue  # reported by the path-containment check
        if not identity["git_tracked"]:
            if v.results_policy == RESULTS_POLICY_NONE:
                counts["local_only_deferred"] += 1
                continue
            counts["local_only_checked"] += 1
        else:
            counts["tracked"] += 1
        if not v.require(
            CHECK_FILES,
            "LOCAL_RESULTS_ABSENT" if not identity["git_tracked"] else "FILE_ABSENT",
            path.is_file(),
            f"{relative} is not present in the working tree",
        ):
            continue
        raw_ok = (
            path.stat().st_size == identity["bytes"] and sha256_file(path) == identity["sha256"]
        )
        if not identity["git_tracked"]:
            v.require(
                CHECK_FILES,
                "RAW_BYTES_DIFFER_IN_CONTENT",
                raw_ok,
                f"{relative}: raw working-tree bytes do not match the recorded identity",
            )
            continue
        if not git_ok:
            continue
        blob_id, anchor = identity["git_blob_id"], identity["git_anchor_commit"]
        v.equal(
            CHECK_FILES,
            "GIT_BLOB_MISMATCH_AT_ANCHOR_COMMIT",
            v.git.tree(anchor).get(relative, _MISSING),
            blob_id,
            f"{relative} blob id in anchor commit {anchor}",
        )
        if identity["git_anchor_role"] == ANCHOR_ADDED:
            v.require(
                CHECK_FILES,
                "GIT_PATH_NOT_ADDED_BY_ANCHOR_COMMIT",
                not any(relative in v.git.tree(parent) for parent in v.git.parents(anchor)),
                f"{relative} already exists in a parent of {anchor}; "
                "that commit did not publish it",
            )
        v.equal(
            CHECK_FILES,
            "GIT_BLOB_CHANGED_IN_LIVE_HEAD",
            head_tree.get(relative, _MISSING),
            blob_id,
            f"{relative} blob id in the live HEAD",
        )
        digest = blob_digests.get(blob_id)
        v.require(
            CHECK_FILES,
            "GIT_BLOB_BYTES_MISMATCH",
            digest is not None and digest == (identity["sha256"], identity["bytes"]),
            f"{relative}: the bytes of blob {blob_id} do not hash to the recorded SHA-256",
        )
        if not raw_ok:
            v.fail(
                CHECK_FILES,
                _classify_raw_mismatch(v, path, head_tree.get(relative), identity["sha256"]),
                f"{relative}: raw working-tree bytes do not match the recorded identity",
            )
    v.info["file_identities"] = counts


def _load_json(v: _Verification, check: str, relative: Any, label: str) -> Any:
    path = v.resolve(relative)
    if path is None or not path.is_file():
        v.fail(check, "RECORD_UNREADABLE", f"{label}: {relative!r} is not a readable file")
        return None
    try:
        return json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        v.fail(check, "RECORD_UNREADABLE", f"{label}: {relative} is not valid JSON ({error})")
        return None


def _check_axes(v: _Verification, git_ok: bool) -> None:
    v.start(CHECK_AXES)
    axes = v.pointer["production_generation"]["identity_axes"]
    manifest = v.records.get("g1_candidate_manifest")
    if manifest is None:
        v.fail(CHECK_AXES, "IDENTITY_AXES_SOURCE_UNREADABLE", "the path-list source is unreadable")
        return
    execution_tree = (
        v.git.tree(v.pointer["git_provenance"]["historical_execution_commit"]) if git_ok else {}
    )
    for axis in ("runtime", "validation", "governance_authority"):
        declared = axes[axis]
        recorded = _lookup(manifest, (declared["manifest_key"], "paths"))
        if not isinstance(recorded, Mapping) or not recorded:
            v.fail(CHECK_AXES, "IDENTITY_AXIS_PATHS_ABSENT", f"{axis}: no path map in the source")
            continue
        v.equal(
            CHECK_AXES,
            "IDENTITY_AXIS_PATH_COUNT",
            len(recorded),
            declared["path_count"],
            f"{axis} path count",
        )
        v.equal(
            CHECK_AXES,
            "IDENTITY_AXIS_RECORDED_DIGEST",
            canonical_identity_digest(recorded),
            declared["digest"],
            f"{axis} digest over the recorded path map",
        )
        live: dict[str, str] = {}
        for relative in recorded:
            path = v.resolve(relative)
            if path is None or not path.is_file():
                v.fail(CHECK_AXES, "IDENTITY_AXIS_MEMBER_ABSENT", f"{axis}: {relative} is absent")
                continue
            live[relative] = sha256_file(path)
        drifted = sorted(p for p, h in live.items() if h != recorded[p])
        v.require(
            CHECK_AXES,
            "IDENTITY_AXIS_LIVE_DRIFT",
            not drifted and canonical_identity_digest(live) == declared["digest"],
            f"{axis}: live raw bytes do not reproduce the digest; drifted paths: {drifted}",
        )
        if not git_ok:
            continue
        blob_ids = {p: execution_tree.get(p) for p in recorded}
        missing = sorted(p for p, b in blob_ids.items() if b is None)
        if not v.require(
            CHECK_AXES,
            "IDENTITY_AXIS_NOT_IN_EXECUTION_TREE",
            not missing,
            f"{axis}: absent from the execution commit tree: {missing}",
        ):
            continue
        digests = v.git.blob_digests(list(blob_ids.values()))
        durable = {p: (digests[b] or ("", 0))[0] for p, b in blob_ids.items()}
        v.equal(
            CHECK_AXES,
            "IDENTITY_AXIS_GIT_BLOB_DIGEST",
            canonical_identity_digest(durable),
            declared["digest"],
            f"{axis} digest over the execution-commit blobs",
        )


def _check_bindings(v: _Verification) -> None:
    v.start(CHECK_BINDINGS)
    for left, right in INTERNAL_EQUALITIES:
        v.equal(
            CHECK_BINDINGS,
            "POINTER_INTERNAL_INCONSISTENCY",
            v.value(left),
            v.value(right),
            ".".join(map(str, left)),
        )
    for record, keys, expected in CROSS_BINDINGS:
        if record in LOCAL_RECORDS:
            continue
        payload = v.records.get(record)
        if payload is None:
            continue  # the unreadable record is already a failure
        wanted = expected.value if isinstance(expected, _Literal) else v.value(expected)
        v.equal(
            CHECK_BINDINGS,
            "CROSS_BINDING_MISMATCH",
            _lookup(payload, keys),
            wanted,
            f"{record}:{'.'.join(map(str, keys))}",
        )
    execution = v.records.get("execution_authorization")
    if execution is not None:
        declared = {
            entry["path"]: entry["sha256"]
            for entry in v.pointer["economic_parameter_interfaces"]["execution_input_authority"]
        }
        v.equal(
            CHECK_BINDINGS,
            "CROSS_BINDING_MISMATCH",
            _lookup(execution, ("execution_input_authority",)),
            declared,
            "execution_authorization:execution_input_authority",
        )
    manifest = v.records.get("results_acceptance_manifest")
    if manifest is not None:
        audit = v.pointer["independent_audit_evidence_publication"]
        fields = ("path", "sha256", "bytes", "git_blob_id")
        declared_files = sorted(
            tuple(audit[name][f] for f in fields)
            for name in (
                "independent_audit_report",
                "audit_evidence_record",
                "publication_manifest",
                "checkpoint",
            )
        )
        recorded = _lookup(manifest, ("accepted_evidence_references", "phase_a_files"))
        recorded_files = (
            sorted(tuple(item.get(f) for f in fields) for item in recorded)
            if isinstance(recorded, list) and all(isinstance(i, Mapping) for i in recorded)
            else _MISSING
        )
        v.equal(
            CHECK_BINDINGS,
            "CROSS_BINDING_MISMATCH",
            recorded_files,
            declared_files,
            "results_acceptance_manifest:accepted_evidence_references.phase_a_files",
        )


def _check_universe(v: _Verification) -> None:
    v.start(CHECK_UNIVERSE)
    results = v.pointer["accepted_result_set"]
    universe = results["case_universe"]
    try:
        case_ids = expected_case_ids(universe["alpha_universe"], universe["beta_universe_h"])
    except ValueError as error:
        v.fail(CHECK_UNIVERSE, "CASE_UNIVERSE_INVALID", str(error))
        return
    v.require(
        CHECK_UNIVERSE,
        "CASE_UNIVERSE_INVALID",
        len(set(case_ids)) == len(case_ids) == results["case_count"],
        "the declared grid does not yield case_count distinct case ids",
    )
    run_id, run_path = results["run_id"], results["run_path"]
    v.require(
        CHECK_UNIVERSE,
        "RUN_ID_MALFORMED",
        bool(_RUN_ID_RE.match(run_id)),
        f"run id {run_id!r} is not a published production run id",
    )
    v.equal(
        CHECK_UNIVERSE,
        "RUN_PATH_NOT_BOUND_TO_RUN_ID",
        run_path,
        f"{results['result_namespace']}/runs/{run_id}",
        "accepted_result_set.run_path",
    )
    for name, filename in (
        ("completion_manifest", "completion_manifest.json"),
        ("authority", "authority.json"),
        ("case_schedule", "case_schedule.json"),
    ):
        artifact = results["root_artifacts"][name]
        v.equal(
            CHECK_UNIVERSE,
            "ROOT_ARTIFACT_NOT_UNDER_RUN",
            artifact["path"],
            f"{run_path}/{filename}",
            f"root_artifacts.{name}.path",
        )
        v.require(
            CHECK_UNIVERSE,
            "ROOT_ARTIFACT_NOT_UNDER_RUN",
            artifact["git_tracked"] is False,
            f"root_artifacts.{name} must be a local, untracked identity",
        )


def _overlaps(first: str, second: str) -> bool:
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def _check_roles(v: _Verification, git_ok: bool) -> None:
    v.start(CHECK_ROLES)
    roles = v.pointer["roles"]
    results = v.pointer["accepted_result_set"]
    bound = {value["path"] for _l, _k, value, _p in _walk(v.pointer) if _is_file_identity(value)}
    bound.add(results["run_path"])
    v.equal(
        CHECK_ROLES,
        "ACCEPTED_CURRENT_ROLES_MISMATCH",
        roles["accepted_current"],
        [{"role": role, "path": v.value(location)} for role, location in ACCEPTED_CURRENT_ROLES],
        "roles.accepted_current",
    )
    not_current = [
        entry["path"]
        for group in ("historical_only", "accepted_other_scope_not_bound_by_this_pointer")
        for entry in roles[group]
    ]
    for path in not_current:
        for bound_path in sorted(bound):
            v.require(
                CHECK_ROLES,
                "NON_CURRENT_PATH_CLAIMED_CURRENT",
                not _overlaps(path, bound_path),
                f"{path} is declared not current but overlaps the bound path {bound_path}",
            )
    if git_ok:
        v.equal(
            CHECK_ROLES,
            "RESULT_DURABILITY_STATEMENT_STALE",
            len(v.git.tracked_under(results["run_path"])),
            results["git_durability"]["result_files_git_tracked"],
            "count of Git-tracked files under the accepted run path",
        )
    search_root = v.resolve(POINTER_SEARCH_ROOT_RELATIVE_PATH)
    canonical_present = False
    for path in sorted(search_root.rglob("*.json")) if search_root and search_root.is_dir() else []:
        relative = path.relative_to(v.root).as_posix()
        try:
            other = json.loads(path.read_bytes().decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            if relative == CANONICAL_POINTER_RELATIVE_PATH:
                canonical_present = True
            continue
        if not isinstance(other, Mapping) or other.get("artifact_type") != POINTER_ARTIFACT_TYPE:
            continue
        identity = other.get("pointer_identity")
        claims = not isinstance(identity, Mapping) or (
            identity.get("is_current_authority") is not False
            or identity.get("is_canonical") is not False
            or identity.get("lifecycle_state") != LIFECYCLE_CANDIDATE
        )
        if relative == CANONICAL_POINTER_RELATIVE_PATH:
            canonical_present = True
        elif relative.startswith(CANDIDATE_DIRECTORY_RELATIVE_PATH + "/"):
            v.require(
                CHECK_ROLES,
                "CONFLICTING_CURRENT_MAINLINE_CLAIM",
                not claims,
                f"{relative} is a candidate but claims authority",
            )
        else:
            v.fail(
                CHECK_ROLES,
                "CONFLICTING_CURRENT_MAINLINE_CLAIM",
                f"{relative} is a pointer outside the canonical path and the candidate directory",
            )
    v.info["canonical_pointer_present"] = canonical_present


def _check_findings(v: _Verification) -> None:
    v.start(CHECK_FINDINGS)
    section = v.pointer["open_findings_and_limitations"]
    restrictions = v.pointer["scientific_exposure_restrictions"]
    blocked = set(restrictions["blocked_purposes"])
    permitted = set(restrictions["permitted_purposes"])
    findings = {finding["id"]: finding for finding in section["findings"]}
    v.require(
        CHECK_FINDINGS,
        "DUPLICATE_FINDING_ID",
        len(findings) == len(section["findings"]),
        "a finding id is listed twice",
    )
    v.require(
        CHECK_FINDINGS,
        "FINDING_CLOSED_BY_POINTER",
        section["closed_or_remediated_by_this_pointer"] == [],
        "a pointer closes and remediates no finding",
    )
    for finding in findings.values():
        if finding["closed"]:
            v.require(
                CHECK_FINDINGS,
                "FINDING_CLOSED_WITHOUT_EVIDENCE",
                finding["resolution_evidence"] is not None,
                f"{finding['id']} is marked closed without accepted resolution evidence",
            )
        else:
            v.require(
                CHECK_FINDINGS,
                "OPEN_FINDING_RESTRICTION_NOT_ENFORCED",
                set(finding["blocks_purposes"]) <= blocked,
                f"{finding['id']} blocks purposes that are not in blocked_purposes",
            )
    manifest = v.records.get("results_acceptance_manifest")
    open_after = _lookup(manifest, ("findings_open_after_acceptance",)) if manifest else _MISSING
    if v.require(
        CHECK_FINDINGS,
        "OPEN_FINDING_SOURCE_UNREADABLE",
        isinstance(open_after, list) and bool(open_after),
        "the accepted open-finding set could not be read",
    ):
        for finding_id in open_after:
            carried = findings.get(finding_id)
            if not v.require(
                CHECK_FINDINGS,
                "OPEN_FINDING_DROPPED",
                carried is not None,
                f"{finding_id} is open in the accepted record but absent from the pointer",
            ):
                continue
            v.require(
                CHECK_FINDINGS,
                "FINDING_CLOSED_WITHOUT_EVIDENCE",
                carried["closed"] is False or carried["resolution_evidence"] is not None,
                f"{finding_id} is open in the accepted record but closed in the pointer",
            )
    closure = v.records.get("results_acceptance_closure")
    accepted_findings: dict[Any, tuple[str, Any, Any, Mapping[str, Any]]] = {}
    for listed, severity_key, disposition_key in ACCEPTED_FINDING_LISTS:
        entries = _lookup(closure, (listed,)) if closure else _MISSING
        for accepted in entries if isinstance(entries, list) else []:
            if isinstance(accepted, Mapping) and accepted.get("closed") is False:
                accepted_findings[accepted.get("id")] = (
                    listed,
                    accepted.get(severity_key),
                    accepted.get(disposition_key),
                    accepted,
                )
    v.require(
        CHECK_FINDINGS,
        "OPEN_FINDING_SOURCE_UNREADABLE",
        bool(accepted_findings),
        "the findings of the accepted results acceptance could not be read",
    )
    for finding_id in sorted(set(findings) - set(accepted_findings), key=str):
        v.fail(
            CHECK_FINDINGS,
            "FINDING_WITHOUT_ACCEPTED_SOURCE",
            f"{finding_id} is not a finding of the accepted results acceptance",
        )
    for finding_id, (listed, severity, disposition, accepted) in accepted_findings.items():
        carried = findings.get(finding_id)
        if not v.require(
            CHECK_FINDINGS,
            "OPEN_FINDING_DROPPED",
            carried is not None,
            f"{finding_id} is open in the accepted record but absent from the pointer",
        ):
            continue
        v.equal(
            CHECK_FINDINGS,
            "FINDING_SEVERITY_OR_DISPOSITION_ALTERED",
            (carried["accepted_list"], carried["severity"], carried["disposition"]),
            (listed, severity, disposition),
            f"{finding_id} (list, severity, disposition)",
        )
        if carried["closed"]:
            continue  # an unevidenced closure is reported above
        for flag, purposes in CLOSURE_BLOCKING_FLAG_PURPOSES.items():
            if accepted.get(flag) is True:
                v.require(
                    CHECK_FINDINGS,
                    "SCIENTIFIC_EXPOSURE_RESTRICTION_WEAKENED",
                    set(purposes) <= blocked and set(purposes) <= set(carried["blocks_purposes"]),
                    f"{finding_id}: {flag} is true but {purposes} is not blocked",
                )
    limitations = _lookup(closure, ("disclosed_limitations_carried",)) if closure else _MISSING
    v.equal(
        CHECK_FINDINGS,
        "DISCLOSED_LIMITATION_DROPPED_OR_ALTERED",
        [
            {"id": entry["id"], "statement": entry["statement"]}
            for entry in section["limitations_carried_from_results_acceptance"]
        ],
        [
            {"id": entry.get("id"), "statement": entry.get("statement")}
            for entry in (limitations if isinstance(limitations, list) else [])
            if isinstance(entry, Mapping)
        ]
        or _MISSING,
        "limitations_carried_from_results_acceptance",
    )
    purposes_named = blocked | permitted
    for finding in findings.values():
        purposes_named |= set(finding["blocks_purposes"])
    v.require(
        CHECK_FINDINGS,
        "UNKNOWN_PURPOSE",
        purposes_named <= set(KNOWN_PURPOSES),
        f"purposes unknown to this interface: {sorted(purposes_named - set(KNOWN_PURPOSES))}",
    )
    governing = findings.get(restrictions["governing_finding"])
    v.require(
        CHECK_FINDINGS,
        "GOVERNING_FINDING_ABSENT",
        governing is not None,
        "the governing finding of the exposure restrictions is not listed",
    )
    v.require(
        CHECK_FINDINGS,
        "PURPOSE_BOTH_BLOCKED_AND_PERMITTED",
        not blocked & permitted,
        f"purposes are both blocked and permitted: {sorted(blocked & permitted)}",
    )
    log = restrictions["exposure_log"]
    v.require(
        CHECK_FINDINGS,
        "POINTER_ACTS_AS_EXPOSURE_LOG",
        log["this_pointer_is_an_exposure_log"] is False
        and log["entries_created_by_this_pointer"] == 0,
        "a pointer is not an exposure log and creates no exposure entry",
    )
    if governing is not None and not governing["closed"]:
        v.require(
            CHECK_FINDINGS,
            "EXPOSURE_LOG_CLAIMED_WHILE_FINDING_OPEN",
            log["established"] is False and log["path"] is None,
            "the governing finding is open, so no exposure log may be claimed",
        )


def _check_non_authorization(v: _Verification) -> None:
    v.start(CHECK_NON_AUTHORIZATION)
    boundaries = v.pointer["non_authorization_boundaries"]
    granted = (
        boundaries["pointer_grants_execution_authority"] is not False
        or boundaries["authorizes"] != []
        or v.pointer["full81_authorizations"]["pointer_grants_execution_authority"] is not False
    )
    v.require(
        CHECK_NON_AUTHORIZATION,
        "POINTER_CLAIMS_EXECUTION_AUTHORITY",
        not granted,
        "a pointer authorizes nothing and grants no execution authority",
    )
    declared = set(boundaries["not_authorized_by_this_pointer"])
    closure = v.records.get("results_acceptance_closure")
    carried = _lookup(closure, ("not_authorized_by_this_record",)) if closure else _MISSING
    if v.require(
        CHECK_NON_AUTHORIZATION,
        "NON_AUTHORIZATION_SOURCE_UNREADABLE",
        isinstance(carried, list) and bool(carried),
        "the accepted non-authorization list could not be read",
    ):
        required = (set(carried) - NON_AUTHORIZATION_ITEMS_NOT_CARRIED) | set(
            POINTER_OWN_NON_AUTHORIZATIONS
        )
        v.require(
            CHECK_NON_AUTHORIZATION,
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
            required <= declared,
            f"required boundaries are not declared: {sorted(required - declared)}",
        )
        v.require(
            CHECK_NON_AUTHORIZATION,
            "NON_AUTHORIZATION_BOUNDARY_UNKNOWN",
            declared <= required,
            f"declared boundaries have no source: {sorted(declared - required)}",
        )
    contract = v.pointer["validation_contract"]
    v.equal(
        CHECK_NON_AUTHORIZATION,
        "VALIDATION_CONTRACT_MISMATCH",
        sorted(contract["required_checks"]),
        sorted(CHECK_IDS),
        "validation_contract.required_checks",
    )


def _run_inventory(run_root: Path) -> tuple[dict[str, int], list[str]]:
    """``{relative posix path: size}`` of every file under the run, and links."""

    sizes: dict[str, int] = {}
    links: list[str] = []
    stack = [run_root]
    while stack:
        directory = stack.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                relative = Path(entry.path).relative_to(run_root).as_posix()
                redirected = entry.is_symlink() or entry.is_junction()
                if not redirected and entry.is_dir(follow_symlinks=False):
                    redirected = str(Path(entry.path).resolve()) != str(Path(entry.path))
                if redirected:
                    links.append(relative)
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
                else:
                    sizes[relative] = entry.stat(follow_symlinks=False).st_size
    return sizes, links


def _registry_entries(registry: Any) -> dict[str, tuple[Any, Any]] | None:
    if not isinstance(registry, Mapping):
        return None
    entries: dict[str, tuple[Any, Any]] = {}
    for relative, entry in registry.items():
        if not isinstance(entry, Mapping):
            return None
        entries[str(relative)] = (entry.get("sha256"), entry.get("bytes"))
    return entries


def _check_results(v: _Verification) -> None:
    """Local result registrations.  Result files are hashed as opaque bytes."""

    if v.results_policy == RESULTS_POLICY_NONE:
        v.notes.append(
            "Local result registrations were NOT checked (results policy NOT_CHECKED); "
            "this verification says nothing about the integrity of the result files."
        )
        return
    v.start(CHECK_RESULTS)
    results = v.pointer["accepted_result_set"]
    registrations = results["registrations"]

    def conclude() -> None:
        if v.checks[CHECK_RESULTS] == STATUS_FAIL:
            v.results_integrity = RESULTS_FAIL
        elif v.results_policy == RESULTS_POLICY_STRICT:
            v.results_integrity = RESULTS_STRICT_PASS
        else:
            v.results_integrity = RESULTS_METADATA_ONLY
            v.notes.append(
                "Results policy METADATA_ONLY: names, sizes and the three root artifacts were "
                "checked; result files were NOT re-hashed. This is not full integrity "
                "verification and never permits results consumption."
            )

    run_root = v.resolve(results["run_path"])
    if run_root is None or not run_root.is_dir():
        v.fail(
            CHECK_RESULTS,
            "LOCAL_RESULTS_ABSENT",
            f"{results['run_path']} is not present; the result files are local-only, "
            "not Git-durable, and cannot be restored from Git",
        )
        conclude()
        return
    for name, artifact in results["root_artifacts"].items():
        path = v.resolve(artifact["path"])
        v.require(
            CHECK_RESULTS,
            "ROOT_ARTIFACT_IDENTITY_MISMATCH",
            path is not None
            and path.is_file()
            and path.stat().st_size == artifact["bytes"]
            and sha256_file(path) == artifact["sha256"],
            f"root_artifacts.{name}: raw bytes do not match the recorded identity",
        )
    for record, location in LOCAL_RECORDS.items():
        v.records[record] = _load_json(v, CHECK_RESULTS, v.value((*location, "path")), record)
    for record, keys, expected in CROSS_BINDINGS:
        payload = v.records.get(record) if record in LOCAL_RECORDS else None
        if payload is None:
            continue
        wanted = expected.value if isinstance(expected, _Literal) else v.value(expected)
        v.equal(
            CHECK_RESULTS,
            "CROSS_BINDING_MISMATCH",
            _lookup(payload, keys),
            wanted,
            f"{record}:{'.'.join(map(str, keys))}",
        )
    manifest = v.records.get("run_completion_manifest")
    universe = results["case_universe"]
    case_ids = expected_case_ids(universe["alpha_universe"], universe["beta_universe_h"])
    registry = _registry_entries(_lookup(manifest, ("artifact_registry",)) if manifest else None)
    if registry is None:
        v.fail(
            CHECK_RESULTS, "RESULT_REGISTRY_UNREADABLE", "the root artifact registry is unreadable"
        )
        conclude()
        return
    v.equal(
        CHECK_RESULTS,
        "CASE_UNIVERSE_MISMATCH",
        _lookup(manifest, ("case_ids",)),
        case_ids,
        "run_completion_manifest:case_ids",
    )
    v.equal(
        CHECK_RESULTS,
        "RESULT_REGISTRATION_COUNT_MISMATCH",
        len(registry),
        registrations["root_registered_artifacts"],
        "root registered artifact count",
    )
    sizes, links = _run_inventory(run_root)
    v.require(
        CHECK_RESULTS,
        "RESULT_PATH_IS_A_LINK",
        not links,
        f"links under the run root: {links[:5]}",
    )
    cases_directory = run_root / "cases"
    present_cases = (
        sorted(entry.name for entry in cases_directory.iterdir() if entry.is_dir())
        if cases_directory.is_dir()
        else []
    )
    v.equal(
        CHECK_RESULTS,
        "CASE_UNIVERSE_MISMATCH",
        present_cases,
        sorted(case_ids),
        "case directories under the run",
    )
    v.equal(
        CHECK_RESULTS,
        "RESULT_FILE_COUNT_MISMATCH",
        len(sizes),
        registrations["files_under_run_root"],
        "files under the run root",
    )
    v.equal(
        CHECK_RESULTS,
        "RESULT_TOTAL_BYTES_MISMATCH",
        sum(sizes.values()),
        registrations["total_bytes"],
        "total bytes under the run root",
    )
    missing = sorted(set(registry) - set(sizes))
    unregistered = sorted(set(sizes) - set(registry))
    v.require(
        CHECK_RESULTS,
        "REGISTERED_RESULT_FILE_ABSENT",
        not missing,
        f"{len(missing)} registered result file(s) are absent, first: {missing[:5]}",
    )
    v.equal(
        CHECK_RESULTS,
        "UNREGISTERED_RESULT_FILE_PRESENT",
        unregistered,
        sorted(registrations["unregistered_by_design"]),
        "files under the run root that the root manifest does not register",
    )
    wrong_size = sorted(
        p for p, (_sha, size) in registry.items() if p in sizes and sizes[p] != size
    )
    v.require(
        CHECK_RESULTS,
        "REGISTERED_RESULT_SIZE_MISMATCH",
        not wrong_size,
        f"{len(wrong_size)} registered result file(s) have the wrong size, first: {wrong_size[:5]}",
    )
    if v.results_policy != RESULTS_POLICY_STRICT:
        conclude()
        return

    hashes = {relative: sha256_file(run_root.joinpath(*relative.split("/"))) for relative in sizes}
    wrong_hash = sorted(
        p for p, (sha, _size) in registry.items() if p in hashes and hashes[p] != sha
    )
    v.require(
        CHECK_RESULTS,
        "REGISTERED_RESULT_HASH_MISMATCH",
        not wrong_hash,
        f"{len(wrong_hash)} registered result file(s) fail their SHA-256, first: {wrong_hash[:5]}",
    )
    case_entries = 0
    for case_id in case_ids:
        prefix = f"cases/{case_id}"
        relative = f"{prefix}/completion_manifest.json"
        if relative not in sizes:
            continue  # already reported as absent
        try:
            case = json.loads(run_root.joinpath(*relative.split("/")).read_bytes().decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            case = None
        case_registry = _registry_entries(_lookup(case, ("artifact_registry",)) if case else None)
        if case_registry is None:
            v.fail(CHECK_RESULTS, "RESULT_REGISTRY_UNREADABLE", f"{relative} is unreadable")
            continue
        case_entries += len(case_registry)
        consistent = (
            _lookup(case, ("case_id",)) == case_id
            and _lookup(case, ("status",)) == results["status_layers"]["execution_time_case_status"]
            and all(
                hashes.get(f"{prefix}/{name}") == sha and sizes.get(f"{prefix}/{name}") == size
                for name, (sha, size) in case_registry.items()
            )
        )
        v.require(
            CHECK_RESULTS,
            "CASE_REGISTRATION_MISMATCH",
            consistent,
            f"{relative}: case id, execution-time status or a registered artifact does not verify",
        )
    v.equal(
        CHECK_RESULTS,
        "RESULT_REGISTRATION_COUNT_MISMATCH",
        case_entries,
        registrations["case_registered_artifacts"],
        "case registered artifact count",
    )
    aggregate = sha256_bytes(
        "".join(f"{p}\t{hashes[p]}\t{sizes[p]}\n" for p in sorted(sizes)).encode("utf-8")
    )
    v.equal(
        CHECK_RESULTS,
        "RUN_FILE_AGGREGATE_MISMATCH",
        aggregate,
        results["run_file_aggregate"]["sha256"],
        "run-file aggregate over every file under the run root",
    )
    conclude()


def _check_activation(v: _Verification, git_ok: bool) -> None:
    """Canonical mode only: the accepted, published basis of the pointer."""

    v.start(CHECK_ACTIVATION)
    activation = v.pointer["activation_basis"]
    if not v.equal(
        CHECK_ACTIVATION,
        "ACTIVATION_BASIS_ABSENT",
        activation["status"],
        ACTIVATION_ACCEPTED_PUBLISHED,
        "activation_basis.status",
    ):
        return
    artifacts = {role: activation[role] for role in ACTIVATION_ROLES}
    if not v.require(
        CHECK_ACTIVATION,
        "ACTIVATION_BASIS_ABSENT",
        all(
            isinstance(a, Mapping)
            and a.get("git_tracked") is True
            and a.get("git_anchor_role") == ANCHOR_ADDED
            for a in artifacts.values()
        ),
        "every activation role must be a Git-tracked artifact bound to its publication commit",
    ):
        return
    paths = [artifact["path"] for artifact in artifacts.values()]
    v.require(
        CHECK_ACTIVATION,
        "ACTIVATION_ROLE_ALIASED",
        len(set(paths)) == len(paths) and CANONICAL_POINTER_RELATIVE_PATH not in paths,
        "activation roles must be four distinct artifacts, none of them the pointer itself",
    )
    v.require(
        CHECK_ACTIVATION,
        "ACTIVATION_ROLE_ALIASED",
        artifacts["audited_candidate"]["path"].startswith(CANDIDATE_DIRECTORY_RELATIVE_PATH + "/"),
        "the audited candidate must be a file under the candidate directory",
    )
    payload = pointer_payload_digest(v.pointer)
    loaded = {
        role: _load_json(v, CHECK_ACTIVATION, artifacts[role]["path"], role)
        for role in ACTIVATION_ROLES
    }
    if any(value is None for value in loaded.values()):
        return
    candidate, audit = loaded["audited_candidate"], loaded["independent_audit_record"]
    closure, manifest = loaded["acceptance_closure"], loaded["acceptance_manifest"]
    candidate_sha = artifacts["audited_candidate"]["sha256"]

    def bind(code: str, actual: Any, expected: Any, what: str) -> None:
        v.equal(CHECK_ACTIVATION, code, actual, expected, what)

    bind(
        "ACTIVATION_PAYLOAD_NOT_THE_AUDITED_CANDIDATE",
        pointer_payload_digest(candidate) if isinstance(candidate, Mapping) else _MISSING,
        payload,
        "payload digest of the audited candidate",
    )
    bind(
        "ACTIVATION_PAYLOAD_NOT_THE_AUDITED_CANDIDATE",
        _lookup(candidate, ("pointer_identity", "lifecycle_state")),
        LIFECYCLE_CANDIDATE,
        "lifecycle state of the audited candidate",
    )
    audit_sha = artifacts["independent_audit_record"]["sha256"]
    closure_sha = artifacts["acceptance_closure"]["sha256"]
    invalid_audit, invalid_acceptance = "ACTIVATION_AUDIT_INVALID", "ACTIVATION_ACCEPTANCE_INVALID"
    for code, record, keys, expected in (
        (invalid_audit, audit, ("artifact_type",), ACTIVATION_AUDIT_ARTIFACT_TYPE),
        (invalid_audit, audit, ("verdict",), "PASS"),
        (invalid_audit, audit, ("self_audit",), False),
        (invalid_audit, audit, ("audited_candidate", "sha256"), candidate_sha),
        (invalid_audit, audit, ("audited_payload_digest",), payload),
        (invalid_acceptance, closure, ("artifact_type",), ACTIVATION_CLOSURE_ARTIFACT_TYPE),
        (invalid_acceptance, closure, ("acceptance_status",), "CLOSED_ACCEPTED"),
        (
            invalid_acceptance,
            closure,
            ("canonical_pointer_path",),
            CANONICAL_POINTER_RELATIVE_PATH,
        ),
        (invalid_acceptance, closure, ("accepted_candidate", "sha256"), candidate_sha),
        (invalid_acceptance, closure, ("accepted_payload_digest",), payload),
        (invalid_acceptance, closure, ("independent_audit_record", "sha256"), audit_sha),
        (invalid_acceptance, manifest, ("artifact_type",), ACTIVATION_MANIFEST_ARTIFACT_TYPE),
        (invalid_acceptance, manifest, ("acceptance_closure", "sha256"), closure_sha),
    ):
        bind(code, _lookup(record, keys), expected, ".".join(keys))
    # The object under verification must be the published file, not a variant.
    on_disk, _digest, unreadable = _read_pointer(v.root, CANONICAL_POINTER_RELATIVE_PATH)
    v.require(
        CHECK_ACTIVATION,
        "CANONICAL_OBJECT_NOT_THE_PUBLISHED_FILE",
        unreadable is None and on_disk == v.pointer,
        "the pointer under verification is not the content of the canonical file",
    )
    if not git_ok:
        return
    pointer_path = v.resolve(CANONICAL_POINTER_RELATIVE_PATH)
    head_blob = v.git.tree("HEAD").get(CANONICAL_POINTER_RELATIVE_PATH)
    if not v.require(
        CHECK_ACTIVATION,
        "CANONICAL_POINTER_NOT_PUBLISHED",
        head_blob is not None and pointer_path is not None and pointer_path.is_file(),
        "the canonical pointer is not tracked in the live HEAD",
    ):
        return
    digest = v.git.blob_digests([head_blob])[head_blob]
    v.require(
        CHECK_ACTIVATION,
        "CANONICAL_POINTER_NOT_PUBLISHED",
        digest is not None and digest[0] == sha256_file(pointer_path),
        "the working-tree canonical pointer differs from its blob in the live HEAD",
    )
    introduced = v.git.last_commit_touching(CANONICAL_POINTER_RELATIVE_PATH)
    upstream = v.git.rev(v.pointer["git_provenance"]["upstream_ref"])
    v.require(
        CHECK_ACTIVATION,
        "CANONICAL_POINTER_NOT_PUBLISHED",
        bool(introduced and upstream and v.git.is_ancestor(introduced, upstream)),
        "the commit that last wrote the canonical pointer is not reachable from the upstream ref",
    )


def _verify(
    root: Path,
    pointer: Any,
    *,
    mode: str,
    pointer_relative_path: str,
    results_policy: str,
) -> dict[str, Any]:
    """Verify an already-parsed pointer object.  Read-only; never raises."""

    if results_policy not in RESULTS_POLICIES:
        raise ValueError(f"unknown results policy: {results_policy!r}")
    v = _Verification(root, mode, results_policy, pointer_relative_path)
    if mode == MODE_CANDIDATE:
        v.checks[CHECK_ACTIVATION] = STATUS_NOT_APPLICABLE
    if not _check_schema(v, pointer):
        return v.result()
    v.pointer = pointer
    v.info["pointer_payload_digest"] = pointer_payload_digest(pointer)
    git_ok = False
    steps = (
        (CHECK_LIFECYCLE, lambda: _check_lifecycle(v)),
        (CHECK_PATHS, lambda: _check_paths(v)),
    )
    for check, step in steps:
        _guarded(v, check, step)
    try:
        git_ok = _check_git(v)
    except Exception as error:  # fail closed, never crash open
        v.fail(CHECK_GIT, "VERIFIER_INTERNAL_ERROR", f"{type(error).__name__}: {error}")
    for record, location in TRACKED_RECORDS.items():
        v.records[record] = _load_json(v, CHECK_BINDINGS, v.value((*location, "path")), record)
    later = [
        (CHECK_FILES, lambda: _check_files(v, git_ok)),
        (CHECK_AXES, lambda: _check_axes(v, git_ok)),
        (CHECK_BINDINGS, lambda: _check_bindings(v)),
        (CHECK_UNIVERSE, lambda: _check_universe(v)),
        (CHECK_ROLES, lambda: _check_roles(v, git_ok)),
        (CHECK_FINDINGS, lambda: _check_findings(v)),
        (CHECK_NON_AUTHORIZATION, lambda: _check_non_authorization(v)),
        (CHECK_RESULTS, lambda: _check_results(v)),
    ]
    if mode == MODE_CANONICAL:
        later.append((CHECK_ACTIVATION, lambda: _check_activation(v, git_ok)))
    for check, step in later:
        _guarded(v, check, step)
    if v.checks[CHECK_RESULTS] == STATUS_FAIL:
        v.results_integrity = RESULTS_FAIL
    return v.result()


def _guarded(v: _Verification, check: str, step: Any) -> None:
    try:
        step()
    except Exception as error:  # fail closed, never crash open
        v.fail(check, "VERIFIER_INTERNAL_ERROR", f"{type(error).__name__}: {error}")


def _read_pointer(root: Path, relative: str) -> tuple[Any, str | None, str | None]:
    """``(pointer, sha256, failure code)`` of a pointer file read from disk."""

    try:
        path = resolve_repository_path(root, relative)
    except PointerPathError as error:
        return None, None, error.code
    if not path.is_file():
        return None, None, "POINTER_ABSENT"
    data = path.read_bytes()
    try:
        return json.loads(data.decode("utf-8")), sha256_bytes(data), None
    except (UnicodeDecodeError, ValueError):
        return None, sha256_bytes(data), "POINTER_NOT_VALID_JSON"


def _unreadable(root: Path, mode: str, relative: str, policy: str, code: str) -> dict[str, Any]:
    v = _Verification(root, mode, policy, relative)
    v.start(CHECK_SCHEMA)
    v.fail(CHECK_SCHEMA, code, f"{relative} could not be read as a pointer")
    return v.result()


def verify_candidate_pointer(
    repo_root: Path | str,
    pointer_relative_path: str,
    *,
    results_policy: str = RESULTS_POLICY_NONE,
) -> dict[str, Any]:
    """Report whether a candidate pointer is internally consistent.

    A passing result is ``CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY``.
    It is never an acceptance, never promotes the candidate and never confers
    authority: ``is_current_authority`` and ``results_consumption_permitted``
    are always ``False`` in this mode.
    """

    root = Path(repo_root).resolve()
    pointer, digest, code = _read_pointer(root, pointer_relative_path)
    if code is not None:
        return _unreadable(root, MODE_CANDIDATE, pointer_relative_path, results_policy, code)
    result = _verify(
        root,
        pointer,
        mode=MODE_CANDIDATE,
        pointer_relative_path=pointer_relative_path,
        results_policy=results_policy,
    )
    result["pointer_sha256"] = digest
    return result


def verify_canonical_pointer(
    repo_root: Path | str, *, results_policy: str = RESULTS_POLICY_NONE
) -> dict[str, Any]:
    """Verify the canonical pointer, and only the canonical pointer.

    The canonical path is the single place looked at.  If nothing accepted and
    published is there, the result is ``FAIL_CLOSED``; no candidate, handoff or
    filename is consulted as a substitute route.
    """

    root = Path(repo_root).resolve()
    relative = CANONICAL_POINTER_RELATIVE_PATH
    pointer, digest, code = _read_pointer(root, relative)
    if code is not None:
        code = "CANONICAL_POINTER_ABSENT" if code == "POINTER_ABSENT" else code
        return _unreadable(root, MODE_CANONICAL, relative, results_policy, code)
    result = _verify(
        root,
        pointer,
        mode=MODE_CANONICAL,
        pointer_relative_path=relative,
        results_policy=results_policy,
    )
    result["pointer_sha256"] = digest
    return result


def require_current_mainline(
    repo_root: Path | str,
    *,
    purpose: str,
    results_policy: str = RESULTS_POLICY_STRICT,
) -> dict[str, Any]:
    """Return the verified current-mainline route, or raise.

    The read-first entry point for downstream tools.  It succeeds only for a
    verified canonical pointer and only for a purpose the pointer permits; a
    purpose blocked by an open scientific-exposure restriction is refused.
    The run path is returned only after strict result verification.
    """

    result = verify_canonical_pointer(repo_root, results_policy=results_policy)
    if result["verdict"] != VERDICT_CANONICAL_VERIFIED:
        raise CurrentMainlinePointerError("CANONICAL_POINTER_NOT_VERIFIED", result)
    exposure = result["scientific_exposure"]
    if purpose in exposure["blocked_purposes"]:
        raise CurrentMainlinePointerError(
            "PURPOSE_BLOCKED_BY_SCIENTIFIC_EXPOSURE_RESTRICTION", result
        )
    if purpose not in exposure["permitted_purposes"]:
        raise CurrentMainlinePointerError("PURPOSE_NOT_PERMITTED", result)
    pointer, _digest, _code = _read_pointer(
        Path(repo_root).resolve(), CANONICAL_POINTER_RELATIVE_PATH
    )
    results = pointer["accepted_result_set"]
    return {
        "purpose": purpose,
        "methodology_authority": pointer["methodology_authority"]["document"]["path"],
        "evidence_authority": pointer["evidence_authority"]["document"]["path"],
        "production_generation": pointer["production_generation"]["generation_id"],
        "canonical_annual_input": pointer["canonical_annual_input"]["path"],
        "scientific_model_core": pointer["implementation"]["scientific_model_core"]["path"],
        "production_successor_stack": pointer["implementation"]["production_successor_stack"][
            "path"
        ],
        "production_runner": pointer["implementation"]["production_runner"]["path"],
        "accepted_result_run_id": results["run_id"],
        "accepted_result_run_path": (
            results["run_path"] if result["results_consumption_permitted"] else None
        ),
        "results_consumption_permitted": result["results_consumption_permitted"],
        "grants_execution_authority": False,
        "verification": result,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only verifier for the Iris Thesis current-mainline pointer."
    )
    parser.add_argument("mode", choices=("candidate", "canonical"))
    parser.add_argument("--pointer", help="candidate pointer path (candidate mode only)")
    parser.add_argument("--results-policy", choices=RESULTS_POLICIES, default=RESULTS_POLICY_NONE)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    arguments = parser.parse_args(argv)
    if arguments.mode == "candidate":
        if not arguments.pointer:
            parser.error("candidate mode requires --pointer")
        result = verify_candidate_pointer(
            arguments.repo_root, arguments.pointer, results_policy=arguments.results_policy
        )
    else:
        if arguments.pointer:
            parser.error("canonical mode reads only the canonical path")
        result = verify_canonical_pointer(
            arguments.repo_root, results_policy=arguments.results_policy
        )
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["verdict"] != VERDICT_FAIL_CLOSED else 2


if __name__ == "__main__":
    raise SystemExit(main())
