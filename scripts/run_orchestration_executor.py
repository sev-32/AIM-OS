from __future__ import annotations

import argparse
import sys
from pathlib import Path

from packages.orchestration_builder.executor import OrchestrationExecutor


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute a generated orchestration using Gemini."
    )
    parser.add_argument(
        "orchestration_path",
        type=Path,
        help="Path to the orchestration directory (the folder containing orchestration_summary.json).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-exp",
        help="Gemini model to use. Defaults to gemini-2.0-flash-exp.",
    )
    parser.add_argument(
        "--max-agents",
        type=int,
        default=None,
        help="Optionally limit the number of agents executed (useful for dry-runs).",
    )
    parser.add_argument(
        "--skip-coordinators",
        action="store_true",
        help="Skip stage coordinator agents.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    executor = OrchestrationExecutor(
        args.orchestration_path,
        model_name=args.model,
    )
    audit_path = executor.run(
        max_agents=args.max_agents,
        include_coordinators=not args.skip_coordinators,
    )
    print(f"Audit trail written to {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
