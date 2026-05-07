"""Shared operation accounting report for validation-scoped loop selectors.

Selectors retain their conservative all-alternative totals for compatibility and
also emit shared-operation totals. This report cross-checks the selector fields
against an independent derivation on the deterministic validation protocols.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from alg0023_loop_tests import _input_stats
import alg0029_validation_protocol_tests as alg0029_protocol
import alg0032_validation_protocol_tests as alg0032_protocol
import body_count_validation_product_selector
import body_inclusion_validation_selector
import per_body_inclusion_validation_selector


def _as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _selector_kwargs(case: Dict[str, Any]) -> Dict[str, int]:
    return {
        "min_dominant_count": _as_int(case.get("min_dominant_count"), 5),
        "min_dominant_share_numerator": _as_int(case.get("min_dominant_share_numerator"), 5),
        "min_dominant_share_denominator": _as_int(case.get("min_dominant_share_denominator"), 7),
        "rare_body_count": _as_int(case.get("rare_body_count"), 1),
        "max_rare_bodies": _as_int(case.get("max_rare_bodies"), 2),
    }


def _shared_axis_totals(
    result: Dict[str, Any],
    evidence_key: str,
    base_alternative: str,
) -> Dict[str, Any]:
    operation_counts = result.get("operation_counts", {})
    evidence = result.get("pmir", {}).get("evidence", {}).get(evidence_key, {})
    scores = evidence.get("scores", [])

    selected_discovery_total = _as_int(operation_counts.get("total"))
    base_total = selected_discovery_total
    for row in scores:
        if row.get("alternative") == base_alternative:
            base_total = _as_int(row.get("operation_total"), selected_discovery_total)
            break

    alternative_details = []
    incremental_extra_total = 0
    naive_from_scores = 0
    for row in scores:
        alternative = row.get("alternative")
        operation_total = _as_int(row.get("operation_total"))
        naive_from_scores += operation_total
        incremental_extra = 0
        if alternative != base_alternative:
            incremental_extra = max(0, operation_total - base_total)
            incremental_extra_total += incremental_extra
        alternative_details.append(
            {
                "alternative": alternative,
                "operation_total": operation_total,
                "incremental_extra_after_shared_base": incremental_extra,
                "validates_all": bool(row.get("validates_all")),
            }
        )

    if not scores:
        naive_from_scores = selected_discovery_total

    naive_discovery_total = _as_int(
        operation_counts.get("all_alternative_discovery_total"),
        naive_from_scores,
    )
    shared_discovery_total = base_total + incremental_extra_total
    selector_total = _as_int(operation_counts.get("selector_total"))
    validation_replay_proxy_total = _as_int(
        operation_counts.get("validation_replay_proxy_total")
    )
    current_all_alternative_total = _as_int(
        operation_counts.get("total_with_all_alternatives_and_validation_proxy"),
        naive_discovery_total + selector_total + validation_replay_proxy_total,
    )
    shared_total = shared_discovery_total + selector_total + validation_replay_proxy_total
    integrated_shared_discovery_total = _as_int(
        operation_counts.get("shared_all_alternative_discovery_total"),
        shared_discovery_total,
    )
    integrated_shared_total = _as_int(
        operation_counts.get("total_with_shared_alternatives_and_validation_proxy"),
        shared_total,
    )
    return {
        "selected_discovery_total": selected_discovery_total,
        "base_alternative": base_alternative,
        "base_discovery_total": base_total,
        "alternative_count": len(scores),
        "naive_all_alternative_discovery_total": naive_discovery_total,
        "incremental_extra_total_after_shared_base": incremental_extra_total,
        "shared_all_alternative_discovery_total": shared_discovery_total,
        "selector_total": selector_total,
        "validation_replay_proxy_total": validation_replay_proxy_total,
        "current_all_alternative_total_with_validation_proxy": current_all_alternative_total,
        "derived_shared_total_with_validation_proxy": shared_total,
        "shared_total_with_validation_proxy": integrated_shared_total,
        "selector_integrated_shared_all_alternative_discovery_total": integrated_shared_discovery_total,
        "selector_integrated_shared_total_matches_derivation": integrated_shared_total == shared_total,
        "shared_savings": current_all_alternative_total - integrated_shared_total,
        "shared_savings_percent": _percent(
            current_all_alternative_total - integrated_shared_total,
            current_all_alternative_total,
        ),
        "alternatives": alternative_details,
    }


def _percent(numerator: int, denominator: int) -> Optional[float]:
    if denominator <= 0:
        return None
    return round((100.0 * numerator) / denominator, 2)


def _body_case_report(case: Dict[str, Any]) -> Dict[str, Any]:
    result = body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        guard_policy=case.get("guard_policy"),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "body_inclusion_validation_selector", {}
    )
    return {
        "candidate_id": "ALG-0029",
        "case": case["name"],
        "input_stats": _input_stats(case["train"]),
        "selection_status": selector.get("selection_status"),
        "selected_alternative": selector.get("selected_alternative"),
        "reason": selector.get("reason"),
        "operation_totals": _shared_axis_totals(
            result,
            "body_inclusion_validation_selector",
            "keep_all_bodies",
        ),
    }


def _product_case_report(case: Dict[str, Any]) -> Dict[str, Any]:
    result = body_count_validation_product_selector.select(
        case["train"],
        case["body_validation_positive"],
        case["body_validation_negative"],
        case["count_validation_positive"],
        case["count_validation_negative"],
        guard_policy=case.get("guard_policy"),
    )
    operation_counts = result.get("operation_counts", {})
    evidence = result.get("pmir", {}).get("evidence", {})
    product_selector = evidence.get("body_count_validation_product_selector", {})
    body_axis = _shared_axis_totals(
        result,
        "body_inclusion_validation_selector",
        "keep_all_bodies",
    )
    selected_body_discovery_total = _as_int(operation_counts.get("total"))
    count_scores = product_selector.get("count_scores", [])
    count_compile_alternatives = []
    derived_all_count_compile_extra_total = 0
    for row in count_scores:
        total_with_discovery = _as_int(row.get("total_with_discovery_ops"))
        compile_extra = max(0, total_with_discovery - selected_body_discovery_total)
        derived_all_count_compile_extra_total += compile_extra
        count_compile_alternatives.append(
            {
                "policy": row.get("policy"),
                "total_with_discovery_ops": total_with_discovery,
                "incremental_compile_extra_after_selected_body": compile_extra,
                "validates_all": bool(row.get("validates_all")),
            }
        )

    count_selector_total = _as_int(operation_counts.get("count_selector_total"))
    count_replay_total = _as_int(operation_counts.get("count_validation_replay_proxy_total"))
    selected_count_compile_extra = _as_int(operation_counts.get("count_compile_extra_total"))
    all_count_compile_extra_total = _as_int(
        operation_counts.get("count_all_compile_extra_total"),
        derived_all_count_compile_extra_total,
    )
    derived_shared_selected_count_total = (
        body_axis["shared_total_with_validation_proxy"]
        + selected_count_compile_extra
        + count_selector_total
        + count_replay_total
    )
    derived_shared_all_count_total = (
        body_axis["shared_total_with_validation_proxy"]
        + all_count_compile_extra_total
        + count_selector_total
        + count_replay_total
    )
    shared_selected_count_total = _as_int(
        operation_counts.get("total_with_shared_product_selected_count_and_validation_proxy"),
        derived_shared_selected_count_total,
    )
    shared_all_count_total = _as_int(
        operation_counts.get("total_with_shared_product_all_count_alternatives_and_validation_proxy"),
        derived_shared_all_count_total,
    )
    current_reported_total = _as_int(
        operation_counts.get("total_with_product_selector_and_validation_proxy")
    )
    return {
        "candidate_id": "ALG-0030",
        "case": case["name"],
        "input_stats": _input_stats(case["train"]),
        "selection_status": product_selector.get("selection_status"),
        "selected_body_alternative": product_selector.get("selected_body_alternative"),
        "selected_count_policy": product_selector.get("selected_count_policy"),
        "reason": product_selector.get("reason"),
        "operation_totals": {
            "current_reported_product_total": current_reported_total,
            "derived_shared_total_with_selected_count_compile_extra": derived_shared_selected_count_total,
            "derived_shared_total_with_all_count_compile_extras": derived_shared_all_count_total,
            "shared_total_with_selected_count_compile_extra": shared_selected_count_total,
            "shared_total_with_all_count_compile_extras": shared_all_count_total,
            "selector_integrated_selected_count_total_matches_derivation": (
                shared_selected_count_total == derived_shared_selected_count_total
            ),
            "selector_integrated_all_count_total_matches_derivation": (
                shared_all_count_total == derived_shared_all_count_total
            ),
            "reported_minus_shared_selected_count": (
                current_reported_total - shared_selected_count_total
            ),
            "reported_minus_shared_all_count": current_reported_total - shared_all_count_total,
            "reported_minus_shared_all_count_percent": _percent(
                current_reported_total - shared_all_count_total,
                current_reported_total,
            ),
            "body_axis": body_axis,
            "count_axis": {
                "selected_body_discovery_total": selected_body_discovery_total,
                "selected_count_compile_extra_total": selected_count_compile_extra,
                "all_count_compile_extra_total": all_count_compile_extra_total,
                "derived_all_count_compile_extra_total": derived_all_count_compile_extra_total,
                "selector_integrated_all_count_compile_matches_derivation": (
                    all_count_compile_extra_total == derived_all_count_compile_extra_total
                ),
                "count_selector_total": count_selector_total,
                "count_validation_replay_proxy_total": count_replay_total,
                "alternatives": count_compile_alternatives,
            },
        },
    }


def _per_body_case_report(case: Dict[str, Any]) -> Dict[str, Any]:
    result = per_body_inclusion_validation_selector.select(
        case["train"],
        case["validation_positive"],
        case["validation_negative"],
        **_selector_kwargs(case),
    )
    selector = result.get("pmir", {}).get("evidence", {}).get(
        "per_body_inclusion_validation_selector", {}
    )
    return {
        "candidate_id": "ALG-0032",
        "case": case["name"],
        "input_stats": _input_stats(case["train"]),
        "selection_status": selector.get("selection_status"),
        "selected_alternative": selector.get("selected_alternative"),
        "selected_dropped_bodies": selector.get("selected_dropped_bodies", []),
        "reason": selector.get("reason"),
        "operation_totals": _shared_axis_totals(
            result,
            "per_body_inclusion_validation_selector",
            "drop_none",
        ),
    }


def _summarize_axis(rows: List[Dict[str, Any]], total_key: str) -> Dict[str, Any]:
    if not rows:
        return {
            "case_count": 0,
            "max_current_total": 0,
            "max_shared_total": 0,
            "max_savings": 0,
            "case_with_max_shared_total": None,
        }
    max_current = 0
    max_shared = 0
    max_savings = None
    max_shared_case = None
    max_savings_case = None
    for row in rows:
        totals = row["operation_totals"]
        if total_key == "axis":
            current = _as_int(totals.get("current_all_alternative_total_with_validation_proxy"))
            shared = _as_int(totals.get("shared_total_with_validation_proxy"))
        else:
            current = _as_int(totals.get("current_reported_product_total"))
            shared = _as_int(totals.get(total_key))
        savings = current - shared
        if current > max_current:
            max_current = current
        if shared > max_shared:
            max_shared = shared
            max_shared_case = row["case"]
        if max_savings is None or savings > max_savings:
            max_savings = savings
            max_savings_case = row["case"]
    return {
        "case_count": len(rows),
        "max_current_total": max_current,
        "max_shared_total": max_shared,
        "case_with_max_shared_total": max_shared_case,
        "max_savings": max_savings,
        "case_with_max_savings": max_savings_case,
    }


def build_report() -> Dict[str, Any]:
    alg0029_rows = [_body_case_report(case) for case in alg0029_protocol.body_protocol_cases()]
    alg0030_rows = [_product_case_report(case) for case in alg0029_protocol.composition_cases()]
    alg0032_rows = [_per_body_case_report(case) for case in alg0032_protocol.protocol_cases()]
    return {
        "assumptions": [
            "One upstream ALG-0025 length-bounded loop discovery is charged once per train log.",
            "Each guarded body alternative pays only its measured incremental partition/recompile extra over that shared base.",
            "Validation replay remains a proxy: one scan_event per validation event and one comparison per validation trace per evaluated alternative.",
            "ALG-0030 reports both selected-count and all-count compile variants; all-count compile is the conservative selector-evaluation estimate.",
            "Selector outputs retain naive totals and now expose shared totals; this report checks those shared totals against an independent derivation.",
            "No selector behavior, replay result, or promotion status is changed by this accounting.",
        ],
        "candidates": {
            "ALG-0029": {
                "summary": _summarize_axis(alg0029_rows, "axis"),
                "cases": alg0029_rows,
            },
            "ALG-0030": {
                "summary": _summarize_axis(
                    alg0030_rows,
                    "shared_total_with_all_count_compile_extras",
                ),
                "cases": alg0030_rows,
            },
            "ALG-0032": {
                "summary": _summarize_axis(alg0032_rows, "axis"),
                "cases": alg0032_rows,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/selector-shared-cost-report.json"),
    )
    args = parser.parse_args()

    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for candidate_id, candidate in report["candidates"].items():
        summary = candidate["summary"]
        print(
            f"{candidate_id}: cases={summary['case_count']} "
            f"max_current={summary['max_current_total']} "
            f"max_shared={summary['max_shared_total']} "
            f"max_savings={summary['max_savings']} "
            f"max_shared_case={summary['case_with_max_shared_total']}"
        )


if __name__ == "__main__":
    main()
