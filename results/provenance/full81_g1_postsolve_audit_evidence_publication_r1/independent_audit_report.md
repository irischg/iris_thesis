## A. Verdict

**FULL81 POST-SOLVE INDEPENDENT ACCEPTANCE — PASS**

本次獨立稽核支持這組 Full81 結果進入後續接受程序。**本報告沒有建立正式 acceptance artifact、變更 current pointer，或將結果提升為 thesis-authoritative result set。**

## B. 白話說明

81 個預定案例全部存在，保存的 solver 結果全部符合既定接受條件；輸出檔案的 SHA-256、位元組數及登錄關係均一致。另以 canonical input 與保存的 dispatch，獨立重算物理限制、所有有效停電起點、電費、跨季結算、成本、退化與 rainflow，結果均落在接受容差內。

G1 lifecycle、scope authorization、no-solve preflight 與獨立 execution authorization 的檔案身分、Git containment 及先後順序亦成立。

仍須保留幾項非阻擋限制：沒有保存逐次 solver invocation telemetry、Gurobi version、best bound 或完整 solver log；不能宣稱完整重建歷史執行環境。這些不是現行 publisher 規定的必要輸出，且不妨礙本次重建必要的數值接受條件。

## C. 五層評估

| 層次 | 結論 | 證據強度及界線 |
|---|---|---|
| Methodology | PASS | **CONFIRMED**：依 accepted Framework v7.4；未重開 CLOSED decisions |
| Evidence | PASS | **CONFIRMED**：canonical input、結果檔案、必要數值檢查均可重建 |
| Implementation | PASS，保留非阻擋事項 | **CONFIRMED**：21 個 implementation paths 的實際 bytes 與 G1 digest 一致 |
| Numerical Execution | PASS | **CONFIRMED**：81 個保存結果符合 solver contract；歷史實際呼叫次數屬 **SUPPORTED** |
| Governance / Provenance | PASS | **CONFIRMED**：必要 authority chain、publication containment、Git 順序成立；完整操作歷史仍有界線 |

本次是既有結果的唯讀接受稽核，沒有 methodology change 或 implementation correction。

## D. 身分表

以下路徑以 repository root 為基準：

`C:\Users\Iris C\OneDrive\Desktop\iris_thesis`

**R** 代表實際確認存在、不是 symlink 的目標目錄：

`results/layer_a/final_81_v7_3/runs/20261008T183934456307Z_a6826f4828`

未使用誤植的 `20261008T1839344456307Z_a6826f4828`。

