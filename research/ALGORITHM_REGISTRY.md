# ALGORITHM_REGISTRY.md

Append-only registry of candidate algorithms. Every candidate, including failures, must be tracked.

## Status vocabulary

`idea -> specified -> implemented -> smoke-tested -> benchmarked -> promising -> deep-testing -> super-promising -> property-studied -> report-ready -> retired`

## Initial candidate families for the first Petri-net goal

| ID | Name | Status | Family | Intermediate format | Main hypothesis | Next test | Decision |
|---|---|---:|---|---|---|---|---|
| ALG-0001 | Alpha-Lite Relations | smoke-tested | Alpha-style relation mining | PMIR relation graph | A direct-follows scan plus simple relation classification can recover basic sequence, choice, and concurrency structures at low operation cost. | Add negative-trace precision checks and loop/skip repairs. | Baseline only; not promoted. EXP-0003 replay: sequence/xor/parallel/noise full, skip 2/4, short-loop 1/3. |
| ALG-0002 | Frequency-Threshold Dependency Graph | smoke-tested | Heuristic miner style | Dependency graph / PMIR | Counting direct-follows frequencies and filtering low-dependency edges can improve robustness under noise while preserving low operation cost. | Run threshold sweep and add precision/workflow-net checks. | Implemented in EXP-0003; not promoted because thresholding can leave unconstrained visible transitions. |
| ALG-0003 | Cut-Limited Process Tree Miner | specified | Inductive miner style | Process tree -> Petri net | Detect a small set of cuts using DFG summaries, then compile a block-structured process tree to a sound Petri net. | Implement sequence, XOR, parallel, and skip cuts. | Baseline family specified; no executable prototype yet. |
| ALG-0004 | Bounded Place-Candidate Region Miner | specified | Region/ILP-inspired | Place candidates / constraints | A constrained, non-ILP place-candidate search over small presets/postsets may recover useful Petri-net places under an operation budget. | Implement `k <= 2` place candidate checks against token replay constraints. | Risky but important comparator specified; no executable prototype yet. |
| ALG-0005 | Prefix Automaton Compression Miner | specified | Automaton/grammar | Prefix automaton -> grammar/PMIR -> Petri net | Build a prefix automaton from variants, compress equivalent states cheaply, then synthesize places or blocks. | Implement trie plus suffix-signature state compression. | Exact-replay/overfitting comparator specified; no executable prototype yet. |
| ALG-0006 | PMIR Split-Join Compiler | smoke-tested | Novel limited-operation PMIR | PMIR blocks + relation evidence | Learn an intermediate split/join skeleton using only scans, sets, comparisons, and construction; compile to Petri net via local split/join places. | Repair XOR and skip over-constraint, then rerun replay and structural diagnostics. | Starter candidate; low operation counts but disproven XOR replay in EXP-0003. Not promoted. |
| ALG-0007 | Local Pattern Stitcher | idea | Local process models | Frequent local fragments -> Petri net | Discover small reliable fragments and stitch them into a global net, retaining uncertainty annotations. | Define fragment support and conflict resolution. | Risky candidate. |
| ALG-0008 | Evolutionary Tiny-Net Search | idea | Search/evolutionary | Petri net candidates | Under small activity counts, a bounded search may discover nets with good metrics and reveal reusable structural motifs. | Define tiny logs only; use as oracle/counterexample tool. | Counterexample aid, not low-cost default. |

## Operation-cost model for first iteration

Input-size variables:

- `T`: number of traces.
- `N`: total events.
- `A`: number of distinct activity labels.
- `D`: number of observed direct-follows pairs.
- `V`: number of distinct variants.
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
- `ALG-0003`: expected `O(N + A^2 + recursive_cut_checks)`, approximately `O(N + A^3)` if cut checks are bounded and deterministic.
- `ALG-0004`: `O(N + P + A^(2k) * P * k)` with small fixed `k` and no external solver.
- `ALG-0005`: trie build `O(N)`, compression approximately `O(P * signature_cost)` or `O(PA)` for bounded signatures.
- `ALG-0006`: `O(N + A^2 + sum_v out(v)^2 + sum_v in(v)^2)` for relation classification and local split/join grouping.

## First-iteration candidate requirements

Each candidate below has the required hypothesis, intermediate format, operations, expected cost, first smoke test, likely failure modes, and promotion criteria. Linked candidate files contain the longer records.

- `ALG-0001` Alpha-Lite Relations: baseline Alpha-style relation miner. First smoke gate: sequence, XOR, and parallel replay; skip/loop/noise are failure-characterization gates. Promotion is not expected unless a bounded-pair variant shows useful quality/cost tradeoff. See `candidates/ALG-0001-alpha-lite-relations.md`.
- `ALG-0002` Frequency-Threshold Dependency Graph: heuristic/dependency graph with support and dependency thresholds. First smoke gate: sequence, XOR, parallel, and noise, plus structural diagnostics for unconstrained transitions. Promotion requires threshold sweep, replay without floating/unconstrained visible transitions, and better noise behavior than Alpha-Lite. See `candidates/ALG-0002-frequency-threshold-dependency-graph.md`.
- `ALG-0003` Cut-Limited Process Tree Miner: process-tree candidate with bounded sequence/XOR/parallel/skip cut detection. First smoke gate: sequence, XOR, parallel, skip. Promotion requires sound block-structured compilation and measured cut-operation counts. See `candidates/ALG-0003-cut-limited-process-tree-miner.md`.
- `ALG-0004` Bounded Place-Candidate Region Miner: region-inspired bounded place search over small presets/postsets. First smoke gate: sequence, XOR, parallel, then all six logs for replay constraints. Promotion requires `k <= 2` operation counts and places that fix cases relation miners miss. See `candidates/ALG-0004-bounded-place-candidate-region-miner.md`.
- `ALG-0005` Prefix Automaton Compression Miner: trie/grammar candidate designed for exact observed replay and controlled compression. First smoke gate: exact replay on sequence/XOR/skip, plus parallel overfitting check. Promotion requires compactness versus raw trace net and explicit precision tradeoff. See `candidates/ALG-0005-prefix-automaton-compression-miner.md`.
- `ALG-0006` PMIR Split-Join Compiler: novel local PMIR split/join compiler. First smoke gate: sequence, XOR, parallel, skip; short-loop/noise as counterexample gates. Promotion requires repaired XOR/skip semantics and retained operation advantage. See `candidates/ALG-0006-pmir-split-join-compiler.md`.

## Candidate record template

When a candidate becomes more than a row, create `candidates/<ID>-<slug>.md` using `candidates/TEMPLATE.md`, then link it here.
