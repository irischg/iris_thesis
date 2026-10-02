# U-06 V7.4 production-authority alignment — Candidate (no-solve)

**Date:** 2026-10-02
**Candidate identity:** `U_06_V7_4_PRODUCTION_AUTHORITY_ALIGNMENT_CANDIDATE`
**Disposition:** **CANDIDATE / NOT ACCEPTED / NOT CLOSED / NOT YET AUTHORITY**
**Pass type:** additive production-authority / provenance alignment; no solve
**Scientific or numerical execution required:** NO
**Scope:** **bounded `U-06` production-authority V7.4 binding ONLY**

> **This checkpoint is NOT Full81 authorization.** It is not an acceptance act, not an
> independent audit, not a production-authority re-freeze acceptance, and not execution
> authority. Candidate creation is never self-acceptance. The next required gate is a
> **fresh independent audit** of this alignment.

## 1. Current source-of-truth banner

- `FRAMEWORK = V7.4` — `docs/research_framework_v7_4_2026-09-26_r2.md`
- `REGISTRY = V7.4` — `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`
- `PIPELINE = V7.4 CURRENT ACCEPTED ROUTE`
- `TASK_3_PREREGISTRATION_CANDIDATE_R2 = CLOSED / ACCEPTED`
- `TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_CANDIDATE_R2 = CLOSED / ACCEPTED / PUBLISHED`
- `U-01 = OPEN / HOLD`
- `A2 = HARD BLOCKED`
- `MAIN V7.4 FULL81 = NOT YET AUTHORIZED`

Framework v7.4 and Registry v7.4 are **not** modified, reinterpreted, or reopened by this
pass. Older `v7_2` / `v7_3` implementation and data filenames are accepted provenance
naming; they do not downgrade the current route and are **not** renamed.

## 2. Authorizing basis

The accepted and published
`TASK_3_GOVERNANCE_SEQUENCING_SUCCESSOR_CANDIDATE_R2_ACCEPTANCE_CLOSURE` (§9, §10)
records:

- the mandatory remaining lifecycle
  `R2 acceptance -> governance-bundle / production-authority V7.4 alignment / re-freeze
  -> fresh independent verification of that alignment -> separate Main Full81
  authorization / preflight -> Main Full81 execution`;
- verdict `GOVERNANCE_BUNDLE_ALIGNMENT_REQUIRED_AFTER_SUCCESSOR_ACCEPTANCE`;
- that live production authority remained **V7.3-bound**, that Framework V7.4 and
  Registry V7.4 were **not production-gate-bound**, and that `U-06` was the broader
  alignment gap and the **next gate**.

A fresh independent final cross-document alignment audit subsequently returned
`GO_FOR_U06_ALIGNMENT`, with `GO_FOR_FULL81_PREFLIGHT = NO` and `GO_FOR_FULL81 = NO`.
That audit exists as an external/read-only governance result; **no repository audit
artifact path is asserted or invented here.**

This pass implements that bounded alignment and nothing else.

## 3. Pre-implementation repository identity — verified from primary bytes

| Item | Verified value |
|---|---|
| Working tree | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis` |
| Branch | `thesis-v7` |
| Pre-implementation HEAD | `fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0` |
| Local `origin/thesis-v7` | `fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0` |
| Ahead / behind | `0 / 0` |
| Staged paths at entry | `0` |
| Unstaged tracked paths at entry | `0` |
| Protected-surface untracked paths at entry | `0` |
| Pre-existing unrelated untracked user paths | `8` (five porcelain records, one a directory) |

The expected starting HEAD stated in the task matched live Git exactly. Every authority
hash quoted in this checkpoint was recomputed from primary repository bytes in this pass;
none was inherited from a narrative summary.

## 4. U-06 root cause — confirmed from primary bytes

The live pre-execution authority mechanism is
`src/production_input_authority_v7_3.py`, whose module-level `AUTHORITY_FILES` mapping
exact-pins three artifacts:

| Key | Pinned path | Pinned SHA-256 |
|---|---|---|
| `methodology` | `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `evidence` | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| `lifecycle` | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |

`verify_authority_files()` fails closed unless those exact V7.3 bytes are present. That
mapping is reached on **every** production path:

```text
run_layer_a_production / run_eob_production
  -> require_production_authority
    -> inspect_deployment_snapshot
      -> load_accepted_v7_3_annual_input
        -> verify_authority_files          <-- V7.3 ONLY
```

