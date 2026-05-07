"""Targeted tests for ALG-0025 length-bounded rework-loop bodies."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any, Dict, List

from alg0023_loop_tests import _input_stats, candidate_functions, evaluate_candidate


TraceLog = List[List[str]]


def test_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "length2_body_choice",
            "description": "Two length-2 rework bodies around the same anchor should compile as a bounded body-choice loop.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"]],
            "negative": [["A", "B", "C", "F"], ["A", "D", "E", "F"], ["A", "A", "F"]],
        },
        {
            "name": "mixed_singleton_and_length2_body",
            "description": "A singleton body and a length-2 body can coexist under the length-bounded loop hypothesis.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "heldout": [["A", "B", "A", "C", "D", "A", "F"]],
            "negative": [["A", "B", "F"], ["A", "C", "D", "F"], ["A", "A", "F"]],
        },
        {
            "name": "singleton_body_regression",
            "description": "The ALG-0024 singleton-body choice case should remain accepted.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [["A", "B", "A", "C", "A", "D"]],
            "negative": [["A", "B", "D"], ["A", "C", "D"], ["A", "A", "D"]],
        },
        {
            "name": "length3_body_rejected",
            "description": "Length-3 bodies should remain outside the ALG-0025 max-body-length-2 scope.",
            "train": [["A", "Z"], ["A", "B", "C", "D", "A", "Z"], ["A", "E", "F", "G", "A", "Z"]],
            "heldout": [["A", "B", "C", "D", "A", "E", "F", "G", "A", "Z"]],
            "negative": [["A", "B", "C", "D", "Z"], ["A", "E", "F", "G", "Z"], ["A", "A", "Z"]],
        },
        {
            "name": "overlapping_body_labels_rejected",
            "description": "Body alternatives sharing visible labels are rejected until duplicate-label body compilation is studied.",
            "train": [["A", "Z"], ["A", "B", "C", "A", "Z"], ["A", "C", "D", "A", "Z"]],
            "heldout": [["A", "B", "C", "A", "C", "D", "A", "Z"]],
            "negative": [["A", "B", "C", "Z"], ["A", "C", "D", "Z"], ["A", "A", "Z"]],
        },
        {
            "name": "bounded_count_length2_prior",
            "description": "Length-2 body evidence interpreted under an at-most-one rework prior.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [],
            "negative": [["A", "B", "C", "A", "D", "E", "A", "F"], ["A", "D", "E", "A", "B", "C", "A", "F"], ["A", "B", "C", "F"], ["A", "A", "F"]],
        },
    ]


def stability_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "length2_body_choice_order_stability",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
        },
        {
            "name": "mixed_singleton_and_length2_body_order_stability",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
        },
    ]


def _signature(result: Dict[str, Any]) -> Dict[str, Any]:
    evidence = result.get("pmir", {}).get("evidence", {})
    process_tree = evidence.get("process_tree", {})
    return {
        "candidate_id": result.get("candidate_id"),
        "selected_cut": evidence.get("selected_cut"),
        "loop_repetition_policy": process_tree.get("loop_repetition_policy"),
        "bounded_count_ambiguous": process_tree.get("bounded_count_ambiguous"),
        "max_body_length": process_tree.get("max_body_length"),
        "anchor": process_tree.get("anchor"),
        "bodies": process_tree.get("bodies"),
        "body_support": process_tree.get("body_support"),
        "prefix": process_tree.get("prefix"),
        "suffix": process_tree.get("suffix"),
    }


def _unique_permutations(log: TraceLog) -> List[TraceLog]:
    unique = []
    seen = set()
    for perm in itertools.permutations(log):
        key = tuple(tuple(trace) for trace in perm)
        if key in seen:
            continue
        seen.add(key)
        unique.append([list(trace) for trace in perm])
    return unique


def run_tests() -> Dict[str, Any]:
    candidates = candidate_functions()
    results: Dict[str, Any] = {"cases": {}, "stability": {}, "candidates": sorted(candidates)}
    for case in test_cases():
        case_result: Dict[str, Any] = {
            "description": case["description"],
            "input_stats": _input_stats(case["train"]),
            "heldout_count": len(case["heldout"]),
            "negative_count": len(case["negative"]),
            "results": {},
        }
        for name, discover in candidates.items():
            try:
                case_result["results"][name] = evaluate_candidate(
                    discover,
                    case["train"],
                    case["heldout"],
                    case["negative"],
                )
            except Exception as exc:
                case_result["results"][name] = {"error": repr(exc)}
        results["cases"][case["name"]] = case_result

    alg0025 = candidates["cut_limited_length_bounded_loop"]
    for case in stability_cases():
        signatures: List[Dict[str, Any]] = []
        for permuted_log in _unique_permutations(case["train"]):
            signatures.append(_signature(alg0025(permuted_log)))
        canonical = signatures[0] if signatures else {}
        results["stability"][case["name"]] = {
            "permutation_count": len(signatures),
            "stable": all(signature == canonical for signature in signatures),
            "canonical_signature": canonical,
            "unique_signatures": [
                json.loads(signature_json)
                for signature_json in sorted({json.dumps(sig, sort_keys=True) for sig in signatures})
            ],
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0025-length-bounded-loop-tests.json"))
    args = parser.parse_args()

    results = run_tests()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for case_name, case in results["cases"].items():
        pieces = []
        for name in results["candidates"]:
            result = case["results"][name]
            if "error" in result:
                pieces.append(f"{name}=ERROR")
                continue
            pieces.append(
                f"{name} cut={result['selected_cut']} grammar={result['selected_grammar']} "
                f"train={result['train_replay']['replayed_traces']}/{result['train_replay']['trace_count']} "
                f"heldout={result['heldout_replay']['replayed_traces']}/{result['heldout_replay']['trace_count']} "
                f"neg={result['negative_probe']['rejected_negative_traces']}/{result['negative_probe']['negative_trace_count']} "
                f"ops={result['operation_counts']['total']}"
            )
        print(f"{case_name}: " + "; ".join(pieces))
    for case_name, case in results["stability"].items():
        print(f"{case_name}: stable={case['stable']} permutations={case['permutation_count']}")


if __name__ == "__main__":
    main()
