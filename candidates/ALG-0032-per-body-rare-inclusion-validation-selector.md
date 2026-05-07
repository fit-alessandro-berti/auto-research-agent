# ALG-0032 - Per-Body Rare Inclusion Validation Selector

## Status

smoke-tested

## One-sentence hypothesis

External validation probes can select a bounded per-body keep/drop vector for rare loop bodies, repairing mixed valid/noisy rare-body cases that group keep/filter selectors cannot distinguish.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0025` emits a length-bounded multi-body rework-loop PMIR.
- A dominant loop body satisfies an explicit support threshold.
- At most `max_rare_bodies` non-dominant bodies have the configured `rare_body_count`.
- Validation positives and negatives are separate from final probes and are allowed to encode external domain evidence.

Default selector policy in the prototype:

- `min_dominant_count = 5`;
- `min_dominant_share = 5/7`;
- `rare_body_count = 1`;
- `max_rare_bodies = 2`.

## Output

- PMIR:
  - source `ALG-0025` loop evidence;
  - per-body selector configuration;
  - dominance context;
  - bounded inclusion-vector scores;
  - selected dropped/kept body set, or an unresolved/budget/conflict status.
- Petri net:
  - selected keep-all `ALG-0025` net, or a guarded recompilation with the chosen dropped bodies removed;
  - if unresolved, the upstream net is retained only for compatibility and must not be treated as a selected policy.
- Other:
  - selector operation counts;
  - validation replay proxy counts;
  - naive all-alternative discovery totals;
  - selector-integrated shared operation-accounting totals.

## Intermediate representation

`ALG-0025` process-tree loop PMIR plus a per-body inclusion-vector selector:

- dominant body and support;
- rare candidate bodies;
- all bounded drop subsets;
- per-subset validation replay/negative-probe scores;
- selected subset when exactly one assignment satisfies validation.

## Allowed operations / operation-cost model

Uses only the first-goal primitive operations:

- `scan_event` for validation replay proxy events and trace/body partitioning;
- `comparison` for threshold checks, validation conflicts, score comparisons, and body matching;
- `arithmetic` for dominant-share and score arithmetic;
- `construct` for alternatives, selector rows, and guarded Petri-net recompilation;
- inherited `set_lookup`, `set_insert`, `dict_increment`, and `relation_classification` counts from upstream discovery/recompilation.

Expected prototype cost:

```text
ALG-0025 discovery
+ O(B) dominance and rare-body checks
+ O(2^R * (T * L + compile_guarded_net + validation_proxy))
```

where `B` is the number of loop-body alternatives, `R <= max_rare_bodies`, `T` is trace count, and `L` is maximum trace length. The exponential factor is deliberately capped; the prototype refuses selection with `too_many_rare_bodies` when the cap is exceeded.

EXP-0038 selector-integrated shared-accounting convention:

```text
one ALG-0025 base discovery
+ sum(max(0, alternative_total - drop_none_total) for non-base alternatives)
+ selector scoring counts
+ validation replay proxy counts
```

The selector output carries both the original naive total and the shared total. `experiments/selector-shared-cost-report.json` cross-checks the integrated fields against the same derivation.

## Algorithm sketch

1. Run `ALG-0025`.
2. Require the selected cut to be `multi_body_rework_loop`.
3. Extract body support and check the declared dominant-body threshold.
4. Identify non-dominant bodies with count equal to `rare_body_count`.
5. If the rare-body count exceeds `max_rare_bodies`, return `too_many_rare_bodies`.
6. Enumerate all bounded drop subsets over rare bodies.
7. Compile each subset by keeping all non-dropped bodies; the empty subset reuses the upstream keep-all net.
8. Replay validation positives and run negative probes for every alternative.
9. Select only when exactly one alternative replays all validation positives and rejects all validation negatives.
10. Return conflict statuses for positive/negative validation overlap and training-negative overlap.

## Expected complexity

For fixed `max_rare_bodies` and fixed maximum body length `M=2`, the selector adds bounded constant-factor work over `ALG-0025`. Without the cap, per-body inclusion vectors would be exponential in the number of rare bodies and should not be considered a limited-operation candidate.

## Smoke tests

Command:

```bash
python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json
```

EXP-0035 result: 11/11 cases passed.

Key controls:

- one rare valid: keep it;
- one rare noise: drop it;
- two rare bodies, one valid and one noise: keep `C`, drop `E`;
- two rare bodies both valid: keep both;
- two rare bodies both noise: drop both;
- count-two rare bodies with explicit `5/9` policy: split valid `C` from noisy `E`;
- partial validation signal: unresolved;
- validation conflict and training-negative conflict: detected;
- too many rare bodies: budget refusal;
- weak dominance: no selection.

Additional split validation/final protocol:

Command:

```bash
python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json
```

EXP-0036 result: 13/13 cases passed.

Key additions:

- split final generalization for singleton, length-2, mixed-width, and count-two length-2 rare bodies;
- direct `ALG-0029` and `ALG-0030` baseline unresolved comparisons on mixed valid/noisy rare-body cases;
- validation/final overlap and training-negative conflict controls;
- final-probe-not-used ambiguity control;
- cap boundary with three rare bodies allowed (`8` alternatives) and cap refusal with the default cap;
- duplicate suffix-label, overlapping body-label, and wrong-rare-count blocked-scope controls.

Cap and operation-budget stress:

Command:

```bash
python3 scripts/alg0032_cap_stress_tests.py --out experiments/alg0032-cap-stress-tests.json
```

EXP-0039 result: 11/11 cases passed.

Key observations:

- one rare body is under the deep soft budget for both base selection and non-base drop selection;
- two rare bodies are already over the deep soft budget even with selector-integrated shared accounting;
- selected alternatives grow as `2^R`: 4, 8, 16, and 32 alternatives for `R=2..5`;
- cap-plus-one refusals build zero alternatives, keep validation replay proxy at zero, have no shared savings, and stay under the deep soft budget;
- all shared-accounting identities matched the integrated operation-count fields.

| Case | Status | Alternatives | Shared total | Naive total | Deep budget |
|---|---|---:|---:|---:|---:|
| `rare_count_1_cap_1_selected_under_budget` | `selected` | 2 | 677 | 1083 | 778 |
| `rare_count_1_cap_1_drop_nonbase_under_budget` | `selected` | 2 | 692 | 1098 | 778 |
| `rare_count_2_cap_2_selected_over_budget` | `selected` | 4 | 1434 | 2931 | 970 |
| `rare_count_3_cap_3_selected_over_budget` | `selected` | 8 | 3167 | 7430 | 1186 |
| `rare_count_4_cap_4_selected_over_budget` | `selected` | 16 | 7096 | 18061 | 1426 |
| `rare_count_5_cap_5_selected_over_budget_reference` | `selected` | 32 | 15949 | 42764 | 1690 |

## Baselines for comparison

- `ALG-0025` keep-all length-bounded loop miner.
- `ALG-0028` support-prior group filter.
- `ALG-0029` keep-all versus group-filter validation selector.
- `ALG-0031` count-two group-filter ablation.

## Metrics

- Validation selection status and reason.
- Selected dropped and kept bodies.
- Final positive replay and final negative rejection for selected cases.
- Alternative count and budget-refusal behavior.
- Selector primitive counts and validation replay proxy counts.
- Naive all-alternative discovery total.
- Selector-integrated shared all-alternative discovery and validation-proxy total.

## Known failure modes

- Not a training-log-only discovery rule; validation evidence is required for selection.
- Exponential inclusion vectors are only controlled by `max_rare_bodies`.
- Partial validation signal stays unresolved when an unprobed rare body can be kept or dropped without changing validation score.
- Inherits `ALG-0025` limits: body length greater than two, duplicate/overlapping labels, one-iteration-only evidence, and upstream cut failures.
- Selector outputs now include shared totals, but the breakdown is still derived from total fields rather than primitive-level shared instrumentation.
- Validation representativeness is an assumption, not proven.
- `EXP-0036` shows the cap-three case can reach a naive total of 7430 operations on a small toy log. EXP-0038 reports 3167 selector-integrated shared operations for that case, but this remains above the deep soft budget and keeps cap stress as a promotion blocker.
- EXP-0039 shows the budget boundary is lower than the cap-three case: selected exhaustive enumeration exceeds the deep soft budget from two rare bodies onward, while cap-plus-one refusals remain cheap.

## Promotion criteria

Do not promote beyond `smoke-tested` unless:

- split train/validation/final tests are expanded beyond the current toy controls;
- `ALG-0029` and `ALG-0031` comparisons show repeated mixed rare-body advantage;
- operation accounting has a primitive-level shared breakdown;
- budget behavior is stress-tested for larger rare-body counts;
- or a lower-cost bounded validation rule replaces exhaustive per-body enumeration;
- upstream blocked-scope cases are either fixed or formally scoped out.

## Experiment links

- EXP-0035: per-body rare inclusion selector and counterexample controls.
- EXP-0036: split validation/final protocol, width controls, cap boundary/refusal, and blocked-scope controls.
- EXP-0037: shared operation-accounting report for `ALG-0029`, `ALG-0030`, and `ALG-0032`.
- EXP-0038: selector-integrated shared operation-count fields and report cross-checks.
- EXP-0039: cap and operation-budget stress for one through five rare bodies.

## Property-study notes

No property dossier. The candidate is not `super-promising`.

Potential future property question: conditional selector correctness can be stated only relative to a fixed validation objective and bounded alternative set; it should not be stated as true process-identification correctness.

## Decision history

- EXP-0035: added as `smoke-tested`. It repairs the mixed valid/noisy rare-body limitation of `ALG-0029`/`ALG-0031` on controlled cases, but remains validation-scoped with naive operation accounting and a bounded alternative cap.
- EXP-0036: split validation/final protocol passed 13/13 cases and added direct `ALG-0029`/`ALG-0030` unresolved baseline comparisons. Kept at `smoke-tested` because shared operation accounting and broader non-toy validation remain unresolved.
- EXP-0037: shared accounting report reduces the cap-three case from 7430 naive operations to 3167 shared operations. Kept at `smoke-tested` because the accounting was still external at that point, validation-scoped, and above budget at the cap boundary.
- EXP-0038: integrated the same shared totals into selector outputs and verified them with the shared-cost report. Kept at `smoke-tested` because primitive-level shared breakdowns, validation representativeness, cap stress, and upstream blocked-scope repairs remain open.
- EXP-0039: cap stress passed 11/11 and confirmed cap-plus-one refusals are cheap, but selected exhaustive enumeration exceeds the deep soft budget from two rare bodies onward. Kept at `smoke-tested`; this strengthens the cost blocker rather than supporting promotion.
