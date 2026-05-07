"""Evaluate ALG-0021 ambiguity alternatives as a small multi-net protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from limited_ops import OpCounter
from petri_eval import precision_probe, replay_log
import prefix_block_abstraction
import prefix_block_ambiguity_aware

from alg0015_noise_incomplete_tests import _input_stats, test_cases


TraceLog = List[List[str]]


def _activities(log: TraceLog) -> List[str]:
    return sorted({activity for trace in log for activity in trace})


def _replay_summary(net: Dict[str, Any], log: TraceLog) -> Dict[str, Any]:
    replay = replay_log(net, log)
    return {
        "replayed_traces": replay["replayed_traces"],
        "trace_count": replay["trace_count"],
        "failed_examples": replay["failed_examples"],
    }


def _evaluate_net(net: Dict[str, Any], train: TraceLog, heldout: TraceLog, negative: TraceLog) -> Dict[str, Any]:
    return {
        "train_replay": _replay_summary(net, train),
        "heldout_replay": _replay_summary(net, heldout),
        "negative_probe": precision_probe(net, negative),
    }


def _compile_alternative(
    grammar: Dict[str, Any],
    train: TraceLog,
    discovery_operation_total: int,
) -> Dict[str, Any]:
    counter = OpCounter()
    net = prefix_block_abstraction._compile_block_net(_activities(train), grammar, counter)
    compile_counts = counter.to_dict()
    return {
        "petri_net": net.to_dict(),
        "compile_operation_counts": compile_counts,
        "total_with_discovery_ops": discovery_operation_total + compile_counts["total"],
    }


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    train = case["train"]
    heldout = case["heldout"]
    negative = case["negative"]
    selected = prefix_block_ambiguity_aware.discover(train)
    selected_evidence = selected["pmir"]["evidence"]
    ambiguity = selected_evidence.get("ambiguity", {})
    discovery_operation_total = selected["operation_counts"]["total"]
    result: Dict[str, Any] = {
        "description": case["description"],
        "interpretation": case["interpretation"],
        "input_stats": _input_stats(train),
        "selected": {
            "candidate_id": selected["candidate_id"],
            "selected_grammar": selected_evidence.get("selected_grammar"),
            "grammar_origin": selected_evidence.get("grammar", {}).get("origin"),
            "selected_policy": ambiguity.get("selected_policy"),
            "operation_counts": selected["operation_counts"],
            **_evaluate_net(selected["petri_net"], train, heldout, negative),
        },
        "ambiguity": {
            "detected": ambiguity.get("detected", False),
            "type": ambiguity.get("type"),
            "reason": ambiguity.get("reason"),
        },
        "alternatives": [],
    }

    for alternative in ambiguity.get("alternatives", []):
        grammar = alternative.get("grammar")
        if not isinstance(grammar, dict):
            continue
        compiled = _compile_alternative(grammar, train, discovery_operation_total)
        evaluated = _evaluate_net(compiled["petri_net"], train, heldout, negative)
        result["alternatives"].append(
            {
                "policy": alternative.get("policy"),
                "grammar_type": grammar.get("type"),
                "grammar_origin": grammar.get("origin"),
                "grammar": grammar,
                "compile_operation_counts": compiled["compile_operation_counts"],
                "total_with_discovery_ops": compiled["total_with_discovery_ops"],
                **evaluated,
            }
        )
    return result


def run_tests() -> Dict[str, Any]:
    results: Dict[str, Any] = {"cases": {}}
    for case in test_cases():
        results["cases"][case["name"]] = evaluate_case(case)
    return results


def _format_fraction(summary: Dict[str, Any], total_key: str, hit_key: str) -> str:
    return f"{summary[hit_key]}/{summary[total_key]}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0021-ambiguity-protocol-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        selected = case["selected"]
        pieces = [
            f"selected={selected['selected_policy']}",
            f"ambiguous={case['ambiguity']['detected']}",
            f"selected_heldout={_format_fraction(selected['heldout_replay'], 'trace_count', 'replayed_traces')}",
            (
                "selected_neg="
                f"{selected['negative_probe']['rejected_negative_traces']}/"
                f"{selected['negative_probe']['negative_trace_count']}"
            ),
        ]
        for alternative in case["alternatives"]:
            pieces.append(
                f"{alternative['policy']} heldout="
                f"{_format_fraction(alternative['heldout_replay'], 'trace_count', 'replayed_traces')} "
                f"neg={alternative['negative_probe']['rejected_negative_traces']}/"
                f"{alternative['negative_probe']['negative_trace_count']} "
                f"ops={alternative['total_with_discovery_ops']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))


if __name__ == "__main__":
    main()
