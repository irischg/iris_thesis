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

import fnmatch
import hashlib
import io
import json
import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.production_input_authority_v7_3 import sha256_file


#: Candidate R5 (design observation ``N-R5D-05``): this reported label still
#: named the auth-mechanism candidate R2 although the overlay contract had since
#: advanced through the preflight-authorization-guard candidates.  It is a
#: reported label only, never an acceptance criterion.
#:
#: Current Full81 Production Generation G1 candidate R1: the overlay gained one
#: additive generation, its own content contract and its predeclared governance
#: paths, so the label names that candidate.
LIFECYCLE_MODULE_VERSION = (
    "v7.4-production-authority-accepted-lifecycle-overlay-2026-10-07-"
    "current-full81-production-generation-g1-candidate-r1"
)

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
    #: Generation-independent artifact-type suffix.  The full ``artifact_type``
    #: is ``<generation artifact-type prefix> + <suffix>``, so a role record of
    #: one authority generation is detectably the wrong TYPE in another, not
    #: merely the wrong schema.
    artifact_type_suffix: str
    schema_version: str
    #: Generation-independent schema suffix.  The full ``schema_version`` is
    #: ``<generation schema prefix> + <suffix>``, which is what makes a role
    #: record of one authority generation detectably unusable in another.
    schema_suffix: str
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

    def for_generation_namespace(
        self, artifact_type_prefix: str, schema_prefix: str
    ) -> "RoleContract":
        """This contract re-expressed in another generation's namespace."""

        return RoleContract(
            role=self.role,
            artifact_type=artifact_type_prefix + self.artifact_type_suffix,
            artifact_type_suffix=self.artifact_type_suffix,
            schema_version=schema_prefix + self.schema_suffix,
            schema_suffix=self.schema_suffix,
            binds_roles=self.binds_roles,
            declares_candidate_manifest=self.declares_candidate_manifest,
            required_fields=self.required_fields,
        )


#: The accepted U-06 R3 namespace prefixes.  Unchanged values: the accepted
#: role ``artifact_type`` and ``schema_version`` strings are reproduced exactly.
_ARTIFACT_TYPE_PREFIX = "U06_"
_SCHEMA_PREFIX = "iris-thesis-u06-r3-"

ROLE_CONTRACT_TEMPLATES: Mapping[str, RoleContract] = {
    "implementation_candidate": RoleContract(
        role="implementation_candidate",
        artifact_type="U06_IMPLEMENTATION_CANDIDATE",
        artifact_type_suffix="IMPLEMENTATION_CANDIDATE",
        schema_version=_SCHEMA_PREFIX + "implementation-candidate-v1",
        schema_suffix="implementation-candidate-v1",
        binds_roles=(),
        declares_candidate_manifest=False,
        required_fields=("candidate_checkpoint", "implementation_identity_digest"),
    ),
    "independent_audit_pass": RoleContract(
        role="independent_audit_pass",
        artifact_type="U06_INDEPENDENT_AUDIT_PASS",
        artifact_type_suffix="INDEPENDENT_AUDIT_PASS",
        schema_version=_SCHEMA_PREFIX + "independent-audit-pass-v1",
        schema_suffix="independent-audit-pass-v1",
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
        artifact_type_suffix="ACCEPTANCE_CLOSURE",
        schema_version=_SCHEMA_PREFIX + "acceptance-closure-v1",
        schema_suffix="acceptance-closure-v1",
        binds_roles=("implementation_candidate", "independent_audit_pass"),
        declares_candidate_manifest=True,
        required_fields=("acceptance_status", "audit_publication_commit"),
    ),
    "acceptance_manifest": RoleContract(
        role="acceptance_manifest",
        artifact_type="U06_ACCEPTANCE_MANIFEST",
        artifact_type_suffix="ACCEPTANCE_MANIFEST",
        schema_version=_SCHEMA_PREFIX + "acceptance-manifest-v1",
        schema_suffix="acceptance-manifest-v1",
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
        artifact_type_suffix="PRODUCTION_AUTHORITY_RE_FREEZE",
        schema_version=_SCHEMA_PREFIX + "production-authority-re-freeze-v1",
        schema_suffix="production-authority-re-freeze-v1",
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

#: Role order is the lifecycle order; later roles bind earlier ones.  Generation
#: independent: every generation uses the same five roles in the same order.
REQUIRED_ACCEPTED_ROLES: tuple[str, ...] = tuple(ROLE_CONTRACT_TEMPLATES)

#: The accepted U-06 R3 generation role contracts, retained under their accepted
#: name.  ``AuthorityGeneration.role_contracts`` supplies any other generation.
ROLE_CONTRACTS: Mapping[str, RoleContract] = {
    role: contract.for_generation_namespace(_ARTIFACT_TYPE_PREFIX, _SCHEMA_PREFIX)
    for role, contract in ROLE_CONTRACT_TEMPLATES.items()
}

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
# H-01: production-authority GENERATIONS
# ---------------------------------------------------------------------------
#
# Finding ``H-01`` (CRITICAL) against Candidate R1: this overlay was
# single-generation and hard-bound to U-06 R3, so once accepted implementation
# bytes changed there was no lawful path by which any successor could be
# audited, accepted, or re-frozen.  Every lifecycle role rejected a successor
# lineage with ``U06_LINEAGE_MISMATCH``, the implementation-candidate role was
# path-pinned to the R3 alignment manifest, and the single accepted-lifecycle
# record slot was already occupied by a committed record declaring the
# predecessor digest.  Reaching ``FROZEN`` for changed bytes would have
# required MUTATING accepted R3 artifacts.
#
# The remedy follows the repository own verified R2 -> R3 precedent, in which
# the overlay advanced its generation namespace (new lineage, new candidate,
# new schema prefix, new accepted-lifecycle record directory) while every
# predecessor artifact stayed byte-identical.  That precedent is now
# generalised rather than repeated by hand: a generation is a value, the
# registry holds every generation ever declared, and exactly one is current.
#
# Advancing to a further generation therefore needs one new
# :class:`AuthorityGeneration` plus a change of :data:`CURRENT_GENERATION` - it
# never needs a validator rewrite, and it never touches a predecessor artifact.
#
# No digest and no commit is hard-coded here.  Predecessor identity is read
# from the predecessor own on-disk record and from live Git, so this module
# still contains zero 64-hex literals.


@dataclass(frozen=True)
class AuthorityGeneration:
    """One production-authority lifecycle generation.

    A generation owns its lineage identity, its candidate identity, the fixed
    candidate artifacts an acceptance must be about, its accepted-lifecycle
    record slot, and its schema namespace.  Two generations can never satisfy
    each other roles: the lineage, the candidate id, the candidate paths and
    every role ``schema_version`` all differ.
    """

    generation_id: str
    lineage_id: str
    candidate_id: str
    candidate_checkpoint_path: str
    candidate_manifest_path: str
    accepted_lifecycle_record_path: str
    artifact_type_prefix: str
    schema_prefix: str
    #: Candidate ids of failed/superseded candidates in this lineage, which a
    #: role record may never name.
    superseded_candidate_ids: tuple[str, ...]
    #: Candidate artifact paths that may never fill roles 2-5 of this
    #: generation.
    candidate_artifact_paths: tuple[str, ...]
    #: The accepted generation this one succeeds, or ``None`` for the first.
    predecessor_generation_id: str | None
    predecessor_lineage_id: str | None
    predecessor_accepted_lifecycle_record_path: str | None
    disposition: str
    #: The independent-audit state of THIS generation's OWN current candidate
    #: (the candidate named by :attr:`candidate_id`).
    #:
    #: Candidate R3 remediation of independent-audit blocker ``R2-AUD-03``
    #: (MAJOR / BLOCKING).  The pre-acceptance audit state used to come from a
    #: single module-level constant describing the *historical U-06 alignment*
    #: candidate history, so the active generation's candidate audit state was
    #: reported as that unrelated history.  Audit state is per-generation data,
    #: so it is declared per generation here and never shared between them.
    #:
    #: It defaults to the only state a new candidate can truthfully have.  A
    #: generation may never declare ``PASS`` for itself: a real ``PASS`` is
    #: proved by a published accepted-lifecycle record, which the role
    #: validators check independently.  The two values below are set only
    #: because each predecessor's on-disk accepted record already declares
    #: ``u06_independent_audit_status = PASS``.
    candidate_audit_state: str = "NOT_YET_PERFORMED"
    #: The CONTENT contract this generation's implementation-candidate manifest
    #: must satisfy, beyond the shared role envelope.
    #:
    #: Candidate R5 remediation of independent-audit blocker ``R4-AUD-01``
    #: (MAJOR / BLOCKING): the implementation-candidate role was validated by
    #: its envelope only, so a manifest could carry stale, self-referential or
    #: unverified identity assertions and still fill the role.  A generation
    #: that names a contract here has its candidate manifest validated by
    #: :func:`validate_candidate_manifest_identity_contract` on the production
    #: lifecycle path.
    #:
    #: ``None`` means "accepted under the envelope-only contract".  It is the
    #: value every HISTORICAL generation was accepted with, so their accepted
    #: records keep being judged by the contract they were written under and
    #: nothing is reinterpreted retroactively.  An import-time guard below
    #: refuses ``None`` for the CURRENT generation.
    candidate_manifest_contract: str | None = None
    #: The candidate's machine-readable change / reproducibility ledger.
    #:
    #: Candidate R6 addition.  The ledger is finalized BEFORE the checkpoint
    #: and the manifest, so the manifest can lawfully bind its raw SHA-256
    #: (obligation ``C9``) and the contract validates every identity the
    #: ledger states.  ``None`` for every generation accepted before ledgers
    #: existed, so none of them is re-judged retroactively.
    candidate_change_ledger_path: str | None = None
    #: The exact paths roles 2-5 of this generation must be published at,
    #: declared BEFORE the candidate is frozen, as ``(role, path)`` pairs.
    #:
    #: Current Full81 Production Generation G1 addition.  The R8 acceptance
    #: authored its four role records at paths no source declared, so they
    #: entered the raw-byte consumer universe only after acceptance and had no
    #: exact-path EOL rule.  A generation that predeclares its role paths has
    #: every future governance record protected the moment it is authored, and
    #: its lifecycle validator refuses a role filled at any other path.
    #: ``None`` for every historical generation, so none is re-judged.
    predeclared_role_record_paths: tuple[tuple[str, str], ...] | None = None

    @property
    def role_record_path_map(self) -> dict[str, str] | None:
        """Predeclared role -> path for roles 2-5, or ``None`` if undeclared."""

        if self.predeclared_role_record_paths is None:
            return None
        return dict(self.predeclared_role_record_paths)

    @property
    def role_contracts(self) -> Mapping[str, RoleContract]:
        """This generation five role contracts, in lifecycle order."""

        return {
            role: contract.for_generation_namespace(
                self.artifact_type_prefix, self.schema_prefix
            )
            for role, contract in ROLE_CONTRACT_TEMPLATES.items()
        }

    @property
    def lifecycle_record_artifact_type(self) -> str:
        return self.artifact_type_prefix + "ACCEPTED_LIFECYCLE"

    @property
    def lifecycle_record_schema_version(self) -> str:
        return self.schema_prefix + "accepted-lifecycle-v1"

    def as_dict(self) -> dict[str, Any]:
        return {
            "generation_id": self.generation_id,
            "lineage_id": self.lineage_id,
            "candidate_id": self.candidate_id,
            "candidate_checkpoint_path": self.candidate_checkpoint_path,
            "candidate_manifest_path": self.candidate_manifest_path,
            "accepted_lifecycle_record_path": self.accepted_lifecycle_record_path,
            "artifact_type_prefix": self.artifact_type_prefix,
            "schema_prefix": self.schema_prefix,
            "lifecycle_record_artifact_type": (
                self.lifecycle_record_artifact_type
            ),
            "lifecycle_record_schema_version": (
                self.lifecycle_record_schema_version
            ),
            "role_artifact_types": {
                role: c.artifact_type for role, c in self.role_contracts.items()
            },
            "role_schema_versions": {
                role: c.schema_version for role, c in self.role_contracts.items()
            },
            "superseded_candidate_ids": list(self.superseded_candidate_ids),
            "predecessor_generation_id": self.predecessor_generation_id,
            "predecessor_lineage_id": self.predecessor_lineage_id,
            "predecessor_accepted_lifecycle_record_path": (
                self.predecessor_accepted_lifecycle_record_path
            ),
            "disposition": self.disposition,
            "candidate_audit_state": self.candidate_audit_state,
            "candidate_manifest_contract": self.candidate_manifest_contract,
            "candidate_change_ledger_path": self.candidate_change_ledger_path,
            "predeclared_role_record_paths": self.role_record_path_map,
        }


#: Generation 1 - U-06 R3.  ACCEPTED, FROZEN, and now an immutable historical
#: predecessor.  Its values are byte-for-byte the ones it was accepted with;
#: nothing here is rewritten.
U06_R3_GENERATION = AuthorityGeneration(
    generation_id="U06_V7_4_PRODUCTION_AUTHORITY_R3",
    lineage_id=LINEAGE_ID,
    candidate_id=R3_CANDIDATE_ID,
    candidate_checkpoint_path=R3_CANDIDATE_CHECKPOINT_PATH,
    candidate_manifest_path=R3_CANDIDATE_MANIFEST_PATH,
    accepted_lifecycle_record_path=(
        ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH.as_posix()
    ),
    artifact_type_prefix=_ARTIFACT_TYPE_PREFIX,
    schema_prefix=_SCHEMA_PREFIX,
    superseded_candidate_ids=SUPERSEDED_CANDIDATE_IDS,
    candidate_artifact_paths=CANDIDATE_ARTIFACT_PATHS,
    predecessor_generation_id=None,
    predecessor_lineage_id=None,
    predecessor_accepted_lifecycle_record_path=None,
    disposition="IMMUTABLE_HISTORICAL_ACCEPTED_PREDECESSOR_GENERATION",
    #: Verified against this generation's own published accepted-lifecycle
    #: record, which declares ``u06_independent_audit_status = PASS``.
    candidate_audit_state="PASS",
)

#: Generation 2 - the Main Full81 authorization-mechanism successor.
#: ``MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1`` FAILED its read-only
#: audit on ``H-01`` / ``H-02`` and is on the rejection list below, so it can
#: never be revived.  Candidate R2 is the bounded remediation and is itself a
#: CANDIDATE: no artifact of this generation exists yet.
FULL81_AUTHORIZATION_MECHANISM_R2_ARTIFACT_TYPE_PREFIX = (
    "FULL81_AUTH_MECH_R2_"
)
FULL81_AUTHORIZATION_MECHANISM_R2_SCHEMA_PREFIX = "iris-thesis-full81-auth-mech-r2-"

FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_authorization_mechanism_candidate_r2_2026-10-02.md"
)
FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_authorization_mechanism_candidate_r2_2026-10-02/"
    "authorization_mechanism_manifest.json"
)
FULL81_AUTHORIZATION_MECHANISM_R2_ACCEPTED_LIFECYCLE_RECORD_PATH = (
    "results/provenance/"
    "main_full81_authorization_mechanism_accepted_lifecycle_r2/"
    "accepted_lifecycle_record.json"
)

#: Candidate R1 provenance, retained as immutable failed-candidate evidence and
#: barred from filling any role of this generation.
FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_authorization_mechanism_candidate_r1_2026-10-02.md"
)
FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_authorization_mechanism_candidate_r1_2026-10-02/"
    "authorization_mechanism_manifest.json"
)

FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION = AuthorityGeneration(
    generation_id="MAIN_FULL81_AUTHORIZATION_MECHANISM_R2",
    lineage_id="MAIN_FULL81_AUTHORIZATION_MECHANISM_R1",
    candidate_id="MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2",
    candidate_checkpoint_path=(
        FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_CHECKPOINT_PATH
    ),
    candidate_manifest_path=(
        FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_MANIFEST_PATH
    ),
    accepted_lifecycle_record_path=(
        FULL81_AUTHORIZATION_MECHANISM_R2_ACCEPTED_LIFECYCLE_RECORD_PATH
    ),
    artifact_type_prefix=(
        FULL81_AUTHORIZATION_MECHANISM_R2_ARTIFACT_TYPE_PREFIX
    ),
    schema_prefix=FULL81_AUTHORIZATION_MECHANISM_R2_SCHEMA_PREFIX,
    superseded_candidate_ids=(
        "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1",
    ),
    candidate_artifact_paths=(
        FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_CHECKPOINT_PATH,
        FULL81_AUTHORIZATION_MECHANISM_R1_CANDIDATE_MANIFEST_PATH,
        FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_CHECKPOINT_PATH,
        FULL81_AUTHORIZATION_MECHANISM_R2_CANDIDATE_MANIFEST_PATH,
    ),
    predecessor_generation_id=U06_R3_GENERATION.generation_id,
    predecessor_lineage_id=U06_R3_GENERATION.lineage_id,
    predecessor_accepted_lifecycle_record_path=(
        U06_R3_GENERATION.accepted_lifecycle_record_path
    ),
    disposition="CURRENT_GENERATION_CANDIDATE_NOT_ACCEPTED_NOT_FROZEN",
    #: Verified against this generation's own published accepted-lifecycle
    #: record, which declares ``u06_independent_audit_status = PASS``.
    candidate_audit_state="PASS",
)

#: Generation 3 - the Main Full81 no-solve preflight authorization-guard
#: successor.  Independent audit finding ``N-04`` (MAJOR) established that
#: ``scripts/21d_preflight_v7_3_final81_successor.py`` *resolved and reported*
#: the Main Full81 scope authorization without ever *requiring* it, so the
#: zero-solve entrypoint was fail-open against its own prerequisite.
#:
#: Remediating that changes runner bytes, and the runner is one of the accepted
#: implementation-identity paths, so the accepted implementation digest changes
#: with it.  Generation 2's single accepted-lifecycle record slot is already
#: occupied by a committed record declaring the PREDECESSOR digest; reaching
#: ``FROZEN`` for the changed bytes inside generation 2 would therefore require
#: MUTATING an accepted artifact, which is forbidden.
#:
#: This generation is consequently additive, exactly as the generalised R2 -> R3
#: precedent above prescribes: new lineage, new candidate, new schema namespace,
#: new accepted-lifecycle slot, and every predecessor generation value left
#: byte-identical.  It is a CANDIDATE: no artifact of this generation exists
#: beyond its own implementation-candidate manifest, nothing is accepted,
#: nothing is frozen, and no Main Full81 authorization exists for it.
#:
#: Candidate iteration R1 -> R2.  Candidate R1 PASSED its fresh independent
#: read-only audit (``N-04`` and ``N-05`` both CLOSED / CORRECTION_VERIFIED) but
#: its candidate-publication pass STOPPED: two of its eight audited artifacts
#: were CRLF in the working tree while the repository runs ``core.autocrlf=true``
#: with no ``.gitattributes``, so Git's clean filter would have normalised them
#: and committed bytes other than the audited bytes.  That is finding ``I-04``
#: (MAJOR / OPEN / CARRIED) manifesting as a publication blocker - not a defect
#: in the ``N-04``/``N-05`` guard logic.
#:
#: Candidate R2 therefore advances the CANDIDATE within this SAME generation and
#: lineage, exactly as generation 2 advanced its own candidate R1 -> R2: this
#: generation's single accepted-lifecycle record slot does not exist on disk, so
#: nothing accepted or frozen is mutated by the advance, and the additive-new-
#: generation requirement that applied to generation 2 does not apply here.
#: Candidate R1 is retained as immutable superseded provenance and barred from
#: filling any role of this generation.
FULL81_PREFLIGHT_AUTH_GUARD_R1_ARTIFACT_TYPE_PREFIX = (
    "FULL81_PREFLIGHT_AUTH_GUARD_R1_"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_SCHEMA_PREFIX = (
    "iris-thesis-full81-preflight-auth-guard-r1-"
)

#: Candidate R1 provenance, retained as immutable superseded-candidate evidence
#: and barred from filling any role of this generation.  Its publication STOPPED
#: on the ``I-04`` clean-filter incompatibility; it was never accepted and never
#: committed.  These two paths are NOT rewritten: the exact audited R1 bytes are
#: additionally preserved verbatim under
#: ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r1_publication_stop_2026-10-04/``.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r1_2026-10-03.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r1_2026-10-03/"
    "preflight_authorization_guard_manifest.json"
)

#: Candidate R2: the current candidate of this generation.  Publication-
#: compatible successor of candidate R1; same generation, same lineage, same
#: accepted-lifecycle slot, new candidate identity and new candidate artifacts.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R2_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r2_2026-10-04.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R2_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r2_2026-10-04/"
    "preflight_authorization_guard_manifest.json"
)
#: Candidate R3.  Candidate R2's fresh independent audit returned FAIL / NO-GO
#: on ``R2-AUD-01`` / ``R2-AUD-02`` / ``R2-AUD-03``, so candidate R2 is a
#: REJECTED immutable historical candidate - not merely superseded - and its
#: namespace may never be reused.  Candidate R3 was the bounded
#: provenance/governance remediation of exactly those three blockers.
#:
#: Candidate R3's own fresh independent audit then returned FAIL / NO-GO on
#: ``R3-AUD-01`` (stale/cyclic checkpoint-manifest binding), ``R3-AUD-02``
#: (incomplete EOL authority coverage), ``R3-AUD-03`` (fail-open bundle
#: verifier), ``R2-AUD-03`` (stale historical ownership in the current register
#: entry) and ``R3-AUD-04`` (predecessor premises in the validation surface).
#: Candidate R3 is therefore ALSO a REJECTED immutable historical candidate.
#: Its exact audited bytes are preserved verbatim under
#: ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r3_audit_stop_2026-10-05/``
#: and the two candidate R3 artifact paths below are NOT rewritten.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R3_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r3_2026-10-04.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R3_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r3_2026-10-04/"
    "preflight_authorization_guard_manifest.json"
)
#: Candidate R4: the bounded remediation of the five Candidate R3 blockers
#: listed above.
#:
#: Candidate R4's own fresh independent read-only audit returned FAIL / NO-GO on
#: ``R4-AUD-01`` (MAJOR / BLOCKING): its manifest froze a snapshot of the LIVE
#: durable-publication report, so it carried stale ``live_sha256`` values for
#: the candidate checkpoint and for the manifest's OWN path while asserting
#: ``live_content_matches_canonical = true`` and
#: ``placeholder_or_stale_sha_used = false``, and no production validator read
#: those fields.  Candidate R4 is therefore a REJECTED immutable historical
#: candidate.  Its exact audited bytes are preserved verbatim under
#: ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r4_audit_stop_2026-10-05/``
#: and the two candidate R4 artifact paths below are NOT rewritten.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r4_2026-10-05.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r4_2026-10-05/"
    "preflight_authorization_guard_manifest.json"
)
#: Candidate R5: the bounded remediation of ``R4-AUD-01``.
#:
#: Candidate R5's own fresh independent read-only audit returned FAIL / NO-GO
#: on ``R5-AUD-01`` (CRITICAL): the checkpoint identity guard proved only that
#: each raw digest in the checkpoint occurred SOMEWHERE in the manifest, not
#: that the role the checkpoint gave it was the role the manifest's owning
#: obligation gives it, so a lawful implementation digest under a "Manifest
#: SHA-256" label passed; and on ``R5-AUD-02`` (MAJOR): a test-suite
#: disposable-write helper did not keep its write target inside the disposable
#: root.  Candidate R5 is therefore a REJECTED immutable historical candidate.
#: Its exact audited bytes are preserved verbatim under ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r5_audit_stop_2026-10-05/``
#: and the two candidate R5 artifact paths below are NOT rewritten.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r5_2026-10-05.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r5_2026-10-05/"
    "preflight_authorization_guard_manifest.json"
)
#: Candidate R6: the bounded remediation of ``R5-AUD-01`` and ``R5-AUD-02``.
#:
#: Candidate R6's own fresh independent read-only audit returned FAIL / NO-GO
#: on ``R6-AUD-01`` (CRITICAL): in GATE mode the preservation-package and
#: predecessor identities were accepted STRUCTURALLY (never value-checked), so
#: the R5 STOP archive and index digests swapped between their roles - with the
#: checkpoint claims rebound to the swapped values - still passed; and on
#: ``R6-AUD-02`` (MAJOR): the test-suite write guard missed unsafe writer
#: patterns and disposable teardown could delete outside its root through a
#: junction.  Candidate R6 is therefore a REJECTED immutable historical
#: candidate.  Its exact audited bytes are preserved verbatim under
#: ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r6_audit_stop_2026-10-05/``
#: and the three candidate R6 artifact paths below are NOT rewritten.
#:
#: The same-generation advance R5 -> R6 was lawful for the same primary reason
#: every earlier candidate advance was: this generation's single
#: accepted-lifecycle record slot
#: (:data:`FULL81_PREFLIGHT_AUTH_GUARD_R1_ACCEPTED_LIFECYCLE_RECORD_PATH`) does
#: not exist on disk, so nothing accepted or frozen is mutated by the advance,
#: and every predecessor candidate artifact stays byte-identical.  That
#: precondition is not asserted in prose: it is re-derived mechanically by
#: :func:`same_generation_advance_lawfulness`.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r6_2026-10-05.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r6_2026-10-05/"
    "preflight_authorization_guard_manifest.json"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHANGE_LEDGER_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r6_2026-10-05/"
    "candidate_change_ledger.json"
)
#: Candidate R7: the remediation of the ``R6-AUD-01`` and ``R6-AUD-02`` defect
#: CLASSES (not their examples).
#:
#: Candidate R7's own fresh independent read-only audit returned FAIL / NO-GO
#: on ``R7-AUD-01`` (CRITICAL): the production GATE's historical expected
#: values were still candidate-controlled.  Its pinned historical role table
#: lived in candidate source and its implementation identity was
#: recomputable, so four independently constructed rebinding attacks - two
#: roles swapped, a three-role cycle, one lawful historical digest replaced
#: by another, the authority-bundle digest placed in a historical role -
#: restored GATE PASS after every candidate-controlled identity was
#: recomputed.  Candidate R7 is therefore a REJECTED immutable historical
#: candidate.  Its exact audited bytes are preserved verbatim under
#: ``results/provenance/
#: main_full81_preflight_authorization_guard_candidate_r7_audit_stop_2026-10-06/``,
#: that preservation is bound by the independently accepted R7 Preservation
#: Authority Binding, and the three candidate R7 artifact paths below are
#: NOT rewritten.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r7_2026-10-06.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r7_2026-10-06/"
    "preflight_authorization_guard_manifest.json"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHANGE_LEDGER_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r7_2026-10-06/"
    "candidate_change_ledger.json"
)
#: Candidate R8: the current candidate of this generation, and the bounded
#: repair of the ``R6-AUD-01`` defect class as ``R7-AUD-01`` exposed it - the
#: GATE's historical semantic truth is derived from externally authenticated
#: evidence (contract V4), never from candidate-controlled material.  Same
#: generation, same lineage, same accepted-lifecycle slot; the advance is
#: lawful for the reason re-derived by :func:`same_generation_advance_lawfulness`.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "main_full81_preflight_authorization_guard_candidate_r8_2026-10-06.md"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_MANIFEST_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r8_2026-10-06/"
    "preflight_authorization_guard_manifest.json"
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r8_2026-10-06/"
    "candidate_change_ledger.json"
)

#: ``R4-AUD-01`` remediation as first implemented by Candidate R5.  Retained as
#: the historical name of the contract the immutable R5 manifest declares; it
#: is no longer a contract any generation may use (see below).
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V1 = (
    "FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V1"
)

#: Candidate R6 contract.  V1 semantics are superseded, not extended: under V1
#: a checkpoint digest needed only to occur somewhere in the manifest
#: (``R5-AUD-01``).  Under V2 every checkpoint identity is a canonical claim
#: naming the exact manifest identity pointer that owns it, the candidate
#: change ledger is bound (``C9``) and validated, and the predecessor evidence
#: describes the immediate predecessor, Candidate R5.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V2 = (
    "FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V2"
)

#: Candidate R7 contract (``R6-AUD-01``).  V2 semantics are superseded, not
#: extended: under V2 an identity whose obligation was "not verified in this
#: mode" was accepted STRUCTURALLY, and a checkpoint claim only had to equal
#: the manifest's own value at its pointer - so a consistent permutation of
#: individually lawful digests between roles passed the GATE.  Under V3 there
#: is no structural acceptance in any mode: every identity pointer is resolved
#: through the closed-world semantic role schema
#: (:data:`CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS` /
#: :data:`CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS`) to ONE role whose
#: authoritative value is established independently of the manifest - live
#: bytes, the live implementation digest, an authority-bundle pin, or a
#: historical role identity pinned in the bundle - and a checkpoint claim must
#: equal that independently established value.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V3 = (
    "FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V3"
)

#: Candidate R8 contract (``R7-AUD-01``).  V3 semantics are superseded, not
#: extended: under V3 a historical identity was bound to a value pinned in
#: candidate source (the bundle's historical role table), which a
#: recomputing author could rewrite together with every other candidate
#: artifact.  Under V4 every historical identity - and the predecessor change
#: set - is bound, in every mode, to the value derived from the EXTERNAL
#: historical authority: the Git-frozen pre-R8 trust root, the accepted R7
#: Preservation Authority Binding it pins, and the authenticated R7
#: preservation package.  The bundle table is a diagnostic assertion of that
#: derivation, never a source of value, and there is no fallback to it.
FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4 = (
    "FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4"
)

#: Current Full81 Production Generation G1 contract.  V4 is NOT reused: it
#: hard-wires the predecessor to Candidate R7 and derives every historical
#: value from the R7 preservation chain, which is false for G1, whose
#: predecessor is the accepted R8 generation.  The G1 contract keeps every
#: generic closed-world live-identity obligation of V4 (checkpoint, runtime
#: implementation identity, bundle pins, durable declaration, change ledger,
#: forbidden own identity), drops the two R7-only historical obligations, and
#: adds separately classed validation and governance-authority identities
#: bound to live raw bytes.  See :func:`validate_g1_candidate_manifest_contract`.
G1_CANDIDATE_MANIFEST_CONTRACT = (
    "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_MANIFEST_CONTRACT_V1"
)

#: Every content contract this module can validate.  A generation naming any
#: other value is refused at import time rather than silently left unvalidated.
#: V1, V2 and V3 are deliberately absent: a manifest declaring any of them can
#: never satisfy the current contract.  Each known contract has its own
#: validator; :func:`validate_candidate_manifest_content_contract` dispatches by
#: the generation's declared contract and never lets one contract's validator
#: judge another contract's manifest.
KNOWN_CANDIDATE_MANIFEST_CONTRACTS: tuple[str, ...] = (
    FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4,
    G1_CANDIDATE_MANIFEST_CONTRACT,
)
FULL81_PREFLIGHT_AUTH_GUARD_R1_ACCEPTED_LIFECYCLE_RECORD_PATH = (
    "results/provenance/"
    "main_full81_preflight_authorization_guard_accepted_lifecycle_r1/"
    "accepted_lifecycle_record.json"
)

FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION = AuthorityGeneration(
    generation_id="MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1",
    lineage_id="MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1",
    candidate_id="MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8",
    candidate_checkpoint_path=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHECKPOINT_PATH
    ),
    candidate_manifest_path=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_MANIFEST_PATH
    ),
    accepted_lifecycle_record_path=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_ACCEPTED_LIFECYCLE_RECORD_PATH
    ),
    artifact_type_prefix=FULL81_PREFLIGHT_AUTH_GUARD_R1_ARTIFACT_TYPE_PREFIX,
    schema_prefix=FULL81_PREFLIGHT_AUTH_GUARD_R1_SCHEMA_PREFIX,
    #: Cumulative, exactly as generation 2 was: it listed both its own
    #: candidate R2 and the failed candidate R1 of its lineage. A successor
    #: generation inherits the whole prior candidate history rather than
    #: starting an empty bar list, because a role record of THIS generation may
    #: never name ANY predecessor candidate - failed or accepted-and-superseded.
    #: Derived from the predecessor generations so the list cannot drift.
    #:
    #: ``MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1`` is this
    #: generation's OWN superseded candidate, named explicitly for the same
    #: reason generation 2 named its own failed candidate R1: it is a candidate
    #: of this very lineage, so no predecessor-generation expression can derive
    #: it, and a role record of this generation may never name it.
    superseded_candidate_ids=(
        *FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.superseded_candidate_ids,
        FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.candidate_id,
        U06_R3_GENERATION.candidate_id,
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1",
        #: Candidate R2 of this very lineage. Its fresh independent audit
        #: returned FAIL / NO-GO, so it is additionally listed in
        #: ``REJECTED_CANDIDATE_IDS`` in the authorization mechanism. It is
        #: barred here for the same reason candidate R1 is: no role record of
        #: this generation may ever name a predecessor candidate.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2",
        #: Candidate R3 of this very lineage. Its fresh independent audit also
        #: returned FAIL / NO-GO (R3-AUD-01, R3-AUD-02, R3-AUD-03, R2-AUD-03,
        #: R3-AUD-04), so it is additionally listed in
        #: ``REJECTED_CANDIDATE_IDS`` in the authorization mechanism and barred
        #: here exactly as R1 and R2 are.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3",
        #: Candidate R4 of this very lineage. Its fresh independent audit
        #: returned FAIL / NO-GO on R4-AUD-01, so it is additionally listed in
        #: ``REJECTED_CANDIDATE_IDS`` in the authorization mechanism and barred
        #: here exactly as R1, R2 and R3 are.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
        #: Candidate R5 of this very lineage. Its fresh independent audit
        #: returned FAIL / NO-GO on R5-AUD-01 and R5-AUD-02, so it is
        #: additionally listed in ``REJECTED_CANDIDATE_IDS`` in the
        #: authorization mechanism and barred here exactly as R1-R4 are.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5",
        #: Candidate R6 of this very lineage. Its fresh independent audit
        #: returned FAIL / NO-GO on R6-AUD-01 and R6-AUD-02, so it is
        #: additionally listed in ``REJECTED_CANDIDATE_IDS`` in the
        #: authorization mechanism and barred here exactly as R1-R5 are.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6",
        #: Candidate R7 of this very lineage. Its fresh independent audit
        #: returned FAIL / NO-GO on R7-AUD-01, so it is additionally listed
        #: in ``REJECTED_CANDIDATE_IDS`` in the authorization mechanism and
        #: barred here exactly as R1-R6 are.
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7",
    ),
    #: Likewise cumulative. A candidate artifact may never fill a role that
    #: accepts a candidate, so every predecessor candidate checkpoint and
    #: manifest stays barred from roles 2-5 of this generation. Narrowing this
    #: to only this generation's own artifacts would silently drop the
    #: cross-generation self-acceptance negative control.  Candidate R1's own
    #: checkpoint and manifest stay listed for exactly that reason.
    candidate_artifact_paths=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHANGE_LEDGER_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R6_CHANGE_LEDGER_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R5_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R4_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R3_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R3_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R2_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R2_MANIFEST_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_CHECKPOINT_PATH,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_PATH,
        *FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.candidate_artifact_paths,
        *U06_R3_GENERATION.candidate_artifact_paths,
    ),
    predecessor_generation_id=(
        FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.generation_id
    ),
    predecessor_lineage_id=(
        FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.lineage_id
    ),
    predecessor_accepted_lifecycle_record_path=(
        FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION.accepted_lifecycle_record_path
    ),
    disposition="CURRENT_GENERATION_CANDIDATE_NOT_ACCEPTED_NOT_FROZEN",
    #: Candidate R8 is this generation's current candidate. Its fresh
    #: independent read-only audit has NOT been performed, so this is the only
    #: truthful value. It is deliberately NOT the historical U-06 alignment
    #: audit history (``R1_FAILED_R2_NO_GO_R3_PENDING``), which belongs to the
    #: U-06 generation and is retained separately under
    #: :data:`HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS`. Conflating the two was
    #: independent-audit blocker ``R2-AUD-03``.
    candidate_audit_state="NOT_YET_PERFORMED",
    #: ``R4-AUD-01`` / ``R5-AUD-01`` / ``R6-AUD-01`` / ``R7-AUD-01``: this
    #: generation's implementation-candidate manifest is validated by the
    #: closed-world semantic identity contract on the production lifecycle
    #: path, with every historical value derived from the external
    #: historical authority.  The contract applies to the CURRENT candidate
    #: (R8); the barred R1-R7 candidates of this lineage can never fill the
    #: role at all.
    candidate_manifest_contract=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4
    ),
    candidate_change_ledger_path=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R8_CHANGE_LEDGER_PATH
    ),
)

#: Generation 4 - Current Full81 Production Generation G1.
#:
#: Why a new generation, and why now.  Generation 3 (candidate R8) was
#: independently audited, accepted and re-frozen, so its single accepted-
#: lifecycle slot is occupied by a published record that binds the R8-claimed
#: implementation digest.  The live repository has since lawfully changed bytes
#: on that surface (the accepted FULLSTACK-01 authorization source and the
#: committed 21c / 21d route), so that record can never again resolve
#: PRESENT_VALID for the live implementation, and reaching ``FROZEN`` inside
#: generation 3 would require mutating an accepted artifact.  The repository's
#: own generalised precedent therefore applies: one additive generation, a
#: pointer advance, and every predecessor generation value left byte-identical.
#:
#: G1 is a governance / runtime CONSOLIDATION, not a methodology change: it
#: binds the current runtime, validation and governance-authority identities
#: into one generation with one content contract.  Generation 3's values above
#: are unchanged; its ``disposition`` string is the value it was declared with,
#: and its historical status follows from its position in
#: :data:`HISTORICAL_GENERATIONS`, never from that string.
#:
#: This generation is a CANDIDATE.  Its accepted-lifecycle slot and its four
#: predeclared role-record paths do not exist, so the live lifecycle resolves
#: ABSENT / NOT_FROZEN, and nothing here is accepted, frozen or authorized.
G1_GENERATION_ID = "CURRENT_FULL81_PRODUCTION_GENERATION_G1"
G1_ARTIFACT_TYPE_PREFIX = "FULL81_PRODUCTION_G1_"
G1_SCHEMA_PREFIX = "iris-thesis-full81-production-g1-"
G1_CANDIDATE_R1_CHECKPOINT_PATH = (
    "docs/checkpoints/"
    "current_full81_production_generation_g1_candidate_r1_2026-10-07.md"
)
G1_CANDIDATE_R1_MANIFEST_PATH = (
    "results/provenance/"
    "current_full81_production_generation_g1_candidate_r1_2026-10-07/"
    "g1_candidate_manifest.json"
)
G1_CANDIDATE_R1_CHANGE_LEDGER_PATH = (
    "results/provenance/"
    "current_full81_production_generation_g1_candidate_r1_2026-10-07/"
    "candidate_change_ledger.json"
)
G1_ACCEPTED_LIFECYCLE_RECORD_PATH = (
    "results/provenance/"
    "current_full81_production_generation_g1_accepted_lifecycle/"
    "accepted_lifecycle_record.json"
)
#: Future role-record paths, predeclared so that their exact-path EOL rules
#: exist before any of them is authored.  None of these files exists.
G1_PREDECLARED_ROLE_RECORD_PATHS: tuple[tuple[str, str], ...] = (
    (
        "independent_audit_pass",
        "results/provenance/"
        "current_full81_production_generation_g1_independent_audit_r1/"
        "independent_audit_pass_record.json",
    ),
    (
        "acceptance_closure",
        "results/provenance/"
        "current_full81_production_generation_g1_acceptance_r1/"
        "acceptance_closure.json",
    ),
    (
        "acceptance_manifest",
        "results/provenance/"
        "current_full81_production_generation_g1_acceptance_r1/"
        "acceptance_manifest.json",
    ),
    (
        "production_authority_re_freeze",
        "results/provenance/"
        "current_full81_production_generation_g1_re_freeze_r1/"
        "production_authority_re_freeze_record.json",
    ),
)

G1_GENERATION = AuthorityGeneration(
    generation_id=G1_GENERATION_ID,
    lineage_id=G1_GENERATION_ID,
    candidate_id="CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    candidate_checkpoint_path=G1_CANDIDATE_R1_CHECKPOINT_PATH,
    candidate_manifest_path=G1_CANDIDATE_R1_MANIFEST_PATH,
    accepted_lifecycle_record_path=G1_ACCEPTED_LIFECYCLE_RECORD_PATH,
    artifact_type_prefix=G1_ARTIFACT_TYPE_PREFIX,
    schema_prefix=G1_SCHEMA_PREFIX,
    #: Cumulative: every candidate of every predecessor generation, including
    #: the accepted-and-superseded R8 candidate, is barred.  Derived from the
    #: predecessor so the list cannot drift.
    superseded_candidate_ids=(
        *FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.superseded_candidate_ids,
        FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.candidate_id,
    ),
    #: Likewise cumulative, so no predecessor candidate artifact can ever fill
    #: roles 2-5 of G1.  G1's own candidate artifacts are listed first.
    candidate_artifact_paths=(
        G1_CANDIDATE_R1_CHECKPOINT_PATH,
        G1_CANDIDATE_R1_MANIFEST_PATH,
        G1_CANDIDATE_R1_CHANGE_LEDGER_PATH,
        *FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.candidate_artifact_paths,
    ),
    predecessor_generation_id=FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.generation_id,
    predecessor_lineage_id=FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.lineage_id,
    predecessor_accepted_lifecycle_record_path=(
        FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.accepted_lifecycle_record_path
    ),
    disposition="CURRENT_GENERATION_CANDIDATE_NOT_ACCEPTED_NOT_FROZEN",
    #: G1 candidate R1 has not been independently audited.
    candidate_audit_state="NOT_YET_PERFORMED",
    candidate_manifest_contract=G1_CANDIDATE_MANIFEST_CONTRACT,
    candidate_change_ledger_path=G1_CANDIDATE_R1_CHANGE_LEDGER_PATH,
    predeclared_role_record_paths=G1_PREDECLARED_ROLE_RECORD_PATHS,
)

#: Every generation ever declared, oldest first.  Predecessors are retained so
#: that what they were stays provable, never so that they can authorise.
AUTHORITY_GENERATIONS: tuple[AuthorityGeneration, ...] = (
    U06_R3_GENERATION,
    FULL81_AUTHORIZATION_MECHANISM_R2_GENERATION,
    FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION,
    G1_GENERATION,
)

#: The one generation that may freeze live production authority.  Advancing this
#: pointer is the whole mechanism of a generation change: no validator is
#: rewritten and no predecessor artifact is touched.  Until this candidate is
#: independently audited, accepted and re-frozen, its accepted-lifecycle slot
#: does not exist, so the live lifecycle resolves ABSENT / NOT_FROZEN. That is
#: the correct and intended candidate-era state, not a regression.
#:
#: Advanced to G1.  Generation 3 (candidate R8) is now historical: its accepted,
#: published record stays byte-identical and provable, and it can never freeze
#: live production authority again.
CURRENT_GENERATION = G1_GENERATION

#: Fail-closed structural guard for ``R4-AUD-01``, run at import time so the
#: defect cannot be reintroduced silently: the CURRENT generation may never
#: fall back to envelope-only validation of its candidate manifest, and may
#: never name a contract this module cannot validate.
if CURRENT_GENERATION.candidate_manifest_contract is None:
    raise AssertionError(
        "R4-AUD-01 regression: the current generation "
        f"{CURRENT_GENERATION.generation_id} declares no candidate-manifest "
        "content contract, so its implementation-candidate manifest would be "
        "validated by the role envelope only."
    )
if (
    CURRENT_GENERATION.candidate_manifest_contract
    not in KNOWN_CANDIDATE_MANIFEST_CONTRACTS
):
    raise AssertionError(
        "R4-AUD-01 regression: the current generation names an unknown "
        f"candidate-manifest contract "
        f"{CURRENT_GENERATION.candidate_manifest_contract!r}."
    )
if (
    CURRENT_GENERATION.candidate_manifest_contract
    == FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4
    and not CURRENT_GENERATION.candidate_change_ledger_path
):
    raise AssertionError(
        "Contract V4 requires a candidate change ledger, but the current "
        f"generation {CURRENT_GENERATION.generation_id} declares none."
    )
#: G1 additions to the same fail-closed import guard.  The G1 contract binds
#: a change ledger, and a G1-contract generation must predeclare the exact path
#: of every future role record so that none can be authored without an EOL rule
#: or filled from an unexpected location.
if (
    CURRENT_GENERATION.candidate_manifest_contract == G1_CANDIDATE_MANIFEST_CONTRACT
    and not CURRENT_GENERATION.candidate_change_ledger_path
):
    raise AssertionError(
        "The G1 contract requires a candidate change ledger, but the current "
        f"generation {CURRENT_GENERATION.generation_id} declares none."
    )
if CURRENT_GENERATION.candidate_manifest_contract == G1_CANDIDATE_MANIFEST_CONTRACT and (
    CURRENT_GENERATION.role_record_path_map is None
    or set(CURRENT_GENERATION.role_record_path_map)
    != {role for role in ROLE_CONTRACT_TEMPLATES if role != "implementation_candidate"}
    or len(set(CURRENT_GENERATION.role_record_path_map.values()))
    != len(CURRENT_GENERATION.role_record_path_map)
):
    raise AssertionError(
        "The G1 contract requires exactly one distinct predeclared path for "
        "each of the four non-candidate lifecycle roles."
    )

#: Superseded generations: provable, never authoritative.
HISTORICAL_GENERATIONS: tuple[AuthorityGeneration, ...] = tuple(
    g for g in AUTHORITY_GENERATIONS if g is not CURRENT_GENERATION
)

GENERATIONS_BY_ID: Mapping[str, AuthorityGeneration] = {
    g.generation_id: g for g in AUTHORITY_GENERATIONS
}
GENERATIONS_BY_LINEAGE: Mapping[str, AuthorityGeneration] = {
    g.lineage_id: g for g in AUTHORITY_GENERATIONS
}


def generation_for_lineage(lineage_id: Any) -> "AuthorityGeneration | None":
    """The declared generation for `lineage_id`, or ``None`` if unknown."""

    return GENERATIONS_BY_LINEAGE.get(str(lineage_id))


def current_generation() -> "AuthorityGeneration":
    """The one generation that may freeze live production authority."""

    return CURRENT_GENERATION


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
    "src/main_full81_authorization_v7_4.py",
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
#:
#: Candidate R4 adds the two suites that were missing from this surface. Both
#: are negative-control suites for the CURRENT generation, so leaving them
#: undeclared meant a silent swap of either one was undetectable by the same
#: identity mechanism that protects every other suite - the same defect class
#: as ``R3-AUD-02``, one layer up. Adding them widens what is protected and
#: weakens nothing.
#:
#: Current Full81 Production Generation G1: this is now ``G1_VALIDATION_IDENTITY``,
#: the validation generation of G1, versioned separately from the runtime
#: generation.  Membership changes, each justified:
#:
#: * ``tests/test_fullstack_01_execution_input_authority.py`` joins.  It is the
#:   accepted FULLSTACK-01 validation of the execution-input authority that the
#:   G1 execution guard consumes, and it was never declared here.
#: * ``tests/test_21l_full81_production_generation_g1.py`` joins: the G1
#:   contract, phase, execution-guard and raw-byte invariant suite.
#: * ``tests/test_21j_authority_raw_byte_eol_coverage.py`` and
#:   ``tests/test_21k_external_historical_authority_attacks.py`` move to
#:   :data:`HISTORICAL_VALIDATION_IDENTITY_PATHS`.  Both assert generation 3
#:   (candidate R8) as current and bind contract-V4 positive controls to live
#:   R8-era bytes, so neither can describe G1.  They are retained
#:   byte-identical as R8 regression evidence, and the generation-independent
#:   invariants they carried are restated for G1 in the 21l suite.
#:
#: ``tests/test_21i_main_full81_preflight_authorization_guard.py`` stays: it was
#: declared here by R8 and recorded as an executed suite by the published R8
#: ledger, but never committed.  G1 does not publish those R8-recorded bytes: its
#: N-04 control is phase-aware in G1, so G1 creates the suite, and the raw
#: SHA-256 the published R8 ledger recorded remains historical evidence of the
#: R8 run only.
VALIDATION_IDENTITY_PATHS: tuple[str, ...] = (
    "tests/test_21a_v7_3_production_routing_preflight.py",
    "tests/test_21b_21d_v7_3_production_successor_stack.py",
    "tests/test_21e_v7_4_production_authority_bundle.py",
    "tests/test_21f_u06_accepted_lifecycle_gate.py",
    "tests/test_21g_u06_r3_substitution_attacks.py",
    "tests/test_21h_main_full81_authorization_mechanism.py",
    "tests/test_21i_main_full81_preflight_authorization_guard.py",
    "tests/test_21l_full81_production_generation_g1.py",
    "tests/test_fullstack_01_execution_input_authority.py",
)

#: Validation suites of a SUPERSEDED generation, retained byte-identical as
#: historical regression evidence.  They are not part of
#: ``G1_VALIDATION_IDENTITY`` and are not executed as G1 validation, but their
#: raw bytes stay protected by the EOL policy so the historical evidence remains
#: reproducible from a clean clone.
HISTORICAL_VALIDATION_IDENTITY_PATHS: tuple[str, ...] = (
    "tests/test_21j_authority_raw_byte_eol_coverage.py",
    "tests/test_21k_external_historical_authority_attacks.py",
)

#: Validation suites whose exact bytes are pinned by RUNTIME code, so that
#: changing one changes the runtime implementation digest.  This coupling is
#: deliberate and pre-dates G1: the production-authority bundle pins the 21e,
#: 21f, 21g and 21h suites (derived live from its pin table, see
#: :func:`g1_intentional_runtime_validation_coupling`), and the successor stack
#: pins the 21a suite through ``ADDITIONAL_AUTHORITY_FILES``.  The stack is not
#: imported here (it would load the production backend), so its one pinned
#: suite is declared and the 21l suite proves the declaration equals the stack.
G1_STACK_PINNED_VALIDATION_PATHS: tuple[str, ...] = (
    "tests/test_21a_v7_3_production_routing_preflight.py",
)

#: Retained for continuity of the R2 name; it is now the full accepted surface.
IMPLEMENTATION_CANDIDATE_SURFACE = ACCEPTED_IMPLEMENTATION_PATHS


# ---------------------------------------------------------------------------
# R2-AUD-01: durable publication requirements
# ---------------------------------------------------------------------------
#
# Candidate R3 remediation of independent-audit blocker ``R2-AUD-01`` (MAJOR /
# BLOCKING).  ``data/reference/parameter_registry_v7_2.csv`` is an authority
# pin of the production bundle, but it is matched by the broad ``data/`` rule in
# ``.gitignore`` and was absent from ``HEAD``.  A third party cloning the
# published repository therefore could not verify the authority bundle at all:
# the file simply was not there, and the only copy was an ignored working-tree
# file on one machine.  An authority pin whose target is not published is not
# durable authority.
#
# The remedy is publication, not relaxation.  The canonical content is NOT
# modified, and ``.gitignore`` is NOT modified: a narrowly scoped force-add
# (``git add -f <exact path>``) is mechanically sufficient, which this
# repository already proves - ``data/processed/annual_input_v7_3_reconstructed_
# pv_mainline_candidate_r3_2026-09-23.parquet`` and its manifest are tracked and
# published in ``HEAD`` under that very same ``data/`` ignore rule.  Because a
# force-add demonstrably provides durable publication, broadening the ignore
# policy would be an unjustified change and is deliberately not made.
#
# Declaring the requirement here is what makes it enforceable rather than
# advisory: a future candidate publication that omits one of these paths can be
# detected mechanically instead of discovered by a later auditor.

#: Authority-critical paths that MUST exist in published Git content for the
#: production-authority route to be reconstructible from a clean clone.
#:
#: Mechanically derived, not guessed.  Of the 34 authority-bundle pin targets,
#: 32 are already present in ``HEAD`` and exactly two are not: the parameter
#: registry and the new EOL policy.  All 21 accepted implementation-identity
#: paths are already published.  The current generation's candidate checkpoint
#: and manifest are added because a future acceptance's role validators read
#: them by path, so an unpublished one is the same defect class as ``R2-AUD-01``.
#:
#: ``.gitignore`` has TWO broad rules that bear on this, both deliberately left
#: unchanged: ``data/`` (line 20) and ``results/`` (line 23).  Every required
#: path under either tree therefore needs a narrowly scoped force-add, which is
#: how this repository already publishes its other authority artifacts under
#: those same trees.
#:
#: Candidate R6: the current candidate's change ledger joins them.  The
#: manifest binds the ledger's raw SHA-256 and the GATE-mode contract reads
#: the ledger, so an unpublished ledger would be the same defect class.
REQUIRED_DURABLE_PUBLICATION_PATHS: tuple[str, ...] = (
    "data/reference/parameter_registry_v7_2.csv",
    ".gitattributes",
    CURRENT_GENERATION.candidate_checkpoint_path,
    CURRENT_GENERATION.candidate_manifest_path,
    *(
        (CURRENT_GENERATION.candidate_change_ledger_path,)
        if CURRENT_GENERATION.candidate_change_ledger_path
        else ()
    ),
)

#: Which required paths carry a bundle pin, and therefore a canonical digest to
#: verify against.  The candidate checkpoint and manifest deliberately have no
#: pin: the manifest binds the checkpoint by hash, and nothing may bind the
#: manifest's own hash without creating a cycle.  For those two, durability
#: means "published, and published bytes equal live bytes" rather than
#: "published, and matching a pinned constant".
REQUIRED_DURABLE_PUBLICATION_PIN_LABELS: Mapping[str, str] = {
    "data/reference/parameter_registry_v7_2.csv": "parameter_registry",
    ".gitattributes": "repository_eol_policy",
}


def required_durable_publication_force_add_paths(root: Path) -> tuple[str, ...]:
    """Required paths still matched by an ignore rule, so needing ``git add -f``.

    Derived from live ignore state rather than restated as a constant, so it
    cannot fall behind a ``.gitignore`` change or a path that becomes tracked.
    Force-adding names exactly one path and never broadens the ignore policy.
    """

    return tuple(
        rel
        for rel in REQUIRED_DURABLE_PUBLICATION_PATHS
        if _is_path_ignored(root, rel)
    )

#: This module deliberately contains **no** 64-hex digest literal, and that
#: invariant is enforced by a static test.  Canonical digests are therefore read
#: from the authority bundle, which is the one module whose job is to hold
#: exact-hash pins.  Restating one here would create a second source of truth
#: that could silently drift from the pin it duplicates - exactly the class of
#: provenance defect this overlay exists to prevent.
#:
#: Of note: the parameter registry is canonically CRLF (27 CRLF, 0 bare LF).
#: Normalizing it to LF yields a different digest and destroys its pinned
#: identity, which is why the EOL policy declares that path ``-text`` rather
#: than ``text eol=lf``.
def _required_durable_publication_sha256() -> dict[str, str | None]:
    """Canonical digests for the required paths, read from the authority bundle.

    Imported lazily: the bundle imports this overlay, so a module-level import
    here would be circular.  By the time this is called the bundle is loaded.
    Returns ``None`` for a path whose pin cannot be resolved, so a caller fails
    closed rather than silently accepting an unverifiable path.
    """

    try:
        from src.production_authority_bundle_v7_4 import all_pins
    except Exception:  # pragma: no cover - fail closed, never fail open
        return {rel: None for rel in REQUIRED_DURABLE_PUBLICATION_PATHS}

    by_label = {pin.label: pin for pin in all_pins()}
    out: dict[str, str | None] = {}
    for relative in REQUIRED_DURABLE_PUBLICATION_PATHS:
        label = REQUIRED_DURABLE_PUBLICATION_PIN_LABELS.get(relative)
        pin = by_label.get(label) if label else None
        # The pin must also agree about the path, or the mapping is stale.
        out[relative] = (
            pin.sha256 if pin is not None and pin.relative_path == relative else None
        )
    return out

#: Known, deliberately-scoped limitation carried forward from ``I-04``.
#:
#: The declarations above cover the *authority-reconstruction* surface: the 34
#: bundle pin targets, the 21 implementation-identity paths, Framework, Registry,
#: and the candidate artifacts.  A clean clone that adds the two paths above can
#: verify every authority identity.
#:
#: It does NOT cover *scientific source data*, which the broad ``data/`` ignore
#: rule also excludes and which the full successor stack loads only when it
#: actually builds model inputs - for example the 14a normalized tariff at
#: ``data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv``.  Those files
#: are not authority pins, are not part of the implementation identity, and are
#: not reachable on any no-solve authority-verification path.
#:
#: This is recorded rather than silently fixed because publishing scientific
#: source data is a separate decision with its own licensing and data-governance
#: questions, and nothing in the Candidate R3 scope authorizes it.  It remains an
#: open durability gap for full-stack reconstruction and is reported as such.
NON_AUTHORITY_GITIGNORED_RUNTIME_DEPENDENCIES: tuple[str, ...] = (
    "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
)
#: Candidate-neutral since Candidate R6: the label used to name a specific
#: candidate and went stale at every candidate advance.
NON_AUTHORITY_GITIGNORED_DEPENDENCY_STATUS = (
    "OPEN_CARRIED_NOT_IN_CURRENT_CANDIDATE_SCOPE_FULL_STACK_RECONSTRUCTION_ONLY"
)

#: ``FULLSTACK-01``, carried forward explicitly and NOT expanded in this pass.
#: These are scientific source-data / settlement-interface files that the full
#: successor stack loads only when it actually builds model inputs.  None is an
#: authority pin, none is part of the implementation identity, and none is
#: reachable on any no-solve authority-verification path, so none blocks the
#: current candidate.  Publishing them is a separate licensing and
#: data-governance decision that nothing in the current candidate scope
#: authorizes.
#:
#: The sentinel below is what stops this being forgotten: it is carried into
#: the candidate manifest and checkpoint and states the gate at which it
#: becomes blocking.
FULLSTACK_01_PATHS: tuple[str, ...] = (
    "data/reference/production_economic_interface_v7_2.json",
    "data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv",
    "data/reference/taipower_transition_period_settlement_interface_v7_2.json",
    "data/reference/taipower_seasonal_settlement_matrix_v7_2.csv",
)
FULLSTACK_01_STATUS = (
    "OPEN_NONBLOCKING_CURRENT_CANDIDATE_BLOCKING_BEFORE_FULL_SUCCESSOR_"
    "PREFLIGHT_OR_EXECUTION"
)
FULLSTACK_01_BLOCKING_BEFORE: tuple[str, ...] = (
    "FULL_SUCCESSOR_PREFLIGHT",
    "MAIN_FULL81_EXECUTION",
)


# ---------------------------------------------------------------------------
# R3-AUD-02: the COMPLETE raw-byte authority consumer universe
# ---------------------------------------------------------------------------
#
# Candidate R3 received ``FAIL / NO-GO`` on ``R3-AUD-02`` (MAJOR / BLOCKING):
# its ``.gitattributes`` omitted twelve historical accepted-lifecycle artifacts
# whose raw bytes are authority-critical.  Under ``core.autocrlf=true`` all
# twelve became CRLF on a fresh checkout, their raw SHA-256 changed, and Git
# still reported the working tree clean.
#
# The defect existed because EOL coverage and the raw-byte consumer set were
# maintained independently: one was a hand-written list in ``.gitattributes``,
# the other was wherever a validator happened to read a file.  Appending the
# twelve would fix today's symptom and leave the drift mechanism intact.
#
# The remedy is to make the consumer set derivable.  :func:`
# authority_raw_byte_consumer_universe` reconstructs it from PRIMARY SOURCE -
# the bundle's own pin table, this overlay's own identity declarations, every
# declared generation's own lifecycle paths, the role records that on-disk
# accepted-lifecycle records actually name, and the authorization mechanism's
# own path declarations.  :func:`eol_policy_coverage` then checks
# ``.gitattributes`` against that derived universe and fails closed on any
# uncovered or wrongly-treated path.  A future raw-byte consumer added without
# a rule is therefore caught by a test rather than by a later auditor.
#
# The twelve paths the independent audit named are a strict subset of what the
# derivation finds; they are covered because the derivation finds them, not
# because they were restated here.  This module deliberately contains no
# hand-written copy of that twelve-path list.

#: Deterministic raw-byte preservation packages for the candidates of this
#: generation.  Each holds immutable audited candidate bytes, so the archives
#: must round-trip bit-exactly and the index / STOP records must check out
#: byte-identically.  Declared here because they are read as raw bytes when a
#: predecessor candidate's exact state has to be reproduced.
CANDIDATE_PRESERVATION_PACKAGES: Mapping[str, Mapping[str, str]] = {
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r1_"
            "publication_stop_2026-10-04"
        ),
        "archive": "candidate_r1_raw_bytes.zip",
        "index": "candidate_r1_raw_byte_index.json",
        "stop_record": "publication_stop_record.json",
        "stop_class": "PUBLICATION_STOP",
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r2_"
            "audit_stop_2026-10-04"
        ),
        "archive": "candidate_r2_raw_bytes.zip",
        "index": "candidate_r2_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r3_"
            "audit_stop_2026-10-05"
        ),
        "archive": "candidate_r3_raw_bytes.zip",
        "index": "candidate_r3_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
    #: Candidate R5 addition.  The Candidate R4 independent-audit STOP package
    #: passed its own independent audit with nonblocking findings.  Its bytes
    #: are immutable; declaring it here only makes its three files raw-byte
    #: authority consumers, so their checkout form is pinned by the EOL policy.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r4_"
            "audit_stop_2026-10-05"
        ),
        "archive": "candidate_r4_raw_bytes.zip",
        "index": "candidate_r4_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
    #: Candidate R6 addition.  The Candidate R5 independent-audit STOP package
    #: (R5-AUD-01 / R5-AUD-02).  Its bytes are immutable; declaring it here
    #: makes its three files raw-byte authority consumers, and its raw-byte
    #: index is the verifiable source of every R5-era identity the Candidate R6
    #: change ledger states.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r5_"
            "audit_stop_2026-10-05"
        ),
        "archive": "candidate_r5_raw_bytes.zip",
        "index": "candidate_r5_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
    #: Candidate R7 addition.  The Candidate R6 independent-audit STOP package
    #: (R6-AUD-01 / R6-AUD-02).  Its bytes are immutable; declaring it here
    #: makes its three files raw-byte authority consumers, and its raw-byte
    #: index is the verifiable source of every R6-era identity the Candidate R7
    #: change ledger states.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r6_"
            "audit_stop_2026-10-05"
        ),
        "archive": "candidate_r6_raw_bytes.zip",
        "index": "candidate_r6_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
    #: Candidate R8 addition.  The Candidate R7 independent-audit STOP package
    #: (R7-AUD-01).  Its bytes are immutable and its identity is bound by the
    #: independently accepted R7 Preservation Authority Binding, which the
    #: Git-frozen pre-R8 trust root pins.  This declaration is shape only:
    #: contract V4 requires it to equal the package the external evidence
    #: describes, and never reads an identity from it.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7": {
        "directory": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r7_"
            "audit_stop_2026-10-06"
        ),
        "archive": "candidate_r7_raw_bytes.zip",
        "index": "candidate_r7_raw_byte_index.json",
        "stop_record": "independent_audit_stop_record.json",
        "stop_class": "INDEPENDENT_AUDIT_STOP",
    },
}

#: Paths whose canonical form is NOT LF and which therefore must be declared
#: byte-preserving (``-text`` or ``binary``) rather than ``text eol=lf``.
#: Derived from live bytes by :func:`canonical_eol_class`, never asserted here;
#: this tuple records only the ones whose non-LF form is itself pinned, so a
#: silent change of canonical form is a coverage failure rather than a quiet
#: re-classification.
CANONICAL_NON_LF_AUTHORITY_PATHS: tuple[str, ...] = (
    "data/reference/parameter_registry_v7_2.csv",
    "results/provenance/"
    "main_full81_preflight_authorization_guard_candidate_r1_2026-10-03/"
    "preflight_authorization_guard_manifest.json",
)

#: Accepted historical artifacts that must stay entirely unfiltered.  They are
#: MIXED-EOL, so any ``text`` rule would rewrite them and any ``-text`` rule
#: would still add an attribute to an accepted blob.  They are not raw-byte
#: authority consumers, so the correct treatment is no rule at all, and a
#: coverage guard that silently "fixed" them would corrupt accepted provenance.
DELIBERATELY_UNFILTERED_HISTORICAL_PREFIXES: tuple[str, ...] = (
    "results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/",
)

EOL_POLICY_RELATIVE_PATH = ".gitattributes"


def canonical_eol_class(root: Path, relative: str) -> str:
    """Classify a path's live canonical bytes: LF / CRLF / MIXED / BINARY.

    ``ABSENT`` for a lawful path not yet authored.  Read-only.
    """

    path = Path(root) / relative
    if not path.is_file():
        return "ABSENT"
    data = path.read_bytes()
    if b"\x00" in data:
        return "BINARY"
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    if crlf and lf:
        return "MIXED"
    if crlf:
        return "CRLF"
    if lf:
        return "LF"
    return "NONE"


def authority_raw_byte_consumer_universe(root: Path) -> dict[str, tuple[str, ...]]:
    """Every path whose RAW BYTES can change an authority decision.

    Reconstructed from primary source on every call, so it cannot fall behind
    the declarations it is derived from.  Returns ``{relative_path: reasons}``.

    Read-only: nothing is written, staged, committed, or executed, and no
    model is constructed.
    """

    root = Path(root).resolve()
    universe: dict[str, set[str]] = {}

    def add(relative: Any, reason: str) -> None:
        normalized = str(relative).replace("\\", "/").strip()
        if normalized:
            universe.setdefault(normalized, set()).add(reason)

    # 1. The authority bundle's own pin table: every pin is verified by raw
    #    SHA-256, so every pin target is a raw-byte consumer by definition.
    #    Imported lazily because the bundle imports this overlay.
    try:
        from src.production_authority_bundle_v7_4 import all_pins
    except Exception:  # pragma: no cover - fail closed, never fail open
        add("<BUNDLE_PINS_UNRESOLVABLE>", "BUNDLE_PIN_IMPORT_FAILED")
    else:
        for pin in all_pins():
            add(pin.relative_path, f"AUTHORITY_BUNDLE_PIN[{pin.label}]")

    # 2. This overlay's own identity declarations.
    for relative in ACCEPTED_IMPLEMENTATION_PATHS:
        add(relative, "ACCEPTED_IMPLEMENTATION_IDENTITY")
    for relative in VALIDATION_IDENTITY_PATHS:
        add(relative, "VALIDATION_IDENTITY")
    for relative in HISTORICAL_VALIDATION_IDENTITY_PATHS:
        add(relative, "HISTORICAL_VALIDATION_IDENTITY")
    for relative in REQUIRED_DURABLE_PUBLICATION_PATHS:
        add(relative, "REQUIRED_DURABLE_PUBLICATION")
    add(EOL_POLICY_RELATIVE_PATH, "REPOSITORY_GOVERNANCE_EOL_POLICY")

    # 3. Every declared generation's own lifecycle surface.  Lawful paths that
    #    do not exist yet are included on purpose: a FUTURE record must be
    #    protected the moment it is authored, not after the next audit.
    for generation in AUTHORITY_GENERATIONS:
        tag = generation.generation_id
        add(generation.candidate_checkpoint_path, f"CANDIDATE_CHECKPOINT[{tag}]")
        add(generation.candidate_manifest_path, f"CANDIDATE_MANIFEST[{tag}]")
        if generation.candidate_change_ledger_path:
            add(
                generation.candidate_change_ledger_path,
                f"CANDIDATE_CHANGE_LEDGER[{tag}]",
            )
        add(
            generation.accepted_lifecycle_record_path,
            f"ACCEPTED_LIFECYCLE_RECORD_SLOT[{tag}]",
        )
        if generation.predecessor_accepted_lifecycle_record_path:
            add(
                generation.predecessor_accepted_lifecycle_record_path,
                f"PREDECESSOR_ACCEPTED_LIFECYCLE_RECORD[{tag}]",
            )
        for relative in generation.candidate_artifact_paths:
            add(relative, f"BARRED_CANDIDATE_ARTIFACT[{tag}]")
        for role, relative in (generation.role_record_path_map or {}).items():
            add(relative, f"PREDECLARED_ROLE_RECORD_SLOT[{tag}::{role}]")

    # 4. The role records that on-disk accepted-lifecycle records actually
    #    name.  THIS is the step Candidate R3 had no equivalent of, and it is
    #    what finds the historical accepted-lifecycle chains: the role
    #    validators read each of these by path and hash its raw bytes, so a
    #    CRLF-smudged checkout makes a lawful acceptance resolve
    #    PRESENT_INVALID.
    seen_records: set[str] = set()
    for generation in AUTHORITY_GENERATIONS:
        for slot in (
            generation.accepted_lifecycle_record_path,
            generation.predecessor_accepted_lifecycle_record_path,
        ):
            if not slot or slot in seen_records:
                continue
            seen_records.add(slot)
            record = root / slot
            if not record.is_file():
                continue
            try:
                payload = json.loads(record.read_text(encoding="utf-8"))
            except Exception:  # pragma: no cover - unreadable record
                add(slot, f"ACCEPTED_LIFECYCLE_RECORD_UNREADABLE[{slot}]")
                continue
            if not isinstance(payload, Mapping):
                continue
            roles = payload.get("roles")
            if isinstance(roles, Mapping):
                for role, entry in roles.items():
                    if isinstance(entry, Mapping) and entry.get("path"):
                        add(entry["path"], f"ACCEPTED_LIFECYCLE_ROLE[{slot}::{role}]")
            for field in ("candidate_checkpoint", "candidate_manifest"):
                entry = payload.get(field)
                if isinstance(entry, Mapping) and entry.get("path"):
                    add(entry["path"], f"ACCEPTED_LIFECYCLE_FIELD[{slot}::{field}]")

    # 5. The Main Full81 authorization mechanism's own path declarations.
    try:
        from src.main_full81_authorization_v7_4 import (
            AUTHORIZATION_RECORD_RELATIVE_PATH,
            EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH,
            EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
            EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
            EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
            EXPECTED_RUNNER_RELATIVE_PATH,
            FULL81_EXECUTION_INPUT_AUTHORITY_PINS,
            NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH,
            REJECTED_AUTHORIZATION_PATHS_THIS_LINEAGE,
            REJECTED_HISTORICAL_AUTHORIZATION_PATHS,
            SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM,
        )
    except Exception:  # pragma: no cover - fail closed, never fail open
        add("<FULL81_AUTHORIZATION_UNRESOLVABLE>", "FULL81_AUTHORIZATION_IMPORT_FAILED")
    else:
        add(
            AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
            "FULL81_AUTHORIZATION_RECORD_SLOT",
        )
        # G1: the execution-authorization guard reads both of these by raw
        # bytes once they exist, so their checkout form is fixed now.
        add(
            EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
            "FULL81_EXECUTION_AUTHORIZATION_RECORD_SLOT",
        )
        add(
            NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix(),
            "FULL81_NO_SOLVE_PREFLIGHT_EVIDENCE_SLOT",
        )
        # FULLSTACK-01: the execution-input authority hashes these raw bytes at
        # the execution boundary, so a smudged checkout would refuse execution.
        for pin in FULL81_EXECUTION_INPUT_AUTHORITY_PINS:
            add(pin.relative_path, f"FULL81_EXECUTION_INPUT_AUTHORITY_PIN[{pin.label}]")
        add(EXPECTED_RUNNER_RELATIVE_PATH, "FULL81_AUTHORIZATION_TARGET_RUNNER")
        add(EXPECTED_ANNUAL_INPUT_RELATIVE_PATH, "FULL81_AUTHORIZATION_ANNUAL_INPUT")
        add(EXPECTED_ANNUAL_MODEL_RELATIVE_PATH, "FULL81_AUTHORIZATION_ANNUAL_MODEL")
        add(
            EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
            "FULL81_AUTHORIZATION_PARAMETER_REGISTRY",
        )
        for relative in REJECTED_HISTORICAL_AUTHORIZATION_PATHS:
            add(relative, "REJECTED_HISTORICAL_AUTHORIZATION_PATH")
        for relative in REJECTED_AUTHORIZATION_PATHS_THIS_LINEAGE:
            add(relative, "REJECTED_AUTHORIZATION_PATH_THIS_LINEAGE")
        for relative in SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM:
            add(relative, "SUPERSEDED_AUTHORIZATION_PATH_THIS_MECHANISM")

    # 6. Candidate raw-byte preservation packages.
    for candidate, package in CANDIDATE_PRESERVATION_PACKAGES.items():
        directory = package["directory"]
        for key in ("archive", "index", "stop_record"):
            add(f"{directory}/{package[key]}", f"CANDIDATE_PRESERVATION[{candidate}]")

    # 7. Candidate R8 (contract V4): the external historical authority's own
    #    inputs.  The trust root is authenticated from its Git blob and its
    #    working-tree copy must equal that blob; the binding is read by its
    #    exact raw bytes.  Both are therefore raw-byte consumers.  The
    #    binding locator is read from the trust root's frozen blob, never
    #    restated here.
    try:
        from src.production_authority_bundle_v7_4 import (
            PRE_R8_HISTORICAL_TRUST_ROOT as frozen,
        )
    except Exception:  # pragma: no cover - fail closed, never fail open
        add("<PRE_R8_TRUST_ROOT_UNRESOLVABLE>", "PRE_R8_TRUST_ROOT_IMPORT_FAILED")
    else:
        add(frozen.path, "PRE_R8_HISTORICAL_TRUST_ROOT")
        try:
            selection = _trust_root_binding_selection(
                _git_bytes(root, "cat-file", "blob", frozen.blob) or b""
            )
        except U06LifecycleError:
            add("<R7_BINDING_LOCATOR_UNRESOLVABLE>", "PRE_R8_TRUST_ROOT_UNREADABLE")
        else:
            add(selection["locator"], "R7_PRESERVATION_AUTHORITY_BINDING")

    return {relative: tuple(sorted(reasons)) for relative, reasons in universe.items()}


def _parse_eol_policy(text: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Parse ``.gitattributes`` into ordered ``(pattern, attributes)`` rules."""

    rules: list[tuple[str, tuple[str, ...]]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        rules.append((fields[0], tuple(fields[1:])))
    return tuple(rules)


def _eol_rule_matches(pattern: str, relative: str) -> bool:
    """Git attribute matching, restricted to the forms this policy uses.

    This policy declares only full repository-relative paths and one bare
    filename (``.gitattributes``).  A pattern containing ``/`` matches the full
    path; a pattern without one matches the basename at any depth, which is
    Git's own rule.  No other glob form is used, and a future rule that needed
    one would be caught by the coverage guard rather than silently mismatched.
    """

    if "/" in pattern.strip("/"):
        return fnmatch.fnmatchcase(relative, pattern)
    return fnmatch.fnmatchcase(relative.rsplit("/", 1)[-1], pattern)


def effective_eol_rule(
    rules: Sequence[tuple[str, tuple[str, ...]]], relative: str
) -> tuple[str, tuple[str, ...]] | None:
    """The rule Git would apply to ``relative``: the LAST matching rule."""

    effective: tuple[str, tuple[str, ...]] | None = None
    for pattern, attributes in rules:
        if _eol_rule_matches(pattern, relative):
            effective = (pattern, attributes)
    return effective


def eol_policy_coverage(root: Path) -> dict[str, Any]:
    """Check ``.gitattributes`` against the derived raw-byte consumer universe.

    Fails closed: a path with no rule, or with a rule that would not preserve
    its canonical bytes, is reported as a coverage failure.  Read-only; never
    raises for a coverage problem, so a caller states the blocker rather than
    crashing, and never modifies ``.gitattributes``.

    The universe is derived, not restated, so adding a raw-byte consumer
    anywhere in primary source without a matching rule here turns this report
    unsatisfied on the next run.
    """

    root = Path(root).resolve()
    policy_path = root / EOL_POLICY_RELATIVE_PATH
    universe = authority_raw_byte_consumer_universe(root)

    if not policy_path.is_file():
        return {
            "satisfied": False,
            "policy_present": False,
            "policy_path": EOL_POLICY_RELATIVE_PATH,
            "blocking_reason": (
                "REPOSITORY_EOL_POLICY_MISSING: .gitattributes does not exist, "
                "so no authority path has a deterministic checkout rule."
            ),
            "universe_path_count": len(universe),
            "rule_count": 0,
            "uncovered": sorted(universe),
            "uncovered_count": len(universe),
            "wrongly_treated": [],
            "wrongly_treated_count": len(universe),
            "unused_rules": [],
            "entries": {},
            "deliberately_unfiltered_prefixes": list(
                DELIBERATELY_UNFILTERED_HISTORICAL_PREFIXES
            ),
        }

    rules = _parse_eol_policy(policy_path.read_text(encoding="utf-8"))
    entries: dict[str, Any] = {}
    uncovered: list[str] = []
    wrongly_treated: list[dict[str, Any]] = []
    used_patterns: set[str] = set()

    for relative in sorted(universe):
        eol_class = canonical_eol_class(root, relative)
        rule = effective_eol_rule(rules, relative)
        if rule is None:
            uncovered.append(relative)
            entries[relative] = {
                "eol_class": eol_class,
                "rule_pattern": None,
                "rule_attributes": [],
                "deterministic": False,
                "reasons": list(universe[relative]),
            }
            continue
        pattern, attributes = rule
        used_patterns.add(pattern)
        attribute_set = set(attributes)
        byte_preserving = bool(attribute_set & {"-text", "binary"})
        lf_pinned = "text" in attribute_set and "eol=lf" in attribute_set
        # A canonically non-LF path must be byte-preserving: `text eol=lf`
        # would rewrite it and destroy a pinned identity.  A canonically LF
        # path is deterministic under either treatment.
        if eol_class in ("CRLF", "MIXED", "BINARY"):
            deterministic = byte_preserving
        else:
            deterministic = lf_pinned or byte_preserving
        entries[relative] = {
            "eol_class": eol_class,
            "rule_pattern": pattern,
            "rule_attributes": list(attributes),
            "deterministic": deterministic,
            "reasons": list(universe[relative]),
        }
        if not deterministic:
            wrongly_treated.append(
                {
                    "path": relative,
                    "eol_class": eol_class,
                    "rule_pattern": pattern,
                    "rule_attributes": list(attributes),
                    "required": (
                        "byte-preserving (-text or binary)"
                        if eol_class in ("CRLF", "MIXED", "BINARY")
                        else "text eol=lf, or byte-preserving"
                    ),
                }
            )

    # A rule matching nothing in the universe is not a failure, but it IS a
    # drift signal worth reporting: either the universe shrank or the rule is
    # broader than the policy claims to be.
    unused_rules = [
        {"pattern": pattern, "attributes": list(attributes)}
        for pattern, attributes in rules
        if pattern not in used_patterns
    ]

    # No rule may reach the deliberately-unfiltered accepted historical blobs.
    overreaching: list[dict[str, Any]] = []
    for pattern, attributes in rules:
        for prefix in DELIBERATELY_UNFILTERED_HISTORICAL_PREFIXES:
            if pattern.startswith(prefix) or _eol_rule_matches(pattern, prefix):
                overreaching.append(
                    {"pattern": pattern, "attributes": list(attributes), "prefix": prefix}
                )

    satisfied = not uncovered and not wrongly_treated and not overreaching
    return {
        "satisfied": satisfied,
        "policy_present": True,
        "policy_path": EOL_POLICY_RELATIVE_PATH,
        "policy_sha256": sha256_file(policy_path),
        "derivation": (
            "Universe derived from primary source by "
            "authority_raw_byte_consumer_universe(); coverage derived from the "
            "live .gitattributes. Neither side is a hand-written copy of the "
            "other, so the two cannot drift apart silently."
        ),
        "universe_path_count": len(universe),
        "rule_count": len(rules),
        "uncovered": uncovered,
        "uncovered_count": len(uncovered),
        "wrongly_treated": wrongly_treated,
        "wrongly_treated_count": len(wrongly_treated),
        "overreaching_rules": overreaching,
        "unused_rules": unused_rules,
        "entries": entries,
        "deliberately_unfiltered_prefixes": list(
            DELIBERATELY_UNFILTERED_HISTORICAL_PREFIXES
        ),
        "blocking_reason": None
        if satisfied
        else (
            "REPOSITORY_EOL_POLICY_INCOMPLETE: "
            f"{len(uncovered)} uncovered, {len(wrongly_treated)} wrongly "
            f"treated, {len(overreaching)} overreaching."
        ),
    }


def same_generation_advance_lawfulness(root: Path) -> dict[str, Any]:
    """Whether the current generation may still advance its candidate.

    A same-generation candidate advance is lawful only while this generation's
    single accepted-lifecycle record slot does not exist: once it does,
    advancing the candidate would mean mutating an accepted, frozen artifact.
    Re-derived from live state rather than asserted in prose.  Read-only.
    """

    root = Path(root).resolve()
    generation = CURRENT_GENERATION
    slot = generation.accepted_lifecycle_record_path
    slot_exists = (root / slot).is_file()
    return {
        "generation_id": generation.generation_id,
        "lineage_id": generation.lineage_id,
        "candidate_id": generation.candidate_id,
        "accepted_lifecycle_record_path": slot,
        "accepted_lifecycle_record_exists": slot_exists,
        "same_generation_advance_lawful": not slot_exists,
        "new_generation_created": False,
        "reason": (
            "This generation's single accepted-lifecycle record slot does not "
            "exist on disk, so a candidate advance mutates nothing accepted or "
            "frozen and every predecessor candidate artifact stays "
            "byte-identical."
            if not slot_exists
            else "An accepted-lifecycle record exists: a candidate advance "
            "within this generation would mutate accepted, frozen authority. A "
            "successor must open a NEW generation."
        ),
        "superseded_candidate_ids": list(generation.superseded_candidate_ids),
    }


#: How the canonical identity of each required durable-publication path is
#: established.  ``R4-AUD-01`` remediation: every live comparison names its
#: source, so no auditor has to guess what "matches canonical" was compared to.
DURABLE_IDENTITY_SOURCE_PIN = "AUTHORITY_BUNDLE_PIN"
DURABLE_IDENTITY_SOURCE_CHECKPOINT_FIELD = "MANIFEST_CANDIDATE_CHECKPOINT_FIELD"
DURABLE_IDENTITY_SOURCE_LEDGER_FIELD = "MANIFEST_CANDIDATE_CHANGE_LEDGER_FIELD"
DURABLE_IDENTITY_SOURCE_EXTERNAL = "EXTERNAL_LIFECYCLE_ROLE_BINDING"


def _manifest_artifact_binding(
    root: Path, generation: AuthorityGeneration, field: str, expected_path: str
) -> str | None:
    """The SHA-256 the current candidate manifest binds under ``field``, or None.

    The manifest field is the ONE authoritative location of that candidate
    artifact's identity.  Never raises: an absent, unreadable, duplicate-keyed
    or mis-targeted manifest yields ``None`` and the caller fails closed.
    """

    path = Path(root) / generation.candidate_manifest_path
    if not path.is_file():
        return None
    try:
        payload = _strict_json_object(
            path.read_bytes(), label=f"candidate manifest {field} binding"
        )
    except Exception:
        return None
    entry = payload.get(field)
    if not isinstance(entry, Mapping):
        return None
    if entry.get("path") != expected_path:
        return None
    digest = entry.get("sha256")
    if not isinstance(digest, str) or not _SHA256_RE.match(digest):
        return None
    return digest


def _manifest_checkpoint_binding(
    root: Path, generation: AuthorityGeneration | None = None
) -> str | None:
    """The checkpoint SHA-256 the current candidate manifest binds, or None."""

    generation = generation or CURRENT_GENERATION
    return _manifest_artifact_binding(
        root, generation, "candidate_checkpoint", generation.candidate_checkpoint_path
    )


def durable_publication_requirements(root: Path) -> dict[str, Any]:
    """Report publication durability of every required authority path.

    Read-only.  Never raises: a missing or mismatched path is reported, so a
    caller states the blocker instead of crashing.  Writes nothing, stages
    nothing, and commits nothing.

    This is the LIVE report.  Its status fields change as soon as the candidate
    is published, which is exactly why a candidate artifact must never freeze
    a copy of it (``R4-AUD-01``); a candidate manifest carries the static
    ``durable_publication_declaration`` instead.

    ``live_content_matches_canonical`` is a real raw-SHA-256 comparison against
    the source named in ``canonical_identity_source``.  It is never ``True``
    merely because a file exists:

    * pinned path - compared with its authority-bundle pin;
    * candidate checkpoint - compared with the candidate manifest's
      ``candidate_checkpoint.sha256``, its one authoritative location;
    * candidate change ledger - compared with the candidate manifest's
      ``candidate_change_ledger.sha256``, its one authoritative location;
    * candidate manifest - ``None`` (not applicable): its final identity
      cannot be embedded in its own bytes and is bound externally by the
      lifecycle role records, which compare it themselves.
    """

    root = root.resolve()
    generation = CURRENT_GENERATION
    expected_by_path = _required_durable_publication_sha256()
    checkpoint_binding = _manifest_checkpoint_binding(root, generation)
    ledger_binding = (
        _manifest_artifact_binding(
            root,
            generation,
            "candidate_change_ledger",
            generation.candidate_change_ledger_path,
        )
        if generation.candidate_change_ledger_path
        else None
    )
    entries: dict[str, Any] = {}
    satisfied = True
    for relative in REQUIRED_DURABLE_PUBLICATION_PATHS:
        path = root / relative
        live_sha = sha256_file(path) if path.is_file() else None
        head_sha = blob_sha256_at(root, "HEAD", relative)
        ignored = _is_path_ignored(root, relative)
        pinned = relative in REQUIRED_DURABLE_PUBLICATION_PIN_LABELS
        content_ok: bool | None
        if pinned:
            # A pinned path must match its pin exactly; an unresolvable expected
            # digest fails closed on both counts.
            source = DURABLE_IDENTITY_SOURCE_PIN
            expected = expected_by_path.get(relative)
            published = (
                expected is not None
                and head_sha is not None
                and head_sha == expected
            )
            content_ok = expected is not None and live_sha == expected
            comparison = "RAW_SHA256_EQUALITY_AGAINST_AUTHORITY_BUNDLE_PIN"
        elif relative == generation.candidate_checkpoint_path:
            source = DURABLE_IDENTITY_SOURCE_CHECKPOINT_FIELD
            expected = checkpoint_binding
            published = (
                live_sha is not None
                and head_sha is not None
                and head_sha == live_sha
            )
            # No readable manifest binding is a failure, not a pass.
            content_ok = expected is not None and live_sha == expected
            comparison = (
                "RAW_SHA256_EQUALITY_AGAINST_MANIFEST_CANDIDATE_CHECKPOINT_FIELD"
            )
        elif (
            generation.candidate_change_ledger_path
            and relative == generation.candidate_change_ledger_path
        ):
            source = DURABLE_IDENTITY_SOURCE_LEDGER_FIELD
            expected = ledger_binding
            published = (
                live_sha is not None
                and head_sha is not None
                and head_sha == live_sha
            )
            # No readable manifest binding is a failure, not a pass.
            content_ok = expected is not None and live_sha == expected
            comparison = (
                "RAW_SHA256_EQUALITY_AGAINST_MANIFEST_CANDIDATE_CHANGE_LEDGER_FIELD"
            )
        elif relative == generation.candidate_manifest_path:
            source = DURABLE_IDENTITY_SOURCE_EXTERNAL
            expected = None
            published = (
                live_sha is not None
                and head_sha is not None
                and head_sha == live_sha
            )
            content_ok = None
            comparison = (
                "NOT_APPLICABLE_FINAL_IDENTITY_BOUND_EXTERNALLY_BY_LIFECYCLE_ROLES"
            )
        else:  # pragma: no cover - every required path is classified above
            source = "UNCLASSIFIED"
            expected = None
            published = False
            content_ok = False
            comparison = "UNCLASSIFIED_REQUIRED_PATH_FAILS_CLOSED"
        if not published or content_ok is False:
            satisfied = False
        if ignored:
            requirement = (
                "MUST be included in the candidate publication commit at this "
                "exact canonical path, using a narrowly scoped `git add -f` "
                "while the path remains ignored. Content must NOT be modified "
                "and .gitignore must NOT be broadened."
            )
        else:
            requirement = (
                "MUST be included in the candidate publication commit at this "
                "exact canonical path. The path is not ignored, so no force-add "
                "is required. Content must NOT be modified."
            )
        entries[relative] = {
            "pinned": pinned,
            "pin_label": REQUIRED_DURABLE_PUBLICATION_PIN_LABELS.get(relative),
            "canonical_identity_source": source,
            "expected_sha256": expected,
            "live_present": live_sha is not None,
            "live_sha256": live_sha,
            "live_content_matches_canonical": content_ok,
            "live_content_comparison": comparison,
            "present_in_head": head_sha is not None,
            "head_sha256": head_sha,
            "published_durably": published,
            "ignored_by_gitignore": ignored,
            "force_add_required": ignored,
            "publication_requirement": requirement,
        }
    return {
        "required_paths": list(REQUIRED_DURABLE_PUBLICATION_PATHS),
        "force_add_paths": list(
            required_durable_publication_force_add_paths(root)
        ),
        "gitignore_rules_deliberately_unchanged": ["data/", "results/"],
        "entries": entries,
        "all_requirements_satisfied": satisfied,
        "missing_required_authority_files": sorted(
            rel for rel, e in entries.items() if not e["published_durably"]
        ),
        "remediates": "R2-AUD-01",
        "remediation_status": (
            "DECLARED_AND_ENFORCEABLE_PUBLICATION_NOT_YET_PERFORMED"
        ),
        "gitignore_modified": False,
        "canonical_content_modified": False,
        "non_authority_gitignored_runtime_dependencies": list(
            NON_AUTHORITY_GITIGNORED_RUNTIME_DEPENDENCIES
        ),
        "non_authority_gitignored_dependency_status": (
            NON_AUTHORITY_GITIGNORED_DEPENDENCY_STATUS
        ),
    }


# --- Pre-acceptance constants -------------------------------------------------
# Current factual pre-acceptance state only.  Every emitted field is read from
# the resolved lifecycle mapping, which replaces all of these with
# record-derived values once a valid accepted-lifecycle record exists.

PRE_ACCEPTANCE_ALIGNMENT_STATUS = "CANDIDATE"

#: The historical U-06 *alignment* candidate audit history: U-06 alignment
#: candidate R1 FAILED, candidate R2 returned NO-GO, candidate R3 was pending.
#:
#: This is retained verbatim and is NOT deleted -- it is the audit history of
#: the U-06 alignment generation and remains true of that generation.  It was
#: previously named ``PRE_ACCEPTANCE_AUDIT_STATUS`` and was emitted as the
#: ``u06_independent_audit_status`` of whatever generation happened to be
#: current, which is exactly independent-audit blocker ``R2-AUD-03`` (MAJOR /
#: BLOCKING): the active preflight-authorization-guard candidate's audit state
#: was reported as this unrelated historical string.
#:
#: It is now reachable only under explicitly historical keys and can never
#: again stand in for the active candidate's audit state.
HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS = "R1_FAILED_R2_NO_GO_R3_PENDING"

#: The pre-acceptance audit state of the CURRENT generation's OWN candidate,
#: derived from that generation rather than shared across generations.  For the
#: active generation this is candidate R3's state: ``NOT_YET_PERFORMED``.
PRE_ACCEPTANCE_AUDIT_STATUS = CURRENT_GENERATION.candidate_audit_state

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

#: ---------------------------------------------------------------------------
#: R2-AUD-03: the ACTIVE candidate generation's own audit history
#: ---------------------------------------------------------------------------
#:
#: The two records above (``CANDIDATE_R1_AUDIT_RECORD`` /
#: ``CANDIDATE_R2_AUDIT_RECORD``) are the audit history of the **U-06 alignment**
#: generation.  They are retained unchanged.  They are NOT the audit history of
#: the active Main Full81 preflight-authorization-guard generation, and the
#: independent audit of Candidate R2 found that the latter was being reported
#: using the former.
#:
#: This register is therefore explicitly namespaced to the active generation.
#: Every entry states all three lifecycle facts separately, so a passed audit
#: can never be read as a publication, and a publication can never be read as an
#: acceptance.
PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY: Mapping[str, Mapping[str, Any]] = {
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1": {
        "candidate_revision": "R1",
        "independent_audit": "PASS_WITH_NONBLOCKING_FINDINGS",
        "publication": "STOP",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "SUPERSEDED_HISTORICAL_PREDECESSOR_IMMUTABLE",
        "disposition_reason": (
            "Its independent logic audit PASSED (N-04 and N-05 both CLOSED / "
            "CORRECTION_VERIFIED) but its candidate-publication pass STOPPED on "
            "the I-04 Git clean-filter / EOL raw-byte incompatibility. It is "
            "superseded, NOT rejected."
        ),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r1_"
            "publication_stop_2026-10-04"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2": {
        "candidate_revision": "R2",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Its fresh independent audit returned FAIL / NO-GO on R2-AUD-01 "
            "(parameter registry absent from HEAD), R2-AUD-02 (no .gitattributes "
            "under core.autocrlf=true) and R2-AUD-03 (stale historical U-06 audit "
            "state reported as the current candidate's audit state). It is "
            "REJECTED, not merely superseded, and may never authorise."
        ),
        "blocking_findings": ("R2-AUD-01", "R2-AUD-02", "R2-AUD-03"),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r2_"
            "audit_stop_2026-10-04"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3": {
        "candidate_revision": "R3",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Bounded provenance/governance remediation of R2-AUD-01, R2-AUD-02 "
            "and R2-AUD-03. R2-AUD-01 was CORRECTION_VERIFIED, but its own "
            "fresh independent audit returned FAIL / NO-GO on R3-AUD-01 "
            "(stale/cyclic candidate checkpoint-manifest binding), R3-AUD-02 "
            "(twelve historical accepted-lifecycle artifacts omitted from the "
            "EOL policy), R3-AUD-03 (CRITICAL: the production bundle verifier "
            "never verified the repository-governance pin group it declared, "
            "and reported verified_pin_count from len(all_pins())), R2-AUD-03 "
            "(u06_register_entry still reported historical U-06 alignment "
            "ownership for the current candidate) and R3-AUD-04 (predecessor "
            "premises retained in the required validation surface). It is "
            "REJECTED, not merely superseded, and may never authorise."
        ),
        "blocking_findings": (
            "R3-AUD-01",
            "R3-AUD-02",
            "R3-AUD-03",
            "R2-AUD-03",
            "R3-AUD-04",
        ),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r3_"
            "audit_stop_2026-10-05"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4": {
        "candidate_revision": "R4",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Bounded remediation of the five Candidate R3 blockers. Its fresh "
            "independent audit verified the acyclic primary manifest-to-"
            "checkpoint binding, the 94-path EOL authority coverage and the "
            "34 / 34 declared-versus-verified pin parity, but returned FAIL / "
            "NO-GO on R4-AUD-01 (MAJOR): its manifest froze a snapshot of the "
            "LIVE durable-publication report, carrying stale live_sha256 values "
            "for the candidate checkpoint and for the manifest's own path while "
            "asserting live_content_matches_canonical=true and "
            "placeholder_or_stale_sha_used=false, and no production validator "
            "read those fields. It is REJECTED, not merely superseded, and may "
            "never authorise."
        ),
        "blocking_findings": ("R4-AUD-01",),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r4_"
            "audit_stop_2026-10-05"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5": {
        "candidate_revision": "R5",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Bounded remediation of R4-AUD-01. Its fresh independent audit "
            "returned FAIL / NO-GO on R5-AUD-01 (CRITICAL): the checkpoint "
            "identity guard proved only that each checkpoint digest occurred "
            "somewhere in the manifest, not that its stated role was the role "
            "of the manifest obligation owning it, so a lawful implementation "
            "digest under a 'Manifest SHA-256' label passed the GATE "
            "validator; and on R5-AUD-02 (MAJOR): a test-suite disposable-write "
            "helper did not keep its write target inside the disposable root. "
            "It is REJECTED, not merely superseded, and may never authorise."
        ),
        "blocking_findings": ("R5-AUD-01", "R5-AUD-02"),
        "nonblocking_findings": ("R5-AUD-03",),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r5_"
            "audit_stop_2026-10-05"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6": {
        "candidate_revision": "R6",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Bounded remediation of R5-AUD-01 and R5-AUD-02. Its fresh "
            "independent audit returned FAIL / NO-GO on R6-AUD-01 (CRITICAL): "
            "the GATE accepted preservation-package and predecessor identities "
            "structurally, without a value check, so the individually lawful "
            "R5 STOP archive and index digests swapped between their roles, "
            "with the canonical checkpoint claims rebound, still passed; and "
            "on R6-AUD-02 (MAJOR): the test-suite AST write guard missed unsafe "
            "writer patterns and disposable teardown could delete outside its "
            "root through a junction. It is REJECTED, not merely superseded, "
            "and may never authorise."
        ),
        "blocking_findings": ("R6-AUD-01", "R6-AUD-02"),
        "nonblocking_findings": ("R5-AUD-03",),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r6_"
            "audit_stop_2026-10-05"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7": {
        "candidate_revision": "R7",
        "independent_audit": "FAIL_NO_GO",
        "publication": "NOT_PERFORMED",
        "acceptance": "NOT_ACCEPTED",
        "disposition": "REJECTED_HISTORICAL_CANDIDATE_IMMUTABLE",
        "disposition_reason": (
            "Remediation of the R6-AUD-01 and R6-AUD-02 defect classes. Its "
            "fresh independent audit returned FAIL / NO-GO on R7-AUD-01 "
            "(CRITICAL): the production GATE's historical expected values were "
            "still candidate-controlled - pinned in candidate source and "
            "covered only by a recomputable implementation identity - so four "
            "independently constructed rebinding attacks (two roles swapped, a "
            "three-role cycle, a lawful historical digest substituted, the "
            "authority-bundle digest placed in a historical role) restored "
            "GATE PASS after every candidate-controlled identity was "
            "recomputed. R6-AUD-01 was therefore not closed, and the R6-AUD-02 "
            "remediation it claimed was never independently verified. It is "
            "REJECTED, not merely superseded, and may never authorise."
        ),
        "blocking_findings": ("R7-AUD-01",),
        "preservation_package": (
            "results/provenance/"
            "main_full81_preflight_authorization_guard_candidate_r7_"
            "audit_stop_2026-10-06"
        ),
    },
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8": {
        "candidate_revision": "R8",
        "independent_audit": "NOT_YET_PERFORMED",
        "publication": "NOT_YET_AUTHORIZED",
        "acceptance": "NOT_YET_ACCEPTED",
        "disposition": "ACTIVE_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT",
        "disposition_reason": (
            "Bounded repair of the R6-AUD-01 defect class as R7-AUD-01 exposed "
            "it, and nothing else: in every mode the GATE derives every "
            "historical role value, and the predecessor change set, from "
            "externally authenticated evidence - the Git-frozen pre-R8 "
            "historical trust root, the accepted R7 Preservation Authority "
            "Binding it pins, and the authenticated R7 preservation package - "
            "and a candidate-local historical table is only a diagnostic "
            "assertion that must equal that derivation, with no fallback "
            "(contract V4). R6-AUD-02 is carried unchanged and out of scope. "
            "The repair is IMPLEMENTED and NOT_YET_INDEPENDENTLY_VERIFIED. The "
            "next lawful gate is a fresh independent read-only audit."
        ),
        "remediates": ("R6-AUD-01", "R7-AUD-01"),
    },
}
#: The register above is the generation-3 (preflight-authorization-guard)
#: register exactly as candidate R8 declared it.  It is retained unchanged
#: because the contract-V4 validator replays the R8 manifest and ledger
#: against it, so its R8 entry records the CANDIDATE-TIME state that R8's own
#: artifacts state.  R8's later independent audit PASS, acceptance and re-freeze
#: are proved by its published accepted-lifecycle record, not by this register,
#: and generation 3 is now historical.

#: Current Full81 Production Generation G1: its own candidate audit register,
#: namespaced to G1 exactly as ``R2-AUD-03`` requires.  Every entry states the
#: audit, publication and acceptance facts separately.
G1_CANDIDATE_AUDIT_HISTORY: Mapping[str, Mapping[str, Any]] = {
    "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1": {
        "candidate_revision": "R1",
        "independent_audit": "NOT_YET_PERFORMED",
        "publication": "NOT_YET_AUTHORIZED",
        "acceptance": "NOT_YET_ACCEPTED",
        "disposition": "ACTIVE_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT",
        "disposition_reason": (
            "Consolidation of the current Full81 production runtime, validation "
            "and governance-authority identities into one additive generation "
            "with its own content contract, predeclared governance paths, a "
            "relocated Main Full81 scope-authorization slot and a fail-closed "
            "execution-authorization guard. It is IMPLEMENTED and "
            "NOT_YET_INDEPENDENTLY_VERIFIED. The next lawful gate is a fresh "
            "independent read-only audit."
        ),
    },
}

#: Candidate audit registers, one per generation that has one.  Generations 1
#: and 2 pre-date per-generation registers and declare their audit state on the
#: generation itself.
CANDIDATE_AUDIT_REGISTERS: Mapping[str, Mapping[str, Mapping[str, Any]]] = {
    FULL81_PREFLIGHT_AUTH_GUARD_R1_GENERATION.generation_id: (
        PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY
    ),
    G1_GENERATION.generation_id: G1_CANDIDATE_AUDIT_HISTORY,
}

#: The CURRENT generation's own register.  Every emitted "active candidate"
#: field is read from this and from nothing else.
CURRENT_CANDIDATE_AUDIT_HISTORY: Mapping[str, Mapping[str, Any]] = (
    CANDIDATE_AUDIT_REGISTERS.get(CURRENT_GENERATION.generation_id, {})
)

#: The one candidate of the active generation whose audit state the generic
#: ``u06_independent_audit_status`` field must resolve to.
ACTIVE_CANDIDATE_ID = CURRENT_GENERATION.candidate_id

#: Fail-closed structural guards for ``R2-AUD-03``.  These run at import time so
#: the defect cannot be reintroduced silently by a later edit.
#:
#: 1. The active candidate must be declared in its own generation's register.
#: 2. A generation may never self-declare an audit ``PASS``: a real ``PASS`` is
#:    proved only by a published accepted-lifecycle record, which the role
#:    validators verify independently.
#: 3. The historical U-06 alignment audit string may never be the active
#:    candidate's audit state.
if ACTIVE_CANDIDATE_ID not in CURRENT_CANDIDATE_AUDIT_HISTORY:
    raise AssertionError(
        "R2-AUD-03 regression: the active candidate "
        f"{ACTIVE_CANDIDATE_ID!r} has no entry in its own generation's "
        "candidate audit register."
    )
if CURRENT_GENERATION.candidate_audit_state == ACCEPTED_AUDIT_STATUS:
    raise AssertionError(
        "R2-AUD-03 regression: the current generation self-declares audit "
        f"{ACCEPTED_AUDIT_STATUS!r}. An audit PASS must be proved by a "
        "published accepted-lifecycle record, never declared in source."
    )
if PRE_ACCEPTANCE_AUDIT_STATUS == HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS:
    raise AssertionError(
        "R2-AUD-03 regression: the active candidate's audit state is the "
        "historical U-06 alignment audit history "
        f"{HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS!r}."
    )
if (
    CURRENT_CANDIDATE_AUDIT_HISTORY[ACTIVE_CANDIDATE_ID]["independent_audit"]
    != PRE_ACCEPTANCE_AUDIT_STATUS
):
    raise AssertionError(
        "R2-AUD-03 regression: the emitted pre-acceptance audit state and the "
        "active candidate's register entry disagree."
    )


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

    That agreement used to be an unenforced assumption, and ``R2-AUD-02``
    escalated it to a BLOCKING defect: under ``core.autocrlf=true`` with no
    ``.gitattributes``, a clean checkout smudged LF blobs to CRLF working-tree
    bytes, so the two diverged and every authority check failed closed on a
    correct repository.  The Candidate R3 ``.gitattributes`` policy now pins the
    checkout form of each authority-critical path explicitly, which is what
    makes this equality hold by construction instead of by luck.
    """

    done = _git(root, "cat-file", "-e", f"{commit}:{relative}")
    if done.returncode != 0:
        return None
    blob = _git(root, "cat-file", "blob", f"{commit}:{relative}")
    if blob.returncode != 0:
        return None
    return hashlib.sha256(blob.stdout).hexdigest()


def _is_path_ignored(root: Path, relative: str) -> bool:
    """True when `relative` is matched by an ignore rule.

    Used only to report whether a required durable-publication path still needs
    a narrowly scoped force-add (``R2-AUD-01``).  Git reports an already-tracked
    path as not ignored, which is the desired semantics here: once the path is
    published, no force-add is required any more.
    """

    return _git(root, "check-ignore", "-q", "--", relative).returncode == 0


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


def _strict_json_object(raw: bytes, *, label: str) -> dict[str, Any]:
    """Parse ``raw`` as a JSON object, REJECTING duplicate object keys.

    ``R4-AUD-01`` hardening, scoped to the candidate-manifest contract only
    (design observation ``N-R5D-03``).  ``json.loads`` silently keeps the LAST
    of two duplicate keys, so a human reading the file and the validator
    parsing it could see different values for the same field.  The generic
    :func:`_read_json` is deliberately left unchanged: its historical callers
    are not re-judged by a stricter parser.
    """

    def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise U06LifecycleError(
                    "U06_ROLE_SCHEMA_INVALID",
                    f"{label}: duplicate JSON object key {key!r}. A reader and "
                    "json.loads would see different values for that field, so "
                    "the record is not a single unambiguous claim.",
                )
            out[key] = value
        return out

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise U06LifecycleError(
            "U06_ROLE_ARTIFACT_NOT_JSON",
            f"{label}: not UTF-8 ({exc}).",
        ) from exc
    try:
        payload = json.loads(text, object_pairs_hook=_no_duplicates)
    except U06LifecycleError:
        raise
    except Exception as exc:
        raise U06LifecycleError(
            "U06_ROLE_ARTIFACT_NOT_JSON",
            f"{label}: not machine-readable JSON ({exc}).",
        ) from exc
    _require(
        isinstance(payload, dict),
        "U06_ROLE_ARTIFACT_NOT_JSON",
        f"{label}: not a JSON object.",
    )
    return payload


def _validate_role_path(
    role: str,
    relative: str,
    record_relative: str,
    generation: AuthorityGeneration | None = None,
) -> None:
    generation = generation or CURRENT_GENERATION
    normalized = relative.replace("\\", "/").strip()
    _require(
        bool(normalized) and not normalized.startswith("/"),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"Role {role!r} has an unusable path: {relative!r}",
    )
    if role == "implementation_candidate":
        _require(
            normalized == generation.candidate_manifest_path,
            "U06_ROLE_TARGET_MISMATCH",
            f"The implementation-candidate role of generation "
            f"{generation.generation_id} must be its candidate manifest "
            f"{generation.candidate_manifest_path}; observed {normalized}.",
        )
        return
    _require(
        normalized not in generation.candidate_artifact_paths,
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
    # G1: a generation that predeclared its role-record paths accepts each role
    # ONLY at its predeclared path, so no role can be filled by a file that has
    # no exact-path EOL rule or that sits outside the declared namespace.
    predeclared = generation.role_record_path_map
    if predeclared is not None:
        _require(
            normalized == predeclared.get(role),
            "U06_ROLE_TARGET_MISMATCH",
            f"Role {role!r} of generation {generation.generation_id} must be "
            f"published at its predeclared path {predeclared.get(role)}; "
            f"observed {normalized}.",
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
    generation: AuthorityGeneration | None = None,
) -> dict[str, Any]:
    """Validate the common lineage/type/target envelope of one role record.

    ``generation`` selects the authority generation whose contract applies.
    Omitting it uses :data:`CURRENT_GENERATION`, so an omission can never let a
    superseded generation authorise anything.
    """

    generation = generation or CURRENT_GENERATION
    contract = generation.role_contracts[role]
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
        payload.get("lineage_id") == generation.lineage_id,
        "U06_LINEAGE_MISMATCH",
        f"{label}: lineage_id must be {generation.lineage_id!r} for generation "
        f"{generation.generation_id}; observed {payload.get('lineage_id')!r}",
    )
    target = payload.get("target_candidate_id")
    _require(
        target not in generation.superseded_candidate_ids,
        "U06_SUPERSEDED_CANDIDATE_REJECTED",
        f"{label}: target_candidate_id {target!r} names a superseded candidate "
        f"of generation {generation.generation_id}. A failed candidate may "
        "never be revived.",
    )
    _require(
        target == generation.candidate_id,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: target_candidate_id must be {generation.candidate_id!r}; "
        f"observed {target!r}",
    )

    checkpoint_rel, checkpoint_sha = _declared_identity(
        payload, "candidate_checkpoint", label=label
    )
    _require(
        checkpoint_rel == generation.candidate_checkpoint_path,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_checkpoint must be "
        f"{generation.candidate_checkpoint_path}; observed {checkpoint_rel}",
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
            manifest_rel == generation.candidate_manifest_path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: candidate_manifest must be "
            f"{generation.candidate_manifest_path}; observed {manifest_rel}",
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
        "generation_id": generation.generation_id,
        "artifact_type": contract.artifact_type,
        "schema_version": contract.schema_version,
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
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
    generation: AuthorityGeneration | None = None,
) -> None:
    """Require this role to bind the exact identity of every earlier role."""

    generation = generation or CURRENT_GENERATION
    contract = generation.role_contracts[role]
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


# ---------------------------------------------------------------------------
# R4-AUD-01: the closed-world candidate-manifest identity contract
# ---------------------------------------------------------------------------
#
# Candidate R4 received ``FAIL / NO-GO`` on ``R4-AUD-01`` (MAJOR / BLOCKING).
# Its primary manifest -> checkpoint binding was correct and acyclic, but the
# same manifest froze a snapshot of the LIVE durable-publication report taken
# before the checkpoint and the manifest were final.  It therefore recorded a
# stale ``live_sha256`` for the checkpoint and - unsatisfiably - for the
# manifest's OWN path, asserted ``live_content_matches_canonical = true`` for
# both, and asserted ``placeholder_or_stale_sha_used = false``.  The
# implementation-candidate role was validated by its envelope only, so none of
# those fields was ever checked.
#
# The remedy has three parts, none of which adds an artifact:
#
# 1. The manifest DECLARES (``durable_publication_declaration``) and never
#    snapshots: which paths must be published and where each path's canonical
#    identity comes from.  Live status belongs to the live report alone.
# 2. The manifest's OWN final identity is never embedded in its own bytes.  It
#    is bound externally by the lifecycle role records that already declare
#    ``candidate_manifest`` and by the accepted-lifecycle record's
#    ``roles.implementation_candidate`` entry; the manifest only names those
#    binding fields.
# 3. Every embedded raw SHA-256 is CLOSED-WORLD: discovered by semantic JSON
#    traversal, owned by exactly one declared obligation, and either verified
#    or (for ignored, unpublished provenance at the gate) explicitly
#    structural.  Collected == verified UNION structural, or the contract
#    fails.  Any raw-hash cycle, self-hash or placeholder necessarily leaves a
#    stale embedded value, so closed-world verification is what makes "no
#    cycle" a checked fact rather than a self-label.
#
# Candidate R5 then received ``FAIL / NO-GO`` on ``R5-AUD-01`` (CRITICAL):
# the checkpoint side of that closed world checked VALUE MEMBERSHIP only.  A
# checkpoint digest had merely to occur somewhere in the manifest, so a lawful
# implementation digest printed under a "Manifest SHA-256" label passed.  The
# defect class is "an identity claim whose ROLE is not verified", and a label
# can never be the thing that is verified.  Contract V2 therefore removes
# labels from the trust path altogether:
#
# 4. A checkpoint may state a raw identity ONLY as a canonical claim
#    ``<RFC 6901 manifest pointer> <digest>`` inside an ``identity-claims``
#    block.  The pointer names the manifest identity field - and through it
#    the single obligation - that owns the value, and the claim passes only if
#    the manifest holds exactly that digest at exactly that pointer.  A digest
#    anywhere else (prose, tables, headings, other blocks) is unclassified and
#    fails, whatever label surrounds it.  The same digest may be claimed under
#    two pointers only where the manifest itself lawfully holds it at both.
# 5. The candidate change ledger is bound by the manifest (``C9``) and is
#    itself closed-world: every identity it states is owned by one ledger
#    obligation and verified, so the traceability record cannot become the
#    next unvalidated identity surface.
#
# Candidate R6 then received ``FAIL / NO-GO`` on ``R6-AUD-01`` (CRITICAL):
# part 3's "explicitly structural" class was itself the hole.  In GATE mode a
# structural identity was never value-checked, and part 4 compared a claim with
# the manifest's own value, so a consistent permutation of individually lawful
# digests between roles - claims rebound to match - passed.  Contract V3
# replaces parts 3 and 4 (see "closed-world semantic role binding" below):
#
# 3'. Every embedded raw SHA-256 is owned by one obligation of the closed-world
#     role schema and BOUND, in every mode, to one role whose value is
#     established independently of the candidate artifacts.  Collected ==
#     bound, or the contract fails; the structural class no longer exists.
# 4'. A checkpoint claim must equal the BOUND authority value of the pointer
#     it names - never merely the manifest's bytes at that pointer.

#: Validation modes.  ``GATE`` is what the production lifecycle path runs:
#: every identity is bound to its role's independent authority value, and
#: (contract V4) every historical identity to the value derived from the
#: EXTERNAL historical authority - the Git-frozen pre-R8 trust root, the
#: accepted R7 binding it pins and the authenticated R7 preservation package
#: - which must be present or the GATE fails closed.  ``CANDIDATE_PACKAGE``
#: runs the same derivation and additionally proves that the R1-R7 files the
#: historical values describe are live in the candidate working tree; it is
#: what candidate-era validation and an independent audit run.  Neither mode
#: ever accepts an identity structurally or takes a historical value from
#: candidate-controlled material.
CANDIDATE_MANIFEST_MODE_GATE = "GATE"
CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE = "CANDIDATE_PACKAGE"
CANDIDATE_MANIFEST_MODES: tuple[str, ...] = (
    CANDIDATE_MANIFEST_MODE_GATE,
    CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE,
)

#: Top-level field classes.  Every top-level key of the candidate manifest has
#: exactly one class; an unclassified key fails closed.
FIELD_CLASS_IDENTITY = "IDENTITY"
FIELD_CLASS_CONSTANT = "CONSTANT"
FIELD_CLASS_OBSERVATION = "OBSERVATION_AT_CONSTRUCTION"
FIELD_CLASS_PROSE = "PROSE"

CANDIDATE_MANIFEST_FIELD_CLASSES: Mapping[str, str] = {
    "schema_version": FIELD_CLASS_CONSTANT,
    "artifact_type": FIELD_CLASS_CONSTANT,
    "role": FIELD_CLASS_CONSTANT,
    "candidate_manifest_contract": FIELD_CLASS_CONSTANT,
    "date": FIELD_CLASS_OBSERVATION,
    "generation_id": FIELD_CLASS_CONSTANT,
    "lineage_id": FIELD_CLASS_CONSTANT,
    "candidate_id": FIELD_CLASS_CONSTANT,
    "target_candidate_id": FIELD_CLASS_CONSTANT,
    "candidate_revision": FIELD_CLASS_CONSTANT,
    "scope": FIELD_CLASS_PROSE,
    "disposition": FIELD_CLASS_CONSTANT,
    "self_accepted": FIELD_CLASS_CONSTANT,
    "package_binding": FIELD_CLASS_IDENTITY,
    "candidate_checkpoint_path": FIELD_CLASS_CONSTANT,
    "candidate_checkpoint": FIELD_CLASS_IDENTITY,
    "candidate_manifest_path": FIELD_CLASS_CONSTANT,
    "implementation_identity_digest": FIELD_CLASS_IDENTITY,
    "implementation_identity": FIELD_CLASS_IDENTITY,
    "generation_advance_lawfulness_at_construction": FIELD_CLASS_OBSERVATION,
    "authority_bundle": FIELD_CLASS_IDENTITY,
    "repository_eol_policy": FIELD_CLASS_IDENTITY,
    "parameter_registry_durability": FIELD_CLASS_IDENTITY,
    "durable_publication_declaration": FIELD_CLASS_IDENTITY,
    "candidate_preservation_packages": FIELD_CLASS_IDENTITY,
    "candidate_change_ledger": FIELD_CLASS_IDENTITY,
    #: Candidate R8 (contract V4): the external historical authority this
    #: candidate consumes, by frozen Git identity and binding locator only (no
    #: SHA-256: the binding digest is stated by the trust root alone).  A
    #: CONSTANT checked against the live authenticated chain, never a source.
    "external_historical_authority": FIELD_CLASS_CONSTANT,
    "predecessor_candidates": FIELD_CLASS_OBSERVATION,
    "lifecycle_state": FIELD_CLASS_OBSERVATION,
    "accepted_lifecycle_record_path": FIELD_CLASS_CONSTANT,
    "remediation": FIELD_CLASS_OBSERVATION,
    "carried_findings": FIELD_CLASS_OBSERVATION,
    "mutation_counters": FIELD_CLASS_OBSERVATION,
    "execution_counters": FIELD_CLASS_OBSERVATION,
    "repository_head_at_authoring": FIELD_CLASS_OBSERVATION,
    "next_legal_gate": FIELD_CLASS_PROSE,
}

#: Keys that are forbidden ANYWHERE in a candidate manifest.  They are the
#: frozen live-report fields and the hand-set identity self-labels of the R4
#: schema: each one is either time-variant (its truth changes when the
#: candidate is published) or a boolean claim that only a validator may make.
#: The validator computes the honest equivalents and reports them instead.
CANDIDATE_MANIFEST_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "required_durable_publication",
        "live_sha256",
        "head_sha256",
        "live_present",
        "present_in_head",
        "published_durably",
        "ignored_by_gitignore",
        "force_add_required",
        "force_add_paths",
        "all_requirements_satisfied",
        "live_content_matches_canonical",
        "missing_required_authority_files",
        "accepted_lifecycle_record_exists",
        "placeholder_or_stale_sha_used",
        "manifest_records_own_sha256",
        "checkpoint_records_manifest_raw_sha256",
        "mutual_raw_hash_cycle_present",
        "manifest_binds_checkpoint_path",
        "manifest_binds_checkpoint_raw_sha256",
        "checkpoint_names_manifest_path",
        "placeholder_digests_used",
        "fabricated_future_hashes",
    }
)

PACKAGE_BINDING_SCHEME = "ACYCLIC_MANIFEST_TO_CHECKPOINT_ONLY"
PACKAGE_BINDING_DIRECTION = "manifest -> checkpoint"
PACKAGE_BINDING_KEYS: frozenset[str] = frozenset(
    {"scheme", "direction", "manifest_self_identity", "rationale", "predecessor_defect"}
)

DURABLE_DECLARATION_SEMANTICS = "STATIC_DECLARATION_NOT_A_LIVE_SNAPSHOT"
DURABLE_DECLARATION_LIVE_STATUS_SOURCE = (
    "src.production_authority_lifecycle_u06.durable_publication_requirements"
)
DURABLE_DECLARATION_KEYS: frozenset[str] = frozenset(
    {"semantics", "live_status_source", "required_paths", "entries"}
)
DURABLE_CHECKPOINT_IDENTITY_FIELD = "candidate_checkpoint.sha256"
DURABLE_LEDGER_IDENTITY_FIELD = "candidate_change_ledger.sha256"

#: The predecessor-defect evidence contract V4 requires: the IMMEDIATE
#: predecessor, Candidate R7, and its blocking finding.  Recorded as typed
#: HISTORICAL evidence, never as a binding.  R7's defect lay in validator CODE
#: (where the GATE took historical values from), not in identity values its
#: artifacts recorded, so there is no stale-value list to carry.
PREDECESSOR_DEFECT_EVIDENCE_CLASS = (
    "HISTORICAL_PREDECESSOR_DEFECT_EVIDENCE_NOT_A_LIVE_BINDING"
)
PREDECESSOR_DEFECT_LOCATION_CODE = (
    "PRODUCTION_VALIDATOR_AND_TEST_CODE_NOT_RECORDED_IDENTITY_VALUES"
)
CONTRACT_V4_PREDECESSOR_DEFECT: Mapping[str, Any] = {
    "findings": ("R7-AUD-01",),
    "predecessor_candidate_id": (
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7"
    ),
    "checkpoint_path": FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_CHECKPOINT_PATH,
    "manifest_path": FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_R7_MANIFEST_PATH,
}
PREDECESSOR_DEFECT_KEYS: frozenset[str] = frozenset(
    {
        "findings",
        "predecessor_candidate_id",
        "evidence_class",
        "predecessor_candidate_checkpoint",
        "predecessor_candidate_manifest",
        "defect_location",
        "recorded_in_stop_record",
    }
)

IMPLEMENTATION_IDENTITY_KEYS: frozenset[str] = frozenset(
    {
        "path_count",
        "derivation",
        "digest_algorithm",
        "implementation_digest",
        "paths",
        "predecessor_digest",
        "predecessor_digest_carried_forward",
    }
)
AUTHORITY_BUNDLE_KEYS: frozenset[str] = frozenset(
    {"declared_pin_groups", "declared_pin_count", "pins"}
)
REPOSITORY_EOL_POLICY_KEYS: frozenset[str] = frozenset(
    {
        "path",
        "sha256",
        "bundle_pin_label",
        "coverage_at_construction",
        "historical_blobs_normalized",
        "renormalize_run",
        "core_autocrlf_changed",
    }
)
PARAMETER_REGISTRY_DURABILITY_KEYS: frozenset[str] = frozenset(
    {
        "path",
        "canonical_sha256",
        "bundle_pin_label",
        "eol_rule",
        "canonical_eol_class",
        "scientific_content_modified",
        "r2_aud_01_status",
    }
)
PRESERVATION_ENTRY_KEYS: frozenset[str] = frozenset(
    {
        "directory",
        "stop_class",
        "archive_path",
        "archive_sha256",
        "index_path",
        "index_sha256",
        "stop_record_path",
        "stop_record_sha256",
    }
)


#: ``R6-AUD-01``: where a role's authoritative value comes from.  Every source is
#: independent of the candidate artifacts being validated, and every one is
#: available in EVERY validation mode, so no identity is ever accepted on
#: structure alone.  ``R7-AUD-01`` / contract V4: historical role values are
#: no longer pinned in candidate source.  They come from the EXTERNAL historical
#: authority (:func:`resolve_external_historical_authority`: Git-frozen trust
#: root -> accepted R7 binding -> authenticated R7 preservation package) in
#: every mode; ``CANDIDATE_PACKAGE`` mode additionally proves that the R1-R7
#: files those values describe are live.
AUTHORITY_LIVE_RAW_BYTES = "LIVE_RAW_BYTES"
AUTHORITY_LIVE_IMPLEMENTATION = "LIVE_IMPLEMENTATION_IDENTITY"
AUTHORITY_BUNDLE_PIN = "AUTHORITY_BUNDLE_PIN"
AUTHORITY_HISTORICAL_ROLE = "EXTERNAL_HISTORICAL_AUTHORITY"
IDENTITY_AUTHORITY_SOURCES: tuple[str, ...] = (
    AUTHORITY_LIVE_RAW_BYTES,
    AUTHORITY_LIVE_IMPLEMENTATION,
    AUTHORITY_BUNDLE_PIN,
    AUTHORITY_HISTORICAL_ROLE,
)


@dataclass(frozen=True)
class IdentityObligation:
    """One semantic role class of embedded raw-SHA-256 identity pointers.

    ``pattern`` is a JSON-pointer pattern in which ``"*"`` matches exactly one
    key or list index.  ``authority`` names the independent source of the
    role's expected value.  Contract V2 carried a ``scope`` here - the weakest
    mode in which the obligation was verified, with STRUCTURAL acceptance in a
    weaker one.  That was ``R6-AUD-01``; contract V3 has no such field.
    """

    obligation_class: str
    kind: str
    pattern: tuple[str, ...]
    authority: str
    description: str


#: THE single declaration of what may carry an embedded raw SHA-256 in a
#: candidate manifest - the closed-world semantic role schema.  ``C8`` (the
#: manifest's own identity) has no pattern: it is forbidden, and enforced
#: structurally before any obligation runs.
CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS: tuple[IdentityObligation, ...] = (
    IdentityObligation(
        "C1", "candidate_checkpoint", ("candidate_checkpoint", "sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Candidate checkpoint raw SHA-256: the one embedded checkpoint identity.",
    ),
    IdentityObligation(
        "C2", "implementation_digest", ("implementation_identity_digest",),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "Live accepted implementation identity digest.",
    ),
    IdentityObligation(
        "C2", "implementation_digest",
        ("implementation_identity", "implementation_digest"),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "The same digest, which must also reproduce from the paths map.",
    ),
    IdentityObligation(
        "C3", "implementation_paths", ("implementation_identity", "paths", "*"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Raw SHA-256 of every accepted implementation path.",
    ),
    IdentityObligation(
        "C4", "bundle_pins", ("authority_bundle", "pins", "*", "sha256"),
        AUTHORITY_BUNDLE_PIN,
        "Every authority-bundle pin, equal to the bundle's own constant.",
    ),
    IdentityObligation(
        "C4", "bundle_pins", ("repository_eol_policy", "sha256"),
        AUTHORITY_BUNDLE_PIN,
        "The repository_eol_policy pin, restated.",
    ),
    IdentityObligation(
        "C4", "bundle_pins", ("parameter_registry_durability", "canonical_sha256"),
        AUTHORITY_BUNDLE_PIN,
        "The parameter_registry pin, restated.",
    ),
    IdentityObligation(
        "C5", "durable_pinned",
        ("durable_publication_declaration", "entries", "*", "expected_raw_sha256"),
        AUTHORITY_BUNDLE_PIN,
        "Static durable-publication declaration: pinned paths only.",
    ),
    IdentityObligation(
        "C6", "preservation",
        ("candidate_preservation_packages", "*", "archive_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor preservation archive, per its external historical role.",
    ),
    IdentityObligation(
        "C6", "preservation",
        ("candidate_preservation_packages", "*", "index_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor preservation raw-byte index, per its external historical role.",
    ),
    IdentityObligation(
        "C6", "preservation",
        ("candidate_preservation_packages", "*", "stop_record_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor preservation STOP record, per its external historical role.",
    ),
    IdentityObligation(
        "C7", "predecessor_evidence", ("implementation_identity", "predecessor_digest"),
        AUTHORITY_HISTORICAL_ROLE,
        "Historical predecessor implementation digest.",
    ),
    IdentityObligation(
        "C7", "predecessor_evidence",
        ("package_binding", "predecessor_defect",
         "predecessor_candidate_checkpoint", "raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Historical predecessor checkpoint raw SHA-256.",
    ),
    IdentityObligation(
        "C7", "predecessor_evidence",
        ("package_binding", "predecessor_defect",
         "predecessor_candidate_manifest", "raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Historical predecessor manifest raw SHA-256.",
    ),
    IdentityObligation(
        "C9", "candidate_change_ledger", ("candidate_change_ledger", "sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Candidate change ledger raw SHA-256; the ledger is then validated.",
    ),
)

#: The forbidden identity class, enforced before any obligation runs.
CANDIDATE_MANIFEST_FORBIDDEN_IDENTITY_CLASS = "C8"

_HEX_RUN_RE = re.compile(r"[0-9a-fA-F]{64,}")
_SHA256_VALUE_RE = re.compile(r"^[0-9a-f]{64}$")


def candidate_manifest_external_binding_fields(
    generation: AuthorityGeneration | None = None,
) -> tuple[str, ...]:
    """Where the candidate manifest's final identity is bound, outside itself.

    Derived from the generation's own role contracts, so it cannot drift from
    what the lifecycle validator actually requires.
    """

    generation = generation or CURRENT_GENERATION
    fields = [
        f"{role}.candidate_manifest.sha256"
        for role, contract in generation.role_contracts.items()
        if contract.declares_candidate_manifest
    ]
    fields.append("accepted_lifecycle_record.roles.implementation_candidate.sha256")
    return tuple(fields)


def _required_durable_paths_for(generation: AuthorityGeneration) -> tuple[str, ...]:
    return (
        *REQUIRED_DURABLE_PUBLICATION_PIN_LABELS,
        generation.candidate_checkpoint_path,
        generation.candidate_manifest_path,
        *(
            (generation.candidate_change_ledger_path,)
            if generation.candidate_change_ledger_path
            else ()
        ),
    )


def rfc6901_pointer(pointer: Sequence[Any]) -> str:
    """Canonical RFC 6901 encoding of a JSON pointer tuple.

    ``~`` is written ``~0`` and ``/`` is written ``~1``; list indices are
    decimal.  This is the ONLY spelling a checkpoint identity claim may use, so
    one manifest identity field has exactly one claimable name.
    """

    return "".join(
        "/" + (str(s) if isinstance(s, int) else s.replace("~", "~0").replace("/", "~1"))
        for s in pointer
    )


def collect_identity_pointers(
    payload: Any,
) -> tuple[list[tuple[tuple[Any, ...], str]], list[tuple[Any, ...]]]:
    """Semantically collect every embedded raw-SHA-256 identity in ``payload``.

    Returns ``(identity_pointers, hidden_pointers)``.  An identity pointer is a
    string value that is exactly a lowercase 64-hex digest.  A hidden pointer
    is any key or string carrying a run of 64+ hex characters that is NOT
    exactly such a value - a digest buried in prose, an uppercase digest, or a
    key - which can never be owned by an obligation.
    """

    identities: list[tuple[tuple[Any, ...], str]] = []
    hidden: list[tuple[Any, ...]] = []

    def walk(node: Any, pointer: tuple[Any, ...]) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if isinstance(key, str) and _HEX_RUN_RE.search(key):
                    hidden.append(pointer + (key,))
                walk(value, pointer + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, pointer + (index,))
        elif isinstance(node, str):
            if _SHA256_VALUE_RE.match(node):
                identities.append((pointer, node))
            elif _HEX_RUN_RE.search(node):
                hidden.append(pointer)

    walk(payload, ())
    return identities, hidden


def _pointer_matches(pattern: Sequence[Any], pointer: Sequence[Any]) -> bool:
    return len(pattern) == len(pointer) and all(
        p == "*" or p == q for p, q in zip(pattern, pointer)
    )


def _resolve_pointer(payload: Any, pointer: Sequence[Any]) -> Any:
    node = payload
    for segment in pointer:
        if isinstance(node, Mapping) and segment in node:
            node = node[segment]
        elif (
            isinstance(node, list)
            and isinstance(segment, int)
            and not isinstance(segment, bool)
            and 0 <= segment < len(node)
        ):
            node = node[segment]
        else:
            raise KeyError(tuple(pointer))
    return node


def _associated_paths(payload: Mapping[str, Any], pointer: Sequence[Any]) -> set[str]:
    """Every repository path an identity pointer is semantically tied to.

    The pointer's own key segments plus the direct string values of every
    enclosing object below the root.  The root is excluded on purpose: it
    names the manifest's own path as plain metadata, which ties no digest.
    """

    associated = {segment for segment in pointer if isinstance(segment, str)}
    node: Any = payload
    for segment in pointer[:-1]:
        node = node[segment]
        if isinstance(node, Mapping):
            associated.update(v for v in node.values() if isinstance(v, str))
    return associated


def _identity_target_path(payload: Mapping[str, Any], pointer: Sequence[Any]) -> str | None:
    """The live artifact path an identity pointer claims the digest OF."""

    leaf = pointer[-1]
    parent = _resolve_pointer(payload, pointer[:-1])
    if tuple(pointer[:2]) in (
        ("implementation_identity", "paths"),
        ("durable_publication_declaration", "entries"),
    ):
        return str(pointer[2])
    if pointer[0] == "candidate_preservation_packages" and isinstance(leaf, str):
        value = parent.get(leaf[: -len("_sha256")] + "_path")
        return value if isinstance(value, str) else None
    if leaf == "recorded_value":
        # A stale value the predecessor recorded.  It intentionally differs from
        # the actual digest, so it is not an identity OF any live path.
        return None
    if leaf == "actual_raw_sha256_of_described_path":
        value = parent.get("describes_path")
        return value if isinstance(value, str) else None
    if isinstance(parent, Mapping) and isinstance(parent.get("path"), str):
        return parent["path"]
    return None


# ---------------------------------------------------------------------------
# R6-AUD-01: closed-world semantic role binding
# ---------------------------------------------------------------------------
#
# Candidate R6 received ``FAIL / NO-GO`` on ``R6-AUD-01`` (CRITICAL).  Contract
# V2 let an obligation be "not verified in this mode": in GATE mode the
# preservation-package and predecessor identities were accepted on STRUCTURE
# alone, and a checkpoint claim only had to equal the manifest's own value at
# its pointer.  So a package in which every digest was individually lawful and
# every referenced object existed - but two digests had swapped roles, with the
# claims rebound to match - reached PASS.
#
# The defect class is "an identity accepted without an independently
# established value for its exact role".  Contract V3 removes it, not its
# example:
#
# * every identity pointer is owned by ONE obligation of the closed-world role
#   schema, which names ONE role and ONE independent authority for it;
# * :class:`_RoleBinding` is the only way a verifier may accept a pointer: it
#   records the role and the authority's value, and refuses a value that is not
#   that value;
# * pointer parity requires EVERY collected identity to be bound - there is no
#   structural class left, in any mode;
# * a checkpoint claim is checked against the BOUND authority value of the
#   pointer it names, never against the manifest's own bytes.
#
# Historical identities (predecessor STOP packages, predecessor evidence) live
# in ignored, unpublished files.  Contract V3 therefore pinned their values as
# HISTORICAL ROLE IDENTITIES in the authority bundle and, in GATE mode, trusted
# the pins without proof.  Candidate R7's fresh independent audit returned
# FAIL / NO-GO on ``R7-AUD-01`` (CRITICAL): the pins are candidate-controlled
# source, so a recomputing author could exchange lawful historical digests
# between roles in the pin table, the manifest, the ledger and the checkpoint
# alike, recompute the implementation digest, and restore GATE PASS.  The
# ``R6-AUD-01`` defect class had survived one layer up.
#
# Contract V4 (Candidate R8) removes candidate-controlled material as the
# source of historical semantic truth.  In EVERY mode, the expected value of
# every historical role is derived from externally authenticated evidence:
#
#   Git-frozen pre-R8 trust root (annotated tag -> commit -> blob, published)
#   -> the accepted R7 Preservation Authority Binding it pins (locator + SHA)
#   -> the authenticated R7 preservation package (archive, index, STOP record)
#   -> role-specific historical evidence inside that package
#
# A role's MEANING comes from that evidence's own structure - which candidate,
# which package file, which predecessor artifact - never from a path, a role
# name or a table in candidate source.  The trust root is read from the Git
# blob, never from a working-tree copy, and its binding locator and SHA come
# from that blob, never from candidate code.  The bundle's
# ``HISTORICAL_ROLE_IDENTITIES`` survives only as a DIAGNOSTIC ASSERTION: it
# must equal the external derivation exactly, it is never consulted for a
# value, and there is no fallback to it when the external evidence is
# unavailable - missing evidence fails closed.

#: The three files of every preservation package, as historical role fields.
HISTORICAL_ROLE_PRESERVATION_FIELDS: tuple[str, ...] = ("archive", "index", "stop_record")
PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST = "predecessor:implementation_digest"
PREDECESSOR_ROLE_CHECKPOINT = "predecessor:checkpoint"
PREDECESSOR_ROLE_MANIFEST = "predecessor:manifest"
PREDECESSOR_ROLE_EOL_POLICY = "predecessor:repository_eol_policy"
PREDECESSOR_MODIFIED_FILE_ROLE_PREFIX = "predecessor:modified_file:"
HISTORICAL_ROLE_PREFIXES: tuple[str, ...] = ("preservation:", "predecessor:")

#: Fail-closed statuses of the external historical authority (``R7-AUD-01``).
#: They are distinct from every other status so that a rejection always names
#: WHICH layer refused: the frozen Git authority, the presence of the external
#: evidence, the internal consistency of that evidence, or the agreement of a
#: candidate's claims with it.
TRUST_ROOT_GIT_AUTHORITY_INVALID = "U06_TRUST_ROOT_GIT_AUTHORITY_INVALID"
EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE = "U06_EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE"
EXTERNAL_HISTORICAL_EVIDENCE_INVALID = "U06_EXTERNAL_HISTORICAL_EVIDENCE_INVALID"
EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH = "U06_EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH"

#: What the externally frozen artifacts must BE, so that another lawful
#: provenance record can never stand in for one of them.
PRE_R8_TRUST_ROOT_ARTIFACT_TYPE = "MAIN_FULL81_PREFLIGHT_PRE_R8_HISTORICAL_TRUST_ROOT"
PRE_R8_TRUST_ROOT_SCHEMA_VERSION = (
    "iris-thesis-main-full81-preflight-pre-r8-historical-trust-root-v1"
)
R7_BINDING_ARTIFACT_TYPE = "R7_PRESERVATION_AUTHORITY_BINDING"
R7_BINDING_SCHEMA_VERSION = "iris-thesis-r7-preservation-authority-binding-v1"
R7_CANDIDATE_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7"
R7_FAILED_LIFECYCLE = "FAILED / NO-GO / NOT_ACCEPTED"
R7_INDEX_ARTIFACT_TYPE = (
    FULL81_PREFLIGHT_AUTH_GUARD_R1_ARTIFACT_TYPE_PREFIX
    + "CANDIDATE_R7_AUDIT_STOP_RAW_BYTE_INDEX"
)
R7_STOP_RECORD_ARTIFACT_TYPE = (
    FULL81_PREFLIGHT_AUTH_GUARD_R1_ARTIFACT_TYPE_PREFIX
    + "CANDIDATE_R7_INDEPENDENT_AUDIT_STOP"
)
#: R1-R6 are authenticated through the R7 raw-byte index; R7 through the binding.
INDEX_AUTHENTICATED_PREDECESSORS: tuple[str, ...] = tuple(
    f"MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R{n}" for n in range(1, 7)
)
#: The sections of the R7 raw-byte index that together state the R7 bytes of
#: every path of R7's preserved candidate surface.
R7_SURFACE_SECTIONS: tuple[tuple[str, str], ...] = (
    ("members", "original_repository_path"),
    ("referenced_not_duplicated", "path"),
    ("head_identical_dependencies", "path"),
)


def preservation_role(candidate_id: str, field: str) -> str:
    """Closed-world name of one preservation-package file's historical role."""

    return f"preservation:{candidate_id}:{field}"


def predecessor_modified_file_role(relative: str) -> str:
    """Closed-world name of a modified file's predecessor-era identity role."""

    return PREDECESSOR_MODIFIED_FILE_ROLE_PREFIX + relative


def is_historical_role(role: str) -> bool:
    """A role whose value only the external historical authority establishes."""

    return isinstance(role, str) and role.startswith(HISTORICAL_ROLE_PREFIXES)


def required_historical_roles() -> dict[str, str | None]:
    """The historical role SCHEMA this source declares -> the path each is OF.

    Derived from the declared preservation packages and the V4 predecessor.
    This is a declaration of shape only: :func:`resolve_external_historical_
    authority` derives the roles independently from external evidence, and the
    two must agree exactly or the contract fails closed.  ``None`` marks a
    digest that is not a file's.
    """

    roles: dict[str, str | None] = {}
    for candidate, declared in CANDIDATE_PRESERVATION_PACKAGES.items():
        for field in HISTORICAL_ROLE_PRESERVATION_FIELDS:
            roles[preservation_role(candidate, field)] = (
                f"{declared['directory']}/{declared[field]}"
            )
    roles[PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST] = None
    roles[PREDECESSOR_ROLE_CHECKPOINT] = CONTRACT_V4_PREDECESSOR_DEFECT["checkpoint_path"]
    roles[PREDECESSOR_ROLE_MANIFEST] = CONTRACT_V4_PREDECESSOR_DEFECT["manifest_path"]
    roles[PREDECESSOR_ROLE_EOL_POLICY] = EOL_POLICY_RELATIVE_PATH
    return roles


# -- the external historical authority (contract V4) ---------------------------


def _git_bytes(root: Path, *args: str) -> bytes | None:
    done = _git(root, *args)
    return done.stdout if done.returncode == 0 else None


def _external_evidence_object(raw: bytes, *, label: str) -> dict[str, Any]:
    """Strictly parse external evidence; any defect is EVIDENCE_INVALID."""

    try:
        return _strict_json_object(raw, label=label)
    except U06LifecycleError as exc:
        raise U06LifecycleError(EXTERNAL_HISTORICAL_EVIDENCE_INVALID, str(exc)) from exc


def _evidence_digest(value: Any, *, what: str) -> str:
    _require(
        isinstance(value, str) and bool(_SHA256_RE.match(value)),
        EXTERNAL_HISTORICAL_EVIDENCE_INVALID,
        f"external historical evidence: {what} is not a lowercase SHA-256: {value!r}",
    )
    return value


def _evidence_relative_path(value: Any, *, what: str) -> str:
    """A canonical repository-relative POSIX path named BY external evidence.

    Absolute, rooted, drive, UNC, backslash and traversal forms are refused, so
    no evidence (and no caller) can redirect a read outside the repository.
    """

    _require(
        isinstance(value, str)
        and bool(value)
        and not value.startswith("/")
        and "\\" not in value
        and ":" not in value
        and all(part not in ("", ".", "..") for part in value.split("/")),
        EXTERNAL_HISTORICAL_EVIDENCE_INVALID,
        f"external historical evidence: {what} is not a canonical "
        f"repository-relative path: {value!r}",
    )
    return value


def _external_file_bytes(root: Path, relative: str, *, what: str) -> bytes:
    """The bytes at ONE canonical locator, or fail closed.  No alternate path."""

    path = root / relative
    _require(
        path.is_file()
        and not path.is_symlink()
        and path.resolve().is_relative_to(root),
        EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE,
        f"{what} is not present at its canonical locator {relative}. Historical "
        "authority fails closed; no alternate path, copy or candidate-local "
        "value is substituted.",
    )
    return path.read_bytes()


def authenticate_pre_r8_trust_root(root: Path) -> dict[str, Any]:
    """Authenticate the pre-R8 historical trust root through frozen Git objects.

    The frozen identity (tag ref, tag object, peeled commit, path, blob and its
    raw SHA-256) was established by the independently audited Git freeze gate
    before Candidate R8 existed; the bundle records it, and this function
    consumes it.  It never selects or redefines it: the ref must resolve to an
    annotated tag object naming exactly that commit and tag, the commit must
    contain exactly that blob at exactly that path, the blob must be the frozen
    bytes, HEAD must still carry that blob there, the frozen commit must be in
    the ancestry of both HEAD and the published upstream, and the working-tree
    copy must be unaltered.  The returned ``bytes`` are the Git blob, never a
    working-tree read.  Takes no path, ref or override: the locator is fixed.
    """

    # Lazy: the bundle imports this overlay.
    from src.production_authority_bundle_v7_4 import (
        PRE_R8_HISTORICAL_TRUST_ROOT as frozen,
    )

    root = Path(root).resolve()
    bad = TRUST_ROOT_GIT_AUTHORITY_INVALID
    label = f"pre-R8 historical trust root ({frozen.tag_ref})"
    tag_object = _git_text(root, "rev-parse", "--verify", "--quiet", frozen.tag_ref)
    _require(
        tag_object == frozen.tag_object,
        bad,
        f"{label}: the ref resolves to {tag_object!r}, not the frozen annotated tag "
        f"object {frozen.tag_object}.",
    )
    _require(
        _git_text(root, "cat-file", "-t", frozen.tag_object) == "tag",
        bad,
        f"{label}: {frozen.tag_object} is not an annotated tag object.",
    )
    header: dict[str, str] = {}
    for line in (_git_bytes(root, "cat-file", "tag", frozen.tag_object) or b"").split(b"\n"):
        if not line:
            break
        key, _, value = line.decode("utf-8", "replace").partition(" ")
        header.setdefault(key, value)
    _require(
        header.get("object") == frozen.commit
        and header.get("type") == "commit"
        and header.get("tag") == frozen.tag_ref.removeprefix("refs/tags/"),
        bad,
        f"{label}: the tag object names object={header.get('object')!r}, "
        f"type={header.get('type')!r}, tag={header.get('tag')!r}; the frozen "
        f"authority is commit {frozen.commit}.",
    )
    _require(
        _git_text(root, "rev-parse", "--verify", "--quiet", f"{frozen.commit}^{{commit}}")
        == frozen.commit,
        bad,
        f"{label}: the frozen commit {frozen.commit} is not present.",
    )
    _require(
        _git_text(root, "rev-parse", "--verify", "--quiet", f"{frozen.commit}:{frozen.path}")
        == frozen.blob,
        bad,
        f"{label}: commit {frozen.commit} does not carry the frozen blob "
        f"{frozen.blob} at {frozen.path}.",
    )
    blob = _git_bytes(root, "cat-file", "blob", frozen.blob)
    _require(
        blob is not None
        and len(blob) == frozen.byte_count
        and hashlib.sha256(blob).hexdigest() == frozen.raw_sha256,
        bad,
        f"{label}: blob {frozen.blob} is not the frozen trust-root bytes.",
    )
    _require(
        _git_text(root, "rev-parse", "--verify", "--quiet", f"HEAD:{frozen.path}")
        == frozen.blob,
        bad,
        f"{label}: HEAD does not carry the frozen trust-root blob at "
        f"{frozen.path}; the trust root was altered or removed after its freeze.",
    )
    for ref in ("HEAD", EXPECTED_UPSTREAM):
        _require(
            is_ancestor(root, frozen.commit, ref),
            bad,
            f"{label}: the frozen commit {frozen.commit} is not in the ancestry of "
            f"{ref}, so it is not the published pre-R8 authority.",
        )
    live = root / frozen.path
    _require(
        live.is_file() and live.read_bytes() == blob,
        bad,
        f"{label}: the working-tree copy of {frozen.path} differs from the frozen "
        "blob.",
    )
    return {
        "tag_ref": frozen.tag_ref,
        "tag_object": frozen.tag_object,
        "commit": frozen.commit,
        "path": frozen.path,
        "blob": frozen.blob,
        "raw_sha256": frozen.raw_sha256,
        "byte_count": frozen.byte_count,
        "bytes": blob,
    }


def _trust_root_binding_selection(blob: bytes) -> dict[str, Any]:
    """The ONE binding the frozen trust root selects, read from its Git blob."""

    from src.production_authority_bundle_v7_4 import (
        PRE_R8_HISTORICAL_TRUST_ROOT as frozen,
    )

    bad = EXTERNAL_HISTORICAL_EVIDENCE_INVALID
    label = "pre-R8 historical trust root"
    record = _external_evidence_object(blob, label=label)
    selection = record.get("canonical_r7_binding")
    generation = record.get("r7_generation")
    policy = record.get("override_policy")
    excluded = record.get("excluded_predecessor")
    termination = record.get("git_termination")
    _require(
        record.get("artifact_type") == PRE_R8_TRUST_ROOT_ARTIFACT_TYPE
        and record.get("schema_version") == PRE_R8_TRUST_ROOT_SCHEMA_VERSION
        and isinstance(selection, Mapping)
        and isinstance(generation, Mapping)
        and isinstance(policy, Mapping)
        and isinstance(excluded, Mapping)
        and isinstance(termination, Mapping),
        bad,
        f"{label}: not a pre-R8 historical trust-root record.",
    )
    _require(
        selection.get("selection_cardinality") == "EXACTLY_ONE"
        and selection.get("artifact_type") == R7_BINDING_ARTIFACT_TYPE
        and selection.get("schema_version") == R7_BINDING_SCHEMA_VERSION
        and isinstance(selection.get("byte_count"), int)
        and not isinstance(selection.get("byte_count"), bool),
        bad,
        f"{label}: it does not select exactly one R7 Preservation Authority Binding.",
    )
    _require(
        generation.get("candidate_id") == R7_CANDIDATE_ID
        and generation.get("lifecycle") == R7_FAILED_LIFECYCLE
        and excluded.get("trust_dependency") is False
        and termination.get("canonical_tracked_path") == frozen.path,
        bad,
        f"{label}: its R7 generation, failed-selector exclusion or canonical "
        "tracked path is not the frozen pre-R8 authority.",
    )
    overrides = {k: v for k, v in policy.items() if k.endswith("_allowed")}
    _require(
        bool(overrides) and all(v is False for v in overrides.values()),
        bad,
        f"{label}: its override policy permits a redirection: {overrides}",
    )
    return {
        "locator": _evidence_relative_path(
            selection.get("locator"), what="trust-root binding locator"
        ),
        "sha256": _evidence_digest(selection.get("sha256"), what="trust-root binding SHA-256"),
        "byte_count": selection["byte_count"],
    }


def resolve_external_historical_authority(root: Path) -> dict[str, Any]:
    """Derive every historical role from externally authenticated evidence.

    Fail-closed and read-only.  The chain is fixed: the Git-frozen trust root
    selects one binding; the binding's bytes must be exactly the pinned bytes;
    the binding names one R7 preservation package whose archive, index and STOP
    record must be exactly the bound bytes and must agree with one another
    (archive members == index records; index and STOP record restate the
    binding).  Only then are role identities read from that evidence:

    * ``preservation:<R1..R6>:*`` from the index's own per-candidate record of
      the predecessor packages it verified;
    * ``preservation:<R7>:*`` from the binding's canonical package;
    * ``predecessor:*`` (the R7 implementation digest, checkpoint and manifest)
      from the binding, cross-checked against the index and the STOP record;
    * ``predecessor:repository_eol_policy`` from the archived R7 EOL policy;
    * the R7 bytes of every path of R7's preserved surface, for change sets.

    There is no parameter through which a caller could name another path, ref
    or binding, and no fallback when any of it is missing.
    """

    root = Path(root).resolve()
    bad = EXTERNAL_HISTORICAL_EVIDENCE_INVALID
    trust = authenticate_pre_r8_trust_root(root)
    selection = _trust_root_binding_selection(trust["bytes"])

    locator = selection["locator"]
    raw = _external_file_bytes(
        root, locator, what="The accepted R7 Preservation Authority Binding"
    )
    _require(
        len(raw) == selection["byte_count"]
        and hashlib.sha256(raw).hexdigest() == selection["sha256"],
        bad,
        f"R7 binding at {locator}: its raw bytes are not the bytes the frozen trust "
        f"root pins ({selection['sha256']}).",
    )
    binding = _external_evidence_object(raw, label="R7 Preservation Authority Binding")
    _require(
        binding.get("artifact_type") == R7_BINDING_ARTIFACT_TYPE
        and binding.get("schema_version") == R7_BINDING_SCHEMA_VERSION
        and binding.get("predecessor_generation") == "R7"
        and binding.get("predecessor_candidate_id") == R7_CANDIDATE_ID
        and binding.get("predecessor_lifecycle") == R7_FAILED_LIFECYCLE
        and isinstance(binding.get("canonical_package"), Mapping)
        and isinstance(binding.get("predecessor_identities"), Mapping),
        bad,
        "R7 binding: it is not the failed-R7 preservation authority binding.",
    )

    # The R7 preservation package, exactly as bound.
    package = binding["canonical_package"]
    directory = _evidence_relative_path(package.get("directory"), what="R7 package directory")
    bound: dict[str, tuple[str, str]] = {}
    blobs: dict[str, bytes] = {}
    for field in HISTORICAL_ROLE_PRESERVATION_FIELDS:
        entry = package.get(field)
        _require(isinstance(entry, Mapping), bad, f"R7 binding: no canonical {field}.")
        relative = _evidence_relative_path(entry.get("path"), what=f"R7 package {field}")
        digest = _evidence_digest(entry.get("sha256"), what=f"R7 package {field}")
        _require(
            relative.rsplit("/", 1)[0] == directory,
            bad,
            f"R7 binding: the {field} {relative} is outside the package directory.",
        )
        data = _external_file_bytes(root, relative, what=f"The R7 preservation {field}")
        _require(
            hashlib.sha256(data).hexdigest() == digest,
            bad,
            f"R7 preservation {field} at {relative}: live bytes are not the bound "
            f"bytes {digest}.",
        )
        bound[field] = (relative, digest)
        blobs[field] = data

    identities = binding["predecessor_identities"]
    implementation = identities.get("implementation")
    _require(
        isinstance(implementation, Mapping)
        and implementation.get("path_count") == len(ACCEPTED_IMPLEMENTATION_PATHS),
        bad,
        "R7 binding: the predecessor implementation identity is malformed.",
    )
    r7_digest = _evidence_digest(
        implementation.get("digest"), what="R7 implementation digest"
    )
    artifacts: dict[str, tuple[str, str]] = {}
    for field in ("checkpoint", "manifest", "change_ledger"):
        entry = identities.get(field)
        _require(isinstance(entry, Mapping), bad, f"R7 binding: no predecessor {field}.")
        artifacts[field] = (
            _evidence_relative_path(entry.get("path"), what=f"R7 {field}"),
            _evidence_digest(entry.get("sha256"), what=f"R7 {field}"),
        )

    index = _external_evidence_object(blobs["index"], label="R7 raw-byte index")
    _require(
        index.get("artifact_type") == R7_INDEX_ARTIFACT_TYPE
        and index.get("preserved_candidate_id") == R7_CANDIDATE_ID
        and index.get("preserved_implementation_digest") == r7_digest
        and isinstance(index.get("archive"), Mapping)
        and index["archive"].get("path") == bound["archive"][0]
        and index["archive"].get("sha256") == bound["archive"][1],
        bad,
        "R7 raw-byte index: it does not describe the bound R7 archive and "
        "implementation identity.",
    )
    for field in ("checkpoint", "manifest", "change_ledger"):
        entry = index.get(f"candidate_{field}")
        _require(
            isinstance(entry, Mapping)
            and (entry.get("path"), entry.get("raw_sha256")) == artifacts[field],
            bad,
            f"R7 raw-byte index: its candidate {field} disagrees with the binding.",
        )
    members = index.get("members")
    _require(
        isinstance(members, list) and members,
        bad,
        "R7 raw-byte index: no archive members.",
    )
    try:
        archive = zipfile.ZipFile(io.BytesIO(blobs["archive"]))
        names = archive.namelist()
        archived = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in names}
    except Exception as exc:  # pragma: no cover - any archive defect fails closed
        raise U06LifecycleError(bad, f"R7 archive: unreadable ({exc}).") from exc
    recorded = {}
    for entry in members:
        _require(
            isinstance(entry, Mapping)
            and isinstance(entry.get("archive_member_path"), str)
            and entry.get("archive_member_path") == entry.get("original_repository_path"),
            bad,
            "R7 raw-byte index: a member record is malformed.",
        )
        recorded[entry["archive_member_path"]] = _evidence_digest(
            entry.get("raw_sha256"), what=f"R7 member {entry['archive_member_path']}"
        )
    _require(
        len(names) == len(set(names)) and archived == recorded,
        bad,
        "R7 archive: its members are not exactly the bytes its raw-byte index "
        "records.",
    )

    stop = _external_evidence_object(blobs["stop_record"], label="R7 STOP record")
    preserved = stop.get("preservation_package")
    _require(
        stop.get("artifact_type") == R7_STOP_RECORD_ARTIFACT_TYPE
        and stop.get("candidate_id") == R7_CANDIDATE_ID
        and stop.get("lifecycle_status") == R7_FAILED_LIFECYCLE
        and stop.get("candidate_implementation_digest") == r7_digest
        and isinstance(preserved, Mapping)
        and (preserved.get("archive_path"), preserved.get("archive_sha256"))
        == bound["archive"]
        and (preserved.get("byte_index_path"), preserved.get("byte_index_sha256"))
        == bound["index"],
        bad,
        "R7 STOP record: it does not record the failed R7 candidate and the bound "
        "archive and index.",
    )
    for field in ("checkpoint", "manifest", "change_ledger"):
        entry = stop.get(f"candidate_{field}")
        _require(
            isinstance(entry, Mapping)
            and (entry.get("path"), entry.get("sha256")) == artifacts[field],
            bad,
            f"R7 STOP record: its candidate {field} disagrees with the binding.",
        )

    # Role derivation: semantics from the evidence's own structure only.
    roles: dict[str, tuple[str | None, str]] = {}
    packages: dict[str, dict[str, str]] = {}

    def record_package(candidate: str, files: Mapping[str, tuple[str, str]]) -> None:
        directories = {relative.rsplit("/", 1)[0] for relative, _ in files.values()}
        _require(
            candidate not in packages and len(directories) == 1,
            bad,
            f"external historical evidence: the {candidate} package is duplicated "
            "or not one directory.",
        )
        packages[candidate] = {"directory": directories.pop()}
        for field, (relative, digest) in files.items():
            packages[candidate][field] = relative.rsplit("/", 1)[1]
            roles[preservation_role(candidate, field)] = (relative, digest)

    verified = index.get("predecessor_preservation_packages_verified")
    _require(
        isinstance(verified, list)
        and [e.get("candidate_id") if isinstance(e, Mapping) else None for e in verified]
        == list(INDEX_AUTHENTICATED_PREDECESSORS),
        bad,
        "R7 raw-byte index: it does not record exactly the R1-R6 preservation "
        "packages it verified.",
    )
    for entry in verified:
        record_package(
            entry["candidate_id"],
            {
                field: (
                    _evidence_relative_path(
                        entry.get(f"{field}_path"),
                        what=f"{entry['candidate_id']} {field}",
                    ),
                    _evidence_digest(
                        entry.get(f"{field}_sha256"),
                        what=f"{entry['candidate_id']} {field}",
                    ),
                )
                for field in HISTORICAL_ROLE_PRESERVATION_FIELDS
            },
        )
    record_package(R7_CANDIDATE_ID, bound)
    roles[PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST] = (None, r7_digest)
    roles[PREDECESSOR_ROLE_CHECKPOINT] = artifacts["checkpoint"]
    roles[PREDECESSOR_ROLE_MANIFEST] = artifacts["manifest"]

    surface: dict[str, str] = {}
    for section, key in R7_SURFACE_SECTIONS:
        entries = index.get(section)
        _require(isinstance(entries, list), bad, f"R7 raw-byte index: no {section}.")
        for entry in entries:
            relative = _evidence_relative_path(
                entry.get(key) if isinstance(entry, Mapping) else None,
                what=f"R7 {section} path",
            )
            digest = _evidence_digest(entry.get("raw_sha256"), what=f"R7 {relative}")
            _require(
                surface.setdefault(relative, digest) == digest,
                bad,
                f"R7 raw-byte index: {relative} carries two different R7 identities.",
            )
    eol = [
        m for m in members
        if m.get("original_repository_path") == EOL_POLICY_RELATIVE_PATH
        and m.get("role") == "REPOSITORY_EOL_POLICY"
    ]
    _require(
        len(eol) == 1,
        bad,
        "R7 raw-byte index: it does not archive exactly one R7 EOL policy.",
    )
    roles[PREDECESSOR_ROLE_EOL_POLICY] = (EOL_POLICY_RELATIVE_PATH, eol[0]["raw_sha256"])

    return {
        "trust_root": {k: v for k, v in trust.items() if k != "bytes"},
        "binding": {
            "path": locator,
            "sha256": selection["sha256"],
            "byte_count": selection["byte_count"],
        },
        "predecessor_candidate_id": R7_CANDIDATE_ID,
        "roles": roles,
        "preservation_packages": packages,
        "predecessor_surface": surface,
    }


def external_predecessor_change_set(
    root: Path, authority: Mapping[str, Any]
) -> dict[str, str]:
    """Every R7-surface path whose live bytes are not R7's -> R7's raw SHA-256.

    The predecessor change set, derived in every mode from the authenticated R7
    surface and live bytes - never from a candidate's own list.  An absent path
    counts as changed, so missing historical bytes fail closed downstream.
    """

    root = Path(root).resolve()
    changed: dict[str, str] = {}
    for relative, recorded in authority["predecessor_surface"].items():
        path = root / relative
        if not path.is_file() or sha256_file(path) != recorded:
            changed[relative] = recorded
    return changed


def historical_role_identities(*, label: str) -> dict[str, tuple[str | None, str]]:
    """The bundle's candidate-local DIAGNOSTIC historical table, shape-checked.

    Never an authority: :class:`_RoleBinding` requires it to equal the external
    derivation exactly and never reads a value from it.  Fails closed on a
    duplicate role, a malformed role name, path or digest.  Read-only.
    """

    # Lazy: the bundle imports this overlay.
    from src.production_authority_bundle_v7_4 import HISTORICAL_ROLE_IDENTITIES

    out: dict[str, tuple[str | None, str]] = {}
    for entry in HISTORICAL_ROLE_IDENTITIES:
        role = entry.role
        _require(
            role not in out,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: historical role {role!r} is listed twice.",
        )
        _require(
            is_historical_role(role)
            and (entry.relative_path is None or isinstance(entry.relative_path, str))
            and isinstance(entry.sha256, str)
            and bool(_SHA256_VALUE_RE.match(entry.sha256)),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: historical role {role!r} is malformed.",
        )
        out[role] = (entry.relative_path, entry.sha256)
    return out


def _require_declared_schema_agrees(
    authority: Mapping[str, Any], *, label: str
) -> None:
    """This source's declared package/predecessor schema equals the evidence."""

    declared = required_historical_roles()
    derived = {role: entry[0] for role, entry in authority["roles"].items()}
    _require(
        declared == derived,
        EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
        f"{label}: the declared historical role schema disagrees with the "
        "externally authenticated evidence: "
        f"undeclared={sorted(set(derived) - set(declared))}, "
        f"unevidenced={sorted(set(declared) - set(derived))}, "
        f"other_path={sorted(r for r in set(declared) & set(derived) if declared[r] != derived[r])}",
    )
    for candidate, layout in authority["preservation_packages"].items():
        declared_layout = CANDIDATE_PRESERVATION_PACKAGES.get(candidate, {})
        _require(
            all(declared_layout.get(k) == v for k, v in layout.items()),
            EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
            f"{label}: the declared {candidate} package layout disagrees with the "
            "externally authenticated evidence.",
        )


def _require_local_table_agrees(
    derived: Mapping[str, tuple[str | None, str]], *, label: str
) -> None:
    """The candidate-local diagnostic table equals the external derivation."""

    local = historical_role_identities(label=label)
    differing = sorted(
        role
        for role in set(local) | set(derived)
        if local.get(role) != derived.get(role)
    )
    _require(
        not differing,
        EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
        f"{label}: the candidate-local historical table disagrees with the "
        f"externally authenticated historical derivation for roles {differing}. "
        "Candidate-local values are diagnostic only and never authoritative.",
    )


class _RoleBinding:
    """The ONE way an identity is accepted: bound to a role and an authority.

    Shared by the candidate-manifest and change-ledger validations.  A verifier
    calls :meth:`bind` for every pointer it accepts; :func:`_verify_owned_
    identities` then requires every collected identity to be bound.  Nothing
    is ever accepted on structure alone, in any mode, and no historical value
    is ever taken from candidate-controlled material (contract V4).
    """

    def __init__(self, root: Path, mode: str, label: str) -> None:
        self.root = root
        self.mode = mode
        self.label = label
        #: pointer -> the independently established value for its role.
        self.authority: dict[tuple[Any, ...], str] = {}
        #: pointer -> the role it was bound to.
        self.roles: dict[tuple[Any, ...], str] = {}
        self._external: Mapping[str, Any] | None = None
        self._historical: dict[str, tuple[str | None, str]] | None = None
        self._proved: set[str] = set()

    # -- authorities ---------------------------------------------------------

    @property
    def proves_preserved_bytes(self) -> bool:
        """``CANDIDATE_PACKAGE`` additionally proves the R1-R7 files are live."""

        return self.mode == CANDIDATE_MANIFEST_MODE_CANDIDATE_PACKAGE

    def live_sha(self, relative: str, *, field: str) -> str:
        path = self.root / relative
        _require(
            path.is_file(),
            "U06_ROLE_TARGET_MISMATCH",
            f"{self.label}: {field} names a file that does not exist: {relative}",
        )
        return sha256_file(path)

    def external(self) -> Mapping[str, Any]:
        """The externally authenticated historical authority, resolved once."""

        if self._external is None:
            authority = resolve_external_historical_authority(self.root)
            _require_declared_schema_agrees(authority, label=self.label)
            self._external = authority
        return self._external

    def predecessor_change_set(self) -> dict[str, str]:
        return external_predecessor_change_set(self.root, self.external())

    def historical_roles(self) -> dict[str, tuple[str | None, str]]:
        """Every historical role -> its EXTERNALLY established (path, digest).

        The preservation and predecessor roles come from the authenticated
        evidence; the modified-file roles are the externally derived change set.
        The candidate-local table must equal this exactly; it is never read for
        a value, and nothing here falls back to it.
        """

        if self._historical is None:
            derived = dict(self.external()["roles"])
            for relative, digest in self.predecessor_change_set().items():
                derived[predecessor_modified_file_role(relative)] = (relative, digest)
            _require_local_table_agrees(derived, label=self.label)
            self._historical = derived
        return self._historical

    def historical(self, role: str) -> str:
        """The externally established value of a historical role."""

        entry = self.historical_roles().get(role)
        _require(
            entry is not None,
            EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
            f"{self.label}: {role!r} is not a role of the externally authenticated "
            "historical evidence.",
        )
        path, digest = entry
        if self.proves_preserved_bytes and role not in self._proved:
            self._prove_historical(role, path, digest)
            self._proved.add(role)
        return digest

    def _prove_historical(self, role: str, path: str | None, digest: str) -> None:
        """``CANDIDATE_PACKAGE``: the described historical files are live too."""

        if role.startswith("preservation:") or role in (
            PREDECESSOR_ROLE_CHECKPOINT,
            PREDECESSOR_ROLE_MANIFEST,
        ):
            _require_live_match(
                self.root, str(path), digest, label=self.label, field=f"historical role {role}"
            )
        elif role == PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST:
            manifest = _strict_json_object(
                (self.root / CONTRACT_V4_PREDECESSOR_DEFECT["manifest_path"]).read_bytes(),
                label="predecessor candidate manifest",
            )
            _require(
                manifest.get("implementation_identity_digest") == digest,
                EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
                f"{self.label}: the externally established predecessor "
                "implementation digest is not the predecessor manifest's own.",
            )

    # -- binding -------------------------------------------------------------

    def bind(self, pointer: tuple[Any, ...], value: str, expected: Any, role: str) -> None:
        """Accept ``value`` at ``pointer`` only as ``role``'s authority value."""

        dotted = ".".join(map(str, pointer))
        _require(
            isinstance(expected, str) and bool(_SHA256_VALUE_RE.match(expected)),
            "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
            f"{self.label}: {dotted} has no independently established value for "
            f"its role {role!r}.",
        )
        _require(
            pointer not in self.authority,
            "U06_ROLE_SCHEMA_INVALID",
            f"{self.label}: {dotted} is bound to two roles "
            f"({self.roles.get(pointer)!r}, {role!r}).",
        )
        historical = is_historical_role(role)
        _require(
            value == expected,
            EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH
            if historical
            else "U06_ROLE_TARGET_MISMATCH",
            f"{self.label}: {dotted} holds {value}, but its role {role!r} is "
            + (
                "established by the externally authenticated historical authority "
                if historical
                else "independently established "
            )
            + f"as {expected}. A digest lawful for one role is never accepted in "
            "another.",
        )
        self.authority[pointer] = expected
        self.roles[pointer] = role


class _ContractContext(_RoleBinding):
    """Shared, lazily computed live identities for one contract validation."""

    def __init__(
        self,
        root: Path,
        payload: Mapping[str, Any],
        generation: AuthorityGeneration,
        mode: str,
        label: str,
    ) -> None:
        super().__init__(root, mode, label)
        self.payload = payload
        self.generation = generation
        self._identity: dict[str, str] | None = None
        #: Filled by the ``C9`` verifier: the validated ledger's report.
        self.ledger_report: dict[str, Any] | None = None

    def live_identity(self) -> dict[str, str]:
        if self._identity is None:
            self._identity = implementation_identity(self.root)
        return self._identity

    def live_digest(self) -> str:
        return canonical_identity_digest(self.live_identity())


_Item = tuple[tuple[Any, ...], str, IdentityObligation]


def _verify_candidate_checkpoint(ctx: _ContractContext, items: list[_Item]):
    _require(
        [item[0] for item in items] == [("candidate_checkpoint", "sha256")],
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: exactly one candidate checkpoint identity is required; "
        f"observed {[item[0] for item in items]}",
    )
    pointer, value, _ = items[0]
    relative = ctx.generation.candidate_checkpoint_path
    ctx.bind(
        pointer,
        value,
        ctx.live_sha(relative, field="candidate_checkpoint"),
        f"candidate_checkpoint:{relative}",
    )


def _verify_implementation_digest(ctx: _ContractContext, items: list[_Item]):
    expected = {
        ("implementation_identity_digest",),
        ("implementation_identity", "implementation_digest"),
    }
    observed = [item[0] for item in items]
    _require(
        len(observed) == 2 and set(observed) == expected,
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: both implementation-digest identities are required; "
        f"observed {observed}",
    )
    live = ctx.live_digest()
    for pointer, value, _ in items:
        _require(
            value == live,
            "U06_IMPLEMENTATION_IDENTITY_DRIFT",
            f"{ctx.label}: {'.'.join(map(str, pointer))} declares {value} but the "
            f"live accepted implementation digest is {live}.",
        )
        ctx.bind(pointer, value, live, "live_implementation_digest")
    paths = ctx.payload["implementation_identity"]["paths"]
    reproduced = canonical_identity_digest(paths) if isinstance(paths, Mapping) else None
    _require(
        reproduced == live,
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        f"{ctx.label}: the declared implementation paths map does not reproduce "
        f"the declared digest (reproduced={reproduced}, live={live}).",
    )


def _verify_implementation_paths(ctx: _ContractContext, items: list[_Item]):
    declared = {str(item[0][2]): item[1] for item in items}
    _require(
        set(declared) == set(ACCEPTED_IMPLEMENTATION_PATHS)
        and len(items) == len(ACCEPTED_IMPLEMENTATION_PATHS),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: implementation_identity.paths must declare exactly the "
        f"{len(ACCEPTED_IMPLEMENTATION_PATHS)} accepted implementation paths; "
        f"missing={sorted(set(ACCEPTED_IMPLEMENTATION_PATHS) - set(declared))}, "
        f"extra={sorted(set(declared) - set(ACCEPTED_IMPLEMENTATION_PATHS))}",
    )
    live = ctx.live_identity()
    for pointer, value, _ in items:
        relative = str(pointer[2])
        _require(
            value == live[relative],
            "U06_IMPLEMENTATION_IDENTITY_DRIFT",
            f"{ctx.label}: implementation_identity.paths[{relative}] declares "
            f"{value} but live bytes hash to {live[relative]}.",
        )
        ctx.bind(pointer, value, live[relative], f"implementation_path:{relative}")


def _verify_bundle_pins(ctx: _ContractContext, items: list[_Item]):
    # Lazy: the bundle imports this overlay.
    from src.production_authority_bundle_v7_4 import all_pins

    by_label = {pin.label: pin for pin in all_pins()}
    pin_items = [i for i in items if i[0][:2] == ("authority_bundle", "pins")]
    labels = [str(i[0][2]) for i in pin_items]
    _require(
        sorted(labels) == sorted(by_label),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: authority_bundle.pins must restate exactly the "
        f"{len(by_label)} declared bundle pins; "
        f"missing={sorted(set(by_label) - set(labels))}, "
        f"extra={sorted(set(labels) - set(by_label))}",
    )
    restated = {
        ("repository_eol_policy", "sha256"): "repository_eol_policy",
        ("parameter_registry_durability", "canonical_sha256"): "parameter_registry",
    }
    other = [i[0] for i in items if i[0][:2] != ("authority_bundle", "pins")]
    _require(
        sorted(other) == sorted(restated),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: restated pins must be exactly {sorted(restated)}; "
        f"observed {sorted(other)}",
    )
    for pointer, value, _ in items:
        label = str(pointer[2]) if pointer[:2] == ("authority_bundle", "pins") else restated[pointer]
        pin = by_label[label]
        holder = _resolve_pointer(ctx.payload, pointer[:-1])
        _require(
            holder.get("path") == pin.relative_path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: pin {label!r} is restated for path "
            f"{holder.get('path')!r} but the bundle pins {pin.relative_path}.",
        )
        ctx.bind(pointer, value, pin.sha256, f"bundle_pin:{label}")


def _verify_durable_pinned(ctx: _ContractContext, items: list[_Item]):
    expected = _required_durable_publication_sha256()
    declared = {str(item[0][2]): item[1] for item in items}
    _require(
        set(declared) == set(REQUIRED_DURABLE_PUBLICATION_PIN_LABELS)
        and len(items) == len(REQUIRED_DURABLE_PUBLICATION_PIN_LABELS),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: expected_raw_sha256 is required for exactly the pinned "
        f"durable paths {sorted(REQUIRED_DURABLE_PUBLICATION_PIN_LABELS)} and "
        f"forbidden elsewhere; observed {sorted(declared)}",
    )
    for pointer, value, _ in items:
        relative = str(pointer[2])
        canonical = expected.get(relative)
        _require(
            canonical is not None,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: durable declaration for {relative} has no resolvable "
            "authority pin.",
        )
        ctx.bind(
            pointer,
            value,
            canonical,
            f"bundle_pin:{REQUIRED_DURABLE_PUBLICATION_PIN_LABELS[relative]}",
        )


def _verify_preservation(ctx: _ContractContext, items: list[_Item]):
    """``C6``: each preservation file identity is ITS external historical role."""

    packages = ctx.payload.get("candidate_preservation_packages")
    _require(
        isinstance(packages, Mapping)
        and set(packages) == set(CANDIDATE_PRESERVATION_PACKAGES),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: candidate_preservation_packages must name exactly "
        f"{sorted(CANDIDATE_PRESERVATION_PACKAGES)}",
    )
    expected_pointers: set[tuple[Any, ...]] = set()
    for candidate, declared in CANDIDATE_PRESERVATION_PACKAGES.items():
        entry = packages[candidate]
        _require(
            isinstance(entry, Mapping) and set(entry) == PRESERVATION_ENTRY_KEYS,
            "U06_ROLE_SCHEMA_INVALID",
            f"{ctx.label}: preservation entry {candidate} must have exactly "
            f"{sorted(PRESERVATION_ENTRY_KEYS)}",
        )
        directory = declared["directory"]
        for field, want in (
            ("directory", directory),
            ("stop_class", declared["stop_class"]),
            ("archive_path", f"{directory}/{declared['archive']}"),
            ("index_path", f"{directory}/{declared['index']}"),
            ("stop_record_path", f"{directory}/{declared['stop_record']}"),
        ):
            _require(
                entry.get(field) == want,
                "U06_ROLE_TARGET_MISMATCH",
                f"{ctx.label}: preservation {candidate}.{field} must be "
                f"{want!r}; observed {entry.get(field)!r}",
            )
        for key in ("archive_sha256", "index_sha256", "stop_record_sha256"):
            expected_pointers.add(("candidate_preservation_packages", candidate, key))
    _require(
        {item[0] for item in items} == expected_pointers
        and len(items) == len(expected_pointers),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every preservation package needs exactly its three "
        "raw SHA-256 identities.",
    )
    for pointer, value, _ in items:
        candidate, key = str(pointer[1]), str(pointer[2])
        role = preservation_role(candidate, key[: -len("_sha256")])
        ctx.bind(pointer, value, ctx.historical(role), role)


def _verify_predecessor_evidence(ctx: _ContractContext, items: list[_Item]):
    """``C7`` (contract V3): typed evidence of the IMMEDIATE predecessor, R6."""

    base = ("package_binding", "predecessor_defect")
    roles = {
        ("implementation_identity", "predecessor_digest"): (
            PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST
        ),
        base + ("predecessor_candidate_checkpoint", "raw_sha256"): (
            PREDECESSOR_ROLE_CHECKPOINT
        ),
        base + ("predecessor_candidate_manifest", "raw_sha256"): PREDECESSOR_ROLE_MANIFEST,
    }
    _require(
        {item[0] for item in items} == set(roles) and len(items) == len(roles),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: predecessor-defect evidence identities are incomplete or "
        "extra.",
    )
    _require(
        ctx.payload["implementation_identity"]["predecessor_digest"]
        != ctx.payload["implementation_identity"]["implementation_digest"],
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: the predecessor implementation digest equals the current "
        "one, so it would be a carried-forward identity, not history.",
    )
    for pointer, value, _ in items:
        ctx.bind(pointer, value, ctx.historical(roles[pointer]), roles[pointer])


def _verify_candidate_change_ledger(ctx: _ContractContext, items: list[_Item]):
    """``C9``: the bound ledger is exactly the live ledger, and it is valid."""

    _require(
        [item[0] for item in items] == [("candidate_change_ledger", "sha256")],
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: exactly one candidate change ledger identity is required; "
        f"observed {[item[0] for item in items]}",
    )
    pointer, value, _ = items[0]
    relative = ctx.payload["candidate_change_ledger"]["path"]
    ctx.bind(
        pointer,
        value,
        ctx.live_sha(relative, field="candidate_change_ledger"),
        f"candidate_change_ledger:{relative}",
    )
    ctx.ledger_report = validate_candidate_change_ledger(
        ctx.root,
        (ctx.root / relative).read_bytes(),
        ctx.payload,
        ctx.generation,
        mode=ctx.mode,
        live_identity=ctx.live_identity(),
    )


def _own_identity_pointers(
    identities: Sequence[tuple[tuple[Any, ...], str]],
    obligations: Sequence[IdentityObligation],
    label: str,
) -> dict[str, list[_Item]]:
    """Give every identity pointer to exactly one declared obligation."""

    owned: dict[str, list[_Item]] = {o.kind: [] for o in obligations}
    for pointer, value in identities:
        owners = [o for o in obligations if _pointer_matches(o.pattern, pointer)]
        _require(
            bool(owners),
            "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
            f"{label}: {'.'.join(map(str, pointer))} carries a raw SHA-256 that "
            "no declared identity obligation owns.",
        )
        _require(
            len(owners) == 1,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {'.'.join(map(str, pointer))} is claimed by "
            f"{len(owners)} obligations; ownership must be exclusive.",
        )
        owned.setdefault(owners[0].kind, []).append((pointer, value, owners[0]))
    return owned


def _verify_owned_identities(
    owned: Mapping[str, list[_Item]],
    identities: Sequence[tuple[tuple[Any, ...], str]],
    verifiers: Mapping[str, Any],
    context: _RoleBinding,
    label: str,
) -> tuple[set[tuple[Any, ...]], set[tuple[Any, ...]]]:
    """Run every obligation's verifier, then prove role-binding parity.

    ``R6-AUD-01``: there is no structural class.  Every collected identity must
    have been bound by its verifier to one role whose value was established
    independently, and must still equal that value.  Returns ``(bound,
    set())``; the empty second element keeps the historical report shape.
    """

    for kind in sorted(owned):
        verifier = verifiers.get(kind)
        _require(
            verifier is not None,
            "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
            f"{label}: obligation kind {kind!r} has no verifier.",
        )
        verifier(context, owned[kind])
    collected = dict(identities)
    bound = context.authority
    unbound = set(collected) - set(bound)
    _require(
        not unbound and set(bound) <= set(collected) and len(collected) == len(identities),
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: role-binding parity failed: collected={len(collected)}, "
        f"bound={len(bound)}; every identity must be bound to one role with an "
        "independently established value, and none may be accepted on "
        f"structure alone. unbound={sorted('.'.join(map(str, p)) for p in unbound)}",
    )
    mismatched = sorted(
        ".".join(map(str, p)) for p, value in collected.items() if bound[p] != value
    )
    _require(
        not mismatched,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: identities differ from their role's authority value: {mismatched}",
    )
    return set(bound), set()


def _strict_equal(a: Any, b: Any) -> bool:
    """Type-strict structural equality (``False`` is never ``0``)."""

    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# ---------------------------------------------------------------------------
# Candidate R6: the closed-world candidate change / reproducibility ledger
# ---------------------------------------------------------------------------
#
# The ledger is an INDEX of what a candidate changed and why; the raw-byte
# difference stays the authoritative modification evidence.  It still states
# raw SHA-256 identities, and an identity no validator checks is exactly the
# ``R4-AUD-01`` defect class.  So the ledger is bound by the manifest (``C9``)
# and every identity it states is owned by one ledger obligation and verified.
#
# Candidate R7 (``R6-AUD-01``): under contract V2 the predecessor,
# modified-file-predecessor and executed-suite identities were STRUCTURAL in
# GATE mode, so a swap applied consistently to the ledger and the manifest was
# undetectable there.  Under V3 every ledger identity is bound, in every mode,
# to one role whose value is established independently: live bytes, the live
# implementation identity, a bundle pin, or a pinned historical role identity.
# CANDIDATE_PACKAGE mode additionally proves those historical pins against the
# immutable predecessor bytes and its raw-byte index, and proves the
# modified-file list COMPLETE over the predecessor's preserved surface.
#
# Candidate R8 (``R7-AUD-01``, contract V4): the historical values, and the
# modified-file change set itself, are derived in EVERY mode from the
# externally authenticated R7 evidence (see ``_RoleBinding``); no ledger
# identity takes its expected value from candidate-controlled material.

CANDIDATE_CHANGE_LEDGER_SCHEMA_SUFFIX = "candidate-change-ledger-v1"
CANDIDATE_CHANGE_LEDGER_ARTIFACT_TYPE_SUFFIX = "CANDIDATE_CHANGE_LEDGER"
CANDIDATE_CHANGE_LEDGER_SEMANTICS = (
    "INDEX_OF_CANDIDATE_CHANGES_RAW_BYTE_DIFFERENCE_IS_AUTHORITATIVE"
)
CANDIDATE_CHANGE_LEDGER_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "artifact_type",
        "ledger_semantics",
        "generation_id",
        "lineage_id",
        "candidate_id",
        "candidate_artifact_paths",
        "predecessor",
        "modified_files",
        "implementation_identity",
        "authority_route",
        "scientific_authority",
        "tests_executed",
        "execution_status",
        "lifecycle_status",
    }
)
LEDGER_MODIFICATION_CLASSES: frozenset[str] = frozenset(
    {
        "LIFECYCLE_VALIDATOR_CORRECTION",
        "CANDIDATE_POINTER_ADVANCE",
        "AUTHORITY_PIN_VALUE_UPDATE",
        #: Candidate R7: bundle pin values plus the new pinned historical role
        #: identities (``R6-AUD-01``).
        "AUTHORITY_PIN_VALUE_UPDATE_AND_HISTORICAL_ROLE_IDENTITIES",
        #: Candidate R8: bundle pin values, the consumed Git-frozen trust-root
        #: identity, and the historical table demoted to a diagnostic assertion
        #: of the external derivation (``R7-AUD-01``).
        "AUTHORITY_PIN_VALUE_UPDATE_AND_EXTERNAL_TRUST_ROOT_IDENTITY",
        #: Candidate R8: negative controls realigned to the external historical
        #: authority, with the current-candidate pointer advanced.
        "TEST_NEGATIVE_CONTROL_ALIGNMENT_TO_EXTERNAL_HISTORICAL_AUTHORITY",
        "EOL_POLICY_EXACT_PATH_EXTENSION",
        "TEST_SAFETY_CORRECTION_AND_NEGATIVE_CONTROLS",
        "TEST_CURRENT_CANDIDATE_POINTER_UPDATE",
    }
)
LEDGER_TEST_RESULTS: frozenset[str] = frozenset({"OK", "FAILED", "NOT_RUN"})
#: The one implementation-digest algorithm, stated identically everywhere.
IMPLEMENTATION_DIGEST_ALGORITHM = (
    "sha256 over json.dumps({path: sha256}, sort_keys=True, "
    "separators=(',',':')) encoded utf-8"
)
LEDGER_SCIENTIFIC_PIN_LABELS: tuple[str, ...] = (
    "framework_v7_4",
    "registry_v7_4",
    "canonical_planning_input",
)
LEDGER_EXECUTION_STATUS: Mapping[str, Any] = {
    "production_solve": False,
    "main_full81_execution": False,
    "real_21c": False,
    "real_21d": False,
    "production_model_constructions": 0,
    "optimize_calls": 0,
    "milp_solves": 0,
    "full81_cases": 0,
    "a2_actions": 0,
}

CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS: tuple[IdentityObligation, ...] = (
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "implementation_digest"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor implementation digest.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "checkpoint", "raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor checkpoint raw SHA-256.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "manifest", "raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor manifest raw SHA-256.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "repository_eol_policy", "raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor-era EOL policy raw SHA-256.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "stop_package", "archive_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor STOP-package archive raw SHA-256.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "stop_package", "index_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor STOP-package raw-byte index raw SHA-256.",
    ),
    IdentityObligation(
        "L1", "ledger_predecessor",
        ("predecessor", "preserved_identity", "stop_package", "stop_record_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "Predecessor STOP record raw SHA-256.",
    ),
    IdentityObligation(
        "L2", "ledger_modified_files",
        ("modified_files", "*", "predecessor_raw_sha256"),
        AUTHORITY_HISTORICAL_ROLE,
        "A modified file's predecessor-era raw SHA-256.",
    ),
    IdentityObligation(
        "L2", "ledger_modified_files",
        ("modified_files", "*", "candidate_raw_sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "A modified file's candidate raw SHA-256.",
    ),
    IdentityObligation(
        "L3", "ledger_implementation", ("implementation_identity", "digest"),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "Candidate implementation digest.",
    ),
    IdentityObligation(
        "L3", "ledger_implementation", ("implementation_identity", "paths", "*"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Candidate implementation path inventory.",
    ),
    IdentityObligation(
        "L4", "ledger_scientific_authority",
        ("scientific_authority", "*", "raw_sha256"),
        AUTHORITY_BUNDLE_PIN,
        "Framework, Registry and canonical planning input pins.",
    ),
    IdentityObligation(
        "L5", "ledger_tests", ("tests_executed", "*", "raw_sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Raw SHA-256 of each executed validation suite.",
    ),
)


class _LedgerContext(_RoleBinding):
    """Everything one ledger validation needs, computed once."""

    def __init__(
        self,
        root: Path,
        ledger: Mapping[str, Any],
        manifest: Mapping[str, Any],
        generation: AuthorityGeneration,
        mode: str,
        label: str,
        live_identity: Mapping[str, str],
    ) -> None:
        super().__init__(root, mode, label)
        self.ledger = ledger
        self.manifest = manifest
        self.generation = generation
        self.live_identity = dict(live_identity)


def _ledger_predecessor_constant(generation: AuthorityGeneration) -> dict[str, Any]:
    predecessor_id = CONTRACT_V4_PREDECESSOR_DEFECT["predecessor_candidate_id"]
    history = PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[predecessor_id]
    return {
        "candidate_id": predecessor_id,
        "independent_audit": history["independent_audit"],
        "blocking_findings": list(history["blocking_findings"]),
        "nonblocking_findings": list(history.get("nonblocking_findings", ())),
    }


def _ledger_lifecycle_constant(generation: AuthorityGeneration) -> dict[str, Any]:
    history = PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY[generation.candidate_id]
    return {
        "candidate_disposition": history["disposition"],
        "independent_audit": history["independent_audit"],
        "publication": history["publication"],
        "acceptance": history["acceptance"],
        "production_authority": PRE_ACCEPTANCE_FREEZE_STATUS,
        "main_full81_authorization": "NOT_GRANTED",
        "a2": "HARD_BLOCKED",
    }


def _verify_ledger_predecessor(ctx: _LedgerContext, items: list[_Item]):
    """``L1``: every predecessor identity is ITS external historical role."""

    predecessor = CONTRACT_V4_PREDECESSOR_DEFECT["predecessor_candidate_id"]
    base = ("predecessor", "preserved_identity")
    roles = {
        base + ("implementation_digest",): PREDECESSOR_ROLE_IMPLEMENTATION_DIGEST,
        base + ("checkpoint", "raw_sha256"): PREDECESSOR_ROLE_CHECKPOINT,
        base + ("manifest", "raw_sha256"): PREDECESSOR_ROLE_MANIFEST,
        base + ("repository_eol_policy", "raw_sha256"): PREDECESSOR_ROLE_EOL_POLICY,
        base + ("stop_package", "archive_sha256"): preservation_role(predecessor, "archive"),
        base + ("stop_package", "index_sha256"): preservation_role(predecessor, "index"),
        base + ("stop_package", "stop_record_sha256"): preservation_role(
            predecessor, "stop_record"
        ),
    }
    _require(
        {i[0] for i in items} == set(roles) and len(items) == len(roles),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: predecessor preserved-identity fields are incomplete or extra.",
    )
    for pointer, value, _ in items:
        ctx.bind(pointer, value, ctx.historical(roles[pointer]), roles[pointer])
    # Cross-consistency with the manifest, in every mode: one predecessor.  Both
    # sides are already bound to the same pinned roles; this states it directly.
    preserved = ctx.ledger["predecessor"]["preserved_identity"]
    defect = ctx.manifest["package_binding"]["predecessor_defect"]
    package = ctx.manifest["candidate_preservation_packages"][predecessor]
    for ledger_value, manifest_value, what in (
        (
            preserved["implementation_digest"],
            ctx.manifest["implementation_identity"]["predecessor_digest"],
            "implementation digest",
        ),
        (
            preserved["checkpoint"]["raw_sha256"],
            defect["predecessor_candidate_checkpoint"]["raw_sha256"],
            "checkpoint",
        ),
        (
            preserved["manifest"]["raw_sha256"],
            defect["predecessor_candidate_manifest"]["raw_sha256"],
            "manifest",
        ),
        (preserved["stop_package"]["archive_sha256"], package["archive_sha256"], "archive"),
        (preserved["stop_package"]["index_sha256"], package["index_sha256"], "index"),
        (
            preserved["stop_package"]["stop_record_sha256"],
            package["stop_record_sha256"],
            "STOP record",
        ),
    ):
        _require(
            ledger_value == manifest_value,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: the ledger's predecessor {what} {ledger_value} disagrees "
            f"with the manifest's {manifest_value}.",
        )


def _verify_ledger_modified_files(ctx: _LedgerContext, items: list[_Item]):
    """``L2``: predecessor side is the external role; candidate side is live bytes."""

    entries = ctx.ledger["modified_files"]
    expected = set()
    for index_, _ in enumerate(entries):
        expected.add(("modified_files", index_, "predecessor_raw_sha256"))
        expected.add(("modified_files", index_, "candidate_raw_sha256"))
    _require(
        {i[0] for i in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every modified file needs exactly its two raw SHA-256 "
        "identities.",
    )
    # Closed world, in EVERY mode (contract V4): the listed change set is
    # exactly the change set derived from the externally authenticated R7
    # surface and live bytes - never a candidate-declared or table-pinned set.
    changed = sorted(ctx.predecessor_change_set())
    listed = sorted(entry["path"] for entry in entries)
    _require(
        listed == changed,
        EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
        f"{ctx.label}: the modified-file list is not the exact change set over the "
        "externally authenticated predecessor surface: "
        f"unlisted={sorted(set(changed) - set(listed))}, "
        f"not_changed={sorted(set(listed) - set(changed))}",
    )
    # Cross-consistency, in every mode: a modified file that is also an
    # implementation path or a pin target has ONE identity, not two.
    from src.production_authority_bundle_v7_4 import all_pins

    bundle_pinned = {pin.relative_path: pin.sha256 for pin in all_pins()}
    for entry in entries:
        relative = entry["path"]
        for authoritative, what in (
            (ctx.live_identity.get(relative), "implementation identity"),
            (bundle_pinned.get(relative), "authority-bundle pin"),
        ):
            if authoritative is not None:
                _require(
                    entry["candidate_raw_sha256"] == authoritative,
                    "U06_ROLE_TARGET_MISMATCH",
                    f"{ctx.label}: the ledger states {entry['candidate_raw_sha256']} "
                    f"for {relative} but its {what} is {authoritative}.",
                )
    for index_, entry in enumerate(entries):
        relative = entry["path"]
        role = predecessor_modified_file_role(relative)
        ctx.bind(
            ("modified_files", index_, "predecessor_raw_sha256"),
            entry["predecessor_raw_sha256"],
            ctx.historical(role),
            role,
        )
        ctx.bind(
            ("modified_files", index_, "candidate_raw_sha256"),
            entry["candidate_raw_sha256"],
            ctx.live_sha(relative, field="modified_files.candidate_raw_sha256"),
            f"candidate_file:{relative}",
        )


def _verify_ledger_implementation(ctx: _LedgerContext, items: list[_Item]):
    identity = ctx.ledger["implementation_identity"]
    declared = identity["paths"]
    expected = {("implementation_identity", "digest")} | {
        ("implementation_identity", "paths", relative) for relative in declared
    }
    _require(
        {i[0] for i in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: implementation inventory identities are incomplete or extra.",
    )
    _require(
        set(declared) == set(ACCEPTED_IMPLEMENTATION_PATHS),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: the ledger's implementation inventory is not the accepted "
        "implementation path set.",
    )
    for relative, value in declared.items():
        _require(
            value == ctx.live_identity[relative],
            "U06_IMPLEMENTATION_IDENTITY_DRIFT",
            f"{ctx.label}: ledger implementation path {relative} states {value} but "
            f"live bytes hash to {ctx.live_identity[relative]}.",
        )
        ctx.bind(
            ("implementation_identity", "paths", relative),
            value,
            ctx.live_identity[relative],
            f"implementation_path:{relative}",
        )
    live_digest = canonical_identity_digest(ctx.live_identity)
    _require(
        identity["digest"] == live_digest
        and identity["digest"] == ctx.manifest["implementation_identity_digest"],
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        f"{ctx.label}: the ledger's implementation digest {identity['digest']} is not "
        f"the live digest {live_digest} the manifest binds.",
    )
    ctx.bind(
        ("implementation_identity", "digest"),
        identity["digest"],
        live_digest,
        "live_implementation_digest",
    )


def _verify_ledger_scientific_authority(ctx: _LedgerContext, items: list[_Item]):
    from src.production_authority_bundle_v7_4 import all_pins

    by_label = {pin.label: pin for pin in all_pins()}
    authority = ctx.ledger["scientific_authority"]
    _require(
        sorted(i[0][1] for i in items) == sorted(LEDGER_SCIENTIFIC_PIN_LABELS)
        and len(items) == len(LEDGER_SCIENTIFIC_PIN_LABELS),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: scientific authority must state exactly "
        f"{list(LEDGER_SCIENTIFIC_PIN_LABELS)}.",
    )
    for pointer, value, _ in items:
        pin = by_label[pointer[1]]
        _require(
            authority[pointer[1]]["path"] == pin.relative_path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: scientific authority {pointer[1]} disagrees with its "
            f"authority-bundle pin {pin.relative_path} / {pin.sha256}.",
        )
        ctx.bind(pointer, value, pin.sha256, f"bundle_pin:{pin.label}")


def _verify_ledger_tests(ctx: _LedgerContext, items: list[_Item]):
    """``L5``: each executed suite's identity is that suite's live bytes."""

    suites = ctx.ledger["tests_executed"]
    expected = {("tests_executed", index_, "raw_sha256") for index_ in range(len(suites))}
    _require(
        {i[0] for i in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every executed suite needs exactly its raw SHA-256.",
    )
    for index_, entry in enumerate(suites):
        ctx.bind(
            ("tests_executed", index_, "raw_sha256"),
            entry["raw_sha256"],
            ctx.live_sha(entry["suite"], field="tests_executed.raw_sha256"),
            f"validation_suite:{entry['suite']}",
        )


#: One verifier per ledger obligation kind.
CANDIDATE_CHANGE_LEDGER_OBLIGATION_VERIFIERS: dict[str, Any] = {
    "ledger_predecessor": _verify_ledger_predecessor,
    "ledger_modified_files": _verify_ledger_modified_files,
    "ledger_implementation": _verify_ledger_implementation,
    "ledger_scientific_authority": _verify_ledger_scientific_authority,
    "ledger_tests": _verify_ledger_tests,
}


def _check_ledger_structure(
    ledger: Mapping[str, Any], generation: AuthorityGeneration, label: str
) -> None:
    def keyed(value: Any, keys: set[str], what: str) -> Mapping[str, Any]:
        _require(
            isinstance(value, Mapping) and set(value) == keys,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {what} must have exactly {sorted(keys)}; observed "
            f"{sorted(value) if isinstance(value, Mapping) else value!r}",
        )
        return value

    keyed(ledger, set(CANDIDATE_CHANGE_LEDGER_KEYS), "the ledger")
    _require(
        ledger["artifact_type"]
        == generation.artifact_type_prefix + CANDIDATE_CHANGE_LEDGER_ARTIFACT_TYPE_SUFFIX,
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type {ledger['artifact_type']!r} is not this "
        "generation's candidate change ledger type.",
    )
    _require(
        ledger["schema_version"]
        == generation.schema_prefix + CANDIDATE_CHANGE_LEDGER_SCHEMA_SUFFIX,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version {ledger['schema_version']!r} is not this "
        "generation's ledger schema.",
    )
    _require(
        ledger["ledger_semantics"] == CANDIDATE_CHANGE_LEDGER_SEMANTICS,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: ledger_semantics must be {CANDIDATE_CHANGE_LEDGER_SEMANTICS!r}.",
    )
    for field, want in (
        ("generation_id", generation.generation_id),
        ("lineage_id", generation.lineage_id),
    ):
        _require(
            ledger[field] == want,
            "U06_LINEAGE_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {ledger[field]!r}",
        )
    _require(
        ledger["candidate_id"] not in generation.superseded_candidate_ids,
        "U06_SUPERSEDED_CANDIDATE_REJECTED",
        f"{label}: candidate_id {ledger['candidate_id']!r} names a superseded "
        "candidate.",
    )
    _require(
        ledger["candidate_id"] == generation.candidate_id,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_id must be {generation.candidate_id!r}.",
    )
    _require(
        _strict_equal(
            ledger["candidate_artifact_paths"],
            {
                "checkpoint": generation.candidate_checkpoint_path,
                "manifest": generation.candidate_manifest_path,
                "change_ledger": generation.candidate_change_ledger_path,
            },
        ),
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_artifact_paths must name this candidate's checkpoint, "
        "manifest and change ledger.",
    )

    predecessor = keyed(
        ledger["predecessor"],
        {
            "candidate_id",
            "independent_audit",
            "blocking_findings",
            "nonblocking_findings",
            "preserved_identity",
        },
        "predecessor",
    )
    _require(
        _strict_equal(
            {k: v for k, v in predecessor.items() if k != "preserved_identity"},
            _ledger_predecessor_constant(generation),
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the predecessor's identity, audit outcome and findings must "
        "equal the candidate register's.",
    )
    preserved = keyed(
        predecessor["preserved_identity"],
        {"implementation_digest", "checkpoint", "manifest", "repository_eol_policy", "stop_package"},
        "predecessor.preserved_identity",
    )
    package = CANDIDATE_PRESERVATION_PACKAGES[
        CONTRACT_V4_PREDECESSOR_DEFECT["predecessor_candidate_id"]
    ]
    directory = package["directory"]
    for field, path in (
        ("checkpoint", CONTRACT_V4_PREDECESSOR_DEFECT["checkpoint_path"]),
        ("manifest", CONTRACT_V4_PREDECESSOR_DEFECT["manifest_path"]),
        ("repository_eol_policy", EOL_POLICY_RELATIVE_PATH),
    ):
        entry = keyed(preserved[field], {"path", "raw_sha256"}, f"preserved_identity.{field}")
        _require(
            entry["path"] == path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: preserved_identity.{field}.path must be {path}.",
        )
    stop = keyed(
        preserved["stop_package"],
        {
            "directory",
            "archive_path",
            "archive_sha256",
            "index_path",
            "index_sha256",
            "stop_record_path",
            "stop_record_sha256",
        },
        "preserved_identity.stop_package",
    )
    for field, want in (
        ("directory", directory),
        ("archive_path", f"{directory}/{package['archive']}"),
        ("index_path", f"{directory}/{package['index']}"),
        ("stop_record_path", f"{directory}/{package['stop_record']}"),
    ):
        _require(
            stop[field] == want,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: preserved_identity.stop_package.{field} must be {want}.",
        )

    entries = ledger["modified_files"]
    _require(
        isinstance(entries, list) and entries,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: modified_files must be a non-empty list.",
    )
    for entry in entries:
        keyed(
            entry,
            {"path", "predecessor_raw_sha256", "candidate_raw_sha256", "classification", "summary"},
            "a modified_files entry",
        )
        _require(
            entry["classification"] in LEDGER_MODIFICATION_CLASSES
            and isinstance(entry["summary"], str)
            and entry["summary"].strip()
            and entry["predecessor_raw_sha256"] != entry["candidate_raw_sha256"],
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: modified file {entry.get('path')!r} needs a known "
            "classification, a summary, and two DIFFERENT identities.",
        )
    paths = [entry["path"] for entry in entries]
    _require(
        paths == sorted(set(paths)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: modified_files must be unique and sorted by path; observed {paths}",
    )

    identity = keyed(
        ledger["implementation_identity"],
        {"path_count", "digest_algorithm", "digest", "paths"},
        "implementation_identity",
    )
    _require(
        identity["path_count"] == len(ACCEPTED_IMPLEMENTATION_PATHS)
        and identity["digest_algorithm"] == IMPLEMENTATION_DIGEST_ALGORITHM
        and isinstance(identity["paths"], Mapping),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: implementation_identity metadata is inconsistent.",
    )
    _require(
        _strict_equal(
            ledger["authority_route"],
            {
                "runtime_production_dependency_paths": list(
                    RUNTIME_PRODUCTION_DEPENDENCY_PATHS
                ),
                "gate_protected_dependency_paths": list(GATE_PROTECTED_DEPENDENCY_PATHS),
                "validation_identity_paths": list(VALIDATION_IDENTITY_PATHS),
            },
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: authority_route must be exactly the declared runtime, "
        "gate-protected and validation path sets.",
    )
    authority = ledger["scientific_authority"]
    _require(
        isinstance(authority, Mapping)
        and sorted(authority) == sorted(LEDGER_SCIENTIFIC_PIN_LABELS)
        and all(
            isinstance(v, Mapping) and set(v) == {"path", "raw_sha256"}
            for v in authority.values()
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: scientific_authority must state exactly "
        f"{list(LEDGER_SCIENTIFIC_PIN_LABELS)} as path + raw_sha256.",
    )
    suites = ledger["tests_executed"]
    _require(
        isinstance(suites, list) and suites,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: tests_executed must be a non-empty list.",
    )
    for entry in suites:
        keyed(
            entry,
            {"suite", "raw_sha256", "ran", "failures", "errors", "skipped", "result"},
            "a tests_executed entry",
        )
        counts = [entry[k] for k in ("ran", "failures", "errors", "skipped")]
        _require(
            entry["suite"] in VALIDATION_IDENTITY_PATHS
            and all(isinstance(c, int) and not isinstance(c, bool) and c >= 0 for c in counts)
            and entry["result"] in LEDGER_TEST_RESULTS
            and (entry["result"] == "OK")
            == (entry["ran"] > 0 and entry["failures"] == 0 and entry["errors"] == 0)
            and (entry["result"] == "NOT_RUN") == (entry["ran"] == 0)
            and (entry["result"] != "NOT_RUN" or not any(counts)),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: executed suite {entry.get('suite')!r} is not a validation "
            "suite or states inconsistent counts and result.",
        )
    names = [entry["suite"] for entry in suites]
    _require(
        len(names) == len(set(names)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: an executed suite is listed twice.",
    )
    _require(
        _strict_equal(ledger["execution_status"], dict(LEDGER_EXECUTION_STATUS)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: execution_status must record no production solve, no Full81, "
        "no real 21c / 21d, and zero model constructions, optimizer calls, MILP "
        "solves, Full81 cases and A2 actions.",
    )
    _require(
        _strict_equal(ledger["lifecycle_status"], _ledger_lifecycle_constant(generation)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: lifecycle_status must equal the candidate register's state.",
    )


def validate_candidate_change_ledger(
    root: Path,
    ledger_bytes: bytes,
    manifest: Mapping[str, Any],
    generation: AuthorityGeneration | None = None,
    *,
    mode: str,
    live_identity: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Validate a candidate change ledger: structure, then closed-world identity.

    Fail-closed.  ``manifest`` is the already strictly-parsed candidate manifest
    that binds this ledger; the ledger may never disagree with it.  Read-only.
    """

    root = Path(root).resolve()
    generation = generation or CURRENT_GENERATION
    _require(
        mode in CANDIDATE_MANIFEST_MODES,
        "U06_ROLE_SCHEMA_INVALID",
        f"candidate change ledger: unknown validation mode {mode!r}.",
    )
    _require(
        bool(generation.candidate_change_ledger_path),
        "U06_ROLE_SCHEMA_INVALID",
        f"generation {generation.generation_id} declares no candidate change ledger.",
    )
    label = f"candidate change ledger ({generation.candidate_change_ledger_path})"
    ledger = _strict_json_object(ledger_bytes, label=label)
    _check_ledger_structure(ledger, generation, label)

    identities, hidden = collect_identity_pointers(ledger)
    _require(
        not hidden,
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: raw identities hidden in prose, keys or malformed values: "
        f"{['.'.join(map(str, p)) for p in hidden]}",
    )
    # No identity in the ledger may be tied to the candidate artifacts that are
    # finalized at or after it: any such value would be stale or self-referential.
    later = {
        generation.candidate_change_ledger_path,
        generation.candidate_checkpoint_path,
        generation.candidate_manifest_path,
    }
    for pointer, _ in identities:
        tied = later & _associated_paths(ledger, pointer)
        _require(
            not tied,
            "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
            f"{label}: {'.'.join(map(str, pointer))} asserts an identity of "
            f"{sorted(tied)}, which is finalized at or after the ledger.",
        )
    owned = _own_identity_pointers(
        identities, CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS, label
    )
    context = _LedgerContext(
        root,
        ledger,
        manifest,
        generation,
        mode,
        label,
        live_identity if live_identity is not None else implementation_identity(root),
    )
    verified, structural = _verify_owned_identities(
        owned, identities, CANDIDATE_CHANGE_LEDGER_OBLIGATION_VERIFIERS, context, label
    )
    return {
        "ledger_path": generation.candidate_change_ledger_path,
        "mode": mode,
        "collected_identity_count": len(identities),
        "verified_identity_count": len(verified),
        "structural_identity_count": len(structural),
        "role_bound_identity_count": len(context.authority),
        "unaccounted_identity_count": 0,
        "historical_pins_proved_against_preserved_bytes": context.proves_preserved_bytes,
        "obligation_classes": sorted(
            {o.obligation_class for o in CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS}
        ),
        "modified_file_count": len(ledger["modified_files"]),
        "executed_suite_count": len(ledger["tests_executed"]),
    }


#: One verifier per obligation kind.  A kind with no verifier, or a verifier
#: that does not account for every pointer it is handed, fails parity.
CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS: dict[str, Any] = {
    "candidate_checkpoint": _verify_candidate_checkpoint,
    "implementation_digest": _verify_implementation_digest,
    "implementation_paths": _verify_implementation_paths,
    "bundle_pins": _verify_bundle_pins,
    "durable_pinned": _verify_durable_pinned,
    "preservation": _verify_preservation,
    "predecessor_evidence": _verify_predecessor_evidence,
    "candidate_change_ledger": _verify_candidate_change_ledger,
}


def _check_candidate_manifest_self_identity(
    payload: Mapping[str, Any], generation: AuthorityGeneration, label: str
) -> None:
    """``C8``: the manifest's own identity is never asserted internally."""

    own = generation.candidate_manifest_path
    identities, hidden = collect_identity_pointers(payload)
    for pointer in [p for p, _ in identities] + hidden:
        _require(
            own not in _associated_paths(payload, pointer),
            "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
            f"{label}: {'.'.join(map(str, pointer))} asserts a raw SHA-256 tied "
            f"to the manifest's own path {own}. The final identity of a file can "
            "never be embedded in its own bytes; it is bound externally by "
            f"{list(candidate_manifest_external_binding_fields(generation))}.",
        )
    declaration = payload.get("durable_publication_declaration")
    entries = declaration.get("entries") if isinstance(declaration, Mapping) else None
    if isinstance(entries, Mapping) and own in entries:
        entry = entries[own]
        _require(
            isinstance(entry, Mapping)
            and set(entry) == {"identity_source", "external_binding_fields"}
            and entry.get("identity_source") == DURABLE_IDENTITY_SOURCE_EXTERNAL,
            "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
            f"{label}: the manifest's own durable entry must state only "
            f"identity_source={DURABLE_IDENTITY_SOURCE_EXTERNAL!r} and its "
            "external_binding_fields; any other claim about its own identity "
            f"is rejected. Observed keys: "
            f"{sorted(entry) if isinstance(entry, Mapping) else entry!r}",
        )


def _check_candidate_manifest_constants(
    payload: Mapping[str, Any],
    generation: AuthorityGeneration,
    relative: str,
    label: str,
) -> None:
    contract = generation.role_contracts["implementation_candidate"]
    _require(
        payload.get("artifact_type") == contract.artifact_type
        and payload.get("role") == "implementation_candidate",
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type/role must be {contract.artifact_type!r} / "
        f"'implementation_candidate'; observed {payload.get('artifact_type')!r} / "
        f"{payload.get('role')!r}",
    )
    _require(
        payload.get("schema_version") == contract.schema_version,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version must be {contract.schema_version!r}.",
    )
    for field, want in (
        ("generation_id", generation.generation_id),
        ("lineage_id", generation.lineage_id),
    ):
        _require(
            payload.get(field) == want,
            "U06_LINEAGE_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {payload.get(field)!r}",
        )
    for field in ("candidate_id", "target_candidate_id"):
        value = payload.get(field)
        _require(
            value not in generation.superseded_candidate_ids,
            "U06_SUPERSEDED_CANDIDATE_REJECTED",
            f"{label}: {field} {value!r} names a superseded candidate. A failed "
            "candidate may never be revived.",
        )
        _require(
            value == generation.candidate_id,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: {field} must be {generation.candidate_id!r}; observed {value!r}",
        )
    for field, want in (
        ("candidate_revision", generation.candidate_id.rsplit("_", 1)[-1]),
        ("candidate_checkpoint_path", generation.candidate_checkpoint_path),
        ("candidate_manifest_path", generation.candidate_manifest_path),
        ("accepted_lifecycle_record_path", generation.accepted_lifecycle_record_path),
    ):
        _require(
            payload.get(field) == want,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {payload.get(field)!r}",
        )
    _require(
        relative == generation.candidate_manifest_path,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: validated at {relative}, not at "
        f"{generation.candidate_manifest_path}.",
    )
    _require(
        payload.get("self_accepted") is False,
        "U06_SELF_ACCEPTANCE_REJECTED",
        f"{label}: self_accepted must be literally false.",
    )
    history = PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY.get(generation.candidate_id)
    _require(
        history is not None
        and payload.get("disposition") == history.get("disposition"),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: disposition must equal the candidate register's "
        f"{(history or {}).get('disposition')!r}.",
    )


def _check_candidate_manifest_structure(
    payload: Mapping[str, Any], generation: AuthorityGeneration, label: str
) -> None:
    def section(name: str, keys: frozenset[str]) -> Mapping[str, Any]:
        value = payload.get(name)
        _require(
            isinstance(value, Mapping) and set(value) == keys,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {name} must have exactly {sorted(keys)}; observed "
            f"{sorted(value) if isinstance(value, Mapping) else value!r}",
        )
        return value

    # package_binding and its typed predecessor evidence.
    binding = section("package_binding", PACKAGE_BINDING_KEYS)
    for field, want in (
        ("scheme", PACKAGE_BINDING_SCHEME),
        ("direction", PACKAGE_BINDING_DIRECTION),
        ("manifest_self_identity", DURABLE_IDENTITY_SOURCE_EXTERNAL),
    ):
        _require(
            binding.get(field) == want,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: package_binding.{field} must be {want!r}.",
        )
    defect = binding.get("predecessor_defect")
    _require(
        isinstance(defect, Mapping) and set(defect) == PREDECESSOR_DEFECT_KEYS,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: package_binding.predecessor_defect must have exactly "
        f"{sorted(PREDECESSOR_DEFECT_KEYS)}",
    )
    want = CONTRACT_V4_PREDECESSOR_DEFECT
    _require(
        defect.get("findings") == list(want["findings"])
        and defect.get("predecessor_candidate_id") == want["predecessor_candidate_id"]
        and defect.get("evidence_class") == PREDECESSOR_DEFECT_EVIDENCE_CLASS
        and defect.get("defect_location") == PREDECESSOR_DEFECT_LOCATION_CODE,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: predecessor_defect must be typed {list(want['findings'])} "
        f"evidence of {want['predecessor_candidate_id']}.",
    )
    _require(
        want["predecessor_candidate_id"] in generation.superseded_candidate_ids,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the evidenced predecessor must be a superseded candidate.",
    )
    current = {
        generation.candidate_checkpoint_path,
        generation.candidate_manifest_path,
        generation.candidate_change_ledger_path,
    }
    for field, path in (
        ("predecessor_candidate_checkpoint", want["checkpoint_path"]),
        ("predecessor_candidate_manifest", want["manifest_path"]),
    ):
        entry = defect.get(field)
        _require(
            isinstance(entry, Mapping)
            and set(entry) == {"path", "raw_sha256"}
            and entry.get("path") == path
            and path in generation.candidate_artifact_paths
            and path not in current,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: predecessor_defect.{field} must name the barred "
            f"predecessor artifact {path}.",
        )
    package = CANDIDATE_PRESERVATION_PACKAGES.get(want["predecessor_candidate_id"])
    _require(
        package is not None
        and defect.get("recorded_in_stop_record")
        == {"path": f"{package['directory']}/{package['stop_record']}"},
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: recorded_in_stop_record must name the predecessor's "
        "preserved STOP record.",
    )

    # candidate_checkpoint: the one embedded checkpoint identity.
    checkpoint = section("candidate_checkpoint", frozenset({"path", "sha256"}))
    _require(
        checkpoint.get("path") == generation.candidate_checkpoint_path,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_checkpoint.path must be "
        f"{generation.candidate_checkpoint_path}.",
    )
    # candidate_change_ledger: the one embedded ledger identity (C9).
    ledger = section("candidate_change_ledger", frozenset({"path", "sha256"}))
    _require(
        ledger.get("path") == generation.candidate_change_ledger_path,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_change_ledger.path must be "
        f"{generation.candidate_change_ledger_path}.",
    )

    # Static durable-publication declaration.
    declaration = section("durable_publication_declaration", DURABLE_DECLARATION_KEYS)
    _require(
        declaration.get("semantics") == DURABLE_DECLARATION_SEMANTICS
        and declaration.get("live_status_source")
        == DURABLE_DECLARATION_LIVE_STATUS_SOURCE,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the durable-publication declaration must be a static "
        "declaration whose live status comes from the live report only.",
    )
    required = _required_durable_paths_for(generation)
    declared_paths = declaration.get("required_paths")
    _require(
        isinstance(declared_paths, list)
        and len(declared_paths) == len(set(map(str, declared_paths))),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: duplicate durable declaration path in {declared_paths!r}",
    )
    _require(
        declared_paths == list(required),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: required_paths must be exactly {list(required)}; missing="
        f"{sorted(set(required) - set(declared_paths))}, extra="
        f"{sorted(set(declared_paths) - set(required))}",
    )
    entries = declaration.get("entries")
    _require(
        isinstance(entries, Mapping) and set(entries) == set(required),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: durable entries must cover exactly the required paths.",
    )
    for relative, entry in entries.items():
        if relative in REQUIRED_DURABLE_PUBLICATION_PIN_LABELS:
            _require(
                isinstance(entry, Mapping)
                and set(entry)
                == {"identity_source", "pin_label", "expected_raw_sha256"}
                and entry.get("identity_source") == DURABLE_IDENTITY_SOURCE_PIN
                and entry.get("pin_label")
                == REQUIRED_DURABLE_PUBLICATION_PIN_LABELS[relative],
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: pinned durable entry {relative} must state exactly its "
                "identity source, pin label and expected raw SHA-256.",
            )
        elif relative == generation.candidate_checkpoint_path:
            _require(
                entry
                == {
                    "identity_source": DURABLE_IDENTITY_SOURCE_CHECKPOINT_FIELD,
                    "identity_field": DURABLE_CHECKPOINT_IDENTITY_FIELD,
                },
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the checkpoint durable entry must refer to "
                f"{DURABLE_CHECKPOINT_IDENTITY_FIELD} and carry no duplicate "
                "digest: one identity fact has one authoritative location.",
            )
        elif relative == generation.candidate_change_ledger_path:
            _require(
                entry
                == {
                    "identity_source": DURABLE_IDENTITY_SOURCE_LEDGER_FIELD,
                    "identity_field": DURABLE_LEDGER_IDENTITY_FIELD,
                },
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the change-ledger durable entry must refer to "
                f"{DURABLE_LEDGER_IDENTITY_FIELD} and carry no duplicate digest.",
            )
        else:
            _require(
                entry.get("external_binding_fields")
                == list(candidate_manifest_external_binding_fields(generation)),
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the manifest's own durable entry must declare exactly "
                f"the external binding fields "
                f"{list(candidate_manifest_external_binding_fields(generation))}.",
            )

    # Remaining identity sections: exact shape and constant metadata.
    identity = section("implementation_identity", IMPLEMENTATION_IDENTITY_KEYS)
    _require(
        identity.get("path_count") == len(ACCEPTED_IMPLEMENTATION_PATHS)
        and isinstance(identity.get("paths"), Mapping)
        and identity.get("predecessor_digest_carried_forward")
        is (identity.get("predecessor_digest") == identity.get("implementation_digest")),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: implementation_identity metadata is inconsistent (path_count, "
        "paths map, or a predecessor_digest_carried_forward self-label that "
        "does not match the declared digests).",
    )
    from src.production_authority_bundle_v7_4 import PIN_GROUPS, all_pins

    bundle = section("authority_bundle", AUTHORITY_BUNDLE_KEYS)
    pins = bundle.get("pins")
    _require(
        bundle.get("declared_pin_groups") == len(PIN_GROUPS)
        and bundle.get("declared_pin_count") == len(all_pins())
        and isinstance(pins, Mapping)
        and all(
            isinstance(v, Mapping) and set(v) == {"path", "sha256"}
            for v in pins.values()
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: authority_bundle counts or pin entries are malformed.",
    )
    eol = section("repository_eol_policy", REPOSITORY_EOL_POLICY_KEYS)
    _require(
        eol.get("path") == EOL_POLICY_RELATIVE_PATH
        and eol.get("bundle_pin_label") == "repository_eol_policy",
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: repository_eol_policy must restate the .gitattributes pin.",
    )
    registry = section(
        "parameter_registry_durability", PARAMETER_REGISTRY_DURABILITY_KEYS
    )
    _require(
        registry.get("path") == "data/reference/parameter_registry_v7_2.csv"
        and registry.get("bundle_pin_label") == "parameter_registry",
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: parameter_registry_durability must restate the "
        "parameter_registry pin.",
    )


def _check_identity_path_conflicts(
    payload: Mapping[str, Any],
    identities: Sequence[tuple[tuple[Any, ...], str]],
    label: str,
) -> None:
    by_path: dict[str, set[str]] = {}
    for pointer, value in identities:
        target = _identity_target_path(payload, pointer)
        if target is not None:
            by_path.setdefault(target, set()).add(value)
    conflicts = {path: sorted(v) for path, v in by_path.items() if len(v) > 1}
    _require(
        not conflicts,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: the same path carries conflicting identities: {conflicts}",
    )


def checkpoint_identity_tokens(text: str) -> list[str]:
    """Every run of 64+ hex characters in a checkpoint, as written."""

    return _HEX_RUN_RE.findall(text)


#: ``R5-AUD-01`` remediation: the ONE place a checkpoint may state a raw
#: identity.  A fenced block opened by exactly this line and closed by exactly
#: ``CHECKPOINT_CLAIM_FENCE_CLOSE``; every non-blank line inside it is a claim
#: ``<RFC 6901 manifest pointer> <lowercase 64-hex digest>`` and nothing else.
#: No label, heading, table cell or comment ever confers a role on a digest.
CHECKPOINT_CLAIM_FENCE_OPEN = "```identity-claims"
CHECKPOINT_CLAIM_FENCE_CLOSE = "```"
_CHECKPOINT_CLAIM_LINE_RE = re.compile(r"^(/\S*) ([0-9a-f]{64})$")
#: The checkpoint is finalized BEFORE the manifest records its digest, so it
#: can never truthfully claim that digest: such a claim is self-referential.
CHECKPOINT_SELF_IDENTITY_POINTER = "/candidate_checkpoint/sha256"


def parse_checkpoint_identity_claims(text: str) -> dict[str, Any]:
    """Split a checkpoint into canonical identity claims and everything else.

    Pure and read-only.  Returns the claims ``(line, pointer, digest)``, any
    malformed claim-block lines, every run of 64+ hex characters OUTSIDE a
    claim block (each one an unclassified identity), the number of claim
    blocks, and whether a claim block was left unterminated.
    """

    claims: list[tuple[int, str, str]] = []
    malformed: list[tuple[int, str]] = []
    outside: list[tuple[int, str]] = []
    blocks = 0
    open_line: int | None = None
    for number, line in enumerate(text.split("\n"), start=1):
        if open_line is None:
            if line == CHECKPOINT_CLAIM_FENCE_OPEN:
                open_line = number
                blocks += 1
                continue
            outside.extend((number, token) for token in _HEX_RUN_RE.findall(line))
            continue
        if line == CHECKPOINT_CLAIM_FENCE_CLOSE:
            open_line = None
            continue
        if not line.strip():
            continue
        match = _CHECKPOINT_CLAIM_LINE_RE.match(line)
        if match:
            claims.append((number, match.group(1), match.group(2)))
        else:
            malformed.append((number, line))
    return {
        "claims": claims,
        "malformed": malformed,
        "outside_identities": outside,
        "block_count": blocks,
        "unterminated_block_line": open_line,
    }


_RFC6901_TOKEN_RE = re.compile(r"^(?:[^~/]|~[01])*$")


def parse_rfc6901_pointer(text: str) -> tuple[str, ...] | None:
    """Strictly decode an RFC 6901 JSON pointer, or ``None`` if malformed.

    ``R6-AUD-01`` closed-world claim grammar.  The pointer must be non-empty
    (the document root is a container, never an identity), start with ``/``,
    and use ``~`` only as ``~0`` / ``~1``.  A pointer that decodes is then
    looked up by its exact canonical spelling, so an equivalent-but-different
    spelling of one target can never name a second role.
    """

    if not isinstance(text, str) or not text.startswith("/"):
        return None
    tokens = text[1:].split("/")
    if not all(_RFC6901_TOKEN_RE.match(token) for token in tokens):
        return None
    decoded = tuple(t.replace("~1", "/").replace("~0", "~") for t in tokens)
    if rfc6901_pointer(decoded) != text:
        return None
    return decoded


def _check_checkpoint_identity_claims(
    root: Path,
    generation: AuthorityGeneration,
    binding: _RoleBinding,
    label: str,
) -> dict[str, int]:
    """Every checkpoint identity is a claim of one BOUND role, valued by it.

    ``R5-AUD-01`` / ``R6-AUD-01`` remediation.  Under contract V1 a checkpoint
    digest needed only to occur somewhere in the manifest; under V2 it needed
    only to equal the manifest's own value at its pointer, so rebinding claims
    to a consistently permuted manifest passed.  Under V3 a digest is accepted
    only as a canonical claim of one identity pointer that the obligation
    verifiers BOUND to a role, and only if it equals that role's independently
    established value (``binding.authority``) - never the manifest's bytes.
    Any digest outside a claim, any malformed or unknown pointer (including a
    container, a non-canonical spelling or a non-identity field), any duplicate
    or conflicting claim and any claim of the checkpoint's own identity fails
    closed.  Labels are never consulted.
    """

    text = (root / generation.candidate_checkpoint_path).read_text(encoding="utf-8")
    parsed = parse_checkpoint_identity_claims(text)
    _require(
        parsed["unterminated_block_line"] is None,
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: the identity-claims block opened at checkpoint line "
        f"{parsed['unterminated_block_line']} is never closed.",
    )
    _require(
        not parsed["outside_identities"],
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: the candidate checkpoint states raw identities outside a "
        "canonical identity claim, so their role is unclassified: "
        f"{[f'line {n}: {t}' for n, t in parsed['outside_identities']]}. A "
        "digest is only ever stated as a claim of the manifest identity pointer "
        "that owns it; no label confers a role.",
    )
    _require(
        not parsed["malformed"],
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: malformed identity-claim lines "
        f"{[f'line {n}: {t!r}' for n, t in parsed['malformed']]}.",
    )
    claimable = {
        rfc6901_pointer(pointer): (binding.roles[pointer], value)
        for pointer, value in binding.authority.items()
    }
    first_line: dict[str, int] = {}
    for number, pointer, digest in parsed["claims"]:
        _require(
            parse_rfc6901_pointer(pointer) is not None,
            "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
            f"{label}: line {number} claims {pointer!r}, which is not a "
            "well-formed RFC 6901 pointer.",
        )
        _require(
            pointer not in first_line,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {pointer} is claimed at checkpoint lines "
            f"{first_line.get(pointer)} and {number}; one identity field has "
            "exactly one claim.",
        )
        first_line[pointer] = number
        _require(
            pointer != CHECKPOINT_SELF_IDENTITY_POINTER,
            "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
            f"{label}: line {number} claims the checkpoint's own identity. The "
            "checkpoint is finalized before the manifest records that digest, "
            "so any such claim is self-referential.",
        )
        _require(
            pointer in claimable,
            "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
            f"{label}: line {number} claims {pointer}, which is not a role-bound "
            "identity field of the candidate manifest.",
        )
        role, authority = claimable[pointer]
        _require(
            authority == digest,
            EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH
            if is_historical_role(role)
            else "U06_ROLE_TARGET_MISMATCH",
            f"{label}: line {number} presents {digest} as {pointer}, but that "
            f"pointer's role {role!r} is "
            + (
                "established by the externally authenticated historical authority "
                if is_historical_role(role)
                else "independently established "
            )
            + f"as {authority}. A digest lawful for one role is never accepted "
            "in another.",
        )
    return {
        "checkpoint_identity_claim_count": len(parsed["claims"]),
        "checkpoint_identity_claim_block_count": parsed["block_count"],
        "checkpoint_identity_token_count": len({d for _, _, d in parsed["claims"]}),
        "checkpoint_unclassified_identity_count": 0,
    }


def external_historical_authority_declaration(
    authority: Mapping[str, Any],
) -> dict[str, Any]:
    """What a V4 candidate manifest must declare it consumes, from the chain.

    Derived from an authenticated :func:`resolve_external_historical_authority`
    result.  Git identities and the binding LOCATOR only: the binding's SHA-256
    is stated by the frozen trust root alone, so restating it here would create
    a second, candidate-controlled statement of it.
    """

    trust = authority["trust_root"]
    return {
        "semantics": (
            "CONSUMED_EXTERNALLY_FROZEN_HISTORICAL_AUTHORITY_NOT_SELECTED_OR_"
            "REDEFINED_BY_THIS_CANDIDATE"
        ),
        "trust_root": {
            "tag_ref": trust["tag_ref"],
            "tag_object": trust["tag_object"],
            "commit": trust["commit"],
            "path": trust["path"],
            "blob": trust["blob"],
        },
        "binding_locator_source": "PRE_R8_TRUST_ROOT_GIT_BLOB",
        "binding_path": authority["binding"]["path"],
        "predecessor_candidate_id": authority["predecessor_candidate_id"],
        "predecessor_package_directory": authority["preservation_packages"][
            authority["predecessor_candidate_id"]
        ]["directory"],
        "historical_role_value_source": AUTHORITY_HISTORICAL_ROLE,
        "candidate_local_historical_table": "DIAGNOSTIC_ASSERTION_ONLY_NO_FALLBACK",
    }


def _check_external_authority_declaration(
    payload: Mapping[str, Any], context: "_ContractContext", label: str
) -> dict[str, Any]:
    """Contract V4: authenticate the external chain and match the declaration."""

    authority = context.external()
    expected = external_historical_authority_declaration(authority)
    _require(
        _strict_equal(payload.get("external_historical_authority"), expected),
        EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH,
        f"{label}: external_historical_authority does not declare exactly the "
        "authenticated pre-R8 trust root and the R7 binding it selects.",
    )
    return {
        "authenticated": True,
        "trust_root_tag_ref": authority["trust_root"]["tag_ref"],
        "trust_root_tag_object": authority["trust_root"]["tag_object"],
        "trust_root_commit": authority["trust_root"]["commit"],
        "trust_root_blob": authority["trust_root"]["blob"],
        "binding_path": authority["binding"]["path"],
        "historical_role_count": len(authority["roles"]),
        "predecessor_surface_path_count": len(authority["predecessor_surface"]),
    }


def validate_candidate_manifest_identity_contract(
    root: Path,
    relative: str | None = None,
    payload: Mapping[str, Any] | None = None,
    generation: AuthorityGeneration | None = None,
    *,
    mode: str,
    manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Validate a candidate manifest against its generation's content contract.

    Fail-closed and ordered so the raised status names the real defect:
    duplicate keys, contract marker, own identity (``C8``), forbidden snapshot
    and self-label keys, envelope constants, field classification, section
    structure, closed-world identity ownership, same-path conflicts, obligation
    verification (including the bound change ledger, ``C9``), pointer parity,
    and finally the checkpoint's semantic identity claims.

    ``manifest_bytes`` validates those exact bytes instead of reading
    ``relative`` from ``root``; the strictly parsed bytes are always what is
    validated, and a supplied ``payload`` must equal them.

    Read-only.  Returns a report whose ``computed_binding_facts`` are the
    honest, validator-derived replacements for the R4 self-labels.
    """

    root = Path(root).resolve()
    generation = generation or CURRENT_GENERATION
    relative = (relative or generation.candidate_manifest_path).replace("\\", "/").strip()
    label = f"candidate manifest ({relative})"
    _require(
        mode in CANDIDATE_MANIFEST_MODES,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: unknown validation mode {mode!r}.",
    )
    contract = generation.candidate_manifest_contract
    _require(
        contract in KNOWN_CANDIDATE_MANIFEST_CONTRACTS,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: generation {generation.generation_id} names no known "
        f"candidate-manifest contract ({contract!r}).",
    )
    # G1: this validator implements contract V4 and nothing else.  Another
    # known contract has its own validator (see
    # validate_candidate_manifest_content_contract); judging it here would
    # apply V4's R7-predecessor obligations to a generation they are false for.
    _require(
        contract == FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: generation {generation.generation_id} declares contract "
        f"{contract!r}; this validator implements only "
        f"{FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4!r}.",
    )
    if manifest_bytes is None:
        path = root / relative
        _require(
            path.is_file(),
            "U06_ROLE_ARTIFACT_MISSING",
            f"{label}: candidate manifest is missing.",
        )
        manifest_bytes = path.read_bytes()
    strict = _strict_json_object(manifest_bytes, label=label)
    _require(
        payload is None or dict(payload) == strict,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the payload under validation is not exactly the strictly "
        "parsed manifest bytes.",
    )
    payload = strict

    _require(
        payload.get("candidate_manifest_contract") == contract,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: candidate_manifest_contract must be {contract!r}; observed "
        f"{payload.get('candidate_manifest_contract')!r}. A manifest written "
        "under no contract, or under a superseded one, cannot fill this role.",
    )
    _check_candidate_manifest_self_identity(payload, generation, label)

    forbidden: list[str] = []

    def find_forbidden(node: Any, pointer: tuple[Any, ...]) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if key in CANDIDATE_MANIFEST_FORBIDDEN_KEYS:
                    forbidden.append(".".join(map(str, pointer + (key,))))
                find_forbidden(value, pointer + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                find_forbidden(value, pointer + (index,))

    find_forbidden(payload, ())
    _require(
        not forbidden,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: frozen live-report or self-label fields are forbidden in a "
        f"candidate manifest: {sorted(forbidden)}. Live status belongs to the "
        "live report; identity truthfulness is computed by the validator.",
    )
    _check_candidate_manifest_constants(payload, generation, relative, label)

    keys = set(payload)
    classified = set(CANDIDATE_MANIFEST_FIELD_CLASSES)
    _require(
        keys == classified,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: top-level fields must be exactly the classified set; "
        f"unclassified={sorted(keys - classified)}, "
        f"missing={sorted(classified - keys)}",
    )
    _check_candidate_manifest_structure(payload, generation, label)

    identities, hidden = collect_identity_pointers(payload)
    _require(
        not hidden,
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: raw identities hidden in prose, keys or malformed values: "
        f"{['.'.join(map(str, p)) for p in hidden]}",
    )
    obligations = CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS
    owned = _own_identity_pointers(identities, obligations, label)
    _check_identity_path_conflicts(payload, identities, label)

    context = _ContractContext(root, payload, generation, mode, label)
    # Contract V4: authenticate the external historical authority FIRST, in
    # every mode, before any identity is bound; the manifest's declaration of
    # what it consumes must be exactly the authenticated chain.
    external_report = _check_external_authority_declaration(payload, context, label)
    verified, structural = _verify_owned_identities(
        owned, identities, CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS, context, label
    )
    checkpoint_report = _check_checkpoint_identity_claims(
        root, generation, context, label
    )

    return {
        "contract": contract,
        "mode": mode,
        "manifest_path": relative,
        "collected_identity_count": len(identities),
        "verified_identity_count": len(verified),
        "structural_identity_count": len(structural),
        "role_bound_identity_count": len(context.authority),
        "historical_pins_proved_against_preserved_bytes": context.proves_preserved_bytes,
        "unaccounted_identity_count": 0,
        "conflict_count": 0,
        "obligation_classes": sorted({o.obligation_class for o in obligations}),
        "obligation_kinds": sorted(owned),
        "forbidden_identity_class": CANDIDATE_MANIFEST_FORBIDDEN_IDENTITY_CLASS,
        "verified_pointers": sorted(".".join(map(str, p)) for p in verified),
        "identity_roles": dict(
            sorted((".".join(map(str, p)), role) for p, role in context.roles.items())
        ),
        "structural_pointers": sorted(".".join(map(str, p)) for p in structural),
        "external_binding_fields": list(
            candidate_manifest_external_binding_fields(generation)
        ),
        **checkpoint_report,
        "external_historical_authority": external_report,
        "change_ledger": context.ledger_report,
        "computed_binding_facts": {
            "manifest_binds_checkpoint_path": True,
            "manifest_binds_checkpoint_raw_sha256": True,
            "manifest_binds_change_ledger_raw_sha256": True,
            "manifest_records_own_sha256": False,
            "checkpoint_records_unaccounted_raw_sha256": False,
            "checkpoint_identity_roles_verified": True,
            "structural_only_identities_accepted": False,
            "mutual_raw_hash_cycle_present": False,
            "placeholder_or_stale_sha_used": False,
            "derivation": (
                "Computed by validate_candidate_manifest_identity_contract from "
                "the manifest, change-ledger and checkpoint bytes; never read "
                "from a self-label."
            ),
        },
    }


# ---------------------------------------------------------------------------
# Current Full81 Production Generation G1: three separately versioned identities
# ---------------------------------------------------------------------------
#
# G1 keeps four version axes apart: methodology (Framework v7.4, unchanged),
# the production RUNTIME generation, the VALIDATION generation, and the
# GOVERNANCE / AUTHORITY generation.  The last three are each one identity:
#
# ``G1_RUNTIME_IDENTITY``
#     The 21 :data:`ACCEPTED_IMPLEMENTATION_PATHS`; its digest is THE
#     implementation digest every lifecycle role and authorization binds.
# ``G1_VALIDATION_IDENTITY``
#     The :data:`VALIDATION_IDENTITY_PATHS` suites.
# ``G1_GOVERNANCE_AUTHORITY_IDENTITY``
#     Every other path whose exact bytes runtime code pins: the authority-
#     bundle pin targets and the FULLSTACK-01 execution-input pins, minus the
#     runtime and validation members.  It is DERIVED from those pin tables, so
#     it cannot drift from what the runtime actually enforces.
#
# The three member sets are disjoint.  Where a validation file is also pinned
# by runtime code, changing it changes the runtime digest; that coupling is
# declared explicitly (:func:`g1_intentional_runtime_validation_coupling`)
# rather than hidden.  Every digest uses :data:`IMPLEMENTATION_DIGEST_ALGORITHM`.

G1_IDENTITY_CLASS_RUNTIME = "G1_RUNTIME_IDENTITY"
G1_IDENTITY_CLASS_VALIDATION = "G1_VALIDATION_IDENTITY"
G1_IDENTITY_CLASS_GOVERNANCE = "G1_GOVERNANCE_AUTHORITY_IDENTITY"
G1_IDENTITY_CLASSES: tuple[str, ...] = (
    G1_IDENTITY_CLASS_RUNTIME,
    G1_IDENTITY_CLASS_VALIDATION,
    G1_IDENTITY_CLASS_GOVERNANCE,
)
INTENTIONAL_RUNTIME_VALIDATION_COUPLING = "INTENTIONAL_RUNTIME_VALIDATION_COUPLING"


def validation_identity_strict(root: Path) -> dict[str, str]:
    """Live SHA-256 of every validation member.  A missing member raises.

    :func:`validation_identity` reports a missing suite as ``""`` for display;
    an identity that is BOUND must never contain a hole, so this one refuses.
    """

    root = Path(root).resolve()
    out: dict[str, str] = {}
    for relative in VALIDATION_IDENTITY_PATHS:
        path = root / relative
        _require(
            path.is_file(),
            "U06_VALIDATION_IDENTITY_INCOMPLETE",
            f"Validation identity member is missing: {relative}",
        )
        out[relative] = sha256_file(path)
    return out


def validation_identity_digest(root: Path) -> str:
    return canonical_identity_digest(validation_identity_strict(root))


def governance_authority_identity_paths() -> tuple[str, ...]:
    """``G1_GOVERNANCE_AUTHORITY_IDENTITY`` members, derived from the pin tables."""

    # Lazy: the bundle and the authorization mechanism both import this overlay.
    from src.main_full81_authorization_v7_4 import FULL81_EXECUTION_INPUT_AUTHORITY_PINS
    from src.production_authority_bundle_v7_4 import all_pins

    pinned = {pin.relative_path for pin in all_pins()} | {
        pin.relative_path for pin in FULL81_EXECUTION_INPUT_AUTHORITY_PINS
    }
    excluded = set(ACCEPTED_IMPLEMENTATION_PATHS) | set(VALIDATION_IDENTITY_PATHS)
    return tuple(sorted(pinned - excluded))


def governance_authority_identity(root: Path) -> dict[str, str]:
    """Live SHA-256 of every governance-authority member.  Missing => raise."""

    root = Path(root).resolve()
    out: dict[str, str] = {}
    for relative in governance_authority_identity_paths():
        path = root / relative
        _require(
            path.is_file(),
            "U06_GOVERNANCE_IDENTITY_INCOMPLETE",
            f"Governance-authority identity member is missing: {relative}",
        )
        out[relative] = sha256_file(path)
    return out


def governance_authority_identity_digest(root: Path) -> str:
    return canonical_identity_digest(governance_authority_identity(root))


#: What a runtime pin of a validation file means, stated once.
G1_COUPLING_EFFECT = "RUNTIME_IMPLEMENTATION_DIGEST_CHANGES_WHEN_THIS_VALIDATION_FILE_CHANGES"
G1_BUNDLE_COUPLING_RATIONALE = (
    "The production-authority bundle pins this alignment-surface suite so that "
    "the gate fails closed if the suite proving its fail-closed behaviour is "
    "silently replaced; the bundle is a runtime member, so the suite's bytes "
    "are part of the runtime digest by design."
)
G1_STACK_COUPLING_RATIONALE = (
    "The successor stack pins this routing-preflight suite in its accepted "
    "ADDITIONAL_AUTHORITY_FILES table, unchanged since Step 2E-1; the stack is "
    "a runtime member, so the suite's bytes are part of the runtime digest."
)


def g1_intentional_runtime_validation_coupling() -> list[dict[str, str]]:
    """Every validation member whose exact bytes runtime code pins, declared."""

    from src.production_authority_bundle_v7_4 import all_pins

    entries: list[dict[str, str]] = []
    for pin in all_pins():
        if pin.relative_path in VALIDATION_IDENTITY_PATHS:
            entries.append(
                {
                    "path": pin.relative_path,
                    "coupling": INTENTIONAL_RUNTIME_VALIDATION_COUPLING,
                    "runtime_pin_holder": "src/production_authority_bundle_v7_4.py",
                    "pin_label": pin.label,
                    "effect": G1_COUPLING_EFFECT,
                    "rationale": G1_BUNDLE_COUPLING_RATIONALE,
                }
            )
    for relative in G1_STACK_PINNED_VALIDATION_PATHS:
        entries.append(
            {
                "path": relative,
                "coupling": INTENTIONAL_RUNTIME_VALIDATION_COUPLING,
                "runtime_pin_holder": "src/production_successor_stack_v7_3.py",
                "pin_label": "ADDITIONAL_AUTHORITY_FILES[step2e1_test]",
                "effect": G1_COUPLING_EFFECT,
                "rationale": G1_STACK_COUPLING_RATIONALE,
            }
        )
    return sorted(entries, key=lambda entry: entry["path"])


def g1_identity_axes(root: Path) -> dict[str, Any]:
    """Read-only report of the three G1 identities, their digests and overlaps."""

    root = Path(root).resolve()
    runtime = implementation_identity(root)
    validation = validation_identity_strict(root)
    governance = governance_authority_identity(root)
    sets = {
        G1_IDENTITY_CLASS_RUNTIME: set(runtime),
        G1_IDENTITY_CLASS_VALIDATION: set(validation),
        G1_IDENTITY_CLASS_GOVERNANCE: set(governance),
    }
    overlaps = {
        f"{a}&{b}": sorted(sets[a] & sets[b])
        for index, a in enumerate(G1_IDENTITY_CLASSES)
        for b in G1_IDENTITY_CLASSES[index + 1 :]
    }
    return {
        "digest_algorithm": IMPLEMENTATION_DIGEST_ALGORITHM,
        G1_IDENTITY_CLASS_RUNTIME: {
            "member_count": len(runtime),
            "digest": canonical_identity_digest(runtime),
            "paths": dict(sorted(runtime.items())),
        },
        G1_IDENTITY_CLASS_VALIDATION: {
            "member_count": len(validation),
            "digest": canonical_identity_digest(validation),
            "paths": dict(sorted(validation.items())),
        },
        G1_IDENTITY_CLASS_GOVERNANCE: {
            "member_count": len(governance),
            "digest": canonical_identity_digest(governance),
            "paths": dict(sorted(governance.items())),
        },
        "member_set_overlaps": overlaps,
        "member_sets_disjoint": not any(overlaps.values()),
        "intentional_runtime_validation_coupling": (
            g1_intentional_runtime_validation_coupling()
        ),
    }


# ---------------------------------------------------------------------------
# Current Full81 Production Generation G1: predeclared governance paths, phase
# ---------------------------------------------------------------------------


def g1_predeclared_governance_paths(
    generation: AuthorityGeneration | None = None,
) -> dict[str, str]:
    """Every G1 governance path, including the ones no lifecycle gate has reached.

    Paths only.  No future digest, commit or PASS is known, stated or reserved
    here.  The scope-authorization, no-solve-evidence and execution-
    authorization slots are owned by the authorization mechanism and are read
    from it, so there is one declaration of each.
    """

    from src.main_full81_authorization_v7_4 import (
        AUTHORIZATION_RECORD_RELATIVE_PATH,
        EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH,
        NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH,
    )

    generation = generation or CURRENT_GENERATION
    roles = generation.role_record_path_map or {}
    return {
        "candidate_change_ledger": generation.candidate_change_ledger_path or "",
        "candidate_checkpoint": generation.candidate_checkpoint_path,
        "candidate_manifest": generation.candidate_manifest_path,
        **{role: roles[role] for role in roles},
        "accepted_lifecycle_record": generation.accepted_lifecycle_record_path,
        "main_full81_scope_authorization": AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        "main_full81_no_solve_preflight_evidence": (
            NO_SOLVE_PREFLIGHT_EVIDENCE_RELATIVE_PATH.as_posix()
        ),
        "main_full81_execution_authorization": (
            EXECUTION_AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
        ),
    }


#: The lawful order of the G1 governance artifacts, as (phase, keys) stages.
G1_GOVERNANCE_STAGES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "CANDIDATE_PACKAGED",
        ("candidate_change_ledger", "candidate_checkpoint", "candidate_manifest"),
    ),
    ("INDEPENDENT_AUDIT_RECORD_PRESENT", ("independent_audit_pass",)),
    ("ACCEPTANCE_RECORDS_PRESENT", ("acceptance_closure", "acceptance_manifest")),
    (
        "RE_FREEZE_AND_LIFECYCLE_RECORDS_PRESENT",
        ("production_authority_re_freeze", "accepted_lifecycle_record"),
    ),
    ("SCOPE_AUTHORIZATION_RECORD_PRESENT", ("main_full81_scope_authorization",)),
    (
        "NO_SOLVE_PREFLIGHT_EVIDENCE_PRESENT",
        ("main_full81_no_solve_preflight_evidence",),
    ),
    ("EXECUTION_AUTHORIZATION_RECORD_PRESENT", ("main_full81_execution_authorization",)),
)
G1_PHASE_NOT_YET_PACKAGED = "IMPLEMENTATION_CANDIDATE_NOT_YET_PACKAGED"
G1_PHASE_OUT_OF_ORDER = "OUT_OF_ORDER_GOVERNANCE_ARTIFACTS_FAIL_CLOSED"


def current_generation_phase(root: Path) -> dict[str, Any]:
    """Deterministic, read-only PRESENCE phase of the current generation.

    Presence is never validity and this function authorizes nothing: live
    acceptance, scope authorization and execution authorization are decided
    only by their resolvers.  It makes the candidate phase explicit - every
    future artifact is named and reported ABSENT - and it fails closed on any
    artifact present before an earlier stage is complete.
    """

    root = Path(root).resolve()
    generation = CURRENT_GENERATION
    paths = g1_predeclared_governance_paths(generation)
    presence = {key: (root / path).is_file() for key, path in paths.items()}
    reached = G1_PHASE_NOT_YET_PACKAGED
    complete_so_far = True
    out_of_order: list[str] = []
    for phase, keys in G1_GOVERNANCE_STAGES:
        present = [presence[key] for key in keys]
        if complete_so_far and all(present):
            reached = phase
            continue
        if not complete_so_far:
            out_of_order.extend(key for key in keys if presence[key])
        elif any(present):
            # Partially present stage: the present members are early.
            out_of_order.extend(key for key in keys if presence[key])
        complete_so_far = False
    return {
        "generation_id": generation.generation_id,
        "candidate_id": generation.candidate_id,
        "phase": G1_PHASE_OUT_OF_ORDER if out_of_order else reached,
        "presence_phase_without_order_check": reached,
        "out_of_order_present": sorted(out_of_order),
        "presence": presence,
        "paths": paths,
        "absent_future_artifacts": sorted(k for k, v in presence.items() if not v),
        "presence_is_not_validity": True,
        "authorizes_anything": False,
        "live_lifecycle_authority": "resolve_u06_lifecycle",
        "live_scope_authorization_authority": (
            "src.main_full81_authorization_v7_4.resolve_full81_authorization"
        ),
        "live_execution_authorization_authority": (
            "src.main_full81_authorization_v7_4.resolve_full81_execution_authorization"
        ),
    }


# ---------------------------------------------------------------------------
# Current Full81 Production Generation G1: the candidate content contract
# ---------------------------------------------------------------------------
#
# The G1 implementation-candidate manifest is validated closed-world, exactly
# as contract V4 does for R8, using the same generic machinery: strict JSON,
# no own identity (C8), forbidden snapshot / self-label keys, exact field
# classification, every embedded raw SHA-256 owned by ONE obligation and BOUND
# to ONE role whose value is established independently of the candidate
# artifacts, role-binding parity, same-path conflict detection, and checkpoint
# identity claims checked against the bound authority value.
#
# Every runtime and governance authority value is live: raw bytes, the live
# runtime / governance digests, or an authority-bundle pin (itself required to
# equal live bytes).  The validation generation is versioned separately: it is
# bound to live bytes in CANDIDATE_PACKAGE mode and, in GATE mode, to the blobs
# published together with the candidate manifest, so a later validation-only
# change can never silently move production authority (runtime-pinned suites
# still move the runtime digest).  The only historical identities G1 states
# live in its change ledger and are TYPED predecessor evidence verified by Git
# blob containment in a declared published commit; none of them feeds the live
# freeze.  The GATE path adds Git publication through the lifecycle validator.

G1_CANDIDATE_MANIFEST_FIELD_CLASSES: Mapping[str, str] = {
    "schema_version": FIELD_CLASS_CONSTANT,
    "artifact_type": FIELD_CLASS_CONSTANT,
    "role": FIELD_CLASS_CONSTANT,
    "candidate_manifest_contract": FIELD_CLASS_CONSTANT,
    "date": FIELD_CLASS_OBSERVATION,
    "generation_id": FIELD_CLASS_CONSTANT,
    "lineage_id": FIELD_CLASS_CONSTANT,
    "candidate_id": FIELD_CLASS_CONSTANT,
    "target_candidate_id": FIELD_CLASS_CONSTANT,
    "candidate_revision": FIELD_CLASS_CONSTANT,
    "scope": FIELD_CLASS_PROSE,
    "disposition": FIELD_CLASS_CONSTANT,
    "self_accepted": FIELD_CLASS_CONSTANT,
    "package_binding": FIELD_CLASS_CONSTANT,
    "candidate_checkpoint_path": FIELD_CLASS_CONSTANT,
    "candidate_checkpoint": FIELD_CLASS_IDENTITY,
    "candidate_manifest_path": FIELD_CLASS_CONSTANT,
    "candidate_change_ledger": FIELD_CLASS_IDENTITY,
    "accepted_lifecycle_record_path": FIELD_CLASS_CONSTANT,
    "predecessor_generation": FIELD_CLASS_CONSTANT,
    #: Required by the shared role envelope of EVERY lifecycle role
    #: (``validate_role_envelope``); bound to the same live runtime digest as
    #: ``runtime_identity.digest``.
    "implementation_identity_digest": FIELD_CLASS_IDENTITY,
    "runtime_identity": FIELD_CLASS_IDENTITY,
    "validation_identity": FIELD_CLASS_IDENTITY,
    "governance_authority_identity": FIELD_CLASS_IDENTITY,
    "intentional_runtime_validation_coupling": FIELD_CLASS_CONSTANT,
    "authority_bundle": FIELD_CLASS_IDENTITY,
    "durable_publication_declaration": FIELD_CLASS_IDENTITY,
    "predeclared_governance_paths": FIELD_CLASS_CONSTANT,
    "lifecycle_state": FIELD_CLASS_CONSTANT,
    "execution_counters": FIELD_CLASS_CONSTANT,
    "repository_head_at_authoring": FIELD_CLASS_OBSERVATION,
    "carried_findings": FIELD_CLASS_OBSERVATION,
    "next_legal_gate": FIELD_CLASS_PROSE,
}
G1_PACKAGE_BINDING_KEYS: frozenset[str] = frozenset(
    {"scheme", "direction", "manifest_self_identity", "rationale"}
)
G1_IDENTITY_SECTION_KEYS: frozenset[str] = frozenset(
    {"identity_class", "path_count", "digest_algorithm", "digest", "paths"}
)
#: The three identity sections of a G1 manifest -> their identity class.
G1_IDENTITY_SECTIONS: Mapping[str, str] = {
    "runtime_identity": G1_IDENTITY_CLASS_RUNTIME,
    "validation_identity": G1_IDENTITY_CLASS_VALIDATION,
    "governance_authority_identity": G1_IDENTITY_CLASS_GOVERNANCE,
}
#: Every no-execution counter a G1 candidate record states; all must be zero.
G1_EXECUTION_COUNTERS: Mapping[str, int] = {
    "optimize_calls": 0,
    "model_solves": 0,
    "production_runs": 0,
    "sensitivity_solves": 0,
    "full81_runs": 0,
    "current_generation_21d_runs": 0,
    "scope_authorizations_created": 0,
    "execution_authorizations_created": 0,
}
#: The only lifecycle state a G1 candidate record may declare.  It is a
#: construction-time declaration; live state is resolved, never declared.
G1_CANDIDATE_LIFECYCLE_STATE: Mapping[str, str] = {
    "g1": "CANDIDATE",
    "independent_audit": "NOT_YET_PERFORMED",
    "acceptance": "NOT_YET_PERFORMED",
    "production_authority_re_freeze": "NOT_YET_PERFORMED",
    "accepted_lifecycle_record": "NOT_YET_CREATED",
    "scope_authorization": "NOT_YET_CREATED_NOT_YET_AUTHORIZED",
    "current_generation_21d_no_solve_preflight": "NOT_YET_EXECUTED",
    "execution_authorization": "NOT_AUTHORIZED",
    "full81": "NOT_EXECUTED_NOT_AUTHORIZED",
    "statement_scope": (
        "CANDIDATE_CONSTRUCTION_TIME_DECLARATION_LIVE_STATE_IS_RESOLVED_NOT_DECLARED"
    ),
}
G1_PREDECESSOR_RELATIONSHIP = "SUPERSEDED_HISTORICAL_PREDECESSOR_NOT_A_LIVE_BINDING"

#: G1 authority sources beyond the generic ones.  The validation generation is
#: established from live bytes in CANDIDATE_PACKAGE mode and from the blobs
#: published with the candidate manifest in GATE mode
#: (:meth:`_G1ContractContext.validation_authority`).
AUTHORITY_LIVE_VALIDATION = "VALIDATION_GENERATION_IDENTITY"
AUTHORITY_LIVE_GOVERNANCE = "LIVE_GOVERNANCE_AUTHORITY_IDENTITY"
AUTHORITY_PUBLISHED_GIT_BLOB = "PUBLISHED_GIT_BLOB_AT_DECLARED_ANCESTOR_COMMIT"
G1_IDENTITY_AUTHORITY_SOURCES: tuple[str, ...] = (
    AUTHORITY_LIVE_RAW_BYTES,
    AUTHORITY_LIVE_IMPLEMENTATION,
    AUTHORITY_LIVE_VALIDATION,
    AUTHORITY_LIVE_GOVERNANCE,
    AUTHORITY_BUNDLE_PIN,
    AUTHORITY_PUBLISHED_GIT_BLOB,
)

#: THE closed-world identity schema of a G1 candidate manifest.  The manifest's
#: own identity (``C8``) has no obligation: it is forbidden.  Obligation kinds
#: are numbered because verifiers run in sorted kind order: each identity is
#: judged by its own obligation first, and the change ledger - which restates
#: manifest identities - is verified last, so a rejection names the real role.
G1_CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS: tuple[IdentityObligation, ...] = (
    IdentityObligation(
        "G1-C1", "g1_1_candidate_checkpoint", ("candidate_checkpoint", "sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Candidate checkpoint raw SHA-256.",
    ),
    IdentityObligation(
        "G1-R1", "g1_2_runtime_digest", ("runtime_identity", "digest"),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "G1_RUNTIME_IDENTITY digest: the live implementation digest.",
    ),
    IdentityObligation(
        "G1-R1", "g1_2_runtime_digest", ("implementation_identity_digest",),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "The same digest, as the shared role envelope requires it.",
    ),
    IdentityObligation(
        "G1-R2", "g1_3_runtime_paths", ("runtime_identity", "paths", "*"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Raw SHA-256 of every runtime member.",
    ),
    IdentityObligation(
        "G1-V1", "g1_4_validation_digest", ("validation_identity", "digest"),
        AUTHORITY_LIVE_VALIDATION,
        "G1_VALIDATION_IDENTITY digest.",
    ),
    IdentityObligation(
        "G1-V2", "g1_5_validation_paths", ("validation_identity", "paths", "*"),
        AUTHORITY_LIVE_VALIDATION,
        "Raw SHA-256 of every validation member of the G1 validation generation.",
    ),
    IdentityObligation(
        "G1-G1", "g1_6_governance_digest", ("governance_authority_identity", "digest"),
        AUTHORITY_LIVE_GOVERNANCE,
        "G1_GOVERNANCE_AUTHORITY_IDENTITY digest.",
    ),
    IdentityObligation(
        "G1-G2", "g1_7_governance_paths",
        ("governance_authority_identity", "paths", "*"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Raw SHA-256 of every governance-authority member.",
    ),
    IdentityObligation(
        "G1-B1", "g1_8_bundle_pins", ("authority_bundle", "pins", "*", "sha256"),
        AUTHORITY_BUNDLE_PIN,
        "Every authority-bundle pin, equal to the bundle constant and live bytes.",
    ),
    IdentityObligation(
        "G1-B2", "durable_pinned",
        ("durable_publication_declaration", "entries", "*", "expected_raw_sha256"),
        AUTHORITY_BUNDLE_PIN,
        "Static durable-publication declaration: pinned paths only.",
    ),
    IdentityObligation(
        "G1-L1", "g1_9_candidate_change_ledger", ("candidate_change_ledger", "sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Candidate change ledger raw SHA-256; the ledger is then validated.",
    ),
)


class _G1ContractContext(_RoleBinding):
    """Lazily computed live identities for one G1 contract validation."""

    def __init__(
        self,
        root: Path,
        payload: Mapping[str, Any],
        generation: AuthorityGeneration,
        mode: str,
        label: str,
    ) -> None:
        super().__init__(root, mode, label)
        self.payload = payload
        self.generation = generation
        self._runtime: dict[str, str] | None = None
        self._validation: dict[str, str] | None = None
        self._governance: dict[str, str] | None = None
        #: Filled by the ``G1-L1`` verifier: the validated ledger's report.
        self.ledger_report: dict[str, Any] | None = None

        #: GATE mode: the commit that published the candidate manifest, whose
        #: blobs establish the validation identity (see validation_authority).
        self.validation_reference_commit: str | None = None

    def live_runtime(self) -> dict[str, str]:
        if self._runtime is None:
            self._runtime = implementation_identity(self.root)
        return self._runtime

    def validation_authority(self) -> dict[str, str]:
        """The independently established value of every validation member.

        ``CANDIDATE_PACKAGE`` mode (the candidate as authored and audited):
        live raw bytes.  ``GATE`` mode (the production lifecycle path): the
        blobs PUBLISHED TOGETHER WITH the candidate manifest, read from the
        commit that last modified the manifest in HEAD's history.  The
        validation generation is versioned separately from the runtime
        generation, so a later validation-only change neither rewrites G1's
        recorded validation identity nor moves production authority; a
        recomputing author cannot change a published blob.  Validation members
        that runtime code pins (``INTENTIONAL_RUNTIME_VALIDATION_COUPLING``)
        still move the runtime digest through their runtime pin.
        """

        if self._validation is None:
            if self.mode == CANDIDATE_MANIFEST_MODE_GATE:
                self._validation = self._published_validation()
            else:
                self._validation = validation_identity_strict(self.root)
        return self._validation

    def _published_validation(self) -> dict[str, str]:
        manifest = self.generation.candidate_manifest_path
        commit = last_modifying_commit(self.root, manifest)
        _require(
            isinstance(commit, str) and bool(_COMMIT_RE.match(commit)),
            "U06_LIFECYCLE_NOT_PUBLISHED",
            f"{self.label}: the candidate manifest has no publishing commit in "
            "HEAD's history, so its validation generation cannot be "
            "established from published bytes.",
        )
        _require(
            blob_sha256_at(self.root, commit, manifest)
            == self.live_sha(manifest, field="candidate_manifest"),
            "U06_LIFECYCLE_NOT_PUBLISHED",
            f"{self.label}: the live candidate manifest differs from the bytes "
            f"commit {commit} published.",
        )
        blobs = _blob_sha256_map(self.root, commit, VALIDATION_IDENTITY_PATHS, label=self.label)
        missing = sorted(relative for relative, digest in blobs.items() if digest is None)
        _require(
            not missing,
            "U06_VALIDATION_IDENTITY_INCOMPLETE",
            f"{self.label}: validation members {missing} were not published with "
            f"the candidate manifest in {commit}.",
        )
        self.validation_reference_commit = commit
        return {relative: str(digest) for relative, digest in blobs.items()}

    def live_governance(self) -> dict[str, str]:
        if self._governance is None:
            self._governance = governance_authority_identity(self.root)
        return self._governance

    def live_axis(self, section: str) -> dict[str, str]:
        """The authority map of one identity section (validation: see above)."""

        return {
            "runtime_identity": self.live_runtime,
            "validation_identity": self.validation_authority,
            "governance_authority_identity": self.live_governance,
        }[section]()

    def candidate_sha(self, relative: str, *, field: str) -> str:
        """The established candidate value of one G1 identity-surface path."""

        if relative in VALIDATION_IDENTITY_PATHS:
            return self.validation_authority()[relative]
        return self.live_sha(relative, field=field)


def _g1_verify_checkpoint(ctx: _G1ContractContext, items: list[_Item]):
    _require(
        [item[0] for item in items] == [("candidate_checkpoint", "sha256")],
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: exactly one candidate checkpoint identity is required; "
        f"observed {[item[0] for item in items]}",
    )
    pointer, value, _ = items[0]
    relative = ctx.generation.candidate_checkpoint_path
    ctx.bind(
        pointer,
        value,
        ctx.live_sha(relative, field="candidate_checkpoint"),
        f"candidate_checkpoint:{relative}",
    )


def _g1_axis_digest_verifier(
    section: str,
    role: str,
    drift_status: str,
    extra_pointers: tuple[tuple[Any, ...], ...] = (),
):
    expected = {(section, "digest"), *extra_pointers}

    def verify(ctx: _G1ContractContext, items: list[_Item]) -> None:
        observed = [item[0] for item in items]
        _require(
            len(observed) == len(expected) and set(observed) == expected,
            "U06_ROLE_SCHEMA_INVALID",
            f"{ctx.label}: the {section} digest identities must be exactly "
            f"{sorted(expected)}; observed {observed}",
        )
        live = canonical_identity_digest(ctx.live_axis(section))
        for pointer, value, _ in items:
            _require(
                value == live,
                drift_status,
                f"{ctx.label}: {'.'.join(map(str, pointer))} declares {value} but "
                f"the established {G1_IDENTITY_SECTIONS[section]} digest is {live}.",
            )
        paths = ctx.payload[section]["paths"]
        reproduced = canonical_identity_digest(paths) if isinstance(paths, Mapping) else None
        _require(
            reproduced == live,
            drift_status,
            f"{ctx.label}: {section}.paths does not reproduce its declared digest "
            f"(reproduced={reproduced}, live={live}).",
        )
        for pointer, value, _ in items:
            ctx.bind(pointer, value, live, role)

    return verify


def _g1_axis_paths_verifier(section: str, role_prefix: str, drift_status: str):
    def verify(ctx: _G1ContractContext, items: list[_Item]) -> None:
        live = ctx.live_axis(section)
        declared = {str(item[0][2]): item[1] for item in items}
        _require(
            set(declared) == set(live) and len(items) == len(live),
            "U06_ROLE_SCHEMA_INVALID",
            f"{ctx.label}: {section}.paths must declare exactly the "
            f"{len(live)} {G1_IDENTITY_SECTIONS[section]} members; "
            f"missing={sorted(set(live) - set(declared))}, "
            f"extra={sorted(set(declared) - set(live))}",
        )
        for pointer, value, _ in items:
            relative = str(pointer[2])
            _require(
                value == live[relative],
                drift_status,
                f"{ctx.label}: {section}.paths[{relative}] declares {value} but "
                f"its established bytes hash to {live[relative]}.",
            )
            ctx.bind(pointer, value, live[relative], f"{role_prefix}:{relative}")

    return verify


def _g1_verify_bundle_pins(ctx: _G1ContractContext, items: list[_Item]):
    from src.production_authority_bundle_v7_4 import all_pins

    by_label = {pin.label: pin for pin in all_pins()}
    labels = [str(item[0][2]) for item in items]
    _require(
        sorted(labels) == sorted(by_label) and len(labels) == len(set(labels)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: authority_bundle.pins must restate exactly the "
        f"{len(by_label)} declared bundle pins; "
        f"missing={sorted(set(by_label) - set(labels))}, "
        f"extra={sorted(set(labels) - set(by_label))}",
    )
    for pointer, value, _ in items:
        pin = by_label[str(pointer[2])]
        holder = _resolve_pointer(ctx.payload, pointer[:-1])
        _require(
            holder.get("path") == pin.relative_path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: pin {pin.label!r} is restated for path "
            f"{holder.get('path')!r} but the bundle pins {pin.relative_path}.",
        )
        live = ctx.live_sha(pin.relative_path, field=f"bundle pin {pin.label}")
        _require(
            pin.sha256 == live,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: bundle pin {pin.label!r} states {pin.sha256} but live "
            f"{pin.relative_path} hashes to {live}; a stale pin binds nothing.",
        )
        ctx.bind(pointer, value, pin.sha256, f"bundle_pin:{pin.label}")


def _g1_verify_candidate_change_ledger(ctx: _G1ContractContext, items: list[_Item]):
    _require(
        [item[0] for item in items] == [("candidate_change_ledger", "sha256")],
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: exactly one candidate change ledger identity is required; "
        f"observed {[item[0] for item in items]}",
    )
    pointer, value, _ = items[0]
    relative = ctx.generation.candidate_change_ledger_path or ""
    ctx.bind(
        pointer,
        value,
        ctx.live_sha(relative, field="candidate_change_ledger"),
        f"candidate_change_ledger:{relative}",
    )
    ctx.ledger_report = validate_g1_candidate_change_ledger(
        ctx.root,
        (ctx.root / relative).read_bytes(),
        ctx.payload,
        ctx.generation,
        mode=ctx.mode,
        context=ctx,
    )


G1_CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS: dict[str, Any] = {
    "g1_1_candidate_checkpoint": _g1_verify_checkpoint,
    "g1_2_runtime_digest": _g1_axis_digest_verifier(
        "runtime_identity",
        "live_runtime_digest",
        "U06_IMPLEMENTATION_IDENTITY_DRIFT",
        extra_pointers=(("implementation_identity_digest",),),
    ),
    "g1_3_runtime_paths": _g1_axis_paths_verifier(
        "runtime_identity", "runtime_path", "U06_IMPLEMENTATION_IDENTITY_DRIFT"
    ),
    "g1_4_validation_digest": _g1_axis_digest_verifier(
        "validation_identity", "live_validation_digest", "U06_VALIDATION_IDENTITY_DRIFT"
    ),
    "g1_5_validation_paths": _g1_axis_paths_verifier(
        "validation_identity", "validation_path", "U06_VALIDATION_IDENTITY_DRIFT"
    ),
    "g1_6_governance_digest": _g1_axis_digest_verifier(
        "governance_authority_identity",
        "live_governance_digest",
        "U06_GOVERNANCE_IDENTITY_DRIFT",
    ),
    "g1_7_governance_paths": _g1_axis_paths_verifier(
        "governance_authority_identity",
        "governance_path",
        "U06_GOVERNANCE_IDENTITY_DRIFT",
    ),
    "g1_8_bundle_pins": _g1_verify_bundle_pins,
    "durable_pinned": _verify_durable_pinned,
    "g1_9_candidate_change_ledger": _g1_verify_candidate_change_ledger,
}


def _g1_predecessor_generation(generation: AuthorityGeneration) -> AuthorityGeneration:
    predecessor = GENERATIONS_BY_ID.get(str(generation.predecessor_generation_id))
    _require(
        predecessor is not None,
        "U06_ROLE_SCHEMA_INVALID",
        f"generation {generation.generation_id} names no declared predecessor.",
    )
    return predecessor


def _g1_predecessor_constant(generation: AuthorityGeneration) -> dict[str, str]:
    predecessor = _g1_predecessor_generation(generation)
    return {
        "generation_id": predecessor.generation_id,
        "lineage_id": predecessor.lineage_id,
        "candidate_id": predecessor.candidate_id,
        "accepted_lifecycle_record_path": predecessor.accepted_lifecycle_record_path,
        "relationship": G1_PREDECESSOR_RELATIONSHIP,
    }


def _g1_register_entry(generation: AuthorityGeneration) -> Mapping[str, Any] | None:
    return CANDIDATE_AUDIT_REGISTERS.get(generation.generation_id, {}).get(
        generation.candidate_id
    )


def _g1_check_manifest_constants(
    payload: Mapping[str, Any],
    generation: AuthorityGeneration,
    relative: str,
    label: str,
) -> None:
    contract = generation.role_contracts["implementation_candidate"]
    _require(
        payload.get("artifact_type") == contract.artifact_type
        and payload.get("role") == "implementation_candidate",
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type/role must be {contract.artifact_type!r} / "
        f"'implementation_candidate'; observed {payload.get('artifact_type')!r} / "
        f"{payload.get('role')!r}",
    )
    _require(
        payload.get("schema_version") == contract.schema_version,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version must be {contract.schema_version!r}.",
    )
    for field, want in (
        ("generation_id", generation.generation_id),
        ("lineage_id", generation.lineage_id),
    ):
        _require(
            payload.get(field) == want,
            "U06_LINEAGE_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {payload.get(field)!r}",
        )
    for field in ("candidate_id", "target_candidate_id"):
        value = payload.get(field)
        _require(
            value not in generation.superseded_candidate_ids,
            "U06_SUPERSEDED_CANDIDATE_REJECTED",
            f"{label}: {field} {value!r} names a superseded candidate.",
        )
        _require(
            value == generation.candidate_id,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: {field} must be {generation.candidate_id!r}; observed {value!r}",
        )
    for field, want in (
        ("candidate_revision", generation.candidate_id.rsplit("_", 1)[-1]),
        ("candidate_checkpoint_path", generation.candidate_checkpoint_path),
        ("candidate_manifest_path", generation.candidate_manifest_path),
        ("accepted_lifecycle_record_path", generation.accepted_lifecycle_record_path),
    ):
        _require(
            payload.get(field) == want,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {payload.get(field)!r}",
        )
    _require(
        relative == generation.candidate_manifest_path,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: validated at {relative}, not at "
        f"{generation.candidate_manifest_path}.",
    )
    _require(
        payload.get("self_accepted") is False,
        "U06_SELF_ACCEPTANCE_REJECTED",
        f"{label}: self_accepted must be literally false.",
    )
    history = _g1_register_entry(generation)
    _require(
        history is not None and payload.get("disposition") == history.get("disposition"),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: disposition must equal the candidate register's "
        f"{(history or {}).get('disposition')!r}.",
    )


def _g1_check_durable_declaration(
    payload: Mapping[str, Any], generation: AuthorityGeneration, label: str
) -> None:
    declaration = payload.get("durable_publication_declaration")
    _require(
        isinstance(declaration, Mapping) and set(declaration) == DURABLE_DECLARATION_KEYS,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: durable_publication_declaration must have exactly "
        f"{sorted(DURABLE_DECLARATION_KEYS)}.",
    )
    _require(
        declaration.get("semantics") == DURABLE_DECLARATION_SEMANTICS
        and declaration.get("live_status_source")
        == DURABLE_DECLARATION_LIVE_STATUS_SOURCE,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the durable-publication declaration must be a static "
        "declaration whose live status comes from the live report only.",
    )
    required = list(_required_durable_paths_for(generation))
    _require(
        declaration.get("required_paths") == required,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: required_paths must be exactly {required}.",
    )
    entries = declaration.get("entries")
    _require(
        isinstance(entries, Mapping) and set(entries) == set(required),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: durable entries must cover exactly the required paths.",
    )
    for relative, entry in entries.items():
        if relative in REQUIRED_DURABLE_PUBLICATION_PIN_LABELS:
            _require(
                isinstance(entry, Mapping)
                and set(entry) == {"identity_source", "pin_label", "expected_raw_sha256"}
                and entry.get("identity_source") == DURABLE_IDENTITY_SOURCE_PIN
                and entry.get("pin_label")
                == REQUIRED_DURABLE_PUBLICATION_PIN_LABELS[relative],
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: pinned durable entry {relative} must state exactly its "
                "identity source, pin label and expected raw SHA-256.",
            )
        elif relative == generation.candidate_checkpoint_path:
            _require(
                entry
                == {
                    "identity_source": DURABLE_IDENTITY_SOURCE_CHECKPOINT_FIELD,
                    "identity_field": DURABLE_CHECKPOINT_IDENTITY_FIELD,
                },
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the checkpoint durable entry must refer to "
                f"{DURABLE_CHECKPOINT_IDENTITY_FIELD} and carry no digest.",
            )
        elif relative == generation.candidate_change_ledger_path:
            _require(
                entry
                == {
                    "identity_source": DURABLE_IDENTITY_SOURCE_LEDGER_FIELD,
                    "identity_field": DURABLE_LEDGER_IDENTITY_FIELD,
                },
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the change-ledger durable entry must refer to "
                f"{DURABLE_LEDGER_IDENTITY_FIELD} and carry no digest.",
            )
        else:
            _require(
                entry
                == {
                    "identity_source": DURABLE_IDENTITY_SOURCE_EXTERNAL,
                    "external_binding_fields": list(
                        candidate_manifest_external_binding_fields(generation)
                    ),
                },
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: the manifest's own durable entry must declare exactly "
                "its external binding fields and no identity.",
            )


def _g1_check_manifest_structure(
    payload: Mapping[str, Any], generation: AuthorityGeneration, label: str
) -> None:
    from src.production_authority_bundle_v7_4 import PIN_GROUPS, all_pins

    binding = payload.get("package_binding")
    _require(
        isinstance(binding, Mapping)
        and set(binding) == G1_PACKAGE_BINDING_KEYS
        and binding.get("scheme") == PACKAGE_BINDING_SCHEME
        and binding.get("direction") == PACKAGE_BINDING_DIRECTION
        and binding.get("manifest_self_identity") == DURABLE_IDENTITY_SOURCE_EXTERNAL
        and isinstance(binding.get("rationale"), str)
        and binding["rationale"].strip(),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: package_binding must declare the acyclic manifest -> "
        "checkpoint scheme with the manifest's identity bound externally.",
    )
    for field, path in (
        ("candidate_checkpoint", generation.candidate_checkpoint_path),
        ("candidate_change_ledger", generation.candidate_change_ledger_path),
    ):
        entry = payload.get(field)
        _require(
            isinstance(entry, Mapping)
            and set(entry) == {"path", "sha256"}
            and entry.get("path") == path,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: {field} must be exactly {{path: {path}, sha256}}.",
        )
    _require(
        _strict_equal(payload.get("predecessor_generation"), _g1_predecessor_constant(generation)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: predecessor_generation must name the declared predecessor "
        "generation as superseded historical evidence, not a live binding.",
    )
    expected_counts = {
        "runtime_identity": len(ACCEPTED_IMPLEMENTATION_PATHS),
        "validation_identity": len(VALIDATION_IDENTITY_PATHS),
        "governance_authority_identity": len(governance_authority_identity_paths()),
    }
    for section, identity_class in G1_IDENTITY_SECTIONS.items():
        value = payload.get(section)
        _require(
            isinstance(value, Mapping)
            and set(value) == G1_IDENTITY_SECTION_KEYS
            and value.get("identity_class") == identity_class
            and value.get("path_count") == expected_counts[section]
            and value.get("digest_algorithm") == IMPLEMENTATION_DIGEST_ALGORITHM
            and isinstance(value.get("paths"), Mapping)
            and len(value["paths"]) == expected_counts[section],
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {section} must be a {identity_class} section with "
            f"{expected_counts[section]} paths and the declared digest algorithm.",
        )
    _require(
        _strict_equal(
            payload.get("intentional_runtime_validation_coupling"),
            g1_intentional_runtime_validation_coupling(),
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: intentional_runtime_validation_coupling must declare exactly "
        "the validation members runtime code pins.",
    )
    bundle = payload.get("authority_bundle")
    _require(
        isinstance(bundle, Mapping)
        and set(bundle) == AUTHORITY_BUNDLE_KEYS
        and bundle.get("declared_pin_groups") == len(PIN_GROUPS)
        and bundle.get("declared_pin_count") == len(all_pins())
        and isinstance(bundle.get("pins"), Mapping)
        and all(
            isinstance(v, Mapping) and set(v) == {"path", "sha256"}
            for v in bundle["pins"].values()
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: authority_bundle counts or pin entries are malformed.",
    )
    _g1_check_durable_declaration(payload, generation, label)
    _require(
        _strict_equal(
            payload.get("predeclared_governance_paths"),
            g1_predeclared_governance_paths(generation),
        ),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: predeclared_governance_paths must equal the generation's and "
        "the authorization mechanism's own declarations.",
    )
    _require(
        _strict_equal(payload.get("lifecycle_state"), dict(G1_CANDIDATE_LIFECYCLE_STATE)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: lifecycle_state must be the candidate-time declaration: "
        "nothing audited, accepted, frozen or authorized.",
    )
    _require(
        _strict_equal(payload.get("execution_counters"), dict(G1_EXECUTION_COUNTERS)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: execution_counters must all be zero.",
    )
    head = payload.get("repository_head_at_authoring")
    _require(
        isinstance(head, str) and bool(_COMMIT_RE.match(head)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: repository_head_at_authoring must be a full commit id.",
    )
    for field in ("scope", "next_legal_gate", "date"):
        value = payload.get(field)
        _require(
            isinstance(value, str) and value.strip(),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {field} must be a non-empty string.",
        )
    _require(
        isinstance(payload.get("carried_findings"), list),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: carried_findings must be a list.",
    )


def _g1_identity_target_path(payload: Mapping[str, Any], pointer: Sequence[Any]) -> str | None:
    """The live artifact path a G1 identity pointer claims the digest OF."""

    if tuple(pointer[:2]) in (
        ("runtime_identity", "paths"),
        ("validation_identity", "paths"),
        ("governance_authority_identity", "paths"),
        ("durable_publication_declaration", "entries"),
    ):
        return str(pointer[2])
    parent = _resolve_pointer(payload, pointer[:-1])
    if isinstance(parent, Mapping) and isinstance(parent.get("path"), str):
        return parent["path"]
    return None


def _g1_check_identity_path_conflicts(
    payload: Mapping[str, Any],
    identities: Sequence[tuple[tuple[Any, ...], str]],
    label: str,
) -> None:
    by_path: dict[str, set[str]] = {}
    for pointer, value in identities:
        target = _g1_identity_target_path(payload, pointer)
        if target is not None:
            by_path.setdefault(target, set()).add(value)
    conflicts = {path: sorted(v) for path, v in by_path.items() if len(v) > 1}
    _require(
        not conflicts,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: the same path carries conflicting identities: {conflicts}",
    )


def validate_g1_candidate_manifest_contract(
    root: Path,
    relative: str | None = None,
    payload: Mapping[str, Any] | None = None,
    generation: AuthorityGeneration | None = None,
    *,
    mode: str,
    manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Validate a G1 candidate manifest against the G1 content contract.

    Fail-closed and ordered so the raised status names the real defect.
    Read-only: writes nothing, stages nothing, constructs no model.
    """

    root = Path(root).resolve()
    generation = generation or CURRENT_GENERATION
    relative = (relative or generation.candidate_manifest_path).replace("\\", "/").strip()
    label = f"G1 candidate manifest ({relative})"
    _require(
        mode in CANDIDATE_MANIFEST_MODES,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: unknown validation mode {mode!r}.",
    )
    _require(
        generation.candidate_manifest_contract == G1_CANDIDATE_MANIFEST_CONTRACT,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: generation {generation.generation_id} declares contract "
        f"{generation.candidate_manifest_contract!r}; this validator implements "
        f"only {G1_CANDIDATE_MANIFEST_CONTRACT!r}.",
    )
    if manifest_bytes is None:
        path = root / relative
        _require(
            path.is_file(),
            "U06_ROLE_ARTIFACT_MISSING",
            f"{label}: candidate manifest is missing.",
        )
        manifest_bytes = path.read_bytes()
    strict = _strict_json_object(manifest_bytes, label=label)
    _require(
        payload is None or dict(payload) == strict,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: the payload under validation is not exactly the strictly "
        "parsed manifest bytes.",
    )
    payload = strict
    _require(
        payload.get("candidate_manifest_contract") == G1_CANDIDATE_MANIFEST_CONTRACT,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: candidate_manifest_contract must be "
        f"{G1_CANDIDATE_MANIFEST_CONTRACT!r}; observed "
        f"{payload.get('candidate_manifest_contract')!r}.",
    )
    _check_candidate_manifest_self_identity(payload, generation, label)

    forbidden: list[str] = []

    def find_forbidden(node: Any, pointer: tuple[Any, ...]) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if key in CANDIDATE_MANIFEST_FORBIDDEN_KEYS:
                    forbidden.append(".".join(map(str, pointer + (key,))))
                find_forbidden(value, pointer + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                find_forbidden(value, pointer + (index,))

    find_forbidden(payload, ())
    _require(
        not forbidden,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: frozen live-report or self-label fields are forbidden in a "
        f"candidate manifest: {sorted(forbidden)}.",
    )
    _g1_check_manifest_constants(payload, generation, relative, label)
    keys = set(payload)
    classified = set(G1_CANDIDATE_MANIFEST_FIELD_CLASSES)
    _require(
        keys == classified,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: top-level fields must be exactly the classified set; "
        f"unclassified={sorted(keys - classified)}, "
        f"missing={sorted(classified - keys)}",
    )
    _g1_check_manifest_structure(payload, generation, label)

    identities, hidden = collect_identity_pointers(payload)
    _require(
        not hidden,
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: raw identities hidden in prose, keys or malformed values: "
        f"{['.'.join(map(str, p)) for p in hidden]}",
    )
    obligations = G1_CANDIDATE_MANIFEST_IDENTITY_OBLIGATIONS
    owned = _own_identity_pointers(identities, obligations, label)
    _g1_check_identity_path_conflicts(payload, identities, label)
    context = _G1ContractContext(root, payload, generation, mode, label)
    verified, structural = _verify_owned_identities(
        owned, identities, G1_CANDIDATE_MANIFEST_OBLIGATION_VERIFIERS, context, label
    )
    checkpoint_report = _check_checkpoint_identity_claims(root, generation, context, label)
    return {
        "contract": G1_CANDIDATE_MANIFEST_CONTRACT,
        "mode": mode,
        "manifest_path": relative,
        "collected_identity_count": len(identities),
        "verified_identity_count": len(verified),
        "structural_identity_count": len(structural),
        "role_bound_identity_count": len(context.authority),
        "unaccounted_identity_count": 0,
        "conflict_count": 0,
        "obligation_classes": sorted({o.obligation_class for o in obligations}),
        "obligation_kinds": sorted(owned),
        "forbidden_identity_class": CANDIDATE_MANIFEST_FORBIDDEN_IDENTITY_CLASS,
        "identity_roles": dict(
            sorted((".".join(map(str, p)), role) for p, role in context.roles.items())
        ),
        "external_binding_fields": list(
            candidate_manifest_external_binding_fields(generation)
        ),
        **checkpoint_report,
        "identity_digests": {
            G1_IDENTITY_CLASS_RUNTIME: canonical_identity_digest(context.live_runtime()),
            G1_IDENTITY_CLASS_VALIDATION: canonical_identity_digest(
                context.validation_authority()
            ),
            G1_IDENTITY_CLASS_GOVERNANCE: canonical_identity_digest(
                context.live_governance()
            ),
        },
        "change_ledger": context.ledger_report,
        "validation_identity_authority": (
            "PUBLISHED_WITH_CANDIDATE_MANIFEST"
            if mode == CANDIDATE_MANIFEST_MODE_GATE
            else "LIVE_RAW_BYTES"
        ),
        "validation_reference_commit": context.validation_reference_commit,
        "computed_binding_facts": {
            "manifest_binds_checkpoint_raw_sha256": True,
            "manifest_binds_change_ledger_raw_sha256": True,
            "manifest_records_own_sha256": False,
            "checkpoint_records_unaccounted_raw_sha256": False,
            "structural_only_identities_accepted": False,
            "historical_identity_used_as_live_binding": False,
            "placeholder_or_stale_sha_used": False,
            "derivation": (
                "Computed by validate_g1_candidate_manifest_contract from the "
                "manifest, change-ledger and checkpoint bytes; never read from a "
                "self-label."
            ),
        },
    }


# --- the G1 candidate change ledger -----------------------------------------

G1_CANDIDATE_CHANGE_LEDGER_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "artifact_type",
        "ledger_semantics",
        "generation_id",
        "lineage_id",
        "candidate_id",
        "candidate_artifact_paths",
        "predecessor",
        "modified_files",
        "identity_digests",
        "live_roles",
        "tests_executed",
        "execution_status",
        "lifecycle_status",
    }
)
G1_LEDGER_PREDECESSOR_KEYS: frozenset[str] = frozenset(
    {
        "generation_id",
        "lineage_id",
        "candidate_id",
        "relationship",
        "repository_head_commit",
        "historical_evidence",
        "fullstack_01_reference",
        "known_historical_inconsistency",
    }
)
G1_LEDGER_EVIDENCE_KEYS: frozenset[str] = frozenset(
    {"role", "path", "publication_commit", "raw_sha256", "evidence_class"}
)
G1_HISTORICAL_EVIDENCE_CLASS = "HISTORICAL_PREDECESSOR_EVIDENCE_NOT_A_LIVE_BINDING"
G1_LEDGER_CHANGE_CLASSES: frozenset[str] = frozenset(
    {"MODIFY", "CREATE", "PUBLISH_UNCHANGED"}
)
G1_LEDGER_ABSENT_SENTINEL = "ABSENT_AT_PREDECESSOR_COMMIT"
G1_LEDGER_NOT_APPLICABLE = "NOT_APPLICABLE"
G1_LEDGER_MODIFIED_FILE_KEYS: frozenset[str] = frozenset(
    {
        "path",
        "change_class",
        "predecessor_raw_sha256",
        "candidate_raw_sha256",
        "publication_source",
        "summary",
    }
)
G1_LEDGER_PUBLICATION_SOURCE_KEYS: frozenset[str] = frozenset(
    {"evidence_path", "evidence_commit", "evidence_pointer"}
)
G1_LIVE_ROLE_KEYS: frozenset[str] = frozenset(
    {
        "role",
        "path",
        "raw_sha256",
        "identity_class",
        "lifecycle_status",
        "authority_justification",
    }
)
#: Live-role lifecycle status, by the role path's change class.
G1_LIVE_ROLE_STATUS_BY_CHANGE: Mapping[str | None, str] = {
    "MODIFY": "MODIFIED_IN_G1_CANDIDATE",
    "CREATE": "CREATED_IN_G1_CANDIDATE",
    "PUBLISH_UNCHANGED": "PUBLISHED_UNCHANGED_IN_G1_CANDIDATE",
    None: "CARRIED_FORWARD_UNCHANGED_FROM_PREDECESSOR_COMMIT",
}
G1_LEDGER_TEST_KEYS: frozenset[str] = frozenset(
    {"suite", "command", "raw_sha256", "ran", "failures", "errors", "skipped", "result"}
)
G1_LEDGER_DIGEST_KEYS: Mapping[str, str] = {
    "runtime": "runtime_identity",
    "validation": "validation_identity",
    "governance_authority": "governance_authority_identity",
}

G1_CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS: tuple[IdentityObligation, ...] = (
    IdentityObligation(
        "G1L-P1", "g1_ledger_historical_evidence",
        ("predecessor", "historical_evidence", "*", "raw_sha256"),
        AUTHORITY_PUBLISHED_GIT_BLOB,
        "Typed predecessor evidence, proved by its blob in a published commit.",
    ),
    IdentityObligation(
        "G1L-M1", "g1_ledger_modified_files",
        ("modified_files", "*", "predecessor_raw_sha256"),
        AUTHORITY_PUBLISHED_GIT_BLOB,
        "A modified file's bytes at the declared predecessor commit.",
    ),
    IdentityObligation(
        "G1L-M2", "g1_ledger_modified_files",
        ("modified_files", "*", "candidate_raw_sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "A modified file's candidate raw SHA-256.",
    ),
    IdentityObligation(
        "G1L-D1", "g1_ledger_identity_digests", ("identity_digests", "*"),
        AUTHORITY_LIVE_IMPLEMENTATION,
        "The three live G1 identity digests.",
    ),
    IdentityObligation(
        "G1L-R1", "g1_ledger_live_roles", ("live_roles", "*", "raw_sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "The raw SHA-256 of every live G1 role.",
    ),
    IdentityObligation(
        "G1L-T1", "g1_ledger_tests", ("tests_executed", "*", "raw_sha256"),
        AUTHORITY_LIVE_RAW_BYTES,
        "Raw SHA-256 of each executed validation suite.",
    ),
)


def g1_historical_evidence_roles(
    generation: AuthorityGeneration | None = None,
) -> dict[str, str]:
    """The closed set of typed predecessor evidence roles a G1 ledger states."""

    from src.main_full81_authorization_v7_4 import (
        SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH,
    )

    predecessor = _g1_predecessor_generation(generation or CURRENT_GENERATION)
    return {
        "R8_ACCEPTED_LIFECYCLE_RECORD": predecessor.accepted_lifecycle_record_path,
        "R8_MAIN_FULL81_SCOPE_AUTHORIZATION": SUPERSEDED_R8_AUTHORIZATION_RELATIVE_PATH,
    }


def _resolve_json_pointer_text(payload: Any, text: str) -> Any:
    tokens = parse_rfc6901_pointer(text)
    _require(
        tokens is not None,
        "U06_ROLE_SCHEMA_INVALID",
        f"evidence pointer {text!r} is not a well-formed RFC 6901 pointer.",
    )
    node = payload
    for token in tokens or ():
        if isinstance(node, list):
            _require(
                token.isdigit(),
                "U06_ROLE_TARGET_MISMATCH",
                f"evidence pointer {text!r} indexes a list with {token!r}.",
            )
            index = int(token)
            _require(
                0 <= index < len(node),
                "U06_ROLE_TARGET_MISMATCH",
                f"evidence pointer {text!r} is out of range.",
            )
            node = node[index]
        elif isinstance(node, Mapping) and token in node:
            node = node[token]
        else:
            raise U06LifecycleError(
                "U06_ROLE_TARGET_MISMATCH",
                f"evidence pointer {text!r} does not resolve.",
            )
    return node


def _g1_published_blob_sha(
    root: Path, commit: Any, relative: str, *, label: str, what: str
) -> str | None:
    """SHA-256 of ``relative`` in a full, published ancestor commit of HEAD."""

    _require(
        isinstance(commit, str) and bool(_COMMIT_RE.match(commit)),
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: {what} commit is not a full SHA-1: {commit!r}",
    )
    _require(
        is_ancestor(root, commit, "HEAD"),
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: {what} commit {commit} is not an ancestor of HEAD.",
    )
    return blob_sha256_at(root, commit, relative)


class _G1LedgerContext(_RoleBinding):
    def __init__(
        self,
        root: Path,
        ledger: Mapping[str, Any],
        manifest: Mapping[str, Any],
        generation: AuthorityGeneration,
        mode: str,
        label: str,
        manifest_context: _G1ContractContext,
    ) -> None:
        super().__init__(root, mode, label)
        self.ledger = ledger
        self.manifest = manifest
        self.generation = generation
        self.axes = manifest_context


def _g1_verify_ledger_historical_evidence(ctx: _G1LedgerContext, items: list[_Item]):
    entries = ctx.ledger["predecessor"]["historical_evidence"]
    expected = {("predecessor", "historical_evidence", i, "raw_sha256") for i in range(len(entries))}
    _require(
        {item[0] for item in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every historical evidence entry needs exactly its raw SHA-256.",
    )
    for index, entry in enumerate(entries):
        actual = _g1_published_blob_sha(
            ctx.root,
            entry["publication_commit"],
            entry["path"],
            label=ctx.label,
            what=f"historical evidence {entry['role']}",
        )
        _require(
            actual is not None,
            "U06_PUBLICATION_PROOF_INVALID",
            f"{ctx.label}: {entry['path']} does not exist in commit "
            f"{entry['publication_commit']}.",
        )
        ctx.bind(
            ("predecessor", "historical_evidence", index, "raw_sha256"),
            entry["raw_sha256"],
            actual,
            f"g1_historical_git_blob:{entry['role']}",
        )


def _g1_change_surface() -> tuple[str, ...]:
    return tuple(
        sorted(
            set(ACCEPTED_IMPLEMENTATION_PATHS)
            | set(VALIDATION_IDENTITY_PATHS)
            | set(governance_authority_identity_paths())
        )
    )


def _blob_sha256_map(
    root: Path, commit: str, paths: Sequence[str], *, label: str
) -> dict[str, str | None]:
    """SHA-256 of each path's blob in ``commit`` (``None`` if absent), one Git call."""

    request = b"".join(f"{commit}:{relative}\n".encode("utf-8") for relative in paths)
    done = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=root,
        input=request,
        capture_output=True,
        check=False,
    )
    _require(
        done.returncode == 0,
        "U06_PUBLICATION_PROOF_INVALID",
        f"{label}: git cat-file --batch failed for {commit}: "
        f"{done.stderr.decode('utf-8', 'replace').strip()}",
    )
    data = done.stdout
    offset = 0
    out: dict[str, str | None] = {}
    for relative in paths:
        newline = data.index(b"\n", offset)
        header = data[offset:newline].decode("utf-8", "replace")
        offset = newline + 1
        if header.endswith(" missing") or header.endswith(" ambiguous"):
            out[relative] = None
            continue
        _, kind, size = header.split(" ")
        content = data[offset : offset + int(size)]
        offset += int(size) + 1
        out[relative] = hashlib.sha256(content).hexdigest() if kind == "blob" else None
    return out


def _g1_verify_ledger_modified_files(ctx: _G1LedgerContext, items: list[_Item]):
    entries = ctx.ledger["modified_files"]
    base = ctx.ledger["predecessor"]["repository_head_commit"]
    expected: set[tuple[Any, ...]] = set()
    for index, entry in enumerate(entries):
        expected.add(("modified_files", index, "candidate_raw_sha256"))
        if entry["predecessor_raw_sha256"] != G1_LEDGER_ABSENT_SENTINEL:
            expected.add(("modified_files", index, "predecessor_raw_sha256"))
    _require(
        {item[0] for item in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: modified-file identities are incomplete or extra.",
    )
    # Closed world: the listed set is EXACTLY the set of G1 identity-surface
    # paths whose live bytes differ from the declared predecessor commit.
    surface = _g1_change_surface()
    _g1_published_blob_sha(
        ctx.root, base, surface[0], label=ctx.label, what="predecessor repository head"
    )
    predecessor = _blob_sha256_map(ctx.root, base, surface, label=ctx.label)
    live = {
        relative: ctx.axes.candidate_sha(relative, field="G1 identity surface")
        for relative in surface
    }
    changed = sorted(r for r in predecessor if predecessor[r] != live[r])
    listed = [entry["path"] for entry in entries]
    _require(
        listed == changed,
        "U06_ROLE_TARGET_MISMATCH",
        f"{ctx.label}: modified_files is not the exact change set over the G1 "
        f"identity surface against {base}: unlisted={sorted(set(changed) - set(listed))}, "
        f"not_changed={sorted(set(listed) - set(changed))}",
    )
    for index, entry in enumerate(entries):
        relative = entry["path"]
        absent = predecessor[relative] is None
        _require(
            absent == (entry["predecessor_raw_sha256"] == G1_LEDGER_ABSENT_SENTINEL)
            and absent == (entry["change_class"] in ("CREATE", "PUBLISH_UNCHANGED")),
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: {relative} is classified {entry['change_class']} but is "
            f"{'absent from' if absent else 'present in'} the predecessor commit.",
        )
        if entry["change_class"] == "PUBLISH_UNCHANGED":
            source = entry["publication_source"]
            blob = _git_bytes(
                ctx.root,
                "cat-file",
                "blob",
                f"{source['evidence_commit']}:{source['evidence_path']}",
            )
            _g1_published_blob_sha(
                ctx.root,
                source["evidence_commit"],
                source["evidence_path"],
                label=ctx.label,
                what=f"publication source of {relative}",
            )
            _require(
                blob is not None,
                "U06_PUBLICATION_PROOF_INVALID",
                f"{ctx.label}: publication source of {relative} is not in Git.",
            )
            recorded = _resolve_json_pointer_text(
                _strict_json_object(blob or b"", label=f"{ctx.label} publication source"),
                source["evidence_pointer"],
            )
            _require(
                recorded == entry["candidate_raw_sha256"],
                "U06_ROLE_TARGET_MISMATCH",
                f"{ctx.label}: {relative} is published unchanged, but its published "
                f"evidence records {recorded!r}, not {entry['candidate_raw_sha256']}.",
            )
        else:
            _require(
                entry.get("publication_source") == G1_LEDGER_NOT_APPLICABLE,
                "U06_ROLE_SCHEMA_INVALID",
                f"{ctx.label}: only a PUBLISH_UNCHANGED entry carries a "
                "publication source.",
            )
        if not absent:
            ctx.bind(
                ("modified_files", index, "predecessor_raw_sha256"),
                entry["predecessor_raw_sha256"],
                predecessor[relative],
                f"g1_predecessor_blob:{relative}",
            )
        ctx.bind(
            ("modified_files", index, "candidate_raw_sha256"),
            entry["candidate_raw_sha256"],
            live[relative],
            f"g1_candidate_file:{relative}",
        )


def _g1_verify_ledger_identity_digests(ctx: _G1LedgerContext, items: list[_Item]):
    expected = {("identity_digests", key) for key in G1_LEDGER_DIGEST_KEYS}
    _require(
        {item[0] for item in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: identity_digests must state exactly "
        f"{sorted(G1_LEDGER_DIGEST_KEYS)}.",
    )
    for pointer, value, _ in items:
        section = G1_LEDGER_DIGEST_KEYS[str(pointer[1])]
        live = canonical_identity_digest(ctx.axes.live_axis(section))
        _require(
            ctx.manifest[section]["digest"] == live,
            "U06_ROLE_TARGET_MISMATCH",
            f"{ctx.label}: the ledger and manifest disagree on the {section} digest.",
        )
        ctx.bind(pointer, value, live, f"live_{section}_digest")


def _g1_verify_ledger_live_roles(ctx: _G1LedgerContext, items: list[_Item]):
    rows = ctx.ledger["live_roles"]
    expected = {("live_roles", i, "raw_sha256") for i in range(len(rows))}
    _require(
        {item[0] for item in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every live role needs exactly its raw SHA-256.",
    )
    for index, row in enumerate(rows):
        ctx.bind(
            ("live_roles", index, "raw_sha256"),
            row["raw_sha256"],
            ctx.axes.candidate_sha(row["path"], field="live_roles.raw_sha256"),
            f"g1_live_role:{row['path']}",
        )


def _g1_verify_ledger_tests(ctx: _G1LedgerContext, items: list[_Item]):
    suites = ctx.ledger["tests_executed"]
    expected = {("tests_executed", i, "raw_sha256") for i in range(len(suites))}
    _require(
        {item[0] for item in items} == expected and len(items) == len(expected),
        "U06_ROLE_SCHEMA_INVALID",
        f"{ctx.label}: every executed suite needs exactly its raw SHA-256.",
    )
    for index, entry in enumerate(suites):
        ctx.bind(
            ("tests_executed", index, "raw_sha256"),
            entry["raw_sha256"],
            ctx.axes.candidate_sha(entry["suite"], field="tests_executed.raw_sha256"),
            f"validation_suite:{entry['suite']}",
        )


G1_CANDIDATE_CHANGE_LEDGER_OBLIGATION_VERIFIERS: dict[str, Any] = {
    "g1_ledger_historical_evidence": _g1_verify_ledger_historical_evidence,
    "g1_ledger_modified_files": _g1_verify_ledger_modified_files,
    "g1_ledger_identity_digests": _g1_verify_ledger_identity_digests,
    "g1_ledger_live_roles": _g1_verify_ledger_live_roles,
    "g1_ledger_tests": _g1_verify_ledger_tests,
}


def _g1_check_ledger_structure(
    ledger: Mapping[str, Any],
    manifest: Mapping[str, Any],
    generation: AuthorityGeneration,
    label: str,
) -> None:
    def keyed(value: Any, keys: frozenset[str] | set[str], what: str) -> Mapping[str, Any]:
        _require(
            isinstance(value, Mapping) and set(value) == set(keys),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: {what} must have exactly {sorted(keys)}; observed "
            f"{sorted(value) if isinstance(value, Mapping) else value!r}",
        )
        return value

    def nonempty_text(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    keyed(ledger, G1_CANDIDATE_CHANGE_LEDGER_KEYS, "the ledger")
    _require(
        ledger["artifact_type"]
        == generation.artifact_type_prefix + CANDIDATE_CHANGE_LEDGER_ARTIFACT_TYPE_SUFFIX,
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type {ledger['artifact_type']!r} is not this "
        "generation's candidate change ledger type.",
    )
    _require(
        ledger["schema_version"]
        == generation.schema_prefix + CANDIDATE_CHANGE_LEDGER_SCHEMA_SUFFIX,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version {ledger['schema_version']!r} is not this "
        "generation's ledger schema.",
    )
    _require(
        ledger["ledger_semantics"] == CANDIDATE_CHANGE_LEDGER_SEMANTICS,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: ledger_semantics must be {CANDIDATE_CHANGE_LEDGER_SEMANTICS!r}.",
    )
    for field, want in (
        ("generation_id", generation.generation_id),
        ("lineage_id", generation.lineage_id),
    ):
        _require(
            ledger[field] == want,
            "U06_LINEAGE_MISMATCH",
            f"{label}: {field} must be {want!r}; observed {ledger[field]!r}",
        )
    _require(
        ledger["candidate_id"] not in generation.superseded_candidate_ids
        and ledger["candidate_id"] == generation.candidate_id,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_id must be {generation.candidate_id!r}.",
    )
    _require(
        _strict_equal(
            ledger["candidate_artifact_paths"],
            {
                "checkpoint": generation.candidate_checkpoint_path,
                "manifest": generation.candidate_manifest_path,
                "change_ledger": generation.candidate_change_ledger_path,
            },
        ),
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: candidate_artifact_paths must name this candidate's checkpoint, "
        "manifest and change ledger.",
    )

    predecessor = keyed(ledger["predecessor"], G1_LEDGER_PREDECESSOR_KEYS, "predecessor")
    want = _g1_predecessor_constant(generation)
    _require(
        predecessor["generation_id"] == want["generation_id"]
        and predecessor["lineage_id"] == want["lineage_id"]
        and predecessor["candidate_id"] == want["candidate_id"]
        and predecessor["relationship"] == G1_PREDECESSOR_RELATIONSHIP,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: predecessor must name the declared predecessor generation as "
        "superseded historical evidence.",
    )
    _require(
        isinstance(predecessor["repository_head_commit"], str)
        and bool(_COMMIT_RE.match(predecessor["repository_head_commit"]))
        and predecessor["repository_head_commit"]
        == manifest.get("repository_head_at_authoring"),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: predecessor.repository_head_commit must be a full commit id "
        "equal to the manifest's repository_head_at_authoring.",
    )
    roles = g1_historical_evidence_roles(generation)
    evidence = predecessor["historical_evidence"]
    _require(
        isinstance(evidence, list)
        and [entry.get("role") for entry in evidence if isinstance(entry, Mapping)]
        == sorted(roles),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: historical_evidence must state exactly the roles "
        f"{sorted(roles)}, sorted.",
    )
    for entry in evidence:
        keyed(entry, G1_LEDGER_EVIDENCE_KEYS, "a historical_evidence entry")
        _require(
            entry["path"] == roles[entry["role"]]
            and entry["evidence_class"] == G1_HISTORICAL_EVIDENCE_CLASS,
            "U06_ROLE_TARGET_MISMATCH",
            f"{label}: historical evidence {entry['role']} must name "
            f"{roles[entry['role']]} as {G1_HISTORICAL_EVIDENCE_CLASS}.",
        )
    _require(
        isinstance(predecessor["fullstack_01_reference"], Mapping)
        and nonempty_text(predecessor["known_historical_inconsistency"]),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: fullstack_01_reference must be an object and the known "
        "historical inconsistency must be stated.",
    )

    entries = ledger["modified_files"]
    _require(
        isinstance(entries, list) and entries,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: modified_files must be a non-empty list.",
    )
    for entry in entries:
        keyed(entry, G1_LEDGER_MODIFIED_FILE_KEYS, "a modified_files entry")
        change = entry["change_class"]
        _require(
            change in G1_LEDGER_CHANGE_CLASSES and nonempty_text(entry["summary"]),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: modified file {entry.get('path')!r} needs a known change "
            "class and a summary.",
        )
        if change == "MODIFY":
            _require(
                entry["predecessor_raw_sha256"] != entry["candidate_raw_sha256"],
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: modified file {entry['path']} states two equal identities.",
            )
        if change == "PUBLISH_UNCHANGED":
            source = keyed(
                entry["publication_source"],
                G1_LEDGER_PUBLICATION_SOURCE_KEYS,
                "a publication_source",
            )
            _require(
                all(nonempty_text(source[k]) for k in G1_LEDGER_PUBLICATION_SOURCE_KEYS),
                "U06_ROLE_SCHEMA_INVALID",
                f"{label}: publication_source of {entry['path']} is incomplete.",
            )
    paths = [entry["path"] for entry in entries]
    _require(
        paths == sorted(set(paths)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: modified_files must be unique and sorted by path.",
    )

    keyed(ledger["identity_digests"], set(G1_LEDGER_DIGEST_KEYS), "identity_digests")

    rows = ledger["live_roles"]
    _require(
        isinstance(rows, list) and rows,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: live_roles must be a non-empty list.",
    )
    membership: dict[str, str] = {}
    for relative in ACCEPTED_IMPLEMENTATION_PATHS:
        membership[relative] = G1_IDENTITY_CLASS_RUNTIME
    for relative in VALIDATION_IDENTITY_PATHS:
        membership[relative] = G1_IDENTITY_CLASS_VALIDATION
    for relative in governance_authority_identity_paths():
        membership[relative] = G1_IDENTITY_CLASS_GOVERNANCE
    change_by_path = {entry["path"]: entry["change_class"] for entry in entries}
    role_names: list[str] = []
    for row in rows:
        keyed(row, G1_LIVE_ROLE_KEYS, "a live_roles entry")
        relative = row["path"]
        _require(
            membership.get(relative) == row["identity_class"]
            and row["lifecycle_status"]
            == G1_LIVE_ROLE_STATUS_BY_CHANGE[change_by_path.get(relative)]
            and nonempty_text(row["role"])
            and nonempty_text(row["authority_justification"]),
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: live role {relative!r} has the wrong identity class, a "
            "lifecycle status inconsistent with modified_files, or no role / "
            "authority justification.",
        )
        role_names.append(row["role"])
    row_paths = [row["path"] for row in rows]
    _require(
        row_paths == sorted(set(row_paths))
        and set(row_paths) == set(membership)
        and len(role_names) == len(set(role_names)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: live_roles must name every G1 identity member exactly once, "
        f"sorted by path, with unique role names; missing="
        f"{sorted(set(membership) - set(row_paths))}, extra="
        f"{sorted(set(row_paths) - set(membership))}",
    )

    suites = ledger["tests_executed"]
    _require(
        isinstance(suites, list) and suites,
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: tests_executed must be a non-empty list.",
    )
    for entry in suites:
        keyed(entry, G1_LEDGER_TEST_KEYS, "a tests_executed entry")
        counts = [entry[k] for k in ("ran", "failures", "errors", "skipped")]
        _require(
            all(isinstance(c, int) and not isinstance(c, bool) and c >= 0 for c in counts)
            and nonempty_text(entry["command"])
            and entry["result"] == "OK"
            and entry["ran"] > 0
            and entry["failures"] == 0
            and entry["errors"] == 0,
            "U06_ROLE_SCHEMA_INVALID",
            f"{label}: executed suite {entry.get('suite')!r} must have run, with "
            "zero failures and errors, result OK and a recorded command.",
        )
    names = sorted(entry["suite"] for entry in suites)
    _require(
        names == sorted(VALIDATION_IDENTITY_PATHS),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: tests_executed must record every G1 validation suite exactly "
        f"once; missing={sorted(set(VALIDATION_IDENTITY_PATHS) - set(names))}, "
        f"extra={sorted(set(names) - set(VALIDATION_IDENTITY_PATHS))}",
    )
    _require(
        _strict_equal(ledger["execution_status"], dict(G1_EXECUTION_COUNTERS)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: execution_status must record zero for every no-execution counter.",
    )
    _require(
        _strict_equal(ledger["lifecycle_status"], dict(G1_CANDIDATE_LIFECYCLE_STATE)),
        "U06_ROLE_SCHEMA_INVALID",
        f"{label}: lifecycle_status must be the candidate-time declaration.",
    )


def validate_g1_candidate_change_ledger(
    root: Path,
    ledger_bytes: bytes,
    manifest: Mapping[str, Any],
    generation: AuthorityGeneration | None = None,
    *,
    mode: str,
    context: _G1ContractContext | None = None,
) -> dict[str, Any]:
    """Validate a G1 candidate change ledger: structure, then closed world."""

    root = Path(root).resolve()
    generation = generation or CURRENT_GENERATION
    _require(
        mode in CANDIDATE_MANIFEST_MODES,
        "U06_ROLE_SCHEMA_INVALID",
        f"G1 candidate change ledger: unknown validation mode {mode!r}.",
    )
    _require(
        bool(generation.candidate_change_ledger_path),
        "U06_ROLE_SCHEMA_INVALID",
        f"generation {generation.generation_id} declares no candidate change ledger.",
    )
    label = f"G1 candidate change ledger ({generation.candidate_change_ledger_path})"
    ledger = _strict_json_object(ledger_bytes, label=label)
    _g1_check_ledger_structure(ledger, manifest, generation, label)
    identities, hidden = collect_identity_pointers(ledger)
    _require(
        not hidden,
        "U06_CANDIDATE_MANIFEST_IDENTITY_UNACCOUNTED",
        f"{label}: raw identities hidden in prose, keys or malformed values: "
        f"{['.'.join(map(str, p)) for p in hidden]}",
    )
    later = {
        generation.candidate_change_ledger_path,
        generation.candidate_checkpoint_path,
        generation.candidate_manifest_path,
    }
    for pointer, _ in identities:
        tied = later & _associated_paths(ledger, pointer)
        _require(
            not tied,
            "U06_CANDIDATE_MANIFEST_SELF_IDENTITY_REJECTED",
            f"{label}: {'.'.join(map(str, pointer))} asserts an identity of "
            f"{sorted(tied)}, which is finalized at or after the ledger.",
        )
    owned = _own_identity_pointers(
        identities, G1_CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS, label
    )
    manifest_context = context or _G1ContractContext(root, manifest, generation, mode, label)
    ledger_context = _G1LedgerContext(
        root, ledger, manifest, generation, mode, label, manifest_context
    )
    verified, structural = _verify_owned_identities(
        owned,
        identities,
        G1_CANDIDATE_CHANGE_LEDGER_OBLIGATION_VERIFIERS,
        ledger_context,
        label,
    )
    return {
        "ledger_path": generation.candidate_change_ledger_path,
        "mode": mode,
        "collected_identity_count": len(identities),
        "verified_identity_count": len(verified),
        "structural_identity_count": len(structural),
        "role_bound_identity_count": len(ledger_context.authority),
        "unaccounted_identity_count": 0,
        "obligation_classes": sorted(
            {o.obligation_class for o in G1_CANDIDATE_CHANGE_LEDGER_IDENTITY_OBLIGATIONS}
        ),
        "modified_file_count": len(ledger["modified_files"]),
        "live_role_count": len(ledger["live_roles"]),
        "executed_suite_count": len(ledger["tests_executed"]),
        "historical_evidence_count": len(ledger["predecessor"]["historical_evidence"]),
    }


#: One validator per known content contract; a contract never judges another's.
CANDIDATE_MANIFEST_CONTRACT_VALIDATORS: Mapping[str, Any] = {
    FULL81_PREFLIGHT_AUTH_GUARD_R1_CANDIDATE_MANIFEST_CONTRACT_V4: (
        validate_candidate_manifest_identity_contract
    ),
    G1_CANDIDATE_MANIFEST_CONTRACT: validate_g1_candidate_manifest_contract,
}


def validate_candidate_manifest_content_contract(
    root: Path,
    relative: str | None = None,
    payload: Mapping[str, Any] | None = None,
    generation: AuthorityGeneration | None = None,
    *,
    mode: str,
    manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Validate a candidate manifest with ITS generation's own contract."""

    generation = generation or CURRENT_GENERATION
    validator = CANDIDATE_MANIFEST_CONTRACT_VALIDATORS.get(
        generation.candidate_manifest_contract
    )
    _require(
        validator is not None,
        "U06_ROLE_SCHEMA_INVALID",
        f"generation {generation.generation_id} names no validatable "
        f"candidate-manifest contract ({generation.candidate_manifest_contract!r}).",
    )
    return validator(
        root, relative, payload, generation, mode=mode, manifest_bytes=manifest_bytes
    )


def validate_role_specifics(
    root: Path,
    role: str,
    relative: str,
    payload: Mapping[str, Any],
    resolved: Mapping[str, Mapping[str, Any]],
    generation: AuthorityGeneration | None = None,
) -> None:
    """Role-specific semantics, beyond the shared envelope."""

    generation = generation or CURRENT_GENERATION
    label = f"role {role!r} ({relative})"

    if role == "implementation_candidate":
        # R4-AUD-01: the implementation-candidate role is no longer validated by
        # its envelope alone.  GATE mode checks every identity available in a
        # clean published checkout.  A historical generation accepted under the
        # envelope-only contract declares no content contract and is not
        # re-judged retroactively.
        if generation.candidate_manifest_contract is not None:
            validate_candidate_manifest_content_contract(
                root,
                relative,
                payload,
                generation,
                mode=CANDIDATE_MANIFEST_MODE_GATE,
            )

    elif role == "independent_audit_pass":
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
            generation.candidate_checkpoint_path,
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
    root: Path,
    payload: Mapping[str, Any],
    *,
    record_relative: str,
    generation: AuthorityGeneration | None = None,
) -> dict[str, Any]:
    """Validate an accepted-lifecycle record and its whole role chain.

    Fail-closed, and ordered so the reported status names the real governance
    problem: envelope, then role authenticity, then chain consistency, then
    publication containment.

    ``generation`` selects the authority generation whose contract applies.
    When omitted it is resolved from the record own declared ``lineage_id``
    against the generation registry, so a record of a superseded generation is
    still validated by the contract it was written under rather than silently
    judged by a newer one.  That resolution is a *pure validator* convenience:
    live production authority comes from :func:`resolve_u06_lifecycle`, which
    reads only the CURRENT generation record slot, and from
    :func:`require_frozen_lifecycle`, which refuses any generation but the
    current one.
    """

    root = root.resolve()
    label = f"accepted lifecycle record ({record_relative})"

    _require(
        isinstance(payload, Mapping),
        "U06_LIFECYCLE_RECORD_INVALID",
        f"{label}: not a JSON object.",
    )
    if generation is None:
        declared_lineage = payload.get("lineage_id")
        generation = generation_for_lineage(declared_lineage)
        _require(
            generation is not None,
            "U06_LINEAGE_MISMATCH",
            f"{label}: lineage_id {declared_lineage!r} is not a declared "
            "production-authority generation lineage. Known lineages: "
            f"{sorted(GENERATIONS_BY_LINEAGE)}.",
        )
    _require(
        payload.get("artifact_type") == generation.lifecycle_record_artifact_type,
        "U06_ROLE_ARTIFACT_TYPE_MISMATCH",
        f"{label}: artifact_type must be "
        f"{generation.lifecycle_record_artifact_type!r} for generation "
        f"{generation.generation_id}.",
    )
    _require(
        payload.get("schema_version")
        == generation.lifecycle_record_schema_version,
        "U06_ROLE_SCHEMA_MISMATCH",
        f"{label}: schema_version must be "
        f"{generation.lifecycle_record_schema_version!r} for generation "
        f"{generation.generation_id}.",
    )
    _require(
        payload.get("lineage_id") == generation.lineage_id,
        "U06_LINEAGE_MISMATCH",
        f"{label}: lineage_id must be {generation.lineage_id!r}.",
    )
    _require(
        payload.get("target_candidate_id") == generation.candidate_id,
        "U06_ROLE_TARGET_MISMATCH",
        f"{label}: target_candidate_id must be {generation.candidate_id!r}.",
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
        _validate_role_path(role, relative, record_relative, generation)
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
            root,
            role,
            relative,
            record,
            live_digest=live_digest,
            generation=generation,
        )
        _validate_bound_roles(
            root, role, relative, record, resolved, generation
        )
        validate_role_specifics(
            root, role, relative, record, resolved, generation
        )
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
    generations = {r["generation_id"] for r in resolved.values()}
    _require(
        generations == {generation.generation_id},
        "U06_CROSS_GENERATION_ROLE_REJECTED",
        f"{label}: roles disagree on authority generation: {sorted(generations)}. "
        "A lifecycle may never be assembled from roles of different "
        "production-authority generations.",
    )
    _require(
        lineages == {generation.lineage_id},
        "U06_LINEAGE_MISMATCH",
        f"{label}: roles disagree on lineage_id: {sorted(lineages)}",
    )
    _require(
        targets == {generation.candidate_id},
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
        "generation_id": generation.generation_id,
        "generation": generation.as_dict(),
        "is_current_generation": (
            generation.generation_id == CURRENT_GENERATION.generation_id
        ),
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
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
        # Historical U-06 ALIGNMENT generation audit history. Explicitly
        # namespaced by R2-AUD-03 remediation so it can never be mistaken for
        # the active candidate's audit state. Retained, never deleted.
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
        "historical_u06_alignment_audit": {
            "scope": "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_GENERATION",
            "audit_status": HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
            "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
            "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
            "is_current_candidate_audit_state": False,
            "note": (
                "Audit history of the U-06 alignment generation only. It is NOT "
                "the audit state of the active preflight-authorization-guard "
                "candidate. Reporting it as such was blocker R2-AUD-03."
            ),
        },
        # The generation-3 (preflight-authorization-guard) register, retained
        # under its historical key; since G1 it is a PREDECESSOR register.
        "preflight_authorization_guard_candidate_audit_history": {
            k: dict(v)
            for k, v in PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY.items()
        },
        # The ACTIVE generation's own candidate audit history, separately.
        "current_generation_candidate_audit_history": {
            k: dict(v) for k, v in CURRENT_CANDIDATE_AUDIT_HISTORY.items()
        },
        "active_candidate_id": ACTIVE_CANDIDATE_ID,
        "active_candidate_audit": dict(
            CURRENT_CANDIDATE_AUDIT_HISTORY[ACTIVE_CANDIDATE_ID]
        ),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def absent_lifecycle(
    *,
    reason: str | None = None,
    record_path: str | None = None,
    generation: AuthorityGeneration | None = None,
) -> dict[str, Any]:
    """The most restrictive lifecycle state: nothing accepted, nothing frozen."""

    generation = generation or CURRENT_GENERATION
    return {
        "lifecycle_module_version": LIFECYCLE_MODULE_VERSION,
        "generation_id": generation.generation_id,
        "generation": generation.as_dict(),
        "is_current_generation": (
            generation.generation_id == CURRENT_GENERATION.generation_id
        ),
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
        "record_path": record_path or generation.accepted_lifecycle_record_path,
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
            "No accepted lifecycle record exists for the current "
            f"production-authority generation {generation.generation_id} at "
            f"{generation.accepted_lifecycle_record_path}. Production authority "
            "cannot be frozen by an unaccepted candidate, by clean Git state, by "
            "matching authority hashes, by publishing candidate bytes, by any "
            "set of unrelated historical artifacts, or by a superseded "
            "generation accepted lifecycle."
        ),
        "implementation_identity_digest": None,
        "required_future_roles": list(REQUIRED_ACCEPTED_ROLES),
        "satisfied_roles": {},
        "missing_roles": list(REQUIRED_ACCEPTED_ROLES),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        # Historical U-06 ALIGNMENT generation audit history. Explicitly
        # namespaced by R2-AUD-03 remediation so it can never be mistaken for
        # the active candidate's audit state. Retained, never deleted.
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
        "historical_u06_alignment_audit": {
            "scope": "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_GENERATION",
            "audit_status": HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
            "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
            "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
            "is_current_candidate_audit_state": False,
            "note": (
                "Audit history of the U-06 alignment generation only. It is NOT "
                "the audit state of the active preflight-authorization-guard "
                "candidate. Reporting it as such was blocker R2-AUD-03."
            ),
        },
        # The generation-3 (preflight-authorization-guard) register, retained
        # under its historical key; since G1 it is a PREDECESSOR register.
        "preflight_authorization_guard_candidate_audit_history": {
            k: dict(v)
            for k, v in PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY.items()
        },
        # The ACTIVE generation's own candidate audit history, separately.
        "current_generation_candidate_audit_history": {
            k: dict(v) for k, v in CURRENT_CANDIDATE_AUDIT_HISTORY.items()
        },
        "active_candidate_id": ACTIVE_CANDIDATE_ID,
        "active_candidate_audit": dict(
            CURRENT_CANDIDATE_AUDIT_HISTORY[ACTIVE_CANDIDATE_ID]
        ),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def resolve_u06_lifecycle(root: Path) -> dict[str, Any]:
    """Resolve U-06 lifecycle state from live bytes and Git. Read-only.

    Never raises: anything invalid resolves to a NOT_FROZEN state carrying the
    reason, so callers report the blocker instead of crashing. Writes nothing.

    Every returned state additionally carries ``durable_publication``, the
    ``R2-AUD-01`` report on whether each required authority file is actually
    reachable from published Git content.  It is attached to *every* branch,
    including the fail-closed ones, so publication durability can never be
    silently absent from a resolved state.
    """

    root = root.resolve()
    state = _resolve_u06_lifecycle_inner(root)
    state["durable_publication"] = durable_publication_requirements(root)
    return state


def _resolve_u06_lifecycle_inner(root: Path) -> dict[str, Any]:
    """Lifecycle resolution proper; see :func:`resolve_u06_lifecycle`."""

    root = root.resolve()
    generation = CURRENT_GENERATION
    record_relative = generation.accepted_lifecycle_record_path
    path = root / record_relative

    if not path.is_file():
        return absent_lifecycle(
            record_path=record_relative, generation=generation
        )

    tracked, clean = is_tracked_and_clean(root, record_relative)
    if not tracked or not clean:
        state = absent_lifecycle(
            record_path=record_relative, generation=generation,
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
            record_path=record_relative, generation=generation,
            reason=f"Accepted-lifecycle record is not readable JSON: {exc}",
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        return state

    try:
        return validate_accepted_lifecycle_payload(
            root,
            payload,
            record_relative=record_relative,
            generation=generation,
        )
    except U06LifecycleError as exc:
        state = absent_lifecycle(
            record_path=record_relative, generation=generation, reason=f"{exc.status}: {exc}"
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["accepted_lifecycle_overlay"] = PRESENT_INVALID_OVERLAY_STATUS
        state["rejected_status"] = exc.status
        return state


#: Invariants a resolved lifecycle mapping must satisfy before any freeze.
#: ``generation_id`` / ``is_current_generation`` are the H-01 gate: a complete,
#: valid, published accepted lifecycle of a SUPERSEDED generation must never
#: freeze live production authority.
_FROZEN_INVARIANTS: Mapping[str, Any] = {
    "accepted_lifecycle_overlay": PRESENT_VALID_OVERLAY_STATUS,
    "generation_id": CURRENT_GENERATION.generation_id,
    "is_current_generation": True,
    "lineage_id": CURRENT_GENERATION.lineage_id,
    "target_candidate_id": CURRENT_GENERATION.candidate_id,
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
            "No accepted lifecycle was resolved. Production authority cannot be "
            "frozen without an accepted lifecycle record of the current "
            f"production-authority generation {CURRENT_GENERATION.generation_id}.",
        )

    # Absence first: when no accepted-lifecycle record exists for the current
    # generation at all, say so. It is the most informative answer and the most
    # restrictive state.
    if lifecycle.get("accepted_lifecycle_overlay") == PRE_ACCEPTANCE_OVERLAY_STATUS:
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_ABSENT",
            lifecycle.get("freeze_blocked_reason")
            or (
                "No accepted lifecycle record exists for the current "
                f"production-authority generation "
                f"{CURRENT_GENERATION.generation_id}."
            ),
        )

    # Then completeness: a mapping that does not satisfy every role is
    # incomplete, and saying so is more useful than naming a generation
    # problem it also has.
    satisfied = lifecycle.get("satisfied_roles")
    if not isinstance(satisfied, Mapping) or set(satisfied) != set(
        REQUIRED_ACCEPTED_ROLES
    ):
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
            "Accepted lifecycle does not satisfy every required role: "
            f"required={list(REQUIRED_ACCEPTED_ROLES)}, "
            f"satisfied={sorted(satisfied) if isinstance(satisfied, Mapping) else satisfied}",
        )
    missing_first: Sequence[Any] = lifecycle.get("missing_roles") or []
    if list(missing_first):
        raise U06LifecycleError(
            "U06_ACCEPTED_LIFECYCLE_INCOMPLETE",
            f"Accepted lifecycle reports missing roles: {list(missing_first)}",
        )

    for field, expected in _FROZEN_INVARIANTS.items():
        observed = lifecycle.get(field)
        if observed != expected:
            if field in ("generation_id", "is_current_generation"):
                observed_generation = lifecycle.get("generation_id")
                status = (
                    "U06_SUPERSEDED_GENERATION_REJECTED"
                    if observed_generation in GENERATIONS_BY_ID
                    else "U06_ACCEPTED_LIFECYCLE_INVALID"
                )
            elif (
                lifecycle.get("accepted_lifecycle_overlay")
                == PRE_ACCEPTANCE_OVERLAY_STATUS
            ):
                status = "U06_ACCEPTED_LIFECYCLE_ABSENT"
            else:
                status = "U06_ACCEPTED_LIFECYCLE_INVALID"
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
        "generation_id": resolved.get("generation_id"),
        "is_current_generation": resolved.get("is_current_generation"),
        "current_generation_id": CURRENT_GENERATION.generation_id,
        "current_generation_lineage_id": CURRENT_GENERATION.lineage_id,
        "lineage_id": resolved.get("lineage_id"),
        "target_candidate_id": resolved.get("target_candidate_id"),
        "u06_alignment_status": resolved.get("u06_alignment_status"),
        # R2-AUD-03: this generic field is the audit state of the ACTIVE
        # generation's current candidate and of nothing else. The two fields
        # beneath it say so explicitly, so a consumer can never have to guess
        # whose audit state it is reading.
        "u06_independent_audit_status": resolved.get("u06_independent_audit_status"),
        "u06_independent_audit_status_scope": (
            "ACTIVE_GENERATION_CURRENT_CANDIDATE_ONLY"
        ),
        "u06_independent_audit_status_candidate_id": resolved.get(
            "target_candidate_id"
        ),
        "historical_u06_alignment_audit_status": (
            HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS
        ),
        "historical_u06_alignment_audit_status_is_current": False,
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
        # R2-AUD-01: publication durability of every required authority file.
        "durable_publication": resolved.get("durable_publication"),
        "missing_required_authority_files": list(
            (resolved.get("durable_publication") or {}).get(
                "missing_required_authority_files"
            )
            or []
        ),
        "missing_roles": list(resolved.get("missing_roles") or []),
        "satisfied_roles": sorted(resolved.get("satisfied_roles") or {}),
        "required_lifecycle_sequence": list(REQUIRED_LIFECYCLE_SEQUENCE),
        "lifecycle_distinctions": list(LIFECYCLE_DISTINCTIONS),
        # Historical U-06 ALIGNMENT generation audit history. Explicitly
        # namespaced by R2-AUD-03 remediation so it can never be mistaken for
        # the active candidate's audit state. Retained, never deleted.
        "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
        "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
        "historical_u06_alignment_audit": {
            "scope": "U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_GENERATION",
            "audit_status": HISTORICAL_U06_ALIGNMENT_AUDIT_STATUS,
            "candidate_r1_audit": dict(CANDIDATE_R1_AUDIT_RECORD),
            "candidate_r2_audit": dict(CANDIDATE_R2_AUDIT_RECORD),
            "is_current_candidate_audit_state": False,
            "note": (
                "Audit history of the U-06 alignment generation only. It is NOT "
                "the audit state of the active preflight-authorization-guard "
                "candidate. Reporting it as such was blocker R2-AUD-03."
            ),
        },
        # The generation-3 (preflight-authorization-guard) register, retained
        # under its historical key; since G1 it is a PREDECESSOR register.
        "preflight_authorization_guard_candidate_audit_history": {
            k: dict(v)
            for k, v in PREFLIGHT_AUTH_GUARD_CANDIDATE_AUDIT_HISTORY.items()
        },
        # The ACTIVE generation's own candidate audit history, separately.
        "current_generation_candidate_audit_history": {
            k: dict(v) for k, v in CURRENT_CANDIDATE_AUDIT_HISTORY.items()
        },
        "active_candidate_id": ACTIVE_CANDIDATE_ID,
        "active_candidate_audit": dict(
            CURRENT_CANDIDATE_AUDIT_HISTORY[ACTIVE_CANDIDATE_ID]
        ),
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

    generation = CURRENT_GENERATION
    return {
        "generation_id": generation.generation_id,
        "generation": generation.as_dict(),
        "historical_generations": [g.as_dict() for g in HISTORICAL_GENERATIONS],
        "superseded_generation_can_freeze_live_authority": False,
        "advancing_a_generation_requires_a_validator_rewrite": False,
        "advancing_a_generation_mutates_a_predecessor_artifact": False,
        "lineage_id": generation.lineage_id,
        "target_candidate_id": generation.candidate_id,
        "candidate_checkpoint_path": generation.candidate_checkpoint_path,
        "candidate_manifest_path": generation.candidate_manifest_path,
        "accepted_lifecycle_record_path": (
            generation.accepted_lifecycle_record_path
        ),
        "accepted_lifecycle_artifact_type": (
            generation.lifecycle_record_artifact_type
        ),
        "accepted_lifecycle_schema_version": (
            generation.lifecycle_record_schema_version
        ),
        "record_exists_today": False,
        "role_contracts": {
            role: contract.as_dict()
            for role, contract in generation.role_contracts.items()
        },
        "roles_a_candidate_may_never_fill": list(NON_SELF_ACCEPTABLE_ROLES),
        "forbidden_role_paths": list(generation.candidate_artifact_paths),
        "forbidden_role_prefixes": list(NON_GOVERNANCE_PREFIXES),
        "superseded_candidate_ids_rejected": list(
            generation.superseded_candidate_ids
        ),
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
            f"declaring lineage_id = {generation.lineage_id}",
            f"declaring target_candidate_id = {generation.candidate_id}",
            "declaring the exact candidate checkpoint path and live SHA-256 of "
            f"generation {generation.generation_id}",
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
            "guessed, reserved, or stubbed in this module. A superseded "
            "generation accepted lifecycle, however complete and published, "
            "cannot freeze live production authority."
        ),
    }


def runtime_dependency_report(root: Path) -> dict[str, Any]:
    """Read-only report of the accepted implementation and validation surfaces."""

    root = root.resolve()
    identity = implementation_identity(root)
    return {
        "generation_id": CURRENT_GENERATION.generation_id,
        "lineage_id": CURRENT_GENERATION.lineage_id,
        "predecessor_generation_id": CURRENT_GENERATION.predecessor_generation_id,
        "predecessor_lineage_id": CURRENT_GENERATION.predecessor_lineage_id,
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
