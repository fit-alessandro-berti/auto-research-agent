"""Targeted loop-generalization tests for ALG-0023."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List

from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "single_rework_zero_or_one",
            "description": "Observed A-C exit and one A-B-A-C rework iteration; a loop model should admit repeated B/A cycles.",
            "train": [["A", "B", "A", "C"], ["A", "B", "A", "C"], ["A", "C"]],
            "heldout": [["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "B", "C"], ["A", "A", "C"], ["B", "A", "C"]],
        },
        {
            "name": "single_rework_one_iteration_only",
            "description": "Without an observed zero-iteration exit, the bounded loop detector should not infer optional loop exit.",
            "train": [["A", "B", "A", "C"], ["A", "B", "A", "C"]],
            "heldout": [["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "C"], ["A", "B", "C"], ["A", "A", "C"]],
        },
        {
            "name": "optional_skip_not_loop",
            "description": "A simple optional skip should stay an optional-sequence cut, not a loop.",
            "train": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"]],
            "heldout": [],
            "negative": [["A", "B", "B", "C"], ["A", "C", "B"], ["B", "C"]],
        },
        {
            "name": "different_rework_body_rejected",
            "description": "Two distinct rework bodies around the same anchor are outside the singleton-body loop scope.",
            "train": [["A", "B", "A", "C"], ["A", "D", "A", "C"], ["A", "C"]],
            "heldout": [["A", "B", "A", "D", "A", "C"]],
            "negative": [["A", "B", "C"], ["A", "D", "C"], ["A", "A", "C"]],
        },
    ]


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "cut_limited_process_tree": importlib.import_module("cut_limited_process_tree").discover,
        "cut_limited_loop_repair": importlib.import_module("cut_limited_loop_repair").discover,
        "cut_limited_multi_body_loop": importlib.import_module("cut_limited_multi_body_loop").discover,
        "cut_limited_length_bounded_loop": importlib.import_module("cut_limited_length_bounded_loop").discover,
        "cut_limited_body_support_guard": importlib.import_module("cut_limited_body_support_guard").discover,
        "prefix_automaton_compression": importlib.import_module("prefix_automaton_compression").discover,
        "prefix_block_support_guard": importlib.import_module("prefix_block_support_guard").discover,
        "prefix_block_grammar_only": importlib.import_module("prefix_block_grammar_only").discover,
    }


def _input_stats(log: TraceLog) -> Dict[str, int]:
    activities = {event for trace in log for event in trace}
    dfg = {(a, b) for trace in log for a, b in zip(trace, trace[1:])}
    event_count = sum(len(trace) for trace in log)
    return {
        "trace_count": len(log),
        "event_count": event_count,
        "activity_count": len(activities),
        "direct_follows_count": len(dfg),
        "max_trace_length": max((len(trace) for trace in log), default=0),
        "deep_soft_budget": 16 * event_count + 12 * len(activities) * len(activities) + 10 * len(dfg) + 120,
    }


def evaluate_candidate(discover: DiscoverFn, train: TraceLog, heldout: TraceLog, negative: TraceLog) -> Dict[str, Any]:
    result = discover(train)
    evidence = result.get("pmir", {}).get("evidence", {})
    train_replay = replay_log(result["petri_net"], train)
    heldout_replay = replay_log(result["petri_net"], heldout)
    negative_probe = precision_probe(result["petri_net"], negative)
    stats = _input_stats(train)
    ops = result["operation_counts"]["total"]
    return {
        "candidate_id": result["candidate_id"],
        "operation_counts": result["operation_counts"],
        "operation_budget": stats["deep_soft_budget"],
        "operation_budget_ratio": 0.0 if stats["deep_soft_budget"] == 0 else ops / stats["deep_soft_budget"],
        "selected_cut": evidence.get("selected_cut"),
        "selected_grammar": evidence.get("selected_grammar"),
        "process_tree": evidence.get("process_tree"),
        "train_replay": {
            "replayed_traces": train_replay["replayed_traces"],
            "trace_count": train_replay["trace_count"],
            "failed_examples": train_replay["failed_examples"],
        },
        "heldout_replay": {
            "replayed_traces": heldout_replay["replayed_traces"],
            "trace_count": heldout_replay["trace_count"],
            "failed_examples": heldout_replay["failed_examples"],
        },
        "negative_probe": negative_probe,
        "structural_diagnostics": train_replay["structural_diagnostics"],
    }


def run_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in test_cases():
        case_result: Dict[str, Any] = {
            "description": case["description"],
            "input_stats": _input_stats(case["train"]),
            "heldout_count": len(case["heldout"]),
            "negative_count": len(case["negative"]),
            "results": {},
        }
        for name, discover in candidates.items():
            try:
                case_result["results"][name] = evaluate_candidate(
                    discover,
                    case["train"],
                    case["heldout"],
                    case["negative"],
                )
            except Exception as exc:
                case_result["results"][name] = {"error": repr(exc)}
        results["cases"][case["name"]] = case_result
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0023-loop-tests.json"))
    args = parser.parse_args()

    results = run_tests()
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
            pieces.append(
                f"{name} cut={result['selected_cut']} grammar={result['selected_grammar']} "
                f"train={result['train_replay']['replayed_traces']}/{result['train_replay']['trace_count']} "
                f"heldout={result['heldout_replay']['replayed_traces']}/{result['heldout_replay']['trace_count']} "
                f"neg={result['negative_probe']['rejected_negative_traces']}/{result['negative_probe']['negative_trace_count']} "
                f"ops={result['operation_counts']['total']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
