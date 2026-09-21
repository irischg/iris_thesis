# Corrected EOB Re-Authorization — v7.2

**Checkpoint date:** 2026-09-17 (Asia/Taipei)
**Gate:** Gate 6B — Corrected EOB Re-Authorization
**Branch:** `thesis-v7` · **HEAD:** `b03721275c73b05d45517bdf84c1e0bd03833376`
**Captured:** 2026-09-17T15:37:16+08:00 / 2026-09-17T07:37:16Z

> **Status: CORRECTED EOB RE-AUTHORIZATION PASS**
> **EXACTLY ONE corrected EOB production run is authorized. The run has NOT been executed.**

This is an additive provenance checkpoint. It modifies no production source, no test, no historical
artifact and no methodology document.

---

## 1. What this gate decided

Whether the driver created by Gate 6A closes the single Gate-6 blocker
(`EOB_EXECUTION_PATH_NOT_READY`), and whether one corrected EOB production run may now be authorized.

**Answer: yes, and yes.** 21 of 21 conditions PASS.

## 2. The blocker is closed

**`EOB_EXECUTION_PATH_READY`.**

Gate 6 withheld authorization because no repository script could run a corrected EOB under r10
additively: 15b was pinned to the historical r1 core and defaulted its output into the immutable
historical EOB directory, 15a had no core pin at all, and every other `solve_eob` caller belonged to a
different stage. `scripts/15d_run_corrected_eob_v7_2.py` closes exactly that gap without touching any
of them.

## 3. Authorized execution

| Field | Value |
|---|---|
| Driver | `scripts/15d_run_corrected_eob_v7_2.py` |
| Driver SHA-256 | `3a14ec166ca4162489a5a76d3e34efb2c59dbfb9c4c8a361e51836bdcf87dca2` |
| Command | `.venv/Scripts/python.exe -X utf8 -B scripts/15d_run_corrected_eob_v7_2.py --execute-production` |
| Authorized run count | **1** |
| `CORE_VERSION` | `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10` |
| Core SHA-256 | `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8` |
| Output namespace | `results/eob_production_corrected/runs/<UTC_TIMESTAMP>_<FINGERPRINT>/` |
| Initial result authority | `CORRECTED_EOB_CANDIDATE_PENDING_AUDIT` |

The authorization does **not** permit a second run, a retry with changed settings, Layer A,
sensitivities, the final 81, or any change to formulation, MIPGap, tolerances or historical authority.
**If the run fails, stop and audit it — do not rerun automatically.**

## 4. Why the driver is safe

Audited from source by AST, not from the Gate-6A narrative:

- **Zero** model-building primitives anywhere in the driver — the optimization formulation is not
  duplicated; it stays in the accepted core.
- **Exactly one** `solve_eob` call site (line 740) with `layer_a_requirements=None`; zero `optimize()`
  sites; zero loops or exception handlers around the solve, so no retry path exists.
- **20 identities hard-pinned**, every one aborting before any model import or solve. Zero missing pins.
- The CLI has two mutually-exclusive flags and **no** override for any path, hash, core, input, solver
  setting or output location.
- `_validate_loaded_inputs()` re-checks κ and the resolved source paths *after* loading, so a
  substitution inside the loader is caught too.
- The historical `results/eob_production` namespace is explicitly rejected, an existing run directory
  is refused, and there is no `--force` and no destructive call.
- The driver **cannot label its own result accepted** — the acceptance tokens are absent from the
  source entirely.

## 5. Solver policy, traced to primary evidence

The accepted historical production EOB's own Gurobi log records exactly two non-default parameters:

```
Non-default parameters:
MIPGap  1e-06
NumericFocus  1
```

The driver reproduces precisely that policy. **NodeLimit leakage: NO** — `SolveSettings` has no
node-limit field, the core never assigns one, and the driver makes zero `setParam` calls. Gate 5's
diagnostic log shows `NodeLimit 0` as a third non-default parameter, which means any leak would be
log-visible; its absence is checkable evidence rather than an assumption.

## 6. Verified protections

Core, Framework, Registry, 15b, 15c, `EXPECTED_EOB_REFERENCE`, the historical EOB, the historical
final-81 (2,196 files, one run directory) and all 7 tags are **byte-identical**. All Gate-1→6A
artifacts are unchanged; all 10 Gate-6A identities verified.

## 7. Authority ladder

```
CORRECTED_CORE_AUTHORITY_ALIGNED_PRE_EOB          <- current
        |  (ONE authorized run of 15d)
        v
CORRECTED_EOB_CANDIDATE_PENDING_AUDIT
        |  (independent post-solve audit, Gate 7)
        v
CORRECTED_EOB_ACCEPTED
        |  (separate downstream gates, none automatic)
        v
FINAL CORRECTED PRODUCTION AUTHORITY              <- NOT ESTABLISHED
```

**Gate 6B assigns no corrected-EOB result authority, because no corrected EOB exists yet.**

## 8. Next step

**READY FOR ONE CORRECTED EOB EXECUTION.** Gate 6B stops here without executing it.
