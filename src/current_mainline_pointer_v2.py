"""Read-only verifier for the Iris Thesis current-mainline pointer, schema v2.

Schema v2 is an additive compatibility route.  It lets a pointer name a
METHODOLOGY-ONLY authority, Framework v8 with the composite Registry v8, while
every v8 implementation, production, input-compatibility, Pilot and result
stage is still unbuilt.  The v1 schema cannot say that: it requires a current
production generation, implementation, canonical input and accepted result set,
and anchors the methodology document at the historical Full81 execution commit.

Nothing in :mod:`current_mainline_pointer_v1` is changed.  v1 keeps verifying
schema-v1 pointers, including the canonical pointer R2 while v7.4 is current.
This module reuses v1's generic machinery wherever it is not tied to v7.4 G1 or
Full81:

* path containment, raw-byte SHA-256 and Git-blob identities, anchor-commit
  roles and the EOL classification (``_check_paths``, ``_check_files``);
* candidate / canonical lifecycle separation (``_check_lifecycle``);
* the audited, accepted and published activation basis (``_check_activation``);
* read-only Git access (``_Git``) and the fail-closed result discipline.

It replaces the G1 checks with v8 ones:

* the Framework v8 document, the Gate 3 acceptance record and the Gate 2
  governing sources are anchored at the v8 package publication commit, never at
  the historical execution commit, and the Gate 3 record bytes must state their
  SHA-256 values, the audit verdict and the composite Registry formula;
* Registry v8 is exactly Registry v7.4 (base) plus Registry v8 Delta R1;
* every unbuilt v8 stage carries its exact ``NOT_YET_*`` sentinel and nothing
  else, so no historical or placeholder identity can stand in for it;
* v7.4 history is bound by content: the predecessor pointer R2 (audited
  candidate file and canonical Git object), pointer R1, and the historical
  verification route, which this module runs (v1, candidate mode, on R2).

Three status words are kept apart:

``NOT_APPLICABLE``
    A check status.  Only the v8 result-validation check uses it, and only after
    confirming that the numerical-result and result-acceptance stages are
    ``NOT_YET_EXECUTED``: there is no v8 result object to inspect.  Any other
    stage state fails that check.  The activation check is ``NOT_APPLICABLE`` in
    candidate mode, as in v1.
``NOT_YET_EXECUTED`` / ``NOT_YET_AUTHORIZED``
    Pointer sentinels for research stages that have not occurred or have not
    been authorized (Version Provenance Protocol sections 3, 12, 14 and 24).
``FAIL_CLOSED``
    The verdict whenever a required identity or consistency condition fails.

A candidate that passes is ``CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY``:
never an acceptance, never an activation.  Canonical mode reads only the
canonical path and requires a schema-v2 pointer whose activation basis is
audited, accepted and published; a schema-v1 canonical pointer is reported
``FAIL_CLOSED`` here and is verified by v1.

Standard library only (plus v1).  No solver import, no model construction, no
``optimize()``, no file written, no state-changing Git subcommand.  Like v1, it
carries no identity literal: every expected hash and commit lives in the pointer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from src import current_mainline_pointer_v1 as v1
except ImportError:  # run as a script: python -B src/current_mainline_pointer_v2.py
    import current_mainline_pointer_v1 as v1

INTERFACE_VERSION = "iris-thesis-current-mainline-pointer-verifier-v2"
POINTER_ARTIFACT_TYPE = v1.POINTER_ARTIFACT_TYPE
POINTER_SCHEMA_VERSION = "iris-thesis-current-mainline-pointer-v2"
VERIFIER_MODULE_RELATIVE_PATH = "src/current_mainline_pointer_v2.py"

CANONICAL_POINTER_RELATIVE_PATH = v1.CANONICAL_POINTER_RELATIVE_PATH
CANDIDATE_DIRECTORY_RELATIVE_PATH = v1.CANDIDATE_DIRECTORY_RELATIVE_PATH
POINTER_SEARCH_ROOT_RELATIVE_PATH = v1.POINTER_SEARCH_ROOT_RELATIVE_PATH

MODE_CANDIDATE = v1.MODE_CANDIDATE
MODE_CANONICAL = v1.MODE_CANONICAL
VERDICT_CANDIDATE_CONSISTENT = v1.VERDICT_CANDIDATE_CONSISTENT
VERDICT_CANONICAL_VERIFIED = v1.VERDICT_CANONICAL_VERIFIED
VERDICT_FAIL_CLOSED = v1.VERDICT_FAIL_CLOSED

STATUS_PASS = v1.STATUS_PASS
STATUS_FAIL = v1.STATUS_FAIL
STATUS_NOT_RUN = v1.STATUS_NOT_RUN
STATUS_NOT_APPLICABLE = v1.STATUS_NOT_APPLICABLE

NOT_YET_AUTHORIZED = "NOT_YET_AUTHORIZED"
NOT_YET_EXECUTED = "NOT_YET_EXECUTED"
V8_RESULT_VALIDATION_NOT_APPLICABLE = "NOT_APPLICABLE_NO_V8_RESULT_OBJECT"
V8_RESULT_VALIDATION_FAIL = "FAIL_CLOSED"

FRAMEWORK_FORMAL_NAME = "Framework v8"
REGISTRY_FORMAL_NAME = "Registry v8"
REGISTRY_BASE_FORMAL_NAME = "Registry v7.4"
REGISTRY_DELTA_FORMAL_NAME = "Registry v8 Delta R1"
REGISTRY_COMPOSITION = "REGISTRY_V7_4_BASE_PLUS_REGISTRY_V8_DELTA_R1"
ROLE_METHODOLOGY = "CURRENT_METHODOLOGY_AUTHORITY"
ROLE_EVIDENCE = "CURRENT_EVIDENCE_AUTHORITY"
#: True before and after activation; whether the pointer is current lives in
#: the lifecycle envelope, so the audited payload never has to change.
LIFECYCLE_GATE3_ACCEPTED = "GATE3_ACCEPTED"
#: The Gate 3 audit report exists in conversation only (Gate 3 record section 2).
#: It is cited through the record, never bound as a file.
GATE3_AUDIT_CUSTODY = "CONVERSATION_ONLY_NOT_FILE_BOUND"
GATE3_NOT_ACTIVATED_MARKER = "NOT ACTIVATED"
#: Framework v8 R2 section 8.5-4: the Gate 2 sources the acceptance binds.
GATE2_SOURCE_IDS = ("REC", "SPEC", "CL1", "RES", "ART2", "DD")
#: The ids under which the Gate 3 record's own identity tables (section 1) list
#: each bound document.  A hash must appear on its own row, not just anywhere:
#: the record also lists Framework v7.4, which must never pass as Framework v8.
GATE3_RECORD_ROW_IDS: Mapping[str, str] = {
    "framework": "FW8R2",
    "registry_delta": "REGD",
    "registry_base": "REG74",
    "governing_protocol": "PROT",
}

HISTORICAL_SCOPE = "HISTORICAL_V7_4_FULL81_SCOPE_ONLY"
HISTORICAL_STATUS_UPON_ACTIVATION = "HISTORICAL_ACCEPTED_PREDECESSOR"
HISTORICAL_ROLE_PREFIX = "HISTORICAL_"

#: Every unbuilt v8 stage and its only valid (status, identity).  Build stages
#: need an authorization first (Protocol section 24); results have not occurred
#: (Protocol section 14).  Nothing else, and no identity, may stand here.
V8_UNBUILT_STAGES: Mapping[str, tuple[str, str]] = {
    "scientific_implementation": (NOT_YET_AUTHORIZED, NOT_YET_AUTHORIZED),
    "production_generation": (NOT_YET_AUTHORIZED, NOT_YET_AUTHORIZED),
    "production_runner": (NOT_YET_AUTHORIZED, NOT_YET_AUTHORIZED),
    "input_compatibility": (NOT_YET_AUTHORIZED, NOT_YET_AUTHORIZED),
    "pilot": (NOT_YET_AUTHORIZED, NOT_YET_EXECUTED),
    "numerical_results": (NOT_YET_EXECUTED, NOT_YET_EXECUTED),
    "result_acceptance": (NOT_YET_EXECUTED, NOT_YET_EXECUTED),
}
V8_RESULT_STAGES = ("numerical_results", "result_acceptance")
V8_STAGE_FIELDS = frozenset({"status", "identity"})

#: Boundaries every v2 pointer states (Gate 3 record section 4.2; Framework v8
#: R2 section 8.5-7).  A pointer may list more, never fewer.
REQUIRED_NON_AUTHORIZATIONS = (
    "V8_CODING_OR_IMPLEMENTATION",
    "MODEL_CONSTRUCTION",
    "SOLVER_CALL",
    "V8_PILOT",
    "V8_PRODUCTION_GENERATION_OR_RUN",
    "V8_INPUT_COMPATIBILITY_DECISION",
    "V8_RESULT_ACCEPTANCE",
    "SENSITIVITY_OR_VALIDATION_EXECUTION",
    "GIT_COMMIT_TAG_OR_PUSH",
    "HANDOFF_OR_PROTOCOL_ROUTING_UPDATE",
    "LAYER_B",
    "DG_EXTENSION",
    "BETA_24H_SCOPE",
    "NEW_KNEE_OR_MARGINAL_DECISION_RULE",
    "NEW_FULL81_EXECUTION_OR_RERUN",
    "U_01_RESOLUTION_OR_CALIBRATION",
    "A2_EXECUTION_OR_EXPOSURE",
    "REMEDIATION_OR_CLOSURE_OF_HISTORICAL_FINDINGS",
    "MODIFICATION_OF_HISTORICAL_V7_4_ARTIFACTS",
    "RENAMING_OF_HISTORICAL_VERSION_LABELS_OR_DIRECTORIES",
)

#: Candidate consistency -> independent audit -> researcher acceptance ->
#: publication / activation.  No step triggers the next.
ACTIVATION_CONTRACT: Mapping[str, Any] = {
    "lifecycle_sequence": [
        "CANDIDATE_CONSISTENCY",
        "INDEPENDENT_AUDIT",
        "RESEARCHER_ACCEPTANCE",
        "PUBLICATION_AND_ACTIVATION",
    ],
    "independent_audit_required_before_acceptance": True,
    "independent_audit_must_not_be_self_audit": True,
    "candidate_consistency_is_acceptance": False,
    "automatic_progression": False,
    "activation_record_form": "CANONICAL_POINTER_SUCCESSOR",
    "activation_artifact_types": {
        "independent_audit_record": v1.ACTIVATION_AUDIT_ARTIFACT_TYPE,
        "acceptance_closure": v1.ACTIVATION_CLOSURE_ARTIFACT_TYPE,
        "acceptance_manifest": v1.ACTIVATION_MANIFEST_ARTIFACT_TYPE,
    },
    "closure_activation_binding_key": "accepted_methodology_activation",
}

CHECK_SCHEMA = "C01_SCHEMA_V2"
CHECK_LIFECYCLE = v1.CHECK_LIFECYCLE
CHECK_PATHS = v1.CHECK_PATHS
CHECK_GIT = "C04_GIT_PROVENANCE"
CHECK_FILES = v1.CHECK_FILES
CHECK_HISTORICAL_OBJECTS = "C06_HISTORICAL_GIT_OBJECT_IDENTITIES"
CHECK_V8_AUTHORITY = "C07_V8_METHODOLOGY_EVIDENCE_AND_GATE3_BINDINGS"
CHECK_V8_STAGES = "C08_V8_NOT_YET_STAGE_STATUSES"
CHECK_ROLES = "C09_ROLES_AND_CONFLICTING_CLAIMS"
CHECK_HISTORICAL = "C10_HISTORICAL_V7_4_PRESERVATION"
CHECK_BOUNDARIES = "C11_NON_AUTHORIZATION_AND_ACTIVATION_CONTRACT"
CHECK_V8_RESULTS = "C12_V8_RESULT_VALIDATION"
CHECK_HISTORICAL_ROUTE = "C13_HISTORICAL_V7_4_VERIFICATION_ROUTE"
CHECK_ACTIVATION = "C14_CANONICAL_ACTIVATION_BASIS"
CHECK_IDS = (
    CHECK_SCHEMA,
    CHECK_LIFECYCLE,
    CHECK_PATHS,
    CHECK_GIT,
    CHECK_FILES,
    CHECK_HISTORICAL_OBJECTS,
    CHECK_V8_AUTHORITY,
    CHECK_V8_STAGES,
    CHECK_ROLES,
    CHECK_HISTORICAL,
    CHECK_BOUNDARIES,
    CHECK_V8_RESULTS,
    CHECK_HISTORICAL_ROUTE,
    CHECK_ACTIVATION,
)
#: v1 check ids raised by the reused v1 checks, and the v2 check they report to.
_V1_CHECK_ALIASES: Mapping[str, str] = {
    v1.CHECK_LIFECYCLE: CHECK_LIFECYCLE,
    v1.CHECK_PATHS: CHECK_PATHS,
    v1.CHECK_FILES: CHECK_FILES,
    v1.CHECK_ACTIVATION: CHECK_ACTIVATION,
}

_MISSING = v1._MISSING
_FILE, _SHA, _COMMIT = v1._FILE, v1._SHA, v1._COMMIT
_IDENTITY_LIKE_RE = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

#: An object in Git history, verified against that commit's tree only, never
#: against the live HEAD (the canonical path is rewritten on every activation).
_GIT_OBJECT = {
    "git_path": str,
    "git_commit": _COMMIT,
    "git_blob_id": _COMMIT,
    "blob_sha256": _SHA,
    "blob_bytes": int,
}

#: Top level is closed-world; nested objects are open-world (v1 convention),
#: except the v8 stages and carried identities, which their checks close.
POINTER_SCHEMA: Mapping[str, Any] = {
    "artifact_type": str,
    "schema_version": str,
    "pointer_revision": str,
    "documentation": {"purpose": str, "serialization": str, "path_convention": str},
    "pointer_identity": v1.POINTER_SCHEMA["pointer_identity"],
    "activation_basis": v1.POINTER_SCHEMA["activation_basis"],
    "methodology_authority": {
        "formal_name": str,
        "role": str,
        "lifecycle": str,
        "document": _FILE,
        "gate3_acceptance_record": _FILE,
        "gate3_independent_audit": {
            "verdict_as_recorded": str,
            "report_custody": str,
            "report_file": (None,),
        },
        "gate3_researcher_acceptance": {
            "acceptor": str,
            "decision_ids": [str],
            "activation_authorized_by_gate3_record": bool,
        },
        "gate2_governing_sources": [{"source_id": str, "document": _FILE}],
        "governing_protocol": _FILE,
    },
    "evidence_authority": {
        "formal_name": str,
        "role": str,
        "lifecycle": str,
        "composition": str,
        "composite_formula_as_recorded": str,
        "delta_alone_is_registry_v8": bool,
        "base_component": {
            "formal_name": str,
            "acceptance_commit": _COMMIT,
            "modified_by_v8": bool,
            "document": _FILE,
        },
        "delta_component": {"formal_name": str, "document": _FILE},
    },
    "v8_unbuilt_stages": {"historical_identity_reuse_permitted": bool},
    "historical_v7_4_authority": {
        "scope": str,
        "status_upon_activation": str,
        "bytes_modified_by_this_pointer": bool,
        "predecessor_pointer": {
            "pointer_id": str,
            "schema_version": str,
            "payload_digest": _SHA,
            "canonical_object": _GIT_OBJECT,
            "audited_candidate": _FILE,
            "independent_audit_record": _FILE,
            "acceptance_closure": _FILE,
            "acceptance_manifest": _FILE,
        },
        "pointer_r1": {
            "pointer_id": str,
            "payload_digest": _SHA,
            "canonical_object": _GIT_OBJECT,
            "candidate": _FILE,
        },
        "historical_verification_route": {
            "verifier_module_identity": _FILE,
            "verifier_interface_version": str,
            "mode": str,
            "pointer_path": str,
            "results_policy": str,
        },
        "carried_identities": {},
        "carried_dispositions": {
            "scope": str,
            "reinterpreted_as_v8_constraint": bool,
            "closed_or_remediated_by_this_pointer": [str],
            "ACC-N1": {"severity": str, "disposition": str, "closed": bool},
            "U-01": {"status": str, "must_be_frozen_before": [str]},
            "A2": {"a2_variable_floor_status": str},
        },
    },
    "git_provenance": {
        "branch": str,
        "upstream_ref": str,
        "v8_package_publication_commit": _COMMIT,
        "predecessor_pointer_activation_commit": _COMMIT,
        "ancestry_chain_oldest_to_newest": [_COMMIT],
        "live_head_must_equal_a_recorded_commit": bool,
    },
    "roles": {
        "accepted_current": [{"role": str, "path": str}],
        "historical_only": [{"role": str, "path": str}],
    },
    "non_authorization_boundaries": {
        "pointer_grants_execution_authority": bool,
        "authorizes": [str],
        "not_authorized_by_this_pointer": [str],
    },
    "activation_contract": {"predecessor_pointer_id": str},
    "validation_contract": {
        "verifier_module": str,
        "verifier_interface_version": str,
        "required_checks": [str],
    },
}

_METHODOLOGY = ("methodology_authority",)
_EVIDENCE = ("evidence_authority",)
_BASE = (*_EVIDENCE, "base_component")
_DELTA = (*_EVIDENCE, "delta_component")
_STAGES = ("v8_unbuilt_stages",)
_HISTORICAL = ("historical_v7_4_authority",)
_PREDECESSOR = (*_HISTORICAL, "predecessor_pointer")
_POINTER_R1 = (*_HISTORICAL, "pointer_r1")
_ROUTE = (*_HISTORICAL, "historical_verification_route")
_CARRIED = (*_HISTORICAL, "carried_identities")
_DISPOSITIONS = (*_HISTORICAL, "carried_dispositions")
_PROVENANCE = ("git_provenance",)

#: The complete, ordered accepted-current role list (default deny).  The
#: labels describe the routing this pointer would establish once activated.
ACCEPTED_CURRENT_ROLES: tuple[tuple[str, tuple], ...] = (
    (ROLE_METHODOLOGY, (*_METHODOLOGY, "document", "path")),
    ("CURRENT_EVIDENCE_AUTHORITY_BASE_COMPONENT", (*_BASE, "document", "path")),
    ("CURRENT_EVIDENCE_AUTHORITY_DELTA_COMPONENT", (*_DELTA, "document", "path")),
    ("METHODOLOGY_GATE3_ACCEPTANCE_RECORD", (*_METHODOLOGY, "gate3_acceptance_record", "path")),
)

#: Historical v7.4 values the pointer restates, each compared with the bound
#: predecessor payload (pointer R2).  Restated, never re-derived or re-graded.
CARRIED_IDENTITIES: Mapping[str, tuple[str, ...]] = {
    "framework_v7_4_document_path": ("methodology_authority", "document", "path"),
    "framework_v7_4_document_sha256": ("methodology_authority", "document", "sha256"),
    "registry_v7_4_document_sha256": ("evidence_authority", "document", "sha256"),
    "production_generation_id": ("production_generation", "generation_id"),
    "g1_accepted_lifecycle_record_sha256": (
        "production_generation", "accepted_lifecycle_record", "sha256",
    ),
    "canonical_annual_input_sha256": ("canonical_annual_input", "sha256"),
    "scientific_model_core_sha256": ("implementation", "scientific_model_core", "sha256"),
    "production_successor_stack_sha256": (
        "implementation", "production_successor_stack", "sha256",
    ),
    "production_runner_sha256": ("implementation", "production_runner", "sha256"),
    "historical_execution_commit": ("git_provenance", "historical_execution_commit"),
    "full81_run_id": ("accepted_result_set", "run_id"),
    "full81_run_file_aggregate_sha256": ("accepted_result_set", "run_file_aggregate", "sha256"),
    "results_acceptance_closure_sha256": (
        "formal_results_acceptance", "acceptance_closure", "sha256",
    ),
    "results_acceptance_publication_commit": ("formal_results_acceptance", "publication_commit"),
}


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


class _Verification(v1._Verification):
    """v1's verification state, reporting to the v2 check ids."""

    def __init__(self, root: Path, mode: str, pointer_relative_path: str) -> None:
        # v2 binds no local result file; v1's file check needs a policy only
        # for untracked identities, which the v2 schema refuses.
        super().__init__(root, mode, v1.RESULTS_POLICY_NONE, pointer_relative_path)
        self.checks = {check: STATUS_NOT_RUN for check in CHECK_IDS}
        self.predecessor: Mapping[str, Any] | None = None
        self.v8_result_validation = STATUS_NOT_RUN

    def start(self, check: str) -> None:
        super().start(_V1_CHECK_ALIASES.get(check, check))

    def fail(self, check: str, code: str, detail: str) -> None:
        super().fail(_V1_CHECK_ALIASES.get(check, check), code, detail)

    def value(self, path: Sequence[Any]) -> Any:
        if path and path[0] == "__interface__":
            return globals()[path[1]]
        return v1._lookup(self.pointer, path)

    def result(self) -> dict[str, Any]:
        failed = bool(self.failures)
        if failed:
            verdict = VERDICT_FAIL_CLOSED
        elif self.mode == MODE_CANONICAL:
            verdict = VERDICT_CANONICAL_VERIFIED
        else:
            verdict = VERDICT_CANDIDATE_CONSISTENT
        authority = self.mode == MODE_CANONICAL and not failed
        routed = {
            "methodology_authority": None,
            "evidence_authority_components": [],
        }
        if authority:
            routed = {
                "methodology_authority": self.value((*_METHODOLOGY, "document", "path")),
                "evidence_authority_components": [
                    self.value((*_BASE, "document", "path")),
                    self.value((*_DELTA, "document", "path")),
                ],
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
            "candidate_accepted": False,
            "activation_performed_by_this_verification": False,
            "routed_current_authority": routed,
            "v8_result_validation": self.v8_result_validation,
            "results_consumption_permitted": False,
            "checks": dict(self.checks),
            "failure_codes": sorted({failure["code"] for failure in self.failures}),
            "failures": list(self.failures),
            "notes": list(self.notes),
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
    found = (pointer.get("artifact_type"), pointer.get("schema_version"))
    if found != (POINTER_ARTIFACT_TYPE, POINTER_SCHEMA_VERSION):
        v.fail(
            CHECK_SCHEMA,
            "SCHEMA_VERSION_NOT_V2",
            f"found {found!r}; this interface verifies {POINTER_SCHEMA_VERSION} only "
            f"({v1.POINTER_SCHEMA_VERSION} pointers are verified by "
            f"{v1.VERIFIER_MODULE_RELATIVE_PATH})",
        )
        return False
    problems: list[str] = []
    v1._schema_problems(pointer, POINTER_SCHEMA, "pointer", problems)
    for key in pointer:
        if key not in POINTER_SCHEMA:
            problems.append(f"pointer.{key}: unknown top-level key")
    for location, _key, value, _parent in v1._walk(pointer):
        if v1._is_file_identity(value) and value.get("git_tracked") is not True:
            problems.append(f"pointer.{location}: a v2 pointer binds Git-tracked identities only")
    for problem in problems:
        v.fail(CHECK_SCHEMA, "SCHEMA_VIOLATION", problem)
    return not problems


def _recorded_commits(pointer: Mapping[str, Any]) -> dict[str, str]:
    commits: dict[str, str] = {}
    for location, key, value, _parent in v1._walk(pointer):
        if isinstance(value, str) and key.endswith("_commit"):
            commits.setdefault(value, location)
    for index, sha in enumerate(pointer["git_provenance"]["ancestry_chain_oldest_to_newest"]):
        commits.setdefault(sha, f"git_provenance.ancestry_chain_oldest_to_newest[{index}]")
    return commits


def _check_git(v: _Verification) -> bool:
    """Same publication discipline as v1, over the v2 provenance fields."""

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
        "the pointer must not require the live HEAD to equal a recorded commit",
    )
    in_head = v.git.reachable_from(head)
    published = v.git.reachable_from(upstream) if upstream is not None else frozenset()
    for sha, location in _recorded_commits(v.pointer).items():
        if sha not in in_head:
            v.fail(
                CHECK_GIT,
                "GIT_COMMIT_NOT_IN_HEAD_ANCESTRY" if v.git.is_commit(sha) else "GIT_COMMIT_ABSENT",
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
    for name in ("v8_package_publication_commit", "predecessor_pointer_activation_commit"):
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
        "live_head_equality_is_not_required": True,
    }
    return True


