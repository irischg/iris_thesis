# v7.2 Framework–Registry Alignment Audit — 2026-08-24

## Artifacts audited

| Artifact | Role | SHA-256 |
|---|---|---|
| `research_framework_v7_2_2026-08-24.md` | Current framework source of truth | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |
| `thesis_literature_evidence_registry_v7_2_2026-08-24.md` | Current literature/evidence source of truth | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |

## Alignment result

**PASS — no current methodological conflict detected between Framework v7.2 and Registry v7.2.**

The following high-risk items were checked in both artifacts and are aligned:

- Gate 1: PNNL 10 MW-scale full package = ex-ante mainline; 1 MW-scale full package = cost-scale sensitivity.
- Cost-scale role is not selected from preliminary or final optimized BESS power.
- Full-package consistency covers `C_E`, `C_P`, `FOM`, `C_rep`, and bracket-specific `lambda_k`.
- PNNL fitting window = 4/6/8/10 h; `C_rep` basis = DC Storage Block arithmetic mean across those durations.
- PNNL monetary normalization = 2023 USD to constant NTD-2023 using FX = 31.150 NTD/USD.
- Gate 2: optimization monetary basis = constant NTD-2023; 5% discount rate = real modeling rate; 20-year horizon and derived CRF remain unchanged.
- Raw case-year Taipower tariff/bill values remain nominal for institutional validation; optimization uses a separately derived constant-NTD-2023 tariff layer.
- Billing-demand calibration is scripted-reproduced / closed; kappa remains NTUST-specific and is not a universal coefficient.
- Script 11f/11g/11h lineage = dual-bracket economic packages; Script 12a lineage = Xu intertemporal semantics audit.
- 13b tariff-registry gate = PASS; 13c pure-season bill-component regression = PASS.
- `SCHOOL/FROZEN` is a project institutional-treatment label, not a universal official Taipower category name.
- Non-summer peak = N/A, not a zero-rate peak period.
- May/October 50/50 basic-charge transition remains an NTUST case-validated empirical rule unless an explicit official general rule is later found.
- No separate subsidy cash-flow term is added when policy support is already reflected in the effective tariff/bill.
- EOB and the 81-point Layer A production run remain not yet executed.
- Post-solve exact demand maxima, ex-post rainflow validation, winter-PV long-block sensitivity, and downstream DG parameterization remain implementation/validation items rather than reopened methodological blockers.
- Script 14a remains the next production-interface preflight and must validate package routing, monetary metadata, raw-vs-normalized tariff layers, CRF, kappa, and legacy-contamination guards before EOB.

## New/updated evidence roles in Registry v7.2

- R34 — Rahman et al. (2021), Applied Energy: scale-dependent BESS economics / economies-of-scale rationale.
- R35 — Vatankhah Ghadim et al. (2025), Applied Energy: cross-study cost normalization to a common base-year monetary value.
- R36 — Giovanniello & Wu (2023), Applied Energy: storage optimization using component costs adjusted to a common cost year.
- T5 — NIST Handbook 135: constant-dollar / real-discount-rate and current-dollar / nominal-discount-rate consistency.
- P6 — exact project resolution and implementation status for Scripts 06–13c, Gate 1, Gate 2, tariff/accounting semantics, and remaining production gates.

## Boundary check

The Registry does **not** attribute the exact thesis choices below to external literature:

- 10 MW as the NTUST mainline cost package;
- 1 MW as the sensitivity package;
- FX = 31.150 NTD/USD;
- the future Taiwan price-index/deflator used for tariff normalization;
- 5% as NTUST WACC;
- `SCHOOL/FROZEN` as an official universal Taipower category;
- May/October 50/50 as a universal official Taipower rule.

Those remain thesis/project-specific choices or audit findings and are controlled by Framework v7.2 / P6 / machine-readable production artifacts.

## Remaining pre-EOB implementation gate

Gate 1 and Gate 2 are methodologically closed. The remaining economic integration task is implementation, not methodology: create and audit the optimization-facing Taipower tariff layer in constant NTD-2023 and verify it through Script 14a before EOB.
