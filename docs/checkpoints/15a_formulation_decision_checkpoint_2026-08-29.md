# v7.2 Formulation Decision Checkpoint
Date: 2026-08-29

## Current decision
Production mainline formulation: **Binary charge/discharge exclusivity**

Rationale:
- Binary formulation directly enforces mutually exclusive charging/discharging.
- This is preferred for the thesis mainline because physical feasibility is guaranteed ex ante.
- Runtime is currently treated as secondary to model correctness / defensibility.

## EOB formulation benchmark evidence

### Relaxed formulation
- E_N = 86.111111 kWh
- P_B = 62.000000 kW AC
- CC = 4399.137306 kW
- Objective = 66,738,326.341514 NTD-2023/year
- Max simultaneous charge/discharge = 0 kW
- Simultaneous hours above tolerance = 0
- Runtime ≈ 9.78 s
- Transition certificate = PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE

### Binary formulation, MIPGap = 1e-6
- E_N = 86.111111 kWh
- P_B = 62.000000 kW AC
- CC = 4399.137306 kW
- Objective = 66,738,326.341512 NTD-2023/year
- Best bound = 66,738,326.341512 NTD-2023/year
- Final MIP gap = 0
- Max simultaneous charge/discharge = 0 kW
- Simultaneous hours above tolerance = 0
- Runtime ≈ 226.19 s
- Transition certificate = PASS_NO_RATE_AMBIGUOUS_INCREMENTAL_OVERAGE

## Benchmark verdict
- Binary and relaxed formulations converge to the same EOB optimum within floating-point tolerance.
- BESS energy sizing, BESS power sizing, and contract capacity are identical.
- Relaxed formulation shows no simultaneous charge/discharge in the EOB benchmark.
- Relaxed is much faster, but binary remains the production preference because the physical exclusivity constraint is explicit.


## MANDATORY CHECK BEFORE FULL 81-CASE RUN
**Do not launch the full 9×9 Layer A grid immediately after the first successful Layer A solve.**

After the first small batch of representative **binary** Layer A cases, stop and review:
- per-case runtime
- solver status
- final MIP gap
- convergence behavior
- E_N / P_B / CC
- whether any representative case becomes operationally burdensome

### Re-open the formulation decision if:
- representative binary cases are much slower than the EOB benchmark,
- some cases struggle to close the MIP gap,
- projected full-grid runtime becomes impractical,
- or binary runtime would materially delay required validation / sensitivity work.

If any trigger is met, compare **binary vs relaxed** again on representative Layer A cases before running all 81 cases.

**Current default remains Binary. Relaxed is only a validated fallback candidate; do not switch automatically.**

## Re-evaluation trigger for Layer A
Do **not** switch formulation automatically.

Re-evaluate binary vs relaxed only if Layer A shows one or more of the following:
1. Representative binary cases require substantially longer runtimes than EOB and make the 81-case grid operationally burdensome.
2. Some binary cases have persistent convergence / MIP-gap difficulty.
3. Projected full-grid wall time becomes impractical for repeated sensitivity runs.
4. Binary runtime prevents completion of required validation or sensitivity analysis.

When re-evaluating:
- Select representative Layer A cases covering low, medium, and high resilience requirements.
- Run both binary and relaxed formulations on the same cases.
- Compare:
  - objective
  - E_N
  - P_B
  - CC
  - resilience feasibility / reserve requirement
  - simultaneous charge/discharge
  - runtime
- Only consider relaxed production use if:
  - design decisions are materially equivalent,
  - objective differences are negligible,
  - no simultaneous charge/discharge occurs,
  - resilience constraints remain satisfied,
  - and the computational benefit is substantial.

## Current methodological position
Mainline: **Binary**
Relaxed: **Benchmark / fallback candidate only**

## Next checkpoint
After the first small batch of representative Layer A cases, record:
- per-case runtime
- MIP gap
- solver status
- E_N / P_B / CC
- whether any case shows convergence difficulty

Then decide whether binary remains practical for the full 9×9 Layer A grid.
