# V7.4 Results & Managerial-Insight Analysis Plan

**Project:** Iris Thesis  
**Status:** CANDIDATE R1 — NOT ACCEPTED / NOT EXECUTION AUTHORITY  
**Role:** Additive results-analysis and interpretation preregistration  
**Methodology authority:** Framework v7.4  
**Evidence authority:** Registry v7.4  
**Pipeline:** V7.4 CURRENT ACCEPTED ROUTE  

---

## 0. Purpose and authority boundary

This document preregisters how the accepted v7.4 experimental outputs should be analyzed and interpreted after lawful numerical execution.

Its purpose is to prevent post-hoc result storytelling and to ensure that the thesis extracts defensible managerial and scientific insight rather than merely reporting optimization outputs case by case.

This document does **not**:

- modify Framework v7.4;
- modify Registry v7.4;
- alter any CLOSED / ACCEPTED methodology;
- alter the accepted α–β case universe;
- alter the constant reserve-floor mainline;
- alter the accepted A2 robustness case set;
- introduce forecasting, MPC, stochastic optimization, or a new EMS controller;
- authorize current-route Full81;
- authorize A2 execution;
- authorize robustness implementation;
- authorize a production gate;
- authorize a production-authority re-freeze;
- define any currently unresolved U-item by implication.

A result-analysis plan is not numerical-execution authority.

A PASS of this document does not authorize any solve.

---

# 1. Primary research interpretation

The main thesis question is not:

> Which α–β case is “best”?

Nor is the contribution merely:

> Running a large number of optimization cases and reporting their optimal ESS sizes and costs.

The intended research interpretation is:

> **How does incorporating service-continuity / resilience requirements into annual ESS planning change optimal battery sizing and economic performance, and what resilience–cost trade-offs are relevant to planning and managerial decision-making?**

The experimental analysis therefore focuses on:

1. the additional ESS capacity associated with stronger resilience requirements;
2. the corresponding economic premium;
3. the marginal cost of increasing resilience;
4. nonlinearities, transition regions, and diminishing-return behavior;
5. the mechanisms responsible for these changes;
6. the sensitivity of managerial conclusions to material modeling assumptions.

No case may be described as globally “optimal,” “best,” or “recommended” solely because it has the lowest objective value among the evaluated cases.

---

# 2. Mainline 81-case analytical role

The accepted Full81 case universe is treated as a structured response surface over the accepted resilience dimensions.

The purpose of the Full81 analysis is not merely to rank 81 solutions.

It is to characterize how the planning solution changes across resilience requirements.

For each lawful current-route case, analysis should distinguish at minimum:

- resilience requirement;
- nominal ESS energy capacity \(E^N\);
- ESS AC/PCS power capacity \(P_B\);
- contract-capacity decision where applicable;
- annualized economic objective;
- relevant cost components;
- reserve requirement;
- technically binding or economically active mechanisms where supported by accepted outputs.

Only accepted current-route outputs may be used for current-v7.4 scientific interpretation.

Historical Full81 outputs may not be silently substituted for current-route results.

---

# 3. Analysis Axis A — Absolute resilience premium

For each resilience case, quantify the incremental planning consequence relative to the accepted comparison baseline.

Relevant quantities may include:

\[
\Delta E^N
\]

\[
\Delta P_B
\]

\[
\Delta C
\]

and, where meaningful,

\[
\%\Delta E^N,\qquad
\%\Delta P_B,\qquad
\%\Delta C.
\]

The interpretation should answer:

> How much additional storage capacity and annualized cost are associated with providing the specified level and duration of service continuity?

Absolute differences and percentage differences should not be conflated.

---

# 4. Analysis Axis B — Marginal resilience cost

The analysis should evaluate not only total cost but the incremental cost of strengthening the resilience requirement.

Examples include changes along the accepted α dimension while holding β fixed and changes along the accepted β dimension while holding α fixed.

Conceptually:

\[
MC_{\alpha}
=
\frac{\Delta C}{\Delta \alpha}
\]

and

\[
MC_{\beta}
=
\frac{\Delta C}{\Delta \beta}.
\]

These quantities are descriptive finite differences over the accepted experimental grid.

They must not automatically be interpreted as continuous derivatives.

