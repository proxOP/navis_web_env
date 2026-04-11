"""Reporting and visualization helpers for Navis Web evaluations."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .site_loader import load_task


def _slugify(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def _node_id(page_id: str) -> str:
    return f"node_{page_id}"


def render_trajectory_mermaid(task_id: str, path: list[str] | None = None) -> str:
    """Render a Mermaid graph for a task, highlighting the visited trajectory."""

    task = load_task(task_id)
    path = path or []
    visited_nodes = set(path)
    path_edges = {(path[index], path[index + 1]) for index in range(len(path) - 1)}

    lines = ["graph TD"]
    for page_id, page in task.pages.items():
        node_class = []
        if page_id == task.target_page_id:
            node_class.append("target")
        if page_id == task.start_page_id:
            node_class.append("start")
        if page_id in visited_nodes:
            node_class.append("visited")

        lines.append(f'    {_node_id(page_id)}["{page.title}"]')
        if node_class:
            lines.append(f"    class {_node_id(page_id)} {','.join(node_class)}")

        for link in page.links:
            edge = (page_id, link.destination_page_id)
            edge_suffix = ":::pathEdge" if edge in path_edges else ""
            lines.append(
                f'    {_node_id(page_id)} -->|"{link.label}"| {_node_id(link.destination_page_id)}{edge_suffix}'
            )

    lines.extend(
        [
            "    classDef start fill:#d8f3dc,stroke:#2d6a4f,stroke-width:2px;",
            "    classDef target fill:#ffe5d9,stroke:#bc3908,stroke-width:3px;",
            "    classDef visited fill:#e9f5ff,stroke:#1d4ed8,stroke-width:2px;",
            "    classDef pathEdge stroke:#1d4ed8,stroke-width:3px;",
        ]
    )
    return "\n".join(lines)


def _task_table_rows(task_results: list[dict[str, Any]]) -> str:
    rows = []
    for result in task_results:
        summary = result.get("summary", {})
        rows.append(
            "| {task_id} | {score:.3f} | {reached_target} | {actual_steps} | {optimal_steps} | {invalid_actions} | {repeat_visits} |".format(
                task_id=result["task_id"],
                score=float(result["score"]),
                reached_target="yes" if summary.get("reached_target") else "no",
                actual_steps=summary.get("actual_steps", 0),
                optimal_steps=summary.get("optimal_steps", 0),
                invalid_actions=summary.get("invalid_actions", 0),
                repeat_visits=summary.get("repeat_visits", 0),
            )
        )
    return "\n".join(rows)


def render_markdown_report(report: dict[str, Any]) -> str:
    """Create a markdown report for one or more benchmark modes."""

    lines = ["# Navis Web Evaluation Report", ""]
    for mode_report in report["modes"]:
        lines.extend(
            [
                f"## Mode: `{mode_report['agent_mode']}`",
                "",
                f"- Aggregate score: `{mode_report['aggregate_score']:.3f}`",
                f"- Success rate: `{mode_report['success_rate']:.2%}`",
                f"- Mean efficiency: `{mode_report['mean_efficiency']:.2%}`",
                "",
                "| Task | Score | Success | Steps | Optimal | Invalid | Revisits |",
                "| --- | ---: | :---: | ---: | ---: | ---: | ---: |",
                _task_table_rows(mode_report["tasks"]),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_html_dashboard(report: dict[str, Any]) -> str:
    """Render a lightweight HTML dashboard from a benchmark comparison payload."""

    sections = []
    for mode_report in report["modes"]:
        rows = []
        for result in mode_report["tasks"]:
            summary = result.get("summary", {})
            rows.append(
                "<tr>"
                f"<td>{html.escape(result['task_id'])}</td>"
                f"<td>{float(result['score']):.3f}</td>"
                f"<td>{'yes' if summary.get('reached_target') else 'no'}</td>"
                f"<td>{summary.get('actual_steps', 0)}</td>"
                f"<td>{summary.get('optimal_steps', 0)}</td>"
                f"<td>{summary.get('invalid_actions', 0)}</td>"
                f"<td>{summary.get('repeat_visits', 0)}</td>"
                "</tr>"
            )

        sections.append(
            """
            <section>
              <h2>Mode: {mode}</h2>
              <p><strong>Aggregate score:</strong> {aggregate:.3f} |
                 <strong>Success rate:</strong> {success:.2%} |
                 <strong>Mean efficiency:</strong> {efficiency:.2%}</p>
              <table>
                <thead>
                  <tr><th>Task</th><th>Score</th><th>Success</th><th>Steps</th><th>Optimal</th><th>Invalid</th><th>Revisits</th></tr>
                </thead>
                <tbody>
                  {rows}
                </tbody>
              </table>
            </section>
            """.format(
                mode=html.escape(mode_report["agent_mode"]),
                aggregate=float(mode_report["aggregate_score"]),
                success=float(mode_report["success_rate"]),
                efficiency=float(mode_report["mean_efficiency"]),
                rows="".join(rows),
            )
        )

    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Navis Web Evaluation</title>"
        "<style>body{font-family:Arial,sans-serif;margin:24px;color:#111827;}table{border-collapse:collapse;width:100%;margin:12px 0 28px;}th,td{border:1px solid #d1d5db;padding:8px;text-align:left;}th{background:#f3f4f6;}section{margin-bottom:32px;}code{background:#f3f4f6;padding:2px 4px;border-radius:4px;}</style>"
        "</head><body><h1>Navis Web Evaluation Dashboard</h1>"
        f"{''.join(sections)}</body></html>"
    )


def write_evaluation_artifacts(report: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    """Write comparison report plus per-task trajectory visualizations."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    trajectories_dir = output_path / "trajectories"
    trajectories_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = output_path / "report.md"
    html_path = output_path / "dashboard.html"
    json_path = output_path / "report.json"

    markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
    html_path.write_text(render_html_dashboard(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    written_paths = {
        "markdown_report": str(markdown_path),
        "html_dashboard": str(html_path),
        "json_report": str(json_path),
    }

    for mode_report in report["modes"]:
        for result in mode_report["tasks"]:
            summary = result.get("summary", {})
            path = summary.get("path", [])
            mermaid = render_trajectory_mermaid(result["task_id"], path=path)
            file_name = f"{_slugify(mode_report['agent_mode'])}-{_slugify(result['task_id'])}.md"
            trajectory_path = trajectories_dir / file_name
            trajectory_path.write_text(
                "\n".join(
                    [
                        f"# Trajectory: {mode_report['agent_mode']} / {result['task_id']}",
                        "",
                        f"- Score: `{float(result['score']):.3f}`",
                        f"- Path: `{ ' -> '.join(path) if path else 'no path recorded' }`",
                        "",
                        "```mermaid",
                        mermaid,
                        "```",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

    return written_paths
