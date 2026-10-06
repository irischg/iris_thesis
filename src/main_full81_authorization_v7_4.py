"""Dedicated Main V7.4 Full81 authorization mechanism (candidate successor).

The defect this module closes
-----------------------------
The accepted U-06 R3 architecture *names* a separate Main Full81 authorization
step — ``MAIN_FULL81_REMAINING_LIFECYCLE`` ends with
``SEPARATE_MAIN_FULL81_AUTHORIZATION``, and the U-06 re-freeze role contract
requires ``authorizes_main_full81 = false`` — but it provided **no lawful
mechanism** by which that authorization could ever be granted.  The only
mechanical artefact was a module-level placeholder,
``MAIN_FULL81_AUTHORIZATION_ARTIFACT = None``, with the scope guard failing
closed while it stayed ``None``.  There was no authorization role, no
``artifact_type``, no ``schema_version``, no lawful path, no validator, no
publication contract, and no precedent artifact.

Editing that placeholder to name a real artifact would have been unlawful: the
bundle holding it is part of the accepted implementation identity
(``ACCEPTED_IMPLEMENTATION_PATHS``), so each authorization would have caused
``U06_IMPLEMENTATION_IDENTITY_DRIFT`` and invalidated the accepted frozen
lifecycle.  Authorization must therefore be **data outside the accepted code**,
reached through a fixed resolver, so that creating or revoking an authorization
never requires another production-code modification.

Design precedent, not a copy
----------------------------
The historical V7.2 route did have a real dedicated Full81 authorization
architecture: an external machine-readable runner-authority manifest at
``docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json``
(SHA-256 ``4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9``),
bound to runner ``scripts/19b_run_final_layer_a_81_cases.py`` version
``v7.2-final-layer-a-81-production-runner-2026-09-11-r3`` under tag
``v7.2-final81-runner-ready-r3`` (peeled
``b03721275c73b05d45517bdf84c1e0bd03833376``).  Its *shape* is reused here:
external manifest, exact runner identity, exact grid identity, solver
fingerprint, fresh-run-only policy, repository/publication identity, and
pre-solve authority validation.

Its *content* is not, and must not be, reused.  That manifest routed
``data/processed/annual_input_v7_1.parquet``, which is not the current canonical
production input, and it is bound to superseded V7.2 identities.  It remains
immutable historical provenance.  It is named in
:data:`REJECTED_HISTORICAL_AUTHORIZATION_PATHS` so that presenting it as current
Full81 authority is rejected by path as well as by schema.

Historical provenance caveat, preserved truthfully
--------------------------------------------------
The historical execution-authorization namespace
``results/layer_a/final_81_execution_authorization/20260911T065811Z/`` records
``FAIL — 81-CASE PRODUCTION EXECUTION NOT AUTHORIZED``, blocking finding ``F-01``
(an untracked protocol file was a reachable content-hashed authority
dependency).  That protocol was tracked by the later r3 authority state, but no
superseding explicit independent execution-authorization ``PASS`` artifact was
recovered from Git history.  So the historical provenance is **not** claimed to
be perfect, the early ``FAIL`` is **not** current authority, and no historical
defect is carried forward merely because it existed.

Five states, still separate
---------------------------
``PRODUCTION_AUTHORITY_FROZEN``            U-06 overlay; says nothing about Full81
``MAIN_FULL81_AUTHORIZED``                 here; authorizes the no-solve preflight
``FULL81_NO_SOLVE_PREFLIGHT_PASS``         the preflight's own outcome
``FULL81_EXECUTION_AUTHORIZED / ARMED``    a further, separate act — NOT granted here
``FULL81_EXECUTED``                        never implied by any of the above

A valid authorization artifact resolves to
:data:`AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT` and nothing further.  It is explicitly
**not** permission to call ``optimize()``: the execution interlock after the
preflight is retained separately (see
:func:`require_full81_execution_authorization`, which always rejects in this
candidate).

Nothing authorized exists
-------------------------
No authorization artifact exists at :data:`AUTHORIZATION_RECORD_RELATIVE_PATH`,
and **no digest for any future authorization artifact is hard-coded, reserved,
or stubbed anywhere in this module**.  Only lineage, role, schema, path, grid,
and the accepted production identities are hard-coded — which is precisely what
makes a substituted or stale artifact detectable.  The resolver therefore
reports ``NOT_GRANTED`` and the Full81 scope guard fails closed.

This module is a CANDIDATE.  It is not accepted, not frozen, authorizes no Main
Full81, authorizes no Full81 preflight, and authorizes no Full81 execution.  It
contains no optimization formulation, no model construction, no economic
evaluation, and no solver call.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.production_authority_lifecycle_u06 import (
    CURRENT_GENERATION as CURRENT_PRODUCTION_AUTHORITY_GENERATION,
    HISTORICAL_GENERATIONS as HISTORICAL_PRODUCTION_AUTHORITY_GENERATIONS,
    U06LifecycleError,
    implementation_identity_digest,
    is_tracked_and_clean,
    require_frozen_lifecycle_against_live_implementation,
    require_published_in_commit,
    require_published_in_head,
    upstream_synchronized,
)
from src.production_input_authority_v7_3 import (
    ACCEPTED_ANNUAL_RELATIVE_PATH,
    ACCEPTED_ANNUAL_SHA256,
    sha256_file,
)


#: Advanced to candidate-r8 because this module's CONTRACT changed in
#: Candidate R8: :data:`CANDIDATE_ID` advanced R7 -> R8 and candidate R7 was
#: added to :data:`REJECTED_CANDIDATE_IDS` after its fresh independent audit
#: returned FAIL / NO-GO.  Leaving the label at ``candidate-r7`` would
#: attribute the current contract to a rejected candidate - the same
#: misattribution class as ``R2-AUD-03``.  This string is reported, never used
#: as an acceptance criterion.
AUTHORIZATION_MODULE_VERSION = (
    "v7.4-main-full81-authorization-mechanism-2026-10-06-candidate-r8"
)

#: The successor lineage this mechanism belongs to.  Deliberately **not** a
#: U-06 revision: U-06 R3 was accepted and frozen, not STOPped, and U-06's own
#: accepted scope excludes Full81 authorization.  Deliberately **not** ``U-07``,
#: which is reserved as ``UNRESOLVED_CLASSIFICATION / A2_ONLY``.
#: Advanced for the ``N-04`` successor.  Finding ``N-04`` (MAJOR) required the
#: no-solve runner to *require* this authorization rather than report it, which
#: changed runner bytes, the accepted implementation digest, and therefore the
#: production-authority generation (see
#: :data:`~src.production_authority_lifecycle_u06.CURRENT_GENERATION`).  The
#: mechanism's own pinned contract changed with it: the lawful record path and
#: the authorized runner version below are both different.  Reusing the R2
#: lineage / candidate identity for that changed contract would let the
#: historical, lawfully published R2 authorization satisfy the lineage and
#: candidate checks against a successor it was never about.
#: Candidate iteration R1 -> R2.  The LINEAGE is unchanged: candidate R2 is the
#: publication-compatible successor of candidate R1 inside the SAME production-
#: authority generation, not a new guard generation.  Only the CANDIDATE
#: identity advances, so a future authorization must name candidate R2 and the
#: never-published candidate R1 identity can no longer satisfy the candidate
#: check below.
#: Candidate iteration R2 -> R3.  The LINEAGE is again unchanged: candidate R3
#: is the bounded provenance/governance remediation of the three BLOCKING
#: findings of candidate R2's fresh independent audit (``R2-AUD-01`` parameter-
#: registry publication durability, ``R2-AUD-02`` repository EOL checkout
#: authority, ``R2-AUD-03`` truthful candidate audit-state reporting) inside the
#: SAME production-authority generation, not a new guard generation.  Only the
#: CANDIDATE identity advances, so a future authorization must name candidate R3
#: and neither the never-published candidate R1 identity nor the audit-rejected
#: candidate R2 identity can satisfy the candidate check below.
#: Candidate iteration R3 -> R4.  The LINEAGE is again unchanged: candidate R4
#: is the bounded remediation of the five BLOCKING findings of candidate R3's
#: fresh independent audit (``R3-AUD-01`` stale/cyclic candidate package
#: binding, ``R3-AUD-02`` incomplete EOL authority coverage, ``R3-AUD-03``
#: CRITICAL fail-open bundle verifier, ``R2-AUD-03`` stale historical ownership
#: in the current register entry, ``R3-AUD-04`` predecessor premises in the
#: validation surface) inside the SAME production-authority generation, not a
#: new guard generation.  Only the CANDIDATE identity advances.
#:
#: This advance is REQUIRED, not cosmetic.  Candidate R3 is now listed in
#: :data:`REJECTED_CANDIDATE_IDS`, so leaving ``CANDIDATE_ID`` at R3 would make
#: this mechanism self-contradictory: the hard ``candidate_id == CANDIDATE_ID``
#: equality below would demand the very identity the rejection list bars.  A
#: future authorization must name candidate R4, and none of the never-published
#: candidate R1 identity, the audit-rejected candidate R2 identity, or the
#: audit-rejected candidate R3 identity can satisfy the candidate check below.
#: Candidate iteration R4 -> R5.  The LINEAGE is again unchanged: candidate R5
#: is the bounded remediation of the single BLOCKING finding of candidate R4's
#: fresh independent audit (``R4-AUD-01``, a frozen live durable-publication
#: snapshot with stale and self-referential SHA claims that no validator
#: checked) inside the SAME production-authority generation.  Only the
#: CANDIDATE identity advances, and for the same reason as R3 -> R4 the advance
#: is required: candidate R4 is now in :data:`REJECTED_CANDIDATE_IDS`, so the
#: hard ``candidate_id == CANDIDATE_ID`` equality may not demand it.
#: Candidate iteration R5 -> R6.  The LINEAGE is again unchanged: candidate R6
#: is the bounded remediation of candidate R5's two BLOCKING findings
#: (``R5-AUD-01`` checkpoint identity role ownership, ``R5-AUD-02`` test
#: disposable-write containment) inside the SAME production-authority
#: generation.  Only the CANDIDATE identity advances, and the advance is
#: required for the same reason: candidate R5 is now rejected.
#: Candidate iteration R6 -> R7.  The LINEAGE is again unchanged: candidate R7
#: remediates the defect classes of candidate R6's two BLOCKING findings
#: (``R6-AUD-01`` semantic role ownership / obligation verification,
#: ``R6-AUD-02`` test write-containment) inside the SAME production-authority
#: generation.  Only the CANDIDATE identity advances, and the advance is
#: required for the same reason: candidate R6 is now rejected.
#: Candidate iteration R7 -> R8.  The LINEAGE is again unchanged: candidate R8
#: repairs the defect class of candidate R7's BLOCKING finding
#: (``R7-AUD-01``: candidate-controlled historical expected values in the
#: GATE) inside the SAME production-authority generation.  Only the
#: CANDIDATE identity advances, and the advance is required for the same
#: reason: candidate R7 is now rejected.
LINEAGE_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1"
CANDIDATE_ID = "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8"

#: The predecessor mechanism identity, retained as historical evidence.  It was
#: accepted, frozen and lawfully used to publish the R2 authorization; it is not
#: rejected, it is superseded, and it may never authorise this generation.
SUPERSEDED_LINEAGE_IDS_THIS_MECHANISM: tuple[str, ...] = (
    "MAIN_FULL81_AUTHORIZATION_MECHANISM_R1",
)
#: ``MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1`` is this lineage's
#: own superseded candidate.  It PASSED its fresh independent read-only audit;
#: it is therefore NOT a rejected candidate.  Its candidate-publication pass
#: STOPPED on the ``I-04`` Git clean-filter / EOL raw-byte incompatibility, so
#: it was never accepted, never committed, and no authorization artifact naming
#: it was ever created.  It is listed here so that what is being refused stays
#: explicit and auditable, alongside the hard ``candidate_id == CANDIDATE_ID``
#: equality check that already bars it.
SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM: tuple[str, ...] = (
    "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2",
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R1",
)

#: Candidate ids in this lineage that FAILED and may never authorise.
#: ``MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1`` failed its read-only
#: audit on ``H-01`` (no lawful successor promotion path) and ``H-02`` (static
#: predecessor-lineage coupling).
#:
#: ``MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2`` belongs here, not
#: merely in the superseded list above: its fresh independent audit returned
#: FAIL / NO-GO on three MAJOR BLOCKING findings (``R2-AUD-01``, ``R2-AUD-02``,
#: ``R2-AUD-03``).  The distinction is the one this module already draws -
#: candidate R1 of this guard lineage PASSED its audit and merely stopped at
#: publication, so it is *superseded*; candidate R2 FAILED its audit, so it is
#: *rejected*.  Its exact audited bytes are preserved under
#: ``results/provenance/main_full81_preflight_authorization_guard_candidate_r2_
#: audit_stop_2026-10-04/`` and its namespace may never be reused.
#:
#: Candidate R4 addition.  Candidate R3 of this same guard lineage also failed
#: its fresh independent audit -- ``R3-AUD-01`` (stale/cyclic checkpoint-manifest
#: binding), ``R3-AUD-02`` (incomplete EOL authority coverage), ``R3-AUD-03``
#: (CRITICAL: fail-open bundle verifier), ``R2-AUD-03`` (stale historical
#: ownership in the current register entry) and ``R3-AUD-04`` (predecessor
#: premises in the validation surface) -- so it is REJECTED on exactly the same
#: footing as candidate R2 and is barred here for the same reason.  Omitting it
#: would have left a future authorization able to name a candidate whose audit
#: returned FAIL / NO-GO.  Its exact audited bytes are preserved under
#: ``results/provenance/main_full81_preflight_authorization_guard_candidate_r3_
#: audit_stop_2026-10-05/`` and its namespace may never be reused.
#:
#: Candidate R5 addition.  Candidate R4 of this same guard lineage also failed
#: its fresh independent audit, on ``R4-AUD-01``, so it is REJECTED on exactly
#: the same footing as candidates R2 and R3.  Its exact audited bytes are
#: preserved under ``results/provenance/main_full81_preflight_authorization_
#: guard_candidate_r4_audit_stop_2026-10-05/`` and its namespace may never be
#: reused.
REJECTED_CANDIDATE_IDS: tuple[str, ...] = (
    "MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1",
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R2",
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R3",
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R4",
    #: Candidate R6 addition: candidate R5 failed its fresh independent audit
    #: on R5-AUD-01 / R5-AUD-02 and is rejected on the same footing.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R5",
    #: Candidate R7 addition: candidate R6 failed its fresh independent audit
    #: on R6-AUD-01 / R6-AUD-02 and is rejected on the same footing.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R6",
    #: Candidate R8 addition: candidate R7 failed its fresh independent audit
    #: on R7-AUD-01 and is rejected on the same footing.
    "MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7",
)

# ---------------------------------------------------------------------------
# H-02: the production-authority binding is RESOLVED, never hard-coded
# ---------------------------------------------------------------------------
#
# Candidate R1 carried ``REQUIRED_U06_LINEAGE_ID = U06_LINEAGE_ID``, a static
# constant naming the U-06 R3 predecessor.  The read-only audit returned
# ``H-02`` (MAJOR): once the production-authority lifecycle advances a
# generation, that constant is wrong and every authorization fails
# ``FULL81_AUTHORIZATION_U06_BINDING_INVALID``.  A mechanism meant to bind the
# *current* production authority must not name one generation forever.
#
# There is therefore no expected-lineage constant here.  The validator resolves
# the live accepted/frozen lifecycle first and derives the expected
# production-authority generation id, lineage id, and accepted-lifecycle record
# path FROM that resolved mapping.  The constants below are reported for
# transparency only and are never used as an acceptance criterion.
CURRENT_PRODUCTION_AUTHORITY_GENERATION_ID = (
    CURRENT_PRODUCTION_AUTHORITY_GENERATION.generation_id
)
CURRENT_PRODUCTION_AUTHORITY_LINEAGE_ID = (
    CURRENT_PRODUCTION_AUTHORITY_GENERATION.lineage_id
)
#: Superseded production-authority generations, reported so an auditor can see
#: what is being refused.  A superseded generation can never satisfy the
#: binding, because the freeze guard refuses to resolve one as current.
SUPERSEDED_PRODUCTION_AUTHORITY_GENERATION_IDS: tuple[str, ...] = tuple(
    g.generation_id for g in HISTORICAL_PRODUCTION_AUTHORITY_GENERATIONS
)

#: The one semantic role.  A file is not this role because of where it sits or
#: what it is called; it is this role only if it declares this type and schema.
AUTHORIZATION_ROLE = "main_full81_scope_authorization"
AUTHORIZATION_ARTIFACT_TYPE = "MAIN_FULL81_SCOPE_AUTHORIZATION"
#: ``v2``: Candidate R2 materially changed the production-authority binding
#: fields (``u06_*`` -> ``production_authority_*``) and made the expected
#: lineage runtime-resolved rather than static.  A new schema version is
#: mandatory - the v1 version string must never be reused for these semantics.
#: No authorization artifact has ever existed under v1, so nothing is orphaned.
AUTHORIZATION_SCHEMA_VERSION = "iris-thesis-full81-authorization-v2"
SUPERSEDED_AUTHORIZATION_SCHEMA_VERSIONS: tuple[str, ...] = (
    "iris-thesis-full81-authorization-v1",
)

#: Deterministic lawful path.  Fixed in code, the artifact itself is not: this is
#: what lets a future authorization be created or removed with no production-code
#: modification and no implementation-identity drift.
#: Advanced to an ``r3`` slot for the ``N-04`` successor generation.  The ``r2``
#: path below holds a lawfully published authorization artifact; creating the
#: successor authorization there would OVERWRITE published history, which is
#: forbidden.  A new slot is therefore mandatory, and it is deliberately empty:
#: no authorization artifact for this generation exists.
AUTHORIZATION_RECORD_RELATIVE_PATH = Path(
    "results/provenance/main_full81_authorization_r3/main_full81_authorization.json"
)

#: Candidate R1 authorization path, never created and now barred.
REJECTED_AUTHORIZATION_PATHS_THIS_LINEAGE: tuple[str, ...] = (
    "results/provenance/main_full81_authorization_r1/"
    "main_full81_authorization.json",
)

#: The ``r2`` authorization path.  Unlike the rejected ``r1`` path this artifact
#: was lawfully created, validated and published (publication commit
#: ``b560816e59f61aad2efe0ed5797c516a214df563``).  It is preserved untouched as
#: historical evidence of what was authorized for the PREDECESSOR implementation
#: and may never authorise this successor generation: its declared runner
#: SHA-256, runner version, implementation identity digest, lineage and candidate
#: all name the predecessor.
SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM: tuple[str, ...] = (
    "results/provenance/main_full81_authorization_r2/"
    "main_full81_authorization.json",
)

#: The only scope this role may ever authorize.
AUTHORIZATION_SCOPE = "MAIN_FULL81"

#: What the artifact must declare, and the only thing a valid one earns.
REQUIRED_DECLARED_STATUS = "GRANTED"
AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT = "AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT"
NOT_GRANTED = "NOT_GRANTED"
PRESENT_INVALID = "PRESENT_INVALID"
ABSENT = "ABSENT"

#: The single act a valid authorization permits progression to.
AUTHORIZED_NEXT_ACT = "MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT"

#: Exact current Main Full81 universe.  ``tests/test_21h`` asserts these equal
#: the live ``production_successor_stack_v7_3`` grid, which the bundle pins by
#: hash; declaring them here avoids an import cycle while keeping drift
#: detectable from two directions.
EXPECTED_ALPHA_UNIVERSE: tuple[float, ...] = (
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
    1.00,
)
EXPECTED_BETA_UNIVERSE_H: tuple[int, ...] = (4, 5, 6, 7, 8, 9, 10, 11, 12)
EXPECTED_CASE_COUNT = 81

#: Exact current Full81 entry point.  Its SHA-256 is **not** pinned here: it is
#: declared by the authorization artifact and re-derived from live bytes, so this
#: module never needs re-editing when the runner is lawfully re-accepted.
EXPECTED_RUNNER_RELATIVE_PATH = "scripts/21d_preflight_v7_3_final81_successor.py"
#: Advanced with the runner for ``N-04``.  The runner now REQUIRES this
#: authorization on its no-solve path instead of merely reporting it, so the
#: version string it must declare changed with that contract.  Without this
#: advance no future authorization could ever name the remediated runner.
#:
#: Candidate R4 deliberately does NOT advance this.  It is not a label for the
#: current candidate: it is the exact identity
#: ``scripts/21d_preflight_v7_3_final81_successor.py`` declares in its own
#: ``RUNNER_VERSION``, and Candidate R4 leaves that runner byte-identical.
#: Advancing it here would break the contract with an unchanged runner and make
#: every future authorization unsatisfiable.
EXPECTED_RUNNER_VERSION = (
    "v7.4-main-full81-no-solve-preflight-runner-2026-10-03-candidate-r3"
)
#: The fail-open predecessor runner version, retained so what was superseded
#: stays provable.  An authorization naming it describes the pre-N-04 runner.
SUPERSEDED_RUNNER_VERSIONS: tuple[str, ...] = (
    "v7.4-main-full81-no-solve-preflight-runner-2026-10-02-candidate-r2",
)

#: Accepted production identities an authorization must bind.  Paths and digests
#: of already-accepted artifacts, re-verified against live bytes on every check.
EXPECTED_ANNUAL_INPUT_RELATIVE_PATH = ACCEPTED_ANNUAL_RELATIVE_PATH.as_posix()
EXPECTED_ANNUAL_INPUT_SHA256 = ACCEPTED_ANNUAL_SHA256
EXPECTED_ANNUAL_MODEL_RELATIVE_PATH = "src/annual_design_model_v7_2.py"
EXPECTED_ANNUAL_MODEL_SHA256 = (
    "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8"
)
EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH = "data/reference/parameter_registry_v7_2.csv"
EXPECTED_PARAMETER_REGISTRY_SHA256 = (
    "c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1"
)

#: Accepted Layer-A solver settings, copied for fingerprinting without importing
#: the stack.  ``tests/test_21h`` asserts equality with the live stack mapping.
EXPECTED_LAYER_A_SOLVER_SETTINGS: Mapping[str, Any] = {
    "source": "scripts/19a_preflight_final_layer_a_81_cases.py",
    "mode": "binary",
    "MIPGap": 1e-6,
    "OutputFlag": 0,
    "NumericFocus": 1,
    "TimeLimit": "INFINITY_UNSET",
    "MIPFocus": 0,
    "Threads": 0,
}

#: Ported from the V7.2 precedent: no resumed or partially replayed surface.
REQUIRED_RESTART_POLICY = "FRESH_RUN_ONLY"

#: Scope tokens an authorization must never broaden to.  Checked against every
#: scope-bearing field, so A2 cannot be smuggled in through a list entry.
FORBIDDEN_SCOPE_TOKENS: tuple[str, ...] = (
    "a2",
    "robust",
    "variable_floor",
    "variable-floor",
    "varfloor",
    "perfect_information",
    "perfect-information",
    "perfect information",
    "dg",
    "distributed_generation",
    "sensitivity",
    "treatment_effect",
    "treatment-effect",
)

#: Exclusions an authorization must declare explicitly.  Silence is not an
#: exclusion: a missing entry rejects the artifact.
REQUIRED_DECLARED_EXCLUSIONS: tuple[str, ...] = (
    "A2",
    "A2_VARIABLE_FLOOR_TREATMENT_EFFECT",
    "PERFECT_INFORMATION",
    "DG_EXTENSIONS",
    "NEW_SENSITIVITIES",
    "ALTERNATE_ANNUAL_INPUTS",
    "ALTERED_ALPHA_BETA_GRIDS",
    "NEW_SOLVER_SETTINGS",
    "METHODOLOGY_CHANGES",
)

#: Historical V7.2 manifest-version labels that may never be an authorization
#: lineage.
REJECTED_HISTORICAL_LINEAGE_IDS: tuple[str, ...] = (
    "v7.2-final81-runner-authority-1",
    "v7.2-final81-runner-authority-2",
    "V7_2_FINAL81_RUNNER_AUTHORITY",
)

#: Lineages that may never be the AUTHORIZATION lineage.  The
#: production-authority generation lineages are included because an
#: authorization is a separate act from a production-authority freeze: naming a
#: production-authority lineage as the authorization lineage would conflate the
#: two.  Derived from the live generation registry, so a generation advance
#: extends this set with no edit here.
REJECTED_LINEAGE_IDS: tuple[str, ...] = REJECTED_HISTORICAL_LINEAGE_IDS + tuple(
    g.lineage_id
    for g in (
        CURRENT_PRODUCTION_AUTHORITY_GENERATION,
        *HISTORICAL_PRODUCTION_AUTHORITY_GENERATIONS,
    )
    if g.lineage_id != LINEAGE_ID
)

#: Historical authorization artifacts, rejected by exact path as well as schema.
REJECTED_HISTORICAL_AUTHORIZATION_PATHS: tuple[str, ...] = (
    "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-10.json",
    "docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json",
)

#: An authorization may not be code, a test fixture, or a candidate document.
NON_AUTHORIZATION_PREFIXES: tuple[str, ...] = ("src/", "scripts/", "tests/", "docs/")

#: Upstream whose head must equal HEAD before an authorization is honoured.
EXPECTED_UPSTREAM = "origin/thesis-v7"

#: States that must never collapse into one another.
AUTHORIZATION_DISTINCTIONS: tuple[str, ...] = (
    "PRODUCTION_AUTHORITY_FROZEN",
    "MAIN_FULL81_AUTHORIZED",
    "FULL81_NO_SOLVE_PREFLIGHT_PASS",
    "FULL81_EXECUTION_AUTHORIZED",
    "FULL81_EXECUTED",
)

#: The lawful order.  Each arrow is a separately authorized act.
REQUIRED_AUTHORIZATION_SEQUENCE: tuple[str, ...] = (
    "U06_ACCEPTED_LIFECYCLE_PRESENT_VALID",
    "PRODUCTION_AUTHORITY_FROZEN",
    "FULL81_AUTHORIZATION_MECHANISM_SUCCESSOR_ACCEPTED_AND_RE_FROZEN",
    "MAIN_FULL81_SCOPE_AUTHORIZATION_PUBLISHED",
    "MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT_PASS",
    "SEPARATE_FULL81_EXECUTION_AUTHORIZATION_AND_ARMING",
    "MAIN_FULL81_EXECUTION",
)

#: U-01 semantics, restated from the accepted governance-sequencing successor R2
#: closure so an authorization cannot quietly re-describe them.
U_01_STATUS = "OPEN_HOLD"
U_01_BLOCKS_MAIN_FULL81 = False
U_01_MUST_BE_FROZEN_BEFORE: tuple[str, ...] = (
    "A2_EXECUTION",
    "A2_RESULT_EXPOSURE",
    "A2_INTERPRETATION",
    "A2_CONDITIONAL_EXTENSION_AUTHORIZATION",
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class Full81AuthorizationError(RuntimeError):
    """Fail-closed Full81 authorization error carrying a stable status."""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def _require(condition: bool, status: str, message: str) -> None:
    if not condition:
        raise Full81AuthorizationError(status, message)


@dataclass(frozen=True)
class AuthorizationRoleContract:
    """Machine-readable contract the Full81 authorization role must satisfy."""

    role: str
    artifact_type: str
    schema_version: str
    lineage_id: str
    scope: str
    lawful_path: str
    authorizes: str
    required_fields: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "artifact_type": self.artifact_type,
            "schema_version": self.schema_version,
            "lineage_id": self.lineage_id,
            "scope": self.scope,
            "lawful_path": self.lawful_path,
            "authorizes": self.authorizes,
            "required_fields": list(self.required_fields),
        }


#: Required fields, in the order the validator reads them.  Every one is
#: mechanically checkable against live bytes, live Git, or a fixed contract — no
#: field is declared that the architecture cannot verify.
AUTHORIZATION_REQUIRED_FIELDS: tuple[str, ...] = (
    "artifact_type",
    "schema_version",
    "lineage_id",
    "candidate_id",
    "authorization_status",
    "authorization_scope",
    "authorizes",
    "authorizes_optimize_calls",
    "authorizes_full81_execution",
    "requires_no_solve_preflight_before_execution",
    "production_authority_generation_id",
    "production_authority_lineage_id",
    "production_authority_accepted_lifecycle_record",
    "production_authority_publication_commit",
    "production_authority_freeze_status",
    "implementation_identity_digest",
    "target_runner",
    "canonical_annual_input",
    "accepted_annual_model",
    "parameter_registry",
    "alpha_universe",
    "beta_universe_h",
    "case_count",
    "solver_parameter_fingerprint",
    "restart_policy",
    "excluded_scopes",
    "a2_excluded",
    "u_01_status",
    "u_01_blocks_main_full81",
    "u_01_must_be_frozen_before",
)

AUTHORIZATION_ROLE_CONTRACT = AuthorizationRoleContract(
    role=AUTHORIZATION_ROLE,
    artifact_type=AUTHORIZATION_ARTIFACT_TYPE,
    schema_version=AUTHORIZATION_SCHEMA_VERSION,
    lineage_id=LINEAGE_ID,
    scope=AUTHORIZATION_SCOPE,
    lawful_path=AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
    authorizes=AUTHORIZED_NEXT_ACT,
    required_fields=AUTHORIZATION_REQUIRED_FIELDS,
)

ROLE_CONTRACTS: Mapping[str, AuthorizationRoleContract] = {
    AUTHORIZATION_ROLE: AUTHORIZATION_ROLE_CONTRACT,
}


# ---------------------------------------------------------------------------
# Deterministic identities
# ---------------------------------------------------------------------------


def solver_parameter_fingerprint() -> str:
    """Canonical SHA-256 over the accepted Layer-A solver settings.

    Ported from the V7.2 precedent's external ``solver_parameter_fingerprint``:
    an authorization that does not reproduce it is not an authorization for this
    solver configuration.
    """

    payload = json.dumps(
        dict(EXPECTED_LAYER_A_SOLVER_SETTINGS), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def expected_grid_identity() -> dict[str, Any]:
    """The exact authorized Full81 universe, as the validator requires it."""

    return {
        "alpha_universe": list(EXPECTED_ALPHA_UNIVERSE),
        "beta_universe_h": list(EXPECTED_BETA_UNIVERSE_H),
        "case_count": EXPECTED_CASE_COUNT,
    }


def _scope_text(value: Any) -> str:
    """Flatten any scope-bearing value to lowercase text for token screening."""

    if isinstance(value, Mapping):
        return " ".join(_scope_text(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_scope_text(item) for item in value)
    return str(value).lower()


def _reject_forbidden_tokens(value: Any, *, field: str) -> None:
    """Reject scope broadening, including A2 smuggled into a list entry."""

    text = _scope_text(value)
    for token in FORBIDDEN_SCOPE_TOKENS:
        _require(
            token not in text,
            "FULL81_AUTHORIZATION_SCOPE_BROADENED",
            f"Field {field!r} contains forbidden scope token {token!r}. A Main "
            "Full81 authorization may authorize nothing but the 81-case main "
            f"surface; observed {value!r}.",
        )


def declared_module_constant(source: str, name: str) -> str | None:
    """Read a module-level string constant from source text, without importing.

    Parsed with :mod:`ast`, so the runner's own formatting — single line,
    parenthesized, or implicitly concatenated — cannot change the answer, and no
    import cycle is created by reading the runner this module guards.
    """

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        targets = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target] if isinstance(node, ast.AnnAssign) else []
        )
        if not any(
            isinstance(target, ast.Name) and target.id == name for target in targets
        ):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    return None


def _declared_identity(
    payload: Mapping[str, Any], field: str
) -> tuple[str, str]:
    entry = payload.get(field)
    _require(
        isinstance(entry, Mapping),
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        f"Field {field!r} must be an object carrying path and sha256.",
    )
    relative = str(entry.get("path", "")).replace("\\", "/").strip()
    digest = str(entry.get("sha256", "")).lower()
    _require(
        bool(relative),
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        f"Field {field!r} declares no path.",
    )
    _require(
        bool(_SHA256_RE.match(digest)),
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        f"Field {field!r} declares no usable SHA-256.",
    )
    return relative, digest


def _require_exact_live_identity(
    root: Path,
    payload: Mapping[str, Any],
    field: str,
    expected_relative: str,
    expected_sha256: str | None,
    *,
    status: str,
) -> str:
    """Declared path must be the expected one and must match live bytes."""

    relative, declared = _declared_identity(payload, field)
    _require(
        relative == expected_relative,
        status,
        f"Field {field!r} must name {expected_relative}; observed {relative}.",
    )
    path = root / relative
    _require(
        path.is_file(),
        status,
        f"Field {field!r} names a file that does not exist: {relative}",
    )
    actual = sha256_file(path)
    _require(
        declared == actual,
        status,
        f"Field {field!r} declares SHA-256 {declared} for {relative} but live "
        f"bytes hash to {actual}.",
    )
    if expected_sha256 is not None:
        _require(
            actual == expected_sha256,
            status,
            f"Field {field!r}: live {relative} hashes to {actual}, which is not "
            f"the accepted identity {expected_sha256}.",
        )
    return actual


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_authorization_payload(
    root: Path,
    payload: Mapping[str, Any],
    *,
    record_relative: str,
    lifecycle: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate a Main Full81 authorization artifact. Fail-closed throughout.

    Ordered so the reported status names the real governance problem: envelope,
    then lineage, then the U-06 accepted/frozen binding, then implementation
    identity, then target and universe, then scope, then publication.
    """

    root = root.resolve()
    contract = AUTHORIZATION_ROLE_CONTRACT

    # --- envelope -----------------------------------------------------------
    _require(
        isinstance(payload, Mapping),
        "FULL81_AUTHORIZATION_RECORD_INVALID",
        f"{record_relative}: not a JSON object.",
    )
    _require(
        payload.get("artifact_type") == contract.artifact_type,
        "FULL81_AUTHORIZATION_ARTIFACT_TYPE_MISMATCH",
        f"artifact_type must be {contract.artifact_type!r}; observed "
        f"{payload.get('artifact_type')!r}. An unrelated artifact — including the "
        "historical V7.2 runner-authority manifest — cannot fill this role.",
    )
    _require(
        payload.get("schema_version") == contract.schema_version,
        "FULL81_AUTHORIZATION_SCHEMA_MISMATCH",
        f"schema_version must be {contract.schema_version!r}; observed "
        f"{payload.get('schema_version')!r}",
    )

    missing = [f for f in contract.required_fields if f not in payload]
    _require(
        not missing,
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        f"{record_relative}: missing required fields {missing}",
    )

    # --- lawful path and lineage -------------------------------------------
    normalized = record_relative.replace("\\", "/").strip()
    _require(
        normalized not in REJECTED_AUTHORIZATION_PATHS_THIS_LINEAGE,
        "FULL81_AUTHORIZATION_SUPERSEDED_CANDIDATE_REJECTED",
        f"{normalized} is the superseded Candidate-R1 authorization path and may "
        "never authorise the current generation.",
    )
    _require(
        normalized not in SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM,
        "FULL81_AUTHORIZATION_SUPERSEDED_GENERATION_PATH_REJECTED",
        f"{normalized} is the lawfully published authorization of a PREDECESSOR "
        "production-authority generation. It is immutable historical evidence "
        "of what was authorized for the predecessor implementation and never "
        "carries forward to the successor implementation.",
    )
    _require(
        normalized == contract.lawful_path,
        "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
        f"A Main Full81 authorization is only lawful at {contract.lawful_path}; "
        f"observed {normalized}.",
    )
    _require(
        normalized not in REJECTED_HISTORICAL_AUTHORIZATION_PATHS,
        "FULL81_AUTHORIZATION_HISTORICAL_REUSE_REJECTED",
        f"{normalized} is immutable historical V7.2 provenance and may never "
        "authorize the current V7.4 production surface.",
    )
    _require(
        not normalized.startswith(NON_AUTHORIZATION_PREFIXES),
        "FULL81_AUTHORIZATION_ROLE_PATH_INVALID",
        f"An authorization may not be code, a test fixture, or a checkpoint "
        f"document: {normalized}",
    )

    declared_lineage = payload.get("lineage_id")
    _require(
        declared_lineage not in REJECTED_LINEAGE_IDS,
        "FULL81_AUTHORIZATION_LINEAGE_REJECTED",
        f"lineage_id {declared_lineage!r} names a superseded or unrelated "
        "lineage. A V7.2 manifest never authorizes the V7.4 surface, and the "
        "U-06 lineage is production authority, not Full81 authorization.",
    )
    _require(
        declared_lineage not in SUPERSEDED_LINEAGE_IDS_THIS_MECHANISM,
        "FULL81_AUTHORIZATION_SUPERSEDED_GENERATION_REJECTED",
        f"lineage_id {declared_lineage!r} names the PREDECESSOR authorization "
        "mechanism generation. Its authorization is immutable historical "
        "evidence and never authorises the successor implementation.",
    )
    _require(
        declared_lineage == LINEAGE_ID,
        "FULL81_AUTHORIZATION_LINEAGE_MISMATCH",
        f"lineage_id must be {LINEAGE_ID!r}; observed {declared_lineage!r}",
    )
    declared_candidate = payload.get("candidate_id")
    _require(
        declared_candidate not in REJECTED_CANDIDATE_IDS,
        "FULL81_AUTHORIZATION_SUPERSEDED_CANDIDATE_REJECTED",
        f"candidate_id {declared_candidate!r} names a FAILED candidate of this "
        "lineage. Candidate R1 failed its read-only audit on H-01 and H-02 and "
        "may never be revived.",
    )
    _require(
        declared_candidate not in SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM,
        "FULL81_AUTHORIZATION_SUPERSEDED_GENERATION_REJECTED",
        f"candidate_id {declared_candidate!r} names the PREDECESSOR accepted "
        "candidate. It was lawfully authorized for the predecessor "
        "implementation and may never authorise this successor.",
    )
    _require(
        declared_candidate == CANDIDATE_ID,
        "FULL81_AUTHORIZATION_LINEAGE_MISMATCH",
        f"candidate_id must be {CANDIDATE_ID!r}; observed "
        f"{declared_candidate!r}",
    )

    # --- authorization status and semantics --------------------------------
    _require(
        payload.get("authorization_status") == REQUIRED_DECLARED_STATUS,
        "FULL81_AUTHORIZATION_STATUS_NOT_GRANTED",
        f"authorization_status must be {REQUIRED_DECLARED_STATUS!r}; observed "
        f"{payload.get('authorization_status')!r}",
    )
    _require(
        payload.get("authorization_scope") == AUTHORIZATION_SCOPE,
        "FULL81_AUTHORIZATION_SCOPE_MISMATCH",
        f"authorization_scope must be {AUTHORIZATION_SCOPE!r}; observed "
        f"{payload.get('authorization_scope')!r}",
    )
    authorizes = payload.get("authorizes")
    _require(
        isinstance(authorizes, list) and authorizes == [AUTHORIZED_NEXT_ACT],
        "FULL81_AUTHORIZATION_SCOPE_BROADENED",
        f"authorizes must be exactly [{AUTHORIZED_NEXT_ACT!r}]; observed "
        f"{authorizes!r}. This role authorizes progression to the mandatory "
        "no-solve Full81 production preflight and nothing else.",
    )
    _require(
        payload.get("authorizes_optimize_calls") is False,
        "FULL81_AUTHORIZATION_SCOPE_BROADENED",
        "authorizes_optimize_calls must be false. Authorization is never "
        "permission to call optimize().",
    )
    _require(
        payload.get("authorizes_full81_execution") is False,
        "FULL81_AUTHORIZATION_SCOPE_BROADENED",
        "authorizes_full81_execution must be false. Execution requires a "
        "separate execution authorization and arming interlock.",
    )
    _require(
        payload.get("requires_no_solve_preflight_before_execution") is True,
        "FULL81_AUTHORIZATION_SCOPE_BROADENED",
        "requires_no_solve_preflight_before_execution must be true.",
    )

    # --- accepted, frozen production authority (H-02: RESOLVED, not static) --
    #
    # Order matters. The live accepted/frozen lifecycle is resolved FIRST, and
    # the expected generation id, lineage id, and accepted-lifecycle record path
    # are then derived FROM that resolved mapping. No module constant is used as
    # an acceptance criterion, so the binding follows a lawful generation
    # advance with no production-code edit.
    _require(
        payload.get("production_authority_freeze_status") == "FROZEN",
        "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
        "production_authority_freeze_status must be 'FROZEN'; observed "
        f"{payload.get('production_authority_freeze_status')!r}",
    )
    try:
        resolved_lifecycle = require_frozen_lifecycle_against_live_implementation(
            root, lifecycle
        )
    except U06LifecycleError as exc:
        raise Full81AuthorizationError(
            "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
            "Main Full81 cannot be authorized while production authority is not "
            f"frozen for the live implementation: {exc.status}: {exc}",
        ) from exc

    resolved_generation_id = resolved_lifecycle.get("generation_id")
    resolved_pa_lineage = resolved_lifecycle.get("lineage_id")
    resolved_record_path = resolved_lifecycle.get("record_path")
    _require(
        resolved_lifecycle.get("is_current_generation") is True,
        "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_NOT_FROZEN",
        "The resolved accepted lifecycle is not the current production-authority "
        f"generation (resolved {resolved_generation_id!r}). A superseded "
        "generation never authorises Main Full81.",
    )
    _require(
        payload.get("production_authority_generation_id") == resolved_generation_id,
        "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        "production_authority_generation_id must equal the RESOLVED current "
        f"generation {resolved_generation_id!r}; observed "
        f"{payload.get('production_authority_generation_id')!r}. This value is "
        "derived from the live lifecycle, never from a constant in this module.",
    )
    _require(
        payload.get("production_authority_lineage_id") == resolved_pa_lineage,
        "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        "production_authority_lineage_id must equal the RESOLVED current "
        f"production-authority lineage {resolved_pa_lineage!r}; observed "
        f"{payload.get('production_authority_lineage_id')!r}. A superseded "
        "lineage, including any predecessor generation, is rejected here.",
    )

    lifecycle_relative, lifecycle_declared = _declared_identity(
        payload, "production_authority_accepted_lifecycle_record"
    )
    _require(
        lifecycle_relative == resolved_record_path,
        "FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
        f"production_authority_accepted_lifecycle_record names "
        f"{lifecycle_relative}, but the resolved accepted lifecycle of the "
        f"current generation lives at {resolved_record_path!r}.",
    )
    _require_exact_live_identity(
        root,
        payload,
        "production_authority_accepted_lifecycle_record",
        lifecycle_relative,
        None,
        status="FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID",
    )

    # Phase F-A: the accepted lifecycle record must exist in exactly the commit
    # the authorization names. Arbitrary ancestry is not proof - A-03 semantics.
    # The commit is supplied by the artifact and proved against live Git; it is
    # never a constant, so it follows the generation rather than pinning one.
    pa_commit = str(payload.get("production_authority_publication_commit", ""))
    _require(
        bool(_COMMIT_RE.match(pa_commit)),
        "FULL81_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
        "production_authority_publication_commit is not a full SHA-1: "
        f"{pa_commit!r}",
    )
    try:
        require_published_in_commit(
            root,
            pa_commit,
            lifecycle_relative,
            lifecycle_declared,
            label="full81 authorization production_authority_publication_commit",
        )
    except U06LifecycleError as exc:
        raise Full81AuthorizationError(
            "FULL81_AUTHORIZATION_PUBLICATION_PROOF_INVALID",
            "The authorization does not prove the accepted production-authority "
            "lifecycle record was published in the commit it names. Being some "
            f"ancestor of HEAD is not proof. {exc.status}: {exc}",
        ) from exc

    # --- implementation identity -------------------------------------------
    live_digest = implementation_identity_digest(root)
    declared_digest = str(payload.get("implementation_identity_digest", "")).lower()
    _require(
        bool(_SHA256_RE.match(declared_digest)),
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        "implementation_identity_digest is missing or malformed.",
    )
    _require(
        declared_digest == live_digest,
        "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        f"implementation_identity_digest {declared_digest} does not match the "
        f"live accepted implementation surface digest {live_digest}. An "
        "authorization tied to a predecessor implementation never carries "
        "forward to a successor implementation.",
    )
    _require(
        declared_digest == resolved_lifecycle["implementation_identity_digest"],
        "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
        f"implementation_identity_digest {declared_digest} disagrees with the "
        "accepted U-06 lifecycle identity "
        f"{resolved_lifecycle['implementation_identity_digest']}.",
    )

    # --- target runner ------------------------------------------------------
    runner = payload.get("target_runner")
    _require(
        isinstance(runner, Mapping),
        "FULL81_AUTHORIZATION_TARGET_MISMATCH",
        "target_runner must be an object with path, version, and sha256.",
    )
    runner_relative, runner_declared = _declared_identity(payload, "target_runner")
    _require(
        runner_relative == EXPECTED_RUNNER_RELATIVE_PATH,
        "FULL81_AUTHORIZATION_TARGET_MISMATCH",
        f"target_runner.path must be {EXPECTED_RUNNER_RELATIVE_PATH}; observed "
        f"{runner_relative}.",
    )
    runner_path = root / runner_relative
    _require(
        runner_path.is_file(),
        "FULL81_AUTHORIZATION_TARGET_MISMATCH",
        f"target_runner names a file that does not exist: {runner_relative}",
    )
    runner_actual = sha256_file(runner_path)
    _require(
        runner_declared == runner_actual,
        "FULL81_AUTHORIZATION_RUNNER_HASH_MISMATCH",
        f"target_runner declares SHA-256 {runner_declared} but live runner bytes "
        f"hash to {runner_actual}.",
    )
    declared_runner_version = str(runner.get("version", ""))
    _require(
        declared_runner_version == EXPECTED_RUNNER_VERSION,
        "FULL81_AUTHORIZATION_TARGET_MISMATCH",
        f"target_runner.version must be {EXPECTED_RUNNER_VERSION!r}; observed "
        f"{declared_runner_version!r}",
    )
    live_runner_version = declared_module_constant(
        runner_path.read_text(encoding="utf-8"), "RUNNER_VERSION"
    )
    _require(
        live_runner_version == EXPECTED_RUNNER_VERSION,
        "FULL81_AUTHORIZATION_TARGET_MISMATCH",
        f"The live runner {runner_relative} declares RUNNER_VERSION = "
        f"{live_runner_version!r}, not the authorized "
        f"{EXPECTED_RUNNER_VERSION!r}; an authorization may not name a runner "
        "version the runner itself does not carry.",
    )

    # --- accepted production inputs ----------------------------------------
    _require_exact_live_identity(
        root,
        payload,
        "canonical_annual_input",
        EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
        EXPECTED_ANNUAL_INPUT_SHA256,
        status="FULL81_AUTHORIZATION_CANONICAL_INPUT_MISMATCH",
    )
    _require_exact_live_identity(
        root,
        payload,
        "accepted_annual_model",
        EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
        EXPECTED_ANNUAL_MODEL_SHA256,
        status="FULL81_AUTHORIZATION_ANNUAL_MODEL_MISMATCH",
    )
    _require_exact_live_identity(
        root,
        payload,
        "parameter_registry",
        EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
        EXPECTED_PARAMETER_REGISTRY_SHA256,
        status="FULL81_AUTHORIZATION_PARAMETER_REGISTRY_MISMATCH",
    )

    # --- exact authorized universe -----------------------------------------
    alphas = payload.get("alpha_universe")
    _require(
        isinstance(alphas, list)
        and len(alphas) == len(EXPECTED_ALPHA_UNIVERSE)
        and all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in alphas
        )
        and all(
            abs(float(value) - expected) < 1e-12
            for value, expected in zip(alphas, EXPECTED_ALPHA_UNIVERSE)
        ),
        "FULL81_AUTHORIZATION_ALPHA_UNIVERSE_MISMATCH",
        f"alpha_universe must be exactly {list(EXPECTED_ALPHA_UNIVERSE)}; "
        f"observed {alphas!r}.",
    )
    betas = payload.get("beta_universe_h")
    _require(
        isinstance(betas, list)
        and [
            value
            for value in betas
            if isinstance(value, int) and not isinstance(value, bool)
        ]
        == list(EXPECTED_BETA_UNIVERSE_H),
        "FULL81_AUTHORIZATION_BETA_UNIVERSE_MISMATCH",
        f"beta_universe_h must be exactly {list(EXPECTED_BETA_UNIVERSE_H)}; "
        f"observed {betas!r}.",
    )
    case_count = payload.get("case_count")
    _require(
        isinstance(case_count, int)
        and not isinstance(case_count, bool)
        and case_count == EXPECTED_CASE_COUNT,
        "FULL81_AUTHORIZATION_CASE_COUNT_MISMATCH",
        f"case_count must be the integer {EXPECTED_CASE_COUNT}; observed "
        f"{case_count!r}.",
    )
    _require(
        len(EXPECTED_ALPHA_UNIVERSE) * len(EXPECTED_BETA_UNIVERSE_H)
        == EXPECTED_CASE_COUNT,
        "FULL81_AUTHORIZATION_CASE_COUNT_MISMATCH",
        "The declared universe does not multiply out to the authorized case "
        "count.",
    )

    # --- solver settings and restart policy --------------------------------
    expected_fingerprint = solver_parameter_fingerprint()
    _require(
        str(payload.get("solver_parameter_fingerprint", "")).lower()
        == expected_fingerprint,
        "FULL81_AUTHORIZATION_SOLVER_FINGERPRINT_MISMATCH",
        f"solver_parameter_fingerprint must be {expected_fingerprint}; observed "
        f"{payload.get('solver_parameter_fingerprint')!r}.",
    )
    _require(
        payload.get("restart_policy") == REQUIRED_RESTART_POLICY,
        "FULL81_AUTHORIZATION_RESTART_POLICY_INVALID",
        f"restart_policy must be {REQUIRED_RESTART_POLICY!r}; observed "
        f"{payload.get('restart_policy')!r}.",
    )

    # --- explicit exclusions and no scope broadening -----------------------
    exclusions = payload.get("excluded_scopes")
    _require(
        isinstance(exclusions, list),
        "FULL81_AUTHORIZATION_SCHEMA_INVALID",
        "excluded_scopes must be a list.",
    )
    declared_exclusions = {str(item).upper() for item in exclusions}
    missing_exclusions = [
        item for item in REQUIRED_DECLARED_EXCLUSIONS if item not in declared_exclusions
    ]
    _require(
        not missing_exclusions,
        "FULL81_AUTHORIZATION_EXCLUSIONS_INCOMPLETE",
        f"excluded_scopes must explicitly exclude {missing_exclusions}. Silence "
        "is not an exclusion.",
    )
    _require(
        payload.get("a2_excluded") is True,
        "FULL81_AUTHORIZATION_A2_SMUGGLING_REJECTED",
        "a2_excluded must be true.",
    )
    for field in (
        "authorization_scope",
        "authorizes",
        "target_runner",
        "canonical_annual_input",
    ):
        _reject_forbidden_tokens(payload.get(field), field=field)

    # --- U-01 semantics, restated faithfully -------------------------------
    _require(
        payload.get("u_01_status") == U_01_STATUS,
        "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
        f"u_01_status must be {U_01_STATUS!r}; observed "
        f"{payload.get('u_01_status')!r}.",
    )
    _require(
        payload.get("u_01_blocks_main_full81") is False,
        "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
        "u_01_blocks_main_full81 must be false: the accepted "
        "governance-sequencing successor R2 closure removed U-01 as a Main "
        "Full81 blocker.",
    )
    declared_u01_gates = payload.get("u_01_must_be_frozen_before")
    _require(
        isinstance(declared_u01_gates, list)
        and {str(item).upper() for item in declared_u01_gates}
        == set(U_01_MUST_BE_FROZEN_BEFORE),
        "FULL81_AUTHORIZATION_U_01_SEMANTICS_INVALID",
        "u_01_must_be_frozen_before must restate exactly "
        f"{list(U_01_MUST_BE_FROZEN_BEFORE)}; observed {declared_u01_gates!r}.",
    )

    # --- Phase F-B: publication, proved from live Git ----------------------
    synced, reason = upstream_synchronized(root)
    _require(synced, "FULL81_AUTHORIZATION_NOT_PUBLISHED", reason)
    try:
        require_published_in_head(
            root,
            record_relative,
            sha256_file(root / record_relative),
            label="full81 authorization phase F-B",
        )
    except U06LifecycleError as exc:
        raise Full81AuthorizationError(
            "FULL81_AUTHORIZATION_NOT_PUBLISHED",
            "The authorization itself is not lawfully published: it must be in "
            "HEAD with a HEAD blob equal to its live bytes, tracked, clean, on "
            f"a HEAD equal to {EXPECTED_UPSTREAM}, and last modified by a "
            f"published commit. {exc.status}: {exc}",
        ) from exc

    return {
        "authorization_module_version": AUTHORIZATION_MODULE_VERSION,
        "lineage_id": LINEAGE_ID,
        "candidate_id": CANDIDATE_ID,
        "record_path": record_relative,
        "record_present": True,
        "record_committed": True,
        "record_published": True,
        "self_authorized": False,
        "full81_authorization_status": AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT,
        "authorization_overlay": "PRESENT_VALID",
        "authorization_scope": AUTHORIZATION_SCOPE,
        "authorizes": [AUTHORIZED_NEXT_ACT],
        "authorizes_optimize_calls": False,
        "authorizes_full81_execution": False,
        "requires_no_solve_preflight_before_execution": True,
        "authorization_blocked_reason": None,
        "production_authority_generation_id": resolved_generation_id,
        "production_authority_lineage_id": resolved_pa_lineage,
        "production_authority_accepted_lifecycle_record": lifecycle_relative,
        "production_authority_publication_commit": pa_commit,
        "production_authority_freeze_status": "FROZEN",
        "implementation_identity_digest": live_digest,
        "target_runner": {
            "path": runner_relative,
            "version": declared_runner_version,
            "sha256": runner_actual,
        },
        "alpha_universe": list(EXPECTED_ALPHA_UNIVERSE),
        "beta_universe_h": list(EXPECTED_BETA_UNIVERSE_H),
        "case_count": EXPECTED_CASE_COUNT,
        "solver_parameter_fingerprint": expected_fingerprint,
        "restart_policy": REQUIRED_RESTART_POLICY,
        "excluded_scopes": sorted(declared_exclusions),
        "a2_excluded": True,
        "u_01_status": U_01_STATUS,
        "u_01_blocks_main_full81": U_01_BLOCKS_MAIN_FULL81,
        "authorization_distinctions": list(AUTHORIZATION_DISTINCTIONS),
        "required_authorization_sequence": list(REQUIRED_AUTHORIZATION_SEQUENCE),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def absent_authorization(
    *, reason: str | None = None, record_path: str | None = None
) -> dict[str, Any]:
    """The most restrictive state: Main Full81 is not authorized."""

    return {
        "authorization_module_version": AUTHORIZATION_MODULE_VERSION,
        "lineage_id": LINEAGE_ID,
        "candidate_id": CANDIDATE_ID,
        "record_path": record_path or AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        "record_present": False,
        "record_committed": False,
        "record_published": False,
        "self_authorized": False,
        "full81_authorization_status": NOT_GRANTED,
        "authorization_overlay": ABSENT,
        "authorization_scope": None,
        "authorizes": [],
        "authorizes_optimize_calls": False,
        "authorizes_full81_execution": False,
        "requires_no_solve_preflight_before_execution": True,
        "authorization_blocked_reason": reason
        or (
            "No lawful Main Full81 scope authorization exists. Main Full81 "
            "cannot be authorized by a frozen production authority, by an "
            "accepted U-06 lifecycle, by clean Git state, by a zero-solve "
            "preflight PASS, by the historical V7.2 runner-authority manifest, "
            "or by editing a Python constant."
        ),
        "production_authority_generation_id": None,
        "production_authority_lineage_id": None,
        "production_authority_accepted_lifecycle_record": None,
        "production_authority_publication_commit": None,
        "production_authority_freeze_status": None,
        "implementation_identity_digest": None,
        "target_runner": None,
        "alpha_universe": list(EXPECTED_ALPHA_UNIVERSE),
        "beta_universe_h": list(EXPECTED_BETA_UNIVERSE_H),
        "case_count": EXPECTED_CASE_COUNT,
        "solver_parameter_fingerprint": solver_parameter_fingerprint(),
        "restart_policy": REQUIRED_RESTART_POLICY,
        "excluded_scopes": list(REQUIRED_DECLARED_EXCLUSIONS),
        "a2_excluded": True,
        "u_01_status": U_01_STATUS,
        "u_01_blocks_main_full81": U_01_BLOCKS_MAIN_FULL81,
        "authorization_distinctions": list(AUTHORIZATION_DISTINCTIONS),
        "required_authorization_sequence": list(REQUIRED_AUTHORIZATION_SEQUENCE),
        "placeholder_digests_used": False,
        "fabricated_future_hashes": False,
    }


def resolve_full81_authorization(
    root: Path, lifecycle: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Resolve Main Full81 authorization from live bytes and Git. Read-only.

    Never raises: anything invalid resolves to a ``NOT_GRANTED`` state carrying
    the reason, so callers report the blocker rather than crashing. Writes
    nothing, constructs no model, and calls no solver.
    """

    root = root.resolve()
    record_relative = AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()
    path = root / AUTHORIZATION_RECORD_RELATIVE_PATH

    if not path.is_file():
        return absent_authorization(record_path=record_relative)

    tracked, clean = is_tracked_and_clean(root, record_relative)
    if not tracked or not clean:
        state = absent_authorization(
            record_path=record_relative,
            reason=(
                "A Main Full81 authorization exists in the working tree but is "
                f"{'untracked' if not tracked else 'modified relative to HEAD'}. "
                "A local, unpublished, or dirty authorization authorizes nothing."
            ),
        )
        state["record_present"] = True
        state["authorization_overlay"] = PRESENT_INVALID
        return state

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        state = absent_authorization(
            record_path=record_relative,
            reason=f"Main Full81 authorization is not readable JSON: {exc}",
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["authorization_overlay"] = PRESENT_INVALID
        return state

    try:
        return validate_authorization_payload(
            root, payload, record_relative=record_relative, lifecycle=lifecycle
        )
    except (Full81AuthorizationError, U06LifecycleError) as exc:
        state = absent_authorization(
            record_path=record_relative, reason=f"{exc.status}: {exc}"
        )
        state["record_present"] = True
        state["record_committed"] = True
        state["authorization_overlay"] = PRESENT_INVALID
        state["rejected_status"] = exc.status
        return state


#: Invariants a resolved authorization must satisfy before the no-solve Full81
#: production preflight may proceed.
_AUTHORIZED_INVARIANTS: Mapping[str, Any] = {
    "authorization_overlay": "PRESENT_VALID",
    "lineage_id": LINEAGE_ID,
    "candidate_id": CANDIDATE_ID,
    "full81_authorization_status": AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT,
    "authorization_scope": AUTHORIZATION_SCOPE,
    "record_present": True,
    "record_committed": True,
    "record_published": True,
    "self_authorized": False,
    "authorizes_optimize_calls": False,
    "authorizes_full81_execution": False,
    "requires_no_solve_preflight_before_execution": True,
    "production_authority_freeze_status": "FROZEN",
}


def require_full81_preflight_authorization(
    root: Path, authorization: Mapping[str, Any] | None
) -> dict[str, Any]:
    """Gate guard for the mandatory no-solve Full81 production preflight.

    Raises unless a lawful, published authorization grants exactly that act. The
    live implementation identity is re-derived here, so a code change after an
    authorization was published fails closed even when committed and pushed.
    """

    if authorization is None:
        raise Full81AuthorizationError(
            "FULL81_AUTHORIZATION_NOT_GRANTED",
            "No Main Full81 authorization was resolved. Main Full81 may not "
            "proceed to its no-solve production preflight without a lawful, "
            "published Main Full81 scope authorization.",
        )
    for field, expected in _AUTHORIZED_INVARIANTS.items():
        observed = authorization.get(field)
        if observed != expected:
            reason = authorization.get("authorization_blocked_reason") or (
                f"{field} must be {expected!r}; observed {observed!r}"
            )
            raise Full81AuthorizationError(
                "FULL81_AUTHORIZATION_NOT_GRANTED",
                "Main Full81 is NOT AUTHORIZED. Blocking field="
                f"{field}, expected={expected!r}, observed={observed!r}. {reason}",
            )
    digest = authorization.get("implementation_identity_digest")
    live = implementation_identity_digest(root)
    if not isinstance(digest, str) or digest != live:
        raise Full81AuthorizationError(
            "FULL81_AUTHORIZATION_IMPLEMENTATION_IDENTITY_DRIFT",
            f"The authorization carries implementation identity {digest!r}, but "
            f"the live production dependency surface digest is {live}. A Main "
            "Full81 authorization never carries forward to changed production "
            "code, even when the change is committed, clean, and pushed.",
        )
    return dict(authorization)


def require_full81_execution_authorization(
    authorization: Mapping[str, Any] | None,
) -> None:
    """The retained execution interlock after the preflight.

    A valid scope authorization permits the no-solve preflight only.  Full81
    *execution* additionally requires a separate execution authorization, the
    V7.2-precedent explicit execute flag, ``FRESH_RUN_ONLY``, one armed model,
    exactly one ``optimize()`` per case, and per-case authority rechecks.  None
    of that is granted by this candidate, so this guard always rejects.
    """

    status = (
        (authorization or {}).get("full81_authorization_status") or NOT_GRANTED
    )
    raise Full81AuthorizationError(
        "FULL81_EXECUTION_NOT_AUTHORIZED",
        "Main Full81 execution is NOT AUTHORIZED. The resolved scope "
        f"authorization status is {status!r}, which authorizes only "
        f"{AUTHORIZED_NEXT_ACT}. Execution requires a separately authorized "
        "Full81 execution authorization and arming interlock that this "
        "mechanism does not grant. No model was constructed and no optimization "
        "ran.",
    )


def is_authorized_for_preflight(
    root: Path, authorization: Mapping[str, Any] | None
) -> bool:
    """True only when `authorization` lawfully grants the no-solve preflight."""

    try:
        require_full81_preflight_authorization(root, authorization)
    except (Full81AuthorizationError, U06LifecycleError):
        return False
    return True


def authorization_summary(
    authorization: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Compact, emission-ready authorization view, sourced from `authorization`."""

    resolved = dict(authorization) if authorization is not None else absent_authorization()
    return {
        "authorization_module_version": resolved.get("authorization_module_version"),
        "lineage_id": resolved.get("lineage_id"),
        "candidate_id": resolved.get("candidate_id"),
        "main_full81_authorization": resolved.get("full81_authorization_status"),
        "authorization_overlay": resolved.get("authorization_overlay"),
        "authorization_scope": resolved.get("authorization_scope"),
        "authorizes": list(resolved.get("authorizes") or []),
        "authorizes_optimize_calls": resolved.get("authorizes_optimize_calls", False),
        "authorizes_full81_execution": resolved.get(
            "authorizes_full81_execution", False
        ),
        "requires_no_solve_preflight_before_execution": resolved.get(
            "requires_no_solve_preflight_before_execution", True
        ),
        "authorization_blocked_reason": resolved.get("authorization_blocked_reason"),
        "record_path": resolved.get("record_path"),
        "record_present": resolved.get("record_present"),
        "record_committed": resolved.get("record_committed"),
        "record_published": resolved.get("record_published"),
        "implementation_identity_digest": resolved.get(
            "implementation_identity_digest"
        ),
        "production_authority_generation_id": resolved.get(
            "production_authority_generation_id"
        ),
        "production_authority_lineage_id": resolved.get(
            "production_authority_lineage_id"
        ),
        "production_authority_accepted_lifecycle_record": resolved.get(
            "production_authority_accepted_lifecycle_record"
        ),
        "production_authority_publication_commit": resolved.get(
            "production_authority_publication_commit"
        ),
        "production_authority_binding_is_resolved_not_static": True,
        "target_runner": resolved.get("target_runner"),
        "case_count": resolved.get("case_count"),
        "restart_policy": resolved.get("restart_policy"),
        "a2_excluded": resolved.get("a2_excluded", True),
        "u_01_status": resolved.get("u_01_status"),
        "u_01_blocks_main_full81": resolved.get("u_01_blocks_main_full81"),
        "authorization_distinctions": list(AUTHORIZATION_DISTINCTIONS),
        "required_authorization_sequence": list(REQUIRED_AUTHORIZATION_SEQUENCE),
        "execution_authorization": "NOT_GRANTED_BY_THIS_MECHANISM",
    }


def future_authorization_requirements() -> dict[str, Any]:
    """What a future authorization pass must create. No digest is invented here."""

    return {
        "lineage_id": LINEAGE_ID,
        "candidate_id": CANDIDATE_ID,
        "authorization_record_path": AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix(),
        "record_exists_today": False,
        "role_contracts": {
            role: contract.as_dict() for role, contract in ROLE_CONTRACTS.items()
        },
        "required_fields": list(AUTHORIZATION_REQUIRED_FIELDS),
        "authorized_scope": AUTHORIZATION_SCOPE,
        "authorized_next_act": AUTHORIZED_NEXT_ACT,
        "grid_identity": expected_grid_identity(),
        "target_runner_path": EXPECTED_RUNNER_RELATIVE_PATH,
        "target_runner_version": EXPECTED_RUNNER_VERSION,
        "canonical_annual_input": {
            "path": EXPECTED_ANNUAL_INPUT_RELATIVE_PATH,
            "sha256": EXPECTED_ANNUAL_INPUT_SHA256,
        },
        "accepted_annual_model": {
            "path": EXPECTED_ANNUAL_MODEL_RELATIVE_PATH,
            "sha256": EXPECTED_ANNUAL_MODEL_SHA256,
        },
        "parameter_registry": {
            "path": EXPECTED_PARAMETER_REGISTRY_RELATIVE_PATH,
            "sha256": EXPECTED_PARAMETER_REGISTRY_SHA256,
        },
        "solver_parameter_fingerprint": solver_parameter_fingerprint(),
        "restart_policy": REQUIRED_RESTART_POLICY,
        "required_declared_exclusions": list(REQUIRED_DECLARED_EXCLUSIONS),
        "forbidden_scope_tokens": list(FORBIDDEN_SCOPE_TOKENS),
        "rejected_lineage_ids": list(REJECTED_LINEAGE_IDS),
        "rejected_historical_authorization_paths": list(
            REJECTED_HISTORICAL_AUTHORIZATION_PATHS
        ),
        "production_authority_binding_is_resolved_not_static": True,
        "expected_production_authority_lineage_constant_exists": False,
        "observed_current_production_authority_generation_id": (
            CURRENT_PRODUCTION_AUTHORITY_GENERATION_ID
        ),
        "observed_current_production_authority_lineage_id": (
            CURRENT_PRODUCTION_AUTHORITY_LINEAGE_ID
        ),
        "superseded_production_authority_generation_ids": list(
            SUPERSEDED_PRODUCTION_AUTHORITY_GENERATION_IDS
        ),
        "superseded_authorization_schema_versions": list(
            SUPERSEDED_AUTHORIZATION_SCHEMA_VERSIONS
        ),
        "rejected_candidate_ids": list(REJECTED_CANDIDATE_IDS),
        # N-04 successor provenance: what was superseded, and what must never be
        # carried forward to this generation.
        "superseded_lineage_ids_this_mechanism": list(
            SUPERSEDED_LINEAGE_IDS_THIS_MECHANISM
        ),
        "superseded_candidate_ids_this_mechanism": list(
            SUPERSEDED_CANDIDATE_IDS_THIS_MECHANISM
        ),
        "superseded_authorization_paths_this_mechanism": list(
            SUPERSEDED_AUTHORIZATION_PATHS_THIS_MECHANISM
        ),
        "superseded_runner_versions": list(SUPERSEDED_RUNNER_VERSIONS),
        "every_authorization_must_be": [
            "a machine-readable JSON object",
            f"at exactly {AUTHORIZATION_RECORD_RELATIVE_PATH.as_posix()}",
            f"of artifact_type {AUTHORIZATION_ARTIFACT_TYPE}",
            f"of schema_version {AUTHORIZATION_SCHEMA_VERSION}",
            f"declaring lineage_id = {LINEAGE_ID}",
            "declaring the live accepted implementation identity digest",
            "declaring the accepted U-06 lifecycle record path and live SHA-256",
            "proving that record is published in exactly the named commit",
            "declaring the exact runner path, version, and live SHA-256",
            "declaring the exact 9x9 alpha/beta universe and case_count = 81",
            "declaring the accepted solver parameter fingerprint",
            f"declaring restart_policy = {REQUIRED_RESTART_POLICY}",
            "explicitly excluding A2 and every unrelated scope",
            "tracked, clean, present in HEAD with matching blob bytes",
            f"on a HEAD equal to {EXPECTED_UPSTREAM}",
        ],
        "publication_phases": {
            "phase_f_a": (
                "the accepted U-06 lifecycle record is already published; the "
                "authorization names production_authority_publication_commit "
                "and validation "
                "proves that blob exists in exactly that commit."
            ),
            "phase_f_b": (
                "the authorization itself is proved published from live Git — in "
                "HEAD, HEAD blob equal to live bytes, tracked, clean, HEAD equal "
                "to the upstream, last modifying commit in published ancestry. "
                "Its own containing commit is never self-hard-coded."
            ),
        },
        "arbitrary_ancestor_accepted_as_publication_proof": False,
        "self_referential_commit_hash_required": False,
        "future_hashes_fabricated_now": False,
        "placeholder_digests_present": False,
        "mutable_python_constant_can_authorize": False,
        "authorization_implies_execution": False,
        "note": (
            "No authorization artifact exists. The resolver reports NOT_GRANTED "
            "and the Full81 scope guard fails closed. Creating or removing a "
            "future authorization requires no production-code modification."
        ),
    }


def historical_design_precedent() -> dict[str, Any]:
    """The V7.2 precedent this mechanism reuses, and what it refuses to reuse."""

    return {
        "historical_production_tag": "v7.2-final81-runner-ready-r3",
        "historical_tag_peeled_commit": (
            "b03721275c73b05d45517bdf84c1e0bd03833376"
        ),
        "historical_runner_path": "scripts/19b_run_final_layer_a_81_cases.py",
        "historical_runner_version": (
            "v7.2-final-layer-a-81-production-runner-2026-09-11-r3"
        ),
        "historical_runner_sha256": (
            "4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe"
        ),
        "historical_authority_manifest_path": (
            "docs/checkpoints/"
            "final_81_production_runner_authority_v7_2_2026-09-11.json"
        ),
        "historical_authority_manifest_sha256": (
            "4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9"
        ),
        "features_ported": [
            "DEDICATED_EXTERNAL_MACHINE_READABLE_AUTHORIZATION_ARTIFACT",
            "EXACT_RUNNER_PATH_VERSION_AND_SHA256_IDENTITY",
            "EXACT_ALPHA_BETA_GRID_AND_CASE_COUNT_IDENTITY",
            "EXTERNAL_SOLVER_PARAMETER_FINGERPRINT",
            "FRESH_RUN_ONLY_RESTART_POLICY",
            "PUBLICATION_AND_GIT_IDENTITY_REQUIREMENTS",
            "CLEAN_AND_UPSTREAM_SYNCHRONIZED_REPOSITORY_STATE",
            "PROTECTED_ACCEPTED_PRODUCTION_IDENTITIES",
            "PRE_SOLVE_AUTHORITY_VALIDATION",
            "NON_SELF_REFERENTIAL_PUBLICATION_PROOF",
        ],
        "features_not_carried_forward": {
            "annual_input_v7_1_identity": (
                "data/processed/annual_input_v7_1.parquet is not the current "
                "canonical production input; the accepted reconstructed-PV "
                "mainline R3 parquet is."
            ),
            "historical_v7_2_tag_as_current_authority": (
                "v7.2-final81-runner-ready-r3 is immutable historical "
                "provenance and is never retargeted or reused as current "
                "authority."
            ),
            "obsolete_v7_2_checkpoints_and_protected_identity_table": (
                "The V7.2 protected-identity table pins superseded V7.2 "
                "identities; the current surface is the accepted 20-path U-06 "
                "implementation identity."
            ),
            "self_produced_pre_solve_gate_as_independent_proof": (
                "A runner-produced pre_solve_gate is self-attestation, never "
                "independent audit evidence."
            ),
            "obsolete_governance_semantics_superseded_by_r3": (
                "Role authenticity, exact publication containment, and "
                "lifecycle anchoring follow the accepted U-06 R3 semantics, not "
                "the V7.2 file-identity-only model."
            ),
            "required_production_tag_interlock": (
                "Not ported: the current accepted lifecycle proves publication "
                "by exact HEAD/commit containment against origin/thesis-v7, so "
                "an annotated-tag-at-HEAD requirement would add a second, "
                "weaker oracle rather than a stronger one."
            ),
            "ignored_runtime_inventory_pinning": (
                "Not ported: the current gate controls untracked paths across "
                "the protected surface directly; re-introducing an ignored-file "
                "inventory would re-create the historical F-01 class of defect "
                "in which an untracked file became a reachable authority "
                "dependency."
            ),
            "historical_defects": (
                "No historical defect is carried forward merely because it "
                "existed. The recovered 20260911T065811Z decision was FAIL — "
                "81-CASE PRODUCTION EXECUTION NOT AUTHORIZED on F-01, and no "
                "superseding independent execution-authorization PASS artifact "
                "was recovered from Git history."
            ),
        },
        "provenance_caveat": (
            "Historical Full81 execution-authorization provenance is NOT claimed "
            "to be perfect. The early FAIL is not current authority, and the "
            "absence of a recovered superseding PASS is recorded rather than "
            "papered over."
        ),
    }
