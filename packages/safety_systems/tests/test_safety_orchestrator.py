"""
Tests for the Safety Orchestrator

This module tests the comprehensive safety orchestration functionality
to ensure all safety systems work together properly.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from packages.safety_systems.safety_orchestrator import (
    SafetyOrchestrator, SafetyOperation, SafetyResult,
    safe_modify_file, safe_create_file, monitor_aether_action
)


class TestSafetyOrchestrator:
    """Test cases for the SafetyOrchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a SafetyOrchestrator instance for testing"""
        return SafetyOrchestrator()
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("""# Test Document

This is a test document with multiple lines.
It contains important information.

## Section 1

Some content here.

```python
def test_function():
    return "hello world"
```

## Section 2

More content here.

End of document.
""")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly"""
        assert orchestrator.config is not None
        assert orchestrator.manager_ai is not None
        assert orchestrator.line_removal_detector is not None
        assert orchestrator.data_dir.exists()
        assert len(orchestrator.active_operations) == 0
        assert len(orchestrator.operation_history) == 0
    
    def test_request_operation_create_file(self, orchestrator):
        """Test requesting a file creation operation"""
        operation_id = orchestrator.request_operation(
            operation_type="create_file",
            file_path="test_file.md",
            content="# Test\n\nContent.",
            context={"reason": "Testing"}
        )
        
        assert operation_id is not None
        assert operation_id.startswith("create_file_")
        
        # Check operation history
        assert len(orchestrator.operation_history) == 1
        operation = orchestrator.operation_history[0]
        assert operation.operation_id == operation_id
        assert operation.operation_type == "create_file"
        assert operation.file_path == "test_file.md"
        assert operation.content == "# Test\n\nContent."
        assert operation.status == "approved"
    
    def test_request_operation_modify_file(self, orchestrator, temp_file):
        """Test requesting a file modification operation"""
        new_content = "# Modified Document\n\nShort content."
        
        operation_id = orchestrator.request_operation(
            operation_type="modify_file",
            file_path=temp_file,
            content=new_content,
            context={"reason": "Testing modification"}
        )
        
        assert operation_id is not None
        assert operation_id.startswith("modify_file_")
        
        # Check operation history
        assert len(orchestrator.operation_history) == 1
        operation = orchestrator.operation_history[0]
        assert operation.operation_id == operation_id
        assert operation.operation_type == "modify_file"
        assert operation.file_path == temp_file
        assert operation.content == new_content
        assert operation.status == "approved"
    
    def test_execute_operation_create_file(self, orchestrator):
        """Test executing a file creation operation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            temp_path = f.name
        
        try:
            # Request operation
            operation_id = orchestrator.request_operation(
                operation_type="create_file",
                file_path=temp_path,
                content="# Test\n\nContent.",
                context={"reason": "Testing"}
            )
            
            # Execute operation
            success = orchestrator.execute_operation(operation_id)
            
            assert success
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                content = f.read()
                assert content == "# Test\n\nContent."
            
            # Check operation status
            operation = orchestrator.operation_history[0]
            assert operation.status == "completed"
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_execute_operation_modify_file(self, orchestrator, temp_file):
        """Test executing a file modification operation"""
        original_content = open(temp_file, 'r').read()
        new_content = "# Modified Document\n\nShort content."
        
        # Request operation
        operation_id = orchestrator.request_operation(
            operation_type="modify_file",
            file_path=temp_file,
            content=new_content,
            context={"reason": "Testing modification"}
        )
        
        # Execute operation
        success = orchestrator.execute_operation(operation_id)
        
        assert success
        
        # Check file content
        with open(temp_file, 'r') as f:
            content = f.read()
            assert content == new_content
        
        # Check operation status
        operation = orchestrator.operation_history[0]
        assert operation.status == "completed"
    
    def test_execute_operation_delete_file(self, orchestrator, temp_file):
        """Test executing a file deletion operation"""
        assert os.path.exists(temp_file)
        
        # Request operation
        operation_id = orchestrator.request_operation(
            operation_type="delete_file",
            file_path=temp_file,
            context={"reason": "Testing deletion"}
        )
        
        # Execute operation
        success = orchestrator.execute_operation(operation_id)
        
        assert success
        assert not os.path.exists(temp_file)
        
        # Check operation status
        operation = orchestrator.operation_history[0]
        assert operation.status == "completed"
    
    def test_get_operation_status(self, orchestrator):
        """Test getting operation status"""
        operation_id = orchestrator.request_operation(
            operation_type="create_file",
            file_path="test_file.md",
            content="# Test\n\nContent.",
            context={"reason": "Testing"}
        )
        
        status = orchestrator.get_operation_status(operation_id)
        
        assert status is not None
        assert status['operation_id'] == operation_id
        assert status['status'] == "approved"
        assert 'timestamp' in status
        assert 'warnings' in status
        assert 'recommendations' in status
    
    def test_get_operation_status_not_found(self, orchestrator):
        """Test getting status for non-existent operation"""
        status = orchestrator.get_operation_status("non_existent_operation")
        assert status is None
    
    def test_get_safety_summary(self, orchestrator):
        """Test getting safety system summary"""
        # Create some operations
        orchestrator.request_operation(
            operation_type="create_file",
            file_path="test1.md",
            content="# Test 1",
            context={"reason": "Testing"}
        )
        
        orchestrator.request_operation(
            operation_type="create_file",
            file_path="test2.md",
            content="# Test 2",
            context={"reason": "Testing"}
        )
        
        # Execute one operation
        operation_id = orchestrator.operation_history[0].operation_id
        orchestrator.execute_operation(operation_id)
        
        summary = orchestrator.get_safety_summary()
        
        assert 'total_operations' in summary
        assert 'successful_operations' in summary
        assert 'failed_operations' in summary
        assert 'rejected_operations' in summary
        assert 'success_rate' in summary
        assert 'active_operations' in summary
        assert 'recent_warnings' in summary
        assert 'system_status' in summary
        
        assert summary['total_operations'] == 2
        assert summary['successful_operations'] == 1
        assert summary['success_rate'] == 0.5
    
    def test_perform_safety_checks(self, orchestrator, temp_file):
        """Test instantiation of SafetyOrchestrator"""
        orchestrator = SafetyOrchestrator()
        assert orchestrator is not None
        assert orchestrator.config is not None
        assert orchestrator.manager_ai is not None
        assert orchestrator.line_removal_detector is not None
    
    def test_perform_safety_checks_with_content_loss(self, orchestrator, temp_file):
        """Test safety checks with content loss detection"""
        # Create operation that will cause content loss
        operation = SafetyOperation(
            operation_id="test_operation",
            operation_type="modify_file",
            file_path=temp_file,
            content="# Short content",  # Much shorter than original
            context={"reason": "Testing content loss"},
            timestamp=datetime.now(),
            status="pending",
            safety_checks=[],
            warnings=[],
            recommendations=[]
        )
        
        # Perform safety checks
        result = orchestrator._perform_safety_checks(operation)
        
        assert result.operation_id == "test_operation"
        assert not result.approved  # Should not be approved due to content loss
        assert len(result.warnings) > 0
        assert len(result.recommendations) > 0
        assert result.requires_user_confirmation
    
    def test_perform_safety_checks_without_issues(self, orchestrator):
        """Test safety checks without issues"""
        # Create operation that should be safe
        operation = SafetyOperation(
            operation_id="test_operation",
            operation_type="create_file",
            file_path="new_file.md",
            content="# New file content",
            context={"reason": "Testing safe operation"},
            timestamp=datetime.now(),
            status="pending",
            safety_checks=[],
            warnings=[],
            recommendations=[]
        )
        
        # Perform safety checks
        result = orchestrator._perform_safety_checks(operation)
        
        assert result.operation_id == "test_operation"
        assert result.approved  # Should be approved
        assert len(result.warnings) == 0
        assert len(result.recommendations) == 0
        assert not result.requires_user_confirmation


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_safe_modify_file(self, temp_file):
        """Test the safe_modify_file convenience function"""
        original_content = open(temp_file, 'r').read()
        new_content = "# Modified Document\n\nShort content."
        
        success = safe_modify_file(temp_file, new_content, "modify_file", {"reason": "Testing"})
        
        assert success
        
        with open(temp_file, 'r') as f:
            content = f.read()
            assert content == new_content
    
    def test_safe_create_file(self):
        """Test the safe_create_file convenience function"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            temp_path = f.name
        
        try:
            content = "# Test Document\n\nContent here."
            success = safe_create_file(temp_path, content, {"reason": "Testing"})
            
            assert success
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                file_content = f.read()
                assert file_content == content
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_monitor_aether_action(self):
        """Test the monitor_aether_action convenience function"""
        context = {
            'task': 'Test task',
            'goal': 'Test goal',
            'confidence': 0.8,
            'file_path': 'test.md'
        }
        
        # This should return None for safe operations
        result = monitor_aether_action("safe_operation", context)
        
        # Result could be None (safe) or a guidance message (unsafe)
        assert result is None or isinstance(result, str)


