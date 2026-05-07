"""Split validation/final tests for ALG-0032 per-body inclusion selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import body_count_validation_product_selector
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


def _alg0030_baseline(case: Dict[str, Any]) -> Dict[str, Any]:
    guard_policy = {
        "min_dominant_count": case.get("min_dominant_count", 5),
        "min_dominant_share_numerator": case.get("min_dominant_share_numerator", 5),
        "min_dominant_share_denominator": case.get("min_dominant_share_denominator", 7),
        "rare_body_count": case.get("rare_body_count", 1),
    }
    result = body_count_validation_product_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        [],
        [],
        guard_policy=guard_policy,
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "body_count_validation_product_selector", {}
    )
    return {
        "selected_body": selector.get("selected_body_alternative"),
        "selected_policy": selector.get("selected_count_policy"),
        "selection_status": selector.get("selection_status"),
        "body_selector_status": selector.get("body_selector_status"),
        "reason": selector.get("reason"),
    }


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def protocol_cases() -> List[Dict[str, Any]]:
    singleton_two_rare = _loop_log(("B",), 5, {("C",): 1, ("E",): 1})
    length2_two_rare = _loop_log(("B", "C"), 5, {("E", "G"): 1, ("H", "J"): 1}, suffix="F")
    mixed_width_two_rare = _loop_log(("B",), 5, {("C", "E"): 1, ("G",): 1}, suffix="F")
    count_two_length2 = _loop_log(("B",), 5, {("C", "E"): 2, ("G", "H"): 2}, suffix="F")
    return [
        {
            "name": "split_singleton_mixed_final_generalization",
            "description": "Validation keeps C and drops E; final probes check unseen C-only repeats and E-containing negatives.",
            "train": singleton_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)]), _repeat_sequence([("C",), ("E",)])],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("E",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": False,
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
            "compare_alg0030": True,
            "expected_alg0030_status": "body_unresolved",
        },
        {
            "name": "split_singleton_drop_both_final_precision",
            "description": "Validation rejects both rare bodies; final probes test unseen rare-only and mixed rare negatives.",
            "train": singleton_two_rare,
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
            "expected_leakage": False,
        },
        {
            "name": "split_length2_mixed_final_generalization",
            "description": "Length-2 rare body EG is valid while HJ is noise.",
            "train": length2_two_rare,
            "validation_positive": [_repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            "validation_negative": [_repeat_sequence([("H", "J"), ("B", "C")], suffix="F")],
            "final_positive": [_repeat_sequence([("E", "G"), ("E", "G")], suffix="F")],
            "final_negative": [
                _repeat_sequence([("H", "J"), ("H", "J")], suffix="F"),
                _repeat_sequence([("E", "G"), ("H", "J")], suffix="F"),
            ],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("H", "J")]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": False,
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
            "compare_alg0030": True,
            "expected_alg0030_status": "body_unresolved",
        },
        {
            "name": "split_mixed_width_final_generalization",
            "description": "A length-2 rare body is valid while a singleton rare body is noise.",
            "train": mixed_width_two_rare,
            "validation_positive": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "validation_negative": [_repeat_sequence([("G",), ("B",)], suffix="F")],
            "final_positive": [_repeat_sequence([("C", "E"), ("C", "E")], suffix="F")],
            "final_negative": [
                _repeat_sequence([("G",), ("G",)], suffix="F"),
                _repeat_sequence([("C", "E"), ("G",)], suffix="F"),
            ],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("G",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": False,
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
            "compare_alg0030": True,
            "expected_alg0030_status": "body_unresolved",
        },
        {
            "name": "split_count_two_length2_mixed_final_generalization",
            "description": "Configured count-two rare bodies can be split even when rare bodies have length two.",
            "train": count_two_length2,
            "validation_positive": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
            "validation_negative": [_repeat_sequence([("G", "H"), ("B",)], suffix="F")],
            "final_positive": [_repeat_sequence([("C", "E"), ("C", "E")], suffix="F")],
            "final_negative": [
                _repeat_sequence([("G", "H"), ("G", "H")], suffix="F"),
                _repeat_sequence([("C", "E"), ("G", "H")], suffix="F"),
            ],
            "min_dominant_share_numerator": 5,
            "min_dominant_share_denominator": 9,
            "rare_body_count": 2,
            "expected_status": "selected",
            "expected_dropped": _body_rows([("G", "H")]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": False,
            "compare_alg0029": True,
            "expected_alg0029_status": "unresolved",
            "compare_alg0030": True,
            "expected_alg0030_status": "body_unresolved",
        },
        {
            "name": "partial_signal_final_not_used",
            "description": "Final probes would identify E as noise, but validation does not, so the selector must stay unresolved.",
            "train": singleton_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "unresolved",
            "expected_dropped": [],
            "expected_reason": "tie_or_conflicting_per_body_validation_evidence",
            "expected_leakage": False,
        },
        {
            "name": "validation_final_overlap_flagged",
            "description": "The harness must flag validation/final reuse even when selection succeeds.",
            "train": singleton_two_rare,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("E",), ("B",)])],
            "final_positive": [_repeat_sequence([("C",), ("B",)])],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "selected",
            "expected_dropped": _body_rows([("E",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": True,
        },
        {
            "name": "training_negative_conflict_protocol",
            "description": "A validation negative that appears in training must block selection.",
            "train": singleton_two_rare,
            "validation_positive": [],
            "validation_negative": [_one_iteration(("E",))],
            "final_positive": [],
            "final_negative": [_repeat_sequence([("E",), ("E",)])],
            "expected_status": "validation_training_conflict",
            "expected_dropped": [],
            "expected_reason": "validation_negative_contains_training_trace",
            "expected_leakage": True,
        },
        {
            "name": "cap_three_allows_three_rare_split",
            "description": "Raising the cap to three allows an eight-alternative split of C-valid, E/F-noisy bodies.",
            "train": _loop_log(("B",), 5, {("C",): 1, ("E",): 1, ("F",): 1}),
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
                _repeat_sequence([("C",), ("F",)]),
            ],
            "min_dominant_share_denominator": 8,
            "max_rare_bodies": 3,
            "expected_status": "selected",
            "expected_dropped": _body_rows([("E",), ("F",)]),
            "expected_reason": "unique_per_body_assignment_satisfies_validation_probes",
            "expected_leakage": False,
            "expected_alternative_count": 8,
        },
        {
            "name": "cap_two_refuses_three_rare_split",
            "description": "The same three-rare-body evidence must refuse selection under the default cap.",
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
            "expected_leakage": False,
            "expected_alternative_count": 0,
        },
        {
            "name": "duplicate_suffix_label_no_source_cut",
            "description": "Rare body shares the suffix label, so the upstream duplicate-label guard should block per-body alternatives.",
            "train": _loop_log(("B",), 5, {("F",): 1}, suffix="F"),
            "validation_positive": [_repeat_sequence([("B",), ("B",)], suffix="F")],
            "validation_negative": [_repeat_sequence([("F",), ("B",)], suffix="F")],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "no_per_body_alternatives",
            "expected_dropped": [],
            "expected_reason": "source_not_multi_body_rework_loop",
            "expected_leakage": False,
            "expected_alternative_count": 0,
        },
        {
            "name": "overlapping_body_labels_no_source_cut",
            "description": "Dominant and rare length-2 bodies overlap labels, so upstream duplicate-label checks block the cut.",
            "train": _loop_log(("B", "C"), 5, {("C", "E"): 1}, suffix="F"),
            "validation_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
            "validation_negative": [_repeat_sequence([("C", "E"), ("B", "C")], suffix="F")],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "no_per_body_alternatives",
            "expected_dropped": [],
            "expected_reason": "source_not_multi_body_rework_loop",
            "expected_leakage": False,
            "expected_alternative_count": 0,
        },
        {
            "name": "wrong_rare_count_no_candidates",
            "description": "With rare_body_count=1, a count-two rare body should not generate per-body alternatives.",
            "train": _loop_log(("B",), 5, {("C",): 2}),
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_status": "no_per_body_alternatives",
            "expected_dropped": [],
            "expected_reason": "no_rare_candidate_bodies",
            "expected_leakage": False,
            "expected_alternative_count": 0,
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
    leakage = _leakage(case)
    has_leakage = _has_leakage(leakage)
    baseline = _alg0029_baseline(case) if case.get("compare_alg0029") else None
    product_baseline = _alg0030_baseline(case) if case.get("compare_alg0030") else None
    selection_ok = (
        selector.get("selection_status") == case["expected_status"]
        and selector.get("selected_dropped_bodies", []) == case["expected_dropped"]
        and selector.get("reason") == case["expected_reason"]
    )
    if "expected_alternative_count" in case:
        selection_ok = selection_ok and selector.get("alternative_count") == case["expected_alternative_count"]
    leakage_ok = has_leakage == case["expected_leakage"]
    baseline_ok = True
    if baseline is not None:
        baseline_ok = baseline.get("selection_status") == case["expected_alg0029_status"]
    product_baseline_ok = True
    if product_baseline is not None:
        product_baseline_ok = (
            product_baseline.get("selection_status") == case["expected_alg0030_status"]
        )
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    final_required = case["expected_status"] == "selected" and not case["expected_leakage"]
    protocol_pass = (
        selection_ok
        and leakage_ok
        and baseline_ok
        and product_baseline_ok
        and (not final_required or final_ok)
    )
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_status": case["expected_status"],
        "expected_reason": case["expected_reason"],
        "expected_dropped": case["expected_dropped"],
        "expected_leakage": case["expected_leakage"],
        "selection_status": selector.get("selection_status"),
        "selected_alternative": selector.get("selected_alternative"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "reason": selector.get("reason"),
        "alternative_count": selector.get("alternative_count"),
        "selection_ok": selection_ok,
        "leakage": leakage,
        "has_leakage": has_leakage,
        "leakage_ok": leakage_ok,
        "baseline_ok": baseline_ok,
        "product_baseline_ok": product_baseline_ok,
        "final_ok": final_ok,
        "protocol_pass": protocol_pass,
        "alg0029_baseline": baseline,
        "alg0030_baseline": product_baseline,
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "operation_counts": result.get("operation_counts"),
        "scores": selector.get("scores", []),
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in protocol_cases()}
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0032-validation-protocol-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        baseline = case["alg0029_baseline"]
        product_baseline = case["alg0030_baseline"]
        baseline_text = ""
        if baseline is not None:
            baseline_text = f" alg0029={baseline['selection_status']}"
        if product_baseline is not None:
            baseline_text += f" alg0030={product_baseline['selection_status']}"
        print(
            f"{case_name}: status={case['selection_status']} reason={case['reason']} "
            f"dropped={case['selected_dropped_bodies']} alternatives={case['alternative_count']} "
            f"leakage={case['has_leakage']} final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']}"
            f"{baseline_text} pass={case['protocol_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
