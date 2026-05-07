# ALG-0010 — PMIR Conflict-Aware Optional Chain Compiler

## Status

promising

## One-sentence hypothesis

Optional behavior should be compiled from conflict-aware chain shortcuts rather than from every local optional triple, reducing overlapping optional-place contradictions while preserving the guarded PMIR compiler path.

## Input assumptions

- Log is a list of traces over unique activity labels.
- Optional behavior is represented by causal shortcuts over an otherwise ordered chain.
- A candidate optional chain is rejected if observed traces contradict the chain order.
- Short loops, duplicate labels, and optional behavior embedded inside concurrency are not handled completely.

## Output

- PMIR relation graph with transitive-reduction edges, optional-chain candidates, accepted optional chains, rejected chains, XOR groups, residual edge places, and covered edges.
- Petri-net JSON with visible transitions and silent `tau_` transitions for accepted optional-chain shortcuts.

## Intermediate representation

PMIR conflict-aware chain evidence:

- `transitive_reduction_edges`: causal edges after shortcut removal.
- `optional_chain_candidates`: maximal reduced paths of length at least three.
- `optional_chains`: accepted chains with direct chain edges and shortcut skip transitions.
- `rejected_chains`: candidates rejected because they have no shortcuts, overlap another chain, are disabled, or violate observed order.
- `split_groups` and `join_groups`: residual XOR guards after optional-chain coverage.
- `edge_places`: residual causal edges.

## Allowed Operations / Operation-Cost Model

Uses `scan_event`, `dict_increment`, `set_insert`, `set_lookup`, `comparison`, `relation_classification`, and `construct`. The transitive-reduction and chain-selection steps add graph-search comparisons and set operations, but no solver or matrix operations.

Evaluator silent-closure work is not discovery cost.

## Algorithm Sketch

1. Scan the log and classify Alpha-Lite pairwise relations.
2. Build causal incoming/outgoing maps and the causal edge set.
3. Build eventual-order evidence from trace positions.
4. Compute a simple transitive reduction of the causal graph.
5. Extract maximal linear reduced paths as optional-chain candidates.
6. Accept a chain only if it has at least one causal shortcut, has no observed reverse-order evidence, and does not overlap a longer selected chain.
7. Compile accepted chains as places between consecutive activities plus silent skip transitions for shortcut edges.
8. Run residual XOR grouping and residual edge-place emission.

## Expected Complexity

`O(N * L + A^2 + D^2 + path_checks + local_branch_checks)`, where `L` is trace length and `D` is causal-edge count. The first prototype is intentionally conservative and more expensive than `ALG-0009`; it is a refinement probe, not yet the preferred low-operation implementation.

## Smoke Tests

Executed in EXP-0006 on all toy logs with positive replay, negative-trace probes, and structural diagnostics.

- Full replay and full negative rejection: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `skip.json`, `noise.json`.
- Failed scope: `short_loop.json` replay 1/3 and negative rejection 1/3.

## Deep Tests

EXP-0006 synthetic results:

- `overlapping_optional_skips`: improves from `ALG-0009` 1/4 replay to 4/4 while rejecting 3/3 negative probes.
- `nested_xor_sequence`, `incomplete_parallel_observed_sequence`, and `noise_reversal_sequence`: full replay and full negative rejection.
- `parallel_with_optional_branch`: regresses to 0/3 replay, showing optional/concurrency interaction is still unresolved.
- `short_loop_required` and `duplicate_label_rework`: remain 1/3 replay and 1/3 negative rejection.
- Trace-order signatures were stable on checked permutations.

## Baselines for Comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- `ALG-0006` PMIR Split-Join Compiler Lite.
- `ALG-0009` PMIR Guarded Split-Join Compiler.

## Metrics

EXP-0006 measured operation counts, structural counts, silent-transition counts, replay, negative-trace rejection, visible-transition diagnostics, PMIR chain evidence, and trace-order stability.

## Known Failure Modes

- More counted operations than `ALG-0009` on all smoke logs.
- Optional behavior embedded inside concurrency can be worse than `ALG-0009`.
- Short loops and duplicate labels remain unresolved.
- The transitive-reduction heuristic is local and not a proof of block structure.
- It can still emit residual XOR groups that are inappropriate under concurrency.

## Promotion Criteria

Promoted to `promising` in EXP-0006 because it:

- has a deterministic prototype and written specification;
- records operation counts;
- passes five of six toy smoke families;
- fixes the overlapping optional-skips counterexample that broke `ALG-0009`;
- exposes a useful PMIR chain abstraction for optional behavior.

Further promotion requires a strategy for optional/concurrency interaction, operation-cost reduction, and comparison against `ALG-0003`.

## Experiment Links

- EXP-0006 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.
- `experiments/alg0009-deep-tests.json`.

## Property-Study Notes

Potential future properties:

- sufficient conditions for optional-chain replay preservation;
- correctness of shortcut-to-silent-transition compilation for linear chains;
- counterexamples where transitive reduction misidentifies block structure.

No property dossier yet; this candidate is not `super-promising`.

## Decision History

- EXP-0006: implemented as a split refinement from `ALG-0009`; promoted to `promising` with explicit scope limits.
