"""ALG-0030: product selector for loop-body inclusion and loop-count policy."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

import body_inclusion_validation_selector
import loop_policy_set_protocol
from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event
from petri_eval import precision_probe, replay_log
import selector_shared_accounting


TraceLog = List[List[str]]


def _evaluate_policy(
    alternative: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    replay_counter: OpCounter,
) -> Dict[str, Any]:
    net = alternative["petri_net"]
    for trace in validation_positive + validation_negative:
        scan_event(replay_counter, len(trace))
        comparison(replay_counter)
    positive = replay_log(net, validation_positive)
    negative = precision_probe(net, validation_negative)
    return {
        "policy": alternative.get("policy"),
        "candidate_source": alternative.get("candidate_source"),
        "total_with_discovery_ops": alternative.get("total_with_discovery_ops"),
        "validation_positive": {
            "replayed_traces": positive["replayed_traces"],
            "trace_count": positive["trace_count"],
            "failed_examples": positive["failed_examples"],
        },
        "validation_negative": negative,
        "petri_net": net,
    }


def _policy_score(evaluation: Dict[str, Any], counter: OpCounter) -> Tuple[int, int, int]:
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


def _select_policy(
    policy_set: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    selector_counter: OpCounter,
    replay_counter: OpCounter,
) -> Dict[str, Any]:
    evaluations = []
    for alternative in policy_set.get("alternatives", []):
        if not isinstance(alternative.get("petri_net"), dict):
            continue
        evaluations.append(
            _evaluate_policy(
                alternative,
                validation_positive,
                validation_negative,
                replay_counter,
            )
        )
        construct(selector_counter)

    validation_overlap = sorted(
        set(tuple(trace) for trace in validation_positive)
        & set(tuple(trace) for trace in validation_negative)
    )
    comparison(selector_counter, len(validation_positive) + len(validation_negative))
    if not policy_set.get("detected"):
        return {
            "selected_policy": None,
            "selection_status": "no_policy_set",
            "reason": policy_set.get("reason") or "no_policy_set",
            "validation_overlap": [list(trace) for trace in validation_overlap],
            "scores": [],
            "evaluations": evaluations,
        }
    if validation_overlap:
        return {
            "selected_policy": None,
            "selection_status": "validation_inconsistent",
            "reason": "validation_trace_is_both_positive_and_negative",
            "validation_overlap": [list(trace) for trace in validation_overlap],
            "scores": [],
            "evaluations": evaluations,
        }

    scored: List[Tuple[Tuple[int, int, int], Dict[str, Any]]] = []
    for evaluation in evaluations:
        score = _policy_score(evaluation, selector_counter)
        scored.append((score, evaluation))
        construct(selector_counter)
    scored.sort(key=lambda item: (item[0], item[1].get("policy") or ""))
    comparison(selector_counter, max(0, len(scored) - 1))
    if not scored:
        return {
            "selected_policy": None,
            "selection_status": "unresolved",
            "reason": "no_policy_alternatives",
            "validation_overlap": [list(trace) for trace in validation_overlap],
            "scores": [],
            "evaluations": evaluations,
        }
    best_score = scored[-1][0]
    best = [evaluation for score, evaluation in scored if score == best_score]
    comparison(selector_counter, len(scored))
    scores = [
        {
            "policy": evaluation.get("policy"),
            "score": list(score),
            "validates_all": bool(score[0]),
            "validation_positive": evaluation["validation_positive"],
            "validation_negative": evaluation["validation_negative"],
            "total_with_discovery_ops": evaluation.get("total_with_discovery_ops"),
        }
        for score, evaluation in scored
    ]
    if len(best) != 1:
        return {
            "selected_policy": None,
            "selection_status": "unresolved",
            "reason": "tie_or_conflicting_validation_evidence",
            "validation_overlap": [list(trace) for trace in validation_overlap],
            "scores": scores,
            "evaluations": evaluations,
        }
    if best_score[0] != 1:
        return {
            "selected_policy": None,
            "selection_status": "unresolved",
            "reason": "no_policy_satisfies_all_validation_probes",
            "validation_overlap": [list(trace) for trace in validation_overlap],
            "scores": scores,
            "evaluations": evaluations,
        }
    return {
        "selected_policy": best[0].get("policy"),
        "selection_status": "selected",
        "reason": "unique_count_policy_satisfies_validation_probes",
        "validation_overlap": [list(trace) for trace in validation_overlap],
        "scores": scores,
        "evaluations": evaluations,
    }


def _find_policy_net(policy_selection: Dict[str, Any], selected_policy: Optional[str]) -> Optional[Dict[str, Any]]:
    if selected_policy is None:
        return None
    for evaluation in policy_selection.get("evaluations", []):
        if evaluation.get("policy") == selected_policy:
            return evaluation.get("petri_net")
    return None


def select(
    train: TraceLog,
    body_validation_positive: TraceLog,
    body_validation_negative: TraceLog,
    count_validation_positive: TraceLog,
    count_validation_negative: TraceLog,
    guard_policy: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    body_result = body_inclusion_validation_selector.select(
        train,
        body_validation_positive,
        body_validation_negative,
        guard_policy=guard_policy,
    )
    body_selector = body_result.get("pmir", {}).get("evidence", {}).get(
        "body_inclusion_validation_selector", {}
    )
    selected_body = body_selector.get("selected_alternative")
    result = deepcopy(body_result)
    result["candidate_id"] = "ALG-0030"
    result["name"] = "Loop Body-Count Validation Product Selector"

    count_selector_counter = OpCounter()
    count_replay_counter = OpCounter()
    policy_result: Optional[Dict[str, Any]] = None
    count_selection: Dict[str, Any]
    if body_selector.get("selection_status") != "selected":
        count_selection = {
            "selected_policy": None,
            "selection_status": "body_selection_not_selected",
            "reason": body_selector.get("reason") or "body_selection_not_selected",
            "validation_overlap": [],
            "scores": [],
        }
    else:
        policy_result = loop_policy_set_protocol.result_from_base(
            body_result,
            candidate_id_override="ALG-0030",
            name_override="Loop Body-Count Validation Product Selector",
        )
        policy_set = policy_result.get("pmir", {}).get("evidence", {}).get(
            "loop_count_policy_set", {}
        )
        count_selection = _select_policy(
            policy_set,
            count_validation_positive,
            count_validation_negative,
            count_selector_counter,
            count_replay_counter,
        )

    selected_policy = count_selection.get("selected_policy")
    selected_net = _find_policy_net(count_selection, selected_policy)
    if selected_net is not None:
        result["petri_net"] = selected_net
    elif policy_result is not None:
        result["petri_net"] = policy_result.get("petri_net", result["petri_net"])

    count_selector_counts = count_selector_counter.to_dict()
    count_replay_counts = count_replay_counter.to_dict()
    evidence = result.setdefault("pmir", {}).setdefault("evidence", {})
    if policy_result is not None:
        evidence["loop_count_policy_set"] = policy_result.get("pmir", {}).get("evidence", {}).get(
            "loop_count_policy_set", {}
        )
    if body_selector.get("selection_status") == "selected" and count_selection.get("selection_status") == "selected":
        product_status = "selected"
        product_reason = "body_inclusion_and_count_policy_selected"
    elif body_selector.get("selection_status") != "selected":
        product_status = "body_unresolved"
        product_reason = count_selection["reason"]
    else:
        product_status = "count_unresolved"
        product_reason = count_selection["reason"]
    evidence["body_count_validation_product_selector"] = {
        "selected_body_alternative": selected_body,
        "selected_count_policy": selected_policy,
        "selection_status": product_status,
        "reason": product_reason,
        "body_selector_status": body_selector.get("selection_status"),
        "count_selector_status": count_selection.get("selection_status"),
        "body_validation_positive_count": len(body_validation_positive),
        "body_validation_negative_count": len(body_validation_negative),
        "count_validation_positive_count": len(count_validation_positive),
        "count_validation_negative_count": len(count_validation_negative),
        "count_validation_overlap": count_selection.get("validation_overlap", []),
        "count_selector_operation_counts": count_selector_counts,
        "count_validation_replay_proxy_counts": count_replay_counts,
        "count_scores": count_selection.get("scores", []),
        "guard_policy": dict(guard_policy or {}),
    }
    evidence["selected_body_inclusion_alternative"] = selected_body
    evidence["selected_count_policy"] = selected_policy

    operation_counts = dict(result.get("operation_counts", {}))
    body_total = operation_counts.get("total_with_all_alternatives_and_validation_proxy", 0)
    body_shared_total = operation_counts.get(
        "total_with_shared_alternatives_and_validation_proxy",
        body_total,
    )
    selected_body_total = operation_counts.get("total", 0)
    selected_count_total = selected_body_total
    if selected_policy is not None:
        for score in count_selection.get("scores", []):
            if score.get("policy") == selected_policy:
                selected_count_total = score.get("total_with_discovery_ops") or selected_body_total
                break
    count_compile_extra = max(0, int(selected_count_total) - int(selected_body_total))
    all_count_compile_extra = 0
    count_compile_alternatives = []
    loop_policy_set = evidence.get("loop_count_policy_set", {})
    for alternative in loop_policy_set.get("alternatives", []):
        compile_total = selector_shared_accounting.as_int(
            alternative.get("compile_operation_counts", {}).get("total")
        )
        all_count_compile_extra += compile_total
        count_compile_alternatives.append(
            {
                "policy": alternative.get("policy"),
                "candidate_source": alternative.get("candidate_source"),
                "compile_extra_total": compile_total,
            }
        )
    operation_counts["count_selector_total"] = count_selector_counts["total"]
    operation_counts["count_validation_replay_proxy_total"] = count_replay_counts["total"]
    operation_counts["count_compile_extra_total"] = count_compile_extra
    operation_counts["count_all_compile_extra_total"] = all_count_compile_extra
    operation_counts["body_shared_total_with_validation_proxy"] = int(body_shared_total)
    operation_counts["total_with_product_selector_and_validation_proxy"] = (
        int(body_total)
        + count_compile_extra
        + count_selector_counts["total"]
        + count_replay_counts["total"]
    )
    operation_counts["total_with_shared_product_selected_count_and_validation_proxy"] = (
        int(body_shared_total)
        + count_compile_extra
        + count_selector_counts["total"]
        + count_replay_counts["total"]
    )
    operation_counts["total_with_shared_product_all_count_alternatives_and_validation_proxy"] = (
        int(body_shared_total)
        + all_count_compile_extra
        + count_selector_counts["total"]
        + count_replay_counts["total"]
    )
    product_shared_accounting = {
        "method": "shared_body_axis_plus_count_policy_compile_extras",
        "body_shared_total_with_validation_proxy": int(body_shared_total),
        "body_naive_total_with_validation_proxy": int(body_total),
        "selected_count_compile_extra_total": count_compile_extra,
        "all_count_compile_extra_total": all_count_compile_extra,
        "count_selector_total": count_selector_counts["total"],
        "count_validation_replay_proxy_total": count_replay_counts["total"],
        "total_with_selected_count_compile_extra": operation_counts[
            "total_with_shared_product_selected_count_and_validation_proxy"
        ],
        "total_with_all_count_compile_extras": operation_counts[
            "total_with_shared_product_all_count_alternatives_and_validation_proxy"
        ],
        "savings_vs_reported_product_selected_count": (
            operation_counts["total_with_product_selector_and_validation_proxy"]
            - operation_counts["total_with_shared_product_selected_count_and_validation_proxy"]
        ),
        "savings_vs_reported_product_all_count": (
            operation_counts["total_with_product_selector_and_validation_proxy"]
            - operation_counts["total_with_shared_product_all_count_alternatives_and_validation_proxy"]
        ),
        "count_compile_alternatives": count_compile_alternatives,
    }
    evidence["body_count_validation_product_selector"]["shared_operation_accounting"] = (
        product_shared_accounting
    )
    result["operation_counts"] = operation_counts
    result["pmir"]["operation_counts"] = operation_counts
    return result
