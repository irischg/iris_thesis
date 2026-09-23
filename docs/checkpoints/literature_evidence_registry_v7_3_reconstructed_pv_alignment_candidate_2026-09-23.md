# Literature / Evidence Registry v7.3 reconstructed-PV alignment — candidate checkpoint

**Date:** 2026-09-23
**Disposition:** **LITERATURE / EVIDENCE REGISTRY V7.3 RECONSTRUCTED-PV MAINLINE ALIGNMENT — CANDIDATE PASS**
**Acceptance boundary:** candidate only; this checkpoint does not accept or canonize the Registry, the canonical annual input, production routing, or production results. Independent audit is required before this candidate becomes the evidence source of truth.

## 1. Continuation-state audit (read-only, performed before any construction)

A prior Codex agent was reported to have begun this task and lost quota before completion. Before constructing anything, I independently verified:

- `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` — **ABSENT** before this pass;
- `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_2026-09-23.md` — **ABSENT** before this pass;
- no other untracked file existed beyond the six previously accepted unrelated files and the two already-accepted Framework v7.3 candidate files (`docs/research_framework_v7_3_2026-09-23.md`, `docs/checkpoints/framework_v7_3_reconstructed_pv_mainline_successor_candidate_2026-09-23.md`);
- `git diff` and `git diff --cached` were both empty.

**Classification: no interrupted work existed to inherit.** This pass constructs Registry v7.3 fresh, additively, from Registry v7.2 primary bytes. Nothing was inherited, and nothing partial was trusted or reused.

## 2. Scope and protocol

Document/evidence-role alignment only, under `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` (SHA-256 `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696`).

Authorized mutations were limited to:

1. creating the additive successor `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md`;
2. creating this additive candidate checkpoint.

No source code, tests, Framework, canonical input, routing, production results, historical checkpoint, or accepted artifact was edited. No `optimize()` call, model solve, model construction, canonical-input regeneration, production rerun, commit, push, or tag occurred.

## 3. Predecessor and candidate identity

| Artifact | Role | SHA-256 |
|---|---|---|
| `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` | immutable accepted predecessor (unchanged — verified byte-identical before and after) | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |
| `docs/research_framework_v7_3_2026-09-23.md` | accepted alignment target (independently audited CLOSED / ACCEPTED in this session) | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` | additive successor candidate | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` |

Registry v7.3 candidate is 2,610 lines (Registry v7.2 predecessor: 2,385 lines); the delta is entirely additive (net +225 lines across 10 diff hunks, none of which touches unrelated content — verified by full `diff -u` inspection, see §7).

## 4. Exact evidence-role change

The only evidence-role change is the reconstructed-PV mainline/sensitivity reversal, mirroring Framework v7.3's single methodology change:

```text
v7.2: zero-winter PV = mainline evidence role;
      reconstructed winter PV = sensitivity-only evidence role.

v7.3 candidate: separately validated, weather-informed reconstructed full-year PV
                = best-estimate planning mainline evidence role;
                prior zero-winter PV = conservative stress/sensitivity evidence role.
```

This is supported by new project evidence (record **[P7]**, four sub-records P7-A through P7-D) documenting Steps 17a / corrected 17b / 17c, and by targeted realignment of the claim-to-source map, claim boundaries, and status bullets. It is not a new literature claim, and it does not reopen A1–A4, B1–B2, Gate 1, or Gate 2.

## 5. Sections/records changed (10 targeted edits, verified by diff hunk count)

1. Header / title / version-lineage / source-manifest block (v7.2 → v7.3 identity, new source rows for Framework v7.3 and the four P7 evidentiary artifacts);
2. P1-E additive forward-reference paragraph (does not alter the historical Scripts 02–05 finding; points to new [P7]);
3. New record **[P7] Reconstructed-PV mainline promotion evidence** inserted between [P6] and [L1], with sub-records P7-A (Step 17a), P7-B (original Step 17b), P7-C (corrected Step 17b), P7-D (Step 17c), an evidence-role summary table, and one independently-derived data-boundary note (see §8);
4. §12 claim-to-source map: one stale row replaced by two new rows (reconstructed-mainline row; zero-winter-sensitivity row);
5. §14 可以寫: one historical bullet re-scoped to "Under Framework v7.2…", four new v7.3-current bullets added (including the mandatory epistemic sentence verbatim);
6. §14 不要寫: four new forbidden-claim entries added after the existing CWA-extrapolation warning, plus an inline note on that warning;
7. §15: Blocker 2 bullet re-scoped with an additive v7.3 sentence; one new status bullet added for the v7.3 promotion evidence chain;
8. §16 maintenance guardrails: the existing Script-04b guardrail annotated as now-satisfied (not removed), three new guardrails added;
9. §9/[P6] "Remaining implementation/validation gates" bullet list: the winter-PV item re-scoped as a historical pending item with a forward pointer to new §17;
10. New top-level **§17 Framework v7.3 reconstructed-PV mainline evidence alignment** appended at the end, containing the four-class epistemic separation, the Framework→Registry coverage matrix, the historical-evidence preservation matrix, the mainline/zero-winter role table, the numerical-facts table, the status table, the external-literature boundary confirmation, the cross-document consistency audit, and the candidate disposition statement.

