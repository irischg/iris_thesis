# ACC-N1 exposure-log prerequisite withdrawal — Candidate R1

**Lifecycle: `CANDIDATE / NOT ACCEPTED / NOT IN EFFECT`.** Nothing here is accepted, canonical or in force.
The accepted canonical pointer R1 remains the routing authority and still blocks the three scientific
purposes until a separately authorized, independently audited activation replaces it.

| Item | Value |
|---|---|
| Package | `ACC_N1_EXPOSURE_LOG_PREREQUISITE_WITHDRAWAL_CANDIDATE_R1` |
| Amendment id | `ACC_N1_EXPOSURE_LOG_PREREQUISITE_WITHDRAWAL_R1` |
| Date | 2026-10-14 |
| Base | `HEAD` = `origin/thesis-v7` = `354e0492aef8295a52cc35b8c58a14d81be3e3d4` |
| Operator | Claude Code session `49e9c62c-6026-4b8d-be77-99bce1d7f52b`, model id `claude-opus-5-5` as reported by the runtime. The operator does not self-accept. |
| Authorization basis | The thesis owner's explicit decision, given as the task instruction of this session. That instruction is not published, and no signature is claimed. |
| Git actions | None. Nothing was staged, committed, pushed or tagged. |

## 1. Decision and classification

The thesis owner decided to withdraw the ACC-N1 exposure-log prerequisite. Scientific inspection, results
analysis and supervisor discussion of the accepted Main Layer A Full81 result set (run
`20261008T183934456307Z_a6826f4828`) no longer need an exposure log. The owner asked for the withdrawal
of a current-use restriction that is not needed, not for a remediation of ACC-N1.

- **Governance rule revision.** This is the change itself. It is not a methodology change: no formula,
  parameter, input, tariff/cost basis, degradation semantics, solver setting, Layer A/B boundary, result
  or result identity changes.
- **Implementation change.** The pointer verifier is extended so that a pointer can carry the revision.
  Without the extension, the pointer would fail closed. The extension corrects no defect, and a pointer
  without an amendment behaves exactly as before (§7).

## 2. Rule delta

### 2.1 Old rule — preserved byte-for-byte

- Task-3 sequencing acceptance closure §13 (mandatory exposure log), together with §11 and §12. File
  `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md`,
  SHA-256 `9f1af8e805b23f6e16c827ada645bfff7d920d98a24b70fb2ea448683ec78851`.
- ACC-N1 in the Full81 results acceptance closure: MAJOR / OPEN, with
  `blocking_for_first_scientific_inspection_of_full81_results = true` and
  `blocking_for_supervisor_discussion_of_full81_results = true`. File
  `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_closure.json`,
  SHA-256 `3b27f9a60f5e0bfbcffde343aad164e74cff2f8a98581d91fb95d4bc90e2ba02`.
- The first binding carry-forward condition of that closure (the ACC-N1 exposure-log condition).
- Canonical pointer R1, which blocks `SCIENTIFIC_INSPECTION`, `RESULTS_ANALYSIS` and
  `SUPERVISOR_DISCUSSION`.

None of these files is modified. They remain the accepted historical record.

### 2.2 New rule (in effect only after acceptance and activation, §9)

> For the accepted Main Layer A Full81 result set, a dedicated exposure log and per-event exposure records
> are no longer a prerequisite for scientific inspection, results analysis or supervisor discussion. No
> exposure event has to be created for these purposes.

To keep §11 and §12 meaningful without a log, the Main Full81 results are **treated as exposed** for both
sections. The strictest claim boundary therefore applies, and no evidence of exposure timing is needed.

### 2.3 Bounded supersession

The amendment supersedes §13 only as a prerequisite for the three purposes, and only on the bound result
set. Sections 8, 11 and 12 and the rest of the closure remain in force. The amendment does not extend to
A2, the conditional beta=8 extension, Layer B, DG extensions, sensitivity analyses, any other or future
result set, or any solve.

## 3. What stays in force

| Item | State after the amendment |
|---|---|
| ACC-N1 | Stays **MAJOR / OPEN** exactly as recorded. It is not closed, remediated or regraded; only its blocking effect is withdrawn. |
| Exposure log | None exists. None is created, claimed or reconstructed. A retrospective or fabricated record remains a governance failure. |
| Prior exposure | Acknowledged (ACC-N1 `result_information_already_visible`). Full blinding is not claimed. |
| §11 reduced-blinding boundary | In force. U-01 may not be described as fully pre-Full81 blinded. |
| §12 Full81-to-U-01 calibration | **Prohibited**, unchanged. |
| §8 zero-A2-result-exposure firewall | In force in full. |
| U-01 | `OPEN_HOLD`. It must still be frozen before `A2_EXECUTION`, `A2_RESULT_EXPOSURE`, `A2_INTERPRETATION` and `A2_CONDITIONAL_EXTENSION_AUTHORIZATION`. |
| A2 | `HARD_BLOCKED_UNTIL_U_01_RESOLVED_AUDITED_ACCEPTED_AND_FROZEN` |
| Other carry-forward conditions | In force, including the ban on a materiality-classification column in any aggregation layer. |
| Other non-authorizations | Unchanged. These include `CROSS_CASE_AGGREGATION_OR_REPORTING_LAYER`, `PIPELINE_MANAGEMENT_NOTEBOOK`, `EXPOSURE_LOG_CREATION`, `ANY_SOLVER_CALL_MODEL_CONSTRUCTION_OR_PRODUCTION_RUN` and `U_01_RESOLUTION_OR_CALIBRATION`. |
| Framework v7.4, Registry v7.4, EOB, MILP model, parameters | Unchanged. |
| 81 accepted Main Full81 G1 results | Unchanged. The strict 651-file rehash reproduces the accepted run-file aggregate. |

