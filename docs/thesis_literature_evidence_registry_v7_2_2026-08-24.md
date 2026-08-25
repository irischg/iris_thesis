# Thesis Literature Evidence Registry v7.2

**Project:** Campus PV–BESS service-continuity planning with contract-capacity economics  
**Purpose:** Independent literature/evidence registry; intentionally separate from the research-framework MD.  
**Compiled:** 2026-08-04  
**Updated:** 2026-08-24 — Registry v7.2 aligned with Research Framework v7.2. It preserves the v7.1 evidence base while integrating post-v7.1 production evidence through Script 13c, the ex-ante PNNL cost-scale freeze (10 MW mainline / 1 MW sensitivity), constant-NTD-2023 monetary harmonization with a real 5% modeling discount rate, and the latest tariff/accounting traceability rules. A1–A4 and B1–B2 remain methodologically closed.

**Version lineage:** Registry v7.2 is the direct successor to `thesis_literature_evidence_registry_v7_1_2026-08-16.md` and aligns to `research_framework_v7_2_2026-08-24.md`. It does not reopen the v7.1 preprocessing, resilience, billing, degradation, or Layer A/B/DG method decisions. The substantive v7.2 changes are evidence-role and implementation-status updates required by Scripts 06–13c and the two post-v7.1 economic-integration gates: (1) cost-scale selection is frozen ex ante, with the PNNL 10 MW package as mainline and the 1 MW package as higher-cost scale-economy sensitivity; and (2) optimization-facing monetary terms are harmonized to constant NTD-2023, with the 5% discount rate interpreted as a real modeling rate.

> **Source manifest / provenance**
>
> | Source artifact | Role in v7.2 | SHA-256 |
> |---|---|---|
> | `thesis_literature_evidence_registry_v7_1_2026-08-16.md` | Immediate predecessor / evidence base | `9d90218a520b429fe07c081f26c282e68b5fa68d7537f97a13201719d3816c31` |
> | `research_framework_v7_2_2026-08-24.md` | Current framework alignment target | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |
> | Scripts 01–13c outputs | Project preprocessing / integration / parameter / tariff / regression evidence | tracked by repository artifacts / commit hashes |
> | `thesis_literature_evidence_registry_v7_2_2026-08-24.md` | Integrated successor / current registry source of truth | `SELF-HASH: record externally after repository commit` |
>
> **Supersession rule:** Framework v7.2 + Registry v7.2 control current implementation and claim mapping. v7.1 and earlier registry/framework versions remain for provenance, regression, historical lineage, or explicitly labeled legacy/comparison use only. In particular, v7.1's preliminary-optimized-\(P^B\)-dependent cost-bracket rule is superseded; no literature or project evidence may be used to reintroduce outcome-dependent cost-package selection without reopening the framework explicitly.

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
- `IMPLEMENTATION / VALIDATION PENDING`：方法已定，但 downstream production-interface、post-solve validation、rainflow、winter-PV sensitivity或 final rerun尚未完成。

目前不再把 \(\kappa\) reproduction、\(C_E,C_P,FOM,C_{rep}\) population、1 MW/10 MW package construction或 Xu semantics audit列為 pending：這些已由 post-v7.1 scripts 關閉。Gate 2 的 **方法**已關閉，但 official nominal Taipower tariffs → constant NTD-2023 optimization layer 的 machine-readable production conversion仍是 Script 14a 前置 implementation gate。

**Coding source-of-truth rule:** Framework v7.2 + Registry v7.2 are the only current mainline specification/evidence sources for implementation. Earlier framework/registry versions may be used only when v7.2 explicitly classifies them as legacy, replication, regression, provenance, historical lineage, or comparison material. Current script artifacts, not old framework constants, control exact production values.

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

Mainline remains:

\[
\boxed{PV_t^{base}=0}
\]

for these long-unavailable intervals, described as conservative zero **availability**, not observed physical zero generation.

