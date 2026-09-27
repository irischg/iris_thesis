# v7.3 → v7.4 version / provenance transition acceptance closure

**Date:** 2026-09-27  
**Closure identity:** `V7_3_TO_V7_4_VERSION_TRANSITION_ACCEPTANCE_CLOSURE`  
**Disposition:** **CLOSED / ACCEPTED**  
**Pass type:** additive materialization of a separate independent cross-agent read-only audit; governance / provenance only  
**Scientific or numerical rerun required:** NO

## 1. Scope and authority of this closure

This checkpoint formally accepts and closes the exact immutable bytes of
`V7_3_TO_V7_4_VERSION_TRANSITION_CANDIDATE_R2` after a separate independent cross-agent read-only
audit returned `PASS`, concluded that Candidate R2 is independently acceptable, and found it eligible
for this separately authorized closure step.

This is not candidate authoring, candidate repair, methodology redesign, evidence expansion,
implementation work, a production-authority re-freeze, Task 3, or numerical execution. Acceptance is
conferred by this additive checkpoint and its companion manifest. Candidate R2's authoring-time
`CANDIDATE / NOT ACCEPTED / NOT CLOSED` self-text remains immutable historical provenance and is not
rewritten. Candidate R1 likewise remains immutable historical STOP provenance.

## 2. Pre-closure repository identity

