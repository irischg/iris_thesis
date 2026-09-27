# Iris Thesis — v7.3 → v7.4 Version / Provenance Transition Record Candidate R2

**Package identity:** `V7_3_TO_V7_4_VERSION_TRANSITION_CANDIDATE_R2`  
**Date:** 2026-09-27  
**Mode:** primary-source-first; additive-only; bounded F-01 correction; zero solve  
**Lifecycle:** `CANDIDATE / NOT ACCEPTED / NOT CLOSED`  
**Producing-agent verdict:** `V7.3 → V7.4 VERSION TRANSITION RECORD — CANDIDATE R2 PASS`

This is an additive successor to Candidate R1. Candidate R1 remains byte-immutable
`HISTORICAL STOP CANDIDATE` provenance. This checkpoint does not accept R2, authorize production,
begin Task 3, or authorize a Full81 execution.

## A. Bounded purpose and authority boundary

Framework v7.4 and Registry v7.4 remain the closed/current methodology and evidence authorities.
Framework v7.3 and Registry v7.3 remain closed historical predecessors. The accepted reconstructed-PV
planning input, EOB, core-three, implementation, solver/configuration identities, and all numerical
artifacts are unchanged.

R2 corrects one provenance-history scoping defect, F-01. It does not create a fourth scientific change,
does not compare unlike historical/current routes, and does not reopen any accepted decision.

## B. Exact Git state

Literal status argv:

`git -c core.quotePath=false status --porcelain=v1 --untracked-files=all`

