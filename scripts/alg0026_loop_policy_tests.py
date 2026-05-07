"""Evaluate ALG-0026 bounded-count loop policy-set alternatives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from alg0023_loop_tests import _input_stats
from petri_eval import precision_probe, replay_log
import loop_policy_set_protocol


TraceLog = List[List[str]]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "single_rework_unbounded_policy",
            "description": "Singleton rework evidence interpreted as allowing repeated loop iterations.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "heldout": [["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "B", "C"], ["A", "A", "C"], ["B", "A", "C"]],
        },
        {
            "name": "single_rework_bounded_policy",
            "description": "Same singleton rework evidence interpreted as at-most-one rework.",
            "train": [["A", "C"], ["A", "B", "A", "C"]],
            "heldout": [],
            "negative": [["A", "B", "A", "B", "A", "C"], ["A", "B", "C"], ["A", "A", "C"]],
        },
        {
            "name": "multi_body_unbounded_policy",
            "description": "Singleton-body loop choice interpreted as allowing repeated body combinations.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"]],
            "negative": [["A", "B", "D"], ["A", "C", "D"], ["A", "A", "D"]],
        },
        {
            "name": "contexted_multi_body_policy",
            "description": "Prefix/suffix singleton-body loop choice with both loop-count policies preserved.",
            "train": [["S", "A", "E"], ["S", "A", "B", "A", "E"], ["S", "A", "C", "A", "E"]],
            "heldout": [["S", "A", "B", "A", "C", "A", "E"], ["S", "A", "B", "A", "B", "A", "E"]],
            "negative": [["S", "A", "B", "E"], ["S", "A", "C", "E"], ["S", "A", "A", "E"], ["A", "B", "A", "E"]],
        },
        {
            "name": "multi_body_bounded_policy",
            "description": "Same singleton-body loop choice interpreted as at-most-one rework.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [],
            "negative": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"], ["A", "B", "D"], ["A", "A", "D"]],
        },
        {
            "name": "length2_unbounded_policy",
            "description": "Length-2 body loop choice interpreted as allowing repeated body combinations.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"]],
            "negative": [["A", "B", "C", "F"], ["A", "D", "E", "F"], ["A", "A", "F"]],
        },
        {
            "name": "length2_bounded_policy",
            "description": "Same length-2 body loop choice interpreted as at-most-one rework.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [],
            "negative": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"], ["A", "B", "C", "F"], ["A", "A", "F"]],
        },
        {
            "name": "mixed_width_policy",
            "description": "Mixed singleton and length-2 bodies with both loop-count policies preserved.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "heldout": [["A", "B", "A", "C", "D", "A", "F"], ["A", "C", "D", "A", "C", "D", "A", "F"]],
            "negative": [["A", "B", "F"], ["A", "C", "D", "F"], ["A", "A", "F"], ["A", "D", "C", "A", "F"]],
        },
        {
            "name": "one_iteration_only_no_policy_set",
            "description": "No zero-iteration exit means upstream loop detection should not emit bounded-count policy alternatives.",
            "train": [["A", "B", "A", "C"], ["A", "B", "A", "C"]],
            "heldout": [["A", "B", "A", "B", "A", "C"]],
            "negative": [["A", "C"], ["A", "B", "C"], ["A", "A", "C"]],
        },
        {
            "name": "optional_skip_no_policy_set",
            "description": "Optional skip evidence should not emit bounded-loop policy alternatives.",
            "train": [["A", "B", "C"], ["A", "C"], ["A", "B", "C"]],
            "heldout": [["A", "B", "C"]],
            "negative": [["A", "B", "B", "C"], ["A", "C", "B"], ["B", "C"]],
        },
    ]


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def _evaluate_net(net: Dict[str, Any], train: TraceLog, heldout: TraceLog, negative: TraceLog) -> Dict[str, Any]:
    train_replay = replay_log(net, train)
    return {
        "train_replay": {
            "replayed_traces": train_replay["replayed_traces"],
            "trace_count": train_replay["trace_count"],
            "failed_examples": train_replay["failed_examples"],
        },
        "heldout_replay": _replay_summary(net, heldout),
        "negative_probe": precision_probe(net, negative),
        "structural_diagnostics": train_replay["structural_diagnostics"],
    }


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    train = case["train"]
    heldout = case["heldout"]
    negative = case["negative"]
    result = loop_policy_set_protocol.discover(train)
    evidence = result.get("pmir", {}).get("evidence", {})
    policy_set = evidence.get("loop_count_policy_set", {})
    alternatives = []
    for alternative in policy_set.get("alternatives", []):
        net = alternative.get("petri_net")
        if not isinstance(net, dict):
            continue
        alternatives.append(
            {
                "policy": alternative.get("policy"),
                "candidate_source": alternative.get("candidate_source"),
                "compile_operation_counts": alternative.get("compile_operation_counts"),
                "total_with_discovery_ops": alternative.get("total_with_discovery_ops"),
                **_evaluate_net(net, train, heldout, negative),
            }
        )
    return {
        "description": case["description"],
        "input_stats": _input_stats(train),
        "selected": {
            "candidate_id": result.get("candidate_id"),
            "selected_cut": evidence.get("selected_cut"),
            "selected_policy": evidence.get("selected_policy"),
            "operation_counts": result.get("operation_counts"),
            **_evaluate_net(result["petri_net"], train, heldout, negative),
        },
        "policy_set": {
            "detected": policy_set.get("detected", False),
            "type": policy_set.get("type"),
            "reason": policy_set.get("reason"),
            "selected_policy": policy_set.get("selected_policy"),
        },
        "alternatives": alternatives,
    }


def run_tests() -> Dict[str, Any]:
    results: Dict[str, Any] = {"cases": {}}
    for case in test_cases():
        results["cases"][case["name"]] = evaluate_case(case)
    return results


def _format_fraction(summary: Dict[str, Any], total_key: str, hit_key: str) -> str:
    return f"{summary[hit_key]}/{summary[total_key]}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0026-loop-policy-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        selected = case["selected"]
        pieces = [
            f"detected={case['policy_set']['detected']}",
            f"selected={selected['selected_policy']}",
            f"selected_heldout={_format_fraction(selected['heldout_replay'], 'trace_count', 'replayed_traces')}",
            (
                "selected_neg="
                f"{selected['negative_probe']['rejected_negative_traces']}/"
                f"{selected['negative_probe']['negative_trace_count']}"
            ),
        ]
        for alternative in case["alternatives"]:
            pieces.append(
                f"{alternative['policy']} train="
                f"{_format_fraction(alternative['train_replay'], 'trace_count', 'replayed_traces')} "
                f"heldout={_format_fraction(alternative['heldout_replay'], 'trace_count', 'replayed_traces')} "
                f"neg={alternative['negative_probe']['rejected_negative_traces']}/"
                f"{alternative['negative_probe']['negative_trace_count']} "
                f"ops={alternative['total_with_discovery_ops']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
