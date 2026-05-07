# First /goal: limited-operation Petri-net discovery

Paste this into Codex from the repository root:

```text
/goal Read AGENTS.md, CONTINUITY.md, MEMORY.md, PLAN.md, and GOALS/first-petri-net-limited-ops.md. Act as the process-mining research agent.

Research goal: discover and evaluate algorithms for learning a Petri net, or an intermediate representation that can be compiled to a Petri net, from an event log using a limited number/set of mathematical operations.

Do not solve this as a single algorithm. Enumerate and track multiple candidate families, including baselines and risky ideas. Use subagents where useful: one candidate scout, one implementation scout, one evaluator/counterexample scout, and one property-study scout. Merge all findings into the registry.

Required first iteration:
1. Define the operation-cost model precisely enough to instrument prototypes.
2. Populate research/ALGORITHM_REGISTRY.md with at least six candidates. Include Alpha-style relation mining, heuristic/dependency-graph mining, inductive/process-tree mining, region/ILP-inspired mining, prefix-automaton/grammar-to-net mining, and at least one novel limited-operation PMIR-to-Petri-net idea.
3. Make sure every candidate has: hypothesis, intermediate format, allowed operations, expected cost, first smoke test, likely failure modes, and promotion criteria.
4. Run or extend scripts/benchmark.py on the toy logs in examples/logs.
5. Implement at least one minimal baseline and one new limited-operation candidate, unless the current scaffold already contains a baseline; in that case validate it and add the new candidate.
6. Record all commands and results in research/EXPERIMENT_LOG.md.
7. Promote any promising candidates only if they meet the protocol in research/EVALUATION_PROTOCOL.md.
8. For any candidate that looks super-promising, start a property dossier under reports/ and study its properties using research/PROPERTY_STUDY_PROTOCOL.md.
9. Update CONTINUITY.md, MEMORY.md, PLAN.md, and the registry before stopping.

Done when: there is a reproducible first research iteration with a candidate registry, executed smoke tests, at least two executable prototypes or one executable prototype plus one fully specified prototype, explicit operation counts, promotion/retirement decisions, and a next-experiment plan.
```