The Script-04b result validates only the observed **3 h / 7 h short-gap shapes**. It does **not** validate CWA reconstruction for the 1,463-hour long block. A CWA winter alternative must first pass block/month holdout validation and remains a separate sensitivity branch.

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
- Script 14a production-interface preflight, including the constant-NTD-2023 Taipower tariff layer；
- EOB and 81-point Layer A production runs；
- post-solve exact modeled demand maxima；
- ex-post rainflow validation；
- winter-PV long-block alternative sensitivity。

These are **not new methodological blockers**.

**Evidence role:** **v7.2 economic/tariff implementation status and Gate 1–2 exact thesis-resolution source-of-truth.**

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

# 12. Claim-to-source map（v7.2 aligned）

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
| long unavailable winter PV = conservative zero mainline | **P1 + thesis scope decision** | 1,463 h以zero availability處理；short-gap validation不能外推成long-block reconstruction |
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
| \(\kappa\approx1.01037\) | **P2 + I3 + I1 + P6** | production scripted reproduction CLOSED；exact digits由audit output控制，仍為site-specific proxy |
| \(\kappa\) is billing proxy, not 15-min reconstruction | **P2 + R28, R29** | proxy corrects monthly billed-demand representation only; hourly operational limitations remain |
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
- “The 1,463-hour pre-system/winter PV-unavailable block remains **conservative zero availability** in the mainline; short-gap validation is not used as evidence for long-block reconstruction.”
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
- “因為 CWA 在 3 h / 7 h pseudo-gaps 勝出，所以 1,463 h winter block 也已被驗證可直接重建。”
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

# 15. 官方／場域／parameter evidence 狀態（v7.2）

## 已從 blocker 轉為 locked evidence / parameter-registry item

- **A1 efficiency**：\(\eta_c=\eta_d=0.90\) 已鎖定；R30 是 direct peer-reviewed precedent，T2/PNNL performance data只作 system-level sanity check；0.91/0.91 不再是 mainline。
- **A2 reserve/replay semantics**：constant worst-case reserve floor + separate outage replay 已鎖定；exact equations/6-point robustness由 P4 保存，R7只支持 preparedness trade-off。
- **Taiwan 15-minute maximum-demand settlement basis**：由 Taipower official rule 支持；hourly model不宣稱 exact 15-min reconstruction。
- **A3 tariff/CC/over-contract**：I3 已鎖定 usage-period indexing、one-regular-CC NTUST case boundary、four TOU maxima、non-duplication、2×/3×；I4作 billed-overall-max external corroboration。
- **High-voltage summer definition = 5/16–10/15**：由 Taipower official pricing information 支持。
- **\(\kappa\approx1.01037\)**：不是文獻值；P2 scripted reproduction 已 **CLOSED**，final source-of-truth為 production calibration audit output；future rerun仍須由 canonical inputs重建。
- **A4 exact billing diagnostics**：P5 已鎖定 post-solve exact maxima of the calibrated hourly proxy；不報 floating optimization epigraph。
- **hourly temporal-resolution limitation**：R28–R29 為主要近期文獻；它們不提供 \(\kappa\)，也不消除 sub-hourly limitation。
- **Blocker 2 / preprocessing empirical freeze**：P1 已以 Scripts 02–05 更新。Load production = same weekday ±6 weeks/K=1；PV donor ±30d/K5 mean = benchmark；PV short-gap production = CWA `hourly_ghi_ratio_median`；10 Load + 10 PV outage hours已重建；1,463 h long unavailable PV mainline維持zero availability。
- **PV reconstruction literature boundary**：R23保留solar-gap artificial-gap validation角色；R32–R33新增weather/irradiance→PV與multi-metric model-selection evidence；I5新增CWA官方資料來源。exact production model仍由P1控制。
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
- Do not use Script-04b short-gap results to justify long winter reconstruction without separate block/month holdout validation.
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
