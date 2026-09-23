# Literature / Evidence Registry v7.3 **R2** — Reconstructed-PV Alignment — Candidate Checkpoint

**Date:** 2026-09-23
**Pass:** RERUN-2 Step 2C-R2 (additive successor correction after independent STOP)
**Disposition:** **LITERATURE / EVIDENCE REGISTRY V7.3 R2 RECONSTRUCTED-PV ALIGNMENT — CANDIDATE PASS**

This checkpoint does **not** declare Registry v7.3 R2 CLOSED or ACCEPTED. R2 is a candidate. It is not
self-accepting and does not become the evidence source of truth until an independent, read-only audit
accepts it. Registry v7.2 remains the accepted evidence source of truth until then.

Governance: `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md`.

---

## 1. Why R2 exists

The R1 candidate failed independent acceptance. R1 was **not** edited, repaired, renamed, or deleted.
R2 is a new file created alongside it.

R1's two acceptance-critical defects, both re-confirmed against R1's primary bytes at the start of this
pass (locations re-derived independently, not taken from the prior report):

**Defect 1 — unscoped P1-E wording (Category D).** In R1 (`e06f5a1e…`):

| R1 line | Text | Problem |
|---|---|---|
| 1675 | `Mainline remains:` | present tense, unscoped |
| 1678 | `\boxed{PV_t^{base}=0}` | contradicts accepted Framework v7.3 §4.1.3 |
| 1681 | `for these long-unavailable intervals, described as conservative zero **availability**, …` | present tense, unscoped |
| 1683 | `A CWA winter alternative must first pass … and remains a separate sensitivity branch.` | present tense, role inverted under v7.3 |
| 1685 | forward reference | did **not** scope the above; its own text says it "does not alter" the finding and that the finding "remains true under Framework v7.3" |

Accepted Framework v7.3 boxes the opposite assignment for the identical index set at
`docs/research_framework_v7_3_2026-09-23.md` lines 506–510:
`PV_t^{base}=\widehat{PV}_t^{winter,recon}, t∈{pre_system, missing_winter}` — the same 600 h + 863 h =
1,463 h. Same symbol, same index set, same display form, opposite value.

**Defect 2 — inaccurate R1 self-audit certification.** R1's checkpoint certified `D = 0` on a
description of R1's own bytes that was wrong in three respects: it placed the boxed equation at line
1722 (which in fact holds an unrelated [P2] calibration sentence — the equation is at line 1678); it
asserted the forward reference "immediately followed" the equation (two paragraphs intervene, at 1681
and 1683); and it treated that forward reference as scoping the equation, which the reference's own
text disclaims. R1's Sec 17.3 coverage matrix and Sec 17.9 contradiction sweep surveyed only Sec 12,
Sec 14 and P7, and omitted P1-E.

**Correction to the prior independent report:** that report cited the "conservative zero availability"
sentence at R1 line 1680. Re-derived from primary bytes it is at line **1681**. The defect finding is
unaffected; the location is corrected here for the record.

---

## 2. Files created (nothing else written)

