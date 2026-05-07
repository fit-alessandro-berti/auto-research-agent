"""ALG-0009: PMIR Guarded Split-Join Compiler.

This variant keeps the low-operation local PMIR strategy from ALG-0006 but
separates grouped split/join detection from edge-place emission. Edges covered
by XOR or optional-skip guards are not emitted again as individual places.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, comparison, construct, dict_increment, relation_classification, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


Edge = Tuple[str, str]
Group = Tuple[Tuple[str, ...], Tuple[str, ...]]
OptionalPattern = Tuple[str, str, str]


def _safe_name(*parts: str) -> str:
    return "_".join(parts).replace(" ", "_").replace("/", "_")


def _tau_name(prefix: str, *parts: str) -> str:
    return f"tau_{prefix}_{_safe_name(*parts)}"


def _mutually_unrelated(items: List[str], rel: Dict[Edge, str], counter: OpCounter) -> bool:
    for a, b in combinations(items, 2):
        set_lookup(counter, 2)
        comparison(counter, 2)
        if rel.get((a, b)) != "unrelated" or rel.get((b, a)) != "unrelated":
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


def _add_optional_skip(net: PetriNet, a: str, b: str, c: str, counter: OpCounter) -> None:
    split = place_name("optsplit", [a], [b, c])
    join = place_name("optjoin", [a, b], [c])
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


def _build_causal_maps(rel: Dict[Edge, str], counter: OpCounter) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    outgoing: Dict[str, List[str]] = defaultdict(list)
    incoming: Dict[str, List[str]] = defaultdict(list)
    for (a, b), relation in sorted(rel.items()):
        comparison(counter)
        if relation == "causal":
            outgoing[a].append(b)
            incoming[b].append(a)
            dict_increment(counter, 2)
    return outgoing, incoming


def _detect_optional_patterns(outgoing: Dict[str, List[str]], rel: Dict[Edge, str], counter: OpCounter) -> List[OptionalPattern]:
    patterns: List[OptionalPattern] = []
    for a, posts in sorted(outgoing.items()):
        posts = sorted(set(posts))
        set_insert(counter, len(posts))
        for b in posts:
            for c in posts:
                comparison(counter, 2)
                if b == c:
                    continue
                set_lookup(counter)
                relation_classification(counter)
                if rel.get((b, c)) == "causal":
                    patterns.append((a, b, c))
                    construct(counter)
    return sorted(set(patterns))


def _detect_xor_groups(
    outgoing: Dict[str, List[str]],
    incoming: Dict[str, List[str]],
    rel: Dict[Edge, str],
    covered_edges: Set[Edge],
    counter: OpCounter,
) -> Tuple[List[Group], List[Group]]:
    split_groups: List[Group] = []
    join_groups: List[Group] = []

    for a, posts in sorted(outgoing.items()):
        posts = sorted({b for b in posts if (a, b) not in covered_edges})
        set_insert(counter, len(posts))
        if len(posts) > 1 and _mutually_unrelated(posts, rel, counter):
            group = ((a,), tuple(posts))
            split_groups.append(group)
            construct(counter)
            for b in posts:
                covered_edges.add((a, b))
                set_insert(counter)

    for b, pres in sorted(incoming.items()):
        pres = sorted({a for a in pres if (a, b) not in covered_edges})
        set_insert(counter, len(pres))
        if len(pres) > 1 and _mutually_unrelated(pres, rel, counter):
            group = (tuple(pres), (b,))
            join_groups.append(group)
            construct(counter)
            for a in pres:
                covered_edges.add((a, b))
                set_insert(counter)

    return split_groups, join_groups


def discover(log: List[List[str]], enable_optional: bool = True, enable_xor: bool = True) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    outgoing, incoming = _build_causal_maps(rel, counter)

    optional_patterns = _detect_optional_patterns(outgoing, rel, counter) if enable_optional else []
    covered_edges: Set[Edge] = set()
    for a, b, c in optional_patterns:
        covered_edges.update({(a, b), (a, c), (b, c)})
        set_insert(counter, 3)

    if enable_xor:
        split_groups, join_groups = _detect_xor_groups(outgoing, incoming, rel, covered_edges, counter)
    else:
        split_groups, join_groups = [], []

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

    for a, b, c in optional_patterns:
        _add_optional_skip(net, a, b, c, counter)

    emitted_groups: Set[Group] = set()
    for pre, post in split_groups + join_groups:
        if (pre, post) not in emitted_groups:
            emitted_groups.add((pre, post))
            _add_place(net, "guard", list(pre), list(post), counter)

    emitted_edges: Set[Edge] = set()
    for a, posts in sorted(outgoing.items()):
        for b in sorted(set(posts)):
            edge = (a, b)
            if edge in covered_edges or edge in emitted_edges:
                continue
            emitted_edges.add(edge)
            _add_place(net, "edge", [a], [b], counter)

    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence={
            "configuration": {
                "enable_optional": enable_optional,
                "enable_xor": enable_xor,
            },
            "optional_patterns": [[a, b, c] for a, b, c in optional_patterns],
            "split_groups": [[list(pre), list(post)] for pre, post in split_groups],
            "join_groups": [[list(pre), list(post)] for pre, post in join_groups],
            "edge_places": [[a, b] for a, b in sorted(emitted_edges)],
            "covered_edges": [list(edge) for edge in sorted(covered_edges)],
        },
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0009",
        "name": "PMIR Guarded Split-Join Compiler",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
