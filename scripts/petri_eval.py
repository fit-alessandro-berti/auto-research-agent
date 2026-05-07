"""Minimal token-game evaluation for JSON Petri nets.

This evaluator is intentionally conservative: a trace replays only if each
visible transition is enabled in sequence and the final marking matches exactly.
It does not search silent-transition paths yet.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple


def _transition_name(activity: str) -> str:
    return f"t_{activity}"


def _build_flow(petri_net: Dict[str, Any]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    transitions = set(petri_net.get("transitions", []))
    inputs: Dict[str, List[str]] = {t: [] for t in transitions}
    outputs: Dict[str, List[str]] = {t: [] for t in transitions}
    for arc in petri_net.get("arcs", []):
        source = arc["source"]
        target = arc["target"]
        if target in transitions:
            inputs.setdefault(target, []).append(source)
        if source in transitions:
            outputs.setdefault(source, []).append(target)
    return inputs, outputs


def structural_diagnostics(petri_net: Dict[str, Any]) -> Dict[str, Any]:
    inputs, outputs = _build_flow(petri_net)
    transitions = sorted(petri_net.get("transitions", []))
    visible_transitions = [t for t in transitions if not t.startswith("tau_")]
    places = set(petri_net.get("places", []))
    initial_places = set(petri_net.get("initial_marking", {}))
    final_places = set(petri_net.get("final_marking", {}))
    place_inputs = {place: 0 for place in places}
    place_outputs = {place: 0 for place in places}
    invalid_arcs = []

    for arc in petri_net.get("arcs", []):
        source = arc["source"]
        target = arc["target"]
        if source in transitions and target in places:
            place_inputs[target] += 1
        elif source in places and target in transitions:
            place_outputs[source] += 1
        else:
            invalid_arcs.append(arc)

    return {
        "visible_transitions_without_inputs": [t for t in visible_transitions if not inputs.get(t)],
        "visible_transitions_without_outputs": [t for t in visible_transitions if not outputs.get(t)],
        "places_without_inputs_except_initial": sorted(p for p, n in place_inputs.items() if n == 0 and p not in initial_places),
        "places_without_outputs_except_final": sorted(p for p, n in place_outputs.items() if n == 0 and p not in final_places),
        "invalid_arcs": invalid_arcs,
    }


def replay_trace(petri_net: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
    inputs, outputs = _build_flow(petri_net)
    transitions = set(petri_net.get("transitions", []))
    marking = defaultdict(int, petri_net.get("initial_marking", {}))

    for index, activity in enumerate(trace):
        transition = _transition_name(activity)
        if transition not in transitions:
            return {
                "ok": False,
                "reason": "missing_transition",
                "activity": activity,
                "event_index": index,
            }
        missing = [p for p in inputs.get(transition, []) if marking[p] <= 0]
        if missing:
            return {
                "ok": False,
                "reason": "transition_not_enabled",
                "activity": activity,
                "transition": transition,
                "event_index": index,
                "missing_input_places": missing,
            }
        for place in inputs.get(transition, []):
            marking[place] -= 1
        for place in outputs.get(transition, []):
            marking[place] += 1

    final_marking = petri_net.get("final_marking", {})
    places = set(petri_net.get("places", [])) | set(marking) | set(final_marking)
    mismatches = {
        place: {"actual": int(marking[place]), "expected": int(final_marking.get(place, 0))}
        for place in sorted(places)
        if int(marking[place]) != int(final_marking.get(place, 0))
    }
    if mismatches:
        return {"ok": False, "reason": "final_marking_mismatch", "mismatches": mismatches}
    return {"ok": True}


def replay_log(petri_net: Dict[str, Any], log: List[List[str]], max_failures: int = 3) -> Dict[str, Any]:
    silent_transitions = [t for t in petri_net.get("transitions", []) if t.startswith("tau_")]
    replayed = 0
    failures = []
    for trace in log:
        result = replay_trace(petri_net, trace)
        if result["ok"]:
            replayed += 1
        elif len(failures) < max_failures:
            failure = {"trace": trace}
            failure.update(result)
            failures.append(failure)

    trace_count = len(log)
    return {
        "trace_count": trace_count,
        "replayed_traces": replayed,
        "replay_fitness": 1.0 if trace_count == 0 else replayed / trace_count,
        "strict_final_marking": True,
        "silent_transition_support": "none" if not silent_transitions else "not_supported",
        "silent_transitions": silent_transitions,
        "structural_diagnostics": structural_diagnostics(petri_net),
        "failed_examples": failures,
    }
