# EXPERIMENT_LOG.md

Append-only record. Do not delete failed experiments.

## EXP-0000 — Scaffold creation

Date/time: initial scaffold
Goal: create reusable process-mining research agent
Command(s): not applicable
Candidate IDs: ALG-0001..ALG-0008 initialized
Logs/datasets: toy logs scaffolded
Metrics: not run
Operation-count model: default limited-operation primitives in `MEMORY.md`
Results summary: scaffold created, no benchmark executed yet
Failures / anomalies: none
Decision: run first smoke benchmark next
Next action: execute `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`

## EXP-0001 — Initial smoke benchmark of scaffold prototypes

Date/time: scaffold validation run
Goal: validate that the starter harness can execute executable candidates
Command(s): `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
Code version / commit if available: scaffold before Git initialization
Candidate IDs: ALG-0001, ALG-0006
Logs/datasets: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `short_loop.json`, `skip.json`, `noise.json`
Metrics: operation counts; structural counts for places, transitions, arcs
Operation-count model: primitives in `scripts/limited_ops.py`
Results summary: both prototypes executed on all toy logs. ALG-0006 used fewer counted operations in every smoke log in this initial harness, but the structural output requires semantic validation before promotion.
Failures / anomalies: ALG-0006 produced more places/arcs than ALG-0001 on `xor.json`, suggesting duplicate or over-constrained XOR join/split behavior to inspect.
Decision: keep ALG-0001 as baseline and ALG-0006 as implemented starter candidate; do not promote yet without replay/conformance checks and semantic inspection.
Next action: add replay/fitness checks or PM4Py-based validation; inspect XOR and loop outputs; create candidate spec files for ALG-0001 and ALG-0006.