| File | Role |
|---|---|
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | R2 successor candidate Registry |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_r2_2026-09-23.md` | this checkpoint |

No other file in the repository was created, modified, or deleted.

---

## 3. Primary hashes (independently computed this pass)

| Artifact | SHA-256 | State |
|---|---|---|
| `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` | accepted authority — unchanged |
| `docs/research_framework_v7_2_2026-08-24.md` | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` | historical — unchanged |
| `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` | accepted predecessor — unchanged |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` | **failed R1 — byte-identical, unedited** |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_2026-09-23.md` | `301b931a3b7ea4b0c981079789e66a69e5571294a0d29467bd0c6c262c17fe2d` | **failed R1 checkpoint — byte-identical, unedited** |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` | **R2 candidate (this pass)** |
| corrected 17b parquet | `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9` | re-verified identical before and after read-only inspection |
| 17a decision JSON | `454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594` | unchanged |
| 17c paired JSON | `b8acd3027c3c1db31bd8840cf0ea6af7f67ea784fcd856bb3dcd2e3317677ca5` | unchanged |

---

## 4. Diff characterisation (accurate wording)

R2 is an **additive successor candidate with scoped replacements and deletions**; the historical
predecessor and the failed R1 candidate remain byte-identical.

| Comparison | Insertions | Deletions | Hunks (default `-U3`) |
|---|---|---|---|
| Registry v7.2 → R2 | 375 | 20 | 10 |
| Failed R1 → R2 | 157 | 27 | 11 |

R2 is explicitly **not** "entirely additive": it deletes and replaces text, by design, because the R1
failure could only be cleared by replacing unscoped wording. R2 line count: 2,740 (R1: 2,610;
v7.2: 2,385).

---

## 5. P1-E correction (Defect 1)

P1-E is now split into two explicitly labelled subsections.

**Historical role — under Framework v7.1/v7.2 (superseded; retained as historical evidence).** The
boxed equation is retained verbatim, preceded by a bold `HISTORICAL V7.1/V7.2 MAINLINE DEFINITION —
SUPERSEDED FOR CURRENT V7.3 METHODOLOGY` statement, annotated inline in the equation itself
(`\qquad\text{(HISTORICAL v7.1/v7.2 mainline definition — SUPERSEDED)}`), and immediately followed by a
blockquote that states the current §4.1.3 assignment `PV_t^{base}=\widehat{PV}_t^{winter,recon}` for the
same index set and records that the zero-availability treatment is retained as the conservative
stress/sensitivity case. Nothing was deleted from the historical content.

**Current role — under accepted Framework v7.3.** States the role reversal explicitly, cites Step 17a's
historical `PASS_FOR_SENSITIVITY` verdict as preserved unchanged, and closes with a "What is unchanged"
paragraph confirming that the Scripts 02-05 finding is not altered, weakened, or re-audited — it remains
true and is the reason Step 17a was required.

**Sensitivity-branch wording (§3 of the task).** The R1 sentence "…and remains a separate sensitivity
branch" is now past-scoped: "Under that historical framework a CWA winter alternative had first to pass
block/month holdout validation, and **for as long as that validation was outstanding** it remained a
separate sensitivity branch." The v7.3 reversal is stated separately in the "Current role" subsection.
Step 17a's verdict is not rewritten anywhere.

**Verification:** the string `Mainline remains:` no longer appears in R2 in any PV context. Its two
remaining occurrences are (a) line 1914, an unrelated Layer A reserve-floor sentence inherited unchanged
from v7.2, and (b) §18.2, where R1's defective wording is quoted verbatim inside an explicit
failed-candidate record.

---

## 6. Framework → Registry coverage matrix (rebuilt from scratch)

Re-derived for R2 from a fresh read of accepted Framework v7.3 primary bytes. R1's "9/9" was **not**
reused, and neither was the prior independent audit's 13/14 matrix. Recorded in Registry R2 §17.3 and
§17.9.

All fourteen required mappings are covered: (1) reconstructed full-year PV = mainline; (2) zero-winter =
conservative stress/sensitivity; (3) observed vs planning-baseline PV; (4) long-block reconstruction
validation; (5) weather-informed reconstruction role; (6) reconstruction epistemic boundary; (7) same
reconstructed artifact for economics + Layer A; (8) R(α,β) / P_out / binding-window semantics; (9)
Layer A outage replay semantics; (10) baseline Layer B semantics; (11) billing calibration remains
observed-data based; (12) sensitivity-role reversal; (13) limitation / claim boundary; (14) current
implementation authorization state.

**P1-E is now a required mapping location** for four of these — current reconstructed-PV mainline role,
historical zero-winter role, validation requirement, and sensitivity-role reversal — and each such row
names **both** the historical evidence text and the current v7.3 evidence-role interpretation. Result:
no Framework/Registry contradiction.

---

## 7. Stale-wording audit — re-derived from R2 bytes

R1's counts (229 / 138 / A100 / B26 / C17) were **not** reused. Search terms as specified, matched
case-insensitively as substrings over all 2,740 lines of R2.

**Universe: 302 matched lines; 302 unique line texts; 286 core (length > 40).**

| Term | Lines | Term | Lines | Term | Lines |
|---|---|---|---|---|---|
| winter | 68 | reconstruction | 50 | 17b | 19 |
| missing_winter | 7 | synthetic | 1 | 17c | 22 |
| pre_system | 7 | CWA | 49 | sensitivity | 103 |
| zero winter | 0 | GHI | 24 | mainline | 113 |
| zero-winter | 18 | long block | 2 | canonical | 26 |
| zero availability | 4 | long-block | 18 | | |
| zero-availability | 4 | 17a | 22 | | |
| reconstructed | 65 | | | | |

Classification of the relevant subset: **A ≈ 141, B ≈ 44, C ≈ 22, D = 0.** A line may carry more than
one clause-level category.

### 7.1 Exact D = 0 derivation

A mechanical over-broad detector was run over the matched universe, flagging any line that (a)
co-occurs "zero" and "mainline", (b) contains "sensitivity branch", (c) contains "remains" near "zero"
or "sensitivity", or (d) contains `PV_t^{base}=0`. It flagged **27** lines. Each was then adjudicated
against the Category D definition (asserts the superseded role as current). Twenty were scoped by
in-line tokens. The remaining seven were adjudicated individually:

| R2 line | Flagged text | Adjudication |
|---|---|---|
| 2117 | table row `pv_reconstruction_method \| unavailable_zero_mainline (×1,463) \| **No** — inherited zero-mainline label` | **B** — verbatim artifact field value in a table whose third column answers "No"; not a role assertion |
| 2125 | "over the full year `pv_reconstruction_method` reads `observed` (7,287 h), `unavailable_zero_mainline` (1,463 h)…" | **B** — verbatim artifact field values |
| 2595 | heading `## 17.5 Mainline / zero-winter role alignment table` | not an assertion |
| 2599 | `Reconstructed full-year PV … \| sensitivity branch only; not mainline \| **mainline best-estimate planning baseline**` | **B/A** — column-scoped; the table header row is `\| Role \| v7.2 (historical) \| v7.3 candidate (current) \|` |
| 2645 | `Layer B baseline \| same reconstructed-mainline artifact, not zero-winter … \| YES` | **A** — asserts the correct current role |
| 2691 | quoted `Mainline remains:` + boxed `PV_t^{base}=0` | **B** — inside §18.2, explicitly framed as R1's failed wording being documented |
| 2696 | quoted "remains a separate sensitivity branch" | **B** — same §18.2 failed-candidate record |

