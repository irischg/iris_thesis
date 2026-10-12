# Current-Mainline Pointer Candidate R1 — Candidate Implementation Checkpoint

**Date:** 2026-10-12
**Package:** `CURRENT_MAINLINE_POINTER_CANDIDATE_R1`
**Lifecycle recorded here:** `CANDIDATE / NOT ACCEPTED / NOT CANONICAL / NOT CURRENT AUTHORITY`,
pending an independent read-only audit by a fresh separate operator.

**This checkpoint is not** an acceptance, an independent audit, an activation of the canonical pointer,
a publication, an exposure log, a pipeline notebook, a results analysis or an execution authorization.
Nothing in this package is staged, committed, pushed or tagged. Creating a JSON file does not complete
Step 4.

## 1. What this candidate is

A current-mainline pointer is a read-first routing index. It answers one question for Claude Code, Codex,
PowerShell, the future Pipeline Manager notebook and downstream analysis code: which methodology, evidence
authority, production implementation, canonical input and formally accepted result set are current, and can
their identities be verified?

This package proposes that pointer as a **candidate** and adds a read-only verifier for it. The pointer is
not a governance authority of its own: every identity in it is re-derived from live bytes and Git objects
and cross-checked against the accepted primary artifacts it routes to. It replaces none of them and grants
no production execution authority.

## 2. Files created

| Path | Role | Bytes | SHA-256 |
| --- | --- | --- | --- |
| `configs/candidates/current_mainline_pointer_candidate_r1.json` | candidate pointer | 53873 | `1619627b0b1e3d28f16e2d985bf83a8d47d8743402d07cb87f8cfb9abea5c24f` |
| `src/current_mainline_pointer_v1.py` | read-only verifier | 118860 | `fc73068a6a469842a7c234d4c07dac1baba1d669fc9c5a1adf2449b571d483e0` |
| `tests/test_current_mainline_pointer_v1.py` | focused zero-solve tests | 96372 | `887ac34c56d2d9149e005e28b4b16bc6656c1284250077bb11ceea84d9db4188` |
| `docs/checkpoints/current_mainline_pointer_candidate_r1_2026-10-12.md` | this checkpoint | registered by the manifest | registered by the manifest |
| `results/provenance/current_mainline_pointer_candidate_r1/candidate_manifest.json` | candidate manifest | omitted by design | omitted by design (no circular self-hash) |

All five are new files. Hashes are over LF bytes as written. The pointer embeds no hash of itself, of the
verifier, of the tests, of this checkpoint or of the manifest; the verifier and the tests embed no hash at
all; this checkpoint quotes no hash of the manifest. Pointer payload digest (the pointer minus its lifecycle
envelope): `1c118f22350aa21d74b04f94307be8bbb43d694023e5350b1edf512824980fdf`.

**Storage.** The proposed canonical path is `configs/current_mainline_pointer.json`: `configs/` is
Git-tracked, stable and not ignored, unlike `results/`. That file is **not created**. The candidate lives at
`configs/candidates/current_mainline_pointer_candidate_r1.json`. No other pointer, canonical or candidate, existed before this pass. Every path in the pointer is
repository-relative POSIX; no absolute path or drive letter is part of any identity.

## 3. Pointer schema `iris-thesis-current-mainline-pointer-v1`, revision `R1`

| Section | Carries |
| --- | --- |
| `artifact_type`, `schema_version`, `pointer_revision`, `documentation` | schema identity; purpose, serialization and path convention |
| `pointer_identity`, `activation_basis` | lifecycle envelope: candidate flags, proposed canonical path, absent activation basis |
| `methodology_authority`, `evidence_authority` | Framework v7.4 and Registry v7.4, their acceptance records and acceptance commits |
| `production_generation` | G1 ids, accepted lifecycle record, five lifecycle roles, three identity-axis digests |
| `full81_authorizations` | scope authorization, no-solve preflight evidence, execution authorization (historical provenance only) |
| `canonical_annual_input`, `implementation`, `economic_parameter_interfaces` | input, model core, successor stack, runner, parameter registry, execution-input authority |
| `accepted_result_set` | run id and path, 81-case universe, root artifacts, registration counts, run-file aggregate, two status layers, Git durability |
| `independent_audit_evidence_publication`, `formal_results_acceptance` | the two published packages and their publication commits |
| `git_provenance` | historical execution commit versus governance publication commits; ancestry chain |
| `roles` | accepted-current list (exact); advisory historical-only and other-scope lists |
| `open_findings_and_limitations`, `scientific_exposure_restrictions` | every carried finding, U-01, limitations, blocked and permitted purposes |
| `non_authorization_boundaries`, `validation_contract` | what the pointer does not authorize; required checks and verifier interface |

