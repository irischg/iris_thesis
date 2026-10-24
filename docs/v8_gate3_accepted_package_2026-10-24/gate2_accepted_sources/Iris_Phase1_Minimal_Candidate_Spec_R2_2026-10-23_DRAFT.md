# Iris Thesis — Phase-1 Minimal Candidate Spec R2

**日期：2026-10-23（Asia/Taipei）**
**狀態：CANDIDATE R2 / NOT ACCEPTED / PENDING INDEPENDENT STATIC AUDIT**
**文件類型：additive mathematical specification；不是 MILP implementation、執行授權或 accepted methodology。**

## 1. 文件身份、授權與 provenance

使用者於本 Session 明確授權：整合兩輪已完成的唯讀審查，僅在 repository 外新增本 Markdown；不得改寫 R1、Framework、Registry、Constitution、程式、參數、資料、Git 或歷史結果。授權原文身份見 §2 manifest。正式名稱為 Iris Thesis Phase-1 Minimal Candidate Spec R2；檔名為 Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md。

直接 parent：Iris_Phase1_Static_Audit_Handoff_2026-10-22.zip 內的 Iris_Phase1_Minimal_Candidate_Spec_2026-10-22_DRAFT.md，SHA-256 e86a63fda04319d58545731f92f26776e3b861692990af638cc48c635aebbb4c。Parent 保持不可變。ZIP member 路徑以「archive.zip!/member」表示，未將 member 解壓或改寫。

兩輪審查角色：
- 2026-10-22 Codex Independent Read-only Static Audit：STOP；F-01 tariff epigraph、F-02 floors、F-03 endpoint 定義未封閉。
- 2026-10-23 Codex Audit Follow-up：提出修訂規格、三組 floors、九組 B2 算術證書、PV-only 算術與 objective-dependent tier 新發現。
- 這兩份 Codex 完整報告是本 Session 的對話輸出，沒有獨立持久化檔案；exact file path／byte hash = NOT AVAILABLE（conversation-only evidence），不補造 SHA。ZIP 中 PreIndependent_Static_Audit 是不同的前置文件，不能冒充第一輪 Codex 獨立審查。
- 本 R2 對上述報告採 integration role；核心來源 bytes 已再核對。已完成統計採 carried verified arithmetic 身份，非本輪重新求解。
- 本輪文件作者不是本 R2 的獨立審查者。作者內部一致性檢查不構成 PASS／ACCEPTED。

現行 authority 為 Framework v7.4、Registry v7.4。已讀取各自 acceptance closure，並核對 canonical pointer 的 document／closure／manifest 身份；Registry 的 acceptance 來自正式 closure，不是因檔名有 Candidate R1。Framework 路徑的 _r2 亦只是 provenance revision。Registry v7.3 R3 與 v7.3 freeze 為 accepted immutable predecessors；較早 v7.2／v7.3 手冊描述不能覆蓋 v7.4 accepted chain。Constitution／Protocol 的治理規則繼續適用，歷史版本文字保留原貌。

本 Phase-1 是對既有 accepted v7.4 的新候選方法 delta，不把 v7.4 Full81 接受狀態轉移給 Phase-1。當前狀態以 freshly read CURRENT_STATE 與 canonical pointer 的 primary chain 為準；本文件不另指定一個「latest checkpoint」。

## 2. Source manifest 與 authority roles

下列 manifest 全部為 2026-10-23 本輪唯讀 SHA-256 核對。Repository root 為 C:/Users/Iris C/OneDrive/Desktop/iris_thesis。每列保存完整絕對路徑，archive member 保存精確 member 名稱。命名中的舊版本／candidate 字眼不獨立決定 authority。

角色對應：
- S01–S02：current accepted methodology／evidence documents；S20–S25：其 acceptance／audit 與 canonical activation 證據。
- S03–S04：accepted evidence predecessor／歷史 lifecycle closure，不作 current 方法替代。
- S05–S06：current routing／implementation orientation；不單獨授權執行。
- S07：accepted annual-design core 的 source-level semantic dependency；CORE_VERSION = v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10。
- S08–S12：accepted economic／tariff interfaces v7.2；S13：accepted reconstructed-PV planning series；S14：observed calibration source。
- S15–S16：被 economic interface 綁定的 PNNL cost／degradation package，不因 basename 含 candidate 而重新判成未接受。
- S17–S18：治理 protocol／constitution；S19：本次使用者文件授權。
- S26–S30：handoff containers、immutable parent candidate、前置審查與 decision handoff；不是 accepted Phase-1 authority。

