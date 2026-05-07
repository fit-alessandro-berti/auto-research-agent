# CONTINUITY.md

## Active goal

`GOALS/first-petri-net-limited-ops.md`.

## Current status

Thirty-eighth research iteration complete. `ALG-0033` is now a smoke-tested lower-cost direct-signal selector for per-body rare loop inclusion. It avoids `ALG-0032`'s exhaustive `2^R` assignment enumeration by parsing validation traces once, assigning positive rare-body keep signals, unit-propagating negative rare-body clauses, compiling at most one guarded net, and replaying validation only for that selected net. `scripts/alg0033_direct_signal_tests.py` passes 16/16 cases: core one-rare and two-rare mixed cases, count-two rare bodies, unit propagation, R=3/R=5 direct-signal scale cases, partial-signal unresolved, body-signal conflict, non-unit interaction ambiguity, cap overflow, weak dominance, validation overlap, and training-negative conflict. Matched two-rare/count-two cases stay under `B_deep` and below `ALG-0032` shared totals, and the R=5 direct-signal reference totals 1442/1690 operations. `ALG-0033` remains `smoke-tested`, not `promising`, because evidence is synthetic/validation-scoped and deliberately incomplete for non-unit interaction clauses. `ALG-0032`, `ALG-0029`, and `ALG-0030` remain `smoke-tested`; `ALG-0003`, `ALG-0009`, `ALG-0011`, and `ALG-0015` remain in `deep-testing`; `ALG-0027` remains `promising`; no candidate is `super-promising`.

## Last completed actions

