# 研究框架 v7.1（2026-08-16，preprocessing empirical integration / traceability freeze）

> **Version lineage:** v7.1 is the integrated successor to `research_framework_v7_2026-08-14.md`. It incorporates the preprocessing empirical amendment `research_framework_v7_preprocessing_update_2026-08-16.md`, which records the completed Scripts 01–05 validation and production-reconstruction decisions. Except where the amendment explicitly supersedes v7 preprocessing/data-lineage wording, all v7 research questions, Layer A/B/DG boundaries, A1–A4 / B1–B2 methodological resolutions, tariff/billing rules, degradation formulation, cost methodology, equations, claim boundaries, and legacy-governance rules are retained unchanged.

> **Source manifest / provenance**
>
> | Source artifact | Role in v7.1 | SHA-256 |
> |---|---|---|
> | `research_framework_v7_2026-08-14.md` | Base authoritative framework | `08d5b76495173ccb8dde9ce5308f5d93d2f125020c19ba0836ceb0035efac5a2` |
> | `research_framework_v7_preprocessing_update_2026-08-16.md` | Empirical preprocessing amendment | `b777b826caa46135886e16d1dbb5e4685c60d46d0897c7df84ff8de2704ef7c6` |
> | `research_framework_v7_1_2026-08-16.md` | Integrated successor / new framework source of truth | `SELF-HASH: record externally after repository commit` |
>
> **Supersession rule:** From v7.1 onward, the two source artifacts above are retained for provenance/lineage only. For current methodology and implementation status, v7.1 controls. Earlier framework versions must not be used to infer, supplement, or override v7.1 mainline methodology or unresolved production values unless v7.1 explicitly labels them as legacy, replication, regression, provenance, historical lineage, or comparison material.

> **Current implementation status:** **Component preprocessing through Scripts 01–05 is CLOSED / PASSED; final integrated annual input and downstream production implementation are still pending.** v7.1 together with the current Literature/Evidence Registry remains the authoritative coding specification. Unchecked items in §32 are implementation, parameter-population, reproducibility, validation, integration, and final-rerun acceptance gates; they do **not** reopen A1–A4 or B1–B2.

## 校園 PV–BESS 服務連續性之成本–韌性規劃框架

> **文件用途**：本文件是研究規格書（research specification），用來鎖定研究問題、模型邊界、實驗順序、指標定義、驗證要求與舊結果處理方式。它不是論文章節全文，但可直接作為第一至四章的骨架。
>
> **版本原則**：v7.1 以 v7（2026-08-14）為完整 base framework，並整合 2026-08-16 preprocessing empirical amendment。A1–A4、B1–B2 仍視為 **methodologically closed**；本次不重新開啟 tariff、billing、degradation、cost、Layer A/B 或 DG 方法方向。新增的實質更新只限於：Scripts 01–05 preprocessing 已完成；Load short-gap production rule 由 NTUST pseudo-gap validation 鎖定為 same weekday ±6 weeks / K=1；PV short-gap production method 經 donor-vs-CWA head-to-head validation 改採 CWA `hourly_ghi_ratio_median`；long unavailable winter PV mainline仍維持 conservative zero；pre-v7 `annual_input_existing_pv.*` 不再因檔名而被視為 canonical。其餘 v7 方法決議、equations 與 claim boundaries 均保留。
>
> **文獻分流**：Blocker 1–5、7 的詳細文獻證據、來源頁碼與引用用途不在本框架重複展開；本文件只保留必要的方法選擇理由與 source-of-truth 類型。詳細文獻與參數 lineage 另存 literature/parameter registry。
>
> **本版核心更新**：
>
> 1. **A1 CLOSED — efficiency**：stationary LFP mainline 固定 \(\eta_c=\eta_d=0.90\)，AC/PCS-side charge/discharge power 與 battery-side stored-energy boundary 維持一致；0.91/0.91 與 0.95/0.90 不再是 mainline candidates。
> 2. **A2 CLOSED — reserve/outage semantics**：annual normal-operation optimization 維持 constant worst-case reserve floor \(e_t\ge SOC_{min}E^N+R\)；outage adequacy 以獨立 replay 實作，起始於最低 preparedness state，停電中只受 technical SOCmin 約束且不要求期末恢復 \(R\)。
> 3. A2 targeted robustness 只比較 constant reserve floor 與 perfect-information time-varying floor 於 6 個 \(3\times2\) points：\(\alpha=0.60,0.80,1.00\) × \(\beta=4,12\) h；不把它擴張成第二個 response surface。
> 4. **A3 CLOSED — tariff/CC**：NTUST mainline 只最佳化一個 annual regular contract capacity \(CC\)；supplementary half-peak / Saturday-half-peak / off-peak contracts 固定為 NTUST case values（0），四個 TOU periods 仍保留於 energy/billing logic；over-contract 依 Taipower period-specific threshold、non-duplication 與 2×/3× rules 實作。
> 5. billing month 與 usage period 分離；例如標題 2025/10 的帳單對應 2025/09/01–09/30 usage period。所有 bill-to-hourly joins 以實際 usage period 為準。
> 6. **A4 CLOSED — demand proxy diagnostics**：optimization 不再依賴可浮動的 monthly \(D_m^{proxy}\) 作報表值；cost-facing epigraph/exceedance variables 只服務 tariff constraints，solve 後由 optimized hourly grid profile ex-post 精確計算各 TOU period 與 overall monthly maxima。
> 7. 15-min billing-demand calibration 保留 site-specific \(\kappa\) 方法：以 2025/01–10 valid-PV usage months 的 observed historical grid import 對帳單四時段最高需量之 overall maximum 做 through-origin LS；現有 \(\kappa=1.01037\) 必須由 production `calibrate_kappa.py` 重現，而非 hard-code 為無 lineage 常數。
> 8. **B1 CLOSED — degradation**：主線採 PNNL DOD–cycle-life calibration + **adaptation of Xu et al.'s intertemporal convex PWL cycle-aging formulation**；segment energy states 必須跨時間延續。Harry-style hourly-reset PWL 排除作 mainline；linear throughput 僅保留 benchmark/equivalence check；full rainflow 不嵌入 optimization，只作 ex-post validation。
> 9. B1 effective breakpoints 固定為 \(b=(0,0.30,0.60,0.80)\)，原始五個 PNNL effective-DOD/cycle-life points仍完整保存在 registry。所有 \(\lambda_k\) 必須由 final \(C_{rep}\) 與 calibration table 自動生成，不 hard-code Harry-era 0.532/1.596/2.128。
> 10. degradation 的 DOD/segment energy 以 battery-side energy 計算；若 \(p_t^{dis}\) 是 AC-side，battery-side discharge 為 \(p_t^{dis}\Delta t/\eta_d\)。
> 11. **B2 CLOSED — no structural change**：annualized CAPEX + annual FOM + operating costs（含 cycling degradation）之 accounting structure 維持；不新增 explicit replacement/augmentation cash-flow stream。20-year horizon 是 financial analysis period，不是 battery 必須 physically survive 20 years 的 hard gate。
> 12. 正式 case year 維持 2024-11-01 00:00 至 2025-11-01 00:00（Asia/Taipei，hourly）；source hour-ending timestamp 轉為 interval-start 後再產生 calendar/TOU/billing labels。
> 13. BESS mainline CAPEX source仍為 PNNL v2024 LFP cost data；\(r=5\%\)、\(n=20\) yr、\(CRF=0.0802426\)。legacy 813.75／694.4／0.07 僅供 replication。
> 14. BESS site feasibility 仍不是 RQ、Layer A constraint 或 production blocker；結果定位為 modeled planning requirements。dense Layer A、fixed-design Layer B、DG external coverage sweep 與 claim boundary 維持不變。
> 15. hourly-resolution evidence 仍以 Omoyele et al. (2024) 與 Browne & Williams (2023) 支持 aggregation limitation；\(\kappa\) 仍是 NTUST site-specific empirical calibration，不是文獻 universal coefficient。
16. **Preprocessing empirical freeze**：Script 02 將 Load short-gap production rule 鎖定為 same weekday ±6 weeks / K=1 / same-day outside-gap RMSE；原 ±8 weeks / K=3 退為被 empirical validation 否決的 framework candidate。
17. **PV short-gap method selection**：Script 04 的 ±30 days / K=5 mean donor 保留為 validated benchmark；Script 04b 在相同 604 pseudo-events 上證明 CWA `hourly_ghi_ratio_median` 明顯改善 MAE、RMSE 與 event-energy error，因此 Script 05 production short-gap reconstruction 改採 CWA method。
18. **Data-integration status**：Scripts 01–05 component preprocessing 已通過；下一個 data gate 是由 `load_annual_baseline.*` + `pv_annual_baseline.*` 生成 final integrated annual input，重新建立 interval-start calendar/TOU/billing tags並完成 integration audit。

---
# 0. 研究狀態與決策分級

## 0.1 已鎖定的核心決策

下列內容除非發現程式、資料或 source transcription 錯誤，否則不再回到舊版：

- 研究主線為 **PV + BESS 的 zero-combustion service-continuity planning**；NTUST 是 demonstration case，不是研究問題本身。
- \(\alpha\) 與 \(\beta\) 是 decision-maker-specified planning targets，不是法定標準，也不是模型自行最佳化的偏好。
- Layer A 使用 dense \(9\times9=81\) 的 \(\alpha,\beta\) grid 與 case-year 內所有 valid historical outage starts 的 worst-case reserve；year-end 不做 circular wrap。
- BESS mainline technology 為 stationary LFP；\(E^N\) 為 installed/nameplate energy sizing variable，\(e_t\) 為 battery-side stored-energy state。
- 主線 \(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)，因此 \(E^U=0.8E^N\)。normal-operation reserve 必須位於 technical SOCmin 之上。
- charge/discharge power 以 AC/PCS-side 定義；**A1 已關閉：\(\eta_c=\eta_d=0.90\) fixed**，效率只套用一次，不做 efficiency curve mainline。
- **A2 已關閉**：annual optimization 與 outage replay 是兩個分離的 model stages。annual normal operation 使用 constant worst-case reserve floor；outage replay 從最低 preparedness state 開始，停電期間 reserve 可被使用，只維持 technical SOCmin。
- 正式 case year 為 **2024-11-01 00:00 ≤ \(t\) < 2025-11-01 00:00（Asia/Taipei）**，\(\Delta t=1\) h，\(T=8760\)。source hour-ending timestamp 轉 interval-start 後再產生 calendar/TOU/billing labels。
- observed Load/PV 與 planning-baseline Load/PV 分離；historical billing calibration 使用 observed series，annual planning 使用 baseline/available series。
- **A3 已關閉**：NTUST mainline 只最佳化一個 annual regular contract capacity \(CC\)；supplementary contracts 固定於 NTUST case values（0）；四 TOU periods、period-specific basic rates、non-duplication 與 2×/3× over-contract rules 保留。
- **A4 已關閉**：solver 內 cost-facing demand/exceedance variables 不當作 exact diagnostics；各 period/month maximum demand 一律由 optimized grid profile ex-post 重算。
- Taipower 15-min billing demand 使用 site-specific calibrated hourly proxy。現有 \(\kappa=1.01037\) 保留為待 scripted reproduction 的既有結果；production `calibrate_kappa.py` 必須由 2025/01–10 observed grid-import / billed-overall-max pairs 重新產生。
- **B1 已關閉**：mainline degradation = **PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation**；segment states 跨時間延續。Harry-style hourly-reset PWL 不作 mainline，linear throughput 只作 benchmark，rainflow 只作 ex-post validation。
- **B2 已關閉且不改總成本結構**：annualized CAPEX + annual FOM + operating costs（含 cycling degradation）維持；不額外加入 full replacement/augmentation cash-flow stream。
- high-voltage summer calendar 固定為 **May 16–October 15**，不得使用整月 shortcut。
- BESS mainline CAPEX source 為 PNNL v2024-derived energy/power planning package；\(r=5\%\)、\(n=20\) yr、\(CRF=0.0802426\)。
- Layer B 固定 Layer A 設計，不重新擴充設備；Layer B structured scenarios 不是可靠度機率。
- BESS site/fire-code/interconnection constraints 不進主線 optimization；輸出稱 modeled planning requirements，不稱 final recommended installation。
- existing emergency DG 不進 aggregate campus service mainline；hypothetical campus-serving DG 為獨立外生 coverage extension。
- DG extension 同時報告成本、燃料與 onsite CO₂，不強迫用任意碳價加權成單一 objective。

## 0.2 待 Layer A 完成後決定

- Layer B 最終使用 3、5 或 9 組 benchmark designs。
- benchmark designs 的實際 \((\alpha,\beta)\) 座標。
- Layer A 是否存在 knee / transition region。
- DG sweep 是否需要在某一區間做 5% 細化。
- 是否保留 24 h 作為 boundary case。

## 0.3 已定方法、待 implementation／parameter population 的項目

A1–A4、B1–B2 均 **methodologically closed**。下列事項屬 production implementation / reproducibility / final integration，不重新打開 blocker。

### 已完成：component preprocessing freeze

- **Scripts 01–05 component preprocessing is CLOSED / PASSED.**
- Script 01 formal observed input：`data/processed/ntust_case_year_observed.*`。
- Script 03 formal Load baseline output：`data/processed/load_annual_baseline.*`。
- Script 05 formal PV baseline output：`data/processed/pv_annual_baseline.*`。
- 已完成 canonical 8,760-hour interval-start observed dataset、observed/planning-baseline separation、Load short-gap validation + production reconstruction、PV donor benchmark、PV donor-vs-CWA head-to-head validation、PV short-gap CWA production reconstruction，以及 long unavailable PV conservative-zero assignment。
- 任何 pre-v7 pipeline 產生的既有 `annual_input_existing_pv.*` 皆視為 **legacy input artifact**；不得因檔名相同直接作 production canonical input。

### 下一個 data gate：final integrated annual input

由 current v7.1 preprocessing outputs 合併產生 final integrated annual model input，至少：

- combine current `load_annual_baseline.*` and `pv_annual_baseline.*`；
- preserve Script-01 observed columns unchanged；
- preserve Load/PV reconstruction provenance and long-PV status；
- from canonical interval-start timestamp regenerate calendar / summer / TOU / billing-period fields；
- assert exactly 8,760 consecutive hours, no duplicates/missing timestamps, observed equality, and no legacy baseline contamination。

只有通過此 integration audit 後，該 artifact 才能成為 downstream billing calibration、EOB、Layer A 與 Layer B 的 canonical annual input。

### 其餘尚待 production implementation / population

- 建立 `billing_demand_registry.csv`：以 **usage period** 而非 bill-title month 索引，保存 regular/supplementary CC、四 TOU billed maxima、overall billed maximum、tariff source 與 bill filename。
- 建立 `calibrate_kappa.py`：從 final integrated input 的 `observed_load_kw - observed_pv_kw` 與 billing registry 重建 2025/01–10 十組 \(H_m,B_m\)，輸出 ratios、residuals 與 through-origin \(\kappa\)；不得只 hard-code 1.01037。
- 從 PNNL v2024 cost data/工作簿填入正式 \(C_E,C_P,FOM,C_{rep}\) 與 currency/base-year metadata；不得回退 legacy annualized coefficients。
- 將 PNNL LFP DOD–cycle-life calibration table寫入 machine-readable parameter registry，並由 final \(C_{rep}\) 自動產生 effective PWL slopes \(\lambda_k\)。
- 實作 Xu-derived intertemporal segment states、aggregate SOC linking、segment-level charge/discharge dynamics 與 segment cyclic boundary；不得使用 hourly-reset Harry proxy 作 final mainline。
- 完成 ex-post rainflow/cycle-depth diagnostic，用於驗證 PWL aging cost 與 realized DOD distribution；不嵌入 optimization。
- 以 NTUST case-year bills + effective-date tariff tables實作四 TOU periods、regular CC、supplementary CC=0 case settings、period-specific basic rates、non-duplication、2×/3× over-contract rules；至少精確重現已核對的 September 2025 bill case。
- 完成 code audit：SOC bounds、reserve floor、annual-vs-outage state semantics、AC/DC efficiency、valid-start outage indexing、intertemporal PWL semantics、billing-period alignment、post-solve exact demand maxima。
- winter-PV alternative branch 必須先做與 long-block use case 相符的 block/month holdout validation，再跑 conservative-zero vs alternative reconstructed-PV economic sensitivity。
- DG CAPEX、FOM、fuel curve、diesel price 與 emission factor 仍需獨立完成 source/parameter audit。

# 1. 建議論文定位

## 1.1 核心問題

當一個大型用電場域希望在停電期間維持一定比例的服務，但又不希望主線依賴現地燃燒式備援時，PV 與 BESS 必須同時承擔：

1. 正常運轉下的電費、契約容量與削峰功能；
2. 停電發生前的能量儲備；
3. 停電期間的能量與瞬時功率供應。

因此，韌性不是額外加上一顆獨立備援電池，而是限制同一個 BESS 在平時可自由使用的程度，並可能要求更大的 energy capacity 與 power capacity。

本研究要量化的是：

> 在不同服務比例 \(\alpha\) 與設計停電時長 \(\beta\) 下，PV–BESS 系統需要增加多少儲能容量、功率容量與年度成本；這些固定設計在 PV 衰減與需求成長下何時失效；若允許 hypothetical DG，成本與現地碳排如何交換。

## 1.2 研究主張應控制在什麼程度

### 可以主張

- 提出一個結合台灣高壓用戶契約容量經濟與歷史 all-start outage adequacy 的應用型規劃框架。
- 量化 \(\alpha\)、\(\beta\) 對 BESS energy、power、contract capacity 與 cost premium 的影響。
- 辨識 marginal cost、binding mechanisms、knee 或 no-knee 結果。
- 分析固定設計對 PV deterioration 與 demand growth 的失效條件。
- 以 hypothetical DG extension 呈現 zero-combustion 與 fossil-assisted preparedness 的成本–排放權衡。

### 不應主張

- 不宣稱模型保證任何未來真實停電一定成功。
- 不宣稱 structured-scenario coverage 等於實際可靠度機率。
- 不宣稱 \(\alpha L_t\) 是完整的校園 critical-load inventory。
- 不宣稱沒有場地上限的結果就是校園應實際安裝的容量。
- 不宣稱 50% DG 是普遍最佳比例。
- 不宣稱由年度成本與單次事件排放形成的比值是無條件市場碳價。
- 不宣稱提出全新的 resilience theory 或 optimization algorithm。

## 1.3 題目方向（待老師定稿）

### 英文建議

**A Cost–Resilience Trade-off Framework for Campus PV–BESS Planning under Historical All-Start Outage Requirements: A Diesel-Backup Counterfactual**

### 中文建議

**基於歷史全年任意停電起點要求之校園 PV–BESS 成本–韌性規劃框架：柴油備援反事實分析**

也可弱化「任意」一詞，改成：

**校園 PV–BESS 服務連續性之成本–韌性規劃：全年停電起點適足性與柴油備援對照**

---

# 2. 研究問題

## RQ1：成本–韌性 response surface

在正常運轉成本最佳化中加入 \((\alpha,\beta)\) 服務連續性要求後：

- BESS energy capacity 如何變化？
- BESS power capacity 如何變化？
- contract capacity 如何變化？
- annualized total cost 與 resilience premium 如何變化？

## RQ2：容量與成本的結構性機制

- \(\alpha\) 主要推動 power requirement，還是 energy requirement？
- \(\beta\) 主要推動 energy requirement，還是也顯著改變 power requirement？
- resilience premium 主要來自 BESS CAPEX、正常營運彈性損失，或契約容量變化？
- response surface 是否存在 knee / threshold？若沒有，是否呈現穩定的邊際成本規律？

## RQ3：固定設計的 off-design capability

Layer A 選出的固定設計，在下列條件下：

- PV availability 下降；
- campus demand 成長；
- 不同 baseline outage archetype；

會從何時開始出現 service shortfall？其 ENS 與 worst-hour shortfall 為何？

## RQ4：DG-assisted counterfactual

若允許一個 hypothetical campus-serving DG，且 DG 容量以外生 coverage ratio 增加：

- BESS energy 與 power 可以下降多少？
- annual fixed preparedness cost 可以下降多少？
- 每次 outage 的柴油量與現地 CO₂ 增加多少？
- 是否存在成本快速下降後邊際效益遞減的 knee region？
- 結論對 BESS cost、DG cost 與 diesel price 是否穩健？

---

# 3. 研究邊界與核心定義

## 3.1 系統邊界

### 納入

