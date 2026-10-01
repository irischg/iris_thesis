# V7.4 Results & Managerial-Insight Analysis Plan — Candidate R2 (bounded correction)

**Project:** Iris Thesis  
**Date:** 2026-10-01  
**Package identity:** `V7_4_RESULTS_MANAGERIAL_INSIGHT_ANALYSIS_PLAN_CANDIDATE_R2`  
**Status:** **CANDIDATE R2 — NOT ACCEPTED / NOT EXECUTION AUTHORITY**  
**Role:** Additive results-analysis and interpretation preregistration  
**Predecessor:** Candidate R1 — **IMMUTABLE PROVENANCE** (`docs/checkpoints/v7_4_results_managerial_insight_analysis_plan_candidate_r1.md`; 15,477 bytes; SHA-256 `57fc4ac6fd13bd88f94251e7252bf7f4e44a65c52cead815f5f5b766ec1e93dd`)  
**Methodology authority:** Framework v7.4 — `docs/research_framework_v7_4_2026-09-26_r2.md` (SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273`; `CLOSED / ACCEPTED`)  
**Evidence authority:** Registry v7.4 — `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` (SHA-256 `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433`; `CLOSED / ACCEPTED`)  
**Pipeline:** V7.4 CURRENT ACCEPTED ROUTE  
**Base HEAD observed at authoring:** `243cfd3ca1394a1bed5283fa127e7a74a33d25a6` (branch `thesis-v7`) — an observation at this authoring moment, not a permanent claim; re-derive live before relying on it.  
**Authoring disposition:** `CANDIDATE_R2_AUTHORED` — bounded correction-package completeness only. **Not** scientific acceptance, **not** governance acceptance, **not** execution authority.

---

## 0. Purpose and authority boundary

This document preregisters how the accepted v7.4 experimental outputs should be analyzed and interpreted after lawful numerical execution.

Its purpose is to prevent post-hoc result storytelling and to ensure that the thesis extracts defensible managerial and scientific insight rather than merely reporting optimization outputs case by case.

This document does **not**:

- modify Framework v7.4;
- modify Registry v7.4;
- alter any CLOSED / ACCEPTED methodology;
- alter the accepted \(\alpha\)–\(\beta\) case universe;
- alter the constant reserve-floor mainline;
- alter the accepted A2 robustness case set;
- introduce forecasting, MPC, stochastic optimization, or a new EMS controller;
- authorize current-route Full81;
- authorize A2 execution;
- authorize robustness implementation;
- authorize a production gate;
- authorize a production-authority re-freeze;
- define any currently unresolved U-item by implication;
- narrow, reduce, or substitute for Framework v7.4 §8.2's required output matrix or §8.3's required figure set;
- define any sizing-percentage denominator;
- create any quantitative knee, threshold, or optimum criterion;
- add any sensitivity or robustness dimension;
- create any resilience-benefit, outage-value, reliability-value, or utility function;
- create or alter any machine-readable record, manifest, provenance namespace, code path, test, solver setting, data artifact, or accepted result.

A result-analysis plan is not numerical-execution authority.

A PASS of this document does not authorize any solve.

### 0.1 Governance-representation neutrality (U-06 / U-07)

At the time of authoring, two representations of U-06 / U-07 state exist and are **not** reconciled here:

1. a working/session-level representation in which a bounded U-06 adjudication has occurred and U-07 has been adjudicated as `METHODOLOGY_GAP` while remaining **OPEN / NOT CLOSED**;
2. the live repository authority at the base HEAD above, in which `CURRENT_STATE.md`, `PROJECT_HANDOFF.md`, and Task 3 Candidate R2 §12 record `U-06 = UNRESOLVED_IMPLEMENTATION_AUTHORITY_ALIGNMENT` and `U-07 = UNRESOLVED_CLASSIFICATION`.

**This document does not resolve, reconcile, adjudicate, or overwrite either representation, and must not be cited as evidence for either.** It is written to remain lawful under **both**: it specifies no U-07 content whatsoever (§9, §10), asserts no production-authority or re-freeze state, and treats every U-item as unresolved for all purposes within this plan. Reconciliation is a separate, separately authorized governance action.

### 0.2 Candidate R1 lifecycle and correction boundary

Candidate R1 is **immutable provenance**. It was not edited, normalized, regenerated, renamed, deleted, promoted, or back-patched by this pass. Its authoring-time wording is preserved exactly as published.

Candidate R2 is a **bounded correction / hardening** pass over Candidate R1. It does not redesign the document. Candidate R1's structure, section order, and analytical intent are preserved except where a change is required by:

- **A** — a required correction identified by the independent read-only audit of Candidate R1 (verdict `PASS_WITH_WORDING_CORRECTIONS`);
- **B** — an accepted-authority clarification (Framework v7.4 / Registry v7.4 / Task 3 Candidate R2); or
- **C** — a strictly necessary consistency fix caused by **A** or **B**.

No other change class is introduced. No analysis is added because it appeared academically attractive. No equation is introduced that is not already present in accepted authority and necessary to remove an ambiguity identified in Candidate R1.

### 0.3 Bounded R1 → R2 correction register

| ID | Bounded correction | Class |
|---|---|---|
| `R2-W01` | Scope the research-question restatement: this plan covers Layer A / Full81 results under the RQ1–RQ2 lens and does not replace or narrow Framework §1.1 or RQ3/RQ4. | A |
| `R2-W02` | Remove the colloquial use of "material" as a selector of which assumptions to test. | A |
| `R2-W03` | Harden the historical-result firewall from "not silently substituted" to "not current-v7.4 scientific evidence at all". | A |
| `R2-W04` | State that the annual regular contract capacity \(CC\) is always present in the Layer A mainline (A3), rather than "where applicable". | A |
| `R2-W05` | Apply accepted notation and unit semantics: \(E^N\) / \(E^U\) / \(e_t\), \(P^B\), \(R(\alpha,\beta)\), \(P^{out}\), \(\eta_d\) exactly once. | A |
| `R2-W06` | Name the accepted comparison baseline (EOB) explicitly; retain Premium% only where Framework §6 defines its denominator; do not report \(\%\Delta E^N\) or \(\%\Delta P^B\). | A |
| `R2-W07` | State the marginal-cost normalization and units; preserve Framework §8.4's per-step reporting quantity and forbid interchanging it with a per-unit-\(\alpha\) quotient. | A |
| `R2-W08` | Remove every formulation implying a resilience-benefit, outage-value, or benefit-per-cost quantity. | A |
| `R2-W09` | Distinguish prohibited post-hoc threshold creation from the already-authorized Framework §8.5 / §9.2 post-Layer-A knee / no-knee determination. | A |
| `R2-W10` | Record that Framework §7.5's "loss of normal economic dispatch freedom" is not an independently emitted cost component. | A |
| `R2-W11` | Record that Framework Chapter 5's conditional decision rules and §8.6's optional simplified quoting rule remain authorized deliverables. | A |
| `R2-W12` | Bind "oracle" as an informal synonym only, defining none of the U-07 elements. | A |
| `R2-W13` | State that the A2 outcome interpretations are not the U-02 outcome/escalation taxonomy. | A |
| `R2-W14` | Disambiguate the A2 robustness screen (Framework §16.1) from CLOSED decision A2 (Framework §0.1). | A |
| `R2-W15` | Scope the forecasting boundary to the Layer A reserve-floor formulation, preserving Framework §10.7's optional Layer B comparator. | A |
| `R2-W16` | State that no sensitivity or robustness dimension is added and that U-03 / U-04 remain unresolved. | A |
| `R2-W17` | Add an explicit non-derogation clause for Framework §8.2 / §8.3, naming the outputs that must not be dropped. | A |
| `R2-W18` | Rename the claim category "Observed numerical fact" and add the model-conditional epistemic boundary. | A |
| `R2-W19` | Label the analysis success criteria as thesis-writing / analysis-quality criteria only. | A |
| `R2-W20` | State that numerical tolerance fields are not the U-01 scientific materiality rule. | A |
| `R2-W21` | Close the "optimal if an explicit decision criterion exists" loophole. | A |
| `R2-N01` | Add §0.1 governance-representation neutrality. | C |
| `R2-N02` | Add §0.2 / §0.3 lifecycle, correction boundary, and bounded correction register, following the structure of the accepted Task 3 Candidate R2. | C |
| `R2-N03` | Record, without resolving, the implementation / output-schema aggregation observation (§16). | A |
| `R2-N04` | Renumber R1 §16 (Governance status) to §17 to accommodate §16. | C |

---

# 1. Primary research interpretation

## 1.1 Scope of this analysis plan

This plan covers the interpretation of **Layer A / Full81 results** (and, where separately authorized, the A2 reserve-floor robustness screen of Framework §16.1).

Its operative interpretation lens is **Framework v7.4 RQ1 and RQ2**:

- **RQ1** — the cost–resilience response surface: how BESS energy capacity, power capacity, contract capacity, annualized total cost, and resilience premium change when \((\alpha,\beta)\) service-continuity requirements are added;
- **RQ2** — the structural mechanism: which requirement drives energy versus power, and which cost channel generates the premium.

This plan does **not** replace, narrow, supersede, or re-scope:

- Framework §1.1's full core question, which also covers when a fixed design fails under PV deterioration and demand growth, and how cost trades against onsite CO\(_2\) under a hypothetical DG extension;
- **RQ3** — fixed-design off-design capability (Layer B);
- **RQ4** — the DG-assisted counterfactual.

**RQ3 and RQ4 remain fully in force under Framework §2 and are unchanged by this document.** No research question is redefined here. Sections of the thesis governed by RQ3 and RQ4 are outside this plan's scope and retain their own Framework-defined requirements (Framework §9–§15, §25 Phases 3–5).

## 1.2 Interpretation within scope

For the results within scope, the main question is not:

> Which \(\alpha\)–\(\beta\) case is "best"?

Nor is the contribution merely:

> Running a large number of optimization cases and reporting their optimal ESS sizes and costs.

The intended interpretation is:

> **How does incorporating service-continuity / resilience requirements into annual ESS planning change optimal battery sizing and economic performance, and what resilience–cost trade-offs are relevant to planning and managerial decision-making?**

The experimental analysis therefore focuses on:

1. the additional ESS capacity associated with stronger resilience requirements;
2. the corresponding economic premium;
3. the marginal cost of increasing resilience;
4. nonlinearities, transition regions, and diminishing-return behavior in the **cost** response;
5. the mechanisms responsible for these changes;
6. the sensitivity of managerial conclusions to the assumptions that fall within the authorized sensitivity / robustness scope (Framework §16.1 as registered in Task 3 Candidate R2 §9) — see §11.

No case may be described as globally "optimal," "best," or "recommended" solely because it has the lowest objective value among the evaluated cases. Cases at stronger requirements are strictly more constrained by the accepted reserve and power-adequacy constraints (Framework §7.3–§7.5), so ordering cases by objective value is not a preference-free ranking; Framework §8.5 states directly that absent a knee there is no preference-free natural optimal service level.

---

# 2. Mainline 81-case analytical role

The accepted Full81 case universe is treated as a structured response surface over the accepted resilience dimensions, consistent with Framework §16.1, which designates the \(\alpha\times\beta\) 81-point grid as the core planning response surface rather than a sensitivity analysis.

The purpose of the Full81 analysis is not merely to rank 81 solutions.

It is to characterize how the planning solution changes across resilience requirements.

## 2.1 Per-case reporting floor

For each lawful current-route case, analysis should distinguish **at minimum**:

- the resilience requirement \((\alpha,\beta)\);
- nameplate battery-side ESS energy capacity \(E^N\) (kWh);
- AC/PCS-side ESS power capacity \(P^B\) (kW);
- the annual regular contract capacity \(CC\) (kW) — a single annual decision variable always present in the Layer A mainline under A3 (CLOSED);
- the annualized economic objective (constant NTD-2023 per year);
- the accepted cost components (§6);
- the energy reserve requirement \(R(\alpha,\beta)\) (battery-side kWh, with \(\eta_d\) accounted exactly once) and the instantaneous power requirement \(P^{out}(\alpha)\) (AC-side kW);
- technically binding or economically active mechanisms where supported by accepted outputs.

**This list is a reporting floor, not a ceiling, and it does not replace Framework §8.2's required output matrix.** Framework §8.2 remains binding in full, including its exact ex-post demand diagnostics, degradation diagnostics, realized SOC range, ex-post rainflow cycle-depth summary, reserve-floor binding frequency / normal-operation SOC headroom, binding critical window, and solver reporting. Nothing in this plan authorizes omitting any §8.2 item.

## 2.2 Current-versus-historical result identity

Only accepted current-route outputs may be used for current-v7.4 scientific interpretation.

**Historical Full81 outputs are not current-v7.4 scientific evidence — neither silently nor with explicit labeling.** Per Task 3 Candidate R2 §7, permitted uses of historical Full81 and historical sensitivity results are limited to:

- provenance;
- lineage;
- explicitly labeled historical regression context.

Historical numerical outcomes must **not** be used for:

- threshold selection;
- materiality calibration;
- PASS-rule tuning;
- current A2 case selection;
- current-v7.4 counterfactual interpretation;
- managerial recommendation tuning.

The historical v7.2 Full81 production execution is immutable historical provenance and is not a controlled current-route counterfactual. Accepted EOB and accepted core-three results are visible information that may anchor identity and field semantics, but may not tune any threshold or rule.

---

# 3. Analysis Axis A — Absolute resilience premium

For each resilience case, quantify the incremental planning consequence relative to the accepted economic-only baseline (EOB), which Framework §6 establishes as the comparison basis for all resilience premium.

Reported absolute differences:

\[
\Delta E^N(\alpha,\beta)=E^N(\alpha,\beta)-E^N_{EOB}
\quad\text{[kWh, nameplate battery-side]}
\]

\[
\Delta P^B(\alpha,\beta)=P^B(\alpha,\beta)-P^B_{EOB}
\quad\text{[kW, AC/PCS-side]}
\]

\[
\Delta C(\alpha,\beta)=C(\alpha,\beta)-C_{EOB}
\quad\text{[constant NTD-2023 per year]}
\]

Percentage change is reported **only** where accepted authority defines the denominator. Framework §6 defines exactly one such quantity:

\[
Premium\%(\alpha,\beta)=\frac{\Delta C(\alpha,\beta)}{C_{EOB}}\times100\%.
\]

**No accepted authority defines a denominator for sizing percentages.** Accordingly, \(\%\Delta E^N\) and \(\%\Delta P^B\) are **not** reported under this plan. Sizing changes are reported as absolute differences in kWh (nameplate battery-side) and kW (AC/PCS-side). A sizing-percentage quantity may only be introduced if a denominator is separately accepted through a lawful future mechanism; **this document does not create, propose, or select such a mechanism.**

The interpretation should answer:

> How much additional storage capacity and annualized cost are associated with providing the specified level and duration of service continuity?

Absolute differences and percentage differences must not be conflated, and the monetary basis (constant NTD-2023) must be stated wherever a monetary quantity is reported.

---

# 4. Analysis Axis B — Marginal resilience cost

The analysis should evaluate not only total cost but the incremental cost of strengthening the resilience requirement: changes along the accepted \(\alpha\) dimension while holding \(\beta\) fixed, and changes along the accepted \(\beta\) dimension while holding \(\alpha\) fixed.

## 4.1 Accepted grid steps

On the accepted analysis domain (Framework §3.4), the grid steps are:

\[
\Delta\alpha=0.05\ (\text{= 5 percentage points}),
\qquad
\Delta\beta=1\ \text{h}.
\]

## 4.2 Reported quantity and normalization

Framework §8.4 defines the marginal-change forms:

\[
MC_\alpha(\alpha,\beta)\approx\frac{C(\alpha+\Delta\alpha,\beta)-C(\alpha,\beta)}{\Delta\alpha},
\qquad
MC_\beta(\alpha,\beta)\approx\frac{C(\alpha,\beta+\Delta\beta)-C(\alpha,\beta)}{\Delta\beta},
\]

and requires reporting the cost associated with **one +0.05 \(\alpha\) step (5 percentage points)** and the cost associated with **one +1 h \(\beta\) step**, together with whether marginal cost is increasing, decreasing, or approximately constant.

The reported quantities are therefore the per-step cost changes:

\[
C(\alpha+0.05,\beta)-C(\alpha,\beta)
\quad\text{[constant NTD-2023 per year, per +0.05 }\alpha\text{ step]}
\]

\[
C(\alpha,\beta+1\,\text{h})-C(\alpha,\beta)
\quad\text{[constant NTD-2023 per year, per +1 h }\beta\text{ step]}
\]

**Normalization must be stated explicitly wherever these quantities appear.** The difference-quotient forms above carry different units and, for \(\alpha\), a different magnitude: dividing by \(\Delta\alpha=0.05\) rescales the \(\alpha\) quantity by a factor of 20 and converts it to "per unit \(\alpha\)". A per-unit-\(\alpha\) quotient must **never** be reported as, labelled as, or interchanged with Framework §8.4's per-+0.05-step reporting quantity. For \(\beta\), dividing by \(\Delta\beta=1\) h leaves the magnitude unchanged but changes the unit to "per hour"; the unit must still be stated.

These quantities are descriptive finite differences over the accepted experimental grid. They must not be interpreted as continuous derivatives.

The analysis should determine whether the cost of resilience is approximately proportional or whether stronger resilience requirements become progressively more expensive.

---

# 5. Analysis Axis C — Nonlinearity and transition regions

The Full81 response surface should be inspected for systematic changes in slope or behavior of the **cost** response.

Candidate phenomena include:

- accelerating cost growth;
- diminishing returns in the sense of a decelerating **capacity or cost** response to successive equal requirement steps;
- rapid ESS-energy expansion;
- rapid PCS-power expansion;
- changes in the dominant economic mechanism;
- regions in which a one-step increase in the specified \(\alpha\) or \(\beta\) target is associated with a disproportionately large increase in annualized cost.

## 5.1 No benefit or value quantity exists

\(\alpha\) and \(\beta\) are **decision-maker-specified service-continuity / resilience requirements** (Framework §3.2, §3.3), not endogenous model outputs and not measures of delivered benefit. The accepted model contains:

- no resilience-benefit function;
- no outage-value or value-of-lost-load quantity;
- no reliability-value or utility function;
- no outage probability distribution, Monte Carlo reliability probability, or component forced-outage probability (excluded by Framework §3.1);
- no internal determination of the value of resilience.

Consequently the analysis **must not** compute, report, or imply any benefit-per-cost ratio, cost-effectiveness ratio, or "additional resilience per unit cost" quantity unless such a quantity is separately authorized through a future methodology process. This plan does not authorize one.

Permitted statements concern the **cost** response to a specified requirement step: cost change per step, nonlinear cost response, disproportionate cost increases, and regional slope changes.

## 5.2 A visible bend is not a threshold

A visually apparent bend is **not automatically a formal threshold or optimum**.

Unless a threshold criterion has been preregistered and scientifically justified independently of observed result magnitudes, the thesis should use language such as:

- transition region;
- region of accelerated cost growth;
- nonlinear response;
- change in marginal cost;

rather than claiming a mathematically identified "optimal threshold."

**This document creates no quantitative knee, threshold, or optimum criterion.** It also does not suspend the determination Framework already requires: Framework §0.2 defers to after Layer A completion the question of whether a knee / transition region exists, Framework §8.5 governs how that determination is reported (knee region rather than a single point; no force-finding a knee; no-knee as a formal result; knee robustness checked against the accepted BESS cost sensitivity), and Framework §9.2 governs the Layer B benchmark-selection branch under a rule frozen in advance. Those determinations are qualitative and regional, are made lawfully after observing Layer A results, and are **not** thresholds within the meaning of §12.

No post-hoc threshold may be selected merely because it produces a convenient managerial story.

---

# 6. Analysis Axis D — Cost decomposition and mechanism explanation

A difference in total annualized cost should not be treated as sufficient explanation.

Where accepted model outputs permit, the analysis should determine which components account for the observed change.

The accepted cost components, as defined by Framework §7.8 and required as a decomposition by Framework §8.2, are:

- annualized BESS capital cost, reported with its accepted energy-capacity and power-capacity split;
- BESS fixed O&M (FOM);
- grid TOU energy charge;
- contract-capacity basic charge;
- Taipower period-specific non-duplicative over-contract penalties;
- cycling degradation economic wear.

## 6.1 Component boundaries

- **Over-contract penalties may have distinct accepted subcomponents** (pure-season and transition-resolved settlement). Where the accepted output distinguishes them, they must not be silently collapsed into a single undifferentiated quantity, and the transition component's accepted claim boundary must be preserved.
- **Framework §7.5's third premium channel — the loss of normal economic dispatch freedom caused by the reserve floor — is not an independently emitted cost component.** It must not be presented as though it were a directly measured objective component. It may be discussed only as the net change across the operating components, with that status stated.
- **Framework §28.2's caution remains in force:** the claim that the premium is "almost pure CAPEX" must be demonstrated by formal cost decomposition and must not be inferred from a TOU-cost decrease alone.
- No new decomposition, component, or allocation rule is invented here. The accepted objective structure (B2, CLOSED) is unchanged.

The objective is to distinguish:

> **what changed**

from:

> **why it changed.**

Claims about mechanisms must be supported by accepted output quantities or additional lawful diagnostic analysis.

No causal mechanism should be inferred solely from correlation between two result columns.

---

# 7. Analysis Axis E — Energy-versus-power sizing behavior

ESS energy capacity and PCS power capacity represent different planning requirements and must not be collapsed into a single "battery size" statement.

## 7.1 Required quantity distinctions

The analysis must keep the accepted quantities distinct and labelled (Framework §5.1, §5.2; Task 3 Candidate R2 §14):

- \(E^N\) — installed/nameplate BESS energy capacity (kWh), battery-side; the energy sizing decision variable and the energy CAPEX basis;
- \(E^U\) — derived usable energy within the SOC operating window (kWh); not an independent sizing variable;
- \(e_t\) — actual stored battery energy (kWh); the primary physical state;
- \(P^B\) — BESS charge/discharge power rating (kW), AC/PCS-side;
- \(R(\alpha,\beta)\) — the energy reserve requirement above technical \(SOC_{min}\), in battery-side kWh, with \(\eta_d\) accounted **exactly once**;
- \(P^{out}(\alpha)\) — the instantaneous power requirement, AC-side kW.

No reported quantity may silently mix nameplate with usable energy, battery-side with AC/PCS-side quantities, or apply \(\eta_d\) more than once.

## 7.2 Mechanism question

The analysis should examine whether increasing \(\alpha\) or \(\beta\) primarily affects:

- energy capacity;
- power capacity;
- both;
- or neither to a degree detectable above the accepted frozen numerical tolerances — with any formal materiality classification deferred to the separately accepted materiality rule (§11).

This distinction should be interpreted physically.

For example, longer service duration may create a different sizing pressure from higher instantaneous service requirements.

However, the thesis must derive the actual mechanism from accepted model structure and results rather than assuming such behavior in advance. RQ2 poses this as an open question and it must be answered, not presupposed.

---

# 8. Analysis Axis F — Managerial decision interpretation

The final analysis should translate model outputs into planning-relevant questions.

Examples include:

- What economic premium is associated with moving from a lower to a higher resilience requirement?
- Does the marginal resilience premium remain stable or rise rapidly across successive requirement steps?
- Are there regions where a one-step increase in the specified requirement is associated with a disproportionately large increase in investment or annualized cost?
- Which planning variables are most sensitive to stronger service-continuity requirements?
- Which assumptions within the authorized sensitivity scope affect the planning conclusion, and in what direction?

The thesis should distinguish:

### Scientific result

What the optimization model produces under the accepted assumptions.

### Managerial implication

What that result means for a planner choosing among resilience targets, stated conditionally and with its assumptions explicit.

### Recommendation

A normative statement that may require preferences, budgets, risk tolerance, policy objectives, or other information not contained in the optimization itself.

The first two may be supported directly by the thesis.

The third must not be asserted unless the necessary decision criteria are explicitly available **and were not constructed after observing the results**.

## 8.1 Authorized decision-rule deliverables

The following remain authorized or required by accepted authority and fall under **managerial implication**, not **recommendation**:

- Framework Chapter 5's three to five **conditional** decision rules;
- Framework §8.6's optional simplified quoting rule, which if offered must report the approximation error across the full 81-cell grid rather than only favorable cells.

These are conditional, assumption-explicit statements of what the accepted results imply for a stated requirement, not deployment prescriptions.

## 8.2 Decision-criterion discipline

A decision criterion may not be invented after observing results in order to designate a case "optimal". Any decision criterion used must be:

- external to the optimization;
- stated explicitly, and stated before the claim it supports is made;
- preference-explicit where it depends on preferences, budget, or risk tolerance;
- reported as conditional, with the claim scoped to that criterion.

Consistent with Framework §8.5 and §11.2, the study does not make the final deployment decision for the planner. Results are **modeled planning requirements** under a specified resilience target. The thesis must not claim "NTUST should install X MWh", a recommended campus installation size, a physically deployable capacity, or a site-feasible design, unless separately authorized.

---

# 9. A2 reserve-floor robustness interpretation (Framework §16.1 robustness screen)

**Label disambiguation.** "A2" in this section means the **reserve-floor formulation robustness screen of Framework §16.1**. It does **not** mean CLOSED decision A2 of Framework §0.1, which separates annual optimization from outage replay and fixes the constant worst-case reserve mainline, the outage initial state, the outage technical lower bound, and the outage terminal requirement. CLOSED decision A2 must not be mined for a variable-floor definition, and nothing in this section reopens it.

The accepted §16.1 comparison is:

> constant worst-case reserve floor  
> versus  
> perfect-information time-varying reserve floor.

The screen is a **model-form robustness screen**, not a second research question and not a replacement mainline methodology, and it is locked to the six targeted points recorded in Task 3 Candidate R2 §5.

## 9.1 Status of the perfect-information arm

The perfect-information arm must be interpreted as an:

> **intentionally favorable perfect-information counterfactual used to assess sensitivity to the conservatism of the constant worst-case reserve-floor formulation.**

If the informal term "oracle" is used, it is bound **only** as a colloquial synonym for Framework §16.1's "perfect-information time-varying floor". The term defines **none** of the following, all of which remain entirely outside this document:

- any reserve-floor equation;
- any time-indexed reserve quantity;
- the information window;
- the floor time domain;
- forward, backward, or centered window construction;
- year-start or year-end treatment;
- cyclic treatment;
- replay semantics;
- scalar-to-vector or derived solver bound treatment.

These remain the subject of the unresolved U-07 classification and must not be inferred from this document, from notation, or from any implementation artifact.

The perfect-information arm must **not** be described as:

- a realistic real-time controller;
- a deployable EMS strategy;
- a practical forecast-based reserve policy;
- a claim that future load and PV can be known perfectly.

Registry v7.4 §20.7 records "perfect-information benchmark mislabeled deployable operation" as an excluded claim, and Framework §10.7 forbids presenting perfect-information results as actual operational reliability, real-time robustness, or actual success probability.

## 9.2 The relevant question and its permissible readings

> **Would relaxing the constant worst-case reserve-floor assumption under an intentionally favorable perfect-information counterfactual change the planning conclusion, as judged by the separately accepted materiality rule?**

If the difference is small under that future accepted rule, the permissible interpretation is that the mainline conclusion is comparatively robust to this reserve-floor model-form assumption.

If the difference is classified as material under that future accepted rule, the permissible interpretation is that reserve-floor formulation is decision-relevant **in the sense defined by that rule**, and that practical dynamic-reserve formulations warrant further study.

**These are permissible narrative readings only. They do not constitute the U-02 outcome/escalation taxonomy, which is unresolved and is not resolved here.** Formal materiality remains governed by the future accepted U-01 rule. The only authorized escalation action remains Framework §16.1's conditional \(\beta=8\) extension, and only if a future **frozen** material-shift rule triggers; expansion is not automatic and no rule, threshold, or trigger value is selected here.

A perfect-information result must not be presented as an achievable real-world operational performance level.

---

# 10. Forecasting boundary

**Scope of this boundary: the Layer A reserve-floor formulation.**

Forecast-based dynamic reserve for the Layer A reserve floor is outside the current thesis experimental pipeline unless separately authorized through a future methodology process. The accepted mainline is the constant worst-case reserve floor (A2, CLOSED), and the variable floor exists only as the Framework §16.1 six-point perfect-information model-form screen.

No forecasting subsystem, architecture, or model is added, proposed, or recommended by this analysis plan.

This boundary is deliberate. Adding operational forecasting would introduce additional scientific questions involving, among others:

- forecasting architecture;
- training and validation design;
- forecasting horizon;
- forecast accuracy;
- load/PV information availability;
- forecast error propagation;
- rolling-horizon operation;
- leakage prevention;
- uncertainty treatment.

These questions are not required to answer the current reserve-formulation robustness question.

**This boundary does not remove, narrow, or rewrite anything separately authorized elsewhere.** In particular, Framework §10.7's optional Layer B rolling-horizon or simple rule-based dispatch comparator — an optional enhancement for quantifying perfect-foresight uplift, not a mainline requirement — retains exactly its accepted status, and Framework Chapter 5 retains rolling control as designated future work.

Forecast-based or uncertainty-aware dynamic reserve may therefore be identified as a future operational extension.

This limitation must not be hidden.

---

# 11. Sensitivity and robustness interpretation

Sensitivity analysis should answer:

> **Would a change in an uncertain or modeling assumption, within the authorized sensitivity scope, alter the substantive planning conclusion?**

## 11.1 No sensitivity dimension is added

**This document adds no sensitivity or robustness dimension, case, range, or parameter.** The authorized set remains exactly what is currently accepted by Framework v7.4 §16.1 and registered, dimension by dimension with its status, in Task 3 Candidate R2 §9. Sensitivity runs must not be added solely to increase the number of experiments (Framework §16.3).

`U-03` (historical cost/SOC sensitivity sufficiency) and `U-04` (non-A2 robustness case universes) remain **unresolved** unless current repository authority demonstrates otherwise, and are **not resolved, narrowed, or implied** here. Neither automatic sufficiency nor a mandatory rerun may be inferred from this document.

## 11.2 Interpretation layers

For each authorized sensitivity or robustness test, interpretation should distinguish:

1. whether numerical outputs change;
2. whether the direction of the conclusion changes;
3. whether the managerial implication changes.

## 11.3 Materiality remains unresolved and external to this document

A numerically detectable difference is not automatically a material difference in the scientific sense.

Any formal materiality classification must follow the separately accepted materiality rule. **This document does not create that rule, select any threshold, metric, unit, denominator, relative/absolute form, trigger value, direction, tie treatment, or \(\beta=8\) semantics, and does not resolve `U-01`.** Technical PASS against the accepted frozen tolerances is not scientific non-materiality (Task 3 Candidate R2 §10).

**Numerical tolerance and equivalence fields in the accepted output schema are not the U-01 scientific materiality rule.** Any emitted field whose name resembles a materiality threshold — for example a field named along the lines of `materiality_threshold_for_nonzero_PWL_rainflow_error` in the ex-post rainflow validation summary — is a numerical equivalence/tolerance field governing validator behavior. It must never be cited as, substituted for, or treated as evidence of the unresolved U-01 scientific materiality definition.

---

# 12. Prohibited post-hoc practices

The following are prohibited unless separately preregistered and justified:

- post-hoc creation or tuning of a **decision threshold, materiality threshold, PASS threshold, or scientific-acceptance threshold** after observing results. *This prohibition does not apply to the Framework §8.5 knee / no-knee determination or the Framework §9.2 Layer B benchmark-selection branch, which are qualitative, regional, governed by a rule frozen in advance, and lawfully made after observing Layer A results (see §5.2);*
- changing the analyzed case subset because another subset gives a clearer story;
- redefining "material" after observing effect sizes;
- presenting historical results as current-v7.4 evidence, or using historical outcomes to tune a threshold, a PASS rule, A2 case selection, a counterfactual interpretation, or a managerial recommendation;
- adding a forecast model because the perfect-information result appears unfavorable;
- changing A2 robustness-screen semantics after observing its results;
- choosing sensitivity ranges because they produce desired conclusions, or adding a sensitivity dimension outside the authorized scope;
- claiming causality from output correlation alone;
- computing or implying a resilience-benefit, outage-value, or benefit-per-cost quantity;
- introducing a sizing-percentage denominator that accepted authority does not define;
- labeling one \(\alpha\)–\(\beta\) case "optimal" — including by constructing a decision criterion after observing results, or by applying a criterion that is not external, explicitly stated in advance of the claim, preference-explicit where applicable, and reported as conditional (§8.2);
- hiding null or inconvenient robustness findings.

Null results remain scientific results.

---

# 13. Required figure / table logic

## 13.1 Non-derogation

**This section is additive to, and does not reduce, Framework v7.4 §8.2's required output matrix or §8.3's required figure set.** No Framework-required output or figure may be omitted on the basis of this section, including but not limited to:

- the \(CC\) heatmap;
- the binding-window calendar map;
- the degradation segment utilization / degradation-cost contribution summary;
- the ex-post realized DOD / rainflow depth distribution and PWL-vs-rainflow validation summary;
- the \(E^N\) heatmap, \(P^B\) heatmap, resilience-premium heatmap, marginal-cost heatmap, premium-vs-\(\alpha\), premium-vs-\(\beta\), and premium-decomposition figures.

"Prioritize" in this section means emphasis, sequencing, and main-text-versus-appendix placement. **It never means omitting a required figure or output.**

## 13.2 Presentation families

Within that constraint, the final thesis should foreground figures and tables that reveal decision structure rather than maximize output volume. Candidate presentation families include:

### A. Response surfaces

Show how ESS sizing or annualized cost changes across \(\alpha\) and \(\beta\).

### B. Marginal-change plots

Show finite per-step changes across adjacent resilience levels, with the normalization and units of §4.2 stated on the figure.

### C. Cost decomposition

Show which economic components generate the resilience premium, preserving the component boundaries of §6.1.

### D. Energy-versus-power sizing

Separate \(E^N\) (kWh, nameplate battery-side) and \(P^B\) (kW, AC/PCS-side) responses.

### E. Robustness comparison

Compare accepted mainline results with authorized robustness arms using the same quantity definitions, units, and monetary basis.

Exact main-text placement may depend on accepted result availability.

Figures must not be chosen to conceal unfavorable or null findings.

---

# 14. Claim discipline

The following distinctions must remain explicit.

### Accepted-output fact

A value directly emitted by an accepted current-route artifact.

> **Terminology note.** "Observed" is a reserved term under Framework v7.4 CHANGE B and Registry v7.4 §20.2 / §14, denoting measured historical data in the historical empirical / calibration layer. It must never be applied to a model output. This category is therefore named "accepted-output fact", not "observed numerical fact".

### Derived numerical quantity

Calculated transparently from accepted outputs.

### Model-mechanism interpretation

Supported jointly by accepted equations and numerical outputs.

### Managerial implication

A conditional, assumption-explicit interpretation of the preceding results.

### Speculation / future work

Not established by the present experiment.

These categories must not be collapsed in the thesis narrative.

## 14.1 Epistemic boundary of current-route planning results

Every current-route planning result interpreted under this plan is a **model output**, conditional on the accepted planning inputs — in particular the single accepted reconstructed-PV planning artifact identity recorded in `CURRENT_STATE.md` and Task 3 Candidate R2 §8.

Accordingly, and without weakening Framework v7.4 CHANGE B or any Registry claim boundary:

- reconstructed PV values are model-based, weather-informed, separately validated **planning estimates**;
- they are **not** observed historical PV measurements;
- they are **not** exact ground truth;
- they are **not** an exact recovery of the unavailable historical series;
- they are **not** online forecast information;
- the historical empirical / calibration layer uses observed data wherever valid, the planning / counterfactual layer uses the accepted reconstructed full-year PV, and **no hybrid routing** between the two is used;
- planning and adequacy conclusions therefore remain **model-conditional** and do not establish future-outage reliability or physical islanding capability.

---

# 15. Success criterion for the thesis analysis

**These are thesis-writing / analysis-quality criteria only.** They are **not** technical PASS gates, run-acceptance gates, production gates, governance acceptance gates, or scientific materiality rules, and they add nothing whatsoever to the frozen technical gates, invariants, and tolerances recorded in Task 3 Candidate R2 §10, which remain binding and unchanged.

As a writing criterion, the experimental contribution is not considered complete merely because all optimization cases solve successfully.

A successful analysis should be able to explain:

1. how resilience requirements change ESS sizing;
2. how they change annualized economic performance;
3. how the marginal cost of resilience changes across the experimental space;
4. what physical/economic mechanisms generate those changes;
5. which findings are robust to the accepted, authorized sensitivity checks;
6. which assumptions remain decision-critical, stated conditionally;
7. what a campus energy planner can legitimately learn from these results.

The desired endpoint is therefore:

> **optimization outputs → structured evidence → mechanism explanation → robustness assessment → managerial insight**

rather than:

> **optimization outputs → case ranking.**

---

# 16. Implementation / output-schema observation — recorded, not resolved

The independent audit of Candidate R1 recorded the following observation, which is reproduced here for completeness:

> The accepted per-case outputs support much of the analysis preregistered above, but a current-route Full81 reporting / aggregation layer may still be required in order to produce cross-case response surfaces, resilience-premium tables, marginal-cost grids, and the Framework §8.3 figure set.

Classification: **`IMPLEMENTATION / OUTPUT-SCHEMA GAP`**.

This observation is explicitly **not**:

- a methodology gap;
- a defect in the accepted optimization model;
- a reason to alter the model, objective, constraints, parameters, or solver settings;
- authority to create, modify, or run any code;
- authority to execute Full81;
- authority to perform any new solve;
- authority to re-freeze production authority.

It is recorded and **not resolved**. No aggregation layer is designed, specified, or implemented by this document. Any future reporting/aggregation work requires its own separate authorization and, if it touches production artifacts, its own independent audit.

---

# 17. Governance status

This Candidate R2 is an additive interpretation / analysis-plan candidate only.

It does not supersede or amend Framework v7.4, Registry v7.4, or Task 3 Candidate R2.

It does not close, resolve, narrow, or imply any unresolved U-item, and does not reconcile the governance-representation discrepancy described in §0.1.

It does not authorize implementation or numerical execution.

Candidate R1 remains immutable provenance and was not modified by this pass.

**Execution counters for this authoring pass:** file creations = **1** (this file); authority-file modifications = **0**; code/test/solver/data modifications = **0**; model constructions = **0**; `optimize()` calls = **0**; MILP solves = **0**; EOB reruns = **0**; core-three reruns = **0**; Full81 runs = **0**; A2 / robustness solves = **0**; production gates run = **0**; production-authority re-freezes = **0**; U-items resolved = **0**; commits = **0**; pushes = **0**; tags = **0**.

Before acceptance, this candidate should receive a fresh-session independent read-only audit for:

- consistency with Framework v7.4;
- consistency with Registry v7.4;
- consistency with Task 3 Candidate R2;
- absence of hidden methodology changes;
- absence of post-hoc tuning routes;
- compatibility with the accepted output schema;
- historical-versus-current result separation;
- leakage / look-ahead / information-advantage boundaries;
- claim-to-source discipline;
- authority / provenance integrity;
- faithful and bounded incorporation of the required Candidate R1 corrections, with no change outside the correction classes of §0.2.

Authoring this candidate is not acceptance. An audit PASS would not be self-acceptance, and acceptance would not authorize implementation, Full81, or A2 execution.

**CANDIDATE R2 — NOT ACCEPTED / NOT EXECUTION AUTHORITY.**
