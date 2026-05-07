# ALG-0005 — Prefix Automaton Compression Miner

## Status

specified

## One-sentence hypothesis

A prefix automaton built from variants can exactly replay observed traces, and bounded state compression can expose grammar-like blocks that compile to smaller Petri nets.

## Input assumptions

- Log is a finite set of traces over activity labels.
- Exact observed replay is prioritized before generalization.
- Variant explosion is possible and must be measured.
- Concurrency is not inferred unless compression evidence supports it.

## Output

- Prefix trie or compressed automaton.
- Grammar/PMIR block hints.
- Petri-net JSON, initially as an accepting automaton net or compiled grammar fragments.

## Intermediate representation

Prefix automaton with node counts, terminal markers, optional suffix signatures, and compression/merge evidence.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments for variant counts, trie node lookups/inserts, set operations for signatures, comparisons for merge decisions, and construction operations for automaton/net nodes and arcs.

## Algorithm sketch

1. Insert each trace into a prefix trie and count variants.
2. Mark terminal nodes and start/end evidence.
3. Compute bounded suffix signatures bottom-up.
4. Merge nodes with identical bounded signatures when doing so preserves accepted observed traces.
5. Compile the automaton to a Petri net or grammar-like PMIR blocks.

## Expected complexity

Trie build is `O(N)`. Compression is expected around `O(P * signature_cost)` or `O(PA)` for bounded signatures, where `P` is the number of prefix states.

## Smoke tests

First gates: exact replay on `sequence.json`, `xor.json`, and `skip.json`. `parallel_ab_cd.json` is a precision/generalization gate because a trie can memorize both observed orders without discovering concurrency.

## Baselines for comparison

- `ALG-0001` Alpha-Lite Relations.
- `ALG-0002` Frequency-Threshold Dependency Graph.
- `ALG-0008` Evolutionary Tiny-Net Search as a small-log oracle if implemented.

## Metrics

Planned metrics: exact replay, automaton node count, compressed node count, Petri-net size, operation counts, and negative-trace precision probes.

## Known failure modes

- Variant explosion.
- Overfitting and weak concurrency generalization.
- Noise preserved as valid behavior.
- Unsafe state merges if signatures are too coarse.
- Petri-net compilation may add behavior not represented in the automaton.

## Promotion criteria

Can become `promising` only after:

- exact observed replay on all smoke logs in its claimed scope;
- compression improves compactness over a raw trace net;
- operation counts remain near-linear for trie construction;
- negative-trace tests document precision/generalization tradeoffs.

## Experiment links

- Specified during EXP-0003; no executable result yet.

## Property-study notes

Potential future dossier topics: exact replay by trie construction, language preservation under safe state merges, and complexity of bounded-signature compression.

## Decision history

- EXP-0003: specified as the prefix-automaton/grammar-to-net family.
