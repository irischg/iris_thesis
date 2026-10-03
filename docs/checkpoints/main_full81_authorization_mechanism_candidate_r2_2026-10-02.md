# Main Full81 Authorization-Mechanism Successor — Candidate R2

**Date:** 2026-10-02
**Lineage:** `MAIN_FULL81_AUTHORIZATION_MECHANISM_R1`
**Candidate ID:** `MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2`
**Immediate predecessor:** `MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R1` — **FAILED**
**Accepted predecessor authority:** U-06 R3, commit `e10f8f123af19c0796f5045a51807486cb58647a`

> ## STATUS
>
> **CANDIDATE R2**
> **NOT ACCEPTED**
> **NOT FROZEN**
> **DOES NOT AUTHORIZE MAIN FULL81**
> **DOES NOT AUTHORIZE FULL81 PREFLIGHT**
> **DOES NOT AUTHORIZE FULL81 EXECUTION**
>
> This pass created **no** independent audit PASS, acceptance closure,
> acceptance manifest, production-authority re-freeze record,
> accepted-lifecycle record, or Main Full81 authorization. None may be inferred
> from it.
>
> **Independent audit — performed 2026-10-03.** A fresh, strictly independent,
> read-only audit returned **`CONDITIONAL PASS — REMEDIATION SOUND BUT
> ACCEPTANCE BLOCKED PENDING SPECIFIED NON-SCIENTIFIC CORRECTION`**, closing
> `H-01` and `H-02`. It did **not** accept this candidate, create any acceptance
> artifact, re-freeze production authority, or create any Main Full81
> authorization. An audit verdict is never self-acceptance.
>
> **Provenance correction — 2026-10-03 (this revision).** That audit found the
> `J-01` accepted-suite disclosure in §5 materially inaccurate. §5 is corrected
> here: §5.2 carries the corrected regression accounting, including three
> previously undisclosed `tests/test_21g` regressions, and §5.3 records the
> carried independent-audit findings. The correction is **documentation and
> provenance only** — no production code, no test byte, no methodology, no
> Framework, no Registry, and no implementation identity changed. The
> Candidate-R2 implementation identity therefore remains
> `1644c426f9dceba081cd3cccf0501623ccfbeeaef5b3131b565fbf928615900f`.
>
> Because this revision changes the candidate-checkpoint bytes **after** the
> audit read them, the verdict above attaches to the pre-correction checkpoint
> identity
> `c98052420f18bb7c0ede19bcfef8c93de63f5503b6bbfd18700c88374b938dfc`, and this
> revision **requires fresh independent verification** before acceptance (§7).
> No lifecycle role artifact of any generation exists, so no published artifact
> bound the superseded checkpoint identity and nothing is invalidated by the
> change.

---

## 1. Candidate R1 — failed, preserved, not promoted

A strictly read-only audit of Candidate R1 returned
**`NO LAWFUL SUCCESSOR PROMOTION / RE-FREEZE PATH EXISTS — CANDIDATE REVISION
REQUIRED`** on two findings:

| Finding | Severity | Substance |
|---|---|---|
| `H-01` | **CRITICAL** | The production-authority lifecycle overlay was single-generation and hard-bound to U-06 R3, so no lawful path existed from CANDIDATE → INDEPENDENTLY AUDITED → ACCEPTED → RE-FROZEN for changed implementation bytes. The first impossible transition was **T2** (`U06_LINEAGE_MISMATCH`). Reaching `FROZEN` would have required **mutating** accepted R3 artifacts. |
| `H-02` | MAJOR | The Full81 authorization validator statically bound `REQUIRED_U06_LINEAGE_ID` to the predecessor R3 lineage, so even after a lawful generation advance every authorization would have failed. |

Candidate R1 is now **immutable failed historical candidate provenance**. Its
checkpoint and manifest are **byte-unchanged**:

| R1 artifact | SHA-256 |
|---|---|
| `docs/checkpoints/main_full81_authorization_mechanism_candidate_r1_2026-10-02.md` | `6ee0d67d34174070a63a7f5034957de6103c5fce47917e3893ea48966cb384a1` |
| `results/provenance/main_full81_authorization_mechanism_candidate_r1_2026-10-02/authorization_mechanism_manifest.json` | `563ffa467cfac298cd3de3a1ee63976ebe98537c2d7169714636736c18205303` |

