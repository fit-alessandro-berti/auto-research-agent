"""ALG-0005: Prefix Automaton Compression Miner.

This candidate is an exact-replay comparator. It builds a prefix trie over log
variants, merges states with identical suffix signatures, and compiles the
resulting finite automaton to an accepting Petri net.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from limited_ops import OpCounter, comparison, construct, dict_increment, relation_classification, scan_event, set_insert, set_lookup
from pn_ir import PMIR, PetriNet, pair_key


TraceLog = List[List[str]]
Signature = Tuple[bool, Tuple[Tuple[str, object], ...]]
AutomatonEdge = Tuple[str, str, str]


def _safe_name(*parts: str) -> str:
    return "_".join(str(part) for part in parts).replace(" ", "_").replace("/", "_")


def _place(state: str) -> str:
    return f"p_pa_{state}"


def _transition(label: str, source: str, target: str) -> str:
    return f"t_{_safe_name(label)}__{source}__{target}"


def _tau_accept(state: str) -> str:
    return f"tau_pa_accept_{state}"


def _insert_traces(log: TraceLog, counter: OpCounter) -> Tuple[List[Dict[str, int]], Set[int], Counter]:
    children: List[Dict[str, int]] = [{}]
    terminal_nodes: Set[int] = set()
    variants: Counter = Counter()

    for trace in log:
        variants[tuple(trace)] += 1
        dict_increment(counter)
        node = 0
        for event in trace:
            scan_event(counter)
            set_lookup(counter)
            if event not in children[node]:
                children.append({})
                children[node][event] = len(children) - 1
                set_insert(counter)
                construct(counter)
            node = children[node][event]
        terminal_nodes.add(node)
        set_insert(counter)
    return children, terminal_nodes, variants


def _compress_states(
    children: List[Dict[str, int]],
    terminal_nodes: Set[int],
    counter: OpCounter,
) -> Tuple[Dict[int, str], Dict[int, object], Dict[str, object]]:
    signatures: Dict[int, object] = {}
    signature_to_state: Dict[object, str] = {}
    node_to_state: Dict[int, str] = {}
    merge_evidence: Dict[str, object] = {}

    for node in reversed(range(len(children))):
        child_signatures = []
        for label, child in sorted(children[node].items()):
            set_lookup(counter)
            child_signatures.append((label, signatures[child]))
            construct(counter)
        signature = (node in terminal_nodes, tuple(child_signatures))
        signatures[node] = signature
        set_lookup(counter)
        if signature not in signature_to_state:
            state = f"q{len(signature_to_state)}"
            signature_to_state[signature] = state
            merge_evidence[state] = {
                "terminal": node in terminal_nodes,
                "raw_nodes": [],
                "outgoing_labels": [label for label, _ in child_signatures],
            }
            set_insert(counter)
            construct(counter)
        state = signature_to_state[signature]
        node_to_state[node] = state
        merge_evidence[state]["raw_nodes"].append(node)  # type: ignore[index]
        relation_classification(counter)

    return node_to_state, signatures, merge_evidence


def _compressed_edges(
    children: List[Dict[str, int]],
    node_to_state: Dict[int, str],
    terminal_nodes: Set[int],
    counter: OpCounter,
) -> Tuple[List[AutomatonEdge], Set[str]]:
    edges: Set[AutomatonEdge] = set()
    terminal_states: Set[str] = set()
    for node, outgoing in enumerate(children):
        source = node_to_state[node]
        if node in terminal_nodes:
            terminal_states.add(source)
            set_insert(counter)
        for label, child in sorted(outgoing.items()):
            edge = (source, label, node_to_state[child])
            edges.add(edge)
            set_insert(counter)
    return sorted(edges), terminal_states


def _compile_automaton(
    states: Set[str],
    edges: List[AutomatonEdge],
    start_state: str,
    terminal_states: Set[str],
    counter: OpCounter,
) -> PetriNet:
    net = PetriNet()
    for state in sorted(states):
        net.add_place(_place(state))
        construct(counter)
    net.add_place("p_end")
    net.initial_marking = {_place(start_state): 1}
    net.final_marking = {"p_end": 1}
    construct(counter)

    for source, label, target in edges:
        transition = _transition(label, source, target)
        net.add_transition(transition)
        net.transition_labels[transition] = label
        net.add_arc(_place(source), transition)
        net.add_arc(transition, _place(target))
        construct(counter, 3)

    for state in sorted(terminal_states):
        transition = _tau_accept(state)
        net.add_transition(transition)
        net.add_arc(_place(state), transition)
        net.add_arc(transition, "p_end")
        construct(counter, 3)

    return net


def discover(log: TraceLog) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    children, terminal_nodes, variants = _insert_traces(log, counter)
    node_to_state, _signatures, merge_evidence = _compress_states(children, terminal_nodes, counter)
    edges, terminal_states = _compressed_edges(children, node_to_state, terminal_nodes, counter)
    states = set(node_to_state.values())
    net = _compile_automaton(states, edges, node_to_state[0], terminal_states, counter)

    raw_edge_count = sum(len(outgoing) for outgoing in children)
    evidence = {
        "raw_trie_nodes": len(children),
        "raw_trie_edges": raw_edge_count,
        "compressed_states": len(states),
        "compressed_edges": len(edges),
        "terminal_states": sorted(terminal_states),
        "start_state": node_to_state[0],
        "variant_count": len(variants),
        "variants": [
            {"trace": list(trace), "count": count}
            for trace, count in sorted(variants.items(), key=lambda item: (item[0], item[1]))
        ],
        "state_merges": {
            state: data
            for state, data in sorted(merge_evidence.items())
            if len(data["raw_nodes"]) > 1  # type: ignore[index]
        },
        "automaton_edges": [
            {"source": source, "label": label, "target": target}
            for source, label, target in edges
        ],
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
        "candidate_id": "ALG-0005",
        "name": "Prefix Automaton Compression Miner",
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
