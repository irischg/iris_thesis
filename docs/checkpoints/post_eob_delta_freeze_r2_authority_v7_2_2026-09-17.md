# Post-EOB Delta-Freeze r2 — Authority Checkpoint

**Checkpoint date:** 2026-09-17 (Asia/Taipei) · **Captured:** 2026-09-17T20:30:51+08:00 / 2026-09-17T12:30:51Z
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`

> **Current post-EOB delta-freeze authority: the r2 package**
> `results/provenance/post_eob_delta_freeze_v7_2_20260917_r2/`

Additive governance artifact. No production source, historical artifact, run manifest or methodology
document was modified.

---

## 1. Supersession

| Field | Value |
|---|---|
| Supersedes | `results/provenance/post_eob_delta_freeze_v7_2_20260917/` |
| Scope of supersession | **post-EOB delta-freeze authority only** |
| r1 status | **REJECTED_BY_INDEPENDENT_AUDIT** |
| r1 disposition | **PRESERVED IMMUTABLE** as historical audit provenance |
| Rejection nature | **package / governance only** |
| Production numerical defect found | **NO** |
| Corrected-EOB authority defect found | **NO** |

**Reasons for supersession:** attribution-count inconsistency; incomplete 19a/19b downstream dependency
inventory; comparability wording qualification; final-81 aggregate-evidence clarification.

The r1 package remains on disk and is **not** rewritten. This checkpoint does not imply it never existed.

## 2. Corrected EOB production authority — UNAFFECTED

| Field | Value |
|---|---|
| Run ID | `20260917T082758521112Z_a4b6383308` |
| Status | **`CORRECTED_EOB_ACCEPTED_PRODUCTION_AUTHORITY`** |
| Result | `d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022` |
| Run manifest | `9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a` |
| Core | `v7.2-…-exact-d-preflight-2026-09-16-r10` · `9d828321…7e193da8` |
| Objective | 66,708,197.09463947 NTD-2023/year |

The STOP applied **only** to the additive delta-freeze package. The corrected EOB production authority
established by the independent post-run acceptance audit stands unchanged.

The corrected run manifest still reads `CORRECTED_EOB_CANDIDATE_PENDING_AUDIT` — correct and
deliberate. It records what the driver knew at serialization time; acceptance lives in additive
governance artifacts. The existing accepted-corrected-EOB checkpoint
(`corrected_eob_accepted_authority_v7_2_2026-09-17.md`, `e71401ec…`) is **not** rewritten to hide the
rejected delta package.

## 3. Execution counters

optimization calls = 0 · model creations = 0 · solve_eob calls = 0 · EOB runs = 0 · Layer A runs = 0 ·
sensitivity runs = 0 · 81-case runs = 0 · production code edits = 0 · historical artifact edits = 0 ·
corrected-run edits = 0 · downstream pin updates = 0 · commits = 0 · pushes = 0 · tags = 0

## 4. Next step

The r2 package must next receive a **fresh independent read-only audit**. Downstream current pins must
not be updated, and representative Layer A must not run, until that audit passes and a separate
current-authority update gate is authorized.
