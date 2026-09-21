# Corrected EOB driver runtime import repair checkpoint — v7.2 — 2026-09-17

## Status

`CORRECTED EOB RUNTIME IMPORT REPAIR PASS — IMPORT DEFECT CLOSED / READY FOR RE-AUTHORIZATION`

This checkpoint records an implementation correction to the corrected-EOB production driver. It does not change methodology, the annual model, solver policy, inputs, the Framework, or the Registry. No corrected-EOB production command was executed in Gate 7A.

## Closed defect

Gate 7 failed before core import because direct filesystem-path execution placed `scripts/` rather than the repository root on `sys.path`. The repaired driver applies the established repository-root bootstrap before importing `src.annual_design_model_v7_2`.

The failed run directory `results/eob_production_corrected/runs/20260917T074854498781Z_967301557c/` remains empty and preserved as `CORRECTED_EOB_EXECUTION_FAILED_PRE_SOLVE`. It is not a candidate and cannot be reused.

## Frozen repair identities

- Driver: `scripts/15d_run_corrected_eob_v7_2.py`
  - pre-repair SHA-256: `3a14ec166ca4162489a5a76d3e34efb2c59dbfb9c4c8a361e51836bdcf87dca2`
  - repaired SHA-256: `90d19baac8c0b96e08de00b4769b7ae68dff745f71923b850433ffc2935091a8`
  - version: `v7.2-corrected-eob-production-driver-2026-09-17-r2-runtime-import-repair`
- Dedicated tests: `tests/test_15d_corrected_eob_driver_v7_2.py`
  - pre-repair SHA-256: `4e284417624fa86022237ccc3dab252ed70e668f5c819ed3e6b2dbbebdd52d2f`
  - repaired SHA-256: `98e11acdf479588a40dd43718f00ec40d6ffb7d728346b92cbe8e9dd067f79e9`
- Core: `src/annual_design_model_v7_2.py`
  - `CORE_VERSION`: `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10`
  - SHA-256: `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8`

## Validation

The actual repository-root command below exited `0`:

```text
.venv/Scripts/python.exe -X utf8 -B scripts/15d_run_corrected_eob_v7_2.py --runtime-import-check
```

It resolved the accepted core, `SolveSettings`, `load_annual_design_inputs`, `solve_eob`, and Gurobi 13.0.1. Runtime guards recorded zero model-construction attempts, zero optimization attempts, zero solve calls, and zero production run-directory allocations.

The dedicated suite passed `17/17`: original T01–T12 and new T13–T17. Static inspection confirms exactly one future production `solve_eob` call site, `layer_a_requirements=None`, no `node_limit` setting, and no retry path. Gate-1 through Gate-6B evidence, preexisting checkpoints, historical EOB outputs, historical final-81 outputs, tags, branch, and HEAD were unchanged.

## Gate 7A evidence identities

- `gate7a_failure_classification_2026-09-17.json`: `eb646631178063b37715d312f4f56df0ad4ed0e2bee17810886f72d0e62bf495`
- `gate7a_pre_repair_state_2026-09-17.json`: `b7618b1e65cfd35946573fc72a808e89d6fa285d67113ba9650213cc22bb7496`
- `gate7a_runtime_import_root_cause_2026-09-17.md`: `35c804674637955397bbe852ae942c13f4a4af778e4fa3860273d4ea9654067e`
- `gate7a_repair_diff_2026-09-17.txt`: `c7abb09af03d94cd78ad5d0fcd192ec4fa5547711a19c8dd67d0075b0b7a930e`
- `gate7a_runtime_import_test_results_2026-09-17.json`: `381d72a873067162693392df342bd81b6c0b78acfa9961e7d0c4b57371cdef1f`
- `gate7a_driver_manifest_2026-09-17.json`: `97599ad023f671478c10db496bdbd1e15689cf424630d3ab9a3d132075952a14`
- `gate7a_validation_report_2026-09-17.md`: `c013737e31b58a80b44041c93707ac9715aaa7227f3509f3a5dd744e2779a6b7`

Evidence root: `results/provenance/production_rerun_v7_2_20260915/gate7a_driver_runtime_import_repair/`.

## Future production command

The canonical future command remains:

```text
.venv/Scripts/python.exe -X utf8 -B scripts/15d_run_corrected_eob_v7_2.py --execute-production
```

This command requires a new explicit one-run authorization. Gate 7A did not execute it.

## Next readiness

`READY FOR ONE-RUN CORRECTED EOB RE-AUTHORIZATION`
