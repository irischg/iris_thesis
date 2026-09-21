# Pre-Corrected-Rerun Version Lineage — v7.2

**Baseline date:** 2026-09-15 (Asia/Taipei)
**Branch:** `thesis-v7`
**HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`
**Authority classification of the current working tree:** `CURRENT_IMPLEMENTATION_PENDING_PRODUCTION`

> This document is an **additive** provenance record. It rewrites nothing. It freezes a durable
> BEFORE-state so that the corrected production rerun can later be compared, line by line, against
> the production that preceded it.
>
> **The current working tree is NOT final corrected production authority.** No corrected EOB has
> been run. No corrected Layer A has been run. No corrected 81-case surface exists.

---

## 1. What the previous accepted production version was

The last accepted production state is the **final-81 Layer A run**:

| Item | Value |
|---|---|
| Run directory | `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da` |
| Cases | 81 |
| Run manifest SHA-256 | `d38627eabb08d9d286e1bdfcc78bfacb392b75e14477c924a2c88896bbb7428a` |
| Surface summary SHA-256 | `611bc69891bb313cbf57161c01c8c10c3c37bfdb240d0689c09b09d2151349c8` |
| Production tag | `v7.2-final81-runner-ready-r3` |
| Authority manifest | `v7.2-final81-runner-authority-2` |
| Runner | `scripts/19b_run_final_layer_a_81_cases.py` v`…-2026-09-11-r3`, SHA-256 `4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe` |
| Frozen base tag | `v7.2-pre81-ready` (object `2aeccf58…`, peeled `b2acdf28cf1459aee5da44e4407c225f5d3c68a6`) |
| Core model SHA-256 at that production | `d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0` |
| Core version string | `v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9` |

Its economic denominator is the **historical production EOB**:

| Item | Value |
|---|---|
| Artifact | `results/eob_production/eob_production_result_v7_2.json` |
| Core version that solved it | `v7.2-annual-design-core-transition-rate-audit-2026-08-29-r1` |
| Objective | 66,738,326.341512024 NTD-2023/yr |
| E_N | 86.11111111111111 kWh |
| P_B | 62.0 kW-AC |
| CC (regular) | 4,399.137305991739 kW |
| Degradation | 16,168.568637706101 NTD-2023/yr |

**Lineage note worth recording:** the EOB was solved under core `…2026-08-29-r1`, an *earlier* core
than the `…2026-09-06-r9` used for the final-81 run. This is the pre-existing project finding W-03
and is unchanged by this baseline.

---

## 2. Why it remains historical provenance but is no longer sufficient as current authority

The final-81 production was **legitimately accepted at the time it was produced**. Nothing about it
was fraudulent or careless, and it is not being withdrawn as a record.

It is nevertheless **no longer sufficient as current corrected thesis authority**, because four
defects have since been confirmed against it with reproducible evidence:

1. **W-04** — a confirmed *input* defect: `2025-02-01` was classified as an ordinary Saturday
   instead of an all-day off-peak day. Confirmed against the official 114年時間電價日曆表 (114/8/26 修).
2. **W-07** — a confirmed *implementation* defect: the over-contract 2× allowance was pooled
   cumulatively across TOU periods, so earlier-period exceedance consumed a later period's own
   allowance.
3. **Surface-1** — a confirmed *solver-formulation* defect: the cumulative running maximum `z` was
   only an epigraph, which under the corrected per-increment allowance became economically
   exploitable.
4. **Exact-D** — the same looseness one level upstream: the tariff-cost-facing demand auxiliary `D`
   was also only an epigraph, and inflating it reproduced the exploit exactly.

These two dimensions must be kept separate: *historical acceptance status* (accepted) and *current
validity status* (superseded for current authority).

---

## 3. What has changed since that production

Seven gates have run since. All are additive; none rewrote a historical artifact.

| Gate | Verdict | Agent | Accepted (Asia/Taipei) |
|---|---|---|---|
| Gate A — W-04 + W-18 | PASS | Codex | 2026-09-14T22:48:01+0800 |
| Gate B before-snapshot | baseline | Codex | 2026-09-15T14:37:43+0800 |
| Gate B — W-07 | PASS | Claude Code | 2026-09-15T14:57:09+0800 |
| Gate C — dependency refresh | PASS | Claude Code | 2026-09-15T15:40:29+0800 |
| Pre-EOB solver integration | **STOP** | Claude Code | 2026-09-15T15:53:17+0800 |
| Surface-1 repair | **STOP** | Claude Code | 2026-09-15T16:27:28+0800 |
| Exact-D closure | PASS | Claude Code | 2026-09-15T17:00:22+0800 |

The two STOP gates are **not failures of process** — they are the record of the defect being found
and then only partially closed, and they are preserved as separate lineage nodes rather than being
collapsed into the final PASS.

---

## 4. Which changes were input corrections

**W-04 only.**

| Item | Before | After |
|---|---|---|
| `2025-02-01` day type | `saturday` | `offpeak_day` |
| `2025-01-27` day type | `weekday` | `weekday` (unchanged; primary-source confirmed) |
| Day counts (weekday / saturday / offpeak_day) | 251 / 50 / 64 | **251 / 49 / 65** |
| `sat_half` hours | 750 | **735** (−15) |
| `off` hours | 4,245 | **4,260** (+15) |
| `peak`, `half` hours | unchanged | unchanged |

Explicitly **preserved**: timestamps, observed and baseline load, observed and available PV, season,
billing usage-period membership, and load/PV reconstruction provenance.

**The affected tariff-calendar date (2025-02-01) and the date the code was modified (2026-09-14) are
different things and are recorded in separate fields throughout the ledger.**

---

## 5. Which changes were solver / model implementation corrections

**W-07, Surface-1 and Exact-D** — all three are implementation corrections to make the code compute
the already-frozen equations. The frozen tier equations themselves did not change:

```
r[p]    = max(0, D[p] - C[p])
q[p]    = max(0, r[p] - max_{j<p} r[j])
h[p]    = 0.10 * C[p]
q_2x[p] = min(q[p], h[p])
q_3x[p] = q[p] - q_2x[p]
charge  = rate[p] * (2*q_2x[p] + 3*q_3x[p])
```

The corrected solver chain is now exact end to end:

```
p_grid[t]
  -> D[m,q]  = kappa * max_{t in (m,q)} p_grid[t]      (exact, addGenConstrMax)
  -> raw[p]  = max(0, D[p] - CC)                        (exact)
  -> z[first]= raw[first];  z[p] = max(z[p-1], raw[p])  (exact running max)
  -> delta_z[p] = z[p] - z[p-1]  ==  frozen q[p]
  -> q_2x[p] = min(delta_z[p], 0.10*C[p]);  q_3x[p] = delta_z[p] - q_2x[p]
