"""Stress tests for ALG-0024 multi-body loop boundaries."""

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
            "name": "longer_body_choice_rejected",
            "description": "Two length-2 rework bodies around the same anchor; current ALG-0024 supports singleton bodies only.",
            "train": [["A", "F"], ["A", "B", "C", "A", "F"], ["A", "D", "E", "A", "F"]],
            "heldout": [["A", "B", "C", "A", "D", "E", "A", "F"]],
            "negative": [["A", "B", "C", "F"], ["A", "D", "E", "F"], ["A", "A", "F"]],
            "interpretation": "longer body sequences need a separate candidate or detector extension",
        },
        {
            "name": "mixed_singleton_and_sequence_body_rejected",
            "description": "One singleton body and one length-2 body share an anchor; this should remain outside the current singleton-body scope.",
            "train": [["A", "F"], ["A", "B", "A", "F"], ["A", "C", "D", "A", "F"]],
            "heldout": [["A", "B", "A", "C", "D", "A", "F"]],
            "negative": [["A", "B", "F"], ["A", "C", "D", "F"], ["A", "A", "F"]],
            "interpretation": "mixed body widths should not be silently coerced into a singleton choice",
        },
        {
            "name": "duplicate_label_in_suffix_rejected",
            "description": "A body alternative also appears in the suffix, creating duplicate-label ambiguity outside the current compiler scope.",
            "train": [["S", "A", "B"], ["S", "A", "B", "A", "B"], ["S", "A", "C", "A", "B"]],
            "heldout": [["S", "A", "B", "A", "C", "A", "B"]],
            "negative": [["S", "A", "B", "B"], ["S", "A", "C", "B"], ["S", "A", "A", "B"]],
            "interpretation": "duplicate body/suffix labels should remain rejected until duplicate-label loop compilation is studied",
        },
        {
            "name": "bounded_count_multi_body_prior",
            "description": "The same multi-body evidence interpreted as at-most-one rework; repeated body combinations are invalid under this prior.",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
            "heldout": [],
            "negative": [["A", "B", "A", "C", "A", "D"], ["A", "C", "A", "B", "A", "D"], ["A", "B", "D"], ["A", "A", "D"]],
            "interpretation": "unbounded-repeat candidates should fail bounded-count precision by accepting repeated body combinations",
        },
        {
            "name": "support_imbalance_body_choice",
            "description": "One body alternative has much stronger support; ALG-0024 currently treats observed alternatives as choices, not noise.",
            "train": [
                ["A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "C", "A", "D"],
            ],
            "heldout": [["A", "C", "A", "B", "A", "D"]],
            "negative": [["A", "C", "D"], ["A", "B", "D"], ["A", "A", "D"]],
            "interpretation": "support imbalance is not yet used as a noise guard for loop bodies",
        },
    ]


def stability_cases() -> List[Dict[str, Any]]:
    return [
        {
            "name": "multi_body_loop_choice_order_stability",
            "train": [["A", "D"], ["A", "B", "A", "D"], ["A", "C", "A", "D"]],
        },
        {
            "name": "nested_choice_loop_context_order_stability",
            "train": [["S", "A", "E"], ["S", "A", "B", "A", "E"], ["S", "A", "C", "A", "E"]],
        },
        {
            "name": "support_imbalance_body_choice_order_stability",
            "train": [
                ["A", "D"],
                ["A", "B", "A", "D"],
                ["A", "B", "A", "D"],
                ["A", "C", "A", "D"],
            ],
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
            "interpretation": case["interpretation"],
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

    alg0024 = candidates["cut_limited_multi_body_loop"]
    for case in stability_cases():
        signatures: List[Dict[str, Any]] = []
        for permuted_log in _unique_permutations(case["train"]):
            signatures.append(_signature(alg0024(permuted_log)))
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
    parser.add_argument("--out", type=Path, default=Path("experiments/alg0024-stress-tests.json"))
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
