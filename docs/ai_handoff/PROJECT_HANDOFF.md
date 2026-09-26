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
2. **`docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`** — current evidence source of
   truth (literature-vs-project-vs-implementation-choice mapping), `CLOSED / ACCEPTED`. **Registry
   v7.3 remains the evidence authority.**
3. **Current repository working tree + latest accepted applicable implementation checkpoint/audit** —
   current implementation state. Exact numeric values (parameters, hashes, cost coefficients) live in
   machine-readable artifacts (`data/reference/*.json`/`*.csv`, `results/parameter_audit/*`), not
   hard-coded in the framework text.

**Registry v7.4 is a candidate, not authority.**
`docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` exists as **Candidate R1** provenance.
Its independent audit is pending and it has not been accepted. It must never be cited as the current
evidence authority; Registry v7.3 holds that role until an independent audit and a separate explicit
closure say otherwise.

Framework v7.3 is an accepted immutable predecessor and historical lineage; so are Framework v7.2 and
Registry v7.2. `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` is the v7.3
methodology/evidence lifecycle closure: its bytes are immutable, Framework v7.4 supersedes its
methodology-side current-prescriptive role additively going forward, and its Registry-facing content
remains correct under the still-current Registry v7.3 authority. Registry v7.3 R1 and R2, and
Framework v7.4 Candidate R1, are failed or non-accepted immutable candidate provenance only. Earlier
framework/registry versions and failed candidates are **provenance / regression / historical lineage
only** unless the current accepted authorities explicitly assign another role. They may explain lineage
or support a labeled regression comparison, never act as current methodology/evidence authority.

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
| Current evidence source of truth | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` (Registry v7.3) |
| Registry v7.4 — candidate only, audit pending | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`, with `docs/checkpoints/literature_evidence_registry_v7_4_framework_alignment_candidate_2026-09-26.md` |
| v7.3 methodology/evidence lifecycle closure (methodology side now historical) | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` |
| Historical accepted predecessors | `docs/research_framework_v7_3_2026-09-23.md`, `docs/research_framework_v7_2_2026-08-24.md`, `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` |
| Non-accepted / failed immutable candidates | `docs/research_framework_v7_4_2026-09-26.md` (Framework v7.4 Candidate R1), `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` (Registry R1), `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` (Registry R2) |
| Earlier historical framework/registry lineage | `docs/research_framework_v7_2026-08-14.md`, `docs/research_framework_v7_1_2026-08-16.md`, `docs/thesis_literature_evidence_registry_v7_2026-08-14.md`, `docs/thesis_literature_evidence_registry_v7_1_2026-08-16.md` |
| Numbered pipeline scripts | `scripts/` (active), `scripts_archive/` (superseded, do not use as production input) |
| Current production routing authority and successor stack | `src/production_input_authority_v7_3.py`, `src/production_successor_stack_v7_3.py`, `scripts/21a`–`21d` |
| Core annual optimization model | `src/annual_design_model_v7_2.py` |
| Rainflow ex-post validation | `src/rainflow_validation_v7_2.py` |
| Data | `data/raw/`, `data/interim/`, `data/processed/` (accepted annual planning input, valid outage starts), `data/reference/` (tariffs, parameter registry, economic interface — machine-readable production parameters) |
| Results / audits | `results/` (subdirectories per script family: `data_audit`, `parameter_audit`, `model_audit`, `billing_audit`, `degradation_validation`, `eob_benchmark*`, `eob_production` (v7.2 historical), `eob_production_v7_3`, `sensitivity`, `layer_a`, `anchors`, `provenance`) |
| Frozen checkpoints / production authority manifests | `docs/checkpoints/` |
| Cross-agent / audit protocol | `docs/protocols/iris_thesis_rigorous_audit_skill.md` |
| Tests | `tests/` |

Do not invent completed results in this document or in `CURRENT_STATE.md`. If a claim cannot be traced
to a script, checkpoint, or audit artifact, mark it explicitly as not yet demonstrated.
