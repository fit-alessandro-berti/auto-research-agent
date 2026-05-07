# PROPERTY_STUDY_PROTOCOL.md

Use this protocol for any `super-promising` candidate, and optionally for promising candidates with interesting theory.

## Property dossier structure

Create `reports/<candidate-id>-property-dossier.md` with these sections.

### 1. Candidate statement

- Algorithm ID and version.
- Input assumptions.
- Output type: PMIR, Petri net, process tree, or other.
- Operation model.
- Claimed scope.

### 2. Conversion correctness

If the algorithm uses an intermediate representation, study:

- Is every PMIR instance accepted by the compiler?
- Does compilation preserve intended ordering relations?
- Does compilation add behavior not represented in the PMIR?
- Are silent transitions introduced, and what semantics do they have?

### 3. Behavioral properties

Study or test:

- Replay of observed traces.
- Missing behavior and incompleteness sensitivity.
- Overgeneralization / precision.
- Generalization to held-out variants.
- Noise sensitivity.
- Concurrency detection correctness.
- Loop detection correctness.
- Duplicate-label handling.

### 4. Petri-net structural properties

Study:

- Workflow-net structure.
- Soundness.
- Deadlock freedom.
- Liveness under final-marking semantics.
- Boundedness / safeness.
- Free-choice property.
- Reachability complexity for generated nets.
- Place minimality or redundancy.

### 5. Computational properties

Study:

- Time complexity.
- Memory complexity.
- Primitive operation counts.
- Determinism.
- Stability under trace order, duplicate traces, and small perturbations.
- Incremental updateability.

### 6. Proof/counterexample table

Use this format:

| Property | Status | Evidence | Counterexample search | Notes |
|---|---|---|---|---|
| Valid Petri net output | unknown/proven/disproven/empirical | | | |
| Replays all observed traces under assumptions | unknown/proven/disproven/empirical | | | |
| Soundness | unknown/proven/disproven/empirical | | | |
| Boundedness | unknown/proven/disproven/empirical | | | |
| Operation bound | unknown/proven/disproven/empirical | | | |

## Claim discipline

Use these labels exactly:

- **Proven**: formal argument covers stated assumptions.
- **Disproven**: counterexample found.
- **Empirical**: observed in tests only.
- **Conjecture**: plausible but unproven.
- **Unknown**: not yet studied.
