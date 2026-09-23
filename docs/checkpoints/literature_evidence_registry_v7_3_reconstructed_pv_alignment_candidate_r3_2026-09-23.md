# Registry v7.3 R3 reconstructed-PV alignment candidate checkpoint

**Date:** 2026-09-23  
**Pass:** RERUN-2 Step 2C-R3  
**Disposition:** **LITERATURE / EVIDENCE REGISTRY V7.3 R3 RECONSTRUCTED-PV ALIGNMENT — CANDIDATE PASS**

This is a producer checkpoint for a new additive R3 candidate. It does not declare R3 `CLOSED` or
`ACCEPTED`; independent read-only acceptance is still required.

## 1. Governing identities re-verified before editing

| Artifact | SHA-256 | State |
|---|---|---|
| `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` | accepted methodology authority |
| `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` | last accepted evidence source |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` | failed R1; immutable provenance |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_2026-09-23.md` | `301b931a3b7ea4b0c981079789e66a69e5571294a0d29467bd0c6c262c17fe2d` | failed R1 checkpoint; immutable provenance |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` | failed R2; immutable provenance |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_r2_2026-09-23.md` | `5b9f063709b680f8099d72ee440d9be6be02687e82476267903f95be8f416917` | failed R2 checkpoint; immutable provenance |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` | R3 candidate; not accepted |

R1 and R2 primary files and checkpoints were not edited, repaired, renamed, or deleted.

## 2. R2 STOP root cause re-derived from primary bytes

R2's audit-status block contained this unqualified current-authority statement:

> `Framework v7.2 + Registry v7.2 are the only current mainline specification/evidence sources for implementation.`

It conflicted with all three independently checked locations:

1. accepted Framework v7.3 is the methodology authority specified for this pass;
2. R2's source manifest identifies Framework v7.3 as the accepted alignment target;
3. R2 Sec 17.7 identifies Framework v7.3 as `CLOSED / ACCEPTED`.

The statement was inherited from Registry v7.2 without historical/superseded scoping. R2's checkpoint
therefore incorrectly certified `D = 0` and no Framework/Registry contradiction.

## 3. Exact R3 correction

R3 replaces that one authority rule with explicit temporal separation:

- v7.2 authority state: Framework v7.2 + Registry v7.2 were the then-current pair;
- current v7.3 transition state: Framework v7.3 is the accepted methodology source of truth;
- Registry v7.2 remains the last accepted evidence source until a v7.3 Registry successor passes
  independent acceptance;
- R3 is candidate only;
- Framework v7.2 is a historical methodology predecessor, not current methodology authority.

Dependent edits record R3 identity, R1/R2 lifecycle provenance, the corrected Sec 17 status table, and
the fresh consistency/stale-wording audit. No scientific/evidence-role correction was made.

## 4. Framework-to-Registry consistency re-check

| Location checked | R3 result |
|---|---|
| Document header / lineage | R3 candidate; failed R2 identified; Framework v7.3 accepted |
| Source manifest | Framework v7.3 accepted; Registry v7.2 last accepted; R1/R2 failed and immutable |
| Supersession rule | R3 candidate only; correct current methodology/evidence split |
| Audit-status rule | v7.2 authority past-scoped; v7.3 transition state explicit |
| P1-E | historical zero-winter/current reconstructed-PV separation preserved exactly from R2 |
| Sec 17 status table | Framework v7.3 accepted; R1/R2 failed; R3 candidate only |
| Sec 17 coverage / consistency | all fourteen reconstructed-PV claims rechecked; authority sweep added |

The whole-document authority-wording sweep found no sentence assigning current methodology authority
to Framework v7.2. Surviving Framework v7.2 references are historical, predecessor, frozen-decision,
or failed-candidate descriptions. Result: **no Framework/Registry contradiction found in R3**.

## 5. Fresh stale-wording and authority-wording audit

Search was re-run over R3 primary bytes using the complete prior term set plus the six authority terms.
Counts are case-insensitive substring matches by line and were not reused from R2.

| Term | Lines | Term | Lines | Term | Lines |
|---|---:|---|---:|---|---:|
| winter | 68 | reconstruction | 50 | 17b | 19 |
| missing_winter | 7 | synthetic | 1 | 17c | 22 |
| pre_system | 7 | CWA | 49 | sensitivity | 103 |
| zero winter | 0 | GHI | 24 | mainline | 114 |
| zero-winter | 18 | long block | 2 | canonical | 27 |
| zero availability | 4 | long-block | 18 | current | 55 |
| zero-availability | 4 | 17a | 22 | source of truth | 10 |
| reconstructed | 67 | authoritative | 7 | authority | 26 |
| accepted | 38 | specification | 6 | | |

Universe: **364 matched line indices / 364 unique line texts / 345 lines longer than 40 characters**.

Relevant lines were adjudicated clause-wise:

- **A:** current v7.3 role/authority statements identify reconstructed PV and Framework v7.3 correctly;
- **B:** v7.2 and failed-R1/R2 statements are explicitly historical, predecessor, frozen, or quoted-failure records;
- **C:** zero-winter treatment is consistently conservative stress/sensitivity when stated as current;
- **D:** **0 stale, contradictory, or ambiguous current-role/current-authority statements**.

Quoted R1/R2 defect wording in lifecycle sections is explicitly attributed to failed candidates and is
not a current R3 assertion.

## 6. R2 to R3 diff minimality

Independent text diff:

- insertions: **63**
- deletions: **18**
- default `-U3` hunks: **8**

| Hunk | Content | Classification |
|---:|---|---|
| 1 | R3 title, updated summary and lineage | `REQUIRED_R3_LIFECYCLE_PROVENANCE` |
| 2 | source manifest and supersession rule | `REQUIRED_R3_LIFECYCLE_PROVENANCE` |
| 3 | audit-status authority rule | `REQUIRED_AUTHORITY_SCOPING_CORRECTION` |
| 4 | fresh Framework coverage result | `REQUIRED_DEPENDENT_AUDIT_UPDATE` |
| 5 | Sec 17 status table | `REQUIRED_R3_LIFECYCLE_PROVENANCE` |
| 6 | consistency/stale audit and R3 candidate disposition | `REQUIRED_DEPENDENT_AUDIT_UPDATE` / `REQUIRED_R3_LIFECYCLE_PROVENANCE` |
| 7 | historical Sec 18 R2 identity | `REQUIRED_R3_LIFECYCLE_PROVENANCE` |
| 8 | corrected R2 status and additive Sec 19 R2-to-R3 record | `REQUIRED_R3_LIFECYCLE_PROVENANCE` |

`UNRELATED_CHANGE = 0`.

## 7. Scientific and non-PV preservation

The diff contains no change to P1-E, P7, 17a/17b/17c roles or values, legacy provenance fields, P7-D
numbers, Script 14a references, [L1], external-literature records, A1-A4, B1-B2, Gate 1, Gate 2,
billing calibration, tariff methodology, degradation, PNNL cost roles, monetary basis, rainflow role,
SOC20-80 role, solver settings, or production parameters.

## 8. Current authorization boundary

| Item | State |
|---|---|
| Framework v7.3 | `CLOSED / ACCEPTED` |
| Registry R1 | failed / superseded candidate; immutable |
| Registry R2 | failed / superseded candidate; immutable |
| Registry R3 | `CANDIDATE PASS`; not accepted |
| Registry v7.2 | last accepted evidence source pending R3 acceptance |
| Canonical reconstructed-mainline artifact | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` |
| Production routing | `NOT_YET_AUTHORIZED` |
| Step 17c EOB | promotion/adjudication candidate evidence only |
| Representative cases / Steps 11A-B-C | not closed under v7.3 |
| Final81 | not authorized under v7.3 |

## 9. Repository state and zero-solve boundary

Pre-edit state:

- branch `thesis-v7`;
- HEAD/origin `28b0e780c3b298cd88c02e218a99fe3463ff496c`;
- ahead/behind `0/0`;
- no staged or tracked modifications;
- 12 untracked files.

Post-edit state:

- branch `thesis-v7`;
- HEAD/origin remain `28b0e780c3b298cd88c02e218a99fe3463ff496c`;
- ahead/behind remains `0/0`;
- no staged or tracked modifications;
- 14 untracked files: the original 12 plus the two authorized R3 files below.

Only these new files were authored:

1. `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`;
2. `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_r3_2026-09-23.md`.

No `optimize()`, model construction, solver invocation, production rerun, parquet regeneration,
canonical-artifact construction, routing change, source-code edit, test edit, commit, push, or tag was
performed.

## 10. Required next gate

An independent auditor who did not produce R3 must perform a read-only acceptance audit from primary
bytes. R3 must remain a candidate until that audit returns `CLOSED / ACCEPTED`. Canonical reconstructed-PV
artifact construction and production routing remain out of scope until the later merge/alignment/freeze
sequence authorizes them.
