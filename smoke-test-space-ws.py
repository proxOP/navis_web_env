"""Persistent-session smoke test for the live Hugging Face Space."""

from __future__ import annotations

import argparse
import asyncio
from typing import Sequence

from navis_web_env.client import NavisWebEnv
from navis_web_env.models import NavisWebAction


async def run(base_url: str, task_id: str) -> int:
    print(f"Connecting to {base_url}")
    print(f"Task: {task_id}")
    print("")

    async with NavisWebEnv(base_url=base_url) as env:
        reset_result = await env.reset(task_id=task_id)
        print(
            f"[PASS] reset page_id={reset_result.observation.page_id} "
            f"remaining_steps={reset_result.observation.remaining_steps}"
        )

        step1 = await env.step(NavisWebAction(click_link_id="home_support"))
        print(
            f"[PASS] step1 page_id={step1.observation.page_id} "
            f"reward={step1.reward} done={step1.done}"
        )

        step2 = await env.step(NavisWebAction(click_link_id="support_contact"))
        print(
            f"[PASS] step2 page_id={step2.observation.page_id} "
            f"reward={step2.reward} done={step2.done}"
        )

        state = await env.state()
        print(
            f"[PASS] state current_page_id={state.current_page_id} "
            f"step_count={state.step_count} termination_reason={state.termination_reason}"
        )

        if reset_result.observation.page_id != "home":
            print("[FAIL] reset did not start on the expected easy-task page")
            return 1
        if step1.observation.page_id != "support_center":
            print("[FAIL] first step did not reach support_center")
            return 1
        if step2.observation.page_id != "contact_support" or not step2.done:
            print("[FAIL] second step did not finish the easy task")
            return 1

        print("")
        print("[PASS] WebSocket/OpenEnv session continuity is working.")
        return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the live HF Space via OpenEnv client session.")
    parser.add_argument("--base-url", default="https://proxjod-navis-web-env.hf.space")
    parser.add_argument("--task-id", default="easy")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    return asyncio.run(run(base_url=args.base_url, task_id=args.task_id))


if __name__ == "__main__":
    raise SystemExit(main())