**Category D = 0.**

One line did require correction during this pass and is no longer Category D: the P7-D **Design**
sentence, which in R1 read "solved under (i) the mainline (zero-winter) PV input and (ii) the corrected
reconstructed-winter-PV sensitivity input". It now reads "(i) the **then-mainline v7.2 zero-winter** PV
input and (ii) the corrected reconstructed-winter-PV input, which under Framework v7.2 was the
**sensitivity** arm and under accepted Framework v7.3 is the **mainline** arm", and notes that the run
artifact's own `mainline_comparators` / `winter_pv_sensitivity` keys are v7.2-era labels preserved
unchanged.

---

## 8. Legacy provenance-field disclosure (corrected and expanded)

R1 named a single field. R2 enumerates the full set, independently read from the corrected 17b parquet's
primary bytes over the 1,463-hour block. **The parquet was not mutated** — its SHA-256 was recomputed
after inspection and is unchanged.

| Field | Value over the block | Consistent with a reconstructed mainline artifact? |
|---|---|---|
| `pv_reconstruction_method` | `unavailable_zero_mainline` (×1,463) | No |
| `pv_reconstructed` | `False` (×1,463) | No |
| `pv_long_unavailable_assumption` | `True` (×1,463) | No |
| `pv_cwa_model` | null/NaN (×1,463) | No |
| `artifact_role` | `winter_pv_sensitivity_only` (file-wide, ×8,760) | No — and correctly so |
| `winter_pv_sensitivity_method` | `cwa_hourly_ghi_ratio_median_all_eligible_v7_2` | Yes |
| `winter_pv_sensitivity_applied` | `True` (×1,463) | Yes |

Full-year context: `pv_reconstruction_method` = `observed` (7,287 h) / `unavailable_zero_mainline`
(1,463 h) / `cwa_hourly_ghi_ratio_median_leave_target_day_out` (10 h); `pv_reconstructed = True` on
exactly those 10 P1-D short-gap hours.

