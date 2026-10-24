# Iris Thesis — Phase-1 Proposed Acceptance Artifact R2 Candidate

**日期：2026-10-24（Asia/Taipei）**
**狀態：PROPOSED / NOT ACCEPTED / PENDING FRESH INDEPENDENT TARGETED AUDIT / PENDING USER APPROVAL**
**文件類型：** 待研究者正式核准之 acceptance artifact 草案；為 Proposed Acceptance Artifact R1（SHA-256 `d406bd63ab479121a570203b2f82e947874630be2476efcac42c1a8079d05bab`）之 additive successor candidate。R1 經 2026-10-24 Final Limited Audit（FLA，§1.6）判定 **G-01 / ACCEPTANCE ARTIFACT FINAL LIMITED AUDIT — STOP**，依 PROT §4（L119–144）為不可變之歷史 candidate；本輪未修改 R1 任何 byte。R2 只修正 G-01／D12、D8、與其直接相關之核准／狀態／precedence 文字及必要 provenance metadata；其餘內容逐字承接 R1。本文件**不是** acceptance、不是 Acceptance Decision Record、不是 Framework v8、不是 Spec Candidate R3、不是 Coding／Pilot／Production 授權；不改寫任何既有 candidate、clarification、resolution、audit 或 accepted source。
**Writer：** Claude Code session `5ee3a2bd-4853-4234-9c5b-7e1289175b30`（Opus 5.5）。此 session 不是 R1 作者、不是 FLA 審查者，亦未參與 R2／CL1／RES 之撰寫或審查；但與 R1 作者、CL1／RES 作者及 AUD 審查者**同工具、同模型**，且 session 開始時已載入研究者 project-memory（見 §3.1、§3.7、§15）。R1 原 writer：Claude Code session `fd2b5546-0469-4ac0-a2e0-e424d95f3ada`（Opus 5.5），同時是 Resolution R1 的 targeted auditor 與 TA-01～TA-05 文字的作者。

---

## 0. 本文件的性質與使用方式

1. 本草案列出研究者核准後將生效的完整文字與決策選項。所有決策皆為 **RECOMMENDED / PENDING USER APPROVAL**，沒有任何一項已被核准。
2. 核准方式：研究者另立一份簡短的 **Acceptance Decision Record**，引用本草案（R2）的 SHA-256、§11 各決策之選擇，以及 §11 D8-c 所要求之 fresh targeted audit PASS 紀錄。R1 不得作為 Decision Record 之決策對象（STOP 之歷史 candidate；PROT §4）。本草案一經雜湊即視為不可變，不就地改為 ACCEPTED（PROT L157、L601；additive-only）。
3. 標記說明：

| 標記 | 意義 |
|---|---|
| `[AUDITED-VERBATIM]` | 逐字承接 RES Independent Targeted Audit 的文字（SHA `3ae99b7b…`） |
| `[CARRIED]` | 承接 R2／CL1／Resolution 已審查文字，未改內容 |
| `[RESEARCHER-SPECIFIED]` | 來自研究者 2026-10-23 指令；與已審查文字之差異逐項列明 |
| `[CONSOLIDATED]` | 將上列來源合併表述，不新增規則 |
| `[NEW — NEEDS TARGETED REVIEW]` | 先前任何審查都未涵蓋的新治理項目（R1 用語） |
| `[FLA-VERBATIM]` | 逐字承接 2026-10-24 Final Limited Audit 之建議文字（§1.6；擷取文字 SHA `4090e75a…`） |
| `[R2-NEW — NEEDS TARGETED REVIEW]` | 本 R2 新增或改寫之治理文字；須經 §11 D8-c 強制 fresh targeted audit |

---

## 1. Source identities（R1 輪 2026-10-23 核對；R2 輪 2026-10-24 以唯讀 SHA-256 全部重新核對；全部 MATCH）

### 1.1 決策對象與審查

| ID | 完整路徑 | SHA-256 | Bytes | 自述狀態 |
|---|---|---|---:|---|
| R2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` | 40,221 | CANDIDATE R2 / NOT ACCEPTED（L4） |
| CL1 | `C:/Users/Iris C/Downloads/Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` | `4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878` | 30,690 | DRAFT / NOT ACCEPTED（L4） |
| RES | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Resolution_R1_2026-10-23_DRAFT.md` | `3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5` | 27,864 | DRAFT / NOT ACCEPTED（L4） |
| AUD | `C:/Users/Iris C/Downloads/Iris_Phase1_Acceptance_Resolution_R1_Independent_Targeted_Audit_2026-10-23.md` | `3ae99b7b5f9672fe79f45aebebdbd746f98a25798c84e8e749afe675f583a3eb` | 23,062 | CONDITIONAL PASS / NOT CLOSED |

### 1.2 治理來源

| ID | 路徑 | SHA-256 | Bytes |
|---|---|---|---:|
| PROT | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md`（clean vs HEAD；`docs/protocols/` 無後續 revision） | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` | 19,977 |
| CONST | `C:/Users/Iris C/Downloads/Iris_Thesis_Response_Mode_and_Research_Governance_Constitution_2026-10-03.md` | `4f5eaf050d96f84d96e06ebebd53e095f209ad50bb0a0f94a180f2dd0efc9c38` | 22,435 |

### 1.3 Accepted authority records（repo HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；全部 clean vs HEAD）

