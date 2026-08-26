# Thesis Writing Checklist — v7.2

Status: writing-stage reminder only  
Methodology authority: v7.2 Framework + v7.2 Literature Evidence Registry  
Created: 2026-08-26

## 1. Research positioning to preserve

The thesis should NOT present NTUST as the protagonist of the research.

Preferred framing:
- The research develops a planning framework that translates service-continuity targets into BESS/contract-capacity requirements and economic consequences.
- NTUST is the empirical demonstration case used to implement and validate the framework.
- Core decision-policy mapping:
  (alpha, beta) -> BESS energy / BESS power / contract capacity -> resilience premium -> off-design capability.

Avoid wording that implies:
- the thesis is simply an NTUST energy-saving project;
- the framework is universally calibrated from one campus;
- modeled planning requirements are final engineering installation recommendations.

## 2. Laboratory thesis lineage to explain in Chapter 2 / research gap

Use earlier laboratory theses mainly as internal methodological/contextual lineage, not as primary evidence for current numerical assumptions.

Suggested lineage:

Pieter
-> early PV-BESS sizing / techno-economic analysis / separate energy and power sizing / stress-test thinking

Mu
-> joint BESS and contract-capacity optimization and management-facing economic interpretation

Harry
-> NTUST annual planning, tariff-aware economics, full-year chronology, fixed-design replay, sensitivity and reproducibility discipline

Iris
-> service-continuity target surface:
   (alpha, beta)
   -> joint BESS/CC planning
   -> capacity and cost premiums
   -> structured off-design capability

Dennis and Eric may be discussed as supporting laboratory precedents for result presentation and SEMS scenario/dispatch interpretation, but they are not direct NTUST main-meter methodological benchmarks.

Important factual caveat:
- Mu, Pieter, and Harry are the strongest NTUST/campus-context precedents.
- Eric uses campus/building SEMS concepts but includes simulated/inferred inputs.
- Dennis is primarily a residential-building/community study, not an NTUST main-meter case.

## 3. What to borrow from each prior thesis

### Pieter

Borrow:
- distinction between BESS power and energy sizing;
- techno-economic interpretation;
- stress / off-design comparison concept.

Do NOT inherit:
- legacy seasonal/representative-day sizing assumptions;
- legacy SOC bounds, FiT/export assumptions, or numerical parameters;
- any cost parameter merely because it appeared in the prior thesis.

### Mu

Borrow:
- joint interpretation of contract capacity and BESS decisions;
- management-facing reporting:
  optimal CC, BESS size, electricity-cost effect, financial implication.

Do NOT inherit:
- hard grid-import <= contract-capacity treatment when the current v7.2 model explicitly represents Taipower over-contract penalties.

### Harry

Borrow:
- annual chronological planning architecture;
- separation of design and fixed-design replay;
- cost-component reporting;
- sensitivity analysis;
- reproducibility and limitations framing.

Do NOT inherit production values from the Harry-era model.
The following remain legacy/replication-only unless explicitly used for comparison:
- annualized energy coefficient 813.75
- annualized power coefficient 694.4
- CRF = 0.07
- c_deg = 0.55
- C_rep = 5107.57
- PWL slopes 0.532 / 1.596 / 2.128
- hourly-reset PWL degradation logic
- eta_c = 0.95

### Dennis

Borrow:
- scenario-to-cost-component reporting;
- showing how contract/basic charge, energy charge, penalties and total cost change across scenarios.

Do NOT import:
- residential EV/V2B assumptions;
- residential load structures;
- unrelated replacement or mobility assumptions.

### Eric

Borrow:
- dispatch visualizations;
- intuitive explanation of when PV, grid and BESS supply the load;
- transparent discussion of data limitations.

Do NOT import:
- RL merely because it is more algorithmically complex;
- EV/V2B assumptions;
- green-energy target assumptions not part of the current research question.

## 4. Chapter 2 wording tasks

When writing Literature Review / Research Gap:

- distinguish international Q1 literature from internal laboratory precedent;
- use Q1 literature and official/technical sources as the primary methodological evidence;
- use prior lab theses to establish research lineage and local empirical continuity;
- do not cite a lab thesis as the sole justification for a production parameter when a stronger primary source exists.

Explicitly articulate the gap:

Existing studies commonly address some subset of:
- economic BESS sizing;
- tariff arbitrage;
- peak-demand reduction;
- contract-capacity optimization;
- outage resilience;
- PV-BESS dispatch.

The present research contribution is the explicit mapping of management-selected service-continuity targets (alpha, beta) to:
- required BESS energy;
- required BESS power;
- annual regular contract capacity;
- total annualized cost;
- resilience/capacity premiums;
- binding mechanisms;
- off-design capability.

