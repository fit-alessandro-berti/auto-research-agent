# MEMORY.md

Durable memory for the process-mining research agent. Append only stable facts, definitions, conventions, and decisions. Do not store transient status here; use `CONTINUITY.md` instead.

## Definitions

- **Event log**: a collection of traces/cases; each trace is an ordered sequence of activity labels, optionally with timestamps and attributes.
- **Process discovery**: learning a process model from an event log.
- **Petri net output**: represented here as transitions, places, directed arcs, an initial marking, and a final marking.
- **PMIR**: Process-Mining Intermediate Representation. A deliberately lightweight intermediate format that can store activities, start/end evidence, direct-follows evidence, inferred relations, block/decomposition hints, and place candidates before compilation to a Petri net.
- **Limited-operation model**: a declared set of primitive operations and a rule for counting them. For the first goal, the default primitives are event scan, dictionary increment, comparison, set insert, set lookup, relation classification, and arc/place construction.

## Durable research principles

- Candidate algorithms must be compared on fitness, precision/generalization behavior, simplicity, soundness/structural properties, robustness, and operation cost.
- A failed algorithm is valuable if it yields a counterexample, limitation, or useful intermediate representation.
- Promising algorithms should be refined through ablations and counterexample-guided repair before formal claims are made.
- Super-promising algorithms require a property dossier before being presented as a serious research result.

## Default smoke-log families

- Strict sequence: `A B C D`
- Exclusive choice: `A (B|C) D`
- Parallel/concurrent behavior: `A B C D` and `A C B D`
- Short loop: `A B A C` or `A B B C`
- Skip behavior: `A B C` and `A C`
- Noise/infrequent behavior: dominant pattern plus rare directly-follows deviations

## Do-not-forget decisions

- The repository must remain generic. The first Petri-net task is a goal, not the agent identity.
- Intermediate representations are allowed and encouraged when they make discovery or property study easier.
