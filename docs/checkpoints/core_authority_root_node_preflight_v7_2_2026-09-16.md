# Core Authority Alignment + Root-Node Tractability Preflight — 2026-09-16

**Gate:** POST-BASELINE GATE 5  
**Verdict:** CORE AUTHORITY + ROOT-NODE PREFLIGHT PASS — READY FOR INDEPENDENT AUDIT BEFORE EOB AUTHORIZATION  
**Tractability:** `TRACTABILITY_PASS`  
**Current authority:** `CORRECTED_CORE_AUTHORITY_ALIGNED_PRE_EOB`  
**Final corrected production authority:** NOT ESTABLISHED

The accepted Exact-D core was assigned the single successor identity `v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10`. Reversing only that string reproduces the accepted pre-alignment SHA-256 `f848282a33e3c3d243c4d1819f7d506f5cd460de43493031e54fafb3916e9233` exactly; the aligned core SHA-256 is `9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8`. Equations, coefficients, objective, domains, physical constraints, degradation, tariff, reserve, replay, and solver settings were not changed.

Historical `15b`, `EXPECTED_EOB_REFERENCE`, the historical EOB, final-81 artifacts, tags, Framework v7.2, Registry v7.2, and Gate 1–4 baseline artifacts remain byte-identical.

The full 8,760-hour corrected model built with 105,335 linear rows, 122,915 variables, 8,764 binaries, 122 MAX constraints and 307,138 nonzeros. With `NodeLimit=0`, ordinary presolve produced 109,176 rows, 139,263 columns and 26,409 binaries. The root relaxation completed in 9.80 seconds with best bound 66708137.56793594; no incumbent or warning occurred. A second optimize call was unnecessary.

## Evidence identities

- Authority manifest: `a37186a5e8dc8a26c887b0d52699d56df536ad635d6103ea41812fa44cce8bc4`
- Final validation report: `5c43ad664a190538d1039e57604d0f893d759e9396a70595e6a3fd9db0cd2da4`
- Annual structure: `b2a2afa178a748b51c1fbe7d825415afd46df2fa293299d69d2c29c6c5fd1bcb`
- Root diagnostic: `730534c43a480baf459608a8a02eb014122f8e7a255d8a02f87f400f35890153`
- Solver log: `446a90b43a36b8338ffd33c1c77bdc0aeb9383e336a637f70bcc882b5f3acabb`

Corrected EOB, Layer A, sensitivities, and final 81 cases were not run. No commit, push, tag, reset, clean, or rebase occurred. The required next step is an independent Gate-5 audit before any EOB authorization.
