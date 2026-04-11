"""Run Navis Web benchmark modes and emit evaluation artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inference import run_benchmark_comparison
from navis_web_env.reporting import write_evaluation_artifacts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Navis Web benchmark modes.")
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["heuristic", "oracle"],
        help="Agent modes to benchmark.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/evals",
        help="Directory where report files should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    comparison = run_benchmark_comparison(args.modes)
    output_paths = write_evaluation_artifacts(comparison, Path(args.output_dir))
    for label, path in output_paths.items():
        print(f"[REPORT] {label}={path}", flush=True)


if __name__ == "__main__":
    main()
