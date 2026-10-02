# U-06 V7.4 production-authority alignment — Candidate R3 (no-solve remediation)

**Date:** 2026-10-02
**Candidate identity:** `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R3`
**Lineage identity:** `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3`
**Disposition:** **CANDIDATE / NOT ACCEPTED / NOT CLOSED / NOT FROZEN / PENDING FRESH INDEPENDENT AUDIT**
**Pass type:** bounded governance / provenance remediation of a CRITICAL audit NO-GO; additive; no solve
**Scope:** `A-01`, `A-02`, `A-03` remediation plus truthful `R1` / `R2` provenance

> **Nothing here is closed.** `F-01`, `A-01`, `A-02`, and `A-03` are
> **REMEDIATION IMPLEMENTED — PENDING FRESH INDEPENDENT VERIFICATION**. Closure
> requires a fresh independent audit, which has not been performed. This
> checkpoint is not acceptance, not a closure, not a re-freeze, and not Full81
> authorization.

## 1. Current governance state — verified live before editing

| Item | State |
|---|---|
| Branch | `thesis-v7` |
| HEAD | `fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0` = `origin/thesis-v7` |
| Staged paths / tags created | `0` / `0` |
| Framework V7.4 | `CLOSED / ACCEPTED` |
| Registry V7.4 | `CLOSED / ACCEPTED` |
| Governance-sequencing successor R2 | `CLOSED / ACCEPTED / PUBLISHED` |
| `U-01` | `OPEN / HOLD` — does not block Main Full81 |
| `A2` | `HARD BLOCKED` |
| Main Full81 | `NOT AUTHORIZED` |
| `U-06 R1` | `FAILED` independent audit (`F-01`) |
| `U-06 R2` | `NO-GO / CRITICAL GOVERNANCE DEFECT` |
| `U-06 R3` | this candidate — current remediation target |
| `U-07` | `UNRESOLVED_CLASSIFICATION` / A2-only |

## 2. R2 NO-GO findings acknowledged

R2 **must not** be accepted, closed, frozen, committed as production authority,
or used to authorize Full81. It is recorded as `NO-GO — CRITICAL GOVERNANCE
DEFECT` with:

| Finding | Severity | Substance |
|---|---|---|
| `A-01` | **CRITICAL** | Arbitrary unrelated tracked / clean / hash-correct historical artifacts could satisfy the five lifecycle roles and produce `PRODUCTION_AUTHORITY_FROZEN`. |
| `A-02` | MAJOR | The seven-file accepted implementation identity omitted actual runtime-loaded production dependencies. |
| `A-03` | MAJOR | `publication_commit` only had to be an arbitrary `HEAD` ancestor, which does not prove the claimed artifacts were published in that commit. |
| `A-04` | MINOR | Test-quality weakness. |
| `A-05` | MINOR | LF/CRLF hash portability. |
| `A-06` | INFORMATIONAL | R1 source non-durability. |

**The root cause of `A-01`, stated plainly:** R2 proved **file identity** — path,
SHA-256, tracked, clean — and mistook it for **artifact role authenticity**. A
digest says *which bytes* a file has. It says nothing about whether that file
*is* the U-06 R3 independent audit, acceptance closure, acceptance manifest, or
re-freeze authority. Five genuine, unrelated accepted governance documents could
therefore be assembled into a lifecycle, each individually above suspicion.

These findings are recorded in machine-readable form in
`src/production_authority_lifecycle_u06.py::CANDIDATE_R2_AUDIT_RECORD` and are
emitted into every lifecycle report, so they travel with the provenance.

## 3. R1 / R2 / R3 provenance

| Revision | Audit outcome | Lifecycle |
|---|---|---|
| **R1** `docs/checkpoints/u_06_…_candidate_2026-10-02.md` + its manifest | `FAIL — REMEDIATION REQUIRED` (`F-01`) | `IMMUTABLE_HISTORICAL_FAILED_CANDIDATE_PROVENANCE` |
| **R2** `docs/checkpoints/u_06_…_candidate_r2_2026-10-02.md` + its manifest | `NO-GO — CRITICAL GOVERNANCE DEFECT` (`A-01`/`A-02`/`A-03`) | `IMMUTABLE_HISTORICAL_NO_GO_CANDIDATE_PROVENANCE` |
| **R3** this checkpoint + `results/provenance/u_06_…_candidate_r3_2026-10-02/alignment_manifest.json` | **PENDING FRESH INDEPENDENT AUDIT** | `CANDIDATE / NOT ACCEPTED` |

