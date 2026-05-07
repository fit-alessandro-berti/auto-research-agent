"""ALG-0023 wrapper for cut-limited process tree mining with a bounded loop cut."""

from __future__ import annotations

from typing import Dict, List

import cut_limited_process_tree


TraceLog = List[List[str]]


def discover(log: TraceLog) -> Dict[str, object]:
    return cut_limited_process_tree.discover(
        log,
        enable_parallel_optional=True,
        enable_short_loop=True,
        candidate_id_override="ALG-0023",
        name_override="Cut-Limited Single-Rework Loop Miner",
    )
