"""ALG-0029: validation selector for loop-body inclusion alternatives."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import cut_limited_body_support_guard
import cut_limited_length_bounded_loop
from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event
from petri_eval import precision_probe, replay_log
import selector_shared_accounting


TraceLog = List[List[str]]


def _trace_key(trace: List[str]) -> Tuple[str, ...]:
    return tuple(trace)


def _sorted_traces(traces: set[Tuple[str, ...]]) -> TraceLog:
    return [list(trace) for trace in sorted(traces)]


def _evaluate_alternative(
    label: str,
    result: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    replay_counter: OpCounter,
) -> Dict[str, Any]:
    net = result["petri_net"]
    for trace in validation_positive + validation_negative:
        scan_event(replay_counter, len(trace))
        comparison(replay_counter)
    positive = replay_log(net, validation_positive)
    negative = precision_probe(net, validation_negative)
    support_guard = result.get("pmir", {}).get("evidence", {}).get("support_guard", {})
    return {
        "alternative": label,
        "candidate_source": result.get("candidate_id"),
        "operation_total": result.get("operation_counts", {}).get("total"),
        "support_guard_applied": support_guard.get("applied"),
        "filtered_bodies": support_guard.get("filtered_bodies", []),
        "validation_positive": {
            "replayed_traces": positive["replayed_traces"],
            "trace_count": positive["trace_count"],
            "failed_examples": positive["failed_examples"],
        },
        "validation_negative": negative,
        "petri_net": net,
        "result": result,
    }


def _alternative_score(evaluation: Dict[str, Any], counter: OpCounter) -> Tuple[int, int, int]:
    positive = evaluation["validation_positive"]
    negative = evaluation["validation_negative"]
    positive_misses = positive["trace_count"] - positive["replayed_traces"]
    accepted_negatives = negative["accepted_negative_traces"]
    arithmetic(counter, 2)
    valid = 1 if positive_misses == 0 and accepted_negatives == 0 else 0
    comparison(counter, 2)
    total_hits = positive["replayed_traces"] + negative["rejected_negative_traces"]
    arithmetic(counter)
    return (valid, total_hits, -accepted_negatives)


def _score_rows(
    scored: List[Tuple[Tuple[int, int, int], Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    rows = []
    for score, evaluation in scored:
        rows.append(
            {
                "alternative": evaluation["alternative"],
                "candidate_source": evaluation["candidate_source"],
                "score": list(score),
                "validates_all": bool(score[0]),
                "support_guard_applied": evaluation["support_guard_applied"],
                "filtered_bodies": evaluation["filtered_bodies"],
                "validation_positive": evaluation["validation_positive"],
                "validation_negative": evaluation["validation_negative"],
                "operation_total": evaluation["operation_total"],
            }
        )
    return rows


def _select_unique_best(
    evaluations: List[Dict[str, Any]],
    counter: OpCounter,
) -> Dict[str, Any]:
    scored: List[Tuple[Tuple[int, int, int], Dict[str, Any]]] = []
    for evaluation in evaluations:
        score = _alternative_score(evaluation, counter)
        scored.append((score, evaluation))
        construct(counter)
    scored.sort(key=lambda item: (item[0], item[1]["alternative"]))
    comparison(counter, max(0, len(scored) - 1))
    if not scored:
        return {
            "selected_alternative": None,
            "selection_status": "unresolved",
            "reason": "no_alternatives",
            "scores": [],
        }
    best_score = scored[-1][0]
    best = [evaluation for score, evaluation in scored if score == best_score]
    comparison(counter, len(scored))
    scores = _score_rows(scored)
    if len(best) != 1:
        return {
            "selected_alternative": None,
            "selection_status": "unresolved",
            "reason": "tie_or_conflicting_validation_evidence",
            "scores": scores,
        }
    if best_score[0] != 1:
        return {
            "selected_alternative": None,
            "selection_status": "unresolved",
            "reason": "no_alternative_satisfies_all_validation_probes",
            "scores": scores,
        }
    selected = best[0]
    return {
        "selected_alternative": selected["alternative"],
        "selection_status": "selected",
        "reason": "unique_body_inclusion_alternative_satisfies_validation_probes",
        "scores": scores,
    }


def select(
    train: TraceLog,
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    guard_policy: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    guard_policy = dict(guard_policy or {})
    keep_all = cut_limited_length_bounded_loop.discover(train)
    support_guard = cut_limited_body_support_guard.discover_with_policy(train, **guard_policy)
    replay_counter = OpCounter()
    selector_counter = OpCounter()
    evaluations = [
        _evaluate_alternative("keep_all_bodies", keep_all, validation_positive, validation_negative, replay_counter),
        _evaluate_alternative("support_guard", support_guard, validation_positive, validation_negative, replay_counter),
    ]
    construct(selector_counter, len(evaluations))

    positive_keys = {_trace_key(trace) for trace in validation_positive}
    negative_keys = {_trace_key(trace) for trace in validation_negative}
    train_keys = {_trace_key(trace) for trace in train}
    validation_overlap = positive_keys & negative_keys
    training_negative_overlap = train_keys & negative_keys
    comparison(selector_counter, len(validation_positive) + len(validation_negative) + len(train))

    if validation_overlap:
        selection = _select_unique_best(evaluations, selector_counter)
        selection["selected_alternative"] = None
        selection["selection_status"] = "validation_inconsistent"
        selection["reason"] = "validation_trace_is_both_positive_and_negative"
    elif training_negative_overlap:
        selection = _select_unique_best(evaluations, selector_counter)
        selection["selected_alternative"] = None
        selection["selection_status"] = "validation_training_conflict"
        selection["reason"] = "validation_negative_contains_training_trace"
    else:
        selection = _select_unique_best(evaluations, selector_counter)

    selected_alternative: Optional[str] = selection.get("selected_alternative")
    selected_result = keep_all
    for evaluation in evaluations:
        if evaluation["alternative"] == selected_alternative:
            selected_result = evaluation["result"]
            break

    result = deepcopy(selected_result)
    result["candidate_id"] = "ALG-0029"
    result["name"] = "Loop Body Inclusion Validation Selector"
    evidence = result.setdefault("pmir", {}).setdefault("evidence", {})
    selector_counts = selector_counter.to_dict()
    replay_counts = replay_counter.to_dict()
    evidence["body_inclusion_validation_selector"] = {
        "validation_positive_count": len(validation_positive),
        "validation_negative_count": len(validation_negative),
        "selected_alternative": selected_alternative,
        "selection_status": selection["selection_status"],
        "reason": selection["reason"],
        "validation_overlap": _sorted_traces(validation_overlap),
        "training_negative_overlap": _sorted_traces(training_negative_overlap),
        "selector_operation_counts": selector_counts,
        "validation_replay_proxy_counts": replay_counts,
        "guard_policy": guard_policy,
        "scores": selection["scores"],
    }
    result["pmir"]["evidence"]["selected_body_inclusion_alternative"] = selected_alternative
    selected_total = result.get("operation_counts", {}).get("total", 0)
    all_alternative_total = sum(
        int(evaluation.get("operation_total") or 0)
        for evaluation in evaluations
    )
    shared_accounting = selector_shared_accounting.shared_body_axis_accounting(
        evaluations,
        base_alternative="keep_all_bodies",
        selected_discovery_total=int(selected_total),
        selector_total=selector_counts["total"],
        validation_replay_proxy_total=replay_counts["total"],
        naive_all_alternative_discovery_total=all_alternative_total,
    )
    evidence["body_inclusion_validation_selector"]["shared_operation_accounting"] = shared_accounting
    result["operation_counts"] = dict(result.get("operation_counts", {}))
    result["operation_counts"]["selector_total"] = selector_counts["total"]
    result["operation_counts"]["validation_replay_proxy_total"] = replay_counts["total"]
    result["operation_counts"]["all_alternative_discovery_total"] = all_alternative_total
    result["operation_counts"]["shared_base_discovery_total"] = shared_accounting[
        "base_discovery_total"
    ]
    result["operation_counts"]["shared_incremental_discovery_extra_total"] = shared_accounting[
        "incremental_extra_total_after_shared_base"
    ]
    result["operation_counts"]["shared_all_alternative_discovery_total"] = shared_accounting[
        "shared_all_alternative_discovery_total"
    ]
    result["operation_counts"]["total_with_selector"] = selected_total + selector_counts["total"]
    result["operation_counts"]["total_with_selector_and_validation_proxy"] = (
        selected_total + selector_counts["total"] + replay_counts["total"]
    )
    result["operation_counts"]["total_with_all_alternatives_and_validation_proxy"] = (
        all_alternative_total + selector_counts["total"] + replay_counts["total"]
    )
    result["operation_counts"]["total_with_shared_alternatives_and_validation_proxy"] = (
        shared_accounting["shared_total_with_validation_proxy"]
    )
    result["operation_counts"]["shared_savings_vs_all_alternatives"] = shared_accounting[
        "shared_savings_vs_naive"
    ]
    result["pmir"]["operation_counts"] = result["operation_counts"]
    return result
