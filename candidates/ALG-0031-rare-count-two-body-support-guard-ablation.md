# ALG-0031 - Rare-Count-Two Body Support Guard Ablation

## Status

smoke-tested

## One-sentence hypothesis

Raising the `ALG-0028` rare-body filter from count one to count two can reject repeated rare-body noise under a declared support prior, but it remains a policy ablation rather than an identifiable discovery rule.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0025` emits length-bounded rework-loop body evidence.
- A dominant loop body has support at least five.
- A non-dominant body appears exactly twice.
- The configured support policy uses:
  - `min_dominant_count = 5`;
  - `min_dominant_share = 5/7`;
  - `rare_body_count = 2`.

## Output

Same output shape as `ALG-0028`:

- PMIR with support-guard evidence;
- Petri net compiled from the kept loop bodies when filtering applies;
- fallback to the upstream `ALG-0025` result when the policy does not apply.

## Intermediate representation

`ALG-0025` loop-body support PMIR plus a configured support-policy annotation:

- dominant body;
- count-two rare bodies;
- kept bodies;
- filtered bodies;
- source loop evidence.

## Allowed operations / operation-cost model

Same counted primitives as `ALG-0028`:

- comparisons and arithmetic for dominant-share checks;
- set lookups and scan events for trace/body partitioning;
- construction for PMIR records and guarded Petri-net recompilation.

The expected cost is `ALG-0025` discovery plus `O(B)` support-policy checks, and, when filtering applies, `O(T * L)` body partitioning plus bounded loop-net recompilation for fixed body length `M=2`.

## Algorithm sketch

1. Run `ALG-0025`.
2. Read loop-body support counts from the selected process-tree evidence.
3. Apply `ALG-0028.discover_with_policy(...)` with `rare_body_count=2` and a five-of-seven dominant share.
4. Filter all non-dominant bodies with count two if the dominant support threshold passes.
5. Recompile the guarded loop body set.

## Smoke tests

Command: `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`

Relevant controls:

| Case | Expected | Observed | Interpretation |
|---|---|---|---|
| `rare_count_two_default_body_unresolved` | no body selection | `body_unresolved` | Default `ALG-0028` count-one policy does not filter count-two rare bodies. |
| `rare_count_two_configured_filter_unbounded` | `support_guard + unbounded_repeat` | selected | Count-two policy can filter rare-count-two noise when validation says repeated rare combinations are invalid. |
| `rare_count_two_configured_keep_all_at_most_once` | `keep_all_bodies + at_most_once` | selected | Validation can override the count-two support prior when the rare body is valid. |
| `two_rare_count_two_one_valid_one_noise_unresolved` | no body selection | `body_unresolved` | Group filtering cannot keep one count-two rare body while filtering another. |

## Baselines for comparison

- `ALG-0025` keep-all body inclusion.
- `ALG-0028` count-one rare-body support guard.
- `ALG-0029` validation selector over keep-all versus support-guarded body inclusion.
- `ALG-0030` product selector over body inclusion and count policy.

## Metrics

- Whether the support guard applies.
- Selected body-inclusion alternative under `ALG-0030`.
- Final positive replay and negative rejection for the selected product.
- Operation counts from the product stress protocol.

## Known failure modes

- Count-two filtering is still a support prior, not an identifiable training-log-only claim.
- It can drop valid rare behavior unless validation selects keep-all instead.
- It filters count-two rare bodies as a group; it cannot keep one rare body and filter another under the same support count.
- It inherits `ALG-0025` body-length, duplicate-label, and one-iteration-only limits.

## Promotion criteria

Do not promote beyond `smoke-tested` unless:

- broader count-two rare-body cases distinguish valid from noisy rare behavior using explicit validation or domain priors;
- per-body inclusion alternatives are studied for mixed valid/noise rare bodies;
- operation counts are reported outside the `ALG-0030` product wrapper;
- the rule shows a concrete advantage over `ALG-0028` without causing unacceptable valid-rare loss.

## Experiment links

- EXP-0034: product stress and rare-count-two support-policy controls.

## Property-study notes

No property dossier. The candidate is not `super-promising`.

## Decision history

- EXP-0034: added as a smoke-tested ablation. It can filter count-two rare-body noise under explicit validation, but group filtering fails the one-valid-one-noisy count-two rare-body control.
