# V7.2 Transition-Settlement Decision Bridge

**Status:** FROZEN PROJECT IMPLEMENTATION PROVENANCE

**Decision date:** 2026-09-09

**Scope:** documentation of the already-accepted post-14b transition-settlement implementation; no mathematics is changed.

## Authority and claim boundary

Script 14b intentionally stopped short of claiming an official, universal Taipower formula for aggregating positive over-contract demand across summer/non-summer portions of a mixed-season billing period. The retained public evidence establishes date-sensitive tariff applicability and supports the audited season-specific rates and 10% / 2x / 3x tiers, but it does not directly provide a complete universal cross-season positive-over-contract aggregation formula.

The current annual core subsequently implements a **project-specific settlement interpretation** to complete the thesis model. Under that accepted implementation, sequential non-duplication is applied to the billing-period TOU maximum, and each positive incremental overage is priced using the basic-charge rate for the season containing the canonical binding/maximum event.

The reduced-native-MAX formulation is an implementation of this project rule. It is not a claim that Taipower officially publishes this exact optimization construction. Class A and Class B components use billing-demand epigraphs; only Class C components, where two active seasons have different settlement rates, retain two exact native seasonal MAX resultants and a source-selection binary.

**THIS IS A THESIS PROJECT IMPLEMENTATION RULE USED TO COMPLETE THE CROSS-SEASON SETTLEMENT MODEL WHERE PUBLIC TAIPOWER MATERIAL DID NOT PROVIDE A DIRECTLY OBSERVED COMPLETE FORMULA.**

This addendum supplements but does not amend the v7.2 Framework, Registry, Script 14b, annual core, or tariff interfaces.

## Exact tie behavior in the accepted implementation

Let `d = later-season maximum - earlier-season maximum`.

* The numerical tie band is `max(1e-4 kW, 100 × FeasibilityTol, 100 × machine-epsilon × demand-scale)`. With the default `FeasibilityTol = 1e-6`, the controlling band is `1e-4 kW`.
* If `abs(d) <= tie_band`, including exact equality at either boundary, the canonical source is the earliest maximum timestamp/earlier season: `NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP`.
* If `d < -tie_band`, the earlier season is clearly larger.
* The later-season branch begins at `d >= tie_band + selection_guard`, where `selection_guard = 10 × FeasibilityTol`.
* A value strictly inside `(tie_band, tie_band + selection_guard)` is `NUMERICAL_BOUNDARY_UNRESOLVED`; it is not silently assigned the cheaper rate.
* For Class C, an unresolved boundary is rate-relevant and fails the transition-settlement certificate. For Class B, the two audited rates are equal, so the source label remains diagnostic and does not affect cost or certificate validity.

The static test fixes the closed-band and guard-boundary classifications. The existing focused Class-C integration test additionally fixes early-season, later-season, and genuine-tie outcomes, including selection of the earlier season even when the later-season rate is cheaper. That integration test is recorded as evidence here but is not executed by this provenance pass because it optimizes a fixture.

## Frozen evidence identifiers

| Role | Version | SHA-256 |
|---|---|---|
| Current annual core, `src/annual_design_model_v7_2.py` | `v7.2-annual-design-core-transition-candidate1-reduced-native-max-2026-09-06-r9` | `d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0` |
| Current Script 16a, `scripts/16a_preflight_layer_a_representative_binary_cases.py` | `v7.2-layer-a-analytical-representative-binary-preflight-transition-candidate1-reduced-native-max-provenance-2026-09-06-r10` | `c9e01022a7596b2fdf2f42e1a84855585c7901b06af100f0cb8d189852ee502f` |
| Script 14b settlement interface builder | `v7.2-transition-period-seasonal-settlement-preflight-2026-08-26` | `0eb79d6ba80bd5028d8263400610cabbf58faae39d365f554c91814b0370bf2f` |
| Transition settlement interface | n/a | `896f07e4dd6335fb26a906d2274446c362d11da503d7bd08be766f2d223a4916` |
| Settlement matrix | n/a | `31172c471c11034ac55811d9eb0ee5602d0e2dbbdc55f09f3320855078e190e1` |
| Static transition test, `tests/test_transition_candidate1_static_v7_2.py` | n/a | `56fe83b0ca3b17905af5531084abb216b6d5ee43a2234152fec2dc8ab45c7693` |
| Class-C integration test, `tests/test_transition_candidate1_class_c_integration_v7_2.py` | n/a | `5fd227fbfe6d14096d9f57f57d98218e80520ce42a9fa09d36a3dfa4104b81e0` |
| Framework v7.2 | n/a | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |
| Literature/Evidence Registry v7.2 | n/a | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |
| Framework–Registry alignment audit | n/a | `0035514813799df8baa46bf912a73c76f946ccdadd87ce88014c92fd79a7517d` |
