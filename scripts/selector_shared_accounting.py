"""Shared operation-accounting helpers for validation selectors."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def as_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def shared_body_axis_accounting(
    evaluations: List[Dict[str, Any]],
    base_alternative: str,
    selected_discovery_total: int,
    selector_total: int,
    validation_replay_proxy_total: int,
    naive_all_alternative_discovery_total: Optional[int] = None,
) -> Dict[str, Any]:
    """Compute shared-base totals from evaluated body alternatives.

    The selector prototypes expose total counts for each alternative. This helper
    charges the base alternative once and charges non-base alternatives by the
    measured incremental total over that base.
    """

    base_total = selected_discovery_total
    for evaluation in evaluations:
        if evaluation.get("alternative") == base_alternative:
            base_total = as_int(evaluation.get("operation_total"), selected_discovery_total)
            break

    alternatives = []
    naive_from_evaluations = 0
    incremental_extra_total = 0
    for evaluation in evaluations:
        alternative = evaluation.get("alternative")
        operation_total = as_int(evaluation.get("operation_total"))
        naive_from_evaluations += operation_total
        incremental_extra = 0
        if alternative != base_alternative:
            incremental_extra = max(0, operation_total - base_total)
            incremental_extra_total += incremental_extra
        alternatives.append(
            {
                "alternative": alternative,
                "operation_total": operation_total,
                "incremental_extra_after_shared_base": incremental_extra,
                "is_base_alternative": alternative == base_alternative,
            }
        )

    if not evaluations:
        naive_from_evaluations = selected_discovery_total

    naive_discovery_total = as_int(
        naive_all_alternative_discovery_total,
        naive_from_evaluations,
    )
    shared_discovery_total = base_total + incremental_extra_total
    naive_total = naive_discovery_total + selector_total + validation_replay_proxy_total
    shared_total = shared_discovery_total + selector_total + validation_replay_proxy_total
    return {
        "method": "single_shared_base_plus_incremental_alternative_extras",
        "base_alternative": base_alternative,
        "selected_discovery_total": selected_discovery_total,
        "base_discovery_total": base_total,
        "alternative_count": len(evaluations),
        "naive_all_alternative_discovery_total": naive_discovery_total,
        "incremental_extra_total_after_shared_base": incremental_extra_total,
        "shared_all_alternative_discovery_total": shared_discovery_total,
        "selector_total": selector_total,
        "validation_replay_proxy_total": validation_replay_proxy_total,
        "naive_total_with_validation_proxy": naive_total,
        "shared_total_with_validation_proxy": shared_total,
        "shared_savings_vs_naive": naive_total - shared_total,
        "alternatives": alternatives,
    }