- NTUST aggregate campus load（依實際 meter boundary）。
- 外生 PV profile 與固定 PV capacity。
- BESS energy capacity、power capacity 與 annual dispatch。
- grid import。
- annual regular contract capacity、TOU energy charge、basic charge、Taipower period-specific non-duplicative over-contract charge。
- PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive BESS cycle-aging formulation。
- outage service target \(\alpha L_t\)。

### 主線排除

- PV capacity sizing。
- grid export revenue。
- feeder-level power flow、bus voltage、line congestion、protection coordination。
- 真實 critical-load circuit inventory。
- 現有 life-safety emergency DG。
- outage probability distribution。
- stochastic Monte Carlo reliability probability。
- component forced-outage probability。
- site-specific BESS siting、fire-code compliance、construction constraints、interconnection engineering 與 institutional budget constraints。
- explicit battery calendar-aging state、SOH transition、augmentation schedule 與 full replacement schedule。

因此 \(E^{N*}\)、\(P^{B*}\) 應解讀為指定 resilience target 下的 **modeled planning requirements**，不是 NTUST 的 final recommended/physically deployable installation size。

## 3.2 服務比例 \(\alpha\)

\[
0<\alpha\le 1
\]

\(\alpha\) 表示停電時希望維持的 **aggregate campus service ratio proxy**：

\[
L^{service}_t=\alpha L_t
\]

### 正確解讀

- \(\alpha=0.8\)：每個時段要求供應 baseline aggregate load 的 80%。
- 它是規劃代理變數，用來建立成本–服務曲線。

### 限制

- 它不代表已辨識出哪些建築或設備屬於 critical load。
- 它不代表真實 load-shedding priority。
- 未來若取得 critical-load inventory，可用分群負載取代比例代理。

## 3.3 設計停電時長 \(\beta\)

\(\beta\) 是決策者要求系統在歷史 baseline 條件下可維持服務的 design-duration target。

### 正確解讀

- \(\beta=8\) h 表示此設計按 8 小時停電需求 sizing。
- 若決策者要 12 h resilience，應在 Layer A 設定 \(\beta=12\) h，而不是先設計 8 h 再把 12 h 當主要 sensitivity。

### 非正確解讀

- \(\beta\) 不是預測實際停電一定持續多久。
- \(\beta\) 不是 outage duration probability。

## 3.4 主分析範圍

建議主線 grid：

\[
\alpha\in\{0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00\}
\]

\[
\beta\in\{4,5,6,7,8,9,10,11,12\}\text{ h}
\]

共 81 組。

### 補充邊界

- \(\beta=24\) h 可作 boundary/extrapolation case，但不與主線 4–12 h 等同解讀。
- 0.60–1.00 與 4–12 h 是研究者設定的 analysis domain，不是普遍政策標準。

---

# 4. 資料與參數

## 4.1 正式時序資料與 chronology

正式 model year 固定為：

\[
2024\text{-}11\text{-}01\ 00{:}00
\le t
<
2025\text{-}11\text{-}01\ 00{:}00
\]

時區為 Asia/Taipei，時間解析度為：

\[
\Delta t=1\text{ h},\qquad T=8760.
\]

source electricity data 以 **hour-ending** 解讀。canonical raw timestamp 必須由可靠的 `Date + Time` 欄位重建，不直接沿用舊 combined CSV 的 `DateTime` 欄位（該欄位曾在 2024/12/02 出現已知 corruption）。raw timestamp \(t^{raw}\) 再轉為：

\[
t^{start}=t^{raw}-1h
\]

再從 \(t^{start}\) 重建 year、month、date、weekday、hour、summer/non-summer、TOU tag 與 billing month。

正式 annual filtering 必須依 timestamp half-open interval 執行，不可用 `df.iloc[:8760]` 或其他 row-position truncation。完成後必須 assert exactly 8,760 consecutive hourly intervals。

### 4.1.1 observed 與 planning-baseline series

final dataset 同時保存：

\[
L_t^{obs},\quad PV_t^{obs}
\]

與：

\[
L_t^{base},\quad PV_t^{base}.
\]

- observed series：保留 meter/source 真實紀錄。
- baseline series：供 EOB、Layer A、Layer B baseline conditions 與 annual economic optimization 使用。

本框架後續若未加上 superscript，\(L_t\)、\(PV_t\) 預設指 **planning-baseline series**。

### 4.1.2 歷史 outage-contaminated short gaps：site-validated production rules

歷史 grid outage 造成 Load 與 PV 同時為零的時段，不得直接解讀為 baseline demand/resource 同時為零。formal observed series 必須原樣保留，僅在 planning-baseline / available series 中重建 outage-contaminated intervals。

Script 01 identified exactly **10 outage-contaminated hours** within the formal case year：

- 2025-04-19 14:00–16:00：3 h unplanned outage；
- 2025-08-02 09:00–15:00：7 h planned outage。

#### Load short-gap production rule

Load reconstruction 採 NTUST pseudo-gap validation 後鎖定的：

\[
\boxed{\text{same weekday},\ \pm 6\text{ weeks},\ K=1}
\]

with matching metric:

\[
\boxed{\text{same-calendar-day outside-gap RMSE}}
\]

production method label：

`same_weekday_pm6weeks_top1_context_rmse`

Implementation rules：

- donor candidates 以 exact integer-week offsets 搜尋，且與 target 為 same weekday；
- donor calendar day 必須具完整 24 h；
- donor hours 必須 `load_status=normal` 且 `observed_load_kw>0`；
- actual outage days不得作 donor；
- target-day context 使用 outage block 以外之同日觀測時段；
- 依 outside-gap context RMSE 選出最相似 donor；
- \(K=1\)，因此不存在 mean / median aggregation choice；
- 只替換 `baseline_load_kw` 的 outage-contaminated hours；`observed_load_kw` 不修改。

Script 02 artificial pseudo-gap validation 使用兩種 observed outage shapes，共 **92 pseudo-events / 460 gap-hours**。selected \(\pm6\) weeks / \(K=1\) result：

- MAE = **100.436957 kW**；
- RMSE = **174.069420 kW**；
- signed energy bias = **+0.252411%**；
- mean event absolute energy bias = **436.771739 kWh**。

原 framework candidate \(\pm8\) weeks / \(K=3\) 在相同 pseudo-gap framework 下明顯較差，因此不再作 production rule。精確的 \(\pm6/K1\) 是 **NTUST site-specific empirical choice**，不是由外部文獻直接提供的 universal hyperparameter。

Script 03 將此 rule 套用於兩個真實 outage blocks，重建 exactly 10 Load hours；所有 non-outage hours之 `baseline_load_kw` 與 `observed_load_kw` 完全一致。

> **Retrospective-use boundary:** same-day outside-gap context 可使用 target day 中 gap 前後的已觀測時段；這是歷史 planning-baseline reconstruction，不是 real-time / online forecasting method。

#### PV short-gap production rule

PV short-gap method selection分成兩階段。

**Stage 1 — donor benchmark validation.** Script 04 以 observed outage shapes 建立 **604 pseudo-events / 3,020 gap-hours**，比較 calendar-day donors。原 v7 candidate `±30 days / K=5 / no weekday restriction` 的 **mean** aggregation是具競爭力的 donor benchmark：

- MAE = **34.625033 kW**；
- RMSE = **49.998621 kW**；
- signed energy bias = **+1.113409%**；
- mean event absolute energy bias = **135.937748 kWh**。

但此結果只建立「validated donor benchmark」，尚不足以證明 donor 是最好的 available reconstruction family。

**Stage 2 — donor vs CWA head-to-head validation.** Script 04b 在與 Script 04 **完全相同的 604 pseudo-events** 上比較 donor benchmark與 CWA GHI-based models，並對每一 pseudo-event排除 entire target calendar day from model fitting，以避免 target-day leakage。

CWA timestamp alignment必須遵守：

1. CODiS exact `23:59` daily-end labels先加 1 minute 正規化為 next-day `00:00` hour-ending label；
2. 再依 v7 electricity convention減 1 hour轉為 interval-start。

final production short-gap model：

\[
\boxed{\texttt{hourly\_ghi\_ratio\_median}}
\]

production method label：

`cwa_hourly_ghi_ratio_median_leave_target_day_out`

Core fitting semantics：

- 只使用 valid、non-outage observed PV / CWA overlap observations；
- 對每一 real/pseudo target event，entire target calendar day不進 fit；
- hour-specific median \(PV/GHI\) ratio為 primary coefficient；
- global median ratio為 fallback；
- low/no-irradiance period預測為 zero；
- prediction不得超過 training observations 支持的 fixed-system output range。

Head-to-head aggregate result：

| metric | CWA `hourly_ghi_ratio_median` | donor `±30d/K5 mean` |
|---|---:|---:|
| MAE (kW) | **16.954595** | 34.625033 |
| RMSE (kW) | **29.741402** | 49.998621 |
| signed energy bias (%) | +1.669484 | **+1.113409** |
| mean event absolute energy bias (kWh) | **51.967974** | 135.937748 |

Paired-event wins out of 604 pseudo-events：

- MAE：CWA **486** vs donor 118；
- RMSE：CWA **479** vs donor 125；
- event energy error：CWA **454** vs donor 150。

因此 short outage PV production reconstruction正式採 **CWA `hourly_ghi_ratio_median`**。donor `±30 days / K=5 mean` 保留作 validated benchmark，不再是 mainline production rule。

Script 05依此 production method重建 exactly 10 real outage PV hours：

- 2025-04-19 14:00–16:00：reconstructed event energy = **211.887706 kWh**；
- 2025-08-02 09:00–15:00：reconstructed event energy = **965.124933 kWh**。

`observed_pv_kw` 完全不修改；只更新 short outage hours 的 `pv_available_kw` / reconstruction provenance。

#### Claim boundary

外部文獻只支持 energy / solar missing-data reconstruction需利用 temporal/pattern information並透過 artificial-gap validation選方法。以下精確 production choices皆屬 **NTUST project empirical evidence**：

- Load：same weekday ±6 weeks / K=1 / same-day outside-gap RMSE；
- PV short-gap：CWA `hourly_ghi_ratio_median` with leave-target-day-out fitting。

不得將上述 exact rules寫成 literature constants。

#### Contamination / recovery-envelope status

v7（2026-08-14）中的「core-only vs expanded contamination-envelope 對 81-point \(R(\alpha,\beta)\) 與 \(P^{out}(\alpha)\) 無影響」**不得保留為 current validated finding**，因為 Scripts 02–05 並未在新的 empirical production rules下重做該 Layer-A-level robustness comparison。

Current rule：

- formal outage start/restoration logs若可明確界定 contamination period，以 formal log為準；
- 若沒有額外 recovery envelope evidence，不自行發明 statistical recovery window；
- 若 final data audit後仍存在合理的 expanded-envelope alternative，於 final production acceptance前做 targeted preprocessing robustness check；
- 未完成前不得宣稱 expanded envelope已證實對 final Layer A 81 points無影響。

---

### 4.1.3 2024/11–12 prolonged PV unavailability

長時間 PV 資料不可用必須與短期 outage contamination分開處理。

Formal Script-01 status counts：

- `pre_system` = **600 h**；
- `missing_winter` = **863 h**；
- total long unavailable PV = **1,463 h**。

Mainline planning baseline固定：

\[
\boxed{
PV_t^{base}=0,\qquad
t\in\{\texttt{pre\_system},\texttt{missing\_winter}\}
}
\]

並描述為：

> **conservatively assigned zero PV availability due to unavailable observations**

不得寫成「實際 PV generation = 0」。

Script 04b / Script 05 的 CWA superiority證據只針對 observed outage shapes所代表的 **3 h / 7 h short gaps**；它不能外推成「CWA 已被驗證可直接填補 1,463 h long unavailable block」。

因此：

- long unavailable PV在 mainline維持 zero；
- alternative CWA reconstructed / synthetic winter PV仍只作 **separate sensitivity branch**；
- 啟用 winter sensitivity前，必須以與 long-block使用情境相符的 block/month holdout validation重新驗證 CWA→PV model，而不能直接沿用 short-gap Script-04b accuracy numbers；
- winter sensitivity至少檢查 EOB、annual dispatch、CC、annual cost與 resilience premium；
- alternative winter reconstruction不得取代 Layer A adequacy mainline的 conservative-zero definition。

---

### 4.1.4 最低 provenance fields與 current v7.1 data lineage

final integrated thesis dataset至少保留：

**Time**
- `timestamp_raw_end`（若來源層仍可追溯）；
- `timestamp_start` 或 canonical `timestamp`；
- `time_index`。

**Observed Load / baseline Load**
- `observed_load_kw`；
- `baseline_load_kw`；
- `load_status`；
- `outage_contaminated_flag` / equivalent explicit provenance；
- `load_reconstructed`；
- `load_reconstruction_method`；
- donor provenance（對 reconstructed rows至少可追到 donor timestamp / offset / context metric）。

**Observed PV / available PV**
- `observed_pv_kw`；
- `pv_available_kw`；
- `pv_status`；
- `pv_reconstructed`；
- `pv_reconstruction_method`；
- CWA production model / fit provenance sufficient to reproduce short-gap estimates；
- long-unavailable hours須能與 short-gap reconstructed hours明確區分。

**Weather, if merged into production annual input**
- `ghi_kwh_m2`；
- `air_temperature_c`（若後續 model/sensitivity需要）。

**Regenerated calendar / institutional tags**
- year；
- month；
- date/day；
- weekday；
- hour；
- summer/non-summer；
- TOU tag；
- billing usage-period identifier。

所有 calendar / TOU / billing tags必須從 canonical interval-start timestamp重新生成，不沿用未審核 legacy labels。

Raw observed input immutable。任何 reconstruction不得覆寫 observed columns；每一個 reconstructed / conservatively assigned value都必須由 status或method field追溯其來源。

Current v7.1 lineage：

```text
raw cleaned observed source
        ↓
Script 01
ntust_case_year_observed.*
        ├───────────────┐
        ↓               ↓
Script 02           Script 04
Load validation     PV donor validation
        ↓               ↓
Script 03           Script 04b
load_annual_        donor vs CWA
baseline.*              ↓
                    Script 05
                    pv_annual_baseline.*
        └───────────────┘
                ↓
      final integrated annual input
      [NEXT DATA-INTEGRATION TASK]
```

---

## 4.2 電價與契約容量

正式 tariff parameter registry 必須對應 **case-year historical usage/billing period**，不能用論文定稿當下的最新費率回填歷史年，也不能把 bill-title month 當成實際用電月份。

source-of-truth 優先序：

1. NTUST 實際 Taipower bills；
2. 對應 effective-date 的 Taipower detailed tariff tables/rules。

至少保存：

| 欄位 | 定義 |
|---|---|
| tariff/service category | 校園實際適用類別 |
| usage_period_start / end | 實際計價用電期間；billing join 的主索引 |
| bill_title_month | 帳單標題月份；僅作文件識別，不用來切 hourly data |
| effective start/end date | 費率／規則有效期間 |
| summer/non-summer | 依日期邊界，不用整月 shortcut |
| TOU period definition | peak / half-peak / Saturday-half-peak / off-peak |
| energy-charge rate | NTD/kWh |
| regular contract capacity | NTD/kW-month 對應的 regular/peak CC |
| supplementary contract capacities | half-peak / Saturday-half-peak / off-peak；NTUST mainline case 固定為 0 |
| period-specific basic-charge rate | 各 TOU period 的 applicable contract/basic rate |
| over-contract rule | cumulative threshold、non-duplication、2×/3× tier |
| source | bill filename / official tariff version |

高壓／特高壓 summer calendar 在本 case-year 固定為：

\[
\boxed{\text{May 16--October 15}}
\]

非夏月為 January 1–May 15 與 October 16–December 31。code 不得使用 `summer_months=[6,7,8,9]` 類型整月判定。

### 4.2.1 Contract-capacity decision boundary（A3 CLOSED）

NTUST mainline 只最佳化一個年度 regular contract capacity：

\[
\boxed{CC=CC^{regular}}
\]

Taipower 制度本身允許 supplementary half-peak、Saturday-half-peak、off-peak contract capacities；本研究不是宣稱制度只有一個 CC，而是依 NTUST case 將 supplementary components 固定為實際值 0，不把 tariff-design / multi-contract optimization 擴張成新的研究問題。

四個 TOU periods 仍必須保留，因為 energy rates、period maxima 與 over-contract applicable basic rates不同。

### 4.2.2 Billed maximum 與 over-contract rule

對 usage period \(m\)，帳單四時段 15-min maxima 記為：

\[
B_{m,q},\qquad q\in\{peak,half,sat,off\}.
\]

帳單 overall maximum demand 定義為：

\[
\boxed{B_m=\max_q B_{m,q}}.
\]

此 \(B_m\) 用於 §4.3 的 hourly-to-billing calibration。

over-contract charge **不得把四時段超約量直接相加**。production tariff module 必須依 Taipower 三段式時間電價規則使用 period-specific cumulative contract thresholds，並扣除前面已計收之超約，使同一 kW 不重複計費；各新增超約區段使用其所屬 TOU period 的 applicable basic-charge rate。

超約 tier 固定依 official case-year rule：

- 契約容量 10% 以內的超約部分：2× applicable basic rate；
- 超過 10% 的部分：3× applicable basic rate。

已核對的 regression case：2025/10 標題帳單實際對應 2025/09/01–09/30 usage period；四時段 maxima 為 4896 / 5016 / 3352 / 3776 kW，因此 overall max = 5016 kW。regular CC=5000 kW，當期只有 half-peak exceedance 16 kW；以 half-peak summer basic rate 166.9 NTD/kW-month、2× tier 得：

\[
16\times166.9\times2=\boxed{5,340.8\text{ NTD}},
\]

production billing code 必須精確重現此值。

## 4.3 15-min demand 與 hourly billing proxy

Taipower billing maximum demand 以 15-min average kW 為基礎；本研究維持 hourly optimization，因此不宣稱精確重建 sub-hourly metering profile。

historical calibration 使用 **final v7.1 integrated annual input 中的 observed historical grid import**，不得使用 outage-reconstructed planning baseline：

\[
\boxed{
P_t^{grid,hist}
=
observed\_load\_kw_t
-
observed\_pv\_kw_t
}
\]

File name 本身不是 source-of-truth。若 final integrated artifact 仍命名為 `annual_input_existing_pv.csv/.parquet`，該檔案必須：

1. 由 current v7.1 `load_annual_baseline.*` + `pv_annual_baseline.*` 重新生成；
2. 保留 Script-01 observed values 不變；
3. 使用 current v7.1 interval-start 8,760-hour timeline；
4. 重新生成 calendar / TOU / billing-period fields；
5. 通過 final integration audit。

任何 pre-v7 同名檔案皆視為 legacy，不得用於 final billing calibration、EOB、Layer A 或 Layer B。

Billing calibration 只能使用 `observed_load_kw - observed_pv_kw`；不得使用 `baseline_load_kw - pv_available_kw`，因後者含 counterfactual reconstruction，與帳單實際量測邊界不一致。

正式 status schema 以 `pv_status` 為 current v7.1 concept；若 final merged file 為向後相容另保留 `solar_status` alias，必須在 data dictionary 明確註明兩者映射，不可讓 legacy naming 控制 production logic。

對 calibration usage period \(m\)：

\[
H_m=\max_{t\in m}P_t^{grid,hist},
\qquad
B_m=\max_q B_{m,q}^{15min,bill}.
\]

Mainline 以 2025/01–2025/10 十個 `pv_status=valid` usage months 做 through-origin least-squares calibration：

\[
\boxed{
\kappa=
\frac{\sum_m H_mB_m}{\sum_m H_m^2}
}
\]

既有 audited calculation 為：

\[
\boxed{\kappa\approx1.01037},
\]

但 production model **不得只 hard-code 1.01037**；`calibrate_kappa.py` 必須從 canonical hourly input + billing registry 重建十組 \((H_m,B_m)\)、重算 \(\kappa\)，並保存可追溯 audit table。

### 4.3.1 \(\kappa\) 的方法定位

\(\kappa\) 是 NTUST site-specific empirical multiplicative calibration，不是文獻給定的 universal coefficient，也不沿用 lab predecessor 固定值。through-origin least squares 是針對比例式 proxy \(B_m\approx\kappa H_m\) 所採 estimator；temporal-resolution 文獻只支持 hourly aggregation 對 peak/power quantity 可能產生偏差，不提供本研究的 \(\kappa\) 或 estimator 公式。

2024/11 與 2024/12 **只排除 coefficient estimation**，不從 12-month simulation 刪除：前者為 pre-system/pre-PV regime，後者為 `missing_winter`，都無法與 2025/01–10 valid-PV usage months 用同一 observed grid-import definition 建立 calibration pair。

### 4.3.2 Billing-period alignment

