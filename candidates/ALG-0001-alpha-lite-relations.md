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

For event count `N`, activity count `A`, bounded subset size `k`, and raw candidate-pair count `C`, expected cost is `O(N + A^2 + A^(2k) + C^2)`. Current default `k=2`. The full Alpha search can become expensive as `k` grows, which makes this a baseline rather than the preferred limited-operation candidate.

## Smoke tests

Executed in EXP-0001 on toy sequence, XOR, parallel, loop, skip, and noise logs. Rerun with strict token-game replay in EXP-0003:

- Full replay: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `noise.json`.
- Partial replay: `skip.json` 2/4 and `short_loop.json` 1/3.

## Baselines for comparison

- ALG-0006 PMIR Split-Join Compiler Lite.
- Future: PM4Py Alpha Miner / Inductive Miner / Heuristics Miner if installed.

## Metrics

Initial EXP-0001 metrics were operation counts and structural counts only. EXP-0003 adds strict token-game replay and structural diagnostics.

## Known failure modes

- Short loops.
- Noise creates false parallelism.
- Duplicate labels.
- Potential over/under-generalization not yet measured.
- Optional skips are over-constrained by separate `A -> B`, `A -> C`, and `B -> C` places.

## Promotion criteria

Not intended for promotion except as a baseline. Could become promising only if the bounded-pair variant shows a useful operation-quality tradeoff.

## Experiment links

- EXP-0001 in `research/EXPERIMENT_LOG.md`.
- EXP-0003 in `research/EXPERIMENT_LOG.md`.
- EXP-0004 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.

## Property-study notes

No property claims yet.

## Decision history

- Scaffold: implemented as starter baseline.
- EXP-0001: smoke-tested; kept as baseline.
- EXP-0003: validated with strict token-game replay; not promoted because skip and short-loop gates fail and precision is unmeasured.
- EXP-0004: negative probes added; kept as unpromoted baseline because skip and short-loop behavior remain partial.
