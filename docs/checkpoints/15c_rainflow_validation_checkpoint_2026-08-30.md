# 15c Rainflow Validation Checkpoint — 2026-08-30

## Status

**EOB ex-post rainflow / DOD validation: CLOSED / PASS**

Final verdict:

`EOB_RAINFLOW_VALIDATION_PASS`

## Frozen EOB under validation

- E_N = 86.111111 kWh
- P_B = 62.000000 kW AC
- Regular contract capacity CC = 4399.137306 kW
- Annual objective = 66,738,326.341512 NTD-2023/year
- Production formulation = Binary
- EOB contains no Layer A resilience constraints.

## Rainflow validation result

The frozen 15b EOB dispatch was validated ex post using the reusable v7.2 rainflow validator.

Cycle-depth diagnostics:

- Turning points = 797
- Rainflow records = 506
- Weighted cycle count = 398.000000
- Equivalent full cycles, nameplate-normalized = 173.241935
- Equivalent full cycles, 0.80 usable-window-normalized = 216.552419
- Maximum rainflow DOD = 80.0000%
- Weighted-median rainflow DOD = 30.0000%
- Energy-weighted rainflow DOD = 54.9233%

## Energy reconciliation

Battery-side annual discharge:

- Dispatch = 14,918.055556 kWh
- Intertemporal PWL segments = 14,918.055556 kWh
- Rainflow accounting = 14,918.055556 kWh
- Rainflow minus dispatch = 0.0000000000 kWh

Result: **PASS**

## Degradation-cost reconciliation

- Frozen 15b PWL degradation cost = 16,168.568638 NTD-2023/year
- PWL cost reconstructed from dispatch segments = 16,168.568638 NTD-2023/year
- Rainflow-implied cost using the same locked PNNL-calibrated G(delta) curve = 16,168.568638 NTD-2023/year
- PWL minus rainflow = 0.000000 NTD/year
- Absolute relative difference = 0.00000000%

Result: **PASS**

This validates the frozen EOB dispatch under the current degradation calibration. It does not claim universal equivalence between finite PWL degradation accounting and rainflow for every future dispatch.

## Validation gates

All Script 15c hard gates passed:

- 15b freeze provenance
- solver / binary / optimality provenance
- shared-core hash
- 14a economic-interface hash
- 10 MW mainline degradation package
- retained PNNL Table 4.2 technical provenance
- rainflow algorithm internal self-test
- formal 8,760-hour case timeline
- SOC / physical-energy identity
- SOC bounds
- annual cyclic state
- hourly segment power linkage
- intertemporal segment-state dynamics
- physical / segment-state identity
- PWL dispatch-cost reconciliation
- rainflow / dispatch discharged-energy reconciliation
- rainflow technical DOD-domain check
- PWL / rainflow degradation-cost numerical equivalence

## Methodological boundary

Rainflow remains an **ex-post validation method only**.

It is not inserted into the annual optimization objective and does not modify:

- E_N
- P_B
- CC
- dispatch
- PNNL cost package
- C_rep
- lambda_k
- the B1 mainline degradation formulation

The callable validator in:

`src/rainflow_validation_v7_2.py`

must be reused for subsequent final Layer A solution validation rather than reimplementing a separate rainflow method.

## Layer A authorization

**GO FOR 16a REPRESENTATIVE LAYER A CASES**

The pre-16a rainflow validation blocker identified by the staged pipeline audit is resolved.

However:

**FULL 81-CASE GRID: NOT YET AUTHORIZED**

Before launching the complete 9 x 9 Layer A grid, a representative Binary Layer A batch must be reviewed for:

- solver status
- runtime
- final MIP gap
- convergence behavior
- E_N / P_B / CC
- resilience feasibility / reserve behavior
- simultaneous charge/discharge
- ex-post rainflow validation

If Binary Layer A becomes computationally impractical or develops convergence issues, reopen the previously validated Binary-vs-Relaxed fallback review before authorizing the full grid.
