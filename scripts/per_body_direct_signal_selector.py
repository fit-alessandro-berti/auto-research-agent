"""ALG-0033: direct-signal selector for rare loop-body inclusion.

This candidate is intentionally narrower than ALG-0032. It avoids enumerating
all rare-body keep/drop subsets by accepting only direct validation evidence:
positive validation traces that contain one rare body keep that body, and
negative validation traces that contain exactly one rare body drop that body.
Multi-rare negative traces are treated as interaction evidence unless the
singleton signals already identify every rare body.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import cut_limited_body_support_guard
import cut_limited_length_bounded_loop
from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event, set_lookup
import per_body_inclusion_validation_selector as exhaustive_selector
from petri_eval import precision_probe, replay_log


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


def _extract_loop_bodies(
    trace: Sequence[str],
    prefix: Sequence[str],
    anchor: str,
    suffix: Sequence[str],
    counter: OpCounter,
) -> Optional[List[Body]]:
    """Parse a trace against the source loop context and return body segments."""

    scan_event(counter, len(trace))
    prefix_list = list(prefix)
    suffix_list = list(suffix)
    comparison(counter, 4)
    if len(trace) < len(prefix_list) + 1 + len(suffix_list):
        return None
    if list(trace[: len(prefix_list)]) != prefix_list:
        return None
    anchor_index = len(prefix_list)
    if trace[anchor_index] != anchor:
        return None
    loop_end = len(trace) - len(suffix_list)
    if suffix_list and list(trace[loop_end:]) != suffix_list:
        return None

    bodies: List[Body] = []
    index = anchor_index + 1
    comparison(counter)
    while index < loop_end:
        next_anchor = None
        for candidate in range(index, loop_end):
            comparison(counter)
            if trace[candidate] == anchor:
                next_anchor = candidate
                break
        comparison(counter)
        if next_anchor is None:
            return None
        body = tuple(trace[index:next_anchor])
        comparison(counter)
        if not body:
            return None
        bodies.append(body)
        construct(counter)
        index = next_anchor + 1
        arithmetic(counter)
    return bodies


def _empty_signal_row(body: Body) -> Dict[str, Any]:
    return {
        "body": list(body),
        "positive_trace_count": 0,
        "negative_trace_count": 0,
        "action": "unresolved",
        "positive_examples": [],
        "negative_examples": [],
    }


def _direct_signal_assignment(
    context: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    counter: OpCounter,
) -> Dict[str, Any]:
    rare_bodies = sorted(context["rare_bodies"])
    rare_set = set(rare_bodies)
    signals: Dict[Body, Dict[str, Any]] = {
        body: _empty_signal_row(body) for body in rare_bodies
    }
    negative_clauses: List[Dict[str, Any]] = []
    ambiguous_negative_traces: List[Dict[str, Any]] = []
    malformed_validation_traces: List[List[str]] = []

    for trace in validation_positive:
        bodies = _extract_loop_bodies(
            trace,
            context["prefix"],
            context["anchor"],
            context["suffix"],
            counter,
        )
        comparison(counter)
        if bodies is None:
            malformed_validation_traces.append(list(trace))
            construct(counter)
            continue
        hits = sorted({body for body in bodies if body in rare_set})
        set_lookup(counter, len(bodies))
        for body in hits:
            signals[body]["positive_trace_count"] += 1
            signals[body]["positive_examples"].append(list(trace))
            arithmetic(counter)
            construct(counter)

    for trace in validation_negative:
        bodies = _extract_loop_bodies(
            trace,
            context["prefix"],
            context["anchor"],
            context["suffix"],
            counter,
        )
        comparison(counter)
        if bodies is None:
            malformed_validation_traces.append(list(trace))
            construct(counter)
            continue
        hits = sorted({body for body in bodies if body in rare_set})
        set_lookup(counter, len(bodies))
        comparison(counter)
        if hits:
            negative_clauses.append(
                {
                    "trace": list(trace),
                    "rare_bodies": hits,
                }
            )
            construct(counter)

    positive_kept = {
        body for body, row in signals.items() if row["positive_trace_count"] > 0
    }
    for clause in negative_clauses:
        hits = list(clause["rare_bodies"])
        undecided_hits = [body for body in hits if body not in positive_kept]
        comparison(counter, len(hits) + 1)
        if not undecided_hits:
            for body in hits:
                signals[body]["negative_trace_count"] += 1
                signals[body]["negative_examples"].append(clause["trace"])
                arithmetic(counter)
                construct(counter)
        elif len(undecided_hits) == 1:
            body = undecided_hits[0]
            signals[body]["negative_trace_count"] += 1
            signals[body]["negative_examples"].append(clause["trace"])
            arithmetic(counter)
            construct(counter)
        else:
            ambiguous_negative_traces.append(
                {
                    "trace": clause["trace"],
                    "rare_bodies": _body_rows(undecided_hits),
                    "required_keep_bodies": _body_rows(
                        body for body in hits if body in positive_kept
                    ),
                }
            )
            construct(counter)

    dropped: Set[Body] = set()
    kept: Set[Body] = set()
    unresolved: List[Body] = []
    conflicts: List[Body] = []
    for body in rare_bodies:
        row = signals[body]
        has_positive = row["positive_trace_count"] > 0
        has_negative = row["negative_trace_count"] > 0
        comparison(counter, 2)
        if has_positive and has_negative:
            row["action"] = "conflict"
            conflicts.append(body)
            construct(counter)
        elif has_positive:
            row["action"] = "keep"
            kept.add(body)
            construct(counter)
        elif has_negative:
            row["action"] = "drop"
            dropped.add(body)
            construct(counter)
        else:
            row["action"] = "unresolved"
            unresolved.append(body)
            construct(counter)

    comparison(counter, 2)
    if conflicts:
        status = "body_signal_conflict"
        reason = "rare_body_has_positive_and_negative_direct_signal"
    elif unresolved and ambiguous_negative_traces:
        status = "interaction_ambiguous"
        reason = "negative_trace_mentions_multiple_rare_bodies_without_direct_assignment"
    elif unresolved:
        status = "partial_direct_signal"
        reason = "missing_direct_body_signal"
    else:
        status = "direct_assignment_available"
        reason = "direct_body_signals_identify_assignment"

    return {
        "status": status,
        "reason": reason,
        "dropped_bodies": dropped,
        "kept_rare_bodies": kept,
        "unresolved_bodies": unresolved,
        "conflicting_bodies": conflicts,
        "signals": [signals[body] for body in rare_bodies],
        "ambiguous_negative_traces": ambiguous_negative_traces,
        "malformed_validation_traces": malformed_validation_traces,
    }


def _build_selected_result(
    train: TraceLog,
    base_result: Dict[str, Any],
    context: Dict[str, Any],
    dropped_bodies: Set[Body],
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    if not dropped_bodies:
        return base_result, {"total": 0}

    guard_counter = OpCounter()
    policy = exhaustive_selector._policy_from_drop_set(  # pylint: disable=protected-access
        context,
        dropped_bodies,
    )
    filtered_log, dropped_traces = cut_limited_body_support_guard._partition_log_by_body(  # pylint: disable=protected-access
        train,
        context["prefix"],
        context["anchor"],
        context["suffix"],
        dropped_bodies,
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
    return result, guard_counter.to_dict()


def _validation_summary(
    result: Dict[str, Any],
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    counter: OpCounter,
) -> Dict[str, Any]:
    for trace in validation_positive + validation_negative:
        scan_event(counter, len(trace))
        comparison(counter)
    positive = replay_log(result["petri_net"], validation_positive)
    negative = precision_probe(result["petri_net"], validation_negative)
    return {
        "positive": {
            "replayed_traces": positive["replayed_traces"],
            "trace_count": positive["trace_count"],
            "failed_examples": positive["failed_examples"],
        },
        "negative": negative,
        "validates_all": (
            positive["replayed_traces"] == positive["trace_count"]
            and negative["accepted_negative_traces"] == 0
        ),
    }


def _retag_result(
    result: Dict[str, Any],
    evidence_payload: Dict[str, Any],
    operation_counts: Dict[str, int],
) -> Dict[str, Any]:
    tagged = deepcopy(result)
    tagged["candidate_id"] = "ALG-0033"
    tagged["name"] = "Per-Body Direct-Signal Validation Selector"
    evidence = tagged.setdefault("pmir", {}).setdefault("evidence", {})
    evidence["per_body_direct_signal_selector"] = evidence_payload
    evidence["selected_per_body_direct_signal_alternative"] = evidence_payload.get(
        "selected_alternative"
    )
    tagged["operation_counts"] = operation_counts
    tagged["pmir"]["operation_counts"] = operation_counts
    return tagged


def select(
    train: TraceLog,
    validation_positive: TraceLog,
    validation_negative: TraceLog,
    min_dominant_count: int = 5,
    min_dominant_share_numerator: int = 5,
    min_dominant_share_denominator: int = 7,
    rare_body_count: int = 1,
    max_rare_bodies: int = 5,
) -> Dict[str, Any]:
    base_result = cut_limited_length_bounded_loop.discover(train)
    selector_counter = OpCounter()
    validation_counter = OpCounter()
    context = exhaustive_selector._dominance_context(  # pylint: disable=protected-access
        base_result,
        selector_counter,
        min_dominant_count,
        min_dominant_share_numerator,
        min_dominant_share_denominator,
        rare_body_count,
        max_rare_bodies,
    )

    positive_keys = {_trace_key(trace) for trace in validation_positive}
    negative_keys = {_trace_key(trace) for trace in validation_negative}
    train_keys = {_trace_key(trace) for trace in train}
    validation_overlap = positive_keys & negative_keys
    training_negative_overlap = train_keys & negative_keys
    comparison(selector_counter, len(validation_positive) + len(validation_negative) + len(train))

    selected_result = base_result
    selected_alternative: Optional[str] = None
    selected_dropped_bodies: List[List[str]] = []
    selected_kept_bodies: List[List[str]] = []
    guard_counts = {"total": 0}
    validation_result: Optional[Dict[str, Any]] = None
    attempted_compile_extra_total = 0
    base_total = int(base_result.get("operation_counts", {}).get("total", 0))
    direct_assignment: Dict[str, Any] = {
        "status": context["selection_status"],
        "reason": context["reason"],
        "dropped_bodies": set(),
        "kept_rare_bodies": set(),
        "unresolved_bodies": [],
        "conflicting_bodies": [],
        "signals": [],
        "ambiguous_negative_traces": [],
        "malformed_validation_traces": [],
    }

    if validation_overlap:
        selection_status = "validation_inconsistent"
        reason = "validation_trace_is_both_positive_and_negative"
    elif training_negative_overlap:
        selection_status = "validation_training_conflict"
        reason = "validation_negative_contains_training_trace"
    elif not context.get("detected"):
        selection_status = context["selection_status"]
        reason = context["reason"]
    else:
        direct_assignment = _direct_signal_assignment(
            context,
            validation_positive,
            validation_negative,
            selector_counter,
        )
        if direct_assignment["status"] != "direct_assignment_available":
            selection_status = direct_assignment["status"]
            reason = direct_assignment["reason"]
        else:
            dropped_bodies = set(direct_assignment["dropped_bodies"])
            selected_result, guard_counts = _build_selected_result(
                train,
                base_result,
                context,
                dropped_bodies,
            )
            attempted_compile_extra_total = max(
                0,
                int(selected_result.get("operation_counts", {}).get("total", base_total)) - base_total,
            )
            validation_result = _validation_summary(
                selected_result,
                validation_positive,
                validation_negative,
                validation_counter,
            )
            if not validation_result["validates_all"]:
                selected_result = base_result
                selection_status = "selected_net_fails_validation"
                reason = "direct_assignment_does_not_satisfy_validation_probes"
            else:
                selection_status = "selected"
                reason = "direct_body_signals_identify_assignment"
                selected_dropped_bodies = _body_rows(sorted(dropped_bodies))
                selected_alternative = (
                    "drop_none"
                    if not dropped_bodies
                    else "drop_" + "__".join(
                        _body_text(body).replace(" ", "_")
                        for body in sorted(dropped_bodies)
                    )
                )
                policy = exhaustive_selector._policy_from_drop_set(  # pylint: disable=protected-access
                    context,
                    dropped_bodies,
                )
                selected_kept_bodies = policy["kept_bodies"]

    selector_counts = selector_counter.to_dict()
    validation_counts = validation_counter.to_dict()
    candidate_total = int(selected_result.get("operation_counts", {}).get("total", base_total))
    compile_extra_total = max(attempted_compile_extra_total, candidate_total - base_total)
    selected_total_with_selector = base_total + compile_extra_total + selector_counts["total"]
    total_with_validation = selected_total_with_selector + validation_counts["total"]
    operation_counts = dict(selected_result.get("operation_counts", {}))
    operation_counts["base_discovery_total"] = base_total
    operation_counts["direct_signal_selector_total"] = selector_counts["total"]
    operation_counts["guarded_compile_extra_total"] = compile_extra_total
    operation_counts["validation_replay_proxy_total"] = validation_counts["total"]
    operation_counts["evaluated_alternative_count"] = 1 if selected_alternative else 0
    operation_counts["avoided_exhaustive_alternative_count"] = (
        2 ** len(context.get("rare_bodies", [])) if context.get("detected") else 0
    )
    operation_counts["total_with_selector"] = selected_total_with_selector
    operation_counts["total_with_selector_and_validation_proxy"] = total_with_validation

    evidence_payload = {
        "validation_positive_count": len(validation_positive),
        "validation_negative_count": len(validation_negative),
        "selected_alternative": selected_alternative,
        "selected_dropped_bodies": selected_dropped_bodies,
        "selected_kept_bodies": selected_kept_bodies,
        "selection_status": selection_status,
        "reason": reason,
        "validation_overlap": _sorted_traces(validation_overlap),
        "training_negative_overlap": _sorted_traces(training_negative_overlap),
        "selector_operation_counts": selector_counts,
        "validation_replay_proxy_counts": validation_counts,
        "guarded_compile_operation_counts": guard_counts,
        "configuration": {
            "source_candidate": "ALG-0025",
            "min_dominant_count": min_dominant_count,
            "min_dominant_share": f"{min_dominant_share_numerator}/{min_dominant_share_denominator}",
            "rare_body_count": rare_body_count,
            "max_rare_bodies": max_rare_bodies,
            "selector_rule": "direct singleton rare-body validation signal",
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
        "direct_signal_assignment": {
            "status": direct_assignment["status"],
            "reason": direct_assignment["reason"],
            "signals": direct_assignment["signals"],
            "unresolved_bodies": _body_rows(direct_assignment["unresolved_bodies"]),
            "conflicting_bodies": _body_rows(direct_assignment["conflicting_bodies"]),
            "ambiguous_negative_traces": direct_assignment["ambiguous_negative_traces"],
            "malformed_validation_traces": direct_assignment["malformed_validation_traces"],
        },
        "validation_selected_net": validation_result,
        "alternative_count": 1 if selected_alternative else 0,
        "avoided_exhaustive_alternative_count": operation_counts[
            "avoided_exhaustive_alternative_count"
        ],
    }
    return _retag_result(selected_result, evidence_payload, operation_counts)


def discover(log: TraceLog) -> Dict[str, Any]:
    return select(log, [], [])
