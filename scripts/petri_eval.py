"""Minimal token-game evaluation for JSON Petri nets.

This evaluator is intentionally conservative: a trace replays only if each
visible transition is enabled in sequence and the final marking matches exactly.
For nets with silent transitions, it explores a bounded silent-transition
closure before each visible event and before the final marking check.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Tuple


def _transition_name(activity: str) -> str:
    return f"t_{activity}"


Marking = Tuple[Tuple[str, int], ...]


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


def _activity_transitions(petri_net: Dict[str, Any]) -> Dict[str, List[str]]:
    transitions = sorted(petri_net.get("transitions", []))
    explicit_labels = petri_net.get("transition_labels", {})
    by_activity: Dict[str, List[str]] = defaultdict(list)
    for transition in transitions:
        if transition.startswith("tau_"):
            continue
        label = explicit_labels.get(transition)
        if label is None and transition.startswith("t_"):
            label = transition[2:]
        if label is not None:
            by_activity[label].append(transition)
    return by_activity


def _normalize_marking(marking: Dict[str, int]) -> Marking:
    return tuple(sorted((place, count) for place, count in marking.items() if count))


def _marking_dict(marking: Marking) -> Dict[str, int]:
    return defaultdict(int, dict(marking))


def _enabled(marking: Dict[str, int], inputs: Dict[str, List[str]], transition: str) -> bool:
    return all(marking[p] > 0 for p in inputs.get(transition, []))


def _fire(marking: Dict[str, int], inputs: Dict[str, List[str]], outputs: Dict[str, List[str]], transition: str) -> Marking:
    next_marking = defaultdict(int, marking)
    for place in inputs.get(transition, []):
        next_marking[place] -= 1
    for place in outputs.get(transition, []):
        next_marking[place] += 1
    return _normalize_marking(next_marking)


def _silent_closure(
    markings: List[Marking],
    inputs: Dict[str, List[str]],
    outputs: Dict[str, List[str]],
    silent_transitions: List[str],
    max_states: int = 1000,
) -> Tuple[List[Marking], bool]:
    seen = set(markings)
    queue = deque(markings)
    truncated = False
    while queue and len(seen) < max_states:
        marking = queue.popleft()
        marking_dict = _marking_dict(marking)
        for transition in silent_transitions:
            if _enabled(marking_dict, inputs, transition):
                next_marking = _fire(marking_dict, inputs, outputs, transition)
                if next_marking not in seen:
                    seen.add(next_marking)
                    queue.append(next_marking)
    if queue:
        truncated = True
    return sorted(seen), truncated


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
    by_activity = _activity_transitions(petri_net)
    silent_transitions = sorted(t for t in transitions if t.startswith("tau_"))
    markings = [_normalize_marking(defaultdict(int, petri_net.get("initial_marking", {})))]
    closure_truncated = False

    for index, activity in enumerate(trace):
        candidate_transitions = by_activity.get(activity, [])
        if not candidate_transitions:
            return {
                "ok": False,
                "reason": "missing_transition",
                "activity": activity,
                "event_index": index,
            }
        markings, truncated = _silent_closure(markings, inputs, outputs, silent_transitions)
        closure_truncated = closure_truncated or truncated
        next_markings = []
        for marking in markings:
            marking_dict = _marking_dict(marking)
            for transition in candidate_transitions:
                if _enabled(marking_dict, inputs, transition):
                    next_markings.append(_fire(marking_dict, inputs, outputs, transition))
        if not next_markings:
            sample = _marking_dict(markings[0]) if markings else defaultdict(int)
            missing_by_transition = {
                transition: [p for p in inputs.get(transition, []) if sample[p] <= 0]
                for transition in candidate_transitions
            }
            return {
                "ok": False,
                "reason": "transition_not_enabled",
                "activity": activity,
                "candidate_transitions": candidate_transitions,
                "event_index": index,
                "missing_input_places_by_transition": missing_by_transition,
                "silent_closure_truncated": closure_truncated,
            }
        markings = sorted(set(next_markings))

    final_marking = petri_net.get("final_marking", {})
    final_normalized = _normalize_marking(defaultdict(int, final_marking))
    markings, truncated = _silent_closure(markings, inputs, outputs, silent_transitions)
    closure_truncated = closure_truncated or truncated
    if final_normalized in markings:
        return {"ok": True, "silent_closure_truncated": closure_truncated}

    sample = _marking_dict(markings[0]) if markings else defaultdict(int)
    places = set(petri_net.get("places", [])) | set(sample) | set(final_marking)
    mismatches = {
        place: {"actual": int(sample[place]), "expected": int(final_marking.get(place, 0))}
        for place in sorted(places)
        if int(sample[place]) != int(final_marking.get(place, 0))
    }
    return {
        "ok": False,
        "reason": "final_marking_mismatch",
        "mismatches": mismatches,
        "silent_closure_truncated": closure_truncated,
    }


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


def precision_probe(petri_net: Dict[str, Any], negative_traces: List[List[str]], max_failures: int = 3) -> Dict[str, Any]:
    accepted = []
    rejected = 0
    for trace in negative_traces:
        result = replay_trace(petri_net, trace)
        if result["ok"]:
            if len(accepted) < max_failures:
                accepted.append({"trace": trace, "reason": "negative_trace_replayed"})
        else:
            rejected += 1

    total = len(negative_traces)
    return {
        "negative_trace_count": total,
        "rejected_negative_traces": rejected,
        "accepted_negative_traces": total - rejected,
        "negative_rejection_rate": 1.0 if total == 0 else rejected / total,
        "accepted_examples": accepted,
    }