| ID | Exact path / archive member | SHA-256 | Bytes |
|---|---|---|---:|
| S01 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/research_framework_v7_4_2026-09-26_r2.md | 36dd18039667ef908c80cc0be78aa8ea0a89779ab1f1cd23d9ee21541ad2f273 | 216186 |
| S02 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md | 5cc5d091af3be1943531a5a44d648fad58738730581dbf0331cdc2fe86029433 | 245125 |
| S03 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md | e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d | 187796 |
| S04 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/v7_3_methodology_evidence_authority_freeze_2026-09-23.md | 23ff149dd892d08d6aa2cc71848906821eb30f7369024585537a186b2813df6d | 12358 |
| S05 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/configs/current_mainline_pointer.json | ed7005dea8dc423fb4372554b3f8d15fd34c3988441c4fb14c2dede0d64afcb4 | 58156 |
| S06 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/ai_handoff/CURRENT_STATE.md | 043711e8bb422bec7e26ea8263a06ffbf4bf7d28af27cefa91b190f2868b327f | 78260 |
| S07 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/src/annual_design_model_v7_2.py | 9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8 | 124399 |
| S08 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/reference/parameter_registry_v7_2.csv | c0969421853b9a6dd778bba658f869d275ca745921a67c68455188fbad3f76a1 | 7951 |
| S09 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/reference/production_economic_interface_v7_2.json | 9277d310a124e1ae9d91fe1bf5fc1d70210372ca2f3d9e3b1c110cd210c319a9 | 8118 |
| S10 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/reference/taipower_tariff_optimization_ntd2023_v7_2.csv | 5c1582d8ecebba3fc46a4afe61a5ecb66c8a059ef81b4edeba69f67cc9974395 | 19752 |
| S11 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/reference/taipower_seasonal_settlement_matrix_v7_2.csv | ed7f8dbf9d3e41564e3fc289c395df17aa390466b1abc1ea03a5c9e421324b79 | 16427 |
| S12 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/reference/taipower_transition_period_settlement_interface_v7_2.json | f101af4754f89a2126333796e3cea63210140c94cccc1ad925fa9128361c5b88 | 4579 |
| S13 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/data/processed/annual_input_v7_3_reconstructed_pv_mainline_candidate_r3_2026-09-23.parquet | 3ac8dda4a3f1c6983780508cc8131977dd87fda35fc0fc7aff287cc56a50c428 | 554037 |
| S14 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/data_audit/kappa_calibration_pairs_v7_1.csv | c8e32a279f7f3c1b16cda6254831621147d03a9ccaadc4190fb44a7a7ba30020 | 2322 |
| S15 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/parameter_audit/pnnl_v2024_lfp_ntd2023_candidate_cost_packages.csv | f0c167001cf554804152d5f5eb114ee9403c784bb7937f3c5c90bf000203b3e7 | 3306 |
| S16 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/parameter_audit/pnnl_calibrated_pwl_degradation_candidate_packages.csv | 6921ae2171da8318945a48280b41780a9c26ce70a15b373088f6dfb486a1eff3 | 653 |
| S17 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/protocols/Iris_Thesis_Version_Provenance_Management_Protocol_v1_2026-09-21.md | c7a339896ddafc3575d0dc1d3eb78d3dc13ba89bb8acf70791db6cc21c4fd696 | 19977 |
| S18 | C:/Users/Iris C/Downloads/Iris_Thesis_Response_Mode_and_Research_Governance_Constitution_2026-10-03.md | 4f5eaf050d96f84d96e06ebebd53e095f209ad50bb0a0f94a180f2dd0efc9c38 | 22435 |
| S19 | C:/Users/Iris C/.codex/attachments/d161451c-3566-4091-bb30-1256785d305d/Pasted text.txt | 4726dea2467b0b42d0c21e127992889e1aba5dfd65f9cf3d8a92ad938b3f15ec | 14982 |
| S20 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/checkpoints/framework_v7_4_acceptance_closure_2026-09-26.md | 39171a983534f723550ee8003924f28ad88b1abb4cb7a63d2944a1123496dd1f | 18809 |
| S21 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/provenance/framework_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json | 5f883925a4ff08fa1953d4b8b132d7cd93fae2b8774b2e167d42a426cd628a33 | 15144 |
| S22 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/checkpoints/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26.md | 4b7607373f457fc3c607d0f4e3205e55ff2db2a4fc319c41dc7706b9ad391977 | 16944 |
| S23 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/provenance/literature_evidence_registry_v7_4_acceptance_closure_2026-09-26/acceptance_manifest.json | 53074cfe44c0276d6f319497cbe6f5aaf07b255ac0c335f9481174dd968063fe | 16818 |
| S24 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/docs/checkpoints/literature_evidence_registry_v7_4_independent_audit_2026-09-26.md | bf909363d726ecd2f55ce883a71e6a894e718587bbeb6946d879758f246c12ce | 7639 |
| S25 | C:/Users/Iris C/OneDrive/Desktop/iris_thesis/results/provenance/current_mainline_pointer_acceptance_r2/acceptance_closure.json | bf0bb2766d15fd69b27d95436e4375958de1bc98f84dce31b2c1be3249053d71 | 16901 |
| S26 | C:/Users/Iris C/Downloads/Iris_Phase1_Static_Audit_Handoff_2026-10-22.zip | 2828acdde1e7728ec02aeeab5ded0f23840c37bbf2c10672c083b76b33b53f56 | 18853 |
| S27 | C:/Users/Iris C/Downloads/Iris_Phase1_Static_Audit_Handoff_2026-10-22.zip!/Iris_Phase1_Minimal_Candidate_Spec_2026-10-22_DRAFT.md | e86a63fda04319d58545731f92f26776e3b861692990af638cc48c635aebbb4c | 18648 |
| S28 | C:/Users/Iris C/Downloads/Iris_Phase1_Static_Audit_Handoff_2026-10-22.zip!/Iris_Phase1_PreIndependent_Static_Audit_2026-10-22.md | 1b33ab5039400e79c07129b422ebab4b03ae570346bdbb9689b9477ca7d95ca3 | 9802 |
| S29 | C:/Users/Iris C/Downloads/Iris_Thesis_Phase1_Handoff_Bundle_2026-10-22.zip | 6ffa856387cf2aaedd2c70e8fb23016f6053b62cd9ef607c157db97b7cd21560 | 34480 |
| S30 | C:/Users/Iris C/Downloads/Iris_Thesis_Phase1_Handoff_Bundle_2026-10-22.zip!/Iris_Thesis_Phase1_Decision_Handoff_2026-10-22.md | c9687b6852b0602d38bcc655fd2bbecc5472cd3237b66f840ebbddfd25ff549e | 26467 |

