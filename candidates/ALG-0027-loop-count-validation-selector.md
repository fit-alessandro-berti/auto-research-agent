# ALG-0027 - Loop Count Validation Selector

## Status

promising

## One-sentence hypothesis

If an `ALG-0026` loop-count policy set is given explicit validation positives and negatives, a deterministic selector can choose unbounded-repeat or at-most-once only when one policy uniquely satisfies the validation probes.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0026` can emit a loop-count policy set from bounded-count ambiguous loop evidence.
- External validation traces are separated into:
  - validation positives that should replay;
  - validation negatives that should be rejected.
- Validation data is an explicit additional signal. The selector does not claim the training log alone identifies the loop-count policy.

## Output

- Benchmark-compatible Petri net:
  - selected alternative when a unique policy satisfies validation probes;
  - upstream selected net only as compatibility output when unresolved.
- PMIR evidence: `loop_count_validation_selector` with validation counts, selected policy, selection status, reason, validation overlap, selector operation counts, and per-policy scores.

## Intermediate representation

`ALG-0026` loop policy set plus selector evidence:

- `selected_policy`
- `selection_status`
- `reason`
- `scores`
- `validation_overlap`
- `selector_operation_counts`
- `validation_replay_proxy_counts`

## Allowed operations / operation-cost model

Uses the first-goal primitive operations for the selector itself:

- comparisons for validation-overlap checks, score comparisons, and tie detection;
- arithmetic for validation hit/miss scores;
- construction for score/evidence records.

Validation replay uses the existing token-game evaluator. In EXP-0028 it was reported as selector evidence while primitive selector counts were tracked separately as `selector_operation_counts`.

Expected selector cost after `ALG-0026` is `O(P + Vp + Vn)` score/comparison work for `P` policy alternatives, `Vp` validation positives, and `Vn` validation negatives, plus the replay cost of evaluating alternatives on validation traces.

From EXP-0029 onward, validation replay has an explicit proxy count: for each policy alternative and each validation trace, count one `scan_event` per event and one `comparison` for the trace outcome. This is a declared validation-work budget, not a full token-game transition/reachability cost.

## Algorithm sketch

1. Run `ALG-0026` on the training log.
2. If no loop-count policy set is emitted, return `selection_status=no_policy_set`.
3. Evaluate each policy alternative on validation positives and validation negatives.
4. If any validation trace appears in both positive and negative sets, return `selection_status=validation_inconsistent`.
5. Score each policy by:
   - whether it replays all validation positives and rejects all validation negatives;
   - total validation hits;
   - accepted-negative penalty.
6. Select only if exactly one policy satisfies all validation probes.
7. Return unresolved on ties or when no policy satisfies all probes.

## Expected complexity

`O(C_0026 + P * validation_replay_cost + P + Vp + Vn)` with `P=2` in the current loop-count policy set. The selector is deterministic and batch-only.

## Smoke tests

Primary gates:

- `single_rework_selects_unbounded`
- `single_rework_selects_at_most_once`
- `multi_body_selects_unbounded`
- `multi_body_selects_at_most_once`
- `length2_selects_unbounded`
- `length2_selects_at_most_once`
- `mixed_width_selects_unbounded`

Controls:

- `no_discriminator_unresolved`
- `conflicting_validation_unresolved`
- `optional_skip_no_policy_set`

## Baselines for comparison

- `ALG-0026` loop-count policy-set protocol.
- `ALG-0023`, `ALG-0024`, and `ALG-0025` unbounded selected-net candidates.

## Metrics

- Selected policy.
- Selection status and reason.
- Validation positive replay.
- Validation negative rejection.
- Selector operation counts.
- Validation replay proxy operation counts.
- Per-policy validation scores.

## Known failure modes

- Requires external validation data or declared priors; without them the selector must remain unresolved.
- Validation traces can be inconsistent or leak final-test evidence.
- It does not rescue cases where `ALG-0026` emits no policy set.
- It inherits upstream body-length and duplicate-label limits.
- It selects loop-count policy only; it does not decide whether a low-support observed loop body should be treated as valid behavior or noise.
- Validation replay proxy counts are lower bounds on the actual token-game evaluator work.

## EXP-0028 Results

Command: `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`

| Case | Expected | Selected | Status | Validation pos | Validation neg | Selector ops |
|---|---|---|---|---:|---:|---:|
| `single_rework_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 1/1 | 3/3 | 21 |
| `single_rework_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 3/3 | 20 |
| `multi_body_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 3/3 | 22 |
| `multi_body_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 4/4 | 21 |
| `length2_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 3/3 | 22 |
| `length2_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 4/4 | 21 |
| `mixed_width_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 4/4 | 23 |
| `no_discriminator_unresolved` | none | none | `unresolved` | 2/2 | 2/2 | 21 |
| `conflicting_validation_unresolved` | none | none | `validation_inconsistent` | 1/1 | 0/1 | 19 |
| `optional_skip_no_policy_set` | none | none | `no_policy_set` | 1/1 | 3/3 | 4 |

