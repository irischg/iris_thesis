# Layer A robustness preregistration — Candidate R1

Date: 2026-09-27  
Package identity: `LAYER_A_ROBUSTNESS_PREREGISTRATION_CANDIDATE_R1`  
Lifecycle: **CANDIDATE / NOT ACCEPTED / NOT CLOSED**  
Authoring verdict: **CANDIDATE_R1_PASS** (package completeness only; not scientific acceptance or execution authority)

## 1. Current source-of-truth banner and action gate

- `FRAMEWORK = V7.4`
- `PIPELINE = V7.4 CURRENT ACCEPTED ROUTE`
- `REGISTRY = V7.4`
- `TARGET_ACTION = CREATE_NEW_TASK3_PREREGISTRATION_CANDIDATE_R1`
- `WRITE_SCOPE = NEW_ADDITIVE_CANDIDATE_FILES_ONLY`
- `SOLVE_SCOPE = ZERO`
- `IMPLEMENTATION_SCOPE = ZERO`
- `FULL81_SCOPE = ZERO`

The current methodology authority is `docs/research_framework_v7_4_2026-09-26_r2.md`; the current evidence authority is `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`. Older implementation filenames do not downgrade the current v7.4 accepted route. This checkpoint creates documentation/provenance only. It does not accept itself, change methodology, change code or data, authorize a production run, or authorize Full81.

## 2. Purpose and locked A2 design

Framework v7.4 §16.1 locks A2 as a targeted **robustness/model-form screening** comparison between the current mainline constant worst-case reserve floor and a perfect-information time-varying reserve floor. It is not a new mainline and not a second research question.

The six cases are exactly:

1. `a0.60_b04`
2. `a0.60_b12`
3. `a0.80_b04`
4. `a0.80_b12`
5. `a1.00_b04`
6. `a1.00_b12`

When separately authorized, the constant-floor arm is reused and the counterfactual requires exactly six new variable-floor solves. If, and only if, a future frozen material-shift rule triggers, the extension is exactly three beta=8 points: `a0.60_b08`, `a0.80_b08`, and `a1.00_b08`. Expansion is not automatic.

## 3. Structural Full81 dependency

The constant-floor arm must be reused from the accepted current-route Full81 surface. Under this preregistration's locked dependency record, only `a0.60_b04` of the six required constant-floor points is presently available for A2 reuse from accepted core-three. The five baselines registered as structurally dependent on current-route Full81 are `a0.60_b12`, `a0.80_b04`, `a0.80_b12`, `a1.00_b04`, and `a1.00_b12`.

Accordingly, A2 execution depends structurally on a future, separately authorized current-route Full81. This is a dependency, not authorization. Current Full81 is **NOT YET EXECUTED / NOT YET AUTHORIZED**, and the scientific materiality rule must be frozen before Full81.

## 4. Leakage firewall

The directory `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da/`, including `case_matrix.csv`, `surface_summary.csv`, and `surface_summary.json`, is **HISTORICAL V7.2 R9 PROVENANCE**.

Permitted uses are provenance, lineage, and explicitly labeled historical regression context. Prohibited uses are current threshold calibration, current case selection, PASS-rule tuning, and current-v7.4 counterfactual use.

These directories are likewise historical/non-tuning:

- `results/sensitivity/bess_cost_scale_1mw/`
- `results/sensitivity/soc_20_80/`
- `results/sensitivity/winter_pv_17c/`

Accepted EOB and core-three results are already visible information. They may anchor identity and field semantics, but they must not tune the scientific materiality threshold. No numerical threshold option is proposed in this candidate.

## 5. Data-role boundaries

The following roles remain distinct and must not be collapsed:

