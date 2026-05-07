# ALG-0030 - Loop Body-Count Validation Product Selector

## Status

smoke-tested

## One-sentence hypothesis

Loop-body inclusion and loop-count semantics should be selected as separate validation-scoped axes, then compiled as a product policy, rather than allowing rare-body noise evidence to masquerade as a loop-count decision.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0029` can select or reject rare loop-body inclusion from explicit body-validation probes.
- The selected body-inclusion result still carries a process-tree loop PMIR that can be passed to the `ALG-0026` count-policy compiler.
- Count-validation positives and negatives are distinct from body-validation probes and from final-test probes.
- Validation is an external signal. The candidate does not claim the event log alone identifies either axis.

## Output

- Benchmark-compatible Petri net:
  - selected body-inclusion alternative;
  - selected loop-count policy over that body-inclusion alternative;
  - compatibility fallback when either axis is unresolved.
- PMIR evidence under `body_count_validation_product_selector`:
  - selected body alternative;
  - selected count policy;
  - body-selector and count-selector statuses;
  - count validation scores;
  - selector and validation replay proxy counts.
  - selector-integrated shared operation-accounting totals.

## Intermediate representation

Cartesian policy product:

- body-inclusion axis: `keep_all_bodies` or `support_guard`;
- count-policy axis: `unbounded_repeat` or `at_most_once`;
- a selected product only when both axes are uniquely identified by their own validation probes.

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- body-axis costs are inherited from `ALG-0029`;
- count-axis validation replay proxy counts one `scan_event` per validation event and one `comparison` per validation trace per count alternative;
- selector scoring uses comparisons, arithmetic, and construction operations;
- at-most-once compilation reuses the `ALG-0026` construction pattern.

The prototype retains its naive product total and, since EXP-0038, also reports selector-integrated shared product totals: the shared body-axis total from `ALG-0029`, selected or all count-policy compile extras, count-selector costs, and count-validation replay proxy counts.

## Algorithm sketch

1. Run `ALG-0029` on body-validation positives and negatives.
2. If body selection is not unique, return a `body_unresolved` product decision.
3. Build an `ALG-0026` loop-count policy set from the selected body-inclusion result.
4. Score count alternatives on count-validation positives and negatives.
5. If no count-policy set exists, or no unique count policy satisfies validation, return `count_unresolved`.
6. If both axes select uniquely, return the selected product Petri net.

## Expected complexity

`O(C_0029 + C_count_compile + P_count * count_validation_replay_proxy + P_count + Vp_count + Vn_count)` with two body alternatives and at most two count alternatives.

## Smoke tests

Command: `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`

Joint selector controls:

- `keep_all_unbounded_joint`;
- `keep_all_at_most_once_joint`;
- `filter_unbounded_joint`;
- `filter_at_most_once_joint`;
- `body_selected_count_unresolved`;
- `count_selected_body_unresolved`.

## Stress tests

Command: `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`

EXP-0034 adds 20 product-stress controls:

- 4 length-2 body product quadrants;
- 8 mixed-width product quadrants across singleton-dominant and length-2-dominant directions;
- 4 blocked-scope controls for duplicate suffix labels, overlapping body labels, length greater than two, and one-iteration-only evidence;
- 4 rare-count-two controls, including configured count-two filtering and mixed valid/noisy rare bodies.

All 20 cases pass. The result strengthens the stress evidence for `ALG-0030` but does not promote it because the protocol remains validation-scoped and blocked-scope cases still depend on upstream rejection.

## Baselines for comparison

- `ALG-0027` loop-count validation selector.
- `ALG-0029` body-inclusion validation selector.
- `ALG-0025` keep-all body inclusion and unbounded repeat.
- `ALG-0028` support-prior body filtering.

## Metrics

- Selected body-inclusion alternative.
- Selected loop-count policy.
- Product selection status.
- Final positive replay and final negative rejection.
- Per-axis selector operation counts.
- Per-axis validation replay proxy counts.
- Naive and selector-integrated shared product operation totals.

## Known failure modes

- Requires two validation channels or an explicitly partitioned validation set.
- If body selection is unresolved, count selection is not used to infer body inclusion.
- If count selection is unresolved, body selection is not treated as a complete product model.
- It inherits the upstream loop detector's length, duplicate-label, and one-iteration-only limits.
- Shared operation totals are integrated into selector output, but they are still derived from total fields rather than primitive-level shared instrumentation.
- Rare-count-two support policies require separate ablation tracking (`ALG-0031`) and can still fail mixed valid/noisy rare-body cases.

## Promotion criteria

Do not promote beyond `smoke-tested` until:

- split validation/final protocols cover all four selected product quadrants;
- one-axis-identifiable controls remain unresolved on the other axis;
- validation/final leakage is checked explicitly;
- count-policy compilation from guarded body results is stress-tested on body widths beyond the current controls;
- operation accounting has a primitive-level shared breakdown.

## Experiment links

- EXP-0033: first split validation/final tests for `ALG-0029` and composition smoke tests for `ALG-0030`.
- EXP-0034: widened product stress tests for length-2, mixed-width, blocked-scope, and rare-count-two policy cases.
- EXP-0038: selector-integrated shared product operation totals and report cross-checks.

## Property-study notes

No property dossier. The candidate is not `super-promising`.

## Decision history

- EXP-0033: added as a smoke-tested product selector after all four joint product quadrants and two unresolved-axis controls passed targeted tests. Not promoted because the protocol is still synthetic and the product operation count is a naive upper bound.
- EXP-0034: kept at `smoke-tested` after 20/20 stress cases passed. Width robustness improved, but duplicate-label, length >2, one-iteration-only, mixed rare-body filtering, and shared-cost accounting still block promotion.
- EXP-0038: integrated conservative shared product totals into selector outputs and verified the report derivation. Kept at `smoke-tested` because primitive-level accounting, validation-scope limits, and upstream blocked scopes remain open.
