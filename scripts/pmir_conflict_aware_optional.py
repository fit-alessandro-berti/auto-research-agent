"""ALG-0010: PMIR Conflict-Aware Optional Chain Compiler.

This variant refines ALG-0009's optional handling. Instead of emitting every
local optional triple, it detects optional chains from transitive shortcuts and
rejects chains whose activity order is contradicted by observed traces.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, comparison, construct, dict_increment, relation_classification, scan_event, set_insert, set_lookup
from pmir_guarded_split_join import _detect_xor_groups, _add_place, _safe_name, _tau_name
from pn_ir import PMIR, PetriNet, pair_key, place_name, transition_name


Edge = Tuple[str, str]
Chain = Tuple[str, ...]
Group = Tuple[Tuple[str, ...], Tuple[str, ...]]


def _chain_place(a: str, b: str) -> str:
    return place_name("optchain", [a], [b])


def _build_causal_maps(rel: Dict[Edge, str], counter: OpCounter) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Set[Edge]]:
    outgoing: Dict[str, List[str]] = defaultdict(list)
    incoming: Dict[str, List[str]] = defaultdict(list)
    causal_edges: Set[Edge] = set()
    for (a, b), relation in sorted(rel.items()):
        comparison(counter)
        if relation == "causal":
            outgoing[a].append(b)
            incoming[b].append(a)
            causal_edges.add((a, b))
            dict_increment(counter, 2)
            set_insert(counter)
    return outgoing, incoming, causal_edges


def _eventual_before(log: List[List[str]], counter: OpCounter) -> Set[Edge]:
    before: Set[Edge] = set()
    for trace in log:
        for i, a in enumerate(trace):
            scan_event(counter)
            for b in trace[i + 1 :]:
                before.add((a, b))
                set_insert(counter)
    return before


def _has_alternate_path(start: str, end: str, edges: Set[Edge], removed: Edge, counter: OpCounter) -> bool:
    stack = [start]
    seen = {start}
    while stack:
        node = stack.pop()
        for a, b in sorted(edges):
            comparison(counter)
            if (a, b) == removed or a != node:
                continue
            comparison(counter)
            if b == end:
                return True
            if b not in seen:
                seen.add(b)
                stack.append(b)
                set_insert(counter)
    return False


def _transitive_reduction(edges: Set[Edge], counter: OpCounter) -> Set[Edge]:
    reduced: Set[Edge] = set()
    for edge in sorted(edges):
        if not _has_alternate_path(edge[0], edge[1], edges, edge, counter):
            reduced.add(edge)
            set_insert(counter)
        else:
            relation_classification(counter)
    return reduced


def _path_chains(reduced_edges: Set[Edge], counter: OpCounter) -> List[Chain]:
    outgoing: Dict[str, List[str]] = defaultdict(list)
    incoming: Dict[str, List[str]] = defaultdict(list)
    for a, b in sorted(reduced_edges):
        outgoing[a].append(b)
        incoming[b].append(a)
        dict_increment(counter, 2)

    starts = sorted({a for a, _ in reduced_edges if len(incoming[a]) != 1} | {a for a, _ in reduced_edges if len(outgoing[a]) != 1})
    chains: List[Chain] = []
    visited_edges: Set[Edge] = set()
    for start in starts:
        for nxt in sorted(outgoing[start]):
            edge = (start, nxt)
            if edge in visited_edges:
                continue
            path = [start, nxt]
            visited_edges.add(edge)
            set_insert(counter)
            current = nxt
            while len(outgoing[current]) == 1 and len(incoming[current]) == 1:
                following = sorted(outgoing[current])[0]
                next_edge = (current, following)
                if next_edge in visited_edges or following in path:
                    break
                path.append(following)
                visited_edges.add(next_edge)
                set_insert(counter)
                current = following
            if len(path) >= 3:
                chains.append(tuple(path))
                construct(counter)
    return chains


def _shortcut_edges(chain: Chain, causal_edges: Set[Edge], counter: OpCounter) -> Set[Edge]:
    shortcuts: Set[Edge] = set()
    for i, a in enumerate(chain):
        for j in range(i + 2, len(chain)):
            b = chain[j]
            set_lookup(counter)
            if (a, b) in causal_edges:
                shortcuts.add((a, b))
                set_insert(counter)
    return shortcuts


def _order_consistent(chain: Chain, before: Set[Edge], counter: OpCounter) -> bool:
    for i, earlier in enumerate(chain):
        for later in chain[i + 1 :]:
            set_lookup(counter)
            comparison(counter)
            if (later, earlier) in before:
                return False
    return True


def _select_optional_chains(
    chains: List[Chain],
    causal_edges: Set[Edge],
    before: Set[Edge],
    counter: OpCounter,
) -> Tuple[List[Chain], List[Dict[str, object]]]:
    selected: List[Chain] = []
    rejected: List[Dict[str, object]] = []
    used_nodes: Set[str] = set()
    for chain in sorted(chains, key=lambda c: (-len(c), c)):
        shortcuts = _shortcut_edges(chain, causal_edges, counter)
        if not shortcuts:
            rejected.append({"chain": list(chain), "reason": "no_shortcut_edges"})
            continue
        if not _order_consistent(chain, before, counter):
            rejected.append({"chain": list(chain), "reason": "observed_reverse_order"})
            continue
        overlap = sorted(set(chain) & used_nodes)
        set_lookup(counter, len(chain))
        if overlap:
            rejected.append({"chain": list(chain), "reason": "overlaps_selected_chain", "overlap": overlap})
            continue
        selected.append(chain)
        used_nodes.update(chain)
        set_insert(counter, len(chain))
        construct(counter)
    return selected, rejected


def _add_optional_chain(
    net: PetriNet,
    chain: Chain,
    causal_edges: Set[Edge],
    covered_edges: Set[Edge],
    counter: OpCounter,
) -> Dict[str, object]:
    chain_edges = []
    skip_edges = []
    for a, b in zip(chain, chain[1:]):
        place = _chain_place(a, b)
        net.add_place(place)
        net.add_arc(transition_name(a), place)
        net.add_arc(place, transition_name(b))
        covered_edges.add((a, b))
        chain_edges.append([a, b])
        construct(counter, 3)
        set_insert(counter)

    for i, a in enumerate(chain):
        for j in range(i + 2, len(chain)):
            b = chain[j]
            if (a, b) not in causal_edges:
                continue
            source_place = _chain_place(chain[i], chain[i + 1])
            target_place = _chain_place(chain[j - 1], chain[j])
            skipped = chain[i + 1 : j]
            tau = _tau_name("skipchain", a, b, "over", _safe_name(*skipped))
            net.add_transition(tau)
            net.add_arc(source_place, tau)
            net.add_arc(tau, target_place)
            covered_edges.add((a, b))
            skip_edges.append({"edge": [a, b], "skipped": list(skipped), "transition": tau})
            construct(counter, 3)
            set_insert(counter)

    return {"chain": list(chain), "chain_edges": chain_edges, "skip_edges": skip_edges}


def discover(log: List[List[str]], enable_optional_chains: bool = True, enable_xor: bool = True) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    outgoing, incoming, causal_edges = _build_causal_maps(rel, counter)

    before = _eventual_before(log, counter)
    reduced_edges = _transitive_reduction(causal_edges, counter)
    chain_candidates = _path_chains(reduced_edges, counter)
    if enable_optional_chains:
        selected_chains, rejected_chains = _select_optional_chains(chain_candidates, causal_edges, before, counter)
    else:
        selected_chains = []
        rejected_chains = [{"chain": list(chain), "reason": "optional_chains_disabled"} for chain in chain_candidates]

    covered_edges: Set[Edge] = set()
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

    emitted_chains = [_add_optional_chain(net, chain, causal_edges, covered_edges, counter) for chain in selected_chains]

    if enable_xor:
        split_groups, join_groups = _detect_xor_groups(outgoing, incoming, rel, covered_edges, counter)
    else:
        split_groups, join_groups = [], []

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
                "enable_optional_chains": enable_optional_chains,
                "enable_xor": enable_xor,
            },
            "transitive_reduction_edges": [list(edge) for edge in sorted(reduced_edges)],
            "optional_chain_candidates": [list(chain) for chain in chain_candidates],
            "optional_chains": emitted_chains,
            "rejected_chains": rejected_chains,
            "split_groups": [[list(pre), list(post)] for pre, post in split_groups],
            "join_groups": [[list(pre), list(post)] for pre, post in join_groups],
            "edge_places": [[a, b] for a, b in sorted(emitted_edges)],
            "covered_edges": [list(edge) for edge in sorted(covered_edges)],
        },
        operation_counts=counter.to_dict(),
    )
    return {
        "candidate_id": "ALG-0010",
        "name": "PMIR Conflict-Aware Optional Chain Compiler",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
