# Thesis Literature Evidence Registry v8 — Minimal Additive Delta Candidate R1（2026-10-24）

> **REGISTRY V8 DELTA — CANDIDATE R1 / NOT ACCEPTED / NOT ACTIVATED / PENDING TARGETED INDEPENDENT AUDIT**
>
> 本文件是 Registry v7.4（REG74）的**最小 additive delta 候選**，供 Framework v8 Candidate R2（FW8R2）之 Gate 3 使用（ART2 §7.5.4-D：Gate 3 對象含「Registry（或 delta）」）。它**不是** Registry v7.4 的改寫，**不修改** REG74 任何 byte，不刪除、不改名、不追溯重新標記 REG74 任何條目或其歷史角色。在 Gate 3 獨立審查 PASS、研究者正式接受、並另行明示 Activation 之前（FW8R2 §8.5），**Registry v7.4 仍是唯一 current accepted evidence authority**；本 delta 只對 v8 軌增列角色註記與 claim-to-source mapping。

---

## 0. 性質、權源與讀法

### 0.1 來源（2026-10-24 本輪以唯讀 SHA-256 核對；全部 MATCH）

| ID | 路徑 | SHA-256 | 角色 |
|---|---|---|---|
| REG74 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` | 被延伸之 accepted evidence authority（不修改） |
| REG74-C | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` | REG74 接受紀錄 |
| FW74 | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` | current accepted methodology（至 Activation） |
| REC | `C:/Users/Iris C/Downloads/Iris_Phase1_Methodology_Specification_Acceptance_Decision_Record_2026-10-24.md` | `459c3a861ae890fd90a868bac9f269d9f1316eba25cf054796597d071b9d795b` | Gate 2 接受紀錄 |
| SPEC | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` | v8 數學規格本體 |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` | Class-C guard 澄清 |
| RES | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md` | `3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5` | R-01～R-10 |
| ART2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R2_Candidate_2026-10-24_DRAFT.md` | `2386d47b96690ac3a8c81673b1c4750e85bce93ef837ce47a75e850cb49f8268` | Acceptance artifact |
| DD | `C:/Users/Iris C/Downloads/Iris_Phase1_Methodology_Specification_Acceptance_Decision_Candidate_R1_2026-10-24_DRAFT.md` | `ac0728d9d8eb33efdc92b2866bd1f87c709710e53c6e75b7b030313f100c04b7` | 僅第 0 層內容有效（REC §1.2） |
| PROT | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` | 治理 protocol |
| AUD3 | Codex Gate 3 稽核 final answer（session `01a16cc6-a809-7ce1-9129-5b35de1a5630`；rollout 第 138 行；23,234 bytes） | `8cdae46384efaec96d28aec239e2b4aaa3342259367e21f7e1c643800c319e05` | E-1～E-5 缺陷之證據（不是接受權源）；custody 見 FW8R2 §1 |
| FW8R2 | `C:/Users/Iris C/Downloads/Iris_Thesis_Research_Framework_v8_Candidate_R2_2026-10-24_DRAFT.md` | 由交付回覆提供（FW8R2 內嵌本 delta 之 SHA；為避免循環，本檔不嵌入 FW8R2 SHA） | 對應 Framework Candidate |

Repository 路徑相對於 `C:/Users/Iris C/OneDrive/Desktop/iris_thesis`。

### 0.2 範圍與不做之事

- 只處理 AUD3 §5 之 E-1～E-5，以及 v8 claim-to-source mapping（AUD3 §5 末段：E-5 應涵蓋 exact billing／P5、floors、normal-SOC replay 等已接受之 v8 差異）。
- **本輪未作任何新文獻檢索；未重新核實任何外部原文。** 下文引用 REG74 既有條目時，其書目與「支持什麼／不能支持」以 REG74 原紀錄為準；本 delta 不宣稱已重新核實其外部原文。
- 不新增 bibliography 條目；不為使 Registry「看似完整」而建立任何未核實之引用。
- 不重複 REG74 已有條目；只對 v8 軌增列角色註記。

