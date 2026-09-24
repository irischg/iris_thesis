# Step 2D Candidate R3 — Independent Acceptance Attestation

**Record identity:** `V7_3_RECONSTRUCTED_PV_MAINLINE_STEP_2D_R3_INDEPENDENT_ACCEPTANCE_2026_09_24`  
**Record type:** `INDEPENDENT_ACCEPTANCE_ATTESTATION`  
**Record date:** 2026-09-24  
**Independent auditor:** `CODEX`  
**Primary implementation agent:** `CLAUDE CODE`

This is an additive attestation of an already-completed independent read-only audit. It is not a
candidate and is not pending another independent audit.

## A. Independent verdict and accepted state

`POST_2D_A_GOVERNANCE_CLOSURE_AUDIT — PASS`

- Post-2D-A Governance Closure: `CLOSED / ACCEPTED`
- Step 2D Candidate R3: `CLOSED / ACCEPTED`
- Accepted candidate identity: `V7_3_RECONSTRUCTED_PV_MAINLINE_CANDIDATE_R3`
- Accepted canonical data artifact:
  `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`
- Accepted canonical data-artifact SHA-256:
  `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`

The independent audit accepted only the exact audited reconstructed-PV mainline data artifact and
the exact post-2D-A governance-closure bytes. It did not perform or authorize production routing or
optimization.

## B. Accepted governance-closure bytes

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.md` | `32e873bb5a17e2b1dc3b90cf30cb6341fb1c36563e242698c9756748433f5705` | 16,381 |
| `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.json` | `ff870de5af30c54d1ad5d83fb7b3fb6837e3d00d797a396d3b12aae751d9cb3d` | 23,618 |

## C. Accepted R3 subject

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `scripts/20c_build_v7_3_reconstructed_pv_mainline_candidate_r3.py` | `e7af06409afd735e6556ee4cad64a2a1bd8cb26a772d0fe9c51b6d2727aff1ad` | 82,803 |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` | 554,037 |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23_manifest.json` | `f0e63614010d3a7450b5041409943fd94749d7b1af88ac4fd1c2b07701af9326` | 49,620 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/historical_canonical_to_candidate_column_diff.csv` | `18b926b65151c2b28ccc1a1f169d7fad1ef2286a2edfb6f37d9c86e0fbc4f96a` | 12,807 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/promotion_source_to_candidate_column_diff.csv` | `1a828db1cef3c1f1131883aeadc2299071db144a682327844de8f5477eb179ec` | 17,364 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/run_manifest.json` | `06f4a873770abc7b3488ba7d1d904a8824be583d4bb1898ae7fde4b7dcfdee27` | 50,439 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/package_manifest.json` | `454a6136fa81d55153d8f58e4252034b9c1d2cec604cb12e00582b394200cf14` | 2,471 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/completion_manifest.json` | `811ed297b67aeec15ea7b0839f2a35272887f15766768f6d4af3835b4ca0a281` | 15,582 |

## D. Current authority

| Role | Path | SHA-256 |
| --- | --- | --- |
| Methodology | `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| Evidence | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| Methodology/evidence lifecycle | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
| Version/provenance procedure | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |

No methodology was changed and no CLOSED scientific decision was reopened.

## E. Independent audit confirmations

The independent read-only audit confirmed from primary repository bytes:

- all eight R3 subject artifacts were exact;
- the closure Markdown and JSON were mutually consistent;
- R1 and R2 historical dispositions were truthful;
- the 83/86 difference was a `NON-BLOCKING EVIDENCE-ROSTER PERSISTENCE LIMITATION`;
- gates 77, 78, and 79 were independently reconstructible and each passed;
- all 28 controlled immutable members had zero drift;
- the governance implementation changed only the authorized three paths;
- model constructions, optimization calls, economic evaluations, and routing changes were zero;
- the audit itself caused zero repository mutation.

## F. Historical lineage

- Step 2D Candidate R1: `STOP / FAILED IMMUTABLE PROVENANCE`
- Step 2D Candidate R2: `STOP / ABANDONED IMMUTABLE PROVENANCE`
- Step 2D Candidate R3: `CLOSED / ACCEPTED`

R1 and R2 remain historical immutable provenance. They are excluded from this durability-freeze
commit except for their already-recorded references in accepted governance records.

## G. Epistemic boundary

Reconstructed long-unavailable PV values are model-based/weather-informed planning estimates and are
not observed truth, ground truth, or exact historical recovery.

## H. Downstream non-authorizations

| Item | Status |
| --- | --- |
| Step 2E | `NOT_YET_AUTHORIZED` |
| Production routing | `NOT_YET_AUTHORIZED` |
| EOB | `NOT_AUTHORIZED` |
| Layer A | `NOT_AUTHORIZED` |
| Layer B | `NOT_AUTHORIZED` |
| Final81 | `NOT_AUTHORIZED` |
| Optimization | `NOT_AUTHORIZED` |

This attestation and durability freeze do not authorize solving.

## I. Git durability-freeze target

- Branch: `thesis-v7`
- Authorized annotated tag: `v7.3-step2d-r3-accepted-2026-09-24`
- Freeze scope: the exact 13-path authority package authorized for this task.

The authoritative freeze commit and annotated-tag identities are Git metadata verified after
publication. This attestation intentionally does not attempt to encode the future commit SHA of the
commit containing itself.

## J. No-solve and no-routing assertions

- `model_constructions = 0`
- `optimization_calls = 0`
- `economic_evaluations = 0`
- `production_routing_changes = 0`

No EOB, representative case, Layer A, Layer B, Final81, winter-sensitivity solve, or production
runner was executed.
