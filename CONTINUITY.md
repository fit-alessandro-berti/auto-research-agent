# CONTINUITY.md

## Active goal

`GOALS/first-petri-net-limited-ops.md`.

## Current status

Eighth research iteration complete. `ALG-0005` stress tests now document its exact-replay tradeoff: it rejects held-out valid interleavings, memorizes noisy observed variants, and shows rapid raw-trie growth under permutation variants. It remains `promising`, not `deep-testing`.

## Last completed actions

- Created process-mining research-agent scaffold.
- Added candidate registry, evaluation protocol, property-study protocol, and smoke-test harness.
- Implemented `ALG-0001` Alpha-Lite Relations baseline.
- Implemented `ALG-0006` PMIR Split-Join Compiler Lite starter candidate.
- Ran `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Spawned candidate, implementation, evaluator/counterexample, and property-study scouts; merged their findings into registry and experiment notes.
- Added `ALG-0002` Frequency-Threshold Dependency Graph prototype.
- Added `scripts/petri_eval.py` with strict token-game replay and structural diagnostics.
- Added explicit `arithmetic` primitive to the operation model.
- Created candidate records for `ALG-0002` through `ALG-0005`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json` and `python3 -B -m compileall scripts`.
- Added `ALG-0009` PMIR Guarded Split-Join Compiler as a repaired variant of `ALG-0006`.
- Extended the evaluator with bounded silent-transition closure for `tau_` transitions.
- Added negative-trace precision probes to `scripts/benchmark.py`.
- Added `scripts/dependency_threshold_sweep.py` and ran `experiments/dependency-threshold-sweep.json`.
- Promoted `ALG-0009` to `promising`; no candidate is `super-promising`.
- Added ablation switches to `ALG-0009` for optional and XOR guards.
- Added `scripts/alg0009_deep_tests.py` with synthetic counterexamples and trace-order stability checks.
- Ran `experiments/alg0009-deep-tests.json`.
- Moved `ALG-0009` to `deep-testing`; no candidate is `super-promising`.
- Added `ALG-0010` PMIR Conflict-Aware Optional Chain Compiler.
- Wired `ALG-0010` into smoke and synthetic deep-test runners.
- Promoted `ALG-0010` to `promising`; no candidate is `super-promising`.
- Added `scripts/cut_limited_process_tree.py` for `ALG-0003`.
- Wired `ALG-0003` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0003` to `promising`; no candidate is `super-promising`.
- Added `parallel_optional_sequence` detection and compilation to `ALG-0003`.
- Added `cut_tree_no_parallel_optional` ablation to `scripts/alg0009_deep_tests.py`.
- Reran smoke and synthetic tests; moved `ALG-0003` to `deep-testing`; no candidate is `super-promising`.
- Added optional `transition_labels` to Petri-net JSON and evaluator support for multiple same-label visible transitions.
- Added `scripts/prefix_automaton_compression.py` for `ALG-0005`.
- Wired `ALG-0005` into smoke and synthetic runners.
- Promoted `ALG-0005` to `promising`; no candidate is `super-promising`.
- Added `scripts/alg0005_stress_tests.py`.
- Ran `experiments/alg0005-stress-tests.json`.
- Kept `ALG-0005` at `promising`; no candidate is `super-promising`.

## Latest smoke result

EXP-0009 executable-candidate replay summary:

| Log | ALG-0001 ops / replay / neg reject | ALG-0002 ops / replay / neg reject | ALG-0003 ops / replay / neg reject | ALG-0005 ops / replay / neg reject | ALG-0006 ops / replay / neg reject | ALG-0009 ops / replay / neg reject | ALG-0010 ops / replay / neg reject |
|---|---:|---:|---:|---:|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 / 3 of 3 | 214 / 4 of 4 / 3 of 3 | 261 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `parallel_ab_cd.json` | 544 / 4 of 4 / 3 of 3 | 240 / 4 of 4 / 3 of 3 | 243 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `sequence.json` | 499 / 3 of 3 / 3 of 3 | 211 / 3 of 3 / 3 of 3 | 168 / 3 of 3 / 3 of 3 | 228 / 3 of 3 / 3 of 3 | 181 / 3 of 3 / 3 of 3 | 190 / 3 of 3 / 3 of 3 | 239 / 3 of 3 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 / 1 of 3 | 118 / 1 of 3 / 1 of 3 | 191 / 0 of 3 / 3 of 3 | 186 / 3 of 3 / 3 of 3 | 110 / 1 of 3 / 1 of 3 | 113 / 1 of 3 / 1 of 3 | 139 / 1 of 3 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 / 3 of 3 | 144 / 2 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 175 / 4 of 4 / 3 of 3 | 132 / 2 of 4 / 3 of 3 | 139 / 4 of 4 / 3 of 3 | 187 / 4 of 4 / 3 of 3 |
| `xor.json` | 552 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 194 / 4 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 204 / 0 of 4 / 3 of 3 | 216 / 4 of 4 / 3 of 3 | 284 / 4 of 4 / 3 of 3 |

Semantic and structural interpretation:

- `ALG-0003` passes sequence, XOR, parallel, skip, and noise smoke families with clean structural diagnostics.
- EXP-0008 synthetic tests show `ALG-0003` now fixes `parallel_with_optional_branch` (3/3 replay and 3/3 negative rejection) while the `cut_tree_no_parallel_optional` ablation still fails it (0/3).
- `ALG-0003` fallback rejects short-loop and duplicate-label positives; this is a scoped failure, not a loop solution.
- `ALG-0005` exactly replays all current smoke and synthetic positives, including loop and duplicate-label cases, but this is exact automaton acceptance rather than a generalization claim.
- EXP-0010 shows `ALG-0005` rejects held-out valid interleavings: 0/4 for balanced parallel and 0/2 for optional-concurrency held-out traces. `ALG-0003` replays those same held-out sets 4/4 and 2/2 when its block evidence is sufficient.
- EXP-0010 also shows `ALG-0005` memorizes observed noise (`noise_memorization` rejects 0/1 clean negative probes) and grows to 447 raw trie nodes, 34 compressed states, and 8258 counted operations for all width-5 permutations.
- `ALG-0003` and `ALG-0009` are `deep-testing`. `ALG-0005` and `ALG-0010` are `promising`. No candidate is `super-promising`.

## Next action

Continue the first goal by prioritizing:

1. Implement `ALG-0004` bounded place-candidate region miner to complete the specified comparator families.
2. Consider an `ALG-0005` refinement with grammar/block abstraction or bounded merge ablation.
3. Broaden optional-concurrency tests beyond one singleton plus one optional length-2 branch.
4. Decide whether loop support belongs as a bounded `ALG-0003` cut or a split candidate.

## Current candidate focus

- `ALG-0001`: baseline, smoke-tested.
- `ALG-0002`: dependency-threshold baseline, smoke-tested, lower operation counts but not promoted because of unconstrained-transition diagnostics.
- `ALG-0003`: deep-testing block-structured baseline; next targets are loop/duplicate-label decisions and broader optional-concurrency tests.
- `ALG-0005`: promising exact automaton/grammar comparator; stress-tested for overfitting and variant growth, next target is abstraction/refinement.
- `ALG-0006`: smoke-tested starter candidate, lower counted operations but not promoted because XOR replay is disproven.
- `ALG-0009`: deep-testing guarded PMIR variant; next target is conflict-aware optional guard refinement.
- `ALG-0010`: promising conflict-aware optional-chain variant; fixes overlapping optional skips but not optional/concurrency.

## Decisions to preserve

- Keep the agent generic across process-mining research topics.
- For the first task, use Petri-net discovery under a limited-operation model as a concrete benchmark.
- Every candidate algorithm must be tracked, including failed and retired candidates.
- Do not promote `ALG-0006` without replay/semantic validation.
- Do not promote any candidate on positive-trace replay alone; structural diagnostics and negative traces are required.
- `ALG-0009` is promising only for the currently tested simple sequence/XOR/parallel/skip/noise scope; short loops and nested structures remain open.
- `ALG-0009` should not be called super-promising until overlapping optional and optional-concurrency counterexamples are repaired or explicitly scoped out.
- `ALG-0010` should be compared against a block-structured baseline before further promotion; its operation cost is higher than `ALG-0009`.
- `ALG-0003` is deep-testing only for simple accepted blocks and common sequence context; do not present it as a recursive inductive miner yet.
- The `ALG-0003` bounded optional-concurrency cut is causal for `parallel_with_optional_branch` but narrow.
- `ALG-0005` requires labeled visible transitions; evaluator now supports optional `transition_labels` while preserving legacy `t_<activity>` behavior.
- `ALG-0005` should not be promoted without an abstraction/refinement; EXP-0010 shows held-out failure and noise memorization.

## Blockers / unknowns

- Need to validate whether the EXP-0007 operation-budget formulas are tight enough after more synthetic cases.
- Need to decide whether to install PM4Py/ProM for standard metrics or keep early prototypes dependency-free.
- Need broader negative-trace precision tests and a non-trivial synthetic benchmark suite before any `super-promising` decision.

## Resume checklist

1. Read `AGENTS.md`.
2. Read this file.
3. Read `MEMORY.md` and `PLAN.md`.
4. Read `research/ALGORITHM_REGISTRY.md` and `research/EXPERIMENT_LOG.md`.
5. Continue from `Next action` unless the user gives a new goal.
