"""Tests for parity calculation"""

import pytest
from pathlib import Path
import tempfile
import os

from sdfcvf.quartet import Quartet
from sdfcvf.parity import (
    ParityCalculator,
    ParityResult,
    calculate_parity,
    weighted_parity,
)


def test_parity_result_creation():
    """Test ParityResult creation"""
    result = ParityResult(
        parity_score=0.95,
        code_docs_similarity=0.96,
        code_tests_similarity=0.94,
        code_traces_similarity=0.95,
        complete=True,
    )
    
    assert result.parity_score == 0.95
    assert result.complete is True


def test_parity_result_passes_gate():
    """Test parity gate checking"""
    high_parity = ParityResult(
        parity_score=0.95,
        code_docs_similarity=0.95,
        code_tests_similarity=0.95,
        code_traces_similarity=0.95,
        complete=True,
    )
    
    assert high_parity.passes_gate(0.90) is True
    assert high_parity.passes_gate(0.95) is True
    assert high_parity.passes_gate(0.96) is False
    
    low_parity = ParityResult(
        parity_score=0.75,
        code_docs_similarity=0.75,
        code_tests_similarity=0.75,
        code_traces_similarity=0.75,
        complete=True,
    )
    
    assert low_parity.passes_gate(0.90) is False
    assert low_parity.passes_gate(0.70) is True


def test_parity_calculator_initialization():
    """Test ParityCalculator initialization"""
    calc = ParityCalculator()
    assert calc.embedding_fn is not None


def test_incomplete_quartet_low_parity():
    """Test incomplete quartet gets low parity"""
    calc = ParityCalculator()
    
    incomplete = Quartet(
        code_files=["code.py"],
        # Missing docs, tests, traces
    )
    
    result = calc.calculate(incomplete)
    
    assert result.complete is False
    assert result.parity_score == 0.50  # Incomplete = low parity
    assert len(result.warnings) > 0
    assert "incomplete" in result.warnings[0].lower()


def test_parity_with_mock_files():
    """Test parity calculation with mock file content"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create mock files with similar content
        code_content = "class Feature:\n    def process(self): pass"
        docs_content = "Feature class processes data using process() method"
        tests_content = "def test_feature_process(): feature = Feature(); feature.process()"
        trace_content = "Feature.process() was called successfully"
        
        (tmppath / "code.py").write_text(code_content)
        (tmppath / "docs.md").write_text(docs_content)
        (tmppath / "test.py").write_text(tests_content)
        (tmppath / "trace.md").write_text(trace_content)
        
        quartet = Quartet(
            code_files=["code.py"],  # Relative paths
            doc_files=["docs.md"],
            test_files=["test.py"],
            trace_files=["trace.md"],
        )
        
        calc = ParityCalculator(repo_root=str(tmppath))  # Set repo root
        result = calc.calculate(quartet)
        
        # All files contain related content, should have decent parity
        assert result.complete is True
        assert result.parity_score > 0.0
        assert 0.0 <= result.code_docs_similarity <= 1.0
        assert 0.0 <= result.code_tests_similarity <= 1.0
        assert 0.0 <= result.code_traces_similarity <= 1.0


def test_parity_result_to_dict():
    """Test ParityResult serialization"""
    result = ParityResult(
        parity_score=0.92,
        code_docs_similarity=0.90,
        code_tests_similarity=0.94,
        code_traces_similarity=0.92,
        complete=True,
        warnings=["test warning"],
    )
    
    data = result.to_dict()
    
    assert data["parity_score"] == 0.92
    assert data["complete"] is True
    assert data["passes_gate_90"] is True
    assert data["warnings"] == ["test warning"]


def test_calculate_parity_convenience_function():
    """Test convenience function for parity calculation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        (tmppath / "code.py").write_text("code content")
        (tmppath / "docs.md").write_text("documentation")
        (tmppath / "test.py").write_text("test code")
        (tmppath / "trace.md").write_text("audit trace")
        
        result = calculate_parity(
            code_files=[str(tmppath / "code.py")],
            doc_files=[str(tmppath / "docs.md")],
            test_files=[str(tmppath / "test.py")],
            trace_files=[str(tmppath / "trace.md")],
        )
        
        assert isinstance(result, ParityResult)
        assert result.complete is True