- `OBSERVED_HISTORICAL`: measured evidence in its accepted observational role, not the planning input.
- `RECONSTRUCTED_PLANNING`: the sole planning identity, `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`, SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`, 8760 rows.
- `HISTORICAL_VALIDATION_PROVENANCE`: historical v7.2 Full81, historical sensitivity runs, and zero-winter evidence.
- `ROBUSTNESS_COUNTERFACTUAL`: a future controlled variable-floor comparison using the same accepted planning identity.
- `DIAGNOSTIC_ONLY`: numerical, solver, and linear-throughput diagnostics that cannot become scientific decision rules without separate authority.

Hybrid routing is prohibited. Historical v7.2 Full81 is not a current counterfactual. Zero-winter remains historical validation/provenance under v7.4; it is already closed, out of scope, requires no new solve, and has no substitute.

## 6. Robustness dimension register

| Dimension | Registered status |
|---|---|
| A2 reserve-floor | `IN_SCOPE / LOCKED`; execution not authorized |
| BESS 1 MW cost package | Framework minimum-list item; historical v7.2-route execution exists; current-route obligation `UNRESOLVED` |
| SOC 20–80 | Framework minimum-list item; historical v7.2-route execution exists; current-route obligation `UNRESOLVED` |
| Rainflow / DOD validation | `MANDATORY / IN_SCOPE / POST-PROCESSING` for future authorized final solutions |
| Linear throughput | `DIAGNOSTIC_ONLY`; not a second mainline |
| Outage recovery-envelope expansion | `CONDITIONAL`; current condition unmet unless primary evidence proves otherwise |
| Efficiency robustness | `REVIEWER-CONDITIONAL / OUT_OF_SCOPE` |
| Zero-winter | `ALREADY_CLOSED / OUT_OF_SCOPE / NO SUBSTITUTE` |
| Discount-rate sweep | `OUT_OF_SCOPE` |
| 24h beta boundary | `DEFERRED / OUT_OF_SCOPE` |
| Solver-parameter sensitivity | `NOT_AUTHORIZED` scientifically; `DIAGNOSTIC_ONLY` if separately authorized |
| Layer B dimensions | `OUT_OF_SCOPE` |

No additional robustness dimension is created here.

## 7. Metric partition and technical gates

The metric list preregisters extraction and reporting fields; it does not settle the materiality decision function.

### Primary decision outputs

- Battery nameplate capacity: `result.json:sizing.E_N_kwh`, battery-side kWh.
- Battery power rating: `result.json:sizing.P_B_kw_ac`, AC/PCS-side kW.

For both, paired variable-floor minus constant-floor outputs must be retained. Whether the future rule uses either or both, and whether it uses a relative or absolute difference, remains unresolved.

### Secondary explanatory outputs

- `result.json:objective_ntd2023_per_year`, constant NTD-2023/year.
- `result.json:sizing.CC_regular_kw`, AC-side kW.
- `result.json:annual_energy.*`, with the AC/battery-side boundary stated by each field name.
- `result.json:cost_components_ntd2023_per_year.*`, constant NTD-2023/year.
- `result.json:layer_a_resilience.*`, including battery-side reserve kWh and AC-side power adequacy kW.
- `mandatory_audits.json:rainflow.summary.*`, including cycle-depth, equivalent-cycle, and PWL/rainflow cost fields.

### Diagnostic outputs

- `mip_gap`, runtimes, node/iteration counts, and `physical_diagnostics.*`.
- Billing, transition-settlement, and cost-reconciliation residuals.
- Linear-throughput benchmarking, if separately authorized, remains diagnostic only.

### Provenance-only outputs

- Paths, hashes, byte counts, run/input/authority identities.
- Historical v7.2 R9 surface values, which remain inside the leakage firewall.

Layer B `ENS`, `nENS`, `WHS`, and `WHSR` must not be imported into Layer A robustness decision rules.

Every future result must be `OPTIMAL`, have a solution, have a finite objective, satisfy `mip_gap <= 1e-6`, and pass all mandatory Layer A audits: solver, physical, resilience, billing, transition, cost, degradation, and rainflow. Existing resilience, rainflow/PWL numerical-equivalence, billing, settlement, physical, and cost invariants remain binding.

Frozen tolerances are reused exactly: MIP gap `1e-6`; simultaneous charge/discharge `1e-5 kW`; transition overage `1e-6 kW`; balance `1e-5`; transition-rate equality `1e-9 NTD-2023/(kW-month)`; cost reconciliation `1e-3 NTD`; and the accepted rainflow/PWL numerical cost-equivalence tolerance `0.05 NTD`. This candidate creates no new technical tolerance. Passing technical gates is necessary but does not establish scientific non-materiality.

## 8. Scientific materiality status

`THRESHOLD_DECISION_REQUIRED_BEFORE_EXECUTION`  
`authority_status = UNRESOLVED_BY_CURRENT_AUTHORITY`

There is no accepted numerical threshold in this candidate. The future adjudication must freeze:

- metric or metrics;
- unit;
- denominator;
- relative versus absolute form;
- trigger value;
- sign/direction;
- equality/tie treatment; and
- beta=8 extension trigger semantics.

No implicit zero threshold, rounding-derived threshold, solver tolerance, historical variation, or inspection of accepted EOB/core-three/historical Full81 may be treated as the scientific rule.

## 9. Unresolved register U-01 through U-07

### U-01 — material difference/material shift

- **Issue:** Numerical definition of material difference/material shift.
- **Primary evidence:** Framework v7.4 §16.1 requires a material shift before beta=8 extension and refers to materially changed sizing, but gives no complete numerical rule.
- **Status:** `UNRESOLVED_BY_CURRENT_AUTHORITY`.
- **Blocks:** A2 PASS/extension logic, Full81 authorization, and A2 execution.
- **Does not block:** Candidate documentation or independent read-only audit.
- **Required adjudication:** A named scientific owner must freeze every component listed in §8 before execution.
- **Prohibited inference:** No threshold may be inferred from solver tolerance, zero difference, historical dispersion, visible results, or an unstated percentage.

### U-02 — outcome/escalation taxonomy

- **Issue:** Scientific outcome and escalation taxonomy beyond existing protocol vocabulary.
- **Primary evidence:** Framework v7.4 states stable-stop versus material-shift conditional extension; the provenance protocol does not define a complete A2 outcome taxonomy.
- **Status:** `UNRESOLVED_BY_CURRENT_AUTHORITY`.
- **Blocks:** Machine-actionable scientific outcome labels and escalation mapping.
- **Does not block:** Recording or auditing the locked case set.
- **Required adjudication:** Owner-approved mapping for technical invalidity, non-material stability, material shift, and conditional beta=8 extension.
- **Prohibited inference:** Do not invent or self-accept new scientific PASS/FAIL/ESCALATE meanings.

### U-03 — historical cost/SOC sufficiency

- **Issue:** Whether historical v7.2-route BESS-cost and SOC20–80 results satisfy v7.4's sensitivity obligation.
- **Primary evidence:** Framework v7.4 lists both as minimum items, and historical directories exist, but no current authority adjudicates current-route sufficiency.
- **Status:** `UNRESOLVED_BY_CURRENT_AUTHORITY`.
- **Blocks:** Claiming the current obligation satisfied or claiming reruns are required.
- **Does not block:** Preserving and labeling historical evidence as non-tuning provenance.
- **Required adjudication:** Independent owner decision on reuse versus current-route execution.
- **Prohibited inference:** Neither automatic sufficiency nor automatic rerun requirement may be inferred.

### U-04 — non-A2 case universe

- **Issue:** Case universe for robustness dimensions other than locked A2.
- **Primary evidence:** Framework v7.4 locks six A2 points but not a complete case universe for the other dimensions.
- **Status:** `UNRESOLVED_BY_CURRENT_AUTHORITY`.
- **Blocks:** Non-A2 execution scope and solve counts.
- **Does not block:** The six-case A2 design or its audit.
- **Required adjudication:** Freeze each separately authorized non-A2 case universe before execution.
- **Prohibited inference:** Do not copy historical, core-three, or Full81 case universes into another dimension without authority.

### U-05 — output namespace / selected_scope

- **Issue:** Robustness output namespace and `selected_scope` identity.
- **Primary evidence:** `PRODUCTION_CASE_SETS` has no robustness scope, and no accepted Task 3 scientific-output namespace exists.
- **Status:** `UNRESOLVED_BY_CURRENT_AUTHORITY`.
- **Blocks:** Writing scientific outputs and production invocation.
- **Does not block:** This documentation-only provenance namespace.
- **Required adjudication:** Approve a collision-free namespace, scope identity, manifest semantics, and retention rules.
- **Prohibited inference:** Do not overload EOB, core-three, historical Full81, current Full81, or another existing scope.

### U-06 — v7.4 identities absent from live authority bundle

- **Issue:** Framework v7.4 and Registry v7.4 identities are absent from the current pre-execution authority bundle.
- **Primary evidence:** `src/production_input_authority_v7_3.py:AUTHORITY_FILES` still pins Framework v7.3, Registry v7.3 R3, and the v7.3 lifecycle closure.
- **Status:** `UNRESOLVED_IMPLEMENTATION_AUTHORITY_ALIGNMENT`.
- **Blocks:** A claim that Task 3 production execution passed a v7.4-aware live authority gate.
- **Does not block:** Candidate authoring or independent audit.
- **Required adjudication:** Separately authorized production-authority re-freeze before production execution.
- **Prohibited inference:** Never weaken, bypass, hand-patch, or reinterpret the authority guard.

### U-07 — variable-floor implementation classification

- **Issue:** Whether implementing the perfect-information variable floor is already-authorized robustness implementation or a methodology addition.
- **Primary evidence:** Framework v7.4 scientifically authorizes A2, while `src/annual_design_model_v7_2.py` implements only one scalar `reserve_kwh_battery` floor applied at every hour.
- **Status:** `UNRESOLVED_CLASSIFICATION`.
- **Blocks:** Coding and its acceptance/audit route.
- **Does not block:** Recording the accepted design and implementation gap.
- **Required adjudication:** Methodology and implementation owners must classify the change before code is written.
- **Prohibited inference:** Scientific authorization of the comparison is not, by itself, authorization to alter equations or production code.

No U-item is resolved by this candidate.

## 10. Implementation readiness

- Task 3 documentation: `READY_AS_IS`.
- A2 robustness execution: `SUBSTANTIAL_IMPLEMENTATION_REQUIRED`.

Known blockers, recorded but not fixed:

1. No robustness scope exists in `PRODUCTION_CASE_SETS`.
2. No perfect-information variable reserve-floor implementation exists.
3. Framework v7.4 and Registry v7.4 are not yet included in the live pre-execution authority bundle.

No code, data, model, equation, parameter, solver setting, handoff, accepted result, or authority artifact was changed.

## 11. Units, scale, and AC/DC boundaries

- `E_N_kwh`: nameplate battery-side energy.
- `e_t`: battery-side stored energy.
- `P_B_kw_ac`: AC/PCS-side power.
- `p_ch` / `p_dis`: AC/PCS-side power.
- `R(alpha,beta)`: battery-side kWh; `eta_d` is accounted for exactly once.
- `P_out`: AC-side kW.
- `C_rep`: DC Storage Block basis.
- Monetary basis: constant NTD-2023.

These boundaries must remain explicit in every future paired comparison.

## 12. Solver policy

Current settings remain frozen: binary mode, `MIPGap=1e-6`, `NumericFocus=1`, `OutputFlag=0`, `TimeLimit=null`, `MIPFocus=0`, and `Threads=0`. Solver-parameter sensitivity is not an authorized scientific dimension. There is no automatic retry with altered parameters and no requirement for bitwise cross-machine equality. Future comparisons must use frozen numerical tolerances.

## 13. Full81 authorization boundary and lifecycle

The required order is:

`Candidate R1 authoring`  
→ `independent read-only preregistration audit`  
→ `separate acceptance closure if PASS`  
→ `final cross-document alignment audit`  
→ `production-authority re-freeze if required`  
→ `separately authorized Full81`

Candidate creation does not authorize Full81. Candidate acceptance alone does not automatically authorize Full81.

## 14. Package and non-mutation statement

The companion namespace is `results/provenance/layer_a_robustness_preregistration_candidate_r1/`. It contains the machine-readable preregistration record, source artifact inventory, exact Git state snapshot, and non-circular package manifest. The manifest deliberately omits its own hash and byte count.

The pre-write repository state was branch `thesis-v7`, HEAD/local origin/live remote `a96cf7929b84374c8e3d5a62a3fed84093268b2c`, ahead/behind `0/0`, staged `0`, tracked dirty `0`, with eight pre-existing untracked paths. The Git snapshot preserves the exact porcelain bytes and records the post-write path set. Protected authority, closure, planning, implementation, EOB, core-three, and historical Full81 identities are inventoried for before/after verification.

## 15. Execution counters

All are zero: model constructions, `optimize()` calls, MILP solves, EOB reruns, core-three reruns, historical Full81 reruns, current Full81 runs, robustness solves, sensitivity solves, implementation changes, code changes, data changes, commits, pushes, and tags.

## 16. Disposition and next legal step

This authoring pass returns **CANDIDATE_R1_PASS** because the bounded candidate package exists and is internally eligible for review. That verdict does not resolve U-01 through U-07 and is not acceptance or closure.

The only next legal step is a **fresh-session independent read-only preregistration audit by a different agent**. Do not accept, commit, push, tag, implement robustness, resolve U-01 through U-07, or run Full81.