外部 evidence assessment 沿用前輪已核查結果，非本輪新檢索：
- Laws et al. (2018), Renewable Energy 127, 896–909，DOI 10.1016/j.renene.2018.05.011：獨立非負 inverter kW／battery kWh 與 resilience economics；不是通用 positive floor。
- Bazdar, Nasiri & Haghighat (2024), Energy 308, 132836，DOI 10.1016/j.energy.2024.132836：Eq.17 設計域與 integer battery modules；Table A2 的 2.1 kWh 是其模組參數，不是 NTUST minimum。
- Gorman et al. (2023), Applied Energy 342, 121166，DOI 10.1016/j.apenergy.2023.121166：10／30 kWh usable-energy 情境及固定 2 h duration，不轉成本案 nameplate floor 或 P/E coupling。
- 前輪以 SJR 2024 Q1 作上述期刊分區依據；不是 JCR 聲明，亦不倒推 2018／2023 發表年分區。數值 floor 不由 Q1 身份導出。
- NTUST 華夏校區 2 MWh 官方資料是另一校區建置規模，未提供本案最低 PCS／GFM threshold。網址：https://www.ntust.edu.tw/p/406-1000-152616%2Cr1182.php?Lang=en 。Web byte hash = NOT AVAILABLE；未保存或建立網頁副本。

**NO VERIFIED NTUST GFM ELIGIBILITY THRESHOLD FOUND**
**Q1 literature supports the methodology, but numerical floors remain case-specific research assumptions.**

## 3. Research scope、時間、輸入與單位

研究問題：NTUST 既有 PV0、BESS AC/PCS power P_B [kW]、battery-side nameplate energy E_B [kWh]、單一年度 regular contract capacity CC [kW] 的 annual Cost–ENS planning。PV0 固定、額外 PV 容量為零。

T=8760，Δt=1 h。正常 interval t=0,…,T−1，state t=0,…,T。使用 S13 的 baseline_load_kw = L_t、pv_available_kw = V_t、timestamp_start／timestamp、billing_usage_period_id、season、tou_period。這是唯一 planning series；κ calibration 維持 observed evidence route，不混換為 reconstructed planning PV。

已核實時間為 2024-11-01 00:00 至 2025-10-31 23:00；8760 個不重複連續小時；使用的 L/V 無缺值或負值。L_min=42 kW，L_max=5179 kW；annual load=21293763 kWh；annual PV=427105.4351329623 kWh；此 dataset 全部 V_t≤L_t。

Candidate study grid：α∈{0.10,0.25,0.50}，β∈{4,8,12} h。α 是 service-load proxy，不是已盤點 critical equipment inventory。
n_β=β/Δt，S_β={0,…,T−n_β}，事件不跨年、不 wrap；起點數依序8757／8753／8749。每個事件有其完整窗口 load/PV foresight；這是 conditional achievable service capability，不是真實操作成功率或年度停電機率。

所有功率含 shed／curtailment 為 AC kW；SOC／segment energy 為 battery-side kWh；ENS／D_s 為 AC kWh。η_c=η_d=0.90 固定且各用一次。成本為 constant NTD-2023/year。無 paid export、T-REC 收益、DG、PV0 sunk CAPEX、額外 subsidy cashflow 或 outage operating／cycling cost。

## 4. B1：zero／positive branches 與 floors

### Branch 0

P_B=E_B=0；全部 battery powers、normal／outage SOC、Xu segment states 為零。正常 PV 可自用／棄光，CC 仍最佳化。依本研究 branch assumption，沒有 island-forming source，停電 PV 不服務負載：
shed_{sτ}=Q_{sτ}，ENS_s=D_s，r_ENS=1。

### Branch +

\[
10\le P_B\le\bar P,\qquad20\le E_B\le\bar E.
\]

**P_lo=10 kW；E_lo=20 kWh。**
角色：user-authorized proposed mainline research assumption，ASSUMPTION，非 accepted engineering threshold。不是 Q1 規定、NTUST GFM 認證、optimal sizing 或 full-service adequacy。
P/E 兩個 sizing variables 獨立；無固定 ratio、1C、1–8 h 或 installation binary。10／20 的角點不限制其他可行 P/E 組合。

兩分支未來分別建置／求解／比較；本輪只指定數學 contract，沒有建置。Normal no export、strict hourly charge/discharge exclusivity；outage fixed PV-first，不加 hourly outage mode binary。Positive branch 採 conditional island-ready BESS assumption，不聲稱10 kW PCS已驗證能支撐全校 PV。

CC_min=0 是繼承模型域，不是台電法律最低契約容量聲明。CC upper bound 見 §9。

## 5. B3：Normal annual dispatch 與 Xu states

\[
p_t^{grid}+p_t^{dis}+v_t^{use}=L_t+p_t^{ch},
\quad0\le v_t^{use}\le V_t,\quad v_t^{curt}=V_t-v_t^{use},\quad p_t^{grid}\ge0.
\]
\[
0\le p_t^{ch}\le P_B,\quad0\le p_t^{dis}\le P_B,\quad u_t\in\{0,1\},
\]
\[
p_t^{ch}\le M_{ch}u_t,\qquad p_t^{dis}\le M_{dis,t}(1-u_t).
\]
u_t=1 允許 charging，u_t=0 允許 discharging；idle 可屬任一 mode。M 是 §9 推得的常數；不使用 u_t P_B 的連續乘積。

\[
e^N_{t+1}=e^N_t+\eta_cp_t^{ch}\Delta t-p_t^{dis}\Delta t/\eta_d,
\quad0.10E_B\le e^N_t\le0.90E_B,\quad e^N_T=e^N_0.
\]
e^N_0 自由但受相同 bounds／cyclic 約束；不另固定50%初始 SOC。

Xu-derived intertemporal PWL：k=1,2,3，b=(0,0.30,0.60,0.80)，w=(0.30,0.30,0.20)。
\[
e^N_t=0.10E_B+\sum_k e_{t,k},\qquad0\le e_{t,k}\le w_kE_B.
\]
\[
p_t^{ch}=\sum_kp_{t,k}^{ch},\quad p_t^{dis}=\sum_kp_{t,k}^{dis},\quad p_{t,k}^{ch},p_{t,k}^{dis}\ge0,
\]
\[
e_{t+1,k}=e_{t,k}+0.90p_{t,k}^{ch}\Delta t-p_{t,k}^{dis}\Delta t/0.90,
\quad e_{T,k}=e_{0,k}.
\]
Aggregate SOC equation 由 segment equations 加總成立；可作 derived identity，避免把兩者視為不同物理狀態。
\[
C_{deg}=\sum_{t,k}\lambda_kp_{t,k}^{dis}\Delta t/0.90.
\]
繼承 accepted segment semantics，不做 hourly reset、不另增 segment ordering binaries，不重複計效率／replacement。λ 的單位是 NTD-2023 per battery-side discharged kWh。

