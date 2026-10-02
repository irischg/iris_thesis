# Project Handoff — Iris Thesis (Campus PV–BESS Service-Continuity Planning)

**Stable orientation document.** This file explains what the research is, how the pipeline fits
together, and who/what controls methodology. It does not track day-to-day implementation status —
that is `CURRENT_STATE.md`.

## 1. The research problem, in plain language

When a large electricity consumer (a campus) wants to keep some fraction of its load running through
a grid outage, without relying on onsite combustion as the mainline backup, its PV + BESS system has
to do three jobs at once:

1. normal-operation cost optimization — electricity bill, contract capacity, peak shaving;
2. build up an energy reserve in case an outage starts;
3. actually supply energy and instantaneous power during an outage, for a target service fraction
   \(\alpha\) and design outage duration \(\beta\).

Resilience is therefore not "add a separate backup battery" — it is a constraint on how freely the
*same* BESS can be used day-to-day, which can force larger energy and power capacity than a pure
cost-minimizing design would choose.

The thesis quantifies: for different \((\alpha, \beta)\) targets, how much BESS energy capacity, power
capacity, and annual cost is required; when a fixed design fails as PV degrades and demand grows; and,
if a hypothetical diesel generator (DG) extension is allowed, how cost trades off against onsite CO₂.

## 2. Role of NTUST

**NTUST (National Taiwan University of Science and Technology) is a demonstration case, not the
research question itself.** Its load, PV, tariff class (Taipower high-voltage, project-labeled
SCHOOL/FROZEN), and billing-demand calibration (\(\kappa\)) are used to instantiate and validate the
framework — they are not claimed as universal parameters, and results are not claimed to guarantee
real-world outage performance (see Framework §1.2 "不應主張").

## 3. Pipeline overview (conceptual)

```
raw data (load, PV, weather, tariff, cost sources)
  -> Scripts 01–05: preprocessing, load/PV baseline reconstruction, calendar/TOU build
  -> Script 06: historical v7.2 integrated annual input (accepted historical/canonical lineage)
  -> Scripts 07–10: billing-demand registry, kappa calibration, outage-start sets,
     BESS state semantics audit
  -> Scripts 11a–11h: PNNL v2024 LFP cost profiling, linearization, dual-bracket
     (1 MW / 10 MW) cost-package construction
  -> Script 12a: Xu-derived intertemporal degradation semantics audit
  -> Scripts 13a–13c: Taipower tariff registry + pure-season bill-component regression
  -> Script 14a: production economic interface (mainline cost package, constant
     NTD-2023 tariff layer)
  -> Script 14b: transition-period (May/October) settlement interface
  -> Scripts 15a/15c: EOB formulation benchmark, rainflow validation methodology
  -> Scripts 16a–18b: representative-case preflight, winter-PV long-block sensitivity
     protocol (17a–17c), production-environment/checkpoint validation
  -> Script 20c: builder for the accepted reconstructed-PV mainline annual planning input
  -> Scripts 21a–21d + src/production_successor_stack_v7_3.py: production routing authority
     and the EOB / Layer A / Full81 successor preflights and runners
  -> EOB production baseline (results/eob_production_v7_3/*)
  -> Layer A: dense 9x9 alpha/beta grid, annual design optimization + outage replay
     (representative core-three executed first; Full81 is the complete surface)
  -> Layer B: fixed-design benchmark scenarios (3, 5, or 9 designs, selected after Layer A)
  -> DG extension: hypothetical diesel-backup cost/emission comparison
```

Historical lineage retained for provenance: Scripts 19a/19b are the **v7.2** final-81 preflight and
Layer A production runner, and `results/eob_production/` is the **v7.2** EOB production baseline.
Neither is the current production route; see `CURRENT_STATE.md`.

**Do not infer that a stage is complete because its script exists.** This pipeline map describes what
each stage *does*, not whether it has currently run or passed. Current completion/pass/pending status
is controlled only by `docs/ai_handoff/CURRENT_STATE.md` and the latest applicable checkpoint/audit —
consult it before making any claim about what has actually been executed or accepted.

### Reconstructed-PV and observed-PV routing (accepted Framework v7.4)

The accepted methodology uses reconstructed full-year PV, including the prolonged winter unavailable
block, as the best-estimate **planning** mainline. Reconstructed values are weather-informed,
model-based, separately validated planning estimates — never observed historical PV truth, exact
ground truth, exact recovery of the unavailable series, or online forecast information.

