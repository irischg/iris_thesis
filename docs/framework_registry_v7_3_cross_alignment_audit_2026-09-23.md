# Framework v7.3 ↔ Literature / Evidence Registry v7.3 R3 Cross-Alignment Audit

**Project:** Iris Thesis  
**Audit date:** 2026-09-23  
**Audit mode:** Read-only bilateral methodology/evidence alignment audit  
**Verdict:** **PASS / CLOSED**

## 1. Scope

This audit checks whether the accepted methodology authority and accepted evidence authority are mutually consistent:

- Framework: `research_framework_v7_3_2026-09-23.md`
- Registry: `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`

It focuses on high-risk cross-document boundaries where an evidence registry can accidentally contradict methodology, overclaim project evidence, or misstate implementation status.

This audit does **not** verify repository branch/HEAD/staging state and does **not** itself authorize production solves or routing.


## Current accepted authority state at audit completion

- **Current methodology authority:**  
  `research_framework_v7_3_2026-09-23.md`  
  SHA-256: `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a`  
  Status: `CLOSED / ACCEPTED`

- **Current evidence authority:**  
  `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`  
  SHA-256: `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`  
  Status: `CLOSED / ACCEPTED`

- Registry v7.3 R1 and R2 are **FAILED immutable provenance only** and must not be used as current evidence authority.
- Registry v7.2 is the **historical accepted predecessor**, superseded by Registry v7.3 R3 as the current accepted evidence authority.
- Framework v7.2 is the **historical accepted predecessor**, superseded by Framework v7.3 as the current accepted methodology authority.
- The accepted Framework v7.3 and Registry v7.3 R3 primary files remain byte-identical; this authority statement records the external lifecycle state after independent acceptance and does not rewrite either primary artifact.

## 2. Primary artifact identity

| Authority | Artifact | SHA-256 |
|---|---|---|
| Methodology | `research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| Evidence | `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |

Hashes were recomputed from the primary bytes available in the project environment during audit packaging.

## 3. Authority separation

The pair maintains the required authority split:

- Framework owns methodology decisions and formal model requirements.
- Registry owns literature / institutional / project-evidence support, evidence roles, and claim boundaries.
- Project validation evidence does not self-promote into methodology authority.
- External literature does not substitute for NTUST-specific empirical validation.

No competing methodology authority is identified in the Registry.

## 4. Reconstructed-PV mainline alignment

Both authorities agree that:

- reconstructed full-year PV, including the 1,463-hour prolonged unavailable block, is the v7.3 **best-estimate planning mainline**;
- prior zero-winter treatment is a **conservative stress / sensitivity**;
- reconstruction is model-based / weather-informed and is not observed meter data, exact ground truth, or exact recovery.

**Result: PASS**

## 5. Historical zero-winter wording

Registry R3 retains the historical v7.1/v7.2 boxed zero-winter equation but labels it historical / superseded and places the current v7.3 reconstructed assignment alongside it.

It does not function as a competing current prescription.

**Result: PASS**

## 6. Same-artifact / no-hybrid rule

Framework requires a common reconstructed-PV artifact identity for:

- EOB / economic optimization;
- Layer A `R(alpha,beta)`;
- `P_out(alpha)`;
- binding-window classification;
- outage replay;
- baseline Layer B.

Registry R3 restates the same boundary and explicitly avoids claiming that routing compliance is already proven.

**Result: PASS**

## 7. Layer A / Layer B stage semantics

Aligned distinction:

- Layer A analytical-consistency replay: no outage PV-surplus recharge;
- Layer B event capability replay: may allow outage PV-surplus recharge under its existing rules.

This stage distinction is not treated as permission to use different baseline PV identities.

**Result: PASS**

## 8. Observed vs reconstructed data boundary

Framework separates:

- observed data for historical billing calibration; and
- planning-baseline / available data for annual planning.

Registry P2 preserves the observed-data billing-calibration formulation and does not substitute reconstructed planning PV into the historical `kappa` calibration.

**Result: PASS**

## 9. Long-block validation boundary

Both documents preserve the rule that:

- short-gap validation alone does not validate the 1,463-hour prolonged block;
- separate long-block/monthly holdout validation was required;
- Step 17a supplies that separate validation evidence within its original `PASS_FOR_SENSITIVITY` acceptance boundary.

**Result: PASS**

## 10. Step 17a / 17b / 17c evidence roles

Aligned roles:

| Item | Framework role | Registry role | Alignment |
|---|---|---|---|
| Step 17a | historical `PASS_FOR_SENSITIVITY` validation evidence | same | PASS |
| Original Step 17b | sensitivity-only historical artifact | same | PASS |
| Corrected Step 17b | promotion-source candidate; not canonical | same | PASS |
| Step 17c | paired sensitivity/adjudication evidence | same | PASS |
| Prior EOB / Layer A outputs | historical / candidate / predecessor evidence | same | PASS |

No historical artifact is silently promoted to accepted final v7.3 production evidence.

## 11. Corrected Step 17b / future canonical identity

Both authorities agree:

