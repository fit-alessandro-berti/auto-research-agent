# ALGORITHM_REGISTRY.md

Append-only registry of candidate algorithms. Every candidate, including failures, must be tracked.

## Status vocabulary

`idea -> specified -> implemented -> smoke-tested -> benchmarked -> promising -> deep-testing -> super-promising -> property-studied -> report-ready -> retired`

## Initial candidate families for the first Petri-net goal

| ID | Name | Status | Family | Intermediate format | Main hypothesis | Next test | Decision |
|---|---|---:|---|---|---|---|---|
| ALG-0001 | Alpha-Lite Relations | smoke-tested | Alpha-style relation mining | PMIR relation graph | A direct-follows scan plus simple relation classification can recover basic sequence, choice, and concurrency structures at low operation cost. | Use as baseline for ALG-0009 deep tests; inspect loop/skip repairs separately. | Baseline only; not promoted. EXP-0004 replay/negative probes pass sequence/xor/parallel/noise but skip and short-loop remain partial. |
| ALG-0002 | Frequency-Threshold Dependency Graph | smoke-tested | Heuristic miner style | Dependency graph / PMIR | Counting direct-follows frequencies and filtering low-dependency edges can improve robustness under noise while preserving low operation cost. | Add workflow-net checks and compare against guarded PMIR on broader logs. | EXP-0004 sweep found clean settings for sequence/XOR/parallel/noise, but not skip or short-loop. Not promoted. |
| ALG-0003 | Cut-Limited Process Tree Miner | deep-testing | Inductive miner style | Process tree -> Petri net | Detect a small set of cuts using DFG summaries, then compile a block-structured process tree to a sound Petri net. | Add loop/duplicate-label handling or explicitly scope them out; broaden optional-concurrency beyond one singleton plus one optional length-2 branch. | Promoted in EXP-0007 and moved to deep-testing in EXP-0008 after a bounded optional-concurrency cut fixed `parallel_with_optional_branch` with ablation evidence. Still fails loops and duplicate labels. |
| ALG-0004 | Bounded Place-Candidate Region Miner | benchmarked | Region/ILP-inspired | Place candidates / constraints | A constrained, non-ILP place-candidate search over small presets/postsets may recover useful Petri-net places under an operation budget. | Add optional silent-place patterns or retire as a visible-place-only comparator after broader precision tests. | Implemented and benchmarked in EXP-0011. It recovers sequence/XOR/parallel/noise but is high-cost, overgeneralizes optional behavior, and does not solve loops; not promoted. |
| ALG-0005 | Prefix Automaton Compression Miner | promising | Automaton/grammar | Prefix automaton -> grammar/PMIR -> Petri net | Build a prefix automaton from variants, compress equivalent states cheaply, then synthesize places or blocks. | Implement a grammar/block abstraction or bounded merge ablation; compare held-out recovery against ALG-0003. | Promoted in EXP-0009; EXP-0010 shows exact replay rejects held-out valid interleavings and memorizes noisy observed variants. Retained as overfitting comparator, not a generalizing miner. |
| ALG-0006 | PMIR Split-Join Compiler | smoke-tested | Novel limited-operation PMIR | PMIR blocks + relation evidence | Learn an intermediate split/join skeleton using only scans, sets, comparisons, and construction; compile to Petri net via local split/join places. | Retain as failed counterexample and compare against ALG-0009 ablations. | Starter candidate; low operation counts but disproven XOR replay in EXP-0003. Repaired variant split into ALG-0009. |
| ALG-0007 | Local Pattern Stitcher | idea | Local process models | Frequent local fragments -> Petri net | Discover small reliable fragments and stitch them into a global net, retaining uncertainty annotations. | Define fragment support and conflict resolution. | Risky candidate. |
| ALG-0008 | Evolutionary Tiny-Net Search | idea | Search/evolutionary | Petri net candidates | Under small activity counts, a bounded search may discover nets with good metrics and reveal reusable structural motifs. | Define tiny logs only; use as oracle/counterexample tool. | Counterexample aid, not low-cost default. |
| ALG-0009 | PMIR Guarded Split-Join Compiler | deep-testing | Novel limited-operation PMIR | Guarded PMIR covered-edge compiler -> Petri net | Separating guard detection from residual edge emission can fix XOR and simple skip over-constraint while preserving the low-operation local PMIR strategy. | Refine guard conflict resolution or split a new variant for overlapping optional/concurrency cases. | Promoted in EXP-0004; EXP-0005 deep tests show trace-order stability but failures on overlapping skips, optional concurrency, short loops, and duplicate labels. |
| ALG-0010 | PMIR Conflict-Aware Optional Chain Compiler | promising | Novel limited-operation PMIR | Transitive-reduction optional-chain PMIR -> Petri net | Optional behavior should be compiled from order-consistent chain shortcuts rather than from every local optional triple. | Reduce operation cost and solve optional/concurrency interaction; compare with ALG-0003. | EXP-0006 fixes overlapping optional skips while preserving smoke successes, but regresses optional-concurrency behavior. |
| ALG-0011 | Region Optional-Tau Repair Miner | deep-testing | Region/PMIR hybrid | Place candidates + optional tau fragments | A bounded visible-place region miner can repair simple optional-skip overgeneralization by adding silent skip fragments only when a non-overlapping optional singleton is certified by a selected shortcut place. | Decide whether to add chain-aware optional repair or delegate overlapping optional behavior to ALG-0010-style chain compilation. | Promoted in EXP-0012 for fixing ALG-0004's `skip.json` precision failure and moved to deep-testing in EXP-0013 after a no-repair ablation and optional-pattern counterexamples. High cost and overlapping optional/concurrency failures remain. |
| ALG-0012 | Region Optional-Chain Repair Miner | promising | Region/PMIR hybrid | Place candidates + optional chain fragments | Selected bounded-region shortcut places can certify optional-chain repairs, allowing a region-based miner to handle overlapping optional skips without accepting arbitrary local optional triples. | Search for cases where selected-shortcut certification prevents harmful optional-chain emission; otherwise pivot to ALG-0005 grammar/block abstraction or ALG-0003 optional-concurrency refinement. | Promoted in EXP-0014 for fixing ALG-0011's overlapping optional-chain failure. EXP-0015 ablation showed selected-shortcut certification has no quality effect on current suites and saves only 5-12 operations when disabled; high cost and optional/concurrency failures remain. |
| ALG-0013 | Region Optional-Chain No-Certification Ablation | smoke-tested | Region/PMIR hybrid ablation | Place candidates + uncertified optional chain fragments | If order-consistent optional chains are already safe enough, selected-region-shortcut certification may be unnecessary overhead. | Search for uncertified-chain false positives and compare against ALG-0012 on larger optional/concurrency suites. | Added in EXP-0015 as the `require_region_shortcut=False` ablation of ALG-0012. It matches ALG-0012 behavior on current optional and synthetic suites while saving only tiny counts, so it is not promoted. |
| ALG-0014 | Prefix Block Abstraction Miner | promising | Automaton/grammar refinement | Prefix variants -> block grammar or exact automaton -> Petri net | A small common-boundary grammar abstraction can reduce ALG-0005 overfitting by compiling observed middle-segment permutations as blocks before falling back to exact automaton replay. | Add support guards for noisy reversals and prefix-biased partial permutations; compare against ALG-0003 on held-out interleavings. | Added and promoted in EXP-0016. It fixes balanced held-out parallel interleavings and the new optional-singleton parallel probe, but fails prefix-biased held-out parallel and treats rare reversal noise as a parallel block. |

