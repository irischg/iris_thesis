# v7.2 Framework Merge / Supersession Audit — 2026-08-25

## 1. Audit purpose

This audit records the controlled transition from Research Framework v7.1 to v7.2. It is a provenance and supersession document, not a new research specification. The current methodology is controlled by the v7.2 framework itself.

The audit was performed on 2026-08-25 against the final local artifacts listed below.

## 2. Integration provenance

### Base framework

- File: `research_framework_v7_1_2026-08-16.md`
- Role: previous authoritative framework / merge base
- SHA-256: `5baf78dc6b2ee7c60159d095029d9a15b114e9e8385e53d6376fd7269db06624`

### Integrated successor

- File: `research_framework_v7_2_2026-08-24.md`
- Role: post-audit economic-integration / production-interface framework; current framework source of truth
- SHA-256: `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5`

### Companion evidence artifact

- File: `thesis_literature_evidence_registry_v7_2_2026-08-24.md`
- Role: v7.2 evidence / claim mapping
- SHA-256: `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e`

### Cross-file alignment audit

- File: `v7_2_framework_registry_alignment_audit_2026-08-24.md`
- Role: verifies v7.2 Framework ↔ Registry alignment after both updates
- SHA-256: `0035514813799df8baa46bf912a73c76f946ccdadd87ce88014c92fd79a7517d`

## 3. Merge strategy

v7.2 was built from the complete v7.1 framework and updated incrementally. It was not reconstructed from v7, the preprocessing amendment, or older framework fragments.

No numbered top-level section from v7.1 was removed. A new §34 was added as the v7.2 economic-integration traceability snapshot.

The following v7.1 top-level sections are text-identical in v7.2:

- §1 — thesis positioning
- §2 — research questions
- §3 — research boundary and core definitions
- §5 — variables and units
- §6 — EOB definition
- §8 — Layer A experimental design and outputs
- §9 — Layer B benchmark design selection
- §10 — Layer B fixed-design stress test
- §11 — site-feasibility implementation boundary
- §12 — DG dual-track boundary
- §13 — DG external coverage sweep
- §14 — DG cost / emissions accounting
- §15 — DG result presentation
- §17 — computation planning
- §20 — thesis chapter structure
- §21 — safe contribution framing
- §22 — limitations
- §23 — literature-anchor section
- §24 — decision logic
- §29 — campus-facility information list

This confirms that v7.2 does **not** reopen or redesign the research questions, dense Layer A surface, fixed-design Layer B logic, DG boundary, site-feasibility boundary, or the previously closed A1–A4 / B1–B2 methodological structure.

## 4. Sections changed in v7.2

The actual diff shows changes in the preamble and the following top-level sections:

- §0 — implementation status and locked economic decisions
- §4 — tariff / billing / BESS cost / monetary-basis parameterization
- §7 — Layer A objective accounting basis
- §16 — targeted sensitivity and cost-scale governance
- §18 — validation / sanity-check wording
- §19 — legacy-result handling wording
- §25 — next execution order
- §26 — one-page oral-defense positioning
- §27 — coverage-audit status synchronization
- §28 — legacy parameter/result register wording
- §30 — literature / parameter verification tracking
- §31 — outputs, tasks, and critical path
- §32 — final coverage gate
- §33 — preprocessing traceability status synchronization
- §34 — **new** v7.2 economic integration freeze / traceability snapshot

These changes are dominated by post-v7.1 implementation status, economic-parameter governance, tariff/accounting traceability, and explicit supersession rules.

## 5. Major substantive supersessions

### 5.1 Gate 1 — PNNL cost-scale selection

**v7.1 rule superseded:**

> mainline coefficient choice depends on preliminary optimized `P^B` range and the parameter registry.

This rule is explicitly retired because the cost package affects optimized BESS power, making outcome-dependent bracket selection circular.

**v7.2 frozen rule:**

- PNNL **10 MW-scale full package = ex-ante mainline**.
- PNNL **1 MW-scale full package = higher-cost / reduced-scale-economy sensitivity**.
- Package role is fixed **before** EOB / Layer A optimization.
- Preliminary or final optimized `P^B` must never select or re-select the cost package.
- The 1 MW / 10 MW labels are **cost-scale source cases**, not BESS power bounds.
- A sensitivity switch must replace the complete bracket-specific economic package:
  - `C_E`
  - `C_P`
  - FOM
  - `C_rep`
  - derived `lambda_k`
- Cross-bracket mixing is prohibited.
- No unsupported 5 MW or continuous interpolation rule is introduced.

### 5.2 Gate 2 — monetary-basis harmonization

