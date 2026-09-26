# Registry v7.4 Framework-alignment candidate checkpoint (Candidate R1)

**Date:** 2026-09-26
**Pass:** Task 2 — Registry v7.4 successor candidate authoring
**Disposition:** **LITERATURE / EVIDENCE REGISTRY V7.4 FRAMEWORK-ALIGNMENT SUCCESSOR — CANDIDATE R1**
**Pass type:** documentation / evidence-governance only; zero solves; zero code, data, model or parameter changes

This is a **producer** checkpoint for a new additive Registry v7.4 candidate. It does **not** declare the
candidate `CLOSED`, `ACCEPTED`, `FINAL`, or `PROMOTED`, and the authoring pass has no authority to do so.
An independent read-only audit is required before the candidate may become the evidence authority.

## 1. Formal version naming

| Item | Value |
|---|---|
| Formal future evidence-version name | **Registry v7.4** |
| Candidate revision identifier | **Candidate R1** — provenance revision only; **not** a formal evidence-version number |
| Candidate path | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` |
| Role of the missing `_r1` suffix | follows the existing first-candidate convention; a later correction must be additive as Candidate R2, never an overwrite of these bytes |

If and only if this candidate passes independent audit and closure, the accepted evidence authority is
named **Registry v7.4** — never "Registry v7.4 R1". Candidate terminology is used only for exact
repository identity, provenance, audits, hashes, and candidate lineage. No historical Registry artifact
was renamed.

## 2. Pre-authoring repository identity (verified before any mutation)

| Item | Verified value |
|---|---|
| Repository | `irischg/iris_thesis` |
| Branch | `thesis-v7` |
| Pre-authoring HEAD | `2fe2105180c68d9289eddc2668399687d4c49d2e` |
| Local `origin/thesis-v7` | `2fe2105180c68d9289eddc2668399687d4c49d2e` |
| Live remote `origin/thesis-v7` | `2fe2105180c68d9289eddc2668399687d4c49d2e` |
| Ahead / behind | 0 / 0 |
| Staged tracked files | 0 |
| Unstaged tracked modifications | 0 |
| Pre-existing unrelated untracked files | 8 — preserved; not cleaned, deleted, stashed, reset, or committed |

## 3. Immutable authorities re-verified from primary bytes before editing

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/research_framework_v7_4_2026-09-26_r2.md` | **CLOSED / ACCEPTED methodology authority**; alignment target; formal name **Framework v7.4** | 216186 | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | Framework v7.4 acceptance / lifecycle-closure evidence | 18809 | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` |
| `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | Framework v7.4 acceptance manifest | 15144 | `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33` |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | **CLOSED / ACCEPTED evidence predecessor**; current evidence authority until this candidate is accepted | 187796 | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| `docs/research_framework_v7_3_2026-09-23.md` | accepted methodology predecessor; immutable historical lineage | 181798 | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | accepted v7.3 methodology/evidence lifecycle closure | 12358 | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
| `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | governing provenance/lifecycle protocol | 19977 | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |

All seven hashes matched their expected values exactly. **Registry v7.3 R3 was re-hashed after authoring
and remains byte-identical** (`e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`). No
predecessor registry, failed candidate, historical checkpoint, audit, freeze, manifest, or result was
edited, repaired, renamed, or deleted.

## 4. Created artifacts

| Path | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | **Registry v7.4 Candidate R1** | 245125 | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| `docs/checkpoints/literature_evidence_registry_v7_4_framework_alignment_candidate_2026-09-26.md` | this candidate checkpoint | *recorded in the final report* | *recorded in the final report* |
| `results/provenance/literature_evidence_registry_v7_4_framework_alignment_candidate_r1/completion_manifest.json` | candidate completion manifest | *see manifest* | *see manifest* |
| `results/provenance/literature_evidence_registry_v7_4_framework_alignment_candidate_r1/package_manifest.json` | candidate package manifest | *see manifest* | *self-hash deliberately omitted* |

No acceptance artifact and no Registry v7.4 closure artifact was created.

## 5. Authoring method — how minimality was enforced

The candidate was produced by copying the accepted Registry v7.3 R3 bytes and then applying a fixed set of
**exact-anchor** replacements, each asserted to match its predecessor text **exactly once**. Anything not
matched by a declared anchor is inherited byte-for-byte. The complete anchor register is §6.

**Verification performed on the result:**

- Registry v7.3 R3 re-hashed: byte-identical.
- Source-record inventory (`## [Rxx]/[Txx]/[Ixx]/[Pxx]/[L1]` headings): **identical** to the predecessor —
  no literature or project record added, removed, renamed, or re-numbered.
