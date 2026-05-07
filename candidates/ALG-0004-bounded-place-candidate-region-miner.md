# ALG-0004 — Bounded Place-Candidate Region Miner

## Status

specified

## One-sentence hypothesis

A bounded, solver-free search over small place presets and postsets can recover useful Petri-net places that relation miners miss while keeping the operation budget explicit.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Candidate preset/postset size is bounded by a small fixed `k`, initially `k <= 2`.
- Places are accepted by deterministic replay/enablement constraints over observed prefixes.
- No external ILP solver is used in the limited-operation prototype.

## Output

- PMIR place-candidate table with accepted/rejected constraints.
- Petri-net JSON compiled from accepted places.

## Intermediate representation

Prefix-state abstraction plus bounded place candidates with token-balance, enablement, and final-marking evidence.

## Allowed operations / operation-cost model

Uses event scans, prefix-state construction, set inserts/lookups, bounded preset/postset enumeration, comparisons for enablement/token balance, arithmetic for token deltas, and construction operations.

## Algorithm sketch

1. Build prefix states or replay checkpoints for the log.
2. Enumerate candidate `(preset, postset)` pairs up to size `k`.
3. Simulate token balance of each candidate over observed trace prefixes.
4. Reject places that block observed events or leave impossible final residue.
5. Keep a minimal non-redundant subset of accepted places.
6. Add source/sink places and compile to Petri-net JSON.

## Expected complexity

`O(N + P + A^(2k) * P * k)` with fixed `k`; candidate explosion is expected if `k` grows.

## Smoke tests

First gates: `sequence.json`, then `xor.json` and `parallel_ab_cd.json`; all six logs become gates once replay constraints are implemented.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0006` PMIR Split-Join Compiler Lite.
- Future region/ILP miner if dependencies are accepted.

## Metrics

Planned metrics: accepted/rejected candidate counts, replay, structural diagnostics, operation counts by enumeration and constraint check, and place redundancy.

## Known failure modes

- Candidate explosion for larger `k`.
- Underfitting for too-small `k`.
- Noise and incompleteness overfit constraints.
- Accepted places can still over-constrain unseen but valid behavior.
- Soundness is not guaranteed by local constraints alone.

## Promotion criteria

Can become `promising` only after:

- `k <= 2` prototype runs on all smoke logs;
- observed replay is at least as good as Alpha-Lite on skip/loop counterexamples or reveals why not;
- operation counts are explicit by candidate enumeration and constraint checks;
- accepted places provide a concrete advantage or useful counterexample evidence.

## Experiment links

- Specified during EXP-0003; no executable result yet.

## Property-study notes

Potential future dossier topics: replay preservation for accepted places, bounded enumeration complexity, and counterexamples to local-place soundness.

## Decision history

- EXP-0003: specified as the region/ILP-inspired comparator without using an ILP solver.
