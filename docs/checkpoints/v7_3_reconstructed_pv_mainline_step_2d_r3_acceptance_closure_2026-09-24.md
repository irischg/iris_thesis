# Step 2D Candidate R3 — Acceptance Closure Checkpoint (post-2D-A governance record)

**Record identity:** `V7_3_RECONSTRUCTED_PV_MAINLINE_STEP_2D_R3_ACCEPTANCE_CLOSURE_2026_09_24`  
**Record status:** `GOVERNANCE_CLOSURE_CANDIDATE_PASS_PENDING_INDEPENDENT_AUDIT`  
**Record date:** 2026-09-24  
**Machine-readable companion:** `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.json`  
**Companion SHA-256:** `ff870de5af30c54d1ad5d83fb7b3fb6837e3d00d797a396d3b12aae751d9cb3d` (23,618 bytes)

> **This record is itself a CANDIDATE.** Its status above applies to this governance
> closure record only. It does **not** downgrade Step 2D Candidate R3, which remains
> `CLOSED / ACCEPTED`. This record must receive its own independent read-only audit
> before any commit/push/tag freeze.

## A. Purpose

This is an **additive governance record** created **after** an independent Step 2D-A
audit returned PASS on Step 2D Candidate R3. Its purpose is to make that already-completed
acceptance durable and machine-readable in the repository's governance metadata.

It does **not**:

- replace, mutate, rename, or re-hash any candidate artifact;
- perform, re-perform, alter, weaken, or expand the Step 2D-A audit;
- reopen any CLOSED scientific decision;
- authorize production routing, optimization, or Step 2E;
- commit, push, or tag.

The independent Step 2D-A audit was performed separately and beforehand by an independent
read-only auditor. **This closure implementation did not perform that audit.**

Only three repository paths were touched by this pass:

- **ADD** `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.md`
- **ADD** `docs/checkpoints/v7_3_reconstructed_pv_mainline_step_2d_r3_acceptance_closure_2026-09-24.json`
- **MODIFY** `docs/ai_handoff/CURRENT_STATE.md`

No file was added inside the R3 candidate evidence namespace, which remains byte-identical.

## B. Current authority

| Role | Path | SHA-256 |
| --- | --- | --- |
| Methodology — Framework v7.3 | `docs/research_framework_v7_3_2026-09-23.md` | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| Evidence — Registry v7.3 R3 | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| Lifecycle closure — v7.3 authority freeze | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
| Procedural governance — Protocol v1 | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |

- Research lineage branch: `thesis-v7`
- CLOSED decision reopened: **false**
- Methodology changed: **false**

**Revision-family disambiguation.** Registry v7.3 R3 is the current EVIDENCE authority revision. Step 2D Candidate R3 is the reconstructed-PV DATA-ARTIFACT candidate revision accepted here. These are different revision families and must not be conflated.

## C. Step 2D lineage

### Step 2D Candidate R1 — `STOP / FAILED IMMUTABLE PROVENANCE`

- **Rejected for a demonstrated numerical data defect:** **false**
- **Verified defect class:** evidence / provenance / lifecycle packaging: noncompliant manifest and lifecycle contract, and historical evidence-filename contract defects.
- **Immutability:** R1 remains immutable historical provenance; no R1 byte was modified.

> Historical disposition recorded post hoc in the Step 2D R3 acceptance closure based on the preserved R1 bytes and the previously established STOP decision. This record is NOT an original contemporaneous R1 audit and does not claim to be one.

**Defect class re-confirmed from preserved R1 bytes during this closure pass:**

- R1's adjacent manifest uses '.manifest.json'; the accepted R3 contract uses '_manifest.json'.
- No epistemic_boundary statement exists anywhere in R1's adjacent manifest or completion manifest.
- R1's evidence namespace carries all three defective filenames (diff_vs_historical_canonical.csv, diff_vs_promotion_source.csv, evidence_package_manifest.json) that the accepted R3 builder hard-codes as forbidden.
- R1's completion manifest registers only three evidence files and omits both the package manifest and itself.
- R1's adjacent manifest exposes 22 top-level keys and does not satisfy the accepted R3 18-key contract; 13 required keys are absent, including candidate_identity, all_build_gates_pass, target_mask, numerical_inheritance, provenance_transformation, mutation_audit and outputs.

