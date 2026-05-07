# ALG-0013 — Region Optional-Chain No-Certification Ablation

## Status

smoke-tested

## One-sentence hypothesis

Order-consistent optional chains may be sufficient without selected-region-shortcut certification, reducing operation count without changing discovered behavior.

## Input assumptions

- Same base assumptions as `ALG-0012`.
- Optional-chain candidates are still extracted from transitive reduction over causal edges and filtered by order-consistency.
- Unlike `ALG-0012`, a chain does not need a selected singleton shortcut place from the bounded region miner.

## Output

- PMIR evidence with `require_region_shortcut=false` and `region_certification=disabled_ablation`.
- Petri-net JSON with selected visible region places plus any uncertified optional-chain fragments.

## Intermediate representation

Visible place-candidate table plus order-consistent optional chains without selected-region certification.

## Allowed operations / operation-cost model

Same as `ALG-0012` minus selected-shortcut certification checks. The bounded region enumeration and chain-detection stages still dominate measured cost.

## Algorithm sketch

1. Run the `ALG-0012` bounded visible-region and optional-chain pipeline.
2. Select order-consistent optional chains.
3. Skip the selected-shortcut intersection filter.
4. Compile the selected visible region places and all selected optional-chain fragments.

## Expected complexity

`O(N + P + A^(2k) * P * k + N * L + A^2 + D^2 + path_checks)`, with a smaller constant than `ALG-0012` because selected-shortcut filtering is disabled.

## Smoke tests

First gate: the optional-pattern suite in `scripts/alg0011_optional_tests.py`, especially overlapping optional chains and optional/concurrency cases.

Broader gate: synthetic cases in `scripts/alg0009_deep_tests.py`.

## Likely failure modes

- May accept optional-chain fragments that selected region places would reject.
- Does not solve optional behavior inside concurrency in the current tests.
- Inherits `ALG-0004` loop and duplicate-label limitations.
- Saves only tiny operation counts unless selected-shortcut filtering grows on larger logs.

## EXP-0015 optional-pattern comparison

Command: `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`

| Case | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `singleton_optional_skip` | 427 | 4/4 | 3/3 | 1 |
| `two_disjoint_optional_skips` | 1636 | 4/4 | 3/3 | 1 |
| `overlapping_optional_chain` | 1026 | 4/4 | 3/3 | 1 |
| `optional_inside_parallel` | 1815 | 3/3 | 1/3 | 0 |
| `optional_singleton_parallel_branch` | 1008 | 4/4 | 2/3 | 0 |

## EXP-0015 broader synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Ops | Replay | Negative rejection |
|---|---:|---:|---:|
| `nested_xor_sequence` | 1515 | 3/3 | 3/3 |
| `overlapping_optional_skips` | 1026 | 4/4 | 3/3 |
| `parallel_with_optional_branch` | 1815 | 3/3 | 1/3 |
| `short_loop_required` | 357 | 1/3 | 3/3 |
| `duplicate_label_rework` | 357 | 1/3 | 3/3 |
| `incomplete_parallel_observed_sequence` | 754 | 2/2 | 3/3 |
| `noise_reversal_sequence` | 1461 | 4/4 | 3/3 |

## Promotion criteria

Not promoted in EXP-0015. It matched `ALG-0012` on observed quality but the cost savings were too small to justify replacing the certified variant, and no counterexample search has shown certification is unnecessary in general.

## Experiment links

- EXP-0015: selected-shortcut-certification ablation and extra optional-concurrency counterexample.

## Property-study notes

No property dossier. This variant weakens the empirical safety argument for `ALG-0012` and needs counterexample search before any formal study.

## Decision history

- EXP-0015: added as an executable ablation via `region_optional_chain_miner.discover(..., require_region_shortcut=False)`; retained for comparison but not promoted.
