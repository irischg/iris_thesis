# V7.2 production version lineage / rerun difference freeze

Status: **CANDIDATE PASS**  
Captured: `2026-09-20T04:49:05.7449159Z`  
Branch / HEAD: `thesis-v7` / `b03721275c73b05d45517bdf84c1e0bd03833376`

## Governing identity rule

`lineage_id` is the stable semantic version/branch identity. `run_id` identifies one execution. Date/time is execution metadata only. `authority_status` controls whether an artifact is historical, current, accepted, candidate, sensitivity-only, or not yet executed. Chronology alone never determines supersession.

## Authority tree

```text
MAINLINE-HIST-R1                         historical EOB; superseded
MAINLINE-HIST-R9-FINAL81                 separate historical 81-case authority; exact R9 core

MAINLINE-CORRECTED-R10                   CURRENT corrected mainline authority
├─ accepted corrected EOB                20260917T082758521112Z_a4b6383308
├─ accepted representative evidence      five independent runs; not a full 81-case surface
├─ SENS-WINTERPV-R10                     accepted sensitivity-only; 2 solves
├─ SENS-COST1MW-R10                      accepted sensitivity-only; 6 solves
├─ SENS-SOC2080-R10                      NOT_YET_EXECUTED
├─ FINAL81-CORRECTED-R10                 NOT_YET_EXECUTED
└─ ROBUST-A2-R10                         NOT_YET_EXECUTED
```

Sensitivity branches do **not** supersede `MAINLINE-CORRECTED-R10`. The historical final81 is named `MAINLINE-HIST-R9-FINAL81`, not forced under R1, because its immutable manifest pins core R9 (`d145eeb0c48a865c9a5d467346d94b63075e8245c08de4ecf890c1055e4369c0`).

## Supersession and execution record

| lineage_id | authority_status | run_id / execution scope |
|---|---|---|
| MAINLINE-HIST-R1 | historical accepted, superseded | original timestamp run_id not retained; do not fabricate |
| MAINLINE-HIST-R9-FINAL81 | historical accepted 81-case, superseded for corrected architecture | `20260911T112258206802Z_4d0eb9e1da` (81 solves) |
| MAINLINE-CORRECTED-R10 | current accepted mainline | corrected EOB `20260917T082758521112Z_a4b6383308`; five accepted representative runs |
| SENS-WINTERPV-R10 | accepted sensitivity-only | `20260918T155044175327Z_3d71b70173` (2 alternative solves; 0 mainline solves) |
| SENS-COST1MW-R10 | accepted sensitivity-only | `20260919T151258567077Z_0541e6897a` (6 alternative solves; 0 mainline solves) |
| SENS-SOC2080-R10 | NOT_YET_EXECUTED | PENDING |
| FINAL81-CORRECTED-R10 | NOT_YET_EXECUTED | PENDING |
| ROBUST-A2-R10 | NOT_YET_EXECUTED | PENDING |

## What changed

- Historical EOB R1 → corrected R10: joint accepted code/data correction bundle (corrected annual input, R10 Exact-D/MAX-demand handling, corrected transition settlement interface/matrix, W-07 per-increment overcontract allocation). Tariff, 10 MW package, SOC/efficiency, degradation method, and binary solver target remain frozen. Observed economic deltas are not uniquely attributable because no isolated counterfactual solves exist.
- Historical final81 R9 → future corrected final81: corrected architecture is known, but the corrected 81-case execution and all result deltas remain `PENDING`.
- Winter-PV: only authorized Winter-PV availability changes (619 rows; +39,484.422494 kWh available PV). Core, tariff, package, settlement, SOC/efficiency, reserve, and solver controls remain frozen.
- 1 MW cost scale: the full PNNL 1 MW cost/degradation package changes atomically. The label is not a power bound. All non-cost assumptions and architecture remain frozen.

## Accepted result summary

- Corrected EOB: objective `66,708,197.09463947` NTD-2023/year; `E_N=77.7777777778 kWh`, `P_B=56 kW-AC`, `CC=4388.666231266645 kW`.
- Historical→corrected EOB: objective `-30,129.24687255174` NTD-2023/year; `E_N=-8.3333333333 kWh`; `P_B=-6 kW`; `CC=-10.4710747251 kW`. Full component deltas are in the difference matrix.
- Corrected representatives: `a0.60_b04`, `a0.60_b12`, `a0.80_b08`, `a1.00_b04`, `a1.00_b12` are accepted individually; they do not constitute corrected final81.
- Winter-PV accepted results: EOB objective `66,622,010.51124089`; `a0.80_b08` objective `107,688,858.80331968` NTD-2023/year.
- 1 MW cost accepted results: six cases (`EOB` plus the five representatives); every objective/design/cost delta is carried in the machine-readable matrix and source paired comparison.

## Machine-readable authority links

