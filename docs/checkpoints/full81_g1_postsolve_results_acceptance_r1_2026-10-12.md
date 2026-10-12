# Full81 G1 Post-Solve Results Acceptance R1 — Formal Results Acceptance / Governance Closure

**Date:** 2026-10-12
**Package:** `FULL81_G1_POSTSOLVE_RESULTS_ACCEPTANCE_R1`
**Decision recorded here:** Main Full81 numerical results of run `20261008T183934456307Z_a6826f4828` — `CLOSED / ACCEPTED` for the
current Layer A mainline.

Whether this acceptance is *published* is determined from live Git only: the three files listed in
section 9 must be contained, byte-identical, in one commit reachable from `origin/thesis-v7`. This
checkpoint embeds no containing commit id and no tag, because none existed when it was written. A
local-only copy is not a completed governance closure.

**This checkpoint is not** the G1 implementation-generation acceptance, a solver-execution manifest, the
independent audit, the Phase A evidence publication, a current-mainline pointer, an exposure log, a
notebook or a results analysis. It adds no lifecycle role and changes no existing record.

## 1. What was decided, and what it means

The 81 stored constant-floor Layer A case results of the target run are accepted as the valid numerical
outputs of the accepted Framework v7.4 method, executed by the accepted and frozen G1 implementation
generation on the accepted canonical planning input. Acceptance is a governance status. It is not a
scientific interpretation, and no result was analyzed here.

The original result files are unchanged. Their execution-time `completion_manifest.json` status,
`COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`, is historical and is not rewritten; the current
governance status is carried by this additive package, as already done for the accepted EOB and
core-three runs.

- Acceptance closure: `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_closure.json`
  (SHA-256 `3b27f9a60f5e0bfbcffde343aad164e74cff2f8a98581d91fb95d4bc90e2ba02`, 85857 bytes).
- Acceptance manifest: `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_manifest.json` (registers the closure and this
  checkpoint; its own hash is deliberately embedded nowhere, to avoid a circular self-hash).

## 2. Target run and bound identities

