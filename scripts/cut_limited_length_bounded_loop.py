"""ALG-0025 wrapper for cut-limited loop mining with length-bounded body choices."""

from __future__ import annotations

from typing import Dict, List

import cut_limited_process_tree


TraceLog = List[List[str]]


def discover(log: TraceLog) -> Dict[str, object]:
    return cut_limited_process_tree.discover(
        log,
        enable_parallel_optional=True,
        enable_short_loop=True,
        enable_multi_body_loop=True,
        multi_body_loop_max_body_length=2,
        candidate_id_override="ALG-0025",
        name_override="Cut-Limited Length-Bounded Rework Loop Miner",
    )
