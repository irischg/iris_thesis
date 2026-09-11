# CLAUDE.md — Governance for Claude Code

This is a master's thesis research repository (campus PV–BESS service-continuity
planning, NTUST demonstration case), not a generic software project.
**Methodological validity and academic defensibility outrank speed or code elegance.**

## Read first, in order

1. `docs/research_framework_v7_2_2026-08-24.md` — **current methodology source of truth**
2. `docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md` — **current evidence source of truth**
3. `docs/ai_handoff/PROJECT_HANDOFF.md` — stable orientation (problem, pipeline, authority hierarchy)
4. `docs/ai_handoff/CURRENT_STATE.md` — **current implementation state** (branch, HEAD, latest
   checkpoint/audit, open blockers) — this is the only file that should ever name a specific "latest"
   checkpoint or audit path. Re-read it fresh every session; it goes stale as soon as the repository
   advances.
5. `docs/ai_handoff/CROSS_AUDIT_PROTOCOL.md` — how Claude Code and Codex split work and cross-check each other
6. The latest applicable checkpoint/audit **as identified by `CURRENT_STATE.md`** — treat this, not any
   path hard-coded here, as the current implementation evidence.

Earlier framework/registry files (`*_v7_2026-08-14.md`, `*_v7_1_2026-08-16.md`, merge-audit files) are
**provenance / regression / historical lineage only**, unless v7.2 explicitly assigns them another role.
Do not cite or apply them as current methodology.

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
