# MCP Integration L3: Detailed Implementation

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~50,000 tokens  
**Purpose:** Complete implementation guide for MCP integration system  

---

## 🎯 **Implementation Overview**

This document provides complete implementation guidance for the MCP Integration system, including detailed code examples, integration patterns, testing strategies, and deployment procedures.

## 🏗️ **MCP Server Implementation**

### **Core MCP Server Implementation**
```python
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from datetime import datetime, timezone
import asyncio
import logging

class MCPTool:
    """MCP tool definition"""
    
    def __init__(self, name: str, description: str, category: str, 
                 input_schema: Dict[str, Any], execute_function: callable):
        self.name = name
        self.description = description
        self.category = category
        self.input_schema = input_schema
        self.execute_function = execute_function
        self.tool_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)

class MCPServer:
    """Core MCP server for Cursor IDE integration"""
    
    def __init__(self, config: MCPServerConfig = None):
        self.config = config or MCPServerConfig()
        self.tool_registry: ToolRegistry = ToolRegistry()
        self.request_handler: RequestHandler = RequestHandler()
        self.response_generator: ResponseGenerator = ResponseGenerator()
        self.error_handler: ErrorHandler = ErrorHandler()
        self.logging_system: LoggingSystem = LoggingSystem()
        self.server_state: ServerState = ServerState()
        
        # Initialize server
        self._initialize_server()
    
    def _initialize_server(self) -> None:
        """Initialize MCP server with all tools"""
        
        # Register all 16 tools
        self._register_all_tools()
        
        # Setup request handling
        self._setup_request_handling()
        
        # Initialize logging
        self._initialize_logging()
        
        # Set server state to ready
        self.server_state.set_ready()
    
    def _register_all_tools(self) -> None:
        """Register all 16 MCP tools"""
        
        # Register core AIM-OS tools
        self._register_core_aimos_tools()
        
        # Register cross-model consciousness tools
        self._register_cross_model_tools()
    
    def _register_core_aimos_tools(self) -> None:
        """Register core AIM-OS tools"""
        
        # Memory tools
        store_memory_tool = MCPTool(
            name="store_memory",
            description="Store information in AIM-OS persistent memory",
            category="memory",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "tags": {"type": "object"}
                },
                "required": ["content"]
            },
            execute_function=self._execute_store_memory
        )
        self.tool_registry.register_tool(store_memory_tool)
        
        get_memory_stats_tool = MCPTool(
            name="get_memory_stats",
            description="Get statistics about the AIM-OS memory system",
            category="memory",
            input_schema={
                "type": "object",
                "properties": {}
            },
            execute_function=self._execute_get_memory_stats
        )
        self.tool_registry.register_tool(get_memory_stats_tool)
        
        retrieve_memory_tool = MCPTool(
            name="retrieve_memory",
            description="Search and retrieve memories from AIM-OS persistent memory",
            category="memory",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                    "tags": {"type": "object"}
                },
                "required": ["query"]
            },
            execute_function=self._execute_retrieve_memory
        )
        self.tool_registry.register_tool(retrieve_memory_tool)
        
        # Orchestration tools
        create_plan_tool = MCPTool(
            name="create_plan",
            description="Create an execution plan using APOE",
            category="orchestration",
            input_schema={
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "context": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                },
                "required": ["goal"]
            },
            execute_function=self._execute_create_plan
        )
        self.tool_registry.register_tool(create_plan_tool)
        
        # Verification tools
        track_confidence_tool = MCPTool(
            name="track_confidence",
            description="Track confidence and provenance using VIF",
            category="verification",
            input_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reasoning": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["task", "confidence"]
            },
            execute_function=self._execute_track_confidence
        )
        self.tool_registry.register_tool(track_confidence_tool)
        
        # Knowledge tools
        synthesize_knowledge_tool = MCPTool(
            name="synthesize_knowledge",
            description="Synthesize knowledge using SEG",
            category="knowledge",
            input_schema={
                "type": "object",
                "properties": {
                    "topics": {"type": "array", "items": {"type": "string"}},
                    "depth": {"type": "string", "enum": ["shallow", "medium", "deep"]},
                    "format": {"type": "string", "enum": ["summary", "detailed", "structured"]}
                },
                "required": ["topics"]
            },
            execute_function=self._execute_synthesize_knowledge
        )
        self.tool_registry.register_tool(synthesize_knowledge_tool)
    
    def _register_cross_model_tools(self) -> None:
        """Register cross-model consciousness tools"""
        
        # Model selection tools
        select_models_tool = MCPTool(
            name="select_models",
            description="Select optimal models for cross-model operations",
            category="model_selection",
            input_schema={
                "type": "object",
                "properties": {
                    "task_complexity": {"type": "number", "minimum": 0, "maximum": 1},
                    "quality_requirements": {"type": "number", "minimum": 0, "maximum": 1},
                    "cost_constraints": {"type": "object"}
                },
                "required": ["task_complexity", "quality_requirements"]
            },
            execute_function=self._execute_select_models
        )
        self.tool_registry.register_tool(select_models_tool)
        
        evaluate_model_performance_tool = MCPTool(
            name="evaluate_model_performance",
            description="Evaluate model performance for specific tasks",
            category="model_selection",
            input_schema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string"},
                    "task_type": {"type": "string"},
                    "performance_metrics": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["model_id", "task_type"]
            },
            execute_function=self._execute_evaluate_model_performance
        )
        self.tool_registry.register_tool(evaluate_model_performance_tool)
        
        # Insight transfer tools
        extract_insights_tool = MCPTool(
            name="extract_insights",
            description="Extract structured insights from model outputs",
            category="insight_transfer",
            input_schema={
                "type": "object",
                "properties": {
                    "model_output": {"type": "string"},
                    "source_model": {"type": "string"},
                    "extraction_context": {"type": "object"}
                },
                "required": ["model_output", "source_model"]
            },
            execute_function=self._execute_extract_insights
        )
        self.tool_registry.register_tool(extract_insights_tool)
        
        transfer_insights_tool = MCPTool(
            name="transfer_insights",
            description="Transfer insights between models with quality validation",
            category="insight_transfer",
            input_schema={
                "type": "object",
                "properties": {
                    "source_model": {"type": "string"},
                    "target_model": {"type": "string"},
                    "insights": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["source_model", "target_model", "insights"]
            },
            execute_function=self._execute_transfer_insights
        )
        self.tool_registry.register_tool(transfer_insights_tool)
        
        execute_task_tool = MCPTool(
            name="execute_task",
            description="Execute task using cross-model consciousness",
            category="insight_transfer",
            input_schema={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string"},
                    "task_type": {"type": "string"},
                    "execution_context": {"type": "object"}
                },
                "required": ["task_description", "task_type"]
            },
            execute_function=self._execute_execute_task
        )
        self.tool_registry.register_tool(execute_task_tool)
        
        # Provenance tools
        generate_witness_tool = MCPTool(
            name="generate_witness",
            description="Generate cryptographic witness for cross-model operations",
            category="provenance",
            input_schema={
                "type": "object",
                "properties": {
                    "operation_data": {"type": "object"},
                    "operation_type": {"type": "string"},
                    "source_models": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["operation_data", "operation_type"]
            },
            execute_function=self._execute_generate_witness
        )
        self.tool_registry.register_tool(generate_witness_tool)
        
        calibrate_confidence_tool = MCPTool(
            name="calibrate_confidence",
            description="Calibrate confidence scores across different models",
            category="provenance",
            input_schema={
                "type": "object",
                "properties": {
                    "model_id": {"type": "string"},
                    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "calibration_context": {"type": "object"}
                },
                "required": ["model_id", "confidence_score"]
            },
            execute_function=self._execute_calibrate_confidence
        )
        self.tool_registry.register_tool(calibrate_confidence_tool)
        
        replay_operation_tool = MCPTool(
            name="replay_operation",
            description="Replay cross-model operation deterministically",
            category="provenance",
            input_schema={
                "type": "object",
                "properties": {
                    "operation_id": {"type": "string"},
                    "replay_context": {"type": "object"}
                },
                "required": ["operation_id"]
            },
            execute_function=self._execute_replay_operation
        )
        self.tool_registry.register_tool(replay_operation_tool)
        
        # Storage tools
        store_cross_model_atom_tool = MCPTool(
            name="store_cross_model_atom",
            description="Store cross-model atom with tracking and validation",
            category="storage",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "source_model": {"type": "string"},
                    "tags": {"type": "object"}
                },
                "required": ["content", "source_model"]
            },
            execute_function=self._execute_store_cross_model_atom
        )
        self.tool_registry.register_tool(store_cross_model_atom_tool)
        
        query_cross_model_atoms_tool = MCPTool(
            name="query_cross_model_atoms",
            description="Query cross-model atoms with model filtering",
            category="storage",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "model_filter": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            },
            execute_function=self._execute_query_cross_model_atoms
        )
        self.tool_registry.register_tool(query_cross_model_atoms_tool)
        
        get_cross_model_stats_tool = MCPTool(
            name="get_cross_model_stats",
            description="Get statistics about cross-model operations",
            category="storage",
            input_schema={
                "type": "object",
                "properties": {
                    "time_period": {"type": "string"},
                    "model_filter": {"type": "array", "items": {"type": "string"}}
                }
            },
            execute_function=self._execute_get_cross_model_stats
        )
        self.tool_registry.register_tool(get_cross_model_stats_tool)
    
    async def handle_request(self, request_data: str) -> str:
        """Handle incoming JSON-RPC request"""
        
        try:
            # Parse request
            request = self._parse_request(request_data)
            
            # Log request
            self.logging_system.log_request(request)
            
            # Handle request based on method
            if request.method == "initialize":
                response = await self._handle_initialize(request)
            elif request.method == "tools/list":
                response = await self._handle_tools_list(request)
            elif request.method == "tools/call":
                response = await self._handle_tools_call(request)
            else:
                response = self.error_handler.handle_method_not_found(request)
            
            # Log response
            self.logging_system.log_response(response)
            
            return json.dumps(response)
            
        except Exception as e:
            error_response = self.error_handler.handle_general_error(request, e)
            self.logging_system.log_error(error_response)
            return json.dumps(error_response)
    
    def _parse_request(self, request_data: str) -> Dict[str, Any]:
        """Parse JSON-RPC request"""
        try:
            return json.loads(request_data)
        except json.JSONDecodeError as e:
            raise JSONRPCParseError(f"Failed to parse request: {str(e)}")
    
    async def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "aimos-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = []
        for tool in self.tool_registry.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Get tool
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return self.error_handler.handle_tool_not_found(request, tool_name)
        
        try:
            # Execute tool
            result = await tool.execute_function(arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            return self.error_handler.handle_tool_execution_error(request, tool_name, e)
```

