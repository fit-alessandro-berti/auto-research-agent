# ALG-0020 — Prefix Block Conservative-Merge Miner

## Status

smoke-tested

## One-sentence hypothesis

Prefix merge should only be attempted after the ordinary common-boundary block is rejected, preserving precision for sequence-prefix interpretations at the cost of losing some incomplete-parallel generalization.

## Input assumptions

- Same support guards and dominant-sequence handling as `ALG-0015`.
- `max_parallel_support_skew=2`.
- `prefix_merge_policy=after_common_rejects`.
- Exact prefix-automaton fallback remains enabled.

## Output

- PMIR evidence with selected grammar and conservative merge configuration.
- Petri net compiled from an ordinary block grammar, conservatively prefix-merged grammar, dominant sequence, or exact automaton fallback.

## Intermediate representation

Support-guarded prefix block grammar:

- `parallel_block`, with `origin=common_boundary` preferred over `origin=prefix_merge`.
- `optional_singleton_parallel`
- `dominant_sequence`
- `exact_prefix_automaton`

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Compared with `ALG-0015`, it changes only the order of prefix-merge checks: the common-boundary block is tested before prefix merge, and prefix merge is skipped if the common-boundary block is accepted.

Expected cost is close to `ALG-0015`; in cases where common-boundary detection succeeds, prefix-merge construction checks are avoided.

## Algorithm sketch

1. Try support-guarded common-boundary parallel-block detection.
2. If common-boundary detection succeeds, accept it and skip prefix merge.
3. If common-boundary detection fails, try prefix merge.
4. Try optional-singleton-parallel detection.
5. Try dominant-sequence noise handling.
6. Fall back to exact prefix automaton.

## Smoke tests

Primary gates:

- `prefix_merge_full_parallel_interpretation`
- `prefix_merge_sequence_then_parallel_interpretation`
- `heldout_parallel_prefix_biased_2_of_6`
- `noise_reversal_3_to_1`
- Standard toy smoke and optional-pattern suites

## Baselines for comparison

- `ALG-0015` full support-guarded miner.
- `ALG-0018` prefix-merge ablation.
- `ALG-0017` support-skew-only ablation.
- `ALG-0014` unguarded common-boundary abstraction.

## Metrics

- Held-out replay under full-parallel interpretation.
- Negative rejection under sequence-prefix interpretation.
- Selected grammar origin.
- Operation count.
- Fallback dependence.

## Known failure modes

- Loses the `ALG-0015` prefix-biased held-out parallel repair whenever the common-boundary block is accepted.
- Does not resolve the underlying identifiability problem: the same observed log can support both a full-parallel and sequence-prefix interpretation.
- Still depends on exact fallback for loops, duplicate labels, XOR, optional chains, and optional concurrency.

## EXP-0019 results

Command: `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`

| Case | Grammar | Origin | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---|---:|---:|---:|---:|
| `prefix_merge_full_parallel_interpretation` | `parallel_block` | `common_boundary` | 2/2 | 0/4 | 3/3 | 259 |
| `prefix_merge_sequence_then_parallel_interpretation` | `parallel_block` | `common_boundary` | 2/2 | 0/0 | 4/4 | 259 |
| `noise_reversal_2_to_1` | `parallel_block` | `common_boundary` | 3/3 | 0/0 | 0/1 | 215 |
| `noise_reversal_3_to_1` | `dominant_sequence` | n/a | 3/4 | 0/0 | 1/1 | 339 |
| `noise_reversal_5_to_1` | `dominant_sequence` | n/a | 5/6 | 0/0 | 1/1 | 433 |

Standard-suite checks:

- Toy smoke matches `ALG-0015` on all six logs.
- ALG-0005 stress confirms the intended tradeoff: `heldout_parallel_prefix_biased_2_of_6` drops from `ALG-0015`'s 4/4 held-out replay to 0/4, but the sequence-prefix ambiguity case rejects 4/4 late-B negatives.

## Promotion criteria

Not promoted. It is a useful precision-side tradeoff and counterexample control, but it sacrifices the main prefix-biased held-out gain that motivated `ALG-0015`.

## Experiment links

- EXP-0019: noisy/incomplete threshold sweep and prefix-merge ambiguity study.

## Property-study notes

No property dossier.

## Decision history

- EXP-0019: added as a smoke-tested tradeoff candidate; not promoted.
