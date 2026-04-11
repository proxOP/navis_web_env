---
title: Navis Web
sdk: docker
app_port: 8000
---
# Navis Web

Navis Web Env is a deterministic OpenEnv environment for training and evaluating web-navigation agents on a realistic but fully controlled task: moving through mock websites to reach a target page.

## Why This Environment Exists

Real browser environments are powerful, but they are also brittle for a hackathon setting. Live sites change, break, rate-limit, and introduce nondeterminism. This environment keeps the task realistic while removing that instability:

- The agent still solves a real task humans do: website wayfinding.
- Pages contain natural-language content and browser-like links.
- Each task is deterministic, reproducible, and easy to grade.
- Reward shaping gives signal across the full trajectory instead of only at the end.

## Environment Design

Each task is a mock site represented as a directed graph of pages:

- A page has a `title`, `text`, and ordered outgoing links.
- Each link includes DOM-lite metadata such as `label`, `role`, `aria_label`, and `preview_text`.
- The agent starts on a fixed page and must reach a fixed target page.

### Action Space

The action space is intentionally narrow:

- `NavisWebAction(click_link_id: str, reason: str | None = None)`

The only valid action is clicking one of the presented links.

### Observation Space

Each observation includes:

- `page_id`
- `page_title`
- `page_text`
- `available_links`
- `target_page_title`
- `goal_instruction`
- `remaining_steps`
- `visited_count`
- `done`
- `reward`

### State

The exported state includes the OpenEnv base metadata plus environment-specific details:

- current task id
- current page id
- target page id
- visit history
- visit counts per page
- shortest-path distance to target
- max steps
- action validity
- termination reason

## Tasks

The environment ships with 5 deterministic tasks:

- `easy`: 2-3 clicks with light distraction and no meaningful loops
- `medium`: 4-6 clicks with semantically plausible detours
- `hard`: 6-9 clicks with loops, repeated terminology, and near-target decoys
- `expert`: 6-step provider-portal workflow with claims/authorization ambiguity and escalation-form decoys
- `adversarial`: 5-step city-services utility workflow with emergency/outage lookalikes and reversal-form decoys

The tasks are defined under [`navis_web_env/sites`](./navis_web_env/sites).

## Reward Shaping

Reward is dense and trajectory-aware:

- `+1.0` for reaching the target page
- `+0.15` for strictly reducing shortest-path distance
- `0.0` bonus when a valid action leaves distance unchanged
- `-0.05` per step
- `-0.10` for revisiting a page
- `-0.20` for invalid link ids
- `-0.15` extra penalty for tight loops or repeated moves that increase distance

Episodes terminate on:

- success when the target is reached
- failure when max steps are exhausted
- failure when any page is visited more than 3 times

## Graders

Task graders are deterministic project-level functions. They score the final episode summary strictly inside `(0.0, 1.0)`:

- `0.99` for an optimal successful route
- `0.7-0.99` for successful but inefficient routes
- `0.01` for failure

Grader-facing episode summaries include:

- `task_id`
- `reached_target`
- `actual_steps`
- `optimal_steps`
- `invalid_actions`
- `repeat_visits`
- `termination_reason`

## Local Development

Install dependencies:

```bash
pip install -e .
```

Or using uv:

```bash
uv sync
```

Run the server locally:

```bash
uv run uvicorn navis_web_env.server.app:app --host 0.0.0.0 --port 8000
```

For the fallback plain-HTTP path, `POST /reset` now returns a `session_id`. Subsequent `POST /step` and `GET /state` calls should include that `session_id` so episode state is preserved even when requests are handled independently.

## OpenEnv Validation

```bash
openenv validate --verbose
```

If `openenv` is not installed yet, install the runtime first:

```bash
pip install "openenv-core[core]"
```

## Docker

Build:

```bash
openenv build
```

Run directly with Docker:

```bash
docker build -t navis-web-env .
docker run -p 8000:8000 navis-web-env
```

## Baseline Inference

The hackathon baseline script is at the repo root as [`inference.py`](./inference.py). It supports three agent modes:

- `agent` (default): uses the OpenAI-compatible client with `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`, with heuristic fallback if the response is invalid
- `heuristic`: a stronger local policy that scores link labels, aria text, previews, revisit penalties, and backtracking hints
- `oracle`: shortest-path ceiling policy for debugging and benchmarking

Environment variables (configured via `.env`):

- `BASELINE_AGENT=agent`, `BASELINE_AGENT=heuristic`, or `BASELINE_AGENT=oracle`
- `API_BASE_URL` — the LLM API endpoint (only needed for `agent` mode)
- `MODEL_NAME` — the model identifier (only needed for `agent` mode)
- `HF_TOKEN` — your API key (only needed for `agent` mode)

Example default LLM agent run:

```bash
python inference.py
```

Example heuristic run:

```bash
# Set in .env or export:
# BASELINE_AGENT=heuristic
python inference.py
```

Example oracle run:

```bash
# Set in .env or export:
# BASELINE_AGENT=oracle
python inference.py
```

All modes run all tasks in fixed order and save a reproducible report to `outputs/evals/baseline.json`.

## Expected Baseline Outputs

The exact score depends on the selected agent mode and model, but the output report includes:

- per-task score
- path taken
- invalid action count
- repeat visits
- trajectory trace
- aggregate mean score

## Evaluation Dashboard And Trajectory Visualizer

Run the comparison script to benchmark multiple modes and generate judge-friendly artifacts:

```bash
uv run python scripts/evaluate.py --modes heuristic oracle
```

This writes:

- `outputs/evals/report.md` — markdown summary with aggregate metrics and per-task tables
- `outputs/evals/dashboard.html` — lightweight dashboard for quick viewing
- `outputs/evals/report.json` — machine-readable benchmark comparison output
- `outputs/evals/trajectories/*.md` — per-task trajectory reports with Mermaid graphs highlighting the visited path

The trajectory artifacts are useful for demos because they show:

- the full task graph
- the target page
- the start page
- the exact path the policy followed
- where loops or detours appeared

## Testing

Run the full test suite with:

```bash
uv run --with pytest pytest
```

## Hugging Face Spaces Deployment

This environment is deployed as a Docker-backed Hugging Face Space.

1. Validate locally with `openenv validate --verbose`
2. Create a Docker Space on Hugging Face
3. Push this repository to the Space repository
4. Set the required Space variables and secrets: `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN`
5. Ensure the Space responds correctly for `/health`, `/reset`, `/step`, `/state`, `/metadata`, and `/schema`

Because the environment is fully self-contained, deployment does not require access to live websites or external page content.
