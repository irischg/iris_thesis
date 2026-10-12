# Full81 G1 Post-Solve Independent Audit Evidence Publication R1 — Phase A

**Date:** 2026-10-12
**Package:** `FULL81_G1_POSTSOLVE_AUDIT_EVIDENCE_PUBLICATION_R1`
**Lifecycle result recorded here:** `FULL81_POSTSOLVE_INDEPENDENT_AUDIT_EVIDENCE` authored for Phase A
publication; `RESULT_ACCEPTANCE_PENDING`.

Whether this evidence is *published* is determined from live Git only: the four files listed in
section 7 must be contained, byte-identical, in one commit reachable from `origin/thesis-v7`. This
checkpoint embeds no containing commit id, no accepted-at timestamp and no tag, because none of those
existed when it was written.

**This checkpoint is not** a Full81 result acceptance, an acceptance closure, an accepted-lifecycle or
re-freeze record, a current-mainline pointer, or any production or execution authority. The Full81
results remain `NOT_ACCEPTED / NOT_CLOSED`.

## 1. What this package is

A separate Codex session performed an independent, read-only post-solve audit of the completed Main Full81
run and reported `FULL81 POST-SOLVE INDEPENDENT ACCEPTANCE — PASS`. This package places that audit
transcript, and a machine-readable record tying it to the exact run, under Git so that the reported PASS
is traceable. It changes no result, no implementation, no methodology and no earlier record.

- Machine-readable record: `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/audit_evidence_record.json`
  (SHA-256 `a02f05e52862a3f99abb0d56e5f8b44d1a6ee851ad2f6fdbc012b1bd608ac3fa`, 88562 bytes).
- Audit transcript copy: `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/independent_audit_report.md`
  (SHA-256 `c6a07064451fa98f84fd714d09d59ed93eabc3e1b8d3e0461dd664e47937d394`, 21479 bytes).
- Manifest: `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/publication_manifest.json` (registers the two files above and this checkpoint; its own hash is
  deliberately not embedded anywhere in the package, to avoid a circular self-hash).

## 2. Target run

