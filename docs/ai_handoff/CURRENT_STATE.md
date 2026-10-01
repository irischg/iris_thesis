# Current State — Living Implementation Status

**This file describes implementation status only. It does not, and must not, reopen or restate
methodology — see `PROJECT_HANDOFF.md` and the Framework itself for that.**
A stage below is marked complete only where a checkpoint/audit artifact supports it — never merely
because a script exists.

Last reconstructed: 2026-09-27, from primary repository evidence at the observed pre-F-03 base
commit `d07d34a163f0e45c8f8764526e81070f19d48747` ("Governance: accept Task 3 robustness
preregistration Candidate R2").
Every authority hash quoted below was re-derived from primary repository bytes at that base.
Re-derive live Git and implementation authority before trusting this file after the repository advances.

Last updated: 2026-09-27, for the **F-03 bounded handoff synchronization** after Task 3 Candidate R2
acceptance and the final cross-document alignment audit. This synchronization is documentation-only:
it changes no methodology, evidence content, data value, result, implementation, or production-routing
authority; it performs no solve, model construction, rerun, threshold decision, U-item resolution, or
production-authority re-freeze. It records Task 3 Candidate R1 as immutable historical STOP provenance,
Candidate R2 as `CLOSED / ACCEPTED`, and the final alignment audit as completed. It does **not** authorize
implementation, robustness execution, or current-route Full81.

Also updated: 2026-10-01, for the **bounded acceptance/closure of the V7.4 Results & Managerial-Insight
Analysis Plan Candidate R2**. That pass is governance/provenance only: it changes no methodology,
evidence content, equation, parameter, data value, result, implementation, or production-routing
authority; it performs no solve, model construction, rerun, threshold decision, U-item resolution,
production-authority re-freeze, or production-gate run. It records that plan's Candidate R1 as immutable
historical candidate provenance and its Candidate R2 as `CLOSED / ACCEPTED`. It does **not** authorize
implementation, an aggregation/reporting layer, robustness execution, A2, or current-route Full81, and it
does **not** reconcile the `U-06` / `U-07` representation discrepancy.

**Self-reference convention — read this before trusting any HEAD/tag fact below.** This file is itself a
tracked, committed file. Committing or amending it (like any other commit) advances the repository's
live HEAD; that does not invalidate the historical reconstruction record below, it only means the record
describes a specific past base point rather than whatever HEAD is live right now. Accordingly:

- Every commit hash below is labeled the **base HEAD observed at last reconstruction**, not a
  permanent declaration of "the current HEAD." This file must never be edited to try to embed its own
  future containing commit hash, and must never be committed/amended in a loop chasing its own HEAD —
  that is not the point of this convention.
- The **live current HEAD** must always be obtained fresh, on demand, via `git rev-parse HEAD` — never
  assumed from this file.
- Similarly, any tag-vs-HEAD relationship described below (§5) is an **observation from that specific
  reconstruction**, not an ongoing or permanent claim about current tag status. Re-check it live
  (`git rev-parse <tag>^{}` vs `git rev-parse HEAD`) before relying on it.
- **Production authorization must always be determined live**, by running the current production
  runner's own authority gate against the live HEAD — never read off this file. The current gate is
  the deployment-gate / `require_production_authority()` path in
  `src/production_successor_stack_v7_3.py`; read that implementation directly before any production
  run. Section 5 records a historical v7.2 mechanism and does not authorize its reuse.

## 1. Source of truth

- **Methodology — current authority**: `docs/research_framework_v7_4_2026-09-26_r2.md`
  (SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273`;
  `CLOSED / ACCEPTED`).
  - **The formal methodology name is `Framework v7.4`, never "Framework v7.4 R2".** The `_r2` suffix is
    repository/provenance identity only (Candidate R2 supplied the accepted bytes).
  - Acceptance checkpoint: `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md`
    (SHA-256 `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f`).
  - Acceptance manifest:
    `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`
    (SHA-256 `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33`).
- **Evidence — current authority**: `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`
  (SHA-256 `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433`;
  `CLOSED / ACCEPTED`).
  - **The formal evidence name is `Registry v7.4`, never "Registry v7.4 R1".** `Candidate R1` is
    repository/provenance revision identity only; the accepted path carries no `_r1` suffix.
  - Independent audit record:
    `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md`
    (SHA-256 `bf909363d726ecd2f55ce883a71e6a894e718587bbeb6946d879758f246c12ce`).
  - Acceptance checkpoint:
    `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md`
    (SHA-256 `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977`).
  - Acceptance manifest:
    `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`
    (SHA-256 `53074cfe44c0276d6f319497cbe6f5aaf07b255ac0c335f9481174dd968063fe`).
  - Acceptance commit: `9050d0eabd0ee5c41626ba924c31a67f301c7293`.
- **Evidence — historical accepted predecessor**:
  `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`
  (SHA-256 `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`). Registry v7.3 is a
  `CLOSED / ACCEPTED` **historical accepted predecessor** and is no longer the current evidence
  authority. Its bytes are immutable and unchanged; cite it for lineage, regression comparison, or the
  historical v7.3-authority record only.

Historical methodology/evidence lifecycle closure for the v7.3 pair:
`docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md`
(`V7.3 METHODOLOGY / EVIDENCE CONTENT FREEZE — CLOSED / ACCEPTED`). Its bytes are immutable. It is now
historical on **both** sides: Framework v7.4 superseded its methodology-side current-prescriptive role
additively, going forward, from the v7.4 methodology acceptance, and Registry v7.4 likewise superseded
its evidence-side current-prescriptive role additively from the Registry v7.4 acceptance closure
(`9050d0eabd0ee5c41626ba924c31a67f301c7293`). Its Registry-facing statements — including the v7.3
zero-winter role wording — remain correct **as historical v7.3-authority records**, and are read under
the accepted v7.4 pair going forward.

Lineage roles, for the record: Framework v7.3 is an accepted immutable predecessor and historical
lineage. Registry v7.3 R3 is the historical accepted evidence predecessor. Framework v7.2 and Registry
v7.2 are historical accepted predecessors only. Registry v7.3 R1/R2 are failed immutable provenance
only. Framework v7.4 Candidate R1 is immutable non-accepted candidate provenance; Candidate R2 supplied
the accepted Framework v7.4 bytes; Candidate R3 was `NOT REQUIRED / NOT CREATED`. **Registry v7.4
Candidate R1 is the historical provenance identity of the exact bytes that were independently audited
and then accepted unchanged as Registry v7.4** — it is not a separate document and not a current
lifecycle state. Apart from the accepted v7.4 pair itself, none of these is current authority.

### Registry v7.4 lifecycle — for the record

| Stage | Identity | Status |
|---|---|---|
| Candidate R1 authoring | commit `bf87b7f0659da17277fbb797099141b24343aa79` | complete; immutable provenance |
| Independent read-only audit | `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md` | `PASS` — and it explicitly did **not** self-accept |
| Acceptance closure | commit `9050d0eabd0ee5c41626ba924c31a67f301c7293` | `CLOSED / ACCEPTED` — current evidence authority |

The accepted Registry v7.4 primary bytes are **exactly** the audited Candidate R1 bytes, SHA-256
`5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433`. Acceptance was conferred by an
additive governance/provenance closure; it did **not** create rewritten Registry bytes, rename the
candidate file, or mutate it in place. The independent audit and the acceptance decision are two
separate governance actions performed in separate passes — an audit `PASS` is never self-acceptance.

### v7.3→v7.4 version/provenance transition lifecycle — for the record

- Candidate R1 remains `IMMUTABLE HISTORICAL STOP PROVENANCE`.
- Candidate R2 is `CLOSED / ACCEPTED`; its authoring-time candidate bytes remain immutable.
- The transition is `CLOSED / ACCEPTED` through
  `docs/checkpoints/v7_3_to_v7_4_version_transition_acceptance_closure_2026-09-27.md`, published in
  commit `55df7322fae9901b07d7334dcbc811ea94fbed2d`.
- That closure is governance/provenance only; it did not authorize Task 3 or Full81.

### Task 3 Layer A robustness preregistration lifecycle — current

- Candidate R1 is an `IMMUTABLE HISTORICAL STOP CANDIDATE`; its bytes must not be edited.
- Candidate R2 is `CLOSED / ACCEPTED`. Its exact immutable candidate bytes were accepted through
  `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_acceptance_closure_2026-09-27.md`
  and its companion manifest, published in commit
  `d07d34a163f0e45c8f8764526e81070f19d48747`.
- The independent Candidate R2 audit is `COMPLETED`: verdict
  `PASS WITH ONE NON-BLOCKING OBSERVATION`, acceptance-critical findings `0`. The observation concerned
  directory-digest ordering documentation precision; the accepted interpretation is relative
  forward-slash path, case-insensitive sort, classified
  `NON_BLOCKING_PROVENANCE_DOCUMENTATION_PRECISION`. No repository audit artifact path is asserted.
- This scientific/preregistration acceptance does not authorize threshold selection, U-item resolution,
  implementation, robustness execution, production-authority re-freeze, or Full81.

### V7.4 Results & Managerial-Insight Analysis Plan lifecycle — current

- Candidate R1 (`docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r1.md`;
  15,477 bytes; SHA-256 `57fc4ac6fd13bd88f94251e7252bf7f4e44a65c52cead815f5f5b766ec1e93dd`) is
  `IMMUTABLE HISTORICAL CANDIDATE PROVENANCE`; its bytes must not be edited and it is never promoted.
- Candidate R2 (`docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r2_2026-10-01.md`;
  45,741 bytes; SHA-256 `2c4931b9e07a969d93caf682e0b1483786ece0f13cb5bb63f2ab255ad28548c6`) is
  `CLOSED / ACCEPTED`. Its exact immutable candidate bytes were accepted **as written**, with zero
  wording changes applied, through
  `docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r2_acceptance_closure_2026-10-01.md`
  and its companion manifest
  `results/provenance/v7_4_results_managerial_insight_analysis_plan_candidate_r2_acceptance_closure_2026-10-01/acceptance_manifest.json`.
- The separate fresh-session independent read-only Candidate R2 audit is `COMPLETED`: verdict
  `PASS_WITH_NONBLOCKING_WORDING_NOTES`, blocking corrections `0`, methodology leakage `0`, authority
  conflicts `0`, R1-to-R2 corrections closed `21 / 21` (all Disposition A), firewalls holding `9 / 9`.
  The three notes are `NON_BLOCKING_EDITORIAL` and required no change before acceptance. The audit
  exists as an external/read-only governance result; no repository audit artifact path is asserted.
- Candidate R3 is `NOT REQUIRED / NOT CREATED`.
- The accepted scope is **interpretation discipline, not science**: it governs how accepted Layer A /
  Full81 outputs are analyzed, reported, and described. It creates no scientific model, experiment,
  case, sensitivity dimension, metric, benefit/utility function, threshold, materiality rule,
  knee-identification rule, decision criterion, forecasting method, or reserve-floor definition.
- This acceptance does **not** authorize implementation, an aggregation/reporting layer, robustness
  implementation, A2, current-route Full81, a production gate, or a production-authority re-freeze, and
  resolves no U-item.
- Publication of this closure to `origin/thesis-v7` is **not yet performed** and requires separate
  authorization.

## 2. Git state — base HEAD observed at last reconstruction

- Branch: `thesis-v7`
- **Base HEAD observed before this F-03 synchronization**:
  `d07d34a163f0e45c8f8764526e81070f19d48747` — "Governance: accept Task 3 robustness preregistration
  Candidate R2". This commit durably records the immutable Task 3 R1/R2 candidate families and the
  additive Candidate R2 acceptance closure.
  **This is not necessarily the live current HEAD** — obtain that fresh via `git rev-parse HEAD`.
- Published lineage to that base, for the record:
  `2fe2105180c68d9289eddc2668399687d4c49d2e` ("Accept Framework v7.4 methodology authority")
  -> `bf87b7f0659da17277fbb797099141b24343aa79` (Registry v7.4 Candidate R1 authoring)
  -> `9e2f05c93d7642fc07881210983a030550455a17` (post-Framework-v7.4 handoff refresh)
  -> `9050d0eabd0ee5c41626ba924c31a67f301c7293` (Registry v7.4 acceptance closure)
  -> `53e3d5e38e68d000b25eea7d06d35b4600219c02` (post-Registry-v7.4 handoff refresh)
  -> `55df7322fae9901b07d7334dcbc811ea94fbed2d` (v7.3→v7.4 transition Candidate R2 acceptance closure)
  -> `a96cf7929b84374c8e3d5a62a3fed84093268b2c` (F-02 bounded Full81 handoff correction)
  -> `d07d34a163f0e45c8f8764526e81070f19d48747` (Task 3 Candidate R2 acceptance closure).
- At this reconstruction, local `origin/thesis-v7` and the live remote `origin/thesis-v7` both pointed
  at `d07d34a163f0e45c8f8764526e81070f19d48747`, with ahead/behind `0/0` — the Task 3 closure is
  published. The future commit containing this self-referential file is intentionally not embedded in
  its own text; obtain and verify its identity live after publication. No earlier commit may be amended.
- No code, data, script, test, solver, result, checkpoint, manifest, or production-routing artifact is
  changed by this F-03 synchronization. Only this file and `PROJECT_HANDOFF.md` are synchronized.
- Earlier base HEADs recorded by previous reconstructions, retained as historical observations only:
  `52e46e83678bf24393cf561062b16e59171a39a7` (v7.3 governance-freeze baseline, 2026-09-23) and
  `23bdadaa87bd4fbb1ce849a0c774e9394a4e2270` (Step 2D acceptance-closure update, 2026-09-24).
- Published v7.3 governance tags observed at this reconstruction, present both locally and on
  `origin`: `v7.3-step2d-r3-accepted-2026-09-24` peeling to `07200697d0da7567715ec77edf3d853acbc53918`
  (Step 2D R3 durability freeze — **completed**, superseding the earlier
  `FREEZE_AUTHORIZED_IN_THIS_GATE` pending state), and
  `v7.3-step2e1-routing-authority-accepted-2026-09-24` peeling to
  `d52d9584b22da2a41b51c8ce3e99a0335e39da2b` (Step 2E-1 routing authority). These are frozen
  provenance and must not be retargeted.
- Tag state at this reconstruction: **no tag is created or moved by this correction.** Any tag-vs-HEAD
  relationship above is an observation at this base and must be re-derived live from Git.

## 3. Checkpoint / audit chain

**Current V7.4 Results & Managerial-Insight Analysis Plan chain:**

1. `docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r2_acceptance_closure_2026-10-01.md`
   and its companion acceptance manifest — Candidate R2 acceptance/lifecycle closure,
   `CLOSED / ACCEPTED`.
2. Separate fresh-session independent read-only Candidate R2 audit — `COMPLETED`, verdict
   `PASS_WITH_NONBLOCKING_WORDING_NOTES`, blocking corrections `0`. The audit exists as an
   external/read-only governance result; no committed audit artifact path is fabricated here.
3. `docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r2_2026-10-01.md` — exact
   immutable accepted candidate provenance; its authoring-time candidate wording is not rewritten.
4. `docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r1.md` — immutable
   historical candidate provenance; never promoted.

**Current Task 3 Layer A robustness preregistration chain:**

1. `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_acceptance_closure_2026-09-27.md`
   and its companion acceptance manifest — Candidate R2 acceptance/lifecycle closure,
   `CLOSED / ACCEPTED`, published in commit `d07d34a163f0e45c8f8764526e81070f19d48747`.
2. Separate fresh-session independent read-only Candidate R2 audit — `COMPLETED`, verdict
   `PASS WITH ONE NON-BLOCKING OBSERVATION`, acceptance-critical findings `0`. The audit exists as an
   external/read-only governance result; no committed audit artifact path is fabricated here.
3. `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_2026-09-27.md` — exact immutable
   accepted candidate provenance; its authoring-time candidate wording is not rewritten.
4. `docs/checkpoints/layer_a_robustness_preregistration_candidate_r1_2026-09-27.md` — immutable
   historical STOP candidate; never promoted.

**Current v7.3→v7.4 version/provenance transition record:**

1. `docs/checkpoints/v7_3_to_v7_4_version_transition_acceptance_closure_2026-09-27.md` — Candidate R2
   acceptance/lifecycle closure, `CLOSED / ACCEPTED`, published in commit `55df7322fae9901b07d7334dcbc811ea94fbed2d`.
2. `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r2_2026-09-27.md` — immutable accepted
   candidate provenance; its authoring-time candidate wording is not rewritten.
3. `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r1_2026-09-27.md` — immutable historical
   STOP provenance; never promoted.

**Framework/Registry v7.4 governance chain (most recent first):**

1. `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` — Registry
   v7.4 evidence acceptance/lifecycle closure, `CLOSED / ACCEPTED`, with
   `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`.
2. `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md` — durable
   record of the completed independent read-only audit of Registry v7.4 Candidate R1; verdict
   `REGISTRY v7.4 CANDIDATE R1 INDEPENDENT AUDIT = PASS`, explicitly **not** a self-acceptance.
3. `docs/checkpoints/literature_evidence_registry_v7_4_framework_alignment_candidate_2026-09-26.md`
   — Registry v7.4 Candidate R1 producer checkpoint. Its authoring-time disposition **CANDIDATE R1**
   was correctly not acceptance, not promotion, and not routing authorization *at that time*.
   Companion manifests:
   `results/provenance/literature_evidence_registry_v7_4_framework_alignment_candidate_r1/completion_manifest.json`
   and `.../package_manifest.json`. These candidate artifacts keep their authoring-time wording as
   immutable provenance; the current accepted lifecycle status is carried by items 1–2 above.
4. `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` — Framework v7.4
   acceptance/lifecycle closure, `CLOSED / ACCEPTED`, with
   `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`.
5. `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_r2_2026-09-26.md`
   — accepted Framework v7.4 candidate (R2) checkpoint.
6. `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_2026-09-26.md`
   — Framework v7.4 Candidate R1 checkpoint; immutable non-accepted candidate provenance.

**Historical v7.3 methodology/evidence closure chain (complete; superseded on both the methodology and
evidence sides by the accepted v7.4 pair):**

1. `docs/framework_v7_3_merge_audit_2026-09-23.md` — Framework successor merge audit, PASS/CLOSED.
2. `docs/registry_v7_3_r3_merge_audit_2026-09-23.md` — Registry R3 successor merge audit, PASS/CLOSED.
3. `docs/framework_registry_v7_3_cross_alignment_audit_2026-09-23.md` — Framework/Registry alignment
   audit, PASS/CLOSED.
4. `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` — v7.3 content/authority freeze,
   `CLOSED / ACCEPTED`.
5. Commit `52e46e83678bf24393cf561062b16e59171a39a7` — committed/pushed repository baseline containing
   the complete twelve-file v7.3 governance package.

**Step 2D acceptance closure (2026-09-24), `CLOSED / ACCEPTED`:**

- `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.md` and
  its `.json` companion manifest — acceptance-closure checkpoint;
- `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_independent_acceptance_2026-09-24.md`
  and its `.json` companion — independent acceptance attestation.

Those records document an **already-completed** independent Step 2D-A audit with verdict
`STEP_2D_CANDIDATE_R3_2D_A — PASS`, followed by a separate independent closure audit with verdict
`POST_2D_A_GOVERNANCE_CLOSURE_AUDIT — PASS`. Step 2D Candidate R3 and its post-2D-A governance closure
are both `CLOSED / ACCEPTED`.

Historical v7.2 implementation/runner evidence retained for provenance, not current production
authority:

- `docs/checkpoints/production_checkpoint_manifest_v7_2_pre81_ready_2026-09-10.json`;
- `docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-10.json`;
- `results/layer_a/final_81_execution_authorization/20260911T065811Z/`;
- `results/layer_a/final_81_runner_audit/20260911T081511741789Z_dd663aeba1/`.

The detailed historical reconstruction remains in §5. None of those v7.2 runner/tag artifacts
authorizes current production execution.

## 4. Latest completed implementation stage

- **Framework v7.4 methodology governance: `CLOSED / ACCEPTED`** (see §1). Framework v7.4 accepted
  exactly three claim-boundary changes — zero-winter current role, observed-versus-planning PV
  routing, and the \(\kappa\) claim boundary — and changed no equation, parameter, tariff rule,
  degradation rule, reserve rule, planning-input identity, or solver-facing methodology. It did **not**
  invalidate the accepted EOB or core-three results and required **no** rerun.
- **Registry v7.4 evidence governance: `CLOSED / ACCEPTED`** (see §1). The independent read-only audit
  of Candidate R1 returned `PASS` and did not self-accept; a separate acceptance closure
  (`9050d0eabd0ee5c41626ba924c31a67f301c7293`) then promoted those exact audited bytes to current
  evidence authority, with Registry v7.3 becoming the historical accepted predecessor. This acceptance
  changed no equation, parameter, unit, data value, or result, required **no** rerun, and does **not**
  authorize Full81.
- **v7.3→v7.4 version/provenance transition Candidate R2: `CLOSED / ACCEPTED`.** The additive closure
  in commit `55df7322fae9901b07d7334dcbc811ea94fbed2d` preserves Candidate R1 as immutable historical STOP
  provenance and Candidate R2's exact audited bytes. It changed no scientific content or numerical
  state and did not authorize Task 3 or Full81.
- **Task 3 Layer A robustness preregistration Candidate R2: `CLOSED / ACCEPTED`.** Candidate R1 remains
  an immutable historical STOP candidate. The separate independent Candidate R2 audit completed with
  verdict `PASS WITH ONE NON-BLOCKING OBSERVATION` and `0` acceptance-critical findings; the additive
  acceptance closure was published in commit `d07d34a163f0e45c8f8764526e81070f19d48747`.
  The accepted design is bounded as follows:
  - locked A2 cases: `a0.60_b04`, `a0.60_b12`, `a0.80_b04`, `a0.80_b12`, `a1.00_b04`,
    `a1.00_b12` — six targeted points, **not** a full factorial;
  - reusable accepted current-route constant-floor baselines: `a0.60_b04`, `a1.00_b12` (`2`);
  - missing current-route constant-floor baselines: `a0.60_b12`, `a0.80_b04`, `a0.80_b12`,
    `a1.00_b04` (`4`);
  - `required_new_variable_floor_solves = 6` for the perfect-information arm;
  - conditional extension: `a0.60_b08`, `a0.80_b08`, `a1.00_b08`, **only** if a future frozen
    material-shift rule triggers — never automatic, and no rule or threshold is selected here.
  Acceptance is scientific/preregistration closure only; it is not implementation or execution authority.
  The scientific firewall remains intact: `LEAKAGE_FINDINGS = 0`, `LOOK_AHEAD_FINDINGS = 0`, and
  `INFORMATION_ADVANTAGE_FINDINGS = 0`. Historical v7.2 R9 Full81 and historical sensitivities remain
  non-tuning provenance/validation context; accepted EOB/core-three establish baseline availability only.
- **Accepted planning input — Step 2D, `CLOSED / ACCEPTED`:**
  - `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`
    (SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`;
    role `reconstructed_pv_mainline`; rows 8,760).
  - Independent Step 2D-A verdict: `STEP_2D_CANDIDATE_R3_2D_A — PASS`. Acceptance applies **only** to
    those exact bytes.
  - Step 2D lineage: Candidate R1 `STOP / FAILED IMMUTABLE PROVENANCE` (evidence/provenance/lifecycle
    packaging defect class, **not** a numerical data defect); Candidate R2
    `STOP / ABANDONED IMMUTABLE PROVENANCE` (builder only survived; no R2 parquet or evidence
    namespace was ever published); Candidate R3 `CLOSED / ACCEPTED`. R1 and R2 remain immutable
    historical provenance and must not be modified or executed.
  - Epistemic boundary: reconstructed long-unavailable PV values are model-based/weather-informed
    planning estimates — **not** observed truth, **not** ground truth, **not** exact historical
    recovery. Do not restate them as observed data anywhere downstream.
  - Git durability freeze: **completed**. The accepted `data/` and `results/` bytes were committed in
    `0720069` despite their general gitignore rules, and the annotated tag
    `v7.3-step2d-r3-accepted-2026-09-24` is published on `origin` (§2).
- **Production routing authority (Step 2E-1): frozen and committed.**
  `src/production_input_authority_v7_3.py`,
  `scripts/21a_preflight_v7_3_production_routing.py`, and their tests were frozen in commit
  `d52d9584b22da2a41b51c8ce3e99a0335e39da2b`, which the current gate requires to be an ancestor of HEAD.
- **Production successor stack (Macro Gate 2E-A): closed.** `src/production_successor_stack_v7_3.py`
  and `scripts/21b`–`21d` (EOB, Layer A, Full81 successor preflights) were closed in commit `e668840`,
  with subsequent serialization/interlock corrections in `39af835`, `b87575c`, and `1651b31`.
- **Same-artifact routing: `COMPLETED / ACCEPTED` for the accepted EOB and core-three.** EOB/economic
  optimization and Layer A residual load, \(R(\alpha,\beta)\), \(P^{out}\), binding
  identification/classification, and outage replay all consumed the single accepted planning-input
  identity above; both run `authority.json` records show `status: "PRODUCTION_AUTHORITY_FROZEN"` with
  that identity. This is a factual execution status; it adds no routing methodology.
- **Accepted EOB: `CLOSED / ACCEPTED`** —
  `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556`. Framework v7.4 did not
  invalidate it and **no EOB rerun is required**.
- **Accepted core-three Layer A representative cases: `CLOSED / ACCEPTED`** —
  `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55`, each run with
  `surplus_pv_recharge=False`:

  | Case | \(\alpha\) | \(\beta\) |
  |---|---:|---:|
  | LOW | 0.60 | 4 h |
  | CENTRAL | 0.80 | 8 h |
  | HIGH | 1.00 | 12 h |

  Framework v7.4 did not invalidate these and **no core-three rerun is required**.
- **Two status layers for the accepted results must not be conflated.** The immutable execution-time
  `completion_manifest.json` of each run records `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE` —
  historical, correct for its moment, and **not to be rewritten**. Subsequent governance adjudication
  accepted both results, so their **current governance status** is `CLOSED / ACCEPTED`, superseding
  the historical run-lifecycle wording for current-status purposes without changing the historical
  manifest bytes.
- **Current accepted v7.3/v7.4-route Full81: `NOT_YET_EXECUTED` / `NOT_YET_AUTHORIZED`** — no Full81
  execution has yet occurred on the accepted current route using the accepted reconstructed-PV planning
  input, and neither the Registry v7.4 acceptance nor the transition closure authorized it. Core-three
  acceptance must never be written as Full81 completion, and Full81's pending state must never be
  back-propagated into EOB/core-three status.
- Historical accepted v7.2 implementation lineage, unchanged: Scripts 01 through 13c **CLOSED / PASS**
  (preprocessing, canonical annual input, billing/kappa calibration, PNNL cost dual-bracket
  construction, Xu degradation semantics audit, Taipower tariff registry + bill-component regression).
- Historical, under their original v7.2 evidence roles: Scripts 14a/14b (production economic interface,
  transition-settlement interface), the v7.2 EOB formulation benchmark/production baseline
  (`results/eob_production/`), rainflow validation, 16a representative-case preflight, and the 17a–17c
  winter-PV long-block sensitivity protocol. Step 17a, corrected 17b, and Step 17c keep their original
  historical validation, promotion-source, and adjudication evidence roles; they do **not** supersede
  the accepted EOB or accepted core-three.

## 5. Historical v7.2 no-solve authorization check — reconstruction record (base HEAD `d18d335`)

**This section records what one specific check found at one specific base HEAD. It is a reconstruction
record, not a live status feed or current production authority.** Preserve it for provenance. Do
not re-run or reuse this v7.2 runner/tag route as current authority; the current v7.3 successor stack
(§4) supplies the independently audited production identity.

**Mechanism used**: the runner's own built-in, officially-designed no-solve path — invoking
`scripts/19b_run_final_layer_a_81_cases.py` with **no** `--execute-production` flag. In that mode
`ExecutionGuard(False)` patches `gp.Model.__init__` to unconditionally raise before any model can be
constructed, blocks `optimizeAsync`/`optimizeBatch`/`tune`, and `main()` routes to `audit_only()` rather
than `production()`. `audit_only()` writes only under `results/layer_a/final_81_runner_audit/` (never
the production namespace `results/layer_a/final_81/`) and itself asserts the production artifact
registry is byte-identical before and after. No script, manifest, or authority file was modified to run
this — it is the pre-existing `--help`-documented behavior of the runner as committed.

**Command run** (from repo root):
```
.venv\Scripts\python.exe -X utf8 -B scripts\19b_run_final_layer_a_81_cases.py
```

**Result**: exit code 0.
`results/layer_a/final_81_runner_audit/20260911T081511741789Z_dd663aeba1/completion_manifest.json` —
verdict `"SCRIPT 19B IMPLEMENTATION GATE PASS — READY FOR INDEPENDENT PRE-SOLVE AUDIT"`.

- `optimization_calls: 0`, `production_surface_solved: false`, `production_cases_completed: 0`.
- `execution_guard_audit.json`: `model_construction_blocked: true`, `production_results_created: 0`.
- `authority_gate.json` → `repository`: `branch: "thesis-v7"`, `head` and `origin_tracking` both
  `d18d33546cd5a4432e4f791cc934772bf93ad6eb`, `frozen_ancestor_verified: true`,
  **`untracked_files: []`, `worktree: []`** — i.e. the F-01-class working-tree-contamination condition
  is **structurally resolved**: nothing untracked exists for the authority gate to hash or reject.
- `authority_gate.json` → `status: "PASS"` for the implementation/audit-only gate itself.

**But**: `authority_gate.json` → `deployment_status: "PRODUCTION_AUTHORITY_NOT_YET_FROZEN"`, with
`not_yet_frozen_reason: "Production tag/HEAD mismatch"`. This is the runner's own tag-based
production-authorization check (`git rev-parse v7.2-final81-runner-ready^{} == HEAD`, script lines
~330–345). In audit-only mode this is reported as data, not raised as a hard failure of the
implementation gate — but it is the authoritative signal for whether an actual `--execute-production`
invocation would be allowed to proceed at the time of the check.

**At that reconstruction against base HEAD `d18d335`, the production-ready tag did not peel to that
base HEAD.** (Separately verified: the tag `v7.2-final81-runner-ready` peels to
`f4bbdebfb37a44983462df7ffa3477536761c3a9`, the commit immediately prior to the governance commit.) **This
is an observation from that reconstruction, not a permanent declaration of current tag status.** The tag
is a live Git reference whose current target must be re-checked from Git
(`git rev-parse v7.2-final81-runner-ready^{}` vs `git rev-parse HEAD`) rather than assumed from this file
at any later time. **This does not imply authorization to retarget, delete, recreate, or force-update the
published tag** — see §7 for the governing decision on that question.

**Conclusion at that reconstruction — production execution was NOT authorized against base HEAD
`d18d335`**, for a different and more benign reason than F-01: F-01 (untracked reachable file) was
resolved; the open item was that the production tag's target did not equal the base HEAD being checked.
Per the governance decision recorded in §7, the already-published `v7.2-final81-runner-ready` tag is
preserved as historical/frozen provenance evidence and is not to be retargeted; a new production-authority
identity was the path taken instead, and that is the v7.3 successor stack recorded in §4.

**Do not** treat this PASS on the implementation/audit-only gate as production authorization at any
point in time. Do not run `--execute-production` to "check" whether the tag matters — that path performs
real production case enumeration and staging and requires its own separate authorization. Production
authorization must be re-determined live from the current repository-authority gate every time it
matters, not read off this file.

## 6. Current governance, implementation, and validation state

- **Task 3 preregistration: `CLOSED / ACCEPTED`.** Candidate R1 is immutable historical STOP provenance;
  Candidate R2 is the accepted design recorded in §4. This is not implementation or execution authority.
- **Independent Task 3 Candidate R2 audit: `COMPLETED`.** Verdict
  `PASS WITH ONE NON-BLOCKING OBSERVATION`; acceptance-critical findings `0`. The non-blocking
  directory-digest wording observation and accepted ordering interpretation are recorded in §1.
- **Final cross-document alignment audit: `COMPLETED`.** Verdict
  `PASS WITH BOUNDED ALIGNMENT ACTIONS REQUIRED`; acceptance-critical findings `0`; blocking alignment
  defects `0`. This F-03 synchronization is the bounded handoff action required by that external/read-only
  audit. No repository audit artifact path is asserted where none exists.
- **V7.4 Results & Managerial-Insight Analysis Plan Candidate R2: `CLOSED / ACCEPTED`.** Candidate R1
  remains immutable historical candidate provenance. The separate independent Candidate R2 audit
  completed with verdict `PASS_WITH_NONBLOCKING_WORDING_NOTES` and `0` blocking corrections; the
  additive acceptance closure accepted the audited bytes as written. Candidate R3 is
  `NOT REQUIRED / NOT CREATED`. This is interpretation-discipline acceptance only: it is not
  implementation or execution authority, authorizes no aggregation/reporting layer, and resolves no
  U-item. Publication of the closure to `origin/thesis-v7` is not yet performed.
- **Current-route aggregation / reporting layer: `IMPLEMENTATION / OUTPUT-SCHEMA GAP`, recorded and
  unresolved.** The historical v7.2 Full81 run emitted `surface_summary.*` and `case_matrix.csv`; the
  current-route run directory emits no cross-case aggregation. The gap requires only
  aggregation/reporting implementation from already-defined accepted outputs — **not** new methodology
  or new scientific definitions. It is not designed, specified, implemented, or authorized, and any
  future work on it requires separate authorization. An implementer must not add a
  materiality-classification column, which would depend on the unresolved `U-01`.
- **Materiality threshold: `THRESHOLD_DECISION_REQUIRED_BEFORE_EXECUTION` and
  `UNRESOLVED_BY_CURRENT_AUTHORITY`.** Accepted numerical threshold = `null`; selected threshold option =
  `null`. Neither technical tolerances nor historical Full81, core-three, EOB, historical sensitivities,
  or literature values may be used to infer or tune it.
- **Unresolved register — no item is resolved here:**
  - `U-01` materiality definition — `UNRESOLVED`;
  - `U-02` outcome / escalation taxonomy — `UNRESOLVED`;
  - `U-03` historical cost/SOC sensitivity sufficiency — `UNRESOLVED`;
  - `U-04` non-A2 robustness case universes — `UNRESOLVED`;
  - `U-05` robustness namespace / `selected_scope` — `UNRESOLVED`;
  - `U-06` v7.4 authority-bundle alignment — `UNRESOLVED_IMPLEMENTATION_AUTHORITY_ALIGNMENT`;
  - `U-07` variable-floor implementation-versus-methodology classification —
    `UNRESOLVED_CLASSIFICATION`.
- **Current implementation blockers — implementation facts, not methodology decisions or authority to
  repair them:** (B-01) no robustness scope exists in `PRODUCTION_CASE_SETS`; (B-02) no
  perfect-information variable reserve-floor implementation exists; and (B-03) Framework v7.4 / Registry
  v7.4 identities are absent from the current live pre-execution authority bundle. Robustness
  implementation and execution remain `NO-GO`.
- **Production-authority re-freeze: `RE_FREEZE_REQUIRED = YES`,
  `RE_FREEZE_NOT_YET_PERFORMED`; `U-06 = UNRESOLVED`.** Its exact scope/content requires separately
  authorized U-06 adjudication. This F-03 pass neither performs nor authorizes the re-freeze.
- **Live-gate status observation only.** `_authority_untracked_paths` in the current successor stack
  filters untracked paths under `src/`, `scripts/`, `tests/`, `data/`, and `results/`. At the observed
  pre-F-03 base, the eight unrelated pre-existing untracked paths were outside that protected surface,
  and `HEAD == origin/thesis-v7` with ahead/behind `0/0`. The production gate was **not run** here, so
  `PRODUCTION_AUTHORITY_FROZEN` is not claimed and production is not authorized. The runner must
  re-determine authority live at the then-live HEAD before any production execution.
- **Current accepted v7.3/v7.4-route Full81: `NOT_YET_EXECUTED` / `NOT_YET_AUTHORIZED`.** No Full81
  execution has yet occurred on that route using the accepted reconstructed-PV planning input. A
  historical v7.2 R9 Full81 production execution does exist: it completed 81 cases using
  `data/processed/annual_input_v7_1.parquet` and is retained at
  `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da` as immutable historical
  provenance. It is not the current v7.3/v7.4 Full81 and cannot serve as a controlled current-route
  counterfactual.
- Post-solve exact demand maxima and ex-post rainflow/cycle-depth validation beyond the accepted EOB
  and core-three runs remain pending for the Full81 surface, because current-route Full81 has not been
  executed.
- Corrected Sep-18 reconstructed-PV artifact: promotion-source candidate only; not canonical and must
  not be renamed or mutated into the canonical artifact. It remains the accepted numerical promotion
  source **from which** the Step 2D canonical artifact was constructed; that does not make it
  canonical.
- Layer B benchmark-design count (3/5/9) and coordinates: explicitly deferred until after Layer A
  (Framework §0.2) — do not decide this from implementation convenience.
- DG extension CAPEX/FOM/fuel/emission parameter audit: not started; may proceed in parallel with
  Layer A per Framework §0.3, but has not been started as of this writing.

## 7. Next legal step

> **SEPARATELY AUTHORIZED U-ITEM ADJUDICATION.** It is not performed or authorized by this F-03
> handoff synchronization.

Current go/no-go state: Task 3 preregistration is `CLOSED / ACCEPTED`; this F-03 publication completes
the bounded handoff synchronization; U-item adjudication is `NOT YET PERFORMED`; robustness
implementation is `NO-GO`; current-route Full81 is `NO-GO / NOT_YET_AUTHORIZED / NOT_YET_EXECUTED`;
robustness execution is `NO-GO`; and the production-authority re-freeze is required but not yet performed.
Scientific acceptance must not be conflated with implementation or execution authorization.

**Next legal sequence — each item requires separate authorization, and none is pre-authorized here:**

1. U-item adjudication, prioritizing `U-01` materiality-threshold freeze, `U-06` authority-bundle
   alignment / re-freeze scope, and `U-07` variable-floor implementation classification.
2. Production-authority re-freeze.
3. Robustness implementation candidate.
4. Independent audit / acceptance of that implementation as required.
5. Current-route Full81 authorization.
6. Full81 execution.
7. A2 robustness execution.

**Step 2D is closed.** For the record, Step 2D was required to be separately authorized and followed by
an independent canonical-artifact audit before any same-artifact production routing, and it was
forbidden from:

- renaming or mutating the corrected v7.2 sensitivity artifact into canonical;
- overwriting observed columns or describing reconstructed values as observed truth/exact recovery;
- authorizing EOB/economic, Layer A, or baseline Layer B routing in the artifact-construction step;
- running EOB, representative cases, or final81 within that step.

The independent Step 2D-A audit verified each of those constraints against primary repository bytes and
returned `STEP_2D_CANDIDATE_R3_2D_A — PASS`. Routing was authorized afterwards, separately, through the
Step 2E-1 freeze and the Macro Gate 2E-A successor stack recorded in §4.

Historical v7.2 production tags and runner/authority manifests remain frozen provenance. They must not
be retargeted or cited as current production authority. Any further routing/runner authority must be
additive, independently audited, and verified against the then-live HEAD.
