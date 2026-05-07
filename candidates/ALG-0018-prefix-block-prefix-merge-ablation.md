# ALG-0018 — Prefix Block Prefix-Merge Ablation

## Status

smoke-tested

## One-sentence hypothesis

Prefix-bias merging is the causal `ALG-0015` feature for recovering held-out interleavings when observed variants share a misleading middle prefix.

## Input assumptions

- Same shallow common-boundary setting as `ALG-0014`.
- `max_parallel_support_skew=2`.
- Prefix merge is enabled.
- Dominant-sequence handling is disabled.
- Exact prefix-automaton fallback remains enabled.

## Output

- PMIR evidence with support-skew and prefix-merge configuration.
- Petri net compiled from a prefix-merged grammar or exact automaton fallback.

## Intermediate representation

Support-guarded block grammar:

- `parallel_block`, including `origin=prefix_merge` evidence.
- `optional_singleton_parallel`
- `exact_prefix_automaton`

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Compared with `ALG-0017`, it adds construction and set/comparison checks for moving the final common-prefix activity into the candidate middle block.

Expected cost is `ALG-0017` plus `O(T)` prefix-merge segment construction/checking; fallback adds the `ALG-0005` automaton cost.

## Algorithm sketch

1. Try support-guarded parallel-block detection after moving the final common-prefix activity into each middle segment.
2. If that fails, try the ordinary common-boundary parallel block.
3. Try optional-singleton-parallel detection.
4. Fall back to exact prefix automaton.

## Smoke tests

Primary ablation gates:

- `prefix_biased_parallel_2_of_6`
- `balanced_parallel_2_of_6`
- `rare_reversal_noise_3_to_1`
- `rare_reversal_noise_5_to_1`

## Baselines for comparison

- `ALG-0014` unguarded prefix block abstraction.
- `ALG-0017` support-skew-only ablation.
- `ALG-0019` dominant-sequence ablation.
- `ALG-0015` full support-guarded miner.

## Metrics

- Selected grammar and grammar origin.
- Held-out replay.
- Negative-trace rejection.
- Operation count.

## Known failure modes

- Rare-reversal noise still falls back to exact automaton when support-skew rejects parallel evidence, so noisy observed variants remain accepted.
- Prefix merge may overgeneralize if the moved prefix activity is truly mandatory sequence context rather than an under-observed parallel branch.
- This ablation does not address fallback dependence on loops, XOR, duplicate labels, or optional chains.

## EXP-0018 results

Command: `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`

| Case | Grammar | Origin | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---|---:|---:|---:|---:|
| `prefix_biased_parallel_2_of_6` | `parallel_block` | `prefix_merge` | 2/2 | 4/4 | 3/3 | 267 |
| `balanced_parallel_2_of_6` | `parallel_block` | `common_boundary` | 2/2 | 4/4 | 3/3 | 262 |
| `rare_reversal_noise_3_to_1` | `exact_prefix_automaton` | n/a | 4/4 | 0/0 | 0/1 | 409 |
| `rare_reversal_noise_5_to_1` | `exact_prefix_automaton` | n/a | 6/6 | 0/0 | 0/1 | 511 |
| `same_order_incomplete_parallel` | `exact_prefix_automaton` | n/a | 2/2 | 0/1 | 3/3 | 238 |

## Promotion criteria

Not promoted as an independent candidate. EXP-0018 shows prefix merge is causal for the prefix-biased held-out gain, but the ablation keeps the rare-reversal precision failure.

## Experiment links

- EXP-0018: feature ablation for `ALG-0015`.

## Property-study notes

No property dossier.

## Decision history

- EXP-0018: added as smoke-tested ablation; not promoted.
