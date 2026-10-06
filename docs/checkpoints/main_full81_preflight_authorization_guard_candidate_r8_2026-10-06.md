# Main Full81 Preflight Authorization Guard — Candidate R8

**Date:** 2026-10-06
**Candidate:** `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8`
**Generation / lineage:** `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1` / `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_R1`
**Predecessor:** `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7` — independent audit **FAIL / NO-GO** (`R7-AUD-01` CRITICAL)
**Scope:** repair of the `R6-AUD-01` defect class as `R7-AUD-01` exposed it, and nothing else; no scientific change
**Status:** CANDIDATE — IMPLEMENTATION PASS / PENDING FRESH INDEPENDENT READ-ONLY AUDIT. Not audited, not published, not accepted, not frozen.

---

## 0. How identities are stated in this checkpoint

Every raw SHA-256 here appears ONLY inside an `identity-claims` block, as
`<RFC 6901 manifest pointer> <digest>`. A claim is accepted only if its pointer
is a canonical identity pointer that the validator BOUND to one closed-world
role, and its digest equals that role's independently established value. Under
contract V4 every historical role value is established by the EXTERNAL
historical authority (section 3), never by candidate material. Git object
identities below are 40-hex and are not raw SHA-256 identity claims.

## 1. Package binding

**Manifest path:** `results/provenance/main_full81_preflight_authorization_guard_candidate_r8_2026-10-06/preflight_authorization_guard_manifest.json`
**Change ledger path:** `results/provenance/main_full81_preflight_authorization_guard_candidate_r8_2026-10-06/candidate_change_ledger.json`

Finalization order (acyclic): change ledger → this checkpoint → manifest. The
manifest binds this checkpoint and the ledger.
This checkpoint deliberately does not record the manifest's digest: the
manifest hashes this file, so the reverse would be a circular raw-byte
dependency and any value written here would be stale by construction. The
manifest's final identity is bound externally by later lifecycle role records,
none of which exists.

```identity-claims
/candidate_change_ledger/sha256 8f0adccf9016134094388e12c28dc47352cf1a69804ad63c691b31c2a5caec6f
```

## 2. Lifecycle state

| Item | State |
| --- | --- |
| R1 | historical publication STOP / NOT_ACCEPTED |
| R2–R7 | historical independent-audit FAIL / NO-GO / NOT_ACCEPTED |
| R8 | **ACTIVE_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT** |
| Production authority | **NOT_FROZEN** |
| Main Full81 authorization | **NOT_GRANTED** |
| Preflight / real 21c / real 21d / Full81 | NOT_AUTHORIZED / NOT_RUN |
| A2 | **HARD_BLOCKED** |

Same-generation advance re-derived by `same_generation_advance_lawfulness`:
accepted-lifecycle slot absent; lawful. Implementation PASS is not
independent-audit PASS. Nothing here self-accepts or closes a finding:
`R6-AUD-01` and `R7-AUD-01` remain OPEN until a fresh independent audit.

## 3. Defect-class repair — the external historical authority (contract V4)

**R7-AUD-01 (CRITICAL).** R7's GATE took every historical role's expected
value from `HISTORICAL_ROLE_IDENTITIES`, a table in candidate source covered
only by a recomputable implementation digest. A recomputing author rewrote the
table, manifest, ledger and checkpoint together and restored GATE PASS with
lawful historical digests in the wrong roles.

**Contract V4.** In EVERY mode the GATE now derives historical semantic truth
from externally authenticated evidence, in this fixed order:

1. **Git-frozen pre-R8 trust root.** `refs/tags/v7.4-main-full81-pre-r8-historical-trust-root-accepted-2026-10-06` must resolve to the
   annotated tag object `6b31fef7c84bd0646a7171cf8168564ee969b10f`, which must name commit
   `c8f3665d5c67e0cae3222073cd71b9a6231279b1`; that commit must carry blob `d10707b922004f3084ae6045fe3f1b1caf6eaea4` at
   `docs/checkpoints/main_full81_preflight_pre_r8_historical_trust_root_2026-10-06.json`; the blob must be the frozen bytes; HEAD must still carry
   it; the commit must be in the ancestry of HEAD and of `origin/thesis-v7`;
   and the working-tree copy must be unaltered. The trust root is read from the
   Git blob. Candidate R8 consumes this frozen identity; it did not choose it.
