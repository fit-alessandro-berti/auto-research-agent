# ALG-0029 - Loop Body Inclusion Validation Selector

## Status

smoke-tested

## One-sentence hypothesis

Explicit validation positives and negatives can select whether to keep all observed loop bodies or apply an `ALG-0028` support guard when body inclusion is ambiguous under training support alone.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0025` can emit a length-bounded rework-loop body-choice net.
- `ALG-0028` can emit a support-guarded alternative over the same training log.
- Validation traces are separated into:
  - positives that should replay;
  - negatives that should be rejected.
- Validation data is an additional signal. The selector does not claim the training log alone identifies whether a rare observed body is valid or noise.

## Output

- Benchmark-compatible Petri net:
  - selected `keep_all_bodies` alternative from `ALG-0025`;
  - selected `support_guard` alternative from `ALG-0028`;
  - upstream `ALG-0025` output only as compatibility output when unresolved or inconsistent.
- PMIR evidence under `body_inclusion_validation_selector`:
  - selected alternative;
  - selection status and reason;
  - validation overlap;
  - training-negative overlap;
  - selector and validation replay proxy counts;
  - per-alternative validation scores.

## Intermediate representation

Body-inclusion alternative set:

- `keep_all_bodies`: `ALG-0025` result.
- `support_guard`: `ALG-0028` result under the configured support policy.
- Validation score table over both alternatives.

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- comparisons for validation overlap checks, training-negative conflict checks, score comparison, and tie detection;
- arithmetic for validation hit/miss scores;
- construction for score/evidence records;
- validation replay proxy counts of one `scan_event` per validation event and one `comparison` per validation trace per alternative.

Measured selector evidence also records the naive discovery cost of both alternatives. This intentionally over-counts reusable upstream work but makes the first prototype reproducible.

## Algorithm sketch

1. Run `ALG-0025` on the training log as `keep_all_bodies`.
2. Run `ALG-0028` on the training log as `support_guard`.
3. Evaluate both alternatives on validation positives and negatives.
4. If a validation trace is both positive and negative, return `validation_inconsistent`.
5. If a validation negative is an observed training trace, return `validation_training_conflict`.
6. Score each alternative by:
   - whether all validation positives replay and all validation negatives reject;
   - total validation hits;
   - accepted-negative penalty.
7. Select only if exactly one alternative satisfies all validation probes.
8. Return unresolved on ties or when no alternative satisfies validation.

## Expected complexity

`O(C_0025 + C_0028 + P * validation_replay_proxy + P + Vp + Vn + T)` with `P=2` alternatives, `Vp` validation positives, `Vn` validation negatives, and `T` training traces for training-negative conflict checks.

## Smoke tests

Command: `python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json`

| Case | Expected | Selected | Status | Naive total with alternatives + validation proxy | Interpretation |
|---|---|---|---|---:|---|
| `validation_selects_keep_rare_3_to_1` | `keep_all_bodies` | `keep_all_bodies` | `selected` | 897 | Rare body is explicitly validated, so support filtering is overridden. |
| `validation_selects_filter_rare_3_to_1` | `support_guard` | `support_guard` | `selected` | 903 | Rare-body combinations are validation negatives, so filtering is selected. |
| `validation_no_body_signal_unresolved` | none | none | `unresolved` | 906 | Validation does not distinguish alternatives. |
| `validation_training_conflict` | none | none | `validation_training_conflict` | 884 | Marking an observed training trace negative is reported as conflict. |
| `validation_positive_negative_conflict` | none | none | `validation_inconsistent` | 903 | Positive/negative validation overlap is reported as inconsistent. |

## Split validation/final protocol

Command: `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`

EXP-0033 adds a frozen train/validation/final split similar to `ALG-0027`.

| Case | Expected | Selected | Status | Leakage | Final result | Naive total |
|---|---|---|---|---:|---|---:|
| `body_keep_final_generalization` | `keep_all_bodies` | `keep_all_bodies` | `selected` | no | 1/1 final positives, 2/2 negatives rejected | 906 |
| `body_filter_final_precision` | `support_guard` | `support_guard` | `selected` | no | 1/1 final positives, 2/2 negatives rejected | 903 |
| `body_no_signal_final_not_used` | none | none | `unresolved` | no | final probes not used for selection | 906 |
| `body_validation_final_overlap_guard` | `keep_all_bodies` | `keep_all_bodies` | `selected` | yes | excluded from promotion-quality evidence | 897 |
| `body_training_negative_conflict_final_control` | none | none | `validation_training_conflict` | yes | conflict control | 884 |
| `body_positive_negative_overlap` | none | none | `validation_inconsistent` | no | conflict control | 903 |
| `body_support_ratio_5_to_1_keep` | `keep_all_bodies` | `keep_all_bodies` | `selected` | no | 1/1 final positives, 1/1 negatives rejected | 1104 |
| `body_length2_rare_filter` | `support_guard` | `support_guard` | `selected` | no | 1/1 final positives, 1/1 negatives rejected | 1503 |
| `two_rare_one_valid_one_noise_unresolved` | none | none | `unresolved` | no | alternatives cannot split individual rare bodies | 1060 |
| `rare_count_two_noise_unresolved` | none | none | `unresolved` | no | support guard does not filter count-two rare bodies | 947 |

## Baselines for comparison

- `ALG-0025` keep-all body inclusion.
- `ALG-0028` support-prior filtering.
- `ALG-0027` loop-count validation selector, as a count-policy analogue.
- `ALG-0030` body-count product selector, as a composition protocol.

## Metrics

- Selected body-inclusion alternative.
- Selection status and reason.
- Validation positive replay.
- Validation negative rejection.
- Training-negative overlap.
- Selector operation counts.
- Validation replay proxy counts.
- Naive all-alternative discovery cost.

## Known failure modes

- Requires external validation data.
- Validation can be contradictory or conflict with training replay.
- If validation does not mention the rare body, selection remains unresolved.
- It inherits `ALG-0025` and `ALG-0028` body-shape limits.
- Naive all-alternative cost double-counts upstream discovery that could be shared in a later optimized selector.
- Two rare bodies with one valid and one noisy body remain unresolved because the current alternatives keep all rare bodies or filter all singleton rare bodies together.
- Rare-body count two remains outside the current support-guard scope.

## Promotion criteria

Do not promote beyond `smoke-tested` until:

- validation replay cost is refined beyond the current proxy;
- individual rare-body filtering is studied for two-rare-body mixed valid/noise cases;
- rare-count-two support/noise behavior gets its own policy or selector;
- interactions with `ALG-0030` are stress-tested beyond the four first product quadrants.

## Experiment links

- EXP-0032: first threshold ablation and validation-selector smoke tests.
- EXP-0033: split validation/final protocol, leakage controls, support-ratio/body-width controls, and product-composition smoke tests.

## Property-study notes

No property dossier. The candidate is not `super-promising`. Future property work should define selector correctness relative to explicit validation assumptions and conflict handling.

## Decision history

- EXP-0032: added as a smoke-tested selector protocol. It can select keep-all or support-guarded body inclusion when validation distinguishes them, and returns unresolved or conflict statuses when validation is insufficient or inconsistent. Not promoted because it lacks split final-test validation and broader support-ratio coverage.
- EXP-0033: split validation/final tests pass and composition with count-policy selection is smoke-tested through `ALG-0030`. Kept at `smoke-tested` because validation replay cost is still a proxy and mixed rare-body / count-two rare-body limits remain unresolved.