### 0.3 Evidence-role 代碼（本 delta 專用）

| 代碼 | 意義 |
|---|---|
| **AM** | Accepted project methodology：Gate 2 已接受之 v8 方法規格（REC D1；SPEC＋CL1＋RES＋ART2＋DD 第 0 層）之定義或規則 |
| **PD** | Project mathematical derivation：accepted package 內之證明或推導；其接受受 REC D8 覆蓋限制（SPEC 數學未經全面重新驗證） |
| **LC** | Literature conceptual support：REG74 既有外部文獻條目，角色以 REG74 所載為限 |
| **OS** | Official tariff／technical source：REG74 既有官方／機構來源（I1–I5、T2–T5） |
| **RA** | Research assumption：研究假設，不是外部事實或工程門檻 |
| **EN** | Empirical numerical evidence：accepted package 已記錄之資料算術或構造（例如 SPEC §3 資料事實、§9.3 reference certificates、§12 \(r_{PV}\)）；**v8 尚無任何 solver 結果** |
| **NV** | Not yet verified：外部 attribution 或證據尚未核實 |
| **HIST** | 只在 v7.4 範圍有效之歷史角色；不是 v8 規定 |

---

## 1. E-1 — ε-constraint 與 lexicographic 方法

**REG74 現況：** 無專門條目。本輪於 REG74 bytes 搜尋 `ε-constraint`、`epsilon-constraint`、`lexicograph`、`Haimes`、`Mavrotas`，皆無命中。REG74 中 [R2]、[R13]、[R15] 等之多目標或 resilience 脈絡，**不得**升格為 exact ε-constraint／lexicographic 方法來源（AUD3 §5）。

| 層次 | 內容 | 依據 | 角色 |
|---|---|---|---|
| Project-specific 定義 | \(C_+^*(\epsilon)\)、\(r_+^*(\epsilon)\)、EOB0、EOB+、Global EOB、RES、ε-frontier、最低 ε-grid \(\{0,\tfrac12r_{EOB+},r_{EOB+},1\}\)、去重與 mapping 規則 | SPEC §10（L368–395）；RES R-07；ART2 §8-1 | AM |
| Lexicographic 階段結構 | cost-first、ENS-second；stage 2 保留完整決策空間；cost band \(C\le\min(C_{full},U_C+\delta_C)\)；Global EOB 共同 cost band 程序 | SPEC §10 L376、§11 L397–429（L425）；RES R-02（各階段有效域） | AM |
| Numerical certification | cost／ENS gap、\(\delta_C\)、\(\tau_r\)、reconciliation、不以 relative MIP gap 作 same-cost tolerance；native multiobjective 若使用須證明等價於 explicit cap | SPEC §11（「Proposed numerical targets — pending Pilot verification」） | AM；可達性 = NV（待 Pilot） |
| 誤差界 | \(C(x_2)-C^*_{guard}\le(U^{guard}_C-L^{guard}_C)+\delta_C+\tau_C\)（約 ≤ 2.001 NTD-2023/年，只相對 \(C^*_{guard}\)） | RES R-03；ART2 §8-2 | PD |
| 外部 scholarly attribution | ε-constraint 方法與 lexicographic（preemptive／hierarchical）多目標最佳化之文獻出處 | **REG74 與 Gate 2 package 均無書目紀錄** | **NV** |

**限制與影響：**
- v8 方法在本論文中之有效性，建立在 accepted project specification（精確定義）與 numerical certification 上，**不**建立在外部文獻上；不得以一般多目標文獻作為本案 exact implementation 之驗證。
- 論文若寫出「ε-constraint／lexicographic 為既有標準方法」之**附引用**句子，須先經另行授權之文獻核實；在此之前，該類句子只能不附引用、或明示為本研究之方法設定。
- **Gate 3 影響：** 非 Framework 內容接受之 blocker——FW8R2 未以外部文獻作為任何 v8 方法宣稱之依據（FW8R2 §9.2）；屬論文撰寫之 evidence limitation。若研究者要求 Gate 3 接受即包含外部方法 attribution，則須先授權 E-1 核實，屆時本項成為 blocker。