所有 \(H_m\) 必須使用與帳單 \(B_m\) 完全相同的 **usage period**。例如標題 2025/10 的帳單代表 2025/09/01–09/30 用電，因此應配對 September hourly maximum，而不是 October hourly data。

`billing_demand_registry.csv` 至少保存：

- usage-period start/end；
- regular/supplementary CC；
- peak / half / sat-half / off-peak maxima；
- \(B_m=\max_q B_{m,q}\)；
- source bill filename。

`calibrate_kappa.py` 輸出至少包含：

- \(H_m\)、四時段 billed maxima、\(B_m\)；
- \(B_m/H_m\)；
- fitted \(\hat B_m=\kappa H_m\)；
- residual；
- final \(\kappa\)。

### 4.3.3 Optimization 與 exact demand reporting（A4 CLOSED）

optimization 中可使用 period-specific epigraph/exceedance variables 服務 tariff constraints，例如對每個 usage period/TOU period：

\[
D_{m,q}^{opt}\ge \kappa p_t^{grid},\qquad t\in(m,q),
\]

或直接以 exceedance variables 對 \(\kappa p_t^{grid}-CC_q^{threshold}\) 建 constraint。這些變數的角色是 **cost-facing optimization auxiliaries**，不是報表上的 exact maximum。

solve 後一律由 optimized hourly grid profile ex-post 重算：

\[
\boxed{
D_{m,q}^{exact}=\max_{t\in(m,q)}\kappa p_t^{grid}
}
\]

\[
\boxed{
D_m^{exact}=\max_q D_{m,q}^{exact}
}
\]

因此不再依賴可能 floating 的單一 \(D_m^{proxy}\) 作 monthly diagnostic。正式用語仍為：

> calibrated hourly proxy for the 15-minute billing demand.

不得寫成 exact 15-min billing reconstruction。

## 4.4 BESS 技術、成本與 degradation 參數

### 4.4.1 技術 reference（A1 CLOSED）

- battery chemistry：stationary LFP。
- nameplate energy capacity：\(E^N\)。
- power rating：\(P^B\)。
- mainline \(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)。
- derived usable energy：

\[
E^U=0.8E^N.
\]

- 20–80% SOC window 可作 deliberately more restrictive technical sensitivity，不宣稱 universal optimum。
- \(p_t^{ch}\)、\(p_t^{dis}\)、\(P^B\) 定義於 AC/PCS side。
- \(e_t\) 為 battery-side stored energy。
- **mainline efficiency fixed**：

\[
\boxed{\eta_c=\eta_d=0.90}.
\]

因此 one-step state transition 為：

\[
e_{t+1}=e_t+0.90\,p_t^{ch}\Delta t-\frac{p_t^{dis}\Delta t}{0.90}.
\]

0.95/0.90 與由 PNNL system RTE 對稱拆解的約 0.91/0.91 均不再是 mainline candidates。Qi et al. (2025, *Applied Energy*) 的 system-level battery formulation作直接文獻 precedent；PNNL system-level RTE僅作 boundary-consistency sanity check，不用來重新拆效率。

mainline 不做 efficiency curve 或效率 sensitivity full sweep；若 reviewer 要求，可做小型 robustness check，但不重新打開 A1。

### 4.4.2 BESS capital-cost basis

正式 purchase basis：

\[
CAPEX_{BESS}=C_EE^N+C_PP^B.
\]

\(C_E\) 必須以 installed/nameplate kWh 為 denominator；若 source 是 usable-kWh basis，先轉換後才可入模。

mainline numerical cost source 改為 **PNNL v2024 LFP cost data 的 thesis-derived energy/power-separated linear planning approximation**。1 MW 與 10 MW source cases作 scale bracket；正式 \(C_E,C_P,FOM\) 與 currency/base-year normalization 放在 parameter registry，不在本框架重複列來源細節。

經濟假設固定：

\[
r=0.05,\qquad n=20\text{ yr}
\]

\[
CRF(r,n)=
\frac{r(1+r)^n}{(1+r)^n-1}
=
\boxed{0.0802426}.
\]

因此：

\[
C^{annual}_{BESS,cap}
=
CRF(C_EE^N+C_PP^B).
\]

FOM 若已是 annual basis，直接加至 objective，**不得再乘 CRF**。

legacy 813.75、694.4、CRF=0.07 僅保留 replication/lineage，不得控制 mainline results。

### 4.4.3 Cycling degradation（B1 CLOSED）

mainline 採：

\[
\boxed{
\text{PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation}
}
\]

此模型的目標是讓 multi-hour cycle depth 對 cycling wear 有作用，同時維持可整合進年度 sizing/dispatch optimization 的 convex/PWL 結構。它不是完整 electrochemical lifetime model。

**Attribution boundary：** Xu et al. (2018) 控制的是 intertemporal PWL cycle-aging formulation 的核心數學語義（segment-specific charge/discharge、cross-time segment-energy states、convex shallow-to-deep priority 與 rainflow benchmark rationale）；PNNL 控制 LFP DOD–cycle-life technical calibration。本研究另自行處理 PNNL sparse/nonuniform calibration、equal-slope merging、endogenous \(E^N\) segment widths、10–90% SOC 對應的 effective depth domain，以及 annual cyclic segment boundary。因此本方法不得簡稱為「the Xu model」或宣稱 Xu 的 theorem 已直接證明本研究完整 sizing extension。

#### A. Technical calibration：PNNL LFP DOD–cycle-life points

固定 technical calibration input：

| Effective / lifetime-average DOD \(\delta\) | Cycle life \(N(\delta)\) |
|---:|---:|
| 0.05 | 192,000 |
| 0.30 | 32,000 |
| 0.60 | 8,000 |
| 0.70 | 6,000 |
| 0.80 | 4,800 |

PNNL raw reported DOD 與 lifetime-average/effective DOD 並非總是一致；raw-to-effective interpretation、source page 與 provenance 必須保存在 literature/parameter registry，code 不得靜默把 reported DOD 當 model cycle depth。

由於 0–5% 與 5–30% 的 derived marginal slope 相同、60–70% 與 70–80% 的 slope相同，production effective breakpoints 可合併為：

\[
\boxed{b=(0,\ 0.30,\ 0.60,\ 0.80)}.
\]

原始五點仍完整保留於 registry；三段只是數學合併，不是刪除 provenance。

#### B. Economic wear curve

以 final replacement-cost basis \(C_{rep}\) 定義：

\[
G(0)=0,
\qquad
G(\delta)=\frac{C_{rep}}{N(\delta)}\quad(\delta>0).
\]

PWL marginal slopes：

\[
\boxed{
\lambda_k=
\frac{G(b_k)-G(b_{k-1})}{b_k-b_{k-1}}
}
\]

必須區分：

- \(N(\delta)\)：固定 technical cycle-life calibration；
- \(C_{rep}\)：final economic replacement-cost basis；
- \(\lambda_k\)：由前兩者導出的 marginal cycling-wear coefficient。

在本研究 convention 中，\(\lambda_k\) 明確定義為：

\[
\boxed{\lambda_k:\ \mathrm{NTD/(battery\text{-}side\ discharged\ kWh)}}.
\]

因此 \(\lambda_k\) 本身**不含** discharge-efficiency conversion；若 segment discharge power \(p_{t,k}^{dis}\) 定義於 AC/PCS side，objective 必須使用 \(p_{t,k}^{dis}\Delta t/\eta_d\) 轉為 battery-side discharged energy。這與 Xu et al. Eq. (5)–(7) 將 \(1/\eta^{dis}\) 直接吸收到 AC-side marginal cost coefficient \(c_j\) 的 convention 代數等價；兩種 convention 不得混用，否則會 double-count discharge efficiency。

\(\lambda_k\) **不得獨立 hard-code**。Harry-era \(C_{rep}=5107.57\) NTD/kWh 與 legacy slopes 0.532 / 1.596 / 2.128 只能作 replication/regression test，不得控制 mainline。

#### C. Intertemporal segment-state requirement

每個 degradation segment \(k\) 必須有跨時間 stored-energy state \(e_{t,k}^{seg}\)，而不是每小時重新分配 discharge throughput。設 segment capacity：

\[
\bar E_k=(b_k-b_{k-1})E^N.
\]

定義 shifted usable state：

\[
x_t=e_t-SOC_{min}E^N,
\qquad
x_t=\sum_k e_{t,k}^{seg}.
\]

segment bounds：

\[
0\le e_{t,k}^{seg}\le \bar E_k.
\]

aggregate charge/discharge：

\[
p_t^{ch}=\sum_k p_{t,k}^{ch},
\qquad
p_t^{dis}=\sum_k p_{t,k}^{dis}.
\]

segment dynamics：

\[
e_{t+1,k}^{seg}
=
e_{t,k}^{seg}
+\eta_c p_{t,k}^{ch}\Delta t
-\frac{p_{t,k}^{dis}\Delta t}{\eta_d}.
\]

annual periodicity 同時要求 total state 與 segment states cyclic：

\[
e_T=e_0,
\qquad
e_{T,k}^{seg}=e_{0,k}^{seg}\quad\forall k.
\]

production implementation 必須遵循 Xu-derived convex segment-priority semantics：較淺 depth segment 具有不高於較深 segment 的 marginal cost，並以 cross-time segment state 維持 multi-interval depth history。不得使用 Harry-style「每小時 reset、每小時重新從最便宜 segment 開始」的 proxy 作 final mainline。

#### D. AC / battery-side degradation boundary

DOD 與 segment capacity 是 **battery-side energy fraction**。因 \(p_t^{dis}\) 定義於 AC side，segment cycling cost 應以 battery-side discharged energy計：

\[
\boxed{
C_{cycling}^{deg}
=
\sum_t\sum_k
\lambda_k\frac{p_{t,k}^{dis}\Delta t}{\eta_d}
}
\]

不得直接把 AC-side discharged kWh 當成 DOD energy，否則會低估 battery-side depth/use。

#### E. Model boundary / validation

mainline 不加入：

- calendar-aging state；
- temperature-dependent aging；
- C-rate aging；
- dwell-SOC aging；
- dynamic SOH transition；
- augmentation schedule；
- explicit battery replacement schedule。

因此論文 claim 是 **DOD-sensitive cycling economic wear approximation**，不是完整 physical lifetime prediction。

full rainflow cycle counting **不嵌入 optimization**；只作 ex-post validation，至少比較 realized cycle-depth distribution、PWL cycling cost 與 rainflow-derived benchmark cost。linear discharge-throughput model保留為 model-form benchmark；若 reserve-heavy Layer A solutions 局部落在 shallow region、PWL 自然近似 linear，應報告為 empirical result，而不是事前 simplification。

#### F. B2 accounting guardrail（no structural change）

B1 改變的是 \(C_{cycling}^{deg}\) 的計算方式，不改 overall accounting：annualized BESS CAPEX + annual FOM + operating costs的結構維持。mainline 不另加 full replacement/augmentation cash-flow stream，以避免與 annualized ownership cost + marginal cycling wear重複計價。20-year horizon 是 financial analysis period，不是 battery physical-life hard constraint。

## 4.5 Locked parameter / setting register snapshot

> 本表是 framework-level snapshot，用來防止 production code、registry 與正文出現新舊參數混用。`pending population` 表示 numerical source extraction 尚未完成，**不表示方法未決**。

| 項目 | Mainline 值／設定 | 狀態 | Source / implementation rule |
|---|---|---|---|
| Battery chemistry | stationary LFP | **LOCKED** | PNNL-aligned technical reference |
| \(SOC_{min}\) | 0.10 | **LOCKED** | mainline technical window |
| \(SOC_{max}\) | 0.90 | **LOCKED** | mainline technical window |
| usable fraction | 0.80 \(E^N\) | **DERIVED / LOCKED** | \(SOC_{max}-SOC_{min}\) |
| charge efficiency \(\eta_c\) | 0.90 | **LOCKED (A1)** | system-level AC→battery boundary |
| discharge efficiency \(\eta_d\) | 0.90 | **LOCKED (A1)** | battery→AC boundary |
| annual normal reserve floor | \(e_t\ge0.10E^N+R(\alpha,\beta)\) | **LOCKED (A2)** | constant worst-case reserve mainline |
| outage initial state | \(e_0=0.10E^N+R\) | **LOCKED (A2)** | lowest preparedness state |
| outage technical lower bound | \(e_\tau\ge0.10E^N\) | **LOCKED (A2)** | reserve may be consumed during outage |
| outage terminal requirement | \(e_\beta\ge0.10E^N\)；不要求恢復 \(R\) | **LOCKED (A2)** | separate replay semantics |
| reserve-floor robustness | 6 points: \(\alpha=0.60,0.80,1.00\) × \(\beta=4,12\) | **LOCKED targeted check** | constant vs perfect-information variable floor |
| regular contract capacity \(CC\) | one annual decision variable | **LOCKED (A3)** | NTUST planning decision |
| supplementary CCs | half / Sat-half / off = 0 | **LOCKED NTUST case setting** | not optimized |
| TOU demand periods | peak / half / Sat-half / off | **LOCKED** | Taipower case-year tariff |
| summer calendar | May 16–Oct 15 | **LOCKED** | Taipower case-year rule |
| over-contract tier 1 | first 10% exceedance ×2 | **LOCKED (A3)** | period-specific applicable basic rate |
| over-contract tier 2 | beyond 10% exceedance ×3 | **LOCKED (A3)** | period-specific applicable basic rate |
| non-duplication | required across TOU exceedance accounting | **LOCKED (A3)** | Taipower rule |
| billing calibration quantity | observed Load − observed PV | **LOCKED** | canonical file observed columns only |
| calibration usage months | 2025/01–2025/10 | **LOCKED** | valid-PV periods |
| billed calibration target \(B_m\) | max of four TOU billed maxima | **LOCKED** | usage-period aligned |
| \(\kappa\) estimator | through-origin LS | **LOCKED** | site-specific multiplicative calibration |
| \(\kappa\) numerical value | existing ≈1.01037 | **PENDING SCRIPTED REPRODUCTION** | final source = `calibrate_kappa.py` output |
| exact modeled billing maxima | post-solve \(D_{m,q}^{exact},D_m^{exact}\) | **LOCKED (A4)** | do not report floating auxiliary variable |
| degradation formulation | PNNL calibration + Xu et al. intertemporal PWL adaptation | **LOCKED (B1)** | DOD-sensitive cycling wear |
| raw effective-DOD calibration | (0.05,192000), (0.30,32000), (0.60,8000), (0.70,6000), (0.80,4800) | **LOCKED technical inputs** | PNNL LFP cycle-life calibration |
| effective PWL breakpoints | (0, 0.30, 0.60, 0.80) | **LOCKED** | equal-slope segments merged |
| \(C_{rep}\) | TBD from final PNNL cost basis | **PENDING POPULATION** | method closed; numerical extraction pending |
| \(\lambda_k\) | derived from \(C_{rep}\) and DOD table | **DERIVED / NO HARD-CODE** | NTD per battery-side discharged kWh; \(1/\eta_d\) applied to AC-side discharge in objective |
| rainflow | ex-post validation only | **LOCKED** | not embedded in objective |
| linear degradation | benchmark/equivalence diagnostic only | **LOCKED secondary role** | not mainline |
| discount rate \(r\) | 0.05 | **LOCKED** | financial assumption |
| analysis horizon \(n\) | 20 yr | **LOCKED** | financial horizon, not physical-life gate |
| CRF | 0.0802426 | **DERIVED / LOCKED** | code derives from \(r,n\) |
| \(C_E,C_P,FOM\) | TBD from PNNL v2024 | **PENDING POPULATION** | raw cost → normalization → annualization |
| B2 accounting | annualized CAPEX + annual FOM + operating costs | **LOCKED / NO STRUCTURAL CHANGE** | no explicit replacement stream |

Production `parameter_registry` remains the machine-readable source of truth; this table is the human-readable specification snapshot. Any numerical parameter not listed as `LOCKED` or `PENDING POPULATION` must not be silently introduced into production code.

---
# 5. 變數與單位定義

## 5.1 BESS nameplate、usable energy 與 stored-energy state

正式定義：

- \(E^N\)：installed/nameplate BESS energy capacity（kWh），Layer A sizing decision variable，也是 energy CAPEX 的容量基礎。
- \(E^U\)：SOC operating window 內的 derived usable energy（kWh），不是獨立 sizing variable。
- \(e_t\)：actual stored battery energy（kWh），正式論文與 code audit 的 primary physical state。
- \(x_t\)：SOCmin 以上的 shifted usable state，只作輔助解釋，不作主 state。

一般式：

\[
E^U=(SOC_{\max}-SOC_{\min})E^N.
\]

mainline 10–90% SOC：

\[
\boxed{E^U=0.8E^N}.
\]

stored-energy bounds：

\[
\boxed{
SOC_{\min}E^N
\le e_t
\le
SOC_{\max}E^N
}
\]

即：

\[
0.10E^N\le e_t\le0.90E^N.
\]

輔助 shifted state：

\[
x_t=e_t-SOC_{\min}E^N,
\qquad
0\le x_t\le E^U.
\]

resilience reserve \(R(\alpha,\beta)\) 是 technical minimum SOC **之上**額外必須保留的 usable energy，因此正式 reserve constraint 為：

\[
\boxed{
e_t\ge SOC_{\min}E^N+R(\alpha,\beta)
}
\]

且必須有：

\[
(SOC_{\max}-SOC_{\min})E^N\ge R(\alpha,\beta).
\]

mainline 因而得到：

\[
\boxed{
E^N\ge\frac{R(\alpha,\beta)}{0.8}
}.
\]

## 5.2 其他決策／輔助變數

### Core design / dispatch variables

- \(P^B\)：BESS charge/discharge power rating（kW）。
- \(CC\)：annual regular contract capacity（kW）。
- \(p_t^{grid}\)：grid import（kW）。
- \(p_t^{ch}\)：battery charging power，AC/PCS side（kW）。
- \(p_t^{dis}\)：battery discharging power，AC/PCS side（kW）。
- \(PV_t^{use}\)：used PV power（kW）。
- \(PV_t^{curt}\)：curtailed PV power（kW）。

### Degradation auxiliary variables

- \(e_{t,k}^{seg}\)：Xu-derived degradation segment \(k\) 的 intertemporal battery-side stored-energy state（kWh）。
- \(p_{t,k}^{ch}\)、\(p_{t,k}^{dis}\)：segment-level AC-side charge/discharge power（kW）。
- segment capacities \(\bar E_k=(b_k-b_{k-1})E^N\)；不是獨立 sizing variables。

### Billing auxiliary variables

optimization 可使用 period-specific demand epigraph/exceedance variables以實作 tariff cost，但它們不是報表上的 exact maxima。exact \(D_{m,q}^{exact}\)、\(D_m^{exact}\) 一律 post-solve 由 optimized \(p_t^{grid}\) 計算。

supplementary contract capacities不是 decisions；NTUST case 固定為 0。

# 6. Baseline：economic-only design（EOB）

在加入 resilience requirement 前，先求一個 economic-only baseline：

\[
(\alpha,\beta)\text{ constraint absent}
\]

輸出：

- \(E^N_{EOB}\)
- \(P^B_{EOB}\)
- \(CC_{EOB}\)
- \(C_{EOB}\)
- annual dispatch、TOU cost、basic charge、over-contract penalty、degradation cost。

EOB 是所有 resilience premium 的比較基準：

\[
\Delta C(\alpha,\beta)=C(\alpha,\beta)-C_{EOB}
\]

\[
Premium\%(\alpha,\beta)=\frac{\Delta C(\alpha,\beta)}{C_{EOB}}\times100\%
\]

---

# 7. Layer A：All-start resilience-constrained annual planning

## 7.1 Layer A 的功能

Layer A 回答：

> 在正式 case-year baseline load–PV chronology 與模型技術假設下，為了在每一個完整 \(\beta\)-hour trajectory 均位於該 case year 內的 valid historical outage start 維持 \(\alpha\) 比例服務，年度固定 BESS/CC 設計至少需要多少容量與成本？

Layer A 是 sizing layer，不是 outage probability model。

## 7.2 淨服務缺口

對給定 \(\alpha\)：

\[
d_t(\alpha)=\left[\alpha L_t-PV_t\right]^+
\]

其中本章 \(L_t\)、\(PV_t\) 預設指 §4.1 的 planning-baseline series，且：

\[
[z]^+=\max(z,0).
\]

### 為何 \(\alpha\) 必須放在 max 內

PV 是先抵減「需要維持的服務負載」\(\alpha L_t\)，不是先抵減 full load 再乘 \(\alpha\)。

正確：

\[
[\alpha L_t-PV_t]^+
\]

不建議：

\[
\alpha[L_t-PV_t]^+.
\]

兩者的物理意義不同。

