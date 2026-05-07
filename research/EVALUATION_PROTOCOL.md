# EVALUATION_PROTOCOL.md

## Evaluation dimensions

Every implemented candidate should be evaluated along these dimensions.

### Model quality

- Replay fitness on observed traces.
- Precision / overgeneralization behavior.
- Generalization behavior under held-out variants.
- Simplicity: number of places, transitions, arcs, silent transitions, and structural complexity.
- Ability to represent sequence, XOR, AND/concurrency, loops, skips, duplicate labels, and noise.

### Structural properties

- Is the output a valid Petri net representation?
- Is it a workflow net or accepting Petri net when claimed?
- Soundness / deadlock freedom under intended semantics.
- Safeness or boundedness when claimed.
- Free-choice or block-structured properties when claimed.

### Computational properties

- Allowed primitive operations.
- Measured operation counts.
- Asymptotic cost in traces, events, activities, variants, and direct-follows pairs.
- Memory footprint.
- Determinism and stability under trace ordering.
- Batch vs incremental/streaming compatibility.

## First smoke-test suite

Use logs in `examples/logs/`:

1. `sequence.json`: sequence only.
2. `xor.json`: exclusive choice.
3. `parallel_ab_cd.json`: simple concurrency evidence via swapped order.
4. `short_loop.json`: one short loop.
5. `skip.json`: optional activity.
6. `noise.json`: dominant behavior plus rare noise.

## Promotion criteria

### implemented -> smoke-tested

- Runs without crashing on all toy logs.
- Produces a PMIR or Petri-net JSON artifact.
- Records operation counts.

### smoke-tested -> promising

At least three of the following must hold:

- Correctly recovers the intended structure for at least four smoke logs.
- Uses fewer counted operations than a baseline on comparable input.
- Produces simpler nets than a baseline with similar behavior.
- Handles a failure mode that another baseline misses.
- Reveals a useful intermediate representation or compiler path.
- Has a plausible formal property claim.

### promising -> deep-testing

- Candidate has a written specification in `candidates/`.
- At least one ablation or refined variant is proposed.
- Counterexample search has been started.

### deep-testing -> super-promising

All must hold:

- Performs well on multiple smoke families and at least one non-trivial synthetic benchmark.
- Has measured operation and runtime costs.
- Has at least one non-obvious advantage over baselines.
- Has property claims that can be studied formally or semi-formally.
- Known failures are documented and do not trivialize the contribution.

## Required experiment log entry

Each experiment entry in `research/EXPERIMENT_LOG.md` must include:

```text
Date/time:
Goal:
Command(s):
Code version / commit if available:
Candidate IDs:
Logs/datasets:
Metrics:
Operation-count model:
Results summary:
Failures / anomalies:
Decision:
Next action:
```
