# MEMORY.md

Durable memory for the process-mining research agent. Append only stable facts, definitions, conventions, and decisions. Do not store transient status here; use `CONTINUITY.md` instead.

## Definitions

- **Event log**: a collection of traces/cases; each trace is an ordered sequence of activity labels, optionally with timestamps and attributes.
- **Process discovery**: learning a process model from an event log.
- **Petri net output**: represented here as transitions, places, directed arcs, an initial marking, and a final marking.
- **PMIR**: Process-Mining Intermediate Representation. A deliberately lightweight intermediate format that can store activities, start/end evidence, direct-follows evidence, inferred relations, block/decomposition hints, and place candidates before compilation to a Petri net.
- **Limited-operation model**: a declared set of primitive operations and a rule for counting them. For the first goal, the default counted primitives are event scan, dictionary increment, comparison, set insert, set lookup, arithmetic, relation classification, and arc/place construction.
- **First-goal soft operation budgets**: for later screening, use `B_smoke = 10N + 8A^2 + 6D + 80` on toy logs and `B_deep = 16N + 12A^2 + 10D + 120` on small synthetic logs. These are not quality metrics and do not override replay, negative probes, or structural diagnostics.

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
- In this workspace, use `python3` for benchmark commands; `python` was not available during EXP-0002.
- Replay fitness from the local token-game evaluator is not a precision or soundness claim. Structural diagnostics and negative-trace probes are required before promotion.
- A candidate with unconstrained visible transitions must not be promoted based on positive-trace replay alone.
- The local token-game evaluator supports bounded silent-transition closure for `tau_` transitions; this is enough for smoke replay of optional skips, not a full reachability/soundness proof.
- Local optional-skip guards can conflict when multiple optional triples overlap. Future PMIR guard compilers need a conflict-resolution or block-detection step before emitting optional places.
- Transitive-reduction optional-chain compilation can repair overlapping optional skips, but it is costlier and does not solve optional behavior embedded in concurrency.
- The cut-limited process-tree baseline (`ALG-0003`) currently handles top-level sequence, common-context XOR, common-context parallel, optional-sequence blocks, and one bounded optional-concurrency form: a mandatory singleton branch parallel with a two-step branch whose second activity is optional. It is not yet recursive and should not be treated as a full inductive miner.
- Petri-net JSON may include optional `transition_labels` for candidates that need multiple visible transitions with the same activity label. The evaluator still infers legacy `t_<activity>` labels when no explicit label is present.
- The prefix-automaton comparator (`ALG-0005`) is an exact observed-language baseline. Its strong replay/negative-probe behavior should be read as memorization until held-out and variant-explosion tests are run.
- EXP-0010 held-out tests confirm `ALG-0005` does not generalize to unobserved valid interleavings and memorizes observed noise. It needs a grammar/block abstraction before any deep-testing promotion.
