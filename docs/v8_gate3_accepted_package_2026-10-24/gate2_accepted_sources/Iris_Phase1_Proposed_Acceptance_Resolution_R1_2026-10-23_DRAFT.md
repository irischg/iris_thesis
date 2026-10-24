# Iris Thesis — Phase-1 Proposed Acceptance Resolution R1

**日期：2026-10-23（Asia/Taipei）**
**狀態：PROPOSED ACCEPTANCE RESOLUTION R1 — DRAFT / NOT ACCEPTED / PENDING USER DECISION**
**文件類型：** 供研究者一次審查 Candidate R2、Class-C Guard Additive Clarification R1 及必要勘誤的決策草案。本文件不是 Acceptance、不是 Candidate R3、不是 Coding／Pilot 授權；不改寫 R2、Clarification R1、Framework、Registry、程式、資料或任何歷史 artifact。

---

## 1. Source identities（2026-10-23 本輪重新以 SHA-256 唯讀核對）

### 1.1 決策對象（不可變；本文件只引用、不覆寫）

| ID | 路徑 | SHA-256 | Bytes | 狀態 |
|---|---|---|---:|---|
| R2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` | 40,221 | CANDIDATE R2 / NOT ACCEPTED（R2 L4） |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` | 30,690 | DRAFT / NOT ACCEPTED（CL1 L4） |

### 1.2 依據來源

| ID | 路徑 | SHA-256 |
|---|---|---|
| CORE | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis/src/annual_design_model_v7_2.py`（CORE_VERSION r10，L78；HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；相對 HEAD 無變更） | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| BRIDGE | `…/iris_thesis/docs/checkpoints/transition_settlement_decision_bridge_v7_2_2026-09-09.md` | `7bb5c6c134e6c790088999ba80464dc37087ddcebcac0408399413176c952394` |
| PROT | `…/iris_thesis/docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
| CONST | `C:/Users/Iris C/Downloads/Iris_Thesis_Response_Mode_and_Research_Governance_Constitution_2026-10-03.md` | `4f5eaf050d96f84d96e06ebebd53e095f209ad50bb0a0f94a180f2dd0efc9c38` |
| FW74 | `…/iris_thesis/docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| REG74 | `…/iris_thesis/docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| STATE | `…/iris_thesis/docs/ai_handoff/CURRENT_STATE.md`（L45：Framework v7.4 與 Registry v7.4 `CLOSED / ACCEPTED`） | `043711e8bb422bec7e26ea8263a06ffbf4bf7d28af27cefa91b190f2868b327f` |
| PTR | `…/iris_thesis/configs/current_mainline_pointer.json` | `ed7005dea8dc423fb4372554b3f8d15fd34c3988441c4fb14c2dede0d64afcb4` |
| S11 | `…/iris_thesis/data/reference/taipower_seasonal_settlement_matrix_v7_2.csv` | `ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79` |
| REPORT | `C:/Users/IRISC~1/AppData/Local/Temp/iris_classc_guard_experiment_20261023/run_20261023T060151Z/REPORT.md` | `db021bf52689c504b3ee5cd05fffe9de74ef48e7f734a1cfbffd11c4e21b8439` |
| MANIFEST | 同目錄 `MANIFEST.json`（174/174 檔案重新雜湊一致） | `303005d9aa2a8d19c4551919805cdb0fcc284a701e9f207e72310e6479a634cc` |
| EXP3 | 同目錄 `artifacts/exp3_adversarial.csv` | `bb8754e300c47876aac386477867c7a4ff07f5979a8747243c41d8e1df7b14d7` |
| EXP4 | 同目錄 `artifacts/exp4_counterexample.json` | `d5c5f4f3abfaaae64189fbd58471dedb0c2a59bc134b41ddee751ca9a6edf364` |
| EXP5 | 同目錄 `artifacts/exp5_month_fixture.json` | `485a3400d84faada485fda4a39d31289e7d6359fb8862d369bcc5fd1a78f9706` |

