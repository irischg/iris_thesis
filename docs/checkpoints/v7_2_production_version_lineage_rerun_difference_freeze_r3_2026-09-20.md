# V7.2 Production Version Lineage / Rerun Difference Freeze — CANDIDATE R3

**Date:** 2026-09-20
**Package:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r3/`
**Status:** **CANDIDATE ONLY — NOT CLOSED, NOT ACCEPTED.** Requires independent cross-agent audit.
**Optimize calls:** 0 · **Model constructions:** 0 · **Git operations:** 0

---

## 1. Predecessor candidates — both preserved, both STOP

| Candidate | Status | Disposition |
|---|---|---|
| **v1** — `docs/checkpoints/v7_2_production_version_lineage_rerun_difference_freeze_2026-09-20.md` + `results/provenance/v7_2_production_version_lineage_freeze_candidate/` | **STOP · HISTORICAL_PROVENANCE_ONLY** | Preserved byte-identical. Not modified. |
| **R2** — `docs/checkpoints/v7_2_production_version_lineage_rerun_difference_freeze_r2_2026-09-20.md` + `results/provenance/v7_2_production_version_lineage_freeze_candidate_r2/` | **STOP · HISTORICAL_PROVENANCE_ONLY** | Preserved byte-identical. Not modified. |
| **R3** — this package | **CANDIDATE** | Rebuilt from primary repository and run evidence; R2 used only as historical context. |

R3 uses new paths throughout. No R2 path was reused, overwritten or patched in place.

### R2 package facts, corrected

The R2 narrative stated "34 files in the R2 provenance directory." That figure was wrong. The correct facts:

- R2 directory contains **35 files**;
- `package_manifest.json` is **one of those 35**;
- its artifact registry covers **36 artifacts**;
- composition = **34 non-manifest files inside the R2 directory + 2 external checkpoints**;
- the manifest **does not register itself**, therefore **no circular self-hash exists**.

The R2 manifest *structure* was sound; only the narrative count was wrong.

---

## 2. Three-level architecture (unchanged, re-derived from primary evidence)

8 semantic lineages · 10 executions · **96** executed result records. No self-parent, acyclic, one
lineage node per *version* rather than per execution.

```
MAINLINE-HIST-R1                    superseded_by → MAINLINE-CORRECTED-R10
└── MAINLINE-HIST-R9-FINAL81        superseded_by → NOT_YET_APPLICABLE
    └── MAINLINE-CORRECTED-R10      CURRENT ACCEPTED MAINLINE AUTHORITY
        ├── SENS-WINTERPV-R10       ACCEPTED_SENSITIVITY   (branch)
        ├── SENS-COST1MW-R10        ACCEPTED_SENSITIVITY   (branch)
        ├── SENS-SOC2080-R10        NOT_YET_EXECUTED
        ├── FINAL81-CORRECTED-R10   NOT_YET_EXECUTED
        └── ROBUST-A2-R10           NOT_YET_EXECUTED
