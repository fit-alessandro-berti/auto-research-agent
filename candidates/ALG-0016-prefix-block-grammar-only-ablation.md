# ALG-0016 — Prefix Block Grammar-Only Ablation

## Status

smoke-tested

## One-sentence hypothesis

Disabling exact fallback separates true grammar generalization from exact automaton memorization in `ALG-0015`.

## Input Assumptions

- Same grammar detectors and support guards as `ALG-0015`.
- Exact automaton fallback is disabled.
- If no grammar is selected, the emitted net is a base rejecting net over the observed activity set.

## Output

- PMIR evidence with `allow_exact_fallback=false`.
- Petri net compiled from a selected grammar, or a no-grammar rejecting net.

## Intermediate Representation

Support-guarded block grammar only:

- `parallel_block`
- `optional_singleton_parallel`
- `dominant_sequence`
- `no_grammar`

## Allowed Operations / Operation-Cost Model

Same grammar operation model as `ALG-0015`, minus exact automaton construction.

## Algorithm Sketch

1. Run the `ALG-0015` grammar detectors.
2. Compile a selected grammar when found.
3. If no grammar is selected, emit a rejecting base net instead of an exact automaton.

## Smoke Tests

Use as an ablation in:

- `scripts/alg0005_stress_tests.py`
- `scripts/benchmark.py`
- `scripts/alg0009_deep_tests.py`
- `scripts/alg0011_optional_tests.py`

## Known Failure Modes

- Fails replay on all cases that require exact fallback.
- Does not support XOR, optional chains, duplicate labels, or loops unless one of the shallow grammars happens to apply.

## EXP-0017 Results

Command: `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`

| Case | Grammar | Train replay | Held-out replay | Negative rejection |
|---|---|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | `parallel_block` | 2/2 | 4/4 | 3/3 |
| `heldout_parallel_balanced_2_of_6` | `parallel_block` | 2/2 | 4/4 | 3/3 |
| `heldout_optional_concurrency` | `no_grammar` | 0/3 | 0/2 | 3/3 |
| `noise_memorization` | `dominant_sequence` | 3/4 | 0/0 | 1/1 |
| `all_permutations_width_2` | `parallel_block` | 2/2 | 0/0 | 3/3 |
| `all_permutations_width_3` | `parallel_block` | 6/6 | 0/0 | 3/3 |

## Promotion Criteria

Not promoted. It is an ablation showing that `ALG-0015`'s prefix-biased parallel and rare-reversal noise results are true grammar behavior, while loop, duplicate-label, XOR, skip, and optional-chain successes depend on exact fallback.

## Experiment Links

- EXP-0017: exact-fallback ablation for `ALG-0015`.
- EXP-0018: confirmed that grammar-only behavior matches full `ALG-0015` on prefix-merged parallel and dominant-sequence cases, while fallback-dependent behavior remains rejected by the no-grammar net.

## Property-Study Notes

No property dossier.

## Decision History

- EXP-0017: added as a smoke-tested ablation; not promoted.
- EXP-0018: retained as a smoke-tested exact-fallback ablation; not promoted.
