# Iris Thesis — Version / Provenance Management Protocol

**Protocol status:** GOVERNING HANDOFF / REUSABLE PROJECT RULE  
**Date:** 2026-09-21  
**Project:** Iris Thesis  
**Applies to:** all future Claude Code / Codex / coding-agent tasks involving versioning, provenance, checkpoints, production runners, manifests, reruns, audits, or accepted research artifacts.

---

## 0. Purpose

This document defines the default version-management and provenance procedure for the Iris Thesis repository.

It exists to prevent the failure modes discovered during the V7.2 provenance/version-lineage work, including:

- treating unchanged file bytes as proof of executable-route compatibility;
- overwriting prior provenance candidates;
- allowing a candidate to self-accept;
- confusing implementation state with methodology authority;
- deriving new provenance from predecessor prose instead of primary artifacts;
- double-counting subconditions or aggregate summaries as independent guards;
- omitting fail-closed source conditions;
- falsely declaring JSON/CSV parity from row counts only;
- losing exact Git-status semantics through whitespace normalization;
- conflating historical production authority with corrected/future production authority;
- silently changing accepted results, historical runners, manifests, or checkpoints.

This protocol is the default unless a later **explicitly authorized protocol revision** supersedes it.

---

# 1. Source-of-Truth Hierarchy

Unless explicitly superseded by a later accepted artifact:

## Methodology source of truth
**Framework v7.2**

## Evidence / literature source of truth
**Registry v7.2**

## Implementation source of truth
The **latest accepted implementation checkpoint / independently audited artifact / live working tree**, subject to the authority hierarchy below.

## Authority hierarchy

When sources conflict, use this order:

1. **Primary repository bytes / source code**
2. **Primary run artifacts / manifests / hashes**
3. **Git objects / tags / refs / commits**
4. **Accepted machine-readable provenance artifacts**
5. **Accepted human-readable checkpoints**
6. **Candidate provenance artifacts**
7. **Prior reports / prose / agent summaries**

Agent prose is never stronger authority than primary bytes.

---

# 2. CLOSED Decisions Must Not Be Reopened Casually

Default rule:

> Do not reopen CLOSED / ACCEPTED research or methodology decisions unless a primary code, data, formula, source-transcription, or provenance error is demonstrated.

A later agent disagreeing with an earlier decision is **not sufficient**.

A reopening requires explicit evidence such as:

- source-code contradiction;
- data/transcription error;
- wrong equation implementation;
- wrong primary-source interpretation;
- wrong SHA / artifact identity;
- wrong Git-object reconstruction;
- reproducibility/provenance defect that changes the claimed authority.

If no such evidence exists, preserve the accepted decision.

---

# 3. Candidate Lifecycle

Every new provenance/version-management change follows this lifecycle:

**IMPLEMENTATION / CORRECTION**
→ **CANDIDATE**
→ **INDEPENDENT READ-ONLY AUDIT**
→ one of:

- **PASS → CLOSED / ACCEPTED**
- **STOP → immutable historical candidate**

A producing agent must never self-promote its own candidate to CLOSED / ACCEPTED.

## Allowed status vocabulary

Use explicit states such as:

- `CANDIDATE`
- `CANDIDATE_PASS`
- `PASS`
- `STOP`
- `CLOSED`
- `ACCEPTED`
- `NOT_YET_EXECUTED`
- `NOT_YET_AUTHORIZED`
- `NOT_APPLICABLE`
- `UNKNOWN`
- `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE`
- `PARTIALLY_RECONSTRUCTIBLE`
- `FULLY_RECONSTRUCTIBLE`

Do not substitute vague prose such as “probably valid”, “essentially accepted”, or “looks fine”.

---

# 4. STOP Candidates Are Immutable Historical Provenance

If Candidate Rn receives `STOP`:

- do **not** edit it;
- do **not** overwrite it;
- do **not** patch its machine-readable records in place;
- do **not** rewrite its checkpoint to make it pass;
- do **not** reuse its namespace as the next candidate.

