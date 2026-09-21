# V7.2 Production Version Lineage / Rerun Difference Freeze — Candidate R6

**Artifact class:** targeted additive provenance/taxonomy correction candidate; implementation correction only.  
**Date:** 2026-09-20  
**Package:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r6/`  
**Status:** **CANDIDATE ONLY — NOT CLOSED / NOT ACCEPTED — pending independent cross-agent audit**

No methodology, model, data, parameter, runner, historical or corrected result, accepted-sensitivity
artifact, completion manifest, authority manifest, commit, or tag was changed. Candidate v1, R2, R3,
R4, and R5 remain immutable **STOP / historical-provenance-only** candidates. R6 is a new additive
candidate only.

## 1. Governing R5 STOP and retained conclusion

The independent R5 audit is accepted as the corrective basis. R5's substantive result remains valid:

```
FINAL81-CORRECTED-R10 = NOT_YET_AUTHORIZED
FINAL81-CORRECTED-R10 = NOT_YET_EXECUTED
```

R5 received **STOP** because its route-authority inventory over-counted component evidence and an
aggregate as independent mandatory guards:

1. G16 already represents the single `protected_identities` loop-level execution requirement and
   reports all 11 mismatched collection members. G33-G36 are four useful path-level mismatch details
   from that same list, not four additional independently evaluated conditions.
2. G40 is a derived deployment aggregate over lower-level blocking guards, not another mandatory
   guard. R5 counted it and also included it in the conceptual blocking set it summarized, producing
   an invalid self-referential aggregate representation.

R6 corrects only that taxonomy and its dependent counts. It does not reopen any R5 finding concerning
START_HEAD, tag roles, repository boundaries, raw-runner identity, historical evidence, timing, the
accepted 1 MW sensitivity, 17d, or causal interpretation.

## 2. Primary-source guard definition and reconstruction

R6 was rebuilt from the current exact bytes of
`scripts/19b_run_final_layer_a_81_cases.py`, particularly `repository_authority()` and
`authority_gate()`, together with the pinned authority manifest, repository state, Git objects/tags,
live remote refs, and hash-pinned evidence. R5 was used only as predecessor context.

A **DISTINCT_MANDATORY_GUARD** is one independently evaluated execution condition whose pass/fail
state is required by the runner. A failed member of a checked collection is component evidence within
that collection-level guard. A status calculated from lower-level guards is an aggregate summary.
Neither increases the distinct-guard count.

Every R6 route record uses one complete canonical schema with explicit `record_role`,
`parent_guard_id`, and `counts_as_distinct_guard` fields. The actual rebuilt taxonomy is:

| Record role | Count | Counting treatment |
|---|---:|---|
| `DISTINCT_MANDATORY_GUARD` | **35** | enters distinct-guard and C4 route-row counts |
| `COMPONENT_DETAIL` | **4** | G33-G36, parent G16; evidence only |
| `AGGREGATE_SUMMARY` | **1** | G40; non-distinct summary only |
| **All inventory records** | **40** | JSON/CSV inventory rows, not guard count |

Among the 35 distinct mandatory guards, 26 currently pass, six are genuine hard failures, and three
are historical-only authorities incompatible with a corrected-R10 route.

## 3. Corrected hard-failure and blocking taxonomy

Primary evidence confirms six current hard-FAIL guards:

1. **G07 — tracked/staged execute boundary:** execute mode requires zero changed tracked/staged
   paths; eight tracked files are modified and staged state is empty.
2. **G08 — untracked execute allowlist:** the pre-R6 repository has 34 untracked paths outside the
   execute-mode one-file allowlist boundary.
3. **G16 — protected identities:** the authority manifest's one collection-level loop finds 11
   mismatched protected identities. G33-G36 retain four important mismatch details but are explicitly
   `COMPONENT_DETAIL`, parent `G16`, and non-blocking as separate records.
4. **G17 — ignored-runtime set equality:** the manifest expects 449 ignored runtime/data paths; the
   current set has 459, with ten extras and no missing expected paths.
5. **G18 — ignored-runtime inventory hashes:** six manifest-pinned ignored artifacts have byte
   mismatches.
6. **G26 — HELPER19_SHA:** current 19a SHA `a139f1cd…` differs from 19b's historical pin
   `ad4f041a…`.

Three additional distinct guards pass only for the historical R9 route and fail corrected-R10
compatibility:

1. **G30 — accepted historical 19a authority**;
2. **G31 — historical runner routing authority**;
3. **G38 — historical EOB comparator authority**.

The corrected `blocking_guard_ids` is therefore exactly:

```
G07, G08, G16, G17, G18, G26, G30, G31, G38
```

This is **nine distinct blocking concepts**: six current hard failures plus three historical-only
corrected-route incompatibilities. It contains no G33-G36 component records and no G40 aggregate; no
self-reference is possible.

## 4. START_HEAD, tags, and repository boundaries

Fresh primary checks preserve the R5 corrections:

| Authority concept | Current evidence | Status |
|---|---|---|
| branch | `thesis-v7` | PASS |
| HEAD equals local `origin/thesis-v7` | both `b0372127…` | PASS |
| pre81 tag type | annotated `tag` | PASS |
| pre81 tag object | `2aeccf58…` | PASS |
| pre81 tag peel / START_HEAD | `b2acdf28…` | PASS |
| START_HEAD relationship | ancestor of current HEAD | PASS |
| production tag type | annotated `tag` | PASS |
| production tag object | `3c5feb22…` | PASS |
| production tag peel | current HEAD `b0372127…` | PASS |
| five live-remote refs | exact local/remote match | PASS |

START_HEAD is an ancestry/frozen-base requirement, not a current-HEAD equality requirement. The
`v7.2-pre81-ready` tag object and `v7.2-final81-runner-ready-r3` production-tag object are distinct
authority concepts. The tracked/staged boundary and untracked allowlist are separate mandatory guards.

## 5. Raw runner identity versus corrected-route compatibility

The raw 19b file remains byte-identical:

```
19b_raw_sha256 = 4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe
raw identity   = UNCHANGED
```

That file remains valid evidence for the historical R9 execution route. It is not executable authority
for corrected R10 because the nine distinct blockers above remain. R6 therefore preserves these
controlled sentinels for `FINAL81-CORRECTED-R10`:

```
production_runner_status  = NOT_YET_AUTHORIZED
production_runner_sha256  = NOT_YET_AUTHORIZED
runner_authority_manifest = NOT_YET_AUTHORIZED
production_tag_identity   = NOT_YET_AUTHORIZED
final81_preflight_identity = NOT_YET_AUTHORIZED
execution_route_status    = CURRENT_19B_NOT_COMPATIBLE_WITH_CORRECTED_R10_AUTHORITY_PINS
```

The route-status detail names only the nine distinct blocking concepts.

## 6. Rebuilt C4 and total difference matrix

C1-C3 were freshly schema/parity checked and retained because R6 changes none of their records or
primary-evidence bases. C4 was reconstructed from the corrected distinct-guard taxonomy, not obtained
by merely subtracting five from the R5 total:

| C4 content | Rows |
|---|---:|
| known specification differences | 9 |
| unchanged raw 19b identity | 1 |
| corrected-route compatibility | 1 |
| distinct mandatory guards | 35 |
| future-authority sentinels | 5 |
| other specification/parameter/unchanged fields | 26 |
| pending optimization responses | 11 |
| **C4 total** | **88** |

G33-G36 and G40 do not appear as C4 guard rows. The complete rebuilt matrix is:

| Comparison | Rows |
|---|---:|
| C1 — R1 to corrected-R10 EOB | 29 |
| C2 — corrected-R10 to winter-PV | 52 |
| C3 — corrected-R10 to 1 MW cost scale | 72 |
| C4 — historical R9 final81 to planned corrected final81 | **88** |
| **Total** | **241** |

The eleven future numerical rows retain `new_value=NOT_YET_EXECUTED`, `changed=UNKNOWN`,
`numerical_delta=NOT_APPLICABLE`, `relative_delta=NOT_APPLICABLE`, and
`change_type=OPTIMIZATION_RESPONSE`.

## 7. Architecture, schemas, and exact parity

The reverified architecture remains:

- eight semantic lineages;
- ten actual executions;
- 96 executed result records, partitioned 1 historical R1 EOB / 81 historical R9 final81 / six
  corrected-R10 mainline / two winter-PV / six accepted 1 MW;
- three future lineages with zero executions and zero result records.

The future comparison template remains `TEMPLATE_ONLY_NOT_EXECUTED_RESULT_EVIDENCE`.

Lineage, execution, result, difference, historical-evidence, and route-authority records each use one
deterministic complete schema. JSON and CSV are emitted from the same canonical records; every CSV cell
is canonical JSON, decoded with `json.loads`, and compared back to the source dictionary. Exact parity
passes for 8/8 lineage, 10/10 execution, 96/96 result, 241/241 difference, 8/8 historical evidence,
and 40/40 route inventory records. Every active lineage, execution, result, and difference row uses
`V7_2_PRODUCTION_VERSION_LINEAGE_FREEZE_CANDIDATE_R6`.

## 8. Historical evidence and reconstructibility

Fresh byte verification preserves the established evidence boundary:

- the pre-W-04 canonical input `e0d4a8e8…9fa0e` survives in the Gate-A preserved `before/` copy;
- the historical settlement interface `896f07e4…a4916` survives in the Gate-C preserved `before/`
  copy;
- the historical settlement matrix `31172c47…90e1` remains unavailable in the research artifact
  tree and reachable Git objects.

Code, input, execution-identity, full-state, and overall reconstructibility remain separately
classified. R1 and historical R9 are partially reconstructible because the matrix is unavailable; R1
also lacks a recoverable execution ID. Accepted corrected-R10 branches are reconstructible from current
hash-pinned bytes, subject to the existing working-tree/gitignored durability limitation. Future
lineages remain `NOT_APPLICABLE`.

## 9. Exact-D, W-07, demand-MAX, 1 MW, and 17d

Re-hashed R9/R10 core bytes retain the verified temporal ordering: historical core R9 lacks the
Exact-D tariff-facing encoding and uses the pre-W-07 cumulative-tier allocation; corrected core R10
contains Exact-D, the W-07 per-increment allocator, and the additional exact tariff-facing two-operand
MAX while retaining the reduced native maximum. These changes post-date the historical 81-case run.
This is a specification/timing finding, not a reopened methodology decision.

The original 1 MW completion manifest remains unmodified with its original candidate-pending-audit
status. The separate additive acceptance checkpoint continues to establish
`SENS-COST1MW-R10 = ACCEPTED_SENSITIVITY`.

17d was not executed. Its current route remains
`REPOSITORY_BOUNDARY_FROZEN_AGAINST_REINVOCATION`; the initial freeze chronology originates at
candidate v1, while R2-R6 are later additive provenance entries. This does not invalidate the accepted
1 MW result.

## 10. Repository non-mutation and package boundary

The pre-R6 state was branch `thesis-v7`, HEAD and local origin both `b0372127…`, zero staged paths,
eight tracked modifications, 34 untracked paths, and 42 porcelain records. After adding only the R6
checkpoint, the observed visible state is zero staged paths, the same eight tracked modifications,
35 untracked paths, and 43 porcelain records; the Git-ignored R6 package does not enter the untracked
inventory.

Protected hashes are unchanged:

- Framework: `bfe724a3…c8d5`;
- Registry: `8b72bd3f…021e`;
- corrected core R10: `9d828321…da8`;
- 19a: `a139f1cd…72d3`;
- 19b: `4abbda9d…2bbe`.

R6 contains 23 exact-byte snapshots of required untracked authority/support files and the unchanged
eight-path tracked patch (`71ea02b2…af6b`, 95,656 bytes). Its deterministic package manifest is built
only after this checkpoint exists, registers every non-manifest package file plus this external
checkpoint, verifies path/hash/byte triples, does not hash itself, and has no circular self-hash.

No optimize call, solver call, model construction, production rerun, corrected-final81 execution, SOC
sensitivity, commit, push, tag, reset, clean, stash, or checkout occurred.

## 11. Causal boundary and remaining limitations

All R1-to-R10 numerical effects remain observational. U01/U02/U03 and the M05 optimality-envelope
caution remain explicit; no correction receives unsupported unique causal attribution.

Remaining limitations are:

1. R6 is a **candidate**, not CLOSED or accepted, until independent cross-agent audit passes.
2. Corrected final81 remains unexecuted and lacks an authorized corrected runner/manifest/preflight
   route.
3. The historical settlement matrix remains unavailable.
4. Several accepted-current reconstruction artifacts remain working-tree/gitignored bytes rather than
   durable Git-history objects.
5. The repository boundaries intentionally remain failed/frozen; this provenance pass does not repair,
   bypass, or weaken them.
