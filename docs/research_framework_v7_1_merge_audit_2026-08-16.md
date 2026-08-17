# v7.1 Framework Merge Audit — 2026-08-16

## Integration provenance

`research_framework_v7_1_2026-08-16.md` was produced by integrating:

1. Base framework: `research_framework_v7_2026-08-14.md`
   - SHA-256: `08d5b76495173ccb8dde9ce5308f5d93d2f125020c19ba0836ceb0035efac5a2`
2. Preprocessing amendment: `research_framework_v7_preprocessing_update_2026-08-16.md`
   - SHA-256: `b777b826caa46135886e16d1dbb5e4685c60d46d0897c7df84ff8de2704ef7c6`

Integrated v7.1 artifact:
- `research_framework_v7_1_2026-08-16.md`
- SHA-256: `5baf78dc6b2ee7c60159d095029d9a15b114e9e8385e53d6376fd7269db06624`

## Merge scope audit

The integration started from the complete v7 base file. Changes are limited to the v7.1 preamble/version lineage and the following top-level sections required by the amendment or its supersession guardrails:

- §0 — implementation/data status
- §4 — preprocessing, baseline reconstruction, provenance, canonical-input wording
- §16 — preprocessing robustness wording
- §18 — data/chronology audit wording
- §25 — Phase 1 execution order
- §31 — production Layer A prerequisite status
- §32 — final coverage gate
- §33 — new preprocessing empirical freeze / traceability snapshot

All other numbered top-level sections from the v7 base remain text-identical.

## Empirical preprocessing decisions frozen in v7.1

- Load short-gap production rule:
  `same weekday ±6 weeks / K=1 / same-day outside-gap RMSE`
- PV donor `±30 days / K=5 mean`:
  retained as validated benchmark only
- PV short-gap production rule:
  `CWA hourly_ghi_ratio_median`, leave-target-day-out fitting
- Short outage-contaminated hours reconstructed:
  10 Load hours + 10 PV hours
- Long unavailable PV:
  1,463 h retained as mainline zero availability
- Final integrated annual input:
  still pending; must be rebuilt from current `load_annual_baseline.*` and `pv_annual_baseline.*`

## Supersession status

v7.1 is the current framework source of truth.

The following are retained only for provenance:
- `research_framework_v7_2026-08-14.md`
- `research_framework_v7_preprocessing_update_2026-08-16.md`

Do not delete them; archive them beside v7.1 so the merge lineage can be reproduced.