**On R1/R3 parquet byte-identity.** R1's parquet is byte-identical to the accepted R3 parquet (SHA-256 3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428). The independent Step 2D-A audit established R3's data correctness directly from the two accepted source authorities, and established statically that the R3 builder never reads the R1 parquet as construction input (it is hashed as an immutability control only). The identity is therefore a reproducibility observation and corroborates that R1's failure was not a numerical data defect.

Preserved R1 artifacts (unchanged):

| Path | SHA-256 | Bytes |
| --- | --- | --- |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.manifest.json` | `bf63eeaa0e52559cd342465989980d8a693b3f0abf8c6f7876dd2271c2d715cc` | 30,551 |
| `scripts/20a_build_v7_3_reconstructed_pv_mainline_candidate_r1.py` | `dfb2f586efcc22b23ffad2a3768311143518acf5e1f2f3bc0049c29480b18f80` | 45,595 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/completion_manifest.json` | `0f743a834fc94fb8c5553d12c2fbd891cf6a95eb26888f9f7390acce91a58c99` | 3,034 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_historical_canonical.csv` | `b3ee8b362ec441f2e83d7d22f0820abd0570f38bd965b05273ac838e6da7121e` | 11,255 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/diff_vs_promotion_source.csv` | `2194ca2bd7812830c7b2c9910fa8c16d155a8f5b34bede1a938b00fb1dfdf2eb` | 15,974 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/evidence_package_manifest.json` | `4e3fcaf2bcea03dfcd831d2082af965b6477f10ab06fa348c205b6498a0d115d` | 1,367 |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r1_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` | 554,037 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r1/run_manifest.json` | `447fe701cf9ec9cddd1b08630288781c0482794606799ed9ebcd6b5baa596c25` | 51,918 |

### Step 2D Candidate R2 — `STOP / ABANDONED IMMUTABLE PROVENANCE`

- **Surviving artifact:** R2 builder only.
- **R2 candidate parquet published:** false
- **R2 evidence namespace published:** false
- **Abandonment reason:** Abandoned after an R2 path collision and static discovery of inherited filename-contract defects.
- **Immutability:** Not executed, not modified.

| Path | SHA-256 | Bytes |
| --- | --- | --- |
| `scripts/20b_build_v7_3_reconstructed_pv_mainline_candidate_r2.py` | `6f30660c5de9442aafccb8085fd26d994a1438b816a7ca9e4797fc23e572e3b9` | 47,729 |

### Step 2D Candidate R3 — `CLOSED / ACCEPTED`

- **Independent Step 2D-A verdict:** `STEP_2D_CANDIDATE_R3_2D_A — PASS`
- **Accepted exact canonical DATA ARTIFACT SHA-256:** `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`
- **Acceptance scope:** v7.3 reconstructed-PV mainline canonical DATA ARTIFACT only; does NOT authorize production routing or optimization.

## D. Accepted R3 subject

Candidate identity: `V7_3_RECONSTRUCTED_PV_MAINLINE_CANDIDATE_R3`

All subject hashes below were re-verified against live repository bytes at closure time.

| Path | SHA-256 | Bytes |
| --- | --- | --- |
| `scripts/20c_build_v7_3_reconstructed_pv_mainline_candidate_r3.py` | `e7af06409afd735e6556ee4cad64a2a1bd8cb26a772d0fe9c51b6d2727aff1ad` | 82,803 |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` | 554,037 |
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23_manifest.json` | `f0e63614010d3a7450b5041409943fd94749d7b1af88ac4fd1c2b07701af9326` | 49,620 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/completion_manifest.json` | `811ed297b67aeec15ea7b0839f2a35272887f15766768f6d4af3835b4ca0a281` | 15,582 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/historical_canonical_to_candidate_column_diff.csv` | `18b926b65151c2b28ccc1a1f169d7fad1ef2286a2edfb6f37d9c86e0fbc4f96a` | 12,807 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/package_manifest.json` | `454a6136fa81d55153d8f58e4252034b9c1d2cec604cb12e00582b394200cf14` | 2,471 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/promotion_source_to_candidate_column_diff.csv` | `1a828db1cef3c1f1131883aeadc2299071db144a682327844de8f5477eb179ec` | 17,364 |
| `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3/run_manifest.json` | `06f4a873770abc7b3488ba7d1d904a8824be583d4bb1898ae7fde4b7dcfdee27` | 50,439 |

Evidence namespace: `results/provenance/v7_3_reconstructed_pv_mainline_candidate_r3`

Source authorities from which the accepted artifact was constructed and independently
re-derived during the Step 2D-A audit:

| Role | Path | SHA-256 |
| --- | --- | --- |
| Historical zero-winter canonical | `data/processed/annual_input_v7_1.parquet` | `9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e` |
| Corrected Sep-18 promotion source | `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet` | `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9` |

## E. Independent acceptance result

```
STEP_2D_CANDIDATE_R3_2D_A — PASS

