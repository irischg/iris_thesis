# Corrected EOB Authorization — v7.2

**Checkpoint date:** 2026-09-17 (Asia/Taipei)
**Gate:** Gate 6 — Corrected EOB Authorization Gate
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`
**Captured:** 2026-09-17T14:22:39+08:00 / 2026-09-17T06:22:39Z

> **Status: CORRECTED EOB AUTHORIZATION STOP — EOB EXECUTION NOT AUTHORIZED**
> `authorization_status = CORRECTED_EOB_NOT_AUTHORIZED`

This is an additive provenance checkpoint. It modifies no production source, no historical artifact
and no methodology document. It authorizes nothing.

---

## 1. What this gate asked

Whether **one** corrected production EOB run may be authorized under the aligned corrected core, and
under what frozen execution, acceptance and comparison contracts. The gate was explicitly forbidden
from running the EOB.

## 2. Answer

**Authorization is withheld.** 18 of 21 pass conditions PASS, 1 FAILS, 2 are NOT_ESTABLISHED.

The blocker is narrow and worth stating precisely, because it is easy to misread as something worse
than it is:

> **No safe corrected-EOB execution path exists in the repository.**

This is a **missing implementation**, not a provenance defect, not a broken guard, not an integrity
failure, and not a tractability problem. Everything that *was* built and verified is sound.

## 3. State of the corrected core

| Field | Value |
|---|---|
| `CORE_VERSION` | `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10` |
| core SHA-256 | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| authority | `CORRECTED_CORE_AUTHORITY_ALIGNED_PRE_EOB` |
| final corrected production authority | **NOT ESTABLISHED** |

Gate 5's contribution to the core was proved — not accepted on report — to be **exactly one metadata
line**: reverting the single `CORE_VERSION` line to the r9 string reproduces the Gate-4-accepted
Exact-D core hash `f848282a…` with a byte delta of zero.

## 4. Why no path exists

`scripts/15b_freeze_production_eob_baseline.py` is the historical EOB freeze mechanism and the only
unconstrained-EOB production path. It is disqualified twice:

1. Its `EXPECTED_CORE_VERSION` is pinned to the historical **r1** core, so under r10 it raises
   `RuntimeError` before any solve. **This is the provenance guard working correctly.** It is signal,
   not an obstacle, and must not be edited around.
2. Its default `--output-dir` is `results/eob_production` — the historical immutable EOB location.
   Running it there would overwrite the frozen production result and its freeze audit.

`15a` is an ungated formulation benchmark with no core pin at all. `16a`, `17c`, `19a` and `19b`
belong to other stages and never solve an unconstrained EOB.

The model-level callable `solve_eob(..., layer_a_requirements=None)` is correct under r10. What is
missing is a **production driver** around it.

## 5. What a future implementation gate must deliver

A new, separately authorized execution path that:

- pins `CORE_VERSION` r10 and core SHA `9d828321…`, and aborts on drift;
- pins the corrected canonical input `9142b8b6…` and the Gate-C refreshed settlement interface
  `f101af47…` and matrix `ed7f8dbf…`;
- leaves `15b`, `15c`, `EXPECTED_EOB_REFERENCE` and every historical artifact untouched;
- writes to a **new additive run directory**, never to `results/eob_production/`;
- records the full provenance and acceptance evidence frozen in this gate;
- uses production solver settings only — `MIPGap = 1e-6`, **no** `NodeLimit`, no time cap, no tuning.

## 6. Verified protections

- Historical EOB `ad606a50…` and freeze audit `18bf9341…` — **unchanged**.
- Historical final-81 — **unchanged** (2,196 files, aggregate `d990fe31…`, one run directory).
- `15b` `9a5f61d1…` and `15c` `14fd9f33…` (host of `EXPECTED_EOB_REFERENCE`) — **unchanged**.
- All 7 tags — **unchanged**; `v7.2-final81-runner-ready-r3` still peels to HEAD.
- Framework `bfe724a3…` and Registry `8b72bd3f…` — **unchanged**.
- All 30 Gate-1→4 baseline artifacts and all 10 Gate-5 artifacts — **unchanged**.

## 7. Production solver state

`NodeLimit = 0` **cannot** reach production. The decisive fact is structural rather than procedural:
`SolveSettings` has **no node-limit field**, so no caller can pass one. The core never assigns
`NodeLimit`; the single repository occurrence of that token is a Gurobi status-code label. No
`gurobi.env` or `*.prm` exists, no `GRB_*` override is set, and no Gate-5 driver script was left in
the repository. No production solver setting was altered by Gate 5.

## 8. Authority ladder (frozen)

```
CORRECTED_CORE_AUTHORITY_ALIGNED_PRE_EOB          <- current
        |  (Gate 7 solve, if separately authorized)
        v
CORRECTED_EOB_CANDIDATE_PENDING_AUDIT
        |  (independent post-solve audit)
        v
CORRECTED_EOB_ACCEPTED
        |  (separate downstream gates, none automatic)
        v
FINAL CORRECTED PRODUCTION AUTHORITY              <- NOT ESTABLISHED
```

Layer A, representative cases, sensitivities and the final 81 remain separate downstream stages. No
corrected EOB result, once accepted, automatically updates any of them, and historical production tags
are never retargeted.

## 9. Next step

**NOT READY FOR CORRECTED EOB EXECUTION.** A separate implementation gate must first create the
execution path described in §5. Gate 6 was forbidden from creating one, and did not.