| ID（沿用 R2 §2） | 路徑（相對 repo root） | SHA-256 | Bytes |
|---|---|---|---:|
| S01 FW74 | `docs/research_framework_v7_4_2026-09-26_r2.md` | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` | 216,186 |
| S02 REG74 | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` | 245,125 |
| S05 PTR | `configs/current_mainline_pointer.json` | `ed7005dea8dc423fb4372554b3f8d15fd34c3988441c4fb14c2dede0d64afcb4` | 58,156 |
| S06 STATE | `docs/ai_handoff/CURRENT_STATE.md`（L45：Framework v7.4、Registry v7.4 `CLOSED / ACCEPTED`；全文無 Phase-1 條目） | `043711e8bb422bec7e26ea8263a06ffbf4bf7d28af27cefa91b190f2868b327f` | 78,260 |
| S20 | `docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md` | `39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f` | 18,809 |
| S21 | `results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | `5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33` | 15,144 |
| S22 | `docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md` | `4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977` | 16,944 |
| S23 | `results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json` | `53074cfe44c0276d6f319497cbe6f5aaf07b255ac0c335f9481174dd968063fe` | 16,818 |
| S24 | `docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md` | `bf909363d726ecd2f55ce883a71e6a894e718587bbeb6946d879758f246c12ce` | 7,639 |
| S25 | `results/provenance/current_mainline_pointer_acceptance_r2/acceptance_closure.json` | `bf0bb2766d15fd69b27d95436e4375958de1bc98f84dce31b2c1be3249053d71` | 16,901 |

### 1.4 技術支撐來源

| ID | 路徑 | SHA-256 |
|---|---|---|
| CORE | `…/iris_thesis/src/annual_design_model_v7_2.py`（CORE_VERSION r10；clean vs HEAD；本輪重核） | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| BRIDGE | `…/iris_thesis/docs/checkpoints/transition_settlement_decision_bridge_v7_2_2026-09-09.md`（AUD 已核） | `7bb5c6c134e6c790088999ba80464dc37087ddcebcac0408399413176c952394` |
| S11 | `…/iris_thesis/data/reference/taipower_seasonal_settlement_matrix_v7_2.csv`（AUD 已核） | `ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79` |
| REPORT | `C:/Users/IRISC~1/AppData/Local/Temp/iris_classc_guard_experiment_20261023/run_20261023T060151Z/REPORT.md`（本輪重核） | `db021bf52689c504b3ee5cd05fffe9de74ef48e7f734a1cfbffd11c4e21b8439` |
| MANIFEST | 同目錄 `MANIFEST.json`（本輪重核；目錄共 176 檔） | `303005d9aa2a8d19c4551919805cdb0fcc284a701e9f207e72310e6479a634cc` |
| EXP3 | 同目錄 `artifacts/exp3_adversarial.csv`（本輪重核） | `bb8754e300c47876aac386477867c7a4ff07f5979a8747243c41d8e1df7b14d7` |
| EXP4 | 同目錄 `artifacts/exp4_counterexample.json`（本輪重核） | `d5c5f4f3abfaaae64189fbd58471dedb0c2a59bc134b41ddee751ca9a6edf364` |
| EXP5 | 同目錄 `artifacts/exp5_month_fixture.json`（本輪重核） | `485a3400d84faada485fda4a39d31289e7d6359fb8862d369bcc5fd1a78f9706` |

### 1.5 找不到或未驗證的來源

- R1 輪：要求的所有檔案來源均已找到，無替代。R2 輪之新增來源與限制見 §1.6。
- **Conversation-only（無檔案、未讀內容）：**
  - R2 Independent Static Audit：Codex rollout `rollout-2026-10-23T12-25-31-01a16701…jsonl`，transcript SHA 前綴 `8934245f…`（依 CL1 L62、RES L39）。
  - CL1 Independent Targeted Static Audit：Claude Code session `180c3fec-52f7-4dc4-8216-e37c9b7a67f6`（依 RES L38）。Transcript 檔案存在（1,728,990 bytes），依 custody 規則未讀。
- 上述兩份審查的結論本草案僅能「依所引文件轉述」，不是本輪獨立核對的事實。

### 1.6 R2 輪新增來源（2026-10-24；唯讀）`[R2-NEW]`

| ID | 路徑 | SHA-256 | Bytes | 角色／狀態 |
|---|---|---|---:|---|
| ART1 | `C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R1_2026-10-23_DRAFT.md` | `d406bd63ab479121a570203b2f82e947874630be2476efcac42c1a8079d05bab` | 42,469（497 行，LF） | 前身；FLA = STOP；本輪未修改 |
| FLA | 見下方 custody | 擷取文字 `4090e75a53700918b886f5ca073d509ee02e0f98ce4542e1425b8a5ef507cfc3` | 19,586（UTF-8） | 2026-10-24 Final Limited Audit；G-01 STOP |
| RCA | 見下方 custody | 擷取文字 `cf2bb7fa421c717f9b9fced21f4a3af9f87769a62048bf627bc49e9dd197374d` | 36,191（UTF-8） | 2026-10-23 Layer A Root-Cause Audit（SUFFICIENT）之 Codex final answer |
| HO2 | `C:/Users/Iris C/Downloads/Iris_Thesis_v7_4_to_v8_Handoff_R2_RootCauseUpdated_2026-10-23.md` | `889dfb720c2ab529901ac350111965ba3d901bbbe4cc9db135644ce51a91d71d` | 49,185 | 研究者端 handoff；僅作脈絡與轉述，非 primary evidence |
| PTR-C | `results/provenance/current_mainline_pointer_acceptance_r2/acceptance_closure.json`（= §1.3 S25） | `bf0bb2766d15fd69b27d95436e4375958de1bc98f84dce31b2c1be3249053d71` | 16,901 | Pointer R2 限定例外先例（L95–108） |
| PTR-A | `results/provenance/current_mainline_pointer_independent_audit_r2/independent_audit_record.json` | `0de5756fdbcfc548b258e5d99b34036f140ff4cc3b98f041544629ede0416e08` | 14,501 | Pointer R2 審查紀錄（L9、L21–22） |
| G1R | `results/provenance/full81_g1_postsolve_results_acceptance_r1/acceptance_closure.json` | `3b27f9a60f5e0bfbcffde343aad164e74cff2f8a98581d91fb95d4bc90e2ba02` | 85,857 | Full81 結果 acceptance；本輪只核對身分 |

R2 輪亦重新雜湊 §1.1–§1.4 全部來源（含 Temp 實驗目錄之 REPORT、MANIFEST、EXP3～EXP5；目錄仍為 176 檔），全部與 R1 所列相同；repo HEAD 仍為 `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`，`git status --porcelain` 雜湊仍為 `e2c74e09…`（16 項）。

**FLA／RCA custody（operator-extracted；非原始交付檔案）：**
- 研究者於 2026-10-24 本輪對話中，就本任務**單次**授權自 Codex rollout 擷取最終回覆；此授權不構成常設規則。
- 擷取方法：以 `python -I` 逐行解析 rollout JSONL，只取 `type=response_item`、`payload.type=message`、`payload.role=assistant`、`payload.phase=final_answer` 之單一紀錄，串接其 `output_text`，以 UTF-8 編碼後雜湊；並確認其與 `event_msg/task_complete.last_agent_message` 完全相同。另只讀取 `session_meta`（id、timestamp、cwd、originator、cli_version）與 `turn_context`（model、effort）欄位；未閱讀其他對話紀錄。
- FLA transcript：`C:/Users/Iris C/.codex/sessions/2026/10/23/rollout-2026-10-23T23-49-45-01a16974-3389-7001-a658-c10585f05a7a.jsonl`；847,689 bytes；SHA-256 `dc928fef878815396d2b1de1589bee2dec20c7b0849f439567ce5a86930602c2`；final answer 位於第 132 行，timestamp `2026-10-24T03:15:52.865Z`；session id `01a16974-3389-7001-a658-c10585f05a7a`；`turn_context` 記錄 model `gpt-6-astra`、effort `high`；originator `codex_vscode`。
- RCA transcript：同目錄 `rollout-2026-10-23T23-00-21-01a16946-f93c-7003-856e-5d3e3d879e2c.jsonl`；2,359,543 bytes；SHA-256 `71ee12c1a4431fdd82130fe3b2fa91471ddca0de8be7ce7eed06b83ec6c2030f`；final answer 位於第 160 行，timestamp `2026-10-23T15:18:13.655Z`；`turn_context` 記錄 model `gpt-6-astra`、effort `xhigh`。
- 擷取副本暫存於本 session scratchpad（`%LOCALAPPDATA%\Temp`，非 durable），可依上述方法由 transcript 決定性重現。本文「FLA Lnn」「RCA Lnn」指擷取文字之行號。
- Model 名稱為 rollout 自身紀錄，本輪未另行驗證其實際後端。

**Root-Cause 原始報告限制：** HO2 L8、L75 所述「使用者上傳 549 行 Markdown，SHA-256 `ab9aa820c20ee0e8d0dbd9c61f687e2884c3e1bf3a59d78d71afcffeec238f7f`」之副本，本輪仍**未找到**（FLA L57–59 亦同）。RCA 擷取文字為 36,191 bytes，與該 SHA 不符；以 LF／CRLF、結尾換行、去除空白行等簡單正規化亦無一相符。因此 RCA 與該上傳副本之同一性 **NOT ESTABLISHED**；`ab9aa820…` 之實際 bytes：**NOT VERIFIED**。本草案引用之 Root-Cause 數值均為 RCA 擷取文字之**轉述**，本輪未由 Full81 primary outputs 重算（§7.6）。

---

## 2. Independent audit results

| 審查 | 對象 | Reviewer | Verdict | 處理去向 | Custody |
|---|---|---|---|---|---|
| R2 Independent Static Audit | R2 | Codex session `01a16701…`（轉述自 CL1 L62） | CONDITIONAL PASS；R2-N01 MODERATE／CARRIED，R2-N02 MINOR／OPEN wording（轉述自 CL1 L17、L62） | CL1 | conversation-only |
| CL1 Targeted Static Audit | CL1 | Claude Code `180c3fec…`（轉述自 RES L38、L252） | CONDITIONAL PASS；F-01～F-11（轉述自 RES §2） | RES R-01～R-10；F-11 → D8 | conversation-only |
| RES Targeted Audit | RES | Claude Code `fd2b5546…` | **CONDITIONAL PASS**；TA-01（MODERATE）、TA-02～TA-05（MINOR）；N-1～N-7 informational | 本草案 §3～§7、§13 | 檔案（AUD） |
| **Final Limited Audit（FLA）** `[R2-NEW]` | ART R1 之 TA-01～TA-05 parity、G-01／D12、D8、precedence | Codex session `01a16974…`（rollout 紀錄 model `gpt-6-astra`） | **STOP**（G-01／D12：MAJOR／接受阻擋）；TA-01 條文補正 PASS（D8 決定仍 PENDING）；TA-02～TA-05 PASS | 本 R2 §3.7、§7.5、§7.6、§11 | operator-extracted（§1.6） |

RES Targeted Audit（AUD）摘要 `[CARRIED]`：
- R-01～R-10 每項都對應可由 CL1／R2 原始 bytes 重現的真實缺陷。
- 矩陣判定：R-01、R-02、R-03、R-07、R-08、R-09、R-10 = PASS；R-04（TA-03）、R-05（TA-02、TA-04）、R-06（TA-04）= CONDITIONAL PASS。
- R2 §10 不需覆寫（AUD §B.1）。
- 條件：acceptance artifact 逐字採納 TA-01～TA-05，或明示列為 carried residual。

FLA 摘要 `[R2-NEW]`（FLA L3–17、L144–176、L217–221；operator-extracted，§1.6）：
- 整體 verdict：**G-01 / ACCEPTANCE ARTIFACT FINAL LIMITED AUDIT — STOP**；阻擋項為 G-01／D12 之前瞻權威轉移機制尚未封閉（MAJOR／接受阻擋）。
- TA-01：條文補正 PASS，D8 研究者決定仍 PENDING；TA-02～TA-05：PASS；precedence 限於明列衝突範圍；未發現需重開 Class-C、B1–B4 或 Full81 數學審查之新矛盾。
- Readiness：D2～D7、D9 READY；D10 數學文件鏈足夠；D11 READY FOR SEPARATE AUTHORIZATION；D1 待 G-01／D8；D8 仍需明示決定；D12 STOP／MAJOR。
- 最小剩餘動作：以 additive 候選（可為最小 Artifact R2）固定 successor、限定 CLOSED 處置、兩階段接受、歷史保留與 D8 實際審查紀錄，並只審查新增條款與交叉引用；無須重寫 Spec R2、建立 Resolution R3 或重做 Class-C／Full81。

**PASS 詞彙註記：** 整條審查鏈（含 FLA）沒有任何一份對 acceptance 對象發出無條件 `<TOPIC> — PASS`；FLA 對 R1 之整體 verdict 為 STOP。PROT L689–691：「Only an independent PASS may additionally state: `<TOPIC> — CLOSED / ACCEPTED`」。處理方式見 D8-c（R2 起為強制要件）。

---

## 3. TA-01 — 審查獨立性紀錄

### 3.1 Writer 與各審查 session 身分 `[CONSOLIDATED]`

| 文件 | 作者 | 審查者 | Session independence | Cross-model independence | 依據 |
|---|---|---|---|---|---|
| R2 | Codex（**推定**：R2 S19 授權原文位於 `.codex/attachments/…`；session id 未核） | Codex `01a16701…` | YES（轉述，未核） | **NO**（推定 Codex→Codex） | R2 L58；CL1 L62 |
| CL1 | Claude Code（CL1 L18）；依檔案 mtime 推定 `60b08cd1…` | Claude Code `180c3fec…` | YES | **NO** | CL1 L18；RES L251–255 |
| RES | Claude Code `180c3fec…`（RES L253） | Claude Code `fd2b5546…` | YES | **NO** | RES L253；AUD §0 |
| TA-01～TA-05 文字 | Claude Code `fd2b5546…` | Codex `01a16974…`（FLA；parity 與語義之有限審查） | YES | 跨工具 YES；跨模型 YES（依 rollout 紀錄 `gpt-6-astra` 對 R1 所記 Opus 5.5；後端未另驗） | FLA L144–153；§1.6 |
| ART R1 | Claude Code `fd2b5546…` | Codex `01a16974…`（FLA；限 TA parity、G-01、D8、precedence；verdict STOP） | YES | 同上 | FLA L3、L125–133 |
| 本 R2 Candidate | Claude Code `5ee3a2bd…` | **無**（PENDING；D8-c 強制） | — | — | 本文件 |

Session 推定只使用 session 檔名與 mtime（CL1 mtime 15:45:02 ↔ `60b08cd1` 最後寫入 15:45；RES mtime 16:45:07 ↔ `180c3fec` 最後寫入 16:45），沒有讀取 transcript 內容。

**事實（R2 更新）：** R2→CL1→RES 審查鏈中**沒有任何一份經過跨模型審查**。FLA 為唯一跨工具（Codex 審查 Claude Code 作者之文字）審查，範圍限於 ART R1 之 TA parity、G-01、D8 與 precedence，未重審整份 R2 數學（FLA L137），且 verdict 為 STOP。本 R2 Candidate 尚未經任何審查。

### 3.2 Protocol／Constitution 原文（逐字）與適用

**硬性（Mandatory）：**

| 出處 | 原文 | 本次安排 |
|---|---|---|
| PROT L18 | 「allowing a candidate to self-accept;」（列為須防止之失效模式） | 無 self-accept |
| PROT L95 | 「A producing agent must never self-promote its own candidate to CLOSED / ACCEPTED.」 | 符合：acceptance 由研究者決定 |
| PROT L322 | 「The agent that creates a candidate must not be the only agent that accepts it.」 | 符合：acceptor 為研究者 |
| PROT L329–335 | 「The independent auditor must: treat candidate prose as untrusted; re-derive acceptance-critical facts; use primary repository bytes; make zero repairs during audit; perform zero solves unless audit scope explicitly authorizes them.」 | AUD 依此執行（AUD §E.3） |
| PROT L689–691 | 「Only an independent PASS may additionally state: `<TOPIC> — CLOSED / ACCEPTED`」 | **未完全滿足**：鏈中只有 CONDITIONAL PASS（D8-c） |
| PROT L713 | 「candidate self-acceptance without independent audit.」（§27 STOP condition） | 不觸發 |
| PROT L735 | 「Candidate author cannot self-accept.」 | 符合 |
| PROT L157、L601 | 「new acceptance artifact after independent audit.」；「After independent acceptance, create a separate additive acceptance artifact if durable closure needs to be recorded.」 | 依 §0-2 另立 Decision Record |

**字面要求，但術語未定義：**

| 出處 | 原文 | 問題 |
|---|---|---|
| PROT L736（§28 Default Handoff Header） | 「Acceptance requires independent read-only cross-agent audit.」 | "agent" 未定義以工具、model 或 session 區分。§11 標題「Cross-Agent Independence Rule」與 L324–327 皆以工具（Claude Code／Codex）表述，**工具層級讀法較自然**；在該讀法下，同為 Claude Code 的 session 審查**不滿足**本條。 |
| PROT L803（§31） | 「AUDIT WITH A DIFFERENT AGENT」（不確定時之預設） | 同上 |
| PROT L28 | 「This protocol is the default unless a later **explicitly authorized protocol revision** supersedes it.」 | 已查 `docs/protocols/`：無後續 revision |

**偏好（Preferred）：**

| 出處 | 原文 |
|---|---|
| PROT L324–327 | 「Preferred pattern: Claude Code implements → Codex audits; Codex implements → Claude Code audits」 |
| CONST L545、L547 | 「對 Claude Code 修改做第二模型稽核；」「需要和 implementation agent 分離的治理工作。」（Codex 適用場景） |
| CONST L606–610 | 指令須說明「可否沿用原 session；是否必須 fresh session；是否需要 cross-model independence。」 |
| CONST L703–713（§19） | independent audit 等情況「預設要求 fresh session」；含「cross-model verification 能明顯提高 defensibility。」；「若同一 session 可以合理沿用，必須說明原因。」 |

**Protocol 修訂程序：** PROT L780–792（§30）：須保留原版、建立新 revision、說明缺陷與理由，且「independently audit the revised protocol if it changes acceptance-critical behavior」（L789）。

### 3.3 研究者立場 `[RESEARCHER-SPECIFIED]`

依研究者 2026-10-23 指令：
- 不以跨模型供應商審查作為自動阻擋條件；
- 可依實際額度選擇 Codex 或 Claude Code；
- 不同 Claude Code session 的審查必須如實標記為 session-independent、非 cross-model-independent。

本草案僅記錄此立場，不代研究者核准。

### 3.4 核准後生效之 D8 紀錄文字 `[AUDITED-VERBATIM]`（PENDING D8；生效前不構成研究者決定）

> **D8／F-11 獨立性紀錄。** PROT v1 硬性規定：candidate author 不得 self-accept（L95、L735）；creator 不得為唯一 acceptor（L322）；auditor 須符合 L329–335；僅 independent PASS 可導向 CLOSED／ACCEPTED（L689–691）。L736「Acceptance requires independent read-only cross-agent audit」與 L803「AUDIT WITH A DIFFERENT AGENT」未定義 "agent" 是否以 session 或 model 區分。研究者就本次 acceptance 決定：以與 CL1 author session、RES author session 均不同且無共享對話脈絡之 Claude Code fresh session targeted audit，作為 L736／L803 所稱之獨立審查。Session independence = YES；Cross-model independence = NO；同模型相關錯誤風險已知。此為本次 acceptance 之限定解釋，不構成 Protocol revision（L28）；如欲成為常設規則，須依 PROT §30 另行修訂。

### 3.5 補充條文 `[RESEARCHER-SPECIFIED]`／`[CONSOLIDATED]`（PENDING D8）

1. **例外並列：** 若 L736／L803 的 "agent" 依工具層級讀法理解（§3.2），本次安排與該兩條存在**無法以解釋消除的衝突**。因此 D8-a 的核准同時構成：在該讀法下，對 PROT L736、L803 的**研究者正式核定之限定例外**，範圍僅限本次 Phase-1 acceptance（R2、CL1、RES 與本 Artifact R2；R1 僅為歷史前身）；R2 輪之分層範圍見 §3.7。
2. **R2 鏈：** 上述紀錄同樣適用於 R2 的 Codex→Codex（推定）審查；標記為 session-independent（轉述）、非 cross-model-independent。
3. **常設政策：** 「可依額度選擇 Codex 或 Claude Code」若要成為常設規則，屬改變 acceptance-critical behavior 的 Protocol revision，須依 PROT §30（含 L789 獨立審查）另行辦理。**本草案不產生此效果**（D8-b）。
4. **PASS 詞彙：** 見 D8-c。

### 3.6 合規聲明

本草案**不宣稱完全合規**，亦不宣稱超出實際證據之 cross-agent／cross-model 合規。PROT 硬性規定中，L95、L322、L329–335、L713、L735 已滿足（L329–335 依 AUD、FLA 自述）；L689–691 須以 D8-c 之 fresh targeted audit 明確 PASS 滿足（R2 起為強制，§3.7-4）；L736、L803：ART／TA／G-01 層已有 FLA 之跨工具審查，R2／CL1／RES 歷史審查層在工具層級讀法下仍須以 D8-a 之本案限定例外處理（§3.7-2）。

### 3.7 D8 R2 處置（PROPOSED；PENDING D8）`[R2-NEW — NEEDS TARGETED REVIEW]`

FLA 建議之最小 D8 決定 `[FLA-VERBATIM]`（FLA L137–140）：

> 1. 如實接受本輪作為 ART／TA／G-01 的有限跨代理審查，不宣稱它重審整份 R2 數學。
> 2. 對仍依賴的同工具歷史審查，研究者須另作**本次專屬**的充分性決定／限定例外，明列文件、範圍及未驗證身分；不能直接套用 Pointer R2。
> 3. D8-b 若要成為常設工具政策，仍走 PROT §30。
> 4. 保留 D8-c(i)：補正後取得正式有限審查 PASS。不要以「CONDITIONAL PASS 足夠」取代目前尚未關閉的 G-01。

依此展開之分層處置：

| 層 | 對象 | 實際審查 | 獨立性（如實） | 已知限制 | 擬議處置 |
|---|---|---|---|---|---|
| L1 | ART R1 之 TA-01～TA-05 parity、G-01、D8、precedence | FLA（Codex `01a16974…`） | Session：YES；跨工具：YES；跨模型：依 rollout 紀錄 YES | 範圍有限，未重審 R2 數學；verdict STOP；custody 為 operator-extracted | 如實認定為**有限跨代理審查**；不得延伸為 R2／CL1／RES 之跨代理審查 |
| L2 | R2（Spec） | Codex `01a16701…` Independent Static Audit（轉述） | Session：YES（轉述）；跨工具：NO（推定 Codex→Codex）；跨模型：NO（推定） | conversation-only，未讀；作者 session 身分為推定 | 研究者**本案專屬**充分性決定／限定例外 |
| L2 | CL1 | Claude Code `180c3fec…` Targeted Static Audit（轉述） | Session：YES；跨工具：NO；跨模型：NO | conversation-only，未讀；作者 session 依 mtime 推定 | 同上 |
| L2 | RES | Claude Code `fd2b5546…`（AUD，檔案） | Session：YES；跨工具：NO；跨模型：NO | 同模型相關錯誤風險；AUD 作者同時撰寫 TA 文字與 R1 | 同上；§3.4 為本層既有之 TA-01 紀錄文字 |
| L3 | 本 R2 Candidate 之 `[R2-NEW]`／`[FLA-VERBATIM]` 條文 | 無（PENDING） | — | 作者 Claude Code `5ee3a2bd…` 與 L2 多數作者／審查者同模型，且曾載入研究者 project-memory | **強制** fresh targeted audit 明確 PASS（第 4 點） |

1. **L1（已執行之有限跨代理審查）：** FLA 只審查 ART／TA／G-01／D8／precedence 之有限範圍；其 TA-02～TA-05 PASS 與 TA-01 條文補正 PASS 可如實引用；不得表述為 R2 數學之跨模型重審，亦不得表述為整條鏈之 cross-agent 合規。FLA 整體 verdict 為 STOP，不構成 PROT L689–691 之 PASS。
2. **L2（歷史同工具審查之本案專屬充分性決定）：** 研究者如選 D8-a(i)，即就本次 Phase-1 方法規格 acceptance 明示認定：R2（推定 Codex→Codex）、CL1（Claude Code→Claude Code）、RES（Claude Code→Claude Code）之 session-independent 審查，連同 L1 之有限跨代理審查與 L3 之強制 PASS，**足以**作為本案 PROT L736／L803 所稱之獨立審查；在工具層級讀法下，此認定即構成對 L736、L803 之**本案限定例外**（§3.5-1）。範圍限於上表所列文件與審查；R2、CL1 審查報告內容及 R2／CL1 作者 session 身分為 **NOT VERIFIED**（轉述／推定），此不確定性須一併明示接受或拒絕。§3.4 文字為 AUD 層之既有紀錄，不擴大其範圍。
3. **Pointer R2 先例之限制：** PTR-C L95–103 記錄研究者曾就 Pointer R2 單一案件作 `CASE-SPECIFIC EXCEPTION`（`protocol_revision`：None），PTR-A L21–22 記錄 `cross_agent_review=false`、`same_model_as_author=true`。該紀錄只證明「研究者得就單一案件記錄限定例外而不修訂 Protocol」之**機制先例**；其案件分類為 `GOVERNANCE / AUTHORIZATION CHANGE`、明示「not SCIENTIFIC METHODOLOGY CHANGE」（PTR-C L106–108）。它**不**預先授權本案，亦不得自動套用（FLA L94、L123、L138）；本案例外須由研究者另行明示核准。
4. **L3（強制審查）：** 本 R2 之 `[R2-NEW]`／`[FLA-VERBATIM]` 條文及其交叉引用，須於 Acceptance Decision Record 前取得 fresh independent targeted audit 之明確 `<TOPIC> — PASS`（範圍見 §11 D8-c）。審查者須為未參與 R1、R2 撰寫之 fresh session；依 PROT L324–327 之偏好，建議由 Codex 審查（本 R2 作者為 Claude Code）。若改由 Claude Code session 審查，須如實標為 session-independent、非 cross-model，並列入 D8-a 例外範圍。結果為 CONDITIONAL PASS 或 STOP 時，均不得記錄 D1（§16-4）。
5. **不宣稱事項：** 不宣稱整條 Phase-1 鏈已滿足 cross-agent 或 cross-model 要求；不宣稱 FLA 已驗證所有歷史 session 身分（FLA L131–132）；不宣稱 FLA 擷取副本等同 Codex 端交付之原始檔案（§1.6）。
6. **常設政策：** 「依額度選擇 Codex 或 Claude Code」仍僅記錄研究者立場；成為常設規則須依 PROT §30（含 L789 獨立審查）另行修訂（D8-b；§3.5-3 不變）。

---

## 4. TA-02 — PV0 Pilot fail-closed rule

### 4.1 AUD 原文 `[AUDITED-VERBATIM]`（供追溯；效力由 §4.2 取代）

> 觸發條件包含：任何 Class-C component 之 `NUMERICAL_BOUNDARY_UNRESOLVED`，或其任何 post-solve invariant failure（`source_selection`、`bounded_product`、`source_timestamp`、`resolved_rate`、`native_seasonal_max`，CORE L2421–2444 或 Phase-1 實作之等價欄位）。
> PRESERVE DIAGNOSTICS 另含：earlier／later 季別最大時刻 timestamp；以 hourly dispatch 獨立重算之該 component τ-convention 帳單與 strict 帳單；模型 \(C_{over}\) 與重算 \(C_{over}\) 之差；整體 cost reconciliation 差額。
> STOP 範圍：該 run 立即標記無效；其餘 run 是否續行由 Pilot 授權文件明定，未明定時預設停止整個 Pilot、待研究者決定。
> 狀態標記：`CLASS_C_CERTIFICATE_FAILED`（run／case 層級 certificate failure）；不得表述為模型數學不可行、solver INFEASIBLE、方法論無效，亦不得表述為 guard 已改變最適值。

### 4.2 生效條文：R-05b（as amended）— PROPOSED PILOT ENTRY RULE（PENDING D6）`[CONSOLIDATED]`

本條取代 RES L156–164 的 R-05b。核准前，PV0 correctness Pilot 不得授權（沿用 RES L156）。

1. **觸發。** 在 PV0 correctness Pilot 的任何 run 中，出現下列任一事件：
   - (a) 任何 Class-C component 之 `NUMERICAL_BOUNDARY_UNRESOLVED`；
   - (b) 任何 Class-C component 之 source／rate certificate failure 或其他 post-solve invariant failure：`source_selection`、`bounded_product`、`source_timestamp`、`resolved_rate`、`native_seasonal_max`（CORE L2421–2444，或 Phase-1 實作之等價欄位）。

   判定沿用 live classifier 既定規則（CORE L163–190、L205–208）：**不論該 component 的 W 是否為 0**，皆同樣判定。
2. **STOP。**
   - 該 run 不得標記 PASS，不得被宣稱為有效結果，不得進入 frontier、endpoint 或比較表。
   - 停止該案例的 acceptance。
   - Pilot 後續案例的自動推進立即暫停，等待診斷及研究者決定。
3. **REPORT。**
   - 向研究者回報 component、事件類型與數值。
   - 狀態標記為 `CLASS_C_CERTIFICATE_FAILED`（run／case 層級 certificate failure／numerical boundary）。
   - 不得表述為 MILP／模型數學不可行、solver INFEASIBLE 或方法論無效，亦不得表述為 guard 已改變最適值。
4. **PRESERVE DIAGNOSTICS。** 保留以下全部資料：
   - **原始 solver 輸出。**
   - **每個 Class-C component：**
     - 識別與最大值：month、period、exact \(G_e,G_l\)、earlier／later 季別最大時刻 timestamp；
     - 差值：\(d\)、\(d-\tau\)、\(d-(\tau+g)\)；
     - source binary 與計價：b 原值與四捨五入值、\(W_{exact}\)、乘積值、兩季費率、resolved rate；
     - 驗證結果：classifier status、各 invariant 結果、native seasonal maxima 驗證誤差。
   - **全域數值設定與結果：** FeasibilityTol、IntFeasTol、τ、g、solver status 與 gap、原單位之最大約束違反量（constraint residual）。
   - **帳單重算：**
     - 以 hourly dispatch 獨立重算之該 component τ-convention 帳單與 strict 帳單，及兩者差額；
     - 模型 \(C_{over}\) 與 ex-post 重算 \(C_{over}\) 之差；
     - 整體 cost reconciliation 差額。
   - **實作版本身分。**
5. **禁止（均須研究者另行明示授權）：** 重新分類、放寬 classifier、調整容差、手動改標籤、重算後改標 PASS、以不同設定重跑以「消除」該事件、修改正式 code。
6. 本條不修改 classifier；CL1 §10.1 classifier 改善維持 NOT AUTHORIZED（D9）。

### 4.3 條文追溯與差異分類

| 條款 | 來源 | 與已審查文字之差異 | 分類 |
|---|---|---|---|
| 1(a) | RES L158 | 無 | `[CARRIED]` |
| 1(b) 列舉 | AUD TA-02 第 1 句 | 「source／rate certificate failure」為研究者用語，對應同一組 invariant | `[AUDITED-VERBATIM]` 語義 |
| 1「不論 W」 | 研究者指令；CORE L205–208；RES R-05a（S8b） | 重述現行 classifier 語義，無新判定 | `[CARRIED]` |
| 2 第 1 點 | RES L160；研究者「不得標記 PASS」 | 無實質差異 | `[CARRIED]` |
| 2 第 2–3 點 | 研究者指令 | AUD 原文：「其餘 run 是否續行由 Pilot 授權文件明定，未明定時預設停止整個 Pilot、待研究者決定」。研究者版本：「暫停後續自動推進，等待診斷及研究者決定」。兩者都禁止自動續行並交由研究者決定；研究者版本**不新增任何許可**，只取消「由 Pilot 授權文件預先另定」的路徑 | `[RESEARCHER-SPECIFIED]`；同等或更嚴；非新增許可性規則 |
| 3 | RES L161；AUD TA-02 第 4 句；研究者「certificate failure／numerical boundary」用語 | 無實質差異 | `[AUDITED-VERBATIM]`＋`[CARRIED]` |
| 4 | RES L162；AUD TA-02 第 2 句；研究者列舉（resolved rate、source timestamp、native seasonal maxima、constraint residual、ex-post overcontract、strict／τ 差） | 診斷欄位聯集，無新判定 | `[CONSOLIDATED]` |
| 5 | RES L163；研究者「重算後改標 PASS、修改正式 code」 | 禁止項目聯集 | `[CONSOLIDATED]` |
| 6 | RES L164 | 無 | `[CARRIED]` |

判定：§4.2 沒有新增許可性或數學性規範。唯一偏離 AUD 文字之處（STOP 範圍）為研究者明示、同等或更嚴的程序選擇，因此不標 NEEDS TARGETED REVIEW，但列入 D8-c 確認性審查範圍（建議）。

---

## 5. TA-03 — 費率方向與數學結論

### 5.1 生效條文 `[AUDITED-VERBATIM]`（PENDING D5；取代 RES L134 該點）

> 若某 component 滿足 \(r_l\ge r_e\)（開側較貴）：該 component 之閉合計價逐點等於 canonical 計價，非 canonical 可行點只會高估。**僅當模型中所有 Class-C component 均滿足 \(r_l\ge r_e\) 時**，才有 \(C^*_{closed}=\min f_\tau=\inf_\tau\)（可達）；現行 calendar 因 October component 不滿足此條件。

### 5.2 適用說明 `[CARRIED]`

- 現行 calendar（S11 L21–22、L25–26、L44–45、L48–49）中，2025-05 的 `sat_half`／`off` 滿足 \(r_l>r_e\)，2025-10 的 `sat_half`／`off` 滿足 \(r_l<r_e\)。
- 因此全年模型不得因 May component 的方向而推論閉合方案在年度層級精確。
- RES L135–138（\(r_l<r_e\)、W=0、方案 B）不變。

---

## 6. TA-04 — 實驗觀察語氣

### 6.1 RES L154 替換文字 `[AUDITED-VERBATIM]`（取代「故 Phase-1 類型模型會停在距條帶 \(10^{-4}\) kW 以內」）

即此兩個 Phase-1 類型月度 fixture 停在 d=0，距條帶下緣 τ=\(10^{-4}\) kW。

### 6.2 RES L171 替換文字 `[AUDITED-VERBATIM]`（取代「在 May 方向（\(r_e<r_l\)），A 在 τ-convention 下的吸引點即為 \(d=\tau\)。」）

在 May 方向（\(r_e<r_l\)），A 的最適解**可能**停在 d=τ（τ-convention 允許 earlier 標籤之上緣），此時兩規則帳單相差 \((r_l-r_e)W\)；EXP5b 真實資料 fixture（May、α=0.50、W=657.064）實際停在 d=0，兩規則一致。全年行為 NOT VERIFIED。

### 6.3 明確保留之觀察與宣稱限制 `[CARRIED]`＋`[RESEARCHER-SPECIFIED]`

- **觀察（EXP5，SHA `485a3400…`）：** EXP5b 兩個 α=0.50 真實資料月度 fixture 的 `off` component 皆位於 **d=0**：2025-05 的 W=657.064 kW，2025-10 的 W=0。本觀察不得寫成 d=τ。
- **宣稱限制：** 不得由上述 fixture、EXP3 toy 或 S12／S8b 型構造，推論 Phase-1 全年模型一定發生 Class-C false-fail，或一定不發生。Phase-1 全年模型中的 Class-C d／W 行為：**NOT VERIFIED**（RES R-05a、§5-4）。本句只限縮宣稱，不新增規則。

---

## 7. TA-05、Precedence 與 Framework 邊界

### 7.1 生效條文 `[AUDITED-VERBATIM]`（PENDING D1／D2）

> R-01 之優先範圍包含 CL1 §4.3（L116–123）。R-05b 為本 Resolution 之規範條目（Pilot entry precondition），其效力不因置於 CL1 §6.2 之後而改變；R-05a 為證據補記，非規範。

補充 `[CONSOLIDATED]`：上句中的「R-05b」，核准後指本草案 §4.2 的 R-05b（as amended）。

### 7.2 有效 precedence chain（核准後；只在不一致之範圍內適用）`[CONSOLIDATED]`

1. **本 Artifact（R2）採納之修正文字：** §3.4–§3.5、§3.7（若 D8 核准）、§4.2、§5.1、§6.1–§6.2、§7.1，以及 §7.5（若 D12 核准）。R1 不在本 precedence chain 內（STOP 之歷史 candidate；與本 R2 相同之文字以本 R2 為準）。本 chain 只在 Phase-1／v8 規格文件之間適用；與 Framework v7.4 之關係見 §7.5.5。
2. **RES R-01～R-10**（經第 1 層修正）。
3. **CL1 §4.2（L81–114）、§4.3（L116–123）、§7.4（L257–264）、§9（L287–312）**（經 RES 修正）。
4. **R2 對應段落：** §8.3（L259–286）、§9.4（L355–366）、§11（L397–429）。

**R2 其餘內容全部不變**：§1–§7、§8.1–§8.2、§9.1–§9.3、§10、§12–§17。具體包括 B1、B2、B3、F-01 exact billing 與 numerical targets（RES L209）。

### 7.3 R2 §10 `[CARRIED]`（AUD §B.1）

**R2 §10 不做整章或局部覆蓋。** 理由：
- R2 L370 的 \(F_+(\epsilon)\) 為「同一 candidate positive domain」，已含 §8.3 L271–275 source-binary guard；
- §10 只定義問題，無 unrestricted-optimality 宣稱；
- reference 構造的 Class-C d 值（R2 L308）在任何可設 FeasibilityTol 下都不落入 \((\tau,\tau+g)\)，故解析 \(r_{min}=0\) 在 guard 下成立；
- R2 L395 與 R-07 一致。

CL1 §7.4／R-07 僅為宣稱範圍規則。

### 7.4 CL1 各章規範地位 `[CONSOLIDATED]`

| CL1 章節 | 地位 |
|---|---|
| §4.2、§4.3、§7.4、§9（經修正） | 規範；依 §7.2 第 3 層 |
| §3、§6（R-05a 為證據補記）、§10、§11、§12 | 非規範（RES L213；TA-05） |
| §1、§2、§4.1、§4.4、§5、§7.1–§7.3、§8、§13 | 依原文承接，經 R-03、R-04、R-08、R-10 修正之數學與宣稱敘述以修正後為準；本 Artifact 不另賦予覆寫 R2 之效力 |

### 7.5 G-01 — v7.4 → v8 前瞻方法 successor 與權威承接 `[R2-NEW — NEEDS TARGETED REVIEW]`（governance；PENDING D12）

**R1 文字之地位：** R1 §7.5（L302–326）與 R1 D12 選項 (a)（L393）之「候選研究軌規格；不修訂 v7.4、不重開 §0.1；日後另依 Framework 修訂程序面對 L66 鎖定條款；本 Artifact 不產生該效果」文字，經 FLA 判定為「有效的暫時隔離，但不足以完成本次要求的 successor 機制」，屬 **MAJOR／接受阻擋**（FLA L98、L176）。該文字在本 R2 **不具任何規範效力**，亦不再列為推薦處置；其中「v8 在正式接受與啟用前不是 methodology authority」之隔離事實，改由 §7.5.4-D 承接。

#### 7.5.1 事實（R1 已核；R2 輪以 primary bytes 重核）

- Framework v7.4 §0.1 L66：「下列內容除非發現程式、資料或 source transcription 錯誤，否則不再回到舊版」。§0.1 鎖定清單為 L68–90。其中：
  - **L70**：Layer A 使用 dense \(9\times9=81\) 的 \(\alpha,\beta\) grid 與 case-year 內所有 valid historical outage starts 的 worst-case reserve。
  - **L74（A2 已關閉）**：annual optimization 與 outage replay 是兩個分離的 model stages；annual normal operation 使用 constant worst-case reserve floor。
- Framework v7.4 §7（L1373）至 §7.5（L1475–1514）以外生之 valid-start energy reserve（§7.3，L1415）、瞬時 power adequacy（§7.4，L1461）及全年 reserve floor \(e_t\ge SOC_{\min}E^N+R(\alpha,\beta)\)（§7.5）規範 Layer A。（FLA L69 引作 L1373–1504；§7.5 之「研究意義」說明延續至 L1514。）
- R2 §14 第 1 點（L464）：「舊all-start hard reserve／adequacy轉為aggregate ENS／ε，不同時帶入舊reserve」。R2 L89 研究 grid 為 α∈{0.10,0.25,0.50}、β∈{4,8,12} h。R2 L152：「不得帶回舊 Layer A 的 e_t≥0.10E_B+R(α,β) 或 P_B≥舊 power adequacy。」R2 §14 第 3 點（L466）改為 normal SOC handoff 之 PV-first outage recourse；第 5 點（L468）明確分離 EOB_global／EOB+／RES／ε／fixed-SOC replay。
- 因此差異**不限於 grid 稀疏化**，而涵蓋服務要求之定義（hard all-start adequacy → aggregate ENS／ε）、reserve／power adequacy 下限之存廢，以及 normal operation 與 outage 之聯結（FLA L77）。
- R2 L22 已自述為「對既有 accepted v7.4 的新候選方法 delta，不把 v7.4 Full81 接受狀態轉移給 Phase-1」。
- 註（沿用 R1）：CURRENT_STATE 中的「A2 `HARD_BLOCKED`」是 robustness A2 case scope（STATE L27、L708），與 Framework §0.1 的 A2 方法決策同名但不同義，本項不涉及前者。

#### 7.5.2 分類（FLA L67）

- **實質 methodology successor，加上治理授權變更；不是 implementation correction，也不是錯誤修正。**
- 本 successor **不主張、亦未證明** v7.4 存在程式、資料、公式、source transcription 或 provenance 錯誤；因此不以 PROT §2（L61–79）之錯誤證據路徑重開 v7.4 決策。
- v8 為**明示之新研究問題**：在固定服務定義下，將部分 ENS 與成本之交換納入內生決策（§7.6）；不是對 v7.4 研究問題之更正答案。

#### 7.5.3 控制條款與例外權源

| 條款（primary bytes） | 作用 |
|---|---|
| FW v7.4 §0.1 L66、L70、L74；§7–§7.5 L1373–1514 | 鎖定 v7.4 之 Layer A 方法決策 |
| PROT §2 L65、L67、L79 | 無錯誤證據不得重開 CLOSED／ACCEPTED 方法決策；後續 agent 不同意不足以重開 |
| CONST §7 L251–266 | 同上；「更漂亮的方法」不是重開理由 |
| CLAUDE.md L28 | agent 不得重開 CLOSED 方法決策（含 A2） |
| PROT §1 L34 | source of truth「Unless explicitly superseded by a later accepted artifact」：允許由後續**明示接受**之 artifact 前瞻取代 |
| PROT L95、L322、L735 | candidate 作者不得自我接受；接受者為研究者 |
| PROT §4 L119–144、§5 L146–172 | STOP candidate 不可變；修正一律 additive；歷史不可覆寫 |
| PROT L28、§30 L780–792（含 L789） | 常設治理規則之變更須 additive Protocol revision；改變 acceptance-critical behavior 時須獨立審查 |
| PTR-C L95–108；PTR-A L21–22 | 研究者曾就單一案件記錄限定例外且 `protocol_revision`：None；該案分類為 governance／authorization change，非 methodology change |

**權源分析（PROPOSED；須由 D8-c fresh targeted audit 明確裁定）：**

1. **前瞻取代之依據：** PROT §1 L34 容許後續明示接受之 artifact 取代 methodology source of truth。v8 經 Gate 3 接受並明示 Activation 後成為 current methodology authority，即走此路徑；它**不**追溯改變 v7.4 之 CLOSED／ACCEPTED 狀態。
2. **與 CLOSED 規則之關係：** PROT §2、FW §0.1、CONST §7 均以「重開」為規範對象；現行文字未定義「為新研究問題前瞻採行不同方法並承接主線權威」是否屬於「重開」。本 R2 **不依賴**「不構成重開」之有利解釋：若此承接被解讀為受上述條款限制，§7.5.4 之研究者決定即構成**本案限定例外**（FLA L106）。
3. **例外之權源與缺口（FLAG）：** PROT v1 未明文規定研究者得就方法決策作個案例外。可援引者為：(a) 研究者為唯一接受者（PROT L95、L322）；(b) PTR-C L103 已接受之立場：「Neither protocol makes a prior revision a precondition for an owner's case-specific exception」。但 (b) 之適用對象為 governance／authorization change（PTR-C L106–108），**不是** scientific methodology change；本案屬該先例未涵蓋之類型。故「**是否可不經 Protocol revision，而以本案限定例外處理 methodology successor**」為未決之治理問題，須由 D8-c fresh targeted audit 明確裁定：
   - 若裁定**足夠**：依 D12(a) 辦理；不建立一般例外政策（FLA L96）。
   - 若裁定**不足**：須先依 PROT §30 建立 additive Protocol revision（保留 v1、說明缺陷與理由、依 L789 獨立審查、明示 supersession），經接受後再決定 D12（D12(b)）。**本 R2 不建立、亦不修改任何 Protocol revision。**
4. **字面讀法註記（不依賴）：** FW §0.1 L66 字面為「不再回到舊版」；本 R2 不以此字面讀法主張 v8 不受 L66 限制。
5. **入口文件版本落後：** PROT §1 L36–40 與 §28 L724–725 仍以 Framework／Registry v7.2 為 source of truth；CLAUDE.md L9–11 仍列 v7.3（FLA L53）。此為入口文件落後，不得據此將權威退回 v7.2／v7.3；是否於 Gate 3 以 additive 方式更新入口文件，另行授權，本 R2 不處理。

#### 7.5.4 建議核准後生效之 D12 文字

**A. FLA 建議替換文字** `[FLA-VERBATIM]`（FLA L102–110；本 R2 未改一字）：

> **PROPOSED / NOT ACCEPTED — D12／G-01**
>
> 研究者擬接受的 D1 對象，是以明列 SHA-256 綁定的 R2、CL1、RES 及經審查補正所構成之 Cost–ENS／ε-constraint 研究方法規格。此規格定位為 Framework v7.4 的前瞻方法繼承者，目的為增加固定服務定義下的內生部分 ENS–成本權衡。
>
> 本決定不主張 v7.4 存在錯誤，不追溯重開或撤銷其 CLOSED／ACCEPTED 狀態。研究者須明示核准：僅就本次所列方法差異及未來權威承接，允許在未證明 v7.4 錯誤的情況下採行新研究規格；若此承接被解讀為受到 Framework §0.1、Protocol §2 及相應 CLOSED 規則限制，本決定構成本案限定例外。它不授權其他 CLOSED 決策變更，也不建立一般例外政策。
>
> 規格接受不等於 Framework v8 接受。只有另經文件製作授權、建立 additive Framework v8／Registry／provenance，完成獨立審查及正式接受後，v8 才可依明示生效紀錄成為 current thesis methodology authority；在此前，v7.4 仍為目前 accepted authority。
>
> v7.4 Framework、Registry、EOB／Full81 結果、原始 SHA、Git lineage、manifest、checkpoint 及接受紀錄保持不可變，並在其原始假設下維持歷史有效性。此決定不授權 Git publication、code/data compatibility audit、Coding、Pilot 或任何求解。

**B. 研究者授權文句**（Decision Record 須逐字記錄；如有修改即為新規範文字，依 §16-5 處理）`[R2-NEW]`：

> 本人（研究者）知悉：以 SHA-256 綁定之 Candidate R2（`1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557`）、Class-C Clarification R1（`4fde9052cde3450c9476829d7144d70606d077f54f8b4030a801e5e064b0a878`）、Proposed Acceptance Resolution R1（`3c9e35033c9fab492593b6b056cbcde447ed8a949ac4de8ff1e096e9db5a04c5`）及本 Proposed Acceptance Artifact R2 Candidate（SHA-256 由 Decision Record 記錄）所構成之 Cost–ENS／ε-constraint 方法規格，與 Framework v7.4 §0.1 L70、L74 及 §7.3–§7.5 所定方法不同（差異窮盡列於本 Artifact §7.5.4-C）；且本人未主張、亦未證明 v7.4 存在程式、資料、公式、source transcription 或 provenance 錯誤。本人仍核准：(1) 採行上述規格作為新研究問題之 v8 方法規格；(2) 該規格日後僅能經另行授權、獨立審查、正式接受並明示啟用之 Framework v8，前瞻承接本論文之 methodology authority；(3) 若 (1)、(2) 被解讀為受 Framework v7.4 §0.1、Protocol v1 §2、Constitution §7 或 CLAUDE.md 之 CLOSED 規則限制，本核准僅就 §7.5.4-C 所列差異構成本案限定例外。本核准不修改 Protocol、Framework v7.4 或 Registry v7.4，不授權其他 CLOSED 決策變更，不建立一般例外政策，不追溯取代任何歷史 bytes。

**C. 本案限定 CLOSED 處置清單（窮盡列舉）** `[R2-NEW]`：

| v7.4 鎖定內容 | v8 規格中之處置 | 依據 |
|---|---|---|
| §0.1 L70：dense 9×9 α／β grid | v8 研究 grid 為 α∈{0.10,0.25,0.50}、β∈{4,8,12} h | R2 L89 |
| §0.1 L70：所有 valid outage starts 之 worst-case reserve 作為服務要求 | 改為 aggregate ENS／ε 服務要求 | R2 L152、L464 |
| §0.1 L74（A2）：annual／outage 分離；annual normal operation 使用 constant worst-case reserve floor | 不帶入 reserve floor；normal SOC handoff 之 PV-first outage recourse；EOB_global／EOB+／RES／ε／fixed-SOC replay 明確分離 | R2 L152、L466、L468 |
| §7.3–§7.5（L1415–1514）：外生 valid-start energy reserve、瞬時 power adequacy、全年 reserve floor 與由此導出之 \(E^N\) 下限 | v8 不繼承；服務要求由 ENS cap 決定 | R2 L152 |

- **不在本處置範圍內：** Framework v7.4 §0.1（L68–90）上表以外之全部鎖定內容，對 v8 繼續有效，除非另經研究者明示處置並審查。R2 §14 第 6 點（L469）亦聲明不改效率、SOC、monetary basis、κ evidence route 與 PNNL cost／Xu semantics。
- **待審查確認之邊界項：** §0.1 L72 後句「normal-operation reserve 必須位於 technical SOCmin 之上」在 v8 不設 reserve floor 時之適用方式（是否為空集合條件，或須列入本處置），以及 L87（Layer B 固定 Layer A 設計）對 v8 之適用，由 D8-c fresh targeted audit 判定；本 R2 不擅自處置。
- 後續若發現 R2 規格與上列以外之 §0.1 鎖定內容衝突，即 STOP，不得以本例外涵蓋（§16-7）。

**D. 兩階段接受與啟用** `[R2-NEW]`：

| 階段 | 對象 | 必要條件 | 效果 | 不產生之效果 |
|---|---|---|---|---|
| Gate 2：Methodology／Specification Acceptance | R2＋CL1＋RES＋本 Artifact R2 | D8-c fresh targeted audit 明確 PASS；研究者 Acceptance Decision Record（綁定各 SHA、D1～D12 選擇、§7.5.4-B 文句） | 規格成為**已接受之 v8 方法規格**，可作為 Gate 3 起草依據 | 不是 Framework v8 接受；v7.4 仍為 current methodology authority；不授權 Coding／Pilot／求解／Git |
| Gate 3：Framework v8／Registry／Provenance Formal Acceptance | 另行建立之 additive Framework v8、Registry（或 delta）、methodology delta matrix、provenance／manifest | 另行之文件製作授權；candidate → 獨立審查 PASS → 研究者正式接受 | v8 文件成為已接受之 Framework／Registry | 接受本身不等於啟用 |
| Activation | 明示生效紀錄（形式於 Gate 3 決定，例如 canonical pointer successor） | Gate 3 接受後，另行明示啟用 | **自此** v8 成為 current thesis methodology authority；v7.4 轉為 historical accepted predecessor | 不追溯；不授權 Coding、Pilot、Production、Git publication |

- Activation 之前，任何文件、程式或報告不得將 Phase-1／v8 規格稱為 current thesis methodology authority，亦不得稱 v7.4 已被取代。
- Gate 3 與 Activation 均**不由本 R2 或 Gate 2 自動啟動**；各需研究者另行明示授權。

**E. 歷史保留與禁止追溯取代** `[R2-NEW]`：

- Framework v7.4、Registry v7.4 及其 acceptance closures／manifests、Full81 run `20261008T183934456307Z_a6826f4828` 及其 acceptance（G1R）、EOB 結果、canonical pointer R1／R2、checkpoints、Git lineage 與所有原始 SHA，保持 byte-identical，並在其原始假設下維持歷史有效性。
- 禁止以 v8 文件、v8 結果或任何後續 artifact 覆寫、刪除、改名、就地修補或追溯重新標記上述歷史 bytes；禁止將 v7.4 描述為「失敗」「無效」或「已撤銷」。
- v7.4 與 v8 之比較須標明兩者為不同研究問題與不同可行域；差異不得全部歸因於單一變更（§7.6）。

**F. 本決定不授權**（FLA L110、L221）：Framework v8 文件建立、任何 acceptance／promotion、Git publication、legacy code/data compatibility audit、Coding、PV0／PV scenarios、Type-3、classifier 修改及所有模型／求解工作。

#### 7.5.5 與 Framework v7.4 之 precedence

§7.2 之 precedence chain 只在 Phase-1／v8 規格文件之間適用。對 Framework v7.4／Registry v7.4：Activation 之前，v7.4 為唯一 current accepted methodology／evidence authority；Gate 2 已接受之規格只拘束 v8 軌之文件與 Gate 3 起草，不修改、亦不適用於 v7.4 及其結果。

### 7.6 v8 successor 科學理由（Root-Cause 更正版；PROPOSED）`[R2-NEW — NEEDS TARGETED REVIEW]`

**證據分級**（依 FLA L180–185，並以 RCA 擷取文字補充行號）：

| 等級 | 內容 | 來源 |
|---|---|---|
| PROVEN（formulation） | v7.4 以外生 all-valid-start adequacy 與 constant reserve floor 規範 Layer A；R2 改為 aggregate ENS／ε 與聯結之 outage recourse | FW §0.1 L70、L74、§7.3–§7.5；R2 L152、§14 |
| OBSERVED（RCA 轉述；本輪未由 Full81 primary outputs 重算） | 年度總成本 82.842–139.265 百萬 NTD-2023／年，全距 56.423 百萬（RCA L11、L44、L53）；resilience premium 16.220–72.643 百萬／年，為 EOB 之 24.346%–109.037%（RCA L45、L54、L70、L78）；能量容量 16.251–75.697 MWh、功率 2.914–4.985 MW（RCA L13）；**正常營運成本合計**跨格全距 14,297.98 NTD-2023／年（約 14,298），CC 全距 5.557 kW（RCA L12）；未辨認出清楚 knee（RCA L130，為本 grid 之描述性判讀） | RCA（§1.6） |
| CONDITIONAL | 經核准之 v8 規格可在指定條件下研究部分 ENS–成本交換；實際曲面形狀待未來授權實驗 | FLA L184 |
| NOT VERIFIED | `ab9aa820…` 原始報告 bytes 及其審查獨立性；constant reserve floor 為唯一成因；移除 floor 之特定節省額；v8 經濟優勢、Pareto knee | FLA L185；RCA L17；§1.6 |

**建議科學理由文字** `[R2-NEW]`（依 FLA L189 改寫：只更新證據來源描述並補明「非扁平」與「不保證成本降低／unrestricted optimality」，未改其主張）：

> Framework v7.4 以所有合法停電起點均須滿足指定服務比例與時長的要求，研究其設備容量及年度成本。依 Root-Cause 審查（operator-extracted Codex final answer；本輪未由 Full81 primary outputs 重算；原上傳副本 bytes 未驗證）之轉述，81 案年度總成本與韌性增額成本均有顯著變動，並非扁平；最壞情境 adequacy 要求強烈影響 BESS sizing 與成本，而正常營運成本合計及契約容量的跨案例變動較有限，其中約 14,298 NTD／年指正常營運成本合計的全距，不是每個分項的全距。擬議 v8 將研究問題擴展為固定服務定義下的內生部分 ENS–成本權衡；此轉向不表示 v7.4 失效，也不證明 reserve floor 是唯一原因，不保證 v8 出現 Pareto knee 或成本降低，亦不構成 unrestricted optimality 宣稱（§8）。新規格的 \(r_{ENS}\) 為 deterministic aggregate service metric，並非 EENS 或可靠度機率；新舊比較亦不能將所有差異歸因於 ENS 單一變更。

**宣稱限制：** 不得以「v7.4 年成本幾乎不變」「premium 平坦」「v7.4 失敗」「v8 必然更便宜或具有 knee」作為已證明結果。若正式 v8 理由須將上列數值列為直接驗證證據，須先取得原始報告 bytes，或另行授權由 Full81 primary outputs 重算（FLA L191）。

---

## 8. Guard-restricted 最適性宣稱（核准後之宣稱規則）`[CONSOLIDATED]`

1. **宣稱範圍（R-07）：**
   - EOB0 的最適性只在 \(F_0\cap X_g\) 上成立。
   - EOB+、RES stage 2、ε-frontier、lexicographic endpoints 只在 \(F_+(\epsilon)\cap X_g\) 上成立。
   - Global EOB 定義於 \((F_0\cap X_g)\cup(F_+(1)\cap X_g)\)。
2. **2.001 NTD 誤差界（CL1 L260、R-03）：** R2 §11 的約 2.001 NTD-2023/year 誤差界只相對於 \(C^*_{guard}\)：\(C(x_2)-C^*_{guard}\le(U^{guard}_C-L^{guard}_C)+\delta_C+\tau_C\)。此界不是 unrestricted physical domain 的誤差證書。
3. **下界記號（R-03）：** \(L^{guard}_C\) 不得作為 \(\inf_\tau\) 或 \(\inf_{strict}\) 的下界。不等式鏈為 \(C^*_{overlap}\le C^*_{closed}\le\inf_\tau\le C^*_{strip}\le C^*_{guard}\)（stage-1 cost minimization；R-08 own-pricing cap 下方向仍成立；不適用 stage 2）。
4. **不得宣稱 guard 無影響（CL1 L261；RES §5-1）：** 不得宣稱 \(C^*_{guard}=\inf_\tau\)，或兩者差為 0。T5 的約 0.0054 NTD/年只能以「在假設 H 下」的條件形式引用；H 在最佳化後全年解上為 NOT VERIFIED。
5. **計價 formulation（R-04、TA-03）：** 閉合方案的精確性只在 component 層級成立，年度層級須所有 Class-C component 同向（§5.1）。方案 B 不得作為計價 formulation；方案 C 在 October 方向會低估，只能作 relaxation／lower-bound 工具；本研究不採用 C 計價。
6. **帳單報告與揭露（R-06、TA-04）：**
   - 論文報告之帳單為 τ-convention 帳單（BRIDGE L21–30），應如此揭露。
   - τ 與 strict 帳單只在 \(0<d\le\tau\) 時不一致；此時單一設計的差額為 \((r_e-r_l)W\)，\(|r_e-r_l|=10.97458029197081\) NTD-2023/kW-month。
   - 約 0.054 NTD/年只是最適值之間的條件界，NOT VERIFIED。
   - L2 是 project rule，不是台電官方完整跨季公式；τ、g 是數值實作慣例。
7. **數值宣稱綁定 run 設定（R-07）：** 每個數值宣稱綁定該 run 實際記錄的 FeasibilityTol、τ、g 與實作版本身分。不同 τ／g 的 run 不得視為同一可行域。
8. **歷史結果（R-10、CL1 §8）：** solver 回報之 OPTIMAL 只對其所解之 formulation 可行域成立。本宣稱規則不修訂任何歷史 acceptance，也不宣稱 guard 必然影響或必然不影響歷史最適成本。

> **Guard-restricted mathematical optimality ≠ unrestricted physical-domain optimality.**

---

## 9. Pilot entry safeguards（PV0 Pilot 仍 NOT AUTHORIZED）`[CONSOLIDATED]`

PV0 correctness Pilot 正式授權前，下列各項須已由研究者固定（RES §6，經本草案更新）：

1. **Fail-closed 規則：** §4.2 R-05b（as amended）（D6）。
2. **Big-M 版本（D3）：**
   - 建議採 baseline：\(M_{ch}:=\bar P\)；\(M_{dis,t}:=\min(\bar P,L_t)\) 或共同 \(M_{dis}:=\min(\bar P,L_{max})\)。
   - CL1 L299–303 tightening 亦已證明有效，可作替代。
   - 任何其他更緊之界須依 R-02 另經證明與核定；只對 stage-1 argmin 成立之界不得用於 stage-2 cost band。
3. **每次 run 保留：** FeasibilityTol、IntFeasTol、τ、g、實作版本身分（R-07）。
4. **Classifier：** 使用 live classifier 原規則，不得放寬（CL1 L318、R-05b）。
5. **另行授權：** Pilot 的範圍、cell、時間上限與 STOP 條件，另以 Pilot 授權文件明定。該文件若偏離 §4.2，須逐項明示並經研究者核准（§4.2-5）。
6. **授權時身分核對：** Pilot 授權當時，須重新核對 §1.1 四份文件、本草案與 Acceptance Decision Record 的 SHA-256；不符即 STOP（PROT L707「wrong SHA」）。

---

## 10. Scientific residual limitations（核准後仍然存在）`[CARRIED]`＋`[CONSOLIDATED]`

1. Guard-restricted optimality ≠ unrestricted physical-domain optimality（§8）。
2. Type-3 全年 certification：NOT VERIFIED（D9 預設不授權）。
3. H-PV 在最佳化後全年解上：NOT VERIFIED。EXP4b 只在 reference dispatch 上觀察到 8/8 最大時刻 PV>0。若最大時刻落在夜間（PV=0），H-PV 在該點不成立（條件句；AUD N-3）。
4. Phase-1 全年 Class-C d／W 行為：NOT VERIFIED（§6.3）。
5. τ-convention 與 strict 在 \(0<d\le\tau\) 時偏離（§8-6）。
6. L2 為 project rule；τ、g 為數值慣例（BRIDGE L9–19；S12 `OFFICIAL_CROSS_SEASON_AGGREGATION_NOT_EXPLICITLY_LOCATED`）。
7. 隔離實驗（1,316 次 optimize）未經獨立重跑；EXP5b 為月度簡化模型；toy 數值不是 NTUST 年成本。
8. FeasibilityTol = 1e-9 時出現決定性的錯誤 INFEASIBLE（EXP6）；調緊容差不是安全修正。
9. R2 §16 L500 其餘 nonblocking limitations 不變。
10. **審查獨立性：** R2→CL1→RES 鏈無跨模型審查；FLA 為唯一跨工具審查，範圍有限且 verdict 為 STOP；本 R2 尚未審查；同模型相關錯誤風險存在（§3.1、§3.7）。
11. **證據 custody：**
    - R2 與 CL1 的審查報告為 conversation-only。
    - 隔離實驗目錄位於 `%LOCALAPPDATA%\Temp`。Storage Sense 已啟用 temp-file 清除（registry `StoragePolicy` 04=1；2048=0，即低磁碟空間時執行；鍵值語義依一般 Windows 文件理解，本輪未查官方文件），故有被自動刪除的風險。
    - `Downloads` 自動清除為關閉（32=0）。
    - Downloads 中的文件與審查皆非 Git-durable，亦無備份副本（D11）。
    - FLA 與 RCA 原文僅存於 Codex rollout（`~/.codex/sessions`）；本輪擷取副本位於 session scratchpad（Temp），均非 Git-durable（D11；§1.6）。
12. **Framework 邊界與權威承接：** Phase-1／v8 規格與 Framework v7.4 §0.1 L70、A2 L74 及 §7.3–§7.5 之差異，依 D12 以前瞻 successor 與本案限定處置辦理（§7.5）；例外權源是否足夠待 D8-c fresh targeted audit 裁定（§7.5.3-3）；v8 在 Gate 3 接受並明示 Activation 前不是 current methodology authority。
13. **Root-Cause 證據限制：** 原上傳副本（`ab9aa820…`，549 行）bytes 未找到；RCA 為 operator-extracted Codex final answer，與該副本之同一性未確立；§7.6 數值為轉述，未由 Full81 primary outputs 重算（§1.6）。

---

## 11. User decision register（全部 RECOMMENDED / PENDING USER APPROVAL）

| ID | 決定事項 | 選項 | 建議 | 依據 | 狀態 |
|---|---|---|---|---|---|
| **D12** | G-01：v7.4 → v8 前瞻方法 successor 與權威承接 | (a) 依 §7.5.4 核准前瞻 successor：逐字記錄 §7.5.4-B 授權文句、§7.5.4-C 本案限定 CLOSED 處置、§7.5.4-D 兩階段接受與 Activation、§7.5.4-E 歷史保留；(b) 先依 PROT §30 建立並審查 additive Protocol revision（successor／例外機制），再決定 D12；(c) 維持 candidate-only 隔離（R1 原 D12(a)；FLA 判定不足以承接主線）；(d) 不接受 | **(a)**；若 D8-c 審查裁定本案限定例外權源不足，改 **(b)** | §7.5；FLA §C | PENDING；`[R2-NEW — NEEDS TARGETED REVIEW]` |
| **D8-a** | 本次審查獨立性（分層處置） | (i) 依 §3.4、§3.5 及 §3.7：L1 如實認定 FLA 為有限跨代理審查；L2 由研究者作本案專屬充分性決定／限定例外（明列文件、範圍、未驗證身分）；不套用 Pointer R2 先例；(ii) 改要求對 R2／CL1／RES 補作 cross-model 審查 | **(i)** | §3.7；FLA §D；研究者立場（§3.3） | PENDING |
| **D8-b** | 「依額度選 Codex 或 Claude Code」作為常設政策 | 記錄立場，另依 PROT §30 修訂／暫不處理 | **記錄立場；另行修訂** | PROT L28、L780–792 | PENDING；本 Artifact 不生效 |
| **D8-c** | PROT L689–691 PASS 詞彙；R2 補正後審查 | **強制（無替代選項）**：fresh independent targeted audit 對本 R2 之 `[R2-NEW]`／`[FLA-VERBATIM]` 條文及交叉引用（範圍見下）產出明確 `<TOPIC> — PASS／STOP`。R1 之選項 (ii)（CONDITIONAL PASS 即足夠）**刪除**；R1 選項 (i) 之範圍由下列範圍取代 | **強制**；審查者由研究者依 §3.7-4 選定（建議 Codex） | FLA L140、L218 | PENDING（審查未執行） |
| D1 | 接受 R2 + CL1 + RES（含本 Artifact R2 精確修正）作為限定 guard domain 之 Cost–ENS／ε-constraint 方法規格（Gate 2；v8 方法規格；**不等於** Framework v8 接受） | 接受／修改後接受／不接受／暫緩 | **接受**（須同時核定 D12、D8，且已取得 D8-c 明確 PASS） | AUD §D；FLA L165 | PENDING |
| D2 | Precedence 範圍；R2 §10 處理 | 照 §7.2 列／擴及 §10／其他 | **照列；R2 §10 不覆蓋** | AUD §B.1；§7.3 | PENDING |
| D3 | Big-M 版本 | baseline／CL1 tightening／暫不決定 | **Baseline** | AUD §D；§9-2 | PENDING |
| D4 | Guard-restricted 宣稱範圍（CL1 §7.4，經 R-03、R-07 修正） | 接受／不接受 | **接受** | AUD 矩陣 R-03、R-07 PASS；§8 | PENDING |
| D5 | R-04 數學宣稱修正（經 TA-03 修正） | 接受／修改 | **接受** | §5 | PENDING |
| D6 | PV0 Pilot fail-closed rule | 採 §4.2／另定 | **採 §4.2** | §4 | PENDING |
| D7 | R-06 τ／strict 揭露（經 TA-04 修正） | 接受／另定 | **接受** | §6、§8-6 | PENDING |
| D9 | Type-3 certification、classifier 修改 | 均不授權／另行授權 | **均 NOT AUTHORIZED** | RES §8；CL1 §10 | PENDING |
| D10 | 承接方式 | Resolution＋Acceptance Artifact／R2 successor（R3） | **Resolution＋Artifact，不建 R3** | AUD §D | PENDING |
| D11 | Audit 紀錄持久化 | 授權／不授權 | **授權**，範圍見下 | §10-11 | PENDING |

**D11 建議範圍**（每項皆須研究者另行授權後才執行；本輪均未執行）：
1. 將 R2 Codex 審查（rollout `01a16701…`）與 CL1 審查（session `180c3fec…`）的最終報告抽出為檔案。須保留來源 transcript 完整路徑、SHA-256 與抽取方法，由研究者選定方式；transcript 不由 agent 主動讀取。（R2 輪：FLA 與 RCA 已依研究者單次授權擷取至非 durable 暫存，§1.6；R2／CL1 審查仍未擷取。）
2. 將 §1.1 四份文件、本草案、Decision Record，以及 `%LOCALAPPDATA%\Temp` 隔離實驗目錄（176 檔，含 MANIFEST），複製到 durable custody，並附 SHA256SUMS 與讀回驗證。
3. 任何 repository 內收錄（例如 `docs/` 或 Git commit）屬 repository mutation，須另行授權。

**D8-c 強制 fresh targeted audit 範圍** `[R2-NEW]`：
1. **身分與 diff：** R1 仍為 `d406bd63…`；本 R2 之 SHA 與 bytes；R2 對 R1 之差異僅限 identity／diff report 所列項目；未列為變更之章節與 R1 逐 byte 相同。
2. **§7.5 G-01：** 分類；控制條款引用與 primary bytes 一致；**明確裁定 §7.5.3-3 之例外權源（本案限定例外足夠，或須 PROT §30 revision）**；§7.5.4-C 處置清單相對 FW §0.1 L68–90 及 §7 之完整性（含 L72 後句與 Layer B 相關項）；兩階段接受與 Activation；歷史保留；確認 R1 candidate-only 文字未以任何形式殘留為規範。
3. **§3.7 D8：** 獨立性表與 FLA、AUD、R1 §3.1 一致；無超出證據之 cross-agent／cross-model 宣稱；Pointer R2 僅作機制先例。
4. **§7.6：** 數值與 RCA 擷取文字一致；證據分級；無「扁平」、knee、成本降低或 unrestricted optimality 宣稱；Root-Cause custody 限制已揭露。
5. **§1.6 custody：** 依所列方法由 rollout 重現 FLA／RCA 擷取 SHA（審查者讀取 rollout 須研究者另行授權）。
6. **§0、§11、§12、§16 一致性：** D1～D12 全部 PENDING；無自我接受；無 v8 升格。
7. **範圍外：** R2 Spec 數學、CL1 guard 公式、TA-02～TA-05 內容（只做逐 byte 比對）、Big-M baseline、D6 規則、Type-3、Full81 結果。

**建議決策順序：** D8-c fresh targeted audit（對本 R2；須明確 PASS，並裁定 §7.5.3-3 例外權源）→ D12（若審查裁定權源不足，改 D12(b)）→ D8-a／D8-b → D1（Gate 2）→ D2～D7、D9～D11。Gate 3（Framework v8）與 Activation 不在本序列內，另行授權。

---

## 12. Acceptance 與 Coding 之隔離 `[CARRIED]`

| 項目 | 本草案核准後之狀態 |
|---|---|
| Phase-1 specification acceptance（Gate 2） | 由 D1（連同 D12、D8，且 D8-c 明確 PASS）決定；**不等於** Framework v8 接受 |
| Phase-1 formal implementation（Coding） | **NOT_YET_AUTHORIZED**：須在 D1、D8 完成後另行明示授權（RES L307） |
| PV0 correctness Pilot | **NOT_YET_AUTHORIZED**：另需 §9 各項與 Pilot 授權文件 |
| Production／re-freeze | **NOT_YET_AUTHORIZED** |
| Type-3 certification | **NOT_YET_AUTHORIZED**（D9） |
| Accepted core／classifier 修改 | **NOT_YET_AUTHORIZED**（D9） |
| Framework v8／Registry／Provenance 建立、審查與接受（Gate 3） | **NOT_YET_AUTHORIZED**；須另行授權（D12；§7.5.4-D） |
| v8 成為 current thesis methodology authority | **NOT YET**：僅於 Gate 3 接受並明示 Activation 後（§7.5.4-D） |
| v7.4 Framework／Registry／結果之修改或追溯取代 | **PROHIBITED**（§7.5.4-E） |
| Protocol revision（D12(b) successor／例外機制） | **NOT_YET_AUTHORIZED** |
| CURRENT_STATE、pointer、Git 收錄 | **NOT_YET_AUTHORIZED**（repository mutation） |
| Protocol revision（D8-b） | **NOT_YET_AUTHORIZED** |

**Specification acceptance 不會自動啟動 Framework v8（Gate 3）、Activation、Coding、Pilot、Production 或 Type-3**；各自需要獨立授權。

---

## 13. Informational reading notes（承接 AUD N-1～N-7 之摘要；非規範、不需補正）`[CARRIED]`

| ID | 位置 | 讀法 |
|---|---|---|
| N-1 | RES L184 | τ 亦依 demand scale（CORE L141–146、L1239）；在本資料下數值可忽略 |
| N-2 | R-03 | 對照表非窮盡；R2 L404、L413、L425 與 CL1 L319 同符號同義 |
| N-3 | RES L223 | 「夜間 off-peak 最大時刻 PV=0」讀為條件句（§10-3） |
| N-4 | RES L154 | 「EXP0 … 源自 v7.3 模型」讀為「既有 accepted（pre-Phase-1）模型」 |
| N-5 | RES L171 | 3,843.73 NTD 為 S12 中 B／C 設計之 τ 與 strict 帳單差，非 A 之設計 |
| N-6 | RES L91 | Branch 0「Big-M 不適用」指 \(M_{ch},M_{dis}\)；billing 常數仍需 \(\bar p^{grid}_t=L_t\) |
| N-7 | RES L78 | 「取代 CL1 L304 全句」指 F-02 所引之句；L304 首、末句保留 |

---

## 14. Writer 自我檢查：TA closure mapping（author-side；不是獨立驗證）

逐字對照方法：以 `python -I` 腳本自 AUD 抽出 TA-01～TA-05 之規範文字（AUD 中以 `> ` 開頭之引用行，以及 TA-04 兩段「」內文字），逐行檢查是否完整出現於本草案。結果記錄於交付回覆，並可由任何人以同一方法重現。

| TA | AUD 要求 | 本草案處理 | 位置 | 逐字 |
|---|---|---|---|---|
| TA-01 | D8 紀錄文字；引用 L28、L736、L803、CONST §19；增列 I-5 | §3.4 逐字；§3.2 逐字引用全部條文；§3.5 例外並列；D8-a／b／c。I-5 安排即 D8-a(i) | §3、§11 | 是 |
| TA-02 | 觸發集、診斷、STOP 範圍、狀態標記 | §4.1 逐字；§4.2 生效條文；§4.3 差異（STOP 範圍為研究者同等或更嚴版本） | §4 | 是（§4.1）；§4.2 有一處研究者差異 |
| TA-03 | 取代 RES L134 | §5.1 逐字 | §5 | 是 |
| TA-04 | 取代 RES L154、L171 | §6.1、§6.2 逐字；§6.3 保留 d=0、W=657.064 | §6 | 是 |
| TA-05 | R-01 含 §4.3；R-05b 規範地位 | §7.1 逐字；§7.2 鏈；§7.4 地位表 | §7 | 是 |
| （新） | — | G-01 → v7.4→v8 前瞻 successor（FLA STOP 後改寫） | §7.5、§7.6 | `[R2-NEW — NEEDS TARGETED REVIEW]` |
| D8（R2） | — | FLA 建議之分層 D8 處置 | §3.7 | `[FLA-VERBATIM]`＋`[R2-NEW]` |

自我檢查限制：R1 作者與 TA 文字作者為同一 session（§3.1），故本表不構成獨立驗證。FLA（L144–155）已對 R1 完成 TA-01～TA-05 機械與語義 parity 檢查（TA-01 條文 PASS、TA-02～TA-05 PASS）。R2 輪以機械比對確認 §3.2–§3.4、§4、§5、§6、§7.1、§7.3、§7.4、§8、§9、§13 與 R1 逐 byte 相同；此為 R2 作者端自查，不構成獨立驗證；D8-c 強制審查用以補足。

---

## 15. Provenance 與 integrity

**R2 輪（2026-10-24）：**

- 新增 candidate 檔案：`C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R2_Candidate_2026-10-24_DRAFT.md`（repository 外）；另依任務授權於同目錄建立 identity／diff report。R1 未修改（交付前重新雜湊確認）。
- 建立方式：以 `python -I` 讀取 R1 bytes（先驗證 SHA），套用逐條斷言唯一出現之字串替換後以獨占建立方式寫出；未替換部分與 R1 逐 byte 相同（§14）。
- 操作：SHA-256／`wc`；`sed`／`grep` 檢視 primary bytes；`git rev-parse`、`git status --porcelain`、`git for-each-ref`、`git ls-tree`、`git diff --stat`（唯讀）；依研究者單次授權自兩份 Codex rollout 擷取 final answer（§1.6），擷取副本置於 session scratchpad。
- 為定位 R1 路徑，以 R1 SHA 搜尋 Claude Code transcript，只讀取含該 SHA 之紀錄片段與其 `file_path` 欄位；未閱讀其他對話內容。session 開始時自動載入研究者 project-memory 索引，並讀取其中 transcript custody 規則一則。
- 計數：Existing files modified = 0；Repository modified = 0；Git mutations = 0；Framework v8 created = 0；Acceptance Decision Record created = 0；Model builds = 0；Solver calls = 0；Production runs = 0；Coding = 0；Self-acceptance = 0。
- Repository：branch `thesis-v7`，HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`；`git status --porcelain` 雜湊 `e2c74e093887272558d88751adb7668fe0b5023c1fa3959793b983341c277f1c`（16 項），與 R1 輪相同。
- 本檔不嵌入自身 SHA；交付回覆與 identity report 另行提供。