Framework v7.4 fixes the epistemic routing as two layers, with **no hybrid routing**:

| Layer | Data identity |
|---|---|
| Historical empirical / calibration | observed data wherever valid |
| Planning / counterfactual model | the accepted reconstructed full-year PV (one artifact identity) |

Planning consumers consistently include EOB/economic optimization, Layer A, Full81,
\(R(\alpha,\beta)\), \(P^{out}\), binding-outage identification/classification, Layer A outage
consistency replay, and baseline Layer B. The single accepted planning artifact and its status live in
`CURRENT_STATE.md`.

**Zero-winter — current role.** Under accepted Framework v7.4, zero-winter is **historical
conservative validation / provenance evidence** supporting the reconstructed-PV promotion and
adjudication decision. It is **not** a mandatory EOB, Layer A, or Layer B sensitivity, not an
equal-status alternative planning baseline, and no new zero-winter solve is required. *Historically*,
zero-winter was the v7.2 mainline treatment and then a conservative stress/sensitivity under v7.3;
those past-scoped statements remain true as historical records, and existing zero-winter artifacts,
manifests, checkpoints, and audits keep their original acceptance boundaries.

**\(\kappa\) claim boundary.** Historical \(\kappa\) calibration uses observed valid historical data
only. The accepted reconstructed planning PV does not redefine or re-estimate \(\kappa\). \(\kappa\)
remains a billing-demand proxy — not sub-hourly physical validation.

## 4. Layer A / Layer B / DG — conceptual roles

- **Layer A**: the core annual design optimization. For each \((\alpha, \beta)\) cell in a dense
  9×9 grid, optimize BESS energy/power sizing, contract capacity, and annual dispatch, subject to a
  worst-case reserve constraint sized against *every* valid historical outage start in the case year,
  then replay the outage. Annual normal-operation optimization and outage replay are two separate
  model stages (A2, CLOSED) — not a single joint dispatch. Representative cases (LOW / CENTRAL / HIGH)
  are a subset of that grid and are a different execution state from the complete Full81 surface; the
  two must never be conflated.
- **Layer B**: takes Layer A's *finished* design(s) — it does not re-optimize equipment — and runs
  structured, non-probabilistic scenarios against them. Layer B scenario coverage is explicitly not
  claimed to be a reliability probability.
- **DG (diesel generator) extension**: a hypothetical, exogenous coverage extension, reported on cost,
  fuel, and onsite CO₂ together — not collapsed into a single objective via an assumed carbon price.
  Existing campus emergency DG is out of scope for the aggregate mainline optimization.

## 5. Authority hierarchy (read this before trusting any number or rule)

1. **`docs/research_framework_v7_4_2026-09-26_r2.md`** — current methodology source of truth
   (`CLOSED / ACCEPTED`). The formal methodology name is **Framework v7.4**, never "Framework v7.4
   R2"; the `_r2` suffix is repository/provenance identity only. Its acceptance evidence is
   `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` and
   `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`.
2. **`docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`** — current evidence source of
   truth (literature-vs-project-vs-implementation-choice mapping), `CLOSED / ACCEPTED`. The formal
   evidence name is **Registry v7.4**, never "Registry v7.4 R1"; `Candidate R1` is
   repository/provenance revision identity only. Its acceptance evidence is
   `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md` (the completed
   independent read-only audit of Candidate R1, verdict `PASS`, explicitly not a self-acceptance),
   `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` (the separate
   acceptance closure), and
   `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json`,
   accepted in commit `9050d0eabd0ee5c41626ba924c31a67f301c7293`. The accepted bytes are **exactly**
   the audited Candidate R1 bytes — acceptance created no rewritten Registry copy, renamed nothing, and
   mutated nothing in place.
3. **Current repository working tree + latest accepted applicable implementation checkpoint/audit** —
   current implementation state. Exact numeric values (parameters, hashes, cost coefficients) live in
   machine-readable artifacts (`data/reference/*.json`/`*.csv`, `results/parameter_audit/*`), not
   hard-coded in the framework text.

**`docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` (Registry v7.3) is the historical
accepted evidence predecessor.** It is `CLOSED / ACCEPTED` and immutable, and it is no longer the current
evidence authority — Registry v7.4 superseded that role additively at the acceptance closure recorded
above. Registry v7.3 remains citable for lineage, labeled regression comparison, and the historical
v7.3-authority record, never as current evidence authority.

