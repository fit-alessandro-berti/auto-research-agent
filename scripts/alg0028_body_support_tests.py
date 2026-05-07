"""Targeted smoke tests for ALG-0028 body-support loop guard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Dict, List

from alg0023_loop_tests import _input_stats
from petri_eval import precision_probe, replay_log

import cut_limited_body_support_guard
import cut_limited_length_bounded_loop


TraceLog = List[List[str]]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


def candidate_functions() -> Dict[str, DiscoverFn]:
    return {
        "cut_limited_length_bounded_loop": cut_limited_length_bounded_loop.discover,
        "cut_limited_body_support_guard": cut_limited_body_support_guard.discover,
    }


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "rare_body_noise_3_to_1",
            "description": "A singleton-supported body under a 3:1 dominant body prior is treated as noise.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "B", "A", "B", "A", "D"]],
            "negative": [["A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"]],
            "expect_guard": {
                "applied": True,
                "filtered_bodies": [["C"]],
                "train_replay": [4, 5],
                "heldout_replay": [1, 1],
                "negative_rejected": [2, 2],
            },
        },
        {
            "name": "rare_body_valid_3_to_1_documented_failure",
            "description": "The same support pattern may be valid rare behavior; the pure support prior should document this failure mode.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "C", "A", "B", "A", "D"], ["A", "C", "A", "C", "A", "D"]],
            "negative": [],
            "expect_guard": {
                "applied": True,
                "filtered_bodies": [["C"]],
                "train_replay": [4, 5],
                "heldout_replay": [0, 2],
                "negative_rejected": [0, 0],
            },
        },
        {
            "name": "balanced_two_body_choice",
            "description": "Balanced body alternatives are kept because support alone does not identify noise.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"]],
            "negative": [["A", "B", "D"], ["A", "C", "D"]],
            "expect_guard": {
                "applied": False,
                "train_replay": [5, 5],
                "heldout_replay": [2, 2],
                "negative_rejected": [2, 2],
            },
        },
        {
            "name": "low_sample_2_to_1_ambiguous",
            "description": "A 2:1 support skew is too weak for the default rare-body filter.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "C", "A", "B", "A", "D"]],
            "negative": [["A", "B", "D"], ["A", "C", "D"]],
            "expect_guard": {
                "applied": False,
                "train_replay": [4, 4],
                "heldout_replay": [1, 1],
                "negative_rejected": [2, 2],
            },
        },
        {
            "name": "length2_rare_body_noise",
            "description": "A singleton-supported length-2 body is filtered, while the dominant length-2 body remains repeatable.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "B", "C", "A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [["A", "B", "C", "A", "B", "C", "A", "F"]],
            "negative": [["A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"]],
            "expect_guard": {
                "applied": True,
                "filtered_bodies": [["D", "E"]],
                "train_replay": [4, 5],
                "heldout_replay": [1, 1],
                "negative_rejected": [2, 2],
            },
        },
        {
            "name": "mixed_width_rare_singleton_noise",
            "description": "A dominant singleton body can remain after filtering a singleton-supported length-2 body.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "B", "A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "heldout": [["A", "B", "A", "B", "A", "F"]],
            "negative": [["A", "C", "D", "A", "F"], ["A", "C", "D", "A", "B", "A", "F"]],
            "expect_guard": {
                "applied": True,
                "filtered_bodies": [["C", "D"]],
                "train_replay": [4, 5],
                "heldout_replay": [1, 1],
                "negative_rejected": [2, 2],
            },
        },
        {
            "name": "two_rare_bodies_no_dominant",
            "description": "Two singleton rare bodies with only weak dominance are kept rather than over-filtered.",
            "train": [["A", "Z"], ["A", "B", "A", "Z"], ["A", "B", "A", "Z"], ["A", "C", "A", "Z"], ["A", "D", "A", "Z"]],
            "heldout": [["A", "C", "A", "D", "A", "Z"]],
            "negative": [["A", "C", "Z"], ["A", "D", "Z"]],
            "expect_guard": {
                "applied": False,
                "train_replay": [5, 5],
                "heldout_replay": [1, 1],
                "negative_rejected": [2, 2],
            },
        },
    ]


def _guard_evidence(result: Dict[str, Any]) -> Dict[str, Any]:
    return result.get("pmir", {}).get("evidence", {}).get("support_guard", {})


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
        "support_guard": evidence.get("support_guard", {}),
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


def _result_guard_evidence(result: Dict[str, Any]) -> Dict[str, Any]:
    return result.get("support_guard", {})


def _expectation_result(result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    guard = _result_guard_evidence(result)
    checks: Dict[str, bool] = {}
    checks["guard_applied"] = guard.get("applied") == expected.get("applied")
    if "filtered_bodies" in expected:
        checks["filtered_bodies"] = guard.get("filtered_bodies") == expected["filtered_bodies"]
    checks["train_replay"] = [
        result["train_replay"]["replayed_traces"],
        result["train_replay"]["trace_count"],
    ] == expected["train_replay"]
    checks["heldout_replay"] = [
        result["heldout_replay"]["replayed_traces"],
        result["heldout_replay"]["trace_count"],
    ] == expected["heldout_replay"]
    checks["negative_rejected"] = [
        result["negative_probe"]["rejected_negative_traces"],
        result["negative_probe"]["negative_trace_count"],
    ] == expected["negative_rejected"]
    return {"passed": all(checks.values()), "checks": checks}


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
            evaluated = evaluate_candidate(discover, case["train"], case["heldout"], case["negative"])
            if name == "cut_limited_body_support_guard":
                evaluated["expectation"] = _expectation_result(evaluated, case["expect_guard"])
            case_result["results"][name] = evaluated
        results["cases"][case["name"]] = case_result
    results["all_expectations_passed"] = all(
        case["results"]["cut_limited_body_support_guard"]["expectation"]["passed"]
        for case in results["cases"].values()
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0028-body-support-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        pieces = []
        for name in results["candidates"]:
            result = case["results"][name]
            guard = result.get("support_guard", {})
            pieces.append(
                f"{name} cut={result['selected_cut']} guard={guard.get('applied')} "
                f"train={result['train_replay']['replayed_traces']}/{result['train_replay']['trace_count']} "
                f"heldout={result['heldout_replay']['replayed_traces']}/{result['heldout_replay']['trace_count']} "
                f"neg={result['negative_probe']['rejected_negative_traces']}/{result['negative_probe']['negative_trace_count']} "
                f"ops={result['operation_counts']['total']}"
            )
        expectation = case["results"]["cut_limited_body_support_guard"]["expectation"]["passed"]
        print(f"{case_name}: expectation={expectation}; " + "; ".join(pieces))
    if not results["all_expectations_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
