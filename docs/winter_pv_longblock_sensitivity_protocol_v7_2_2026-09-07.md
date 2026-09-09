# V7.2 PROJECT IMPLEMENTATION PROTOCOL

## WINTER-PV SENSITIVITY ONLY

**Protocol date:** 2026-09-07

**Freeze date:** 2026-09-09

**Protocol status:** FROZEN / APPROVED FOR IMPLEMENTATION

**Role:** project-level v7.2 implementation protocol; sensitivity-only
**Methodological scope:** controls Winter-PV long-block H1/H2/H3 holdout validation and the prerequisites for the later sensitivity-only branch
**Authority boundary:** this document supplements, and does not supersede, the authoritative v7.2 Framework and v7.2 Literature/Evidence Registry.

This approved protocol freezes the operational details that the v7.2 Framework and Registry require but do not fully prescribe for the Winter-PV long-block sensitivity. It does **not** alter the production/mainline model, tariff authority, data source-of-truth, or frozen EOB provenance.

---

## 1. Controlling purpose and authority

### 1.1 Framework / Registry requirements

The controlling sources are:

| Controlling source | Exact requirement used here |
|---|---|
| `docs/research_framework_v7_2_2026-08-24.md` §4.1.3, lines 477–510 | `pre_system` and `missing_winter` PV availability remains conservative zero in the mainline; an alternative CWA/synthetic winter branch is sensitivity-only; a long-block/month holdout must precede it. |
| Framework §16.1, lines 2480–2499 | Winter PV is a one-time comparison of conservative-zero against an alternative reconstructed/synthetic PV treatment for economic outputs. |
| Framework §25 Phase 1 #11, line 3117; §31.3 #9, line 3550; §32 checklist, line 3643 | Complete long-block/month holdout validation before running and saving the Winter-PV economic sensitivity. |
| Framework §6, lines 1222–1245 | EOB outputs are \(E^N_{EOB}\), \(P^B_{EOB}\), \(CC_{EOB}\), \(C_{EOB}\), dispatch, and billing/degradation components; resilience premium is defined relative to EOB. |
| `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` R32, lines 1070–1088; I5, lines 1549–1574 | CWA weather/irradiance can be an explanatory input, but the CWA→PV mapping must be validated against observed NTUST PV. |
| Registry P1-E, lines 1666–1680; maintenance rule, line 2368 | The 1,463-hour long-unavailable block is conservative-zero mainline; Script-04b short-gap evidence must not be used as long-block evidence without separate block/month holdout validation. |

The relevant Framework wording is deliberately narrow: long unavailable PV is described as **“conservatively assigned zero PV availability due to unavailable observations.”** It must never be reported as proof that the physical PV generation was truly zero.

### 1.1.1 Explicit authority versus project decisions frozen here

| Category | Controlled by Framework / Registry | Project-level decision frozen by this protocol |
|---|---|---|
| Mainline boundary | Long-unavailable PV remains conservative-zero; an alternative is sensitivity-only. | None: this protocol preserves the controlling mainline rule. |
| Validation prerequisite | A block/month holdout must precede Winter-PV use. | H1/H2/H3 geometry, exact target timestamps, no temporal buffer, and the overlap-reporting rule. |
| Candidate evidence | A CWA→PV mapping requires validation against observed NTUST PV; short-gap evidence is insufficient for the long block. | Primary CWA candidate, training-only hour-of-day mean PV climatology baseline, no additional model families, metrics, bootstrap convention, and comparative acceptance rule. |
| Economic scope | At least EOB, dispatch, CC, annual cost, and resilience premium must be checked; Winter-PV is a one-time sensitivity. | Exactly one alternative EOB and exactly one alternative `a0.80_b08` solve; the fixed comparator artifacts and reporting layout. |
| Provenance / non-mutation | Canonical mainline and existing source lineage must remain controlled. | Required future manifest fields and separate alternative-artifact role/naming. |

Nothing in the right-hand column claims to be an official tariff rule, an external literature threshold, or a Framework amendment.

### 1.1.2 Completed implementability evidence

The following is repository/data implementability evidence. It is neither an external Framework/Registry requirement nor a project-level accuracy result. No H1/H2/H3 holdout prediction or validation metric has been generated or observed.