Every edit was applied as an exact, uniqueness-verified string substitution against the live Registry v7.2 bytes (old text extracted programmatically from the source file, never retyped, to guarantee byte-exact matching including markdown hard-break whitespace). A post-hoc `diff -u` against Registry v7.2 confirms exactly 10 hunks and zero incidental changes elsewhere in the 2,385-line predecessor.

## 6. Framework → Registry coverage

Full coverage matrix is recorded in Registry v7.3 §17.3. Summary: **9 of 9** acceptance-relevant Framework v7.3 reconstructed-PV claims identified from a full read of the accepted Framework's primary bytes are mapped to a Registry record, evidence type, support level, and anti-claim boundary. One item (Layer A/B same-artifact routing enforcement) is marked "Partial — Registry scope: claim boundary only," because the exact equations and routing enforcement are Framework/implementation authority, not Registry content; this is disclosed rather than overclaimed as fully covered.

## 7. Historical evidence preservation

- **Step 17a**: historical `PASS_FOR_SENSITIVITY` verdict reproduced **verbatim** from `results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/final_validation_decision.json` (SHA-256 `454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594`, independently re-verified this pass); not rewritten. P7-A's "Scope this does NOT establish" list explicitly bars treating the PASS as automatic production-mainline authority.
- **Original Step 17b** (`…sensitivity_protocol_2026-09-07.parquet`, SHA-256 `023cba88416b965c7dedf4139e9a495602039117ecc827e52a372f10a1aad986`, independently re-verified this pass): preserved as `winter_pv_sensitivity_only`; explicitly not identified as a future production source.
- **Corrected Step 17b promotion-source candidate** (`…corrected_authority_project_venv_2026-09-18.parquet`, SHA-256 `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9`, independently re-verified this pass): documented as corrected candidate, **not canonical**; the future canonical artifact's path/hash are recorded as `NOT_YET_CREATED / NOT_YET_AUTHORIZED`.
- **Step 17c**: preserved as paired reconstructed-PV sensitivity/promotion-adjudication evidence only; not retroactively called a v7.3 production run.

P1's historical Scripts 02–05 finding ("short-gap validation does not certify the 1,463-hour long block") is **unmodified** — only an additive forward-reference paragraph was appended after it, pointing to the new, separate P7 evidence.

## 8. Independently derived facts (not taken from any prior report)

I opened the corrected Step 17b candidate parquet directly (read-only, no model construction) and independently re-derived:

- long-unavailable block: 1,463 rows, split `pre_system` = 600 h / `missing_winter` = 863 h — matches P1-E exactly;
- `observed_pv_kw` uniformly 0 over that block — observed columns untouched;
- `winter_pv_sensitivity_applied = True`, `winter_pv_sensitivity_method = cwa_hourly_ghi_ratio_median_all_eligible_v7_2` for all 1,463 rows;
- **619** of 1,463 hours carry positive reconstructed `pv_available_kw`/`kwh`, summing to **39,484.422494 kWh** — matching the task brief's stated figures exactly;
- this figure is independently cross-checked against Step 17c's own `paired_sensitivity_comparison.json` (`pv_available_kwh` delta between the winter-PV-sensitivity and mainline EOB rows = 427,105.4351329623 − 387,621.01263887703 = 39,484.42249408527 kWh — agrees to 6 decimal places).

**One data-boundary finding not present in any prior report:** the candidate artifact's own `pv_reconstruction_method` categorical field for these 1,463 rows still reads the inherited label `unavailable_zero_mainline`, even though the numeric `pv_available_kw`/`kwh` columns for the same rows are the nonzero reconstructed values (the correct method name is instead carried in the separate `winter_pv_sensitivity_method` field). This is recorded in P7-C as a provenance-labeling item for a future canonical-artifact build to correct — not evidence against the reconstruction itself, and not a blocker for this candidate.

## 9. Stale-wording coverage audit (independently re-derived from v7.3 candidate bytes)

Search terms per the task brief: `zero winter`, `zero-winter`, `zero availability`, `zero-availability`, `mainline`, `reconstructed`, `reconstruction`, `synthetic`, `winter`, `missing_winter`, `pre_system`, `17a`, `17b`, `17c`, `sensitivity`, `canonical`.

Total lines matching any search term: **229** (dominated by unrelated `mainline`/`sensitivity` hits — BESS cost-scale mainline, SOC mainline, etc., which are out of scope for this audit). Narrowing to the winter/reconstruction-specific core terms (`winter`, `missing_winter`, `pre_system`, `zero availability`, `zero-availability`, `zero-winter`, `zero winter`, `reconstructed`, `reconstruction`, `synthetic`, `1,463`, `17a`, `17b`, `17c`) gives **138 relevant lines**.