## 4. Package

| Path | Status | SHA-256 | Bytes |
|---|---|---|---|
| `results/provenance/acc_n1_exposure_log_prerequisite_withdrawal_candidate_r1/governance_amendment_record.json` | new | `bd97a6d06985712c35b1b3dfcd755cff2889dfc71c8f1be0a15fa13688282b85` | 10575 |
| `configs/candidates/current_mainline_pointer_candidate_r2.json` | new | `7f4971f630a8ceed429f7a3638d68015ec21758b05817a6500b1d9e808aebb60` | 56791 |
| `src/current_mainline_pointer_v1.py` | modified | `03485b36188d83163cdf9fd49cc14770aec8ca37769a402cbca4643df18ad930` | 132591 |
| `tests/test_current_mainline_pointer_acc_n1_amendment.py` | new | `a1a998662c1c75cbef7fae8b47f6e5f90c4135053d36f734d6758fe183a976bf` | 36718 |
| this checkpoint | new | omitted (no self-hash) | — |

Notes on the package:

- **Verifier predecessor.** The R1-accepted verifier bytes are SHA-256
  `fc73068a6a469842a7c234d4c07dac1baba1d669fc9c5a1adf2449b571d483e0`. They stay durable in Git as blob
  `29e3b0ad2b7fd247450fff1fef7d8c449fe45e00`, published at `baf5eab`.
- **Pointer R2 payload digest:** `08d09477d7bcda349197427f38bd642cf8f7d3e0413abdfdc4c362dab141ee4e`. The
  R1 payload digest is `1c118f22350aa21d74b04f94307be8bbb43d694023e5350b1edf512824980fdf`.
- **Encoding.** All files are UTF-8 with LF line endings; the JSON files use `json.dumps(indent=2,
  ensure_ascii=False)` plus a trailing newline.
- **Not modified:** `tests/test_current_mainline_pointer_v1.py`, every accepted record, checkpoint,
  manifest and run artifact, and every handoff document.

## 5. How the rule is enforced (verifier extension)

A pointer may bind amendments under `scientific_exposure_restrictions.governance_amendments`, by path,
SHA-256 and size. The verifier enforces the following:

- **Identity.** The record is re-hashed on every run, whatever the results policy.
- **Scope of the lift.** An amendment may withdraw only blocking flags that the accepted results
  acceptance sets for the **governing** open finding. The lifted purposes must be exactly the purposes of
  those flags.
- **Non-authorizations.** Only `DOWNSTREAM_LAYER_A_RESULTS_ANALYSIS_OR_SCIENTIFIC_INSPECTION` and
  `SUPERVISOR_DISCUSSION_OF_FULL81_RESULTS_WITHOUT_AN_EXPOSURE_EVENT` can be lifted, and only if the
  accepted record lists them.
- **Carry-forward conditions.** The amendment supersedes exactly the conditions prefixed by the target
  finding id, and no other condition. The U-01/A2 condition cannot be superseded.
- **Matching sources.** The record must name the accepted results-acceptance closure and the governing
  clause by path and SHA-256, and the bound run path and case set.
- **Preserved restrictions.** The record must keep the finding open and unremediated, claim no exposure
  log, and be neither self-accepted nor an exposure event. Its U-01 status, U-01 freeze list and A2 status
  must equal the pointer's, which are cross-bound to the accepted scope authorization. It must record the
  calibration prohibition, the "not pre-Full81 blinded" status and the "treated as exposed" status.
- **Fail closed.** An invalid, duplicated or altered amendment fails closed and **lifts nothing**.
- **Applied.** A valid amendment must actually be applied: the lifted purposes leave the finding and move
  to `permitted_purposes`.
- **Canonical mode.** The activation acceptance closure must list the amendment under
  `accepted_governance_amendments` by id, path and SHA-256. The record must be in the live `HEAD` with the
  bound bytes and published upstream.

No check id, consumption purpose or interface version is added. A pointer without the key verifies
exactly as before.

## 6. Pointer candidate R2

R2 is the R1 payload with these revisions only:

- `pointer_revision` is `R2`.
- `blocked_purposes` is `[]`.
- `permitted_purposes` adds the three purposes.
- The amendment binding is added.
- ACC-N1 `blocks_purposes` is `[]`.
- The two lifted items are removed from `not_authorized_by_this_pointer`.
- Descriptive `*_note` and `documentation` text is updated.