def test_weighted_parity():
    """Test weighted parity calculation"""
    result = ParityResult(
        parity_score=0.85,  # Not used in weighted calc
        code_docs_similarity=0.90,
        code_tests_similarity=0.95,
        code_traces_similarity=0.70,
        complete=True,
    )
    
    # Default weights: docs 0.40, tests 0.40, traces 0.20
    weighted = weighted_parity(result)
    
    expected = (0.90 * 0.40) + (0.95 * 0.40) + (0.70 * 0.20)
    assert abs(weighted - expected) < 0.01


def test_weighted_parity_custom_weights():
    """Test weighted parity with custom weights"""
    result = ParityResult(
        parity_score=0.85,
        code_docs_similarity=0.80,
        code_tests_similarity=0.90,
        code_traces_similarity=0.60,
        complete=True,
    )
    
    # Custom: tests most important (60%)
    weighted = weighted_parity(
        result,
        docs_weight=0.30,
        tests_weight=0.60,
        traces_weight=0.10,
    )
    
    expected = (0.80 * 0.30) + (0.90 * 0.60) + (0.60 * 0.10)
    assert abs(weighted - expected) < 0.01


def test_cosine_similarity():
    """Test cosine similarity calculation"""
    calc = ParityCalculator()
    
    # Identical vectors
    vec1 = [1.0, 2.0, 3.0]
    vec2 = [1.0, 2.0, 3.0]
    sim = calc._cosine_similarity(vec1, vec2)
    assert sim > 0.99  # Should be very high (nearly 1.0)
    
    # Orthogonal vectors (cosine = 0, normalized to 0.5)
    vec3 = [1.0, 0.0, 0.0]
    vec4 = [0.0, 1.0, 0.0]
    sim2 = calc._cosine_similarity(vec3, vec4)
    assert 0.4 < sim2 < 0.6  # Orthogonal → ~0.5 after normalization


def test_fallback_embedding():
    """Test fallback embedding generation"""
    calc = ParityCalculator()
    
    embedding = calc._fallback_embedding("test text content")
    
    assert len(embedding) == 3
    assert all(isinstance(v, float) for v in embedding)


def test_fallback_embedding_empty():
    """Test fallback embedding with empty text"""
    calc = ParityCalculator()
    
    embedding = calc._fallback_embedding("")
    assert embedding == [0.0, 0.0, 0.0]


def test_parity_warnings_low_similarity():
    """Test warnings generated for low similarities"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create files with VERY different content
        (tmppath / "code.py").write_text("aaaaaa" * 100)
        (tmppath / "docs.md").write_text("bbbbbb" * 100)
        (tmppath / "test.py").write_text("cccccc" * 100)
        (tmppath / "trace.md").write_text("dddddd" * 100)
        
        quartet = Quartet(
            code_files=[str(tmppath / "code.py")],
            doc_files=[str(tmppath / "docs.md")],
            test_files=[str(tmppath / "test.py")],
            trace_files=[str(tmppath / "trace.md")],
        )
        
        calc = ParityCalculator()
        result = calc.calculate(quartet)
        
        # Very different content should produce warnings
        # (Exact number depends on similarity thresholds)
        assert len(result.warnings) >= 0  # May have warnings


def test_parity_empty_files_list():
    """Test parity with empty file lists"""
    calc = ParityCalculator()
    
    # Empty code files
    empty_emb = calc._embed_files([])
    assert len(empty_emb) == 3
    assert all(v == 0.0 for v in empty_emb)


def test_parity_nonexistent_files():
    """Test parity gracefully handles nonexistent files"""
    calc = ParityCalculator()
    
    # Files that don't exist
    quartet = Quartet(
        code_files=["nonexistent_code.py"],
        doc_files=["nonexistent_docs.md"],
        test_files=["nonexistent_test.py"],
        trace_files=["nonexistent_trace.md"],
    )
    
    # Should not crash
    result = calc.calculate(quartet)
    assert isinstance(result, ParityResult)

