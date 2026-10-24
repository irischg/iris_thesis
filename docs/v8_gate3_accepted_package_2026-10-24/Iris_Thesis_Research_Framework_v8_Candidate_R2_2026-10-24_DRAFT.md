# 研究框架 v8 — Candidate R2（2026-10-24）

## 校園 PV–BESS 服務連續性之 Cost–ENS／ε-constraint 年度規劃框架

> **FRAMEWORK V8 — CANDIDATE R2 / NOT ACCEPTED / NOT ACTIVATED / PENDING TARGETED INDEPENDENT AUDIT**
>
> 本文件是 Gate 3 的 Framework v8 **候選文件 R2**，為 Candidate R1（`d35cd196…6d89`；獨立 Gate 3 稽核 STOP）之 additive successor；R1 保持不可變。它**不是** current methodology authority，**不是** accepted Framework，也不授權 Coding、Pilot、Solver、Production、Git 或 Activation。在 Gate 3 獨立審查 PASS、研究者正式接受、並另行明示 Activation 之前，**Framework v7.4 與 Registry v7.4 仍是唯一的 current accepted methodology／evidence authority**（ART2 §7.5.4-D、§7.5.5）。任何文件、程式或報告不得在 Activation 前將本文件或 Phase-1／v8 規格稱為 current thesis methodology authority，亦不得稱 v7.4 已被取代。
>
> **R2 修正範圍：** 只處理 Codex 獨立 Gate 3 稽核（AUD3，§1）所列之限定缺陷與研究者 2026-10-24 Gate 3 範圍決定：費率方向宣稱條件（§7.1 第 5 點、§7.2）、v7.4 逐條承接（§0.4、§8.3）、驗證義務分層（§6.9）、研究範圍（§2.5）、Registry delta（§9.2）、Activation 契約（§8.5）、14 項 OPEN 之處置（§11.2）。核心數學（§3、§5、§6.1–§6.6 之方程式、參數與數值）與 R1 逐 byte 相同、未變更；完整變更清單見 §14。

---

## 0. 文件性質、權源與讀法

### 0.1 權源

1. **唯一新方法依據：** 2026-10-24 Gate 2 Methodology Specification Acceptance Decision Record（下稱 REC）所接受的 v8 方法規格：SPEC、CL1、RES、ART2，連同 Decision Draft（DD）第 0 層內容（§C.3 [DC-NEW] 列、§D.4、§D.6 範圍）。
2. **繼承依據：** Framework v7.4（FW74）依 REC D12(a)、ART2 §7.5.4-C 與 DD §C.3 之處置前瞻承接；v7.4 歷史 CLOSED／ACCEPTED 效力完整保留（ART2 §7.5.4-E）。
3. **治理依據：** Version／Provenance Management Protocol v1（PROT）；Research Governance Constitution（CONST）。
4. **Gate 3 稽核證據：** AUD3（§1）——R1 缺陷之證據，不是接受權源；R2 只修正其所列之限定缺陷。
5. **研究者 Gate 3 範圍決定**（2026-10-24，研究者於本 session 之書面指示；conversation-only，無獨立檔案 bytes）：只授權本 Candidate 記錄範圍之納入／排除／延後（§2.5），**不是** Gate 3 接受，也不是 Gate 2 數學修訂；於研究者 Gate 3 接受紀錄中確認後才生效（§8.5）。

### 0.2 與 Gate 2 規格的 precedence

- 本文件是 Gate 2 規格的**整合與組織**，不是其修訂。**凡本文件與 Gate 2 package 原始 bytes 不一致之處（含轉錄錯誤），一律以 Gate 2 package 依 ART2 §7.2 與 DD §B.2 之 precedence chain 為準**，並應視為本 Candidate 的缺陷，以 additive successor 修正。
- 本文件**不新增、不修改、不擴張**任何 Gate 2 方程式、參數、假設、數值 target 或宣稱邊界。

### 0.3 標記規則

| 標記 | 意義 |
|---|---|
| `[G2]` | 轉錄或摘要自 Gate 2 已接受 package；後附來源位置 |
| `[G2-D]` | Gate 2 研究者決定（REC §4） |
| `[V74-CONT]` | v7.4 內容，依 Gate 2 處置（DD §C.3／ART2 §7.5.4-C）對 v8 繼續適用 |
| `[V74-ONLY]` | v7.4 內容，依 Gate 2 處置只在 v7.4 有效、v8 不繼承 |
| `[FW8-PROPOSED]` | 本 Candidate 提出、Gate 2 未明文決定的**非數學**組織或承接安排；須經 Gate 3 審查與研究者確認 |
| `[OPEN]` | R1 中之未決事項；R2 已逐項處置（§11.2）；`[OPEN-xx]` 字樣在 R2 只作 R1 交叉引用 |
| `[G3-SCOPE]` | 研究者 2026-10-24 Gate 3 範圍決定（納入／排除／延後；§2.5）；不改任何 Gate 2 方程式或 contract；Gate 3 接受前不生效 |

R2 起，v7.4 承接分類採 AUD3 §3 之五類代碼：① 承接＝`[V74-CONT]`；② 由 Gate 2 明示取代＝`[V74-ONLY]`（取代）；③ 歷史限定＝`[V74-ONLY]`（v8 中無適用對象，或屬 v7.4 結果／計數）；④ 本 Candidate 之 v8 安排＝`[FW8-PROPOSED]`；⑤ 研究者範圍決定延後＝`[G3-SCOPE]`。

### 0.4 v7.4 非 §0.1 內容的承接規則 `[FW8-PROPOSED]`（R2 修正；回應 AUD3 §3、R1 OPEN-14）

Gate 2 只對 FW74 §0.1（L68–90）、§7.3–§7.5、§7.7、§7.10、§7.11 作明示處置（DD §C.3）。R1 以「是否以被取代項目為前提」對整節分類；AUD3 判定其中 §7.2、§18.4 之整節分類過廣，且承接不得以「未衝突就繼承」或「未列就撤銷」自動決定。R2 改採下列規則：

1. **逐條（clause-level）分類：** 同一 FW74 章節內，不同句子、公式或檢查項可分屬不同類；分類單位是條款，不是整節。
2. 分類代碼採 §0.3 之 ①～⑤。
3. 只有 Gate 2 accepted package 明示取代者可標 ②。共同定義（例如 valid-start 集合、residual-load 運算、power balance、technical SOC window、成本分項）即使原先出現在 reserve-based 章節中，只要 Gate 2 未取代且與 SPEC 一致，即標 ①。
4. 驗證義務不因所屬章節被部分取代而整體取消；逐項處置見 §6.9。
5. 本分類（§8.3、§6.9）為 Gate 3 提案，須經 targeted independent audit 與研究者接受；不修改 FW74 任何 byte。

逐條分類見 §8.3；驗證義務見 §6.9。

---

## 1. Source manifest（2026-10-24 本輪以唯讀 SHA-256 核對；全部 MATCH）