---

## 2. E-2 — Jeroslow–Lowe

**位置：** CL1 §5 L135（命題 T1 之證明步驟）：「有界 MILP 的可行集是有限個多胞形的聯集（Jeroslow–Lowe），因此是緊緻閉集；它在 \((d,\lambda)\) 上的投影也是閉集。」此為**名稱引用**，無作者全名、題名、出處、年份或頁碼。REG74 未收錄。

**拘束之 accepted 命題：** RES R-04a（取代 CL1 L141–145「三選一」敘述；CL1 L147–153「本命題的界線」保留；REC D5）：設有界、整數取值有限、僅含非嚴格線性約束之 MILP，其可行集在 \((d,\lambda)\) 上之投影為閉集 \(F\)；若 \(F\subseteq\Gamma\)，則存在 \(\delta>0\) 使 \((\tau,\tau+\delta)\) 不屬於 \(F\) 的 d-投影（二分性質，PROVEN）。

| 項目 | 角色 |
|---|---|
| R-04a 命題及其證明（在 Gate 2 接受範圍內） | PD（REC D8：SPEC／CL1 數學未經全面重新驗證之限制保留） |
| 證明所使用之性質：上述類型 MILP 之可行集為有限個多面體之聯集、為閉集，其線性投影亦為閉集 | PD（作為 accepted 證明之一步） |
| 「Jeroslow–Lowe」外部 attribution | **NV**；名稱引用不是書目驗證 |

**限制：**
- 不得把該引用擴張為 MILP representability 之一般刻劃（例如何種集合可由 MILP 表示之充要條件），也不得宣稱超出 R-04a 所需之上述閉集性質；R-04a 亦不主張其他技術（CL1 L147–153 所列）一定無法處理此問題。
- 論文寫法二擇一：(i) 將該性質呈現為本研究之推導、不附外部 attribution；或 (ii) 經另行授權核實書目後再附引用。
- **Gate 3 影響：** 非 blocker；本輪未授權、亦不進行 representability 之重新研究。

---

## 3. E-3 — NTUST 華夏校區 2 MWh 網頁

**來源：** SPEC L76（URL `https://www.ntust.edu.tw/p/406-1000-152616%2Cr1182.php?Lang=en`；Web byte hash = NOT AVAILABLE；未保存網頁副本）。REG74 未收錄。本輪未重新開啟該網頁（NV）。

**角色限定：** 至多為「另一校區存在 2 MWh 級建置」之背景脈絡（依 SPEC 前輪轉述；NV）。**不得**作為下列任一之證據：
- 最低 GFM 建置規模；
- 不存在最低 GFM 規模；
- 本案系統之工程可行性；
- 任何 floor 或門檻。

**正確敘述（取代 Framework v8 Candidate R1 §9.2 E-3「只作『無 NTUST GFM threshold』的負面證據」）：** 本案**尚未取得可核實的 NTUST GFM minimum 證據**（SPEC L78：`NO VERIFIED NTUST GFM ELIGIBILITY THRESHOLD FOUND`）。未找到證據不等於證明門檻不存在。

**10／20 floors：** 依 Gate 2 原意為 RA——user-authorized proposed mainline research ASSUMPTION，非 accepted engineering threshold，不是 Q1 規定、NTUST GFM 認證、optimal sizing 或 full-service adequacy（SPEC L108；FW8R2 §5.2）。[R1] Laws et al. (2018)、[R2] Bazdar et al. (2024)、[R4] Gorman et al. (2023) 只作 floor 之文獻脈絡（獨立非負 kW／kWh、integer modules、usable-energy 情境；SPEC L72–75），不提供 floor 數值（LC）。Floor sensitivity A／C 亦為 RA（SPEC §13）。**不新增工程認證要求或 blocker。**

