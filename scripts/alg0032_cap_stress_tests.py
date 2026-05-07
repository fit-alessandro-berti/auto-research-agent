"""Operation-budget stress tests for ALG-0032 rare-body cap behavior."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import per_body_inclusion_validation_selector
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
Body = Tuple[str, ...]


RARE_LABELS = ["C", "E", "F", "G", "H", "I"]


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
    rare_count: int,
    dominant_count: int = 5,
    rare_observation_count: int = 1,
    suffix: str = "D",
) -> TraceLog:
    if rare_count > len(RARE_LABELS):
        raise ValueError("rare_count exceeds available deterministic labels")
    log = [["A", suffix]]
    for _ in range(dominant_count):
        log.append(_one_iteration(("B",), suffix))
    for label in RARE_LABELS[:rare_count]:
        for _ in range(rare_observation_count):
            log.append(_one_iteration((label,), suffix))
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


def stress_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "rare_count_1_cap_1_selected_under_budget",
            "rare_count": 1,
            "max_rare_bodies": 1,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "selected",
            "expected_alternative_count": 2,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_count_1_cap_1_drop_nonbase_under_budget",
            "rare_count": 1,
            "max_rare_bodies": 1,
            "validation_mode": "drop_all",
            "expected_status": "selected",
            "expected_alternative_count": 2,
            "expected_dropped": _body_rows([("C",)]),
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_count_2_cap_2_selected_over_budget",
            "rare_count": 2,
            "max_rare_bodies": 2,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "selected",
            "expected_alternative_count": 4,
            "expected_dropped": _body_rows([("E",)]),
            "expected_shared_over_deep_budget": True,
        },
        {
            "name": "rare_count_2_cap_1_refuses_under_budget",
            "rare_count": 2,
            "max_rare_bodies": 1,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "too_many_rare_bodies",
            "expected_alternative_count": 0,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_count_3_cap_3_selected_over_budget",
            "rare_count": 3,
            "max_rare_bodies": 3,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "selected",
            "expected_alternative_count": 8,
            "expected_dropped": _body_rows([("E",), ("F",)]),
            "expected_shared_over_deep_budget": True,
        },
        {
            "name": "rare_count_4_cap_4_selected_over_budget",
            "rare_count": 4,
            "max_rare_bodies": 4,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "selected",
            "expected_alternative_count": 16,
            "expected_dropped": _body_rows([("E",), ("F",), ("G",)]),
            "expected_shared_over_deep_budget": True,
        },
        {
            "name": "rare_count_4_cap_3_refuses_under_budget",
            "rare_count": 4,
            "max_rare_bodies": 3,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "too_many_rare_bodies",
            "expected_alternative_count": 0,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_count_5_cap_5_selected_over_budget_reference",
            "rare_count": 5,
            "max_rare_bodies": 5,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "selected",
            "expected_alternative_count": 32,
            "expected_dropped": _body_rows([("E",), ("F",), ("G",), ("H",)]),
            "expected_shared_over_deep_budget": True,
        },
        {
            "name": "rare_count_3_cap_2_refuses_under_budget",
            "rare_count": 3,
            "max_rare_bodies": 2,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "too_many_rare_bodies",
            "expected_alternative_count": 0,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_count_5_cap_4_refuses_under_budget",
            "rare_count": 5,
            "max_rare_bodies": 4,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "too_many_rare_bodies",
            "expected_alternative_count": 0,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
        {
            "name": "rare_body_count_mismatch_no_alternatives",
            "rare_count": 1,
            "rare_observation_count": 2,
            "rare_body_count": 1,
            "max_rare_bodies": 1,
            "validation_mode": "keep_first_drop_rest",
            "expected_status": "no_per_body_alternatives",
            "expected_alternative_count": 0,
            "expected_dropped": [],
            "expected_shared_over_deep_budget": False,
        },
    ]


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    rare_count = case["rare_count"]
    rare_bodies = [(label,) for label in RARE_LABELS[:rare_count]]
    train = _loop_log(
        rare_count,
        rare_observation_count=case.get("rare_observation_count", 1),
    )
    total_body_observations = 5 + rare_count * case.get("rare_observation_count", 1)
    validation_mode = case.get("validation_mode", "keep_first_drop_rest")
    if validation_mode == "drop_all":
        validation_positive = [_repeat_sequence([("B",), ("B",)])]
        validation_negative = [_repeat_sequence([body, ("B",)]) for body in rare_bodies]
        final_positive = [_repeat_sequence([("B",), ("B",), ("B",)])]
        final_negative = [_repeat_sequence([body, body]) for body in rare_bodies]
    elif validation_mode == "keep_first_drop_rest":
        validation_positive = [_repeat_sequence([rare_bodies[0], ("B",)])]
        validation_negative = [
            _repeat_sequence([body, ("B",)])
            for body in rare_bodies[1:]
        ]
        final_positive = [_repeat_sequence([rare_bodies[0], rare_bodies[0]])]
        final_negative = [
            _repeat_sequence([body, body])
            for body in rare_bodies[1:]
        ] + [
            _repeat_sequence([rare_bodies[0], body])
            for body in rare_bodies[1:]
        ]
    else:
        raise ValueError(f"unknown validation_mode: {validation_mode}")
    result = per_body_inclusion_validation_selector.select(
        train,
        validation_positive,
        validation_negative,
        min_dominant_share_denominator=case.get(
            "min_dominant_share_denominator",
            total_body_observations,
        ),
        rare_body_count=case.get("rare_body_count", 1),
        max_rare_bodies=case["max_rare_bodies"],
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "per_body_inclusion_validation_selector", {}
    )
    operation_counts = result.get("operation_counts", {})
    stats = _input_stats(train)
    deep_budget = stats["deep_soft_budget"]
    naive_total = operation_counts.get("total_with_all_alternatives_and_validation_proxy")
    shared_total = operation_counts.get("total_with_shared_alternatives_and_validation_proxy")
    all_alternative_total = operation_counts.get("all_alternative_discovery_total", 0)
    shared_discovery_total = operation_counts.get("shared_all_alternative_discovery_total", 0)
    selector_total = operation_counts.get("selector_total", 0)
    validation_proxy_total = operation_counts.get("validation_replay_proxy_total", 0)
    savings = operation_counts.get("shared_savings_vs_all_alternatives", 0)
    shared_identity_ok = (
        shared_total == shared_discovery_total + selector_total + validation_proxy_total
    )
    naive_identity_ok = (
        naive_total == all_alternative_total + selector_total + validation_proxy_total
    )
    savings_identity_ok = savings == naive_total - shared_total
    shared_not_above_naive = shared_total <= naive_total
    shared_over_deep_budget = shared_total > deep_budget
    scores = selector.get("scores", [])
    valid_score_count = sum(1 for row in scores if row.get("validates_all"))
    selection_ok = (
        selector.get("selection_status") == case["expected_status"]
        and selector.get("alternative_count") == case["expected_alternative_count"]
        and selector.get("selected_dropped_bodies", []) == case["expected_dropped"]
    )
    score_ok = case["expected_status"] != "selected" or valid_score_count == 1
    no_enumeration_ok = True
    if case["expected_status"] != "selected":
        no_enumeration_ok = (
            selector.get("alternative_count") == 0
            and validation_proxy_total == 0
            and savings == 0
            and shared_total == naive_total
        )
    budget_ok = shared_over_deep_budget == case["expected_shared_over_deep_budget"]
    final_positive_replay = _replay_summary(result["petri_net"], final_positive)
    final_negative_probe = precision_probe(result["petri_net"], final_negative)
    final_required = case["expected_status"] == "selected"
    final_ok = (
        final_positive_replay["replayed_traces"] == final_positive_replay["trace_count"]
        and final_negative_probe["accepted_negative_traces"] == 0
    )
    pass_case = (
        selection_ok
        and budget_ok
        and shared_identity_ok
        and naive_identity_ok
        and savings_identity_ok
        and shared_not_above_naive
        and score_ok
        and no_enumeration_ok
        and (not final_required or final_ok)
    )
    return {
        "rare_count": rare_count,
        "max_rare_bodies": case["max_rare_bodies"],
        "expected_status": case["expected_status"],
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "selected_alternative": selector.get("selected_alternative"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "alternative_count": selector.get("alternative_count"),
        "input_stats": stats,
        "deep_soft_budget": deep_budget,
        "naive_total_with_validation_proxy": naive_total,
        "shared_total_with_validation_proxy": shared_total,
        "shared_savings_vs_naive": savings,
        "shared_budget_ratio": 0.0 if deep_budget == 0 else shared_total / deep_budget,
        "naive_budget_ratio": 0.0 if deep_budget == 0 else naive_total / deep_budget,
        "shared_over_deep_budget": shared_over_deep_budget,
        "expected_shared_over_deep_budget": case["expected_shared_over_deep_budget"],
        "selection_ok": selection_ok,
        "budget_ok": budget_ok,
        "valid_score_count": valid_score_count,
        "score_ok": score_ok,
        "no_enumeration_ok": no_enumeration_ok,
        "shared_identity_ok": shared_identity_ok,
        "naive_identity_ok": naive_identity_ok,
        "savings_identity_ok": savings_identity_ok,
        "shared_not_above_naive": shared_not_above_naive,
        "final_ok": final_ok,
        "protocol_pass": pass_case,
        "operation_counts": operation_counts,
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "shared_operation_accounting": selector.get("shared_operation_accounting"),
        "final_positive_replay": final_positive_replay,
        "final_negative_probe": final_negative_probe,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in stress_cases()}
    selected_cases = [
        name for name, case in cases.items()
        if case["selection_status"] == "selected"
    ]
    refused_cases = [
        name for name, case in cases.items()
        if case["selection_status"] == "too_many_rare_bodies"
    ]
    selected_over_budget = [
        name for name in selected_cases
        if cases[name]["shared_over_deep_budget"]
    ]
    max_shared_case = max(
        cases,
        key=lambda name: cases[name]["shared_total_with_validation_proxy"],
    )
    max_naive_case = max(
        cases,
        key=lambda name: cases[name]["naive_total_with_validation_proxy"],
    )
    return {
        "candidate_id": "ALG-0032",
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "passed": sum(1 for case in cases.values() if case["protocol_pass"]),
            "failed": [name for name, case in cases.items() if not case["protocol_pass"]],
            "selected_cases": selected_cases,
            "refused_cases": refused_cases,
            "selected_over_deep_budget": selected_over_budget,
            "first_selected_over_deep_budget": (
                selected_over_budget[0] if selected_over_budget else None
            ),
            "max_shared_case": max_shared_case,
            "max_shared_total": cases[max_shared_case]["shared_total_with_validation_proxy"],
            "max_naive_case": max_naive_case,
            "max_naive_total": cases[max_naive_case]["naive_total_with_validation_proxy"],
            "max_alternative_count": max(
                case["alternative_count"] for case in cases.values()
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/alg0032-cap-stress-tests.json"),
    )
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        print(
            f"{case_name}: status={case['selection_status']} "
            f"alternatives={case['alternative_count']} "
            f"shared={case['shared_total_with_validation_proxy']} "
            f"naive={case['naive_total_with_validation_proxy']} "
            f"budget={case['deep_soft_budget']} "
            f"ratio={case['shared_budget_ratio']:.2f} "
            f"pass={case['protocol_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
