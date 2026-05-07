# ALG-0001 — Alpha-Lite Relations

## Status

smoke-tested

## One-sentence hypothesis

A low-cost direct-follows scan plus Alpha-style relation classification can recover basic sequence, choice, and concurrency structures well enough to serve as a transparent baseline.

## Input assumptions

- Log is a list of traces.
- Each trace is an ordered list of activity labels.
- No duplicate labels are handled specially.
- Short loops and noisy directly-follows relations are expected failure cases.

## Output

- PMIR relation graph.
- Petri-net JSON with places, transitions, arcs, initial marking, and final marking.

## Intermediate representation

PMIR with activities, start/end counts, direct-follows counts, pairwise relation labels, and maximal Alpha-style preset/postset pairs.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments, set inserts/lookups, comparisons, relation classifications, and construction operations.

## Algorithm sketch

1. Scan traces to collect activities, start/end counts, and direct-follows counts.
2. Classify pairwise relations as causal, parallel, unrelated, self-loop, or reverse-causal.
3. Enumerate small candidate preset/postset pairs up to `max_pair_set_size`.
4. Keep pairs where all preset activities causally precede all postset activities and members inside each side are mutually unrelated.
5. Remove subsumed pairs.
6. Compile places/arcs to a Petri net.

## Expected complexity

For activity count `a`, pair enumeration is bounded by subsets up to size `k`; current default `k=2`. The full Alpha search can become expensive as `k` grows, which makes this a baseline rather than the preferred limited-operation candidate.

## Smoke tests

Executed in EXP-0001 on toy sequence, XOR, parallel, loop, skip, and noise logs.

## Baselines for comparison

- ALG-0006 PMIR Split-Join Compiler Lite.
- Future: PM4Py Alpha Miner / Inductive Miner / Heuristics Miner if installed.

## Metrics

Initial metrics: operation counts and structural counts only. Need replay/fitness and semantic checks.

## Known failure modes

- Short loops.
- Noise creates false parallelism.
- Duplicate labels.
- Potential over/under-generalization not yet measured.

## Promotion criteria

Not intended for promotion except as a baseline. Could become promising only if the bounded-pair variant shows a useful operation-quality tradeoff.

## Experiment links

- EXP-0001 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.

## Property-study notes

No property claims yet.

## Decision history

- Scaffold: implemented as starter baseline.
- EXP-0001: smoke-tested; kept as baseline.
