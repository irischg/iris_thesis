# Framework v7.4 Candidate R2 documentation/status correction checkpoint

**Date:** 2026-09-26
**Disposition:** CANDIDATE ONLY — not CLOSED, not ACCEPTED, not FINAL, not PROMOTED
**Correction class:** documentation / status / provenance only
**Fresh independent read-only R2 audit required:** YES

## 1. Scope and authority boundary

Framework v7.4 Candidate R2 is a minimal successor of immutable Candidate R1. It corrects stale v7.3-candidate-era implementation/status language and adds R2 provenance plumbing. It does not add a methodology decision, a Change D scientific category, an equation, a parameter, a sensitivity design, a solver-facing change, or a numerical-result change.

Current accepted methodology authority remains Framework v7.3. Current accepted evidence authority remains Registry v7.3 R3. Candidate R2 cannot self-accept; no Registry v7.4 successor work, Layer A preregistration work, production-authority re-freeze, or Full81 execution is authorized by this checkpoint.

## 2. Pre-correction repository identity

| Item | Verified value |
|---|---|
| Branch | `thesis-v7` |
| Pre-HEAD | `5d81ee989856d42a21e715def4625162ea9fc0af` |
| Pre-HEAD parent | `1651b31008c565e105fc79a958f9ca98a194aa80` |
| Local `origin/thesis-v7` before correction | `5d81ee989856d42a21e715def4625162ea9fc0af` |
| Live remote `origin/thesis-v7` before correction | `5d81ee989856d42a21e715def4625162ea9fc0af` |
| R1 independent verdict | `CONDITIONAL PASS / REVISE` |
| R1 blocking class | stale candidate-era implementation/status wording |
| Scientific methodology defect found by R1 audit | NO |
| Accepted numerical-result defect found by R1 audit | NO |

The pre-correction worktree contained exactly eight unrelated untracked files. They were preserved and excluded from this correction. The reconstructed UTF-8 porcelain snapshot contained 447 bytes with SHA-256 `2720879eb0de989bf50e4755e2c5518748a832a5295ecc5e1cdde237c3edbcd8`.

## 3. Immutable predecessor and authority verification

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/research_framework_v7_4_2026-09-26.md` | immediate candidate predecessor, R1 | 212268 | `52459a06a6c527413c74bd5d740992975284b1d41216168aad5869c585da6cda` |
| `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_2026-09-26.md` | immutable R1 checkpoint | 19041 | `a9df7162ee27bfd037b500e531a64bc921a001ab39a103543a9031d7141d551e` |
| `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/completion_manifest.json` | immutable R1 completion manifest | 15909 | `923343ab7958e9739e194fced97a6372fd4f81e6ddd97a38ae86d3a7f6c98d0b` |
| `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/package_manifest.json` | immutable R1 package manifest | 5582 | `e6592857561bf3940c2468704a7108633b4f0ea198ea432acb9ff8b2c00de124` |
| `docs/research_framework_v7_3_2026-09-23.md` | accepted methodology predecessor/current authority | 181798 | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | accepted evidence authority | 187796 | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | accepted v7.3 lifecycle closure | 12358 | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
| `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | governing provenance protocol | 19977 | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |

Every path, byte count, and hash above was re-read and verified before R2 mutation. Candidate R1 and all accepted/historical authorities remained byte-identical.

## 4. Correct current implementation/result state

| Item | R2 current statement |
|---|---|
| Accepted planning input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`; SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`; role `reconstructed_pv_mainline`; 8760 rows; CLOSED / ACCEPTED |
| Production routing used by accepted EOB/core-three | COMPLETED / ACCEPTED |
| Accepted EOB | `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556`; CLOSED / ACCEPTED |
| Accepted core-three | `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55`; LOW 0.60/4 h, CENTRAL 0.80/8 h, HIGH 1.00/12 h; CLOSED / ACCEPTED |
| EOB valid under v7.4 scientific delta | YES, per R1 independent audit |
| Core-three valid under v7.4 scientific delta | YES, per R1 independent audit |
| Methodology rerun required | NO, per R1 independent audit |
| Full81 | NOT_YET_EXECUTED / NOT AUTHORIZED |

## 5. Exact stale-status corrections

| Section | R1 problem | R2 treatment | Authoritative basis |
|---|---|---|---|
| §0.3 | Accepted v7.3 authorities, canonical artifact, routing, EOB, and core-three were still described as candidate/pending future work. | Replaced with an explicit completed/accepted block, a separately bounded future-v7.4 governance block, and the R1 downstream-impact verdict. | Accepted v7.3 authority/freeze, accepted artifact identity, accepted EOB/core-three, R1 independent audit. |
| §4.1.3 | Corrected Sep-18 promotion source appeared to be current while the canonical reconstructed-mainline artifact appeared not yet created/authorized. | Named the accepted R3 planning input as current authority; retained corrected Sep-18 only as historical promotion-source lineage; updated the routing diagram. | Accepted planning input path/hash/role/row count and production routing evidence. |
| §19.1 | Future final EOB plus 81-point Layer A rerun language could be read as making accepted EOB/core-three pending. | Distinguished accepted EOB/core-three from unexecuted Full81 and recorded no methodology rerun requirement. | Accepted results and R1 audit. |
| §31.2–§31.3 | Critical-path/task wording treated canonical input, routing, EOB, and core-three as future. | Split completed/accepted facts from pending v7.4 governance and Full81; did not preauthorize later tasks. | Accepted artifacts/results plus current governance boundary. |
| §32 | Inherited unchecked candidate-era checklist looked current. | Added a current replacement table and an explicit whole-checklist historical-snapshot scope. | Current accepted evidence and provenance-preserving historical treatment. |
| §36.6–§36.8 | Downstream validity remained not adjudicated and candidate identity did not distinguish R2. | Recorded the completed R1 adjudication, correct result states, zero execution counts, R2 authorization table, and fresh-audit-only disposition. | R1 independent verdict and current accepted result authorities. |
| Full document | Two additional v7.3-candidate references looked current outside the principal sections. | Converted both to explicit past-scoped provenance statements. §35 was not rewritten because it was already locally and adequately historical-scoped. | R1 audit finding and minimum-semantic-diff rule. |

