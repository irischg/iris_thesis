# Iris Thesis — Phase-1 Class-C Guard Additive Clarification R1

**日期：2026-10-23（Asia/Taipei）**
**狀態：ADDITIVE CLARIFICATION R1 — DRAFT / NOT ACCEPTED / PENDING TARGETED INDEPENDENT AUDIT**
**文件類型：** 附加於 Candidate R2 的 additive clarification。本文件不是 Candidate R3，不取代 R2、Framework v7.4 或 Registry v7.4，也不是 implementation、執行授權或 acceptance。

---

## 1. 文件身份與 parent

| 項目 | 值 |
|---|---|
| 正式名稱 | Iris Thesis Phase-1 Class-C Guard Additive Clarification R1 |
| 檔名 | `Iris_Phase1_ClassC_Guard_Additive_Clarification_R1_2026-10-23_DRAFT.md` |
| Parent | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md`，SHA-256 `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557`，40,221 bytes（本輪已重新核對） |
| Parent 狀態 | CANDIDATE R2 / NOT ACCEPTED / PENDING INDEPENDENT STATIC AUDIT（R2 第 4 行，未變） |
| 處理對象 | 2026-10-23 R2 Independent Static Audit 的 R2-N01（MODERATE／CARRIED）與 R2-N02（MINOR／OPEN wording） |
| 作者身份 | 本文件、其所依據的 Historical Decision Recovery 及隔離實驗，均由同一 Claude Code session 撰寫或執行。**作者不是本文件的獨立審查者。**依 Constitution 與 Version/Provenance Protocol，作者的一致性檢查不構成 PASS 或 ACCEPTED。 |

本文件**不改寫** R2 的任何文字。凡寫「建議 successor 使用以下文字」之處，都只是供未來另行授權的 R2 successor 引用的候選文字。

---

## 2. Scope 與 governance

**本文件做的事：**

1. 把 R2 §8.3 已採用、繼承自 accepted core 的 Class-C source-selection guard，正式寫明為求解前的可行域限制（feasible-domain restriction）。
2. 依證明強度，整理 2026-10-23 隔離實驗的發現。
3. 為 Phase-1 的 EOB+、Global EOB、RES、ε-frontier、lexicographic endpoints 與 R2 §11 的成本近似界，固定 guard-restricted 宣稱邊界。
4. 記錄既有 v7.3 accepted results 的宣稱邊界。
5. 提供 R2-N02 的精確替換文字。
6. 列出可選的未來工作與尚待使用者決定的事項。

**本文件不做的事：**

- 不修改 accepted core、Framework、Registry、R2、R1、參數、資料、測試、classifier、Git，也不修改任何歷史 manifest 或 acceptance。
- 不新增或執行 MILP 或 solver。本輪 model builds 與 solver calls 皆為 0。
- 不撤銷、也不重新解讀任何歷史 acceptance。
- 不修改 R2 中已收斂的方法內容：B1（zero／positive branches 與 10 kW／20 kWh floors）、B2（analytical zero-ENS 證明與 finite cost domain、九組 certificates）、B3（normal dispatch、Xu states、fixed-PV outage recourse），以及 F-01 §8.3 transition settlement（2026-10-23 Codex follow-up 中標記為 B4）的數學 contract。上述內容維持 R2 原文。

**治理依據：** Version/Provenance Management Protocol v1 §5（additive-only correction；candidate 不可 self-accept），以及 Response Mode and Research Governance Constitution（independent audit 必須與作者或實作 agent 分離）。

---

## 3. 歷史動機與已回收的決策邊界

證據身份分為兩類：**正式檔案**（repository 中有 commit 或 hash）與 **conversation-only transcript**（Codex 或 Claude 的本機 session log，沒有正式 acceptance record）。

| 日期（UTC） | 事件 | 證據身份 |
|---|---|---|
| 2026-09-03 | r5 transition formulation 使用 `math.nextafter` 表示嚴格邊界，加上 76 個 indicator。單案求解 900 s 仍無 incumbent | transcript：Codex 主 session `rollout-2026-08-26T21-12-11-01a03e33…jsonl`（SHA `70568f42…7ad6`） |
| 09-04 05:10 | Codex 稽核建議以等價 formulation 取代 r5。理由：`nextafter` 的間距 2.1e-22 kW，遠小於 FeasibilityTol，solver 無法區分；且 epigraph 可以虛增 seasonal maximum | 同上 transcript |
| 09-04 13:29 | 研究者下達 Candidate-1 指令。§6 授權「explicit solver-safe band … documented as a numerical implementation convention」，並要求「the optimizer must not freely select the cheaper rate」 | transcript 附件 `attachments/77d9c823…/pasted-text.txt`（SHA `74a01689…ad73e`） |
| 09-04 13:50 | Codex sub-agent 設計出 guard：`B<d<B+g ⇒ NUMERICAL_BOUNDARY_UNRESOLVED` | transcript（主 session 第 2384 行） |
| 09-04 14:15 | Codex sub-agent 指出 guard 是「不可行缺口… 可能改變可行域與最優解」。同一輪隨即因 usage limit 中斷，**此警告未轉達研究者** | transcript：主 session 第 2771、2773 行；review session `01a06cbe…`（SHA `fa07aa9b…a2a9f`） |
| 09-05 05:54 / 05:58 | 研究者收到的報告只有一句：「explicit solver-safe feasibility exclusion, not a tariff rule」。研究者回覆將「guard gap g」列為不得更改的項目 | transcript（主 session） |
| 09-05 11:02 | 研究者核准單案求解診斷；若 Class-C 出現 `NUMERICAL_BOUNDARY_UNRESOLVED` 則 STOP | transcript 附件 `7da49e97…`（SHA `5466cf7c…6ca6`） |
| 09-07 | guard 首次進入 Git：commit `6916fa5`（core r9） | 正式（Git） |
| 09-09 | Decision Bridge 記錄 τ／g 與分類規則，但沒有寫明它在求解前就是可行域排除 | 正式：`docs/checkpoints/transition_settlement_decision_bridge_v7_2_2026-09-09.md`（SHA `7bb5c6c1…2394`，commit `2b353c4`） |
| 09-21 | commit `b0cd2ac`（accepted r10 implementation state），guard 未變 | 正式（Git） |
| 10-23 | R2 Independent Static Audit 給出 CONDITIONAL PASS。R2-N01：已以真實資料構造出落在條帶內的物理可行點；R2-N02：Big-M 措辭問題 | transcript：Codex `rollout-2026-10-23T12-25-31-01a16701…jsonl`（SHA `8934245f…1fcf`）。**沒有獨立持久化的報告檔案** |

**已回收的決策邊界（Historical Decision Recovery Verdict B）：** guard 曾被討論、實作、測試（包括 static policy test 與 3 個 fixture 的 integration test），並被凍結為不得更改的實作慣例。但**找不到任何明確接受「guard-restricted optimum」或接受其最適性影響的紀錄**。本文件不補造這樣的 acceptance。

---

## 4. 精確的 guard-restricted domain

### 4.1 六個必須分開的層次

| 層次 | 定義 | 來源 |
|---|---|---|
| L1 Physical dispatch feasibility | R2 §5–§6 的 normal／outage 物理方程、§8.2 與 §9 的 finite bounds、ε 與 cost-sublevel 限制。記為集合 \(X\) | R2 |
| L2 Intended source rule（strict project rule） | 每一筆正值的非重複超約增量，以包含 billing-period TOU canonical maximum event 的季別費率計價。d=0 視為 tie，取 earliest timestamp，也就是 earlier season。**此為研究案例 project rule，不是台電已公布的完整跨季公式**（14b：`OFFICIAL_CROSS_SEASON_AGGREGATION_NOT_EXPLICITLY_LOCATED`） | Bridge 2026-09-09；14b interface |
| L3 τ-convention | \(\lvert d\rvert\le\tau\) 視為 numerical tie。等價於：\(d\le\tau\) 取 earlier，\(d>\tau\) 取 later | core L123–147、L184；Bridge |
| L4 Guard-restricted MILP domain | 見 §4.2。開區間 \((\tau,\tau+g)\) 在求解前即被排除 | core L1707–1730 |
| L5 Post-solve settlement／certificate | 從 hourly dispatch 重算 exact seasonal maxima，再用 live classifier 分類。Class-C 若為 UNRESOLVED，certificate 失敗 | core L163–190、L2302–2347、L2372 |
| L6 Solver numerical tolerance | 約束只在 FeasibilityTol（accepted 值 1e-6）與 IntFeasTol（1e-5）內成立 | Gurobi settings；core L1238 |

### 4.2 公式（逐字對應 live core `src/annual_design_model_v7_2.py`，SHA `9d828321…93da8`，CORE_VERSION r10）

對每個 Class-C component（兩季、費率不同；在現行 calendar 中為 2025-05 與 2025-10 的 `sat_half` 與 `off`），定義：

\[
d=D_{later}-D_{earlier}=\kappa\,(G_l-G_e),\qquad G_s=\max_{t\in I_{m,q,s}}p^{grid}_t\ (\text{native exact MAX}),
\]

\[
d\in[-U_e,\;U_l],\qquad U_s=\kappa\max_{t\in I_{m,q,s}}\bar p^{grid}_t ,
\]

\[
\tau=\max\{10^{-4}\text{ kW},\;100f,\;100\,\epsilon_{machine}\max(1,L_{max})\}\quad(\text{L110–147}),\qquad
g=10f\quad(\text{L118, L150–160}),
\]

其中 \(f\) 為**模型建構時實際讀取的 Gurobi FeasibilityTol**（L1238：`feasibility_tol = float(model.Params.FeasibilityTol)`）。因此 τ 與 g 會隨 f 改變。當 f > 1e-6 時，τ = 100f。在 accepted 設定 f = 1e-6、L_max = 5179 下，τ = 1e-4 kW，g = 1e-5 kW（浮點實現值為 9.999999999999999e-06）。

Source binary \(b\in\{0,1\}\)（L1712–1730）：

\[
d\le\tau+(U_l-\tau)\,b,\qquad d\ge -U_e(1-b)+(\tau+g)\,b .
\]

由此得：\(b=0\Rightarrow -U_e\le d\le\tau\)（earlier 或 tie）；\(b=1\Rightarrow \tau+g\le d\le U_l\)（later 明確較大）。若 \(U_l<\tau+g\)，模型拒絕建構（L1707）。

**Guard-restricted domain：**

\[
X_g=\{x\in X:\ d_c(x)\notin(\tau,\tau+g)\ \ \forall c\in\mathcal C\}.
\]

**這是求解前的可行域限制，不只是求解後的警告。** 不論該 component 的超約量 W 是否為 0，凡是 \(d_c(x)\in(\tau,\tau+g)\) 的物理排程 \(x\) 都不在 MILP 可行域內。core L1069 只對 finite-bound 所用的 idle reference 做了「不得落在條帶內」的檢查，並未保護其他排程。

### 4.3 Post-solve classifier（L163–190）

- \(\lvert d\rvert\le\tau\)：NUMERICAL_TIE_EARLIEST_MAX_TIMESTAMP
- \(d<-\tau\)：EARLIER_SEASON_CLEARLY_LARGER
- \(d<\tau+g\)：NUMERICAL_BOUNDARY_UNRESOLVED
- 其餘：LATER_SEASON_CLEARLY_LARGER

Class-C 的 UNRESOLVED 會計入 certificate failure（L193–215）。Binary 以 0.5 四捨五入（L2341）。McCormick 乘積以容差 1e-5 對照「四捨五入後的 b × exact W」檢查（L2372）。

### 4.4 Tolerance dependency（L6）

由於有 FeasibilityTol，solver 可能回報約束違反量 ≤ f 的解。例如 \(b=0\) 而 \(d=\tau+10^{-7}\)，或 \(b=1\) 而 \(d=\tau+g-10^{-7}\)。另外 post-solve 重算 maxima 時，可能出現約 1e-13 kW 的浮點偏移。這類結果的 d 落在 \((\tau,\tau+g)\) 內，會被 L5 標成 UNRESOLVED，不會被靜默計價（EXP1、EXP3）。

---

## 5. Strict boundary 的數學限制

**命題 T1（PROVEN；適用範圍：有界、只含非嚴格線性約束與整數限制的 MILP）。**

設計價標籤 \(\lambda\in\{\text{earlier},\text{later}\}\) 由 MILP 變數決定。有界 MILP 的可行集是有限個多胞形的聯集（Jeroslow–Lowe），因此是緊緻閉集；它在 \((d,\lambda)\) 上的投影也是閉集。

而 τ-convention 的 canonical 圖形
\[
\Gamma=\{(d,\text{earlier}):d\le\tau\}\cup\{(d,\text{later}):d>\tau\}
\]
不是閉集：\((\tau,\text{later})\in\overline\Gamma\setminus\Gamma\)。strict rule 以 0 取代 τ，結論相同。由此得到三選一：

1. 若可行標籤集 \(F\subseteq\Gamma\)（從不錯標），則 later 部分是 \((\tau,U_l]\) 的閉子集，最小值必定 > τ，**必然排除某個 \((\tau,\tau+\delta)\)，δ > 0**。這就是現行 guard（δ = g）。
2. 若 \(F\supseteq\Gamma\)（不排除任何物理點），則 \(F\supseteq\overline\Gamma\ni(\tau,\text{later})\)，**至少在 d = τ 允許非 canonical 標籤**。這就是 overlap 方案 B 與 closed 方案 C、C0。
3. 對非 canonical 區域改用保守費率計價（方案 E）。

**本命題的界線：** 本命題只針對上述類型的有界 closed MILP 表示。它**不主張**其他技術一定無法處理此問題，例如：
- 把需量差離散到電表解析度格點後重新定義語義；
- 精確有理數或區間驗證的事後修正；
- hierarchical／lexicographic tie-break 的特殊設計；
- 其他語義重定義。

這些方法都會改變語義或建模範圍，本研究**尚未評估**。另外，「沒有可行域缺口」**不等於**「精確」：B、C 沒有缺口，但會錯標。

**命題 T4（PROVEN，由構造得到）。** 在 strict 或 τ 規則下，若邊界另一側的費率較便宜，canonical 成本函數在邊界上不是下半連續，因此下確界可能無法達到（EXP3 S11 型構造）。所以「unguarded optimum」可能不存在，只能談下確界 \(\inf\)。

---

## 6. 隔離實驗證據

來源：`C:\Users\IRISC~1\AppData\Local\Temp\iris_classc_guard_experiment_20261023\run_20261023T060151Z\`
- `REPORT.md`：SHA `db021bf52689c504b3ee5cd05fffe9de74ef48e7f734a1cfbffd11c4e21b8439`，18,427 bytes。
- `MANIFEST.json`：SHA `303005d9aa2a8d19c4551919805cdb0fcc284a701e9f207e72310e6479a634cc`，30,521 bytes；本輪重新雜湊 174/174 個檔案，全部一致。

實驗共 1,316 次 `optimize()`，沿用既有結果，本輪未重跑。實驗與報告都是同一作者所為，**未經獨立審查**。

### 6.1 方案定義

令 \(X\) 為除 Class-C 標籤約束以外完全相同的可行域。\(f_\tau(x)\) 為 canonical τ-convention 年成本，包含 energy、basic、以 canonical 費率計價的 overcontract、degradation 與 capex。

| 方案 | 標籤約束（每個 Class-C component） | 目標值 | 與 \(f_\tau\) 的關係 |
|---|---|---|---|
| A（live guard）／D（A + 本文件宣稱） | b=0: d ≤ τ；b=1: d ≥ τ+g | \(A^*=\min_{x\in X_g}f_\tau(x)\) | 可行點的標籤必為 canonical，所以成本 = \(f_\tau\) |
| B overlap（09-04 提案） | b=0: d ≤ τ+g；b=1: d ≥ τ | \(\min_x f_B(x)\) | \(f_B\le f_\tau\)：在 [τ, τ+g] 內取較便宜費率 |
| C closed τ | b=0: d ≤ τ；b=1: d ≥ τ | \(\min_x f_C(x)\) | \(f_C\le f_\tau\)：只在 d = τ 取較便宜費率 |
| C0 closed strict | b=0: d ≤ 0；b=1: d ≥ 0 | \(\min_x f_{C0}(x)\) | \(\le\) strict canonical 成本 |
| E conservative strip（實驗新增） | 三態：s0: d ≤ τ；s1: d ≥ τ+g；ss: τ ≤ d ≤ τ+g，以 max(r_e, r_l) 計價 | \(\min_x f_E(x)\) | \(f_E\ge f_\tau\)；在 \(X_g\) 上 \(f_E=f_\tau\) |

### 6.2 證據表

| 證據 | 內容 | 角色 | 強度 |
|---|---|---|---|
| EXP0 | Accepted Full81 G1（81 cases）、v7.3 EOB、corrected EOB，共 332 筆 Class-C 列：W > 0 為 **0**；d 與條帶最近 372.8 kW；consistency 全部 PASS | 既有結果診斷 | EMPIRICALLY OBSERVED（只描述**實際解**） |
| EXP1 / 1-E | 14 個 d 點 × 方案 × 2 種費率方向 × 容差變體，共 1,036 次 | 邊界分類 | EMPIRICALLY OBSERVED：在 f = 1e-6 下，各方案都會在閾值 ±1e-6 內接受精確上不可行的分支；**只有 A 的錯標全部被 live classifier 標出** |
| EXP3 | 6 小時 toy，完整 billing 鏈，13 個 scenario，234 次 | 對抗性計費反例 | EMPIRICALLY OBSERVED（toy）：B、C、C0 在邊界上會低估 3,227–3,846 NTD；A 在剛性條帶點上不可行（包含 W = 0 的情形）；A 在無法往上逃離時有 3,227 NTD 的最適性損失（S7）；E 只會高估 |
| EXP4 | 以 S13／S10／S11 重建 R2-N01 的反例 | 真實資料可行性反例 | EMPIRICALLY OBSERVED：年成本 68,411,665.65019892（與 R2 差 −7e-8）；d − τ = +5.0e-6；W = 0；A 排除、C 與 C0 只允許 later、B 兩者皆允許 |
| EXP4b | Reference dispatch 上各 Class-C 最大時刻的 PV | H-PV 前提的唯讀檢查 | EMPIRICALLY OBSERVED：8/8 個最大時刻有 PV 在用（25–257 kW），**但只限 reference dispatch** |
| EXP5b | 真實資料單月 fixture（744 h，May/Oct × α ∈ {0.10, 0.50}，β = 4），16 次 | 縮減模型比較 | EMPIRICALLY OBSERVED：同一 fixture 內 A、C、E、C0 的目標值相同（差 < 1e-6 NTD，gap ≤ 3e-16）。這些是**月度簡化模型**（月內 cyclic、固定 BESS、無 outage／ENS） |
| EXP6 | IntFeasTol × big-M；f = 1e-9 | 容差穩健性 | EMPIRICALLY OBSERVED：未觀察到整數容差被利用（解析上的暴露範圍 1.69 kW，可被 post-solve 偵測）；f = 1e-9 時 Gurobi 對可行模型給出決定性的錯誤 INFEASIBLE，**調緊容差不是安全的修正** |
| Type-3 | 全年 EOB+／Global EOB／RES／ε-frontier 上 A 與其 relaxation 的比較 | — | **NOT VERIFIED** |

**解讀限制（必須保留）：**

- 332 筆 accepted 列沒有 W > 0，只描述已求得的 guard-restricted 解。它**不證明**未被探索的排程沒有跨季成本影響。
- 16 個 fixture 的目標值相同，**不證明**全年 EOB、RES、ε-frontier 等價。
- 真實資料反例只證明 feasibility exclusion，**不證明** full-model optimum 已改變。
- Toy 的 3,227–3,846 NTD 是人為構造的 toy 數值，**不是** NTUST 的全年成本損失。
- Solver 回報 OPTIMAL，只代表在該 formulation、該可行域與容差下的最適。

---

## 7. Guarded 與 unguarded 的最適性宣稱

### 7.1 符號

- \(C^*_{guard}\equiv A^*\)：A 在 \(X_g\) 上的最小值。若 \(X_g=\varnothing\)，記為 \(+\infty\)。
- \(\inf_\tau\equiv\inf_{x\in X}f_\tau(x)\)：τ-convention 的 unguarded 下確界，可能無法達到（T4）。
- \(\inf_{strict}\)：strict rule 的對應下確界。
- 「\(C^*_{unguarded}\)」必須先指明是 \(\inf_\tau\) 或 \(\inf_{strict}\)，並以下確界理解，不得默認存在 minimizer。

### 7.2 夾擠關係（命題 T2，PROVEN，精確算術）

**條件：**
- (i) 各方案除 Class-C 標籤約束外，可行域 \(X\) 完全相同（相同 bounds、ε、cost cap、floors、physical constraints）；
- (ii) 各方案的成本函數除 Class-C overcontract 計價外完全相同；
- (iii) 比較的是單一 cost-minimization（例如 ε-constraint stage 1 在固定 ε 下 \(\min C\)）；
- (iv) \(X\) 有界閉，因此各 MILP 若可行，最小值可以達到。

**結論：**

\[
B^*\le C^*\le \inf_\tau\le E^*\le A^*=C^*_{guard},\qquad C0^*\le\inf_{strict}.
\]

**證明要點：**
- \(f_B\le f_C\le f_\tau\)，且 B、C 允許所有 canonical 的 (x, λ) 組合，故 \(B^*\le C^*\le\inf_\tau\)。
- \(f_E\ge f_\tau\)，故 \(\inf_\tau\le E^*\)。
- A 的每個可行點都可以用相同成本在 E 中實現，故 \(E^*\le A^*\)。
- 注意左側是最小值，中間是下確界。

**不適用於：** lexicographic stage 2（ENS secondary 的 \(r\) 值）、Global EOB 的跨分支 lexmin、cost band 內的 ENS 比較。這些情形沒有推導出夾擠關係。

**實務 certificate（未執行，僅供未來選用）：** 若對 C-relaxation 求得 proven lower bound \(L_C\)，對 A 求得獨立重算的可行成本 \(U_A\)，則在 solver 正確性與容差範圍內：
\[
\inf_\tau\in[L_C,\ U_A],\qquad U_A-\inf_\tau\le U_A-L_C .
\]

### 7.3 條件界線（命題 T5：在假設 H 下的推論已證明，但假設 H 本身 NOT VERIFIED）

**假設 H-PV：** 對 τ-problem 的某個 minimizing sequence 中每一個點 \(x\)，以及每一個 \(d_c(x)\in(\tau,\tau+g)\) 的 component \(c\)，都存在一個 later-season 最大 import 時刻 \(t^*\)，滿足 \(v^{use}_{t^*}\ge g/\kappa\)（可以 curtail）。若在 R2 stage 2 使用，還需要 cost cap 至少有 0.0054 NTD 的 slack。

**推論：** 在 \(t^*\) curtail \(\Delta<g/\kappa\)，會使 \(d\) 升到 \(\tau+g\)，標籤仍為 later（canonical）。變化如下：

- 只有該 component 的 \(D\) 增加，而且增加量 < g。
- 在 running maximum 下，後續時段的 \(\Delta z\) 不會增加。
- W 對 Δ 為非遞減且 3-Lipschitz。
- SOC、segments、ENS／outage recourse（使用 \(V_t\)，而非 normal 的 \(v^{use}\)）、CC 與 floors 都不變。

因此：

\[
0\le A^*-\inf_\tau\le\sum_{c\in\mathcal C}\big(3\,r_{l,c}+\rho_{t^*}/\kappa\big)\,g\ \le\ 4\,(3\times43.032+5.676/\kappa)\times10^{-5}\approx0.0054\ \text{NTD-2023/year}.
\]

若 H 不成立，此界不適用。EXP3 S7 顯示，無法往上逃離時，toy 中的差距可以達到 \((r_e-r_l)W\)。H-PV 只在 reference dispatch 上觀察成立（EXP4b），**在優化後的全年解上 NOT VERIFIED**。strict rule 與 τ-convention 之間可以用同樣方式推得約 0.054 NTD/年的條件界線（τ 取代 g），但需要兩側都能逃離，本文件只列為 CONDITIONAL，沒有另作驗證。

### 7.4 Phase-1 宣稱規則（建議 successor 採用）

1. EOB+、Global EOB、RES（stage 2 \(\min C\mid r=0\)）、ε-constraint frontier、lexicographic approximate endpoints，以及 R2 §11 的 cost approximation certificate，其最適性結論**一律限於實際建構、包含 Class-C guard 的候選可行域**，也就是 \(F_+(\epsilon)\cap X_g\)。
2. R2 §11 的 \(C(x_2)-C^*\le(U_C-L_C)+\delta_C+\tau_C\approx2.001\) NTD-2023/year 中的 \(C^*\)，是 guard-restricted 的 \(C^*_{guard}\)。**此界不是 unrestricted physical domain 的誤差證書。**
3. 除非另有有效數學證明，或經授權完成 Type-3 certification，否則不得宣稱 \(C^*_{guard}=C^*_{unguarded}\)，也不得宣稱 \(C^*_{guard}-C^*_{unguarded}=0\)。T5 只能以「在假設 H 下 ≤ 約 0.0054 NTD/年」的條件形式引用。
4. τ 與 g 是研究案例的數值實作慣例，**不是台電官方規範**。τ band 本身在 \(0<d\le\tau\) 時偏離 strict rule，論文中應予揭露。

> **Guard-restricted mathematical optimality ≠ unrestricted physical-domain optimality.**

---

## 8. 既有 v7.3 accepted results 的宣稱邊界

**事實（本輪唯讀核對）：** 以下結果都是以包含此 guard 的 accepted core r10 求得：
- Accepted Main Layer A Full81 run `results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828`：81 個 `result.json` 都記錄 core r10、`gurobi_feasibility_tol` = 1e-6、τ = 1e-4、g = 9.999999999999999e-06、`numerical_boundary_unresolved_count` = 0；
- v7.3 EOB `results/eob_production_v7_3/runs/20260924T184038809594Z_59116b1556`；
- corrected EOB `results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308`。

**宣稱邊界：** 這些 accepted solver results 的最適性宣稱，應理解為其原始 formulation 可行域上的最適，即 guard-restricted。

本文件明確**不**做以下任何事：
- 撤銷任何歷史 acceptance；
- 覆寫原始結果，或修改歷史 manifest、checkpoint、provenance record；
- 宣稱 guard 必然影響或必然不影響歷史最適成本（EXP0 只顯示實際解的 W = 0，且 d 距條帶 ≥ 372.8 kW）；
- 把未來的 Phase-1 Methodology Acceptance 自動套用到舊研究。

若日後需要修訂既有 acceptance wording，必須另行授權治理程序。

---

## 9. R2-N02 Big-M wording correction（只記錄文字，不改寫 R2）

**R2 §9.4 現行文字：**

> 可選的同域有效tightening為 M_ch≤min(Pbar,.80Ebar/(.90Δt))、M_dis,t≤min(Pbar,L_t,.90×.80Ebar/Δt)；這是數學界，不是新增物理duration限制。

**問題：** 寫成「≤」時，若孤立閱讀，任何更小的常數（甚至 \(M_{ch}=0\)）都看似符合，可能截掉合法的充電設計。

**建議 successor 使用的精確替換文字：**

> **主 contract（已證明有效）：** \(M_{ch}:=\bar P\)；\(M_{dis,t}:=\min(\bar P,L_t)\)，或共同的 \(M_{dis}:=\min(\bar P,L_{max})=5179\) kW。
>
> **可選 tightening（同一 cell、同一 domain）：** 實作可改取
> \[
> M_{ch}:=\min\!\Big(\bar P,\ \frac{0.80\,\bar E}{0.90\,\Delta t}\Big),\qquad
> M_{dis,t}:=\min\!\Big(\bar P,\ L_t,\ \frac{0.90\times0.80\,\bar E}{\Delta t}\Big).
> \]
> 右側每一項都已獨立證明為該 cell 保留可行域內 \(p^{ch}_t\)（\(u_t=1\) 時）或 \(p^{dis}_t\)（\(u_t=0\) 時）的有效上界，因此取其最小值仍是有效上界。**任何小於這個最小值的常數，都不是合法的 tightening**；若要使用，必須另行證明它對所有保留的 cost-optimal 與 ε-feasible 點都有效。這些是數學界，不是新增的物理 duration 限制。
>
> 若採用 tightened \(M_{ch}\)，§8.2 中由 \(M_{ch}\) 推得的 \(\bar p^{grid}_t=L_t+M_{ch}\)、\(G\) 與 \(D\) 的上界、Class-C 的 \(U_e,U_l\)、\(\bar z_q\)、\(\bar W\)，都必須以同一個 \(M_{ch}\) 重算，並重新檢查 \(U_l\ge\tau+g\)。

**本輪重新核對的代數依據：**
- \(p^{ch}\le P_B\le\bar P\)。
- \(u_t=1\Rightarrow p^{dis}_t=0\)，因此 \(0.90\,p^{ch}_t\Delta t=e_{t+1}-e_t\le0.90E_B-0.10E_B=0.80E_B\le0.80\bar E\)。
- \(u_t=0\Rightarrow p^{ch}_t=0\)，因此 \(p^{dis}_t\Delta t/0.90=e_t-e_{t+1}\le0.80\bar E\)；又因 \(p^{grid}_t,v^{use}_t\ge0\)，由 balance 得 \(p^{dis}_t\le L_t\)。
- Xu segments 的總和等於 aggregate SOC，所以同一組界對 segment formulation 也成立。

---

## 10. 可選的未來工作（皆未授權）

1. **OPTIONAL FUTURE CLASSIFIER-VALIDATION IMPROVEMENT。** EXP3 S6、S8b、S12 中，A 的最優解停在 \(d=\tau+g-1.6\times10^{-13}\)，計費算術正確，但 live classifier 回報 UNRESOLVED（false-fail）。本輪**不放寬** classifier。未來若授權修正，必須同時驗證：binary source selection、constraint residual（原單位）、exact seasonal maxima、實際 tariff reconciliation、numerical tolerance，並且同時評估 false-pass 與 false-fail。不得只為提高 PASS rate 而調整檢查器。
2. **Type-3 certification（future optional strengthening）。** 對選定的全年 headline cases，求解 C-relaxation 以取得 \(L_C\)，再依 §7.2 判斷 \(U_A-L_C\)。這需要另行授權全年求解。它**不是**本文件完成的必要前置條件。
3. **H 的唯讀檢查。** 在既有或未來的最優 dispatch 上，檢查 Class-C later-season 最大時刻的 \(v^{use}\)。這只需唯讀。
4. **方案 E（conservative strip）只列為備選。** 它是唯一「無可行域缺口、且精確算術下不低估」的方案，但需要修改 accepted core 並全部重跑，而且無法改善 S7 型的最適性損失。B 與 C **不得**作為計價 formulation，C 只能作為 relaxation 或 lower-bound 工具。

---

## 11. 尚待使用者決定的事項

1. 是否選擇 guard-restricted Phase-1 scope，並以 §7.4 作為宣稱規則。若選擇，在完成必要文件治理後，Class-C 不再是核心數學 Coding blocker。
2. 是否在 R2 successor 採用 §9 的 R2-N02 替換文字。
3. 是否授權 §10 的 Type-3 certification，或 classifier 改善，或兩者都不做。
4. 論文中如何揭露 τ band 與 strict rule 的差異，以及 L2 project rule 不是台電官方公式。
5. 指定新的、獨立的 Targeted Static Audit Session。建議由非本作者 agent 執行。

**以下事項尚未自動取得授權：** formal Phase-1 implementation、PV0 correctness Pilot、Type-3 annual certification、任何 accepted core 修改、post-solve classifier 修改、acceptance 或 production re-freeze。

---

## 12. 作者端一致性檢查（不是審查 verdict）

| 檢查項目 | 結果 |
|---|---|
| 保留 guard | 是。§4、§7.4、§10.4 |
| 未錯誤宣稱 unguarded optimality | 是。§7.4-3；T5 只以條件形式出現 |
| 區分 strict tariff 與 τ-convention | 是。§4.1 L2／L3、§7.4-4 |
| 區分數學證明與 toy／fixture 觀察 | 是。§5、§6.2、§7 皆標明強度 |
| 保留 B1–B4 已收斂的方法 | 是。§2；未改任何方程或證明 |
| 未修改 10 kW／20 kWh floors | 是 |
| 未改寫 v7.3 acceptance | 是。§8 |
| 未把 Type-3 當成已驗證 | 是。§6.2、§7.3、§10.2 |
| Big-M wording 修正正確記錄 | 是。§9，含代數依據 |
| 未改程式、未用 solver、未改正式 artifact | 是。§13 |

**Material contradiction：** 未發現。若 Targeted Audit 發現 material defect，應標記 HOLD，以 additive successor 處理，不覆寫本文件。

---

## 13. Additive status、STOP 與 provenance

### 13.1 Source identities（本輪 SHA-256 唯讀核對）

| ID | 路徑 | SHA-256 |
|---|---|---|
| R2 | `C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md` | `1a7cf0bd926f821cc9dddbec0145854dbba212a825d32f948bb2f00e5347f557` |
| Core | `C:/Users/Iris C/OneDrive/Desktop/iris_thesis/src/annual_design_model_v7_2.py`（r10；HEAD `5a53f5f`） | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Bridge | `…/docs/checkpoints/transition_settlement_decision_bridge_v7_2_2026-09-09.md` | `7bb5c6c134e6c790088999ba80464dc37087ddcebcac0408399413176c952394` |
| Protocol | `…/docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md` | `c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696` |
| Constitution | `C:/Users/Iris C/Downloads/Iris_Thesis_Response_Mode_and_Research_Governance_Constitution_2026-10-03.md` | `4f5eaf050d96f84d96e06ebebd53e095f209ad50bb0a0f94a180f2dd0efc9c38` |
| S13 | `…/data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet` | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| S10 / S11 / S12 | tariff optimization / seasonal settlement matrix / transition interface | `5c1582d8…4395` / `ed7f8dbf…4b79` / `f101af47…5b88` |
| Experiment REPORT | `C:/Users/IRISC~1/AppData/Local/Temp/iris_classc_guard_experiment_20261023/run_20261023T060151Z/REPORT.md` | `db021bf52689c504b3ee5cd05fffe9de74ef48e7f734a1cfbffd11c4e21b8439` |
| Experiment MANIFEST | 同目錄 `MANIFEST.json`（174 個檔案，全部重新驗證） | `303005d9aa2a8d19c4551919805cdb0fcc284a701e9f207e72310e6479a634cc` |
| 主要實驗 artifacts | exp0 `bf075fc5…`、exp1 grid `0afdfd98…`、exp1e grid `0b251b43…`、exp3 `aef858a2…`、exp4 `d5c5f4f3…`、exp5 `485a3400…`、exp6 `e659a430…` | 見 MANIFEST |
| Codex transcripts（conversation-only） | `~/.codex/sessions/2026/08/26/…01a03e33….jsonl`；`…/2026/09/04/…01a06cbe….jsonl`；`…/2026/10/23/…01a16701….jsonl`；附件 `77d9c823…`、`7da49e97…` | `70568f42…`；`fa07aa9b…`；`8934245f…`；`74a01689…`；`5466cf7c…` |

**缺少或未驗證的證據：**
- 2026-10-23 R2 Independent Static Audit 沒有獨立持久化的報告檔案，只存在於 transcript。
- 本機沒有任何 ChatGPT 對話匯出可供查核。
- Type-3 證據不存在。
- H 在優化後全年解上的狀態不明。
- 隔離實驗未經獨立審查。

### 13.2 Integrity

- 本輪唯一新增的檔案就是本文件。
- Existing files modified = 0；Repository modified = 0；Git mutations = 0；Model builds = 0；Solver calls = 0；Production reruns = 0；Self-acceptance = 0。
- 本輪只做了來源讀取與 SHA-256 核對（包括重新雜湊 MANIFEST 列出的 174 個檔案）。
- 本檔不嵌入自身的 SHA，以避免循環；交付回覆中另行提供最終 bytes 與 SHA-256。

**ADDITIVE CLARIFICATION R1 — DRAFT / NOT ACCEPTED / PENDING TARGETED INDEPENDENT AUDIT**

**完成本文件即停止。下一步只有：使用者檢視，再安排新的、獨立的 Targeted Static Audit Session。NO CODING / NO SOLVER / NO GIT MUTATION / NO SELF-ACCEPTANCE / NO R2 MODIFICATION / NO R3。**
