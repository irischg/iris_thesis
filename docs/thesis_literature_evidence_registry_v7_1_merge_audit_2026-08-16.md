# Registry v7.1 Merge / Evidence-Role Audit — 2026-08-16

## Provenance

- Base registry: `thesis_literature_evidence_registry_v7_2026-08-14.md`
  - SHA-256: `d13c3674ca35c06775bc75d04acf6270db739e3baa0974e6956ae648456004d5`
- Alignment framework: `research_framework_v7_1_2026-08-16.md`
  - SHA-256: `5baf78dc6b2ee7c60159d095029d9a15b114e9e8385e53d6376fd7269db06624`
- Integrated registry: `thesis_literature_evidence_registry_v7_1_2026-08-16.md`
  - SHA-256: `9d90218a520b429fe07c081f26c282e68b5fa68d7537f97a13201719d3816c31`

## Structural preservation

- Evidence IDs in base registry: 45
- Evidence IDs in v7.1 registry: 48
- Removed evidence IDs: None
- Added evidence IDs: ['R32', 'R33', 'I5']

No pre-existing R/T/I/P/L evidence item was deleted.

## Main evidence-role changes

1. **R21–R22 retained**
   - Continue to support pattern/context-aware Load imputation and artificial-gap validation.
   - Exact production rule is no longer ±8 weeks/K=3.
   - Exact v7.1 rule is controlled by P1: same weekday ±6 weeks/K=1 / same-day outside-gap RMSE.

2. **R23 retained but narrowed**
   - Supports solar-gap / artificial-gap validation logic.
   - It no longer appears to support a production PV donor rule.

3. **R32 added — Ramadhan et al. (2021)**
   - Supports irradiance/weather-to-PV-power estimation as a valid model family.
   - Does not support `hourly_ghi_ratio_median` as a literature constant.

4. **R33 added — Mayer & Gróf (2021)**
   - Supports model-selection sensitivity and multi-metric comparison.
   - Used only as methodological support for Script 04b selection logic.

5. **I5 added — CWA CODiS / Open Data**
   - Establishes official weather-data provenance.
   - Does not claim official support for the project-specific 23:59 timestamp normalization.

6. **P1 fully rewritten**
   - Load: ±6 weeks/K=1 production.
   - PV donor ±30d/K5 mean: validated benchmark.
   - PV production: CWA `hourly_ghi_ratio_median`.
   - 10 Load + 10 PV outage hours reconstructed.
   - 1,463 h long-unavailable PV remains conservative-zero mainline.
   - Old “expanded-envelope already has no effect on all 81 cases” claim is not retained as a current validated result.

7. **P2 canonical-input wording updated**
   - Billing calibration must use observed columns of the final v7.1 integrated annual input.
   - File name is not source of truth.
   - Pre-v7 `annual_input_existing_pv.*` is legacy until regenerated and audited.

## Claim-map / maintenance synchronization

The following were updated to match the new evidence roles:
- §0.1 conflict-resolution table
- §12 claim-to-source map
- §13 priority-reading order
- §14 safe / unsafe claim wording
- §15 evidence-status summary
- §16 working bibliography
- v7.1 maintenance guardrails

## Current preprocessing evidence status

- Component preprocessing Scripts 01–05: CLOSED / PASSED.
- Final integrated annual input: still pending.
- Long-block winter CWA reconstruction: not validated by short-gap Script 04b; requires separate block/month holdout validation before use as sensitivity.