R2 states the consequence the task requires: these fields reflect the historical sensitivity-branch
construction, and are a substantive reason the future canonical artifact must be **newly built** under
mainline semantics rather than produced by renaming this parquet — a rename would leave a file whose own
provenance fields assert a sensitivity-branch identity while being routed as production mainline.

**Additional precision correction.** R1 stated `winter_pv_sensitivity_method` was set "for all 1,463
rows". It is in fact populated file-wide on all 8,760 rows as a file-level label; it is
`winter_pv_sensitivity_applied` that delimits the 1,463-hour block. R2 states this correctly.

---

## 9. P7-D numerical correction

Deltas independently re-derived from `paired_sensitivity_comparison.json` primary bytes. R1's wording
implied both cases share the same `pv_used_kwh` increase; that is false for EOB.

| Quantity (winter-PV-sensitivity − mainline) | EOB | `a0.80_b08` |
|---|---|---|
| `pv_available_kwh` delta | +39,484.422494 | +39,484.422494 |
| `pv_used_kwh` delta | **+39,482.731136** | +39,484.422494 |
| `pv_curtailment_kwh` | 15.308642 → 17.000000 (+1.691358) | 0.0 → 0.0 (0.0) |
| `grid_import_kwh` delta | −39,485.597556 | −39,484.422494 |

The available-energy delta is identical across both cases and equals the P7-C block figure. The EOB
`pv_used_kwh` shortfall of 1.691358 kWh is exactly its curtailment increase; the identity
`Δavailable − Δused − Δcurtailment = 0` holds to floating-point residual (1.8e-11 for EOB, exactly 0.0
for `a0.80_b08`). The difference is curtailment-scale only (0.0043% of the block), and **the scientific
interpretation is unchanged** — R2 says so explicitly.

---

## 10. Script 14a reference audit

Occurrences were classified, not mechanically removed. `scripts/14a_build_production_economic_interface.py`
exists in the repository, and accepted Framework v7.3 line 3719 still carries the corresponding gate as
an unchecked item, so the gate is genuinely still pending.

| R2 line | Text | Classification | Action |
|---|---|---|---|
| 52 | "…machine-readable production conversion仍是 Script 14a 前置 implementation gate" | CURRENT_REQUIRED_REFERENCE | none |
| ~2380 | "**Next economic implementation gate**：Script 14a需建立/驗證…" | CURRENT_REQUIRED_REFERENCE | none |
| ~2481 | "Keep raw nominal tariff evidence immutable; Script 14a normalization must create a separate optimization layer…" | CURRENT_REQUIRED_REFERENCE | none |
| ~2055 | P6 gate row, identifier absent: "production-interface preflight, including the constant-NTD-2023 Taipower tariff layer" | HISTORICAL_REFERENCE / framework-aligned | none |

No STALE_STATUS_REFERENCE was found, so **no textual correction was made**.

**Disclosed unevenness (explicitly, rather than claiming zero incidental changes):** R1 removed the
`Script 14a` identifier from one of four occurrences — the P6 "Remaining implementation/validation
gates" row — while leaving the other three intact, and R1's checkpoint §5 item 9 described only the
winter-PV re-scoping in that hunk and did not disclose the identifier removal. R2 inherits this uneven
pattern unchanged. It is framework-aligned (accepted Framework v7.3 removed the identifier from the
identical gate line at FW L119 and contains zero `14a` tokens) and it changes no evidence role, but the
Registry is now internally uneven in how it names that gate. This is recorded here as a known,
non-blocking inconsistency for the acceptance authority to rule on, not silently carried.

---

## 11. Additional inherited defect found and corrected

R1 contained a **duplicated, empty `## [L1]` heading** at R1 line 2041, produced by its [P7] insertion:
the orphan heading was followed immediately by `---` and then `## [P7]`, with the real [L1] heading and
its body re-emitted afterwards. Registry v7.2 has exactly one `## [L1]` heading; R1 had two.

