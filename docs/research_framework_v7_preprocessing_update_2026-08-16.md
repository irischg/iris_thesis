# 研究框架 v7（2026-08-16 preprocessing empirical update）

> **Amendment scope:** 本文件只更新 `research_framework_v7_2026-08-14.md` 中與資料 preprocessing / baseline reconstruction / canonical-input status 直接相關的段落。除本文件明列之段落外，v7（2026-08-14）的研究問題、Layer A/B/DG 邊界、A1–A4、B1–B2、tariff、billing、degradation、cost 與 claim boundary 均維持不變。
>
> **Empirical freeze status:** Scripts 01–05 已完成並通過 component-level preprocessing validation。短期 Load/PV outage-contamination 的 production reconstruction rules 已由 NTUST site-specific pseudo-gap / head-to-head validation 鎖定；long unavailable winter PV 的 mainline 仍維持 conservative zero，alternative reconstruction 仍屬後續 sensitivity。
>
> **Important:** 本次更新取代 v7（2026-08-14）中仍將 Load `±8 weeks / K=3` 與 PV donor `±30 days / K=5` 寫成 mainline reconstruction rules 的舊 wording。兩者不得再作 production mainline hard-code。

---

## Patch A — §0.3 已定方法、待 implementation／parameter population 的項目

將 §0.3 中「final cleaned/canonical dataset 尚待落地、production model input 優先使用既有 `annual_input_existing_pv.csv`」的舊敘述，更新為：

- **Component-level preprocessing through Scripts 01–05 is CLOSED / PASSED.** 已完成：
  - canonical 8,760-hour interval-start observed dataset；
  - observed / planning-baseline separation；
  - Load short-gap method validation與 production reconstruction；
  - PV donor benchmark validation；
  - PV donor-vs-CWA head-to-head validation；
  - PV short-gap CWA production reconstruction；
  - long unavailable PV mainline conservative-zero assignment。
- Script 01 formal observed input固定為 `data/processed/ntust_case_year_observed.*`。
- Script 03 formal Load baseline output固定為 `data/processed/load_annual_baseline.*`。
- Script 05 formal PV baseline output固定為 `data/processed/pv_annual_baseline.*`。
- **仍待完成的 data integration task**：由上述 current v7 outputs 合併產生 final integrated annual model input，並從 interval-start timestamp 重新生成 calendar / summer / TOU / billing-period fields；完成後需再次 assert exactly 8,760 consecutive hours、observed columns unchanged、baseline provenance完整。
- 任何 pre-v7 pipeline 產生的既有 `annual_input_existing_pv.*` 皆視為 **legacy input artifact**。只有當它由 current v7 Script-03 / Script-05 outputs 重新生成並通過 final data audit 後，該檔名才可重新成為 production canonical input；不得因檔名相同而沿用舊數值。

其餘 §0.3 尚待項目（billing registry、\(\kappa\) reproduction、PNNL parameters、Xu-derived degradation implementation、tariff audit、rainflow、winter-PV sensitivity、DG parameter audit）維持原 v7 規格。

---

## Patch B — replace §4.1.2 with the following

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

## Patch C — replace §4.1.3 with the following

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

## Patch D — replace §4.1.4 with the following

### 4.1.4 最低 provenance fields與 current v7 data lineage

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

Current lineage：

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

## Patch E — §4.3 canonical-input wording

保留 §4.3 的 billing-demand calibration equation與 methodology不變，但將所有「production canonical input固定等於既有 `annual_input_existing_pv.csv`」的 wording改成：

Historical billing calibration的 source-of-truth是 **final v7 integrated annual input中的 observed columns**：

\[
\boxed{
P_t^{grid,hist}
=
observed\_load\_kw_t
-
observed\_pv\_kw_t
}
\]

File name本身不是 source-of-truth。

若 final integrated artifact仍命名為 `annual_input_existing_pv.csv/.parquet`，該檔案必須：

1. 由 current v7 `load_annual_baseline.*` + `pv_annual_baseline.*` 重新生成；
2. 保留 Script-01 observed values不變；
3. 使用 current v7 interval-start 8,760-hour timeline；
4. 重新生成 calendar / TOU / billing-period fields；
5. 通過 final integration audit。

任何 pre-v7 同名檔案皆視為 legacy，不得用於 final billing calibration、EOB、Layer A或Layer B。

Billing calibration仍只能使用：

`observed_load_kw - observed_pv_kw`