## Operation-cost model for first iteration

Input-size variables:

- `T`: number of traces.
- `N`: total events.
- `A`: number of distinct activity labels.
- `D`: number of observed direct-follows pairs.
- `V`: number of distinct variants.
- `L`: maximum trace length.
- `P`: prefix states or trie nodes when an automaton candidate is used.
- `k`: fixed bound on preset/postset candidate size.

Allowed counted primitive operations:

- `scan_event`: reading one event or one adjacent event pair during log summarization.
- `dict_increment`: incrementing or recording one counter/map entry.
- `set_insert`: adding one element to a set-like structure.
- `set_lookup`: membership or keyed lookup in a set/map relation.
- `comparison`: equality, threshold, subset, or ordering decision.
- `arithmetic`: one elementary numeric operation used for scores or margins.
- `relation_classification`: assigning a relation/dependency class from counted evidence.
- `construct`: creating a PMIR item, place, transition, arc, marking, or emitted pattern.

Uncounted in this first iteration: Python interpreter overhead, sorting for stable JSON, JSON serialization, dataclass/list membership overhead inside `PetriNet`, and import/module startup. This is a research operation model, not a CPU profiler.

Candidate expected costs under this model:

- `ALG-0001`: `O(N + A^2 + A^(2k) + C^2)` for bounded Alpha pair enumeration and subsumption over candidate pairs `C`.
- `ALG-0002`: `O(N + A^2 + local_branch_checks)` in the implemented full-pair score variant; an observed-edge-only variant could be `O(N + D)`.
- `ALG-0003`: current non-recursive prototype is `O(N + A^2 + T * L^2)` for DFG/relation summaries plus bounded cut checks; a future recursive version is expected around `O(N + A^3)` if decomposition checks remain bounded.
- `ALG-0004`: `O(N + P + A^(2k) * P * k)` with small fixed `k` and no external solver.
- `ALG-0005`: trie build `O(N)`, suffix-signature compression `O(P * signature_cost)`, and automaton-net construction `O(P + E)` over compressed states and automaton edges.
- `ALG-0006`: `O(N + A^2 + sum_v out(v)^2 + sum_v in(v)^2)` for relation classification and local split/join grouping.
- `ALG-0009`: `O(N + A^2 + sum_v out(v)^2 + sum_v in(v)^2 + optional_checks)` with local optional checks bounded by outgoing-degree pairs.
- `ALG-0010`: `O(N * L + A^2 + D^2 + path_checks + local_branch_checks)` for eventual-order evidence, transitive reduction, optional-chain selection, and residual guards.
- `ALG-0011`: `O(N + P + A^(2k) * P * k + A + E)` with the `ALG-0004` bounded region cost plus causal-map construction and non-overlapping optional singleton checks.
- `ALG-0012`: `O(N + P + A^(2k) * P * k + N * L + A^2 + D^2 + path_checks)` for bounded region enumeration plus optional-chain detection, order consistency, and selected-shortcut certification.
- `ALG-0013`: same as `ALG-0012` minus selected-shortcut certification checks; measured savings are currently tiny because chain detection and bounded-region enumeration dominate.
- `ALG-0014`: abstraction path `O(N + A^2 + T * L^2 + B)` for common-boundary block checks and block construction, where `B` is emitted block size; fallback path adds the `ALG-0005` exact automaton cost `O(P * signature_cost + P + E)`.

