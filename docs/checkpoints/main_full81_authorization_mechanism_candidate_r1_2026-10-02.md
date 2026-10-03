# Main Full81 Authorization-Mechanism Successor — Candidate R1

**Date:** 2026-10-02
**Lineage:** `MAIN_FULL81_AUTHORIZATION_MECHANISM_R1`
**Candidate ID:** `MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1`
**Predecessor authority:** U-06 R3 accepted / frozen V7.4 production authority
(commit `e10f8f123af19c0796f5045a51807486cb58647a`)

> ## STATUS
>
> **CANDIDATE**
> **NOT ACCEPTED**
> **NOT FROZEN**
> **DOES NOT AUTHORIZE MAIN FULL81**
> **DOES NOT AUTHORIZE FULL81 PREFLIGHT**
> **DOES NOT AUTHORIZE FULL81 EXECUTION**
>
> This candidate is **pending a fresh independent audit**. Nothing here is an
> acceptance, an audit outcome, a closure, a re-freeze, or an authorization. It
> creates **no** Main Full81 authorization artifact. No independent audit PASS,
> acceptance closure, acceptance manifest, re-freeze record, or accepted-lifecycle
> record was created by this pass, and none may be inferred from it.

---

## 1. Confirmed defect

The accepted U-06 R3 architecture **names** a separate Main Full81 authorization
step but provided **no lawful mechanism** by which it could ever be granted.

At the accepted frozen commit, the predecessor surface contained:

| Element | Predecessor state |
|---|---|
| Full81 authorization role in `ROLE_CONTRACTS` | **absent** (the five roles are all U-06 lifecycle roles) |
| Full81 authorization `artifact_type` | **absent** |
| Full81 authorization `schema_version` | **absent** |
| Lawful path / resolver | **absent** |
| Validator contract | **absent** |
| Publication contract | **absent** |
| Precedent authorization artifact | **absent** |

The only mechanical placeholder was
`src/production_authority_bundle_v7_4.py:108`:

```python
MAIN_FULL81_AUTHORIZATION_ARTIFACT: str | None = None
```

with `require_full81_scope_authorization()` failing closed while it stayed
`None`.

**Migration point.** Authorization migrated from the historical V7.2 route's
runner `scripts/19b_run_final_layer_a_81_cases.py` — which carried a real
dedicated external authority manifest and a `repository_authority()` gate — to
the current route's entry point `scripts/21d_preflight_v7_3_final81_successor.py`,
whose gate lives in `src/production_successor_stack_v7_3.py`. The V7.4 rebuild
carried over the *requirement* for a separate Full81 authorization but not its
*mechanism*.

**Why direct constant editing is invalid.** `src/production_authority_bundle_v7_4.py`
is a member of `ACCEPTED_IMPLEMENTATION_PATHS`, so the accepted U-06 R3 lifecycle
is cryptographically bound to its bytes. Editing the constant to name a real
artifact would change the live implementation-identity digest, raise
`U06_IMPLEMENTATION_IDENTITY_DRIFT`, and invalidate the accepted frozen
lifecycle — on **every** authorization and every revocation. Authorization must
therefore be external data reached through a fixed resolver.

---

## 2. Lineage selection

**Selected: a distinct Full81-authorization-mechanism governance successor
lineage** — `MAIN_FULL81_AUTHORIZATION_MECHANISM_R1`, candidate `R1`.

Not U-06 R4, not U-07, and not a new U-item number. Repository evidence:

1. **U-06 R3 was accepted, not STOPped.** The provenance protocol's
   `Candidate R(n+1)` rule is explicitly for a candidate that *receives* `STOP`
   ("If Candidate Rn receives `STOP` … instead create `Candidate R(n+1)`" —
   `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md`
   §4). R3 received an independent audit PASS, acceptance, and a re-freeze.
   Numbering this `U-06 R4` would falsely assert that R3 failed.
2. **U-06's accepted scope excludes Full81 authorization.** Its
   `production_authority_re_freeze` role contract *requires*
   `authorizes_main_full81 = false`, its aggregator requires
   `authorizes_main_full81 = false`, and `REQUIRED_LIFECYCLE_SEQUENCE` ends with
   `SEPARATE_MAIN_FULL81_AUTHORIZATION` as a step *after* U-06 completes. The
   mechanism is downstream of U-06 by U-06's own accepted design.
