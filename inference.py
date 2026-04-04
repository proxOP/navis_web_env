"""Baseline inference runner for the Navis OpenEnv hackathon submission."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from navis_web_env.grading import grade_episode
from navis_web_env.models import NavisWebAction
from navis_web_env.server.navis_web_environment import NavisWebEnvironment
from navis_web_env.site_loader import list_task_ids

load_dotenv()

OUTPUT_DIR = Path("outputs/evals")
OUTPUT_PATH = OUTPUT_DIR / "baseline.json"
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i", "in", "into",
    "is", "it", "of", "on", "or", "page", "reach", "site", "that", "the", "this", "to", "you", "your"
}
MAX_STEPS_FALLBACK = 20
BENCHMARK_NAME = "navis_web_env"


def agent_mode() -> str:
    return os.getenv("BASELINE_AGENT", "agent").strip().lower()


def api_base_url() -> str:
    url = os.getenv("API_BASE_URL")
    if not url:
        raise RuntimeError("API_BASE_URL is required for BASELINE_AGENT=agent.")
    return url


def api_key() -> str:
    key = os.getenv("HF_TOKEN")
    if not key:
        raise RuntimeError("HF_TOKEN is required for BASELINE_AGENT=agent.")
    return key


def model_name() -> str:
    model = os.getenv("MODEL_NAME")
    if not model:
        raise RuntimeError("MODEL_NAME is required.")
    return model


def build_client() -> Any:
    from openai import OpenAI
    return OpenAI(base_url=api_base_url(), api_key=api_key())


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    action_text = action.replace("\n", "\\n")
    error_text = (error or "none").replace("\n", "\\n")
    print(
        f"[STEP] step={step} action={action_text} reward={reward:.3f} "
        f"done={str(done).lower()} error={error_text}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{reward:.2f}" for reward in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def prompt_from_observation(observation: Any) -> str:
    link_lines = []
    for link in observation.available_links:
        preview = f" | preview: {link.preview_text}" if link.preview_text else ""
        aria = f" | aria: {link.aria_label}" if link.aria_label else ""
        link_lines.append(f"- {link.link_id}: {link.label} | role: {link.role}{aria}{preview}")

    return "\n".join(
        [
            "You are navigating a deterministic mock website.",
            "Choose exactly one available link id that best helps reach the goal page.",
            "Return strict JSON with this shape only: {\"click_link_id\": \"...\"}",
            f"Goal: {observation.goal_instruction}",
            f"Target page title: {observation.target_page_title}",
            f"Current page title: {observation.page_title}",
            f"Current page text: {observation.page_text}",
            f"Remaining steps: {observation.remaining_steps}",
            "Available links:",
            *link_lines,
        ]
    )


def _extract_response_text(response: Any) -> str:
    try:
        return response.choices[0].message.content.strip()
    except (IndexError, AttributeError):
        return ""


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS and len(token) > 1}


def choose_action_with_llm(client: Any, model: str, observation: Any) -> str:
    prompt = prompt_from_observation(observation)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a web navigation agent. Respond only with valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    text = _extract_response_text(response)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return "__invalid_json__"
    click_link_id = payload.get("click_link_id")
    return click_link_id if isinstance(click_link_id, str) else "__invalid_json__"


def choose_action_with_heuristic(observation: Any) -> str:
    goal_tokens = _tokenize(observation.goal_instruction)
    target_tokens = _tokenize(observation.target_page_title)
    page_tokens = _tokenize(observation.page_title + " " + observation.page_text)
    query_tokens = goal_tokens | target_tokens

    best_link_id = observation.available_links[0].link_id if observation.available_links else "__invalid_json__"
    best_score = float("-inf")

    for index, link in enumerate(observation.available_links):
        link_text = " ".join(
            part for part in [link.label, link.aria_label or "", link.preview_text or ""] if part
        )
        link_tokens = _tokenize(link_text)

        overlap_score = len(query_tokens & link_tokens) * 3
        target_overlap = len(target_tokens & link_tokens) * 5
        support_bonus = 2 if "support" in query_tokens and "support" in link_tokens else 0
        page_novelty = len((query_tokens - page_tokens) & link_tokens)
        total_score = overlap_score + target_overlap + support_bonus + page_novelty - (index * 0.01)

        if total_score > best_score:
            best_score = total_score
            best_link_id = link.link_id

    return best_link_id


def choose_action(agent: Any, model: str | None, observation: Any, mode: str) -> str:
    if mode == "heuristic":
        return choose_action_with_heuristic(observation)
    if mode == "agent":
        if agent is None or model is None:
            return "__invalid_json__"
        return choose_action_with_llm(agent, model, observation)
    raise ValueError(f"Unsupported BASELINE_AGENT '{mode}'. Expected 'heuristic' or 'agent'.")


def run_task(agent: Any, model: str | None, task_id: str, mode: str | None = None) -> dict[str, Any]:
    selected_mode = mode or agent_mode()
    model_label = model or "heuristic-semantic-baseline"
    env = NavisWebEnvironment(default_task_id=task_id)
    observation = env.reset(task_id=task_id)
    rewards: list[float] = []
    steps_taken = 0

    log_start(task=task_id, env=BENCHMARK_NAME, model=model_label)

    while not observation.done:
        click_link_id = choose_action(agent, model, observation, selected_mode)
        action_error = None if click_link_id != "__invalid_json__" else "invalid_action"
        observation = env.step(NavisWebAction(click_link_id=click_link_id))
        reward = float(observation.reward or 0.0)
        rewards.append(reward)
        steps_taken += 1
        log_step(
            step=steps_taken,
            action=click_link_id,
            reward=reward,
            done=observation.done,
            error=action_error,
        )

    summary = env.get_last_info()
    score = grade_episode(summary)
    log_end(
        success=bool(summary.get("reached_target")),
        steps=steps_taken,
        score=score,
        rewards=rewards,
    )
    return {
        "task_id": task_id,
        "score": score,
        "summary": summary,
    }


def main() -> None:
    selected_mode = agent_mode()
    selected_model = model_name() if selected_mode == "agent" else "heuristic-semantic-baseline"
    agent = build_client() if selected_mode == "agent" else None

    results = [run_task(agent, selected_model if selected_mode == "agent" else None, task_id, mode=selected_mode) for task_id in list_task_ids()]
    aggregate = round(sum(result["score"] for result in results) / len(results), 4)

    report = {
        "agent_mode": selected_mode,
        "model": selected_model,
        "tasks": results,
        "aggregate_score": aggregate,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