---

## 4. E-4 — [R7] 與 [P4] 在 v8 軌之角色

兩者**均已存在**於 REG74：[R7] Son et al. (2024)（L290–317）；[P4] A2 reserve-floor／outage-replay semantics（L1942–1999）。Framework v8 Candidate R1 §9.2 將其列為「Registry v7.4 未收錄」之缺口係誤列；需要的是 v8 角色註記，不是新增來源。

### 4.1 [R7] Son et al. (2024)

| REG74 中之用途 | v8 軌角色 |
|---|---|
| 「同一顆 BESS 的經濟用途與 preparedness 互相競爭」；reserve 更多 stored energy 會犧牲正常運轉經濟性 | **保留（LC）**：作為 v8 Cost–ENS 權衡之概念脈絡。v8 以 ε-frontier 與 normal-SOC handoff 內生表示此權衡（SPEC §6、§10），其公式為 project methodology（AM），**不是** R7 所提供 |
| 「不再任意指定停電瞬間 initial SOC」 | 概念相容（LC）：v8 之 outage 起始狀態為 \(e^O_{s,0}=e^N_s\)（SPEC §6），由 normal operation 決定、非任意指定；該 handoff 公式為 AM，非 R7 |
| 「改用 year-round reserve／minimum available-energy policy」 | **HIST**：v8 無 reserve floor（SPEC L152；DD §C.3 L72、L74 列）；不得作 v8 規定或 v8 方法證據 |
| REG74 L2299 claim-map 列「year-round reserve／min SOC preparedness \| R7」 | **HIST**（v7.4 範圍）；v8 對應列見 §5 第 10 列 |

R7 之「不能支持」（\(R(\alpha,\beta)\) 公式、universal minimum SOC、LFP 10–90%）原文保留，並延伸至 v8：R7 亦不支持 ENS cap、aggregate denominator、ε-frontier 或 handoff 公式。

### 4.2 [P4] A2 reserve-floor／outage-replay semantics

| P4 內容 | v8 軌角色 |
|---|---|
| Annual reserve floor \(SOC_{\min}E^N+R(\alpha,\beta)\le e_t\) | **HIST**（Gate 2 取代；SPEC L152） |
| Outage replay \(e_0=SOC_{\min}E^N+R\) | **HIST**（v8：handoff \(e^O_{s,0}=e^N_s\)） |
| Layer A consistency replay 禁止 PV-surplus recharge | **HIST**（v8 outage 允許 \(c\le S\)） |
| 6-point reserve-floor robustness | **HIST**（v8 無 reserve floor） |
| Outage technical SOC window、\(p^{grid}_\tau=0\)、terminal 只需技術下界 | 這些性質**在 v8 仍成立**，但其 v8 依據是 SPEC §6（AM），**不是** P4 |
| Evidence boundary（R7 不提供 exact equations） | 保留，且對 v8 同樣成立 |
| REG74 L2300 claim-map 列「constant reserve floor + separate outage replay semantics \| P4 + R7 boundary」 | **HIST**（v7.4 範圍） |

P4 之歷史 evidence 角色（A2 exact thesis-method resolution／anti-overclaim record）**完整保留**，可用於描述 v7.4 方法與 v7.4–v8 差異（ART2 §7.5.4-E：兩者為不同研究問題與不同可行域）；**不得**作為 v8 之現行規定。

---

## 5. E-5 — v8 claim-to-source mapping

每列之「方法依據」為 Gate 2 accepted package 位置；「既有證據」只引用 REG74 已有條目，角色以 REG74 所載為限。