### **Tool Execution Implementation**
```python
class ToolExecutor:
    """Execute MCP tools with error handling and logging"""
    
    def __init__(self):
        self.execution_logger: ExecutionLogger = ExecutionLogger()
        self.performance_tracker: PerformanceTracker = PerformanceTracker()
        self.error_handler: ToolErrorHandler = ToolErrorHandler()
    
    async def execute_tool(self, tool: MCPTool, arguments: Dict[str, Any]) -> Any:
        """Execute tool with performance tracking and error handling"""
        
        start_time = datetime.now()
        
        try:
            # Log tool execution
            self.execution_logger.log_tool_execution_start(tool, arguments)
            
            # Execute tool
            result = await tool.execute_function(arguments)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Track performance
            self.performance_tracker.record_execution(tool, execution_time, True)
            
            # Log successful execution
            self.execution_logger.log_tool_execution_success(tool, result, execution_time)
            
            return result
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Track performance
            self.performance_tracker.record_execution(tool, execution_time, False)
            
            # Log error
            self.execution_logger.log_tool_execution_error(tool, e, execution_time)
            
            # Handle error
            return self.error_handler.handle_tool_error(tool, e)
```

## 🧪 **Testing Implementation**

### **Unit Testing Framework**
```python
import pytest
from unittest.mock import Mock, patch
from mcp_integration import MCPServer, MCPTool, ToolRegistry

class TestMCPServer:
    """Unit tests for MCP Server"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mcp_server = MCPServer()
        self.mock_request = {
            "jsonrpc": "2.0",
            "id": "test_id",
            "method": "tools/list",
            "params": {}
        }
    
    def test_initialize_server(self):
        """Test server initialization"""
        assert self.mcp_server.server_state.is_ready()
        assert len(self.mcp_server.tool_registry.list_tools()) == 16
    
    def test_handle_tools_list(self):
        """Test tools/list request handling"""
        response = asyncio.run(self.mcp_server._handle_tools_list(self.mock_request))
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test_id"
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 16
    
    def test_handle_tools_call(self):
        """Test tools/call request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": "test_id",
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "Test content",
                    "tags": {"test": "tag"}
                }
            }
        }
        
        response = asyncio.run(self.mcp_server._handle_tools_call(request))
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "test_id"
        assert "result" in response
        assert "content" in response["result"]
    
    def test_parse_request(self):
        """Test request parsing"""
        request_data = json.dumps(self.mock_request)
        parsed_request = self.mcp_server._parse_request(request_data)
        
        assert parsed_request["jsonrpc"] == "2.0"
        assert parsed_request["method"] == "tools/list"

class TestToolRegistry:
    """Unit tests for Tool Registry"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool_registry = ToolRegistry()
        self.mock_tool = MCPTool(
            name="test_tool",
            description="Test tool description",
            category="test",
            input_schema={"type": "object"},
            execute_function=Mock()
        )
    
    def test_register_tool(self):
        """Test tool registration"""
        result = self.tool_registry.register_tool(self.mock_tool)
        
        assert result.success
        assert self.mock_tool.name in self.tool_registry.tools
    
    def test_get_tool(self):
        """Test tool retrieval"""
        self.tool_registry.register_tool(self.mock_tool)
        retrieved_tool = self.tool_registry.get_tool("test_tool")
        
        assert retrieved_tool == self.mock_tool
    
    def test_list_tools(self):
        """Test tool listing"""
        self.tool_registry.register_tool(self.mock_tool)
        tools = self.tool_registry.list_tools()
        
        assert len(tools) == 1
        assert tools[0] == self.mock_tool
    
    def test_list_tools_by_category(self):
        """Test tool listing by category"""
        self.tool_registry.register_tool(self.mock_tool)
        tools = self.tool_registry.list_tools_by_category("test")
        
        assert len(tools) == 1
        assert tools[0] == self.mock_tool

class TestToolExecution:
    """Unit tests for Tool Execution"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool_executor = ToolExecutor()
        self.mock_tool = MCPTool(
            name="test_tool",
            description="Test tool description",
            category="test",
            input_schema={"type": "object"},
            execute_function=Mock()
        )
    
    def test_execute_tool_success(self):
        """Test successful tool execution"""
        self.mock_tool.execute_function.return_value = {"result": "success"}
        
        result = asyncio.run(self.tool_executor.execute_tool(self.mock_tool, {}))
        
        assert result["result"] == "success"
        self.mock_tool.execute_function.assert_called_once()
    
    def test_execute_tool_failure(self):
        """Test tool execution failure"""
        self.mock_tool.execute_function.side_effect = Exception("Test error")
        
        result = asyncio.run(self.tool_executor.execute_tool(self.mock_tool, {}))
        
        assert "error" in result
        assert result["error"] == "Test error"
```

