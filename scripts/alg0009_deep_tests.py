"""Deep smoke and counterexample tests for guarded PMIR candidates."""

from __future__ import annotations

import argparse
import importlib
import json
from itertools import permutations
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import pmir_guarded_split_join
import pmir_conflict_aware_optional
import cut_limited_process_tree
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


SYNTHETIC_CASES = [
    {
        "name": "nested_xor_sequence",
        "description": "A simple XOR branch inside a sequence.",
        "traces": [["A", "B", "D", "E"], ["A", "C", "D", "E"], ["A", "B", "D", "E"]],
        "negative_traces": [["A", "B", "C", "D", "E"], ["A", "D", "E"], ["A", "C", "B", "D", "E"]],
    },
    {
        "name": "overlapping_optional_skips",
        "description": "Two optional activities between the same start and end, including the double-skip variant.",
        "traces": [["A", "B", "C", "D"], ["A", "C", "D"], ["A", "B", "D"], ["A", "D"]],
        "negative_traces": [["A", "B", "B", "D"], ["A", "C", "B", "D"], ["A", "D", "C"]],
    },
    {
        "name": "parallel_with_optional_branch",
        "description": "Concurrent B/C evidence with an optional D after B.",
        "traces": [["A", "B", "D", "C", "E"], ["A", "C", "B", "D", "E"], ["A", "B", "C", "E"]],
        "negative_traces": [["A", "D", "B", "C", "E"], ["A", "B", "D", "D", "C", "E"], ["A", "E"]],
    },
    {
        "name": "short_loop_required",
        "description": "A short loop where relation classifiers tend to mark bidirectional evidence as parallel.",
        "traces": [["A", "B", "A", "C"], ["A", "B", "A", "C"], ["A", "C"]],
        "negative_traces": [["A", "B", "C"], ["B", "A", "C"], ["A", "A", "C"]],
    },
    {
        "name": "duplicate_label_rework",
        "description": "Repeated label A appears both before and after B.",
        "traces": [["A", "B", "A", "C"], ["A", "C"], ["A", "B", "A", "C"]],
        "negative_traces": [["A", "B", "C"], ["B", "A", "C"], ["A", "A", "B", "C"]],
    },
    {
        "name": "incomplete_parallel_observed_sequence",
        "description": "Only one order of an intended parallel pair is observed; this tests incompleteness sensitivity.",
        "traces": [["A", "B", "C", "D"], ["A", "B", "C", "D"]],
        "negative_traces": [["A", "C", "B", "D"], ["A", "B", "D"], ["A", "D"]],
    },
    {
        "name": "noise_reversal_sequence",
        "description": "Dominant sequence with one rare reversed pair that can be mistaken for concurrency.",
        "traces": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "C", "B", "D"]],
        "negative_traces": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
    },
]


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "alpha_lite": importlib.import_module("alpha_lite").discover,
        "dependency_threshold": importlib.import_module("dependency_threshold").discover,
        "cut_limited_process_tree": cut_limited_process_tree.discover,
        "cut_tree_no_parallel_optional": lambda log: cut_limited_process_tree.discover(
            log,
            enable_parallel_optional=False,
        ),
        "prefix_automaton_compression": importlib.import_module("prefix_automaton_compression").discover,
        "pmir_split_join_lite": importlib.import_module("pmir_split_join_lite").discover,
        "pmir_guarded_split_join": pmir_guarded_split_join.discover,
        "pmir_conflict_aware_optional": pmir_conflict_aware_optional.discover,
        "pmir_guarded_no_optional": lambda log: pmir_guarded_split_join.discover(log, enable_optional=False, enable_xor=True),
        "pmir_guarded_no_xor": lambda log: pmir_guarded_split_join.discover(log, enable_optional=True, enable_xor=False),
        "pmir_guarded_edge_only": lambda log: pmir_guarded_split_join.discover(log, enable_optional=False, enable_xor=False),
        "pmir_conflict_no_optional_chains": lambda log: pmir_conflict_aware_optional.discover(
            log,
            enable_optional_chains=False,
            enable_xor=True,
        ),
    }


