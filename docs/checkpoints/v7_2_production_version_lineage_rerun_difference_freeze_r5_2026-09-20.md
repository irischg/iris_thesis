# V7.2 Production Version Lineage / Rerun Difference Freeze — Candidate R5

**Artifact class:** additive provenance correction candidate; implementation correction only.  
**Date:** 2026-09-20  
**Package:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r5/`  
**Status:** **CANDIDATE ONLY — NOT CLOSED / NOT ACCEPTED — pending independent cross-agent audit**

No methodology, model, data, parameter, runner, result, completion manifest, authority manifest,
commit or tag was changed. Candidate v1, R2, R3 and R4 remain immutable historical provenance
candidates with verdict **STOP**. R5 is a new additive candidate only.

## 1. Governing R4 STOP and scope of this correction

The independent R4 audit is the corrective basis. R4's overall conclusion was correct:

```
FINAL81-CORRECTED-R10 = NOT_YET_AUTHORIZED
```

R4 nevertheless received **STOP** because its C4 route evidence contained three defects:

1. it treated `START_HEAD` as if current `HEAD` had to equal it;
2. it compared the `v7.2-pre81-ready` tag-object pin with the distinct production-tag object;
3. it omitted the execute-mode untracked-file allowlist.

R5 rebuilds the route authority from `scripts/19b_run_final_layer_a_81_cases.py`, current repository
bytes, local and live-remote Git refs, manifests and preserved artifacts. R4 prose is not used as
primary authority.

## 2. Correct Git and tag semantics

The actual 19b conditions and their current states are:

| Authority concept | Expected | Current | Result |
|---|---|---|---|
| branch | `thesis-v7` | `thesis-v7` | PASS |
| current HEAD equals `origin/thesis-v7` | `b0372127…` | `b0372127…` | PASS |
| `v7.2-pre81-ready` is annotated | `tag` | `tag` | PASS |
| pre81 tag object | `2aeccf58…` | `2aeccf58…` | PASS |
| pre81 tag peel | `START_HEAD=b2acdf28…` | `b2acdf28…` | PASS |
| `START_HEAD` ancestry | ancestor of current HEAD | confirmed | PASS |
| production tag is annotated | `tag` | `tag` | PASS |
| production tag peel | current HEAD | `b0372127…` | PASS |
| five live-remote refs | exact local values | exact match | PASS |

`START_HEAD` is therefore an **ancestry/frozen-base condition**, not a demand that current HEAD equal
the pre81 commit. The pre81 tag object `2aeccf58…` and production tag object `3c5feb22…` are two
different authority identities. Both currently pass their own actual guards and neither is cited as a
corrected-R10 blocker.

## 3. Complete static 19b route inventory

`final81_route_authority_guard_inventory.json/.csv` records **40 separately identified guard
concepts** using one canonical schema. Static results are:

- 26 `PASS`;
- 11 `FAIL`;
- 3 `PASS_HISTORICAL_R9_ONLY_FAIL_CORRECTED_R10`.

The true current blocker families are:

1. **HELPER19 pin:** current 19a SHA `a139f1cd…` differs from 19b's historical
   `HELPER19_SHA=ad4f041a…`. Changing 19a alone cannot satisfy the unchanged 19b pin.
2. **Tracked execute boundary:** execute mode requires zero tracked/staged changes; current accepted
   state has eight tracked modifications.
3. **Untracked execute boundary:** execute mode permits only
   `docs/protocols/iris_thesis_rigorous_audit_skill.md`; the pre-R5 repository has 33 untracked
   paths, so this separate guard fails.
4. **Historical protected identities:** the historical authority manifest has 11 exact-byte
   mismatches against the corrected repository, including core, canonical input, settlement
   interface/matrix, helper and accepted correction sources.
5. **Ignored-runtime boundary:** the manifest expects 449 ignored runtime/data paths; current state
   has 459, including 10 extra paths, and six pinned ignored artifacts have byte mismatches.
6. **Historical route authority:** the accepted-19a, preflight and routing manifest describe the R9
   route, not corrected R10.
7. **Historical comparator:** 19b routes the historical EOB comparator rather than the accepted
   corrected-R10 EOB authority.

The historical checkpoint, preflight, committed 19b/manifest bytes, grid, solver fingerprint,
mainline economic package, kappa and physical constants remain internally valid. Their passing state
does not create a corrected-R10 production route.

## 4. Raw runner identity is not execution compatibility

```
19b_raw_file_sha256 = 4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe
raw byte identity   = UNCHANGED
```

Separately:

```
historical route = VALID_FOR_HISTORICAL_R9_PRODUCTION
corrected route  = NOT_YET_AUTHORIZED_FOR_CORRECTED_R10
```

The second conclusion is supported only by the true blockers above, not by the passing START_HEAD,
pre81-tag, production-tag, checkpoint or HEAD/origin conditions.

## 5. FINAL81-CORRECTED-R10 remains future-only

The lineage retains controlled sentinels:

```
production_runner_status   = NOT_YET_AUTHORIZED
production_runner_sha256   = NOT_YET_AUTHORIZED
runner_authority_manifest  = NOT_YET_AUTHORIZED
production_tag_identity    = NOT_YET_AUTHORIZED
final81_preflight_path/SHA  = NOT_YET_AUTHORIZED
execution_route_status     = CURRENT_19B_NOT_COMPATIBLE_WITH_CORRECTED_R10_AUTHORITY_PINS
```

It has zero executions, zero results, zero result hashes and no numerical objective, `E_N`, `P_B` or
`CC`. The 81-case comparison template remains
`TEMPLATE_ONLY_NOT_EXECUTED_RESULT_EVIDENCE` and is excluded from executed-result counts.

## 6. Architecture and rebuilt comparison counts

R5 retains the independently reverified architecture:

- 8 semantic lineages;
- 10 executions;
- 96 executed results: 1 historical R1 EOB, 81 historical R9 final81, 6 corrected-R10 accepted
  mainline results, 2 winter-PV results, and 6 accepted 1 MW results;
- three future lineages with zero executions/results.

The rebuilt one-field-per-row difference matrix contains:

| Comparison | Rows |
|---|---:|
| C1 — R1 to corrected-R10 EOB | 29 |
| C2 — corrected-R10 to winter-PV | 52 |
| C3 — corrected-R10 to 1 MW cost scale | 72 |
| C4 — historical R9 final81 to planned corrected final81 | **93** |
| **Total** | **246** |

C4 consists of nine specification differences, one unchanged raw-runner row, one route-compatibility
summary, 40 separately enumerated authority concepts, five future-authority sentinel rows, 26 other
specification/parameter rows, and 11 pending optimization-result rows.

## 7. Canonical schema and exact JSON/CSV parity

Every record within each family uses one complete deterministic key set. Semantic absence is encoded
with controlled sentinels; the six nested execution-setting nulls inherited from R4 were normalized
to `NOT_APPLICABLE` or `INFINITY_UNSET` in R5. JSON and CSV are emitted from the same canonical
in-memory records; every CSV cell contains canonical JSON encoding and is independently decoded for
exact dictionary comparison.

Completed verification covers:

- lineage: 8/8;
- execution: 10/10;
- result: 96/96;
- difference: 246/246;
- historical evidence: 8/8;
- route-authority guard inventory: 40/40.

Every active lineage, execution, result and difference record uses
`V7_2_PRODUCTION_VERSION_LINEAGE_FREEZE_CANDIDATE_R5`.

## 8. Historical reconstructibility and timing

Fresh hashing confirms:

- historical canonical input `e0d4a8e8…9fa0e` survives in the W-04/W-18 preserved `before/` copy;
- historical settlement interface `896f07e4…a4916` survives in the Gate-C preserved `before/` copy;
- historical settlement matrix `31172c47…90e1` is absent from the working tree and reachable Git
  blobs.

Accordingly, R1 and R9 remain partially reconstructible because historical input state is incomplete;
R1 additionally lacks a reconstructible execution ID. Accepted R10 branches are currently fully
reconstructible from hash-pinned bytes, subject to the disclosed working-tree/gitignored durability
limitation. Future branches remain `NOT_APPLICABLE`.

Historical core-object comparison continues to show Exact-D absent in R9 and active in R10, W-07
changing from cumulative-tier to per-increment allocation, and the billing-demand/MAX formulation
changing after the historical 81-case execution.

## 9. Accepted sensitivities and causal boundary

The original 1 MW completion manifest remains byte-identical with status
`CANDIDATE_PASS_PENDING_INDEPENDENT_POST_RUN_AUDIT`; the separate additive acceptance checkpoint
continues to support `SENS-COST1MW-R10 = ACCEPTED_SENSITIVITY`.

17d remains `REPOSITORY_BOUNDARY_FROZEN_AGAINST_REINVOCATION`. Candidate v1 created the first
boundary mismatch; R2/R3/R4/R5 are later additive provenance entries. This does not invalidate the
already accepted 1 MW run.

All R1-to-R10 numerical effects remain observational. U01/U02/U03 and the M05 optimality-envelope
caution remain explicit; no correction receives an unsupported unique causal attribution.

## 10. Package boundary and remaining limitations

R5 uses exact-byte snapshots of 23 untracked authority/support files plus the unchanged tracked patch.
Its deterministic manifest does not hash itself and separately registers this external checkpoint.
Actual file, registry and protected-rehash counts are recorded in `package_manifest.json` after final
construction and verified rather than assumed from R4.

Remaining limitations:

1. R5 is a **candidate**, not CLOSED or accepted, until independent cross-agent audit passes.
2. Corrected final81 remains unexecuted and lacks an authorized runner/manifest/preflight route.
3. The historical settlement matrix remains unavailable.
4. Several accepted-current reconstruction artifacts exist only as working-tree/gitignored bytes;
   current reconstructibility is stronger than durable Git-history reconstructibility.
5. No SOC sensitivity, corrected-final81 run, model construction or optimization was performed.
