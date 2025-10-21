from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from .executor import PlanExecutionError, execute_plan, parse_params
from .loader import load_plan

app = typer.Typer(help="APOE ACL runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@app.command()
def run(
    plan_path: Path = typer.Argument(..., help="Path to the ACL plan (YAML)."),
    workspace: Optional[Path] = typer.Option(None, "--workspace", "-w", help="Workspace directory for outputs."),
    param: Optional[List[str]] = typer.Option(None, "--param", "-p", help="Input parameters as key=value (JSON accepted)."),
) -> None:
    """Execute an APOE ACL plan."""
    plan = load_plan(plan_path)
    run_workspace = workspace or Path("runs") / f"{plan['id']}_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    params = parse_params(param or [])
    try:
        context = execute_plan(plan, workspace=run_workspace, params=params)
    except PlanExecutionError as exc:
        raise typer.Exit(code=1) from exc
    typer.echo(f"Plan '{plan['id']}' completed. Workspace: {run_workspace}")
    typer.echo(f"Outputs: {context.get('output', {})}")


if __name__ == "__main__":
    app()
