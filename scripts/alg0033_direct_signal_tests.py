"""Smoke and counterexample tests for ALG-0033 direct-signal selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import per_body_direct_signal_selector
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
        "max_rare_bodies": case.get("max_rare_bodies", 5),
    }


def test_cases() -> List[Dict[str, Any]]:
    train_5_to_1 = _loop_log(("B",), 5, {("C",): 1})
    train_two_rare = _loop_log(("B",), 5, {("C",): 1, ("E",): 1})
    train_two_rare_count_two = _loop_log(("B",), 5, {("C",): 2, ("E",): 2})
    train_three_rare = _loop_log(("B",), 5, {("C",): 1, ("E",): 1, ("F",): 1})
    train_five_rare = _loop_log(
        ("B",),
        5,
        {("C",): 1, ("E",): 1, ("F",): 1, ("G",): 1, ("H",): 1},
    )
    return [
        {
            "name": "one_rare_valid_include",
            "description": "Positive validation contains the rare body, so the direct rule keeps it.",
            "train": train_5_to_1,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [["B", "A", "D"], ["A", "C", "D"]],
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": [],
        },
        {
            "name": "one_rare_noise_exclude",
            "description": "A singleton rare-body negative gives a direct drop signal.",
            "train": train_5_to_1,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("C",)]),
        },
        {
            "name": "two_rare_one_valid_one_noise",
            "description": "Mixed rare bodies are handled without enumerating all four assignments.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("E",)]),
            "compare_exhaustive_cost": True,
            "expect_direct_lower_than_exhaustive": True,
            "expect_direct_under_deep_budget": True,
        },
        {
            "name": "two_rare_both_valid",
            "description": "Two direct positive signals keep both rare bodies.",
            "train": train_two_rare,
            "validation_positive": [
                _repeat_sequence([("C",), ("B",)]),
                _repeat_sequence([("E",), ("B",)]),
            ],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("E",), ("B",)])],
            "final_negative": [["A", "C", "D"], ["E", "A", "D"]],
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": [],
        },
        {
            "name": "two_rare_both_noise",
            "description": "Two singleton negative signals drop both rare bodies.",
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
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("C",), ("E",)]),
            "compare_exhaustive_cost": True,
            "expect_direct_lower_than_exhaustive": True,
            "expect_direct_under_deep_budget": True,
        },
        {
            "name": "count_two_mixed_valid_noise",
            "description": "Configured count-two rare bodies can be split by direct validation signals.",
            "train": train_two_rare_count_two,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "min_dominant_share_numerator": 5,
            "min_dominant_share_denominator": 9,
            "rare_body_count": 2,
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("E",)]),
            "compare_exhaustive_cost": True,
            "expect_direct_lower_than_exhaustive": True,
            "expect_direct_under_deep_budget": True,
        },
        {
            "name": "unit_propagation_negative_clause",
            "description": "Positive validation requires C; a C+E negative then unit-propagates to dropping E.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("E",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("E",)]),
            "compare_exhaustive_cost": True,
            "expect_direct_lower_than_exhaustive": True,
            "expect_direct_under_deep_budget": True,
            "expected_exhaustive_status": "selected",
        },
        {
            "name": "rare_count_3_direct_scale_under_budget",
            "description": "Three rare bodies are selected from one positive keep signal and singleton drop signals without eight assignments.",
            "train": train_three_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [
                _repeat_sequence([("E",), ("B",)]),
                _repeat_sequence([("F",), ("B",)]),
            ],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [
                _repeat_sequence([("E",), ("E",)]),
                _repeat_sequence([("F",), ("F",)]),
                _repeat_sequence([("C",), ("E",)]),
            ],
            "min_dominant_share_denominator": 8,
            "max_rare_bodies": 5,
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("E",), ("F",)]),
            "expect_direct_under_deep_budget": True,
        },
        {
            "name": "rare_count_5_direct_scale_under_budget_reference",
            "description": "Five rare bodies stay on a linear direct-signal path instead of a 32-assignment exhaustive path.",
            "train": train_five_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [
                _repeat_sequence([("E",), ("B",)]),
                _repeat_sequence([("F",), ("B",)]),
                _repeat_sequence([("G",), ("B",)]),
                _repeat_sequence([("H",), ("B",)]),
            ],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [
                _repeat_sequence([("E",), ("E",)]),
                _repeat_sequence([("F",), ("F",)]),
                _repeat_sequence([("G",), ("G",)]),
                _repeat_sequence([("H",), ("H",)]),
                _repeat_sequence([("C",), ("E",)]),
            ],
            "min_dominant_share_denominator": 10,
            "max_rare_bodies": 5,
            "expected_status": "selected",
            "expected_reason": "direct_body_signals_identify_assignment",
            "expected_dropped": _body_rows([("E",), ("F",), ("G",), ("H",)]),
            "expect_direct_under_deep_budget": True,
        },
        {
            "name": "partial_signal_unresolved",
            "description": "Validation keeps C but gives no direct signal about E.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "partial_direct_signal",
            "expected_reason": "missing_direct_body_signal",
            "expected_dropped": [],
        },
        {
            "name": "body_signal_conflict",
            "description": "The same rare body appears in positive and singleton-negative validation traces.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("C",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "body_signal_conflict",
            "expected_reason": "rare_body_has_positive_and_negative_direct_signal",
            "expected_dropped": [],
        },
        {
            "name": "interaction_negative_ambiguous",
            "description": "A non-unit negative with no otherwise classified rare body stays unresolved.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("E",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "interaction_ambiguous",
            "expected_reason": "negative_trace_mentions_multiple_rare_bodies_without_direct_assignment",
            "expected_dropped": [],
            "compare_exhaustive_cost": True,
            "expected_exhaustive_status": "unresolved",
        },
        {
            "name": "too_many_rare_bodies_budget",
            "description": "The direct rule still keeps an explicit rare-body cap, though no 2^R alternatives are built.",
            "train": _loop_log(("B",), 5, {("C",): 1, ("E",): 1, ("F",): 1}),
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "min_dominant_share_denominator": 8,
            "max_rare_bodies": 2,
            "expected_status": "too_many_rare_bodies",
            "expected_reason": "rare_body_alternative_budget_exceeded",
            "expected_dropped": [],
        },
        {
            "name": "dominance_threshold_not_met",
            "description": "The direct rule is scoped to the same dominant-support context as ALG-0032.",
            "train": _loop_log(("B",), 3, {("C",): 1, ("E",): 1}),
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "dominance_threshold_not_met",
            "expected_reason": "dominant_count_below_threshold",
            "expected_dropped": [],
        },
        {
            "name": "positive_negative_overlap",
            "description": "Validation labels are inconsistent when the same trace is positive and negative.",
            "train": train_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "validation_inconsistent",
            "expected_reason": "validation_trace_is_both_positive_and_negative",
            "expected_dropped": [],
        },
        {
            "name": "training_negative_conflict",
            "description": "A validation negative must not be an observed training trace.",
            "train": train_two_rare,
            "validation_positive": [],
            "validation_negative": [_one_iteration(("C",))],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "validation_training_conflict",
            "expected_reason": "validation_negative_contains_training_trace",
            "expected_dropped": [],
        },
    ]


def _exhaustive_baseline(case: Dict[str, Any]) -> Dict[str, Any]:
    result = per_body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        **_selector_kwargs(case),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "per_body_inclusion_validation_selector", {}
    )
    operation_counts = result.get("operation_counts", {})
    return {
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "alternative_count": selector.get("alternative_count"),
        "shared_total_with_validation_proxy": operation_counts.get(
            "total_with_shared_alternatives_and_validation_proxy"
        ),
        "naive_total_with_validation_proxy": operation_counts.get(
            "total_with_all_alternatives_and_validation_proxy"
        ),
    }


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = per_body_direct_signal_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        **_selector_kwargs(case),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "per_body_direct_signal_selector", {}
    )
    operation_counts = result.get("operation_counts", {})
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    exhaustive = _exhaustive_baseline(case) if case.get("compare_exhaustive_cost") else None
    stats = _input_stats(case["train"])
    direct_total = operation_counts.get("total_with_selector_and_validation_proxy", 0)
    direct_under_budget = direct_total <= stats["deep_soft_budget"]
    exhaustive_shared_total = (
        exhaustive.get("shared_total_with_validation_proxy") if exhaustive else None
    )
    direct_lower_than_exhaustive = (
        exhaustive_shared_total is not None
        and direct_total < exhaustive_shared_total
    )
    selection_ok = (
        selector.get("selection_status") == case["expected_status"]
        and selector.get("reason") == case["expected_reason"]
        and selector.get("selected_dropped_bodies", []) == case["expected_dropped"]
    )
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    final_required = case["expected_status"] == "selected"
    cost_ok = True
    if "expect_direct_lower_than_exhaustive" in case:
        cost_ok = cost_ok and direct_lower_than_exhaustive == case["expect_direct_lower_than_exhaustive"]
    if "expect_direct_under_deep_budget" in case:
        cost_ok = cost_ok and direct_under_budget == case["expect_direct_under_deep_budget"]
    if "expected_exhaustive_status" in case:
        cost_ok = cost_ok and exhaustive is not None and exhaustive.get("selection_status") == case[
            "expected_exhaustive_status"
        ]
    protocol_pass = selection_ok and cost_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": stats,
        "expected_status": case["expected_status"],
        "expected_reason": case["expected_reason"],
        "expected_dropped": case["expected_dropped"],
        "selection_status": selector.get("selection_status"),
        "selected_alternative": selector.get("selected_alternative"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "reason": selector.get("reason"),
        "alternative_count": selector.get("alternative_count"),
        "avoided_exhaustive_alternative_count": selector.get("avoided_exhaustive_alternative_count"),
        "selection_ok": selection_ok,
        "cost_ok": cost_ok,
        "final_ok": final_ok,
        "protocol_pass": protocol_pass,
        "direct_total_with_validation_proxy": direct_total,
        "direct_under_deep_budget": direct_under_budget,
        "direct_budget_ratio": (
            0.0 if stats["deep_soft_budget"] == 0 else direct_total / stats["deep_soft_budget"]
        ),
        "direct_lower_than_exhaustive": direct_lower_than_exhaustive,
        "exhaustive_baseline": exhaustive,
        "direct_signal_assignment": selector.get("direct_signal_assignment"),
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "operation_counts": operation_counts,
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in test_cases()}
    selected_cases = {
        name: case for name, case in cases.items() if case["selection_status"] == "selected"
    }
    return {
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "passed": sum(1 for case in cases.values() if case["protocol_pass"]),
            "failed": [name for name, case in cases.items() if not case["protocol_pass"]],
            "selected_case_count": len(selected_cases),
            "max_direct_total_with_validation_proxy": max(
                (case["direct_total_with_validation_proxy"] for case in cases.values()),
                default=0,
            ),
            "selected_cases_over_deep_budget": [
                name for name, case in selected_cases.items() if not case["direct_under_deep_budget"]
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0033-direct-signal-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        exhaustive = case["exhaustive_baseline"]
        exhaustive_text = ""
        if exhaustive is not None:
            exhaustive_text = (
                f" exhaustive={exhaustive['selection_status']} "
                f"shared={exhaustive['shared_total_with_validation_proxy']}"
            )
        print(
            f"{case_name}: status={case['selection_status']} reason={case['reason']} "
            f"dropped={case['selected_dropped_bodies']} direct_total="
            f"{case['direct_total_with_validation_proxy']} budget_ratio="
            f"{case['direct_budget_ratio']:.2f} final_ok={case['final_ok']}"
            f"{exhaustive_text} pass={case['protocol_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