def evaluate_result(result: Dict[str, Any], traces: TraceLog, negative_traces: TraceLog) -> Dict[str, Any]:
    replay = replay_log(result["petri_net"], traces)
    probe = precision_probe(result["petri_net"], negative_traces)
    return {
        "candidate_id": result["candidate_id"],
        "operation_counts": result["operation_counts"],
        "structural_summary": result["structural_summary"],
        "replay_summary": {
            "replayed_traces": replay["replayed_traces"],
            "trace_count": replay["trace_count"],
            "replay_fitness": replay["replay_fitness"],
            "failed_examples": replay["failed_examples"],
            "structural_diagnostics": replay["structural_diagnostics"],
        },
        "precision_probe": probe,
        "pmir_evidence": result.get("pmir", {}).get("evidence", {}),
    }


def stable_under_permutation(discover: DiscoverFn, traces: TraceLog, limit: int = 24) -> Dict[str, Any]:
    signatures = {}
    checked = 0
    for permuted in permutations(traces):
        result = discover([list(trace) for trace in permuted])
        signature = json.dumps(
            {
                "petri_net": result["petri_net"],
                "pmir_evidence": result.get("pmir", {}).get("evidence", {}),
            },
            sort_keys=True,
        )
        signatures[signature] = signatures.get(signature, 0) + 1
        checked += 1
        if checked >= limit:
            break
    return {
        "permutations_checked": checked,
        "distinct_signatures": len(signatures),
        "stable": len(signatures) == 1,
    }


def run_deep_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in SYNTHETIC_CASES:
        case_results: Dict[str, Any] = {
            "description": case["description"],
            "trace_count": len(case["traces"]),
            "event_count": sum(len(t) for t in case["traces"]),
            "negative_trace_count": len(case["negative_traces"]),
            "results": {},
        }
        for name, discover in candidates.items():
            try:
                result = discover(case["traces"])
                case_results["results"][name] = evaluate_result(result, case["traces"], case["negative_traces"])
            except Exception as exc:
                case_results["results"][name] = {"error": repr(exc)}
        case_results["trace_order_stability"] = stable_under_permutation(
            pmir_guarded_split_join.discover,
            case["traces"],
        )
        case_results["trace_order_stability_alg0010"] = stable_under_permutation(
            pmir_conflict_aware_optional.discover,
            case["traces"],
        )
        results["cases"][case["name"]] = case_results
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0009-deep-tests.json"))
    args = parser.parse_args()

    results = run_deep_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        alg0003 = case["results"]["cut_limited_process_tree"]
        alg0005 = case["results"]["prefix_automaton_compression"]
        alg0009 = case["results"]["pmir_guarded_split_join"]
        alg0010 = case["results"]["pmir_conflict_aware_optional"]
        replay3 = alg0003["replay_summary"]
        probe3 = alg0003["precision_probe"]
        replay5 = alg0005["replay_summary"]
        probe5 = alg0005["precision_probe"]
        replay = alg0009["replay_summary"]
        probe = alg0009["precision_probe"]
        replay10 = alg0010["replay_summary"]
        probe10 = alg0010["precision_probe"]
        stability = case["trace_order_stability"]
        stability10 = case["trace_order_stability_alg0010"]
        print(
            f"{case_name}: ALG-0003 ops={alg0003['operation_counts']['total']} "
            f"replay={replay3['replayed_traces']}/{replay3['trace_count']} "
            f"neg_reject={probe3['rejected_negative_traces']}/{probe3['negative_trace_count']}; "
            f"ALG-0005 ops={alg0005['operation_counts']['total']} "
            f"replay={replay5['replayed_traces']}/{replay5['trace_count']} "
            f"neg_reject={probe5['rejected_negative_traces']}/{probe5['negative_trace_count']}; "
            f"ALG-0009 ops={alg0009['operation_counts']['total']} "
            f"replay={replay['replayed_traces']}/{replay['trace_count']} "
            f"neg_reject={probe['rejected_negative_traces']}/{probe['negative_trace_count']} "
            f"stable={stability['stable']}; ALG-0010 ops={alg0010['operation_counts']['total']} "
            f"replay={replay10['replayed_traces']}/{replay10['trace_count']} "
            f"neg_reject={probe10['rejected_negative_traces']}/{probe10['negative_trace_count']} "
            f"stable={stability10['stable']}"
        )


if __name__ == "__main__":
    main()
