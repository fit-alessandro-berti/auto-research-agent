# PLAN.md

Phase-gated plan for the process-mining research agent. Update status as work proceeds.

## Phase 0 — Initialize research context

Status: complete for `first-petri-net-limited-ops`

Acceptance criteria:

- Active goal selected.
- Operation model and constraints written down.
- Candidate registry has at least initial baseline families.
- Smoke-test logs are available.

## Phase 1 — Candidate enumeration

Status: complete for first iteration

Acceptance criteria:

- At least six candidate families listed.
- Each candidate has ID, hypothesis, intermediate representation, operation-cost expectation, failure risks, and first test.
- Baselines are included.

## Phase 2 — Baseline harness

Status: extended and smoke-validated

Acceptance criteria:

- `scripts/benchmark.py` runs on toy logs.
- Each run records operation counts and a machine-readable result.
- Petri-net/PMIR artifacts can be serialized to JSON.
- EXP-0004 additionally records strict token-game replay, bounded silent-transition closure, negative-trace probes, and visible-transition structural diagnostics.

## Phase 3 — First prototypes

Status: active, first iteration extended with all required comparator families executable or intentionally risky

Acceptance criteria:

- Implement 2–3 low-cost candidates.
- Run smoke tests.
- Record failures and counterexamples.
- Promote or retire candidates according to evidence.

Progress:

- Executable and smoke-tested or benchmarked: `ALG-0001`, `ALG-0002`, `ALG-0003`, `ALG-0004`, `ALG-0005`, `ALG-0006`, `ALG-0009`, `ALG-0010`, `ALG-0011`, `ALG-0012`, `ALG-0013`, `ALG-0014`, `ALG-0015`, `ALG-0016`, `ALG-0017`, `ALG-0018`, `ALG-0019`, `ALG-0020`, `ALG-0021`, `ALG-0022`, `ALG-0023`, `ALG-0024`, `ALG-0025`, `ALG-0026`, `ALG-0027`, `ALG-0028`, `ALG-0029`, `ALG-0030`.
- Specified but not executable among required first comparator families: none. `ALG-0007` and `ALG-0008` remain risky idea-stage side candidates.
- `ALG-0009` promoted to `promising` in EXP-0004 and moved to `deep-testing` in EXP-0005; `ALG-0010` promoted to `promising` in EXP-0006; `ALG-0003` promoted to `promising` in EXP-0007 and moved to `deep-testing` in EXP-0008; `ALG-0005` promoted to `promising` in EXP-0009; `ALG-0004` implemented and benchmarked in EXP-0011 but not promoted; `ALG-0011` promoted to `promising` in EXP-0012 and moved to `deep-testing` in EXP-0013; `ALG-0012` promoted to `promising` in EXP-0014 and kept there after EXP-0015; `ALG-0013` added as a smoke-tested ablation in EXP-0015; `ALG-0014` promoted to `promising` in EXP-0016; `ALG-0015` promoted to `promising` in EXP-0017 and moved to `deep-testing` in EXP-0018; `ALG-0016` added as a smoke-tested ablation in EXP-0017; `ALG-0017`, `ALG-0018`, and `ALG-0019` added as smoke-tested ablations in EXP-0018; `ALG-0020` added as a smoke-tested tradeoff candidate in EXP-0019; `ALG-0021` added as a smoke-tested ambiguity-evidence PMIR refinement in EXP-0020; `ALG-0022` added as a smoke-tested ambiguity-set protocol in EXP-0021; `ALG-0023` added and promoted to `promising` in EXP-0022; `ALG-0024` added and promoted to `promising` in EXP-0024; `ALG-0025` added and promoted to `promising` in EXP-0026; `ALG-0026` added as a smoke-tested loop-count policy-set protocol in EXP-0027; `ALG-0027` added as a smoke-tested validation selector in EXP-0028 and promoted to `promising` in EXP-0029; `ALG-0028` added as a smoke-tested body-support guard in EXP-0031; `ALG-0029` added as a smoke-tested body-inclusion validation selector in EXP-0032 and split-tested in EXP-0033; `ALG-0030` added as a smoke-tested body-count product selector in EXP-0033; `ALG-0001`, `ALG-0002`, and `ALG-0006` remain unpromoted baselines/counterexamples.

