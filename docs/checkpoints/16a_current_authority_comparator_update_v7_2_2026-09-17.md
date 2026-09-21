# Script 16a Current-Authority Comparator Update — Checkpoint

Captured UTC: `2026-09-17T15:00:44.015007Z`  
Branch: `thesis-v7`  
HEAD: `b03721275c73b05d45517bdf84c1e0bd03833376`

Status: **PASS_IMPLEMENTATION_PENDING_INDEPENDENT_AUDIT**

Script 16a now has an explicit corrected/current EOB authority loader pinned to run `20260917T082758521112Z_a4b6383308`, result `d7c37a0013ad6ea5a8dc3231a67bf427ec0c502aef96fedc47aacfe7c8897022`, immutable run manifest `9acb3f52948c63e65c29baf3f8a84653d127febf96369f1945cbb358389eb99a`, accepted corrected-EOB checkpoint `e71401ec3562b0803e52e3d054f8d7a69a1528fd197a03c6a7d42df629ab32a2`, and accepted R3 evidence.

Historical reproduction remains explicit through `historical_eob()` and the compatibility alias `canonical_eob()`. No historical artifact was rewritten. Corrected rainflow is not a comparator dependency.

## Identities

- prior Script 16a: `18af1d21150a4dd519cbee03a1033a34f680594b19f43bfd69f2e059490eaf05`
- updated Script 16a: `3f62fa290e1c8e1699c34d4b1bc78b9af0e716387b251afb4ada2b3198d7524f`
- new dedicated test: `122305822a7ae2336398846e54f87e0ef4459b3e363f19cb0b88756e9ee0ae0c`
- package hash manifest: `d7687b785f261c3320ed953c0740e412f8562d12eb1175a034a1d0191f244884`

## Validation

- real no-solve authority validation: PASS
- dedicated tests: 7/7 PASS
- existing static tests: 10/10 PASS
- optimization calls: 0
- model creations: 0
- solve_eob calls: 0
- Layer A runs: 0

17c, 19a, 19b, and `CURRENT_STATE.md` remain unchanged and deferred. Representative Layer A must not run until a separate independent auditor accepts this checkpoint.
