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

## EXP-0011 — ALG-0004 bounded place-candidate region comparator

Date/time: 2026-05-07T07:58:59+02:00
Goal: implement the remaining specified region/ILP-inspired comparator without an external solver, then benchmark it against current smoke and synthetic cases
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summaries for `bounded_place_region_miner` smoke and synthetic candidate counts
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/bounded_place_region_miner.py` and wiring `bounded_place_region_miner` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0003, ALG-0004, ALG-0005, ALG-0006, ALG-0009, ALG-0010
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, bounded place-candidate enumeration counts, locally valid candidates, selected candidates
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0004` counts summarization, relation classification, bounded preset/postset enumeration, candidate evidence checks, token-balance checks, greedy nonblocking selection, and Petri-net construction
Results summary:

Smoke results for `ALG-0004`:

| Log | Ops | Replay | Negative rejection | Enumerated | Valid local | Selected |
|---|---:|---:|---:|---:|---:|---:|
| `noise.json` | 1325 | 4/4 | 3/3 | 100 | 4 | 4 |
| `parallel_ab_cd.json` | 1301 | 4/4 | 3/3 | 100 | 4 | 4 |
| `sequence.json` | 804 | 3/3 | 3/3 | 100 | 3 | 3 |
| `short_loop.json` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |
| `skip.json` | 332 | 4/4 | 1/3 | 36 | 1 | 1 |
| `xor.json` | 730 | 4/4 | 3/3 | 100 | 2 | 2 |

Synthetic results for `ALG-0004`:

| Synthetic case | Ops | Replay | Negative rejection | Enumerated | Valid local | Selected |
|---|---:|---:|---:|---:|---:|---:|
| `duplicate_label_rework` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |
| `incomplete_parallel_observed_sequence` | 678 | 2/2 | 3/3 | 100 | 3 | 3 |
| `nested_xor_sequence` | 1350 | 3/3 | 3/3 | 225 | 3 | 3 |
| `noise_reversal_sequence` | 1325 | 4/4 | 3/3 | 100 | 4 | 4 |
| `overlapping_optional_skips` | 802 | 4/4 | 0/3 | 100 | 1 | 1 |
| `parallel_with_optional_branch` | 1604 | 3/3 | 1/3 | 225 | 3 | 3 |
| `short_loop_required` | 316 | 1/3 | 3/3 | 36 | 1 | 1 |

Comparison notes:

- `ALG-0004` recovers useful visible places for sequence, XOR, parallel, and noise smoke logs, and it keeps positive replay for nested XOR and the current optional-concurrency synthetic case.
- Its counted operation cost is substantially higher than the local PMIR and block baselines on all smoke logs. For example, `sequence.json` costs 804 operations versus 168 for `ALG-0003`, 190 for `ALG-0009`, and 228 for `ALG-0005`.
- Optional behavior exposes the current visible-place limitation: `skip.json` replays positives but rejects only 1/3 negative probes, and `overlapping_optional_skips` rejects 0/3.
- Loop and duplicate-label behavior remain unresolved; both loop-shaped cases replay only 1/3 positives.

Failures / anomalies:

