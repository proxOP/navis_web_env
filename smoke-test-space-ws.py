"""Persistent-session smoke test for the live Hugging Face Space."""

from __future__ import annotations

import argparse
import asyncio
from typing import Sequence

from navis_web_env.client import NavisWebEnv
from navis_web_env.models import NavisWebAction

TASK_PATHS = {
    "easy": {
        "start_page": "home",
        "target_page": "contact_support",
        "actions": ["home_support", "support_contact"],
    },
    "medium": {
        "start_page": "landing",
        "target_page": "tuition_appeals_form",
        "actions": ["landing_students", "students_forms", "forms_tuition", "tuition_appeals"],
    },
    "hard": {
        "start_page": "dashboard",
        "target_page": "emergency_access_reset_playbook",
        "actions": ["dash_admin_console", "admin_secure_access", "secure_remote_signin", "remote_signin_reset_guide", "guides_emergency_playbook"],
    },
    "expert": {
        "start_page": "provider_home",
        "target_page": "prior_auth_escalation_worksheet",
        "actions": ["provider_auth", "auth_prior_auth", "prior_exception", "exceptions_clinical", "clinical_prior_auth", "prior_escalation_worksheet"],
    },
    "adversarial": {
        "start_page": "city_home",
        "target_page": "after_hours_shutoff_reversal_form",
        "actions": ["city_utilities", "utilities_service_interruptions", "interruptions_restoration", "restoration_emergency", "emergency_restoration_after_hours", "after_hours_form"],
    },
}


async def run(base_url: str, task_id: str) -> int:
    if task_id not in TASK_PATHS:
        print(f"[FAIL] Unsupported task_id '{task_id}'. Expected one of: {', '.join(TASK_PATHS)}")
        return 1

    task_plan = TASK_PATHS[task_id]
    print(f"Connecting to {base_url}")
    print(f"Task: {task_id}")
    print("")

    async with NavisWebEnv(base_url=base_url) as env:
        reset_result = await env.reset(task_id=task_id)
        print(
            f"[PASS] reset page_id={reset_result.observation.page_id} "
            f"remaining_steps={reset_result.observation.remaining_steps}"
        )

        step_result = reset_result
        for step_index, click_link_id in enumerate(task_plan["actions"], start=1):
            step_result = await env.step(NavisWebAction(click_link_id=click_link_id))
            print(
                f"[PASS] step{step_index} page_id={step_result.observation.page_id} "
                f"reward={step_result.reward} done={step_result.done} action={click_link_id}"
            )

        state = await env.state()
        print(
            f"[PASS] state current_page_id={state.current_page_id} "
            f"step_count={state.step_count} termination_reason={state.termination_reason}"
        )

        if reset_result.observation.page_id != task_plan["start_page"]:
            print(f"[FAIL] reset did not start on the expected page '{task_plan['start_page']}'")
            return 1
        if state.current_page_id != task_plan["target_page"]:
            print(f"[FAIL] final state did not reach target page '{task_plan['target_page']}'")
            return 1
        if not step_result.done:
            print("[FAIL] final step did not finish the task")
            return 1

        print("")
        print("[PASS] WebSocket/OpenEnv session continuity is working.")
        return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test the live HF Space via OpenEnv client session.")
    parser.add_argument("--base-url", default="https://adieee5-navis-web-ad.hf.space")
    parser.add_argument("--task-id", default="easy")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    return asyncio.run(run(base_url=args.base_url, task_id=args.task_id))


if __name__ == "__main__":
    raise SystemExit(main())
