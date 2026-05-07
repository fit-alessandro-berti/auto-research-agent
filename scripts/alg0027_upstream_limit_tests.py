"""Stress ALG-0027 against upstream loop-evidence limits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from alg0023_loop_tests import _input_stats
import loop_count_validation_selector
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]


def limit_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "one_iteration_only_no_policy_set",
            "description": "Only one-iteration loop evidence is present; upstream has no zero/one ambiguity to expose.",
            "train": [["A", "B", "A", "C"]],
            "validation_positive": [["A", "B", "A", "B", "A", "C"]],
            "validation_negative": [["A", "B", "C"], ["A", "A", "C"]],
            "final_positive": [["A", "B", "A", "B", "A", "C"]],
            "final_negative": [["A", "B", "C"]],
            "expected_policy": None,
            "expected_status": "no_policy_set",
            "expected_final_ok": None,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "duplicate_suffix_label_no_policy_set",
            "description": "A body label also occurs in the suffix; upstream duplicate-label guard rejects loop evidence.",
            "train": [["S", "A", "B"], ["S", "A", "B", "A", "B"], ["S", "A", "C", "A", "B"]],
            "validation_positive": [["S", "A", "B", "A", "C", "A", "B"]],
            "validation_negative": [["S", "A", "B", "B"], ["S", "A", "A", "B"]],
            "final_positive": [["S", "A", "C", "A", "B", "A", "B"]],
            "final_negative": [["S", "A", "C", "B"]],
            "expected_policy": None,
            "expected_status": "no_policy_set",
            "expected_final_ok": None,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "length3_body_no_policy_set",
            "description": "Body alternatives of length three exceed the current ALG-0025 max-body-length bound.",
            "train": [["A", "Z"], ["A", "B", "C", "D", "A", "Z"], ["A", "E", "F", "G", "A", "Z"]],
            "validation_positive": [["A", "B", "C", "D", "A", "E", "F", "G", "A", "Z"]],
            "validation_negative": [["A", "B", "C", "D", "Z"], ["A", "A", "Z"]],
            "final_positive": [["A", "E", "F", "G", "A", "B", "C", "D", "A", "Z"]],
            "final_negative": [["A", "E", "F", "G", "Z"]],
            "expected_policy": None,
            "expected_status": "no_policy_set",
            "expected_final_ok": None,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "overlapping_body_labels_no_policy_set",
            "description": "Different body alternatives share visible labels; upstream rejects this duplicate-label body context.",
            "train": [["A", "Z"], ["A", "B", "C", "A", "Z"], ["A", "C", "D", "A", "Z"]],
            "validation_positive": [["A", "B", "C", "A", "C", "D", "A", "Z"]],
            "validation_negative": [["A", "B", "C", "Z"], ["A", "A", "Z"]],
            "final_positive": [["A", "C", "D", "A", "B", "C", "A", "Z"]],
            "final_negative": [["A", "C", "D", "Z"]],
            "expected_policy": None,
            "expected_status": "no_policy_set",
            "expected_final_ok": None,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "rare_body_valid_unbounded_control",
            "description": "A rare observed body is treated as valid when validation positives require repeated rare-body behavior.",
            "train": [
                ["A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "C", "A", "D"],
            ],
            "validation_positive": [["A", "C", "A", "B", "A", "D"]],
            "validation_negative": [["A", "B", "D"], ["A", "A", "D"]],
            "final_positive": [["A", "C", "A", "C", "A", "D"]],
            "final_negative": [["A", "C", "D"], ["A", "D", "C"]],
            "expected_policy": "unbounded_repeat",
            "expected_status": "selected",
            "expected_final_ok": True,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "rare_body_noise_gap",
            "description": "If the rare observed body should be treated as noise, loop-count validation cannot remove it.",
            "train": [
                ["A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "C", "A", "D"],
            ],
            "validation_positive": [],
            "validation_negative": [["A", "B", "A", "B", "A", "D"], ["A", "B", "D"]],
            "final_positive": [],
            "final_negative": [["A", "C", "A", "D"]],
            "expected_policy": "at_most_once",
            "expected_status": "selected",
            "expected_final_ok": False,
            "expected_train_validation_overlap": False,
        },
        {
            "name": "rare_body_noise_training_conflict",
            "description": "Marking an observed rare body invalid in validation conflicts with the training log and leaves selection unresolved.",
            "train": [
                ["A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "C", "A", "D"],
            ],
            "validation_positive": [],
            "validation_negative": [["A", "C", "A", "D"]],
            "final_positive": [],
            "final_negative": [["A", "C", "A", "D"]],
            "expected_policy": None,
            "expected_status": "unresolved",
            "expected_final_ok": None,
            "expected_train_validation_overlap": True,
        },
    ]


def _trace_set(log: TraceLog) -> set[tuple[str, ...]]:
    return {tuple(trace) for trace in log}


def _sorted_traces(traces: set[tuple[str, ...]]) -> TraceLog:
    return [list(trace) for trace in sorted(traces)]


def _overlap(left: TraceLog, right: TraceLog) -> TraceLog:
    return _sorted_traces(_trace_set(left) & _trace_set(right))


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def _selected_cut(result: Dict[str, Any]) -> Optional[str]:
    return result.get("pmir", {}).get("evidence", {}).get("selected_cut")


def _policy_set_detected(result: Dict[str, Any]) -> bool:
    policy_set = result.get("pmir", {}).get("evidence", {}).get("loop_count_policy_set", {})
    return bool(policy_set.get("detected"))


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
    final_ok = (
        final_positive["replayed_traces"] == final_positive["trace_count"]
        and final_negative["accepted_negative_traces"] == 0
    )
    validation_log = case["validation_positive"] + case["validation_negative"]
    train_validation_overlap = _overlap(case["train"], validation_log)
    selection_ok = (
        selector.get("selected_policy") == case["expected_policy"]
        and selector.get("selection_status") == case["expected_status"]
    )
    expected_final_ok = case["expected_final_ok"]
    final_ok_matches = expected_final_ok is None or final_ok == expected_final_ok
    overlap_ok = bool(train_validation_overlap) == case["expected_train_validation_overlap"]
    stress_pass = selection_ok and final_ok_matches and overlap_ok
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_policy": case["expected_policy"],
        "expected_status": case["expected_status"],
        "expected_final_ok": expected_final_ok,
        "expected_train_validation_overlap": case["expected_train_validation_overlap"],
        "selected_policy": selector.get("selected_policy"),
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "selected_cut": _selected_cut(result),
        "policy_set_detected": _policy_set_detected(result),
        "selector_operation_counts": selector.get("selector_operation_counts"),
        "validation_replay_proxy_counts": selector.get("validation_replay_proxy_counts"),
        "operation_counts": result.get("operation_counts"),
        "scores": selector.get("scores", []),
        "train_validation_overlap": train_validation_overlap,
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
        "final_ok": final_ok,
        "selection_ok": selection_ok,
        "final_ok_matches": final_ok_matches,
        "overlap_ok": overlap_ok,
        "stress_pass": stress_pass,
    }


def run_tests() -> Dict[str, Any]:
    cases = {case["name"]: evaluate_case(case) for case in limit_cases()}
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0027-upstream-limit-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        positive = case["final_positive_replay"]
        negative = case["final_negative_probe"]
        print(
            f"{case_name}: expected={case['expected_policy']} selected={case['selected_policy']} "
            f"status={case['selection_status']} cut={case['selected_cut']} policy_set={case['policy_set_detected']} "
            f"train_val_overlap={bool(case['train_validation_overlap'])} "
            f"final_pos={positive['replayed_traces']}/{positive['trace_count']} "
            f"final_neg={negative['rejected_negative_traces']}/{negative['negative_trace_count']} "
            f"final_ok={case['final_ok']} pass={case['stress_pass']}"
        )
    if results["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
