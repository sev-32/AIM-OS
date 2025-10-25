"""
Tests for MCP Context Tools

This module provides comprehensive tests for the MCP context tools,
including context loading, weighted priorities, and optimization.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_context_tools import (
    ContextBootloaderMCP,
    ContextLoadingResult,
    mcp_load_bootloader_context,
    mcp_load_context_with_weights,
    mcp_optimize_context_for_task,
    mcp_get_available_bootloaders,
    mcp_get_context_statistics
)


class TestContextBootloaderMCP:
    """Test cases for ContextBootloaderMCP"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mcp_tools = ContextBootloaderMCP()
    
    def test_load_bootloader_context_success(self):
        """Test successful context loading with bootloader"""
        # Mock smart loader
        mock_context = [
            Mock(
                content='test content',
                weight=1.0,
                priority=Mock(value='mandatory'),
                tokens_used=5000,
                file_path='test_file.md',
                source='file',
                relevance=1.0
            )
        ]
        
        with patch.object(self.mcp_tools.smart_loader, 'load_context_for_task') as mock_load:
            mock_load.return_value = mock_context
            
            with patch.object(self.mcp_tools.smart_loader, 'get_context_summary') as mock_summary:
                mock_summary.return_value = {
                    'total_sources': 1,
                    'total_tokens': 5000,
                    'priority_distribution': {'mandatory': 1},
                    'files_loaded': ['test_file.md'],
                    'average_weight': 1.0
                }
                
                # Test context loading
                result = self.mcp_tools.load_bootloader_context('test_task', 80000)
                
                # Verify result
                assert result.success is True
                assert result.task_type == 'test_task'
                assert result.budget_used == 5000
                assert result.sources_loaded == 1
                assert len(result.context) == 1
                assert result.context[0]['content'] == 'test content'
                assert result.context[0]['weight'] == 1.0
                assert result.context_summary['total_sources'] == 1
    
    def test_load_bootloader_context_error(self):
        """Test context loading with error"""
        # Mock smart loader to raise exception
        with patch.object(self.mcp_tools.smart_loader, 'load_context_for_task') as mock_load:
            mock_load.side_effect = Exception("Test error")
            
            # Test context loading
            result = self.mcp_tools.load_bootloader_context('test_task', 80000)
            
            # Verify error handling
            assert result.success is False
            assert result.task_type == 'test_task'
            assert result.budget_used == 0
            assert result.sources_loaded == 0
            assert result.error_message == "Test error"
    
    def test_load_context_with_weights(self):
        """Test context loading with custom weights"""
        # Mock smart loader
        mock_context = [
            Mock(
                content='test content',
                weight=1.0,
                priority=Mock(value='mandatory'),
                tokens_used=5000,
                file_path='test_file.md',
                source='file',
                relevance=1.0
            )
        ]
        
        with patch.object(self.mcp_tools.smart_loader, 'load_context_for_task') as mock_load:
            mock_load.return_value = mock_context
            
            # Test context loading with weights
            weights = {'test_file.md': 0.8}
            result = self.mcp_tools.load_context_with_weights('test_task', weights, 80000)
            
            # Verify result
            assert result.success is True
            assert result.task_type == 'test_task'
            assert result.budget_used == 5000
            assert result.sources_loaded == 1
            assert len(result.context) == 1
            assert result.context[0]['weight'] == 0.8  # Custom weight applied
    
    def test_optimize_context_for_task(self):
        """Test context optimization for task"""
        # Mock semantic loader
        mock_context = [
            Mock(
                content='test content',
                weight=1.0,
                priority=Mock(value='mandatory'),
                tokens_used=5000,
                file_path='test_file.md',
                source='file',
                relevance=1.0
            )
        ]
        
        with patch.object(self.mcp_tools.semantic_loader, 'load_context_with_semantic_enhancement') as mock_load:
            mock_load.return_value = mock_context
            
            with patch.object(self.mcp_tools.semantic_loader, 'get_context_summary') as mock_summary:
                mock_summary.return_value = {
                    'total_sources': 1,
                    'total_tokens': 5000,
                    'priority_distribution': {'mandatory': 1},
                    'files_loaded': ['test_file.md'],
                    'average_weight': 1.0
                }
                
                # Test context optimization
                result = self.mcp_tools.optimize_context_for_task('test_task', 'test query', 80000)
                
                # Verify result
                assert result.success is True
                assert result.task_type == 'test_task'
                assert result.budget_used == 5000
                assert result.sources_loaded == 1
                assert len(result.context) == 1
                assert result.context_summary['total_sources'] == 1
    
    def test_get_available_bootloaders(self):
        """Test getting available bootloaders"""
        # Mock bootloader directory
        with patch.object(self.mcp_tools.smart_loader, 'bootloader_dir') as mock_dir:
            mock_dir.exists.return_value = True
            mock_dir.glob.return_value = [
                Mock(stem='vif_implementation'),
                Mock(stem='safety_systems'),
                Mock(stem='test_task')
            ]
            
            # Test getting available bootloaders
            bootloaders = self.mcp_tools.get_available_bootloaders()
            
            # Verify result
            assert len(bootloaders) == 3
            assert 'vif_implementation' in bootloaders
            assert 'safety_systems' in bootloaders
            assert 'test_task' in bootloaders
    
    def test_get_context_statistics(self):
        """Test getting context statistics"""
        # Mock bootloader config
        mock_config = Mock()
        mock_config.context_sources = {
            'critical': [
                Mock(estimated_tokens=5000, priority=Mock(value='mandatory'))
            ],
            'helpful': [
                Mock(estimated_tokens=3000, priority=Mock(value='high'))
            ]
        }
        mock_config.max_context_budget = 80000
        mock_config.context_strategy = 'weighted_loading'
        mock_config.loading_strategy = 'weighted_progressive'
        mock_config.fallback_strategy = 'essential_only'
        mock_config.semantic_enhancement = True
        mock_config.cross_session_continuity = True
        
        with patch.object(self.mcp_tools.smart_loader, 'load_bootloader_config') as mock_load_config:
            mock_load_config.return_value = mock_config
            
            # Test getting statistics
            stats = self.mcp_tools.get_context_statistics('test_task')
            
            # Verify result
            assert stats['task_type'] == 'test_task'
            assert stats['total_sources'] == 2
            assert stats['total_estimated_tokens'] == 8000
            assert stats['priority_distribution']['mandatory'] == 1
            assert stats['priority_distribution']['high'] == 1
            assert stats['max_context_budget'] == 80000
            assert stats['context_strategy'] == 'weighted_loading'
            assert stats['semantic_enhancement'] is True