## 7.3 case-year valid-start energy reserve

設時間步長為 \(\Delta t\) 小時，\(n_\beta=\beta/\Delta t\)。

正式 valid-start set：

\[
\boxed{
\mathcal S_\beta=\{s:\ s+n_\beta\le T\}
}.
\]

對每個 \(s\in\mathcal S_\beta\)：

\[
G_s(\alpha,\beta)=
\sum_{k=0}^{n_\beta-1}
d_{s+k}(\alpha)\Delta t.
\]

**Mainline 不做 circular year-end wrap。** 只有完整 \(\beta\)-hour trajectory 被正式 case-year chronology 觀察到的 outage start 才進入 maximum。若未來有真實 next-year continuation data，才可另行擴展 end-of-year starts。

reserve 定義為：

\[
\boxed{
R(\alpha,\beta)=
\frac{1}{\eta_d}
\max_{s\in\mathcal S_\beta}G_s(\alpha,\beta)
}.
\]

### 物理意義

- 掃描 formal case year 內所有 valid \(\beta\)-hour outage starts。
- 對每個窗口計算需由 BESS 放出的 positive residual energy。
- 取 valid starts 中的最大值。
- 除以 discharge efficiency，換成 outage 開始前必須存在 battery-side 的 usable stored energy above SOCmin。

### 保守性

此 reserve 以 \([\alpha L-PV]^+\) 加總，**不依賴 outage 期間的 PV surplus 再充電**。因此它是一個透明、保守的 energy adequacy requirement。

- 若 outage 中出現 PV surplus，實際 dispatch 可能比此 reserve 更有利。
- 不可把 \(R\) 稱為考慮所有動態後的唯一精確最小 reserve，除非另以 exhaustive dynamic replay 證明。

## 7.4 瞬時 power adequacy

\[
P^{out}(\alpha)=\max_t d_t(\alpha).
\]

Layer A 必須要求：

\[
P^B\ge P^{out}(\alpha).
\]

白話：energy capacity 是水箱大小，power rating 是水管粗細。總電量足夠不代表單一小時能吐出足夠功率。

## 7.5 年度 reserve policy

正式 state 使用 actual stored energy \(e_t\)。

全年 reserve floor：

\[
\boxed{
e_t\ge
SOC_{\min}E^N+R(\alpha,\beta),
\qquad\forall t
}
\]

同時：

\[
\boxed{
(SOC_{\max}-SOC_{\min})E^N
\ge R(\alpha,\beta)
}.
\]

mainline 10–90% SOC 下：

\[
E^N\ge\frac{R(\alpha,\beta)}{0.8}.
\]

這表示正常運轉時可以用 BESS 做削峰與 TOU shifting，但 technical minimum SOC 與 resilience reserve 均不可被正常經濟 dispatch 侵蝕。

### 研究意義

resilience premium 可能包含：

1. 額外購買 energy capacity；
2. 額外購買 power capacity；
3. 因 reserve floor 而失去一部分正常經濟 dispatch freedom；
4. 因 BESS/CC 聯合最佳化導致的 contract capacity 變化。

## 7.6 正常運轉 power balance

若不允許 export：

\[
p^{grid}_t+p^{dis}_t+PV^{use}_t=L_t+p^{ch}_t
\]

\[
0\le PV^{use}_t\le PV_t
\]

\[
PV^{curt}_t=PV_t-PV^{use}_t
\]

\[
p^{grid}_t\ge0.
\]

## 7.7 BESS dynamics

AC-side charge/discharge power 與 battery-side stored energy 的 state transition：

\[
\boxed{
e_{t+1}
=
e_t
+0.90\,p_t^{ch}\Delta t
-\frac{p_t^{dis}\Delta t}{0.90}
}
\]

亦即 mainline：

\[
\boxed{\eta_c=\eta_d=0.90}.
\]

\[
0\le p_t^{ch}\le P^B,
\qquad
0\le p_t^{dis}\le P^B.
\]

annual normal-operation state bounds：

\[
\boxed{
SOC_{min}E^N+R(\alpha,\beta)
\le e_t
\le
SOC_{max}E^N
}.
\]

### 年度 state boundary

annual economic dispatch 使用 \(T+1\) 個 state index：

\[
\boxed{e_T=e_0}.
\]

Xu-derived degradation segment states 同樣使用 periodic boundary：

\[
\boxed{e_{T,k}^{seg}=e_{0,k}^{seg}\quad\forall k}.
\]

annual state cyclicity 與 §7.3 禁止 outage-window circular wrap 是不同概念：前者防止年度 optimization 在研究邊界免費耗盡／累積 energy；後者禁止把 year-end outage trajectory 人工接回 case-year 開頭。

不得使用語意不明的 `e[0]=e[8759]`；transition 必須明確由 \(t\) 到 \(t+1\)。

### 充放電互斥

主線優先維持 convex/LP-compatible formulation，前提是完成以下 audit：

- 全年無顯著 simultaneous aggregate charge/discharge；
- efficiency loss 與 cycling degradation cost 使 simultaneous operation 無經濟誘因；
- segment-level allocation符合 Xu-derived convex ordering semantics；
- 若仍出現實質性同充同放或 solver exploitation，才加入必要 binary/complementarity constraints，並記錄計算影響。

## 7.8 Layer A objective

概念上：

\[
\min C^{annual}.
\]

其中：

\[
\boxed{
C^{annual}
=
C^{annual}_{BESS,cap}
+
C^{FOM}
+
C^{TOU}
+
C^{CC}
+
C^{over}
+
C^{deg}_{cycling}
}
\]

### 7.8.1 Annualized BESS capital cost

\[
CAPEX_{BESS}=C_EE^N+C_PP^B
\]

\[
\boxed{
C^{annual}_{BESS,cap}
=
0.0802426\left(C_EE^N+C_PP^B\right)
}
\]

其中 \(C_E,C_P\) 是 PNNL v2024-derived、以 nameplate energy/power basis 定義的 raw CAPEX planning coefficients，先完成 currency/base-year normalization，再乘 CRF。

FOM 若已是 annual value，直接加入 objective，不得 CRF twice。

### 7.8.2 Cycling degradation cost

mainline 使用 §4.4.3 鎖定的 **PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation**。

有效 breakpoints：

\[
\boxed{b=(0,0.30,0.60,0.80)}.
\]

segment capacity：

\[
\bar E_k=(b_k-b_{k-1})E^N.
\]

shifted usable state 與 segment states 必須一致：

\[
x_t=e_t-SOC_{min}E^N=\sum_k e_{t,k}^{seg}.
\]

segment dynamics：

\[
e_{t+1,k}^{seg}
=
e_{t,k}^{seg}
+\eta_c p_{t,k}^{ch}\Delta t
-\frac{p_{t,k}^{dis}\Delta t}{\eta_d}.
\]

aggregate power：

\[
p_t^{ch}=\sum_kp_{t,k}^{ch},
\qquad
p_t^{dis}=\sum_kp_{t,k}^{dis}.
\]

cycling cost：

\[
\boxed{
C_{cycling}^{deg}
=
\sum_t\sum_k
\lambda_k\frac{p_{t,k}^{dis}\Delta t}{\eta_d}
}
\]

其中 \(\lambda_k\) 由 final \(C_{rep}\) + PNNL DOD–cycle-life table自動產生，不 hard-code。

**禁止 final mainline 使用 hourly-reset PWL**：不得在每小時把 total discharge throughput重新從 cheapest segment 分配；segment stored-energy state必須跨時間延續，使 multi-hour deep cycle 能進入較高 marginal wear region。

full rainflow 不進 objective；post-processing 以 rainflow-derived cycle-depth/cost作 validation。linear throughput只作 model-form benchmark/equivalence check。

Xu et al. Appendix Theorem 1 支持在**給定 feasible battery dispatch、convex marginal aging curve**下 shallow-to-deep segment priority 的最小 aging-cost性質；Theorem 2 支持其等寬 PWL sequence 在 segment 數趨近無限時收斂至 rainflow-based benchmark cost。這些結果是本研究 intertemporal PWL representation 的理論基礎，但**不直接證明** endogenous \(E^N\) sizing、PNNL 非等寬有限分段、equal-slope merging 或 annual cyclic adaptation；上述 thesis-specific extensions 必須以 unit tests 與 ex-post rainflow comparison 自行驗證。

### 7.8.3 其他成本

1. grid TOU energy charge。
2. contract capacity basic charge。
3. Taipower period-specific non-duplicative over-contract penalties，作用於 §4.2–4.3 的 cost-facing demand/exceedance constraints。
4. BESS FOM。
5. cycling degradation economic wear。

PV 為外生既有資產時，其 sunk CAPEX 不進入不同 \((\alpha,\beta)\) 的增量比較；但論文須清楚說明。

mainline 不另加 full battery replacement/augmentation stream，以免和 annualized CAPEX、cycling wear proxy 產生 double counting。

## 7.9 單一 outage anchor 的新角色

### 不再做

- 不事先選 9/16 或其他單一日期作為 sizing source。
- 不宣稱一個 common anchor 對所有 \(\alpha\) 都具有代表性。
- 不以單一 outage branch 建立 arbitrary-start guarantee。

### 改為 ex-post binding window

對每個 \((\alpha,\beta)\)：

\[
s^*(\alpha,\beta)=
\arg\max_{s\in\mathcal S_\beta}G_s(\alpha,\beta).
\]

此窗口可用來：

- 解釋為何某組設計需要特定 reserve；
- 畫 load、PV、residual gap 與 BESS dispatch；
- 研究 binding window 是否隨 \(\alpha\)、\(\beta\) 改變。

建議稱：

- binding critical window；
- ex-post worst historical window；
- illustrative high-stress window。

避免再稱它為預先指定的 universal design-basis anchor。

## 7.10 Exhaustive adequacy audit / outage replay（A2 CLOSED）

annual normal-operation optimization 與 outage replay 是 **兩個分離的 programs/stages**，不是在同一 annual model 裡用 outage binary 切換 regime。

完成每個 Layer A design 後固定：

- \(E^N\)、\(E^U\)、\(P^B\)、\(CC\)；
- outage initial stored energy採 annual policy允許的最低 preparedness state：

\[
\boxed{
e_0=SOC_{min}E^N+R(\alpha,\beta)
}
\]

- outage grid import：

\[
\boxed{p_\tau^{grid}=0}.
\]

停電 replay 中 reserve 被視為可用 preparedness energy，因此 state bound 改為 technical SOC window：

\[
\boxed{
SOC_{min}E^N
\le e_\tau
\le
SOC_{max}E^N
}
\]

**不得**在 outage replay 中繼續要求 \(e_\tau\ge SOC_{min}E^N+R\)。

replay 期末只要求：

\[
\boxed{e_\beta\ge SOC_{min}E^N}
\]

不要求 outage 結束立即恢復 \(R\)。

### Layer A analytical-consistency replay

對所有 \(s\in\mathcal S_\beta\) 執行 \(\beta\)-hour replay。為與 §7.3 analytical reserve

\[
R=\max_s\sum[\alpha L-PV]^+\Delta t/\eta_d
\]

完全一致，這個 **Layer A consistency audit 不允許 outage 期間利用 PV surplus 對 BESS 再充電**。其目的不是模擬最靈活的 island operation，而是驗證 analytical reserve、efficiency、power limit、indexing 與 state transition沒有錯誤。

對真正 binding worst-case window，若只有 energy constraint binding，應有：

\[
|e_\beta-SOC_{min}E^N|\le\epsilon
\]

（容許 solver tolerance）。

### Layer B distinction

Layer B 是 fixed-design actual-capability stress test，可允許 outage 中 PV surplus recharge；不得把 Layer B 較靈活的 dispatch semantics反向拿來改寫 Layer A analytical reserve定義。

### audit 目的

- 驗證所有 valid baseline historical starts均可達 service target；
- 檢查 annual reserve floor與 outage-consumption semantics是否一致；
- 檢查 efficiency、state transition、power constraint、timestamp/indexing；
- 驗證 analytical reserve與power lower bound無 implementation錯誤。

正式描述：

> Exhaustive replay is a model-consistency audit of the valid-start all-start adequacy formulation under the stated outage-dispatch assumptions.

不得描述為未來停電保證或可靠度機率。

## 7.11 Layer A 保證範圍

可寫：

> For every valid historical outage start whose complete \(\beta\)-hour trajectory is observed within the formal case-year load–PV chronology, the design satisfies the modeled energy and power adequacy requirements under the stated technical assumptions.

不可寫：

> The design guarantees any future outage.

因為未納入：

- 未來 load/PV 分布改變；
- 設備故障；
- inverter/transformer/network constraints；
- BESS degradation-induced available-capacity loss；
- outage probability 與 weather correlation。

---

# 8. Layer A 實驗設計與輸出

## 8.1 計算順序

1. EOB baseline。
2. 預計算每個 \((\alpha,\beta)\) 的 \(R\)、\(P^{out}\)、\(s^*\)。
3. 跑 81 組 annual optimization。
4. 跑 all-start adequacy audit。
5. 匯總 response surface。
6. 完成結果解讀後，才鎖定 Layer B benchmark designs。

## 8.2 核心輸出矩陣

對每組 \((\alpha,\beta)\) 報告：

- \(R(\alpha,\beta)\)；
- \(P^{out}(\alpha)\)；
- \(E^N\)、\(E^U\)、\(P^B\)、\(CC\)；
- annualized total cost；
- resilience premium；
- TOU、CC、over-contract penalty、FOM、cycling degradation、annualized CAPEX 分解；
- binding critical window；
- ex-post exact demand diagnostics：各 usage period / TOU period \(D_{m,q}^{exact}\) 與 overall \(D_m^{exact}\)；
- degradation diagnostics：各 segment annual battery-side discharged energy、segment cost contribution、total cycling degradation cost、degradation cost share；
- realized SOC range、maximum hourly discharge fraction（僅作 power/use intensity diagnostic，不稱 DOD）；
- ex-post rainflow cycle-depth summary：maximum/median/energy-weighted DOD、depth-bin counts/energy、PWL-vs-rainflow cost difference；
- reserve-floor binding frequency / normal-operation SOC headroom；
- solver status、runtime、optimality gap（若適用）。

## 8.3 應產出的圖

1. Premium vs. \(\alpha\)，分不同 \(\beta\)。
2. Premium vs. \(\beta\)，分不同 \(\alpha\)。
3. \(E^N\) heatmap。
4. \(P^B\) heatmap。
5. \(CC\) heatmap。
6. resilience premium heatmap。
7. marginal cost heatmap。
8. binding-window calendar map。
9. premium decomposition。
10. degradation segment utilization / degradation-cost contribution summary（主文或 appendix，依結果重要性）。
11. ex-post realized DOD / rainflow depth distribution 與 PWL-vs-rainflow validation summary。

本研究不再要求 site-feasible/infeasible overlay 作核心輸出。

## 8.4 邊際變化

### \(\alpha\) 方向

\[
MC_\alpha(\alpha,\beta)\approx\frac{C(\alpha+\Delta\alpha,\beta)-C(\alpha,\beta)}{\Delta\alpha}
\]

### \(\beta\) 方向

\[
MC_\beta(\alpha,\beta)\approx\frac{C(\alpha,\beta+\Delta\beta)-C(\alpha,\beta)}{\Delta\beta}
\]

報告：

- 服務比例每增加 5 percentage points 的成本；
- outage target 每增加 1 h 的成本；
- 邊際成本是否遞增、遞減或近似固定。

## 8.5 knee / no-knee 判斷

不得因期待管理結論而硬找 knee。

### 若有 knee

- 報告 knee region，而不是單一神奇點。
- 檢查 knee 對 BESS cost sensitivity 是否穩健。

### 若無 knee

將 no-knee 作為正式結果：

> 成本–服務關係呈平滑、近似單調的邊際交換，無不依賴偏好的自然最佳服務水準。

此時決策仍需外部偏好、預算或 implementation constraints；本研究不替管理者做最終部署決策。

## 8.6 近似決策規則

若結果支持，可估計：

\[
\Delta C
\approx
CRF\left(C_E\Delta E^N+C_P\Delta P^B\right)
+\Delta C^{op}.
\]

其中 \(\Delta C^{op}\) 應包含 FOM、TOU、CC/over-contract 與 cycling-degradation 的淨變化。

若 \(\Delta C^{op}\) 很小，可進一步提出簡化報價規則；但必須報告全 81 格的 approximation error，不能只挑成功案例。

---

# 9. Layer B benchmark design selection

## 9.1 原則

Layer B design subset 必須在看完 Layer A 結果後選定。

不得先寫：

> \(0.6/0.8/1.0\times4/8/12\) 是 representative designs。

可寫：

> A benchmark subset was selected after observing the Layer A cost–capacity response surface.

建議用詞：

- selected benchmark designs；
- illustrative designs spanning the investigated space；
- Layer A design subset。

慎用 representative，除非明確說明代表的是 design-space coverage，而不是統計代表性。

## 9.2 選點程序需預先鎖定

在查看 Layer B 結果前，先凍結 selection rule，以免 cherry-picking。

### 情況 A：Layer A 有明顯 knee

選：

1. knee 前低要求設計；
2. knee/transition 設計；
3. knee 後高要求設計；
4. 視需要加 α 與 β 對照點。

### 情況 B：Layer A 無明顯 knee

建議：

#### 精簡版：3 designs

- low requirement / low premium；
- middle of response surface；
- high requirement / high premium。

#### 完整版：5 designs

- low-low corner；
- high-high corner；
- center；
- high-α / lower-β contrast；
- lower-α / high-β contrast。

目的不是宣稱五點最有代表性，而是分辨：

- service ratio effect；
- duration effect；
- combined high-requirement effect。

## 9.3 原本九點的處理

原本九點可在 Layer A 完成後重新被選中，但必須符合 selection rule。

正確因果順序：

> 先跑完整 surface → 再依結果選 benchmark subset。

不是：

> 先決定九點 → 再用 dense grid 替九點找理由。

---

# 10. Layer B：Fixed-design off-design capability stress test

## 10.1 Layer B 的功能

Layer B 回答：

> 在設備容量完全固定時，若 baseline PV 或需求假設惡化，設計最多能維持多少服務，以及從何種條件開始失效？

Layer B 不重新 sizing，因此反映 fixed-asset capability。

## 10.2 刪除的舊維度

### 刪除 initial SOC 30/50/80%

原因：

- Layer A 已內生建立全年 reserve policy。
- outage start state 使用最低允許 actual stored-energy state \(e_0=SOC_{\min}E^N+R\)。
- 再任意設定 30/50/80% 會混淆 reserve policy 與外生假設。

### 刪除 realized outage duration 4/8/12/24 h

原因：

- 每套設計本身已由其 \(\beta\) 定義。
- 若要 12 h service，應在 Layer A 建 12 h design。
- 以 4 h design 測 12 h 可作極端延伸，但不應成為主 sensitivity 維度。

## 10.3 保留的 stress dimensions

### A. Outage archetype

每一個 benchmark design 使用自己的 \(\alpha\)、\(\beta\)，由其 \(\beta\)-hour baseline windows 建立 archetype。

為避免 cherry-picking，建議預先註冊：

1. **Severe**：\(G_s\) 最接近 95th percentile 的非 binding window；binding maximum 另在 Layer A audit/illustration 報告。
2. **Typical**：\(G_s\) 最接近 50th percentile 的 window。
3. **Solar-assisted**：先選 PV contribution ratio 位於 top decile 的 windows，再取其中 \(G_s\) 接近中位數者。

PV contribution ratio 可定義：

\[
H_s=\frac{\sum_k\min(PV_{s+k},\alpha L_{s+k})\Delta t}{\sum_k\alpha L_{s+k}\Delta t}
\]

### 注意

- archetype 是 nested within each design’s \(\alpha,\beta\)。
- 不宜宣稱這是完整 factorial experiment 中 archetype 的獨立主效應。

### B. PV availability multiplier

建議：

\[
\gamma_{PV}\in\{1.0,0.5,0\}
\]

含義：

- 1.0：baseline PV；
- 0.5：顯著 availability deterioration；
- 0：PV unavailable。

### C. Demand multiplier

建議：

\[
\lambda_L\in\{1.0,1.1,1.2\}
\]

含義：

- baseline；
- +10%；
- +20%。

## 10.4 案例數

每組 benchmark design：

\[
3\text{ archetypes}\times3\text{ PV levels}\times3\text{ demand levels}=27
\]

- 3 designs：81 replays。
- 5 designs：135 replays。
- 9 designs：243 replays。

案例數應由研究問題與結果覆蓋決定，不以 243 為目標。

## 10.5 固定容量

Layer B 固定：

