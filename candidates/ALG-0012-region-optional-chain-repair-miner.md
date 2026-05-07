# ALG-0012 — Region Optional-Chain Repair Miner

## Status

promising

## One-sentence hypothesis

Selected bounded-region shortcut places can certify optional-chain repairs, allowing a region-based miner to handle overlapping optional skips without accepting arbitrary local optional triples.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Base visible region candidates use `ALG-0004` with `k <= 2`.
- Optional-chain candidates are extracted from transitive reduction over causal edges.
- A chain is emitted only if it is order-consistent and has at least one shortcut edge selected by the bounded region miner.

## Output

- PMIR evidence containing selected region places, selected shortcut edges, optional-chain candidates, rejected chains, and emitted optional-chain fragments.
- Petri-net JSON with selected visible region places plus `tau_skipchain_*` transitions for chain shortcuts.

## Intermediate representation

Visible place-candidate table plus order-consistent optional chains certified by selected singleton shortcut places.

## Allowed operations / operation-cost model

Uses the `ALG-0004` bounded region operations plus eventual-order scans, transitive-reduction path checks, optional-chain selection, selected-shortcut filtering, and construction operations for optional-chain places and silent skip transitions.

## Algorithm sketch

1. Run bounded visible-place enumeration and greedy selection from `ALG-0004`.
2. Build causal edges from the relation summary.
3. Compute eventual-before evidence and a simple transitive reduction.
4. Extract path chains from the reduced graph.
5. Select order-consistent chains with shortcut evidence.
6. Keep only chains whose shortcut evidence intersects selected singleton region shortcuts.
7. Compile selected visible region places, then add optional-chain places and `tau` shortcuts.

## Expected complexity

`O(N + P + A^(2k) * P * k + N * L + A^2 + D^2 + path_checks)` with fixed `k`; this is intentionally higher than `ALG-0011` because it uses chain detection and eventual-order evidence.

## Smoke tests

First gate: `overlapping_optional_chain` / `overlapping_optional_skips`, where `ALG-0011` rejects all chain candidates and overgeneralizes.

Broader gates: all smoke logs, optional-pattern tests, and synthetic cases in `scripts/alg0009_deep_tests.py`.

## Likely failure modes

- Higher operation cost than `ALG-0011`, `ALG-0010`, and `ALG-0003`.
- Optional behavior inside concurrency remains unresolved when chain order is contradicted by interleavings.
- Inherits `ALG-0004` loop and duplicate-label limitations.
- Chain fragments are empirically replay-tested but not yet proven sound or safe.

## EXP-0014 smoke results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `noise.json` | 1461 | 4/4 | 3/3 | 0 |
| `parallel_ab_cd.json` | 1437 | 4/4 | 3/3 | 0 |
| `sequence.json` | 890 | 3/3 | 3/3 | 0 |
| `short_loop.json` | 357 | 1/3 | 3/3 | 0 |
| `skip.json` | 432 | 4/4 | 3/3 | 1 |
| `xor.json` | 844 | 4/4 | 3/3 | 0 |

## EXP-0014 optional-pattern comparison

Command: `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`

| Case | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `singleton_optional_skip` | 432 | 4/4 | 3/3 | 1 |
| `two_disjoint_optional_skips` | 1648 | 4/4 | 3/3 | 1 |
| `overlapping_optional_chain` | 1037 | 4/4 | 3/3 | 1 |
| `optional_inside_parallel` | 1815 | 3/3 | 1/3 | 0 |

## EXP-0015 selected-shortcut-certification ablation

Command: `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`

`ALG-0013` disables selected-shortcut certification while keeping order-consistent optional-chain selection. On current optional-pattern cases it matches `ALG-0012` replay and negative rejection, with only tiny operation savings:

| Case | ALG-0012 ops / replay / neg reject | ALG-0013 ops / replay / neg reject |
|---|---:|---:|
| `singleton_optional_skip` | 432 / 4/4 / 3/3 | 427 / 4/4 / 3/3 |
| `two_disjoint_optional_skips` | 1648 / 4/4 / 3/3 | 1636 / 4/4 / 3/3 |
| `overlapping_optional_chain` | 1037 / 4/4 / 3/3 | 1026 / 4/4 / 3/3 |
| `optional_inside_parallel` | 1815 / 3/3 / 1/3 | 1815 / 3/3 / 1/3 |
| `optional_singleton_parallel_branch` | 1008 / 4/4 / 2/3 | 1008 / 4/4 / 2/3 |

The ablation does not justify replacing the certified variant because the current savings are small and no broader counterexample search has shown certification to be redundant.

## EXP-0014 broader synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `duplicate_label_rework` | 357 | 1/3 | 3/3 | 0 |
| `incomplete_parallel_observed_sequence` | 754 | 2/2 | 3/3 | 0 |
| `nested_xor_sequence` | 1515 | 3/3 | 3/3 | 0 |
| `noise_reversal_sequence` | 1461 | 4/4 | 3/3 | 0 |
| `overlapping_optional_skips` | 1037 | 4/4 | 3/3 | 1 |
| `parallel_with_optional_branch` | 1815 | 3/3 | 1/3 | 0 |
| `short_loop_required` | 357 | 1/3 | 3/3 | 0 |

## Promotion criteria

Promoted to `promising` in EXP-0014 because:

- deterministic executable prototype in `scripts/region_optional_chain_miner.py`;
- written specification and explicit operation model;
- measured operation counts;
- fixes `ALG-0011`'s overlapping optional-chain failure while preserving smoke replay;
- provides a clear comparison point against `ALG-0010` chain compilation.

It remains at `promising` after EXP-0015. The internal ablation is now implemented, but it did not establish a clearer cost/quality advantage over `ALG-0010` or `ALG-0003`; optional/concurrency, loop, duplicate-label, and high-cost limitations remain material.

## Experiment links

- EXP-0013: `ALG-0011` no-repair ablation showed overlapping optional chains were still unrepaired.
- EXP-0014: this chain-aware region repair fixes overlapping optional chains but not optional/concurrency.
- EXP-0015: selected-shortcut-certification ablation (`ALG-0013`) matches current behavior with only tiny operation-count savings.

## Property-study notes

Potential future dossier topics if promoted further: replay preservation of selected region shortcuts plus chain fragments, soundness of optional-chain fragments, and conditions under which order-consistency prevents concurrency overconstraint.

## Decision history

- EXP-0014: implemented and promoted to `promising`; retained as chain-aware region comparator, not a general optional/concurrency solution.
- EXP-0015: kept at `promising`; ablation evidence does not support deeper promotion.