- §16 Working bibliography block: **byte-identical** to the predecessor.
- Numeric-token sweep predecessor → candidate: **no numeric value lost**. The only new numeric content is
  (i) the \(\kappa\) full-precision and shorthand display forms of the already-accepted parameter,
  (ii) hashes / run identifiers of already-accepted artifacts, and (iii) new section numbers. **No model
  parameter was added or changed.**
- Markdown table-row integrity across the new §20: 0 column-count mismatches.

## 6. Anchor register — every substantive change and its authorized class

Authorized classes:
**A** = `FRAMEWORK_V7_4_CHANGE_A_ZERO_WINTER_ROLE_ALIGNMENT`;
**B** = `FRAMEWORK_V7_4_CHANGE_B_PV_EPISTEMIC_ROUTING_ALIGNMENT`;
**C** = `FRAMEWORK_V7_4_CHANGE_C_KAPPA_CLAIM_BOUNDARY_ALIGNMENT`;
**D** = `CURRENT_AUTHORITY_STATUS_UPDATE`;
**E** = `PROJECT_EVIDENCE_AUTHORITY_UPDATE`;
**F** = `PROVENANCE / VERSION PLUMBING`.

| # | Location | Change | Class |
|---:|---|---|---|
| 1 | Document header, formal-naming note, version lineage, source manifest, execution-time-vs-governance-status rule, supersession rule | rewritten for Registry v7.4 Candidate R1 identity; registers the accepted Framework v7.4 authority/closure/manifest, the accepted planning input, the accepted EOB and core-three, and the accepted Registry v7.3 R3 predecessor | F + D + E |
| 2 | §0 audit-status rule — `IMPLEMENTATION / VALIDATION PENDING` list | winter-PV sensitivity removed as a pending item; explicit v7.4 scoping note added stating the historical position and that **no substitute sensitivity replaces it** | A |
| 3 | §0 coding source-of-truth rule | v7.2 and v7.3 authority states past-scoped; current state set to Framework v7.4 (methodology) + Registry v7.3 R3 (evidence); this candidate marked candidate-only | D |
| 4 | [P1] P1-E superseded-box note | reconstructed planning-baseline assignment marked as continued unchanged under Framework v7.4; the v7.3 zero-winter stress/sensitivity role explicitly marked historical and the current v7.4 role stated inline | A + B |
| 5 | [P1] P1-E "Current role — under accepted Framework v7.3" | retitled to a historical record of the v7.3 decision and past-scoped; a new **"Current role — under accepted Framework v7.4"** subsection added covering the zero-winter current role, its five explicit negations, preservation requirements, historical truthfulness, and planning-layer routing | A + B |
| 6 | [P2] | new subsection **"\(\kappa\) historical-calibration / planning-use claim boundary"**: preserved production identity table (estimator, basis, sample, value at three display precisions, scripted-reproduction requirement), epistemic-layer separation, the prohibition on using reconstructed planning PV to redefine/re-estimate \(\kappa\), and the \(\kappa\) claim boundary including that R28–R29 limitations are undiminished | C |
| 7 | [P6] remaining implementation/validation gates | current execution state substituted for the v7.3-era list: EOB and core-three `CLOSED / ACCEPTED`, Full81 `NOT_YET_EXECUTED` as a distinct state, winter-PV sensitivity removed with historical scoping, accepted planning input named | D + A + E |
| 8 | [P7] P7-C interpretation/consequence paragraph | canonical-rebuild requirement past-scoped and recorded as **satisfied**, pointing to P7-E; artifact still immutable and not renamed | E |
| 9 | [P7] P7-C role statement | role restated as **historical promotion-source lineage / project evidence only**; the v7.3-era `NOT_YET_CREATED / NOT_YET_AUTHORIZED` canonical-artifact status marked historical and no longer current | E + D |
| 10 | [P7] | new subsection **P7-E** registering the accepted planning input (path, SHA-256, role, 8,760 rows), the accepted EOB run, the accepted core-three run with LOW/CENTRAL/HIGH coordinates, the execution-time-vs-governance status rule, the Full81 distinction, and the project-evidence claim boundary | E + D |
| 11 | [P7] evidence-role summary table | current roles restated; rows added for the zero-winter treatment as such, the accepted planning input, and the accepted EOB/core-three, each with its "not authorized to claim" boundary | A + B + E |
| 12 | §12 heading | retitled to note alignment to accepted Framework v7.4 | F |
| 13 | §12 reconstructed-PV / zero-winter rows | reconstructed row restated with the accepted artifact, the four required and four prohibited descriptions, and the full planning-consumer list; new **epistemic-routing** row; zero-winter split into an explicit **current-role** row and a **historical-roles** row | B + A |
| 14 | §12 \(\kappa\) rows | production-pinned identity added with the display-precision equivalence; new row for observed-only historical calibration and the reconstructed-PV prohibition; billing-proxy row extended with the full claim boundary and the R28–R29 non-override statement | C |
| 15 | §14 「可以寫」 | v7.3 zero-winter bullet past-scoped; eight bullets added covering the Framework v7.4 required thesis-language boundary, the assigned-zero-availability wording, the two-layer routing, the single planning identity, the retrospective-not-forecast guardrail, and the two \(\kappa\) boundary statements | A + B + C |
| 16 | §14 「不要寫」 | corrected-17b entry updated to the current artifact status; eleven prohibitions added covering re-mandating zero-winter, equal-status baseline, erasing v7.3 history, reconstructed-for-observed substitution in historical calibration, hybrid routing, forecast/information-advantage claims, \(\kappa\)-as-physical-validation, the manifest-status conflation, and the core-three/Full81 conflation | A + B + C + D |
| 17 | §15 heading | retitled to note that current status is aligned to accepted Framework v7.4 | F |
| 18 | §15 \(\kappa\) bullet | display-precision forms and the Change C claim boundary added | C |
| 19 | §15 Blocker 2 bullet | v7.3 role statement past-scoped; current v7.4 zero-winter role added | A |
| 20 | §15 promotion bullet + new status bullet | v7.3-era `NOT_YET_*` statuses replaced by the accepted planning-input identity; new bullet giving the full current governance/execution status | D + E |
| 21 | Maintenance guardrails | corrected-17b guardrail updated; eight guardrails added covering zero-winter symmetry (neither re-mandate nor erase), no substitute sensitivity, planning/historical routing discipline, the \(\kappa\) prohibitions, and the two status-conflation rules | A + B + C + D |
| 22 | §17 heading + scoping banner | §17 relabelled the **inherited historical record**, with §20 named as the current alignment and in-place rescoping preferred over a distant disclaimer | F |
| 23 | §17.1 | v7.3 zero-winter clause past-scoped; inline current-role update box added | A |
| 24 | §17.5 | role table extended with a **v7.4 (current, accepted)** column; v7.2/v7.3 entries retained as historical provenance | A |
| 25 | §17.7 | rebuilt as a two-column **historical snapshot vs current state** table covering Framework v7.3/v7.4, Registry lineage, accepted planning input, routing, Step 17c, EOB, core-three, representative cases, 11A–C, Full81, and the three not-yet-performed governance stages | D + E |
| 26 | §17.9 | relabelled a historical R3-vs-Framework-v7.3 audit with a scope banner; the zero-winter, canonical-input and Final81 rows marked **SUPERSEDED** or restated; sweep-scope paragraph past-scoped | D |
| 27 | §17.10 | R3 inventory marked historical; the Candidate R1 inventory location named | F |
| 28 | §17.11 | retitled as the Registry v7.3 R3 historical disposition; records that R3 has since been accepted; points to §20.9 for this document's disposition | D + F |
| 29 | §18.5 | Registry v7.2-as-last-accepted sentence explicitly past-scoped, with the current Registry v7.3 R3 acceptance stated | D |
| 30 | §19.2 | the five quoted R3 correction bullets explicitly marked a historical record of that correction, not current authority | D |
| 31 | §19.3 | past-scoped, with the current Registry v7.3 R3 `CLOSED / ACCEPTED` status stated | D |
| 32 | **New §20** | Framework v7.4 evidence-role / claim-boundary alignment freeze: §20.0 identity and authorized scope; §20.1 Change A; §20.2 Change B; §20.3 Change C; §20.4 current authority and execution status with the status-semantics rule; §20.5 claim-to-evidence coverage and the evidence-gap result; §20.6 preserved literature/evidence roles; §20.7 leakage / information-advantage / claim audit; §20.8 inherited-unchanged freeze inventory; §20.9 candidate disposition and execution counters | A + B + C + D + E + F |