*Historically*, the same bytes now accepted as Registry v7.4 were first published as **Candidate R1**
provenance, and were candidate-only — with the independent audit outstanding and acceptance not yet
done — until that audit passed and a separate closure accepted them unchanged. Those past-scoped
statements remain true as historical records and do not describe the current lifecycle state.

Framework v7.3 is an accepted immutable predecessor and historical lineage; so are Framework v7.2 and
Registry v7.2. `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` is the v7.3
methodology/evidence lifecycle closure: its bytes are immutable, and it is now historical on **both**
sides — Framework v7.4 superseded its methodology-side current-prescriptive role additively going
forward, and Registry v7.4 likewise superseded its evidence-side current-prescriptive role additively at
the Registry v7.4 acceptance closure. Its Registry-facing content remains correct as a historical
v7.3-authority record. Registry v7.3 R1 and R2, and
Framework v7.4 Candidate R1, are failed or non-accepted immutable candidate provenance only. Earlier
framework/registry versions and failed candidates are **provenance / regression / historical lineage
only** unless the current accepted authorities explicitly assign another role. They may explain lineage
or support a labeled regression comparison, never act as current methodology/evidence authority.

### Current governance sequence and execution boundary

Dated, detailed Git and implementation status stays in `CURRENT_STATE.md`. The current governance
position is:

1. Framework v7.4 methodology acceptance — closed.
2. Registry v7.4 evidence acceptance — closed.
3. Task 3 Candidate R1 — `IMMUTABLE HISTORICAL STOP CANDIDATE`.
4. Task 3 Candidate R2 — independently audited and `CLOSED / ACCEPTED` in commit
   `d07d34a163f0e45c8f8764526e81070f19d48747`. Its current lifecycle authority is
   `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_acceptance_closure_2026-09-27.md`.
   The independent audit verdict was
   `PASS WITH ONE NON-BLOCKING OBSERVATION`, with `0` acceptance-critical findings. Its observation was
   directory-digest ordering documentation precision; the accepted interpretation is relative
   forward-slash path, case-insensitive sort (`NON_BLOCKING_PROVENANCE_DOCUMENTATION_PRECISION`).
5. Final cross-document alignment audit — completed; verdict
   `PASS WITH BOUNDED ALIGNMENT ACTIONS REQUIRED`, with `0` acceptance-critical findings and `0`
   blocking alignment defects. This F-03 publication performs the required bounded handoff alignment;
   no repository audit artifact path is invented for the external/read-only audit result.
6. V7.4 Results & Managerial-Insight Analysis Plan Candidate R1 — `IMMUTABLE HISTORICAL CANDIDATE
   PROVENANCE`; Candidate R2 — independently audited and `CLOSED / ACCEPTED`. Its current lifecycle
   authority is
   `docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r2_acceptance_closure_2026-10-01.md`.
   The independent audit verdict was `PASS_WITH_NONBLOCKING_WORDING_NOTES`, with `0` blocking
   corrections, `0` methodology leakage, `0` authority conflicts, `21 / 21` R1-to-R2 corrections closed,
   and `9 / 9` firewalls holding. Its three notes are `NON_BLOCKING_EDITORIAL` and required no change
   before acceptance; the audited bytes were accepted as written and Candidate R3 is
   `NOT REQUIRED / NOT CREATED`. That plan governs interpretation discipline for Layer A / Full81
   results — how accepted outputs are analyzed, reported, and described — and creates no scientific
   definition. Its acceptance is not implementation or execution authority, authorizes no
   aggregation/reporting layer, and resolves no U-item. That closure **is published** — commit
   `2b13f22c3e98f16c669d89256b29425cd91baa5f`, an ancestor of `origin/thesis-v7`. Being published does
   **not** make it a production-authority pin: its role is downstream interpretation/analysis
   governance, not production execution authority, so it is deliberately **not** bound into the V7.4
   production-authority bundle.