**Conversation-only 證據（無持久化檔案，不補造 hash）：**
- 2026-10-23 Class-C Guard Clarification R1 Independent Targeted Static Audit：Claude Code session `180c3fec-52f7-4dc4-8216-e37c9b7a67f6` 的對話輸出。`NOT PERSISTED`。
- 2026-10-23 R2 Independent Static Audit（Codex rollout `8934245fa43b7238bfb581975c92262dca58ddbb9587d7e55572e5be88fa1fcf`）：審查時僅核對身份，未讀內容；R2-N01／R2-N02 已由 primary bytes 獨立重建。
- Historical Decision Recovery（Verdict B）：無持久化檔案；有界 repository 搜尋結果與其結論一致（SUPPORTED，非 CONFIRMED）。

---

## 2. Independent audit verdict（摘錄自上述 conversation-only 審查）

**整體：CONDITIONAL PASS。** CL1 可與 R2 一起進入研究者 Acceptance Decision Gate；條件為 F-01、F-02 須在 acceptance record 處理，並由研究者就 F-11 作決定。審查未發現 HOLD 等級缺陷。依 PROT L681–691，CONDITIONAL PASS 不是 `<TOPIC> — PASS`，更不是 `CLOSED / ACCEPTED`。

| 項目 | 判定 |
|---|---|
| Source identity | PASS |
| Governance | CONDITIONAL PASS（F-01、F-11） |
| Guard mathematics | PASS |
| Mathematical impossibility claim（T1/T4） | CONDITIONAL PASS（F-04） |
| Cost-bound certificate（T2/T5/§7.4） | CONDITIONAL PASS（F-03；F-07、F-08） |
| Experimental evidence interpretation | CONDITIONAL PASS（F-05、F-06） |
| Historical accepted-result boundary | PASS（F-10 資訊性） |
| R2-N02 Big-M correction | CONDITIONAL PASS（F-02、F-09） |
| Readiness for user decision | CONDITIONAL PASS |

---

## 3. Exact corrective wording（勘誤；僅於研究者核定後生效）

以下每一條均以「原文位置 → 問題 → 核定後生效文字」呈現。未列出的 CL1／R2 文字不受本節影響。

### F-01 文件優先效力

- **原文位置：** CL1 L20（「凡寫『建議 successor 使用以下文字』之處，都只是供未來另行授權的 R2 successor 引用的候選文字」）；CL1 L257（§7.4 標題「建議 successor 採用」）；CL1 L295（§9「建議 successor 使用的精確替換文字」）。
- **問題：** CL1 自述其文字非 binding；若研究者僅「接受 R2 + CL1」，R2 §9.4 L360–361 的「≤」與 R2 §8.3 L275 的 post-solve 式措辭仍然有效，R2-N01／N02 無法形式封閉。
- **核定後生效文字：**

> **R-01（Precedence）** 經本 Resolution 勘誤修正後之 Clarification R1 §4.2（L81–114）、§7.4（L257–264）、§9（L287–312），在與 Candidate R2 §8.3（L259–286）、§9.4（L355–366）、§11（L397–429）不一致之範圍內具優先效力。CL1 L20、L257、L295 所稱「僅供 successor 引用」之限制，於上述範圍內以本條取代。Candidate R2 其餘未被明確覆寫之內容保持不變（範圍見本文件 §4）。

### F-02 Big-M（R2-N02）

- **原文位置：** CL1 L304（「任何小於這個最小值的常數，都不是合法的 tightening；若要使用，必須另行證明它對所有保留的 cost-optimal 與 ε-feasible 點都有效」）；R2 L360–361。
- **問題：** 前半句作為一般命題為假，後半句與之矛盾，且「cost-optimal 與 ε-feasible 點」之有效域含糊。反例（只為否證該句，**不採用、不構成實作義務**）：在 R2 §9.2 的 cost-sublevel 域（R2 L324、L337）中，全部成本項非負，故 \(a_PP_B+a_EE_B\le C_{full}\)；配合 \(p^{ch}_t\le\min(P_B,\,0.8E_B/0.9)\)，可證 \(p^{ch}_t\le C_{full}/(a_P+1.125\,a_E)\)。在 (α,β)=(.10,4) cell 此值為 48,325.5 kW，小於 CL1 所稱最小值 \(\min(\bar P,0.8\bar E/0.9)=68{,}859.8\) kW。
- **核定後生效文字（取代 CL1 L304 全句；CL1 L297 主 contract 與 L299–303 公式不變）：**