| Item | Verified implementability evidence |
|---|---|
| H1 | 744 unique target hours; all 744 have valid observed-PV truth, no outage contamination, and required CWA GHI. |
| H2 | 672 unique target hours; all 672 have valid observed-PV truth, no outage contamination, and required CWA GHI. |
| H3 | 1,463 unique target hours; all 1,463 have valid observed-PV truth, no outage contamination, and required CWA GHI. |
| Actual Nov–Dec sensitivity target | All 1,463 long-unavailable target timestamps have CWA GHI coverage required by the approved candidate. |
| CWA candidate | With the entire applicable holdout excluded before fitting, the existing `hourly_ghi_ratio_median` model family can produce complete leakage-free H1/H2/H3 predictions. |
| HOD mean climatology baseline | The same whole-holdout eligibility masks leave 6,543 H1, 6,615 H2, and 5,824 H3 training rows. Every hour-of-day retains eligible observations; Script 17a must independently recompute and gate these counts. |
| Historical donor method | It cannot produce complete leakage-free H1/H2/H3 predictions under the whole-holdout rule because its validated short-gap formulation requires target-day context PV and `K=5` donors within a ±30-calendar-day window. |
| Capacity bound | The eligible non-holdout training sets resolve to 357.0 kW for H1, H2, and H3; the future all-eligible production fit also resolves to 357.0 kW. This is evidence from the current data, not a hard-coded parameter. |

### 1.2 Mainline boundary

The production/mainline annual input remains unchanged:

\[
PV_t^{base}=0,
\qquad t\in\{\texttt{pre_system},\texttt{missing_winter}\}.
\]

This protocol exists only to test whether that conservative-zero assumption materially affects:

1. EOB economics; and
2. the Layer-A resilience premium.

It does not authorize overwriting `data/processed/annual_input_v7_1.parquet`, its CSV counterpart, any tariff interface, or any frozen EOB artifact.

---

## 2. Current PV lineage and fixed data boundary

The formal case year is 2024-11-01 00:00 through 2025-11-01 00:00, end-exclusive, on the audited interval-start hourly chronology.

| PV lineage category | Hours | Timestamp span | Mainline role |
|---|---:|---|---|
| `pv_status=valid` | 7,297 | 2024-12-31 23:00 through 2025-10-31 23:00 | Observed PV truth retained. |
| Short outage-contaminated PV | 10 | 2025-04-19 14:00–16:00 (3 h); 2025-08-02 09:00–15:00 (7 h) | Planning PV was reconstructed by the validated short-gap rule; `observed_pv_kw` remains preserved. |
| `pre_system` | 600 | 2024-11-01 00:00 through 2024-11-25 23:00 | Conservative-zero availability. |
| `missing_winter` | 863 | 2024-11-26 00:00 through 2024-12-31 22:00 | Conservative-zero availability. |
| Long unavailable total | 1,463 | Near-contiguous Nov–Dec block | Sensitivity-only target; not observed physical zero generation. |

The existing script roles remain unchanged:

- Script 04 validates short donor pseudo-gaps and explicitly excludes prolonged winter/unavailable PV.
- Script 04b compares donor and CWA reconstruction on the same 3 h / 7 h pseudo-events and explicitly excludes the long block.
- Script 05 constructs the mainline planning PV baseline: it reconstructs the 10 short intervals and assigns `unavailable_zero_mainline` to the long statuses.
- Script 06 integrates the annual input, preserves provenance, and asserts the long-status zero assignment.

---

## 3. Frozen reconstruction candidate and long-block baseline

### 3.1 Primary candidate

The sole primary candidate is:

```text
CWA hourly_ghi_ratio_median
```

This is the existing CWA mapping used for validated short gaps. It estimates a PV/GHI ratio from eligible observed training rows, uses hour-specific medians, falls back to the model's existing global median where necessary, and retains the existing daylight and controlled-capacity behavior.

For H1/H2/H3, the future dedicated Script 17a may replace the current short-gap `training_rows()` target-day exclusion orchestration with the whole-window exclusion mask required by Section 5. This is an orchestration change only. It must not change:

- the `hourly_ghi_ratio_median` equation;
- the hourly PV/GHI ratio estimator;
- the existing GHI thresholds;
- the existing training-derived global-median fallback;
- the existing night/daylight guard;
- training eligibility semantics; or
- the training-derived `pv_cap_kw` rule.

