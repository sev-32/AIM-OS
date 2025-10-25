"""
Adaptive Context Dumping System - Cost and Speed Optimized Context Management

This module provides adaptive context dumping strategies with cost optimization,
speed considerations, and various levels from full context to perfectly summarized.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# MCP imports for AIM-OS integration
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}


class ContextDumpLevel(Enum):
    """Levels of context dumping from full to perfectly summarized"""
    FULL = "full"                    # Complete context dump (expensive)
    DETAILED = "detailed"            # Detailed context with key insights (high cost)
    MODERATE = "moderate"            # Moderate context with summaries (medium cost)
    COMPRESSED = "compressed"        # Compressed context with key points (low cost)
    MINIMAL = "minimal"              # Minimal context with essential info (very low cost)
    PERFECTLY_SUMMARIZED = "perfectly_summarized"  # Perfect summary (lowest cost)


class ContextDumpStrategy(Enum):
    """Strategies for context dumping"""
    COST_OPTIMIZED = "cost_optimized"      # Optimize for cost
    SPEED_OPTIMIZED = "speed_optimized"    # Optimize for speed
    QUALITY_OPTIMIZED = "quality_optimized" # Optimize for quality
    BALANCED = "balanced"                  # Balance cost, speed, and quality
    ADAPTIVE = "adaptive"                  # Adapt based on context complexity


class ModelCostTier(Enum):
    """Model cost tiers for optimization"""
    PREMIUM = "premium"      # Expensive models (GPT-4, Claude-3.5)
    STANDARD = "standard"    # Standard models (GPT-3.5, Claude-3)
    ECONOMY = "economy"      # Economy models (GPT-3, smaller models)
    FREE = "free"           # Free models (local models, free tiers)


@dataclass
class ContextDumpConfig:
    """Configuration for context dumping"""
    dump_level: ContextDumpLevel
    strategy: ContextDumpStrategy
    model_cost_tier: ModelCostTier
    max_tokens: int
    max_cost: float  # Maximum cost in dollars
    max_time: float  # Maximum time in seconds
    quality_threshold: float  # Minimum quality threshold (0.0-1.0)
    compression_ratio: float  # Compression ratio for context


@dataclass
class ContextDumpResult:
    """Result of context dumping operation"""
    dump_id: str
    timestamp: datetime
    dump_level: ContextDumpLevel
    strategy: ContextDumpStrategy
    model_cost_tier: ModelCostTier
    context_size: int  # Size of dumped context
    token_count: int
    cost: float
    time_taken: float
    quality_score: float
    compression_ratio: float
    success: bool
    error_message: Optional[str] = None


class AdaptiveContextDumpingSystem:
    """
    Adaptive context dumping system with cost and speed optimization
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.context_dump_history: List[ContextDumpResult] = []
        self.cost_optimization_data: Dict[str, Any] = {}
        self.speed_optimization_data: Dict[str, Any] = {}
        self.quality_optimization_data: Dict[str, Any] = {}
        
        # Default configurations for different scenarios
        self.default_configs = {
            ContextDumpStrategy.COST_OPTIMIZED: ContextDumpConfig(
                dump_level=ContextDumpLevel.COMPRESSED,
                strategy=ContextDumpStrategy.COST_OPTIMIZED,
                model_cost_tier=ModelCostTier.ECONOMY,
                max_tokens=1000,
                max_cost=0.01,
                max_time=5.0,
                quality_threshold=0.7,
                compression_ratio=0.3
            ),
            ContextDumpStrategy.SPEED_OPTIMIZED: ContextDumpConfig(
                dump_level=ContextDumpLevel.MINIMAL,
                strategy=ContextDumpStrategy.SPEED_OPTIMIZED,
                model_cost_tier=ModelCostTier.STANDARD,
                max_tokens=500,
                max_cost=0.05,
                max_time=2.0,
                quality_threshold=0.6,
                compression_ratio=0.2
            ),
            ContextDumpStrategy.QUALITY_OPTIMIZED: ContextDumpConfig(
                dump_level=ContextDumpLevel.DETAILED,
                strategy=ContextDumpStrategy.QUALITY_OPTIMIZED,
                model_cost_tier=ModelCostTier.PREMIUM,
                max_tokens=5000,
                max_cost=0.50,
                max_time=30.0,
                quality_threshold=0.9,
                compression_ratio=0.8
            ),
            ContextDumpStrategy.BALANCED: ContextDumpConfig(
                dump_level=ContextDumpLevel.MODERATE,
                strategy=ContextDumpStrategy.BALANCED,
                model_cost_tier=ModelCostTier.STANDARD,
                max_tokens=2000,
                max_cost=0.10,
                max_time=10.0,
                quality_threshold=0.8,
                compression_ratio=0.5
            )
        }
    
    def dump_context_adaptive(
        self,
        context: Dict[str, Any],
        strategy: ContextDumpStrategy = ContextDumpStrategy.BALANCED,
        model_cost_tier: ModelCostTier = ModelCostTier.STANDARD
    ) -> ContextDumpResult:
        """
        Dump context using adaptive strategy based on cost, speed, and quality requirements
        """
        start_time = datetime.now()
        
        # Get configuration for strategy
        config = self._get_adaptive_config(strategy, model_cost_tier, context)
        
        # Determine optimal dump level based on context complexity
        optimal_level = self._determine_optimal_dump_level(context, config)
        
        # Dump context at optimal level
        dump_result = self._dump_context_at_level(context, optimal_level, config)
        
        # Calculate metrics
        time_taken = (datetime.now() - start_time).total_seconds()
        dump_result.time_taken = time_taken
        
        # Store result
        self.context_dump_history.append(dump_result)
        
        # Update optimization data
        self._update_optimization_data(dump_result)
        
        return dump_result
    
    def _get_adaptive_config(
        self, 
        strategy: ContextDumpStrategy, 
        model_cost_tier: ModelCostTier, 
        context: Dict[str, Any]
    ) -> ContextDumpConfig:
        """
        Get adaptive configuration based on strategy, model cost, and context complexity
        """
        base_config = self.default_configs[strategy]
        
        # Adjust based on model cost tier
        if model_cost_tier == ModelCostTier.PREMIUM:
            base_config.max_cost *= 2.0
            base_config.max_tokens = min(base_config.max_tokens * 2, 10000)
        elif model_cost_tier == ModelCostTier.ECONOMY:
            base_config.max_cost *= 0.5
            base_config.max_tokens = max(base_config.max_tokens // 2, 500)
        elif model_cost_tier == ModelCostTier.FREE:
            base_config.max_cost = 0.0
            base_config.max_tokens = 1000
        
        # Adjust based on context complexity
        context_complexity = self._calculate_context_complexity(context)
        if context_complexity > 0.8:
            # High complexity - allow more tokens and cost
            base_config.max_tokens = min(base_config.max_tokens * 1.5, 15000)
            base_config.max_cost *= 1.5
        elif context_complexity < 0.3:
            # Low complexity - reduce tokens and cost
            base_config.max_tokens = max(base_config.max_tokens // 2, 500)
            base_config.max_cost *= 0.7
        
        return base_config
    
    def _calculate_context_complexity(self, context: Dict[str, Any]) -> float:
        """
        Calculate context complexity (0.0-1.0)
        """
        complexity = 0.0
        
        # File count complexity
        files_read = context.get('files_read', [])
        complexity += min(len(files_read) * 0.05, 0.3)
        
        # Insight count complexity
        insights_gained = context.get('insights_gained', [])
        complexity += min(len(insights_gained) * 0.1, 0.2)
        
        # Decision count complexity
        decisions_made = context.get('decisions_made', [])
        complexity += min(len(decisions_made) * 0.1, 0.2)
        
        # Context budget complexity
        context_budget = context.get('context_budget_used', 0)
        complexity += min(context_budget / 100000, 0.3)  # Normalize to 100k tokens
        
        return min(complexity, 1.0)
    
    def _determine_optimal_dump_level(
        self, 
        context: Dict[str, Any], 
        config: ContextDumpConfig
    ) -> ContextDumpLevel:
        """
        Determine optimal dump level based on context and configuration
        """
        context_complexity = self._calculate_context_complexity(context)
        
        # Base level from config
        base_level = config.dump_level
        
        # Adjust based on complexity
        if context_complexity > 0.8:
            # High complexity - use more detailed level
            if base_level == ContextDumpLevel.MINIMAL:
                return ContextDumpLevel.COMPRESSED
            elif base_level == ContextDumpLevel.COMPRESSED:
                return ContextDumpLevel.MODERATE
            elif base_level == ContextDumpLevel.MODERATE:
                return ContextDumpLevel.DETAILED
            else:
                return ContextDumpLevel.FULL
        elif context_complexity < 0.3:
            # Low complexity - use more compressed level
            if base_level == ContextDumpLevel.FULL:
                return ContextDumpLevel.DETAILED
            elif base_level == ContextDumpLevel.DETAILED:
                return ContextDumpLevel.MODERATE
            elif base_level == ContextDumpLevel.MODERATE:
                return ContextDumpLevel.COMPRESSED
            else:
                return ContextDumpLevel.MINIMAL
        
        return base_level
    
    def _dump_context_at_level(
        self, 
        context: Dict[str, Any], 
        level: ContextDumpLevel, 
        config: ContextDumpConfig
    ) -> ContextDumpResult:
        """
        Dump context at specific level
        """
        dump_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            if level == ContextDumpLevel.FULL:
                dumped_context = self._dump_full_context(context)
            elif level == ContextDumpLevel.DETAILED:
                dumped_context = self._dump_detailed_context(context)
            elif level == ContextDumpLevel.MODERATE:
                dumped_context = self._dump_moderate_context(context)
            elif level == ContextDumpLevel.COMPRESSED:
                dumped_context = self._dump_compressed_context(context)
            elif level == ContextDumpLevel.MINIMAL:
                dumped_context = self._dump_minimal_context(context)
            elif level == ContextDumpLevel.PERFECTLY_SUMMARIZED:
                dumped_context = self._dump_perfectly_summarized_context(context)
            else:
                raise ValueError(f"Unknown dump level: {level}")
            
            # Calculate metrics
            context_size = len(json.dumps(dumped_context))
            token_count = self._estimate_token_count(dumped_context)
            cost = self._calculate_cost(token_count, config.model_cost_tier)
            time_taken = (datetime.now() - start_time).total_seconds()
            quality_score = self._calculate_quality_score(dumped_context, context)
            compression_ratio = context_size / len(json.dumps(context)) if context else 1.0
            
            return ContextDumpResult(
                dump_id=dump_id,
                timestamp=start_time,
                dump_level=level,
                strategy=config.strategy,
                model_cost_tier=config.model_cost_tier,
                context_size=context_size,
                token_count=token_count,
                cost=cost,
                time_taken=time_taken,
                quality_score=quality_score,
                compression_ratio=compression_ratio,
                success=True
            )
            
        except Exception as e:
            return ContextDumpResult(
                dump_id=dump_id,
                timestamp=start_time,
                dump_level=level,
                strategy=config.strategy,
                model_cost_tier=config.model_cost_tier,
                context_size=0,
                token_count=0,
                cost=0.0,
                time_taken=(datetime.now() - start_time).total_seconds(),
                quality_score=0.0,
                compression_ratio=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _dump_full_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump full context without compression
        """
        return context.copy()
    
    def _dump_detailed_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump detailed context with key insights highlighted
        """
        dumped = {
            'current_task': context.get('current_task', ''),
            'user_input': context.get('user_input', ''),
            'files_read': context.get('files_read', [])[:10],  # Limit to 10 files
            'insights_gained': context.get('insights_gained', []),
            'decisions_made': context.get('decisions_made', []),
            'confidence_levels': context.get('confidence_levels', {}),
            'context_budget_used': context.get('context_budget_used', 0),
            'tools_used': context.get('tools_used', [])[:5],  # Limit to 5 tools
            'mental_model': self._summarize_mental_model(context.get('mental_model', {}))
        }
        return dumped
    
    def _dump_moderate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump moderate context with summaries
        """
        dumped = {
            'current_task': context.get('current_task', ''),
            'user_input': context.get('user_input', ''),
            'files_read_summary': f"{len(context.get('files_read', []))} files read",
            'key_insights': context.get('insights_gained', [])[:3],  # Top 3 insights
            'key_decisions': context.get('decisions_made', [])[:2],  # Top 2 decisions
            'confidence_summary': self._summarize_confidence(context.get('confidence_levels', {})),
            'context_budget_used': context.get('context_budget_used', 0)
        }
        return dumped
    
    def _dump_compressed_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump compressed context with key points
        """
        dumped = {
            'task': context.get('current_task', ''),
            'input': context.get('user_input', '')[:100] + '...' if len(context.get('user_input', '')) > 100 else context.get('user_input', ''),
            'files_count': len(context.get('files_read', [])),
            'insights_count': len(context.get('insights_gained', [])),
            'decisions_count': len(context.get('decisions_made', [])),
            'confidence_avg': self._calculate_average_confidence(context.get('confidence_levels', {})),
            'budget_used': context.get('context_budget_used', 0)
        }
        return dumped
    
    def _dump_minimal_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump minimal context with essential info only
        """
        dumped = {
            'task': context.get('current_task', ''),
            'input': context.get('user_input', '')[:50] + '...' if len(context.get('user_input', '')) > 50 else context.get('user_input', ''),
            'files': len(context.get('files_read', [])),
            'insights': len(context.get('insights_gained', [])),
            'budget': context.get('context_budget_used', 0)
        }
        return dumped
    
    def _dump_perfectly_summarized_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dump perfectly summarized context
        """
        # Create a perfect summary using AI (this would be implemented with actual AI)
        summary = self._create_ai_summary(context)
        
        dumped = {
            'summary': summary,
            'key_metrics': {
                'files_read': len(context.get('files_read', [])),
                'insights_gained': len(context.get('insights_gained', [])),
                'decisions_made': len(context.get('decisions_made', [])),
                'context_budget_used': context.get('context_budget_used', 0)
            }
        }
        return dumped
    
    def _create_ai_summary(self, context: Dict[str, Any]) -> str:
        """
        Create AI-powered summary of context
        """
        # This would use actual AI to create a perfect summary
        # For now, create a basic summary
        task = context.get('current_task', 'Unknown task')
        files_count = len(context.get('files_read', []))
        insights_count = len(context.get('insights_gained', []))
        decisions_count = len(context.get('decisions_made', []))
        
        summary = f"Working on {task}. Read {files_count} files, gained {insights_count} insights, made {decisions_count} decisions."
        
        return summary
    
    def _summarize_mental_model(self, mental_model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize mental model
        """
        if not mental_model:
            return {}
        
        # Keep only top-level concepts
        summarized = {}
        for key, value in list(mental_model.items())[:5]:  # Limit to 5 concepts
            if isinstance(value, str) and len(value) > 100:
                summarized[key] = value[:100] + '...'
            else:
                summarized[key] = value
        
        return summarized
    
    def _summarize_confidence(self, confidence_levels: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize confidence levels
        """
        if not confidence_levels:
            return {}
        
        # Calculate average confidence
        avg_confidence = sum(confidence_levels.values()) / len(confidence_levels)
        
        return {
            'average': avg_confidence,
            'high_confidence_areas': [k for k, v in confidence_levels.items() if v > 0.8],
            'low_confidence_areas': [k for k, v in confidence_levels.items() if v < 0.5]
        }
    
    def _calculate_average_confidence(self, confidence_levels: Dict[str, Any]) -> float:
        """
        Calculate average confidence
        """
        if not confidence_levels:
            return 0.0
        
        return sum(confidence_levels.values()) / len(confidence_levels)
    
    def _estimate_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for context
        """
        # Simple estimation: 1 token ≈ 4 characters
        context_str = json.dumps(context)
        return len(context_str) // 4
    
    def _calculate_cost(self, token_count: int, model_cost_tier: ModelCostTier) -> float:
        """
        Calculate cost based on token count and model cost tier
        """
        # Cost per 1k tokens (rough estimates)
        cost_per_1k_tokens = {
            ModelCostTier.PREMIUM: 0.03,    # $0.03 per 1k tokens
            ModelCostTier.STANDARD: 0.002,  # $0.002 per 1k tokens
            ModelCostTier.ECONOMY: 0.001,   # $0.001 per 1k tokens
            ModelCostTier.FREE: 0.0         # Free
        }
        
        cost_per_token = cost_per_1k_tokens[model_cost_tier] / 1000
        return token_count * cost_per_token
    
    def _calculate_quality_score(self, dumped_context: Dict[str, Any], original_context: Dict[str, Any]) -> float:
        """
        Calculate quality score for dumped context
        """
        if not original_context:
            return 1.0
        
        # Calculate information retention ratio
        original_size = len(json.dumps(original_context))
        dumped_size = len(json.dumps(dumped_context))
        
        if original_size == 0:
            return 1.0
        
        # Quality based on information retention and structure
        retention_ratio = dumped_size / original_size
        structure_score = 1.0 if 'current_task' in dumped_context else 0.8
        
        return min(retention_ratio * structure_score, 1.0)
    
    def _update_optimization_data(self, dump_result: ContextDumpResult):
        """
        Update optimization data based on dump result
        """
        # Update cost optimization data
        if dump_result.strategy == ContextDumpStrategy.COST_OPTIMIZED:
            self.cost_optimization_data[dump_result.dump_level.value] = {
                'avg_cost': dump_result.cost,
                'avg_quality': dump_result.quality_score,
                'avg_time': dump_result.time_taken
            }
        
        # Update speed optimization data
        if dump_result.strategy == ContextDumpStrategy.SPEED_OPTIMIZED:
            self.speed_optimization_data[dump_result.dump_level.value] = {
                'avg_time': dump_result.time_taken,
                'avg_quality': dump_result.quality_score,
                'avg_cost': dump_result.cost
            }
        
        # Update quality optimization data
        if dump_result.strategy == ContextDumpStrategy.QUALITY_OPTIMIZED:
            self.quality_optimization_data[dump_result.dump_level.value] = {
                'avg_quality': dump_result.quality_score,
                'avg_cost': dump_result.cost,
                'avg_time': dump_result.time_taken
            }
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get optimization recommendations based on historical data
        """
        recommendations = {
            'cost_optimization': self._get_cost_optimization_recommendations(),
            'speed_optimization': self._get_speed_optimization_recommendations(),
            'quality_optimization': self._get_quality_optimization_recommendations(),
            'balanced_optimization': self._get_balanced_optimization_recommendations()
        }
        
        return recommendations
    
    def _get_cost_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get cost optimization recommendations
        """
        if not self.cost_optimization_data:
            return {'message': 'No cost optimization data available'}
        
        # Find best cost/quality ratio
        best_ratio = 0.0
        best_level = None
        
        for level, data in self.cost_optimization_data.items():
            if data['avg_quality'] > 0:
                ratio = data['avg_quality'] / data['avg_cost']
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_level = level
        
        return {
            'recommended_level': best_level,
            'cost_quality_ratio': best_ratio,
            'data': self.cost_optimization_data
        }
    
    def _get_speed_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get speed optimization recommendations
        """
        if not self.speed_optimization_data:
            return {'message': 'No speed optimization data available'}
        
        # Find fastest level with acceptable quality
        fastest_level = None
        fastest_time = float('inf')
        
        for level, data in self.speed_optimization_data.items():
            if data['avg_time'] < fastest_time and data['avg_quality'] > 0.6:
                fastest_time = data['avg_time']
                fastest_level = level
        
        return {
            'recommended_level': fastest_level,
            'fastest_time': fastest_time,
            'data': self.speed_optimization_data
        }
    
    def _get_quality_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get quality optimization recommendations
        """
        if not self.quality_optimization_data:
            return {'message': 'No quality optimization data available'}
        
        # Find highest quality level
        highest_quality = 0.0
        best_level = None
        
        for level, data in self.quality_optimization_data.items():
            if data['avg_quality'] > highest_quality:
                highest_quality = data['avg_quality']
                best_level = level
        
        return {
            'recommended_level': best_level,
            'highest_quality': highest_quality,
            'data': self.quality_optimization_data
        }
    
    def _get_balanced_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get balanced optimization recommendations
        """
        # Combine all optimization data
        all_data = {}
        
        for level in ContextDumpLevel:
            level_data = {
                'cost': 0.0,
                'time': 0.0,
                'quality': 0.0,
                'count': 0
            }
            
            # Aggregate data from all strategies
            for strategy_data in [self.cost_optimization_data, self.speed_optimization_data, self.quality_optimization_data]:
                if level.value in strategy_data:
                    data = strategy_data[level.value]
                    level_data['cost'] += data.get('avg_cost', 0)
                    level_data['time'] += data.get('avg_time', 0)
                    level_data['quality'] += data.get('avg_quality', 0)
                    level_data['count'] += 1
            
            if level_data['count'] > 0:
                level_data['cost'] /= level_data['count']
                level_data['time'] /= level_data['count']
                level_data['quality'] /= level_data['count']
                all_data[level.value] = level_data
        
        # Find best balanced level
        best_score = 0.0
        best_level = None
        
        for level, data in all_data.items():
            # Balanced score: quality / (cost + time)
            if data['cost'] + data['time'] > 0:
                score = data['quality'] / (data['cost'] + data['time'])
                if score > best_score:
                    best_score = score
                    best_level = level
        
        return {
            'recommended_level': best_level,
            'balanced_score': best_score,
            'data': all_data
        }


# Example usage and testing
if __name__ == "__main__":
    # Create adaptive context dumping system
    dumping_system = AdaptiveContextDumpingSystem()
    
    # Sample context
    sample_context = {
        'current_task': 'vif_implementation',
        'user_input': 'Implement VIF witness envelopes with comprehensive validation',
        'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md', 'knowledge_architecture/systems/vif/L2_architecture.md'],
        'insights_gained': ['VIF requires comprehensive witness envelopes', 'Witness envelopes need bitemporal versioning'],
        'decisions_made': [{'decision': 'Use L3 documentation for VIF implementation'}],
        'confidence_levels': {'vif_implementation': 0.85, 'witness_envelopes': 0.75},
        'context_budget_used': 15000,
        'tools_used': ['read_file', 'write', 'grep'],
        'mental_model': {'vif': 'Verifiable Intelligence Framework', 'cmc': 'Context Memory Core'}
    }
    
    # Test different strategies
    strategies = [
        ContextDumpStrategy.COST_OPTIMIZED,
        ContextDumpStrategy.SPEED_OPTIMIZED,
        ContextDumpStrategy.QUALITY_OPTIMIZED,
        ContextDumpStrategy.BALANCED
    ]
    
    for strategy in strategies:
        result = dumping_system.dump_context_adaptive(
            sample_context,
            strategy=strategy,
            model_cost_tier=ModelCostTier.STANDARD
        )
        
        print(f"\n{strategy.value} Strategy:")
        print(f"  Level: {result.dump_level.value}")
        print(f"  Cost: ${result.cost:.4f}")
        print(f"  Time: {result.time_taken:.2f}s")
        print(f"  Quality: {result.quality_score:.2f}")
        print(f"  Compression: {result.compression_ratio:.2f}")
    
    # Get optimization recommendations
    recommendations = dumping_system.get_optimization_recommendations()
    print(f"\nOptimization Recommendations: {recommendations}")