| Field | Pre-R2 | Post-R2 path creation |
|---|---|---|
| Repository | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis` | same |
| Branch | `thesis-v7` | same |
| HEAD | `53e3d5e38e68d000b25eea7d06d35b4600219c02` | same |
| Parent | `9050d0eabd0ee5c41626ba924c31a67f301c7293` | same |
| Local origin/thesis-v7 | `9050d0eabd0ee5c41626ba924c31a67f301c7293` | same |
| Live remote origin/thesis-v7 | `9050d0eabd0ee5c41626ba924c31a67f301c7293` | same |
| Ahead / behind | `1 / 0` | same |
| Staged / tracked dirty | `0 / 0` | `0 / 0` |
| Porcelain untracked records | `9` | `10` |
| Raw byte count | `526` | `605` |
| Raw SHA-256 | `d193286aead0e82cdcda855a8f7624fe66145429939746548fe581d181466b4e` | `376b5c22e983d7ad2d39222fb9d7e12aab83d70ea3d4d38dff0f2c05c27e698b` |

The pre-R2 state includes the R1 checkpoint. The post-R2 state adds only this R2 checkpoint to visible
porcelain; all ten R2 package files are ignored by the pre-existing `results/` rule. Raw Base64,
decoded exact text, and structured records are preserved in `git_state_snapshot.json`.

## C. R1 immutability

Before R2 writes, all 11 R1 artifacts were enumerated, byte-counted, and SHA-256 hashed. After R2
construction the same inventory was rechecked.

| Check | Result |
|---|---:|
| R1 files checked | 11 |
| SHA-256 mismatches | 0 |
| Byte-count mismatches | 0 |
| Lifecycle | `HISTORICAL STOP CANDIDATE` |

R1 was not edited, normalized, staged, moved, renamed, regenerated, or promoted.

## D. F-01 primary-evidence reconstruction

Historical run directory:

`results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da`

| Evidence | Independently verified value |
|---|---|
| Run identity | `20260911T112258206802Z_4d0eb9e1da` |
| Lineage | historical v7.2 R9 |
| Recursive files | 2,196 |
| Case directories | 81, plus an empty `.staging` directory |
| Per-case completion manifests | 81 |
| Completion manifest | 345,891 bytes; `5f18abe30100cfb6fb68ef9a38784c3c26ebcd5116f3a56656389fdd7b89b39d` |
| Completion status | `COMPLETE_PASS` |
| Surface solved | `true` |
| Optimization calls | 81 |
| Run manifest | 87,124 bytes; `d38627eabb08d9d286e1bdfcc78bfacb392b75e14477c924a2c88896bbb7428a` |
| Mode / execution flag | `PRODUCTION / true` |
| Script version | `v7.2-final-layer-a-81-production-runner-2026-09-11-r3` |
| Runner bytes | `scripts/19b_run_final_layer_a_81_cases.py`; 76,537 bytes; `4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe` |
| Execution repository HEAD/origin | `b03721275c73b05d45517bdf84c1e0bd03833376` |
| Historical input path | `data/processed/annual_input_v7_1.parquet` |
| Historical input SHA pinned by run manifest | `e0d4a8e84bee68c71f3d278e617df6fee0bb022a97c6fb5e9c49da6d6809fa0e` |
| Accepted v7.3 reconstructed-PV identity in historical manifest | absent |

The currently surviving file at the historical input path is 535,531 bytes with SHA-256
`9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e`, so it is not mislabeled as
the execution-time `e0d4…fa0e` bytes. The run manifest is the authority for the historical input
identity; exact historical input bytes are not claimed to survive at the same path.

Historical provenance was independently confirmed in:

- `docs/checkpoints/pre_corrected_rerun_version_lineage_v7_2_2026-09-15.md` — 19,535 bytes,
  `67b071ff50e1cc637d0c841e049c8d8ba553da29c6356e79bf2078d8577783d1`;
- `docs/checkpoints/v7_2_production_version_lineage_rerun_difference_freeze_2026-09-20.md` — 8,802 bytes,
  `865d9fdc26b7edd5b84f473a0f5e5c0e425f862923e786516cce6b0b4dcf5bab`.

## E. Historical/current route distinction

| State | Historical v7.2 R9 Final81 | Current accepted v7.3/v7.4 route |
|---|---|---|
| Exists/executed | Yes; completed 81-case production surface | Full81: no, on this route/input |
| Lifecycle | immutable historical provenance | current accepted route; Full81 pending |
| Planning input | `annual_input_v7_1.parquet` at execution-pinned SHA | `annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` |
| Cases/results | 81 historical cases | EOB and core-three accepted; current-route Full81 not executed |
| Current v7.4 Full81 | no | no |
| Full81 authorization | historical execution only; no present authority implied | not authorized |
| Comparable as controlled counterfactual | no | no numerical Full81 comparison exists yet |

The historical surface is not a v7.4 execution, is not evidence that current-route Full81 executed,
and cannot support a causal v7.3→v7.4 numerical delta.

## F. R1 → R2 bounded correction register

| ID | Source | Domain | R1 defect | R2 action | Status |
|---|---|---|---|---|---|
| C-01 | F-01 | Full81 execution universe | universal negative omitted historical v7.2 R9 surface | scope every current-state assertion to accepted v7.3/v7.4 route/input | corrected |
| C-02 | F-01 | source inventory | historical surface absent | register directory identity, manifests, runner, input identity, checkpoints, and Git objects | corrected |
| C-03 | F-01 | reconstructibility | R003 implied no historical completed Full81 | distinguish historical current-byte reconstruction from current-route pending state | corrected |
| C-04 | F-01 | difference matrix | D026 implementation wording overbroad | route-scope the statement and prohibit an invalid causal comparison | corrected |
| C-05 | F-02 | inherited handoff wording | separate observation in `CURRENT_STATE.md` | no change in this task | `DEFERRED_TO_SEPARATE_HANDOFF_PASS` |

No unrelated cleanup was performed.

## G. Scientific and implementation verdicts

Scientific change groups remain exactly three:

1. zero-winter current role;
2. observed-versus-planning PV epistemic routing, including no-hybrid routing;
3. κ historical-calibration/planning-use claim boundary.

Missing groups: `0`. Extra groups: `0`.

F-01 required no implementation change. Planning input, annual core, tariff, production stack, helpers,
preflights, solver fingerprint, parameter fingerprint, BESS, degradation, rainflow, resilience, and
outage replay remain unchanged. EOB and core-three retain execution identity at
`b87575c24aa7e85f77f9c43419b460943d71a9da`, unchanged artifact identity, and current
`CLOSED / ACCEPTED` governance status. They are not v7.4 reruns.

## H. Difference, authority, and reconstructibility matrices

Difference matrix: 27 records; changed `YES=9`, unchanged `NO=17`, `UNKNOWN=1`. D026 preserves
`new_value=NOT_YET_EXECUTED`, `changed=UNKNOWN`, `change_type=OPTIMIZATION_RESPONSE`, and both deltas
as `NOT_APPLICABLE`. Only its execution/evidence wording was route-scoped.

Authority matrix: 12 records. A012 retains current-route `NOT_YET_EXECUTED / NOT_YET_AUTHORIZED` and
adds the historical v7.2 R9 surface only as a non-current caveat. No authority changed.

Reconstructibility matrix: 3 records. R003 remains the current/future accepted-route outcome record.
Its code and accepted input are reconstructible; current-route execution identity/outcomes are not
reconstructible because that run has not occurred. The same record now explicitly states that the
historical v7.2 R9 surface survives locally, is only partially Git-durable, used a different input, and
is outside the comparison basis. No schema redesign or artificial fourth row was needed.

## I. Source inventory

| Inventory | R1 | R2 | Added |
|---|---:|---:|---:|
| Artifact records | 36 | 46 | 10 |
| Git objects | 14 | 17 | 3 |

Added artifacts S037–S044 reconstruct the historical directory identity, completion/run manifests,
runner, two lineage checkpoints, execution-pinned input identity, and same-path mismatch limitation.
S045–S046 register the immutable R1 checkpoint/package-manifest predecessor. Added Git objects are the
historical execution commit `b037212…`, annotated `v7.2-pre81-ready` tag object `2aeccf…`, and peeled
build-ready commit `b2acdf…`. Missing records: `0`; wrong hashes: `0`; wrong roles: `0`.

## J. JSON / CSV exact parity

Every CSV cell contains a JSON serialization and was independently decoded before dictionary equality
comparison with the canonical JSON records.

| Pair | Exact parity |
|---|---:|
| Difference | 27 / 27 |
| Authority | 12 / 12 |
| Reconstructibility | 3 / 3 |

Schema/key, order, type, and value mismatches: `0`.

## K. Overbroad-negative audit

Audit unit and final counts are recorded in `version_transition_summary.json` after a semantic review of
all active R2 files, including JSON/CSV mirrors and this checkpoint.

| Class | Count |
|---|---:|
| A — properly scoped current route/input | 57 |
| B — historical quotation/R1 defect description | 3 |
| C — invalid overbroad active statement | 0 |

## L. Non-mutation proof

Protected tracked authority, closure, handoff, protocol, implementation, and tag refs were checked by
exact bytes/refs. Ignored EOB, core-three, and historical v7.2 R9 run trees were checked with a
verification-only file inventory digest (sorted relative path, byte count, and per-file SHA-256); this
is not asserted as a canonical directory artifact hash.

| Protected family | Files | Verification result |
|---|---:|---|
| R1 candidate | 11 | exact; 0 mismatches |
| Framework/Registry v7.3/v7.4 and closures/manifests | 9 | exact; 0 mismatches |
| Accepted planning input | 1 | exact |
| Implementation/preflights/calibration | 9 | exact |
| Accepted EOB tree | 8 | exact inventory |
| Accepted core-three tree | 27 | exact inventory |
| Historical v7.2 R9 Full81 tree | 2,196 | exact inventory |
| `CURRENT_STATE.md` / `PROJECT_HANDOFF.md` | 2 | exact |
| Governing protocol | 1 | exact |
| Existing tag refs | 10 | exact |

Existing artifacts modified: `0`. Only the eleven authorized R2 paths are new.

## M. Zero-execution counters

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
| Commits / pushes / tags | 0 / 0 / 0 |

All work was static hashing, parsing, source/provenance inspection, Git-object/ref inspection,
directory inventory, parity checking, and manifest reconciliation. No model-bearing module was imported.

## N. R2 file family

1. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/version_transition_summary.json`
2. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/version_transition_difference_matrix.json`
3. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/version_transition_difference_matrix.csv`
4. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/authority_transition_matrix.json`
5. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/authority_transition_matrix.csv`
6. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/reconstructibility_matrix.json`
7. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/reconstructibility_matrix.csv`
8. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/git_state_snapshot.json`
9. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/source_artifact_inventory.json`
10. `results/provenance/v7_3_to_v7_4_version_transition_candidate_r2/package_manifest.json`
11. `docs/checkpoints/v7_3_to_v7_4_version_transition_candidate_r2_2026-09-27.md`

The package manifest omits its own hash/byte count to avoid circular identity and registers the other ten
files. Required/missing, hash, byte-count, and unexpected-file counters must all be zero.

## O. Unresolved observation and legal next step

F-02 inherited `CURRENT_STATE.md` wording remains intentionally unmodified and requires a separately
authorized future handoff correction. `PROJECT_HANDOFF.md` also remains unchanged.

Candidate R2 may proceed to an independent cross-agent read-only audit. It remains uncommitted and
unaccepted. Candidate R1 remains immutable historical STOP provenance. Do not accept R2, commit, push,
tag, begin Task 3, or run Full81 as part of this candidate task.

## P. Final disposition

> **V7.3 → V7.4 VERSION TRANSITION RECORD — CANDIDATE R2 PASS**
>
> Candidate R2 is internally verified and may proceed to independent cross-agent read-only audit.
> It remains `CANDIDATE / NOT ACCEPTED / NOT CLOSED`.
