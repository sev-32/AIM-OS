"""
Context Capacity Monitor - Real-time Context Usage Monitoring

This module provides real-time monitoring of context usage and capacity
with automated alerts and context dumping when approaching limits.
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

# MCP imports for AIM-OS integration
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}


class CapacityAlertLevel(Enum):
    """Alert levels for context capacity"""
    INFO = "info"           # Informational
    WARNING = "warning"     # Warning level
    CRITICAL = "critical"   # Critical level
    EMERGENCY = "emergency" # Emergency level


@dataclass
class ContextCapacityMetrics:
    """Metrics for context capacity monitoring"""
    current_tokens: int
    max_tokens: int
    usage_percentage: float
    estimated_remaining_tokens: int
    estimated_remaining_time: float  # seconds
    context_growth_rate: float  # tokens per second
    files_read_count: int
    insights_gained_count: int
    decisions_made_count: int
    conversation_turns: int
    last_update: datetime


@dataclass
class CapacityAlert:
    """Alert for context capacity"""
    alert_id: str
    timestamp: datetime
    level: CapacityAlertLevel
    current_usage: ContextCapacityMetrics
    message: str
    recommended_action: str
    estimated_time_to_limit: float  # seconds
    urgency_score: float  # 0.0-1.0


class ContextCapacityMonitor:
    """
    Real-time context capacity monitor with automated alerts
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.max_tokens = 128000  # Default GPT-4 context limit
        self.warning_threshold = 0.70   # 70% warning
        self.critical_threshold = 0.85  # 85% critical
        self.emergency_threshold = 0.95 # 95% emergency
        
        # Monitoring data
        self.capacity_history: List[ContextCapacityMetrics] = []
        self.alert_history: List[CapacityAlert] = []
        self.current_metrics: Optional[ContextCapacityMetrics] = None
        
        # Callbacks
        self.on_capacity_alert: Optional[Callable[[CapacityAlert], None]] = None
        self.on_emergency_alert: Optional[Callable[[CapacityAlert], None]] = None
        
        # Context tracking
        self.context_snapshots: List[Dict[str, Any]] = []
        self.last_snapshot_time: Optional[datetime] = None
    
    def start_monitoring(self, context_getter: Callable[[], Dict[str, Any]]):
        """
        Start monitoring context capacity
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
        Stop monitoring context capacity
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
                
                # Calculate capacity metrics
                metrics = self._calculate_capacity_metrics(current_context)
                self.current_metrics = metrics
                self.capacity_history.append(metrics)
                
                # Store context snapshot
                self._store_context_snapshot(current_context)
                
                # Check for alerts
                alert = self._check_capacity_alerts(metrics)
                if alert:
                    self._handle_capacity_alert(alert)
                
                # Sleep for monitoring interval
                time.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error in capacity monitoring loop: {e}")
                time.sleep(30.0)  # Wait longer on error
    
    def _calculate_capacity_metrics(self, context: Dict[str, Any]) -> ContextCapacityMetrics:
        """
        Calculate context capacity metrics
        """
        # Estimate current token usage
        current_tokens = self._estimate_token_count(context)
        
        # Calculate usage percentage
        usage_percentage = current_tokens / self.max_tokens
        
        # Calculate remaining tokens
        estimated_remaining_tokens = self.max_tokens - current_tokens
        
        # Calculate context growth rate
        context_growth_rate = self._calculate_growth_rate()
        
        # Estimate remaining time
        estimated_remaining_time = 0.0
        if context_growth_rate > 0:
            estimated_remaining_time = estimated_remaining_tokens / context_growth_rate
        
        # Count context elements
        files_read_count = len(context.get('files_read', []))
        insights_gained_count = len(context.get('insights_gained', []))
        decisions_made_count = len(context.get('decisions_made', []))
        conversation_turns = len(context.get('conversation_history', []))
        
        return ContextCapacityMetrics(
            current_tokens=current_tokens,
            max_tokens=self.max_tokens,
            usage_percentage=usage_percentage,
            estimated_remaining_tokens=estimated_remaining_tokens,
            estimated_remaining_time=estimated_remaining_time,
            context_growth_rate=context_growth_rate,
            files_read_count=files_read_count,
            insights_gained_count=insights_gained_count,
            decisions_made_count=decisions_made_count,
            conversation_turns=conversation_turns,
            last_update=datetime.now()
        )
    
    def _calculate_growth_rate(self) -> float:
        """
        Calculate context growth rate (tokens per second)
        """
        if len(self.capacity_history) < 2:
            return 0.0
        
        # Get last two measurements
        current = self.capacity_history[-1]
        previous = self.capacity_history[-2]
        
        # Calculate time difference
        time_diff = (current.last_update - previous.last_update).total_seconds()
        if time_diff <= 0:
            return 0.0
        
        # Calculate token difference
        token_diff = current.current_tokens - previous.current_tokens
        
        # Calculate growth rate
        growth_rate = token_diff / time_diff
        
        return max(0.0, growth_rate)  # Only positive growth
    
    def _check_capacity_alerts(self, metrics: ContextCapacityMetrics) -> Optional[CapacityAlert]:
        """
        Check if capacity alerts are needed
        """
        # Check emergency threshold
        if metrics.usage_percentage >= self.emergency_threshold:
            return self._create_alert(
                CapacityAlertLevel.EMERGENCY,
                metrics,
                f"EMERGENCY: Context usage at {metrics.usage_percentage:.1%} - immediate action required!",
                "Perform emergency context dump immediately",
                metrics.estimated_remaining_time,
                1.0
            )
        
        # Check critical threshold
        elif metrics.usage_percentage >= self.critical_threshold:
            return self._create_alert(
                CapacityAlertLevel.CRITICAL,
                metrics,
                f"CRITICAL: Context usage at {metrics.usage_percentage:.1%} - context dump recommended",
                "Perform selective context dump",
                metrics.estimated_remaining_time,
                0.8
            )
        
        # Check warning threshold
        elif metrics.usage_percentage >= self.warning_threshold:
            return self._create_alert(
                CapacityAlertLevel.WARNING,
                metrics,
                f"WARNING: Context usage at {metrics.usage_percentage:.1%} - monitor closely",
                "Consider incremental context cleanup",
                metrics.estimated_remaining_time,
                0.6
            )
        
        # Check if approaching limits quickly
        elif metrics.estimated_remaining_time > 0 and metrics.estimated_remaining_time < 300:  # 5 minutes
            return self._create_alert(
                CapacityAlertLevel.WARNING,
                metrics,
                f"WARNING: Context approaching limit in {metrics.estimated_remaining_time:.0f} seconds",
                "Prepare for context dump",
                metrics.estimated_remaining_time,
                0.7
            )
        
        return None
    
    def _create_alert(
        self,
        level: CapacityAlertLevel,
        metrics: ContextCapacityMetrics,
        message: str,
        recommended_action: str,
        estimated_time_to_limit: float,
        urgency_score: float
    ) -> CapacityAlert:
        """
        Create a capacity alert
        """
        alert = CapacityAlert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level=level,
            current_usage=metrics,
            message=message,
            recommended_action=recommended_action,
            estimated_time_to_limit=estimated_time_to_limit,
            urgency_score=urgency_score
        )
        
        self.alert_history.append(alert)
        return alert
    
    def _handle_capacity_alert(self, alert: CapacityAlert):
        """
        Handle a capacity alert
        """
        # Call alert callback if set
        if self.on_capacity_alert:
            self.on_capacity_alert(alert)
        
        # Call emergency callback if emergency
        if alert.level == CapacityAlertLevel.EMERGENCY and self.on_emergency_alert:
            self.on_emergency_alert(alert)
        
        # Store alert in MCP
        self._store_alert_in_mcp(alert)
    
    def _store_context_snapshot(self, context: Dict[str, Any]):
        """
        Store context snapshot for analysis
        """
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'context_size': self._estimate_token_count(context),
            'context_summary': {
                'files_read': len(context.get('files_read', [])),
                'insights_gained': len(context.get('insights_gained', [])),
                'decisions_made': len(context.get('decisions_made', [])),
                'conversation_turns': len(context.get('conversation_history', []))
            }
        }
        
        self.context_snapshots.append(snapshot)
        self.last_snapshot_time = datetime.now()
        
        # Keep only recent snapshots (last 100)
        if len(self.context_snapshots) > 100:
            self.context_snapshots = self.context_snapshots[-100:]
    
    def _store_alert_in_mcp(self, alert: CapacityAlert):
        """
        Store capacity alert in MCP
        """
        try:
            self.mcp_client.store_memory({
                'type': 'capacity_alert',
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level.value,
                'message': alert.message,
                'recommended_action': alert.recommended_action,
                'urgency_score': alert.urgency_score,
                'current_usage': {
                    'current_tokens': alert.current_usage.current_tokens,
                    'max_tokens': alert.current_usage.max_tokens,
                    'usage_percentage': alert.current_usage.usage_percentage,
                    'estimated_remaining_tokens': alert.current_usage.estimated_remaining_tokens,
                    'estimated_remaining_time': alert.current_usage.estimated_remaining_time
                }
            })
        except Exception as e:
            print(f"Error storing capacity alert in MCP: {e}")
    
    def _estimate_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for context
        """
        # Simple estimation: 1 token ≈ 4 characters
        context_str = json.dumps(context)
        return len(context_str) // 4
    
    def get_current_capacity_status(self) -> Dict[str, Any]:
        """
        Get current capacity status
        """
        if not self.current_metrics:
            return {'status': 'no_data'}
        
        metrics = self.current_metrics
        
        return {
            'current_tokens': metrics.current_tokens,
            'max_tokens': metrics.max_tokens,
            'usage_percentage': metrics.usage_percentage,
            'estimated_remaining_tokens': metrics.estimated_remaining_tokens,
            'estimated_remaining_time': metrics.estimated_remaining_time,
            'context_growth_rate': metrics.context_growth_rate,
            'files_read_count': metrics.files_read_count,
            'insights_gained_count': metrics.insights_gained_count,
            'decisions_made_count': metrics.decisions_made_count,
            'conversation_turns': metrics.conversation_turns,
            'last_update': metrics.last_update.isoformat(),
            'status': 'monitoring_active' if self.monitoring_active else 'monitoring_inactive'
        }
    
    def get_capacity_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get capacity history
        """
        history = []
        for metrics in self.capacity_history[-limit:]:
            history.append({
                'timestamp': metrics.last_update.isoformat(),
                'current_tokens': metrics.current_tokens,
                'usage_percentage': metrics.usage_percentage,
                'estimated_remaining_tokens': metrics.estimated_remaining_tokens,
                'estimated_remaining_time': metrics.estimated_remaining_time,
                'context_growth_rate': metrics.context_growth_rate
            })
        
        return history
    
    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get alert history
        """
        history = []
        for alert in self.alert_history[-limit:]:
            history.append({
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level.value,
                'message': alert.message,
                'recommended_action': alert.recommended_action,
                'urgency_score': alert.urgency_score,
                'current_usage': {
                    'current_tokens': alert.current_usage.current_tokens,
                    'usage_percentage': alert.current_usage.usage_percentage,
                    'estimated_remaining_time': alert.current_usage.estimated_remaining_time
                }
            })
        
        return history
    
    def get_capacity_forecast(self, hours_ahead: int = 1) -> Dict[str, Any]:
        """
        Get capacity forecast for the next N hours
        """
        if not self.current_metrics or self.current_metrics.context_growth_rate <= 0:
            return {'forecast': 'insufficient_data'}
        
        current_metrics = self.current_metrics
        growth_rate = current_metrics.context_growth_rate
        current_tokens = current_metrics.current_tokens
        
        # Calculate forecast
        forecast_points = []
        for hour in range(1, hours_ahead + 1):
            time_seconds = hour * 3600
            estimated_tokens = current_tokens + (growth_rate * time_seconds)
            estimated_usage = estimated_tokens / self.max_tokens
            
            forecast_points.append({
                'hours_ahead': hour,
                'estimated_tokens': int(estimated_tokens),
                'estimated_usage_percentage': estimated_usage,
                'will_exceed_limit': estimated_tokens > self.max_tokens
            })
        
        return {
            'current_tokens': current_tokens,
            'current_usage_percentage': current_metrics.usage_percentage,
            'growth_rate': growth_rate,
            'forecast_points': forecast_points,
            'will_exceed_limit': any(point['will_exceed_limit'] for point in forecast_points)
        }
    
    def set_capacity_thresholds(
        self, 
        warning: float = 0.70, 
        critical: float = 0.85, 
        emergency: float = 0.95
    ):
        """
        Set capacity thresholds
        """
        self.warning_threshold = warning
        self.critical_threshold = critical
        self.emergency_threshold = emergency
    
    def set_max_tokens(self, max_tokens: int):
        """
        Set maximum token limit
        """
        self.max_tokens = max_tokens


