"""Noisy/incomplete-log and prefix-merge ambiguity tests for ALG-0015."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from petri_eval import precision_probe, replay_log
import prefix_block_abstraction


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


PREFIX_BIASED_TRAIN = [["A", "B", "C", "D", "E"], ["A", "B", "D", "C", "E"]]
PREFIX_LATE_B_HELDOUT = [
    ["A", "C", "B", "D", "E"],
    ["A", "C", "D", "B", "E"],
    ["A", "D", "B", "C", "E"],
    ["A", "D", "C", "B", "E"],
]


def repeated_trace(trace: List[str], count: int) -> TraceLog:
    return [list(trace) for _ in range(count)]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "prefix_merge_full_parallel_interpretation",
            "description": "Same observations as the sequence-prefix case, interpreted as incomplete three-way parallel behavior.",
            "train": PREFIX_BIASED_TRAIN,
            "heldout": PREFIX_LATE_B_HELDOUT,
            "negative": [["A", "B", "C", "E"], ["A", "B", "B", "C", "D", "E"], ["B", "C", "D", "E"]],
            "interpretation": "late-B traces should replay",
        },
        {
            "name": "prefix_merge_sequence_then_parallel_interpretation",
            "description": "Same observations as the full-parallel case, interpreted as B followed by parallel C/D.",
            "train": PREFIX_BIASED_TRAIN,
            "heldout": [],
            "negative": PREFIX_LATE_B_HELDOUT,
            "interpretation": "late-B traces should be rejected",
        },
        {
            "name": "noise_reversal_2_to_1",
            "description": "Two dominant sequence traces plus one rare reversal.",
            "train": repeated_trace(["A", "B", "C", "D"], 2) + [["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
            "interpretation": "rare reversal treated as noise",
        },
        {
            "name": "noise_reversal_3_to_1",
            "description": "Three dominant sequence traces plus one rare reversal.",
            "train": repeated_trace(["A", "B", "C", "D"], 3) + [["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
            "interpretation": "rare reversal treated as noise",
        },
        {
            "name": "noise_reversal_5_to_1",
            "description": "Five dominant sequence traces plus one rare reversal.",
            "train": repeated_trace(["A", "B", "C", "D"], 5) + [["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "C", "B", "D"]],
            "interpretation": "rare reversal treated as noise",
        },
        {
            "name": "valid_rare_parallel_3_to_1",
            "description": "Same 3-to-1 observations as noise_reversal_3_to_1, interpreted as valid but imbalanced parallel behavior.",
            "train": repeated_trace(["A", "B", "C", "D"], 3) + [["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
            "interpretation": "rare reversal should replay",
        },
        {
            "name": "incomplete_parallel_one_order_2",
            "description": "Only one order of a possible parallel pair is observed twice.",
            "train": repeated_trace(["A", "B", "C", "D"], 2),
            "heldout": [["A", "C", "B", "D"]],
            "negative": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
            "interpretation": "held-out reversal may be valid if the log is incomplete",
        },
        {
            "name": "balanced_reversal_tie",
            "description": "Balanced order evidence should not trigger dominant-sequence noise handling.",
            "train": [["A", "B", "C", "D"], ["A", "C", "B", "D"]],
            "heldout": [],
            "negative": [["A", "D"], ["A", "B", "D"], ["A", "C", "D"]],
            "interpretation": "balanced reversal remains parallel-like",
        },
    ]


def _alg0015_variant(
    max_skew: Optional[int],
    ratio: int,
    min_count: int = 2,
    prefix_merge_policy: str = "before_common",
    allow_exact_fallback: bool = True,
) -> DiscoverFn:
    def discover(log: TraceLog) -> Dict[str, Any]:
        return prefix_block_abstraction.discover(
            log,
            max_parallel_support_skew=max_skew,
            enable_prefix_merge=True,
            enable_dominant_sequence=True,
            allow_exact_fallback=allow_exact_fallback,
            prefix_merge_policy=prefix_merge_policy,
            min_dominant_count=min_count,
            min_dominant_ratio_percent=ratio,
            candidate_id_override="ALG-0015",
            name_override="Prefix Block Support-Guard Miner Sweep Variant",
        )

    return discover


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "prefix_block_abstraction": importlib.import_module("prefix_block_abstraction").discover,
        "prefix_block_support_only": importlib.import_module("prefix_block_support_only").discover,
        "prefix_block_prefix_merge_only": importlib.import_module("prefix_block_prefix_merge_only").discover,
        "prefix_block_dominant_only": importlib.import_module("prefix_block_dominant_only").discover,
        "prefix_block_support_guard": importlib.import_module("prefix_block_support_guard").discover,
        "prefix_block_grammar_only": importlib.import_module("prefix_block_grammar_only").discover,
        "prefix_block_conservative_merge": importlib.import_module("prefix_block_conservative_merge").discover,
        "prefix_block_ambiguity_aware": importlib.import_module("prefix_block_ambiguity_aware").discover,
        "sweep_skew1_ratio60": _alg0015_variant(1, 60),
        "sweep_skew2_ratio60": _alg0015_variant(2, 60),
        "sweep_skew2_ratio75": _alg0015_variant(2, 75),
        "sweep_skew2_ratio85": _alg0015_variant(2, 85),
        "sweep_skew3_ratio60": _alg0015_variant(3, 60),
        "sweep_no_skew_ratio60": _alg0015_variant(None, 60),
        "sweep_conservative_skew2_ratio60": _alg0015_variant(2, 60, prefix_merge_policy="after_common_rejects"),
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
    ambiguity = evidence.get("ambiguity", {})
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
        "ambiguity": ambiguity,
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


def run_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "candidates": sorted(candidates)}
    for case in test_cases():
        case_result: Dict[str, Any] = {
            "description": case["description"],
            "interpretation": case["interpretation"],
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0015-noise-incomplete-tests.json"))
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
                f"{name} grammar={result['selected_grammar']} "
                f"origin={result['grammar_origin']} "
                f"train={result['train_replay']['replayed_traces']}/{result['train_replay']['trace_count']} "
                f"heldout={result['heldout_replay']['replayed_traces']}/{result['heldout_replay']['trace_count']} "
                f"neg={result['negative_probe']['rejected_negative_traces']}/{result['negative_probe']['negative_trace_count']} "
                f"ambiguous={result['ambiguity'].get('detected')} "
                f"ops={result['operation_counts']['total']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