**No change outside classes A–F was made.** No fourth scientific change category exists in this candidate.

## 7. Change-magnitude counters

| Counter | Value |
|---|---:|
| New external literature sources | **0** |
| Removed or re-roled external literature sources (outside A/B/C) | **0** |
| New model equations | **0** |
| Changed model equations | **0** |
| New numerical parameters | **0** |
| Changed numerical parameters | **0** |
| New methodology decisions beyond accepted Framework v7.4 A/B/C | **0** |
| Predecessor bytes modified | **0** |
| Historical/frozen artifacts modified | **0** |

The \(\kappa\) forms `1.0103668594376984`, `1.0103668594` and `1.01037` are the **same accepted parameter
at different display precision**, recorded to fix the Change C claim boundary; this is not a parameter
change.

## 8. Framework v7.4 claim-to-evidence coverage result

| Framework v7.4 change | Registry representation | Result |
|---|---|---|
| **A** zero-winter current role | §20.1; [P1] P1-E current-role subsection; [P7] Step 17a / corrected 17b / Step 17c historical validation and adjudication evidence; §12 rows; §14; §17.5 | **COVERED** |
| **B** observed-vs-planning PV routing | §20.2; existing [R21]–[R23], [R32]–[R33], [I5] reconstruction/validation literature with unchanged roles; [P1] P1-C/P1-E; [P7] P7-A/C/D; [P7] P7-E accepted planning artifact; §12 routing row | **COVERED** |
| **C** \(\kappa\) claim boundary | §20.3; [P2] claim-boundary subsection; existing [R28], [R29] temporal-resolution evidence with unchanged roles; [I1]/[I3]/[I4]; §12 \(\kappa\) rows; §15 | **COVERED** |