| # | v8 claim／設定 | 方法依據 | 角色 | 既有 REG74 證據（角色） | 限制／未核實 |
|---|---|---|---|---|---|
| 1 | Cost–ENS 研究問題：annual cost 與 aggregate ENS 之內生權衡（PV0 固定） | SPEC §3 L83；§7；§6 L180–184；ART2 §7.6 | AM | R1、R2（resilience 改變 sizing／cost，REG74 L2293；LC）；R6、R5（ENS／shortfall 為連續退化指標，REG74 L2298；LC） | 文獻不支持本案 objective 結構、ε 或 denominator；v8 曲面形狀 CONDITIONAL，Pareto knee／成本降低 NOT VERIFIED（ART2 §7.6） |
| 2 | ε-constraint | SPEC §10 L368–395 | AM | — | 外部 attribution NV（§1） |
| 3 | Lexicographic stages 與 numerical certificates | SPEC §10–§11；RES R-02、R-03 | AM＋PD | — | 外部 attribution NV（§1）；targets 可達性 NV（待 Pilot） |
| 4 | EOB0（Branch 0；\(r=1\)） | SPEC §4 Branch 0（L96–99）、§10 | AM＋RA（Branch 0 無 island-forming source 之 branch assumption） | — | 最適性只在 \(F_0\cap X_g\)（ART2 §8-1） |
| 5 | EOB+（\(r_{EOB+}=r_+^*(1)\)） | SPEC §10 | AM | — | 只在 \(F_+(1)\cap X_g\)；EOB+ 不能取代 Global EOB |
| 6 | Global EOB 與 cost premium \(C_+^*(\epsilon)-C_{global}^*\) | SPEC §10 L383–386；L425 | AM | [R1]（resilience premium 概念，REG74 L2294；LC：只支持「islandable capability 有增量成本」） | FW74 §6 之 EOB 與 \(\Delta C(\alpha,\beta)\) 為 **HIST**（不同定義）；v7.4 EOB 數值不得作 v8 Global EOB；EOB+ 不能取代 Global EOB |
| 7 | RES（解析 stage 1 \(r_{min}=0\)；stage 2 min C \| r=0） | SPEC §9.1–§9.2、§10 L388 | AM＋PD（reference construction 證明 zero-ENS 可行） | — | 無 solver 得到之 minimum-cost RES 數值；reference 構造非實機 GFM 驗證（SPEC §9.1） |
| 8 | Aggregate ENS denominator \(r=\sum_sENS_s/D_\Sigma\)；所有合法起點等權 | SPEC L180–184 | AM | R6、R5（ENS 概念；LC） | 文獻不支持 \(D_\Sigma\) 等權 aggregation；\(D_\Sigma\) 不是 annual load；重疊窗口不是實際停電次數 |
| 9 | Outage residual demand 與 recourse：\(Q=\alpha L\)、\(R=\max(Q-V^O,0)\)、PV-first、\(c\le S\)、\(d\le R\)、\(shed=R-d\)、grid import = 0；valid starts 不 wrap | SPEC §6 L154–178；L90 | AM＋RA（perfect event-window foresight；positive branch conditional island-ready assumption） | R4、R5（outage capability 受 load／PV／duration 影響；LC）；R11 boundary（不支持 circular wrap；REG74 claim map）；FW74 §7.2 \([\alpha L-PV]^+\) 運算（v7.4 方法文字，非外部文獻；FW8R2 §8.3 ①） | 不是 inverter／protection／islanding engineering 驗證（FW74 §22-11 前段承接） |
| 10 | Normal-SOC handoff \(e^O_{s,0}=e^N_s\)；事件獨立反事實 | SPEC §6 | AM | R7（preparedness–economic trade-off 概念；LC；§4.1） | P4 不是其依據（§4.2） |
| 11 | Source-binary guards \(X_g\)、classifier、fail-closed | CL1 §4.2–§4.3（經 RES R-01）；SPEC §8.3 L271–275；ART2 §4.2；REC D6、D9 | AM；excluded strip 之必要性 = PD（RES R-04a） | — | Jeroslow–Lowe attribution NV（§2）；全年 Type-3 NV；guard-restricted ≠ unrestricted optimality |
| 12 | Big-M 與 finite bounds | REC D3；RES R-02、R-09；SPEC §9.2–§9.4 | AM＋PD（cost certificate 推得之界） | — | Bound 鬆緊、numeric conditioning、runtime NV（待 Pilot） |
| 13 | Exact billing／Class-C／tariff 方向 | SPEC §8.1–§8.3（F-01）；RES R-04b、R-06；ART2 §5.1、§6、§8-5、§8-6 | AM＋PD（R-04b） | I1（15-min basis；OS）、I2（summer boundary；OS）、I3（tariff source-of-truth；OS）、I4（billed overall max；OS）、P2（κ；site-specific calibration，角色不變） | 方向條件：component 須 \(r_l\ge r_e\)，年度結論須所有 Class-C component 均 \(r_l\ge r_e\)（ART2 §5.1）；L2 transition 為 project rule，不是台電官方完整跨季公式（RA；S12 `OFFICIAL_CROSS_SEASON_AGGREGATION_NOT_EXPLICITLY_LOCATED`）；κ hourly proxy 不是 15-min 量測 |
| 13a | [P5] 在 v8 軌之角色 | 同上；SPEC L286；SPEC §14-7 | — | P5：「solve 後由 optimized hourly proxy profile ex-post 重算 exact maxima」及「exact = calibrated hourly proxy 之 exact maximum」**保留**（並由 SPEC L286 擴及 timestamps、rates、tier 費用、annual cost）；P5「optimization 可使用 cost-facing auxiliary（epigraph）」之條款於 v8 **由 SPEC §8.2 exact MAX contract 取代**（「不可只留 epigraph」），該條款為 **HIST** | REG74 L2350 claim-map 列之 v8 讀法同此 |
| 14 | 10／20 floors 與 floor sensitivity A／B／C | SPEC §4 L101–113、§13 | RA | R1、R2、R4（LC；不提供 floor 數值） | 非工程門檻；華夏網頁不作證據（§3） |
| 15 | Fixed-design／fixed-normal-SOC min-ENS replay | SPEC §11 L427–429 | AM | —（project diagnostic；不需外部 attribution） | **不是** Layer B；R6（Layer B 核心方法文獻）**不**作為此 replay 之依據；v8 Layer B 延後（FW8R2 §2.5） |
| 16 | Degradation mainline 與 ex-post rainflow validation、linear throughput benchmark | FW74 §0.1 B1（L80）、§4.4.3-E（L1194）、§16.1；SPEC §5、§14-6；FW8R2 §6.9 A4–A6 | AM（Xu-derived PWL 於 SPEC §5）＋承接之 v7.4 validation 義務 | R20（Xu PWL；LC）、R31＋R20（rainflow ex-post validation，REG74 L2317；LC）、T4（DOD／cycle-life calibration；OS）、T2（cost package；OS） | 角色不變；rainflow 不嵌入 optimization；cycling economic-wear approximation，不是 physical lifetime prediction |
| 17 | 機率可靠度宣稱之範圍與限制 | SPEC L90、L184、L500；ART2 §7.6；DD §K；REC §6-5 | AM（宣稱限制） | R13（stochastic reliability comparator；本研究刻意不做 outage probability；LC）；R5、R6「不能支持」欄（structured coverage ≠ probability） | \(r\) 為 deterministic aggregate service metric，不是 EENS、LOLP 或年度停電機率；structured-start event-coverage proportion 不稱 reliability；不保證任何未來停電（FW74 §7.11 承接） |
| 18 | Positive-branch PV islanding boundary \(r_{PV}\) | SPEC §12 | EN（前輪 read-only 算術）＋RA（conditional island-ready） | — | 不是 EOB+ optimum；不證明實體 10 kW PCS 對全校 PV 具 GFM 能力 |
| 19 | v7.4 vs v8 比較與 successor 理由 | ART2 §7.5.4-E、§7.6；REC S5(ii) | AM（宣稱限制） | — | RCA 數值為 OBSERVED-relay；原 549 行報告 `ab9aa820…` NOT VERIFIED；差異不可全部歸因於單一變更；不得稱 v7.4 失敗 |

