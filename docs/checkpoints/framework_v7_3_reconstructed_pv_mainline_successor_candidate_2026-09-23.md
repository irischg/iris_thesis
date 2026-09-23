# Framework v7.3 reconstructed-PV mainline successor — candidate checkpoint

**Date:** 2026-09-23  
**Disposition:** **FRAMEWORK V7.3 RECONSTRUCTED-PV MAINLINE SUCCESSOR — CANDIDATE PASS**  
**Acceptance boundary:** candidate only; this checkpoint does not accept or canonize the framework, Registry, annual input, routing, or production results. Independent audit is required.

## 1. Scope and protocol

This was a document/methodology-only additive implementation under `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` (SHA-256 `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696`).

Authorized mutations were limited to:

1. creating the full integrated successor `docs/research_framework_v7_3_2026-09-23.md`;
2. creating this additive candidate checkpoint.

No source code, tests, Registry, canonical input, routing, production results, historical checkpoint, or accepted artifact was edited. No `optimize()` call, model solve, canonical-input regeneration, production rerun, commit, push, or tag occurred.

## 2. Predecessor and candidate identity

| Artifact | Role | SHA-256 |
|---|---|---|
| `docs/research_framework_v7_2_2026-08-24.md` | immutable accepted predecessor | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |
| `docs/research_framework_v7_3_2026-09-23.md` | additive successor candidate | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
| `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` | accepted Registry predecessor; unchanged | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |

Registry v7.3 is `NOT_YET_CREATED / NOT_YET_ACCEPTED`. The v7.3 candidate is not self-accepting; v7.2 remains authoritative until independent acceptance.

## 3. Exact superseded decision

The only superseded methodology role is:

```text
v7.2: zero-winter PV = mainline;
      reconstructed winter PV = sensitivity only.

v7.3 candidate: separately validated, weather-informed reconstructed full-year PV
                = best-estimate planning mainline;
                prior zero-winter PV = conservative stress/sensitivity.
```

The reconstructed 1,463-hour winter block is model-based and not observed data, exact ground truth, or exact recovery. The same future canonical reconstructed-mainline series must feed EOB/economic optimization, Layer A residual load, `R(alpha,beta)`, `P_out(alpha)`, binding classification, analytical-consistency outage replay, and baseline Layer B. A hybrid economics-credit/outage-no-credit route is prohibited.

## 4. Promotion-source evidence and canonical boundary

| Artifact | Preserved role | SHA-256 |
|---|---|---|
| `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_protocol_2026-09-07.parquet` | immutable September-07 sensitivity-only historical artifact; not promotion source | `023cba88416b965c7dedf4139e9a495602039117ecc827e52a372f10a1aad986` |
| `results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/final_validation_decision.json` | Step 17a `PASS_FOR_SENSITIVITY` evidence | `454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594` |
| `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet` | corrected promotion-source candidate; not canonical | `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9` |
| corresponding corrected 17b manifest | sensitivity-only provenance retained | `e6808ca6270afd808e930a4baa8032852d88bf92c232bb53e68f434fdfba1381` |
| `results/sensitivity/winter_pv_17c/20260918T155044175327Z_3d71b70173/completion_manifest.json` | corrected Step 17c paired-run evidence | `484af5b205fd9ac2cdc047da5f42929f308de3f1f1719f24eeaceb8299ea81ee` |
| `results/sensitivity/winter_pv_17c/20260918T155044175327Z_3d71b70173/paired_sensitivity_comparison.json` | paired reconstructed-vs-zero comparison evidence | `b8acd3027c3c1db31bd8840cf0ea6af7f67ea784fcd856bb3dcd2e3317677ca5` |

The future canonical reconstructed-mainline artifact path/hash is `NOT_YET_CREATED / NOT_YET_AUTHORIZED`; none was invented or generated.

## 5. Materially changed framework locations

- top-level version lineage, source manifest, supersession rule, candidate status, and core-delta summary;
- §0.3 implementation/governance status and next gates;
- §4.1.1 observed versus planning-baseline consumers;
- §4.1.3 prolonged-winter role reversal, epistemic boundary, promotion source, routing, and formula boundary;
- §4.1.4 provenance fields and data lineage;
- §§7.2–7.4 Layer A PV input interpretation for residual load, reserve, and power;
- §7.10 outage-replay artifact identity and unchanged no-surplus-recharge rule;
- §10.3 baseline Layer B PV identity;
- §16.1 reversed winter-PV sensitivity roles;
- §§18.1 and 18.4 data/adequacy validation gates;
- §19.1 historical-result treatment;
- §22 limitation 7;
- §§25–26 execution sequence and oral-defense summary;
- §§31–32 old-output handling, next work, and production checklist;
- §§33–34 explicit historical-snapshot labeling;
- new §35 v7.3 reconstructed-PV decision, provenance, evidence-preservation, authorization-state, and disposition freeze.

## 6. Preserved CLOSED decisions

Diff review and exact-string checks confirmed no redesign of:

- A1–A4, B1–B2, Gate 1, or Gate 2;
- mainline SOC 10–90% and `eta_c = eta_d = 0.90`;
- tariff methodology and constant-NTD-2023 monetary basis;
- intertemporal DOD-sensitive PWL degradation methodology;
- annual regular contract-capacity semantics;
- alpha–beta grid and valid-start non-circular semantics;
- `d_t(alpha) = max(alpha L_t - PV_t, 0)`;
- `R(alpha,beta) = max(valid-start positive residual energy) / eta_d`;
- `P_out(alpha) = max hourly positive residual deficit`;
- annual/replay stage separation and Layer A analytical-consistency no-PV-surplus-recharge rule.

Only the identity/role of mainline `PV_t` in the prolonged unavailable winter block changed.

