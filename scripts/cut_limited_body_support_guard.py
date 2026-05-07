"""ALG-0028: Cut-limited body-support guard for length-bounded rework loops.

The guard starts from the ALG-0025 length-bounded loop evidence and applies a
conservative precision prior: only singleton-supported loop bodies are filtered,
and only when the remaining evidence has a clearly dominant body. This is a
noise-handling hypothesis, not a completeness claim.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import cut_limited_length_bounded_loop
import cut_limited_process_tree as process_tree_miner
from limited_ops import OpCounter, arithmetic, comparison, construct, scan_event, set_lookup
from pn_ir import PMIR, pair_key


TraceLog = List[List[str]]
Body = Tuple[str, ...]


MIN_DOMINANT_COUNT = 3
MIN_DOMINANT_SHARE_NUMERATOR = 3
MIN_DOMINANT_SHARE_DENOMINATOR = 4
RARE_BODY_COUNT = 1


def _combine_counts(*operation_counts: Dict[str, int]) -> Dict[str, int]:
    combined: Counter[str] = Counter()
    for counts in operation_counts:
        for key, value in counts.items():
            if key == "total":
                continue
            combined[key] += int(value)
    combined["total"] = sum(combined.values())
    return dict(combined)


def _support_to_bodies(body_support: Dict[str, int]) -> Dict[Body, int]:
    bodies: Dict[Body, int] = {}
    for body_text, count in body_support.items():
        body = tuple(part for part in body_text.split(" ") if part)
        if body:
            bodies[body] = int(count)
    return bodies


def _body_key(body: Sequence[str]) -> str:
    return " ".join(body)


def _body_from_trace(
    trace: Sequence[str],
    prefix: Sequence[str],
    anchor: str,
    suffix: Sequence[str],
    counter: OpCounter,
) -> Optional[Body]:
    scan_event(counter, len(trace))
    comparison(counter, 5)
    if trace == list(prefix) + [anchor] + list(suffix):
        return ()
    if len(trace) < len(prefix) + len(suffix) + 3:
        return None
    if trace[: len(prefix)] != list(prefix):
        return None
    if trace[len(prefix)] != anchor:
        return None
    if suffix and trace[-len(suffix) :] != list(suffix):
        return None
    repeat_index = len(trace) - len(suffix) - 1
    comparison(counter)
    if repeat_index <= len(prefix) or trace[repeat_index] != anchor:
        return None
    return tuple(trace[len(prefix) + 1 : repeat_index])


def _partition_log_by_body(
    log: TraceLog,
    prefix: Sequence[str],
    anchor: str,
    suffix: Sequence[str],
    dropped_bodies: Set[Body],
    counter: OpCounter,
) -> Tuple[TraceLog, TraceLog]:
    filtered: TraceLog = []
    dropped: TraceLog = []
    for trace in log:
        body = _body_from_trace(trace, prefix, anchor, suffix, counter)
        comparison(counter)
        if body is not None and body in dropped_bodies:
            set_lookup(counter)
            dropped.append(list(trace))
            construct(counter)
        else:
            filtered.append(list(trace))
            construct(counter)
    return filtered, dropped


def _support_policy(
    body_counts: Dict[Body, int],
    counter: OpCounter,
    min_dominant_count: int = MIN_DOMINANT_COUNT,
    min_dominant_share_numerator: int = MIN_DOMINANT_SHARE_NUMERATOR,
    min_dominant_share_denominator: int = MIN_DOMINANT_SHARE_DENOMINATOR,
    rare_body_count: int = RARE_BODY_COUNT,
) -> Dict[str, Any]:
    policy_config = {
        "min_dominant_count": min_dominant_count,
        "min_dominant_share": f"{min_dominant_share_numerator}/{min_dominant_share_denominator}",
        "rare_body_count": rare_body_count,
    }
    if min_dominant_share_denominator <= 0:
        raise ValueError("min_dominant_share_denominator must be positive")
    if not body_counts:
        return {"applied": False, "reason": "no_body_support", **policy_config}

    total_body_observations = sum(body_counts.values())
    dominant_body, dominant_count = max(body_counts.items(), key=lambda item: (item[1], item[0]))
    comparison(counter, max(1, len(body_counts) - 1))
    arithmetic(counter, 2)
    dominant_share_ok = (
        dominant_count * min_dominant_share_denominator
        >= total_body_observations * min_dominant_share_numerator
    )
    comparison(counter, 2)
    if dominant_count < min_dominant_count:
        return {
            "applied": False,
            "reason": "dominant_count_below_threshold",
            **policy_config,
            "dominant_body": list(dominant_body),
            "dominant_count": dominant_count,
            "total_body_observations": total_body_observations,
        }
    if not dominant_share_ok:
        return {
            "applied": False,
            "reason": "dominant_share_below_threshold",
            **policy_config,
            "dominant_body": list(dominant_body),
            "dominant_count": dominant_count,
            "total_body_observations": total_body_observations,
        }

    dropped = []
    kept = []
    for body, count in sorted(body_counts.items()):
        comparison(counter)
        if body != dominant_body and count == rare_body_count:
            dropped.append(body)
            construct(counter)
        else:
            kept.append(body)
            construct(counter)

    comparison(counter, 2)
    if not dropped:
        return {
            "applied": False,
            "reason": "no_singleton_rare_body",
            **policy_config,
            "dominant_body": list(dominant_body),
            "dominant_count": dominant_count,
            "total_body_observations": total_body_observations,
        }
    if not kept:
        return {
            "applied": False,
            "reason": "filter_would_remove_all_bodies",
            **policy_config,
            "dominant_body": list(dominant_body),
            "dominant_count": dominant_count,
            "total_body_observations": total_body_observations,
        }

    return {
        "applied": True,
        "reason": "singleton_rare_body_under_dominant_support_prior",
        **policy_config,
        "dominant_body": list(dominant_body),
        "dominant_count": dominant_count,
        "total_body_observations": total_body_observations,
        "kept_bodies": [list(body) for body in kept],
        "filtered_bodies": [list(body) for body in dropped],
        "rare_body_ambiguous": True,
    }


def _build_guarded_result(
    base_result: Dict[str, Any],
    original_trace_count: int,
    filtered_log: TraceLog,
    dropped_traces: TraceLog,
    policy: Dict[str, Any],
    guard_counts: Dict[str, int],
) -> Dict[str, Any]:
    base_evidence = base_result.get("pmir", {}).get("evidence", {})
    base_tree = base_evidence.get("process_tree", {})
    counter = OpCounter()
    activities, starts, ends, dfg = process_tree_miner.summarize_log(filtered_log, counter)
    rel = process_tree_miner.classify_relations(activities, dfg, counter)

    kept_bodies = policy["kept_bodies"]
    body_support = base_tree.get("body_support", {})
    kept_support = {
        _body_key(body): int(body_support.get(_body_key(body), 0))
        for body in kept_bodies
    }
    process_tree = deepcopy(base_tree)
    process_tree.update(
        {
            "type": "body_support_guard_rework_loop",
            "compiled_from": "multi_body_rework_loop",
            "bodies": kept_bodies,
            "body_support": kept_support,
            "filtered_bodies": policy["filtered_bodies"],
            "support_policy": (
                "singleton-rare-body-filter-after-"
                f"{policy['min_dominant_count']}-count-"
                f"{policy['min_dominant_share']}-dominance"
            ),
            "rare_body_ambiguous": True,
        }
    )
    net = process_tree_miner._compile_multi_body_rework_loop(  # pylint: disable=protected-access
        activities,
        process_tree["prefix"],
        process_tree["anchor"],
        process_tree["bodies"],
        process_tree["suffix"],
        counter,
    )
    evidence = {
        "configuration": {
            "source_candidate": "ALG-0025",
            "min_dominant_count": policy["min_dominant_count"],
            "min_dominant_share": policy["min_dominant_share"],
            "rare_body_count": policy["rare_body_count"],
        },
        "selected_cut": "body_support_guard_rework_loop",
        "process_tree": process_tree,
        "support_guard": {
            **policy,
            "original_trace_count": original_trace_count,
            "filtered_trace_count": len(filtered_log),
            "dropped_trace_count": len(dropped_traces),
            "dropped_traces": dropped_traces,
        },
        "source_evidence": {
            "selected_cut": base_evidence.get("selected_cut"),
            "process_tree": base_tree,
            "operation_counts": base_result.get("operation_counts", {}),
        },
    }
    compile_counts = counter.to_dict()
    operation_counts = _combine_counts(base_result.get("operation_counts", {}), guard_counts, compile_counts)
    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence=evidence,
        operation_counts=operation_counts,
    )
    return {
        "candidate_id": "ALG-0028",
        "name": "Cut-Limited Body-Support Guard Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": operation_counts,
    }


def _retag_base_result(
    base_result: Dict[str, Any],
    policy: Dict[str, Any],
    guard_counts: Dict[str, int],
    original_trace_count: int,
) -> Dict[str, Any]:
    result = deepcopy(base_result)
    result["candidate_id"] = "ALG-0028"
    result["name"] = "Cut-Limited Body-Support Guard Miner"
    evidence = result.setdefault("pmir", {}).setdefault("evidence", {})
    evidence["support_guard"] = {
        **policy,
        "original_trace_count": original_trace_count,
        "filtered_trace_count": original_trace_count,
        "dropped_trace_count": 0,
        "dropped_traces": [],
    }
    operation_counts = _combine_counts(base_result.get("operation_counts", {}), guard_counts)
    result["operation_counts"] = operation_counts
    result["pmir"]["operation_counts"] = operation_counts
    return result


def discover(log: TraceLog) -> Dict[str, object]:
    return discover_with_policy(log)


def discover_with_policy(
    log: TraceLog,
    min_dominant_count: int = MIN_DOMINANT_COUNT,
    min_dominant_share_numerator: int = MIN_DOMINANT_SHARE_NUMERATOR,
    min_dominant_share_denominator: int = MIN_DOMINANT_SHARE_DENOMINATOR,
    rare_body_count: int = RARE_BODY_COUNT,
) -> Dict[str, object]:
    base_result = cut_limited_length_bounded_loop.discover(log)
    guard_counter = OpCounter()
    evidence = base_result.get("pmir", {}).get("evidence", {})
    process_tree = evidence.get("process_tree", {})
    comparison(guard_counter)
    if evidence.get("selected_cut") != "multi_body_rework_loop" or not isinstance(process_tree, dict):
        policy = {"applied": False, "reason": "source_not_multi_body_rework_loop"}
        return _retag_base_result(base_result, policy, guard_counter.to_dict(), len(log))

    body_counts = _support_to_bodies(process_tree.get("body_support", {}))
    policy = _support_policy(
        body_counts,
        guard_counter,
        min_dominant_count=min_dominant_count,
        min_dominant_share_numerator=min_dominant_share_numerator,
        min_dominant_share_denominator=min_dominant_share_denominator,
        rare_body_count=rare_body_count,
    )
    if not policy.get("applied"):
        return _retag_base_result(base_result, policy, guard_counter.to_dict(), len(log))

    prefix = process_tree["prefix"]
    anchor = process_tree["anchor"]
    suffix = process_tree["suffix"]
    dropped_bodies = {tuple(body) for body in policy["filtered_bodies"]}
    filtered_log, dropped_traces = _partition_log_by_body(
        log,
        prefix,
        anchor,
        suffix,
        dropped_bodies,
        guard_counter,
    )
    return _build_guarded_result(
        base_result,
        len(log),
        filtered_log,
        dropped_traces,
        policy,
        guard_counter.to_dict(),
    )
