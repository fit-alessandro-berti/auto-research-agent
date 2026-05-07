# ALG-0033 - Per-Body Direct-Signal Validation Selector

## Status

smoke-tested

## One-sentence hypothesis

External validation probes can select individual rare loop-body keep/drop decisions at lower cost than exhaustive per-body enumeration when the probes provide direct body-level signals or unit-propagated negative clauses.

## Input assumptions

- Batch training log with activity-label traces.
- `ALG-0025` emits a length-bounded multi-body rework-loop PMIR.
- A dominant loop body satisfies an explicit support threshold.
- Rare loop bodies are the non-dominant bodies with the configured `rare_body_count`.
- Validation positives and negatives are separate from final probes and are intended as direct rare-body inclusion probes.
- A positive validation trace that contains a rare body is evidence to keep that body.
- A negative validation trace constrains at least one rare body in the trace to be dropped; after required-keep bodies are removed, singleton clauses become direct drop signals.

Default selector policy in the prototype:

- `min_dominant_count = 5`;
- `min_dominant_share = 5/7`;
- `rare_body_count = 1`;
- `max_rare_bodies = 5`.

## Output

- PMIR:
  - source `ALG-0025` loop evidence;
  - direct-signal selector configuration;
  - dominance context;
  - per-body positive, negative, conflict, and unresolved signal rows;
  - ambiguous negative clauses;
  - selected dropped/kept body set, or an unresolved/budget/conflict status.
- Petri net:
  - selected keep-all `ALG-0025` net, or one guarded recompilation with selected dropped bodies removed;
  - if unresolved, the upstream net is retained only for compatibility and must not be treated as a selected policy.
- Other:
  - selector operation counts;
  - guarded compile extra counts;
  - validation replay proxy counts;
  - avoided exhaustive alternative count for comparison with `ALG-0032`.

## Intermediate representation

`ALG-0025` process-tree loop PMIR plus a direct body-signal constraint layer:

- dominant body and support;
- rare candidate bodies;
- positive keep signals from validation positives;
- negative drop clauses from validation negatives;
- unit-propagated drop signals after required-keep bodies are removed;
- conflict, partial-signal, and interaction-ambiguity annotations.

## Allowed operations / operation-cost model

Uses only the first-goal primitive operations:

- `scan_event` for validation trace parsing, trace/body partitioning, and validation replay proxy events;
- `set_lookup` for rare-body membership checks during trace parsing;
- `comparison` for threshold checks, parser checks, signal decisions, and validation conflicts;
- `arithmetic` for dominant-share checks, loop-parser index updates, and signal counters;
- `construct` for signal rows, ambiguous clauses, and the selected guarded net;
- inherited `dict_increment`, `set_insert`, `relation_classification`, and construction counts from upstream discovery/recompilation.

Expected prototype cost:

```text
ALG-0025 discovery
+ O(B) dominance and rare-body checks
+ O(V * L) direct validation parsing
+ O(C * R_clause) bounded clause/unit-signal checks
+ at most one O(T * L + compile_guarded_net) guarded recompilation
+ one validation replay proxy for the selected net
```

where `B` is the number of loop-body alternatives, `V` is validation trace count, `L` is maximum trace length, `C` is the number of negative clauses, and `R_clause` is the number of rare bodies in a validation negative. The prototype does not build or replay all `2^R` assignments.

## Algorithm sketch

1. Run `ALG-0025`.
2. Require the selected cut to be `multi_body_rework_loop`.
3. Extract body support and check the declared dominant-body threshold.
4. Identify non-dominant rare candidate bodies with count equal to `rare_body_count`.
5. If the rare-body count exceeds `max_rare_bodies`, return `too_many_rare_bodies`.
6. Parse validation traces using the source loop prefix, anchor, and suffix.
7. Mark rare bodies seen in validation positives as required keep.
8. Convert validation negatives into rare-body drop clauses.
9. For each negative clause, remove required-keep bodies; singleton remaining clauses become drop signals, empty clauses become conflicts, and multi-body clauses remain ambiguous.
10. Select only when every rare body has exactly one non-conflicting keep or drop signal.
11. Compile at most one guarded net from the selected drop set.
12. Replay validation positives and negatives once as a safety check; if the selected net fails, return `selected_net_fails_validation`.

## Expected complexity

For fixed maximum body length `M=2`, direct selection is linear in validation events plus one selected guarded recompilation. It is lower-cost but less complete than `ALG-0032`: it refuses ambiguous interaction clauses instead of searching all assignments.