| Item | Value |
|---|---|
| Run | `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828` |
| Root `completion_manifest.json` | SHA-256 `d5c647846e4ec4ddfedd50ff2fed837f70e5398dedd95d0fea90dfc5fcad7d24`, 103575 bytes; stored status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE` (unchanged) |
| Root `authority.json` | SHA-256 `ecef360b340de92b2f1f612b7028efebfa1b26986fa9fe22efad66a46b3442bb`, 110125 bytes |
| Root `case_schedule.json` | SHA-256 `08b05f654dbf997fb91ed4d835594d3f796567e47882e478b9fa05e5ba240df4`, 570473 bytes |
| Files under the run root | 651 (156562246 bytes); 650 registered in the root manifest; 0 hash or byte-count mismatches; 0 symlinks |
| Execution HEAD (frozen, historical) | `c8f555094d6ab711ce6426302419fff958ed19fa` on `thesis-v7` |
| Production generation | `CURRENT_FULL81_PRODUCTION_GENERATION_G1` |
| Framework v7.4 | `docs/research_framework_v7_4_2026-09-26_r2.md`, SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| Registry v7.4 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`, SHA-256 `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| G1 implementation identity digest (21 paths, recomputed from live bytes) | `8cca5e81d62ab3976aaeeeea162bdfdca7867af4871156446bbcae4ece65eabc` |
| Solver parameter fingerprint (as bound in the scope and execution authorizations) | `598dc4365ce65055aa509f6c98a87ba91b173ff361e06119000bf165af4fdebe` |

The execution HEAD stays `c8f5550` after this publication advances repository HEAD. A
publication commit is not the solver-execution commit and grants no permission to run a production
runner. The `final_81_v7_3` path segment and the v7.2 core label are accepted implementation-lineage
names.

### G1 authority chain (live bytes, each equal to its HEAD blob)

| Stage | Path | SHA-256 | Commit | Commit time |
|---|---|---|---|---|
| G1_CANDIDATE | `docs/checkpoints/current_full81_production_generation_g1_candidate_r1_2026-10-07.md` | `dccbbffccc37dbea2179bcbc6210f1afa76351d9883fc73485f3be83278ce9a9` | `59e530f` | 2026-10-08T18:17:13+08:00 |
| G1_CANDIDATE | `results/provenance/current_full81_production_generation_g1_candidate_r1_2026-10-07/g1_candidate_manifest.json` | `bd3621cf9de16a6b7ed0c84444272cd17ce28326b2f4081317c926cd3aa1071a` | `59e530f` | 2026-10-08T18:17:13+08:00 |
| G1_CANDIDATE | `results/provenance/current_full81_production_generation_g1_candidate_r1_2026-10-07/candidate_change_ledger.json` | `e1b2ecc8fcb44327b4d8e0a38f1fd7ba200bd9fa44b363ceaf89220aadbde080` | `59e530f` | 2026-10-08T18:17:13+08:00 |
| G1_INDEPENDENT_AUDIT_PASS_PHASE_A | `results/provenance/current_full81_production_generation_g1_independent_audit_r1/independent_audit_pass_record.json` | `e7c3dcd60ed613ffaea14afe5e6fd91fe711ae0f385b8bfc7cdc6c7d1c09500c` | `59e530f` | 2026-10-08T18:17:13+08:00 |
| G1_ACCEPTANCE_PHASE_B | `results/provenance/current_full81_production_generation_g1_acceptance_r1/acceptance_closure.json` | `d0122f990a14d202fa2e07f1805ce6e8cba17952e37ff1badc37613a517a5879` | `bdbe063` | 2026-10-08T20:46:20+08:00 |
| G1_ACCEPTANCE_PHASE_B | `results/provenance/current_full81_production_generation_g1_acceptance_r1/acceptance_manifest.json` | `bb4aa458d94bfd73db51ae1d87a1661f5272c3a57eaa260be5df3e89abac0926` | `bdbe063` | 2026-10-08T20:46:20+08:00 |
| G1_RE_FREEZE_PHASE_C | `results/provenance/current_full81_production_generation_g1_re_freeze_r1/production_authority_re_freeze_record.json` | `41ec7d2a185993d55f745eaf512df2ab08e82c98e66bf611a95dc967a32c0982` | `b31d88c` | 2026-10-08T21:27:43+08:00 |
| G1_ACCEPTED_LIFECYCLE_PHASE_C | `results/provenance/current_full81_production_generation_g1_accepted_lifecycle/accepted_lifecycle_record.json` | `f1d798ab357ff82454f3030587b3cda30e13b55bf890a2b7257bbb40c325d3b0` | `b31d88c` | 2026-10-08T21:27:43+08:00 |
| MAIN_FULL81_SCOPE_AUTHORIZATION | `results/provenance/main_full81_authorization_g1/main_full81_authorization.json` | `0dc75214904682476def42f36e73688a1f1d254523f20bfd319e6561c4a81338` | `ab5c7be` | 2026-10-08T23:29:44+08:00 |
| MAIN_FULL81_NO_SOLVE_PREFLIGHT_EVIDENCE | `results/provenance/main_full81_no_solve_preflight_g1/main_full81_21d_no_solve_preflight_evidence.json` | `95047e2fa9c0d524d5c43c0fdcafe40a93662c4282fd1aaaf0558be681f4da76` | `21ff5f4` | 2026-10-09T00:10:33+08:00 |
| MAIN_FULL81_EXECUTION_AUTHORIZATION | `results/provenance/main_full81_execution_authorization_g1/main_full81_execution_authorization.json` | `87ec6643deef262bc3710b2e1d7e76d582bcfd1eebd41ffdc6c6c71eb2f12c6e` | `c8f5550` | 2026-10-09T01:12:13+08:00 |

The run was established at 2026-10-08T18:39:34Z, after the execution-authorization
commit. All cross-bindings between these records were rechecked from live bytes (record section
`g1_authority_chain.cross_binding_checks_by_publication_operator`).

### Bound input and implementation identities (live bytes)

| Identity | Path | SHA-256 |
|---|---|---|
| canonical_annual_input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| production_runner | `scripts/21d_preflight_v7_3_final81_successor.py` | `1a55c34897548a3595a9812dfeaa854f3b6b478594630c750931cd7cf2371bd1` |
| model_core | `src/annual_design_model_v7_2.py` | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| production_successor_stack | `src/production_successor_stack_v7_3.py` | `65728c40e8df746da92865e859072c345370ae93aa4a2b32a24b149c67a3dcda` |
| parameter_registry | `data/reference/parameter_registry_v7_2.csv` | `c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1` |
| main_full81_authorization_module | `src/main_full81_authorization_v7_4.py` | `0b4899412bc5cd6d6a4b64a45a243ae8b98d2488ea9ac165f595d2cd7eec7880` |
| accepted_lifecycle_overlay_module | `src/production_authority_lifecycle_u06.py` | `c65aaedc6ea4f357b4ac463ebe0428d717ed953c5e12dc2f547cc98334bd7c45` |
| v7_4_alignment_verifier | `scripts/21e_preflight_v7_4_production_authority_alignment.py` | `6b97be4258f0cccf3538a9078548951d0f4fc5d1ede7c43ae94cd26319568803` |
| execution_input:production_economic_interface_v7_2.json | `data/reference/production_economic_interface_v7_2.json` | `9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9` |
| execution_input:taipower_seasonal_settlement_matrix_v7_2.csv | `data/reference/taipower_seasonal_settlement_matrix_v7_2.csv` | `ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79` |
| execution_input:taipower_tariff_optimization_ntd2023_v7_2.csv | `data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv` | `5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395` |
| execution_input:taipower_transition_period_settlement_interface_v7_2.json | `data/reference/taipower_transition_period_settlement_interface_v7_2.json` | `f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88` |

## 3. The independent audit evidence, and whose it is

The PASS belongs to the Codex audit. The publication operator did not perform the numerical post-solve
reconstruction and does not claim it.

- Reported verdict: `FULL81 POST-SOLVE INDEPENDENT ACCEPTANCE — PASS`.
- Reported coverage: 81/81 cases; 81 stored results meeting the solver acceptance contract; independent
  reconstruction of physical limits, all-start resilience (708,993 valid starts, 5,671,404 outage hours),
  billing (3,888 demand rows), transition settlement (648 rows), cost, degradation and rainflow, all
  reported PASS; zero solver calls, reruns, repository edits and Git writes in the audit session.
- The report states that it created no acceptance artifact, changed no current pointer and promoted no
  result set.

**Source and custody.** No separate report file was handed over. With explicit owner authorization in
this publication session, the operator read the local Codex rollout log read-only and extracted the final
assistant message verbatim. The published copy is exactly the UTF-8 encoding of that message: nothing was
added, removed, redacted, reworded or newline-normalized.

| Item | Value |
|---|---|
| Rollout file | `rollout-2026-10-12T16-02-28-01a12f22-6d74-7c32-bb7d-84a93188e17a.jsonl` (outside the repository; not published; not Git-durable) |
| Rollout at extraction | 1252680 bytes, SHA-256 `dd4be32bfc772c7da40027b2909a5948f485fc9023e409c7984e4c69f33e0a82` |
| Source record | zero-based line 223; the only assistant `final_answer` message; identical to the `task_complete` last message |
| Session, as recorded in the rollout | id `01a12f22-6d74-7c32-bb7d-84a93188e17a`, started 2026-10-12T08:02:28.154Z, final answer 2026-10-12T08:26:20.100Z, model `gpt-6.1-sol`, effort `xhigh` |
| Signature | none exists |

The session metadata is reproduced as recorded and was not independently verified. The report itself
states that it does not claim the session ran under the model setting named in its audit instructions.

**Disclosure.** The destination repository is public. The report contains one local absolute path (the
repository root) and one public GitHub URL, and no e-mail address, credential or session identifier. The
owner decided in this session to publish it verbatim on that basis.

## 4. Evidence qualifications carried unchanged

| Item | Grade as reported |
|---|---|
| Historical actual optimization attempts (81) | `SUPPORTED` — saved counters and guarded source path; no durable per-invocation telemetry |
| Historical model constructions (81) | `SUPPORTED` |
| Gurobi version, best-bound values, complete warning history | `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE` |
| Operator identity and owner launch decision history | not reconstructible from saved artifacts |
| Full execution state | `PARTIALLY_RECONSTRUCTIBLE` |
| Stored numerical outputs | checked in the auditor's environment from local bytes; **not Git-durable** |
| Full production validator fixture suite | not executed by the audit |

Nothing here is upgraded: `SUPPORTED` is not `CONFIRMED`, and `PARTIALLY_RECONSTRUCTIBLE` is not
`FULLY_RECONSTRUCTIBLE`. The 651 result files are gitignored and untracked; this package makes only
their identities durable (the root manifest hash, which registers the other 650 files), not their
bytes.

## 5. Findings carried — none closed, none remediated

Severity, disposition and blocking are separate dimensions, exactly as reported.

| ID | Category | Severity | Disposition | Blocking | Closed here |
|---|---|---|---|---|---|
| `AUD-N1` | Evidence | MODERATE | NONBLOCKING | NO | NO |
| `AUD-N2` | Implementation | MODERATE | OPEN / NONBLOCKING | NO | NO |
| `AUD-N3` | Implementation | MINOR | NONBLOCKING | NO | NO |
| `AUD-N4` | Evidence | INFORMATIONAL | NONBLOCKING | NO | NO |
| `G1-N1` | Governance | MINOR | CARRIED / NONBLOCKING | NO | NO |
| `G1-N2` | Governance | MAJOR | CARRIED / NONBLOCKING | NO | NO |
| `G1-N3` | Evidence | INFORMATIONAL | CARRIED | NO | NO |
| `R7_BINDING_AND_PRESERVATION_GIT_DURABILITY` | Evidence | MAJOR | CARRIED / NONBLOCKING | NO | NO |
| `SAR-N1` | Governance | MINOR–MODERATE | CARRIED / NONBLOCKING | NO | NO |
| `SAR-N2` | Governance | MINOR–MODERATE | CARRIED / NONBLOCKING | NO | NO |
| `SAR-N3` | Governance | MINOR–MODERATE | CARRIED / NONBLOCKING | NO | NO |
| `SAR-N4` | Governance | MINOR–MODERATE | CARRIED / NONBLOCKING | NO | NO |

The `SAR-N1`–`SAR-N4` severity is a group range in the report; no per-item severity is stated or
assigned. Also carried unchanged from the accepted G1 lifecycle: `AUDITOR_INDEPENDENCE_BOUNDARY`,
`AUDIT_PRIMARY_EVIDENCE_NOT_GIT_DURABLE`, `HISTORICAL_21I_CONTENT`, and the fixture-control limitation,
which stays **53/54** — `54/54` is not claimed.

`AUD-N2` (timestamp fingerprint hashed in the units pandas reads rather than the claimed int64-ns) is a
cross-environment portability limitation. No frozen artifact was patched.

## 6. Operator self-checks and observations

These are implementation self-checks, not an independent audit.

- 49 report claims that can be checked against local bytes were rechecked; all agree
  (record section `publication_operator_consistency_cross_checks`). Not reproduced: the section G
  residuals and tolerances, the section I aggregate hashes (algorithm not specified), the negative
  controls, and the 1,062 ignored-inventory count.
- `PUB-OBS-1`: the four published files have no `.gitattributes` rule and `core.autocrlf=true` here.
  `.gitattributes` is a pinned authority file and was not modified. Registered hashes are over LF bytes,
  equal to the Git blob bytes; verify against blobs on a checkout that smudges to CRLF.
- `PUB-OBS-2`: the pre-existing stat-only ` M` entry on
  `results/provenance/main_full81_authorization_r2/main_full81_authorization.json` is untouched; its
  working bytes equal the HEAD blob.
- `PUB-OBS-3`: the report confirmed the remote branch through a GitHub connector after its local
  `git ls-remote` failed; in this session `git ls-remote --heads origin thesis-v7` succeeded and returned
  `c8f555094d6ab711ce6426302419fff958ed19fa`.
- `PUB-OBS-4`: Framework and Registry v7.4 were verified by hash and read in the governing sections, not
  in full.
- `PUB-OBS-5`: no test suite, validator, preflight or production gate was run.

## 7. Package files and byte-integrity contract

| Path | Role |
|---|---|
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/independent_audit_report.md` | verbatim audit transcript copy |
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/audit_evidence_record.json` | machine-readable audit evidence record |
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/publication_manifest.json` | publication manifest |
| `docs/checkpoints/full81_g1_postsolve_audit_evidence_publication_r1_2026-10-12.md` | this checkpoint (external to the package directory) |

