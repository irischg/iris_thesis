# Pre-Corrected-Rerun Version Lineage — v7.2 (Gate-4 Frozen Baseline)

**Freeze date:** 2026-09-16 (Asia/Taipei) · **Baseline date:** 2026-09-15
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`
**Authority classification of the current working tree:** `CURRENT_IMPLEMENTATION_PENDING_PRODUCTION`

> **What this document is.** An additive provenance record produced by Gate 4 of the Pre-Rerun Baseline
> protocol, consolidating the independently accepted Gate 1 (evidence discovery), Gate 2 (lineage
> reconstruction) and Gate 3 (baseline registers). It rewrites nothing and freezes a durable BEFORE-state
> so the corrected production rerun can later be compared line by line against the production preceding it.
>
> **What this document is not.** It is **not** corrected production authority. No corrected EOB has been
> run. No corrected Layer A has been run. No corrected 81-case surface exists.
>
> **Relationship to the 2026-09-15 file.** A similarly named untracked artifact,
> `pre_corrected_rerun_version_lineage_v7_2_2026-09-15.md`, already exists. It is classified
> `PRIOR_UNACCEPTED_ADDITIVE_ARTIFACT`, was **not** edited or overwritten, and controlled **zero** fields
> in Gates 2–4. This file sits alongside it. Where the two differ, see §17.

---

## 1. What the previous accepted production was

| Item | Value |
|---|---|
| HEAD | `b03721275c73b05d45517bdf84c1e0bd03833376` |
| Production tag | `v7.2-final81-runner-ready-r3` (peels exactly to HEAD) |
| Authority manifest | `v7.2-final81-runner-authority-2`, SHA-256 `4af8a90a…` |
| Runner | `scripts/19b_…py` v`…-2026-09-11-r3`, SHA-256 `4abbda9d…` |
| Final-81 run | `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da` |
| Run manifest / surface summary | `d38627ea…` / `611bc698…` |
| Completion | `COMPLETE_PASS`, 81 cases, `optimization_calls: 81` |
| Core at final-81 | `d145eeb0…`, `CORE_VERSION` `…reduced-native-max-2026-09-06-r9` |
| Canonical input | CSV `d381217c…`, Parquet `e0d4a8e8…` |
| TOU calendar | `5d5a6d7f…` |

Its economic denominator is the **historical production EOB**
(`results/eob_production/eob_production_result_v7_2.json`, `ad606a50…`): objective
**66 738 326.341512024 NTD-2023/yr**, E_N 86.11111111111111 kWh, P_B 62.0 kW-AC,
CC 4 399.137305991739 kW, degradation 16 168.568637706101 — `OPTIMAL`, `mip_gap 0.0`, 12/12 gates PASS.

**W-03 preserved:** the EOB was solved under core `…2026-08-29-r1` (`448235d3…`), an *earlier* core than
the `r9` used for the final-81 run. Gate 4 neither resolves nor reopens this.

---

## 2. Why it remains immutable historical provenance

The final-81 production was **legitimately accepted when it was produced**. Nothing about it was
fraudulent or careless. It is not withdrawn, and it is **not retrospectively invalid**.

All of its artifacts were re-hashed at Gates 1, 2, 3 and 4 and are **unchanged**. They are classified
`HISTORICAL_IMMUTABLE_PROVENANCE` and must never be edited, regenerated in place, or deleted.

---

## 3. Why it is nevertheless insufficient as current corrected authority

Four defects have since been confirmed against it with reproducible evidence:

1. **W-04** — an *input* defect: `2025-02-01` classified as an ordinary Saturday instead of an all-day
   off-peak day, against the official 114年時間電價日曆表 (114/8/26 修).
2. **W-07** — an *implementation* defect: the over-contract 2× allowance was pooled cumulatively across
   TOU periods, so an earlier period's exceedance consumed a later period's own allowance.
3. **Surface-1** — a *solver-formulation* defect: the cumulative running maximum `z` was only an
   epigraph, which under the corrected per-increment allowance became economically exploitable.
4. **Exact-D** — the same looseness one level upstream: the tariff-cost-facing demand auxiliary `D` was
   also only an epigraph, and inflating it reproduced the exploit exactly.

Two dimensions are kept separate throughout: *historical acceptance status* (accepted) and *current
validity status* (superseded for current authority).

---

## 4. Current corrected implementation identity

| Item | Value |
|---|---|
| Core source | `src/annual_design_model_v7_2.py`, SHA-256 **`f848282a33e3c3d243c4d1819f7d506f5cd460de43493031e54fafb3916e9233`** |
| `CORE_VERSION` | `…reduced-native-max-2026-09-06-r9` — **unchanged** |
| Authority relationship | `SOURCE_CHANGED_VERSION_PENDING_ALIGNMENT` |
| Implementation authority | `CURRENT_IMPLEMENTATION_PENDING_PRODUCTION` |
| Corrected canonical input | CSV `6ab78508…`, Parquet `9142b8b6…` |
| Corrected TOU calendar | `e6053311…` |
| Working tree | dirty — 3 tracked modifications, 8 untracked paths, nothing staged |

**The corrected core has never been solved.** The Exact-D annual audit was **build-only**
(`full_annual_production_optimize_calls = 0`): 122 915 variables, 8 764 binaries, 105 335 linear and
17 642 general constraints, building in 3.40 s. Build success is not solve tractability.

---

## 5. W-04 — input / calendar correction

**Classification: `CONFIRMED_INPUT_DEFECT` + `INPUT_CORRECTION` + `METHODOLOGY_UNCHANGED`.**

| | Before | After |
|---|---|---|
| `2025-02-01` day type | `saturday` | `offpeak_day` ("special holiday overrides Saturday") |
| Hours moved | — | **15 h, `sat_half` → `off`** |
| Annual `sat_half` | 750 | **735** |
| Annual `off` | 4 245 | **4 260** |
| Annual `peak` / `half` | 642 / 3 123 | unchanged |
| Day counts (weekday/sat/offpeak) | 251 / 50 / 64 | **251 / 49 / 65** |
| `2025-01-27` | `weekday` | `weekday` (unchanged, primary-source confirmed) |

All 50 canonical columns were compared exactly; only `tou_day_type` (24 cells) and `tou_period`
(15 cells) changed. Timestamps, observed and baseline load, observed and available PV, season, billing
usage-period membership and reconstruction provenance are explicitly preserved.

**Three dates are kept strictly apart:** affected data date **2025-02-01**, code modification date
**2026-09-14**, Gate A acceptance **2026-09-14T22:48:01+08:00**. Calendar *semantics* did not change —
only one date's classification. The season boundary is unmoved (`05-16`…`10-15`, re-verified against
both the tariff registry and the corrected parquet).

---

## 6. W-18 — validation addition

**Classification: `VALIDATION_GAP_CLOSURE`. Methodology unchanged. No production input changed.**

New artifacts: `scripts/06b_validate_hourly_to_bill_v7_2.py` (`d5a5b3fa…`) and
`tests/test_w18_hourly_to_bill_v7_2.py` (`48f78f3c…`), both untracked and never committed. 14 tests,
0 failures, 0 errors, passing both before and after generation.

**Scope:** 2025 = **HARD** authority; 2024/11–12 = **STRONGLY CORROBORATED / INFORMATIONAL**, with
legacy 113-rule audited calendar notes retained byte-for-byte and explicitly not treated as HARD.

W-04 and W-18 closed in the same gate but are **different logical items** and are deliberately never
merged: one corrected a production input, the other added validation that changed nothing.

---

## 7. W-07 — implementation correction

**Classification: `IMPLEMENTATION_CHANGED_METHODOLOGY_UNCHANGED`.
Reason: `CONFIRMED_MODEL_IMPLEMENTATION_DEFECT`.**

> **This is an implementation-semantics correction, not a numerical modeling-parameter change.**
> `register_entry_changed = YES` · `methodology_changed = NO` · `numeric_parameter_changed = NO` ·
> `implementation_semantics_changed = YES`

The frozen intended equations are **unchanged**:

```
r[p]    = max(0, D[p] - C[p])
q[p]    = max(0, r[p] - max_{j<p} r[j])
h[p]    = 0.10 * C[p]                    (continuous, never rounded)
q_2x[p] = min(q[p], h[p])
q_3x[p] = q[p] - q_2x[p]
charge  = rate[p] * (2*q_2x[p] + 3*q_3x[p])
```

What changed is only that the code now *computes* them. The historical implementation pooled the
allowance cumulatively; the corrected implementation enforces it per increment
(`q_tier1 ≤ delta_z` and `q_tier1 ≤ 0.10·CC`).

**No numeric parameter moved.** The 2× and 3× multipliers, the 0.10 tier fraction and the ordered-period
non-duplication rule were all re-read from the tariff registry at Gate 3 and are **unchanged**. Gate B
proved non-duplication identical to historical over 200 000 random samples, with 0 violations across
four separate proofs.

Four controlling surfaces were modified; `fifth_controlling_surface_found = false`.

---

## 8. Pre-EOB — solver defect discovery (STOP)

**Verdict: `STOP - SURFACE 1 DEFECT FOUND`. Core hash unchanged (`e87309fe`) — a
`SOURCE_UNCHANGED_EVENT_NODE`.**

W-19 (candidate): `z` was constrained only as an epigraph (`z ≥ raw`, `z ≥ z_prev`); nothing forced
`z == max(raw, z_prev)`. Inflating an intermediate `z` split one period's exceedance across two periods
and harvested two 0.10·CC allowances instead of one.

**Failure signature:** S1 with CC=240, raw=3/6/33 → solver `z` `[3, 27, 33]` against expected
`[3, 6, 33]`; residual **−96.171980 NTD-2023** = −3 × 32.057327 (off basic rate). S2 also failed.

**Reachability, not a corner case:** the NTUST school tariff sets `sat_half` and `off` basic rates equal
in **both** seasons (44.7/44.7 summer, 33.3/33.3 non-summer — re-read from the registry at Gate 3), so
the interior-`z` objective coefficient `3·(rate_k − rate_{k+1})` is exactly zero.

**Masking:** the pre-Gate-B cumulative pool globally capped the monthly 2× total, so the W-07 correction
**exposed** a pre-existing under-constraint rather than creating one.

**The defect was caught by the production post-solve guard itself**, not by external review.
`production_source_modifications = 0` — the gate deliberately did not repair what it found.

This stage is preserved as an independent lineage node **despite having no source-hash delta**, and must
never be collapsed by hash de-duplication.

---

## 9. Surface-1 — partial repair (STOP)

**Verdict: `STOP - BLOCKER REMAINS (exploit relocated to the D epigraph)`. Core `e87309fe` → `02abcaa1`.**

`raw = max(0, D − CC)` via `addGenConstrMax`; `z[first] == raw[first]`; `z[p] = max(z[p−1], raw[p])`.
Structural — it holds for every feasible solution, not only at the optimum. No big-M, no new binaries.

**Residual defect:** `D` remained a one-sided epigraph, and with `raw` and `z` now exact *functions* of
`D`, inflating `D` reproduced the exploit exactly — solver `D(sat_half)` **246 → 267** (+21 kW),
residual −96.171980; S2 residual −112.200643.

Closure was **blocked** because an exact `D` collided with two CLOSED decisions (A4 and the
reduced-native-MAX tractability implementation). It was correctly **escalated as a methodology question
rather than silently implemented**.

---

## 10. Exact-D — closure (PASS)

**Verdict: `PASS - Surface 1 end-to-end validated; full annual build-only audit PASS`.
Core `02abcaa1` → `f848282a`.**

The solver chain is now exact end to end:

```
p_grid[t]
  → D[m,q]  = kappa · max over period hours of p_grid[t]   (exact, addGenConstrMax)
  → raw[p]  = max(0, D[p] − CC)                             (exact)
  → z[first]= raw[first];  z[p] = max(z[p−1], raw[p])       (exact running max)
  → delta_z[p] == frozen q[p]
  → q_2x[p] = min(delta_z[p], 0.10·C[p]);  q_3x[p] = delta_z[p] − q_2x[p]