> **R-02（Big-M validity）** 主 contract：\(M_{ch}:=\bar P\)；\(M_{dis,t}:=\min(\bar P,L_t)\) 或共同 \(M_{dis}:=\min(\bar P,L_{max})\)（R2 L358；CL1 L297）。可選 tightening（CL1 L299–303）的右側各項已證明有效，可取其最小值。
>
> 除此之外，**只有經獨立數學證明、對實際使用之完整候選可行域及所有相關 lexicographic 階段仍有效的上界，才可作為更緊的 Big-M。不能任意縮小；若無有效證明，沿用原已證明的 baseline Big-M。** 任何更緊上界之採用，須另行經研究者核定。
>
> 有效域依決策階段區分如下，不得將只對某一階段（尤其只對成本最適點）成立的界用於其他階段：
>
> | 階段 | 定義來源 | 有效域 | Big-M 適用 |
> |---|---|---|---|
> | RES stage 1（ENS-first, min r） | R2 L327 | positive domain，**未**預設 cost-first 容量界 | 解析求得 \(r_{min}=0\)，不建模、不求解，故不定義 Big-M。由 \(C\le C_{full}\) 推得之任何界（含 baseline \(\bar P\)）在此域**不保證有效**；若未來改為數值求解，須另行證明。 |
> | Cost-first stage 1（EOB+、ε-frontier stage 1、RES stage 2 = ε=0） | R2 L372–375、L388、L412 | \(F_+(\epsilon)\cap\{C\le C_{full}\}\cap\) R2 §8.2/§9 bounds | Baseline 與 CL1 L299–303 tightening 有效。新界須對**整個**此域有效。 |
> | Stage 2 cost band（min r） | R2 L413、L425 | \(F_+(\epsilon)\cap\{C\le\min(C_{full},U^{guard}_C+\delta_C)\}\) | 為 stage-1 域之子集，故對 stage-1 整域有效之界自動有效。**只對 stage-1 argmin 成立的界不得使用**，因 band 含非成本最適點。 |
> | Branch 0（EOB0、Global EOB 的 zero 分支） | R2 L96–100 | \(P_B=E_B=0\) | 無 battery power，Big-M 不適用。 |
> | Fixed-design replay | R2 L427–429 | 固定 P/E/CC/normal SOC；outage 無 mode binary（R2 L363） | 不適用。 |

### F-03 符號

- **原文位置：** CL1 L206–209、L222、L226–229、L233–235、L260；R2 L412、L419。
- **問題：** \(C^*\) 同時指 scheme C 最適值（\(\le\inf_\tau\)）與 R2 成本最適值（\(=C^*_{guard}\ge\inf_\tau\)）；\(L_C\) 同時指 C-relaxation 下界（\(\le\inf_\tau\)）與 guard MILP 下界（只 \(\le C^*_{guard}\)）。
- **核定後生效文字（記號對照；不改任何數學內容）：**

> **R-03（Notation）**
>
> | 新記號 | 意義 | 取代之原記號 |
> |---|---|---|
> | \(C^*_{guard}\) | 方案 A（live guard）在 \(X_g\) 上之最小值 | CL1 的 \(A^*\)、\(C^*_{guard}\)；R2 L419 的 \(C^*\) |
> | \(C^*_{closed}\) | 方案 C（closed τ）之最小值 | CL1 L222、L226 的 \(C^*\) |
> | \(C^*_{closed,0}\) | 方案 C0（closed strict）之最小值 | CL1 L222 的 \(C0^*\) |
> | \(C^*_{overlap}\) | 方案 B 之最小值 | CL1 的 \(B^*\) |
> | \(C^*_{strip}\) | 方案 E 之最小值 | CL1 的 \(E^*\) |
> | \(\inf_\tau,\ \inf_{strict}\) | unguarded 下確界（可能不可達） | 不變 |
> | \(L^{relax}\) | C-relaxation 的 proven lower bound | CL1 L233 的 \(L_C\) |
> | \(L^{guard}_C,\ U^{guard}_C\) | guard-restricted MILP 的 proven lower bound 與獨立重算可行上界 | R2 L412、L419 的 \(L_C,U_C\)；CL1 L233 的 \(U_A\) |
>
> 修正後之關係式：
> \[
> C^*_{overlap}\le C^*_{closed}\le\inf_\tau\le C^*_{strip}\le C^*_{guard},\qquad C^*_{closed,0}\le\inf_{strict};
> \]
> \[
> \inf_\tau\in[L^{relax},\,U^{guard}_C]\ \ (\text{未執行，僅選用});\qquad
> C(x_2)-C^*_{guard}\le(U^{guard}_C-L^{guard}_C)+\delta_C+\tau_C\ \ (\text{R2 L419}).
> \]
> \(L^{guard}_C\) **不得**作為 \(\inf_\tau\) 或 \(\inf_{strict}\) 的下界；R2 的約 2.001 NTD-2023/year 只相對於 \(C^*_{guard}\)。