## 6. Scientific immutability and two-way diff audit

### Accepted v7.3 to Candidate R2

The only scientific delta remains the already-audited R1 Change A/B/C:

1. Change A — zero-winter current role is historical conservative validation / provenance evidence.
2. Change B — observed-versus-planning PV epistemic routing is formalized without equation change.
3. Change C — kappa historical-calibration versus planning-use claim boundary is explicit without recalibration.

No Change D scientific category exists. Display-equation extraction found 152 blocks in accepted v7.3 and 154 in R2. The only two multiset additions are duplicate routing restatements of `P_t^{grid,hist}=L_t^{obs}-PV_t^{obs}`, both inherited unchanged from R1 Change B; no accepted-v7.3 display equation was removed or altered.

### Candidate R1 to Candidate R2

The complete semantic diff was reviewed. Every substantive R2-only hunk is classified as `STATUS_CORRECTION`, `HISTORICAL_SCOPING`, or `PROVENANCE_R2_PLUMBING`. Display-equation extraction found 154 blocks in both R1 and R2 with multiset difference 0.

| Scientific guard | Result |
|---|---|
| New model equations | 0 |
| Changed model equations | 0 |
| New parameters | 0 |
| Changed parameters | 0 |
| New sensitivity designs | 0 |
| Solver-facing methodology changes | 0 |
| A1–A4 unchanged | YES |
| B1–B2 unchanged | YES |
| Gate 1 / Gate 2 unchanged | YES |
| Zero-winter role unchanged from R1 | YES |
| PV routing unchanged from R1 | YES |
| Kappa estimator and pinned production value unchanged | YES |
| Accepted EOB result unchanged | YES |
| Accepted core-three result unchanged | YES |

## 7. Full-document stale-status search

Every case-insensitive exact occurrence of the required search phrases was classified. Counts below are occurrence counts, not merely matching-line counts.

| Phrase | A: correct current state | B: historical snapshot | C: future v7.4 governance | D: stale contradiction | Total |
|---|---:|---:|---:|---:|---:|
| `NOT_YET_CREATED` | 0 | 4 | 11 | 0 | 15 |
| `NOT_YET_ACCEPTED` | 0 | 1 | 0 | 0 | 1 |
| `NOT_YET_AUTHORIZED` | 0 | 4 | 16 | 0 | 20 |
| `future canonical` | 0 | 2 | 0 | 0 | 2 |
| `future EOB` | 0 | 0 | 0 | 0 | 0 |
| `rerun` | 21 | 2 | 0 | 0 | 23 |
| `representative cases` | 1 | 2 | 0 | 0 | 3 |
| `Registry v7.3` | 12 | 2 | 0 | 0 | 14 |
| `canonical routing` | 0 | 1 | 0 | 0 | 1 |
| `production rerun` | 0 | 1 | 0 | 0 | 1 |
| `candidate evidence only` | 0 | 1 | 0 | 0 | 1 |
| `pending` | 6 | 3 | 4 | 0 | 13 |
| `before v7.3 acceptance` | 0 | 0 | 0 | 0 | 0 |
| `after v7.3 acceptance` | 0 | 0 | 0 | 0 | 0 |
| **Total** | **40** | **23** | **31** | **0** | **94** |

**STALE CURRENT-STATUS CONTRADICTIONS REMAIN: NO.**

## 8. Execution and governance counts

| Action/state | Value |
|---|---:|
| Optimization calls | 0 |
| Model constructions | 0 |
| MILP solves | 0 |
| EOB reruns | 0 |
| Core-three reruns | 0 |
| Full81 runs | 0 |
| Sensitivity solves | 0 |
| Registry successor | NOT CREATED |
| Layer A preregistration checkpoint | NOT CREATED |
| Methodology acceptance | NOT PERFORMED |
| Production-authority re-freeze | NOT PERFORMED |
| Fresh independent R2 audit required | YES |

No production run, model construction, solver invocation, process termination, legacy-error investigation, code edit, data edit, or result edit was performed.

## 9. R2 artifact identity and manifest rule

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/research_framework_v7_4_2026-09-26_r2.md` | Framework v7.4 Candidate R2 | 216186 | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_r2_2026-09-26.md` | this checkpoint | recorded externally | recorded in R2 manifests |
| `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r2/completion_manifest.json` | deterministic R2 completion record | recorded by package manifest | recorded by package manifest |
| `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r2/package_manifest.json` | deterministic package registry | self omitted | self omitted |

The completion manifest omits its own hash. The package manifest registers the framework, checkpoint, and completion manifest, but omits itself. This avoids circular self-hash.

## 10. Candidate conclusion

Framework v7.4 Candidate R2 passes this bounded authoring-session correction audit: R1 science is unchanged, stale current-status contradiction count is zero, accepted EOB/core-three remain valid without rerun, and Full81 remains unexecuted and unauthorized. This conclusion is not methodology acceptance. A fresh independent read-only R2 audit is required before Task 2 may begin.
