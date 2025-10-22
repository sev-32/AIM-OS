"""Parity Calculation - Measure quartet alignment

Parity score indicates how well quartet elements align:
- 1.0: Perfect alignment (code, docs, tests, traces all consistent)
- 0.95+: Excellent alignment
- 0.90+: Good alignment
- <0.90: Poor alignment (gate should block)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import math


@dataclass
class ParityResult:
    """Result of parity calculation
    
    Attributes:
        parity_score: Overall alignment (0.0-1.0)
        code_docs_similarity: How well code aligns with docs
        code_tests_similarity: How well code aligns with tests
        code_traces_similarity: How well code aligns with traces
        complete: Whether quartet has all 4 elements
        warnings: List of parity warnings
    """
    parity_score: float
    code_docs_similarity: float
    code_tests_similarity: float
    code_traces_similarity: float
    complete: bool
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    def passes_gate(self, threshold: float = 0.90) -> bool:
        """Check if parity passes gate threshold
        
        Args:
            threshold: Minimum parity score to pass
            
        Returns:
            True if parity >= threshold
        """
        return self.parity_score >= threshold
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "parity_score": self.parity_score,
            "code_docs_similarity": self.code_docs_similarity,
            "code_tests_similarity": self.code_tests_similarity,
            "code_traces_similarity": self.code_traces_similarity,
            "complete": self.complete,
            "warnings": self.warnings,
            "passes_gate_90": self.passes_gate(0.90),
            "passes_gate_95": self.passes_gate(0.95),
        }


class ParityCalculator:
    """Calculate parity score for a quartet
    
    Uses embedding similarity to measure alignment between quartet elements.
    
    Examples:
        >>> from sdfcvf import Quartet, ParityCalculator
        >>> 
        >>> quartet = Quartet(
        ...     code_files=["packages/vif/witness.py"],
        ...     doc_files=["knowledge_architecture/systems/vif/L3_detailed.md"],
        ...     test_files=["packages/vif/tests/test_witness.py"],
        ...     trace_files=["audit/vif_witness_usage.md"]
        ... )
        >>> 
        >>> calculator = ParityCalculator()
        >>> result = calculator.calculate(quartet)
        >>> 
        >>> print(f"Parity: {result.parity_score:.2f}")
        >>> print(f"Passes gate: {result.passes_gate(0.90)}")
    """
    
    def __init__(self, embedding_fn: Optional[callable] = None, repo_root: Optional[str] = None):
        """Initialize parity calculator
        
        Args:
            embedding_fn: Function to generate embeddings (text -> vector)
                         If None, uses simple fallback
            repo_root: Repository root path (defaults to current directory)
        """
        self.embedding_fn = embedding_fn or self._fallback_embedding
        self.repo_root = Path(repo_root) if repo_root else Path(".")
    
    def calculate(self, quartet: Quartet) -> ParityResult:
        """Calculate parity score for quartet
        
        Args:
            quartet: Quartet to calculate parity for
            
        Returns:
            ParityResult with score and details
        """
        # Check completeness
        complete = quartet.is_complete()
        warnings = []
        
        if not complete:
            missing = quartet.missing_elements()
            warnings.append(f"Incomplete quartet: missing {', '.join(missing)}")
        
        # If quartet incomplete, parity is low
        if not complete:
            return ParityResult(
                parity_score=0.50,  # Incomplete = low parity
                code_docs_similarity=0.0,
                code_tests_similarity=0.0,
                code_traces_similarity=0.0,
                complete=False,
                warnings=warnings,
            )
        
        # Generate embeddings for each element
        code_emb = self._embed_files(quartet.code_files)
        docs_emb = self._embed_files(quartet.doc_files)
        tests_emb = self._embed_files(quartet.test_files)
        traces_emb = self._embed_files(quartet.trace_files)
        
        # Calculate pairwise similarities
        code_docs_sim = self._cosine_similarity(code_emb, docs_emb)
        code_tests_sim = self._cosine_similarity(code_emb, tests_emb)
        code_traces_sim = self._cosine_similarity(code_emb, traces_emb)
        
        # Calculate overall parity (average of similarities)
        parity = (code_docs_sim + code_tests_sim + code_traces_sim) / 3.0
        
        # Add warnings for low similarities
        if code_docs_sim < 0.85:
            warnings.append(f"Low code-docs alignment: {code_docs_sim:.2f}")
        if code_tests_sim < 0.85:
            warnings.append(f"Low code-tests alignment: {code_tests_sim:.2f}")
        if code_traces_sim < 0.70:  # Traces can be less similar
            warnings.append(f"Low code-traces alignment: {code_traces_sim:.2f}")
        
        return ParityResult(
            parity_score=parity,
            code_docs_similarity=code_docs_sim,
            code_tests_similarity=code_tests_sim,
            code_traces_similarity=code_traces_sim,
            complete=True,
            warnings=warnings,
        )
    
    def _embed_files(self, filepaths: List[str]) -> List[float]:
        """Generate aggregate embedding for list of files
        
        Args:
            filepaths: List of file paths
            
        Returns:
            Aggregate embedding vector
        """
        if not filepaths:
            return [0.0] * 3  # Empty embedding
        
        # Read files and concatenate content
        combined_text = ""
        for filepath in filepaths:
            try:
                # Handle both relative and absolute paths
                path = Path(filepath)
                if not path.is_absolute():
                    path = self.repo_root / path
                
                if path.exists():
                    combined_text += path.read_text(encoding='utf-8', errors='ignore')
                    combined_text += "\n"
            except Exception:
                # Skip files that can't be read
                pass
        
        if not combined_text.strip():
            return [0.0] * 3
        
        # Generate embedding
        return self.embedding_fn(combined_text)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not vec1 or not vec2:
            return 0.0
        
        # Ensure same length
        min_len = min(len(vec1), len(vec2))
        v1 = vec1[:min_len]
        v2 = vec2[:min_len]
        
        # Calculate dot product
        dot = sum(a * b for a, b in zip(v1, v2))
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = dot / (mag1 * mag2)
        
        # Clamp to [0, 1] (should be in [-1, 1], but we want 0-1)
        return max(0.0, min(1.0, (similarity + 1.0) / 2.0))
    
    def _fallback_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding using character statistics
        
        Args:
            text: Text to embed
            
        Returns:
            3-dimensional embedding vector
        """
        text = text.strip()
        if not text:
            return [0.0, 0.0, 0.0]
        
        # Simple character statistics
        codes = [ord(ch) for ch in text[:1000]]  # First 1000 chars
        total = sum(codes)
        length = len(codes)
        avg = total / length if length > 0 else 0
        variance = sum((c - avg) ** 2 for c in codes) / length if length > 0 else 0
        
        return [float(total), float(avg), float(variance)]