**不得帶回舊 Layer A 的 e_t≥0.10E_B+R(α,β) 或 P_B≥舊 power adequacy。**本候選服務要求由 ENS cap 決定；只有 B2 reference construction 用充分服務容量，不把該容量當全部設計的 lower bound。

## 6. B3：Fixed-PV outage recourse 與 ENS

僅 Branch +，s∈S_β，τ=0,…,n_β−1：
\[
Q_{sτ}=\alpha L_{s+τ},\quad V^O_{sτ}=V_{s+τ},
\quad S_{sτ}=\max(V^O_{sτ}-Q_{sτ},0),\quad R_{sτ}=\max(Q_{sτ}-V^O_{sτ},0).
\]
Q,V^O,S,R 是固定參數；上述參數 max 可在資料準備時純算術求得，不是 endogenous MAX。

PV-first 先供 min(Q,V^O)：
\[
0\le c_{sτ}\le S_{sτ},\quad c_{sτ}\le P_B,\qquad
0\le d_{sτ}\le R_{sτ},\quad d_{sτ}\le P_B,
\]
\[
shed_{sτ}=R_{sτ}-d_{sτ},\qquad curt^O_{sτ}=S_{sτ}-c_{sτ}.
\]
\[
e^O_{s,0}=e^N_s,\qquad
e^O_{s,τ+1}=e^O_{s,τ}+0.90c_{sτ}\Delta t-d_{sτ}\Delta t/0.90,
\]
\[
0.10E_B\le e^O_{s,τ}\le0.90E_B\quad(\tau=0,\ldots,n_\beta).
\]
Grid outage import=0；事件 terminal 只需10%技術下界，不恢復事件前 SOC、不 cyclic。事件彼此獨立反事實，不依次耗用同一串年度 SOC。S R=0，因此 c,d 自動互斥，不需要新增 mode binary 或其 Big-M。

\[
D_s=\sum_\tau Q_{sτ}\Delta t,\quad ENS_s=\sum_\tau shed_{sτ}\Delta t,\quad
D_\Sigma=\sum_sD_s>0,\quad r=\sum_sENS_s/D_\Sigma.
\]
所有合法起點等權 aggregate；重疊窗口不是實際一年發生數千次停電，D_Σ 不是 annual load。Q=αL，不能改為α[L−PV]^+。0≤r≤1。若報 pass rate，稱 structured-start event-coverage proportion，不稱機率 reliability。

## 7. Annual economics 與已核實參數