- corrected Sep-18 artifact is not canonical;
- future canonical reconstructed-mainline artifact is not yet created / authorized at this stage;
- a truthful new canonical artifact must be built rather than merely renaming the sensitivity-branch artifact.

**Result: PASS**

## 12. A1–A4 alignment

No contradiction identified.

- A1: `eta_c = eta_d = 0.90`
- A2: constant worst-case reserve floor in annual operation + separate outage replay
- A3: one annual regular CC for NTUST mainline; supplementary CC fixed at case values
- A4: exact modeled maxima recomputed ex post; solver epigraph variables are not exact diagnostics

**Result: PASS**

## 13. B1–B2 alignment

No contradiction identified.

- B1: PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation
- rainflow: ex-post validation / benchmark, not embedded as annual sizing objective
- B2: annualized CAPEX + annual FOM + operating costs including cycling wear; no automatic second full replacement stream

**Result: PASS**

## 14. Gate 1 / Gate 2 alignment

Both authorities agree:

- 10 MW-scale PNNL full package = ex-ante mainline;
- 1 MW-scale full package = cost-scale sensitivity;
- package switching cannot depend on optimized `P_B`;
- optimization monetary basis = constant NTD-2023;
- 5% = real modeling discount rate, not claimed as NTUST WACC.

**Result: PASS**

## 15. Tariff / billing / institutional-claim alignment

Aligned boundaries include:

- raw case-year tariff / bill evidence preserved in nominal NTD;
- optimization-facing monetary layer normalized separately;
- `SCHOOL/FROZEN` is a project institutional label, not a universal official category name;
- non-summer peak = N/A, not a zero-rate peak period;
- May/October 50/50 treatment remains case-validated empirical, not universal-official;
- subsidy is not double-counted through a second cash-flow term if already embedded in the effective tariff.

**Result: PASS**

## 16. Non-circular outage-start boundary

Framework and Registry agree that valid outage windows must be fully contained in the case year and must not wrap artificially from year-end to year-start without genuine continuation data.

**Result: PASS**

## 17. Layer B / reliability claim boundary

Aligned:

- Layer B is fixed-design capability testing under structured off-design scenarios;
- structured-scenario coverage is not outage-success probability;
- deterministic capability results are not probabilistic reliability claims;
- DG comparison remains a deterministic counterfactual extension rather than an outage-probability model.

**Result: PASS**

## 18. Current implementation / production status

The pair is consistent that methodology/evidence acceptance does not imply production completion.

At the stage audited here:

- canonical reconstructed-mainline input: not yet created / authorized;
- production routing: not yet authorized;
- Step 17c EOB: promotion/adjudication candidate evidence only;
- representative cases: not closed under v7.3;
- Steps 11A / 11B / 11C: not closed under v7.3;
- final 81-point production: not authorized.

**Result: PASS**

## 19. Lifecycle-snapshot asymmetry

The immutable Framework and Registry were created at different lifecycle times:

- Framework v7.3 contains creation-time statements that Registry v7.3 had not yet been accepted.
- Registry R3 contains creation-time statements that Framework v7.3 was already accepted while R3 itself was still candidate-only.
- Subsequent external acceptance advanced the lifecycle beyond both internal snapshots.

This is not a methodology/evidence contradiction. The accepted files should remain byte-identical; the current external lifecycle belongs in a later freeze / authority checkpoint.

## 20. High-risk alignment matrix

| High-risk item | Result |
|---|---|
| reconstructed PV mainline | PASS |
| zero-winter sensitivity | PASS |
| observed vs reconstructed boundary | PASS |
| short-gap vs long-block validation | PASS |
| epistemic claim boundary | PASS |
| same-artifact / no-hybrid | PASS |
| `R` / `P_out` / binding / replay semantics | PASS |
| Layer A no-surplus recharge | PASS |
| baseline Layer B identity | PASS |
| billing / `kappa` observed-data boundary | PASS |
| 17a / 17b / 17c roles | PASS |
| corrected 17b ≠ canonical | PASS |
| A1–A4 | PASS |
| B1–B2 | PASS |
| Gate 1 / Gate 2 | PASS |
| tariff / monetary / subsidy boundaries | PASS |
| non-circular outage starts | PASS |
| Layer B reliability claim boundary | PASS |
| final81 authorization boundary | PASS |
| acceptance-critical cross-document contradictions | **0 identified** |

## 21. Verdict

**FRAMEWORK V7.3 ↔ REGISTRY V7.3 R3 CROSS-ALIGNMENT AUDIT — PASS / CLOSED**

No acceptance-critical methodology/evidence contradiction, evidence-role inversion, or status-boundary defect was identified.

No Framework successor or Registry R4 is required on the basis of this audit.

## 22. Next governance gate

The next gate is a **v7.3 Methodology / Evidence Freeze** that records the externally accepted current authorities without modifying either accepted primary file.

Expected freeze identities:

- Methodology authority: `research_framework_v7_3_2026-09-23.md`
  - SHA-256: `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a`
- Evidence authority: `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`
  - SHA-256: `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`

Only after the freeze and required repository/provenance verification should the project proceed to construction and audit of the new canonical reconstructed-mainline input.