R2 removes the orphan heading. R2 has exactly one `## [L1]` heading and one `## [P7]` heading, and the
[L1] block is now **byte-identical to Registry v7.2's**
(`2d0da518ad5e98cbd30a24aa098508098b55fe2f0ecfa567fff07507d7576bd5`, bounded to the next heading).

This is a document-integrity correction that restores the predecessor's structure. It changes no
evidence role and no content.

---

## 12. Non-PV evidence preservation

Every listed record was compared block-by-block against Registry v7.2 and is **byte-identical** in R2:

`R20` (degradation / Xu), `R21`, `R22`, `R23`, `R28`, `R29` (temporal-resolution limitation), `R31`
(rainflow), `R32`, `R33`, `R34` (scale economics), `R35`, `R36`, `T2` (PNNL cost), `T4`, `T5`, `I5`,
`P2` (billing-demand calibration / κ), `P3`, `P4`, `P5`, `L1`.

A1, A3, A4, B1, B2, Gate 1, Gate 2, tariff methodology, billing-demand calibration, degradation, PNNL
scale roles, monetary basis, rainflow role and SOC20–80 role are unchanged. A2 is affected only through
the authorized reconstructed-PV input-role implication. **No unrelated evidence-role change.**

---

## 13. Current authorization state (unchanged, restated in R2 §17.7)

| Layer | State |
|---|---|
| Framework v7.3 | `CLOSED / ACCEPTED` |
| Registry v7.3 R1 | **SUPERSEDED** — failed independent acceptance; immutable provenance |
| Registry v7.3 R2 | **`CANDIDATE PASS`** — not yet independently accepted |
| Canonical reconstructed-mainline input | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` |
| Production routing | `NOT_YET_AUTHORIZED` |
| Step 17c EOB | promotion / adjudication candidate evidence only |
| Representative cases | NOT CLOSED UNDER V7.3 |
| Steps 11A / 11B / 11C | NOT CLOSED UNDER V7.3 |
| Final81 | NOT AUTHORIZED UNDER V7.3 |

No downstream completion is claimed or fabricated.

---

## 14. Repository state

Identical before and after this pass, except for the two new R2 files.

| Item | Value |
|---|---|
| Branch | `thesis-v7` |
| HEAD | `28b0e780c3b298cd88c02e218a99fe3463ff496c` (unchanged) |
| Origin | `origin/thesis-v7`, 0 ahead / 0 behind |
| Staged | none |
| Tracked modifications | none |
| Tags at HEAD | none |
| Untracked before | 10 files |
| Untracked after | 12 files (the 10 pre-existing, plus the two new R2 files) |

No commit, no push, no tag. R1 Registry and R1 checkpoint re-hashed after the pass and confirmed
byte-identical.

---

## 15. Zero-solve confirmation

**Performed:** reading primary bytes; independently recomputing SHA-256 (never trusted from any prior
report or from R1); `git` read-only inspection; textual diffing; whole-Registry search and
classification; one read-only `pandas.read_parquet` inspection of the corrected Step 17b candidate
(data inspection only); JSON reads of the 17a decision, 17c paired comparison, 17c run manifest and 17c
completion manifest; Markdown authoring of the two new R2 files.

**Not performed:** `optimize()`, model construction, any Gurobi or other solve, production rerun,
canonical-input regeneration, production-routing change, source-code edit, test edit, edits to any
historical or frozen artifact, edits to either R1 artifact, commit, push, or tag.

---

## 16. Next required gate

An **independent, read-only acceptance audit of Registry v7.3 R2**, performed by an auditor who did not
produce it. The candidate author cannot self-accept.

That audit should re-derive, at minimum: the R1-immutability check; the P1-E historical/current
separation; the rebuilt Framework→Registry coverage matrix; the D = 0 stale-wording derivation in §7.1
above; the legacy provenance-field enumeration; the P7-D deltas; and the non-PV preservation set. It
should also rule explicitly on the disclosed Script 14a unevenness recorded in §10.

Only after R2 is accepted may a separate additive pass build and audit the new canonical
reconstructed-mainline artifact and authorize same-artifact production routing. The subsequent gate
after that remains the v7.3 Framework merge audit + Registry merge audit + Framework–Registry alignment
audit. None of those artifacts were created in this pass.
