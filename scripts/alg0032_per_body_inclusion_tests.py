"""Smoke and counterexample tests for ALG-0032 per-body inclusion selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import body_inclusion_validation_selector
import per_body_inclusion_validation_selector
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


def _body_rows(bodies: Sequence[Body]) -> List[List[str]]:
    return [list(body) for body in sorted(bodies)]


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def _selector_kwargs(case: Dict[str, Any]) -> Dict[str, int]:
    return {
        "min_dominant_count": case.get("min_dominant_count", 5),
        "min_dominant_share_numerator": case.get("min_dominant_share_numerator", 5),
        "min_dominant_share_denominator": case.get("min_dominant_share_denominator", 7),
        "rare_body_count": case.get("rare_body_count", 1),
        "max_rare_bodies": case.get("max_rare_bodies", 2),
    }


def _alg0029_baseline(case: Dict[str, Any]) -> Dict[str, Any]:
    guard_policy = {
        "min_dominant_count": case.get("min_dominant_count", 5),
        "min_dominant_share_numerator": case.get("min_dominant_share_numerator", 5),
        "min_dominant_share_denominator": case.get("min_dominant_share_denominator", 7),
        "rare_body_count": case.get("rare_body_count", 1),
    }
    result = body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        guard_policy=guard_policy,
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "body_inclusion_validation_selector", {}
    )
    return {
        "selected_alternative": selector.get("selected_alternative"),
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
    }


def test_cases() -> List[Dict[str, Any]]:
    train_5_to_1 = _loop_log(("B",), 5, {("C",): 1})
    train_two_rare = _loop_log(("B",), 5, {("C",): 1, ("E",): 1})
    train_two_rare_count_two = _loop_log(("B",), 5, {("C",): 2, ("E",): 2})
    return [
        {
            "name": "one_rare_valid_include",
            "description": "Validation requires the rare body, so the per-body vector should keep it.",
            "train": train_5_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [["B", "A", "D"], ["A", "C", "D"]],
            "expected_status": "selected",
            "expected_dropped": [],
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
        },
        {
            "name": "one_rare_noise_exclude",
            "description": "Validation rejects rare-body combinations, so the rare body should be dropped.",
            "train": train_5_to_1,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("C",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
        },
        {
            "name": "two_rare_one_valid_one_noise",
            "description": "Direct repair target: keep C but drop E under the same rare count.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("E",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
        },
        {
            "name": "two_rare_both_valid",
            "description": "Validation requires both rare bodies, so no rare body should be dropped.",
            "train": train_two_rare,
            "validation_positive": [
                _repeat_sequence([("C",), ("B",)]),
                _repeat_sequence([("E",), ("B",)]),
            ],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("E",), ("B",)])],
            "final_negative": [["A", "C", "D"], ["E", "A", "D"]],
            "expected_status": "selected",
            "expected_dropped": [],
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
        },
        {
            "name": "two_rare_both_noise",
            "description": "Validation rejects both rare bodies, so both rare bodies should be dropped.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [
                _repeat_sequence([("C",), ("B",)]),
                _repeat_sequence([("E",), ("B",)]),
            ],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [
                _repeat_sequence([("C",), ("C",)]),
                _repeat_sequence([("E",), ("E",)]),
                _repeat_sequence([("C",), ("E",)]),
            ],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("C",), ("E",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
        },
        {
            "name": "count_two_mixed_valid_noise",
            "description": "Count-two rare bodies can be split when an explicit 5/9 support policy is declared.",
            "train": train_two_rare_count_two,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "min_dominant_share_numerator": 5,
            "min_dominant_share_denominator": 9,
            "rare_body_count": 2,
            "expected_status": "selected",
            "expected_dropped": _body_rows([("E",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
        },
        {
            "name": "partial_signal_ambiguous",
            "description": "Validation distinguishes C but gives no signal about E, so selection must stay unresolved.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "unresolved",
            "expected_dropped": [],
            "expected_reason": "tie_or_conflicting_per_body_validation_evidence",
        },
        {
            "name": "positive_negative_overlap",
            "description": "The same validation trace appears as positive and negative.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "validation_inconsistent",
            "expected_dropped": [],
            "expected_reason": "validation_trace_is_both_positive_and_negative",
        },
        {
            "name": "training_negative_conflict",
            "description": "A validation negative is an observed training trace.",
            "train": train_two_rare,
            "validation_positive": [],
            "validation_negative": [_one_iteration(("C",))],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "validation_training_conflict",
            "expected_dropped": [],
            "expected_reason": "validation_negative_contains_training_trace",
        },
        {
            "name": "too_many_rare_bodies_budget",
            "description": "Rare-body enumeration is capped to avoid an unbounded inclusion-vector product.",
            "train": _loop_log(("B",), 5, {("C",): 1, ("E",): 1, ("F",): 1}),
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "min_dominant_share_denominator": 8,
            "max_rare_bodies": 2,
            "expected_status": "too_many_rare_bodies",
            "expected_dropped": [],
            "expected_reason": "rare_body_alternative_budget_exceeded",
        },
        {
            "name": "dominance_threshold_not_met",
            "description": "No per-body selection should occur without the declared dominant-support context.",
            "train": _loop_log(("B",), 3, {("C",): 1, ("E",): 1}),
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "dominance_threshold_not_met",
            "expected_dropped": [],
            "expected_reason": "dominant_count_below_threshold",
        },
    ]


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = per_body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        **_selector_kwargs(case),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "per_body_inclusion_validation_selector", {}
    )
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    baseline = _alg0029_baseline(case) if case.get("compare_alg0029") else None
    selection_ok = (
        selector.get("selection_status") == case["expected_status"]
        and selector.get("selected_dropped_bodies", []) == case["expected_dropped"]
        and selector.get("reason") == case["expected_reason"]
    )
    baseline_ok = True
    if baseline is not None:
        baseline_ok = baseline.get("selection_status") == case["expected_alg0029_status"]
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    final_required = case["expected_status"] == "selected"
    protocol_pass = selection_ok and baseline_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_status": case["expected_status"],
        "expected_reason": case["expected_reason"],
        "expected_dropped": case["expected_dropped"],
        "selection_status": selector.get("selection_status"),
        "selected_alternative": selector.get("selected_alternative"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "reason": selector.get("reason"),
        "alternative_count": selector.get("alternative_count"),
        "selection_ok": selection_ok,
        "baseline_ok": baseline_ok,
        "final_ok": final_ok,
        "protocol_pass": protocol_pass,
        "alg0029_baseline": baseline,
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "operation_counts": result.get("operation_counts"),
        "scores": selector.get("scores", []),
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in test_cases()}
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "passed": sum(1 for case in cases.values() if case["protocol_pass"]),
            "failed": [name for name, case in cases.items() if not case["protocol_pass"]],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0032-per-body-inclusion-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        baseline = case["alg0029_baseline"]
        baseline_text = ""
        if baseline is not None:
            baseline_text = f" alg0029={baseline['selection_status']}"
        print(
            f"{case_name}: status={case['selection_status']} reason={case['reason']} "
            f"dropped={case['selected_dropped_bodies']} alternatives={case['alternative_count']} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']}"
            f"{baseline_text} pass={case['protocol_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
