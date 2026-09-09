# V7.2 Production Artifact Authority and Legacy Boundary

**Status:** FROZEN CONSUMER POLICY

**Date:** 2026-09-09

**Scope:** future Winter-PV economic sensitivity and final 81-case production runners.

## Authoritative accepted artifacts

* Frozen EOB comparator: `results/eob_production/eob_production_result_v7_2.json`, certified by `results/eob_production/eob_production_freeze_audit_v7_2.json` and the Script-15c rainflow outputs in `results/degradation_validation/`.
* Current representative validation: exact run ID `20260906T050046737317Z_5f2cd1942c`; completion manifest `results/layer_a/preflight/runs/20260906T050046737317Z_5f2cd1942c/run_completion_v7_2.json`; status `REPRESENTATIVE_PASS`; all five selected cases present.
* Formal Winter-PV validation: exact run ID `20260909T042957292822Z_7de1c7a4f4`; completion manifest `results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/completion_manifest.json`; decision `PASS_FOR_SENSITIVITY`.

Exact paths, hashes, versions, and status gates are frozen in `docs/checkpoints/production_checkpoint_manifest_v7_2_2026-09-09.json`.

## Historical or non-authoritative locations

| Location | Classification | Future-consumer rule |
|---|---|---|
| `results/layer_a/preflight/representative_cases/` | stale top-level convenience output | Never consume as production evidence. |
| `results/layer_a/preflight/layer_a_representative_preflight_summary_v7_2.csv` | stale top-level convenience output | Never consume as production evidence. |
| `results/eob_benchmark/` | historical Script-15a benchmark | Never use as the production EOB comparator. |
| `results/eob_benchmark_gap1e-5/` | historical Script-15a benchmark | Never use as the production EOB comparator. |
| `results/eob_benchmark_gap1e-6/` | historical Script-15a benchmark | Never use as the production EOB comparator. |
| `results/layer_a/preflight/runs/20260903T132530103499Z_f32ad981ca/` | historical failed representative run | Never consume; completion status is `REPRESENTATIVE_GATE_FAIL`. |
| `results/layer_a/preflight/runs/20260905T110342777608Z_e9587c959c/` | historical failed representative run | Never consume; completion status is `REPRESENTATIVE_GATE_FAIL`. |
| `results/layer_a/preflight/runs/20260906T040445014999Z_df972f82f0/` | build-only intermediate | Not accepted solved validation evidence. |
| `results/layer_a/preflight/runs/20260906T044615625390Z_53ab30b125/` | superseded one-case representative pass | Not the accepted five-case run. |
| `results/eob_production/` | historical frozen Script-15b output | Consume only through the exact frozen comparator hashes; do not relabel as a current-core solve. |
| `results/degradation_validation/` | historical frozen Script-15c validation | Preserve as ex-post validation of the frozen EOB; do not regenerate implicitly. |
| `results/data_audit/winter_pv_holdouts/20260908T110508357881Z_3944dda5e0/` | superseded pre-freeze 17a evidence | Preserve, but do not use as formal production provenance. |

## Mandatory future-consumer rules

Future production code must never:

* choose a run or artifact by filename recency, directory ordering, or modification time;
* trust a top-level convenience copy;
* use Script-15a benchmark output as the production EOB;
* consume a failed, incomplete, build-only, or superseded run directory;
* silently update an expected hash or regenerate a frozen artifact.

Future production code must require:

1. the exact run ID named in the production checkpoint manifest;
2. the exact run-specific completion manifest and required PASS status;
3. the expected source, core, wrapper, input, economic, tariff, and settlement hashes;
4. the exact frozen EOB comparator and freeze-audit hashes;
5. production-environment preflight PASS;
6. production-checkpoint validation PASS;
7. an explicitly recorded repository state;
8. a new run-specific output directory; and
9. a completion manifest written only after successful completion.
