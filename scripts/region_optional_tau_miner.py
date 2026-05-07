"""ALG-0011: Region Optional-Tau Repair Miner.

This refinement keeps ALG-0004's bounded visible-place search, then adds a
small, explicitly counted silent-skip repair for non-overlapping optional
singletons certified by a selected shortcut place.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Sequence, Tuple

from alpha_lite import classify_relations, summarize_log
from bounded_place_region_miner import (
    PlaceCandidate,
    _compile_net,
    _enumerate_valid_candidates,
    _select_nonblocking_candidates,
)
from limited_ops import OpCounter, comparison, construct, dict_increment, relation_classification, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


Edge = Tuple[str, str]
OptionalPattern = Tuple[str, str, str]
TraceLog = List[List[str]]


def _safe_name(*parts: str) -> str:
    return "_".join(parts).replace(" ", "_").replace("/", "_")


def _tau_name(prefix: str, *parts: str) -> str:
    return f"tau_region_{prefix}_{_safe_name(*parts)}"


def _build_causal_maps(
    rel: Dict[Edge, str],
    counter: OpCounter,
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    outgoing: Dict[str, List[str]] = defaultdict(list)
    incoming: Dict[str, List[str]] = defaultdict(list)
    for (a, b), relation in sorted(rel.items()):
        comparison(counter)
        if relation == "causal":
            outgoing[a].append(b)
            incoming[b].append(a)
            dict_increment(counter, 2)
    return outgoing, incoming


def _detect_nonoverlap_optional_patterns(
    activities: Sequence[str],
    starts: Counter,
    ends: Counter,
    dfg: Counter,
    rel: Dict[Edge, str],
    selected: List[PlaceCandidate],
    counter: OpCounter,
) -> Tuple[List[OptionalPattern], Dict[str, int]]:
    outgoing, incoming = _build_causal_maps(rel, counter)
    selected_shortcuts = {(pre[0], post[0]) for pre, post in selected if len(pre) == 1 and len(post) == 1}
    stats = {
        "optional_candidates": 0,
        "rejected_start_or_end_middle": 0,
        "rejected_non_single_context": 0,
        "rejected_no_shortcut_place": 0,
        "rejected_no_direct_shortcut": 0,
    }
    patterns: List[OptionalPattern] = []

    for a in activities:
        for b in sorted(outgoing.get(a, [])):
            for c in sorted(outgoing.get(b, [])):
                stats["optional_candidates"] += 1
                relation_classification(counter)
                comparison(counter, 4)
                if len({a, b, c}) != 3:
                    continue
                if starts.get(b, 0) or ends.get(b, 0):
                    stats["rejected_start_or_end_middle"] += 1
                    continue
                set_lookup(counter, 2)
                if incoming.get(b, []) != [a] or outgoing.get(b, []) != [c]:
                    stats["rejected_non_single_context"] += 1
                    continue
                set_lookup(counter)
                if (a, c) not in selected_shortcuts:
                    stats["rejected_no_shortcut_place"] += 1
                    continue
                set_lookup(counter)
                comparison(counter, 2)
                if dfg.get((a, c), 0) <= 0 or rel.get((a, c)) != "causal":
                    stats["rejected_no_direct_shortcut"] += 1
                    continue
                patterns.append((a, b, c))
                construct(counter)

    return sorted(set(patterns)), stats


def _add_optional_skip(net: PetriNet, a: str, b: str, c: str, counter: OpCounter) -> None:
    split = place_name("regoptsplit", [a], [b, c])
    join = place_name("regoptjoin", [a, b], [c])
    tau = _tau_name("skip", a, c, "over", b)
    net.add_place(split)
    net.add_place(join)
    net.add_transition(tau)
    construct(counter, 3)
    net.add_arc(transition_name(a), split)
    net.add_arc(split, transition_name(b))
    net.add_arc(split, tau)
    net.add_arc(transition_name(b), join)
    net.add_arc(tau, join)
    net.add_arc(join, transition_name(c))
    construct(counter, 6)


def _compile_repaired_net(
    activities: Sequence[str],
    starts: Counter,
    ends: Counter,
    selected: List[PlaceCandidate],
    optional_patterns: List[OptionalPattern],
    counter: OpCounter,
) -> PetriNet:
    net = _compile_net(activities, starts, ends, selected, counter)
    for a, b, c in optional_patterns:
        _add_optional_skip(net, a, b, c, counter)
    return net


def discover(log: TraceLog, max_set_size: int = 2, enable_optional_repair: bool = True) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    valid, stats = _enumerate_valid_candidates(activities, dfg, log, max_set_size, counter)
    selected, rejected_positive_replay = _select_nonblocking_candidates(valid, log, counter)
    if enable_optional_repair:
        optional_patterns, optional_stats = _detect_nonoverlap_optional_patterns(
            activities,
            starts,
            ends,
            dfg,
            rel,
            selected,
            counter,
        )
    else:
        optional_patterns = []
        optional_stats = {
            "optional_candidates": 0,
            "rejected_start_or_end_middle": 0,
            "rejected_non_single_context": 0,
            "rejected_no_shortcut_place": 0,
            "rejected_no_direct_shortcut": 0,
        }
    net = _compile_repaired_net(activities, starts, ends, selected, optional_patterns, counter)

    evidence = {
        "configuration": {
            "max_set_size": max_set_size,
            "enable_optional_repair": enable_optional_repair,
            "optional_pattern": "nonoverlap_singleton_with_selected_shortcut",
        },
        "candidate_stats": {
            **stats,
            "valid_local_candidates": len(valid),
            "selected_candidates": len(selected),
            "rejected_positive_replay": rejected_positive_replay,
        },
        "optional_stats": {
            **optional_stats,
            "accepted_optional_patterns": len(optional_patterns),
        },
        "valid_local_candidates": [[list(pre), list(post)] for pre, post in valid],
        "selected_candidates": [[list(pre), list(post)] for pre, post in selected],
        "optional_patterns": [[a, b, c] for a, b, c in optional_patterns],
    }
    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence=evidence,
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0011",
        "name": "Region Optional-Tau Repair Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
