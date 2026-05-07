"""Optional-pattern tests for region optional repairs and ablations."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List

import region_optional_tau_miner
import region_optional_chain_miner
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


OPTIONAL_CASES = [
    {
        "name": "singleton_optional_skip",
        "description": "One optional middle activity with direct shortcut evidence.",
        "traces": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"], ["A", "C"]],
        "negative_traces": [["A", "B", "B", "C"], ["A", "C", "B"], ["B", "C"]],
    },
    {
        "name": "two_disjoint_optional_skips",
        "description": "Two non-overlapping optional singleton skips in sequence.",
        "traces": [["A", "B", "C", "D", "E"], ["A", "C", "D", "E"], ["A", "B", "C", "E"], ["A", "C", "E"]],
        "negative_traces": [["A", "B", "B", "C", "E"], ["A", "C", "D", "C", "E"], ["A", "E"]],
    },
    {
        "name": "overlapping_optional_chain",
        "description": "Two overlapping optional activities between the same boundary.",
        "traces": [["A", "B", "C", "D"], ["A", "C", "D"], ["A", "B", "D"], ["A", "D"]],
        "negative_traces": [["A", "B", "B", "D"], ["A", "C", "B", "D"], ["A", "D", "C"]],
    },
    {
        "name": "optional_inside_parallel",
        "description": "Optional singleton on one branch while another branch may interleave.",
        "traces": [["A", "B", "D", "C", "E"], ["A", "C", "B", "D", "E"], ["A", "B", "C", "E"]],
        "negative_traces": [["A", "D", "B", "C", "E"], ["A", "B", "D", "D", "C", "E"], ["A", "E"]],
    },
    {
        "name": "optional_singleton_parallel_branch",
        "description": "Optional singleton branch interleaves with one mandatory branch before a common join.",
        "traces": [["A", "B", "C", "D"], ["A", "C", "B", "D"], ["A", "C", "D"], ["A", "B", "C", "D"]],
        "negative_traces": [["A", "B", "B", "C", "D"], ["A", "B", "D", "C"], ["A", "D"]],
    },
]


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "bounded_place_region_miner": importlib.import_module("bounded_place_region_miner").discover,
        "region_optional_tau_miner": region_optional_tau_miner.discover,
        "region_optional_chain_miner": region_optional_chain_miner.discover,
        "region_optional_chain_no_region_cert": lambda log: region_optional_chain_miner.discover(
            log,
            require_region_shortcut=False,
        ),
        "region_optional_tau_no_repair": lambda log: region_optional_tau_miner.discover(
            log,
            enable_optional_repair=False,
        ),
        "cut_limited_process_tree": importlib.import_module("cut_limited_process_tree").discover,
        "prefix_block_abstraction": importlib.import_module("prefix_block_abstraction").discover,
        "pmir_conflict_aware_optional": importlib.import_module("pmir_conflict_aware_optional").discover,
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


def run_optional_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in OPTIONAL_CASES:
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
        results["cases"][case["name"]] = case_results
    return results


def _optional_count(result: Dict[str, Any]) -> int:
    evidence = result.get("pmir_evidence", {})
    if "optional_chains" in evidence:
        return len(evidence.get("optional_chains", []))
    return evidence.get("optional_stats", {}).get("accepted_optional_patterns", 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0011-optional-tests.json"))
    args = parser.parse_args()

    results = run_optional_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        pieces = []
        for name in results["candidates"]:
            result = case["results"][name]
            if "error" in result:
                pieces.append(f"{name}=ERROR")
                continue
            replay = result["replay_summary"]
            probe = result["precision_probe"]
            pieces.append(
                f"{name} ops={result['operation_counts']['total']} "
                f"replay={replay['replayed_traces']}/{replay['trace_count']} "
                f"neg_reject={probe['rejected_negative_traces']}/{probe['negative_trace_count']} "
                f"opt={_optional_count(result)}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
