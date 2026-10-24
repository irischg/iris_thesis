# Iris Thesis — Phase-1 Methodology Specification Acceptance Decision Candidate R1

**日期：2026-10-24（Asia/Taipei）**

> **PROPOSED / NOT ACCEPTED / NOT SIGNED / NOT EFFECTIVE**
>
> **ACCEPTANCE EXECUTION STATUS: HOLD — REQUIRED INDEPENDENT AUDIT PASS OR GOVERNANCE DISPOSITION PENDING**
>
> 研究者在 §F 所列的 conditions precedent 全部關閉之前，**不得簽署**本文件的 §G。

**文件類型：** 研究者審閱用的方法規格接受決定**草案**（Gate 2：Methodology／Specification Acceptance）。本文件**不是** Acceptance Decision Record、不是 Framework v8、不是 Framework v8 的接受或啟用、也不是 Coding／Pilot／Solver／Git 授權。本文件不修改 Spec R2、CL1、RES、Artifact R1／R2 或任何 accepted source 的任何 byte。

**作者：** Claude Code session（scratchpad id `c93e3fb8-1ff6-4dce-ac4f-76ae360653f1`；Opus 5.5）。此 session 並未撰寫 Spec R2、CL1、RES、Artifact R1、Artifact R2 或 MBR，也未審查它們；但它與 Artifact R1／R2 的作者、CL1／RES 的作者、AUD 的審查者使用**相同工具與相同模型**，且 session 開始時已自動載入研究者的 project-memory 索引，並讀取了其中一則（`phase1-v8-acceptance-artifact-r2-candidate`）。因此本 session **不得**擔任本文件的獨立審查者。

---

## A. 接受對象與身分（2026-10-24 本輪以唯讀 SHA-256 重新核對；全部 MATCH）

### A.1 決策對象：Phase-1 方法規格 package

| ID | 完整路徑 | SHA-256 | 角色 |
|---|---|---|---|
| SPEC | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` | 數學規格本體 |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` | Class-C guard 澄清（規範部分見 B.2） |
| RES | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md` | `3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5` | R-01～R-10 勘誤 |
| ART2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R2_Candidate_2026-10-24_DRAFT.md` | `2386d47b96690ac3a8c81673b1c4750e85bce93ef837ce47a75e850cb49f8268` | 待接受的 artifact；TA-01～TA-05、G-01／D12、D8 |

歷史前身（**不是**決策對象）：Artifact R1 `d406bd63ab479121a570203b2f82e947874630be2476efcac42c1a8079d05bab`（FLA = STOP，不可變）；AUD `3ae99b7b5f9672fe79f45aebebdbd746f98a25798c84e8e749afe675f583a3eb`；ART2 identity／diff report `6efc6697aa0d686d4d527f585bae532b633b30b1979e84f5a1c87506020093ae`。

### A.2 具拘束力的治理來源與 accepted history（repo HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；以下檔案皆與 HEAD 一致、無本地修改）