Text under a key named `note` or `documentation`, or ending in `_note`, is explanation and is not verified.
Every other payload value is checked against a primary artifact, a Git object or the verifier interface.

**Two status layers are kept separate.** Execution-time completion manifest status:
`COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE` (historical, bytes not rewritten).
Current governance status of the results: `CLOSED / ACCEPTED / PUBLISHED`, carried by the additive results
acceptance and proven published from Git, not self-asserted.

## 4. Identity bindings

Production generation `CURRENT_FULL81_PRODUCTION_GENERATION_G1` (candidate `CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1`), freeze status
`FROZEN`. Accepted run `20261008T183934456307Z_a6826f4828` at `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828`: case
set `full81`, 81 cases, 651 files and
156562246 bytes, 650 root and 567
case registrations, run-file aggregate `7d0e2d0c066d956080445f66236bc91ed97ad5cd8d8256f6617a4f2b07b12c41`.

| Item | Path | SHA-256 | Git anchor |
| --- | --- | --- | --- |
| Framework v7.4 (methodology) | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` | `c8f5550` (content at) |
| Framework v7.4 acceptance closure | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` | `2fe2105` (added by) |
| Registry v7.4 (evidence) | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` | `c8f5550` (content at) |
| Registry v7.4 acceptance closure | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` | `9050d0e` (added by) |
| G1 accepted lifecycle record | `results/provenance/current_full81_production_generation_g1_accepted_lifecycle/accepted_lifecycle_record.json` | `f1d798ab357ff82454f3030587b3cda30e13b55bf890a2b7257bbb40c325d3b0` | `b31d88c` (added by) |
| G1 candidate manifest (identity path lists) | `results/provenance/current_full81_production_generation_g1_candidate_r1_2026-10-07/g1_candidate_manifest.json` | `bd3621cf9de16a6b7ed0c84444272cd17ce28326b2f4081317c926cd3aa1071a` | `59e530f` (added by) |
| Main Full81 scope authorization | `results/provenance/main_full81_authorization_g1/main_full81_authorization.json` | `0dc75214904682476def42f36e73688a1f1d254523f20bfd319e6561c4a81338` | `ab5c7be` (added by) |
| Main Full81 no-solve preflight evidence | `results/provenance/main_full81_no_solve_preflight_g1/main_full81_21d_no_solve_preflight_evidence.json` | `95047e2fa9c0d524d5c43c0fdcafe40a93662c4282fd1aaaf0558be681f4da76` | `21ff5f4` (added by) |
| Main Full81 execution authorization | `results/provenance/main_full81_execution_authorization_g1/main_full81_execution_authorization.json` | `87ec6643deef262bc3710b2e1d7e76d582bcfd1eebd41ffdc6c6c71eb2f12c6e` | `c8f5550` (added by) |
| Canonical annual planning input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` | `c8f5550` (content at) |
| Scientific model core | `src/annual_design_model_v7_2.py` | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` | `c8f5550` (content at) |
| Production successor stack | `src/production_successor_stack_v7_3.py` | `65728c40e8df746da92865e859072c345370ae93aa4a2b32a24b149c67a3dcda` | `c8f5550` (content at) |
| Production runner | `scripts/21d_preflight_v7_3_final81_successor.py` | `1a55c34897548a3595a9812dfeaa854f3b6b478594630c750931cd7cf2371bd1` | `c8f5550` (content at) |
| Parameter registry | `data/reference/parameter_registry_v7_2.csv` | `c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1` | `c8f5550` (content at) |
| Execution-input authority | `data/reference/production_economic_interface_v7_2.json` | `9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9` | `c8f5550` (content at) |
| Execution-input authority | `data/reference/taipower_seasonal_settlement_matrix_v7_2.csv` | `ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79` | `c8f5550` (content at) |
| Execution-input authority | `data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv` | `5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395` | `c8f5550` (content at) |
| Execution-input authority | `data/reference/taipower_transition_period_settlement_interface_v7_2.json` | `f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88` | `c8f5550` (content at) |
| Run root completion manifest | `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828/completion_manifest.json` | `d5c647846e4ec4ddfedd50ff2fed837f70e5398dedd95d0fea90dfc5fcad7d24` | local only, not Git-tracked |
| Run authority snapshot | `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828/authority.json` | `ecef360b340de92b2f1f612b7028efebfa1b26986fa9fe22efad66a46b3442bb` | local only, not Git-tracked |
| Run case schedule | `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828/case_schedule.json` | `08b05f654dbf997fb91ed4d835594d3f796567e47882e478b9fa05e5ba240df4` | local only, not Git-tracked |
| Audit report (verbatim source copy) | `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/independent_audit_report.md` | `c6a07064451fa98f84fd714d09d59ed93eabc3e1b8d3e0461dd664e47937d394` | `5992624` (added by) |
| Audit evidence record | `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/audit_evidence_record.json` | `a02f05e52862a3f99abb0d56e5f8b44d1a6ee851ad2f6fdbc012b1bd608ac3fa` | `5992624` (added by) |
| Audit publication manifest | `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/publication_manifest.json` | `9f90449b31175f17d78d74cccf68764cf2e587f507a4bd13719b957d3d539337` | `5992624` (added by) |
| Audit publication checkpoint | `docs/checkpoints/full81_g1_postsolve_audit_evidence_publication_r1_2026-10-12.md` | `6d7c49dd68e44d42915e2d4584a4be148032650475645b8b4a1bd9c1a2dc5f84` | `5992624` (added by) |
| Results acceptance closure | `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_closure.json` | `3b27f9a60f5e0bfbcffde343aad164e74cff2f8a98581d91fb95d4bc90e2ba02` | `fcb35fc` (added by) |
| Results acceptance manifest | `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_manifest.json` | `c3137a9779585f18c340317b271b68a5fbd20b447cc7c47cc0c799589b1c5aed` | `fcb35fc` (added by) |
| Results acceptance checkpoint | `docs/checkpoints/full81_g1_postsolve_results_acceptance_r1_2026-10-12.md` | `451587a89f217fedad0c3b8b6f387f735619ef901316fbe9367f798d6e327e38` | `fcb35fc` (added by) |
| Governing exposure clause (sequencing closure) | `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md` | `9f1af8e805b23f6e16c827ada645bfff7d920d98a24b70fb2ea448683ec78851` | `c8f5550` (content at) |