**R1 輪（2026-10-23；歷史紀錄，逐字承接）：**

- 本輪唯一新增檔案：`C:/Users/Iris C/Downloads/Iris_Phase1_Proposed_Acceptance_Artifact_R1_2026-10-23_DRAFT.md`（repository 外）。
- 本輪操作皆為唯讀：
  - SHA-256 與 `wc`；
  - `sed`／`grep`／`nl` 檢視；
  - `unzip -p` 以 stdout 讀取 R2 S30 handoff；
  - `git rev-parse`、`git status`、`git diff --quiet`；
  - `reg query`（Storage Sense）；
  - 交付前之 `python -I` 逐字比對腳本（置於 session scratchpad）。
- 未讀取任何 transcript 內容。
- 計數：Existing files modified = 0；Repository modified = 0；Git mutations = 0；Model builds = 0；Solver calls = 0；Production runs = 0；Coding = 0；Self-acceptance = 0。
- Repository：branch `thesis-v7`，HEAD `5a53f5f30e260cb61df4ff3e8ea5062b6220c10f`，`git status --porcelain` 雜湊 `e2c74e093887272558d88751adb7668fe0b5023c1fa3959793b983341c277f1c`（16 項，與 session 開始時一致；唯一既有 modified 為 `results/provenance/main_full81_authorization_r2/main_full81_authorization.json`，非本輪造成）。
- 本檔不嵌入自身 SHA，以避免循環；交付回覆另行提供 bytes 與 SHA-256。

