"""
Tests for Smart Context Loader

This module provides comprehensive tests for the SmartContextLoader class,
including weighted context loading, MCP integration, and bootloader configurations.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from smart_context_loader import (
    SmartContextLoader, 
    SemanticContextLoader,
    BootloaderConfig,
    ContextSource,
    Priority,
    DetailLevel,
    LoadedContext
)


class TestSmartContextLoader:
    """Test cases for SmartContextLoader"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.bootloader_dir = Path(self.temp_dir) / "bootloaders"
        self.bootloader_dir.mkdir(exist_ok=True)
        
        # Mock MCP client
        self.mock_mcp_client = Mock()
        self.mock_mcp_client.store_memory.return_value = {'success': True, 'id': 'test_memory_id'}
        self.mock_mcp_client.retrieve_memory.return_value = []
        
        # Create context loader
        self.loader = SmartContextLoader(mcp_client=self.mock_mcp_client)
        self.loader.bootloader_dir = self.bootloader_dir
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_bootloader_config_existing(self):
        """Test loading existing bootloader configuration"""
        # Create test bootloader config
        config_data = {
            'task': 'test_task',
            'context_strategy': 'weighted_loading',
            'max_context_budget': 80000,
            'context_sources': {
                'critical': [
                    {
                        'file': 'test_file.md',
                        'weight': 1.0,
                        'detail_level': 'L3',
                        'estimated_tokens': 5000,
                        'priority': 'mandatory',
                        'description': 'Test file'
                    }
                ]
            }
        }
        
        config_path = self.bootloader_dir / "test_task.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config = self.loader.load_bootloader_config('test_task')
        
        # Verify configuration
        assert config.task == 'test_task'
        assert config.context_strategy == 'weighted_loading'
        assert config.max_context_budget == 80000
        assert len(config.context_sources['critical']) == 1
        assert config.context_sources['critical'][0].file == 'test_file.md'
        assert config.context_sources['critical'][0].weight == 1.0
    
    def test_load_bootloader_config_default(self):
        """Test loading default bootloader configuration when none exists"""
        config = self.loader.load_bootloader_config('nonexistent_task')
        
        # Verify default configuration
        assert config.task == 'nonexistent_task'
        assert config.context_strategy == 'weighted_loading'
        assert config.max_context_budget == 80000
        assert len(config.context_sources['critical']) == 1
        assert config.context_sources['critical'][0].file.endswith('README.md')
    
    def test_load_weighted_context(self):
        """Test weighted context loading"""
        # Create test bootloader config
        config = BootloaderConfig(
            task='test_task',
            context_strategy='weighted_loading',
            max_context_budget=80000,
            context_sources={
                'critical': [
                    ContextSource(
                        file='test_file1.md',
                        weight=1.0,
                        detail_level=DetailLevel.L3,
                        estimated_tokens=5000,
                        priority=Priority.MANDATORY,
                        description='Test file 1'
                    )
                ],
                'helpful': [
                    ContextSource(
                        file='test_file2.md',
                        weight=0.7,
                        detail_level=DetailLevel.L2,
                        estimated_tokens=3000,
                        priority=Priority.HIGH,
                        description='Test file 2'
                    )
                ]
            }
        )
        
        # Mock file loading
        with patch.object(self.loader, '_load_file_with_detail_level') as mock_load:
            mock_load.side_effect = ['content1', 'content2']
            
            # Load context
            context = self.loader.load_weighted_context(config, 10000)
            
            # Verify context loading
            assert len(context) == 2
            assert context[0].content == 'content1'
            assert context[0].weight == 1.0
            assert context[0].priority == Priority.MANDATORY
            assert context[1].content == 'content2'
            assert context[1].weight == 0.7
            assert context[1].priority == Priority.HIGH
    
    def test_load_weighted_context_budget_limit(self):
        """Test weighted context loading with budget limits"""
        # Create test bootloader config
        config = BootloaderConfig(
            task='test_task',
            context_strategy='weighted_loading',
            max_context_budget=80000,
            context_sources={
                'critical': [
                    ContextSource(
                        file='test_file1.md',
                        weight=1.0,
                        detail_level=DetailLevel.L3,
                        estimated_tokens=5000,
                        priority=Priority.MANDATORY,
                        description='Test file 1'
                    )
                ],
                'helpful': [
                    ContextSource(
                        file='test_file2.md',
                        weight=0.7,
                        detail_level=DetailLevel.L2,
                        estimated_tokens=3000,
                        priority=Priority.HIGH,
                        description='Test file 2'
                    )
                ]
            }
        )
        
        # Mock file loading
        with patch.object(self.loader, '_load_file_with_detail_level') as mock_load:
            mock_load.side_effect = ['content1', 'content2']
            
            # Load context with limited budget
            context = self.loader.load_weighted_context(config, 4000)
            
            # Verify only critical context is loaded (budget limit)
            assert len(context) == 1
            assert context[0].content == 'content1'
            assert context[0].priority == Priority.MANDATORY
    
    def test_load_file_with_detail_level(self):
        """Test file loading with detail level"""
        # Create test file
        test_file = Path(self.temp_dir) / "test_file.md"
        test_file.write_text("Test content")
        
        # Load file
        content = self.loader._load_file_with_detail_level(str(test_file), DetailLevel.L3)
        
        # Verify content
        assert content == "Test content"
    
    def test_load_file_with_detail_level_nonexistent(self):
        """Test file loading with nonexistent file"""
        content = self.loader._load_file_with_detail_level("nonexistent_file.md", DetailLevel.L3)
        
        # Verify None is returned
        assert content is None
    
    def test_get_context_summary(self):
        """Test context summary generation"""
        # Create test context
        context = [
            LoadedContext(
                content="content1",
                weight=1.0,
                priority=Priority.MANDATORY,
                tokens_used=5000,
                file_path="file1.md"
            ),
            LoadedContext(
                content="content2",
                weight=0.7,
                priority=Priority.HIGH,
                tokens_used=3000,
                file_path="file2.md"
            )
        ]
        
        # Get summary
        summary = self.loader.get_context_summary(context)
        
        # Verify summary
        assert summary['total_sources'] == 2
        assert summary['total_tokens'] == 8000
        assert summary['priority_distribution']['mandatory'] == 1
        assert summary['priority_distribution']['high'] == 1
        assert summary['average_weight'] == 0.85
    
    def test_load_context_for_task(self):
        """Test complete context loading for task"""
        # Create test bootloader config
        config_data = {
            'task': 'test_task',
            'context_strategy': 'weighted_loading',
            'max_context_budget': 80000,
            'context_sources': {
                'critical': [
                    {
                        'file': 'test_file.md',
                        'weight': 1.0,
                        'detail_level': 'L3',
                        'estimated_tokens': 5000,
                        'priority': 'mandatory',
                        'description': 'Test file'
                    }
                ]
            }
        }
        
        config_path = self.bootloader_dir / "test_task.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Mock file loading
        with patch.object(self.loader, '_load_file_with_detail_level') as mock_load:
            mock_load.return_value = 'test content'
            
            # Load context
            context = self.loader.load_context_for_task('test_task', 10000)
            
            # Verify context loading
            assert len(context) == 1
            assert context[0].content == 'test content'
            assert context[0].weight == 1.0
            
            # Verify MCP memory storage
            self.mock_mcp_client.store_memory.assert_called_once()


