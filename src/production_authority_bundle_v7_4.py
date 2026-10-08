"""Additive V7.4 production-authority successor bundle (bounded U-06 alignment).

Purpose
-------
The accepted methodology, evidence, and governance-sequencing authority of this
repository is **V7.4**.  The live pre-execution production-authority mechanism,
however, exact-pins only the **V7.3** methodology/evidence/lifecycle trio through
``src.production_input_authority_v7_3.AUTHORITY_FILES``.  That is the exact
``U-06`` defect: a production run gated by that mechanism alone could not prove
which accepted V7.4 authority it was executed under.

This module closes that binding gap **additively**.  It is a successor, not a
replacement:

* ``src/production_input_authority_v7_3.py`` is **not modified**.  Its V7.3
  methodology/evidence/lifecycle pins are retained here verbatim as
  ``INHERITED_V7_3_HISTORICAL_AUTHORITY`` and are verified on every bundle check,
  so a destructive rewrite of the historical layer fails this gate closed.
* The accepted scientific implementation, canonical planning input, solver
  settings, alpha/beta grid, and output namespace are untouched.  This module
  contains no optimization formulation, no model construction, no economic
  evaluation, and no solver call.

Scope of this module after the Candidate R1 audit
-------------------------------------------------
A fresh independent audit of Candidate R1 returned ``FAIL — REMEDIATION
REQUIRED`` on ``F-01``: the gate could reach ``PRODUCTION_AUTHORITY_FROZEN``
once candidate bytes were merely committed and pushed.  Closing that required
separating *implementation identity* from *lifecycle acceptance*.  This module
is now the **base identity** half only:

* it answers "which accepted V7.4 authority is this route bound to?" and, when
  every pin verifies, reports ``PRODUCTION_AUTHORITY_ALIGNMENT_STATUS =
  CANDIDATE_ALIGNED`` — an implementation statement, never an acceptance;
* it holds **no** acceptance, audit, closure, or freeze authority.  That lives
  in the separate overlay ``src/production_authority_lifecycle_u06.py``, so
  acceptance bytes never need to be injected into the object whose hash an
  acceptance names.

Every governance view below therefore takes a resolved ``lifecycle`` mapping and
reads U-06 state out of it.  Omitting it yields the most restrictive state
(``ABSENT`` / ``NOT_FROZEN``), so an omission can never read as acceptance, and
a lawful future acceptance changes the emitted state with no code edit.

Authority-alignment is not execution authorization
--------------------------------------------------
Five states are kept mechanically distinct and must never be conflated:

``PRODUCTION_AUTHORITY_ALIGNMENT_STATUS`` (here)
    Whether the live route can prove the accepted V7.4 identities.  When this
    bundle verifies, that is ``CANDIDATE_ALIGNED``.

``U06_INDEPENDENT_AUDIT_STATUS`` / ``U06_ACCEPTANCE_STATUS`` /
``PRODUCTION_AUTHORITY_FREEZE_STATUS`` (overlay)
    Audit outcome, acceptance/closure, and freeze.  All three are currently
    pre-acceptance, and none is implied by alignment.

``MAIN_FULL81_AUTHORIZATION_STATUS`` (resolved, not constant)
    Whether Main V7.4 Full81 may proceed.  This is now **derived** from the
    dedicated mechanism in ``src/main_full81_authorization_v7_4.py``, which
    resolves an external, published, lineage-bound authorization artifact at a
    fixed lawful path.  No such artifact exists, so the resolved state is
    ``NOT_GRANTED`` and :func:`require_full81_scope_authorization` rejects the
    ``full81`` scope.  :func:`require_a2_hard_block` still rejects every A2 /
    variable-floor scope token.  A frozen production authority would still not
    authorize Full81, and a lawful authorization would authorize only the
    mandatory no-solve Full81 production preflight — never ``optimize()``.

    The retired module constant :data:`MAIN_FULL81_AUTHORIZATION_ARTIFACT` is
    permanently ``None`` and is **never consulted**.  Editing a constant must
    never be able to authorize production, and binding an authorization path
    into these accepted bytes would drift the accepted implementation identity
    on every authorization.

Governing authority for those semantics is the accepted, published
``TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_CANDIDATE_R2_ACCEPTANCE_CLOSURE``:
``U-01`` is ``OPEN / HOLD`` and no longer blocks Main Full81 authorization,
execution, inspection, analysis, or supervisor discussion, but it must still be
resolved, independently audited, accepted, and frozen before any A2 event.  That
closure also requires this production-authority alignment to be followed by a
**fresh independent verification** before any Main Full81 authorization gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.main_full81_authorization_v7_4 import (
    AUTHORIZATION_MODULE_VERSION as FULL81_AUTHORIZATION_MODULE_VERSION,
    AUTHORIZATION_RECORD_RELATIVE_PATH as FULL81_AUTHORIZATION_RECORD_PATH,
    AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT,
    Full81AuthorizationError,
    LINEAGE_ID as FULL81_AUTHORIZATION_LINEAGE_ID,
    NOT_GRANTED as FULL81_NOT_GRANTED,
    authorization_summary,
    future_authorization_requirements,
    historical_design_precedent,
    require_full81_execution_authorization,
    require_full81_preflight_authorization,
    resolve_full81_authorization,
)
from src.production_authority_lifecycle_u06 import lifecycle_summary
from src.production_input_authority_v7_3 import (
    ACCEPTED_ANNUAL_RELATIVE_PATH,
    ACCEPTED_ANNUAL_SHA256,
    ACCEPTED_ARTIFACT_ROLE,
    AUTHORITY_FILES as V7_3_AUTHORITY_FILES,
    AUTHORITY_VERSION as V7_3_AUTHORITY_VERSION,
    sha256_file,
)


#: This module's repository root, used only as the fallback for a live
#: implementation-identity re-derivation when a caller supplies an already
#: resolved authorization without naming a root.
ROOT = Path(__file__).resolve().parents[1]

BUNDLE_VERSION = (
    "v7.4-production-authority-bundle-2026-10-02-"
    "full81-authorization-mechanism-candidate-r2"
)
BUNDLE_SCOPE = "ADDITIVE_V7_4_PRODUCTION_AUTHORITY_BASE_IDENTITY_ONLY_NO_LIFECYCLE_AUTHORITY"
BUNDLE_LINEAGE = "ADDITIVE_SUCCESSOR_TO_V7_3_PRODUCTION_INPUT_AUTHORITY_NOT_A_REPLACEMENT"

#: Alignment of the production route to accepted V7.4 authority.  This is
#: implementation/provenance identity only.  It is explicitly **not** an
#: acceptance, an audit outcome, a freeze, or Full81 authorization — see the
#: accepted-lifecycle overlay for those.
PRODUCTION_AUTHORITY_ALIGNMENT_STATUS = "CANDIDATE_ALIGNED"

#: Pre-authorization default for the Main V7.4 Full81 surface.  Deliberately
#: separate from the line above; see
#: :func:`alignment_is_not_full81_authorization`.  Every emitted authorization
#: field is **resolved** through :func:`main_full81_authorization_state`, so this
#: constant is a floor, never a grant.
MAIN_FULL81_AUTHORIZATION_STATUS = "NOT_AUTHORIZED"

#: RETIRED placeholder, permanently ``None`` and never consulted by any guard.
#:
#: It is kept, and kept ``None``, as a standing regression guard: the former
#: mechanism was "edit this constant to a path", which is unlawful here because
#: these bytes are part of the accepted implementation identity, so every
#: authorization would have caused ``U06_IMPLEMENTATION_IDENTITY_DRIFT``.
#: Authorization is now external data resolved from
#: ``src/main_full81_authorization_v7_4.py`` at a fixed lawful path.
MAIN_FULL81_AUTHORIZATION_ARTIFACT: str | None = None

#: Where a FUTURE lawful Main Full81 authorization must live.  Absent today.
MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH = (
    FULL81_AUTHORIZATION_RECORD_PATH.as_posix()
)

#: Set by the accepted governance-sequencing successor R2 closure, §9.  These
#: bytes are accepted governance text and are deliberately left unchanged.
MAIN_FULL81_REMAINING_LIFECYCLE = (
    "V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE",
    "FRESH_INDEPENDENT_VERIFICATION_OF_THAT_ALIGNMENT",
    "SEPARATE_MAIN_FULL81_AUTHORIZATION_PREFLIGHT",
    "MAIN_FULL81_EXECUTION",
)

#: ADDITIVE successor refinement.  The line above names
#: ``SEPARATE_MAIN_FULL81_AUTHORIZATION_PREFLIGHT`` as one undivided act for
#: which no mechanism existed.  This successor splits it into the acts a real
#: mechanism can distinguish, and is emitted alongside — never instead of — the
#: accepted sequence, so no accepted governance string is rewritten.
MAIN_FULL81_REMAINING_LIFECYCLE_SUCCESSOR_REFINEMENT = (
    "FULL81_AUTHORIZATION_MECHANISM_SUCCESSOR_INDEPENDENT_AUDIT",
    "FULL81_AUTHORIZATION_MECHANISM_SUCCESSOR_ACCEPTANCE_AND_RE_FREEZE",
    "SEPARATE_MAIN_FULL81_SCOPE_AUTHORIZATION",
    "MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT",
    "SEPARATE_FULL81_EXECUTION_AUTHORIZATION_AND_ARMING",
    "MAIN_FULL81_EXECUTION",
)

A2_STATUS = "HARD_BLOCKED"
A2_RESULT_EXPOSURE_STATUS = "ZERO_A2_RESULT_EXPOSURE_FIREWALL_INTACT"

#: Scope-name fragments that would route to an A2 / variable-floor universe.
#: ``PRODUCTION_CASE_SETS`` defines no such scope today; this is an explicit,
#: additive second barrier so an A2 scope can never be reached by name.
A2_BLOCKED_SCOPE_TOKENS = (
    "a2",
    "robust",
    "variable_floor",
    "variable-floor",
    "varfloor",
    "perfect_information",
    "perfect-information",
)

#: Output namespace of the accepted current route.  The historical ``v7_3``
#: segment is accepted provenance naming and is deliberately NOT renamed.
ACCEPTED_OUTPUT_NAMESPACE = "results/layer_a/final_81_v7_3/runs/<unique-run-id>"
ACCEPTED_OUTPUT_NAMESPACE_DISPOSITION = (
    "HISTORICAL_NAME_OPERATIONALLY_VALID_NOT_RENAMED_IN_THIS_ALIGNMENT"
)

CANONICAL_INPUT_EXPECTED_ROWS = 8760
CANONICAL_INPUT_EXPECTED_COLUMNS = 51
CANONICAL_INPUT_WINDOW_START = "2024-11-01 00:00:00"
CANONICAL_INPUT_WINDOW_END_INCLUSIVE = "2025-10-31 23:00:00"
CANONICAL_INPUT_INTEGRATION_STATUS = "passed"
CANONICAL_INPUT_FILENAME_NOTE = (
    "The v7_3 filename segment is accepted provenance naming for the canonical "
    "planning input and must not be renamed, regenerated, or normalized."
)

CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
)
CORE_VERSION_NOTE = (
    "A v7.2 core version label is a provenance label. It does not make the "
    "accepted implementation stale and is not evidence of methodology drift."
)


class ProductionAuthorityBundleError(RuntimeError):
    """Fail-closed V7.4 production-authority bundle error with a stable status."""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


class Full81AuthorizationNotGranted(ProductionAuthorityBundleError):
    """Raised when a Full81 scope is requested without separate authorization."""

    def __init__(self, message: str) -> None:
        super().__init__("FULL81_AUTHORIZATION_NOT_GRANTED", message)


class A2ExecutionHardBlocked(ProductionAuthorityBundleError):
    """Raised when any A2 / variable-floor scope is requested before U-01 freeze."""

    def __init__(self, message: str) -> None:
        super().__init__("A2_HARD_BLOCKED", message)


@dataclass(frozen=True)
class AuthorityPin:
    """One exact-hash production-authority binding."""

    label: str
    relative_path: str
    sha256: str
    role: str
    lifecycle: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.relative_path,
            "sha256": self.sha256,
            "role": self.role,
            "lifecycle": self.lifecycle,
        }


# ---------------------------------------------------------------------------
# A. / B.  Current accepted methodology and evidence authority (V7.4)
# ---------------------------------------------------------------------------

METHODOLOGY_EVIDENCE_AUTHORITY_V7_4: tuple[AuthorityPin, ...] = (
    AuthorityPin(
        "framework_v7_4",
        "docs/research_framework_v7_4_2026-09-26_r2.md",
        "36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273",
        "CURRENT_METHODOLOGY_AUTHORITY",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "framework_v7_4_acceptance_closure",
        "docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md",
        "39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f",
        "METHODOLOGY_ACCEPTANCE_LIFECYCLE_CLOSURE",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "framework_v7_4_acceptance_manifest",
        "results/provenance/framework_v7_4_acceptance_closure_2026-09-26/"
        "acceptance_manifest.json",
        "5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33",
        "METHODOLOGY_ACCEPTANCE_MANIFEST",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "registry_v7_4",
        "docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md",
        "5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433",
        "CURRENT_EVIDENCE_AUTHORITY",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "registry_v7_4_independent_audit",
        "docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_"
        "2026-09-26.md",
        "bf909363d726ecd2f55ce883a71e6a894e718587bbeb6946d879758f246c12ce",
        "EVIDENCE_INDEPENDENT_AUDIT_RECORD_NOT_SELF_ACCEPTANCE",
        "PASS",
    ),
    AuthorityPin(
        "registry_v7_4_acceptance_closure",
        "docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_"
        "2026-09-26.md",
        "4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977",
        "EVIDENCE_ACCEPTANCE_LIFECYCLE_CLOSURE",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "registry_v7_4_acceptance_manifest",
        "results/provenance/literature_evidence_registry_v7_4_acceptance_closure_"
        "2026-09-26/acceptance_manifest.json",
        "53074cfe44c0276d6f319497cbe6f5aaf07b255ac0c335f9481174dd968063fe",
        "EVIDENCE_ACCEPTANCE_MANIFEST",
        "CLOSED_ACCEPTED",
    ),
)

#: Formal names, for the record.  The ``_r2`` / Candidate-R1 suffixes are
#: repository provenance identity only.
FRAMEWORK_FORMAL_NAME = "Framework v7.4"
REGISTRY_FORMAL_NAME = "Registry v7.4"
REGISTRY_V7_4_ACCEPTANCE_COMMIT = "9050d0eabd0ee5c41626ba924c31a67f301c7293"


# ---------------------------------------------------------------------------
# C. / D.  Accepted governance authority chains
# ---------------------------------------------------------------------------

TASK_3_LAYER_A_PREREGISTRATION_R2: tuple[AuthorityPin, ...] = (
    AuthorityPin(
        "task_3_preregistration_candidate_r2",
        "docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_"
        "2026-09-27.md",
        "7957fbaf2566da612db1770fbbc8a08be18a6c7aaec4f4564b20fb4e5bad4ab4",
        "ACCEPTED_LAYER_A_ROBUSTNESS_PREREGISTRATION_CANDIDATE",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "task_3_preregistration_machine_record",
        "results/provenance/layer_a_robustness_preregistration_candidate_r2/"
        "preregistration_record.json",
        "14c2f0a2a1bd0cbc5ac022f14abcd24af8325976694ef4a6b3a133ade46d0b6f",
        "ACCEPTED_MACHINE_READABLE_PREREGISTRATION_RECORD",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "task_3_preregistration_acceptance_closure",
        "docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_"
        "acceptance_closure_2026-09-27.md",
        "d26ad46a08087d41831a8168d789294dcc635008ffb0f3aceb443121b5379b02",
        "PREREGISTRATION_ACCEPTANCE_LIFECYCLE_CLOSURE",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "task_3_preregistration_acceptance_manifest",
        "results/provenance/layer_a_robustness_preregistration_candidate_r2_"
        "acceptance_closure_2026-09-27/acceptance_manifest.json",
        "08a1e5b5929b5791e14b2ae887c4b9592dccbd803c7e0981c581f41561aa268d",
        "PREREGISTRATION_ACCEPTANCE_MANIFEST",
        "CLOSED_ACCEPTED",
    ),
)

TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_R2: tuple[AuthorityPin, ...] = (
    AuthorityPin(
        "governance_sequencing_successor_candidate_r2",
        "docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_"
        "successor_candidate_r2_2026-10-01.md",
        "db20ea059c48b99bb5c57801dff5654b4b8e1b94ce51ce4ded6e82eec4ac922e",
        "ACCEPTED_U_01_AND_MAIN_FULL81_ORDERING_SUCCESSOR",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "governance_sequencing_successor_acceptance_closure",
        "docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_"
        "successor_candidate_r2_acceptance_closure_2026-10-01.md",
        "9f1af8e805b23f6e16c827ada645bfff7d920d98a24b70fb2ea448683ec78851",
        "GOVERNANCE_SEQUENCING_ACCEPTANCE_LIFECYCLE_CLOSURE",
        "CLOSED_ACCEPTED_PUBLISHED",
    ),
    AuthorityPin(
        "governance_sequencing_successor_acceptance_manifest",
        "results/provenance/layer_a_robustness_preregistration_governance_sequencing_"
        "successor_candidate_r2_acceptance_closure_2026-10-01/acceptance_manifest.json",
        "4bbd58b8e8bd92c292d44b7b3d8b6a2035c3d41dc894581697f52583a55b6476",
        "GOVERNANCE_SEQUENCING_ACCEPTANCE_MANIFEST",
        "CLOSED_ACCEPTED_PUBLISHED",
    ),
    AuthorityPin(
        "governance_sequencing_successor_original_candidate",
        "docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_"
        "successor_candidate_2026-10-01.md",
        "f2bc1f5909ce4281d05465dba07541507194974d841df704fbf5a471f8b92d82",
        "IMMUTABLE_HISTORICAL_CANDIDATE_PROVENANCE_NOT_ACCEPTED",
        "IMMUTABLE_HISTORICAL_CANDIDATE_PROVENANCE",
    ),
)

#: Commit that published the accepted governance-sequencing successor R2 chain.
GOVERNANCE_SEQUENCING_SUCCESSOR_PUBLISHED_COMMIT = (
    "fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0"
)


# ---------------------------------------------------------------------------
# E. - I.  Implementation / input / runner authority
# ---------------------------------------------------------------------------

CANONICAL_PLANNING_INPUT = AuthorityPin(
    "canonical_planning_input",
    ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix(),
    ACCEPTED_ANNUAL_SHA256,
    "ACCEPTED_CANONICAL_ANNUAL_PLANNING_INPUT",
    "CLOSED_ACCEPTED",
)

IMPLEMENTATION_AUTHORITY_V7_4: tuple[AuthorityPin, ...] = (
    CANONICAL_PLANNING_INPUT,
    AuthorityPin(
        "model_core",
        "src/annual_design_model_v7_2.py",
        "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8",
        "ACCEPTED_SCIENTIFIC_IMPLEMENTATION_UNCHANGED",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "parameter_registry",
        "data/reference/parameter_registry_v7_2.csv",
        "c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1",
        "ACCEPTED_PARAMETER_REGISTRY",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "production_input_authority_v7_3",
        "src/production_input_authority_v7_3.py",
        "f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1",
        "INHERITED_ACCEPTED_INPUT_AUTHORITY_PRESERVED_UNMODIFIED",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "step2e1_routing_preflight",
        "scripts/21a_preflight_v7_3_production_routing.py",
        "3d99a4200dce93cd00db94727f72489d9be497eb52c74270a1c49b17fc8a7e95",
        "INHERITED_ACCEPTED_ROUTING_PREFLIGHT",
        "CLOSED_ACCEPTED",
    ),
    AuthorityPin(
        "provenance_protocol",
        "docs/protocols/"
        "Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md",
        "c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696",
        "ACCEPTED_VERSION_PROVENANCE_PROTOCOL",
        "CLOSED_ACCEPTED",
    ),
)

#: G. / H. / J.  Bytes carrying this alignment.  They are pinned exactly, so a
#: later edit to the successor stack, the Full81 runner, this bundle's verifier,
#: or its test fails the gate closed until the bundle is re-pinned in the same
#: audited correction.
ALIGNMENT_SURFACE_V7_4: tuple[AuthorityPin, ...] = (
    AuthorityPin(
        "production_successor_stack",
        "src/production_successor_stack_v7_3.py",
        "65728c40e8df746da92865e859072c345370ae93aa4a2b32a24b149c67a3dcda",
        "PRODUCTION_SUCCESSOR_STACK_V7_4_AUTHORITY_BOUND",
        "U_06_ALIGNMENT_CANDIDATE_R3",
    ),
    # N-04 re-pin. The Full81 runner was changed to REQUIRE the Main Full81
    # scope authorization on its no-solve path instead of merely reporting it.
    # This is the audited re-pin the pin contract above calls for: it restores
    # byte-identity verification for the successor implementation and nothing
    # else. It does NOT restore PRODUCTION_AUTHORITY_FROZEN, which is governed
    # by the accepted-lifecycle record of the current generation and resolves
    # ABSENT / NOT_FROZEN for these candidate bytes, and it does NOT authorize
    # Main Full81, which resolves NOT_GRANTED.
    #
    # Candidate R2 deliberately does NOT re-pin this entry. The R1 -> R2
    # iteration corrects publication/EOL compatibility and candidate ownership
    # only; it changed no byte of the Full81 runner, which is already LF and
    # carries forward from candidate R1 byte-identically. The ``lifecycle`` tag
    # therefore still names candidate R1, which is where these exact bytes
    # originate - the same convention under which other pins retain
    # ``U_06_ALIGNMENT_CANDIDATE_R3`` and
    # ``FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2``. Re-pinning an unchanged
    # file would be an unnecessary repin.
    AuthorityPin(
        "full81_runner",
        "scripts/21d_preflight_v7_3_final81_successor.py",
        "1a55c34897548a3595a9812dfeaa854f3b6b478594630c750931cd7cf2371bd1",
        "FULL81_PREFLIGHT_AND_DEPLOYMENT_GATED_ENTRY_POINT",
        "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1",
    ),
    AuthorityPin(
        "v7_4_alignment_verifier",
        "scripts/21e_preflight_v7_4_production_authority_alignment.py",
        "6b97be4258f0cccf3538a9078548951d0f4fc5d1ede7c43ae94cd26319568803",
        "V7_4_AUTHORITY_ALIGNMENT_NO_SOLVE_VERIFIER",
        "U_06_ALIGNMENT_CANDIDATE_R3",
    ),
    # N-04 re-pin: the overlay gained one additive AuthorityGeneration and
    # advanced CURRENT_GENERATION. No predecessor generation value changed.
    #
    # Candidate R2 re-pin. The overlay advanced the CURRENT generation's
    # candidate identity R1 -> R2 (same generation_id, same lineage_id, same
    # accepted-lifecycle slot), repointed that generation's candidate checkpoint
    # and manifest at the R2 artifacts, and barred candidate R1. That changes
    # overlay bytes, so the pin must follow or the gate fails closed. It does
    # NOT restore PRODUCTION_AUTHORITY_FROZEN and does NOT authorize Main Full81.
    #
    # Candidate R3 re-pin. The overlay advanced the CURRENT generation's
    # candidate identity R2 -> R3 (same generation_id, same lineage_id, same
    # accepted-lifecycle slot), repointed that generation's candidate checkpoint
    # and manifest at the R3 artifacts, barred candidate R2, declared the
    # R2-AUD-01 durable-publication requirements, and separated the active
    # candidate's audit state from the historical U-06 alignment audit history
    # (R2-AUD-03). That changes overlay bytes, so the pin must follow or the
    # gate fails closed. It does NOT restore PRODUCTION_AUTHORITY_FROZEN and
    # does NOT authorize Main Full81.
    #
    # Candidate R5 re-pin (R4-AUD-01). The overlay advanced the CURRENT
    # generation's candidate identity R4 -> R5, barred candidate R4, added the
    # R4 STOP preservation package, gave the live durable-publication report
    # real canonical comparisons, and added the closed-world candidate-manifest
    # identity contract enforced on the implementation-candidate role. That
    # changes overlay bytes, so the pin must follow or the gate fails closed.
    # It does NOT restore PRODUCTION_AUTHORITY_FROZEN and does NOT authorize
    # Main Full81.
    #
    # Candidate R6 re-pin (R5-AUD-01). Candidate identity R5 -> R6, R5 barred,
    # the R5 STOP package declared, candidate-manifest contract V2: checkpoint
    # identities verified as role-owned canonical claims, and a bound,
    # closed-world candidate change ledger. Not a freeze; not Full81.
    #
    # Candidate R7 re-pin (R6-AUD-01). Candidate identity R6 -> R7, R6 barred,
    # the R6 STOP package declared, candidate-manifest contract V3: no identity
    # accepted structurally in any mode; every identity bound to one
    # closed-world role with an independently established value (historical
    # roles via HISTORICAL_ROLE_IDENTITIES below). Not a freeze; not Full81.
    #
    # Candidate R8 re-pin (R7-AUD-01). Candidate identity R7 -> R8, R7 barred,
    # the R7 STOP package declared, candidate-manifest contract V4: every
    # historical role value and the predecessor change set are derived from
    # the EXTERNAL historical authority (Git-frozen pre-R8 trust root ->
    # accepted R7 binding -> authenticated R7 package) in every mode; the
    # bundle table is a diagnostic assertion only. Not a freeze; not Full81.
    #
    # Current Full81 Production Generation G1 re-pin. The overlay gained one
    # additive AuthorityGeneration (G1) and advanced CURRENT_GENERATION to it;
    # the accepted R8 generation and its contract V4 are retained byte-stable
    # as historical. G1 adds its own closed-world candidate-manifest contract
    # and change ledger, predeclared governance role paths, phase-aware
    # validation, and the three G1 identity axes. The ``lifecycle`` tag now
    # names the G1 candidate, where these exact bytes originate; it named R8
    # only while the pinned bytes were R8's. Not a freeze; not Full81.
    AuthorityPin(
        "u06_lifecycle_overlay",
        "src/production_authority_lifecycle_u06.py",
        "c65aaedc6ea4f357b4ac463ebe0428d717ed953c5e12dc2f547cc98334bd7c45",
        "U_06_ACCEPTED_LIFECYCLE_OVERLAY_NO_SCIENTIFIC_CONTENT",
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
    # Candidate R3 re-pin. One assertion in this suite required the ACTIVE
    # candidate's audit state to be the HISTORICAL U-06 alignment audit history
    # ("R1_FAILED_R2_NO_GO_R3_PENDING"), so the suite encoded blocker R2-AUD-03
    # instead of catching it. That assertion now requires the truthful active
    # state, and two bounded regression guards were added: one proving the
    # historical U-06 audit record cannot masquerade as the active candidate's
    # audit state, one proving the R2-AUD-01 durable-publication requirement is
    # declared. No production guard was weakened and no fail-closed assertion
    # was removed or relaxed.
    #
    # Candidate R5 re-pin (R4-AUD-01). The active-candidate assertion advanced
    # R4 -> R5 (a current pointer), Candidate R4 gained an explicit historical
    # rejected-candidate assertion, and the live durable-publication report is
    # now asserted never to equate presence with content. Every R1-R3
    # historical assertion is retained unchanged; nothing was relaxed.
    #
    # Candidate R6 re-pin. Active-candidate pointer R5 -> R6, an explicit
    # historical R5 rejection assertion, and the live report's change-ledger
    # comparison asserted. No assertion removed or relaxed.
    #
    # Candidate R7 re-pin. Active-candidate pointer R6 -> R7 and an explicit
    # historical R6 rejection assertion. No assertion removed or relaxed.
    #
    # Candidate R8 re-pin. Active-candidate pointer R7 -> R8 and an explicit
    # historical R7 rejection assertion. No assertion removed or relaxed.
    #
    # G1 re-pin. Current-generation assertions advanced R8 -> G1 and are
    # phase-aware (read from primary state, never hard-coded pre-acceptance);
    # R8 is asserted as the accepted, superseded historical predecessor.
    AuthorityPin(
        "u06_lifecycle_test",
        "tests/test_21f_u06_accepted_lifecycle_gate.py",
        "e21b734db9da2a816e7181c93c5246d452ef58a2b9212d568b5d93c17ddf6c31",
        "U_06_LIFECYCLE_GATE_STATIC_TEST_F_01_REGRESSION",
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
    # Candidate R4 re-pin (R3-AUD-04). This A-01 suite was written when U-06 R3
    # was the CURRENT generation and still drove the validator with a U-06 R3
    # payload. U-06 R3 has since been lawfully accepted, frozen, published and
    # superseded, so replaying the attack against it stopped at
    # U06_IMPLEMENTATION_IDENTITY_DRIFT before reaching the role-authenticity
    # layer the attack exists to test: still rejected, but no longer proving
    # what it claims. The attack is now aimed at the CURRENT generation, whose
    # candidate manifest declares the live implementation digest, and the U-06
    # R3 cases are retained as explicitly historical controls. No negative
    # control was deleted and no guard was weakened.
    #
    # G1 re-pin. The attacks are aimed at the G1 generation: structural
    # substitution attacks run against the predeclared G1 role paths, and
    # authenticity attacks run in a disposable G1 repository. Every attack
    # case is retained; no negative control was deleted or relaxed.
    AuthorityPin(
        "u06_r3_substitution_attack_test",
        "tests/test_21g_u06_r3_substitution_attacks.py",
        "ffb4c5ead017f29e5822ae5f2045f72e9dffcf8e2e5be7080dc174ee898c569b",
        "U_06_R3_ARBITRARY_ARTIFACT_SUBSTITUTION_ATTACK_SUITE",
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
    AuthorityPin(
        "v7_4_alignment_test",
        "tests/test_21e_v7_4_production_authority_bundle.py",
        "0ba258c1a63df33c88f7499bbac7b353eb926aa1b7fb79cfd10fb9e4181bb7a6",
        "V7_4_AUTHORITY_ALIGNMENT_STATIC_TEST",
        # Candidate R4 re-pin (R2-AUD-03 / R3-AUD-04). One assertion here
        # required the pre-acceptance U-06 register entry to be
        # "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT", the
        # ownership string of the HISTORICAL U-06 alignment generation. The
        # suite therefore REQUIRED blocker R2-AUD-03 instead of catching it.
        # It now requires the candidate-neutral entry, asserts the historical
        # string is never emitted as the active one, and additionally checks
        # the explicit ownership fields. No assertion was removed or relaxed.
        #
        # G1 re-pin. Live-state assertions are phase-aware: the lifecycle,
        # register, ownership and Full81 states are read from primary state
        # (absent slot -> most restrictive state; present slot -> a valid
        # accepted record is required). No assertion was removed or relaxed.
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
    AuthorityPin(
        "main_full81_authorization_mechanism",
        "src/main_full81_authorization_v7_4.py",
        # N-04 re-pin: successor-compatibility advance of the lawful record
        # path, the authorized runner version, and the mechanism identity, so a
        # FUTURE authorization can target the successor implementation without
        # overwriting the published R2 authorization. No authorization artifact
        # was created and none is authorized by this change.
        #
        # Candidate R2 re-pin. CANDIDATE_ID advanced R1 -> R2 and candidate R1
        # was added to SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM. LINEAGE_ID, the
        # lawful record path and the authorization schema version are unchanged.
        # The lawful record path remains deliberately empty: no authorization
        # artifact exists, and none is authorized by this change.
        #
        # Candidate R3 re-pin. CANDIDATE_ID advanced R2 -> R3 and candidate R2
        # was added to REJECTED_CANDIDATE_IDS, because candidate R2's fresh
        # independent audit returned FAIL / NO-GO. LINEAGE_ID, the lawful record
        # path and the authorization schema version are unchanged. The lawful
        # record path remains deliberately empty: no authorization artifact
        # exists, and none is authorized by this change.
        #
        # Candidate R4 re-pin. Candidate R3's own fresh independent audit
        # returned FAIL / NO-GO, so R3 was added to REJECTED_CANDIDATE_IDS on
        # exactly the footing R2 already had. Without that addition a future
        # authorization could have named a candidate whose audit failed.
        # LINEAGE_ID, the lawful record path and the authorization schema
        # version are unchanged. The lawful record path remains deliberately
        # empty: no authorization artifact exists, and none is authorized by
        # this change.
        #
        # Candidate R5 re-pin. Candidate R4's own fresh independent audit
        # returned FAIL / NO-GO on R4-AUD-01, so R4 was added to
        # REJECTED_CANDIDATE_IDS and CANDIDATE_ID advanced R4 -> R5. LINEAGE_ID,
        # the lawful record path, the authorization schema version, the N-04 /
        # N-05 guard semantics and every execution-authorization rule are
        # unchanged. No authorization artifact exists or is authorized.
        #
        # Candidate R6 re-pin. CANDIDATE_ID R5 -> R6 and R5 added to
        # REJECTED_CANDIDATE_IDS; nothing else changed.
        #
        # Candidate R7 re-pin. CANDIDATE_ID R6 -> R7 and R6 added to
        # REJECTED_CANDIDATE_IDS; nothing else changed.
        #
        # Candidate R8 re-pin. CANDIDATE_ID R7 -> R8 and R7 added to
        # REJECTED_CANDIDATE_IDS; nothing else changed.
        #
        # G1 re-pin. Lineage and candidate advanced to G1, with the accepted R8
        # candidate and the r3 authorization slot superseded; a G1 scope-
        # authorization slot and a separate, fail-closed execution-
        # authorization MECHANISM were added. No authorization artifact exists
        # or is created by this change: scope and execution both resolve
        # NOT_GRANTED, and a mechanism is not an authorization.
        "0b4899412bc5cd6d6a4b64a45a243ae8b98d2488ea9ac165f595d2cd7eec7880",
        "MAIN_FULL81_AUTHORIZATION_MECHANISM_NO_SCIENTIFIC_CONTENT",
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
    # Candidate R3 re-pin. Pin 34 (`repository_eol_policy`) made `.gitattributes`
    # a required authority file, and this suite's isolated promotion fixture is a
    # miniature repository reconstruction. The fixture did not copy it, so the
    # bundle correctly reported a missing required authority file and every
    # positive control resolved NOT_GRANTED. The fixture now derives its
    # authority-file set from `REQUIRED_DURABLE_PUBLICATION_PATHS`, so it cannot
    # silently fall behind a future pin. The guard was not weakened: it fired
    # correctly, and the fixture was completed to match it.
    AuthorityPin(
        "main_full81_authorization_test",
        "tests/test_21h_main_full81_authorization_mechanism.py",
        "5b0be95a279ad092eafe6118556590d0c765ad269df15e2454795f9109744b9a",
        "MAIN_FULL81_AUTHORIZATION_MECHANISM_FAIL_CLOSED_SUITE",
        # Candidate R4 re-pin (R3-AUD-04). Three assertions encoded
        # predecessor-generation premises: two reached a specific HISTORICAL
        # generation through `CURRENT_GENERATION` rather than selecting it by
        # id, and one tested "no hard-coded commit" by counting 40-hex tokens
        # in the whole source file, so a commit hash cited in a provenance
        # comment failed it although nothing had become hard-coded. All three
        # now assert the real invariant: historical generations are selected
        # explicitly by id, the current generation is derived from primary
        # contracts, and the module is parsed so that only 40-hex literals
        # reachable by EXECUTABLE code are constrained. Strictly stronger.
        #
        # Candidate R5 re-pin (R4-AUD-01). The current-generation assertion
        # advanced R4 -> R5 and now also requires the candidate-manifest
        # contract; Candidate R4 is asserted on every rejection list; and new
        # promotion-fixture controls prove the manifest is bound only from
        # OUTSIDE itself and that post-binding byte changes never freeze. No
        # negative control was deleted or relaxed.
        #
        # Candidate R6 re-pin. Current-generation assertion R5 -> R6 (contract
        # V2, change ledger) and R5 asserted on every rejection list.
        #
        # Candidate R7 re-pin. Current-generation assertion R6 -> R7 (contract
        # V3), R6 asserted on every rejection list, and the GATE positive
        # control no longer REQUIRES a structural identity class - it had
        # encoded R6-AUD-01 as expected behaviour. Strictly stronger.
        #
        # Candidate R8 re-pin. Current-generation assertion R7 -> R8 (contract
        # V4, V3 asserted superseded) and R7 asserted on every rejection list.
        # No assertion removed or relaxed.
        #
        # G1 re-pin. The promotion fixture synthesizes a G1 candidate package
        # with its role records at the predeclared G1 paths; contract V4 is
        # retained as a historical control on R8. No negative control was
        # deleted or relaxed.
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
)

#: K.  Repository governance authority.
#:
#: Candidate R3 remediation of independent-audit blocker ``R2-AUD-02`` (MAJOR /
#: BLOCKING).  The repository runs ``core.autocrlf=true`` and, through Candidate
#: R2, carried no ``.gitattributes``.  A clean checkout therefore smudged every
#: authority-critical LF text file to CRLF, which changed its raw SHA-256 and
#: destroyed the canonical implementation identity -- so no third party could
#: reconstruct the accepted bytes from published Git content alone.
#:
#: ``.gitattributes`` now fixes the checkout form of every authority-critical
#: path explicitly.  That makes it a *reproducibility precondition of the
#: production-authority route*, not a convenience file: edit it and the raw bytes
#: that every other pin and the implementation digest are computed over can
#: change underneath them.  An unbound file with that power is exactly the kind
#: of silent authority surface this bundle exists to forbid, so it is pinned.
#:
#: Deliberate separation of concerns:
#:
#: * the 21-path *implementation identity* remains the runtime / gate-protected
#:   implementation universe and is NOT expanded to 22 -- ``.gitattributes`` is
#:   not imported, loaded, or executed on any production path;
#: * ``.gitattributes`` is bound here as *governance/authority identity*.
#:
#: Because this bundle's own source now carries the pin, the bundle's SHA-256
#: changes, and the bundle is one of the 21 implementation paths -- so the
#: implementation digest advances as a natural consequence.  That is expected.
#:
#: This pin is identity only.  It is not an acceptance, not an audit outcome,
#: not a freeze, and not Main Full81 authorization.
#: Candidate R4 re-pin.  Declaring this pin was necessary but was not
#: sufficient: the Candidate R3 verifier never actually verified the group it
#: sits in (``R3-AUD-03``, CRITICAL), so deleting ``.gitattributes`` outright
#: still returned ``PASS``.  The verifier now traverses :data:`PIN_GROUPS` and
#: enforces declared-versus-verified set equality, which is what makes this pin
#: fail closed.  The policy's own coverage advanced from a hand-maintained list
#: to the complete raw-byte consumer universe derived from primary source
#: (``R3-AUD-02``), so its bytes - and therefore this digest - advance with it.
#: Candidate R5 re-pin (R4-AUD-01).  The derived raw-byte consumer universe
#: gained exactly five consumers - the Candidate R5 checkpoint and manifest and
#: the three files of the Candidate R4 STOP preservation package - and the
#: policy gained exactly the five matching exact-path rules.  No rule was
#: removed or broadened.
#: Candidate R6 re-pin: exactly six more consumers (R6 checkpoint, manifest and
#: change ledger; R5 STOP package) and exactly six matching exact-path rules.
#: Candidate R7 re-pin: exactly six more consumers (R7 checkpoint, manifest and
#: change ledger; R6 STOP package) and exactly six matching exact-path rules.
#: Candidate R8 re-pin: exactly nine more consumers (R8 checkpoint, manifest and
#: change ledger; R7 STOP package; the Git-frozen pre-R8 trust root and the R7
#: binding it selects, which contract V4 reads by raw bytes; the R8 attack
#: suite) and exactly nine matching exact-path rules.  No rule was removed or
#: broadened.
#: G1 re-pin: exactly seventeen more consumers (124 -> 141) and exactly
#: seventeen matching exact-path rules: the G1 candidate checkpoint, manifest
#: and change ledger; the five predeclared G1 governance role records; the G1
#: scope-authorization, execution-authorization and no-solve-evidence slots
#: (the evidence slot byte-preserving, the others LF-pinned); the four role
#: records the accepted R8 lifecycle record names; and the G1 and FULLSTACK-01
#: suites.  No rule was removed or broadened.
REPOSITORY_GOVERNANCE_AUTHORITY_V7_4: tuple[AuthorityPin, ...] = (
    AuthorityPin(
        "repository_eol_policy",
        ".gitattributes",
        "0dc5e0700c4375ad2a3ad8da1d149c5e7806722c983c85904ce1d7e944685ddc",
        "REPOSITORY_EOL_CHECKOUT_POLICY_REPRODUCIBILITY_PRECONDITION",
        "CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1",
    ),
)

#: The V7.3 methodology/evidence/lifecycle trio still pinned by the unmodified
#: ``src/production_input_authority_v7_3.py``.  Retained and verified here as
#: historical provenance so that a destructive rewrite of the historical layer is
#: detected rather than silently absorbed.
INHERITED_V7_3_HISTORICAL_AUTHORITY: tuple[AuthorityPin, ...] = tuple(
    AuthorityPin(
        f"v7_3_{label}",
        relative.as_posix(),
        expected,
        "HISTORICAL_ACCEPTED_PREDECESSOR_AUTHORITY_NOT_CURRENT_PRESCRIPTIVE",
        "CLOSED_ACCEPTED_HISTORICAL",
    )
    for label, (relative, expected) in V7_3_AUTHORITY_FILES.items()
)


# ---------------------------------------------------------------------------
# R3-AUD-03: ONE declared pin universe, verified exactly once
# ---------------------------------------------------------------------------
#
# Candidate R3 received ``FAIL / NO-GO`` on ``R3-AUD-03`` (CRITICAL /
# BLOCKING).  ``all_pins()`` was a hand-written sum of seven group constants
# while :func:`verify_v7_4_authority_bundle` was a hand-written sequence of six
# ``_verify_pins`` calls.  The two lists were maintained independently, the
# ``REPOSITORY_GOVERNANCE_AUTHORITY_V7_4`` group was added to the first and not
# the second, and ``verified_pin_count`` was populated from ``len(all_pins())``.
# The verifier therefore reported 34 verified pins while verifying 33, and
# deleting ``.gitattributes`` entirely still returned ``PASS``.
#
# The remedy is to delete the second list rather than to repair it.
# :data:`PIN_GROUPS` is now the single declaration; ``all_pins()`` is derived
# from it, and the verifier TRAVERSES it.  A new group is therefore verified
# the moment it is declared, with no second edit that could be forgotten.
#
# Deriving both sides from one object makes agreement structural, not
# incidental - but a fail-open defect of this class must not be defended by
# structure alone.  :func:`declared_pin_inventory` independently re-derives the
# declared set, and the verifier mechanically compares DECLARED to VERIFIED and
# fails closed on any asymmetry, duplicate label, duplicate path, missing file
# or SHA mismatch.  ``verified_pin_count`` is the count of pins this run
# actually hashed, and is emitted only once that comparison has passed.
PIN_GROUPS: Mapping[str, tuple[AuthorityPin, ...]] = {
    "methodology_evidence_authority": METHODOLOGY_EVIDENCE_AUTHORITY_V7_4,
    "task_3_authority": TASK_3_LAYER_A_PREREGISTRATION_R2,
    "governance_sequencing_successor": TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_R2,
    "implementation_authority": IMPLEMENTATION_AUTHORITY_V7_4,
    "alignment_surface": ALIGNMENT_SURFACE_V7_4,
    "repository_governance_authority": REPOSITORY_GOVERNANCE_AUTHORITY_V7_4,
    "inherited_v7_3_historical_authority": INHERITED_V7_3_HISTORICAL_AUTHORITY,
}


def all_pins() -> tuple[AuthorityPin, ...]:
    """Every pin this bundle verifies, in stable declaration order.

    Derived from :data:`PIN_GROUPS`, which is also what the verifier
    traverses, so a declared group can never go unverified.
    """

    return tuple(pin for group in PIN_GROUPS.values() for pin in group)


def declared_pin_inventory() -> dict[str, Any]:
    """Independently re-derive the declared pin universe and its integrity.

    Deliberately does NOT call :func:`all_pins`: it walks :data:`PIN_GROUPS`
    itself, so the inventory is a second reading of the declaration rather than
    a restatement of the first.  Reports duplicate labels and duplicate paths,
    either of which would make a "verified once" claim unsound.
    """

    labels: list[str] = []
    paths: list[str] = []
    by_group: dict[str, list[str]] = {}
    for group_name, group in PIN_GROUPS.items():
        by_group[group_name] = [pin.label for pin in group]
        for pin in group:
            labels.append(pin.label)
            paths.append(pin.relative_path)

    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})
    duplicate_paths = sorted({path for path in paths if paths.count(path) > 1})
    return {
        "group_count": len(PIN_GROUPS),
        "group_names": list(PIN_GROUPS),
        "labels_by_group": by_group,
        "declared_labels": sorted(labels),
        "declared_label_count": len(labels),
        "declared_unique_label_count": len(set(labels)),
        "duplicate_labels": duplicate_labels,
        "duplicate_paths": duplicate_paths,
        "integrity_ok": not duplicate_labels and not duplicate_paths,
    }


# ---------------------------------------------------------------------------
# R6-AUD-01: pinned HISTORICAL ROLE IDENTITIES (not bundle pins)
# ---------------------------------------------------------------------------
#
# Candidate R6 received ``FAIL / NO-GO`` on ``R6-AUD-01`` (CRITICAL): the
# production GATE accepted predecessor preservation-package and predecessor-
# evidence identities STRUCTURALLY, because their files are ignored and
# unpublished, so a clean checkout has no bytes to verify them against.  Two
# individually lawful digests swapped between roles therefore passed.
#
# Each such identity now has ONE closed-world semantic role, and that role's
# authoritative value is pinned here, in the module whose job is to hold exact
# hashes.  The lifecycle overlay's candidate-manifest contract (V3) binds every
# historical identity to exactly this value in EVERY mode, and in
# ``CANDIDATE_PACKAGE`` mode additionally proves each value against the
# immutable preserved bytes (or the predecessor's immutable raw-byte index) it
# describes.  Because this module is inside the accepted implementation
# identity, changing any value here is implementation drift.
#
# Deliberate separation: these are NOT authority-bundle pins.  They are not in
# :data:`PIN_GROUPS`, are not counted by :func:`all_pins` (still 7 groups / 34
# pins), and are not verified by :func:`verify_v7_4_authority_bundle`, because
# their targets are unpublished historical provenance rather than production
# authority.  Role names are closed-world: the overlay rejects an unknown role,
# a role pinned twice, a role whose path is not the path its name requires, and
# a required role left unpinned (``historical_role_identities``).
#
# Roles:
#   preservation:<candidate>:archive|index|stop_record  - every declared STOP
#       preservation package (Candidates R1-R6);
#   predecessor:implementation_digest|checkpoint|manifest|repository_eol_policy
#       - the immediate predecessor, Candidate R6;
#   predecessor:modified_file:<path> - the R6 bytes of every path Candidate R7
#       modifies (the closed predecessor change set its ledger must list).
#
# ---------------------------------------------------------------------------
# R7-AUD-01: the table above is DIAGNOSTIC ONLY (Candidate R8, contract V4)
# ---------------------------------------------------------------------------
#
# Candidate R7 received ``FAIL / NO-GO`` on ``R7-AUD-01`` (CRITICAL): this
# table is candidate-controlled source, and the implementation identity that
# covers it is recomputable, so a recomputing author rewrote it together with
# the manifest, ledger and checkpoint and restored GATE PASS with lawful
# historical digests assigned to the wrong roles.  Pinning historical truth
# HERE was the defect.
#
# Under contract V4 the lifecycle overlay derives every historical role value
# from EXTERNAL evidence instead: the Git-frozen pre-R8 historical trust root
# below -> the accepted R7 Preservation Authority Binding that trust root pins
# -> the authenticated R7 preservation package.  The table that follows is kept
# only as a DIAGNOSTIC ASSERTION of that derivation: the overlay requires it to
# be exactly equal, never reads a value from it, and never falls back to it.
# Rewriting it can only make the GATE fail.
#
# Roles asserted (Candidate R8):
#   preservation:<candidate>:archive|index|stop_record - Candidates R1-R7;
#   predecessor:implementation_digest|checkpoint|manifest|repository_eol_policy
#       - the immediate predecessor, Candidate R7;
#   predecessor:modified_file:<path> - the R7 bytes of every path of R7's
#       preserved surface that Candidate R8 changes.
#
# Current Full81 Production Generation G1: the trust root and table below are
# HISTORICAL R8 provenance, read only when the accepted R8 candidate is
# re-validated under contract V4.  The G1 candidate-manifest contract and
# change ledger never consult them; G1 binds its predecessor through published
# Git evidence (the predecessor commit, the accepted R8 lifecycle record and
# the superseded R8 scope authorization), so nothing here is a live G1 role and
# nothing here may be edited for G1.


@dataclass(frozen=True)
class FrozenGitAuthority:
    """The externally frozen Git identity of one pre-R8 governance artifact."""

    tag_ref: str
    tag_object: str
    commit: str
    path: str
    blob: str
    raw_sha256: str
    byte_count: int


#: The pre-R8 historical trust root, as frozen by its independently audited Git
#: freeze gate BEFORE Candidate R8 existed: annotated tag, peeled commit,
#: tracked path, blob, raw bytes.  Candidate R8 CONSUMES this identity; it does
#: not choose it.  Every value is independently checkable against the published
#: remote tag, and the overlay
#: (:func:`~src.production_authority_lifecycle_u06.authenticate_pre_r8_trust_root`)
#: verifies it through live Git objects - ref -> annotated tag object -> commit
#: -> blob, published ancestry - and reads the trust root from the Git blob.  The
#: R7 binding locator and SHA-256 are read FROM that blob; they are deliberately
#: not restated anywhere in candidate source.
PRE_R8_HISTORICAL_TRUST_ROOT = FrozenGitAuthority(
    tag_ref="refs/tags/v7.4-main-full81-pre-r8-historical-trust-root-accepted-2026-10-06",
    tag_object="6b31fef7c84bd0646a7171cf8168564ee969b10f",
    commit="c8f3665d5c67e0cae3222073cd71b9a6231279b1",
    path="docs/checkpoints/main_full81_preflight_pre_r8_historical_trust_root_2026-10-06.json",
    blob="d10707b922004f3084ae6045fe3f1b1caf6eaea4",
    raw_sha256="889964f9574ce4d90e6919b29c2425fe60ccf30b5b20bbcfb553fb3f9d8d2fb5",
    byte_count=5496,
)


@dataclass(frozen=True)
class HistoricalRoleIdentity:
    """One DIAGNOSTIC assertion of an externally derived historical role value."""

    role: str
    relative_path: str | None
    sha256: str


HISTORICAL_ROLE_IDENTITIES: tuple[HistoricalRoleIdentity, ...] = (
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r1_publication_stop_2026-10-04/candidate_r1_raw_bytes.zip",
        "45ff1028fab900f13e0eede29abae56d9c06834e9605bda51b2bfd11f2827f6f",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r1_publication_stop_2026-10-04/candidate_r1_raw_byte_index.json",
        "720fafade81b1cb8c0f22ddc0600611bfe5bad6f8e320270542bfaae2ba9f579",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r1_publication_stop_2026-10-04/publication_stop_record.json",
        "c8400b6da1bffe8ad1ca7c919569b9980024f7d459ed7f890a472f9a24e99911",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r2_audit_stop_2026-10-04/candidate_r2_raw_bytes.zip",
        "308646c16731a3695e340c48c53d5ce51f1af078e2729cdc43a0692eec3d3743",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r2_audit_stop_2026-10-04/candidate_r2_raw_byte_index.json",
        "beaf1e53d25064ec22af5b6aa632fcd9bcbb310facd0a260cd34efe3978eed27",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r2_audit_stop_2026-10-04/independent_audit_stop_record.json",
        "5cddedbec20d194d17de64d6d9a0977898b310fee496c44e12c9edf0f19f0840",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r3_audit_stop_2026-10-05/candidate_r3_raw_bytes.zip",
        "6f616f748cd2d51f140707bffe99055741ecd413c9bd9706c50f6b381738918b",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r3_audit_stop_2026-10-05/candidate_r3_raw_byte_index.json",
        "8209d12ec5a995780fcf4aa106e3ac5ae8b1617944c720b2a37c4fa921e11a17",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r3_audit_stop_2026-10-05/independent_audit_stop_record.json",
        "e66512336a3612994b6f9da6b379f915f0014bf114c200861f45b2d6a5093b02",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r4_audit_stop_2026-10-05/candidate_r4_raw_bytes.zip",
        "aecfb8f6b99b0a730205ee4ff958a2e2e52df34dd682bf4bec1813fa7f87cd3f",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r4_audit_stop_2026-10-05/candidate_r4_raw_byte_index.json",
        "cc1c52ae6130987798fa5e29064bc73f60042c219216a02b25ef00000ec96121",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r4_audit_stop_2026-10-05/independent_audit_stop_record.json",
        "2385666eb1c2b7206e620780da12a1490ed93239f363ea97075b990cb3054c75",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r5_audit_stop_2026-10-05/candidate_r5_raw_bytes.zip",
        "f956f85aa8b163501e5310b674c428bc647c29b8e8ebfd15782a098d0510048e",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r5_audit_stop_2026-10-05/candidate_r5_raw_byte_index.json",
        "ec2a1457715b300a4ef3406f5cdd4aa1c074b9c765d96c726a9e06618cff4420",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r5_audit_stop_2026-10-05/independent_audit_stop_record.json",
        "4ac15dde83bfc1ed7c76a21f04efe0d1da68426a645d7c7151481c5dc61c7385",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r6_audit_stop_2026-10-05/candidate_r6_raw_bytes.zip",
        "03559218fcc6e028f631ba00d311dfa9d0612f0494512fab63c8ee47376e1ce7",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r6_audit_stop_2026-10-05/candidate_r6_raw_byte_index.json",
        "ab7df3b8bed4d21286ff1bff202777a53a908acb94ce6a4b62a7318d2d5efd29",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r6_audit_stop_2026-10-05/independent_audit_stop_record.json",
        "5abe9ddcabcc514cb9118b7909d9834d636fdbec471da2c25745cfcf48ef6b70",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7:archive",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r7_audit_stop_2026-10-06/candidate_r7_raw_bytes.zip",
        "5b9042a59f43852c0c9c19b37df2c10cdd7588952df2bd5eecaaf7c46af8a4ae",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7:index",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r7_audit_stop_2026-10-06/candidate_r7_raw_byte_index.json",
        "ebf2b1ad3185e78e918e86dd67420ace44be5ccc387ea142a5e85d468884b225",
    ),
    HistoricalRoleIdentity(
        "preservation:MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7:stop_record",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r7_audit_stop_2026-10-06/independent_audit_stop_record.json",
        "4f48982132784aec932e0100202f16db5bb45544934adfb382127f23e0cc8066",
    ),
    HistoricalRoleIdentity(
        "predecessor:implementation_digest",
        None,
        "cb78b3ac0c5bcee793757f0de7a3684f248b70abac1226e5b263f11fa6690b5c",
    ),
    HistoricalRoleIdentity(
        "predecessor:checkpoint",
        "docs/checkpoints/main_full81_preflight_authorization_guard_candidate_r7_2026-10-06.md",
        "cff4273fc9cb1080dc3f4fb7d9060febc002262ac81ee4fb69e76e83ebdf150c",
    ),
    HistoricalRoleIdentity(
        "predecessor:manifest",
        "results/provenance/main_full81_preflight_authorization_guard_candidate_r7_2026-10-06/preflight_authorization_guard_manifest.json",
        "3d9a27f08ad60c9d08971e6fc652f7cdd31fa5dd89ef52057a51918de5bdeb6f",
    ),
    HistoricalRoleIdentity(
        "predecessor:repository_eol_policy",
        ".gitattributes",
        "27187c9be7cfd2d2ab1fd39f4f0d94a48e63d81d9fa3f327996def6fb798a3aa",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:.gitattributes",
        ".gitattributes",
        "27187c9be7cfd2d2ab1fd39f4f0d94a48e63d81d9fa3f327996def6fb798a3aa",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:src/main_full81_authorization_v7_4.py",
        "src/main_full81_authorization_v7_4.py",
        "8dc2fb506f7506d7e2e864b17a9fca1a7fc329679db45c7566a6277ae0eeb35a",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:src/production_authority_bundle_v7_4.py",
        "src/production_authority_bundle_v7_4.py",
        "50c680cf39d8383caf2ca81ef1b929b4920b93b6c81edba273fa42bc00178aa4",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:src/production_authority_lifecycle_u06.py",
        "src/production_authority_lifecycle_u06.py",
        "ee81109c8414753fef1d0dae24d3a598bf43f8d1a8f9bf769b2318614705865b",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:tests/test_21f_u06_accepted_lifecycle_gate.py",
        "tests/test_21f_u06_accepted_lifecycle_gate.py",
        "619c45a977800bf8b495788f89df7430aa4aad1eaef22bd2338c86a28ea3e774",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:tests/test_21h_main_full81_authorization_mechanism.py",
        "tests/test_21h_main_full81_authorization_mechanism.py",
        "8b944b6982891c75ef3f3768451c1ba91e6bcbaca8a2f2c27a0d0abe7558553d",
    ),
    HistoricalRoleIdentity(
        "predecessor:modified_file:tests/test_21j_authority_raw_byte_eol_coverage.py",
        "tests/test_21j_authority_raw_byte_eol_coverage.py",
        "49940a21cf281dba2e8fe07955373d7b6970faf810699fbdfbb80d147922bc11",
    ),
)


# ---------------------------------------------------------------------------
# Governance semantics encoded by this bundle
# ---------------------------------------------------------------------------

#: Events that still require U-01 to be resolved, independently audited,
#: accepted, and frozen first.  ``FULL81_AUTHORIZATION`` is deliberately absent,
#: per the accepted governance-sequencing successor R2 closure §7.2.
U_01_MUST_BE_FROZEN_BEFORE = (
    "A2_EXECUTION",
    "A2_RESULT_EXPOSURE",
    "A2_INTERPRETATION",
    "A2_CONDITIONAL_EXTENSION_AUTHORIZATION",
)

U_01_DOES_NOT_BLOCK = (
    "MAIN_FULL81_AUTHORIZATION",
    "MAIN_FULL81_EXECUTION",
    "MAIN_FULL81_INTEGRITY_INSPECTION",
    "MAIN_FULL81_SCIENTIFIC_INSPECTION",
    "MAIN_FULL81_RESPONSE_SURFACE_ANALYSIS",
    "SUPERVISOR_DISCUSSION_OF_MAIN_FULL81",
)

#: U-items whose state is a fixed governance fact of the accepted authorities.
#: ``U-06`` is deliberately absent: its state is lifecycle-dependent and is read
#: from the resolved overlay, never from a constant here (audit finding F-01,
#: second part).
STATIC_UNRESOLVED_REGISTER = {
    "U-01": "OPEN_HOLD",
    "U-02": "UNRESOLVED",
    "U-03": "UNRESOLVED",
    "U-04": "UNRESOLVED",
    "U-05": "UNRESOLVED",
    "U-07": "UNRESOLVED_CLASSIFICATION",
}


#: R2-AUD-03 remediation.  The pre-acceptance register entry is now
#: candidate-NEUTRAL.  The string it replaces,
#: ``V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT``, names the
#: HISTORICAL U-06 V7.4 *alignment* candidate, and reporting it as the
#: ownership of the active Main Full81 preflight-authorization-guard candidate
#: was the defect.  This value names no generation and no candidate at all, so
#: it cannot misattribute one to another; who the entry is ABOUT is carried in
#: the explicit fields of :func:`u06_register_state` instead of being smuggled
#: inside a status string.
ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY = (
    "ACTIVE_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT"
)

#: The historical string, retained ONLY so the substitution tests can prove it
#: is never emitted as the active entry.  It is not used to derive any state.
HISTORICAL_U06_ALIGNMENT_REGISTER_ENTRY = (
    "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT"
)


def u06_register_entry(lifecycle: Mapping[str, Any] | None) -> str:
    """Derive the ``U-06`` register entry from lifecycle state, not a constant.

    Before acceptance this reads as a candidate-neutral "pending fresh
    independent audit"; after a lawful acceptance the same code reads as
    accepted/frozen, with no edit here and no rewriting of any historical
    artifact.

    Candidate R3 remediation of independent-audit blocker ``R2-AUD-03`` (MAJOR
    / BLOCKING) corrected most audit fields but left this function returning
    the historical U-06 *alignment* ownership string for the current
    preflight-authorization-guard generation.  The pre-acceptance return value
    is now candidate-neutral, and
    :func:`u06_register_state` carries generation, lineage, candidate id and
    candidate audit status as separate explicit fields.
    """

    summary = lifecycle_summary(lifecycle)
    acceptance = summary["u06_acceptance_status"]
    freeze = summary["production_authority_freeze_status"]
    if acceptance == "CLOSED_ACCEPTED" and freeze == "FROZEN":
        return "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_FROZEN"
    if acceptance == "CLOSED_ACCEPTED":
        return "CLOSED_ACCEPTED_PRODUCTION_AUTHORITY_NOT_YET_FROZEN"
    if summary["u06_independent_audit_status"] == "PASS":
        return "INDEPENDENT_AUDIT_PASS_PENDING_ACCEPTANCE"
    return ACTIVE_CANDIDATE_PENDING_AUDIT_REGISTER_ENTRY


def u06_register_state(lifecycle: Mapping[str, Any] | None) -> dict[str, Any]:
    """The ``U-06`` register entry WITH explicit ownership, never implied.

    ``R2-AUD-03`` was possible because one status string had to carry both
    "what state is this in?" and "whose state is it?".  Those are separated
    here: ``entry`` is the state, and generation / lineage / candidate id /
    candidate audit status say who it belongs to.  Every field is read from the
    CURRENT generation through the resolved lifecycle, so a historical record
    can never supply them.
    """

    summary = lifecycle_summary(lifecycle)
    return {
        "entry": u06_register_entry(lifecycle),
        "entry_is_candidate_neutral": True,
        "generation_id": summary["current_generation_id"],
        "lineage_id": summary["current_generation_lineage_id"],
        "candidate_id": summary["active_candidate_id"],
        "candidate_audit_status": summary["u06_independent_audit_status"],
        "candidate_audit_status_scope": (
            summary["u06_independent_audit_status_scope"]
        ),
        "candidate_audit_status_candidate_id": summary["active_candidate_id"],
        "historical_u06_alignment_audit_status": (
            summary["historical_u06_alignment_audit_status"]
        ),
        "historical_u06_alignment_is_current": False,
        "historical_u06_alignment_register_entry": (
            HISTORICAL_U06_ALIGNMENT_REGISTER_ENTRY
        ),
        "historical_u06_alignment_register_entry_is_current": False,
        "ownership_note": (
            "entry describes the state of candidate_id in generation_id and of "
            "nothing else. The historical U-06 alignment fields are retained "
            "for provenance and are never the active candidate's state; "
            "reporting them as such was blocker R2-AUD-03."
        ),
    }

#: U-07 is an A2-only classification question and is not a Main Full81 blocker.
#: No variable-floor support is implemented and no reserve-floor equation accepts
#: a time-varying floor.
U_07_RECORD = {
    "status": "UNRESOLVED_CLASSIFICATION",
    "scope": "A2_ONLY",
    "blocks_main_full81": False,
    "variable_floor_support_implemented": False,
    "annual_model_accepts_time_varying_reserve_floor": False,
    "resolved_by_this_alignment": False,
}

#: Recorded as a later requirement; explicitly out of scope for this pass and
#: not a prerequisite for executing Full81.
CROSS_CASE_AGGREGATION_RECORD = {
    "status": "GAP_RECORDED_NOT_DESIGNED_NOT_IMPLEMENTED_NOT_AUTHORIZED",
    "implemented_by_this_alignment": False,
    "prerequisite_for_full81_execution": False,
    "required_before": (
        "SUBSTANTIVE_RESPONSE_SURFACE_INTERPRETATION",
        "MEETING_ANALYSIS",
    ),
    "note": (
        "A cross-case surface-summary aggregation layer must not add a "
        "materiality-classification column, which would depend on the "
        "unresolved U-01."
    ),
}

MATERIALITY_THRESHOLD_RECORD = {
    "status": "THRESHOLD_DECISION_REQUIRED_BEFORE_A2",
    "accepted_numerical_threshold": None,
    "selected_threshold_option": None,
    "selected_by_this_alignment": False,
}


def governance_state(
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """The exact governance semantics this production authority encodes.

    ``lifecycle`` is the resolved U-06 accepted-lifecycle overlay.  Omitting it
    yields the most restrictive state, so an omission never reads as acceptance.
    """

    summary = lifecycle_summary(lifecycle)
    register = dict(STATIC_UNRESOLVED_REGISTER)
    register["U-06"] = u06_register_entry(lifecycle)
    return {
        "u06_lifecycle": summary,
        # R2-AUD-03: the register entry WITH explicit ownership, so no consumer
        # has to infer whose state the one-line entry describes.
        "u06_register_state": u06_register_state(lifecycle),
        "u06_acceptance_status": summary["u06_acceptance_status"],
        "u06_independent_audit_status": summary["u06_independent_audit_status"],
        "production_authority_freeze_status": summary[
            "production_authority_freeze_status"
        ],
        "u_01_status": "OPEN_HOLD",
        "u_01_resolved_by_this_alignment": False,
        "u_01_must_be_frozen_before": list(U_01_MUST_BE_FROZEN_BEFORE),
        "u_01_does_not_block": list(U_01_DOES_NOT_BLOCK),
        "u_01_blocks_main_full81": False,
        "a2_status": A2_STATUS,
        "a2_result_exposure": A2_RESULT_EXPOSURE_STATUS,
        "a2_authorized_by_this_alignment": False,
        "a2_paired_difference_exposed": False,
        "a2_conditional_beta8_escalation_authorized": False,
        "main_full81_authorization": main_full81_authorization_status(authorization),
        "main_full81_authorization_resolved": main_full81_authorization_state(
            authorization
        ),
        "main_full81_authorized_by_this_alignment": False,
        "main_full81_execution_authorized": False,
        "main_full81_remaining_lifecycle": list(MAIN_FULL81_REMAINING_LIFECYCLE),
        "unresolved_register": register,
        "u_07": dict(U_07_RECORD),
        "cross_case_aggregation": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in CROSS_CASE_AGGREGATION_RECORD.items()
        },
        "materiality_threshold": dict(MATERIALITY_THRESHOLD_RECORD),
        "governing_authority": (
            "TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_CANDIDATE_R2_ACCEPTANCE_CLOSURE"
        ),
        "governing_authority_published_commit": (
            GOVERNANCE_SEQUENCING_SUCCESSOR_PUBLISHED_COMMIT
        ),
    }


def alignment_is_not_full81_authorization(
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Keep every production state separable from Full81 authorization.

    The mechanical answer to "is Full81 authorized?".  Alignment may be
    ``CANDIDATE_ALIGNED`` and the lifecycle may be ``FROZEN`` while
    authorization stays ``NOT_AUTHORIZED``: the fields are independent, and the
    authorization field is resolved from an external artifact that does not
    exist.  Even a lawful authorization would only reach
    ``AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT`` — never execution.
    """

    summary = lifecycle_summary(lifecycle)
    authorization_view = main_full81_authorization_state(authorization)
    return {
        "production_authority_alignment": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "u06_independent_audit_status": summary["u06_independent_audit_status"],
        "u06_acceptance_status": summary["u06_acceptance_status"],
        "production_authority_freeze_status": summary[
            "production_authority_freeze_status"
        ],
        "main_full81_authorization": main_full81_authorization_status(authorization),
        "main_full81_authorization_resolved": authorization_view,
        "main_full81_authorization_lawful_path": (
            MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH
        ),
        "main_full81_authorization_artifact": MAIN_FULL81_AUTHORIZATION_ARTIFACT,
        "main_full81_authorization_artifact_constant_is_retired": True,
        "main_full81_authorization_mechanism_module": (
            "src/main_full81_authorization_v7_4.py"
        ),
        "main_full81_authorization_mechanism_version": (
            FULL81_AUTHORIZATION_MODULE_VERSION
        ),
        "main_full81_authorization_mechanism_lineage": (
            FULL81_AUTHORIZATION_LINEAGE_ID
        ),
        "main_full81_authorization_mechanism_lifecycle": (
            "CANDIDATE_NOT_ACCEPTED_NOT_FROZEN"
        ),
        "alignment_implies_authorization": False,
        "acceptance_implies_authorization": False,
        "freeze_implies_authorization": False,
        "authorization_implies_execution": False,
        "preflight_pass_implies_authorization": False,
        "separate_authorization_required": True,
        "separate_execution_authorization_required": True,
        "remaining_lifecycle": list(MAIN_FULL81_REMAINING_LIFECYCLE),
        "lifecycle_distinctions": summary["lifecycle_distinctions"],
        "authorization_distinctions": authorization_view[
            "authorization_distinctions"
        ],
        "next_required_gate": "FRESH_INDEPENDENT_AUDIT_OF_THE_U_06_R2_CANDIDATE",
        "next_required_gate_successor_refinement": (
            "INDEPENDENT_AUDIT_OF_THE_FULL81_AUTHORIZATION_MECHANISM_SUCCESSOR"
        ),
        "remaining_lifecycle_successor_refinement": list(
            MAIN_FULL81_REMAINING_LIFECYCLE_SUCCESSOR_REFINEMENT
        ),
    }