**v7.1 ambiguity superseded:** equipment costs on a 2023 price basis and case-year 2024/2025 nominal tariff values must not be added directly without monetary-vintage harmonization.

**v7.2 frozen rule:**

- All optimization-facing monetary terms use **constant NTD-2023**.
- PNNL 2023 USD values are converted to NTD-2023 with **FX = 31.150 NTD/USD**.
- PNNL 2023 cost vintage is not additionally inflated before entering the constant-2023 objective.
- Raw Taipower case-year tariffs / bills remain in original nominal NTD for institutional validation and bill regression.
- A separate, traceable optimization tariff layer must convert the official nominal tariffs to constant NTD-2023.
- `r = 5%` is explicitly a **real modeling discount rate**; `n = 20 yr`; `CRF = 0.0802426` remains code-derived.
- The 5% value is not claimed to be NTUST WACC.
- 2025 nominal-equivalent values, if later reported, are supplementary reporting only and do not feed back into optimization.

## 6. Post-v7.1 implementation / empirical status incorporated

v7.2 synchronizes the framework with project work completed after v7.1, including:

- Script 06 annual-input integration completed / passed.
- Billing-demand calibration / `kappa` scripted reproduction closed.
- Scripts 11f / 11g / 11h completed dual-bracket PNNL cost/FOM/`C_rep`/`lambda_k` package construction.
- Cost fitting uses the exact PNNL 4/6/8/10 h window.
- `C_rep` uses the bracket-specific DC Storage Block arithmetic mean across 4/6/8/10 h.
- Script 12a completed the production-oriented Xu intertemporal segment-state semantics audit.
- Script 13b Taipower tariff-registry production gate = CLOSED / PASS.
- Script 13c pure-season monthly bill-component regression = CLOSED / PASS.

These status updates close implementation/provenance items without reopening A1–A4 or B1–B2.

## 7. Tariff / accounting traceability additions

v7.2 explicitly records the following case-specific guardrails:

- `SCHOOL/FROZEN high-voltage` is an NTUST **project institutional-treatment label**, not a universal official Taipower category name.
- Non-summer peak is **N/A / not applicable**, not a zero-rate peak period.
- May/October 50/50 basic-charge transition remains a **case-validated empirical transition rule**; it is not generalized as a universal official rule without direct official text.
- No separate subsidy credit/debit is added when the relevant policy support is already embedded in the effective tariff / bill; duplicate subsidy accounting is prohibited.
- Raw nominal tariff evidence is preserved separately from the normalized optimization tariff layer.

## 8. Parameter-package freeze incorporated

v7.2 records as locked / populated where appropriate:

- 10 MW mainline package and 1 MW sensitivity package roles.
- Bracket-specific `C_E`, `C_P`, FOM, `C_rep`, and `lambda_k`.
- PNNL 4/6/8/10 h fitting window.
- FX = 31.150 NTD/USD.
- Constant NTD-2023 BESS monetary basis.
- Real 5% discount-rate interpretation.
- `n = 20 yr` and `CRF = 0.0802426`.

The underlying numerical derivations remain controlled by project artifacts / parameter registry rather than by narrative text alone.

## 9. Items deliberately still pending after v7.2 freeze

The following are **not** methodological blockers and remain downstream implementation / validation / sensitivity work:

- Script 14a production-interface preflight.
- Machine-readable official nominal Taipower tariff → constant NTD-2023 conversion with explicit deflator / price-index provenance.
- EOB production run.
- Final 81-point Layer A production run.
- Post-solve exact demand-max diagnostics.
- Rainflow ex-post degradation validation.
- Long-block winter-PV alternative reconstruction sensitivity.
- Layer B benchmark-design selection after Layer A results.
- DG parameterization / extension work.

Gate 1 and Gate 2 are not reopened by these pending tasks.

## 10. Supersession / source-of-truth status

Effective with v7.2:

- `research_framework_v7_2_2026-08-24.md` is the current framework source of truth.
- `research_framework_v7_1_2026-08-16.md` remains archived for provenance, regression, and historical comparison.
- Earlier framework versions and amendments must not be used to override v7.2 current methodology or to refill unresolved production values unless v7.2 explicitly classifies them as legacy / replication / regression / provenance material.
- The retained quotation of the old preliminary-`P^B` bracket rule in §34 is historical supersession evidence only; it is not an active rule.

## 11. Audit conclusion

**PASS — controlled incremental merge with explicit supersession.**

The v7.1 → v7.2 transition is traceable and bounded. The substantive methodological changes are limited to the two post-v7.1 economic-integration gates and their required accounting / traceability consequences. Core research questions, Layer A/B/DG architecture, technical BESS semantics, and previously closed methodological choices are preserved.
