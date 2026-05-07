# ALG-0002 — Frequency-Threshold Dependency Graph

## Status

smoke-tested

## One-sentence hypothesis

A low-operation dependency graph that filters direct-follows edges by frequency and directional dependency score can reduce noisy edge effects while remaining cheaper than Alpha-style bounded subset search.

## Input assumptions

- Log is a list of traces.
- Each trace is an ordered list of activity labels.
- Rare but valid behavior may be filtered when support is below `min_count`.
- Duplicate labels, short loops, and silent behavior are not handled specially.

## Output

- PMIR dependency graph with DFG counts, accepted dependency edges, scores, thresholds, and grouped place evidence.
- Petri-net JSON compiled from grouped dependency edges and individual edge places.

## Intermediate representation

Dependency-graph PMIR: activities, start/end counts, direct-follows counts, accepted dependency edges, dependency scores, and local grouped place candidates.

## Allowed operations / operation-cost model

Uses `scan_event`, `dict_increment`, `set_insert`, `set_lookup`, `comparison`, `arithmetic`, `relation_classification`, and `construct`. The implemented dependency score counts arithmetic operations explicitly.

## Algorithm sketch

1. Scan traces to collect activities, start/end counts, and direct-follows counts.
2. For every ordered activity pair, compute `(count(a,b) - count(b,a)) / (count(a,b) + count(b,a) + 1)`.
3. Keep edges whose support is at least `min_count` and whose score is at least `dependency_threshold`.
4. Group local XOR alternatives when branch activities are never observed to follow each other.
5. Compile grouped places and remaining edge places to a Petri net.

## Expected complexity

Implemented full-pair version: `O(N + A^2 + local_branch_checks)`.

An observed-edge-only variant could reduce relation scoring toward `O(N + D)` but has not been implemented.

## Smoke tests

Executed in EXP-0003 on sequence, XOR, parallel, short-loop, skip, and noise logs. Results:

- Full replay: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `noise.json`.
- Partial replay: `skip.json` 2/4, `short_loop.json` 1/3.
- Structural diagnostics: `noise.json` contains unconstrained visible transitions `t_C` without input and `t_B` without output.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0006` PMIR Split-Join Compiler Lite.
- Future: threshold sweeps and PM4Py/ProM-style heuristics miner if dependencies are accepted.

## Metrics

Initial metrics: operation counts, strict token-game replay, structural counts, and visible-transition input/output diagnostics.

## Known failure modes

- Thresholds can erase valid low-frequency behavior and produce under-constrained visible transitions.
- Replay can look good because unconstrained transitions float through the token game.
- Short loops remain unresolved when reverse evidence cancels dependency scores.
- Skip behavior is over-constrained by edge places.
- Parameter sensitivity is expected.

## Promotion criteria

Can become `promising` only after:

- threshold sweep is recorded;
- replay success is not caused by unconstrained visible transitions;
- noise behavior improves over `ALG-0001` without losing intended rare behavior;
- operation counts remain lower than the Alpha-style baseline;
- failure cases and recommended threshold ranges are documented.

## Experiment links

- EXP-0003 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.

## Property-study notes

No property dossier. Potential future properties include deterministic dependency scoring, operation bounds, and sufficient conditions for edge-filter soundness.

## Decision history

- EXP-0003: implemented and smoke-tested. Not promoted because structural diagnostics found unconstrained transitions on the noise log.