```

Core model SHA-256 sequence through the repair:

| Stage | SHA-256 | Committed |
|---|---|:---:|
| Historical production core | `d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0` | yes (HEAD) |
| Gate B (W-07 per-increment allowance) | `e87309fedf33280ce747f920acd7a77edc3413f477d5a6011a8b972a080b4f57` | no |
| Surface-1 partial (exact `raw`, exact `z`) | `02abcaa12c1e209c58f851c8197d2ea524029ad54048960797947dc9ec1b37bc` | no |
| **Exact-D closure (current)** | **`f848282a33e3c3d243c4d1819f7d506f5cd460de43493031e54fafb3916e9233`** | **no** |

Observed failure signatures preserved as regression oracles: S1 residual **−96.171980** NTD-2023 and
S2 residual **−112.200643** NTD-2023; solver `D(sat_half)` inflated **246 → 267**.

---

## 6. Which methodology decisions remained unchanged

| Decision | Methodology changed? | Note |
|---|:---:|---|
| **A4** (billing-demand reporting) | **NO** | In-model `D` is still a tariff-cost-facing auxiliary; reported maxima are still recomputed post-solve; wording remains "calibrated hourly proxy for the 15-minute billing demand" |
| W-04 calendar | **NO** | Input corrected; calendar semantics unchanged |
| W-18 | **NO** | Additive validation only |
| W-07 tier definition | **NO** | Frozen equations preserved; implementation corrected |
| Surface-1 | **NO** | Solver encoding corrected |
| Exact-D | **NO** | Implementation made exact; A4 compatible |
| κ estimator / boundary / window | **NO** | through-origin LS, observed load − observed PV, 2025-01…2025-10 |
| Tariff source | **NO** | 13b NO ACTION |
| CC semantics | **NO** | One annual endogenous continuous CC; supplementary = 0 |
| PNNL package roles | **NO** | 10 MW mainline, 1 MW sensitivity |
| Degradation (B1) | **NO** | PNNL Table 4.2 + Xu-adapted PWL |
| Reserve / replay / rainflow | **NO** | Constant worst-case reserve; rainflow ex-post only |

**Narrowly reopened, by explicit governance ruling:** the *reduced-native-MAX / floating-demand
tractability implementation* — and only because a demonstrated solver-correctness defect invalidated
the assumption that a floating demand epigraph was harmless.

---

## 7. Which artifacts were regenerated but numerically unchanged

| Artifact | Result |
|---|---|
| Script 08 kappa pairs + audit | **bit-identical**; κ = 1.0103668594376984, absolute difference **0.0** |
| Script 13c (4 outputs) | **bit-identical**; all four residual classes 0.000000 NTD |
| 14a production economic interface | **bit-identical** (`9277d310…`) |
| 14a parameter registry, CPI registry, optimization tariff | regenerated, values unchanged |

κ is invariant by construction: `B_m` is the maximum over the four TOU billed maxima and `H_m` the
monthly maximum of observed grid demand — both are maxima over hour *sets*, which TOU relabelling
re-partitions but does not change.

13c is bit-identical because across all 12 NTUST bills exactly **one** period-row has positive
over-contract exceedance (2025-09 `half`, 16 kW → 5,340.8 NTD), and **zero** months have two or more
exceeding periods. The real data never exercises the W-07 discriminator.

---

## 8. Which artifacts changed only in provenance identity

| Artifact | Change |
|---|---|
| `taipower_transition_period_settlement_interface_v7_2.json` | `896f07e4…` → `f101af47…`. **Only** content delta: pinned annual-input parquet `e0d4a8e8…` (pre-W-04) → `9142b8b6…` (corrected). This was the single **active stale dependency** in the whole chain. |
| `taipower_seasonal_settlement_matrix_v7_2.csv` | `31172c47…` → `ed7f8dbf…`. Exactly two cells: 2025-02 non-summer `sat_half` 60→45 and `off` 327→342 — the W-04 propagation, nothing else. |

---

## 9. Which production outputs remain historical

- `results/eob_production/*` — historical production EOB (immutable)
- `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da` — historical final-81 (immutable)
- `docs/checkpoints/*` — all historical checkpoints and runner-authority manifests (immutable)
- `scripts/15c_…py` `EXPECTED_EOB_REFERENCE` — still the **historical** values; must be re-baselined
  under audit only *after* a corrected EOB exists

---

## 10. Which production outputs are pending corrected rerun

All four are `PENDING_CORRECTED_RERUN`, with reserved ledger slots and **no fabricated values**:

- corrected production EOB
- corrected representative Layer A cases
- corrected final-81 Layer A production
- corrected sensitivities (winter-PV; the planned 6-point reserve-floor A2 gate)

---

## 11. What the current working-tree state means

Three tracked files are modified and uncommitted, plus four untracked new files:

| Path | State | Gate |
|---|---|---|
| `src/annual_design_model_v7_2.py` | modified | Gate B → Surface-1 → Exact-D |
| `scripts/13c_regress_taipower_core_bill_components.py` | modified | Gate B |
| `scripts/06a_build_taipower_tou_calendar.py` | modified | Gate A |
| `scripts/06b_validate_hourly_to_bill_v7_2.py` | untracked (new) | Gate A |
| `tests/test_w18_hourly_to_bill_v7_2.py` | untracked (new) | Gate A |
| `tests/test_w07_overcontract_tier_allocation.py` | untracked (new) | Gate B |
| `tests/test_w07_surface1_solver_integration_v7_2.py` | untracked (new) | Exact-D |

Because `data/` and `results/` are gitignored, the corrected canonical inputs and every gate artifact
carry **no Git history at all**. Their lineage is established by checkpoint manifests, gate manifests
and recorded SHA-256 values — which is why this baseline exists.

**Version/hash divergence:** `CORE_VERSION` still reads
`v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9` while the core
source hash is `f848282a…`. Classification: **`SOURCE_CHANGED_VERSION_PENDING_ALIGNMENT`** —
the implementation is newer than the formal authority string. This is an
`AUTHORITY_ALIGNMENT_PENDING` condition, **not** a model defect.

---

## 12. What still has to happen before final corrected production authority exists

1. **Core authority alignment** — bump `CORE_VERSION` coherently with its six strict exact-string
   pins: `scripts/15b`, `scripts/16a`, `scripts/17b`, `scripts/17c`, `scripts/19a`, and the
   cross-check in `tests/test_transition_candidate1_static_v7_2.py`. The seven `docs/checkpoints/`
   occurrences are historical provenance and must remain untouched.
   The same pass must update `test_reduced_max_builder_is_class_specific_and_ex_post_safe`, which
   still asserts the superseded `transition_demand_ge_seasonal_max_` construct.
2. **Root-node tractability preflight** — the annual model builds in 3.40 s with 122,915 variables,
   8,764 binaries, 105,335 linear and 17,642 general constraints, but build success is not solve
   tractability. A bounded solve preflight is required.
3. **Corrected EOB**, then re-baseline `EXPECTED_EOB_REFERENCE` under audit.
4. **Representative Layer A**, sensitivities, and the 6-point reserve-floor **A2 decision gate**.
5. **One** corrected 81-case production in a new run directory.
6. **New production authority**: new commit, checkpoint, authority manifest, runner version and a new
   annotated tag. Historical tags are never retargeted.

---

## Appendix A — Parameter register (previous production vs current)

Every production-controlling parameter, whether or not it changed. Values verified from current
source and artifacts, not copied from expectation.

| Parameter | Previous production | Current | Changed? | Source of truth |
|---|---|---|:---:|---|
| SOC_MIN | 0.10 | 0.10 | NO | `src/annual_design_model_v7_2.py:85` |
| SOC_MAX | 0.90 | 0.90 | NO | `:86` |
| eta_c | 0.90 | 0.90 | NO | `:87` |
| eta_d | 0.90 | 0.90 | NO | `:88` |
| Layer A alpha grid | 0.60–1.00 step 0.05 | same | NO | `19a:46` |
| Layer A beta grid | 4–12 h step 1 | same | NO | `19a:47` |
| Layer A case count | 81 | 81 | NO | `19a` |
| Regular CC semantics | one annual endogenous continuous variable | same | NO | core docstring |
| Supplementary CC | 0 | 0 | NO | `13c cumulative_contract_thresholds` |
| Summer boundary | 2025-05-16 … 2025-10-15 | same | NO | canonical input |
| TOU periods | peak, half, sat_half, off | same | NO | `:96` |
| Non-summer peak | N/A (not zero-rate) | same | NO | registry `energy_non_summer_peak = NaN` |
| κ estimator | through-origin least squares | same | NO | 14a interface |
| **κ value** | 1.0103668594376984 | **1.0103668594376984** | **NO (bitwise)** | Script 08 rerun, Gate C |
| κ calibration window | 2025-01 … 2025-10 | same | NO | kappa pairs (10 rows) |
| κ boundary quantity | observed load − observed PV | same | NO | Framework v7.2 |
| Over-contract tier-1 multiplier | 2.0 | 2.0 | NO | tariff registry |
| Over-contract tier-2 multiplier | 3.0 | 3.0 | NO | tariff registry |
| Tier threshold fraction | 0.10 | 0.10 (continuous) | NO | tariff registry |
| Non-duplication semantics | required | required | NO | 詳細電價表 §七(一)2.(5) |
| **Tier allocation implementation** | cumulative monthly pool | **per-increment allowance** | **YES (implementation)** | Gate B |
| PNNL mainline package | `pnnl_v2024_lfp_2023_point_10mw_4to10h` | same | NO | 14a interface |
| PNNL sensitivity package | `pnnl_v2024_lfp_2023_point_1mw_4to10h` | same | NO | 14a interface |
| FX | 31.150 NTD/USD | same | NO | 14a interface |
| Monetary base year | constant NTD-2023 | same | NO | 14a interface |
| Discount rate | 0.05 real | 0.05 | NO | 14a interface |
| Analysis horizon | 20 yr | 20 | NO | 14a interface |
| CRF | 0.08024258719069129 | same | NO | 14a interface |
| Degradation technical calibration | (0.05,192000) … (0.80,4800) | same | NO | PNNL Table 4.2 (W-15 CLOSED) |
| Effective PWL breakpoints | (0, 0.30, 0.60, 0.80) | same | NO | `:89` |
| C_rep | 5,952.064124999999 NTD/kWh | same | NO | 14a interface |
| Reserve-floor semantics | constant worst-case | same | NO | core; A2 gate pending |
| Outage replay | grid = 0, PV surplus curtailed | same | NO | core |
| Rainflow role | ex-post validation only | same | NO | Framework v7.2 |
| Calendar aging | sensitivity candidate, not blocker | same | NO | W-05 |
| **Billing-demand auxiliary `D`** | one-sided epigraph | **exact period maximum** | **YES (implementation)** | Exact-D gate |

---

## Appendix B — Backward traceability chains (§32)

Legend: `→` reads "has parent". `EVA` = `EARLIEST_VERIFIABLE_ANCESTOR`.

1. **Canonical annual input** — current `6ab78508…`(CSV)/`9142b8b6…`(PQ) → Gate A correction
   (2026-09-14) → production `d381217c…`/`e0d4a8e8…` → **EVA** pinned in
   `production_checkpoint_manifest_v7_2_2026-09-09`. No Git history (`data/` ignored).
2. **TOU calendar** — current `e6053311…` → Gate A → production `5d5a6d7f…` → **EVA** same checkpoint;
   generator `06a` root commit `2a380ab` (2026-08-17).
3. **Core model** — current `f848282a…` → `02abcaa1…` → `e87309fe…` → production `d145eeb0…` →
   root commit `ae31d13` (2026-08-30). **ORIGINAL_VERIFIED.**
4. **Over-contract implementation** — lives inside items 3 and 5; corrected at Gate B.
5. **13c billing regression** — current `125ae8c1…` → Gate B → production `eb3c0e4e…` → root commit
   `410e12e` (2026-08-24). **ORIGINAL_VERIFIED.**
6. **κ / Script 08** — source unchanged `6014a24b…`, root commit `81a8e77` (2026-08-17);
   output pairs `c8e32a27…` bit-identical across the Gate C rerun. **ORIGINAL_VERIFIED.**
7. **14a economic interface** — source root `d02a54a` (2026-08-26); artifact `9277d310…` unchanged.
8. **14b settlement interface** — source root `bb7a786` (2026-08-26); artifact `896f07e4…` →
   `f101af47…` at Gate C.
9. **Historical EOB** — `v7.2-post15c-eob` freeze (2026-08-30), core `…2026-08-29-r1`. **EVA.**
10. **Final-81 authority** — run `20260911T112258206802Z_4d0eb9e1da` → authority manifest
    `v7.2-final81-runner-authority-2` → frozen base `v7.2-pre81-ready` (peeled `b2acdf28…`) →
    repository root commit `cc50a1d` (2026-04-20). **ORIGINAL_VERIFIED.**

No link in any chain is silently broken. Where Git cannot reach (everything under `data/` and
`results/`), the chain is explicitly marked `EARLIEST_VERIFIABLE_ANCESTOR` rather than guessed.

---

## Appendix C — Cross-agent execution history

| Stage | Agent |
|---|---|
| Gate A (W-04 + W-18), Gate B before-snapshot | Codex |
| Gate B (W-07), Gate C, Pre-EOB integration, Surface-1 repair, Exact-D closure | Claude Code |

**This is provenance metadata only. It is not an authority hierarchy.** Neither agent's output is
privileged. Technical authority derives from repository state, SHA-256 identities, deterministic
tests, solver-integration results, accepted gate manifests and checkpoint records. Where any agent
report were to conflict with reproducible repository evidence, **the repository evidence wins** and
the discrepancy is recorded rather than quietly reconciled.

No such conflict was found at this baseline: all six externally supplied hashes were verified against
the live tree and matched.
