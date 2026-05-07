# ALG-0005 — Prefix Automaton Compression Miner

## Status

promising

## One-sentence hypothesis

A prefix automaton built from variants can exactly replay observed traces, and bounded state compression can expose grammar-like blocks that compile to smaller Petri nets.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Exact observed replay is prioritized before generalization.
- Variant explosion is possible and must be measured.
- Concurrency is not inferred unless compression evidence supports it.

## Output

- Prefix trie or compressed automaton.
- Grammar/PMIR block hints.
- Petri-net JSON, initially as an accepting automaton net or compiled grammar fragments.

## Intermediate representation

Prefix automaton with node counts, terminal markers, optional suffix signatures, and compression/merge evidence.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments for variant counts, trie node lookups/inserts, set operations for signatures, comparisons for merge decisions, and construction operations for automaton/net nodes and arcs.

## Algorithm sketch

1. Insert each trace into a prefix trie and count variants.
2. Mark terminal nodes and start/end evidence.
3. Compute bounded suffix signatures bottom-up.
4. Merge nodes with identical bounded signatures when doing so preserves accepted observed traces.
5. Compile the automaton to a Petri net or grammar-like PMIR blocks.

## Expected complexity

Trie build is `O(N)`. Compression is expected around `O(P * signature_cost)` or `O(PA)` for bounded signatures, where `P` is the number of prefix states.

## Smoke tests

First gates: exact replay on `sequence.json`, `xor.json`, and `skip.json`. `parallel_ab_cd.json` is a precision/generalization gate because a trie can memorize both observed orders without discovering concurrency.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- `ALG-0008` Evolutionary Tiny-Net Search as a small-log oracle if implemented.

## Metrics

Metrics: exact replay, automaton node count, compressed node count, Petri-net size, operation counts, negative-trace precision probes, and future held-out variant behavior.

## Known failure modes

- Variant explosion.
- Overfitting and weak concurrency generalization.
- Noise preserved as valid behavior.
- Unsafe state merges if signatures are too coarse.
- Petri-net compilation may add behavior not represented in the automaton.
- Exact replay can look strong while preserving noise and failing to infer concurrency/generalization.

## Executable prototype

Implemented in `scripts/prefix_automaton_compression.py` and wired into:

- `scripts/benchmark.py`
- `scripts/alg0009_deep_tests.py`

EXP-0009 also extended the Petri-net JSON/evaluator with optional `transition_labels`, so automaton nets can use distinct transition IDs for repeated visible labels while older `t_A` transition names keep their legacy activity-label behavior.

## EXP-0009 smoke results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Ops | Replay | Negative rejection | Raw nodes | Compressed states | Edges | Merge groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| `noise.json` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `parallel_ab_cd.json` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `sequence.json` | 228 | 3/3 | 3/3 | 5 | 5 | 4 | 0 |
| `short_loop.json` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |
| `skip.json` | 175 | 4/4 | 3/3 | 5 | 4 | 4 | 1 |
| `xor.json` | 235 | 4/4 | 3/3 | 6 | 4 | 4 | 2 |

All smoke structural diagnostics were clean.

## EXP-0009 synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Ops | Replay | Negative rejection | Raw nodes | Compressed states | Edges | Merge groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| `duplicate_label_rework` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |
| `incomplete_parallel_observed_sequence` | 206 | 2/2 | 3/3 | 5 | 5 | 4 | 0 |
| `nested_xor_sequence` | 308 | 3/3 | 3/3 | 8 | 5 | 5 | 3 |
| `noise_reversal_sequence` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `overlapping_optional_skips` | 270 | 4/4 | 3/3 | 9 | 5 | 7 | 2 |
| `parallel_with_optional_branch` | 368 | 3/3 | 3/3 | 12 | 8 | 9 | 2 |
| `short_loop_required` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |

## EXP-0010 held-out and variant-explosion stress

Command: `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`

| Case | Variants | Raw nodes | Compressed states | Edges | Ops | Held-out replay | Negative rejection |
|---|---:|---:|---:|---:|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | 2 | 9 | 7 | 7 | 315 | 0/4 | 3/3 |
| `heldout_parallel_balanced_2_of_6` | 2 | 10 | 8 | 8 | 328 | 0/4 | 3/3 |
| `heldout_optional_concurrency` | 3 | 12 | 8 | 9 | 368 | 0/2 | 3/3 |
| `noise_memorization` | 2 | 8 | 6 | 6 | 281 | 0/0 | 0/1 |
| `all_permutations_width_2` | 2 | 8 | 6 | 6 | 237 | 0/0 | 3/3 |
| `all_permutations_width_3` | 6 | 23 | 10 | 14 | 555 | 0/0 | 3/3 |
| `all_permutations_width_4` | 24 | 90 | 18 | 34 | 1732 | 0/0 | 3/3 |
| `all_permutations_width_5` | 120 | 447 | 34 | 82 | 8258 | 0/0 | 3/3 |

Interpretation:

- Exact automaton replay rejects held-out valid interleavings by construction.
- `ALG-0003` accepted 4/4 held-out traces for `heldout_parallel_balanced_2_of_6` and 2/2 for `heldout_optional_concurrency`, showing a concrete generalization advantage over `ALG-0005`.
- `noise_memorization` confirms that observed rare/noisy behavior is preserved as accepted behavior.
- Full-permutation stress shows raw trie nodes and operation counts grow quickly with variants even though suffix compression reduces the state count.

## Promotion criteria

Promoted to `promising` after EXP-0009 because it has:

- exact observed replay on all smoke logs in its claimed scope;
- compression improves compactness over a raw trace net;
- operation counts remain near-linear for trie construction;
- negative-trace tests document precision/generalization tradeoffs.

It is not `deep-testing` yet. EXP-0010 started counterexample search and documented exact-replay overfitting, but a refined variant or ablation is still required before deep-testing. Next evidence should include bounded suffix-depth merging, grammar block extraction, or another explicit abstraction step plus a language-preservation argument.

## Experiment links

- EXP-0003: specified as the prefix-automaton/grammar-to-net family.
- EXP-0009: implemented and promoted to `promising`; not `deep-testing`.
- EXP-0010: held-out and variant-explosion stress tests document overfitting and variant growth; remains `promising`.

## Property-study notes

Potential future dossier topics: exact replay by trie construction, language preservation under safe state merges, and complexity of bounded-signature compression.

## Decision history

- EXP-0003: specified as the prefix-automaton/grammar-to-net family.
- EXP-0009: implemented suffix-signature compression and automaton-to-Petri-net compilation with labeled visible transitions.
- EXP-0010: stress tests show exact replay does not generalize to held-out interleavings and memorizes noisy observed variants.
