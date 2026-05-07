# ALG-0014 — Prefix Block Abstraction Miner

## Status

promising

## One-sentence hypothesis

A small common-boundary grammar abstraction can reduce `ALG-0005` overfitting by compiling observed middle-segment permutations as blocks before falling back to exact automaton replay.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Labels are treated as unique activity identities for block abstraction; duplicate-label cases fall back to exact automaton replay.
- The first abstraction pass is intentionally shallow: one common-prefix/common-suffix middle block per log.
- Parallel abstraction requires observed order variation, not a single observed order.

## Output

- PMIR evidence containing selected grammar, grammar attempts, and fallback automaton evidence when no block grammar is accepted.
- Petri-net JSON compiled either from a block grammar or from the exact prefix automaton fallback.

## Intermediate Representation

Prefix-derived grammar with two block forms:

- `parallel_block`: every middle segment has the same activity set and at least two orders are observed.
- `optional_singleton_parallel`: one mandatory singleton branch and one optional singleton branch are observed in both relative orders, with at least one optional-absent trace.

If neither form is accepted, the intermediate representation is the exact compressed prefix automaton from `ALG-0005`.

## Allowed Operations / Operation-Cost Model

Uses the first-goal primitive operations: event scans, set lookups/inserts, comparisons, relation classifications, dictionary increments, and construction operations.

Abstraction path: `O(N + A^2 + T * L^2 + B)` for summarization, relation classification, common-boundary checks, segment-set checks, and block construction, where `B` is emitted block size.

Fallback path: abstraction checks plus `ALG-0005` exact automaton cost `O(P * signature_cost + P + E)`.

## Algorithm Sketch

1. Summarize starts, ends, DFG counts, and relation evidence.
2. Compute common prefix, common suffix, and middle segments.
3. Try `parallel_block`.
4. Try `optional_singleton_parallel`.
5. Compile the accepted block grammar to a Petri net.
6. If no grammar is accepted, fall back to the compressed prefix automaton.

## Smoke Tests

First gate: `scripts/alg0005_stress_tests.py`, especially held-out parallel interleavings and noise memorization.

Broader gates: toy logs via `scripts/benchmark.py`, synthetic cases via `scripts/alg0009_deep_tests.py`, and optional-pattern cases via `scripts/alg0011_optional_tests.py`.

## Baselines for Comparison

- `ALG-0005` exact prefix automaton.
- `ALG-0003` cut-limited process tree.
- `ALG-0010` conflict-aware optional-chain PMIR.
- Region variants `ALG-0011` and `ALG-0012` on optional-pattern cases.

## Metrics

- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation counts.
- Selected grammar.
- Structural diagnostics.

## Known Failure Modes

- Prefix-biased partial parallel evidence remains too narrow: if all training variants share a first branch, that branch becomes part of the common prefix and held-out interleavings moving it later are rejected.
- Rare reversal noise can be interpreted as a parallel block, preserving the `ALG-0005` noise-memorization problem in a different form.
- Duplicate-label and loop cases currently fall back to exact automaton replay, so success there is memorization rather than process generalization.
- The grammar is shallow and detects only one block.

## EXP-0016 Smoke Results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Ops | Replay | Negative rejection |
|---|---:|---:|---:|
| `noise.json` | 235 | 4/4 | 3/3 |
| `parallel_ab_cd.json` | 227 | 4/4 | 3/3 |
| `sequence.json` | 272 | 3/3 | 3/3 |
| `short_loop.json` | 248 | 3/3 | 3/3 |
| `skip.json` | 216 | 4/4 | 3/3 |
| `xor.json` | 294 | 4/4 | 3/3 |

## EXP-0016 Stress Results

Command: `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`

| Case | Grammar | Ops | Train replay | Held-out replay | Negative rejection |
|---|---|---:|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | `parallel_block` | 254 | 2/2 | 0/4 | 3/3 |
| `heldout_parallel_balanced_2_of_6` | `parallel_block` | 257 | 2/2 | 4/4 | 3/3 |
| `heldout_optional_concurrency` | `exact_prefix_automaton` | 447 | 3/3 | 0/2 | 3/3 |
| `noise_memorization` | `parallel_block` | 235 | 4/4 | 0/0 | 0/1 |
| `all_permutations_width_2` | `parallel_block` | 183 | 2/2 | 0/0 | 3/3 |
| `all_permutations_width_3` | `parallel_block` | 363 | 6/6 | 0/0 | 3/3 |

## EXP-0016 Optional-Pattern Results

Command: `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`

| Case | Ops | Replay | Negative rejection |
|---|---:|---:|---:|
| `singleton_optional_skip` | 216 | 4/4 | 3/3 |
| `two_disjoint_optional_skips` | 448 | 4/4 | 3/3 |
| `overlapping_optional_chain` | 333 | 4/4 | 3/3 |
| `optional_inside_parallel` | 447 | 3/3 | 3/3 |
| `optional_singleton_parallel_branch` | 278 | 4/4 | 3/3 |

## Promotion Criteria

Promoted to `promising` in EXP-0016 because:

- deterministic executable prototype in `scripts/prefix_block_abstraction.py`;
- written specification and operation model;
- passes toy smoke replay/negative probes;
- measures operation counts;
- improves over `ALG-0005` on balanced held-out parallel interleavings;
- fixes the `optional_singleton_parallel_branch` counterexample where `ALG-0003`, `ALG-0010`, and region variants each fail one metric.

It is not `deep-testing` because the noise and prefix-bias failures are material and the grammar is still shallow.

## Experiment Links

- EXP-0010: `ALG-0005` stress tests showed held-out overfitting and noise memorization.
- EXP-0015: added `optional_singleton_parallel_branch` as a durable optional/concurrency counterexample.
- EXP-0016: implemented this grammar/block refinement.

## Property-Study Notes

No property dossier. The candidate is not `super-promising`; it needs support thresholds, incompleteness guards, and deeper block composition before formal study.

## Decision History

- EXP-0016: implemented and promoted to `promising`; retained as a grammar-abstraction direction with explicit noise and prefix-bias counterexamples.
