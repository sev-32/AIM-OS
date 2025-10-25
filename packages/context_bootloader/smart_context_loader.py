"""
Smart Context Loader - Intelligent context loading with weights and MCP integration

This module provides intelligent context loading capabilities for AI tasks through:
- Task-specific bootloader configurations with weighted priorities
- Smart context budget management with fallback strategies
- MCP integration for persistent memory and semantic enhancement
- Progressive disclosure based on context budget and task complexity
"""

from __future__ import annotations

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# MCP imports (assuming we have MCP client)
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}
        
        def retrieve_memory(self, query: str, max_results: int = 10, min_relevance: float = 0.8) -> List[Dict[str, Any]]:
            return []


class Priority(Enum):
    """Priority levels for context sources"""
    MANDATORY = "mandatory"
    HIGH = "high"
    LOW = "low"
    SEMANTIC = "semantic"


class DetailLevel(Enum):
    """Detail levels for context loading"""
    L1 = "L1"  # Basic overview
    L2 = "L2"  # Architecture overview
    L3 = "L3"  # Detailed implementation
    L4 = "L4"  # Full implementation with code


@dataclass
class ContextSource:
    """Represents a context source with metadata"""
    file: str
    weight: float
    detail_level: DetailLevel
    estimated_tokens: int
    priority: Priority
    description: str = ""
    tokens_used: int = 0


@dataclass
class BootloaderConfig:
    """Bootloader configuration for a specific task"""
    task: str
    context_strategy: str
    max_context_budget: int
    context_sources: Dict[str, List[ContextSource]] = field(default_factory=dict)
    loading_strategy: str = "weighted_progressive"
    fallback_strategy: str = "essential_only"
    semantic_enhancement: bool = True
    cross_session_continuity: bool = True


@dataclass
class LoadedContext:
    """Represents loaded context with metadata"""
    content: str
    weight: float
    priority: Priority
    tokens_used: int
    file_path: str
    source: str = "file"
    relevance: float = 1.0