| Item | Verified value |
|---|---|
| Repository | `irischg/iris_thesis` |
| Working tree | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis` |
| Branch | `thesis-v7` |
| Pre-closure HEAD | `53e3d5e38e68d000b25eea7d06d35b4600219c02` |
| Parent | `9050d0eabd0ee5c41626ba924c31a67f301c7293` |
| Local `origin/thesis-v7` | `9050d0eabd0ee5c41626ba924c31a67f301c7293` |
| Live remote `origin/thesis-v7` | `9050d0eabd0ee5c41626ba924c31a67f301c7293` |
| Ahead / behind | 1 / 0 |
| Staged paths | 0 |
| Unstaged tracked paths | 0 |
| Porcelain untracked records | 10: eight unrelated pre-existing paths plus R1 and R2 checkpoints |
| Exact porcelain byte count | 605 |
| Exact porcelain SHA-256 | `376b5c22e983d7ad2d39222fb9d7e12aab83d70ea3d4d38dff0f2c05c27e698b` |
| Existing tag refs | 10 |

Literal status command:

`git -c core.quotePath=false status --porcelain=v1 --untracked-files=all`

The local-only pre-closure HEAD is the expected post-Registry-v7.4 handoff refresh. Publication of this
closure therefore advances the remote through that already-existing parent and the new bounded closure
commit. No earlier commit is amended.

## 3. Governing additive-acceptance pattern

The governing version/provenance protocol requires independent audit before acceptance, immutable STOP
candidates, additive closure, deterministic manifests, and a separately authorized commit/publication
freeze. The established Framework v7.4 and Registry v7.4 closure pattern uses:

1. one additive human-readable acceptance checkpoint;
2. one additive machine-readable acceptance manifest;
3. a bounded closure commit and publication after verification;
4. no acceptance tag unless a separate established tag requirement exists.

This closure follows that pattern. No acceptance tag is required or created.

## 4. Candidate R1 — immutable historical STOP provenance

Candidate R1 remains permanently `IMMUTABLE HISTORICAL STOP PROVENANCE`. All 11 artifacts were
enumerated and rehashed before this closure; all hashes and byte counts match the pre-R2 and post-R2
inventories.

| Primary identity | Bytes | SHA-256 |
|---|---:|---|
| `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r1_2026-09-27.md` | 17667 | `a8f137ab528ea602e87e802f46d103b57763226932bc86191335f058611f31bf` |
| `results/provenance/v7_3_to_v7_4_version_transition_candidate_r1/package_manifest.json` | 7386 | `8eee7927114bf873a97e701bbb260c0f9ff670a354735f0c1a25b917e4f8c34b` |

R1 files checked: `11`; SHA mismatches: `0`; byte-count mismatches: `0`. R1 is not promoted by
this closure. It is committed only to make the failed first-candidate provenance durable.

## 5. Candidate R2 exact identity and lifecycle transition

| Primary identity | Bytes | SHA-256 |
|---|---:|---|
| `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r2_2026-09-27.md` | 13693 | `817a8ad54e2ba475b426bfd75b1e5085cf7433417f085562375b374a37b1b383` |
| `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/package_manifest.json` | 9185 | `7b1b0f85a12b4d1a8742820a0a645497a966ebc7237a415323999fb845f1f858` |

All 11 Candidate R2 artifacts were independently rehashed. Package identity is consistently
`V7_3_TO_V7_4_VERSION_TRANSITION_CANDIDATE_R2`; stale active R1 ownership labels are absent.

Lifecycle transition conferred by this closure:

`CANDIDATE / NOT ACCEPTED / NOT CLOSED` → **`CLOSED / ACCEPTED`**

The candidate bytes themselves remain unchanged. Their authoring-time lifecycle wording is retained as
historical self-text; this external closure is the current lifecycle authority.

## 6. Independent audit basis consumed

The separate audit established, among other acceptance-critical facts:

- Candidate R2 verdict: `PASS`;
- Candidate R2 independently acceptable: `YES`;
- eligible for a separately authorized acceptance/closure step: `YES`;
- R1 preserved 11/11;
- R003 and D026 corrected;
- historical/current Full81 distinction correct;
- scientific change groups: exactly 3, missing 0, extra 0;
- invalid overbroad active Full81 statements, Class C: 0;
- JSON/CSV parity: 27/27, 12/12, and 3/3 exact;
- package manifest and source inventory: PASS;
- F-02 untouched;
- methodology, evidence, implementation, and numerical mutations: 0;
- model constructions, optimization calls, and solves: 0.

The independent audit occurred in cross-agent governance history but no separate repository audit file
was supplied for this acceptance pass. No audit path or hash is fabricated. Acceptance rests on the
explicit independent PASS authorization plus fresh verification of the audited R1/R2 identities and
acceptance-critical primary bytes before this closure.

## 7. Historical v7.2 R9 Full81 evidence — preserved distinction

Historical run:

`results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da`

| Property | Verified state |
|---|---|
| Lifecycle | `EXISTS / HISTORICAL / IMMUTABLE / NON-CURRENT` |
| Recursive files | 2196 |
| Completion-manifest artifact registry entries | 2195 |
| Difference | completion manifest itself, intentionally self-excluded |
| `.staging` | empty; 0 files |
| Case directories / optimization calls | 81 / 81 |
| Completion status / surface solved | `COMPLETE_PASS` / `true` |
| Mode / execution flag | `PRODUCTION` / `true` |
| Input path | `data/processed/annual_input_v7_1.parquet` |
| Execution-pinned input SHA-256 | `e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e` |

This surface is historical v7.2 R9 provenance. It is not a v7.4 Full81 execution, not evidence of
current-route execution, and not a controlled counterfactual for the v7.3→v7.4 scientific changes.
No causal numerical delta is accepted from it.

## 8. Current accepted v7.3/v7.4 route state

| Item | State after this closure |
|---|---|
| Accepted planning input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`; unchanged |
| EOB | `CLOSED / ACCEPTED`; unchanged |
| Core-three | `CLOSED / ACCEPTED`; unchanged |
| Current-route Full81 | `NOT_YET_EXECUTED / NOT_YET_AUTHORIZED` |
| Task 3 | `NOT STARTED` |
| F-02 handoff wording observation | `DEFERRED` |

Accepting Candidate R2 does not authorize Task 3, a production-authority re-freeze, or Full81.

## 9. Frozen scientific change universe

The accepted v7.3→v7.4 scientific change universe remains exactly:

1. zero-winter role;
2. observed-versus-planning / no-hybrid PV routing;
3. κ historical-calibration/planning-use claim boundary.

No fourth scientific change is introduced. Equations, model structure, inputs, parameters, solver
configuration, tariffs, BESS semantics, degradation, rainflow, resilience, outage replay, units/scales,
and AC/DC semantics are unchanged.

