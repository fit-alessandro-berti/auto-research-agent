# ALGORITHM_REGISTRY.md

Append-only registry of candidate algorithms. Every candidate, including failures, must be tracked.

## Status vocabulary

`idea -> specified -> implemented -> smoke-tested -> benchmarked -> promising -> deep-testing -> super-promising -> property-studied -> report-ready -> retired`

## Initial candidate families for the first Petri-net goal

| ID | Name | Status | Family | Intermediate format | Main hypothesis | Next test | Decision |
|---|---|---:|---|---|---|---|---|
| ALG-0001 | Alpha-Lite Relations | smoke-tested | Alpha-style relation mining | PMIR relation graph | A direct-follows scan plus simple relation classification can recover basic sequence, choice, and concurrency structures at low operation cost. | Add replay/fitness checks and inspect loop failure. | Baseline, not a final claim. |
| ALG-0002 | Frequency-Threshold Dependency Graph | idea | Heuristic miner style | Dependency graph / PMIR | Counting direct-follows frequencies and filtering low-dependency edges can improve robustness under noise while preserving low operation cost. | Specify dependency score and threshold sweep. | Baseline/variant. |
| ALG-0003 | Cut-Limited Process Tree Miner | idea | Inductive miner style | Process tree -> Petri net | Detect a small set of cuts using DFG summaries, then compile a block-structured process tree to a sound Petri net. | Define allowed cuts and operation budget. | Candidate. |
| ALG-0004 | Bounded Place-Candidate Region Miner | idea | Region/ILP-inspired | Place candidates / constraints | A constrained, non-ILP place-candidate search over small presets/postsets may recover useful Petri-net places under an operation budget. | Specify candidate generation and pruning. | Candidate. |
| ALG-0005 | Prefix Automaton Compression Miner | idea | Automaton/grammar | Prefix automaton -> grammar/PMIR -> Petri net | Build a prefix automaton from variants, compress equivalent states cheaply, then synthesize places or blocks. | Implement trie and compression heuristic. | Candidate. |
| ALG-0006 | PMIR Split-Join Compiler | implemented | Novel limited-operation PMIR | PMIR blocks + relation evidence | Learn an intermediate split/join skeleton using only scans, sets, and comparisons; compile to Petri net with silent transitions for ambiguous joins. | Inspect XOR/loop semantics and add replay checks. | Starter candidate; lower counted operations than ALG-0001 in EXP-0001, but not promoted. |
| ALG-0007 | Local Pattern Stitcher | idea | Local process models | Frequent local fragments -> Petri net | Discover small reliable fragments and stitch them into a global net, retaining uncertainty annotations. | Define fragment support and conflict resolution. | Risky candidate. |
| ALG-0008 | Evolutionary Tiny-Net Search | idea | Search/evolutionary | Petri net candidates | Under small activity counts, a bounded search may discover nets with good metrics and reveal reusable structural motifs. | Define tiny logs only; use as oracle/counterexample tool. | Counterexample aid, not low-cost default. |

## Candidate record template

When a candidate becomes more than a row, create `candidates/<ID>-<slug>.md` using `candidates/TEMPLATE.md`, then link it here.