\[
C=CRF(C_PP_B+C_EE_B)+FOM_PP_B+FOM_EE_B
+\sum_t\rho_t^{energy}p_t^{grid}\Delta t
+\sum_m B_mCC+\sum_{m,q}C_{over,m,q}+C_{deg}.
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

Source package ID：pnnl_v2024_lfp_2023_point_10mw_4to10h。10 MW／4to10h 是既有 cost package label，不是設備最小／最大容量或本研究 duration constraint。FOM 不再乘 CRF；C_rep 不再乘 CRF，不另計整包 replacement。λ 繼承 S16／S09 的 PNNL-calibrated Xu-derived package；不由新結果反向挑 cost bracket。

Energy rates 以 S10 的 (parameter_id=energy_{season}_{tou_period}, usage_year) 唯一列映射，每列取 value_constant_ntd2023；N/A 必須拒絕，不填零。月份使用 billing_usage_period_id 的 usage year。純季 B_m 取 basic_{season}_regular；May／October 取兩季 regular basic rates 的算術平均。Supplementary contract components 固定0。Σ_m B_m=2206.3163138237587 NTD-2023/kW-year。S11 決定各 active season／period 的 overcontract rate；S12 提供 masks／period order metadata。不得從記憶重建電價或使用 nominal NTD 混入 constant-dollar objective。

## 8. F-01：Objective-independent exact billing／transition

### 8.1 Exact quantities

q 為依 peak→half→sat_half→off 排序的 eligible TOU periods。純非夏月 peak=N/A，省略該 component。I_mq 為該 usage-month／period 的實際 timestamp set。
\[
G_{m,q}=\max_{t\in I_{m,q}}p_t^{grid},\quad D_{m,q}=\kappa G_{m,q},
\]
\[
a_{m,q}=\max(0,D_{m,q}-CC),\quad z_{m,0}=0,
\]
\[
z_{m,q}=\max(z_{m,q-1},a_{m,q}),\quad
\Delta_{m,q}=z_{m,q}-z_{m,q-1}\ge0,
\]
\[
h_{m,q}=\max(0,\Delta_{m,q}-0.10CC),\quad
W_{m,q}=2\Delta_{m,q}+h_{m,q}.
\]
Fixed applicable rate 時 C_over,mq=ρ_mq W_mq。每個「新增」區段各有10%CC的2×allowance，其餘3×；不是全月共享 allowance，也不重複計各 period raw exceedance。

R1 的單向 D epigraph 可操控分段：CC=100、真 maxima=(100,100,120)，虛增中間 maximum 至110，費用由50ρ變40ρ；ρ=32.05732664233577 時由1602.866332變1282.293066 NTD-2023。此為已核實靜態反例。

S07 L1524–1636 使用 exact maxima／raw／running maxima；較早 file-header／L1448 註解的 epigraph 用語過時，實際 constraints 為準。S07 L1643–1650 的 tier allowance t≤Δ、t≤.1CC 則靠成本 objective 推到 min；ENS-secondary 不保證等式。例如Δ=20、CC=100，t=9.99仍可行，比真 t=10 多計0.320573 NTD-2023，可能被1元cost band容納。此為 overstatement 風險，不推翻舊 cost-first objective 的tightness。

R2 以 exact h 修正；若需要 t，僅定義 t=Δ−h。**所有 billing等式在任何 objective 下成立。**這是保持相同 tariff function 的 formulation correction，不是新計費方法；本輪沒有修改 accepted core。

### 8.2 Exact MAX 的 MILP contract

凡 endogenous y=max_i x_i，且 finite L_i≤x_i≤U_i，令 U=max_i U_i：
\[
y\ge x_i\quad\forall i,\qquad
y\le x_i+(U-L_i)(1-b_i)\quad\forall i,
\]
\[
\sum_i b_i=1,\qquad b_i\in\{0,1\}.
\]
可包含常數0 operand。可用 exact native MAX general constraints 實現同一 contract；不可只留 epigraph，不預先宣稱 presolve 後 binary 數。不得把此處必要 billing binaries 誤認為被禁止的 outage mode／installation binary。

Finite bounds（§9 每 cell 常數）：
- 0≤p_grid,t≤L_t+M_ch；G_mq upper=max_{I_mq}(L_t+M_ch)，D upper=κG upper。
- D−CC∈[−CCbar,Dbar]；a∈[0,Dbar]。
- z_q upper=max_{j≤q}Dbar_j；0≤Δ_q≤zbar_q。
- Δ−.1CC∈[−.1CCbar,zbar_q]；0≤h≤Δ；0≤W≤3zbar_q。
上述是保守有效界，不用任何尚未執行之 optimal solution 推導。

### 8.3 Transition source 與 binary product

May 16–Oct 15 為夏季，依每小時 timestamp applicability。Class A 只有一個 season；Class B 兩季相同費率；Class C 兩季不同費率。

A／B 直接對 eligible hours 建立 exact G_mq，適用單一／共同ρ。C 對各 season 先建立 exact G_e,G_l，再 exact G_mq=max(G_e,G_l)，D=κG_mq。e,l 按時間先後，不按名稱排序；現有 masks 不交錯。若新 masks 交錯，不能默默套用兩段 contract。

令 D_e=κG_e、D_l=κG_l，其 finite upper U_e,U_l；d=D_l−D_e∈[−U_e,U_l]。
按 S07 L123–160／L1698–1764：
\[
\tau=\max(10^{-4},100f,100\epsilon_{machine}\max(1,L_{max})),\qquad g=10f,
\]
f 是實際 solver FeasibilityTol（kW-row尺度）。若 f=10^{-6}，τ=10^{-4} kW、g=10^{-5} kW；這是條件例，非本輪 solver 設定驗證。
\[
d\le\tau+(U_l-\tau)b,\qquad
d\ge-U_e(1-b)+(\tau+g)b,\qquad b\in\{0,1\}.
\]
b=0 選 earlier／numerical tie；b=1 選 later clear maximum。需 U_l≥τ+g；否則不得照搬此常數 contract 而不檢查。開區間(τ,τ+g)為 unresolved guard，Class C 不接受落入該區間的結果。Class B 相同費率的 source status 只作 diagnostic。這是繼承的數值 convention，不是官方計量精確性聲明。

Wbar=3zbar_q；Y=bW 使用：
\[
0\le Y,\quad Y\le W,\quad Y\le Wbar\,b,\quad Y\ge W-Wbar(1-b).
\]
\[
C_{over,m,q}=\rho_eW+(\rho_l-\rho_e)Y.
\]
不存在未線性化連續乘積。May／October regular basic charge 的50/50不適用於overcontract。S12 較早 unresolved institutional wording 不被改寫；canonical source pricing 的角色為 accepted case formulation，不能擴張為所有台電用戶通用官方規定。

所有最終 billed maxima、canonical timestamps、month/season rates、tier費用與annual cost須從 hourly dispatch 獨立重算並與模型核對。κ hourly proxy 不等於實際15-minute meter讀值；不得把solver auxiliary直接當量測證據。

## 9. B2：Analytical zero-ENS proof 與 finite cost domain

### 9.1 Reference construction

\[
W_\beta=\max_{s\in S_\beta}\sum_{\tau=0}^{n_\beta-1}L_{s+\tau}\Delta t,
\quad P_{ref}=\max(P_{lo},5179\alpha),
\]
\[
E_{ref}=\max(E_{lo},\alpha W_\beta/0.72).
\]
W_4=20451、W_8=39601、W_12=55977 kWh。全域α=.10/.25/.50的最大服務功率=517.9／1294.75／2589.5 kW。

Normal：p_ch=p_dis=0、v_use=min(V,L)、p_grid=[L−V]^+、e^N_t=.90E_ref。
Xu states e_{t,k}=(.30,.30,.20)_k E_ref 為常數；segment powers=0；aggregate SOC=.10E+.80E=.90E；全部 cyclic，C_deg=0。
CC_ref=κmax_t p_grid=κ×4985=5036.678794296927 kW，因此所有 overcontract=0。

Outage：c=0、d=R≤Q≤P_ref。全窗口 battery-side discharge≤αW_β/.90≤.80E_ref，所有 prefix亦不超過此值（R≥0）；故SOC≥.10E_ref，全部ENS=0。PV surplus可棄，無需假定必充電。

此證明要求：normal初始SOC自由且cyclic；允許curtailment；grid可負擔normal負載；無額外緊的硬性 interconnection／investment cap。未新增site cap。證明適用本候選方程，不是實機GFM驗證，也不是optimized sizing。
Reference May/Oct Class-C d 依 sat_half/off順序為410.208944932、−1005.315025141、372.825371133、1289.228112643 kW，遠離前述示例guard；未以guard排除reference。

### 9.2 Cost certificate 與 RES separation

Reference energy charge=56124521.04295606、basic charge=11112506.59134749 NTD-2023/year；故
\[
C_{full}=67237027.63430355+
466.41388392833P_{ref}+932.6520871107918E_{ref}.
\]
此為feasible reference cost，不是EOB optimum。

全部cost groups非負，a_P,a_E>0，因此 L_other=0：
\[
\bar P=C_{full}/432.74073392833,\qquad
\bar E=C_{full}/905.2556621107918.
\]
r=0 reference對所有ε∈[0,1]可行，所以cost-first最適解C*≤C_full；限制到C≤C_full及這些bounds保留其全部cost-optimal designs。
若加入負收益或額外cap，須重新證明，不得沿用。

RES理論stage1先在未預設cost-first容量界的positive domain上min r；由r≥0與上述有限構造，解析r_min=0。其後stage2 min C | r=0才套cost certificate。有限uniform domain包含同一reference，因此保留此零ENS端點與cost optimum；不是用小domain假定無界RES結論。

CC structural upper：
\[
CCbar_{struct}=\kappa(5179+\bar P).
\]
超過全部billed maxima後overcontract已零，regular basic正向遞增，因此不會改善cost或ENS；可保留cost-optimal解於此界。另由非負cost：
\[
CCbar_{cost}=C_{full}/2206.3163138237587.
\]
本R2的共同cost-sublevel domain採CCbar=min(CCbar_struct,CCbar_cost)，兩界皆報告。不是法律上限。Branch0有idle feasible cost67237027.63430355<C_full，也可使用此共同cost cap；不能反向拿zero branch成本當positive ε=0證書。

### 9.3 九組 numeric certificates

全部為carried independently recomputed arithmetic／feasible reference certificates，**不是Solver outcome**。本輪source hashes一致；不以重述表格冒充新執行。10<517.9且20<2840.416666667，因此mainline floor不影響任何一列；sensitivity A/C同樣低於這兩門檻。以下展示值四捨五入，後續implementation須由full precision公式重算，若保存decimal upper bounds須向上取整，不能用向下rounded表格值當硬界。

| α | β h | P_ref kW | E_ref kWh | C_full NTD-2023/year | Pbar kW | Ebar kWh | CCbar_struct kW | CCbar_cost kW |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| .10 | 4 | 517.900 | 2840.417 | 70127703.92 | 162054.779 | 77467.291 | 168967.468 | 31784.973 |
| .10 | 8 | 517.900 | 5500.139 | 72608299.40 | 167787.069 | 80207.506 | 174759.184 | 32909.288 |
| .10 | 12 | 517.900 | 7774.583 | 74729564.76 | 172689.000 | 82550.784 | 179711.933 | 33870.739 |
| .25 | 4 | 1294.750 | 7101.042 | 74463718.34 | 172074.669 | 82257.114 | 179091.232 | 33750.246 |
| .25 | 8 | 1294.750 | 13750.347 | 80665207.05 | 186405.394 | 89107.653 | 193570.523 | 36561.035 |
| .25 | 12 | 1294.750 | 19436.458 | 85968370.44 | 198660.222 | 94965.847 | 205952.395 | 38964.662 |
| .50 | 4 | 2589.500 | 14202.083 | 81690409.05 | 188774.485 | 90240.153 | 195964.173 | 37025.701 |
| .50 | 8 | 2589.500 | 27500.694 | 94093386.46 | 217435.936 | 103941.229 | 224922.754 | 42647.279 |
| .50 | 12 | 2589.500 | 38872.917 | 104699713.25 | 241945.592 | 115657.618 | 249686.498 | 47454.534 |

### 9.4 Normal／outage bounds

每cell採自己的certificate，不能借另一cell較小C_full。Normal主contract：
M_ch=Pbar；M_dis,t=min(Pbar,L_t)，可用共同M_dis=min(Pbar,L_max)=5179 kW。
由strict mode與no export，discharge時p_dis≤L_t；charge時p_grid≤L_t+Pbar。可選的同域有效tightening為
M_ch≤min(Pbar,.80Ebar/(.90Δt))、
M_dis,t≤min(Pbar,L_t,.90×.80Ebar/Δt)；這是數學界，不是新增物理duration限制。

Outage無mode binary，**outage mode Big-M=NOT APPLICABLE**。僅需
c≤min(S,Pbar)、d≤min(R,Pbar)、0≤shed≤R、0≤curt^O≤S、e^O≤.90Ebar；
max d≤αL_max，max c≤max S。不得將max outage deficit用作normal PCS sizing upper bound。
Bound鬆緊／numeric conditioning／runtime尚未經Pilot驗證。

## 10. F-03：EOB、RES、ε 與 lexicographic endpoint

x包括P/E、CC、全部normal dispatch/binaries/SOC/segment states、outage recourse、exact billing auxiliaries。F_+(ε)為同一candidate positive domain加r≤ε。
\[
C_+^*(\epsilon)=\min_{x\in F_+(\epsilon)}C(x),
\quad
r_+^*(\epsilon)=\min_{\substack{x\in F_+(\epsilon)\\C(x)=C_+^*(\epsilon)}}r(x).
\]
\[
r_{EOB+}=r_+^*(1).
\]
第二階段保留完整decision space；不能固定第一階段任意P/E/CC/normal SOC。Warm start可用，不等於fixing。ENS最小不保證唯一dispatch；不宣稱唯一解或另加第三objective。

EOB0：min C於Branch0，r=1。Global EOB：
\[
(C_{global}^*,r_{global}^*)=
lexmin\{(C_0^*,1),(C_+^*(1),r_{EOB+})\}.
\]
EOB+不能取代global baseline。若呈現cost premium，精確定義為C_+^*(ε)−C_global^*；百分比需C_global^*>0。數值近似報告另列實際reconciled endpoints與bounds，不混用incumbent／lower bound為同一最適值。

RES：解析stage1 r_min=0；stage2 min C subject to r=0；即positive ε=0。沒有solver得到的minimum-cost RES數值。

ε-frontier：min C subject to r≤ε，再在cost-optimal set min r；Branch0僅ε≥1可行。本文件主要frontier報positive branch，global zero點另外標示。
最小grid：
\[
\{0,\tfrac12r_{EOB+},r_{EOB+},1\}.
\]
數值上以已記錄的hat r_EOB+產生近似grid；按τ_r=10^-6排序去重，保留0／1精確端點並保存每個raw label到代表點的mapping，若中間點近0／1則合併到端點。ε limit與achieved r分欄。ε=1可重用同一EOB+結果，ε=0與RES相同定義；禁止用不同domain產生端點後混圖。

## 11. Numerical targets、reconciliation 與 replay

**Proposed numerical targets — pending Pilot verification.**
本輪未證明可達，未修改任何production solver settings。

| 項目 | Proposed target |
|---|---|
| Primary absolute cost gap | U_C−L_C≤1 NTD-2023/year |
| Same-cost allowance δ_C | 1 NTD-2023/year，事前固定 |
| Secondary ENS absolute gap | U_r−L_r≤10^-7 |
| ENS reporting/comparison τ_r | 10^-6；另報τ_r D_Σ kWh |
| Cost reconciliation target | 10^-3 NTD-2023/year |
| Cost numeric representation | 可用C/1000，但所有cap/gap換算並以原單位報告 |

最小procedure為兩階段單目標求解（未來授權後）：
1. Stage1記錄solver incumbent、proven lower bound L_C、獨立reconciled feasible upper U_C與gap；未達target不能宣稱取得指定精度端點。
2. Stage2保留全部variables，以r為objective，加入C≤min(C_full,U_C+δ_C)。Exact billing在此仍成立。
3. 獨立重算cost、ENS與物理residual；記錄stage2 U_r/L_r／gap，不能只憑status稱最適。

C_full cap保留exact cost optimum，但明確將近似cost band限制於同一certificate sublevel；不宣稱搜尋了超出此domain的全部near-optimal designs。
若成本重算允許誤差τ_C：
\[
C(x_2)-C^*\le(U_C-L_C)+\delta_C+\tau_C.
\]
建議targets下約≤2.001 NTD-2023/year；此為conditional數值誤差budget，不是已執行證書。沒有保證其ENS接近精確lexicographic r。Exact theoretical optimum、tolerance-bounded approximate endpoint、incumbent、lower bound、reconciled achieved值均需不同欄位。

不以relative MIP gap當same-cost tolerance；7000萬元的10^-4約7000元。r接近零時不用relative gap判定。τ_r亦不是對每條SOC／balance constraint任意放寬10^-6；physical residual以原單位、實際FeasibilityTol另記。Native multiobjective如將來使用，必須證明其base-value退化規則等價上述explicit cap，不能默認ObjNAbsTol就是本規格δ_C。

Approximate Global EOB在兩分支stage1取得U_0,U_+與L_0,L_+；用共同U=min(U_0,U_+)、L=min(L_0,L_+)與共同cap min(C_full,U+δ_C)，在符合共同cap的兩分支各min r後比較。不能用非傳遞的pairwise「差不多同成本」判定。Individual EOB+仍用其自己的positive cost band，不混作global secondary解。

Replay另名為「fixed-design / fixed-normal-SOC min-ENS replay」：
固定P/E、CC及整條normal SOC（normal結果保留，不重新最佳化），每事件用§6相同outage可行域min ENS_s。比較ENS_main,s與ENS_replay,s；理論上replay最優≤main，數值比較須納入replay實際gap／residual。可報event比較解析度10^-6 D_s kWh，但不得讓容差掩蓋較大的未解gap。Branch0均ENS=D_s。
Replay不能探索另一套同成本設計／SOC，因此不是正式lexicographic tie-break；若replay改善超出已證明secondary gap／residual，需調查endpoint實作／精度，不能改名掩蓋。

## 12. Positive-branch PV islanding claim boundary

Positive battery存在但outage c=d=0的構造仍容許PV-first服務：
\[
r_{PV}=1-\frac{\sum_s\sum_\tau\min(\alpha L_{s+\tau},V_{s+\tau})\Delta t}{D_\Sigma}.
\]
前輪read-only算術命令已成功exit_code=0；不是未完成命令。數值如下：

| α | β=4 | β=8 | β=12 |
|---:|---:|---:|---:|
| .10 | .804499863 | .804422879 | .804345053 |
| .25 | .919760662 | .919729065 | .919696998 |
| .50 | .959873167 | .959857366 | .959841329 |

相對Branch0 r=1，改善約19.55–19.57、8.02–8.03、4.01–4.02 percentage points。這是conditional可行構造，不是EOB+ optimum；不能把全部改善歸因於電池能量。10／20 floors不能消除此branch service jump，也不證明實體10 kW PCS對全校PV具GFM能力。維持本研究工程簡化，不新增transient／distribution flow／商用certification blocker。

## 13. Floor sensitivity preregistration

| Scenario | P_lo kW | E_lo kWh | P_lo/Lmax % | E_lo/Lmax h-equivalent | Role |
|---|---:|---:|---:|---:|---|
| A | 1 | 1 | .019308747 | .000193087 | Low-intervention sensitivity |
| B | 10 | 20 | .193087469 | .003861749 | Proposed mainline |
| C | 50 | 100 | .965437343 | .019308747 | Higher-floor sensitivity |

三者均ASSUMPTION。B功率約為最小α尖峰517.9 kW的1.93%；滿研究SOC可用AC能量=.72×20=14.4 kWh；角點支援10 kW約1.44 h，不能解讀為支援517.9 kW。A干預較小但更接近極小BESS啟用PV的邊界；C排除更多小容量partial-service designs。

未來優先(α,β)=(.10,4)的EOB+及high-ENS frontier，對三組採相同cost／ENS/tariff／input/tolerance contract。EOB+各自報端點；跨floor frontier比較使用共同absolute ε，不以各自normalized端點位置冒充同一ε。具體額外ε點在執行前另行固定；本輪不執行、不產生結果。配對變動只辨認joint floor effect；必要時再另行授權one-factor檢查，不從配對比較斷言是P或E單獨造成。

靜態上F_C⊆F_B⊆F_A，固定ε的精確minimum cost不會隨floors提高而下降。三組均保留九組r=0 reference與同一bounds，但不代表相同optimal frontier。EOB+是否貼floor、partial-service最適解是否排除、runtime及numeric conditioning = PENDING PILOT VALIDATION。小容量成本沿用已凍結cost-scale假設，不把它解讀為小商用設備採購報價。

## 14. Accepted v7.4 → Phase-1 methodology delta

此為new candidate methodology變更，明示而不靜默套入accepted code：
1. 舊all-start hard reserve／adequacy轉為aggregate ENS／ε，不同時帶入舊reserve。
2. Normal採strict hourly binary；保留free PV-use、curtailment、grid charging、no export。
3. Fixed-PV outage採PV-first獨立recourse、normal SOC handoff，無outage mode binary。
4. Zero／positive branches分開，conditional island-ready eligibility floors=10／20。
5. EOB_global／EOB+／RES／ε／fixed-SOC replay明確分離。
6. 不新增T-REC、paid export、DG或outage wear；不改已接受的效率、SOC、monetary basis、κ evidence route、PNNL cost／Xu semantics。
7. F-01修正錯誤epigraph繼承；exact tier為新objective下相同tariff函數的formulation correction，非計費方法重設。
8. PV0 correctness優先；新增PV離散固定情境及selective continuous joint-sizing屬後續gate，不先行加入內生PV。2026/10/16歷史joint pilot存在由使用者確認，不重搜、不將其轉述數字當accepted新Phase-1結果。

## 15. R1 → R2 additive changelog 與作者一致性檢查

| 項目 | R1 | R2 |
|---|---|---|
| Floors | NEEDS_STUDY_DECISION | user-authorized proposed10／20；非正式acceptance |
| F-01 | cost-facing epigraph | exact G,D,a,z,Δ；objective-independent h,W；完整transition MILP contract |
| F-03 | secondary minENS與fixed-design replay可混用 | 完整空間cost-first/ENS-second；replay另名；global不同於positive |
| Numerical targets | 未定 | explicit proposed gaps／allowance／reconciliation與誤差界，pending Pilot |
| B2 inputs | 多項numeric unavailable | source identities與完整係數／reference／九組bounds |
| PV branch boundary | qualitative | 加入已核實PV-only算術與貢獻歸因限制 |
| Floor sensitivity | 未固定方案 | A/B/C與(.10,4)優先計畫，未執行 |
| Lifecycle | R1 draft／STOP findings | additive R2；pending新independent static audit |

作者內部檢查（不是獨立審查verdict）：
- 變數／index／AC-DC單位已逐節列明，Δt與效率位置一致。
- Exact tariff quantities不依賴objective；Class-C product已線性化；guard未隱藏。
- Normal cyclic與outage noncyclic terminal並存，outage initial由normal相同起點state決定。
- Branch0不獲positive PV island service；P/E independent；無installation binary。
- Analytical RES r_min與cost-first有限界分開；所有cost-optimal endpoints使用同一domain。
- 未繼承舊analytical reserve／power adequacy；未新增售電或T-REC。
- 九組numeric tables標為reference而非optimized results；未宣告可達proposed solver targets。
- R1／accepted文件保持原貌；source hashes在本輪核對，沒有執行Git指令。

## 16. Residual findings 與剩餘 gates

Authoring時未識別需靠改方法或猜測掩蓋的material mathematical defect；這不是獨立無缺陷證明。若下一輪提出material defect，標記HOLD並走additive後繼修訂，不覆寫歷史候選。

Nonblocking limitations：floor為研究假設；無NTUST GFM minimum來源；PV eligibility jump；hourly κ proxy非15-minute量測；cost-scale extrapolation；perfect outage foresight；structured starts非停電機率；transition case-rule非普遍官方規定；bound可能鬆；conversation-only審查報告無持久化byte身份。

Pending：
- 新的獨立唯讀靜態Audit Session，包含source identities、B2證明、objective-independent tariff、endpoints／tolerances審查。
- 使用者檢視與之後另行決定acceptance／implementation授權。
- 未來獲授權後才可驗證implementation parity、physical／billing residual、MIP gaps、endpoint reproduction與floor sensitivity。
- 本文件不授權model build、solver、PV0 pilot、sensitivity、production、authority re-freeze或Git mutation。

## 17. Integrity 與 explicit stop

本輪唯一授權新增物：
C:/Users/Iris C/Downloads/Iris_Phase1_Minimal_Candidate_Spec_R2_2026-10-23_DRAFT.md

Existing files modified=0；Repository files modified=0；Git operations=0（未執行任何Git指令）；Model builds=0；Solver calls=0；Production reruns=0；Self-acceptance=0。只進行來源讀取／hash與文件建立，不匯入project model／runner、不執行optimize。

本檔自我SHA不嵌入以避免循環；交付回覆另提供最終bytes與SHA-256。這是單一新增Markdown，沒有伴隨manifest／log／code／report檔案。

**CANDIDATE R2 / NOT ACCEPTED / PENDING INDEPENDENT STATIC AUDIT**
**完成本文件即停止。下一步僅為使用者檢視，再安排新的獨立唯讀靜態Audit Session。NO CODING / NO SOLVER / NO GIT MUTATION / NO SELF-ACCEPTANCE。**
