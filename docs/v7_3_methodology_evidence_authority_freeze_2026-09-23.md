# V7.3 Methodology / Evidence Authority Freeze

**Project:** Iris Thesis  
**Freeze date:** 2026-09-23  
**Purpose:** Additive authority checkpoint after Framework v7.3 acceptance, Registry v7.3 R3 acceptance, successor-lineage merge audits, and Framework–Registry cross-alignment audit.

## A. Freeze verdict

> **V7.3 METHODOLOGY / EVIDENCE CONTENT FREEZE — CLOSED / ACCEPTED**

This freeze records the current accepted methodology and evidence authorities. It does **not** rewrite either accepted primary artifact.

Separate status:

- **Content / authority freeze:** `CLOSED / ACCEPTED`
- **Repository branch / HEAD / staged-state verification:** `PENDING EXTERNAL REPO CHECK`
- **Commit / push / tag freeze:** `NOT_YET_AUTHORIZED BY THIS DOCUMENT`
- **Canonical reconstructed-mainline annual input:** `NOT_YET_CREATED / NOT_YET_AUTHORIZED`
- **Production routing:** `NOT_YET_AUTHORIZED`
- **Final81:** `NOT AUTHORIZED`

The repository-state and commit/tag items are intentionally separated from the scientific/content freeze because this document was generated from the accepted primary bytes and audit package available in the project environment, not from a live local Git working tree.

## B. Current accepted authority state

### Methodology source of truth

`research_framework_v7_3_2026-09-23.md`

SHA-256:

`44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a`

Status:

**CLOSED / ACCEPTED**

### Evidence source of truth

`thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`

SHA-256:

`e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`

Status:

**CLOSED / ACCEPTED**

### Explicit current-authority rule

From this freeze onward:

> **Current methodology source of truth = Framework v7.3.**  
> **Current evidence source of truth = Registry v7.3 R3.**

Framework v7.2 and Registry v7.2 remain historical accepted predecessors only. Registry v7.3 R1 and R2 remain failed immutable provenance only and must not be used as current authority.

No earlier framework, registry, failed candidate, handoff, or historical run may override the two current accepted authorities above unless a later independently accepted successor explicitly supersedes them.

## C. Historical predecessor identities

| Artifact | Role | SHA-256 |
|---|---|---|
| `research_framework_v7_2_2026-08-24.md` | Historical accepted methodology predecessor | `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` |
| `thesis_literature_evidence_registry_v7_2_2026-08-24.md` | Historical accepted evidence predecessor | `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e` |

Historical Registry v7.3 failed-candidate identities retained by the accepted R3 lineage:

| Artifact | Status | SHA-256 |
|---|---|---|
| Registry v7.3 R1 | FAILED / STOP — immutable provenance | `e06f5a1e30ffd7af0c3a8405e6758c25f82d18eb7756bb05da276dffe609db1e` |
| R1 checkpoint | FAILED / STOP — immutable provenance | `301b931a3b7ea4b0c981079789e66a69e5571294a0d29467bd0c6c262c17fe2d` |
| Registry v7.3 R2 | FAILED / STOP — immutable provenance | `460c30fefb70d64d614d02039205dde0fbe2e45c20462a9f19c256f392716b0c` |
| R2 checkpoint | FAILED / STOP — immutable provenance | `5b9f063709b680f8099d72ee440d9be6be02687e82476267903f95be8f416917` |
| Registry v7.3 R3 candidate checkpoint | Accepted-candidate provenance; do not rewrite | `17112066c12ef2de1eaeaf278913d3652710b9b9bf3694bed34b289ceff82ae9` |

R1 and R2 must not be deleted, overwritten, renamed into the current authority namespace, or cited as current evidence authority.

## D. Audit package incorporated into this freeze

The following additive audit records are part of the v7.3 freeze package:

| Audit artifact | Verdict | SHA-256 |
|---|---|---|
| `framework_v7_3_merge_audit_2026-09-23.md` | PASS / CLOSED | `7f4bf71cc505e0aa989755ae48a4aef8be9b4bc6bf2fa148070043f29eba1643` |
| `registry_v7_3_r3_merge_audit_2026-09-23.md` | PASS / CLOSED | `1b2298e7f172ef88317e354de0e4426eb3fc866f10b33be232ec640c114a6ed4` |
| `framework_registry_v7_3_cross_alignment_audit_2026-09-23.md` | PASS / CLOSED | `1d9f86683bc11096a7b6ee58fc1dafe57acd145d3d3e6a196955b0eaf3ac1d17` |

These audits establish, at the document/content level:

1. Framework v7.3 is a valid additive successor to Framework v7.2 with no unrelated methodology drift identified.
2. Registry v7.3 R3 is a valid additive successor to Registry v7.2 with no unrelated evidence-role drift identified.
3. Framework v7.3 and Registry v7.3 R3 are mutually aligned on the acceptance-critical methodology/evidence boundaries reviewed.

This freeze does not silently convert those document audits into a claim about the current local Git working tree. Repository identity remains a separate verification item.

## E. Frozen reconstructed-PV methodology / evidence role

The following is now frozen unless a primary code, data, formula, source-transcription, or provenance error is demonstrated:

1. The prolonged unavailable winter-PV block is represented by a separately validated, weather-informed reconstruction as the **best-estimate planning mainline**.
2. The prior zero-winter treatment is retained as a **conservative stress / sensitivity**.
3. Reconstructed values are model-based planning estimates, **not observed meter data, not exact ground truth, and not exact historical recovery**.
4. The same reconstructed full-year planning-baseline PV identity must feed:
   - EOB / annual economic optimization;
   - Layer A residual-load construction;
   - `R(alpha,beta)`;
   - `P_out(alpha)`;
   - binding-window classification;
   - exhaustive outage replay;
   - baseline Layer B.
5. A hybrid route that gives reconstructed-PV credit to economics while reverting Layer A or baseline Layer B to zero-winter PV is unauthorized.
6. Historical billing calibration remains based on observed Load/PV and actual billing records; reconstructed planning PV does not re-estimate `kappa`.
7. Layer A analytical-consistency replay retains its no-outage-PV-surplus-recharge rule.
8. Layer B may retain its existing event-replay surplus-recharge semantics; that stage distinction does not authorize a different baseline PV artifact identity.

## F. Frozen non-PV methodology

The following previously CLOSED decisions remain CLOSED and are not reopened by v7.3:

- stationary LFP mainline;
- mainline SOC = 10–90%;
- 20–80% = deliberately more restrictive technical sensitivity;
- `eta_c = eta_d = 0.90`;
- battery-side stored-energy state; AC/PCS-side charge/discharge power;
- constant worst-case reserve floor in annual normal operation;
- separate outage replay that may consume reserve down to technical SOCmin;
- non-circular valid outage-start set;
- frozen Layer A reserve / power definitions;
- annual regular contract capacity as the mainline decision variable; supplementary contracts fixed at NTUST case values;
- exact reported demand maxima recomputed ex post from optimized grid profiles;
- Taipower tariff / over-contract semantics already closed in the accepted framework;
- 10 MW-scale PNNL full economic package = ex-ante mainline;
- 1 MW-scale full package = cost-scale sensitivity;
- no optimized-`P_B`-dependent cost-package switching;
- optimization monetary basis = constant NTD-2023;
- 5% = real modeling discount-rate assumption;
- PNNL-calibrated adaptation of Xu et al.'s intertemporal convex PWL DOD-sensitive cycle-aging formulation;
- rainflow = ex-post validation / benchmark only;
- B2 total-cost structure = annualized CAPEX + annual FOM + operating costs including cycling wear;
- Layer B = fixed-design structured capability test, not reliability probability;
- DG extension = deterministic counterfactual extension, not outage-probability model.

## G. Evidence-role boundaries frozen

The accepted Registry v7.3 R3 keeps the following evidence roles fixed:

| Evidence | Frozen role |
|---|---|
| Step 17a | historical `PASS_FOR_SENSITIVITY`; separate long-block/monthly holdout validation |
| Original Step 17b | historical sensitivity-only artifact |
| Corrected Sep-18 Step 17b | corrected promotion-source candidate; not canonical |
| Step 17c | paired reconstructed-vs-zero-winter sensitivity / adjudication evidence |
| Prior EOB / Layer A / continuation / rainflow outputs | historical, diagnostic, sensitivity, candidate, or predecessor evidence according to original manifests |