# Example usage and testing
if __name__ == "__main__":
    # Create context capacity monitor
    monitor = ContextCapacityMonitor()
    
    # Set up callbacks
    def on_capacity_alert(alert: CapacityAlert):
        print(f"🚨 CAPACITY ALERT [{alert.level.value.upper()}]: {alert.message}")
        print(f"   Usage: {alert.current_usage.usage_percentage:.1%}")
        print(f"   Remaining time: {alert.estimated_time_to_limit:.0f}s")
        print(f"   Recommended: {alert.recommended_action}")
    
    def on_emergency_alert(alert: CapacityAlert):
        print(f"🚨 EMERGENCY ALERT: {alert.message}")
        print(f"   Usage: {alert.current_usage.usage_percentage:.1%}")
        print(f"   Immediate action required!")
    
    monitor.on_capacity_alert = on_capacity_alert
    monitor.on_emergency_alert = on_emergency_alert
    
    # Sample context getter
    def get_current_context():
        return {
            'current_task': 'vif_implementation',
            'user_input': 'Implement VIF witness envelopes with comprehensive validation',
            'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md'] * 100,  # Simulate high usage
            'insights_gained': ['VIF requires comprehensive witness envelopes'] * 50,
            'decisions_made': [{'decision': 'Use L3 documentation for VIF implementation'}] * 20,
            'confidence_levels': {'vif_implementation': 0.85, 'witness_envelopes': 0.75},
            'context_budget_used': 100000,  # High usage
            'tools_used': ['read_file', 'write', 'grep'],
            'mental_model': {'vif': 'Verifiable Intelligence Framework', 'cmc': 'Context Memory Core'},
            'conversation_history': [{'role': 'user', 'content': 'Test message'}] * 100
        }
    
    # Start monitoring
    monitor.start_monitoring(get_current_context)
    
    # Simulate monitoring for a bit
    time.sleep(10.0)
    
    # Get current status
    status = monitor.get_current_capacity_status()
    print(f"Current Capacity Status: {status}")
    
    # Get capacity forecast
    forecast = monitor.get_capacity_forecast(hours_ahead=1)
    print(f"Capacity Forecast: {forecast}")
    
    # Get alert history
    alert_history = monitor.get_alert_history()
    print(f"Alert History: {len(alert_history)} alerts")
    
    # Stop monitoring
    monitor.stop_monitoring()
