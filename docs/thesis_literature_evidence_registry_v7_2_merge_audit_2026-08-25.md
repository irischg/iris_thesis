# Registry v7.2 Merge / Evidence-Role Audit — 2026-08-25

## 1. Audit purpose

This audit records the controlled evidence-registry transition from v7.1 to v7.2. It documents evidence-ID preservation, new evidence, changed evidence roles, implementation-status updates, and alignment to Research Framework v7.2.

The registry remains an evidence / claim-mapping artifact. It does not independently create thesis methodology; exact thesis decisions remain controlled by the framework and project evidence.

## 2. Provenance

### Base registry

- File: `thesis_literature_evidence_registry_v7_1_2026-08-16.md`
- Role: previous evidence-registry source of truth
- SHA-256: `9d90218a520b429fe07c081f26c282e68b5fa68d7537f97a13201719d3816c31`

### Alignment framework

- File: `research_framework_v7_2_2026-08-24.md`
- Role: current methodology / implementation alignment target
- SHA-256: `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5`

### Integrated registry

- File: `thesis_literature_evidence_registry_v7_2_2026-08-24.md`
- Role: current evidence-registry source of truth
- SHA-256: `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e`

### Companion alignment audit

- File: `v7_2_framework_registry_alignment_audit_2026-08-24.md`
- SHA-256: `0035514813799df8baa46bf912a73c76f946ccdadd87ce88014c92fd79a7517d`

## 3. Structural preservation

Evidence IDs in Registry v7.1: **48**  
Evidence IDs in Registry v7.2: **53**

Removed evidence IDs: **None**

Added evidence IDs:

- `R34` — Rahman et al. (2021): BESS scale-dependent techno-economic modeling
- `R35` — Vatankhah Ghadim et al. (2025): common-base-year cost normalization
- `R36` — Giovanniello & Wu (2023): storage optimization with common cost-year basis
- `T5` — NIST Handbook 135 / FEMP LCC guidance: constant-dollar / real-rate consistency
- `P6` — post-v7.1 economic / tariff integration project evidence

All pre-existing evidence IDs `R1–R33`, `T1–T4`, `I1–I5`, `P1–P5`, and `L1` are retained.

## 4. Scope of registry changes

The registry diff preserves the original thematic literature sections §1–§7. Changes are concentrated in:

- preamble / audit-status rules
- §8–§9 where existing evidence wording and the new R34–R36 entries are integrated
- §10 authoritative sources, including new T5
- §11 institutional / project evidence, including new P6 and post-v7.1 status updates
- §12 claim-to-source map
- §13 priority-reading order
- §14 safe / unsafe claim language
- §15 evidence-status summary
- §16 working bibliography and maintenance guardrails

No older literature stream is deleted to make room for the economic-integration evidence.

## 5. New evidence roles in v7.2

### 5.1 R34 — Rahman et al. (2021)

**Role:** supports the general proposition that utility-scale electrochemical storage costs are scale-dependent and that economies of scale matter in techno-economic modeling.

**Permitted use:**

- justify retaining scale distinctions in BESS cost assumptions;
- support the methodological legitimacy of a cost-scale sensitivity.

**Explicit boundary:**

- R34 does **not** select NTUST's exact 10 MW mainline package;
- it does not imply `CC = 5 MW` means BESS power is 5 or 10 MW;
- it does not validate an invented continuous 1–10 MW interpolation curve.

Exact Gate 1 role selection is controlled by P6 + Framework v7.2.

### 5.2 R35 — Vatankhah Ghadim et al. (2025)

**Role:** recent academic precedent for converting heterogeneous technology-cost information to a common price / base year before comparison.

**Permitted use:** supports the Gate 2 common-base-year normalization principle.

**Explicit boundary:** does not supply NTUST's FX = 31.150, tariff deflator, or 5% real-rate choice.

### 5.3 R36 — Giovanniello & Wu (2023)

**Role:** storage-sizing optimization precedent in which component costs are harmonized to a common cost-year basis before optimization.

**Permitted use:** connects common-base-year treatment directly to storage optimization rather than only to cross-study cost comparison.

**Explicit boundary:** does not dictate the thesis's exact base year, currency, or tariff normalization series.

### 5.4 T5 — NIST Handbook 135 / FEMP LCC guidance

**Role:** fundamental authoritative method source for monetary-basis / discount-rate consistency.

Controls the rule that:

- constant-dollar cash flows pair with a **real discount rate**;
- current / nominal-dollar cash flows pair with a **nominal discount rate**.

T5 supports the consistency rule but does not establish that 5% is NTUST WACC.

### 5.5 P6 — post-v7.1 economic / tariff integration project evidence

**Role:** exact thesis/project control record for decisions and completed audits that literature cannot determine.

P6 records:

- Script 06 integration status;
- Scripts 11f / 11g / 11h dual-bracket package construction;
- exact 4/6/8/10 h fitting window;
- bracket-specific `C_E`, `C_P`, FOM, `C_rep`, and `lambda_k` lineage;
- FX = 31.150 NTD/USD and constant NTD-2023 BESS basis;
- Script 12a Xu intertemporal semantics audit;
- 13b tariff production gate = CLOSED / PASS;
- 13c pure-season bill-component regression = CLOSED / PASS;
- Gate 1 exact role freeze: 10 MW mainline / 1 MW sensitivity;
- Gate 2 exact monetary freeze: constant NTD-2023 / real 5%;
- `SCHOOL/FROZEN` project-label semantics;
- non-summer peak = N/A;
- subsidy non-double-counting boundary;
- Script 14a as the next production-interface gate.