First limited-operation budget tiers for subsequent promotion discussions:

- Smoke soft budget: `B_smoke = 10N + 8A^2 + 6D + 80` counted primitive operations on a toy log. A candidate can exceed this as a baseline, but low-operation advantage claims should say so explicitly.
- Deep-test soft budget: `B_deep = 16N + 12A^2 + 10D + 120` counted primitive operations on synthetic logs with at most five distinct activities.
- Promotion note: these budgets are screening thresholds, not quality metrics. Replay, negative probes, structural diagnostics, and documented scope still dominate promotion decisions.

## First-iteration candidate requirements

Each candidate below has the required hypothesis, intermediate format, operations, expected cost, first smoke test, likely failure modes, and promotion criteria. Linked candidate files contain the longer records.

- `ALG-0001` Alpha-Lite Relations: baseline Alpha-style relation miner. First smoke gate: sequence, XOR, and parallel replay; skip/loop/noise are failure-characterization gates. Promotion is not expected unless a bounded-pair variant shows useful quality/cost tradeoff. See `candidates/ALG-0001-alpha-lite-relations.md`.
- `ALG-0002` Frequency-Threshold Dependency Graph: heuristic/dependency graph with support and dependency thresholds. First smoke gate: sequence, XOR, parallel, and noise, plus structural diagnostics for unconstrained transitions. Promotion requires threshold sweep, replay without floating/unconstrained visible transitions, and better noise behavior than Alpha-Lite. See `candidates/ALG-0002-frequency-threshold-dependency-graph.md`.
- `ALG-0003` Cut-Limited Process Tree Miner: process-tree candidate with bounded sequence/XOR/parallel/optional-sequence and one bounded optional-concurrency cut. Promoted to `promising` after EXP-0007 and `deep-testing` after EXP-0008: it passes sequence, XOR, parallel, skip, noise, nested XOR, overlapping optional-chain, and bounded optional-concurrency probes with clean structural diagnostics, but fails short loops and duplicate labels. See `candidates/ALG-0003-cut-limited-process-tree-miner.md`.
- `ALG-0004` Bounded Place-Candidate Region Miner: region-inspired bounded place search over small presets/postsets. Implemented and benchmarked in EXP-0011 with `k <= 2`: it passes sequence, XOR, parallel, and noise, but skip precision and loop replay remain poor and operation counts are high. Retained as a visible-place-only comparator, not promoted. See `candidates/ALG-0004-bounded-place-candidate-region-miner.md`.
- `ALG-0005` Prefix Automaton Compression Miner: trie/grammar candidate designed for exact observed replay and controlled compression. Promoted to `promising` after EXP-0009; EXP-0010 documents held-out overfitting, noise memorization, and variant-growth pressure. It remains promising as a comparator and possible grammar-abstraction source, not as a generalizing miner. See `candidates/ALG-0005-prefix-automaton-compression-miner.md`.
- `ALG-0006` PMIR Split-Join Compiler: novel local PMIR split/join compiler. First smoke gate: sequence, XOR, parallel, skip; short-loop/noise as counterexample gates. Promotion requires repaired XOR/skip semantics and retained operation advantage. See `candidates/ALG-0006-pmir-split-join-compiler.md`.
- `ALG-0009` PMIR Guarded Split-Join Compiler: repaired guarded PMIR compiler that marks grouped/optional edges as covered before residual edge emission. Promoted to `promising` after EXP-0004 because it passes positive and negative probes for sequence, XOR, parallel, skip, and noise while retaining lower counts than `ALG-0001`; moved to `deep-testing` in EXP-0005 after ablations and synthetic counterexamples started. See `candidates/ALG-0009-pmir-guarded-split-join-compiler.md`.
- `ALG-0010` PMIR Conflict-Aware Optional Chain Compiler: transitive-reduction optional-chain variant. Promoted to `promising` after EXP-0006 because it fixes overlapping optional skips and passes five of six smoke families, but remains limited by optional/concurrency, short-loop, duplicate-label, and cost issues. See `candidates/ALG-0010-pmir-conflict-aware-optional-chain-compiler.md`.
- `ALG-0011` Region Optional-Tau Repair Miner: bounded region/PMIR hybrid that adds silent skip fragments only for non-overlapping optional singleton patterns certified by a selected region shortcut. Promoted to `promising` after EXP-0012 and moved to `deep-testing` after EXP-0013: the no-repair ablation confirms the optional fragment is causal for singleton and two-disjoint-skip precision gains. It remains narrow and high-cost, with overlapping optional, optional/concurrency, loop, and duplicate-label limitations. See `candidates/ALG-0011-region-optional-tau-repair-miner.md`.
- `ALG-0012` Region Optional-Chain Repair Miner: bounded region/PMIR hybrid that adds order-consistent optional-chain fragments only when selected region shortcut places certify the chain. Promoted to `promising` after EXP-0014 because it fixes overlapping optional-chain precision while preserving smoke replay. It remains high-cost and does not solve optional/concurrency, loop, or duplicate-label cases. See `candidates/ALG-0012-region-optional-chain-repair-miner.md`.
- `ALG-0013` Region Optional-Chain No-Certification Ablation: ablation of `ALG-0012` that emits order-consistent optional chains without requiring selected singleton shortcut places. EXP-0015 shows it matches `ALG-0012` on current optional and synthetic cases while saving only 5-12 operations on chain-emitting logs; not promoted. See `candidates/ALG-0013-region-optional-chain-no-certification-ablation.md`.
- `ALG-0014` Prefix Block Abstraction Miner: grammar/block refinement of `ALG-0005` that detects common-prefix/common-suffix parallel blocks and optional singleton parallel blocks before falling back to exact automaton replay. Promoted to `promising` in EXP-0016 because it recovers balanced held-out interleavings and fixes the optional-singleton parallel probe, but it remains vulnerable to prefix-biased partial permutations and noise. See `candidates/ALG-0014-prefix-block-abstraction-miner.md`.

## Candidate record template

When a candidate becomes more than a row, create `candidates/<ID>-<slug>.md` using `candidates/TEMPLATE.md`, then link it here.
