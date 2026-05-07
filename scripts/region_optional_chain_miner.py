"""ALG-0012: Region Optional-Chain Repair Miner.

This candidate tests whether ALG-0011's singleton optional repair can be
extended to chain skips while still grounding the repair in selected bounded
region shortcut places. With require_region_shortcut=False it acts as ALG-0013,
the no-certification ablation.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from alpha_lite import classify_relations, summarize_log
from bounded_place_region_miner import (
    PlaceCandidate,
    _compile_net,
    _enumerate_valid_candidates,
    _select_nonblocking_candidates,
)
from limited_ops import OpCounter, comparison, construct, set_insert, set_lookup
from pmir_conflict_aware_optional import (
    Chain,
    _add_optional_chain,
    _build_causal_maps,
    _eventual_before,
    _path_chains,
    _select_optional_chains,
    _shortcut_edges,
    _transitive_reduction,
)
from pn_ir import PMIR, pair_key


Edge = Tuple[str, str]
TraceLog = List[List[str]]


def _selected_shortcuts(selected: List[PlaceCandidate], counter: OpCounter) -> Set[Edge]:
    shortcuts: Set[Edge] = set()
    for pre, post in selected:
        comparison(counter)
        if len(pre) == 1 and len(post) == 1:
            shortcuts.add((pre[0], post[0]))
            set_insert(counter)
    return shortcuts


def _filter_region_certified_chains(
    chains: List[Chain],
    causal_edges: Set[Edge],
    selected_shortcuts: Set[Edge],
    counter: OpCounter,
) -> Tuple[List[Chain], List[Dict[str, object]]]:
    accepted: List[Chain] = []
    rejected: List[Dict[str, object]] = []
    for chain in chains:
        shortcuts = _shortcut_edges(chain, causal_edges, counter)
        certified = sorted(edge for edge in shortcuts if edge in selected_shortcuts)
        set_lookup(counter, len(shortcuts))
        comparison(counter)
        if certified:
            accepted.append(chain)
            construct(counter)
        else:
            rejected.append(
                {
                    "chain": list(chain),
                    "reason": "no_selected_region_shortcut",
                    "shortcut_edges": [list(edge) for edge in sorted(shortcuts)],
                }
            )
    return accepted, rejected


def discover(
    log: TraceLog,
    max_set_size: int = 2,
    enable_optional_chains: bool = True,
    require_region_shortcut: bool = True,
) -> Dict[str, object]:
    counter = OpCounter()
    activities, starts, ends, dfg = summarize_log(log, counter)
    rel = classify_relations(activities, dfg, counter)
    valid, stats = _enumerate_valid_candidates(activities, dfg, log, max_set_size, counter)
    selected, rejected_positive_replay = _select_nonblocking_candidates(valid, log, counter)

    _outgoing, _incoming, causal_edges = _build_causal_maps(rel, counter)
    before = _eventual_before(log, counter)
    reduced_edges = _transitive_reduction(causal_edges, counter)
    chain_candidates = _path_chains(reduced_edges, counter)
    selected_shortcuts = _selected_shortcuts(selected, counter)

    if enable_optional_chains:
        initially_selected, rejected_chains = _select_optional_chains(chain_candidates, causal_edges, before, counter)
        if require_region_shortcut:
            optional_chains, region_rejected = _filter_region_certified_chains(
                initially_selected,
                causal_edges,
                selected_shortcuts,
                counter,
            )
            rejected_chains.extend(region_rejected)
        else:
            optional_chains = initially_selected
    else:
        optional_chains = []
        rejected_chains = [{"chain": list(chain), "reason": "optional_chains_disabled"} for chain in chain_candidates]

    net = _compile_net(activities, starts, ends, selected, counter)
    covered_edges: Set[Edge] = set()
    emitted_chains = [_add_optional_chain(net, chain, causal_edges, covered_edges, counter) for chain in optional_chains]

    evidence = {
        "configuration": {
            "max_set_size": max_set_size,
            "enable_optional_chains": enable_optional_chains,
            "require_region_shortcut": require_region_shortcut,
            "region_certification": (
                "requires_selected_singleton_shortcut" if require_region_shortcut else "disabled_ablation"
            ),
        },
        "candidate_stats": {
            **stats,
            "valid_local_candidates": len(valid),
            "selected_candidates": len(selected),
            "rejected_positive_replay": rejected_positive_replay,
        },
        "selected_candidates": [[list(pre), list(post)] for pre, post in selected],
        "selected_shortcuts": [list(edge) for edge in sorted(selected_shortcuts)],
        "transitive_reduction_edges": [list(edge) for edge in sorted(reduced_edges)],
        "optional_chain_candidates": [list(chain) for chain in chain_candidates],
        "optional_chains": emitted_chains,
        "rejected_chains": rejected_chains,
        "covered_edges": [list(edge) for edge in sorted(covered_edges)],
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
    candidate_id = "ALG-0012" if require_region_shortcut else "ALG-0013"
    name = (
        "Region Optional-Chain Repair Miner"
        if require_region_shortcut
        else "Region Optional-Chain No-Certification Ablation"
    )
    return {
        "candidate_id": candidate_id,
        "name": name,
        "pmir": pmir.to_dict(),
        "petri_net": net.to_dict(),
        "structural_summary": net.structural_summary(),
        "operation_counts": counter.to_dict(),
    }