| Item | Value |
| --- | --- |
| Run | `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828` |
| Root `completion_manifest.json` | SHA-256 `d5c647846e4ec4ddfedd50ff2fed837f70e5398dedd95d0fea90dfc5fcad7d24`, 103575 bytes |
| Root `authority.json` | SHA-256 `ecef360b340de92b2f1f612b7028efebfa1b26986fa9fe22efad66a46b3442bb` |
| Root `case_schedule.json` | SHA-256 `08b05f654dbf997fb91ed4d835594d3f796567e47882e478b9fa05e5ba240df4` |
| Files under the run root | 651 (156562246 bytes); 650 root registrations and 567 case registrations re-hashed, 0 mismatches; 0 symlinks |
| Execution HEAD (frozen, historical) | `c8f555094d6ab711ce6426302419fff958ed19fa` on `thesis-v7` |
| Production generation | `CURRENT_FULL81_PRODUCTION_GENERATION_G1` |
| Framework v7.4 | `docs/research_framework_v7_4_2026-09-26_r2.md`, SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| Registry v7.4 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`, SHA-256 `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| Canonical planning input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`, SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| G1 accepted lifecycle | SHA-256 `f1d798ab357ff82454f3030587b3cda30e13b55bf890a2b7257bbb40c325d3b0` |
| Execution authorization (`GRANTED`) | SHA-256 `87ec6643deef262bc3710b2e1d7e76d582bcfd1eebd41ffdc6c6c71eb2f12c6e`, commit `c8f5550` |
| G1 runtime / validation / governance identity digests | `8cca5e81d62ab3976aaeeeea162bdfdca7867af4871156446bbcae4ece65eabc` (21 paths) / `1bd49904e8d774c27b5e8a0390240eb836e92fa6cf857948f7b9d3486914111b` (9) / `360c81b133440e1b0444e01f2fd120eb1f49d0db3501283773a2952c032dbeb4` (26) — all three recomputed here from live bytes and from execution-HEAD blobs |

All eleven G1 authority records were each added by exactly one commit, in lifecycle order, every one an
ancestor of the execution HEAD; the execution authorization binds the accepted lifecycle, the scope
authorization and the no-solve preflight by hash; the run started after the execution-authorization
commit. Framework v7.4 sections 0.1 and 3.4 fix the 9 x 9 grid. No CLOSED decision is reopened.

## 3. Evidence basis and its classification

The numerical PASS belongs to the independent Codex post-solve audit. The acceptance operator did not
recompute the numerical results and does not claim to have.

| Evidence | Classification |
| --- | --- |
| Independent numerical acceptance | **Codex-reported PASS**, subject to the publication-evidence checks below |
| Historical optimization-call count (81) | **SUPPORTED** — not directly confirmed from per-invocation telemetry |
| Complete transient solver execution environment | **PARTIALLY_RECONSTRUCTIBLE** |
| The 651 result files | locally retained and verified by the prior audit, re-hashed here; **not Git-durable** |

### Phase A publication, verified from Git objects

Commit `5992624e26d19304c1fc76f09c2ce128ab0e7215`, sole parent `c8f555094d6ab711ce6426302419fff958ed19fa`,
added exactly four files and changed none of the 301 paths of the execution-HEAD tree.

| Path | SHA-256 (blob bytes) | Bytes |
| --- | --- | --- |
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/independent_audit_report.md` | `c6a07064451fa98f84fd714d09d59ed93eabc3e1b8d3e0461dd664e47937d394` | 21479 |
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/audit_evidence_record.json` | `a02f05e52862a3f99abb0d56e5f8b44d1a6ee851ad2f6fdbc012b1bd608ac3fa` | 88562 |
| `results/provenance/full81_g1_postsolve_audit_evidence_publication_r1/publication_manifest.json` | `9f90449b31175f17d78d74cccf68764cf2e587f507a4bd13719b957d3d539337` | 4617 |
| `docs/checkpoints/full81_g1_postsolve_audit_evidence_publication_r1_2026-10-12.md` | `6d7c49dd68e44d42915e2d4584a4be148032650475645b8b4a1bd9c1a2dc5f84` | 17624 |

The manifest's three registrations match the blobs; its allowlist equals the commit's path set; the
report binds the run, the G1 generation, the Framework, the input, the execution authorization and the
root manifest; Phase A records `RESULT_ACCEPTANCE_PENDING`, not an acceptance. `git ls-remote` and the
GitHub REST API both returned this commit as the head of `thesis-v7`. This is an acceptance-prerequisite
verification of the evidence package, not a new audit of the 81 dispatches.

### Full81 contract coverage (stored evidence, read by the acceptance operator)

81 cases, alpha 0.60 to 1.00 in 0.05 steps and beta 4 to 12 h; case directories, root manifest and
schedule agree; 0 missing, duplicate, unexpected or failed cases; 81 stored `OPTIMAL` results with finite
objectives; maximum stored MIPGap `9.916563814474196e-07` (`a0.90_b12`), none above `1e-6`; eight
mandatory audit families stored `PASS` for 81/81; one solver-settings identity for all cases. The
independent reconstruction of the eight families is the audit's (report section G). Every report claim
re-derived here from stored bytes agrees, and a six-case spot check of dispatch bytes against the
canonical input found a maximum AC-balance residual of `8.8151e-07` kW
(`a0.60_b06`), the same worst case the audit reports.

## 4. Acceptance criteria

| # | Criterion | Result | Grade |
| --- | --- | --- | --- |
| 1 | The source publication exists in the correct remote commit. | **PASS** | CONFIRMED |
| 2 | Its exact evidence identities and registrations verify. | **PASS** | CONFIRMED |
| 3 | The independent post-solve numerical PASS is adequately evidenced. | **PASS** | CODEX_REPORTED_PASS; SUPPORTED by the corroboration recorded here; not recomputed |
| 4 | The complete Full81 result set and required acceptance conditions are supported. | **PASS** | CONFIRMED for completeness, stored solver predicates and registry integrity; CODEX_REPORTED for the eight-family numerical reconstruction |
| 5 | No unresolved acceptance-blocking finding exists. | **PASS** | Every carried finding is NONBLOCKING for results acceptance; ACC-N1 is OPEN and NONBLOCKING for results acceptance by the terms of its governing clause and by the owner's in-session decision |
| 6 | The methodology/evidence/implementation authority chain remains coherent. | **PASS** | CONFIRMED, with the label qualifications of AUD-N3 / ACC-OBS-4 and the undischarged obligation of ACC-N1 |
| 7 | All provenance and reconstructibility limitations are retained. | **PASS** | CONFIRMED (carried in this record; none closed) |
| 8 | The acceptance decision is made by an operator separate from the prior audit and evidence-publication operators. | **PASS** | CONFIRMED at session level, with the boundary of ACC-OBS-3 |
| 9 | The owner's conditional authorization legitimately covers this acceptance decision. | **PASS** | CONFIRMED by the Step 3 authorization and an in-session owner decision; no signature claimed |
| 10 | The live Git state permits a narrowly scoped additive publication. | **PASS** | CONFIRMED |

## 5. Decision, authority and operator

- **Decision:** Full81 numerical results accepted for the current Layer A mainline.
- **Authority:** the thesis owner's conditional Step 3 authorization, received as the task instruction of
  this session, and an in-session owner decision taken before any write: accept and publish, carrying
  `ACC-N1` as OPEN. No signature is claimed and the instruction text is not published.
- **Operator:** Claude Code session `1f3d8c9a-aeb0-4a9f-a5c7-fc8e5e79204b`, model id `claude-opus-5-5` as reported
  by the runtime; reasoning effort not verifiable by the operator. Not the Codex auditor, not the Phase A
  publication operator, not a G1 author or acceptance operator, and not the launcher of the run.
- **Contract:** Provenance Protocol v1 sections 3, 5, 9, 11, 16-18, 20, 22, 25; Constitution sections 3,
  8, 10, 19, 22; Framework v7.4 sections 0.1 and 3.4; the solver-acceptance predicates and the eight
  mandatory audit families in the runtime source. The G1 role contract has no result-acceptance role and
  no result-acceptance schema exists for the current route, so this package follows the Phase A
  conventions and invents no role.

## 6. Governance deviations adjudicated

**Audit model identity.** The audit instruction requested GPT-5.6 Sol / Extra High; the Codex rollout, as
recorded by Phase A, shows `gpt-6.1-sol` / `xhigh`. The audit never claimed GPT-5.6 Sol, and neither does
this record. Constitution section 14.C names that model as the *default recommended* model and section 15
requires a *suggested* model in generated instructions; the mandatory conditions are a fresh session and
separation from the implementation agent (Constitution section 19, Protocol section 11), both met.
Determination: tool-selection recommendation, not a mandatory acceptance condition — **nonblocking,
disclosed, carried**. The original audit instruction is outside the repository and was not read here.

**Source custody.** The published report is an *operator-extracted transcript* of the Codex rollout's
final message, not an owner-supplied report file. The rollout is unpublished and not Git-durable, carries
no signature, and was not read or re-verified in this session. Nonblocking; carried.

**Publication observations.** `PUB-OBS-1` (line endings): confirmed, nonblocking, open — hashes are over
LF blob bytes; a CRLF-smudging checkout changes working-tree hashes only; the same holds for this package.
`PUB-OBS-5` (no test suite run): nonblocking for results acceptance, open — no implementation, validator,
test, data or authority byte differs from the executed state, and this session ran no suite either.

## 7. New finding and observations from this session

| ID | Class | Severity | Disposition | Blocks results acceptance |
| --- | --- | --- | --- | --- |
| `ACC-N1` | MANDATORY_EXPOSURE_LOG_NOT_ESTABLISHED | MAJOR | OPEN | NO |
| `ACC-OBS-1` | STALE_PRE_EXECUTION_TEST_PREMISE | MINOR | OPEN | NO |
| `ACC-OBS-2` | EARLIER_INCOMPLETE_STAGING_ATTEMPT | INFORMATIONAL | OPEN / CARRIED | NO |
| `ACC-OBS-3` | ACCEPTANCE_OPERATOR_INDEPENDENCE_BOUNDARY | INFORMATIONAL | DISCLOSED / CARRIED | NO |
| `ACC-OBS-4` | STATIC_AUTHORITY_LABELS_IN_STORED_OUTPUTS | MINOR | OPEN / CARRIED | NO |
| `ACC-OBS-5` | PHASE_A_NEXT_GATE_WORDING | INFORMATIONAL | DISCLOSED | NO |
| `ACC-OBS-6` | STALE_HANDOFF_DOCUMENTS | MINOR | OPEN / CARRIED | NO |

**`ACC-N1` — mandatory exposure log not established.** The accepted governance-sequencing closure
(`docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md`,
section 13), which the run's own `authority.json` names as its governing authority, requires a prospective
exposure log in the authorized Full81 provenance namespace before the first scientific inspection, with
its path and serialization fixed by the Main Full81 authorization/preflight, and calls an omitted or
retrospective exposure record a governance failure. No exposure log exists, and the G1 scope
authorization, preflight evidence and execution authorization fixed no path for one. The clause conditions
scientific inspection and supervisor discussion, not numerical-results acceptance, and does not touch the
numerical validity of the results; the owner, shown this before any write, decided to accept and carry it
OPEN. It **blocks the first scientific inspection and any supervisor discussion** until an exposure log is
established under a separate authorization. Whether the audit, its publication or this session count as an
exposure event is not decided here. This checkpoint is not an exposure log and creates no exposure entry.

Result information already visible: the published audit report and Phase A record show the solver status
distribution, gap and runtime ranges and the objective range over the 81 cases. In this session the
operator read stored summaries for all 81 cases and dispatch values for six, and session tool output
displayed sizing values for those six cases; none are published here. No surface, ranking, knee or
transition analysis was performed, and no A2 result exists or was exposed.

**`ACC-OBS-1`.** `tests/test_21f_u06_accepted_lifecycle_gate.py:1280-1284` asserts that the runs directory
holds only the core-three run; it is expected to fail on the live tree now that the authorized Full81 run
exists. Read, not executed; a stale pre-execution premise, not a behavioral regression; file not edited.

**`ACC-OBS-2`.** An earlier incomplete staging directory beside the run holds the same `authority.json`
and `case_schedule.json` and no case artifact. It is not part of the accepted run; whether it issued a
solver call is not reconstructible. Not touched.

**`ACC-OBS-3`.** The acceptance operator is session-independent from the publication operator but reports
the same model id, and shares a persistent agent-notes directory with earlier Claude Code sessions.

**`ACC-OBS-4`.** All 81 stored case definitions and the root `authority.json` carry static labels such as
`main_full81_authorization = NOT_AUTHORIZED` and `main_full81_execution_authorized = false` (the `AUD-N3`
class). The effective authority is the separately published `GRANTED` execution authorization, which the
execution gate resolves. The stored bytes are historical and unchanged.

**`ACC-OBS-5`.** Phase A named a publication audit and a separately authorized acceptance as its next
gates; the owner's Step 3 authorization assigned both to this session. The G1 Phase B acceptance operator
likewise verified Phase A containment within its own acceptance pass.

**`ACC-OBS-6`.** The `CLAUDE.md` read-first list and `CURRENT_STATE.md` predate G1 and the Full81 run
(`SAR-N2`); the live accepted artifacts govern. Not edited.

## 8. Findings and limitations carried — none closed, none remediated

| ID | Category | Severity | Disposition as reported | Blocks results acceptance | Closed |
| --- | --- | --- | --- | --- | --- |
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

The `SAR-N1`–`SAR-N4` severity is a group range in the audit report. Also carried unchanged:
`AUDITOR_INDEPENDENCE_BOUNDARY` (the G1 delta audit was a separate Claude Code session, not Codex, and is
not claimed as cross-model verification), `AUDIT_PRIMARY_EVIDENCE_NOT_GIT_DURABLE`, `HISTORICAL_21I_CONTENT`,
and the fixture-control limitation, which stays **53/54** — `54/54` is not claimed. `AUD-N2` is not
repaired. `SUPPORTED` is not upgraded to `CONFIRMED`; `PARTIALLY_RECONSTRUCTIBLE` is not upgraded.

## 9. Package files and byte-integrity contract

| Path | Role |
| --- | --- |
| `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_closure.json` | results acceptance closure |
| `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_manifest.json` | acceptance manifest |
| `docs/checkpoints/full81_g1_postsolve_results_acceptance_r1_2026-10-12.md` | this checkpoint (external to the package directory) |

These three paths are the complete publication allowlist. The two files under `results/` are covered by
the `results/` ignore rule and need an exact-path forced add; `.gitignore` and `.gitattributes` are not
modified. Registered hashes are over the LF bytes written, which equal the Git blob bytes.

## 10. Lifecycle boundary

**Before:** G1 accepted and frozen; Main Full81 executed; independent post-solve audit reported PASS;
audit evidence published (Phase A); result acceptance pending.

**After verified publication of these three files:** Full81 numerical results `CLOSED / ACCEPTED /
PUBLISHED` for the current Layer A mainline; no current-mainline pointer exists.

**Still not authorized:** a current-mainline pointer; a pipeline notebook; any scientific inspection,
results analysis or supervisor discussion (blocked by `ACC-N1` until an exposure log exists); creation of
the exposure log itself; a cross-case aggregation layer; any solve, model construction or production run;
A2, Layer B, DG or sensitivity work; remediation of any finding; preservation or publication of the 651
result files; handoff-document synchronization; any Git tag. U-01 remains `OPEN / HOLD` and may no longer
be described as fully pre-Full81 blinded; Full81 magnitudes must not be used to calibrate it.

## 11. Zero execution in this acceptance session

Model constructions 0; `optimize()` calls 0; solver calls 0; solver-library imports 0; production runs 0;
A2 / Layer B / DG / sensitivity solves 0; tests, validators, preflights and production gates executed 0;
repairs 0; production result files modified 0; previously accepted or historical files modified 0. This is
the operator's own report as of authoring.

## 12. Next legal gate

Design and implementation of a machine-readable current-mainline pointer, under a separate owner
authorization. Not performed here.