Classification (a line may carry more than one category when it contains both a historical and a current clause, consistent with the task's allowance):

- **A — correct current v7.3 evidence role:** 100 lines;
- **B — correct historical v7.2 role:** 26 lines (e.g. L8, L16–17 header lineage note; L1722 P1-E's unmodified `\boxed{PV_t^{base}=0}` and surrounding Scripts-02–05 text; L2033/2047/2066/2075 P6 historical Gate-2 context; several §17 table cells that restate v7.2's historical role for contrast);
- **C — correct zero-winter conservative-sensitivity role:** 17 lines (the demoted zero-winter treatment, consistently described as "conservative stress/sensitivity," never as "truth" or "observed zero generation");
- **D — stale / contradictory / ambiguous: 0.**

**D = 0 independently confirmed by two methods:**

1. A forbidden-phrase scan for the exact stale v7.2 current-mainline assertions (`1,463 h long unavailable PV mainline維持zero availability。` unqualified; `remains **conservative zero availability** in the mainline` unqualified) returned **zero** unscoped occurrences in the candidate. The only surviving `\boxed{PV_t^{base}=0}` instance sits inside P1-E's untouched historical paragraph, immediately followed by the new forward-reference explicitly scoping it as the pre-v7.3 finding.
2. A regex scan for every line combining "reconstruct…" with "observed/exact truth/exact recovery" found 15 lines; all 15 are either genuinely historical (P1's unmodified text), inside an explicit "does NOT establish" / "不要寫" boundary list, or inside the mandatory negated epistemic sentence. None asserts, unscoped, that reconstructed values are observed or exact.

## 10. Current implementation/result status boundary (as recorded in Registry v7.3 §17.7)

| Layer | State |
|---|---|
| Framework v7.3 | `CLOSED / ACCEPTED` |
| **Registry v7.3** | **`CANDIDATE PASS`** — not yet independently accepted |
| Canonical reconstructed-mainline input | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` |
| Production routing | `NOT_YET_AUTHORIZED` |
| Step 17c reconstructed-mainline EOB | promotion/adjudication candidate evidence only |
| Representative cases | NOT CLOSED UNDER V7.3 |
| Steps 11A / 11B / 11C | NOT CLOSED UNDER V7.3 |
| Final81 | NOT AUTHORIZED UNDER V7.3 |

No future result was fabricated anywhere in this candidate.

## 11. External-literature claim-boundary confirmation

R21–R23, R32–R33, and I5 were re-read in full against the task's forbidden-overclaim list. None is cited, anywhere in this candidate, as establishing the NTUST 39,484.422494 kWh figure, the 619 positive hours, the exact CWA→PV coefficients as universal, PV-equals-measurement equivalence, or the validity of any future 81-point result — each of those numbers is attributed only to project evidence (P1/P7). No web research was performed; this pass reused only citations already present and audited in Registry v7.2.

## 12. Repository before/after state

### Before

- branch: `thesis-v7`;
- `HEAD`: `28b0e780c3b298cd88c02e218a99fe3463ff496c`;
- `origin/thesis-v7`: `28b0e780c3b298cd88c02e218a99fe3463ff496c`; ahead/behind 0/0;
- staged: 0; tracked modified: 0;
- untracked: the 6 pre-existing accepted files, plus the 2 already-accepted Framework v7.3 candidate files (`docs/research_framework_v7_3_2026-09-23.md`, `docs/checkpoints/framework_v7_3_reconstructed_pv_mainline_successor_candidate_2026-09-23.md`).

### After authorized mutations

- branch, `HEAD`, `origin/thesis-v7`: **unchanged**;
- staged: 0; tracked modified: 0;
- all 8 pre-existing untracked files preserved byte-identically;
- added untracked candidate files only:
  - `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md`;
  - this checkpoint.
- Registry v7.2 SHA-256 verified unchanged before and after: `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e`;
- Framework v7.2 SHA-256 (not touched by this pass, re-verified for completeness): `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5`;
- Framework v7.3 SHA-256 (not touched by this pass): `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a`.

## 13. Zero-solve confirmation

Performed: reading primary bytes, hashing files (independently re-derived, never trusted from any prior report), semantic string diffing, Registry-wide search/classification, a direct read-only `pandas.read_parquet` inspection of the corrected Step 17b candidate artifact (data inspection only — no model construction, no `LayerAResilienceRequirements`, no `SolveSettings`, no `core.solve_eob`), Markdown/structural validation, and read-only Git inspection.

Not performed: `optimize()`, model construction, solves, canonical-input regeneration, production routing changes, source-code edits, test changes, commit, push, or tag.

## 14. Next required independent audit

An independent, read-only audit of this Registry v7.3 candidate is required before it can be accepted as the evidence source of truth, following the same pattern already used for Framework v7.3 (independent capability audit → freeze → pre-execution authorization). Only after that acceptance may a separate additive pass build and audit the new canonical reconstructed-mainline artifact and authorize same-artifact production routing.