def require_a2_hard_block(selected_scope: str | None) -> None:
    """Reject every A2 / variable-floor scope before a U-01 freeze exists."""

    if selected_scope is None:
        return
    lowered = str(selected_scope).strip().lower()
    for token in A2_BLOCKED_SCOPE_TOKENS:
        if token in lowered:
            raise A2ExecutionHardBlocked(
                "A2 / variable-floor execution is HARD BLOCKED until U-01 is "
                "resolved, independently audited, accepted, and frozen. Requested "
                f"scope {selected_scope!r} matched blocked token {token!r}. No "
                "model was constructed and no optimization ran."
            )


def main_full81_authorization_state(
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """The resolved Main Full81 authorization view, defaulting to the floor.

    ``authorization`` is the mapping returned by
    :func:`~src.main_full81_authorization_v7_4.resolve_full81_authorization`.
    Omitting it yields the most restrictive state, so an omission can never read
    as authorization.
    """

    return authorization_summary(authorization)


def main_full81_authorization_status(
    authorization: Mapping[str, Any] | None = None,
) -> str:
    """``AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT`` only for a lawful authorization."""

    resolved = main_full81_authorization_state(authorization)
    if resolved.get("main_full81_authorization") == AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT:
        return AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT
    return MAIN_FULL81_AUTHORIZATION_STATUS


def require_full81_scope_authorization(
    selected_scope: str | None,
    *,
    root: Path | None = None,
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> None:
    """Reject the Main Full81 scope unless a lawful authorization grants it.

    Resolution order, fail-closed at every step:

    1. a non-``full81`` scope is not this guard's business and returns;
    2. with no ``root`` and no pre-resolved ``authorization`` the guard cannot
       prove anything, so it rejects — absence is never authorization;
    3. otherwise the authorization is resolved from live bytes and Git and must
       satisfy every invariant in the authorization mechanism.

    A lawful authorization grants progression to the mandatory **no-solve**
    Full81 production preflight and nothing more.  It is never permission to
    call ``optimize()``: Full81 *execution* additionally requires the separate
    execution authorization and arming interlock, which
    :func:`~src.main_full81_authorization_v7_4.require_full81_execution_authorization`
    always refuses in this candidate.

    :data:`MAIN_FULL81_AUTHORIZATION_ARTIFACT` is never read here.
    """

    if selected_scope is None or str(selected_scope).strip().lower() != "full81":
        return

    if authorization is None:
        if root is None:
            raise Full81AuthorizationNotGranted(
                "Main V7.4 Full81 is NOT AUTHORIZED. No repository root was "
                "supplied, so no Main Full81 scope authorization could be "
                "resolved or proved. Absence of proof is never authorization. No "
                "model was constructed and no optimization ran."
            )
        authorization = resolve_full81_authorization(Path(root), lifecycle)

    try:
        require_full81_preflight_authorization(
            Path(root) if root is not None else ROOT, authorization
        )
    except Full81AuthorizationError as exc:
        raise Full81AuthorizationNotGranted(
            "Main V7.4 Full81 is NOT AUTHORIZED. A frozen production authority, "
            "an accepted U-06 lifecycle, a clean repository, and a zero-solve "
            "preflight PASS are each insufficient, alone or together: a lawful, "
            "published Main Full81 scope authorization at "
            f"{MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH} is required. "
            f"{exc.status}: {exc} No model was constructed and no optimization "
            "ran."
        ) from exc


def _verify_pins(root: Path, pins: Sequence[AuthorityPin]) -> dict[str, dict[str, Any]]:
    verified: dict[str, dict[str, Any]] = {}
    root = root.resolve()
    for pin in pins:
        path = root / pin.relative_path
        if not path.is_file():
            raise ProductionAuthorityBundleError(
                "V7_4_AUTHORITY_ARTIFACT_MISSING",
                f"Required V7.4 production authority is missing: {pin.relative_path}",
            )
        actual = sha256_file(path)
        if actual != pin.sha256:
            raise ProductionAuthorityBundleError(
                "V7_4_AUTHORITY_HASH_FAIL",
                f"V7.4 authority SHA256 mismatch for {pin.label}: "
                f"expected={pin.sha256}, actual={actual}, path={pin.relative_path}",
            )
        verified[pin.label] = pin.as_dict()
    return verified


def canonical_planning_input_contract() -> dict[str, Any]:
    """Declared identity/shape of the accepted canonical planning input."""

    return {
        "path": CANONICAL_PLANNING_INPUT.relative_path,
        "sha256": CANONICAL_PLANNING_INPUT.sha256,
        "artifact_role": ACCEPTED_ARTIFACT_ROLE,
        "integration_status": CANONICAL_INPUT_INTEGRATION_STATUS,
        "expected_rows": CANONICAL_INPUT_EXPECTED_ROWS,
        "expected_columns": CANONICAL_INPUT_EXPECTED_COLUMNS,
        "window_start": CANONICAL_INPUT_WINDOW_START,
        "window_end_inclusive": CANONICAL_INPUT_WINDOW_END_INCLUSIVE,
        "filename_provenance_note": CANONICAL_INPUT_FILENAME_NOTE,
        "renamed_regenerated_or_normalized": False,
    }


def declared_authority_record(
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Declared V7.4 authority identities for emission into run-level provenance.

    Pure and deterministic: it restates the pinned identities without touching the
    filesystem.  Proof that those bytes are live is supplied by
    :func:`verify_v7_4_authority_bundle`, which the production gate runs before
    this record is emitted.  U-06 lifecycle state comes from ``lifecycle``, never
    from a constant, so a lawful future acceptance is emitted without a code edit.
    """

    summary = lifecycle_summary(lifecycle)
    return {
        "bundle_version": BUNDLE_VERSION,
        "bundle_scope": BUNDLE_SCOPE,
        "bundle_lineage": BUNDLE_LINEAGE,
        "alignment_status": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "u06_lifecycle": summary,
        "u06_alignment_status": summary["u06_alignment_status"],
        "u06_acceptance_status": summary["u06_acceptance_status"],
        "production_authority_freeze_status": summary[
            "production_authority_freeze_status"
        ],
        "framework": {
            "formal_name": FRAMEWORK_FORMAL_NAME,
            **_pin("framework_v7_4").as_dict(),
        },
        "registry": {
            "formal_name": REGISTRY_FORMAL_NAME,
            "acceptance_commit": REGISTRY_V7_4_ACCEPTANCE_COMMIT,
            **_pin("registry_v7_4").as_dict(),
        },
        "methodology_evidence_authority": {
            pin.label: pin.as_dict() for pin in METHODOLOGY_EVIDENCE_AUTHORITY_V7_4
        },
        "task_3_authority": {
            pin.label: pin.as_dict() for pin in TASK_3_LAYER_A_PREREGISTRATION_R2
        },
        "governance_sequencing_successor": {
            "published_commit": GOVERNANCE_SEQUENCING_SUCCESSOR_PUBLISHED_COMMIT,
            **{
                pin.label: pin.as_dict()
                for pin in TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_R2
            },
        },
        "canonical_planning_input": canonical_planning_input_contract(),
        "parameter_registry": _pin("parameter_registry").as_dict(),
        "model_core": {
            "core_version": CORE_VERSION,
            "core_version_note": CORE_VERSION_NOTE,
            **_pin("model_core").as_dict(),
        },
        "production_successor_stack": _pin("production_successor_stack").as_dict(),
        "full81_runner": _pin("full81_runner").as_dict(),
        "v7_4_alignment_verifier": _pin("v7_4_alignment_verifier").as_dict(),
        "u06_lifecycle_overlay_module": _pin("u06_lifecycle_overlay").as_dict(),
        "main_full81_authorization_module": _pin(
            "main_full81_authorization_mechanism"
        ).as_dict(),
        "inherited_v7_3_authority": {
            "authority_version": V7_3_AUTHORITY_VERSION,
            "module": "src/production_input_authority_v7_3.py",
            "disposition": "PRESERVED_UNMODIFIED_HISTORICAL_PROVENANCE",
            "destructively_rewritten": False,
            "pins": {
                pin.label: pin.as_dict() for pin in INHERITED_V7_3_HISTORICAL_AUTHORITY
            },
        },
        "output_namespace": {
            "namespace": ACCEPTED_OUTPUT_NAMESPACE,
            "disposition": ACCEPTED_OUTPUT_NAMESPACE_DISPOSITION,
            "renamed": False,
        },
        "governance_state": governance_state(lifecycle, authorization),
        "full81_authorization": alignment_is_not_full81_authorization(
            lifecycle, authorization
        ),
        "full81_authorization_mechanism": {
            "module": "src/main_full81_authorization_v7_4.py",
            "module_version": FULL81_AUTHORIZATION_MODULE_VERSION,
            "lineage_id": FULL81_AUTHORIZATION_LINEAGE_ID,
            "lawful_path": MAIN_FULL81_AUTHORIZATION_LAWFUL_PATH,
            "lifecycle": "CANDIDATE_NOT_ACCEPTED_NOT_FROZEN",
        },
    }


def case_level_provenance(
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compact V7.4 authority identity for emission into case-level artifacts."""

    record = declared_authority_record(lifecycle, authorization)
    summary = lifecycle_summary(lifecycle)
    return {
        "bundle_version": BUNDLE_VERSION,
        "alignment_status": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "u06_alignment_status": summary["u06_alignment_status"],
        "u06_acceptance_status": summary["u06_acceptance_status"],
        "production_authority_freeze_status": summary[
            "production_authority_freeze_status"
        ],
        "framework": record["framework"],
        "registry": record["registry"],
        "parameter_registry": record["parameter_registry"],
        "task_3_authority": record["task_3_authority"][
            "task_3_preregistration_acceptance_closure"
        ],
        "governance_sequencing_successor": record["governance_sequencing_successor"][
            "governance_sequencing_successor_acceptance_closure"
        ],
        "canonical_planning_input": {
            "path": CANONICAL_PLANNING_INPUT.relative_path,
            "sha256": CANONICAL_PLANNING_INPUT.sha256,
        },
        "model_core": record["model_core"],
        "production_successor_stack": record["production_successor_stack"],
        "full81_runner": record["full81_runner"],
        "main_full81_authorization": main_full81_authorization_status(authorization),
        "main_full81_execution_authorized": False,
        "a2_status": A2_STATUS,
        "u_01_status": "OPEN_HOLD",
    }


def _pin(label: str) -> AuthorityPin:
    for pin in all_pins():
        if pin.label == label:
            return pin
    raise ProductionAuthorityBundleError(
        "V7_4_AUTHORITY_PIN_UNKNOWN", f"No V7.4 authority pin named {label!r}."
    )


def verify_v7_4_authority_bundle(
    root: Path,
    lifecycle: Mapping[str, Any] | None = None,
    authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify every pinned V7.4 authority identity against live repository bytes.

    Fail-closed.  No model is constructed, no optimization is called, no case is
    run, no output directory is created, and nothing is written.
    """

    root = root.resolve()

    # R3-AUD-03. Refuse before hashing anything if the DECLARATION itself is
    # unsound: a duplicate label or path would make "every declared pin
    # verified exactly once" unprovable.
    inventory = declared_pin_inventory()
    if not inventory["integrity_ok"]:
        raise ProductionAuthorityBundleError(
            "V7_4_AUTHORITY_PIN_DECLARATION_INVALID",
            "The declared V7.4 authority pin universe is not well formed: "
            f"duplicate labels={inventory['duplicate_labels']}, "
            f"duplicate paths={inventory['duplicate_paths']}.",
        )

    # Traverse the ONE declaration. Every declared group is verified here
    # because the verifier iterates the same object `all_pins()` is derived
    # from; there is no second list to fall behind.
    verified_groups: dict[str, dict[str, dict[str, Any]]] = {}
    verified_labels: list[str] = []
    for group_name, group in PIN_GROUPS.items():
        verified = _verify_pins(root, group)
        verified_groups[group_name] = verified
        verified_labels.extend(verified)

    # Mechanical DECLARED-vs-VERIFIED parity. This is the check that would
    # have caught R3-AUD-03 even if the two lists had stayed separate.
    declared_set = set(inventory["declared_labels"])
    verified_set = set(verified_labels)
    declared_unverified = sorted(declared_set - verified_set)
    verified_undeclared = sorted(verified_set - declared_set)
    duplicate_verified = sorted(
        {label for label in verified_labels if verified_labels.count(label) > 1}
    )
    if declared_unverified or verified_undeclared or duplicate_verified:
        raise ProductionAuthorityBundleError(
            "V7_4_AUTHORITY_PIN_PARITY_FAIL",
            "Declared and verified V7.4 authority pin sets disagree: "
            f"declared-but-unverified={declared_unverified}, "
            f"verified-but-undeclared={verified_undeclared}, "
            f"verified-more-than-once={duplicate_verified}.",
        )

    # Only now is a pin count honest: it is the number of pins THIS RUN
    # actually hashed, after exact set equality has been established. It is
    # never len(all_pins()).
    verified_pin_count = len(verified_labels)
    if verified_pin_count != len(declared_set):
        raise ProductionAuthorityBundleError(
            "V7_4_AUTHORITY_PIN_PARITY_FAIL",
            f"Verified {verified_pin_count} pins but {len(declared_set)} are "
            "declared.",
        )

    methodology = verified_groups["methodology_evidence_authority"]
    task_3 = verified_groups["task_3_authority"]
    governance = verified_groups["governance_sequencing_successor"]
    implementation = verified_groups["implementation_authority"]
    alignment_surface = verified_groups["alignment_surface"]
    repository_governance = verified_groups["repository_governance_authority"]
    inherited = verified_groups["inherited_v7_3_historical_authority"]

    return {
        "status": "PASS",
        "verdict": "V7.4 PRODUCTION-AUTHORITY BUNDLE VERIFIED",
        "bundle_version": BUNDLE_VERSION,
        "bundle_scope": BUNDLE_SCOPE,
        "bundle_lineage": BUNDLE_LINEAGE,
        "alignment_status": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "verified_pin_count": verified_pin_count,
        "declared_pin_count": len(declared_set),
        "pin_parity": {
            "declared_pin_count": len(declared_set),
            "verified_pin_count": verified_pin_count,
            "declared_but_unverified": declared_unverified,
            "verified_but_undeclared": verified_undeclared,
            "verified_more_than_once": duplicate_verified,
            "exact_set_equality": True,
            "verified_groups": list(verified_groups),
            "declared_groups": inventory["group_names"],
            "count_source": "ACTUALLY_VERIFIED_UNIQUE_PINS_NOT_LEN_ALL_PINS",
        },
        "methodology_evidence_authority": methodology,
        "task_3_authority": task_3,
        "governance_sequencing_successor": governance,
        "governance_sequencing_successor_published_commit": (
            GOVERNANCE_SEQUENCING_SUCCESSOR_PUBLISHED_COMMIT
        ),
        "implementation_authority": implementation,
        "alignment_surface": alignment_surface,
        "repository_governance_authority": repository_governance,
        "inherited_v7_3_historical_authority": inherited,
        "canonical_planning_input": canonical_planning_input_contract(),
        "model_core": {
            "path": _pin("model_core").relative_path,
            "sha256": _pin("model_core").sha256,
            "core_version": CORE_VERSION,
            "core_version_note": CORE_VERSION_NOTE,
            "equations_changed": False,
        },
        "declared_authority_record": declared_authority_record(
            lifecycle, authorization
        ),
        "governance_state": governance_state(lifecycle, authorization),
        "full81_authorization": alignment_is_not_full81_authorization(
            lifecycle, authorization
        ),
        "full81_authorization_resolved": main_full81_authorization_state(
            authorization
        ),
        "full81_future_authorization_requirements": (
            future_authorization_requirements()
        ),
        "full81_historical_design_precedent": historical_design_precedent(),
        "u06_lifecycle": lifecycle_summary(lifecycle),
        "lifecycle_authority_held_by_this_bundle": False,
        "lifecycle_authority_module": "src/production_authority_lifecycle_u06.py",
        "full81_authorization_authority_held_by_this_bundle": False,
        "full81_authorization_authority_module": (
            "src/main_full81_authorization_v7_4.py"
        ),
        "output_namespace": {
            "namespace": ACCEPTED_OUTPUT_NAMESPACE,
            "disposition": ACCEPTED_OUTPUT_NAMESPACE_DISPOSITION,
            "renamed": False,
        },
        "execution_counters": {
            "model_constructions": 0,
            "optimization_calls": 0,
            "economic_evaluations": 0,
            "solves": 0,
            "full81_runs": 0,
            "a2_runs": 0,
            "production_run_directories_created": 0,
        },
        "execution_boundary": {
            "Production authority alignment": "VERIFIED",
            "Main Full81 authorization": main_full81_authorization_status(
                authorization
            ),
            "Main Full81 execution authorization": "NOT AUTHORIZED",
            "Main Full81 preflight": "NOT PERFORMED BY THIS BUNDLE",
            "Main Full81 execution": "NOT EXECUTED",
            "A2 / variable-floor execution": "HARD BLOCKED",
            "A2 result exposure": "ZERO EXPOSURE",
            "U-01 adjudication": "NOT PERFORMED",
            "U-07 implementation": "NOT PERFORMED",
            "Cross-case aggregation": "NOT IMPLEMENTED",
        },
    }


def expected_pin_table() -> dict[str, dict[str, str]]:
    """Flat label -> {path, sha256} table, for auditing this bundle's claims."""

    return {
        pin.label: {"path": pin.relative_path, "sha256": pin.sha256}
        for pin in all_pins()
    }


def verify_pin_table_against_live_bytes(root: Path) -> dict[str, Mapping[str, Any]]:
    """Recompute every pinned hash from live bytes and report agreement per pin."""

    root = root.resolve()
    report: dict[str, Mapping[str, Any]] = {}
    for pin in all_pins():
        path = root / pin.relative_path
        exists = path.is_file()
        actual = sha256_file(path) if exists else None
        report[pin.label] = {
            "path": pin.relative_path,
            "exists": exists,
            "expected_sha256": pin.sha256,
            "actual_sha256": actual,
            "matches": bool(exists and actual == pin.sha256),
        }
    return report