The analysis should determine whether the cost of resilience is approximately proportional or whether stronger resilience requirements become progressively more expensive.

---

# 5. Analysis Axis C — Nonlinearity and transition regions

The Full81 response surface should be inspected for systematic changes in slope or behavior.

Candidate phenomena include:

- accelerating cost growth;
- diminishing returns;
- rapid ESS-energy expansion;
- rapid PCS-power expansion;
- changes in the dominant economic mechanism;
- regions in which stronger resilience produces relatively little additional benefit per unit of cost.

A visually apparent bend is **not automatically a formal threshold**.

Unless a threshold criterion has been preregistered and scientifically justified independently of observed result magnitudes, the thesis should use language such as:

- transition region;
- region of accelerated cost growth;
- nonlinear response;
- change in marginal cost;

rather than claiming a mathematically identified “optimal threshold.”

No post-hoc threshold may be selected merely because it produces a convenient managerial story.

---

# 6. Analysis Axis D — Cost decomposition and mechanism explanation

A difference in total annualized cost should not be treated as sufficient explanation.

Where accepted model outputs permit, the analysis should determine which components account for the observed change.

Relevant mechanisms may include:

- battery energy-capacity investment;
- PCS / power-capacity investment;
- degradation-related cost;
- electricity-energy charges;
- contract-demand charges;
- over-contract penalties;
- other cost components already defined by the accepted methodology.

The objective is to distinguish:

> **what changed**

from:

> **why it changed.**

Claims about mechanisms must be supported by accepted output quantities or additional lawful diagnostic analysis.

No causal mechanism should be inferred solely from correlation between two result columns.

---

# 7. Analysis Axis E — Energy-versus-power sizing behavior

ESS energy capacity and PCS power capacity represent different planning requirements and should not be collapsed into a single “battery size” statement.

The analysis should examine whether increasing α or β primarily affects:

- energy capacity;
- power capacity;
- both;
- or neither materially.

This distinction should be interpreted physically.

For example, longer service duration may create a different sizing pressure from higher instantaneous service requirements.

However, the thesis must derive the actual mechanism from accepted model structure and results rather than assuming such behavior in advance.

---

# 8. Analysis Axis F — Managerial decision interpretation

The final analysis should translate model outputs into planning-relevant questions.

Examples include:

- What economic premium is associated with moving from a lower to a higher resilience requirement?
- Does the marginal resilience premium remain stable or rise rapidly?
- Are there regions where substantial additional investment produces comparatively small additional resilience?
- Which planning variables are most sensitive to stronger service-continuity requirements?
- Which assumptions materially affect the planning conclusion?

The thesis should distinguish:

### Scientific result

What the optimization model produces under the accepted assumptions.

### Managerial implication

What that result means for a planner choosing among resilience targets.

### Recommendation

A normative statement that may require preferences, budgets, risk tolerance, policy objectives, or other information not contained in the optimization itself.

The first two may be supported directly by the thesis.

The third must not be asserted unless the necessary decision criteria are explicitly available.

---

# 9. A2 reserve-floor robustness interpretation

The accepted A2 comparison is:

> constant worst-case reserve floor  
> versus  
> perfect-information variable reserve floor.

A2 remains a **model-form robustness screen**, not a second research question and not a replacement mainline methodology.

The perfect-information arm must be interpreted as an:

> **oracle / perfect-information counterfactual used to assess sensitivity to the conservatism of the constant worst-case reserve-floor formulation.**

It must **not** be described as:

- a realistic real-time controller;
- a deployable EMS strategy;
- a practical forecast-based reserve policy;
- a claim that future load and PV can be known perfectly.

The relevant A2 scientific question is:

> **Would relaxing the constant worst-case reserve-floor assumption under an intentionally favorable perfect-information counterfactual materially change the planning conclusion?**

If the difference is small under the future accepted materiality rule, the permissible interpretation is that the mainline conclusion is comparatively robust to this reserve-floor model-form assumption.

If the difference is material, the permissible interpretation is that reserve-floor formulation is decision-relevant and that practical dynamic-reserve formulations warrant further study.

A perfect-information result must not be presented as an achievable real-world operational performance level.

---

# 10. Forecasting boundary

