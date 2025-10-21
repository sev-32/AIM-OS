"""Run MIGE seed?trunk?branch pipeline via APOE runner."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOE_CLI = [sys.executable, "-m", "packages.apoe_runner.cli"]


def run_plan(plan: str, *params: str, workspace: Path | None = None) -> None:
    workspace_args: list[str] = []
    if workspace is not None:
        workspace_args = ["--workspace", str(workspace)]
    cmd = APOE_CLI + [plan, *workspace_args]
    for param in params:
        cmd.extend(["--param", param])
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", default="runs/pipeline_seed", help="Workspace for seed plan")
    parser.add_argument("--trunk", default="runs/pipeline_trunk", help="Workspace for trunk plan")
    parser.add_argument("--branch", default="runs/pipeline_branch", help="Workspace for branch plan")
    parser.add_argument("--seed-capsule", default="Amplify Memory-to-Idea pipeline for governed deployments", help="Seed capsule vision text")
    parser.add_argument("--axes", nargs="*", default=["memory", "idea", "governance"], help="Axes passed to seed plan")
    parser.add_argument(
        "--policy-packs",
        nargs="*",
        default=["policy.mige.default"],
        help="Policy pack IDs applied to the seed vision tensor",
    )
    parser.add_argument("--constraint-proof", default="evidence/mige/constraint_proofs_p1.md", help="Path to constraint proof markdown")
    parser.add_argument("--vision-fit-threshold", type=float, default=0.8, help="Threshold for seed g_vision_fit gate")
    parser.add_argument("--trunk-threshold", type=float, default=0.82, help="Threshold for trunk g_trunk_coherence gate")
    args = parser.parse_args()

    seed_workspace = ROOT / args.seed
    trunk_workspace = ROOT / args.trunk
    branch_workspace = ROOT / args.branch

    axes_array = ",".join(f'\"{axis}\"' for axis in args.axes)
    policy_array = ",".join(f'\"{pack}\"' for pack in args.policy_packs)
    run_plan(
        "plans/seed_to_tensor.acl",
        f"seed_capsule=\"{args.seed_capsule}\"",
        f"axes=[{axes_array}]",
        f"policy_pack_ids=[{policy_array}]",
        f"vision_fit_threshold={args.vision_fit_threshold}",
        workspace=seed_workspace,
    )
    run_plan(
        "plans/tensor_to_trunk.acl",
        f"vision_tensor_path={seed_workspace / 'vision_tensor.json'}",
        f"trunk_coherence_threshold={args.trunk_threshold}",
        workspace=trunk_workspace,
    )
    run_plan(
        "plans/branch_to_specs.acl",
        f"trunk_nodes_path={trunk_workspace / 'trunk_nodes.json'}",
        f"constraint_proof_path={args.constraint_proof}",
        workspace=branch_workspace,
    )


if __name__ == "__main__":
    main()