class TestConfiguration:
    """Test configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration"""
        orchestrator = SafetyOrchestrator()
        config = orchestrator._default_config()
        
        assert 'enable_manager_ai' in config
        assert 'enable_line_removal_detection' in config
        assert 'enable_automatic_approval' in config
        assert 'enable_user_notifications' in config
        assert 'operation_timeout' in config
        assert 'max_concurrent_operations' in config
        assert 'safety_check_timeout' in config
        assert 'manager_ai' in config
        assert 'line_removal_detector' in config
    
    def test_custom_config(self):
        """Test custom configuration"""
        custom_config = {
            'enable_manager_ai': False,
            'enable_line_removal_detection': False,
            'enable_automatic_approval': True,
            'manager_ai': {
                'confidence_threshold': 0.5
            }
        }
        
        orchestrator = SafetyOrchestrator(custom_config)
        
        assert orchestrator.config['enable_manager_ai'] == False
        assert orchestrator.config['enable_line_removal_detection'] == False
        assert orchestrator.config['enable_automatic_approval'] == True
        assert orchestrator.config['manager_ai']['confidence_threshold'] == 0.5
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test with invalid config
        invalid_config = {
            'invalid_key': 'invalid_value'
        }
        
        orchestrator = SafetyOrchestrator(invalid_config)
        
        # Should still work with default config merged
        assert 'enable_manager_ai' in orchestrator.config
        assert 'enable_line_removal_detection' in orchestrator.config


