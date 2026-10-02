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

``MAIN_FULL81_AUTHORIZATION_STATUS`` (here)
    Whether Main V7.4 Full81 may be executed.  That is ``NOT_AUTHORIZED`` and
    requires a separate authorization artifact that does not exist.  Accordingly
    :func:`require_full81_scope_authorization` rejects the ``full81`` scope
    unconditionally, and :func:`require_a2_hard_block` rejects every A2 /
    variable-floor scope token.  A frozen production authority would still not
    authorize Full81.

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

from src.production_authority_lifecycle_u06 import lifecycle_summary
from src.production_input_authority_v7_3 import (
    ACCEPTED_ANNUAL_RELATIVE_PATH,
    ACCEPTED_ANNUAL_SHA256,
    ACCEPTED_ARTIFACT_ROLE,
    AUTHORITY_FILES as V7_3_AUTHORITY_FILES,
    AUTHORITY_VERSION as V7_3_AUTHORITY_VERSION,
    sha256_file,
)


BUNDLE_VERSION = "v7.4-production-authority-bundle-2026-10-02-candidate-r2"
BUNDLE_SCOPE = "ADDITIVE_V7_4_PRODUCTION_AUTHORITY_BASE_IDENTITY_ONLY_NO_LIFECYCLE_AUTHORITY"
BUNDLE_LINEAGE = "ADDITIVE_SUCCESSOR_TO_V7_3_PRODUCTION_INPUT_AUTHORITY_NOT_A_REPLACEMENT"

#: Alignment of the production route to accepted V7.4 authority.  This is
#: implementation/provenance identity only.  It is explicitly **not** an
#: acceptance, an audit outcome, a freeze, or Full81 authorization — see the
#: accepted-lifecycle overlay for those.
PRODUCTION_AUTHORITY_ALIGNMENT_STATUS = "CANDIDATE_ALIGNED"

#: Authorization to execute the Main V7.4 Full81 surface.  Deliberately separate
#: from the line above; see :func:`alignment_is_not_full81_authorization`.
MAIN_FULL81_AUTHORIZATION_STATUS = "NOT_AUTHORIZED"

#: A separate accepted Main Full81 authorization artifact would be pinned here.
#: None exists, so the Full81 scope guard below can never pass.
MAIN_FULL81_AUTHORIZATION_ARTIFACT: str | None = None

