# 1 MW BESS cost-scale sensitivity implementation candidate — 2026-09-19

## Scope and status

This is additive implementation evidence for the no-solve hardening gate. It is
not execution authorization and does not accept any sensitivity result. The six
1 MW cases remain unexecuted and require a separate independent no-solve audit
before authorization.

## Added implementation

- `scripts/17d_run_bess_cost_scale_sensitivity.py`
  - SHA-256: `9899bc0e2a24bbf6d01d8b2c5dd976142975eb48c7f05933a46b43477eabdb55`
  - Default mode is read-only authority validation.
  - Future execution requires the explicit `--execute-production` flag.
  - The runner uses a copy-style `dataclasses.replace` adapter and does not
    modify the corrected annual core.
- `tests/test_17d_bess_cost_scale_sensitivity_v7_2.py`
  - SHA-256: `9ad271ce225ba88ecba8ca14e64833b6641d4060015225c9495669ea7dec5c93`
  - Covers package routing/atomicity, lambda lineage, legacy rejection,
    fair-comparison pins, allow-list/comparators, default zero-solve behavior,
    execution gating, artifact contract, and core immutability.

## Frozen authority

- corrected core r10 SHA-256 before/after:
  `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8`
- framework SHA-256:
  `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5`
- evidence registry SHA-256:
  `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e`
- 1 MW package-object SHA-256:
  `38432cb791dccc95c4c178def34bb0fb97651802953338adb0397cb883fafac7`
- 10 MW mainline package-object SHA-256:
  `b8c461eb3513a2f6f05739a824d124e797aa7f59d12b1cf28b066bc391bcd5e2`

## Verification record

- `python -B -m unittest -v tests.test_17d_bess_cost_scale_sensitivity_v7_2`
  — 16 passed, 0 failed.
- `python -B -m unittest -v tests.test_16a_current_eob_authority_v7_2 tests.test_17c_corrected_authority_alignment_v7_2 tests.test_transition_candidate1_static_v7_2`
  — 20 passed, 0 failed.
- Default 17d validation mode — PASS, read-only, zero model constructions,
  zero `solve_eob` calls, and zero optimization calls.
- Optional build-only verification was not performed.
- Actual optimization-call count for this gate: **0**.

## Repository boundary

- branch: `thesis-v7`
- HEAD and `origin/thesis-v7`:
  `b03721275c73b05d45517bdf84c1e0bd03833376`
- staged files: none
- gate-local additions: this checkpoint, the 17d runner, and its focused test
- pre-existing tracked modifications and untracked files were preserved
- no accepted or historical result artifact was modified

## Decision boundary

Candidate implementation only. Do not execute the six sensitivity cases.
