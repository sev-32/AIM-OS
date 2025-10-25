"""
MCP Context Tools - ICMP tools for context management and loading

This module provides MCP tools for intelligent context management through:
- Context bootloader loading with weighted priorities
- Semantic context enhancement and retrieval
- Context optimization and budget management
- Cross-session context continuity
"""

from __future__ import annotations

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .smart_context_loader import SmartContextLoader, SemanticContextLoader, LoadedContext, Priority


@dataclass
class ContextLoadingResult:
    """Result of context loading operation"""
    success: bool
    context: List[Dict[str, Any]]
    task_type: str
    budget_used: int
    sources_loaded: int
    error_message: Optional[str] = None
    context_summary: Optional[Dict[str, Any]] = None


class ContextBootloaderMCP:
    """
    MCP tools for context bootloader management
    """
    
    def __init__(self):
        self.smart_loader = SmartContextLoader()
        self.semantic_loader = SemanticContextLoader()
    
    def load_bootloader_context(self, task_type: str, context_budget: int) -> ContextLoadingResult:
        """
        MCP tool for loading context with bootloader
        
        Args:
            task_type: Type of task (e.g., "vif_implementation")
            context_budget: Maximum tokens available for context
            
        Returns:
            ContextLoadingResult with loaded context
        """
        try:
            # Load context using smart loader
            context = self.smart_loader.load_context_for_task(task_type, context_budget)
            
            # Convert to serializable format
            context_data = []
            for ctx in context:
                context_data.append({
                    'content': ctx.content,
                    'weight': ctx.weight,
                    'priority': ctx.priority.value,
                    'tokens_used': ctx.tokens_used,
                    'file_path': ctx.file_path,
                    'source': ctx.source,
                    'relevance': ctx.relevance
                })
            
            # Get context summary
            summary = self.smart_loader.get_context_summary(context)
            
            return ContextLoadingResult(
                success=True,
                context=context_data,
                task_type=task_type,
                budget_used=sum(ctx.tokens_used for ctx in context),
                sources_loaded=len(context),
                context_summary=summary
            )
            
        except Exception as e:
            return ContextLoadingResult(
                success=False,
                context=[],
                task_type=task_type,
                budget_used=0,
                sources_loaded=0,
                error_message=str(e)
            )
    
    def load_context_with_weights(self, task_type: str, weights: Dict[str, float], budget: int) -> ContextLoadingResult:
        """
        MCP tool for loading context with custom weights
        
        Args:
            task_type: Type of task
            weights: Custom weights for different context sources
            budget: Maximum tokens available
            
        Returns:
            ContextLoadingResult with loaded context
        """
        try:
            # Load base context
            base_context = self.smart_loader.load_context_for_task(task_type, budget)
            
            # Apply custom weights
            weighted_context = []
            for ctx in base_context:
                # Apply custom weight if available
                custom_weight = weights.get(ctx.file_path, ctx.weight)
                weighted_context.append(LoadedContext(
                    content=ctx.content,
                    weight=custom_weight,
                    priority=ctx.priority,
                    tokens_used=ctx.tokens_used,
                    file_path=ctx.file_path,
                    source=ctx.source,
                    relevance=ctx.relevance
                ))
            
            # Sort by custom weights
            weighted_context.sort(key=lambda x: x.weight, reverse=True)
            
            # Convert to serializable format
            context_data = []
            for ctx in weighted_context:
                context_data.append({
                    'content': ctx.content,
                    'weight': ctx.weight,
                    'priority': ctx.priority.value,
                    'tokens_used': ctx.tokens_used,
                    'file_path': ctx.file_path,
                    'source': ctx.source,
                    'relevance': ctx.relevance
                })
            
            return ContextLoadingResult(
                success=True,
                context=context_data,
                task_type=task_type,
                budget_used=sum(ctx.tokens_used for ctx in weighted_context),
                sources_loaded=len(weighted_context)
            )
            
        except Exception as e:
            return ContextLoadingResult(
                success=False,
                context=[],
                task_type=task_type,
                budget_used=0,
                sources_loaded=0,
                error_message=str(e)
            )
    
    def optimize_context_for_task(self, task_type: str, query: str, budget: int) -> ContextLoadingResult:
        """
        MCP tool for optimizing context based on task and query
        
        Args:
            task_type: Type of task
            query: Semantic query for optimization
            budget: Maximum tokens available
            
        Returns:
            ContextLoadingResult with optimized context
        """
        try:
            # Load context with semantic enhancement
            context = self.semantic_loader.load_context_with_semantic_enhancement(
                task_type, query, budget
            )
            
            # Convert to serializable format
            context_data = []
            for ctx in context:
                context_data.append({
                    'content': ctx.content,
                    'weight': ctx.weight,
                    'priority': ctx.priority.value,
                    'tokens_used': ctx.tokens_used,
                    'file_path': ctx.file_path,
                    'source': ctx.source,
                    'relevance': ctx.relevance
                })
            
            # Get context summary
            summary = self.semantic_loader.get_context_summary(context)
            
            return ContextLoadingResult(
                success=True,
                context=context_data,
                task_type=task_type,
                budget_used=sum(ctx.tokens_used for ctx in context),
                sources_loaded=len(context),
                context_summary=summary
            )
            
        except Exception as e:
            return ContextLoadingResult(
                success=False,
                context=[],
                task_type=task_type,
                budget_used=0,
                sources_loaded=0,
                error_message=str(e)
            )
    
    def get_available_bootloaders(self) -> List[str]:
        """
        Get list of available bootloader configurations
        
        Returns:
            List of available task types
        """
        try:
            bootloader_dir = self.smart_loader.bootloader_dir
            if not bootloader_dir.exists():
                return []
            
            bootloaders = []
            for yaml_file in bootloader_dir.glob("*.yaml"):
                bootloaders.append(yaml_file.stem)
            
            return bootloaders
            
        except Exception as e:
            return []
    
    def create_bootloader_config(self, task_type: str, config_data: Dict[str, Any]) -> bool:
        """
        Create or update bootloader configuration
        
        Args:
            task_type: Type of task
            config_data: Configuration data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import yaml
            
            config_path = self.smart_loader.bootloader_dir / f"{task_type}.yaml"
            
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            return True
            
        except Exception as e:
            return False
    
    def get_context_statistics(self, task_type: str) -> Dict[str, Any]:
        """
        Get context loading statistics for a task type
        
        Args:
            task_type: Type of task
            
        Returns:
            Statistics dictionary
        """
        try:
            # Load bootloader config
            bootloader = self.smart_loader.load_bootloader_config(task_type)
            
            # Calculate statistics
            total_sources = 0
            total_estimated_tokens = 0
            priority_counts = {}
            
            for source_type, sources in bootloader.context_sources.items():
                total_sources += len(sources)
                for source in sources:
                    total_estimated_tokens += source.estimated_tokens
                    priority_counts[source.priority.value] = priority_counts.get(source.priority.value, 0) + 1
            
            return {
                'task_type': task_type,
                'total_sources': total_sources,
                'total_estimated_tokens': total_estimated_tokens,
                'priority_distribution': priority_counts,
                'max_context_budget': bootloader.max_context_budget,
                'context_strategy': bootloader.context_strategy,
                'loading_strategy': bootloader.loading_strategy,
                'fallback_strategy': bootloader.fallback_strategy,
                'semantic_enhancement': bootloader.semantic_enhancement,
                'cross_session_continuity': bootloader.cross_session_continuity
            }
            
        except Exception as e:
            return {
                'task_type': task_type,
                'error': str(e)
            }


# MCP Tool Functions (for MCP server integration)
def mcp_load_bootloader_context(task_type: str, context_budget: int) -> Dict[str, Any]:
    """
    MCP tool function for loading context with bootloader
    
    Args:
        task_type: Type of task
        context_budget: Maximum tokens available
        
    Returns:
        Dictionary with context loading result
    """
    mcp_tools = ContextBootloaderMCP()
    result = mcp_tools.load_bootloader_context(task_type, context_budget)
    
    return {
        'success': result.success,
        'context': result.context,
        'task_type': result.task_type,
        'budget_used': result.budget_used,
        'sources_loaded': result.sources_loaded,
        'error_message': result.error_message,
        'context_summary': result.context_summary
    }


def mcp_load_context_with_weights(task_type: str, weights: Dict[str, float], budget: int) -> Dict[str, Any]:
    """
    MCP tool function for loading context with custom weights
    
    Args:
        task_type: Type of task
        weights: Custom weights for different context sources
        budget: Maximum tokens available
        
    Returns:
        Dictionary with context loading result
    """
    mcp_tools = ContextBootloaderMCP()
    result = mcp_tools.load_context_with_weights(task_type, weights, budget)
    
    return {
        'success': result.success,
        'context': result.context,
        'task_type': result.task_type,
        'budget_used': result.budget_used,
        'sources_loaded': result.sources_loaded,
        'error_message': result.error_message
    }


def mcp_optimize_context_for_task(task_type: str, query: str, budget: int) -> Dict[str, Any]:
    """
    MCP tool function for optimizing context based on task and query
    
    Args:
        task_type: Type of task
        query: Semantic query for optimization
        budget: Maximum tokens available
        
    Returns:
        Dictionary with optimized context result
    """
    mcp_tools = ContextBootloaderMCP()
    result = mcp_tools.optimize_context_for_task(task_type, query, budget)
    
    return {
        'success': result.success,
        'context': result.context,
        'task_type': result.task_type,
        'budget_used': result.budget_used,
        'sources_loaded': result.sources_loaded,
        'error_message': result.error_message,
        'context_summary': result.context_summary
    }


def mcp_get_available_bootloaders() -> List[str]:
    """
    MCP tool function for getting available bootloader configurations
    
    Returns:
        List of available task types
    """
    mcp_tools = ContextBootloaderMCP()
    return mcp_tools.get_available_bootloaders()


def mcp_get_context_statistics(task_type: str) -> Dict[str, Any]:
    """
    MCP tool function for getting context loading statistics
    
    Args:
        task_type: Type of task
        
    Returns:
        Statistics dictionary
    """
    mcp_tools = ContextBootloaderMCP()
    return mcp_tools.get_context_statistics(task_type)


# Example usage and testing
if __name__ == "__main__":
    # Create MCP tools
    mcp_tools = ContextBootloaderMCP()
    
    # Test context loading
    result = mcp_tools.load_bootloader_context("vif_implementation", 80000)
    print(f"Loaded {result.sources_loaded} sources with {result.budget_used} tokens")
    
    # Test available bootloaders
    bootloaders = mcp_tools.get_available_bootloaders()
    print(f"Available bootloaders: {bootloaders}")
    
    # Test statistics
    stats = mcp_tools.get_context_statistics("vif_implementation")
    print(f"Statistics: {stats}")