7. Task 3 governance-sequencing successor — original candidate `IMMUTABLE HISTORICAL CANDIDATE
   PROVENANCE`; Candidate R2 independently audited (`INDEPENDENT_R2_AUDIT_PASS`, `CRITICAL 0 /
   MAJOR 0 / MINOR 0`, one non-blocking `INFORMATIONAL`, `0` blocking corrections) and
   `CLOSED / ACCEPTED`, published in commit `fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0`. Its current
   lifecycle authority is
   `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md`.
   Its bounded delta: **`U-01` remains `OPEN / HOLD` but no longer blocks Main V7.4 Full81
   authorization, execution, inspection, analysis, or supervisor discussion.** The accepted freeze
   order is `[A2_EXECUTION, A2_RESULT_EXPOSURE, A2_INTERPRETATION,
   A2_CONDITIONAL_EXTENSION_AUTHORIZATION]`, with `FULL81_AUTHORIZATION` deliberately absent. `U-01`
   must still be resolved, independently audited, accepted, and frozen before every one of those four
   A2 events, and A2 stays `HARD BLOCKED` behind an intact zero-exposure firewall. The supersession of
   Task 3 Candidate R2 is bounded to that ordering question only. That closure also fixed the mandatory
   remaining lifecycle: production-authority V7.4 alignment / re-freeze -> fresh independent
   verification of it -> separate Main Full81 authorization / preflight -> Main Full81 execution. There
   is no direct acceptance-to-Full81 path.
8. U-06 V7.4 production-authority alignment — three candidates, none accepted. **R1 FAILED its
   independent audit** (`F-01`, lifecycle anchoring). **R2 received `NO-GO — CRITICAL GOVERNANCE
   DEFECT`** on `A-01` (CRITICAL: arbitrary unrelated tracked/clean/hash-correct historical artifacts
   could satisfy the lifecycle roles), `A-02` (incomplete runtime implementation identity), and `A-03`
   (insufficient publication-containment proof); R2 must never be accepted, closed, frozen, committed
   as production authority, or used to authorize Full81. Both are retained as immutable provenance and
   their verdicts are not softened. The remediated **Candidate R3** is
   `CANDIDATE / NOT ACCEPTED / NOT CLOSED / NOT FROZEN / PENDING FRESH INDEPENDENT AUDIT`, at
   `docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02.md` with
   `results/provenance/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02/alignment_manifest.json`.
   The implementation separates identity from lifecycle: `src/production_authority_bundle_v7_4.py`
   holds the base V7.4 authority identity (`31` exact pins, reporting `CANDIDATE_ALIGNED`) and
   `src/production_authority_lifecycle_u06.py` holds all audit/acceptance/freeze authority (currently
   `ABSENT` / `NOT_FROZEN`) under lineage `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3`. Every lifecycle
   role must now prove **role authenticity** — a role-specific `artifact_type` and `schema_version`,
   the exact lineage and candidate identity, the live implementation-identity digest, and the exact
   identity of every earlier role — not merely a path, a digest, and a clean Git status. The accepted
   implementation identity covers **20** traced runtime and gate-protected paths, tests excluded, and a
   committed, clean, pushed change to any of them fails the freeze closed. Publication is proved by
   **containment in a named commit**, not by arbitrary `HEAD` ancestry.
   `src/production_input_authority_v7_3.py` is byte-identical and preserved as historical provenance.
   R3 is **not accepted, not independently audited, not a production-authority re-freeze, and not
   Full81 authorization**, and `F-01`/`A-01`/`A-02`/`A-03` are `REMEDIATION IMPLEMENTED — PENDING FRESH
   INDEPENDENT VERIFICATION`. See `CURRENT_STATE.md` §1.1.

Keep these governance distinctions intact: an independent audit is not an acceptance decision;
acceptance is not publication; publication is not handoff synchronization; handoff synchronization is
not scientific or execution authorization; Registry or Task 3 acceptance is not Full81 authorization;
and **production-authority V7.4 alignment is not Full81 authorization either** — the current
implementation keeps `PRODUCTION_AUTHORITY_ALIGNMENT` and `MAIN_FULL81_AUTHORIZATION` as independent
fields, with the `full81` scope rejected unconditionally until a separate authorization artifact exists.

The accepted Task 3 preregistration is a targeted six-point A2 model-form screen, **not** a full
factorial. Its locked cases are `a0.60_b04`, `a0.60_b12`, `a0.80_b04`, `a0.80_b12`, `a1.00_b04`, and
`a1.00_b12`. Accepted current-route constant-floor baselines are reusable for `a0.60_b04` and
`a1.00_b12` (`2` available); `a0.60_b12`, `a0.80_b04`, `a0.80_b12`, and `a1.00_b04` are missing (`4`).
`required_new_variable_floor_solves = 6` for the perfect-information arm. The only conditional
extension is `a0.60_b08`, `a0.80_b08`, and `a1.00_b08`, and it applies only if a future **frozen**
material-shift rule triggers; beta=8 expansion is not automatic, and no rule or threshold is selected here.