## Phase 4 — Deep testing of promising candidates

Status: active for `ALG-0009`, `ALG-0011`, and `ALG-0015`; started for comparator candidates

Acceptance criteria:

- Run broader synthetic logs with controlled noise, missing behavior, duplicated labels, loops, choices, and concurrency.
- Compare against baselines.
- Run ablations and parameter sweeps.
- Measure runtime and operation counts.

Progress:

- EXP-0005 ran ablations and seven synthetic counterexample families.
- `ALG-0009` was stable under checked trace-order permutations.
- Material failures remain for overlapping optional skips, optional branches mixed with concurrency, short loops, and duplicate labels.
- EXP-0006 added `ALG-0010`, fixing overlapping optional skips but not optional/concurrency.
- EXP-0007 added `ALG-0003` to the synthetic runner. It handles nested XOR and overlapping optional skips, but initially failed optional-concurrency, short-loop, and duplicate-label cases through fallback.
- EXP-0008 added a bounded optional-concurrency cut and ablation to `ALG-0003`; `parallel_with_optional_branch` now replays 3/3 with 3/3 negative rejection, while the ablation still fails 0/3.
- EXP-0009 added `ALG-0005` to the smoke and synthetic runners. It exactly replays all current positive traces and rejects all current negative probes, including loop and duplicate-label cases, but is treated as an overfitting comparator.
- EXP-0010 stress-tested `ALG-0005`: it rejects held-out valid interleavings, memorizes observed noise, and shows fast raw-trie growth under full permutation variants. It remains `promising`.
- EXP-0011 added `ALG-0004` to the smoke and synthetic runners. It recovers visible places for sequence, XOR, parallel, and noise, but remains `benchmarked` because optional skips overgeneralize, loops remain partial, and operation counts are high.
- EXP-0012 added `ALG-0011` to the smoke and synthetic runners. It fixes the simple `skip.json` precision failure of `ALG-0004` using one accepted optional tau pattern, but does not repair overlapping optional chains or optional/concurrency.
- EXP-0013 added a no-repair ablation and broader optional-pattern tests for `ALG-0011`. The repair is causal for singleton and two-disjoint optional skips, but overlapping optional chains and optional/concurrency still fail.
- EXP-0014 added `ALG-0012`, a chain-aware region repair. It fixes overlapping optional chains but costs more than `ALG-0010` and still does not repair optional/concurrency.
- EXP-0015 added `ALG-0013`, the no-certification ablation of `ALG-0012`, and a new optional-concurrency probe. The ablation matched `ALG-0012` with only tiny operation savings; `optional_singleton_parallel_branch` exposed a new optional/concurrency gap for `ALG-0003`, `ALG-0010`, and the region variants.
- EXP-0016 added `ALG-0014`, a prefix block abstraction refinement of `ALG-0005`. It fixes balanced held-out parallel interleavings and `optional_singleton_parallel_branch`, but it still fails prefix-biased held-out parallel and rare reversal noise.
- EXP-0017 added `ALG-0015`, a support-guarded refinement of `ALG-0014`, and `ALG-0016`, the grammar-only ablation. `ALG-0015` fixes prefix-biased held-out parallel and rare-reversal precision, but trades away rare-trace replay and still relies on exact fallback for many cases.
- EXP-0018 added `ALG-0017`, `ALG-0018`, and `ALG-0019` feature ablations. Prefix merge is causal for prefix-biased held-out replay, dominant-sequence handling is causal for rare-reversal precision, and support-skew alone is only a selection guard while exact fallback remains enabled.
- EXP-0019 added `ALG-0020`, a conservative prefix-merge tradeoff candidate, and broadened noisy/incomplete sweeps. It shows prefix merge is ambiguous under the same observed traces and that support-skew 1 versus 2 controls 2:1 noise behavior.
- EXP-0020 added `ALG-0021`, an ambiguity-aware PMIR refinement. It detects the prefix-merge ambiguity in targeted cases while preserving `ALG-0015` selected-net behavior, so it is not promoted beyond smoke-tested.
- EXP-0021 added `ALG-0022`, an ambiguity-set protocol. It compiles `ALG-0021` alternatives and confirms that the full-parallel and sequence-prefix policies optimize different probes on the same observations.
- EXP-0022 added `ALG-0023`, a bounded single-rework loop cut. It fixes `short_loop_required` and `duplicate_label_rework` with 3/3 replay and 3/3 negative rejection, and replays a held-out second loop iteration.
- EXP-0023 stress-tested `ALG-0023`. Prefix/suffix singleton-loop context works, but bounded-at-most-one, multi-body, nested-choice, and one-iteration-only loop evidence block deeper promotion.
- EXP-0024 added `ALG-0024`, a multi-body rework-loop cut. It fixes multi-body and nested-context loop-choice replay with held-out body-combination generalization, while preserving singleton-loop behavior through the `ALG-0023` detector.
- EXP-0025 stress-tested `ALG-0024`. Trace-order stability holds on checked cases, but length-2 body choices, mixed-width body choices, duplicate body/suffix labels, bounded-count priors, and support/noise policy remain unresolved.
- EXP-0026 added `ALG-0025`, a length-bounded multi-body rework-loop cut. It fixes length-2 and mixed singleton/length-2 body-loop choices with held-out body-combination generalization and stable checked trace ordering, while keeping bounded-count priors, length >2, duplicate labels, and support/noise policy unresolved.
- EXP-0027 added `ALG-0026`, a loop-count policy-set protocol. It emits unbounded-repeat and at-most-once alternatives from the same bounded-count ambiguous loop evidence and shows those alternatives bracket held-out repeat generalization versus bounded-count negative rejection.
- EXP-0028 added `ALG-0027`, a validation selector over `ALG-0026` alternatives. It selects a loop-count policy only when explicit validation positives/negatives uniquely identify one, and leaves ties, conflicts, or no-policy-set cases unresolved.
- EXP-0029 added validation replay proxy counts to `ALG-0027` and ran frozen train/validation/final-test protocol cases. It promotes `ALG-0027` to `promising` within its explicit external-validation scope, while keeping final probes out of selector choice.
- EXP-0030 stress-tested `ALG-0027` against upstream limits. One-iteration-only, duplicate-label, length >2, and overlapping body-label cases emit no policy set; rare-body/noise validity remains outside loop-count selection.
- EXP-0031 added `ALG-0028`, a body-support guard over `ALG-0025`. It filters singleton rare loop bodies only under 3-count / 75-percent dominant support, improves rare-body-noise precision, preserves balanced and 2:1 ambiguity, and documents valid rare-body failure under the same support pattern.
- EXP-0032 swept `ALG-0028` thresholds from 2:1 through 5:1. Higher thresholds recover more valid rare behavior but reject less rare-body noise. EXP-0032 also added `ALG-0029`, a validation selector that chooses keep-all versus support-guarded body inclusion only when validation probes distinguish them.
- EXP-0033 added split validation/final tests for `ALG-0029`: 10/10 cases passed, including keep/filter selection, leakage controls, 5:1 support-ratio keep, length-2 rare-body filtering, and unresolved rare-count-two / mixed rare-body controls.
- EXP-0033 added `ALG-0030`, a body-count product selector. All four body-inclusion x count-policy quadrants passed, and one-axis-unresolved controls remained unresolved.

