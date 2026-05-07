# CONTINUITY.md

## Active goal

`GOALS/first-petri-net-limited-ops.md`.

## Current status

First research iteration complete. The registry now tracks six fully specified first-goal candidate families, three executable smoke-tested prototypes, explicit operation primitives, strict token-game replay diagnostics, and promotion decisions.

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

## Latest smoke result

EXP-0003 executable-candidate replay summary:

| Log | ALG-0001 ops / replay | ALG-0002 ops / replay | ALG-0006 ops / replay |
|---|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 | 214 / 4 of 4 | 208 / 4 of 4 |
| `parallel_ab_cd.json` | 544 / 4 of 4 | 240 / 4 of 4 | 208 / 4 of 4 |
| `sequence.json` | 499 / 3 of 3 | 211 / 3 of 3 | 181 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 | 118 / 1 of 3 | 110 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 | 144 / 2 of 4 | 132 / 2 of 4 |
| `xor.json` | 552 / 4 of 4 | 228 / 4 of 4 | 204 / 0 of 4 |

Semantic and structural interpretation:

- `ALG-0006` has a real XOR replay failure, not just a structural-count anomaly.
- `ALG-0002` has lower operation counts but can leave visible transitions unconstrained, so replay fitness alone is misleading.
- All executable candidates fail short-loop and skip behavior under the current strict final-marking token game.

## Next action

Continue the first goal by prioritizing:

1. Repair or variant-split `ALG-0006` to avoid XOR and skip over-constraint.
2. Add negative-trace precision probes so unconstrained transitions are caught as behavior, not just diagnostics.
3. Run an `ALG-0002` threshold sweep on noise/rare-behavior logs.
4. Implement `ALG-0003` Cut-Limited Process Tree Miner as the next baseline.

## Current candidate focus

- `ALG-0001`: baseline, smoke-tested.
- `ALG-0002`: dependency-threshold baseline, smoke-tested, lower operation counts but not promoted because of unconstrained-transition diagnostics.
- `ALG-0006`: smoke-tested starter candidate, lower counted operations but not promoted because XOR replay is disproven.

## Decisions to preserve

- Keep the agent generic across process-mining research topics.
- For the first task, use Petri-net discovery under a limited-operation model as a concrete benchmark.
- Every candidate algorithm must be tracked, including failed and retired candidates.
- Do not promote `ALG-0006` without replay/semantic validation.
- Do not promote any candidate on positive-trace replay alone; structural diagnostics and negative traces are required.

## Blockers / unknowns

- Need to define exact operation-budget thresholds, not just counts.
- Need to decide whether to install PM4Py/ProM for standard metrics or keep early prototypes dependency-free.
- Need negative-trace precision tests and at least one non-trivial synthetic benchmark before any `super-promising` decision.

## Resume checklist

1. Read `AGENTS.md`.
2. Read this file.
3. Read `MEMORY.md` and `PLAN.md`.
4. Read `research/ALGORITHM_REGISTRY.md` and `research/EXPERIMENT_LOG.md`.
5. Continue from `Next action` unless the user gives a new goal.