The scientific firewall remains intact: `LEAKAGE_FINDINGS = 0`, `LOOK_AHEAD_FINDINGS = 0`, and
`INFORMATION_ADVANTAGE_FINDINGS = 0`. Historical v7.2 R9 Full81 remains provenance/validation context
only and cannot tune the threshold, PASS rule, or A2 case selection; accepted core-three establishes
baseline availability only and likewise cannot tune the materiality threshold.

The threshold state is `THRESHOLD_DECISION_REQUIRED_BEFORE_EXECUTION` and
`UNRESOLVED_BY_CURRENT_AUTHORITY`; accepted numerical threshold = `null`, selected threshold option =
`null`. `U-01` materiality definition, `U-02` outcome/escalation taxonomy, `U-03` historical cost/SOC
sensitivity sufficiency, `U-04` non-A2 case universes, and `U-05` robustness namespace/`selected_scope`
are `UNRESOLVED`; `U-06` v7.4 authority-bundle alignment is
`V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT` (Candidate R1 failed audit, Candidate R2 is
a CRITICAL `NO-GO`, Candidate R3 is pending, and the live route now derives this status from the
accepted-lifecycle overlay rather than a constant); and `U-07` variable-floor
implementation-versus-methodology classification is `UNRESOLVED_CLASSIFICATION`, scope **A2-only**, and
**not** a Main Full81 blocker. None is resolved here. `U-01` is `OPEN / HOLD`: still required before
every A2 event, no longer a blocker of Main Full81.

Two A2-side implementation facts remain blockers: no robustness scope exists in `PRODUCTION_CASE_SETS`,
and no perfect-information variable reserve-floor implementation exists. A third — that the live
pre-execution authority bundle did not include Framework v7.4 / Registry v7.4 identities — now has an
**unaccepted candidate remedy** in U-06 Candidate R3, which binds those identities in the live gate and
verifies them from live bytes; it is not closed, because closure requires the fresh independent audit of
R3 and a separate acceptance. These facts are not methodology
decisions or authority to repair or implement anything. A production-authority re-freeze is required
(`RE_FREEZE_REQUIRED = YES`) but has not been accepted (`RE_FREEZE_NOT_YET_ACCEPTED`). Production
authority must be re-determined live by the runner at the then-live HEAD — read
`src/production_successor_stack_v7_3.py`, `src/production_authority_bundle_v7_4.py`, and
`src/production_authority_lifecycle_u06.py` directly; this handoff does not claim that the gate was run
in authorizing mode or that production is authorized. With no accepted U-06 R3 lifecycle record, the
gate currently fails closed for every production scope.

**Current accepted v7.3/v7.4-route Full81 is `NOT_YET_EXECUTED` / `NOT_YET_AUTHORIZED`.** No Full81
execution has yet occurred on that route using the accepted reconstructed-PV planning input. A historical
v7.2 R9 Full81 production execution exists as immutable historical provenance; it is not the current
Full81 and cannot serve as a controlled current-route counterfactual. Accepting Framework v7.4 and
Registry v7.4 did not authorize current-route Full81, and the accepted representative core-three cases
must never be written up as the complete Full81 surface. The accepted preregistration did not depend
on any current-route Full81 result.

The next legal sequence, with every item separately authorized, is: (1) fresh independent read-only
audit of U-06 production-authority alignment Candidate R3, with the `A-01` substitution attack
re-attempted against the live validator; (2) acceptance of that alignment, creation of the accepted
U-06 R3 lifecycle record across its three publication phases, and the production-authority re-freeze it
supports — noting that committing alone is explicitly insufficient for a freeze; (3) separate Main V7.4 Full81 authorization/preflight; (4) Main
Full81 execution; (5) the cross-case surface-summary aggregation layer, required before substantive
response-surface interpretation or meeting analysis but **not** a prerequisite for executing Full81;
(6) `U-01` resolution, independent audit, acceptance, and freeze, required before any A2 event;
(7) `U-07` classification, then the robustness implementation candidate and its independent
audit/acceptance; and (8) A2 robustness execution. This ordering authorizes none of those actions.
Current go/no-go state: U-06 Candidate R1 failed its independent audit, Candidate R2 is a CRITICAL
`NO-GO`, and Candidate R3 exists as an unaccepted, un-audited candidate; production authority is
`NOT_FROZEN`; robustness
implementation is `NO-GO`; current-route Main Full81 is
`NO-GO / NOT_YET_AUTHORIZED / NOT_YET_EXECUTED`; A2 robustness execution is `HARD BLOCKED`; and the
required production-authority re-freeze has not been accepted. **No Full81 result exists.**