---

## 6. REG74 既有條目之 v8 軌角色註記（只列有變化或需澄清者）

| REG74 條目 | v8 軌角色 |
|---|---|
| [R6] Pickering & Choudhary (2021) | 「ENS／shortfall 為連續退化指標」之概念支持保留（LC）；其「Layer B 核心方法文獻」角色只在 v7.4 Layer B 範圍（v8 Layer B 延後；HIST 至另行定義） |
| [R7] | 見 §4.1 |
| [R12]、[R13] | DG counterfactual 角色隨 v8 DG extension 延後（HIST 至另行定義）；R13 作 stochastic comparator／claim-boundary 之用途保留（§5 第 17 列） |
| [R14]、[R15]、[R17]、[R19] | SOC 10–90% mainline 與 20–80% conservative sensitivity 之角色不變（FW8R2 §6.9-B3） |
| [P4] | 見 §4.2 |
| [P5] | 見 §5 第 13a 列 |
| [P6]、[T2]、[R34] | 10 MW mainline／1 MW 整包 cost-scale sensitivity 角色不變（FW74 §0.1 L83–84；FW8R2 §6.9-B2） |
| [R31]、[R20]、[T4] | 角色不變（§5 第 16 列） |
| REG74 §14「可以寫」中以 all-start／historical-start adequacy 為主詞之句子 | v7.4 範圍；v8 改以 ENS／ε 表述（§5 第 17 列）；不得把 v7.4 adequacy 句子用於 v8 結果 |