不得使用：

`baseline_load_kw - pv_available_kw`

因後者含 counterfactual reconstruction。

此外，正式 schema以 `pv_status` 為 current v7 status concept；若 final merged file為向後相容另保留 `solar_status` alias，必須在 data dictionary明確註明兩者映射，不可讓 old schema naming控制 production logic。

---

## Patch F — §25 Phase 1 執行順序

將 Phase 1 的 data item更新為：

1. **Scripts 01–05 component preprocessing CLOSED / PASSED.**
2. **NEXT：build final integrated annual input** from current `load_annual_baseline.*` and `pv_annual_baseline.*`; preserve observed columns, reconstruction provenance, long-PV status；regenerate interval-start calendar / TOU / billing usage-period tags；assert exact 8,760-hour chronology。
3. 建立 `billing_demand_registry.csv`。
4. 建立 `calibrate_kappa.py`，從 final integrated input的 observed Load–PV重建 2025/01–10 calibration pairs。
5. Implement valid-start \(\mathcal S_\beta\)，移除 outage-window circular wrap。
6. Implement \(e_t\) state、10–90% SOC、constant reserve above SOCmin、\(\eta_c=\eta_d=0.90\)。
7. Populate PNNL v2024-derived \(C_E,C_P,FOM,C_{rep}\)，derive CRF與 PWL \(\lambda_k\)。
8. Implement Xu-derived intertemporal degradation segment states、segment cyclic boundary、battery-side degradation energy accounting。
9. Implement case-year Taipower tariff module並重現 September-2025 regression case。
10. Implement post-solve exact demand reporting + ex-post rainflow validator。
11. 跑一次 separately validated winter-PV economic sensitivity。
12. DG cost/fuel/emission parameters可於主線 Layer A後平行完成。

其餘 Phase 2–6維持原 v7。

---

## Patch G — §31.3 Production Layer A 前必做

將原 item 2「final canonical case-year dataset 尚待完成」更新為：

2. **Component preprocessing已完成；final integration尚待完成。** Scripts 01–05 已輸出 audited observed / Load-baseline / PV-baseline artifacts。Production Layer A前必須由 current v7 outputs生成 final integrated 8,760-hour annual input，重新生成 TOU/billing tags並完成 integration audit；pre-v7 `annual_input_existing_pv.*` 不得直接沿用。

其餘 priority ordering依 §25更新後順延，不改原 methodological dependencies。

---

## Patch H — §32 最終 coverage gate

在 data/preprocessing gate中加入或改成下列兩層狀態：

- [x] **Component preprocessing Scripts 01–05 passed**：
  - exact 8,760 interval-start observed timeline；
  - observed Load/PV preserved；
  - Load short-gap production rule = same weekday ±6 weeks / K=1 / outside-gap RMSE；
  - exactly 10 Load hours reconstructed in planning baseline；
  - PV donor benchmark validated；
  - CWA vs donor head-to-head completed on same 604 pseudo-events；
  - PV short-gap production rule = CWA `hourly_ghi_ratio_median` with leave-target-day-out fitting；
  - exactly 10 short-gap PV hours reconstructed；
  - 1,463 long unavailable PV hours assigned zero in mainline and not mislabeled as reconstructed。
- [ ] **Final integrated annual input passed**：
  - generated from current v7 `load_annual_baseline.*` and `pv_annual_baseline.*`；
  - exact 8,760 chronology；
  - observed equality verified；
  - reconstruction/status provenance retained；
  - interval-start calendar / summer / TOU / billing-period fields regenerated and audited；
  - no pre-v7 baseline artifact contamination。

因此 preprocessing的 **method selection + component baseline generation已完成**，但在第二個 checkbox完成前，不應將「final integrated production dataset」標記為 fully CLOSED。

---

# Empirical result snapshot for thesis traceability

## Load

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

## PV short gap

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

# Supersession note

For preprocessing only, this 2026-08-16 amendment supersedes any 2026-08-14 v7 wording that:

- calls Load `±8 weeks / K=3` the production mainline；
- calls PV donor `±30 days / K=5` the production mainline；
- treats short-gap CWA solely as a sensitivity after the Script-04b result；
- states that core-only vs expanded-envelope has already been shown not to affect final 81-point Layer A under the newly selected production rules；
- treats a pre-v7 `annual_input_existing_pv.*` file as canonical solely by filename。

All non-preprocessing v7 specifications remain unchanged.