Neither R1 nor R2 is rewritten to appear successful. Their bytes are unchanged,
they are not renamed or deleted, and their verdicts are not softened. Both R1 and
R2 candidate IDs are additionally placed on a **rejection list**
(`SUPERSEDED_CANDIDATE_IDS`): a future lifecycle record naming either as its
target is rejected with `U06_SUPERSEDED_CANDIDATE_REJECTED`, so a failed
candidate cannot be revived.

As previously recorded, R1's and R2's *implementation* hashes describe their own
bytes, which R3 supersedes in the working tree. That is correct lineage for
immutable superseded candidates, not a reproduction failure.

**On `A-06`:** R2's source bytes are now preserved durably under
`results/provenance/u_06_…_candidate_r3_2026-10-02/superseded_sources/`
(lifecycle overlay, base bundle, and R2 lifecycle test). R1's source is **not
recoverable** — R2 edited those modules in place before any snapshot existed.
That is stated rather than papered over; the practice begins with R2.

## 4. Core R3 principle: identity is not authenticity

Every lifecycle role must now be **semantically and cryptographically bound to
the same U-06 R3 lineage**, not merely be a file with a known digest. Each role
record must declare, and have re-verified against live bytes and live Git:

- `artifact_type` — role-specific;
- `schema_version` — role-specific;
- `lineage_id` — exactly `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3`;
- `target_candidate_id` — exactly `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE_R3`;
- the exact R3 candidate checkpoint (and, for later roles, manifest) path and
  live SHA-256, where the paths are **fixed in code**;
- `implementation_identity_digest` — equal to the live digest over the audited
  accepted implementation surface;
- the exact path + SHA-256 of **every earlier role** in the chain.

Boolean self-labels are never trusted alone: `verdict`, `independent_audit`, and
`acceptance_status` are checked, *and* every claimed identity is re-resolved from
disk and every claimed publication re-proved from Git.

## 5. Role-schema design

| # | Role | `artifact_type` | Binds |
|---|---|---|---|
| 1 | `implementation_candidate` | `U06_IMPLEMENTATION_CANDIDATE` | — (it is the R3 candidate manifest) |
| 2 | `independent_audit_pass` | `U06_INDEPENDENT_AUDIT_PASS` | candidate |
| 3 | `acceptance_closure` | `U06_ACCEPTANCE_CLOSURE` | candidate, audit |
| 4 | `acceptance_manifest` | `U06_ACCEPTANCE_MANIFEST` | candidate, audit, closure |
| 5 | `production_authority_re_freeze` | `U06_PRODUCTION_AUTHORITY_RE_FREEZE` | candidate, audit, closure, manifest |
| — | aggregator | `U06_ACCEPTED_LIFECYCLE` | all five |

Each has a distinct `schema_version` under the `iris-thesis-u06-r3-` prefix. Role
1 does **not** declare its own digest — it *is* the manifest, and the validator
hashes it independently, following the existing anti-circularity precedent.

Role-specific semantics enforced:

- **audit**: `verdict = PASS`, `blocking_critical = 0` and `blocking_major = 0`
  as integers (a boolean `True` is rejected), `independent_audit = true`,
  `candidate_author_is_not_self_accepting = true`;
- **closure**: `acceptance_status = CLOSED_ACCEPTED`, binds the exact audit
  artifact, and proves Phase-A publication containment;
- **manifest**: `acceptance_status = CLOSED_ACCEPTED`, cross-binds candidate +
  audit + closure;
- **re-freeze**: `production_authority_status_intended = FROZEN`,
  `authorizes_main_full81 = false`, binds the full accepted chain, and proves
  Phase-B publication containment;
