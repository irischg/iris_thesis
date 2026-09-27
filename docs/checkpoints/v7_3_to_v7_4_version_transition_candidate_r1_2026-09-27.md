# V7.3 → V7.4 version / provenance transition record — Candidate R1

**Date:** 2026-09-27  
**Package identity:** `V7_3_TO_V7_4_VERSION_TRANSITION_CANDIDATE_R1`  
**Pass type:** primary-source-first, documentation/provenance only, zero solve  
**Lifecycle:** `CANDIDATE`; not self-accepting

## A. Candidate verdict

> **V7.3 → V7.4 VERSION / PROVENANCE TRANSITION RECORD — CANDIDATE PASS**

This producing pass found a coherent, reconstructible transition from the final v7.3-only repository
boundary to the accepted Framework/Registry v7.4 pair. It created only the eleven additive candidate
files authorized by the task. It did not modify any accepted or historical artifact, did not execute a
model, and did not perform a commit, push, or tag operation.

This is **not** an independent acceptance. A different agent must conduct a read-only audit before this
candidate may become accepted transition authority.

## B. Current authority state

| Domain | Current authority | Exact identity | Lifecycle |
|---|---|---|---|
| Methodology | **Framework v7.4** | `docs/research_framework_v7_4_2026-09-26_r2.md`; SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` | `CLOSED / ACCEPTED` |
| Evidence | **Registry v7.4** | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`; SHA-256 `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` | `CLOSED / ACCEPTED` |
| Accepted methodology predecessor | Framework v7.3 | `docs/research_framework_v7_3_2026-09-23.md`; SHA-256 `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` | immutable historical accepted predecessor |
| Accepted evidence predecessor | Registry v7.3 | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`; SHA-256 `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` | immutable historical accepted predecessor |

Formal names are **Framework v7.4** and **Registry v7.4**. Candidate suffixes are provenance revision
identities, not part of either formal version name.

## C. Final v7.3 boundary

The final v7.3-only boundary immediately before the first v7.4 artifact is:

- commit `1651b31008c565e105fc79a958f9ca98a194aa80`;
- parent `b87575c24aa7e85f77f9c43419b460943d71a9da`;
- subject `Repair post-core-three reporting JSON serialization`;
- successor: `5d81ee989856d42a21e715def4625162ea9fc0af`, the first Framework v7.4 Candidate R1 commit.

The accepted EOB and core-three runs record their execution-time authority at commit
`b87575c24aa7e85f77f9c43419b460943d71a9da`, with `HEAD = origin/thesis-v7`. The intervening
`1651b310` change adds narrow console JSON encoding for datetime-like and NumPy values; it changes no
published run artifact, equation, parameter, input, solver contract, or accepted numerical result.

## D. Transition commit sequence

| Commit | Parent | Transition role | Path scope |
|---|---|---|---|
| `1651b31008c565e105fc79a958f9ca98a194aa80` | `b87575c24aa7e85f77f9c43419b460943d71a9da` | final v7.3-only boundary | successor stack and 21b–21d/test reporting serialization only |
| `5d81ee989856d42a21e715def4625162ea9fc0af` | `1651b310…` | Framework v7.4 Candidate R1 | four additive Framework candidate/provenance files |
| `52be8dec7b8529b6fcb411bbee765f1aa4c745df` | `5d81ee98…` | Framework v7.4 Candidate R2 | four additive stale-status correction candidate/provenance files; no fourth science category |
| `2fe2105180c68d9289eddc2668399687d4c49d2e` | `52be8dec…` | Framework v7.4 acceptance | acceptance checkpoint + manifest |
| `bf87b7f0659da17277fbb797099141b24343aa79` | `2fe21051…` | Registry v7.4 Candidate R1 | four additive Registry alignment candidate/provenance files |
| `9e2f05c93d7642fc07881210983a030550455a17` | `bf87b7f0…` | post-Framework handoff refresh | two handoff files only |
| `9050d0eabd0ee5c41626ba924c31a67f301c7293` | `9e2f05c9…` | Registry v7.4 acceptance | independent audit record + acceptance checkpoint + manifest |
| `53e3d5e38e68d000b25eea7d06d35b4600219c02` | `9050d0ea…` | post-Registry handoff refresh | two handoff files only |

Relevant immutable tags:

- `v7.3-step2d-r3-accepted-2026-09-24`: tag object `d37e5f1fd1a562989038af895e31a68f89b03913`, peeled commit `07200697d0da7567715ec77edf3d853acbc53918`;
- `v7.3-step2e1-routing-authority-accepted-2026-09-24`: tag object `22c4091cbd584a7267c78f7e43046e76959855be`, peeled commit `d52d9584b22da2a41b51c8ce3e99a0335e39da2b`.

## E. Methodology versus implementation classification

The transition is a **methodology/claim-boundary authority successor plus evidence-authority
alignment**. It is not an implementation correction and not a numerical rerun.

- Methodology/specification change: exactly three accepted groups, listed in §F.
- Evidence change: Registry v7.4 aligns claim/evidence boundaries to those same three groups; no new
  external source and no fourth scientific category.
- Implementation change across `1651b310` → `53e3d5e3`: **none** in core, input authority, successor
  stack, preflights, data, parameters, solver settings, or results.
- Numerical change: **none**. EOB and core-three exact result identities are preserved.
- Governance/lifecycle change: Framework v7.4 and Registry v7.4 become current accepted authorities;
  their v7.3 counterparts become historical accepted predecessors.

## F. Exact science change set

The accepted v7.4 delta contains exactly these three groups:

1. **A — zero-winter current role.** Under v7.3 it was a conservative stress/sensitivity. Under v7.4
   its current role is historical conservative validation / provenance evidence supporting the
   reconstructed-PV promotion/adjudication decision. It is not a mandatory new EOB, Layer A, or Layer B
   sensitivity and is not an equal-status planning baseline. No replacement sensitivity is introduced.
2. **B — observed-versus-planning PV epistemic routing.** Historical empirical/calibration claims use
   observed data wherever valid. Planning/counterfactual consumers use one accepted reconstructed
   full-year PV identity. Hybrid fallback to zero-winter or any other annual PV identity is prohibited.
3. **C — \(\kappa\) historical-calibration / planning-use claim boundary.** Production
   `1.0103668594376984`, the through-origin estimator, the ten valid usage-month calibration period,
   and the observed-data calibration basis remain unchanged. Reconstructed planning PV cannot
   recalibrate \(\kappa\). The coefficient is a billing-demand representation proxy, not 15-minute
   chronology reconstruction or sub-hourly physical adequacy proof.

No equation, parameter, numerical setting, solver setting, production input, or accepted numerical
result changed.

## G. Meaningful unchanged set

The 27-row difference matrix records the following unchanged scientific/implementation families:

- planning input identity;
- tariff and billing-period methodology;
- BESS equations, SOC 10–90%, and `eta_c = eta_d = 0.90`;
- Xu-adapted intertemporal PWL degradation and B2 accounting;
- rainflow ex-post validation role;
- resilience definition and annual/replay stage separation;
- non-circular outage replay and `surplus_pv_recharge=False` for Layer A consistency replay;
- alpha grid `0.60:0.05:1.00` and beta grid `4:12 h`, giving the unchanged 9×9 universe;
- PNNL 10 MW full package as ex-ante mainline and 1 MW full package as sensitivity;
- constant NTD-2023, real 5% rate, 20-year horizon, and CRF treatment;
- solver contracts/fingerprint;
- production successor stack and fail-closed production gate;
- accepted EOB and core-three numerical artifacts.

## H. Input continuity

The accepted planning artifact is unchanged:

`data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`

- SHA-256: `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`
- Git blob: `d23dfbcca8c49703d11c20d4c4303a323035c84c`
- bytes: `554037`
- rows: `8760`
- role: `reconstructed_pv_mainline`
- accepted durability commit: `07200697d0da7567715ec77edf3d853acbc53918`

The exact same identity appears in the EOB authority, core-three authority, and all four annual-identity
contexts for every core-three case.

## I. Implementation continuity

| Component | Final v7.3 boundary / current identity | Finding |
|---|---|---|
| Scientific core | `src/annual_design_model_v7_2.py`; SHA-256 `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8`; blob `4724023c…` | exact continuity |
| Input authority | `src/production_input_authority_v7_3.py`; SHA-256 `f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1`; blob `c4e21749…` | exact continuity |
| Current successor stack | `src/production_successor_stack_v7_3.py`; SHA-256 `f1d7125f0ee7897db0e25486eca7dd562369d13b5dae1f5364aa4e0384c27323`; blob `041a7252…` | exact continuity from `1651b310` to HEAD |
| Execution-time successor stack | SHA-256 `5c5a9f7412c8eb40dafe65e52d54ba7cd725380ff4c9bc9e8948b2ecac915f20`; blob `de8d3e48…` at `b87575c` | preserved Git-reconstructible execution identity |

The current production gate still requires an explicit execution flag and fixed scope, branch
`thesis-v7`, Step 2E-1 ancestry, committed successor bytes, clean tracked/index state, equality of HEAD
and `origin/thesis-v7`, valid authority hashes, exact accepted input identity, absence of CSV fallback,
and absence of visible untracked authority-surface paths. This candidate grants no production authority.

## J. Accepted artifacts and Full81 state

### EOB

- path: `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556`
- result SHA-256: `14752e0fb78d585c4bb6f3ad3c8dcb14b60ad50311640840f3c8b7c248f52fe1`
- objective: `66622010.51124089 NTD-2023/year`
- historical execution-manifest state: `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`
- current governance state: `CLOSED / ACCEPTED`
- v7.4 continuing validity: `YES`; rerun required: `NO`

### Core-three

- path: `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55`
- LOW `a0.60_b04`: result SHA-256 `a70d784b94896fcb83586a7f3426bc496918637a7cc2d1c5f22db97fdd805ca0`
- CENTRAL `a0.80_b08`: result SHA-256 `9973f2ce5c6c52ae2b19a3e170c8f7a17f6a199e4d1d6d5ebee6a9a4ec72417c`
- HIGH `a1.00_b12`: result SHA-256 `9ad1cff430c644b97501c2216efafb5cb913785b4bb7ba48889189243123301f`
- historical execution-manifest state: `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`
- current governance state: `CLOSED / ACCEPTED`
- v7.4 continuing validity: `YES`; rerun required: `NO`

### Full81

`new_value = NOT_YET_EXECUTED`; `changed = UNKNOWN`; `change_type = OPTIMIZATION_RESPONSE`;
`numerical_delta = NOT_APPLICABLE`; `relative_delta = NOT_APPLICABLE`.

Only one `final_81_v7_3/runs` directory exists and it contains exactly three case directories. Core-three
acceptance is not Full81 completion. This package does not authorize Full81.

## K. Reconstructibility

| State | Current surviving bytes | Git-only durability | Overall finding |
|---|---|---|---|
| Actual final v7.3 state | `FULLY_RECONSTRUCTIBLE` | `PARTIALLY_RECONSTRUCTIBLE` | code, input, execution identity, and actual execution state are fully recoverable now |
| Actual accepted v7.4 state | `FULLY_RECONSTRUCTIBLE` | `PARTIALLY_RECONSTRUCTIBLE` | resolves to new accepted governance authorities plus unchanged accepted v7.3 code/input/runs |
| Future v7.4 Full81 outcomes | `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE` | same | `NOT_YET_EXECUTED`; no result may be inferred |

The limitation is durability, not present-day ambiguity: EOB and core-three run directories are
gitignored. The pre-existing EOB ZIP is an exact redundant copy: all eight ZIP entries match the
surviving EOB run files by byte count and SHA-256. No Git-durable core-three archive was found.

## L. Git provenance and non-mutation

Task-start repository identity:

- repository: `C:/Users/Iris C/OneDrive/Desktop/iris_thesis`
- branch: `thesis-v7`
- HEAD: `53e3d5e38e68d000b25eea7d06d35b4600219c02`
- parent: `9050d0eabd0ee5c41626ba924c31a67f301c7293`
- local `origin/thesis-v7`: `9050d0eabd0ee5c41626ba924c31a67f301c7293`
- live remote `origin/thesis-v7`: `9050d0eabd0ee5c41626ba924c31a67f301c7293`
- ahead/behind: `1/0`
- staged paths: `0`
- unstaged tracked paths: `0`
- pre-existing porcelain-untracked paths: `8`, preserved

Exact raw porcelain evidence is in `git_state_snapshot.json`:

- pre-task raw bytes: `447`; SHA-256 `2720879eb0de989bf50e4755e2c5518748a832a5295ecc5e1cdde237c3edbcd8`;
- post-build raw bytes: `526`; SHA-256 `d193286aead0e82cdcda855a8f7624fe66145429939746548fe581d181466b4e`;
- only new porcelain-visible path: this checkpoint;
- the ten package-directory files are ignored by the repository-wide `results/` rule and are therefore
  separately enumerated as authorized ignored paths.

No branch, HEAD, parent, local origin, or live remote ref changed. No staged or tracked modification was
introduced. No pre-existing untracked file was removed or altered by this task.

## M. Epistemic and causal-claim boundary

The winter PV reconstruction is model-based, weather-informed, separately validated planning evidence.
It is not observed historical PV, not exact ground truth, not exact recovery of the unavailable series,
and not online forecast information. Historical empirical/calibration statements remain on observed
data wherever valid.

There is no cross-version numerical result difference to causally attribute: accepted EOB and core-three
bytes are unchanged, and Full81 has not executed. Future numerical effects of v7.4 cannot be inferred
without separately authorized counterfactual solves.

## N. Zero-solve / zero-mutation proof

| Action | Count |
|---|---:|
| Model constructions | 0 |
| `optimize()` calls | 0 |
| MILP solves | 0 |
| EOB reruns | 0 |
| Core-three reruns | 0 |
| Full81 runs | 0 |
| Sensitivity solves | 0 |
| Code changes | 0 |
| Data changes | 0 |
| Accepted-result changes | 0 |
| Commits / pushes / tags | 0 / 0 / 0 |

All verification was static: file hashing, JSON/CSV parsing, source inspection, Git object/ref inspection,
manifest reconciliation, directory inventory, and ZIP-entry hashing. No model module was imported.

## O. Source-artifact inventory

`source_artifact_inventory.json` registers:

- 36 primary external artifact records;
- 14 Git commit/tag object records;
- exact path, SHA-256, byte count, role, lifecycle, Git tracking/blob identity, and reconstruction role
  for every file directly used to establish candidate facts.

The inventory distinguishes tracked authority from gitignored surviving execution bytes and the
pre-existing untracked EOB preservation ZIP.

## P. JSON / CSV exact parity

All paired ledgers were generated from the same canonical JSON records. Every CSV cell is a JSON
serialization; validation reloaded every cell with `json.loads()` and reconstructed the exact record.

| Pair | Exact records |
|---|---:|
| `version_transition_difference_matrix.json/.csv` | 27 / 27 |
| `authority_transition_matrix.json/.csv` | 12 / 12 |
| `reconstructibility_matrix.json/.csv` | 3 / 3 |

Schema identity, key order, types, values, and record order all match exactly.

## Q. Package verification

The package manifest registers nine non-manifest files in the package directory plus this external
checkpoint. The manifest deliberately omits its own hash and byte count to avoid circular identity.

Expected and verified counters:

- registered non-manifest artifacts: `10`;
- registered-but-missing: `0`;
- required-unregistered: `0`;
- SHA-256 mismatches: `0`;
- byte-count mismatches: `0`;
- unexpected files in the candidate namespace: `0`.

## R. Candidate files created

1. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/version_transition_summary.json`
2. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/version_transition_difference_matrix.json`
3. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/version_transition_difference_matrix.csv`
4. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/authority_transition_matrix.json`
5. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/authority_transition_matrix.csv`
6. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/reconstructibility_matrix.json`
7. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/reconstructibility_matrix.csv`
8. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/git_state_snapshot.json`
9. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/source_artifact_inventory.json`
10. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/package_manifest.json`
11. `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r1_2026-09-27.md`

No other path was created, modified, deleted, renamed, staged, or committed.

## S. Next legal step

Run an independent read-only audit by a different agent against primary repository bytes. The auditor
must independently re-derive the v7.3 boundary, the seven-commit v7.4 transition, the three-group science
delta, implementation/input/result continuity, exact JSON/CSV parity, package manifest integrity, and
before/after Git-state semantics. If the audit returns PASS, acceptance must be recorded additively; do
not rewrite this candidate.

Task 3, a production-authority re-freeze, and Full81 remain separate later gates. This candidate does not
authorize any of them.

## T. Final disposition

> **V7.3 → V7.4 VERSION / PROVENANCE TRANSITION RECORD — CANDIDATE PASS**
>
> Candidate R1 is complete and internally verified, but remains uncommitted and unaccepted pending an
> independent read-only audit by a different agent.