Forecast-based dynamic reserve is outside the current thesis experimental pipeline unless separately authorized through a future methodology process.

No forecasting subsystem is added by this analysis plan.

This boundary is deliberate.

Adding operational forecasting would introduce additional scientific questions involving, among others:

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

Forecast-based or uncertainty-aware dynamic reserve may therefore be identified as a future operational extension.

This limitation must not be hidden.

---

# 11. Sensitivity and robustness interpretation

Sensitivity analysis should answer:

> **Would a reasonable change in an uncertain or modeling assumption alter the substantive planning conclusion?**

Sensitivity runs should not be added solely to increase the number of experiments.

For each sensitivity or robustness test, interpretation should distinguish:

1. whether numerical outputs change;
2. whether the direction of the conclusion changes;
3. whether the managerial implication changes.

A numerically detectable difference is not automatically a materially important difference.

Any formal materiality classification must follow the separately accepted materiality rule.

This document does not create that rule.

---

# 12. Prohibited post-hoc practices

The following are prohibited unless separately preregistered and justified:

- selecting thresholds after observing results;
- changing the analyzed case subset because another subset gives a clearer story;
- redefining “material” after observing effect sizes;
- presenting historical results as current-v7.4 evidence;
- adding a forecast model because the perfect-information result appears unfavorable;
- changing A2 semantics after observing A2 results;
- choosing sensitivity ranges because they produce desired conclusions;
- claiming causality from output correlation alone;
- labeling one α–β case “optimal” without an explicit decision criterion;
- hiding null or inconvenient robustness findings.

Null results remain scientific results.

---

# 13. Required figure / table logic

The final thesis should prioritize figures and tables that reveal decision structure rather than maximize output volume.

Candidate presentation families include:

### A. Response surfaces

Show how ESS sizing or annualized cost changes across α and β.

### B. Marginal-change plots

Show finite changes across adjacent resilience levels.

### C. Cost decomposition

Show which economic components generate the resilience premium.

### D. Energy-versus-power sizing

Separate \(E^N\) and \(P_B\) responses.

### E. Robustness comparison

Compare accepted mainline results with authorized robustness arms using the same quantity definitions and units.

Exact figure selection may depend on accepted result availability.

Figures must not be chosen to conceal unfavorable or null findings.

---

# 14. Claim discipline

The following distinctions must remain explicit.

### Observed numerical fact

Directly supported by an accepted current-route output.

### Derived numerical quantity

Calculated transparently from accepted outputs.

### Model-mechanism interpretation

Supported jointly by accepted equations and numerical outputs.

### Managerial implication

A decision-relevant interpretation of the preceding results.

### Speculation / future work

Not established by the present experiment.

These categories must not be collapsed in the thesis narrative.

---

# 15. Success criterion for the thesis analysis

The experimental contribution is not considered complete merely because all optimization cases solve successfully.

A successful analysis should be able to explain:

1. how resilience requirements change ESS sizing;
2. how they change annualized economic performance;
3. how the marginal cost of resilience changes across the experimental space;
4. what physical/economic mechanisms generate those changes;
5. which findings are robust to the accepted sensitivity checks;
6. which assumptions remain decision-critical;
7. what a campus energy planner can legitimately learn from these results.

The desired endpoint is therefore:

> **optimization outputs → structured evidence → mechanism explanation → robustness assessment → managerial insight**

rather than:

> **optimization outputs → case ranking.**

---

# 16. Governance status

This Candidate R1 is an additive interpretation / analysis-plan candidate only.

It does not supersede or amend Framework v7.4 or Registry v7.4.

It does not close any unresolved U-item.

It does not authorize implementation or numerical execution.

Before acceptance, it should receive an independent read-only audit for:

- consistency with Framework v7.4;
- consistency with Registry v7.4;
- consistency with Task 3 Candidate R2;
- absence of hidden methodology changes;
- absence of post-hoc tuning routes;
- compatibility with the accepted output schema;
- historical-versus-current result separation;
- leakage / look-ahead / information-advantage boundaries;
- claim-to-source discipline;
- authority / provenance integrity.

**CANDIDATE R1 — NOT ACCEPTED / NOT EXECUTION AUTHORITY.**
