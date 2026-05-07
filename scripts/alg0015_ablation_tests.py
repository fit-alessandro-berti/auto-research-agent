"""Feature-ablation tests for ALG-0015 prefix block support guards."""

from __future__ import annotations

import argparse
import importlib
import json
from itertools import permutations
from pathlib import Path
from typing import Any, Callable, Dict, List

from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


def _perm_traces(branches: List[str]) -> TraceLog:
    return [["A", *perm, "E"] for perm in permutations(branches)]


def ablation_cases() -> List[Dict[str, Any]]:
    prefix_biased_train = _perm_traces(["B", "C", "D"])[:2]
    prefix_biased_heldout = _perm_traces(["B", "C", "D"])[2:]
    return [
        {
            "name": "prefix_biased_parallel_2_of_6",
            "description": "Two observed interleavings share a middle prefix; the valid remaining interleavings are held out.",
            "train": prefix_biased_train,
            "heldout": prefix_biased_heldout,
            "negative": [["A", "B", "C", "E"], ["A", "B", "B", "C", "D", "E"], ["B", "C", "D", "E"]],
        },
        {
            "name": "balanced_parallel_2_of_6",
            "description": "Two observed interleavings do not share a misleading middle prefix.",
            "train": [["A", "B", "C", "D", "E"], ["A", "C", "D", "B", "E"]],
            "heldout": [
                trace
                for trace in _perm_traces(["B", "C", "D"])
                if trace not in [["A", "B", "C", "D", "E"], ["A", "C", "D", "B", "E"]]
            ],
            "negative": [["A", "B", "C", "E"], ["A", "B", "B", "C", "D", "E"], ["B", "C", "D", "E"]],
        },
        {
            "name": "rare_reversal_noise_3_to_1",
            "description": "A dominant sequence plus one rare reversed trace that should be treated as noise for precision probing.",
            "train": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
        },
        {
            "name": "rare_reversal_noise_5_to_1",
            "description": "A stronger dominant sequence plus one rare reversed trace.",
            "train": [
                ["A", "B", "C", "D"],
                ["A", "B", "C", "D"],
                ["A", "B", "C", "D"],
                ["A", "B", "C", "D"],
                ["A", "B", "C", "D"],
                ["A", "C", "B", "D"],
            ],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
        },
        {
            "name": "ambiguous_reversal_tie",
            "description": "Balanced reversal evidence should remain parallel-like rather than dominant-sequence noise.",
            "train": [["A", "B", "C", "D"], ["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
        },
        {
            "name": "same_order_incomplete_parallel",
            "description": "Only one order is observed twice; the reversed order is held out to expose conservative incompleteness behavior.",
            "train": [["A", "B", "C", "D"], ["A", "B", "C", "D"]],
            "heldout": [["A", "C", "B", "D"]],
            "negative": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
        },
        {
            "name": "different_activity_sets_skip_like",
            "description": "Variant activity sets differ, so dominant-sequence handling should stay disabled.",
            "train": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"], ["A", "C"]],
            "heldout": [],
            "negative": [["A", "C", "B"], ["A", "B", "B", "C"], ["B", "C"]],
        },
    ]


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "prefix_automaton_compression": importlib.import_module("prefix_automaton_compression").discover,
        "prefix_block_abstraction": importlib.import_module("prefix_block_abstraction").discover,
        "prefix_block_support_only": importlib.import_module("prefix_block_support_only").discover,
        "prefix_block_prefix_merge_only": importlib.import_module("prefix_block_prefix_merge_only").discover,
        "prefix_block_dominant_only": importlib.import_module("prefix_block_dominant_only").discover,
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
    train_replay = replay_log(result["petri_net"], train)
    heldout_replay = replay_log(result["petri_net"], heldout)
    negative_probe = precision_probe(result["petri_net"], negative)
    evidence = result.get("pmir", {}).get("evidence", {})
    grammar = evidence.get("grammar", {})
    stats = _input_stats(train)
    ops = result["operation_counts"]["total"]
    return {
        "candidate_id": result["candidate_id"],
        "operation_counts": result["operation_counts"],
        "operation_budget": stats["deep_soft_budget"],
        "operation_budget_ratio": 0.0 if stats["deep_soft_budget"] == 0 else ops / stats["deep_soft_budget"],
        "selected_grammar": evidence.get("selected_grammar"),
        "grammar_origin": grammar.get("origin") if isinstance(grammar, dict) else None,
        "support_counts": grammar.get("support_counts") if isinstance(grammar, dict) else None,
        "configuration": evidence.get("configuration", {}),
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
    }


def run_ablation_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in ablation_cases():
        train = case["train"]
        heldout = case["heldout"]
        negative = case["negative"]
        case_result: Dict[str, Any] = {
            "description": case["description"],
            "input_stats": _input_stats(train),
            "heldout_count": len(heldout),
            "negative_count": len(negative),
            "results": {},
        }
        for name, discover in candidates.items():
            try:
                case_result["results"][name] = evaluate_candidate(discover, train, heldout, negative)
            except Exception as exc:
                case_result["results"][name] = {"error": repr(exc)}
        results["cases"][case["name"]] = case_result
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0015-ablation-tests.json"))
    args = parser.parse_args()

    results = run_ablation_tests()
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
                f"{name} grammar={result['selected_grammar']} "
                f"origin={result['grammar_origin']} "
                f"train={result['train_replay']['replayed_traces']}/{result['train_replay']['trace_count']} "
                f"heldout={result['heldout_replay']['replayed_traces']}/{result['heldout_replay']['trace_count']} "
                f"neg={result['negative_probe']['rejected_negative_traces']}/{result['negative_probe']['negative_trace_count']} "
                f"ops={result['operation_counts']['total']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