- **aggregator**: all five roles must resolve to the **same** `lineage_id`,
  `target_candidate_id`, candidate checkpoint identity, and
  `implementation_identity_digest`. Any disagreement fails closed. Five
  individually valid but mutually unrelated files are rejected.

Anti-aliasing and anti-self-acceptance: the five role paths must be pairwise
distinct (one file may not fill two roles); roles 2–5 may never be a candidate
artifact (R1/R2/R3 checkpoint or manifest), the lifecycle record itself, or any
path under `src/`, `scripts/`, or `tests/`.

## 6. `A-02`: the complete runtime production dependency identity

The R2 seven-file list was **not preserved**. The surface was reconstructed by
tracing the real entrypoints — `scripts/21b` (EOB), `scripts/21c` (Layer A),
`scripts/21d` (Main Full81), and `scripts/21e` — and following real imports
including function-level ones, `__import__` arguments, and paths handed to
`_load_helper` / `_load_module` / `load_module` / `load` /
`spec_from_file_location`. Provenance *citation* strings (lineage lists, pin
tables) were deliberately **not** followed; that distinction is what keeps the
surface honest in both directions.

`RUNTIME_PRODUCTION_DEPENDENCY_PATHS` — **16** executed paths:

| Layer | Paths |
|---|---|
| Entrypoints | `scripts/21b`, `scripts/21c`, `scripts/21d`, `scripts/21e` |
| Authority | `src/production_successor_stack_v7_3.py`, `src/production_authority_bundle_v7_4.py`, `src/production_authority_lifecycle_u06.py`, `src/production_input_authority_v7_3.py`, `scripts/21a_preflight_v7_3_production_routing.py` |
| Scientific / execution | `src/annual_design_model_v7_2.py`, `src/rainflow_validation_v7_2.py`, `scripts/09_build_valid_outage_start_sets.py`, `scripts/15d_run_corrected_eob_v7_2.py`, `scripts/16a_preflight_layer_a_representative_binary_cases.py`, `scripts/19a_preflight_final_layer_a_81_cases.py`, `scripts/19b_run_final_layer_a_81_cases.py` |

Every path the independent audit named is present. The trace additionally found
`scripts/21a` (loaded through the stack's `STEP2E1_PREFLIGHT` constant rather
than a literal, which is exactly how a path-literal scan would miss it),
`scripts/21d`, `src/rainflow_validation_v7_2.py`, and the authority layer itself.
The audit's list was correctly treated as non-exhaustive.

`GATE_PROTECTED_DEPENDENCY_PATHS` — **4** paths not executed on a production path
but required tracked and clean by the gate's own `verify_protected_methodology`,
so a swap would change whether production may run:
`scripts/08_calibrate_kappa.py`, `scripts/15a_…`, `scripts/15b_…`,
`scripts/15c_…`.

`ACCEPTED_IMPLEMENTATION_PATHS` = the union, **20** paths, each exact-bound by
path + SHA-256 and summarized by an order-independent
`implementation_identity_digest`.

`VALIDATION_IDENTITY_PATHS` tracks the five test files **separately**. Tests are
not runtime production authority, and
`tests_are_runtime_production_authority = false` is emitted explicitly so the two
are never conflated.

## 7. `A-02` code-drift property

The gate no longer only validates the lifecycle *shape*; it re-derives the live
digest over the 20 accepted implementation paths and compares it to the accepted
one. If **any** exact-bound runtime dependency changes after acceptance — even
when the change is committed, the working tree is clean, and `HEAD` equals the
upstream — the gate raises `U06_IMPLEMENTATION_IDENTITY_DRIFT` and production
authority is not frozen until a new authority lifecycle is established.

The guard that the production gate calls is
`require_frozen_lifecycle_against_live_implementation(root, lifecycle)`, and the
error text states the committed/clean/pushed case explicitly.

## 8. `A-03`: publication containment without a hash cycle

`publication_commit = some ancestor of HEAD` is **removed** as sufficient proof.
Publication is now proved by **containment**: the artifact must exist *in that
exact commit* and the blob there must hash to the expected value. A commit that
predates an artifact, or contains different bytes, is rejected with
`U06_PUBLICATION_PROOF_INVALID`.

