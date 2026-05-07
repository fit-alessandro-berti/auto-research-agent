# ALG-0009 — PMIR Guarded Split-Join Compiler

## Status

deep-testing

## One-sentence hypothesis

A guarded PMIR split/join compiler can keep the low-operation local strategy from `ALG-0006` while avoiding over-constrained XOR and optional-skip behavior by marking grouped edges as covered before individual edge places are emitted.

## Input assumptions

- Log is a list of traces.
- Each trace is an ordered list of activity labels.
- Activity labels are unique at the model level.
- Direct-follows evidence is sufficient for first-pass relation classification.
- Optional-skip patterns have the simple form `A -> B`, `B -> C`, and `A -> C`.
- Short loops and duplicate labels are out of scope for this variant.

## Output

- PMIR relation graph with covered-edge evidence, XOR split/join groups, optional-skip guards, and residual edge places.
- Petri-net JSON with visible transitions and silent `tau_` transitions only for optional skips.

## Intermediate representation

PMIR guarded-place evidence:

- `split_groups`: mutually unrelated successors covered by one split place.
- `join_groups`: mutually unrelated predecessors covered by one join place.
- `optional_patterns`: simple skip triples `(A, B, C)` compiled with a guarded silent skip transition.
- `covered_edges`: causal edges consumed by grouped or optional guards.
- `edge_places`: residual causal edges emitted as ordinary places.

## Allowed Operations / Operation-Cost Model

Uses `scan_event`, `dict_increment`, `set_insert`, `set_lookup`, `comparison`, `relation_classification`, and `construct`. It does not enumerate arbitrary preset/postset subsets and does not use solver operations.

The evaluator explores silent-transition closure, but those replay operations are evaluation cost, not discovery cost.

## Algorithm Sketch

1. Scan the log to collect activities, start/end counts, and direct-follows counts.
2. Classify pairwise relations with the Alpha-Lite relation classifier.
3. Build incoming and outgoing causal maps.
4. Detect simple optional-skip triples `(A, B, C)` and mark `A->B`, `B->C`, and `A->C` as covered.
5. Detect XOR split and join groups among remaining mutually unrelated branches and mark those edges as covered.
6. Compile optional guards, XOR guard places, and residual edge places into a Petri net.
7. Store all guard and covered-edge evidence in PMIR.

## Expected Complexity

`O(N + A^2 + sum_v out(v)^2 + sum_v in(v)^2 + optional_checks)`, where optional checks are bounded by local outgoing degree pairs. This keeps the same broad complexity class as `ALG-0006` and avoids Alpha-style subset enumeration.

## Smoke Tests

Executed in EXP-0004 on all toy logs with positive replay, negative-trace probes, and structural diagnostics.

- Full replay and full negative rejection: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `skip.json`, `noise.json`.
- Failed scope: `short_loop.json` replay 1/3 and negative rejection 1/3.

EXP-0005 started deep testing with ablations and synthetic counterexamples:

- Stable under checked trace-order permutations on all synthetic cases.
- Full replay/full negative rejection on `nested_xor_sequence`, `incomplete_parallel_observed_sequence`, and `noise_reversal_sequence`.
- Failed replay on `overlapping_optional_skips` 1/4, `parallel_with_optional_branch` 1/3, `short_loop_required` 1/3, and `duplicate_label_rework` 1/3.

## Baselines for Comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- `ALG-0006` PMIR Split-Join Compiler Lite.
- Future: `ALG-0003` Cut-Limited Process Tree Miner.

## Metrics

EXP-0004 measured operation counts, structural counts, strict token-game replay with silent closure, negative-trace rejection, and visible-transition structural diagnostics.

## Known Failure Modes

- Short loops still fail because bidirectional direct-follows evidence is classified as parallel rather than loop behavior.
- Duplicate labels are not handled.
- Nested optional/choice/concurrency structures are untested.
- Noise can still be interpreted as concurrency when reversed direct-follows evidence appears.
- Silent-closure replay is bounded and not a full soundness check.
- Overlapping optional guards can create mutually incompatible input requirements.
- Optional branches mixed with concurrent evidence can falsely force branch order.

## Promotion Criteria

Promoted to `promising` in EXP-0004 because it:

- has a written deterministic specification and prototype;
- records measured operation counts;
- passes positive and negative smoke probes for five of six smoke logs;
- fixes the `ALG-0006` XOR failure and the shared optional-skip replay failure;
- keeps lower counted operations than `ALG-0001` on all smoke logs;
- exposes a compact covered-edge PMIR compiler path worth deeper testing.

Further promotion requires ablations, synthetic benchmarks, trace-order stability checks, and formal study of guarded PMIR-to-net conversion.

Promoted to `deep-testing` in EXP-0005 because ablations and counterexample search have started. It is not `super-promising`: the synthetic failures above are material.

## Experiment Links

- EXP-0004 in `research/EXPERIMENT_LOG.md`.
- EXP-0005 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.
- `experiments/alg0009-deep-tests.json`.

## Property-Study Notes

Potential future properties:

- sufficient conditions for XOR guard correctness;
- sufficient conditions for simple optional-skip correctness;
- operation bound relative to Alpha-style subset enumeration;
- counterexamples for nested or overlapping guards.

No property dossier yet; the candidate is not `super-promising`.

## Decision History

- EXP-0004: implemented as repaired variant of `ALG-0006`; promoted to `promising` under the smoke-test protocol, with short-loop failure documented.
- EXP-0005: moved to `deep-testing`; retained as promising but narrowed after failures on overlapping skips, optional concurrency, short loops, and duplicate labels.