### F-04 數學宣稱（T1／T4）

- **原文位置：** CL1 L141–145（「由此得到三選一」）；L155（T4）；L321（「B 與 C 不得作為計價 formulation」）。
- **問題：** 已證明的是二分性質，非三選一的窮盡分類；T4 漏「W>0」；未區分費率方向，May／October 被一併處理。
- **核定後生效文字（取代 CL1 L141–145 之「由此得到三選一」至第 3 點，及 L155 之 T4 敘述；L147–153「本命題的界線」保留）：**

> **R-04a（T1，二分性質，PROVEN）** 設有界、整數取值有限、僅含非嚴格線性約束之 MILP，其可行集在 \((d,\lambda)\) 上之投影為閉集 \(F\)。若 \(F\subseteq\Gamma\)（從不錯標），則存在 \(\delta>0\) 使 \((\tau,\tau+\delta)\) 不屬於 \(F\) 的 d-投影；等價地，若 \(F\) 的 d-投影包含某個 \((\tau,\tau+\varepsilon)\)，則 \(F\) 至少含一個非 canonical 標籤點。此結論只在 τ 右側確有物理可達之 d 時構成實際排除（EXP4 已構造真實資料點）。strict 規則以 0 取代 τ，結論相同。
>
> **主要設計選項（非窮盡）：** (A) 排除條帶（現行 guard，δ=g）；(B／C／C0) 重疊或閉合，不排除點但允許非 canonical 標籤；(E) 第三狀態保守計價。尚有其他組合（例如閾值平移、部分重疊加部分缺口）及 CL1 L147–151 所列非本類 MILP 技術，均未評估。
>
> **R-04b（費率方向與 W>0）** 令 \(r_e,r_l\) 為 earlier／later 季別超約費率，\(W\ge0\)。
> - 若 \(r_l\ge r_e\)（開側較貴）：逐點 \(f_{closed}(x)=f_\tau(x)\)，故 \(C^*_{closed}=\min f_\tau=\inf_\tau\)（可達）；閉合方案的非 canonical 可行點只會高估。
> - 若 \(r_l<r_e\)（開側較便宜）且邊界點 \(W>0\)：\(f_\tau\) 在 \(d=\tau\) 不是下半連續，\(\inf_\tau\) 可能不可達（T4）；閉合方案在 \(d=\tau\) 低估 \((r_e-r_l)W\)。
> - 若 \(W=0\)：標籤不影響成本，但方案 A 仍排除條帶內的點（EXP4，W=0）。
> - 方案 B 在兩個方向均可能低估（EXP3 S2，May：−3,227.00 NTD toy；S12，Oct）。
>
> **現行 calendar（S11 L21–22、L25–26、L44–45、L48–49；R2 L261）：**
>
> | Component | earlier（rate） | later（rate） | 方向 |
> |---|---|---|---|
> | 2025-05 sat_half／off | non_summer 32.05732664233577 | summer 43.031906934306576 | \(r_l>r_e\)：閉合方案成本精確 |
> | 2025-10 sat_half／off | summer 43.031906934306576 | non_summer 32.05732664233577 | \(r_l<r_e\)：T4 適用，閉合方案可能低估 |
>
> 因此 CL1 L321 應讀為：「B 不得作為計價 formulation；C 在 October 方向會低估，只能作為 relaxation／lower-bound 工具；本研究不採用 C 計價。」R-04 不改變保留方案 A 的建議，也不授權任何 formulation 變更。

