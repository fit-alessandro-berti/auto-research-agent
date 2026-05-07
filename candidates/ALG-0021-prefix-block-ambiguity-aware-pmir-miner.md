# ALG-0021 — Prefix Block Ambiguity-Aware PMIR Miner

## Status

smoke-tested

## One-sentence hypothesis

When prefix-merge and common-boundary grammars both explain the observed log, the miner should preserve both interpretations in PMIR evidence instead of pretending the selected Petri net is uniquely justified.

## Input assumptions

- Same support guards and dominant-sequence handling as `ALG-0015`.
- `max_parallel_support_skew=2`.
- `prefix_merge_policy=before_common`, so the compiled Petri net matches the full-parallel `ALG-0015` policy.
- Prefix-merge ambiguity evidence is emitted when both common-boundary and prefix-merge parallel-block grammars are accepted and have different branch scopes.

## Output

- PMIR evidence with:
  - selected grammar and selected policy;
  - `ambiguity.detected`;
  - both common-boundary and prefix-merge alternatives when detected;
  - each alternative's intended policy label.
- Petri net compiled from the selected grammar.

## Intermediate representation

Ambiguity-aware support-guarded prefix block PMIR:

- `parallel_block`
- `optional_singleton_parallel`
- `dominant_sequence`
- `exact_prefix_automaton`
- `ambiguity` annotation with alternative grammars

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Compared with `ALG-0015`, it repeats bounded common-prefix/common-suffix and segment-set checks to populate ambiguity evidence.

Expected cost is `ALG-0015 + O(T * L + B)` for the extra ambiguity check, where `B` is the emitted alternative grammar size.

## Algorithm sketch

1. Run the `ALG-0015` support-guarded grammar selection.
2. Compile the selected grammar to a Petri net.
3. Independently test the common-boundary and prefix-merge parallel-block alternatives.
4. If both alternatives are accepted and differ, emit `ambiguity.detected=true` with both alternatives:
   - `sequence_prefix_precision` for common-boundary grammar.
   - `full_parallel_generalization` for prefix-merge grammar.
5. Preserve exact fallback behavior for cases outside the shallow grammar scope.

## Smoke tests

Primary gates:

- `prefix_merge_full_parallel_interpretation`
- `prefix_merge_sequence_then_parallel_interpretation`
- standard toy smoke logs
- ALG-0005 stress suite

## Baselines for comparison

- `ALG-0015` full support-guarded miner.
- `ALG-0020` conservative prefix-merge miner.
- `ALG-0018` prefix-merge ablation.
- `ALG-0017` support-skew-only ablation.

## Metrics

- Whether ambiguity is detected.
- Number and type of alternatives.
- Selected policy.
- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation count overhead relative to `ALG-0015`.

## Known failure modes

- It does not resolve ambiguity automatically; it records it.
- The compiled Petri net still follows `ALG-0015`'s full-parallel preference, so sequence-prefix precision failures remain in the selected net.
- Ambiguity evidence currently covers only prefix-merge versus common-boundary parallel blocks.
- Extra evidence checks increase operation counts.

## EXP-0020 Results

Command: `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`

| Case | Grammar | Ambiguous | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|---:|
| `prefix_merge_full_parallel_interpretation` | `parallel_block` / `prefix_merge` | yes | 2/2 | 4/4 | 3/3 | 361 |
| `prefix_merge_sequence_then_parallel_interpretation` | `parallel_block` / `prefix_merge` | yes | 2/2 | 0/0 | 0/4 | 361 |
| `noise_reversal_3_to_1` | `dominant_sequence` | no | 3/4 | 0/0 | 1/1 | 415 |
| `incomplete_parallel_one_order_2` | `dominant_sequence` | no | 2/2 | 0/1 | 3/3 | 227 |

Standard-suite checks:

- Toy smoke behavior matches `ALG-0015`, with extra operation counts for ambiguity evidence.
- Ambiguity is not detected on the six toy smoke logs.
- The ambiguity detector fires on the targeted prefix-merge ambiguity cases.

## EXP-0021 Follow-up

`ALG-0022` consumes the ambiguity alternatives from this candidate and compiles each into a Petri net. The model-set protocol confirms that the `full_parallel_generalization` alternative recovers 4/4 held-out late-B traces in the full-parallel interpretation, while the `sequence_prefix_precision` alternative rejects 4/4 late-B negatives in the sequence-prefix interpretation.

## Promotion criteria

Not promoted. It is a useful PMIR/evidence refinement but does not improve selected-net quality yet. Promotion would require a downstream selector, domain prior, or multi-net evaluation protocol that uses the ambiguity annotation.

## Experiment links

- EXP-0020: ambiguity-aware PMIR evidence for prefix-block candidates.
- EXP-0021: ambiguity-set alternative compilation protocol (`ALG-0022`).

## Property-study notes

No property dossier.

## Decision history

- EXP-0020: added as a smoke-tested PMIR/evidence candidate; not promoted.
- EXP-0021: retained as smoke-tested; alternatives are consumed by `ALG-0022`, but no deterministic selector exists yet.