G1 identity digests, recomputed from live raw bytes and from the blobs of the historical execution commit:
runtime `8cca5e81d62ab3976aaeeeea162bdfdca7867af4871156446bbcae4ece65eabc` (21 paths), validation
`1bd49904e8d774c27b5e8a0390240eb836e92fa6cf857948f7b9d3486914111b` (9), governance authority
`360c81b133440e1b0444e01f2fd120eb1f49d0db3501283773a2952c032dbeb4` (26). Solver-parameter
fingerprint `598dc4365ce65055aa509f6c98a87ba91b173ff361e06119000bf165af4fdebe`. Framework v7.4 acceptance commit
`2fe2105180c68d9289eddc2668399687d4c49d2e`; Registry v7.4 acceptance commit
`9050d0eabd0ee5c41626ba924c31a67f301c7293`.

| Commit role | Commit |
| --- | --- |
| 1. G1 candidate and independent audit PASS publication (Phase A) | `59e530f3a7d78c0480fa1368c56331f11e5731f0` |
| 2. G1 acceptance publication (Phase B) | `bdbe0637a1de41cea0c2d2391149fe1a86e684e3` |
| 3. G1 production-authority re-freeze and accepted lifecycle publication (Phase C) | `b31d88c35d4d86bd4a4294bb783737d18d9e287e` |
| 4. Main Full81 scope authorization publication | `ab5c7bea4fdcd28e0ca967daadc80d86f25c7588` |
| 5. Main Full81 no-solve preflight evidence publication | `21ff5f48a606f88b2dcd5429ddb10799341f3aeb` |
| 6. Main Full81 execution authorization publication = historical execution commit | `c8f555094d6ab711ce6426302419fff958ed19fa` |
| 7. Full81 post-solve independent audit evidence publication | `5992624e26d19304c1fc76f09c2ce128ab0e7215` |
| 8. Full81 numerical results acceptance publication | `fcb35fcbe8edd8095822a32d2cae8c8b45f45a1f` |