`src/production_successor_stack_v7_3.py::run_successor_stack` then republished exactly
those three V7.3 hashes as `authority_integrity.framework / .registry / .lifecycle`,
alongside four `ADDITIONAL_AUTHORITY_FILES` pins (provenance protocol, the v7.3 input
authority module, the Step-2E-1 preflight, the Step-2E-1 test) and the accepted parquet.

**Confirmed root cause.** The mechanism was scientifically correct and the accepted
implementation was valid, but its *authority binding* was stale in three specific ways:

1. **No V7.4 methodology/evidence binding.** Framework V7.4 and Registry V7.4 — current
   accepted authority — appeared nowhere in the live gate, so no production artifact
   could prove which accepted methodology/evidence it ran under.
2. **No governance binding.** Neither the accepted Task-3 Layer A preregistration
   Candidate R2 chain nor the accepted/published governance-sequencing successor R2 chain
   was hash-bound to the gate.
3. **No alignment-surface or parameter-registry binding.** The model/core source, the
   parameter registry, the successor stack, and the Full81 runner were not exact-hash
   bound in the pre-execution authority record (the core and runner were checked only for
   tracked/clean status, not identity).

This is implementation/provenance authority, **not** scientific methodology. No equation,
parameter, tariff rule, degradation rule, reserve rule, solver setting, or planning-input
identity is implicated.

## 5. Additive design decision — and why

**Chosen architecture: additive successor module plus a bounded binding change in the
mutable successor layer. The historical V7.3 authority module is untouched.**

| Option | Decision | Reason |
|---|---|---|
| Rewrite `src/production_input_authority_v7_3.py` to pin V7.4 | **REJECTED** | Destructive rewrite of accepted immutable historical provenance. It is also hash-pinned at `f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1` inside `ADDITIONAL_AUTHORITY_FILES` and listed in `PROTECTED_METHODOLOGY_PATHS`, so editing it would break the very gate it serves. |
| New V7.4 authority module, V7.3 preserved | **ADOPTED** | Follows the established repository pattern (`production_input_authority_v7_3` -> `production_successor_stack_v7_3`): authority is extended by additive successors, never by in-place version rewrites. |
| Entirely new V7.4 runner replacing `21d` | **REJECTED** | The independent audit found the existing Full81 scientific path valid. A parallel runner would duplicate the grid, case plan, solver contract, and publication logic — exactly the redesign this pass is forbidden to perform — and would create a second production route to keep in sync. |
| Bounded additive binding inside the existing successor stack and `21d` | **ADOPTED** | `src/production_successor_stack_v7_3.py` is the *designed mutable successor layer*: it is not hash-pinned by any authority list, and the accepted Macro Gate 2E-A record already documents post-freeze additive corrections to it (commits `39af835`, `b87575c`, `1651b31`). Binding there is the minimum change that makes **run-level and case-level** artifacts carry the V7.4 identities. |

A separate V7.4 wrapper around the runner was considered and rejected for the reason in
row 3: the runner's scientific content is accepted and the only defect was *which
authority it bound*. Binding is a property of the gate, not of the entrypoint, so the
correct minimum fix is in the gate — leaving `21d`'s own change to six added report lines.

### 5.1 What the V7.3 layer retains

`src/production_input_authority_v7_3.py` is **byte-identical** (`git diff` empty). Its
V7.3 trio is retained inside the new bundle as
`INHERITED_V7_3_HISTORICAL_AUTHORITY`, verified on every bundle check and labelled
`HISTORICAL_ACCEPTED_PREDECESSOR_AUTHORITY_NOT_CURRENT_PRESCRIPTIVE` /
`CLOSED_ACCEPTED_HISTORICAL`. A destructive rewrite of the historical layer therefore
**fails this gate closed** rather than being silently absorbed.

The accepted, frozen eight-key `authority_integrity` surface of
`run_successor_stack()` is likewise left **byte-for-byte unchanged**, still carrying the
inherited V7.3 trio. Current V7.4 authority is bound in a **sibling** key,
`v7_4_authority_alignment`, with `authority_integrity_lineage` naming the relationship.

## 6. Files added