**Evidence-gap result:** no accepted Framework v7.4 claim was found to lack a defensible basis in existing
literature, official sources, accepted project evidence, or accepted primary artifacts. No new external
literature was required, sought, or added, and no source was broadened beyond what it supports. Every
NTUST-specific fact — exact parameter values, the promotion decision, the accepted reconstructed artifact,
and the EOB/core-three results — is attributed to **project evidence**, never to external literature.

## 9. Stale-status / contradiction audit of this candidate's bytes

A full-text sweep was run over the candidate for: `Framework v7.2`, `Framework v7.3`, `Framework v7.4`,
`Registry v7.2`, `Registry v7.3`, `candidate only`, `current authority`, `source of truth`,
`NOT_YET_CREATED`, `NOT_YET_AUTHORIZED`, `NOT_YET_ACCEPTED`, `NOT_YET_EXECUTED`, `NOT_YET_PERFORMED`,
`pending`, `future canonical`, `promotion source`, `EOB`, `core-three`, `81-point`, `Full81`,
`zero-winter`, `zero PV`, `zero availability`, `conservative stress`, `stress/sensitivity`,
`winter PV sensitivity`, `paired sensitivity`, `alternative planning baseline`, `17a`, `17b`, `17c`,
`Step 17`, \(\kappa\), and `reconstructed PV`.

Every material occurrence classifies as:

| Class | Meaning | Count |
|---|---|---:|
| **A** | correct current v7.4 / v7.3 authority state | many |
| **B** | clearly historical provenance, explicitly past-scoped | many |
| **C** | correct future governance state | many |
| **D** | **stale / ambiguous contradiction** | **0** |

Two Class-D occurrences found in the first authoring iteration were corrected in place before this
checkpoint was written: (i) the §17.9 rows whose cross-references still asserted
`NOT_YET_CREATED / NOT_YET_AUTHORIZED` and the v7.3 zero-winter role as current; and (ii) the §19.2 quoted
correction bullets, which read as current authority. Both are now explicitly scoped. **No locally
current-looking stale statement is left to be cured by a distant disclaimer** — every rescoping is
adjacent to the text it scopes.

## 10. Leakage / information-advantage / claim audit

