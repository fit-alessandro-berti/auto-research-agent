# ALG-0025 - Cut-Limited Length-Bounded Rework Loop Miner

## Status

promising

## One-sentence hypothesis

If zero-iteration evidence and two or more short rework bodies of length at most two are observed around the same anchor, the multi-body loop cut can generalize held-out repeated body combinations while keeping duplicate-label and longer-body cases out of scope.

## Input assumptions

- Batch event log with activity-label traces.
- The supported shape is:
  - zero iteration: `prefix anchor suffix`;
  - one iteration: `prefix anchor body_i anchor suffix`;
  - each observed `body_i` has length one or two;
  - at least two distinct bodies are observed;
  - body labels do not overlap with each other, the anchor, prefix, or suffix;
  - a non-empty suffix is observed after the repeated anchor.
- The emitted loop uses an explicit unbounded-repeat prior. Bounded-at-most-one semantics are not inferred from the event log alone.

## Output

- PMIR/process-tree cut: `multi_body_rework_loop` with prefix, anchor, body sequences, body support, `max_body_length=2`, suffix, zero-iteration exemplar, `loop_repetition_policy=unbounded_repeat`, and `bounded_count_ambiguous=true`.
- Petri net: duplicate visible transitions for the anchor label, a post-anchor choice between suffix exit and each body sequence, and a repeat-anchor transition returning to the post-anchor loop place.

## Intermediate representation

Cut-limited process tree / PMIR:

- `prefix`
- `anchor`
- `bodies`
- `body_support`
- `max_body_length`
- `suffix`
- `zero_iteration`
- `observed_max_iterations`
- loop-policy annotations

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- event scans to inspect repeated-label positions and candidate body slices;
- dictionary increments for tuple body-support counts;
- set insertions/lookups for duplicate-label and repeated-anchor checks;
- comparisons for shape validation, prefix/suffix checks, body-length bounds, and variant acceptance;
- construction operations for PMIR entries, duplicate-labeled anchor transitions, body-sequence places, arcs, and markings.

Expected cost is `ALG-0024 + O(T * L * M + B * M)` for fixed maximum body length `M=2` and `B` accepted body alternatives. In the current implementation this is the same detector as `ALG-0024` parameterized by `multi_body_loop_max_body_length=2`, so singleton-body logs should match `ALG-0024` behavior with the same selected cut and similar counts.

## Algorithm sketch

1. Run the existing `ALG-0003` sequence, XOR, parallel, and optional-concurrency cut detectors.
2. Try the parameterized multi-body loop detector with `max_body_length=2`.
3. Inspect longest variants for exactly one repeated anchor label.
4. Derive `prefix`, tuple body, and `suffix` from each candidate one-iteration trace.
5. Accept only if every trace is either `prefix anchor suffix` or `prefix anchor body_i anchor suffix`, with `1 <= len(body_i) <= 2`.
6. Require a zero-iteration trace and at least two distinct body tuples.
7. Reject if the anchor occurs in a body, a body has duplicate labels, or labels overlap across prefix, anchor, bodies, and suffix.
8. Compile an unbounded body-choice loop using duplicate visible anchor transitions and sequence wiring for each body.
9. Fall back to singleton-loop detection or the normal `ALG-0003` optional/fallback behavior otherwise.

## Expected complexity

`O(N + A^2 + T * L^2 + T * L * M + B * M)` under the cut-limited process-tree path for fixed `M=2`. Sorting and Python container overhead remain outside the first-iteration counted operation model.

## Smoke tests

Primary gates:

- `length2_body_choice`
- `mixed_singleton_and_length2_body`
- `singleton_body_regression`

Boundary controls:

- `length3_body_rejected`
- `overlapping_body_labels_rejected`
- `bounded_count_length2_prior`
- trace-order stability for length-2 and mixed-width body evidence

Regression controls:

