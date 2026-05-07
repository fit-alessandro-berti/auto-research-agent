# ALG-0024 — Cut-Limited Multi-Body Rework Loop Miner

## Status

promising

## One-sentence hypothesis

If zero-iteration evidence and two or more singleton rework bodies are observed around the same anchor, a bounded process-tree cut can compile an unbounded loop with an XOR body choice and recover held-out repeated body combinations.

## Input assumptions

- Batch event log with activity-label traces.
- The supported shape is:
  - zero iteration: `prefix anchor suffix`;
  - one iteration: `prefix anchor body_i anchor suffix`;
  - each observed `body_i` is a singleton activity;
  - at least two distinct singleton bodies are observed;
  - the repeated label is only the loop anchor.
- The emitted loop uses an explicit unbounded-repeat prior. Bounded-at-most-one semantics are not inferred from the event log alone.

## Output

- PMIR/process-tree cut: `multi_body_rework_loop` with prefix, anchor, singleton bodies, body support, suffix, zero-iteration exemplar, `loop_repetition_policy=unbounded_repeat`, and `bounded_count_ambiguous=true`.
- Petri net: duplicate visible transitions for the anchor label, a post-anchor choice between suffix exit and observed body transitions, and a repeat-anchor transition returning to the post-anchor loop place.

## Intermediate representation

Cut-limited process tree / PMIR:

- `prefix`
- `anchor`
- `bodies`
- `body_support`
- `suffix`
- `zero_iteration`
- `observed_max_iterations`
- loop-policy annotations

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- event scans to inspect repeated-label positions;
- dictionary increments for singleton body-support counts;
- set insertions/lookups for duplicate-label and body-set checks;
- comparisons for shape validation, prefix/suffix checks, and variant acceptance;
- construction operations for PMIR entries, duplicate-labeled anchor transitions, body-choice arcs, places, and markings.

Expected cost is `ALG-0023 + O(T * L + B)` for `B` accepted singleton body alternatives. The current prototype tries multi-body detection before singleton-loop detection when enabled, so singleton-loop cases pay extra rejected-detector cost.

## Algorithm sketch

1. Run the existing `ALG-0003` sequence, XOR, parallel, and optional-concurrency cut detectors.
2. If multi-body loop detection is enabled, inspect longest variants for exactly one repeated anchor label.
3. Derive `prefix`, singleton `body_i`, and `suffix` from candidate one-iteration traces.
4. Accept only if every trace is either `prefix anchor suffix` or `prefix anchor body_i anchor suffix`.
5. Require a zero-iteration trace and at least two distinct singleton bodies.
6. Compile the loop as an unbounded body-choice loop using duplicate visible anchor transitions.
7. Fall back to `ALG-0023` singleton-loop detection or the normal `ALG-0003` optional/fallback behavior otherwise.

## Expected complexity

`O(N + A^2 + T * L^2 + T * L + B)` under the cut-limited process-tree path, with sorting overhead still uncounted by the first-iteration operation model. The additional measured operations are from candidate-shape scans, body-support counting, and body-branch construction.

## Smoke tests

Primary gates:

- `multi_body_loop_choice`
- `nested_choice_loop_context`
- existing `different_rework_body_rejected` case, now reinterpreted as a positive multi-body loop case

Regression controls:

- `loop_unbounded_control`
- `single_rework_zero_or_one`
- `short_loop.json`
- `short_loop_required`
- `duplicate_label_rework`
- `one_iteration_only`
- `bounded_at_most_one_rework`

## Baselines for comparison

- `ALG-0003` cut-limited process-tree baseline.
- `ALG-0023` singleton-loop repair.
- `ALG-0005` exact prefix automaton.
- `ALG-0015` prefix-block support-guard miner.
- `ALG-0016` grammar-only prefix-block ablation.

## Metrics

- Selected cut.
- Body support and loop-policy evidence.
- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation count and budget ratio.
- Structural diagnostics.

## Known failure modes

- Bounded-count semantics remain ambiguous. The same zero/one evidence can mean unbounded repeat or at-most-one rework.
- Only singleton body alternatives are supported.
- One-iteration-only evidence is rejected because no loop exit was observed, leaving fallback replay poor.
- Duplicate labels inside body alternatives or suffix/prefix contexts are rejected.
- Body-choice repetition may overgeneralize unseen body sequences or repeated body combinations if the process permits only one rework.

