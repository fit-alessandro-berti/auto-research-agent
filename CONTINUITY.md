# CONTINUITY.md

## Active goal

`GOALS/first-petri-net-limited-ops.md`.

## Current status

Thirteenth research iteration complete. `ALG-0013` is now tracked as the no-certification ablation of `ALG-0012`. The ablation matches `ALG-0012` on current optional-pattern and broader synthetic replay/negative metrics while saving only tiny operation counts, so `ALG-0012` stays `promising` and `ALG-0013` is only `smoke-tested`. A new optional-concurrency probe, `optional_singleton_parallel_branch`, exposes a distinct gap across current generalizing candidates.

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
- Added `scripts/bounded_place_region_miner.py` for `ALG-0004`.
- Wired `ALG-0004` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Moved `ALG-0004` to `benchmarked`; no candidate is `super-promising`.
- Added `scripts/region_optional_tau_miner.py` for `ALG-0011`.
- Wired `ALG-0011` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Added `candidates/ALG-0011-region-optional-tau-repair-miner.md`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0011` to `promising`; no candidate is `super-promising`.
- Added `enable_optional_repair` ablation switch to `scripts/region_optional_tau_miner.py`.
- Added `scripts/alg0011_optional_tests.py` with singleton, two-disjoint, overlapping-chain, and optional-inside-parallel cases.
- Ran `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Moved `ALG-0011` to `deep-testing`; no candidate is `super-promising`.
- Added `scripts/region_optional_chain_miner.py` for `ALG-0012`.
- Wired `ALG-0012` into `scripts/benchmark.py`, `scripts/alg0009_deep_tests.py`, and `scripts/alg0011_optional_tests.py`.
- Added `candidates/ALG-0012-region-optional-chain-repair-miner.md`.
- Ran `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0012` to `promising`; no candidate is `super-promising`.
- Added `require_region_shortcut` to `scripts/region_optional_chain_miner.py`.
- Added `ALG-0013` as the `require_region_shortcut=False` ablation of `ALG-0012`.
- Wired `region_optional_chain_no_region_cert` into `scripts/alg0011_optional_tests.py` and `scripts/alg0009_deep_tests.py`.
- Added `optional_singleton_parallel_branch` to the optional-pattern suite.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, and `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`.
- Ran `python3 -B -m unittest` and `git diff --check` for final verification.
- Kept `ALG-0012` at `promising`, added `ALG-0013` as `smoke-tested`; no candidate is `super-promising`.

## Latest smoke result

EXP-0014 executable-candidate replay summary:

| Log | ALG-0001 ops / replay / neg reject | ALG-0002 ops / replay / neg reject | ALG-0003 ops / replay / neg reject | ALG-0004 ops / replay / neg reject | ALG-0011 ops / replay / neg reject | ALG-0012 ops / replay / neg reject | ALG-0005 ops / replay / neg reject | ALG-0006 ops / replay / neg reject | ALG-0009 ops / replay / neg reject | ALG-0010 ops / replay / neg reject |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 / 3 of 3 | 214 / 4 of 4 / 3 of 3 | 261 / 4 of 4 / 3 of 3 | 1325 / 4 of 4 / 3 of 3 | 1365 / 4 of 4 / 3 of 3 | 1461 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `parallel_ab_cd.json` | 544 / 4 of 4 / 3 of 3 | 240 / 4 of 4 / 3 of 3 | 243 / 4 of 4 / 3 of 3 | 1301 / 4 of 4 / 3 of 3 | 1341 / 4 of 4 / 3 of 3 | 1437 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `sequence.json` | 499 / 3 of 3 / 3 of 3 | 211 / 3 of 3 / 3 of 3 | 168 / 3 of 3 / 3 of 3 | 804 / 3 of 3 / 3 of 3 | 842 / 3 of 3 / 3 of 3 | 890 / 3 of 3 / 3 of 3 | 228 / 3 of 3 / 3 of 3 | 181 / 3 of 3 / 3 of 3 | 190 / 3 of 3 / 3 of 3 | 239 / 3 of 3 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 / 1 of 3 | 118 / 1 of 3 / 1 of 3 | 191 / 0 of 3 / 3 of 3 | 316 / 1 of 3 / 3 of 3 | 327 / 1 of 3 / 3 of 3 | 357 / 1 of 3 / 3 of 3 | 186 / 3 of 3 / 3 of 3 | 110 / 1 of 3 / 1 of 3 | 113 / 1 of 3 / 1 of 3 | 139 / 1 of 3 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 / 3 of 3 | 144 / 2 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 332 / 4 of 4 / 1 of 3 | 368 / 4 of 4 / 3 of 3 | 432 / 4 of 4 / 3 of 3 | 175 / 4 of 4 / 3 of 3 | 132 / 2 of 4 / 3 of 3 | 139 / 4 of 4 / 3 of 3 | 187 / 4 of 4 / 3 of 3 |
| `xor.json` | 552 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 194 / 4 of 4 / 3 of 3 | 730 / 4 of 4 / 3 of 3 | 770 / 4 of 4 / 3 of 3 | 844 / 4 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 204 / 0 of 4 / 3 of 3 | 216 / 4 of 4 / 3 of 3 | 284 / 4 of 4 / 3 of 3 |

Semantic and structural interpretation:

- `ALG-0003` passes sequence, XOR, parallel, skip, and noise smoke families with clean structural diagnostics, and EXP-0008 showed the bounded optional-concurrency cut is causal for `parallel_with_optional_branch`.
- `ALG-0004` completes the required region-inspired comparator family as an executable bounded visible-place search. It passes sequence, XOR, parallel, and noise, but is high cost and overgeneralizes optional behavior (`skip.json` rejects only 1/3 negatives; `overlapping_optional_skips` rejects 0/3).
- `ALG-0011` repairs the simple skip overgeneralization by accepting optional pattern `A,B,C` on `skip.json`; it improves negative rejection from `ALG-0004`'s 1/3 to 3/3 while preserving 4/4 replay.
- EXP-0013 confirms that repair is causal: the no-repair ablation matches `ALG-0004` on singleton and two-disjoint optional cases, while full `ALG-0011` improves negative rejection to 3/3 in both.
- `ALG-0011` rejects all overlapping optional-chain candidates under its non-single-context guard, so `overlapping_optional_skips` remains 0/3 negative rejection and `parallel_with_optional_branch` remains 1/3.
- `ALG-0012` repairs overlapping optional chains using selected region shortcuts: `overlapping_optional_skips` improves to 4/4 replay and 3/3 negative rejection, but operation count rises to 1037.
- `ALG-0012` still does not repair optional/concurrency: `parallel_with_optional_branch` remains 3/3 replay and 1/3 negative rejection.
- `ALG-0004` loop and duplicate-label behavior remains partial: `short_loop.json`, `short_loop_required`, and `duplicate_label_rework` replay only 1/3 positives.
- `ALG-0005` exactly replays all current smoke and synthetic positives, including loop and duplicate-label cases, but EXP-0010 shows this is exact observed-language memorization: held-out interleavings fail and observed noise is accepted.
- EXP-0015 shows `ALG-0013` matches `ALG-0012` on all current optional-pattern and broader synthetic replay/negative metrics. Savings are only 5-12 operations on chain-emitting cases and zero elsewhere.
- `optional_singleton_parallel_branch` broadens optional/concurrency testing: `ALG-0004`, `ALG-0011`, `ALG-0012`, and `ALG-0013` replay positives but reject only 2/3 negatives; `ALG-0010` replays 3/4 positives; `ALG-0003` replays 0/4 positives.
- `ALG-0003`, `ALG-0009`, and `ALG-0011` are `deep-testing`. `ALG-0005`, `ALG-0010`, and `ALG-0012` are `promising`. `ALG-0013` is `smoke-tested`. `ALG-0004` is `benchmarked`. No candidate is `super-promising`.

## Next action

Continue the first goal by prioritizing:

1. Search systematically for an uncertified-chain false positive, or stop the high-cost region repair line and pivot to `ALG-0005` grammar/block abstraction.
2. Refine optional/concurrency handling using the new `optional_singleton_parallel_branch` counterexample.
3. Decide whether loop support belongs as a bounded `ALG-0003` cut or a split candidate.

## Current candidate focus

- `ALG-0001`: baseline, smoke-tested.
- `ALG-0002`: dependency-threshold baseline, smoke-tested, lower operation counts but not promoted because of unconstrained-transition diagnostics.
- `ALG-0003`: deep-testing block-structured baseline; next targets are loop/duplicate-label decisions and broader optional-concurrency tests.
- `ALG-0004`: benchmarked visible-place region comparator; next decision is bounded silent optional-place refinement versus retaining as a negative comparator.
- `ALG-0005`: promising exact automaton/grammar comparator; stress-tested for overfitting and variant growth, next target is abstraction/refinement.
- `ALG-0006`: smoke-tested starter candidate, lower counted operations but not promoted because XOR replay is disproven.
- `ALG-0009`: deep-testing guarded PMIR variant; next target is conflict-aware optional guard refinement.
- `ALG-0010`: promising conflict-aware optional-chain variant; fixes overlapping optional skips but not optional/concurrency.
- `ALG-0011`: deep-testing narrow region optional-tau repair; fixes singleton and two-disjoint optional skip precision but not overlapping optional chains or optional/concurrency.
- `ALG-0012`: promising chain-aware region repair; fixes overlapping optional chains but is high-cost and does not solve optional/concurrency.
- `ALG-0013`: smoke-tested no-certification ablation of `ALG-0012`; current behavior matches `ALG-0012` with only tiny operation savings, so it is not promoted.

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
- `ALG-0004` should not be promoted without resolving optional overgeneralization or demonstrating a clear advantage over existing block/PMIR/automaton comparators.
- `ALG-0011` should not be promoted beyond `deep-testing` until overlapping optional-chain and optional/concurrency failures are repaired or formally scoped out, and its high operation cost is justified by a clear advantage.
- `ALG-0012` should not move beyond `promising` without selected-shortcut-certification ablation evidence and a clearer cost/quality advantage over `ALG-0010` or `ALG-0003`.
- EXP-0015 supplied selected-shortcut-certification ablation evidence for `ALG-0012`, but did not show a clearer cost/quality advantage; keep `ALG-0012` at `promising`.
- `ALG-0013` should remain an ablation unless counterexample search shows selected-region certification is redundant or harmful.

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