## Smoke tests

Command:

```bash
python3 scripts/alg0033_direct_signal_tests.py --out experiments/alg0033-direct-signal-tests.json
```

EXP-0040 result: 16/16 cases passed.

Key controls:

- one rare valid: keep it;
- one rare noise: drop it;
- two rare bodies, one valid and one noise: keep `C`, drop `E`;
- two rare bodies both valid: keep both;
- two rare bodies both noise: drop both;
- count-two rare bodies under explicit `5/9` policy: split valid `C` from noisy `E`;
- unit-propagated negative clause: positive `C` plus negative `C,E` drops `E`;
- three and five rare body direct-signal scale cases stay under `B_deep`;
- partial validation signal: unresolved;
- conflicting body signal: conflict;
- non-unit ambiguous negative with no required keep body: unresolved;
- cap overflow, weak dominance, validation overlap, and training-negative conflict are detected.

Selected operation observations from EXP-0040:

| Case | Status | Dropped bodies | Direct total with validation proxy | Deep budget | Exhaustive shared total |
|---|---|---|---:|---:|---:|
| `two_rare_one_valid_one_noise` | `selected` | `E` | 896 | 970 | 1434 |
| `two_rare_both_noise` | `selected` | `C,E` | 877 | 970 | 1463 |
| `count_two_mixed_valid_noise` | `selected` | `E` | 1009 | 1098 | 1610 |
| `unit_propagation_negative_clause` | `selected` | `E` | 897 | 970 | 1434 |
| `rare_count_3_direct_scale_under_budget` | `selected` | `E,F` | 1066 | 1186 | not run |
| `rare_count_5_direct_scale_under_budget_reference` | `selected` | `E,F,G,H` | 1442 | 1690 | not run |

## Baselines for comparison

- `ALG-0025` keep-all length-bounded loop miner.
- `ALG-0028` support-prior group filter.
- `ALG-0029` keep-all versus group-filter validation selector.
- `ALG-0032` exhaustive per-body rare inclusion selector.

## Metrics

- Validation selection status and reason.
- Selected dropped and kept bodies.
- Direct signal rows and ambiguous clauses.
- Final positive replay and final negative rejection for selected cases.
- Evaluated alternative count and avoided exhaustive alternative count.
- Selector primitive counts, guarded compile extra, validation replay proxy, and total with selector/proxy.
- Budget ratio against `B_deep`.
- Cost comparison against `ALG-0032` shared totals on matched cases.

## Known failure modes

- Not a training-log-only discovery rule; validation evidence is required for selection.
- Lower-cost but less complete than `ALG-0032`: non-unit negative clauses with multiple plausible drop bodies remain unresolved.
- Direct attribution can be unsound if a validation negative fails for order, loop-count, suffix/prefix, or upstream-scope reasons rather than rare-body inclusion.
- Validation representativeness is an assumption, not proven.
- Every rare body must receive a non-conflicting direct keep/drop signal; otherwise the selector returns `partial_direct_signal`.
- Inherits `ALG-0025` limits: body length greater than two, duplicate/overlapping labels, one-iteration-only evidence, and upstream cut failures.
- The current prototype has smoke coverage only on deterministic synthetic probes, not non-toy logs.

## Promotion criteria

Do not promote beyond `smoke-tested` unless:

- split train/validation/final controls are broadened beyond the current direct-signal smoke suite;
- direct-signal stress is run across length-2, mixed-width, count-two, and blocked upstream scopes;
- ambiguity controls show the selector refuses non-unit clauses reliably;
- operation counts remain below `B_deep` on larger direct-signal rare-body families;
- comparisons against `ALG-0032` show repeated cost savings while documenting lost completeness;
- validation-negative attribution assumptions are either formalized or checked by a stronger validation-trace classifier.

## Experiment links

- EXP-0040: initial direct-signal selector, unit-propagation tests, direct-signal scale cases, and `ALG-0032` cost comparisons.

## Property-study notes

No property dossier. The candidate is not `super-promising`.

Potential future property question: conditional correctness can be stated as sound selection relative to a validation objective only when each validation negative is a clean rare-body inclusion clause over the source loop PMIR.

## Decision history

- EXP-0040: added as `smoke-tested`. It preserves core mixed rare-body wins at lower cost than `ALG-0032` on matched two-rare/count-two cases and stays under `B_deep` through five rare bodies on the deterministic direct-signal scale family. It is not promoted because evidence is synthetic, validation-scoped, and deliberately incomplete for non-unit ambiguous negative clauses.
