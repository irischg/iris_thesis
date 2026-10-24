# Iris Thesis — Pointer v2 / R3 Combined Candidate: Researcher Acceptance Record

**Date:** 2026-10-24
**Record type:** Researcher acceptance of an exact compatibility candidate (additive, single file)
**Status:** `ACCEPTED_CANDIDATE` — **NOT ACTIVATED**. This is NOT activation of Framework v8, NOT promotion of R3 to canonical, and NOT a pointer change.
**Acceptance authority:** Researcher Iris (sole acceptance authority)
**Recorded by:** Claude Code (model `claude-sonnet-5-5` as reported by the runtime), at the researcher's explicit instruction of 2026-10-24. The decision in section 1 is the researcher's; this file only records it and the checks made before recording it.
**Authoring clock:** 2026-10-24 ~19:5x (+08:00, host clock)

---

## 1. Researcher decision

The researcher explicitly accepts the following exact candidate package. Identities were re-verified against the working tree immediately before this record was written (section 5).

| # | Path (repository-relative) | SHA-256 | Bytes |
|---|---|---|---|
| 1 | `src/current_mainline_pointer_v2.py` | `d2d2d7f0b65097c5485b9f0c910f3d45a41aafa9d7a3d0579e6676986627f1dd` | 60611 |
| 2 | `configs/candidates/current_mainline_pointer_candidate_r3.json` | `7cd154f82089991a1346efe71525f4dab1dd80c3390abb0947c87277a9ff63e4` | 30703 |
| 3 | `tests/test_current_mainline_pointer_v2.py` | `56b9c5645db7109e0e95da7674075ba6ee08276325fd5d8a2a304c5eb9c71013` | 41355 |

**Accepted R3 payload digest:** `886b906bf2f9d8a13ad2693a93fe4ea122196ecb65504cb3228e84c9e16df506`
(`current_mainline_pointer_v1.pointer_payload_digest`, i.e. SHA-256 of the sorted-key compact UTF-8 JSON of the pointer minus its lifecycle envelope).

The researcher adopts the final independent review verdict:

> `POINTER V2 / R3 TARGETED INDEPENDENT CLOSURE — PASS`

This is acceptance of the exact compatibility candidate. It is **not** activation of Framework v8.

## 2. Acceptance scope

The accepted candidate is a **methodology/evidence-only v8 authority-routing implementation**. Its purpose is to permit a future, separately authorized activation of:

- **Framework v8 R2** as current methodology (document identity as bound in R3 `methodology_authority`; Gate 3 record identity in section 4).
- **Registry v8** = Registry v7.4 plus the accepted v8 delta.

For v8 the following remain **unbuilt, unexecuted or unauthorized** (R3 `v8_unbuilt_stages`: every item `NOT_YET_AUTHORIZED` / `NOT_YET_EXECUTED`; no historical identity or placeholder hash may stand in):

- Scientific implementation
- Production runner and generation
- Input compatibility
- Pilot
- Numerical results
- Numerical result acceptance

Methodology change vs. implementation correction: this acceptance changes **no** methodology. No CLOSED decision (A1–A4, B1–B2, Gate 1, Gate 2) is reopened, and no formula, tariff/cost basis, degradation semantics, preprocessing rule, Layer A/B boundary, solver setting or production parameter is touched. It accepts routing/verification code and a candidate pointer payload only.

## 3. Independent audit evidence and its limitations

**Verdict as relayed by the researcher:** `POINTER V2 / R3 TARGETED INDEPENDENT CLOSURE — PASS`, scoped to the three artifacts and payload digest in section 1.

Facts relayed by the researcher about that closure, recorded as stated:

- The final closure independently executed **49** v2 tests. (Corroboration only: the test module at the accepted SHA contains 49 `def test_` methods; Claude Code did **not** re-run them in this task.)
- A valid hypothetical canonical activation reached `CANONICAL_POINTER_VERIFIED` in an **isolated synthetic Git environment**.
- The final closure review itself reported **no project-file or Git mutations**.

Limitations that bind this acceptance (not softened):

