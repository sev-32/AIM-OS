"""Tests for Blast Radius Analysis"""

from __future__ import annotations
import pytest
from pathlib import Path
import tempfile
import os

from sdfcvf.blast_radius import DependencyAnalyzer, BlastRadiusResult, analyze_blast_radius


def test_blast_radius_basic():
    """Test basic blast radius calculation."""
    # Use actual project for realistic test
    analyzer = DependencyAnalyzer(repo_root=".")
    
    # Analyze blast radius of quartet.py
    result = analyzer.calculate_blast_radius(["packages/sdfcvf/quartet.py"])
    
    assert isinstance(result, BlastRadiusResult)
    assert result.directly_affected == 1
    assert result.total_affected >= result.directly_affected
    assert result.blast_radius_factor >= 0.0


def test_empty_changed_files():
    """Blast radius of no changes should be zero."""
    analyzer = DependencyAnalyzer(repo_root=".")
    result = analyzer.calculate_blast_radius([])
    
    assert result.total_affected == 0
    assert result.blast_radius_factor == 0.0


def test_high_impact_detection():
    """Should detect high-impact changes."""
    result = BlastRadiusResult(
        changed_files=["core.py"],
        directly_affected=1,
        transitively_affected=10,
        total_affected=11,
        affected_files=[],
        blast_radius_factor=11.0
    )
    
    assert result.is_high_impact(threshold=5.0)
    assert not result.is_high_impact(threshold=15.0)


def test_get_dependents():
    """Test getting files that depend on a file."""
    analyzer = DependencyAnalyzer(repo_root=".")
    
    # quartet.py is likely imported by other files
    dependents = analyzer.get_dependents("packages/sdfcvf/quartet.py")
    
    # Should return list (may be empty if no dependents)
    assert isinstance(dependents, list)


def test_get_dependencies():
    """Test getting files a file depends on."""
    analyzer = DependencyAnalyzer(repo_root=".")
    
    # quartet.py likely imports from pathlib, etc.
    dependencies = analyzer.get_dependencies("packages/sdfcvf/quartet.py")
    
    # Should return list
    assert isinstance(dependencies, list)


def test_convenience_function():
    """Test convenience function for blast radius."""
    result = analyze_blast_radius(["packages/sdfcvf/quartet.py"], repo_root=".")
    
    assert isinstance(result, BlastRadiusResult)
    assert result.directly_affected >= 0


@pytest.mark.skipif(
    not Path("packages/sdfcvf/quartet.py").exists(),
    reason="Requires actual codebase"
)
def test_realistic_blast_radius():
    """Test realistic blast radius with actual project files."""
    analyzer = DependencyAnalyzer(repo_root=".")
    
    # Change multiple related files
    changed = [
        "packages/sdfcvf/quartet.py",
        "packages/sdfcvf/parity.py"
    ]
    
    result = analyzer.calculate_blast_radius(changed)
    
    # Should detect some impact
    assert result.directly_affected == 2
    assert result.total_affected >= 2
    
    # Blast radius should be reasonable (not insane)
    assert result.blast_radius_factor < 50.0, "Blast radius factor too high"
    
    print(f"\n Blast radius for {len(changed)} files:")
    print(f"  Directly affected: {result.directly_affected}")
    print(f"  Transitively affected: {result.transitively_affected}")
    print(f"  Total affected: {result.total_affected}")
    print(f"  Blast radius factor: {result.blast_radius_factor:.1f}x")