The historical execution commit is `c8f555094d6ab711ce6426302419fff958ed19fa`. The audit-evidence publication
`5992624e26d19304c1fc76f09c2ce128ab0e7215` is its direct child and the results-acceptance publication
`fcb35fcbe8edd8095822a32d2cae8c8b45f45a1f` is the direct child of that. The live HEAD is never
required to equal any of them. Every owner-stated identity of the Step 4 instruction reproduced from live
bytes; none was taken on trust.

## 5. Verifier `src/current_mainline_pointer_v1.py`

Standard library only. It imports no solver, builds no model, calls no `optimize()`, writes no file, runs
only seven read-only Git subcommands and contains no hash or commit literal, so it cannot become a second
pointer.

- **Candidate mode** reads a file under `configs/candidates/` and reports
  `CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY` or `FAIL_CLOSED`. `is_current_authority` and
  `results_consumption_permitted` are always false in this mode.
- **Canonical mode** reads only `configs/current_mainline_pointer.json`. Absent, candidate-only, unpublished,
  mismatched or stale: `FAIL_CLOSED`, with no substitute route. On the live repository it
  returns `CANONICAL_POINTER_ABSENT`.
- **Thirteen checks**: `C01_SCHEMA`, `C02_POINTER_LIFECYCLE_AND_MODE`, `C03_PATH_CONTAINMENT`, `C04_GIT_PROVENANCE`, `C05_FILE_IDENTITIES_RAW_BYTES_AND_GIT_BLOBS`, `C06_G1_IDENTITY_AXES`, `C07_GOVERNANCE_STATUS_AND_CROSS_BINDINGS`, `C08_CASE_UNIVERSE_AND_RUN_BINDING`, `C09_ROLES_AND_CONFLICTING_CLAIMS`, `C10_OPEN_FINDINGS_AND_SCIENTIFIC_EXPOSURE`, `C11_NON_AUTHORIZATION_BOUNDARIES`, `C12_LOCAL_RESULT_REGISTRATIONS`, `C13_CANONICAL_ACTIVATION_BASIS`.
- **Two hash axes, reported separately**: raw working-tree SHA-256, and Git blob identity (blob id at the
  anchor commit and in the live HEAD, plus the SHA-256 of the blob bytes). A raw mismatch is classified as an
  EOL conversion or a content difference and fails closed either way.
- **Publication commits are proven, not asserted**: a record bound to its publication commit must be absent
  from that commit's parents.
