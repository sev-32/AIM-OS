"""
Health Check System for Cross-Model MCP Server

This module provides comprehensive health checking, monitoring, and observability
for the cross-model consciousness MCP server.
"""

import time
import psutil
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result["status"] = self.status.value
        result["timestamp"] = self.timestamp.isoformat()
        return result


class HealthCheckSystem:
    """Comprehensive health check system"""
    
    def __init__(self, server_instance):
        self.server = server_instance
        self.checks = {}
        self.register_default_checks()
    
    def register_default_checks(self):
        """Register default health checks"""
        self.register_check("server_status", self.check_server_status)
        self.register_check("memory_usage", self.check_memory_usage)
        self.register_check("cpu_usage", self.check_cpu_usage)
        self.register_check("response_time", self.check_response_time)
        self.register_check("error_rate", self.check_error_rate)
        self.register_check("tool_availability", self.check_tool_availability)
        self.register_check("database_connectivity", self.check_database_connectivity)
        self.register_check("cross_model_components", self.check_cross_model_components)
    
    def register_check(self, name: str, check_function):
        """Register a health check"""
        self.checks[name] = check_function
    
    def check_server_status(self) -> HealthCheckResult:
        """Check if server is responding"""
        start_time = time.time()
        
        try:
            # Test basic server functionality
            response = self.server.handle_initialize({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "health-check", "version": "1.0.0"}
                }
            })
            
            response_time = (time.time() - start_time) * 1000
            
            if response and response.get("jsonrpc") == "2.0":
                return HealthCheckResult(
                    name="server_status",
                    status=HealthStatus.HEALTHY,
                    message="Server is responding normally",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    metadata={"response_id": response.get("id")}
                )
            else:
                return HealthCheckResult(
                    name="server_status",
                    status=HealthStatus.UNHEALTHY,
                    message="Server response invalid",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name="server_status",
                status=HealthStatus.CRITICAL,
                message=f"Server check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Memory thresholds
            if memory_mb < 256:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_mb:.1f}MB"
            elif memory_mb < 512:
                status = HealthStatus.DEGRADED
                message = f"Memory usage elevated: {memory_mb:.1f}MB"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory_mb:.1f}MB"
            
            return HealthCheckResult(
                name="memory_usage",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0,
                metadata={
                    "memory_mb": memory_mb,
                    "memory_percent": process.memory_percent(),
                    "available_memory_mb": psutil.virtual_memory().available / 1024 / 1024
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="memory_usage",
                status=HealthStatus.CRITICAL,
                message=f"Memory check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_cpu_usage(self) -> HealthCheckResult:
        """Check CPU usage"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=1)
            system_cpu = psutil.cpu_percent(interval=1)
            
            # CPU thresholds
            if cpu_percent < 25:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            elif cpu_percent < 50:
                status = HealthStatus.DEGRADED
                message = f"CPU usage elevated: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                name="cpu_usage",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=1000,  # CPU check takes 1 second
                metadata={
                    "process_cpu_percent": cpu_percent,
                    "system_cpu_percent": system_cpu,
                    "cpu_count": psutil.cpu_count()
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="cpu_usage",
                status=HealthStatus.CRITICAL,
                message=f"CPU check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_response_time(self) -> HealthCheckResult:
        """Check response time"""
        try:
            start_time = time.time()
            
            # Test a simple tool call
            response = self.server.select_models(1, {
                "task_description": "Health check test",
                "context_size": 100,
                "budget_limit": 0.01,
                "quality_requirement": "acceptable"
            })
            
            response_time = (time.time() - start_time) * 1000
            
            # Response time thresholds
            if response_time < 100:
                status = HealthStatus.HEALTHY
                message = f"Response time excellent: {response_time:.1f}ms"
            elif response_time < 500:
                status = HealthStatus.DEGRADED
                message = f"Response time slow: {response_time:.1f}ms"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Response time critical: {response_time:.1f}ms"
            
            return HealthCheckResult(
                name="response_time",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=response_time,
                metadata={
                    "tool": "select_models",
                    "success": response.get("jsonrpc") == "2.0"
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="response_time",
                status=HealthStatus.CRITICAL,
                message=f"Response time check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_error_rate(self) -> HealthCheckResult:
        """Check error rate (simplified version)"""
        try:
            # This is a simplified error rate check
            # In a real implementation, you would track errors over time
            
            # Test multiple requests to see error rate
            error_count = 0
            total_requests = 10
            
            for i in range(total_requests):
                try:
                    response = self.server.select_models(i + 1, {
                        "task_description": f"Error rate test {i}",
                        "context_size": 100,
                        "budget_limit": 0.01,
                        "quality_requirement": "acceptable"
                    })
                    
                    if response.get("jsonrpc") != "2.0":
                        error_count += 1
                        
                except Exception:
                    error_count += 1
            
            error_rate = error_count / total_requests
            
            if error_rate < 0.01:  # < 1%
                status = HealthStatus.HEALTHY
                message = f"Error rate normal: {error_rate:.1%}"
            elif error_rate < 0.05:  # < 5%
                status = HealthStatus.DEGRADED
                message = f"Error rate elevated: {error_rate:.1%}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Error rate critical: {error_rate:.1%}"
            
            return HealthCheckResult(
                name="error_rate",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0,
                metadata={
                    "error_count": error_count,
                    "total_requests": total_requests,
                    "error_rate": error_rate
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="error_rate",
                status=HealthStatus.CRITICAL,
                message=f"Error rate check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_tool_availability(self) -> HealthCheckResult:
        """Check tool availability"""
        try:
            # Get available tools
            tools_response = self.server.handle_request({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            })
            
            if tools_response.get("jsonrpc") != "2.0":
                return HealthCheckResult(
                    name="tool_availability",
                    status=HealthStatus.CRITICAL,
                    message="Failed to get tools list",
                    timestamp=datetime.now(),
                    response_time_ms=0
                )
            
            tools = tools_response.get("result", {}).get("tools", [])
            expected_tools = [
                "select_models", "extract_insights", "transfer_insights",
                "execute_task", "generate_witness", "calibrate_confidence",
                "replay_operation", "store_cross_model_atom", "query_cross_model_atoms",
                "get_cross_model_stats"
            ]
            
            available_tools = [tool["name"] for tool in tools]
            missing_tools = [tool for tool in expected_tools if tool not in available_tools]
            
            if not missing_tools:
                status = HealthStatus.HEALTHY
                message = f"All {len(expected_tools)} tools available"
            elif len(missing_tools) <= 2:
                status = HealthStatus.DEGRADED
                message = f"Some tools missing: {missing_tools}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple tools missing: {missing_tools}"
            
            return HealthCheckResult(
                name="tool_availability",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0,
                metadata={
                    "total_tools": len(tools),
                    "expected_tools": len(expected_tools),
                    "missing_tools": missing_tools,
                    "available_tools": available_tools
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="tool_availability",
                status=HealthStatus.CRITICAL,
                message=f"Tool availability check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_database_connectivity(self) -> HealthCheckResult:
        """Check database connectivity"""
        try:
            # Check if memory system is accessible
            if hasattr(self.server, 'memory') and self.server.memory:
                # Try to get memory stats
                stats_response = self.server.get_memory_stats(1, {})
                
                if stats_response.get("jsonrpc") == "2.0":
                    status = HealthStatus.HEALTHY
                    message = "Database connectivity normal"
                else:
                    status = HealthStatus.DEGRADED
                    message = "Database connectivity issues"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Memory system not initialized"
            
            return HealthCheckResult(
                name="database_connectivity",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="database_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Database connectivity check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def check_cross_model_components(self) -> HealthCheckResult:
        """Check cross-model components"""
        try:
            components = {
                "model_selector": self.server.model_selector,
                "insight_extractor": self.server.insight_extractor,
                "insight_transfer": self.server.insight_transfer,
                "execution_orchestrator": self.server.execution_orchestrator,
                "witness_generator": self.server.witness_generator,
                "confidence_calibrator": self.server.confidence_calibrator,
                "replay_system": self.server.replay_system,
                "atom_creator": self.server.atom_creator,
                "atom_storage": self.server.atom_storage
            }
            
            missing_components = [name for name, component in components.items() if component is None]
            
            if not missing_components:
                status = HealthStatus.HEALTHY
                message = "All cross-model components initialized"
            elif len(missing_components) <= 2:
                status = HealthStatus.DEGRADED
                message = f"Some components missing: {missing_components}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple components missing: {missing_components}"
            
            return HealthCheckResult(
                name="cross_model_components",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time_ms=0,
                metadata={
                    "total_components": len(components),
                    "initialized_components": len(components) - len(missing_components),
                    "missing_components": missing_components
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="cross_model_components",
                status=HealthStatus.CRITICAL,
                message=f"Cross-model components check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time_ms=0
            )
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for name, check_function in self.checks.items():
            try:
                result = check_function()
                results.append(result)
                
                # Update overall status
                if result.status == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                elif result.status == HealthStatus.UNHEALTHY and overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                result = HealthCheckResult(
                    name=name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.now(),
                    response_time_ms=0
                )
                results.append(result)
                overall_status = HealthStatus.CRITICAL
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": [result.to_dict() for result in results],
            "summary": {
                "total_checks": len(results),
                "healthy": len([r for r in results if r.status == HealthStatus.HEALTHY]),
                "degraded": len([r for r in results if r.status == HealthStatus.DEGRADED]),
                "unhealthy": len([r for r in results if r.status == HealthStatus.UNHEALTHY]),
                "critical": len([r for r in results if r.status == HealthStatus.CRITICAL])
            }
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a quick health summary"""
        results = self.run_all_checks()
        
        return {
            "status": results["overall_status"],
            "timestamp": results["timestamp"],
            "summary": results["summary"]
        }


class MetricsCollector:
    """Metrics collection system"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "metrics": self.metrics
        }


# Global instances
health_checker = None
metrics_collector = MetricsCollector()


def initialize_health_checking(server_instance):
    """Initialize health checking system"""
    global health_checker
    health_checker = HealthCheckSystem(server_instance)
    return health_checker


def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    if health_checker:
        return health_checker.get_health_summary()
    else:
        return {
            "status": "unknown",
            "message": "Health checking not initialized"
        }


def get_detailed_health() -> Dict[str, Any]:
    """Get detailed health information"""
    if health_checker:
        return health_checker.run_all_checks()
    else:
        return {
            "overall_status": "unknown",
            "message": "Health checking not initialized"
        }