| Path | Bytes | SHA-256 |
|---|---:|---|
| `src/production_authority_bundle_v7_4.py` | `33,587` | `48daa90d29ae499beb3a0d87fcc21e6ed06ac3d7d1bff0a3b900df952037539d` |
| `scripts/21e_preflight_v7_4_production_authority_alignment.py` | `7,800` | `666cceb164581d9ffe78f5b3a9476f7427ff14854fcbb4c0f83ce227b4d2fd72` |
| `tests/test_21e_v7_4_production_authority_bundle.py` | `25,444` | `895f7474a30b54c19807bf28f381ea35256476dc01b12be8414d03a733fa17c7` |
| this checkpoint | — | recorded in the companion manifest |
| `results/provenance/u_06_v7_4_production_authority_alignment_candidate_2026-10-02/alignment_manifest.json` | — | omits its own digest, per repository precedent |

## 7. Files modified

| Path | Bytes after | SHA-256 after | Change |
|---|---:|---|---|
| `src/production_successor_stack_v7_3.py` | `73,645` | `bef5ce7dea61ce82910347747ab8f6d7f5c97d05a7bbbddc05eeeb42d785ff79` | `+54` lines, `-0` |
| `scripts/21d_preflight_v7_3_final81_successor.py` | `4,667` | `f26ce15d83efe761d54b08c70bd30323f7a326f289572167fc6ebec9ca76949a` | `+6` lines, `-0` |

On the **code / production surface**, `git diff --stat` for this pass is exactly
`2 files changed, 60 insertions(+)` — **zero deletions and zero modified existing lines**.
The change is strictly additive at the line level.

Separately, this pass also performs the bounded handoff synchronization required of it:
`docs/ai_handoff/CURRENT_STATE.md` and `docs/ai_handoff/PROJECT_HANDOFF.md` are updated to
state the current accepted governance position. Those are documentation files; they carry
no authority binding, are not hash-pinned by any gate, and their diffs do include replaced
status lines (the previously-recorded `U-06 = UNRESOLVED_IMPLEMENTATION_AUTHORITY_ALIGNMENT`
wording, the pre-successor next-legal-step ordering, and the `U-01`-blocks-Full81 ordering
superseded by the accepted governance-sequencing successor R2). Historical narrative is not
rewritten beyond that synchronization. A whole-pass `git diff --stat` therefore shows four
changed files; only the two above are production-surface changes.

## 8. Exact V7.4 authority bindings

The bundle verifies **28** pins against live bytes. Full per-pin paths and hashes are in
the companion manifest; the required bindings are:

| Role | Path | SHA-256 |
|---|---|---|
| Framework V7.4 | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| Framework V7.4 acceptance closure | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` |
| Framework V7.4 acceptance manifest | `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33` |
| Registry V7.4 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| Registry V7.4 independent audit | `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md` | `bf909363d726ecd2f55ce883a71e6a894e718587bbeb6946d879758f246c12ce` |
| Registry V7.4 acceptance closure | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` |
| Registry V7.4 acceptance manifest | `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | `53074cfe44c0276d6f319497cbe6f5aaf07b255ac0c335f9481174dd968063fe` |
| Task-3 preregistration Candidate R2 | `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_2026-09-27.md` | `7957fbaf2566da612db1770fbbc8a08be18a6c7aaec4f4564b20fb4e5bad4ab4` |
| Task-3 machine record | `results/provenance/layer_a_robustness_preregistration_candidate_r2/preregistration_record.json` | `14c2f0a2a1bd0cbc5ac022f14abcd24af8325976694ef4a6b3a133ade46d0b6f` |
| Task-3 acceptance closure | `docs/checkpoints/layer_a_robustness_preregistration_candidate_r2_acceptance_closure_2026-09-27.md` | `d26ad46a08087d41831a8168d789294dcc635008ffb0f3aceb443121b5379b02` |
| Task-3 acceptance manifest | `results/provenance/layer_a_robustness_preregistration_candidate_r2_acceptance_closure_2026-09-27/acceptance_manifest.json` | `08a1e5b5929b5791e14b2ae887c4b9592dccbd803c7e0981c581f41561aa268d` |
| Governance successor Candidate R2 | `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_2026-10-01.md` | `db20ea059c48b99bb5c57801dff5654b4b8e1b94ce51ce4ded6e82eec4ac922e` |
| Governance successor acceptance closure | `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01.md` | `9f1af8e805b23f6e16c827ada645bfff7d920d98a24b70fb2ea448683ec78851` |
| Governance successor acceptance manifest | `results/provenance/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_r2_acceptance_closure_2026-10-01/acceptance_manifest.json` | `4bbd58b8e8bd92c292d44b7b3d8b6a2035c3d41dc894581697f52583a55b6476` |
| Governance successor original candidate (immutable, not accepted) | `docs/checkpoints/layer_a_robustness_preregistration_governance_sequencing_successor_candidate_2026-10-01.md` | `f2bc1f5909ce4281d05465dba07541507194974d841df704fbf5a471f8b92d82` |
| Canonical planning input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| Model / core | `src/annual_design_model_v7_2.py` | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Parameter registry | `data/reference/parameter_registry_v7_2.csv` | `c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1` |
| Production successor stack | `src/production_successor_stack_v7_3.py` | `bef5ce7dea61ce82910347747ab8f6d7f5c97d05a7bbbddc05eeeb42d785ff79` |
| Full81 runner | `scripts/21d_preflight_v7_3_final81_successor.py` | `f26ce15d83efe761d54b08c70bd30323f7a326f289572167fc6ebec9ca76949a` |
| V7.4 alignment verifier | `scripts/21e_preflight_v7_4_production_authority_alignment.py` | `666cceb164581d9ffe78f5b3a9476f7427ff14854fcbb4c0f83ce227b4d2fd72` |
| V7.4 alignment static test | `tests/test_21e_v7_4_production_authority_bundle.py` | `895f7474a30b54c19807bf28f381ea35256476dc01b12be8414d03a733fa17c7` |
| Inherited V7.3 input authority (unmodified) | `src/production_input_authority_v7_3.py` | `f6d5093f94b767882c23544e2d0390aea2f939e5755f8950fc3c53d9878a8ed1` |
| Inherited Step-2E-1 routing preflight | `scripts/21a_preflight_v7_3_production_routing.py` | `3d99a4200dce93cd00db94727f72489d9be497eb52c74270a1c49b17fc8a7e95` |
| Provenance protocol | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
| Inherited V7.3 methodology (historical) | `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| Inherited V7.3 evidence (historical) | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| Inherited V7.3 lifecycle (historical) | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |

Additional non-hash identities bound: core version
`v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10`;
Registry V7.4 acceptance commit `9050d0eabd0ee5c41626ba924c31a67f301c7293`; governance
successor published commit `fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0`; Step-2E-1 accepted
commit `d52d9584b22da2a41b51c8ce3e99a0335e39da2b`.

**Deliberately not bound.** No unrelated authority was added for completeness. The
accepted V7.4 Results & Managerial-Insight Analysis Plan Candidate R2 is interpretation
discipline for *already-produced* results, not pre-execution production authority, and its
closure is not yet published to `origin/thesis-v7`; binding it in a production gate would
make the gate depend on an unpublished artifact. The v7.3->v7.4 transition closure,
Step 2D acceptance records, and historical v7.2 runner artifacts are lineage provenance,
already covered transitively by the accepted chains above.

### 8.1 Hash-basis observation for the independent audit

Every pin is over **working-tree bytes**. The pinned source files are LF-terminated on
disk, which is the form under which the already-accepted pin for
`src/production_input_authority_v7_3.py` verifies. This repository has
`core.autocrlf = true` and no `.gitattributes`, so a fresh Windows checkout would rewrite
text files to CRLF and change these digests. That is a **pre-existing repository-wide
property** that applies identically to the already-accepted `production_input_authority_v7_3`,
`step2e1_preflight`, and `step2e1_test` pins; it is **not** introduced by this alignment,
and this pass deliberately does not add `.gitattributes` or renormalize anything, which
would be an unrelated change. It is recorded here as an observation, not a claim of
defect, for the independent audit to classify.

## 9. Runner / provenance alignment

Future production artifacts can now prove their applicable identities directly:

| Surface | Field added | Content |
|---|---|---|
| Run-level `authority.json` | `v7_4_production_authority` | full declared V7.4 record: Framework, Registry, Task-3 chain, governance successor chain (with published commit), canonical input contract, parameter registry, model/core + core version, successor stack, Full81 runner, alignment verifier, inherited V7.3 pins, output namespace, governance state, Full81-authorization state |
| Run-level `authority.json` | `solver_settings_contract`, `alpha_grid`, `beta_grid_h`, `expected_full_surface_cases`, `stack_version`, `core_module`, `core_version` | the accepted settings/grid as declared constants — values unchanged |
| Case-level `case_definition.json` | `v7_4_authority` | compact per-case record: bundle version, alignment status, Framework, Registry, parameter registry, Task-3 acceptance closure, governance successor closure, canonical input, model/core, stack, runner, `main_full81_authorization`, `a2_status`, `u_01_status` |
| Authority / preflight report (`21d`) | `v7_4_authority_bundle_version`, `v7_4_authority_alignment` | the full verified bundle record |