## 10. Immutable authority and implementation identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Framework v7.4 | 216186 | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| Registry v7.4 | 245125 | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| Accepted planning input | 554037 | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| Annual scientific core | 124399 | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Production input authority | 13182 | `f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1` |
| Production successor stack | 70547 | `f1d7125f0ee7897db0e25486eca7dd562369d13b5dae1f5364aa4e0384c27323` |
| `CURRENT_STATE.md` | 29260 | `e8d5fddf843e488f2db5f747b098e81f0ada84ccbef92fd82c186f8a731848f1` |
| `PROJECT_HANDOFF.md` | 20260 | `348e4b9f059cceb659dff58eece85683a2519717a94331f7730d92a1437a5aba` |

The calibration and production preflight scripts were also rehashed and remain unchanged. EOB,
core-three, and historical Full81 ignored trees were checked by sorted file-level inventories; those
verification digests are non-canonical integrity checks, not newly invented directory identities.

## 11. Final lifecycle state conferred

| Item | Lifecycle |
|---|---|
| Framework v7.4 | `CLOSED / ACCEPTED` |
| Registry v7.4 | `CLOSED / ACCEPTED` |
| EOB | `CLOSED / ACCEPTED` |
| Core-three | `CLOSED / ACCEPTED` |
| Candidate R1 | `IMMUTABLE HISTORICAL STOP PROVENANCE` |
| **Candidate R2** | **`CLOSED / ACCEPTED`** |
| Historical v7.2 R9 Full81 | `EXISTS / HISTORICAL / IMMUTABLE / NON-CURRENT` |
| Current accepted v7.3/v7.4-route Full81 | `NOT_YET_EXECUTED / NOT_YET_AUTHORIZED` |
| F-02 | `DEFERRED` |
| Task 3 | `NOT STARTED` |

## 12. Execution and mutation counts

| Action | Count |
|---|---:|
| Model constructions | 0 |
| `optimize()` calls | 0 |
| MILP solves | 0 |
| EOB reruns | 0 |
| Core-three reruns | 0 |
| Historical Full81 reruns | 0 |
| Current Full81 runs | 0 |
| Sensitivity solves | 0 |
| Code changes | 0 |
| Data changes | 0 |
| Accepted-result changes | 0 |
| Candidate R1 modifications | 0 |
| Candidate R2 modifications | 0 |
| `CURRENT_STATE.md` modifications | 0 |
| `PROJECT_HANDOFF.md` modifications | 0 |

## 13. Additive artifacts and durability set

This closure creates exactly two new artifacts:

| Artifact | Role |
|---|---|
| `docs/checkpoints/v7_3_to_v7_4_version_transition_acceptance_closure_2026-09-27.md` | this acceptance/closure checkpoint |
| `results/provenance/v7_3_to_v7_4_version_transition_acceptance_closure_2026-09-27/acceptance_manifest.json` | deterministic machine-readable acceptance manifest |

The bounded durability commit also includes the previously untracked/ignored immutable R1 and R2
candidate families: 11 files each. This makes the failed R1 provenance, audited R2 identity, and
external acceptance lifecycle authority reproducible from Git history. It changes none of those 22
candidate files.

The companion manifest registers this checkpoint's exact hash and byte count and all R1/R2 identities.
It deliberately omits its own digest to avoid circular self-identity. Its digest and the containing
commit are reported externally after generation/publication.

## 14. Commit, push, and tag boundary

This acceptance instruction separately authorizes the minimum durability action required by the
governing protocol. After pre-commit verification, one bounded commit may add the 22 immutable candidate
files and two closure artifacts. The remote ref must be reverified immediately before publication.

No tag is required by the governing protocol or the established Framework/Registry closure pattern;
therefore no tag is created. No unrelated pre-existing untracked path may be staged or committed.

## 15. Next legal step

This closure does not automatically authorize Task 3 or Full81. The next separately authorized
governance task is the bounded F-02 handoff wording correction. `CURRENT_STATE.md` and
`PROJECT_HANDOFF.md` remain untouched in this pass.

## 16. Closure statement

> **V7.3 → V7.4 VERSION / PROVENANCE TRANSITION CANDIDATE R2 — CLOSED / ACCEPTED.**
>
> Candidate R1 remains immutable historical STOP provenance. Historical v7.2 R9 Full81 remains
> historical/non-current. Current accepted-route Full81 remains `NOT_YET_EXECUTED /
> NOT_YET_AUTHORIZED`. F-02 remains deferred and Task 3 remains not started.
