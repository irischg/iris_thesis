# CLAUDE.md — Governance for Claude Code

This is a master's thesis research repository (campus PV–BESS service-continuity
planning, NTUST demonstration case), not a generic software project.
**Methodological validity and academic defensibility outrank speed or code elegance.**

## Read first, in order

1. `configs/current_mainline_pointer.json` — **canonical routing index** (Pointer R3, schema v2). Verify it
   with `python -B src/current_mainline_pointer_v2.py canonical`; only `CANONICAL_POINTER_VERIFIED` routes
   authority. Activation acceptance: `results/provenance/current_mainline_pointer_acceptance_r3/acceptance_closure.json`.
2. `docs/v8_gate3_accepted_package_2026-10-24/Iris_Thesis_Research_Framework_v8_Candidate_R2_2026-10-24_DRAFT.md`
   — **current methodology source of truth (Framework v8)**, Gate 3 accepted, activated 2026-10-24
3. **Registry v8** = `docs/thesis_literature_evidence_registry_v7_4_2026-09-26.md` (unchanged base) **plus**
   `docs/v8_gate3_accepted_package_2026-10-24/Iris_Thesis_Literature_Evidence_Registry_v8_Delta_Candidate_R1_2026-10-24_DRAFT.md`
   (delta) — **current evidence source of truth**. The delta alone is not Registry v8.
4. `docs/ai_handoff/PROJECT_HANDOFF.md` — stable orientation (problem, pipeline, authority hierarchy)
5. `docs/ai_handoff/CURRENT_STATE.md` — **current implementation state** (branch, HEAD, latest
   checkpoint/audit, open blockers) — this is the only file that should ever name a specific "latest"
   checkpoint or audit path. Re-read it fresh every session; it goes stale as soon as the repository
   advances.
6. `docs/ai_handoff/CROSS_AUDIT_PROTOCOL.md` — how Claude Code and Codex split work and cross-check each other
7. The latest applicable checkpoint/audit **as identified by `CURRENT_STATE.md`** — treat this, not any
   path hard-coded here, as the current implementation evidence.

The current research lineage branch is `thesis-v7` (the branch name is historical and is not renamed).
Framework v8 activation is methodology/evidence only: v8 coding, model construction, solver calls, Pilot,
production runs and results acceptance are **not authorized** (every v8 stage in the pointer is
`NOT_YET_AUTHORIZED` / `NOT_YET_EXECUTED`). Framework v7.4, the accepted G1 / Full81 / EOB results and
Pointers R1/R2 are historical accepted predecessors in v7.4 scope; Registry v7.4 continues only as the
unchanged base component of Registry v8. `src/current_mainline_pointer_v1.py` canonical mode now fails
closed by design; the historical v7.4 route is v1 candidate mode on
`configs/candidates/current_mainline_pointer_candidate_r2.json`. Framework v7.3 and Registry v7.3 are
historical accepted predecessors only. Framework v7.2 and Registry v7.2 are historical
accepted predecessors only. Registry v7.3 R1/R2 are failed immutable provenance. Earlier framework /
registry files and failed candidates must not be used as current authority; use them only for their
explicitly assigned provenance, regression, historical-lineage, replication, or comparison roles.

## Hard rules

- **Do not reopen a CLOSED methodological decision** (A1–A4, B1–B2, Gate 1, Gate 2 — see Framework
  §0.1) without demonstrating a code error, data error, or source-transcription error. A disagreement
  or an alternative modeling preference is not sufficient.
- **Inspect before editing.** Read the current file/section and the framework clause governing it before
  touching anything methodology-adjacent.
- **Distinguish methodology change from implementation correction** explicitly, every time. Never
  silently change formulas, parameter semantics, tariff/cost basis, degradation semantics, preprocessing
  rules, Layer A/B boundaries, solver settings, or production parameters to make code simpler or a model
  easier to solve.
- **Never alter frozen/historical artifacts** — checkpoints, audits, `results/eob_production/*`, anything
  under `docs/checkpoints/`. A provenance guard rejecting a run is signal, not an obstacle. This applies
  with equal force to production-authority and repository-authority checks — see "Working-tree
  discipline" below.
- **Run relevant tests/audits after modification** and **inspect `git diff` before declaring PASS**.
  This project already runs a strict evidence-discipline protocol — see
  `docs/protocols/iris_thesis_rigorous_audit_skill.md` — follow it: separate feasibility from optimality
  from research acceptability; never treat a Codex/Claude narrative summary as evidence when a
  source/build/test/run artifact is required.

## Working-tree discipline specific to this repo

This repository gates production execution behind a `repository_authority()`-style check in the current
production runner (see `CURRENT_STATE.md` for which script that is right now). That check treats
untracked files and protected-identity mismatches as hard blockers, not warnings.

**Before any production run**: inspect `CURRENT_STATE.md` and read the CURRENT implementation of the
runner's authority-gate function directly — do not rely on a description of it written at any earlier
time, including in this file. Production provenance guards must never be bypassed, weakened, or edited
around. Any untracked file or protected-identity inconsistency the gate reports must be treated as an
evidence/provenance finding to investigate and resolve through an authorized correction — never silently
ignored, deleted around, or hand-patched in the manifest outside the runner's own audited process.

## Scope discipline

- Never edit the same governance/methodology-adjacent files that Codex is actively working on in the same
  working tree at the same time — see `docs/ai_handoff/CROSS_AUDIT_PROTOCOL.md`.
- Do not commit or push unless explicitly instructed for that specific change.
