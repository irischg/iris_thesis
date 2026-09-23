# Framework v7.3 Merge / Successor-Lineage Audit

**Project:** Iris Thesis  
**Audit date:** 2026-09-23  
**Audit mode:** Read-only primary-document merge / successor-lineage audit  
**Verdict:** **PASS / CLOSED**

## 1. Scope

This audit checks whether `research_framework_v7_3_2026-09-23.md` is a defensible additive successor to `research_framework_v7_2_2026-08-24.md`, with no unrelated methodology drift.

This audit does **not** establish repository branch/HEAD/staging state and does **not** authorize production solves, canonical-artifact construction, or routing changes. Those are separate provenance / implementation gates.


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

| Artifact | SHA-256 | Lines |
|---|---|---:|
| `research_framework_v7_2_2026-08-24.md` | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` | 3,832 |
| `research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` | 3,956 |

The hashes were recomputed from the primary bytes available in the project environment during audit packaging.

## 3. Full-file diff

`v7.2 -> v7.3` mechanical diff:

- insertions: **206**
- deletions: **82**
- unified-diff hunks (`-U3`): **36**
- net line change: **+124**

The change pattern is additive and localized. The substantive methodology delta is the reconstructed-PV role reversal and its required consistency / provenance consequences.

## 4. Authorized methodology delta

Framework v7.3 changes the prolonged unavailable winter-PV planning role as follows:

- reconstructed full-year PV, including the 1,463-hour prolonged unavailable block, becomes the **best-estimate planning mainline**;
- the prior zero-winter treatment becomes a **conservative stress / sensitivity**;
- reconstructed values remain **model-based, weather-informed estimates**, not observed meter data, exact ground truth, or exact historical recovery.

This is the only substantive methodology-role change relative to v7.2.

## 5. Same-artifact / no-hybrid consistency

Framework v7.3 requires the same reconstructed full-year planning-baseline PV identity to feed:

- EOB / annual economic optimization;
- Layer A residual-load construction;
- `R(alpha,beta)`;
- `P_out(alpha)`;
- binding-window classification;
- exhaustive outage replay;
- baseline Layer B.

A hybrid implementation in which economics receives reconstructed-PV credit but Layer A or baseline Layer B reverts to zero-winter PV is explicitly unauthorized.

The audit finds this requirement internally consistent across the successor document.

## 6. Formula and stage-semantics preservation

The PV promotion is an **input-role change**, not an equation redesign.

Preserved:

- Layer A analytical-consistency replay continues to prohibit outage-period PV-surplus recharge;
- Layer B event replay may retain its distinct allowed-surplus-recharge semantics;
- the Layer A / Layer B stage distinction is not treated as an exception to common PV artifact identity.

No unrelated formula change was identified.

## 7. Observed-data / billing-calibration boundary

Framework v7.3 preserves the separation between:

- observed Load/PV used for historical billing calibration; and
- planning-baseline / available series used for annual planning.

`kappa` is not to be re-estimated from reconstructed winter PV solely because the planning baseline changes.

This boundary is preserved and is consistent with the accepted billing-calibration lineage.

## 8. Preserved CLOSED methodology

The v7.3 successor preserves the previously closed methodology, including:

- A1–A4;
- B1–B2;
- Gate 1 and Gate 2;
- stationary LFP;
- mainline SOC 10–90%;
- `eta_c = eta_d = 0.90`;
- annual regular contract-capacity semantics;
- Taipower tariff treatment and constant-NTD-2023 accounting;
- 10 MW-scale PNNL package mainline / 1 MW-scale package sensitivity;
- intertemporal DOD-sensitive PWL degradation;
- alpha–beta design grid;
- non-circular valid-start semantics;
- analytical reserve formula;
- annual-operation / outage-replay stage separation;
- Layer A no-surplus-recharge consistency semantics.

No unrelated methodology reopening was identified.

## 9. Historical-snapshot preservation

Framework v7.3 does not silently rewrite v7.2 history. Where older zero-winter or historical implementation state is retained, it is temporally scoped as predecessor / historical state and separated from current v7.3 methodology.

Creation-time status statements inside the immutable v7.3 artifact (for example candidate-state entries) are treated as provenance snapshots, not as the current external lifecycle state after independent acceptance.

## 10. Promotion-source / future-canonical boundary

The corrected Sep-18 reconstructed-PV artifact remains a **promotion-source candidate**, not the production canonical input.

The future canonical reconstructed-mainline artifact remains, at this audit stage:

- `NOT_YET_CREATED`
- `NOT_YET_AUTHORIZED`

The framework correctly requires a newly built canonical artifact with truthful provenance rather than merely renaming the old v7.2 sensitivity artifact.

## 11. Change classification

All reviewed v7.2 -> v7.3 diff blocks fall within one of the following authorized categories:

- reconstructed-PV role reversal;
- downstream same-artifact consistency;
- observed/planning boundary clarification;
- historical temporal scoping;
- promotion-source / future-canonical provenance;
- current governance / implementation-state recording;
- additive v7.3 successor freeze material.

**Unrelated methodology change: 0 identified.**

## 12. Verdict

**FRAMEWORK V7.3 MERGE / SUCCESSOR-LINEAGE AUDIT — PASS / CLOSED**

- predecessor identity: PASS
- merge completeness: PASS
- authorized methodology delta: PASS
- CLOSED-method preservation: PASS
- historical scoping: PASS
- same-artifact / no-hybrid consistency: PASS
- observed/billing boundary: PASS
- promotion-source / canonical boundary: PASS
- unrelated methodology drift: **0 identified**
- reopen Framework v7.3 acceptance: **NO**

## 13. Downstream boundary

This merge audit does not itself authorize:

- canonical reconstructed-mainline artifact construction;
- production routing;
- representative-case reruns;
- Steps 11A / 11B / 11C;
- final 81-point production.

Those remain downstream gates.
