# ALG-0006 — PMIR Split-Join Compiler Lite

## Status

implemented

## One-sentence hypothesis

A local split/join compiler can avoid Alpha-style subset search by using pairwise relation evidence to group XOR-like branches and keep parallel branches separate, reducing counted operations while preserving interpretable Petri-net structure.

## Input assumptions

- Log is a list of traces.
- Each trace is an ordered list of activity labels.
- Direct-follows evidence is sufficient for first-pass relation classification.
- XOR-like alternatives appear as mutually unrelated branch activities.
- Parallel branches appear through swapped direct-follows evidence.

## Output

- PMIR relation graph and emitted split/join place patterns.
- Petri-net JSON.

## Intermediate representation

PMIR with local split/join evidence. The compiler emits:

- `splitxor` places for one predecessor and multiple mutually unrelated successors;
- `joinxor` places for multiple mutually unrelated predecessors and one successor;
- `edge` places for individual causal edges, especially parallel branches.

## Allowed operations / operation-cost model

Uses event scans, dictionary increments, set inserts/lookups, comparisons, relation classifications, and construction operations. It does not enumerate arbitrary preset/postset subsets.

## Algorithm sketch

1. Scan log and classify direct-follows relations.
2. Build incoming and outgoing causal maps.
3. For each activity, group mutually unrelated outgoing successors into XOR-like split places; otherwise emit individual edge places.
4. For each activity, group mutually unrelated incoming predecessors into XOR-like join places; otherwise emit individual edge places.
5. Compile places/arcs directly to a Petri net.

## Expected complexity

Expected to be roughly dominated by log scan plus pairwise relation classification: `O(events + activities^2 + local_branch_checks)`. It should avoid the exponential subset search of Alpha-style place candidates.

## Smoke tests

Executed in EXP-0001 on toy sequence, XOR, parallel, loop, skip, and noise logs.

## Baselines for comparison

- ALG-0001 Alpha-Lite Relations.
- Future: dependency-graph, inductive/process-tree, and region-inspired variants.

## Metrics

Initial metrics: operation counts and structural counts. In EXP-0001, this candidate used fewer counted operations than ALG-0001 on every toy log. Semantic metrics are not yet implemented.

## Known failure modes

- XOR example currently produces more places/arcs than ALG-0001, suggesting duplicate or over-constrained split/join compilation.
- Relation classification is fragile under noise.
- Loops and duplicate labels are not handled.
- Soundness is unknown.

## Promotion criteria

Can be promoted to `promising` only after:

- token-game or PM4Py replay checks show it can replay intended smoke logs;
- XOR and skip behavior are inspected and repaired if over-constrained;
- operation advantage remains after repairs;
- known failure modes are documented with counterexamples.

## Experiment links

- EXP-0001 in `research/EXPERIMENT_LOG.md`.
- `experiments/smoke-results.json`.

## Property-study notes

Potential properties to study if refined:

- operation bound compared with Alpha-style subset enumeration;
- conditions under which mutually unrelated branch grouping correctly models XOR;
- conditions under which pairwise swapped evidence correctly models parallelism;
- conversion correctness from PMIR split/join patterns to Petri-net places.

## Decision history

- Scaffold: implemented as starter novel limited-operation candidate.
- EXP-0001: lower counted operations than ALG-0001, but not promoted because semantic validation is missing.