```

Result partition: R1 EOB 1 · R9 final81 81 · corrected R10 6 · winter-PV 2 · 1 MW 6 = **96**.
Future lineages hold **zero** executions and **zero** result records. C4 creates no result records.

---

## 3. NEW: C4 — historical R9 final-81 → future corrected R10 final-81

This is the R2 blocker, now closed. C4 is a **SPECIFICATION comparison**, not a result comparison.

**51 rows: 12 changed · 28 meaningfully unchanged · 11 numerical-result fields PENDING.**

### 3.1 The 12 known specification differences

| Category | Field | R9 final-81 | Planned corrected R10 final-81 |
|---|---|---|---|
| IMPLEMENTATION_ONLY | `core_version_string` | `…reduced-native-max-2026-09-06-r9` | `…exact-d-preflight-2026-09-16-r10` |
| IMPLEMENTATION_ONLY | `core_sha256` | `d145eeb0…` | `9d828321…` |
| IMPLEMENTATION_ONLY | `core_source_line_count` | 2668 | 2749 (+134 / −53) |
| DATA | `canonical_input_sha256` | `e0d4a8e8…` (pre-W-04) | `9142b8b6…` (W-04 corrected) |
| PREPROCESSING | `settlement_interface_sha256` | `896f07e4…` | `f101af47…` |
| PREPROCESSING | `settlement_matrix_sha256` | `31172c47…` | `ed7f8dbf…` |
| **MODEL_EQUATION** | `exact_d_tariff_facing_encoding` | **ABSENT in core r9** | **ACTIVE in core r10** |
| **CONSTRAINT_SEMANTICS** | `overcontract_tier_semantics` | **cumulative tier-1 allowance (pre-W-07)** | **W-07 per-increment tier allocation** |
| MODEL_EQUATION | `billing_demand_max_formulation` | reduced native MAX only | reduced native MAX **+** exact 2-operand tariff-facing max |
| IMPLEMENTATION_ONLY | `final81_preflight_sha256` (19a) | `ad4f041a…` | `a139f1cd…` |
| PROVENANCE_ONLY | 19a pinned `CORE_SHA` | `d145eeb0…` | `9d828321…` |
| PROVENANCE_ONLY | 19a pinned `CANONICAL_SHA` | `e0d4a8e8…` | `9142b8b6…` |

**These were verified from bytes, not inferred from version strings.** Re-hashing the r9 core blob
from Git object `6916fa5a` and diffing it against the working-tree r10 core shows the Exact-D marker
(`demand_exact_link_` / `demand_exact_max_`) is **absent in r9 and present in r10**, and that r9
builds `cum_tier1_{month}_{period}_kw` bounded by `tier_cumulative_ub` while r10 builds
`incr_tier1_{month}_{period}_kw` bounded by `tier_increment_ub` and adds the frozen
`overcontract_tier_split()` single-source allocator.

**Consequence of record: both Exact-D and W-07 landed AFTER the historical 81-point surface ran.**
The historical surface therefore predates both corrections.

### 3.2 What did NOT change (28 rows)

The final-81 **production runner 19b is byte-identical** (`4abbda9d…`, tracked and unmodified) — the
corrected surface would use the same runner, repinned only through 19a. Also unchanged: the 14a
economic interface (`9277d310…`), the PNNL 10 MW package object (`b8c461eb…`), the optimization
tariff (`5c1582d8…`), κ, SOC 0.10–0.90, usable SOC 0.80, η_c/η_d 0.90/0.90, degradation breakpoints
and 1:3:4 λ ratio and C_rep, the rainflow validator (`4ae83643…`), the constant worst-case reserve
floor (`layer_a_reserve_floor_t` present in **both** r9 and r10), constant NTD-2023 / real 5% /
20-year / CRF, binary formulation and 1e-6 MIPGap, `FRESH_RUN_ONLY`, mainline conservative-zero
winter-PV on both sides, the 81-case count, and the solver environment (gurobipy 13.0.1, numpy
2.4.4, pandas 3.0.2).

> **Correction to the R2 audit's working list.** That list named `default_runner_path` and
> `default_runner_sha256` as R9→R10 differences. They are not: those fields were being read off the
> *EOB/representative* runners. On the final-81 axis the production runner is 19b in both cases and
> is unchanged. The real runner-side difference is 19a, the preflight that supplies 19b's pinned
> constants.

### 3.3 Numerical 81-case results remain PENDING

Eleven result fields — objective, E_N, P_B, CC, energy, basic, pure over-contract, transition
over-contract, degradation, annualized CAPEX, FOM — are recorded with
`new_value = NOT_YET_EXECUTED`, `numerical_delta = NOT_APPLICABLE`,
`relative_delta = NOT_APPLICABLE`, `changed = UNKNOWN`,
`change_type = OPTIMIZATION_RESPONSE`, and the boundary *"No numerical historical-to-corrected
final81 claim is permitted until the corrected 81-case production surface is executed and
independently accepted."* **No numerical delta was fabricated.**

`c4_future_case_comparison_template.json` lists the 81 matched case ids for future population and is
explicitly marked `TEMPLATE_ONLY_NOT_EXECUTED_RESULT_EVIDENCE`.

---

## 4. Difference matrix totals

| Comparison | Rows |
|---|---|
| `C1_R1_TO_R10_EOB` | 29 |
| `C2_R10_TO_WINTERPV` | 52 |
| `C3_R10_TO_COST1MW` | 72 |
| `C4_R9FINAL81_TO_FINAL81CORRECTED_SPECIFICATION` | **51** |
| **Total** | **204** |

Schema, controlled taxonomy, `(new−old)/|old|` convention, zero-denominator and non-numeric sentinel
handling are unchanged from R2. The R1→R10 causal guard is retained: differences are observational,
sourced from the accepted R3 delta authority, with U01/U02/U03 carried as `NOT_COMPARED` and the M05
optimality-envelope caution preserved.

---

## 5. Reconstructibility — axis decomposition (R2 defect corrected)

Every lineage now carries `code_reconstructibility`, `input_reconstructibility`,
`execution_identity_reconstructibility`, `full_execution_state_reconstructibility`, an explicit
`reconstructibility_limiting_axis`, and a note per axis.

| Lineage | Code | Input | Exec identity | Full state | Overall | Limiting axis |
|---|---|---|---|---|---|---|
| MAINLINE-HIST-R1 | **FULL** | NOT_RECONSTRUCTIBLE | NOT_RECONSTRUCTIBLE | NOT_RECONSTRUCTIBLE | PARTIAL | **INPUT** (and execution identity) |
| MAINLINE-HIST-R9-FINAL81 | **FULL** | NOT_RECONSTRUCTIBLE | FULL | NOT_RECONSTRUCTIBLE | PARTIAL | **INPUT** |
| MAINLINE-CORRECTED-R10 | FULL | FULL | FULL | FULL | FULL | NOT_APPLICABLE |
| SENS-WINTERPV-R10 | FULL | FULL | FULL | FULL | FULL | NOT_APPLICABLE |
| SENS-COST1MW-R10 | FULL | FULL | FULL | FULL | FULL | NOT_APPLICABLE |
| three future branches | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |

**The R2 error is corrected.** Historical code is **fully reconstructible**: core r1 (`448235d3…`)
survives at Git commit `ae31d136`, core r9 (`d145eeb0…`) at `6916fa5a`, runner 15b (`9a5f61d1…`) at
`c054814d`, and runner 19b (`4abbda9d…`) is tracked at HEAD — all four re-hashed from Git objects
during this build. The limiting axis is **INPUT**: `data/` and `data/reference/` are gitignored, so
the pre-W-04 canonical input (`e0d4a8e8…`) and the historical settlement interface (`896f07e4…`) and
matrix (`31172c47…`) exist in no Git object and no working-tree copy. "Absent from the working tree"
is no longer used as evidence of irreconstructibility anywhere in this package.

*Durability caveat recorded for the R10 lineages:* their inputs are present and hash-pinned but also
gitignored, so they are protected only by the working tree, not by Git history.

---

## 6. 17d execution route — boundary-frozen, durably recorded

Recorded in the working-tree snapshot and on the `SENS-COST1MW-R10` lineage node
(`execution_route_status`):

- completed 1 MW run: **VALID / ACCEPTED**, unaffected;
- current 17d route: **`REPOSITORY_BOUNDARY_FROZEN_AGAINST_REINVOCATION`**;
- mechanism: 17d pins a frozen `EXPECTED_UNTRACKED` inventory, and the live untracked inventory now
  contains provenance checkpoints absent from it, so `repository_authority()` fails closed **before
  any solve**;
- **timing, accurately:** the freeze already existed once the **candidate v1** checkpoint was created
  — v1 predates R2. R2 added two further checkpoint entries and **did not originate the freeze**;
  R3 adds its own, widening the same pre-existing divergence;
- this is **intentional fail-closed behaviour, not repository damage**, and does not invalidate the
  completed accepted run;
- a future re-run requires **separately authorized boundary alignment**.

17d was **not modified** and **not re-run** by this gate; the state was established statically.

---

## 7. Protected rehash — explicitly scoped

`protected_rehash_manifest.json` carries `protected_rehash_scope = REPORTING_SUBSET` and
`protected_rehash_count = 35`, with an explicit note that it is **not** the complete universe of
protected bytes. It was expanded from R2's 18 to cover Framework, Registry, corrected core, rainflow
validator, historical EOB result **and** freeze audit, R9 final-81 run/completion/pre-solve-gate/case
matrix, corrected EOB result and manifest, winter-PV completion and manifest and input, 1 MW
completion/manifest/pre-solve-gate and its acceptance checkpoint, the R3 delta authority and its
package manifest, canonical input, economic/tariff/settlement authorities, all three PNNL parameter
files, and six runner identities (15d, 16a, 17c, 17d, 19a, 19b).

Separately recorded under `additional_authority_evidence_verified_during_build`: **all 96 Level-3
result artifacts** were hashed, the historical core and runner blobs were re-hashed from Git, and
both prior candidates were verified unmodified. Per-case result hashes are therefore **not** absent —
they are covered by the result records rather than duplicated into the protected subset.

---

## 8. 1 MW acceptance retained

Neither the original completion manifest nor the R2-created acceptance checkpoint was modified. Both
were rehashed and are referenced. The original still reads
`CANDIDATE_PASS_PENDING_INDEPENDENT_POST_RUN_AUDIT`; the separate acceptance checkpoint remains the
repository evidence for `SENS-COST1MW-R10 = ACCEPTED_SENSITIVITY`.

---

## 9. JSON / CSV semantic parity

Canonical-JSON cell encoding; verified by decoding every cell and comparing reconstructed records for
**full structural equality**, not row counts.

| Pair | Records | CSV rows | Columns | Round-trip |
|---|---|---|---|---|
| lineage ledger | 8 | 8 | 58 | **PASS** |
| execution ledger | 10 | 10 | 26 | **PASS** |
| result records | 96 | 96 | 15 | **PASS** |
| difference matrix | 204 | 204 | 16 | **PASS** |

---

## 10. Limitations

1. **R3 is a candidate**, not authority; it requires independent cross-agent audit.
2. **C4 is a specification comparison only.** No corrected 81-point surface exists; all numerical
   81-case result differences remain `NOT_YET_EXECUTED`.
3. C4 compares the *planned* corrected specification. If the corrected surface is eventually executed
   under different authorities, C4 must be re-derived against what actually ran.
4. Historical R1 and R9 remain `PARTIALLY_RECONSTRUCTIBLE`, limited by **input** bytes that no Git
   object preserves.
5. The historical EOB execution identity is unrecoverable.
6. `U01`/`U02`/`U03` remain unresolved; `U02` would require isolated counterfactual solves that do
   not exist and are not authorized.
7. R1 → R10 differences are observational only; no per-correction attribution is made.
8. Sensitivity rows (C2/C3) reuse each run's frozen paired-comparison artifact as source evidence;
   they were not recomputed from dispatch.
9. The R10 lineages' input bytes are gitignored and protected only by the working tree.
10. The 17d route stays boundary-frozen until a separately authorized alignment.

---

## 11. Non-mutation

Candidate v1, candidate R2, Framework, Registry, corrected core, all inputs, all accepted and
historical result artifacts, the original 1 MW completion manifest and the 1 MW acceptance checkpoint
are **all byte-identical**. Only new additive R3 files were created.

- Optimize calls: **0** · model constructions: **0**
- Commit / push / tag / reset / clean / stash / checkout: **0**
- Branch `thesis-v7`, HEAD = `origin/thesis-v7` = `b03721275c73b05d45517bdf84c1e0bd03833376`, staged = 0
