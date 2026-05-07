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

Status: active, first iteration extended with all required comparator families executable or intentionally risky

Acceptance criteria:

- Implement 2–3 low-cost candidates.
- Run smoke tests.
- Record failures and counterexamples.
- Promote or retire candidates according to evidence.

Progress:

- Executable and smoke-tested or benchmarked: `ALG-0001`, `ALG-0002`, `ALG-0003`, `ALG-0004`, `ALG-0005`, `ALG-0006`, `ALG-0009`, `ALG-0010`, `ALG-0011`, `ALG-0012`, `ALG-0013`.
- Specified but not executable among required first comparator families: none. `ALG-0007` and `ALG-0008` remain risky idea-stage side candidates.
- `ALG-0009` promoted to `promising` in EXP-0004 and moved to `deep-testing` in EXP-0005; `ALG-0010` promoted to `promising` in EXP-0006; `ALG-0003` promoted to `promising` in EXP-0007 and moved to `deep-testing` in EXP-0008; `ALG-0005` promoted to `promising` in EXP-0009; `ALG-0004` implemented and benchmarked in EXP-0011 but not promoted; `ALG-0011` promoted to `promising` in EXP-0012 and moved to `deep-testing` in EXP-0013; `ALG-0012` promoted to `promising` in EXP-0014 and kept there after EXP-0015; `ALG-0013` added as a smoke-tested ablation in EXP-0015; `ALG-0001`, `ALG-0002`, and `ALG-0006` remain unpromoted baselines/counterexamples.

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
- EXP-0011 added `ALG-0004` to the smoke and synthetic runners. It recovers visible places for sequence, XOR, parallel, and noise, but remains `benchmarked` because optional skips overgeneralize, loops remain partial, and operation counts are high.
- EXP-0012 added `ALG-0011` to the smoke and synthetic runners. It fixes the simple `skip.json` precision failure of `ALG-0004` using one accepted optional tau pattern, but does not repair overlapping optional chains or optional/concurrency.
- EXP-0013 added a no-repair ablation and broader optional-pattern tests for `ALG-0011`. The repair is causal for singleton and two-disjoint optional skips, but overlapping optional chains and optional/concurrency still fail.
- EXP-0014 added `ALG-0012`, a chain-aware region repair. It fixes overlapping optional chains but costs more than `ALG-0010` and still does not repair optional/concurrency.
- EXP-0015 added `ALG-0013`, the no-certification ablation of `ALG-0012`, and a new optional-concurrency probe. The ablation matched `ALG-0012` with only tiny operation savings; `optional_singleton_parallel_branch` exposed a new optional/concurrency gap for `ALG-0003`, `ALG-0010`, and the region variants.

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
- `ALG-0004` completes the required region-inspired comparator family as a solver-free visible-place implementation. Next work is either a small silent optional-place refinement or retirement as a documented negative comparator.
- `ALG-0011` is the small silent optional-place refinement. EXP-0013 added an ablation; next work should decide whether chain-aware optional repair belongs in a region variant or in the existing `ALG-0010` chain compiler family.
- `ALG-0012` is the chain-aware region repair. EXP-0015 added the selected-shortcut-certification ablation (`ALG-0013`) and found no current quality difference. Next work should either search for uncertified-chain false positives or shift to `ALG-0005` grammar/block abstraction because the region repair line is increasingly costly.

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