Run identity (`<unique-run-id>`), case coordinate (`alpha`, `beta_h`, `case_id`), solver
settings, and the existing checkpoint/authority identities were already emitted and are
unchanged. **No scientific output field was added.** No case was run to populate any of
this; every field above is declared or hash-derived.

## 10. Governance semantics encoded

```text
U-01                              = OPEN / HOLD
U-01 blocks Main Full81           = NO
U-01 must be frozen before        = [A2_EXECUTION, A2_RESULT_EXPOSURE,
                                     A2_INTERPRETATION,
                                     A2_CONDITIONAL_EXTENSION_AUTHORIZATION]
                                    (FULL81_AUTHORIZATION deliberately absent)
A2                                = HARD_BLOCKED
A2 result exposure                = ZERO_A2_RESULT_EXPOSURE_FIREWALL_INTACT
MAIN_FULL81_AUTHORIZATION         = NOT_AUTHORIZED
PRODUCTION_AUTHORITY_ALIGNMENT    = V7_4_ALIGNED
alignment implies authorization   = FALSE
```

Two **fail-closed guards** make this mechanical rather than declarative, and both run
*before* every repository check so that no amount of clean repository state can be read as
authorization:

- `require_full81_scope_authorization("full81")` raises
  `FULL81_AUTHORIZATION_NOT_GRANTED` unconditionally, because
  `MAIN_FULL81_AUTHORIZATION_ARTIFACT is None`. A future separate authorization gate is
  the only thing that can populate it.
- `require_a2_hard_block(scope)` raises `A2_HARD_BLOCKED` for every A2 / variable-floor /
  robustness / perfect-information scope token.

Verified live against a synthetically clean deployment snapshot: `full81` ->
`FULL81_AUTHORIZATION_NOT_GRANTED`; `a2_variable_floor` -> `A2_HARD_BLOCKED`;
`core-three` -> `PRODUCTION_AUTHORITY_FROZEN` (unchanged accepted behavior). The six
accepted non-Full81 scopes (`eob`, `low`, `central`, `high`, `core-three`,
`historical-five`) are **not** newly restricted.

This alignment authorizes **none** of: A2 execution, A2 result exposure, A2
paired-difference exposure, A2 interpretation, conditional beta=8 escalation, Main Full81
authorization, Main Full81 preflight, or Main Full81 execution.

## 11. U-07 — unresolved, unchanged

```text
U-07 = UNRESOLVED_CLASSIFICATION
scope = A2_ONLY
blocks Main Full81 = NO
```

No variable-floor support is implemented. The annual model does **not** accept
time-varying reserve floors and its equations were not touched. U-07 is **not** resolved,
reclassified, or silently closed.

## 12. Cross-case aggregation — recorded as a later requirement

`GAP_RECORDED_NOT_DESIGNED_NOT_IMPLEMENTED_NOT_AUTHORIZED`. It is **not** implemented in
this pass and is **not** a prerequisite for executing Full81. It is required before
substantive response-surface interpretation or meeting analysis. A future implementer must
not add a materiality-classification column, which would depend on the unresolved `U-01`.

## 13. No-solve / non-mutation declaration

| Item | Count / state |
|---|---:|
| Model constructions | `0` |
| `optimize()` calls | `0` |
| Solver executions / MILP solves | `0` |
| Full81 runs | `0` |
| Full81 authorizations | `0` |
| Full81 preflight authorizations | `0` |
| Full81 results in existence from this pass | `0` |
| A2 / robustness runs | `0` |
| A2 result exposures | `0` |
| Production run directories created | `0` |
| Production gates run in authorizing mode | `0` |
| U-items resolved | `0` |
| Thresholds selected | `0` |
| Framework files modified | `0` |
| Registry files modified | `0` |
| Canonical input bytes changed | `0` |
| Scientific methodology changes | `0` |
| Solver-setting changes | `0` |
| Historical V7.3 authority files modified | `0` |
| Historical production result artifacts modified | `0` |
| Output namespaces renamed | `0` |
| Cross-case aggregation layers added | `0` |
| Commits | `0` |
| Pushes | `0` |
| Tags created or moved | `0` |
| Paths staged | `0` |