### **Integration Testing Framework**
```python
class TestMCPIntegration:
    """Integration tests for MCP integration"""
    
    def setup_method(self):
        """Setup integration test fixtures"""
        self.mcp_server = MCPServer()
        self.test_requests = [
            {
                "jsonrpc": "2.0",
                "id": "test_1",
                "method": "initialize",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": "test_2",
                "method": "tools/list",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": "test_3",
                "method": "tools/call",
                "params": {
                    "name": "store_memory",
                    "arguments": {
                        "content": "Integration test content",
                        "tags": {"test": "integration"}
                    }
                }
            }
        ]
    
    def test_end_to_end_mcp_workflow(self):
        """Test complete MCP workflow"""
        
        # Test initialize
        init_response = asyncio.run(self.mcp_server._handle_initialize(self.test_requests[0]))
        assert init_response["jsonrpc"] == "2.0"
        assert "result" in init_response
        
        # Test tools/list
        list_response = asyncio.run(self.mcp_server._handle_tools_list(self.test_requests[1]))
        assert list_response["jsonrpc"] == "2.0"
        assert "tools" in list_response["result"]
        assert len(list_response["result"]["tools"]) == 16
        
        # Test tools/call
        call_response = asyncio.run(self.mcp_server._handle_tools_call(self.test_requests[2]))
        assert call_response["jsonrpc"] == "2.0"
        assert "result" in call_response
        assert "content" in call_response["result"]
    
    def test_mcp_server_initialization(self):
        """Test MCP server initialization"""
        assert self.mcp_server.server_state.is_ready()
        assert len(self.mcp_server.tool_registry.list_tools()) == 16
        
        # Verify all tool categories are represented
        categories = set()
        for tool in self.mcp_server.tool_registry.list_tools():
            categories.add(tool.category)
        
        expected_categories = {"memory", "orchestration", "verification", "knowledge", 
                             "model_selection", "insight_transfer", "provenance", "storage"}
        assert categories == expected_categories
    
    def test_tool_execution_performance(self):
        """Test tool execution performance"""
        tool = self.mcp_server.tool_registry.get_tool("store_memory")
        
        start_time = datetime.now()
        result = asyncio.run(tool.execute_function({
            "content": "Performance test content",
            "tags": {"test": "performance"}
        }))
        execution_time = (datetime.now() - start_time).total_seconds()
        
        assert execution_time < 1.0  # Should execute in less than 1 second
        assert result is not None
```

