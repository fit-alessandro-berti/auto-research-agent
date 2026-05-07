---
name: process-mining-property-study
description: Use for formal and empirical property studies of promising process-mining algorithms, especially Petri-net discovery algorithms and PMIR-to-net compilers.
---

# Process-Mining Property Study Skill

Use this skill when a candidate is `super-promising`, or when the active task asks for formal guarantees, properties, proofs, counterexamples, or theoretical analysis.

## Required workflow

1. Read `research/PROPERTY_STUDY_PROTOCOL.md`.
2. Create or update a property dossier in `reports/`.
3. State input assumptions and output semantics precisely.
4. Distinguish formal proof, counterexample, empirical evidence, conjecture, and unknown.
5. For every claimed property, attempt a counterexample before strengthening the claim.
6. Study both the discovery algorithm and any intermediate-format compiler.
7. Update candidate status and experiment log.

## Core properties to study

- valid Petri-net construction;
- workflow-net or accepting-net structure;
- replay of observed traces;
- soundness;
- boundedness/safeness;
- liveness/deadlock freedom;
- free-choice or block-structured property;
- precision/generalization behavior;
- robustness to noise and incompleteness;
- operation-count and complexity bounds;
- determinism and stability;
- incremental updateability;
- conversion correctness from PMIR or other intermediate representation.

## Claim labels

Use exactly: Proven, Disproven, Empirical, Conjecture, Unknown.