- The prototype is solver-free and bounded to `k <= 2`; this makes enumeration explicit but does not provide the expressive power of full region/ILP mining.
- Places are currently visible-only. Optional behavior needs silent optional-place patterns or a different compilation layer to avoid overgeneralization.
- Candidate pruning uses direct-follows evidence, so it can miss valid non-local region constraints.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`; current reproducibility checks are compile plus benchmark scripts.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- `ALG-0004` advances from `specified` to `benchmarked`: it is executable, wired into smoke and synthetic runners, and has measured operation counts and candidate-enumeration evidence.
- `ALG-0004` is not promoted to `promising` because its cost is high, optional behavior overgeneralizes, and it adds no current quality advantage over `ALG-0003`, `ALG-0005`, `ALG-0009`, or `ALG-0010`.
- No candidate is `super-promising`; no property dossier was created.

Next action: decide whether to refine `ALG-0004` with bounded silent optional-place patterns or retain it as a negative visible-region comparator, then prioritize an `ALG-0005` abstraction/refinement or broader optional-concurrency tests for `ALG-0003`.

## EXP-0012 — ALG-0011 optional-tau repair for bounded region mining

Date/time: 2026-05-07T08:05:32+02:00
Goal: test whether a narrow silent optional-skip repair can fix `ALG-0004`'s simple optional-skip overgeneralization without masking the visible-region baseline
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summaries for `region_optional_tau_miner` optional-pattern counts
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/region_optional_tau_miner.py`, wiring it into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`, and creating `candidates/ALG-0011-region-optional-tau-repair-miner.md`; no commit recorded
Candidate IDs: ALG-0001, ALG-0002, ALG-0003, ALG-0004, ALG-0005, ALG-0006, ALG-0009, ALG-0010, ALG-0011
Logs/datasets: toy logs in `examples/logs/*.json`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, structural diagnostics, visible region candidate counts, accepted optional-pattern counts
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0011` inherits `ALG-0004` bounded region costs and adds counted causal-map construction, non-overlap optional checks, selected-shortcut lookups, and optional tau-fragment construction
Results summary:

Smoke results for `ALG-0011`:

| Log | Ops | Replay | Negative rejection | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `noise.json` | 1365 | 4/4 | 3/3 | 0 |
| `parallel_ab_cd.json` | 1341 | 4/4 | 3/3 | 0 |
| `sequence.json` | 842 | 3/3 | 3/3 | 0 |
| `short_loop.json` | 327 | 1/3 | 3/3 | 0 |
| `skip.json` | 368 | 4/4 | 3/3 | 1 |
| `xor.json` | 770 | 4/4 | 3/3 | 0 |

Synthetic results for `ALG-0011`:

| Synthetic case | Ops | Replay | Negative rejection | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `duplicate_label_rework` | 327 | 1/3 | 3/3 | 0 |
| `incomplete_parallel_observed_sequence` | 716 | 2/2 | 3/3 | 0 |
| `nested_xor_sequence` | 1415 | 3/3 | 3/3 | 0 |
| `noise_reversal_sequence` | 1365 | 4/4 | 3/3 | 0 |
| `overlapping_optional_skips` | 858 | 4/4 | 0/3 | 0 |
| `parallel_with_optional_branch` | 1677 | 3/3 | 1/3 | 0 |
| `short_loop_required` | 327 | 1/3 | 3/3 | 0 |

Comparison notes:

- Targeted repair succeeded on `skip.json`: `ALG-0004` replayed 4/4 positives but rejected only 1/3 negatives; `ALG-0011` replays 4/4 and rejects 3/3 by accepting optional pattern `A,B,C`.
- Sequence, XOR, parallel, and noise smoke behavior did not regress. No optional tau patterns were accepted in those logs.
- The repair is intentionally conservative. In `overlapping_optional_skips`, four optional candidates were considered but rejected by the non-single-context guard; precision remains 0/3 negative rejection, matching `ALG-0004`.
- Optional behavior mixed with concurrency is still not repaired: `parallel_with_optional_branch` remains 3/3 replay with only 1/3 negative rejection.
- Operation counts increase modestly over `ALG-0004` because every log pays causal-map and optional-check overhead, while only `skip.json` benefits.

Failures / anomalies:

- `ALG-0011` inherits `ALG-0004` high enumeration costs and does not solve loops or duplicate labels.
- The non-overlap guard blocks useful overlapping optional-chain patterns by design; this keeps the repair safe but narrow.
- No ablation beyond the `ALG-0004` parent is implemented yet.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- `ALG-0011` is added and promoted to `promising` for a narrow scope: non-overlapping singleton optional skips certified by selected shortcut places.
- It is not `deep-testing` because the repair is narrow, high-cost, lacks an internal ablation, and still fails overlapping optional and optional/concurrency precision probes.
- `ALG-0004` remains `benchmarked` as the visible-place-only negative comparator.
- No candidate is `super-promising`; no property dossier was created.

Next action: add an `ALG-0011` ablation or broaden optional-pattern tests, then choose between a chain-aware region repair and an `ALG-0005` grammar/block abstraction as the next refinement path.

## EXP-0013 — ALG-0011 optional-pattern ablation and counterexamples

Date/time: 2026-05-07T08:10:31+02:00
Goal: test whether `ALG-0011`'s silent optional repair is causally responsible for the precision gain, and broaden optional-pattern counterexamples before further promotion
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `enable_optional_repair` to `scripts/region_optional_tau_miner.py` and adding `scripts/alg0011_optional_tests.py`; no commit recorded
Candidate IDs: ALG-0003, ALG-0004, ALG-0010, ALG-0011 and ablation `region_optional_tau_no_repair`
Logs/datasets: synthetic optional-pattern cases in `scripts/alg0011_optional_tests.py`: `singleton_optional_skip`, `two_disjoint_optional_skips`, `overlapping_optional_chain`, `optional_inside_parallel`; smoke and broader synthetic artifacts rerun for consistency
Metrics: operation counts, replay, negative-trace rejection, accepted optional-pattern count, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; evaluator replay work is not counted as discovery cost
Results summary:

Optional-pattern ablation results:

| Case | ALG-0004 replay / neg reject / ops | ALG-0011 no-repair replay / neg reject / ops | ALG-0011 replay / neg reject / ops | Accepted optional patterns |
|---|---:|---:|---:|---:|
| `singleton_optional_skip` | 4/4 / 1/3 / 332 | 4/4 / 1/3 / 332 | 4/4 / 3/3 / 368 | 1 |
| `two_disjoint_optional_skips` | 4/4 / 2/3 / 1382 | 4/4 / 2/3 / 1382 | 4/4 / 3/3 / 1489 | 2 |
| `overlapping_optional_chain` | 4/4 / 0/3 / 802 | 4/4 / 0/3 / 802 | 4/4 / 0/3 / 858 | 0 |
| `optional_inside_parallel` | 3/3 / 1/3 / 1604 | 3/3 / 1/3 / 1604 | 3/3 / 1/3 / 1677 | 0 |

Comparator notes:

- `ALG-0003` replays all positives and rejects 3/3 negatives on all four optional-pattern cases.
- `ALG-0010` replays all positives and rejects 3/3 negatives on the singleton, disjoint, and overlapping optional cases, but replays 0/3 positives on `optional_inside_parallel`.

Interpretation:

- The ablation is causal for the intended repair: `region_optional_tau_no_repair` exactly matches `ALG-0004` on all four optional-pattern cases, while full `ALG-0011` improves the singleton and two-disjoint optional cases.
- The non-overlap guard is too narrow for optional chains: `overlapping_optional_chain` accepts zero optional patterns and remains at 0/3 negative rejection.
- Optional behavior inside concurrency remains unrepaired. `ALG-0011` accepts zero optional patterns in `optional_inside_parallel` and remains at 1/3 negative rejection.
- Operation cost remains high because `ALG-0011` inherits `ALG-0004` bounded region enumeration and then adds optional-pattern overhead.

Failures / anomalies:

- The optional test suite is synthetic and still small.
- `ALG-0011` has no answer for loops or duplicate labels beyond inherited `ALG-0004` behavior.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Move `ALG-0011` from `promising` to `deep-testing`: it now has a written specification, an explicit no-repair ablation, and counterexample search for optional-pattern families.
- Do not promote to `super-promising`; high cost plus overlapping optional, optional/concurrency, loop, and duplicate-label failures remain material.
- No property dossier was created.

Next action: decide between a chain-aware region optional repair versus treating overlapping optional chains as the responsibility of `ALG-0010`; separately, start an `ALG-0005` grammar/block abstraction if the next priority is generalization rather than region repair.

## EXP-0014 — ALG-0012 chain-aware region optional repair

Date/time: 2026-05-07T08:16:34+02:00
Goal: test whether selected bounded-region shortcut places can safely certify optional-chain repairs, closing the `ALG-0011` overlapping optional-chain gap
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summaries for `region_optional_chain_miner` optional-chain counts
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/region_optional_chain_miner.py` and wiring `region_optional_chain_miner` into smoke, deep, and optional-pattern runners; no commit recorded
Candidate IDs: ALG-0003, ALG-0004, ALG-0010, ALG-0011, ALG-0012
Logs/datasets: smoke logs in `examples/logs/*.json`; optional-pattern cases in `scripts/alg0011_optional_tests.py`; broader synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, optional-chain count, selected region shortcut evidence, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0012` inherits bounded region enumeration and adds eventual-order scans, transitive-reduction path checks, optional-chain selection, selected-shortcut filtering, and chain-fragment construction
Results summary:

Smoke results for `ALG-0012`:

| Log | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `noise.json` | 1461 | 4/4 | 3/3 | 0 |
| `parallel_ab_cd.json` | 1437 | 4/4 | 3/3 | 0 |
| `sequence.json` | 890 | 3/3 | 3/3 | 0 |
| `short_loop.json` | 357 | 1/3 | 3/3 | 0 |
| `skip.json` | 432 | 4/4 | 3/3 | 1 |
| `xor.json` | 844 | 4/4 | 3/3 | 0 |

Optional-pattern comparison for `ALG-0012`:

| Case | Ops | Replay | Negative rejection | Optional chains | Selected region shortcuts |
|---|---:|---:|---:|---:|---|
| `singleton_optional_skip` | 432 | 4/4 | 3/3 | 1 | `A->C` |
| `two_disjoint_optional_skips` | 1648 | 4/4 | 3/3 | 1 | `A->C`, `C->E` |
| `overlapping_optional_chain` | 1037 | 4/4 | 3/3 | 1 | `A->D` |
| `optional_inside_parallel` | 1815 | 3/3 | 1/3 | 0 | `A->B`, `A->C`, `C->E` |

Broader synthetic results for `ALG-0012`:

| Synthetic case | Ops | Replay | Negative rejection | Optional chains |
|---|---:|---:|---:|---:|
| `duplicate_label_rework` | 357 | 1/3 | 3/3 | 0 |
| `incomplete_parallel_observed_sequence` | 754 | 2/2 | 3/3 | 0 |
| `nested_xor_sequence` | 1515 | 3/3 | 3/3 | 0 |
| `noise_reversal_sequence` | 1461 | 4/4 | 3/3 | 0 |
| `overlapping_optional_skips` | 1037 | 4/4 | 3/3 | 1 |
| `parallel_with_optional_branch` | 1815 | 3/3 | 1/3 | 0 |
| `short_loop_required` | 357 | 1/3 | 3/3 | 0 |

Comparison notes:

- `ALG-0012` fixes the overlapping optional-chain failure left by `ALG-0011`: `overlapping_optional_chain` and `overlapping_optional_skips` improve from 0/3 negative rejection under `ALG-0011` to 3/3 under `ALG-0012`.
- The repair is more expensive than both `ALG-0011` and `ALG-0010`. On `overlapping_optional_chain`, `ALG-0012` costs 1037 operations versus 858 for `ALG-0011`, 802 for `ALG-0004`, 366 for `ALG-0010`, and 320 for `ALG-0003`.
- `ALG-0012` still does not repair optional behavior inside concurrency: `optional_inside_parallel` and `parallel_with_optional_branch` remain 1/3 negative rejection.
- `ALG-0012` preserves smoke successes on sequence, XOR, parallel, skip, and noise but keeps inherited short-loop limitations.

Failures / anomalies:

- High operation cost is now the main objection to the region-repair line.
- Optional/concurrency, loops, and duplicate labels remain unresolved.
- No internal ablation for selected-shortcut certification is implemented yet.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0012` and promote it to `promising`: it has a written spec, deterministic prototype, measured counts, smoke success in its claimed scope, and a concrete advantage over `ALG-0011` on overlapping optional chains.
- Do not move it to `deep-testing` yet; it needs an internal ablation and broader optional/concurrency tests.
- No candidate is `super-promising`; no property dossier was created.

Next action: compare `ALG-0012` against an ablation without selected-shortcut certification, or switch to `ALG-0005` grammar/block abstraction if the next priority is reducing overfitting rather than extending the region repair line.

## EXP-0015 — ALG-0012 selected-shortcut-certification ablation

Date/time: 2026-05-07T08:26:15+02:00
Goal: test whether `ALG-0012`'s selected-region-shortcut certification is necessary or whether order-consistent optional chains can be emitted without it under the current limited-operation suite
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` diagnostic summary for `ALG-0012` versus `ALG-0013` optional-pattern evidence
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `require_region_shortcut` to `scripts/region_optional_chain_miner.py`, adding ablation candidate `ALG-0013`, wiring `region_optional_chain_no_region_cert` into optional and synthetic runners, and adding one optional-concurrency probe; no commit recorded
Candidate IDs: ALG-0003, ALG-0004, ALG-0010, ALG-0011, ALG-0012, ALG-0013
Logs/datasets: toy logs in `examples/logs/*.json`; optional-pattern cases in `scripts/alg0011_optional_tests.py`; synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, replay, negative-trace rejection, optional-chain count, selected-shortcut certification setting, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0013` uses the `ALG-0012` operation model minus selected-shortcut certification checks
Results summary:

Optional-pattern ablation results:

| Case | ALG-0012 replay / neg reject / ops / opt | ALG-0013 replay / neg reject / ops / opt |
|---|---:|---:|
| `singleton_optional_skip` | 4/4 / 3/3 / 432 / 1 | 4/4 / 3/3 / 427 / 1 |
| `two_disjoint_optional_skips` | 4/4 / 3/3 / 1648 / 1 | 4/4 / 3/3 / 1636 / 1 |
| `overlapping_optional_chain` | 4/4 / 3/3 / 1037 / 1 | 4/4 / 3/3 / 1026 / 1 |
| `optional_inside_parallel` | 3/3 / 1/3 / 1815 / 0 | 3/3 / 1/3 / 1815 / 0 |
| `optional_singleton_parallel_branch` | 4/4 / 2/3 / 1008 / 0 | 4/4 / 2/3 / 1008 / 0 |

Broader synthetic ablation results:

| Synthetic case | ALG-0012 replay / neg reject / ops | ALG-0013 replay / neg reject / ops |
|---|---:|---:|
| `nested_xor_sequence` | 3/3 / 3/3 / 1515 | 3/3 / 3/3 / 1515 |
| `overlapping_optional_skips` | 4/4 / 3/3 / 1037 | 4/4 / 3/3 / 1026 |
| `parallel_with_optional_branch` | 3/3 / 1/3 / 1815 | 3/3 / 1/3 / 1815 |
| `short_loop_required` | 1/3 / 3/3 / 357 | 1/3 / 3/3 / 357 |
| `duplicate_label_rework` | 1/3 / 3/3 / 357 | 1/3 / 3/3 / 357 |
| `incomplete_parallel_observed_sequence` | 2/2 / 3/3 / 754 | 2/2 / 3/3 / 754 |
| `noise_reversal_sequence` | 4/4 / 3/3 / 1461 | 4/4 / 3/3 / 1461 |

Additional optional-concurrency probe:

| Candidate | `optional_singleton_parallel_branch` replay / neg reject / ops |
|---|---:|
| `ALG-0003` | 0/4 / 3/3 / 292 |
| `ALG-0004` | 4/4 / 2/3 / 880 |
| `ALG-0010` | 3/4 / 3/3 / 305 |
| `ALG-0011` | 4/4 / 2/3 / 920 |
| `ALG-0012` | 4/4 / 2/3 / 1008 |
| `ALG-0013` | 4/4 / 2/3 / 1008 |

Smoke results:

- Rerunning `scripts/benchmark.py` on `examples/logs` produced the same default `ALG-0012` smoke summary as EXP-0014: sequence, XOR, parallel, skip, and noise pass replay/negative probes; short-loop replay remains 1/3.

Interpretation:

- The selected-shortcut-certification ablation is not causal under current tests: `ALG-0013` matches `ALG-0012` on all optional-pattern and broader synthetic replay/negative metrics.
- The measured savings from disabling certification are tiny: 5 operations on singleton optional skip, 12 on two-disjoint optional skips, and 11 on overlapping optional chains; no savings appear where no optional chain is emitted.
- The new `optional_singleton_parallel_branch` case broadens optional/concurrency testing and exposes a distinct gap: current region variants preserve positive replay but still overgeneralize one negative probe, while `ALG-0003` and `ALG-0010` lose positive replay.
- `ALG-0012` still has no cost/quality advantage over `ALG-0003` or `ALG-0010` except for the region-family comparison against `ALG-0011`.

Failures / anomalies:

- The ablation did not find a case where selected-shortcut certification prevents a harmful optional-chain emission.
- Optional/concurrency remains unresolved for all current non-automaton generalizing candidates in at least one tested shape.
- `ALG-0013` currently returns through the same module as `ALG-0012`; its distinguishing configuration is `require_region_shortcut=false`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0013` as a tracked smoke-tested ablation, but do not promote it: it only offers tiny count savings and weakens the certification argument.
- Keep `ALG-0012` at `promising`, not `deep-testing`: the required ablation now exists, but it did not establish a clearer advantage over `ALG-0010` or `ALG-0003`.
- Do not create a property dossier. No candidate is `super-promising`.

Next action: either search systematically for an uncertified-chain false positive, or pause the high-cost region repair line and implement an `ALG-0005` grammar/block abstraction to address automaton overfitting.

## EXP-0016 — ALG-0014 prefix block abstraction refinement

Date/time: 2026-05-07T08:34:15+02:00
Goal: implement and test a small grammar/block abstraction for the `ALG-0005` prefix-automaton family, targeting held-out interleaving generalization while preserving limited-operation instrumentation
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/prefix_block_abstraction.py`, wiring `prefix_block_abstraction` into smoke, synthetic, optional, and ALG-0005 stress runners, and creating `candidates/ALG-0014-prefix-block-abstraction-miner.md`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0010, ALG-0011, ALG-0012, ALG-0014
Logs/datasets: toy logs in `examples/logs/*.json`; ALG-0005 stress cases in `scripts/alg0005_stress_tests.py`; optional-pattern cases in `scripts/alg0011_optional_tests.py`; broader synthetic cases in `scripts/alg0009_deep_tests.py`
Metrics: operation counts, training replay, held-out replay, negative-trace rejection, selected grammar, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0014` counts summarization, relation classification, common-prefix/common-suffix scans, segment-set comparisons, block construction, and exact-automaton fallback operations when no block grammar is accepted
Results summary:

Smoke results for `ALG-0014`:

| Log | Ops | Replay | Negative rejection |
|---|---:|---:|---:|
| `noise.json` | 235 | 4/4 | 3/3 |
| `parallel_ab_cd.json` | 227 | 4/4 | 3/3 |
| `sequence.json` | 272 | 3/3 | 3/3 |
| `short_loop.json` | 248 | 3/3 | 3/3 |
| `skip.json` | 216 | 4/4 | 3/3 |
| `xor.json` | 294 | 4/4 | 3/3 |

ALG-0005 stress comparison:

| Case | ALG-0005 held-out / neg reject / ops | ALG-0014 grammar / held-out / neg reject / ops | ALG-0003 held-out / cut |
|---|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | 0/4 / 3/3 / 315 | `parallel_block` / 0/4 / 3/3 / 254 | 0/4 / `parallel` |
| `heldout_parallel_balanced_2_of_6` | 0/4 / 3/3 / 328 | `parallel_block` / 4/4 / 3/3 / 257 | 4/4 / `parallel` |
| `heldout_optional_concurrency` | 0/2 / 3/3 / 368 | `exact_prefix_automaton` / 0/2 / 3/3 / 447 | 2/2 / `parallel_optional_sequence` |
| `noise_memorization` | 0/0 / 0/1 / 281 | `parallel_block` / 0/0 / 0/1 / 235 | 0/0 / `parallel` |
| `all_permutations_width_2` | 0/0 / 3/3 / 237 | `parallel_block` / 0/0 / 3/3 / 183 | 0/0 / `parallel` |
| `all_permutations_width_3` | 0/0 / 3/3 / 555 | `parallel_block` / 0/0 / 3/3 / 363 | 0/0 / `parallel` |

Optional-pattern results for `ALG-0014`:

| Case | Ops | Replay | Negative rejection |
|---|---:|---:|---:|
| `singleton_optional_skip` | 216 | 4/4 | 3/3 |
| `two_disjoint_optional_skips` | 448 | 4/4 | 3/3 |
| `overlapping_optional_chain` | 333 | 4/4 | 3/3 |
| `optional_inside_parallel` | 447 | 3/3 | 3/3 |
| `optional_singleton_parallel_branch` | 278 | 4/4 | 3/3 |

Broader synthetic results for `ALG-0014`:

| Synthetic case | Ops | Replay | Negative rejection | Selected grammar |
|---|---:|---:|---:|---|
| `nested_xor_sequence` | 365 | 3/3 | 3/3 | `exact_prefix_automaton` |
| `overlapping_optional_skips` | 333 | 4/4 | 3/3 | `exact_prefix_automaton` |
| `parallel_with_optional_branch` | 447 | 3/3 | 3/3 | `exact_prefix_automaton` |
| `short_loop_required` | 248 | 3/3 | 3/3 | `exact_prefix_automaton` |
| `duplicate_label_rework` | 232 | 3/3 | 3/3 | `exact_prefix_automaton` |
| `incomplete_parallel_observed_sequence` | 234 | 2/2 | 3/3 | `exact_prefix_automaton` |
| `noise_reversal_sequence` | 235 | 4/4 | 3/3 | `parallel_block` |

Interpretation:

- `ALG-0014` partially addresses `ALG-0005` overfitting: on balanced two-of-six held-out parallel interleavings it improves held-out replay from 0/4 to 4/4 while reducing counted operations from 328 to 257.
- The abstraction is evidence-sensitive. Prefix-biased training still fails held-out interleavings because the shared first branch is absorbed into the common prefix, so both `ALG-0014` and `ALG-0003` replay 0/4 held-out traces there.
- `ALG-0014` fixes the EXP-0015 `optional_singleton_parallel_branch` counterexample with 4/4 replay and 3/3 negative rejection at 278 operations, where `ALG-0003` replayed 0/4, `ALG-0010` replayed 3/4, and region variants rejected only 2/3 negatives.
- The noise-memorization problem remains material: in `noise_memorization`, `ALG-0014` selects `parallel_block` and accepts the rare reversed trace just like `ALG-0005` accepts it by exact replay.
- Many loop/duplicate-label successes are fallback exact automaton replay, not structural loop or duplicate-label generalization.

Failures / anomalies:

- `ALG-0014` is shallow: it supports one middle block only.
- Support/noise thresholds are absent; rare reversals can trigger a parallel block.
- Prefix-bias remains unresolved.
- Full-permutation stress width 4 and 5 currently fall back to exact automaton because the stress generator reuses `E` as both branch label and suffix, creating duplicate-label input for the block abstraction guard.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0014` and promote it to `promising`: it has a written spec, deterministic prototype, measured counts, smoke success, and concrete advantages on balanced held-out interleavings and the optional-singleton parallel counterexample.
- Do not promote to `deep-testing` or `super-promising`: prefix-bias, noise, shallow-block composition, and fallback memorization are material limitations.
- No property dossier was created.

Next action: add support thresholds and a prefix-bias guard/merge for `ALG-0014`, or run a controlled ablation disabling exact fallback to separate true grammar generalization from memorization.

## EXP-0017 — ALG-0015 support-guard refinement and ALG-0016 fallback ablation

Date/time: 2026-05-07T08:42:37+02:00
Goal: refine `ALG-0014` with support/noise guards and prefix-bias handling, then run an exact-fallback-disabled ablation to separate true grammar behavior from automaton memorization
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 -c '...'` selected-grammar diagnostic summary for `ALG-0015` and `ALG-0016`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding support-skew checks, prefix merge, dominant-sequence noise handling, wrappers `scripts/prefix_block_support_guard.py` and `scripts/prefix_block_grammar_only.py`, and candidate records for `ALG-0015` and `ALG-0016`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0014, ALG-0015, ALG-0016
Logs/datasets: toy logs in `examples/logs/*.json`; ALG-0005 stress cases; optional-pattern cases; broader synthetic cases
Metrics: operation counts, training replay, held-out replay, negative-trace rejection, selected grammar, exact-fallback dependence
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0015` adds support counters, skew comparisons, prefix-merge checks, and same-activity-set dominant-sequence checks to `ALG-0014`; `ALG-0016` removes exact automaton fallback costs
Results summary:

ALG-0005 stress comparison:

| Case | ALG-0014 grammar / train / held-out / neg reject / ops | ALG-0015 grammar / train / held-out / neg reject / ops | ALG-0016 grammar / train / held-out / neg reject / ops |
|---|---:|---:|---:|
| `heldout_parallel_prefix_biased_2_of_6` | `parallel_block` / 2/2 / 0/4 / 3/3 / 257 | `parallel_block` / 2/2 / 4/4 / 3/3 / 267 | `parallel_block` / 2/2 / 4/4 / 3/3 / 267 |
| `heldout_parallel_balanced_2_of_6` | `parallel_block` / 2/2 / 4/4 / 3/3 / 260 | `parallel_block` / 2/2 / 4/4 / 3/3 / 262 | `parallel_block` / 2/2 / 4/4 / 3/3 / 262 |
| `heldout_optional_concurrency` | `exact_prefix_automaton` / 3/3 / 0/2 / 3/3 / 447 | `exact_prefix_automaton` / 3/3 / 0/2 / 3/3 / 470 | `no_grammar` / 0/3 / 0/2 / 3/3 / 306 |
| `noise_memorization` | `parallel_block` / 4/4 / 0/0 / 0/1 / 240 | `dominant_sequence` / 3/4 / 0/0 / 1/1 / 339 | `dominant_sequence` / 3/4 / 0/0 / 1/1 / 339 |
| `all_permutations_width_2` | `parallel_block` / 2/2 / 0/0 / 3/3 / 186 | `parallel_block` / 2/2 / 0/0 / 3/3 / 188 | `parallel_block` / 2/2 / 0/0 / 3/3 / 188 |
| `all_permutations_width_3` | `parallel_block` / 6/6 / 0/0 / 3/3 / 370 | `parallel_block` / 6/6 / 0/0 / 3/3 / 372 | `parallel_block` / 6/6 / 0/0 / 3/3 / 372 |

Toy smoke results for `ALG-0015`:

| Log | Grammar | Ops | Replay | Negative rejection |
|---|---|---:|---:|---:|
| `noise.json` | `dominant_sequence` | 339 | 3/4 | 3/3 |
| `parallel_ab_cd.json` | `parallel_block` | 234 | 4/4 | 3/3 |
| `sequence.json` | `dominant_sequence` | 242 | 3/3 | 3/3 |
| `short_loop.json` | `exact_prefix_automaton` | 263 | 3/3 | 3/3 |
| `skip.json` | `exact_prefix_automaton` | 227 | 4/4 | 3/3 |
| `xor.json` | `exact_prefix_automaton` | 306 | 4/4 | 3/3 |

Broader synthetic results for `ALG-0015`:

| Synthetic case | Grammar | Ops | Replay | Negative rejection |
|---|---|---:|---:|---:|
| `nested_xor_sequence` | `exact_prefix_automaton` | 380 | 3/3 | 3/3 |
| `overlapping_optional_skips` | `exact_prefix_automaton` | 347 | 4/4 | 3/3 |
| `parallel_with_optional_branch` | `exact_prefix_automaton` | 470 | 3/3 | 3/3 |
| `short_loop_required` | `exact_prefix_automaton` | 263 | 3/3 | 3/3 |
| `duplicate_label_rework` | `exact_prefix_automaton` | 243 | 3/3 | 3/3 |
| `incomplete_parallel_observed_sequence` | `dominant_sequence` | 207 | 2/2 | 3/3 |
| `noise_reversal_sequence` | `dominant_sequence` | 339 | 3/4 | 3/3 |

Exact-fallback ablation interpretation:

- `ALG-0016` matches `ALG-0015` on prefix-biased held-out parallel, balanced held-out parallel, rare-reversal noise, sequence, simple parallel, and optional-singleton parallel. These are true grammar behaviors.
- `ALG-0016` fails fallback-dependent cases with `no_grammar`, including skip, XOR, short loops, duplicate-label rework, overlapping optional chains, and optional concurrency. These `ALG-0015` successes are inherited exact automaton replay, not grammar generalization.

Interpretation:

- Prefix merge repaired the EXP-0016 prefix-bias failure: held-out replay improves from 0/4 under `ALG-0014` to 4/4 under `ALG-0015`, with 3/3 negative rejection.
- Support-skew plus same-activity-set dominant-sequence handling repaired the rare-reversal precision probe: `noise_memorization` negative rejection improves from 0/1 under `ALG-0014` to 1/1 under `ALG-0015`.
- The repair trades away rare-trace replay: `noise.json` and `noise_reversal_sequence` replay 3/4 positives instead of 4/4 because the rare reversal is treated as noise.
- The same-activity-set guard prevents the initial dominant-sequence variant from misclassifying `nested_xor_sequence`; after the fix `ALG-0015` uses exact fallback and replays 3/3 with 3/3 negative rejection.

Failures / anomalies:

- `ALG-0015` still depends heavily on exact fallback.
- `ALG-0016` shows grammar coverage is still narrow.
- Dominant-sequence handling encodes a precision/fitness tradeoff, not an unambiguous quality improvement.
- Full-permutation width 4 and 5 still fall back because the stress generator duplicates `E` as both branch label and suffix.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0015` and promote it to `promising`: it has a written spec, deterministic prototype, measured counts, and concrete improvements over `ALG-0014` on prefix-biased held-out interleavings and rare-reversal noise precision.
- Add `ALG-0016` as a smoke-tested ablation; do not promote it because fallback-dependent replay collapses.
- Do not promote anything to `deep-testing` or `super-promising`; no property dossier was created.

Next action: run ablations isolating prefix merge versus dominant-sequence handling inside `ALG-0015`, then expand noisy/incomplete-log tests before any deeper promotion.

## EXP-0018 — ALG-0015 feature ablations

Date/time: 2026-05-07T09:04:52+02:00
Goal: isolate which `ALG-0015` features cause the prefix-biased held-out parallel repair and rare-reversal precision repair
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 -c '...'` ablation diagnostic summary
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/prefix_block_support_only.py`, `scripts/prefix_block_prefix_merge_only.py`, `scripts/prefix_block_dominant_only.py`, `scripts/alg0015_ablation_tests.py`, wiring the new ablations into standard runners, and creating candidate records `ALG-0017` through `ALG-0019`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0014, ALG-0015, ALG-0016, ALG-0017, ALG-0018, ALG-0019
Logs/datasets: targeted ablation cases in `scripts/alg0015_ablation_tests.py`; toy logs in `examples/logs/*.json`; ALG-0005 stress cases; optional-pattern cases; broader synthetic cases
Metrics: operation counts, selected grammar, grammar origin, support counts, training replay, held-out replay, negative-trace rejection, exact-fallback dependence
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0017` adds support-skew counting to `ALG-0014`, `ALG-0018` adds prefix-merge checks, and `ALG-0019` adds same-activity-set dominant-sequence checks

Targeted ablation summary:

| Case | ALG-0014 grammar / held-out / neg reject | ALG-0017 support-only | ALG-0018 prefix-merge | ALG-0019 dominant-only | ALG-0015 full |
|---|---:|---:|---:|---:|---:|
| `prefix_biased_parallel_2_of_6` | `parallel_block` common / 0/4 / 3/3 | `parallel_block` common / 0/4 / 3/3 | `parallel_block` prefix-merge / 4/4 / 3/3 | `parallel_block` common / 0/4 / 3/3 | `parallel_block` prefix-merge / 4/4 / 3/3 |
| `balanced_parallel_2_of_6` | `parallel_block` common / 4/4 / 3/3 | `parallel_block` common / 4/4 / 3/3 | `parallel_block` common / 4/4 / 3/3 | `parallel_block` common / 4/4 / 3/3 | `parallel_block` common / 4/4 / 3/3 |
| `rare_reversal_noise_3_to_1` | `parallel_block` common / 0/0 / 0/1 | `exact_prefix_automaton` / 0/0 / 0/1 | `exact_prefix_automaton` / 0/0 / 0/1 | `dominant_sequence` / 0/0 / 1/1 | `dominant_sequence` / 0/0 / 1/1 |
| `rare_reversal_noise_5_to_1` | `parallel_block` common / 0/0 / 0/1 | `exact_prefix_automaton` / 0/0 / 0/1 | `exact_prefix_automaton` / 0/0 / 0/1 | `dominant_sequence` / 0/0 / 1/1 | `dominant_sequence` / 0/0 / 1/1 |
| `ambiguous_reversal_tie` | `parallel_block` common / 0/0 / 3/3 | `parallel_block` common / 0/0 / 3/3 | `parallel_block` common / 0/0 / 3/3 | `parallel_block` common / 0/0 / 3/3 | `parallel_block` common / 0/0 / 3/3 |
| `same_order_incomplete_parallel` | `exact_prefix_automaton` / 0/1 / 3/3 | `exact_prefix_automaton` / 0/1 / 3/3 | `exact_prefix_automaton` / 0/1 / 3/3 | `dominant_sequence` / 0/1 / 3/3 | `dominant_sequence` / 0/1 / 3/3 |
| `different_activity_sets_skip_like` | `exact_prefix_automaton` / 0/0 / 3/3 | `exact_prefix_automaton` / 0/0 / 3/3 | `exact_prefix_automaton` / 0/0 / 3/3 | `exact_prefix_automaton` / 0/0 / 3/3 | `exact_prefix_automaton` / 0/0 / 3/3 |

Standard-suite deltas:

- Toy smoke now includes `ALG-0017`, `ALG-0018`, and `ALG-0019`. They all pass replay/negative probes where exact fallback or existing block grammars apply, except `ALG-0019` intentionally replays 3/4 on `noise.json`, matching full `ALG-0015`.
- ALG-0005 stress confirms the targeted result in the standard artifact: on `heldout_parallel_prefix_biased_2_of_6`, `ALG-0018`, `ALG-0015`, and `ALG-0016` replay 4/4 held-out traces, while `ALG-0014`, `ALG-0017`, and `ALG-0019` replay 0/4.
- The optional-pattern suite shows the three new ablations match the prior prefix-block family on optional cases; the grammar-only ablation still replays 0 positives on fallback-dependent optional-chain cases.
- Broader synthetic tests show no new loop, duplicate-label, or optional-concurrency repair from these ablations.

Interpretation:

- Prefix merge is causal for the prefix-biased held-out parallel repair. Support-only and dominant-only ablations retain the old common-boundary split and fail 0/4 held-out traces.
- Dominant-sequence handling is causal for rare-reversal precision. Support-only and prefix-merge-only variants reject the unsupported parallel block but fall back to exact replay, so they still accept the noisy observed rare trace.
- Support-skew alone is useful as a selection guard, but it does not improve end-to-end precision while exact fallback is enabled.
- The same-activity-set and tie guards behave as intended in the targeted suite: skip-like differing activity sets do not trigger dominant sequence, and balanced reversal evidence remains a parallel block.

Failures / anomalies:

- `same_order_incomplete_parallel` confirms the current dominant-sequence policy is conservative under incomplete parallel evidence: it rejects the held-out reversed order.
- The ablations do not broaden grammar coverage for loops, duplicate labels, XOR, optional chains, or optional/concurrency.
- `ALG-0018` needs a future false-positive search for cases where moving the final common-prefix activity is unsound.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0017`, `ALG-0018`, and `ALG-0019` as smoke-tested ablation controls; do not promote them independently.
- Move `ALG-0015` from `promising` to `deep-testing` because written feature ablations and targeted counterexample tests now exist.
- Do not promote anything to `super-promising`; no property dossier was created.

Next action: broaden `ALG-0015` noisy/incomplete testing with threshold sweeps and prefix-merge false-positive search, then decide whether loop support belongs in the prefix-block grammar family or should remain a separate candidate line.

## EXP-0019 — ALG-0015 noisy/incomplete sweep and prefix-merge ambiguity

Date/time: 2026-05-07T09:31:18+02:00
Goal: broaden `ALG-0015` noisy/incomplete testing with support-skew and dominant-threshold sweeps, and search for prefix-merge false positives
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 -c '...'` diagnostic summary for `ALG-0020`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after exposing `prefix_merge_policy`, `min_dominant_count`, and `min_dominant_ratio_percent` in `scripts/prefix_block_abstraction.py`, adding `scripts/prefix_block_conservative_merge.py`, wiring `prefix_block_conservative_merge` into standard runners, adding `scripts/alg0015_noise_incomplete_tests.py`, and creating `candidates/ALG-0020-prefix-block-conservative-merge-miner.md`; no commit recorded
Candidate IDs: ALG-0014, ALG-0015, ALG-0016, ALG-0017, ALG-0018, ALG-0019, ALG-0020
Logs/datasets: targeted noisy/incomplete and prefix-merge ambiguity cases in `scripts/alg0015_noise_incomplete_tests.py`; toy logs in `examples/logs/*.json`; ALG-0005 stress cases; optional-pattern cases; broader synthetic cases
Metrics: operation counts, selected grammar, grammar origin, support counts, training replay, held-out replay, negative-trace rejection, threshold configuration, prefix-merge policy
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; sweep variants reuse `ALG-0015` primitives while varying support-skew and dominant-ratio thresholds

Prefix-merge ambiguity summary:

| Case | ALG-0015 full | ALG-0020 conservative | Interpretation |
|---|---:|---:|---|
| `prefix_merge_full_parallel_interpretation` | 4/4 held-out replay, 3/3 neg reject, `prefix_merge` | 0/4 held-out replay, 3/3 neg reject, `common_boundary` | Full B/C/D parallel: prefix merge helps. |
| `prefix_merge_sequence_then_parallel_interpretation` | 0/4 negative rejection, `prefix_merge` | 4/4 negative rejection, `common_boundary` | B then C/D parallel: prefix merge overgeneralizes. |

Noise and threshold summary:

| Case | Current ALG-0015 behavior | Notable sweep result |
|---|---|---|
| `noise_reversal_2_to_1` | `parallel_block`, 3/3 replay, 0/1 rare-reversal rejection | `max_parallel_support_skew=1` selects `dominant_sequence`, replaying 2/3 and rejecting 1/1. |
| `noise_reversal_3_to_1` | `dominant_sequence`, 3/4 replay, 1/1 rejection | `min_dominant_ratio_percent=85` is too strict and falls back to exact replay, rejecting 0/1. |
| `noise_reversal_5_to_1` | `dominant_sequence`, 5/6 replay, 1/1 rejection | Ratio 85 is still too strict because support is 5/6; ratios 60 and 75 select dominant sequence. |
| `valid_rare_parallel_3_to_1` | `dominant_sequence`, 3/4 replay, 3/3 neg reject | Same observations as 3-to-1 noise show the unavoidable precision/fitness ambiguity if the rare reversal is actually valid. |
| `incomplete_parallel_one_order_2` | `dominant_sequence`, 2/2 replay, 0/1 held-out reversal replay | Current policy remains conservative under missing reversed-order evidence. |

Standard-suite deltas:

- `ALG-0020` matches `ALG-0015` on all six toy smoke logs.
- On ALG-0005 stress, `ALG-0020` matches `ALG-0015` on balanced held-out parallel and rare-reversal noise, but loses the prefix-biased held-out repair: `heldout_parallel_prefix_biased_2_of_6` held-out replay is 0/4 instead of `ALG-0015`'s 4/4.
- Optional-pattern and broader synthetic runs show no new loop, duplicate-label, XOR, optional-chain, or optional/concurrency repair from `ALG-0020`.

Interpretation:

- Prefix merge is not a free improvement. The same observed log supports two incompatible interpretations; without more evidence or a user/domain prior, `ALG-0015` and `ALG-0020` encode opposite bets.
- Support-skew threshold is currently the dominant control for 2:1 noise. A skew of 2 treats the rare reversal as parallel; a skew of 1 treats it as noise through dominant-sequence selection.
- Dominant-ratio thresholds above 75 are too strict for the current small noise cases because 3/4 and 5/6 support should still be considered dominant under the existing noise policy.
- `ALG-0020` is useful as a precision-side counter-candidate but not a replacement for `ALG-0015`.

Failures / anomalies:

- No threshold setting resolves the ambiguity between rare valid parallel behavior and rare noise without an explicit assumption.
- No threshold setting recovers held-out reversed order when only one order is observed.
- `ALG-0020` still relies on exact fallback for the same broad cases as `ALG-0015`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0020` as a smoke-tested tradeoff candidate; do not promote it.
- Keep `ALG-0015` at `deep-testing`, not `super-promising`; the new evidence documents a fundamental ambiguity rather than a clean repair.
- Do not create a property dossier.

Next action: decide whether to add an explicit ambiguity-aware PMIR output mode for prefix-block candidates, or pivot to bounded loop support as a separate candidate line.

## EXP-0020 — ALG-0021 ambiguity-aware PMIR evidence

Date/time: 2026-05-07T09:56:00+02:00
Goal: add an explicit ambiguity-aware PMIR output mode for prefix-block candidates so common-boundary and prefix-merge interpretations can both be tracked when the observed log does not identify a unique branch scope
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 -c '...'` diagnostic ambiguity summary over `experiments/alg0015-noise-incomplete-tests.json` and `experiments/alg0005-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `_prefix_merge_ambiguity` and `emit_prefix_merge_ambiguity` to `scripts/prefix_block_abstraction.py`, adding `scripts/prefix_block_ambiguity_aware.py`, wiring `prefix_block_ambiguity_aware` into standard runners, and creating `candidates/ALG-0021-prefix-block-ambiguity-aware-pmir-miner.md`; no commit recorded
Candidate IDs: ALG-0015, ALG-0020, ALG-0021, plus existing prefix-block ablation controls
Logs/datasets: targeted noisy/incomplete and prefix-merge ambiguity cases in `scripts/alg0015_noise_incomplete_tests.py`; toy logs in `examples/logs/*.json`; ALG-0005 stress cases; optional-pattern cases; broader synthetic cases
Metrics: operation counts, selected grammar, grammar origin, selected policy, ambiguity flag, ambiguity alternatives, training replay, held-out replay, negative-trace rejection
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0021` adds a second bounded common-boundary/prefix-merge check to emit ambiguity alternatives into PMIR evidence

Targeted ambiguity results for `ALG-0021`:

| Case | Grammar / origin | Ambiguity detected | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|---:|
| `prefix_merge_full_parallel_interpretation` | `parallel_block` / `prefix_merge` | yes | 2/2 | 4/4 | 3/3 | 361 |
| `prefix_merge_sequence_then_parallel_interpretation` | `parallel_block` / `prefix_merge` | yes | 2/2 | 0/0 | 0/4 | 361 |
| `noise_reversal_3_to_1` | `dominant_sequence` | no | 3/4 | 0/0 | 1/1 | 415 |
| `incomplete_parallel_one_order_2` | `dominant_sequence` | no | 2/2 | 0/1 | 3/3 | 227 |

Standard-suite deltas:

- On the six toy smoke logs, `ALG-0021` matches `ALG-0015` selected-net behavior with higher counted operations from ambiguity evidence: `noise.json` 415 ops / 3 of 4 replay / 3 of 3 negative rejection; `parallel_ab_cd.json` 302 / 4 of 4 / 3 of 3; `sequence.json` 271 / 3 of 3 / 3 of 3; `short_loop.json` 299 / 3 of 3 / 3 of 3; `skip.json` 248 / 4 of 4 / 3 of 3; `xor.json` 329 / 4 of 4 / 3 of 3.
- Ambiguity is not detected on the six toy smoke logs.
- On ALG-0005 stress, `ALG-0021` detects ambiguity for `heldout_parallel_prefix_biased_2_of_6`, where the selected grammar is `parallel_block` / `prefix_merge`, held-out replay is 4/4, negative rejection is 3/3, and counted operations are 361.
- On `heldout_parallel_balanced_2_of_6`, ambiguity is false, held-out replay remains 4/4, and counted operations are 314.
- On `noise_memorization`, ambiguity is false, selected grammar remains `dominant_sequence`, negative rejection is 1/1, and counted operations are 415.
- Optional-pattern and broader synthetic runs show no new loop, duplicate-label, XOR, optional-chain, or optional/concurrency repair from `ALG-0021`; the selected Petri net intentionally matches `ALG-0015`.

Interpretation:

- `ALG-0021` converts the EXP-0019 ambiguity from an external note into machine-readable PMIR evidence. It can now tell downstream code that both `sequence_prefix_precision` and `full_parallel_generalization` alternatives are plausible for the same observed prefix-merge log.
- This is not a quality repair for the compiled Petri net. The selected Petri net still follows `ALG-0015`'s full-parallel preference, so the sequence-prefix negative case still rejects 0/4 negatives.
- The ambiguity detector is intentionally narrow: it covers common-boundary versus prefix-merge parallel-block alternatives, not noise versus rare valid behavior, missing reversed-order evidence, loops, duplicate labels, or optional-concurrency.

Failures / anomalies:

- Ambiguity evidence increases operation counts even when no ambiguity is detected.
- No downstream selector consumes the alternatives yet.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0021` as a smoke-tested PMIR/evidence candidate; do not promote it because selected-net quality is unchanged.
- Keep `ALG-0015` at `deep-testing`, not `super-promising`; ambiguity annotations clarify uncertainty but do not settle the prefix-merge assumption.
- Keep `ALG-0020` as the conservative precision-side comparator.
- Do not create a property dossier.

Next action: implement a small downstream ambiguity selector or multi-net evaluation protocol for `ALG-0021`, or pivot to bounded loop support as the next independent candidate line.

## EXP-0021 — ALG-0022 ambiguity-set alternative protocol

Date/time: 2026-05-07T10:13:00+02:00
Goal: consume `ALG-0021` ambiguity annotations by compiling each alternative grammar into a Petri net and evaluating the resulting model set
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0021_ambiguity_protocol_tests.py --out experiments/alg0021-ambiguity-protocol-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/alg0021_ambiguity_protocol_tests.py` and `candidates/ALG-0022-prefix-block-ambiguity-set-protocol.md`; no commit recorded
Candidate IDs: ALG-0021, ALG-0022, with ALG-0015 and ALG-0020 as policy comparators
Logs/datasets: `scripts/alg0015_noise_incomplete_tests.py` cases, including targeted prefix-merge ambiguity, rare-reversal noise, valid-rare-parallel, incomplete one-order parallel, and balanced reversal controls
Metrics: ambiguity detection, selected policy, per-alternative held-out replay, per-alternative negative-trace rejection, per-alternative compile operation counts, total operations including `ALG-0021` discovery
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; totals include the `ALG-0021` discovery count plus extra bounded block-net construction for each alternative

Targeted alternative results:

| Case | Selected policy / selected held-out / selected neg reject | Alternative | Held-out replay | Negative rejection | Total ops including discovery |
|---|---:|---|---:|---:|---:|
| `prefix_merge_full_parallel_interpretation` | `full_parallel_generalization` / 4/4 / 3/3 | `sequence_prefix_precision` | 0/4 | 3/3 | 385 |
| `prefix_merge_full_parallel_interpretation` | `full_parallel_generalization` / 4/4 / 3/3 | `full_parallel_generalization` | 4/4 | 3/3 | 388 |
| `prefix_merge_sequence_then_parallel_interpretation` | `full_parallel_generalization` / 0/0 / 0/4 | `sequence_prefix_precision` | 0/0 | 4/4 | 385 |
| `prefix_merge_sequence_then_parallel_interpretation` | `full_parallel_generalization` / 0/0 / 0/4 | `full_parallel_generalization` | 0/0 | 0/4 | 388 |

Controls:

- No alternatives are emitted for `noise_reversal_2_to_1`, `noise_reversal_3_to_1`, `noise_reversal_5_to_1`, `valid_rare_parallel_3_to_1`, `incomplete_parallel_one_order_2`, or `balanced_reversal_tie`.
- The selected policy can be `sequence_prefix_precision` on non-ambiguous common-boundary parallel detections, but this is not an ambiguity-set decision unless `ambiguity.detected=true`.

Interpretation:

- The protocol makes the ambiguity actionable for evaluation: one alternative preserves full-parallel held-out recovery, while the other preserves sequence-prefix negative rejection.
- The event log alone still does not identify which alternative is correct. The protocol is therefore a model-set output, not a solved selector.
- Per-alternative compile overhead is small on the targeted toy cases, but it is additive and should be budgeted if ambiguity sets grow.

Failures / anomalies:

- The prototype imports the prefix-block compiler directly, so it is a research protocol rather than a stable public API.
- No deterministic selector, validation-set rule, or domain-prior mechanism exists yet.
- It does not address noise-versus-rare-valid ambiguity, loop behavior, duplicate labels, or optional/concurrency.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0022` as a smoke-tested multi-net PMIR protocol; do not promote it.
- Keep `ALG-0021` smoke-tested and `ALG-0015` deep-testing.
- Do not create a property dossier.

Next action: either add a deterministic ambiguity selector with explicit priors/validation evidence, or pivot to bounded loop support as the next independent candidate line.

## EXP-0022 — ALG-0023 bounded single-rework loop cut

Date/time: 2026-05-07T10:42:00+02:00
Goal: pivot from ambiguity handling to bounded loop support by adding a narrow process-tree loop cut for the repeated-anchor short-loop counterexample
Command(s):

- `python3 -B -m compileall scripts`
- `python3 -c '...'` diagnostic replay/precision check for `cut_limited_loop_repair` on `examples/logs/short_loop.json`
- `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `enable_short_loop` to `scripts/cut_limited_process_tree.py`, adding `scripts/cut_limited_loop_repair.py`, wiring the new candidate into smoke/deep/optional/stress runners, adding `scripts/alg0023_loop_tests.py`, and creating `candidates/ALG-0023-cut-limited-single-rework-loop-miner.md`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0015, ALG-0016, ALG-0023
Logs/datasets: toy logs in `examples/logs/*.json`; targeted loop cases in `scripts/alg0023_loop_tests.py`; broader synthetic cases in `scripts/alg0009_deep_tests.py`; optional-pattern and ALG-0005 stress suites as collateral checks
Metrics: selected cut, operation counts, training replay, held-out replay, negative-trace rejection, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0023` adds singleton rework-loop detection and duplicate-labeled loop-net construction to the `ALG-0003` process-tree path

Targeted loop results:

| Case | ALG-0023 selected cut | ALG-0023 replay / held-out / neg reject / ops | Key comparator result |
|---|---|---:|---|
| `single_rework_zero_or_one` | `single_rework_loop` | 3/3 / 1/1 / 3/3 / 216 | `ALG-0003` replays 0/3 train and 0/1 held-out; `ALG-0005` replays 3/3 train but 0/1 held-out. |
| `single_rework_one_iteration_only` | `fallback_dfg` | 0/2 / 0/1 / 3/3 / 212 | Loop cut correctly refuses because zero-iteration exit was not observed, but fallback replay remains poor. |
| `optional_skip_not_loop` | `optional_sequence` | 3/3 / 0/0 / 3/3 / 207 | Optional skip remains optional sequence, not loop. |
| `different_rework_body_rejected` | `fallback_dfg` | 0/3 / 0/1 / 3/3 / 286 | Multi-body rework is outside the singleton-loop scope. |

Toy smoke results for `ALG-0023`:

| Log | Selected cut | Ops | Replay | Negative rejection |
|---|---|---:|---:|---:|
| `noise.json` | `parallel` | 261 | 4/4 | 3/3 |
| `parallel_ab_cd.json` | `parallel` | 243 | 4/4 | 3/3 |
| `sequence.json` | `sequence` | 168 | 3/3 | 3/3 |
| `short_loop.json` | `single_rework_loop` | 216 | 3/3 | 3/3 |
| `skip.json` | `optional_sequence` | 240 | 4/4 | 3/3 |
| `xor.json` | `xor` | 194 | 4/4 | 3/3 |

Broader synthetic results for `ALG-0023`:

| Synthetic case | Selected cut | Ops | Replay | Negative rejection |
|---|---|---:|---:|---:|
| `nested_xor_sequence` | `xor` | 255 | 3/3 | 3/3 |
| `overlapping_optional_skips` | `optional_sequence` | 337 | 4/4 | 3/3 |
| `parallel_with_optional_branch` | `parallel_optional_sequence` | 373 | 3/3 | 3/3 |
| `short_loop_required` | `single_rework_loop` | 216 | 3/3 | 3/3 |
| `duplicate_label_rework` | `single_rework_loop` | 204 | 3/3 | 3/3 |
| `incomplete_parallel_observed_sequence` | `sequence` | 155 | 2/2 | 3/3 |
| `noise_reversal_sequence` | `parallel` | 261 | 4/4 | 3/3 |

Interpretation:

- `ALG-0023` repairs the key non-automaton short-loop failure: `short_loop.json` improves from `ALG-0003` 0/3 replay to 3/3 while keeping 3/3 negative rejection.
- It also gives a true grammar-style advantage over exact prefix automata: on `single_rework_zero_or_one`, it replays the held-out second loop iteration 1/1, while `ALG-0005` and `ALG-0015` exact-fallback variants replay 0/1.
- The duplicate-label rework synthetic case is the same repeated-anchor loop shape, so the loop cut repairs it too.
- The detector is conservative: it does not fire on optional skips, one-iteration-only evidence, or two distinct rework bodies.

Failures / anomalies:

- One-iteration-only logs still fall back to `ALG-0003` DFG behavior and replay 0/2 observed positives. This is an explicit scope gap.
- Multi-body loops are rejected rather than modeled.
- The emitted net permits repeated loop iterations once zero and one iteration are observed; this may overgeneralize processes where exactly one rework is possible.
- Optional-singleton-parallel remains an `ALG-0003` family weakness: `ALG-0023` still replays 0/4 there because the loop cut is orthogonal.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0023` and promote it to `promising`: it has a written spec, deterministic prototype, measured counts, targeted smoke/deep success, clean negative probes, and a concrete held-out loop-generalization advantage over `ALG-0003` and exact automata.
- Do not move it to `deep-testing` or `super-promising`; loop scope is too narrow and one-iteration-only / multi-body behavior is unresolved.
- Keep `ALG-0003` at `deep-testing` as the baseline process-tree candidate with loop repair split out.
- Do not create a property dossier.

Next action: stress `ALG-0023` on multi-body loops, bounded-count loops, and nested loop-with-choice cases, or add a deterministic ambiguity selector for the `ALG-0021`/`ALG-0022` line.

## EXP-0023 — ALG-0023 loop-boundary stress tests

Date/time: 2026-05-07T11:06:00+02:00
Goal: stress `ALG-0023` on bounded-count, prefix/suffix context, multi-body loop, nested loop-with-choice, and one-iteration-only evidence cases before any deeper promotion
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/alg0023_loop_stress_tests.py`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0015, ALG-0016, ALG-0023
Logs/datasets: targeted loop-boundary cases in `scripts/alg0023_loop_stress_tests.py`
Metrics: selected cut, operation counts, training replay, held-out replay, negative-trace rejection, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; no discovery-code changes beyond the EXP-0022 `ALG-0023` loop detector

Stress results for `ALG-0023`:

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `bounded_at_most_one_rework` | `single_rework_loop` | 3/3 | 0/0 | 2/3 | 204 | Accepts a second iteration negative, so bounded-count domains need an explicit prior or different candidate. |
| `prefixed_suffixed_single_rework` | `single_rework_loop` | 3/3 | 1/1 | 3/3 | 368 | Prefix/suffix context works and still generalizes the loop. |
| `multi_body_loop_choice` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 286 | Multi-body loop choice remains outside scope. |
| `nested_loop_with_choice_context` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 381 | Nested choice in a loop body remains outside scope. |
| `one_iteration_only_with_clean_dfg_path` | `fallback_dfg` | 0/3 | 0/2 | 3/3 | 282 | Requiring zero-iteration evidence prevents unsupported loop inference, but fallback replay remains poor. |

Comparator notes:

- Exact automaton and prefix-block exact-fallback comparators replay the observed multi-body and one-iteration-only training logs, but reject held-out loop iterations. They remain memorization comparators, not loop generalizers.
- `ALG-0003` fallback rejects all loop-stress training cases except non-loop optional/sequence-style cases from earlier tests.
- `ALG-0016` grammar-only still rejects loop cases entirely.

Interpretation:

- EXP-0023 confirms `ALG-0023` is a useful unbounded singleton-loop candidate, not a general loop miner.
- The key new counterexample is `bounded_at_most_one_rework`: the same zero/one evidence that supports loop generalization also overgeneralizes if domain semantics cap the loop at one rework.
- Prefix and suffix sequence context do not break the detector.
- Multi-body and nested-choice loop evidence should become a separate candidate if pursued; forcing it into `ALG-0023` would broaden the current hypothesis too much.

Failures / anomalies:

- No deterministic way exists yet to choose unbounded-loop versus bounded-at-one semantics from the same zero/one evidence.
- One-iteration-only evidence is intentionally rejected, but this leaves observed replay poor under the process-tree fallback.
- No property dossier was created because the candidate is not `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Keep `ALG-0023` at `promising`; do not move it to `deep-testing`.
- Do not retire it: prefix/suffix loop context and held-out unbounded-loop replay remain useful evidence.
- Do not create a property dossier.

Next action: either split a bounded-count loop candidate, split a multi-body loop-choice candidate, or return to the ambiguity-selector line for `ALG-0021`/`ALG-0022`.

## EXP-0024 — ALG-0024 multi-body rework-loop choice

Date/time: 2026-05-07T10:26:46+02:00
Goal: split the unresolved multi-body loop-choice case from `ALG-0023` into a narrow process-tree candidate while keeping bounded-count semantics as an explicit prior/ambiguity
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`
- `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`
- `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `enable_multi_body_loop` and `multi_body_rework_loop` detection/compilation to `scripts/cut_limited_process_tree.py`, adding `scripts/cut_limited_multi_body_loop.py`, adding `scripts/alg0024_multibody_loop_tests.py`, wiring `ALG-0024` into standard runners, and creating `candidates/ALG-0024-cut-limited-multi-body-rework-loop-miner.md`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0015, ALG-0016, ALG-0023, ALG-0024
Logs/datasets: targeted multi-body loop cases in `scripts/alg0024_multibody_loop_tests.py`; existing loop tests and loop-stress cases; toy logs in `examples/logs/*.json`; broader synthetic, optional-pattern, and prefix-automaton stress suites as collateral checks
Metrics: selected cut, loop-policy evidence, body support, operation counts, training replay, held-out replay, negative-trace rejection, structural diagnostics
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0024` adds multi-body candidate scans, body-support `dict_increment`s, and body-choice loop construction before falling through to the `ALG-0023` singleton-loop detector

Subagent findings merged:

- Candidate scout recommended multi-body loop choice as the evidence-driven next split. Rationale: bounded-at-most-one and unbounded-repeat semantics are not identifiable from the same zero/one evidence without a prior.
- Implementation scout noted a bounded-at-most-one compiler would be smaller, but also flagged that it would be a policy candidate rather than an evidence-discovered improvement.
- Evaluator scout supplied the minimal multi-body, bounded-count, one-iteration-only, and nested-context stress cases.
- Property-study scout identified later obligations for loop soundness, duplicate-label conversion correctness, determinism, and operation-budget tightness; no dossier was started because no candidate is `super-promising`.

Targeted `ALG-0024` results:

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops |
|---|---|---:|---:|---:|---:|
| `loop_unbounded_control` | `single_rework_loop` | 3/3 | 1/1 | 3/3 | 270 |
| `bounded_at_most_one_rework` | `single_rework_loop` | 3/3 | 0/0 | 2/3 | 270 |
| `multi_body_loop_choice` | `multi_body_rework_loop` | 3/3 | 2/2 | 3/3 | 258 |
| `nested_choice_loop_context` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 349 |
| `one_iteration_only` | `fallback_dfg` | 0/3 | 0/2 | 3/3 | 415 |

Comparator notes:

- On `multi_body_loop_choice`, `ALG-0023` replays 0/3 train and 0/2 held-out traces, while `ALG-0024` replays 3/3 train and 2/2 held-out traces with 3/3 negative rejection.
- On `nested_choice_loop_context`, `ALG-0023` replays 0/3 train and 0/1 held-out traces, while `ALG-0024` replays 3/3 train and 1/1 held-out traces with 3/3 negative rejection.
- Exact automaton and prefix-block exact-fallback comparators replay observed multi-body training traces but reject held-out body combinations, so `ALG-0024` has a real loop-generalization advantage on the targeted cases.
- `ALG-0016` grammar-only rejects these loop cases, confirming the fix comes from the loop candidate rather than a prefix-block grammar.

Standard-suite deltas:

- `short_loop.json`: `ALG-0024` selects `single_rework_loop`, 292 ops, 3/3 replay, 3/3 negative rejection. This preserves `ALG-0023` behavior with extra rejected multi-body-detector overhead.
- `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `skip.json`, and `noise.json`: `ALG-0024` matches `ALG-0023` replay and negative-rejection behavior.
- Existing optional-pattern and prefix-automaton stress suites show no quality regression; operation counts rise only where the extra detector runs before an existing cut or fallback.

Interpretation:

- `ALG-0024` converts the previous `different_rework_body_rejected` / multi-body loop case from an unresolved failure into a deliberately scoped loop-choice candidate.
- The emitted net models `prefix anchor (body_1 anchor | ... | body_k anchor)* suffix`, where each body is currently a singleton activity.
- The unbounded-repeat prior remains explicit through `loop_repetition_policy=unbounded_repeat` and `bounded_count_ambiguous=true`.
- The candidate is not a bounded-count loop miner and not a general recursive loop miner.

Failures / anomalies:

- Bounded-at-most-one domains still fail precision: the second loop iteration negative is accepted, so negative rejection remains 2/3.
- One-iteration-only evidence still falls back to DFG behavior and replays 0/3 observed positives.
- Only singleton body alternatives are supported; longer body sequences and duplicate labels inside body alternatives are untested.
- Extra detector overhead is visible on singleton-loop cases (`short_loop.json` 292 ops versus `ALG-0023` 216).
- No property dossier was created because the candidate is not `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0024` and promote it to `promising`: it has a written spec, deterministic prototype, measured operation counts, targeted smoke/deep success, clean negative probes, and a concrete held-out loop-generalization advantage over `ALG-0023` and exact automata.
- Do not move it to `deep-testing` or `super-promising`; bounded-count priors, one-iteration-only logs, longer body sequences, duplicate-label body contexts, and trace-order stability are unresolved.
- Keep `ALG-0023` as the singleton-loop reference candidate.
- Do not create a property dossier.

Next action: stress `ALG-0024` on longer body sequences, duplicate-label body contexts, trace-order stability, and explicit bounded-count prior/model-set variants, or return to the `ALG-0021`/`ALG-0022` ambiguity-selector line.

## EXP-0025 — ALG-0024 boundary stress and stability tests

Date/time: 2026-05-07T10:41:56+02:00
Goal: stress `ALG-0024` before any deeper promotion on longer body sequences, duplicate-label contexts, bounded-count priors, support imbalance, and trace-order stability
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0024_stress_tests.py --out experiments/alg0024-stress-tests.json`
- `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`
- `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/alg0024_stress_tests.py`; no discovery-code changes after EXP-0024; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0015, ALG-0016, ALG-0023, ALG-0024
Logs/datasets: targeted boundary cases and permutation stability cases in `scripts/alg0024_stress_tests.py`; refreshed EXP-0024 targeted suite and ALG-0023 loop-stress suite as collateral checks
Metrics: selected cut, loop-policy evidence, body support, operation counts, training replay, held-out replay, negative-trace rejection, structural diagnostics, and selected-cut stability across trace-order permutations
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; no new primitives added

Stress results for `ALG-0024`:

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `longer_body_choice_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 438 | Length-2 body alternatives remain outside scope. |
| `mixed_singleton_and_sequence_body_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 387 | Mixed body widths are rejected rather than coerced into singleton choices. |
| `duplicate_label_in_suffix_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 388 | Duplicate body/suffix labels remain outside the current compiler scope. |
| `bounded_count_multi_body_prior` | `multi_body_rework_loop` | 3/3 | 0/0 | 2/4 | 258 | Repeated body combinations are accepted under the unbounded prior, so bounded-count domains remain ambiguous. |
| `support_imbalance_body_choice` | `multi_body_rework_loop` | 5/5 | 1/1 | 3/3 | 332 | Low-support body alternatives are treated as valid observed choices, not noise. |

Trace-order stability:

| Case | Stable | Unique permutations |
|---|---:|---:|
| `multi_body_loop_choice_order_stability` | yes | 6 |
| `nested_choice_loop_context_order_stability` | yes | 6 |
| `support_imbalance_body_choice_order_stability` | yes | 12 |

Comparator notes:

- Exact automaton and prefix-block exact-fallback comparators replay observed longer-body and duplicate-label-context training traces, but reject held-out repeated combinations. They remain memorization comparators.
- `ALG-0024` intentionally refuses length-2 and duplicate-label loop candidates, which preserves a narrow hypothesis but leaves observed replay at 0/3 under the process-tree fallback.
- In the support-imbalance case, `ALG-0024` records body support (`B=3`, `C=1`) but still compiles both bodies; this is a useful next support/noise policy question rather than a promotion point.

Interpretation:

- EXP-0025 gives positive evidence for deterministic selection: the emitted `multi_body_rework_loop` signature is stable under checked trace-order permutations.
- The same experiment gives negative evidence against deeper promotion: the candidate remains singleton-body-only, duplicate-label-conservative, and unbounded-repeat by prior.
- Bounded-count semantics are still a model-set or domain-prior problem, not something the current event-log evidence identifies.

Failures / anomalies:

- Length-2 body choices and mixed-width body choices are not modeled.
- Duplicate labels shared between body and suffix are rejected.
- Bounded-count multi-body semantics fail precision because repeated body combinations are accepted.
- There is no support threshold for treating a rare loop body as noise.
- No property dossier was created because the candidate is not `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Keep `ALG-0024` at `promising`; do not move it to `deep-testing`.
- Do not retire it: targeted multi-body held-out generalization and trace-order stability remain useful.
- Do not create a property dossier.

Next action: either split a length-2 body loop candidate, split a bounded-count policy-set candidate for loops, or add a support/noise guard for rare loop-body alternatives.

## EXP-0026 - ALG-0025 length-bounded rework-loop bodies

Date/time: 2026-05-07T11:01:51+02:00
Goal: split the length-2 body-loop gap from `ALG-0024` into a bounded process-tree candidate while preserving the explicit unbounded-repeat prior
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`
- `python3 scripts/alg0024_stress_tests.py --out experiments/alg0024-stress-tests.json`
- `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`
- `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`
- `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`
- `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`
- `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`
- `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`
- `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after parameterizing `_detect_multi_body_rework_loop` with `multi_body_loop_max_body_length`, adding `scripts/cut_limited_length_bounded_loop.py`, adding `scripts/alg0025_length_bounded_loop_tests.py`, wiring `ALG-0025` into affected runners, and creating `candidates/ALG-0025-cut-limited-length-bounded-rework-loop-miner.md`; no commit recorded
Candidate IDs: ALG-0003, ALG-0005, ALG-0015, ALG-0016, ALG-0023, ALG-0024, ALG-0025 plus collateral smoke/deep-suite candidates already present in the runners
Logs/datasets: targeted length-bounded loop cases and stability cases in `scripts/alg0025_length_bounded_loop_tests.py`; refreshed loop suites; toy logs in `examples/logs/*.json`; broader synthetic, optional-pattern, and prefix-automaton stress suites as collateral checks
Metrics: selected cut, loop-policy evidence, `max_body_length`, body support, operation counts, training replay, held-out replay, negative-trace rejection, structural diagnostics, and selected-signature stability across trace-order permutations
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; `ALG-0025` adds body-length-bounded validation and sequence-body construction for fixed `M=2`

Targeted `ALG-0025` results:

| Case | Selected cut | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---|---:|---:|---:|---:|---|
| `length2_body_choice` | `multi_body_rework_loop` | 3/3 | 2/2 | 3/3 | 401 | Fixes the length-2 body-choice gap from EXP-0025. |
| `mixed_singleton_and_length2_body` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 322 | Supports mixed singleton and length-2 loop bodies. |
| `singleton_body_regression` | `multi_body_rework_loop` | 3/3 | 1/1 | 3/3 | 258 | Preserves `ALG-0024` singleton-body behavior and counts. |
| `length3_body_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 641 | Body length greater than two remains outside scope. |
| `overlapping_body_labels_rejected` | `fallback_dfg` | 0/3 | 0/1 | 3/3 | 436 | Shared body labels remain rejected. |
| `bounded_count_length2_prior` | `multi_body_rework_loop` | 3/3 | 0/0 | 2/4 | 401 | Repeated body combinations are accepted under the unbounded prior. |

Trace-order stability:

| Case | Stable | Unique permutations |
|---|---:|---:|
| `length2_body_choice_order_stability` | yes | 6 |
| `mixed_singleton_and_length2_body_order_stability` | yes | 6 |

Comparator notes:

- On `length2_body_choice`, `ALG-0024` falls back with 0/3 train replay and 0/2 held-out replay, while `ALG-0025` replays 3/3 train and 2/2 held-out traces with 3/3 negative rejection.
- On `mixed_singleton_and_length2_body`, `ALG-0024` falls back with 0/3 train replay and 0/1 held-out replay, while `ALG-0025` replays 3/3 train and 1/1 held-out trace with 3/3 negative rejection.
- Exact automaton and prefix-block exact-fallback comparators replay observed length-2 training traces but reject held-out repeated combinations, so `ALG-0025` has a real loop-generalization advantage on the targeted cases.
- `ALG-0025` preserves `ALG-0024` behavior on singleton multi-body, nested-context, and support-imbalance loop-choice cases.

Standard-suite deltas:

- `short_loop.json`: `ALG-0025` selects `single_rework_loop`, 292 ops, 3/3 replay, and 3/3 negative rejection, matching `ALG-0024`.
- `sequence.json`, `xor.json`, `parallel_ab_cd.json`, `skip.json`, and `noise.json`: `ALG-0025` matches the current cut-limited loop line's replay and negative-rejection behavior.
- Optional-pattern and prefix-automaton stress suites show no quality regression from adding `ALG-0025`; operation counts rise where the extra detector runs before an existing cut or fallback.

Interpretation:

- EXP-0026 turns the length-2 loop-body counterexample from EXP-0025 into a deliberately scoped candidate instead of broadening `ALG-0024`.
- The emitted language is `prefix anchor (body_1 anchor | ... | body_k anchor)* suffix` with `1 <= |body_i| <= 2`.
- The unbounded-repeat prior remains explicit through `loop_repetition_policy=unbounded_repeat` and `bounded_count_ambiguous=true`.
- Body-length bound `M=2` is a policy/cost choice, not a learned proof that longer bodies are invalid.

Failures / anomalies:

- Bounded-count domains still fail precision: repeated body combinations are accepted, so the bounded-count length-2 prior rejects only 2/4 negatives.
- Length >2 body alternatives and overlapping body-label alternatives are rejected; observed training replay is poor under fallback for those cases.
- One-iteration-only loop evidence remains outside scope.
- No support threshold exists for treating a rare loop body as noise.
- No property dossier was created because the candidate is not `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0025` and promote it to `promising`: it has a written spec, deterministic prototype, measured operation counts, targeted length-2/mixed-width success, checked trace-order stability, and a concrete held-out loop-generalization advantage over `ALG-0024` and exact automata.
- Do not move it to `deep-testing` or `super-promising`; bounded-count priors, length >2 scaling, duplicate-label contexts, one-iteration-only evidence, and rare-body/noise policy remain unresolved.
- Keep `ALG-0024` as the singleton-body reference candidate.
- Do not create a property dossier.

Next action: split a bounded-count loop policy-set candidate or support/noise guard for rare loop bodies before increasing the body-length bound further.

## EXP-0027 - ALG-0026 bounded loop-count policy-set protocol

Date/time: 2026-05-07T11:11:25+02:00
Goal: preserve bounded-count loop ambiguity by compiling both unbounded-repeat and at-most-once policy alternatives from the same `ALG-0025` loop evidence
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0026_loop_policy_tests.py --out experiments/alg0026-loop-policy-tests.json`
- `python3 -B -m compileall scripts`
- `python3 scripts/alg0026_loop_policy_tests.py --out experiments/alg0026-loop-policy-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/loop_policy_set_protocol.py`, adding `scripts/alg0026_loop_policy_tests.py`, and creating `candidates/ALG-0026-loop-count-policy-set-protocol.md`; no commit recorded
Candidate IDs: ALG-0023, ALG-0024, ALG-0025, ALG-0026
Logs/datasets: targeted bounded-count policy cases in `scripts/alg0026_loop_policy_tests.py`
Metrics: policy alternatives emitted, selected policy, train replay, held-out replay, negative-trace rejection, structural diagnostics, compile operation counts, and total-with-discovery operation counts per policy
Operation-count model: first-iteration model in `research/ALGORITHM_REGISTRY.md`; upstream `ALG-0025` discovery count is reused and the at-most-once alternative adds counted construction operations only

Subagent findings merged:

- Candidate scout recommended `ALG-0026` as a multi-net policy-set protocol rather than a selected-net bounded-at-most-one candidate, because the same zero/one evidence cannot identify bounded versus unbounded loop semantics.
- Evaluator scout supplied the discriminator pattern: both alternatives should replay training traces; unbounded should accept repeated-iteration held-out probes; at-most-once should reject repeated-iteration bounded-count negatives; controls should emit no alternatives.
- Implementation scout recommended reusing existing loop PMIR evidence, keeping selected-net behavior compatible, and compiling the at-most-once alternative without changing detector order or `pn_ir.py`.

Targeted `ALG-0026` results:

| Case | Policy set | Unbounded train / held-out / neg | At-most-once train / held-out / neg | At-most-once ops | Interpretation |
|---|---:|---:|---:|---:|---|
| `single_rework_unbounded_policy` | yes | 2/2 / 1/1 / 3/3 | 2/2 / 0/1 / 3/3 | 216 | Unbounded wins on second-iteration held-out. |
| `single_rework_bounded_policy` | yes | 2/2 / 0/0 / 2/3 | 2/2 / 0/0 / 3/3 | 216 | At-most-once wins on bounded-count negatives. |
| `multi_body_unbounded_policy` | yes | 3/3 / 2/2 / 3/3 | 3/3 / 0/2 / 3/3 | 283 | Unbounded wins on repeated body combinations. |
| `contexted_multi_body_policy` | yes | 3/3 / 2/2 / 4/4 | 3/3 / 0/2 / 4/4 | 378 | Prefix/suffix context preserves the policy split. |
| `multi_body_bounded_policy` | yes | 3/3 / 0/0 / 2/4 | 3/3 / 0/0 / 4/4 | 283 | At-most-once rejects repeated body-combination negatives. |
| `length2_unbounded_policy` | yes | 3/3 / 2/2 / 3/3 | 3/3 / 0/2 / 3/3 | 434 | Length-2 body alternatives preserve the split. |
| `length2_bounded_policy` | yes | 3/3 / 0/0 / 2/4 | 3/3 / 0/0 / 4/4 | 434 | At-most-once fixes length-2 bounded-count precision. |
| `mixed_width_policy` | yes | 3/3 / 2/2 / 4/4 | 3/3 / 0/2 / 4/4 | 351 | Mixed singleton and length-2 bodies preserve the split. |
| `one_iteration_only_no_policy_set` | no | selected fallback 0/1 held-out / 3/3 neg | n/a | n/a | No zero-iteration loop evidence, so no policy set. |
| `optional_skip_no_policy_set` | no | selected optional cut 1/1 held-out / 3/3 neg | n/a | n/a | Optional skip is not a loop-count ambiguity. |

Interpretation:

- `ALG-0026` cleanly brackets the ambiguity seen in EXP-0023 through EXP-0026: unbounded alternatives recover repeated-iteration held-out behavior, while at-most-once alternatives reject repeated-iteration negatives.
- Both alternatives replay all zero/one-iteration training traces in all emitted policy-set cases.
- The controls correctly emit no policy alternatives when upstream loop evidence is absent.
- The selected net remains unbounded-repeat only for single-net benchmark compatibility. This is not an identifiability claim.

Failures / anomalies:

- No final selector exists. The protocol reports a model set, not a chosen process model.
- One-iteration-only evidence remains unresolved because upstream loop detection does not emit bounded-count ambiguity evidence.
- The at-most-once compiler inherits upstream restrictions on duplicate labels and body length.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0026` as `smoke-tested`: it is deterministic, emits policy alternatives only for bounded-count ambiguous loop evidence, records per-policy operation counts and replay/negative metrics, and demonstrates the policy-set bracketing behavior.
- Do not promote it to `promising` yet because it has no deterministic selector, validation rule, or domain-prior mechanism.
- Do not create a property dossier.

Next action: add a selector/validation policy for loop-count model sets, or move to rare-body support/noise guards for `ALG-0024`/`ALG-0025`.

## EXP-0028 - ALG-0027 loop-count validation selector

Date/time: 2026-05-07T11:16:17+02:00
Goal: add a deterministic selector for `ALG-0026` loop-count policy sets that chooses a final policy only when explicit validation positives/negatives distinguish the alternatives
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`
- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`
- `python3 -B -m compileall scripts`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/loop_count_validation_selector.py`, adding `scripts/alg0027_loop_selector_tests.py`, and creating `candidates/ALG-0027-loop-count-validation-selector.md`; no commit recorded
Candidate IDs: ALG-0026, ALG-0027
Logs/datasets: targeted validation selector cases in `scripts/alg0027_loop_selector_tests.py`
Metrics: selected policy, selection status, reason, validation-positive replay, validation-negative rejection, selector primitive operation counts, total-with-selector count, and per-policy validation scores
Operation-count model: first-iteration primitive model for selector comparisons/arithmetic/evidence construction; validation replay is reported as selector evidence and not yet folded into discovery primitive counts

Subagent findings merged:

- Skeptical evaluator scout required explicit validation evidence, no default selection on training evidence alone, unresolved output for non-discriminating validation, and separate handling of no-policy-set and inconsistent validation controls.

Targeted `ALG-0027` results:

| Case | Expected | Selected | Status | Validation positives | Validation negatives | Selector ops |
|---|---|---|---|---:|---:|---:|
| `single_rework_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 1/1 | 3/3 | 21 |
| `single_rework_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 3/3 | 20 |
| `multi_body_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 3/3 | 22 |
| `multi_body_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 4/4 | 21 |
| `length2_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 3/3 | 22 |
| `length2_selects_at_most_once` | `at_most_once` | `at_most_once` | `selected` | 0/0 | 4/4 | 21 |
| `mixed_width_selects_unbounded` | `unbounded_repeat` | `unbounded_repeat` | `selected` | 2/2 | 4/4 | 23 |
| `no_discriminator_unresolved` | none | none | `unresolved` | 2/2 | 2/2 | 21 |
| `conflicting_validation_unresolved` | none | none | `validation_inconsistent` | 1/1 | 0/1 | 19 |
| `optional_skip_no_policy_set` | none | none | `no_policy_set` | 1/1 | 3/3 | 4 |

Interpretation:

- `ALG-0027` selects `unbounded_repeat` when validation positives include repeated loop iterations and validation negatives contain only structural invalid traces.
- `ALG-0027` selects `at_most_once` when validation negatives mark repeated loop iterations as invalid and no validation positive requires repetition.
- Non-discriminating validation leaves selection unresolved rather than defaulting to a policy.
- Contradictory validation, where the same trace is both positive and negative, is detected explicitly.
- Optional-skip controls emit `no_policy_set`, so the selector does not invent loop-count choices without upstream ambiguity evidence.

Failures / anomalies:

- Validation and final-test evidence are not yet separated in a broader evaluation protocol, so this is not a promotion-quality selector.
- Validation replay cost is reported but not fully integrated into the primitive discovery-operation model.
- The selector inherits upstream `ALG-0026` limitations: no policy set for one-iteration-only evidence, duplicate-label restrictions, and body-length restrictions.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0027` as `smoke-tested`: it deterministically selects either loop-count policy when validation probes uniquely identify one, and it correctly leaves ties, conflicts, and no-policy-set cases unresolved.
- Do not promote it to `promising` yet because validation/final-test separation and validation replay cost need a clearer protocol.
- Do not create a property dossier.

Next action: either define a broader validation protocol for `ALG-0027` with held-out final tests, or shift to rare-body support/noise guards for `ALG-0024`/`ALG-0025`.

## EXP-0029 - ALG-0027 split validation/final-test protocol

Date/time: 2026-05-07T11:23:50+02:00
Goal: test `ALG-0027` under frozen train/validation/final splits and add explicit validation replay proxy counts
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`
- `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`
- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`
- `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding validation replay proxy counts to `scripts/loop_count_validation_selector.py` and adding `scripts/alg0027_validation_protocol_tests.py`; no commit recorded
Candidate IDs: ALG-0026, ALG-0027
Logs/datasets: targeted train/validation/final loop-count protocol cases in `scripts/alg0027_validation_protocol_tests.py`
Metrics: selected policy, selection status, train/validation/final leakage flags, final-positive replay, final-negative rejection, selector operation counts, validation replay proxy counts, per-policy final evaluations, and protocol pass/fail flags
Operation-count model: first-iteration primitive model plus an explicit validation replay proxy: for each policy alternative and validation trace, count one `scan_event` per event and one `comparison` per trace outcome; final replay remains evaluation-only and is not counted as discovery/selection work

Subagent findings merged:

- Evaluator/counterexample scout recommended frozen `train`, `validation`, and `final` partitions, with final probes unused until the selector output is frozen.
- Leakage should include reused final probes in validation, validation edits after seeing final failures, or final metrics influencing policy choice.
- Promotion is reasonable if split cases pass and validation replay cost is reported, but `deep-testing` should wait for one-iteration-only, duplicate-label, length >2, and noisy rare-body limits.

Targeted `ALG-0027` protocol results:

| Case | Expected | Selected | Status | Leakage | Final positives | Final negatives | Selector ops | Validation replay proxy ops |
|---|---|---|---|---:|---:|---:|---:|---:|
| `single_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 1/1 | 2/2 | 20 | 30 |
| `single_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 22 |
| `multi_body_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 2/2 | 2/2 | 20 | 30 |
| `multi_body_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 22 |
| `length2_unbounded_final_generalization` | `unbounded_repeat` | `unbounded_repeat` | `selected` | no | 1/1 | 2/2 | 20 | 36 |
| `mixed_width_bounded_final_precision` | `at_most_once` | `at_most_once` | `selected` | no | 0/0 | 2/2 | 19 | 24 |
| `no_discriminator_remains_unresolved` | none | none | `unresolved` | no | 1/1 | 1/1 | 19 | 16 |
| `optional_skip_no_policy_set_final_control` | none | none | `no_policy_set` | no | 0/0 | 1/1 | 2 | 0 |
| `leakage_guard_reports_validation_final_overlap` | `unbounded_repeat` | `unbounded_repeat` | `selected` | yes | 1/1 | 1/1 | 19 | 22 |

Interpretation:

- Split validation/final tests support the `ALG-0027` selector under its declared external-validation assumption.
- The selector generalizes beyond validation positives on unbounded cases: singleton third iteration, unseen multi-body repetitions, and reversed length-2 body repetitions replay in final probes.
- The selector preserves bounded precision when validation negatives declare repetition invalid: final repeated singleton, multi-body, and mixed-width traces are rejected by the selected at-most-once net.
- The non-discriminating case remains unresolved even though final probes contain a repeated-loop positive; this confirms final probes are not used for selection.
- The optional-skip control remains `no_policy_set`.
- The leakage guard detects validation/final overlap and records it as protocol leakage rather than treating the final result as promotion-quality evidence.
- Validation replay proxy counts are now reported separately from selector-scoring counts and folded into `operation_counts.total_with_selector_and_validation_proxy`.

Failures / anomalies:

- The validation replay proxy is still a lower-bound accounting model; it does not count all token-game marking and silent-closure work.
- At-most-once final-positive probes are empty in bounded cases because the valid zero/one loop traces are already in the training log; broader protocols need independent positive variants with richer context.
- One-iteration-only evidence still emits no policy set upstream.
- Duplicate-label, length >2, and noisy rare-body loop evidence remain untested under the selector protocol.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Promote `ALG-0027` from `smoke-tested` to `promising`: it has a written specification, deterministic prototype, relevant smoke/protocol tests, measured selector and validation replay proxy counts, a concrete advantage over `ALG-0026` model-set output when external validation exists, and unresolved behavior when evidence does not identify a policy.
- Do not move `ALG-0027` to `deep-testing`; the next tests should stress upstream limits and refine validation replay cost accounting.
- Do not create a property dossier.

Next action: stress `ALG-0027` with one-iteration-only controls, duplicate-label and length >2 blocked cases, and rare-body/noise support policies; alternatively split a rare-body support/noise guard candidate for `ALG-0024`/`ALG-0025`.

## EXP-0030 - ALG-0027 upstream-limit stress

Date/time: 2026-05-07T11:28:55+02:00
Goal: test whether `ALG-0027` stays within its selector scope on upstream loop-evidence limits and rare-body/noise ambiguity
Command(s):

- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_upstream_limit_tests.py --out experiments/alg0027-upstream-limit-tests.json`
- `python3 -B -m compileall scripts`
- `python3 scripts/alg0027_upstream_limit_tests.py --out experiments/alg0027-upstream-limit-tests.json`
- `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`
- `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`
- `python3 -B -m unittest`
- `git diff --check`

Code version / commit if available: working tree after adding `scripts/alg0027_upstream_limit_tests.py` and updating `candidates/ALG-0027-loop-count-validation-selector.md`; no commit recorded
Candidate IDs: ALG-0024, ALG-0025, ALG-0026, ALG-0027
Logs/datasets: targeted upstream-limit and support/noise cases in `scripts/alg0027_upstream_limit_tests.py`
Metrics: selected policy, selection status, upstream selected cut, policy-set detected flag, train/validation overlap, final-positive replay, final-negative rejection, expected failure/pass flags, selector counts, and validation replay proxy counts
Operation-count model: first-iteration primitive model plus `ALG-0027` validation replay proxy from EXP-0029

Subagent findings merged:

- Evaluator/counterexample scout recommended `no_policy_set` as the correct behavior for one-iteration-only, duplicate-label, and body length greater than two cases.
- The scout flagged rare-body/noise as outside loop-count selection: current alternatives inherit the same body choices, so selecting `unbounded_repeat` or `at_most_once` must not be interpreted as resolving body inclusion.
- Validation/final leakage should continue to be flagged and excluded from promotion-quality evidence.

Targeted `ALG-0027` upstream-limit results:

| Case | Expected | Selected | Status | Policy set | Final positives | Final negatives | Interpretation |
|---|---|---|---|---:|---:|---:|---|
| `one_iteration_only_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | No zero-iteration evidence; upstream exposes no count ambiguity. |
| `duplicate_suffix_label_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Duplicate body/suffix labels remain blocked upstream. |
| `length3_body_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Body length greater than two remains outside the current detector. |
| `overlapping_body_labels_no_policy_set` | none | none | `no_policy_set` | no | 0/1 | 1/1 | Overlapping body labels remain blocked upstream. |
| `rare_body_valid_unbounded_control` | `unbounded_repeat` | `unbounded_repeat` | `selected` | yes | 1/1 | 2/2 | Rare body is treated as valid when validation positives require it. |
| `rare_body_noise_gap` | `at_most_once` | `at_most_once` | `selected` | yes | 0/0 | 0/1 | Count selection does not remove a rare observed body treated as noise. |
| `rare_body_noise_training_conflict` | none | none | `unresolved` | yes | 0/0 | 0/1 | Marking an observed rare body invalid conflicts with training evidence. |

Interpretation:

- `ALG-0027` correctly refuses to select loop-count policies when upstream `ALG-0026` emits no policy set.
- The blocked cases confirm that `ALG-0027` cannot repair upstream detector/compiler limits: one-iteration-only evidence, duplicate labels, length >2 bodies, and overlapping body labels need separate candidates.
- The rare-body valid control shows the selector still works when validation declares rare observed bodies valid.
- The rare-body noise gap is the important negative result: selecting at-most-once count semantics does not remove the rare observed body from the accepted language, so support/noise body selection is separate from count selection.
- Marking an observed rare body invalid in validation creates a training/validation conflict and leaves selection unresolved.

Failures / anomalies:

- This experiment intentionally includes expected negative results; passing means the limitations were observed and not silently converted into selection claims.
- Final-positive replay is poor on `no_policy_set` blocked cases because fallback nets do not model the held-out loop behavior.
- The rare-body/noise gap leaves `ALG-0027` below `deep-testing`.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Keep `ALG-0027` at `promising`; do not move it to `deep-testing`.
- Do not retire it: within explicit external-validation and upstream-policy-set scope it remains useful.
- Treat rare loop-body support/noise as a new candidate line or guard, not as an `ALG-0027` count-selector feature.
- Do not create a property dossier.

Next action: split a rare-body support/noise guard candidate for `ALG-0024`/`ALG-0025`, with controls that distinguish valid rare bodies from noise.

## EXP-0031 - ALG-0028 body-support guard smoke tests

Date: 2026-05-07

Goal: split rare loop-body support/noise handling from `ALG-0027` loop-count selection and test a conservative support-prior guard over `ALG-0025`

Subagent support:

- Spawned a candidate/evaluator scout for the rare-body support/noise guard design.
- Merged recommendation: keep `ALG-0028` smoke-tested only; filter only singleton rare bodies when a dominant body has count at least 3 and at least 75 percent body-share; preserve 2:1 and balanced cases as ambiguous; explicitly document valid rare-body failure.

Code version / commit if available: working tree after adding `scripts/cut_limited_body_support_guard.py`, `scripts/alg0028_body_support_tests.py`, wiring `cut_limited_body_support_guard` into `scripts/alg0023_loop_tests.py` and `scripts/benchmark.py`, and creating `candidates/ALG-0028-cut-limited-body-support-guard-miner.md`; no commit recorded

Candidate IDs: ALG-0025, ALG-0028

Commands:

```bash
python3 -B -m compileall scripts/cut_limited_body_support_guard.py scripts/alg0028_body_support_tests.py
python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json
python3 -B -m compileall scripts/alg0023_loop_tests.py scripts/alg0025_length_bounded_loop_tests.py scripts/cut_limited_body_support_guard.py scripts/alg0028_body_support_tests.py
python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json
python3 -B -m compileall scripts/benchmark.py scripts/cut_limited_body_support_guard.py scripts/alg0023_loop_tests.py scripts/alg0028_body_support_tests.py
python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json
python3 -B -m compileall scripts
python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json
python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json
python3 -B -m unittest
git diff --check
```

Operation-count model: first-goal primitive model. `ALG-0028` reports combined counts for upstream `ALG-0025` discovery, support-policy checks, trace/body filtering, and guarded loop-net recompilation when filtering applies.

Implemented:

- `scripts/cut_limited_body_support_guard.py`
  - Runs `ALG-0025`.
  - Applies the support policy only when `dominant_count >= 3`, dominant body share is at least 75 percent, and a non-dominant body has count exactly 1.
  - Recompiles the loop with kept bodies when filtering applies, including the one-kept-body length-2 case.
  - Records `support_guard`, `filtered_bodies`, `kept_bodies`, source evidence, and combined operation counts.
- `scripts/alg0028_body_support_tests.py`
  - Seven targeted smoke/control cases with expected outcomes and a failing exit on expectation mismatch.
- `scripts/benchmark.py` and `scripts/alg0023_loop_tests.py`
  - Added `cut_limited_body_support_guard` to the reusable candidate lists.

Targeted `ALG-0028` results:

| Case | Guard applied | Train replay | Held-out replay | Negative rejection | Ops | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `rare_body_noise_3_to_1` | yes | 4/5 | 1/1 | 2/2 | 519 | Singleton rare body is filtered and rare-body-as-noise probes are rejected; training replay intentionally loses the rare observed trace. |
| `rare_body_valid_3_to_1_documented_failure` | yes | 4/5 | 0/2 | 0/0 | 519 | Same support pattern can represent valid rare behavior; this blocks promotion. |
| `balanced_two_body_choice` | no | 5/5 | 2/2 | 2/2 | 338 | Balanced body choices are preserved. |
| `low_sample_2_to_1_ambiguous` | no | 4/4 | 1/1 | 2/2 | 301 | 2:1 evidence is kept ambiguous. |
| `length2_rare_body_noise` | yes | 4/5 | 1/1 | 2/2 | 732 | Singleton-supported length-2 body is filtered; dominant length-2 body remains repeatable. |
| `mixed_width_rare_singleton_noise` | yes | 4/5 | 1/1 | 2/2 | 584 | Singleton-supported length-2 body is filtered while the dominant singleton body remains repeatable. |
| `two_rare_bodies_no_dominant` | no | 5/5 | 1/1 | 2/2 | 395 | Weak dominance with multiple rare bodies is not filtered. |

Baseline comparison observations:

- `ALG-0025` replays all training traces on rare-body cases but accepts rare-body-as-noise probes, e.g. `rare_body_noise_3_to_1` negative rejection is 0/2 for `ALG-0025` versus 2/2 for `ALG-0028`.
- On balanced and low-sample cases, `ALG-0028` matches `ALG-0025` behavior with small policy-count overhead.
- On the six toy logs in `examples/logs`, `ALG-0028` behaves like `ALG-0025` plus one counted comparison because no support guard applies.

Failures / anomalies:

- The valid rare-body control is an intentional negative result: the support prior filters rare behavior when the held-out positives require it.
- `ALG-0028` intentionally sacrifices observed-trace replay in noisy rare-body cases, so its training replay can be lower than `ALG-0025`.
- It inherits `ALG-0025` detector limits: length greater than two, overlapping body labels, duplicate labels, and one-iteration-only evidence remain unresolved.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Add `ALG-0028` as `smoke-tested`, not `promising`.
- Do not promote: support alone cannot distinguish valid rare behavior from noise.
- Keep it as a precision-prior candidate and counterexample line for future threshold/validation selection.

Next action: run support-threshold ablations for `ALG-0028` across 3:1, 4:1, 5:1, 2:1, two-rare-body, and valid rare-body controls; then test whether external validation can select body inclusion before combining with `ALG-0026`/`ALG-0027` loop-count policy sets.

## EXP-0032 - ALG-0028 threshold ablation and ALG-0029 body-inclusion validation selector

Date: 2026-05-07

Goal: quantify the `ALG-0028` support-threshold tradeoff and test whether explicit validation can select loop-body inclusion when support alone is ambiguous

Subagent support:

- Spawned an evaluator/counterexample scout for the `ALG-0028` ablation matrix.
- Merged recommendation: test 2:1, 3:1, 4:1, and 5:1 support policies; record valid-rare and rare-noise matched cases; include rare-count-two, multiple-rare-body, length-2, mixed-width, validation-include, validation-exclude, validation-conflict, and no-signal controls; do not promote `ALG-0028` on threshold evidence alone.

Code version / commit if available: working tree after parameterizing `scripts/cut_limited_body_support_guard.py`, adding `scripts/body_inclusion_validation_selector.py`, adding `scripts/alg0028_threshold_ablation_tests.py`, and creating `candidates/ALG-0029-loop-body-inclusion-validation-selector.md`; no commit recorded

Candidate IDs: ALG-0025, ALG-0028, ALG-0029

Commands:

```bash
python3 -B -m compileall scripts/body_inclusion_validation_selector.py scripts/alg0028_threshold_ablation_tests.py scripts/cut_limited_body_support_guard.py
python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json
python3 -B -m compileall scripts
python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json
python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json
python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json
python3 -B -m unittest
git diff --check
```

Operation-count model: first-goal primitive model. `ALG-0028` counts upstream discovery plus guard policy/filtering/compilation. `ALG-0029` reports selector counts, validation replay proxy counts, selected-result totals, and a naive all-alternative total that includes both `ALG-0025` and `ALG-0028` discovery.

Implemented:

- `scripts/cut_limited_body_support_guard.py`
  - Added `discover_with_policy(...)` while preserving default `discover(log)` behavior.
  - Supports configurable dominant-count, dominant-share, and rare-body-count thresholds.
- `scripts/body_inclusion_validation_selector.py`
  - Adds `ALG-0029`, a selector over `keep_all_bodies` (`ALG-0025`) and `support_guard` (`ALG-0028`) alternatives.
  - Selects only when validation positives/negatives uniquely distinguish alternatives.
  - Reports `validation_inconsistent`, `validation_training_conflict`, and `unresolved` controls.
- `scripts/alg0028_threshold_ablation_tests.py`
  - Runs support threshold policies `2:1`, `3:1 default`, `4:1`, and `5:1`.
  - Includes singleton noise/valid pairs for support counts 2 through 5, rare count two, two rare bodies, length-2 dominant/rare cases, mixed-width cases, and five `ALG-0029` validation controls.

`ALG-0028` threshold summary:

| Policy | Guard-applied cases | Train replay | Valid-rare replay | Rare-noise rejection | Interpretation |
|---|---:|---:|---:|---:|---|
| `keep_all_baseline` | 0 | 86/86 | 10/10 | 0/17 | Baseline preserves all observed/valid rare behavior but accepts all rare-noise probes. |
| `support_2_to_1` | 13 | 71/86 | 0/10 | 15/17 | Aggressive: best rare-noise rejection and worst valid-rare loss. |
| `support_3_to_1_default` | 9 | 77/86 | 3/10 | 10/17 | Reproduces EXP-0031 tradeoff. |
| `support_4_to_1` | 7 | 79/86 | 5/10 | 8/17 | More conservative; partial recovery of valid rare behavior with less rare-noise rejection. |
| `support_5_to_1` | 3 | 83/86 | 8/10 | 4/17 | Safest support prior; leaves most rare-noise probes unfiltered. |

`ALG-0029` validation-selector results:

| Case | Expected | Selected | Status | Naive all-alternative + validation proxy total | Interpretation |
|---|---|---|---|---:|---|
| `validation_selects_keep_rare_3_to_1` | `keep_all_bodies` | `keep_all_bodies` | `selected` | 897 | Validation positives require the rare body, so support filtering is overridden. |
| `validation_selects_filter_rare_3_to_1` | `support_guard` | `support_guard` | `selected` | 903 | Validation negatives reject rare-body combinations, so filtering is selected. |
| `validation_no_body_signal_unresolved` | none | none | `unresolved` | 906 | Validation does not mention rare-body inclusion; no selection. |
| `validation_training_conflict` | none | none | `validation_training_conflict` | 884 | Validation negative overlaps an observed training trace. |
| `validation_positive_negative_conflict` | none | none | `validation_inconsistent` | 903 | Same validation trace is both positive and negative. |

Interpretation:

- `ALG-0028` is a threshold-sensitive precision prior. A stricter threshold improves valid-rare replay but leaves more rare-noise behavior accepted.
- Rare-count-two noise and multiple rare-body noise expose gaps in singleton-only filtering.
- The validation selector can choose body inclusion when explicit probes distinguish the alternatives, matching the pattern that made `ALG-0027` useful for loop-count policy.
- `ALG-0029` should be treated as a selector protocol, not a training-log-only miner.

Failures / anomalies:

- No support threshold cleanly separates rare noise from valid rare behavior across the matrix.
- The aggressive 2:1 policy destroys valid-rare replay in the tested controls.
- The 5:1 policy preserves most valid-rare replay but rejects only 4/17 rare-noise probes.
- `ALG-0029` currently uses a naive all-alternative cost that double-counts upstream discovery work that a later optimized selector might share.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Keep `ALG-0028` at `smoke-tested`; threshold ablations reinforce that support-only body filtering is a policy tradeoff.
- Add `ALG-0029` as `smoke-tested`, not `promising`: it has executable validation-selector evidence but lacks split final-test protocol, broader support-ratio coverage, and refined validation cost accounting.
- Do not promote any candidate to `super-promising`.

Next action: add a split validation/final-test protocol for `ALG-0029`, then test composition with `ALG-0026`/`ALG-0027` so body inclusion and loop-count policy are selected independently rather than conflated.

## EXP-0033 - ALG-0029 split validation protocol and ALG-0030 body-count product selector

Date/time: 2026-05-07T12:53:00+02:00

Goal: add a split validation/final-test protocol for `ALG-0029` and test whether body inclusion and loop-count semantics can be selected as independent policy axes

Subagent support:

- Spawned an evaluator/counterexample scout for `ALG-0029` split protocol and composition design.
- Merged recommendations: add keep/filter final-generalization and final-precision cases, no-signal and leakage controls, training/validation conflict controls, 5:1 support-ratio keep control, length-2 rare-body filter control, two-rare-body mixed valid/noise unresolved control, rare-count-two unresolved control, and four joint product quadrants for body inclusion x loop count.

Code version / commit if available: working tree after adding `scripts/body_count_validation_product_selector.py`, `scripts/alg0029_validation_protocol_tests.py`, `candidates/ALG-0030-loop-body-count-validation-product-selector.md`, and extending `scripts/loop_policy_set_protocol.py` with `result_from_base(...)`; no commit recorded

Candidate IDs: ALG-0025, ALG-0026, ALG-0027, ALG-0028, ALG-0029, ALG-0030

Commands:

```bash
python3 -B -m compileall scripts/body_count_validation_product_selector.py scripts/alg0029_validation_protocol_tests.py scripts/loop_policy_set_protocol.py
python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json
python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json
python3 -B -m compileall scripts
python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json
python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json
python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json
python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json
python3 -B -m unittest
git diff --check
python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json
python3 -c "import json; d=json.load(open('experiments/alg0029-validation-protocol-tests.json')); print('body_summary', d['body_protocol']['summary']); print('composition_summary', d['composition_protocol']['summary']); print('body_cases'); [print(n, c['selected_alternative'], c['selection_status'], 'leak', c['has_leakage'], 'total', c['operation_counts'].get('total_with_all_alternatives_and_validation_proxy')) for n,c in sorted(d['body_protocol']['cases'].items())]; print('composition_cases'); [print(n, c['selected_body'], c['selected_policy'], c['selection_status'], 'total', c['operation_counts'].get('total_with_product_selector_and_validation_proxy')) for n,c in sorted(d['composition_protocol']['cases'].items())]"
```

Operation-count model: first-goal primitive model. `ALG-0029` keeps the naive all-alternative discovery plus selector and validation replay proxy counts from EXP-0032. `ALG-0030` adds count-policy compilation from the selected body result, count-selector operations, and count-validation replay proxy counts; the reported product total is a naive upper bound and does not yet share all reusable discovery work.

Implemented:

- `scripts/loop_policy_set_protocol.py`
  - Added `result_from_base(...)` so count-policy alternatives can be built from an already-selected body-inclusion result.
  - Allowed `body_support_guard_rework_loop` process-tree evidence to produce count-policy alternatives.
- `scripts/body_count_validation_product_selector.py`
  - Added `ALG-0030`, a product selector over body inclusion (`keep_all_bodies` or `support_guard`) and count policy (`unbounded_repeat` or `at_most_once`).
  - Returns `body_unresolved` if body inclusion is not selected and `count_unresolved` if count policy is not selected.
- `scripts/alg0029_validation_protocol_tests.py`
  - Added 10 split validation/final tests for `ALG-0029`.
  - Added 6 composition tests for `ALG-0030`.
- `candidates/ALG-0030-loop-body-count-validation-product-selector.md`
  - Added candidate record with hypothesis, intermediate representation, operation model, failure modes, and promotion criteria.

`ALG-0029` split validation/final results:

| Case | Expected | Selected | Status | Leakage | Final result | Naive total |
|---|---|---|---|---:|---|---:|
| `body_keep_final_generalization` | `keep_all_bodies` | `keep_all_bodies` | `selected` | no | 1/1 positive, 2/2 negatives rejected | 906 |
| `body_filter_final_precision` | `support_guard` | `support_guard` | `selected` | no | 1/1 positive, 2/2 negatives rejected | 903 |
| `body_no_signal_final_not_used` | none | none | `unresolved` | no | final probes not used for selection | 906 |
| `body_validation_final_overlap_guard` | `keep_all_bodies` | `keep_all_bodies` | `selected` | yes | leakage flagged | 897 |
| `body_training_negative_conflict_final_control` | none | none | `validation_training_conflict` | yes | conflict control | 884 |
| `body_positive_negative_overlap` | none | none | `validation_inconsistent` | no | conflict control | 903 |
| `body_support_ratio_5_to_1_keep` | `keep_all_bodies` | `keep_all_bodies` | `selected` | no | 1/1 positive, 1/1 negative rejected | 1104 |
| `body_length2_rare_filter` | `support_guard` | `support_guard` | `selected` | no | 1/1 positive, 1/1 negative rejected | 1503 |
| `two_rare_one_valid_one_noise_unresolved` | none | none | `unresolved` | no | alternatives cannot split rare bodies individually | 1060 |
| `rare_count_two_noise_unresolved` | none | none | `unresolved` | no | rare count two remains outside support guard | 947 |

Summary: 10/10 body protocol cases passed.

`ALG-0030` composition results:

| Case | Expected product | Selected product | Status | Final result | Naive product total |
|---|---|---|---|---|---:|
| `keep_all_unbounded_joint` | keep-all + unbounded | keep-all + unbounded | `selected` | 1/1 positive, 1/1 negative rejected | 942 |
| `keep_all_at_most_once_joint` | keep-all + at-most-once | keep-all + at-most-once | `selected` | 0/0 positives, 2/2 negatives rejected | 959 |
| `filter_unbounded_joint` | support-guard + unbounded | support-guard + unbounded | `selected` | 1/1 positive, 1/1 negative rejected | 948 |
| `filter_at_most_once_joint` | support-guard + at-most-once | support-guard + at-most-once | `selected` | 0/0 positives, 2/2 negatives rejected | 962 |
| `body_selected_count_unresolved` | support-guard + none | support-guard + none | `count_unresolved` | not selection-quality | 934 |
| `count_selected_body_unresolved` | none + none | none + none | `body_unresolved` | not selection-quality | 897 |

Summary: 6/6 composition protocol cases passed.

Regression checks:

- `ALG-0028` threshold ablation unchanged: keep-all 86/86 train and 0/17 rare-noise rejection; 2:1 71/86 train, 0/10 valid rare, 15/17 rare-noise rejection; 3:1 77/86, 3/10, 10/17; 4:1 79/86, 5/10, 8/17; 5:1 83/86, 8/10, 4/17.
- `ALG-0027` split validation protocol remains 9/9 passed.
- `ALG-0028` body-support tests remain 7/7 expectation-true.
- `scripts/benchmark.py` completed on all logs in `examples/logs`; no new candidate was wired into the general benchmark because both `ALG-0029` and `ALG-0030` require validation channels.

Failures / anomalies:

- The first local run of `alg0029_validation_protocol_tests.py` failed two leakage expectations because final negatives reused validation negatives; the cases were corrected to use distinct final probes and rerun successfully.
- `ALG-0029` remains unable to resolve a mixed two-rare-body case where one rare body is valid and one is noise because the current alternatives either keep or filter rare bodies as a group.
- `ALG-0029` remains unable to filter rare bodies with count two because `ALG-0028` only filters `rare_body_count=1` by default.
- `ALG-0030` validates a product protocol but not a training-log-only discovery claim.
- Product operation counts are naive upper bounds; shared discovery accounting is still unresolved.
- No property dossier was created because no candidate is `super-promising`.
- `python3 -B -m unittest` found no tests and exited with `NO TESTS RAN`.
- `git diff --check` exited successfully, with only pre-existing CRLF replacement warnings for `.gitignore` and `LICENSE`.

Decision:

- Keep `ALG-0029` at `smoke-tested`: split final tests now pass, but validation cost remains a proxy and unresolved rare-count-two / mixed rare-body cases block promotion.
- Add `ALG-0030` as `smoke-tested`: the product protocol works on four joint quadrants and one-axis-unresolved controls, but needs broader stress and better operation accounting before promotion.
- Do not promote any candidate to `super-promising`.

Next action: stress `ALG-0030` on length-2 and mixed-width product quadrants, duplicate-label blocked cases, and rare-count-two body policy alternatives; then refine selector operation accounting to share upstream discovery work across body/count axes.
