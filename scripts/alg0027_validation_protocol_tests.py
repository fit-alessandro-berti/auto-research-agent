"""Split validation/final-test protocol checks for ALG-0027."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from alg0023_loop_tests import _input_stats
import loop_count_validation_selector
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]


def protocol_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "single_unbounded_final_generalization",
            "description": "Validation selects unbounded repeat; final probes require a third singleton-loop iteration.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [["A", "B", "A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "C"], ["B", "A", "C"]],
            "final_positive": [["A", "B", "A", "B", "A", "B", "A", "C"]],
            "final_negative": [["A", "A", "C"], ["A", "C", "B"]],
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "single_bounded_final_precision",
            "description": "Validation selects at-most-once; final probes check different repeated singleton-loop negatives.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "B", "A", "C"], ["A", "B", "C"]],
            "final_positive": [],
            "final_negative": [["A", "B", "A", "B", "A", "B", "A", "C"], ["A", "A", "C"]],
            "expected_policy": "at_most_once",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "multi_body_unbounded_final_generalization",
            "description": "Validation selects unbounded repeat; final probes require unseen repeated body combinations.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "validation_positive": [["A", "B", "A", "C", "A", "D"]],
            "validation_negative": [["A", "B", "D"], ["A", "A", "D"]],
            "final_positive": [["A", "C", "A", "B", "A", "D"], ["A", "B", "A", "B", "A", "D"]],
            "final_negative": [["A", "C", "D"], ["A", "D", "B"]],
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "multi_body_bounded_final_precision",
            "description": "Validation selects at-most-once; final probes check different repeated body combinations.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "C", "A", "D"], ["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [["A", "C", "A", "B", "A", "D"], ["A", "B", "A", "B", "A", "D"]],
            "expected_policy": "at_most_once",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "length2_unbounded_final_generalization",
            "description": "Validation selects unbounded repeat for length-2 bodies; final probes reverse the repeated body order.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "validation_positive": [["A", "B", "C", "A", "D", "E", "A", "F"]],
            "validation_negative": [["A", "B", "C", "F"], ["A", "A", "F"]],
            "final_positive": [["A", "D", "E", "A", "B", "C", "A", "F"]],
            "final_negative": [["A", "D", "E", "F"], ["A", "C", "B", "A", "F"]],
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "mixed_width_bounded_final_precision",
            "description": "Validation selects at-most-once for mixed singleton/length-2 bodies.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "C", "D", "A", "F"], ["A", "B", "F"]],
            "final_positive": [],
            "final_negative": [["A", "C", "D", "A", "B", "A", "F"], ["A", "B", "A", "B", "A", "F"]],
            "expected_policy": "at_most_once",
            "expected_status": "selected",
            "expected_leakage": False,
        },
        {
            "name": "no_discriminator_remains_unresolved",
            "description": "Validation negatives are structural invalid traces both policies reject, so final probes must not be used to select.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "C"], ["B", "A", "C"]],
            "final_positive": [["A", "B", "A", "B", "A", "C"]],
            "final_negative": [["A", "A", "C"]],
            "expected_policy": None,
            "expected_status": "unresolved",
            "expected_leakage": False,
        },
        {
            "name": "optional_skip_no_policy_set_final_control",
            "description": "Optional-skip evidence should not become a loop-count decision under validation/final probes.",
            "train": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"]],
            "validation_positive": [],
            "validation_negative": [["A", "B", "B", "C"], ["B", "C"]],
            "final_positive": [],
            "final_negative": [["A", "C", "B"]],
            "expected_policy": None,
            "expected_status": "no_policy_set",
            "expected_leakage": False,
        },
        {
            "name": "leakage_guard_reports_validation_final_overlap",
            "description": "Protocol guard must flag reused validation positives in the final-test split.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "validation_positive": [["A", "B", "A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "C"]],
            "final_positive": [["A", "B", "A", "B", "A", "C"]],
            "final_negative": [["A", "A", "C"]],
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
            "expected_leakage": True,
        },
    ]


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


def _policy_final_evaluations(
    result: Dict[str, Any],
    final_positive: TraceLog,
    final_negative: TraceLog,
) -> List[Dict[str, Any]]:
    policy_set = result.get("pmir", {}).get("evidence", {}).get("loop_count_policy_set", {})
    evaluations = []
    for alternative in policy_set.get("alternatives", []):
        net = alternative.get("petri_net")
        if not isinstance(net, dict):
            continue
        evaluations.append(
            {
                "policy": alternative.get("policy"),
                "final_positive_replay": _replay_summary(net, final_positive),
                "final_negative_probe": precision_probe(net, final_negative),
                "total_with_discovery_ops": alternative.get("total_with_discovery_ops"),
            }
        )
    return evaluations


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = loop_count_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
    )
    evidence = result.get("pmir", {}).get("evidence", {})
    selector = evidence.get("loop_count_validation_selector", {})
    selected_net = result["petri_net"]
    final_positive = _replay_summary(selected_net, case["final_positive"])
    final_negative = precision_probe(selected_net, case["final_negative"])
    leakage = _leakage(case)
    has_leakage = _has_leakage(leakage)
    selection_ok = (
        selector.get("selected_policy") == case["expected_policy"]
        and selector.get("selection_status") == case["expected_status"]
    )
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    leakage_ok = has_leakage == case["expected_leakage"]
    final_required = case["expected_policy"] is not None and not case["expected_leakage"]
    protocol_pass = selection_ok and leakage_ok and (not final_required or final_ok)
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_policy": case["expected_policy"],
        "expected_status": case["expected_status"],
        "expected_leakage": case["expected_leakage"],
        "selected_policy": selector.get("selected_policy"),
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
        "policy_final_evaluations": _policy_final_evaluations(
            result,
            case["final_positive"],
            case["final_negative"],
        ),
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0027-validation-protocol-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        replay_proxy = case["validation_replay_proxy_counts"]["total"]
        print(
            f"{case_name}: expected={case['expected_policy']} selected={case['selected_policy']} "
            f"status={case['selection_status']} leakage={case['has_leakage']} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"selector_ops={case['selector_operation_counts']['total']} "
            f"validation_replay_proxy_ops={replay_proxy} pass={case['protocol_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