Instead create:

`Candidate R(n+1)`

as a new additive namespace.

Example:

- R4 = STOP
- R5 = new additive correction
- R5 = STOP
- R6 = new additive correction

Every successor must preserve all predecessors byte-identically.

---

# 5. Additive-Only Correction Rule

Version/provenance corrections are additive by default.

Authorized changes should normally be limited to:

- new candidate namespace;
- new checkpoint;
- new manifest;
- new machine-readable ledgers;
- new deterministic snapshots;
- new acceptance artifact after independent audit.

Do not mutate historical:

- runner files;
- run results;
- completion manifests;
- prior provenance packages;
- prior checkpoints;
- prior tags;
- accepted evidence;
- accepted sensitivity outputs.

If mutation of an accepted production artifact is truly required, stop and create a separately authorized migration plan first.

---

# 6. Historical Production Artifacts Must Remain Historical

A historical production runner is evidence of what was actually executed.

Therefore:

> Never silently repurpose a historical runner by changing its pins and continuing to call it the same production authority.

If corrected methodology/input/core requires a new production route:

- preserve the historical runner byte-identically;
- create a new runner lineage;
- create a new preflight;
- create a new runner-authority manifest;
- create a new production checkpoint/tag authority only after audit.

Raw runner identity and route compatibility are separate concepts.

Example:

`historical_19b_raw_sha = UNCHANGED`

does **not** imply:

`corrected_R10_execution_route = AUTHORIZED`.

---

# 7. Primary-Source-First Reconstruction

Any acceptance-critical version/provenance inventory must be generated from primary source.

Correct generation order:

1. read primary source code / artifact bytes;
2. enumerate acceptance-relevant evaluation sites;
3. build source-coverage ledger;
4. classify guards / components / summaries;
5. evaluate current state;
6. generate route/provenance inventory;
7. generate difference matrix;
8. calculate counts;
9. serialize JSON/CSV;
10. audit independently.

Forbidden pattern:

> predecessor inventory → hard-coded ID filter → new candidate

or:

> predecessor difference matrix → delete/add selected rows → claim independent reconstruction.

Predecessor packages may be used for **historical comparison only**, not to define the new acceptance-critical universe.

---

# 8. Source-Coverage Requirement

For execution/authority logic, every acceptance-relevant source evaluation site must map to a declared role.

Recommended controlled roles:

- `DISTINCT_MANDATORY_GUARD`
- `COMPONENT_DETAIL`
- `AGGREGATE_SUMMARY`
- `REDUNDANT_RECHECK`
- `NON_EXECUTION_DIAGNOSTIC`
- `NOT_APPLICABLE`

The package must explain why each source site belongs to its role.

## Important distinction

**Guard count ≠ root-cause count.**

Multiple independently evaluated fail-closed guards may expose the same root cause.

Likewise:

- a collection loop may be one guard with many mismatching members;
- those members are component details unless independently evaluated elsewhere;
- an aggregate summary is not an additional guard;
- a summary must never contain itself in the set it summarizes.

---

# 9. Pre-Execution Authority vs Post-Solve Acceptance

Every production route must explicitly distinguish:

## Pre-execution production authority
Conditions that determine whether a solve is allowed to start.

Examples:

- runner/helper/core/input identities;
- Git/ref authority;
- repository boundary;
- manifest authority;
- parameter fingerprint;
- solver fingerprint;
- case universe/order;
- validator/preflight requirements.

## Post-solve result acceptance
Conditions that can only be evaluated after optimization/results exist.

Examples may include:

- result-surface completeness;
- postsolve checks;
- case-result rechecks;
- output integrity validation.

Post-solve conditions must not be counted as pre-execution authorization guards.

---

# 10. No Solve During Provenance / Authority Repair Unless Explicitly Authorized

Default for version-lineage, provenance, runner-alignment, manifest, checkpoint, and audit work:

- `ZERO optimize()`
- `ZERO model solve`
- `ZERO production rerun`
- `ZERO sensitivity solve`
- model construction should be zero if static verification is sufficient.

Allowed:

- source inspection;
- AST parsing;
- syntax/import checks;
- SHA verification;
- Git read-only inspection;
- manifest checks;
- schema validation;
- JSON/CSV parity;
- static preflight;
- build-only checks.

A solve requires a separately authorized gate.

---

# 11. Cross-Agent Independence Rule

The agent that creates a candidate must not be the only agent that accepts it.

Preferred pattern:

- Claude Code implements → Codex audits
- Codex implements → Claude Code audits

The independent auditor must:

- treat candidate prose as untrusted;
- re-derive acceptance-critical facts;
- use primary repository bytes;
- make zero repairs during audit;
- perform zero solves unless audit scope explicitly authorizes them.

If audit = STOP:

> report blockers and stop.

Do not repair in the same audit pass.

---

# 12. Machine-Readable Evidence Must Be Canonical

For each record family:

1. define the complete schema first;
2. every record uses the same key set;
3. semantic absence uses controlled sentinels;
4. do not inconsistently mix absent keys and `null`;
5. generate JSON and CSV from the **same canonical in-memory records**.

Recommended sentinels include:

- `NOT_APPLICABLE`
- `NOT_YET_EXECUTED`
- `NOT_YET_AUTHORIZED`
- `UNKNOWN`
- `INFINITY_UNSET`
- `NOT_RECONSTRUCTIBLE_FROM_AVAILABLE_EVIDENCE`

---

# 13. JSON / CSV Parity Rule

Row-count equality is not parity.

Required audit:

JSON record  
→ corresponding CSV row  
→ `json.loads()` every CSV cell  
→ reconstruct dictionary  
→ exact structural equality.

Acceptance requires:

`all records / all records exact`

for every dual-format family.

Any absent-key / present-null mismatch is a failure.

---

# 14. Difference Matrix Rules

A cross-version difference matrix must distinguish at minimum:

- specification changes;
- raw identity;
- execution-route authority;
- meaningful unchanged fields;
- future authority sentinels;
- pending optimization responses.

For unexecuted future cases:

- `new_value = NOT_YET_EXECUTED`
- `changed = UNKNOWN`
- `numerical_delta = NOT_APPLICABLE`
- `relative_delta = NOT_APPLICABLE`
- `change_type = OPTIMIZATION_RESPONSE`

Never fabricate future numerical results.

Do not infer numerical effects of individual corrections without isolated counterfactual solves.

---

# 15. Causal Claim Boundary

Cross-version numerical differences are observational unless isolated counterfactual experiments exist.

Do not say:

> correction X caused Δobjective

when multiple corrections changed simultaneously.

Use language such as:

> the observed R1→R10 difference reflects the combined corrected implementation and cannot be uniquely attributed to one correction.

Preserve explicit unresolved/caution items.

---

# 16. Exact Git-State Preservation

Git status whitespace is semantic.

For exact repository snapshots:

- capture raw subprocess bytes before decoding;
- never `.strip()` / `.lstrip()` exact porcelain output;
- record literal command argv;
- record raw bytes or Base64;
- record SHA-256;
- record byte count;
- record decoded text;
- create structured parsing separately.

Recommended command must be recorded literally, for example:

`git -c core.quotePath=false status --porcelain=v1 --untracked-files=all`

Do not claim byte-exact reproducibility without recording the invocation.

Cross-check separately:

- staged paths;
- unstaged tracked paths;
- untracked paths;
- ignored-runtime inventory where relevant.

---

# 17. Repository Non-Mutation Proof

Every audit/corrective pass must record before/after:

- branch;
- HEAD;
- origin;
- staged state;
- tracked modified paths;
- untracked paths;
- exact porcelain bytes/hash where required;
- Framework SHA;
- Registry SHA;
- relevant core SHA;
- relevant runner/helper SHAs;
- prior candidate/checkpoint/manifest SHAs.

