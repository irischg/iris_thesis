# Iris Thesis — Phase-1 Methodology Specification Acceptance Decision Record

**日期：2026-10-24（Asia/Taipei）**

> **PHASE-1 METHODOLOGY SPECIFICATION — ACCEPTED（Gate 2 only）／RESEARCHER DECISION RECORDED／EFFECTIVE 2026-10-24**
>
> 本 Record **不是** Framework v8、**不是** Framework v8 的接受或 Activation、**不是** current methodology authority 的變更，也**不是** Coding／Pilot／Solver／Git 授權。Framework v7.4 與 Registry v7.4 仍是唯一的 current accepted methodology／evidence authority（ART2 §7.5.5）。

**接受者：** 研究者 Iris（PROT L95、L322；唯一 acceptor）。
**記錄者：** Claude Code session `414ae497-0221-4ddf-aca4-5eb94803643e`（Opus 5.5），依研究者 2026-10-24 本 session 中的明示書面核准與建立授權記錄。記錄者不是接受者、不是任何受接受文件的作者，也不是本案獨立審查者；與 Decision Draft、Artifact R1／R2 的作者使用相同工具與模型。
**核准方式：** 研究者於本 session 以書面文字明示核准；本 Record 未另附手寫或電子簽名。

本 Record 只記錄身分、審查、研究者決定與適用效力；**不新增規範文字**（ART2 §16-5；Decision Draft §G）。凡下文引用之條款，以所引文件之原始 bytes 為準。

---

## 1. 文件身分（CP-1；建立本 Record 前於 2026-10-24T14:55:39+08:00 以唯讀 SHA-256 重新核對；全部 MATCH）

### 1.1 受接受的方法規格文件

