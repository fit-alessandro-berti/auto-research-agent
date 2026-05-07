# CONTINUITY.md

## Active goal

None yet. Suggested first active goal: `GOALS/first-petri-net-limited-ops.md`.

## Current status

Repository scaffold initialized and initial smoke benchmark executed for two starter candidates.

## Last completed actions

- Created process-mining research-agent scaffold.
- Added candidate registry, evaluation protocol, property-study protocol, and smoke-test harness.
- Implemented `ALG-0001` Alpha-Lite Relations baseline.
- Implemented `ALG-0006` PMIR Split-Join Compiler Lite starter candidate.
- Ran `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.

## Initial smoke result

Both executable candidates ran on all toy logs. `ALG-0006` used fewer counted operations than `ALG-0001` in the initial harness, but semantic validation is not yet implemented. `ALG-0006` produced more places/arcs than `ALG-0001` on the XOR smoke log, which needs inspection.

## Next action

Run the first goal in `GOALS/first-petri-net-limited-ops.md`. Prioritize:

1. Add replay/fitness or token-game checks.
2. Create detailed candidate files for `ALG-0001` and `ALG-0006`.
3. Inspect XOR, short-loop, skip, and noise behavior.
4. Decide whether `ALG-0006` deserves `promising` status after semantic checks.

## Current candidate focus

- `ALG-0001`: baseline, smoke-tested.
- `ALG-0006`: implemented starter candidate, lower counted operations in EXP-0001 but not promoted.

## Decisions to preserve

- Keep the agent generic across process-mining research topics.
- For the first task, use Petri-net discovery under a limited-operation model as a concrete benchmark.
- Every candidate algorithm must be tracked, including failed and retired candidates.
- Do not promote `ALG-0006` without replay/semantic validation.

## Blockers / unknowns

- Need to define exact operation-budget thresholds, not just counts.
- Need a semantic evaluator for generated Petri nets.
- Need to decide whether to install PM4Py/ProM for standard metrics or keep early prototypes dependency-free.

## Resume checklist

1. Read `AGENTS.md`.
2. Read this file.
3. Read `MEMORY.md` and `PLAN.md`.
4. Read `research/ALGORITHM_REGISTRY.md` and `research/EXPERIMENT_LOG.md`.
5. Continue from `Next action` unless the user gives a new goal.
