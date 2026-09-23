# IRIS THESIS — UNIVERSAL RESEARCH / CODEX AUTHORITY HEADER

## 1. AUTHORITATIVE SOURCES

Current methodology source of truth:
- `docs/research_framework_v7_3_2026-09-23.md` — Research Framework v7.3 (`CLOSED / ACCEPTED`)

Current literature / evidence source of truth:
- `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` — Thesis Literature Evidence Registry v7.3 R3 (`CLOSED / ACCEPTED`)

Current methodology/evidence lifecycle authority checkpoint:
- `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` — v7.3 authority freeze (`CLOSED / ACCEPTED`)

Current implementation source of truth:
- Current local working tree
- Latest completed checkpoint / implementation audit
- Latest accepted script outputs and machine-readable production artifacts

Repository code and generated production artifacts control exact implemented values where the Framework / Registry explicitly delegate numerical authority to those artifacts.

Earlier Frameworks, Registries, scripts, thesis predecessors, legacy constants, archived outputs, or old chat discussions are NOT current authority unless the accepted Framework v7.3 / Registry v7.3 R3 explicitly classifies them as:
- provenance,
- historical lineage,
- regression,
- replication,
- benchmark,
- sensitivity,
- or legacy comparison material.

Do not silently recover a missing current value from an older version.

---

## 2. CLOSED-DECISION RULE

Do NOT reopen a decision classified as CLOSED, LOCKED, PASS, or methodologically resolved unless there is affirmative evidence of at least one of the following:

1. code implementation error;
2. data error;
3. source-transcription or interpretation error;
4. mathematical inconsistency;
5. violation of the current Framework;
6. direct contradiction between authoritative current artifacts;
7. a newly discovered issue that would materially invalidate the intended methodology.

A different modeling preference, cleaner formulation, alternative literature precedent, or potentially better approach is NOT by itself sufficient to reopen a CLOSED decision.

If a problem is found, first classify it as:

- implementation defect;
- numerical / provenance defect;
- validation gap;
- reporting / interpretation defect;
- or genuine methodological defect.

Do not automatically escalate an implementation issue into a methodology change.

---

## 3. NO LEGACY CONTAMINATION

Never allow superseded assumptions or values to re-enter production merely because they exist in old code or old documents.

In particular:

- legacy parameters must not override current v7.3 parameters or current machine-readable values delegated by the accepted authorities;
- predecessor theses are lineage / comparison evidence, not current numerical authority;
- a PENDING current value must not be filled using an older version unless Framework v7.3 / Registry v7.3 R3 explicitly authorizes this;
- sensitivity packages must not leak into mainline;
- mainline and sensitivity parameters must remain internally consistent packages;
- parameter selection must not depend retrospectively on the optimization result unless the Framework explicitly permits it.

If legacy contamination is detected, report it explicitly.

---

## 4. RESEARCH-INTEGRITY AUDIT MODE

Treat this as a graduate-thesis research implementation, not ordinary software development.

For every material change, check where relevant:

- consistency with the research question;
- consistency with Framework v7.3;
- consistency with Registry v7.3 R3;
- mathematical correctness;
- unit consistency;
- temporal indexing;
- information availability at the decision time;
- look-ahead / perfect-information leakage;
- non-anticipativity where applicable;
- baseline fairness;
- physical BESS feasibility;
- SOC continuity and efficiency semantics;
- tariff / billing semantics;
- degradation accounting;
- cost accounting and monetary basis;
- parameter provenance;
- output semantics;
- reproducibility;
- regression against already accepted behavior.

A solver returning a feasible or optimal solution is NOT sufficient evidence that the model is academically or physically correct.

---

## 5. CLAIM BOUNDARY

Always distinguish:

1. what external literature explicitly supports;
2. what official / institutional sources establish;
3. what this project empirically validates;
4. what the optimization actually produces;
5. what can reasonably be inferred;
6. what remains hypothesis, sensitivity, or limitation.

Do not strengthen claims beyond the available evidence.

Do not describe:
- structured stress-scenario coverage as real-world reliability probability;
- project-specific coefficients as universal constants;
- modeled planning requirements as final engineering installation recommendations;
- empirical NTUST rules as universal Taipower rules;
- benchmark or sensitivity assumptions as mainline assumptions.