3. **`U-07` is reserved.** It is `UNRESOLVED_CLASSIFICATION`, scope `A2_ONLY`,
   and explicitly not a Main Full81 blocker.
4. **The U-item register is for unresolved questions, not mechanisms.** `U-01`
   … `U-07` are unresolved methodology/governance *questions* (materiality
   definition, outcome taxonomy, sensitivity sufficiency, case universes,
   namespace, authority-bundle alignment, variable-floor classification). A
   missing authorization mechanism is an implementation/architecture gap of the
   `B-01` … `B-03` kind. Minting `U-08` would file an implementation mechanism in
   the unresolved-methodology register — a category error. No `U-08` and no
   `B-04` exists anywhere in the repository.
5. **New runner/authority lineages are the protocol's prescribed form** for a
   new production route (§6: "create a new runner lineage; create a new
   preflight; create a new runner-authority manifest").

---

## 3. Historical design precedent

Verified from primary Git bytes, not from narrative.

| Item | Value |
|---|---|
| Historical production tag | `v7.2-final81-runner-ready-r3` |
| Tag peeled commit | `b03721275c73b05d45517bdf84c1e0bd03833376` |
| Historical runner | `scripts/19b_run_final_layer_a_81_cases.py` |
| Historical runner version | `v7.2-final-layer-a-81-production-runner-2026-09-11-r3` |
| Historical runner SHA-256 | `4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe` |
| Historical authority manifest | `docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-11.json` |
| Historical manifest SHA-256 | `4af8a90a0039f97ff05e4eb5903a179d9c3541808d6094131863859fc7e1d9a9` |

The prompt's abbreviated digest (`4af8a90a...e7e1d9a9`) differs in its final
eight characters from the exact bytes (`…fc7e1d9a9`); the value above was
re-derived from the blob at the peeled commit and is authoritative.

### Features ported

- dedicated external machine-readable authorization artifact;
- exact runner path, version, and SHA-256 identity;
- exact alpha/beta grid and case-count identity;
- external solver parameter fingerprint;
- `FRESH_RUN_ONLY` restart policy;
- publication / Git identity requirements;
- clean and upstream-synchronized repository state;
- protected accepted production identities;
- pre-solve authority validation;
- non-self-referential publication proof (the historical manifest's
  `non_self_reference` clause: "Neither this file nor runner embeds its own
  future containing commit or own hash").

### Features deliberately NOT carried forward

| Not ported | Why |
|---|---|
| `data/processed/annual_input_v7_1.parquet` routing | Superseded. The current canonical input is the accepted reconstructed-PV mainline R3 parquet. |
| V7.2 tag as current authority | Immutable historical provenance; never retargeted or reused. |
| V7.2 checkpoints / protected-identity table | Pins superseded V7.2 identities; the current surface is the accepted 21-path implementation identity. |
| Self-produced `pre_solve_gate` as independent proof | Runner self-attestation is never independent audit evidence. |
| Governance semantics superseded by R3 | Role authenticity, exact publication containment, and lifecycle anchoring follow R3, not V7.2's file-identity-only model. |
| `required_production_tag` annotated-tag interlock | The accepted lifecycle already proves publication by exact HEAD/commit containment against `origin/thesis-v7`; an annotated-tag-at-HEAD requirement would add a second, weaker oracle. |
| `ignored_runtime_inventory` pinning | Re-creates the historical `F-01` class of defect, in which an untracked/ignored file became a reachable content-hashed authority dependency. |
| Any historical defect | Not carried forward merely because it existed. |

### Historical provenance caveat — preserved truthfully

`results/layer_a/final_81_execution_authorization/20260911T065811Z/decision.json`
records:

```
FAIL — 81-CASE PRODUCTION EXECUTION NOT AUTHORIZED
blocking_findings: ["F-01"]
real_optimize_calls: 0
production_cases_started: 0
```

`F-01` was `UNTRACKED PROTOCOL FILE IS A REACHABLE PRODUCTION AUTHORITY
DEPENDENCY` (`docs/protocols/iris_thesis_rigorous_audit_skill.md`). That
protocol **was** tracked by the later r3 authority state — verified:
`git cat-file -e b03721275c73b05d45517bdf84c1e0bd03833376:docs/protocols/iris_thesis_rigorous_audit_skill.md`
succeeds. However, `git log --all -- "results/layer_a/final_81_execution_authorization/*"`
returns **nothing**: that namespace was never committed, and **no superseding
explicit independent execution-authorization PASS artifact was recovered from
Git history**.

Therefore: historical Full81 execution-authorization provenance is **not**
claimed to be perfect; the early `FAIL` is **not** current authority; and no
historical defect is required to be carried into the new mechanism.

---

## 4. The new Main Full81 authorization role

| Property | Value |
|---|---|
| Role | `main_full81_scope_authorization` |
| `artifact_type` | `MAIN_FULL81_SCOPE_AUTHORIZATION` |
| `schema_version` | `iris-thesis-full81-authorization-v1` |
| Lawful path (resolver) | `results/provenance/main_full81_authorization_r1/main_full81_authorization.json` |
| Lineage binding | `lineage_id = MAIN_FULL81_AUTHORIZATION_MECHANISM_R1`, `candidate_id = MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1` |
| Target binding | `scripts/21d_preflight_v7_3_final81_successor.py`, version `v7.4-main-full81-no-solve-preflight-runner-2026-10-02-candidate-r1`, live SHA-256 |
| Implementation binding | `implementation_identity_digest` must equal the **live** digest over all accepted implementation paths |
| Lifecycle binding | U-06 lineage `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3`; `require_frozen_lifecycle_against_live_implementation` must pass; the accepted-lifecycle record's path + live SHA-256 must be declared and must be published in the exact named commit |
| Scope | `MAIN_FULL81` only |
| Authorizes | exactly `["MAIN_FULL81_NO_SOLVE_PRODUCTION_PREFLIGHT"]` |
| Publication | exact HEAD containment (A-03 semantics), tracked, clean, `HEAD == origin/thesis-v7`, last modifying commit in published ancestry; the artifact never hard-codes its own containing commit |

The role depends on **none** of: file existence alone, an arbitrary filename,
arbitrary ancestor containment, a mutable Python constant, a manually edited
boolean, or a self-declared textual statement.

`MAIN_FULL81_AUTHORIZATION_ARTIFACT` is **retired**: permanently `None`, never
consulted by any guard, and retained as a standing regression guard against
reintroducing the constant-editing path.

### Separation of states — preserved

```
PRODUCTION_AUTHORITY_FROZEN
  !=  MAIN_FULL81_AUTHORIZED            (this mechanism)
  !=  FULL81_NO_SOLVE_PREFLIGHT_PASS
  !=  FULL81_EXECUTION_AUTHORIZED / ARMED
  !=  FULL81_EXECUTED
```

A lawful authorization reaches exactly `AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT`.
It is **not** permission to call `optimize()`. The execution interlock is
retained separately as `require_full81_execution_authorization()`, which
**always** raises `FULL81_EXECUTION_NOT_AUTHORIZED` in this candidate, and the
pre-existing explicit two-flag execution interface, fresh-run policy, one-armed
model guard, one-`optimize()`-per-case guard, and per-case authority rechecks are
all left byte-unchanged.

---

## 5. Future authorization requires no production-code change

The lawful path is fixed in code; the artifact is not. Creating, revoking, or
replacing a future authorization is a data act at that path. No constant is
edited, no hash is re-pinned, and no implementation-identity drift is caused.

---

## 6. Expected gate behaviour with this successor in the working tree

Because this successor modifies accepted implementation bytes, the published R3
accepted lifecycle **must not** grant live production authority to the modified
tree — and it does not:

```
U-06 overlay        PRESENT_INVALID
U-06 freeze         NOT_FROZEN
rejected_status     U06_IMPLEMENTATION_IDENTITY_DRIFT
```

Every accepted role artifact declares the predecessor digest
`b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a`; the live
digest differs. This is the designed A-02 code-drift property, not a regression.

**The accepted R3 freeze remains fully valid for its accepted commit
`e10f8f123af19c0796f5045a51807486cb58647a`.** It simply does not transfer to
changed bytes. No identity check was weakened to keep production authority
appearing `FROZEN` during successor development.

---

## 7. Open / non-blocking findings

| ID | Severity | Finding |
|---|---|---|
| `G-01` | INFORMATIONAL | Pre-existing `F-POSTPUB-01` lifecycle-stale tests remain, and five further assertions in `tests/test_21g_u06_r3_substitution_attacks.py` became stale under the expected identity drift. **Every one still rejects**; only the reported *status string* changed (`U06_ACCEPTED_LIFECYCLE_INVALID` instead of `…_ABSENT`, `U06_IMPLEMENTATION_IDENTITY_DRIFT` instead of a substitution status). No accepted test byte was modified. See §8. |
| `G-02` | INFORMATIONAL | `scripts/21e_preflight_v7_4_production_authority_alignment.py` contains a lifecycle-stale assertion — `verify_lifecycle_gate()` raises `U06_LIFECYCLE_GATE_DID_NOT_REJECT` when the lifecycle *is* lawfully frozen. At the accepted commit `21e` therefore **fails**; it passes in this working tree only because the drift makes the lifecycle `NOT_FROZEN`. It will fail again once this successor is accepted and re-frozen. Left unmodified: repairing post-freeze verifier semantics is outside this bounded scope and belongs in its own authorized correction. |
| `G-03` | INFORMATIONAL | `A-05` (LF/CRLF hash portability) and `A-04` (verifier/test self-reference) remain recorded only, unchanged by this pass. All new bytes are LF. |
| `G-04` | INFORMATIONAL | The alpha/beta universe and Layer-A solver settings are declared in the mechanism to avoid an import cycle, and cross-checked against the live stack constants by `tests/test_21h`. Drift is detectable from both directions, but it is a second declaration rather than a single source. |

---

## 8. Existing accepted tests — reported, not rewritten

No accepted historical test byte was modified. Verified `UNCHANGED` against
`HEAD`: `tests/test_21a_…`, `tests/test_21b_21d_…`, `tests/test_21e_…`,
`tests/test_21f_…`, `tests/test_21g_…`, and
`scripts/21e_preflight_v7_4_production_authority_alignment.py`.

Two accepted assertions in `tests/test_21e_…` **would** have required
modification had this pass redefined `MAIN_FULL81_REMAINING_LIFECYCLE` and
`next_required_gate`:

- `GovernanceSemanticsTests.test_main_full81_is_not_authorized_by_this_alignment`
  asserts `main_full81_remaining_lifecycle[0] == "V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE"`;
- `GovernanceSemanticsTests.test_alignment_is_mechanically_distinct_from_authorization`
  asserts `next_required_gate == "FRESH_INDEPENDENT_AUDIT_OF_THE_U_06_R2_CANDIDATE"`.

Both strings are already lifecycle-stale at `HEAD` (they name a candidate and an
alignment that have since been audited, accepted, and frozen). Rather than edit
them, this candidate **restored both accepted values verbatim** and added the
successor refinement **additively** as
`MAIN_FULL81_REMAINING_LIFECYCLE_SUCCESSOR_REFINEMENT`,
`remaining_lifecycle_successor_refinement`, and
`next_required_gate_successor_refinement`. This follows the protocol's
additive-only correction rule and keeps both accepted tests green and
byte-identical.

The five newly-stale `test_21g` assertions are reported here for the independent
auditor. A lifecycle-aware successor test would be preferable to editing them,
but creating or modifying it is **not** authorized by this pass.

---

## 9. No-solve guarantee

| Counter | Value |
|---|---|
| `optimize()` calls | **0** |
| Annual MILP solves | **0** |
| Model constructions | **0** |
| Main Full81 cases executed | **0** |
| A2 cases executed | **0** |
| Production run directories created | **0** |
| Real Main Full81 authorization artifacts created | **0** |

An AST scan of every changed and added source finds zero
`optimize` / `optimizeAsync` / `optimizeBatch` / `tune` call sites. The
positive control runs entirely inside throwaway Git repositories under the
system temp directory, which are removed on teardown.

---

## 10. Required next gate

**A fresh independent read-only audit of this candidate**, re-attempting every
negative control against the live validator, with the historical V7.2 manifest
re-presented as current authority.

Acceptance, the accepted-lifecycle record, the production-authority re-freeze,
commit/publication, the creation of a real Main Full81 authorization artifact,
the Main Full81 no-solve production preflight, the separate Full81 execution
authorization, and Main Full81 execution are **each separate acts requiring
their own authorization**. None is conferred by this candidate.
