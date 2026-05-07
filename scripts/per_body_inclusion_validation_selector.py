"""ALG-0032: validation selector for per-body rare loop inclusion."""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import cut_limited_body_support_guard
import cut_limited_length_bounded_loop
from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event
from petri_eval import precision_probe, replay_log
import selector_shared_accounting


TraceLog = List[List[str]]
Body = Tuple[str, ...]


def _trace_key(trace: Sequence[str]) -> Tuple[str, ...]:
    return tuple(trace)


def _sorted_traces(traces: Set[Tuple[str, ...]]) -> TraceLog:
    return [list(trace) for trace in sorted(traces)]


def _body_text(body: Sequence[str]) -> str:
    return " ".join(body)


def _body_rows(bodies: Sequence[Body]) -> List[List[str]]:
    return [list(body) for body in sorted(bodies)]


def _combine_counts(*operation_counts: Dict[str, int]) -> Dict[str, int]:
    return cut_limited_body_support_guard._combine_counts(  # pylint: disable=protected-access
        *operation_counts
    )


def _dominance_context(
    base_result: Dict[str, Any],
    counter: OpCounter,
    min_dominant_count: int,
    min_dominant_share_numerator: int,
    min_dominant_share_denominator: int,
    rare_body_count: int,
    max_rare_bodies: int,
) -> Dict[str, Any]:
    if min_dominant_share_denominator <= 0:
        raise ValueError("min_dominant_share_denominator must be positive")
    if max_rare_bodies < 0:
        raise ValueError("max_rare_bodies must be non-negative")

    evidence = base_result.get("pmir", {}).get("evidence", {})
    process_tree = evidence.get("process_tree", {})
    comparison(counter)
    if evidence.get("selected_cut") != "multi_body_rework_loop" or not isinstance(process_tree, dict):
        return {
            "detected": False,
            "selection_status": "no_per_body_alternatives",
            "reason": "source_not_multi_body_rework_loop",
            "source_selected_cut": evidence.get("selected_cut"),
        }

    body_counts = cut_limited_body_support_guard._support_to_bodies(  # pylint: disable=protected-access
        process_tree.get("body_support", {})
    )
    if not body_counts:
        return {
            "detected": False,
            "selection_status": "no_per_body_alternatives",
            "reason": "no_body_support",
        }

    total_body_observations = sum(body_counts.values())
    dominant_body, dominant_count = max(body_counts.items(), key=lambda item: (item[1], item[0]))
    comparison(counter, max(1, len(body_counts) - 1))
    arithmetic(counter, 2)
    dominant_share_ok = (
        dominant_count * min_dominant_share_denominator
        >= total_body_observations * min_dominant_share_numerator
    )
    comparison(counter, 2)
    config = {
        "min_dominant_count": min_dominant_count,
        "min_dominant_share": f"{min_dominant_share_numerator}/{min_dominant_share_denominator}",
        "rare_body_count": rare_body_count,
        "max_rare_bodies": max_rare_bodies,
        "dominant_body": list(dominant_body),
        "dominant_count": dominant_count,
        "total_body_observations": total_body_observations,
        "body_support": {
            _body_text(body): count for body, count in sorted(body_counts.items())
        },
    }
    if dominant_count < min_dominant_count:
        return {
            "detected": False,
            "selection_status": "dominance_threshold_not_met",
            "reason": "dominant_count_below_threshold",
            **config,
        }
    if not dominant_share_ok:
        return {
            "detected": False,
            "selection_status": "dominance_threshold_not_met",
            "reason": "dominant_share_below_threshold",
            **config,
        }

    rare_bodies: List[Body] = []
    for body, count in sorted(body_counts.items()):
        comparison(counter)
        if body != dominant_body and count == rare_body_count:
            rare_bodies.append(body)
            construct(counter)
    if not rare_bodies:
        return {
            "detected": False,
            "selection_status": "no_per_body_alternatives",
            "reason": "no_rare_candidate_bodies",
            **config,
        }
    if len(rare_bodies) > max_rare_bodies:
        return {
            "detected": False,
            "selection_status": "too_many_rare_bodies",
            "reason": "rare_body_alternative_budget_exceeded",
            "rare_candidate_bodies": _body_rows(rare_bodies),
            **config,
        }

    return {
        "detected": True,
        "selection_status": "alternatives_available",
        "reason": "rare_body_candidates_with_dominant_support",
        "prefix": process_tree["prefix"],
        "anchor": process_tree["anchor"],
        "suffix": process_tree["suffix"],
        "all_bodies": sorted(body_counts),
        "rare_bodies": rare_bodies,
        "rare_candidate_bodies": _body_rows(rare_bodies),
        **config,
    }


def _alternative_label(dropped_bodies: Sequence[Body]) -> str:
    if not dropped_bodies:
        return "drop_none"
    return "drop_" + "__".join(_body_text(body).replace(" ", "_") for body in sorted(dropped_bodies))


