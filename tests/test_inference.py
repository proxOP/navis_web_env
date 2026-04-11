"""Tests for the baseline inference script."""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from io import StringIO
from contextlib import redirect_stdout

ROOT = os.path.join(os.path.dirname(__file__), "..")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import inference


class FakeCompletions:
    def __init__(self, choices: list[str]) -> None:
        self._choices = choices
        self._index = 0

    def create(self, **_: object) -> SimpleNamespace:
        choice = self._choices[self._index]
        self._index += 1
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=f'{{"click_link_id": "{choice}"}}')
                )
            ]
        )


class FakeClient:
    def __init__(self, choices: list[str]) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions(choices))


class BrokenCompletions:
    def create(self, **_: object) -> SimpleNamespace:
        raise RuntimeError("upstream completion failure")


class BrokenClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=BrokenCompletions())


def test_task_scores_always_stay_strictly_inside_open_interval():
    failing_result = inference.run_task(None, None, "easy", mode="heuristic")

    assert 0.0 < failing_result["score"] < 1.0


def test_aggregate_score_is_clamped_inside_open_interval():
    assert inference.normalize_score(0.0) == 0.01
    assert inference.normalize_score(1.0) == 0.99


def test_log_end_emits_explicit_clamped_score_for_output_parser():
    stream = StringIO()

    with redirect_stdout(stream):
        inference.log_end(success=True, steps=2, rewards=[0.15, 1.0], score=0.99)

    output = stream.getvalue().strip()
    assert "[END]" in output
    assert "score=0.990" in output


def test_run_task_completes_with_mocked_openai_compatible_client():
    client = FakeClient(["home_support", "support_contact"])
    result = inference.run_task(client, "fake-model", "easy", mode="agent")

    assert result["task_id"] == "easy"
    assert 0.0 < result["score"] < 1.0
    assert result["summary"]["reached_target"] is True


def test_heuristic_policy_completes_easy_task_without_llm():
    result = inference.run_task(None, None, "easy", mode="heuristic")

    assert result["task_id"] == "easy"
    assert result["score"] >= 0.7
    assert result["summary"]["reached_target"] is True


def test_heuristic_selects_support_link_for_easy_start_page():
    env = inference.NavisWebEnvironment(default_task_id="easy")
    observation = env.reset(task_id="easy")

    click_link_id = inference.choose_action_with_heuristic(observation)

    assert click_link_id == "home_support"


def test_run_task_falls_back_to_heuristic_when_agent_client_raises():
    result = inference.run_task(BrokenClient(), "fake-model", "easy", mode="agent")

    assert result["task_id"] == "easy"
    assert result["score"] >= 0.7
    assert 0.0 < result["score"] < 1.0
    assert result["summary"]["reached_target"] is True


def test_oracle_mode_reaches_target_optimally():
    result = inference.run_task("adversarial", mode="oracle")

    assert result["task_id"] == "adversarial"
    assert result["summary"]["reached_target"] is True
    assert result["summary"]["actual_steps"] == result["summary"]["optimal_steps"]
    assert result["score"] == 0.99


def test_run_benchmark_comparison_returns_mode_level_metrics():
    comparison = inference.run_benchmark_comparison(["heuristic", "oracle"])

    assert comparison["benchmark"] == "navis_web_env"
    assert [mode_report["agent_mode"] for mode_report in comparison["modes"]] == ["heuristic", "oracle"]
    assert all(0.0 < mode_report["aggregate_score"] < 1.0 for mode_report in comparison["modes"])
