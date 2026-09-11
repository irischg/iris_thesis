# Current State — Living Implementation Status

> **SNAPSHOT STATUS: PRE-GOVERNANCE-COMMIT.** This file must be reconstructed from Git + latest audit
> evidence immediately after the governance/protocol files (`AGENTS.md`, `CLAUDE.md`,
> `docs/ai_handoff/*`, and `docs/protocols/iris_thesis_rigorous_audit_skill.md`) are committed, and
> before any production authorization is trusted. Everything below — including the F-01 finding and the
> "additional untracked files" note — reflects the working tree as observed before that commit. Do not
> assume F-01 is resolved, and do not assume it is still open, without independently re-checking current
> repository evidence.

**This file describes implementation status only. It does not, and must not, reopen or restate
methodology — see `PROJECT_HANDOFF.md` and the Framework itself for that.**
A stage below is marked complete only where a checkpoint/audit artifact supports it — never merely
because a script exists.

Last reconstructed: 2026-09-11, from repository inspection (git state, latest checkpoint/audit files,
Framework v7.2 status text). Re-derive this from the repository before trusting it if substantial time
has passed — see §7.

## 1. Source of truth

- **Methodology**: `docs/research_framework_v7_2_2026-08-24.md`
  (SHA-256 `bfe724a35dd019b9f29456a7a7b569e132aa63b399c21c82d2c69a9fd934c8d5` per its own provenance
  header and cross-referenced from the pre81 checkpoint).
- **Evidence**: `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md`
  (SHA-256 `8b72bd3f56226f0be6900f52779b1702daaa8bbf85f674040b336f9aae6e021e`).

## 2. Git state (at time of writing)

- Branch: `thesis-v7`
- HEAD: `f4bbdebfb37a44983462df7ffa3477536761c3a9` — "Freeze audited 19b r2 production authority
  mechanism" (2026-09-11 14:31:19 +08:00)
- `origin/thesis-v7` matches HEAD (verified inside the latest execution-authorization audit).
- Working tree before this governance bootstrap: clean except one untracked file,
  `docs/protocols/iris_thesis_rigorous_audit_skill.md`.
- **After this governance bootstrap pass**, five additional untracked files exist:
  `AGENTS.md`, `CLAUDE.md`, `docs/ai_handoff/PROJECT_HANDOFF.md`, `docs/ai_handoff/CURRENT_STATE.md`,
  `docs/ai_handoff/CROSS_AUDIT_PROTOCOL.md`. **This matters mechanically, not just stylistically** —
  see §5.

## 3. Latest verified checkpoint / audit chain

In order, most recent last:

1. `docs/checkpoints/production_checkpoint_manifest_v7_2_pre81_ready_2026-09-10.json` —
   `FROZEN_PRE81_READY`, tag `v7.2-pre81-ready` (commit `b2acdf2`).
2. `docs/checkpoints/final_81_production_runner_authority_v7_2_2026-09-10.json` —
   `v7.2-final81-runner-authority-1`, pins runner `scripts/19b_run_final_layer_a_81_cases.py`
   (version `v7.2-final-layer-a-81-production-runner-2026-09-10-r2`,
   SHA-256 `d206c81b691cccb8c81ef36cee2f9bd19a8a165d188115a69c202ac9d64a9b97`). Explicitly states:
   *"Source authority only... does not certify any optimi[zation]"* — i.e. this is an authorization
   mechanism, not a production result.
3. Independent re-audits of the runner: `results/layer_a/final_81_reaudit/r2_20260911_0443/`,
   `r2b_20260911/`, accepted completion at `r2c_20260911` (referenced by the execution-authorization
   gate below).
4. **Latest execution-authorization gate**:
   `results/layer_a/final_81_execution_authorization/20260911T065811Z/` —
   **verdict: `FAIL — 81-CASE PRODUCTION EXECUTION NOT AUTHORIZED`**. All authority identities, the
   grid (81 cases: α ∈ {0.60...1.00 step 0.05}, β ∈ {4...12 h}), inputs, environment, and scientific
   invariants PASS. Blocked solely by finding **F-01**.
   - No model was built, no `optimize()` call was made, no case directory was created
     (`real_model_creations=0`, `real_optimize_calls=0`, `production_cases_started=0`).

## 4. Latest completed implementation stage

