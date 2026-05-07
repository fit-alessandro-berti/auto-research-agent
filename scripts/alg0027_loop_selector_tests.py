"""Evaluate ALG-0027 validation selection for loop-count policy sets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from alg0023_loop_tests import _input_stats
from petri_eval import precision_probe, replay_log
import loop_count_validation_selector


TraceLog = List[List[str]]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "single_rework_selects_unbounded",
            "description": "Validation positives include a second singleton-loop iteration.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [["A", "B", "A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "C"], ["A", "A", "C"], ["B", "A", "C"]],
            "expected_policy": "unbounded_repeat",
        },
        {
            "name": "single_rework_selects_at_most_once",
            "description": "Validation negatives declare a second singleton-loop iteration invalid.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "B", "A", "C"], ["A", "B", "C"], ["A", "A", "C"]],
            "expected_policy": "at_most_once",
        },
        {
            "name": "multi_body_selects_unbounded",
            "description": "Validation positives include repeated singleton-body loop combinations.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "validation_positive": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"]],
            "validation_negative": [["A", "B", "D"], ["A", "C", "D"], ["A", "A", "D"]],
            "expected_policy": "unbounded_repeat",
        },
        {
            "name": "multi_body_selects_at_most_once",
            "description": "Validation negatives declare repeated singleton-body combinations invalid.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"], ["A", "B", "D"], ["A", "A", "D"]],
            "expected_policy": "at_most_once",
        },
        {
            "name": "length2_selects_unbounded",
            "description": "Validation positives include repeated length-2 body combinations.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "validation_positive": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"]],
            "validation_negative": [["A", "B", "C", "F"], ["A", "D", "E", "F"], ["A", "A", "F"]],
            "expected_policy": "unbounded_repeat",
        },
        {
            "name": "length2_selects_at_most_once",
            "description": "Validation negatives declare repeated length-2 body combinations invalid.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"], ["A", "B", "C", "F"], ["A", "A", "F"]],
            "expected_policy": "at_most_once",
        },
        {
            "name": "mixed_width_selects_unbounded",
            "description": "Validation positives include repeated mixed singleton and length-2 bodies.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "validation_positive": [["A", "B", "A", "C", "D", "A", "F"], ["A", "C", "D", "A", "C", "D", "A", "F"]],
            "validation_negative": [["A", "B", "F"], ["A", "C", "D", "F"], ["A", "A", "F"], ["A", "D", "C", "A", "F"]],
            "expected_policy": "unbounded_repeat",
        },
        {
            "name": "no_discriminator_unresolved",
            "description": "Validation probes do not distinguish unbounded from at-most-once behavior.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "C"], ["A", "A", "C"]],
            "expected_policy": None,
        },
        {
            "name": "conflicting_validation_unresolved",
            "description": "The same second-iteration trace is presented as both positive and negative.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [["A", "B", "A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "A", "B", "A", "C"]],
            "expected_policy": None,
        },
        {
            "name": "optional_skip_no_policy_set",
            "description": "No loop policy set exists, so validation cannot select a loop-count policy.",
            "train": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"]],
            "validation_positive": [["A", "B", "C"]],
            "validation_negative": [["A", "B", "B", "C"], ["A", "C", "B"], ["B", "C"]],
            "expected_policy": None,
        },
    ]


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = loop_count_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
    )
    evidence = result.get("pmir", {}).get("evidence", {})
    selector = evidence.get("loop_count_validation_selector", {})
    selected_net = result["petri_net"]
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_policy": case["expected_policy"],
        "selected_policy": selector.get("selected_policy"),
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "operation_counts": result.get("operation_counts"),
        "scores": selector.get("scores", []),
        "validation_positive_replay": _replay_summary(selected_net, case["validation_positive"]),
        "validation_negative_probe": precision_probe(selected_net, case["validation_negative"]),
    }


def run_tests() -> Dict[str, Any]:
    results: Dict[str, Any] = {"cases": {}}
    for case in test_cases():
        results["cases"][case["name"]] = evaluate_case(case)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0027-loop-selector-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["validation_positive_replay"]
        negative = case["validation_negative_probe"]
        print(
            f"{case_name}: expected={case['expected_policy']} selected={case['selected_policy']} "
            f"status={case['selection_status']} reason={case['reason']} "
            f"val_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"val_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"selector_ops={case['selector_operation_counts']['total']}"
        )


if __name__ == "__main__":
    main()
