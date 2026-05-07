"""ALG-0006 prototype: PMIR Split-Join Compiler.

This novel starter candidate avoids the Alpha-style subset search. It scans the
log once, classifies pairwise relations, then creates local split/join places:

- one place for XOR-like alternatives whose branches are mutually unrelated;
- separate places for parallel branches;
- individual places when no grouping is justified.

The goal is not to be complete, but to create a low-operation PMIR-to-Petri-net
candidate that can be refined and challenged by counterexamples.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Dict, List, Tuple

from limited_ops import OpCounter, comparison, construct, dict_increment, relation_classification, scan_event, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name
from alpha_lite import summarize_log, classify_relations


def _mutually_unrelated(items: List[str], rel: Dict[Tuple[str, str], str], counter: OpCounter) -> bool:
    for a, b in combinations(items, 2):
        set_lookup(counter, 2)
        comparison(counter, 2)
        if rel.get((a, b)) != "unrelated" or rel.get((b, a)) != "unrelated":
            return False
    return True


def _add_place(net: PetriNet, prefix: str, pre: List[str], post: List[str], counter: OpCounter) -> None:
    p = place_name(prefix, pre, post)
    net.add_place(p)
    construct(counter)
    for a in pre:
        net.add_arc(transition_name(a), p)
        construct(counter)
    for b in post:
        net.add_arc(p, transition_name(b))
        construct(counter)


def discover(log: List[List[str]]) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)

    outgoing = defaultdict(list)
    incoming = defaultdict(list)
    for (a, b), r in rel.items():
        comparison(counter)
        if r == "causal":
            outgoing[a].append(b)
            incoming[b].append(a)
            dict_increment(counter, 2)

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

    # Split grouping: a -> {b, c} when b and c are mutually unrelated (XOR-like).
    for a, posts in outgoing.items():
        posts = sorted(set(posts))
        set_insert(counter, len(posts))
        if len(posts) > 1 and _mutually_unrelated(posts, rel, counter):
            key = (tuple([a]), tuple(posts))
            emitted.add(key)
            _add_place(net, "splitxor", [a], posts, counter)
        else:
            for b in posts:
                key = (tuple([a]), tuple([b]))
                if key not in emitted:
                    emitted.add(key)
                    _add_place(net, "edge", [a], [b], counter)

    # Join grouping: {a, b} -> c when a and b are mutually unrelated (XOR-like).
    for b, pres in incoming.items():
        pres = sorted(set(pres))
        set_insert(counter, len(pres))
        if len(pres) > 1 and _mutually_unrelated(pres, rel, counter):
            # Remove individual edge places that would over-constrain an XOR join.
            key = (tuple(pres), tuple([b]))
            if key not in emitted:
                emitted.add(key)
                _add_place(net, "joinxor", pres, [b], counter)
        else:
            for a in pres:
                key = (tuple([a]), tuple([b]))
                if key not in emitted:
                    emitted.add(key)
                    _add_place(net, "edge", [a], [b], counter)

    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence={"emitted_place_patterns": [[list(pre), list(post)] for pre, post in sorted(emitted)]},
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0006",
        "name": "PMIR Split-Join Compiler Lite",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