The validated CWA model family therefore remains unchanged.

### 3.2 Training-only hour-of-day mean PV climatology baseline

The Winter-PV long-block/month validation baseline is the project-level:

```text
TRAINING-ONLY HOUR-OF-DAY MEAN PV CLIMATOLOGY
```

For each holdout independently:

1. Apply exactly the same whole-holdout exclusion mask used for CWA fitting.
2. Retain only eligible valid, observed, non-outage PV training rows.
3. For each hour-of-day `h`, compute:

   ```text
   climatology_mean_h = mean(
       observed_pv_kw
       for eligible training rows
       where hour_of_day == h
   )
   ```

4. For each target timestamp `t`, predict:

   ```text
   prediction_climatology_t = climatology_mean_{hour_of_day(t)}
   ```

5. Apply the existing controlled non-negativity and training-derived PV-capacity physical bound.
6. Apply the same established night/daylight physical rule where applicable.

The HOD mean climatology baseline must use training data only. It must not use target PV, target-day context PV, CWA GHI, other weather information, or donor ranking. It must produce exactly one prediction for every H1/H2/H3 target timestamp.

The CWA-specific target-hour rule `GHI <= DAYLIGHT_GHI_THRESHOLD => prediction = 0` is retained for the CWA candidate. It is not applicable to the HOD mean climatology baseline because that baseline is prohibited from reading target CWA GHI. For climatology, the training-derived HOD mean, non-negativity/cap checks, and reported night behavior apply; no separate target-GHI rule or replacement daylight model is introduced.

The two methods intentionally use different statistics for different roles:

- The CWA candidate retains the validated hour-specific **median PV/GHI ratio**, multiplied by contemporaneous CWA GHI, plus its existing global-median fallback and physical guards.
- The climatology baseline uses the arithmetic **mean observed PV by hour-of-day** as a simple weather-free reference.

The HOD mean climatology is selected because climatology is a standard simple reference family for solar-prediction validation, the mean is the natural central tendency under squared-error loss, and hourly RMSE is one of the two primary comparative metrics. It therefore provides a transparent naive benchmark aligned with that loss. This is a project-level methodological decision made before validation outcomes are observed and frozen by the approval recorded above before formal validation. It is not explicitly required by Framework v7.2 or prescribed as this exact NTUST protocol by an external paper, and it does not imply that alternative robust climatological summaries are invalid.

Before calculating validation metrics, Script 17a must record and verify for each holdout:

- eligible climatology training-row count;
- eligible rows for every hour-of-day;
- the HOD mean PV value for every hour 0–23;
- no missing or non-finite HOD mean;
- complete, unique target prediction coverage;
- no target leakage;
- resolved training-derived `pv_cap_kw`; and
- all physical-validity gates in Section 6.3.

If any hour-of-day lacks an eligible training observation, validation fails to execute. Script 17a must stop without inventing a fallback. No global fallback of any kind is authorized for the climatology baseline.

This HOD mean climatology is a new project-level long-block validation baseline. It is not an official Framework/Registry method, an external-paper requirement, or the historical short-gap donor method. Its sole purpose is to test whether the weather-informed CWA mapping adds predictive value beyond a simple leakage-free time-of-day mean-PV climatology.

### 3.3 Historical donor scope

The existing donor method remains valid evidence only for the previously completed short-gap reconstruction comparison. It is not used as the Winter-PV long-block/month benchmark and has no role in the Winter-PV PASS/FAIL decision.

Its validated formulation requires target-day context PV and `K=5` donors within a ±30-calendar-day search window. Those requirements are incompatible with whole-month/whole-block leakage exclusion. This scope distinction is not evidence that the donor method is poor.

This protocol does not authorize widening the donor window, reducing `K`, adding a donor fallback, using target-day PV, or relabelling a modified donor as the previously validated donor method.

### 3.4 Excluded alternatives

This protocol introduces no additional weather-to-PV model family, no seasonal regression family, no machine-learning model, and no new donor rule. The project-level HOD mean climatology is a validation baseline, not a candidate reconstruction model for the actual Nov–Dec sensitivity target.

---

## 4. Frozen observed-PV holdout geometry

