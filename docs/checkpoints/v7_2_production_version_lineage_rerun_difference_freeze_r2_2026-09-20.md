# V7.2 Production Version Lineage / Rerun Difference Freeze — R2 RECOVERY CANDIDATE

**Date:** 2026-09-20
**Package:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r2/`
**Status:** **CANDIDATE ONLY — NOT CLOSED, NOT ACCEPTED.** Requires independent cross-agent audit.
**Optimize calls:** 0 · **Model constructions:** 0 · **Git operations:** 0

---

## 1. Predecessor status — what this package is and is not

| Artifact | Status |
|---|---|
| `docs/checkpoints/v7_2_production_version_lineage_rerun_difference_freeze_2026-09-20.md` and `results/provenance/v7_2_production_version_lineage_freeze_candidate/` | **LINEAGE_FREEZE_CANDIDATE_V1 · AUDIT_STATUS = STOP · HISTORICAL_PROVENANCE_ONLY.** Preserved byte-identical. Not read for authority, not edited, not overwritten. |
| Interrupted Codex R2 attempt | **ABSENT.** A read-only recovery inspection of the live working tree found **no** R2 directory, **no** R2 checkpoint and **no** other R2-specific provenance artifact. The interrupted session left nothing on disk. Recovery classification: **(A) R2 directory absent.** |
| This package (R2) | **CANDIDATE.** Built at the intended R2 paths, because no partial R2 bytes existed to preserve. Not authority. |

Because the interrupted pass produced nothing, no `_r2_recovery` namespace was needed and none was
created; the authorized R2 paths were used directly.

---

## 2. Three-level architecture

Semantic lineage, execution and result are now **separate record types in separate files**. No
semantic lineage node is its own parent; no lineage node is created per execution.

```
MAINLINE-HIST-R1                         (root; core r1; superseded_by MAINLINE-CORRECTED-R10)
└── MAINLINE-HIST-R9-FINAL81             (core r9; HISTORICAL_REFERENCE_NOT_CURRENT_FOR_FINAL_THESIS)
    └── MAINLINE-CORRECTED-R10           (core r10; CURRENT_ACCEPTED_MAINLINE_PRODUCTION_AUTHORITY)
        ├── EX-03  corrected EOB execution            → 1 result  (EOB)
        ├── EX-04  representative execution a0.60_b04 → 1 result
        ├── EX-05  representative execution a0.60_b12 → 1 result
        ├── EX-06  representative execution a0.80_b08 → 1 result
        ├── EX-07  representative execution a1.00_b04 → 1 result
        ├── EX-08  representative execution a1.00_b12 → 1 result
        ├── SENS-WINTERPV-R10   [sensitivity branch]  → EX-09 → 2 results
        ├── SENS-COST1MW-R10    [sensitivity branch]  → EX-10 → 6 results
        ├── SENS-SOC2080-R10    [NOT_YET_EXECUTED]    → 0 executions, 0 results
        ├── FINAL81-CORRECTED-R10 [NOT_YET_EXECUTED]  → 0 executions, 0 results
        └── ROBUST-A2-R10       [NOT_YET_EXECUTED]    → 0 executions, 0 results
