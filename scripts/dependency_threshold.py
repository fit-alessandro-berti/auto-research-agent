"""ALG-0002: Frequency-Threshold Dependency Graph baseline.

This heuristic-miner-style prototype keeps only direct-follows edges whose
frequency and directional dependency score exceed fixed thresholds. It then
compiles the filtered dependency graph to a small Petri net using local
XOR-grouping where branch activities are never observed to follow each other.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Set, Tuple

from alpha_lite import summarize_log
from limited_ops import OpCounter, arithmetic, comparison, construct, dict_increment, relation_classification, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


Edge = Tuple[str, str]


def _dependency_score(a: str, b: str, dfg: Dict[Edge, int], counter: OpCounter) -> float:
    set_lookup(counter, 2)
    ab = dfg.get((a, b), 0)
    ba = dfg.get((b, a), 0)
    arithmetic(counter, 4)
    relation_classification(counter)
    return (ab - ba) / (ab + ba + 1)


def _are_xor_alternatives(items: List[str], dfg: Dict[Edge, int], counter: OpCounter) -> bool:
    for a, b in combinations(items, 2):
        set_lookup(counter, 2)
        comparison(counter, 2)
        if dfg.get((a, b), 0) > 0 or dfg.get((b, a), 0) > 0:
            return False
    return True


def _add_place(net: PetriNet, prefix: str, pre: List[str], post: List[str], counter: OpCounter) -> None:
    place = place_name(prefix, pre, post)
    net.add_place(place)
    construct(counter)
    for activity in pre:
        net.add_arc(transition_name(activity), place)
        construct(counter)
    for activity in post:
        net.add_arc(place, transition_name(activity))
        construct(counter)


def _compile_dependency_graph(
    activities: List[str],
    starts: Dict[str, int],
    ends: Dict[str, int],
    accepted_edges: Set[Edge],
    dfg: Dict[Edge, int],
    counter: OpCounter,
) -> Tuple[PetriNet, List[Tuple[List[str], List[str]]]]:
    outgoing: Dict[str, List[str]] = defaultdict(list)
    incoming: Dict[str, List[str]] = defaultdict(list)
    for a, b in sorted(accepted_edges):
        outgoing[a].append(b)
        incoming[b].append(a)
        dict_increment(counter, 2)

    grouped_places: List[Tuple[List[str], List[str]]] = []
    covered_edges: Set[Edge] = set()

    for a, posts in sorted(outgoing.items()):
        posts = sorted(set(posts))
        set_insert(counter, len(posts))
        if len(posts) > 1 and _are_xor_alternatives(posts, dfg, counter):
            grouped_places.append(([a], posts))
            for b in posts:
                covered_edges.add((a, b))
                set_insert(counter)

    for b, pres in sorted(incoming.items()):
        pres = sorted(set(pres))
        set_insert(counter, len(pres))
        if len(pres) > 1 and _are_xor_alternatives(pres, dfg, counter):
            grouped_places.append((pres, [b]))
            for a in pres:
                covered_edges.add((a, b))
                set_insert(counter)

    net = PetriNet()
    net.add_place("p_start")
    net.add_place("p_end")
    net.initial_marking = {"p_start": 1}
    net.final_marking = {"p_end": 1}
    construct(counter, 2)

    for activity in activities:
        net.add_transition(transition_name(activity))
        construct(counter)
    for activity in starts:
        net.add_arc("p_start", transition_name(activity))
        construct(counter)
    for activity in ends:
        net.add_arc(transition_name(activity), "p_end")
        construct(counter)

    emitted = set()
    for pre, post in grouped_places:
        key = (tuple(pre), tuple(post))
        if key not in emitted:
            emitted.add(key)
            _add_place(net, "depgrp", pre, post, counter)

    for a, b in sorted(accepted_edges):
        if (a, b) in covered_edges:
            continue
        key = ((a,), (b,))
        if key not in emitted:
            emitted.add(key)
            _add_place(net, "depedge", [a], [b], counter)

    return net, grouped_places


def discover(log: List[List[str]], min_count: int = 2, dependency_threshold: float = 0.5) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)

    accepted_edges: Set[Edge] = set()
    scores: Dict[str, float] = {}
    for a in activities:
        for b in activities:
            comparison(counter)
            if a == b:
                continue
            score = _dependency_score(a, b, dfg, counter)
            set_lookup(counter)
            count = dfg.get((a, b), 0)
            comparison(counter, 2)
            if count >= min_count and score >= dependency_threshold:
                accepted_edges.add((a, b))
                scores[pair_key(a, b)] = round(score, 6)
                set_insert(counter)
                dict_increment(counter)

    net, grouped_places = _compile_dependency_graph(activities, starts, ends, accepted_edges, dfg, counter)
    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): "dependency" for (a, b) in sorted(accepted_edges)},
        evidence={
            "min_count": min_count,
            "dependency_threshold": dependency_threshold,
            "dependency_scores": scores,
            "grouped_places": [[pre, post] for pre, post in grouped_places],
        },
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0002",
        "name": "Frequency-Threshold Dependency Graph",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