The following are three independent validation exercises. H3 intentionally overlaps H1 and H2; results must be reported separately and must not be pooled as independent observations.

| ID | Target interval, end-exclusive | Expected intervals | Role |
|---|---|---:|---|
| H1 | 2025-01-01 00:00 \(\le t <\) 2025-02-01 00:00 | 744 | January full-month observed winter proxy. |
| H2 | 2025-02-01 00:00 \(\le t <\) 2025-03-01 00:00 | 672 | February full-month observed winter proxy. |
| H3 | 2025-01-01 00:00 \(\le t <\) 2025-03-02 23:00 | 1,463 | Primary exact-length contiguous long-block holdout. |

### 4.1 Pre-implementation verification

This protocol independently checked `data/processed/ntust_case_year_observed.csv` before implementation:

| Holdout | Actual rows | Expected rows | Valid observed-PV truth rows | Outage-contaminated rows | Duplicate timestamps |
|---|---:|---:|---:|---:|---:|
| H1 | 744 | 744 | 744 | 0 | 0 |
| H2 | 672 | 672 | 672 | 0 | 0 |
| H3 | 1,463 | 1,463 | 1,463 | 0 | 0 |

The source used for this check has SHA-256:

```text
C5039B55049F28BD4B99D2DFB0DCD0C5F9A26790E90C8D6C6947E3D4C8BA05D3
```

H1/H2/H3 are observed winter-proxy periods. They do **not** supply direct ground truth for the actual 2024-11 through 2024-12 unavailable interval. H3 tests robustness to a contiguous block of the same length; it is not a claim of historical recovery truth.

---

## 5. Frozen leakage control

For every holdout and for both the CWA candidate and HOD mean climatology baseline:

1. Remove the **entire target holdout** from CWA fitting and HOD mean climatology construction.
2. Permit no target-hour or target-day observed PV value to enter any fit statistic, HOD mean statistic, capacity calculation, or fallback statistic.
3. Derive the CWA global-median fallback only from the eligible non-holdout CWA training rows.
4. Permit no fallback for the HOD mean climatology baseline.
5. Permit contemporaneous CWA meteorological inputs only as explanatory inputs available to the CWA mapping.
6. Forbid lagged, rolling, target-PV, or target-derived PV features.

No extra temporal buffer is required for this frozen model because it uses no lagged or rolling target-PV feature. If implementation adds any such feature, it must stop: this protocol no longer applies and requires a new controlled protocol.

---

## 6. Frozen metrics, uncertainty reporting, and physical gates

### 6.1 Required metrics for each holdout and method

Report all of the following:

- hourly MAE, kW;
- hourly RMSE, kW;
- total observed energy, kWh;
- total reconstructed energy, kWh;
- signed aggregate energy bias, %;
- absolute aggregate energy bias, %;
- daily signed energy-error distribution, reported in kWh and, when daily observed energy is positive, as a percent of daily observed energy;
- physical-validity checks; and
- daylight/night behavior.

### 6.2 Frozen bootstrap reporting convention

For the CWA candidate and HOD mean climatology baseline in each holdout, calculate a daily-block bootstrap 95% percentile confidence interval for:

- hourly MAE; and
- signed aggregate energy bias.

The project-level implementation convention frozen here is:

- H1 consists of 31 complete 24-hour daily blocks;
- H2 consists of 28 complete 24-hour daily blocks;
- H3 consists of 60 complete 24-hour daily blocks and one final fixed 23-hour partial block;
- resample the complete calendar-day blocks with replacement within the holdout;
- preserve all hourly observations in each sampled day;
- calculate each metric from the concatenated sampled blocks;
- use 10,000 resamples, seed `20260907`, and the 2.5th/97.5th percentiles;
- retain the per-resample values or a reproducible compressed equivalent in the validation artifact.

For every H3 bootstrap replicate, sample the 60 complete daily blocks with replacement and include the final 23-hour partial block exactly once. Bootstrap intervals are uncertainty reporting only; they are not additional PASS/FAIL thresholds.

### 6.3 Required physical/data-quality gates

Every one of the following must pass:

- no leakage;
- exactly one prediction per target timestamp;
- no missing target prediction;
- no duplicate target timestamp;
- prediction \(\ge 0\);
- prediction \(\le\) the applicable training-derived `pv_cap_kw` defined in Section 6.4;
- existing candidate daylight/night guard is retained;
- observed target truth is never overwritten; and
- exact target-hour count equals the Section 4 definition.