### F-05 PV0 Pilot 前之處置

- **原文位置：** CL1 L188（EXP5b 列）、L192–198（解讀限制）、L318（§10.1 false-fail 列為 optional future）、L329（§11-3）。
- **問題：** 未記錄 EXP5b 的 d=0 吸引點；未沿用 REPORT 的 NOT VERIFIED 項「R2 Phase-1 實際的 Class-C 誘因」；false-fail 在 Phase-1 中為可預見事件。
- **核定後生效文字（新增於 CL1 §6.2 解讀限制之後；不修改 classifier）：**

> **R-05a（證據補記）** EXP5b（EXP5 artifact）兩個 α=0.50 真實資料月度 fixture 中，`off` component 皆精確落在 \(d=0\)（numerical tie）：2025-05 時 \(W=657.064\) kW，2025-10 時 \(W=0\)。故 Phase-1 類型模型會停在距條帶 \(10^{-4}\) kW 以內；EXP0 的「≥ 372.8 kW」源自 v7.3 模型，對 Phase-1 不具代表性。EXP3 S12（October 方向、BESS）顯示 A 的最優解被釘在 \(\tau+g\)，計價為 canonical，但 live classifier 回報 `NUMERICAL_BOUNDARY_UNRESOLVED`；S8b 顯示 \(W=0\) 時亦同（CORE L205–208 不以 W 區分）。**Phase-1 全年模型中 Class-C 的實際 d／W 行為：NOT VERIFIED。**
>
> **R-05b（Pilot entry rule，預設）** 在 PV0 correctness Pilot 正式授權前固定下列規則；未固定前不得授權 Pilot：
>
> **Class-C `NUMERICAL_BOUNDARY_UNRESOLVED`、`source_selection` 失敗或 `bounded_product` 失敗 → STOP / REPORT / PRESERVE DIAGNOSTICS。**
>
> - STOP：該 run 不得被宣稱為有效結果，不得進入 frontier、endpoint 或比較表。
> - REPORT：向研究者回報 component、類型與數值。
> - PRESERVE DIAGNOSTICS：保留原始 solver 輸出與每個 Class-C component 的 month、period、exact \(G_e,G_l\)、\(d\)、\(d-\tau\)、\(d-(\tau+g)\)、b 原值與四捨五入值、\(W_{exact}\)、乘積值、兩季費率、classifier status、FeasibilityTol、IntFeasTol、τ、g、solver status 與 gap、最大約束違反量。
> - 禁止：重新分類、放寬 classifier、調整容差、手動改標籤，或以不同設定重跑以「消除」該事件；以上均須另行授權。
> - 本輪不修改 classifier；CL1 §10.1 的 classifier 改善仍為未授權之選項。

### F-06 Strict tariff 與 τ-convention

- **原文位置：** CL1 L255（約 0.054 NTD/年條件界）；L262（§7.4-4）。
- **核定後生效文字（附加於 CL1 L262 之後）：**

> **R-06（τ／strict 帳單揭露）** 約 0.054 NTD-2023/year 只是兩側皆可逃離時 \(|\inf_\tau-\inf_{strict}|\) 的條件界，為**最適值之間**的差，NOT VERIFIED。對單一設計，若某 Class-C component 滿足 \(0<d\le\tau\) 且 \(W>0\)，其 τ-convention 帳單（earlier 費率）與 strict 帳單（later 費率）相差 \((r_e-r_l)W\)；現行費率差為 \(|r_e-r_l|=10.97458029197081\) NTD-2023/kW-month（S11），EXP3 S12 toy 中為 3,843.73 NTD。此差異**不受**上述條件式小誤差界限制。在 May 方向（\(r_e<r_l\)），A 在 τ-convention 下的吸引點即為 \(d=\tau\)。\(-\tau\le d\le0\) 時兩規則一致。
>
> 論文報告之帳單為 τ-convention 帳單（BRIDGE L21–30 之 accepted project convention），應如此揭露。**建議**（非本輪實作義務）：未來診斷記錄所有「\(0<d\le\tau\) 且 \(W>0\)」之 component，並列其 strict settlement。

### F-07 分支宣稱範圍