Unless explicitly authorized:

- no commit;
- no push;
- no tag;
- no reset;
- no clean;
- no stash;
- no checkout.

Only explicitly authorized additive files may appear.

---

# 18. Reconstructibility Must Be Multi-Axis

Do not report one vague “reconstructible” flag.

Track separately:

- `code_reconstructibility`
- `input_reconstructibility`
- `execution_identity_reconstructibility`
- `full_execution_state_reconstructibility`
- `overall_reconstructibility`

Also distinguish:

> currently reconstructible from surviving working-tree/gitignored bytes

from:

> durably reconstructible from Git history.

A gitignored surviving file is not equivalent to Git-durable provenance.

---

# 19. Historical Evidence Search Rule

Before declaring a historical artifact missing:

- search active working tree;
- search preserved audit copies;
- search relevant `before/` snapshots;
- inspect Git objects/history where applicable;
- verify expected SHA.

Do not classify an artifact as absent merely because:

- it is gitignored;
- it is outside the active input path;
- it is not visible in the current top-level directory.

Record:

- expected SHA;
- surviving path;
- surviving SHA;
- required-for-reconstruction;
- limiting consequence.

---

# 20. Manifest Rules

A package manifest must be deterministic.

Clearly distinguish:

- physical files in package directory;
- internal non-manifest registered artifacts;
- external registered artifacts/checkpoints;
- manifest itself.

Avoid circular self-hash.

If manifest self-hash is intentionally omitted, state this explicitly.

Verify:

- registered path exists;
- SHA matches;
- byte count matches;
- zero registered-but-missing;
- zero required-unregistered;
- zero hash mismatches;
- zero byte mismatches.

---

# 21. Package Identity Rules

Every active record in Candidate Rn must carry one Rn package identity.

Example:

`V7_2_PRODUCTION_VERSION_LINEAGE_FREEZE_CANDIDATE_R7`

Older candidate names may appear only as:

- predecessor references;
- historical evidence;
- audit subjects.

No stale active ownership labels are allowed.

---

# 22. Version Naming / Namespace Convention

Use explicit additive version names.

Recommended structure:

`results/provenance/<topic>_candidate_rN/`

and:

`docs/checkpoints/<topic>_rN_<YYYY-MM-DD>.md`

Never reuse an old candidate directory.

After independent acceptance, create a separate additive acceptance artifact if durable closure needs to be recorded.

Do not rewrite the candidate checkpoint to pretend it was always accepted.

---

# 23. Runner / Authority Versioning Rule

A production route is a bundle, not a single Python file.

Treat authority as including, where applicable:

- runner SHA;
- helper SHA;
- core SHA/version;
- canonical input SHA;
- settlement artifacts;
- preflight SHA;
- authority manifest;
- parameter fingerprint;
- solver fingerprint;
- case universe/order;
- repository boundary;
- checkpoint/tag/commit identity.

Therefore:

> same runner bytes ≠ same production route.

Any corrected production route must receive its own coherent authority bundle.

---

# 24. Future Route Status Rules

If future production authority has not yet been built/audited, use explicit states:

- `production_runner_status = NOT_YET_AUTHORIZED`
- `production_runner_sha256 = NOT_YET_AUTHORIZED`
- `runner_authority_manifest = NOT_YET_AUTHORIZED`
- `production_tag_identity = NOT_YET_AUTHORIZED`
- `final81_preflight_identity = NOT_YET_AUTHORIZED`

Do not use historical authority values as placeholders for corrected/future authority.

---

# 25. Commit / Tag Freeze Rule

Do not commit/tag merely because an implementation agent reports Candidate Pass.

Preferred sequence:

1. build candidate;
2. independent read-only audit;
3. PASS / CLOSED;
4. separately authorize commit/tag freeze;
5. verify local/remote refs;
6. only then authorize production execution.

