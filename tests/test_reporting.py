"""Tests for evaluation reporting and trajectory visualization."""

from __future__ import annotations

import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import inference
from navis_web_env.reporting import render_trajectory_mermaid, write_evaluation_artifacts


def test_render_trajectory_mermaid_marks_target_and_path():
    mermaid = render_trajectory_mermaid("easy", path=["home", "support_center", "contact_support"])

    assert "graph TD" in mermaid
    assert 'node_contact_support["Contact Support"]' in mermaid
    assert "class node_contact_support target,visited" in mermaid
    assert ":::pathEdge" in mermaid


def test_write_evaluation_artifacts_creates_dashboard_and_trajectory_files(tmp_path):
    comparison = inference.run_benchmark_comparison(["heuristic"])

    written = write_evaluation_artifacts(comparison, tmp_path)

    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "dashboard.html").exists()
    assert (tmp_path / "report.json").exists()
    assert "markdown_report" in written

    trajectory_files = list((tmp_path / "trajectories").glob("*.md"))
    assert trajectory_files
    trajectory_content = trajectory_files[0].read_text(encoding="utf-8")
    assert "```mermaid" in trajectory_content
    assert "Path:" in trajectory_content
