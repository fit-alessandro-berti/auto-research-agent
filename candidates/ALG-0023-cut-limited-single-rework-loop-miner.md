# ALG-0023 — Cut-Limited Single-Rework Loop Miner

## Status

promising

## One-sentence hypothesis

A narrow loop cut that recognizes an observed zero-iteration exit and a singleton rework body can repair the short-loop failure of `ALG-0003` without adding a general recursive loop miner.

## Input assumptions

- Batch event log with activity-label traces.
- The supported loop shape is:
  - zero iteration: `prefix anchor suffix`;
  - one iteration: `prefix anchor body anchor suffix`;
  - `body` is a singleton activity;
  - the repeated label is only the loop anchor.
- At least one zero-iteration trace and one one-iteration trace must be observed before the loop cut fires.

## Output

Petri net with duplicate visible transitions for the loop anchor:

- one entry transition labeled as the anchor;
- one repeat transition labeled as the same anchor;
- body transition returns to the repeat-anchor input;
- suffix exits from the post-anchor place.

## Intermediate representation

Cut-limited process tree / PMIR with a `single_rework_loop` cut:

- `prefix`
- `anchor`
- `body`
- `suffix`
- zero-iteration exemplar
- one-iteration exemplar

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- event scans to inspect candidate traces and repeated-label positions;
- set insertions and lookups for duplicate-label checks;
- comparisons for trace-shape validation and variant acceptance;
- construction operations for loop PMIR entries, duplicate-labeled transitions, places, arcs, and markings.

Expected cost is `ALG-0003 + O(T * L + A)` when the loop detector is enabled, plus constant-size loop-net construction for the singleton-body scope.

## Algorithm sketch

1. Run the existing `ALG-0003` cut detectors.
2. If earlier sequence/XOR/parallel/optional-concurrency cuts fail and loop detection is enabled, inspect longest variants for exactly one repeated label.
3. Accept a loop candidate only if every trace equals either `prefix anchor suffix` or `prefix anchor body anchor suffix`.
4. Require both zero-iteration and one-iteration variants.
5. Compile the loop using duplicate visible transitions for the anchor label.
6. Fall back to the normal `ALG-0003` optional-sequence or DFG fallback behavior when the loop pattern does not match.

## Smoke tests

Primary gates:

- `short_loop.json`
- `short_loop_required`
- `duplicate_label_rework`
- targeted `single_rework_zero_or_one`

False-positive controls:

- `single_rework_one_iteration_only`
- `optional_skip_not_loop`
- `different_rework_body_rejected`

## Baselines for comparison

- `ALG-0003` cut-limited process-tree baseline.
- `ALG-0005` exact prefix automaton.
- `ALG-0015` prefix-block support-guard miner.
- `ALG-0016` grammar-only prefix-block ablation.

## Metrics

- Selected cut.
- Training replay.
- Held-out replay.
- Negative-trace rejection.
- Operation count and budget ratio.
- Structural diagnostics.

## Known failure modes

- The loop detector is intentionally non-recursive and singleton-body only.
- If only the one-iteration variant is observed, the loop cut does not fire and the current `ALG-0003` fallback may fail observed replay.
- It does not handle two different rework bodies around the same anchor.
- The multi-body rework case was split into `ALG-0024` rather than broadening this singleton-body hypothesis.
- It generalizes to repeated loop iterations once zero and one iteration are observed; that is useful for loop behavior but can overgeneralize if the process permits at most one rework.
- Duplicate visible transitions require evaluator support for `transition_labels`.

## EXP-0022 Results

Command: `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|
| `single_rework_zero_or_one` | `single_rework_loop` | 3/3 | 1/1 | 3/3 | 216 |
| `single_rework_one_iteration_only` | `fallback_dfg` | 0/2 | 0/1 | 3/3 | 212 |
| `optional_skip_not_loop` | `optional_sequence` | 3/3 | 0/0 | 3/3 | 207 |
| `different_rework_body_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 286 |

Standard smoke:

- `short_loop.json`: 216 ops, 3/3 replay, 3/3 negative rejection.
- Sequence, XOR, parallel, skip, and noise smoke behavior matches `ALG-0003` except for small detector-overhead increases on skip.

Deep synthetic:

- `short_loop_required`: `single_rework_loop`, 216 ops, 3/3 replay, 3/3 negative rejection.
- `duplicate_label_rework`: `single_rework_loop`, 204 ops, 3/3 replay, 3/3 negative rejection.
- No new regressions on nested XOR, overlapping optional skips, optional concurrency, incomplete parallel, or noise reversal synthetic cases.

## EXP-0023 Loop-Stress Results

Command: `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `bounded_at_most_one_rework` | `single_rework_loop` | 3/3 | 0/0 | 2/3 | 204 | Accepts a second loop iteration, so bounded-count domains need an explicit prior. |
| `prefixed_suffixed_single_rework` | `single_rework_loop` | 3/3 | 1/1 | 3/3 | 368 | Prefix/suffix context is handled. |
| `multi_body_loop_choice` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 286 | Multi-body loop choice is outside scope. |
| `nested_loop_with_choice_context` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 381 | Nested loop-with-choice is outside scope. |
| `one_iteration_only_with_clean_dfg_path` | `fallback_dfg` | 0/3 | 0/2 | 3/3 | 282 | Zero-iteration evidence is required, and fallback remains poor. |

Decision after EXP-0023: keep status at `promising`. The stress suite confirms the loop cut is useful for a narrow unbounded-loop assumption but exposes bounded-count and multi-body limitations that block `deep-testing`.

## Promotion criteria

Promoted to `promising` in EXP-0022 because it has:

- deterministic executable wrapper in `scripts/cut_limited_loop_repair.py`;
- written loop-cut specification;
- measured operation counts;
- full replay and negative rejection on the targeted short-loop smoke/deep cases;
- a concrete advantage over `ALG-0003` and exact automaton baselines by replaying a held-out second loop iteration.

It is not `deep-testing` or `super-promising`. The scope is narrow, one-iteration-only logs currently fall back poorly, and multi-body or bounded-count loop behavior remains unstudied.

## Experiment links

- EXP-0022: targeted loop tests and standard-suite reruns.
- EXP-0023: loop-boundary stress tests.

## Property-study notes

No property dossier.

## Decision history

- EXP-0022: implemented and promoted to `promising`; no property dossier because the candidate is not `super-promising`.
- EXP-0023: retained at `promising`; stress tests exposed bounded-count and multi-body limitations.
- EXP-0024: kept as the singleton-loop reference candidate while multi-body loop choice moved to `ALG-0024`.