1. **Independence was by session, not cross-provider.** Same model family; this is not cross-model assurance.
2. **The positive canonical fixture is not yet part of the durable v2 test module.** The `CANONICAL_POINTER_VERIFIED` result exists only as a reviewer-run synthetic check, not as a repeatable test in the accepted module.
3. **`core.autocrlf=true` can produce CRLF checkout mismatches that correctly fail closed.** The host's system Git config sets `core.autocrlf=true` (observed 2026-10-24). A CRLF-smudged checkout of a bound file will change its raw SHA-256 and the verifier will reject it; that is intended behavior, not a defect.
4. **Existing v1 callers, routing documents and current-state assumptions require a controlled transition at Activation.** None was changed here.
5. **Historical procedural incident — preserved as recorded, not erased.** A previous reviewer temporarily modified `.git/config` without authorization. That was a procedural violation and must not be described as compliant. Observation by Claude Code on 2026-10-24: current `.git/config` (mtime 18:25:21 +08:00, after the artifacts' last write) contains only standard repository/remote/branch entries and no `core.autocrlf` override; Claude Code has no record of the file's pre-incident bytes and does not assert that it is byte-identical to its state before the incident.
6. **Report custody is conversation-only.** The full review report exists in the conversation, not as a file. No original report bytes were verified or preserved in this task, and **no audit transcript or file-bound audit record is manufactured or implied here**. This record's reference to the audit is by verdict string and relayed facts only.

## 4. Preserved identities

**Framework v8 Gate 3 Acceptance Record** (verified byte-identical in Downloads and in the repository):

- Downloads: `Iris_Thesis_Framework_v8_Registry_v8_Delta_Gate3_Acceptance_Record_2026-10-24.md`
- Repo: `docs/v8_gate3_accepted_package_2026-10-24/Iris_Thesis_Framework_v8_Registry_v8_Delta_Gate3_Acceptance_Record_2026-10-24.md`
- SHA-256 `b67eb1f05f8cd6dfd08040cf12599a324483cb4616c23bb1dc8763d436880cc9`, 14291 bytes
- Matches the identity bound in R3 `methodology_authority.gate3_acceptance_record`. Git blob `1abde566cd9bfe16acf14807bb49059fa431b711` and anchor commit `420f182ed221f3d4e2629f5e44da95c395d9f6b3` are as recorded in R3 (not independently re-derived here).
- The Gate 3 record authorizes neither activation, nor a pointer change, nor Git, Coding, Solver or Pilot.

**Predecessor / current canonical pointer:** `CURRENT_MAINLINE_POINTER_R2`
(`configs/current_mainline_pointer.json`, `ACCEPTED_CANONICAL`, payload digest `08d09477d7bcda349197427f38bd642cf8f7d3e0413abdfdc4c362dab141ee4e`, Git blob `c6b9b50ce37c44040e5ff9660a1242ec63845c26` in HEAD and in the working tree, activated at `5a101042cb91f6191208cfdad1e8ddcbebb972f0`, an ancestor of HEAD). R3 records exactly this digest as its predecessor.

## 5. Pre-write verification (performed by Claude Code, read-only, 2026-10-24)

| Check | Result |
|---|---|
| SHA-256 of the three candidate files | all three match section 1 |
| R3 payload digest recomputed with v1 `pointer_payload_digest` | `886b906b…16df506` — matches |
| Gate 3 acceptance record SHA/bytes (Downloads and repo) | match section 4 |
| Canonical pointer is still R2 | yes; `pointer_id` = `CURRENT_MAINLINE_POINTER_R2`, `is_canonical` true; file clean vs HEAD |
| Output path unused before writing | yes (`Test-Path` False) |
| Branch / HEAD | `thesis-v7` @ `420f182ed221f3d4e2629f5e44da95c395d9f6b3`; equals `origin/thesis-v7` |
| Three candidate artifacts | **untracked** (not in Git) |
| `src/current_mainline_pointer_v1.py`, `configs/current_mainline_pointer.json`, `.gitattributes`, `CLAUDE.md`, `docs/ai_handoff/` | no diff vs HEAD |
| Working-tree status | 19 entries, identical to the session-start snapshot, including one **pre-existing** unrelated modification (`results/provenance/main_full81_authorization_r2/main_full81_authorization.json`) that this task did not touch and does not characterize |

## 6. Historical preservation requirements

Unchanged and immutable by this record: Framework v7.4, Registry v7.4, G1, Full81, EOB, all accepted results and checkpoints, canonical pointer R1 and R2, `src/current_mainline_pointer_v1.py`, and `.gitattributes`. The v7.4 canonical route **remains current** after this record is written. The three accepted artifacts must not be edited in place; any change requires a new candidate and a new audit.

## 7. Future activation dependencies (none authorized or triggered here)

Per R3 `activation_contract` (`automatic_progression: false`; candidate consistency and acceptance are not activation), activation additionally requires, each under its own authorization:

1. Controlled Git publication of the accepted v2/R3 package (currently untracked) and this acceptance record, with bound tracked files carrying identical blobs in live HEAD and their anchor commits, and recorded commits reachable from `origin/thesis-v7`.
2. A **file-bound independent audit record** (`CURRENT_MAINLINE_POINTER_INDEPENDENT_AUDIT_RECORD`) for this exact candidate and payload digest. **Open gap:** the PASS currently has conversation-only custody (section 3.6); the owner must decide how this requirement is met without fabricating a transcript.
3. A researcher acceptance closure and manifest (`CURRENT_MAINLINE_POINTER_ACCEPTANCE_CLOSURE` / `_MANIFEST`) whose `accepted_methodology_activation` names Framework v8, both Registry v8 components, the Gate 3 record and the predecessor pointer.
4. A separately authorized canonical replacement whose payload equals the audited payload `886b906b…16df506`.
5. A controlled transition for v1 callers, handoff/protocol routing and `CURRENT_STATE` assumptions (R3 OPEN-11), as separate repository mutations.
6. Recommended before activation: promote the positive canonical fixture into the durable v2 test module (new candidate + audit, since the accepted test SHA would change) and decide the `core.autocrlf` / checkout-line-ending handling so a legitimate checkout does not fail closed.

## 8. Explicit non-actions of this record

No activation record; no promotion of R3; no edit of the three accepted artifacts, v1, canonical pointer R2 or `.gitattributes`; no Git add/commit/tag/push; no change to CLAUDE.md, CURRENT_STATE or routing; no historical document rewritten; no energy model, solver, Pilot or production run. This file is the only file created by the task.

## 9. Self-identity note

This file's own SHA-256 is not embedded (circular). It is reported in the task's final message at creation time and should be bound by any later publication record.