class TestMCPToolFunctions:
    """Test cases for MCP tool functions"""
    
    def test_mcp_load_bootloader_context(self):
        """Test MCP tool function for loading bootloader context"""
        # Mock MCP tools
        with patch('mcp_context_tools.ContextBootloaderMCP') as mock_mcp_class:
            mock_mcp_instance = Mock()
            mock_mcp_class.return_value = mock_mcp_instance
            
            mock_result = ContextLoadingResult(
                success=True,
                context=[{'content': 'test content', 'weight': 1.0}],
                task_type='test_task',
                budget_used=5000,
                sources_loaded=1
            )
            mock_mcp_instance.load_bootloader_context.return_value = mock_result
            
            # Test MCP tool function
            result = mcp_load_bootloader_context('test_task', 80000)
            
            # Verify result
            assert result['success'] is True
            assert result['task_type'] == 'test_task'
            assert result['budget_used'] == 5000
            assert result['sources_loaded'] == 1
            assert len(result['context']) == 1
    
    def test_mcp_load_context_with_weights(self):
        """Test MCP tool function for loading context with weights"""
        # Mock MCP tools
        with patch('mcp_context_tools.ContextBootloaderMCP') as mock_mcp_class:
            mock_mcp_instance = Mock()
            mock_mcp_class.return_value = mock_mcp_instance
            
            mock_result = ContextLoadingResult(
                success=True,
                context=[{'content': 'test content', 'weight': 0.8}],
                task_type='test_task',
                budget_used=5000,
                sources_loaded=1
            )
            mock_mcp_instance.load_context_with_weights.return_value = mock_result
            
            # Test MCP tool function
            weights = {'test_file.md': 0.8}
            result = mcp_load_context_with_weights('test_task', weights, 80000)
            
            # Verify result
            assert result['success'] is True
            assert result['task_type'] == 'test_task'
            assert result['budget_used'] == 5000
            assert result['sources_loaded'] == 1
            assert result['context'][0]['weight'] == 0.8
    
    def test_mcp_optimize_context_for_task(self):
        """Test MCP tool function for optimizing context"""
        # Mock MCP tools
        with patch('mcp_context_tools.ContextBootloaderMCP') as mock_mcp_class:
            mock_mcp_instance = Mock()
            mock_mcp_class.return_value = mock_mcp_instance
            
            mock_result = ContextLoadingResult(
                success=True,
                context=[{'content': 'test content', 'weight': 1.0}],
                task_type='test_task',
                budget_used=5000,
                sources_loaded=1,
                context_summary={'total_sources': 1, 'total_tokens': 5000}
            )
            mock_mcp_instance.optimize_context_for_task.return_value = mock_result
            
            # Test MCP tool function
            result = mcp_optimize_context_for_task('test_task', 'test query', 80000)
            
            # Verify result
            assert result['success'] is True
            assert result['task_type'] == 'test_task'
            assert result['budget_used'] == 5000
            assert result['sources_loaded'] == 1
            assert result['context_summary']['total_sources'] == 1
    
    def test_mcp_get_available_bootloaders(self):
        """Test MCP tool function for getting available bootloaders"""
        # Mock MCP tools
        with patch('mcp_context_tools.ContextBootloaderMCP') as mock_mcp_class:
            mock_mcp_instance = Mock()
            mock_mcp_class.return_value = mock_mcp_instance
            
            mock_mcp_instance.get_available_bootloaders.return_value = [
                'vif_implementation', 'safety_systems', 'test_task'
            ]
            
            # Test MCP tool function
            result = mcp_get_available_bootloaders()
            
            # Verify result
            assert len(result) == 3
            assert 'vif_implementation' in result
            assert 'safety_systems' in result
            assert 'test_task' in result
    
    def test_mcp_get_context_statistics(self):
        """Test MCP tool function for getting context statistics"""
        # Mock MCP tools
        with patch('mcp_context_tools.ContextBootloaderMCP') as mock_mcp_class:
            mock_mcp_instance = Mock()
            mock_mcp_class.return_value = mock_mcp_instance
            
            mock_stats = {
                'task_type': 'test_task',
                'total_sources': 2,
                'total_estimated_tokens': 8000,
                'priority_distribution': {'mandatory': 1, 'high': 1},
                'max_context_budget': 80000,
                'context_strategy': 'weighted_loading'
            }
            mock_mcp_instance.get_context_statistics.return_value = mock_stats
            
            # Test MCP tool function
            result = mcp_get_context_statistics('test_task')
            
            # Verify result
            assert result['task_type'] == 'test_task'
            assert result['total_sources'] == 2
            assert result['total_estimated_tokens'] == 8000
            assert result['priority_distribution']['mandatory'] == 1
            assert result['priority_distribution']['high'] == 1


class TestContextLoadingResult:
    """Test cases for ContextLoadingResult"""
    
    def test_context_loading_result_creation(self):
        """Test ContextLoadingResult creation"""
        result = ContextLoadingResult(
            success=True,
            context=[{'content': 'test content'}],
            task_type='test_task',
            budget_used=5000,
            sources_loaded=1
        )
        
        assert result.success is True
        assert len(result.context) == 1
        assert result.task_type == 'test_task'
        assert result.budget_used == 5000
        assert result.sources_loaded == 1
        assert result.error_message is None
        assert result.context_summary is None
    
    def test_context_loading_result_with_error(self):
        """Test ContextLoadingResult with error"""
        result = ContextLoadingResult(
            success=False,
            context=[],
            task_type='test_task',
            budget_used=0,
            sources_loaded=0,
            error_message='Test error'
        )
        
        assert result.success is False
        assert len(result.context) == 0
        assert result.task_type == 'test_task'
        assert result.budget_used == 0
        assert result.sources_loaded == 0
        assert result.error_message == 'Test error'


if __name__ == "__main__":
    pytest.main([__file__])
