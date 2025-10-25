"""
Automated Context Dumping System - Prevent Context Resets with Smart Dumping

This module provides automated context dumping that monitors context usage
and automatically dumps context when approaching capacity limits to prevent resets.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

# MCP imports for AIM-OS integration
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}


class ContextDumpTrigger(Enum):
    """Triggers for automated context dumping"""
    CAPACITY_THRESHOLD = "capacity_threshold"      # Near capacity limit
    TIME_THRESHOLD = "time_threshold"              # Time-based threshold
    QUALITY_THRESHOLD = "quality_threshold"        # Quality degradation
    MANUAL = "manual"                              # Manual trigger
    EMERGENCY = "emergency"                        # Emergency dump


class ContextDumpStrategy(Enum):
    """Strategies for automated context dumping"""
    INCREMENTAL = "incremental"        # Dump incrementally as needed
    FULL_DUMP = "full_dump"            # Full context dump
    SELECTIVE_DUMP = "selective_dump"  # Selective dump of important context
    COMPRESSED_DUMP = "compressed_dump" # Compressed dump
    EMERGENCY_DUMP = "emergency_dump"  # Emergency dump


@dataclass
class ContextUsageMetrics:
    """Metrics for context usage monitoring"""
    current_tokens: int
    max_tokens: int
    usage_percentage: float
    time_since_last_dump: float  # seconds
    context_quality: float
    context_complexity: float
    files_read_count: int
    insights_gained_count: int
    decisions_made_count: int


@dataclass
class ContextDumpAlert:
    """Alert for context dumping"""
    alert_id: str
    timestamp: datetime
    trigger: ContextDumpTrigger
    current_usage: ContextUsageMetrics
    recommended_strategy: ContextDumpStrategy
    urgency_level: int  # 1-10 scale
    estimated_dump_size: int
    estimated_dump_time: float
    message: str


@dataclass
class ContextDumpResult:
    """Result of automated context dump"""
    dump_id: str
    timestamp: datetime
    trigger: ContextDumpTrigger
    strategy: ContextDumpStrategy
    context_size_before: int
    context_size_after: int
    tokens_freed: int
    dump_size: int
    dump_time: float
    success: bool
    error_message: Optional[str] = None


class AutomatedContextDumpingSystem:
    """
    Automated context dumping system that monitors context usage
    and automatically dumps context to prevent resets
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.context_dump_history: List[ContextDumpResult] = []
        self.context_dump_alerts: List[ContextDumpAlert] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.capacity_threshold = 0.85  # 85% capacity threshold
        self.time_threshold = 300.0     # 5 minutes threshold
        self.quality_threshold = 0.7    # Quality threshold
        self.emergency_threshold = 0.95  # 95% emergency threshold
        
        # Callbacks for different events
        self.on_capacity_alert: Optional[Callable[[ContextDumpAlert], None]] = None
        self.on_dump_complete: Optional[Callable[[ContextDumpResult], None]] = None
        self.on_emergency_dump: Optional[Callable[[ContextDumpResult], None]] = None
        
        # Context tracking
        self.current_context: Dict[str, Any] = {}
        self.last_dump_time: Optional[datetime] = None
        self.context_usage_history: List[ContextUsageMetrics] = []
    
    def start_monitoring(self, context_getter: Callable[[], Dict[str, Any]]):
        """
        Start monitoring context usage
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(context_getter,),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """
        Stop monitoring context usage
        """
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitoring_loop(self, context_getter: Callable[[], Dict[str, Any]]):
        """
        Main monitoring loop
        """
        while self.monitoring_active:
            try:
                # Get current context
                current_context = context_getter()
                self.current_context = current_context
                
                # Calculate usage metrics
                usage_metrics = self._calculate_usage_metrics(current_context)
                self.context_usage_history.append(usage_metrics)
                
                # Check for dump triggers
                alert = self._check_dump_triggers(usage_metrics)
                if alert:
                    self._handle_dump_alert(alert)
                
                # Sleep for monitoring interval
                time.sleep(10.0)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(30.0)  # Wait longer on error
    
    def _calculate_usage_metrics(self, context: Dict[str, Any]) -> ContextUsageMetrics:
        """
        Calculate context usage metrics
        """
        # Estimate current token usage
        current_tokens = self._estimate_token_count(context)
        
        # Get max tokens (this would be from the actual model context limit)
        max_tokens = 128000  # Default for GPT-4 context limit
        
        # Calculate usage percentage
        usage_percentage = current_tokens / max_tokens
        
        # Calculate time since last dump
        time_since_last_dump = 0.0
        if self.last_dump_time:
            time_since_last_dump = (datetime.now() - self.last_dump_time).total_seconds()
        
        # Calculate context quality
        context_quality = self._calculate_context_quality(context)
        
        # Calculate context complexity
        context_complexity = self._calculate_context_complexity(context)
        
        # Count various context elements
        files_read_count = len(context.get('files_read', []))
        insights_gained_count = len(context.get('insights_gained', []))
        decisions_made_count = len(context.get('decisions_made', []))
        
        return ContextUsageMetrics(
            current_tokens=current_tokens,
            max_tokens=max_tokens,
            usage_percentage=usage_percentage,
            time_since_last_dump=time_since_last_dump,
            context_quality=context_quality,
            context_complexity=context_complexity,
            files_read_count=files_read_count,
            insights_gained_count=insights_gained_count,
            decisions_made_count=decisions_made_count
        )
    
    def _check_dump_triggers(self, usage_metrics: ContextUsageMetrics) -> Optional[ContextDumpAlert]:
        """
        Check if any dump triggers are activated
        """
        # Check capacity threshold
        if usage_metrics.usage_percentage >= self.emergency_threshold:
            return self._create_alert(
                ContextDumpTrigger.EMERGENCY,
                usage_metrics,
                ContextDumpStrategy.EMERGENCY_DUMP,
                urgency_level=10,
                message=f"EMERGENCY: Context usage at {usage_metrics.usage_percentage:.1%} - immediate dump required!"
            )
        elif usage_metrics.usage_percentage >= self.capacity_threshold:
            return self._create_alert(
                ContextDumpTrigger.CAPACITY_THRESHOLD,
                usage_metrics,
                ContextDumpStrategy.SELECTIVE_DUMP,
                urgency_level=8,
                message=f"Context usage at {usage_metrics.usage_percentage:.1%} - dump recommended"
            )
        
        # Check time threshold
        if usage_metrics.time_since_last_dump >= self.time_threshold:
            return self._create_alert(
                ContextDumpTrigger.TIME_THRESHOLD,
                usage_metrics,
                ContextDumpStrategy.INCREMENTAL,
                urgency_level=5,
                message=f"Time threshold reached ({usage_metrics.time_since_last_dump:.0f}s) - incremental dump recommended"
            )
        
        # Check quality threshold
        if usage_metrics.context_quality < self.quality_threshold:
            return self._create_alert(
                ContextDumpTrigger.QUALITY_THRESHOLD,
                usage_metrics,
                ContextDumpStrategy.COMPRESSED_DUMP,
                urgency_level=6,
                message=f"Context quality degraded ({usage_metrics.context_quality:.2f}) - compressed dump recommended"
            )
        
        return None
    
    def _create_alert(
        self,
        trigger: ContextDumpTrigger,
        usage_metrics: ContextUsageMetrics,
        strategy: ContextDumpStrategy,
        urgency_level: int,
        message: str
    ) -> ContextDumpAlert:
        """
        Create a context dump alert
        """
        # Estimate dump size and time
        estimated_dump_size = self._estimate_dump_size(usage_metrics, strategy)
        estimated_dump_time = self._estimate_dump_time(estimated_dump_size, strategy)
        
        alert = ContextDumpAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            trigger=trigger,
            current_usage=usage_metrics,
            recommended_strategy=strategy,
            urgency_level=urgency_level,
            estimated_dump_size=estimated_dump_size,
            estimated_dump_time=estimated_dump_time,
            message=message
        )
        
        self.context_dump_alerts.append(alert)
        return alert
    
    def _handle_dump_alert(self, alert: ContextDumpAlert):
        """
        Handle a context dump alert
        """
        # Call alert callback if set
        if self.on_capacity_alert:
            self.on_capacity_alert(alert)
        
        # Perform automated dump
        result = self.perform_automated_dump(alert)
        
        # Call completion callback if set
        if self.on_dump_complete:
            self.on_dump_complete(result)
        
        # Call emergency callback if emergency
        if alert.trigger == ContextDumpTrigger.EMERGENCY and self.on_emergency_dump:
            self.on_emergency_dump(result)
    
    def perform_automated_dump(self, alert: ContextDumpAlert) -> ContextDumpResult:
        """
        Perform automated context dump based on alert
        """
        dump_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Get context size before dump
            context_size_before = self._estimate_token_count(self.current_context)
            
            # Perform dump based on strategy
            if alert.recommended_strategy == ContextDumpStrategy.EMERGENCY_DUMP:
                dumped_context = self._emergency_dump(self.current_context)
            elif alert.recommended_strategy == ContextDumpStrategy.FULL_DUMP:
                dumped_context = self._full_dump(self.current_context)
            elif alert.recommended_strategy == ContextDumpStrategy.SELECTIVE_DUMP:
                dumped_context = self._selective_dump(self.current_context)
            elif alert.recommended_strategy == ContextDumpStrategy.COMPRESSED_DUMP:
                dumped_context = self._compressed_dump(self.current_context)
            elif alert.recommended_strategy == ContextDumpStrategy.INCREMENTAL:
                dumped_context = self._incremental_dump(self.current_context)
            else:
                raise ValueError(f"Unknown dump strategy: {alert.recommended_strategy}")
            
            # Calculate metrics
            dump_time = (datetime.now() - start_time).total_seconds()
            context_size_after = self._estimate_token_count(dumped_context)
            tokens_freed = context_size_before - context_size_after
            dump_size = self._estimate_token_count(dumped_context)
            
            # Update last dump time
            self.last_dump_time = datetime.now()
            
            # Store in MCP for persistence
            self._store_dump_in_mcp(dumped_context, alert)
            
            result = ContextDumpResult(
                dump_id=dump_id,
                timestamp=start_time,
                trigger=alert.trigger,
                strategy=alert.recommended_strategy,
                context_size_before=context_size_before,
                context_size_after=context_size_after,
                tokens_freed=tokens_freed,
                dump_size=dump_size,
                dump_time=dump_time,
                success=True
            )
            
            self.context_dump_history.append(result)
            return result
            
        except Exception as e:
            result = ContextDumpResult(
                dump_id=dump_id,
                timestamp=start_time,
                trigger=alert.trigger,
                strategy=alert.recommended_strategy,
                context_size_before=0,
                context_size_after=0,
                tokens_freed=0,
                dump_size=0,
                dump_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error_message=str(e)
            )
            
            self.context_dump_history.append(result)
            return result
    
    def _emergency_dump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Emergency dump - minimal context to prevent reset
        """
        return {
            'emergency_dump': True,
            'timestamp': datetime.now().isoformat(),
            'current_task': context.get('current_task', ''),
            'user_input': context.get('user_input', '')[:100] + '...' if len(context.get('user_input', '')) > 100 else context.get('user_input', ''),
            'key_insights': context.get('insights_gained', [])[:2],
            'confidence_levels': {k: v for k, v in list(context.get('confidence_levels', {}).items())[:3]},
            'context_budget_used': context.get('context_budget_used', 0)
        }
    
    def _full_dump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full dump - complete context
        """
        return context.copy()
    
    def _selective_dump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Selective dump - important context only
        """
        return {
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
    
    def _compressed_dump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compressed dump - compressed context
        """
        return {
            'current_task': context.get('current_task', ''),
            'user_input': context.get('user_input', '')[:200] + '...' if len(context.get('user_input', '')) > 200 else context.get('user_input', ''),
            'files_read_summary': f"{len(context.get('files_read', []))} files read",
            'key_insights': context.get('insights_gained', [])[:3],  # Top 3 insights
            'key_decisions': context.get('decisions_made', [])[:2],  # Top 2 decisions
            'confidence_summary': self._summarize_confidence(context.get('confidence_levels', {})),
            'context_budget_used': context.get('context_budget_used', 0)
        }
    
    def _incremental_dump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Incremental dump - incremental context cleanup
        """
        # Remove old/less important context
        cleaned_context = context.copy()
        
        # Remove old files (keep only recent ones)
        files_read = cleaned_context.get('files_read', [])
        if len(files_read) > 5:
            cleaned_context['files_read'] = files_read[-5:]  # Keep only last 5 files
        
        # Remove old insights (keep only recent ones)
        insights_gained = cleaned_context.get('insights_gained', [])
        if len(insights_gained) > 5:
            cleaned_context['insights_gained'] = insights_gained[-5:]  # Keep only last 5 insights
        
        # Remove old decisions (keep only recent ones)
        decisions_made = cleaned_context.get('decisions_made', [])
        if len(decisions_made) > 3:
            cleaned_context['decisions_made'] = decisions_made[-3:]  # Keep only last 3 decisions
        
        return cleaned_context
    
    def _estimate_dump_size(self, usage_metrics: ContextUsageMetrics, strategy: ContextDumpStrategy) -> int:
        """
        Estimate dump size based on strategy
        """
        base_size = usage_metrics.current_tokens
        
        if strategy == ContextDumpStrategy.EMERGENCY_DUMP:
            return base_size // 10  # 10% of original size
        elif strategy == ContextDumpStrategy.FULL_DUMP:
            return base_size  # 100% of original size
        elif strategy == ContextDumpStrategy.SELECTIVE_DUMP:
            return base_size // 2  # 50% of original size
        elif strategy == ContextDumpStrategy.COMPRESSED_DUMP:
            return base_size // 3  # 33% of original size
        elif strategy == ContextDumpStrategy.INCREMENTAL:
            return base_size // 4  # 25% of original size
        else:
            return base_size // 2  # Default to 50%
    
    def _estimate_dump_time(self, dump_size: int, strategy: ContextDumpStrategy) -> float:
        """
        Estimate dump time based on size and strategy
        """
        base_time = dump_size / 1000  # Base time in seconds
        
        if strategy == ContextDumpStrategy.EMERGENCY_DUMP:
            return base_time * 0.5  # Faster for emergency
        elif strategy == ContextDumpStrategy.FULL_DUMP:
            return base_time * 2.0  # Slower for full dump
        else:
            return base_time  # Default time
    
    def _estimate_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for context
        """
        # Simple estimation: 1 token ≈ 4 characters
        context_str = json.dumps(context)
        return len(context_str) // 4
    
    def _calculate_context_quality(self, context: Dict[str, Any]) -> float:
        """
        Calculate context quality score
        """
        quality = 1.0
        
        # Check for essential elements
        if not context.get('current_task'):
            quality -= 0.2
        if not context.get('user_input'):
            quality -= 0.2
        if not context.get('files_read'):
            quality -= 0.1
        if not context.get('insights_gained'):
            quality -= 0.1
        if not context.get('decisions_made'):
            quality -= 0.1
        
        return max(0.0, quality)
    
    def _calculate_context_complexity(self, context: Dict[str, Any]) -> float:
        """
        Calculate context complexity
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
    
    def _store_dump_in_mcp(self, dumped_context: Dict[str, Any], alert: ContextDumpAlert):
        """
        Store dumped context in MCP for persistence
        """
        try:
            self.mcp_client.store_memory({
                'type': 'automated_context_dump',
                'dump_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'trigger': alert.trigger.value,
                'strategy': alert.recommended_strategy.value,
                'urgency_level': alert.urgency_level,
                'context': dumped_context
            })
        except Exception as e:
            print(f"Error storing context dump in MCP: {e}")
    
    def get_context_usage_status(self) -> Dict[str, Any]:
        """
        Get current context usage status
        """
        if not self.context_usage_history:
            return {'status': 'no_data'}
        
        latest_usage = self.context_usage_history[-1]
        
        return {
            'current_tokens': latest_usage.current_tokens,
            'max_tokens': latest_usage.max_tokens,
            'usage_percentage': latest_usage.usage_percentage,
            'time_since_last_dump': latest_usage.time_since_last_dump,
            'context_quality': latest_usage.context_quality,
            'context_complexity': latest_usage.context_complexity,
            'files_read_count': latest_usage.files_read_count,
            'insights_gained_count': latest_usage.insights_gained_count,
            'decisions_made_count': latest_usage.decisions_made_count,
            'status': 'monitoring_active' if self.monitoring_active else 'monitoring_inactive'
        }
    
    def get_dump_history(self) -> List[ContextDumpResult]:
        """
        Get context dump history
        """
        return self.context_dump_history.copy()
    
    def get_alert_history(self) -> List[ContextDumpAlert]:
        """
        Get context dump alert history
        """
        return self.context_dump_alerts.copy()
    
    def force_emergency_dump(self) -> ContextDumpResult:
        """
        Force an emergency context dump
        """
        # Create emergency alert
        emergency_usage = ContextUsageMetrics(
            current_tokens=self._estimate_token_count(self.current_context),
            max_tokens=128000,
            usage_percentage=1.0,
            time_since_last_dump=0.0,
            context_quality=1.0,
            context_complexity=1.0,
            files_read_count=len(self.current_context.get('files_read', [])),
            insights_gained_count=len(self.current_context.get('insights_gained', [])),
            decisions_made_count=len(self.current_context.get('decisions_made', []))
        )
        
        emergency_alert = self._create_alert(
            ContextDumpTrigger.EMERGENCY,
            emergency_usage,
            ContextDumpStrategy.EMERGENCY_DUMP,
            urgency_level=10,
            message="FORCED EMERGENCY DUMP"
        )
        
        return self.perform_automated_dump(emergency_alert)


# Example usage and testing
if __name__ == "__main__":
    # Create automated context dumping system
    dumping_system = AutomatedContextDumpingSystem()
    
    # Set up callbacks
    def on_capacity_alert(alert: ContextDumpAlert):
        print(f"🚨 CAPACITY ALERT: {alert.message}")
        print(f"   Usage: {alert.current_usage.usage_percentage:.1%}")
        print(f"   Strategy: {alert.recommended_strategy.value}")
        print(f"   Urgency: {alert.urgency_level}/10")
    
    def on_dump_complete(result: ContextDumpResult):
        print(f"✅ DUMP COMPLETE: {result.dump_id}")
        print(f"   Tokens freed: {result.tokens_freed}")
        print(f"   Dump time: {result.dump_time:.2f}s")
        print(f"   Success: {result.success}")
    
    def on_emergency_dump(result: ContextDumpResult):
        print(f"🚨 EMERGENCY DUMP: {result.dump_id}")
        print(f"   Tokens freed: {result.tokens_freed}")
        print(f"   Dump time: {result.dump_time:.2f}s")
    
    dumping_system.on_capacity_alert = on_capacity_alert
    dumping_system.on_dump_complete = on_dump_complete
    dumping_system.on_emergency_dump = on_emergency_dump
    
    # Sample context getter
    def get_current_context():
        return {
            'current_task': 'vif_implementation',
            'user_input': 'Implement VIF witness envelopes with comprehensive validation',
            'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md'] * 50,  # Simulate high usage
            'insights_gained': ['VIF requires comprehensive witness envelopes'] * 20,
            'decisions_made': [{'decision': 'Use L3 documentation for VIF implementation'}] * 10,
            'confidence_levels': {'vif_implementation': 0.85, 'witness_envelopes': 0.75},
            'context_budget_used': 100000,  # High usage
            'tools_used': ['read_file', 'write', 'grep'],
            'mental_model': {'vif': 'Verifiable Intelligence Framework', 'cmc': 'Context Memory Core'}
        }
    
    # Start monitoring
    dumping_system.start_monitoring(get_current_context)
    
    # Simulate monitoring for a bit
    time.sleep(15.0)
    
    # Get status
    status = dumping_system.get_context_usage_status()
    print(f"Context Usage Status: {status}")
    
    # Get dump history
    dump_history = dumping_system.get_dump_history()
    print(f"Dump History: {len(dump_history)} dumps")
    
    # Get alert history
    alert_history = dumping_system.get_alert_history()
    print(f"Alert History: {len(alert_history)} alerts")
    
    # Stop monitoring
    dumping_system.stop_monitoring()