- **原文位置：** CL1 L259（§7.4-1 僅寫 \(F_+(\epsilon)\cap X_g\)）；R2 L381–384（Global EOB）。
- **核定後生效文字（取代 CL1 L259 之域記號）：**

> **R-07（Branch claim domains）**
> - Zero-BESS branch（EOB0）：最適性限於 \(F_0\cap X_g\)（\(F_0\) 見 R2 L96–100）。
> - Positive-BESS branch（EOB+、RES stage 2、ε-frontier、lexicographic endpoints）：限於 \(F_+(\epsilon)\cap X_g\)（R2 L370）。
> - Global EOB：在兩分支各自 guard-restricted 域上求得之端點，依 R2 L381–384 取 lexmin，即定義於 \((F_0\cap X_g)\cup(F_+(1)\cap X_g)\)。
> - \(X_g=X_g(\tau,g)\)，而 \(\tau=\tau(f)\)、\(g=g(f)\)（CL1 L94–98；CORE L110–160、L1238）。每次數值 run 的宣稱以該 run 實際記錄的 FeasibilityTol、τ、g（數值原樣）及實作版本身分為準（現行 core 已於 CORE L2704–2712 記錄前三者）。不同 τ／g 的 run 不得視為同一可行域。

### F-08～F-10 編輯性澄清（不擴張結論、不新增實作義務）

> **R-08（CL1 L214、L240）** 條件 (i) 讀為：「各方案除 Class-C 標籤約束外之物理域、bounds、floors、ε 相同。若成本上限以各方案自身計價施加，T2 各不等式方向仍成立。」CL1 L240 的 stage-2 子句只是條件 H 的前提敘述；本 Resolution **不**新增任何 stage-2 結論，T5 只就 stage-1 最適值成立。
>
> **R-09（CL1 L306）** 「都必須以同一個 \(M_{ch}\) 重算」讀為：「**可**以同一 \(M_{ch}\) 一致重算（建議）；若保留由 \(\bar P\) 推得之較鬆界，該界仍有效。必要條件只有兩項：每個推導界不得小於其在該 cell 域上的真實上確界，以及以實際採用之界檢查 \(U_l\ge\tau+g\)（CORE L1707）。」依賴鏈另含 \(a\)、\(D-CC\)、\(\Delta-0.1CC\)、\(h\) 範圍及 R2 §8.2 exact-MAX 之 \((U-L_i)\) 常數（R2 L242–257）。
>
> **R-10（CL1 L275）** 「應理解為 guard-restricted」讀為：「作為數學事實，solver 回報之 OPTIMAL 只對其所解之 formulation 可行域成立；本句不構成任何歷史 acceptance 之修訂（CL1 L39、L277–283）。」

---

## 4. Scope of precedence

| R2 原文 | 核定後之規範文字 | 效果 |
|---|---|---|
| §8.3 L271–273（source-binary 公式） | 與 CL1 L102–106 相同 | 不變 |
| §8.3 L275（「開區間(τ,τ+g)為 unresolved guard，Class C 不接受落入該區間的結果」） | CL1 §4.2 L108–114（\(X_g\) 為求解前之可行域限制）＋ §4.3 L116–123 | 補充並優先：條帶在求解前即被排除，post-solve 另行分類 |
| §8.3 L277–286（McCormick、帳單重算） | 不變 | — |
| §9.4 L358（主 contract） | 與 CL1 L297 相同 | 不變 |
| §9.4 L359–361（可選 tightening「≤」） | CL1 L299–303 ＋ **R-02** ＋ **R-09** | 取代 |
| §9.4 L363–366（outage bounds） | 不變 | — |
| §11 L417–421（\(C(x_2)-C^*\) 誤差界） | CL1 L260 ＋ **R-03** | 解釋為相對於 \(C^*_{guard}\)；不是 unrestricted 證書 |
| §11 其餘（L399–416、L422–429） | 不變 | — |

**其餘 R2 內容全部保持不變**，包括 §1–§7、§8.1–§8.2、§9.1–§9.3、§10 之定義、§12–§17：B1（branches 與 10 kW／20 kWh floors）、B2（analytical zero-ENS、九組 certificates）、B3（normal dispatch、Xu、fixed-PV outage recourse）、F-01 exact billing，以及 numerical targets 表。

