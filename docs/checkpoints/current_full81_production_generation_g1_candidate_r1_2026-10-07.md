# Current Full81 Production Generation G1 - Candidate R1 checkpoint

**CANDIDATE ONLY.** This file is the producer-side candidate checkpoint of the G1
implementation. It is not an independent audit, not an acceptance, not a
production-authority freeze and not an authorization of any kind.

## Status at packaging time

- Producer-side implementation: completed (G1 Batches 1-4, including 3.2); this
  package is Batch 5.
- Independent audit: NOT YET PERFORMED.
- Candidate: NOT ACCEPTED (`self_accepted` is false).
- Production authority: NOT FROZEN; the G1 accepted-lifecycle record is ABSENT.
- Main Full81 scope: NOT AUTHORIZED; the G1 scope authorization is ABSENT.
- Main Full81 execution: NOT AUTHORIZED; the G1 execution authorization is ABSENT.
- 21d no-solve preflight: NOT EXECUTED in the real repository.
- Full81: NOT EXECUTED. Zero `optimize()` calls, zero model solves, zero
  production runs during G1.

## Identity

- Generation: `CURRENT_FULL81_PRODUCTION_GENERATION_G1` (lineage `CURRENT_FULL81_PRODUCTION_GENERATION_G1`).
- Candidate: `CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1`.
- Predecessor: `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1`, candidate
  `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8`, relationship
  `SUPERSEDED_HISTORICAL_PREDECESSOR_NOT_A_LIVE_BINDING`.
- Predecessor repository head (the commit every change below is measured
  against): `222685f0ea8a1a9f281e30962e223a339d5ec938`.
- Package: this checkpoint, `results/provenance/current_full81_production_generation_g1_candidate_r1_2026-10-07/candidate_change_ledger.json` and
  `results/provenance/current_full81_production_generation_g1_candidate_r1_2026-10-07/g1_candidate_manifest.json`.
- Binding order: change ledger, then this checkpoint, then the manifest. The
  manifest binds this checkpoint and the ledger by raw SHA-256; its own identity
  is bound only by later lifecycle role records. No package file records its
  own digest, and the ledger names no digest of a later package file.

## G1 identity axes

The three aggregate digests are stated once, as canonical claims, in the
identity-claims block at the end of this file. Digest algorithm:
sha256 over json.dumps({path: sha256}, sort_keys=True, separators=(',',':')) encoded utf-8.

- `G1_RUNTIME_IDENTITY`: 21 members (the accepted
  implementation paths); also the manifest's `implementation_identity_digest`.
- `G1_VALIDATION_IDENTITY`: 9 suites.
- `G1_GOVERNANCE_AUTHORITY_IDENTITY`: 26
  members (authority-bundle pins and the four FULLSTACK-01 execution inputs,
  minus runtime and validation members).
- The three member sets are pairwise disjoint (56 unique
  members, each a live role of the change ledger).
- Intentional runtime-validation coupling (validation files whose bytes runtime
  code pins, so editing them moves the runtime digest):
- `tests/test_21a_v7_3_production_routing_preflight.py` (pinned by `src/production_successor_stack_v7_3.py`, label `ADDITIONAL_AUTHORITY_FILES[step2e1_test]`)
- `tests/test_21e_v7_4_production_authority_bundle.py` (pinned by `src/production_authority_bundle_v7_4.py`, label `v7_4_alignment_test`)
- `tests/test_21f_u06_accepted_lifecycle_gate.py` (pinned by `src/production_authority_bundle_v7_4.py`, label `u06_lifecycle_test`)
- `tests/test_21g_u06_r3_substitution_attacks.py` (pinned by `src/production_authority_bundle_v7_4.py`, label `u06_r3_substitution_attack_test`)
- `tests/test_21h_main_full81_authorization_mechanism.py` (pinned by `src/production_authority_bundle_v7_4.py`, label `main_full81_authorization_test`)

## Change set against the predecessor head (mechanically derived)

9 MODIFY, 2 CREATE,
0 PUBLISH_UNCHANGED; the other 45
identity members are carried forward unchanged. Files outside the 56-member
identity surface (including unrelated untracked user files) are not part of
this candidate.

| Path | Change | Identity axis |
|---|---|---|
| `.gitattributes` | MODIFY | G1_GOVERNANCE_AUTHORITY_IDENTITY |
| `src/main_full81_authorization_v7_4.py` | MODIFY | G1_RUNTIME_IDENTITY |
| `src/production_authority_bundle_v7_4.py` | MODIFY | G1_RUNTIME_IDENTITY |
| `src/production_authority_lifecycle_u06.py` | MODIFY | G1_RUNTIME_IDENTITY |
| `tests/test_21b_21d_v7_3_production_successor_stack.py` | MODIFY | G1_VALIDATION_IDENTITY |
| `tests/test_21e_v7_4_production_authority_bundle.py` | MODIFY | G1_VALIDATION_IDENTITY |
| `tests/test_21f_u06_accepted_lifecycle_gate.py` | MODIFY | G1_VALIDATION_IDENTITY |
| `tests/test_21g_u06_r3_substitution_attacks.py` | MODIFY | G1_VALIDATION_IDENTITY |
| `tests/test_21h_main_full81_authorization_mechanism.py` | MODIFY | G1_VALIDATION_IDENTITY |
| `tests/test_21i_main_full81_preflight_authorization_guard.py` | CREATE | G1_VALIDATION_IDENTITY |
| `tests/test_21l_full81_production_generation_g1.py` | CREATE | G1_VALIDATION_IDENTITY |

