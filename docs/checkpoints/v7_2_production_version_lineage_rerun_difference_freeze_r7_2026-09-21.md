# V7.2 Production Version Lineage / Rerun Difference Freeze — Candidate R7

**Date:** 2026-09-21  
**Status:** CANDIDATE PASS — NOT CLOSED / NOT ACCEPTED  
**Package identity:** `V7_2_PRODUCTION_VERSION_LINEAGE_FREEZE_CANDIDATE_R7`  
**Package namespace:** `results/provenance/v7_2_production_version_lineage_freeze_candidate_r7/`

This is an additive provenance correction only. It does not authorize or execute a corrected final81 run, create a corrected production runner, start SOC sensitivity, change methodology, or supersede any production result.

## Required findings

1. **R6 disposition:** Candidate R6 received **STOP** and remains immutable historical provenance.
2. **Substantive R6 conclusion retained:** `FINAL81-CORRECTED-R10 = NOT_YET_AUTHORIZED / NOT_YET_EXECUTED` remains correct.
3. **R6 taxonomy defect:** R6 did not establish a genuinely primary-source-first taxonomy because its builder selected predecessor guard IDs and loaded predecessor route/difference records as the generative universe.
4. **R7 correction:** R7 rebuilt the route taxonomy from a complete, machine-readable source coverage ledger over current `scripts/19b_run_final_layer_a_81_cases.py` bytes (`SHA-256 4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe`).
5. **Generation boundary:** No R5/R6 route inventory or C4 row was loaded to define the R7 route universe. Predecessor material was consulted only after the primary taxonomy was complete, and only for retained historical records plus C1–C3 regression checking.
6. **`repository_authority()` count:** 23 distinct mandatory guards were derived from source.
7. **`authority_gate()` count:** 33 distinct mandatory guards were derived from source, including the delegated execution-guard integrity predicates.
8. **Production-entry count:** 1 distinct explicit execute-flag guard was derived outside the two authority functions. The later production authority check is classified as one non-distinct redundant recheck.
9. **Total distinct mandatory guard count:** 57, computed from the source coverage ledger rather than asserted as an input.
10. **Failing distinct guard count:** 11 current fail-closed guard rows.
11. **Unique hard-failure root-cause count:** 6: helper19 SHA mismatch, tracked boundary, untracked boundary, protected-identity family, ignored-runtime set mismatch, and ignored-runtime hash mismatch.
12. **Historical-only incompatibility count:** 3 unique concepts: accepted historical 19a authority, historical R9 routing authority, and historical EOB comparator authority. These are separate from the six current hard-failure root causes.
13. **Coverage completeness:** 59 acceptance-relevant source sites are mapped as 57 `DISTINCT_MANDATORY_GUARD`, 0 source-site `COMPONENT_DETAIL`, 1 `AGGREGATE_SUMMARY`, 1 `REDUNDANT_RECHECK`, 0 `NON_EXECUTION_DIAGNOSTIC`, and 0 `NOT_APPLICABLE`; `unmapped_acceptance_relevant_sites = 0`. Collection-member mismatch evidence is represented separately as route-inventory component-detail records and is excluded from the distinct count.
14. **Preflight versus accumulated rehash:** The 93-item preflight registry independently passes. The later accumulated-identity rehash is a separate distinct guard and fails with 11 mismatches. A registry PASS cannot mask the later rehash failure.
15. **Corrected C4 count:** 110 rows, derived as 9 specification differences + 1 raw 19b identity + 1 route-compatibility summary + 57 distinct route guards + 5 future-authority sentinels + 26 meaningful unchanged fields + 11 pending optimization-response fields.
16. **Corrected total difference count:** 263 rows: C1=29, C2=52, C3=72, C4=110. C1–C3 normalized R5/R6 records match exactly and their referenced result/historical evidence was rehashed before retention.
17. **Exact Git porcelain:** R7 stores raw subprocess bytes before decoding, exact UTF-8 text without `.strip()`/`.lstrip()`/`.rstrip()`, Base64 bytes, byte count, newline flag, and SHA-256. Staged, unstaged tracked, and untracked paths are captured independently with NUL-delimited Git commands and cross-checked against the raw porcelain status classes.
18. **Corrected final81 boundary:** `FINAL81-CORRECTED-R10` has zero executions, zero results, zero result SHA, zero completion manifest, and no objective / `E_N` / `P_B` / `CC`. It remains `NOT_YET_AUTHORIZED / NOT_YET_EXECUTED`.
19. **Non-mutation:** No production runner, model/core, Framework, Registry, 19a, 19b, tariff/data input, historical result, corrected result, accepted sensitivity, completion manifest, existing authority manifest, Git commit, or Git tag was changed by R7. No model was constructed and no optimization or production rerun occurred.
20. **Remaining limitations:** R7 is a candidate provenance package requiring independent read-only acceptance audit. It does not create the future corrected runner/authority manifest/tag/preflight, does not resolve the dirty working-tree and identity guard failures, does not recover the missing historical settlement matrix, and cannot provide corrected-final81 numerical deltas before a separately authorized and accepted execution.

## Source-derived guard outcomes

- Hard failing rows: tracked boundary; untracked boundary; protected-identity collection; ignored-runtime set; ignored-runtime hash collection; helper19 SHA; delegated lineage gate; checkpoint identity collection; later accumulated-identity rehash; existing 18a/18b validator collection; recomputed-column collection.
- The preflight artifact registry passes independently with 93 registered artifacts.
- The later accumulated-identity map contains 11 current mismatches and therefore fails independently.
- START_HEAD semantics pass: `v7.2-pre81-ready` peels to `b2acdf28cf1459aee5da44e4407c225f5d3c68a6`, which is an ancestor of current HEAD; current HEAD is not required to equal START_HEAD.
- Tag concepts remain separate: `v7.2-pre81-ready` and `v7.2-final81-runner-ready-r3` have independently checked tag-object and peeled-commit identities.
- Raw 19b identity remains unchanged; that does not establish corrected-R10 route compatibility.

## Claim boundary

R7 is an implementation/provenance correction, not a methodology change. The package records source coverage, current guard state, historical lineage, reconstructibility, and pending-result boundaries. It makes no claim that a corrected 81-case surface exists, that the current 19b route can execute corrected R10 authority, or that any pending optimization response is numerically known.
