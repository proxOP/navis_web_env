"""Baseline inference runner for the Navis OpenEnv hackathon submission."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from navis_web_env.grading import grade_episode
from navis_web_env.models import NavisWebAction
from navis_web_env.server.navis_web_environment import NavisWebEnvironment
from navis_web_env.site_loader import list_task_ids

load_dotenv()

# ── Environment variables (hackathon spec) ──────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# ── OpenAI client (uses HF_TOKEN as api_key per guidelines) ────────────
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# ── Constants ───────────────────────────────────────────────────────────
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


# ── Structured logging (hackathon output format) ───────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    action_text = action.replace("\n", "\\n")
    error_text = error.replace("\n", "\\n") if error else "null"
    print(
        f"[STEP] step={step} action={action_text} reward={reward:.2f} "
        f"done={str(done).lower()} error={error_text}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)


# ── Prompt / parsing helpers ───────────────────────────────────────────

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


# ── Action selection ───────────────────────────────────────────────────

def choose_action_with_llm(observation: Any, llm_client: Any = None, model_name: str | None = None) -> str:
    prompt = prompt_from_observation(observation)
    _client = llm_client if llm_client is not None else client
    _model = model_name if model_name is not None else MODEL_NAME
    response = _client.chat.completions.create(
        model=_model,
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


def choose_action(observation: Any, mode: str, llm_client: Any = None, model_name: str | None = None) -> str:
    if mode == "heuristic":
        return choose_action_with_heuristic(observation)
    if mode == "agent":
        return choose_action_with_llm(observation, llm_client=llm_client, model_name=model_name)
    raise ValueError(f"Unsupported BASELINE_AGENT '{mode}'. Expected 'heuristic' or 'agent'.")


# ── Task runner ────────────────────────────────────────────────────────

def run_task(
    llm_client_or_task_id: Any,
    model_name_or_mode: str | None = None,
    task_id: str | None = None,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """Run a single task episode and return the graded result.

    Supports two calling conventions:
      run_task(task_id, mode=...)                          # original positional form
      run_task(client, model_name, task_id, mode=...)     # injectable client form
    """
    # Detect calling convention
    if task_id is not None:
        # New form: run_task(client, model_name, task_id, mode=...)
        _llm_client = llm_client_or_task_id
        _model_name = model_name_or_mode
        _task_id = task_id
        _mode = mode
    elif isinstance(llm_client_or_task_id, str):
        # Original form: run_task(task_id, mode=...)
        _llm_client = None
        _model_name = None
        _task_id = llm_client_or_task_id
        _mode = model_name_or_mode or mode
    else:
        raise ValueError("task_id must be a string")

    selected_mode = _mode or agent_mode()
    model_label = (_model_name or MODEL_NAME) if selected_mode == "agent" else "heuristic-semantic-baseline"
    env = NavisWebEnvironment(default_task_id=_task_id)
    observation = env.reset(task_id=_task_id)
    rewards: list[float] = []
    steps_taken = 0
    success = False

    log_start(task=_task_id, env=BENCHMARK_NAME, model=model_label)

    try:
        while not observation.done:
            click_link_id = choose_action(observation, selected_mode, llm_client=_llm_client, model_name=_model_name)
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
        success = bool(summary.get("reached_target"))
    except Exception:
        summary = {}
        score = 0.01
    finally:
        log_end(success=success, steps=steps_taken, rewards=rewards)

    # Guarantee score is strictly within (0, 1) as required by the hackathon validator
    score = max(0.01, min(0.99, float(score)))

    return {
        "task_id": _task_id,
        "score": score,
        "summary": summary,
    }


# ── Main ───────────────────────────────────────────────────────────────

def main() -> None:
    selected_mode = agent_mode()
    model_label = MODEL_NAME if selected_mode == "agent" else "heuristic-semantic-baseline"

    results = [run_task(task_id, mode=selected_mode) for task_id in list_task_ids()]
    aggregate = round(sum(r["score"] for r in results) / len(results), 4) if results else 0.01
    aggregate = max(0.01, min(0.99, aggregate))

    report = {
        "agent_mode": selected_mode,
        "model": model_label,
        "tasks": results,
        "aggregate_score": aggregate,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
