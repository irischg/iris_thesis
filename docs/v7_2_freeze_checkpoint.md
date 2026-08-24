# v7.2 Freeze Checkpoint

**Project:** Iris_thesis  
**Purpose:** Cross-conversation milestone guardrail before entering the formal EOB / Layer A stage.

## Trigger condition

When **all three gates below are CLOSED**, STOP before running the formal EOB or Layer A optimization.

### Gate 1 — Taipower tariff integration
Complete and freeze:
- NTUST school/frozen high-voltage three-period TOU tariff source;
- mixed-season May/October basic-charge rule;
- final case-year production tariff registry;
- required bill-regression checks.

### Gate 2 — Monetary-basis harmonization
Complete and freeze:
- treatment of PNNL BESS cost vintage = **2023**;
- treatment of Taipower tariff vintage = **2024-11 to 2025-10 case year**;
- common monetary basis for the final objective;
- consistency of the `r = 5%` / CRF interpretation with the chosen real-vs-nominal monetary basis.

**Guardrail:** Do not directly combine 2023 BESS monetary values with 2024/2025 nominal tariff costs without an explicit harmonization rule.

### Gate 3 — PNNL 1 MW vs 10 MW mainline bracket
Complete and freeze:
- select the mainline cost bracket **ex ante**;
- retain the other PNNL bracket as cost-scale sensitivity;
- formally supersede the v7.1 wording that selected the bracket using preliminary optimized `P^B`, because that rule is circular.

## Mandatory action at trigger

Once Gates 1–3 are all CLOSED:

> **STOP BEFORE EOB. Freeze v7.2 first.**

Create and audit:
1. `research_framework_v7_2_<date>.md`
2. `thesis_literature_evidence_registry_v7_2_<date>.md`
3. `research_framework_v7_2_merge_audit_<date>.md`

The merge audit must classify changes as:
- **ADDED**
- **CLARIFIED**
- **SUPERSEDED**
- **UNCHANGED**

At minimum, v7.2 should incorporate:
- PNNL 2023 Point LFP source scope;
- 4–10 h cost-linearization window;
- `C_E`, `C_P`, `FOM`, and `C_rep` population rules;
- USD-2023 → NTD-2023 normalization;
- code-derived PNNL-calibrated `lambda_k`;
- Xu-adapted intertemporal degradation validation;
- ex-ante 1 MW / 10 MW bracket rule;
- NTUST school/frozen tariff;
- subsidy/accounting role;
- mixed-season tariff treatment;
- final 2023 BESS vs 2024/2025 tariff monetary-basis harmonization rule.

## Current status

- Gate 1: **IN PROGRESS**
- Gate 2: **PENDING**
- Gate 3: **PENDING**
- v7.2 framework freeze: **NOT YET**
- Formal EOB / Layer A: **DO NOT START UNTIL v7.2 FREEZE IS COMPLETED**

## Reminder sentence for future coding conversations

> If tariff integration, monetary-basis harmonization, and the ex-ante PNNL bracket rule are all closed, remind Iris that the project has reached the **v7.2 freeze milestone** and should update framework + registry + merge audit before proceeding to EOB.
