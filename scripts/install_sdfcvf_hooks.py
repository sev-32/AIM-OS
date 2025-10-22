"""Install SDF-CVF Git Hooks

Installs pre-commit hook that checks quartet parity before allowing commits.
"""

from pathlib import Path
import shutil


PRE_COMMIT_HOOK = """#!/usr/bin/env python3
\"\"\"SDF-CVF Pre-Commit Hook

Checks quartet parity for changed files before allowing commit.
\"\"\"

import sys
import subprocess
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.sdfcvf import QuartetDetector, ParityCalculator, ParityGate, GateType

def main():
    # Get staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error getting staged files")
        sys.exit(1)
    
    changed_files = [f for f in result.stdout.strip().split('\\n') if f]
    
    if not changed_files:
        print("No files staged")
        sys.exit(0)
    
    print(f"SDF-CVF: Checking parity for {len(changed_files)} files...")
    
    # Detect quartet
    detector = QuartetDetector(repo_root=".")
    quartet = detector.detect_from_changes(changed_files)
    
    print(f"  Code: {len(quartet.code_files)}")
    print(f"  Docs: {len(quartet.doc_files)}")
    print(f"  Tests: {len(quartet.test_files)}")
    print(f"  Traces: {len(quartet.trace_files)}")
    
    # Calculate parity
    calculator = ParityCalculator(repo_root=".")
    parity_result = calculator.calculate_parity(quartet)
    
    print(f"  Parity score: {parity_result.parity_score:.3f}")
    
    # Check gate
    gate = ParityGate(gate_type=GateType.PRE_COMMIT, min_parity=0.70)
    gate_result = gate.check(parity_result)
    
    if gate_result.passed:
        print(f"✅ Parity check PASSED ({parity_result.parity_score:.3f} >= {gate.min_parity})")
        sys.exit(0)
    else:
        print(f"❌ Parity check FAILED ({parity_result.parity_score:.3f} < {gate.min_parity})")
        print(f"\\nReason: {gate_result.reason}")
        
        if gate_result.recommendation:
            print(f"Recommendation: {gate_result.recommendation}")
        
        print("\\nTo bypass (not recommended): git commit --no-verify")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""


def install_hooks(repo_root: Path = Path(".")):
    """
    Install SDF-CVF Git hooks.
    
    Args:
        repo_root: Repository root directory
    """
    git_hooks_dir = repo_root / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print(f"❌ Git hooks directory not found: {git_hooks_dir}")
        print("   Is this a Git repository?")
        return False
    
    # Install pre-commit hook
    pre_commit_path = git_hooks_dir / "pre-commit"
    
    # Backup existing hook if present
    if pre_commit_path.exists():
        backup_path = git_hooks_dir / "pre-commit.backup"
        shutil.copy(pre_commit_path, backup_path)
        print(f"📋 Backed up existing pre-commit hook to {backup_path}")
    
    # Write new hook
    pre_commit_path.write_text(PRE_COMMIT_HOOK)
    
    # Make executable (Unix)
    try:
        import stat
        pre_commit_path.chmod(pre_commit_path.stat().st_mode | stat.S_IEXEC)
    except Exception:
        pass  # Windows doesn't need this
    
    print(f"✅ Installed SDF-CVF pre-commit hook at {pre_commit_path}")
    print(f"   Parity threshold: 0.70 (configurable in hook)")
    print(f"   Bypass with: git commit --no-verify (not recommended)")
    
    return True


def uninstall_hooks(repo_root: Path = Path(".")):
    """
    Uninstall SDF-CVF Git hooks.
    
    Args:
        repo_root: Repository root directory
    """
    git_hooks_dir = repo_root / ".git" / "hooks"
    pre_commit_path = git_hooks_dir / "pre-commit"
    backup_path = git_hooks_dir / "pre-commit.backup"
    
    if not pre_commit_path.exists():
        print("No pre-commit hook installed")
        return
    
    # Restore backup if exists
    if backup_path.exists():
        shutil.copy(backup_path, pre_commit_path)
        backup_path.unlink()
        print(f"✅ Restored backup pre-commit hook")
    else:
        pre_commit_path.unlink()
        print(f"✅ Removed SDF-CVF pre-commit hook")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_hooks()
    else:
        install_hooks()