| evidence | path | SHA-256 |
|---|---|---|
| historical EOB result | `results/eob_production/eob_production_result_v7_2.json` | `ad606a503b3f68ceba048e4b94bc0e19e6ddde00f88c145d051f772557e0bd56` |
| historical R9 final81 surface | `results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da/surface_summary.json` | `d051018fc9fd4b87534d766cad887d33e95701a0a157e43d64ed4329a96f4203` |
| corrected EOB result | `results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/corrected_eob_result.json` | `d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022` |
| corrected representative a0.60_b04 | `results/layer_a/preflight/runs/20260918T054012682911Z_54b3624894/representative_cases/a0.60_b04/a0.60_b04_result_v7_2.json` | `2e5710835b9a882a4978fda39990f493020418b34cd0d386d6f1399301fa23c5` |
| corrected representative a0.60_b12 | `results/layer_a/preflight/runs/20260918T063627414306Z_c114929d2c/representative_cases/a0.60_b12/a0.60_b12_result_v7_2.json` | `6372608d847b8498c7b819bddd8e59a707cf4fbecb311496d27787e52205df3d` |
| corrected representative a0.80_b08 | `results/layer_a/preflight/runs/20260918T085202453195Z_755e01dfb2/representative_cases/a0.80_b08/a0.80_b08_result_v7_2.json` | `8a9bc67fc541ea682f9360e6063ededdb5bc0e2c6340c43c10c1fde86ab155f6` |
| corrected representative a1.00_b04 | `results/layer_a/preflight/runs/20260918T105101058616Z_a75a268198/representative_cases/a1.00_b04/a1.00_b04_result_v7_2.json` | `9fa5506db13681df0dd86b91bf3f9729b47f7a874fe57909b422dea7a6dfa628` |
| corrected representative a1.00_b12 | `results/layer_a/preflight/runs/20260918T123936526903Z_82e3bc3214/representative_cases/a1.00_b12/a1.00_b12_result_v7_2.json` | `6ea1dce9c951d11f3129c8654057c33df97030e54241f367123cfb6776590321` |
| Winter-PV paired comparison | `results/sensitivity/winter_pv_17c/20260918T155044175327Z_3d71b70173/paired_sensitivity_comparison.json` | `b8acd3027c3c1db31bd8840cf0ea6af7f67ea784fcd856bb3dcd2e3317677ca5` |
| 1 MW cost paired comparison | `results/sensitivity/bess_cost_scale_1mw/runs/20260919T151258567077Z_0541e6897a/paired_sensitivity_comparison.json` | `5a440334c273da91958977f2bf82e911ae0f13e584019981dedbe6105ea67b8a` |
| semantic lineage ledger | `results/provenance/v7_2_production_version_lineage_freeze_candidate/production_version_lineage_ledger.json` | `b809c2158cc8d8f85cfc2de9052730693168659979976e096b89f26c7fbee50a` |
| cross-version difference matrix | `results/provenance/v7_2_production_version_lineage_freeze_candidate/cross_version_difference_matrix.json` | `182cdec87d54d5ec5c611e9097aade872fa3f043dd2f072434145f5172fb4048` |
| working-tree snapshot | `results/provenance/v7_2_production_version_lineage_freeze_candidate/working_tree_snapshot_manifest.json` | `f72694addfd46dcf51363a5efba9fc94eeda6daf62823b9f5ff9a5f6dc1d9ad9` |

## Reconstructibility and current snapshot

- R1 core is byte-reconstructible from `9ac078ccc8a42410bf01b7bf1871ae8b5acd88ca:src/annual_design_model_v7_2.py`.
- R9 core is byte-reconstructible from `b2acdf28cf1459aee5da44e4407c225f5d3c68a6:src/annual_design_model_v7_2.py`.
- R10 core and its corrected drivers are not committed at HEAD; exact bytes are pinned by run manifests and `working_tree_snapshot_manifest.json`. The preserved tracked patch reconstructs tracked modifications from HEAD; relevant untracked source files are SHA-pinned.
- `docs/ai_handoff/CURRENT_STATE.md` was intentionally not edited and is stale relative to these accepted runs; it is not used here as current run authority.

## Package artifacts

- `production_version_lineage_ledger.json` / `.csv`: authoritative semantic ledger, complete run identities, assumptions, results, and reconstructibility.
- `cross_version_difference_matrix.json` / `.csv`: one field/model feature per row, controlled `change_type`, explicit pending rows.
- `working_tree_snapshot_manifest.json`: pre-package branch/HEAD/status, untracked inventory, relevant file hashes, and patch identity.
- `prepackage_tracked_changes.patch`: exact tracked working-tree delta against HEAD.
- `results/provenance/v7_2_production_version_lineage_freeze_candidate/package_manifest.json`: final SHA-256 index for this package and this master checkpoint.

No optimization model was created and no solver was run for this consolidation gate. No methodology, implementation, input, accepted result, `CURRENT_STATE.md`, commit, tag, or remote state was changed.