| Failure mode | Result |
|---|---|
| reconstructed PV mislabeled observed | excluded (§20.2, §20.7, [P1] P1-E, §14) |
| retrospective reconstruction mislabeled online forecast | excluded (§20.2 guardrail, §14) |
| historical calibration using future planning reconstruction | excluded (§20.3 prohibition, [P2], guardrails) |
| look-ahead hidden as empirical evidence | excluded (two-layer routing, §20.2) |
| perfect-information benchmark mislabeled deployable operation | excluded (inherited Layer B capability-upper-bound framing, not expanded) |
| \(\kappa\) mislabeled sub-hourly physical validation | excluded (§20.3, [P2], §12, §14) |
| literature precedent overstated as exact NTUST validation | excluded (§20.5, §17.8, per-source boundary text inherited unchanged) |
| planning evidence overstated as historical measurement truth | excluded (§20.2, §14, [P7] boundary columns) |
| implementation status conflated with methodology authority | excluded (§0 coding rule, §20.0, §20.4 status-semantics rule, §17.7) |

## 11. Frozen decisions reaffirmed

A1–A4 **CLOSED**; B1–B2 **CLOSED**; Gate 1 and Gate 2 **CLOSED**. Research questions, Layer A/B/DG
boundaries, the \(\alpha\) and \(\beta\) grids, the \(9\times9=81\) universe, valid-start semantics, LFP
chemistry, SOC 10–90%, \(\eta_c=\eta_d=0.90\), the AC/PCS power boundary, the battery-side energy state,
the reserve formulation, outage replay semantics, tariff treatment, annual regular contract capacity, the
degradation formulation, the rainflow role, the discount rate, the horizon, the monetary basis, the PNNL
cost-package choice, `surplus_pv_recharge=False`, and the Layer A equations are all inherited unchanged
(§20.8). No closed decision was reopened, and no literature was reinterpreted to reopen one.

## 12. Execution counters for this pass

| Counter | Value |
|---|---:|
| `optimize()` calls | **0** |
| Model constructions | **0** |
| MILP solves | **0** |
| EOB reruns | **0** |
| core-three reruns | **0** |
| Full81 runs | **0** |
| Sensitivity solves | **0** |
| Code changes | **0** |
| Data changes | **0** |
| Accepted numerical result changes | **0** |
| Tags created | **0** |
| Pushes performed | **0** |

No optimization model was instantiated for evidence checking.

## 13. Governance state after this pass

| Layer | State |
|---|---|
| Framework v7.4 | **CLOSED / ACCEPTED** — current methodology authority |
| Registry v7.3 R3 | **CLOSED / ACCEPTED** — current evidence authority, pending independent audit of this candidate |
| Registry v7.4 Candidate R1 | **CANDIDATE ONLY** — not accepted; not self-accepted; cannot self-promote |
| Independent Registry audit | **REQUIRED** |
| Registry v7.4 acceptance / closure artifacts | **NOT CREATED** |
| Accepted reconstructed planning input | **CLOSED / ACCEPTED** |
| Accepted EOB | **CLOSED / ACCEPTED** |
| Accepted core-three | **CLOSED / ACCEPTED** |
| Full81 | `NOT_YET_EXECUTED` — not authorized |
| Layer A robustness / preregistration checkpoint | `NOT_YET_CREATED` — not authorized |
| Final cross-document alignment audit | `NOT_YET_EXECUTED` |
| Production-authority re-freeze under v7.4 | `NOT_YET_PERFORMED` |

## 14. Disclosed observation (not a Registry defect; outside this pass's authorized scope)

`docs/ai_handoff/CURRENT_STATE.md` §1 still names Framework v7.3 as the methodology source of truth and
was last updated on 2026-09-24, before Framework v7.4 acceptance. That file is a living
implementation-status document outside the authorized artifact set for this pass, and it was **not**
edited here. It is recorded so the discrepancy is not mistaken for a Registry contradiction, and it
belongs to the later cross-document alignment stage.

## 15. Disposition

> **LITERATURE / EVIDENCE REGISTRY V7.4 FRAMEWORK-ALIGNMENT SUCCESSOR — CANDIDATE R1**

This disposition means only that the candidate document expresses the three authorized Framework v7.4
alignment categories and their boundaries, with a zero Class-D stale-status self-audit result. It is
**not** evidence acceptance, **not** artifact promotion, **not** routing authorization, **not** a
production-authority re-freeze, and **not** authorization for Layer A preregistration or Full81.

**Registry v7.4 Candidate R1 is not the accepted evidence authority and cannot self-promote. An
independent read-only audit is required.**
