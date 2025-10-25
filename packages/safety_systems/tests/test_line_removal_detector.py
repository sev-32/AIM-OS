"""
Tests for the Line Removal Detection System

This module tests the comprehensive line removal detection functionality
to ensure it properly detects content loss and provides appropriate alerts.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from packages.safety_systems.line_removal_detector import (
    LineRemovalDetector, LineRemoval, ContentAnalysis, safe_modify_file
)


class TestLineRemovalDetector:
    """Test cases for the LineRemovalDetector class"""
    
    @pytest.fixture
    def detector(self):
        """Create a LineRemovalDetector instance for testing"""
        return LineRemovalDetector()
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("""# Test Document

This is a test document with multiple lines.

## Section 1

Some content here with **bold text** and *italic text*.

```python
def test_function():
    return "hello world"
```

### Subsection

- List item 1
- List item 2
- List item 3

## Section 2

More content with [a link](https://example.com) and file paths like `/path/to/file.py`.

End of document.
""")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_detector_initialization(self, detector):
        """Test that detector initializes correctly"""
        assert detector.config is not None
        assert detector.snapshots_dir.exists()
        assert detector.backups_dir.exists()
        assert detector.logs_dir.exists()
    
    def test_analyze_changes_no_content_loss(self, detector):
        """Test analysis when there's no significant content loss"""
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2\nLine 3\nLine 4"  # Adding content
        
        analysis = detector._analyze_changes(old_content, new_content, "test.md")
        
        assert analysis.file_path == "test.md"
        assert analysis.old_size == len(old_content)
        assert analysis.new_size == len(new_content)
        assert analysis.size_reduction < 0  # Negative means increase
        assert analysis.old_lines == 3
        assert analysis.new_lines == 4
        assert analysis.line_reduction < 0  # Negative means increase
        assert len(analysis.line_removals) == 0
        assert not analysis.content_loss_detected
        assert len(analysis.warnings) == 0
    
    def test_analyze_changes_significant_content_loss(self, detector):
        """Test analysis when there's significant content loss"""
        old_content = """# Test Document

This is a comprehensive test document with many lines.
It contains important information that should not be lost.

## Section 1

Important content here.

```python
def important_function():
    return "critical code"
```

## Section 2

More important content.

End of document.
"""
        new_content = "# Test Document\n\nShort content."
        
        analysis = detector._analyze_changes(old_content, new_content, "test.md")
        
        assert analysis.content_loss_detected
        assert analysis.size_reduction_percent > detector.config['size_reduction_threshold_percent']
        assert analysis.line_reduction_percent > detector.config['line_removal_threshold_percent']
        assert len(analysis.line_removals) > detector.config['line_removal_threshold']
        assert "Code blocks" in analysis.missing_elements
        assert len(analysis.warnings) > 0
    
    def test_detect_line_removals(self, detector):
        """Test detection of specific line removals"""
        old_content = "Line 1\nLine 2\nLine 3\nLine 4"
        new_content = "Line 1\nLine 3"  # Removed Line 2 and Line 4
        
        removals = detector._detect_line_removals(old_content, new_content)
        
        assert len(removals) == 2
        assert removals[0].content == "Line 2"
        assert removals[0].line_number == 2
        assert removals[1].content == "Line 4"
        assert removals[1].line_number == 4
    
    def test_detect_missing_elements(self, detector):
        """Test detection of missing key elements"""
        old_content = """# Header

**Bold text** and *italic text*.

```python
def test():
    pass
```

[A link](https://example.com)

/path/to/file.py
"""
        new_content = "Simple text without special elements."
        
        missing_elements = detector._detect_missing_elements(old_content, new_content)
        
        assert "Header sections" in missing_elements
        assert "Bold text" in missing_elements
        assert "Italic text" in missing_elements
        assert "Python code blocks" in missing_elements
        assert "URLs/links" in missing_elements
        assert "File paths" in missing_elements
    
    def test_calculate_line_importance(self, detector):
        """Test calculation of line importance scores"""
        # Code block should have high importance
        code_line = "```python"
        assert detector._calculate_line_importance(code_line) > 0.7
        
        # Header should have high importance
        header_line = "# Important Header"
        assert detector._calculate_line_importance(header_line) > 0.7
        
        # URL should have medium-high importance
        url_line = "https://example.com"
        assert detector._calculate_line_importance(url_line) > 0.5
        
        # File path should have medium importance
        path_line = "/path/to/file.py"
        assert detector._calculate_line_importance(path_line) > 0.4
        
        # Empty line should have low importance
        empty_line = ""
        assert detector._calculate_line_importance(empty_line) < 0.2
        
        # Regular text should have low importance
        text_line = "Regular text line"
        assert detector._calculate_line_importance(text_line) < 0.3
    
    def test_classify_line_type(self, detector):
        """Test classification of line types"""
        assert detector._classify_line_type("# Header") == "header"
        assert detector._classify_line_type("```python") == "code_block"
        assert detector._classify_line_type("- List item") == "list_item"
        assert detector._classify_line_type("https://example.com") == "link"
        assert detector._classify_line_type("/path/to/file.py") == "file_path"
        assert detector._classify_line_type("**Bold text**") == "formatted_text"
        assert detector._classify_line_type("") == "empty"
        assert detector._classify_line_type("Regular text") == "text"
    
    def test_get_line_context(self, detector):
        """Test getting context around a line"""
        lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        context = detector._get_line_context(lines, 2, 1)  # Context around Line 3
        
        assert "Line 2" in context
        assert ">>> 3:" in context  # Marked as the target line
        assert "Line 4" in context
    
    def test_merge_content(self, detector):
        """Test merging old and new content"""
        old_content = "Original content"
        new_content = "New content"
        
        merged = detector._merge_content(old_content, new_content)
        
        assert old_content in merged
        assert new_content in merged
        assert "New Content Added at" in merged
        assert "=" * 50 in merged
    
    def test_is_content_loss_detected(self, detector):
        """Test content loss detection logic"""
        # Test size reduction threshold
        assert detector._is_content_loss_detected(25.0, 0.0, [], [])
        
        # Test line reduction threshold
        assert detector._is_content_loss_detected(0.0, 25.0, [], [])
        
        # Test line removal count threshold
        removals = [LineRemoval(1, "line", "context", 0.5, "text")] * 6
        assert detector._is_content_loss_detected(0.0, 0.0, removals, [])
        
        # Test important removal count
        important_removals = [LineRemoval(1, "line", "context", 0.8, "text")] * 4
        assert detector._is_content_loss_detected(0.0, 0.0, important_removals, [])
        
        # Test missing elements
        assert detector._is_content_loss_detected(0.0, 0.0, [], ["Code blocks"])
        
        # Test no content loss
        assert not detector._is_content_loss_detected(5.0, 5.0, [], [])
    
    @patch('builtins.input', return_value='yes')
    def test_generate_content_loss_alert_yes(self, mock_input, detector):
        """Test content loss alert with 'yes' response"""
        analysis = ContentAnalysis(
            file_path="test.md",
            old_size=1000,
            new_size=500,
            size_reduction=500,
            size_reduction_percent=50.0,
            old_lines=50,
            new_lines=25,
            line_reduction=25,
            line_reduction_percent=50.0,
            line_removals=[LineRemoval(1, "test line", "context", 0.8, "text")],
            missing_elements=["Code blocks"],
            content_loss_detected=True,
            warnings=["Size reduction: 50.0%"],
            recommendations=["Create backup"]
        )
        
        response = detector._generate_content_loss_alert(analysis, "test")
        assert response == "yes"
    
    @patch('builtins.input', return_value='no')
    def test_generate_content_loss_alert_no(self, mock_input, detector):
        """Test content loss alert with 'no' response"""
        analysis = ContentAnalysis(
            file_path="test.md",
            old_size=1000,
            new_size=500,
            size_reduction=500,
            size_reduction_percent=50.0,
            old_lines=50,
            new_lines=25,
            line_reduction=25,
            line_reduction_percent=50.0,
            line_removals=[],
            missing_elements=[],
            content_loss_detected=True,
            warnings=[],
            recommendations=[]
        )
        
        response = detector._generate_content_loss_alert(analysis, "test")
        assert response == "no"
    
    @patch('builtins.input', side_effect=['invalid', 'merge'])
    def test_generate_content_loss_alert_invalid_then_valid(self, mock_input, detector):
        """Test content loss alert with invalid then valid response"""
        analysis = ContentAnalysis(
            file_path="test.md",
            old_size=1000,
            new_size=500,
            size_reduction=500,
            size_reduction_percent=50.0,
            old_lines=50,
            new_lines=25,
            line_reduction=25,
            line_reduction_percent=50.0,
            line_removals=[],
            missing_elements=[],
            content_loss_detected=True,
            warnings=[],
            recommendations=[]
        )
        
        response = detector._generate_content_loss_alert(analysis, "test")
        assert response == "merge"
    
    def test_safe_modify_file_new_file(self, detector):
        """Test safe modification of a new file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            temp_path = f.name
        
        try:
            new_content = "# New File\n\nThis is a new file."
            result = detector.safe_modify_file(temp_path, new_content, "create", "Creating new file")
            
            assert result
            with open(temp_path, 'r') as f:
                assert f.read() == new_content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('builtins.input', return_value='yes')
    def test_safe_modify_file_existing_file_approved(self, mock_input, detector, temp_file):
        """Test safe modification of existing file with approval"""
        new_content = "# Modified File\n\nShort content."
        result = detector.safe_modify_file(temp_file, new_content, "modify", "Modifying file")
        
        assert result
        with open(temp_file, 'r') as f:
            assert f.read() == new_content
    
    @patch('builtins.input', return_value='no')
    def test_safe_modify_file_existing_file_cancelled(self, mock_input, detector, temp_file):
        """Test safe modification of existing file with cancellation"""
        original_content = open(temp_file, 'r').read()
        new_content = "# Modified File\n\nShort content."
        
        result = detector.safe_modify_file(temp_file, new_content, "modify", "Modifying file")
        
        assert not result  # Should be cancelled
        with open(temp_file, 'r') as f:
            assert f.read() == original_content  # Content should be unchanged
    
    @patch('builtins.input', return_value='merge')
    def test_safe_modify_file_existing_file_merge(self, mock_input, detector, temp_file):
        """Test safe modification of existing file with merge"""
        new_content = "# Additional Content\n\nNew section."
        result = detector.safe_modify_file(temp_file, new_content, "modify", "Merging content")
        
        assert result
        with open(temp_file, 'r') as f:
            content = f.read()
            assert "Additional Content" in content
            assert "New Content Added at" in content


class TestConvenienceFunction:
    """Test cases for the convenience function"""
    
    def test_safe_modify_file_convenience_function(self):
        """Test the convenience function"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            temp_path = f.name
        
        try:
            new_content = "# Test\n\nContent."
            result = safe_modify_file(temp_path, new_content, "test", "Testing convenience function")
            
            assert result
            with open(temp_path, 'r') as f:
                assert f.read() == new_content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestConfiguration:
    """Test configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration"""
        detector = LineRemovalDetector()
        config = detector._default_config()
        
        assert 'size_reduction_threshold_percent' in config
        assert 'line_removal_threshold' in config
        assert 'line_removal_threshold_percent' in config
        assert 'importance_threshold' in config
        assert 'important_removal_count' in config
        assert 'backup_large_files_threshold' in config
        assert 'enable_automatic_backup' in config
        assert 'enable_snapshots' in config
        assert 'enable_logging' in config
    
    def test_custom_config(self):
        """Test custom configuration"""
        custom_config = {
            'size_reduction_threshold_percent': 10.0,
            'line_removal_threshold': 3,
            'enable_automatic_backup': False
        }
        
        detector = LineRemovalDetector(custom_config)
        
        assert detector.config['size_reduction_threshold_percent'] == 10.0
        assert detector.config['line_removal_threshold'] == 3
        assert detector.config['enable_automatic_backup'] == False
        # Should still have default values for other configs
        assert 'enable_snapshots' in detector.config


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_files(self):
        """Test handling of empty files"""
        detector = LineRemovalDetector()
        
        analysis = detector._analyze_changes("", "Some content")
        
        assert analysis.old_size == 0
        assert analysis.new_size == len("Some content")
        assert analysis.size_reduction_percent == 0  # Should handle division by zero
        assert not analysis.content_loss_detected
    
    def test_identical_content(self):
        """Test handling of identical content"""
        detector = LineRemovalDetector()
        content = "Identical content"
        
        analysis = detector._analyze_changes(content, content)
        
        assert analysis.size_reduction == 0
        assert analysis.line_reduction == 0
        assert len(analysis.line_removals) == 0
        assert not analysis.content_loss_detected
    
    def test_unicode_content(self):
        """Test handling of unicode content"""
        detector = LineRemovalDetector()
        
        old_content = "Line with émojis 🚀 and spécial characters"
        new_content = "Different content with 中文 and русский"
        
        analysis = detector._analyze_changes(old_content, new_content)
        
        assert analysis.old_size == len(old_content)
        assert analysis.new_size == len(new_content)
        assert len(analysis.line_removals) == 1
    
    def test_large_content(self):
        """Test handling of large content"""
        detector = LineRemovalDetector()
        
        old_content = "Line\n" * 1000  # 1000 lines
        new_content = "Line\n" * 500   # 500 lines
        
        analysis = detector._analyze_changes(old_content, new_content)
        
        assert analysis.old_lines == 1000
        assert analysis.new_lines == 500
        assert analysis.line_reduction == 500
        assert analysis.content_loss_detected


if __name__ == "__main__":
    pytest.main([__file__])