**R2 §10 的處理：** CL1 §7.4（經 R-07 修正）只對 R2 §10 的端點加上最適性**宣稱範圍**限制，不改變其定義，因此不列為 R2 §10 的覆寫。是否要明文擴及 R2 §10，見 §8 的 D2。

**CL1 中不成為規範的部分：** §3（provenance 歷史）、§6（證據，非規格）、§10（未授權之可選工作）、§11（決策清單）、§12（作者自檢）。

**優先順序（僅於上述範圍）：** 本 Resolution 之 R-01～R-10 > CL1 §4.2、§7.4、§9 > R2 對應段落。

---

## 5. Remaining scientific limitations（核定後仍然存在）

1. **Guard-restricted mathematical optimality ≠ unrestricted physical-domain optimality**（CL1 L264）。不得宣稱 \(C^*_{guard}=\inf_\tau\) 或兩者差為 0（CL1 L261）。
2. Type-3 全年 certification：NOT VERIFIED。
3. H-PV 在最佳化後全年解上：NOT VERIFIED（只在 reference dispatch 上觀察到，EXP4b）。夜間 off-peak 最大時刻 PV=0，H-PV 不成立，但不代表 gap 大。T5 的約 0.0054 NTD/年只能以條件形式引用。
4. Phase-1 全年 Class-C d／W 行為：NOT VERIFIED（R-05a）。
5. τ-convention 與 strict（L2）在 \(0<d\le\tau\) 時偏離，個別帳單差可為 \(|r_e-r_l|W\)（R-06）。
6. L2 是研究案例 project rule，不是台電公布的完整跨季公式（BRIDGE L9–19；S12 status `OFFICIAL_CROSS_SEASON_AGGREGATION_NOT_EXPLICITLY_LOCATED`）。τ、g 為數值實作慣例，非官方規範（CL1 L262）。
7. 隔離實驗（1,316 次 optimize）未經獨立重跑；靜態審查只核對了 artifact 與 hash。EXP5b 是月度簡化模型；toy 數值不是 NTUST 年成本。
8. FeasibilityTol = 1e-9 時出現決定性的錯誤 INFEASIBLE（EXP6）；調緊容差不是安全修正。
9. R2 §16 L500 所列其餘 nonblocking limitations 維持不變。

---

## 6. Pilot entry rules（建議；PV0 Pilot 仍 NOT AUTHORIZED）

PV0 correctness Pilot 正式授權前，下列各項應已由研究者固定：

1. R-05b 的 STOP／REPORT／PRESERVE DIAGNOSTICS 規則。
2. 實作採用的 Big-M 版本：baseline，或 CL1 L299–303 tightening；任何其他界須依 R-02 另經核定。
3. 每次 run 保留 FeasibilityTol、IntFeasTol、τ、g、實作版本身分（R-07）。
4. 使用 live classifier 原規則；不得放寬（CL1 L318、R-05b）。
5. Pilot 的範圍、cell、時間上限與 STOP 條件，另以授權文件明定。本文件不指定。

---

## 7. Independence decision options（F-11）

**事實記錄：**

| 項目 | 值 |
|---|---|
| CL1 author | Claude Code（CL1 L18） |
| Reviewer（targeted static audit） | 另一個 Claude Code session（`180c3fec-52f7-4dc4-8216-e37c9b7a67f6`，Opus 5.5） |
| 本 Resolution 草稿 author | 與 reviewer **同一** session |
| Session-independent | YES（reviewer 對 CL1） |
| Cross-agent-independent | **NO** |
| Cross-agent audit 已完成 | **NO** |

**Protocol 原文判定：**
- PROT L322：「The agent that creates a candidate must not be the only agent that accepts it.」此句為強制規定，但對象是 **acceptance**，而且 Protocol 未定義不同 session 的同一工具是否為不同「agent」。
- PROT L324–327：「Preferred pattern: Claude Code implements → Codex audits; Codex implements → Claude Code audits.」原文用 **Preferred**，非強制。
- PROT L95：「A producing agent must never self-promote its own candidate to CLOSED / ACCEPTED.」本文件未作此事。
- CONST L545 把「對 Claude Code 修改做第二模型稽核」列為 Codex 的適用場景；CONST L606–610 要求指令說明「是否需要 cross-model independence」（L610）。兩者都是 routing 規則，沒有把 cross-model audit 列為一律強制。

