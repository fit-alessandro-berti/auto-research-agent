---
name: process-mining-research
description: Use for process-mining research tasks: enumerate candidate algorithms, track all candidates, run experiments, promote/refine promising algorithms, and prepare research reports.
---

# Process-Mining Research Skill

Use this skill whenever the task involves process mining, process discovery, Petri nets, event logs, conformance checking, process trees, directly-follows graphs, object-centric logs, or algorithmic research around such topics.

## Required workflow

1. Read `AGENTS.md`, `CONTINUITY.md`, `MEMORY.md`, `PLAN.md`, `research/ALGORITHM_REGISTRY.md`, and `research/EXPERIMENT_LOG.md`.
2. Identify the active goal and constraints.
3. Enumerate candidate algorithm families before implementing.
4. Add every candidate to `research/ALGORITHM_REGISTRY.md`.
5. For each candidate, specify hypothesis, intermediate representation, operation model, expected complexity, failure modes, first test, and promotion criteria.
6. Implement small deterministic prototypes.
7. Run smoke tests and record commands/results.
8. Promote, refine, or retire candidates based on the protocol.
9. For promising candidates, run deeper tests and ablations.
10. For super-promising candidates, invoke the property-study workflow.
11. Update continuity and plan files before finishing.

## Candidate diversity requirements

For Petri-net discovery tasks, consider at least these families unless the active goal explicitly excludes them:

- Alpha-style relation mining;
- heuristic/frequency/dependency graph mining;
- inductive/process-tree mining;
- region/ILP-inspired place discovery;
- prefix automaton, grammar, or language-based synthesis;
- local-process-model or fragment stitching;
- bounded search/evolutionary candidate generation;
- novel intermediate representations compilable to Petri nets.

## Promotion discipline

Do not call a candidate promising merely because it looks elegant. Require implemented behavior, smoke-test evidence, operation counts, and a concrete advantage or interesting failure mode.

## Output discipline

When reporting to the user, include:

- candidate IDs and statuses;
- experiments run;
- promotions and retirements;
- next experiment;
- uncertainties and limitations.
