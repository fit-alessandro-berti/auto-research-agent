"""ALG-0001: Alpha-Lite Relations baseline.

This is a deliberately small Alpha-style prototype for smoke testing. It is not
presented as a complete Alpha Miner implementation. It uses a direct-follows
scan, classifies causal/parallel/unrelated relations, searches small maximal
(place preset, place postset) pairs, and compiles them to a Petri net.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple

from limited_ops import (
    OpCounter,
    comparison,
    construct,
    dict_increment,
    relation_classification,
    scan_event,
    set_insert,
    set_lookup,
)
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


def _subsets(items: Sequence[str], max_size: int) -> Iterable[Tuple[str, ...]]:
    for size in range(1, min(max_size, len(items)) + 1):
        yield from combinations(items, size)


def summarize_log(log: List[List[str]], counter: OpCounter) -> Tuple[List[str], Counter, Counter, Counter]:
    activities = set()
    starts: Counter = Counter()
    ends: Counter = Counter()
    dfg: Counter = Counter()

    for trace in log:
        if not trace:
            continue
        dict_increment(counter)
        starts[trace[0]] += 1
        dict_increment(counter)
        ends[trace[-1]] += 1
        for event in trace:
            scan_event(counter)
            before = len(activities)
            activities.add(event)
            if len(activities) != before:
                set_insert(counter)
        for a, b in zip(trace, trace[1:]):
            scan_event(counter)
            dfg[(a, b)] += 1
            dict_increment(counter)

    return sorted(activities), starts, ends, dfg


def classify_relations(activities: List[str], dfg: Counter, counter: OpCounter) -> Dict[Tuple[str, str], str]:
    rel: Dict[Tuple[str, str], str] = {}
    for a in activities:
        for b in activities:
            set_lookup(counter, 2)
            ab = dfg.get((a, b), 0)
            ba = dfg.get((b, a), 0)
            comparison(counter, 3)
            if a == b and ab > 0:
                rel[(a, b)] = "self_loop"
            elif ab > 0 and ba > 0:
                rel[(a, b)] = "parallel"
            elif ab > 0 and ba == 0:
                rel[(a, b)] = "causal"
            elif ab == 0 and ba == 0:
                rel[(a, b)] = "unrelated"
            else:
                rel[(a, b)] = "reverse_causal"
            relation_classification(counter)
    return rel


def _all_causal(pre: Tuple[str, ...], post: Tuple[str, ...], rel: Dict[Tuple[str, str], str], counter: OpCounter) -> bool:
    for a in pre:
        for b in post:
            set_lookup(counter)
            comparison(counter)
            if rel.get((a, b)) != "causal":
                return False
    return True


def _mutually_unrelated(group: Tuple[str, ...], rel: Dict[Tuple[str, str], str], counter: OpCounter) -> bool:
    for a, b in combinations(group, 2):
        set_lookup(counter, 2)
        comparison(counter, 2)
        if rel.get((a, b)) != "unrelated" or rel.get((b, a)) != "unrelated":
            return False
    return True


def discover(log: List[List[str]], max_pair_set_size: int = 2) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)

    raw_pairs: List[Tuple[Tuple[str, ...], Tuple[str, ...]]] = []
    for pre in _subsets(activities, max_pair_set_size):
        for post in _subsets(activities, max_pair_set_size):
            comparison(counter)
            if not _all_causal(pre, post, rel, counter):
                continue
            if not _mutually_unrelated(pre, rel, counter):
                continue
            if not _mutually_unrelated(post, rel, counter):
                continue
            raw_pairs.append((pre, post))
            construct(counter)

    maximal_pairs: List[Tuple[Tuple[str, ...], Tuple[str, ...]]] = []
    for pre, post in raw_pairs:
        is_subsumed = False
        for pre2, post2 in raw_pairs:
            comparison(counter)
            if (pre, post) == (pre2, post2):
                continue
            if set(pre).issubset(pre2) and set(post).issubset(post2):
                set_lookup(counter, len(pre) + len(post))
                is_subsumed = True
                break
        if not is_subsumed:
            maximal_pairs.append((pre, post))

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

    for pre, post in maximal_pairs:
        p = place_name("alpha", pre, post)
        net.add_place(p)
        construct(counter)
        for a in pre:
            net.add_arc(transition_name(a), p)
            construct(counter)
        for b in post:
            net.add_arc(p, transition_name(b))
            construct(counter)

    pmir = PMIR(
        activities=activities,
        start_counts=dict(starts),
        end_counts=dict(ends),
        dfg_counts={pair_key(a, b): c for (a, b), c in dfg.items()},
        relations={pair_key(a, b): r for (a, b), r in rel.items() if r != "unrelated"},
        evidence={"maximal_pairs": [[list(pre), list(post)] for pre, post in maximal_pairs]},
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0001",
        "name": "Alpha-Lite Relations",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
