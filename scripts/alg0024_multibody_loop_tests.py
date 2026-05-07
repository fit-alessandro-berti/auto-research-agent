"""Targeted tests for ALG-0024 multi-body rework-loop choice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from alg0023_loop_tests import _input_stats, candidate_functions, evaluate_candidate


TraceLog = List[List[str]]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "loop_unbounded_control",
            "description": "Singleton loop control where ALG-0024 should preserve ALG-0023's unbounded rework behavior.",
            "train": [["A", "C"], ["A", "B", "A", "C"], ["A", "B", "A", "C"]],
            "heldout": [["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "B", "C"], ["A", "A", "C"], ["B", "A", "C"]],
        },
        {
            "name": "bounded_at_most_one_rework",
            "description": "Same zero/one evidence as an unbounded loop, interpreted as an at-most-one domain.",
            "train": [["A", "C"], ["A", "B", "A", "C"], ["A", "B", "A", "C"]],
            "heldout": [],
            "negative": [["A", "B", "A", "B", "A", "C"], ["A", "B", "C"], ["A", "A", "C"]],
        },
        {
            "name": "multi_body_loop_choice",
            "description": "Two singleton rework bodies around the same anchor should compile as a loop-body choice.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"]],
            "negative": [["A", "B", "D"], ["A", "C", "D"], ["A", "A", "D"]],
        },
        {
            "name": "nested_choice_loop_context",
            "description": "The same body-choice loop embedded in sequence context.",
            "train": [["S", "A", "E"], ["S", "A", "B", "A", "E"], ["S", "A", "C", "A", "E"]],
            "heldout": [["S", "A", "B", "A", "C", "A", "E"]],
            "negative": [["S", "A", "B", "E"], ["S", "A", "C", "E"], ["S", "A", "A", "E"]],
        },
        {
            "name": "one_iteration_only",
            "description": "A loop cut should not fire when no zero-iteration exit is observed.",
            "train": [["A", "B", "A", "C"], ["A", "B", "A", "C"], ["A", "B", "A", "C"]],
            "heldout": [["A", "C"], ["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "B", "C"], ["A", "A", "C"], ["B", "A", "C"]],
        },
    ]


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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0024-multibody-loop-tests.json"))
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
