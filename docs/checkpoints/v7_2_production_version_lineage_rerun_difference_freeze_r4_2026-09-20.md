# V7.2 Production Version Lineage / Rerun Difference Freeze — CANDIDATE R4

**Date:** 2026-09-20
**Package:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r4/`
**Status:** **CANDIDATE ONLY — NOT CLOSED, NOT ACCEPTED.** Requires independent cross-agent audit.
**Optimize calls:** 0 · **Model constructions:** 0 · **Git operations:** 0

---

## 1. Why R3 received STOP

| Finding | Status in R4 |
|---|---|
| **Blocker 1** — R3 treated raw 19b byte identity as evidence that the same route could execute corrected final-81 after only a 19a repin. | **Removed and replaced.** See §2–§3. |
| **Blocker 2** — JSON/CSV "full structural parity" was falsely reported (lineage 0/8, execution 1/10 exact). | **Fixed.** Canonical schemas + exact round-trip, §6. |
| **Defect 3** — records carried stale `CANDIDATE_R2_RECOVERY` package identity. | **Fixed.** Every record carries `provenance_package = …CANDIDATE_R4`, §7. |
| **Defect 4** — historical reconstructibility overstated the missing evidence. | **Fixed.** Two of three historical inputs survive; only the matrix is missing, §4–§5. |

All four findings are accepted, not debated.

Predecessors: **v1 = STOP**, **R2 = STOP**, **R3 = STOP** — all three preserved byte-identical as
historical provenance candidates. R4 uses new paths only; nothing in v1/R2/R3 was edited.

---

## 2. Why unchanged 19b bytes do **not** mean corrected-run compatibility

`scripts/19b_run_final_layer_a_81_cases.py` is byte-identical to the runner that executed the
historical R9 surface. **That is file identity, not executable authority compatibility.** Reading
19b's own module constants (lines 38–49) and comparing them against the live repository:

| 19b hard pin | Pinned value | Current state | Compatible? |
|---|---|---|---|
| `HELPER19_SHA` (19a) | `ad4f041a…` *(historical 19a)* | `a139f1cd…` *(corrected 19a)* | **No** |
| `START_HEAD` / `tag_peeled` | `b2acdf28…` *(pre81-ready)* | `b0372127…` | **No** |
| `TAG_OBJECT` | `2aeccf58…` | `3c5feb22…` | **No** |
| `CHECKPOINT_SHA` | `08b1fef4…` | `08b1fef4…` | yes |
| `RUNNER_AUTHORITY` manifest | `final_81_production_runner_authority_v7_2_2026-09-11.json` | pinned to the **historical** runner identity | **No** |
| `PREFLIGHT` / `PREFLIGHT_SHA` | historical preflight run `20260909T170841521430Z_55cc09a45f` | no corrected preflight run exists | **No** |
| `--execute-production` tracked-change rule | **zero** tracked changes required | 8 tracked modifications, including the corrected r10 core itself | **No** |

**The decisive point:** 19b pins `HELPER19_SHA` to the **historical** 19a. Repinning 19a — R3's
proposed single change — would **break 19b's own pin** and make the route *strictly less* runnable,
not more. R3's claim is therefore removed entirely from R4.

---

## 3. Corrected final-81 production route: NOT_YET_AUTHORIZED

Recorded on the `FINAL81-CORRECTED-R10` lineage node and in the working-tree snapshot:

```
production_runner_status      = NOT_YET_AUTHORIZED
production_runner_sha256      = NOT_YET_AUTHORIZED
runner_authority_manifest     = NOT_YET_AUTHORIZED
production_tag_identity       = NOT_YET_AUTHORIZED
final81_preflight_identity    = NOT_YET_AUTHORIZED
execution_route_status        = CURRENT_19B_NOT_COMPATIBLE_WITH_CORRECTED_R10_AUTHORITY_PINS
```

and separately, as facts rather than a single conflated claim:

```
historical_19b_raw_byte_identity        = UNCHANGED
current_corrected_final81_route_status  = NOT_YET_AUTHORIZED
```

A **separately authorized future gate** must establish runner identity, helper/preflight identity,
the authority manifest, the required SHA pins, and production tag/checkpoint identity. **None of
that was done here.** `19a` and `19b` were not modified, no pins were updated, no tag was created,
no authority manifest was touched.

### C4 row treatment

C4 now carries **two disjoint row families**, exactly as required:

| field | old | new | changed |
|---|---|---|---|
| `19b_raw_file_sha256` | `4abbda9d…` | `4abbda9d…` | **false** — bytes unchanged; file identity only |
| `final81_execution_route_compatibility` | `VALID_FOR_HISTORICAL_R9_PRODUCTION` | `NOT_YET_AUTHORIZED_FOR_CORRECTED_R10` | **true** |

plus one row per individual pin and per unestablished route component, all under the new category
`EXECUTION_ROUTE_AUTHORITY`. The unchanged-bytes row explicitly states it must not be read as route
compatibility.

---

## 4. Historical evidence that **survives**

Re-derived by hashing every file in the working tree (9,277 files scanned) rather than assuming:

| Artifact | Expected SHA | Surviving location |
|---|---|---|
| Historical canonical input (pre-W-04) | `e0d4a8e8…` | `results/data_audit/gate_a_w04_w18/20260914T144406Z/before/annual_input_v7_1.parquet` |
| Historical settlement interface | `896f07e4…` | `results/data_audit/gate_c_dependency_refresh/20260915T073204Z/before/taipower_transition_period_settlement_interface_v7_2.json` |
| Core r1 | `448235d3…` | Git object at commit `ae31d136` |
| Core r9 | `d145eeb0…` | Git object at commit `6916fa5a` |
| Runner 15b | `9a5f61d1…` | Git object at commit `c054814d` |
| Historical 19a | `ad4f041a…` | Git object at `HEAD` |
| Runner 19b | `4abbda9d…` | tracked, unmodified at `HEAD` |

Both preserved `before/` copies were **re-hashed and matched exactly**.

## 5. Historical evidence still **missing**

| Artifact | Expected SHA | Status |
|---|---|---|
| Historical settlement **matrix** | `31172c47…` | **NOT FOUND** in any working-tree file or Git object |

This is the **sole** limiting artifact. `historical_evidence_inventory.json` records every component
with role, expected SHA, surviving path, surviving SHA, availability status, whether it is required,
and its limiting consequence.

### Corrected reconstructibility axes

| Lineage | Code | Input | Exec identity | Full state | Overall | Limiting axis |
|---|---|---|---|---|---|---|
| MAINLINE-HIST-R1 | FULL | **PARTIAL** | NOT_RECONSTRUCTIBLE | **PARTIAL** | PARTIAL | INPUT *(missing settlement matrix)* + execution identity |
| MAINLINE-HIST-R9-FINAL81 | FULL | **PARTIAL** | FULL | **PARTIAL** | PARTIAL | INPUT *(missing settlement matrix only)* |
| three R10 lineages | FULL | FULL | FULL | FULL | FULL | NOT_APPLICABLE |
| three future branches | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |

R3 said "all historical input bytes are absent." That was wrong: two of three components survive.
R4 records `PARTIALLY_RECONSTRUCTIBLE` on the input and full-state axes and names the single missing
component.

---

## 6. JSON / CSV parity — now exact

A **canonical schema is declared per record family before serialization**; every record in a family
carries that exact key set, with controlled sentinels (`NOT_APPLICABLE`, `NOT_YET_EXECUTED`,
`NOT_YET_AUTHORIZED`, `UNKNOWN`, `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE`) rather than absent
keys or bare nulls. JSON and CSV are generated from the **same** in-memory records, so absent-key
versus null mismatches are structurally impossible.

| Family | Records exactly equal | Status |
|---|---|---|
| lineage ledger | **8 / 8** | PASS |
| execution ledger | **10 / 10** | PASS |
| result records | **96 / 96** | PASS |
| difference matrix | **212 / 212** | PASS |
| historical evidence inventory | **8 / 8** | PASS |

## 7. Package identity consistency

Every lineage, execution, result and difference record carries
`provenance_package = "V7_2_PRODUCTION_VERSION_LINEAGE_FREEZE_CANDIDATE_R4"`. No active R4 record
carries `CANDIDATE_R2_RECOVERY` or `candidate_r3`. R2/R3 appear only where they are the subject —
in the predecessor blocks and the protected-rehash entries that verify them unmodified.

## 8. Re-verified architecture and difference counts

8 lineages · 10 executions · **96** executed results (1 / 81 / 6 / 2 / 6), all 96 artifacts
re-hashed. Future lineages hold zero executions and zero results. `.staging` excluded. No self-parent,
acyclic, single supersession edge (`MAINLINE-HIST-R1 → MAINLINE-CORRECTED-R10`); R9 final-81 keeps
`superseded_by = NOT_YET_APPLICABLE`.

| Comparison | Rows |
|---|---|
| `C1_R1_TO_R10_EOB` | 29 |
| `C2_R10_TO_WINTERPV` | 52 |
| `C3_R10_TO_COST1MW` | 72 |
| `C4_R9FINAL81_TO_FINAL81CORRECTED_SPECIFICATION` | **59** |
| **Total** | **212** |

C4 = 9 specification differences + 13 execution-route/authority rows + 26 meaningfully-unchanged
rows + 11 pending result rows. The R3 total of 204 is **not** forced; routing expansion changed it.

Retained and re-verified: Exact-D and W-07 both landed **after** the historical surface (verified
from r9 versus r10 core bytes); 1 MW acceptance; 17d boundary-frozen state; exact-byte snapshots
(23 files, patch reproduces `git diff HEAD`); the R1→R10 observational causal boundary with
U01/U02/U03 and the M05 caution; non-circular package manifest.

## 9. 17d status (retained, re-verified)

Completed 1 MW run **VALID / ACCEPTED**; current route
**`REPOSITORY_BOUNDARY_FROZEN_AGAINST_REINVOCATION`**. The freeze began when the **candidate v1**
checkpoint added an untracked file outside 17d's frozen `EXPECTED_UNTRACKED` inventory; v1 predates
R2, R3 and R4. Intentional fail-closed behaviour, not repository damage. 17d was not modified and
not re-run.

## 10. Protected rehash

`protected_rehash_scope = REPORTING_SUBSET`, `protected_rehash_count = 41` — expanded to include
the two preserved historical `before/` copies, the final-81 runner-authority manifest, the
pre81 production checkpoint, six runner identities, and the v1/R2/R3 manifests. All re-hashed, zero
mismatches. Separately recorded: all 96 Level-3 result artifacts hashed; historical blobs re-hashed
from Git.

---

## 11. Remaining limitations

1. **R4 is a candidate**, not authority; independent cross-agent audit is still required.
2. The corrected final-81 production route is **NOT_YET_AUTHORIZED**; C4 is a specification and
   route-authority comparison only, and all numerical 81-case result differences remain
   `NOT_YET_EXECUTED`.
3. C4 compares the *planned* corrected specification; if the corrected surface eventually runs under
   different authorities, C4 must be re-derived against what actually ran.
4. Historical R1/R9 remain `PARTIALLY_RECONSTRUCTIBLE`, limited solely by the missing historical
   settlement matrix (`31172c47…`).
5. The historical EOB execution identity is unrecoverable.
6. `U01`/`U02`/`U03` remain unresolved; `U02` needs counterfactual solves that do not exist and are
   not authorized.
7. R1→R10 differences are observational only; no per-correction attribution.
8. C2/C3 reuse each run's frozen paired-comparison artifact as source evidence; not recomputed from
   dispatch.
9. R10 input bytes are gitignored and protected only by the working tree.
10. The 17d route stays boundary-frozen pending separately authorized alignment.
11. The preserved historical `before/` copies live under `results/`, which is gitignored — they are
    protected only by the working tree, not by Git history.

## 12. Non-mutation

Candidate v1, R2 and R3, Framework, Registry, corrected core, all inputs, all historical/corrected/
accepted results, both original completion manifests, the 1 MW acceptance checkpoint, `19a` and `19b`
are **all byte-identical**. Only new additive R4 files were created.

- Optimize calls: **0** · model constructions: **0**
- Commit / push / tag / reset / clean / stash / checkout: **0**
- Branch `thesis-v7`, HEAD = `origin/thesis-v7` = `b03721275c73b05d45517bdf84c1e0bd03833376`, staged = 0