## EXP-0029 Results

Command: `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`

| Case | Expected | Selected | Status | Leakage | Final positives | Final negatives | Selector ops | Validation replay proxy ops |
|---|---|---|---|---:|---:|---:|---:|---:|
| `single_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 1/1 | 2/2 | 20 | 30 |
| `single_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 22 |
| `multi_body_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 2/2 | 2/2 | 20 | 30 |
| `multi_body_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 22 |
| `length2_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 1/1 | 2/2 | 20 | 36 |
| `mixed_width_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 24 |
| `no_discriminator_remains_unresolved` | none | none | `unresolved` | no | 1/1 | 1/1 | 19 | 16 |
| `optional_skip_no_policy_set_final_control` | none | none | `no_policy_set` | no | 0/0 | 1/1 | 2 | 0 |
| `leakage_guard_reports_validation_final_overlap` | `unbounded_repeat` | `unbounded_repeat` | `selected` | yes | 1/1 | 1/1 | 19 | 22 |

## EXP-0030 Results

Command: `python3 scripts/alg0027_upstream_limit_tests.py --out experiments/alg0027-upstream-limit-tests.json`

| Case | Expected | Selected | Status | Policy set | Final positives | Final negatives | Interpretation |
|---|---|---|---|---:|---:|---:|---|
| `one_iteration_only_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | No zero-iteration evidence, so no upstream count ambiguity exists. |
| `duplicate_suffix_label_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Duplicate body/suffix label context remains blocked upstream. |
| `length3_body_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Body length greater than two remains outside the bounded detector. |
| `overlapping_body_labels_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Overlapping body labels remain blocked upstream. |
| `rare_body_valid_unbounded_control` | `unbounded_repeat` | `unbounded_repeat` | `selected` | yes | 1/1 | 2/2 | Rare observed body is treated as valid when validation requires it. |
| `rare_body_noise_gap` | `at_most_once` | `at_most_once` | `selected` | yes | 0/0 | 0/1 | Count selection does not remove a rare observed body treated as noise. |
| `rare_body_noise_training_conflict` | none | none | `unresolved` | yes | 0/0 | 0/1 | Marking an observed rare body invalid conflicts with training evidence. |

## Promotion criteria

`ALG-0027` is `promising` because it:

- deterministically selects both unbounded-repeat and at-most-once policies when validation traces distinguish them;
- remains unresolved on non-discriminating validation;
- detects contradictory validation overlap;
- emits no loop-count selection when `ALG-0026` has no policy set;
- reports selector operation counts, validation replay proxy counts, and per-policy scores;
- passes a frozen train/validation/final-test split protocol on singleton, multi-body, length-2, and mixed-width loop evidence;
- has a concrete advantage over `ALG-0026` as a model-set-only protocol: it can choose a final policy when external validation evidence exists, while preserving unresolved behavior when it does not.

It is not moved to `deep-testing` because EXP-0030 confirms upstream and scope limits: one-iteration-only evidence, duplicate labels, and body length greater than two emit no policy set, and rare-body/noise validity is a separate support-policy problem. The replay proxy also remains a lower-bound cost model.

## Experiment links

- EXP-0028: targeted loop-count validation selector tests.
- EXP-0029: split train/validation/final-test protocol with validation replay proxy counts.
- EXP-0030: upstream-limit stress tests for one-iteration-only, duplicate labels, length >2 bodies, and rare-body/noise ambiguity.

## Property-study notes

No property dossier. Future property work should define selector soundness relative to validation assumptions, leakage risks, deterministic tie behavior, and how validation replay cost should be counted.

## Decision history

- EXP-0028: added as a validation selector for `ALG-0026`; kept at `smoke-tested` because it needs a broader validation protocol before promotion.
- EXP-0029: promoted to `promising` after passing split validation/final-test protocol cases and adding validation replay proxy operation counts.
- EXP-0030: kept at `promising`; upstream-limit stress shows blockers for `deep-testing` and motivates a separate rare-body support/noise candidate.