These four paths are the complete publication allowlist. The three files under `results/` are covered
by the `results/` ignore rule and need an exact-path forced add; `.gitignore` is not modified. The
manifest registers path, role, byte count and SHA-256 for the report, the record and this checkpoint,
computed from the written bytes.

## 8. Lifecycle boundary

**Before:** G1 implementation generation accepted and frozen; Main Full81 numerical execution complete;
independent post-solve audit reported PASS; formal result acceptance pending.

**After verified publication of these four files:** the independent audit evidence is durably recorded
and traceable to the exact run. State: `FULL81_POSTSOLVE_INDEPENDENT_AUDIT_EVIDENCE — PUBLISHED /
RESULT_ACCEPTANCE_PENDING`.

**Still not authorized:** Full81 result acceptance or `CLOSED_ACCEPTED`; a current-mainline pointer;
thesis-authoritative promotion; any accepted-lifecycle, re-freeze or authorization record; any solve,
production run, A2, Layer B, DG or sensitivity; remediation of any finding; a pipeline notebook;
downstream analysis; any Git tag.

## 9. Zero execution in this publication session

Model constructions 0; `optimize()` calls 0; solver calls 0; production runs 0; A2 / Layer B / DG /
sensitivity solves 0; repairs 0; production result files modified 0; previously accepted or historical
files modified 0. This is the operator's own report as of authoring.

## 10. Next legal gate

A fresh, independent, read-only audit of this package and its publication commit; then, separately, a
formal Full81 result-acceptance decision. Neither is performed here, and the publication operator does
not accept its own package.