| 項目 | 預期與實測 |
|---|---|
| Branch | `thesis-v7`，一致 |
| Execution HEAD／目前 HEAD／local origin ref | 均為 `c8f555094d6ab711ce6426302419fff958ed19fa` |
| 實際 GitHub branch | 經 connector 獨立確認為相同 commit。[遠端分支](https://github.com/irischg/iris_thesis/tree/thesis-v7) |
| Framework | `docs/research_framework_v7_4_2026-09-26_r2.md`；CURRENT_METHODOLOGY_AUTHORITY |
| Registry | `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md`；CURRENT_EVIDENCE_AUTHORITY |
| Generation／lineage | `CURRENT_FULL81_PRODUCTION_GENERATION_G1` |
| Candidate | `CURRENT_FULL81_PRODUCTION_GENERATION_G1_CANDIDATE_R1` |
| Accepted lifecycle | `results/provenance/current_full81_production_generation_g1_accepted_lifecycle/accepted_lifecycle_record.json`；五個必要 roles 齊全 |
| Scope authorization | `results/provenance/main_full81_authorization_g1/main_full81_authorization.json` |
| No-solve preflight | `results/provenance/main_full81_no_solve_preflight_g1/main_full81_21d_no_solve_preflight_evidence.json` |
| Execution authorization | `results/provenance/main_full81_execution_authorization_g1/main_full81_execution_authorization.json`；`GRANTED` |
| Canonical input | `data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet`；8,760 rows、51 columns |
| Core | `src/annual_design_model_v7_2.py`；版本符合指定的 `…2026-09-16-r10` |
| Stack | `src/production_successor_stack_v7_3.py`；accepted inherited implementation lineage |
| Runner | `scripts/21d_preflight_v7_3_final81_successor.py`；`v7.4-main-full81-no-solve-preflight-runner-2026-10-03-candidate-r3` |
| Root manifest | `R/completion_manifest.json`；`COMPLETE_PASS_PENDING_INDEPENDENT_ACCEPTANCE` |

下列 SHA-256 均由實際 bytes 重算，與適用 authority binding 一致：

| Artifact／identity | SHA-256 |
|---|---|
| Framework | `36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273` |
| Registry | `5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433` |
| G1 accepted lifecycle | `f1d798ab357ff82454f3030587b3cda30e13b55bf890a2b7257bbb40c325d3b0` |
| Scope authorization | `0dc75214904682476def42f36e73688a1f1d254523f20bfd319e6561c4a81338` |
| No-solve preflight | `95047e2fa9c0d524d5c43c0fdcafe40a93662c4282fd1aaaf0558be681f4da76` |
| Execution authorization | `87ec6643deef262bc3710b2e1d7e76d582bcfd1eebd41ffdc6c6c71eb2f12c6e` |
| Canonical input | `3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428` |
| Core | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Stack | `65728c40e8df746da92865e859072c345370ae93aa4a2b32a24b149c67a3dcda` |
| Runner | `1a55c34897548a3595a9812dfeaa854f3b6b478594630c750931cd7cf2371bd1` |
| Parameter registry | `c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1` |
| Solver fingerprint | `598dc4365ce65055aa509f6c98a87ba91b173ff361e06119000bf165af4fdebe` |
| Runtime identity，21 paths | `8cca5e81d62ab3976aaeeeea162bdfdca7867af4871156446bbcae4ece65eabc` |
| Validation identity，9 paths | `1bd49904e8d774c27b5e8a0390240eb836e92fa6cf857948f7b9d3486914111b` |
| Governance identity，26 paths | `360c81b133440e1b0444e01f2fd120eb1f49d0db3501283773a2952c032dbeb4` |
| `R/authority.json` | `ecef360b340de92b2f1f612b7028efebfa1b26986fa9fe22efad66a46b3442bb` |
| `R/case_schedule.json` | `08b05f654dbf997fb91ed4d835594d3f796567e47882e478b9fa05e5ba240df4` |
| `R/completion_manifest.json` | `d5c647846e4ec4ddfedd50ff2fed837f70e5398dedd95d0fea90dfc5fcad7d24` |

四個 execution inputs 亦全部吻合：

| `data/reference/` 下的檔案 | SHA-256 |
|---|---|
| `production_economic_interface_v7_2.json` | `9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9` |
| `taipower_seasonal_settlement_matrix_v7_2.csv` | `ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79` |
| `taipower_tariff_optimization_ntd2023_v7_2.csv` | `5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395` |
| `taipower_transition_period_settlement_interface_v7_2.json` | `f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88` |

## E. Full81 完整性

由 Framework §3.4、planning code、schedule、case definitions 與 manifests 分別交叉核對：

- α：`0.60, 0.65, …, 1.00`
- β：`4, 5, …, 12 h`

| 項目 | 預期 | 實測 |
|---|---:|---:|
| Cartesian-product cases | 81 | 81 |
| 實際 case directories | 81 | 81 |
| Case completion manifests | 81 | 81 |
| Unique case IDs／αβ combinations | 81／81 | 81／81 |
| Unique solve slots | 81 | 81，順序為 1–81 |
| Missing／duplicate／unexpected cases | 0 | 0 |
| Failed／unattempted final cases | 0 | 0 |
| 缺少必要 artifacts | 0 | 0 |
| Root reported optimization calls | 81 | 81 |
| Case-reported calls 加總 | 81 | 81 |
| 歷史實際 optimization attempts | 每 case 1 | **SUPPORTED：81**；沒有逐次 durable telemetry 可直接逐筆證明 |
| 歷史 model constructions | 81 | **SUPPORTED：81**；由 guarded call chain 推導，未保存逐模型 counter |

`OneSolveExecutionGuard`、duplicate-build guard、每 case counter 檢查及完整發布條件共同支持單次執行；沒有把 81 個目錄本身當成 81 次 solves 的證明。

## F. Solver 摘要

接受條件來自 `scripts/19b_run_final_layer_a_81_cases.py:446` 的 `solver_acceptance()`：

`has_solution`、`OPTIMAL/status_code=2`、finite objective、`0 ≤ MIPGap ≤ 10⁻⁶`。

| 指標 | 全部 81 cases |
|---|---|
| Status distribution | `OPTIMAL`：81 |
| Primal／finite objective | 81／81 |
| Solution count | 2–10 |
| MIPGap | 0–`9.916563814474196e-7` |
| 最大 gap case | `a0.90_b12` |
| Gurobi runtime | 72.301–6,143.711 s |
| 最短／最長 runtime | `a0.80_b05`／`a0.60_b10` |
| Runtime 合計 | 279,674.522 s，約 77.687 h |
| 最大 wall−Gurobi runtime | 1.113 s，`a0.70_b04` |
| Objective 範圍 | 82,841,774.990–139,264,927.383 NTD-2023/year |

81 份設定檔均為：

```text
mode=binary, MIPGap=1e-6, NumericFocus=1,
MIPFocus=0, Threads=0, OutputFlag=0, TimeLimit=null
```

`TimeLimit=null` 的 source semantics 是不設定限制，保留 infinity；沒有採用 TIME_LIMIT incumbent 作接受結果。

**NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE：**執行時 Gurobi version、直接 best-bound 值、完整 warning history。保存的設定與 accepted source 一致；本報告沒有宣稱完整 solver log 無警告。

## G. 獨立 post-solve audit matrix

八個 mandatory families 由 `src/production_successor_stack_v7_3.py:1885` 的實際 production path 推導。Producer 分別為 runner19 的 solver／physical／all-start／billing／transition／cost-degradation adapters，以及 h16→rainflow validator。

主要證據為每個 `R/cases/<case_id>/` 下的 `dispatch.csv`、`result.json`、`billing_exact.csv`、`transition_settlement_detail.csv`、`mandatory_audits.json`。

| Family | Cases／方法 | 結論 | 最大殘差、worst case | 接受容差 |
|---|---|---|---|---|
| Physical | 81；重算 AC balance、aggregate／segment dynamics、SOC、bounds、cyclicity、互斥與 binary indicators | PASS | AC：`8.8151e-7 kW`，`a0.60_b06`；state dynamics：`8.8494e-7 kWh`，`a1.00_b08` | `1e-5 kW/kWh` |
| Resilience | 81；掃描全部 **708,993 valid starts、5,671,404 outage hours** | PASS | Reserve：`1.4552e-11 kWh`，`a0.90_b12`；power violation：`4.5475e-13 kW` | Reserve identity `1e-6 kWh`；state `1e-5 kWh`；power `1e-6 kW` |
| Billing | 81；重算 **3,888 demand rows**、hourly TOU、12-month basic charges、pure-season penalties | PASS | Demand：`1.3642e-12 kW`，`a0.85_b11`；pure penalty：`2.4212e-5 NTD-2023`，`a0.60_b06` | Demand `1e-5 kW`；penalty `0.05 NTD` |
| Transition | 81；重算 **648 rows** 的 seasonal maxima、source、timestamps、tiers、rates、bounded products | PASS | Native maxima：`1.9008e-10 kW`，`a0.90_b06`；annual charge：`5.5984e-7 NTD`，`a0.80_b10` | `1e-5 kW`；`0.05 NTD` |
| Cost | 81；獨立重算所有七項成本及 objective | PASS | `2.4363e-5 NTD-2023/year`，`a0.60_b06` | `0.001 NTD` |
| Degradation | 81；segment discharge／ηd、derived λ、cost reconciliation | PASS | Throughput：`2.7791e-5 kWh`，`a0.80_b06`；cost：`4.1473e-10 NTD` | `0.001 kWh/NTD` |
| Rainflow | 81；另寫記憶體內 periodic turning-point／stack counting，使用固定五點 G curve | PASS | Energy：`3.5000e-5 kWh`；PWL−rainflow：`4.4693e-6 NTD`，均為 `a0.80_b06` | Energy `0.001 kWh`；cost `max(0.05, 10⁻⁶×cost scale)` |
| Solver acceptance | 81；依 source predicates 獨立核對 | PASS | 最大 gap `9.9166e-7` | `1e-6` |

補充確認：

- Annual reserve 使用 `0.10Eᴺ+R`；outage replay 可消耗至 `0.10Eᴺ`，沒有 reserve restoration 要求。
- 全部 valid starts 均為 non-circular，沒有 outage PV-surplus recharge。
- Canonical timeline 為 `2024-11-01 00:00` 至 `2025-10-31 23:00`，無缺漏或重複。
- Canonical 與各 dispatch 的 Load/PV 數值一致；以 round-trip CSV parsing 確認 PV residual **0 kW**。
- κ 保持 `1.0103668594376984`，沒有重新校準。
- CRF、CAPEX annualization、三個 λ 均獨立重算吻合；FOM 未再次 annualize。
- Transition guard unresolved count 為 **0**；source／timestamp／classification parity 未發現錯誤。
- Rainflow 保持 ex-post diagnostic 角色，沒有重新定義 optimization degradation。

執行了 **12 個記憶體內負向控制**，全部拒絕對應缺陷：無 primal、非 optimal、超限 gap、非有限 objective、missing／duplicate case、corrupt hash、wrong input、missing execution authorization、scope 冒充 execution、audit FAIL、缺少 registration。另有一個 solver positive control。

其中 solver controls 使用 AST 擷取、已審讀的純函式；其他為獨立 audit predicates。**沒有執行完整 production validator fixture suite，亦未宣稱執行過。**

## H. Authority state machine

以 exact-commit blobs 與 ancestry 重建如下，時間為臺北時間：

| 階段 | Publication commit | 時間 |
|---|---|---|
| G1 candidate＋independent audit | `59e530f3a7d78c0480fa1368c56331f11e5731f0` | 10/08 18:17:13 |
| Acceptance closure＋manifest | `bdbe0637a1de41cea0c2d2391149fe1a86e684e3` | 10/08 20:46:20 |
| Re-freeze＋accepted lifecycle | `b31d88c35d4d86bd4a4294bb783737d18d9e287e` | 10/08 21:27:43 |
| Scope authorization | `ab5c7bea4fdcd28e0ca967daadc80d86f25c7588` | 10/08 23:29:44 |
| No-solve preflight publication | `21ff5f48a606f88b2dcd5429ddb10799341f3aeb` | 10/09 00:10:33 |
| Execution authorization | `c8f555094d6ab711ce6426302419fff958ed19fa` | 10/09 01:12:13 |
| Run establishment | 目標 run ID／root artifacts | 10/09 02:39:34 |
| Completion manifest | `R/completion_manifest.json` | 10/12 09:01:23 |

所有必要 named-commit containment 與順序檢查成立；未發現事後補授權。

Scope record 的 `authorizes_full81_execution=false` 是正確分工：它授權 no-solve preflight。Execution 另由 `MAIN_FULL81_EXECUTION_AUTHORIZATION/GRANTED` 提供，仍要求兩個 flags：

`--execute-production`、`--confirm-native-solve`

A2、DG、sensitivities、alternate inputs、changed grids／solver settings 均不在授權範圍。

FULLSTACK-01 的 historical implementation blobs、audit、acceptance、re-freeze bindings 亦核對成立。其歷史 digest 未被當成 G1 live digest。

Execution-authorization authoring pass 本身沒有 launch；保存 artifacts 無法重建操作者身分或另外的 owner launch 對話。本次確認的是既定 machine-readable execution authority，不把發布 commit 誤當成 launch 行為證明。

## I. Artifact integrity 與 Git non-mutation

**Artifact integrity：沒有 mismatch。**

| 檢查 | 實測 |
|---|---:|
| Physical files | 651 |
| Root registrations | 650 |
| Case registrations | 567＝81×7 |
| Registry identity checks，含 root/case 重複核對 | 1,217 |
| Parsed JSON／CSV | 408／243 |
| Missing／hash／byte-count／path-escape／symlink defects | 0 |
| Duplicate JSON keys／CSV headers | 0 |

Root manifest 不登錄自身；case manifest 同樣不自我 hash。這符合 publisher 的非循環登錄方式。

Schedule 的 case objects 與 case definitions 完整一致。Billing/dispatch 沒有被 publisher 規定的同內容 JSON 副本，因此沒有以 row count 冒充不存在的 dual-format parity。

唯一周邊 staging 目錄：

`.pending_layer_a_20261008T182936610185Z_802a64df5c`

它沒有 case completion manifest，屬較早的 incomplete staging evidence；不是目標 final run 的缺案。未操作該目錄。Publisher 使用 exclusive creation、collision check 與 `os.rename(staging, final)`，支持既有 monitor 歸零的 rename 解釋；沒有發現 silent overwrite 證據。

Git 使用的唯讀命令包括：

```text
git rev-parse --show-toplevel
git rev-parse --show-prefix
git branch --show-current
git rev-parse HEAD
git rev-parse refs/remotes/origin/thesis-v7
git rev-parse --symbolic-full-name @{upstream}
git status --porcelain=v1 -z --untracked-files=all
git diff --cached --raw -z
git diff --raw -z
git diff --cached --name-status -z
git diff --name-status -z
git diff --quiet -- <path>
git cat-file blob <commit>:<path>
git merge-base --is-ancestor <before> <after>
git show -s --format=...
git log -1 --format=%H -- <path>
git ls-files --others --ignored --exclude-standard -z -- <scope>
git remote get-url origin
git ls-remote --heads origin thesis-v7
```

最後一項因本機連線失敗；之後透過 GitHub connector 成功確認實際 remote HEAD，沒有 fetch 或修改 refs。

前後 snapshot 完全一致：

- Staged diff：空。
- Unstaged content diff：空。
- Porcelain 原樣保留一筆 **` M`**：`results/provenance/main_full81_authorization_r2/main_full81_authorization.json`。其 working bytes 與 HEAD blob 完全相同，SHA-256 均為 `ef534fdf6ae10b5c37811c95dc5c900b0c022bff14f7e445eb546e940886b15f`。
- Untracked：**20 files**，前後同一 inventory；均不在 `src/、scripts/、tests/、data/、results/` protected prefixes。
- Relevant ignored inventory：1,062 entries，前後 digest 相同；目標 run 的 651 files 均為 ignored、未 Git-track。
- 539 個選定 source／authority／root-artifact hashes 的 aggregate：前後均為 `6143bce917600a35d92ae46ba1ef75f3e457c315ab5faf2bfcc832c452c02199`。
- 651 個 run-file hashes 的 aggregate：前後均為 `37a033deeec2e3683f418fe537dabf7d8592a5a0509a89bc5df67daa54830766`。

以上是明確範圍的 byte verification，沒有宣稱對整個磁碟建立完整 snapshot。

## J. Findings ledger

Severity 與 blocking disposition 分開判斷；以下均不要求重開 CLOSED methodology。

| ID | Category／Severity | Disposition／阻擋 | 證據、預期與觀察；後續方向 |
|---|---|---|---|
| AUD-N1 | Evidence／MODERATE | NONBLOCKING／否 | `SolveSettings.telemetry_callback=None`、`log_file=None`；publisher 未保存 invocation telemetry、version、bound 或完整 warnings。必要 solver contract 可驗證，完整歷史不可重建。未來若增強記錄，須另行授權 |
| AUD-N2 | Implementation／MODERATE | OPEN／NONBLOCKING／否 | `production_input_authority_v7_3.py:153–201` 宣稱 timestamp int64-ns，但目前 pandas 3.0.2 讀入 `datetime64[us]`，`.asi8` 實際以 µs hashing。Native digest 為保存的 `1aa2f364f08b54d0ba5a6c37e7855c652ce19ce6703d693d557265313c62bcb0`；強制 ns 則為 `d38fa2437abf5bb243140d50e1e992d6a2911adfb5ccfaf9978c5a348179d0b2`。影響跨環境 portability，未改變本 run chronology 或已綁定身分；不得原地修補 frozen artifacts |
| AUD-N3 | Implementation／MINOR | NONBLOCKING／否 | `production_successor_stack_v7_3.py` 的 authority payload 固定輸出 `main_full81_execution_authorized=False`；有效 execution guard 另行解析並要求獨立 authorization。此欄不能代表有效 execution 權限；未來 reporting correction 須走新 authority 流程 |
| G1-N1 | Governance／MINOR | CARRIED／NONBLOCKING／否 | 已接受的 historical origin-label ambiguity；實際 bytes/digest 正確，未默示關閉 |
| G1-N2 | Governance／MAJOR | CARRIED／NONBLOCKING／否 | predecessor freeze coverage gap 保留；G1 自身 21-path live identity 完整，未將 predecessor gap 當成 current binding |
| G1-N3 | Evidence／INFORMATIONAL | CARRIED／否 | validation evidence phase 限制照原 lifecycle 保留；本次沒有重跑或重新認證歷史 test campaign |
| R7 durability | Evidence／MAJOR | CARRIED／NONBLOCKING／否 | historical preservation/audit primary evidence 的 Git durability 限制，見 G1 acceptance closure；沒有假稱 scratchpad／ZIP 已 durable publication |
| SAR-N1–N4 | Governance／MINOR–MODERATE | CARRIED／NONBLOCKING／否 | stale FULLSTACK label、stale handoff、protected surface 外 untracked checkpoints、缺少獨立 frozen-verification role record；適用必要 roles 已存在，未自動關閉這些事項 |
| AUD-N4 | Evidence／INFORMATIONAL | NONBLOCKING／否 | 本 run 的 651 files 僅由目前 local bytes＋manifest hashes 支持，未 Git-track；現行 publisher 不要求將結果提交 Git。後續保存／publication 必須另行授權 |

既有 `53/54 fixture controls` 例外及原 G1 audit independence boundary 均保留，沒有改寫成 `54/54` 或跨模型歷史驗證。

## K. Reconstructibility

| 類別 | 結論 |
|---|---|
| Code | **CONFIRMED**：21 個 implementation files 可由 execution HEAD 重建，與 live bytes 相同 |
| Input | **CONFIRMED**：canonical raw bytes、schema、chronology、參數與四個 execution inputs 可重建 |
| Execution identity | **CONFIRMED**：HEAD、source/input identities、authorization chain 可重建 |
| Full execution state | **PARTIALLY_RECONSTRUCTIBLE**：缺 OS/process history、逐次 telemetry、solver version/log、操作者 launch history |
| Numerical results | **CONFIRMED**：目前保存 primal 足以重算所有 mandatory numerical checks |
| Overall | **足以支持本次 post-solve acceptance**；不等同完整 transient execution replay 或已完成 durable result publication |

## L. 禁止行為計數

| 行為 | 本 session 次數 |
|---|---:|
| Repository files modified | 0 |
| Repository files created／deleted | 0／0 |
| Git stage／commit／push／tag operations | 0 |
| Model constructions | 0 |
| `optimize()` calls | 0 |
| Production reruns | 0 |
| A2／Layer B／DG solves | 0 |
| Sensitivity solves | 0 |
| Repairs | 0 |

計算均在記憶體內完成；沒有建立稽核報告檔。亦未宣稱已將此會話切換成附件指定的 GPT-5.6 Sol／Extra High 設定。

## M. Lifecycle 與下一步

**稽核前：**Full81 numerical execution 已完成、outputs 已發布，independent acceptance pending。

**本次稽核後：**獨立 post-solve 證據支持接受；repository 中的正式結果接受與 thesis-authoritative promotion 狀態尚未被本報告改變。

下一個合法 gate 是**另行明確授權的結果 acceptance／governance publication**，保留上述 carried findings 與 reconstructibility 界線。本 session 沒有建立 acceptance manifest、pointer、notebook，亦沒有開始 downstream substantive analysis。