#: Set by the accepted governance-sequencing successor R2 closure, §9.
MAIN_FULL81_REMAINING_LIFECYCLE = (
    "V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE",
    "FRESH_INDEPENDENT_VERIFICATION_OF_THAT_ALIGNMENT",
    "SEPARATE_MAIN_FULL81_AUTHORIZATION_PREFLIGHT",
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
        "d9a79cdb224ec83a928100927a23dc6e13e978a590257b60b130dccaefc5a00e",
        "PRODUCTION_SUCCESSOR_STACK_V7_4_AUTHORITY_BOUND",
        "U_06_ALIGNMENT_CANDIDATE_R2",
    ),
    AuthorityPin(
        "full81_runner",
        "scripts/21d_preflight_v7_3_final81_successor.py",
        "1996dbfbd350f60a0d81eccbbb8272bb83e21c7219cbf59969565773acfa9bc7",
        "FULL81_PREFLIGHT_AND_DEPLOYMENT_GATED_ENTRY_POINT",
        "U_06_ALIGNMENT_CANDIDATE_R2",
    ),
    AuthorityPin(
        "v7_4_alignment_verifier",
        "scripts/21e_preflight_v7_4_production_authority_alignment.py",
        "6b97be4258f0cccf3538a9078548951d0f4fc5d1ede7c43ae94cd26319568803",
        "V7_4_AUTHORITY_ALIGNMENT_NO_SOLVE_VERIFIER",
        "U_06_ALIGNMENT_CANDIDATE_R2",
    ),
    AuthorityPin(
        "u06_lifecycle_overlay",
        "src/production_authority_lifecycle_u06.py",
        "a95f56df5cbef270816243189a50fac5d2fbc53ae80a4ae37252eb2e4ceb8fdb",
        "U_06_ACCEPTED_LIFECYCLE_OVERLAY_NO_SCIENTIFIC_CONTENT",
        "U_06_ALIGNMENT_CANDIDATE_R2",
    ),
    AuthorityPin(
        "u06_lifecycle_test",
        "tests/test_21f_u06_accepted_lifecycle_gate.py",
        "018f4536bc36ce4295b0930f1caa124b1375d91521271599dceec93cf5dd3c83",
        "U_06_LIFECYCLE_GATE_STATIC_TEST_F_01_REGRESSION",
        "U_06_ALIGNMENT_CANDIDATE_R2",
    ),
    AuthorityPin(
        "v7_4_alignment_test",
        "tests/test_21e_v7_4_production_authority_bundle.py",
        "8aaba7371834ce159d3c97188f3f0563dc0fcf8165705888942fe1c78a115338",
        "V7_4_AUTHORITY_ALIGNMENT_STATIC_TEST",
        "U_06_ALIGNMENT_CANDIDATE_R2",
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


def all_pins() -> tuple[AuthorityPin, ...]:
    """Every pin this bundle verifies, in stable declaration order."""

    return (
        METHODOLOGY_EVIDENCE_AUTHORITY_V7_4
        + TASK_3_LAYER_A_PREREGISTRATION_R2
        + TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_R2
        + IMPLEMENTATION_AUTHORITY_V7_4
        + ALIGNMENT_SURFACE_V7_4
        + INHERITED_V7_3_HISTORICAL_AUTHORITY
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


def u06_register_entry(lifecycle: Mapping[str, Any] | None) -> str:
    """Derive the ``U-06`` register entry from lifecycle state, not a constant.

    Before acceptance this reads as a candidate pending audit; after a lawful
    acceptance the same code reads as accepted/frozen, with no edit here and no
    rewriting of any historical artifact.
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
    return "V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT"

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


def governance_state(lifecycle: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The exact governance semantics this production authority encodes.

    ``lifecycle`` is the resolved U-06 accepted-lifecycle overlay.  Omitting it
    yields the most restrictive state, so an omission never reads as acceptance.
    """

    summary = lifecycle_summary(lifecycle)
    register = dict(STATIC_UNRESOLVED_REGISTER)
    register["U-06"] = u06_register_entry(lifecycle)
    return {
        "u06_lifecycle": summary,
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
        "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
        "main_full81_authorized_by_this_alignment": False,
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
) -> dict[str, Any]:
    """Keep every production state separable from Full81 authorization.

    The mechanical answer to "is Full81 authorized?".  Alignment may be
    ``CANDIDATE_ALIGNED``, and a future lifecycle may even be ``FROZEN``, while
    authorization stays ``NOT_AUTHORIZED``: the fields are independent, and the
    authorization field has no accepted backing artifact.
    """

    summary = lifecycle_summary(lifecycle)
    return {
        "production_authority_alignment": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "u06_independent_audit_status": summary["u06_independent_audit_status"],
        "u06_acceptance_status": summary["u06_acceptance_status"],
        "production_authority_freeze_status": summary[
            "production_authority_freeze_status"
        ],
        "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
        "main_full81_authorization_artifact": MAIN_FULL81_AUTHORIZATION_ARTIFACT,
        "alignment_implies_authorization": False,
        "acceptance_implies_authorization": False,
        "freeze_implies_authorization": False,
        "separate_authorization_required": True,
        "remaining_lifecycle": list(MAIN_FULL81_REMAINING_LIFECYCLE),
        "lifecycle_distinctions": summary["lifecycle_distinctions"],
        "next_required_gate": "FRESH_INDEPENDENT_AUDIT_OF_THE_U_06_R2_CANDIDATE",
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


def require_full81_scope_authorization(selected_scope: str | None) -> None:
    """Reject the Main Full81 scope while no separate authorization exists.

    V7.4 production-authority alignment does not authorize Full81.  Until an
    accepted Main Full81 authorization artifact is pinned in
    :data:`MAIN_FULL81_AUTHORIZATION_ARTIFACT`, this guard always rejects.
    """

    if selected_scope is None or str(selected_scope).strip().lower() != "full81":
        return
    if MAIN_FULL81_AUTHORIZATION_ARTIFACT is None:
        raise Full81AuthorizationNotGranted(
            "Main V7.4 Full81 is NOT AUTHORIZED. V7.4 production-authority "
            "alignment is not Full81 authorization: a fresh independent audit of "
            "this alignment and a separate Main Full81 authorization/preflight are "
            "both required first. No model was constructed and no optimization ran."
        )


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
        "governance_state": governance_state(lifecycle),
        "full81_authorization": alignment_is_not_full81_authorization(lifecycle),
    }


def case_level_provenance(
    lifecycle: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compact V7.4 authority identity for emission into case-level artifacts."""

    record = declared_authority_record(lifecycle)
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
        "main_full81_authorization": MAIN_FULL81_AUTHORIZATION_STATUS,
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
    root: Path, lifecycle: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Verify every pinned V7.4 authority identity against live repository bytes.

    Fail-closed.  No model is constructed, no optimization is called, no case is
    run, no output directory is created, and nothing is written.
    """

    root = root.resolve()
    methodology = _verify_pins(root, METHODOLOGY_EVIDENCE_AUTHORITY_V7_4)
    task_3 = _verify_pins(root, TASK_3_LAYER_A_PREREGISTRATION_R2)
    governance = _verify_pins(root, TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_R2)
    implementation = _verify_pins(root, IMPLEMENTATION_AUTHORITY_V7_4)
    alignment_surface = _verify_pins(root, ALIGNMENT_SURFACE_V7_4)
    inherited = _verify_pins(root, INHERITED_V7_3_HISTORICAL_AUTHORITY)

    return {
        "status": "PASS",
        "verdict": "V7.4 PRODUCTION-AUTHORITY BUNDLE VERIFIED",
        "bundle_version": BUNDLE_VERSION,
        "bundle_scope": BUNDLE_SCOPE,
        "bundle_lineage": BUNDLE_LINEAGE,
        "alignment_status": PRODUCTION_AUTHORITY_ALIGNMENT_STATUS,
        "verified_pin_count": len(all_pins()),
        "methodology_evidence_authority": methodology,
        "task_3_authority": task_3,
        "governance_sequencing_successor": governance,
        "governance_sequencing_successor_published_commit": (
            GOVERNANCE_SEQUENCING_SUCCESSOR_PUBLISHED_COMMIT
        ),
        "implementation_authority": implementation,
        "alignment_surface": alignment_surface,
        "inherited_v7_3_historical_authority": inherited,
        "canonical_planning_input": canonical_planning_input_contract(),
        "model_core": {
            "path": _pin("model_core").relative_path,
            "sha256": _pin("model_core").sha256,
            "core_version": CORE_VERSION,
            "core_version_note": CORE_VERSION_NOTE,
            "equations_changed": False,
        },
        "declared_authority_record": declared_authority_record(lifecycle),
        "governance_state": governance_state(lifecycle),
        "full81_authorization": alignment_is_not_full81_authorization(lifecycle),
        "u06_lifecycle": lifecycle_summary(lifecycle),
        "lifecycle_authority_held_by_this_bundle": False,
        "lifecycle_authority_module": "src/production_authority_lifecycle_u06.py",
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
            "Main Full81 authorization": "NOT AUTHORIZED",
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