### 6.4 Training-derived physical capacity bound

`pv_cap_kw` is not a new fixed nameplate parameter. For each holdout and method, derive it only from the eligible non-holdout observed-PV training set:

\[
pv\_cap\_kw=\max_{t\in\text{eligible non-holdout training rows}}PV_t^{observed}.
\]

The CWA candidate and HOD mean climatology baseline must use the same eligible training-set definition and resolved bound for a given holdout. Script 17a must record the value, units, training-row count, and training-row hash in validation provenance.

Current implementability evidence resolves H1, H2, H3, and the future all-eligible production fit to 357.0 kW. That value must not be hard-coded: it remains a data-derived result that must be recomputed and checked from the controlled inputs.

---

## 7. Frozen validation acceptance rule

There is no externally specified absolute NTUST reconstruction-accuracy threshold. This protocol therefore introduces **no** 10%, 15%, 20%, or other absolute error threshold.

The frozen comparative acceptance rule, selected before seeing these holdout outcomes, is:

### 7.1 Primary H3 requirement

The CWA `hourly_ghi_ratio_median` primary candidate must have both:

1. lower hourly RMSE than the training-only HOD mean climatology baseline; and
2. lower absolute aggregate energy bias than the training-only HOD mean climatology baseline.

### 7.2 Secondary H1/H2 requirement

For H1 and H2 independently, CWA must not be strictly worse than the training-only HOD mean climatology baseline on both:

1. hourly RMSE; and
2. absolute aggregate energy bias.

Equivalently, for neither monthly holdout may the HOD mean climatology baseline strictly dominate CWA on both primary metrics simultaneously.

### 7.3 Verdict

If every physical, completeness, and leakage gate passes and Sections 7.1–7.2 hold:

```text
WINTER_PV_RECONSTRUCTION_VALIDATION = PASS_FOR_SENSITIVITY
```

Otherwise:

```text
WINTER_PV_RECONSTRUCTION_VALIDATION = FAIL
```

On `FAIL`, no alternative annual economic-sensitivity input may be produced.
No Winter-PV economic-sensitivity solve may be run.

`PASS_FOR_SENSITIVITY` means only:

> qualified as a plausible sensitivity alternative.

It does **not** mean that actual missing Nov–Dec PV has been recovered accurately.

---

## 8. Frozen alternative annual-input build, conditional on PASS

Only after `PASS_FOR_SENSITIVITY`:

1. Fit the approved CWA `hourly_ghi_ratio_median` mapping using all canonical case-year PV/GHI training rows that are valid, observed, non-outage, and non-long-unavailable.
2. Apply that fit only to the 1,463 `pre_system` / `missing_winter` timestamps.
3. Preserve timestamps, Load, `observed_pv_kw`, `pv_status`, calendar labels, TOU labels, billing-usage-period labels, and all source provenance fields.
4. Replace only the alternative artifact's planning PV-availability field for the controlled long statuses, and update any directly dependent planning residual field consistently.

The alternative artifact must have a separate role, for example:

```text
winter_pv_sensitivity_only
```

It must receive a distinct filename and hash. It must never overwrite:

```text
data/processed/annual_input_v7_1.parquet
data/processed/annual_input_v7_1.csv
```

---

## 9. Frozen kappa and economic-method boundary

Winter-PV sensitivity isolates only the long-unavailable planning-PV assumption. The following remain exactly unchanged:

- observed-data \(\kappa\); no recalibration;
- tariff registry and tariff calendar;
- transition-period settlement method;
- current PNNL cost package;
- degradation formulation;
- real discount rate and CRF;
- current reduced-MAX Candidate-1.1 production formulation; and
- production `MIPGap = 1e-6`.

The existing \(\kappa\) calibration remains based on observed Load–PV data, not on sensitivity PV.

---

## 10. Frozen economic-sensitivity scope

After Sections 4–8 pass, the exact economic scope is:

1. one alternative-PV EOB annual solve; and
2. one alternative-PV Layer-A annual solve at:

```text
alpha = 0.80
beta_h = 8
case_id = a0.80_b08
```