其餘 REG74 條目、claim boundary 與 parameter lineage 不變。

---

## 7. 對 acceptance readiness 之影響（彙整）

| 項目 | 本 delta 後之狀態 | 是否 Gate 3 blocker |
|---|---|---|
| E-1 外部 attribution | NV；已限定只由 project specification 支持 | 否（AUD3 §5 所列之「明確限定」路線）；若研究者要求外部 attribution 為接受內容，則是 |
| E-2 外部 attribution | NV；R-04a 為 accepted project derivation | 否（同上） |
| E-3 | 措辭已縮限；floors 仍為 RA | 否 |
| E-4 | R7／P4 之 v8 角色已註記 | 待 targeted audit 確認 |
| E-5 | v8 mapping 19 列（含 13a） | 待 targeted audit 確認 |
| 新文獻檢索 | 未執行；未授權 | — |

---

## 8. Provenance

- 作者：Claude Code session `203b1afd-3311-4f4e-91cd-4547e4f63365`（Opus 5.5）；與 FW8R2 同一作者 session。**本 session 不得擔任本 delta 或 FW8R2 之獨立審查者。**
- 授權：研究者 2026-10-24 Gate 3 補正指令（只授權建立本檔與 FW8R2 兩份 candidate；不授權接受、Activation、Git、Coding、Solver、Pilot、新文獻檢索）。
- 操作：對 §0.1 來源唯讀 SHA-256、`sed`／`grep`；本輪無外部檢索。
- 計數：Existing files modified = 0；REG74 modified = 0；Repository modified = 0；Git mutations = 0；New bibliography entries = 0；Literature retrieval = 0；Model builds = 0；Solver calls = 0；Self-acceptance = 0。
- 本檔不嵌入自身 SHA-256；一經雜湊即不可變，更正以 additive successor 處理（PROT §4–§5）。

**REGISTRY V8 MINIMAL ADDITIVE DELTA — CANDIDATE R1 / NOT ACCEPTED / NOT ACTIVATED / PENDING TARGETED INDEPENDENT AUDIT — REGISTRY V7.4 REMAINS CURRENT EVIDENCE AUTHORITY**
