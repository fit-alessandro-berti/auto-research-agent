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

## EXP-0004 — Guarded PMIR variant, negative probes, and dependency-threshold sweep

Date/time: 2026-05-07T07:16:03+02:00
Goal: continue the first Petri-net limited-operation goal by repairing the PMIR split/join failure mode, adding negative-trace probes, and sweeping ALG-0002 thresholds
Command(s):

- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/dependency_threshold_sweep.py --logs examples/logs --out experiments/dependency-threshold-sweep.json`
- `python3 -B -m compileall scripts`
- `python3 - <<'PY' ...` diagnostic JSON summaries for replay, negative probes, structural diagnostics, and clean sweep settings

Code version / commit if available: working tree after adding `scripts/pmir_guarded_split_join.py`, negative probes in `scripts/benchmark.py`, bounded silent-transition closure and precision probes in `scripts/petri_eval.py`, and `scripts/dependency_threshold_sweep.py`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0006, ALG-0009
Logs/datasets: positive traces in `examples/logs/*.json`; built-in negative probes in `scripts/benchmark.py`
Metrics: operation counts by primitive, Petri-net structural counts, silent-transition count, strict token-game replay with bounded silent closure, negative-trace rejection, visible-transition structural diagnostics, dependency-threshold sweep outcomes
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; evaluator silent-closure work is not counted as discovery cost
Results summary:

| Log | ALG-0001 ops / replay / neg reject | ALG-0002 ops / replay / neg reject | ALG-0006 ops / replay / neg reject | ALG-0009 ops / replay / neg reject |
|---|---:|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 / 3 of 3 | 214 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 |
| `parallel_ab_cd.json` | 544 / 4 of 4 / 3 of 3 | 240 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 |
| `sequence.json` | 499 / 3 of 3 / 3 of 3 | 211 / 3 of 3 / 3 of 3 | 181 / 3 of 3 / 3 of 3 | 190 / 3 of 3 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 / 1 of 3 | 118 / 1 of 3 / 1 of 3 | 110 / 1 of 3 / 1 of 3 | 113 / 1 of 3 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 / 3 of 3 | 144 / 2 of 4 / 3 of 3 | 132 / 2 of 4 / 3 of 3 | 139 / 4 of 4 / 3 of 3 |
| `xor.json` | 552 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 204 / 0 of 4 / 3 of 3 | 216 / 4 of 4 / 3 of 3 |

Dependency-threshold sweep summary:

- Clean settings, defined as full positive replay, full negative rejection, and no unconstrained visible transitions, exist for `sequence.json`, `xor.json`, `parallel_ab_cd.json`, and `noise.json`.
- No clean setting was found for `short_loop.json` or `skip.json`.
- `skip.json` can get full positive replay at `min_count=1`, `dependency_threshold=0.75`, but then only rejects 1/3 negative probes, so the gain is overgeneralized.

Failures / anomalies:

- `ALG-0009` still fails short-loop behavior. It inherits the relation-classification weakness where bidirectional direct-follows evidence is treated as parallel rather than loop structure.
- Negative probes are hand-written smoke probes, not a complete precision metric.
- `ALG-0002` still has parameter tradeoffs and is not robust enough for promotion.
- Bounded silent-transition closure supports optional-skip smoke replay but is not a soundness or boundedness proof.

Decision:

- `ALG-0009` is promoted to `promising`: written deterministic prototype, explicit PMIR evidence, measured operation counts, lower counted operations than `ALG-0001`, and positive/negative smoke success on five of six smoke families.
- `ALG-0001`, `ALG-0002`, and `ALG-0006` remain `smoke-tested` and unpromoted.
- `ALG-0006` is retained as a useful failed counterexample rather than overwritten.
- No candidate is `super-promising`; no property dossier was created.

Next action: run `ALG-0009` ablations and counterexample search, especially short loops, nested choice/concurrency, overlapping optional guards, trace-order stability, and noise/incompleteness stress tests; implement `ALG-0003` as the next baseline comparator.

## EXP-0005 — ALG-0009 ablations and synthetic counterexample search

Date/time: 2026-05-07T07:20:54+02:00
Goal: deep-test `ALG-0009` with ablations, synthetic counterexamples, and trace-order stability checks
Command(s):

- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 -B -m compileall scripts`
- `python3 - <<'PY' ...` diagnostic JSON summaries for ablations, failures, and stability

Code version / commit if available: working tree after adding ablation switches to `scripts/pmir_guarded_split_join.py` and `scripts/alg0009_deep_tests.py`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0006, ALG-0009 and ALG-0009 ablations (`no_optional`, `no_xor`, `edge_only`)
Logs/datasets: synthetic in-memory cases in `scripts/alg0009_deep_tests.py`: `nested_xor_sequence`, `overlapping_optional_skips`, `parallel_with_optional_branch`, `short_loop_required`, `duplicate_label_rework`, `incomplete_parallel_observed_sequence`, `noise_reversal_sequence`
Metrics: operation counts, replay, negative-trace rejection, visible-transition diagnostics, PMIR evidence, and trace-order signature stability over up to 24 permutations
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; ablation toggles alter discovery operations and are measured separately
Results summary for full `ALG-0009`:

| Synthetic case | Ops | Replay | Negative rejection | Trace-order stable |
|---|---:|---:|---:|---:|
| `nested_xor_sequence` | 291 | 3 of 3 | 3 of 3 | yes |
| `overlapping_optional_skips` | 274 | 1 of 4 | 3 of 3 | yes |
| `parallel_with_optional_branch` | 309 | 1 of 3 | 3 of 3 | yes |
| `short_loop_required` | 113 | 1 of 3 | 1 of 3 | yes |
| `duplicate_label_rework` | 113 | 1 of 3 | 1 of 3 | yes |
| `incomplete_parallel_observed_sequence` | 178 | 2 of 2 | 3 of 3 | yes |
| `noise_reversal_sequence` | 228 | 4 of 4 | 3 of 3 | yes |

Ablation observations:

- Disabling XOR guards makes `nested_xor_sequence` fail replay 0/3 and reject only 1/3 negative traces, confirming the XOR guard is doing real work.
- Disabling optional guards makes the simple skip smoke behavior regress, and does not solve overlapping optional skips.
- Edge-only behavior is consistently cheaper but fails key XOR/optional behavior, so the guarded compiler is not just decorative overhead.
- All checked `ALG-0009` trace-order signatures were stable for the synthetic cases.

Failures / anomalies:

- Overlapping optional guards generate conflicting required places. Example: `A C D` in `overlapping_optional_skips` requires optional-split places from both `A` and `B`.
- Optional behavior mixed with concurrency can falsely force branch order. Example: `parallel_with_optional_branch` blocks `C` before `D` because the optional pattern `D,C,E` creates a split that requires `D` first.
- Short loops and duplicate labels remain unresolved and share the same disconnected-transition symptom as earlier candidates.

Decision:

- `ALG-0009` advances from `promising` to `deep-testing` because it has a written specification, ablation variants, and active counterexample search.
- `ALG-0009` is not `super-promising`; the overlapping optional and optional-concurrency failures are material and require a new refinement.
- No property dossier was created.

Next action: refine `ALG-0009` or split `ALG-0010` with conflict-aware optional guards; implement `ALG-0003` as a block-structured baseline for comparison.

## EXP-0006 — ALG-0010 conflict-aware optional-chain refinement

Date/time: 2026-05-07T07:25:29+02:00
Goal: split a conflict-aware optional-chain refinement from `ALG-0009` and compare it on smoke and synthetic counterexamples
Command(s):

- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -B -m compileall scripts`
- `python3 - <<'PY' ...` diagnostic summaries for ALG-0010 PMIR evidence and replay failures

Code version / commit if available: working tree after adding `scripts/pmir_conflict_aware_optional.py` and wiring `pmir_conflict_aware_optional` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0006, ALG-0009, ALG-0010
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, silent transitions, PMIR optional-chain evidence, trace-order stability
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; ALG-0010 adds counted graph-search comparisons and set operations for transitive reduction and chain selection
Smoke results summary:

| Log | ALG-0010 ops / replay / neg reject |
|---|---:|
| `noise.json` | 312 / 4 of 4 / 3 of 3 |
| `parallel_ab_cd.json` | 312 / 4 of 4 / 3 of 3 |
| `sequence.json` | 239 / 3 of 3 / 3 of 3 |
| `short_loop.json` | 139 / 1 of 3 / 1 of 3 |
| `skip.json` | 187 / 4 of 4 / 3 of 3 |
| `xor.json` | 284 / 4 of 4 / 3 of 3 |

Synthetic comparison summary:

| Synthetic case | ALG-0009 replay / neg reject | ALG-0010 replay / neg reject | Interpretation |
|---|---:|---:|---|
| `nested_xor_sequence` | 3/3 / 3/3 | 3/3 / 3/3 | preserved |
| `overlapping_optional_skips` | 1/4 / 3/3 | 4/4 / 3/3 | fixed by optional-chain compilation |
| `parallel_with_optional_branch` | 1/3 / 3/3 | 0/3 / 3/3 | regression; optional/concurrency unresolved |
| `short_loop_required` | 1/3 / 1/3 | 1/3 / 1/3 | unchanged failure |
| `duplicate_label_rework` | 1/3 / 1/3 | 1/3 / 1/3 | unchanged failure |
| `incomplete_parallel_observed_sequence` | 2/2 / 3/3 | 2/2 / 3/3 | preserved |
| `noise_reversal_sequence` | 4/4 / 3/3 | 4/4 / 3/3 | preserved |

Failures / anomalies:

- ALG-0010 is more expensive than ALG-0009 on every smoke log because it computes eventual-order evidence and a simple transitive reduction.
- ALG-0010 fixes overlapping optional skips by compiling chain `A,B,C,D` with shortcut tau transitions `A->C`, `A->D`, and `B->D`.
- ALG-0010 regresses `parallel_with_optional_branch`; rejected chain evidence avoids the false optional chain, but residual XOR/edge logic still cannot represent the optional/concurrent structure.
- Short loops and duplicate labels remain unresolved.

Decision:

- `ALG-0010` becomes `promising`, not `deep-testing`: it has a deterministic prototype, written specification, measured counts, passes five of six smoke families, and fixes one material `ALG-0009` counterexample.
- `ALG-0010` is not a replacement for `ALG-0009`; it trades higher cost and optional/concurrency regression for better overlapping optional-chain behavior.
- No candidate is `super-promising`; no property dossier was created.

Next action: implement `ALG-0003` Cut-Limited Process Tree Miner to provide a block-structured comparator for the optional/concurrency cases, then decide whether `ALG-0010` should be refined or scoped.

## EXP-0007 — ALG-0003 cut-limited process-tree baseline

Date/time: 2026-05-07T07:32:55+02:00
Goal: implement the specified inductive/process-tree baseline and compare it with guarded PMIR candidates on smoke and synthetic counterexamples
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summary for `cut_limited_process_tree` synthetic results; first attempt failed with `NameError: name 'selected_cut' is not defined` because of shell quoting around an f-string, then rerun with `.format(...)` succeeded.
- `python3 -c '...'` diagnostic summary for `cut_limited_process_tree` smoke selected cuts and structural diagnostics.

Code version / commit if available: working tree after adding `scripts/cut_limited_process_tree.py` and wiring it into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0003, ALG-0006, ALG-0009, ALG-0010
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, selected cut evidence, and fallback frequency
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; EXP-0007 also defines soft budgets `B_smoke = 10N + 8A^2 + 6D + 80` and `B_deep = 16N + 12A^2 + 10D + 120` for later screening discussions
Results summary:

Smoke results for `ALG-0003`:

| Log | Selected cut | Ops | Replay | Negative rejection | Structural diagnostics |
|---|---:|---:|---:|---:|---|
| `noise.json` | parallel | 261 | 4/4 | 3/3 | clean |
| `parallel_ab_cd.json` | parallel | 243 | 4/4 | 3/3 | clean |
| `sequence.json` | sequence | 168 | 3/3 | 3/3 | clean |
| `short_loop.json` | fallback_dfg | 164 | 0/3 | 3/3 | clean but no loop support |
| `skip.json` | optional_sequence | 209 | 4/4 | 3/3 | clean |
| `xor.json` | xor | 194 | 4/4 | 3/3 | clean |

Synthetic `ALG-0003` comparison summary:

| Synthetic case | Selected cut | Ops | Replay | Negative rejection |
|---|---:|---:|---:|---:|
| `nested_xor_sequence` | xor | 255 | 3/3 | 3/3 |
| `overlapping_optional_skips` | optional_sequence | 290 | 4/4 | 3/3 |
| `incomplete_parallel_observed_sequence` | sequence | 155 | 2/2 | 3/3 |
| `noise_reversal_sequence` | parallel | 261 | 4/4 | 3/3 |
| `parallel_with_optional_branch` | fallback_dfg | 314 | 0/3 | 3/3 |
| `short_loop_required` | fallback_dfg | 164 | 0/3 | 3/3 |
| `duplicate_label_rework` | fallback_dfg | 154 | 0/3 | 3/3 |

Comparison notes:

- `ALG-0003` is cleaner than the dependency baseline for block-structured skip behavior and avoids unconstrained visible-transition diagnostics.
- `ALG-0003` matches `ALG-0010` on overlapping optional skips and is cheaper there (290 operations versus 366), but it cannot compose optional behavior inside concurrency.
- `ALG-0003` beats `ALG-0010` on `nested_xor_sequence` operation count (255 versus 394) with the same replay and negative rejection.
- `ALG-0003` is deliberately conservative under incomplete parallel evidence: it selects sequence for `incomplete_parallel_observed_sequence` and rejects the unobserved reversed order.

Failures / anomalies:

- `short_loop.json`, `short_loop_required`, and `duplicate_label_rework` fall back and fail observed replay because duplicated labels and loop cuts are out of current scope.
- `parallel_with_optional_branch` falls back and fails all positives; top-level cut recognition is not enough for optional-concurrency composition.
- `noise.json` and `noise_reversal_sequence` are classified as parallel because the current cut detector treats swapped order as concurrency evidence rather than infrequent noise.
- One diagnostic `python3 -c` command failed due to shell quoting, then was rerun successfully; no experiment artifact was corrupted.

Decision:

- `ALG-0003` advances from `specified` to `promising`: it has a deterministic executable prototype, written candidate record, measured operation counts, clean structural diagnostics, and full replay/negative rejection on five of six smoke families.
- `ALG-0003` does not advance to `deep-testing` or `super-promising`: loop, duplicate-label, and optional-concurrency failures are material and the prototype is not recursive.
- `ALG-0009` remains `deep-testing`; `ALG-0010` remains `promising`; no property dossier was created.

Next action: add recursive cut composition or a bounded optional-concurrency cut for `ALG-0003`, then compare that against a targeted `ALG-0010` refinement; keep loop support as a separate candidate/ablation rather than hiding it in fallback.

## EXP-0008 — ALG-0003 bounded optional-concurrency cut

Date/time: 2026-05-07T07:38:41+02:00
Goal: refine `ALG-0003` with a bounded optional-concurrency cut and verify that it fixes the targeted `parallel_with_optional_branch` counterexample without regressing smoke behavior
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summary comparing `cut_limited_process_tree` with `cut_tree_no_parallel_optional`
- `python3 -c '...'` smoke selected-cut summary for `cut_limited_process_tree`
- `python3 -c '...'` structural/evidence dump for the `parallel_with_optional_branch` result

Code version / commit if available: working tree after adding `parallel_optional_sequence` detection/compilation to `scripts/cut_limited_process_tree.py` and adding the `cut_tree_no_parallel_optional` ablation to `scripts/alg0009_deep_tests.py`; no commit recorded
Candidate IDs: ALG-0003, ALG-0009, ALG-0010; baselines rerun in smoke output
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, selected cut evidence, and ablation comparison
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; added detector uses counted relation classifications, set operations, comparisons, scans, and construction operations
Results summary:

Smoke results for `ALG-0003` after adding the detector:

| Log | Selected cut | Ops | Replay | Negative rejection |
|---|---:|---:|---:|---:|
| `noise.json` | parallel | 261 | 4/4 | 3/3 |
| `parallel_ab_cd.json` | parallel | 243 | 4/4 | 3/3 |
| `sequence.json` | sequence | 168 | 3/3 | 3/3 |
| `short_loop.json` | fallback_dfg | 191 | 0/3 | 3/3 |
| `skip.json` | optional_sequence | 235 | 4/4 | 3/3 |
| `xor.json` | xor | 194 | 4/4 | 3/3 |

Synthetic `ALG-0003` versus ablation summary:

| Synthetic case | Default cut / replay / ops | Ablation cut / replay / ops | Interpretation |
|---|---:|---:|---|
| `parallel_with_optional_branch` | parallel_optional_sequence / 3/3 / 373 | fallback_dfg / 0/3 / 314 | Targeted fix; ablation confirms the new cut is causal. |
| `overlapping_optional_skips` | optional_sequence / 4/4 / 320 | optional_sequence / 4/4 / 290 | Preserved behavior with detector overhead. |
| `nested_xor_sequence` | xor / 3/3 / 255 | xor / 3/3 / 255 | Preserved. |
| `incomplete_parallel_observed_sequence` | sequence / 2/2 / 155 | sequence / 2/2 / 155 | Preserved conservative behavior. |
| `noise_reversal_sequence` | parallel / 4/4 / 261 | parallel / 4/4 / 261 | Preserved. |
| `short_loop_required` | fallback_dfg / 0/3 / 191 | fallback_dfg / 0/3 / 164 | Loop failure unchanged. |
| `duplicate_label_rework` | fallback_dfg / 0/3 / 179 | fallback_dfg / 0/3 / 154 | Duplicate-label failure unchanged. |

Comparison notes:

- `ALG-0003` now outperforms `ALG-0009` and `ALG-0010` on `parallel_with_optional_branch`: `ALG-0003` replays 3/3, `ALG-0009` replays 1/3, and `ALG-0010` replays 0/3, all with 3/3 negative rejection.
- The new Petri-net fragment for `parallel_with_optional_branch` has clean structural diagnostics, 7 places, 6 transitions, 1 silent transition, and 14 arcs.
- The accepted process-tree evidence is `A ; parallel(optional_sequence(B,D optional), C) ; E`.

Failures / anomalies:

- The detector is intentionally narrow: exactly one mandatory singleton branch plus one length-2 branch whose second activity is optional.
- The detector adds overhead on logs that reject it before later cuts: `skip.json` increased from 209 to 235 operations, `short_loop.json` from 164 to 191, `overlapping_optional_skips` from 290 to 320, `duplicate_label_rework` from 154 to 179.
- Loop and duplicate-label failures remain unchanged.

Decision:

- `ALG-0003` moves from `promising` to `deep-testing`: it has a written specification, a refined cut with ablation evidence, active counterexample search, and a concrete advantage over both PMIR variants on the optional-concurrency case.
- `ALG-0003` is not `super-promising`; loop and duplicate-label behavior remain disproven, and the optional-concurrency cut is still narrow.
- No property dossier was created.

Next action: decide whether to add a bounded loop cut to `ALG-0003`, split loop handling into a new candidate, or implement `ALG-0004`/`ALG-0005` as a different-family comparator before further promotion.

## EXP-0009 — ALG-0005 prefix automaton compression comparator

Date/time: 2026-05-07T07:44:26+02:00
Goal: implement the prefix-automaton/grammar-family comparator before further overfitting `ALG-0003`, and validate duplicate-label replay support
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summary of `ALG-0005` synthetic replay, compression, and negative probes
- `python3 -c '...'` diagnostic summary of `ALG-0005` smoke replay, compression, and negative probes
- `python3 -c '...'` diagnostic summary of `ALG-0005` smoke structural diagnostics

Code version / commit if available: working tree after adding `scripts/prefix_automaton_compression.py`, adding optional `transition_labels` to `scripts/pn_ir.py`, extending `scripts/petri_eval.py` to replay multiple same-label transitions, and wiring `prefix_automaton_compression` into the benchmark and synthetic runner; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0003, ALG-0005, ALG-0006, ALG-0009, ALG-0010
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, raw trie node count, compressed-state count, compressed-edge count, suffix-signature merge groups
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; evaluator work is not counted as discovery cost
Results summary:

Smoke results for `ALG-0005`:

| Log | Ops | Replay | Negative rejection | Raw nodes | Compressed states | Edges | Merge groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| `noise.json` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `parallel_ab_cd.json` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `sequence.json` | 228 | 3/3 | 3/3 | 5 | 5 | 4 | 0 |
| `short_loop.json` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |
| `skip.json` | 175 | 4/4 | 3/3 | 5 | 4 | 4 | 1 |
| `xor.json` | 235 | 4/4 | 3/3 | 6 | 4 | 4 | 2 |

Synthetic results for `ALG-0005`:

| Synthetic case | Ops | Replay | Negative rejection | Raw nodes | Compressed states | Edges | Merge groups |
|---|---:|---:|---:|---:|---:|---:|---:|
| `duplicate_label_rework` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |
| `incomplete_parallel_observed_sequence` | 206 | 2/2 | 3/3 | 5 | 5 | 4 | 0 |
| `nested_xor_sequence` | 308 | 3/3 | 3/3 | 8 | 5 | 5 | 3 |
| `noise_reversal_sequence` | 281 | 4/4 | 3/3 | 8 | 6 | 6 | 2 |
| `overlapping_optional_skips` | 270 | 4/4 | 3/3 | 9 | 5 | 7 | 2 |
| `parallel_with_optional_branch` | 368 | 3/3 | 3/3 | 12 | 8 | 9 | 2 |
| `short_loop_required` | 186 | 3/3 | 3/3 | 6 | 5 | 5 | 1 |

Comparison notes:

- `ALG-0005` is the first candidate to exactly replay `short_loop.json`, `short_loop_required`, `duplicate_label_rework`, and all other current smoke/synthetic positives while rejecting all current negative probes.
- This strength is expected for an automaton net and should be interpreted as exact observed-language memorization, not process generalization.
- The evaluator now supports multiple visible transitions sharing one activity label through `transition_labels`; legacy candidates still work through `t_<activity>` inference.
- Suffix-signature compression reduces state count for XOR, skip, loop, and nested suffix-sharing examples, but not for pure sequence or incomplete parallel observed sequence.

Failures / anomalies:

- `ALG-0005` intentionally preserves rare/noisy variants and does not infer concurrency beyond observed interleavings.
- Current negative probes do not test held-out valid behavior, so high rejection can mean overfitting rather than precision.
- Variant explosion remains untested.

Decision:

- `ALG-0005` moves from `specified` to `promising`: deterministic prototype, exact observed replay on all current smoke/synthetic logs, measured operation counts, clean structural diagnostics on smoke logs, compression evidence, and a concrete duplicate-label/loop comparator role.
- `ALG-0005` does not move to `deep-testing` or `super-promising`: it needs variant-explosion stress tests, held-out generalization tests, and language-preservation checks for compression.
- No property dossier was created.

Next action: run variant-explosion and held-out behavior tests for `ALG-0005`, or implement `ALG-0004` bounded place-candidate region mining to add the remaining specified comparator family.

## EXP-0010 — ALG-0005 held-out and variant-explosion stress tests

Date/time: 2026-05-07T07:50:54+02:00
Goal: test whether `ALG-0005` generalizes beyond observed variants and profile variant growth before considering deeper promotion
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 -c '...'` diagnostic summary of raw trie nodes, compressed states, edges, variants, operations, held-out replay, and negative rejection

Code version / commit if available: working tree after adding `scripts/alg0005_stress_tests.py`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0009, ALG-0010
Logs/datasets: synthetic in-memory stress cases generated by `scripts/alg0005_stress_tests.py`
Metrics: operation counts, soft budget ratio, train replay, held-out replay, negative-trace rejection, structural diagnostics, raw trie nodes, compressed states, compressed edges, variant count, selected cut for `ALG-0003`
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; held-out and evaluator replay work is not counted as discovery cost
Results summary:

`ALG-0005` stress summary:

| Case | Variants | Raw nodes | States | Edges | Ops | Held-out replay | Negative rejection |
|---|---:|---:|---:|---:|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | 2 | 9 | 7 | 7 | 315 | 0/4 | 3/3 |
| `heldout_parallel_balanced_2_of_6` | 2 | 10 | 8 | 8 | 328 | 0/4 | 3/3 |
| `heldout_optional_concurrency` | 3 | 12 | 8 | 9 | 368 | 0/2 | 3/3 |
| `noise_memorization` | 2 | 8 | 6 | 6 | 281 | 0/0 | 0/1 |
| `all_permutations_width_2` | 2 | 8 | 6 | 6 | 237 | 0/0 | 3/3 |
| `all_permutations_width_3` | 6 | 23 | 10 | 14 | 555 | 0/0 | 3/3 |
| `all_permutations_width_4` | 24 | 90 | 18 | 34 | 1732 | 0/0 | 3/3 |
| `all_permutations_width_5` | 120 | 447 | 34 | 82 | 8258 | 0/0 | 3/3 |

Comparison notes:

- `ALG-0005` rejected every held-out valid interleaving in both parallel held-out cases and in optional-concurrency held-out behavior.
- `ALG-0003` accepted 4/4 held-out traces for `heldout_parallel_balanced_2_of_6` and 2/2 for `heldout_optional_concurrency`, showing where block generalization beats exact automaton replay.
- `ALG-0003` also failed 0/4 on `heldout_parallel_prefix_biased_2_of_6`; the biased evidence shared a middle prefix, so its top-level cut was too narrow. This separates exact automaton overfitting from insufficient block evidence.
- In `noise_memorization`, the rare reversal was included in training but treated as clean-model negative evidence. `ALG-0005` accepted it, rejecting 0/1 clean negative probes, which documents noise memorization.
- Full-permutation stress shows raw trie nodes and operations grow quickly with variants: width 5 has 120 variants, 447 raw trie nodes, 34 compressed states, and 8258 counted operations. Suffix compression keeps compressed states near subset-style growth, but trie construction still scales with observed variants.

Failures / anomalies:

- `ALG-0005` remains an exact observed-language comparator. These tests are counterevidence against using it as a generalizing miner without an additional grammar/block abstraction.
- The EXP-0010 operation-budget ratios remain below the current soft budget because the soft budget scales with total observed events; this budget does not by itself catch factorial variant growth.
- The stress cases are synthetic and small; larger widths are needed before claiming practical scalability limits.

Decision:

- `ALG-0005` remains `promising`, not `deep-testing`: counterexample search has started, but no refined variant or ablation is implemented yet.
- No candidate is `super-promising`; no property dossier was created.

Next action: implement an `ALG-0005` abstraction/refinement such as bounded suffix-depth merging or grammar block extraction, or implement `ALG-0004` bounded place-candidate region mining to complete the specified comparator families.
