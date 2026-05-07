# ALG-0015 — Prefix Block Support-Guard Miner

## Status

deep-testing

## One-sentence hypothesis

Support-skew guards, prefix-bias merging, and same-activity-set dominant-sequence noise handling can improve `ALG-0014` without losing exact fallback coverage.

## Input Assumptions

- Same shallow common-boundary setting as `ALG-0014`.
- Parallel order support is considered suspicious when the most frequent observed order has more than twice the support of the least frequent observed order.
- Prefix merge is allowed: when a common-prefix activity may be an under-observed parallel branch, move the last prefix activity into the candidate middle block.
- Dominant-sequence noise handling is allowed only when all variants have the same activity set and one variant has at least 60% support.

## Output

- PMIR evidence with selected grammar and configuration:
  - `max_parallel_support_skew=2`
  - `enable_prefix_merge=true`
  - `enable_dominant_sequence=true`
  - `allow_exact_fallback=true`
- Petri net compiled from a support-guarded grammar or exact automaton fallback.

## Intermediate Representation

Support-guarded prefix block grammar:

- `parallel_block`
- `optional_singleton_parallel`
- `dominant_sequence`
- `exact_prefix_automaton` fallback

## Allowed Operations / Operation-Cost Model

Uses the first-goal primitive operations. Compared with `ALG-0014`, it adds counted support-counter increments, skew arithmetic/comparisons, prefix-merge construction checks, and same-activity-set comparisons for dominant-sequence selection.

Expected cost is `ALG-0014` plus `O(T * L)` support/noise guard checks; exact fallback still adds `ALG-0005` automaton cost when no grammar is selected.

## Algorithm Sketch

1. Try support-guarded parallel-block detection.
2. If enabled, try moving the final common-prefix activity into the block to address prefix-biased partial permutations.
3. Try optional-singleton-parallel detection.
4. Try dominant-sequence grammar only for same-activity-set variants with skewed support.
5. Fall back to exact prefix automaton if no grammar is selected.

## Smoke Tests

Primary gates:

- `heldout_parallel_prefix_biased_2_of_6`
- `heldout_parallel_balanced_2_of_6`
- `noise_memorization`
- `optional_singleton_parallel_branch`

Broader gates are the standard toy smoke, synthetic deep, and optional-pattern suites.

## Baselines for Comparison

- `ALG-0005` exact prefix automaton.
- `ALG-0014` unguarded prefix block abstraction.
- `ALG-0016` grammar-only ablation.
- `ALG-0003` process-tree baseline.

## Metrics

- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Selected grammar.
- Operation count.
- Fallback dependence.

## Known Failure Modes

- The dominant-sequence noise guard intentionally sacrifices replay of rare reversal traces.
- Many successes still depend on exact fallback, especially loops, duplicate labels, XOR, and optional chains.
- Prefix merge may overgeneralize if a truly mandatory prefix activity is mistaken for an under-observed parallel branch.
- The grammar remains shallow and single-block.

## EXP-0017 Stress Results

Command: `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`

| Case | Grammar | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | `parallel_block` | 2/2 | 4/4 | 3/3 | 267 |
| `heldout_parallel_balanced_2_of_6` | `parallel_block` | 2/2 | 4/4 | 3/3 | 262 |
| `heldout_optional_concurrency` | `exact_prefix_automaton` | 3/3 | 0/2 | 3/3 | 470 |
| `noise_memorization` | `dominant_sequence` | 3/4 | 0/0 | 1/1 | 339 |
| `all_permutations_width_2` | `parallel_block` | 2/2 | 0/0 | 3/3 | 188 |
| `all_permutations_width_3` | `parallel_block` | 6/6 | 0/0 | 3/3 | 372 |

## EXP-0017 Smoke Results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Grammar | Ops | Replay | Negative rejection |
|---|---|---:|---:|---:|
| `noise.json` | `dominant_sequence` | 339 | 3/4 | 3/3 |
| `parallel_ab_cd.json` | `parallel_block` | 234 | 4/4 | 3/3 |
| `sequence.json` | `dominant_sequence` | 242 | 3/3 | 3/3 |
| `short_loop.json` | `exact_prefix_automaton` | 263 | 3/3 | 3/3 |
| `skip.json` | `exact_prefix_automaton` | 227 | 4/4 | 3/3 |
| `xor.json` | `exact_prefix_automaton` | 306 | 4/4 | 3/3 |