def _git_objects(pointer: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    return [
        (location, value)
        for location, _key, value, _parent in v1._walk(pointer)
        if isinstance(value, Mapping) and "git_commit" in value and "blob_sha256" in value
    ]


def _check_historical_objects(v: _Verification, git_ok: bool) -> None:
    """Objects bound at a historical commit: tree entry, blob bytes, authorship."""

    v.start(CHECK_HISTORICAL_OBJECTS)
    if not git_ok:
        v.fail(CHECK_HISTORICAL_OBJECTS, "GIT_UNAVAILABLE", "historical objects need Git")
        return
    for location, entry in _git_objects(v.pointer):
        relative, commit, blob = entry["git_path"], entry["git_commit"], entry["git_blob_id"]
        if not v.equal(
            CHECK_HISTORICAL_OBJECTS,
            "HISTORICAL_OBJECT_BLOB_MISMATCH",
            v.git.tree(commit).get(relative, _MISSING),
            blob,
            f"{location}: blob of {relative} in {commit}",
        ):
            continue
        v.require(
            CHECK_HISTORICAL_OBJECTS,
            "HISTORICAL_OBJECT_BYTES_MISMATCH",
            v.git.blob_digests([blob])[blob] == (entry["blob_sha256"], entry["blob_bytes"]),
            f"{location}: blob {blob} does not hash to the recorded SHA-256 and size",
        )
        v.require(
            CHECK_HISTORICAL_OBJECTS,
            "HISTORICAL_OBJECT_NOT_WRITTEN_BY_COMMIT",
            all(v.git.tree(parent).get(relative) != blob for parent in v.git.parents(commit)),
            f"{location}: {commit} did not write this content of {relative}",
        )
        data = v.git.blob_bytes(blob)
        try:
            v.records[location] = json.loads(data.decode("utf-8")) if data is not None else None
        except (UnicodeDecodeError, ValueError):
            v.records[location] = None
        v.require(
            CHECK_HISTORICAL_OBJECTS,
            "HISTORICAL_OBJECT_UNREADABLE",
            isinstance(v.records[location], Mapping),
            f"{location}: blob {blob} is not a JSON object",
        )


def _v8_identities(pointer: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    """Every identity the v8 methodology route binds as v8 content."""

    methodology = pointer["methodology_authority"]
    delta = pointer["evidence_authority"]["delta_component"]
    rows = [
        ("methodology_authority.document", methodology["document"]),
        ("methodology_authority.gate3_acceptance_record", methodology["gate3_acceptance_record"]),
        ("evidence_authority.delta_component.document", delta["document"]),
    ]
    rows += [
        (f"methodology_authority.gate2_governing_sources[{index}].document", source["document"])
        for index, source in enumerate(methodology["gate2_governing_sources"])
    ]
    return rows


def _check_v8_authority(v: _Verification) -> None:
    v.start(CHECK_V8_AUTHORITY)
    check = CHECK_V8_AUTHORITY
    methodology = v.pointer["methodology_authority"]
    evidence = v.pointer["evidence_authority"]
    base, delta = evidence["base_component"], evidence["delta_component"]
    for code, location, expected in (
        ("V8_METHODOLOGY_MISLABELED", (*_METHODOLOGY, "formal_name"), FRAMEWORK_FORMAL_NAME),
        ("V8_METHODOLOGY_MISLABELED", (*_METHODOLOGY, "role"), ROLE_METHODOLOGY),
        ("V8_METHODOLOGY_MISLABELED", (*_METHODOLOGY, "lifecycle"), LIFECYCLE_GATE3_ACCEPTED),
        ("V8_EVIDENCE_MISLABELED", (*_EVIDENCE, "formal_name"), REGISTRY_FORMAL_NAME),
        ("V8_EVIDENCE_MISLABELED", (*_EVIDENCE, "role"), ROLE_EVIDENCE),
        ("V8_EVIDENCE_MISLABELED", (*_EVIDENCE, "lifecycle"), LIFECYCLE_GATE3_ACCEPTED),
        ("EVIDENCE_AUTHORITY_NOT_COMPOSITE", (*_EVIDENCE, "composition"), REGISTRY_COMPOSITION),
        ("EVIDENCE_AUTHORITY_NOT_COMPOSITE", (*_EVIDENCE, "delta_alone_is_registry_v8"), False),
        ("EVIDENCE_AUTHORITY_NOT_COMPOSITE", (*_BASE, "formal_name"), REGISTRY_BASE_FORMAL_NAME),
        ("EVIDENCE_AUTHORITY_NOT_COMPOSITE", (*_DELTA, "formal_name"), REGISTRY_DELTA_FORMAL_NAME),
        ("REGISTRY_BASE_MODIFIED_BY_V8", (*_BASE, "modified_by_v8"), False),
    ):
        v.equal(check, code, v.value(location), expected, ".".join(location))
    v.require(
        check,
        "EVIDENCE_AUTHORITY_NOT_COMPOSITE",
        "document" not in evidence,
        "Registry v8 is the base plus the delta; a single evidence document is refused",
    )
    v.require(
        check,
        "EVIDENCE_AUTHORITY_NOT_COMPOSITE",
        base["document"]["path"] != delta["document"]["path"],
        "the base and the delta must be different documents",
    )
    publication = v.pointer["git_provenance"]["v8_package_publication_commit"]
    historical_execution = v1._lookup(
        v.predecessor, ("git_provenance", "historical_execution_commit")
    )
    v.require(
        check,
        "PREDECESSOR_PAYLOAD_UNAVAILABLE",
        isinstance(historical_execution, str),
        "the historical execution commit cannot be read from the predecessor pointer",
    )
    for where, identity in _v8_identities(v.pointer):
        anchor = identity["git_anchor_commit"]
        v.require(
            check,
            "V8_ANCHORED_TO_HISTORICAL_EXECUTION_COMMIT",
            anchor != historical_execution,
            f"{where} is anchored at the historical v7.4 execution commit {anchor}",
        )
        v.require(
            check,
            "V8_IDENTITY_NOT_ANCHORED_AT_V8_PUBLICATION",
            anchor == publication and identity["git_anchor_role"] == v1.ANCHOR_ADDED,
            f"{where} must be bound to the commit that published it, {publication}",
        )
    sources = methodology["gate2_governing_sources"]
    v.equal(
        check,
        "GATE2_SOURCES_INCOMPLETE",
        [source["source_id"] for source in sources],
        list(GATE2_SOURCE_IDS),
        "methodology_authority.gate2_governing_sources[].source_id",
    )
    registry_v7_4 = v1._lookup(v.predecessor, ("evidence_authority",))
    if isinstance(registry_v7_4, Mapping):
        for field in ("path", "sha256"):
            v.equal(
                check,
                "REGISTRY_BASE_NOT_REGISTRY_V7_4",
                base["document"][field],
                v1._lookup(registry_v7_4, ("document", field)),
                f"evidence_authority.base_component.document.{field}",
            )
        v.equal(
            check,
            "REGISTRY_BASE_NOT_REGISTRY_V7_4",
            base["acceptance_commit"],
            registry_v7_4.get("acceptance_commit", _MISSING),
            "evidence_authority.base_component.acceptance_commit",
        )
    else:
        v.fail(check, "PREDECESSOR_PAYLOAD_UNAVAILABLE", "Registry v7.4 cannot be read from it")
    _check_gate3_record(v, methodology, evidence)


def _check_gate3_record(
    v: _Verification, methodology: Mapping[str, Any], evidence: Mapping[str, Any]
) -> None:
    """The Gate 3 record's own bytes must state what the pointer says it accepted."""

    check = CHECK_V8_AUTHORITY
    path = v.resolve(methodology["gate3_acceptance_record"]["path"])
    try:
        text = path.read_bytes().decode("utf-8") if path is not None and path.is_file() else None
    except (OSError, UnicodeDecodeError):
        text = None
    if not v.require(
        check, "GATE3_RECORD_UNREADABLE", text is not None, "the Gate 3 record is not readable"
    ):
        return
    rows = [
        (GATE3_RECORD_ROW_IDS["framework"], methodology["document"]["sha256"]),
        (GATE3_RECORD_ROW_IDS["registry_base"], evidence["base_component"]["document"]["sha256"]),
        (GATE3_RECORD_ROW_IDS["registry_delta"], evidence["delta_component"]["document"]["sha256"]),
        (GATE3_RECORD_ROW_IDS["governing_protocol"], methodology["governing_protocol"]["sha256"]),
        *(
            (source["source_id"], source["document"]["sha256"])
            for source in methodology["gate2_governing_sources"]
        ),
    ]
    lines = text.splitlines()
    for row_id, sha in rows:
        row = re.compile(rf"^\|\s*{re.escape(row_id)}(?=[\s|（(])")
        v.require(
            check,
            "GATE3_RECORD_DOES_NOT_BIND",
            any(row.match(line) and sha in line for line in lines),
            f"the Gate 3 record has no {row_id} row stating {sha}",
        )
    acceptance = methodology["gate3_researcher_acceptance"]
    stated = [("composite Registry formula", evidence["composite_formula_as_recorded"])]
    stated += [(f"researcher decision {d}", d) for d in acceptance["decision_ids"]]
    for label, value in stated:
        v.require(
            check,
            "GATE3_RECORD_DOES_NOT_BIND",
            bool(value) and value in text,
            f"the Gate 3 record does not state the {label} ({value!r})",
        )
    v.require(
        check,
        "GATE3_RECORD_DOES_NOT_BIND",
        bool(acceptance["decision_ids"]),
        "no researcher decision is cited",
    )
    audit = methodology["gate3_independent_audit"]
    verdict = audit["verdict_as_recorded"]
    v.require(
        check,
        "GATE3_AUDIT_NOT_PASS",
        verdict in text and verdict.endswith("PASS") and "STOP" not in verdict
        and "CONDITIONAL" not in verdict.upper(),
        f"the Gate 3 record does not carry the PASS verdict {verdict!r}",
    )
    v.equal(
        check,
        "GATE3_AUDIT_CUSTODY_MISSTATED",
        audit["report_custody"],
        GATE3_AUDIT_CUSTODY,
        "methodology_authority.gate3_independent_audit.report_custody",
    )
    v.require(
        check,
        "GATE3_RECORD_CLAIMS_ACTIVATION",
        acceptance["activation_authorized_by_gate3_record"] is False
        and GATE3_NOT_ACTIVATED_MARKER in text,
        "Gate 3 acceptance is not activation; the record must say NOT ACTIVATED",
    )


def _check_v8_stages(v: _Verification) -> None:
    v.start(CHECK_V8_STAGES)
    check = CHECK_V8_STAGES
    stages = v.pointer["v8_unbuilt_stages"]
    v.equal(
        check,
        "V8_HISTORICAL_IDENTITY_REUSE_PERMITTED",
        stages["historical_identity_reuse_permitted"],
        False,
        "v8_unbuilt_stages.historical_identity_reuse_permitted",
    )
    declared = {
        key for key in stages
        if not v1.is_descriptive_key(key) and key != "historical_identity_reuse_permitted"
    }
    for name in sorted(declared - set(V8_UNBUILT_STAGES)):
        v.fail(check, "V8_STAGE_UNKNOWN", f"v8_unbuilt_stages.{name} is not a known stage")
    for name, (status, identity) in V8_UNBUILT_STAGES.items():
        stage = stages.get(name, _MISSING)
        where = f"v8_unbuilt_stages.{name}"
        if not isinstance(stage, Mapping):
            v.fail(check, "V8_STAGE_STATUS_MISSING", f"{where} is missing")
            continue
        fields = {key for key in stage if not v1.is_descriptive_key(key)}
        v.require(
            check,
            "V8_STAGE_CARRIES_UNDECLARED_FIELD",
            fields == V8_STAGE_FIELDS,
            f"{where} may carry status and identity only, found {sorted(fields)}",
        )
        found = stage.get("identity", _MISSING)
        if found != identity:
            fabricated = isinstance(found, Mapping) or (
                isinstance(found, str) and (_IDENTITY_LIKE_RE.match(found) or "/" in found)
            )
            v.fail(
                check,
                "V8_STAGE_IDENTITY_FABRICATED" if fabricated else "V8_STAGE_STATUS_INVALID",
                f"{where}.identity: found {v1._show(found)}, expected {identity!r}",
            )
        stage_status = stage.get("status", _MISSING)
        v.equal(check, "V8_STAGE_STATUS_INVALID", stage_status, status, f"{where}.status")


def _check_v8_results(v: _Verification) -> None:
    """NOT_APPLICABLE only when no v8 result object can exist."""

    absent = all(
        isinstance(stage, Mapping)
        and {k for k in stage if not v1.is_descriptive_key(k)} == V8_STAGE_FIELDS
        and stage.get("status") == NOT_YET_EXECUTED
        and stage.get("identity") == NOT_YET_EXECUTED
        for stage in (v.value((*_STAGES, name)) for name in V8_RESULT_STAGES)
    )
    if absent:
        v.checks[CHECK_V8_RESULTS] = STATUS_NOT_APPLICABLE
        v.v8_result_validation = V8_RESULT_VALIDATION_NOT_APPLICABLE
        return
    v.fail(
        CHECK_V8_RESULTS,
        "V8_RESULT_CLAIM_WITHOUT_RESULT_VALIDATOR",
        "a v8 result stage is not NOT_YET_EXECUTED; interface v2 has no v8 result validator",
    )
    v.v8_result_validation = V8_RESULT_VALIDATION_FAIL


def _predecessor_bound_paths(predecessor: Mapping[str, Any]) -> set[str]:
    """Every path pointer R2 binds or routes, in any role."""

    paths = {
        value["path"]
        for _l, _k, value, _p in v1._walk(predecessor)
        if v1._is_file_identity(value) and isinstance(value.get("path"), str)
    }
    run_path = v1._lookup(predecessor, ("accepted_result_set", "run_path"))
    if isinstance(run_path, str):
        paths.add(run_path)
    return paths | set(_predecessor_routed_paths(predecessor))


def _predecessor_routed_paths(predecessor: Mapping[str, Any]) -> list[str]:
    roles = predecessor.get("roles")
    return [
        entry["path"]
        for group in (roles.values() if isinstance(roles, Mapping) else [])
        if isinstance(group, list)
        for entry in group
        if isinstance(entry, Mapping) and isinstance(entry.get("path"), str)
    ]


def _check_roles(v: _Verification) -> None:
    v.start(CHECK_ROLES)
    roles = v.pointer["roles"]
    v.equal(
        CHECK_ROLES,
        "ACCEPTED_CURRENT_ROLES_MISMATCH",
        roles["accepted_current"],
        [{"role": role, "path": v.value(location)} for role, location in ACCEPTED_CURRENT_ROLES],
        "roles.accepted_current",
    )
    current = [entry["path"] for entry in roles["accepted_current"]]
    historical = roles["historical_only"]
    for entry in historical:
        v.require(
            CHECK_ROLES,
            "HISTORICAL_ROLE_LABEL_INVALID",
            entry["role"].startswith(HISTORICAL_ROLE_PREFIX),
            f"{entry['path']}: a historical role label must start with {HISTORICAL_ROLE_PREFIX}",
        )
        for path in current:
            v.require(
                CHECK_ROLES,
                "NON_CURRENT_PATH_CLAIMED_CURRENT",
                not v1._overlaps(entry["path"], path),
                f"{entry['path']} is declared historical but overlaps the current path {path}",
            )
    if v.predecessor is None:
        v.fail(CHECK_ROLES, "PREDECESSOR_PAYLOAD_UNAVAILABLE", "pointer R2 could not be read")
    else:
        # Registry v7.4 is the only predecessor path that continues, unmodified,
        # as the base component of Registry v8.
        base = v.value((*_BASE, "document", "path"))
        bound = _predecessor_bound_paths(v.predecessor)
        for path in current:
            if path == base:
                continue
            for earlier in sorted(bound):
                v.require(
                    CHECK_ROLES,
                    "HISTORICAL_ROLE_PROMOTED_TO_V8_CURRENT",
                    not v1._overlaps(path, earlier),
                    f"{path} is v8-current but overlaps {earlier}, bound by pointer R2",
                )
        carried = {entry["path"] for entry in historical}
        for path in _predecessor_routed_paths(v.predecessor):
            if path != base:
                v.require(
                    CHECK_ROLES,
                    "HISTORICAL_ROLE_NOT_CARRIED",
                    path in carried,
                    f"{path}, routed by pointer R2, is not carried as historical",
                )
    _check_conflicting_pointers(v)


def _check_conflicting_pointers(v: _Verification) -> None:
    """v1's competing-pointer scan, over v1 and v2 pointers alike."""

    search_root = v.resolve(POINTER_SEARCH_ROOT_RELATIVE_PATH)
    canonical_present = False
    for path in sorted(search_root.rglob("*.json")) if search_root and search_root.is_dir() else []:
        relative = path.relative_to(v.root).as_posix()
        try:
            other = json.loads(path.read_bytes().decode("utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            canonical_present = canonical_present or relative == CANONICAL_POINTER_RELATIVE_PATH
            continue
        if not isinstance(other, Mapping) or other.get("artifact_type") != POINTER_ARTIFACT_TYPE:
            continue
        identity = other.get("pointer_identity")
        claims = not isinstance(identity, Mapping) or (
            identity.get("is_current_authority") is not False
            or identity.get("is_canonical") is not False
            or identity.get("lifecycle_state") != v1.LIFECYCLE_CANDIDATE
        )
        if relative == CANONICAL_POINTER_RELATIVE_PATH:
            canonical_present = True
            v.info["canonical_pointer_schema_version"] = other.get("schema_version")
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


def _check_historical(v: _Verification) -> None:
    v.start(CHECK_HISTORICAL)
    check = CHECK_HISTORICAL
    historical = v.pointer["historical_v7_4_authority"]
    for code, location, expected in (
        ("HISTORICAL_SCOPE_ALTERED", (*_HISTORICAL, "scope"), HISTORICAL_SCOPE),
        (
            "HISTORICAL_SCOPE_ALTERED",
            (*_HISTORICAL, "status_upon_activation"),
            HISTORICAL_STATUS_UPON_ACTIVATION,
        ),
        ("HISTORICAL_BYTES_MODIFIED", (*_HISTORICAL, "bytes_modified_by_this_pointer"), False),
        (
            "PREDECESSOR_SCHEMA_MISMATCH",
            (*_PREDECESSOR, "schema_version"),
            v1.POINTER_SCHEMA_VERSION,
        ),
        (
            "PREDECESSOR_ACTIVATION_COMMIT_MISMATCH",
            (*_PREDECESSOR, "canonical_object", "git_commit"),
            v.value((*_PROVENANCE, "predecessor_pointer_activation_commit")),
        ),
        (
            "PREDECESSOR_POINTER_ID_MISMATCH",
            ("activation_contract", "predecessor_pointer_id"),
            v.value((*_PREDECESSOR, "pointer_id")),
        ),
        (
            "HISTORICAL_ROUTE_MISDECLARED",
            (*_ROUTE, "verifier_module_identity", "path"),
            v1.VERIFIER_MODULE_RELATIVE_PATH,
        ),
        (
            "HISTORICAL_ROUTE_MISDECLARED",
            (*_ROUTE, "verifier_interface_version"),
            v1.INTERFACE_VERSION,
        ),
        ("HISTORICAL_ROUTE_MISDECLARED", (*_ROUTE, "mode"), v1.MODE_CANDIDATE),
        ("HISTORICAL_ROUTE_MISDECLARED", (*_ROUTE, "results_policy"), v1.RESULTS_POLICY_NONE),
        (
            "HISTORICAL_ROUTE_MISDECLARED",
            (*_ROUTE, "pointer_path"),
            v.value((*_PREDECESSOR, "audited_candidate", "path")),
        ),
    ):
        v.equal(check, code, v.value(location), expected, ".".join(location))
    predecessor = v.predecessor
    if predecessor is None:
        v.fail(check, "PREDECESSOR_PAYLOAD_UNAVAILABLE", "pointer R2 could not be read")
        return
    expected_digest = v.value((*_PREDECESSOR, "payload_digest"))
    v.equal(
        check,
        "PREDECESSOR_PAYLOAD_MISMATCH",
        v1.pointer_payload_digest(predecessor),
        expected_digest,
        "payload digest of the predecessor audited candidate",
    )
    v.equal(
        check,
        "PREDECESSOR_PAYLOAD_MISMATCH",
        v1._lookup(predecessor, ("pointer_identity", "lifecycle_state")),
        v1.LIFECYCLE_CANDIDATE,
        "lifecycle state of the predecessor audited candidate",
    )
    _check_canonical_object(v, _PREDECESSOR, "PREDECESSOR")
    _check_canonical_object(v, _POINTER_R1, "POINTER_R1")
    r1_candidate = v1._load_json(
        v, check, v.value((*_POINTER_R1, "candidate", "path")), "pointer R1 candidate"
    )
    if isinstance(r1_candidate, Mapping):
        v.equal(
            check,
            "POINTER_R1_PAYLOAD_MISMATCH",
            v1.pointer_payload_digest(r1_candidate),
            v.value((*_POINTER_R1, "payload_digest")),
            "payload digest of the pointer R1 candidate",
        )
    _check_predecessor_acceptance(v)
    carried = historical["carried_identities"]
    declared = set(CARRIED_IDENTITIES)
    undeclared = [k for k in carried if not v1.is_descriptive_key(k) and k not in declared]
    for key in sorted(undeclared):
        v.fail(check, "HISTORICAL_IDENTITY_UNDECLARED", f"carried_identities.{key} is not defined")
    for key, location in CARRIED_IDENTITIES.items():
        v.equal(
            check,
            "HISTORICAL_IDENTITY_ALTERED",
            carried.get(key, _MISSING),
            v1._lookup(predecessor, location),
            f"carried_identities.{key}",
        )
    _check_dispositions(v, predecessor)


def _check_canonical_object(v: _Verification, location: tuple, label: str) -> None:
    canonical = v.records.get(".".join((*location, "canonical_object")))
    if not isinstance(canonical, Mapping):
        v.fail(
            CHECK_HISTORICAL, f"{label}_CANONICAL_OBJECT_UNREADABLE", f"{label} canonical object"
        )
        return
    for code, actual, expected, what in (
        (
            f"{label}_PAYLOAD_MISMATCH",
            v1.pointer_payload_digest(canonical),
            v.value((*location, "payload_digest")),
            "payload digest of the canonical object",
        ),
        (
            f"{label}_POINTER_ID_MISMATCH",
            v1._lookup(canonical, ("pointer_identity", "pointer_id")),
            v.value((*location, "pointer_id")),
            "pointer id of the canonical object",
        ),
        (
            f"{label}_NOT_ACCEPTED_CANONICAL",
            v1._lookup(canonical, ("pointer_identity", "lifecycle_state")),
            v1.LIFECYCLE_CANONICAL,
            "lifecycle state of the canonical object",
        ),
    ):
        v.equal(CHECK_HISTORICAL, code, actual, expected, what)


def _check_predecessor_acceptance(v: _Verification) -> None:
    """Pointer R2's audit and acceptance, under the contract v1 activated it with."""

    check = CHECK_HISTORICAL
    roles = {
        role: v1._load_json(v, check, v.value((*_PREDECESSOR, role, "path")), role)
        for role in ("independent_audit_record", "acceptance_closure", "acceptance_manifest")
    }
    audit = roles["independent_audit_record"]
    closure, manifest = roles["acceptance_closure"], roles["acceptance_manifest"]
    candidate_sha = v.value((*_PREDECESSOR, "audited_candidate", "sha256"))
    audit_sha = v.value((*_PREDECESSOR, "independent_audit_record", "sha256"))
    closure_sha = v.value((*_PREDECESSOR, "acceptance_closure", "sha256"))
    digest = v.value((*_PREDECESSOR, "payload_digest"))
    for record, keys, expected in (
        (audit, ("artifact_type",), v1.ACTIVATION_AUDIT_ARTIFACT_TYPE),
        (audit, ("verdict",), "PASS"),
        (audit, ("self_audit",), False),
        (audit, ("audited_candidate", "sha256"), candidate_sha),
        (audit, ("audited_payload_digest",), digest),
        (closure, ("artifact_type",), v1.ACTIVATION_CLOSURE_ARTIFACT_TYPE),
        (closure, ("acceptance_status",), v1.ACCEPTANCE_STATUS_CLOSED_ACCEPTED),
        (closure, ("accepted_candidate", "sha256"), candidate_sha),
        (closure, ("accepted_payload_digest",), digest),
        (closure, ("independent_audit_record", "sha256"), audit_sha),
        (manifest, ("artifact_type",), v1.ACTIVATION_MANIFEST_ARTIFACT_TYPE),
        (manifest, ("acceptance_closure", "sha256"), closure_sha),
    ):
        v.equal(
            check,
            "PREDECESSOR_ACCEPTANCE_INVALID",
            v1._lookup(record, keys) if record is not None else _MISSING,
            expected,
            ".".join(keys),
        )


def _check_dispositions(v: _Verification, predecessor: Mapping[str, Any]) -> None:
    """ACC-N1, U-01 and A2 stay exactly as R2 records them, in v7.4 scope only."""

    check = CHECK_HISTORICAL
    carried = v.pointer["historical_v7_4_authority"]["carried_dispositions"]
    v.equal(
        check,
        "HISTORICAL_SCOPE_ALTERED",
        carried["scope"],
        HISTORICAL_SCOPE,
        "carried_dispositions.scope",
    )
    v.equal(
        check,
        "HISTORICAL_FINDING_REINTERPRETED_AS_V8",
        carried["reinterpreted_as_v8_constraint"],
        False,
        "carried_dispositions.reinterpreted_as_v8_constraint",
    )
    v.equal(
        check,
        "HISTORICAL_FINDING_CLOSED_BY_POINTER",
        carried["closed_or_remediated_by_this_pointer"],
        [],
        "carried_dispositions.closed_or_remediated_by_this_pointer",
    )
    findings = v1._lookup(predecessor, ("open_findings_and_limitations", "findings"))
    acc_n1 = next(
        (
            f for f in (findings if isinstance(findings, list) else [])
            if isinstance(f, Mapping) and f.get("id") == "ACC-N1"
        ),
        {},
    )
    u01 = v1._lookup(predecessor, ("open_findings_and_limitations", "unresolved_register", "U-01"))
    u01 = u01 if isinstance(u01, Mapping) else {}
    for what, actual, expected in (
        ("ACC-N1.severity", carried["ACC-N1"]["severity"], acc_n1.get("severity", _MISSING)),
        (
            "ACC-N1.disposition",
            carried["ACC-N1"]["disposition"],
            acc_n1.get("disposition", _MISSING),
        ),
        ("ACC-N1.closed", carried["ACC-N1"]["closed"], acc_n1.get("closed", _MISSING)),
        ("U-01.status", carried["U-01"]["status"], u01.get("status", _MISSING)),
        (
            "U-01.must_be_frozen_before",
            carried["U-01"]["must_be_frozen_before"],
            u01.get("must_be_frozen_before", _MISSING),
        ),
        (
            "A2.a2_variable_floor_status",
            carried["A2"]["a2_variable_floor_status"],
            v1._lookup(predecessor, ("non_authorization_boundaries", "a2_variable_floor_status")),
        ),
    ):
        where = f"carried_dispositions.{what}"
        v.equal(check, "HISTORICAL_DISPOSITION_ALTERED", actual, expected, where)
    v.equal(
        check,
        "HISTORICAL_DISPOSITION_ALTERED",
        carried["ACC-N1"]["closed"],
        False,
        "ACC-N1 stays open",
    )


def _check_boundaries(v: _Verification) -> None:
    v.start(CHECK_BOUNDARIES)
    check = CHECK_BOUNDARIES
    boundaries = v.pointer["non_authorization_boundaries"]
    v.equal(
        check,
        "POINTER_CLAIMS_EXECUTION_AUTHORITY",
        boundaries["pointer_grants_execution_authority"],
        False,
        "non_authorization_boundaries.pointer_grants_execution_authority",
    )
    v.equal(check, "POINTER_CLAIMS_AUTHORIZATION", boundaries["authorizes"], [], "authorizes")
    listed = set(boundaries["not_authorized_by_this_pointer"])
    for item in REQUIRED_NON_AUTHORIZATIONS:
        v.require(
            check,
            "NON_AUTHORIZATION_BOUNDARY_DROPPED",
            item in listed,
            f"not_authorized_by_this_pointer lacks {item}",
        )
    contract = v.pointer["activation_contract"]
    for key, expected in ACTIVATION_CONTRACT.items():
        v.equal(
            check,
            "ACTIVATION_CONTRACT_INVALID",
            contract.get(key, _MISSING),
            expected,
            f"activation_contract.{key}",
        )
    validation = v.pointer["validation_contract"]
    for key, expected in (
        ("verifier_module", VERIFIER_MODULE_RELATIVE_PATH),
        ("verifier_interface_version", INTERFACE_VERSION),
        ("required_checks", list(CHECK_IDS)),
    ):
        v.equal(
            check,
            "VALIDATION_CONTRACT_MISMATCH",
            validation[key],
            expected,
            f"validation_contract.{key}",
        )
    v.equal(
        check,
        "VALIDATION_CONTRACT_MISMATCH",
        v.value(("pointer_identity", "proposed_canonical_path")),
        CANONICAL_POINTER_RELATIVE_PATH,
        "pointer_identity.proposed_canonical_path",
    )


def _check_historical_route(v: _Verification) -> None:
    """Run the historical v7.4 route: v1, candidate mode, on pointer R2."""

    v.start(CHECK_HISTORICAL_ROUTE)
    pointer_path = v.value((*_ROUTE, "pointer_path"))
    result = v1.verify_candidate_pointer(
        v.root, pointer_path, results_policy=v1.RESULTS_POLICY_NONE
    )
    v.info["historical_v7_4_route"] = {
        "verifier_module": result["verifier"]["module"],
        "interface_version": result["verifier"]["interface_version"],
        "mode": result["mode"],
        "pointer_path": result["pointer_path"],
        "results_policy": result["results_policy"],
        "verdict": result["verdict"],
        "failure_codes": result["failure_codes"],
        "checks": result["checks"],
    }
    v.require(
        CHECK_HISTORICAL_ROUTE,
        "HISTORICAL_V7_4_ROUTE_FAILS_CLOSED",
        result["verdict"] == v1.VERDICT_CANDIDATE_CONSISTENT,
        f"v1 candidate verification of {pointer_path}: {result['failure_codes']}",
    )


def _check_activation(v: _Verification, git_ok: bool) -> None:
    """Canonical mode: v1's activation basis, plus the v8 activation binding."""

    v1._check_activation(v, git_ok)
    activation = v.pointer["activation_basis"]
    if activation["status"] != v1.ACTIVATION_ACCEPTED_PUBLISHED:
        return
    artifacts = [activation[role] for role in v1.ACTIVATION_ROLES]
    if not all(isinstance(a, Mapping) for a in artifacts):
        return
    payload = {k: x for k, x in v.pointer.items() if k not in v1.ENVELOPE_KEYS}
    bound = {x["path"] for _l, _k, x, _p in v1._walk(payload) if v1._is_file_identity(x)}
    v.require(
        CHECK_ACTIVATION,
        "ACTIVATION_ROLE_ALIASED",
        not any(a["path"] in bound for a in artifacts),
        "an activation artifact may not be a record the payload already binds",
    )
    closure = v1._load_json(
        v, CHECK_ACTIVATION, activation["acceptance_closure"]["path"], "acceptance_closure"
    )
    expected = {
        "framework_formal_name": FRAMEWORK_FORMAL_NAME,
        "framework_document_sha256": v.value((*_METHODOLOGY, "document", "sha256")),
        "registry_formal_name": REGISTRY_FORMAL_NAME,
        "registry_component_sha256": [
            v.value((*_BASE, "document", "sha256")),
            v.value((*_DELTA, "document", "sha256")),
        ],
        "gate3_acceptance_record_sha256": v.value(
            (*_METHODOLOGY, "gate3_acceptance_record", "sha256")
        ),
        "predecessor_pointer_id": v.value((*_PREDECESSOR, "pointer_id")),
    }
    v.equal(
        CHECK_ACTIVATION,
        "ACTIVATION_DOES_NOT_ACCEPT_V8_METHODOLOGY",
        v1._lookup(closure, (ACTIVATION_CONTRACT["closure_activation_binding_key"],)),
        expected,
        f"acceptance_closure.{ACTIVATION_CONTRACT['closure_activation_binding_key']}",
    )


def _verify(root: Path, pointer: Any, *, mode: str, pointer_relative_path: str) -> dict[str, Any]:
    """Verify an already-parsed pointer object.  Read-only; never raises."""

    v = _Verification(root, mode, pointer_relative_path)
    if mode == MODE_CANDIDATE:
        v.checks[CHECK_ACTIVATION] = STATUS_NOT_APPLICABLE
    if not _check_schema(v, pointer):
        return v.result()
    v.pointer = pointer
    v.info["pointer_payload_digest"] = v1.pointer_payload_digest(pointer)
    v1._guarded(v, CHECK_LIFECYCLE, lambda: v1._check_lifecycle(v))
    v1._guarded(v, CHECK_PATHS, lambda: v1._check_paths(v))
    git_ok = False
    try:
        git_ok = _check_git(v)
    except Exception as error:  # fail closed, never crash open
        v.fail(CHECK_GIT, "VERIFIER_INTERNAL_ERROR", f"{type(error).__name__}: {error}")
    loaded = v1._load_json(
        v, CHECK_HISTORICAL, v.value((*_PREDECESSOR, "audited_candidate", "path")), "predecessor"
    )
    v.predecessor = loaded if isinstance(loaded, Mapping) else None
    later = [
        (CHECK_FILES, lambda: v1._check_files(v, git_ok)),
        (CHECK_HISTORICAL_OBJECTS, lambda: _check_historical_objects(v, git_ok)),
        (CHECK_V8_AUTHORITY, lambda: _check_v8_authority(v)),
        (CHECK_V8_STAGES, lambda: _check_v8_stages(v)),
        (CHECK_ROLES, lambda: _check_roles(v)),
        (CHECK_HISTORICAL, lambda: _check_historical(v)),
        (CHECK_BOUNDARIES, lambda: _check_boundaries(v)),
        (CHECK_V8_RESULTS, lambda: _check_v8_results(v)),
        (CHECK_HISTORICAL_ROUTE, lambda: _check_historical_route(v)),
    ]
    if mode == MODE_CANONICAL:
        later.append((CHECK_ACTIVATION, lambda: _check_activation(v, git_ok)))
    for check, step in later:
        v1._guarded(v, check, step)
    return v.result()


def _unreadable(root: Path, mode: str, relative: str, code: str) -> dict[str, Any]:
    v = _Verification(root, mode, relative)
    v.start(CHECK_SCHEMA)
    v.fail(CHECK_SCHEMA, code, f"{relative} could not be read as a pointer")
    return v.result()


def verify_candidate_pointer(repo_root: Path | str, pointer_relative_path: str) -> dict[str, Any]:
    """Report whether a schema-v2 candidate pointer is internally consistent.

    A passing result is never an acceptance or an activation:
    ``is_current_authority`` is always ``False`` in this mode.
    """

    root = Path(repo_root).resolve()
    pointer, digest, code = v1._read_pointer(root, pointer_relative_path)
    if code is not None:
        return _unreadable(root, MODE_CANDIDATE, pointer_relative_path, code)
    result = _verify(
        root, pointer, mode=MODE_CANDIDATE, pointer_relative_path=pointer_relative_path
    )
    result["pointer_sha256"] = digest
    return result


def verify_canonical_pointer(repo_root: Path | str) -> dict[str, Any]:
    """Verify the canonical pointer as schema v2, and only the canonical path.

    While the canonical pointer is schema v1 (v7.4 current), this reports
    ``FAIL_CLOSED`` with ``SCHEMA_VERSION_NOT_V2``; v1 verifies it.
    """

    root = Path(repo_root).resolve()
    relative = CANONICAL_POINTER_RELATIVE_PATH
    pointer, digest, code = v1._read_pointer(root, relative)
    if code is not None:
        code = "CANONICAL_POINTER_ABSENT" if code == "POINTER_ABSENT" else code
        return _unreadable(root, MODE_CANONICAL, relative, code)
    result = _verify(root, pointer, mode=MODE_CANONICAL, pointer_relative_path=relative)
    result["pointer_sha256"] = digest
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only verifier for schema-v2 Iris Thesis current-mainline pointers."
    )
    parser.add_argument("mode", choices=("candidate", "canonical"))
    parser.add_argument("--pointer", help="candidate pointer path (candidate mode only)")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    arguments = parser.parse_args(argv)
    if arguments.mode == "candidate":
        if not arguments.pointer:
            parser.error("candidate mode requires --pointer")
        result = verify_candidate_pointer(arguments.repo_root, arguments.pointer)
    else:
        if arguments.pointer:
            parser.error("canonical mode reads only the canonical path")
        result = verify_canonical_pointer(arguments.repo_root)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0 if result["verdict"] != VERDICT_FAIL_CLOSED else 2


if __name__ == "__main__":
    raise SystemExit(main())
