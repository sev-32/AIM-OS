#!/usr/bin/env python3
"""
AIM-OS Self-Improvement System MCP Server

Provides MCP tools for the Self-Improvement System including:
- Meta-cognitive analysis
- System usage auditing
- Performance monitoring
- Gap identification
- Improvement implementation
- Continuous learning
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

# Add the packages directory to the path
sys.path.insert(0, "packages")

from sis.sis_core import SISCore, SISConfig, SISStatus
from sis.meta_cognitive_analyzer import MetaCognitiveAnalyzer, DecisionType


class SISMCPServer:
    """MCP Server for AIM-OS Self-Improvement System"""
    
    def __init__(self):
        """Initialize the SIS MCP Server"""
        self.sis_config = SISConfig()
        self.sis_core = SISCore(self.sis_config)
        self.meta_cognitive_analyzer = MetaCognitiveAnalyzer()
        
        # Initialize SIS
        self.sis_core.start()
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                return self._handle_initialize(request_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request_id, params)
            else:
                return self._error_response(request_id, -32601, "Method not found")
                
        except Exception as e:
            return self._error_response(request.get("id"), -32603, f"Internal error: {str(e)}")
    
    def _handle_initialize(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "aimos-sis-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, request_id: int) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = [
            {
                "name": "get_sis_status",
                "description": "Get current status of the Self-Improvement System",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_performance_metrics",
                "description": "Get performance metrics for the Self-Improvement System",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "record_decision",
                "description": "Record a decision for meta-cognitive analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "decision_type": {
                            "type": "string",
                            "enum": ["documentation", "system_selection", "implementation", "knowledge_capture", "integration"]
                        },
                        "context": {"type": "string"},
                        "rationale": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "outcome": {"type": "string"},
                        "success": {"type": "boolean"}
                    },
                    "required": ["decision_type", "context", "rationale", "confidence"]
                }
            },
            {
                "name": "analyze_decisions",
                "description": "Analyze recorded decisions for patterns and insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_improvement_history",
                "description": "Get history of improvements made by the Self-Improvement System",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_learning_history",
                "description": "Get history of learning and adaptation by the Self-Improvement System",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "configure_sis",
                "description": "Configure the Self-Improvement System",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "monitoring_interval_minutes": {"type": "integer", "minimum": 1},
                        "analysis_interval_minutes": {"type": "integer", "minimum": 1},
                        "improvement_interval_minutes": {"type": "integer", "minimum": 1},
                        "usage_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "performance_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "improvement_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": []
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    def _handle_tools_call(self, request_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_sis_status":
            return self._get_sis_status(request_id)
        elif tool_name == "get_performance_metrics":
            return self._get_performance_metrics(request_id)
        elif tool_name == "record_decision":
            return self._record_decision(request_id, arguments)
        elif tool_name == "analyze_decisions":
            return self._analyze_decisions(request_id)
        elif tool_name == "get_improvement_history":
            return self._get_improvement_history(request_id)
        elif tool_name == "get_learning_history":
            return self._get_learning_history(request_id)
        elif tool_name == "configure_sis":
            return self._configure_sis(request_id, arguments)
        else:
            return self._error_response(request_id, -32601, f"Unknown tool: {tool_name}")
    
    def _get_sis_status(self, request_id: int) -> Dict[str, Any]:
        """Get SIS status"""
        status = self.sis_core.get_status()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "is_running": status.is_running,
                "last_monitoring": status.last_monitoring.isoformat() if status.last_monitoring else None,
                "last_analysis": status.last_analysis.isoformat() if status.last_analysis else None,
                "last_improvement": status.last_improvement.isoformat() if status.last_improvement else None,
                "total_improvements": status.total_improvements,
                "successful_improvements": status.successful_improvements,
                "failed_improvements": status.failed_improvements,
                "current_gaps": status.current_gaps,
                "system_usage_rate": status.system_usage_rate,
                "performance_score": status.performance_score
            }
        }
    
    def _get_performance_metrics(self, request_id: int) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = self.sis_core.get_performance_metrics()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": metrics
        }
    
    def _record_decision(self, request_id: int, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Record a decision"""
        try:
            decision_type_str = arguments.get("decision_type")
            decision_type = DecisionType(decision_type_str)
            
            decision = self.meta_cognitive_analyzer.record_decision(
                decision_type=decision_type,
                context=arguments.get("context", ""),
                rationale=arguments.get("rationale", ""),
                confidence=arguments.get("confidence", 0.5),
                outcome=arguments.get("outcome"),
                success=arguments.get("success")
            )
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "decision_id": decision.id,
                    "timestamp": decision.timestamp.isoformat(),
                    "decision_type": decision.decision_type.value,
                    "context": decision.context,
                    "rationale": decision.rationale,
                    "confidence": decision.confidence,
                    "outcome": decision.outcome,
                    "success": decision.success
                }
            }
            
        except Exception as e:
            return self._error_response(request_id, -32602, f"Invalid arguments: {str(e)}")
    
    def _analyze_decisions(self, request_id: int) -> Dict[str, Any]:
        """Analyze decisions"""
        decisions = self.meta_cognitive_analyzer.collect_decision_data()
        analysis = self.meta_cognitive_analyzer.analyze_decisions(decisions)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "total_decisions": analysis.total_decisions,
                "efficiency_score": analysis.efficiency_score,
                "consistency_score": analysis.consistency_score,
                "proactive_score": analysis.proactive_score,
                "patterns": [
                    {
                        "pattern_type": pattern.pattern_type.value,
                        "frequency": pattern.frequency,
                        "confidence": pattern.confidence,
                        "description": pattern.description
                    }
                    for pattern in analysis.patterns
                ],
                "recommendations": analysis.recommendations,
                "timestamp": analysis.timestamp.isoformat()
            }
        }
    
    def _get_improvement_history(self, request_id: int) -> Dict[str, Any]:
        """Get improvement history"""
        history = self.sis_core.get_improvement_history()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "improvements": [
                    {
                        "id": improvement["id"],
                        "timestamp": improvement["timestamp"].isoformat(),
                        "success": improvement["success"]
                    }
                    for improvement in history
                ]
            }
        }
    
    def _get_learning_history(self, request_id: int) -> Dict[str, Any]:
        """Get learning history"""
        history = self.sis_core.get_learning_historyquery
        query = params.get("query", "")
        tags = params.get("tags", {})
        
        # Use the MCP memory system to retrieve memory
        try:
            # This would integrate with the actual MCP memory system
            # For now, return a mock response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "memories": [
                        {
                            "id": "memory_1",
                            "content": "Sample memory content",
                            "tags": {"category": 0.8, "system": 0.9},
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }
            }
        except Exception as e:
            return self._error_response(request_id, -32603, f"Error retrieving memory: {str(e)}")
    
    def _error_response(self, request_id: int, code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


async def main():
    """Main function for MCP server"""
    server = SISMCPServer()
    
    # Read from stdin and write to stdout
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