## EXP-0024 Results

Command: `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|
| `loop_unbounded_control` | `single_rework_loop` | 3/3 | 1/1 | 3/3 | 270 |
| `bounded_at_most_one_rework` | `single_rework_loop` | 3/3 | 0/0 | 2/3 | 270 |
| `multi_body_loop_choice` | `multi_body_rework_loop` | 3/3 | 2/2 | 3/3 | 258 |
| `nested_choice_loop_context` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 349 |
| `one_iteration_only` | `fallback_dfg` | 0/3 | 0/2 | 3/3 | 415 |

Additional stress checks:

- `multi_body_loop_choice` in the ALG-0023 stress suite improves from `ALG-0023` 0/3 train and 0/1 held-out replay to 3/3 train and 1/1 held-out replay, with 3/3 negative rejection.
- `nested_loop_with_choice_context` improves from `ALG-0023` 0/3 train and 0/1 held-out replay to 3/3 train and 1/1 held-out replay, with 3/3 negative rejection.
- Standard smoke behavior is preserved: sequence, XOR, parallel, skip, noise, and short-loop toy logs all replay their positives and reject 3/3 negative probes.

## EXP-0025 Boundary-Stress Results

Command: `python3 scripts/alg0024_stress_tests.py --out experiments/alg0024-stress-tests.json`

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `longer_body_choice_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 438 | Length-2 body alternatives remain outside scope. |
| `mixed_singleton_and_sequence_body_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 387 | Mixed body widths are rejected rather than coerced into singleton choices. |
| `duplicate_label_in_suffix_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 388 | Duplicate body/suffix labels remain outside the current duplicate-label compiler scope. |
| `bounded_count_multi_body_prior` | `multi_body_rework_loop` | 3/3 | 0/0 | 2/4 | 258 | Repeated body combinations are accepted under the unbounded prior, so bounded-count domains remain ambiguous. |
| `support_imbalance_body_choice` | `multi_body_rework_loop` | 5/5 | 1/1 | 3/3 | 332 | Observed low-support body alternatives are treated as valid choices, not noise. |

Trace-order stability:

- `multi_body_loop_choice_order_stability`: stable across 6 unique permutations.
- `nested_choice_loop_context_order_stability`: stable across 6 unique permutations.
- `support_imbalance_body_choice_order_stability`: stable across 12 unique permutations.

Decision after EXP-0025: keep status at `promising`. Stability and support-count evidence are useful, but length-2 bodies, duplicate-label contexts, bounded-count priors, and noise-versus-rare-body selection block `deep-testing`.

## Promotion criteria

Promoted to `promising` in EXP-0024 because it has:

- deterministic executable wrapper in `scripts/cut_limited_multi_body_loop.py`;
- written specification and measured operation counts;
- full train/held-out replay and full negative rejection on targeted multi-body and nested-context cases;
- preserved singleton-loop behavior through the `ALG-0023` detector;
- a concrete advantage over `ALG-0023` and exact automata on held-out multi-body loop combinations.

It is not `deep-testing` or `super-promising` because bounded-count semantics, one-iteration-only logs, longer body sequences, and broader duplicate-label contexts remain unresolved.

## Experiment links

- EXP-0024: targeted multi-body loop tests, standard smoke rerun, and loop-stress rerun.
- EXP-0025: longer-body, duplicate-label, bounded-count, support-imbalance, and trace-order stability stress tests.

## Property-study notes

No property dossier. Future property work must study the language `prefix anchor (body_1 anchor | ... | body_k anchor)* suffix`, duplicate-anchor transition correctness, 1-safeness, replay/precision under unbounded-repeat priors, and operation-budget tightness.

## Decision history

- EXP-0024: implemented as the evidence-driven loop-choice split after `ALG-0023`; promoted to `promising`, not beyond.
- EXP-0025: retained at `promising`; stress tests confirmed deterministic selection but exposed longer-body, duplicate-label, bounded-count, and support/noise boundaries.