## 7. Exhaustive stale-wording coverage audit

The complete v7.3 file was scanned case-insensitively for the required literals. Results are counts of matching lines (one line may match multiple terms):

| Literal | Matching lines |
|---|---:|
| `winter` | 37 |
| `missing_winter` | 4 |
| `pre_system` | 3 |
| `zero availability` | 0 |
| `zero-availability` | 2 |
| `sensitivity` | 77 |
| `1,463` | 12 |
| `1463` | 0 |
| `reconstructed` | 66 |
| `synthetic` | 1 |
| `long unavailable` | 3 |
| `long-block` | 9 |

There were 147 unique matching lines. Every line was semantically reviewed. The exact audited universe was:

`1,3,10,11,14,16,22,28,29,31,32,33,34,39,40,50,74,93,105,114,116,118,123,282,354,467,468,500,501,502,504,508,509,515,517,519,523,526,529,531,532,533,534,535,539,557,559,565,568,569,570,574,588,612,615,733,788,854,871,894,1147,1152,1159,1305,1555,1670,1714,1833,1959,1994,1998,2426,2518,2520,2522,2526,2527,2528,2549,2557,2621,2630,2649,2651,2690,2698,2770,2773,2853,2875,2912,2966,3031,3055,3150,3186,3198,3244,3304,3310,3316,3360,3494,3543,3566,3578,3582,3583,3586,3596,3664,3668,3669,3679,3680,3682,3711,3717,3725,3756,3784,3785,3787,3812,3827,3866,3876,3878,3882,3886,3890,3892,3896,3902,3904,3908,3914,3917,3918,3926,3927,3928,3929,3930,3936,3939,3954`.

Classification rule: the following are the B/C subsets; every audited line not in either subset is category A. Lines 3586, 3680, and 3929 contain both historical and zero-winter-stress clauses and were reviewed under both B and C.

- **A — correct new v7.3 mainline/current framework:** all audited lines not listed under B or C (100 lines).
- **B — correct historical v7.2/evidence reference:** `3,10,11,14,50,123,519,523,2773,3055,3304,3316,3360,3494,3543,3566,3578,3586,3669,3679,3680,3756,3784,3785,3787,3812,3827,3866,3917,3926,3927,3928,3929,3930` (34 lines).
- **C — correct zero-winter conservative sensitivity/stress reference:** `28,31,33,532,533,534,1998,2528,2966,3198,3586,3680,3882,3890,3902,3929` (16 lines).
- **D — stale/contradictory:** none.

Targeted forbidden-phrase scans returned zero for the old current-mainline claims `long unavailable PV在 mainline維持 zero`, `alternative CWA reconstructed / synthetic winter PV仍只作`, `conservative zero-availability mainline vs alternative`, `prolonged PV unavailability 在 mainline 以 conservative zero`, and the unqualified sentence `1,463 long unavailable PV hours remain zero in mainline。` The remaining zero-mainline wording appears only inside explicitly labeled historical snapshots.

## 8. Implementation/result boundaries intentionally pending

| Layer | Candidate state |
|---|---|
| Methodology role decision | `DECIDED` |
| Framework v7.3 | `CANDIDATE PASS`; not accepted |
| Registry v7.3 | `NOT_YET_CREATED / NOT_YET_ACCEPTED` |
| New canonical reconstructed-mainline input | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` |
| New production routing | `NOT_YET_AUTHORIZED` |
| Step 17c EOB adjudication | promotion/adjudication candidate evidence only |
| Representative cases | not closed under v7.3 |
| Steps 11A / 11B / 11C | not closed under v7.3 |
| Final 81-point production run | not authorized under v7.3 |

## 9. Repository before/after state

### Before

- branch: `thesis-v7`;
- `HEAD`: `28b0e780c3b298cd88c02e218a99fe3463ff496c`;
- `origin/thesis-v7`: `28b0e780c3b298cd88c02e218a99fe3463ff496c`;
- staged files: 0;
- tracked modified files: 0;
- pre-existing untracked files: 6;
- raw porcelain snapshot SHA-256: `1b327a6b760149b096447422529c76a0d180717cb6d51642bdede697e863407c` (345 bytes).

The six pre-existing untracked files were:

1. `0629開會逐字稿Iris.docx`;
2. `Claude outputs/0930_進度報告_投影片架構與逐頁講稿_v7.2.md`;
3. `Claude outputs/P2_Literature_Positioning_v7.2.pptx`;
4. `Claude outputs/iris_thesis_independent_audit_2026-09-13.md`;
5. `Claude outputs/iris_thesis_repo_audit_2026-09-13.md`;
6. `docs/ESGC Cost Performance Report 2022 PNNL-33283.pdf`.

### After authorized mutations

- branch, `HEAD`, and `origin/thesis-v7`: unchanged;
- staged files: 0;
- tracked modified files: 0;
- pre-existing untracked files: preserved byte-identically and not touched;
- added untracked candidate files only:
  - `docs/research_framework_v7_3_2026-09-23.md`;
  - `docs/checkpoints/framework_v7_3_reconstructed_pv_mainline_successor_candidate_2026-09-23.md`.

## 10. Validation boundary and next gate

Performed: Markdown heading/fence checks, exact-string checks, SHA-256 verification, path existence checks, read-only Git inspection, predecessor-to-candidate diff review, and exhaustive stale-wording semantic classification.

Not performed: tests requiring source changes, optimizer/model calls, solves, data regeneration, canonical routing, production reruns, Registry creation, commit, push, or tag.

The next required action is an independent audit of the v7.3 framework candidate and this checkpoint. Only after acceptance may a separate additive pass create and accept Registry v7.3, create/audit the new canonical reconstructed-mainline artifact, and authorize same-artifact production routing.