---

## 6. CURRENT-VERSION SEMANTICS

Framework v7.3 and Registry v7.3 R3 supersede earlier methodological/evidence wording where conflicts exist. Framework v7.2 and Registry v7.2 remain historical accepted predecessors; Registry v7.3 R1/R2 remain failed immutable provenance.

Respect all currently CLOSED v7.3 decisions, including the decisions preserved from v7.2, and in particular the established:
- preprocessing lineage;
- efficiency semantics;
- annual reserve / outage replay semantics;
- Taipower tariff and contract-capacity treatment;
- billing-demand calibration methodology;
- exact-vs-cost-facing maximum-demand semantics;
- BESS degradation formulation;
- BESS economic-accounting structure;
- PNNL cost-package methodology;
- mainline versus sensitivity package roles;
- constant monetary-basis rules;
- Layer A / Layer B research boundaries.

For PV input identity, v7.3 additionally fixes reconstructed full-year PV as the best-estimate planning
mainline and prior zero-winter PV as conservative stress/sensitivity. Reconstructed values are
model-based/weather-informed estimates, not observed truth or exact recovery. The future canonical
reconstructed-mainline artifact must be shared by EOB/economic, Layer A adequacy/replay, and baseline
Layer B; that artifact and its production routing are not yet implemented or authorized.

Do not infer an older rule from old scripts when v7.3 has superseded it.

---

## 7. IMPLEMENTATION DISCIPLINE

Before editing:

1. inspect the relevant current files;
2. identify the exact authority controlling the requested behavior;
3. identify dependencies and downstream consumers;
4. determine whether the requested work is:
   - read-only audit,
   - implementation,
   - regression,
   - build/preflight,
   - production solve,
   - sensitivity,
   - or post-solve validation.

Make the smallest defensible change necessary.

Do not broaden scope without evidence that it is required.

Do not refactor unrelated working code merely for style.

Do not modify frozen upstream scripts solely to make a downstream script easier to implement.

Preserve accepted provenance and version lineage.

---

## 8. SOLVE / COMPUTE BOUNDARY

Never run an optimization, long annual MILP, full case matrix, sensitivity sweep, or other expensive production computation merely because code has been edited.

Only run a solve when the current task explicitly authorizes it.

If the task is specified as:
- read-only audit,
- build-only,
- syntax/import check,
- formulation inspection,
- unit test,
- regression test,
- or preflight,

then do NOT call the production optimizer.

A successful build is not permission to solve.

---

## 9. REQUIRED RESPONSE AFTER EACH CODEX TASK

At completion, report clearly:

### A. Verdict
- PASS
- PASS WITH NON-BLOCKING NOTES
- BLOCKED
- FAIL

### B. What was inspected / changed
List the relevant files and the substantive purpose of each modification.

### C. Authority check
State which current Framework / Registry / checkpoint rule controlled the work.

### D. Methodology impact
Explicitly state:
- methodology changed: YES / NO
- CLOSED decision reopened: YES / NO

If YES, provide the exact evidence justifying it.

### E. Validation performed
For example:
- syntax/import;
- unit tests;
- regression;
- build-only model inspection;
- artifact/schema audit;
- solver run, only if explicitly authorized.

### F. Validation NOT performed
State important tests or solves intentionally not run.

### G. Remaining risk
Identify genuine unresolved issues only.
Do not manufacture extra work merely to appear thorough.

### H. Recommended next action
State the smallest academically defensible next step.

---

## 10. STOP CONDITIONS

Do not silently improvise if you discover:

- conflict between Framework v7.3 and Registry v7.3 R3;
- conflict between current documentation and production code;
- missing authoritative numerical provenance;
- unexpected legacy contamination;
- data/schema mismatch affecting scientific results;
- material look-ahead or information leakage;
- unit/accounting error;
- a change that would alter an already CLOSED methodology;
- an instruction that would invalidate accepted provenance.

Instead, isolate the issue, show evidence, classify its severity, and avoid unrelated changes.

The objective is not to make the code pass at all costs.

The objective is to preserve an academically defensible, reproducible implementation of the current thesis methodology.