**Source-byte preservation.** R1's implementation bytes were uncommitted
working-tree bytes. Editing them in place would have made R1's exact source
unrecoverable — reproducing exactly the `A-06` defect the U-06 R3 pass recorded
(*"R2 edited those modules in place before any snapshot existed, so R1 source
bytes are not recoverable… the snapshot practice begins with R2"*). This pass
therefore used the repository's own established failed-candidate
source-snapshot precedent — `<new candidate dir>/superseded_sources/` — before
touching any byte. R1 was **not** committed for convenience; the protocol's
preservation mechanism is the snapshot, not a commit.

Snapshot: `results/provenance/main_full81_authorization_mechanism_candidate_r2_2026-10-02/superseded_sources/`
holding `r1_main_full81_authorization_v7_4.py`,
`r1_production_authority_lifecycle_u06.py`,
`r1_production_authority_bundle_v7_4.py`,
`r1_production_successor_stack_v7_3.py`,
`r1_21d_preflight_v7_3_final81_successor.py`, and
`r1_test_21h_main_full81_authorization_mechanism.py`. Every digest matches the
inventory R1's own manifest published.

---

## 2. H-01 remediation — production-authority generations

The overlay is no longer single-generation. A generation is now a value:

```python
@dataclass(frozen=True)
class AuthorityGeneration:
    generation_id, lineage_id, candidate_id,
    candidate_checkpoint_path, candidate_manifest_path,
    accepted_lifecycle_record_path, schema_prefix,
    superseded_candidate_ids, candidate_artifact_paths,
    predecessor_generation_id, predecessor_lineage_id,
    predecessor_accepted_lifecycle_record_path, disposition
```

| | Generation 1 (predecessor) | Generation 2 (current) |
|---|---|---|
| `generation_id` | `U06_V7_4_PRODUCTION_AUTHORITY_R3` | `MAIN_FULL81_AUTHORIZATION_MECHANISM_R2` |
| `lineage_id` | `U06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_R3` | `MAIN_FULL81_AUTHORIZATION_MECHANISM_R1` |
| `candidate_id` | `…ALIGNMENT_CANDIDATE_R3` | `MAIN_FULL81_AUTHORIZATION_MECHANISM_CANDIDATE_R2` |
| candidate manifest | `…alignment_candidate_r3_2026-10-02/alignment_manifest.json` | `…authorization_mechanism_candidate_r2_2026-10-02/authorization_mechanism_manifest.json` |
| accepted-lifecycle slot | `…u_06_v7_4_production_authority_accepted_lifecycle_r3/` | `…main_full81_authorization_mechanism_accepted_lifecycle_r2/` |
| schema prefix | `iris-thesis-u06-r3-` | `iris-thesis-full81-auth-mech-r2-` |
| disposition | `IMMUTABLE_HISTORICAL_ACCEPTED_PREDECESSOR_GENERATION` | `CURRENT_GENERATION_CANDIDATE_NOT_ACCEPTED_NOT_FROZEN` |

The two generations have **disjoint** lineages, candidate ids, candidate paths,
record slots and role `schema_version` namespaces, so neither can satisfy the
other's roles.

Every validator — `_validate_role_path`, `validate_role_envelope`,
`_validate_bound_roles`, `validate_role_specifics`,
`validate_accepted_lifecycle_payload`, `absent_lifecycle` — now takes the
generation, defaulting to `CURRENT_GENERATION` so an omission can never let a
superseded generation authorise anything. `resolve_u06_lifecycle` reads **only**
the current generation's record slot, and `require_frozen_lifecycle` adds two
new invariants (`generation_id`, `is_current_generation`) that reject a
superseded generation with `U06_SUPERSEDED_GENERATION_REJECTED`. The aggregator
gained `U06_CROSS_GENERATION_ROLE_REJECTED`.

**Generalised, not repeated.** Advancing to a further generation needs one new
`AuthorityGeneration` plus a change of `CURRENT_GENERATION`. It requires no
validator rewrite and touches no predecessor artifact —
`future_acceptance_requirements()` asserts both, and `tests/test_21h` proves them.

**No U-06 R3 artifact was mutated.** `git diff --name-only HEAD` is empty for
the R3 accepted-lifecycle record, candidate manifest, and candidate checkpoint.
Every accepted R3 constant name keeps its accepted value
(`LINEAGE_ID`, `R3_CANDIDATE_ID`, `R3_CANDIDATE_CHECKPOINT_PATH`,
`R3_CANDIDATE_MANIFEST_PATH`, `ACCEPTED_LIFECYCLE_RECORD_RELATIVE_PATH`,
`LIFECYCLE_RECORD_SCHEMA_VERSION`, `ROLE_CONTRACTS`), and the overlay still
contains **zero** 64-hex literals. Predecessor digests and commits are read from
the predecessor's own on-disk record and from live Git, never hard-coded.

---

## 3. H-02 remediation — the binding is resolved, not static

Removed: `REQUIRED_U06_LINEAGE_ID = U06_LINEAGE_ID`. **No expected-lineage
constant exists any more** — `tests/test_21h` asserts this by AST scan of the
module's own assignments.

The validator now resolves the live accepted/frozen lifecycle **first**, then
derives the expected binding from that mapping:

```text
require_frozen_lifecycle_against_live_implementation(root, lifecycle)
  -> resolved["generation_id"]  -> required production_authority_generation_id
  -> resolved["lineage_id"]     -> required production_authority_lineage_id
  -> resolved["record_path"]    -> required accepted-lifecycle record path
  -> resolved["is_current_generation"] must be True
```

New status `FULL81_AUTHORIZATION_PRODUCTION_AUTHORITY_BINDING_INVALID` replaces
the predecessor-specific `…U06_BINDING_INVALID`.

### Field rename and schema version (§9)

The rename is **not** cosmetic: these fields must name whatever production
authority is current, and `u06_*` names encode a predecessor generation that is
no longer current. Keeping them would be a standing invitation to
predecessor-generation confusion.

| Candidate R1 | Candidate R2 |
|---|---|
| `u06_lineage_id` | `production_authority_lineage_id` |
| `u06_accepted_lifecycle_record` | `production_authority_accepted_lifecycle_record` |
| `u06_publication_commit` | `production_authority_publication_commit` |
| — | `production_authority_generation_id` *(new)* |

Because the semantics changed materially, the schema version advanced:
**`iris-thesis-full81-authorization-v1` → `iris-thesis-full81-authorization-v2`**,
with v1 recorded in `SUPERSEDED_AUTHORIZATION_SCHEMA_VERSIONS` and actively
rejected. No authorization artifact has ever existed under v1, so nothing is
orphaned. The lawful path also advanced to
`results/provenance/main_full81_authorization_r2/main_full81_authorization.json`,
and the R1 path is barred by `FULL81_AUTHORIZATION_SUPERSEDED_CANDIDATE_REJECTED`.

`REJECTED_LINEAGE_IDS` is now **derived from the live generation registry** plus
the historical V7.2 labels, so a future generation advance extends it with no
edit. Commit `e10f8f12…` appears nowhere in the module — the mechanism contains
zero 40-hex literals.

---

## 4. Promotion-path control (T1 → T7)

Proved in an isolated throwaway Git repository with four publication commits
(`commit_base`, Phase A, Phase B, Phase C) and no repository writes:

| Transition | Role / artifact | Result |
|---|---|---|
| T1 | `implementation_candidate` = the R2 candidate manifest | **OK** |
| T2 | `independent_audit_pass`, `iris-thesis-full81-auth-mech-r2-independent-audit-pass-v1` | **OK** |
| T3 | `acceptance_closure`, Phase-A commit containment proved | **OK** |
| T4 | `acceptance_manifest` | **OK** |
| T5 | `production_authority_re_freeze`, Phase-B commit containment proved | **OK** |
| T6 | `U06_ACCEPTED_LIFECYCLE` aggregator at the R2 slot → `PRESENT_VALID` | **OK** |
| T7 | `PRODUCTION_AUTHORITY_FREEZE_STATUS = FROZEN` under the R2 digest | **OK** |

All seven are representable with the current R2 schemas and validators, with no
further production-code edit and no mutation of any U-06 R3 artifact. A lawful
R2 authorization then reaches exactly `AUTHORIZED_FOR_NO_SOLVE_PREFLIGHT`, and
the execution interlock still raises `FULL81_EXECUTION_NOT_AUTHORIZED`.

---

## 5. Open / carried findings

### 5.1 Candidate-R2 findings

| ID | Severity | Finding |
|---|---|---|
| `J-01` | **MINOR** | Lifecycle-stale assertions in the accepted R3 suites change outcome under the lawful generation advance. **No accepted test byte was modified.** Every current failure is confirmed **fail-closed** — the gate *refused*; it never accepted. The accounting published in the pre-correction revision of this checkpoint was **materially inaccurate and is corrected in §5.2**, which supersedes it. |
| `J-02` | INFORMATIONAL | `scripts/21e` still contains the lifecycle-stale assertion that the lifecycle gate must reject (`U06_LIFECYCLE_GATE_DID_NOT_REJECT` when lawfully frozen). It is unmodified and outside this bounded scope. |
| `J-03` | INFORMATIONAL | The module is still named `production_authority_lifecycle_u06.py` although it now hosts a generation registry. Renaming it would break the accepted pin set and the accepted R3 test imports for no governance gain, so the name is retained as historical provenance naming — the same disposition the bundle already records for the `v7_3` output-namespace segment. |
| `J-04` | INFORMATIONAL | `A-05` (LF/CRLF portability) and `A-04` (verifier/test self-reference) remain recorded only. All new bytes are LF. **Superseded in part by `I-04` (§5.3)**, which re-classifies the LF/CRLF question as a MAJOR carried promotion-path dependency. |
| `J-05` | INFORMATIONAL | The alpha/beta universe and Layer-A solver settings remain declared in the mechanism to avoid an import cycle, cross-checked against the live stack constants by `tests/test_21h`. |

### 5.2 `J-01` corrected — accepted-suite regression accounting

**This subsection supersedes the accounting published in the pre-correction
revision of this checkpoint.** That revision reported `15` baseline failures →
`14`, with `8` resolved and `7` newly failing, and did not enumerate
`tests/test_21g` at all. The independent audit of 2026-10-03 re-measured the
baseline mechanically and those figures do not stand.

**Counting methods, stated explicitly.** Two different units were in use, which
is the origin of part — but not all — of the discrepancy.

| | Pre-correction revision | **Independent audit (authoritative)** |
|---|---|---|
| unit counted | assertions attributable to the generation advance, in `test_21b_21d` and `test_21f` only | **distinct failing test methods, across all five accepted suites** |
| baseline failures | 15 | **17** |
| current failures | 14 | **14** *(agrees)* |
| resolved | 8 | **12** |
| newly failing | 7 | **9** |

The authoritative figures are the distinct-failing-test counts. They were
obtained by running the five accepted suites against an isolated clone of the
accepted predecessor bytes, proved to be the predecessor by its implementation
identity digest
`b854d0f133ee38f4e9e534c1accdf50b0438b18d681acdb035d8a97d90218e9a`
(20 accepted paths, 16 runtime paths, no `CURRENT_GENERATION` symbol), with test
counts matching the live tree exactly (19 / 66 / 34 / 40 / 31).

The unit difference does **not** account for the three `tests/test_21g`
regressions below: those are whole tests that pass at the accepted predecessor
and fail under Candidate R2 under *either* unit, and they were omitted
altogether. **Nothing in this record should be read as the independent audit
having confirmed the 15 / 8 / 7 accounting. It did not.**

#### Newly failing under Candidate R2 — 9 distinct tests

**Cause A — a pre-generation synthetic lifecycle mapping can no longer freeze
(3).** These accepted tests hand-build a lifecycle mapping that predates the
generation concept, so it carries no `generation_id` / `is_current_generation`.
`require_frozen_lifecycle` now refuses it. In each case the gate *raised*.

- `tests/test_21b_21d_v7_3_production_successor_stack.py::ProductionSuccessorStackV73Tests::test_deployment_gate_pass_fixture_and_all_repository_failures`
- `tests/test_21f_u06_accepted_lifecycle_gate.py::StackIntegrationTests::test_snapshot_lifecycle_defaults_to_the_safe_value`
- `tests/test_21f_u06_accepted_lifecycle_gate.py::PostAcceptanceCodeDriftTests::test_stale_accepted_identity_fails_closed_against_live_code`

Making any of these green would require treating a mapping with no declared
generation as the current generation — a **fail-open** change. Refused.

**Cause B — rejection status string changed, rejection unchanged (1).**

- `tests/test_21f_u06_accepted_lifecycle_gate.py::PostAcceptanceCodeDriftTests::test_the_gate_applies_the_live_drift_recheck`
  — still rejected, reporting `U06_ACCEPTED_LIFECYCLE_INVALID` where the test
  expects `U06_IMPLEMENTATION_IDENTITY_DRIFT`.

**Cause C — the live lifecycle and dependency report now name the current
generation (2).** `resolve_u06_lifecycle` and `runtime_dependency_report` report
`MAIN_FULL81_AUTHORIZATION_MECHANISM_R2` / `…MECHANISM_R1`, not the superseded
R3 identity. These are report-only; no gate changed.

- `tests/test_21f_u06_accepted_lifecycle_gate.py::LiveLifecycleStateTests::test_lineage_identity_is_r3`
- `tests/test_21f_u06_accepted_lifecycle_gate.py::StackIntegrationTests::test_stack_payload_carries_the_audited_dependency_report`

Reporting a superseded lineage in a field named `lineage_id` is precisely the
predecessor-generation confusion this candidate was asked to prevent, so the
fields report the current generation. The accepted field `u06_lineage_id` in the
stack payload **is** retained at its R3 value, additively.

**Cause D — previously undisclosed: the `tests/test_21g` A-01 attack suite
(3).** These three were **not** disclosed in the pre-correction revision. They
are recorded here in full because `tests/test_21g_u06_r3_substitution_attacks.py`
is the suite that exists specifically to defend the CRITICAL `A-01` finding, so
any change in its outcome is governance-relevant whatever its cause.

- `tests/test_21g_u06_r3_substitution_attacks.py::FiveArtifactAttackTests::test_all_json_substitution_is_rejected_on_artifact_type`
- `tests/test_21g_u06_r3_substitution_attacks.py::FiveArtifactAttackTests::test_attack_with_a_correct_candidate_role_still_fails_at_the_audit`
- `tests/test_21g_u06_r3_substitution_attacks.py::PerRoleSubstitutionTests::test_a_declared_digest_that_does_not_match_live_bytes_is_rejected`

Independently determined disposition, recorded truthfully:

- **all three attacks remain rejected** — none is admitted;
- **all three are fail-closed**; the behavioural security property of the `A-01`
  remediation is preserved in full;
- Candidate R2 rejects the attack **one gate earlier** than the historical test
  anticipated;
- the observed status is **`U06_IMPLEMENTATION_IDENTITY_DRIFT`** rather than the
  historical test's expected artifact-type / target-stage rejection, because
  these tests construct R3-generation role records against a live
  implementation surface that is now Candidate R2's, so the
  `implementation_identity_digest` check in `validate_role_envelope` fires
  before the `artifact_type` / `target_candidate_id` check;
- **no production fail-open regression is hidden behind these failures.**

Restoring the historical diagnostic status would mean reordering the envelope
checks so artifact-type precedes digest. That is a diagnostics-only change, it
is **not** authorized by this provenance pass, and it must not be done by
weakening any production check. The accepted historical test bytes are **not**
edited.

#### Pre-existing and unchanged — 5 distinct tests

These fail at the accepted predecessor **and** under Candidate R2. Their cause
is the U-06 R3 acceptance/freeze commit `e10f8f12…` having published the R3
lifecycle without retiring assertions written during R3's own candidate phase.
They are not attributable to this candidate.

- `tests/test_21f_u06_accepted_lifecycle_gate.py::FailClosedFreezeGateTests::test_the_guard_is_not_vacuous` — see §5.2.1
- `tests/test_21f_u06_accepted_lifecycle_gate.py::LiveLifecycleStateTests::test_no_accepted_lifecycle_record_exists_yet` — asserts the R3 record is absent; it was published at `e10f8f12…`
- `tests/test_21g_u06_r3_substitution_attacks.py::NoFabricatedFutureIdentityTests::test_no_lifecycle_artifact_exists_yet` — same premise
- `tests/test_21g_u06_r3_substitution_attacks.py::PublicationProofAttackTests::test_arbitrary_ancestor_is_not_proof_for_a_file_absent_there` — premised on the R3 candidate being untracked; it is now tracked and genuinely published, so containment correctly succeeds
- `tests/test_21g_u06_r3_substitution_attacks.py::PublicationProofAttackTests::test_untracked_r3_artifacts_are_not_published_in_head` — same premise

The publication-proof checks are **not** vacuous:
`test_a_genuinely_contained_artifact_is_accepted` and
`test_a_commit_predating_an_artifact_is_rejected` both pass, and the independent
audit separately provoked `U06_PUBLICATION_PROOF_INVALID` with a stale
`audit_publication_commit`.

#### 5.2.1 `test_the_guard_is_not_vacuous` — attribution corrected

The pre-correction revision listed
`tests/test_21f_u06_accepted_lifecycle_gate.py::FailClosedFreezeGateTests::test_the_guard_is_not_vacuous`
as **newly introduced** by this candidate. That attribution is **wrong** and is
corrected here: the test **already fails at the accepted predecessor**.

| | Failing assertion | Why |
|---|---|---|
| accepted predecessor | line 254, `assertFalse(lc.is_frozen(lc.resolve_u06_lifecycle(ROOT)))` | the live predecessor lifecycle **is** genuinely `PRESENT_VALID` / `FROZEN`, so the assertion that it is not frozen fails |
| Candidate R2 | line 250, `assertTrue(lc.is_frozen(complete))` | a synthetic mapping carrying no declared generation can no longer freeze, so the failure occurs **earlier** |

So the test did not begin failing with Candidate R2; its **failing assertion
moved earlier**. Under distinct-failing-test counting it is therefore
pre-existing, not newly introduced.

The substantive point of the pre-correction revision stands and is independently
confirmed: making the Candidate-R2 assertion at line 250 pass would require
treating an ungenerationed lifecycle mapping as the current generation. That is
**fail-open** and is therefore **not an acceptable production fix**. The
assertion must stay red until a successor-generation lifecycle test supersedes
it. The test is **not** modified.

#### Resolved relative to the accepted predecessor — 12 distinct tests

Recorded for completeness, and with its cause stated plainly rather than
claimed as a repair: most of these tests were written during R3's candidate
phase and assert a `NOT_FROZEN` / `ABSENT` overlay. Advancing the generation
returns the live overlay to `ABSENT`, which is the condition they were written
for. They are **not** evidence that Candidate R2 fixed a defect.

- `tests/test_21e_v7_4_production_authority_bundle.py` (5): `BundleIdentityTests::test_bundle_verifies_and_reports_candidate_alignment_only`, `FailClosedGuardTests::test_production_gate_rejects_full81_and_a2_before_any_repository_check`, `GovernanceSemanticsTests::test_unresolved_register_and_u_07_are_not_silently_resolved`, `StackAndRunnerBindingTests::test_every_case_carries_case_level_v7_4_provenance`, `StackAndRunnerBindingTests::test_stack_payload_carries_the_v7_4_alignment`
- `tests/test_21f_u06_accepted_lifecycle_gate.py` (5): `FailClosedFreezeGateTests::test_aligned_base_authority_alone_does_not_freeze`, `FailClosedFreezeGateTests::test_committed_clean_pushed_candidate_is_not_enough_for_frozen`, `LiveLifecycleStateTests::test_every_required_role_is_reported_missing`, `LiveLifecycleStateTests::test_live_lifecycle_is_absent_and_not_frozen`, `StackIntegrationTests::test_stack_payload_reports_r3_lineage_and_absent_lifecycle`
- `tests/test_21g_u06_r3_substitution_attacks.py` (2): `GateStillFailsClosedTests::test_live_gate_rejects_every_production_scope`, `GateStillFailsClosedTests::test_resolver_writes_nothing_and_never_raises`

**Precedent and recommended remedy.** This is the same transition U-06 R3 itself
made: R3 snapshotted `r2_test_21f_u06_accepted_lifecycle_gate.py` into its
`superseded_sources/` precisely because the predecessor generation's lifecycle
test had to be superseded. The remedy here is the same — a successor
lifecycle-gate test written against the R2 generation, with the R3-generation
test preserved byte-identically as historical provenance. Creating it is **not**
authorized by this pass and is deliberately not done. The independent audit
separately confirmed that the T1→T7 promotion control is already permanently
encoded in `tests/test_21h_main_full81_authorization_mechanism.py` (58 tests,
all passing), so successor coverage is **not** an acceptance blocker.

### 5.3 Carried independent-audit findings

Recorded from the independent audit of 2026-10-03. None is remediated by this
provenance pass; each is carried with its scope stated.

| ID | Severity | Status | Finding |
|---|---|---|---|
| `I-04` | **MAJOR** | **CARRIED — PROMOTION-PATH DEPENDENCY** | CRLF / EOL publication-proof fragility. See §5.3.1. |
| `I-05` | MINOR | CARRIED | Inherited identity-completeness gap for `scripts/20c_…`. See §5.3.2. |
| `I-06` | INFORMATIONAL | CARRIED | The Candidate-R1 manifest is untracked and gitignored and declares neither its own digest nor a containing commit, so its immutability is not cryptographically self-anchored. Its live bytes nevertheless match this checkpoint's claim (`563ffa467cfac298…`) and the preserved `superseded_sources/` inventory was independently recomputed as **6 / 6 exact**. Same class as `A-06`. |
| `I-07` | INFORMATIONAL | CARRIED | The current generation's production-authority `lineage_id` and the Full81 authorization `LINEAGE_ID` are the same string, `MAIN_FULL81_AUTHORIZATION_MECHANISM_R1`. `REJECTED_LINEAGE_IDS` enforces the stated production-authority / authorization separation only for *historical* generations, since the current generation is excluded by the `!= LINEAGE_ID` filter. **No exploit was demonstrated**: the `production_authority_*` fields are still validated against the resolved live lifecycle, not against this constant. |
| `I-08` | INFORMATIONAL | CARRIED | `docs/ai_handoff/CURRENT_STATE.md` is stale — it still describes U-06 R3 as a pending candidate and states that no accepted U-06 lifecycle exists, whereas the predecessor bytes resolve `PRESENT_VALID` / `FROZEN`. Documentation-only, outside this bounded scope, and **recommended for a separate documentation-only refresh**; it is deliberately not touched here. |

#### 5.3.1 `I-04` — MAJOR / CARRIED / promotion-path dependency

The independent audit re-classified the LF/CRLF question recorded under `J-04`
from an inherited note to a **dependency of this candidate's promotion path**.
Facts, as measured:

- there is no `.gitattributes` anywhere in the repository;
- `core.autocrlf=true`;
- tracked files already exist whose HEAD blob is LF while a clean working tree
  is CRLF — `scripts/check_env.py`, `scripts/check_gurobi.py`,
  `scripts/init_project_folders.py`, `src/utils/paths.py` — and `git status`
  reports all four **clean**;
- lifecycle publication proof hashes **live bytes** against the **HEAD blob**
  (`require_published_in_head`);
- a fresh clone under this configuration could therefore **fail closed** with
  `U06_LIFECYCLE_NOT_PUBLISHED`, un-freezing an otherwise lawfully frozen
  production authority;
- the current Candidate-R2 promotion artifacts are LF and publication
  validation succeeds in the present working tree;
- this is inherited from the prior `A-05` / `F-03` / `J-04` record;
- it is **fail-closed, never fail-open**.

Candidate R2 now depends on exact publication containment for **six** promotion
artifacts — the candidate manifest, the four later role records, and the
accepted-lifecycle record — so the dependency is recorded here rather than left
as a general note.

**Not addressed in this pass by instruction.** No `.gitattributes` is added, no
EOL policy is altered, and no implementation byte is modified. **Separate
bounded EOL reproducibility hardening may be performed later if authorized**,
as its own pass with its own independent verification.

#### 5.3.2 `I-05` — MINOR / CARRIED identity-completeness observation

`scripts/20c_build_v7_3_reconstructed_pv_mainline_candidate_r3.py` appears in
the `IMMUTABLE_DEPENDENCIES` tuple of
`scripts/21a_preflight_v7_3_production_routing.py` and is enforced
clean-against-HEAD there, which makes it a gate-protected dependency of a
runtime production dependency. It is nevertheless **absent** from
`ACCEPTED_IMPLEMENTATION_PATHS`, while its three sibling entries in that same
tuple — `src/annual_design_model_v7_2.py`,
`scripts/09_build_valid_outage_start_sets.py` and
`scripts/16a_preflight_layer_a_representative_binary_cases.py` — are all
included.

Recorded disposition:

- this is **inherited from the accepted U-06 R3 identity surface** (20 paths);
  Candidate R2 added only `src/main_full81_authorization_v7_4.py`;
- **no silent exploit was demonstrated**;
- the canonical reconstructed-PV parquet that `20c` produces remains
  **independently hash-pinned** (`ACCEPTED_ANNUAL_SHA256`, re-verified by the
  Full81 authorization validator), so a change to `20c` cannot silently alter a
  production input or result;
- **Candidate R2 does not reopen or repair this inherited identity surface.**

`20c` is deliberately **not** added to the accepted implementation identity in
this pass: that would be an implementation-identity change and requires its own
authorization and independent audit.

---

## 6. No-execution guarantee

| Counter | Value |
|---|---|
| `scripts/21d` invocations | **0** |
| Full81 preflight executions | **0** |
| `optimize()` calls | **0** |
| Annual MILP solves | **0** |
| Main Full81 cases executed | **0** |
| A2 cases executed | **0** |
| Production run directories created | **0** |
| Real lifecycle role / accepted-lifecycle / re-freeze artifacts created | **0** |
| Real Main Full81 authorization artifacts created | **0** |

---

## 7. Required next gate

**Fresh independent verification of this provenance correction.** The fresh
independent read-only audit of Candidate R2 is **complete** (2026-10-03): it
re-attempted every cross-generation substitution against the live validators,
re-derived the T1→T7 promotion control independently, and returned
`CONDITIONAL PASS — REMEDIATION SOUND BUT ACCEPTANCE BLOCKED PENDING SPECIFIED
NON-SCIENTIFIC CORRECTION`, closing `H-01` and `H-02`.

The specified correction is the `J-01` provenance disclosure, applied in §5 of
this revision. Because that correction changed these checkpoint bytes after the
audit read them, acceptance now requires a **fresh independent verification of
the correction itself**, confirming that:

- §5.2 carries the authoritative counts and the counting methods are stated;
- the three previously undisclosed `tests/test_21g` regressions are enumerated
  with their exact live identifiers and their fail-closed disposition;
- the `test_the_guard_is_not_vacuous` attribution is corrected without
  modifying the test;
- `I-04` is recorded as a MAJOR carried promotion-path dependency and `I-05` as
  a carried identity-completeness observation;
- the Candidate-R2 implementation identity is still
  `1644c426f9dceba081cd3cccf0501623ccfbeeaef5b3131b565fbf928615900f`;
- no production code, test, methodology, Framework or Registry byte changed;
- the real repository is still `NOT_ACCEPTED` / `ABSENT` / `NOT_FROZEN` /
  `NOT_GRANTED`, with A2 hard-blocked.

`H-01` and `H-02` are **not** reopened by this pass and must not be re-litigated
by it.

Acceptance, the accepted-lifecycle record, the production-authority re-freeze,
commit/publication, the creation of a real Main Full81 authorization, the
no-solve Full81 production preflight, the separate Full81 execution
authorization, and Main Full81 execution are **each separate acts requiring
their own authorization**. None is conferred by this candidate.