def calculate_parity(
    code_files: List[str],
    doc_files: List[str],
    test_files: List[str],
    trace_files: List[str],
    *,
    embedding_fn: Optional[callable] = None,
) -> ParityResult:
    """Convenience function to calculate parity
    
    Args:
        code_files: List of code file paths
        doc_files: List of doc file paths
        test_files: List of test file paths
        trace_files: List of trace file paths
        embedding_fn: Optional custom embedding function
        
    Returns:
        ParityResult
        
    Examples:
        >>> result = calculate_parity(
        ...     code_files=["src/feature.py"],
        ...     doc_files=["docs/feature.md"],
        ...     test_files=["tests/test_feature.py"],
        ...     trace_files=["audit/feature_usage.md"]
        ... )
        >>> assert result.parity_score > 0.0
    """
    from .quartet import Quartet
    
    quartet = Quartet(
        code_files=code_files,
        doc_files=doc_files,
        test_files=test_files,
        trace_files=trace_files,
    )
    
    calculator = ParityCalculator(embedding_fn=embedding_fn)
    return calculator.calculate(quartet)


def weighted_parity(
    parity_result: ParityResult,
    *,
    docs_weight: float = 0.40,
    tests_weight: float = 0.40,
    traces_weight: float = 0.20,
) -> float:
    """Calculate weighted parity score
    
    Different elements can have different importance:
    - Docs + Tests usually most critical (80%)
    - Traces less critical (20%)
    
    Args:
        parity_result: Result from parity calculation
        docs_weight: Weight for code-docs similarity
        tests_weight: Weight for code-tests similarity
        traces_weight: Weight for code-traces similarity
        
    Returns:
        Weighted parity score
    """
    weighted = (
        (parity_result.code_docs_similarity * docs_weight) +
        (parity_result.code_tests_similarity * tests_weight) +
        (parity_result.code_traces_similarity * traces_weight)
    )
    
    return max(0.0, min(1.0, weighted))