The three phases keep the dependency graph acyclic, so no artifact ever has to
know the hash of the commit that will later contain it:

```text
PHASE A  candidate + independent audit PASS published        -> commit A
         later acceptance artifacts record audit_publication_commit = A,
         and validation proves BOTH blobs exist in exactly A.

PHASE B  acceptance closure + acceptance manifest published  -> commit B
         the re-freeze record records acceptance_publication_commit = B,
         and validation proves BOTH blobs exist in exactly B.

PHASE C  re-freeze + accepted lifecycle record published     -> commit C
         C is NEVER self-hard-coded. The live gate proves from Git that each
         artifact is in HEAD, that HEAD blobs match live bytes, that HEAD
         equals origin/thesis-v7, that paths are clean, and that the last
         modifying commit is in published ancestry.
```

Helper `require_published_in_commit` covers A and B; `require_published_in_head`
plus `upstream_synchronized` covers C. The HEAD-blob comparison uses SHA-256 over
the blob bytes under the repository's existing working-tree convention; if the
two ever diverge (see `A-05`) the check fails closed rather than silently
accepting.

## 9. Acceptance dependency graph

```text
R3 implementation + candidate checkpoint/manifest
  -> independent audit PASS artifact
  -> audit publication commit A
  -> acceptance closure + acceptance manifest
  -> acceptance publication commit B
  -> re-freeze record
  -> accepted_lifecycle_record
  -> publication commit C
  -> runtime Git containment / upstream-sync verification
  -> PRODUCTION_AUTHORITY_FROZEN
  -> separate Main Full81 authorization
```

Every edge points forward. No artifact must contain the digest or commit id of
anything created after it.

## 10. Files added

| Path | Role |
|---|---|
| `docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02.md` | this checkpoint |
| `results/provenance/u_06_…_candidate_r3_2026-10-02/alignment_manifest.json` | R3 machine record; also the `U06_IMPLEMENTATION_CANDIDATE` role artifact |
| `tests/test_21g_u06_r3_substitution_attacks.py` | `A-01` attack suite |
| `results/provenance/u_06_…_candidate_r3_2026-10-02/superseded_sources/` | durable R2 source snapshot (`A-06`) |

## 11. Files modified

| Path | Change |
|---|---|
| `src/production_authority_lifecycle_u06.py` | rewritten for R3: lineage identity, six role contracts, cross-role binding, publication containment, 20-path accepted implementation identity, drift re-check |
| `src/production_authority_bundle_v7_4.py` | bundle version → R3; alignment surface now pins the R3 attack suite; pins re-derived |
| `src/production_successor_stack_v7_3.py` | gate uses the live-drift re-check and takes `root`; emits `u06_lineage_id` and the audited dependency report; registers the new test |
| `tests/test_21f_u06_accepted_lifecycle_gate.py` | rewritten for R3 lifecycle states, dependency identity, and drift |
| `tests/test_21e_v7_4_production_authority_bundle.py` | alignment-surface expectation updated |
| `docs/ai_handoff/CURRENT_STATE.md`, `docs/ai_handoff/PROJECT_HANDOFF.md` | synchronized to R1 FAILED / R2 NO-GO / R3 pending |

Exact byte counts and SHA-256 values for every path are in the companion
manifest, recomputed from live bytes.

## 12. Full81 authorization remains completely separate

`MAIN_FULL81_AUTHORIZATION_STATUS = NOT_AUTHORIZED` and
`MAIN_FULL81_AUTHORIZATION_ARTIFACT is None`. The `full81` scope is rejected with
`FULL81_AUTHORIZATION_NOT_GRANTED` **before** any repository or lifecycle check,
and this is tested against a synthetically valid **frozen** U-06 lifecycle as
well as the live absent one. The emitted record states
`alignment_implies_authorization`, `acceptance_implies_authorization`, and
`freeze_implies_authorization` all `false`. A re-freeze record declaring
`authorizes_main_full81 = true` is rejected with `U06_RE_FREEZE_OVERREACH`.

## 13. `U-01` / `A2` / `U-07` unchanged