No item above is silently reclassified as accepted final v7.3 production evidence.

## H. Current production / implementation status at freeze

The content freeze must not be confused with production completion.

| Layer | Frozen status |
|---|---|
| Framework v7.3 | CLOSED / ACCEPTED |
| Registry v7.3 R3 | CLOSED / ACCEPTED |
| Framework merge audit | PASS / CLOSED |
| Registry merge audit | PASS / CLOSED |
| Framework–Registry alignment audit | PASS / CLOSED |
| Corrected Sep-18 promotion-source artifact | promotion-source candidate; not canonical |
| New canonical reconstructed-mainline annual input | NOT_YET_CREATED / NOT_YET_AUTHORIZED |
| Same-artifact production routing | NOT_YET_AUTHORIZED |
| Step 17c EOB | promotion/adjudication candidate evidence only |
| Representative cases | NOT CLOSED UNDER V7.3 |
| Steps 11A / 11B / 11C | NOT CLOSED UNDER V7.3 |
| Final 81-point production | NOT AUTHORIZED |

## I. Reopen rule

Do **not** reopen the frozen Framework v7.3 / Registry v7.3 R3 methodology-evidence pair merely because:

- a later agent prefers a different modeling choice;
- an older framework/registry used another choice;
- a historical artifact has a different label;
- a sensitivity result differs from the mainline;
- a new prose summary describes the project differently.

Reopening requires a demonstrated acceptance-relevant issue in primary evidence, such as:

- code defect;
- data defect;
- formula defect;
- source-transcription error;
- provenance / identity error;
- newly established primary evidence that invalidates a frozen assumption.

Any future substantive change must use an additive successor; do not silently mutate the accepted Framework v7.3 or Registry v7.3 R3 bytes.

## J. Repository / Git verification still required before implementation promotion

This freeze document was generated from project-visible primary bytes and audit files. It does **not** claim live verification of:

- active Git branch;
- current local `HEAD`;
- `origin` synchronization;
- staged files;
- unstaged tracked modifications;
- untracked files;
- existing or proposed tag identities;
- whether the three audit files and this freeze file have been committed.

Before using this freeze as the durable repository checkpoint for Step 2D, a read-only repository-provenance check must confirm the live repository state and then separately authorize the additive commit / push / tag action if desired.

No tag retargeting and no rewriting of failed candidates is permitted.

## K. Next authorized implementation gate

After repository/provenance verification closes, the next implementation step is:

> **Step 2D — construct a NEW canonical reconstructed-PV mainline annual artifact from the corrected Sep-18 promotion-source candidate, with truthful v7.3 mainline provenance, then independently audit that canonical artifact before authorizing production routing.**

Step 2D must **not**:

- rename the corrected v7.2 sensitivity artifact into canonical;
- mutate the historical promotion-source artifact in place;
- run EOB, representative cases, Steps 11A/B/C, or final81 merely as part of artifact construction;
- authorize same-artifact routing without a separate canonical-artifact audit.

## L. Freeze conclusion

> **CURRENT METHODOLOGY AUTHORITY = Framework v7.3**  
> `research_framework_v7_3_2026-09-23.md`  
> SHA-256 `44e313e71ea2a01e213454b4d838a86ec674fcda4f95a3b194ed68a92115ef2a`

> **CURRENT EVIDENCE AUTHORITY = Registry v7.3 R3**  
> `thesis_literature_evidence_registry_v7_3_2026-09-23_r3.md`  
> SHA-256 `e81efc8ac6ec76846838adc33bd8015e65108bba0ffd6c06052409fdcfd1009d`

> **V7.3 METHODOLOGY / EVIDENCE CONTENT FREEZE = CLOSED / ACCEPTED**

Repository checkpoint / commit / tag closure remains a separate, explicitly pending provenance action.

---

**Freeze-artifact self-hash:** record externally after generation and, if committed, record the repository path / commit identity in the repository-provenance closure artifact.  