Production tags should have explicit semantics:

- tag type;
- tag object;
- peeled commit;
- remote synchronization;
- associated checkpoint/manifest.

---

# 26. Default Final Verdict Format

Every candidate implementation should end with exactly one:

`<TOPIC> — CANDIDATE PASS`

or

`<TOPIC> — STOP`

Every independent audit should end with exactly one:

`<TOPIC> — PASS`

or

`<TOPIC> — STOP`

Only an independent PASS may additionally state:

`<TOPIC> — CLOSED / ACCEPTED`

---

# 27. Default Stop Conditions

STOP if any acceptance-critical issue exists, including:

- primary-source coverage incomplete;
- taxonomy generated from predecessor artifacts instead of primary source;
- required guard omitted;
- duplicate/aggregate guard counted as independent;
- stale package identity;
- JSON/CSV structural mismatch;
- manifest mismatch;
- predecessor modified;
- wrong SHA;
- historical/future authority conflated;
- future numerical result fabricated;
- exact Git snapshot semantically corrupted;
- repository mutation outside authorized scope;
- solve performed when prohibited;
- candidate self-acceptance without independent audit.

---

# 28. Default Handoff Header for Future Agents

Use the following block at the top of future coding/audit instructions:

```text
IRIS THESIS VERSION / PROVENANCE GOVERNANCE

Current methodology source of truth = Framework v7.2.
Current evidence source of truth = Registry v7.2.
Current implementation authority = latest independently CLOSED / ACCEPTED checkpoint plus the verified live working tree.

Follow:
docs/protocols/iris_thesis_version_provenance_management_protocol.md

Do not reopen CLOSED decisions unless a primary code/data/source-transcription/provenance error is demonstrated.

Historical STOP candidates are immutable.
Corrections are additive.
Candidate author cannot self-accept.
Acceptance requires independent read-only cross-agent audit.

Primary bytes outrank candidate prose.
Do not derive acceptance-critical taxonomy from predecessor ledgers.
Do not mutate accepted historical runners/results/manifests.

ZERO solve unless the current gate explicitly authorizes solving.
```

---

# 29. Current V7.2 Milestone State at Protocol Creation

At creation of this protocol:

## Version-lineage / rerun-difference freeze
**R7 = PASS**

**V7.2 VERSION LINEAGE / RERUN DIFFERENCE FREEZE = CLOSED / ACCEPTED**

Accepted independently reconstructed facts include:

- 8 lineages;
- 10 executions;
- 96 executed results;
- 59 acceptance-relevant source sites;
- 57 distinct mandatory route guards;
- 11 currently failing distinct guards;
- 6 unique hard root causes;
- 3 historical-only incompatibility concepts;
- C4 = 110;
- total difference matrix = 263;
- corrected final81 = `NOT_YET_AUTHORIZED`;
- corrected final81 = `NOT_YET_EXECUTED`.

## Next authorized phase
**Corrected R10 Final81 Production Route / Authority Alignment — BUILD ONLY**

No corrected 81-case rerun is authorized yet.

SOC sensitivity is not the current next step.

---

# 30. Governance Rule for Updating This Protocol

This protocol itself should be version-controlled.

If a future defect is discovered:

1. preserve this protocol version;
2. create a new protocol revision;
3. describe the defect and rationale;
4. independently audit the revised protocol if it changes acceptance-critical behavior;
5. explicitly state which revision supersedes the prior one.

Do not silently edit the governing protocol in place after it has been used to authorize production work.

---

# 31. Short Operational Rule

When uncertain, default to:

> PRESERVE HISTORY  
> ADD A NEW VERSION  
> RE-DERIVE FROM PRIMARY BYTES  
> AUDIT WITH A DIFFERENT AGENT  
> DO NOT SOLVE UNTIL THE ROUTE IS AUTHORIZED  
> DO NOT CALL A CANDIDATE ACCEPTED UNTIL INDEPENDENT PASS