```

42 `D`-relations over 7 910 operands, 42 `raw`, 30 `z`, plus 8 pre-existing Class-C — 114 general
constraints added. Residuals collapse to machine epsilon (max |2.9e-11|). Tests E1–E5 PASS; the W-07
deterministic suite passes 19/19.

**A4 remains CLOSED.** `a4_reopened = false`; in-model `D` is still a tariff-cost-facing optimization
auxiliary; reported billing maxima are still recomputed post-solve; the κ methodology and the
"calibrated hourly proxy" wording are unchanged.

> **Exact-D is not an exact reconstruction of 15-minute metering.** It is an exact per-period maximum of
> the *same calibrated hourly proxy* that A4 already governs.

---

## 11. Methodology decisions that did not change

| Decision | Changed? | Note |
|---|:---:|---|
| **A4** (billing-demand reporting) | **NO** | In-model `D` still an auxiliary; maxima still recomputed post-solve |
| **A2** (reserve / outage replay) | **NO** | Constant worst-case floor; `e₀ = 0.10E^N + R`; technical SOCmin; no circular wrap |
| **B1** (degradation) | **NO** | PNNL-calibrated Xu-derived intertemporal PWL |
| W-04 calendar | **NO** | Input corrected; calendar semantics unchanged |
| W-18 | **NO** | Additive validation only |
| W-07 tier definition | **NO** | Frozen equations preserved; implementation corrected |
| Surface-1 / Exact-D | **NO** | Solver encoding corrected |
| κ estimator / window / boundary | **NO** | Through-origin LS; 2025-01…2025-10; observed load − observed PV |
| Tariff source | **NO** | 13b NO ACTION |
| CC semantics | **NO** | One annual endogenous continuous CC; supplementary = 0 |
| PNNL package roles | **NO** | 10 MW mainline, 1 MW sensitivity |
| Rainflow / calendar aging / winter-PV roles | **NO** | Ex-post validation, screening, sensitivity respectively |

**Narrowly reopened, by explicit governance ruling:** only the *reduced-native-MAX / floating-demand
tractability implementation*, and only because a demonstrated solver-correctness defect invalidated the
assumption that a floating demand epigraph was harmless.

---

## 12. Parameter / semantics status

Gate 3 compared **57 production-controlling parameters**, whether or not they changed:

- **56 UNCHANGED**
- **1 CHANGED_EXPECTED** — `P39` tier-allocation semantics (the W-07 implementation correction, §7)
- 0 unexpected, 0 pending, 0 not-recovered

This is worth stating plainly because it is easy to miscount: **four defects were corrected, but only
one of them touched a controlled parameter entry**, and that one is an implementation-semantics change,
not a numeric one. The other three changed an *input* (W-04) or a *solver encoding* (Surface-1,
Exact-D).

A direct diff of **every module-level constant** between the production core blob and the live file
returns **no difference** (`SOC_MIN`, `SOC_MAX`, `ETA_C`, `ETA_D`, `BREAKPOINTS`, `TOU_ORDER`), and the
model-boundary docstring is identical.

---

## 13. Input changes

| Input | Status |
|---|---|
| TOU calendar `5d5a6d7f` → `e6053311` | `VALUE_CHANGED_EXPECTED` (W-04) |
| Canonical CSV `d381217c` → `6ab78508` | `VALUE_CHANGED_EXPECTED` (W-04 propagation) |
| Canonical Parquet `e0d4a8e8` → `9142b8b6` | `VALUE_CHANGED_EXPECTED` (W-04 propagation) |
| Seasonal settlement matrix `31172c47` → `ed7f8dbf` | `VALUE_CHANGED_EXPECTED` — exactly two cells: 2025-02 non-summer `sat_half` 60→45, `off` 327→342 |

**Eleven inputs are bit-identical:** observed site data, baseline load, observed PV, baseline PV, tariff
registry, billing registry, CPI registry, PNNL cost package, degradation package, parameter registry and
the 14a economic interface.

*Disclosure:* the load/PV source artifacts are bit-identical on the basis of filesystem mtimes predating
every gate plus Gate A's **aggregate** `protected_files_unchanged = 2350`, not an itemized manifest pin.
That is weaker evidence than elsewhere and is labelled as such.

---

## 14. Provenance-only refreshes

**14b transition settlement interface** `896f07e4` → `f101af47`:
`VALUE_UNCHANGED_PROVENANCE_REFRESHED`. Its sole content delta is the pinned annual-input parquet
`e0d4a8e8` (pre-W-04) → `9142b8b6` (corrected). This was the single **active stale dependency** in the
whole chain; `active_stale_dependencies` is now 0.

**κ is bit-identical** at `1.0103668594376984` (`absolute_difference 0.0`, `bitwise_identical true`),
invariant by construction because both `B_m` and `H_m` are maxima over hour *sets*, which TOU
relabelling re-partitions but does not change.

**Script 13c's outputs are bit-identical despite its source changing.** Across all 12 NTUST bills
exactly one period-row has positive over-contract exceedance (2025-09 `half`) and no month has two or
more — the real billing data never exercises the W-07 discriminator. **This is not evidence that the
correction is inert in the optimization**, where the discriminator *is* reachable.

---

## 15. Historical results (accepted, superseded, immutable)

- Historical EOB — objective 66 738 326.341512024 NTD-2023/yr and all seven cost components
- Historical final-81 surface — `COMPLETE_PASS`, 81 cases
- Historical representative preflight runs, winter-PV 17a–17c artifacts, ex-post rainflow validation

All re-hashed unchanged. All simultaneously **historically accepted** and **currently superseded**.

`scripts/15c` `EXPECTED_EOB_REFERENCE` still holds the **historical** values (lines 70–76) and must be
re-baselined under audit **only after** a corrected EOB exists.

---

## 16. Pending corrected results

All are `PENDING_CORRECTED_RERUN` with reserved ledger slots and **no fabricated values**:

- corrected production EOB — **CORRECTED EOB NOT YET RUN**
- corrected representative Layer A cases
- corrected final-81 Layer A production (requires a **new** run directory)
- corrected winter-PV sensitivity
- the A2 6-point reserve-floor robustness check (framework line 1093; never executed, so no historical
  baseline and no old-vs-new delta)

No numeric result is predicted anywhere. The single directional expectation recorded is qualitative: the
solver-vs-exact demand residual **should collapse toward zero**, because that is the defining purpose of
the Exact-D correction.

---

## 17. Missing / unresolved historical lineage

**Core revisions r2–r4 and r6–r7 have no surviving evidence.** Gate 2 established that four core
versions exist — `r1` (`448235d3`), `r5` (`7f918717`), `r8` (`07119edd`), `r9` (`d145eeb0`) — of which
only `r1` and `r9` were ever committed. `r5` and `r8` were recovered from Layer A preflight run
manifests. The five states implied by the numbering between them have no hash, no manifest reference and
no artifact anywhere. **They are preserved as an unresolved gap and deliberately not synthesized.**

This gap sits **entirely before** the previous accepted production node `r9`, and does **not** break the
verified `r9`-forward correction chain, in which every link satisfies
`after_hash(N) == before_hash(N+1)` exactly.

**Six core states are `HASH_IDENTITY_ONLY`** — `r5`, `r8`, Gate B (`e87309fe`), Gate C, Pre-EOB and
Surface-1 (`02abcaa1`). Their source bytes no longer exist and cannot be rehashed. They must never be
promoted to `SOURCE_VERSION_FULLY_RECONSTRUCTED`. `r5` and `r8` are the weakest, resting on a single
manifest each.

**No lineage family is claimed `ORIGINAL_VERIFIED`.** All 14 are `EARLIEST_VERIFIABLE_ANCESTOR`. The
core evidence is strong — `git log --all --diff-filter=A` proves the file was *added* at `ae31d136`,
never renamed, and no pre-v7.2 core exists anywhere — but the `r1` version string reads 2026-08-29 while
the commit is 2026-08-30, and `r5`/`r8` prove this project holds untracked core revisions. Earlier origin
cannot be affirmatively ruled out.

**Date-evidence limits:** seven nodes carry `EARLIEST_VERIFIABLE_DATE` only (gitignored artifacts and
never-committed tests). Exactly one node, the historical EOB artifact, rests on `filesystem_time_only`,
corroborated by its freeze-audit `script_version` and the `v7.2-post15c-eob` tag, and marked MEDIUM
confidence. Nothing was guessed.

**Divergence from the 2026-09-15 artifact:** that file records the core chain as
`f848282a → 02abcaa1 → e87309fe → d145eeb0 → root ae31d13, ORIGINAL_VERIFIED`. It omits `r5` and `r8`
entirely and does not record the missing revisions. Its statements that were independently checked all
held; this is an **incompleteness**, not an error, and not a provenance conflict.

---

## 18. CORE_VERSION alignment pending

`CORE_VERSION` still reads `…-2026-09-06-r9` while the source hash is `f848282a…`. Classification:
**`SOURCE_CHANGED_VERSION_PENDING_ALIGNMENT`** — an `AUTHORITY_ALIGNMENT_PENDING` condition, **not** a
model defect. No gate edited it.

The alignment surface, recorded by the Exact-D manifest as out of its own scope: `scripts/15b`
(`EXPECTED_CORE_VERSION`), `scripts/16a`, `scripts/17b`, `scripts/17c`, `scripts/19a`, plus the
cross-check in `tests/test_transition_candidate1_static_v7_2.py`. That test's
`test_reduced_max_builder_is_class_specific_and_ex_post_safe` still asserts the removed source string
`transition_demand_ge_seasonal_max_` and is therefore **currently expected to fail**; it must be updated
together with the version bump, not patched piecemeal. The seven `docs/checkpoints/` occurrences are
historical provenance and must remain untouched.

---

## 19. What remains before corrected production authority exists

1. **Core authority alignment** — bump `CORE_VERSION` coherently with its exact-string pins and update
   the superseded static assertion (§18). Separately authorized.
2. **Root-node tractability preflight** — the annual model builds in 3.40 s, but it has never been
   solved with the corrected formulation. A bounded solve preflight is required.
3. **Corrected EOB**, then re-baseline `EXPECTED_EOB_REFERENCE` under audit.
4. **Corrected representative Layer A**, sensitivities, and the A2 6-point reserve-floor decision gate.
5. **One** corrected 81-case production run in a **new** run directory.
6. **New production authority** — new commit, checkpoint, authority manifest, runner version and a new
   annotated tag. Historical tags are never retargeted.

Each requires its own separate authorization. Nothing in this document confers any of them.

---

## Appendix A — Non-controlling references

| Artifact | Classification | Gate-4 treatment |
|---|---|---|
| `docs/ai_handoff/CURRENT_STATE.md` | `STALE_NON_CONTROLLING_REFERENCE` | Controlled zero fields; **not edited**. Stale on three verified points: it claims no 81-case result exists (it does), names the superseded 2026-09-10 authority manifest as latest, and says the production tag does not peel to HEAD (it does). |
| `pre_corrected_rerun_version_lineage_v7_2_2026-09-15.md` | `PRIOR_UNACCEPTED_ADDITIVE_ARTIFACT` | Controlled zero fields; **not edited or overwritten**. See §17. |

## Appendix B — Cross-agent execution history

| Stage | Agent |
|---|---|
| Gate A (W-04 + W-18), Gate B before-snapshot | Codex |
| Gate B (W-07), Gate C, Pre-EOB, Surface-1, Exact-D | Claude Code |
| Pre-Rerun Baseline Gates 1–4 | Claude Code |

**This is provenance metadata only, not an authority hierarchy.** Neither agent's output is privileged.
Technical authority derives from repository state, SHA-256 identities, deterministic tests,
solver-integration results, accepted gate manifests and checkpoint records. Where any agent report
conflicts with reproducible repository evidence, **the repository evidence wins** and the discrepancy is
recorded rather than quietly reconciled. No such conflict was found across Gates 1–4.
