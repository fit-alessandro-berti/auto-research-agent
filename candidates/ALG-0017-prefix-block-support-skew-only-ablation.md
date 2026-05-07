# ALG-0017 — Prefix Block Support-Skew-Only Ablation

## Status

smoke-tested

## One-sentence hypothesis

A support-skew guard can prevent unsupported parallel-block selection under skewed order evidence, but it cannot by itself repair prefix-biased generalization or noisy exact-fallback memorization.

## Input assumptions

- Same shallow common-boundary setting as `ALG-0014`.
- `max_parallel_support_skew=2`.
- Prefix merge and dominant-sequence handling are disabled.
- Exact prefix-automaton fallback remains enabled.

## Output

- PMIR evidence with support-skew configuration and selected grammar.
- Petri net compiled from a support-guarded grammar or exact automaton fallback.

## Intermediate representation

Support-skew guarded block grammar:

- `parallel_block`
- `optional_singleton_parallel`
- `exact_prefix_automaton`

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Compared with `ALG-0014`, this ablation adds support counter increments, one skew arithmetic check, and skew comparisons for parallel-block candidates.

Expected cost is `ALG-0014` plus `O(T)` support counting for each candidate middle segment set; fallback adds the `ALG-0005` automaton cost.

## Algorithm sketch

1. Try common-boundary parallel-block detection.
2. Reject the parallel block if the largest observed segment support is more than twice the smallest support.
3. Try optional-singleton-parallel detection.
4. Fall back to exact prefix automaton if no grammar is selected.

## Smoke tests

Primary ablation gates:

- `prefix_biased_parallel_2_of_6`
- `rare_reversal_noise_3_to_1`
- `balanced_parallel_2_of_6`
- `different_activity_sets_skip_like`

## Baselines for comparison

- `ALG-0014` unguarded prefix block abstraction.
- `ALG-0015` full support-guarded miner.
- `ALG-0018` prefix-merge ablation.
- `ALG-0019` dominant-sequence ablation.

## Metrics

- Selected grammar and grammar origin.
- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation count.

## Known failure modes

- Prefix-biased held-out parallel still fails because the common boundary is not repaired.
- Rare-reversal noise falls back to exact automaton replay, so the noisy observed reversal is still accepted.
- This is an ablation control, not a standalone candidate for promotion.

## EXP-0018 results

Command: `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`

| Case | Grammar | Origin | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---|---:|---:|---:|---:|
| `prefix_biased_parallel_2_of_6` | `parallel_block` | `common_boundary` | 2/2 | 0/4 | 3/3 | 259 |
| `balanced_parallel_2_of_6` | `parallel_block` | `common_boundary` | 2/2 | 4/4 | 3/3 | 262 |
| `rare_reversal_noise_3_to_1` | `exact_prefix_automaton` | n/a | 4/4 | 0/0 | 0/1 | 409 |
| `rare_reversal_noise_5_to_1` | `exact_prefix_automaton` | n/a | 6/6 | 0/0 | 0/1 | 511 |
| `same_order_incomplete_parallel` | `exact_prefix_automaton` | n/a | 2/2 | 0/1 | 3/3 | 234 |
| `different_activity_sets_skip_like` | `exact_prefix_automaton` | n/a | 4/4 | 0/0 | 3/3 | 216 |

## Promotion criteria

Not promoted. It demonstrates that the support-skew guard changes selected grammar on noisy reversals, but exact fallback still memorizes the noisy observed trace and prefix-biased held-out generalization remains unresolved.

## Experiment links

- EXP-0018: feature ablation for `ALG-0015`.

## Property-study notes

No property dossier.

## Decision history

- EXP-0018: added as smoke-tested ablation control; not promoted.
