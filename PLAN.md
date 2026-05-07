# PLAN.md

Phase-gated plan for the process-mining research agent. Update status as work proceeds.

## Phase 0 — Initialize research context

Status: complete for `first-petri-net-limited-ops`

Acceptance criteria:

- Active goal selected.
- Operation model and constraints written down.
- Candidate registry has at least initial baseline families.
- Smoke-test logs are available.

## Phase 1 — Candidate enumeration

Status: complete for first iteration

Acceptance criteria:

- At least six candidate families listed.
- Each candidate has ID, hypothesis, intermediate representation, operation-cost expectation, failure risks, and first test.
- Baselines are included.

## Phase 2 — Baseline harness

Status: extended and smoke-validated

Acceptance criteria:

- `scripts/benchmark.py` runs on toy logs.
- Each run records operation counts and a machine-readable result.
- Petri-net/PMIR artifacts can be serialized to JSON.
- EXP-0003 additionally records strict token-game replay and visible-transition structural diagnostics.

## Phase 3 — First prototypes

Status: active, first iteration complete

Acceptance criteria:

- Implement 2–3 low-cost candidates.
- Run smoke tests.
- Record failures and counterexamples.
- Promote or retire candidates according to evidence.

Progress:

- Executable and smoke-tested: `ALG-0001`, `ALG-0002`, `ALG-0006`.
- Specified but not executable: `ALG-0003`, `ALG-0004`, `ALG-0005`.
- No candidate promoted to `promising` in EXP-0003.

## Phase 4 — Deep testing of promising candidates

Status: not started

Acceptance criteria:

- Run broader synthetic logs with controlled noise, missing behavior, duplicated labels, loops, choices, and concurrency.
- Compare against baselines.
- Run ablations and parameter sweeps.
- Measure runtime and operation counts.

## Phase 5 — Refinement loop

Status: not started

Acceptance criteria:

- For each promising candidate, produce at least one refined variant or a justified retirement.
- Explain what changed and why.
- Retest all refined variants.

## Phase 6 — Property study for super-promising candidates

Status: not started

Acceptance criteria:

- Create property dossier.
- Prove, disprove, or mark unknown for each property.
- Run counterexample search.
- Separate formal guarantees from empirical evidence.

## Phase 7 — Research report

Status: not started

Acceptance criteria:

- Summarize candidates, results, and properties.
- Include negative results.
- Include reproduction commands.
- Include next research questions.
