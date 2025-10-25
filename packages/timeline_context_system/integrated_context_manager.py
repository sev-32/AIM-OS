"""
Integrated Context Manager - Complete Context Management System

This module provides integrated context management that combines
automated context dumping, capacity monitoring, and cost optimization
into a unified system for preventing context resets.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

# Import our context management modules
from .automated_context_dumping import (
    AutomatedContextDumpingSystem, 
    ContextDumpTrigger, 
    ContextDumpStrategy,
    ContextDumpResult
)
from .context_capacity_monitor import (
    ContextCapacityMonitor, 
    CapacityAlertLevel, 
    CapacityAlert
)
from .cost_optimized_journaling import (
    CostOptimizedJournalingSystem,
    JournalingStrategy,
    ModelTier
)

# MCP imports for AIM-OS integration
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}


class ContextManagerMode(Enum):
    """Operating modes for context manager"""
    AUTOMATIC = "automatic"      # Fully automatic context management
    SEMI_AUTOMATIC = "semi_automatic"  # Automatic with user confirmation
    MANUAL = "manual"           # Manual context management
    EMERGENCY = "emergency"     # Emergency mode with immediate dumps


@dataclass
class ContextManagerConfig:
    """Configuration for integrated context manager"""
    mode: ContextManagerMode
    max_tokens: int
    capacity_thresholds: Dict[str, float]
    dump_strategies: Dict[str, str]
    journaling_strategy: str
    model_tier: str
    monitoring_interval: float
    auto_dump_enabled: bool
    cost_optimization_enabled: bool


@dataclass
class ContextManagerStatus:
    """Status of integrated context manager"""
    is_active: bool
    mode: ContextManagerMode
    current_tokens: int
    max_tokens: int
    usage_percentage: float
    last_dump_time: Optional[datetime]
    dump_count: int
    alert_count: int
    monitoring_active: bool
    cost_optimization_active: bool


class IntegratedContextManager:
    """
    Integrated context manager that combines all context management systems
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        
        # Initialize subsystems
        self.automated_dumping = AutomatedContextDumpingSystem(mcp_client)
        self.capacity_monitor = ContextCapacityMonitor(mcp_client)
        self.cost_optimized_journaling = CostOptimizedJournalingSystem(mcp_client)
        
        # Configuration
        self.config = ContextManagerConfig(
            mode=ContextManagerMode.AUTOMATIC,
            max_tokens=128000,
            capacity_thresholds={
                'warning': 0.70,
                'critical': 0.85,
                'emergency': 0.95
            },
            dump_strategies={
                'warning': 'incremental',
                'critical': 'selective',
                'emergency': 'emergency'
            },
            journaling_strategy='adaptive_depth',
            model_tier='standard',
            monitoring_interval=5.0,
            auto_dump_enabled=True,
            cost_optimization_enabled=True
        )
        
        # State
        self.is_active = False
        self.context_getter: Optional[Callable[[], Dict[str, Any]]] = None
        self.last_dump_time: Optional[datetime] = None
        self.dump_count = 0
        self.alert_count = 0
        
        # Callbacks
        self.on_context_dump: Optional[Callable[[ContextDumpResult], None]] = None
        self.on_capacity_alert: Optional[Callable[[CapacityAlert], None]] = None
        self.on_emergency_dump: Optional[Callable[[ContextDumpResult], None]] = None
        
        # Set up subsystem callbacks
        self._setup_subsystem_callbacks()
    
    def _setup_subsystem_callbacks(self):
        """
        Set up callbacks for subsystems
        """
        # Set up automated dumping callbacks
        self.automated_dumping.on_capacity_alert = self._handle_dump_alert
        self.automated_dumping.on_dump_complete = self._handle_dump_complete
        self.automated_dumping.on_emergency_dump = self._handle_emergency_dump
        
        # Set up capacity monitor callbacks
        self.capacity_monitor.on_capacity_alert = self._handle_capacity_alert
        self.capacity_monitor.on_emergency_alert = self._handle_emergency_alert
    
    def start_context_management(self, context_getter: Callable[[], Dict[str, Any]]):
        """
        Start integrated context management
        """
        if self.is_active:
            return
        
        self.context_getter = context_getter
        self.is_active = True
        
        # Start subsystems
        if self.config.auto_dump_enabled:
            self.automated_dumping.start_monitoring(context_getter)
        
        self.capacity_monitor.start_monitoring(context_getter)
        
        print("🚀 Integrated Context Manager started")
    
    def stop_context_management(self):
        """
        Stop integrated context management
        """
        if not self.is_active:
            return
        
        self.is_active = False
        
        # Stop subsystems
        self.automated_dumping.stop_monitoring()
        self.capacity_monitor.stop_monitoring()
        
        print("🛑 Integrated Context Manager stopped")
    
    def _handle_dump_alert(self, alert):
        """
        Handle dump alert from automated dumping system
        """
        self.alert_count += 1
        
        if self.on_capacity_alert:
            self.on_capacity_alert(alert)
        
        print(f"🚨 DUMP ALERT: {alert.message}")
    
    def _handle_dump_complete(self, result: ContextDumpResult):
        """
        Handle dump completion from automated dumping system
        """
        self.dump_count += 1
        self.last_dump_time = result.timestamp
        
        if self.on_context_dump:
            self.on_context_dump(result)
        
        print(f"✅ DUMP COMPLETE: {result.tokens_freed} tokens freed")
    
    def _handle_emergency_dump(self, result: ContextDumpResult):
        """
        Handle emergency dump from automated dumping system
        """
        self.dump_count += 1
        self.last_dump_time = result.timestamp
        
        if self.on_emergency_dump:
            self.on_emergency_dump(result)
        
        print(f"🚨 EMERGENCY DUMP: {result.tokens_freed} tokens freed")
    
    def _handle_capacity_alert(self, alert: CapacityAlert):
        """
        Handle capacity alert from capacity monitor
        """
        self.alert_count += 1
        
        if self.on_capacity_alert:
            self.on_capacity_alert(alert)
        
        print(f"🚨 CAPACITY ALERT: {alert.message}")
    
    def _handle_emergency_alert(self, alert: CapacityAlert):
        """
        Handle emergency alert from capacity monitor
        """
        self.alert_count += 1
        
        if self.on_emergency_alert:
            self.on_emergency_alert(alert)
        
        print(f"🚨 EMERGENCY ALERT: {alert.message}")
        
        # Trigger emergency dump if in automatic mode
        if self.config.mode == ContextManagerMode.AUTOMATIC:
            self.force_emergency_dump()
    
    def force_emergency_dump(self) -> ContextDumpResult:
        """
        Force an emergency context dump
        """
        if not self.is_active:
            raise RuntimeError("Context manager is not active")
        
        result = self.automated_dumping.force_emergency_dump()
        
        print(f"🚨 FORCED EMERGENCY DUMP: {result.tokens_freed} tokens freed")
        
        return result
    
    def get_context_usage_status(self) -> Dict[str, Any]:
        """
        Get comprehensive context usage status
        """
        if not self.is_active:
            return {'status': 'inactive'}
        
        # Get status from capacity monitor
        capacity_status = self.capacity_monitor.get_current_capacity_status()
        
        # Get status from automated dumping
        dumping_status = self.automated_dumping.get_context_usage_status()
        
        # Combine status
        combined_status = {
            'status': 'active',
            'mode': self.config.mode.value,
            'capacity_status': capacity_status,
            'dumping_status': dumping_status,
            'dump_count': self.dump_count,
            'alert_count': self.alert_count,
            'last_dump_time': self.last_dump_time.isoformat() if self.last_dump_time else None,
            'monitoring_active': self.capacity_monitor.monitoring_active,
            'auto_dump_enabled': self.config.auto_dump_enabled,
            'cost_optimization_enabled': self.config.cost_optimization_enabled
        }
        
        return combined_status
    
    def get_capacity_forecast(self, hours_ahead: int = 1) -> Dict[str, Any]:
        """
        Get capacity forecast
        """
        if not self.is_active:
            return {'forecast': 'inactive'}
        
        return self.capacity_monitor.get_capacity_forecast(hours_ahead)
    
    def get_dump_history(self) -> List[Dict[str, Any]]:
        """
        Get dump history
        """
        if not self.is_active:
            return []
        
        dump_history = self.automated_dumping.get_dump_history()
        
        # Convert to dict format
        history = []
        for result in dump_history:
            history.append({
                'dump_id': result.dump_id,
                'timestamp': result.timestamp.isoformat(),
                'trigger': result.trigger.value,
                'strategy': result.strategy.value,
                'context_size_before': result.context_size_before,
                'context_size_after': result.context_size_after,
                'tokens_freed': result.tokens_freed,
                'dump_time': result.dump_time,
                'success': result.success,
                'error_message': result.error_message
            })
        
        return history
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Get alert history
        """
        if not self.is_active:
            return []
        
        return self.capacity_monitor.get_alert_history()
    
    def configure_context_management(
        self,
        mode: Optional[ContextManagerMode] = None,
        max_tokens: Optional[int] = None,
        capacity_thresholds: Optional[Dict[str, float]] = None,
        dump_strategies: Optional[Dict[str, str]] = None,
        journaling_strategy: Optional[str] = None,
        model_tier: Optional[str] = None,
        monitoring_interval: Optional[float] = None,
        auto_dump_enabled: Optional[bool] = None,
        cost_optimization_enabled: Optional[bool] = None
    ):
        """
        Configure context management settings
        """
        if mode is not None:
            self.config.mode = mode
        
        if max_tokens is not None:
            self.config.max_tokens = max_tokens
            self.capacity_monitor.set_max_tokens(max_tokens)
        
        if capacity_thresholds is not None:
            self.config.capacity_thresholds.update(capacity_thresholds)
            self.capacity_monitor.set_capacity_thresholds(
                warning=capacity_thresholds.get('warning', 0.70),
                critical=capacity_thresholds.get('critical', 0.85),
                emergency=capacity_thresholds.get('emergency', 0.95)
            )
        
        if dump_strategies is not None:
            self.config.dump_strategies.update(dump_strategies)
        
        if journaling_strategy is not None:
            self.config.journaling_strategy = journaling_strategy
        
        if model_tier is not None:
            self.config.model_tier = model_tier
        
        if monitoring_interval is not None:
            self.config.monitoring_interval = monitoring_interval
        
        if auto_dump_enabled is not None:
            self.config.auto_dump_enabled = auto_dump_enabled
        
        if cost_optimization_enabled is not None:
            self.config.cost_optimization_enabled = cost_optimization_enabled
        
        print(f"🔧 Context management configured: {self.config.mode.value} mode")
    
    def journal_consciousness_optimized(
        self,
        prompt_id: str,
        user_input: str,
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Journal consciousness using cost optimization
        """
        if not self.config.cost_optimization_enabled:
            return {'skipped': True, 'reason': 'Cost optimization disabled'}
        
        # Determine journaling strategy based on config
        strategy = JournalingStrategy.ADAPTIVE_DEPTH
        if self.config.journaling_strategy == 'full_depth':
            strategy = JournalingStrategy.FULL_DEPTH
        elif self.config.journaling_strategy == 'selective_depth':
            strategy = JournalingStrategy.SELECTIVE_DEPTH
        elif self.config.journaling_strategy == 'compressed_depth':
            strategy = JournalingStrategy.COMPRESSED_DEPTH
        elif self.config.journaling_strategy == 'minimal_depth':
            strategy = JournalingStrategy.MINIMAL_DEPTH
        
        # Determine model tier based on config
        model_tier = ModelTier.STANDARD
        if self.config.model_tier == 'premium':
            model_tier = ModelTier.PREMIUM
        elif self.config.model_tier == 'economy':
            model_tier = ModelTier.ECONOMY
        elif self.config.model_tier == 'free':
            model_tier = ModelTier.FREE
        
        # Journal consciousness
        result = self.cost_optimized_journaling.journal_consciousness_optimized(
            prompt_id=prompt_id,
            user_input=user_input,
            current_context=current_context,
            strategy=strategy,
            model_tier=model_tier
        )
        
        return result
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get optimization recommendations
        """
        if not self.config.cost_optimization_enabled:
            return {'message': 'Cost optimization disabled'}
        
        return self.cost_optimized_journaling.get_optimization_recommendations()
    
    def get_context_manager_status(self) -> ContextManagerStatus:
        """
        Get comprehensive context manager status
        """
        if not self.is_active:
            return ContextManagerStatus(
                is_active=False,
                mode=self.config.mode,
                current_tokens=0,
                max_tokens=self.config.max_tokens,
                usage_percentage=0.0,
                last_dump_time=None,
                dump_count=0,
                alert_count=0,
                monitoring_active=False,
                cost_optimization_active=False
            )
        
        # Get current metrics
        capacity_status = self.capacity_monitor.get_current_capacity_status()
        
        return ContextManagerStatus(
            is_active=True,
            mode=self.config.mode,
            current_tokens=capacity_status.get('current_tokens', 0),
            max_tokens=capacity_status.get('max_tokens', self.config.max_tokens),
            usage_percentage=capacity_status.get('usage_percentage', 0.0),
            last_dump_time=self.last_dump_time,
            dump_count=self.dump_count,
            alert_count=self.alert_count,
            monitoring_active=self.capacity_monitor.monitoring_active,
            cost_optimization_active=self.config.cost_optimization_enabled
        )


# Example usage and testing
if __name__ == "__main__":
    # Create integrated context manager
    context_manager = IntegratedContextManager()
    
    # Set up callbacks
    def on_context_dump(result: ContextDumpResult):
        print(f"✅ CONTEXT DUMP: {result.tokens_freed} tokens freed")
    
    def on_capacity_alert(alert):
        print(f"🚨 CAPACITY ALERT: {alert.message}")
    
    def on_emergency_dump(result: ContextDumpResult):
        print(f"🚨 EMERGENCY DUMP: {result.tokens_freed} tokens freed")
    
    context_manager.on_context_dump = on_context_dump
    context_manager.on_capacity_alert = on_capacity_alert
    context_manager.on_emergency_dump = on_emergency_dump
    
    # Configure context management
    context_manager.configure_context_management(
        mode=ContextManagerMode.AUTOMATIC,
        max_tokens=128000,
        capacity_thresholds={
            'warning': 0.70,
            'critical': 0.85,
            'emergency': 0.95
        },
        auto_dump_enabled=True,
        cost_optimization_enabled=True
    )
    
    # Sample context getter
    def get_current_context():
        return {
            'current_task': 'vif_implementation',
            'user_input': 'Implement VIF witness envelopes with comprehensive validation',
            'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md'] * 100,
            'insights_gained': ['VIF requires comprehensive witness envelopes'] * 50,
            'decisions_made': [{'decision': 'Use L3 documentation for VIF implementation'}] * 20,
            'confidence_levels': {'vif_implementation': 0.85, 'witness_envelopes': 0.75},
            'context_budget_used': 100000,
            'tools_used': ['read_file', 'write', 'grep'],
            'mental_model': {'vif': 'Verifiable Intelligence Framework', 'cmc': 'Context Memory Core'},
            'conversation_history': [{'role': 'user', 'content': 'Test message'}] * 100
        }
    
    # Start context management
    context_manager.start_context_management(get_current_context)
    
    # Simulate monitoring for a bit
    time.sleep(10.0)
    
    # Get status
    status = context_manager.get_context_usage_status()
    print(f"Context Usage Status: {status}")
    
    # Get capacity forecast
    forecast = context_manager.get_capacity_forecast(hours_ahead=1)
    print(f"Capacity Forecast: {forecast}")
    
    # Get optimization recommendations
    recommendations = context_manager.get_optimization_recommendations()
    print(f"Optimization Recommendations: {recommendations}")
    
    # Stop context management
    context_manager.stop_context_management()