STEP 2D CANDIDATE R3 — CLOSED / ACCEPTED
```

- **Accepted candidate:** `V7_3_RECONSTRUCTED_PV_MAINLINE_CANDIDATE_R3`
- **Accepted parquet SHA-256:** `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`
- **Performed by:** an independent read-only Step 2D-A auditor, prior to and separate from this closure record.
- **Performed by this closure record:** **false**
- **Audit scope:** implementation, data-artifact identity, provenance and evidence contract; it did not reopen the CLOSED Framework v7.3 decision that full reconstructed annual PV is the v7.3 best-estimate planning mainline.

This checkpoint records that result. It does not claim to have produced it.

## F. Acceptance scope

- **Accepted canonical artifact:** v7.3 reconstructed-PV mainline canonical DATA ARTIFACT
- **Accepted parquet path:** `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`
- **Accepted parquet SHA-256:** `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`
- **Authorizes production routing:** **false**
- **Authorizes optimization:** **false**

**Acceptance applies ONLY to these exact audited bytes.**

## G. Epistemic boundary

> Reconstructed long-unavailable PV values are model-based/weather-informed planning estimates and are NOT observed truth, NOT ground truth, and NOT exact historical recovery.

This boundary is preserved verbatim in the accepted R3 adjacent manifest, run manifest,
and completion manifest, and must not be weakened by any downstream record, summary, or
thesis text that cites this artifact.

## H. 83 / 86 gate persistence disposition

**Final disposition: NON-BLOCKING EVIDENCE-ROSTER PERSISTENCE LIMITATION**

- Gates executed: **86**
- Gates persisted in `completion_manifest.json`: **83**
- Reconstructible from primary bytes: **true**

| Gate | Check | Result | Reconstructible from primary bytes |
| --- | --- | --- | --- |
| `gate_77_no_self_classification_wording_tail` | tail wording scan | **PASS** | true |
| `gate_78_no_forbidden_filenames_tail` | tail filename scan | **PASS** | true |
| `gate_79_package_registers_all_but_itself` | package-registry completeness | **PASS** | true |

**Root cause.** The builder snapshots its gate roster into the completion manifest before gates 77-79 execute, because those three gates validate the staged completion and package manifests themselves. A manifest cannot record the result of a check performed on its own finished bytes; this is the same structural self-reference as the package manifest's omitted self-hash.

**Why this is non-blocking.** All three predicates are deterministic functions of bytes that survive on disk. The independent Step 2D-A audit reconstructed all three from published primary bytes alone, without executing the builder, and all three passed. No acceptance-critical fact depends solely on ephemeral stdout.

**Reopening rule.** Do not reopen the 83/86 difference as an unresolved R3 blocker unless new primary evidence contradicts this accepted audit finding.

## I. Current non-authorizations

| Item | Status |
| --- | --- |
| Production routing | `NOT_YET_AUTHORIZED` |
| Step 2E | `NOT_YET_AUTHORIZED` |
| EOB solve | `NOT_AUTHORIZED` |
| Layer A solve | `NOT_AUTHORIZED` |
| Layer B solve | `NOT_AUTHORIZED` |
| Final81 | `NOT_AUTHORIZED` |
| Commit / push / tag freeze | `NOT_AUTHORIZED` |

## J. Durability status

**Scientific acceptance and Git durability are different things and must not be conflated.**

| Dimension | Status |
| --- | --- |
| R3 scientific / data-artifact acceptance | `CLOSED / ACCEPTED` |
| R3 Git commit freeze | `NOT_YET_COMPLETED` |
| R3 remote durability | `NOT_YET_VERIFIED` |
| R3 gitignored runtime bytes present in working tree | `true` |
| Commit identity | `NOT_YET_AUTHORIZED` |
| Tag identity | `NOT_YET_AUTHORIZED` |

The R3 data/evidence package is currently present in the **live working tree only**. Its
paths fall under the gitignore rules `data/`, `results/`, so the accepted bytes are **not** tracked by Git and have **not** been commit/tag frozen.

> **A SHA-256 recorded in this checkpoint attests to the bytes observed in the live working tree at closure time. It does NOT by itself make those gitignored bytes Git-durable, and does not guarantee they are recoverable from any commit or remote.**

Accordingly this checkpoint distinguishes:

- **scientific / data-artifact acceptance = `CLOSED / ACCEPTED`**, from
- **Git durability freeze = `NOT_YET_COMPLETED`**.

## K. Next governance action

**INDEPENDENT READ-ONLY AUDIT OF THIS POST-2D-A GOVERNANCE CLOSURE**

After an independent PASS on this closure record, commit/push/tag freeze of the accepted R3 bytes and of these closure records may be separately authorized.

- Step 2E authorized by this checkpoint: **false**

**This checkpoint does not authorize Step 2E.**

## Explicit non-claims

- This record did NOT perform the Step 2D-A audit; that audit was completed independently beforehand.
- This record does NOT self-accept: it is a governance-closure CANDIDATE pending its own independent read-only audit.
- This record does NOT downgrade Step 2D Candidate R3, which remains CLOSED / ACCEPTED.
- This record does NOT authorize Step 2E, production routing, or any optimization solve.
- This record does NOT constitute a Git durability freeze, and does not commit, push, or tag.
- This record does NOT claim to be an original contemporaneous Step 2D Candidate R1 audit.
- This record does NOT modify any R1, R2, or R3 byte.

## Repository state at closure construction

- Branch: `thesis-v7`
- HEAD: `23bdadaa87bd4fbb1ce849a0c774e9394a4e2270`
- `origin/thesis-v7`: `23bdadaa87bd4fbb1ce849a0c774e9394a4e2270`
- Staged paths: 0
- Unstaged tracked modifications: 0
- Porcelain raw bytes: 597 (SHA-256 `702156318e65380d03be8a78020891dacbfd63c42e5871bd597c2fde698ece3c`)

> R1/R2/R3 data and evidence artifacts live under gitignored data/ and results/ trees and therefore never appear in git status; they are tracked here by explicit path hashing.

**No-solve / no-routing assertions for this closure pass:** `commits = 0`, `economic_evaluations = 0`, `model_constructions = 0`, `optimization_calls = 0`, `production_routing_changes = 0`, `pushes = 0`, `tags = 0`.

Immutability controls recorded: **28** files hashed at `before_governance_closure_edits`; all listed members must be byte-identical before and after this closure pass.

