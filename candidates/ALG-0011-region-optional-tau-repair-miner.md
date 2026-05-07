# ALG-0011 — Region Optional-Tau Repair Miner

## Status

deep-testing

## One-sentence hypothesis

A bounded visible-place region miner can repair simple optional-skip overgeneralization by adding silent skip fragments only when a non-overlapping optional singleton is certified by a selected shortcut place.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Base visible region candidates use `ALG-0004` with `k <= 2`.
- Optional repair is limited to one skipped middle activity `A B C` / `A C`.
- The middle activity must have exactly one causal predecessor and one causal successor in the relation summary.
- A selected visible shortcut place `(A)->(C)` must exist before the silent optional fragment is emitted.

## Output

- PMIR evidence containing visible region candidates, selected shortcut places, optional-pattern statistics, and accepted optional triples.
- Petri-net JSON with the selected visible region places plus optional `tau_region_skip_*` transitions.

## Intermediate representation

Visible place-candidate table plus a guarded optional-singleton pattern list.

## Allowed operations / operation-cost model

Uses the `ALG-0004` counted operations plus causal-map construction, bounded optional triple checks, set lookups for selected shortcut places, and construction operations for two optional places plus one silent transition per accepted optional pattern.

## Algorithm sketch

1. Run the bounded visible-place enumeration and greedy selection from `ALG-0004`.
2. Build causal incoming/outgoing maps from the relation summary.
3. For each causal chain `A -> B -> C`, require:
   - `A`, `B`, and `C` are distinct;
   - `B` is not a start or end activity;
   - `B` has exactly one causal predecessor `A` and one causal successor `C`;
   - the base region miner selected shortcut place `(A)->(C)`;
   - `A -> C` is directly observed and classified causal.
4. Add the optional fragment `A -> split -> (B | tau) -> join -> C`.
5. Keep all operation counts explicit and report accepted/rejected optional candidates.

## Expected complexity

`O(N + P + A^(2k) * P * k + A + E)` with fixed `k`, where the final term is the bounded optional-pattern scan over causal edges.

## Smoke tests

First gate: `skip.json`, where `ALG-0004` overgeneralizes because the skipped activity is unconstrained.

Broader gates: all current smoke logs and synthetic counterexamples in `scripts/alg0009_deep_tests.py`.

## Likely failure modes

- Does not handle overlapping optional chains because the non-overlap guard rejects middle activities with multiple causal contexts.
- Does not handle optional behavior embedded in concurrency.
- Inherits `ALG-0004` high candidate-enumeration cost.
- Inherits `ALG-0004` loop and duplicate-label limitations.
- Silent-transition closure in the evaluator is a smoke replay check, not a soundness proof.

## EXP-0012 smoke results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Ops | Replay | Negative rejection | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `noise.json` | 1365 | 4/4 | 3/3 | 0 |
| `parallel_ab_cd.json` | 1341 | 4/4 | 3/3 | 0 |
| `sequence.json` | 842 | 3/3 | 3/3 | 0 |
| `short_loop.json` | 327 | 1/3 | 3/3 | 0 |
| `skip.json` | 368 | 4/4 | 3/3 | 1 |
| `xor.json` | 770 | 4/4 | 3/3 | 0 |

## EXP-0012 synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Ops | Replay | Negative rejection | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `duplicate_label_rework` | 327 | 1/3 | 3/3 | 0 |
| `incomplete_parallel_observed_sequence` | 716 | 2/2 | 3/3 | 0 |
| `nested_xor_sequence` | 1415 | 3/3 | 3/3 | 0 |
| `noise_reversal_sequence` | 1365 | 4/4 | 3/3 | 0 |
| `overlapping_optional_skips` | 858 | 4/4 | 0/3 | 0 |
| `parallel_with_optional_branch` | 1677 | 3/3 | 1/3 | 0 |
| `short_loop_required` | 327 | 1/3 | 3/3 | 0 |

## EXP-0013 optional-pattern ablation

Command: `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`

| Case | ALG-0004 replay / neg reject / ops | ALG-0011 no-repair replay / neg reject / ops | ALG-0011 replay / neg reject / ops | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `singleton_optional_skip` | 4/4 / 1/3 / 332 | 4/4 / 1/3 / 332 | 4/4 / 3/3 / 368 | 1 |
| `two_disjoint_optional_skips` | 4/4 / 2/3 / 1382 | 4/4 / 2/3 / 1382 | 4/4 / 3/3 / 1489 | 2 |
| `overlapping_optional_chain` | 4/4 / 0/3 / 802 | 4/4 / 0/3 / 802 | 4/4 / 0/3 / 858 | 0 |
| `optional_inside_parallel` | 3/3 / 1/3 / 1604 | 3/3 / 1/3 / 1604 | 3/3 / 1/3 / 1677 | 0 |

Comparison baselines:

- `ALG-0003` rejects 3/3 negatives on all four optional-pattern cases and replays all positives.
- `ALG-0010` rejects 3/3 negatives on singleton, disjoint, and overlapping optional cases, but replays 0/3 positives on `optional_inside_parallel`.

## Promotion criteria

Promoted to `promising` in EXP-0012 for its narrow claimed scope:

- deterministic executable prototype in `scripts/region_optional_tau_miner.py`;
- measured operation counts;
- fixes the `ALG-0004` simple-skip precision failure on `skip.json` from 1/3 to 3/3 negative rejection while preserving 4/4 positive replay;
- does not regress sequence, XOR, parallel, or noise smoke replay.

Moved to `deep-testing` in EXP-0013 because:

- the no-repair ablation matches `ALG-0004` on the optional cases, confirming the silent repair is causal for the singleton and disjoint-skip precision gains;
- counterexample search now covers overlapping optional chains and optional behavior inside concurrency;
- failures are documented and scoped.

It is not `super-promising` because high operation cost remains, overlapping optional chains still overgeneralize, optional/concurrency remains unrepaired, and no formal property study has started.

## Experiment links

- EXP-0011: `ALG-0004` visible-place-only comparator exposed optional-skip overgeneralization.
- EXP-0012: this candidate adds the non-overlap optional-tau repair and validates the targeted fix.
- EXP-0013: no-repair ablation plus broader optional-pattern tests move the candidate to `deep-testing`.
- EXP-0014: chain-aware repair split into `ALG-0012`; this candidate remains the narrower singleton/disjoint optional repair.

## Property-study notes

Potential future dossier topics if promoted further: replay preservation when adding certified optional singleton fragments, safeness of the local optional fragment, and counterexamples for overlapping optional contexts.

## Decision history

- EXP-0012: implemented and promoted to `promising` for narrow non-overlapping singleton optional skips only.
- EXP-0013: moved to `deep-testing`; retained as narrow optional repair, not a general optional/concurrency solution.
- EXP-0014: remains `deep-testing`; overlapping optional-chain repair is tracked separately as `ALG-0012`.