2. **Accepted R7 Preservation Authority Binding.** Its locator and raw SHA-256
   are read FROM the trust-root blob — they are not restated anywhere in
   candidate source or in this package — and its bytes must be exactly those.
   Locator: `results/provenance/main_full81_preflight_guard_r7_preservation_authority_binding_2026-10-06/r7_preservation_authority_binding.json`.
3. **Authenticated R7 preservation package.** Archive, raw-byte index and STOP
   record must be exactly the bound bytes and must agree with one another
   (archive members equal the index records; index and STOP record restate the
   binding's identities).
4. **Role derivation from that evidence's own structure.** R1–R6 package roles
   from the index's per-candidate record of the packages it verified; R7 package
   roles and the R7 predecessor evidence from the binding (cross-checked against
   index and STOP record); the R7 EOL policy from the archived member that has
   that role; and the predecessor change set from the R7 surface the index
   records versus live bytes.

`HISTORICAL_ROLE_IDENTITIES` survives only as a DIAGNOSTIC ASSERTION: it must
equal the external derivation exactly, no value is ever read from it, and when
the external evidence is unavailable there is no fallback — the GATE fails
closed. Every historical mismatch raises
`U06_EXTERNAL_HISTORICAL_AUTHORITY_MISMATCH`; missing evidence raises
`U06_EXTERNAL_HISTORICAL_AUTHORITY_UNAVAILABLE`; inconsistent evidence raises
`U06_EXTERNAL_HISTORICAL_EVIDENCE_INVALID`; a trust-root Git defect raises
`U06_TRUST_ROOT_GIT_AUTHORITY_INVALID`.

The failed runtime-selection-authority candidate is not consumed, not a
fallback, not an intermediary and not a parent: the chain is trust root →
binding.

**Durability boundary (carried, not solved).** The R7 binding and the R1–R7
preservation bytes are gitignored. They are authenticated by locator and
SHA-256 only; when absent, the GATE fails closed. Their Git durability is not
established by this candidate.

**R6-AUD-02** is out of scope: the R7 write-containment code is carried
unchanged and is NOT independently verified. `FULLSTACK-01` and `N-R5D-04` are
carried unchanged and not expanded.

## 4. Predecessor (R7) identities — external historical roles

```identity-claims
/implementation_identity/predecessor_digest cb78b3ac0c5bcee793757f0de7a3684f248b70abac1226e5b263f11fa6690b5c
/package_binding/predecessor_defect/predecessor_candidate_checkpoint/raw_sha256 cff4273fc9cb1080dc3f4fb7d9060febc002262ac81ee4fb69e76e83ebdf150c
/package_binding/predecessor_defect/predecessor_candidate_manifest/raw_sha256 3d9a27f08ad60c9d08971e6fc652f7cdd31fa5dd89ef52057a51918de5bdeb6f
/candidate_preservation_packages/MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7/archive_sha256 5b9042a59f43852c0c9c19b37df2c10cdd7588952df2bd5eecaaf7c46af8a4ae
/candidate_preservation_packages/MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7/index_sha256 ebf2b1ad3185e78e918e86dd67420ace44be5ccc387ea142a5e85d468884b225
/candidate_preservation_packages/MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R7/stop_record_sha256 4f48982132784aec932e0100202f16db5bb45544934adfb382127f23e0cc8066
```

## 5. Change set (R7 → R8)

7 files changed relative to R7's externally authenticated preserved
surface; their R7 and R8 raw SHA-256 values, classifications and reasons are in
the change ledger. The raw-byte difference is the authoritative evidence. The
change set itself is re-derived by the GATE from the R7 surface, never taken
from this list.

- `.gitattributes` — EOL_POLICY_EXACT_PATH_EXTENSION
- `src/main_full81_authorization_v7_4.py` — CANDIDATE_POINTER_ADVANCE
- `src/production_authority_bundle_v7_4.py` — AUTHORITY_PIN_VALUE_UPDATE_AND_EXTERNAL_TRUST_ROOT_IDENTITY
- `src/production_authority_lifecycle_u06.py` — LIFECYCLE_VALIDATOR_CORRECTION
- `tests/test_21f_u06_accepted_lifecycle_gate.py` — TEST_CURRENT_CANDIDATE_POINTER_UPDATE
- `tests/test_21h_main_full81_authorization_mechanism.py` — TEST_CURRENT_CANDIDATE_POINTER_UPDATE
- `tests/test_21j_authority_raw_byte_eol_coverage.py` — TEST_NEGATIVE_CONTROL_ALIGNMENT_TO_EXTERNAL_HISTORICAL_AUTHORITY

Added: this checkpoint, the manifest, the change ledger, and the attack suite
`tests/test_21k_external_historical_authority_attacks.py` (declared in
`VALIDATION_IDENTITY_PATHS`).

## 6. Implementation identity (21 paths)

```identity-claims
/implementation_identity_digest dcbd0fbe24e09e15141d403d47f97109457b1757350244ce3da66d096e3f78ba
/implementation_identity/paths/scripts~108_calibrate_kappa.py 6014a24bee5028d0be1e3ab480ee67587e91c35bc4d57e4b0c324eb6b94141dc
/implementation_identity/paths/scripts~109_build_valid_outage_start_sets.py 3c67e91848c7093e974bf3d3b8440a4c3054ffe25a4fc99b68fd951883ae43d4
/implementation_identity/paths/scripts~115a_benchmark_eob_charge_discharge_formulations.py 504f31b37f2bbaca96792b088cd1adea087206539a3c3553298555f64fc6cff9
/implementation_identity/paths/scripts~115b_freeze_production_eob_baseline.py 9a5f61d19bc279920f51f67294ef96ddcd7623ffe240482ff66b88e029eafc60
/implementation_identity/paths/scripts~115c_validate_production_eob_rainflow.py 14fd9f3363979dd6af6f50723a75477e1525b9330265a0a820d11eec1774f408
/implementation_identity/paths/scripts~115d_run_corrected_eob_v7_2.py 90d19baac8c0b96e08de00b4769b7ae68dff745f71923b850433ffc2935091a8
/implementation_identity/paths/scripts~116a_preflight_layer_a_representative_binary_cases.py 5813119e258e83a45a245ec715ade4536bf9dbf880687f6d3f1e978cce8b06a0
/implementation_identity/paths/scripts~119a_preflight_final_layer_a_81_cases.py a139f1cd1a76e0a6f0657adf025c521b8b966b2fcdd6f74e5f3936a70bab72d3
/implementation_identity/paths/scripts~119b_run_final_layer_a_81_cases.py 4abbda9dc2529f9d7531aff64a77fdf23c3b8b59173a6f3287fda0538def2bbe
/implementation_identity/paths/scripts~121a_preflight_v7_3_production_routing.py 3d99a4200dce93cd00db94727f72489d9be497eb52c74270a1c49b17fc8a7e95
/implementation_identity/paths/scripts~121b_preflight_v7_3_eob_successor.py d12f39acfa33651e49f8f6762c159e5cff217958e34736fca1b15077bda45aa3
/implementation_identity/paths/scripts~121c_preflight_v7_3_layer_a_successor.py 63d9e8b9b3ca968b3df6d76c457ee5329697cfc9a648f2a35978ce23a4eaf0ed
/implementation_identity/paths/scripts~121d_preflight_v7_3_final81_successor.py 1a55c34897548a3595a9812dfeaa854f3b6b478594630c750931cd7cf2371bd1
/implementation_identity/paths/scripts~121e_preflight_v7_4_production_authority_alignment.py 6b97be4258f0cccf3538a9078548951d0f4fc5d1ede7c43ae94cd26319568803
/implementation_identity/paths/src~1annual_design_model_v7_2.py 9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8
/implementation_identity/paths/src~1main_full81_authorization_v7_4.py 075194395bee713f74a7a12d26afb0f1ea46245dd1f847ec4979389f8260d51b
/implementation_identity/paths/src~1production_authority_bundle_v7_4.py c4946af57ce1fe4c60baf3d8c7a89f8ab13526a22acce769f7fbc2cb6c82efba
/implementation_identity/paths/src~1production_authority_lifecycle_u06.py aebd2c5924027eba15fb0114cf155dadaee3505929c2f45e2ffbfadb748a37f3
/implementation_identity/paths/src~1production_input_authority_v7_3.py f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1
/implementation_identity/paths/src~1production_successor_stack_v7_3.py 65728c40e8df746da92865e859072c345370ae93aa4a2b32a24b149c67a3dcda
/implementation_identity/paths/src~1rainflow_validation_v7_2.py 4ae83643dca4e7266ad0e4ebe54c0302a1cf38918935c8789e493798ea6c09d2
```

## 7. Scientific and governance authority (unchanged scientific bytes)

```identity-claims
/authority_bundle/pins/framework_v7_4/sha256 36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273
/authority_bundle/pins/registry_v7_4/sha256 5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433
/authority_bundle/pins/canonical_planning_input/sha256 3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428
/authority_bundle/pins/parameter_registry/sha256 c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1
/authority_bundle/pins/repository_eol_policy/sha256 64e39b0787eda885b19566d7cf46aa225823387f7070b437fb261a39e66925fc
```

Authority bundle: 7 groups, 34 pins (labels, paths and
groups unchanged); re-pinned: `u06_lifecycle_overlay`,
`main_full81_authorization_mechanism`, `repository_eol_policy`,
`u06_lifecycle_test`, `main_full81_authorization_test`. Separately,
32 diagnostic historical-role assertions (not bundle pins, not authority).
EOL policy: 120 derived raw-byte consumers, 120 exact rules,
0 uncovered / 0 wrongly treated / 0 overreaching / 0 unused.

## 8. Findings register

| Finding | Status |
| --- | --- |
| R7-AUD-01 | REPAIR IMPLEMENTED IN R8 / NOT YET INDEPENDENTLY VERIFIED / OPEN |
| R6-AUD-01 | REPAIR IMPLEMENTED IN R8 / NOT YET INDEPENDENTLY VERIFIED / OPEN |
| R6-AUD-02 | UNRESOLVED / OUT OF R8 SCOPE / R7 CODE CARRIED UNCHANGED |
| R5-AUD-01, R5-AUD-02 | OPEN / NOT YET INDEPENDENTLY VERIFIED |
| R5-AUD-03 | NONBLOCKING / CARRIED |
| FULLSTACK-01 | OPEN / CARRIED UNCHANGED |
| N-R5D-04 | OPEN / CARRIED UNCHANGED |
| Binding / R7 preservation Git durability | NOT ESTABLISHED / CARRIED SEPARATELY |

## 9. Tests

| Suite | Ran | Failures | Errors | Skipped | Result |
| --- | --- | --- | --- | --- | --- |
| `tests/test_21a_v7_3_production_routing_preflight.py` | 19 | 0 | 0 | 0 | OK |
| `tests/test_21b_21d_v7_3_production_successor_stack.py` | 67 | 0 | 0 | 0 | OK |
| `tests/test_21e_v7_4_production_authority_bundle.py` | 34 | 0 | 0 | 0 | OK |
| `tests/test_21f_u06_accepted_lifecycle_gate.py` | 54 | 0 | 0 | 0 | OK |
| `tests/test_21g_u06_r3_substitution_attacks.py` | 31 | 0 | 0 | 0 | OK |
| `tests/test_21h_main_full81_authorization_mechanism.py` | 72 | 0 | 0 | 0 | OK |
| `tests/test_21i_main_full81_preflight_authorization_guard.py` | 50 | 0 | 0 | 0 | OK |
| `tests/test_21j_authority_raw_byte_eol_coverage.py` | 124 | 0 | 0 | 1 | OK |
| `tests/test_21k_external_historical_authority_attacks.py` | 13 | 0 | 0 | 0 | OK |

One process per suite, `python -m unittest`, `PYTHONDONTWRITEBYTECODE=1`; no
solver, no production run. Each suite's raw SHA-256 is in the change ledger's
`tests_executed`.

Skipped by the environment (not a pass):

- `tests/test_21j_authority_raw_byte_eol_coverage.py` :: test_symlink_escape_is_refused_before_any_write (DisposableWriteContainmentTests): symbolic links unavailable here: [WinError 1314] A required privilege is not held by the client

This is R7's carried R6-AUD-02 control, unchanged by R8; the same link decision
is exercised on a real junction and by a deterministic decision-logic control.

## 10. Counters and next gate

No staging, commit, push, tag or stash. No preflight, no real 21c / 21d, no
production model construction, no `optimize()`, no MILP solve, no Full81 case,
no A2 action. Repository HEAD at authoring: `c8f3665d5c67e0cae3222073cd71b9a6231279b1`.

**Next legal gate:** FRESH INDEPENDENT READ-ONLY AUDIT OF `MAIN_FULL81_PREFLIGHT_AUTHORIZATION_GUARD_CANDIDATE_R8`.