Every identity binding is carried unchanged, and a live test enforces this section by section. The
carry-forward conditions remain verbatim because they are cross-bound to the accepted closure. The
amendment records which one is superseded.

## 7. Validation (all zero-solve)

| Check | Result |
|---|---|
| Canonical R1 output before vs after the verifier change (`NOT_CHECKED` and `STRICT_FULL_REHASH`) | **Byte-identical** |
| Canonical R1 | `CANONICAL_POINTER_VERIFIED`, strict 651-file integrity PASS, three purposes still blocked |
| Pointer candidate R2 (`NOT_CHECKED`, `STRICT_FULL_REHASH`) | `CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY`, `STRICT_FULL_INTEGRITY_PASS`, amendment valid |
| `tests/test_current_mainline_pointer_acc_n1_amendment.py` | **16 / 16 OK** (250.8 s) |
| `tests/test_current_mainline_pointer_v1.py`, run as the two commands the R1 acceptance used | **59 / 59 OK** (39 in 293.8 s, 20 in 468.8 s); 0 skipped |
| Solver imports / model constructions / `optimize()` calls | 0 / 0 / 0 |
| Full81 result values read or displayed | 0. Result files are hashed as opaque bytes only. |
| Result files modified | 0. The strict rehash reproduces the accepted run-file aggregate. |

The new suite covers the following:

- **Live repository.** R1 is unchanged and still blocks. R2 is consistent. The R2 payload differs from R1
  only in the ACC-N1 routing. The strict rehash passes. The record preserves U-01, A2, §11 and §12.
- **Negative controls.** 26 negative controls run on the live R2. A sweep mutates each of the 183
  non-descriptive leaves of the three revised sections; no mutation goes unnoticed.
- **Isolation.** A subprocess check confirms that no solver or production module is loaded.
- **Hermetic content attacks.** 22 content attacks use correct hash bindings, and every one lifts nothing.
- **Hermetic activation.** A full candidate, audit, acceptance and canonical activation serves the three
  purposes and still refuses `A2`, `FULL81_EXECUTION`, `LAYER_B` and other purposes. Canonical mode refuses
  an unaccepted, unpublished, unpushed or later-rewritten amendment.

## 8. Observations for the independent auditor

- **CAND-OBS-1 (decision point).** The verifier is extended **in place** rather than as an additive v2
  module. Reasons:
  - The pointer binds `verifier_module` and `verifier_interface_version`.
  - A v2 module would duplicate about 3,000 lines, which bears on PTR-REVIEW-2.
  - The R1 bytes remain durable in Git.
  - The canonical R1 output is byte-identical before and after.

  The auditor should decide whether this is acceptable under the additive-only rule (Protocol §5).
- **CAND-OBS-2.** The same session authored every file. Owner identity was not verified, and no signature
  is claimed.
- **CAND-OBS-3.** The new files have no `.gitattributes` rule. A checkout under `core.autocrlf=true` will
  fail closed, as PTR-ACC-OBS-3 already records. `.gitattributes` is not modified.
- **CAND-OBS-4.** The live tests encode the premise that R1 is canonical and R2 is a candidate. Retire
  `test_canonical_r1_is_unchanged_and_still_blocks` and the candidate-lifecycle assertions when R2 is
  activated; do not edit them until they pass.
- **CAND-OBS-5.** These documents still describe ACC-N1 as blocking:
  - `docs/ai_handoff/CURRENT_STATE.md`
  - the R1 pointer acceptance closure (`acc_n1`)
  - the results acceptance closure

  They are not edited: the closures are immutable, and handoff synchronization is not authorized.
- **CAND-OBS-6.** `git status` showed
  `results/provenance/main_full81_authorization_r2/main_full81_authorization.json` as modified before
  this pass. Its content diff is empty (a stat-only change), and this pass did not touch it.
- **CAND-OBS-7.** The amendment record is under the gitignored `results/` tree. Publishing it needs
  `git add -f`, like the other provenance records.

## 9. Lifecycle and next gates

1. **An independent read-only audit by a fresh, separate operator.** This is the next required gate.
   Suggested focus:
   - CAND-OBS-1;
   - whether a lift could reach A2 or U-01;
   - the R1 → R2 payload diff;
   - re-running both suites and the strict canonical check.
2. Publication of this package and the audit record (commit A).
3. An acceptance closure that lists the amendment under `accepted_governance_amendments` by id, path
   and SHA-256, plus its manifest (commit B).
4. Canonical activation: `configs/current_mainline_pointer.json` becomes the R2 payload with an accepted
   envelope (commit C), and the commit is pushed.

Until step 4 is complete, `require_current_mainline` refuses the three purposes. Handoff synchronization
is a separate step after activation.

## 10. Non-claims

- This package is not accepted, not canonical and not in effect.
- ACC-N1 is not closed or remediated. No exposure log exists, and none is created or reconstructed.
- The package makes no blinding claim.
- It does not authorize a solve, a rerun, A2, U-01 resolution or calibration, an aggregation/reporting
  layer, a pipeline notebook, or any change to an accepted artifact.

`ACC-N1 EXPOSURE-LOG PREREQUISITE WITHDRAWAL — CANDIDATE PASS`