## 6. Methodology vs. implementation status — keep these separate

- **Methodology CLOSED** means the *research rule* is settled (e.g., "efficiency is applied once,
  AC/PCS-side, η=0.90") and may not be revisited without a demonstrated code/data/source-transcription
  error.
- **Implementation status** (built / audited / CLOSED-PASS / pending / not started) describes whether
  the code *correctly encodes* that already-settled rule, and whether it has produced accepted
  evidence. A script existing, or even solving successfully, is implementation progress — it is not by
  itself a reopening or a re-validation of methodology, and it is not by itself proof of research
  readiness. See `docs/protocols/iris_thesis_rigorous_audit_skill.md` §5–6 for the full discipline.
- **A result's execution-time manifest status and its governance status are two different layers.** A
  run manifest records what was true when the run finished (for example, "complete, pending
  independent acceptance"); a later governance adjudication may accept that result. The manifest bytes
  are never rewritten to match the newer governance status — read current status from
  `CURRENT_STATE.md` and the governing checkpoint, not from a historical run manifest.

## 7. Major CLOSED methodological families (see Framework §0.1 for exact wording)

- **A1** — BESS efficiency: AC/PCS-side, \(\eta_c = \eta_d = 0.90\) fixed, applied once.
- **A2** — annual optimization and outage replay are separate model stages; replay starts from the
  minimum preparedness state and may draw down to technical SOC_min during an outage.
- **A3** — NTUST mainline optimizes a single annual regular contract capacity \(CC\); supplementary
  contracts fixed at 0; four TOU periods and non-duplication/over-contract rules retained.
- **A4** — cost-facing demand/exceedance variables are not treated as exact diagnostics; all
  period/month maxima are recomputed ex-post from the optimized grid profile.
- **B1** — mainline degradation is a PNNL-calibrated adaptation of Xu et al.'s intertemporal convex
  PWL DOD-sensitive cycle-aging model with persistent segment states; rainflow is ex-post validation
  only, not embedded in sizing.
- **B2** — total cost = annualized CAPEX + annual FOM + operating cost (incl. cycling degradation); no
  separate replacement/augmentation cash-flow stream.
- **Gate 1** — BESS cost scale is fixed ex-ante: PNNL v2024 10 MW-scale package = mainline, 1 MW-scale
  package = higher-cost sensitivity. Never switched based on optimized \(P^B\).
- **Gate 2** — all optimization-facing monetary terms use constant NTD-2023; \(r = 5\%\) is a real
  discount-rate modeling assumption (\(n=20\) yr, \(CRF \approx 0.080243\)).
- Case year: 2024-11-01 00:00 to 2025-11-01 00:00 (Asia/Taipei), hourly, \(T = 8760\), no year-end
  wrap for outage-start adequacy.
- High-voltage summer calendar fixed at May 16–October 15 (no whole-month shortcut); non-summer peak
  is N/A (not a 0-rate peak); May/October 50/50 basic-charge transition is an NTUST-case-validated
  empirical rule, not claimed as universal Taipower policy.
- Subsidy is not a separate objective cash-flow term; the model uses the audited effective billed
  tariff as the institutional price signal (no double counting).

Framework v7.4 changed none of the above. It accepted exactly three claim-boundary clarifications —
zero-winter's current role, observed-versus-planning PV routing, and the \(\kappa\) claim boundary
(all summarized in §3) — and altered no equation, parameter, tariff rule, degradation rule, reserve
rule, planning-input identity, or solver-facing methodology.

## 8. Provenance rule for legacy artifacts

Historical frozen artifacts (older EOB runs, predecessor checkpoints, `scripts_archive/`, superseded
framework/registry versions, failed and non-accepted candidates) must remain untouched and are never
used as evidence for the *current* formulation. Do not "fix" a provenance/hash guard to make an old
script or artifact match new code — a guard rejecting something is a signal to investigate, not an
obstacle.

## 9. Where things live

| What | Where |
|---|---|
| Current methodology source of truth | `docs/research_framework_v7_4_2026-09-26_r2.md` (formal name: Framework v7.4) |
| Framework v7.4 acceptance evidence | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md`, `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` |
| Current evidence source of truth | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` (formal name: Registry v7.4) |
| Registry v7.4 acceptance evidence | `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md`, `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md`, `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` (acceptance commit `9050d0e`) |
| Registry v7.4 Candidate R1 authoring provenance (historical) | `docs/checkpoints/literature_evidence_registry_v7_4_framework_alignment_candidate_2026-09-26.md`, `results/provenance/literature_evidence_registry_v7_4_framework_alignment_candidate_r1/` |
| v7.3 methodology/evidence lifecycle closure (now historical on both the methodology and evidence sides) | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` |
| Historical accepted predecessors | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` (Registry v7.3), `docs/research_framework_v7_3_2026-09-23.md`, `docs/research_framework_v7_2_2026-08-24.md`, `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` |
| Non-accepted / failed immutable candidates | `docs/research_framework_v7_4_2026-09-26.md` (Framework v7.4 Candidate R1), `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` (Registry R1), `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` (Registry R2) |
| Earlier historical framework/registry lineage | `docs/research_framework_v7_2026-08-14.md`, `docs/research_framework_v7_1_2026-08-16.md`, `docs/thesis_literature_evidence_registry_v7_2026-08-14.md`, `docs/thesis_literature_evidence_registry_v7_1_2026-08-16.md` |
| Numbered pipeline scripts | `scripts/` (active), `scripts_archive/` (superseded, do not use as production input) |
| Current production routing authority and successor stack | `src/production_input_authority_v7_3.py` (inherited, unmodified, historical v7.3 pins), `src/production_authority_bundle_v7_4.py` (additive V7.4 base authority identity — candidate), `src/production_authority_lifecycle_u06.py` (U-06 R3 accepted-lifecycle overlay — absent/not frozen), `src/production_successor_stack_v7_3.py`, `scripts/21a`–`21e`. The audited runtime production dependency surface is `RUNTIME_PRODUCTION_DEPENDENCY_PATHS` in the overlay module (16 executed paths; 20 including gate-protected ones). |
| U-06 alignment Candidate R3 (current) | `docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02.md`, `results/provenance/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02/alignment_manifest.json` |
| U-06 alignment Candidate R2 (CRITICAL NO-GO, immutable) | `docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02.md`, `results/provenance/u_06_v7_4_production_authority_alignment_candidate_r2_2026-10-02/alignment_manifest.json` |
| U-06 alignment Candidate R1 (failed audit, immutable) | `docs/checkpoints/u_06_v7_4_production_authority_alignment_candidate_2026-10-02.md`, `results/provenance/u_06_v7_4_production_authority_alignment_candidate_2026-10-02/alignment_manifest.json` |
| U-06 superseded candidate source snapshot | `results/provenance/u_06_v7_4_production_authority_alignment_candidate_r3_2026-10-02/superseded_sources/` |
| Task 3 governance-sequencing successor acceptance evidence | `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md`, `results/provenance/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01/acceptance_manifest.json` (published commit `fbdd5f0`) |
| Core annual optimization model | `src/annual_design_model_v7_2.py` |
| Rainflow ex-post validation | `src/rainflow_validation_v7_2.py` |
| Data | `data/raw/`, `data/interim/`, `data/processed/` (accepted annual planning input, valid outage starts), `data/reference/` (tariffs, parameter registry, economic interface — machine-readable production parameters) |
| Results / audits | `results/` (subdirectories per script family: `data_audit`, `parameter_audit`, `model_audit`, `billing_audit`, `degradation_validation`, `eob_benchmark*`, `eob_production` (v7.2 historical), `eob_production_v7_3`, `sensitivity`, `layer_a`, `anchors`, `provenance`) |
| Frozen checkpoints / production authority manifests | `docs/checkpoints/` |
| Cross-agent / audit protocol | `docs/protocols/iris_thesis_rigorous_audit_skill.md` |
| Tests | `tests/` |

Do not invent completed results in this document or in `CURRENT_STATE.md`. If a claim cannot be traced
to a script, checkpoint, or audit artifact, mark it explicitly as not yet demonstrated.
