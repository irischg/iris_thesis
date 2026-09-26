# Framework v7.4 zero-winter-role / PV-routing / κ-claim-boundary successor — candidate checkpoint

**Date:** 2026-09-26
**Disposition:** **FRAMEWORK V7.4 ZERO-WINTER-ROLE / PV-ROUTING / κ-CLAIM-BOUNDARY SUCCESSOR — CANDIDATE PASS**
**Acceptance boundary:** candidate only. This checkpoint does **not** accept, promote, or canonize Framework v7.4. It does not create or accept a Registry successor, a Layer A robustness/preregistration checkpoint, a canonical input, a production routing authority, or any production result. **A fresh independent read-only Framework audit is required before any Registry successor work may begin.**

## 1. Scope and governing protocol

This was a **documentation / methodology-governance** pass only, executed under
`docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md`
(SHA-256 `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696`).

Authorized mutations were limited to the three additive Task-1 artifacts:

1. the Framework v7.4 successor candidate `docs/research_framework_v7_4_2026-09-26.md`;
2. this additive candidate checkpoint;
3. the additive candidate provenance package under
   `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/`.

No source code, test, Registry, canonical input, parameter artifact, production runner, production
result, historical checkpoint, audit, freeze, or any other accepted artifact was created or edited.
No `optimize()` call, MILP solve, model construction, EOB rerun, core-three rerun, Full81 run,
sensitivity solve, data regeneration, or solver-setting change occurred.

## 2. Predecessor and candidate identity

| Artifact | Role | SHA-256 |
|---|---|---|
| `docs/research_framework_v7_3_2026-09-23.md` | **Direct predecessor**; `CLOSED / ACCEPTED`; current methodology authority; **immutable**, verified unchanged before and after authoring | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `docs/research_framework_v7_4_2026-09-26.md` | Additive successor **candidate** | `52459a06a6c527413c74bd5d740992975284b1d41216168aad5869c585da6cda` |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | Current accepted evidence authority; **unchanged context**, not modified | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | Accepted v7.3 methodology/evidence lifecycle closure; **immutable**, not edited | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
| `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | Governing provenance protocol | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
| `docs/research_framework_v7_2_2026-08-24.md` | Historical accepted predecessor of v7.3; historical lineage only | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |

Framework v7.4 byte count: **212,268 bytes**, 4,271 content lines (+ trailing newline).
Framework v7.3 byte count: **181,798 bytes**, 3,956 content lines — **unchanged**.

Registry v7.4 is `NOT_YET_CREATED / NOT_YET_AUTHORIZED`. The Layer A robustness/preregistration
checkpoint is `NOT_YET_CREATED / NOT_YET_AUTHORIZED`. Framework v7.3 and Registry v7.3 R3 remain the
current accepted methodology and evidence authorities until independent acceptance of this candidate.

## 3. Naming / namespace decisions

| Artifact | Chosen path | Convention basis |
|---|---|---|
| Framework successor | `docs/research_framework_v7_4_2026-09-26.md` | Matches `research_framework_v7_3_2026-09-23.md`; a substantive methodology-role successor, therefore `v7_4`, **not** `v7.3_r4` |
| Candidate checkpoint | `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_2026-09-26.md` | Structural precedent `docs/checkpoints/framework_v7_3_reconstructed_pv_mainline_successor_candidate_2026-09-23.md` |
| Provenance package | `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/` | Protocol §22 `results/provenance/<topic>_candidate_rN/`; neighbouring precedent `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/`. **New namespace; no prior candidate directory reused.** |

## 4. Exactly three authorized substantive changes

### CHANGE A — zero-winter role

```text
v7.2 (historical): zero-winter = mainline.
v7.3 (historical): zero-winter = conservative stress/sensitivity.
v7.4 (current)   : zero-winter = historical conservative validation / provenance evidence
                   supporting the reconstructed-PV promotion/adjudication decision.