## 6. Major evidence-role / status changes for existing entries

### T2 — PNNL v2024

T2 remains the authoritative raw BESS CAPEX/FOM source, but v7.2 makes its role more precise:

- PNNL provides source scale cases / raw cost data;
- thesis-specific 1 MW / 10 MW linearized packages are derived project artifacts;
- T2 does not independently choose the 10 MW package as mainline.

### T3 — PNNL LCOS context

Retained as financial-horizon / context support; it does not override the exact v7.2 package construction or monetary-basis governance.

### P2 — billing-demand calibration

The old pending scripted-reproduction status is closed. `kappa` remains a site-specific project calibration, not a literature coefficient.

### P3 — parameter-registry governance

Expanded in practical importance because v7.2 requires full-package routing and monetary metadata to prevent cross-bracket or nominal/real contamination.

### I3 — tariff source of truth

Retains raw NTUST bills + effective-date Taipower tariff tables as the institutional source layer. v7.2 adds the explicit rule that normalization for optimization must occur in a **separate** layer and must not overwrite raw nominal evidence.

## 7. Gate 1 evidence architecture

Final v7.2 evidence chain:

- **R34** — literature principle: BESS costs are scale-dependent.
- **T2** — authoritative source: PNNL provides the underlying 1 MW / 10 MW scale-case data.
- **P6** — exact thesis governance: 10 MW = ex-ante mainline; 1 MW = full-package sensitivity; optimized `P^B` never chooses the package.

This separation prevents literature from being misused to claim that a journal article or PNNL itself mandates the NTUST 10 MW mainline choice.

## 8. Gate 2 evidence architecture

Final v7.2 evidence chain:

- **R35** — recent common-base-year normalization precedent.
- **R36** — storage-optimization common cost-year precedent.
- **T5** — fundamental constant-dollar / real-rate consistency rule.
- **P6** — exact thesis choice: constant NTD-2023 and 5% real modeling rate.
- **I3** — raw official / bill tariff evidence retained in nominal case-year terms.

The final Gate 2 claim map therefore does not depend on older, redundant examples to establish the method.

## 9. Deliberate evidence-boundary decisions

The registry explicitly distinguishes three levels:

1. **Literature principle** — e.g., scale dependence or common-base-year normalization.
2. **Authoritative technical / institutional source** — e.g., PNNL raw cost data, NIST consistency guidance, Taipower / NTUST bills.
3. **Project-specific exact choice** — e.g., 10 MW mainline, FX = 31.150, constant NTD-2023, 5% real interpretation, `SCHOOL/FROZEN` label, non-summer peak N/A.

A literature source must not be promoted to support an exact project parameter or institutional interpretation that it does not contain.

Discussed but redundant precedents that are not assigned control IDs in v7.2 do not constitute missing evidence. Gate 2 is controlled by the final R35 + R36 + T5 + P6 architecture.

## 10. Claim-map / maintenance synchronization

The following registry areas were updated to match v7.2 roles and status:

- §0.1 conflict-resolution table
- §12 claim-to-source map
- §13 priority-reading order
- §14 safe / unsafe claim wording
- §15 evidence-status summary
- §16 working bibliography
- v7.2 maintenance guardrails

Key guardrails now include:

- never choose 1 MW vs 10 MW from optimized `P^B`;
- never mix bracket-specific `C_E`, `C_P`, FOM, `C_rep`, or `lambda_k`;
- never invent a continuous scale curve without reopening the framework with supported methodology;
- never overwrite raw nominal tariff evidence with normalized values;
- preserve non-summer peak as N/A rather than zero;
- do not universalize the May/October 50/50 empirical rule;
- do not double count subsidy already embedded in effective tariff / bill;
- use constant NTD-2023 with the real-rate interpretation in the optimization layer.

## 11. Current evidence / implementation status after v7.2

Closed / populated:

- preprocessing Scripts 01–05;
- final annual-input integration (Script 06);
- `kappa` scripted reproduction;
- PNNL dual-bracket economic-package construction;
- Xu intertemporal semantics audit;
- 13b tariff production gate;
- 13c pure-season bill-component regression;
- Gate 1 method;
- Gate 2 method.

Still pending as implementation / validation, not evidence-method blockers:

- Script 14a production interface;
- official nominal tariff → constant NTD-2023 machine-readable layer with explicit price-index / deflator provenance;
- post-solve exact maxima diagnostics;
- rainflow ex-post validation;
- winter-PV long-block sensitivity;
- downstream Layer A / Layer B / DG production results.

## 12. Supersession status

Effective with v7.2:

- `thesis_literature_evidence_registry_v7_2_2026-08-24.md` is the current registry source of truth.
- Registry v7.1 remains for provenance / historical comparison.
- Older evidence roles must not be used to override v7.2 claim mapping.
- Exact site/project decisions are controlled by project evidence entries and current framework rules, not backfilled from older registry text.

## 13. Audit conclusion

**PASS — evidence-preserving incremental merge with five added control records and no removed evidence IDs.**

Registry v7.2 preserves the v7.1 evidence base, adds targeted Gate 1 / Gate 2 support, updates post-v7.1 implementation status, and keeps literature principles separate from exact NTUST project decisions. It is aligned to Research Framework v7.2 and the existing Framework–Registry alignment audit.