- Created process-mining research-agent scaffold.
- Added candidate registry, evaluation protocol, property-study protocol, and smoke-test harness.
- Implemented `ALG-0001` Alpha-Lite Relations baseline.
- Implemented `ALG-0006` PMIR Split-Join Compiler Lite starter candidate.
- Ran `python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Spawned candidate, implementation, evaluator/counterexample, and property-study scouts; merged their findings into registry and experiment notes.
- Added `ALG-0002` Frequency-Threshold Dependency Graph prototype.
- Added `scripts/petri_eval.py` with strict token-game replay and structural diagnostics.
- Added explicit `arithmetic` primitive to the operation model.
- Created candidate records for `ALG-0002` through `ALG-0005`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json` and `python3 -B -m compileall scripts`.
- Added `ALG-0009` PMIR Guarded Split-Join Compiler as a repaired variant of `ALG-0006`.
- Extended the evaluator with bounded silent-transition closure for `tau_` transitions.
- Added negative-trace precision probes to `scripts/benchmark.py`.
- Added `scripts/dependency_threshold_sweep.py` and ran `experiments/dependency-threshold-sweep.json`.
- Promoted `ALG-0009` to `promising`; no candidate is `super-promising`.
- Added ablation switches to `ALG-0009` for optional and XOR guards.
- Added `scripts/alg0009_deep_tests.py` with synthetic counterexamples and trace-order stability checks.
- Ran `experiments/alg0009-deep-tests.json`.
- Moved `ALG-0009` to `deep-testing`; no candidate is `super-promising`.
- Added `ALG-0010` PMIR Conflict-Aware Optional Chain Compiler.
- Wired `ALG-0010` into smoke and synthetic deep-test runners.
- Promoted `ALG-0010` to `promising`; no candidate is `super-promising`.
- Added `scripts/cut_limited_process_tree.py` for `ALG-0003`.
- Wired `ALG-0003` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0003` to `promising`; no candidate is `super-promising`.
- Added `parallel_optional_sequence` detection and compilation to `ALG-0003`.
- Added `cut_tree_no_parallel_optional` ablation to `scripts/alg0009_deep_tests.py`.
- Reran smoke and synthetic tests; moved `ALG-0003` to `deep-testing`; no candidate is `super-promising`.
- Added optional `transition_labels` to Petri-net JSON and evaluator support for multiple same-label visible transitions.
- Added `scripts/prefix_automaton_compression.py` for `ALG-0005`.
- Wired `ALG-0005` into smoke and synthetic runners.
- Promoted `ALG-0005` to `promising`; no candidate is `super-promising`.
- Added `scripts/alg0005_stress_tests.py`.
- Ran `experiments/alg0005-stress-tests.json`.
- Kept `ALG-0005` at `promising`; no candidate is `super-promising`.
- Added `scripts/bounded_place_region_miner.py` for `ALG-0004`.
- Wired `ALG-0004` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Moved `ALG-0004` to `benchmarked`; no candidate is `super-promising`.
- Added `scripts/region_optional_tau_miner.py` for `ALG-0011`.
- Wired `ALG-0011` into `scripts/benchmark.py` and `scripts/alg0009_deep_tests.py`.
- Added `candidates/ALG-0011-region-optional-tau-repair-miner.md`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0011` to `promising`; no candidate is `super-promising`.
- Added `enable_optional_repair` ablation switch to `scripts/region_optional_tau_miner.py`.
- Added `scripts/alg0011_optional_tests.py` with singleton, two-disjoint, overlapping-chain, and optional-inside-parallel cases.
- Ran `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Moved `ALG-0011` to `deep-testing`; no candidate is `super-promising`.
- Added `scripts/region_optional_chain_miner.py` for `ALG-0012`.
- Wired `ALG-0012` into `scripts/benchmark.py`, `scripts/alg0009_deep_tests.py`, and `scripts/alg0011_optional_tests.py`.
- Added `candidates/ALG-0012-region-optional-chain-repair-miner.md`.
- Ran `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Reran `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 -B -m compileall scripts`.
- Promoted `ALG-0012` to `promising`; no candidate is `super-promising`.
- Added `require_region_shortcut` to `scripts/region_optional_chain_miner.py`.
- Added `ALG-0013` as the `require_region_shortcut=False` ablation of `ALG-0012`.
- Wired `region_optional_chain_no_region_cert` into `scripts/alg0011_optional_tests.py` and `scripts/alg0009_deep_tests.py`.
- Added `optional_singleton_parallel_branch` to the optional-pattern suite.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, and `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`.
- Ran `python3 -B -m unittest` and `git diff --check` for final verification.
- Kept `ALG-0012` at `promising`, added `ALG-0013` as `smoke-tested`; no candidate is `super-promising`.
- Added `scripts/prefix_block_abstraction.py` for `ALG-0014`.
- Wired `prefix_block_abstraction` into `scripts/benchmark.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0005_stress_tests.py`.
- Added `candidates/ALG-0014-prefix-block-abstraction-miner.md`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, and `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned bounded-loop policy candidate, evaluator/counterexample, and implementation scouts; merged their findings into EXP-0027.
- Added `scripts/loop_policy_set_protocol.py` for `ALG-0026`.
- Added `scripts/alg0026_loop_policy_tests.py`.
- Added `candidates/ALG-0026-loop-count-policy-set-protocol.md`.
- Ran `python3 -B -m compileall scripts` and `python3 scripts/alg0026_loop_policy_tests.py --out experiments/alg0026-loop-policy-tests.json`.
- Added `ALG-0026` as `smoke-tested`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Promoted `ALG-0014` to `promising`; no candidate is `super-promising`.
- Added support-skew checks, prefix-merge detection, and same-activity-set dominant-sequence handling to `scripts/prefix_block_abstraction.py`.
- Added `scripts/prefix_block_support_guard.py` for `ALG-0015`.
- Added `scripts/prefix_block_grammar_only.py` for `ALG-0016`.
- Wired both into `scripts/benchmark.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0005_stress_tests.py`.
- Added candidate records for `ALG-0015` and `ALG-0016`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, and `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Promoted `ALG-0015` to `promising`, added `ALG-0016` as `smoke-tested`; no candidate is `super-promising`.
- Added `scripts/prefix_block_support_only.py` for `ALG-0017`.
- Added `scripts/prefix_block_prefix_merge_only.py` for `ALG-0018`.
- Added `scripts/prefix_block_dominant_only.py` for `ALG-0019`.
- Added `scripts/alg0015_ablation_tests.py`.
- Wired `ALG-0017`, `ALG-0018`, and `ALG-0019` into `scripts/benchmark.py`, `scripts/alg0005_stress_tests.py`, `scripts/alg0009_deep_tests.py`, and `scripts/alg0011_optional_tests.py`.
- Added candidate records for `ALG-0017`, `ALG-0018`, and `ALG-0019`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0015_ablation_tests.py --out experiments/alg0015-ablation-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Moved `ALG-0015` to `deep-testing`; kept `ALG-0017`, `ALG-0018`, and `ALG-0019` as smoke-tested ablations. No candidate is `super-promising`.
- Exposed `prefix_merge_policy`, `min_dominant_count`, and `min_dominant_ratio_percent` in `scripts/prefix_block_abstraction.py`.
- Added `scripts/prefix_block_conservative_merge.py` for `ALG-0020`.
- Added `scripts/alg0015_noise_incomplete_tests.py`.
- Wired `ALG-0020` into `scripts/benchmark.py`, `scripts/alg0005_stress_tests.py`, `scripts/alg0009_deep_tests.py`, and `scripts/alg0011_optional_tests.py`.
- Added `candidates/ALG-0020-prefix-block-conservative-merge-miner.md`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Added `ALG-0020` as a smoke-tested tradeoff candidate; kept `ALG-0015` at `deep-testing`. No candidate is `super-promising`.
- Added prefix-merge ambiguity evidence to `scripts/prefix_block_abstraction.py`.
- Added `scripts/prefix_block_ambiguity_aware.py` for `ALG-0021`.
- Wired `ALG-0021` into `scripts/benchmark.py`, `scripts/alg0005_stress_tests.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0015_noise_incomplete_tests.py`.
- Added `candidates/ALG-0021-prefix-block-ambiguity-aware-pmir-miner.md`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0015_noise_incomplete_tests.py --out experiments/alg0015-noise-incomplete-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, and `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`.
- Added `ALG-0021` as a smoke-tested PMIR/evidence candidate; kept `ALG-0015` at `deep-testing`. No candidate is `super-promising`.
- Added `scripts/alg0021_ambiguity_protocol_tests.py` for `ALG-0022`.
- Added `candidates/ALG-0022-prefix-block-ambiguity-set-protocol.md`.
- Ran `python3 -B -m compileall scripts` and `python3 scripts/alg0021_ambiguity_protocol_tests.py --out experiments/alg0021-ambiguity-protocol-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Added `ALG-0022` as a smoke-tested multi-net PMIR protocol; no candidate is `super-promising`.
- Added `enable_short_loop` to `scripts/cut_limited_process_tree.py`.
- Added `scripts/cut_limited_loop_repair.py` for `ALG-0023`.
- Added `scripts/alg0023_loop_tests.py`.
- Wired `ALG-0023` into `scripts/benchmark.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0005_stress_tests.py`.
- Added `candidates/ALG-0023-cut-limited-single-rework-loop-miner.md`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, and `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Added and promoted `ALG-0023` to `promising`; no candidate is `super-promising`.
- Added `scripts/alg0023_loop_stress_tests.py`.
- Ran `python3 -B -m compileall scripts` and `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Kept `ALG-0023` at `promising`; no candidate is `super-promising`.
- Added `enable_multi_body_loop` and `multi_body_rework_loop` detection/compilation to `scripts/cut_limited_process_tree.py`.
- Added `scripts/cut_limited_multi_body_loop.py` for `ALG-0024`.
- Added `scripts/alg0024_multibody_loop_tests.py`.
- Wired `ALG-0024` into `scripts/benchmark.py`, `scripts/alg0023_loop_tests.py`, `scripts/alg0023_loop_stress_tests.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0005_stress_tests.py`.
- Added `candidates/ALG-0024-cut-limited-multi-body-rework-loop-miner.md`.
- Ran `python3 -B -m compileall scripts`, `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`, `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`, `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, and `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Added and promoted `ALG-0024` to `promising`; no candidate is `super-promising`.
- Added `scripts/alg0024_stress_tests.py`.
- Ran `python3 -B -m compileall scripts`, `python3 scripts/alg0024_stress_tests.py --out experiments/alg0024-stress-tests.json`, `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`, and `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Kept `ALG-0024` at `promising`; no candidate is `super-promising`.
- Extended `scripts/cut_limited_process_tree.py` so the multi-body loop detector accepts a fixed `multi_body_loop_max_body_length`.
- Added `scripts/cut_limited_length_bounded_loop.py` for `ALG-0025`.
- Added `scripts/alg0025_length_bounded_loop_tests.py`.
- Wired `ALG-0025` into `scripts/benchmark.py`, `scripts/alg0023_loop_tests.py`, `scripts/alg0009_deep_tests.py`, `scripts/alg0011_optional_tests.py`, and `scripts/alg0005_stress_tests.py`.
- Added `candidates/ALG-0025-cut-limited-length-bounded-rework-loop-miner.md`.
- Ran `python3 -B -m compileall scripts`, `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`, `python3 scripts/alg0024_stress_tests.py --out experiments/alg0024-stress-tests.json`, `python3 scripts/alg0024_multibody_loop_tests.py --out experiments/alg0024-multibody-loop-tests.json`, `python3 scripts/alg0023_loop_stress_tests.py --out experiments/alg0023-loop-stress-tests.json`, `python3 scripts/alg0023_loop_tests.py --out experiments/alg0023-loop-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0009_deep_tests.py --out experiments/alg0009-deep-tests.json`, `python3 scripts/alg0011_optional_tests.py --out experiments/alg0011-optional-tests.json`, and `python3 scripts/alg0005_stress_tests.py --out experiments/alg0005-stress-tests.json`.
- Added and promoted `ALG-0025` to `promising`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned a skeptical evaluator scout for `ALG-0027` and merged its validation-selector cautions into EXP-0028.
- Added `scripts/loop_count_validation_selector.py` for `ALG-0027`.
- Added `scripts/alg0027_loop_selector_tests.py`.
- Added `candidates/ALG-0027-loop-count-validation-selector.md`.
- Ran `python3 -B -m compileall scripts` and `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`.
- Added `ALG-0027` as `smoke-tested`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned an evaluator/counterexample scout for `ALG-0027` split validation protocol design and merged its findings into EXP-0029.
- Added validation replay proxy counts to `scripts/loop_count_validation_selector.py`.
- Added `scripts/alg0027_validation_protocol_tests.py`.
- Ran `python3 -B -m compileall scripts`, `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`, and `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`.
- Promoted `ALG-0027` to `promising`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`, `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned an evaluator/counterexample scout for `ALG-0027` upstream-limit stress design and merged its findings into EXP-0030.
- Added `scripts/alg0027_upstream_limit_tests.py`.
- Ran `python3 -B -m compileall scripts` and `python3 scripts/alg0027_upstream_limit_tests.py --out experiments/alg0027-upstream-limit-tests.json`.
- Kept `ALG-0027` at `promising`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 scripts/alg0027_upstream_limit_tests.py --out experiments/alg0027-upstream-limit-tests.json`, `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`, `python3 scripts/alg0027_loop_selector_tests.py --out experiments/alg0027-loop-selector-tests.json`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned a candidate/evaluator scout for rare-body support/noise guard design and merged its 3-count / 75-percent dominance recommendation into EXP-0031.
- Added `scripts/cut_limited_body_support_guard.py` for `ALG-0028`.
- Added `scripts/alg0028_body_support_tests.py`.
- Wired `ALG-0028` into `scripts/alg0023_loop_tests.py` and `scripts/benchmark.py`.
- Added `candidates/ALG-0028-cut-limited-body-support-guard-miner.md`.
- Ran `python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json`, `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Added `ALG-0028` as `smoke-tested`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json`, `python3 scripts/alg0025_length_bounded_loop_tests.py --out experiments/alg0025-length-bounded-loop-tests.json`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned an evaluator/counterexample scout for `ALG-0028` threshold ablations and merged its recommendations into EXP-0032.
- Parameterized `scripts/cut_limited_body_support_guard.py` with `discover_with_policy(...)`.
- Added `scripts/body_inclusion_validation_selector.py` for `ALG-0029`.
- Added `scripts/alg0028_threshold_ablation_tests.py`.
- Added `candidates/ALG-0029-loop-body-inclusion-validation-selector.md`.
- Ran `python3 -B -m compileall scripts/body_inclusion_validation_selector.py scripts/alg0028_threshold_ablation_tests.py scripts/cut_limited_body_support_guard.py` and `python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json`.
- Added `ALG-0029` as `smoke-tested`; kept `ALG-0028` at `smoke-tested`; no candidate is `super-promising`.
- Ran final `python3 -B -m compileall scripts`, `python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json`, `python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 -B -m unittest`, and `git diff --check`.
- Spawned an evaluator/counterexample scout for `ALG-0029` split validation/final and `ALG-0030` product-composition test design; merged its recommendations into EXP-0033.
- Extended `scripts/loop_policy_set_protocol.py` with `result_from_base(...)` and support for `body_support_guard_rework_loop` process-tree evidence.
- Added `scripts/body_count_validation_product_selector.py` for `ALG-0030`.
- Added `scripts/alg0029_validation_protocol_tests.py` with 10 `ALG-0029` split validation/final cases and 6 `ALG-0030` composition cases.
- Added `candidates/ALG-0030-loop-body-count-validation-product-selector.md`.
- Ran `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`; 10/10 body protocol cases and 6/6 composition cases passed after correcting deliberate leakage controls.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json`, `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0028_body_support_tests.py --out experiments/alg0028-body-support-tests.json`, `python3 -B -m unittest`, and `git diff --check`.
- Added `ALG-0030` as `smoke-tested`; kept `ALG-0029` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an evaluator/counterexample scout for `ALG-0030` product stress and rare-count-two policy alternatives; merged its recommendations into EXP-0034.
- Added `scripts/alg0030_product_stress_tests.py` with 20 product-stress cases.
- Added `candidates/ALG-0031-rare-count-two-body-support-guard-ablation.md`.
- Ran `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`; 20/20 cases passed.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0028_threshold_ablation_tests.py --out experiments/alg0028-threshold-ablation-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0027_validation_protocol_tests.py --out experiments/alg0027-validation-protocol-tests.json`, `python3 -B -m unittest`, and `git diff --check`.
- Added `ALG-0031` as `smoke-tested`; kept `ALG-0030` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an evaluator/counterexample scout for `ALG-0032` per-body inclusion design and merged its smoke/counterexample recommendations into EXP-0035.
- Added `scripts/per_body_inclusion_validation_selector.py` for `ALG-0032`.
- Added `scripts/alg0032_per_body_inclusion_tests.py` with 11 targeted per-body inclusion, ambiguity, conflict, dominance, and cap controls.
- Added `candidates/ALG-0032-per-body-rare-inclusion-validation-selector.md`.
- Ran `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`; after correcting an overly strict initial 5/6 dominance default to 5/7, the final suite passed 11/11.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Ran final `python3 -B -m unittest`, `git diff --check`, and `git status --short --untracked-files=all`.
- Added `ALG-0032` as `smoke-tested`; kept `ALG-0029`, `ALG-0030`, and `ALG-0031` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an evaluator/counterexample scout for `ALG-0032` split validation/final protocol design and merged its recommendations into EXP-0036.
- Added `scripts/alg0032_validation_protocol_tests.py` with 13 split validation/final, width, leakage, cap, baseline-comparison, and blocked-scope controls.
- Ran `python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json`; 13/13 cases passed.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Ran final `python3 -B -m unittest`, `git diff --check`, and `git status --short --untracked-files=all`.
- Kept `ALG-0032`, `ALG-0029`, `ALG-0030`, and `ALG-0031` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an implementation scout for shared selector accounting and merged its decomposition recommendations into EXP-0037.
- Added `scripts/selector_shared_cost_report.py`.
- Ran `python3 scripts/selector_shared_cost_report.py --out experiments/selector-shared-cost-report.json`; `ALG-0029` max current/shared totals were 1503/934, `ALG-0030` 962/638, and `ALG-0032` 7430/3167.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`, `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`, and `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`.
- Ran final `python3 -B -m unittest`, `git diff --check`, and `git status --short --untracked-files=all`.
- Kept `ALG-0029`, `ALG-0030`, and `ALG-0032` at `smoke-tested`; no candidate is `super-promising`.
- Added `scripts/selector_shared_accounting.py`.
- Integrated shared operation-accounting fields into `scripts/body_inclusion_validation_selector.py`, `scripts/per_body_inclusion_validation_selector.py`, and `scripts/body_count_validation_product_selector.py`.
- Updated `scripts/selector_shared_cost_report.py` to cross-check selector-integrated shared totals against the EXP-0037 derivation.
- Ran `python3 scripts/selector_shared_cost_report.py --out experiments/selector-shared-cost-report.json`; the cross-check reported `mismatches []`.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json`, `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`, `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Ran final `python3 -B -m unittest`, `git diff --check`, and `git status --short --untracked-files=all`.
- Kept `ALG-0029`, `ALG-0030`, and `ALG-0032` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an evaluator/counterexample scout for `ALG-0032` cap-stress design and merged its recommendations into EXP-0039.
- Added `scripts/alg0032_cap_stress_tests.py`.
- Ran `python3 scripts/alg0032_cap_stress_tests.py --out experiments/alg0032-cap-stress-tests.json`; 11/11 cases passed, selected cases exceeded the deep soft budget from two rare bodies onward, and cap-plus-one refusals stayed under budget.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json`, `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`, `python3 scripts/selector_shared_cost_report.py --out experiments/selector-shared-cost-report.json`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Kept `ALG-0032`, `ALG-0029`, and `ALG-0030` at `smoke-tested`; no candidate is `super-promising`.
- Spawned an evaluator/counterexample scout for `ALG-0033` direct-signal selector design and merged its unit-propagation, non-unit ambiguity, and operation-budget recommendations into EXP-0040.
- Added `scripts/per_body_direct_signal_selector.py` for `ALG-0033`.
- Added `scripts/alg0033_direct_signal_tests.py` with 16 direct-signal smoke, counterexample, and scale controls.
- Added `candidates/ALG-0033-per-body-direct-signal-validation-selector.md`.
- Ran `python3 scripts/alg0033_direct_signal_tests.py --out experiments/alg0033-direct-signal-tests.json`; 16/16 cases passed, 9 cases selected, no selected case exceeded `B_deep`, and matched two-rare/count-two cases were lower cost than `ALG-0032` shared totals.
- Reran `python3 -B -m compileall scripts`, `python3 scripts/alg0032_cap_stress_tests.py --out experiments/alg0032-cap-stress-tests.json`, `python3 scripts/alg0032_validation_protocol_tests.py --out experiments/alg0032-validation-protocol-tests.json`, `python3 scripts/alg0032_per_body_inclusion_tests.py --out experiments/alg0032-per-body-inclusion-tests.json`, `python3 scripts/alg0029_validation_protocol_tests.py --out experiments/alg0029-validation-protocol-tests.json`, `python3 scripts/alg0030_product_stress_tests.py --out experiments/alg0030-product-stress-tests.json`, `python3 scripts/selector_shared_cost_report.py --out experiments/selector-shared-cost-report.json`, and `python3 scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json`.
- Ran final `python3 -B -m unittest` (no tests found, exit code 5) and `git diff --check` (success with pre-existing CRLF warnings).
- Added `ALG-0033` as `smoke-tested`; kept `ALG-0032`, `ALG-0029`, and `ALG-0030` at `smoke-tested`; no candidate is `super-promising`.

## Latest smoke / stress result

EXP-0014 executable-candidate replay summary, with later candidate-specific deltas below:

| Log | ALG-0001 ops / replay / neg reject | ALG-0002 ops / replay / neg reject | ALG-0003 ops / replay / neg reject | ALG-0004 ops / replay / neg reject | ALG-0011 ops / replay / neg reject | ALG-0012 ops / replay / neg reject | ALG-0005 ops / replay / neg reject | ALG-0006 ops / replay / neg reject | ALG-0009 ops / replay / neg reject | ALG-0010 ops / replay / neg reject |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `noise.json` | 544 / 4 of 4 / 3 of 3 | 214 / 4 of 4 / 3 of 3 | 261 / 4 of 4 / 3 of 3 | 1325 / 4 of 4 / 3 of 3 | 1365 / 4 of 4 / 3 of 3 | 1461 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `parallel_ab_cd.json` | 544 / 4 of 4 / 3 of 3 | 240 / 4 of 4 / 3 of 3 | 243 / 4 of 4 / 3 of 3 | 1301 / 4 of 4 / 3 of 3 | 1341 / 4 of 4 / 3 of 3 | 1437 / 4 of 4 / 3 of 3 | 281 / 4 of 4 / 3 of 3 | 208 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 312 / 4 of 4 / 3 of 3 |
| `sequence.json` | 499 / 3 of 3 / 3 of 3 | 211 / 3 of 3 / 3 of 3 | 168 / 3 of 3 / 3 of 3 | 804 / 3 of 3 / 3 of 3 | 842 / 3 of 3 / 3 of 3 | 890 / 3 of 3 / 3 of 3 | 228 / 3 of 3 / 3 of 3 | 181 / 3 of 3 / 3 of 3 | 190 / 3 of 3 / 3 of 3 | 239 / 3 of 3 / 3 of 3 |
| `short_loop.json` | 211 / 1 of 3 / 1 of 3 | 118 / 1 of 3 / 1 of 3 | 191 / 0 of 3 / 3 of 3 | 316 / 1 of 3 / 3 of 3 | 327 / 1 of 3 / 3 of 3 | 357 / 1 of 3 / 3 of 3 | 186 / 3 of 3 / 3 of 3 | 110 / 1 of 3 / 1 of 3 | 113 / 1 of 3 / 1 of 3 | 139 / 1 of 3 / 1 of 3 |
| `skip.json` | 251 / 2 of 4 / 3 of 3 | 144 / 2 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 332 / 4 of 4 / 1 of 3 | 368 / 4 of 4 / 3 of 3 | 432 / 4 of 4 / 3 of 3 | 175 / 4 of 4 / 3 of 3 | 132 / 2 of 4 / 3 of 3 | 139 / 4 of 4 / 3 of 3 | 187 / 4 of 4 / 3 of 3 |
| `xor.json` | 552 / 4 of 4 / 3 of 3 | 228 / 4 of 4 / 3 of 3 | 194 / 4 of 4 / 3 of 3 | 730 / 4 of 4 / 3 of 3 | 770 / 4 of 4 / 3 of 3 | 844 / 4 of 4 / 3 of 3 | 235 / 4 of 4 / 3 of 3 | 204 / 0 of 4 / 3 of 3 | 216 / 4 of 4 / 3 of 3 | 284 / 4 of 4 / 3 of 3 |

Semantic and structural interpretation:

- `ALG-0003` passes sequence, XOR, parallel, skip, and noise smoke families with clean structural diagnostics, and EXP-0008 showed the bounded optional-concurrency cut is causal for `parallel_with_optional_branch`.
- `ALG-0004` completes the required region-inspired comparator family as an executable bounded visible-place search. It passes sequence, XOR, parallel, and noise, but is high cost and overgeneralizes optional behavior (`skip.json` rejects only 1/3 negatives; `overlapping_optional_skips` rejects 0/3).
- `ALG-0011` repairs the simple skip overgeneralization by accepting optional pattern `A,B,C` on `skip.json`; it improves negative rejection from `ALG-0004`'s 1/3 to 3/3 while preserving 4/4 replay.
- EXP-0013 confirms that repair is causal: the no-repair ablation matches `ALG-0004` on singleton and two-disjoint optional cases, while full `ALG-0011` improves negative rejection to 3/3 in both.
- `ALG-0011` rejects all overlapping optional-chain candidates under its non-single-context guard, so `overlapping_optional_skips` remains 0/3 negative rejection and `parallel_with_optional_branch` remains 1/3.
- `ALG-0012` repairs overlapping optional chains using selected region shortcuts: `overlapping_optional_skips` improves to 4/4 replay and 3/3 negative rejection, but operation count rises to 1037.
- `ALG-0012` still does not repair optional/concurrency: `parallel_with_optional_branch` remains 3/3 replay and 1/3 negative rejection.
- `ALG-0004` loop and duplicate-label behavior remains partial: `short_loop.json`, `short_loop_required`, and `duplicate_label_rework` replay only 1/3 positives.
- `ALG-0005` exactly replays all current smoke and synthetic positives, including loop and duplicate-label cases, but EXP-0010 shows this is exact observed-language memorization: held-out interleavings fail and observed noise is accepted.
- EXP-0015 shows `ALG-0013` matches `ALG-0012` on all current optional-pattern and broader synthetic replay/negative metrics. Savings are only 5-12 operations on chain-emitting cases and zero elsewhere.
- `optional_singleton_parallel_branch` broadens optional/concurrency testing: `ALG-0004`, `ALG-0011`, `ALG-0012`, and `ALG-0013` replay positives but reject only 2/3 negatives; `ALG-0010` replays 3/4 positives; `ALG-0003` replays 0/4 positives.
- EXP-0016 shows `ALG-0014` improves balanced held-out parallel replay from `ALG-0005`'s 0/4 to 4/4 and fixes `optional_singleton_parallel_branch` at 4/4 replay and 3/3 negative rejection.
- EXP-0016 `ALG-0014` smoke summary: `noise.json` 235 ops / 4 of 4 replay / 3 of 3 negative rejection; `parallel_ab_cd.json` 227 / 4 of 4 / 3 of 3; `sequence.json` 272 / 3 of 3 / 3 of 3; `short_loop.json` 248 / 3 of 3 / 3 of 3; `skip.json` 216 / 4 of 4 / 3 of 3; `xor.json` 294 / 4 of 4 / 3 of 3.
- EXP-0016 also shows `ALG-0014` still fails prefix-biased held-out parallel (0/4) and noise memorization (0/1 negative rejection when rare reversal is treated as negative).
- EXP-0017 shows `ALG-0015` fixes prefix-biased held-out parallel: 4/4 held-out replay and 3/3 negative rejection, versus 0/4 held-out replay for `ALG-0014`.
- EXP-0017 shows `ALG-0015` fixes rare-reversal noise precision by selecting `dominant_sequence`: `noise_memorization` negative rejection improves from 0/1 to 1/1, while training replay drops from 4/4 to 3/4.
- EXP-0017 shows `ALG-0016` matches `ALG-0015` on true grammar cases but fails fallback-dependent cases, separating grammar generalization from exact automaton memorization.
- EXP-0018 shows prefix merge is causal for prefix-biased held-out parallel: `ALG-0018`, `ALG-0015`, and `ALG-0016` replay 4/4 held-out traces, while `ALG-0017` and `ALG-0019` replay 0/4.
- EXP-0018 shows dominant-sequence handling is causal for rare-reversal precision: `ALG-0019`, `ALG-0015`, and `ALG-0016` reject 1/1 rare-reversal negatives, while `ALG-0017` and `ALG-0018` fall back to exact replay and reject 0/1.
- EXP-0018 shows support-skew alone changes grammar selection on noisy reversals but does not improve end-to-end precision while exact fallback is enabled.
- EXP-0018 confirms the current dominant-sequence policy is conservative under incomplete parallel evidence: `same_order_incomplete_parallel` held-out replay remains 0/1.
- EXP-0019 shows prefix merge is ambiguous: under a full-parallel interpretation `ALG-0015` replays 4/4 late-B held-out traces and `ALG-0020` replays 0/4, while under a B-then-C/D interpretation `ALG-0015` rejects 0/4 late-B negatives and `ALG-0020` rejects 4/4.
- EXP-0019 shows `max_parallel_support_skew=2` treats 2:1 reversal evidence as parallel; stricter skew 1 treats it as noise via dominant sequence but sacrifices rare-variant replay.
- EXP-0019 shows dominant-ratio 85 is too strict for 3/4 and 5/6 noise cases; ratios 60 and 75 select dominant sequence.
- EXP-0020 shows `ALG-0021` detects ambiguity on the targeted prefix-merge cases and on the prefix-biased held-out stress case while preserving `ALG-0015` selected-net behavior.
- EXP-0020 shows `ALG-0021` does not fire ambiguity evidence on the six toy smoke logs, rare-reversal noise cases, or incomplete one-order parallel cases.
- EXP-0021 shows `ALG-0022` alternative nets bracket the targeted ambiguity: full-parallel alternatives recover 4/4 held-out late-B traces, while sequence-prefix alternatives reject 4/4 late-B negatives under the sequence-prefix interpretation.
- EXP-0021 emits no alternatives on rare-reversal, valid-rare-parallel, incomplete one-order, or balanced reversal controls.
- EXP-0022 shows `ALG-0023` fixes `short_loop.json` and `short_loop_required` from `ALG-0003`'s 0/3 replay to 3/3 replay with 3/3 negative rejection.
- EXP-0022 shows `ALG-0023` replays a held-out second loop iteration, while exact automaton and prefix-block fallback comparators reject it.
- EXP-0022 shows `ALG-0023` does not fire on optional skips, one-iteration-only loop evidence, or multi-body rework controls.
- EXP-0023 shows `ALG-0023` handles prefixed/suffixed singleton rework loops with 3/3 replay, 1/1 held-out replay, and 3/3 negative rejection.
- EXP-0023 shows the same zero/one evidence overgeneralizes under bounded-at-most-one semantics: second iteration is accepted, so negative rejection is 2/3.
- EXP-0023 confirms multi-body loop choice, nested loop-with-choice, and one-iteration-only evidence remain unresolved.
- EXP-0024 shows `ALG-0024` fixes `multi_body_loop_choice`: 3/3 train replay, 2/2 held-out replay, 3/3 negative rejection, and 258 counted operations.
- EXP-0024 shows `ALG-0024` fixes nested sequence-context body choice: 3/3 train replay, 1/1 held-out replay, 3/3 negative rejection, and 349 counted operations.
- EXP-0024 preserves singleton-loop behavior through the `ALG-0023` detector but pays extra rejected-detector overhead (`short_loop.json`: 292 ops versus `ALG-0023` 216).
- EXP-0024 keeps bounded-count ambiguity explicit: `bounded_at_most_one_rework` still rejects only 2/3 negatives because the selected net uses an unbounded-repeat prior.
- EXP-0024 still rejects one-iteration-only loop inference, leaving fallback replay at 0/3 train and 0/2 held-out.
- EXP-0025 shows `ALG-0024` is trace-order stable on checked multi-body, nested-context, and support-imbalance cases.
- EXP-0025 shows length-2 body choices, mixed-width body choices, and duplicate body/suffix label contexts remain outside scope; all fall back with 0/3 train replay.
- EXP-0025 shows bounded-count multi-body priors still fail precision: repeated body combinations are accepted, so negative rejection is 2/4.
- EXP-0025 shows support imbalance is not treated as noise: with body support `B=3`, `C=1`, `ALG-0024` still replays the held-out `C` then `B` combination.
- EXP-0026 shows `ALG-0025` fixes `ALG-0024`'s length-2 body-choice gap: `length2_body_choice` improves from fallback 0/3 train and 0/2 held-out replay to 3/3 train, 2/2 held-out, and 3/3 negative rejection.
- EXP-0026 shows mixed singleton/length-2 body evidence is supported: `mixed_singleton_and_length2_body` gets 3/3 train replay, 1/1 held-out replay, and 3/3 negative rejection.
- EXP-0026 shows singleton-body regression is clean: `singleton_body_regression` matches `ALG-0024` at 3/3 train, 1/1 held-out, 3/3 negative rejection, and 258 counted operations.
- EXP-0026 keeps body length greater than two and overlapping body labels outside scope; both cases fall back with 0/3 train replay and 3/3 negative rejection.
- EXP-0026 confirms the bounded-count ambiguity persists for length-2 bodies: repeated body combinations are accepted, so `bounded_count_length2_prior` rejects only 2/4 negatives.
- EXP-0026 shows `ALG-0025` is trace-order stable on checked length-2 and mixed-width loop-body cases across 6 unique permutations each.
- EXP-0027 shows `ALG-0026` emits loop-count policy sets for singleton, multi-body, contexted multi-body, length-2, and mixed-width loop evidence, and emits no alternatives for one-iteration-only or optional-skip controls.
- EXP-0027 shows unbounded-repeat alternatives replay repeated-iteration held-out probes, while at-most-once alternatives reject those held-out probes but preserve training replay.
- EXP-0027 shows at-most-once alternatives fix bounded-count negative probes: singleton improves from unbounded 2/3 to 3/3 negative rejection; multi-body and length-2 improve from 2/4 to 4/4.
- EXP-0027 keeps `ALG-0026` at `smoke-tested`, not `promising`, because no validation rule, domain prior, or deterministic selector chooses the final loop-count policy.
- EXP-0028 shows `ALG-0027` selects `unbounded_repeat` when validation positives include repeated loop iterations and validation negatives contain only structural invalid traces.
- EXP-0028 shows `ALG-0027` selects `at_most_once` when validation negatives mark repeated loop iterations invalid and no validation positive requires repetition.
- EXP-0028 shows the selector leaves non-discriminating validation unresolved, detects contradictory validation overlap as `validation_inconsistent`, and returns `no_policy_set` on optional-skip controls.
- EXP-0029 adds validation replay proxy counts to `ALG-0027`: one `scan_event` per validation event and one `comparison` per validation trace per policy alternative.
- EXP-0029 split validation/final protocol passes nine cases, including singleton, multi-body, length-2, mixed-width, non-discriminating, optional-skip no-policy-set, and deliberate leakage controls.
- EXP-0029 shows final probes remain unused for selection: `no_discriminator_remains_unresolved` stays unresolved even though final probes contain a repeated-loop positive.
- EXP-0029 promotes `ALG-0027` to `promising`, not `deep-testing`, because one-iteration-only, duplicate-label, length >2, and noisy rare-body limits remain untested and the validation replay count is a proxy.
- EXP-0030 shows `ALG-0027` correctly returns `no_policy_set` for one-iteration-only, duplicate body/suffix label, length >2 body, and overlapping-body-label cases.
- EXP-0030 shows rare-body valid behavior can still select `unbounded_repeat`, but rare-body-as-noise remains a gap because loop-count selection does not remove an observed rare body from the language.
- EXP-0030 keeps `ALG-0027` at `promising`, not `deep-testing`, and makes rare-body support/noise the next candidate line.
- EXP-0031 shows `ALG-0028` filters singleton rare bodies under a 3-count / 75-percent dominant support prior, improving rare-body-noise negative rejection while intentionally losing replay on filtered observed traces.
- EXP-0031 also shows valid rare behavior can have the same 3:1 support pattern, so `ALG-0028` is a precision-prior candidate and not an identifiable discovery claim.
- EXP-0032 shows `ALG-0028` threshold tradeoffs: 2:1 rejects 15/17 rare-noise probes but replays 0/10 valid-rare positives; default 3:1 rejects 10/17 and replays 3/10; 4:1 rejects 8/17 and replays 5/10; 5:1 rejects 4/17 and replays 8/10.
- EXP-0032 shows `ALG-0029` can select `keep_all_bodies` when validation positives require the rare body, select `support_guard` when validation negatives reject rare-body combinations, and return unresolved/conflict statuses for no-signal, training-conflict, and inconsistent-validation cases.
- EXP-0033 shows `ALG-0029` split validation/final protocol passes 10/10 cases, including keep/filter selection, no-signal unresolved, leakage detection, 5:1 support-ratio keep, length-2 rare-body filtering, mixed rare-body unresolved, and rare-count-two unresolved controls.
- EXP-0033 adds `ALG-0030`: all four body-inclusion x count-policy product quadrants pass, and one-axis-unresolved controls stay unresolved.
- EXP-0034 stress-tests `ALG-0030`: 4/4 length-2 product quadrants, 8/8 mixed-width product quadrants, 4/4 blocked-scope controls, and 4/4 rare-count-two controls pass.
- EXP-0034 adds `ALG-0031`: a configured rare-count-two support-prior ablation can filter count-two rare-body noise under validation and can be overridden by validation to keep rare behavior, but group filtering fails one-valid/one-noisy rare-body controls.
- EXP-0035 adds `ALG-0032`: per-body inclusion vectors repair one-valid/one-noisy rare-body cases for count-one and configured count-two policies where `ALG-0029` remains unresolved.
- EXP-0035 shows `ALG-0032` keeps both rare bodies when both are validated, drops both when both are rejected, and stays unresolved when validation only probes one rare body.
- EXP-0035 shows `ALG-0032` detects `validation_inconsistent`, `validation_training_conflict`, `dominance_threshold_not_met`, and `too_many_rare_bodies` controls.
- EXP-0036 broadens `ALG-0032` to split validation/final testing: 13/13 cases pass, including singleton, length-2, mixed-width, configured count-two, cap-boundary, leakage, and blocked-scope controls.
- EXP-0036 confirms `ALG-0029` and `ALG-0030` remain unresolved on mixed valid/noisy rare-body cases where `ALG-0032` selects a per-body vector.
- EXP-0036 exposes operation-cost pressure: the cap-three case enumerates eight alternatives and reports a naive total of 7430 operations on a toy log.
- EXP-0037 adds shared operation accounting for the validation selectors: `ALG-0029` max protocol total drops from 1503 naive to 934 shared, `ALG-0030` from 962 to 638, and `ALG-0032` cap-three from 7430 to 3167.
- EXP-0038 integrates those shared totals into selector outputs and verifies them with report cross-checks; validation replay proxy costs remain per alternative, and primitive-level shared breakdowns are still missing.
- EXP-0039 stress-tests the `ALG-0032` cap path: selected one-rare-body cases stay under the deep soft budget, selected two-or-more-rare-body cases exceed it, and cap-plus-one refusals stay cheap with zero alternatives.
- EXP-0040 adds `ALG-0033`: direct validation signals and one-step unit propagation preserve core `ALG-0032` mixed rare-body wins while avoiding exhaustive assignment enumeration. The direct-signal R=5 reference stays under the deep soft budget, but non-unit ambiguous negatives are deliberately unresolved.
- `ALG-0003`, `ALG-0009`, `ALG-0011`, and `ALG-0015` are `deep-testing`. `ALG-0005`, `ALG-0010`, `ALG-0012`, `ALG-0014`, `ALG-0023`, `ALG-0024`, `ALG-0025`, and `ALG-0027` are `promising`. `ALG-0013`, `ALG-0016`, `ALG-0017`, `ALG-0018`, `ALG-0019`, `ALG-0020`, `ALG-0021`, `ALG-0022`, `ALG-0026`, `ALG-0028`, `ALG-0029`, `ALG-0030`, `ALG-0031`, `ALG-0032`, and `ALG-0033` are `smoke-tested`. `ALG-0004` is `benchmarked`. No candidate is `super-promising`.

## Next action

Continue the first goal by prioritizing:

1. Broaden `ALG-0033` into a split validation/final protocol matching `ALG-0032`'s length-2, mixed-width, configured count-two, leakage, cap, and blocked-scope controls.
2. Add reference-only direct-signal R=3/R=5 comparisons against `ALG-0032` where runtime remains acceptable, while keeping non-unit interaction clauses as explicit unresolved cases.
3. Add primitive-level shared breakdowns for `ALG-0029`/`ALG-0030`/`ALG-0032`/`ALG-0033`, or explicitly decide that total-field accounting is sufficient only for smoke-stage evidence.
4. Add broader non-toy validation only after the cost and attribution assumptions are clearer, and keep duplicate-label, length >2, and one-iteration-only loop compilation as separate bounded candidates.

## Current candidate focus

- `ALG-0001`: baseline, smoke-tested.
- `ALG-0002`: dependency-threshold baseline, smoke-tested, lower operation counts but not promoted because of unconstrained-transition diagnostics.
- `ALG-0003`: deep-testing block-structured baseline; next targets are loop/duplicate-label decisions and broader optional-concurrency tests.
- `ALG-0004`: benchmarked visible-place region comparator; next decision is bounded silent optional-place refinement versus retaining as a negative comparator.
- `ALG-0005`: promising exact automaton/grammar comparator; stress-tested for overfitting and variant growth, next target is abstraction/refinement.
- `ALG-0006`: smoke-tested starter candidate, lower counted operations but not promoted because XOR replay is disproven.
- `ALG-0009`: deep-testing guarded PMIR variant; next target is conflict-aware optional guard refinement.
- `ALG-0010`: promising conflict-aware optional-chain variant; fixes overlapping optional skips but not optional/concurrency.
- `ALG-0011`: deep-testing narrow region optional-tau repair; fixes singleton and two-disjoint optional skip precision but not overlapping optional chains or optional/concurrency.
- `ALG-0012`: promising chain-aware region repair; fixes overlapping optional chains but is high-cost and does not solve optional/concurrency.
- `ALG-0013`: smoke-tested no-certification ablation of `ALG-0012`; current behavior matches `ALG-0012` with only tiny operation savings, so it is not promoted.
- `ALG-0014`: promising prefix block abstraction; fixes balanced held-out parallel and optional-singleton parallel, but needs support/noise guards and prefix-bias handling.
- `ALG-0015`: deep-testing support-guarded prefix block abstraction; fixes prefix bias and rare-reversal precision, but trades away rare-trace replay and still uses exact fallback.
- `ALG-0016`: smoke-tested grammar-only ablation of `ALG-0015`; useful for separating grammar behavior from fallback memorization.
- `ALG-0017`: smoke-tested support-skew-only ablation of `ALG-0015`; useful as a control, not promoted.
- `ALG-0018`: smoke-tested prefix-merge ablation of `ALG-0015`; shows prefix merge is causal for prefix-biased held-out recovery.
- `ALG-0019`: smoke-tested dominant-sequence ablation of `ALG-0015`; shows dominant-sequence handling is causal for rare-reversal precision.
- `ALG-0020`: smoke-tested conservative prefix-merge tradeoff; protects sequence-prefix precision but loses full-parallel held-out recovery.
- `ALG-0021`: smoke-tested ambiguity-aware PMIR refinement; records common-boundary and prefix-merge alternatives but does not yet improve selected-net quality.
- `ALG-0022`: smoke-tested ambiguity-set protocol; compiles alternatives into separate Petri nets and confirms the targeted ambiguity requires an external selector.
- `ALG-0023`: promising bounded loop refinement of `ALG-0003`; fixes single-anchor rework loops under an unbounded-loop prior but does not cover bounded-count, multi-body, nested-choice, or one-iteration-only loop evidence.
- `ALG-0024`: promising multi-body loop-choice refinement of `ALG-0023`; fixes singleton-body choice loops under an unbounded-loop prior and is trace-order stable on checked cases, but not bounded-count, one-iteration-only, longer body-sequence, duplicate-label, or rare-body/noise cases.
- `ALG-0025`: promising length-bounded body-loop refinement of `ALG-0024`; fixes body alternatives of length at most two and mixed singleton/length-2 loop bodies, but not bounded-count, length >2, duplicate-label, one-iteration-only, or support/noise cases.
- `ALG-0026`: smoke-tested loop-count policy-set protocol; preserves unbounded-repeat and at-most-once alternatives for bounded-count ambiguous loop evidence but does not select a final policy.
- `ALG-0027`: promising loop-count validation selector; selects only when explicit validation probes uniquely distinguish `ALG-0026` alternatives, passes split validation/final tests, and reports validation replay proxy counts. EXP-0030 shows upstream detector limits and rare-body/noise ambiguity block deep-testing.
- `ALG-0028`: smoke-tested body-support guard over `ALG-0025`; improves precision on singleton rare-body noise but drops valid rare behavior under the same 3:1 support pattern, so next work is threshold ablation or external body-inclusion validation.
- `ALG-0029`: smoke-tested body-inclusion validation selector; split validation/final tests pass and EXP-0038 integrates max shared protocol cost at 934, but mixed rare-body and rare-count-two limits plus non-primitive shared accounting block promotion.
- `ALG-0030`: smoke-tested body-count product selector; selects product policies over body inclusion and loop count on singleton, length-2, and mixed-width controlled cases, and EXP-0038 integrates max conservative shared product cost at 638, but blocked upstream limits and primitive-level accounting still block promotion.
- `ALG-0031`: smoke-tested rare-count-two support-prior ablation; useful control for count-two rare noise, but group filtering cannot handle mixed valid/noisy rare bodies.
- `ALG-0032`: smoke-tested per-body rare inclusion validation selector; repairs controlled mixed rare-body cases and passes split validation/final controls. EXP-0039 shows exhaustive selected enumeration exceeds the deep soft budget from two rare bodies onward, while cap-plus-one refusals stay cheap. It remains capped, validation-scoped, and not yet primitive-level in shared accounting.
- `ALG-0033`: smoke-tested per-body direct-signal validation selector; keeps the mixed rare-body repair path under budget by avoiding exhaustive enumeration, but it is narrower than `ALG-0032` and leaves non-unit ambiguous negative clauses unresolved.

## Decisions to preserve

- Keep the agent generic across process-mining research topics.
- For the first task, use Petri-net discovery under a limited-operation model as a concrete benchmark.
- Every candidate algorithm must be tracked, including failed and retired candidates.
- Do not promote `ALG-0006` without replay/semantic validation.
- Do not promote any candidate on positive-trace replay alone; structural diagnostics and negative traces are required.
- `ALG-0009` is promising only for the currently tested simple sequence/XOR/parallel/skip/noise scope; short loops and nested structures remain open.
- `ALG-0009` should not be called super-promising until overlapping optional and optional-concurrency counterexamples are repaired or explicitly scoped out.
- `ALG-0010` should be compared against a block-structured baseline before further promotion; its operation cost is higher than `ALG-0009`.
- `ALG-0003` is deep-testing only for simple accepted blocks and common sequence context; do not present it as a recursive inductive miner yet.
- The `ALG-0003` bounded optional-concurrency cut is causal for `parallel_with_optional_branch` but narrow.
- `ALG-0005` requires labeled visible transitions; evaluator now supports optional `transition_labels` while preserving legacy `t_<activity>` behavior.
- `ALG-0005` should not be promoted without an abstraction/refinement; EXP-0010 shows held-out failure and noise memorization.
- `ALG-0004` should not be promoted without resolving optional overgeneralization or demonstrating a clear advantage over existing block/PMIR/automaton comparators.
- `ALG-0011` should not be promoted beyond `deep-testing` until overlapping optional-chain and optional/concurrency failures are repaired or formally scoped out, and its high operation cost is justified by a clear advantage.
- `ALG-0012` should not move beyond `promising` without selected-shortcut-certification ablation evidence and a clearer cost/quality advantage over `ALG-0010` or `ALG-0003`.
- EXP-0015 supplied selected-shortcut-certification ablation evidence for `ALG-0012`, but did not show a clearer cost/quality advantage; keep `ALG-0012` at `promising`.
- `ALG-0013` should remain an ablation unless counterexample search shows selected-region certification is redundant or harmful.
- `ALG-0014` should not move beyond `promising` until exact-fallback memorization is separated from true grammar generalization and rare-reversal noise no longer triggers an unsupported parallel block.
- `ALG-0015` should not move beyond `deep-testing` until broader noisy/incomplete threshold sweeps, prefix-merge false-positive search, and loop/fallback-scope decisions are complete.
- `ALG-0016` is an ablation only; do not promote it unless grammar coverage expands substantially.
- `ALG-0017`, `ALG-0018`, and `ALG-0019` are ablation controls only; do not promote them independently unless they become intentionally scoped candidates with their own advantage.
- `ALG-0020` is a tradeoff candidate only; do not promote it unless an explicit ambiguity-aware selection rule or domain prior makes its conservative choice preferable.
- `ALG-0025` should not move beyond `promising` until bounded-count loop priors, length >2 body scaling, duplicate-label body contexts, one-iteration-only evidence, and rare-body/noise policy have been tested or explicitly scoped out.
- `ALG-0026` should not move beyond `smoke-tested` without a deterministic selector, validation rule, or explicit domain-prior mechanism for choosing between unbounded-repeat and at-most-once alternatives.
- `ALG-0027` should not move beyond `promising` until a separate body-support/noise policy exists or is explicitly scoped out, and validation replay cost is refined beyond the current proxy.
- `ALG-0028` should not move beyond `smoke-tested` until support-threshold ablations and valid rare-body controls show a reliable selector or external-validation mechanism; support alone is a precision prior, not evidence that a rare body is noise.
- `ALG-0029` should not move beyond `smoke-tested` until shared accounting is primitive-level, and mixed rare-body / rare-count-two limits are addressed or scoped out.
- `ALG-0030` should not move beyond `smoke-tested` despite passing length-2, mixed-width, duplicate-label, length >2, and one-iteration-only stress controls; primitive-level shared accounting and upstream blocked-scope repairs remain unresolved.
- `ALG-0031` should not move beyond `smoke-tested`; count-two rare-body filtering is a policy prior and needs per-body alternatives or validation/domain priors before stronger claims.
- `ALG-0032` should not move beyond `smoke-tested` until shared accounting is primitive-level and either exhaustive enumeration is replaced by a lower-cost bounded rule or the claim is narrowed to one rare body under the declared budget.
- `ALG-0033` should not move beyond `smoke-tested` until split validation/final controls cover length-2, mixed-width, configured count-two, leakage, cap, and blocked-scope cases, and until validation-negative attribution assumptions are made explicit.
- `ALG-0021` is an evidence/PMIR refinement only; do not promote it unless a downstream selector, domain prior, or multi-net protocol uses the ambiguity annotation to improve decisions.
- `ALG-0022` is a model-set protocol only; do not promote it without a deterministic selector or explicit multi-objective acceptance criterion.
- `ALG-0023` should remain the singleton-loop reference candidate; do not move it beyond `promising` until bounded-count and one-iteration-only semantics are resolved or formally scoped out.
- `ALG-0024` should not move beyond `promising` until longer body sequences, duplicate-label body contexts, bounded-count priors, and trace-order stability are tested; its unbounded-repeat prior is not identified by zero/one evidence alone.

## Blockers / unknowns

- Need to validate whether the EXP-0007 operation-budget formulas are tight enough after more synthetic cases.
- Need to decide whether to install PM4Py/ProM for standard metrics or keep early prototypes dependency-free.
- Need broader negative-trace precision tests and a non-trivial synthetic benchmark suite before any `super-promising` decision.

## Resume checklist

1. Read `AGENTS.md`.
2. Read this file.
3. Read `MEMORY.md` and `PLAN.md`.
4. Read `research/ALGORITHM_REGISTRY.md` and `research/EXPERIMENT_LOG.md`.
5. Continue from `Next action` unless the user gives a new goal.