**判定：** 無法從原文確認「cross-agent audit 為強制要求」，也無法確認「同一工具的另一 session 已滿足獨立性要求」→ **PENDING USER DECISION**。

另須注意：**R-01～R-10 的勘誤文字由 reviewer session 本身撰寫，尚未經任何獨立審查。**

**選項：**
- **I-1：** 接受現有 session-independent 審查為足夠，研究者直接就 R2 + CL1 + 本 Resolution 作決定。
- **I-2：** 先由 Codex（fresh session）對 CL1 與本 Resolution 做 cross-agent read-only audit，再作決定。
- **I-3：** 接受對 CL1 的現有審查，但只要求 Codex 審查本 Resolution 新增的 R-01～R-10 文字。
- **I-4：** 暫緩。

---

## 8. Explicit user acceptance decisions（皆待研究者決定；本文件不預設答案）

| ID | 決定事項 | 選項 |
|---|---|---|
| D1 | 是否接受 R2 + CL1 + 本 Resolution 作為 Phase-1 規格 | 接受／修改後接受／不接受／暫緩 |
| D2 | §4 的 precedence 範圍；是否明文擴及 R2 §10 | 照列／擴及 §10／其他 |
| D3 | R-02 Big-M 文字；實作採 baseline 或 CL1 tightening | baseline／tightening／暫不決定 |
| D4 | guard-restricted 宣稱範圍（CL1 §7.4，經 R-03、R-07 修正） | 接受／不接受 |
| D5 | R-04 數學宣稱修正 | 接受／修改 |
| D6 | R-05b Pilot entry rule | 接受預設／另定 |
| D7 | R-06 τ／strict 揭露方式 | 接受／另定 |
| D8 | 獨立性（§7） | I-1／I-2／I-3／I-4 |
| D9 | Type-3 certification、classifier 改善 | 均不授權（預設）／另行授權 |
| D10 | 以本 Resolution 方式接受，或改授權 R2 successor | Resolution／successor／暫緩 |
| D11 | 是否授權將 conversation-only 審查報告持久化 | 授權／不授權 |

若研究者核定，須另建一份獨立的 acceptance artifact（PROT L157）。本草案本身不會轉為 ACCEPTED。

---

## 9. Coding authorization status

| 項目 | 狀態 |
|---|---|
| Phase-1 methodology acceptance | `NOT_YET_AUTHORIZED`（待 D1） |
| Phase-1 formal implementation（Coding） | **`NOT_YET_AUTHORIZED`** |
| PV0 correctness Pilot | `NOT_YET_AUTHORIZED`（另需 §6 各項） |
| Type-3 certification | `NOT_YET_AUTHORIZED` |
| Accepted core／classifier 修改 | `NOT_YET_AUTHORIZED` |
| Production／re-freeze | `NOT_YET_AUTHORIZED` |

審查結論為：在 guard-restricted scope 下，Class-C 無 material mathematical pre-coding blocker；Type-3 不是 Coding 前置條件。**這只是 readiness 判斷，不是授權。** Coding 授權須在 D1、D8 完成後另行明示。

---

## 10. Governance integrity statement

- 本輪唯一新增檔案：`C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md`（repository 外）。
- Existing files modified = 0；R2、CL1 原始 SHA 保持（§1.1）；Repository modified = 0；Git mutations = 0；Model builds = 0；Solver calls = 0；Production runs = 0；Self-acceptance = 0；Classifier／core 修改 = 0。
- 本輪只做 SHA-256 核對、原始碼與 CSV 唯讀檢視及算術。
- 本文件作者即 reviewer session，故本文件的新文字未經獨立審查（§7）。
- 本檔不嵌入自身 SHA，以避免循環；交付回覆另行提供 bytes 與 SHA-256。

**PROPOSED ACCEPTANCE RESOLUTION R1 — DRAFT / NOT ACCEPTED / PENDING USER DECISION**

**完成本文件即停止。NO CODING / NO SOLVER / NO MODEL BUILD / NO GIT MUTATION / NO SELF-ACCEPTANCE / NO R2 OR CL1 MODIFICATION / NO R3。**
