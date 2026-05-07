# ALG-0003 — Cut-Limited Process Tree Miner

## Status

specified

## One-sentence hypothesis

A bounded menu of DFG cut tests can discover simple block-structured process trees and compile them to sound Petri nets with predictable operation cost.

## Input assumptions

- Log is a list of traces over activity labels.
- Target behavior is approximately block-structured.
- Duplicated labels and non-local dependencies are out of first-iteration scope.
- Noise must be filtered or treated as a failed cut, not silently accepted.

## Output

- Process tree with sequence, XOR, parallel, optional/skip, and later loop nodes.
- Petri-net JSON compiled from the process tree.

## Intermediate representation

Process tree, optionally backed by PMIR DFG summaries and cut evidence.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments, set inserts/lookups, comparisons, relation classifications for cut decisions, arithmetic only for optional support scores, and construction operations for tree/net nodes.

## Algorithm sketch

1. Build DFG, start/end counts, and activity set.
2. Try deterministic cut tests in a fixed order: sequence, XOR, parallel, optional/skip.
3. Recurse on induced sublogs only when a cut is accepted.
4. Fall back to a flower or directly-follows fragment when no cut is found.
5. Compile process tree blocks to Petri-net fragments.

## Expected complexity

Expected `O(N + A^2 + recursive_cut_checks)`. With bounded deterministic cuts and simple partition checks, target first prototype is approximately `O(N + A^3)`.

## Smoke tests

First gates: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, and `skip.json`. `short_loop.json` is a gate only after a loop-cut rule is specified; `noise.json` is a robustness gate.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- Future external inductive miner if dependencies are accepted.

## Metrics

Planned metrics: replay, structural soundness by construction, operation counts per cut attempt, tree size, and fallback frequency.

## Known failure modes

- Non-block-structured logs.
- Noise-induced false cuts.
- Missing behavior causing wrong XOR/parallel decisions.
- Duplicate labels.
- Loop cuts that overgeneralize.

## Promotion criteria

Can become `promising` only after a deterministic prototype:

- compiles valid Petri nets from process trees;
- replays at least sequence, XOR, parallel, and skip smoke logs;
- records cut-operation counts;
- has a clear fallback behavior;
- has a soundness-by-construction claim scoped to accepted block nodes.

## Experiment links

- Specified during EXP-0003; no executable result yet.

## Property-study notes

This is the most likely family for future formal workflow-net soundness claims, but no dossier is justified until an executable prototype passes smoke gates.

## Decision history

- EXP-0003: specified as the inductive/process-tree baseline family.