- Scripts 01 through 13c: **CLOSED / PASS** (preprocessing, canonical annual input, billing/kappa
  calibration, PNNL cost dual-bracket construction, Xu degradation semantics audit, Taipower tariff
  registry + bill-component regression).
- Scripts 14a/14b (production economic interface, transition-settlement interface), the EOB
  formulation benchmark/production baseline (`results/eob_production/`), rainflow validation, 16a
  representative-case preflight, and the 17a–17c winter-PV long-block sensitivity protocol: **built and
  audited**, frozen into checkpoints.
- Script 18a/18b (production-environment and checkpoint validation): **PASS**.
- Script 19a (final-81 preflight, build-only): **accepted**.
- Script 19b (final-81 production runner): **frozen and authority-pinned, but execution is NOT
  authorized** — see F-01 below. **No Layer A 81-case result exists yet.**
  `results/layer_a/final_81` (the actual production output namespace) does not exist.

## 5. Open blocker — F-01 (do not silently resolve)

**Finding**: `scripts/19b_run_final_layer_a_81_cases.py`'s `repository_authority()` (around line
287–324) hard-fails production execution unless the *entire* set of untracked files in the working
tree is a subset of a fixed allowlist, currently
`allowed_untracked = {"docs/protocols/iris_thesis_rigorous_audit_skill.md"}` (line 304), and it also
hashes a fixed `protected_identities` dict that already includes that same protocol file by exact path
(line 315–316). The latest execution-authorization audit
(`results/layer_a/final_81_execution_authorization/20260911T065811Z/README.md`) concluded this makes
the untracked protocol file a **reachable authority dependency**, not merely an unrelated stray file,
and FAILED the gate on that basis (Moderate, blocking).

**Consequence of this governance bootstrap**: the five new files created by this pass
(`AGENTS.md`, `CLAUDE.md`, `docs/ai_handoff/*.md`) are also untracked and are **not** in
`allowed_untracked`. Until this is resolved, `repository_authority()` will fail with
`"Unapproved untracked files"` for **six** files, not one — a strict superset of the pre-existing
blocker, same class of issue.

**Resolution requires a decision this bootstrap pass is not authorized to make** (it must not touch
`scripts/19b_run_final_layer_a_81_cases.py`, the authority manifest, or commit anything). Options for
whoever performs the next authorized correction:
- Commit the governance files (and decide whether the protocol file should also be committed) so they
  no longer appear as untracked, then re-run the independent authorization audit; or
- Extend `allowed_untracked` / the relevant protected-identity handling in a separately authorized,
  audited change to the runner and its authority manifest (this itself requires a new frozen checkpoint
  and re-audit, per the runner's own non-self-reference rule).

**Do not** work around this by deleting the untracked files, by adding `--no-verify`-style bypasses, or
by hand-editing the authority manifest outside the runner's own audited process.

## 6. Unresolved IMPLEMENTATION / VALIDATION items (not methodology)

- 81-case Layer A production run: **not executed** (blocked by F-01, §5).
- Post-solve exact demand maxima, ex-post rainflow/cycle-depth validation against a real Layer A
  solve, winter-PV long-block economic sensitivity beyond the holdout-validation stage: all depend on
  the 81-case run and are therefore also pending.
- Layer B benchmark-design count (3/5/9) and coordinates: explicitly deferred until after Layer A
  (Framework §0.2) — do not decide this from implementation convenience.
- DG extension CAPEX/FOM/fuel/emission parameter audit: not started; may proceed in parallel with
  Layer A per Framework §0.3, but has not been started as of this writing.

## 7. Next intended gate, if repository evidence supports it

The next gate is **resolving F-01 and obtaining a PASS execution-authorization verdict**, then running
the actual 81-case Layer A production solve via the exact frozen command identified (for review only,
not authorized by that gate):

```powershell
.venv\Scripts\python.exe -X utf8 -B scripts\19b_run_final_layer_a_81_cases.py --execute-production
```

Do not advance past this gate, and do not treat a future PASS on a *different* execution-authorization
audit directory as current without re-reading it — timestamps under
`results/layer_a/final_81_execution_authorization/` are not monotonically trustworthy at a glance; open
the directory, check its `decision.json`/`README.md`, and confirm its stated HEAD matches current
`git rev-parse HEAD` before relying on it.
