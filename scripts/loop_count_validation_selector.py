"""ALG-0027: validation selector for ALG-0026 loop-count policy sets."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event
import loop_policy_set_protocol
from petri_eval import precision_probe, replay_log


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


def _select_unique_best(
    evaluations: List[Dict[str, Any]],
    counter: OpCounter,
) -> Dict[str, Any]:
    scored: List[Tuple[Tuple[int, int, int], Dict[str, Any]]] = []
    for evaluation in evaluations:
        score = _policy_score(evaluation, counter)
        scored.append((score, evaluation))
        construct(counter)
    scored.sort(key=lambda item: (item[0], item[1].get("policy") or ""))
    comparison(counter, max(0, len(scored) - 1))
    if not scored:
        return {
            "selected_policy": None,
            "selection_status": "unresolved",
            "reason": "no_policy_alternatives",
            "scores": [],
        }
    best_score = scored[-1][0]
    best = [evaluation for score, evaluation in scored if score == best_score]
    comparison(counter, len(scored))
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
            "scores": scores,
        }
    selected = best[0]
    if best_score[0] != 1:
        return {
            "selected_policy": None,
            "selection_status": "unresolved",
            "reason": "no_policy_satisfies_all_validation_probes",
            "scores": scores,
        }
    return {
        "selected_policy": selected.get("policy"),
        "selection_status": "selected",
        "reason": "unique_policy_satisfies_validation_probes",
        "scores": scores,
    }


def select(
    train: TraceLog,
    validation_positive: TraceLog,
    validation_negative: TraceLog,
) -> Dict[str, Any]:
    policy_result = loop_policy_set_protocol.discover(train)
    policy_set = policy_result.get("pmir", {}).get("evidence", {}).get("loop_count_policy_set", {})
    counter = OpCounter()
    validation_replay_counter = OpCounter()
    evaluations: List[Dict[str, Any]] = []
    for alternative in policy_set.get("alternatives", []):
        if not isinstance(alternative.get("petri_net"), dict):
            continue
        evaluations.append(
            _evaluate_policy(alternative, validation_positive, validation_negative, validation_replay_counter)
        )
        construct(counter)

    validation_overlap = sorted(
        set(tuple(trace) for trace in validation_positive) & set(tuple(trace) for trace in validation_negative)
    )
    comparison(counter, len(validation_positive) + len(validation_negative))
    if not policy_set.get("detected"):
        selection = {
            "selected_policy": None,
            "selection_status": "no_policy_set",
            "reason": policy_set.get("reason") or "no_policy_set",
            "scores": [],
        }
    elif validation_overlap:
        selection = _select_unique_best(evaluations, counter)
        selection["selected_policy"] = None
        selection["selection_status"] = "validation_inconsistent"
        selection["reason"] = "validation_trace_is_both_positive_and_negative"
    else:
        selection = _select_unique_best(evaluations, counter)
    selector_counts = counter.to_dict()
    validation_replay_counts = validation_replay_counter.to_dict()
    result = deepcopy(policy_result)
    result["candidate_id"] = "ALG-0027"
    result["name"] = "Loop Count Validation Selector"
    selected_policy: Optional[str] = selection.get("selected_policy")
    if selected_policy is not None:
        for evaluation in evaluations:
            if evaluation.get("policy") == selected_policy:
                result["petri_net"] = evaluation["petri_net"]
                break
    result["pmir"]["evidence"]["loop_count_validation_selector"] = {
        "validation_positive_count": len(validation_positive),
        "validation_negative_count": len(validation_negative),
        "selected_policy": selected_policy,
        "selection_status": selection["selection_status"],
        "reason": selection["reason"],
        "validation_overlap": [list(trace) for trace in validation_overlap],
        "selector_operation_counts": selector_counts,
        "validation_replay_proxy_counts": validation_replay_counts,
        "scores": selection["scores"],
    }
    result["pmir"]["evidence"]["selected_policy"] = selected_policy
    base_total = result.get("operation_counts", {}).get("total", 0)
    result["operation_counts"] = dict(result.get("operation_counts", {}))
    result["operation_counts"]["selector_total"] = selector_counts["total"]
    result["operation_counts"]["validation_replay_proxy_total"] = validation_replay_counts["total"]
    result["operation_counts"]["total_with_selector"] = base_total + selector_counts["total"]
    result["operation_counts"]["total_with_selector_and_validation_proxy"] = (
        base_total + selector_counts["total"] + validation_replay_counts["total"]
    )
    return result