```

The successor establishes explicitly that zero-winter is **not** a mandatory new Layer A sensitivity,
**not** a mandatory new Layer B sensitivity/stress, and **not** an equal-status alternative planning
baseline; that **no** new zero-winter EOB, Layer A, or Layer B solve is required; that the prior
reconstructed-vs-zero-winter comparison remains valid historical project validation/adjudication
evidence; that zero-winter must remain preserved in provenance/history and must not be silently
deleted; and that it may be revisited only if a separately justified future reason is established.

The current-prescriptive "minimum required" Layer A sensitivity bullet was **removed** from §16.1 and
**not replaced** by another sensitivity — the minimum-required list is net one item shorter. The
prohibition on reverting Layer A/Layer B to a different annual PV identity was preserved and, under
Change B, strengthened.

Historically correct past-scoped statements that zero-winter was mainline (v7.2) or
stress/sensitivity (v7.3) were **retained and explicitly labelled historical**, including the whole of
inherited §35, which is re-scoped as an immutable historical record rather than current prescription.

### CHANGE B — formal observed-vs-planning PV routing

New §4.1.1-R and §36.2 make the epistemic routing explicit and internally consistent:

| Layer | Data identity |
|---|---|
| HISTORICAL EMPIRICAL / CALIBRATION | observed data wherever valid |
| PLANNING / COUNTERFACTUAL MODEL | accepted reconstructed full-year PV, single artifact identity |

Historical empirical layer membership recorded: historical billing-demand calibration; Taipower bill
regression; tariff/institutional validation; historical empirical "what actually occurred" checks.
Historical grid-import calibration remains `Load_obs - PV_obs` for valid observed-PV periods against
the actual billing target.

Planning layer membership recorded: EOB planning optimization; Full81 / Layer A; `R(alpha,beta)`;
`P_out`; binding-outage identification/classification; Layer A outage consistency replay; baseline
Layer B; downstream planning scenarios unless explicitly declared an alternative scenario.

No hybrid routing is authorized: `EOB = reconstructed PV` together with
`Layer A / Layer B = zero-winter or any other annual PV identity` is prohibited. The accepted
reconstructed full-year PV must be described as weather-informed, model-based, separately validated,
best-estimate planning baseline, and must not be described as observed historical PV truth, exact
ground truth, or exact recovery. **No model equation was changed by this clarification.**

### CHANGE C — κ historical-calibration / planning-use claim boundary

New §4.3.1-K and §36.3. Production κ, its estimator, and its calibration-period definition are
preserved exactly:

| Item | Status |
|---|---|
| production κ | **UNCHANGED** — ≈1.01037; production-pinned `1.0103668594376984` |
| estimator | **UNCHANGED** — through-origin least squares |
| calibration period | **UNCHANGED** — 2025/01–2025/10, ten `pv_status=valid` usage months |
| calibration basis | **UNCHANGED** — valid observed periods, observed Load/PV, usage-period-aligned actual billed maxima |
| scripted-reproduction requirement | **UNCHANGED** — future rerun must recompute κ from canonical input + billing registry |

The full-precision value is recorded only to fix the claim boundary against the already-frozen
production identity; it was verified against primary repository bytes
(`scripts/19a_preflight_final_layer_a_81_cases.py` κ-drift guard and the v7.2 final-81 runner-authority
manifests, both `1.0103668594376984`) and does **not** relax the existing §4.3 rule that production must
not merely hard-code a constant.

The successor states explicitly that historical κ calibration answers a historical
billing-representation question, that reconstructed full-year PV answers a planning-baseline question,
that these belong to different epistemic layers and are therefore not inconsistent, that κ is a
billing-demand representation proxy, that κ is not a reconstruction of 15-minute chronology, that κ does
not demonstrate capture of sub-hourly BESS physical power peaks, and that κ does not eliminate the
hourly temporal-resolution limitation. Accepted reconstructed planning PV must not be used to redefine
or re-estimate production κ.

## 5. Change-scope diff audit

Structural line diff v7.3 → v7.4: **40 non-equal hunks**; 57 predecessor lines changed/removed;
372 successor lines added/changed; net +315 lines. Every substantive hunk was classified under
exactly one of the four permitted categories:

- **A** zero-winter role — §4.1.3 heading and routing bullets, §4.1.4 provenance planning-role field,
  §10.3-B Layer B annual-baseline note, §16.1 bullet deletion + non-mandatory note, §22 limitation 7,
  §26 one-pager, §31.3 item 9, §35.1/§35.2 historical re-scoping, §36.1.
- **B** observed-vs-planning PV routing — new §4.1.1-R, §4.1.3 routing bullets, §26 one-pager,
  §35.2 strengthening, §36.2.
- **C** κ claim boundary — new §4.3.1-K, §35.3, §26 one-pager, §36.3.
- **D** version/provenance/status plumbing — title, version lineage, source manifest, supersession
  rule, candidate status, 版本原則, 文獻分流, delta block, §0.3 gate list, §25 governance sequence,
  §35 heading/scope/disposition re-scoping as inherited historical record, new §36.0/§36.4–§36.8.

**No other substantive category is present.** No hunk touches an equation, a parameter, a numerical
setting, a solver setting, or a production result.

## 6. Static validation performed

| Check | Result |
|---|---|
| Accepted Framework v7.3 SHA-256 re-verified before and after authoring | **PASS** — `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` unchanged |
| Accepted Registry v7.3 R3 SHA-256 re-verified | **PASS** — `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` unchanged |
| Authority-freeze SHA-256 re-verified | **PASS** — `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` unchanged |
| Provenance-protocol SHA-256 re-verified | **PASS** — `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` unchanged |
| No existing accepted/historical artifact modified | **PASS** — `git diff --name-only` and `git diff --cached --name-only` both empty |
| Display-math / equation block audit | **PASS** — 152 v7.3 blocks, **0 removed, 0 altered**; 154 in v7.4; the 2 additions are restatements of the existing `P_t^{grid,hist}=L_t^{obs}-PV_t^{obs}` definition. `\boxed{}` count identical at 50 |
| Frozen numerical/model setting drift | **PASS** — every audited frozen literal (SOC 0.10/0.90, `E^U=0.8E^N`, `eta_c=eta_d=0.90`, 9×9=81, T=8760, 1,463, CRF 0.0802426, r=5%, n=20, FX 31.150, κ 1.01037, 10 MW / 1 MW, 4/6/8/10 h, May 16–October 15, α/β robustness points, γ_PV set, λ_L set, PNNL DOD–cycle-life points, 243, NTD-2023) shows **zero count decreases and zero value changes**; all deltas are additive restatements in the §36.4 frozen inventory and §4.3.1-K |
| Stale current-prescriptive zero-winter mandate scan | **PASS** — 57 zero-winter-family lines reviewed individually; no line makes zero-winter a mandatory Layer A sensitivity, a mandatory Layer B stress, or an equal-status planning baseline; every surviving stress/sensitivity phrasing is explicitly past-scoped to v7.2/v7.3 or is a cross-document note about immutable predecessor bytes |
| Forbidden-claim scan (reconstructed PV as observed truth; κ re-estimated from planning PV; κ as 15-min chronology; EOB/core-three self-certification; self-accepted status) | **PASS** — zero asserted instances; all regex hits are negations, prohibitions, or explicit disclaimers |
| No code / data / model / parameter file changed | **PASS** — `git status --porcelain` over `src scripts tests data results *.py` empty |
| `git diff --check` whitespace/conflict check | **PASS** — clean |
| optimization calls | **0** (expected 0) |

Not performed, by design: any solve, model construction, optimizer call, data regeneration, Registry
creation, preregistration-checkpoint creation, production-authority re-freeze, tag creation, or tag
retargeting. No solve was used as a validation step.

## 7. Preserved CLOSED decisions

Diff review and literal-count audit confirm no change to: research questions; research positioning;
Layer A / Layer B / DG boundaries; alpha and beta grids; the Layer A 9 × 9 = 81 case universe;
valid-start non-circular semantics; stationary LFP; SOCmin = 0.10; SOCmax = 0.90; usable-energy
semantics; eta_c = eta_d = 0.90; AC/PCS-side charge/discharge power; battery-side stored-energy state;
A1–A4; B1–B2; Gate 1; Gate 2; the constant worst-case mainline reserve floor; outage initial-state
semantics; the outage technical lower bound; outage replay semantics; reserve equations; Layer A
analytical equations; annual regular contract capacity; supplementary-contract treatment; Taipower
tariff and billing-period semantics; over-contract 2×/3× semantics; non-duplication treatment; the κ
estimator and production value; the degradation formulation; Xu-adapted intertemporal PWL semantics;
the rainflow role; the B2 cost-accounting structure; PNNL 10 MW-scale full package as mainline and
1 MW-scale full package as cost sensitivity; full-package cost switching rules; the constant NTD-2023
optimization monetary basis; the real 5% discount-rate modeling assumption; the 20-year financial
horizon; CRF treatment; `surplus_pv_recharge=False` for the accepted Layer A consistency replay;
accepted EOB and core-three numerical results; production code; solver settings; solver fingerprint;
and production inputs/data.

No new equation, no equation rewrite, no parameter change, no new numerical sensitivity design.

## 8. Scientific / model-audit guardrails

New §36.5 records the guardrails this successor asserts against: data leakage; look-ahead bias;
retrospective/operational information confusion; information advantage; unfair baseline comparison;
observed-vs-reconstructed conflation; historical-vs-planning epistemic conflation; billing-proxy vs
physical-power semantics; unit/scale drift; implementation-vs-methodology drift; and silent
model-equation drift.

The successor states explicitly that reconstructed planning PV is a retrospective planning-baseline
construction and **not** online forecast information; that historical κ calibration is **not** a
planning-PV calibration; and that solver success does **not** prove methodological validity.

## 9. EOB / core-three status boundary

This authoring pass changes methodology and document role definitions only.

- No EOB rerun and no core-three rerun is authorized by this authoring pass.
- Continuing EOB/core-three validity **must be decided by the required independent
  Framework-successor downstream-impact audit**.
- This checkpoint deliberately does **not** state that EOB or core-three definitely remain valid;
  that verdict belongs to the independent audit.
- A Framework version change does not by itself constitute grounds for a rerun.
- Live implementation/production status remains governed by `docs/ai_handoff/CURRENT_STATE.md` and live
  repository evidence, not by Framework prose.

## 10. Repository state

### Pre-authoring

- branch: `thesis-v7`;
- `HEAD`: `1651b31008c565e105fc79a958f9ca98a194aa80`;
- `origin/thesis-v7`: `1651b31008c565e105fc79a958f9ca98a194aa80` (in sync);
- staged paths: 0;
- unstaged tracked paths: 0;
- untracked paths: 8 pre-existing, unrelated to this task
  (`0629開會逐字稿Iris.docx`; `Claude outputs/0930_進度報告_投影片架構與逐頁講稿_v7.2.md`;
  `Claude outputs/P2_Literature_Positioning_v7.2.pptx`;
  `Claude outputs/iris_thesis_independent_audit_2026-09-13.md`;
  `Claude outputs/iris_thesis_repo_audit_2026-09-13.md`;
  `EOB_Attempt3_20260924T184038809594Z_59116b1556.zip`;
  `docs/CATOCKERTEAIPOTEP rctㄐㄚPV  I.html`;
  `docs/ESGC Cost Performance Report 2022 PNNL-33283.pdf`).

### After authorized mutations

- branch unchanged; staged/unstaged tracked paths remain 0 until the authorized Task-1 commit;
- the 8 pre-existing untracked paths were preserved byte-identically and not touched, stashed, reset,
  cleaned, or committed;
- added additive Task-1 paths only:
  - `docs/research_framework_v7_4_2026-09-26.md`;
  - `docs/checkpoints/framework_v7_4_zero_winter_role_pv_routing_successor_candidate_2026-09-26.md`;
  - `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/completion_manifest.json`;
  - `results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/package_manifest.json`.

Exact porcelain snapshots, byte counts, and the commit identity are recorded in
`results/provenance/framework_v7_4_zero_winter_role_pv_routing_candidate_r1/completion_manifest.json`.
`package_manifest.json` deliberately omits its own digest (a manifest cannot contain its own hash);
its external SHA-256 is reported with the pass report.

## 11. Governance status and next gate

| Item | State |
|---|---|
| Framework v7.4 status | **CANDIDATE ONLY** |
| Self-acceptance performed | **NO** |
| Independent audit required | **YES** |
| Registry successor created | **NO** |
| Layer A robustness/preregistration checkpoint created | **NO** |
| Methodology promotion performed | **NO** |
| Production-authority re-freeze performed | **NO** |
| Acceptance/freeze artifact created | **NO** |
| Tag created or retargeted | **NO** |
| Model constructions / `optimize()` calls / MILP solves | **0 / 0 / 0** |
| EOB reruns / core-three reruns / Full81 runs / sensitivity solves | **0 / 0 / 0 / 0** |

The required governance sequence from here is: **independent Framework audit → Framework accepted →
Registry successor → independent Registry audit → Registry accepted → Layer A
robustness/preregistration checkpoint → independent checkpoint audit → final cross-document alignment
audit → production-authority re-freeze if required → Full81.**

> **FRAMEWORK V7.4 ZERO-WINTER-ROLE / PV-ROUTING / κ-CLAIM-BOUNDARY SUCCESSOR — CANDIDATE PASS**

Framework v7.4 candidate authoring is complete, but it is **NOT** the accepted methodology authority. A
fresh independent read-only Framework audit is required before any Registry successor work may begin.
