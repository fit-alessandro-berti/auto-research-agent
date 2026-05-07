"""Stress tests for ALG-0030 body-count product selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import body_count_validation_product_selector
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
Body = Tuple[str, ...]


RARE_COUNT_TWO_POLICY = {
    "min_dominant_count": 5,
    "min_dominant_share_numerator": 5,
    "min_dominant_share_denominator": 7,
    "rare_body_count": 2,
}

FIVE_TO_ONE_POLICY = {
    "min_dominant_count": 5,
    "min_dominant_share_numerator": 5,
    "min_dominant_share_denominator": 6,
    "rare_body_count": 1,
}


def _one_iteration(body: Body, suffix: str = "D") -> List[str]:
    return ["A"] + list(body) + ["A", suffix]


def _repeat_sequence(bodies: Sequence[Body], suffix: str = "D") -> List[str]:
    trace = ["A"]
    for body in bodies:
        trace.extend(body)
        trace.append("A")
    trace.append(suffix)
    return trace


def _loop_log(
    dominant_body: Body,
    dominant_count: int,
    rare_counts: Dict[Body, int],
    suffix: str = "D",
) -> TraceLog:
    log = [["A", suffix]]
    for _ in range(dominant_count):
        log.append(_one_iteration(dominant_body, suffix))
    for body, count in sorted(rare_counts.items()):
        for _ in range(count):
            log.append(_one_iteration(body, suffix))
    return log


def stress_cases() -> List[Dict[str, Any]]:
    length2_train = _loop_log(("B", "C"), 5, {("E", "G"): 1}, suffix="F")
    mixed_train = _loop_log(("B",), 5, {("C", "E"): 1}, suffix="F")
    mixed_reverse_train = _loop_log(("B", "C"), 5, {("E",): 1}, suffix="F")
    rare_count_two_train = _loop_log(("B",), 5, {("C",): 2})
    two_rare_count_two_train = _loop_log(("B",), 5, {("C",): 2, ("E",): 2})
    return [
        {
            "name": "length2_keep_all_unbounded",
            "description": "Length-2 rare body is valid and repeated loops are valid.",
            "train": length2_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "count_validation_negative": [["A", "B", "C", "F"], ["A", "A", "F"]],
            "final_positive": [_repeat_sequence([("E", "G"), ("E", "G"), ("B", "C")], suffix="F")],
            "final_negative": [["A", "E", "G", "F"], ["A", "F", "B"]],
            "expected_body": "keep_all_bodies",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "length2_keep_all_at_most_once",
            "description": "Length-2 rare body is valid, but repeated loop iterations are invalid.",
            "train": length2_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [],
            "count_validation_negative": [
                _repeat_sequence([("B", "C"), ("B", "C")], suffix="F"),
                _repeat_sequence([("E", "G"), ("B", "C")], suffix="F"),
            ],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("E", "G"), ("E", "G")], suffix="F"),
                _repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F"),
            ],
            "expected_body": "keep_all_bodies",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "length2_filter_unbounded",
            "description": "Length-2 rare body is filtered while repeated dominant loops are valid.",
            "train": length2_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
            "body_validation_negative": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "count_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "count_validation_negative": [["A", "B", "C", "F"]],
            "final_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "final_negative": [_repeat_sequence([("E", "G"), ("E", "G")], suffix="F")],
            "expected_body": "support_guard",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "length2_filter_at_most_once",
            "description": "Length-2 rare body is treated as noise and repeated loops are invalid.",
            "train": length2_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_one_iteration(("B", "C"), suffix="F")],
            "body_validation_negative": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F"), ["A", "B", "C", "F"]],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("E", "G"), ("E", "G")], suffix="F"),
                _repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F"),
            ],
            "expected_body": "support_guard",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_singleton_dominant_keep_all_unbounded",
            "description": "Dominant singleton and rare length-2 body are both valid with unbounded repeat.",
            "train": mixed_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)], suffix="F")],
            "count_validation_negative": [["A", "B", "F"]],
            "final_positive": [_repeat_sequence([("C", "E"), ("C", "E"), ("B",)], suffix="F")],
            "final_negative": [["A", "C", "E", "F"]],
            "expected_body": "keep_all_bodies",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_singleton_dominant_keep_all_at_most_once",
            "description": "Mixed singleton/length-2 rare body is valid, but repeated loop iterations are invalid.",
            "train": mixed_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B",), ("B",)], suffix="F"), ["A", "B", "F"]],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("C", "E"), ("B",)], suffix="F"),
                _repeat_sequence([("B",), ("B",), ("B",)], suffix="F"),
            ],
            "expected_body": "keep_all_bodies",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_singleton_dominant_filter_unbounded",
            "description": "Mixed singleton/length-2 rare body is noise while repeated dominant loops are valid.",
            "train": mixed_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("B",), ("B",)], suffix="F")],
            "body_validation_negative": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)], suffix="F")],
            "count_validation_negative": [["A", "B", "F"]],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",), ("B",)], suffix="F")],
            "final_negative": [_repeat_sequence([("C", "E"), ("C", "E")], suffix="F")],
            "expected_body": "support_guard",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_singleton_dominant_filter_at_most_once",
            "description": "Dominant singleton remains valid, rare length-2 body and repeated loops are rejected.",
            "train": mixed_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_one_iteration(("B",), suffix="F")],
            "body_validation_negative": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B",), ("B",)], suffix="F"), ["A", "B", "F"]],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("C", "E"), ("C", "E")], suffix="F"),
                _repeat_sequence([("B",), ("B",), ("B",)], suffix="F"),
            ],
            "expected_body": "support_guard",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_length2_dominant_keep_all_unbounded",
            "description": "Dominant length-2 and rare singleton body are both valid with unbounded repeat.",
            "train": mixed_reverse_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("E",), ("B", "C")], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "count_validation_negative": [["A", "B", "C", "F"]],
            "final_positive": [_repeat_sequence([("E",), ("E",), ("B", "C")], suffix="F")],
            "final_negative": [["A", "E", "F"]],
            "expected_body": "keep_all_bodies",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_length2_dominant_keep_all_at_most_once",
            "description": "Rare singleton body is valid, but repeated loop iterations are invalid.",
            "train": mixed_reverse_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("E",), ("B", "C")], suffix="F")],
            "body_validation_negative": [["A", "B", "F"]],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F"), ["A", "B", "C", "F"]],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("E",), ("B", "C")], suffix="F"),
                _repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F"),
            ],
            "expected_body": "keep_all_bodies",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_length2_dominant_filter_unbounded",
            "description": "Rare singleton body is filtered while repeated dominant length-2 loops are valid.",
            "train": mixed_reverse_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
            "body_validation_negative": [_repeat_sequence([("E",), ("B", "C")], suffix="F")],
            "count_validation_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "count_validation_negative": [["A", "B", "C", "F"]],
            "final_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "final_negative": [_repeat_sequence([("E",), ("E",)], suffix="F")],
            "expected_body": "support_guard",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "mixed_width_length2_dominant_filter_at_most_once",
            "description": "Rare singleton body is filtered and repeated dominant length-2 loops are invalid.",
            "train": mixed_reverse_train,
            "guard_policy": FIVE_TO_ONE_POLICY,
            "body_validation_positive": [_one_iteration(("B", "C"), suffix="F")],
            "body_validation_negative": [_repeat_sequence([("E",), ("B", "C")], suffix="F")],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F"), ["A", "B", "C", "F"]],
            "final_positive": [],
            "final_negative": [
                _repeat_sequence([("E",), ("E",)], suffix="F"),
                _repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F"),
            ],
            "expected_body": "support_guard",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "duplicate_suffix_label_body_unresolved",
            "description": "Duplicate body/suffix labels block body selection before count-policy selection.",
            "train": [["S", "A", "B"], ["S", "A", "B", "A", "B"], ["S", "A", "C", "A", "B"]],
            "body_validation_positive": [["S", "A", "C", "A", "B", "A", "B"]],
            "body_validation_negative": [["S", "A", "C", "B"]],
            "count_validation_positive": [["S", "A", "C", "A", "B", "A", "B"]],
            "count_validation_negative": [["S", "A", "B", "B"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
        {
            "name": "overlapping_body_labels_body_unresolved",
            "description": "Overlapping body labels block upstream body-policy evidence.",
            "train": [["A", "Z"], ["A", "B", "C", "A", "Z"], ["A", "C", "D", "A", "Z"]],
            "body_validation_positive": [["A", "B", "C", "A", "C", "D", "A", "Z"]],
            "body_validation_negative": [["A", "B", "C", "Z"]],
            "count_validation_positive": [["A", "B", "C", "A", "C", "D", "A", "Z"]],
            "count_validation_negative": [["A", "A", "Z"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
        {
            "name": "length3_body_body_unresolved",
            "description": "Length-3 body alternatives exceed the upstream fixed body-length bound.",
            "train": [["A", "Z"], ["A", "B", "C", "D", "A", "Z"], ["A", "E", "F", "G", "A", "Z"]],
            "body_validation_positive": [["A", "B", "C", "D", "A", "E", "F", "G", "A", "Z"]],
            "body_validation_negative": [["A", "B", "C", "D", "Z"]],
            "count_validation_positive": [["A", "B", "C", "D", "A", "E", "F", "G", "A", "Z"]],
            "count_validation_negative": [["A", "A", "Z"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
        {
            "name": "one_iteration_only_body_unresolved",
            "description": "One-iteration-only evidence does not expose body or count alternatives.",
            "train": [["A", "B", "A", "D"]],
            "body_validation_positive": [["A", "B", "A", "B", "A", "D"]],
            "body_validation_negative": [["A", "B", "D"]],
            "count_validation_positive": [["A", "B", "A", "B", "A", "D"]],
            "count_validation_negative": [["A", "A", "D"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
        {
            "name": "rare_count_two_default_body_unresolved",
            "description": "Default rare-count-one support guard cannot filter a count-two rare body.",
            "train": rare_count_two_train,
            "body_validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "body_validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "count_validation_negative": [["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
        {
            "name": "rare_count_two_configured_filter_unbounded",
            "description": "Configured rare-count-two policy filters a count-two rare body, while count validation selects unbounded repeat.",
            "train": rare_count_two_train,
            "guard_policy": RARE_COUNT_TWO_POLICY,
            "body_validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "body_validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "count_validation_negative": [["A", "B", "D"]],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "expected_body": "support_guard",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "rare_count_two_configured_keep_all_at_most_once",
            "description": "Configured rare-count-two policy can still be overridden when validation requires the rare body.",
            "train": rare_count_two_train,
            "guard_policy": RARE_COUNT_TWO_POLICY,
            "body_validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "body_validation_negative": [["A", "B", "D"]],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B",), ("B",)]), ["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [_repeat_sequence([("C",), ("C",)]), _repeat_sequence([("B",), ("B",), ("B",)])],
            "expected_body": "keep_all_bodies",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "two_rare_count_two_one_valid_one_noise_unresolved",
            "description": "Group count-two filtering cannot keep one rare body while filtering another.",
            "train": two_rare_count_two_train,
            "guard_policy": RARE_COUNT_TWO_POLICY,
            "body_validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "body_validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "count_validation_negative": [["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
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
    result = body_count_validation_product_selector.select(
        case["train"],
        case["body_validation_positive"],
        case["body_validation_negative"],
        case["count_validation_positive"],
        case["count_validation_negative"],
        guard_policy=case.get("guard_policy"),
    )
    evidence = result.get("pmir", {}).get("evidence", {})
    selector = evidence.get("body_count_validation_product_selector", {})
    body_selector = evidence.get("body_inclusion_validation_selector", {})
    policy_set = evidence.get("loop_count_policy_set", {})
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    selection_ok = (
        selector.get("selected_body_alternative") == case["expected_body"]
        and selector.get("selected_count_policy") == case["expected_policy"]
        and selector.get("selection_status") == case["expected_status"]
    )
    final_required = case["expected_status"] == "selected"
    stress_pass = selection_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "guard_policy": case.get("guard_policy", {}),
        "expected_body": case["expected_body"],
        "expected_policy": case["expected_policy"],
        "expected_status": case["expected_status"],
        "selected_body": selector.get("selected_body_alternative"),
        "selected_policy": selector.get("selected_count_policy"),
        "selection_status": selector.get("selection_status"),
        "body_selector_status": selector.get("body_selector_status"),
        "count_selector_status": selector.get("count_selector_status"),
        "body_selector_reason": body_selector.get("reason"),
        "product_reason": selector.get("reason"),
        "policy_set_detected": bool(policy_set.get("detected")),
        "selection_ok": selection_ok,
        "final_ok": final_ok,
        "stress_pass": stress_pass,
        "operation_counts": result.get("operation_counts"),
        "selector": selector,
        "body_selector": body_selector,
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in stress_cases()}
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "passed": sum(1 for case in cases.values() if case["stress_pass"]),
            "failed": [name for name, case in cases.items() if not case["stress_pass"]],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0030-product-stress-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        total = case["operation_counts"].get("total_with_product_selector_and_validation_proxy")
        print(
            f"{case_name}: expected=({case['expected_body']},{case['expected_policy']}) "
            f"selected=({case['selected_body']},{case['selected_policy']}) "
            f"status={case['selection_status']} policy_set={case['policy_set_detected']} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"total={total} pass={case['stress_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