| ID | 路徑 | SHA-256 |
|---|---|---|
| SPEC | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` |
| RES | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md` | `3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5` |
| ART2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R2_Candidate_2026-10-24_DRAFT.md` | `2386d47b96690ac3a8c81673b1c4750e85bce93ef837ce47a75e850cb49f8268` |

### 1.2 決策文件

| ID | 路徑 | SHA-256 |
|---|---|---|
| DD | `C:/Users/Iris C/Downloads/Iris_Phase1_Methodology_Specification_Acceptance_Decision_Candidate_R1_2026-10-24_DRAFT.md` | `ac0728d9d8eb33efdc92b2866bd1f87c709710e53c6e75b7b030313f100c04b7` |

DD 中具規範效力的內容，僅限 DD §B.2 第 0 層所列三項：§C.3 中標為 [DC-NEW] 的處置列、§D.4 的 D8 分層處置、§D.6 的 D8-c 收尾範圍。

### 1.3 其他已核對身分（未變動；不是決策對象）

Artifact R1 `d406bd63ab479121a570203b2f82e947874630be2476efcac42c1a8079d05bab`（FLA = STOP，不可變）；AUD `3ae99b7b5f9672fe79f45aebebdbd746f98a25798c84e8e749afe675f583a3eb`；PROT `docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696`；repo HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；`git status --porcelain` 雜湊 `e2c74e093887272558d88751adb7668fe0b5023c1fa3959793b983341c277f1c`（16 項）。DD §A.2 其餘治理來源已於同日稍早核對 MATCH。

---

## 2. 獨立審查（DD §D.6）

| 欄位 | 值 |
|---|---|
| Reviewer | Codex；session id `01a16c85-e067-7d10-876d-1ecee7013070`；originator `codex_vscode`；cli `0.162.0-alpha.17.2`；`turn_context` 記錄 model `gpt-6-astra`、effort `high`（實際後端未驗證） |
| 獨立性 | 與 MBR（`01a16c68…`）、FLA（`01a16974…`）為不同 session；DD、ART1、ART2 作者為 Claude Code → 跨工具審查 |
| Transcript | `C:/Users/Iris C/.codex/sessions/2026/10/24/rollout-2026-10-24T14-07-55-01a16c85-e067-7d10-876d-1ecee7013070.jsonl`；776,470 bytes；SHA-256 `7de537ef85d869cf99f009483fe4e24d743c3c44c4d47d6c10b1f7e2fa9de28d` |
| Final answer | rollout 第 142 行；`2026-10-24T06:16:57.457Z`；7,303 bytes（UTF-8）；**SHA-256 `cb6d6e459127ebca93f4d82d2ed95a5bda68d34bf059db74d50e90c41393ee64`**；與 `task_complete.last_agent_message` 完全相同 |
| Verdict（原文，未改寫） | `DECISION DRAFT FINAL INDEPENDENT AUDIT — PASS`（報告 L1） |
| 受審對象 | DD `ac0728d9…c04b7`（報告 L11），以及 ART2、SPEC、CL1、RES（報告 L12–15） |
| 範圍 | 只限 S1–S5；不代表 Spec 數學經本輪重新審查（報告 L3） |
| 報告自述的未涵蓋事項 | MBR 原文未取得（L21）；歷史 session 真實身分未全面驗證（L54）；RCA 只比對擷取副本、未升格為 primary verification（L55）；D8-c 第 5 項 rollout 重現未執行（L56）；`ab9aa820…` 同一性未驗證（L63） |
| Custody | operator-extracted：研究者 2026-10-24 單次授權，以 `python -I` 解析 rollout，只取 `final_answer`、`session_meta`、`turn_context`。擷取副本位於記錄者 session scratchpad（`%LOCALAPPDATA%\Temp`，**非 durable**），可依同法由 transcript 決定性重現 |

---

## 3. Conditions precedent（DD §F）

| CP | 狀態 | 依據 |
|---|---|---|
| CP-1 | **CLOSED** | §1 重新核對，全部 MATCH |
| CP-2 | **CLOSED（研究者程序處置）** | §2 之獨立 PASS；處置見 §3.1 |
| CP-3 | **CLOSED** | MBR 原文不可得，依 DD L185 之替代路徑由本次審查直接裁定權源：報告 L27、L29、L41（M5 PASS）——Protocol §1 前瞻 successor 路線可行，「此限定路線不需要 §30 一般修訂」，不產生任意重開 CLOSED 決策的權利。審查未裁定權源不足（ART2 §16-4） |
| CP-4 | **CLOSED** | 研究者選擇 S5 (ii)（§4.4）；reviewer 判定 (ii) 可接受（報告 L66），且未代研究者選擇（L68） |
| CP-5 | **CLOSED（限本案）** | 研究者僅單次授權讀取 rollout `01a16c85…`；`01a16c68…`、`01a16974…`、`01a16946…` 本輪未讀取 |

### 3.1 CP-2 研究者程序處置（研究者原文）

> 我確認，原 verdict 的 TOPIC 與 Draft §D.6 所列精確字串不同，且位於報告開頭，而非末行。
>
> 鑑於現行 binding Protocol 未要求本案使用特定 TOPIC，而受審對象已由 SHA 唯一綁定，我認定上述差異屬非實質程序差異。
>
> 我明確決定，本案方法規格接受採用已完成的原始 Codex 獨立 PASS，並以 Protocol 的實質獨立性要求及 Draft §F CP-2 為接受依據；不將尚未接受的 Draft §D.6 特定 TOPIC 字串作為額外的生效必要條件。
>
> 本處置不改寫原始 verdict、不創造新的 PASS、不修改已接受 Protocol，亦不建立一般先例。

條文背景（記錄用）：PROT §26（L671–691，「Default Final Verdict Format」）規定獨立審查「should end with exactly one」`<TOPIC> — PASS`，未指定 TOPIC 字串；DD §D.6 所列字串為 `PHASE-1 METHODOLOGY SPECIFICATION ACCEPTANCE DECISION CANDIDATE R1 — PASS`。

---

## 4. 研究者決定（D-register；選項定義依 DD §E 與 ART2 §11）

| ID | 決定 | 定義來源與限制 |
|---|---|---|
| **D12** | **(a) 核准** | DD §E D12、§C.1–§C.3：依 PROT §1 前瞻 v8 methodology successor；逐字採納 ART2 §7.5.4-A、-B、-D、-E、-F；§7.5.4-C 依 DD §C.3 補充（DD §C.2）。v7.4 歷史 CLOSED／ACCEPTED 效力完整保留；PROT §30 本案不需要，且不修改 Protocol；不建立常設或一般 CLOSED 豁免；沒有自動啟用。§7.5.4-B 見 §5 |
| **D8** | **D8-a 核准（DD §D.4 本案限定充分性處置）**；D8-b 僅記錄為研究者立場、無常設效力（DD §D.4-5）；D8-c 依 DD §D.6 以 §2 之 PASS 收尾 | 研究者明示知悉並接受：H1–H3 為歷史同工具審查；FLA／MBR 覆蓋有限、身分未驗證；§2 PASS 只涵蓋 S1–S5；SPEC 數學、Root-Cause、Full81 未經全面重新驗證；研究者接受不能替代必要的獨立審查（DD §D.4-4）。DD §D.3 之未驗證身分不得描述為已驗證，亦不得被 Framework v8 引為 primary evidence；不援引 Pointer R2 先例（DD §D.4-3） |
| **S5** | **(ii)** | DD §D.6-S5(ii)：FLA／RCA 維持 operator-extracted、未經獨立重現；FLA-VERBATIM 文字只以研究者採納之規範文字身分生效；RCA 數值只以 OBSERVED-relay 等級引用；本次不重新擷取 FLA／RCA rollout；不宣稱原 549 行 Root-Cause 報告（`ab9aa820…`）已驗證 |
| **D1** | **接受** | DD §E D1：SPEC + CL1 + RES + ART2（含 DD 第 0 層 [DC-NEW] 內容）作為 guard-restricted 的 Cost–ENS／ε-constraint **v8 方法規格**；效力限 Gate 2 |
| D2 | 依 DD §E D2 採納 | Precedence 依 DD §B.2（窄範圍；SPEC §10 不覆寫） |
| D3 | 依 DD §E D3 採納 | Big-M baseline（RES R-02；ART2 §9-2）；CL1 L299–303 tightening 不選用 |
| D4 | 依 DD §E D4 採納 | 最適性只在 \(F\cap X_g\) 上成立；不得標示為 unrestricted global optimality（ART2 §8） |
| D5 | 依 DD §E D5 採納 | ART2 §5.1（TA-03）與 §8-5 |
| D6 | 依 DD §E D6 採納 | ART2 §4.2 PV0 Pilot fail-closed；**沒有 Pilot 授權** |
| D7 | 依 DD §E D7 採納 | ART2 §6、§8-6 |
| D9 | 依 DD §E D9 採納 | 全年 Type-3 certification NOT VERIFIED；classifier 修改 NOT AUTHORIZED |
| D10 | 依 DD §E D10 採納 | 保留 SPEC／CL1／RES／ART2 + DD；不建 Resolution R3 或 Spec R3 |
| D11 | **不授權** | DD §E D11；Temp／對話證據之 durable 保存未授權（風險見 ART2 §10-11） |
| DD §H | **未選擇；未授權** | Framework v8 Candidate 撰寫屬下一個獨立階段 |

各列「採納」之實質內容，以 DD §E 該列及其所引條款之原文為準；本表不改寫其內容。

---

## 5. ART2 §7.5.4-B 研究者授權文句（逐字採納；ART2 L423）

> 本人（研究者）知悉：以 SHA-256 綁定之 Candidate R2（`1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557`）、Class-C Clarification R1（`4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878`）、Proposed Acceptance Resolution R1（`3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5`）及本 Proposed Acceptance Artifact R2 Candidate（SHA-256 由 Decision Record 記錄）所構成之 Cost–ENS／ε-constraint 方法規格，與 Framework v7.4 §0.1 L70、L74 及 §7.3–§7.5 所定方法不同（差異窮盡列於本 Artifact §7.5.4-C）；且本人未主張、亦未證明 v7.4 存在程式、資料、公式、source transcription 或 provenance 錯誤。本人仍核准：(1) 採行上述規格作為新研究問題之 v8 方法規格；(2) 該規格日後僅能經另行授權、獨立審查、正式接受並明示啟用之 Framework v8，前瞻承接本論文之 methodology authority；(3) 若 (1)、(2) 被解讀為受 Framework v7.4 §0.1、Protocol v1 §2、Constitution §7 或 CLAUDE.md 之 CLOSED 規則限制，本核准僅就 §7.5.4-C 所列差異構成本案限定例外。本核准不修改 Protocol、Framework v7.4 或 Registry v7.4，不授權其他 CLOSED 決策變更，不建立一般例外政策，不追溯取代任何歷史 bytes。

**Decision Record 記錄之 Proposed Acceptance Artifact R2 Candidate SHA-256：** `2386d47b96690ac3a8c81673b1c4750e85bce93ef837ce47a75e850cb49f8268`

---

## 6. 適用效力與限制

1. **效力：** 自 2026-10-24 起，§1.1 四份文件連同 DD 第 0 層內容，成為「已接受的 v8 方法規格」，只可作為 Gate 3（Framework v8）起草依據（ART2 §7.5.4-D）。
2. **非效力：** Framework v8 **NOT ACCEPTED**、**NOT ACTIVATED**；在 Gate 3 接受並另行明示 Activation 之前，任何文件、程式或報告不得將 Phase-1／v8 規格稱為 current thesis methodology authority，亦不得稱 v7.4 已被取代（ART2 §7.5.4-D、§7.5.5）。
3. **歷史保留：** 依 ART2 §7.5.4-E；不得將 v7.4 描述為失敗、無效或已撤銷。
4. **不授權事項：** 依 ART2 §7.5.4-F 與 DD §I——Git add／commit／tag／push；CURRENT_STATE、canonical pointer 或 CLAUDE.md 更新；Framework v8 撰寫、接受或 Activation；Protocol revision；legacy code／data reuse audit；Coding；PV0 Pilot；model build 或 Solver；Type-3；classifier 修改；修改任何 v7.4／Full81／EOB 歷史 bytes。
5. **保留之限制：** ART2 §10 residual limitations 全部保留；DD §K 宣稱限制（deterministic aggregate ENS ≠ probabilistic EENS；guard-restricted ≠ unrestricted optimality；不保證 Pareto knee、成本降低或經濟優勢）全部保留。
6. **STOP 規則：** ART2 §16-7——若發現 SPEC 與 §7.5.4-C（依 DD §C.3 補充）以外之 v7.4 §0.1 鎖定內容衝突，即 STOP，不得以本案例外涵蓋。
7. **後續流程：** 依 DD §J；每一步都不會自動觸發下一步。
8. **入口文件落後：** PROT §1、§28 仍寫 v7.2；CLAUDE.md 仍寫 v7.3；CURRENT_STATE 沒有 Phase-1 條目。不得據此把權威退回 v7.2／v7.3；是否更新屬另行授權事項（DD §F）。

---

## 7. 本 Record 的 provenance

- 位置：repository 之外（`C:/Users/Iris C/Downloads/`）；非 Git-durable。
- 本 Record 建立前的操作只有唯讀的 SHA-256、`stat`、`grep`／`sed`、`git rev-parse`、`git status --porcelain`，以及 §2 所述之單次 rollout 擷取。
- 未修改任何既有文件；未執行 Git mutation、Coding、model build 或 Solver；未建立 Framework v8、checkpoint 或其他 governance ledger。
- 本 Record 一經雜湊即不可變；如需更正，以 additive successor 處理（PROT §4–§5）。
- 本檔不嵌入自身的 SHA-256。

**PHASE-1 METHODOLOGY SPECIFICATION — ACCEPTED（Gate 2 only）— FRAMEWORK V8 NOT ACCEPTED／NOT ACTIVATED — V7.4 REMAINS CURRENT AUTHORITY**