## Authority bundle and raw-byte policy

- 34 pins in 7 groups; every pin equals live bytes; no duplicate role or path;
  no pin names a candidate or future governance artifact. The seven pins whose
  targets carry G1 bytes name the G1 candidate as their origin.
- The candidate checkpoint, manifest and ledger are deliberately not bundle
  pins (pinning them would create a hash cycle).
- Raw-byte consumer universe 141 paths, 141 exact-path rules: 0 uncovered,
  0 wrongly treated, 0 unused, 0 overreaching.

## Validation evidence recorded in the change ledger

Bounded regression of the nine G1 validation suites on exactly these
validation bytes, with native-solver tripwires active, run before this package
existed. All nine suites ran on exactly these runtime bytes.

| Suite | Ran | Failures | Errors | Skipped | Result | Evidence basis |
|---|---|---|---|---|---|---|
| `tests/test_21a_v7_3_production_routing_preflight.py` | 19 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21b_21d_v7_3_production_successor_stack.py` | 71 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21e_v7_4_production_authority_bundle.py` | 34 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21f_u06_accepted_lifecycle_gate.py` | 55 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21g_u06_r3_substitution_attacks.py` | 37 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21h_main_full81_authorization_mechanism.py` | 73 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21i_main_full81_preflight_authorization_guard.py` | 50 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_21l_full81_production_generation_g1.py` | 61 | 0 | 0 | 0 | OK | run on final bytes |
| `tests/test_fullstack_01_execution_input_authority.py` | 9 | 0 | 0 | 0 | OK | run on final bytes |

## Notes for the independent auditor (not resolved by this candidate)

- G1-N1, historical origin label: the bundle pin for
  `src/production_successor_stack_v7_3.py` keeps the origin tag
  `U_06_ALIGNMENT_CANDIDATE_R3`, while Git shows the stack's bytes last changed
  at 02b998b (Main Full81 authorization mechanism R2). Descriptive metadata only;
  no guard reads it. G1 does not modify the stack or re-tag the pin.
- G1-N2, predecessor freeze coverage: at the predecessor head the published
  runtime bytes equal neither the R8 nor the FULLSTACK-01 frozen implementation
  identity (R8 froze 21c/21d bytes first published at 222685f; FULLSTACK-01 froze
  the 82f04841 bytes, and 222685f changed 21c/21d afterwards). G1 binds neither
  frozen identity as a live binding. Detail: the change ledger's
  `known_historical_inconsistency`.
- G1-N3, evidence phase: the recorded test evidence predates the package by
  construction; package-phase regression is reported outside the package. The
  evidence-basis column states which entries ran on exactly these runtime bytes.

## Future governance artifacts (all ABSENT at packaging time)

- independent_audit_pass: `results/provenance/current_full81_production_generation_g1_independent_audit_r1/independent_audit_pass_record.json`
- acceptance_closure: `results/provenance/current_full81_production_generation_g1_acceptance_r1/acceptance_closure.json`
- acceptance_manifest: `results/provenance/current_full81_production_generation_g1_acceptance_r1/acceptance_manifest.json`
- production_authority_re_freeze: `results/provenance/current_full81_production_generation_g1_re_freeze_r1/production_authority_re_freeze_record.json`
- accepted_lifecycle_record: `results/provenance/current_full81_production_generation_g1_accepted_lifecycle/accepted_lifecycle_record.json`
- main_full81_scope_authorization: `results/provenance/main_full81_authorization_g1/main_full81_authorization.json`
- main_full81_no_solve_preflight_evidence: `results/provenance/main_full81_no_solve_preflight_g1/main_full81_21d_no_solve_preflight_evidence.json`
- main_full81_execution_authorization: `results/provenance/main_full81_execution_authorization_g1/main_full81_execution_authorization.json`

## Next legal gate

`FRESH_INDEPENDENT_READ_ONLY_AUDIT` of this candidate. Nothing in this package
may be treated as audited, accepted, frozen or authorized.

```identity-claims
/runtime_identity/digest 8cca5e81d62ab3976aaeeeea162bdfdca7867af4871156446bbcae4ece65eabc
/validation_identity/digest 1bd49904e8d774c27b5e8a0390240eb836e92fa6cf857948f7b9d3486914111b
/governance_authority_identity/digest 360c81b133440e1b0444e01f2fd120eb1f49d0db3501283773a2952c032dbeb4
/candidate_change_ledger/sha256 e1b2ecc8fcb44327b4d8e0a38f1fd7ba200bd9fa44b363ceaf89220aadbde080
```
