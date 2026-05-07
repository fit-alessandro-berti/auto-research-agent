# ALG-0022 — Prefix Block Ambiguity-Set Protocol

## Status

smoke-tested

## One-sentence hypothesis

When `ALG-0021` detects prefix-merge ambiguity, a PMIR protocol that compiles each annotated alternative into its own Petri net can preserve both plausible models for downstream selection instead of forcing one unsupported choice.

## Input assumptions

- Input is `ALG-0021` ambiguity-aware PMIR evidence.
- Alternatives are limited to grammar fragments already accepted by the prefix-block detector.
- Current scope covers common-boundary versus prefix-merge parallel-block alternatives only.

## Output

- The selected `ALG-0021` Petri net.
- Zero or more alternative Petri nets compiled from `ambiguity.alternatives`.
- Replay, held-out replay, negative-probe, and operation-count summaries for each alternative.

## Intermediate representation

Ambiguity-set PMIR:

- selected grammar and selected Petri net;
- ambiguity flag and reason;
- list of `{policy, grammar}` alternatives;
- compiled Petri net and metrics per alternative.

## Allowed operations / operation-cost model

Uses the first-goal primitive operations. Discovery cost is inherited from `ALG-0021`; each additional alternative adds bounded block-net construction cost.

Expected cost is `ALG-0021 + O(m * (A + B))`, where `m` is the number of alternatives and `B` is the emitted block size. The EXP-0021 prototype reports both compile-only counts and total counts including the `ALG-0021` discovery run.

## Algorithm sketch

1. Run `ALG-0021`.
2. If no ambiguity is detected, return the selected net and an empty alternative set.
3. For each ambiguity alternative, compile its grammar to a Petri net using the existing prefix-block compiler.
4. Evaluate each alternative under the same training, held-out, and negative probes.
5. Leave final selection unresolved unless an external policy or validation set is supplied.

## Smoke tests

Primary gate: `scripts/alg0021_ambiguity_protocol_tests.py`.

Cases:

- `prefix_merge_full_parallel_interpretation`
- `prefix_merge_sequence_then_parallel_interpretation`
- noisy reversal and incomplete-parallel controls from `scripts/alg0015_noise_incomplete_tests.py`

## Baselines for comparison

- `ALG-0015` selected-net full-parallel policy.
- `ALG-0020` conservative common-boundary policy.
- `ALG-0021` ambiguity annotation without compiling alternatives.

## Metrics

- Whether ambiguity is detected.
- Number of alternatives.
- Per-alternative training replay.
- Per-alternative held-out replay.
- Per-alternative negative-trace rejection.
- Per-alternative compile operation counts.
- Total operation count when alternatives are compiled after discovery.

## Known failure modes

- It does not resolve ambiguity without an external selector.
- It can increase cost by compiling alternatives that are later discarded.
- Current implementation imports the prefix-block compiler directly and is therefore a research protocol, not a stable public API.
- It only handles alternatives expressible by the current shallow prefix-block grammar.

## EXP-0021 Results

Command: `python3 scripts/alg0021_ambiguity_protocol_tests.py --out experiments/alg0021-ambiguity-protocol-tests.json`

| Case | Alternative | Held-out replay | Negative rejection | Total ops including discovery |
|---|---|---:|---:|---:|
| `prefix_merge_full_parallel_interpretation` | `sequence_prefix_precision` | 0/4 | 3/3 | 385 |
| `prefix_merge_full_parallel_interpretation` | `full_parallel_generalization` | 4/4 | 3/3 | 388 |
| `prefix_merge_sequence_then_parallel_interpretation` | `sequence_prefix_precision` | 0/0 | 4/4 | 385 |
| `prefix_merge_sequence_then_parallel_interpretation` | `full_parallel_generalization` | 0/0 | 0/4 | 388 |

Controls:

- No alternatives are emitted for rare-reversal noise, rare-valid-parallel, incomplete one-order parallel, or balanced reversal tie controls.
- The protocol confirms the same observations need an explicit downstream objective: held-out recovery chooses `full_parallel_generalization`, while sequence-prefix precision chooses `sequence_prefix_precision`.

## Promotion criteria

Not promoted. Promotion would require a deterministic selector, external validation policy, domain-prior mechanism, or multi-objective evaluation rule that uses the alternative set to improve decisions without overclaiming identifiability.

## Experiment links

- EXP-0020: `ALG-0021` ambiguity annotations.
- EXP-0021: this alternative-compilation protocol.

## Property-study notes

No property dossier.

## Decision history

- EXP-0021: added as a smoke-tested multi-net PMIR protocol; not promoted.