## EXP-0018 Ablation Results

Command: `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`

Feature attribution:

- Prefix merge is causal for `prefix_biased_parallel_2_of_6`: `ALG-0018` and full `ALG-0015` replay 4/4 held-out traces with `origin=prefix_merge`, while `ALG-0017` and `ALG-0019` replay 0/4.
- Dominant-sequence handling is causal for rare-reversal precision: `ALG-0019`, full `ALG-0015`, and `ALG-0016` reject 1/1 rare-reversal negative traces while replaying 3/4 or 5/6 training traces; `ALG-0017` and `ALG-0018` fall back to exact automata and reject 0/1.
- The same-activity-set guard prevents dominant-sequence handling on `different_activity_sets_skip_like`.
- Under `same_order_incomplete_parallel`, full `ALG-0015` remains conservative: it selects `dominant_sequence`, replays 2/2 observed traces, and replays 0/1 held-out reversed order.

## EXP-0019 Noisy/Incomplete Results

Command: `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`

Key findings:

- Prefix merge is an explicit ambiguity, not a universally correct repair. On the same training log `A B C D E`, `A B D C E`, full `ALG-0015` replays 4/4 late-B held-out traces when interpreted as incomplete three-way parallel, but rejects 0/4 late-B traces when those same traces are negative under a B-then-C/D interpretation.
- `ALG-0020` is the precision-side counter-candidate: it rejects 4/4 late-B negatives under the sequence-prefix interpretation, but replays 0/4 late-B held-out traces under the full-parallel interpretation.
- The current `max_parallel_support_skew=2` treats 2:1 reversal evidence as parallel, so `noise_reversal_2_to_1` rejects 0/1 rare-reversal negatives. A stricter skew of 1 selects `dominant_sequence` there, replaying 2/3 training traces and rejecting 1/1 rare-reversal negatives.
- For 3:1 noise, `min_dominant_ratio_percent=85` is too strict and falls back to exact replay, rejecting 0/1 rare-reversal negatives; 60 and 75 select dominant sequence and reject 1/1.
- For 5:1 noise, 60 and 75 select dominant sequence; 85 is still too strict because support is 5/6.

## EXP-0020 Ambiguity Evidence Follow-up

`ALG-0021` keeps the `ALG-0015` selected-net policy but emits PMIR ambiguity evidence when both common-boundary and prefix-merge parallel-block grammars are accepted and differ. In the targeted prefix-merge ambiguity cases, it flags both interpretations while preserving `ALG-0015`'s full-parallel compiled net. This does not change `ALG-0015`'s promotion status; it records the ambiguity for a future selector or multi-net evaluation protocol.

## Promotion Criteria

Promoted to `promising` in EXP-0017 because:

- deterministic executable wrapper in `scripts/prefix_block_support_guard.py`;
- written specification and operation model;
- measured counts;
- fixes `ALG-0014`'s prefix-biased held-out parallel failure;
- rejects the rare reversal noise case that `ALG-0005` and `ALG-0014` accept;
- preserves positive replay on non-noise smoke logs and optional-pattern cases.

Moved to `deep-testing` in EXP-0018 because feature ablations now attribute the prefix-bias repair to prefix merge and the rare-reversal precision repair to dominant-sequence handling. It is not `super-promising`: exact fallback remains responsible for many successes, and the noise guard trades away replay of rare variants.

## Experiment Links

- EXP-0016: unguarded `ALG-0014` introduced the grammar direction and exposed prefix-bias/noise failures.
- EXP-0017: this support-guarded refinement.
- EXP-0018: feature ablations for support skew, prefix merge, and dominant-sequence handling.
- EXP-0019: noisy/incomplete threshold sweep and prefix-merge ambiguity study.
- EXP-0020: ambiguity-aware PMIR evidence split into `ALG-0021`.

## Property-Study Notes

No property dossier. Candidate is not `super-promising`.

## Decision History

- EXP-0017: implemented and promoted to `promising`; retained as a precision/generalization tradeoff candidate.
- EXP-0018: moved to `deep-testing`; no property dossier because the candidate is not `super-promising`.
- EXP-0019: retained at `deep-testing`; no `super-promising` promotion because prefix merge and dominant-sequence handling both expose unavoidable precision/fitness tradeoffs under ambiguous evidence.
- EXP-0020: retained at `deep-testing`; ambiguity evidence was split into `ALG-0021` rather than treated as proof that the selected Petri net is uniquely justified.
