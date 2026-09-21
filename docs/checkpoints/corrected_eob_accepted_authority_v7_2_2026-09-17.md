# Corrected EOB — Accepted Production Authority

**Checkpoint date:** 2026-09-17 (Asia/Taipei) · **Captured:** 2026-09-17T19:50:51+08:00 / 2026-09-17T11:50:51Z
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`

> **Current corrected EOB authority: `20260917T082758521112Z_a4b6383308`**
> **Status: `CORRECTED_EOB_ACCEPTED_PRODUCTION_AUTHORITY`**

This is a **new additive governance artifact**. It records an acceptance decision made *after* the
production run was serialized. It modifies no production source, no historical artifact, no run
manifest and no methodology document.

---

## 1. Accepted authority

| Field | Value |
|---|---|
| Run ID | `20260917T082758521112Z_a4b6383308` |
| Run directory | `results/eob_production_corrected/runs/20260917T082758521112Z_a4b6383308/` |
| Result artifact | `corrected_eob_result.json` · `d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022` |
| Run manifest | `run_manifest.json` · `9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a` |
| `CORE_VERSION` | `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10` |
| Core SHA-256 | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Driver | `scripts/15d_run_corrected_eob_v7_2.py` · `90d19baac8c0b96e08de00b4769b7ae68dff745f71923b850433ffc2935091a8` |
| Canonical input | `data/processed/annual_input_v7_1.parquet` · `9142b8b6f81b3f423c4ab43ac049765b3e934aae57d33c761208f3452598518e` |
| Solver | Gurobi 13.0.1 · `OPTIMAL` (code 2) · MIP gap `8.923446611007768e-07` |
| Objective | **66,708,197.09463947 NTD-2023/year** |
| E_N / P_B / CC | **77.77777777777777 kWh** / **56.0 kW-AC** / **4,388.666231266645 kW** |

## 2. Why the run manifest is not edited

The manifest still reads `result_authority = CORRECTED_EOB_CANDIDATE_PENDING_AUDIT` and
`acceptance_status = NOT_AUDITED_DRIVER_DOES_NOT_ACCEPT_ITS_OWN_RESULT`.

**That is correct and must stay.** The manifest represents what the production driver knew at
serialization time — the driver cannot and must not accept its own result. The acceptance decision is
a later, independent governance act and therefore lives here and in the delta-freeze package, not by
retro-editing an immutable artifact.

## 3. Basis of acceptance

An independent read-only post-run audit verified: three-way identity of all 13 input/interface pins;
all 10 artifact hashes and a self-consistent manifest registry; solver `OPTIMAL` with gap ≤ 1e-6 and
non-default parameters exactly `MIPGap 1e-06` / `NumericFocus 1`; full objective reconciliation
(residual 2.31e-07 NTD); Exact-D reconstructed from stored dispatch to 4.55e-13 kW with zero epigraph
slack; W-07 per-increment semantics reproduced to 1.31e-08 NTD with the historical cumulative-pool
defect demonstrably absent; and a clean physical dispatch audit. The Gate-5 model fingerprint
`0xc595f3a0` and root bound `66708137.56793594` match this run exactly.

## 4. Relationship to historical production

The historical EOB (`results/eob_production/`, core **r1**) remains **immutable historical
provenance** and is now **superseded for current corrected authority**. It must never be rewritten,
relabelled, or presented as an r10 result. Both axes are preserved: it was historically accepted *and*
it is currently superseded.

## 5. What this authority does NOT establish

- It does **not** update Layer A, representative cases, sensitivity or the final-81 surface. Those
  remain under historical authority until separately re-executed and audited.
- It does **not** authorize editing `EXPECTED_EOB_REFERENCE`, `15b`, `15c`, historical artifacts or tags.
- It does **not** reopen A4, W-04, W-07 or Surface-1/Exact-D.

## 6. Legitimate downstream use

Future Layer-A / A2 / sensitivity / final-81 authority manifests may pin this run ID and the
identities in §1. Existing historical pins stay frozen; current/future references may be updated only
in a separately authorized implementation gate.
