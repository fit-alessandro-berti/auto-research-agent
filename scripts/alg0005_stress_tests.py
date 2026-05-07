"""Stress tests for ALG-0005 prefix automaton compression.

These tests focus on the exact-replay tradeoff: variant explosion, held-out
interleavings, and memorized noise. They also keep a process-tree comparator in
the same output so exact replay is not mistaken for process generalization.
"""

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


def _perm_traces(branches: List[str], limit: int | None = None) -> TraceLog:
    traces = [["A", *perm, "E"] for perm in permutations(branches)]
    return traces if limit is None else traces[:limit]


def _negative_for_branches(branches: List[str]) -> TraceLog:
    return [
        ["A", *branches[:-1], "E"],
        ["A", branches[0], branches[0], *branches[1:], "E"],
        [branches[0], *branches[1:], "E"],
    ]


def stress_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = [
        {
            "name": "heldout_parallel_prefix_biased_2_of_6",
            "description": "Train on two prefix-sharing interleavings; hold out the remaining valid interleavings.",
            "train": _perm_traces(["B", "C", "D"], limit=2),
            "heldout": _perm_traces(["B", "C", "D"])[2:],
            "negative": _negative_for_branches(["B", "C", "D"]),
        },
        {
            "name": "heldout_parallel_balanced_2_of_6",
            "description": "Train on two interleavings without a common middle prefix; hold out the remaining valid interleavings.",
            "train": [["A", "B", "C", "D", "E"], ["A", "C", "D", "B", "E"]],
            "heldout": [
                trace
                for trace in _perm_traces(["B", "C", "D"])
                if trace not in [["A", "B", "C", "D", "E"], ["A", "C", "D", "B", "E"]]
            ],
            "negative": _negative_for_branches(["B", "C", "D"]),
        },
        {
            "name": "heldout_optional_concurrency",
            "description": "Train on the optional-concurrency counterexample and hold out other valid branch orders.",
            "train": [["A", "B", "D", "C", "E"], ["A", "C", "B", "D", "E"], ["A", "B", "C", "E"]],
            "heldout": [["A", "C", "B", "E"], ["A", "B", "C", "D", "E"]],
            "negative": [["A", "D", "B", "C", "E"], ["A", "B", "D", "D", "C", "E"], ["A", "E"]],
        },
        {
            "name": "noise_memorization",
            "description": "A rare reversed trace is included in training but treated as clean-model negative evidence.",
            "train": [["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "B", "C", "D"], ["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
        },
    ]
    for width in range(2, 6):
        branches = [chr(ord("B") + index) for index in range(width)]
        cases.append(
            {
                "name": f"all_permutations_width_{width}",
                "description": "Train on every interleaving of a parallel block to profile variant growth.",
                "train": _perm_traces(branches),
                "heldout": [],
                "negative": _negative_for_branches(branches),
            }
        )
    return cases


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "cut_limited_process_tree": importlib.import_module("cut_limited_process_tree").discover,
        "prefix_automaton_compression": importlib.import_module("prefix_automaton_compression").discover,
        "prefix_block_abstraction": importlib.import_module("prefix_block_abstraction").discover,
        "pmir_guarded_split_join": importlib.import_module("pmir_guarded_split_join").discover,
        "pmir_conflict_aware_optional": importlib.import_module("pmir_conflict_aware_optional").discover,
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
    stats = _input_stats(train)
    ops = result["operation_counts"]["total"]
    return {
        "candidate_id": result["candidate_id"],
        "operation_counts": result["operation_counts"],
        "operation_budget": stats["deep_soft_budget"],
        "operation_budget_ratio": 0.0 if stats["deep_soft_budget"] == 0 else ops / stats["deep_soft_budget"],
        "structural_summary": result["structural_summary"],
        "train_replay": {
            "replayed_traces": train_replay["replayed_traces"],
            "trace_count": train_replay["trace_count"],
            "failed_examples": train_replay["failed_examples"],
            "structural_diagnostics": train_replay["structural_diagnostics"],
        },
        "heldout_replay": {
            "replayed_traces": heldout_replay["replayed_traces"],
            "trace_count": heldout_replay["trace_count"],
            "failed_examples": heldout_replay["failed_examples"],
        },
        "negative_probe": negative_probe,
        "compression": {
            "raw_trie_nodes": evidence.get("raw_trie_nodes"),
            "compressed_states": evidence.get("compressed_states"),
            "compressed_edges": evidence.get("compressed_edges"),
            "merge_group_count": len(evidence.get("state_merges", {})) if isinstance(evidence.get("state_merges"), dict) else None,
            "variant_count": evidence.get("variant_count"),
        },
        "selected_cut": evidence.get("selected_cut") or evidence.get("selected_grammar"),
    }


def run_stress_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in stress_cases():
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0005-stress-tests.json"))
    args = parser.parse_args()

    results = run_stress_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        prefix = case["results"]["prefix_automaton_compression"]
        block = case["results"]["prefix_block_abstraction"]
        tree = case["results"]["cut_limited_process_tree"]
        print(
            f"{case_name}: ALG-0005 ops={prefix['operation_counts']['total']} "
            f"budget_ratio={prefix['operation_budget_ratio']:.2f} "
            f"train={prefix['train_replay']['replayed_traces']}/{prefix['train_replay']['trace_count']} "
            f"heldout={prefix['heldout_replay']['replayed_traces']}/{prefix['heldout_replay']['trace_count']} "
            f"neg_reject={prefix['negative_probe']['rejected_negative_traces']}/{prefix['negative_probe']['negative_trace_count']} "
            f"states={prefix['compression']['compressed_states']}; "
            f"ALG-0014 ops={block['operation_counts']['total']} "
            f"train={block['train_replay']['replayed_traces']}/{block['train_replay']['trace_count']} "
            f"heldout={block['heldout_replay']['replayed_traces']}/{block['heldout_replay']['trace_count']} "
            f"neg_reject={block['negative_probe']['rejected_negative_traces']}/{block['negative_probe']['negative_trace_count']} "
            f"grammar={block['selected_cut']}; "
            f"ALG-0003 heldout={tree['heldout_replay']['replayed_traces']}/{tree['heldout_replay']['trace_count']} "
            f"cut={tree['selected_cut']}"
        )


if __name__ == "__main__":
    main()