class TestSemanticContextLoader:
    """Test cases for SemanticContextLoader"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.bootloader_dir = Path(self.temp_dir) / "bootloaders"
        self.bootloader_dir.mkdir(exist_ok=True)
        
        # Mock MCP client
        self.mock_mcp_client = Mock()
        self.mock_mcp_client.store_memory.return_value = {'success': True, 'id': 'test_memory_id'}
        self.mock_mcp_client.retrieve_memory.return_value = [
            {
                'content': 'semantic content',
                'relevance': 0.9,
                'source': 'semantic_match'
            }
        ]
        
        # Create semantic context loader
        self.loader = SemanticContextLoader(mcp_client=self.mock_mcp_client)
        self.loader.bootloader_dir = self.bootloader_dir
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_context_with_semantic_enhancement(self):
        """Test context loading with semantic enhancement"""
        # Create test bootloader config
        config_data = {
            'task': 'test_task',
            'context_strategy': 'weighted_loading',
            'max_context_budget': 80000,
            'context_sources': {
                'critical': [
                    {
                        'file': 'test_file.md',
                        'weight': 1.0,
                        'detail_level': 'L3',
                        'estimated_tokens': 5000,
                        'priority': 'mandatory',
                        'description': 'Test file'
                    }
                ]
            }
        }
        
        config_path = self.bootloader_dir / "test_task.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        # Mock file loading
        with patch.object(self.loader, '_load_file_with_detail_level') as mock_load:
            mock_load.return_value = 'test content'
            
            # Load context with semantic enhancement
            context = self.loader.load_context_with_semantic_enhancement(
                'test_task', 'test query', 10000
            )
            
            # Verify context loading
            assert len(context) == 2  # 1 file + 1 semantic match
            
            # Verify file context
            file_context = [c for c in context if c.source == 'file'][0]
            assert file_context.content == 'test content'
            assert file_context.weight == 1.0
            
            # Verify semantic context
            semantic_context = [c for c in context if c.source == 'semantic_match'][0]
            assert semantic_context.content == 'semantic content'
            assert semantic_context.weight == 0.9
            assert semantic_context.priority == Priority.SEMANTIC
            
            # Verify MCP retrieval was called
            self.mock_mcp_client.retrieve_memory.assert_called_once_with(
                'test query', max_results=10, min_relevance=0.8
            )


class TestBootloaderConfig:
    """Test cases for BootloaderConfig"""
    
    def test_bootloader_config_creation(self):
        """Test BootloaderConfig creation"""
        config = BootloaderConfig(
            task='test_task',
            context_strategy='weighted_loading',
            max_context_budget=80000
        )
        
        assert config.task == 'test_task'
        assert config.context_strategy == 'weighted_loading'
        assert config.max_context_budget == 80000
        assert config.loading_strategy == 'weighted_progressive'
        assert config.fallback_strategy == 'essential_only'
        assert config.semantic_enhancement is True
        assert config.cross_session_continuity is True


class TestContextSource:
    """Test cases for ContextSource"""
    
    def test_context_source_creation(self):
        """Test ContextSource creation"""
        source = ContextSource(
            file='test_file.md',
            weight=1.0,
            detail_level=DetailLevel.L3,
            estimated_tokens=5000,
            priority=Priority.MANDATORY,
            description='Test file'
        )
        
        assert source.file == 'test_file.md'
        assert source.weight == 1.0
        assert source.detail_level == DetailLevel.L3
        assert source.estimated_tokens == 5000
        assert source.priority == Priority.MANDATORY
        assert source.description == 'Test file'
        assert source.tokens_used == 0


class TestLoadedContext:
    """Test cases for LoadedContext"""
    
    def test_loaded_context_creation(self):
        """Test LoadedContext creation"""
        context = LoadedContext(
            content='test content',
            weight=1.0,
            priority=Priority.MANDATORY,
            tokens_used=5000,
            file_path='test_file.md'
        )
        
        assert context.content == 'test content'
        assert context.weight == 1.0
        assert context.priority == Priority.MANDATORY
        assert context.tokens_used == 5000
        assert context.file_path == 'test_file.md'
        assert context.source == 'file'
        assert context.relevance == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
