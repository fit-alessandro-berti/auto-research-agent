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

## EXP-0002 — Scaffold rerun before first-iteration extension

Date/time: 2026-05-07T07:09:59+02:00
Goal: rerun the existing scaffold benchmark before adding the first-iteration extension
Command(s):

- `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results-current.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results-current.json`

Code version / commit if available: working tree before EXP-0003 changes; no commit recorded
Candidate IDs: ALG-0001, ALG-0006
Logs/datasets: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `short_loop.json`, `skip.json`, `noise.json`
Metrics: operation counts; structural counts for places, transitions, arcs
Operation-count model: primitives in `scripts/limited_ops.py` before adding explicit `arithmetic`
Results summary: first command failed because `python` is not installed in this environment. Rerun with `python3` succeeded and reproduced the existing scaffold pattern: ALG-0006 used fewer counted operations than ALG-0001, but semantic replay was not yet integrated.
Failures / anomalies: `python: command not found`; ALG-0006 still had the known XOR structural anomaly.
Decision: use `python3` for reproducible commands in this workspace and extend the harness with replay/diagnostics before making promotion decisions.
Next action: implement replay diagnostics and add a heuristic/dependency-graph candidate.

## EXP-0003 — First iteration with replay diagnostics and ALG-0002

Date/time: 2026-05-07T07:09:59+02:00
Goal: create a reproducible first research iteration with an explicit operation model, six specified candidate families, a new limited-operation candidate, replay diagnostics, operation counts, and promotion decisions
Command(s):

- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 -B -m compileall scripts`
- `python3 - <<'PY' ...` diagnostic JSON summary of replay and visible-transition input/output issues

Code version / commit if available: working tree after adding `scripts/dependency_threshold.py`, `scripts/petri_eval.py`, replay integration in `scripts/benchmark.py`, explicit `arithmetic` primitive, and deterministic ALG-0006 evidence ordering; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0003, ALG-0004, ALG-0005, ALG-0006
Logs/datasets: `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `short_loop.json`, `skip.json`, `noise.json`
Metrics: operation counts by primitive, Petri-net structural counts, strict token-game replay with exact final marking, visible-transition input/output diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; counted primitives are `scan_event`, `dict_increment`, `set_insert`, `set_lookup`, `comparison`, `arithmetic`, `relation_classification`, and `construct`
Results summary:

| Log | ALG-0001 ops / replay | ALG-0002 ops / replay | ALG-0006 ops / replay |
|---|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 | 214 / 4 of 4 | 208 / 4 of 4 |
| `parallel_ab_cd.json` | 544 / 4 of 4 | 240 / 4 of 4 | 208 / 4 of 4 |
| `sequence.json` | 499 / 3 of 3 | 211 / 3 of 3 | 181 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 | 118 / 1 of 3 | 110 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 | 144 / 2 of 4 | 132 / 2 of 4 |
| `xor.json` | 552 / 4 of 4 | 228 / 4 of 4 | 204 / 0 of 4 |

Failures / anomalies:

- ALG-0006 fails XOR replay completely: 0/4 traces. The current local split/join compiler creates grouped XOR places plus individual edge places, so unchosen branches can still be required.
- ALG-0001, ALG-0002, and ALG-0006 all fail skip and short-loop gates under strict final marking.
- ALG-0002 looks strong on replay but `noise.json` structural diagnostics show unconstrained visible transitions: `t_C` has no input and `t_B` has no output. This means replay fitness alone is misleading.
- Short-loop diagnostics show `t_B` disconnected from useful input/output for all three executable candidates.

Decision:

- `ALG-0001`: remains `smoke-tested` baseline; not promoted.
- `ALG-0002`: implemented and `smoke-tested`; not promoted because structural diagnostics show under-constrained behavior.
- `ALG-0003`: promoted from idea to `specified`; no executable evidence yet.
- `ALG-0004`: promoted from idea to `specified`; no executable evidence yet.
- `ALG-0005`: promoted from idea to `specified`; no executable evidence yet.
- `ALG-0006`: updated to `smoke-tested`; not promoted because XOR replay is disproven.
- No candidate is `super-promising`; no property dossier was created.

Next action: repair ALG-0006 XOR/skip compilation or create an ALG-0006 variant; add negative-trace precision probes and threshold sweeps for ALG-0002; implement the cut-limited process-tree baseline.