## Phase 5 — Refinement loop

Status: started with `ALG-0010` and block-structured comparator work

Acceptance criteria:

- For each promising candidate, produce at least one refined variant or a justified retirement.
- Explain what changed and why.
- Retest all refined variants.

Progress:

- `ALG-0010` is the first refinement split from `ALG-0009`.
- It improves one material counterexample but introduces higher operation counts and keeps optional/concurrency failures.
- `ALG-0003` now has the explicit bounded optional-concurrency cut; loop/duplicate-label handling was split into `ALG-0023` and multi-body loop choice into `ALG-0024`, so next `ALG-0003` family choices are broader optional-concurrency composition or deeper loop stress tests for the split candidates.
- `ALG-0005` supplies the automaton/grammar comparator; next work should add an abstraction/refinement before further promotion.
- `ALG-0014` is the first grammar/block refinement of `ALG-0005`; next work should add support thresholds, a prefix-bias guard/merge, and an exact-fallback ablation.
- `ALG-0015` is the current automaton/grammar refinement focus; EXP-0019 completed an initial noisy/incomplete threshold sweep and prefix-merge false-positive search, and EXP-0020 added ambiguity-aware PMIR evidence.
- `ALG-0016` is the exact-fallback-disabled ablation; keep it as a comparator, not a promoted candidate.
- `ALG-0017`, `ALG-0018`, and `ALG-0019` are feature-ablation controls for support-skew, prefix merge, and dominant-sequence behavior; keep them as controls in future `ALG-0015` sweeps.
- `ALG-0020` is a conservative prefix-merge tradeoff candidate; keep it as a comparator for ambiguity-aware PMIR decisions, not as a promoted replacement.
- `ALG-0021` is the ambiguity-aware PMIR version of the prefix-block line.
- `ALG-0022` is the multi-net ambiguity-set protocol; next work should add an explicit selector/validation policy or pivot to bounded loop support as a separate candidate line.
- `ALG-0023` is the singleton loop-support split from `ALG-0003`; keep it as the reference for unbounded single-body rework loops.
- `ALG-0024` is the singleton-body multi-body loop-choice split from `ALG-0023`; keep it as the lower-cost reference for singleton body alternatives.
- `ALG-0025` is the length-bounded body-loop split from `ALG-0024`; EXP-0026 keeps it at `promising`, so next work should split bounded-count loop policy sets, duplicate-label body compilation, length >2 scaling, or support/noise guards rather than promoting it.
- `ALG-0026` is the loop-count model-set protocol for the `ALG-0023`/`ALG-0024`/`ALG-0025` line; keep it as a smoke-tested protocol until a selector, validation rule, or domain prior is added.
- `ALG-0027` is the explicit-validation selector for `ALG-0026`; EXP-0029 promotes it to `promising` after split validation/final tests and validation replay proxy accounting. EXP-0030 keeps it below `deep-testing`, so next work should split rare-body support/noise policy or refine replay-cost accounting rather than broadening its claim.
- `ALG-0028` is the first rare-body support/noise policy for the `ALG-0025` loop line; keep it at `smoke-tested` until threshold ablations and valid rare-body controls show whether a selector or external validation signal can avoid dropping legitimate rare behavior.
- `ALG-0029` is the body-inclusion validation selector for the `ALG-0025`/`ALG-0028` line; EXP-0033 completed split validation/final tests, but keep it at `smoke-tested` until validation replay cost is refined and mixed rare-body / rare-count-two limits are addressed.
- `ALG-0030` is the body-count product selector over `ALG-0029` and `ALG-0026` alternatives; keep it at `smoke-tested` until product selection is stress-tested on wider body shapes, duplicate-label limits, and shared-cost accounting.
- `ALG-0004` completes the required region-inspired comparator family as a solver-free visible-place implementation. Next work is either a small silent optional-place refinement or retirement as a documented negative comparator.
- `ALG-0011` is the small silent optional-place refinement. EXP-0013 added an ablation; next work should decide whether chain-aware optional repair belongs in a region variant or in the existing `ALG-0010` chain compiler family.
- `ALG-0012` is the chain-aware region repair. EXP-0015 added the selected-shortcut-certification ablation (`ALG-0013`) and found no current quality difference. Region repair should pause unless a targeted uncertified-chain counterexample is needed.
- `ALG-0015` should now drive the automaton/grammar refinement loop because it repairs the two main EXP-0016 failures with causal ablation evidence while preserving clear exact-fallback, feature-ablation, and conservative-merge controls.

## Phase 6 — Property study for super-promising candidates

Status: not started

Acceptance criteria:

- Create property dossier.
- Prove, disprove, or mark unknown for each property.
- Run counterexample search.
- Separate formal guarantees from empirical evidence.

## Phase 7 — Research report

Status: not started

Acceptance criteria:

- Summarize candidates, results, and properties.
- Include negative results.
- Include reproduction commands.
- Include next research questions.