## 5. Methodology wording tasks

Make clear that:

- EOB is the economic-only reference case, not a no-BESS case.
- EOB may optimally select zero BESS.
- Layer A uses the same annual economic model plus the service-continuity reserve/power requirements.
- reserve R(alpha,beta) is derived from alpha, beta, Load, PV and eta_d; it is not an arbitrary SOC percentage.
- NTUST is the demonstration case.
- alpha and beta are management-selected service targets, not statutory reliability requirements.
- 10 MW PNNL package is the ex-ante mainline cost-scale package.
- 1 MW PNNL package is the higher-cost sensitivity.
- optimized P^B must never be used to choose the PNNL cost bracket ex post.
- all optimization-facing monetary terms use constant NTD-2023.
- r = 5% is a real modeling discount rate, NOT an inflation rate and NOT claimed to be NTUST WACC.
- n = 20 years is the financial analysis horizon, not a guaranteed physical BESS lifetime.

## 6. Results / Chapter 4 presentation tasks

Do not report only optimization variables or heatmaps.

For EOB and Layer A, report at minimum:
- BESS nameplate energy E^N;
- BESS power P^B;
- annual regular contract capacity CC;
- total annualized cost;
- annualized CAPEX;
- annual FOM;
- energy charge;
- basic charge;
- over-contract charge;
- degradation cost;
- annual grid import;
- battery throughput;
- SOC diagnostics;
- post-solve exact monthly billing-demand maxima.

For Layer A, emphasize:
- Delta E(alpha,beta);
- Delta P(alpha,beta);
- Delta C(alpha,beta);
- binding mechanism;
- knee/no-knee behavior.

Borrow the management-facing reporting style from Mu/Dennis:
explain WHY total cost changes, not merely that it changes.

## 7. Dispatch figures to prepare

Use a small number of representative operational plots, not only the 81-point surfaces.

Candidates:
- EOB;
- low service-continuity requirement;
- middle service-continuity requirement;
- high service-continuity requirement.

Plots should show where appropriate:
- Load;
- PV;
- grid import;
- BESS charging;
- BESS discharging;
- SOC;
- reserve floor.

Use these plots to explain how reserve locking changes normal economic dispatch.

## 8. Limitations wording to preserve

Do NOT claim excluded effects are nonexistent.

State them as deliberate planning-level simplifications / scope boundaries, including:
- no explicit calendar-aging state;
- no explicit temperature-dependent aging;
- no explicit C-rate aging state;
- no detailed electrochemical SOH model;
- no explicit replacement/augmentation schedule in the mainline accounting;
- hourly rather than full sub-hourly physical operation;
- kappa is a calibrated hourly-to-billing-demand proxy, not reconstructed 15-min chronology;
- no PV capacity sizing;
- no export/FIT revenue in the mainline;
- no HVAC/EV/flexible-load co-optimization;
- no ancillary-service revenue;
- no site/fire-code/interconnection/budget engineering feasibility constraints in Layer A.

Use wording such as:
"planning-level modeled requirements"
rather than:
"final engineering installation recommendation."

## 9. Defensibility statement for later drafting

The v7.2 core methodology should be presented as:
- consistent with mainstream economic BESS sizing/dispatch literature;
- strengthened by Taiwan-specific tariff and contract-capacity institutional modeling;
- strengthened by audited tariff/bill regression;
- strengthened by site-specific kappa calibration;
- strengthened by common monetary-vintage accounting;
- strengthened by PNNL-calibrated intertemporal DOD-sensitive degradation;
- deliberately scoped to isolate the effect of service-continuity requirements.

Do NOT add complexity merely to imitate previous theses or other papers unless it closes a clearly identified research-question or validity gap.

## 10. Final-writing verification checklist

Before thesis submission, explicitly verify:
- all Q1 quartile claims against the university-required JCR/SJR year;
- all official Taipower tariff claims against retained source artifacts;
- CPI/FX monetary normalization provenance;
- PNNL source version and cost scale;
- EOB / Layer A terminology is consistent across Abstract, Chapters 1-5 and figures;
- lab-thesis lineage is described accurately without overstating that all five studies used the same NTUST dataset;
- legacy numerical parameters appear only when explicitly labeled legacy/replication/comparison;
- limitations are stated transparently;
- contributions are framed as framework-level contributions with NTUST as demonstration case.

## Reminder trigger

When thesis prose drafting begins, review this checklist before drafting:
- Chapter 2 Literature Review / Research Gap
- Chapter 3 Methodology
- Chapter 4 Results and Discussion
- Chapter 5 Limitations / Conclusions

This checklist is not allowed to override the current Framework or Literature Evidence Registry.