| ID | 路徑 | SHA-256 | 角色 |
|---|---|---|---|
| REC | `C:/Users/Iris C/Downloads/Iris_Phase1_Methodology_Specification_Acceptance_Decision_Record_2026-10-24.md` | `459c3a861ae890fd90a868bac9f269d9f1316eba25cf054796597d071b9d795b` | Gate 2 接受紀錄 |
| DD | `C:/Users/Iris C/Downloads/Iris_Phase1_Methodology_Specification_Acceptance_Decision_Candidate_R1_2026-10-24_DRAFT.md` | `ac0728d9d8eb33efdc92b2866bd1f87c709710e53c6e75b7b030313f100c04b7` | Gate 2 決策文件（第 0 層） |
| SPEC | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` | 數學規格本體 |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` | Class-C guard 澄清 |
| RES | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md` | `3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5` | R-01～R-10 勘誤 |
| ART2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R2_Candidate_2026-10-24_DRAFT.md` | `2386d47b96690ac3a8c81673b1c4750e85bce93ef837ce47a75e850cb49f8268` | Acceptance artifact |
| FW74 | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` | current accepted methodology（至 Activation） |
| FW74-C | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` | FW74 接受紀錄 |
| REG74 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` | current accepted evidence authority |
| REG74-C | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` | REG74 接受紀錄 |
| PROT | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` | 治理 protocol |
| R1 | `C:/Users/Iris C/Downloads/Iris_Thesis_Research_Framework_v8_Candidate_R1_2026-10-24_DRAFT.md` | `d35cd196b5b758c31db06908d400d8b13575e08e27b28898c382f1c651006d89` | 前一 Candidate（AUD3 = STOP；不可變；本檔之建立基礎） |
| AUD3 | Codex rollout `C:/Users/Iris C/.codex/sessions/2026/10/24/rollout-2026-10-24T15-18-41-01a16cc6-a809-7ce1-9129-5b35de1a5630.jsonl`（948,092 bytes；SHA `68c2d2fe6228d3fabc41def95f89b36368ab13259575dd4c1af80026acb8d155`）之 final answer：rollout 第 138 行，`2026-10-24T07:29:53.229Z`，23,234 bytes（UTF-8） | `8cdae46384efaec96d28aec239e2b4aaa3342259367e21f7e1c643800c319e05`（final answer） | Framework v8 Candidate R1 獨立 Gate 3 稽核報告；verdict 原文 `FRAMEWORK V8 CANDIDATE R1 — STOP` |
| REGD | `C:/Users/Iris C/Downloads/Iris_Thesis_Literature_Evidence_Registry_v8_Delta_Candidate_R1_2026-10-24_DRAFT.md` | `99fe6eb5d2c47784d978012368f254b0094abdd8613cb1547a0def29f310e93c` | 本 R2 對應之 Registry v8 Minimal Additive Delta Candidate R1（同為 NOT ACCEPTED） |

Repository 路徑相對於 `C:/Users/Iris C/OneDrive/Desktop/iris_thesis`；HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；`git status --porcelain` 雜湊 `e2c74e093887272558d88751adb7668fe0b5023c1fa3959793b983341c277f1c`（16 項）。Gate 2 package 所依賴之 data／tariff／cost artifacts（SPEC S07–S16）的身分以 SPEC §2 manifest 為準，本文件不重列。

R2 輪（2026-10-24）重新以唯讀 SHA-256 核對上表 R1 以外之全部來源及 R1 本身：全部 MATCH；HEAD 與 `git status --porcelain` 雜湊（16 項）與 R1 輪相同。

**AUD3 custody：** 研究者於本 session（2026-10-24）單次授權，以 `python -I` 解析上列 rollout，只取 `final_answer`、`session_meta`、`turn_context`：session `01a16cc6-a809-7ce1-9129-5b35de1a5630`；originator `codex_vscode`；cli `0.162.0-alpha.17.2`；`turn_context` 記錄 model `gpt-6-astra`、effort `high`（實際後端未驗證）。final answer 與 `event_msg/task_complete.last_agent_message` 完全相同。擷取副本位於本 session scratchpad（`%LOCALAPPDATA%\Temp`，**非 durable**），可依同法由 transcript 決定性重現。AUD3 引用之 R1 行號已以 R1 bytes 核對：L415、L471、L484、L524 之內容與 AUD3 所述相符；L409 處並無「同向」字樣，最接近之相關條文為 §7.1 第 5 點（L409；R1 該點省略了 ART2 §8-5 之方向條件與 October 低估理由），R2 一併修正 L409 與 L415。

---

## 2. 研究定位與研究問題

### 2.1 核心研究問題 `[G2]`（SPEC L83；ART2 §7.6）

在 NTUST 既有 PV0 固定（額外 PV 容量為零）之下，對 BESS AC/PCS power \(P_B\) [kW]、battery-side nameplate energy \(E_B\) [kWh] 與單一年度 regular contract capacity \(CC\) [kW] 進行 annual **Cost–ENS** planning：在固定服務定義 \((\alpha,\beta)\) 下，將部分 ENS 與年度成本之交換納入內生決策，以 aggregate ENS 上限 \(r\le\epsilon\) 取代 v7.4 的 hard all-start reserve／adequacy 服務要求（SPEC L152、§14-1）。

### 2.2 科學理由 `[G2]`（ART2 §7.6 建議科學理由文字，逐字）

> Framework v7.4 以所有合法停電起點均須滿足指定服務比例與時長的要求，研究其設備容量及年度成本。依 Root-Cause 審查（operator-extracted Codex final answer；本輪未由 Full81 primary outputs 重算；原上傳副本 bytes 未驗證）之轉述，81 案年度總成本與韌性增額成本均有顯著變動，並非扁平；最壞情境 adequacy 要求強烈影響 BESS sizing 與成本，而正常營運成本合計及契約容量的跨案例變動較有限，其中約 14,298 NTD／年指正常營運成本合計的全距，不是每個分項的全距。擬議 v8 將研究問題擴展為固定服務定義下的內生部分 ENS–成本權衡；此轉向不表示 v7.4 失效，也不證明 reserve floor 是唯一原因，不保證 v8 出現 Pareto knee 或成本降低，亦不構成 unrestricted optimality 宣稱（§8）。新規格的 \(r_{ENS}\) 為 deterministic aggregate service metric，並非 EENS 或可靠度機率；新舊比較亦不能將所有差異歸因於 ENS 單一變更。

（引文內「§8」指 ART2 §8，即本文件 §7.1。）證據等級：v7.4 formulation 差異 = PROVEN（formulation）；RCA 數值 = OBSERVED-relay（REC S5(ii)）；v8 曲面形狀 = CONDITIONAL，待未來授權實驗；constant reserve floor 為唯一成因、特定節省額、經濟優勢、Pareto knee = NOT VERIFIED（ART2 §7.6 表）。

### 2.3 子問題 `[FW8-PROPOSED]`（只重述 Gate 2 已定義的端點與分析；不新增方法）

- **SQ1（端點）：** 各 \((\alpha,\beta)\) cell 的 Global EOB、EOB+ 與 RES 端點的設計 \((P_B,E_B,CC)\)、年度成本與 \(r\) 為何（§3、§5.12）？
- **SQ2（交換）：** positive branch 的 ε-frontier 在 \(r\in[0,1]\) 上的 cost premium \(C_+^*(\epsilon)-C_{global}^*\) 如何變化（§6.4）？不預設 knee 存在。
- **SQ3（假設敏感度）：** 預先登錄的 floor scenarios A／B／C 對 (0.10, 4) cell 的 EOB+ 與 high-ENS frontier 有何影響（§6.5）？

子問題的最終措辭、論文題目與章節結構：編輯性後續（R1 OPEN-08；§11.2），須符合 §2.4–§2.5 之範圍與宣稱邊界。

### 2.4 可主張與不可主張

可主張（條件式）：在 guard-restricted 候選可行域上、於指定數值 tolerance 下，求得之 endpoint 與 frontier（§7.1）。

不可主張 `[G2]`＋`[V74-CONT]`：
- 模型保證任何未來真實停電一定成功（FW74 §1.2；SPEC L90、L184）。
- \(r\) 或 structured-start event-coverage proportion 是 EENS、可靠度機率或年度停電機率（SPEC L90、L184；ART2 §7.6）。
- \(\alpha L_t\) 是完整 critical-load inventory（SPEC L89；FW74 §3.2）。
- 沒有場地上限的結果就是校園應實際安裝的容量（FW74 §3.1、§0.1 L88）。
- unrestricted global optimality；v8 必然成本較低、具有 knee 或經濟優勢；v7.4 失敗、無效或已撤銷（ART2 §7.5.4-E、§7.6、§8）。
- 10 kW PCS 對全校 PV 具 GFM 能力；floors 是 NTUST 工程門檻（SPEC L108、L111、L445）。
- 提出全新的 resilience theory 或 optimization algorithm（FW74 §1.2）。

### 2.5 v8 研究範圍：納入、排除與延後 `[G3-SCOPE]`（研究者 2026-10-24 決定；回應 AUD3 §7-2）

本節記錄研究者之範圍決定。它不修改任何 Gate 2 方程式、研究域、endpoint、source-binary guard、Big-M、數值 tolerance／certificate、tariff 規則或宣稱邊界，因此**不是** Gate 2 methodology amendment；正式效力以 Gate 3 接受為準（§8.5）。

| 類別 | 項目 | 依據／限制 |
|---|---|---|
| **納入**（本次 v8 接受範圍） | PV0／zero-combustion Cost–ENS 規劃，以 ε-constraint 與 lexicographic 求解：§3、§5、§6.1–§6.8、§7 之全部 Gate 2 內容——\(\alpha=\{0.10,0.25,0.50\}\)、\(\beta=\{4,8,12\}\) h 九 cells；最低 ε-grid；EOB0、EOB+、Global EOB、RES；lexicographic stages；source-binary guards；Big-M baseline 與數值 contracts；fixed-design／fixed-normal-SOC replay；normal operation；outage recourse；exact billing 與 Class-C；成本與 degradation | Gate 2 accepted package（REC D1–D7、D9） |
| 納入 | 已登錄之 floor sensitivity A／B／C（§6.5） | SPEC §13 preregistration；執行另行授權 |
| 納入 | §6.9-A 之強制驗證義務（含 ex-post rainflow validation）與 §6.9-B 之承接 sensitivity 角色 | FW74 §0.1 B1、§4.4.3-E、§16.1、§18；SPEC §6、§8、§11；ART2 §4.2 |
| 不帶回 | v7.4 reserve floor \(e_t\ge0.10E_B+R(\alpha,\beta)\)、power adequacy 下限或 all-start zero-shortfall 要求，不得作為 v8 之隱含限制 | SPEC L152；§5.5 |
| **排除**（本次研究域之外） | \(\beta=24\) h | 不在九-cell 研究域內；加入屬另行接受之 domain extension，須另補適用 certificate 與比較範圍（AUD3 §4 OPEN-09） |
| **延後**（不在本次 v8 接受範圍；未定義、未完成） | 新的 v8 Layer B 方法 | 不承接 FW74 §9–§10 為 v8 方法；fixed-normal-SOC replay **不是** Layer B；日後納入須另定方法、獨立審查並接受 |
| 延後 | DG extension | Phase-1 模型不含 DG（SPEC L92、§14-6）；FW74 §0.1 L89–90 之 DG 邊界承接（§8.3）；舊 DG reserve／\(R^{DG}\) sizing 不帶入；將 DG 加入主 objective 或 outage recourse 即屬 Gate 2 變更，須另案 amendment |
| 延後 | 新的 scientific knee 定義、marginal-cost 決策規則 | 不新增；§6.7 最低輸出欄位保留；之後的研究分析可描述結果形狀，但不得預設 knee（ART2 §7.6；DD §K） |
| 延後 | 未被既有 accepted 方法要求之額外 sensitivity／benchmark | §6.9-C；不得藉「sensitivity」標籤取消 §6.9-A 之強制驗證 |
| 延後至實作規劃 | Pilot 子集合、額外 ε 點、執行順序、runtime 上限、排程與資源配置 | 須遵守已接受之最低 contract；**不**授權減少最低 ε-grid 或放寬數值 certificate（SPEC §10–§11；ART2 §9-5） |

本範圍決定**不表示**任何延後項目已完成，亦不表示 Coding、Pilot、Git 或 Activation 已發生。

---

## 3. 方法角色 `[G2]`（SPEC §10、§11 L427–429；RES R-07；ART2 §8-1）

| 角色 | 定義 | 宣稱域 |
|---|---|---|
| **EOB0**（Branch 0） | Branch 0 上 \(\min C\)；\(r=1\) | \(F_0\cap X_g\) |
| **EOB+** | \(r_{EOB+}=r_+^*(1)\)：\(\epsilon=1\) 的 cost-first、ENS-second 端點 | \(F_+(1)\cap X_g\) |
| **Global EOB** | \(\operatorname{lexmin}\{(C_0^*,1),(C_+^*(1),r_{EOB+})\}\)；**EOB+ 不能取代 global baseline** | \((F_0\cap X_g)\cup(F_+(1)\cap X_g)\) |
| **RES** | 解析 stage 1 \(r_{min}=0\)；stage 2 \(\min C\mid r=0\)，即 positive \(\epsilon=0\)；**沒有 solver 得到的 minimum-cost RES 數值** | \(F_+(0)\cap X_g\) |
| **ε-frontier** | \(\min C\) s.t. \(r\le\epsilon\)，再在 cost-optimal set 上 \(\min r\)；Branch 0 僅 \(\epsilon\ge1\) 可行；主要 frontier 報 positive branch，global zero 點另外標示 | \(F_+(\epsilon)\cap X_g\) |
| **Lexicographic** | cost-first、ENS-second；第二階段**保留完整決策空間**，不固定第一階段 P/E/CC/normal SOC；warm start 可用但不等於 fixing | 同上 |
| **Fixed-design／fixed-normal-SOC min-ENS replay** | 固定 P/E、CC 及整條 normal SOC，每事件以 §5.6 相同 outage 可行域 \(\min ENS_s\)；**不是** lexicographic tie-break，**不是** Layer B | 固定設計 |

---

## 4. 研究邊界、時間、輸入與單位

### 4.1 時間與輸入 `[G2]`（SPEC §3）

- \(T=8760\)，\(\Delta t=1\) h；正常 interval \(t=0,\ldots,T-1\)，state \(t=0,\ldots,T\)。
- 唯一 planning series：S13（`data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`，SHA `3ac8dda4…c428`）的 `baseline_load_kw`＝\(L_t\)、`pv_available_kw`＝\(V_t\)、`timestamp_start`／`timestamp`、`billing_usage_period_id`、`season`、`tou_period`。κ calibration 維持 observed evidence route，不混換為 reconstructed planning PV（亦即 FW74 §4.1.1-R、§4.3.1-K 繼續適用 `[V74-CONT]`）。
- 已核實：2024-11-01 00:00 至 2025-10-31 23:00；8760 個不重複連續小時；L/V 無缺值或負值；\(L_{min}=42\) kW，\(L_{max}=5179\) kW；annual load = 21293763 kWh；annual PV = 427105.4351329623 kWh；全部 \(V_t\le L_t\)。

### 4.2 單位與成本基礎 `[G2]`（SPEC L92）

所有功率（含 shed／curtailment）為 AC kW；SOC／segment energy 為 battery-side kWh；ENS／\(D_s\) 為 AC kWh。\(\eta_c=\eta_d=0.90\) 固定且各用一次。成本為 constant NTD-2023/year。無 paid export、T-REC 收益、DG、PV0 sunk CAPEX、額外 subsidy cashflow 或 outage operating／cycling cost。

### 4.3 \(\alpha\)、\(\beta\) 的語義

- \(\alpha\)：service-load proxy，不是已盤點 critical equipment inventory（SPEC L89）`[G2]`；\(\alpha\)、\(\beta\) 為 decision-maker-specified planning targets，不是法定標準（FW74 §0.1 L69）`[V74-CONT]`；FW74 §3.2 的解讀與限制 `[V74-CONT]`。
- \(\beta\)：\(n_\beta=\beta/\Delta t\)，\(S_\beta=\{0,\ldots,T-n_\beta\}\)；事件不跨年、不 wrap；起點數依序 8757／8753／8749（SPEC L90）`[G2]`。每個事件有其完整窗口 load／PV foresight；這是 conditional achievable service capability，不是真實操作成功率或年度停電機率。
- FW74 §3.3「\(\beta=8\) h 表示此設計按 8 小時停電需求 sizing」之 sizing 讀法，以 L70 被取代之 worst-case reserve 服務要求為前提 → 提議 v7.4-only（依賴）`[FW8-PROPOSED]`；FW74 §3.3「非正確解讀」（\(\beta\) 不是停電時長預測或機率）`[V74-CONT]`。

### 4.4 系統邊界

FW74 §3.1 的納入／主線排除清單 `[V74-CONT]`，與 SPEC L83、L92 一致：PV capacity sizing 主線排除（SPEC §14-8：新增 PV 離散情境與 selective continuous joint-sizing 屬後續 gate）；grid export 排除；網路潮流、critical-load inventory、existing emergency DG、outage 機率、Monte Carlo、forced outage、場址與 calendar aging／replacement schedule 均排除。\(E_B^*\)、\(P_B^*\) 解讀為 modeled planning requirements，不是 final recommended installation（FW74 §3.1、§0.1 L88）。

---

## 5. 數學模型 `[G2]`（逐項轉錄；與原 bytes 不一致時以原 bytes 為準，§0.2）

### 5.1 記號

- \(P_B\)、\(E_B\)、\(CC\)：設計變數（SPEC L83）。與 FW74 記號對照：\(P_B\leftrightarrow P^B\)、\(E_B\leftrightarrow E^N\)（battery-side nameplate；FW74 §5.1）`[FW8-PROPOSED：記號對照，非語義變更]`。
- \(x\)：P/E、CC、全部 normal dispatch／binaries／SOC／segment states、outage recourse、exact billing auxiliaries（SPEC L370）。
- \(F_+(\epsilon)\)：同一 candidate positive domain 加 \(r\le\epsilon\)；\(F_0\)：Branch 0 domain；\(X_g\)：guard-restricted domain（§5.10）。

### 5.2 B1：Branch 0／Branch + 與 floors（SPEC §4）

**Branch 0：** \(P_B=E_B=0\)；全部 battery powers、normal／outage SOC、Xu segment states 為零。正常 PV 可自用／棄光，CC 仍最佳化。依本研究 branch assumption，沒有 island-forming source，停電 PV 不服務負載：\(shed_{s\tau}=Q_{s\tau}\)，\(ENS_s=D_s\)，\(r_{ENS}=1\)。（ART2 §13 N-6：Branch 0「Big-M 不適用」指 \(M_{ch},M_{dis}\)；billing 常數仍需 \(\bar p^{grid}_t=L_t\)。）

**Branch +：**
\[
10\le P_B\le\bar P,\qquad 20\le E_B\le\bar E .
\]
\(P_{lo}=10\) kW、\(E_{lo}=20\) kWh：user-authorized proposed mainline research **ASSUMPTION**，非 accepted engineering threshold，不是 Q1 規定、NTUST GFM 認證、optimal sizing 或 full-service adequacy。P/E 兩個 sizing variables 獨立；無固定 ratio、1C、1–8 h 或 installation binary。Normal no export、strict hourly charge/discharge exclusivity；outage fixed PV-first，不加 hourly outage mode binary。Positive branch 採 conditional island-ready BESS assumption。\(CC_{min}=0\) 是繼承模型域，不是台電法律最低契約容量聲明。

### 5.3 B3：Normal annual dispatch 與 Big-M（SPEC §5；§9.4；RES R-02；REC D3）

\[
p_t^{grid}+p_t^{dis}+v_t^{use}=L_t+p_t^{ch},\quad 0\le v_t^{use}\le V_t,\quad v_t^{curt}=V_t-v_t^{use},\quad p_t^{grid}\ge0,
\]
\[
0\le p_t^{ch}\le P_B,\quad 0\le p_t^{dis}\le P_B,\quad u_t\in\{0,1\},\qquad p_t^{ch}\le M_{ch}u_t,\quad p_t^{dis}\le M_{dis,t}(1-u_t).
\]
\(u_t=1\) 允許 charging，\(u_t=0\) 允許 discharging；idle 可屬任一 mode。不使用 \(u_tP_B\) 的連續乘積。

**Big-M（D3 = baseline）：** \(M_{ch}:=\bar P\)；\(M_{dis,t}:=\min(\bar P,L_t)\) 或共同 \(M_{dis}:=\min(\bar P,L_{max})=5179\) kW。每 cell 採自己的 certificate，不能借另一 cell 較小 \(C_{full}\)（SPEC L357）。CL1 L299–303 tightening 已證明有效但**不選用**；日後改用須研究者另行選定。其他更緊的界只有經獨立數學證明、對實際使用之完整候選可行域及所有相關 lexicographic 階段仍有效者才可採用，並須另經研究者核定（RES R-02）。有效域依階段區分（RES R-02 表）：

| 階段 | 有效域 | Big-M |
|---|---|---|
| RES stage 1（min r） | positive domain，未預設 cost-first 容量界 | 解析 \(r_{min}=0\)，不建模不求解，不定義 Big-M；由 \(C\le C_{full}\) 推得之界在此域不保證有效 |
| Cost-first stage 1（EOB+、ε stage 1、RES stage 2） | \(F_+(\epsilon)\cap\{C\le C_{full}\}\cap\) SPEC §8.2／§9 bounds | baseline 有效；新界須對整個此域有效 |
| Stage 2 cost band（min r） | \(F_+(\epsilon)\cap\{C\le\min(C_{full},U^{guard}_C+\delta_C)\}\) | 對 stage-1 整域有效之界自動有效；**只對 stage-1 argmin 成立的界不得使用** |
| Branch 0 | \(P_B=E_B=0\) | 不適用 |
| Fixed-design replay | 固定 P/E/CC/normal SOC | 不適用（outage 無 mode binary） |

RES R-09：若採 tightened \(M_{ch}\)，依賴界「可」以同一 \(M_{ch}\) 一致重算；必要條件為每個推導界不小於其在該 cell 域上的真實上確界，並以實際採用之界檢查 \(U_l\ge\tau+g\)。

### 5.4 SOC 動態與 Xu-derived degradation states（SPEC §5）

\[
e^N_{t+1}=e^N_t+\eta_cp_t^{ch}\Delta t-p_t^{dis}\Delta t/\eta_d,\qquad 0.10E_B\le e^N_t\le0.90E_B,\qquad e^N_T=e^N_0 .
\]
\(e^N_0\) 自由但受相同 bounds／cyclic 約束；不另固定 50% 初始 SOC。

Xu-derived intertemporal PWL：\(k=1,2,3\)，\(b=(0,0.30,0.60,0.80)\)，\(w=(0.30,0.30,0.20)\)。
\[
e^N_t=0.10E_B+\sum_ke_{t,k},\quad 0\le e_{t,k}\le w_kE_B,\quad p_t^{ch}=\sum_kp_{t,k}^{ch},\quad p_t^{dis}=\sum_kp_{t,k}^{dis},\quad p_{t,k}^{ch},p_{t,k}^{dis}\ge0,
\]
\[
e_{t+1,k}=e_{t,k}+0.90p_{t,k}^{ch}\Delta t-p_{t,k}^{dis}\Delta t/0.90,\qquad e_{T,k}=e_{0,k},
\]
\[
C_{deg}=\sum_{t,k}\lambda_kp_{t,k}^{dis}\Delta t/0.90 .
\]
Aggregate SOC equation 由 segment equations 加總成立，可作 derived identity。繼承 accepted segment semantics，不做 hourly reset、不另增 segment ordering binaries，不重複計效率／replacement。\(\lambda\) 的單位是 NTD-2023 per battery-side discharged kWh。

### 5.5 SOC／reserve policy（SPEC L131、L152；DD §C.3 L72 列）

- **沒有 reserve floor。** 不得帶回舊 Layer A 的 \(e_t\ge0.10E_B+R(\alpha,\beta)\) 或 \(P_B\ge\) 舊 power adequacy；服務要求由 ENS cap 決定；只有 B2 reference construction 用充分服務容量，不把該容量當全部設計的 lower bound（SPEC L152）。
- FW74 §0.1 L72「normal-operation reserve 必須位於 technical SOCmin 之上」之 reserve 要求，在 v8 沒有適用對象，**不帶入**任何 reserve `[V74-ONLY]`；\(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)、\(E^U=0.8E^N\) 的技術界限與 usable-energy 意義繼續適用（normal：SPEC L131；outage：SPEC L176）`[V74-CONT]`。
- Normal 與 outage 之聯結見 §5.6 的 handoff \(e^O_{s,0}=e^N_s\)。

### 5.6 Fixed-PV outage recourse 與 normal-operation handoff（SPEC §6）

僅 Branch +，\(s\in S_\beta\)，\(\tau=0,\ldots,n_\beta-1\)：
\[
Q_{s\tau}=\alpha L_{s+\tau},\quad V^O_{s\tau}=V_{s+\tau},\quad S_{s\tau}=\max(V^O_{s\tau}-Q_{s\tau},0),\quad R_{s\tau}=\max(Q_{s\tau}-V^O_{s\tau},0).
\]
\(Q,V^O,S,R\) 是固定參數，可在資料準備時純算術求得，不是 endogenous MAX。PV-first 先供 \(\min(Q,V^O)\)：
\[
0\le c_{s\tau}\le S_{s\tau},\quad c_{s\tau}\le P_B,\qquad 0\le d_{s\tau}\le R_{s\tau},\quad d_{s\tau}\le P_B,
\]
\[
shed_{s\tau}=R_{s\tau}-d_{s\tau},\qquad curt^O_{s\tau}=S_{s\tau}-c_{s\tau},
\]
\[
e^O_{s,0}=e^N_s,\qquad e^O_{s,\tau+1}=e^O_{s,\tau}+0.90c_{s\tau}\Delta t-d_{s\tau}\Delta t/0.90,\qquad 0.10E_B\le e^O_{s,\tau}\le0.90E_B\ (\tau=0,\ldots,n_\beta).
\]
Grid outage import = 0；事件 terminal 只需 10% 技術下界，不恢復事件前 SOC、不 cyclic。事件彼此獨立反事實，不依次耗用同一串年度 SOC。\(SR=0\)，因此 \(c,d\) 自動互斥，不需要新增 mode binary 或其 Big-M（outage mode Big-M = NOT APPLICABLE；SPEC L363）。

### 5.7 ENS 定義（SPEC L180–184）

\[
D_s=\sum_\tau Q_{s\tau}\Delta t,\quad ENS_s=\sum_\tau shed_{s\tau}\Delta t,\quad D_\Sigma=\sum_sD_s>0,\quad r=\sum_sENS_s/D_\Sigma .
\]
所有合法起點等權 aggregate；重疊窗口不是實際一年發生數千次停電，\(D_\Sigma\) 不是 annual load。\(Q=\alpha L\)，不能改為 \(\alpha[L-PV]^+\)。\(0\le r\le1\)。若報 pass rate，稱 structured-start event-coverage proportion，不稱機率 reliability。

### 5.8 年度成本 objective 與參數（SPEC §7）

\[
C=CRF(C_PP_B+C_EE_B)+FOM_PP_B+FOM_EE_B+\sum_t\rho_t^{energy}p_t^{grid}\Delta t+\sum_mB_mCC+\sum_{m,q}C_{over,m,q}+C_{deg}.
\]

| 參數 | 值 | 單位／角色 |
|---|---:|---|
| CRF | 0.08024258719069129 | 1/year；r_real=.05，20年 |
| C_P | 5392.90605 | NTD-2023/kW AC |
| C_E | 11281.486475 | NTD-2023/kWh nameplate |
| FOM_P | 33.67315 | NTD-2023/kW-year |
| FOM_E | 27.396425 | NTD-2023/kWh-year |
| a_P=CRF C_P | 432.74073392833 | NTD-2023/kW-year |
| a_E=CRF C_E | 905.2556621107918 | NTD-2023/kWh-year |
| a_P+FOM_P | 466.41388392833 | NTD-2023/kW-year |
| a_E+FOM_E | 932.6520871107918 | NTD-2023/kWh-year |
| C_rep | 5952.064125 | NTD-2023/battery-side kWh |
| λ_1,λ_2,λ_3 | .6200066796875；1.8600200390625；2.48002671875 | NTD-2023/battery-side discharged kWh |
| κ | 1.0103668594376984 | dimensionless site-specific billing proxy |

Source package ID `pnnl_v2024_lfp_2023_point_10mw_4to10h`；10 MW／4to10h 是 cost package label，不是設備容量或 duration constraint。FOM 與 \(C_{rep}\) 不再乘 CRF，不另計整包 replacement。\(\lambda\) 繼承 PNNL-calibrated Xu-derived package，不由新結果反向挑 cost bracket。Energy rates 以 S10 的 `(parameter_id=energy_{season}_{tou_period}, usage_year)` 唯一列映射，取 `value_constant_ntd2023`；N/A 必須拒絕，不填零。月份使用 `billing_usage_period_id` 的 usage year。純季 \(B_m\) 取 `basic_{season}_regular`；May／October 取兩季 regular basic rates 的算術平均。Supplementary contract components 固定 0。\(\sum_mB_m=2206.3163138237587\) NTD-2023/kW-year。S11 決定 overcontract rate；S12 提供 masks／period order metadata。不得從記憶重建電價或混入 nominal NTD。

### 5.9 F-01：Objective-independent exact billing（SPEC §8.1–§8.2）

\(q\) 依 peak→half→sat_half→off 排序；純非夏月 peak = N/A，省略。\(I_{mq}\) 為該 usage-month／period 的實際 timestamp set。
\[
G_{m,q}=\max_{t\in I_{m,q}}p_t^{grid},\quad D_{m,q}=\kappa G_{m,q},\quad a_{m,q}=\max(0,D_{m,q}-CC),\quad z_{m,0}=0,
\]
\[
z_{m,q}=\max(z_{m,q-1},a_{m,q}),\quad \Delta_{m,q}=z_{m,q}-z_{m,q-1}\ge0,\quad h_{m,q}=\max(0,\Delta_{m,q}-0.10CC),\quad W_{m,q}=2\Delta_{m,q}+h_{m,q}.
\]
Fixed applicable rate 時 \(C_{over,mq}=\rho_{mq}W_{mq}\)。每個「新增」區段各有 10%CC 的 2× allowance，其餘 3×；不是全月共享 allowance，也不重複計各 period raw exceedance。**所有 billing 等式在任何 objective 下成立**；這是保持相同 tariff function 的 formulation correction，不是新計費方法（SPEC L238）。

Exact MAX contract：凡 endogenous \(y=\max_ix_i\)，且 finite \(L_i\le x_i\le U_i\)，令 \(U=\max_iU_i\)：
\[
y\ge x_i\ \forall i,\qquad y\le x_i+(U-L_i)(1-b_i)\ \forall i,\qquad \sum_ib_i=1,\quad b_i\in\{0,1\}.
\]
可包含常數 0 operand；可用 exact native MAX general constraints 實現同一 contract；**不可只留 epigraph**；不得把必要 billing binaries 誤認為被禁止的 outage mode／installation binary。Finite bounds 依 SPEC L252–257（保守有效界，不用任何未執行之 optimal solution 推導）。

### 5.10 Class-C transition、guard domain 與 classifier（SPEC §8.3；CL1 §4.2–§4.3，依 RES R-01 優先）

- May 16–Oct 15 為夏季，依每小時 timestamp applicability。Class A 一季；Class B 兩季同費率；Class C 兩季不同費率（現行 calendar 為 2025-05、2025-10 的 `sat_half`、`off`）。C 先建 exact \(G_e,G_l\)，再 exact \(G_{mq}=\max(G_e,G_l)\)，\(D=\kappa G_{mq}\)；e、l 按時間先後；若新 masks 交錯，不能默默套用兩段 contract。
- \(d=D_l-D_e=\kappa(G_l-G_e)\in[-U_e,U_l]\)；
\[
\tau=\max\{10^{-4}\text{ kW},\ 100f,\ 100\,\epsilon_{machine}\max(1,L_{max})\},\qquad g=10f,
\]
\(f\) 為模型建構時實際讀取的 FeasibilityTol；accepted 設定 \(f=10^{-6}\) 下 \(\tau=10^{-4}\) kW、\(g=10^{-5}\) kW。
\[
d\le\tau+(U_l-\tau)b,\qquad d\ge-U_e(1-b)+(\tau+g)b,\qquad b\in\{0,1\};
\]
需 \(U_l\ge\tau+g\)，否則拒絕建構。McCormick：\(\bar W=3\bar z_q\)，\(0\le Y\le W\)，\(Y\le\bar Wb\)，\(Y\ge W-\bar W(1-b)\)，\(C_{over,m,q}=\rho_eW+(\rho_l-\rho_e)Y\)。May／October regular basic charge 的 50/50 不適用於 overcontract。
- **Guard-restricted domain（求解前的可行域限制，不只是求解後警告）：**
\[
X_g=\{x\in X:\ d_c(x)\notin(\tau,\tau+g)\ \ \forall c\in\mathcal C\}.
\]
- Post-solve classifier（CL1 §4.3）：\(|d|\le\tau\) → NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP；\(d<-\tau\) → EARLIER_SEASON_CLEARLY_LARGER；\(d<\tau+g\) → NUMERICAL_BOUNDARY_UNRESOLVED；其餘 → LATER_SEASON_CLEARLY_LARGER。Class-C UNRESOLVED 計入 certificate failure。
- 所有最終 billed maxima、canonical timestamps、month/season rates、tier 費用與 annual cost 須從 hourly dispatch 獨立重算並與模型核對；κ hourly proxy 不等於實際 15-minute meter 讀值（SPEC L286）。canonical source pricing 為 accepted case formulation，不能擴張為所有台電用戶通用官方規定（SPEC L284）。

### 5.11 B2：Analytical zero-ENS 證明與 finite cost domain（SPEC §9.1–§9.3）

- Reference construction：\(W_\beta=\max_{s\in S_\beta}\sum_{\tau=0}^{n_\beta-1}L_{s+\tau}\Delta t\)；\(P_{ref}=\max(P_{lo},5179\alpha)\)；\(E_{ref}=\max(E_{lo},\alpha W_\beta/0.72)\)；\(W_4=20451\)、\(W_8=39601\)、\(W_{12}=55977\) kWh。Normal：\(p^{ch}=p^{dis}=0\)、\(v^{use}=\min(V,L)\)、\(p^{grid}=[L-V]^+\)、\(e^N_t=.90E_{ref}\)；\(CC_{ref}=\kappa\times4985=5036.678794296927\) kW。Outage：\(c=0\)、\(d=R\)，全部 ENS = 0。此證明適用本候選方程，不是實機 GFM 驗證，也不是 optimized sizing。
- Cost certificate：\(C_{full}=67237027.63430355+466.41388392833P_{ref}+932.6520871107918E_{ref}\)（feasible reference cost，不是 EOB optimum）；\(\bar P=C_{full}/432.74073392833\)，\(\bar E=C_{full}/905.2556621107918\)；\(CC\) 上界 \(\bar{CC}=\min(\bar{CC}_{struct},\bar{CC}_{cost})\)，\(\bar{CC}_{struct}=\kappa(5179+\bar P)\)，\(\bar{CC}_{cost}=C_{full}/2206.3163138237587\)，兩界皆報告，不是法律上限。若加入負收益或額外 cap，須重新證明。
- 九組 numeric certificates：見 SPEC §9.3 表（carried independently recomputed arithmetic／feasible reference certificates，**不是 Solver outcome**）。後續 implementation 須由 full precision 公式重算；保存 decimal upper bounds 須向上取整，不能用向下 rounded 表格值當硬界。
- Normal／outage bounds：SPEC §9.4（經 §5.3 D3、RES R-02／R-09）。Outage：\(c\le\min(S,\bar P)\)、\(d\le\min(R,\bar P)\)、\(0\le shed\le R\)、\(0\le curt^O\le S\)、\(e^O\le.90\bar E\)；不得將 max outage deficit 用作 normal PCS sizing upper bound。Bound 鬆緊／numeric conditioning／runtime 尚未經 Pilot 驗證。

### 5.12 Endpoint 定義（SPEC §10）

\[
C_+^*(\epsilon)=\min_{x\in F_+(\epsilon)}C(x),\qquad r_+^*(\epsilon)=\min_{\substack{x\in F_+(\epsilon)\\C(x)=C_+^*(\epsilon)}}r(x),\qquad r_{EOB+}=r_+^*(1),
\]
\[
(C_{global}^*,r_{global}^*)=\operatorname{lexmin}\{(C_0^*,1),(C_+^*(1),r_{EOB+})\}.
\]
ENS 最小不保證唯一 dispatch；不宣稱唯一解或另加第三 objective。Cost premium 精確定義為 \(C_+^*(\epsilon)-C_{global}^*\)；百分比需 \(C_{global}^*>0\)。數值報告另列實際 reconciled endpoints 與 bounds，不混用 incumbent／lower bound 為同一最適值。

---

## 6. α／β 設計、基準比較、baseline fairness、實驗流程與評估指標

### 6.1 Study grid `[G2]`（SPEC L89–90；ART2 §7.5.4-C）

\(\alpha\in\{0.10,0.25,0.50\}\)、\(\beta\in\{4,8,12\}\) h，共九 cells；valid starts 不跨年、不 wrap。FW74 的 dense 9×9 grid `[V74-ONLY]`。FW74 §3.4 的 \(\beta=24\) h boundary case 不在 v8 研究域內，本次排除 `[G3-SCOPE]`（§2.5；R1 OPEN-09）。

### 6.2 基準與比較 `[G2]`

- 每 cell 的 baseline 為 **Global EOB**（§3）；EOB+ 不能取代 global baseline（SPEC L386）。
- Premium：\(C_+^*(\epsilon)-C_{global}^*\)（SPEC L386）。FW74 §6 的 EOB 與 \(\Delta C(\alpha,\beta)=C(\alpha,\beta)-C_{EOB}\)：其數學角色由 SPEC §10、§14-5 取代（v8 baseline 為 Global EOB）`[V74-ONLY]`（取代）；v7.4 EOB 結果為歷史限定，不得作為 v8 Global EOB `[V74-ONLY]`（歷史）。v8 endpoint 數學並非未決（AUD3 §4；R1 OPEN-03 處置見 §11.2）。
- v7.4 與 v8 之比較：須標明兩者為不同研究問題與不同可行域；差異不得全部歸因於單一變更（ART2 §7.5.4-E、§7.6）。

### 6.3 Baseline fairness 規則 `[G2]`（彙整；每條皆有來源）

1. 所有端點與 frontier 點使用同一 candidate domain 與同一 cell certificate；**禁止用不同 domain 產生端點後混圖**（SPEC L395）；每 cell 採自己的 certificate（SPEC L357）。
2. ε=1 可重用同一 EOB+ 結果；ε=0 與 RES 相同定義（SPEC L395）。
3. Approximate Global EOB：兩分支 stage 1 取得 \(U_0,U_+\) 與 \(L_0,L_+\)；用共同 \(U=\min(U_0,U_+)\)、\(L=\min(L_0,L_+)\) 與共同 cap \(\min(C_{full},U+\delta_C)\)，在符合共同 cap 的兩分支各 \(\min r\) 後比較；不能用非傳遞的 pairwise「差不多同成本」判定；individual EOB+ 用其自己的 positive cost band（SPEC L425）。
4. Floor scenarios 採相同 cost／ENS／tariff／input／tolerance contract；跨 floor frontier 比較使用共同 absolute ε，不以各自 normalized 端點位置冒充同一 ε（SPEC L457）。
5. 同一 planning series 送入所有端點與 outage recourse（SPEC L85；FW74 §0.1 L76 `[V74-CONT]`）。
6. Cost package 事前固定，不依結果反向切換（SPEC L209；FW74 §0.1 L83–84 `[V74-CONT]`）。
7. Branch 0 不獲 positive PV island service（SPEC L98–99、L490）；\(r_{PV}\) 構造的改善不能全部歸因於電池能量（SPEC L445）。
8. 每個數值宣稱綁定該 run 實際記錄的 FeasibilityTol、τ、g 與實作版本身分；不同 τ／g 的 run 不得視為同一可行域（RES R-07；ART2 §8-7）。
9. Replay 比較須納入 replay 實際 gap／residual；不得讓容差掩蓋較大的未解 gap（SPEC L428）。

### 6.4 數值 targets 與求解程序 `[G2]`（SPEC §11；均為 **Proposed numerical targets — pending Pilot verification**）

| 項目 | Proposed target |
|---|---|
| Primary absolute cost gap | \(U_C-L_C\le1\) NTD-2023/year |
| Same-cost allowance \(\delta_C\) | 1 NTD-2023/year，事前固定 |
| Secondary ENS absolute gap | \(U_r-L_r\le10^{-7}\) |
| ENS reporting/comparison \(\tau_r\) | \(10^{-6}\)；另報 \(\tau_rD_\Sigma\) kWh |
| Cost reconciliation target | \(10^{-3}\) NTD-2023/year |
| Cost numeric representation | 可用 C/1000，但所有 cap/gap 換算並以原單位報告 |

最小 procedure（未來授權後）：
1. Stage 1 記錄 solver incumbent、proven lower bound \(L_C\)、獨立 reconciled feasible upper \(U_C\) 與 gap；未達 target 不能宣稱取得指定精度端點。
2. Stage 2 保留全部 variables，以 \(r\) 為 objective，加入 \(C\le\min(C_{full},U_C+\delta_C)\)；exact billing 在此仍成立。
3. 獨立重算 cost、ENS 與物理 residual；記錄 stage 2 \(U_r/L_r\)／gap，不能只憑 status 稱最適。

誤差界：\(C(x_2)-C^*_{guard}\le(U^{guard}_C-L^{guard}_C)+\delta_C+\tau_C\)，建議 targets 下約 ≤ 2.001 NTD-2023/year；此為 conditional 數值誤差 budget，只相對於 \(C^*_{guard}\)（RES R-03；ART2 §8-2），沒有保證其 ENS 接近精確 lexicographic \(r\)。不以 relative MIP gap 當 same-cost tolerance；\(r\) 接近零時不用 relative gap。Native multiobjective 若將來使用，必須證明其 base-value 退化規則等價上述 explicit cap。

ε-frontier 最小 grid：\(\{0,\tfrac12r_{EOB+},r_{EOB+},1\}\)；數值上以已記錄的 \(\hat r_{EOB+}\) 產生近似 grid，按 \(\tau_r=10^{-6}\) 排序去重，保留 0／1 精確端點並保存每個 raw label 到代表點的 mapping；ε limit 與 achieved \(r\) 分欄（SPEC L392–395）。

Replay：比較 \(ENS_{main,s}\) 與 \(ENS_{replay,s}\)；理論上 replay 最優 ≤ main；可報 event 比較解析度 \(10^{-6}D_s\) kWh；若 replay 改善超出已證明 secondary gap／residual，需調查 endpoint 實作／精度，不能改名掩蓋。Branch 0 均 \(ENS=D_s\)（SPEC L427–429）。

### 6.5 Floor sensitivity preregistration `[G2]`（SPEC §13）

| Scenario | \(P_{lo}\) kW | \(E_{lo}\) kWh | Role |
|---|---:|---:|---|
| A | 1 | 1 | Low-intervention sensitivity |
| B | 10 | 20 | Proposed mainline |
| C | 50 | 100 | Higher-floor sensitivity |

三者均 ASSUMPTION。未來優先 \((\alpha,\beta)=(0.10,4)\) 的 EOB+ 及 high-ENS frontier；具體額外 ε 點在執行前另行固定（實作規劃；§2.5；R1 OPEN-07）。配對變動只辨認 joint floor effect；必要時另行授權 one-factor 檢查。靜態上 \(F_C\subseteq F_B\subseteq F_A\)，固定 ε 的精確 minimum cost 不會隨 floors 提高而下降。EOB+ 是否貼 floor、partial-service 最適解是否排除、runtime 及 numeric conditioning = PENDING PILOT VALIDATION。本輪不執行、不產生結果。

### 6.6 Positive-branch PV islanding claim boundary `[G2]`（SPEC §12）

\[
r_{PV}=1-\frac{\sum_s\sum_\tau\min(\alpha L_{s+\tau},V_{s+\tau})\Delta t}{D_\Sigma}.
\]
數值見 SPEC §12 表（前輪 read-only 算術）。相對 Branch 0 \(r=1\)，改善約 19.55–19.57、8.02–8.03、4.01–4.02 percentage points（\(\alpha=.10/.25/.50\)）。這是 conditional 可行構造，不是 EOB+ optimum；10／20 floors 不能消除此 branch service jump，也不證明實體 10 kW PCS 對全校 PV 具 GFM 能力。

### 6.7 評估指標與報告欄位 `[G2]`

| 類別 | 指標／欄位 | 來源 |
|---|---|---|
| 設計 | \(P_B,E_B,CC\)；branch | SPEC §3、§4 |
| 成本 | \(C\) 及分項（annualized CAPEX、FOM、energy、basic、overcontract、\(C_{deg}\)）；cost premium \(C_+^*(\epsilon)-C_{global}^*\)（百分比需 \(C^*_{global}>0\)） | SPEC §7、L386 |
| 服務 | \(r\)；\(ENS_s\)；\(D_s\)；\(D_\Sigma\)；\(\tau_rD_\Sigma\)；structured-start event-coverage proportion（若報 pass rate）；\(r_{PV}\)（構造邊界） | SPEC §6、L406、§12 |
| 精度 | exact theoretical optimum、tolerance-bounded approximate endpoint、incumbent、lower bound、reconciled achieved 值**分欄**；\(U_C,L_C,U_r,L_r\) 與 gap；ε limit 與 achieved \(r\) 分欄 | SPEC L395、L412–421 |
| 重算 | billed maxima、canonical timestamps、month/season rates、tier 費用、annual cost 由 hourly dispatch 獨立重算；物理 residual 以原單位 | SPEC L286、L414 |
| Replay | \(ENS_{main,s}\) vs \(ENS_{replay,s}\)；replay gap／residual | SPEC L428 |
| Class-C | ART2 §4.2 第 4 點 PRESERVE DIAGNOSTICS 全部欄位 | ART2 §4.2 |
| Run 身分 | FeasibilityTol、IntFeasTol、τ、g、實作版本身分 | RES R-07；ART2 §9-3 |

FW74 §8.2 輸出矩陣逐條處置見 §8.3：設計、annualized total cost 與分解、exact demand diagnostics、degradation diagnostics、realized SOC range／maximum hourly discharge fraction、ex-post rainflow summary 與 solver status／runtime／gap 承接 `[V74-CONT]`，與上表並列；\(R\)、\(P^{out}\)、v7.4 定義之 resilience premium、binding critical window、reserve-floor binding frequency／SOC headroom 為歷史 `[V74-ONLY]`。FW74 §8.3–§8.6 之圖表格式、邊際成本與 knee 判斷規則不承接為 v8 必要規則；新增 knee／marginal 指標須另行定義與審查（§2.5；R1 OPEN-04）。FW74 §18.7 solver reporting 欄位 `[V74-CONT]`（§6.9 A14）。

### 6.8 Gates 與 Pilot entry `[G2]`

| 項目 | 狀態 |
|---|---|
| Phase-1 formal implementation（Coding） | NOT_YET_AUTHORIZED（ART2 §12） |
| PV0 correctness Pilot | NOT_YET_AUTHORIZED；入口前置條件：ART2 §4.2 R-05b（as amended，D6）、§9 各項；範圍／cell／時間上限／STOP 條件另以 Pilot 授權文件明定（ART2 §9-5）→ 實作規劃（§2.5；R1 OPEN-07） |
| Production／re-freeze | NOT_YET_AUTHORIZED |
| Type-3 certification；classifier 修改 | NOT AUTHORIZED（D9） |

**Pilot fail-closed（D6；ART2 §4.2 摘要）：** 任何 Class-C component 之 `NUMERICAL_BOUNDARY_UNRESOLVED`，或 `source_selection`、`bounded_product`、`source_timestamp`、`resolved_rate`、`native_seasonal_max` 任一 invariant failure（不論 W 是否為 0）→ **STOP／REPORT／PRESERVE DIAGNOSTICS**；狀態標記 `CLASS_C_CERTIFICATE_FAILED`；不得表述為模型數學不可行、solver INFEASIBLE、方法論無效或 guard 已改變最適值；禁止重新分類、放寬 classifier、調整容差、手動改標籤、重算後改標 PASS、以不同設定重跑消除、修改正式 code（全文以 ART2 §4.2 為準）。

Pilot 授權當時，須重新核對 Gate 2 四份文件、ART2 與 REC 的 SHA-256；不符即 STOP（ART2 §9-6）。

### 6.9 驗證義務分層 `[FW8-PROPOSED]`（逐項標明來源；回應 AUD3 §3、§4 OPEN-05／06）

R1 將 FW74 §4、§18.3 提議承接（含 ex-post rainflow comparison），卻又在 OPEN-05 將 degradation validation 列為「是否執行」待定（AUD3 §3）。R2 將驗證與 sensitivity 分為四層：A 強制驗證義務、B 承接之 sensitivity 角色、C 可選新增項、D 實作細節；E 列出由 Gate 2 取代之 v7.4 驗證項。A 層各項於 Gate 3 接受後，只能經另行 methodology authority 變更，不得以 sensitivity、選擇性或實作便利之名義取消。

**A. 強制驗證義務**

| # | 義務 | 來源 | v8 適用 |
|---|---|---|---|
| A1 | Data／chronology audit：8,760 intervals；首末 timestamp；Asia/Taipei；無重複、無缺漏、步長 1 h；calendar／TOU 由 interval-start 重建；provenance flags；不得 hybrid／zero-winter 回退 | FW74 §18.1 第 1–12 點 `[V74-CONT]`；SPEC §3 | S13 唯一 planning series |
| A2 | 公式與單位：kW×h＝kWh；效率各用一次；\(C_E\) 分母為 nameplate；raw CAPEX → normalization → CRF 之順序；FOM 不再乘 CRF；annual fixed 與 event cost 不混用 | FW74 §18.2 `[V74-CONT]`（「reserve 公式明列 \(\Delta t\)」一項為 ③）；SPEC §5、§7 | 全部模型 |
| A3 | Power／energy balance 與 aggregate SOC：normal balance residual；\(t\to t+1\) transition；\(0.10E_B\le e^N_t\le0.90E_B\)；\(e^N_T=e^N_0\)；strict hourly charge/discharge exclusivity；CAPEX 計於 \(E_B\)（nameplate） | FW74 §18.3 aggregate state `[V74-CONT]`（「\(0.10E^N+R\le e_t\)」「\(0.8E^N\ge R\)」二項為 ②）；SPEC §5 | 每一 endpoint／frontier 點 |
| A4 | Xu segment structure：\(\lambda_k\) 自動產生；\(\sum_ke_{t,k}=e^N_t-0.10E_B\)；segment bounds 與 dynamics residual；periodic boundary；aggregate power＝segment power 和；cycling cost 用 battery-side discharged energy；multi-hour deep-discharge synthetic test；segment diagnostics | FW74 §18.3 Xu 部分 `[V74-CONT]`；SPEC §5 | 同上 |
| A5 | **Ex-post rainflow cycle-depth／cost validation**：solve 後對 SOC trajectory 做 rainflow，至少比較 realized cycle-depth distribution、PWL cycling cost 與 rainflow-derived benchmark cost；差異異常時先查 implementation／calibration，不以文字合理化；rainflow 不嵌入 optimization | FW74 §0.1 B1（L80）、§4.4.3-E（L1194）、§16.1 Degradation validation 第 1、3 點、§18.3 末項 `[V74-CONT]`；SPEC §14-6；REG74 R31＋R20 | 取代 v7.4 用語「全部 final EOB + Layer A solutions」：v8 mainline（floor B）中作為最終結果報告之 positive-branch 最佳化解（EOB+、RES stage 2、ε-frontier 點；Global EOB 落在 positive branch 時亦同）；Branch 0 無電池，不適用。具體清單於實作規劃固定，但不得為空集合 |
| A6 | Linear throughput cost：只作 benchmark／equivalence diagnostic，不作第二 mainline | FW74 §0.1 B1、§4.4.3-E、§16.1 第 2 點 `[V74-CONT]` | post-processing，與 A5 同一組解 |
| A7 | Outage 技術檢查：valid starts 只含完整窗口位於 case year 內者、不 wrap；outage grid import＝0；\(0.10E_B\le e^O_{s\tau}\le0.90E_B\)（含 terminal \(\tau=n_\beta\)）；\(c\le\min(S,P_B)\)、\(d\le\min(R,P_B)\)、\(shed=R-d\)、\(curt^O=S-c\)；handoff \(e^O_{s,0}=e^N_s\)；annual 與 outage 使用同一 planning series；audit 失敗先修模型、不以文字解釋 | FW74 §18.4 第 1（同一 series 部分）、2、6（technical window 部分）、7（grid import 部分）、8（terminal 技術下界部分）、12 點 `[V74-CONT]`；SPEC §6 `[G2]` | 每一 positive-branch endpoint 與 replay |
| A8 | ENS accounting：由 hourly 解獨立重算 \(D_s\)、\(ENS_s\)、\(D_\Sigma\)、\(r=\sum_sENS_s/D_\Sigma\)；\(Q=\alpha L\)（不是 \(\alpha[L-PV]^+\)）；Branch 0 \(ENS_s=D_s\) | SPEC L180–184 `[G2]` | 同上 |
| A9 | Billing 獨立重算：billed maxima、canonical timestamps、month/season rates、tier 費用、annual cost 由 hourly dispatch 重算並與模型核對；FW74 §18.5 保存清單與 2025/09 手算案例（regular CC 5000 kW；half-peak exceedance 16 kW；5,340.8 NTD）由 code 精確重現；cost-facing auxiliaries 不作 diagnostics | SPEC L286、§8 `[G2]`；FW74 §18.5 `[V74-CONT]`（其 epigraph 一致性檢查之對象於 v8 改為 SPEC §8.2 exact MAX contract）；REG74 P5 | 每一 run |
| A10 | Class-C 與 guard：classifier 標籤；UNRESOLVED 與 invariant failure 依 §6.8 fail-closed；建構時檢查 \(U_l\ge\tau+g\) | CL1 §4.2–§4.3；ART2 §4.2 `[G2]` | 每一 run |
| A11 | Big-M 與 bounds：所用 \(M\)／bounds 與 D3 baseline 一致，並以該 cell 自己的 certificate 驗證 | REC D3；RES R-02、R-09；SPEC §9 `[G2]` | 每一 cell |
| A12 | 數值證書：stage-1 \(U_C,L_C\)、stage-2 \(U_r,L_r\) 與 gap；cost reconciliation；共同 cost band；ε limit 與 achieved \(r\) 分欄 | SPEC §11 `[G2]` | 每一 endpoint／frontier 點 |
| A13 | Fixed-design／fixed-normal-SOC replay 比較：\(ENS_{replay,s}\le ENS_{main,s}\)（容差內）；改善超出已證明 gap／residual 須調查 | SPEC L427–429 `[G2]` | 每一 positive-branch endpoint |
| A14 | Solver reporting 與 run identity：status、objective、runtime、MIP gap、infeasibility diagnostics、framework version、parameter-registry hash、input hash、code hash；FeasibilityTol、IntFeasTol、τ、g | FW74 §18.7 `[V74-CONT]`；RES R-07；ART2 §9-3 `[G2]` | 每一 run |

**B. 承接之 sensitivity 角色**（不是 validation；角色依既有 accepted 方法）

| # | 項目 | 處置 |
|---|---|---|
| B1 | Floor sensitivity A／B／C | Gate 2 preregistered（§6.5；SPEC §13）；執行另行授權 |
| B2 | 1 MW-scale cost-scale sensitivity | 角色 ①：FW74 §0.1 L83–84（Gate 1 CLOSED）——exogenous、整包更換 \(C_E,C_P,FOM,C_{rep},\lambda_k\)、不得依結果切換。FW74 §16.1 將其列為 Layer A 最低限度 sensitivity；依研究者範圍規則（既有 accepted 方法所要求者不延後），R2 **不延後、不刪除**本項，其 v8 執行集合（cells／endpoints）於實作規劃固定。研究者若欲於 v8 延後本項，須於 Gate 3 接受紀錄中明示（屬範圍決定，不是 Gate 2 amendment） |
| B3 | SOC 20–80% technical sensitivity | 角色 ①：FW74 §16.1；REG74 R19、R17；10–90% mainline 由 FW74 §0.1 L72 鎖定。處置同 B2：不延後、不刪除；執行集合於實作規劃固定；若欲延後須於 Gate 3 接受紀錄明示 |
| B4 | Efficiency 不做 full sweep | ①（FW74 §0.1 L73、§16.1） |
| B5 | Outage-load／short-gap preprocessing robustness | ① 條件式：僅在 formal outage logs 支持 expanded envelope 時執行（FW74 §16.1） |
| B6 | Zero-winter | ①：不是 mandatory sensitivity（FW74 §16.1、§36.1） |
| B7 | A2 reserve-floor robustness（6 points） | ②：v8 無 reserve floor，不適用 |

**C. 可選之新增 sensitivity／benchmark**（延後；`[G3-SCOPE]`）：未被既有 accepted 方法要求者，例如 floor 之 one-factor 檢查（SPEC §13「必要時另行授權」）、新增 ε 點、新 cost／tariff 情境、DG 相關 sensitivity（隨 DG 延後）。FW74 §16.1 Degradation validation 第 3 點之 selected-case model-form test 為條件觸發：只在 A5 顯示 PWL-vs-rainflow 誤差或 sizing implication 異常、且已先檢查 implementation／calibration 後才考慮。

**D. 實作階段細節**（`[FW8-PROPOSED]`；R1 OPEN-06）：A 層各項之具體 test case、檔案格式、檢查程式與報表樣式，於 Coding／Pilot 授權前以實作清單固定；不得藉此修改 acceptance tolerances、數值 certificates 或刪除 A 層任何一項。

**E. 由 Gate 2 取代、v8 不執行之 v7.4 驗證項**（②／③）：FW74 §18.4 第 3 點（\(R\)、\(P^{out}\) 單調性）、第 4 點（annual reserve floor）、第 5 點（replay initial \(=SOC_{min}E^N+R\)）、第 6 點「不得繼續要求 reserve floor」（v8 無對象）、第 7 點「不利用 outage PV surplus 再充電」（v8 允許 \(c\le S\)）、第 8 點「不要求恢復 \(R\)」（無對象）、第 9 點（all valid starts 無 shortfall；binding window 與預計算一致）、第 10 點（energy-binding window terminal 接近 \(SOC_{min}E^N\)）、第 11 點（Layer B 語義區分，隨 Layer B 延後）；FW74 §18.3「\(0.10E^N+R\le e_t\)」「\(0.8E^N\ge R\)」；FW74 §18.1 末段「重算 81-case \(R/P^{out}\)」（③）。

---

## 7. 證據與宣稱邊界 `[G2]`

### 7.1 Guard-restricted optimality（ART2 §8；D4）

1. 宣稱域（R-07）：EOB0 → \(F_0\cap X_g\)；EOB+、RES stage 2、ε-frontier、lexicographic endpoints → \(F_+(\epsilon)\cap X_g\)；Global EOB → \((F_0\cap X_g)\cup(F_+(1)\cap X_g)\)。
2. 2.001 NTD 誤差界只相對於 \(C^*_{guard}\)，不是 unrestricted physical domain 的誤差證書。
3. \(L^{guard}_C\) 不得作為 \(\inf_\tau\) 或 \(\inf_{strict}\) 的下界。不等式鏈 \(C^*_{overlap}\le C^*_{closed}\le\inf_\tau\le C^*_{strip}\le C^*_{guard}\)（stage-1 cost minimization；不適用 stage 2、Global EOB lexmin、cost band 內 ENS 比較）。
4. 不得宣稱 \(C^*_{guard}=\inf_\tau\) 或差為 0；T5 的約 0.0054 NTD/年只能以「在假設 H 下」的條件形式引用；H 在最佳化後全年解上 NOT VERIFIED。
5. 計價 formulation（RES R-04；ART2 §5.1、§8-5）：若某 Class-C component 滿足 \(r_l\ge r_e\)（開側較貴），該 component 之閉合計價逐點等於 canonical 計價（component 層級）；**僅當模型中所有 Class-C component 均滿足 \(r_l\ge r_e\) 時**，才有 \(C^*_{closed}=\min f_\tau=\inf_\tau\)（可達；年度／全模型層級）。現行 calendar 因 October component（\(r_l<r_e\)）不滿足此條件。方案 B 不得作為計價 formulation；方案 C 在 October 方向會低估，只能作 relaxation／lower-bound 工具；本研究不採用 C 計價。（ART2 §8-5 以「同向（§5.1）」簡寫此條件；依 ART2 §7.2 第 1 層 precedence，以 §5.1 之 \(r_l\ge r_e\) 原文為準——全部 component 均為 \(r_l<r_e\) 雖屬「同向」，亦**不**滿足此結論。）

> **Guard-restricted mathematical optimality ≠ unrestricted physical-domain optimality.**

### 7.2 Tariff 方向與 τ／strict 揭露（D5、D7；ART2 §5.1、§6、§8-5、§8-6）

- **方向條件（ART2 §5.1）：** component 層級——該 component 須滿足 \(r_l\ge r_e\)，其閉合計價才逐點等於 canonical 計價；年度層級——**所有** Class-C component 均須滿足 \(r_l\ge r_e\)，才有 \(C^*_{closed}=\inf_\tau\)（可達）。「同向」不足以表達此條件。現行 calendar：2025-05 `sat_half`／`off` 為 \(r_l>r_e\)（non_summer 32.05732664233577 → summer 43.031906934306576；component 條件成立）；2025-10 為 \(r_l<r_e\)（RES R-04b 表；條件不成立，T4 適用，閉合方案可能低估 \((r_e-r_l)W\)）。因此全年模型不得因 May component 的方向推論閉合方案在年度層級精確（ART2 §5.2）。本修正只恢復宣稱條件，不改任何 billing 方程式（§5.9–§5.10），不重開 Class-C 數學或 D8 處置。
- 論文報告之帳單為 τ-convention 帳單，應如此揭露；\(0<d\le\tau\) 且 \(W>0\) 時，單一設計 τ 與 strict 帳單相差 \((r_e-r_l)W\)，\(|r_e-r_l|=10.97458029197081\) NTD-2023/kW-month；約 0.054 NTD/年只是最適值之間的條件界，NOT VERIFIED。L2 是 project rule，不是台電官方完整跨季公式；τ、g 是數值實作慣例。
- EXP5b 兩個 α=0.50 月度 fixture 的 `off` component 位於 **d=0**（不得寫成 d=τ）；Phase-1 全年 Class-C d／W 行為 NOT VERIFIED（ART2 §6.3）。

### 7.3 Type-3、H-PV、classifier（D9）

全年 Type-3 certification NOT VERIFIED、NOT AUTHORIZED；classifier 修改 NOT AUTHORIZED；H-PV 只在 reference dispatch 上觀察（EXP4b），最佳化後全年解 NOT VERIFIED；隔離實驗（1,316 次 optimize）未經獨立重跑；FeasibilityTol = 1e-9 出現決定性錯誤 INFEASIBLE，調緊容差不是安全修正（ART2 §10）。

### 7.4 RCA 與審查證據（REC S5(ii)、D8）

- RCA 數值只以 OBSERVED-relay 等級引用；原 549 行報告 `ab9aa820…` NOT VERIFIED；若正式 v8 理由須將其列為直接驗證證據，須先取得原始報告 bytes，或另行授權由 Full81 primary outputs 重算（ART2 §7.6）。
- FLA 文字只以研究者採納之規範文字身分生效；FLA／RCA 為 operator-extracted、未經獨立重現。
- Gate 2 審查覆蓋：H1–H3 同工具；FLA／MBR 有限、身分未驗證；Gate 2 S1–S5 PASS 只限所列範圍；SPEC 數學、Root-Cause、Full81 未經全面重新驗證（REC §4 D8）。本 Framework 不得把這些描述為已驗證，亦不得引為 primary evidence（DD §D.4-2）。

### 7.5 Residual limitations

ART2 §10 第 1–13 點、SPEC L500（floor 為研究假設；無 NTUST GFM minimum 來源；PV eligibility jump；hourly κ proxy 非 15-minute 量測；cost-scale extrapolation；perfect outage foresight；structured starts 非停電機率；transition case-rule 非普遍官方規定；bound 可能鬆；conversation-only 審查報告無持久化 byte 身分）、DD §K 全部保留。FW74 §22 逐條（R2 修正）：第 1、4、5、6、7、8、9、10、14、18 項承接 `[V74-CONT]`（第 7 項中之「adequacy」在 v8 讀作 ENS／ε 結果）；第 11 項前段（outage 使用 PV 隱含 island-capable controls／protection／grid-forming capability；本研究不做 inverter／protection／interconnection engineering design）承接，後段（Layer B \(\gamma_{PV}=0\)）隨 Layer B 延後；第 2、3 項以 all-start adequacy／worst-case reserve 為對象，為 ②（v8 對應限制見 §2.4、SPEC L90、L184）；第 12、13 項屬 Layer B、第 15–17 項屬 DG，隨各該延後項保留於 v7.4 範圍（§2.5），日後納入時另行承接。

---

## 8. v7.4 → v8 前瞻繼承、保留與替換

### 8.1 權源與兩階段接受 `[G2-D]`（REC §4 D12、§5；ART2 §7.5.4）

- D12(a)：依 PROT §1 前瞻 v8 methodology successor；逐字採納 ART2 §7.5.4-A、-B、-D、-E、-F；§7.5.4-C 依 DD §C.3 補充。§7.5.4-B 授權文句及 ART2 SHA 見 REC §5。PROT §30 本案不需要；不修改 Protocol；不建立常設或一般 CLOSED 豁免；僅就 §7.5.4-C（依 DD §C.3 補充）所列差異構成本案限定處置。
- 分類：實質 methodology successor，加上治理授權變更；不是 implementation correction，也不是錯誤修正；不主張、亦未證明 v7.4 存在任何錯誤（ART2 §7.5.2）。
- 兩階段（ART2 §7.5.4-D）：Gate 2（已完成，REC）→ Gate 3（本 Candidate → 獨立審查 PASS → 研究者正式接受）→ Activation（另行明示；形式於 Gate 3 決定；本 Candidate 之提案見 §8.5（R1 OPEN-12））。每一步都不會自動觸發下一步。

### 8.2 Gate 2 已接受之處置（DD §C.3 轉錄）`[G2]`

| v7.4 條款 | v7.4-ONLY（v8 不繼承） | CONTINUES（對 v8 繼續適用） | 依據 |
|---|---|---|---|
| §0.1 L70 | dense 9×9 grid；以所有 valid starts 的 worst-case reserve 作為服務要求 | valid starts 不跨年、不 circular wrap | SPEC L89、L90、L152、L464 |
| §0.1 L72 | 「normal-operation reserve 必須位於 technical SOCmin 之上」之 reserve 要求（v8 無 reserve floor，不帶入任何 reserve） | \(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)、\(E^U=0.8E^N\) 之技術界限與 usable-energy 意義 | SPEC L131、L152、L176 |
| §0.1 L74（A2） | annual／outage 分離成兩個 stage；constant worst-case reserve floor；replay 從最低 preparedness state 開始 | —（v8 改為 normal SOC handoff 的 PV-first outage recourse，各端點分開） | SPEC L152、L466、L468 |
| §0.1 L87 | — | Layer B 的歷史角色（固定 Layer A 設計、不重新擴充設備；structured scenarios 不是可靠度機率）。Phase-1 outage recourse 與 fixed-design replay 都不是 Layer B，也不自動授權任何新的 Layer B 工作；**v8 下的 Layer B 須在 Gate 3 另行定義並經審查** | SPEC §6、L427–429 |
| §0.1 其他（L68–69、L71、L73、L75–86、L88–90） | — | 全部繼續適用；SPEC §14-6 明示不改效率、SOC、monetary basis、κ evidence route、PNNL cost／Xu semantics | SPEC L469 |
| §7.3–§7.5（L1415–1514） | 外生 valid-start energy reserve \(R(\alpha,\beta)\)、瞬時 power adequacy、全年 reserve floor，以及由此導出的 \(E^N\)／\(P^B\) 下限 | — | SPEC L152 |
| §7.7（L1535–1598） | normal bound 中的 \(+R(\alpha,\beta)\) 項；「LP-first，只有 audit 發現同時充放電時才加 binary」的主線偏好（v8 改採 strict hourly binary） | \(\eta_c=\eta_d=0.90\) 且只套用一次；\(t\to t+1\) state transition；technical SOC window；年度 cyclic boundary \(e_T=e_0\)；Xu segment 的 periodic boundary | SPEC §5、§14-2 |
| §7.10（L1749–1825） | A2 分離式 replay；\(e_0=SOC_{min}E^N+R\)；Layer A analytical-consistency replay 禁止 PV recharge（v8 outage 允許 \(c\le S\)） | outage grid import = 0；outage 期間只維持技術界限；「不得描述為未來停電保證或可靠度機率」 | SPEC §6 |
| §7.11（L1827–1843） | 正向保證句「每個 valid start 都滿足 modeled energy and power adequacy」（v8 允許部分 ENS，不可沿用此句） | 「不可寫 guarantees any future outage」，以及未納入因素清單 | SPEC L90、L184、L500 |

ART2 §16-7：若之後發現 SPEC 與上表以外的 v7.4 §0.1 鎖定內容衝突 → **STOP**，不得以本處置涵蓋。上表**不修改** FW74 的任何 byte。

### 8.3 其餘 v7.4 章節的逐條承接分類 `[FW8-PROPOSED]`（R2 修正；依 §0.4；須審查與研究者確認）

分類代碼見 §0.3（① 承接；② Gate 2 明示取代；③ 歷史限定；④ 本 Candidate 之 v8 安排；⑤ 研究者範圍決定延後）。R1 本節之整節分類（含「§7.1–§7.2 v7.4-only」「§18.4 v7.4-only」）由下表取代。

| FW74 條款 | 分類 | v8 處理／依據 |
|---|---|---|
| 前言 v7.2／v7.3 economic integration freeze 條列 | ① | 與 SPEC §7、§14-6 一致（Gate 1／Gate 2、CRF、monetary basis、SCHOOL/FROZEN、N/A peak、50/50 basic transition） |
| §0.1（L68–90） | 見 §8.2 | DD §C.3 Gate 2 處置；表列以外者全部 ① |
| §0.2 待 Layer A 完成後決定 | ③；v8 對應處置 ⑤ | Layer B 選點、knee、DG 細化、24 h 均為 v7.4 Layer A 後續事項；v8：Layer B／DG 延後、24 h 排除、knee 不預設（§2.5） |
| §0.3；§24–§27；§29–§32 | ③ | v7.4 governance／狀態紀錄；不承接為 v8 規範 |
| §1.1–§1.2 定位與主張 | ①（部分） | 見 §2.4。§1.1「韌性…是限制同一個 BESS 在平時可自由使用的程度」之 reserve 讀法為 ②；§1.1 量化句中「固定設計在 PV 衰減與需求成長下何時失效」（Layer B）與「hypothetical DG」部分為 ⑤ |
| §1.3 題目；§20 章節；§21 貢獻 | ④（編輯性後續） | R1 OPEN-08；須符合 §2.4–§2.5 |
| §2 RQ1–RQ2 | ③ | 以 all-start adequacy response surface 為研究問題；v8 研究問題見 §2.1、§2.3 |
| §2 RQ3、RQ4 | ⑤ | Layer B、DG 延後（§2.5） |
| §3.1 系統邊界；§3.2 \(\alpha\) | ① | 見 §4.3、§4.4 |
| §3.3 \(\beta\) | sizing 讀法 ②；「非正確解讀」① | 見 §4.3 |
| §3.4 grid | 9×9 grid ②（DD §C.3 L70）；24 h boundary 排除（§2.5） | |
| §4.1–§4.3（資料、chronology、tariff、κ） | ① | SPEC §3、§7、§8 與之一致；§4.2.2 billed-maximum rule 以 SPEC §8 exact MAX 為 v8 formulation |
| §4.4（BESS 技術、cost、degradation） | ① | 含 §4.4.3-E「rainflow 不嵌入 optimization，只作 ex-post validation」與「linear throughput 保留為 model-form benchmark」（§6.9 A5–A6）；§4.4.3-E 中「若 reserve-heavy Layer A solutions…」之預期敘述為 ③ |
| §4.5 register | ①；其中 A2 四列與 reserve-floor robustness 列為 ② | |
| §5.1 | nameplate／usable energy／stored-energy state 定義 ①；reserve 相關式 ② | 記號對照見 §5.1 |
| §5.2 billing auxiliary「可使用 epigraph」 | ② | SPEC §8.2 exact MAX contract；SPEC §14-7 |
| §6 EOB 與 premium | 數學角色 ②；歷史 EOB 結果 ③ | v8 baseline 為 SPEC §10 Global EOB；premium 依 SPEC L386；v7.4 EOB 數值不得作 v8 Global EOB（§6.2） |
| §7.1 Layer A 功能 | ② | all-start sizing 問題由 aggregate ENS／ε 取代（SPEC L152、§14-1） |
| §7.2 淨服務缺口 \(d_t(\alpha)=[\alpha L_t-PV_t]^+\)；「\(\alpha\) 必須放在 max 內」；planning-series identity | ① | 運算與 SPEC §6 之 \(R_{s\tau}=\max(Q_{s\tau}-V^O_{s\tau},0)\)、\(Q=\alpha L\) 相同（AUD3 §3）；R1「§7.2 整節 v7.4-only」之分類撤回 |
| §7.2 中 \(d_t\) 作為 §7.3 reserve 輸入之角色 | ② | v8 不計算 reserve |
| §7.3 valid-start set \(\mathcal S_\beta=\{s:s+n_\beta\le T\}\) 與「不做 circular year-end wrap」 | ① | SPEC L90；DD §C.3 L70 列 |
| §7.3 \(G_s\) 之 reserve 用途與 \(R(\alpha,\beta)\)；§7.4 power adequacy；§7.5 reserve floor | ② | DD §C.3 §7.3–§7.5 列；SPEC L152 |
| §7.6 normal power balance（四式） | ① | AUD3 §3：FW74 L1520–1532 → SPEC L118–119 → 本文件 §5.3，只有 \(PV\leftrightarrow V\) 記號改寫 |
| §7.7、§7.10、§7.11 | 見 §8.2 | 承接：效率各用一次、state transition、technical SOC window、annual cyclic、segment periodic boundary、outage grid import＝0、outage 只維持技術界限、不得寫成未來停電保證及未納入因素清單。取代：normal \(+R\) 界、LP-first 偏好、A2 分離式 replay、\(e_0=SOC_{min}E^N+R\)、outage 禁止 PV recharge、「每個 valid start 都滿足 adequacy」之正向保證句 |
| §7.8 objective 之成本函數（六項）與 §7.8.1–§7.8.3 | ① | AUD3 §3：FW74 L1611–1623 六項 ↔ 本文件 §5.8；\(CRF(C_EE^N+C_PP^B)\)；L1652–1692 之 breakpoints、segment capacity、shifted state、dynamics、power sums、\(\sum\lambda p^{dis}\Delta t/\eta_d\) 一致；`0.0802426` 與 full-precision CRF 為顯示精度差；不另計 replacement stream、不重複 subsidy、排除 PV sunk CAPEX |
| §7.8 作為 Layer A（受 reserve floor 限制）之單一 objective 問題結構 | ② | v8 之外層決策為 ε-constraint／lexicographic（SPEC §10） |
| §7.9 binding window \(s^*=\arg\max G_s\) | ③ | 依賴 \(G_s\) 與 reserve；不是 v8 必要輸出 |
| §8.1 計算順序 | ③ | v8 程序依 SPEC §10–§11 |
| §8.2 輸出矩陣 | ①：\(E^N,E^U,P^B,CC\)；annualized total cost 與分解；exact demand diagnostics；degradation diagnostics；realized SOC range、maximum hourly discharge fraction；ex-post rainflow summary；solver status／runtime／gap。③：\(R\)、\(P^{out}\)、v7.4 定義之 resilience premium、binding critical window、reserve-floor binding frequency／SOC headroom | 與 §6.7 並列 |
| §8.3 應產出的圖 | 圖型 ④（後定）；reserve／binding-window／marginal-cost 圖 ③ | rainflow validation summary 之內容為 §6.9 A5 之報告，呈現形式後定 |
| §8.4 邊際變化；§8.6 近似決策規則 | ③；v8 不設 marginal-cost 決策規則（⑤） | 以 81-grid 為前提 |
| §8.5 knee／no-knee | 「不得因期待管理結論而硬找 knee」①；具體判斷規則 ③；新規則 ⑤ | ART2 §7.6；DD §K |
| §9–§10 Layer B | ③（歷史 Layer B 只在 v7.4 範圍有效）；v8 Layer B ⑤ | 舊 initial SOC \(SOC_{min}E^N+R\) 不得搬入；fixed-normal-SOC replay 不是 Layer B |
| §11 implementation boundary | ① | FW74 §0.1 L88 |
| §12.1 existing DG 不進主線；§12.2 hypothetical DG 為獨立外生 extension；DG 成本／燃料／CO₂ 分列 | ① | FW74 §0.1 L89–90 |
| §12–§15 DG 方法（\(R^{DG}\)／\(G^{ref}\) sizing、sweep、會計、呈現規則） | ③；v8 DG extension ⑤ | 歷史 DG reserve sizing 不帶入 v8 |
| §16.1 | 見 §6.9（A5、A6、B2–B7） | |
| §16.2–§16.3 DG sensitivity、過度計算 | ③；隨 DG ⑤ | |
| §17 計算量 | ③ | 81-grid、A2 6 solves、24 h、DG 之 solve 數均為 v7.4 計數。v8 九 cells **不等於**九次 solver call：每 cell 之 solve plan 至少須涵蓋 Branch 0 與 positive branch、lexicographic stage 1／stage 2、最低 ε-grid 各點（去重後）、Global EOB 共同 cost band 程序、逐事件 fixed-normal-SOC replay，以及 floor sensitivity；具體計畫於實作規劃固定（§2.5）。「adequacy audit 可解析／向量化 replay」「rainflow 屬 post-processing、不計入 annual optimization solve 數」之原則 ① |
| §18.1–§18.7 | 逐項見 §6.9（A1–A14、E） | R1「§18.4 整節 v7.4-only」之分類撤回 |
| §19 舊結果；§28 legacy；§33–§36 lineage | ③ | ART2 §7.5.4-E；歷史保留 |
| §22 limitations | 見 §7.5 | |
| §23 文獻 | 見 §9 與 REGD | |

### 8.4 歷史保留與不授權事項 `[G2]`（ART2 §7.5.4-E、-F）

Framework v7.4、Registry v7.4 及其 acceptance closures／manifests、Full81 run `20261008T183934456307Z_a6826f4828` 及其 acceptance、EOB 結果、canonical pointer R1／R2、checkpoints、Git lineage 與所有原始 SHA，保持 byte-identical，並在其原始假設下維持歷史有效性。禁止以 v8 文件、結果或任何後續 artifact 覆寫、刪除、改名、就地修補或追溯重新標記上述歷史 bytes；禁止將 v7.4 描述為「失敗」「無效」或「已撤銷」。

### 8.5 Gate 3 接受與 Activation 契約 `[FW8-PROPOSED]`（ART2 §7.5.4-D：形式於 Gate 3 決定；R1 OPEN-12）

本節只**定義**未來程序；本 Candidate 不執行其中任何一步，且每一步都不自動觸發下一步。

1. **Targeted independent Gate 3 audit：** 由非本 session、非 R1 作者 session 之獨立審查者（建議 Codex fresh session；PROT L324–327），以唯讀方式審查本 R2 與 REGD 之 exact bytes（範圍 §12），產出明確 verdict（PROT §26：`<TOPIC> — PASS` 或 `— STOP`）。
2. **Exact identity PASS：** PASS 須明示其所審查之 R2 與 REGD 之 SHA-256；任何 byte 變動後之文件不承接該 PASS。CONDITIONAL PASS 或 STOP 不得作為接受依據。
3. **研究者明示接受：** 研究者（唯一 acceptor；PROT L95、L322）以書面 Gate 3 Acceptance Record 接受，記錄：R2 與 REGD 之 SHA-256；審查 verdict 及其 report／rollout 身分；§2.5 範圍決定及 §6.9-B2／B3 處理之確認或修改；接受範圍（Framework v8 = 本 R2；Registry v8 = REG74 + REGD）。接受紀錄不得新增規範文字；若有，該部分另行 targeted review。
4. **SHA-256 綁定：** 接受紀錄綁定 R2、REGD、REC、SPEC、CL1、RES、ART2、DD 之 SHA-256；接受時重新核對，任一不符即 STOP（PROT L707）。
5. **另行授權之 Activation：** Gate 3 接受後，研究者另行明示授權 Activation。明示生效紀錄之形式為 canonical pointer successor（`configs/current_mainline_pointer.json` 為 read-first routing index，現為 R2；其 successor 依既有 pointer candidate → independent audit → acceptance → activation 流程辦理，先例見 `results/provenance/current_mainline_pointer_acceptance_r1/`、`…_r2/`），或研究者於接受紀錄中另定之等效明示紀錄。Git publication 與入口文件（CLAUDE.md、PROT §1／§28、CURRENT_STATE）之 routing 更新屬 repository mutation，各自另行授權（R1 OPEN-11）。
6. **v7.4 歷史身分保留：** Activation 前，FW74／REG74 為唯一 current accepted authority；Activation 後轉為 historical accepted predecessor，其 CLOSED／ACCEPTED 身分、bytes、closures、manifests、Full81、EOB 結果與 pointer R1／R2 均保持不變（ART2 §7.5.4-E）；不追溯。
7. **不授權：** Gate 3 接受與 Activation 均不授權 Coding、Pilot、Solver、Production 或 Git publication（ART2 §7.5.4-D、-F）。

本 Candidate 未執行 Activation、未修改 `current_mainline_pointer.json`、未建立 activation record。

---

## 9. Literature／evidence alignment

### 9.1 Registry v7.4 中 v8 直接使用的條目（角色不變）

| 條目 | v8 用途 | 來源 |
|---|---|---|
| [R1] Laws et al. (2018)、[R2] Bazdar et al. (2024)、[R4] Gorman et al. (2023) | floors 的文獻脈絡：獨立非負 kW／kWh、integer modules、usable-energy 情境；**不是**通用 positive floor 或 NTUST 門檻 | SPEC L72–75、L79 |
| [R5]、[R6] | ENS／shortfall 作連續退化指標 | REG74 L2298 |
| [R20] Xu et al. (2018)；[T2] PNNL v2024；[T4] Viswanathan et al. (2022) | Xu-derived degradation；cost package；DOD calibration | SPEC §5、§7 |
| [R31] Shi et al. (2018) | ex-post rainflow validation 之方法支撐（§6.9 A5）；不嵌入 optimization | REG74 L2317；FW74 §4.4.3-E |
| [I1]–[I3]、[P2] | 15-min demand、summer boundary、tariff source-of-truth、κ calibration | SPEC §7、§8 |
| [T5]、[R35]、[R36] | constant-dollar／real-rate 一致性 | FW74 §0.1 L83 |

### 9.2 Registry v8 Minimal Additive Delta（R2；回應 AUD3 §5、R1 OPEN-10）

R1 §9.2 標題「Registry v7.4 未收錄」不適用全部五項（AUD3 §5）：E-4 之 [R7]、[P4] 已存在於 REG74（L290–317、L1942–1999），E-5 亦有部分既有概念證據；缺的是 v8 適用角色與 mapping。R1 §9.3「若研究者選擇不建 Registry delta，須在 Gate 3 接受紀錄中明示 E-1～E-5 為已揭露的 evidence gap」之選項，與 REC 採納之 ART2 §7.5.4-D（Gate 3 對象含 Registry「或 delta」）衝突（AUD3 §5），**R2 刪除此選項**，改採最小 additive delta 路線：

- **REGD**（§1）：只就 E-1～E-5 與 v8 claim-to-source mapping 增列；不重寫、不修改 REG74 任何 byte；Activation 前 REG74 仍為唯一 current accepted evidence authority。
- 不以 Protocol amendment 迴避 delta 要求。
- 本輪未作新文獻檢索。E-1（ε-constraint／lexicographic 外部文獻）與 E-2（Jeroslow–Lowe 書目）之外部 attribution 在 REGD 中明確標為 NOT VERIFIED，並限定相關內容只由 accepted project specification／project derivation 支持（REGD §1–§2）。
- E-3：R1「只作『無 NTUST GFM threshold』的負面證據」之寫法撤回，改為「本案尚未取得可核實的 NTUST GFM minimum 證據」（SPEC L78；REGD §3）；華夏 2 MWh 網頁不作任何 GFM minimum 之正或反證據。10／20 floors 仍為 accepted research assumption（§5.2）。

| 缺口 | REGD 處置 | 對 Gate 3 之影響 |
|---|---|---|
| E-1 | REGD §1：project definitions（SPEC §10）、numerical certification（SPEC §11）、project derivation（RES R-03）與外部 attribution 分列；外部 attribution NOT VERIFIED，不建書目 | 非 Gate 3 blocker：本 Framework 未以外部文獻作為任何 v8 方法宣稱之依據；論文若寫成附引用之文獻 attribution，須先另行授權核實 |
| E-2 | REGD §2：R-04a 為 accepted project derivation；名稱引用不是書目驗證；不得擴張為一般 representability 定理 | 同上 |
| E-3 | REGD §3 | 非 blocker；不新增工程認證要求 |
| E-4 | REGD §4：R7 之 preparedness–economic trade-off 概念保留；P4 之 reserve floor、initial state、no-recharge 規定為 v7.4 歷史（歷史 evidence 角色保留） | 待 targeted audit 確認 |
| E-5 | REGD §5：v8 claim-to-source mapping（含 exact billing／P5、floors、replay、degradation、機率宣稱限制） | 待 targeted audit 確認 |

### 9.3 Framework 與 REGD 之一致性

§9.1 之既有條目角色不變；REGD 只對 v8 軌增列角色註記，不刪除 REG74 任何條目或其歷史角色。若本 Framework 與 REGD 對同一 claim 之 evidence role 不一致，視為本 Candidate 之缺陷，以 additive successor 修正；方法內容一律以 Gate 2 package 為準（§0.2）。

---

## 10. 本 Candidate 的 provenance

### 10.1 R2 輪（2026-10-24）

- 作者：Claude Code session `203b1afd-3311-4f4e-91cd-4547e4f63365`（Opus 5.5），fresh session；不是 R1 作者 session（`414ae497…`），亦未參與 SPEC、CL1、RES、ART2、DD 或 REC 之撰寫，但與其中多份文件之作者使用相同工具與模型。**本 session 不得擔任 R2 或 REGD 之獨立審查者。**
- 授權：研究者 2026-10-24 Gate 3 STOP remediation 指令——只授權建立本檔與 REGD 兩份 candidate；不授權接受、Activation、Git、Coding、Solver、Pilot 或新文獻檢索。AUD3 之擷取另經研究者於本 session 單次核准（§1）。
- 建立方式：以 `python -I` 讀取 R1 bytes（先驗證 SHA `d35cd196…`），以逐條斷言（行首內容核對、子字串唯一出現）之行替換與插入產生本檔，並以獨占建立方式寫出；未列於 §14 之文字與 R1 逐 byte 相同。
- 操作：對 §1 來源之唯讀 SHA-256、`sed`／`grep`／`awk`、`git rev-parse`、`git status --porcelain`、`git ls-files`；唯讀讀取 `configs/current_mainline_pointer.json` 之欄位（未修改）；AUD3 rollout 擷取（只取 final answer、session_meta、turn_context）。Session scratchpad 中之暫存檔（AUD3 擷取副本、建檔腳本、REGD 草稿）非交付物、非 durable。
- 計數：Existing files modified = 0；Repository modified = 0；Git mutations = 0；New files = 2（本檔與 REGD，皆在 repository 外）；Checkpoint／ledger／manifest created = 0；Model builds = 0；Solver calls = 0；Coding = 0；Literature retrieval = 0；Self-acceptance = 0；Activation = 0。
- 本檔不嵌入自身 SHA-256；一經雜湊即不可變，更正以 additive successor 處理（PROT §4–§5）。

### 10.2 R1 輪（歷史紀錄，逐字承接；文中「本 Candidate」「本文件」指 R1）

- 作者：Claude Code session `414ae497-0221-4ddf-aca4-5eb94803643e`（Opus 5.5）。此 session 亦為 Gate 2 REC 的記錄者，並曾擷取 Gate 2 審查報告；它**不是** SPEC、CL1、RES、ART2、DD 的作者，但與其中多份文件之作者使用相同工具與模型。**本 session 不得擔任本 Candidate 的獨立審查者。**
- 授權：研究者 2026-10-24 Gate 3 指令（單獨授權建立 Framework v8 Candidate；不授權接受、Activation、Git、Coding、Solver、Pilot、Production、D11、memory 修改）。
- 操作：只對 §1 來源作唯讀 SHA-256、`sed`／`grep`、`git rev-parse`、`git status --porcelain`；唯一新增檔案為本文件（repository 之外）。
- 計數：Existing files modified = 0；Repository modified = 0；Git mutations = 0；Registry created = 0；Checkpoint／ledger created = 0；Model builds = 0；Solver calls = 0；Coding = 0；Self-acceptance = 0。
- 本檔不嵌入自身 SHA-256；一經雜湊即不可變，更正以 additive Candidate R2 處理（PROT §4–§5）。

---

## 11. OPEN register 與 R2 處置

### 11.1 R1 OPEN register（R1 原文逐字保留；歷史紀錄；文中「本 Candidate」指 R1）

| ID | 事項 | 為何未決 | 需要的決定 |
|---|---|---|---|
| OPEN-01 | v8 下的 Layer B（FW74 §0.2、§2 RQ3、§9–§10、§22-12/13） | DD §C.3 L87 列要求 Gate 3 另行定義並經審查；Gate 2 規格沒有 v8 Layer B 方法 | 研究者選擇：(a) Phase-1／v8 範圍不含 Layer B；(b) 另行授權撰寫 v8 Layer B 規格並審查；(c) 其他 |
| OPEN-02 | DG extension（FW74 §2 RQ4、§12–§17、§18.6） | 邊界條款（L89–90）承接，但 v8 是否執行 DG 研究未定；Phase-1 模型不含 DG | 研究者決定是否納入及何時 |
| OPEN-03 | FW74 §6 EOB／premium 定義在 v8 的處置 | DD §C.3 未列；SPEC §10 已有 v8 定義 | 確認 §6 為 v7.4-only，或另作處置 |
| OPEN-04 | FW74 §7.9 binding window、§8.2–§8.6 輸出矩陣、圖表、邊際成本、knee 規則 | 多以 reserve 為前提；v8 報告格式未定 | 研究者決定 v8 輸出／圖表規格（不得預設 knee） |
| OPEN-05 | v8 sensitivity 集合（1 MW cost-scale、SOC 20–80%、degradation validation） | Gate 2 只登錄 floor sensitivity | 研究者決定是否執行及範圍 |
| OPEN-06 | v8 驗證清單取代 FW74 §18.4 的完整內容 | Gate 2 只給部分檢查（SPEC L286、§11；ART2 §4.2） | 由實作授權前另行固定 |
| OPEN-07 | 九 cells 的執行順序、額外 ε 點、計算量、Pilot 範圍／cell／時間上限／STOP 條件 | SPEC L457、ART2 §9-5 明示另行固定 | Pilot 授權文件 |
| OPEN-08 | 子問題措辭、論文題目、章節、貢獻寫法 | 非方法規格 | 研究者／指導教授 |
| OPEN-09 | \(\beta=24\) h boundary case | v8 grid 只含 4／8／12 h | 是否另行加入 |
| OPEN-10 | Registry v8 delta（§9.2 E-1～E-5） | 角色變更與新增來源屬 Registry 權責 | 是否建立及何時；E-1、E-2 需檢索授權 |
| OPEN-11 | 入口文件落後（PROT §1／§28 寫 v7.2；CLAUDE.md 寫 v7.3；CURRENT_STATE 無 Phase-1 條目） | 屬 repository mutation | 另行授權；不得據此把權威退回 v7.2／v7.3 |
| OPEN-12 | Activation 的形式（例如 canonical pointer successor） | ART2 §7.5.4-D：形式於 Gate 3 決定 | 研究者於 Gate 3 接受時決定 |
| OPEN-13 | D11 durable custody（Downloads 文件、Temp 實驗目錄、rollout 擷取副本） | REC 未授權 | 另行授權；Temp 有被 Storage Sense 清除的風險 |
| OPEN-14 | §0.4 承接規則與 §8.3 分類本身 | Gate 2 未明文決定 | 審查與研究者確認 |

### 11.2 R2 處置（回應 AUD3 §4；研究者 2026-10-24 範圍決定）

分類欄為 AUD3 §4 之建議分類（A 須在 Gate 3 前處理；B 研究者可明示排除／延後；C 實作／編輯階段；D evidence／custody）；它不代替研究者決定科學範圍。

| OPEN | AUD3 | R2 處置 | 位置 | 尚未發生之事 |
|---|---|---|---|---|
| 01 Layer B | B | 延後；不在本次 v8 接受範圍；歷史 Layer B 只在 v7.4 範圍；replay 不是 Layer B | §2.5、§8.3 | 未定義 v8 Layer B 方法 |
| 02 DG | B | 延後；zero-combustion 主線不變；FW74 §0.1 L89–90 邊界承接；舊 \(R^{DG}\) sizing 為歷史 | §2.5、§8.3 | 未建立 DG 方法 |
| 03 EOB／premium | B（限歷史適用範圍） | 已由 SPEC §10 決定；FW74 §6 數學角色 ②、歷史結果 ③ | §6.2、§8.3 | — |
| 04 outputs／binding／knee | B | §6.7 最低欄位，加上 §8.3 承接之 FW74 §8.2 欄位；reserve／binding 指標 ③；knee／marginal 規則延後 | §6.7、§8.3、§2.5 | 圖表規格未定 |
| 05 sensitivity／degradation | A | 強制 validation（A5、A6）與 sensitivity 角色（B）、可選項（C）、實作細節（D）分層 | §6.9 | 未執行任何 validation 或 sensitivity |
| 06 validation checklist | C | §6.9-A 列出強制義務；具體實作清單於 Coding／Pilot 授權前固定 | §6.9-D | 實作清單未建立 |
| 07 九 cells／ε／Pilot | C | 研究域、最低 ε-grid、certificates 不變；排程、額外 ε 點、Pilot 子集合、時間上限延後至實作規劃；九 cells 不等於九次 solver call | §2.5、§6.8、§8.3（§17 列） | Pilot 未授權 |
| 08 題目／章節／措辭 | C | 編輯性後續；須符合 §2.4–§2.5 | §2.3 | 未改寫 |
| 09 \(\beta=24\) h | B | 排除於本次研究域 | §2.5、§6.1 | — |
| 10 Registry v8 delta | D | 已建立 REGD Candidate R1（未接受）；R1 之省略選項刪除 | §9.2 | REGD 未審查、未接受 |
| 11 入口文件落後 | C | 屬 Gate 3 接受後另行授權之 routing 更新；本輪不修改 CLAUDE.md、PROT、CURRENT_STATE 或 pointer | §8.5-5 | 未更新 |
| 12 Activation 形式 | A | 契約已定義 | §8.5 | 未執行 Activation |
| 13 durable custody | D | 維持已揭露限制（REC D11 不授權；S5(ii)）；本輪無新 custody 操作（AUD3 擷取副本亦在非 durable scratchpad） | §1、§7.5、§10.1 | 未保存 |
| 14 承接規則／分類 | A | 逐條分類；§7.2、§18.4 之整節分類撤回；validation 歧義消除 | §0.4、§8.3、§6.9 | 待 targeted audit 與研究者接受 |

---

## 12. Targeted independent Gate 3 audit 之最小範圍（建議）

**Reviewer：** 不得為本 session（`203b1afd…`）、R1 作者 session（`414ae497…`）或 SPEC、CL1、RES、ART2、DD 之作者；建議 Codex fresh session（PROT L324–327）。若改用 Claude Code fresh session，須如實標記為 session-independent、非 cross-model。Verdict 建議格式（PROT §26）：`FRAMEWORK V8 CANDIDATE R2 AND REGISTRY V8 DELTA CANDIDATE R1 — PASS` 或 `— STOP`。

| # | 範圍 | 內容 |
|---|---|---|
| T1 | 身分 | R2、REGD 之 SHA；§1 全部來源 SHA；R1 仍為 `d35cd196…`；REC 與 Gate 2 package 未變動 |
| T2 | 差異限定 | R2 對 R1 之差異僅限 §14 所列；未列為變更之文字與 R1 逐 byte 相同（可機械 diff） |
| T3 | AUD3 blocker 1 | §7.1 第 5 點與 §7.2 之 \(r_l\ge r_e\) 條件與 ART2 §5.1 一致；billing 方程式未變 |
| T4 | AUD3 blocker 2 | §0.4、§8.3、§6.9 逐條分類：§7.2、§7.3 共同定義、§7.6、§7.8、§18.4 拆分；degradation validation 未被取消；無 reserve-floor 語義被帶回；Layer B／DG 未被默默承接 |
| T5 | 範圍 | §2.5 未改變 Gate 2 研究域、ε-grid、endpoints、guards 或數值 contracts；§6.9-B2／B3 之處置是否忠實於既有 accepted 方法 |
| T6 | AUD3 blocker 3 | REGD E-1～E-5；省略選項已刪除；無杜撰引用；NOT VERIFIED 標示準確；本 Framework §9 與 REGD 一致 |
| T7 | AUD3 blocker 4 | §8.5 Activation 契約之完整性；未執行 Activation；v7.4 current authority 保留 |
| T8 | OPEN | §11.2 對 14 項之處置與 AUD3 §4 一致；無虛假完成宣稱 |

**明確排除：** Gate 2 規格本身之數學正確性（Gate 2 已接受；AUD3 未發現核心方程式轉錄之 major defect）、Class-C／Full81／Root-Cause 重新分析、任何 solve、新文獻檢索；與 R1 逐 byte 相同之段落只需機械比對。

---

## 13. 不授權事項與 STOP

本文件不授權：Framework v8 ACCEPTANCE；current-authority Activation；Registry v8 或 REGD 之接受；Git add／commit／tag／push；CURRENT_STATE、canonical pointer、CLAUDE.md 或 Protocol 更新；Coding；PV0 Pilot；model build 或 Solver；Production；Type-3；classifier 修改；D11 證據保存；新文獻檢索；修改任何 v7.4／Full81／EOB 歷史 bytes。

## 14. R1 → R2 變更清單

| R2 位置 | 變更 | 回應 |
|---|---|---|
| 標題、狀態標記、前言 | R1 → R2；加入 R2 修正範圍說明 | 生命週期 |
| §0.1 第 4–5 點 | 新增 AUD3 與研究者 Gate 3 範圍決定之地位 | F4 |
| §0.3 | `[OPEN]` 定義更新；新增 `[G3-SCOPE]`；①～⑤ 分類代碼 | AUD3 §3 |
| §0.4 | 改為逐條分類規則 | AUD3 §3；OPEN-14 |
| §1 | 新增 R1、AUD3、REGD 列；R2 輪核對與 AUD3 custody | 身分 |
| §2.3 末段 | OPEN-08 處置 | OPEN-08 |
| §2.5（新） | 研究範圍：納入／排除／延後 | AUD3 §7-2；F4 |
| §6.1 末句、§6.2 第 2 點、§6.5 末段、§6.7 末段、§6.8 Pilot 列 | OPEN-09、-03、-07、-04 處置 | OPEN 處置 |
| §6.9（新） | 驗證義務分層 A～E | AUD3 §3；OPEN-05／06；F3 |
| §7.1 第 5 點、§7.2 第 1 點 | 恢復 ART2 §5.1 之 \(r_l\ge r_e\) 條件 | AUD3 blocker 1；F1 |
| §7.5 | FW74 §22 逐條承接 | AUD3 §3 |
| §8.1 第 3 點 | 指向 §8.5 | OPEN-12 |
| §8.3 | 整表改為逐條分類 | AUD3 blocker 2；F2 |
| §8.5（新） | Gate 3 接受與 Activation 契約 | AUD3 blocker 4；F5 |
| §9.1 | 新增 [R31] 列 | §6.9 A5 |
| §9.2–§9.3 | 刪除 Registry 省略選項；REGD 處置；E-3 措辭撤回 | AUD3 blocker 3；F6 |
| §10 | 新增 §10.1 R2 provenance；R1 provenance 逐字保留為 §10.2 | 身分 |
| §11 | R1 OPEN register 逐字保留為 §11.1；新增 §11.2 處置 | AUD3 §4 |
| §12 | 改為 targeted audit 範圍 | 下一 gate |
| §13、§14、末行 | 不授權清單更新；本表；狀態標記 | 生命週期 |

上表以外之全部 R1 行與 R1 逐 byte 相同（可機械 diff 確認）。特別是 §2.1–§2.2、§2.4、§3、§4、§5 全部、§6.3、§6.4、§6.6、§7.3、§7.4、§8.2、§8.4、§10.2 與 §11.1 未變更；§6.1、§6.2、§6.5、§6.7、§6.8 只變更上表所列之句，其方程式、參數、數值與規則未變。

**FRAMEWORK V8 — CANDIDATE R2 / NOT ACCEPTED / NOT ACTIVATED / PENDING TARGETED INDEPENDENT AUDIT — V7.4 REMAINS CURRENT AUTHORITY**
