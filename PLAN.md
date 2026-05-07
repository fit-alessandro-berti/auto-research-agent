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
- EXP-0004 additionally records strict token-game replay, bounded silent-transition closure, negative-trace probes, and visible-transition structural diagnostics.

## Phase 3 — First prototypes

Status: active, first iteration extended

Acceptance criteria:

- Implement 2–3 low-cost candidates.
- Run smoke tests.
- Record failures and counterexamples.
- Promote or retire candidates according to evidence.

Progress:

- Executable and smoke-tested: `ALG-0001`, `ALG-0002`, `ALG-0003`, `ALG-0005`, `ALG-0006`, `ALG-0009`, `ALG-0010`.
- Specified but not executable: `ALG-0004`.
- `ALG-0009` promoted to `promising` in EXP-0004 and moved to `deep-testing` in EXP-0005; `ALG-0010` promoted to `promising` in EXP-0006; `ALG-0003` promoted to `promising` in EXP-0007 and moved to `deep-testing` in EXP-0008; `ALG-0005` promoted to `promising` in EXP-0009; `ALG-0001`, `ALG-0002`, and `ALG-0006` remain unpromoted baselines/counterexamples.

## Phase 4 — Deep testing of promising candidates

Status: active for `ALG-0009`; started for comparator candidates

Acceptance criteria:

- Run broader synthetic logs with controlled noise, missing behavior, duplicated labels, loops, choices, and concurrency.
- Compare against baselines.
- Run ablations and parameter sweeps.
- Measure runtime and operation counts.

Progress:

- EXP-0005 ran ablations and seven synthetic counterexample families.
- `ALG-0009` was stable under checked trace-order permutations.
- Material failures remain for overlapping optional skips, optional branches mixed with concurrency, short loops, and duplicate labels.
- EXP-0006 added `ALG-0010`, fixing overlapping optional skips but not optional/concurrency.
- EXP-0007 added `ALG-0003` to the synthetic runner. It handles nested XOR and overlapping optional skips, but initially failed optional-concurrency, short-loop, and duplicate-label cases through fallback.
- EXP-0008 added a bounded optional-concurrency cut and ablation to `ALG-0003`; `parallel_with_optional_branch` now replays 3/3 with 3/3 negative rejection, while the ablation still fails 0/3.
- EXP-0009 added `ALG-0005` to the smoke and synthetic runners. It exactly replays all current positive traces and rejects all current negative probes, including loop and duplicate-label cases, but is treated as an overfitting comparator.
- EXP-0010 stress-tested `ALG-0005`: it rejects held-out valid interleavings, memorizes observed noise, and shows fast raw-trie growth under full permutation variants. It remains `promising`.

## Phase 5 — Refinement loop

Status: started with `ALG-0010` and block-structured comparator work

Acceptance criteria:

- For each promising candidate, produce at least one refined variant or a justified retirement.
- Explain what changed and why.
- Retest all refined variants.

Progress:

- `ALG-0010` is the first refinement split from `ALG-0009`.
- It improves one material counterexample but introduces higher operation counts and keeps optional/concurrency failures.
- `ALG-0003` now has the explicit bounded optional-concurrency cut; next refinement choices are loop/duplicate-label handling, broader optional-concurrency composition, or pausing to implement another-family comparator (`ALG-0004` or `ALG-0005`).
- `ALG-0005` supplies the automaton/grammar comparator; next work should add an abstraction/refinement before further promotion.

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