Explicitly:

- **no solve occurred**;
- **no Full81 authorization occurred**;
- **no Full81 result exists** from this pass;
- **no A2 execution occurred**;
- `U-01` remains **OPEN / HOLD**;
- `A2` remains **HARD BLOCKED**;
- the **scientific implementation is unchanged**;
- the **canonical input is unchanged**;
- **solver settings are unchanged**;
- **V7.3 production authority is preserved as historical provenance**;
- the **V7.4 authority successor is additive**;
- **next required gate = fresh independent audit**.

## 14. Scientific non-mutation — verified

`git diff` is empty for every one of: Framework V7.4, Registry V7.4,
`src/annual_design_model_v7_2.py`, `src/production_input_authority_v7_3.py`,
`scripts/21a_preflight_v7_3_production_routing.py`,
`scripts/15d_run_corrected_eob_v7_2.py`,
`scripts/16a_preflight_layer_a_representative_binary_cases.py`,
`scripts/19a_preflight_final_layer_a_81_cases.py`,
`scripts/19b_run_final_layer_a_81_cases.py`, all of `data/`, all of `results/`, and all of
`docs/checkpoints/` apart from this new candidate.

Verified unchanged by static assertion: alpha grid `(0.60 … 1.00)` with `9` values; beta
grid `(4 … 12)` with `9` values; `EXPECTED_CASES = 81`; the Final81 case plan is exactly
the `9 x 9` coordinate set with `81` unique IDs; `eta_d = 0.90`; Layer-A `MIPGap = 1e-6`,
`NumericFocus = 1`, `MIPFocus = 0`, `Threads = 0`, `OutputFlag = 0`,
`TimeLimit = INFINITY_UNSET`; EOB `MIPGap = 1e-6`; `surplus_pv_recharge = False` on every
case; `PRODUCTION_CASE_SETS` membership unchanged (no robustness scope added); production
root `results/layer_a/final_81_v7_3/runs`; the eight mandatory Layer-A audits and seven
mandatory EOB audits unchanged; exclusive run-directory creation unchanged.

## 15. Static / build-only validation performed

| Validation | Result |
|---|---|
| `py_compile` of all five added/modified Python files | PASS |
| Import of the new bundle and the modified stack | PASS |
| `scripts/21e …alignment.py` (no-solve verifier) | exit `0`, `status = PASS`, `28 / 28` pins reproduce from live bytes |
| `scripts/21d …final81_successor.py` default preflight (no-solve) | exit `0`, `status = PASS`, `81` cases planned, `0` solves, Full81 `NOT_AUTHORIZED` |
| `tests/test_21e_v7_4_production_authority_bundle.py` | `34 / 34` PASS |
| `tests/test_21b_21d_v7_3_production_successor_stack.py` (accepted, frozen) | `66 / 66` PASS |
| `tests/test_21a_v7_3_production_routing_preflight.py` (accepted, frozen) | `19 / 19` PASS |
| Live `inspect_deployment_snapshot` (read-only) | `authority_hashes_valid = True`; V7.4 bundle verified inside the gate |
| Worktree non-mutation during verification | before == after |
| Production run directories after all validation | exactly the two pre-existing accepted runs |

No test that can reach `optimize()` was run in an executing configuration. The accepted
`test_21b_21d` module structurally replaces every real Gurobi entry point at module setup
before any assertion, and all three suites report zero model constructions and zero
optimization calls. The new test module never writes the production execution flag as a
literal and spawns no subprocess.

## 16. Live production-gate state after this pass

```text
branch                   = thesis-v7
head                     = fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0
origin/thesis-v7         = fbdd5f0c056f6df8e97c5ef27a8d0c5e6942e0f0
authority_hashes_valid   = True        <-- V7.4 bundle verifies inside the live gate
successor_bytes_committed = False
tracked_unstaged_changes = True
authority_untracked_paths = ['scripts/21e_preflight_v7_4_production_authority_alignment.py',
                             'src/production_authority_bundle_v7_4.py',
                             'tests/test_21e_v7_4_production_authority_bundle.py']
core-three scope         -> PRODUCTION_AUTHORITY_NOT_YET_FROZEN
                            ("Current v7.3 successor bytes are not committed in HEAD.")
full81 scope             -> FULL81_AUTHORIZATION_NOT_GRANTED
a2 scope                 -> A2_HARD_BLOCKED
```

