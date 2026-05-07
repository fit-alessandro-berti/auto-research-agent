"""Threshold ablations for ALG-0028 and validation probes for ALG-0029."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

from alg0023_loop_tests import _input_stats
import body_inclusion_validation_selector
import cut_limited_body_support_guard
import cut_limited_length_bounded_loop
from petri_eval import precision_probe, replay_log


TraceLog = List[List[str]]
Body = Tuple[str, ...]
DiscoverFn = Callable[[TraceLog], Dict[str, Any]]


POLICIES: List[Dict[str, Any]] = [
    {
        "name": "support_2_to_1",
        "kwargs": {
            "min_dominant_count": 2,
            "min_dominant_share_numerator": 2,
            "min_dominant_share_denominator": 3,
            "rare_body_count": 1,
        },
    },
    {
        "name": "support_3_to_1_default",
        "kwargs": {
            "min_dominant_count": 3,
            "min_dominant_share_numerator": 3,
            "min_dominant_share_denominator": 4,
            "rare_body_count": 1,
        },
    },
    {
        "name": "support_4_to_1",
        "kwargs": {
            "min_dominant_count": 4,
            "min_dominant_share_numerator": 4,
            "min_dominant_share_denominator": 5,
            "rare_body_count": 1,
        },
    },
    {
        "name": "support_5_to_1",
        "kwargs": {
            "min_dominant_count": 5,
            "min_dominant_share_numerator": 5,
            "min_dominant_share_denominator": 6,
            "rare_body_count": 1,
        },
    },
]


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


def ablation_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for count in [2, 3, 4, 5]:
        cases.append(
            {
                "name": f"singleton_noise_{count}_to_1",
                "family": "singleton_rare_noise",
                "description": f"Dominant singleton body support {count}; singleton rare body is treated as noise.",
                "train": _loop_log(("B",), count, {("C",): 1}),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)])],
                "valid_rare_positive": [],
                "rare_noise_negative": [_one_iteration(("C",)), _repeat_sequence([("C",), ("B",)])],
            }
        )
        cases.append(
            {
                "name": f"singleton_valid_rare_{count}_to_1",
                "family": "singleton_valid_rare",
                "description": f"Dominant singleton body support {count}; singleton rare body is valid held-out behavior.",
                "train": _loop_log(("B",), count, {("C",): 1}),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)])],
                "valid_rare_positive": [_repeat_sequence([("C",), ("B",)]), _repeat_sequence([("C",), ("C",)])],
                "rare_noise_negative": [],
            }
        )
    cases.extend(
        [
            {
                "name": "rare_count_two_noise_5_to_2",
                "family": "rare_count_two_noise",
                "description": "Rare body count two remains outside the singleton-rare filter.",
                "train": _loop_log(("B",), 5, {("C",): 2}),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)])],
                "valid_rare_positive": [],
                "rare_noise_negative": [_repeat_sequence([("C",), ("B",)]), _repeat_sequence([("C",), ("C",)])],
            },
            {
                "name": "two_rare_bodies_noise_4_1_1",
                "family": "two_rare_bodies_noise",
                "description": "Two singleton rare bodies are noise; weaker dominant share may keep them.",
                "train": _loop_log(("B",), 4, {("C",): 1, ("E",): 1}),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)])],
                "valid_rare_positive": [],
                "rare_noise_negative": [_repeat_sequence([("C",), ("B",)]), _repeat_sequence([("E",), ("B",)])],
            },
            {
                "name": "two_rare_bodies_one_valid_5_1_1",
                "family": "two_rare_bodies_one_valid",
                "description": "One singleton rare body is valid and one is noise; support alone cannot distinguish them.",
                "train": _loop_log(("B",), 5, {("C",): 1, ("E",): 1}),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)])],
                "valid_rare_positive": [_repeat_sequence([("C",), ("B",)])],
                "rare_noise_negative": [_repeat_sequence([("E",), ("B",)])],
            },
            {
                "name": "length2_dominant_singleton_rare_noise_4_to_1",
                "family": "length2_dominant_singleton_rare_noise",
                "description": "Dominant length-2 body with singleton rare body as noise.",
                "train": _loop_log(("B", "C"), 4, {("E",): 1}, suffix="F"),
                "dominant_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
                "valid_rare_positive": [],
                "rare_noise_negative": [_one_iteration(("E",), suffix="F"), _repeat_sequence([("E",), ("B", "C")], suffix="F")],
            },
            {
                "name": "singleton_dominant_length2_rare_valid_4_to_1",
                "family": "singleton_dominant_length2_rare_valid",
                "description": "Dominant singleton body with length-2 rare body as valid behavior.",
                "train": _loop_log(("B",), 4, {("C", "E"): 1}, suffix="F"),
                "dominant_positive": [_repeat_sequence([("B",), ("B",)], suffix="F")],
                "valid_rare_positive": [_repeat_sequence([("C", "E"), ("B",)], suffix="F")],
                "rare_noise_negative": [],
            },
            {
                "name": "length2_dominant_length2_rare_noise_5_to_1",
                "family": "length2_dominant_length2_rare_noise",
                "description": "Both dominant and rare bodies have length two; rare body is noise.",
                "train": _loop_log(("B", "C"), 5, {("E", "G"): 1}, suffix="F"),
                "dominant_positive": [_repeat_sequence([("B", "C"), ("B", "C")], suffix="F")],
                "valid_rare_positive": [],
                "rare_noise_negative": [_one_iteration(("E", "G"), suffix="F"), _repeat_sequence([("E", "G"), ("B", "C")], suffix="F")],
            },
        ]
    )
    return cases


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def _evaluate_result(result: Dict[str, Any], case: Dict[str, Any]) -> Dict[str, Any]:
    net = result["petri_net"]
    guard = result.get("pmir", {}).get("evidence", {}).get("support_guard", {})
    train_replay = _replay_summary(net, case["train"])
    dominant_positive = _replay_summary(net, case["dominant_positive"])
    valid_rare_positive = _replay_summary(net, case["valid_rare_positive"])
    rare_noise_negative = precision_probe(net, case["rare_noise_negative"])
    if guard.get("applied"):
        support_only_decision = "filter"
    elif guard:
        support_only_decision = "keep_or_ambiguous"
    else:
        support_only_decision = "keep_all_baseline"
    return {
        "candidate_id": result["candidate_id"],
        "operation_counts": result["operation_counts"],
        "support_guard": guard,
        "support_only_decision": support_only_decision,
        "selected_cut": result.get("pmir", {}).get("evidence", {}).get("selected_cut"),
        "train_replay": train_replay,
        "dominant_positive_replay": dominant_positive,
        "valid_rare_positive_replay": valid_rare_positive,
        "rare_noise_negative_probe": rare_noise_negative,
    }


def _discover_policy(policy: Dict[str, Any]) -> DiscoverFn:
    kwargs = policy["kwargs"]

    def discover(log: TraceLog) -> Dict[str, Any]:
        return cut_limited_body_support_guard.discover_with_policy(log, **kwargs)

    return discover


def run_ablation_matrix() -> Dict[str, Any]:
    candidates: List[Tuple[str, DiscoverFn]] = [
        ("keep_all_baseline", cut_limited_length_bounded_loop.discover)
    ]
    candidates.extend((policy["name"], _discover_policy(policy)) for policy in POLICIES)
    results: Dict[str, Any] = {
        "policies": ["keep_all_baseline"] + [policy["name"] for policy in POLICIES],
        "cases": {},
        "summary": {},
    }
    summary: Dict[str, Dict[str, int]] = {
        name: {
            "guard_applied_cases": 0,
            "train_replayed": 0,
            "train_total": 0,
            "valid_rare_replayed": 0,
            "valid_rare_total": 0,
            "rare_noise_rejected": 0,
            "rare_noise_total": 0,
        }
        for name, _ in candidates
    }
    for case in ablation_cases():
        case_result: Dict[str, Any] = {
            "family": case["family"],
            "description": case["description"],
            "input_stats": _input_stats(case["train"]),
            "dominant_positive_count": len(case["dominant_positive"]),
            "valid_rare_positive_count": len(case["valid_rare_positive"]),
            "rare_noise_negative_count": len(case["rare_noise_negative"]),
            "results": {},
        }
        for name, discover in candidates:
            evaluated = _evaluate_result(discover(case["train"]), case)
            case_result["results"][name] = evaluated
            if evaluated["support_guard"].get("applied"):
                summary[name]["guard_applied_cases"] += 1
            summary[name]["train_replayed"] += evaluated["train_replay"]["replayed_traces"]
            summary[name]["train_total"] += evaluated["train_replay"]["trace_count"]
            summary[name]["valid_rare_replayed"] += evaluated["valid_rare_positive_replay"]["replayed_traces"]
            summary[name]["valid_rare_total"] += evaluated["valid_rare_positive_replay"]["trace_count"]
            summary[name]["rare_noise_rejected"] += evaluated["rare_noise_negative_probe"]["rejected_negative_traces"]
            summary[name]["rare_noise_total"] += evaluated["rare_noise_negative_probe"]["negative_trace_count"]
        results["cases"][case["name"]] = case_result
    results["summary"] = summary
    return results


def validation_cases() -> List[Dict[str, Any]]:
    train = _loop_log(("B",), 3, {("C",): 1})
    return [
        {
            "name": "validation_selects_keep_rare_3_to_1",
            "description": "Validation positives require the rare body, so the selector should keep all bodies.",
            "train": train,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [["A", "B", "D"]],
            "final_positive": [_repeat_sequence([("C",), ("C",)])],
            "final_negative": [["A", "D", "B"]],
            "expected_alternative": "keep_all_bodies",
            "expected_status": "selected",
        },
        {
            "name": "validation_selects_filter_rare_3_to_1",
            "description": "Validation negatives mark unseen rare-body combinations invalid, so the selector should filter the rare body.",
            "train": train,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [_repeat_sequence([("B",), ("B",), ("B",)])],
            "final_negative": [_repeat_sequence([("C",), ("C",)])],
            "expected_alternative": "support_guard",
            "expected_status": "selected",
        },
        {
            "name": "validation_no_body_signal_unresolved",
            "description": "Validation probes do not distinguish keeping versus filtering the rare body.",
            "train": train,
            "validation_positive": [_repeat_sequence([("B",), ("B",)])],
            "validation_negative": [["A", "B", "D"], ["A", "D", "B"]],
            "final_positive": [],
            "final_negative": [],
            "expected_alternative": None,
            "expected_status": "unresolved",
        },
        {
            "name": "validation_training_conflict",
            "description": "Validation negatives contain an observed rare training trace, so body exclusion conflicts with training replay.",
            "train": train,
            "validation_positive": [],
            "validation_negative": [_one_iteration(("C",))],
            "final_positive": [],
            "final_negative": [],
            "expected_alternative": None,
            "expected_status": "validation_training_conflict",
        },
        {
            "name": "validation_positive_negative_conflict",
            "description": "The same rare-body trace appears as both validation positive and negative.",
            "train": train,
            "validation_positive": [_repeat_sequence([("C",), ("B",)])],
            "validation_negative": [_repeat_sequence([("C",), ("B",)])],
            "final_positive": [],
            "final_negative": [],
            "expected_alternative": None,
            "expected_status": "validation_inconsistent",
        },
    ]


def evaluate_validation_case(case: Dict[str, Any]) -> Dict[str, Any]:
    result = body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
    )
    selector = result.get("pmir", {}).get("evidence", {}).get("body_inclusion_validation_selector", {})
    final_positive = _replay_summary(result["petri_net"], case["final_positive"])
    final_negative = precision_probe(result["petri_net"], case["final_negative"])
    selection_ok = (
        selector.get("selected_alternative") == case["expected_alternative"]
        and selector.get("selection_status") == case["expected_status"]
    )
    return {
        "description": case["description"],
        "input_stats": _input_stats(case["train"]),
        "expected_alternative": case["expected_alternative"],
        "expected_status": case["expected_status"],
        "selected_alternative": selector.get("selected_alternative"),
        "selection_status": selector.get("selection_status"),
        "reason": selector.get("reason"),
        "selection_ok": selection_ok,
        "selector": selector,
        "operation_counts": result["operation_counts"],
        "final_positive_replay": final_positive,
        "final_negative_probe": final_negative,
    }


def run_validation_protocol() -> Dict[str, Any]:
    results: Dict[str, Any] = {"cases": {}}
    for case in validation_cases():
        results["cases"][case["name"]] = evaluate_validation_case(case)
    results["all_expectations_passed"] = all(case["selection_ok"] for case in results["cases"].values())
    return results


def run_tests() -> Dict[str, Any]:
    return {
        "ablation_matrix": run_ablation_matrix(),
        "validation_protocol": run_validation_protocol(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0028-threshold-ablation-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for policy, summary in results["ablation_matrix"]["summary"].items():
        print(
            f"{policy}: guard_cases={summary['guard_applied_cases']} "
            f"train={summary['train_replayed']}/{summary['train_total']} "
            f"valid_rare={summary['valid_rare_replayed']}/{summary['valid_rare_total']} "
            f"rare_noise_reject={summary['rare_noise_rejected']}/{summary['rare_noise_total']}"
        )
    for case_name, case in results["validation_protocol"]["cases"].items():
        print(
            f"{case_name}: selected={case['selected_alternative']} "
            f"status={case['selection_status']} ok={case['selection_ok']}"
        )
    if not results["validation_protocol"]["all_expectations_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