`a0.80_b08` is selected ex ante as the canonical center of the validated representative design space. It must not be changed after observing Winter-PV outcomes.

This protocol explicitly forbids:

- an alternative 81-point surface;
- all five representative cases; and
- any outcome-selected alternative case.

---

## 11. Frozen mainline comparators

### 11.1 EOB comparator

Use the existing frozen production EOB artifact. Do not regenerate or overwrite it. The completed semantic-equivalence audit established that the frozen EOB dispatch and objective are numerically equivalent under current tariff semantics for its saved solution.

### 11.2 Layer-A comparator

Use the validated current reduced-MAX representative artifact for:

```text
run_id = 20260906T050046737317Z_5f2cd1942c
case_id = a0.80_b08
```

Before comparison, implementation must verify its recorded source hashes, `OPTIMAL` status, and production MIP-gap result.

Alternative results must use the current production core and the same production tariff, economic, settlement, degradation, and solver settings.

---

## 12. Required economic comparison outputs

For both mainline and Winter-PV alternative, report the following in constant NTD-2023 where monetary:

| Scope | Required outputs |
|---|---|
| EOB | objective / annual cost; \(E^N\); \(P^B\); \(CC\); annual dispatch summary; billing-cost decomposition. |
| Layer A `a0.80_b08` | objective / annual cost; \(E^N\); \(P^B\); \(CC\); dispatch summary; billing-cost decomposition. |

For each comparable scalar \(x\), report:

\[
\Delta x=x_{winter}-x_{main},
\qquad
\%\Delta x=\frac{x_{winter}-x_{main}}{x_{main}}\times100\%,
\]

where the denominator is meaningful and nonzero.

Compute resilience premiums separately:

\[
Premium_{main}=\frac{C_{A,main}-C_{EOB,main}}{C_{EOB,main}}\times100,
\]

\[
Premium_{winter}=\frac{C_{A,winter}-C_{EOB,winter}}{C_{EOB,winter}}\times100,
\]

\[
\Delta Premium_{pp}=Premium_{winter}-Premium_{main}.
\]

`Delta Premium` must be reported in percentage points, not as a percent of a percent.

---

## 13. Winter-PV P1 closure rule

The Winter-PV pre-81 P1 closes only when all of the following are true:

1. this frozen holdout protocol is executed exactly;
2. CWA receives `PASS_FOR_SENSITIVITY`;
3. alternative annual-input provenance/build checks pass;
4. alternative EOB reaches the required production solver/gate status;
5. alternative `a0.80_b08` reaches the required production solver/gate status;
6. all normal physical, billing, tariff, transition, and rainflow gates pass;
7. canonical mainline artifacts remain byte-identical; and
8. a complete mainline-versus-Winter-PV economic comparison is produced.

No desired magnitude of economic change is required for pass. The sensitivity may reveal either a small or a large economic effect; its purpose is measurement, not confirmation of a preferred outcome.

---

## 14. Required future provenance

Future implementation must record, at minimum:

- this protocol's version and SHA-256;
- Git commit and dirty state;
- script and shared-core versions / hashes;
- CWA source hash;
- observed-PV source hash;
- canonical annual-input hash;
- each frozen holdout definition;
- separate CWA and HOD-mean-climatology training-row hashes and counts for each holdout;
- climatology eligible-row counts and resolved means for every hour-of-day;
- CWA fit-row counts, resolved hourly/global ratios, and any invocation of the existing global fallback;
- each holdout's recomputed `pv_cap_kw`, units, and derivation record;
- alternative annual-input hash;
- economic, tariff, and settlement interface hashes;
- run IDs;
- Python and Gurobi versions; and
- the fixed selected Layer-A case `a0.80_b08`.

---

## 15. Non-authority and non-mutation statement

This is a **V7.2 PROJECT IMPLEMENTATION PROTOCOL — WINTER-PV SENSITIVITY ONLY**.

It does not:

- change the production mainline;
- alter Framework or Registry authority;
- claim an official tariff rule;
- claim direct recovery of missing Nov–Dec PV truth;
- authorize an alternative 81-case surface; or
- authorize overwriting canonical data or frozen artifacts.

Implementation is approved under this freeze. Script 17a validation must pass before any later, separate annual economic-sensitivity solve; this protocol does not itself authorize such a solve.