- \(E^N\)、\(E^U\)；
- \(P^B\)；
- \(CC\)（雖 outage 中不直接供電，仍保留 design identity）；
- \(R(\alpha,\beta)\)。

outage initial state：

\[
\boxed{
e_0=SOC_{\min}E^N+R(\alpha,\beta)
}
\]

這是最低允許 preparedness state，不是平均 SOC，也不是隨機 SOC。

## 10.6 Shortfall formulation

對 outage hour \(\tau\)：

\[
p^{dis}_\tau+\gamma_{PV}PV^{use}_\tau+s_\tau
=\lambda_L\alpha L_\tau+p^{ch}_\tau
\]

\[
s_\tau\ge0
\]

以 lexicographic 或足夠大的 penalty 最小化：

\[
ENS=\sum_\tau s_\tau\Delta t
\]

先最大化服務／最小化 ENS，再在同等 ENS 下最小化不必要 cycling 或 fuel。

## 10.7 Perfect foresight 定位

若 Layer B 在每個 outage window 內知道完整未來 PV/load trajectory，正式稱為：

> **maximum achievable service capability under perfect foresight**

或：

> **asset capability upper bound under full trajectory information**

不得直接稱為：

- actual operational reliability；
- real-time robustness；
- actual success probability。

### 可選加強

選少數高風險案例，加一個 rolling-horizon 或 simple rule-based dispatch 對照，用來量化 perfect foresight uplift。這是加強項，不是主線必要條件。

## 10.8 Layer B 指標

### Energy Not Served

\[
ENS=\sum_\tau s_\tau\Delta t
\]

### Normalized ENS

\[
nENS=\frac{ENS}{\sum_\tau\lambda_L\alpha L_\tau\Delta t}
\]

### Service achievement ratio

\[
SAR=1-nENS
\]

### Worst-hour shortfall

\[
WHS=\max_\tau s_\tau
\]

### Worst-hour shortfall ratio

\[
WHSR=\max_\tau\frac{s_\tau}{\lambda_L\alpha L_\tau}
\]

### Structured-scenario coverage