| ID | 路徑 | SHA-256 |
|---|---|---|
| PROT | `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
| CONST | `C:/Users/Iris C/Downloads/Iris_Thesis_Response_Mode_and_Research_Governance_Constitution_2026-10-03.md` | `4f5eaf050d96f84d96e06ebebd53e095f209ad50bb0a0f94a180f2dd0efc9c38` |
| FW74 | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| FW74-C | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` |
| REG74 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| REG74-C | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` |
| PTR | `configs/current_mainline_pointer.json` | `ed7005dea8dc423fb4372554b3f8d15fd34c3988441c4fb14c2dede0d64afcb4` |
| PTR-C | `results/provenance/current_mainline_pointer_acceptance_r2/acceptance_closure.json` | `bf0bb2766d15fd69b27d95436e4375958de1bc98f84dce31b2c1be3249053d71` |
| STATE | `docs/ai_handoff/CURRENT_STATE.md`（L45：v7.4 `CLOSED / ACCEPTED`；全文沒有 Phase-1／v8 條目） | `043711e8bb422bec7e26ea8263a06ffbf4bf7d28af27cefa91b190f2868b327f` |
| XAUD | `docs/ai_handoff/CROSS_AUDIT_PROTOCOL.md`（L24：secondary agent 為「the other of Codex/Claude Code」） | `95f6c967a04c85db06eca0fa593c5665d2693b2f18447b9afa0b515cef640dfd` |

`git status --porcelain` 的雜湊為 `e2c74e09…`（共 16 項），與 ART2 輪的紀錄相同。

### A.3 最新審查：Codex Minimum Blocking Review（MBR）— 身分**未驗證**

| 欄位 | 本輪可證明的內容 |
|---|---|
| 結論 | 「GO — may proceed to a researcher-controlled methodology specification acceptance decision」。**來源：研究者 2026-10-24 的任務指令（轉述）**；本輪未讀到審查原文。 |
| 研究者轉述的四項發現 | (1) 依 PROT §1 可前瞻承接 methodology authority，並保留 v7.4 accepted history；(2) 此 prospective-successor 路線**不需要** PROT §30 amendment；(3) R1→R2 material diff PASS；(4) D8 歷史獨立審查是否充分，仍需研究者明示處置。 |
| 研究者轉述的限制 | 只審查四個治理問題；**沒有**完成 ART2 §11 D8-c 的每一項（包括 FLA／RCA rollout 擷取重現）。 |
| Reviewer／session | 「Codex」— 研究者陳述，**NOT VERIFIED**。`~/.codex/sessions/2026/10/24/` 中唯一的 rollout 為 `rollout-2026-10-24T13-35-58-01a16c68-9773-71f2-b09a-7d68f45c561f.jsonl`（672,748 bytes；2026-10-24T13:57+08:00 的 SHA-256 快照為 `834b3a1da9e15e6b904d01a23651b5787665adc01dcaa1cdfd7b0fa978a880f2`；mtime 等於建立時間，檔案可能仍在寫入）。本輪**沒有讀取其內容**（custody 規則；無額外授權），因此「此 rollout 即為 MBR」**NOT VERIFIED**，其 model、scope 與 verdict 亦 **NOT VERIFIED**。 |
| 正式 verdict 用語 | 「GO」**不是** PROT L683–691 規定的 `<TOPIC> — PASS`。 |

---

## B. 接受對象的實質內容（只引用已審查的 package；不新增方程式、假設或數學決定）

### B.1 方法規格的範圍

| # | 項目 | package 中的定義 |
|---|---|---|
| 1 | 研究問題 | NTUST 既有 PV0（固定；不增加 PV）下，BESS \(P_B\)、\(E_B\) 與單一年度 CC 的 annual **Cost–ENS／ε-constraint** planning（SPEC §3 L83；§10）。 |
| 2 | 內生部分 ENS–年成本權衡 | 服務要求由 aggregate ENS 上限 \(r\le\epsilon\) 決定，取代 v7.4 的 hard all-start reserve／adequacy（SPEC L152、§6、§14-1）。\(r\) 是 deterministic structured-start aggregate service metric，**不是** EENS 或機率 reliability（SPEC L90、L184）。 |
| 3 | α／β 範圍 | α∈{0.10, 0.25, 0.50}、β∈{4, 8, 12} h；valid starts 不跨年、不 wrap（SPEC L89–90）。九組 B2 reference certificates 是**算術證書，不是 Solver 結果**（SPEC §9.3）。Floor sensitivity A／B／C 與 (0.10, 4) 優先計畫：**僅預先登錄，尚未執行**（SPEC §13）。 |
| 4 | 端點與角色 | EOB0（Branch 0）、EOB+（\(r_+^*(1)\)）、Global EOB（lexmin）、RES（解析 stage-1 \(r_{min}=0\)，stage-2 min C \| r=0）、ε-frontier、lexicographic（cost-first、ENS-second；保留完整決策空間）、**fixed-design／fixed-normal-SOC min-ENS replay**（不是 lexicographic tie-break，也不是 Layer B）（SPEC §10、§11 L427–429）。 |
| 5 | 模型適足性與邊界 | Branch 0／Branch +；floors 10 kW／20 kWh 為 **ASSUMPTION**（SPEC §4）。Exact billing／transition（F-01）是**同一 tariff function 的 formulation correction**（SPEC §8；L238）。Class-C source guard 與 τ／g convention（SPEC §8.3；CL1 §4.2–§4.3）。Guard domain \(X_g\)（ART2 §8）。Big-M（ART2 §9-2；RES R-02）。數值 targets 為 proposed，**pending Pilot**（SPEC §11）。 |
| 6 | 宣稱邊界 | ART2 §8（guard-restricted ≠ unrestricted）、§10（residual limitations）、§6.3、§7.6。 |
| 7 | 承接與取代 | 見 §C.3（v7.4-only 項目與繼續適用項目）。 |

### B.2 採納條文與 precedence（**窄範圍**；只在不一致之處適用）

採 ART2 §7.2 的 precedence chain，**不另擴張**：

0. **本 Decision Candidate 本身的規範內容，只限下列三項：** §C.3 中標為 **[DC-NEW]** 的處置列；§D.4 的 D8 分層處置；§D.6 的 D8-c 收尾範圍。除此之外，本文件不覆寫 package 中的任何文字。
1. ART2 採納的修正文字：§3.4–§3.5、§3.7（依本文件 D8 調整）、§4.2、§5.1、§6.1–§6.2、§7.1、§7.5（依 D12）。
2. RES R-01～R-10（依第 1 層修正）。
3. CL1 §4.2（L81–114）、§4.3（L116–123）、§7.4（L257–264）、§9（L287–312）（依 RES 修正）。
4. SPEC 對應段落：§8.3（L259–286）、§9.4（L355–366）、§11（L397–429）。

**SPEC 其餘內容全部不變**（§1–§7、§8.1–§8.2、§9.1–§9.3、§10、§12–§17）。SPEC §10 不被覆寫（ART2 §7.3）。CL1 中非規範章節的地位依 ART2 §7.4。Artifact R1 **不在** chain 內。

---

## C. G-01／D12 — 前瞻方法承接（PROPOSED）

### C.1 擬議的治理立場

1. v8 Cost–ENS／ε-constraint 是**新的研究問題**，在方法上前瞻承接 v7.4，不是 implementation correction，也不是錯誤修正（ART2 §7.5.2）。
2. Framework v7.4 與 Registry v7.4 在其原始假設下維持 **CLOSED / ACCEPTED** 的歷史效力（FW74-C；REG74-C；STATE L45）。本決定不主張、也未證明 v7.4 有任何程式、資料、公式、source transcription 或 provenance 錯誤。
3. **權源：** PROT §1 L34「Unless explicitly superseded by a later accepted artifact」允許經明示接受的後續 artifact **前瞻**取代 methodology source of truth（MBR 發現 1，轉述）。
4. PROT §2（L61–79）、FW74 §0.1 L66、CONST §7（L251–266）繼續保護歷史上的 CLOSED 決策。本決定**不**建立任何一般性的「不理會 CLOSED 決策」的權利。若有人將本承接解讀為受上述條款限制，本決定只就 §C.3 列為 **REPLACED** 的項目構成本案限定處置（ART2 §7.5.4-B (3)）。
5. **PROT §30：** 依 MBR 發現 2（轉述），此 prospective-successor 路線不需要修訂 Protocol。這項結論**只適用於本案**；它不推論其他未來案件也不需修訂，也不改變 PROT v1 的任何文字。
6. **規格接受不等於 Framework v8 接受。** 本決定（Gate 2）**沒有**自動啟用條款。Framework v8 必須另經撰寫授權 → 撰寫 → 獨立審查 PASS → 研究者正式接受（Gate 3）→ 明示 Activation，才能成為 current methodology authority（ART2 §7.5.4-D）。在 Activation 之前，v7.4 是唯一的 current accepted methodology／evidence authority（ART2 §7.5.5）。

### C.2 D12 採納文字

研究者如核准 D12，即**逐字**採納 ART2 §7.5.4-A（FLA 建議文字）、§7.5.4-B（研究者授權文句；Decision Record 須填入 ART2 SHA `2386d47b…8268`）、§7.5.4-D（兩階段接受與 Activation）、§7.5.4-E（歷史保留）、§7.5.4-F（不授權事項）。§7.5.4-C 則依下方 §C.3 補充。

### C.3 v7.4 歷史限制的處置

標記說明：**v7.4-ONLY** = 只在 v7.4 有效，v8 不繼承；**CONTINUES** = 對 v8 繼續適用；**[ART2]** = ART2 §7.5.4-C 已列；**[DC-NEW]** = ART2 留給 D8-c 審查或未列、由本文件提出，**須經 §D.6 窄範圍審查**。

| v7.4 條款 | v7.4-ONLY（v8 不繼承） | CONTINUES（對 v8 繼續適用） | package 依據 | 標記 |
|---|---|---|---|---|
| §0.1 **L70** | dense 9×9 grid；以所有 valid starts 的 worst-case reserve 作為服務要求 | valid starts 不跨年、不 circular wrap（SPEC L90） | SPEC L89、L152、L464 | [ART2]；「繼續適用」欄為 [DC-NEW] |
| §0.1 **L72** | 「normal-operation reserve 必須位於 technical SOCmin 之上」這一句的**reserve 要求**：v8 沒有 reserve floor，所以這個條件沒有適用對象，**不帶入**任何 reserve | \(SOC_{min}=0.10\)、\(SOC_{max}=0.90\)、\(E^U=0.8E^N\) 的技術界限與 usable-energy 意義（normal 用 SPEC L131；outage 用 SPEC L176） | SPEC L131、L152、L176 | **[DC-NEW]**（ART2 L435 留給審查） |
| §0.1 **L74**（A2） | annual／outage 分離成兩個 stage；constant worst-case reserve floor；replay 從最低 preparedness state 開始 | —（v8 改為 normal SOC handoff 的 PV-first outage recourse，並把各端點分開，SPEC §6、§14-3、§14-5） | SPEC L152、L466、L468 | [ART2] |
| §0.1 **L87** | — | Layer B 的歷史角色（固定 Layer A 設計、不重新擴充設備；structured scenarios 不是可靠度機率）繼續保留。**Phase-1 的 outage recourse 與 fixed-design replay 都不是 Layer B，也不自動授權任何新的 Layer B 工作**；v8 下的 Layer B 須在 Gate 3 另行定義並經審查。 | SPEC §6、L427–429 | **[DC-NEW]**（ART2 L435 留給審查） |
| §0.1 其他鎖定項（L68–69、L71、L73、L75–86、L88–90） | — | 全部繼續適用；SPEC §14-6 明示不改效率、SOC、monetary basis、κ evidence route、PNNL cost／Xu semantics | SPEC L469 | [ART2] |
| **§7.3–§7.5**（L1415–1514） | 外生 valid-start energy reserve \(R(\alpha,\beta)\)、瞬時 power adequacy、全年 reserve floor，以及由此導出的 \(E^N\)／\(P^B\) 下限 | — | SPEC L152 | [ART2] |
| **§7.7**（L1535–1598） | normal bound 中的 \(+R(\alpha,\beta)\) 項；「LP-first，只有 audit 發現同時充放電時才加 binary」的主線偏好（v8 改採 strict hourly binary，SPEC §5 L122–127、§14-2） | \(\eta_c=\eta_d=0.90\) 且只套用一次；\(t\to t+1\) 的 state transition；technical SOC window；年度 cyclic boundary \(e_T=e_0\)；Xu segment 的 periodic boundary（SPEC L129–145） | SPEC §5、§14-2 | **[DC-NEW]**（§7.7 不是 §0.1 鎖定項；為避免取代未被記錄而列出） |
| **§7.10**（L1749–1825） | A2 分離式 replay；\(e_0=SOC_{min}E^N+R\)；Layer A analytical-consistency replay 禁止 PV recharge（v8 outage 允許 \(c\le S\)，SPEC L165） | outage grid import = 0；outage 期間只維持技術界限；「不得描述為未來停電保證或可靠度機率」（SPEC L90、L184 同義） | SPEC §6 | **[DC-NEW]**（屬 L74 的實作展開） |
| **§7.11**（L1827–1843） | 正向保證句「每個 valid start 都滿足 modeled energy and power adequacy」（v8 允許部分 ENS，**不可**沿用此句） | 「不可寫 guarantees any future outage」，以及未納入因素清單（load／PV 分布改變、設備故障、網路限制、degradation 造成的容量損失、停電機率） | SPEC L90、L184、L500 | **[DC-NEW]** |

其他規則：

- ART2 §16-7 不變：若之後發現 SPEC 與上表以外的 v7.4 §0.1 鎖定內容衝突 → **STOP**，不得以本處置涵蓋。
- 上表**不修改** FW74 的任何 byte；「v7.4-ONLY」意指這些要求在其原始研究問題下繼續有效，v7.4 及其結果的歷史解讀不變。

---

## D. D8 — 接受前的審查充分性控制（關鍵未決項）

### D.1 審查盤點（如實記錄）

| 層 | 審查 | 對象 | Reviewer | 跨工具 | 跨模型 | Verdict | Custody／限制 |
|---|---|---|---|---|---|---|---|
| H1 | SPEC Independent Static Audit | SPEC | Codex `01a16701…`（轉述） | NO（推定 Codex→Codex） | NO（推定） | CONDITIONAL PASS（轉述） | 只有對話紀錄，未讀；作者 session 為推定 |
| H2 | CL1 Targeted Static Audit | CL1 | Claude Code `180c3fec…`（轉述） | NO | NO | CONDITIONAL PASS（轉述） | 只有對話紀錄，未讀 |
| H3 | RES Targeted Audit（AUD） | RES | Claude Code `fd2b5546…` | NO | NO | CONDITIONAL PASS | 有檔案（`3ae99b7b…`） |
| L1 | Final Limited Audit（FLA） | ART R1 的 TA parity、G-01、D8、precedence | Codex `01a16974…`（rollout 紀錄為 `gpt-6-astra`） | YES | YES（依 rollout 紀錄；backend 未驗證） | **STOP**（G-01） | 由 operator 擷取（`4090e75a…`）；尚未獨立重現 |
| L1b | **MBR** | 四個治理問題（§A.3） | Codex（研究者陳述）；session **NOT VERIFIED** | 推定 YES | NOT VERIFIED | **GO**（不是 PASS） | 本輪未讀原文；身分見 §A.3 |
| L2 | — | ART2 的 `[R2-NEW]` 條文全體 | — | — | — | **ART2 §11 D8-c 要求的 fresh targeted audit 尚未完整執行** | MBR 只涵蓋其中一部分（§D.5） |
| L3 | — | 本 Decision Candidate 的 [DC-NEW] 條文 | — | — | — | **尚未審查** | — |

### D.2 GO 不等於正式 PASS

- PROT §3（L87–95）規定 acceptance 的路徑是 **INDEPENDENT READ-ONLY AUDIT → PASS → CLOSED / ACCEPTED**；PROT L689–691 規定「Only an independent PASS may additionally state `<TOPIC> — CLOSED / ACCEPTED`」。
- ART2 §11 D8-c 將 fresh targeted audit 的明確 PASS 定為**強制、沒有替代選項**；ART2 §16-4 規定審查結果不是明確 PASS 時，不得記錄 D1。
- MBR 的 GO 是「可以進入研究者決策」的許可，**不是** D8-c 要求的 PASS。它的「R1→R2 material diff PASS」只是一個子發現，最多可對應 D8-c 第 1 項（須先取得 MBR 的可驗證紀錄，§D.6-S2）。

### D.3 歷史審查與未驗證身分

- H1–H3 是**同工具**審查（推定 Codex→Codex，或 Claude Code→Claude Code），只具 session independence。L1（FLA）與 L1b（MBR）是後來的**跨工具**審查，但範圍有限，**不能**延伸為 SPEC、CL1、RES 的跨代理重審。
- 未直接驗證的身分：H1／H2 的報告原文與作者 session；SPEC 作者 session；MBR 的 session、model 與原文；Root-Cause 原上傳副本 `ab9aa820…`（549 行，至今未找到）；FLA／RCA 擷取副本與 Codex 原交付之間的同一性（只是可依方法重現，尚未由獨立者重現）。

### D.4 擬議的本案專屬充分性處置（D8-a；PROPOSED）

研究者如核准，即就**本次 Phase-1 方法規格接受**明示認定下列事項：

1. H1–H3（session-independent、同工具）、L1（FLA；有限跨代理）與 L1b（MBR；有限跨工具），**連同 §D.6 的窄範圍 PASS**，合起來足以作為 PROT L736、L803 所稱的獨立審查。在工具層級的讀法下，此認定構成對 L736、L803 的**本案限定例外**，範圍只限 §A.1 四份文件與本 Decision Candidate。
2. §D.3 所列的未驗證身分，研究者**明示接受為已揭露的限制**。它們不得被描述為已驗證，也不得被 Framework v8 引為 primary evidence。
3. **Pointer R2 的先例不適用。** PTR-C L95–108 是 governance／authorization change 的單案例外，且明示不是「SCIENTIFIC METHODOLOGY CHANGE」。本處置是**新的、另行核准**的本案決定，不援引、也不延伸該先例。
4. **研究者核准本身不能補足強制的獨立性缺口。** 研究者是唯一的 acceptor（PROT L95、L322），但 PROT §3／L689–691 的 PASS 要件不因研究者核准而消失。本文件也**不**提議研究者對 PASS 要件本身作例外：那會是性質不同、須另行審查的治理行為，且不會比 §D.6 更短。
5. D8-b：「依額度選擇 Codex 或 Claude Code」只記錄為研究者立場，**沒有常設效力**；若要成為常設規則，須依 PROT §30 另行修訂。

### D.5 本文件採納條件與 ART2 D8-c 的實質差異

| # | ART2 原條件 | 本文件的擬議內容 | 是否實質 |
|---|---|---|---|
| M1 | L72 的處置由 D8-c 審查判定（ART2 L435） | §C.3 L72 列 | 是 |
| M2 | L87 的處置由 D8-c 審查判定（ART2 L435） | §C.3 L87 列 | 是 |
| M3 | §7.5.4-C 只列 §0.1 與 §7.3–§7.5 | 增列 §7.7、§7.10、§7.11 的 v7.4-only／continues 處置，以及 L70「繼續適用」欄 | 是（說明性，但仍屬新的規範文字） |
| M4 | §3.7 的分層中沒有 MBR | 增列 L1b（MBR），並調整 D8-a 的充分性處置 | 是 |
| M5 | §7.5.3-3 的例外權源由 D8-c 審查裁定 | 採用 MBR 發現 1、2（轉述）作為裁定 | 是（MBR 須先取得可驗證紀錄） |
| M6 | D8-c 為一次完整的 fresh targeted audit | 改為「MBR 已涵蓋部分 + 剩餘項目 + M1–M5」合併為一次窄範圍審查（§D.6） | 是 |

依 ART2 §16-5，Decision Record 引入 ART2 未涵蓋的新規範文字時，該部分**須另行 targeted review**。所以 M1–M6 必須進入 §D.6 的審查範圍。

### D.6 最小收尾要件（唯一需要的額外審查）

**一次** fresh、獨立、唯讀的窄範圍 targeted audit。其最終 verdict 必須恰好是下列其一：

`PHASE-1 METHODOLOGY SPECIFICATION ACCEPTANCE DECISION CANDIDATE R1 — PASS`
`PHASE-1 METHODOLOGY SPECIFICATION ACCEPTANCE DECISION CANDIDATE R1 — STOP`

**Reviewer：** 不得是 Artifact R1、Artifact R2、本文件或 MBR 的作者。依 PROT L324–327 與 XAUD L24，建議用 **Codex**（本文件作者為 Claude Code）。若改用 Claude Code fresh session，須如實標記為 session-independent、非 cross-model，並列入 §D.4-1 的例外範圍。

**審查範圍（只限以下各項）：**

- **S1 身分：** §A.1 四份文件、Artifact R1、本 Decision Candidate 的 SHA-256；以及 SPEC／CL1／RES／ART2 自 2026-10-24 以來未被修改。
- **S2 MBR 紀錄：** MBR 原文須以可雜湊的形式提供給 reviewer（由研究者提供檔案，或由研究者授權 reviewer 讀取 rollout `01a16c68…`），並核對 §A.3 轉述的四項發現與限制和原文一致。**若 MBR 原文無法取得 → M5 不成立，§7.5.3-3 的裁定改由本審查直接作出。**
- **S3 M1–M6：** §C.3 中 [DC-NEW] 各列對 FW74 §0.1 L68–90、§7.3–§7.5、§7.7、§7.10、§7.11 與 SPEC 原始 bytes 的正確性與完整性；確認沒有新增方程式或假設；確認 R1 的 candidate-only 文字沒有殘留為規範。
- **S4 ART2 D8-c 的剩餘項目（MBR 未涵蓋者）：** 第 3 項（§3.7 的獨立性表與 FLA／AUD 一致）；第 4 項（ART2 §7.6 的數值與 RCA 擷取文字一致；沒有「扁平」、knee、成本降低或 unrestricted optimality 的宣稱）；第 6 項（D1–D12 一致、沒有自我接受、沒有 v8 升格）。
- **S5 custody（ART2 D8-c 第 5 項）— 研究者擇一：**
  - (i) **〔建議〕**授權 reviewer 依 ART2 §1.6 的方法，由 FLA／RCA rollout 重現擷取 SHA（`4090e75a…`、`cf2bb7fa…`）。此步驟是決定性且成本低的。
  - (ii) 不重現：FLA／RCA 維持「operator-extracted、未經獨立重現」。此時 FLA-VERBATIM 文字只以研究者採納的規範文字身分生效，RCA 數值只以 OBSERVED-relay 等級引用。選 (ii) 本身就是對 D8-c 第 5 項的降級，須由 reviewer 確認沒有任何採納條款依賴已驗證的身分。

**明確排除在範圍外：** SPEC 數學、CL1 guard 公式、TA-02～TA-05 的內容、Big-M baseline、D6 規則、Type-3、Class-C、B1–B4、Root-Cause 與 Full81 的重新分析、solve。

**結果處理：**

- **PASS** → §F 的 CP-2、CP-3 關閉。
- **STOP 或 CONDITIONAL PASS** → 不得簽署。以 additive 的 **Decision Candidate R2** 修正，只重審修正部分；**不**重寫 SPEC、**不**建 Resolution R3。若 STOP 指向 ART2 本身的條文 → 改建 Artifact R3（ART2 §16-3）。

---

## E. D1–D12 擬議決定（全部 **PROPOSED**；研究者尚未核准任何一項）

| ID | 決策主題 | 擬議選擇 | 依據 | 研究者核准的實質內容 | 未決條件 |
|---|---|---|---|---|---|
| **D1** | 方法規格接受（Gate 2） | **接受** SPEC + CL1 + RES + ART2（含本文件 [DC-NEW]），作為 guard-restricted 的 Cost–ENS／ε-constraint **v8 方法規格** | ART2 §11 D1；§7.5.4-D | 該規格成為「已接受的 v8 方法規格」，可作為 Gate 3 起草依據。**這不是 Framework v8 接受，也不是 current authority。** | **HOLD**：§D.6 PASS；D8、D12 先核定 |
| **D2** | Precedence | 依 §B.2（窄範圍；SPEC §10 不覆寫） | ART2 §7.2–§7.4；AUD §B.1 | 只在明列的不一致範圍內優先；SPEC 其餘內容不變 | 無（第 0 層 [DC-NEW] 待 §D.6） |
| **D3** | Big-M | **Baseline**：\(M_{ch}=\bar P\)；\(M_{dis,t}=\min(\bar P,L_t)\) 或共同 \(\min(\bar P,L_{max})\) | RES R-02；ART2 §9-2 | 實作採用 baseline。CL1 L299–303 的 tightening 已證明有效，但**不選用**，日後改用須研究者另行選定。任何其他更緊的界須依 R-02／R-09 另經有效證明並核定；只對 stage-1 argmin 成立的界不得用於 stage-2 | 無 |
| **D4** | Guard-restricted 最適性宣稱 | 接受 ART2 §8（CL1 §7.4，經 R-03、R-07 修正） | AUD 矩陣 PASS | 最適性只在 \(F\cap X_g\) 上成立；2.001 NTD 的誤差界只相對於 \(C^*_{guard}\)；**不得**標示為 unrestricted global optimality | 無 |
| **D5** | Tariff 方向與 source scope | 接受 ART2 §5.1（TA-03）與 §8-5 | RES R-04；TA-03 | 閉合計價只在 component 層級精確；年度層級精確須所有 Class-C component 同向（現行 October 不滿足）。Canonical source pricing 只是 accepted case formulation，L2 是 project rule，不能擴張為台電的通用規定 | 無 |
| **D6** | PV0 Pilot fail-closed | 採 ART2 §4.2：UNRESOLVED 或 certificate failure → **STOP／REPORT／PRESERVE DIAGNOSTICS** | TA-02；FLA PASS | 只是 Pilot 的**入口前置條件**；不得改標籤、放寬或重跑消除。**沒有 Pilot 授權** | 無 |
| **D7** | Strict 與 τ-convention 的宣稱邊界 | 接受 ART2 §6、§8-6 | RES R-06；TA-04 | 報告 τ-convention 帳單並加以揭露；\(0<d\le\tau\) 時兩者差額為 \((r_e-r_l)W\)；0.054 NTD 是**最適值之間**的條件界，NOT VERIFIED；EXP5b 的觀察寫成 d=0 | 無 |
| **D8** | 審查充分性 | §D.4（D8-a 本案專屬處置）；D8-b 只記錄立場；**D8-c 依 §D.6 收尾** | PROT §3、L689–691、L736、L803；ART2 §3.7、§11 | 如實記錄的有限審查覆蓋範圍 + 本案限定例外 + 必要的窄範圍 PASS | **HOLD**：§D.6 PASS；S5 的選擇 |
| **D9** | Type-3、classifier | 全年 Type-3 certification **NOT VERIFIED**；classifier 修改 **NOT AUTHORIZED** | RES §8；CL1 §10 | 不授權 | 無 |
| **D10** | 文件承接方式 | 保留 SPEC／CL1／RES／ART2 + 本 Decision Candidate；**不建** Resolution R3 或 Spec R3 | AUD §D；FLA | 不新增平行文件；只有在審查 STOP 時才建 additive successor（§D.6） | 無 |
| **D11** | Temp／對話證據的 durable 保存 | **本決定不授權**；研究者可**另行**明示選擇提前授權（範圍見 ART2 §11 D11） | ART2 §10-11 | 不核准（除非研究者另行 opt-in） | Temp 實驗目錄有被 Storage Sense 清除的風險（ART2 §10-11）— 建議研究者盡早另行決定 |
| **D12** | 前瞻 v8 承接與 v7.4 歷史保護 | **D12(a)**：依 §C 與 ART2 §7.5.4-A/B/D/E/F；§7.5.4-C 依 §C.3 補充；PROT §30 本案不需要 | PROT §1 L34、§2；MBR 發現 1–2（轉述） | 前瞻承接 + 本案限定 CLOSED 處置；**沒有自動啟用**；v7.4 歷史不變 | **HOLD**：§D.6 的 S2／S3 |

**建議的核准順序：** §D.6 PASS → D12 → D8 → D1 → D2–D7、D9、D10 →（另行）D11。

---

## F. Conditions precedent 與未決事項

| CP | 條件 | 狀態 |
|---|---|---|
| CP-1 | 簽署當下重新核對 §A.1 四份文件與本文件的 SHA-256；任一不符即 STOP（PROT L707） | 簽署時執行 |
| CP-2 | §D.6 窄範圍 independent audit 得到明確 `— PASS` | **OPEN** |
| CP-3 | MBR 的可驗證紀錄（§D.6-S2），或 MBR 不可得時由 §D.6 直接裁定權源 | **OPEN** |
| CP-4 | 研究者選擇 §D.6-S5 的 (i) 或 (ii)；選 (i) 時，另行授權 reviewer 讀取 FLA／RCA rollout | **OPEN** |
| CP-5 | 若需要讀取 rollout `01a16c68…`、`01a16974…`、`01a16946…`，須由研究者另行授權 | **OPEN** |

**接受後仍保留的事項（不阻擋 Gate 2）：**

- ART2 §10 所列的 residual limitations 全部保留。
- 入口文件落後：PROT §1 L36–40、§28 仍寫 v7.2；CLAUDE.md L9–11 仍寫 v7.3（ART2 §7.5.3-5）。不得據此把權威退回 v7.2／v7.3；是否更新屬 Gate 3 的另行授權事項。
- CURRENT_STATE 沒有 Phase-1 條目；repository 收錄須另行授權。

---

## G. 接受決定（**NOT EXECUTED — 不得簽署**）

> **ACCEPTANCE EXECUTION STATUS: HOLD — REQUIRED AUDIT CLOSURE PENDING**

CP-1～CP-4 關閉後，研究者以一份**簡短的** Acceptance Decision Record 執行本決定。該 Record 只記錄下列內容，**不得新增規範文字**（ART2 §16-5）：

| 欄位 | 值 |
|---|---|
| 本 Decision Candidate 的 SHA-256 | （交付回覆提供；Record 填入） |
| §D.6 audit 的 reviewer、session、artifact SHA、verdict 行 | （待審查） |
| D1–D12 的選擇（逐項：核准／修改／否決） | （待研究者決定） |
| ART2 §7.5.4-B 的授權文句（逐字） | （待研究者決定） |
| S5 的選擇 | （待研究者決定） |
| 決定日期與生效日 | （待研究者決定）；生效只代表 Gate 2，**不是** v8 Activation |
| 研究者簽署 | （空白） |

本文件一經雜湊即不可變，不會就地改為 ACCEPTED（PROT §4–§5）。

---

## H. 另行授權：Framework v8 Candidate 撰寫（**OPTIONAL；NOT GRANTED**）

| 選項 | 內容 |
|---|---|
| H-a〔建議〕 | Gate 2 執行後，授權撰寫一份 additive Framework v8 Candidate（Registry 只做必要的 delta；變更摘要放在 Framework 附錄）。該 Candidate 須經獨立審查 PASS 並由研究者正式接受（Gate 3）後，才可另行 Activation。 |
| H-b | 在 Gate 2 之前先行起草（只是撰寫，不是接受）。若 Gate 2 的條款有變，草稿必須跟著改；不得引用為 accepted 規格。 |
| H-c | 暫不授權。 |

勾選任何一項，都**不**授權 Activation、Coding、Pilot、Solver 或 Git。

---

## I. 限制（本決定在任何狀態下都不授權）

Git add／commit／tag／push；CURRENT_STATE、canonical pointer 或 CLAUDE.md 的更新；Framework v8 的接受或 Activation；Protocol revision；legacy code／data reuse audit；Coding；PV0 Pilot；任何 model build 或 Solver；Type-3；classifier 修改；修改 v7.4 Framework／Registry／Full81／EOB 結果或任何歷史 bytes；把 v7.4 描述為失敗、無效或已撤銷。

## J. 後續必要流程

§D.6 audit PASS → 研究者簽署 Gate 2 Record → （另行授權）Framework v8 Candidate → 獨立審查 PASS → 研究者正式接受（Gate 3）→ 明示 Activation 紀錄（例如 canonical pointer successor，形式於 Gate 3 決定）→ （另行授權）Git 保存。**每一步都不會自動觸發下一步。**

---

## K. 科學理由與宣稱限制（等級依現有證據；不重做分析）

- v7.4 的 81 案年度總成本與韌性增額成本**並非扁平**；worst-case adequacy 強烈影響 sizing 與成本。約 **14,297.98 NTD-2023／年**是 81 案**正常營運成本合計**的全距，**不是**各成本分項的全距。（RCA 擷取文字轉述；未由 Full81 primary outputs 重算；原 549 行報告 `ab9aa820…` 的 bytes **NOT VERIFIED**；RCA 擷取文字也**不可**視為該原始報告。）
- v8 探索內生的 Cost–ENS 權衡；**不**證明 v7.4 無效；**不**保證 Pareto knee、成本降低或經濟優勢；**不**證明 reserve floor 是唯一成因。
- Deterministic aggregate ENS ≠ probabilistic EENS。
- Guard-restricted optimality ≠ unrestricted global optimality。
- 新舊比較屬於不同研究問題、不同可行域，差異不可全部歸因於單一變更（ART2 §7.5.4-E、§7.6）。

## L. 本文件的 provenance

- 本輪唯一新增的檔案就是本檔（位於 repository 之外）。
- 只做唯讀操作：SHA-256、`ls`、`grep`、`awk`、`git rev-parse`、`git status --porcelain`、`git diff --quiet`。
- 只讀取了 Codex rollout 的**檔名、大小、mtime 與 SHA**，沒有讀取任何 transcript 內容。
- 計數：Existing files modified = 0；Repository modified = 0；Git mutations = 0；Memory writes = 0；Framework v8 = 0；Acceptance Decision Record = 0；Model builds = 0；Solver calls = 0；Coding = 0；Self-acceptance = 0。
- 本檔不嵌入自身的 SHA。

**PROPOSED / NOT ACCEPTED / NOT SIGNED / NOT EFFECTIVE — HOLD — REQUIRED INDEPENDENT AUDIT PASS OR GOVERNANCE DISPOSITION PENDING**
