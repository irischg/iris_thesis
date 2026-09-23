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
  -> Script 06: historical v7.2 integrated annual input (v7.3 canonical successor pending Step 2D)
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
  -> EOB production baseline (results/eob_production/*)
  -> Scripts 16a–18b: representative-case preflight, winter-PV long-block sensitivity
     protocol (17a–17c), production-environment/checkpoint validation
  -> Scripts 19a/19b: final-81 preflight and Layer A production runner
  -> Layer A: dense 9x9 alpha/beta grid, annual design optimization + outage replay
  -> Layer B: fixed-design benchmark scenarios (3, 5, or 9 designs, selected after Layer A)
  -> DG extension: hypothetical diesel-backup cost/emission comparison
```

**Do not infer that a stage is complete because its script exists.** This pipeline map describes what
each stage *does*, not whether it has currently run or passed. Current completion/pass/pending status
is controlled only by `docs/ai_handoff/CURRENT_STATE.md` and the latest applicable checkpoint/audit —
consult it before making any claim about what has actually been executed or accepted.

### v7.3 reconstructed-PV methodology note

The accepted v7.3 methodology uses reconstructed full-year PV, including the prolonged winter
unavailable block, as the best-estimate planning mainline. The prior zero-winter treatment is retained
as a conservative stress/sensitivity. Reconstructed values are model-based, weather-informed estimates,
not observed truth or exact recovery. EOB/economic optimization, Layer A \(R\), \(P^{out}\), binding
classification and outage replay, and baseline Layer B must all use the same future canonical
reconstructed-mainline artifact. That canonical artifact has not yet been created or authorized, and
production routing has not yet been authorized.

## 4. Layer A / Layer B / DG — conceptual roles

- **Layer A**: the core annual design optimization. For each \((\alpha, \beta)\) cell in a dense
  9×9 grid, optimize BESS energy/power sizing, contract capacity, and annual dispatch, subject to a
  worst-case reserve constraint sized against *every* valid historical outage start in the case year,
  then replay the outage. Annual normal-operation optimization and outage replay are two separate
  model stages (A2, CLOSED) — not a single joint dispatch.
- **Layer B**: takes Layer A's *finished* design(s) — it does not re-optimize equipment — and runs
  structured, non-probabilistic scenarios against them. Layer B scenario coverage is explicitly not
  claimed to be a reliability probability.
- **DG (diesel generator) extension**: a hypothetical, exogenous coverage extension, reported on cost,
  fuel, and onsite CO₂ together — not collapsed into a single objective via an assumed carbon price.
  Existing campus emergency DG is out of scope for the aggregate mainline optimization.

## 5. Authority hierarchy (read this before trusting any number or rule)

1. **`docs/research_framework_v7_3_2026-09-23.md`** — current methodology source of truth.
2. **`docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`** — current evidence source of
   truth (literature-vs-project-vs-implementation-choice mapping).
3. **`docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md`** — current methodology/evidence
   lifecycle closure.
4. **Current repository working tree + latest accepted applicable implementation checkpoint/audit** — current implementation
   state. Exact numeric values (parameters, hashes, cost coefficients) live in machine-readable
   artifacts (`data/reference/*.json`/`*.csv`, `results/parameter_audit/*`), not hard-coded in the
   framework text.

Framework v7.2 and Registry v7.2 are historical accepted predecessors only. Registry v7.3 R1 and R2
are failed immutable provenance only. Earlier framework/registry versions and failed candidates are
**provenance / regression / historical lineage only** unless the current accepted v7.3 authorities
explicitly assign another role. They may explain lineage or support a labeled regression comparison,
never act as current methodology/evidence authority.

## 6. Methodology vs. implementation status — keep these separate

- **Methodology CLOSED** means the *research rule* is settled (e.g., "efficiency is applied once,
  AC/PCS-side, η=0.90") and may not be revisited without a demonstrated code/data/source-transcription
  error.
- **Implementation status** (built / audited / CLOSED-PASS / pending / not started) describes whether
  the code *correctly encodes* that already-settled rule, and whether it has produced accepted
  evidence. A script existing, or even solving successfully, is implementation progress — it is not by
  itself a reopening or a re-validation of methodology, and it is not by itself proof of research
  readiness. See `docs/protocols/iris_thesis_rigorous_audit_skill.md` §5–6 for the full discipline.

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

## 8. Provenance rule for legacy artifacts

Historical frozen artifacts (older EOB runs, predecessor checkpoints, `scripts_archive/`, superseded
framework/registry versions) must remain untouched and are never used as evidence for the *current*
formulation. Do not "fix" a provenance/hash guard to make an old script or artifact match new code —
a guard rejecting something is a signal to investigate, not an obstacle.

## 9. Where things live

| What | Where |
|---|---|
| Current methodology source of truth | `docs/research_framework_v7_3_2026-09-23.md` |
| Current evidence source of truth | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` |
| Current methodology/evidence lifecycle closure | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` |
| Historical accepted predecessors | `docs/research_framework_v7_2_2026-08-24.md`, `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` |
| Failed immutable Registry candidates | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` (R1), `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` (R2) |
| Earlier historical framework/registry lineage | `docs/research_framework_v7_2026-08-14.md`, `docs/research_framework_v7_1_2026-08-16.md`, `docs/thesis_literature_evidence_registry_v7_2026-08-14.md`, `docs/thesis_literature_evidence_registry_v7_1_2026-08-16.md` |
| Numbered pipeline scripts | `scripts/` (active), `scripts_archive/` (superseded, do not use as production input) |
| Core annual optimization model | `src/annual_design_model_v7_2.py` |
| Rainflow ex-post validation | `src/rainflow_validation_v7_2.py` |
| Data | `data/raw/`, `data/interim/`, `data/processed/` (canonical annual input, valid outage starts), `data/reference/` (tariffs, parameter registry, economic interface — machine-readable production parameters) |
| Results / audits | `results/` (subdirectories per script family: `data_audit`, `parameter_audit`, `model_audit`, `billing_audit`, `degradation_validation`, `eob_benchmark*`, `eob_production`, `sensitivity`, `layer_a`, `anchors`) |
| Frozen checkpoints / production authority manifests | `docs/checkpoints/` |
| Cross-agent / audit protocol | `docs/protocols/iris_thesis_rigorous_audit_skill.md` |
| Tests | `tests/` |

Do not invent completed results in this document or in `CURRENT_STATE.md`. If a claim cannot be traced
to a script, checkpoint, or audit artifact, mark it explicitly as not yet demonstrated.