class SmartContextLoader:
    """
    Intelligent context loader with weighted priorities and MCP integration
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.context_cache = {}
        self.bootloader_configs = {}
        self.bootloader_dir = Path("bootloaders")
        
        # Ensure bootloader directory exists
        self.bootloader_dir.mkdir(exist_ok=True)
    
    def load_context_for_task(self, task_type: str, context_budget: int) -> List[LoadedContext]:
        """
        Load context using smart weighting and MCP integration
        
        Args:
            task_type: Type of task (e.g., "vif_implementation")
            context_budget: Maximum tokens available for context
            
        Returns:
            List of loaded context items with metadata
        """
        # Load bootloader configuration
        bootloader = self.load_bootloader_config(task_type)
        
        # Load context with weights
        context = self.load_weighted_context(bootloader, context_budget)
        
        # Store context in MCP memory for future use
        self.mcp_client.store_memory({
            'type': 'context_loading',
            'task_type': task_type,
            'context_summary': [c.file_path for c in context],
            'timestamp': datetime.now().isoformat(),
            'budget_used': sum(c.tokens_used for c in context),
            'sources_loaded': len(context)
        })
        
        return context
    
    def load_bootloader_config(self, task_type: str) -> BootloaderConfig:
        """
        Load bootloader configuration for a specific task
        
        Args:
            task_type: Type of task
            
        Returns:
            BootloaderConfig object
        """
        if task_type in self.bootloader_configs:
            return self.bootloader_configs[task_type]
        
        config_path = self.bootloader_dir / f"{task_type}.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            bootloader = self._parse_bootloader_config(config_data)
            self.bootloader_configs[task_type] = bootloader
            return bootloader
        else:
            # Create default bootloader if none exists
            return self._create_default_bootloader(task_type)
    
    def load_weighted_context(self, bootloader: BootloaderConfig, context_budget: int) -> List[LoadedContext]:
        """
        Load context using weighted priority system
        
        Args:
            bootloader: Bootloader configuration
            context_budget: Maximum tokens available
            
        Returns:
            List of loaded context items
        """
        loaded_context = []
        remaining_budget = context_budget
        
        # Load critical context (mandatory)
        for source in bootloader.context_sources.get('critical', []):
            if remaining_budget >= source.estimated_tokens:
                content = self._load_file_with_detail_level(source.file, source.detail_level)
                if content:
                    loaded_context.append(LoadedContext(
                        content=content,
                        weight=source.weight,
                        priority=source.priority,
                        tokens_used=source.estimated_tokens,
                        file_path=source.file
                    ))
                    remaining_budget -= source.estimated_tokens
        
        # Load helpful context (high priority)
        for source in bootloader.context_sources.get('helpful', []):
            if remaining_budget >= source.estimated_tokens:
                content = self._load_file_with_detail_level(source.file, source.detail_level)
                if content:
                    loaded_context.append(LoadedContext(
                        content=content,
                        weight=source.weight,
                        priority=source.priority,
                        tokens_used=source.estimated_tokens,
                        file_path=source.file
                    ))
                    remaining_budget -= source.estimated_tokens
        
        # Load optional context (low priority) if budget allows
        for source in bootloader.context_sources.get('optional', []):
            if remaining_budget >= source.estimated_tokens:
                content = self._load_file_with_detail_level(source.file, source.detail_level)
                if content:
                    loaded_context.append(LoadedContext(
                        content=content,
                        weight=source.weight,
                        priority=source.priority,
                        tokens_used=source.estimated_tokens,
                        file_path=source.file
                    ))
                    remaining_budget -= source.estimated_tokens
        
        return loaded_context
    
    def _load_file_with_detail_level(self, file_path: str, detail_level: DetailLevel) -> Optional[str]:
        """
        Load file content with appropriate detail level
        
        Args:
            file_path: Path to the file
            detail_level: Detail level to load
            
        Returns:
            File content or None if file doesn't exist
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return None
            
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, return full content
            # TODO: Implement detail level filtering
            return content
            
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None
    
    def _parse_bootloader_config(self, config_data: Dict[str, Any]) -> BootloaderConfig:
        """
        Parse bootloader configuration from YAML data
        
        Args:
            config_data: YAML configuration data
            
        Returns:
            BootloaderConfig object
        """
        context_sources = {}
        
        for source_type, sources in config_data.get('context_sources', {}).items():
            context_sources[source_type] = []
            for source_data in sources:
                context_sources[source_type].append(ContextSource(
                    file=source_data['file'],
                    weight=source_data['weight'],
                    detail_level=DetailLevel(source_data['detail_level']),
                    estimated_tokens=source_data['estimated_tokens'],
                    priority=Priority(source_data['priority']),
                    description=source_data.get('description', '')
                ))
        
        return BootloaderConfig(
            task=config_data['task'],
            context_strategy=config_data.get('context_strategy', 'weighted_loading'),
            max_context_budget=config_data.get('max_context_budget', 100000),
            context_sources=context_sources,
            loading_strategy=config_data.get('loading_strategy', 'weighted_progressive'),
            fallback_strategy=config_data.get('fallback_strategy', 'essential_only'),
            semantic_enhancement=config_data.get('semantic_enhancement', True),
            cross_session_continuity=config_data.get('cross_session_continuity', True)
        )
    
    def _create_default_bootloader(self, task_type: str) -> BootloaderConfig:
        """
        Create default bootloader configuration for a task type
        
        Args:
            task_type: Type of task
            
        Returns:
            Default BootloaderConfig
        """
        # Create basic default configuration
        default_sources = {
            'critical': [
                ContextSource(
                    file=f"knowledge_architecture/systems/{task_type}/README.md",
                    weight=1.0,
                    detail_level=DetailLevel.L2,
                    estimated_tokens=5000,
                    priority=Priority.MANDATORY,
                    description=f"Basic {task_type} documentation"
                )
            ],
            'helpful': [],
            'optional': []
        }
        
        return BootloaderConfig(
            task=task_type,
            context_strategy="weighted_loading",
            max_context_budget=80000,
            context_sources=default_sources,
            loading_strategy="weighted_progressive",
            fallback_strategy="essential_only",
            semantic_enhancement=True,
            cross_session_continuity=True
        )
    
    def get_context_summary(self, context: List[LoadedContext]) -> Dict[str, Any]:
        """
        Get summary of loaded context
        
        Args:
            context: List of loaded context items
            
        Returns:
            Summary dictionary
        """
        total_tokens = sum(c.tokens_used for c in context)
        priority_counts = {}
        for c in context:
            priority_counts[c.priority.value] = priority_counts.get(c.priority.value, 0) + 1
        
        return {
            'total_sources': len(context),
            'total_tokens': total_tokens,
            'priority_distribution': priority_counts,
            'files_loaded': [c.file_path for c in context],
            'average_weight': sum(c.weight for c in context) / len(context) if context else 0
        }


class SemanticContextLoader(SmartContextLoader):
    """
    Enhanced context loader with semantic enhancement capabilities
    """
    
    def load_context_with_semantic_enhancement(self, task_type: str, query: str, context_budget: int = 80000) -> List[LoadedContext]:
        """
        Load context using bootloader + semantic matching
        
        Args:
            task_type: Type of task
            query: Semantic query for enhancement
            context_budget: Maximum tokens available
            
        Returns:
            List of loaded context items with semantic enhancement
        """
        # Load base context from bootloader
        base_context = self.load_context_for_task(task_type, context_budget * 0.8)
        
        # Add semantic matches
        semantic_matches = self.mcp_client.retrieve_memory(
            query, 
            max_results=10,
            min_relevance=0.8
        )
        
        # Weight semantic matches
        for match in semantic_matches:
            if match.get('relevance', 0) > 0.8:
                estimated_tokens = len(match.get('content', '').split()) * 1.3
                base_context.append(LoadedContext(
                    content=match.get('content', ''),
                    weight=match.get('relevance', 0.8),
                    priority=Priority.SEMANTIC,
                    tokens_used=int(estimated_tokens),
                    file_path=match.get('source', 'semantic_match'),
                    source='semantic_match',
                    relevance=match.get('relevance', 0.8)
                ))
        
        return base_context


# Example usage and testing
if __name__ == "__main__":
    # Create context loader
    loader = SmartContextLoader()
    
    # Load context for VIF implementation
    context = loader.load_context_for_task("vif_implementation", 80000)
    
    # Get summary
    summary = loader.get_context_summary(context)
    print(f"Loaded {summary['total_sources']} sources with {summary['total_tokens']} tokens")
    print(f"Priority distribution: {summary['priority_distribution']}")