---

## 16. STOP rules

1. **本輪：** 本草案建立後即停止。不得 self-accept、不得以本草案作為 Coding／Pilot 授權。
2. **決策時身分核對：** 研究者記錄 Acceptance Decision Record 前，須重新核對 §1.1 四份文件與本草案的 SHA-256。任一不符即 STOP，不得記錄 acceptance（PROT L707）。
3. **文字被否決或修改：**
   - 若研究者否決任何 `[AUDITED-VERBATIM]` 或 `[FLA-VERBATIM]` 文字、§3.7、§4.2、§7.5 或 §7.6，即 STOP，以 additive successor 處理。
   - 若研究者選擇修改後接受，修改文字視為新規範文字，依第 5 點處理。
   - 兩種情形皆不就地修改本草案。
4. **強制審查：** D8-c fresh targeted audit 結果若非明確 PASS（包括 STOP 或 CONDITIONAL PASS），不得記錄 D1 acceptance；審查若裁定 §7.5.3-3 之本案限定例外權源不足，不得以 D12(a) 記錄 acceptance。
5. **新規範：** 若 Decision Record 引入本草案未涵蓋的新規範文字，該部分須另行 targeted review。
6. **治理衝突：** 任何後續步驟若觸發 PROT §27 STOP condition，即停止並回報。
7. **CLOSED 處置範圍：** 若發現 Phase-1／v8 規格與 §7.5.4-C 所列以外之 Framework v7.4 §0.1 鎖定內容衝突，即 STOP；不得以本案例外涵蓋。
8. **Gate 3／Activation：** 本 R2 及其 Decision Record 均不啟動 Framework v8 之建立、接受或 Activation；任何文件不得在 Activation 前將 v8 稱為 current thesis methodology authority。

**PROPOSED ACCEPTANCE ARTIFACT R2 CANDIDATE — PROPOSED / NOT ACCEPTED / PENDING FRESH INDEPENDENT TARGETED AUDIT / PENDING USER APPROVAL**

**完成本文件即停止。NO REPOSITORY MUTATION / NO GIT MUTATION / NO FRAMEWORK V8 / NO ACCEPTANCE DECISION RECORD / NO MODEL BUILD / NO SOLVER / NO PRODUCTION RUN / NO CODING / NO SELF-ACCEPTANCE。**
