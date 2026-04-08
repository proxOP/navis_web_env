"""Deterministic graders for the Navis web tasks."""

from __future__ import annotations

from typing import Any, Dict


def grade_episode(summary: Dict[str, Any]) -> float:
    """Grade an episode summary on a deterministic 0.0 to 1.0 scale."""

    if not summary.get("reached_target"):
        raw_score = 0.01  # strictly > 0
    else:
        actual_steps = max(int(summary.get("actual_steps", 0)), 1)
        optimal_steps = max(int(summary.get("optimal_steps", actual_steps)), 1)
        efficiency = min(optimal_steps / actual_steps, 1.0)
        raw_score = 0.7 + (0.3 * efficiency)

    # OpenEnv requirement: scores must be strictly in (0.0, 1.0)
    return round(min(max(raw_score, 0.01), 0.99), 3)
