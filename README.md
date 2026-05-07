# Process-Mining Research Agent for Codex

This scaffold turns Codex into a reusable research agent for process-mining algorithm discovery.
It is generic, but includes a first goal for discovering a Petri net from an event log under a limited-operation model.

## Quick start

1. Copy or unzip this folder into a Git repository.
2. Start Codex from the repository root.
3. Run `/plan` first if you want a reviewable plan, or run the ready-made `/goal` in `GOALS/first-petri-net-limited-ops.md`.
4. Require Codex to keep `CONTINUITY.md`, `MEMORY.md`, `PLAN.md`, `research/ALGORITHM_REGISTRY.md`, and `research/EXPERIMENT_LOG.md` updated after every meaningful step.

## Core idea

The agent is not a single algorithm. It is a research operating system:

- enumerate multiple candidate algorithm families;
- track every candidate, including failures;
- implement small, deterministic prototypes;
- benchmark candidates against baselines and synthetic logs;
- promote promising candidates into deeper testing;
- refine super-promising candidates;
- study formal and empirical properties before making claims.

## Directory map

```text
AGENTS.md                                      Always-loaded Codex operating rules
CONTINUITY.md                                  Current state and next action
MEMORY.md                                      Durable assumptions, definitions, and decisions
PLAN.md                                        Phase-gated research plan
GOALS/first-petri-net-limited-ops.md           Paste-ready first /goal
.agents/skills/process-mining-research/SKILL.md Reusable research workflow skill
.agents/skills/property-study/SKILL.md          Formal/empirical property-study workflow
research/ALGORITHM_REGISTRY.md                 Candidate tracker
research/EVALUATION_PROTOCOL.md                Benchmark and promotion protocol
research/PROPERTY_STUDY_PROTOCOL.md            Property inventory and proof workflow
research/EXPERIMENT_LOG.md                     Append-only experiment log
candidates/TEMPLATE.md                         Candidate record template
scripts/limited_ops.py                         Operation-counting helpers
scripts/pn_ir.py                               JSON Petri-net / PMIR data structures
scripts/alpha_lite.py                          Minimal baseline candidate
scripts/benchmark.py                           Smoke-test benchmark harness
examples/logs/*.json                           Toy logs for smoke tests
```

## First smoke test

```bash
python scripts/benchmark.py --logs examples/logs --out experiments/smoke-results.json
```

This is only a starter harness. The research agent should extend it as hypotheses become concrete.
