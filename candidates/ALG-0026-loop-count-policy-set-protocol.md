# ALG-0026 - Loop Count Policy-Set Protocol

## Status

smoke-tested

## One-sentence hypothesis

When cut-limited loop evidence is marked `bounded_count_ambiguous=true`, preserving both unbounded-repeat and at-most-once Petri-net alternatives is a better intermediate result than selecting either policy from the event log alone.

## Input assumptions

- Batch event log with activity-label traces.
- Upstream loop evidence comes from the `ALG-0025` line, including `ALG-0023` singleton loops, `ALG-0024` singleton-body loop choices, and `ALG-0025` length-bounded body choices.
- The upstream process-tree evidence includes:
  - `prefix`
  - `anchor`
  - `body` or `bodies`
  - `suffix`
  - `bounded_count_ambiguous=true`
- The protocol does not infer a final selected policy without validation data or a domain prior.

## Output

- PMIR evidence: `loop_count_policy_set` with `detected`, `selected_policy`, and alternatives.
- Alternative 1: current unbounded-repeat Petri net from the upstream loop candidate.
- Alternative 2: at-most-once Petri net compiled from the same prefix, anchor, body alternatives, and suffix.
- Benchmark-compatible selected net: the upstream unbounded-repeat net, only for single-net runner compatibility.

## Intermediate representation

Loop policy-set PMIR annotation:

- `type=loop_count_policy`
- `reason=zero_one_loop_evidence_does_not_identify_unbounded_vs_at_most_once`
- `selected_policy=unbounded_repeat`
- per-alternative policy name, source candidate, Petri net, compile operation counts, and total-with-discovery counts

## Allowed operations / operation-cost model

Uses the first-goal primitive operations:

- construction operations for at-most-once places, transitions, arcs, markings, and a zero-exit silent transition;
- no new raw-log scans beyond the upstream `ALG-0025` discovery path;
- replay/evaluation operations remain outside discovery cost, as in previous protocol tests.

Expected cost is upstream `ALG-0025` discovery and selected compilation plus `O(B * M + |prefix| + |suffix|)` construction for the at-most-once alternative, where `B` is the number of body alternatives and `M <= 2` in the current wrapper.

## Algorithm sketch

1. Run `ALG-0025` discovery.
2. If the selected process-tree evidence is not `bounded_count_ambiguous`, emit no alternatives.
3. If the evidence is a singleton or multi-body loop, keep the selected unbounded-repeat net as one alternative.
4. Compile an at-most-once net:
   - entry anchor fires into an after-entry place;
   - zero-iteration path uses `tau_loop_policy_zero_exit` into a shared suffix-entry place;
   - one-iteration path fires one body sequence, then a duplicate visible repeat-anchor transition into the same suffix-entry place;
   - suffix is wired once from the suffix-entry place to final marking.
5. Store both alternatives with operation counts.

## Expected complexity

`O(C_0025 + B * M + |prefix| + |suffix|)` counted construction operations after upstream discovery, with fixed `M=2` in current tests. The protocol is batch and deterministic.

## Smoke tests

Primary gates:

- `single_rework_unbounded_policy`
- `single_rework_bounded_policy`
- `multi_body_unbounded_policy`
- `contexted_multi_body_policy`
- `multi_body_bounded_policy`
- `length2_unbounded_policy`
- `length2_bounded_policy`
- `mixed_width_policy`

Controls:

- `one_iteration_only_no_policy_set`
- `optional_skip_no_policy_set`

## Baselines for comparison

- `ALG-0023` unbounded singleton-loop candidate.
- `ALG-0024` unbounded singleton-body loop-choice candidate.
- `ALG-0025` unbounded length-bounded body-loop candidate.
- `ALG-0022` prefix-block ambiguity-set protocol as a design analogue.

## Metrics

- Policy alternatives emitted.
- Training replay per policy.
- Held-out replay per policy.
- Negative-trace rejection per policy.
- Compile operation counts and total-with-discovery operation counts.
- Structural diagnostics per policy.

## Known failure modes

- No final policy selection without validation data, domain priors, or a declared objective.
- If upstream loop detection falls back, the protocol emits no alternatives.
- One-iteration-only evidence remains unresolved because upstream candidates intentionally reject it.
- At-most-once is a policy alternative, not an evidence-discovered truth.
- The at-most-once compiler inherits upstream duplicate-label and body-length restrictions.

## EXP-0027 Results

Command: `python3 scripts/alg0026_loop_policy_tests.py --out experiments/alg0026-loop-policy-tests.json`

| Case | Alternatives emitted | Unbounded held-out / neg | At-most-once held-out / neg | Interpretation |
|---|---:|---:|---:|---|
| `single_rework_unbounded_policy` | yes | 1/1 / 3/3 | 0/1 / 3/3 | Unbounded wins on second-iteration held-out. |
| `single_rework_bounded_policy` | yes | 0/0 / 2/3 | 0/0 / 3/3 | At-most-once wins on bounded-count negatives. |
| `multi_body_unbounded_policy` | yes | 2/2 / 3/3 | 0/2 / 3/3 | Unbounded wins on repeated body combinations. |
| `contexted_multi_body_policy` | yes | 2/2 / 4/4 | 0/2 / 4/4 | Prefix/suffix context preserves the policy split. |
| `multi_body_bounded_policy` | yes | 0/0 / 2/4 | 0/0 / 4/4 | At-most-once rejects repeated body-combination negatives. |
| `length2_unbounded_policy` | yes | 2/2 / 3/3 | 0/2 / 3/3 | Length-2 body alternatives preserve the split. |
| `length2_bounded_policy` | yes | 0/0 / 2/4 | 0/0 / 4/4 | At-most-once fixes length-2 bounded-count precision. |
| `mixed_width_policy` | yes | 2/2 / 4/4 | 0/2 / 4/4 | Mixed singleton and length-2 bodies preserve the split. |
| `one_iteration_only_no_policy_set` | no | 0/1 / 3/3 selected fallback | n/a | No zero-iteration evidence, so no policy set. |
| `optional_skip_no_policy_set` | no | 1/1 / 3/3 selected optional cut | n/a | Optional skip is not a loop-count ambiguity. |

At-most-once total-with-discovery operation counts:

- singleton: 216
- multi-body singleton: 283
- contexted multi-body: 378
- length-2 body: 434
- mixed-width body: 351

## Promotion criteria

`ALG-0026` is `smoke-tested` because it:

- runs deterministically on targeted bounded-count loop-policy cases;
- emits both alternatives only when upstream loop evidence is bounded-count ambiguous;
- records per-policy replay, negative rejection, structural diagnostics, and operation counts;
- brackets the recurring bounded-count ambiguity without claiming identifiability.

It is not promoted to `promising` yet because it has no selector, validation protocol, or external prior that chooses a final policy.

## Experiment links

- EXP-0027: targeted bounded-loop policy-set tests.

## Property-study notes

No property dossier. Future property work should compare the languages of the alternatives:

- unbounded: `prefix anchor (body_i anchor)* suffix`;
- at-most-once: `prefix anchor (epsilon | body_i anchor) suffix`.

It should also study soundness, 1-safeness, duplicate-anchor transition correctness, and whether the silent zero-exit construction preserves accepting semantics.

## Decision history

- EXP-0027: added as a policy-set protocol after repeated EXP-0023 through EXP-0026 evidence showed bounded-count semantics are not identifiable from zero/one loop evidence alone; kept at `smoke-tested`, not promoted.