\[
Coverage=\frac{\#\{cases: ENS\le\epsilon\}}{\#\{structured\ cases\}}
\]

必須稱：

- structured-scenario coverage；
- stress-test pass proportion。

不得稱為 outage success probability。

## 10.9 Layer B 最終要回答的管理問題

- 哪類 design 對 demand growth 最敏感？
- 哪類 design 對 PV deterioration 最敏感？
- severe window 中的 failure threshold 在哪？
- energy shortfall 還是 power shortfall 主導失效？
- 增加 \(\alpha\) 與增加 \(\beta\) 對 off-design margin 的影響有何不同？

---

# 11. Implementation boundary：BESS site feasibility 不進主線

## 11.1 正式決定

BESS site feasibility / deployment limit 已從 methodological blocker 移除。

Layer A **不加入**任意：

\[
E^N\le E^{site}
\]

或：

\[
P^B\le P^{site}
\]

作 mainline constraint，也不要求 site、fire-code、interconnection 或 budget data 才能進行 production Layer A。

研究問題是量化：

\[
(\alpha,\beta)
\rightarrow
(E^{N*},P^{B*},CC^*,C^*)
\]

的 resilience–capacity–cost trade-off，而不是完成 NTUST turnkey engineering design。

## 11.2 結果用語

推薦：

- modeled BESS capacity requirement；
- planning capacity requirement；
- cost-minimizing capacity under the specified resilience target。

避免：

- NTUST should install X MWh；
- recommended campus installation size；
- physically deployable capacity；
- site-feasible design。

## 11.3 Site information 的角色

physical siting、fire-code compliance、interconnection capacity、construction constraints 與 institutional budget limits 只屬 **optional implementation context / future engineering overlay**。

若未來另做 site-specific engineering assessment，可在本研究 response surface 之上再疊加這些限制；但不回寫為本論文 Layer A 的必要 constraints，也不新增 RQ。

---

# 12. DG 雙軌邊界

## 12.1 Existing emergency DG

經校方設施單位確認：

- 既有 DG 供應法定 life-safety/emergency circuits；
- 不供應本研究 aggregate campus service load；
- 不參與正常 grid-connected operation；
- 不可將其 nameplate capacity 直接放入 campus service model。

因此在本研究 load boundary 中：

\[
P_{DG,existing}^{campus-service}=0
\]

建議論文文字：

> Existing emergency diesel generators are excluded from the main resilience model because they are dedicated to statutory life-safety circuits and are not available to supply the aggregate campus service load represented in this study.

### 校園 DG 實際規格是否必要

- 對主模型：非必要。
- 對 site description：有則更完整。
- 不應用其容量替 hypothetical campus-serving DG 定標。

## 12.2 Hypothetical campus-serving DG

定義為：

- 可在 outage 時支援 aggregate campus service load；
- 主線不在正常運轉使用；
- 非 NTUST 現有設備；
- 為 framework counterfactual。

目的：

> 衡量允許 dispatchable fossil backup 後，可交換到多少 BESS/成本下降，以及增加多少燃料與現地排放。

---

# 13. DG external coverage sweep

## 13.1 不進主模型自由 co-sizing

DG 不與 BESS 在 Layer A 主線一起自由最佳化，原因：

- 保留 zero-combustion mainline 的研究識別。
- 避免研究問題變成一般 least-cost PV–BESS–DG sizing。
- 直接辨識「多允許一點 fossil backup，會換到多少成本下降」。

## 13.2 固定 reference power

建立全研究固定的 strict reference gap：

\[
G^{ref}=\max_t\left[\alpha^{max}L_t-PV_t\right]^+
\]

建議：

\[
\alpha^{max}=1.0
\]

DG capacity：

\[
P_{DG}^{max}(\delta)=\delta G^{ref}
\]

\[
\delta\in[0,1]
\]

### 為何固定 \(G^{ref}\)

- 同一個 physical DG asset 在不同 \(\alpha,\beta\) 下保持相同容量意義。
- 避免每個 design 都把 50% 定義成不同大小的發電機。
- 提升跨 design 比較的可解釋性。

## 13.3 主 sweep

建議：

\[
\delta\in\{0,0.1,0.2,\ldots,1.0\}
\]

只套用 Layer A 後選定的 3–5 組 benchmark designs。

### 局部加密

若 10% sweep 顯示某區域存在快速曲率變化，再於該區域補 5% 點。

例如：

\[
\delta\in\{0.40,0.45,0.50,0.55,0.60\}
\]

若無 knee，不加密、不硬找 sweet spot。

## 13.4 DG-assisted residual gap

在簡化的 fully-dispatchable DG assumption 下：

\[
d_t^{DG}(\alpha,\delta)=\left[\alpha L_t-PV_t-P_{DG}^{max}(\delta)\right]^+
\]

\[
R^{DG}(\alpha,\beta,\delta)=\frac{1}{\eta_d}\max_{s\in\mathcal S_\beta}\sum_k d_{s+k}^{DG}(\alpha,\delta)\Delta t
\]

\[
P^{out,DG}(\alpha,\delta)=\max_t d_t^{DG}(\alpha,\delta)
\]

在每個 \(\delta\) 下，重新最佳化：

- BESS energy；
- BESS power；
- contract capacity；
- annual normal-operation dispatch。

DG capacity 本身固定，不由 optimizer 改變。

## 13.5 DG dispatch assumptions

主版本可採：

\[
0\le p^{DG}_\tau\le P_{DG}^{max}
\]

- 只在 outage replay 使用。
- 不計 normal-operation revenue。
- 若不建模 minimum loading、start-up 與 ramp，須列為 simplifying assumption。

### 加強版 fuel curve

\[
Fuel_\tau=aP_{DG}^{max}y_\tau+bp^{DG}_\tau
\]

\[
y_\tau\in\{0,1\}
\]

此形式納入 no-load/idling fuel。因 outage horizon 短，即使成為 MILP，計算量通常可控。

### Fuel availability

若取得油箱資料，可加：

\[
\sum_\tau Fuel_\tau\le Fuel^{available}
\]

若無資料，燃料供應視為充足，但列為 limitation。

---

# 14. DG 成本與碳排會計

## 14.1 年度固定 preparedness cost

無論是否停電都存在：

\[
C_{DG}^{fixed}=CRF_{DG}\cdot CAPEX_{DG}\cdot P_{DG}^{max}+FOM_{DG}\cdot P_{DG}^{max}
\]

每個 DG coverage case 必須支付其自己的固定成本。

## 14.2 單次事件變動成本

只在 outage 發生時產生：

\[
C_{DG}^{event}=DieselPrice\times Fuel^{event}
\]

報告單位：

- NTD/event；
- L/event；
- 可另報 NTD/kWh-DG generated。

## 14.3 單次事件現地碳排

\[
CO_2^{event}=EF_{diesel}\times Fuel^{event}
\]

報告：

- kg-CO₂/event；
- t-CO₂/event。

若只算燃燒排放，明確稱 onsite operational emissions；不要稱完整 lifecycle emissions。

## 14.4 不混用時間尺度

主結果分開呈現：

### Annual fixed preparedness cost

\[
C^{preparedness}=C^{BESS,fixed}+C_{DG}^{fixed}+\Delta C^{normal-op}
\]

### Event outcomes

- fuel/event；
- fuel cost/event；
- CO₂/event。

不得直接用：

\[
\frac{annual\ cost\ difference}{single-event\ CO_2}
\]

並稱為無條件 carbon price。

## 14.5 條件式等效年度分析（可選）

若要提供 outage-frequency sensitivity，定義：

\[
n=\text{assumed design events per year}
\]

\[
C^{equiv annual}(n)=C^{fixed}+nC^{event}
\]

\[
CO_2^{annual}(n)=nCO_2^{event}
\]

可示範：

- \(n=0.2\)：五年一次；
- \(n=1\)：每年一次；
- \(n=2\)：每年兩次。

但必須稱 illustrative assumption，不代表實際校園停電頻率。

## 14.6 Implied abatement cost

只有時間尺度對齊後才可計算：

\[
IAC(n)=\frac{C_{zero}^{equiv annual}(n)-C_{DG}^{equiv annual}(n)}{CO_{2,DG}^{annual}(n)-CO_{2,zero}^{annual}(n)}
\]

名稱可用：

- implied abatement cost；
- incremental cost of avoided onsite emissions；
- break-even carbon value under assumed outage frequency。

不得稱：

- Taiwan carbon fee；
- market carbon price；
- universal social cost of carbon。

---

# 15. DG 結果呈現

## 15.1 每個 coverage 點的輸出

- \(P_{DG}^{max}\)；
- \(E^N_{BESS}\)、\(P^B_{BESS}\)；
- contract capacity；
- annual BESS cost；
- annual DG fixed cost；
- annual fixed preparedness cost；
- fuel/event；
- fuel cost/event；
- onsite CO₂/event；
- BESS reduction relative to \(\delta=0\)。

## 15.2 主要圖

1. DG coverage vs BESS energy。
2. DG coverage vs BESS power。
3. DG coverage vs annual fixed preparedness cost。
4. DG coverage vs fuel/event。
5. DG coverage vs CO₂/event。
6. Annual fixed cost vs CO₂/event trade-off scatter。
7. Marginal BESS reduction per additional DG kW。

## 15.3 sweet spot 的判斷規則

### 可以說

- best-performing tested configuration；
- cost-minimizing coverage under baseline assumptions；
- knee region around X–Y%；
- marginal benefit begins to diminish beyond X%。

### 不可以說

- 50% is the universal optimum；
- literature recommends 50%；
- 50% is proven sweet spot，若只跑 25/50/100%。

### 若無 knee

正式結論：

> DG coverage creates a smooth cost–emissions trade-off without a preference-independent optimum; the final choice depends on the decision maker’s emissions tolerance or carbon valuation.

---

# 16. Sensitivity analysis

## 16.1 Layer A targeted sensitivity / robustness

Layer A 不追求「每個參數都掃一輪」的 generic sensitivity；\(\alpha\times\beta\) 81-point grid 是核心 planning response surface，不另稱 sensitivity analysis。

最低限度：

- **BESS cost scale**：以 PNNL v2024-derived 1 MW / 10 MW source cases作 scale-economy bracket；mainline coefficient choice依 preliminary \(P^B\) range與 parameter registry 鎖定。
- **SOC operating window**：10–90% mainline；20–80% 作 deliberately more restrictive technical sensitivity。
- **winter-PV treatment**：conservative zero-availability mainline vs alternative reconstructed/synthetic winter PV，一次性檢查 economic outputs。
- **reserve-floor formulation robustness（A2）**：mainline constant worst-case reserve floor vs perfect-information time-varying floor，只跑 6 個 targeted points：

\[
\alpha\in\{0.60,0.80,1.00\},
\qquad
\beta\in\{4,12\}\text{ h}.
\]

  constant-floor結果可直接重用81-grid mainline，只需新增6個 variable-floor solves。此檢查是 model-form screening，不是第二個 research question。若6點皆穩定即停止；只有出現 material shift時才可補 \(\beta=8\) 的3點，不自動擴張。
- **outage-load / short-gap reconstruction**：production methods 已由 Scripts 02–05 的 site-specific validation 鎖定；不重做 full hyperparameter sweep。若 final integration audit 顯示 formal outage logs 支持一個合理的 expanded contamination/recovery envelope，再做 targeted preprocessing robustness check；未驗證前不得宣稱 expanded envelope 對 final 81-point \(R/P^{out}\) 無影響。
- **efficiency**：A1 已鎖 \(0.90/0.90\)，不做 full efficiency sweep；只有 reviewer 明確要求才做小型 robustness check。

### Degradation validation / benchmark（不是重新打開 B1）

B1 mainline 已鎖 PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation。另做：

1. 全部 final EOB + Layer A solutions 的 ex-post rainflow cycle-depth / cost validation；
2. linear throughput cost只作 benchmark/equivalence diagnostic，不作第二個 mainline；
3. 若 PWL-vs-rainflow cost error 或 sizing implication異常，先檢查 segment implementation / calibration，再決定是否需要額外 selected-case model-form test。

不做 discount-rate sweep；\(r=5\%\)、\(n=20\) yr 固定。

目的：

- 檢查 premium 金額、response shape、knee/no-knee、binding mechanism 是否對關鍵假設穩健；
- 驗證 constant reserve-floor 保守性是否 materially 改變 sizing；
- 驗證 DOD-sensitive degradation implementation 的 cycle-depth fidelity，而不是增加沒有決策意義的 parameter sweep。

## 16.2 DG sensitivity

建議 one-at-a-time：

1. BESS cost；
2. DG CAPEX/FOM；
3. diesel price。

使用較粗 coverage：

\[
\delta\in\{0,0.25,0.5,0.75,1.0\}
\]

主版本可只套用 3 組 benchmark designs。

### 計算量

\[
3\text{ designs}\times5\text{ coverage}\times3\text{ parameters}\times2\text{ alt levels}=90\text{ solves}
\]

基準值可由 main sweep 重用。

## 16.3 不建議的過度計算

不做：

- 81 designs × 11 DG points × 所有敏感度的全交叉；
- 3×3×3 full factorial cost assumptions；
- 為了得到一個精確 DG 百分比而無限加密。

研究價值來自 trade-off 結構，不是案例數量。

---

# 17. 計算量規劃

## 17.1 Layer A

- EOB：1 solve。
- dense grid：81 solves。
- A2 variable-floor targeted robustness：最多新增 6 solves（若 material difference 才選擇性補 3 個 \(\beta=8\) points）。
- optional 24 h boundary：依選定 α 值增加 1–9 solves。
- all-start adequacy audit：可用解析／向量化 replay，不需要把每個 outage start 重新做年度 optimization。
- ex-post rainflow / DOD validation：post-processing，不計入 annual optimization solve 數。

## 17.2 Layer B

- 3 benchmark designs：81 short outage replays。
- 5 benchmark designs：135 short outage replays。
- 9 designs：243 short outage replays。

## 17.3 DG

### Main sweep

- 3 designs × 11 levels = 33 solves。
- 5 designs × 11 levels = 55 solves。

### Local refinement

- 每 design 約 2–4 extra points。

### OAT sensitivity

- 3 designs：約 90 solves。
- 5 designs：約 150 solves。

### 推薦總量

- Layer A：82 左右。
- Layer B：81–135。
- DG main + sensitivity：123 左右（3-design 版本）。
- 合計約 286–340 個主要 solve/replay，且不少為短 horizon、可平行或重用。

---

# 18. 驗證與 sanity checks

## 18.1 Data / chronology audit

正式 EOB 或 Layer A 前必須 assert：

1. exactly 8,760 intervals；
2. first model timestamp = 2024/11/01 00:00；
3. last model timestamp = 2025/10/31 23:00；
4. timezone = Asia/Taipei；
5. no duplicate timestamps；
6. every adjacent timestep = 1 h；
7. no missing timestamps；
8. model calendar/TOU labels由 interval-start timestamp 重建；
9. all reconstructed intervals有 provenance flags；
10. outage-contaminated observations 未經明確 reconstruction decision 不得直接作 baseline；
11. `pre_system` / `missing_winter` PV intervals 依主線規則標記；
12. load/PV 單位一致，negative/nighttime PV 等基本異常完成檢查。

另保留：

- Scripts 02 / 04 / 04b 的 pseudo-gap / head-to-head validation artifacts；
- 若 formal outage-log evidence 支持 expanded contamination/recovery envelope，執行 targeted preprocessing robustness check；否則不自行發明 recovery window；
- final integrated input 完成後重算 81-case \(R/P^{out}\)，作為 downstream data-integration consistency check。

## 18.2 公式與單位

- kW × h = kWh。
- reserve 公式明列 \(\Delta t\)。
- \(\eta_c,\eta_d\) 只套用一次，AC-side power / battery-side energy boundary 一致。
- \(C_E\) 的 denominator 與 \(E^N\) nameplate definition 一致。
- raw CAPEX → currency/base-year normalization → CRF annualization；順序不得混淆。
- FOM 若 already annual 不再乘 CRF。
- annual fixed cost 與 event cost 不混用。

## 18.3 BESS state / efficiency / degradation audit

### Aggregate state

- \(E^U=0.8E^N\) under mainline 10–90% SOC。
- annual normal operation：\(0.10E^N+R\le e_t\le0.90E^N\)。
- \(0.8E^N\ge R(\alpha,\beta)\)。
- mainline \(\eta_c=\eta_d=0.90\)；AC-side power / battery-side stored-energy boundary一致且效率只套一次。
- aggregate state-balance residual接近0；annual \(e_T=e_0\) 正確。
- no simultaneous charge/discharge audit。
- CAPEX charged to \(E^N\)，not \(E^U\)。

### Xu-derived intertemporal PWL degradation structure

- \(\lambda_k\) 由 final \(C_{rep}\) + locked PNNL DOD/cycle-life table 自動產生；不得 hard-code legacy slopes。
- \(x_t=e_t-SOC_{min}E^N=\sum_ke_{t,k}^{seg}\) 全年一致。
- \(0\le e_{t,k}^{seg}\le(b_k-b_{k-1})E^N\)。
- segment dynamics residual接近0；\(e_{T,k}^{seg}=e_{0,k}^{seg}\)。
- aggregate \(p_t^{ch/dis}\) 等於 segment-level power和。
- cycling cost 使用 battery-side discharged energy \(p_{t,k}^{dis}\Delta t/\eta_d\)。
- 明確測試 multi-hour deep-discharge synthetic trajectory，確認不會像 Harry hourly-reset proxy 一樣每小時重新回到 cheapest segment。
- 保存 segment energy/cost diagnostics、realized SOC range、maximum hourly discharge fraction。
- ex-post rainflow cycle-depth/cost 與 PWL結果比較；若差異異常，先修 implementation/calibration，不以文字合理化。

B2 accounting不另設 physical-life ≥20 yr hard gate；20 yr只作 financial analysis horizon。

## 18.4 Layer A adequacy / outage semantics

- \(\mathcal S_\beta\) 僅含完整 trajectory位於 case year內的 starts；不允許 year-end circular wrap。
- \(R\) 對 \(\alpha,\beta\) 原則上非遞減；\(P^{out}\) 對 \(\alpha\) 非遞減。
- annual normal-operation reserve floor全年滿足：\(e_t\ge SOC_{min}E^N+R\)。
- outage replay initial state = \(SOC_{min}E^N+R\)。
- outage replay中 **不得** 繼續要求 reserve floor；只要求 technical \(SOC_{min}E^N\le e_\tau\le SOC_{max}E^N\)。
- Layer A consistency replay grid import=0，且不利用 outage PV surplus再充電。
- replay terminal只要求 \(e_\beta\ge SOC_{min}E^N\)，不要求恢復 \(R\)。
- valid-start baseline exhaustive replay皆無 shortfall；binding window與預計算一致。
- 對 energy-binding worst-case window，terminal state應接近 \(SOC_{min}E^N\) within tolerance。
- Layer B 可允許 PV-surplus outage recharge；不可和 Layer A consistency semantics混用。
- 若 audit失敗，先修模型，不得靠文字解釋。

## 18.5 Billing / contract-capacity audit

至少保存：

- 12 個 usage periods 的四時段 Taipower billed maxima與 overall \(B_m=\max_qB_{m,q}\)；
- regular CC 與 supplementary CC components（NTUST case應固定為0）；
- bill-title month 與 actual usage-period start/end；
- 2025/01–10 十個 calibration-period historical hourly grid maxima \(H_m\)；
- \(B_m/H_m\)、fitted values、residuals；
- through-origin reproduced \(\kappa\)（target應重現既有約1.01037；若不同則追查資料/period alignment，不硬保留舊值）；
- gross-load vs observed-grid-import comparison；
- 5/16–10/15 summer-date audit；
- billing category / tariff source / effective dates；
- post-solve \(D_{m,q}^{exact}\)、\(D_m^{exact}\) 與 cost-facing epigraph/exceedance variables 的一致性檢查。

至少手算並由 code 精確重現：

- 2025/09 usage period（2025/10 標題帳單）：regular CC 5000 kW；四時段 maxima 4896 / 5016 / 3352 / 3776；half-peak exceedance 16 kW；\(16\times166.9\times2=5,340.8\) NTD。

另選至少一個不同 season/TOU binding pattern 的月份核對 energy charge、basic charge與 over-contract non-duplication logic。

## 18.6 DG audit

- \(\delta=0\) 必須重現 PV+BESS mainline。
- DG capacity 隨 \(\delta\) 線性增加。
- BESS requirement 原則上不應隨 DG coverage 增加而上升；若上升需解釋成本 coupling 或程式錯誤。
- fixed cost 與 event cost 分開。
- fuel 與 CO₂ 單位一致。
- 不允許 existing emergency DG 被誤標成 modeled campus-serving DG。

## 18.7 Solver reporting

每個 case 保存：

- status；
- objective；
- runtime；
- MIP gap（若有 binary）；
- infeasibility diagnostics；
- framework version；
- parameter-registry version/hash；
- input file hash；
- code/version hash。

---

# 19. 舊結果的處理

## 19.1 原 81-point Layer A

原 81-point Layer A 不得直接升級為 final results。

原因不是 Layer A 架構失效，而是 production specification 已實質更新：

- state 改以 \(e_t\) 為 primary stored-energy state；
- SOC window 鎖定 10–90%，reserve floor 明確位於 SOCmin 之上；
- all-start outage windows 改為 case-year valid starts，移除 circular wrap；
- Load/PV 改採 observed/baseline 分離與 outage-contamination reconstruction；
- tariff calendar、billing proxy 與 \(\kappa=1.01037\) 已鎖定；
- BESS capital-cost/annualization 改為 PNNL v2024-derived package + \(r=5\%\)、\(n=20\)；
- degradation 改為 PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation；Harry hourly-reset proxy 不再是 final mainline。

因此 legacy 81-point outputs 只保留作 regression targets / structural hypotheses。final EOB + 81-point Layer A 必須在 v7 specification 下重跑。

重跑後應逐項解釋新舊差異，而不是要求數值完全重現。

## 19.2 原 243 Layer B replays

定位為：

- preliminary debugging / exploratory results。

不得直接作 final Layer B，因為：

- design subset 尚未依 Layer A 結果正式選定；
- archetype selection 需預先註冊；
- perfect foresight 語意需鎖定；
- coverage 不得解讀為 reliability probability。

## 19.3 原 27 DG results

定位為：

- sparse exploratory comparison。

不得保留的舊結論：

- 「50% 是 sweet spot」；
- 「119 萬 NTD/t 是碳價」。

可保留的用途：

- 程式介面測試；
- 初步證明 DG 可以大量替代 BESS；
- 指導後續 0–100% sweep。

## 19.4 原 design-basis anchor

- 從 sizing 核心移除。
- 可保留作歷史方法說明或 ex-post illustrative window。
- 不再作為 arbitrary-start guarantee 的來源。

---

# 20. 建議章節結構

## Chapter 1 Introduction

1. 低碳轉型與停電服務連續性。
2. 同一 BESS 同時承擔正常運轉與 resilience 的管理衝突。
3. 既有研究多聚焦成本最佳化、單一 outage 或一般 microgrid sizing；本研究聚焦台灣高壓用戶 CC 經濟與 all-start service requirements 的整合量化。
4. 研究問題 RQ1–RQ4。
5. 貢獻與限制。

## Chapter 2 Literature Review

### 2.1 BESS multi-service economics

- TOU、peak shaving、contract capacity、degradation。

### 2.2 Microgrid resilience and outage survivability

- critical-load/service requirement；
- deterministic design event；
- stochastic islanding；
- all-start/worst-case preparedness。

### 2.3 SOC reserve and preparedness

- minimum SOC；
- economic cost vs disaster preparedness。

### 2.4 Fixed-design validation and stress testing

- ENS、shortfall、full-trajectory evaluation；
- perfect foresight vs executable operation。

### 2.5 PV–BESS–DG trade-offs

- life-cycle cost；
- DG reliability；
- cost–emission Pareto；
- sensitivity。

### 2.6 Research gap

不要宣稱沒有任何相關研究；應定位為：

> 缺少一個在台灣校園高壓用戶 tariff/CC 制度下，以 dense service-target response surface、全年 all-start deterministic reserve、fixed-design off-design test 與 external DG counterfactual 共同構成的決策量化案例。

## Chapter 3 Methodology

1. System boundary and formal case-year data pipeline。
2. Economic-only baseline。
3. \(\alpha\)、\(\beta\)、aggregate service proxy 定義。
4. all-start valid-start energy reserve。
5. power adequacy。
6. BESS state/SOC/reserve policy。
7. BESS cost annualization、billing proxy、PWL degradation。
8. annual BESS/CC model。
9. Layer A experiment。
10. benchmark selection rule。
11. Layer B stress test。
12. DG counterfactual。
13. sensitivity、validation、limitations。

## Chapter 4 Results and Discussion

### 4.1 EOB baseline

### 4.2 Layer A response surface

- capacities；
- costs；
- marginal changes；
- binding mechanisms；
- knee/no-knee。

### 4.3 Implementation boundary

- 明確說明 Layer A capacities 是 modeled planning requirements。
- site/fire-code/interconnection/budget 不進 mainline optimization。
- 若取得相關資料，只作 discussion context，不新增 core result layer。

### 4.4 Benchmark selection

先說規則，再列選點。

### 4.5 Layer B fixed-design capability

- ENS/nENS/WHS；
- failure thresholds；
- perfect-foresight caveat。

### 4.6 DG counterfactual

- coverage sweep；
- BESS substitution；
- annual fixed cost；
- event fuel/CO₂；
- knee/no-knee；
- sensitivity。

### 4.7 Management implications

每一組圖必須回答：

> So what should a campus planner know or do differently?

## Chapter 5 Conclusion

1. 回答 RQ1–RQ4。
2. 給三至五條決策規則。
3. 清楚限制。
4. Future work：critical-load inventory、stochastic outage frequency、rolling control、network constraints、DG reliability/co-sizing、site engineering feasibility。

---

# 21. 預期貢獻的安全寫法

## Contribution 1

建立一個將 annual tariff/contract-capacity economics 與 historical all-start outage adequacy 結合的 campus PV–BESS planning framework。

## Contribution 2

以 dense \((\alpha,\beta)\) response surface 取代少數預設點，量化容量、成本、邊際成本與 binding mechanisms。

## Contribution 3

提出一個在 Layer A 結果後選擇 benchmark designs 的 fixed-design off-design stress-test workflow，辨識 PV deterioration 與 demand growth 的失效條件。

## Contribution 4

以外生 DG coverage sweep 呈現 zero-combustion preparedness 與 fossil-assisted preparedness 的 BESS–cost–emissions trade-off，同時避免把 DG 改成主線 least-cost co-sizing 問題。

### 貢獻類型

- integrative；
- case-based；
- decision-quantification；
- management-oriented。

不是新最佳化演算法或普遍理論。

---

# 22. 主要 limitations

1. \(\alpha\) 是 aggregate service ratio proxy，不是真實 critical-load inventory。
2. historical adequacy claim 只針對正式 case year 內具有完整 \(\beta\)-hour trajectory 的 valid historical starts 與模型假設。
3. all-start worst-case reserve 是 conservative deterministic preparedness，不是 probabilistic reliability optimization。
4. BESS siting、fire-code、interconnection、construction 與 institutional budget 不進主模型，因此輸出是 modeled planning requirements，不是 deployable engineering recommendation。
5. hourly optimization 不能精確重現 15-min metering、intra-hour BESS dispatch、sub-hourly SOC/ramping 或瞬時 power adequacy；\(\kappa\) 只校準 monthly billing-demand proxy，不是 15-min profile reconstruction。
6. \(\kappa\) 以 **pre-BESS historical grid-import profiles** 與實際帳單校準後套用到 BESS reshaped grid profiles；這隱含 hourly-to-15-min multiplicative relationship在 BESS dispatch後仍近似可轉移。缺少 post-BESS 15-min metering時無法完全驗證此 transferability。
7. 2024/11–12 prolonged PV unavailability 在 mainline 以 conservative zero availability 處理，可能影響 annual economic results；以 alternative winter-PV sensitivity 檢查。
8. degradation mainline雖為 intertemporal DOD-sensitive convex PWL，但仍是 cycling economic-wear approximation；未顯式建模 calendar aging、temperature、C-rate、dwell SOC、dynamic SOH、augmentation與 replacement scheduling。
9. PNNL DOD–cycle-life points是 calibration data；三段有效 PWL為本研究的 convex approximation。ex-post rainflow用於 validation，但不代表模型可預測 cell-level physical lifetime。
10. 20-year horizon是 financial analysis period，不是 battery physical lifetime guarantee，也不是「implied life 必須 ≥20 yr」的 feasibility requirement。
11. outage replay若使用 PV，隱含 PV–BESS system具有適當 island-capable controls/protection/grid-forming capability；本研究不做 inverter/protection/interconnection engineering design。Layer B 的 \(\gamma_{PV}=0\) 只提供保守 capability boundary，不能替代 islanding-engineering validation。
12. Layer B perfect foresight 是 capability upper bound。
13. archetype × PV × demand 是 structured stress design，不是概率抽樣。
14. 主線未納入配電網路、component forced outages、BESS availability 或 DG reliability。
15. hypothetical DG 不是 NTUST existing emergency DG。
16. 若沒有 outage frequency，annual fixed preparedness cost 與 event fuel/emissions分開報告。
17. onsite CO₂ 不等同完整 lifecycle emissions。
18. 參數與結論轉移到其他場域前需重新校準 load、PV、tariff、billing proxy、cost 與 infrastructure context。

# 23. Q1／權威文獻錨點與用途

> 下列文獻用來支持方法方向，不代表它們原封不動使用本研究的 \(R(\alpha,\beta)\) 公式或研究參數。

## 23.1 Resilience valuation and islandable premium

- Laws, N., Anderson, K., Li, X., McLaren, J., & DiOrio, N. (2018). **Impacts of Valuing Resilience on Cost-Optimal PV and Storage Systems for Commercial Buildings.** *Renewable Energy, 127*.  
  用途：支持 resilience capability 會形成額外 islandable premium，且應與停電服務價值比較。

## 23.2 Stochastic islanding and uncertainty of outage timing

- Wu, R., & Sansavini, G. (2020). **Integrating reliability and resilience to support the transition from passive distribution grids to islanding microgrids.** *Applied Energy, 272*, 115254. https://doi.org/10.1016/j.apenergy.2020.115254  
  用途：支持 islanding occurrence/duration 具有不確定性，單一已知 outage 不是唯一研究路徑。

- Lee, J., Joung, S., & Lee, K. (2024). **Scalable optimization approaches for microgrid operation under stochastic islanding and net load.** *Applied Energy, 374*, 124040. https://doi.org/10.1016/j.apenergy.2024.124040  
  用途：支持 stochastic islanding、sequential realization 與 non-anticipative operation 是更高階方法；本研究因缺可信機率資料採 deterministic worst-case。

## 23.3 SOC reserve and preparedness

- Son, Y., Woo, H., Noh, J., Dehghanian, P., Zhang, X., & Choi, S. (2024). **Optimization of energy storage scheduling considering variable-type minimum SOC for enhanced disaster preparedness.** *Journal of Energy Storage, 93*, 112366. https://doi.org/10.1016/j.est.2024.112366  
  用途：支持以 minimum SOC/reserve 犧牲部分經濟性以提升 outage preparedness。

## 23.4 Backup capability across load and outage conditions

- Gorman, W., Barbose, G., Carvallo, J. P., Baik, S., Miller, C., White, P., & Praprost, M. (2023). **County-level assessment of behind-the-meter solar and storage to mitigate long duration power interruptions for residential customers.** *Applied Energy, 342*, 121166. https://doi.org/10.1016/j.apenergy.2023.121166  
  用途：支持 whole-load/critical-load fraction、不同 outage duration 與 temporally aligned load/PV backup assessment。

## 23.5 Annual chronology and cyclic storage boundary

- Gabrielli, P., Gazzani, M., Martelli, E., & Mazzotti, M. (2018). **Optimal design of multi-energy systems with seasonal storage.** *Applied Energy, 219*, 408–424. https://doi.org/10.1016/j.apenergy.2017.07.142  
  用途：支持 long-horizon storage scheduling 與合理的 cyclic boundary treatment。

## 23.6 PV–battery–diesel resilience and reliability

- Marqusee, J., Becker, W., & Ericson, S. (2021). **Resilience and economics of microgrids with PV, battery storage, and networked diesel generators.** *Advances in Applied Energy, 3*, 100049. https://doi.org/10.1016/j.adapen.2021.100049  
  用途：支持 hybrid microgrid 的 lifecycle economics、DG reduction opportunities 與 component reliability 必須完整考慮。

- Marqusee, J., & Jenket, D. (2020). **Reliability of emergency and standby diesel generators: Impact on energy resiliency solutions.** *Applied Energy*, 114918. https://doi.org/10.1016/j.apenergy.2020.114918  
  用途：支持 emergency DG 並非完全可靠；若未來擴充 reliability model，不應假設 DG 100% available。

## 23.7 Cost–emissions Pareto and DG sizing

- **Multi-objective optimization minimizing cost and life cycle emissions of stand-alone PV–wind–diesel systems with batteries storage.** (2011). *Applied Energy, 88*(11), 4033–4041. https://doi.org/10.1016/j.apenergy.2011.04.019  
  用途：支持成本與排放應以 Pareto trade-off 呈現，而非預先指定單一權重或固定最佳 DG 比例。

- **Optimal allocation and sizing of PV/Wind/Split-diesel/Battery hybrid energy system for minimizing life cycle cost, carbon emission and dump energy of remote residential building.** (2016). *Applied Energy, 171*, 153–171. https://doi.org/10.1016/j.apenergy.2016.03.051  
  用途：支持 PV–battery–diesel 系統需同時看 lifecycle cost、CO₂ 與 unused energy。

- **A multi-objective optimization model for sizing an off-grid hybrid energy microgrid with optimal dispatching of a diesel generator.** (2023). *Journal of Energy Storage, 68*, 107621.  
  用途：支持 DG capacity/loading 與 battery capacity 應系統化研究；不可用少數離散點宣稱通用 optimum。

- **New modelling approach for the optimal sizing of an islanded microgrid considering economic and environmental challenges.** (2023). *Energy Conversion and Management, 277*, 116636. https://doi.org/10.1016/j.enconman.2022.116636  
  用途：支持成本、lifecycle emissions 與 sensitivity analysis 的共同呈現。

- **Optimal sizing and energy management of a microgrid: A joint MILP approach for minimization of energy cost and carbon emission.** (2024). *Renewable Energy*, 120186. https://doi.org/10.1016/j.renene.2024.120186  
  用途：支持以 Pareto front 呈現 economic–environmental trade-off。

## 23.8 BESS efficiency boundary

- Qi, N., Huang, K., Fan, Z., & Xu, B. (2025). **Long-term energy management for microgrid with hybrid hydrogen-battery energy storage: A prediction-free coordinated optimization framework.** *Applied Energy, 377*, 124485. https://doi.org/10.1016/j.apenergy.2024.124485  
  用途：作 system-level BESS charge/discharge efficiency formulation 的近期 Q1 precedent；本研究據此鎖定 \(\eta_c=\eta_d=0.90\)。PNNL system-level round-trip efficiency另作 boundary-consistency cross-check，而不直接對稱拆成0.91/0.91。

## 23.9 DOD-sensitive cycling degradation

- Xu, B., Zhao, J., Zheng, T., Litvinov, E., & Kirschen, D. S. (2018). **Factoring the Cycle Aging Cost of Batteries Participating in Electricity Markets.** *IEEE Transactions on Power Systems*.  
  用途：支持以 convex piecewise-linear marginal cycle-aging costs與跨時間 segment energy states近似 cycle-depth aging，並可與 rainflow benchmark比較。production implementation 必須保留 intertemporal segment-state semantics；不得把 Harry-style hourly-reset proxy誤稱為 Xu-equivalent。

- Shi, Y., Xu, B., Tan, Y., & Zhang, B. (2018). **A Convex Cycle-based Degradation Model for Battery Energy Storage Planning and Operation.**  
  用途：支持 rainflow-based cycle degradation cost 的 convexity與 planning/operation relevance；本研究不嵌 full rainflow optimization，而把 rainflow降為 ex-post validation。

PNNL LFP DOD–cycle-life points與 v2024 cost package是 technical/economic calibration source；完整版本、頁碼、raw/effective-DOD interpretation 與 parameter lineage統一保存於 literature/parameter registry。

## 23.10 BESS cost source pointer

Blocker 1/7 已將 mainline BESS cost source 改為 PNNL v2024-derived LFP planning cost package；詳細資料列、版本、currency conversion、linearization 與 source pages **不在本 framework 重複列出**，統一移至 literature/parameter registry。

舊 NREL cost sensitivity 可保留為 legacy comparison source，但不再是 mainline BESS cost basis。

## 23.11 Temporal-resolution evidence pointer

hourly-resolution limitation 的近期主證據改以 **Omoyele et al. (2024)** 與 **Browne & Williams (2023)** 為主。它們的角色是支持：hourly aggregation 對 annual/planning quantities 可作近似，但對 power sizing、peak demand、battery operation / SOC 與 reliability-related quantities 可能更敏感。

這些文獻 **不提供** 本研究的 \(\kappa=1.01037\)，也不提供 through-origin estimator；\(\kappa\) 是 §4.3 的 NTUST site-specific empirical calibration。完整 citation、source pages、claim/anti-claim 與 evidence role 統一放入 literature evidence registry。

---

# 24. 最終決策邏輯圖（文字版）

```text
Raw NTUST Load / PV / bills
            │
            ▼
Formal case-year data pipeline
(hour-ending → interval-start; observed/base split;
outage-gap reconstruction; provenance flags)
            │
            ├───────────────┐
            ▼               ▼
Historical billing      Planning baseline
calibration view        Load / available PV
(observed Load-PV)            │
            │                 │
            ▼                 │
billing_demand_registry       │
+ calibrate_kappa.py          │
κ + 10-pair audit table       │
            │                 │
            └────────┬────────┘
                     ▼
Economic-only baseline (EOB)
annual regular CC + 10–90% SOC
ηc = ηd = 0.90
PNNL-v2024 CAPEX + CRF
PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation
                     │
                     ▼
For each α,β: scan every valid historical outage start
    ├─ energy requirement R(α,β)
    ├─ power requirement Pout(α)
    └─ ex-post binding critical window
                     │
                     ▼
Annual normal-operation optimization
constant reserve floor:
e_t ≥ SOCmin E^N + R
                     │
                     ▼
Separate outage consistency replay
start = SOCmin E^N + R
grid = 0; technical SOCmin only;
no reserve restoration requirement
                     │
                     ▼
Dense Layer A cost–capacity response surface
+ exact post-solve billing maxima
+ ex-post rainflow/DOD validation
                     │
                     ├─ 6-point reserve-floor robustness
                     ▼
Select benchmark designs only after Layer A
                     │
                     ▼
Fixed-design Layer B capability stress test
(archetype × PV availability × demand growth;
outage PV-surplus recharge allowed)
                     │
                     ▼
Failure thresholds / ENS / normalized shortfall

Implementation-stage boundary:
site / fire-code / interconnection / budget
are NOT Layer A constraints in this thesis.

Separate extension:
Selected Layer A designs
        │
        ▼
External DG coverage sweep δ = 0…100%
        │
        ├─ re-optimize BESS/CC at fixed DG capacity
        ├─ annual fixed preparedness cost
        ├─ fuel and CO₂ per outage event
        └─ cost–emissions trade-off / knee or no-knee
```

# 25. 下一步執行順序

## Phase 1：v7.1 production implementation freeze

1. **Scripts 01–05 component preprocessing CLOSED / PASSED.**
2. **NEXT：build final integrated annual input** from current `load_annual_baseline.*` and `pv_annual_baseline.*`；preserve observed columns、reconstruction provenance、long-PV status；regenerate interval-start calendar / summer / TOU / billing usage-period tags；assert exact 8,760-hour chronology。
3. 建立 `billing_demand_registry.csv`。
4. 建立 `calibrate_kappa.py`，從 final integrated input 的 observed Load–PV 重建 2025/01–10 calibration pairs。
5. Implement valid-start \(\mathcal S_\beta\)，移除 outage-window circular wrap。
6. Implement \(e_t\) state、10–90% SOC、constant reserve above SOCmin、\(\eta_c=\eta_d=0.90\)。
7. Populate PNNL v2024-derived \(C_E,C_P,FOM,C_{rep}\)，derive CRF 與 PWL \(\lambda_k\)。
8. Implement Xu-derived intertemporal degradation segment states、segment cyclic boundary、battery-side degradation energy accounting。
9. Implement case-year Taipower tariff module並重現 September-2025 regression case。
10. Implement post-solve exact demand reporting + ex-post rainflow validator。
11. 先完成 long-block/month holdout validation，再跑 separately validated winter-PV economic sensitivity。
12. DG cost/fuel/emission parameters 可於主線 Layer A 後平行完成。

## Phase 2：Layer A final run

1. EOB。
2. 81-point dense grid。
3. all-start Layer A analytical-consistency outage audit。
4. ex-post exact billing diagnostics + rainflow/DOD validation。
5. 6-point constant-vs-variable reserve-floor robustness；只有 material difference 才補 3 個 \(\beta=8\) points。
6. response surfaces、marginal costs、binding-window analysis、knee/no-knee。

## Phase 3：Benchmark selection

1. 在查看 Layer B 結果前凍結 selection rule。
2. 選 3–5 組 designs。
3. 原本九點降為候選，不作預設 representative set。

## Phase 4：Layer B final run

1. 預先註冊 archetypes。
2. 27 scenarios/design。
3. outage replay使用 technical SOC floor；可允許 PV-surplus recharge。
4. 輸出 ENS、nENS、WHS、WHSR、structured coverage。
5. Layer B 定位為 perfect-foresight capability upper bound。

## Phase 5：DG extension

1. 建立 fixed \(G^{ref}\)。
2. 跑 0–100% 每 10% coverage。
3. 視曲線局部加密。
4. 完整 annual fixed cost accounting。
5. 報 fuel/event 與 CO₂/event。
6. 做 BESS cost、DG cost、diesel price OAT sensitivity。
7. 不再使用「50% sweet spot」或無條件 carbon-price敘事。

## Phase 6：論文與口試

1. 方法章先鎖定 claim boundary。
2. Chapter 4 每張圖回答 management implication。
3. limitation 主動寫出，不等口委指出。
4. 口試能白話解釋：energy vs power、constant reserve vs outage consumption、annual vs replay state semantics、billing usage period、\(\kappa\)、DOD-sensitive PWL vs hourly throughput proxy、rainflow validation、financial horizon vs physical lifetime、perfect foresight、annual/event accounting。

# 26. 一頁式口試定調

> 本研究不是預測停電機率，也不是替校方選擇唯一服務水準或提供 site-specific BESS 工程設計。研究先將 NTUST 原始時序整理成固定 2024-11-01 至 2025-10-31 case-year chronology，保留 observed 與 planning-baseline series；歷史帳單校準只使用 observed Load–PV，並由實際 usage periods 的四時段 billed maxima 建立 site-specific hourly-to-15-min demand proxy \(\kappa\)。年度 planning 則對每組服務比例 \(\alpha\) 與設計停電時長 \(\beta\) 掃描所有 valid historical starts，建立 conservative energy reserve \(R\) 與瞬時 power requirement。正常運轉 optimization 使用同一套 LFP BESS、10–90% SOC、固定 \(\eta_c=\eta_d=0.90\)、SOCmin 以上 constant worst-case reserve、annual regular contract capacity、PNNL-v2024 annualized capital cost，以及 PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation。停電 adequacy 不在 annual model內用同一 reserve floor硬撐，而以獨立 replay 從最低 preparedness state開始、允許消耗 reserve至 technical SOCmin；Layer A consistency replay不利用 outage PV surplus recharge，Layer B capability stress test則可允許。billing maxima與 DOD/rainflow diagnostics都在 solve 後由實際 dispatch重算。完成 dense Layer A response surface與 targeted robustness後才選 benchmark designs做 fixed-design Layer B stress test；existing emergency DG不進主線，hypothetical campus-serving DG另以外生 coverage sweep呈現年度固定成本與單次事件燃料/碳排 trade-off。

# 27. 與 `session_summary_0715.md` 的逐項涵蓋稽核

> **目的**：本節不是新增研究方法，而是確保 2026-07-15 摘要中所有有效資訊都已在本框架中被保留、修正、降級或明確標示為待核實。原摘要同時混合了「方法決策、初步結果、專案待辦與舊版錯誤敘事」；因此新版不應逐字照搬，而應依資訊性質重新安置。

## 27.1 稽核結論

截至本版，`session_summary_0715.md` 的內容分成五種處理結果：

1. **保留並細化**：研究定位、EOB、dense Layer A、SOC reserve、R3/R4、annual state boundary、Layer B fixed-design stress test、DG 雙軌、敏感度與口試推導。
2. **修正後保留**：\(\alpha,\beta\) 的來源、single anchor 的角色、Layer B design subset、pass-rate 解讀、DG sweet spot、碳價解讀。
3. **降級為 legacy/exploratory evidence**：原 81-point Layer A、243 Layer B、27 DG results。
4. **保留為專案管理附錄**：校方設施邊界紀錄、外部資料核實、舊輸出檔名、工作順序與原定 deadline；existing emergency DG 與 BESS site information 均僅保留為 optional documentation / implementation context，不是 production-model prerequisite。
5. **明確刪除的錯誤主張**：共用 design-basis anchor 建立任意起點保證、九點事先具有代表性、50% DG 已證明為最佳、119 萬 NTD/t 是無條件碳價、structured pass rate 等同可靠度機率。

因此，本版的「涵蓋」不是逐句複製，而是確保每一條舊資訊都有明確去向。

## 27.2 研究定位的對照

| `session_summary_0715` 內容 | 本版處理 | 目前狀態 |
|---|---|---|
| 低碳轉型使 PV+BESS 承擔服務連續性成本 | §1.1、§1.2、§21 | 保留並細化 |
| NTUST 降為 demonstration | §0.1、§1.2 | 保留 |
| 輸出是曲線而非單值 | §0.1、RQ1–RQ2、§8 | 保留並發展成 dense response surface |
| \(\alpha,\beta\) 為外部政策輸入 | §0.1、§3.2–3.3 | **修正**為 decision-maker-specified planning targets；只有有法規證據時才稱 policy requirement |
| 不替校方選唯一 \(\alpha\) | §0.1、§1.2 | 保留 |
| 題目待老師定稿 | §1.3 | 保留 |

## 27.3 Layer A 的對照

| 舊內容 | v6.2 處理 | 目前狀態 |
|---|---|---|
| 年化投資＋TOU＋CC 基本費＋兩段超約＋退化 | §4、§7.8 | 結構保留；CAPEX/annualization、billing proxy、degradation numerical method 已依 audit 更新 |
| PV 外生 sunk | §3.1、§7.8 | 保留 |
| 全年 \(e_t\ge R\) | §5.1、§7.5 | **修正**為 \(e_t\ge SOC_{\min}E^N+R\) |
| outage 起點 \(e_0=R\) | §7.10 | **修正**為 \(e_0=SOC_{\min}E^N+R\) |
| R3：全年所有 start、\(\alpha\) 在 max 內、除 \(\eta_d\) | §7.2–7.3 | 保留核心；start set 修正為 case-year valid starts，不做 circular wrap |
| R4：全年最大瞬時缺口 | §7.4 | 保留 |
| 任意起點保證 | §7.10–7.11 | 限縮為 complete trajectory observed within formal case year 的 historical-data conditional adequacy |
| anchor β-specific、不同 α 共用 | §7.9、§19.4 | 刪除為 sizing 規則；改為每個 \((\alpha,\beta)\) ex-post binding critical window |
| annual cyclic \(e_T=e_0\) | §7.7、§18.3 | 保留；明確與 outage-window circular wrap 分離 |
| 純 LP 可省充放互斥 | §7.7、§18.3 | 保留為可接受簡化，但必須做 no-simultaneous audit |
| BESS state / SOC semantics unresolved | §4.4、§5.1、§7.5–7.7 | **已關閉**：LFP、\(E^N\)、\(e_t\)、10–90% SOC、reserve above SOCmin |
| fixed throughput degradation | §4.4.3、§7.8.2 | **已替換**為 PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation；linear throughput只作 benchmark |
| 15-min demand proxy unresolved | §4.3、§18.5 | **已關閉**：observed historical grid-import × billed overall maximum calibration；production script需重現/更新 \(\kappa\) |
| BESS cost/CRF provenance unresolved | §4.4.2、§7.8.1 | **方法已關閉**：PNNL v2024-derived cost package，\(r=5\%\)、\(n=20\)、CRF derived |
| \(E^{site},P^{site}\) / site overlay | §11 | **移出 core methodology**；只保留 optional implementation context |

## 27.4 Layer B 的對照

| 舊內容 | 本版處理 | 目前狀態 |
|---|---|---|
| 五維砍成三維 | §10.2–10.3 | 保留 |
| 刪 realized duration | §10.2 | 保留；\(\beta\) 已是設計承諾，不再另設實際 duration 維度 |
| 刪 initial SOC | §10.2 | 保留；由全年 reserve policy 取代 |
| archetype／PV／demand | §10.3 | 保留並要求 archetype selection rule 預先註冊 |
| 27 情境 × 9 設計 = 243 | §9、§10.4、§19.2 | **修正**：27 scenarios/design 保留；design 數量待 Layer A 後選 3–5，原九點僅為候選或 exploratory subset |
| soft shortfall \(\min\sum s_\tau\) | §10.6 | 保留 |
| 描述性、非因果、非機率 | §10.8–10.9、§22 | 保留並細化 |
| 原 pass rate | §10.8 | 改稱 structured-scenario coverage / stress-test pass proportion |
| 重新最佳化 outage dispatch | §10.7 | 保留，但明確定位為 perfect-foresight maximum achievable capability upper bound |

## 27.5 DG 的對照

| 舊內容 | 本版處理 | 目前狀態 |
|---|---|---|
| 現有 life-safety DG 排除 | §12.1 | 保留 |
| 校園實際 DG 規格不擋主模型 | §12.1、§29 | 保留 |
| hypothetical campus-serving DG 另案 | §12.2 | 保留 |
| DG 不與 BESS 在主線 co-sizing | §13.1 | 保留 |
| 原 25/50/100% | §13.3、§19.3 | 降級為 sparse exploratory comparison；正式版改 0–100% 規則化 sweep |
| 原以每組最壞缺口定標 | §13.2 | 修正為全研究固定 \(G^{ref}\)，提升跨 design 物理可比性 |
| fuel＋CO₂ 事後報告 | §14 | 保留並拆成 annual fixed cost 與 event variable outcomes |
| 50% sweet spot | §15.3、§19.3 | 刪除；只有完整 curve 顯示轉折時才稱 knee region |
| 119 萬 NTD/t | §14.4–14.6、§19.3 | 刪除無條件碳價解讀；僅能作明示 outage-frequency 假設下的 implied abatement cost |

## 27.6 參數、結果、文獻與待辦的對照

- 舊參數與舊數值結果仍由 §28 保存，但 813.75／694.4／CRF 0.07／constant \(c_{deg}\) 已明確降級為 replication-only。
- v7 final results 必須由新的 data chronology、state/SOC、billing proxy、PWL degradation 與 PNNL-derived cost package 重跑；legacy outputs 只作 regression targets/hypotheses。
- Blocker 1–5、7 的詳細 literature/source evidence 不再塞入本 framework，改由獨立 literature/parameter registry 管理。
- 舊 Q1/權威文獻錨點仍可保留作研究定位；若與新 registry 重複，以 registry 為 source of truth。
- 舊營繕組 DG「必問」清單已取消；existing emergency DG 僅保留既已確認的研究邊界與 optional documentation context。BESS site-feasibility 資料同樣維持 optional implementation context。
- 舊輸出檔名與工作關鍵路徑由 §31 保存。

---

# 28. Legacy 參數與數值結果登錄表

> **重要**：本節保存 `session_summary_0715.md` 的歷史數值，避免新版框架把已完成工作遺失。除非通過 §18 的 code/data audit，以下數值不得直接當 final thesis results。引用時應標為 **legacy/preliminary output generated under the v4/v5 specification**。

## 28.1 Legacy main parameter set

| 參數 | 舊值 | v7 狀態 |
|---|---:|---|
| BESS energy annualized coefficient \(c_E\) | 813.75 | **legacy/replication only**；不得作 mainline |
| BESS power annualized coefficient \(c_P\) | 694.4 | **legacy/replication only**；不得作 mainline |
| CRF | 0.07 | **legacy/replication only**；mainline 由 \(r=5\%,n=20\) 算得 0.0802426 |
| degradation cost \(c_{deg}\) | 0.55 | **legacy only**；mainline 改 PNNL-calibrated adaptation of Xu et al.'s intertemporal PWL DOD-sensitive cycle-aging formulation |
| summer regular-contract basic rate | 223.6 | case-year tariff example / legacy lineage；正式 tariff module 以 usage-period effective rule + period-specific rates為準 |
| 166.9 historical rate label | 166.9 | **不得再泛稱 non-summer regular basic charge**；2025/09 bill audit中166.9為 summer half-peak applicable rate |
| over-contract multiplier 1 | 2 | **mainline confirmed rule**；within first 10% exceedance，仍由 official case-year tariff registry治理 |
| over-contract multiplier 2 | 3 | **mainline confirmed rule**；beyond first 10% exceedance，仍由 official case-year tariff registry治理 |
| charge efficiency \(\eta_c\) | 0.95 | **legacy only**；mainline fixed \(0.90\) |
| discharge efficiency \(\eta_d\) | 0.90 | **mainline retained**；paired with \(\eta_c=0.90\) |
| NREL BESS sensitivity | 334 USD/kWh | legacy comparison source；非 v7 mainline cost basis |

### 參數使用規則

1. 正式 run 使用獨立 `parameter_registry` 作 source of truth。
2. 正式 `parameter_registry` 至少使用以下 12 個 machine-readable fields：`parameter_name`、`value`、`unit`、`currency`、`currency_base_year`、`source`、`source_version`、`capacity_basis`、`annualized`、`annualization_method`、`mainline_or_legacy`、`notes`。其中 `mainline_or_legacy` 為防止 legacy 數值混入 production run 的必要 guardrail，不得只靠自由文字備註取代。
3. PNNL v2024-derived \(C_E,C_P,FOM,C_{rep}\) 先完成 unit/currency normalization，再進 model。
4. \(r=0.05\)、\(n=20\) 為 mainline fixed assumptions；CRF 由 code 自動計算，禁止獨立 hard-code。
5. PWL \(\lambda_k\) 必須由 final \(C_{rep}\) 與 cycle-depth table 自動生成；segment states 必須跨時間並以 battery-side discharge energy計價。
6. \(\eta_c=\eta_d=0.90\)、\(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)、\(r=0.05\)、\(n=20\) 為已鎖 mainline assumptions；不得和 legacy候選值混用。
7. legacy coefficients 只用於 reproducing/diagnosing old results，不得混入 final cases。
8. lab-predecessor values（包含 legacy \(\kappa\) 或成本係數）不作 academic benchmark；學術 benchmark 優先使用官方規則、peer-reviewed mainstream/recent literature 與 authoritative technical reports。
8. 813.75／694.4 等歷史成本的 reconstructed lineage 若需保存，放在 registry 的 `legacy` 紀錄並標示 provenance confidence；不在 framework 中包裝成 verified mainline source。

## 28.2 Legacy Layer A outputs

`session_summary_0715.md` 記錄「Layer A 85 solves」，但主網格為 81 組，另含 EOB 與可能的 boundary/diagnostic cases。**正式版必須先從 case manifest 對齊 85 的組成，不能只沿用總數。**

### EOB legacy result

| 指標 | 舊值 |
|---|---:|
| BESS energy | 5.0 MWh |
| BESS power | 874 kW |
| contract capacity | 3,770 kW |
| annualized total cost | 90.06 million NTD/year |

目前處理：

- 可作 rerun regression target。
- v6.2 已實際改變 tariff/billing、SOC/state、cost annualization、degradation 與 outage-start indexing，因此 final EOB 必須重跑並說明差異。
- 不應在 audit 前直接寫入摘要或結論。

### Legacy structural findings

1. **Operating-space relation**：舊結果曾觀察
   \[
   E^*=R+6.09\text{ MWh}
   \]
   且在 12 個檢查案例中精確一致。
2. **Power binding**：舊結果曾觀察
   \[
   P^*=\max_t[\alpha L_t-PV_t]^+
   \]
   且 \(\alpha\) 每增加 0.05，power 約增加 259 kW。
3. **CC change**：舊結果顯示 CC 約增加 2.3%，超約罰款約由 515,000 NTD 降至 191,000 NTD。
4. **TOU effect**：韌性案例的 TOU cost 反而較低，因此舊版推論 flexibility-locking cost 為負或二階、premium 主要來自 CAPEX。
5. **Premium range**：主線約 +13% 至 +57%；\((1.0,24h)\) boundary 約 +89%。
6. **No-knee observation**：
   - β = 4/8/12 h 時，\(\alpha\) 每 +0.05 的舊邊際成本約 +1.10／+1.97／+2.71 million NTD；
   - \(\alpha=1.0\) 時，沿 β 的每小時邊際成本約由 4.31 降至 3.34 million NTD。
7. **Closed-form approximation**：
   \[
   \Delta C\approx c_E R+c_P\Delta P
   \]
   舊 81 格誤差約 +0.8% 至 +3.6%。
8. **NREL sensitivity**：premium 約降至 +9% 至 +43%，舊版認為結構性結論不變。

### 本版對 legacy Layer A findings 的處理

- 上述 1–8 項全部保留為 **待重現的 hypotheses / regression checks**；不得直接沿用為 v7 findings。
- 「無 knee」只有在 final dense surface、更新參數與一致 state definition 下仍成立，才可升級為 final finding。
- 「premium 幾乎純 CAPEX」必須由正式 cost decomposition 證明，不能只因 TOU cost 下降就概括。
- closed-form approximation 應重新計算誤差分布、最大誤差與可能失效區域。
- 24 h 僅作 boundary case，不與 4–12 h mainline 混在同一結論。

## 28.3 Legacy site-limit overlay

舊 hypothetical overlay（30/40/60/80 MWh 等）保留在 archive 只作歷史紀錄。

v6.2 處理：

- 不再作 mainline method demonstration。
- 不再要求重畫 site frontier。
- 不得稱為 NTUST actual deployability evidence。
- site/fire-code/interconnection/budget 若未來取得，可作 implementation-stage discussion 或 future work；不回寫為 core RQ/Layer A constraint。

## 28.4 Legacy DG outputs

| 舊結果 | 舊值／現象 | 本版正確定位 |
|---|---|---|
| \((\alpha,\beta)=(1.0,12h)\) pure BESS premium | +51.6 million NTD | sparse exploratory result，需在完整成本 audit 後重現 |
| 100% DG premium | +3.9 million NTD | 同上 |
| BESS energy change | 66.5 → 5.0 MWh | 可保留作 DG 替代 BESS 的初步證據 |
| event CO₂ | 39.1 t-CO₂/event | 需核實 fuel curve、排放係數與 event dispatch |
| 50% coverage | 舊稱「砍 premium 6–8 成，排放為 full case 約 55%」 | 不再稱 sweet spot；只視為三個測試點中的 intermediate outcome |
| \(\alpha=0.6\)：100% DG 比 50% 稍貴 | 過大固定成本無法被 BESS savings 抵銷 | 可作假設，但需由完整 annual fixed-cost accounting 重現 |
| 119 萬 NTD/t | 舊稱隱含碳價 | 取消無條件解讀；若保留，必須明示 outage frequency 與同一時間尺度 |

## 28.5 Legacy Layer B outputs

| 舊結果 | 舊值 | 本版處理 |
|---|---:|---|
| baseline PV100% × demand100% | 27/27 pass，含 Severe | 保留為 preliminary consistency evidence，不是 R3 的數學證明 |
| failure cases | 72 | 保留為旧 9-design subset exploratory count |
| failure pattern | 100% 為 Severe × 任一劣化 | 待 archetype preregistration 與 final benchmark subset 後重驗 |
| Typical/Solar | 81/81 pass | 同上 |
| demand growth tolerance | < +10% | 不可先當 final threshold；需依 final design subset 回報 |
| worst-hour shortfall | 4,487 kW | 保存為 regression target |
| near-worst-window margin | 約 0 | 可作成本最適 binding hypothesis，需正式 dual/binding analysis |

### Layer B 解讀修正

- 原「27/27 全過是任意起點保證的實證」改為：它與 Layer A adequacy formulation 一致，但保證來自 R/R4 定義與 exhaustive audit。
- 原 72/243 不能換算成現實失敗機率。
- final Layer B 應按每個 benchmark design 分開報 ENS、nENS、WHS、WHSR 與 structured coverage，而非只給總 pass count。

---

# 29. 校方設施資料清單與用途

> 本節以 DG 邊界確認為主。BESS site/fire-code/interconnection 資料在 v6.2 僅屬 optional implementation context，不是 Layer A prerequisite，也不影響 core RQ validity。

## 29.1 Existing emergency DG：boundary documentation only / optional

### 已確認且足以支撐主模型的邊界

依既有校方設施單位確認，本研究採用下列正式邊界：

- 校內既有 emergency DG 服務法定 life-safety / emergency circuits；
- 不供應本研究定義的 aggregate campus service load；
- 不參與正常 grid-connected operation；
- 因此其實際 nameplate capacity、台數、位置、燃料儲備與 ATS 細節不進入 Layer A、Layer B 或 hypothetical DG counterfactual 的 production-model inputs。

在本研究 load boundary 中維持：

\[
P_{DG,existing}^{campus-service}=0
\]

### 是否還需要向營繕組索取資料

**不需要把任何 additional existing-DG facility data 視為 production prerequisite。**

若校方容易提供，以下資料可自願保存作 case-study documentation，但不影響模型是否可正式執行：

1. emergency DG 的設備用途或可引用的書面說明；
2. 設備台數、位置與額定容量；
3. ATS / 啟動模式的一般描述；
4. 測試或維護紀錄的摘要。

取得上述資料的用途僅限於：

- Chapter 1 / Chapter 3 的 case-site description；
- corroborate existing DG 與 aggregate campus service-load boundary；
- future engineering / implementation discussion。

### 不得如何使用 existing DG 資料

即使取得實際設備規格，也不得：

- 將 existing emergency DG capacity 直接加入 aggregate campus outage supply；
- 以 existing DG nameplate capacity 作 hypothetical campus-serving DG 的 \(G^{ref}\)；
- 因設備存在而宣稱 NTUST 已具備本研究定義的 campus-wide resilience capability；
- 把設備台數、燃料或 ATS 細節變成 v7 production run 的必要條件。

因此，若不再向營繕組索取 additional DG data，**不會造成 v7 模型缺少必要輸入，也不影響 RQ1–RQ4 的成立。**

## 29.2 BESS site/implementation context：選擇性取得

若資料容易取得，可保存：

1. 可設置面積或 container footprint context；
2. 消防／用途分區的一般限制；
3. interconnection / transformer power context；
4. institutional budget / phased-deployment preference；
5. 是否已有 BESS 規劃或消防審查經驗。

但這些資料：

- 不作 production Layer A blocker；
- 不形成 \(E^{site},P^{site}\) mainline constraints；
- 不要求建立 feasibility heatmap；
- 不影響 RQ1–RQ4 是否成立。

## 29.3 資料在論文中的去向

- Chapter 1 Scope/Limitations：說明 existing DG 與研究負載邊界；site engineering 明確列為 scope outside。
- Chapter 3 Case Study：若有正式 DG 書面資料，記錄設備用途、確認日期與資料來源。
- Chapter 4：不設 core site-feasibility result section；必要時只在 discussion 補一小段 implementation context。
- DG extension：現有 DG 容量不作 \(G^{ref}\)；最多作 site description 或 future-work context。

---

# 30. 文獻與參數核實追蹤表

> v6.2 不新增 Blocker 1–5、7 的完整 citation dump。這些 audit-specific literature、source pages、cost tables、tariff documents 與 parameter lineage 將移至獨立 literature/parameter registry；本節只保留 v6.1 原本的研究定位型追蹤資訊。

## 30.1 已納入本版的核心錨點

- BESS cost source：v7 mainline 為 PNNL v2024-derived LFP planning package；完整 citation/parameter extraction 移至 registry。
- Gabrielli et al. (2018), *Applied Energy*：long-horizon storage / cyclic boundary。
- Laws et al. (2018), *Renewable Energy*：islandable/resilience premium。
- Marqusee et al. (2021), *Advances in Applied Energy*：PV–battery–diesel economics and reliability。
- Gorman et al. (2023), *Applied Energy*：critical-load fraction、outage duration、temporally aligned backup assessment。
- Wu & Sansavini (2020), *Applied Energy*：stochastic islanding/reliability–resilience。
- Son et al. (2024), *Journal of Energy Storage*：minimum SOC preparedness。
- Qi et al. (2025), *Applied Energy*：system-level BESS efficiency formulation；mainline \(\eta_c=\eta_d=0.90\)。
- Xu et al. (2018), *IEEE Transactions on Power Systems*：intertemporal convex PWL cycle-aging segment model。
- Shi et al. (2018)：convex rainflow/cycle-based degradation planning/operation reference；rainflow作 ex-post validation。
- Taipower case-year detailed tariff + NTUST actual bills：annual regular CC、four-period billed maxima、usage-period alignment、non-duplication與2×/3× over-contract rule。

## 30.2 舊摘要列為「待自行核實」的來源

下列來源不得因曾出現在舊 MD 就自動視為可引用。正式寫作前需確認完整作者、題名、期刊、年份、DOI、真正支持的敘述與期刊分區：

- İşcan & Arıkan (2025)
- Rodriguez (2024)
- Bazdar (2024)
- Chen & Liao (2011)
- Sepúlveda-Mora & Hegedus (2022)
- Harry-era C_BE／C_BP／CRF：僅作 legacy lineage；不再是 mainline source blocker
- 台灣 DG 排放係數或柴油排放因子（環境部或其他官方來源）
- DG相關台電/官方排放與燃料參數；**BESS tariff/CC/over-contract已由 case-year Taipower tariff + NTUST bills 關閉，不再列待核實 blocker**

## 30.3 文獻使用原則

1. Q1 文獻支持方法方向，不代表直接提供本研究的 \(\alpha,\beta\)、DG coverage 或 reserve formula。
2. 學長論文可作 model lineage/context，不應取代原始技術與成本來源。
3. 官方費率與排放因子優先於二手論文。
4. 對「主流」「Q1」「現行規定」等會隨時間改變的敘述，定稿時重新查證。

---

# 31. 舊輸出資產、待辦與關鍵路徑

## 31.1 既有輸出檔案清冊

### 論文草稿

- `Iris_thesis_Ch1.md`
- `Iris_thesis_Ch2.md`
- `Iris_thesis_Ch3_part1.md`
- `Iris_thesis_Ch3_part2.md`
- `Iris_thesis_Ch4_Ch5_skeleton.md`

### 結果資料

- `layerA_results_v4_main.csv`
- `layerA_results_v4_nrel_sensitivity.csv`（舊摘要寫作 `_nrel_sensitivity.csv`，正式清冊需確認精確檔名）
- `layerA_dense_grid_81.csv`
- `dg_comparison_27.csv`
- `layerB_243_replays.csv`
- `reserve_table_3_3_v4.csv`

### 圖表

- `fig1_premium_vs_alpha.png`
- `fig2_premium_vs_beta.png`
- `fig3_heatmap_site_frontier.png`

### 程式與框架

- `layerA_gurobi.py`：舊摘要稱已含 R3/R4；正式版仍需 §18 audit。
- `research_framework_v5.md`：歷史版本。
- `research_framework_v6_1_coverage_audited_2026-07-29.md`：上一版 audited framework。
- `research_framework_v6_2_blockers_resolved_2026-08-10.md`：historical predecessor / archived framework；僅供 lineage、regression 與 comparison，不得覆蓋或補寫 v7 mainline specification。

## 31.2 每一類舊資產的處理

| 資產 | 處理 |
|---|---|
| Layer A CSV | 僅作 regression input；v7.1 specification 已改變，final EOB + 81-point Layer A 必須重跑 |
| Layer B 243 CSV | 作 exploratory archive；final subset 與 archetype freeze 後重跑 |
| DG 27 CSV | 作 sparse-interface test；正式 DG curve 重跑 |
| 舊圖 | 不直接進 final thesis；用 v7.1 final data regeneration；site-frontier 圖保留 archive only |
| 舊 Chapter 1–3 | 依本框架重點修改，不直接假設已同步 |
| Chapter 4–5 skeleton | 保留骨架，等待 final results |
| `layerA_gurobi.py` | 建立 version hash、unit tests、case manifest、solver log |

## 31.3 待辦優先順序

### Production Layer A 前必做

1. 本機 solver 對數與 case manifest，釐清舊「85 solves」組成。
2. **Component preprocessing 已完成；final integration 尚待完成。** Scripts 01–05 已輸出 audited observed / Load-baseline / PV-baseline artifacts。Production Layer A 前必須由 current v7.1 outputs 生成 final integrated 8,760-hour annual input，重新生成 TOU/billing tags並完成 integration audit；pre-v7 `annual_input_existing_pv.*` 不得直接沿用。
3. `billing_demand_registry.csv`：usage-period indexing、regular/supplementary CC、four TOU maxima、bill source。
4. `calibrate_kappa.py`：observed Load–PV + billing registry重建10 pairs、ratios、residuals與 \(\kappa\)。
5. valid-start outage indexing、annual/replay state semantics、10–90% SOC、\(\eta_c=\eta_d=0.90\) audit。
6. populate PNNL v2024-derived \(C_E,C_P,FOM,C_{rep}\)，derive CRF與 PWL \(\lambda_k\)。
7. implement Xu-derived intertemporal degradation segment states + segment cyclicity + battery-side discharge costing；建立 synthetic multi-hour deep-cycle unit test。
8. implement/bill-audit Taipower tariff：summer 5/16–10/15、annual regular CC、supplementary CC=0、four TOU periods、non-duplication、2×/3× tiers；重現2025/09 bill regression case。
9. post-solve exact demand maxima + ex-post rainflow validator。
10. winter-PV economic sensitivity once。
11. DG cost/fuel/emission parameters可在主線 Layer A後平行完成；BESS site data不再是 blocker。

### 模型與分析

12. final EOB + 81-point Layer A。
13. valid-start analytical-consistency outage audit、cost decomposition、intertemporal PWL diagnostics、rainflow/DOD validation、marginal analysis、knee/no-knee。
14. 6-point constant-vs-variable reserve-floor robustness；material difference才補3個 \(\beta=8\) points。
15. freeze benchmark selection rule and select 3–5 designs。
16. final Layer B 27 scenarios/design。
17. DG 0–100% main sweep + local refinement + OAT sensitivity。

### 寫作與口試

18. 同步簡報中的舊 `Validation`、固定 50% SOC、五維 Layer B、single anchor、site-feasibility RQ 與 50% DG sweet spot 敘事。
19. Chapter 4 只填 final/audited v7.1 outputs，legacy values 放在研究紀錄而非正文結論。
20. Chapter 5 回答 RQ1–RQ4、限制與 management rules。
21. 口試需能獨立推導／解釋：case-year valid starts、R、R4、SOCmin + reserve floor、annual state boundary vs outage circular wrap、CC coupling、billing proxy \(\kappa\)、usage-period alignment、Xu-derived intertemporal PWL DOD-sensitive degradation structure、rainflow validation、CRF annualization、perfect foresight、annual/event accounting。

## 31.4 關鍵路徑與時程

舊摘要的關鍵路徑是：

```text
solver/code audit  ||  slide synchronization
           ↓
Layer A final results
           ↓
Chapter 4 results
           ↓
Chapter 5 / abstract
           ↓
oral-defense preparation
```

本版加入兩個不能跳過的 gates：

```text
Layer A final surface
           ↓
benchmark selection frozen
           ↓
Layer B + DG extension
```

`session_summary_0715.md` 記錄的 working deadline 為 **2026 年 9 月底**。本版保留它作專案時程假設，但應由研究者確認是否仍是正式 deadline。BESS site data 不阻擋 Layer A，且不再是 core methodology requirement；production run 真正必須完成的是 data chronology、billing/tariff、BESS state/degradation/cost parameter population 與 code audit。

---

# 32. 最終 coverage gate

v7.1 現在即為 **authoritative coding specification**。下列項目是 **final production-results acceptance gate**：在將 EOB、Layer A/Layer B/DG outputs 視為可進入論文正文的 final/audited production results 前，逐項確認。未勾選不阻擋 coding，但 production run 不得以 legacy／pending 值補缺，且未通過相應 gate 的輸出不得標記為 final。

### Research positioning / unchanged core
- [ ] 研究定位與題目方向已同步。
- [ ] \(\alpha,\beta\) 未誤稱為外部政策標準。
- [ ] RQ 只保留 RQ1–RQ4；site feasibility 不再是條件式 RQ。
- [ ] Layer B selection rule 在 final Layer B 結果前凍結。
- [ ] Layer B 不再使用 initial-SOC 與 realized-duration 維度。
- [ ] structured coverage 不被稱為可靠度機率。
- [ ] DG 使用固定 \(G^{ref}\) 與規則化 coverage sweep。
- [ ] annual fixed cost 與 event outcomes 未混用。
- [ ] 50% DG 與 119 萬 NTD/t 的舊過度解讀已從簡報、正文與口試稿移除。

### Blocker 1 — BESS semantics
- [ ] stationary LFP reference、\(E^N\)、\(E^U\)、\(e_t\) definitions 已同步至 code。
- [ ] mainline SOC = 10–90%，\(E^U=0.8E^N\)。
- [ ] reserve floor = \(SOC_{\min}E^N+R\)。
- [ ] outage replay initial \(e_0=SOC_{\min}E^N+R\)。
- [ ] AC/DC efficiencies 各套用一次。
- [ ] CAPEX charged to \(E^N\)，not \(E^U\)。

### Blocker 2 — chronology / baseline data

- [x] **Component preprocessing Scripts 01–05 passed**：
  - exact 8,760 interval-start observed timeline；
  - observed Load/PV preserved；
  - Load short-gap production rule = same weekday ±6 weeks / K=1 / outside-gap RMSE；
  - exactly 10 Load hours reconstructed in planning baseline；
  - PV donor benchmark validated；
  - CWA vs donor head-to-head completed on the same 604 pseudo-events；
  - PV short-gap production rule = CWA `hourly_ghi_ratio_median` with leave-target-day-out fitting；
  - exactly 10 short-gap PV hours reconstructed；
  - 1,463 long unavailable PV hours assigned zero in mainline and not mislabeled as reconstructed。
- [ ] **Final integrated annual input passed**：
  - generated from current v7.1 `load_annual_baseline.*` and `pv_annual_baseline.*`；
  - exact 8,760 chronology；
  - observed equality verified；
  - reconstruction/status provenance retained；
  - interval-start calendar / summer / TOU / billing-period fields regenerated and audited；
  - no pre-v7 baseline artifact contamination。
- [ ] \(\mathcal S_\beta\) 不做 circular wrap。
- [ ] 若 formal outage-log evidence 支持 expanded contamination/recovery envelope，targeted robustness check 已完成；否則已記錄「無額外 recovery-envelope evidence，不自行發明 window」。
- [ ] long-block/monthly holdout validation 已完成後，winter-PV alternative economic sensitivity 已保存。

### Blocker 3 — degradation
- [ ] constant \(c_{deg}=0.55\) 已退出 mainline。
- [ ] 五個固定 LFP DOD–cycle-life calibration points（0.05/192000、0.30/32000、0.60/8000、0.70/6000、0.80/4800）已寫入 machine-readable registry，且 interpretation metadata 完整。
- [ ] PWL breakpoints / \(C_{rep}\) lineage 在 registry 鎖定；legacy Harry-era replacement basis 不得作 mainline。
- [ ] \(\lambda_k\) 由 final \(C_{rep}\) 與固定 cycle-life calibration 自動產生。
- [ ] segment energy/cost 與 \(r_{\max}\) diagnostics 已輸出。
- [ ] degradation claim 與實際 implementation fidelity 一致。

### Blocker 4 — billing/tariff
- [ ] historical grid import—not gross Load—用於 \(\kappa\) calibration。
- [ ] \(\kappa=1.01037\) 以 2025/01–10 valid-PV months 重現。
- [ ] Nov/Dec 仍留在 12-month simulation。
- [ ] summer boundary = 5/16–10/15。
- [ ] case-year bills/effective-date tariffs 與 over-contract rules 完成 audit。
- [ ] hourly model 未被描述成 exact 15-min reconstruction；\(\kappa\) 僅作用於 monthly billing-demand proxy。
- [ ] \(\kappa\) 被標為 NTUST site-specific empirical calibration，而非 literature/universal 或 lab-predecessor benchmark。
- [ ] temporal-resolution evidence registry 以 Omoyele et al. (2024) 與 Browne & Williams (2023) 支撐 hourly limitation claim。

### Blocker 5 — site feasibility
- [ ] \(E^{site},P^{site}\) 未進 mainline constraints。
- [ ] site/fire-code/interconnection/budget 未列為 production blocker。
- [ ] outputs 稱 modeled/planning requirements，不稱 final recommended installation。

### Blocker 7 — capital cost / annualization
- [ ] PNNL v2024-derived \(C_E,C_P,FOM,C_{rep}\) 已填入 registry。
- [ ] `parameter_registry` 完整 12-field schema 已實作，包含 `mainline_or_legacy` 與 `notes`。
- [ ] currency、base year、capacity basis、raw/annual flag 完整。
- [ ] \(r=5\%\)、\(n=20\) yr。
- [ ] CRF 由 code 算得 0.0802426，非獨立 hard-code legacy 0.07。
- [ ] raw CAPEX → normalization → CRF annualization 順序正確。
- [ ] annual FOM 未再次 annualize。
- [ ] 813.75／694.4／0.07 僅作 legacy replication。

### Final rerun / traceability
- [ ] final EOB + 81-point Layer A 已依 v7.1 重跑。
- [ ] legacy EOB / Layer A 差異已解釋。
- [ ] legacy output files 已封存，final outputs 使用明確版本名稱。
- [ ] framework、parameter registry、input data、code 與 solver logs 可追溯。

通過以上 checklist 後，才可將本版視為可執行、可追溯且與後續 audit resolutions 一致的 production research specification。


---

# 33. Preprocessing empirical freeze / traceability snapshot

本節記錄 v7.1 相對於 v7 的 preprocessing empirical changes，供 code audit、thesis-method traceability 與 future regression 使用；它不是新的研究問題。

### 33.1 Load

Selected production method：

`same_weekday_pm6weeks_top1_context_rmse`

Validation：

- 92 pseudo-events；
- MAE 100.436957 kW；
- RMSE 174.069420 kW；
- signed energy bias +0.252411%；
- mean event absolute energy bias 436.771739 kWh。

Production：

- 10 reconstructed hours；
- 2025-04-19 event → 6,636 kWh；
- 2025-08-02 event → 18,689 kWh；
- observed Load unchanged。

### 33.2 PV short gap

Donor benchmark：

`±30 days / K=5 / mean`

- MAE 34.625033 kW；
- RMSE 49.998621 kW；
- signed energy bias +1.113409%；
- mean event absolute energy bias 135.937748 kWh。

Selected CWA production method：

`cwa_hourly_ghi_ratio_median_leave_target_day_out`

- MAE 16.954595 kW；
- RMSE 29.741402 kW；
- signed energy bias +1.669484%；
- mean event absolute energy bias 51.967974 kWh；
- paired event wins: 486/604 MAE, 479/604 RMSE, 454/604 event-energy error。

Production：

- 10 short-gap PV hours reconstructed；
- reconstructed event energy 211.887706 kWh + 965.124933 kWh；
- observed PV unchanged；
- 1,463 long unavailable PV hours remain zero in mainline。

---
