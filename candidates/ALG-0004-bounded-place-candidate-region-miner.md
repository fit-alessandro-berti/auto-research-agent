# ALG-0004 — Bounded Place-Candidate Region Miner

## Status

benchmarked

## One-sentence hypothesis

A bounded, solver-free search over small place presets and postsets can recover useful Petri-net places that relation miners miss while keeping the operation budget explicit.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Candidate preset/postset size is bounded by a small fixed `k`, initially `k <= 2`.
- Places are accepted by deterministic replay/enablement constraints over observed prefixes.
- No external ILP solver is used in the limited-operation prototype.

## Output

- PMIR place-candidate table with accepted/rejected constraints.
- Petri-net JSON compiled from accepted places.

## Intermediate representation

Prefix-state abstraction plus bounded place candidates with token-balance, enablement, and final-marking evidence.

## Allowed operations / operation-cost model

Uses event scans, prefix-state construction, set inserts/lookups, bounded preset/postset enumeration, comparisons for enablement/token balance, arithmetic for token deltas, and construction operations.

## Algorithm sketch

1. Build prefix states or replay checkpoints for the log.
2. Enumerate candidate `(preset, postset)` pairs up to size `k`.
3. Simulate token balance of each candidate over observed trace prefixes.
4. Reject places that block observed events or leave impossible final residue.
5. Keep a minimal non-redundant subset of accepted places.
6. Add source/sink places and compile to Petri-net JSON.

## Expected complexity

`O(N + P + A^(2k) * P * k)` with fixed `k`; candidate explosion is expected if `k` grows.

## Smoke tests

First gates: `sequence.json`, then `xor.json` and `parallel_ab_cd.json`; all six logs become gates once replay constraints are implemented.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0006` PMIR Split-Join Compiler Lite.
- Future region/ILP miner if dependencies are accepted.

## Metrics

Metrics: accepted/rejected candidate counts, replay, structural diagnostics, operation counts by enumeration and constraint check, negative-trace rejection, and place redundancy.

## Known failure modes

- Candidate explosion for larger `k`.
- Underfitting for too-small `k`.
- Noise and incompleteness overfit constraints.
- Accepted places can still over-constrain unseen but valid behavior.
- Soundness is not guaranteed by local constraints alone.
- Visible-place-only constraints cannot naturally represent optional skips without either leaving activities unconstrained or adding silent structure.

## Executable prototype

Implemented in `scripts/bounded_place_region_miner.py` and wired into:

- `scripts/benchmark.py`
- `scripts/alg0009_deep_tests.py`

The prototype enumerates non-empty preset/postset pairs up to `k = 2`, requires direct-follows evidence for every preset/postset pair, rejects candidates with per-trace token underflow or final residue, then greedily keeps candidates that preserve positive replay.

## EXP-0011 smoke results

Command: `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

| Log | Ops | Replay | Negative rejection | Enumerated | Valid local | Selected |
|---|---:|---:|---:|---:|---:|---:|
| `noise.json` | 1325 | 4/4 | 3/3 | 100 | 4 | 4 |
| `parallel_ab_cd.json` | 1301 | 4/4 | 3/3 | 100 | 4 | 4 |
| `sequence.json` | 804 | 3/3 | 3/3 | 100 | 3 | 3 |
| `short_loop.json` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |
| `skip.json` | 332 | 4/4 | 1/3 | 36 | 1 | 1 |
| `xor.json` | 730 | 4/4 | 3/3 | 100 | 2 | 2 |

## EXP-0011 synthetic comparison

Command: `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`

| Synthetic case | Ops | Replay | Negative rejection | Enumerated | Valid local | Selected |
|---|---:|---:|---:|---:|---:|---:|
| `duplicate_label_rework` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |
| `incomplete_parallel_observed_sequence` | 678 | 2/2 | 3/3 | 100 | 3 | 3 |
| `nested_xor_sequence` | 1350 | 3/3 | 3/3 | 225 | 3 | 3 |
| `noise_reversal_sequence` | 1325 | 4/4 | 3/3 | 100 | 4 | 4 |
| `overlapping_optional_skips` | 802 | 4/4 | 0/3 | 100 | 1 | 1 |
| `parallel_with_optional_branch` | 1604 | 3/3 | 1/3 | 225 | 3 | 3 |
| `short_loop_required` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |

## Promotion criteria

Not promoted after EXP-0011. The prototype meets the executable and benchmark requirements, but does not satisfy the promotion bar because:

- operation counts are much higher than local relation and block baselines;
- short-loop replay remains 1/3;
- optional behavior is overgeneralized (`skip.json` rejects only 1/3 negatives; `overlapping_optional_skips` rejects 0/3);
- it adds no clear advantage over `ALG-0003`, `ALG-0005`, `ALG-0009`, or `ALG-0010` on the current benchmark.

Can become `promising` only after a refined version:

- `k <= 2` prototype runs on all smoke logs;
- observed replay is at least as good as Alpha-Lite on skip/loop counterexamples or reveals why not;
- operation counts are explicit by candidate enumeration and constraint checks;
- accepted places provide a concrete advantage or useful counterexample evidence.

## Experiment links

- EXP-0003: specified as the region/ILP-inspired comparator without using an ILP solver.
- EXP-0011: implemented and benchmarked; not promoted.
- EXP-0012: targeted optional-tau repair split into `ALG-0011`; this record remains the visible-place-only comparator.

## Property-study notes

Potential future dossier topics: replay preservation for accepted places, bounded enumeration complexity, and counterexamples to local-place soundness.

## Decision history

- EXP-0003: specified as the region/ILP-inspired comparator without using an ILP solver.
- EXP-0011: visible-place-only implementation completed; retained as a benchmarked comparator and negative result.
- EXP-0012: retained at `benchmarked`; optional-skip repair is tracked separately as `ALG-0011`.
