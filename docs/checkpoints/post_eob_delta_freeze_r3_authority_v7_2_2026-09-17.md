# Post-EOB Delta-Freeze r3 — Authority Checkpoint

**Checkpoint date:** 2026-09-17 (Asia/Taipei) · **Captured:** 2026-09-17T21:48:35+08:00 / 2026-09-17T13:48:35Z
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`

> **Current candidate post-EOB delta-freeze package: r3**
> `results/provenance/post_eob_delta_freeze_v7_2_20260917_r3/`
> **Status: `CURRENT_CANDIDATE_POST_EOB_DELTA_FREEZE_PACKAGE_PENDING_CROSS_AGENT_AUDIT`**

Additive governance artifact. No production source, historical artifact, run manifest, downstream pin
or methodology document was modified.

---

## 1. Supersession chain

| Package | Status | Disposition |
|---|---|---|
| R1 | `REJECTED_BY_INDEPENDENT_AUDIT` | preserved immutable |
| R2 | `SUPERSEDED_BY_R3_FOR_DELTA_FREEZE_AUTHORITY` | preserved immutable |
| R3 | `CURRENT_CANDIDATE_..._PENDING_CROSS_AGENT_AUDIT` | current candidate |

**Reason R2 was superseded:** a non-material 17c dependency-enumeration inaccuracy found during
same-family self-review — R2 said 17c pins four historical EOB artifacts; the source contains five,
the omitted entry being `mainline_eob_rainflow` (`8660da9f…`).

**R2 was NOT rejected for numerical or production-result error.** The issue was package documentation /
dependency inventory only.

## 2. Corrected EOB production authority — UNAFFECTED

| Field | Value |
|---|---|
| Run ID | `20260917T082758521112Z_a4b6383308` |
| Status | **`CORRECTED_EOB_ACCEPTED_PRODUCTION_AUTHORITY`** |
| Result | `d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022` |
| Run manifest | `9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a` |
| Core | `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10` |
| Objective | 66,708,197.09463947 NTD-2023/year |

The corrected run manifest still reads `CORRECTED_EOB_CANDIDATE_PENDING_AUDIT` — correct and
deliberate. Neither the accepted-corrected-EOB checkpoint nor the R2 authority checkpoint was rewritten.

## 3. What R3 corrects

One thing only: the 17c historical-EOB dependency enumeration, now fully source-backed with all five
`mainline_eob_*` pins (key, path, SHA-256, authority role, definition line, consumption lines, live-pin
satisfaction), plus new evidence that 17c is partially refreshed — core/input/interface pins already
current, all five EOB comparator pins still historical.

No production number, delta, attribution class, comparability conclusion, 19a/19b finding, final-81
evidence or authority statement changed.

## 4. Execution counters

optimization calls = 0 · model creations = 0 · solve_eob calls = 0 · EOB runs = 0 · Layer A runs = 0 ·
sensitivity runs = 0 · 81-case runs = 0 · production code edits = 0 · downstream pin edits = 0 ·
historical edits = 0 · corrected-run edits = 0 · commits = 0 · pushes = 0 · tags = 0

## 5. Next step

R3 must receive a **genuine cross-agent Codex read-only audit** before the POST-EOB OLD-vs-NEW DELTA
FREEZE can become final CLOSED / PASS. This package has not been independently audited: it was produced
by the same model family that produced and self-reviewed R2. Downstream current pins must not be
updated, and representative Layer A must not run, until that audit passes and a separate
current-authority update gate is authorized.