def _policy_from_drop_set(context: Dict[str, Any], dropped_bodies: Set[Body]) -> Dict[str, Any]:
    all_bodies = list(context["all_bodies"])
    kept_bodies = [body for body in all_bodies if body not in dropped_bodies]
    return {
        "applied": bool(dropped_bodies),
        "reason": "per_body_validation_drop_subset" if dropped_bodies else "per_body_validation_keep_all",
        "min_dominant_count": context["min_dominant_count"],
        "min_dominant_share": context["min_dominant_share"],
        "rare_body_count": context["rare_body_count"],
        "dominant_body": context["dominant_body"],
        "dominant_count": context["dominant_count"],
        "total_body_observations": context["total_body_observations"],
        "kept_bodies": _body_rows(kept_bodies),
        "filtered_bodies": _body_rows(sorted(dropped_bodies)),
        "rare_candidate_bodies": context["rare_candidate_bodies"],
        "rare_body_ambiguous": True,
        "selection_axis": "per_body_inclusion",
    }


def _build_alternatives(
    train: TraceLog,
    base_result: Dict[str, Any],
    context: Dict[str, Any],
    counter: OpCounter,
) -> List[Dict[str, Any]]:
    rare_bodies = list(context["rare_bodies"])
    alternatives: List[Dict[str, Any]] = []
    for drop_count in range(len(rare_bodies) + 1):
        for dropped in combinations(rare_bodies, drop_count):
            dropped_set = set(dropped)
            policy = _policy_from_drop_set(context, dropped_set)
            label = _alternative_label(sorted(dropped_set))
            if not dropped_set:
                result = base_result
            else:
                guard_counter = OpCounter()
                filtered_log, dropped_traces = cut_limited_body_support_guard._partition_log_by_body(  # pylint: disable=protected-access
                    train,
                    context["prefix"],
                    context["anchor"],
                    context["suffix"],
                    dropped_set,
                    guard_counter,
                )
                result = cut_limited_body_support_guard._build_guarded_result(  # pylint: disable=protected-access
                    base_result,
                    len(train),
                    filtered_log,
                    dropped_traces,
                    policy,
                    guard_counter.to_dict(),
                )
            alternatives.append(
                {
                    "alternative": label,
                    "dropped_bodies": _body_rows(sorted(dropped_set)),
                    "kept_bodies": policy["kept_bodies"],
                    "policy": policy,
                    "result": result,
                }
            )
            construct(counter)
    return alternatives


