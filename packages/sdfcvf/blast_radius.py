"""Blast Radius Analysis

Analyzes code dependencies to determine change impact.
Uses dependency graph to find all files affected by changes.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Dict, Optional

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


@dataclass
class BlastRadiusResult:
    """Result of blast radius analysis."""
    changed_files: List[str]
    directly_affected: int
    transitively_affected: int
    total_affected: int
    affected_files: List[str]
    blast_radius_factor: float  # Total affected / directly changed
    
    def is_high_impact(self, threshold: float = 5.0) -> bool:
        """Check if blast radius is high (affects many files)."""
        return self.blast_radius_factor > threshold


class DependencyAnalyzer:
    """
    Analyze code dependencies to determine blast radius.
    
    Builds dependency graph from imports and calculates forward propagation
    to identify all files affected by changes.
    """
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        
        if not HAS_NETWORKX:
            raise ImportError("NetworkX required for blast radius analysis. Install with: pip install networkx")
        
        self.graph = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build dependency graph from codebase by parsing imports."""
        # Find all Python files
        py_files = list(self.repo_root.rglob("*.py"))
        
        for file in py_files:
            # Skip test files and __pycache__
            if "__pycache__" in str(file) or "test_" in file.name:
                continue
            
            self._parse_file_dependencies(file)
    
    def _parse_file_dependencies(self, file_path: Path):
        """Parse imports from Python file and add to graph."""
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception:
            return  # Skip files with parse errors
        
        file_module = self._path_to_module(file_path)
        
        # Add node for this file
        self.graph.add_node(file_module, path=str(file_path))
        
        # Parse imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    self.graph.add_edge(file_module, imported)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported = node.module
                    # Handle relative imports
                    if node.level > 0:
                        # Relative import - resolve based on file location
                        parent_parts = file_module.split('.')[:-1]
                        if node.level == 1:
                            imported = '.'.join(parent_parts + [imported]) if parent_parts else imported
                    
                    self.graph.add_edge(file_module, imported)
    
    def _path_to_module(self, path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = path.relative_to(self.repo_root)
        except ValueError:
            # Path not relative to repo root
            return str(path)
        
        # Convert path to module notation
        module = str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')
        
        # Remove leading/trailing dots
        module = module.strip('.')
        
        return module
    
    def calculate_blast_radius(
        self,
        changed_files: List[str]
    ) -> BlastRadiusResult:
        """
        Calculate blast radius: all files potentially affected by changes.
        
        Uses forward propagation through dependency graph to find
        all files that depend on changed files (directly or transitively).
        
        Args:
            changed_files: List of file paths that were changed
            
        Returns:
            BlastRadiusResult with impact analysis
        """
        # Convert changed files to modules
        changed_modules: Set[str] = set()
        for file_path in changed_files:
            try:
                module = self._path_to_module(Path(file_path))
                changed_modules.add(module)
            except Exception:
                continue  # Skip files we can't convert
        
        if not changed_modules:
            return BlastRadiusResult(
                changed_files=changed_files,
                directly_affected=0,
                transitively_affected=0,
                total_affected=0,
                affected_files=[],
                blast_radius_factor=0.0
            )
        
        # Forward propagate (find all dependents)
        affected: Set[str] = set(changed_modules)
        
        for module in changed_modules:
            if module in self.graph:
                # Get all nodes that depend on this module (transitively)
                try:
                    dependents = nx.descendants(self.graph, module)
                    affected.update(dependents)
                except nx.NetworkXError:
                    # Module not in graph or other issue
                    continue
        
        # Convert back to file paths
        affected_files = []
        for module in affected:
            if module in self.graph.nodes:
                path = self.graph.nodes[module].get('path')
                if path:
                    affected_files.append(path)
        
        directly_affected = len(changed_modules)
        transitively_affected = len(affected) - len(changed_modules)
        total_affected = len(affected)
        blast_radius_factor = total_affected / directly_affected if directly_affected > 0 else 0.0
        
        return BlastRadiusResult(
            changed_files=changed_files,
            directly_affected=directly_affected,
            transitively_affected=transitively_affected,
            total_affected=total_affected,
            affected_files=sorted(affected_files),
            blast_radius_factor=blast_radius_factor
        )
    
    def get_dependents(self, file_path: str) -> List[str]:
        """
        Get all files that depend on this file.
        
        Args:
            file_path: File to analyze
            
        Returns:
            List of file paths that depend on this file
        """
        module = self._path_to_module(Path(file_path))
        
        if module not in self.graph:
            return []
        
        try:
            dependents = nx.descendants(self.graph, module)
        except nx.NetworkXError:
            return []
        
        # Convert to file paths
        dependent_files = []
        for dep in dependents:
            if dep in self.graph.nodes:
                path = self.graph.nodes[dep].get('path')
                if path:
                    dependent_files.append(path)
        
        return sorted(dependent_files)
    
    def get_dependencies(self, file_path: str) -> List[str]:
        """
        Get all files this file depends on.
        
        Args:
            file_path: File to analyze
            
        Returns:
            List of file paths this file depends on
        """
        module = self._path_to_module(Path(file_path))
        
        if module not in self.graph:
            return []
        
        try:
            dependencies = nx.ancestors(self.graph, module)
        except nx.NetworkXError:
            return []
        
        # Convert to file paths
        dependency_files = []
        for dep in dependencies:
            if dep in self.graph.nodes:
                path = self.graph.nodes[dep].get('path')
                if path:
                    dependency_files.append(path)
        
        return sorted(dependency_files)


def analyze_blast_radius(changed_files: List[str], repo_root: str = ".") -> BlastRadiusResult:
    """
    Convenience function to analyze blast radius.
    
    Args:
        changed_files: List of changed file paths
        repo_root: Repository root directory
        
    Returns:
        BlastRadiusResult with impact analysis
    """
    analyzer = DependencyAnalyzer(repo_root)
    return analyzer.calculate_blast_radius(changed_files)