```

`MAINLINE-HIST-R1` carries `EX-01` → 1 result. `MAINLINE-HIST-R9-FINAL81` carries `EX-02` → 81 results.

**Identity rules enforced:** `lineage_id` is the primary semantic identity; `run_id` is execution
identity only and is never lineage identity; dates are metadata only.

---

## 3. Authority and supersession

| Lineage | authority_status | supersedes | superseded_by | expected_future_successor |
|---|---|---|---|---|
| MAINLINE-HIST-R1 | HISTORICAL_ACCEPTED_PRODUCTION_SUPERSEDED_FOR_CURRENT_CORRECTED_AUTHORITY | NOT_APPLICABLE | MAINLINE-CORRECTED-R10 | NOT_APPLICABLE |
| MAINLINE-HIST-R9-FINAL81 | **HISTORICAL_REFERENCE_NOT_CURRENT_FOR_FINAL_THESIS** | NOT_APPLICABLE | **NOT_YET_APPLICABLE** | **FINAL81-CORRECTED-R10** |
| MAINLINE-CORRECTED-R10 | CURRENT_ACCEPTED_MAINLINE_PRODUCTION_AUTHORITY | MAINLINE-HIST-R1 | NOT_APPLICABLE | NOT_APPLICABLE |
| SENS-WINTERPV-R10 | ACCEPTED_SENSITIVITY | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| SENS-COST1MW-R10 | ACCEPTED_SENSITIVITY | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| SENS-SOC2080-R10 | NOT_YET_EXECUTED | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| FINAL81-CORRECTED-R10 | NOT_YET_EXECUTED | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |
| ROBUST-A2-R10 | NOT_YET_EXECUTED | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE |

**Historical final-81:** it remains immutable historical production evidence and is **not** current
final-thesis production, but **no supersession edge exists**, because the corrected 81-point surface
has not been executed. `FINAL81-CORRECTED-R10` is recorded only as the *expected* future successor.

**Sensitivity is not version correction.** Neither `SENS-WINTERPV-R10` nor `SENS-COST1MW-R10`
supersedes the mainline; the future SOC branch is likewise a sensitivity branch.

---

## 4. Executed result count — exactly 96

| Lineage | Executions | Results |
|---|---|---|
| MAINLINE-HIST-R1 (historical EOB) | 1 | **1** |
| MAINLINE-HIST-R9-FINAL81 | 1 | **81** |
| MAINLINE-CORRECTED-R10 (corrected EOB + 5 representatives) | 6 | **6** |
| SENS-WINTERPV-R10 | 1 | **2** |
| SENS-COST1MW-R10 | 1 | **6** |
| **TOTAL** | **10** | **96** |

Future branches hold **zero** executions, **zero** results, **zero** pseudo-results and **zero**
objective / E_N / P_B / CC values. The v1 defect of three future placeholder result records is
corrected: this package contains no placeholder results.

---

## 5. Difference matrix

`cross_version_difference_matrix.json` / `.csv` — **153 rows, one field per row**, with the required
schema (`comparison_id`, `case_id`, `old_lineage_id`, `new_lineage_id`, `category`, `field`,
`old_value`, `new_value`, `numerical_delta`, `relative_delta`, `changed`, `change_type`, `reason`,
`source_evidence`, `interpretation_boundary`).

| Comparison | Rows |
|---|---|
| `C1_R1_TO_R10_EOB` — MAINLINE-HIST-R1 → MAINLINE-CORRECTED-R10 | 29 |
| `C2_R10_TO_WINTERPV` — sensitivity branch | 52 |
| `C3_R10_TO_COST1MW` — sensitivity branch | 72 |

Categories used are drawn only from the controlled taxonomy (DATA, PREPROCESSING, MODEL_EQUATION,
CONSTRAINT_SEMANTICS, PARAMETER, TARIFF_BILLING, ECONOMIC_ACCOUNTING, DEGRADATION,
SOLVER_CONFIGURATION, IMPLEMENTATION_ONLY, PROVENANCE_ONLY, OPTIMIZATION_RESPONSE,
SENSITIVITY_FACTOR).

**Relative-delta convention:** `(new − old) / |old|`, dimensionless. `NOT_APPLICABLE` for
non-numeric values; `NOT_APPLICABLE_ZERO_DENOMINATOR` when `old == 0`. Non-numeric rows carry
`numerical_delta = NOT_APPLICABLE`.

**Causal-claim guard.** All R1 → R10 result differences are sourced from the accepted R3
result-delta authority and are recorded as **observational**: "observed after the accepted
correction bundle." W-04, W-07 and Surface-1 / Exact-D were applied **together** in a single
corrected run; no individual correction is claimed to have caused any objective, E_N, P_B, CC or
cost-component difference, because no isolated counterfactual solve exists and none is authorized.
The three R3 items that cannot be compared (`U01` historical per-period billing maxima, `U02`
per-correction objective decomposition, `U03` solver-quality comparability) are carried explicitly
as `NOT_COMPARED` / `changed = UNKNOWN` rather than silently omitted.

---

## 6. Reconstructibility (controlled vocabulary only)

| Lineage | Class |
|---|---|
| MAINLINE-HIST-R1 | `PARTIALLY_RECONSTRUCTIBLE` — core r1 bytes and the pre-W-04 input are absent from the working tree |
| MAINLINE-HIST-R9-FINAL81 | `PARTIALLY_RECONSTRUCTIBLE` — core r9 bytes and the pre-W-04 input are absent |
| MAINLINE-CORRECTED-R10 | `FULLY_RECONSTRUCTIBLE` |
| SENS-WINTERPV-R10 | `FULLY_RECONSTRUCTIBLE` |
| SENS-COST1MW-R10 | `FULLY_RECONSTRUCTIBLE` |
| SENS-SOC2080-R10 / FINAL81-CORRECTED-R10 / ROBUST-A2-R10 | `NOT_APPLICABLE` (not executed) |

The historical EOB execution identity is recorded as
`NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE`: no `run_id` exists in either its result or its freeze
audit. Execution identity was **not** inferred from filesystem timestamps anywhere in this package.

---

## 7. Exact-byte code snapshot

HEAD alone is insufficient, because accepted executions depend on tracked modifications **and** on
untracked authoritative files. Therefore:

- **22 untracked files copied byte-exactly** into `code_snapshot/`, including the two untracked
  accepted runners `scripts/15d_run_corrected_eob_v7_2.py` (corrected EOB) and
  `scripts/17d_run_bess_cost_scale_sensitivity.py` (1 MW), their authority tests, and every
  untracked checkpoint that participates in a runner's hash-pin or repository-boundary gate.
- **8 tracked-modified sources** captured as a unified diff against HEAD in
  `prepackage_tracked_changes.patch` (95,656 bytes) — this covers the `16a`, `17b`/`17c` routes and
  the corrected core.
- Each snapshot record carries original path, snapshot path, SHA-256, byte count, role and the
  lineage/execution that requires it. Bytes were copied, never rewritten.

Route reconstructibility is recorded per route in `code_snapshot_manifest.json`; the two historical
routes (core r1, core r9) are marked `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE`.

---

## 8. 1 MW durable acceptance

An independent read-only re-verification of run `20260919T151258567077Z_0541e6897a` reproduced: one
production invocation, six optimize calls (corroborated by six Gurobi log headers), zero comparator
solves, zero retries, six OPTIMAL binary solves with all gaps ≤ 1e-6, all post-solve gates PASS
(14/14 EOB, 22/22 per representative), rainflow PASS on all six, 124/124 artifact-registry entries
hash-verified, and 1 MW package identity on every case.

The result is recorded in the **separate additive** artifact
`docs/checkpoints/bess_cost_scale_1mw_postrun_acceptance_freeze_v7_2_2026-09-20.md`. The run's
**original completion manifest is unmodified and still reads
`CANDIDATE_PASS_PENDING_INDEPENDENT_POST_RUN_AUDIT`.** Only on that basis is `SENS-COST1MW-R10`
classified `ACCEPTED_SENSITIVITY`.

---

## 9. JSON / CSV semantic parity

All four record families are emitted as both JSON and CSV. Every CSV cell holds the **canonical JSON
encoding** of the corresponding value, so nested structures survive intact. Parity was verified by
re-reading each CSV, `json.loads`-decoding every cell and comparing the reconstructed records for
full structural equality against the JSON — row-count equality alone was explicitly not accepted.

| Pair | JSON records | CSV data rows | Columns | Round-trip |
|---|---|---|---|---|
| `production_version_lineage_ledger` | 8 | 8 | 42 | **PASS** |
| `execution_ledger` | 10 | 10 | 26 | **PASS** |
| `execution_result_records` | 96 | 96 | 15 | **PASS** |
| `cross_version_difference_matrix` | 153 | 153 | 16 | **PASS** |

---

## 10. Limitations

1. **This package is a candidate.** It is not closed and not accepted; it requires independent
   cross-agent audit before it may be treated as provenance authority.
2. **No corrected 81-point surface exists.** The current mainline covers the EOB and five
   representative cases only; `FINAL81-CORRECTED-R10` is unexecuted.
3. **Historical routes are only partially reconstructible.** Core r1 and core r9 bytes and the
   pre-W-04 canonical input are not present in the working tree; only their hashes and result
   artifacts survive.
4. **The historical EOB execution identity is unrecoverable** and is recorded as such.
5. **Three R3 comparisons remain unresolved** (`U01`, `U02`, `U03`) and are carried as
   `NOT_COMPARED`; resolving `U02` would require isolated counterfactual solves, which do not exist
   and are not authorized.
6. **R1 → R10 differences are observational only.** No per-correction attribution is made anywhere
   in this package.
7. **Cross-lineage comparisons are pairwise by case.** The 81-point historical surface is inventoried
   at full result granularity but is not differenced case-by-case against a corrected surface,
   because no corrected surface exists.
8. **Sensitivity comparisons reuse each run's own frozen paired-comparison artifact** as source
   evidence; they were not recomputed from dispatch, and no solve was performed.

---

## 11. Non-mutation record

Framework, Registry, corrected core, canonical and sensitivity inputs, economic/tariff/settlement
interfaces, all accepted run artifacts, all historical artifacts, candidate v1, and the original
1 MW completion manifest were **all left byte-identical**. Only new additive files were created.

- Optimize calls: **0** · model constructions: **0**
- Commit / push / tag / reset / clean / stash / checkout: **0**
- Branch `thesis-v7`, HEAD = `origin/thesis-v7` = `b03721275c73b05d45517bdf84c1e0bd03833376`, staged = 0