- **258 cross-binding rows** compare the pointer with nine records (seven tracked
  governance records and the run's two local root records); 49 internal
  equalities keep the pointer consistent with itself and with the verifier interface.
- **Three result policies**: `NOT_CHECKED`; `METADATA_ONLY`, reported as
  `METADATA_ONLY_NOT_FULL_INTEGRITY`; `STRICT_FULL_REHASH`, which re-hashes every file under the run
  against the root and case registrations and recomputes the run-file aggregate recorded by the results
  acceptance. Only strict verification of a verified canonical pointer permits results consumption.
- **Purpose gate** `require_current_mainline`: default deny; a purpose blocked by an open
  scientific-exposure restriction is refused.

Canonical activation follows a **proposed, unaccepted contract** (audited candidate, independent audit
record, acceptance closure and acceptance manifest, each bound to its publication commit, with the canonical
payload digest equal to the audited one). No activation artifact exists and no digest of one is reserved.

## 6. Verification and tests on the final bytes

Candidate verification of the real pointer against the real repository:

| Result policy | Verdict | Results integrity |
| --- | --- | --- |
| `NOT_CHECKED` | `CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY` | `NOT_CHECKED` |
| `METADATA_ONLY` | `CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY` | `METADATA_ONLY_NOT_FULL_INTEGRITY` |
| `STRICT_FULL_REHASH` | `CANDIDATE_INTERNALLY_CONSISTENT_NOT_ACCEPTED_NOT_AUTHORITY` | `STRICT_FULL_INTEGRITY_PASS` |

`tests/test_current_mainline_pointer_v1.py`: **59 tests, 59 passed, 0 failed, 0 errors, 0 skipped**, run as two commands against the final
bytes (39 static, path and hermetic-fixture tests in 196.3 s; 20 live-repository tests in 437.2 s). No
pre-existing suite was run and no production script was invoked.

- *Static*: standard-library imports only; no solver, model or `optimize` reference; no file write; only
  read-only Git subcommands; no identity literal; no entry point that promotes or activates.
- *Live*, in-memory negative controls on the real pointer and real records: wrong Framework, Registry,
  annual input, generation, run id, runtime digest, results-acceptance reference, commit, blob id or anchor;
  conflated status layers; a historical, core-three, v7.2 or staging namespace repointed as current; paths
  escaping the repository; dropped, closed or re-graded findings; unblocked purposes; a claimed exposure log;
  claimed execution authority.
- *Mutation sweep*: each of the pointer's 688 payload values was mutated once. 66 sit under descriptive keys.
  Of the other 622, 604 mutations fail closed and 18 are explained: `pointer_revision` (the pointer's own
  name), the per-case status string (bound under the strict policy only) and the two advisory role lists.
  The sweep found and closed real gaps during authoring, including identities inside lists that were not
  being hash-checked.
- *Hermetic fixture* (a throwaway repository of synthetic bytes; no real result byte, no alternates):
  canonical verification positive path; absent canonical pointer; candidate bytes at the canonical path;
  unpublished, tampered-payload, role-aliased, role-substituted and stale canonical pointers; later commits
  that preserve identities; missing, extra, resized and content-altered result files; a directory junction
  standing in for the run; an EOL-converted working tree; unpublished history.

## 7. Findings and restrictions carried — none closed, none remediated, none re-graded

| ID | Severity | Disposition | Purposes blocked while open |
| --- | --- | --- | --- |
| `ACC-N1` | MAJOR | OPEN | SCIENTIFIC_INSPECTION, RESULTS_ANALYSIS, SUPERVISOR_DISCUSSION |
| `ACC-OBS-1` | MINOR | OPEN | none |
| `ACC-OBS-2` | INFORMATIONAL | OPEN / CARRIED | none |
| `ACC-OBS-3` | INFORMATIONAL | DISCLOSED / CARRIED | none |
| `ACC-OBS-4` | MINOR | OPEN / CARRIED | none |
| `ACC-OBS-5` | INFORMATIONAL | DISCLOSED | none |
| `ACC-OBS-6` | MINOR | OPEN / CARRIED | none |
| `AUD-N1` | MODERATE | NONBLOCKING | none |
| `AUD-N2` | MODERATE | OPEN / NONBLOCKING | none |
| `AUD-N3` | MINOR | NONBLOCKING | none |
| `AUD-N4` | INFORMATIONAL | NONBLOCKING | none |
| `G1-N1` | MINOR | CARRIED / NONBLOCKING | none |
| `G1-N2` | MAJOR | CARRIED / NONBLOCKING | none |
| `G1-N3` | INFORMATIONAL | CARRIED | none |
| `R7_BINDING_AND_PRESERVATION_GIT_DURABILITY` | MAJOR | CARRIED / NONBLOCKING | none |
| `SAR-N1` | MINOR–MODERATE | CARRIED / NONBLOCKING | none |
| `SAR-N2` | MINOR–MODERATE | CARRIED / NONBLOCKING | none |
| `SAR-N3` | MINOR–MODERATE | CARRIED / NONBLOCKING | none |
| `SAR-N4` | MINOR–MODERATE | CARRIED / NONBLOCKING | none |

Severity and disposition are copied from the accepted results acceptance and compared with it by the
verifier. `U-01` is `OPEN_HOLD` (OPEN / HOLD), as recorded by the G1 scope authorization; A2 stays
`HARD_BLOCKED_UNTIL_U_01_RESOLVED_AUDITED_ACCEPTED_AND_FROZEN`. The fixture-control limitation stays
53/54. The 651 result files remain locally retained and **not Git-durable**.

**`ACC-N1` (MAJOR / OPEN) still blocks** the first scientific inspection, results analysis and any
supervisor discussion. No exposure log exists; none was created and none is claimed. The pointer blocks the
purposes `SCIENTIFIC_INSPECTION, RESULTS_ANALYSIS, SUPERVISOR_DISCUSSION` and permits only
`TECHNICAL_IDENTITY_VERIFICATION`. Authoring and verification displayed no case-level
sizing, objective value, response surface, ranking or turning point; result files were hashed as opaque
bytes.

## 8. Observations from this pass

Severities are the authoring operator's own assessment and are for the independent auditor to revise.

| ID | Severity | Observation |
| --- | --- | --- |
| `PTR-OBS-1` | MODERATE | While untracked, `src/current_mainline_pointer_v1.py` and `tests/test_current_mainline_pointer_v1.py` are untracked files under gate-protected prefixes. Read from source, not executed: the production gate lists untracked paths under `src/` and `tests/`, so it is expected to fail closed until these files are published or removed. No production execution is authorized or pending. |
| `PTR-OBS-2` | MINOR | The live test layer assumes the state bound by Candidate R1 is the live state. When a later accepted pointer revision supersedes R1, those tests are to be retired with it, not edited until they pass. |
| `PTR-OBS-3` | MINOR | The canonical activation contract is proposed and unaccepted. It was exercised on synthetic artifacts only. |
| `PTR-OBS-4` | MINOR | This revision binds the Full81 Layer A result set only. The accepted EOB and core-three runs are listed but neither bound nor verified. |
| `PTR-OBS-5` | MINOR | The verifier makes no network call: "published" is proven against the local remote-tracking ref. One read-only `git ls-remote` at authoring returned the results-acceptance commit as the remote head. |
| `PTR-OBS-6` | MINOR | The pinned `.gitattributes` cannot be extended without changing the frozen G1 governance identity, so the new files have no EOL rule; a CRLF-converting checkout changes their working-tree hashes and the verifier then fails closed, naming the cause. |
| `PTR-OBS-7` | INFORMATIONAL | The verifier checks identities and cross-bindings. It does not re-run the G1 lifecycle role validators, because it must never import the production stack. |
| `PTR-OBS-8` | INFORMATIONAL | The Constitution and the 2026-10-12 handoff were read from outside the repository. The handoff predates the audit publication and the results acceptance; live artifacts were used. Framework v7.4 was read in its header, sections 0.1 to 0.3 and 3.4, and Registry v7.4 in its header, not in full. |
| `PTR-OBS-9` | INFORMATIONAL | The pointer, this checkpoint and the manifest were generated by session-local scripts that are not part of the package. The pointer is verified independently of how it was authored. |
| `PTR-OBS-10` | INFORMATIONAL | A candidate PASS shows the pointer agrees with the accepted records it names. Whether it names the right records is a question for the independent audit. |

## 9. Git state and non-mutation

Branch `thesis-v7`; HEAD before and after `fcb35fcbe8edd8095822a32d2cae8c8b45f45a1f`, equal to
the upstream tracking ref. Nothing staged; no commit, push, tag, reset, clean or stash. The Git index file,
the ref set and the tracked index entries are byte-identical before and after. The working-tree delta is
exactly four new untracked files (the pointer, the verifier, the tests and this checkpoint) plus the
manifest under the ignored `results/` tree. All pre-existing unrelated working-tree entries are preserved.
No accepted or historical file was modified: not the Framework, the Registry, any G1 code, runner, model or
validation file, any authorization or run manifest, any audit-publication or results-acceptance artifact, any
handoff file, `.gitignore` or `.gitattributes`. The run's 651 files re-hash to the
accepted run-file aggregate before and after.

## 10. Zero execution

Solver-library imports 0; model constructions 0; `optimize()` calls 0; production scripts, gates and
preflights executed 0; pre-existing test suites executed 0; A2, Layer B, DG and sensitivity solves 0;
exposure-log entries created 0.

## 11. Lifecycle boundary

**Before:** Full81 numerical results `CLOSED / ACCEPTED / PUBLISHED`; no current-mainline pointer.

**After this pass:** a candidate pointer, a verifier, tests and this evidence exist, uncommitted.
Lifecycle: `CANDIDATE`, `NOT ACCEPTED`, `NOT CANONICAL`.

**Still not authorized:** acceptance or activation of the pointer; creation of the canonical file; commit,
push or tag; a pipeline notebook, dependency graph, selective rerun planner or controlled executor; an
exposure log; any scientific inspection, results analysis or supervisor discussion; any solve; A2, Layer B,
DG or sensitivity work; remediation of any finding.

**Next legal gate:** an independent read-only audit of this candidate by a fresh separate operator.