def _evaluate_alternative(
    alternative: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    replay_counter: OpCounter,
) -> Dict[str, Any]:
    result = alternative["result"]
    net = result["petri_net"]
    for trace in validation_positive + validation_negative:
        scan_event(replay_counter, len(trace))
        comparison(replay_counter)
    positive = replay_log(net, validation_positive)
    negative = precision_probe(net, validation_negative)
    return {
        "alternative": alternative["alternative"],
        "candidate_source": result.get("candidate_id"),
        "operation_total": result.get("operation_counts", {}).get("total"),
        "dropped_bodies": alternative["dropped_bodies"],
        "kept_bodies": alternative["kept_bodies"],
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


def _score_rows(scored: List[Tuple[Tuple[int, int, int], Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rows = []
    for score, evaluation in scored:
        rows.append(
            {
                "alternative": evaluation["alternative"],
                "candidate_source": evaluation["candidate_source"],
                "score": list(score),
                "validates_all": bool(score[0]),
                "dropped_bodies": evaluation["dropped_bodies"],
                "kept_bodies": evaluation["kept_bodies"],
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
            "reason": "no_per_body_assignments",
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
            "reason": "tie_or_conflicting_per_body_validation_evidence",
            "scores": scores,
        }
    if best_score[0] != 1:
        return {
            "selected_alternative": None,
            "selection_status": "unresolved",
            "reason": "no_per_body_assignment_satisfies_all_validation_probes",
            "scores": scores,
        }
    selected = best[0]
    return {
        "selected_alternative": selected["alternative"],
        "selection_status": "selected",
        "reason": "unique_per_body_assignment_satisfies_validation_probes",
        "scores": scores,
    }


def select(
    train: TraceLog,
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    min_dominant_count: int = 5,
    min_dominant_share_numerator: int = 5,
    min_dominant_share_denominator: int = 7,
    rare_body_count: int = 1,
    max_rare_bodies: int = 2,
) -> Dict[str, Any]:
    base_result = cut_limited_length_bounded_loop.discover(train)
    selector_counter = OpCounter()
    replay_counter = OpCounter()
    context = _dominance_context(
        base_result,
        selector_counter,
        min_dominant_count,
        min_dominant_share_numerator,
        min_dominant_share_denominator,
        rare_body_count,
        max_rare_bodies,
    )

    alternatives: List[Dict[str, Any]] = []
    evaluations: List[Dict[str, Any]] = []
    if context.get("detected"):
        alternatives = _build_alternatives(train, base_result, context, selector_counter)
        evaluations = [
            _evaluate_alternative(alternative, validation_positive, validation_negative, replay_counter)
            for alternative in alternatives
        ]

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
    elif not context.get("detected"):
        selection = {
            "selected_alternative": None,
            "selection_status": context["selection_status"],
            "reason": context["reason"],
            "scores": [],
        }
    else:
        selection = _select_unique_best(evaluations, selector_counter)

    selected_result = base_result
    selected_evaluation: Optional[Dict[str, Any]] = None
    for evaluation in evaluations:
        if evaluation["alternative"] == selection.get("selected_alternative"):
            selected_result = evaluation["result"]
            selected_evaluation = evaluation
            break

    result = deepcopy(selected_result)
    result["candidate_id"] = "ALG-0032"
    result["name"] = "Per-Body Rare Inclusion Validation Selector"
    evidence = result.setdefault("pmir", {}).setdefault("evidence", {})
    selector_counts = selector_counter.to_dict()
    replay_counts = replay_counter.to_dict()
    selected_dropped_bodies = selected_evaluation.get("dropped_bodies", []) if selected_evaluation else []
    selected_kept_bodies = selected_evaluation.get("kept_bodies", []) if selected_evaluation else []
    evidence["per_body_inclusion_validation_selector"] = {
        "validation_positive_count": len(validation_positive),
        "validation_negative_count": len(validation_negative),
        "selected_alternative": selection.get("selected_alternative"),
        "selected_dropped_bodies": selected_dropped_bodies,
        "selected_kept_bodies": selected_kept_bodies,
        "selection_status": selection["selection_status"],
        "reason": selection["reason"],
        "validation_overlap": _sorted_traces(validation_overlap),
        "training_negative_overlap": _sorted_traces(training_negative_overlap),
        "selector_operation_counts": selector_counts,
        "validation_replay_proxy_counts": replay_counts,
        "configuration": {
            "source_candidate": "ALG-0025",
            "min_dominant_count": min_dominant_count,
            "min_dominant_share": f"{min_dominant_share_numerator}/{min_dominant_share_denominator}",
            "rare_body_count": rare_body_count,
            "max_rare_bodies": max_rare_bodies,
        },
        "dominance_context": {
            key: value
            for key, value in context.items()
            if key
            not in {
                "all_bodies",
                "rare_bodies",
                "prefix",
                "anchor",
                "suffix",
            }
        },
        "alternative_count": len(alternatives),
        "scores": selection["scores"],
    }
    evidence["selected_per_body_inclusion_alternative"] = selection.get("selected_alternative")

    selected_total = int(result.get("operation_counts", {}).get("total", 0))
    all_alternative_total = sum(
        int(evaluation.get("operation_total") or 0)
        for evaluation in evaluations
    )
    if not evaluations:
        all_alternative_total = selected_total
    shared_accounting = selector_shared_accounting.shared_body_axis_accounting(
        evaluations,
        base_alternative="drop_none",
        selected_discovery_total=selected_total,
        selector_total=selector_counts["total"],
        validation_replay_proxy_total=replay_counts["total"],
        naive_all_alternative_discovery_total=all_alternative_total,
    )
    evidence["per_body_inclusion_validation_selector"]["shared_operation_accounting"] = shared_accounting
    operation_counts = dict(result.get("operation_counts", {}))
    operation_counts["selector_total"] = selector_counts["total"]
    operation_counts["validation_replay_proxy_total"] = replay_counts["total"]
    operation_counts["all_alternative_discovery_total"] = all_alternative_total
    operation_counts["shared_base_discovery_total"] = shared_accounting["base_discovery_total"]
    operation_counts["shared_incremental_discovery_extra_total"] = shared_accounting[
        "incremental_extra_total_after_shared_base"
    ]
    operation_counts["shared_all_alternative_discovery_total"] = shared_accounting[
        "shared_all_alternative_discovery_total"
    ]
    operation_counts["total_with_selector"] = selected_total + selector_counts["total"]
    operation_counts["total_with_selector_and_validation_proxy"] = (
        selected_total + selector_counts["total"] + replay_counts["total"]
    )
    operation_counts["total_with_all_alternatives_and_validation_proxy"] = (
        all_alternative_total + selector_counts["total"] + replay_counts["total"]
    )
    operation_counts["total_with_shared_alternatives_and_validation_proxy"] = (
        shared_accounting["shared_total_with_validation_proxy"]
    )
    operation_counts["shared_savings_vs_all_alternatives"] = shared_accounting[
        "shared_savings_vs_naive"
    ]
    result["operation_counts"] = operation_counts
    result["pmir"]["operation_counts"] = operation_counts
    return result