- `loop_unbounded_control`
- `bounded_at_most_one_rework`
- `multi_body_loop_choice`
- `nested_choice_loop_context`
- `one_iteration_only`
- six toy logs in `examples/logs`

## Baselines for comparison

- `ALG-0003` cut-limited process-tree baseline.
- `ALG-0023` singleton-loop repair.
- `ALG-0024` singleton-body multi-body loop repair.
- `ALG-0005` exact prefix automaton.
- `ALG-0015` prefix-block support-guard miner.
- `ALG-0016` grammar-only prefix-block ablation.

## Metrics

- Selected cut.
- Body support, max body length, and loop-policy evidence.
- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation count and budget ratio.
- Structural diagnostics.
- Trace-order signature stability.

## Known failure modes

- Bounded-count semantics remain ambiguous; repeated body combinations are accepted under the unbounded-repeat prior.
- Body length greater than two is rejected.
- Duplicate body labels and labels shared across body alternatives, prefix, anchor, or suffix are rejected.
- One-iteration-only evidence is rejected because no loop exit was observed.
- Low-support body alternatives are treated as valid choices; no support/noise guard is included.
- Longer body sequences may need a separate cost and overgeneralization study before increasing the bound.

## EXP-0026 Results

Command: `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `length2_body_choice` | `multi_body_rework_loop` | 3/3 | 2/2 | 3/3 | 401 | Fixes the length-2 body-choice gap from EXP-0025. |
| `mixed_singleton_and_length2_body` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 322 | Mixed singleton and length-2 bodies can coexist. |
| `singleton_body_regression` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 258 | Preserves the `ALG-0024` singleton-body behavior. |
| `length3_body_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 641 | Body length greater than two remains outside scope. |
| `overlapping_body_labels_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 436 | Shared body labels remain rejected. |
| `bounded_count_length2_prior` | `multi_body_rework_loop` | 3/3 | 0/0 | 2/4 | 401 | Repeated body combinations expose the unbounded prior. |

Trace-order stability:

- `length2_body_choice_order_stability`: stable across 6 unique permutations.
- `mixed_singleton_and_length2_body_order_stability`: stable across 6 unique permutations.

Additional regression observations:

- In the refreshed `ALG-0024` stress suite, `ALG-0025` reinterprets the former longer-body rejection controls as supported length-2/mixed-width positives and achieves full train, held-out, and negative results on those cases.
- It preserves `ALG-0024` behavior on singleton multi-body loop-choice and support-imbalance cases.
- Standard smoke behavior is preserved on sequence, XOR, parallel, skip, noise, and short-loop toy logs.

## Promotion criteria

Promoted to `promising` in EXP-0026 because it has:

- deterministic executable wrapper in `scripts/cut_limited_length_bounded_loop.py`;
- written specification and measured operation counts;
- full train/held-out replay and full negative rejection on targeted length-2 and mixed-width body-loop cases;
- preserved singleton-body behavior from `ALG-0024`;
- a concrete advantage over `ALG-0024`, `ALG-0023`, exact automata, and prefix-block fallback on held-out length-2 body-loop combinations.

It is not `deep-testing` or `super-promising` because bounded-count priors, length greater than two, duplicate-label body contexts, one-iteration-only evidence, and support/noise body selection remain unresolved.

## Experiment links

- EXP-0026: targeted length-bounded loop-body tests, affected loop-regression reruns, standard smoke rerun, and refreshed synthetic suites.

## Property-study notes

No property dossier. Future property work must study the bounded body language `prefix anchor (body_1 anchor | ... | body_k anchor)* suffix` with `|body_i| <= 2`, sequence-body place wiring, duplicate-anchor transition correctness, 1-safeness, replay/precision under unbounded-repeat priors, and whether increasing `M` preserves the operation-budget story.

## Decision history

- EXP-0026: implemented as the length-bounded loop-body split after EXP-0025 showed length-2 bodies were a concrete replay/generalization gap for `ALG-0024`; promoted to `promising`, not beyond.
