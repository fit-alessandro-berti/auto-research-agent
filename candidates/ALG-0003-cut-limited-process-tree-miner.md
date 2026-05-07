# ALG-0003 — Cut-Limited Process Tree Miner

## Status

deep-testing

## One-sentence hypothesis

A bounded menu of DFG cut tests can discover simple block-structured process trees and compile them to sound Petri nets with predictable operation cost.

## Input assumptions

- Log is a list of traces over activity labels.
- Target behavior is approximately block-structured.
- Duplicated labels and non-local dependencies are out of first-iteration scope.
- Noise must be filtered or treated as a failed cut, not silently accepted.

## Output

- Process tree with sequence, XOR, parallel, optional-sequence, bounded optional-concurrency, and later loop nodes.
- Petri-net JSON compiled from the process tree.

## Intermediate representation

Process tree, optionally backed by PMIR DFG summaries and cut evidence.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments, set inserts/lookups, comparisons, relation classifications for cut decisions, arithmetic only for optional support scores, and construction operations for tree/net nodes.

## Algorithm sketch

1. Build DFG, start/end counts, and activity set.
2. Try deterministic cut tests in a fixed order: sequence, common-prefix/suffix XOR, common-prefix/suffix parallel, bounded optional-concurrency, optional sequence.
3. Compile the accepted top-level block directly to a Petri-net fragment.
4. Fall back to a directly-follows fragment when no cut is found.
5. Record the selected cut and all rejected cuts in PMIR evidence.

## Expected complexity

Current non-recursive prototype is `O(N + A^2 + T * L^2)` for DFG/relation summaries plus bounded cut checks, where `L` is maximum trace length. A future recursive version is expected around `O(N + A^3)` if decomposition checks remain bounded.

## Smoke tests

First gates: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, and `skip.json`. `short_loop.json` is a gate only after a loop-cut rule is specified; `noise.json` is a robustness gate.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- Future external inductive miner if dependencies are accepted.

## Metrics

Metrics: replay, negative-trace rejection, structural diagnostics, operation counts per cut attempt, tree size, and fallback frequency.

## Known failure modes

- Non-block-structured logs.
- Noise-induced false cuts.
- Missing behavior causing wrong XOR/parallel decisions.
- Duplicate labels.
- Loop cuts that overgeneralize.
- Optional behavior embedded inside concurrency beyond the current one mandatory singleton plus one length-2 optional branch.

## Executable prototype

Implemented in `scripts/cut_limited_process_tree.py` and wired into:

- `scripts/benchmark.py`
- `scripts/alg0009_deep_tests.py`

Current prototype is intentionally non-recursive. It accepts only one top-level block pattern plus common sequence context, which keeps the first implementation inspectable but limits broader composition.

## EXP-0007 smoke results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Selected cut | Ops | Replay | Negative rejection | Structural diagnostics |
|---|---:|---:|---:|---:|---|
| `noise.json` | parallel | 261 | 4/4 | 3/3 | clean |
| `parallel_ab_cd.json` | parallel | 243 | 4/4 | 3/3 | clean |
| `sequence.json` | sequence | 168 | 3/3 | 3/3 | clean |
| `short_loop.json` | fallback_dfg | 164 | 0/3 | 3/3 | clean but no loop support |
| `skip.json` | optional_sequence | 209 | 4/4 | 3/3 | clean |
| `xor.json` | xor | 194 | 4/4 | 3/3 | clean |

## EXP-0007 synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Selected cut | Ops | Replay | Negative rejection | Interpretation |
|---|---:|---:|---:|---:|---|
| `nested_xor_sequence` | xor | 255 | 3/3 | 3/3 | Common-prefix/suffix XOR works. |
| `overlapping_optional_skips` | optional_sequence | 290 | 4/4 | 3/3 | Matches ALG-0010's repaired behavior. |
| `incomplete_parallel_observed_sequence` | sequence | 155 | 2/2 | 3/3 | Conservative under incomplete concurrency evidence. |
| `noise_reversal_sequence` | parallel | 261 | 4/4 | 3/3 | Treats reversal as parallel evidence. |
| `parallel_with_optional_branch` | fallback_dfg | 314 | 0/3 | 3/3 | Missing optional-concurrency composition. |
| `short_loop_required` | fallback_dfg | 164 | 0/3 | 3/3 | No loop cut. |
| `duplicate_label_rework` | fallback_dfg | 154 | 0/3 | 3/3 | Duplicate labels unsupported. |

