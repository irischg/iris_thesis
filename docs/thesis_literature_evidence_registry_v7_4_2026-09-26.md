# Thesis Literature Evidence Registry v7.4 (2026-09-26, Framework v7.4 alignment successor — Candidate R1)

**Project:** Campus PV–BESS service-continuity planning with contract-capacity economics
**Purpose:** Independent literature/evidence registry; intentionally separate from the research-framework MD.
**Compiled:** 2026-08-04
**Updated:** 2026-09-26 (v7.4 Candidate R1) — this document is the minimal, additive evidence-role / claim-boundary successor that aligns the Registry to the **CLOSED / ACCEPTED Framework v7.4** (`docs/research_framework_v7_4_2026-09-26_r2.md`, SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273`). Its immediate predecessor, **Registry v7.3 R3**, is `CLOSED / ACCEPTED` and remains the **current accepted evidence authority until this candidate is independently accepted**. This successor changes Registry content **only** in the three accepted Framework v7.4 change categories and their dependent status/authority/provenance language: **(A)** zero-winter current role = historical conservative validation / provenance evidence; **(B)** formal observed-versus-planning PV epistemic routing; **(C)** the \(\kappa\) historical-calibration versus planning-use claim boundary without recalibration. There is **no fourth scientific change category**. No external literature source is added, removed, or re-roled outside those categories; no equation, parameter, tariff/cost basis, degradation semantics, preprocessing rule, Layer A/B/DG boundary, solver setting, or accepted numerical result is changed. A1–A4, B1–B2, Gate 1, and Gate 2 remain methodologically closed and are not reopened.

**Formal version naming.** The formal evidence-version name of this successor, once and only if it is independently accepted, is **Registry v7.4** — never “Registry v7.4 R1”. “Candidate R1” is a **provenance revision identifier only**, used for exact repository identity, provenance, audits, hashes, and candidate lineage. The absence of an `_r1` suffix in this file’s path follows the existing first-candidate convention; any later correction must be additive as Candidate R2 rather than an overwrite of these bytes.

**Version lineage:** Registry v7.4 Candidate R1 is the direct, additive successor to the immutable, **accepted** predecessor `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` (SHA-256 `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`), whose bytes are not modified by this pass. The Registry v7.3 R1 and R2 candidates remain immutable **failed** provenance and are never citable as current; §18 and §19 preserve that historical lifecycle record. Registry v7.2 is a historical accepted evidence predecessor only. This successor does not reopen the v7.1/v7.2/v7.3 preprocessing, resilience, billing, degradation, cost, monetary-basis, or Layer A/B/DG evidence decisions; every literature role, project-evidence role, claim-to-source row, and claim boundary not explicitly updated below is inherited unchanged. Registry v7.4 Candidate R1 is a **candidate only** — it is not self-accepting, cannot self-promote, and does not become the evidence source of truth until an independent read-only audit accepts it, per `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md`.

> **Source manifest / provenance**
>
> | Source artifact | Role in Registry v7.4 Candidate R1 | SHA-256 |
> |---|---|---|
> | `docs/research_framework_v7_4_2026-09-26_r2.md` | **CLOSED / ACCEPTED methodology authority**; the alignment target of this successor; immutable; not modified by this pass. Formal name **Framework v7.4**; the `_r2` path suffix is a candidate/provenance revision identifier only | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
> | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | Framework v7.4 methodology acceptance / lifecycle-closure evidence; immutable | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` |
> | `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | Framework v7.4 acceptance manifest; immutable machine-readable closure record | `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33` |
> | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` | **Accepted immutable evidence predecessor**; `CLOSED / ACCEPTED`; **remains the current accepted evidence authority until this candidate is independently accepted**; not modified by this pass | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
> | `docs/research_framework_v7_3_2026-09-23.md` | Accepted methodology predecessor of Framework v7.4; immutable historical lineage | `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a` |
> | `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` | Accepted v7.3 methodology/evidence lifecycle closure; immutable; **not edited**. Its §E.2 zero-winter role statement is a v7.3-era current-prescriptive clause that accepted Framework v7.4 §36.1 supersedes additively | `23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d` |
> | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | Governing provenance/lifecycle protocol for this successor | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
> | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | **CLOSED / ACCEPTED** planning input; role `reconstructed_pv_mainline`; 8,760 rows; the single accepted planning-layer artifact identity | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
> | `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet` | **Historical promotion-source lineage / project evidence only**; corrected Step 17b candidate; **not** the current canonical planning input | `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9` |
> | `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_protocol_2026-09-07.parquet` | Original Step 17b sensitivity-only artifact (historical; not a promotion source) | `023cba88416b965c7dedf4139e9a495602039117ecc827e52a372f10a1aad986` |
> | `results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/final_validation_decision.json` | Step 17a long-block/monthly holdout validation decision — historical `PASS_FOR_SENSITIVITY` | `454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594` |
> | `results/sensitivity/winter_pv_17c/20260918T155044175327Z_3d71b70173/paired_sensitivity_comparison.json` | Step 17c paired reconstructed-vs-zero-winter comparison; **historical project validation / adjudication evidence** supporting the reconstructed-PV promotion decision | `b8acd3027c3c1db31bd8840cf0ea6af7f67ea784fcd856bb3dcd2e3317677ca5` |
> | `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556` | Accepted EOB production run; current governance status **CLOSED / ACCEPTED** (see the execution-time vs governance status rule below) | run directory; per-file hashes in its own immutable manifests |
> | `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55` | Accepted Layer A core-three run (LOW \(\alpha=0.60,\beta=4\,\mathrm{h}\); CENTRAL \(\alpha=0.80,\beta=8\,\mathrm{h}\); HIGH \(\alpha=1.00,\beta=12\,\mathrm{h}\)); current governance status **CLOSED / ACCEPTED** | run directory; per-file hashes in its own immutable manifests |
> | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` | **Failed Registry v7.3 R1 candidate — immutable provenance**; never current | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` |
> | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | **Failed Registry v7.3 R2 candidate — immutable provenance**; never current | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` |
> | `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` | Historical accepted evidence predecessor of Registry v7.3; historical lineage only | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |
> | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | This additive **Registry v7.4 Candidate R1** | `SELF-HASH: recorded externally in the Candidate R1 checkpoint and manifests after generation` |
>
> **Execution-time status versus governance lifecycle status.** The accepted EOB and core-three **completion manifests retain the execution-time status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`**, which is immutable historical fact about what was recorded when those runs finished. Their **current governance lifecycle status is `CLOSED / ACCEPTED`**, established later by separate governance closure. These are two distinct layers. This Registry does **not** claim that the run manifests themselves contain `CLOSED / ACCEPTED`, and those manifest bytes are not modified.
>
> **Supersession rule:** this Registry v7.4 Candidate R1 file is a **candidate** and is **not self-accepting**. Registry v7.3 R3 remains the `CLOSED / ACCEPTED` current evidence authority, and Framework v7.4 is the `CLOSED / ACCEPTED` current methodology authority, until a fresh independent read-only Registry audit accepts this candidate. Once and only if accepted, **Registry v7.4** supersedes Registry v7.3 **solely** in the three Framework v7.4 change categories and the dependent authority/status language enumerated in §20; everywhere else Registry v7.3’s inherited evidence content governs unchanged. All predecessor registries, candidates, checkpoints, audits, freezes, manifests, and results remain preserved byte-identically for provenance, regression, historical-lineage, replication, and comparison. v7.1’s preliminary-optimized-\(P^B\)-dependent cost-bracket rule remains superseded exactly as in v7.2 and v7.3.

---

## 0. 使用方式

這不是文獻回顧章全文，而是一份「文獻—主張對照表」。每篇文獻固定回答：

1. **它直接支持什麼設定或觀點**
2. **本研究可以怎麼用**
3. **它不能支持什麼**
4. **建議放在論文哪一段**

### 使用原則

- 支持「方法方向」的文獻，不自動等於支持某個特定數值。
- 論文中出現某個數值，只代表 **modeling precedent**，不一定是 universal engineering standard。
- 學長論文可說明 model lineage，但不能取代原始技術、成本或制度來源。
- 台電費率、柴油排放係數、CPC 柴油價格、校園設備用途等，應優先使用官方來源。
- 若不同文獻看似衝突，先判斷它們是否其實對應不同 **technology / scale / operating regime / decision role**；只有在支持同一主張卻方向相反時才視為真正衝突。
- mainline、sensitivity、limitation、comparison、legacy/replication 必須分開標記；不得因某篇文獻數值更新，就讓舊來源繼續控制 mainline。
- 期刊分區會隨年份／分類變化，論文定稿前需按學校採用的 JCR/SJR 年度再次確認。

### Audit-status rule (v7.2)

A1–A4、B1–B2、Gate 1 與 Gate 2 現在均視為 **methodologically CLOSED**。Registry 中的狀態必須區分：
- `CLOSED / PASS`：指定 script / audit 已完成且可作 current production evidence；
- `POPULATED / LOCKED BY PACKAGE`：numerical parameter 已由 current production derivation 建立，但其 exact digits仍由 machine-readable artifact控制；
- `IMPLEMENTATION / VALIDATION PENDING`：方法已定，但 downstream production-interface、post-solve validation、rainflow或 final rerun尚未完成。

**v7.4 scoping of this rule (CHANGE A).** The v7.3-era form of the `IMPLEMENTATION / VALIDATION PENDING` list also named a **winter-PV sensitivity** as outstanding work. That was correct under Framework v7.3. Under accepted **Framework v7.4 §36.1** zero-winter is **not** a mandatory EOB / Layer A / Layer B sensitivity, so it is no longer carried as a pending validation item and **is not replaced by a substitute sensitivity** — the minimum-sensitivity inventory is net one item shorter. Its current role is historical conservative validation / provenance evidence (see [P1] P1-E, [P7], §20.1).

目前不再把 \(\kappa\) reproduction、\(C_E,C_P,FOM,C_{rep}\) population、1 MW/10 MW package construction或 Xu semantics audit列為 pending：這些已由 post-v7.1 scripts 關閉。Gate 2 的 **方法**已關閉，但 official nominal Taipower tariffs → constant NTD-2023 optimization layer 的 machine-readable production conversion仍是 Script 14a 前置 implementation gate。

**Coding source-of-truth rule:** Under the v7.2 authority state, Framework v7.2 and Registry v7.2 were the then-current mainline specification/evidence pair; under the v7.3 authority state, Framework v7.3 and (after its independent acceptance) Registry v7.3 R3 were that pair. Those are **historical** statements. **Under the current authority state: Framework v7.4** (`docs/research_framework_v7_4_2026-09-26_r2.md`) is the `CLOSED / ACCEPTED` methodology source of truth, and **Registry v7.3 R3** (`docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`) is the `CLOSED / ACCEPTED` evidence source of truth **until this Registry v7.4 Candidate R1 passes independent acceptance**. Registry v7.4 Candidate R1 is a candidate only and must not be cited as current evidence authority. Framework v7.2 and Framework v7.3 are historical methodology predecessors, not current methodology authority; Registry v7.2 is a historical evidence predecessor, and Registry v7.3 R1/R2 are failed immutable provenance. Earlier framework/registry versions may be used only when the current accepted Framework or Registry explicitly classifies them as legacy, replication, regression, provenance, historical lineage, or comparison material. Current accepted machine-readable artifacts, not historical framework constants, control exact production values.

**Project-evidence rule for preprocessing:** External literature supports reconstruction principles and validation logic. Exact production choices are empirical project results and must be cited to P1 / Script outputs. A method losing the project head-to-head validation remains a benchmark or comparison method even if it has literature precedent.

**Economic-evidence rule (v7.2):** Literature may support scale dependence, common-base-year normalization, and real/nominal consistency, but it does not by itself select NTUST's exact 10 MW mainline package, FX=31.150, or tariff deflator. Those exact choices are thesis/project decisions or project-derived parameters and must remain traceable to P6 / parameter artifacts.

## 0.1 v7.2 literature/evidence-conflict resolution summary

| 看似衝突的證據 | v7.2 處理 | 最終角色 |
|---|---|---|
| LFP 10–90% vs 20–80% SOC | 不視為互斥標準；前者作 representative mainline，後者作 deliberately more restrictive sensitivity | R14–R19 |
| ηc/ηd 候選值 0.95/0.90、0.91/0.91、0.90/0.90 | A1 已鎖定 system-level ηc=ηd=0.90；Qi et al. (2025) 提供直接近期 precedent；PNNL system-level RTE僅作 boundary-consistency sanity check，不再對稱拆成0.91/0.91 | R30 + T2 |
| PNNL v2024 cost vs NREL 2025 projection | 不混用為同一 numerical source；PNNL v2024 控制 mainline，NREL 2025 保留 external sensitivity/benchmark | T1–T3 |
| Xu et al. (2018) intertemporal PWL vs Harry-style hourly-reset segment penalty | B1 已鎖定 Xu-derived cross-time segment-energy states；hourly-reset只能稱 throughput proxy並降為 legacy/benchmark，不能繼承 Xu 的 cycle-depth claim | R20 + T4 + L1 |
| PWL optimization vs full rainflow cycle counting | mainline 使用 Xu-derived convex PWL approximation；rainflow不嵌入年度 sizing optimization，只作 ex-post cycle-depth/cost validation | R20 + R31 + T4 |
| constant worst-case reserve floor vs time-varying preparedness floor | A2 mainline採 constant worst-case reserve；R7只支持 preparedness/economic trade-off，不提供本研究公式；perfect-information variable floor只做6-point targeted robustness | R7 + P4 |
| annual reserve floor vs outage replay lower bound | annual normal operation維持 SOCmin+R；獨立 outage replay從最低 preparedness state開始後可消耗 R 至 technical SOCmin，事件末不要求恢復 R | P4 |
| annual cyclic BESS state vs outage year-end wrap | 前者是年度 optimization boundary；後者會人工拼接不同 case-year 邊界，v7.2 延續禁止 | R11 + P4 |
| literature imputation / PV-estimation methods vs NTUST site-selected production rules | 文獻只支持 pattern/context-aware Load imputation、solar-gap validation、weather/irradiance→PV estimation與 model-selection logic；exact production rule由 project validation決定：Load = same weekday ±6 weeks/K=1；PV short-gap = CWA `hourly_ghi_ratio_median`。PV donor ±30 days/K=5 mean保留 benchmark，不再是 production mainline | R21–R23 + R32–R33 + I5 + P1 |
| site-feasibility literature/engineering concerns vs mainline optimization | 不否定工程限制，而是將其移出 core RQ / production blocker，降為 implementation-stage overlay | R24–R25 |
| Harry-era 813.75/694.4/0.07、0.55、0.532/1.596/2.128 vs current assumptions | 舊數值僅 replication/lineage；不得控制 v7.2 mainline | T2–T4 + L1 |
| hourly vs sub-hourly temporal resolution | 近期證據只用來界定 hourly model 的 limitation；不把任何文獻的誤差百分比直接移植到 NTUST | R28–R29 |
| literature temporal-resolution evidence vs κ≈1.01037 | 文獻支持 hourly aggregation 對 power/peak/SOC 可能敏感；κ 是 NTUST observed Load−PV 對實際 billed overall maximum 的 site-specific empirical calibration | R28–R29 + I1 + P2 |
| bill-title month vs actual usage period | billing join 一律以帳單明列的 usage-period start/end 為準；例如標題2025/10帳單對應2025/09/01–09/30 | I3 + P2 |
| 四時段 billed maxima vs monthly billed maximum | overall billed maximum定義為 peak/half/Sat-half/off-peak 四者取 max；不是只取 peak period | I3 + I4 + P2 |
| 四時段超約量直接相加 vs Taipower non-duplication | A3 依官方三段式時間電價 cumulative threshold + non-duplication + 2×/3× tier；不同新增超約區段使用所屬時段 applicable basic rate | I3 |
| floating optimization demand epigraph vs exact reporting maximum | A4 將 cost-facing auxiliary與 reporting quantity分離；exact maxima solve後由 optimized grid profile ex-post重算 | P5 |
| annualized CAPEX + degradation wear vs explicit replacement stream | B2 無 structural change；保留 annualized ownership cost + annual FOM + cycling wear，不再額外加入 full replacement/augmentation cash-flow stream | T2–T3 + P3 |
| lab-predecessor κ/cost coefficients vs academic benchmark | lab predecessor 只保留 lineage/context；benchmark 優先順序為 official rules → peer-reviewed mainstream/recent literature → authoritative technical reports | P2 + L1 |
| 1 MW vs 10 MW PNNL cost scale | scale-dependent BESS cost有文獻 precedent，但 v7.2 不依 optimized \(P^B\) 回頭挑 bracket；10 MW package事前固定為mainline、1 MW整包作higher-cost sensitivity | R34 + T2 + P6 |
| continuous scale-dependent cost curve vs discrete PNNL source cases | literature可建立 scale functions，但本研究不以兩個 PNNL source cases自行發明 continuous interpolation；以 source-supported 10 MW / 1 MW scenarios做mainline + sensitivity | R34 + T2 + P6 |
| 2023 BESS cost vs 2024/25 nominal tariff | 不直接相加；optimization-facing costs統一為constant NTD-2023，raw nominal tariff保留給13b/13c institutional validation | R35–R36 + T5 + I3 + P6 |
| 5% discount rate：literature precedent vs real/nominal interpretation | R26–R27只支持5%/20-year modeling precedent；v7.2將5%定義為real rate是為配合constant-dollar accounting，不宣稱文獻提供NTUST real WACC | R26–R27 + T5 + P6 |
| official tariff values vs normalized optimization tariff | official nominal values不得被覆寫；另建立constant-2023 optimization layer。13b/13c仍在原始nominal basis驗證 | I3 + T5 + P6 |
| SCHOOL/FROZEN / non-summer peak / subsidy wording | `SCHOOL/FROZEN`是project institutional label；non-summer peak=N/A，不是0-rate；subsidy不另加cash-flow，避免與effective tariff double count | I3 + P6 |
---

# 1. Resilience 會改變 sizing 與成本

## [R1] Laws et al. (2018)

**Citation**  
Laws, N., Anderson, K., Li, X., McLaren, J., & DiOrio, N. (2018). *Impacts of Valuing Resilience on Cost-Optimal PV and Storage Systems for Commercial Buildings*. **Renewable Energy, 127**, 896–909.  
DOI: https://doi.org/10.1016/j.renene.2018.05.011

### 支持什麼
- 把 resilience value 納入 PV–BESS techno-economic optimization，會改變 cost-optimal PV/BESS capacity。
- 明確討論 **islandable premium**：為了具備停電時供應 critical load 的能力，需要付額外成本。
- resilience investment 應看成本與服務價值的 trade-off，而不是假設越高越好。

### 本研究怎麼用
支持：
- Economic-Only Benchmark (EOB) vs resilience-constrained design；
- resilience/capacity cost premium；
- 「服務連續性要求會改變 BESS sizing 與成本」這個核心研究問題。

### 不能支持
- 你的 \(\alpha\) 數值；
- 你的 \(\beta\) 數值；
- all-start reserve 公式；
- universal best service level。

### 建議放置
Chapter 1 motivation / gap；Chapter 2 resilience economics；Chapter 3 premium 定義。

**Evidence role:** 核心概念文獻。

---

## [R2] Bazdar, Nasiri & Haghighat (2024)

**Citation**  
Bazdar, E., Nasiri, F., & Haghighat, F. (2024). *Resilience-centered optimal sizing and scheduling of a building-integrated PV-based energy system with hybrid adiabatic-compressed air energy storage and battery systems*. **Energy, 308**, 132836.  
DOI: https://doi.org/10.1016/j.energy.2024.132836

### 支持什麼
- 正式做 economic–resilience co-optimization。
- 採 sizing + scheduling 的兩階段結構。
- resilience-oriented design 會改變 storage configuration 與經濟結果。

### 本研究怎麼用
支持「resilience requirement 可以進入容量規劃」，而不是只能事後算 resilience metric。

### 不能支持
- 本研究首創 resilience-constrained sizing；
- Taiwan contract capacity；
- all-start historical requirement；
- 本研究的 BESS-only 具體公式。

### 建議放置
Chapter 2 resilience-centered sizing；research-gap comparison table。

**Evidence role:** 強 comparison paper。

---

## [R3] Rodriguez et al. (2024)

**Citation**  
Rodriguez, R., Osma, G., Bouquain, D., Ordoñez, G., Paire, D., Solano, J., Roche, R., & Hissel, D. (2024). *Electrical resilience assessment of a building operating at low voltage*. **Energy and Buildings, 313**, 114217.  
DOI: https://doi.org/10.1016/j.enbuild.2024.114217

### 支持什麼
- 把 **service continuity** 視為 building electrical resilience 的核心構面。
- 整合 critical loads、backup system、service continuity 與 power quality。

### 本研究怎麼用
支持以「停電時能維持多少服務」作為 resilience framing。

### 不能支持
- \(\alpha L_t\) 等比例負載就是完整 critical-load inventory；
- \(\alpha=0.6\sim1.0\) 的具體數值。

### 建議放置
Chapter 2 resilience definition；Chapter 3 \(\alpha L_t\) proxy limitation。

**Evidence role:** service-continuity 概念支持。

---

# 2. PV–BESS outage capability 與時序條件

## [R4] Gorman et al. (2023)

**Citation**  
Gorman, W., Barbose, G., Carvallo, J. P., Baik, S., Miller, C., White, P., & Praprost, M. (2023). *County-level assessment of behind-the-meter solar and storage to mitigate long duration power interruptions for residential customers*. **Applied Energy, 342**, 121166.  
DOI: https://doi.org/10.1016/j.apenergy.2023.121166

### 支持什麼
- 評估 PV + storage 在 long-duration outages 下的 backup capability。
- 考慮不同 building/customer、climate、whole-building backup 與 critical-load backup。
- backup capability 取決於 load 與 interruption condition，而非只看 BESS nameplate。

### 本研究怎麼用
支持：
- outage duration 與 service/load requirement 是重要規劃維度；
- 必須把 load/PV 時序放進停電能力評估；
- BESS 容量不能單獨代表 resilience。

### 不能支持
- 校園 \(\alpha,\beta\) grid；
- contract-capacity coupling；
- all-start reserve 公式；
- 把住宅結果數值直接套到 NTUST。

### 建議放置
Chapter 2 PV–BESS outage survivability；Layer A 時序理由。

**Evidence role:** 核心 outage-capability 文獻。

---

## [R5] Sepúlveda-Mora & Hegedus (2022)

**Citation**  
Sepúlveda-Mora, S. B., & Hegedus, S. (2022). *Resilience analysis of renewable microgrids for commercial buildings with different usage patterns and weather conditions*. **Renewable Energy, 192**, 731–744.  
DOI: https://doi.org/10.1016/j.renene.2022.04.090

### 支持什麼
- 分析不同 building load pattern 與 weather 對 resilience 的影響。
- 比較 PV、battery、wind、generator configurations。
- 提出 worst/best-case outage selection 的方法。
- 顯示 load shape 與 renewable availability 會影響 outage survivability。

### 本研究怎麼用
支持：
- Layer B 分析不同 load/PV condition；
- severe / typical / solar-assisted archetype 的概念；
- 「失效與 weather/demand condition 有關」；
- PV–BESS-only 與 generator-assisted 的比較。

### 不能支持
- 你的 95th/50th percentile archetype 選法；
- 27-case structure；
- structured-scenario coverage = probability。

### 建議放置
Chapter 2 outage survivability；Chapter 3 Layer B archetype rationale。

**Evidence role:** condition-dependent outage analysis。

---

# 3. Layer B：fixed-design / out-of-sample capability

## [R6] Pickering & Choudhary (2021)

**Citation**  
Pickering, B., & Choudhary, R. (2021). *Quantifying resilience in energy systems with out-of-sample testing*. **Applied Energy, 285**, 116465.  
DOI: https://doi.org/10.1016/j.apenergy.2021.116465

### 支持什麼
- 明確提出 **optimization 後再做 out-of-sample testing**。
- 技術配置固定後，再暴露於新的 demand / power interruption condition。
- 用 energy imbalance / unmet demand 衡量 resilience。
- 清楚區分 design optimization 與 post-design testing。

### 本研究怎麼用
這是 Layer B 最重要的 methodological support：

> 先得到 design，再固定 \(E^N, P^B, CC\)，放入 off-design condition 評估。

也支持使用 ENS、shortfall 等連續退化指標，而非只回 infeasible。

### 不能支持
- Layer B 是 real-world failure probability；
- 27-scenario design；
- formal global sensitivity analysis；
- 你的 \(\epsilon\) threshold。

### 建議放置
Chapter 2 fixed-design validation；Chapter 3 Layer B justification；口試說明。

**Evidence role:** **Layer B 核心方法文獻。**

---

# 4. Preparedness reserve / minimum SOC

## [R7] Son et al. (2024)

**Citation**  
Son, Y., Woo, H., Noh, J., Dehghanian, P., Zhang, X., & Choi, S. (2024). *Optimization of energy storage scheduling considering variable-type minimum SOC for enhanced disaster preparedness*. **Journal of Energy Storage, 93**, 112366.  
DOI: https://doi.org/10.1016/j.est.2024.112366

### 支持什麼
- 把 **minimum SOC management** 明確連到 disaster preparedness。
- reserve 更多 stored energy 可提升供電能力，但會犧牲正常運轉經濟性。
- 經濟 dispatch 與 outage readiness 之間存在 trade-off。

### 本研究怎麼用
直接支持：
- 不再任意指定停電瞬間 initial SOC；
- 改用 year-round reserve / minimum available-energy policy；
- 「同一顆 BESS 的經濟用途與 preparedness 互相競爭」。

### 不能支持
- 你的 \(R(\alpha,\beta)\) 解析公式；
- universal minimum SOC percentage；
- LFP 10–90%。

### 建議放置
Chapter 2 SOC reserve；Chapter 3 reserve-policy justification。

**Evidence role:** **Preparedness reserve 核心文獻。**

---

# 5. TOU、peak shaving 與 contract capacity

## [R8] Chen & Liao (2011)

**Citation**  
Chen, C.-Y., & Liao, C.-J. (2011). *A linear programming approach to the electricity contract capacity problem*. **Applied Mathematical Modelling, 35(8)**, 4077–4082.  
DOI: https://doi.org/10.1016/j.apm.2011.02.032

### 支持什麼
- Taiwan industrial customers 的 electricity contract capacity 可以正式建成 optimization decision。
- 用 linear programming 求 CC。
- 有 university 與 paper mill 真實案例。

### 本研究怎麼用
支持：
- \(CC\) 作 decision variable；
- Taiwan high-voltage customer 的 CC 最佳化有既有研究基礎；
- campus/university 是合理案例場域。

### 不能支持
- 2026 台電費率；
- 2026 超約 multiplier；
- BESS/resilience coupling。

### 建議放置
Chapter 2 Taiwan CC；Chapter 3 endogenous \(CC\)。

**Evidence role:** **Taiwan CC 核心文獻。**

---

## [R9] Sepúlveda-Mora & Hegedus (2021)

**Citation**  
Sepúlveda-Mora, S. B., & Hegedus, S. (2021). *Making the case for time-of-use electric rates to boost the value of battery storage in commercial buildings with grid connected PV systems*. **Energy, 218**, 119447.  
DOI: https://doi.org/10.1016/j.energy.2020.119447

### 支持什麼
- Behind-the-meter PV + Li-ion BESS under TOU tariffs。
- BESS 可做 peak shaving、energy arbitrage。
- degradation assumption 與 tariff structure 會改變經濟性。

### 本研究怎麼用
支持 shared-BESS logic：

> BESS 平時可做 TOU / peak shaving，停電時又承擔 service continuity。

也支持 objective 中考慮 degradation economics。

### 不能支持
- Taiwan tariff 數值；
- contract-capacity penalty；
- 你的 degradation coefficient。

### 建議放置
Chapter 2 BESS multi-service economics；Chapter 3 objective。

**Evidence role:** 正常運轉經濟面核心支持。

---

## [R10] İşcan & Arıkan (2025)

**Citation**  
İşcan, S., & Arıkan, O. (2025). *Optimizing battery energy storage system for campus micro grid: Economic and environmental benefits of strategic sizing*. **Journal of Energy Storage, 124**, 116905.  
DOI: https://doi.org/10.1016/j.est.2025.116905

### 支持什麼
- 直接研究 university campus microgrid 的 BESS sizing。
- 結合 TOU、peak shaving、economic 與 environmental objectives。

### 本研究怎麼用
支持「campus BESS sizing 已有文獻」，因此你的 novelty 不應寫成「第一次做 campus BESS sizing」，而是加入：
- service-continuity requirement；
- Taiwan CC economics；
- all-start adequacy；
- fixed-design off-design analysis。

### 不能支持
- 本研究 outage-service requirement；
- Taiwan CC rule。

### 建議放置
Chapter 2 campus BESS sizing；research-gap table。

**Evidence role:** 直接 campus comparator。

---

# 6. Annual chronology / long-horizon storage

## [R11] Gabrielli et al. (2018)

**Citation**  
Gabrielli, P., Gazzani, M., Martelli, E., & Mazzotti, M. (2018). *Optimal design of multi-energy systems with seasonal storage*. **Applied Energy, 219**, 408–424.  
DOI: https://doi.org/10.1016/j.apenergy.2017.07.142

### 支持什麼
- storage design 可能需要 year-long horizon + hourly resolution。
- 長期 storage state 的 chronological continuity 與年度 boundary 不應任意忽略。
- 長週期 storage optimization 的 computational challenge。

### 本研究怎麼用
支持：
- 保留完整 annual chronology；
- annual optimization 使用明確的 terminal-state rule，例如 \(e_T=e_0\)，避免模型在年末免費耗盡或累積能量；
- 避免 representative-period 壓縮破壞 storage inter-temporal structure。

### 不能支持
- 本研究的 resilience reserve 公式；
- Taiwan tariff；
- resilience-specific SOC floor；
- **不能用來替「outage window 在 10 月底 circular wrap 回同一資料集 11 月初」背書。**

### v6.2 conflict correction

annual cyclic battery-state boundary 與 outage-window circular indexing 是兩件不同的事：

- \(e_T=e_0\) 是 optimization state boundary；
- Layer A outage scan 只使用完整 \(\beta\)-hour trajectory 位於正式 case year 內的 valid starts；
- 若沒有 genuine next-year continuation data，不將 year-end outage 人工接回 year-start。

### 建議放置
Chapter 2 annual chronology；Chapter 3 BESS state boundary；data chronology limitation。

**Evidence role:** long-horizon modeling support；**不支持 outage circular wrap**。

---

# 7. DG / fossil-assisted counterfactual

## [R12] Marqusee, Becker & Ericson (2021)

**Citation**  
Marqusee, J., Becker, W., & Ericson, S. (2021). *Resilience and economics of microgrids with PV, battery storage, and networked diesel generators*. **Advances in Applied Energy, 3**, 100049.  
DOI: https://doi.org/10.1016/j.adapen.2021.100049

### 支持什麼
- 同時分析 PV、battery、emergency diesel generator 的 resilience 與 economics。
- component reliability / availability 會影響 islanded performance。
- hybrid microgrid 的 life-cycle economics 與 resilience trade-off 是合理研究問題。

### 本研究怎麼用
支持把 hypothetical DG 做成正式 counterfactual：
- BESS reliance；
- DG reliance；
- fixed preparedness cost；
- fuel / outage performance。

### 不能支持
- 把 NTUST 現有消防 DG 放進 aggregate campus model；
- 你的 DG coverage 公式；
- 0–100% 每 10%；
- 50% DG optimal。

### 建議放置
Chapter 2 PV–BESS–DG trade-off；Chapter 3 DG counterfactual。

**Evidence role:** **DG 核心文獻。**

---

## [R13] Wu & Sansavini (2020)

**Citation**  
Wu, R., & Sansavini, G. (2020). *Integrating reliability and resilience to support the transition from passive distribution grids to islanding microgrids*. **Applied Energy, 272**, 115254.  
DOI: https://doi.org/10.1016/j.apenergy.2020.115254

### 支持什麼
- 整合 techno-economic、reliability、resilience objectives。
- storage + distributed generation 支援 stochastic islanding / priority demand。
- resilience/reliability requirement 會影響 resource planning。

### 本研究怎麼用
支持 BESS 與 dispatchable generation 都可視為 outage-support resources。

也可用來強調你的 boundary：
- 文獻可做 stochastic reliability；
- 本研究則刻意做 deterministic historical all-start requirement，不宣稱 outage probability。

### 不能支持
- Layer B pass proportion = probability；
- 你的 DG coverage sweep；
- 你的 \((\alpha,\beta)\) response surface。

### 建議放置
Chapter 2 stochastic resilience comparator；claim boundary。

**Evidence role:** 強 comparator。

---

# 8. LFP 與 SOC operating window

## [R14] Wei et al. (2022)

**Citation**  
Wei, Y., Wang, S., Han, X., Lu, L., Li, W., Zhang, F., & Ouyang, M. (2022). *Toward more realistic microgrid optimization: Experiment and high-efficient model of Li-ion battery degradation under dynamic conditions*. **eTransportation, 14**, 100200.  
DOI: https://doi.org/10.1016/j.etran.2022.100200

### 支持什麼
- 使用 graphite–LiFePO₄ (LFP) cells。
- aging profile 來自 PV–BESS–EV microgrid dynamic operation。
- prolonged cycling 在 **DoD > 80% 且有約 1.5C pulse current** 時可能出現 lithium-plating-related nonlinear aging。
- 對文中 severe profile，作者指出 operating SOC 應控制在約 **10%–90%**。

### 本研究怎麼用
這是最直接支持：

\[
SOC_{\min}=0.10,\quad SOC_{\max}=0.90
\]

作為 **representative mainline planning assumption** 的 Q1 技術證據。

### 不能支持
- 所有 LFP 一律 10–90%；
- 10–90% 是 global optimum；
- 忽略 C-rate / profile context。

### 建議放置
Chapter 3 BESS assumptions；parameter appendix。

**Evidence role:** **10–90% 技術核心文獻。**

---

## [R15] Adeyemo & Amusan (2022)

**Citation**  
Adeyemo, A. A., & Amusan, O. T. (2022). *Modelling and multi-objective optimization of hybrid energy storage solution for photovoltaic powered off-grid net zero energy building*. **Journal of Energy Storage, 55**, 105273.  
DOI: https://doi.org/10.1016/j.est.2022.105273

### 支持什麼
- 比較 LFP、retired EV battery、OPzV。
- optimization model 明確設：
  - REVB SOC 20–80%；
  - **LFP SOC 10–90%**。

### 本研究怎麼用
支持「LFP 10–90% 不是本研究自己發明的 modeling range」。

最佳搭配：
- Wei = technical aging evidence；
- Adeyemo = optimization precedent。

### 不能支持
- 10–90% 是 manufacturer universal standard；
- 每一種 stationary LFP 都最佳。

### 建議放置
Chapter 3 SOC parameter justification。

**Evidence role:** **10–90% modeling precedent。**

---

## [R16] Naumann et al. (2018)

**Citation**  
Naumann, M., Schimpe, M., Keil, P., Hesse, H. C., & Jossen, A. (2018). *Analysis and modeling of calendar aging of a commercial LiFePO₄/graphite cell*. **Journal of Energy Storage, 17**, 153–169.  
DOI: https://doi.org/10.1016/j.est.2018.01.019

### 支持什麼
- 29 個月 commercial LFP/graphite calendar-aging study。
- 明確連到 **stationary battery applications**。
- SOC 與 temperature 會顯著影響 capacity loss / resistance increase。

### 本研究怎麼用
支持：
- stationary LFP 是合理技術基準；
- SOC boundary 有實際 aging 意義；
- year-round high reserve SOC 可能產生 calendar-aging implication。

### 不能支持
- 10–90% 精確範圍；
- 忽略 calendar aging。

### 建議放置
Chapter 2/3 LFP aging；limitations。

**Evidence role:** stationary-LFP aging evidence。

---

## [R17] Naumann, Spingler & Jossen (2020)

**Citation**  
Naumann, M., Spingler, F. B., & Jossen, A. (2020). *Analysis and modeling of cycle aging of a commercial LiFePO₄/graphite cell*. **Journal of Power Sources, 451**, 227666.  
DOI: https://doi.org/10.1016/j.jpowsour.2019.227666

### 支持什麼
- commercial LFP/graphite cycle aging。
- 同時測 temperature、C-rate、DoD、SOC。
- dynamic validation 使用 stationary-storage synthetic load profile。
- LFP aging 不宜簡化成單一 universal SOC rule。

### 本研究怎麼用
支持：
- SOC / DoD 需做 sensitivity；
- 不能說「SOC window 越窄一定越好」；
- product/BMS/operation 都可能改變適合範圍。

### 不能支持
- 20–80% 永遠比 10–90% 好；
- universal cycle-life multiplier。

### 建議放置
Chapter 3 SOC/degradation assumption；limitations。

**Evidence role:** sensitivity / claim-boundary evidence。

---

## [R18] Omar et al. (2014)

**Citation**  
Omar, N., Abdel-Monem, M., Firouz, Y., Salminen, J., Smekens, J., Hegazy, O., Gaulous, H., Mulder, G., Van den Bossche, P., Coosemans, T., & Van Mierlo, J. (2014). *Lithium iron phosphate based battery – Assessment of the aging parameters and development of cycle life model*. **Applied Energy, 113**, 1575–1585.  
DOI: https://doi.org/10.1016/j.apenergy.2013.09.003

### 支持什麼
LFP aging 受：
- current rate；
- temperature；
- depth of discharge；
- fast charging condition
影響。

### 本研究怎麼用
支持：
- 不把 0–100% nameplate 當成無代價可用；
- degradation 應進規劃；
- usable-energy / SOC assumption 需要 sensitivity。

### 不能支持
- universal 10–90%；
- 你的 \(c_{deg}\) 係數。

### 建議放置
Chapter 2 battery degradation；Chapter 3 assumptions。

**Evidence role:** foundational LFP aging。

---

## [R19] Xu, Wang, Zhang & Zhao (2021) — SOC sensitivity only

**Citation**  
Xu, M., Wang, X., Zhang, L., & Zhao, P. (2021). *Comparison of the effect of linear and two-step fast charging protocols on degradation of lithium ion batteries*. **Energy, 227**, 120417.  
DOI: https://doi.org/10.1016/j.energy.2021.120417

### 支持什麼
- 研究 cylindrical LFP cell。
- 使用 **20–80% SOC** cycling range。
- 可作較窄 SOC operating range 的實驗 precedent。

### 本研究怎麼用
支持把：

\[
SOC\in[0.20,0.80]
\]

作為 **deliberately more restrictive technical sensitivity case**。

### 不能支持
- 20–80% 是 stationary LFP universal optimum；
- 20–80% 一定比 10–90% 壽命更好；
- fast-charging cell 結果直接等於 campus BESS；
- **不能作 v7.2 PWL degradation formulation 的方法依據。** PWL mainline 的 Xu 文獻是 **Xu et al. (2018), R20**。

### 建議放置
Chapter 3 sensitivity assumptions；appendix。

**Evidence role:** conservative SOC sensitivity precedent only。

---

# 9. Audit-resolution additions：degradation、data reconstruction、decision-support、finance

## [R20] Xu et al. (2018) — intertemporal PWL cycle-aging methodology

**Citation**  
Xu, B., Zhao, J., Zheng, T., Litvinov, E., & Kirschen, D. S. (2018). *Factoring the Cycle Aging Cost of Batteries Participating in Electricity Markets*. **IEEE Transactions on Power Systems, 33(2)**, 2248–2259.  
DOI: https://doi.org/10.1109/TPWRS.2017.2733339  
Open preprint: https://arxiv.org/abs/1707.04567

### 直接支持什麼
- Battery cycle aging 對 cycle depth 呈非線性；Xu 以 **convex piecewise-linear marginal cycle-aging cost** 近似 nonlinear cycle-depth stress，使 degradation economics 可嵌入 dispatch optimization。
- Xu 採 **discharge-only aging convention**：cycle aging cost 計於 discharge stage；其 Eq. (5) 將 discharge efficiency \(1/\eta^{dis}\) 吸收到 AC-side marginal cost coefficient \(c_j\) 中，Eq. (7) 再以 \(c_jp^{dis}_{t,j}M\) 計價。
- 原始 formulation 不是每個 hour reset：它對每個 cycle-depth segment 建立 \(p^{ch}_{t,j}\)、\(p^{dis}_{t,j}\) 與 **跨時間 energy state \(e_{t,j}\)**；Eq. (12) 追蹤 segment stored energy 隨 charge/discharge 與 efficiency 的跨時段演化。
- 由於 marginal aging-cost curve 為 convex，較淺／較便宜 segment 具有較高 dispatch priority；Appendix Theorem 1 對給定 feasible battery dispatch 下的這項 segment-priority property 提供理論基礎。
- Xu 以 rainflow-based benchmark 檢驗 approximation；Appendix Theorem 2 證明其所定義的等寬 PWL sequence 在 segment 數趨近無限時，aging cost 收斂至 rainflow-based benchmark cost。

### Equation-level mapping（已核對原文）
- **Eq. (4)–(5)**：等寬 cycle-depth segmentation 與 marginal aging-cost coefficient \(c_j\) construction；Eq. (5) 的 \(c_j\) 已包含 \(1/\eta^{dis}\)。
- **Eq. (7)**：總 cycle-aging cost 為各時間、各 depth segment discharge cost 的加總。
- **Eq. (8)–(9)**：segment charge/discharge 與 aggregate battery power 的連結。
- **Eq. (10)–(11)**：charge/discharge power-rating constraints。
- **Eq. (12)**：intertemporal segment-energy state dynamics，含 charge/discharge efficiency。
- **Eq. (13)**：segment energy upper bound。
- **Eq. (14)**：aggregate battery minimum/maximum stored-energy constraints。
- **Eq. (15)–(16)**：initial segment energy 與 terminal stored-energy requirement。
- **Appendix Theorem 1**：在給定 feasible dispatch 且 aging curve convex 時，shallow-to-deep segment priority 為 reduced aging-cost problem 的 minimizer。
- **Appendix Theorem 2**：對 Xu 所定義的等寬 segmentation sequence，segment 數趨近無限時，PWL aging cost 收斂至 rainflow benchmark。

### 本研究怎麼用
R20 是 v7.2-retained **B1 mainline optimization formulation 的主要 methodological source**。正式名稱統一為：

> **PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL cycle-aging formulation**

Xu 直接控制的核心 semantics：
- discharge-only cycle-aging convention；
- segment-specific charge/discharge；
- cross-time segment-energy states；
- AC-side discharge / battery-side stored-energy efficiency placement；
- convex shallow-to-deep segment priority；
- rainflow benchmark / convergence rationale。

PNNL（T4）另行控制 LFP DOD–cycle-life technical calibration；兩個來源的角色不得混稱。

### 本研究的 thesis-specific adaptation
Xu 原文研究的是固定額定容量的 market-dispatch battery；本研究另行做以下 adaptation：

1. **PNNL sparse / nonuniform DOD points → finite nonuniform PWL**，而非直接沿用 Xu Eq. (4) 的等寬 \(1/J\) segmentation；
2. **equal-slope merging**：相鄰斜率相同的 PNNL intervals 可合併為 effective 3-segment implementation；
3. **endogenous sizing**：segment capacity 寫成
   \[
   \bar E_k=(b_k-b_{k-1})E^N,
   \]
   其中 \(E^N\) 是 sizing decision；
4. **10–90% SOC window**：本研究 effective depth domain 為 usable 0–80% nameplate range；
5. **annual cyclic segment boundary**：\(e_{T,k}^{seg}=e_{0,k}^{seg}\) 配合年度 optimization horizon；
6. \(\lambda_k\) 的 NTD/battery-kWh numerical values 由 PNNL calibration + final \(C_{rep}\) 推導；
7. finite nonuniform/merged segment implementation 的 rainflow approximation error 必須自行驗證。

上述 adaptation 不改變 B1 方法方向，但也**不得宣稱由 Xu 原文 theorem 原封不動直接證明**。

### \(\lambda_k\) / efficiency convention guardrail
本研究定義：

\[
\boxed{\lambda_k:\ \mathrm{NTD/(battery\text{-}side\ discharged\ kWh)}}.
\]

因此本研究 objective 使用：

\[
C_{cycling}^{deg}
=
\sum_t\sum_k
\lambda_k\frac{p_{t,k}^{dis}\Delta t}{\eta_d}.
\]

這與 Xu Eq. (5)–(7) 的 convention **代數等價但表示位置不同**：Xu 將 \(1/\eta^{dis}\) 包在 AC-side marginal coefficient \(c_j\) 中；本研究讓 \(\lambda_k\) 保持 battery-side coefficient，再將 AC-side discharge energy 除以 \(\eta_d\)。**兩種 convention 不得混用**，否則 discharge efficiency 會被 double-count。

### 不能支持
- 把本研究簡稱為「the Xu model」或暗示 Xu model 原封不動套用；
- Harry-style「每個 hour 把 discharged energy 重新從最便宜 segment 填滿」等同 Xu formulation；
- 本研究的 PNNL DOD/cycle-life 數值、nonuniform exact breakpoints 或 equal-slope merging 是 Xu 原文設定；
- 任意一組 \(\lambda_k\) 是 Xu 或 PNNL published coefficient；
- Xu Theorem 1–2 直接證明 endogenous \(E^N\) sizing extension、annual cyclic adaptation 或本研究 finite nonuniform segmentation；
- finite PWL = exact rainflow；Theorem 2 是 segments → ∞ 的收斂結果；
- 完整 electrochemical SOH / calendar-aging / temperature / C-rate / replacement model。

### v7.2 guardrail
若 production code 沒有 \(e_{t,j}\) 這類 **cross-time segment-energy state**，就不得宣稱與 Xu et al. 的 intertemporal PWL cycle-aging formulation 一致，只能稱 hourly discharge-throughput proxy。

論文與口試的正式 attribution 應使用 **“PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL cycle-aging formulation”**；只有在已明確定義此 shorthand 的內部 technical notes 中，才可使用較短的 “Xu-adapted PWL” 稱呼。

**Evidence role:** **B1 mainline formulation source-of-truth**。
---

## [R21] Weber et al. (2021)

**Citation**  
Weber, M., Turowski, M., Çakmak, H. K., Mikut, R., Kühnapfel, U., & Hagenmeyer, V. (2021). *Data-Driven Copy-Paste Imputation for Energy Time Series*. **IEEE Transactions on Smart Grid, 12(6)**, 5409–5419.  
DOI: https://doi.org/10.1109/TSG.2021.3101831

### 支持什麼
- 用相似特徵的 historical blocks 去填補 energy time-series gaps。
- 保留 time-series pattern，比無條件平均更符合資料結構。
- 以人工插入 missing values 驗證 imputation performance。

### 本研究怎麼用
支持 Load reconstruction 的 **pattern/context-matched donor block** 原則，以及 pseudo-gap validation。

### 不能支持
- NTUST 的「same weekday, ±6 weeks, K=1」是 universal setting；
- 直接證明本研究 donor metric 最佳；
- 對 PV 施加 weekday restriction。

**Evidence role:** Blocker 2 load-imputation method direction。

---

## [R22] Jeong, Park & Ko (2021)

**Citation**  
Jeong, D., Park, C., & Ko, Y. M. (2021). *Missing data imputation using mixture factor analysis for building electric load data*. **Applied Energy, 304**, 117655.  
DOI: https://doi.org/10.1016/j.apenergy.2021.117655

### 支持什麼
- building electric-load missing data 是 domain-specific problem。
- building loads 存在可被利用的 recurring/cyclic patterns。
- missing-data method 應依 load structure 驗證，而不是視為一般隨機缺值。

### 本研究怎麼用
支持 Load donor matching 要利用校園週期/日型資訊，並以 site-specific validation 選設定。

### 不能支持
- ±6 weeks 或 K=1 的精確值；
- 直接支持 PV imputation；
- outage-contaminated zeros 必然用某一固定算法處理。

**Evidence role:** Blocker 2 building-load imputation support。

---

## [R23] Demirhan & Renwick (2018)

**Citation**  
Demirhan, H., & Renwick, Z. (2018). *Missing value imputation for short to mid-term horizontal solar irradiance data*. **Applied Energy, 225**, 998–1012.  
DOI: https://doi.org/10.1016/j.apenergy.2018.05.054

### 支持什麼
- 系統比較多種 solar-irradiance missing-data methods。
- 不同 temporal resolution / gap structure 的最佳方法可能不同。
- 使用人工生成 missing periods 做 semi-Monte-Carlo validation。

### 本研究怎麼用
支持 PV/solar-side gap reconstruction 應以 artificial-gap validation 選方法，而非只憑文獻偏好。

### 不能支持
- 「±30 days, no weekday restriction, K=5 mean」是 production requirement；它在 v7.2 只保留為 validated donor benchmark；
- solar irradiance 與 campus PV power 完全等價；
- 長時間跨 midday gap 一律應用單一插值法。

**Evidence role:** Blocker 2 solar-gap validation support；does not determine the production PV reconstruction family。

---

## [R24] Loomans & Alkemade (2024)

**Citation**  
Loomans, N., & Alkemade, F. (2024). *Exploring trade-offs: A decision-support tool for local energy system planning*. **Applied Energy, 369**, 123527.  
DOI: https://doi.org/10.1016/j.apenergy.2024.123527

### 支持什麼
- local-energy-system planning 可定位為 decision-support / trade-off identification，而不是模型替 decision maker 做最後價值判斷。
- 規劃工具可揭露 competing objectives、bottlenecks 與 system interactions。

### 本研究怎麼用
支持 v7.2 將輸出定位為：

> modeled planning requirements / decision evidence

而非 site-specific turnkey engineering recommendation。

### 不能支持
- 因此所有 site constraints 都「不重要」；
- 直接證明 NTUST 不需考慮消防、併網或施工；
- 本研究的 \((\alpha,\beta)\) 數值。

**Evidence role:** Blocker 5 scoping / decision-support framing。

---

## [R25] Liu, Zhang & Ning (2025)

**Citation**  
Liu, Z., Zhang, Y., & Ning, Y. (2025). *Emergency mobile energy storage optimal allocation in microgrid-integrated distribution networks considering economic and resilience benefits*. **Energy, 322**, 135633.  
DOI: https://doi.org/10.1016/j.energy.2025.135633

### 支持什麼
- resilience enhancement 與 economic feasibility 可作並列 decision dimensions。
- energy-storage allocation/planning 可以顯式呈現 cost–resilience trade-off。

### 本研究怎麼用
作為「本研究量化 consequences/trade-offs，而非宣稱單一工程最適部署」的 secondary comparator。

### 不能支持
- NTUST site constraints 應刪除；
- stationary campus BESS 的具體 sizing formula；
- 本研究 Layer A / Layer B 數值。

**Evidence role:** Blocker 5 secondary decision-support comparator。

---

## [R26] Le et al. (2024)

**Citation**  
Le, S. T., Nguyen, T. N., Bui, D.-K., & Ngo, T. D. (2024). *Techno-economic and life cycle analysis of renewable energy storage systems in buildings: The effect of uncertainty*. **Energy, 307**, 132644.  
DOI: https://doi.org/10.1016/j.energy.2024.132644

### 支持什麼
- 近期 building renewable/storage techno-economic study 使用固定 discount-rate assumption；本 blocker audit 將其 5% 設定作為 recent-literature precedent。
- 顯示 building/storage planning 的 financial assumptions 需清楚揭露並做可追溯設定。

### 本研究怎麼用
支持固定 \(r=5\%\) 作為 **modeling precedent** 之一。

### 不能支持
- 5% 是 Taiwan/NTUST 的真實 WACC；
- 5% 是 universal optimal discount rate；
- 不需揭露 financial-assumption limitation。

**Evidence role:** Blocker 7 discount-rate precedent。

---

## [R27] Jahanbin, Abdolmaleki & Berardi (2024)

**Citation**  
Jahanbin, A., Abdolmaleki, L., & Berardi, U. (2024). *Techno-economic feasibility of integrating hybrid battery-hydrogen energy storage system into an academic building*. **Energy Conversion and Management, 309**, 118445.  
DOI: https://doi.org/10.1016/j.enconman.2024.118445

### 支持什麼
- academic-building energy-storage techno-economic context。
- 明確採 **20-year system lifespan** 與 **5% discount rate**。

### 本研究怎麼用
作為 v7.2-retained \(r=5\%\)、\(n=20\) yr 數值設定的近期、場域相近 literature precedent；不控制 real/nominal interpretation。

### 不能支持
- 20-year horizon 等同 cell physical life；
- 5% 是 NTUST-specific financing rate；
- BESS 不需要 replacement / augmentation considerations。

**Evidence role:** Blocker 7 financial-horizon precedent。

---

## [R28] Omoyele et al. (2024) — temporal-resolution design / reliability evidence

**Citation**  
Omoyele, O., Matrone, S., Hoffmann, M., Ogliari, E., Weinand, J. M., Leva, S., & Stolten, D. (2024). *Impact of temporal resolution on the design and reliability of residential energy systems*. **Energy and Buildings, 319**, 114411.  
DOI: https://doi.org/10.1016/j.enbuild.2024.114411

### 支持什麼
- 直接比較 hourly 與 sub-hourly input resolution 對 optimization-based energy-system design、operation、cost 與 reliability 的影響。
- 該案例顯示，hourly averaging 對 aggregate annual cost 的影響可以相對有限，但會把 sub-hourly supply/demand peaks 平滑掉，因而對 PV inverter、battery sizing 與 reliability-related outputs 造成更明顯影響。
- 支持「時間解析度誤差不是所有 output 等比例受影響；power/peak/reliability quantities 應更保守解讀」這個方法邊界。

### 本研究怎麼用
作為 v7.2-retained **hourly temporal-resolution limitation 的主要近期文獻**。本研究因此把 hourly model 定位為 annual planning approximation，而不是 exact sub-hourly power/reliability reproduction。

它與 Taipower 15-min billing rule 的關係是：文獻支持「hourly aggregation 可能漏掉 power-side peak information」；但本研究的 monthly billing-demand proxy 仍由 NTUST 實際帳單自行校準。

### 不能支持
- hourly resolution 對所有 PV–BESS planning problem 都「足夠精確」；
- Omoyele 案例中的誤差百分比可以直接套到 NTUST；
- \(\kappa=1.01037\) 或 through-origin estimator 是該文獻提供；
- 用單一 \(\kappa\) 即可重建真實 15-min BESS dispatch、SOC、ramping 或 outage power adequacy。

### 建議放置
Chapter 3 temporal-resolution / billing-proxy limitation；Chapter 5 limitations / robustness discussion。

**Evidence role:** **Temporal-resolution / A4 claim-boundary evidence**。

---

## [R29] Browne & Williams (2023) — battery-operation sensitivity to time resolution

**Citation**  
Browne, M. H., & Williams, A. A. (2023). *The effect of time resolution on the modelling of domestic solar energy systems*. **Renewable Energy and Environmental Sustainability, 8**, 5.  
DOI: https://doi.org/10.1051/rees/2023003

### 支持什麼
- 比較 grid-connected domestic solar systems 在 hourly、5-min、1-min resolution 下的模擬結果，包含有／無 battery cases。
- 顯示 hourly averaging 會影響 battery behaviour、SOC trajectory、self-consumption / export 等 quantities；該案例中 hourly model 的 battery SOC 偏差可達約 10%。
- 支持「PV–battery operation 對 temporal resolution 敏感，尤其不能把 hourly result 解讀成 sub-hourly operational truth」。

### 本研究怎麼用
作為 R28 的 **recent corroborating evidence**，強化 v7.2 對 battery operation / SOC / power-side outputs 的 limitation wording。

### 不能支持
- NTUST 的 SOC 或 demand-peak 誤差就是 10%；
- hourly resolution 在 annual cost / energy sizing 上一定不可接受；
- Taipower billing-demand 的 exact correction factor；
- 本研究 \(\kappa\) estimator 的來源。

### 建議放置
Chapter 3 temporal-resolution assumption；Chapter 5 limitation，與 R28 並列而不把 residential case 的數值直接外推到 campus scale。

**Evidence role:** **Temporal-resolution corroborating evidence**。

---

---

## [R30] Qi et al. (2025) — system-level battery efficiency precedent

**Citation**  
Qi, N., Huang, K., Fan, Z., & Xu, B. (2025). *Long-term energy management for microgrid with hybrid hydrogen-battery energy storage: A prediction-free coordinated optimization framework*. **Applied Energy, 377**, 124485.  
DOI: https://doi.org/10.1016/j.apenergy.2024.124485

### 直接支持什麼
- Battery model使用典型 system-level stored-energy balance：
  \[
  E^B_{t+1}
  =
  (1-\epsilon\Delta t)E^B_t
  +
  \Delta t
  \left(
  \eta_{B,c}P^{B,c}_t
  -
  \frac{P^{B,d}_t}{\eta_{B,d}}
  \right).
  \]
- 論文將 battery efficiency視為 constant，並在其 test microgrid parameter table設定
  \[
  \eta_{B,c/d}=0.9.
  \]
- 因而提供一個近期 Applied Energy system-level precedent：charge/discharge loss各在 state equation中套一次，且可用 \(\eta_c=\eta_d=0.90\) 作 planning model parameter。

### 本研究怎麼用
A1 mainline鎖定：

\[
\boxed{\eta_c=\eta_d=0.90}
\]

其中 \(p^{ch},p^{dis}\) 定義於 AC/PCS-side，\(e_t\) 為 battery-side stored energy；state equation採與 R30 同型的 efficiency placement。

PNNL system-level round-trip performance只作 boundary-consistency sanity check；**不再用 \(\sqrt{\mathrm{RTE}}\) 強制拆成0.91/0.91**。

### 不能支持
- 0.90/0.90 是所有 LFP、所有 PCS、所有 scale 的 universal engineering standard；
- Qi 的 microgrid hardware boundary與 NTUST turnkey system完全相同；
- 0.90/0.90 必然等於某一特定 PNNL RTE row；
- efficiency curve / C-rate dependence可忽略於所有用途。

**Evidence role:** **A1 direct recent peer-reviewed modeling precedent**。

---

## [R31] Shi et al. (2018) — rainflow cycle-cost convexity / validation support

**Citation**  
Shi, Y., Xu, B., Tan, Y., & Zhang, B. (2018). *A Convex Cycle-based Degradation Model for Battery Energy Storage Planning and Operation*. **2018 Annual American Control Conference (ACC)**, 4590–4596.  
DOI: https://doi.org/10.23919/ACC.2018.8431814  
Open preprint: https://arxiv.org/abs/1703.07968

### 直接支持什麼
- Rainflow cycle counting是 battery/material fatigue cycle identification 的正式方法之一。
- Rainflow-derived cycle degradation cost可具有 convex structure，可進入 planning/operation optimization analysis。
- 提供「以 cycle-depth-sensitive benchmark檢查較簡化 optimization model」的方法論支撐。

### 本研究怎麼用
- **不**把 full rainflow嵌入8760-h sizing objective。
- solve 後對 SOC trajectory做 ex-post rainflow cycle-depth distribution與 degradation-cost benchmark。
- 與 R20 的 Xu-derived PWL cost比較，用來量化 approximation error / model-form robustness。

### 不能支持
- 本研究必須使用 Shi 的 subgradient algorithm；
- rainflow optimization本身是本研究 mainline；
- PNNL LFP cycle-life curve或本研究 \(\lambda_k\)；
- rainflow可補足 calendar aging、temperature、C-rate等未建模因素。

**Evidence role:** **B1 ex-post validation / cycle-counting methodological support**。


## [R32] Ramadhan et al. (2021) — irradiance / weather to PV-power estimation

**Citation**  
Ramadhan, R. A. A., Heatubun, Y. R. J., Tan, S. F., & Lee, H.-J. (2021). *Comparison of physical and machine learning models for estimating solar irradiance and photovoltaic power*. **Renewable Energy, 178**, 1006–1019.  
DOI: https://doi.org/10.1016/j.renene.2021.06.079

### 直接支持什麼
- solar irradiance 與 meteorological inputs 可用來建立 PV-power estimation model。
- 不同 model families（physical / empirical / machine-learning）在 bias 與 RMS-type error 上的表現可能不同。
- PV-power mapping 的 accuracy 需要用 measured PV data 實證評估，而不是因模型較複雜或較「物理」就自動視為較準。

### 本研究怎麼用
支持 v7.2-retained 的方法方向：

> CWA irradiance/weather observations can be treated as explanatory inputs for estimating unavailable PV power, but the exact mapping must be validated against observed NTUST PV data.

它支援「可以比較 CWA→PV mapping family」；**不提供**本研究 `hourly_ghi_ratio_median` 的公式或係數。

### 不能支持
- CWA Taipei station 466920 與 NTUST rooftop irradiance 完全等價；
- `hourly_ghi_ratio_median` 是 literature-standard PV model；
- short-gap accuracy 可直接外推到 1,463 h winter block；
- 本研究的 16.95 kW MAE / 29.74 kW RMSE 是該文獻結果。

**Evidence role:** PV weather/irradiance-to-power modeling direction；supports P1 head-to-head model selection but does not control the exact production model。

---

## [R33] Mayer & Gróf (2021) — PV model-selection sensitivity

**Citation**  
Mayer, M. J., & Gróf, G. (2021). *Extensive comparison of physical models for photovoltaic power forecasting*. **Applied Energy, 283**, 116239.  
DOI: https://doi.org/10.1016/j.apenergy.2020.116239

### 直接支持什麼
- PV power modeling accuracy can materially depend on the selected irradiance / transposition / temperature / PV-model chain。
- MAE、RMSE、bias 等 metrics 不一定同時偏好同一個 model；model selection 應看多個 error diagnostics。
- simpler models need not be uniformly inferior to more detailed models。

### 本研究怎麼用
支持 Script 04b 的 **head-to-head selection logic**：
- 在同一批 target events 上比較 candidate methods；
- 同時檢查 MAE、RMSE、energy bias / event-energy error；
- 不因 method family 的複雜度或名稱而先驗決定 winner。

### 不能支持
- 把 forecasting study 直接視為 missing-data reconstruction validation；
- `hourly_ghi_ratio_median` 的 exact form；
- CWA short-gap model一定優於 donor method；
- NTUST 的 metric values、paired-event wins 或 target-day exclusion rule。

**Evidence role:** PV model-selection / multi-metric validation support；secondary methodological comparator for P1。

---

## [R34] Rahman et al. (2021) — BESS scale-dependent techno-economic modeling

**Citation**  
Rahman, M. M., Oni, A. O., Gemechu, E., & Kumar, A. (2021). *The development of techno-economic models for the assessment of utility-scale electro-chemical battery storage systems*. **Applied Energy, 283**, 116343.  
DOI: https://doi.org/10.1016/j.apenergy.2020.116343

### 直接支持什麼
- 對多種 electro-chemical stationary storage 建立 bottom-up techno-economic models，並在不同 application / capacity ranges 下評估 life-cycle cost與LCOS。
- 其 results明確顯示 storage economic performance會隨 discharge duration / project scale改變；作者將部分成本下降歸因於 **economies of scale**。
- 支持 storage cost不應被理解成與facility scale完全無關的單一 universal unit cost。

### 本研究怎麼用
支持 v7.2 Gate 1 的一般方法原則：

> BESS cost scale should be treated explicitly as an economic assumption rather than ignored or selected retrospectively from the optimized capacity outcome.

本研究因此保留 PNNL 1 MW / 10 MW source cases的 scale distinction。

### 不能支持
- Rahman並未提供本研究 PNNL 1 MW / 10 MW coefficients；
- 不支持「NTUST因為CC=5 MW所以BESS一定屬10 MW bracket」；
- 不直接支持本研究 **10 MW = mainline** 的 exact thesis choice；該角色由 P6 的 ex-ante governance rule控制；
- 不證明用 1 MW 與 10 MW 兩點做 linear interpolation即可得到真實 continuous cost curve。

### 建議放置
Chapter 2 BESS techno-economic cost scale；Chapter 3 Gate 1 / cost-assumption rationale；sensitivity-method justification。

**Evidence role:** **Gate 1 scale-dependence / economies-of-scale literature support; not the numerical cost source.**

---

## [R35] Vatankhah Ghadim et al. (2025) — common-base-year cost normalization

**Citation**  
Vatankhah Ghadim, H., Haas, J., Breyer, C., Gils, H. C., Read, E. G., Xiao, M., & Peer, R. (2025). *Are we too pessimistic? Cost projections for solar photovoltaics, wind power, and batteries are over-estimating actual costs globally*. **Applied Energy, 390**, 125856.  
DOI: https://doi.org/10.1016/j.apenergy.2025.125856

### 直接支持什麼
- 系統整理跨研究、跨年份的 renewable / Li-ion battery cost assumptions。
- 為可比較性，作者明確處理 inflation，將納入比較的 costs **normalise to the value of the U.S. dollar in 2023**。
- 顯示 cost vintage、data age、discount-rate assumptions與 system-boundary differences會顯著影響跨研究 techno-economic comparison。

### 本研究怎麼用
直接支持 Gate 2 的 common-monetary-vintage 原則：

> monetary inputs drawn from different source years should be normalized to a common base-year purchasing-power basis before direct economic comparison.

它是本研究將 PNNL 2023 cost與 case-year tariff轉到共同 **constant NTD-2023** basis 的近期 academic precedent。

### 不能支持
- 不提供 Taiwan CPI / deflator；
- 不提供 FX=31.150；
- 不規定本研究必須選 2023 而不是其他 base year；
- 不證明 5% 是 NTUST real discount rate。

### 建議放置
Chapter 3 economic parameter normalization / monetary-basis subsection；parameter provenance appendix。

**Evidence role:** **Gate 2 recent common-base-year / inflation-normalization evidence.**

---

## [R36] Giovanniello & Wu (2023) — storage optimization with common cost-year basis

**Citation**  
Giovanniello, M. A., & Wu, X.-Y. (2023). *Hybrid lithium-ion battery and hydrogen energy storage systems for a wind-supplied microgrid*. **Applied Energy, 345**, 121311.  
DOI: https://doi.org/10.1016/j.apenergy.2023.121311

### 直接支持什麼
- 建立含 lithium-ion battery sizing / operation 的 techno-economic optimization。
- 文中將來自不同 sources 的 component cost parameters **adjusted to 2020 USD**，objective亦以 annualized system cost in **2020 USD**表達。
- 提供一個 storage-sizing optimization 的直接 precedent：不同 monetary vintages先整理成共同 base-year cost，再進 objective。

### 本研究怎麼用
支持 Gate 2 的 application-level implementation principle：

> a storage sizing objective should compare component and operating costs on a consistent monetary basis.

與 R35互補：R35支持跨研究 cost normalization，R36支持 optimization objective 內的 common-base-year practice。

### 不能支持
- 不提供本研究 tariff deflator或NTD base year；
- 該文自身使用 nominal discount-rate convention，不能直接作本研究 real 5% 的來源；
- 不支持本研究的 Taiwan tariff / contract capacity formulation。

### 建議放置
Chapter 2/3 storage techno-economic modeling；Gate 2 implementation precedent。

**Evidence role:** **Gate 2 storage-optimization common-base-year precedent.**

---

# 10. Authoritative non-journal / technical sources

## [T1] Cole, Ramasamy & Turan (2025) — NREL cost sensitivity

**Citation**  
Cole, W., Ramasamy, V., & Turan, M. (2025). *Cost Projections for Utility-Scale Battery Storage: 2025 Update*. NREL/TP-6A40-93281.  
DOI: https://doi.org/10.2172/2583471

### 支持什麼
- utility-scale lithium-ion storage 的 low / mid / high future cost projections。
- 提供 cost/O&M/lifetime/efficiency 的 external benchmark。

### v7.2 final role
**保留，但降為 sensitivity / robustness benchmark。**

Mainline numerical source 改由 PNNL v2024 控制；NREL 不能與 PNNL 係數混成一套 source-of-truth。

### 不能支持
- NREL projection = NTUST installed cost；
- 直接取代 PNNL v2024 mainline package；
- SOC 10–90%。

**Evidence role:** authoritative external cost sensitivity。

---

## [T2] PNNL Energy Storage Cost and Performance Database v2024 — raw CAPEX/FOM source and scale-case basis

**Source**  
Pacific Northwest National Laboratory (PNNL). *Energy Storage Cost and Performance Database v2024*.  
Project page: https://www.pnnl.gov/projects/esgc-cost-performance  
Database file: https://www.pnnl.gov/sites/default/files/media/file/ESGC_Cost_Performance_Database_v2024.xlsx

### 支持什麼
- PNNL/DOE storage cost-performance database 正式涵蓋 LFP。
- cost metrics 包含 procurement, installation, grid connection, O&M, and end-of-life components。
- 可作 mainline raw cost/performance source。

### 本研究怎麼用
v7.2 cost formulation：

\[
CAPEX_{BESS}=C_EE^N+C_PP^B
\]

\(C_E,C_P,FOM\) 由 PNNL v2024 LFP data 經 thesis-specific 4/6/8/10 h linearization / normalization 建立。Script 11f/11g/11h 已保存 1 MW與10 MW兩套完整 scale packages。

v7.2 **ex-ante role freeze**：
- **10 MW-scale package = mainline**；
- **1 MW-scale package = higher-cost / reduced-scale-economy sensitivity**。

此 role selection 是 thesis governance decision（P6），不是 PNNL 自己指定 NTUST 應採哪一 bracket。PNNL performance data亦可作 A1 的 **system-level round-trip-efficiency sanity check**；但本研究不把某個 RTE row對稱拆成 \(\eta_c=\eta_d=\sqrt{\mathrm{RTE}}\)。A1 的固定 0.90/0.90 直接 modeling precedent為 R30。

### v7.2 extraction / normalization boundary
- 1 MW / 10 MW 是 **source cost-scale cases**，不是 \(P^B\) 的硬 bound，也不表示 optimized BESS power必須等於1或10 MW。
- production fitting window固定為 **4, 6, 8, 10 h**。
- PNNL 2023 USD cost package轉為 **constant NTD-2023**，FX = **31.150 NTD/USD**；exact FX provenance由 P6 / parameter artifact保存。
- \(C_{rep}\) 使用 bracket-specific **DC Storage Block** 4/6/8/10 h arithmetic mean；\(\lambda_k\) 再由各 bracket 的 \(C_{rep}\) + T4 calibration自動產生。
- mainline/sensitivity 必須整包切換 \(C_E,C_P,FOM,C_{rep},\lambda_k\)，不得 cross-bracket mixing。

### 重要 claim boundary
- 任何 energy/power linearized coefficients都不是 PNNL 直接發表的 NTUST coefficients，而是 thesis-derived planning approximations。
- 1 MW / 10 MW 不是 NTUST turnkey quotation。
- 不得依 preliminary或final optimized \(P^B\) 回頭選 package。

**Evidence role:** **PNNL raw cost/FOM source-of-truth and scale-case basis; P6 controls ex-ante mainline/sensitivity roles.**

---

## [T3] PNNL LCOS Estimates v2024 — financial-horizon/context source

**Source**  
Pacific Northwest National Laboratory (PNNL). *LCOS Estimates v2024*.  
https://www.pnnl.gov/projects/esgc-cost-performance/lcos-estimates

### 支持什麼
- 對幾乎所有 technologies，v2024 LCOS 使用的 capital/O&M/performance parameters 對應 PNNL v2024 database，並代表 **2023 values**。
- LCOS financial analysis period 假設 **20 years**。

### 本研究怎麼用
- 支持把 PNNL v2024 cost data 的 base-year/context 寫清楚；
- 為 20-year economic analysis horizon 提供 authoritative precedent。

### 不能支持
- PNNL 直接規定本研究 discount rate = 5%；
- 20 years = battery cell physical lifetime；
- 本研究必須完整複製 PNNL 的 ARMO schedule。

**Evidence role:** **Financial-horizon / cost-vintage evidence; B2 guardrail support**。

---

## [T4] Viswanathan et al. (2022) — PNNL LFP cycle-life calibration

**Citation**  
Viswanathan, V., Mongird, K., Franks, R., Li, X., Sprenkle, V., & Baxter, R. (2022). *2022 Grid Energy Storage Technology Cost and Performance Assessment* (PNNL-33283). Pacific Northwest National Laboratory.  
Official report: https://www.pnnl.gov/sites/default/files/media/file/ESGC%20Cost%20Performance%20Report%202022%20PNNL-33283.pdf

**Exact source location:** Section 4.1.4.2 “Cycle Life,” especially **Table 4.2, report p. 19**, plus the average-DOD interpretation immediately following the table.

### 支持什麼
- LFP cycle life depends on depth of discharge (DOD).
- For reported DOD above 60%, PNNL explicitly distinguishes **reported DOD** from the lifetime **average/effective DOD**, because available energy falls during cycling.
- PNNL Table 4.2 provides the technical relationship used by this thesis:

| Reported DOD in PNNL | Average / effective DOD \(\delta\) used here | LFP cycles to end of life \(N(\delta)\) |
|---:|---:|---:|
| 100% | 80% | 4,800 |
| 80% | 70% | 6,000 |
| 60% | 60% | 8,000 |
| 30% | 30% | 32,000 |
| 5% | 5% | 192,000 |

Therefore the v7.2-retained fixed technical calibration set is:

\[
(\delta,N)=
(0.05,192000),
(0.30,32000),
(0.60,8000),
(0.70,6000),
(0.80,4800).
\]

### Table 4.2 vs Table 4.3 — do not mix
PNNL also presents **Table 4.3** with different cycle counts for its LCOS calculation. Table 4.3 measures cycles to an intermediate state where remaining energy equals the energy available at the average DOD; it is **not the same endpoint definition as Table 4.2 cycles-to-end-of-life**. Therefore values such as 2,400 cycles at 80% average DOD or 4,500 at 70% average DOD must not silently replace the Table 4.2 calibration used by the thesis.

### 本研究怎麼用
T4 controls the **technical cycle-depth calibration only**. The thesis then combines this fixed \(N(\delta)\) relationship with the final economic replacement-cost basis \(C_{rep}\) to derive the PWL wear coefficients:

\[
G(0)=0,\qquad
G(\delta)=\frac{C_{rep}}{N(\delta)}\;(\delta>0),
\qquad
\lambda_k=\frac{G(b_k)-G(b_{k-1})}{b_k-b_{k-1}}.
\]

Thus:
- \(N(\delta)\) = fixed technical calibration from PNNL Table 4.2;
- \(C_{rep}\) = final economic source-of-truth;
- \(\lambda_k\) = thesis-derived economic wear coefficient.

For production, equal-slope adjacent intervals may be **mathematically merged** to the effective breakpoint set:

\[
\boxed{b=(0,\ 0.30,\ 0.60,\ 0.80)}.
\]

This merging does not delete the original five-point provenance. T4 controls the technical curve; R20 controls the intertemporal optimization semantics.

DOD and segment widths are battery-side energy fractions. Because v7.2 defines \(p_t^{dis}\) on the AC/PCS side, degradation accounting must convert discharged energy to battery-side basis using \(p_t^{dis}\Delta t/\eta_d\) (or an algebraically equivalent segment-state formulation).

Unit convention: \(\lambda_k\) is **NTD per battery-side discharged kWh**. This is algebraically equivalent to Xu et al. Eq. (5)–(7), where \(1/\eta^{dis}\) is embedded in the AC-side marginal coefficient \(c_j\)；v7.2 instead keeps \(\lambda_k\) on a battery-side basis and applies \(1/\eta_d\) to AC-side discharged energy in the objective. Do not apply both conventions simultaneously.

### 不能支持
- 直接把任一組 \(\lambda_k\) 稱為 PNNL published coefficients；
- 把 Harry-era \(C_{rep}=5107.57\) TWD/kWh 或 \((0.532,1.596,2.128)\) 鎖成 v7.2 mainline；
- 宣稱本研究已建立完整 calendar-aging / SOH / augmentation / replacement model；
- 把 Table 4.3 LCOS point-estimate cycle counts與 Table 4.2 technical end-of-life calibration 混為同一資料定義。

**Evidence role:** **B1 technical calibration source-of-truth**。

---

## [T5] NIST Handbook 135 / FEMP LCC guidance — constant-dollar / real-rate consistency

**Source**  
National Institute of Standards and Technology (NIST). *Life-Cycle Costing Manual for the Federal Energy Management Program*, Handbook 135 (2022 update / current FEMP methodology lineage).  
DOI: https://doi.org/10.6028/NIST.HB.135e2022-upd1

### 直接支持什麼
- Life-cycle cost analysis可採 **constant dollars** 或 **current/nominal dollars**，但 monetary basis與discount-rate convention必須一致。
- constant-dollar cash flows應搭配 **real discount rate**；current-dollar cash flows應搭配 **nominal discount rate**。
- constant- and current-dollar amounts不應在同一 LCCA 中直接混合。
- constant-dollar方法的優點之一是避免對一般 inflation作逐年 nominal forecast；base-year purchasing power需明確。

### 本研究怎麼用
T5是 v7.2 Gate 2 的 **fundamental accounting-method authority**：

- optimization-facing BESS/tariff monetary terms統一為 constant NTD-2023；
- \(r=5\%\) 正式定義為 **real modeling discount rate**；
- raw case-year nominal Taipower tariff仍保留為 official/bill-validation source，但不得與 constant-dollar BESS cost直接混入同一 objective。

### 不能支持
- NIST並未指定本研究的5%數值；
- 不提供 Taiwan-specific inflation index / tariff deflator；
- 不提供 NTUST WACC；
- 不要求 thesis reporting 必須轉回2025 nominal NTD。

**Evidence role:** **Gate 2 fundamental real/nominal monetary-consistency authority.**

---

# 11. Institutional / project-specific evidence

## [I1] Taipower — 15-minute demand basis

**Source**  
Taiwan Power Company official tariff/rule materials define demand contract capacity using the agreed maximum demand on a **15-minute average** basis.

### 本研究怎麼用
支持：hourly optimization **不能聲稱精確重現 15-min billing maximum**；因此 v7.2 延續使用 site-specific calibrated hourly billing-demand proxy。

### 不能支持
- \(\kappa=1.01037\) 是台電官方係數；
- gross campus Load 可直接代替 historical grid import 做 calibration。

**Evidence role:** **A3/A4 institutional 15-min billing-basis rule**。

---

## [I2] Taipower — high-voltage summer boundary

**Source**  
Taiwan Power Company electricity-pricing information states that high-voltage users' summer tariff period is **May 16–October 15**.

### 本研究怎麼用
支持 v7.2 calendar tagging 必須依日期 boundary，而非以整月 shortcut 標記 summer/non-summer。

### 不能支持
- case-year 每一項 rate 都可用單一 timeless tariff table；
- 免除對 effective-date rate / bill 的 audit。

**Evidence role:** **A3 tariff-calendar rule**。

---

## [I3] NTUST bills + effective-date Taipower detailed tariff tables — A3 tariff source-of-truth

**Source type:** case-study institutional evidence；primary numerical/rule source。

**Primary files currently used**
- Taipower `詳細電價表.pdf` supplied for the case-year tariff/rule audit.
- NTUST monthly Taipower bills for the case-year usage periods.
- Key audited bill example: `11410本校電費849650110(1140901~1140930).pdf`.

### Taipower detailed-tariff rules directly used
For high-voltage three-period TOU service, the detailed tariff explicitly distinguishes:
- regular contract capacity；
- half-peak supplementary contract capacity；
- Saturday-half-peak supplementary contract capacity；
- off-peak supplementary contract capacity。

The official over-contract section defines period-specific cumulative thresholds and states that exceedance across time periods **must not be counted repeatedly**. It further specifies:
- within the first 10% above contract capacity: **2×** applicable basic charge；
- beyond the first 10%: **3×** applicable basic charge。

For the high-voltage three-period tariff table matched to the audited NTUST bill, summer basic-charge rates include:
- regular contract: 223.60 NTD/kW-month；
- half-peak contract: 166.90 NTD/kW-month；
- Saturday-half-peak: 44.70 NTD/kW-month；
- off-peak: 44.70 NTD/kW-month。

### NTUST case setting
v7.2 optimizes **one annual regular \(CC\)**. Supplementary half/Sat-half/off-peak CCs are not optimization decisions and are fixed to the NTUST case setting recorded in the billing registry.

This is a **case-study boundary**, not a claim that Taipower tariff design only permits one contract component.

### Billing-period / billed-maximum audit
Bills must be indexed by **actual usage period**, not bill-title month.

Audited example:
- bill title: 2025/10；
- usage period: 2025/09/01–2025/09/30；
- regular CC: 5000 kW；
- peak / half / Sat-half / off maxima: 4896 / 5016 / 3352 / 3776 kW；
- overall billed maximum:
  \[
  B_{\mathrm{Sep}}=\max(4896,5016,3352,3776)=5016\text{ kW}.
  \]

The same bill reports non-contract basic charge = 5,340.8 NTD. With only half-peak exceeding regular CC:

\[
(5016-5000)\times 166.9\times2
=
\boxed{5,340.8\text{ NTD}},
\]

which is the production billing regression test.

### v7.2 post-audit institutional/accounting additions
- **13b tariff-registry production gate = CLOSED / PASS**；13c pure-season monthly bill-component regression = **CLOSED / PASS**。
- Project implementation uses **`SCHOOL/FROZEN` high-voltage** as an NTUST institutional-treatment label. This is a **project audit/classification label**, not a claim that Taipower publishes a universal tariff category with exactly this name for all schools.
- In the audited case tariff semantics, **non-summer peak = N/A (period not applicable)**. N/A must not be encoded as a zero-rate peak period.
- May/October 50/50 basic-charge transition treatment is retained only as an **NTUST case-validated empirical transition rule** unless/until an official Taipower source explicitly establishes it as a general rule.
- **Subsidy/accounting boundary:** the optimization uses the audited effective billed tariff as the institutional price signal. No separate subsidy credit/debit is added if policy support is already embedded in the applicable tariff/bill; otherwise the same support would be double counted.
- Raw case-year tariff/bill values remain **nominal NTD** for institutional validation. Their later conversion to constant NTD-2023 is an optimization-layer transformation governed by T5 + P6; it must not overwrite the official source layer.

### 本研究怎麼用
I3 controls:
- case-year TOU rates；
- usage-period boundaries；
- one-regular-CC NTUST modeling boundary；
- period-specific basic-charge rates；
- non-duplication logic；
- 2×/3× tiers；
- actual four-period billed maxima used by P2；
- v7.2 raw-nominal validation layer for tariff/bill evidence。

### 不能支持
- bill-title month = usage month；
- four period exceedances should simply be summed；
- all exceedance can always be priced at one universal basic rate；
- Taipower has only one possible contract-capacity component；
- one timeless tariff table may be applied to every historical/future year；
- `SCHOOL/FROZEN` is a universal official Taipower category name；
- non-summer peak should be represented as a zero-price peak period；
- May/October 50/50 is a universal official rule without explicit official text；
- a separate subsidy cash flow must be added on top of an already subsidized/effective billed tariff。

**Evidence role:** **A3 primary institutional source-of-truth**。

---

## [I4] Yunlin District Court 112重訴字第4號 — billed overall-maximum corroboration

**Source**  
臺灣雲林地方法院民事判決，112年度重訴字第4號，給付電費，裁判日期 2023-08-09。原告為台灣電力股份有限公司雲林區營業處；公開裁判資料來源為司法院裁判書系統。

### 直接支持什麼
判決附表的電費計算說明記載：

> 當月份用電最高需量，取尖峰、半尖峰、週六半尖峰及離峰用電最高需量之最大值計算。

同一附表亦記載超過原經常契約容量時，10%以下按2倍、超過10%部分按3倍計收基本電費。

### 本研究怎麼用
- 作為 \(B_m=\max_q B_{m,q}\) 的 **external corroborating record**；
- 支持 P2 不能只取 peak-period maximum。

### 證據層級
I4 是法院案件中的制度/計費說明，**不是取代 I3 的 primary Taipower detailed-tariff source**。若 I4 與官方 effective-date tariff wording有差異，以 I3 為準。

**Evidence role:** A3 billed-maximum corroboration。

---

## [I5] Central Weather Administration (CWA) CODiS / Open Data — weather-data provenance

**Source type:** official institutional observation-data source。

**Official sources**
- CWA CODiS historical observation query service / operating guide (2025-01-02)：supports station-based historical observation queries and CSV export; its daily report is described as hourly data. Service root: https://codis.cwa.gov.tw/
- CWA Open Data Platform, dataset `O-A0091-001` — 日射量資料-署屬氣象站日射量資料：documents CWA station solar-radiation observations and the `SolarRadiation` observation field. Dataset page: https://opendata.cwa.gov.tw/dataset/observation/O-A0091-001

### 本研究怎麼用
- CWA observations are the institutional source for the weather variables used in the PV reconstruction comparison。
- v7.2-retained project pipeline uses CWA station data (project-selected station ID 466920) and retains station / source-column provenance。
- GHI / temperature inputs are aligned to the v7.2-retained interval-start case-year before any PV mapping is fit。

### 重要 timestamp claim boundary
Official CWA material supports the existence and hourly use of CODiS historical observations, but **this registry does not claim that CWA official documentation establishes the project-specific exact `23:59 → next-day 00:00 → minus 1 h` normalization rule**.

That normalization is retained as a **project data-format audit convention** verified against the downloaded CODiS daily files and the 8,760-hour chronology. If a later official CWA document explicitly defines the 23:59 label semantics, add that document here rather than retroactively attributing the current project convention to CWA.

### 不能支持
- station 466920 is an onsite NTUST pyranometer；
- CWA GHI equals rooftop plane-of-array irradiance；
- spatial mismatch is zero；
- CWA data alone validates the final PV reconstruction model；
- short-gap CWA success validates long-block winter reconstruction。

**Evidence role:** official weather-data provenance / institutional source; exact model selection remains P1 project evidence。

---

## [P1] NTUST site-specific preprocessing validation — Scripts 02–05 empirical freeze

**Source type:** project validation / production evidence；not an external literature source。

### P1-A — Load pseudo-gap validation and production selection
Script 02 evaluates reconstruction settings on the two observed outage shapes using **92 pseudo-events / 460 artificial-gap hours**. Candidate donors are same-weekday integer-week offsets and are ranked using same-calendar-day **outside-gap RMSE**.

Selected production rule:

\[
\boxed{\text{same weekday},\ \pm6\text{ weeks},\ K=1}
\]

Production method label:

`same_weekday_pm6weeks_top1_context_rmse`

Validation result:
- MAE = **100.436957 kW**；
- RMSE = **174.069420 kW**；
- signed energy bias = **+0.252411%**；
- mean event absolute energy bias = **436.771739 kWh**。

The former framework candidate \(\pm8\) weeks / \(K=3\) performs materially worse on the same validation design and is **not** a production rule in v7.2.

Script 03 applies the selected rule to exactly **10 outage-contaminated Load hours**:
- 2025-04-19 14:00–16:00：reconstructed event energy = **6,636 kWh**；
- 2025-08-02 09:00–15:00：reconstructed event energy = **18,689 kWh**。

Observed Load remains unchanged; only planning-baseline Load is reconstructed.

### P1-B — PV donor benchmark
Script 04 evaluates donor methods on the two outage shapes using **604 pseudo-events / 3,020 artificial-gap hours**.

Validated donor benchmark:

\[
\boxed{\pm30\text{ days},\ K=5,\ \text{mean},\ \text{no weekday restriction}}
\]

Result:
- MAE = **34.625033 kW**；
- RMSE = **49.998621 kW**；
- signed energy bias = **+1.113409%**；
- mean event absolute energy bias = **135.937748 kWh**。

This is retained as a **validated benchmark**, not the final short-gap production method.

### P1-C — PV donor vs CWA head-to-head
Script 04b compares CWA-based models with the donor benchmark on the **exact same 604 pseudo-events**.

Leakage guardrail:
- the entire target calendar day is excluded from CWA→PV fitting for each pseudo-event；
- CWA observations are normalized to the v7.2-retained interval-start 8,760-hour chronology before comparison。

Selected production model:

\[
\boxed{\texttt{hourly\_ghi\_ratio\_median}}
\]

Production method label:

`cwa_hourly_ghi_ratio_median_leave_target_day_out`

Head-to-head aggregate results:

| metric | CWA `hourly_ghi_ratio_median` | donor `±30d/K5 mean` |
|---|---:|---:|
| MAE (kW) | **16.954595** | 34.625033 |
| RMSE (kW) | **29.741402** | 49.998621 |
| signed energy bias (%) | +1.669484 | **+1.113409** |
| mean event absolute energy bias (kWh) | **51.967974** | 135.937748 |

Paired-event wins out of 604:
- MAE：CWA **486** vs donor 118；
- RMSE：CWA **479** vs donor 125；
- event-energy error：CWA **454** vs donor 150。

Therefore v7.2 short-gap PV production reconstruction uses **CWA `hourly_ghi_ratio_median`**. The donor method remains a comparison benchmark.

### P1-D — Production reconstruction
Script 05 reconstructs exactly **10 real outage-contaminated PV hours**:
- 2025-04-19 14:00–16:00：**211.887706 kWh** reconstructed event energy；
- 2025-08-02 09:00–15:00：**965.124933 kWh** reconstructed event energy。

Observed PV remains unchanged.

### P1-E — Long unavailable PV boundary
The formal case year contains:
- `pre_system` = **600 h**；
- `missing_winter` = **863 h**；
- total long unavailable PV = **1,463 h**。

#### Historical role — under Framework v7.1/v7.2 (superseded; retained as historical evidence)

**HISTORICAL V7.1/V7.2 MAINLINE DEFINITION — SUPERSEDED FOR CURRENT V7.3 METHODOLOGY.** The equation immediately below is retained verbatim as the historical mainline definition that Scripts 02-05 were audited against. It is **not** a current prescription and must not be applied, cited, or implemented as the current mainline.

\[
\boxed{PV_t^{base}=0}\qquad\text{(HISTORICAL v7.1/v7.2 mainline definition — SUPERSEDED)}
\]

for these long-unavailable intervals, described under that historical framework as conservative zero **availability**, not observed physical zero generation.

> **SUPERSEDED — current v7.3 assignment for the same index set.** Under accepted Framework v7.3 §4.1.3 the current mainline assignment for the identical index set \(t\in\{\texttt{pre\_system},\texttt{missing\_winter}\}\) (the same 600 h + 863 h = 1,463 h) is
>
> \[
> PV_t^{base}=\widehat{PV}_t^{winter,recon}
> \]
>
> — the separately validated, weather-informed reconstructed planning baseline. That planning-baseline assignment is **continued unchanged** by accepted Framework v7.4 §4.1.3.
>
> Under Framework v7.3 the zero-availability treatment boxed above was retained as the **conservative stress/sensitivity** case. **That role statement is historical.** Under accepted **Framework v7.4 §36.1** the zero-availability treatment’s **current role is historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion/adjudication decision — it is **not** a mandatory Layer A sensitivity, **not** a mandatory Layer B sensitivity/stress, and **not** an equal-status alternative planning baseline. This Registry records every role with explicit temporal scope; it does not itself decide the methodology. See **[P7]**, **§17** (inherited v7.3 record) and **§20** (current v7.4 alignment).

**Under Framework v7.2 (historical evidence text, unchanged in substance):** the Script-04b result validates only the observed **3 h / 7 h short-gap shapes**. It does **not** validate CWA reconstruction for the 1,463-hour long block. Under that historical framework a CWA winter alternative had first to pass block/month holdout validation, and for as long as that validation was outstanding it remained a separate sensitivity branch.

#### Role reversal decided under Framework v7.3 (historical record of the decision)

**Sensitivity-branch role reversed.** The block/month holdout validation required above was subsequently and separately performed as **Step 17a** (historical verdict `PASS_FOR_SENSITIVITY`, preserved unchanged — see P7-A); a corrected authority-compatible promotion-source candidate (P7-C) and paired Step 17c evidence (P7-D) were then produced. On that separate evidence, and by the Framework v7.3 §4.1.3 / §35 methodology decision, the roles assigned **at that time** were:

- separately validated, weather-informed **reconstructed** full-year PV = **best-estimate planning mainline**;
- prior **zero-winter** treatment = **conservative stress/sensitivity** (**this second assignment is the v7.3-era role; see the current v7.4 role immediately below**).

See **[P7]** for that project evidence, its exact scope, and its role boundary.

#### Current role — under accepted Framework v7.4

**Reconstructed planning baseline — continued unchanged.** Accepted Framework v7.4 §4.1.3 carries the v7.3 planning-baseline assignment forward verbatim: the separately validated, weather-informed **reconstructed** full-year PV remains the **best-estimate planning baseline** over the identical 1,463-hour index set. The accepted planning artifact identity is recorded in [P7] P7-E.

**Zero-winter current role (Framework v7.4 CHANGE A).** The zero-winter (zero-availability) treatment’s **current role is historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion / adjudication decision. Explicitly, under the current methodology authority zero-winter is:

- **not** a mandatory EOB sensitivity;
- **not** a mandatory Layer A sensitivity;
- **not** a mandatory Layer B sensitivity/stress;
- **not** an equal-status alternative planning baseline;
- **not** a mandatory future downstream scenario;

and **no new zero-winter EOB, Layer A, or Layer B solve is required**. The existing reconstructed-vs-zero-winter comparisons (Step 17a holdout validation, corrected Step 17b, Step 17c paired comparison) **remain valid historical project validation / adjudication evidence** and must be preserved in provenance/history; they must not be silently deleted, overwritten, renamed, or removed from the evidence lineage. A zero-winter branch may be restarted only if a **separately justified future reason** is established, and this Registry does not require it. This role update **does not substitute any other sensitivity** for zero-winter.

**Historical truthfulness (preserved, not erased).** Under Framework v7.2 zero-winter was the mainline; under Framework v7.3 it was classified as conservative stress/sensitivity. Both statements remain true **as past-scoped historical provenance** and are retained throughout this Registry (§17, §18, §19, [P1], [P7]). Only current-prescriptive wording that would still make a downstream zero-winter sensitivity **mandatory** is superseded.

**Planning-layer routing (Framework v7.4 CHANGE B).** The single accepted reconstructed full-year planning artifact identity feeds **every** planning-layer consumer — EOB, Layer A, Full81, \(R(\alpha,\beta)\), \(P^{out}\), binding-outage identification/classification, Layer A outage consistency replay, and baseline Layer B. Historical billing calibration and \(\kappa\) reproduction stay in the historical empirical layer on **observed** Load/PV (see [P2] and §20.2). Hybrid routing — crediting reconstruction in economics while reverting Layer A/B adequacy to zero-winter or any other annual PV identity — remains prohibited, and that prohibition is **not** relaxed by the zero-winter role update.

**What is unchanged:** the Scripts 02-05 finding itself — that short-gap validation alone does not certify long-block reconstruction — is not altered, weakened, or re-audited by v7.3. It remains true, and it is precisely why Step 17a's independent validation was required. What changed is the **role assignment** of the separately validated reconstruction, which is a Framework decision (Framework authority), not a re-audit of Scripts 02-05 and not a literature claim.

### Literature / project evidence boundary
- R21–R22 support Load pattern/context-aware imputation and artificial-gap validation。
- R23 supports solar-gap method validation by gap structure。
- R32–R33 support weather/irradiance→PV estimation and multi-metric model-selection logic。
- I5 establishes official CWA weather-data provenance。
- **None** of these sources provides the exact NTUST production rules or numerical validation metrics above. Those are P1 project evidence。

### Contamination-envelope status
The older claim that “core-only vs expanded contamination-envelope reconstruction has already been shown to have no effect on all 81 \(R/P^{out}\) cases” is **not carried forward as a current v7.2 validated finding** under the newly selected production rules.

If a materially plausible expanded recovery envelope remains after final data integration, it should be tested as a targeted preprocessing robustness check. Until then, do not claim invariance of the final 81-point Layer A surface.

**Evidence role:** **Blocker 2 exact site-specific preprocessing source-of-truth; component preprocessing Scripts 01–05 CLOSED/PASSED**。

## [P2] NTUST site-specific billing-demand proxy calibration

**Source type:** project empirical calibration；不是外部文獻係數。

### Canonical historical data boundary
Production calibration uses the **observed columns of the current final integrated annual input (Script 06 production artifact)**:

\[
\boxed{
P_t^{grid,hist}
=
observed\_load\_kw_t
-
observed\_pv\_kw_t
}
\]

The **file name is not the source of truth**. The final integrated artifact has been regenerated from the v7.1/v7.2-retained `load_annual_baseline.*` + `pv_annual_baseline.*`, preserves Script-01 observed columns, uses the exact interval-start 8,760-hour chronology, regenerates calendar/TOU/billing tags, and has passed the Script 06 integration audit.

Any pre-v7 `annual_input_existing_pv.*` file is a **legacy artifact** until regenerated by the current pipeline. If that filename is reused for the final integrated artifact, provenance must show that it was rebuilt by the current audited pipeline rather than inherited from a pre-v7 file.

Calibration must **not** use `baseline_load_kw - pv_available_kw`, because those fields include counterfactual reconstruction and conservative availability assumptions rather than what the historical Taipower bill actually metered.

### Data pairing
For each calibration **usage period** \(m\):

\[
H_m=\max_{t\in m}P_t^{grid,hist}
\]

and

\[
\boxed{
B_m=\max_q B_{m,q}^{15min,bill}
}
\]

where \(q\in\{peak,half,sat\_half,off\}\).

Calibration sample is fixed to **2025/01–2025/10 valid-PV usage months**. 2024/11 (`pre_system`) and 2024/12 (`missing_winter`) remain in the 8760-h simulation but are excluded from coefficient fitting.

### Estimator
The multiplicative billing proxy is:

\[
B_m\approx \kappa H_m
\]

with through-origin least squares:

\[
\boxed{
\kappa=
\frac{\sum_m H_mB_m}{\sum_m H_m^2}
}
\]

The production scripted reproduction is **CLOSED** and yields approximately:

\[
\boxed{\kappa\approx1.01037}.
\]

The exact digits are controlled by the production calibration audit artifact. This value is **not a production hard-code**: any future rerun must rebuild the ten usage-period pairs from the canonical observed grid-import series + billing registry and reproduce the coefficient, or investigate any discrepancy.

### Known reproducibility anchor
For 2025/09 usage:

\[
H_{\mathrm{Sep}}=4985\text{ kW},
\qquad
B_{\mathrm{Sep}}=5016\text{ kW},
\]

so the single-month ratio is approximately 1.0062. This is a diagnostic pair, not the estimator by itself.

### Required production artifacts
`billing_demand_registry.csv` must retain at least:
- usage-period start/end；
- bill-title month；
- regular/supplementary CCs；
- four TOU billed maxima；
- \(B_m=\max_qB_{m,q}\)；
- source bill filename。

`calibrate_kappa.py` must output:
- the ten \(H_m,B_m\) pairs；
- all four billed maxima；
- \(B_m/H_m\)；
- fitted \(\hat B_m=\kappa H_m\)；
- residuals；
- aggregate error diagnostic(s)；
- final \(\kappa\)。

### \(\kappa\) historical-calibration / planning-use claim boundary (Framework v7.4 CHANGE C)

This subsection fixes a **claim boundary only**. The \(\kappa\) value, its estimator, its calibration sample, and its calibration period are **unchanged**; nothing here recalibrates \(\kappa\).

**Preserved production identity (unchanged).**

| Item | Status |
|---|---|
| estimator | **UNCHANGED** — through-origin least squares, \(\kappa=\left(\sum_m H_mB_m\right)/\left(\sum_m H_m^2\right)\) |
| calibration basis | **UNCHANGED** — valid observed periods; **observed** Load/PV; usage-period-aligned actual billed maxima |
| calibration sample | **UNCHANGED** — the ten 2025/01–2025/10 `pv_status=valid` usage months; 2024/11 and 2024/12 remain excluded from coefficient fitting only, not from the 8,760-hour simulation |
| production value | **UNCHANGED** — \(\kappa\approx1.01037\) (rounded presentation), production-pinned implementation identity **`1.0103668594376984`**, governance shorthand `1.0103668594`. These are the **same accepted parameter at different display precision**, recorded here only to fix the claim boundary |
| scripted-reproduction requirement | **UNCHANGED** — this is **not** a production hard-code; any future rerun must rebuild the ten \((H_m,B_m)\) pairs from the canonical hourly input + billing registry and recompute \(\kappa\), with the production calibration audit output remaining the numerical source of truth |

**Epistemic-layer separation (explicit).**

1. Historical \(\kappa\) calibration answers a **historical billing-representation question**: given actual historical measurements and actual bills, how does the hourly grid-import maximum represent the 15-minute billed demand.
2. The accepted reconstructed full-year PV answers a **planning-baseline question**: what best estimate of full-year PV enters the planning-layer optimization.
3. These belong to **different epistemic layers** (§20.2) and therefore **do not contradict each other**: one calibrates a historical billing representation from observed data, the other supplies a model-based planning baseline.
4. **Prohibition:** the accepted reconstructed planning PV **must not** be used to redefine or re-estimate production \(\kappa\), and **must not** replace its calibration sample or calibration target. Historical \(\kappa\) calibration does not silently switch to reconstructed values.

**\(\kappa\) claim boundary (must not be exceeded).**

- \(\kappa\) **is** a billing-demand representation proxy;
- \(\kappa\) **is not** a 15-minute chronology reconstruction;
- \(\kappa\) **does not prove** that hourly BESS sizing captures all instantaneous or sub-hourly physical power peaks;
- \(\kappa\) **is not** proof of exact physical demand chronology;
- \(\kappa\) **does not eliminate** the hourly temporal-resolution limitation. R28–R29 remain relevant limitation/context evidence with their existing roles unchanged, and \(\kappa\) does not override them.

The formal wording remains **“calibrated hourly proxy for the 15-minute billing demand”**; it must never be written as an exact 15-minute billing reconstruction.

### 方法定位
- \(\kappa\) is **NTUST site-specific empirical multiplicative calibration**.
- through-origin LS is the thesis estimator for proportional proxy \(B_m\approx\kappa H_m\); it is not claimed as a coefficient/formula supplied by R28/R29 or Taipower.
- I1 supplies the 15-min institutional measurement basis.
- I3/I4 establish the correct billed-demand target and usage-period semantics.
- R28–R29 explain why hourly peak quantities require caution.

### 不能支持
- \(\kappa\times\) hourly profile = reconstructed true 15-min profile；
- exact 15-min BESS dispatch / SOC / ramping / outage adequacy；
- gross campus Load can replace historical grid import；
- bill-title month may be joined directly to hourly calendar month；
- \(B_m\) should be peak-period maximum when another TOU period is higher。

**Evidence role:** **A3/A4 site-specific calibration lineage; scripted numerical reproduction CLOSED/PASS; future reruns remain provenance-controlled**。

---

## [P3] Production parameter-registry schema — provenance / contamination-control rule

**Source type:** project governance / reproducibility specification；不是外部文獻。

v7.2 production `parameter_registry` 至少保留以下 12 個 machine-readable fields：

| Field | Purpose |
|---|---|
| `parameter_name` | 唯一參數名稱／key |
| `value` | numerical / categorical value |
| `unit` | physical or financial unit |
| `currency` | currency code when applicable |
| `currency_base_year` | monetary vintage / normalization year |
| `source` | primary source or project evidence |
| `source_version` | report/workbook/tariff version or effective date |
| `capacity_basis` | nameplate / usable / AC / DC / kW / kWh basis |
| `annualized` | whether the stored value is already annualized |
| `annualization_method` | CRF / none / source-defined method |
| `mainline_or_legacy` | machine-readable production guardrail |
| `notes` | derivation, transformation, uncertainty, or claim boundary |

### Mandatory rules
1. `mainline_or_legacy` cannot be replaced by free-text labeling alone；v7.2 至少要能機器辨識 mainline / sensitivity / validation / legacy-or-replication role。
2. raw CAPEX, annualized CAPEX, and annual FOM must have different semantics; annual FOM must not receive CRF again.
3. PNNL v2024 source rows / 4-6-8-10 h duration window / scale / linearization / FX=31.150 / constant-NTD-2023 normalization must remain traceable.
4. PWL \(\lambda_k\) is generated from the selected bracket-specific \(C_{rep}\) + T4 cycle-depth table; do not hard-code an independent slope set or mix brackets.
5. Intertemporal degradation implementation must retain R20 segment-state semantics; an hourly-reset implementation is not an acceptable production substitute.
6. B2 accounting structure remains annualized CAPEX + annual FOM + operating costs including cycling wear; do not add a second full replacement/augmentation cash-flow stream unless the accounting framework is explicitly redesigned.
7. legacy lab coefficients are blocked from production unless a replication run explicitly selects them.
8. 10 MW mainline and 1 MW sensitivity must be routed as **full economic packages** \(C_E,C_P,FOM,C_{rep},\lambda_k\); optimized \(P^B\) must never trigger package switching.
9. raw nominal Taipower tariff rows and constant-NTD-2023 optimization rows must be distinguishable by source/version/base-year metadata; normalization must not overwrite the official source values.
10. the 5% discount rate must be tagged as **real modeling rate** when used with constant NTD-2023 cash-flow coefficients.
11. non-summer peak must preserve **N/A / not-applicable semantics**, not silently become zero.
12. no separate subsidy credit/debit may be introduced when the same policy effect is already embedded in the audited effective tariff.

**Evidence role:** production reproducibility, monetary-basis governance, package-role routing, and legacy-contamination control; aligned to Framework v7.2.

---

---

## [P4] A2 reserve-floor / outage-replay semantics — thesis method resolution

**Source type:** project method specification supported conceptually by R7; exact equations are thesis-derived。

### Locked annual normal-operation semantics
For each \((\alpha,\beta)\), annual optimization enforces:

\[
\boxed{
SOC_{\min}E^N+R(\alpha,\beta)
\le e_t\le
SOC_{\max}E^N
}
\]

with annual cyclic state \(e_T=e_0\).

### Locked outage replay semantics
Outage capability is a **separate replay/audit**, not a binary regime inside the annual optimization:

\[
e_0=SOC_{\min}E^N+R
\]

and during outage:

\[
SOC_{\min}E^N\le e_\tau\le SOC_{\max}E^N,
\qquad
p_\tau^{grid}=0.
\]

Reserve is therefore available to be consumed after outage onset. The replay terminal state must remain above technical \(SOC_{\min}\), but does **not** have to restore \(R\).

### Layer A analytical-consistency replay
To validate the analytical reserve definition \(R=\max_sG_s/\eta_d\), Layer A consistency replay disables outage PV-surplus recharge. A binding worst-case window should end near technical SOCmin.

### Reserve-floor robustness
Mainline remains a constant worst-case reserve floor. A perfect-information time-varying reserve floor is **not** promoted to a second research question; it is tested only at:

\[
\alpha=\{0.60,0.80,1.00\},
\qquad
\beta=\{4,12\}
\]

(6 points), with optional \(\beta=8\) follow-up only if material differences appear.

### Evidence boundary
R7 supports preparedness/minimum-SOC economic trade-off, but it **does not provide**:
- this exact \(R(\alpha,\beta)\) formula；
- the separate annual/replay state semantics；
- the six robustness points；
- the no-recharge Layer A consistency audit。

**Evidence role:** **A2 exact thesis-method resolution / anti-overclaim record**。

---

## [P5] A4 optimization auxiliary vs exact billing diagnostic — thesis method resolution

**Source type:** project optimization/reproducibility specification。

### Problem being closed
A demand epigraph variable constrained only by:

\[
D_{m,q}^{opt}\ge \kappa p_t^{grid}
\]

may float above the true maximum whenever the objective does not force tightness. It is therefore unsafe as a reported diagnostic.

### Locked resolution
Optimization may use period-specific demand/exceedance auxiliary variables **only for tariff-cost constraints**.

After solve, exact modeled proxy maxima are recomputed directly from the optimized hourly profile:

\[
\boxed{
D_{m,q}^{exact}
=
\max_{t\in(m,q)}\kappa p_t^{grid}
}
\]

and:

\[
\boxed{
D_m^{exact}
=
\max_qD_{m,q}^{exact}.
}
\]

### Evidence boundary
This is an optimization-model hygiene / reporting rule; it does not require an external paper and must not be falsely attributed to Taipower or R28/R29.

The word **exact** here means exact maximum of the **calibrated hourly proxy profile**, not exact physical 15-min metering reconstruction.

**Evidence role:** **A4 exact implementation/reporting guardrail**。

## [P6] Post-v7.1 economic / tariff integration audit — Scripts 06–13c and v7.2 Gate 1–2 freeze

**Source type:** project production / audit evidence；not an external literature source。

### P6-A — final annual input / billing calibration status
- Script 06 final annual input integration completed and passed the canonical 8,760-hour integration checks.
- Billing-demand calibration scripted reproduction is **CLOSED**；\(\kappa\) remains an NTUST site-specific empirical coefficient, approximately 1.01037, with exact digits controlled by the production audit output.

### P6-B — PNNL dual-bracket economic package construction
Scripts **11f / 11g / 11h** completed the production-oriented PNNL v2024 LFP cost derivation and preserve both source-scale packages. Frozen derivation semantics include:
- fitting window = **4, 6, 8, 10 h**；
- separate energy/power CAPEX coefficients \(C_E,C_P\)；
- annual FOM energy/power treatment；
- replacement-cost basis \(C_{rep}\) = bracket-specific **DC Storage Block** arithmetic mean over 4/6/8/10 h；
- source monetary vintage = 2023 USD；
- currency normalization = **31.150 NTD/USD → constant NTD-2023**；
- bracket-specific \(\lambda_k\) generated from \(C_{rep}\) + T4 cycle-life calibration, not hard-coded legacy slopes。

These scripts intentionally preserve both 1 MW and 10 MW packages and **do not choose the thesis mainline role**.

### P6-C — Xu semantics audit
Script **12a** completed the production-oriented Xu intertemporal segment-state audit. It confirms that production degradation semantics require cross-time segment-energy states and do not revert to the Harry-style hourly-reset proxy. Script 12a does **not** select 1 MW vs 10 MW cost scale.

### P6-D — Taipower tariff / bill regression status
- **13b Taipower tariff registry production gate = CLOSED / PASS**。
- **13c pure-season Taipower monthly bill-component regression = CLOSED / PASS**。
- Audited implementation evidence includes period-specific tariff handling, cumulative/non-duplicative over-contract accounting, and 2×/3× tiers within the audited NTUST case boundary.
- May/October 50/50 basic-charge transition remains **case-validated empirical**, not universal-official, unless a direct official rule is later added.
- Project tariff treatment retains `SCHOOL/FROZEN` high-voltage as an internal institutional label；non-summer peak = **N/A**, not 0-rate.
- subsidy is not modeled as a separate cash-flow item when already embedded in the effective tariff/bill.

### P6-E — Gate 1 CLOSED: ex-ante cost-scale role
Framework v7.2 freezes:

\[
\boxed{\text{10 MW-scale PNNL full package = mainline}}
\]

\[
\boxed{\text{1 MW-scale PNNL full package = cost-scale sensitivity}}
\]

The role is selected **before** EOB / Layer A optimization. It must never be switched based on preliminary or final optimized \(P^B\). The 1 MW / 10 MW labels are cost-scale source cases, not battery-power bounds.

### P6-F — Gate 2 CLOSED: common monetary basis
Framework v7.2 freezes:

\[
\boxed{\text{optimization monetary basis = constant NTD-2023}}
\]

with:

\[
\boxed{r=5\%\ \text{ real modeling discount rate}}.
\]

Rules:
- PNNL package remains on constant NTD-2023 basis；
- official case-year Taipower tariff / bills remain raw nominal NTD for institutional validation and 13b/13c regression；
- a separate optimization-facing tariff layer must convert the official nominal values to constant NTD-2023 using an explicitly sourced price-index/deflator provenance；
- formal thesis optimization results should be reported primarily on the NTD-2023 basis；a 2025 nominal-equivalent may be added only as supplementary reporting and must not feed back into optimization.

### Evidence boundary
P6 controls the **exact thesis/project choices and implementation status**. R34–R36 and T5 support the general methodological rationale but cannot be cited as if they selected:
- 10 MW mainline；
- 1 MW sensitivity；
- FX=31.150；
- a specific Taiwan deflator；
- \(r=5\%\) as NTUST WACC。

### Remaining implementation/validation gates

The v7.3-era form of this list is superseded by the current execution state; the items below are the **current** status (see also §20.4).

- production-interface preflight, including the constant-NTD-2023 Taipower tariff layer；
- **EOB production run: `CLOSED / ACCEPTED`** — `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556`；
- **Layer A core-three production run: `CLOSED / ACCEPTED`** — `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55`；
- **Full81 (the full 81-point Layer A run): `NOT_YET_EXECUTED`** — Full81 and the accepted core-three are **different execution states**; the pending status of Full81 must not be read back onto the accepted EOB or core-three；
- post-solve exact modeled demand maxima；
- ex-post rainflow validation。

**Zero-winter is no longer carried here (Framework v7.4 CHANGE A).** Under Framework v7.3 this list carried a *winter-PV long-block alternative sensitivity* as an outstanding item. That is a **historical** entry. Under accepted Framework v7.4 §36.1 zero-winter is **not** a mandatory sensitivity and **no new zero-winter solve is required**; the existing Step 17a / corrected 17b / Step 17c evidence is retained as historical project validation / adjudication evidence (see [P7]). No substitute sensitivity is introduced in its place.

**Accepted planning input (Framework v7.4 CHANGE B / project-evidence update).** The canonical planning artifact is no longer outstanding: `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` (SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`; role `reconstructed_pv_mainline`; 8,760 rows) is `CLOSED / ACCEPTED` and is the single accepted planning-layer identity (see [P7] P7-E).

These are **not new methodological blockers**.

**Evidence role:** **v7.2 economic/tariff implementation status and Gate 1–2 exact thesis-resolution source-of-truth.**

---

## [P7] Reconstructed-PV mainline promotion evidence -- Steps 17a / corrected 17b / 17c

**Source type:** project validation / production-candidate evidence; not an external literature source. This record documents the project evidence basis for the Framework v7.3 reconstructed-PV mainline/sensitivity role reversal (see Framework Sec 4.1.3, Sec 35). It does not reopen or reinterpret P1's historical Scripts 02-05 finding; it documents what was done **after** that finding, as a separate, later validation stage.

### P7-A -- Step 17a: long-block/monthly holdout validation

**Artifact:** `results/data_audit/winter_pv_holdouts/20260909T042957292822Z_7de1c7a4f4/final_validation_decision.json` (SHA-256 `454a60574d30731fc621ed57d1355911586df4c97aa6b2184ab405015708c594`).

**Design:** `scripts/17a_validate_winter_pv_longblock_holdouts.py` withholds full observed winter-proxy months (January and February 2025) and compares the CWA `hourly_ghi_ratio_median` reconstruction against a within-day hour-of-day climatology-mean baseline on those withheld months, using a pre-registered, frozen comparison protocol (`docs/winter_pv_longblock_sensitivity_protocol_v7_2_2026-09-07.md`, SHA-256 `630c9c20a388fde31d424d8b1e43d99cd05c5d2c9cf51b17e2d36f90fb50f525`) with three hypotheses (H1-H3) and exact binary64 comparison semantics (no numerical tolerance applied to any nonzero difference).

**Historical verdict (unchanged):**

\[
\boxed{\texttt{WINTER\_PV\_RECONSTRUCTION\_VALIDATION = PASS\_FOR\_SENSITIVITY}}
\]

with `H3_primary_pass = true`, `H1_secondary_pass = true`, `H2_secondary_pass = true`, and `all_physical_leakage_completeness_gates_pass = true`. On both withheld months the CWA reconstruction's RMSE and absolute energy bias were materially and strictly lower than the hour-of-day climatology-mean baseline (e.g. H3: RMSE 14.37 vs 56.52 kW; absolute energy bias 1.93 vs 77.07 kWh).

**Scope this establishes:** the CWA `hourly_ghi_ratio_median` reconstruction is sufficiently validated, on the project's own pre-registered long-block holdout design, to serve as a **sensitivity-grade** -- and, under the separately decided Framework v7.3 role reversal, a **best-estimate planning-baseline** -- input for the prolonged unavailable winter block.

**Scope this does NOT establish:**
- observed historical truth for the withheld or the actual 1,463-hour block;
- exact recovery of the missing measurements;
- rooftop-meter observation;
- universal PV-forecasting accuracy outside this project/station/period;
- probabilistic or calibrated reliability of the reconstruction;
- automatic production-mainline authority -- the mainline/sensitivity role assignment is a separate Framework decision (Framework v7.3 Sec 35.1), not an automatic consequence of a validation PASS.

The historical `PASS_FOR_SENSITIVITY` verdict is not rewritten by Framework v7.3; it is reused as part of the evidence basis for the later, separate promotion decision.

### P7-B -- Original Step 17b sensitivity-only artifact (historical; unchanged role)

**Artifact:** `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_protocol_2026-09-07.parquet` (SHA-256 `023cba88416b965c7dedf4139e9a495602039117ecc827e52a372f10a1aad986`).

**Role:** immutable September-07 historical sensitivity-only lineage. It predates the corrected current TOU/calendar authority. It is **not** the promotion-source candidate and is **not** to be identified as a future production source.

### P7-C -- Corrected Step 17b promotion-source candidate

**Artifact:** `data/processed/alternatives/annual_input_v7_2_winter_pv_sensitivity_corrected_authority_project_venv_2026-09-18.parquet` (SHA-256 `1c1dbc265b092415e649bba23232f645f7ba5c74e0f074f2914c1ed7ac9d7cd9`).

**Verified content (read-only inspection of the candidate artifact, 8,760 rows):**
- long-unavailable block: 1,463 rows, split `pre_system` = 600 h and `missing_winter` = 863 h, matching P1-E exactly;
- `observed_pv_kw` over that block is uniformly 0 -- observed columns are untouched, consistent with the framework's immutable-observed-column rule;
- `winter_pv_sensitivity_applied = True` for exactly the 1,463 block rows (and `False` for the remaining 7,297); `winter_pv_sensitivity_method = cwa_hourly_ghi_ratio_median_all_eligible_v7_2` is populated file-wide on all 8,760 rows as a file-level label, so the applied-flag, not the method label, is what delimits the treated block;
- reconstructed `pv_available_kw`/`pv_available_kwh` are positive (nonzero) in **619** of the 1,463 hours, summing to **39,484.422494 kWh** over the block;
- this 39,484.422494 kWh figure is independently corroborated by the Step 17c paired comparison's `pv_available_kwh` delta between the mainline and winter-PV-sensitivity EOB rows (427,105.4351329623 minus 387,621.01263887703 = 39,484.42249408527 kWh).

**Legacy branch-semantics provenance note (reported, not treated as a blocker; artifact not mutated).** This artifact was built as a **v7.2 sensitivity branch**, and several of its self-descriptive provenance fields still carry that construction's semantics rather than describing the reconstruction that now populates `pv_available_kw`/`kwh`. Independently enumerated from the artifact's primary bytes over the 1,463-hour block:

| Field | Value over the 1,463 h block | Consistent with a reconstructed **mainline** artifact? |
|---|---|---|
| `pv_reconstruction_method` | `unavailable_zero_mainline` (×1,463) | **No** — inherited zero-mainline label; does not name the applied method |
| `pv_reconstructed` | `False` (×1,463) | **No** — the block *is* reconstructed in the planning-baseline layer |
| `pv_long_unavailable_assumption` | `True` (×1,463) | **No** — encodes the superseded zero-availability assumption |
| `pv_cwa_model` | null/NaN (×1,463) | **No** — unpopulated for the block (set only on the 10 short-gap hours) |
| `artifact_role` | `winter_pv_sensitivity_only` (file-wide, ×8,760) | **No** — and correctly so: this artifact *is* a sensitivity-branch build |
| `winter_pv_sensitivity_method` | `cwa_hourly_ghi_ratio_median_all_eligible_v7_2` | **Yes** — this is the field that correctly names the applied method |
| `winter_pv_sensitivity_applied` | `True` (×1,463) | **Yes** — correctly delimits the treated block |

For comparison, over the full year `pv_reconstruction_method` reads `observed` (7,287 h), `unavailable_zero_mainline` (1,463 h), and `cwa_hourly_ghi_ratio_median_leave_target_day_out` (10 h — the P1-D short-gap hours), and `pv_reconstructed = True` on exactly those 10 short-gap hours.

**Interpretation and consequence.** These fields accurately describe *how this artifact was constructed* (a v7.2 sensitivity branch) and inaccurately describe *the role v7.3 assigns to its values*. They do not affect the numeric reconstruction, which was independently verified above. Crucially, this was a substantive reason the canonical reconstructed-mainline artifact had to be **newly built** under mainline semantics rather than produced by renaming, re-labelling, or re-pathing this parquet: a rename would have left a file whose own provenance fields assert a sensitivity-branch identity while being routed as production mainline. **That requirement was satisfied**: the separately built, accepted planning artifact is recorded in P7-E and this parquet was not renamed or re-pathed. The artifact must not be mutated in place; it is immutable evidence of the sensitivity-branch run.

**Role (current, under accepted Framework v7.4):** **historical promotion-source lineage / project evidence only**. No forbidden canonical-column mutation was found (observed columns unchanged; reconstruction confined to the planning-baseline `pv_available_*` columns with explicit status/method flags). This artifact is preserved, must not be deleted or rewritten, and **must not be presented as the current canonical planning input**. The accepted planning input is the separately built artifact recorded in **P7-E**; the v7.3-era `NOT_YET_CREATED / NOT_YET_AUTHORIZED` status of that canonical artifact is **historical and no longer current**.

### P7-D -- Step 17c: paired reconstructed-PV EOB / Layer-A sensitivity evidence

**Artifact:** `results/sensitivity/winter_pv_17c/20260918T155044175327Z_3d71b70173/paired_sensitivity_comparison.json` (SHA-256 `b8acd3027c3c1db31bd8840cf0ea6af7f67ea784fcd856bb3dcd2e3317677ca5`); completion manifest SHA-256 `484af5b205fd9ac2cdc047da5f42929f308de3f1f1719f24eeaceb8299ea81ee`.

**Design:** paired EOB and one representative Layer A case (`a0.80_b08`) solved under (i) the **then-mainline v7.2 zero-winter** PV input and (ii) the corrected reconstructed-winter-PV input, which under Framework v7.2 was the **sensitivity** arm and under accepted Framework v7.3 is the **mainline** arm (the run’s own artifact labels `mainline_comparators` / `winter_pv_sensitivity` are v7.2-era labels and are preserved unchanged), holding every other input, tariff, cost package, and solver setting identical (`status: PASS`; monetary basis: constant NTD-2023/year).

**Optimization feasibility:** both paired solves completed successfully (`status: PASS`); this is evidence that the reconstructed-PV input is solver-tractable in the accepted core, not evidence about the true winter generation.

**Economic-impact mechanism (deltas independently re-derived from the artifact's primary bytes).** Crediting the reconstructed winter PV raises available PV by exactly the P7-C block energy in both paired cases, but the *used*-energy delta differs between the two cases by a curtailment-scale amount and must not be stated as identical:

| Quantity (winter-PV-sensitivity minus mainline) | EOB | `a0.80_b08` |
|---|---|---|
| `pv_available_kwh` delta | **+39,484.422494** kWh | **+39,484.422494** kWh |
| `pv_used_kwh` delta | **+39,482.731136** kWh | **+39,484.422494** kWh |
| `pv_curtailment_kwh` | 15.308642 → 17.000000 (**+1.691358**) | 0.0 → 0.0 (**0.0**) |
| `grid_import_kwh` delta | −39,485.597556 kWh | −39,484.422494 kWh |

The available-energy increase is therefore **identical** across the two cases and equal to the P7-C block figure; the EOB `pv_used_kwh` increase is smaller by **1.691358 kWh**, which is exactly the EOB curtailment increase (the identity `Δavailable − Δused − Δcurtailment = 0` holds to floating-point residual in both cases). Grid-import energy falls correspondingly in both. This difference is **curtailment-scale only** — 1.691358 kWh against a 39,484.42 kWh block, i.e. 0.0043% — and does **not** change the scientific interpretation of the paired comparison.

The reported resilience-premium delta between the two paired runs was small relative to the premium's own magnitude (`delta_ntd2023_per_year = -4.655894`, against `mainline_ntd2023_per_year = 41,066,852.95` and `winter_pv_pct_of_eob = 61.64%`).

**Limits of this evidence (explicit, from the artifact's own `interpretation_boundary` field, quoted verbatim):**

> "Observed deltas apply only to this accepted Winter-PV sensitivity input and these two paired cases; they do not establish historical truth or a universal materiality threshold."

**This evidence does NOT establish:**
- a full 81-point robustness result -- only EOB and one representative case (`a0.80_b08`) were paired;
- that the reconstructed-PV mainline promotion is economically material or immaterial in general;
- historical/observed truth for the reconstructed winter values;
- accepted v7.3 production/final results -- Step 17c remains **promotion/adjudication candidate evidence only**, not a v7.3 canonical production run.

### P7-E -- Accepted planning input and accepted production runs (current project-evidence authority)

This subsection records the **current** accepted project-evidence identities that the v7.3-era P7 record could not yet name. It adds no literature source, no equation, no parameter, and no numerical result.

| Artifact | Role | Identity |
|---|---|---|
| `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | **CLOSED / ACCEPTED accepted planning input**; the **single** planning-layer artifact identity for EOB, Layer A, Full81, \(R(\alpha,\beta)\), \(P^{out}\), binding-outage identification/classification, Layer A outage consistency replay, and baseline Layer B | SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`; role `reconstructed_pv_mainline`; rows 8,760 |
| `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556` | Accepted EOB production run; current governance status **CLOSED / ACCEPTED** | run directory; planning-input identity as above |
| `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55` | Accepted Layer A **core-three** run — LOW \((\alpha=0.60,\beta=4\,\mathrm{h})\), CENTRAL \((\alpha=0.80,\beta=8\,\mathrm{h})\), HIGH \((\alpha=1.00,\beta=12\,\mathrm{h})\); current governance status **CLOSED / ACCEPTED** | run directory; planning-input identity as above |

**Execution-time versus governance lifecycle status (do not conflate).** The EOB and core-three **completion manifests retain the execution-time status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`**. That is immutable historical fact about those manifests. The **current governance status** of both runs is **`CLOSED / ACCEPTED`**, established by later governance closure. This Registry does **not** claim the manifests themselves contain `CLOSED / ACCEPTED`, and does not modify them.

**Full81 is a different execution state.** Full81 is **`NOT_YET_EXECUTED`** and is not authorized by this Registry. Core-three being accepted does **not** make Full81 accepted, and Full81 being pending does **not** make core-three pending. The two must never be grouped as jointly pending.

**Claim boundary.** These are **project evidence**, not external-literature facts. No literature source is cited as establishing the accepted planning artifact’s identity, the promotion decision, the exact NTUST parameter values, or any EOB/core-three numerical result.

### Evidence-role summary

| Item | Current role | Not authorized to claim |
|---|---|---|
| Step 17a | `PASS_FOR_SENSITIVITY`; separate long-block/monthly holdout validation evidence; **historical project validation evidence** supporting the reconstructed-PV adjudication | observed truth, exact recovery, standalone completion of canonical promotion |
| Original Step 17b | sensitivity-only historical run/evidence | canonical mainline |
| Corrected Step 17b | **historical promotion-source lineage / project evidence only** | the current canonical planning input, or production authorization |
| Step 17c | paired reconstructed-vs-zero-winter comparison; **historical project validation / adjudication evidence** (Framework v7.4 CHANGE A) | a mandatory current sensitivity; an equal-status alternative planning baseline; the accepted EOB / core-three results; full-81-point robustness |
| Zero-winter treatment (as such) | **historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion/adjudication decision | a mandatory EOB / Layer A / Layer B sensitivity; an equal-status alternative planning baseline; a required downstream scenario; a claim that observed winter generation was physically zero |
| Accepted planning input (P7-E) | `CLOSED / ACCEPTED` single planning-layer identity | observed historical PV; exact ground truth; exact recovery of the unavailable history; online forecast information |
| Accepted EOB / core-three (P7-E) | `CLOSED / ACCEPTED` current governance status | that their own completion manifests contain `CLOSED / ACCEPTED`; Full81 completion |

**Evidence role:** project evidence basis for the reconstructed-PV planning-baseline decision (Framework v7.3 §4.1.3, continued by Framework v7.4 §4.1.3) and for the Framework v7.4 §36.1 zero-winter current-role assignment; plus the current accepted planning-input and production-run identities in P7-E. Step 17a/17b/17c remain **historical validation / adjudication evidence**, not production acceptance evidence.

---

## [L1] Legacy BESS cost / degradation lineage — provenance record only

**Status:** **legacy / reconstructed / not sufficiently verified for mainline citation**。

Historical v4/v5-era values include:
- annualized energy coefficient 813.75；
- annualized power coefficient 694.4；
- CRF 0.07；
- fixed degradation coefficient \(c_{deg}=0.55\)；
- Harry-era conditional replacement-cost basis \(C_{rep}=5107.57\) TWD/kWh and corresponding illustrative hourly-throughput/PWL slopes such as 0.532 / 1.596 / 2.128.

Harry-style hourly-reset segmentation is retained only for replication/lineage. It must not be described as Xu-equivalent intertemporal cycle-depth tracking.

A previously reconstructed candidate lineage for the old cost coefficients was roughly **Amini et al. → Pieter cost table → FX conversion → legacy annualization**, but the chain is not sufficiently verified to present as a current primary source. Preserve it only to reproduce or diagnose old results.

### v7.2 rule
- Do not use these values as academic benchmarks.
- Do not let them control production results.
- The optional constant first-segment \(c_{deg}=0.532\) equivalence check is **not a required Layer A sensitivity**; it may be resurrected only for a clearly labeled legacy/robustness purpose.
- If legacy provenance is later closed from original files, update this record's confidence level rather than silently promoting the value into mainline.

**Evidence role:** historical reproducibility only; **not evidence for current parameter choice**。

---

# 12. Claim-to-source map（v7.2 base, aligned to accepted Framework v7.4）

| 本研究設定／主張 | Primary source(s) | 真正能支持的內容 |
|---|---|---|
| resilience 會改變 sizing / cost | R1, R2 | resilience requirement/value 可改變容量與經濟決策 |
| resilience premium 概念 | **R1** | islandable capability 有增量成本 |
| service continuity 作 resilience metric | R3 | building resilience 可用 service continuity 評估 |
| outage capability 受 load/PV/duration 影響 | R4, R5 | backup capability 是 time- and condition-dependent |
| 固定 design 後做 off-design test | **R6** | out-of-sample fixed-configuration testing 合理 |
| ENS / shortfall 作連續退化指標 | **R6**, R5 | unmet demand / imbalance 可量化失效程度 |
| year-round reserve / min SOC preparedness | **R7** | preparedness 與 economic flexibility 有 trade-off |
| constant reserve floor + separate outage replay semantics | **P4 + R7 boundary** | exact equations/6-point robustness是 thesis method；R7只支持概念 trade-off |
| Taiwan CC 可做 optimization decision | **R8** | CC 是台灣大型用戶正式規劃問題 |
| NTUST one annual regular CC / supplementary CC fixed | **I3** | case-specific tariff boundary；不等於 Taipower制度只有一個CC |
| Taipower over-contract non-duplication + 2×/3× | **I3** | period-specific cumulative thresholds；official rule controls mainline |
| billed overall maximum = max of four TOU maxima | **I3 + I4** | \(B_m=\max_qB_{m,q}\)；不是只取 peak-period maximum |
| BESS TOU / peak shaving | R9, R10 | 平時經濟調度具削峰與套利價值 |
| campus BESS sizing 已有研究 | R10 | campus sizing 本身不是 novelty |
| annual chronology / annual state boundary | R11 | 長期 chronological storage modeling 與 terminal-state rule 有必要；**不支持 outage circular wrap** |
| mainline outage windows 不 circular wrap | model/data-boundary decision + R11 boundary clarification | 只測 complete trajectory 位於 observed case year 內的 valid starts；不是由 R11 直接推導 |
| DG 是合理 resilience counterfactual | **R12**, R13, R5 | diesel / dispatchable generation 可與 storage 形成成本韌性交換 |
| stationary LFP 技術基準 | R16, R17 | commercial LFP 已直接用於 stationary-storage aging research |
| charge/discharge efficiency 0.90/0.90 | **R30 + T2 sanity check** | A1 fixed system-level modeling assumption；不是 universal LFP standard，不由 RTE 對稱拆解 |
| main SOC 10–90% | **R14 + R15** | LFP dynamic-aging evidence + optimization precedent |
| 10–90% 不是 universal standard | R14, R16, R17 | aging 依 cell / SOC / DoD / C-rate / temperature 改變 |
| 20–80% 作 conservative sensitivity | R19, R17 | 較窄 LFP range 有 precedent，但非 universal optimum |
| degradation 受 DoD/C-rate/SOC/temp 影響 | R14, R16, R17, R18 | operating assumptions 會影響 lifetime |
| intertemporal DOD-sensitive PWL degradation | **R20** | Xu-derived cross-time segment-energy states；hourly-reset proxy不屬 final mainline |
| rainflow cycle-depth validation | **R31 + R20** | rainflow作 ex-post benchmark/validation，不嵌入8760-h sizing objective |
| LFP DOD/cycle-life calibration | **T4** | PNNL 2022 Table 4.2 technical data；effective 3-segment merging與\(\lambda_k\)均為 thesis-derived |
| Load matched-donor imputation direction | R21, R22 | pattern/context-aware Load imputation + artificial-gap validation合理；不提供±6/K1 |
| solar-gap validation logic | R23 | solar-side method需依 gap/time resolution與 artificial-gap evidence驗證 |
| irradiance/weather → PV power estimation | R32 | weather/irradiance可作PV-power estimation inputs；exact mapping需實證 |
| PV model-selection / multi-metric comparison | R33 | model choice會影響MAE/RMSE/bias；同一validation set比較多metrics合理 |
| official CWA weather-data provenance | I5 | CODiS historical observations / CSV + CWA solar-radiation institutional source；不證明project-specific 23:59 semantics |
| exact Load production rule | **P1** | same weekday ±6 weeks/K=1/outside-gap RMSE是NTUST empirical production choice |
| PV donor benchmark | **P1 + R23** | ±30 days/K=5 mean是validated benchmark，不是production rule |
| exact PV short-gap production rule | **P1 + R32–R33 + I5 boundary** | CWA `hourly_ghi_ratio_median`由NTUST 604-event head-to-head選出；不是literature constant |
| accepted reconstructed full-year planning PV (incl. 1,463-hour prolonged block) | **P7 (17a + corrected 17b + 17c) + P7-E accepted planning artifact + accepted Framework v7.4 decision** | model-based, weather-informed, separately validated **best-estimate planning baseline**; **not** observed historical PV, **not** exact ground truth, **not** exact recovery of the unavailable history, **not** online forecast information; the **single** accepted artifact identity must feed EOB, Layer A, Full81, \(R(\alpha,\beta)\), \(P^{out}\), binding-outage identification/classification, Layer A outage consistency replay, and baseline Layer B |
| observed-vs-planning PV epistemic routing (Framework v7.4 CHANGE B) | **accepted Framework v7.4 §4.1.1-R / §36.2 decision + P1 + P2 + P7-E** | historical empirical / calibration claims use **observed** data wherever valid (\(P_t^{grid,hist}=L_t^{obs}-PV_t^{obs}\) over valid observed-PV periods); planning / counterfactual claims use the **accepted reconstructed full-year PV**; **no hybrid routing**. Registry records the routing as a claim/evidence boundary only — the equations and routing enforcement remain Framework/implementation authority |
| zero-winter annual treatment — **current role** (Framework v7.4 CHANGE A) | **P1 + P7 (Step 17a / corrected 17b / Step 17c) + accepted Framework v7.4 §36.1 decision** | **historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion/adjudication decision; **not** a mandatory EOB/Layer A/Layer B sensitivity, **not** an equal-status alternative planning baseline, **not** a required downstream scenario; no new zero-winter solve is required; the 1,463 h zero treatment was conservatively **assigned zero availability due to unavailable observations**, never a claim of physically zero generation |
| zero-winter annual treatment — **historical roles** | **P1 + Framework v7.2 mainline role + Framework v7.3 conservative stress/sensitivity role** | past-scoped historical provenance, still true as history: mainline under Framework v7.2, conservative stress/sensitivity under Framework v7.3; short-gap validation alone could not be extrapolated to long-block reconstruction -- that extrapolation gap is why P7/17a's separate holdout validation was required |
| PNNL v2024 raw CAPEX/FOM + scale cases | **T2** | LFP installed-cost/O&M source；1/10 MW linearized packages為 thesis-derived |
| BESS cost depends on project/application scale | **R34 + T2** | economies of scale / scale-dependent storage economics require explicit treatment; does not select NTUST bracket |
| 10 MW mainline / 1 MW sensitivity | **P6 + T2 + R34 boundary** | exact ex-ante thesis role freeze; not selected from optimized \(P^B\); full-package swap required |
| 4/6/8/10 h cost fitting + DC Storage Block \(C_{rep}\) + FX 31.150 | **P6 + T2/T3** | exact project derivation/provenance; not literature constants |
| common base-year monetary normalization | **R35 + R36 + T5** | different cost vintages should be harmonized before economic comparison/optimization |
| optimization monetary basis = constant NTD-2023 | **P6 + T5 + R35–R36** | exact thesis base-year choice + literature/method consistency rationale |
| 5% interpreted as real discount rate | **P6 + T5 + R26–R27** | 5% numerical precedent from R26/R27; real interpretation follows constant-dollar consistency, not NTUST WACC |
| raw Taipower nominal layer vs constant-2023 optimization layer | **I3 + T5 + P6** | official values retained for validation; normalized copy used in objective |
| SCHOOL/FROZEN / non-summer peak N/A / subsidy boundary | **I3 + P6** | project label and accounting semantics; N/A≠zero; no duplicate subsidy cash flow |
| NREL cost projection | T1 | 只作 alternative sensitivity/benchmark，不控制 mainline |
| 20-year economic horizon | **T3 + R27** | PNNL LCOS 與 academic-building study 提供 precedent；不是 physical-life gate |
| B2 accounting structure | **T2–T3 + P3** | annualized CAPEX + annual FOM + operating wear維持；B1只改\(C^{deg}\)計法，不新增 full replacement stream |
| fixed discount rate 5% numerical precedent | R26, **R27** | recent literature precedent；不是 NTUST WACC，real/nominal interpretation由T5+P6控制 |
| \(CRF=0.0802426\) | derived from \(r=5\%, n=20\) | 計算結果，不是文獻直接發布參數 |
| hourly temporal-resolution limitation | **R28, R29** | hourly aggregation can smooth sub-hourly peaks and distort power/battery-operation/reliability quantities; case-specific errors are not transferred to NTUST |
| 15-min billing basis | **I1** | Taipower institutional rule |
| \(\kappa\approx1.01037\) (production-pinned `1.0103668594376984`) | **P2 + I3 + I1 + P6** | production scripted reproduction CLOSED；exact digits由audit output控制，仍為site-specific proxy; the rounded, shorthand, and full-precision forms are the **same accepted parameter at different display precision** |
| \(\kappa\) historical calibration uses observed data only (Framework v7.4 CHANGE C) | **P2 + I1 + I3 + I4 + accepted Framework v7.4 §4.3.1-K / §36.3** | calibration uses observed valid historical Load, observed valid historical PV, observed historical billing/usage-period evidence, and the accepted billing-demand calibration procedure; the accepted reconstructed planning PV **does not** redefine, re-estimate, or retroactively replace observed historical PV in \(\kappa\) calibration |
| \(\kappa\) is billing proxy, not 15-min reconstruction | **P2 + R28, R29** | proxy corrects monthly billed-demand representation only; \(\kappa\) is **not** a 15-minute chronology reconstruction, **not** physical sub-hourly power validation, **not** evidence that hourly BESS sizing captures all instantaneous peaks, and **not** proof of exact physical demand chronology; R28–R29 hourly-resolution limitations remain in force and are not overridden by \(\kappa\) |
| cost-facing demand auxiliaries vs exact reported maxima | **P5** | solve後從 optimized hourly proxy profile ex-post重算；不報 floating epigraph |
| full production parameter schema | **P3 + P6** | 12-field provenance + package-role / monetary-basis / legacy-contamination guardrails |
| high-voltage summer 5/16–10/15 | **I2** | Taipower official calendar rule |
| site feasibility 不進 mainline | R24, R25 + thesis scope decision | model提供 decision evidence；工程限制仍可事後 overlay，不代表限制不存在 |

---

# 13. 最優先閱讀順序

1. **Xu et al. (2018), IEEE Transactions on Power Systems — R20**：B1 intertemporal PWL degradation mainline；一定要讀 multi-interval segment-state equations與 rainflow benchmark。
2. **PNNL 2022 — T4**：LFP effective-DOD / cycle-life calibration；Table 4.2 與 Table 4.3 endpoint distinction。
3. **PNNL v2024 — T2/T3 + P6**：current BESS raw cost/FOM source、4/6/8/10 h extraction、1 MW/10 MW full-package provenance、2023 cost vintage。
4. **Rahman et al. (2021), Applied Energy — R34**：Gate 1 economies-of-scale / scale-dependent storage-cost rationale；不負責選 NTUST bracket。
5. **Vatankhah Ghadim et al. (2025), Applied Energy — R35 + Giovanniello & Wu (2023), Applied Energy — R36**：Gate 2 common-base-year normalization與storage-optimization precedent。
6. **NIST Handbook 135 — T5**：constant dollars ↔ real discount rate；current/nominal dollars ↔ nominal discount rate 的 fundamental consistency rule。
7. **P6 post-v7.1 production audit**：10 MW mainline / 1 MW sensitivity、FX 31.150、bracket-specific \(C_{rep}/\lambda_k\)、13b/13c status、constant NTD-2023 exact thesis freeze。
8. **Qi et al. (2025), Applied Energy — R30**：A1 \(\eta_c=\eta_d=0.90\) direct precedent。
9. **Taipower detailed tariff + NTUST bills — I3**：usage period、four-period maxima、one-regular-CC case boundary、non-duplication、2×/3×；raw nominal validation layer。
10. **Yunlin District Court 112重訴字第4號 — I4**：四時段最高需量取 overall max 的 external corroboration。
11. **Shi et al. (2018) — R31**：rainflow cycle-based ex-post validation support。
12. **Son et al. (2024) — R7 + P4**：preparedness/minimum-SOC trade-off；exact reserve/replay equations屬 thesis method。
13. **Omoyele et al. (2024) + Browne & Williams (2023) — R28–R29 + P2**：hourly limitation與site-specific billing proxy boundary。
14. **Pickering & Choudhary (2021) — R6；Laws et al. (2018) — R1**：Layer B fixed-design testing與resilience premium。
15. **P1 + R21–R23 + R32–R33 + I5**：NTUST Load/PV preprocessing exact empirical freeze與literature boundary。
16. **R14–R19**：LFP SOC / aging assumptions與technical sensitivity。
17. **R26–R27**：5% / 20-year financial modeling precedent；不能取代 T5 的 real/nominal accounting rule。

---

# 14. Claim boundary：論文安全寫法

## 可以寫

- “The thesis adopts 10–90% SOC as a **representative planning assumption** for stationary LFP BESS.”
- “The 20–80% case is a **deliberately more restrictive technical sensitivity**, not a universal optimum.”
- “The mainline battery state model uses fixed **\(\eta_c=\eta_d=0.90\)** as a system-level planning assumption with recent peer-reviewed precedent; it is not claimed as a universal LFP efficiency standard.”
- “The annual model maintains a constant worst-case preparedness reserve above technical SOCmin, while outage adequacy is checked in a **separate replay that may consume that reserve**.”
- “NTUST billing is indexed by **actual usage period**, and monthly billed maximum demand is the maximum of the four TOU-period maxima.”
- “Taipower over-contract charging follows **period-specific cumulative thresholds, non-duplication, and 2×/3× tiers**.”
- “Reported monthly demand maxima are recomputed **ex post from the optimized calibrated-hourly proxy profile**; optimization epigraph variables are not treated as exact diagnostics.”
- “The mainline cycling-wear model uses a **PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL cycle-aging formulation** with cross-time segment-energy states; it is not a full electrochemical lifetime model.”
- “Rainflow counting is used **ex post as a cycle-depth/cost benchmark**, not embedded in the annual sizing objective.”
- “A Harry-style hourly-reset segment penalty is treated as a **throughput proxy/legacy formulation**, not as Xu-equivalent multi-interval DOD tracking.”
- “Load reconstruction follows literature-supported pattern/context-aware imputation principles, while the exact **same-weekday ±6 weeks / K=1** production rule is selected by NTUST-specific pseudo-gap validation.”
- “For short PV gaps, CWA irradiance-based reconstruction was selected through a **head-to-head artificial-gap validation on the same 604 pseudo-events**; the `±30 days / K=5 mean` donor remains a validated benchmark.”
- “The selected `hourly_ghi_ratio_median` model is a **site-validated empirical mapping**, not a literature-standard PV model.”
- "Under Framework v7.2, the 1,463-hour pre-system/winter PV-unavailable block was treated as **conservative zero availability** in the mainline; short-gap validation alone was not used as evidence for long-block reconstruction."
- "Under Framework v7.3, the 1,463-hour prolonged winter PV block was represented using a **separately validated, weather-informed reconstruction** (Step 17a long-block holdout validation; corrected Step 17b/17c evidence) as the **best-estimate planning mainline**, and the prior zero-winter treatment was retained as a **conservative stress/sensitivity** case." *(historical, past-scoped statement of the v7.3 role assignment)*
- "Under accepted Framework v7.4, the prolonged unavailable winter PV block is represented, **in the planning layer**, using a separately validated weather-informed reconstruction as the **best-estimate planning baseline**. The prior zero-availability treatment is retained as **historical conservative validation evidence** supporting that representation decision; it is **not** a required alternative planning baseline and **not** a required downstream sensitivity. Reconstructed values are model-based planning estimates rather than observed historical PV measurements."
- "The zero-winter treatment conservatively **assigned zero PV availability because observations were unavailable**; it was never a finding that physical generation was zero."
- "The thesis distinguishes a **historical empirical / calibration layer**, which uses observed data wherever valid, from a **planning / counterfactual model layer**, which uses the accepted reconstructed full-year PV; no hybrid routing between the two is used."
- "All planning-layer results — EOB, Layer A, Full81, \(R(\alpha,\beta)\), \(P^{out}\), binding-outage classification, outage consistency replay, and baseline Layer B — share **one** accepted planning-input identity, so no comparison between them is affected by a PV-identity asymmetry."
- "The reconstructed planning PV is a **retrospective planning-baseline construction**; it is not online forecast information and confers no operator information advantage at the time of any historical event."
- "The billing-demand coefficient \(\kappa\) is calibrated **only** on observed historical Load, observed historical PV, and observed billing/usage-period evidence; the accepted reconstructed planning PV does not redefine or re-estimate it."
- "\(\kappa\) is a **billing-demand representation proxy**. It is not a 15-minute chronology reconstruction, does not demonstrate that hourly sizing captures sub-hourly physical power peaks, and does not remove the hourly temporal-resolution limitation."
- "The winter PV reconstruction is a **model-based, weather-informed, separately validated estimate for planning use**; it is not observed meter data, not exact ground truth, and not an exact recovery of the missing historical series."
- "The same reconstructed full-year planning-baseline PV feeds EOB/economic optimization, Layer A's \(R(\alpha,\beta)\), \(P^{out}(\alpha)\), binding-window classification, and analytical-consistency outage replay, and baseline Layer B; a hybrid route crediting reconstruction only in economics while zeroing it in Layer A/B adequacy is not authorized."
- "Deterministic historical-start adequacy under the reconstructed-PV mainline is **conditional on the accepted weather-informed planning estimate**; it is not adequacy under observed winter PV, not a probabilistic reliability claim, and not evidence of physical islanding capability."
- “The annual optimization uses a cyclic terminal battery-state boundary, while outage windows are restricted to **fully observed valid starts within the case year**.”
- “The BESS mainline cost package is **derived from PNNL v2024 LFP cost data**; the linear energy/power coefficients are thesis-derived planning approximations.”
- “The PNNL **10 MW-scale full cost package is selected ex ante as the mainline economic assumption**, while the 1 MW-scale full package is retained as a higher-cost scale-economy sensitivity; neither label is a hard BESS-power bound.”
- “The cost-scale role is fixed **before optimization** and is not selected from preliminary or final optimized \(P^B\).”
- “All optimization-facing monetary terms are expressed in **constant NTD-2023**, while raw case-year Taipower tariff/bill values are retained in nominal NTD for institutional validation.”
- “The 5% discount rate is treated as a **real modeling discount rate** to remain consistent with the constant-dollar objective; it is not claimed as NTUST’s actual WACC.”
- “The project label `SCHOOL/FROZEN` documents the NTUST tariff treatment used in the audit; it is not presented as a universal official Taipower category name.”
- “For the audited case, non-summer peak is treated as **N/A (not applicable), not as a zero-rate peak period**.”
- “No separate subsidy cash-flow term is added when the effective tariff/bill already embeds the relevant policy support, avoiding double counting.”
- “NREL 2025 cost projections are used as an **external cost sensitivity**, not as the mainline NTUST cost source.”
- “The 5% discount rate and 20-year horizon are **transparent financial modeling assumptions with recent literature precedent**, not estimates of NTUST’s actual financing conditions or the battery’s physical lifetime.”
- “B1 changes the calculation of cycling wear only; the B2 accounting structure remains **annualized CAPEX + annual FOM + operating costs**, without an additional full replacement cash-flow stream.”
- “The hourly model is treated as an **annual planning approximation**; recent temporal-resolution studies show that power-, SOC-, and reliability-related outputs can be more sensitive to sub-hourly variation than aggregate annual quantities.”
- “The hourly model uses a **site-specific calibrated proxy** for Taipower’s 15-minute billing demand.”
- “The billing-proxy coefficient is estimated from **NTUST historical grid import and actual billed maximum demand**; it is not a universal literature coefficient.”
- “Layer B evaluates **conditional fixed-design capability under structured off-design scenarios**.”
- “Layer B structured-scenario coverage is **not an outage-success probability**.”
- “The DG module is a **deterministic counterfactual sizing comparison**, not an outage-probability model.”
- “BESS results are **modeled planning requirements**; physical deployment feasibility is an implementation-stage overlay outside the mainline optimization.”

## 不要寫

- “LFP 的標準 SOC 就是 10–90%。”
- “20–80% 一定比 10–90% 更健康。”
- “PNNL round-trip efficiency 可以直接對稱拆成 \(\eta_c=\eta_d=\sqrt{RTE}\)，所以0.91/0.91就是正式值。”
- “\(\eta_c=\eta_d=0.90\) 是所有LFP的標準效率。”
- “Harry 的 hourly-reset PWL 就是 Xu et al. (2018) 的完整 intertemporal formulation。”
- “Xu-derived PWL 與 full rainflow 完全等價。”
- “Xu et al. (2021) 是本研究 PWL degradation 的方法來源。”
- “PNNL 直接公布 402.50/232.65 或 362.17/173.10 這組 NTUST sizing coefficients。”
- “因為 optimized BESS 最後接近 X MW，所以回頭決定該用 1 MW 或 10 MW PNNL cost package。”
- “10 MW mainline 代表模型強迫 BESS power = 10 MW，或 1 MW sensitivity 代表 power上限1 MW。”
- “Rahman et al. (2021) 或 PNNL 指定 NTUST 一定要採10 MW package。”
- “2023 PNNL equipment cost可以直接和2024/2025 nominal Taipower tariff相加而不處理monetary vintage。”
- “5% 是 NIST / PNNL / cited Q1 paper提供的 NTUST real WACC。”
- “正式 tariff normalization可以覆寫原始 official nominal tariff rows。”
- “non-summer peak = 0 NTD/kWh。”
- “May/October 50/50 basic-charge treatment是已由官方條文明確證明的 universal Taipower rule。”
- “已反映在 effective tariff中的政策補助，還要再另外從 objective扣一次 subsidy credit。”
- “NREL BESS cost 就是 NTUST 安裝成本。”
- “20-year financial horizon 代表電池必須 physically survive 20 years。”
- “annualized CAPEX + cycling wear 之後還應無條件再加入完整 replacement cash-flow stream。”
- “PNNL 規定本研究 discount rate 應該是 5%。”
- “文獻建議 \(\alpha=0.8\) 或 \(\beta=8\) h。”
- “文獻規定 Load 必須 ±6 weeks/K=1，或 CWA `hourly_ghi_ratio_median` 是標準 PV reconstruction model。”
- “因為 CWA 在 3 h / 7 h pseudo-gaps 勝出，所以 1,463 h winter block 也已被驗證可直接重建。”（Note: under v7.3 the 1,463 h block promotion is supported by the **separate** Step 17a long-block holdout validation, not by extrapolating the short-gap result -- see P7-A.）
- "The reconstructed winter PV values are observed meter data, exact ground truth, or an exact recovery of the missing historical series."
- "Step 17a's `PASS_FOR_SENSITIVITY` verdict alone authorizes production-mainline promotion." (the mainline/sensitivity role assignment is a separate Framework decision, not an automatic consequence of a validation PASS)
- "Step 17c's paired EOB/`a0.80_b08` comparison demonstrates the full 81-point Layer A resilience surface is materially unaffected (or affected) by the reconstruction." (only EOB and one representative case were paired)
- "The corrected Step 17b artifact is the current canonical planning input." (it is **historical promotion-source lineage / project evidence only**; the accepted planning input is the separately built artifact recorded in P7-E)
- "Under the current methodology, a zero-winter EOB, Layer A, or Layer B sensitivity is still required." (it is not — Framework v7.4 §36.1; no new zero-winter solve is required, and no substitute sensitivity replaces it)
- "Zero-winter is an equal-status alternative planning baseline." (its current role is historical conservative validation / provenance evidence)
- "Framework v7.3 never treated zero-winter as a conservative stress/sensitivity." (it did; that past-scoped statement remains true as historical provenance and must not be erased)
- "Reconstructed planning PV may be substituted for observed PV in historical \(\kappa\) calibration, bill regression, or any other historical empirical check." (prohibited — observed data is used wherever valid in the historical empirical layer)
- "Economics may credit reconstructed winter PV while Layer A/Layer B adequacy reverts to zero-winter or another annual PV identity." (hybrid routing is not authorized; the zero-winter role update does not relax this)
- "The reconstructed planning PV is online forecast information, or gave the operator an information advantage during a historical outage." (it is a retrospective planning-baseline construction)
- "\(\kappa\) validates the model's sub-hourly physical power behaviour, or proves the exact physical demand chronology." (it does neither)
- "The accepted EOB and core-three completion manifests record `CLOSED / ACCEPTED`." (those manifests record the execution-time status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`; the `CLOSED / ACCEPTED` state is a later, separate governance lifecycle status)
- "Full81 and the core-three are both pending." (the core-three is `CLOSED / ACCEPTED`; only Full81 is `NOT_YET_EXECUTED`)
- “CWA 官方文件已證明本研究 `23:59 → next-day 00:00 → interval-start` 的全部 timestamp semantics。”
- “annual cyclic SOC boundary 代表 outage 可以從年末 circular wrap 回年初。”
- “hourly resolution 足以精確重現所有 BESS power、SOC、reliability 或 15-min peak quantities。”
- “帳單標題月份就是實際用電月份。”
- “月最高需量只要取尖峰時段 maximum。”
- “四個 TOU period 的超約量可以直接全部相加。”
- “只要取 overall max exceedance，再乘一個 universal basic rate 就一定能重現台電超約費。”
- “optimization 裡的 demand epigraph variable 就一定等於真實 maximum。”
- “\(\kappa=1.01037\) 是台電官方換算係數。”
- “\(\kappa\times\) hourly profile 就是真實或重建的 15-min profile。”
- “Omoyele 2024 或 Browne & Williams 2023 提供了本研究的 \(\kappa\) 公式／係數。”
- “Layer B cases 表示真實 reliability = X%。”
- “50% DG 是普遍最適 sweet spot。”
- “沒有 site constraint 代表工程限制不重要或已證明可部署。”
- “本研究是第一個 resilience-constrained microgrid sizing model。”

---

# 15. 官方／場域／parameter evidence 狀態（v7.2 base, current status aligned to accepted Framework v7.4）

## 已從 blocker 轉為 locked evidence / parameter-registry item

- **A1 efficiency**：\(\eta_c=\eta_d=0.90\) 已鎖定；R30 是 direct peer-reviewed precedent，T2/PNNL performance data只作 system-level sanity check；0.91/0.91 不再是 mainline。
- **A2 reserve/replay semantics**：constant worst-case reserve floor + separate outage replay 已鎖定；exact equations/6-point robustness由 P4 保存，R7只支持 preparedness trade-off。
- **Taiwan 15-minute maximum-demand settlement basis**：由 Taipower official rule 支持；hourly model不宣稱 exact 15-min reconstruction。
- **A3 tariff/CC/over-contract**：I3 已鎖定 usage-period indexing、one-regular-CC NTUST case boundary、four TOU maxima、non-duplication、2×/3×；I4作 billed-overall-max external corroboration。
- **High-voltage summer definition = 5/16–10/15**：由 Taipower official pricing information 支持。
- **\(\kappa\approx1.01037\)**（production-pinned `1.0103668594376984`；governance shorthand `1.0103668594`；同一 accepted parameter 的不同顯示精度）：不是文獻值；P2 scripted reproduction 已 **CLOSED**，final source-of-truth為 production calibration audit output；future rerun仍須由 canonical inputs重建。**Framework v7.4 CHANGE C claim boundary**：historical calibration 只用 observed Load/PV 與 observed billing evidence，accepted reconstructed planning PV 不得用來重新定義或重新估計 \(\kappa\)；\(\kappa\) 是 billing-demand representation proxy，不是 15-min chronology reconstruction，也不消除 hourly temporal-resolution limitation（見 [P2]、§20.3）。
- **A4 exact billing diagnostics**：P5 已鎖定 post-solve exact maxima of the calibrated hourly proxy；不報 floating optimization epigraph。
- **hourly temporal-resolution limitation**：R28–R29 為主要近期文獻；它們不提供 \(\kappa\)，也不消除 sub-hourly limitation。
- **Blocker 2 / preprocessing empirical freeze**：P1 已以 Scripts 02–05 更新。Load production = same weekday ±6 weeks/K=1；PV donor ±30d/K5 mean = benchmark；PV short-gap production = CWA `hourly_ghi_ratio_median`；10 Load + 10 PV outage hours已重建；1,463 h long unavailable PV under **historical v7.2 mainline** treatment used zero availability。**Under Framework v7.3（見 P7）**，同一 1,463-hour block改用 separately validated reconstructed PV作 best-estimate planning baseline，先前 zero-availability treatment當時改列 conservative stress/sensitivity。**Under accepted Framework v7.4 §36.1（current）**，reconstructed planning baseline 延續不變，而 zero-availability treatment 的 **current role 為 historical conservative validation / provenance evidence**，不再是 mandatory sensitivity。這些都是 evidence-role update，不是 Scripts 02–05 re-audit。
- **PV reconstruction literature boundary**：R23保留solar-gap artificial-gap validation角色；R32–R33新增weather/irradiance→PV與multi-metric model-selection evidence；I5新增CWA官方資料來源。exact production model仍由P1控制。
- **Reconstructed-PV planning-baseline promotion**：P7（Step 17a `PASS_FOR_SENSITIVITY` + corrected Step 17b promotion-source lineage + Step 17c paired evidence）+ Framework v7.3 §35 decision，由 accepted Framework v7.4 §4.1.3 延續。**Current status（取代 v7.3-era 的 `NOT_YET_*`）**：accepted planning input = `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`（SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`；role `reconstructed_pv_mainline`；8,760 rows）**CLOSED / ACCEPTED**；corrected Step 17b parquet = historical promotion-source lineage only；見 [P7] P7-E。
- **Current governance / execution status**：Framework v7.4 = **CLOSED / ACCEPTED**（current methodology authority）；Registry v7.3 R3 = **CLOSED / ACCEPTED**（current evidence authority until this candidate is independently accepted）；Registry v7.4 Candidate R1 = **CANDIDATE ONLY**；accepted EOB = **CLOSED / ACCEPTED**；accepted core-three = **CLOSED / ACCEPTED**；Full81 = `NOT_YET_EXECUTED`；Layer A preregistration checkpoint = `NOT_YET_CREATED`；final cross-document alignment audit = `NOT_YET_EXECUTED`；production-authority re-freeze = `NOT_YET_PERFORMED`。見 §20.4。
- **final integrated annual input**：Script 06 integration已完成 / passed；P2 calibration使用current integrated artifact的observed columns；pre-v7 `annual_input_existing_pv.*`不得因檔名直接沿用。
- **B1 degradation formulation**：R20 + T4 控制 PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation；R31控制 rainflow ex-post validation；Harry hourly-reset降為 legacy。
- **LFP cycle-depth technical calibration**：T4 Table 4.2 five-point effective-DOD/cycle-life set已鎖定；production可合併為0/0.30/0.60/0.80三段，但不得刪除五點 provenance。
- **BESS CAPEX/FOM source + Gate 1**：PNNL v2024 controls raw cost source；Scripts 11f/11g/11h已完成1 MW/10 MW full-package derivation；v7.2事前鎖定10 MW mainline、1 MW sensitivity。
- **B2 accounting**：no structural change；annualized CAPEX + annual FOM + operating costs/cycling wear維持，不新增 full replacement stream。
- **Gate 2 monetary basis / discount rate**：optimization = constant NTD-2023；\(r=5\%\) = real modeling rate；\(n=20\) yr；CRF derived。R26–R27只支持5%/20-year precedent，T5控制real/nominal consistency。
- **Taipower 13b/13c**：tariff-registry gate與pure-season bill-component regression均 CLOSED/PASS；May/October 50/50仍只稱case-validated empirical rule。
- **Tariff/accounting traceability**：`SCHOOL/FROZEN`為project label；non-summer peak=N/A；subsidy不另作cash-flow；raw nominal validation layer與constant-2023 optimization layer分離。
- **Next economic implementation gate**：Script 14a需建立/驗證official nominal tariff → constant NTD-2023 production layer與package routing；這是implementation gate，不重新打開Gate 1/2。

## 仍需在 parameter / institutional registry 保存的 exact evidence

- case-year NTUST monthly bills；
- `billing_demand_registry.csv`：usage-period start/end、bill-title month、regular/supplementary CC、four TOU maxima、source filename；
- each applicable Taipower tariff effective date/version；
- TOU energy rates；
- contract-capacity basic charge；
- over-contract penalty tiers / multipliers；
- monthly billed maximum demand；
- PNNL v2024 source rows / workbook tab / duration / scale used for linearization；
- explicit package role metadata：10 MW = mainline、1 MW = sensitivity；full-package contents \(C_E,C_P,FOM,C_{rep},\lambda_k\)；
- Script 11f/11g/11h versions/hashes and generated dual-bracket package artifacts；
- Script 12a semantics-audit version/hash；
- USD→NTD exchange-rate source and date/base year, including FX = 31.150 NTD/USD provenance；
- raw Taipower nominal tariff rows **and** derived constant-NTD-2023 optimization rows with price-index/deflator source, reference period, formula, and transformation provenance；
- 13b tariff-registry audit and 13c bill-regression artifacts / versions / hashes；
- `SCHOOL/FROZEN` project label meaning, non-summer peak N/A semantics, May/October empirical-status note, and subsidy non-double-counting note；
- PNNL 2022 Table 4.2 cycle-depth calibration provenance：reported DOD、average/effective DOD、cycles-to-EOL、source page/version；
- PWL replacement-cost basis、effective breakpoints與 automatically derived \(\lambda_k\)；
- Xu-derived segment-state implementation unit tests / segment cyclicity audit；
- ex-post rainflow cycle-depth/cost validation outputs；
- \(\kappa\) calibration monthly pairs \(H_m,B_m\)、ratios、residual/error diagnostics、included/excluded months；
- `calibrate_kappa.py` version/hash and generated audit table；
- production `parameter_registry` 12-field schema from P3, including `mainline_or_legacy` and `notes`。

## 仍需官方／場域來源，但屬其他模組

- CPC diesel price；
- Taiwan diesel CO₂ emission factor；
- NTUST existing emergency-DG purpose / circuit boundary。

## 已降級為 optional implementation context

- NTUST BESS site area；
- fire-code spacing；
- interconnection power limit；
- construction constraints；
- institutional budget ceiling。

這些資料若取得，可以放在 discussion / implementation overlay；**不再是 Layer A production-run blocker，也不新增 RQ5。**

---

# 16. Working bibliography

- Adeyemo, A. A., & Amusan, O. T. (2022). *Modelling and multi-objective optimization of hybrid energy storage solution for photovoltaic powered off-grid net zero energy building*. Journal of Energy Storage, 55, 105273. https://doi.org/10.1016/j.est.2022.105273
- Bazdar, E., Nasiri, F., & Haghighat, F. (2024). *Resilience-centered optimal sizing and scheduling of a building-integrated PV-based energy system with hybrid adiabatic-compressed air energy storage and battery systems*. Energy, 308, 132836. https://doi.org/10.1016/j.energy.2024.132836
- Chen, C.-Y., & Liao, C.-J. (2011). *A linear programming approach to the electricity contract capacity problem*. Applied Mathematical Modelling, 35(8), 4077–4082. https://doi.org/10.1016/j.apm.2011.02.032
- Cole, W., Ramasamy, V., & Turan, M. (2025). *Cost Projections for Utility-Scale Battery Storage: 2025 Update*. NREL/TP-6A40-93281. https://doi.org/10.2172/2583471
- Gabrielli, P., Gazzani, M., Martelli, E., & Mazzotti, M. (2018). *Optimal design of multi-energy systems with seasonal storage*. Applied Energy, 219, 408–424. https://doi.org/10.1016/j.apenergy.2017.07.142
- Gorman, W., Barbose, G., Carvallo, J. P., Baik, S., Miller, C., White, P., & Praprost, M. (2023). *County-level assessment of behind-the-meter solar and storage to mitigate long duration power interruptions for residential customers*. Applied Energy, 342, 121166. https://doi.org/10.1016/j.apenergy.2023.121166
- Giovanniello, M. A., & Wu, X.-Y. (2023). *Hybrid lithium-ion battery and hydrogen energy storage systems for a wind-supplied microgrid*. Applied Energy, 345, 121311. https://doi.org/10.1016/j.apenergy.2023.121311
- İşcan, S., & Arıkan, O. (2025). *Optimizing battery energy storage system for campus micro grid: Economic and environmental benefits of strategic sizing*. Journal of Energy Storage, 124, 116905. https://doi.org/10.1016/j.est.2025.116905
- Qi, N., Huang, K., Fan, Z., & Xu, B. (2025). *Long-term energy management for microgrid with hybrid hydrogen-battery energy storage: A prediction-free coordinated optimization framework*. Applied Energy, 377, 124485. https://doi.org/10.1016/j.apenergy.2024.124485
- Rahman, M. M., Oni, A. O., Gemechu, E., & Kumar, A. (2021). *The development of techno-economic models for the assessment of utility-scale electro-chemical battery storage systems*. Applied Energy, 283, 116343. https://doi.org/10.1016/j.apenergy.2020.116343
- Laws, N., Anderson, K., Li, X., McLaren, J., & DiOrio, N. (2018). *Impacts of Valuing Resilience on Cost-Optimal PV and Storage Systems for Commercial Buildings*. Renewable Energy, 127, 896–909. https://doi.org/10.1016/j.renene.2018.05.011
- Marqusee, J., Becker, W., & Ericson, S. (2021). *Resilience and economics of microgrids with PV, battery storage, and networked diesel generators*. Advances in Applied Energy, 3, 100049. https://doi.org/10.1016/j.adapen.2021.100049
- Naumann, M., Schimpe, M., Keil, P., Hesse, H. C., & Jossen, A. (2018). *Analysis and modeling of calendar aging of a commercial LiFePO₄/graphite cell*. Journal of Energy Storage, 17, 153–169. https://doi.org/10.1016/j.est.2018.01.019
- Naumann, M., Spingler, F. B., & Jossen, A. (2020). *Analysis and modeling of cycle aging of a commercial LiFePO₄/graphite cell*. Journal of Power Sources, 451, 227666. https://doi.org/10.1016/j.jpowsour.2019.227666
- Omar, N., Abdel-Monem, M., Firouz, Y., Salminen, J., Smekens, J., Hegazy, O., Gaulous, H., Mulder, G., Van den Bossche, P., Coosemans, T., & Van Mierlo, J. (2014). *Lithium iron phosphate based battery – Assessment of the aging parameters and development of cycle life model*. Applied Energy, 113, 1575–1585. https://doi.org/10.1016/j.apenergy.2013.09.003
- Pickering, B., & Choudhary, R. (2021). *Quantifying resilience in energy systems with out-of-sample testing*. Applied Energy, 285, 116465. https://doi.org/10.1016/j.apenergy.2021.116465
- Rodriguez, R., Osma, G., Bouquain, D., Ordoñez, G., Paire, D., Solano, J., Roche, R., & Hissel, D. (2024). *Electrical resilience assessment of a building operating at low voltage*. Energy and Buildings, 313, 114217. https://doi.org/10.1016/j.enbuild.2024.114217
- Sepúlveda-Mora, S. B., & Hegedus, S. (2021). *Making the case for time-of-use electric rates to boost the value of battery storage in commercial buildings with grid connected PV systems*. Energy, 218, 119447. https://doi.org/10.1016/j.energy.2020.119447
- Sepúlveda-Mora, S. B., & Hegedus, S. (2022). *Resilience analysis of renewable microgrids for commercial buildings with different usage patterns and weather conditions*. Renewable Energy, 192, 731–744. https://doi.org/10.1016/j.renene.2022.04.090
- Shi, Y., Xu, B., Tan, Y., & Zhang, B. (2018). *A Convex Cycle-based Degradation Model for Battery Energy Storage Planning and Operation*. 2018 Annual American Control Conference (ACC), 4590–4596. https://doi.org/10.23919/ACC.2018.8431814
- Son, Y., Woo, H., Noh, J., Dehghanian, P., Zhang, X., & Choi, S. (2024). *Optimization of energy storage scheduling considering variable-type minimum SOC for enhanced disaster preparedness*. Journal of Energy Storage, 93, 112366. https://doi.org/10.1016/j.est.2024.112366
- Wei, Y., Wang, S., Han, X., Lu, L., Li, W., Zhang, F., & Ouyang, M. (2022). *Toward more realistic microgrid optimization: Experiment and high-efficient model of Li-ion battery degradation under dynamic conditions*. eTransportation, 14, 100200. https://doi.org/10.1016/j.etran.2022.100200
- Wu, R., & Sansavini, G. (2020). *Integrating reliability and resilience to support the transition from passive distribution grids to islanding microgrids*. Applied Energy, 272, 115254. https://doi.org/10.1016/j.apenergy.2020.115254
- Xu, M., Wang, X., Zhang, L., & Zhao, P. (2021). *Comparison of the effect of linear and two-step fast charging protocols on degradation of lithium ion batteries*. Energy, 227, 120417. https://doi.org/10.1016/j.energy.2021.120417

- Demirhan, H., & Renwick, Z. (2018). *Missing value imputation for short to mid-term horizontal solar irradiance data*. Applied Energy, 225, 998–1012. https://doi.org/10.1016/j.apenergy.2018.05.054
- Jahanbin, A., Abdolmaleki, L., & Berardi, U. (2024). *Techno-economic feasibility of integrating hybrid battery-hydrogen energy storage system into an academic building*. Energy Conversion and Management, 309, 118445. https://doi.org/10.1016/j.enconman.2024.118445
- Jeong, D., Park, C., & Ko, Y. M. (2021). *Missing data imputation using mixture factor analysis for building electric load data*. Applied Energy, 304, 117655. https://doi.org/10.1016/j.apenergy.2021.117655
- Le, S. T., Nguyen, T. N., Bui, D.-K., & Ngo, T. D. (2024). *Techno-economic and life cycle analysis of renewable energy storage systems in buildings: The effect of uncertainty*. Energy, 307, 132644. https://doi.org/10.1016/j.energy.2024.132644
- Liu, Z., Zhang, Y., & Ning, Y. (2025). *Emergency mobile energy storage optimal allocation in microgrid-integrated distribution networks considering economic and resilience benefits*. Energy, 322, 135633. https://doi.org/10.1016/j.energy.2025.135633
- Loomans, N., & Alkemade, F. (2024). *Exploring trade-offs: A decision-support tool for local energy system planning*. Applied Energy, 369, 123527. https://doi.org/10.1016/j.apenergy.2024.123527
- Browne, M. H., & Williams, A. A. (2023). *The effect of time resolution on the modelling of domestic solar energy systems*. Renewable Energy and Environmental Sustainability, 8, 5. https://doi.org/10.1051/rees/2023003
- Omoyele, O., Matrone, S., Hoffmann, M., Ogliari, E., Weinand, J. M., Leva, S., & Stolten, D. (2024). *Impact of temporal resolution on the design and reliability of residential energy systems*. Energy and Buildings, 319, 114411. https://doi.org/10.1016/j.enbuild.2024.114411
- Mayer, M. J., & Gróf, G. (2021). *Extensive comparison of physical models for photovoltaic power forecasting*. Applied Energy, 283, 116239. https://doi.org/10.1016/j.apenergy.2020.116239
- Ramadhan, R. A. A., Heatubun, Y. R. J., Tan, S. F., & Lee, H.-J. (2021). *Comparison of physical and machine learning models for estimating solar irradiance and photovoltaic power*. Renewable Energy, 178, 1006–1019. https://doi.org/10.1016/j.renene.2021.06.079
- Central Weather Administration (CWA). *CODiS 氣候觀測資料查詢服務：氣候觀測資料查詢簡易操作說明* (2025-01-02). Official institutional source; historical station observations / hourly daily report / CSV export.
- Central Weather Administration (CWA). *日射量資料—署屬氣象站日射量資料* (Open Data Platform dataset O-A0091-001). Official institutional solar-radiation data source.
- Viswanathan, V., Mongird, K., Franks, R., Li, X., Sprenkle, V., & Baxter, R. (2022). *2022 Grid Energy Storage Technology Cost and Performance Assessment* (PNNL-33283). Pacific Northwest National Laboratory.
- Weber, M., Turowski, M., Çakmak, H. K., Mikut, R., Kühnapfel, U., & Hagenmeyer, V. (2021). *Data-Driven Copy-Paste Imputation for Energy Time Series*. IEEE Transactions on Smart Grid, 12(6), 5409–5419. https://doi.org/10.1109/TSG.2021.3101831
- Xu, B., Zhao, J., Zheng, T., Litvinov, E., & Kirschen, D. S. (2018). *Factoring the Cycle Aging Cost of Batteries Participating in Electricity Markets*. IEEE Transactions on Power Systems, 33(2), 2248–2259. https://doi.org/10.1109/TPWRS.2017.2733339
- Vatankhah Ghadim, H., Haas, J., Breyer, C., Gils, H. C., Read, E. G., Xiao, M., & Peer, R. (2025). *Are we too pessimistic? Cost projections for solar photovoltaics, wind power, and batteries are over-estimating actual costs globally*. Applied Energy, 390, 125856. https://doi.org/10.1016/j.apenergy.2025.125856
- National Institute of Standards and Technology (NIST). *Life-Cycle Costing Manual for the Federal Energy Management Program*, Handbook 135, 2022 update. https://doi.org/10.6028/NIST.HB.135e2022-upd1

---

## v7.2 maintenance guardrails

- **Do not add Beck et al. (2016) merely to justify hourly resolution** unless a later literature-review chapter needs historical lineage; current primary temporal-resolution evidence is R28–R29.
- Do not promote Harry/lab-predecessor values into academic benchmark rows.
- Do not use optimized \(P^B\) to choose 1 MW vs 10 MW package. Gate 1 is ex ante: 10 MW mainline, 1 MW sensitivity.
- Do not mix bracket components: \(C_E,C_P,FOM,C_{rep},\lambda_k\) must move together as a full package.
- Do not invent a continuous 1–10 MW interpolation curve from two PNNL source cases unless the framework is explicitly reopened with a supported scaling model.
- Do not mix 2023 constant BESS costs with raw 2024/2025 nominal tariffs in the optimization objective.
- Do not call the 5% rate an NTUST WACC; it is a real modeling rate under the constant-NTD-2023 convention.
- Keep raw nominal tariff evidence immutable; Script 14a normalization must create a separate optimization layer with deflator provenance.
- Preserve non-summer peak as N/A rather than zero, and do not universalize the May/October 50/50 empirical rule.
- Do not add a separate subsidy credit/debit if the same policy effect is already embedded in the audited effective tariff/bill.
- Do not hard-code legacy \(C_{rep}\) or \(\lambda_k\) into mainline; T4 technical life data and final economic cost basis must remain separable.
- When T4 is cited, state whether the thesis is using **Table 4.2 cycles-to-end-of-life** or another PNNL endpoint. The current v7.2 calibration uses Table 4.2.
- If the \(\kappa\) model is changed (e.g. intercept model, month-specific factor, sub-hourly data becomes available), P2 and framework §4.3 must be updated together.
- Do not reintroduce 0.91/0.91 or 0.95/0.90 into mainline without reopening A1 with explicit boundary evidence.
- Do not label any hourly-reset degradation segmentation as consistent with Xu et al.'s intertemporal formulation; R20 requires cross-time segment energy states.
- Do not merge PNNL Table 4.2 technical calibration provenance merely because production uses three effective PWL segments.
- Do not call the mainline simply “the Xu model”; use “PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL cycle-aging formulation” and keep Xu / PNNL / thesis-specific roles separate.
- Keep the efficiency convention explicit: \(\lambda_k\) is NTD per battery-side discharged kWh; if AC-side discharge is divided by \(\eta_d\) in the objective, do not also embed \(1/\eta_d\) inside \(\lambda_k\).
- Do not treat `bill_title_month` as the join key for \(\kappa\) or tariff reconciliation; always use actual usage-period boundaries.
- Do not use floating demand epigraph variables as reported maxima; P5 exact post-solve recomputation is mandatory.
- Do not restore Load ±8/K3 or PV donor ±30/K5 as production rules merely because older Registry v7 recorded them; P1 v7.2-retained empirical evidence supersedes those roles.
- Keep PV donor ±30d/K5 mean as a validated benchmark unless a later registered validation changes its comparison role.
- Do not describe R32/R33 as proving `hourly_ghi_ratio_median`; they support weather→PV estimation and model-selection logic only.
- Do not use Script-04b short-gap results to justify long winter reconstruction without separate block/month holdout validation. **(This holdout validation has since been performed as Step 17a -- see P7-A -- so this guardrail is now satisfied for the reconstructed-PV mainline promotion; it remains the rule for any future re-derivation and must not be treated as skippable.)**
- Do not describe the corrected Step 17b artifact (`...corrected_authority_project_venv_2026-09-18.parquet`) as the current canonical planning input; it is **historical promotion-source lineage / project evidence only** (P7-C). The accepted planning input is recorded in P7-E.
- Do not reintroduce zero-winter as a mandatory EOB/Layer A/Layer B sensitivity or as an equal-status alternative planning baseline; its current role is historical conservative validation / provenance evidence (Framework v7.4 §36.1). Equally, do not delete, rewrite, rename, or drop the existing zero-winter evidence from the lineage — both the erasure and the re-mandating are errors.
- Do not substitute some other sensitivity “in place of” zero-winter; the minimum-sensitivity inventory is net one item shorter, by design.
- Do not route any planning-layer consumer (EOB, Layer A, Full81, \(R\), \(P^{out}\), binding classification, outage consistency replay, baseline Layer B) to a PV identity other than the single accepted planning artifact; and do not route any historical empirical/calibration claim to reconstructed values.
- Do not use the accepted reconstructed planning PV to redefine, re-estimate, or re-sample production \(\kappa\); historical calibration stays on observed Load/PV and observed billing evidence.
- Do not describe \(\kappa\) as a 15-minute reconstruction, as sub-hourly physical power validation, or as evidence that the hourly model captures all instantaneous peaks; and do not let \(\kappa\) be cited against the R28–R29 temporal-resolution limitations.
- Do not state that the accepted EOB/core-three completion manifests contain `CLOSED / ACCEPTED`; they record the execution-time status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`, and the accepted status is a later governance lifecycle layer.
- Do not group the accepted core-three with Full81 as jointly pending; only Full81 is `NOT_YET_EXECUTED`.
- Do not treat Step 17c's paired EOB/`a0.80_b08` comparison as evidence covering the full 81-point Layer A response surface; only two cases were paired (P7-D).
- Do not silently reclassify any pre-v7.3 EOB/Layer A/rainflow/continuation output as v7.3 canonical production evidence; preserve each artifact's original acceptance boundary (see P7 evidence-role summary).
- I5 supports official CWA data provenance, but the exact 23:59 normalization remains project-format audit evidence unless an official CWA definition is later added.
- P2 must follow the current audited final integrated annual input's observed columns; an old pre-v7 `annual_input_existing_pv.*` is legacy and cannot control production.

---

## Maintenance note

之後新增文獻時，不要只補 citation；必須同步補：

- exact supported claim；
- exact unsupported claim；
- thesis placement；
- evidence role（technical basis / modeling precedent / comparison / parameter source）。

這樣可以避免後續 thesis 版本演進時 citation drift 或 overclaim。

另外，若新文獻與既有來源出現不同數值或建議，不直接覆蓋：先標記是 mainline、sensitivity、limitation、comparison 還是 legacy；只有在它們真正支持同一主張且互相矛盾時，才建立 explicit conflict note。

---

# 17. Framework v7.3 reconstructed-PV mainline evidence alignment（**inherited historical record**；current v7.4 alignment 見 §20）

> **Scope of this section (read first).** §17 is the **inherited Registry v7.3 alignment record**. It documents the Registry v7.3 candidate’s additive delta relative to Registry v7.2 against Framework v7.3, and it is retained for provenance, lineage, and regression traceability. Statements inside §17 that assign a **role or status** describe the position **as it stood under Framework v7.3 / at Registry v7.3 R3 authoring time**, unless a row below explicitly carries a current v7.4 value. The **current** evidence-role and claim-boundary alignment to accepted Framework v7.4 — including the zero-winter current role, the observed-vs-planning PV routing, and the \(\kappa\) claim boundary — is in **§20**, and §20 governs wherever the two could be read as differing. Where a §17 statement was locally current-looking and is now stale, it has been rescoped in place (§17.1, §17.5, §17.7, §17.10, §17.11) rather than left to a distant disclaimer.

本節是 Registry v7.3 candidate 相對於 Registry v7.2 的 additive evidence-role delta 與当時 current-state 對照，對應 Framework v7.3 §35 的 methodology decision。它只改變 prolonged-winter PV 的 evidence role assignment，不建立新文獻主張，也不重新打開 A1-A4 / B1-B2 / Gate 1-2。

## 17.1 Decision and epistemic boundary (evidence-role restatement)

**Methodology decision (owned by Framework v7.3, restated here for evidence traceability):** reconstructed full-year PV (含 2024/11-12 共 1,463 個 unavailable-observation hours) 是 v7.3 的 mainline best-estimate planning baseline; v7.2 的 zero-winter treatment 当時改列 conservative stress/sensitivity. This decision is Framework authority (Category C below); the Registry supplies the supporting project evidence (P7) and the literature/claim boundary, and does not itself decide methodology.

> **Current-role update (accepted Framework v7.4).** The reconstructed-PV **planning-baseline** assignment above is **continued unchanged** by accepted Framework v7.4 §4.1.3. The **zero-winter role statement above is historical**: under accepted Framework v7.4 §36.1 the zero-winter treatment’s current role is **historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion/adjudication decision, and it is not a mandatory sensitivity. See §20.1.

Mandatory epistemic sentence (reused verbatim from Framework v7.3; also carried in Sec 14 above):

> "The winter PV reconstruction is a model-based, weather-informed, separately validated estimate for planning use; it is not observed meter data, not exact ground truth, and not an exact recovery of the missing historical series."

## 17.2 Required epistemic separation (four evidence classes)

| Class | What it covers here | Examples in this Registry |
|---|---|---|
| A. External literature / authoritative source facts | R21-R23, R32-R33, I5: reconstruction methodology, weather-informed PV estimation, artificial-gap validation logic, official CWA data provenance | Do not by themselves validate the exact NTUST long-block reconstruction |
| B. Project empirical validation results | P1 (Scripts 02-05 short-gap production rules), P7-A (Step 17a long-block holdout), P7-C (corrected Step 17b candidate), P7-D (Step 17c paired evidence) | Establish the actual NTUST reconstruction candidate, its validation outcome, and its optimization feasibility |
| C. Framework / methodology decisions | Framework v7.3 Sec 4.1.3, Sec 35: mainline/sensitivity role assignment | Decided by the Framework, not by this Registry; Registry documents the evidence basis only |
| D. Inference / claim boundaries | Sec 14 "不要寫" additions; P7 "Scope this does NOT establish" / "Not authorized to claim" columns | Prevent collapsing B or C into stronger claims than the evidence supports |

These four classes are never collapsed in this Registry: no external-literature record (Class A) is cited as establishing NTUST-specific numerical results (Class B); no project validation result (Class B) is cited as itself constituting the mainline/sensitivity role decision (Class C); and every Class B/C item carries an explicit Class D boundary.

## 17.3 Framework v7.3 to Registry v7.3 R2 coverage matrix (rebuilt from scratch for R2)

This matrix was re-derived for R2 from a fresh read of accepted Framework v7.3 primary bytes. It does **not** reuse the R1 matrix. Every mapping row now names both the **historical evidence text** and the **current v7.3 evidence-role interpretation**, because the R1 failure was caused precisely by a mapping that recorded only the current-role sections and omitted the historical text that contradicted them.

| Framework location | Claim | Evidence type | Registry v7.3 record/section | Support level | Anti-claim / boundary | Status |
|---|---|---|---|---|---|---|
| Sec 4.1.3 role reversal (`PV_t^base = reconstructed` for `pre_system`/`missing_winter`) | reconstructed full-year PV is v7.3 mainline; zero-winter is sensitivity | B (project) + C (framework decision) | **Historical text:** P1-E "Historical role" subsection, boxed `PV_t^{base}=0` explicitly labelled HISTORICAL v7.1/v7.2 and SUPERSEDED, with the current v7.3 assignment stated inline for the same index set. **Current role:** P1-E "Current role" subsection; claim-to-source map (Sec 12, both rows); P7 evidence-role summary | Full: numbers verified from primary artifacts (P7-C, P7-D); both roles now carry explicit temporal scope | not observed truth; not exact recovery; historical equation must not be read as a current prescription | MAPPED |
| Sec 4.1.1 observed vs planning-baseline distinction | observed columns immutable; only planning-baseline layer reconstructed | B (project) | P1 (unchanged); P7-C data-boundary note (`observed_pv_kw` verified uniformly 0 over the block) | Full: independently re-verified by reading the candidate artifact | reconstruction never overwrites observed columns | MAPPED |
| Sec 4.1.3 long-block validation requirement | short-gap validation cannot be extrapolated to the 1,463 h block; separate holdout validation required | A (R23/R32/R33/I5 boundary) + B (P1, P7-A) | **Historical text:** P1-E "Under Framework v7.2" paragraph (Scripts 02-05 finding, substance unchanged). **Current role:** P1-E "What is unchanged" paragraph — the finding remains true and is the reason Step 17a was required; P7-A (Step 17a design and verdict) | Full | literature does not itself certify the long block; P7-A is the certifying evidence; the v7.3 promotion does not weaken or re-audit this finding | MAPPED |
| Sec 4.1.3 weather-informed reconstruction | CWA GHI-based `hourly_ghi_ratio_median` used for reconstruction | A (R32-R33, I5) + B (P1-C, P7-A) | P1-C (model selection); I5 (CWA provenance); P7-A (design) | Full | CWA/GHI literature supports the modeling direction only, not the exact NTUST coefficients | MAPPED |
| Sec 4.1.3 / Sec 35.1 epistemic boundary sentence | reconstruction is model-based, not observed/exact/recovered | D (claim boundary) | Sec 14 mandatory bullet (verbatim); P7 evidence-role summary | Full (verbatim reuse) | none beyond the sentence itself | MAPPED |
| Sec 16.1 / Sec 4.1.3 sensitivity role reversal | zero-winter demoted to conservative stress/sensitivity; reconstructed PV promoted to mainline | C (framework) + B (P1 historical) | **Historical text:** P1-E "Under Framework v7.2" paragraph, which states the sensitivity-branch role as it then stood, explicitly past-scoped. **Current role:** P1-E "Current role — under accepted Framework v7.3" subsection, which states the reversal explicitly; claim-to-source map second new row; Sec 14/15 updated bullets; Sec 17.5 | Full | zero-winter is not "truth" or an observed no-generation period; the historical sensitivity-branch role must not be read as current | MAPPED |
| Sec 7.2/7.10/10.3 Layer A/B reconstructed-PV adequacy semantics (same artifact feeds `R`, `P_out`, binding, outage replay, baseline Layer B) | no hybrid economics-credit/outage-no-credit routing | C (framework, exact formulas are framework-owned) | Sec 14 new bullet (same-artifact requirement); claim-to-source map first new row | Partial: Registry restates the requirement; the exact equations and routing enforcement are Framework/implementation authority, not Registry content | Registry does not itself prove routing compliance -- that is an implementation/production-routing audit, out of scope here | MAPPED (Registry scope: claim boundary only) |
| Sec 22 limitation 7 / deterministic historical-start claim boundary | adequacy is conditional on the reconstruction; not probabilistic; not islanding-engineering validation | D (claim boundary) + A (R28-R29 temporal-resolution limitation, retained unchanged) | Sec 14 new bullet; R28/R29 records unchanged | Full | no probabilistic reliability or physical islanding claim is added | MAPPED |
| Sec 35.6 current authorization state (Registry/canonical-input/routing/17c/representative-cases/11A-C/final81) | explicit `NOT_YET_*` states | C (framework) | Sec 17.7 status table below; Sec 15 new bullet | Full | none of these states are fabricated as complete | MAPPED |

**R3 coverage result.** The fourteen acceptance-relevant Framework v7.3 reconstructed-PV claims mapped above and in Sec 17.9 were rechecked against the accepted Framework's primary bytes for R3: (1) reconstructed full-year PV = mainline; (2) zero-winter = conservative stress/sensitivity; (3) observed vs planning-baseline separation; (4) long-block reconstruction validation requirement; (5) weather-informed reconstruction basis; (6) reconstruction epistemic boundary; (7) same reconstructed artifact for economics and Layer A; (8) \(R(\alpha,\beta)\)/\(P^{out}\)/binding-window semantics; (9) Layer A outage replay semantics; (10) baseline Layer B semantics; (11) billing calibration remains observed-data based; (12) sensitivity-role reversal; (13) limitation / claim boundary; (14) current implementation authorization state. The R3 authority-wording sweep additionally covers the document header, source manifest, supersession rule, audit-status rule, P1-E, and Sec 17 status table. No unmapped acceptance-relevant claim or competing current methodology authority remains; see Sec 17.9 and the R3 checkpoint.

## 17.4 Historical evidence preservation matrix

| Evidence | Preserved role under v7.3 | Not authorized to claim |
|---|---|---|
| Step 17a | `PASS_FOR_SENSITIVITY`; separate long-block/monthly holdout validation evidence (P7-A) | observed truth, exact recovery, standalone completion of canonical promotion |
| Original Step 17b | sensitivity-only historical run/evidence (P7-B) | v7.3 canonical mainline |
| Corrected Step 17b | corrected promotion-source candidate (P7-C) | canonical artifact or production authorization |
| Step 17c | paired reconstructed-vs-zero-winter sensitivity and adjudication evidence (P7-D) | accepted v7.3 EOB/final production rerun; full-81-point robustness |
| P1 (Scripts 02-05) | unchanged historical short-gap production rules and the "short-gap does not validate long-block" finding | superseded or contradicted by v7.3 -- it is not; it is the reason P7-A was required |
| P1-E historical boxed `PV_t^{base}=0` | preserved verbatim, explicitly labelled HISTORICAL v7.1/v7.2 MAINLINE DEFINITION and SUPERSEDED, with the current v7.3 assignment stated inline for the same index set | a current mainline prescription; a claim that observed winter generation was physically zero; a reason to treat the v7.3 reconstruction as unvalidated |
| P1-E historical sensitivity-branch statement | preserved, past-scoped to Framework v7.2 ("for as long as that validation was outstanding") | a current statement that reconstructed winter PV is sensitivity-only |
| All prior EOB/Layer A/rainflow/continuation outputs | immutable historical, diagnostic, sensitivity, candidate, or predecessor evidence per original manifests | silent reclassification as v7.3 final |

## 17.5 Reconstructed-PV / zero-winter role alignment table

| Role | v7.2 (historical) | v7.3 (historical) | **v7.4 (current, accepted)** |
|---|---|---|---|
| Reconstructed full-year PV (incl. 1,463 h block) | sensitivity branch only; not mainline | mainline best-estimate planning baseline | **best-estimate planning baseline — continued unchanged**; the single accepted planning-layer artifact identity (P7-E) |
| Zero-winter annual treatment | mainline | conservative stress/sensitivity | **historical conservative validation / provenance evidence** supporting the reconstructed-PV promotion/adjudication decision; **not** a mandatory EOB/Layer A/Layer B sensitivity; **not** an equal-status alternative planning baseline; no new solve required |
| Evidence basis for the block | P1 (short-gap only; long-block unvalidated) | P1 (unchanged) + P7 (Step 17a/corrected 17b/17c) | P1 + P7 (unchanged) + **P7-E accepted planning artifact** |
| Framework authority | Framework v7.2 Sec 4.1.3 (historical) | Framework v7.3 Sec 4.1.3 / Sec 35 (historical) | **Framework v7.4 §4.1.1-R / §4.1.3 / §4.3.1-K / §36 (CLOSED / ACCEPTED)** |

Every v7.2 and v7.3 entry above remains **true as past-scoped historical provenance** and is retained deliberately; only the current-prescriptive column changes.

## 17.6 Required numerical facts with evidence roles (independently re-verified from primary bytes)

| Fact | Value | Evidence role | Source |
|---|---|---|---|
| Prolonged unavailable block | 1,463 h | project fact (P1-E, re-confirmed in P7-C) | canonical/candidate parquet inspection |
| `pre_system` | 600 h | project fact | P1-E, P7-C |
| `missing_winter` | 863 h | project fact | P1-E, P7-C |
| Reconstructed winter energy | 39,484.422494 kWh/year | project fact (candidate artifact), independently cross-checked against Step 17c's paired `pv_available_kwh` delta | P7-C |
| Positive reconstructed winter hours | 619 of 1,463 | project fact | P7-C |
| Original zero-winter mainline treatment | zero availability for all 1,463 h | historical project/framework decision (Framework v7.2) | P1-E |

No reconstructed energy figure above is described as measured generation; each is labeled as a project-derived candidate-artifact fact.

## 17.7 Status boundary — v7.3-era snapshot versus current state

The left column is the **historical snapshot** recorded when Registry v7.3 R3 was authored. The right column is the **current** state under accepted Framework v7.4 and supersedes it for all current-status purposes; the authoritative current table is §20.4.

| Layer | State at Registry v7.3 R3 authoring (historical) | **Current state** |
|---|---|---|
| Framework v7.3 | `CLOSED / ACCEPTED` (independently audited) | `CLOSED / ACCEPTED` **historical methodology predecessor**; no longer the current methodology authority |
| Framework v7.4 | did not exist | **`CLOSED / ACCEPTED` — current methodology authority** |
| Registry v7.3 R1 (failed candidate) | **SUPERSEDED** -- failed independent acceptance; immutable provenance | unchanged — failed immutable provenance |
| Registry v7.3 R2 (failed candidate) | **SUPERSEDED** -- failed independent acceptance on inherited current-authority wording; immutable provenance | unchanged — failed immutable provenance |
| Registry v7.3 R3 | `CANDIDATE PASS` -- not yet independently accepted | **`CLOSED / ACCEPTED` — current evidence authority until Registry v7.4 Candidate R1 is independently accepted** |
| Registry v7.4 Candidate R1 (this file) | did not exist | **CANDIDATE ONLY** — not accepted; cannot self-promote; independent read-only audit required |
| Accepted planning input | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` | **`CLOSED / ACCEPTED`** — `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`, SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`, role `reconstructed_pv_mainline`, 8,760 rows (P7-E) |
| Production routing | `NOT_YET_AUTHORIZED` | planning-layer routing onto the accepted planning identity is **COMPLETED / ACCEPTED** for the accepted EOB and core-three; routing compliance for any future run remains an implementation/production audit, not Registry content |
| Step 17c comparison | promotion/adjudication candidate evidence only | **historical project validation / adjudication evidence** (Framework v7.4 CHANGE A); not a mandatory sensitivity |
| EOB | not yet accepted | **`CLOSED / ACCEPTED`** — `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556` |
| Layer A core-three | not identified as a separate accepted state | **`CLOSED / ACCEPTED`** — `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55` |
| Representative cases | NOT CLOSED UNDER V7.3 | superseded by the accepted core-three (LOW/CENTRAL/HIGH) above |
| Steps 11A / 11B / 11C | NOT CLOSED UNDER V7.3 | historical v7.3-era gate labels; superseded by the accepted EOB/core-three execution state |
| Full81 | NOT AUTHORIZED UNDER V7.3 | **`NOT_YET_EXECUTED`** and not authorized — a **different** execution state from the accepted core-three |
| Layer A robustness / preregistration checkpoint | not yet contemplated | `NOT_YET_CREATED` |
| Final cross-document alignment audit | not yet contemplated | `NOT_YET_EXECUTED` |
| Production-authority re-freeze under v7.4 | not yet contemplated | `NOT_YET_PERFORMED` |

## 17.8 External-literature claim-boundary confirmation

Re-read R21-R23, R32-R33, and I5 in full against the Sec 6 boundary requirements. None of these external sources is cited, in this Registry, as establishing: the NTUST 39,484.422494 kWh reconstructed winter energy; the exact 619 positive reconstructed hours; the exact NTUST CWA-to-PV coefficients as universal; reconstructed PV as equivalent to rooftop measurement; or the validity of any future 81-point resilience result. Each of these external records' own "不能支持" / boundary text already excludes exactly these overclaims (unchanged from Registry v7.2), and P7 attributes every NTUST-specific number to project evidence (P1/P7), never to literature. No web research was performed in this pass; all external-literature citations reused here were already present and audited in Registry v7.2.

## 17.9 Cross-document consistency audit (Registry v7.3 R3 against Framework v7.3 primary bytes) — **historical record**

> **Scope.** This table is the **historical** consistency audit performed on the **Registry v7.3 R3 bytes** against **Framework v7.3** bytes. Its “Registry” column describes **that document’s** sections as they stood then, and its section cross-references (Sec 12 / Sec 14 / Sec 15 / Sec 17.7 / P7) point at the **R3-era** content of those sections. It is **not** a consistency claim about this Registry v7.4 Candidate R1 document or about Framework v7.4. The current Framework-v7.4 claim-to-evidence coverage is **§20.5**, and the formal **final cross-document alignment audit is `NOT_YET_EXECUTED`** (§20.4). Rows marked **SUPERSEDED** below have a changed current value.

| Item | Framework v7.3 | Registry v7.3 R3 (as it then stood) | Consistent under v7.3? |
|---|---|---|---|
| Mainline PV role | reconstructed full-year PV | reconstructed full-year PV (Sec 12, Sec 14, P7) | YES |
| **P1-E historical boxed equation** (the R1 failure point) | §4.1.3 boxes `PV_t^{base}=\widehat{PV}_t^{winter,recon}` for `{pre_system, missing_winter}` | P1-E retains the historical `PV_t^{base}=0` for the same index set **but labels it HISTORICAL v7.1/v7.2 and SUPERSEDED and states the current §4.1.3 assignment inline** | YES — no competing current prescription remains |
| **P1-E sensitivity-branch wording** (the R1 failure point) | reconstructed PV is mainline; zero-winter is sensitivity | P1-E scopes the sensitivity-branch statement to Framework v7.2 and states the v7.3 reversal in a separate "Current role" subsection | YES |
| Zero-winter role | conservative stress/sensitivity | conservative stress/sensitivity (Sec 12, Sec 14, P7) | YES — **SUPERSEDED**: current v7.4 role is historical conservative validation / provenance evidence (§20.1) |
| Epistemic reconstruction boundary | mandatory sentence, model-based/not observed/not exact/not recovered | same sentence reused verbatim (Sec 14, P7) | YES |
| Historical 17a/17b/17c roles | preserved; not retroactively promoted | preserved identically (P7-A/B/C/D, historical-evidence matrix) | YES |
| Outage adequacy claim | conditional on accepted planning estimate; not probabilistic; not islanding proof | same boundary restated (Sec 14 new bullet) | YES |
| Layer B baseline | same reconstructed-mainline artifact, not zero-winter | referenced via Sec 12 same-artifact row; exact formula remains Framework-owned | YES |
| Observed/billing calibration boundary | observed Load/PV only; kappa unchanged by promotion | unchanged (P1/P2 untouched); no Registry claim contradicts this | YES |
| Future canonical-input status | `NOT_YET_CREATED / NOT_YET_AUTHORIZED` | same, as of R3 authoring | YES — **SUPERSEDED**: the accepted planning input now exists and is `CLOSED / ACCEPTED` (§17.7, §20.4, [P7] P7-E) |
| Final81 status | not authorized under v7.3 | same, as of R3 authoring | YES — **still not authorized**: Full81 is `NOT_YET_EXECUTED` under v7.4, while the accepted core-three is `CLOSED / ACCEPTED` (§20.4) |

**Sweep scope (as re-derived for R3; historical).** This R3-era sweep covered the whole Registry v7.3 R3 document, including every location that states a `PV_t^{base}` assignment, a mainline/sensitivity role, or a zero-availability treatment for the 1,463-hour block, plus every occurrence of `current`, `source of truth`, `authoritative`, `authority`, `accepted`, and `specification`. It explicitly covers the document header, source manifest, supersession rule, audit-status rule, [P1]/P1-E, Sec 17 status table, and Framework-to-Registry coverage. No sentence assigns current methodology authority to Framework v7.2; its surviving authority references are explicitly historical. No Framework/Registry contradiction was found in R3.

## 17.10 Stale-wording audit disposition

A complete, freshly re-derived stale-wording and authority-wording inventory of the **Registry v7.3 R3 document** was recorded in the R3 checkpoint (`docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_r3_2026-09-23.md`); that record is historical and is not restated here. The corresponding inventory for **this Registry v7.4 Candidate R1 document** is recorded in the Candidate R1 checkpoint (`docs/checkpoints/literature_evidence_registry_v7_4_framework_alignment_candidate_2026-09-26.md`), again not duplicated here to avoid a second, potentially drifting count. Acceptance target for both: zero Category-D (stale/contradictory/ambiguous) occurrences.

The R1 checkpoint's `D = 0` certification is **withdrawn and superseded** because it misdescribed R1's own bytes. The R2 checkpoint's `D = 0` / no-contradiction certification is also **withdrawn and superseded** because it failed to classify R2's inherited unscoped current-authority statement. The R3 result is freshly derived from R3 bytes using the expanded scientific-role plus authority-wording term set and is recorded in the R3 checkpoint.

## 17.11 Registry v7.3 R3 candidate disposition（historical record）

The disposition recorded **for Registry v7.3 R3 at its authoring time** was:

> **LITERATURE / EVIDENCE REGISTRY V7.3 R3 RECONSTRUCTED-PV MAINLINE ALIGNMENT -- CANDIDATE PASS**

That was a producer-side disposition meaning the R3 document was internally complete and consistent with accepted Framework v7.3. **Registry v7.3 R3 has since been independently accepted and is `CLOSED / ACCEPTED`.** The disposition of **this** document — Registry v7.4 Candidate R1 — is stated in §20.9 and is **CANDIDATE ONLY**.


---

# 18. R1 → R2 candidate lifecycle record (failed-candidate provenance)

This section exists so the Registry v7.3 lifecycle is not silently rewritten. R2 is a **successor
candidate**, not a silent replacement of R1.

## 18.1 Failed R1 candidate identity

| Artifact | SHA-256 | Status |
|---|---|---|
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23.md` | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` | **FAILED independent acceptance — immutable provenance; retained byte-identical; must not be cited as current** |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_2026-09-23.md` | `301b931a3b7ea4b0c981079789e66a69e5571294a0d29467bd0c6c262c17fe2d` | Failed R1 checkpoint — immutable provenance; its `D = 0` certification is withdrawn and superseded |
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` | **FAILED independent acceptance — immutable provenance; retained byte-identical; superseded by R3** |

Neither R1 artifact was edited, repaired, renamed, or deleted in producing R2.

## 18.2 Why R1 failed

R1 failed independent acceptance on two linked defects, both confirmed against R1's primary bytes.

**Defect 1 — unscoped P1-E wording (Category D stale wording).** R1's P1-E retained, in unscoped
present tense, two statements of the superseded v7.2 role:

- `Mainline remains:` followed by a boxed \(PV_t^{base}=0\) for the `pre_system` / `missing_winter`
  index set — directly contradicting accepted Framework v7.3 §4.1.3's boxed
  \(PV_t^{base}=\widehat{PV}_t^{winter,recon}\) over the identical 1,463-hour index set, in the same
  tense and the same display form;
- "A CWA winter alternative must first pass block/month holdout validation and **remains a separate
  sensitivity branch**" — the inverse of the v7.3 role assignment.

R1 did add a forward reference beneath these, but that reference scoped neither statement: its own text
said it "does not alter the Scripts 02-05 finding above" and that the finding "remains true under
Framework v7.3". R1 applied correct temporal scoping in Sec 14 and Sec 15 while leaving P1-E — the
document's most load-bearing statement of the old role — unscoped.

**Defect 2 — inaccurate self-audit certification.** R1's checkpoint certified `D = 0` on the basis of
a description of R1's own bytes that was wrong in three respects: it located the boxed equation at a line
that in fact holds an unrelated [P2] calibration sentence; it asserted the forward reference
"immediately" followed the equation when two paragraphs intervened; and it treated the forward
reference as scoping the equation when that reference disclaimed exactly that effect. R1's Sec 17.9
contradiction sweep and Sec 17.3 coverage matrix were correspondingly under-scoped: both surveyed only
Sec 12, Sec 14 and P7, and neither covered P1-E.

## 18.3 What R2 changes

R2 changes **only** what is required to clear those defects and the advisory precision items raised in
the same audit. It introduces no methodology change, reopens no closed decision, and alters no
evidence role beyond the already-accepted reconstructed-PV alignment.

| # | Change | Driver |
|---|---|---|
| 1 | P1-E restructured into explicit "Historical role (Framework v7.1/v7.2, superseded)" and "Current role (accepted Framework v7.3)" subsections; historical boxed equation retained verbatim but labelled HISTORICAL and SUPERSEDED, with the current §4.1.3 assignment stated inline for the same index set | Defect 1 |
| 2 | P1-E sensitivity-branch statement past-scoped to Framework v7.2; the v7.3 reversal stated separately | Defect 1 |
| 3 | Sec 17.3 coverage matrix rebuilt from scratch; rows now name both historical text and current-role interpretation, and P1-E is a required mapping location | Defect 2 |
| 4 | Sec 17.9 contradiction sweep re-scoped to the whole Registry, with explicit P1-E rows | Defect 2 |
| 5 | Sec 17.4 historical-preservation matrix gains explicit P1-E rows | Defect 2 |
| 6 | Sec 17.10 withdraws the R1 `D = 0` certification and points to the R2 re-derivation | Defect 2 |
| 7 | P7-C legacy provenance note expanded from one field to the full enumerated set of legacy branch-semantics fields, with the canonical-rebuild consequence stated | Audit advisory |
| 8 | P7-C `winter_pv_sensitivity_method` scope corrected (file-wide on 8,760 rows; the applied-flag delimits the 1,463-hour block) | Audit advisory |
| 9 | P7-D `pv_used_kwh` delta corrected: available-energy delta is identical across both cases, used-energy delta is not; the EOB difference is exactly its curtailment increase | Audit advisory |
| 10 | Header, lineage, source manifest and supersession rule record the R1→R2 lifecycle | §4 lifecycle requirement |

## 18.4 What R2 does not change

No methodology decision, equation, parameter, tariff or cost basis, degradation semantics, preprocessing
rule, Layer A/B boundary, solver setting, or production parameter is changed. A1–A4, B1–B2,
Gate 1 and Gate 2 remain closed and are not reopened. Step 17a's historical `PASS_FOR_SENSITIVITY`
verdict is preserved unchanged and is not retroactively inflated. No external-literature record's
supported claim is strengthened. No canonical artifact was created, no production routing was changed,
and no solve was performed.

## 18.5 R2 status

R2 failed independent acceptance because it inherited an unscoped sentence assigning current methodology
authority to Framework v7.2. It remains immutable failed-candidate provenance and is not the evidence
source of truth. **(Historical status note, past-scoped:** at the time this record was written, Registry v7.2
was the last accepted evidence source of truth pending independent acceptance of a v7.3 Registry successor.
That is no longer the current state — **Registry v7.3 R3 is now `CLOSED / ACCEPTED` and is the current
evidence authority**; see §17.7 and §20.4.**)**

---

# 19. R2 → R3 minimal authority-scoping correction record

R3 is a new additive successor candidate. It does not overwrite, repair, rename, or delete R1 or R2.

## 19.1 R2 STOP identity and root cause

| Artifact | SHA-256 | Status |
|---|---|---|
| `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r2.md` | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` | **FAILED independent acceptance — immutable provenance** |
| `docs/checkpoints/literature_evidence_registry_v7_3_reconstructed_pv_alignment_candidate_r2_2026-09-23.md` | `5b9f063709b680f8099d72ee440d9be6be02687e82476267903f95be8f416917` | Failed R2 checkpoint — immutable provenance; its `D = 0` / no-contradiction certification is withdrawn |

R2's audit-status block stated, without historical or superseded scoping, that Framework v7.2 and
Registry v7.2 were the only current mainline specification/evidence sources. That statement contradicted
R2's own source manifest and status table, both of which correctly identified Framework v7.3 as the
accepted methodology authority. The R2 independent audit therefore returned STOP.

## 19.2 Exact R3 correction

R3 replaced only that ambiguous current-authority rule with explicit temporal separation. **The five bullets
below are quoted as the wording R3 introduced at that time; they are a historical record of that correction,
not a statement of current authority** — for current authority see §0 (coding source-of-truth rule), §17.7,
and §20.4:

- under the v7.2 authority state, Framework v7.2 and Registry v7.2 were the then-current pair;
- under the (then-)current v7.3 transition state, Framework v7.3 is the accepted methodology source of truth;
- Registry v7.2 remains the last accepted evidence source until a v7.3 Registry successor passes
  independent acceptance;
- Registry v7.3 R3 is a candidate only;
- Framework v7.2 is a historical methodology predecessor, not current methodology authority.

Dependent edits are limited to R3 identity, R1/R2 lifecycle provenance, the Sec 17 status table, and the
fresh consistency/stale-wording audit statements. P1-E, P7, all 17a/17b/17c evidence roles and numerical
values, Script 14a references, [L1], external-literature records, and every non-PV methodology/evidence
role are preserved from R2.

## 19.3 R3 status

At the time this record was written, R3 was a **candidate only**: not self-accepting, and not the evidence
source of truth until an independent, read-only audit accepted it, with Registry v7.2 remaining the last
accepted evidence source until then. No canonical artifact was created, no production routing was changed,
and no solve was performed in that pass.

**(Current status, superseding the paragraph above for current-status purposes:** Registry v7.3 R3
**passed** independent acceptance and is **`CLOSED / ACCEPTED`** — the current evidence authority until
this Registry v7.4 Candidate R1 is independently accepted. Registry v7.2 is a historical accepted
evidence predecessor only. See §17.7 and §20.4.**)**


---

# 20. Framework v7.4 evidence-role / claim-boundary alignment freeze

This section is the additive evidence-role and claim-boundary delta of **Registry v7.4 Candidate R1**
relative to the **accepted, immutable Registry v7.3 R3**, aligned to the **CLOSED / ACCEPTED
Framework v7.4**. It is the **current** alignment record and governs wherever §17 (the inherited v7.3
record) could be read as differing. It changes **no equation, no parameter, no numerical setting, no
solver setting, no production input, no accepted numerical result, and no external-literature source
role outside the three authorized categories**.

## 20.0 Successor identity and authorized change scope

| Item | Value |
|---|---|
| This document | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` |
| Formal future evidence-version name | **Registry v7.4** (never “Registry v7.4 R1”) |
| Candidate revision identifier | **Candidate R1** — provenance revision only; not a formal evidence-version number |
| Lifecycle status | **CANDIDATE** (not `CLOSED`, not `ACCEPTED`, not `FINAL`, not `PROMOTED`) |
| Direct predecessor | `docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md` |
| Predecessor accepted SHA-256 | `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d` |
| Predecessor status | **CLOSED / ACCEPTED**; immutable; **current accepted evidence authority until this candidate is independently accepted**; no byte modified by this pass |
| Successor type | **ADDITIVE SUCCESSOR** (inherits Registry v7.3 R3 in full; not a rewrite) |
| Alignment target | **Framework v7.4** — `docs/research_framework_v7_4_2026-09-26_r2.md`, SHA-256 `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273`, **CLOSED / ACCEPTED** |
| Framework acceptance evidence | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` (SHA-256 `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f`); `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` (SHA-256 `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33`) |
| Current accepted methodology authority | **Framework v7.4** |
| Current accepted evidence authority | **Registry v7.3 R3** (not this document) |
| Self-acceptance | **NOT PERFORMED**; the authoring pass has no such authority |
| Independent audit | **REQUIRED** before promotion to evidence authority |
| New external literature sources | **0** |
| New / changed model equations | **0 / 0** |
| New / changed numerical parameters | **0 / 0** |
| Solves of any kind | **0** |

**Exactly three** substantive change categories are authorized in this successor, matching the three
accepted Framework v7.4 categories:

| Category | Change |
|---|---|
| **A** | zero-winter **current role** → historical conservative validation / provenance evidence |
| **B** | formal, internally consistent **observed-vs-planning PV epistemic routing** in the evidence layer |
| **C** | **\(\kappa\)** historical-calibration / planning-use **claim boundary**, without recalibration |

Beyond these three — and the dependent current-authority/status, project-evidence-authority, and
version/provenance plumbing required to express them — **all Registry v7.3 R3 evidence content is
inherited unchanged**. There is **no fourth scientific change category**.

## 20.1 CHANGE A — zero-winter evidence role

**Current role:**

> **zero-winter = historical conservative validation / provenance evidence supporting the
> reconstructed-PV promotion / adjudication decision.**

Under the current methodology authority, zero-winter is explicitly **not**:

1. a mandatory EOB sensitivity;
2. a mandatory Layer A sensitivity;
3. a mandatory Layer B sensitivity/stress;
4. an equal-status alternative planning baseline;
5. a mandatory future downstream scenario.

No new zero-winter EOB, Layer A, or Layer B solve is required. **No other sensitivity replaces it**: the
minimum-sensitivity inventory is net one item shorter, with no equal-count substitution.

**Preservation requirements (all mandatory).**

- The existing reconstructed-vs-zero-winter evidence — Step 17a long-block/monthly holdout validation,
  the original and corrected Step 17b artifacts, and the Step 17c paired comparison — **remains valid
  historical project validation / adjudication evidence** and is preserved in full ([P7]).
- Historical zero-winter evidence, artifacts, manifests, checkpoints, and audits **must not** be deleted,
  overwritten, renamed, reclassified, or removed from the evidence lineage; each keeps its original
  acceptance boundary.
- The v7.2 mainline role and the v7.3 conservative-stress/sensitivity role **remain true as past-scoped
  historical statements** and are deliberately retained ([P1] P1-E, §17.5, §17.7, §18, §19).
- No new zero-winter experiment is created by this pass. A zero-winter branch may be restarted only on a
  **separately justified future reason**, as a fully traceable and **separate** branch never cross-wired
  into a planning-layer consumer.

**What this update removes.** Only current-prescriptive wording that would still make a downstream
zero-winter sensitivity **mandatory** — specifically the v7.3-era `IMPLEMENTATION / VALIDATION PENDING`
winter-PV sensitivity item (§0 audit-status rule) and the [P6] remaining-gates winter-PV sensitivity item.

**Historical truthfulness table.**

| Authority | zero-winter role under that authority | Scope |
|---|---|---|
| Framework v7.2 | mainline | **historical** (past-scoped; still true as history) |
| Framework v7.3 | conservative stress/sensitivity | **historical** (past-scoped; still true as history) |
| **Framework v7.4 (current, accepted)** | **historical conservative validation / provenance evidence** | **current prescription** |

**Cross-document note.** `docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md` §E.2 and the
accepted Registry v7.3 R3 bytes record zero-winter as `conservative stress/sensitivity`. Those were
**correct statements under the v7.3 authority** and their bytes are **not modified**. Accepted Framework
v7.4 §36.1 supersedes that current-prescriptive role assignment additively, and this §20.1 is the
corresponding Registry-side alignment.

**Registry-side locations updated for Change A:** §0 audit-status rule; [P1] P1-E (superseded-box note,
v7.3 role-reversal subsection retitled and past-scoped, new “Current role — under accepted Framework
v7.4” subsection); [P6] remaining implementation/validation gates; [P7] evidence-role summary; §12
claim-to-source rows; §14 「可以寫」/「不要寫」; §15; maintenance guardrails; §17.1 / §17.5 / §17.7.

## 20.2 CHANGE B — observed-vs-planning PV epistemic routing

Framework v7.4 §4.1.1-R / §36.2 formalizes two epistemic layers. This Registry represents the same
distinction as an **evidence-routing and claim boundary**; it does not restate or own the equations.

| Layer | Question it answers | Data identity | Evidence records in this Registry |
|---|---|---|---|
| **HISTORICAL EMPIRICAL / CALIBRATION** | “what actually happened?” | **observed data wherever valid** | [P2] \(\kappa\) calibration (\(P_t^{grid,hist}=\mathrm{observed\_load\_kw}_t-\mathrm{observed\_pv\_kw}_t\)); [I1] 15-min institutional basis; [I3]/[I4] billed-demand target and usage-period semantics; [P6] 13b/13c Taipower tariff-registry and bill-component regression; any “what actually happened” historical empirical check |
| **PLANNING / COUNTERFACTUAL MODEL** | “under this design and these assumptions, what is the planning outcome?” | **accepted reconstructed full-year PV** — a single artifact identity | [P1] P1-E planning-baseline assignment; [P7] promotion evidence; **[P7] P7-E accepted planning artifact**; §12 planning rows |

**Explicit planning-layer consumers.** EOB; Layer A; Full81; \(R(\alpha,\beta)\); \(P^{out}\);
binding-outage identification/classification; Layer A outage consistency replay; baseline Layer B; and all
downstream planning scenarios unless a scenario is **explicitly declared** an alternative.

**No hybrid routing is authorized.** Specifically prohibited: crediting reconstructed winter PV in
EOB/economics while reverting Layer A or Layer B adequacy to zero-winter or any **other** annual PV
identity over the same 1,463 hours. The whole planning layer shares one artifact identity; the whole
historical layer uses observed identity. This prohibition is **not** relaxed by the Change A role update.

**Required and prohibited descriptions of the accepted reconstructed full-year PV.**

| Must be described as | Must not be described as |
|---|---|
| model-based | observed historical PV |
| weather-informed | exact ground truth |
| separately validated | exact recovery of the unavailable historical series |
| best-estimate planning baseline | online forecast information |

**Boundary statements.**

- Historical empirical / calibration claims **must not** silently use reconstructed PV as if it were
  observed. Observed columns remain immutable; only the planning-baseline layer carries the
  reconstruction ([P1], [P7] P7-C verified `observed_pv_kw` untouched over the 1,463-hour block).
- Planning / counterfactual claims **must not** silently revert to zero-winter or to any other annual PV
  identity.
- The reconstruction is a **retrospective planning-baseline construction**, not online forecast
  information, and confers no operator information advantage at the time of any historical event. Because
  it applies uniformly to every planning-layer comparison, it creates no PV-identity baseline asymmetry —
  but planning conclusions therefore remain **model-conditional**.
- **This is a claim/evidence-routing alignment only.** No equation is changed, and the Registry does not
  itself prove routing compliance; that is an implementation/production-routing audit outside Registry
  scope. The `surplus_pv_recharge=False` semantics and every Layer A/B formula remain Framework-owned and
  unchanged.

## 20.3 CHANGE C — \(\kappa\) historical-calibration / planning-use claim boundary

The full Registry-side statement is in **[P2]**, subsection “\(\kappa\) historical-calibration /
planning-use claim boundary”. This is the freeze statement.

**\(\kappa\) is not recalibrated.** The estimator, calibration sample, calibration period, calibration
basis, and accepted production value are **unchanged**.

| Item | Status |
|---|---|
| estimator | **UNCHANGED** — through-origin least squares |
| calibration period / sample | **UNCHANGED** — the ten 2025/01–2025/10 `pv_status=valid` usage months |
| calibration basis | **UNCHANGED** — observed valid historical Load, observed valid historical PV, observed historical billing/usage-period evidence, and the accepted billing-demand calibration procedure |
| production value | **UNCHANGED** — implementation identity `1.0103668594376984`; governance shorthand `1.0103668594`; rounded presentation `1.01037`. **These are the same accepted parameter at different display precision**, recorded only to fix the claim boundary |
| scripted-reproduction requirement | **UNCHANGED** — not a hard-code; future reruns rebuild the ten \((H_m,B_m)\) pairs from the canonical input + billing registry |

**Epistemic boundary.** Historical \(\kappa\) calibration answers a **historical billing-representation
question**; the accepted reconstructed full-year PV answers a **planning-baseline question**. They sit in
different epistemic layers (§20.2) and do **not** contradict each other. Therefore the accepted
reconstructed planning PV **does not redefine \(\kappa\)**, **does not re-estimate \(\kappa\)**, and
**does not retroactively replace observed historical PV** in \(\kappa\) calibration or replace its
calibration sample or target.

**Claim boundary.** \(\kappa\) **is** a billing-demand representation proxy. \(\kappa\) is **not** a
15-minute chronology reconstruction, **not** physical sub-hourly power validation, **not** evidence that
hourly BESS sizing captures all instantaneous peaks, and **not** proof of exact physical demand
chronology. The existing temporal-resolution literature **[R28]** and **[R29]** keeps its existing
limitation/context evidence role, unchanged and undiminished; \(\kappa\) must never be cited to override
those limitations. The formal wording remains **“calibrated hourly proxy for the 15-minute billing
demand”**.

## 20.4 Current authority and execution status

| Layer | State |
|---|---|
| **Framework v7.4** | **CLOSED / ACCEPTED** — current methodology authority |
| Framework v7.3 | `CLOSED / ACCEPTED` historical methodology predecessor; no longer current authority |
| Framework v7.2 | historical methodology predecessor only |
| **Registry v7.3 R3** | **CLOSED / ACCEPTED** — **current evidence authority** until this candidate is independently accepted; immutable |
| **Registry v7.4 Candidate R1 (this document)** | **CANDIDATE ONLY** — not accepted; cannot self-promote; independent read-only audit required |
| Registry v7.3 R1 / R2 | failed immutable provenance; never citable as current |
| Registry v7.2 | historical accepted evidence predecessor only |
| **Accepted reconstructed planning input** | **CLOSED / ACCEPTED** — `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`; SHA-256 `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428`; role `reconstructed_pv_mainline`; 8,760 rows |
| Corrected Step 17b artifact | **historical promotion-source lineage / project evidence only**; **not** the current canonical planning input |
| **Accepted EOB** | **CLOSED / ACCEPTED** — `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556` |
| **Accepted core-three** | **CLOSED / ACCEPTED** — `results/layer_a/final_81_v7_3/runs/20260925T062317399837Z_bb564f7b55`; LOW \((\alpha=0.60,\beta=4\,\mathrm{h})\), CENTRAL \((\alpha=0.80,\beta=8\,\mathrm{h})\), HIGH \((\alpha=1.00,\beta=12\,\mathrm{h})\) |
| **Full81** | **`NOT_YET_EXECUTED`** and not authorized — a **different** execution state from the accepted core-three |
| Layer A robustness / preregistration checkpoint | `NOT_YET_CREATED` |
| Final cross-document alignment audit | `NOT_YET_EXECUTED` |
| Production-authority re-freeze under v7.4 | `NOT_YET_PERFORMED` |
| New zero-winter solve requirement | `NOT REQUIRED` (§20.1) |

**Status-semantics rule (must not be conflated).** The accepted EOB and core-three **completion manifests
retain the execution-time status `COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE`**. That is immutable
historical fact about what those manifests record, and it is **not** an error. Their **current governance
lifecycle status is `CLOSED / ACCEPTED`**, established later by separate governance closure. This Registry
does **not** claim the manifests themselves contain `CLOSED / ACCEPTED`, and no manifest byte is modified.

**Do not group the accepted core-three with Full81 as jointly pending.** Core-three is accepted; only
Full81 is `NOT_YET_EXECUTED`.

## 20.5 Framework v7.4 claim-to-evidence coverage

Every changed Framework v7.4 claim has a defensible Registry representation. **No external literature is
invented or stretched** to support any NTUST-specific fact: exact NTUST parameter values, the exact
promotion decision, the exact reconstructed annual artifact, and the exact EOB/core-three results are
**project evidence**, never external-literature facts.

| Framework v7.4 claim | Evidence class | Registry record | Boundary |
|---|---|---|---|
| **CHANGE A** — zero-winter current role = historical conservative validation / provenance evidence | C (Framework decision) + B (project evidence) | §20.1; [P1] P1-E “Current role — under accepted Framework v7.4”; [P7] Step 17a / corrected 17b / Step 17c records and evidence-role summary; §12 zero-winter rows; §14; §17.5 | the role assignment is **Framework** authority, not a Registry decision and not a literature claim; Step 17a’s `PASS_FOR_SENSITIVITY` is not retroactively inflated; zero-winter is never a claim of physically zero generation |
| **CHANGE B** — observed-vs-planning epistemic routing; single accepted planning identity; no hybrid routing | C (Framework) + A (reconstruction/validation literature) + B (project evidence) | §20.2; [R21]–[R23], [R32]–[R33], [I5] (existing roles unchanged — reconstruction principles, weather/irradiance→PV estimation, model-selection logic, official CWA provenance); [P1] P1-C/P1-E; [P7] P7-A/P7-C/P7-D; **[P7] P7-E accepted planning artifact**; §12 routing row | literature supports the **modeling direction and validation logic only** — it never certifies the NTUST long block, the exact coefficients, or the accepted artifact. Registry restates the routing as a claim boundary; equations and routing enforcement stay Framework/implementation authority |
| **CHANGE C** — \(\kappa\) historical-calibration vs planning-use claim boundary, no recalibration | C (Framework) + B (project calibration) + A (temporal-resolution literature) | §20.3; [P2] \(\kappa\) claim-boundary subsection and 方法定位 / 不能支持 lists; [I1], [I3], [I4]; **[R28]**, **[R29]** (roles unchanged); §12 \(\kappa\) rows; §15 | [R28]/[R29] do **not** supply \(\kappa\), its estimator, or its coefficient, and are **not** weakened by it; \(\kappa\) is site-specific project evidence and never a Taipower or literature universal coefficient |
| Dependent current-authority / project-evidence status | C (Framework) + project evidence | §20.0; §20.4; §0 coding source-of-truth rule; [P6] remaining gates; [P7] P7-E; §15; §17.7 | no status is fabricated as complete; execution-time manifest status is distinguished from governance lifecycle status |

**Evidence-gap result.** No accepted Framework v7.4 claim was found to lack a defensible basis in existing
literature, official sources, accepted project evidence, or accepted primary artifacts. **Zero new
external literature sources** were required, sought, or added.

## 20.6 Existing literature and evidence roles — preserved unchanged

Outside categories A/B/C, every literature role, official-source role, project-evidence role,
claim-to-source row, and claim boundary inherited from Registry v7.3 R3 is preserved. In particular, the
accepted distinctions around the following are **unchanged and not re-debated**:

SOC mainline (10–90%) vs sensitivity (20–80%); efficiency evidence (\(\eta_c=\eta_d=0.90\), [R30] with
[T2] sanity check); PNNL vs NREL cost roles ([T1]–[T3]); Xu degradation semantics ([R20], [T4]); rainflow
ex-post role ([R31]); constant reserve floor vs variable-floor robustness ([R7], [P4]); annual reserve vs
outage replay ([P4]); annual cyclic state vs outage wrap ([R11], [P4]); Load and PV preprocessing rules
([P1], [R21]–[R23], [R32]–[R33], [I5]); cost-scale evidence ([R34], [T2], [P6]); monetary basis
([R35]–[R36], [T5], [P6]); the hourly temporal-resolution limitation ([R28]–[R29]); tariff / billing-period
evidence ([I1]–[I4], [P6]); AC/DC semantics; [L1] legacy lineage; and the §0.1 v7.2 conflict-resolution
summary.

No source is re-roled because a newer source exists; no Q1 or journal-status claim is altered; no modeling
precedent is upgraded into a universal engineering standard; no senior-thesis or prior-student work
displaces primary technical, cost, or regulatory evidence; and official claims remain tied to official
sources.

## 20.7 Leakage / information-advantage / claim audit

Registry wording was inspected specifically for the following failure modes. Each is excluded, with the
controlling location named.

| Failure mode | Disposition | Controlling location |
|---|---|---|
| reconstructed PV mislabeled observed | excluded | §20.2 required/prohibited description table; [P1] P1-E; §14 mandatory epistemic sentence and 不要寫 entries; §12 |
| retrospective reconstruction mislabeled online forecast | excluded | §20.2 boundary statements; §14 可以寫 / 不要寫 entries |
| historical calibration using future planning reconstruction | excluded | §20.3 prohibition; [P2] canonical historical data boundary and claim-boundary subsection; maintenance guardrails |
| look-ahead hidden as empirical evidence | excluded | §20.2; the two-layer routing keeps every “what actually happened” claim on observed data |
| perfect-information benchmark mislabeled deployable operation | excluded | inherited Layer B capability-upper-bound framing ([R6], §14 Layer B bullets); not expanded by this pass |
| \(\kappa\) mislabeled sub-hourly physical validation | excluded | §20.3; [P2] 不能支持 list; §12 \(\kappa\) rows; §14 不要寫 entries |
| literature precedent overstated as exact NTUST validation | excluded | §20.5; §17.8; every source’s own 不能支持 / boundary text, inherited unchanged |
| planning evidence overstated as historical measurement truth | excluded | §20.2; §14 model-conditional adequacy bullet; [P7] “not authorized to claim” columns |
| implementation status conflated with methodology authority | excluded | §0 coding source-of-truth rule; §20.0; §20.4 status-semantics rule; §17.7 two-column table |

## 20.8 Inherited unchanged — freeze inventory

The following are inherited from Registry v7.3 R3 **unchanged**, and this successor does not reopen any of
them: research questions; research positioning; Layer A / Layer B / DG boundaries; the \(\alpha\) grid;
the \(\beta\) grid; the \(9\times9=81\) case universe; valid-start non-circular semantics; stationary
LFP; \(SOC_{min}=0.10\); \(SOC_{max}=0.90\); usable-energy semantics; \(\eta_c=\eta_d=0.90\); the
AC/PCS-side power boundary; the battery-side stored-energy state; the constant worst-case reserve floor;
the reserve formulation; outage replay semantics; outage-replay initial-state and technical-lower-bound
semantics; tariff treatment; billing-period semantics; the annual regular contract-capacity treatment;
over-contract and non-duplication semantics; the degradation formulation; Xu-adapted intertemporal PWL
semantics; the rainflow ex-post role; the discount rate \(r=5\%\) (real); the 20-year horizon; \(CRF\);
the constant NTD-2023 monetary basis; the PNNL cost-package choice (10 MW-scale mainline, 1 MW-scale
sensitivity); `surplus_pv_recharge=False`; the Layer A equations; **A1–A4**; **B1–B2**; **Gate 1**; and
**Gate 2**.

**A1–A4, B1–B2, Gate 1 and Gate 2 remain CLOSED and are not reopened.** No literature is reinterpreted
in order to reopen a closed decision.

**NO new equation. NO equation rewrite. NO parameter change. NO new numerical sensitivity design. NO new
external literature source.**

## 20.9 Candidate disposition

The in-document status of this Registry successor is:

> **LITERATURE / EVIDENCE REGISTRY V7.4 FRAMEWORK-ALIGNMENT SUCCESSOR — CANDIDATE R1**

This disposition means only that the document expresses the three authorized Framework v7.4 alignment
categories and their boundaries. It is **not** evidence acceptance, **not** methodology acceptance,
**not** artifact promotion, **not** routing authorization, **not** a production-authority re-freeze, and
**not** authorization for any production run, Layer A preregistration, or Full81 execution.

> **Registry v7.4 Candidate R1 is NOT the accepted evidence authority. Registry v7.3 R3 remains the
> accepted evidence authority. An independent read-only audit of this candidate is required before it
> may become the evidence source of truth, and this candidate cannot self-promote.**

**Execution counters for this authoring pass:** `optimize()` calls = **0**; model constructions = **0**;
MILP solves = **0**; EOB reruns = **0**; core-three reruns = **0**; Full81 runs = **0**; sensitivity
solves = **0**; code changes = **0**; data changes = **0**; accepted-result changes = **0**.
