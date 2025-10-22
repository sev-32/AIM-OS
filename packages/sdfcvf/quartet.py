"""Quartet Detection - Identify code/docs/tests/traces that should evolve together"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Optional
from enum import Enum


class FileClassification(str, Enum):
    """Classification of file types in quartet"""
    CODE = "code"
    DOCS = "docs"
    TESTS = "tests"
    TRACES = "traces"
    UNKNOWN = "unknown"


@dataclass
class Quartet:
    """A quartet of related artifacts that should evolve together
    
    Attributes:
        code_files: Source code files
        doc_files: Documentation files
        test_files: Test files
        trace_files: Audit/log/trace files
    
    Examples:
        >>> quartet = Quartet(
        ...     code_files=["packages/vif/witness.py"],
        ...     doc_files=["knowledge_architecture/systems/vif/L3_detailed.md"],
        ...     test_files=["packages/vif/tests/test_witness.py"],
        ...     trace_files=["audit/vif_witness_usage.md"]
        ... )
        >>> quartet.is_complete()
        True
    """
    code_files: List[str] = field(default_factory=list)
    doc_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    trace_files: List[str] = field(default_factory=list)
    
    def is_complete(self) -> bool:
        """Check if quartet has all 4 elements"""
        return (
            len(self.code_files) > 0 and
            len(self.doc_files) > 0 and
            len(self.test_files) > 0 and
            len(self.trace_files) > 0
        )
    
    def has_code(self) -> bool:
        """Check if has code"""
        return len(self.code_files) > 0
    
    def has_docs(self) -> bool:
        """Check if has documentation"""
        return len(self.doc_files) > 0
    
    def has_tests(self) -> bool:
        """Check if has tests"""
        return len(self.test_files) > 0
    
    def has_traces(self) -> bool:
        """Check if has traces"""
        return len(self.trace_files) > 0
    
    def missing_elements(self) -> List[str]:
        """Get list of missing quartet elements"""
        missing = []
        if not self.has_code():
            missing.append("code")
        if not self.has_docs():
            missing.append("docs")
        if not self.has_tests():
            missing.append("tests")
        if not self.has_traces():
            missing.append("traces")
        return missing
    
    def all_files(self) -> List[str]:
        """Get all files in quartet"""
        return (
            self.code_files +
            self.doc_files +
            self.test_files +
            self.trace_files
        )
    
    def file_count(self) -> int:
        """Total number of files"""
        return len(self.all_files())
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "code": self.code_files,
            "docs": self.doc_files,
            "tests": self.test_files,
            "traces": self.trace_files,
            "complete": self.is_complete(),
            "missing": self.missing_elements(),
        }


class QuartetDetector:
    """Detect quartet elements from file changes
    
    Given a set of changed files, classifies them into quartet categories
    and identifies which quartets are affected.
    
    Examples:
        >>> detector = QuartetDetector()
        >>> changes = [
        ...     "packages/vif/witness.py",
        ...     "packages/vif/tests/test_witness.py",
        ...     "knowledge_architecture/systems/vif/L3_detailed.md"
        ... ]
        >>> quartet = detector.detect_from_changes(changes)
        >>> assert quartet.has_code()
        >>> assert quartet.has_tests()
        >>> assert quartet.has_docs()
    """
    
    def __init__(self, repo_root: Optional[str] = None):
        """Initialize detector
        
        Args:
            repo_root: Repository root path (defaults to current dir)
        """
        self.repo_root = Path(repo_root) if repo_root else Path(".")
    
    def classify_file(self, filepath: str) -> FileClassification:
        """Classify a file into quartet category
        
        Args:
            filepath: Path to file
            
        Returns:
            FileClassification (CODE, DOCS, TESTS, TRACES, UNKNOWN)
        """
        path = Path(filepath)
        path_str = str(path).lower()
        
        # Check in order of specificity:
        # 1. Tests (most specific patterns)
        if self._is_test_file(path, path_str):
            return FileClassification.TESTS
        
        # 2. Traces (check before docs - audit/ coordination/ can have .md)
        if self._is_trace_file(path, path_str):
            return FileClassification.TRACES
        
        # 3. Code (specific extensions + not test)
        if self._is_code_file(path, path_str):
            return FileClassification.CODE
        
        # 4. Documentation (last - catch-all for .md files)
        if self._is_doc_file(path, path_str):
            return FileClassification.DOCS
        
        return FileClassification.UNKNOWN
    
    def _is_test_file(self, path: Path, path_str: str) -> bool:
        """Check if file is a test"""
        # Test patterns
        test_indicators = [
            'test_',           # test_feature.py
            '_test',           # feature_test.py
            '.test.',          # feature.test.js
            'tests/',          # in tests/ directory
            '/test/',          # /test/ directory
            'spec/',           # spec/ directory
            '.spec.',          # feature.spec.ts
        ]
        
        return any(indicator in path_str for indicator in test_indicators)
    
    def _is_code_file(self, path: Path, path_str: str) -> bool:
        """Check if file is source code"""
        # Code extensions
        code_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.cpp', '.c', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.swift',
            '.kt', '.scala', '.clj', '.ex', '.exs'
        }
        
        # Must have code extension
        if path.suffix not in code_extensions:
            return False
        
        # Must NOT be in test directory
        if self._is_test_file(path, path_str):
            return False
        
        # Code is typically in src/, lib/, packages/
        code_indicators = ['src/', 'lib/', 'packages/', 'app/']
        if any(ind in path_str for ind in code_indicators):
            return True
        
        # Default: if has code extension and not test, it's code
        return True
    
    def _is_doc_file(self, path: Path, path_str: str) -> bool:
        """Check if file is documentation"""
        # Doc extensions
        doc_extensions = {'.md', '.rst', '.txt', '.adoc', '.docx'}
        
        # Doc directories (but NOT trace directories)
        doc_directories = [
            'docs/',
            'documentation/',
            'knowledge_architecture/systems/',  # More specific
            'readme',
            'doc/',
        ]
        
        # Check if in doc-specific directory
        in_doc_directory = any(doc_dir in path_str for doc_dir in doc_directories)
        if in_doc_directory:
            return True
        
        # Otherwise, only classify as doc if has doc extension AND not already classified
        # (This is checked last in classify_file, so traces/code/tests already handled)
        return path.suffix in doc_extensions
    
    def _is_trace_file(self, path: Path, path_str: str) -> bool:
        """Check if file is trace/audit/log"""
        # Trace directory indicators
        trace_directories = [
            'audit/',
            'coordination/',
            'evidence/',
            'logs/',
            'trace/',
            'aether_memory/',
        ]
        
        # Trace file patterns
        trace_patterns = [
            '.log',
            'decision_log',
            'audit_',
            'witness_usage',  # But not just "witness" alone
        ]
        
        # Check directories first
        if any(trace_dir in path_str for trace_dir in trace_directories):
            return True
        
        # Check file patterns
        if any(pattern in path_str for pattern in trace_patterns):
            return True
        
        return False
    
    def detect_from_changes(self, changed_files: List[str]) -> Quartet:
        """Detect quartet from list of changed files
        
        Args:
            changed_files: List of file paths
            
        Returns:
            Quartet with files classified into categories
        """
        quartet = Quartet()
        
        for filepath in changed_files:
            classification = self.classify_file(filepath)
            
            if classification == FileClassification.CODE:
                quartet.code_files.append(filepath)
            elif classification == FileClassification.DOCS:
                quartet.doc_files.append(filepath)
            elif classification == FileClassification.TESTS:
                quartet.test_files.append(filepath)
            elif classification == FileClassification.TRACES:
                quartet.trace_files.append(filepath)
            # UNKNOWN files are ignored
        
        return quartet
    
    def detect_related_quartet(self, focal_file: str) -> Quartet:
        """Detect related quartet elements for a focal file
        
        Given a file (e.g., packages/vif/witness.py), find its related:
        - Documentation (knowledge_architecture/systems/vif/*)
        - Tests (packages/vif/tests/test_witness.py)
        - Traces (audit/vif_usage.md)
        
        Args:
            focal_file: File to find quartet for
            
        Returns:
            Quartet with related files
        """
        # This is complex - would use heuristics:
        # - Extract module name from path
        # - Find docs mentioning module
        # - Find tests for module
        # - Find traces referencing module
        
        # For now, placeholder
        raise NotImplementedError("Related quartet detection requires path analysis")
    
    def validate_quartet(self, quartet: Quartet) -> List[str]:
        """Validate quartet completeness
        
        Args:
            quartet: Quartet to validate
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        if not quartet.has_code():
            warnings.append("No code files in quartet")
        
        if not quartet.has_docs():
            warnings.append("No documentation for code changes")
        
        if not quartet.has_tests():
            warnings.append("No tests for code changes")
        
        if not quartet.has_traces():
            warnings.append("No audit/trace files for changes")
        
        return warnings


def extract_module_name(filepath: str) -> Optional[str]:
    """Extract module/component name from filepath
    
    Args:
        filepath: Path to file
        
    Returns:
        Module name or None
        
    Examples:
        >>> extract_module_name("packages/vif/witness.py")
        'vif'
        >>> extract_module_name("packages/hhni/retrieval.py")
        'hhni'
    """
    path = Path(filepath)
    
    # For packages/* structure
    parts = path.parts
    if 'packages' in parts:
        idx = parts.index('packages')
        if len(parts) > idx + 1:
            return parts[idx + 1]
    
    return None

