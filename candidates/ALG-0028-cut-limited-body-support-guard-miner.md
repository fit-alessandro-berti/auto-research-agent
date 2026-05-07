# ALG-0028 - Cut-Limited Body-Support Guard Miner

## Status

smoke-tested

## One-sentence hypothesis

If a length-bounded rework-loop body has only singleton support under a clearly dominant body alternative, a conservative support prior can improve precision by filtering the singleton body as likely noise while keeping balanced or low-sample cases ambiguous.

## Input assumptions

- Batch event log with activity-label traces.
- `ALG-0025` emits a `multi_body_rework_loop` process-tree cut.
- Supported loop shape is inherited from `ALG-0025`:
  - zero iteration: `prefix anchor suffix`;
  - one iteration: `prefix anchor body_i anchor suffix`;
  - each observed body has length one or two;
  - body labels do not overlap with each other, the anchor, prefix, or suffix.
- The support guard is a precision prior, not an identifiable discovery claim. A filtered singleton body may be valid rare behavior.

## Output

- PMIR/process-tree evidence:
  - upstream `ALG-0025` source evidence;
  - `support_guard` policy evidence;
  - `body_support_guard_rework_loop` process tree when filtering applies;
  - kept and filtered body lists;
  - `rare_body_ambiguous=true`.
- Petri net:
  - if no filtering applies, the upstream `ALG-0025` net retagged as `ALG-0028`;
  - if filtering applies, a loop net compiled only from kept bodies.

## Intermediate representation

`ALG-0025` length-bounded loop PMIR plus support-policy annotations:

- `dominant_body`
- `dominant_count`
- `total_body_observations`
- `kept_bodies`
- `filtered_bodies`
- `support_policy`
- `rare_body_ambiguous`
- source process-tree evidence

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- event scans to identify each trace's loop body during filtering;
- comparisons for source-cut checks, support thresholds, prefix/anchor/suffix matching, and policy decisions;
- set lookups for filtered-body membership;
- arithmetic for dominant-share checks;
- construction operations for policy evidence, filtered logs, PMIR records, and loop-net arcs/places.

Measured counts include upstream `ALG-0025` discovery, guard policy work, and guarded recompilation when filtering applies.

## Algorithm sketch

1. Run `ALG-0025` on the training log.
2. If no `multi_body_rework_loop` is selected, return the upstream net with support-guard evidence marked `applied=false`.
3. Read upstream `body_support`.
4. By default, filter only when all hold:
   - max body count is at least 3;
   - dominant body share is at least 75%;
   - a non-dominant body has count exactly 1;
   - at least one body remains after filtering.
5. Treat filtered bodies as noise-prior exclusions and record `rare_body_ambiguous=true`.
6. Recompile the loop using only kept bodies. A single kept body is compiled with the same length-bounded loop wiring so length-2 dominant bodies remain repeatable.
7. Return the guarded net, combined operation counts, and source evidence.

## Expected complexity

`O(C_0025 + B + T * L + B_kept * M + |prefix| + |suffix|)` for upstream `ALG-0025` cost `C_0025`, body alternatives `B`, fixed maximum body length `M=2`, traces `T`, and max trace length `L`.

The no-filter path adds only `O(B)` policy comparisons and evidence construction after `ALG-0025`; the filter path adds one body-identification scan over the log and one guarded loop-net compilation.

## Smoke tests

Command: `python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json`

| Case | Guard applied | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `rare_body_noise_3_to_1` | yes | 4/5 | 1/1 | 2/2 | 519 | Filters singleton rare body `C`; improves precision over `ALG-0025`, but intentionally loses training replay. |
| `rare_body_valid_3_to_1_documented_failure` | yes | 4/5 | 0/2 | 0/0 | 519 | Documents the key failure: valid rare behavior is filtered under the pure support prior. |
| `balanced_two_body_choice` | no | 5/5 | 2/2 | 2/2 | 338 | Balanced alternatives remain valid. |
| `low_sample_2_to_1_ambiguous` | no | 4/4 | 1/1 | 2/2 | 301 | 2:1 support is not strong enough to filter. |
| `length2_rare_body_noise` | yes | 4/5 | 1/1 | 2/2 | 732 | Filters singleton-supported length-2 body and keeps dominant length-2 body repeatable. |
| `mixed_width_rare_singleton_noise` | yes | 4/5 | 1/1 | 2/2 | 584 | Filters rare length-2 body while retaining dominant singleton loop body. |
| `two_rare_bodies_no_dominant` | no | 5/5 | 1/1 | 2/2 | 395 | Weak dominance with two rare bodies stays unresolved. |

Additional regression command: `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`

- `ALG-0028` matches `ALG-0025` on balanced length-bounded loop cases when the support guard does not apply, with a small policy-count overhead.
- Trace-order stability checks for `ALG-0025` remain stable after wiring `ALG-0028` into the shared loop-test candidate list.

Toy-log benchmark command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

- On the six toy logs, `ALG-0028` behaves like `ALG-0025` plus one counted comparison when no multi-body support guard is relevant.

## Baselines for comparison

- `ALG-0025` length-bounded rework-loop miner.
- `ALG-0024` singleton-body multi-body loop miner.
- `ALG-0027` loop-count validation selector, as a separate selector for count policy rather than body inclusion.
- `ALG-0015` prefix-block support guard, as the earlier support/noise tradeoff precedent.

## Metrics

- Guard applied or not.
- Filtered and kept bodies.
- Training replay loss from filtered observed traces.
- Held-out replay for dominant-body repetitions and valid rare-body controls.
- Negative rejection of rare-body-as-noise probes.
- Operation counts and budget ratio.
- Source selected cut and guarded selected cut.

## Known failure modes

- Valid rare behavior is dropped under 3:1 or stronger support imbalance.
- The policy is sensitive on small logs; 3:1 evidence may mean noise or incomplete sampling.
- Filtering to one body changes selected semantics from multi-body choice to a single kept body.
- It inherits `ALG-0025` limits: body length greater than two, overlapping body labels, duplicate prefix/body/suffix labels, and one-iteration-only evidence remain outside scope.
- It does not solve bounded-count ambiguity; combine with `ALG-0026`/`ALG-0027` only after body inclusion is fixed.

## Promotion criteria

Do not promote beyond `smoke-tested` until:

- ablation evidence shows the support guard is causal for rare-body precision gains;
- valid rare-body controls across several support ratios are documented;
- parameter sweeps cover 3:1, 4:1, two-rare-body, and low-sample cases;
- the candidate reports when it is applying a precision prior rather than an identifiable discovery claim;
- interaction with `ALG-0026`/`ALG-0027` loop-count policy sets is tested.

## Experiment links

- EXP-0031: first targeted support-guard smoke test and toy benchmark rerun.
- EXP-0032: support-threshold ablation across 2:1, 3:1, 4:1, and 5:1 policies, plus body-inclusion validation probes.

## Property-study notes

No property dossier. The candidate is not `super-promising`. Future property work should define correctness relative to an explicit noise prior, not relative to the raw training log language.

## Decision history

- EXP-0031: added and kept at `smoke-tested`. It improves precision in rare-body-as-noise probes but fails valid rare-body controls under the same support pattern, so it is a useful policy candidate and counterexample, not a promoted miner.
- EXP-0032: kept at `smoke-tested`. A 2:1 policy rejects 15/17 rare-noise negatives but replays 0/10 valid-rare positives; the default 3:1 policy rejects 10/17 and replays 3/10; 4:1 rejects 8/17 and replays 5/10; 5:1 rejects 4/17 and replays 8/10. This confirms the threshold is a policy tradeoff, not a discovery result.
