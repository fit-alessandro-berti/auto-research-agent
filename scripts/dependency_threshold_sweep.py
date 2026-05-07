"""Parameter sweep for ALG-0002 dependency-threshold mining."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import dependency_threshold
from benchmark import NEGATIVE_TRACES, load_log
from petri_eval import precision_probe, replay_log


def sweep(log_dir: Path, min_counts: List[int], thresholds: List[float]) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "candidate_id": "ALG-0002",
        "algorithm": "dependency_threshold",
        "min_counts": min_counts,
        "dependency_thresholds": thresholds,
        "logs": {},
    }
    for log_path in sorted(log_dir.glob("*.json")):
        log = load_log(log_path)
        log_results = []
        negative_traces = NEGATIVE_TRACES.get(log_path.name, [])
        for min_count in min_counts:
            for threshold in thresholds:
                result = dependency_threshold.discover(log, min_count=min_count, dependency_threshold=threshold)
                replay = replay_log(result["petri_net"], log)
                probe = precision_probe(result["petri_net"], negative_traces)
                log_results.append(
                    {
                        "min_count": min_count,
                        "dependency_threshold": threshold,
                        "operation_total": result["operation_counts"]["total"],
                        "structural_summary": result["structural_summary"],
                        "replay_summary": {
                            "replayed_traces": replay["replayed_traces"],
                            "trace_count": replay["trace_count"],
                            "replay_fitness": replay["replay_fitness"],
                            "structural_diagnostics": replay["structural_diagnostics"],
                        },
                        "precision_probe": probe,
                        "accepted_edges": sorted(result["pmir"]["relations"]),
                    }
                )
        results["logs"][log_path.name] = {
            "trace_count": len(log),
            "event_count": sum(len(t) for t in log),
            "negative_trace_count": len(negative_traces),
            "runs": log_results,
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=Path, default=Path("examples/logs"))
    parser.add_argument("--out", type=Path, default=Path("experiments/dependency-threshold-sweep.json"))
    parser.add_argument("--min-counts", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.0, 0.25, 0.5, 0.75])
    args = parser.parse_args()

    results = sweep(args.logs, args.min_counts, args.thresholds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    for log_name, log_result in results["logs"].items():
        best = max(
            log_result["runs"],
            key=lambda r: (
                r["replay_summary"]["replayed_traces"],
                r["precision_probe"]["rejected_negative_traces"],
                -len(r["replay_summary"]["structural_diagnostics"]["visible_transitions_without_inputs"]),
                -len(r["replay_summary"]["structural_diagnostics"]["visible_transitions_without_outputs"]),
                -r["operation_total"],
            ),
        )
        print(
            f"{log_name}: min_count={best['min_count']} threshold={best['dependency_threshold']} "
            f"ops={best['operation_total']} replay="
            f"{best['replay_summary']['replayed_traces']}/{best['replay_summary']['trace_count']} "
            f"neg_reject={best['precision_probe']['rejected_negative_traces']}/"
            f"{best['precision_probe']['negative_trace_count']}"
        )


if __name__ == "__main__":
    main()
