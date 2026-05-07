# ALG-0019 — Prefix Block Dominant-Sequence Ablation

## Status

smoke-tested

## One-sentence hypothesis

Dominant-sequence handling is the causal `ALG-0015` feature for treating rare same-activity-set reversals as noise instead of concurrency.

## Input assumptions

- Same shallow common-boundary setting as `ALG-0014`.
- `max_parallel_support_skew=2`.
- Dominant-sequence handling is enabled.
- Prefix merge is disabled.
- Exact prefix-automaton fallback remains enabled.

## Output

- PMIR evidence with support-skew and dominant-sequence configuration.
- Petri net compiled from a dominant sequence, ordinary support-guarded block, optional-singleton parallel block, or exact automaton fallback.

## Intermediate representation

Support-guarded block grammar:

- `parallel_block`
- `optional_singleton_parallel`
- `dominant_sequence`
- `exact_prefix_automaton`

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Compared with `ALG-0017`, it adds same-activity-set checks, variant support counting, majority comparisons, and support-ratio arithmetic for dominant-sequence selection.

Expected cost is `ALG-0017` plus `O(T * L + V log V)` for the current deterministic variant ranking; fallback adds the `ALG-0005` automaton cost.

## Algorithm sketch

1. Try support-guarded common-boundary parallel-block detection.
2. Try optional-singleton-parallel detection.
3. If all variants have the same activity set and one variant has at least 60% support without a support tie, emit a dominant sequence.
4. Fall back to exact prefix automaton.

## Smoke tests

Primary ablation gates:

- `rare_reversal_noise_3_to_1`
- `rare_reversal_noise_5_to_1`
- `ambiguous_reversal_tie`
- `same_order_incomplete_parallel`
- `prefix_biased_parallel_2_of_6`

## Baselines for comparison

- `ALG-0014` unguarded prefix block abstraction.
- `ALG-0017` support-skew-only ablation.
- `ALG-0018` prefix-merge ablation.
- `ALG-0015` full support-guarded miner.

## Metrics

- Selected grammar.
- Training replay lost by treating rare variants as noise.
- Negative-trace rejection.
- Held-out replay on prefix-biased parallel.
- Operation count.

## Known failure modes

- Prefix-biased held-out parallel still fails because prefix merge is disabled.
- Dominant-sequence handling intentionally rejects rare same-activity-set variants.
- It is conservative under incomplete parallel evidence: a single observed order becomes a sequence, not a generalized parallel block.

## EXP-0018 results

Command: `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`

| Case | Grammar | Origin | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---|---:|---:|---:|---:|
| `prefix_biased_parallel_2_of_6` | `parallel_block` | `common_boundary` | 2/2 | 0/4 | 3/3 | 259 |
| `rare_reversal_noise_3_to_1` | `dominant_sequence` | n/a | 3/4 | 0/0 | 1/1 | 339 |
| `rare_reversal_noise_5_to_1` | `dominant_sequence` | n/a | 5/6 | 0/0 | 1/1 | 433 |
| `ambiguous_reversal_tie` | `parallel_block` | `common_boundary` | 2/2 | 0/0 | 3/3 | 188 |
| `same_order_incomplete_parallel` | `dominant_sequence` | n/a | 2/2 | 0/1 | 3/3 | 203 |
| `different_activity_sets_skip_like` | `exact_prefix_automaton` | n/a | 4/4 | 0/0 | 3/3 | 227 |

## Promotion criteria

Not promoted as an independent candidate. EXP-0018 shows dominant-sequence handling is causal for rare-reversal precision, but it does not fix prefix-biased held-out parallel and remains a scoped noise policy.

## Experiment links

- EXP-0018: feature ablation for `ALG-0015`.

## Property-study notes

No property dossier.

## Decision history

- EXP-0018: added as smoke-tested ablation; not promoted.