## EXP-0008 bounded optional-concurrency refinement

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

The EXP-0008 refinement added `parallel_optional_sequence`, a bounded cut for one mandatory singleton branch in parallel with one two-step branch whose second activity is optional. It also added an ablation `cut_tree_no_parallel_optional`.

| Synthetic case | Default cut | Default replay | Ablation cut | Ablation replay | Interpretation |
|---|---:|---:|---:|---:|---|
| `parallel_with_optional_branch` | parallel_optional_sequence | 3/3 | fallback_dfg | 0/3 | New cut fixes the targeted optional-concurrency counterexample. |
| `overlapping_optional_skips` | optional_sequence | 4/4 | optional_sequence | 4/4 | Behavior preserved; operation cost increases from the extra rejected detector. |
| `nested_xor_sequence` | xor | 3/3 | xor | 3/3 | Behavior preserved. |
| `short_loop_required` | fallback_dfg | 0/3 | fallback_dfg | 0/3 | Loop failure unchanged. |
| `duplicate_label_rework` | fallback_dfg | 0/3 | fallback_dfg | 0/3 | Duplicate-label failure unchanged. |

EXP-0008 smoke results preserved the EXP-0007 replay outcomes. `skip.json` operation count increased from 209 to 235 and `short_loop.json` from 164 to 191 because these logs now reject the optional-concurrency detector before selecting optional-sequence or fallback.

## EXP-0022 loop-repair split

`ALG-0023` adds an opt-in `single_rework_loop` detector to this implementation while keeping the default `ALG-0003` behavior unchanged. The split candidate fixes `short_loop_required` and `duplicate_label_rework` at 3/3 replay and 3/3 negative rejection, and replays a held-out second loop iteration in the targeted loop suite. `ALG-0003` remains the non-loop baseline and keeps its `deep-testing` status.

## Promotion criteria

Promoted to `promising` after EXP-0007 because the deterministic prototype:

- compiles valid Petri nets from process trees;
- replays sequence, XOR, parallel, skip, and noise smoke logs;
- records cut-operation counts;
- has a clear fallback behavior;
- has a soundness-by-construction claim scoped to accepted block nodes.

Promotion beyond `promising` requires either a bounded loop cut and optional-concurrency composition or an explicit narrower claimed scope plus deep-test evidence against scoped counterexamples.

Moved to `deep-testing` after EXP-0008 because a refined optional-concurrency cut was implemented, the ablation shows the targeted fix is causal, and counterexample testing is active. Promotion beyond `deep-testing` requires loop/duplicate-label decisions, broader composition tests, and formalized block-compilation obligations.

## Experiment links

- EXP-0003: specified as the inductive/process-tree baseline family.
- EXP-0007: implemented and promoted to `promising`; no `super-promising` promotion because fallback fails short-loop, duplicate-label, and optional-concurrency cases.
- EXP-0008: added bounded optional-concurrency cut and ablation; moved to `deep-testing`, not `super-promising`.
- EXP-0022: loop repair split into `ALG-0023`; default `ALG-0003` status unchanged.

## Property-study notes

This is still a strong family for future formal workflow-net soundness claims over accepted blocks. No property dossier is justified yet because the current prototype is not `super-promising` and lacks recursive composition.

## Decision history

- EXP-0003: specified as the inductive/process-tree baseline family.
- EXP-0007: implemented as a top-level cut recognizer and promoted to `promising`, not `deep-testing` or `super-promising`.
- EXP-0008: moved to `deep-testing` after fixing the bounded optional-concurrency counterexample with ablation evidence.
- EXP-0022: retained as the baseline process-tree candidate while `ALG-0023` carries the bounded loop extension.