**This is correct and expected, not a defect.** The alignment candidate's bytes are
uncommitted, so the gate's own repository-authority check reports
`PRODUCTION_AUTHORITY_NOT_YET_FROZEN`. The three untracked paths are this candidate's own
new files and are reported by the gate exactly as designed. **No guard was bypassed,
weakened, or edited around, and no manifest was hand-patched.** Production authority can
only become frozen after this candidate is independently audited, accepted, and committed
by separately authorized acts.

## 17. Explicit non-authorization boundaries

| Boundary | State |
|---|---|
| Is this an acceptance / closure | **NO** — candidate only |
| Is this an independent audit | **NO** |
| Is this a production-authority re-freeze acceptance | **NO** — it is the alignment candidate the re-freeze requires |
| Authorizes Main V7.4 Full81 | **NO** |
| Authorizes Full81 preflight | **NO** |
| Authorizes Full81 execution | **NO** |
| Authorizes A2 under any condition | **NO** |
| Authorizes A2 result exposure / paired difference / interpretation | **NO** |
| Authorizes conditional beta=8 extension | **NO** |
| Resolves `U-01` or selects any threshold | **NO** — `U-01` remains **OPEN / HOLD** |
| Resolves `U-02`–`U-05` | **NO** |
| Resolves `U-07` | **NO** |
| Implements cross-case aggregation | **NO** |
| Implements variable-floor / robustness support | **NO** |
| Modifies Framework, Registry, canonical input, or historical V7.3 authority | **NO** |
| Creates an exposure-log entry | **NO** |
| Creates or moves a tag | **NO** |
| Commits or pushes | **NO** |

Production-authority alignment is **not** execution authorization.

## 18. Dependency state after this pass

| Item | State |
|---|---|
| `U-01` | **OPEN / HOLD** — must be resolved, independently audited, accepted, and frozen before any A2 event; does not block Main Full81 |
| `U-02` – `U-05` | `UNRESOLVED` |
| `U-06` | `V7_4_ALIGNMENT_CANDIDATE_PENDING_FRESH_INDEPENDENT_AUDIT` |
| `U-07` | `UNRESOLVED_CLASSIFICATION` / `A2-ONLY` / not a Main Full81 blocker |
| Materiality threshold | `THRESHOLD_DECISION_REQUIRED_BEFORE_A2`; accepted value `null` |
| Production-authority alignment | **candidate created**; not accepted |
| Production-authority re-freeze | required `YES`; accepted `NO` |
| Production gate | `NOT_RUN` in authorizing mode |
| Robustness implementation | `NOT_AUTHORIZED` |
| Current-route Main Full81 | `NOT_YET_AUTHORIZED` / `NOT_YET_EXECUTED` |
| A2 robustness execution | `HARD_BLOCKED` |
| Aggregation / reporting layer | `GAP_RECORDED_NOT_DESIGNED_NOT_AUTHORIZED` |

The `U-06` / `U-07` representation discrepancy previously recorded in the repository is
addressed for `U-06` only to the extent of creating this alignment candidate; `U-07` is
left exactly as recorded.

## 19. Final disposition

**Lifecycle status:** `CANDIDATE / NOT ACCEPTED / NOT CLOSED / NOT YET AUTHORITY`

> **U-06 V7.4 PRODUCTION-AUTHORITY ALIGNMENT CANDIDATE CREATED — READY FOR FRESH
> INDEPENDENT AUDIT**

`PRODUCTION AUTHORITY = V7.4-ALIGNED` (candidate, pending independent verification).
`MAIN FULL81 = STILL REQUIRES SEPARATE AUTHORIZATION.` `A2 = HARD BLOCKED.`
`U-01 = OPEN / HOLD.` `U-07 = UNRESOLVED_CLASSIFICATION.`

**Next required gate:** a fresh, independent, read-only audit of this alignment candidate.
Acceptance, the production-authority re-freeze, commit/publication, and any Main Full81
authorization or preflight are separate acts, each requiring its own authorization, and
none is conferred here.