## 🚀 **Deployment Implementation**

### **Production Deployment Configuration**
```python
class MCPDeployment:
    """Production deployment for MCP integration"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.deployment_manager = DeploymentManager()
        self.monitoring_setup = MonitoringSetup()
        self.scaling_manager = ScalingManager()
    
    def deploy(self) -> DeploymentResult:
        """Deploy MCP integration to production"""
        try:
            # Initialize components
            self._initialize_components()
            
            # Configure MCP server
            self._configure_mcp_server()
            
            # Setup monitoring
            self._setup_monitoring()
            
            # Configure scaling
            self._configure_scaling()
            
            # Validate deployment
            validation_result = self._validate_deployment()
            
            if validation_result.is_valid:
                return DeploymentResult(
                    success=True,
                    deployment_id=str(uuid.uuid4()),
                    deployment_timestamp=datetime.utcnow(),
                    validation_result=validation_result
                )
            else:
                return DeploymentResult(
                    success=False,
                    error=validation_result.error,
                    deployment_timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=str(e),
                deployment_timestamp=datetime.utcnow()
            )
    
    def _initialize_components(self) -> None:
        """Initialize all MCP components"""
        # Implementation for component initialization
        pass
    
    def _configure_mcp_server(self) -> None:
        """Configure MCP server"""
        # Implementation for MCP server configuration
        pass
    
    def _setup_monitoring(self) -> None:
        """Setup monitoring and health checks"""
        # Implementation for monitoring setup
        pass
    
    def _configure_scaling(self) -> None:
        """Configure scaling for MCP server"""
        # Implementation for scaling configuration
        pass
    
    def _validate_deployment(self) -> ValidationResult:
        """Validate deployment configuration"""
        # Implementation for deployment validation
        return ValidationResult(is_valid=True)
```

---

**Next Level:** [L4 Complete (15kw+)](L4_complete.md)  
**Code:** `run_mcp_cross_model.py`, `packages/mcp_server/`
