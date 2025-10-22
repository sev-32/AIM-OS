"""Tests for quartet detection"""

import pytest
from pathlib import Path

from sdfcvf.quartet import (
    Quartet,
    QuartetDetector,
    FileClassification,
    extract_module_name,
)


def test_quartet_creation():
    """Test creating a quartet"""
    quartet = Quartet(
        code_files=["src/feature.py"],
        doc_files=["docs/feature.md"],
        test_files=["tests/test_feature.py"],
        trace_files=["audit/feature.md"]
    )
    
    assert len(quartet.code_files) == 1
    assert len(quartet.doc_files) == 1
    assert len(quartet.test_files) == 1
    assert len(quartet.trace_files) == 1


def test_quartet_completeness():
    """Test quartet completeness checking"""
    # Complete quartet
    complete = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"]
    )
    assert complete.is_complete() is True
    assert complete.missing_elements() == []
    
    # Incomplete quartet
    incomplete = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        # No tests or traces
    )
    assert incomplete.is_complete() is False
    assert "tests" in incomplete.missing_elements()
    assert "traces" in incomplete.missing_elements()


def test_quartet_element_checks():
    """Test individual element presence checks"""
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
    )
    
    assert quartet.has_code() is True
    assert quartet.has_docs() is True
    assert quartet.has_tests() is False
    assert quartet.has_traces() is False


def test_quartet_all_files():
    """Test getting all files from quartet"""
    quartet = Quartet(
        code_files=["a.py", "b.py"],
        doc_files=["c.md"],
        test_files=["test.py"],
        trace_files=["trace.md"]
    )
    
    all_files = quartet.all_files()
    assert len(all_files) == 5
    assert "a.py" in all_files
    assert "trace.md" in all_files


def test_quartet_file_count():
    """Test file count"""
    quartet = Quartet(
        code_files=["a.py", "b.py", "c.py"],
        doc_files=["d.md"],
        test_files=["test.py"],
    )
    
    assert quartet.file_count() == 5


def test_quartet_to_dict():
    """Test quartet serialization"""
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"]
    )
    
    data = quartet.to_dict()
    
    assert data["code"] == ["code.py"]
    assert data["complete"] is True
    assert data["missing"] == []


def test_detector_initialization():
    """Test QuartetDetector initialization"""
    detector = QuartetDetector()
    assert detector.repo_root == Path(".")


def test_classify_code_file():
    """Test code file classification"""
    detector = QuartetDetector()
    
    assert detector.classify_file("packages/vif/witness.py") == FileClassification.CODE
    assert detector.classify_file("src/main.py") == FileClassification.CODE
    assert detector.classify_file("lib/utils.js") == FileClassification.CODE


def test_classify_test_file():
    """Test test file classification"""
    detector = QuartetDetector()
    
    assert detector.classify_file("tests/test_feature.py") == FileClassification.TESTS
    assert detector.classify_file("packages/vif/tests/test_witness.py") == FileClassification.TESTS
    assert detector.classify_file("spec/feature.spec.js") == FileClassification.TESTS


def test_classify_doc_file():
    """Test documentation file classification"""
    detector = QuartetDetector()
    
    assert detector.classify_file("docs/guide.md") == FileClassification.DOCS
    assert detector.classify_file("README.md") == FileClassification.DOCS
    assert detector.classify_file("knowledge_architecture/systems/vif/L3_detailed.md") == FileClassification.DOCS


def test_classify_trace_file():
    """Test trace file classification"""
    detector = QuartetDetector()
    
    assert detector.classify_file("audit/decision_log.md") == FileClassification.TRACES
    assert detector.classify_file("logs/system.log") == FileClassification.TRACES
    assert detector.classify_file("knowledge_architecture/AETHER_MEMORY/decision_logs/dec-001.md") == FileClassification.TRACES


def test_classify_unknown_file():
    """Test unknown file classification"""
    detector = QuartetDetector()
    
    classification = detector.classify_file("image.png")
    assert classification == FileClassification.UNKNOWN


def test_detect_from_changes():
    """Test detecting quartet from changed files"""
    detector = QuartetDetector()
    
    changes = [
        "packages/vif/witness.py",              # CODE
        "packages/vif/tests/test_witness.py",   # TESTS
        "knowledge_architecture/systems/vif/L3_detailed.md",  # DOCS
        "knowledge_architecture/AETHER_MEMORY/decision_logs/dec-006.md",  # TRACES
        "image.png",                            # UNKNOWN (ignored)
    ]
    
    quartet = detector.detect_from_changes(changes)
    
    assert len(quartet.code_files) == 1
    assert len(quartet.test_files) == 1
    assert len(quartet.doc_files) == 1
    assert len(quartet.trace_files) == 1
    assert quartet.is_complete()


def test_validate_quartet_complete():
    """Test validation of complete quartet"""
    detector = QuartetDetector()
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"]
    )
    
    warnings = detector.validate_quartet(quartet)
    assert len(warnings) == 0


def test_validate_quartet_incomplete():
    """Test validation of incomplete quartet"""
    detector = QuartetDetector()
    
    quartet = Quartet(
        code_files=["code.py"],
        # Missing docs, tests, traces
    )
    
    warnings = detector.validate_quartet(quartet)
    assert len(warnings) == 3  # Missing docs, tests, traces


def test_extract_module_name():
    """Test module name extraction"""
    assert extract_module_name("packages/vif/witness.py") == "vif"
    assert extract_module_name("packages/hhni/retrieval.py") == "hhni"
    assert extract_module_name("packages/sdfcvf/quartet.py") == "sdfcvf"


def test_extract_module_name_no_packages():
    """Test module extraction from non-packages path"""
    result = extract_module_name("src/main.py")
    assert result is None  # No packages/ in path


def test_realistic_vif_changes():
    """Test realistic VIF implementation changes"""
    detector = QuartetDetector()
    
    # Simulate VIF implementation changes from this session
    changes = [
        "packages/vif/witness.py",
        "packages/vif/confidence_extraction.py",
        "packages/vif/calibration.py",
        "packages/vif/kappa_gate.py",
        "packages/vif/tests/test_witness_schema.py",
        "packages/vif/tests/test_confidence_extraction.py",
        "packages/vif/tests/test_calibration.py",
        "knowledge_architecture/systems/vif/L3_detailed.md",
        "knowledge_architecture/AETHER_MEMORY/decision_logs/dec-006_vif_schema_success.md",
    ]
    
    quartet = detector.detect_from_changes(changes)
    
    assert len(quartet.code_files) == 4  # witness, extraction, calibration, kappa_gate
    assert len(quartet.test_files) == 3  # 3 test files
    assert len(quartet.doc_files) == 1   # L3_detailed
    assert len(quartet.trace_files) == 1  # decision log
    assert quartet.is_complete()


def test_code_vs_test_distinction():
    """Test that code and test files are properly distinguished"""
    detector = QuartetDetector()
    
    # Source code should NOT be classified as test
    assert detector.classify_file("packages/vif/witness.py") == FileClassification.CODE
    
    # Test should be TEST not CODE
    assert detector.classify_file("packages/vif/tests/test_witness.py") == FileClassification.TESTS
    
    # Test in name but not in tests/ dir - still test
    assert detector.classify_file("test_utils.py") == FileClassification.TESTS