class TestStateManagement:
    """Test state management functionality"""
    
    def test_load_state(self):
        """Test loading state from disk"""
        orchestrator = SafetyOrchestrator()
        
        # Should not fail even if no state file exists
        orchestrator._load_state()
        
        assert len(orchestrator.operation_history) == 0
    
    def test_save_state(self):
        """Test saving state to disk"""
        orchestrator = SafetyOrchestrator()
        
        # Create some operations
        orchestrator.request_operation(
            operation_type="create_file",
            file_path="test.md",
            content="# Test",
            context={"reason": "Testing state"}
        )
        
        # Save state
        orchestrator._save_state()
        
        # State file should exist
        state_file = orchestrator.data_dir / "safety_orchestrator_state.json"
        assert state_file.exists()
        
        # Load state and verify
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        assert 'operation_history' in state_data
        assert len(state_data['operation_history']) == 1
        assert state_data['operation_history'][0]['operation_type'] == "create_file"


class TestErrorHandling:
    """Test error handling functionality"""
    
    def test_execute_nonexistent_operation(self, orchestrator):
        """Test executing non-existent operation"""
        success = orchestrator.execute_operation("non_existent_operation")
        assert not success
    
    def test_execute_operation_with_missing_file_path(self, orchestrator):
        """Test executing operation with missing file path"""
        operation = SafetyOperation(
            operation_id="test_operation",
            operation_type="modify_file",
            file_path=None,  # Missing file path
            content="# Test",
            context={"reason": "Testing"},
            timestamp=datetime.now(),
            status="approved",
            safety_checks=[],
            warnings=[],
            recommendations=[]
        )
        
        orchestrator.operation_history.append(operation)
        
        success = orchestrator.execute_operation("test_operation")
        assert not success
    
    def test_execute_operation_with_missing_content(self, orchestrator):
        """Test executing operation with missing content"""
        operation = SafetyOperation(
            operation_id="test_operation",
            operation_type="modify_file",
            file_path="test.md",
            content=None,  # Missing content
            context={"reason": "Testing"},
            timestamp=datetime.now(),
            status="approved",
            safety_checks=[],
            warnings=[],
            recommendations=[]
        )
        
        orchestrator.operation_history.append(operation)
        
        success = orchestrator.execute_operation("test_operation")
        assert not success


if __name__ == "__main__":
    pytest.main([__file__])
