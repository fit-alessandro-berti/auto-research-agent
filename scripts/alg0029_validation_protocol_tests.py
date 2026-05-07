"""Split validation/final tests for ALG-0029 and ALG-0030 composition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import body_count_validation_product_selector
import body_inclusion_validation_selector
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
Body = Tuple[str, ...]


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


def _trace_set(log: TraceLog) -> set[tuple[str, ...]]:
    return {tuple(trace) for trace in log}


def _sorted_traces(traces: set[tuple[str, ...]]) -> TraceLog:
    return [list(trace) for trace in sorted(traces)]


def _leakage(case: Dict[str, Any]) -> Dict[str, TraceLog]:
    train = _trace_set(case["train"])
    validation = _trace_set(case["validation_positive"]) | _trace_set(case["validation_negative"])
    final = _trace_set(case["final_positive"]) | _trace_set(case["final_negative"])
    return {
        "train_validation_overlap": _sorted_traces(train & validation),
        "train_final_overlap": _sorted_traces(train & final),
        "validation_final_overlap": _sorted_traces(validation & final),
    }


def _has_leakage(leakage: Dict[str, TraceLog]) -> bool:
    return any(bool(traces) for traces in leakage.values())


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def body_protocol_cases() -> List[Dict[str, Any]]:
    train_3_to_1 = _loop_log(("B",), 3, {("C",): 1})
    train_5_to_1 = _loop_log(("B",), 5, {("C",): 1})
    return [
        {
            "name": "body_keep_final_generalization",
            "description": "Validation requires rare-body repeat behavior; final probes check another rare repeat.",
            "train": train_3_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [["B", "A", "D"], ["A", "B", "B", "D"]],
            "guard_policy": {},
            "expected_alternative": "keep_all_bodies",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "body_filter_final_precision",
            "description": "Validation rejects rare-body combinations; final probes check different rare-body repeats.",
            "train": train_3_to_1,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)]), _repeat_sequence([("C",), ("B",), ("B",)])],
            "guard_policy": {},
            "expected_alternative": "support_guard",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "body_no_signal_final_not_used",
            "description": "Validation does not distinguish body inclusion, although final probes would.",
            "train": train_3_to_1,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "guard_policy": {},
            "expected_alternative": None,
            "expected_status": "unresolved",
            "expected_leakage": False,
        },
        {
            "name": "body_validation_final_overlap_guard",
            "description": "Protocol should flag validation/final reuse even when selection succeeds.",
            "train": train_3_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"]],
            "final_positive": [_repeat_sequence([("C",), ("B",)])],
            "final_negative": [["A", "D", "B"]],
            "guard_policy": {},
            "expected_alternative": "keep_all_bodies",
            "expected_status": "selected",
            "expected_leakage": True,
        },
        {
            "name": "body_training_negative_conflict_final_control",
            "description": "Validation negative contains an observed rare training trace.",
            "train": train_3_to_1,
            "validation_positive": [],
            "validation_negative": [_one_iteration(("C",))],
            "final_positive": [],
            "final_negative": [_repeat_sequence([("C",), ("B",)])],
            "guard_policy": {},
            "expected_alternative": None,
            "expected_status": "validation_training_conflict",
            "expected_leakage": True,
        },
        {
            "name": "body_positive_negative_overlap",
            "description": "The same trace appears in positive and negative validation.",
            "train": train_3_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "guard_policy": {},
            "expected_alternative": None,
            "expected_status": "validation_inconsistent",
            "expected_leakage": False,
        },
        {
            "name": "body_support_ratio_5_to_1_keep",
            "description": "Validation can override a stricter 5:1 support-guard policy when rare behavior is valid.",
            "train": train_5_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [["B", "A", "D"]],
            "guard_policy": {
                "min_dominant_count": 5,
                "min_dominant_share_numerator": 5,
                "min_dominant_share_denominator": 6,
                "rare_body_count": 1,
            },
            "expected_alternative": "keep_all_bodies",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "body_length2_rare_filter",
            "description": "Dominant and rare loop bodies both have length two; validation rejects rare-body combinations.",
            "train": _loop_log(("B", "C"), 5, {("E", "G"): 1}, suffix="F"),
            "validation_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
            "validation_negative": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "final_positive": [_repeat_sequence([("B", "C"), ("B", "C"), ("B", "C")], suffix="F")],
            "final_negative": [_repeat_sequence([("E", "G"), ("E", "G")], suffix="F")],
            "guard_policy": {
                "min_dominant_count": 5,
                "min_dominant_share_numerator": 5,
                "min_dominant_share_denominator": 6,
                "rare_body_count": 1,
            },
            "expected_alternative": "support_guard",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "two_rare_one_valid_one_noise_unresolved",
            "description": "Two singleton rare bodies include one valid and one noisy case; current alternatives cannot distinguish them separately.",
            "train": _loop_log(("B",), 5, {("C",): 1, ("E",): 1}),
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "guard_policy": {},
            "expected_alternative": None,
            "expected_status": "unresolved",
            "expected_leakage": False,
        },
        {
            "name": "rare_count_two_noise_unresolved",
            "description": "Rare body count two is outside the singleton-count support guard.",
            "train": _loop_log(("B",), 5, {("C",): 2}),
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "guard_policy": {},
            "expected_alternative": None,
            "expected_status": "unresolved",
            "expected_leakage": False,
        },
    ]


def evaluate_body_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        guard_policy=case.get("guard_policy"),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get("body_inclusion_validation_selector", {})
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    leakage = _leakage(case)
    has_leakage = _has_leakage(leakage)
    selection_ok = (
        selector.get("selected_alternative") == case["expected_alternative"]
        and selector.get("selection_status") == case["expected_status"]
    )
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    leakage_ok = has_leakage == case["expected_leakage"]
    final_required = case["expected_alternative"] is not None and not case["expected_leakage"]
    protocol_pass = selection_ok and leakage_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_alternative": case["expected_alternative"],
        "expected_status": case["expected_status"],
        "expected_leakage": case["expected_leakage"],
        "selected_alternative": selector.get("selected_alternative"),
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "leakage": leakage,
        "has_leakage": has_leakage,
        "selection_ok": selection_ok,
        "final_ok": final_ok,
        "leakage_ok": leakage_ok,
        "protocol_pass": protocol_pass,
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "operation_counts": result.get("operation_counts"),
        "scores": selector.get("scores", []),
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def composition_cases() -> List[Dict[str, Any]]:
    train = _loop_log(("B",), 3, {("C",): 1})
    return [
        {
            "name": "keep_all_unbounded_joint",
            "description": "Rare body is valid and repeated loops are valid.",
            "train": train,
            "body_validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "body_validation_negative": [["A", "B", "D"]],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "count_validation_negative": [["A", "B", "D"]],
            "final_positive": [_repeat_sequence([("C",), ("C",), ("B",)])],
            "final_negative": [["A", "D", "B"]],
            "expected_body": "keep_all_bodies",
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
        },
        {
            "name": "keep_all_at_most_once_joint",
            "description": "Rare body is valid, but repeated loop iterations are invalid.",
            "train": train,
            "body_validation_positive": [_one_iteration(("C",))],
            "body_validation_negative": [["A", "B", "D"]],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B",), ("B",)]), ["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [_repeat_sequence([("C",), ("B",)]), _repeat_sequence([("B",), ("B",), ("B",)])],
            "expected_body": "keep_all_bodies",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "filter_unbounded_joint",
            "description": "Rare body is filtered, while repeated dominant loops are valid.",
            "train": train,
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
            "name": "filter_at_most_once_joint",
            "description": "Rare body is filtered and repeated loop iterations are invalid.",
            "train": train,
            "body_validation_positive": [_one_iteration(("B",))],
            "body_validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "count_validation_positive": [],
            "count_validation_negative": [_repeat_sequence([("B",), ("B",)]), ["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [_repeat_sequence([("C",), ("C",)]), _repeat_sequence([("B",), ("B",), ("B",)])],
            "expected_body": "support_guard",
            "expected_policy": "at_most_once",
            "expected_status": "selected",
        },
        {
            "name": "body_selected_count_unresolved",
            "description": "Body validation selects support guard, but count validation is non-discriminating.",
            "train": train,
            "body_validation_positive": [_one_iteration(("B",))],
            "body_validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "count_validation_positive": [],
            "count_validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": "support_guard",
            "expected_policy": None,
            "expected_status": "count_unresolved",
        },
        {
            "name": "count_selected_body_unresolved",
            "description": "Count evidence would select unbounded repeat, but body validation does not distinguish alternatives.",
            "train": train,
            "body_validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "body_validation_negative": [["A", "B", "D"]],
            "count_validation_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "count_validation_negative": [["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [],
            "expected_body": None,
            "expected_policy": None,
            "expected_status": "body_unresolved",
        },
    ]


def evaluate_composition_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = body_count_validation_product_selector.select(
        case["train"],
        case["body_validation_positive"],
        case["body_validation_negative"],
        case["count_validation_positive"],
        case["count_validation_negative"],
    )
    evidence = result.get("pmir", {}).get("evidence", {})
    selector = evidence.get("body_count_validation_product_selector", {})
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    selection_ok = (
        selector.get("selected_body_alternative") == case["expected_body"]
        and selector.get("selected_count_policy") == case["expected_policy"]
        and selector.get("selection_status") == case["expected_status"]
    )
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    final_required = case["expected_status"] == "selected"
    protocol_pass = selection_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_body": case["expected_body"],
        "expected_policy": case["expected_policy"],
        "expected_status": case["expected_status"],
        "selected_body": selector.get("selected_body_alternative"),
        "selected_policy": selector.get("selected_count_policy"),
        "selection_status": selector.get("selection_status"),
        "body_selector_status": selector.get("body_selector_status"),
        "count_selector_status": selector.get("count_selector_status"),
        "reason": selector.get("reason"),
        "selection_ok": selection_ok,
        "final_ok": final_ok,
        "protocol_pass": protocol_pass,
        "operation_counts": result.get("operation_counts"),
        "selector": selector,
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_tests() -> Dict[str, Any]:
    body_cases = {case["name"]: evaluate_body_case(case) for case in body_protocol_cases()}
    composition = {case["name"]: evaluate_composition_case(case) for case in composition_cases()}
    return {
        "body_protocol": {
            "cases": body_cases,
            "summary": {
                "case_count": len(body_cases),
                "passed": sum(1 for case in body_cases.values() if case["protocol_pass"]),
                "failed": [name for name, case in body_cases.items() if not case["protocol_pass"]],
            },
        },
        "composition_protocol": {
            "cases": composition,
            "summary": {
                "case_count": len(composition),
                "passed": sum(1 for case in composition.values() if case["protocol_pass"]),
                "failed": [name for name, case in composition.items() if not case["protocol_pass"]],
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0029-validation-protocol-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["body_protocol"]["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        print(
            f"{case_name}: expected={case['expected_alternative']} selected={case['selected_alternative']} "
            f"status={case['selection_status']} leakage={case['has_leakage']} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"pass={case['protocol_pass']}"
        )
    for case_name, case in results["composition_protocol"]["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        print(
            f"{case_name}: expected=({case['expected_body']},{case['expected_policy']}) "
            f"selected=({case['selected_body']},{case['selected_policy']}) status={case['selection_status']} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"pass={case['protocol_pass']}"
        )
    failed = (
        results["body_protocol"]["summary"]["failed"]
        + results["composition_protocol"]["summary"]["failed"]
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
