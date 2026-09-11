# Cross-Audit Protocol

This repository already runs an evidence-discipline culture (see
`docs/protocols/iris_thesis_rigorous_audit_skill.md`) and, concretely, a chain of independent
re-audits before any production run (`results/layer_a/final_81_reaudit/`,
`results/layer_a/final_81_runner_audit/`, `final_81_runner_correction_audit/`,
`final_81_execution_authorization/`). This document generalizes that practice into a stable workflow
for the three collaborators on this project.

## Roles

**GPT Chat**
- Methodology discussion, academic reasoning, source interpretation.
- High-level adjudication: decides whether a proposed change is a methodology change (requires
  reopening a CLOSED decision, per Framework §0.1) or an implementation correction.
- Designs narrow, explicit task prompts for the coding agents rather than letting them infer scope.

**Primary coding agent** — either Codex or Claude Code, whichever is actively assigned a task.
- Inspects/edits the local repository, runs authorized tests/builds/solves, produces structured
  evidence (diffs, model statistics, test output, hashes, git status).
- Follows `AGENTS.md` / `CLAUDE.md` and the evidence-discipline rules in
  `docs/protocols/iris_thesis_rigorous_audit_skill.md`.

**Secondary coding agent** — the other of Codex/Claude Code, invoked whenever an independent
read-only audit is warranted (any change touching methodology-adjacent code, solver settings, cost
basis, degradation semantics, or a frozen checkpoint; any change gating a production run).
- Performs a **read-only** audit: it may re-derive, re-check hashes, re-run build-only/no-solve
  diagnostics, and inspect diffs — it does not edit the working tree as part of the audit.
- Receives: the authoritative sources (Framework v7.2, Registry v7.2), current repository state, the
  diff/commit under review, and any test/audit output the primary agent produced.
- **Does not receive the primary agent's private reasoning or chat transcript** — only its stated
  claims plus the artifacts that should support them. This keeps the audit independent rather than
  anchored.

## Never simultaneous

**Never allow Codex and Claude Code to edit the same working tree at the same time.** One agent holds
write access to the working tree for a given task; the other, if active concurrently, is in a separate
worktree/branch or is strictly in the read-only secondary-audit role described above. This mirrors the
existing project rule against staging/committing unrelated files and against silent concurrent
modification of provenance-guarded artifacts.

## Independent-audit procedure

1. Primary agent completes a change and reports: files changed, methodology-vs-implementation
   classification, version/provenance-guard status, tests run, model/solver statistics if applicable,
   hashes, `git status`/`git diff` output, and a verdict.
2. Secondary agent is given the same authoritative sources plus the primary agent's diff/commit and
   test output — but is asked to independently re-derive the verdict, not to review the primary
   agent's stated reasoning for internal consistency alone.
3. Secondary agent reports its own verdict using the same evidence tiers as
   `docs/protocols/iris_thesis_rigorous_audit_skill.md` §3 (current-run logs/artifacts/hashes/tests
   outrank narrative summaries).

## Disagreement

**Do not resolve disagreement between primary and secondary by majority vote or by re-running until
one agent's verdict wins.** Instead:

1. Trace the disagreement to a specific artifact: does Framework v7.2 or Registry v7.2 say something
   the code contradicts? Does a data file not match what one agent assumed? Is there a source-
   transcription mismatch?
2. If the trace resolves to a **code or data error**, that is an implementation-correction task —
   assign it explicitly, re-audit after the fix.
3. If the trace resolves to a **genuine methodology ambiguity** (the Framework/Registry text does not
   settle the question), **escalate to GPT Chat for methodology adjudication.** Do not let either
   coding agent decide a methodology question by code-level judgment call.
4. Record the resolution path (which artifact settled it, or that it was escalated and why) — this
   repository's checkpoint/audit files are the model for how to do this; follow their level of
   explicitness rather than writing a shorter summary.

## Historical example — 2026-09-11 pre-governance-commit state

At the time this protocol was written, the repository's production runner
(`scripts/19b_run_final_layer_a_81_cases.py`) implemented exactly this kind of independent, read-only,
evidence-based gate for the 81-case Layer A production run (`repository_authority()`,
`ExecutionGuard(False)` mode, no-solve counters), and its latest audit at that time
(`results/layer_a/final_81_execution_authorization/20260911T065811Z/`) was a good concrete template for
what a secondary-agent audit report should look like: explicit identity verification, explicit
reachability analysis for a flagged file, explicit no-solve counters, and a verdict that does not soften
a blocking finding because the rest of the gate passed.

This example is recorded here as a **template for report style**, not as current state. **It does not
describe whether that blocker is still open.** For the live status of the production runner and any open
blockers, consult `docs/ai_handoff/CURRENT_STATE.md`, which is the only file in this handoff set
authorized to carry transient state.