`U-01 = OPEN / HOLD`, unresolved, no threshold selected, still required before all
four A2 events, still not a Main Full81 blocker. `A2 = HARD BLOCKED`, tested
against both the absent and the synthetically frozen lifecycle.
`U-07 = UNRESOLVED_CLASSIFICATION`, A2-only, not a Full81 blocker; no
variable-floor implementation, and the annual model does not accept time-varying
reserve floors. No beta=8 extension is authorized.

## 14. Recorded, deliberately not remediated

- **`A-05` LF/CRLF portability (MINOR).** Carried as a known limitation. No
  `.gitattributes` was added, nothing was renormalized, `core.autocrlf` was not
  changed, and no hash was migrated to a Git blob hash. Pins are over
  working-tree LF bytes — the basis on which the already-accepted
  `production_input_authority_v7_3`, `step2e1_preflight`, and `step2e1_test` pins
  verify. The new HEAD-blob containment checks make a future divergence a hard
  failure rather than a silent acceptance.
- **`A-04` test quality (MINOR).** Partially addressed by the R3 attack suite,
  which uses real repository artifacts rather than only synthetic fixtures. No
  second independent oracle was built into production code.

## 15. Counters

| Action | Count |
|---|---:|
| Acceptances / closures / freezes | `0` |
| Independent audits performed by this pass | `0` |
| Real future lifecycle artifacts created | `0` |
| Fake or placeholder acceptance artifacts created | `0` |
| Digest literals in the overlay module | `0` |
| Model constructions / `optimize()` calls / solves | `0` / `0` / `0` |
| Full81 authorizations / runs / results | `0` / `0` / `0` |
| A2 runs / A2 result exposures | `0` / `0` |
| Production run directories created | `0` |
| Production gates run in authorizing mode | `0` |
| `U-items` resolved / thresholds selected | `0` / `0` |
| Framework / Registry / canonical-input / parameter-registry modifications | `0` |
| Historical V7.3 authority modifications | `0` |
| Historical production result modifications | `0` |
| Output namespace renames / cross-case aggregation layers | `0` / `0` |
| `.gitattributes` added / files renormalized | `0` / `0` |
| Commits / pushes / tags / staged paths | `0` / `0` / `0` / `0` |

## 16. Finding status — truthful wording

| Finding | Status |
|---|---|
| `F-01` | **REMEDIATION TARGET IMPLEMENTED — CLOSURE REQUIRES FRESH INDEPENDENT AUDIT** |
| `A-01` | **REMEDIATION IMPLEMENTED — PENDING FRESH INDEPENDENT VERIFICATION** |
| `A-02` | **REMEDIATION IMPLEMENTED — PENDING FRESH INDEPENDENT VERIFICATION** |
| `A-03` | **REMEDIATION IMPLEMENTED — PENDING FRESH INDEPENDENT VERIFICATION** |
| `A-04` | partially addressed; MINOR, non-blocking |
| `A-05` | recorded only; MINOR, non-blocking |
| `A-06` | R2 source preserved; R1 source not recoverable; INFORMATIONAL |

This checkpoint does **not** state `F-01 CLOSED`, `A-01 CLOSED`, or
`U-06 READY FOR ACCEPTANCE`.

## 17. Final disposition

**Lifecycle status:** `CANDIDATE / NOT ACCEPTED / NOT CLOSED / NOT FROZEN / PENDING FRESH INDEPENDENT AUDIT`

> **U-06 R3 REMEDIATION CANDIDATE READY FOR FRESH INDEPENDENT AUDIT**

`PRODUCTION AUTHORITY = NOT_FROZEN.` `MAIN FULL81 = NOT_AUTHORIZED.`
`A2 = HARD BLOCKED.` `U-01 = OPEN / HOLD.` `U-07 = UNRESOLVED_CLASSIFICATION.`

**Next required gate:** a fresh, independent, read-only audit of this R3
candidate, with the `A-01` substitution attack re-attempted against the live
validator. Acceptance, the accepted-lifecycle record, the production-authority
re-freeze, commit/publication, and any Main Full81 authorization or preflight are
separate acts, each requiring its own authorization. None is conferred here.
