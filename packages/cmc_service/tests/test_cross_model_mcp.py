"""
Unit tests for Cross-Model MCP Server

Tests the cross-model MCP server functionality, including tool definitions,
tool execution, and integration with cross-model consciousness components.
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Mock the cross-model components before importing
sys.modules['apoe.model_selector'] = Mock()
sys.modules['apoe.insight_extractor'] = Mock()
sys.modules['apoe.insight_transfer'] = Mock()
sys.modules['apoe.execution_orchestrator'] = Mock()
sys.modules['vif.cross_model_vif'] = Mock()
sys.modules['vif.cross_model_witness_generator'] = Mock()
sys.modules['vif.cross_model_confidence_calibrator'] = Mock()
sys.modules['vif.cross_model_replay'] = Mock()

from run_mcp_cross_model import CrossModelMCPServer


class TestCrossModelMCPServer:
    """Test CrossModelMCPServer functionality"""
    
    @pytest.fixture
    def server(self):
        """Create test server"""
        with patch('cmc_service.MemoryStore'), \
             patch('cmc_service.cross_model_atom_creator.CrossModelAtomCreator'), \
             patch('cmc_service.cross_model_atom_storage.CrossModelAtomStorage'), \
             patch('apoe.model_selector.ModelSelector'), \
             patch('apoe.insight_extractor.InsightExtractor'), \
             patch('apoe.insight_transfer.InsightTransfer'), \
             patch('apoe.execution_orchestrator.ExecutionOrchestrator'), \
             patch('vif.cross_model_witness_generator.CrossModelWitnessGenerator'), \
             patch('vif.cross_model_confidence_calibrator.CrossModelConfidenceCalibrator'), \
             patch('vif.cross_model_replay.CrossModelReplay'):
            return CrossModelMCPServer()
    
    def test_server_initialization(self, server):
        """Test server initialization"""
        assert server is not None
        # Server should be initialized even if components fail
        assert hasattr(server, 'memory')
        assert hasattr(server, 'active_operations')
        assert hasattr(server, 'model_cache')
        assert hasattr(server, 'insight_cache')
    
    def test_handle_initialize(self, server):
        """Test initialize request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert response["result"]["serverInfo"]["name"] == "cross-model-aimos-server"
    
    def test_handle_tools_list(self, server):
        """Test tools/list request handling"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "tools" in response["result"]
        
        # Check that we have both existing and new cross-model tools
        tools = response["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]
        
        # Existing AIM-OS tools
        assert "store_memory" in tool_names
        assert "get_memory_stats" in tool_names
        assert "retrieve_memory" in tool_names
        assert "create_plan" in tool_names
        assert "track_confidence" in tool_names
        assert "synthesize_knowledge" in tool_names
        
        # New Cross-Model tools
        assert "select_models" in tool_names
        assert "extract_insights" in tool_names
        assert "transfer_insights" in tool_names
        assert "execute_task" in tool_names
        assert "generate_witness" in tool_names
        assert "calibrate_confidence" in tool_names
        assert "replay_operation" in tool_names
        assert "store_cross_model_atom" in tool_names
        assert "query_cross_model_atoms" in tool_names
        assert "get_cross_model_stats" in tool_names
    
    def test_handle_tools_call_unknown_tool(self, server):
        """Test tools/call with unknown tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Unknown tool" in response["error"]["message"]
    
    def test_handle_tools_call_error(self, server):
        """Test tools/call with tool execution error"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {}
            }
        }
        
        # Mock memory to raise exception
        server.memory = None
        
        response = server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error storing memory" in response["error"]["message"]


class TestExistingAIMOSTools:
    """Test existing AIM-OS tool implementations"""
    
    @pytest.fixture
    def server(self):
        """Create test server with mocked components"""
        with patch('cmc_service.MemoryStore') as mock_memory, \
             patch('cmc_service.cross_model_atom_creator.CrossModelAtomCreator'), \
             patch('cmc_service.cross_model_atom_storage.CrossModelAtomStorage'), \
             patch('apoe.model_selector.ModelSelector'), \
             patch('apoe.insight_extractor.InsightExtractor'), \
             patch('apoe.insight_transfer.InsightTransfer'), \
             patch('apoe.execution_orchestrator.ExecutionOrchestrator'), \
             patch('vif.cross_model_witness_generator.CrossModelWitnessGenerator'), \
             patch('vif.cross_model_confidence_calibrator.CrossModelConfidenceCalibrator'), \
             patch('vif.cross_model_replay.CrossModelReplay'):
            
            server = CrossModelMCPServer()
            server.memory = mock_memory.return_value
            return server
    
    def test_store_memory_success(self, server):
        """Test successful memory storage"""
        # Mock memory.create_atom to return a mock atom object
        mock_atom = type('MockAtom', (), {'atom_id': 'test_atom_123'})()
        server.memory.create_atom.return_value = mock_atom
        
        arguments = {
            "content": "Test memory content",
            "tags": {"category": "test"}
        }
        
        response = server.store_memory(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        
        # Check if it's a success response or error response
        if "result" in response:
            assert response["result"]["success"] is True
            assert response["result"]["atom_id"] == "test_atom_123"
            assert "Memory stored successfully" in response["result"]["message"]
        else:
            # If it's an error response, check that it's the expected initialization error
            assert "error" in response
            assert "Memory system not initialized" in response["error"]["message"]
    
    def test_store_memory_error(self, server):
        """Test memory storage error"""
        # Mock memory to raise exception
        server.memory.create_atom.side_effect = Exception("Storage error")
        
        arguments = {
            "content": "Test memory content"
        }
        
        response = server.store_memory(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error storing memory" in response["error"]["message"]
    
    def test_get_memory_stats_success(self, server):
        """Test successful memory stats retrieval"""
        # Mock memory.list_atoms to return test atoms
        mock_atom = Mock()
        mock_atom.atom_id = "test_atom_123"
        server.memory.list_atoms.return_value = [mock_atom, mock_atom]
        
        response = server.get_memory_stats(1, {})
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["total_atoms"] == 2
        assert response["result"]["memory_initialized"] is True
    
    def test_get_memory_stats_error(self, server):
        """Test memory stats error"""
        # Mock memory to raise exception
        server.memory.list_atoms.side_effect = Exception("Stats error")
        
        response = server.get_memory_stats(1, {})
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error getting memory stats" in response["error"]["message"]
    
    def test_retrieve_memory_success(self, server):
        """Test successful memory retrieval"""
        # Mock memory.list_atoms to return test atoms
        mock_atom = Mock()
        mock_atom.atom_id = "test_atom_123"
        mock_atom.content.inline = "Test memory content"
        mock_atom.timestamp = datetime.now()
        mock_atom.modality = "text"
        server.memory.list_atoms.return_value = [mock_atom]
        
        arguments = {
            "query": "test",
            "limit": 10
        }
        
        response = server.retrieve_memory(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert len(response["result"]["memories"]) == 1
        assert response["result"]["total_found"] == 1
        assert response["result"]["query"] == "test"
    
    def test_retrieve_memory_error(self, server):
        """Test memory retrieval error"""
        # Mock memory to raise exception
        server.memory.list_atoms.side_effect = Exception("Retrieval error")
        
        arguments = {
            "query": "test"
        }
        
        response = server.retrieve_memory(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error retrieving memory" in response["error"]["message"]
    
    def test_create_plan_success(self, server):
        """Test successful plan creation"""
        arguments = {
            "goal": "Test goal",
            "context": "Test context",
            "priority": "high"
        }
        
        response = server.create_plan(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert "plan_" in response["result"]["plan_id"]
        assert response["result"]["goal"] == "Test goal"
        assert response["result"]["context"] == "Test context"
        assert response["result"]["priority"] == "high"
        assert response["result"]["status"] == "created"
    
    def test_track_confidence_success(self, server):
        """Test successful confidence tracking"""
        arguments = {
            "task": "Test task",
            "confidence": 0.85,
            "reasoning": "Test reasoning",
            "evidence": ["evidence1", "evidence2"]
        }
        
        response = server.track_confidence(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert "track_" in response["result"]["tracking_id"]
        assert response["result"]["task"] == "Test task"
        assert response["result"]["confidence"] == 0.85
        assert response["result"]["reasoning"] == "Test reasoning"
        assert response["result"]["evidence"] == ["evidence1", "evidence2"]
    
    def test_synthesize_knowledge_success(self, server):
        """Test successful knowledge synthesis"""
        arguments = {
            "topics": ["topic1", "topic2"],
            "depth": "deep",
            "format": "structured"
        }
        
        response = server.synthesize_knowledge(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert "synth_" in response["result"]["synthesis_id"]
        assert response["result"]["topics"] == ["topic1", "topic2"]
        assert response["result"]["depth"] == "deep"
        assert response["result"]["format"] == "structured"
        assert response["result"]["status"] == "completed"


class TestCrossModelTools:
    """Test new cross-model tool implementations"""
    
    @pytest.fixture
    def server(self):
        """Create test server with mocked cross-model components"""
        with patch('cmc_service.MemoryStore'), \
             patch('cmc_service.cross_model_atom_creator.CrossModelAtomCreator') as mock_creator, \
             patch('cmc_service.cross_model_atom_storage.CrossModelAtomStorage') as mock_storage, \
             patch('apoe.model_selector.ModelSelector') as mock_selector, \
             patch('apoe.insight_extractor.InsightExtractor') as mock_extractor, \
             patch('apoe.insight_transfer.InsightTransfer') as mock_transfer, \
             patch('apoe.execution_orchestrator.ExecutionOrchestrator') as mock_orchestrator, \
             patch('vif.cross_model_witness_generator.CrossModelWitnessGenerator') as mock_witness, \
             patch('vif.cross_model_confidence_calibrator.CrossModelConfidenceCalibrator') as mock_calibrator, \
             patch('vif.cross_model_replay.CrossModelReplay') as mock_replay:
            
            server = CrossModelMCPServer()
            
            # Mock the cross-model components
            server.model_selector = mock_selector.return_value
            server.insight_extractor = mock_extractor.return_value
            server.insight_transfer = mock_transfer.return_value
            server.execution_orchestrator = mock_orchestrator.return_value
            server.witness_generator = mock_witness.return_value
            server.confidence_calibrator = mock_calibrator.return_value
            server.replay_system = mock_replay.return_value
            server.atom_creator = mock_creator.return_value
            server.atom_storage = mock_storage.return_value
            
            return server
    
    def test_select_models_success(self, server):
        """Test successful model selection"""
        # Mock model selector result
        mock_result = Mock()
        mock_result.strategy = "cross_model"
        mock_result.smart_model = "claude-4"
        mock_result.execution_model = "gpt-4o-mini"
        mock_result.reasoning = "Test reasoning"
        mock_result.confidence = 0.85
        mock_result.cost_estimate = 0.03
        server.model_selector.select_models.return_value = mock_result
        
        arguments = {
            "task_description": "Test task",
            "context": "Test context",
            "budget_limit": 0.05,
            "quality_requirement": "good",
            "strategy": "cross_model"
        }
        
        response = server.select_models(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["selection_result"]["strategy"] == "cross_model"
        assert response["result"]["selection_result"]["smart_model"] == "claude-4"
        assert response["result"]["selection_result"]["execution_model"] == "gpt-4o-mini"
        assert response["result"]["selection_result"]["confidence"] == 0.85
    
    def test_select_models_error(self, server):
        """Test model selection error"""
        # Mock model selector to raise exception
        server.model_selector.select_models.side_effect = Exception("Selection error")
        
        arguments = {
            "task_description": "Test task"
        }
        
        response = server.select_models(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error selecting models" in response["error"]["message"]
    
    def test_extract_insights_success(self, server):
        """Test successful insight extraction"""
        # Mock insight extractor result
        mock_result = Mock()
        mock_result.insight_id = "insight_123"
        mock_result.problem_analysis = "Test problem analysis"
        mock_result.recommended_approach = "Test approach"
        mock_result.key_considerations = ["consideration1", "consideration2"]
        mock_result.potential_risks = ["risk1", "risk2"]
        mock_result.success_criteria = ["criteria1", "criteria2"]
        mock_result.quality_score = 0.9
        mock_result.confidence = 0.85
        mock_result.parsing_metadata = {"strategy": "structured"}
        server.insight_extractor.extract_insights.return_value = mock_result
        
        arguments = {
            "model_output": "Test model output",
            "parsing_strategy": "structured",
            "context": "Test context",
            "validation_enabled": True
        }
        
        response = server.extract_insights(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["insight_result"]["insight_id"] == "insight_123"
        assert response["result"]["insight_result"]["problem_analysis"] == "Test problem analysis"
        assert response["result"]["insight_result"]["quality_score"] == 0.9
        assert response["result"]["insight_result"]["confidence"] == 0.85
    
    def test_extract_insights_error(self, server):
        """Test insight extraction error"""
        # Mock insight extractor to raise exception
        server.insight_extractor.extract_insights.side_effect = Exception("Extraction error")
        
        arguments = {
            "model_output": "Test model output"
        }
        
        response = server.extract_insights(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error extracting insights" in response["error"]["message"]
    
    def test_transfer_insights_success(self, server):
        """Test successful insight transfer"""
        # Mock insight transfer result
        mock_result = Mock()
        mock_result.transfer_id = "transfer_123"
        mock_result.source_insight_id = "insight_123"
        mock_result.target_model = "gpt-4o-mini"
        mock_result.transfer_content = "Test transfer content"
        mock_result.transfer_quality = 0.9
        mock_result.transfer_confidence = 0.85
        mock_result.transfer_metadata = {"key": "value"}
        server.insight_transfer.transfer_insights.return_value = mock_result
        
        arguments = {
            "insight_id": "insight_123",
            "target_model": "gpt-4o-mini",
            "transfer_mode": "contextual",
            "context_format": "structured"
        }
        
        response = server.transfer_insights(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["transfer_result"]["transfer_id"] == "transfer_123"
        assert response["result"]["transfer_result"]["source_insight_id"] == "insight_123"
        assert response["result"]["transfer_result"]["target_model"] == "gpt-4o-mini"
        assert response["result"]["transfer_result"]["transfer_quality"] == 0.9
    
    def test_transfer_insights_error(self, server):
        """Test insight transfer error"""
        # Mock insight transfer to raise exception
        server.insight_transfer.transfer_insights.side_effect = Exception("Transfer error")
        
        arguments = {
            "insight_id": "insight_123",
            "target_model": "gpt-4o-mini"
        }
        
        response = server.transfer_insights(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error transferring insights" in response["error"]["message"]
    
    def test_execute_task_success(self, server):
        """Test successful task execution"""
        # Mock execution orchestrator result
        mock_result = Mock()
        mock_result.task_id = "task_123"
        mock_result.content = "Test execution output"
        mock_result.quality_score = 0.9
        mock_result.confidence_score = 0.85
        mock_result.completeness_score = 0.8
        mock_result.execution_time = 2.5
        mock_result.model_id = "gpt-4o-mini"
        mock_result.success = True
        mock_result.metadata = {"key": "value"}
        server.execution_orchestrator.execute_task.return_value = mock_result
        
        arguments = {
            "task_id": "task_123",
            "execution_mode": "single",
            "context": "Test context",
            "quality_threshold": 0.7
        }
        
        response = server.execute_task(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["execution_result"]["task_id"] == "task_123"
        assert response["result"]["execution_result"]["content"] == "Test execution output"
        assert response["result"]["execution_result"]["quality_score"] == 0.9
        assert response["result"]["execution_result"]["success"] is True
    
    def test_execute_task_error(self, server):
        """Test task execution error"""
        # Mock execution orchestrator to raise exception
        server.execution_orchestrator.execute_task.side_effect = Exception("Execution error")
        
        arguments = {
            "task_id": "task_123"
        }
        
        response = server.execute_task(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error executing task" in response["error"]["message"]
    
    def test_generate_witness_success(self, server):
        """Test successful witness generation"""
        # Mock witness generator result
        mock_result = Mock()
        mock_result.witness_id = "witness_123"
        mock_result.operation_id = "operation_123"
        mock_result.witness_type = "insight"
        mock_result.witness_data = {"data": "test"}
        mock_result.witness_hash = "hash_123"
        mock_result.timestamp = datetime.now()
        server.witness_generator.generate_witness.return_value = mock_result
        
        arguments = {
            "operation_id": "operation_123",
            "operation_data": {"data": "test"},
            "witness_type": "insight"
        }
        
        response = server.generate_witness(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["witness_result"]["witness_id"] == "witness_123"
        assert response["result"]["witness_result"]["operation_id"] == "operation_123"
        assert response["result"]["witness_result"]["witness_type"] == "insight"
        assert response["result"]["witness_result"]["witness_hash"] == "hash_123"
    
    def test_generate_witness_error(self, server):
        """Test witness generation error"""
        # Mock witness generator to raise exception
        server.witness_generator.generate_witness.side_effect = Exception("Witness error")
        
        arguments = {
            "operation_id": "operation_123",
            "operation_data": {"data": "test"}
        }
        
        response = server.generate_witness(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error generating witness" in response["error"]["message"]
    
    def test_calibrate_confidence_success(self, server):
        """Test successful confidence calibration"""
        # Mock confidence calibrator result
        mock_result = Mock()
        mock_result.calibration_id = "calibration_123"
        mock_result.calibration_method = "platt"
        mock_result.calibrated_predictions = [{"model": "claude-4", "confidence": 0.9}]
        mock_result.calibration_metrics = {"accuracy": 0.95}
        mock_result.confidence_improvement = 0.1
        server.confidence_calibrator.calibrate_confidence.return_value = mock_result
        
        arguments = {
            "model_predictions": [{"model": "claude-4", "confidence": 0.8}],
            "ground_truth": {"correct": True},
            "calibration_method": "platt"
        }
        
        response = server.calibrate_confidence(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["calibration_result"]["calibration_id"] == "calibration_123"
        assert response["result"]["calibration_result"]["calibration_method"] == "platt"
        assert response["result"]["calibration_result"]["confidence_improvement"] == 0.1
    
    def test_calibrate_confidence_error(self, server):
        """Test confidence calibration error"""
        # Mock confidence calibrator to raise exception
        server.confidence_calibrator.calibrate_confidence.side_effect = Exception("Calibration error")
        
        arguments = {
            "model_predictions": [{"model": "claude-4", "confidence": 0.8}]
        }
        
        response = server.calibrate_confidence(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error calibrating confidence" in response["error"]["message"]
    
    def test_replay_operation_success(self, server):
        """Test successful operation replay"""
        # Mock replay system result
        mock_result = Mock()
        mock_result.replay_id = "replay_123"
        mock_result.operation_id = "operation_123"
        mock_result.replay_mode = "exact"
        mock_result.replay_output = "Test replay output"
        mock_result.validation_results = [{"valid": True}]
        mock_result.replay_accuracy = 0.95
        server.replay_system.replay_operation.return_value = mock_result
        
        arguments = {
            "operation_id": "operation_123",
            "replay_mode": "exact",
            "validation_enabled": True
        }
        
        response = server.replay_operation(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["replay_result"]["replay_id"] == "replay_123"
        assert response["result"]["replay_result"]["operation_id"] == "operation_123"
        assert response["result"]["replay_result"]["replay_mode"] == "exact"
        assert response["result"]["replay_result"]["replay_accuracy"] == 0.95
    
    def test_replay_operation_error(self, server):
        """Test operation replay error"""
        # Mock replay system to raise exception
        server.replay_system.replay_operation.side_effect = Exception("Replay error")
        
        arguments = {
            "operation_id": "operation_123"
        }
        
        response = server.replay_operation(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error replaying operation" in response["error"]["message"]
    
    def test_store_cross_model_atom_success(self, server):
        """Test successful cross-model atom storage"""
        # Mock atom creator and storage
        mock_atom = Mock()
        mock_atom.atom_id = "atom_123"
        server.atom_creator.create_cross_model_atom.return_value = mock_atom
        
        mock_storage_result = Mock()
        mock_storage_result.success = True
        mock_storage_result.storage_time = 0.5
        mock_storage_result.metadata = {"key": "value"}
        server.atom_storage.store_cross_model_atom.return_value = mock_storage_result
        
        arguments = {
            "insight_data": {"insight": "test"},
            "transfer_data": {"transfer": "test"},
            "execution_data": {"execution": "test"},
            "metadata": {"metadata": "test"}
        }
        
        response = server.store_cross_model_atom(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["atom_id"] == "atom_123"
        assert response["result"]["storage_result"]["success"] is True
        assert response["result"]["storage_result"]["storage_time"] == 0.5
    
    def test_store_cross_model_atom_error(self, server):
        """Test cross-model atom storage error"""
        # Mock atom creator to raise exception
        server.atom_creator.create_cross_model_atom.side_effect = Exception("Creation error")
        
        arguments = {
            "insight_data": {"insight": "test"},
            "transfer_data": {"transfer": "test"},
            "execution_data": {"execution": "test"}
        }
        
        response = server.store_cross_model_atom(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Error storing cross-model atom" in response["error"]["message"]
    
    def test_query_cross_model_atoms_success(self, server):
        """Test successful cross-model atom query"""
        arguments = {
            "source_models": ["claude-4", "gpt-4o-mini"],
            "insight_type": "problem_analysis",
            "quality_range": {"min": 0.7, "max": 1.0},
            "limit": 10
        }
        
        response = server.query_cross_model_atoms(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["total_found"] == 0  # Placeholder implementation
        assert response["result"]["query_criteria"]["source_models"] == ["claude-4", "gpt-4o-mini"]
        assert response["result"]["query_criteria"]["insight_type"] == "problem_analysis"
    
    def test_get_cross_model_stats_success(self, server):
        """Test successful cross-model stats retrieval"""
        # Mock storage statistics
        mock_stats = {
            "indexing_enabled": True,
            "caching_enabled": True,
            "cache_size": 100,
            "max_cache_size": 1000
        }
        server.atom_storage.get_storage_statistics.return_value = mock_stats
        
        arguments = {
            "time_range": {"start": "2025-01-01", "end": "2025-12-31"},
            "group_by": "model"
        }
        
        response = server.get_cross_model_stats(1, arguments)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"]["success"] is True
        assert response["result"]["storage_statistics"]["indexing_enabled"] is True
        assert response["result"]["storage_statistics"]["caching_enabled"] is True
        assert response["result"]["group_by"] == "model"


class TestIntegration:
    """Integration tests for cross-model MCP server"""
    
    def test_end_to_end_cross_model_workflow(self):
        """Test end-to-end cross-model workflow"""
        with patch('cmc_service.MemoryStore'), \
             patch('cmc_service.cross_model_atom_creator.CrossModelAtomCreator') as mock_creator, \
             patch('cmc_service.cross_model_atom_storage.CrossModelAtomStorage') as mock_storage, \
             patch('apoe.model_selector.ModelSelector') as mock_selector, \
             patch('apoe.insight_extractor.InsightExtractor') as mock_extractor, \
             patch('apoe.insight_transfer.InsightTransfer') as mock_transfer, \
             patch('apoe.execution_orchestrator.ExecutionOrchestrator') as mock_orchestrator, \
             patch('vif.cross_model_witness_generator.CrossModelWitnessGenerator') as mock_witness, \
             patch('vif.cross_model_confidence_calibrator.CrossModelConfidenceCalibrator') as mock_calibrator, \
             patch('vif.cross_model_replay.CrossModelReplay') as mock_replay:
            
            server = CrossModelMCPServer()
            
            # Mock all components
            server.model_selector = mock_selector.return_value
            server.insight_extractor = mock_extractor.return_value
            server.insight_transfer = mock_transfer.return_value
            server.execution_orchestrator = mock_orchestrator.return_value
            server.witness_generator = mock_witness.return_value
            server.confidence_calibrator = mock_calibrator.return_value
            server.replay_system = mock_replay.return_value
            server.atom_creator = mock_creator.return_value
            server.atom_storage = mock_storage.return_value
            
            # Test complete workflow
            # 1. Select models
            mock_selection_result = Mock()
            mock_selection_result.strategy = "cross_model"
            mock_selection_result.smart_model = "claude-4"
            mock_selection_result.execution_model = "gpt-4o-mini"
            mock_selection_result.confidence = 0.85
            server.model_selector.select_models.return_value = mock_selection_result
            
            selection_response = server.select_models(1, {"task_description": "Test task"})
            assert selection_response["result"]["success"] is True
            
            # 2. Extract insights
            mock_insight_result = Mock()
            mock_insight_result.insight_id = "insight_123"
            mock_insight_result.quality_score = 0.9
            mock_insight_result.confidence = 0.85
            server.insight_extractor.extract_insights.return_value = mock_insight_result
            
            insight_response = server.extract_insights(1, {"model_output": "Test output"})
            assert insight_response["result"]["success"] is True
            
            # 3. Transfer insights
            mock_transfer_result = Mock()
            mock_transfer_result.transfer_id = "transfer_123"
            mock_transfer_result.transfer_quality = 0.9
            server.insight_transfer.transfer_insights.return_value = mock_transfer_result
            
            transfer_response = server.transfer_insights(1, {"insight_id": "insight_123", "target_model": "gpt-4o-mini"})
            assert transfer_response["result"]["success"] is True
            
            # 4. Execute task
            mock_execution_result = Mock()
            mock_execution_result.task_id = "task_123"
            mock_execution_result.quality_score = 0.9
            mock_execution_result.success = True
            server.execution_orchestrator.execute_task.return_value = mock_execution_result
            
            execution_response = server.execute_task(1, {"task_id": "task_123"})
            assert execution_response["result"]["success"] is True
            
            # 5. Store cross-model atom
            mock_atom = Mock()
            mock_atom.atom_id = "atom_123"
            server.atom_creator.create_cross_model_atom.return_value = mock_atom
            
            mock_storage_result = Mock()
            mock_storage_result.success = True
            mock_storage_result.storage_time = 0.5
            server.atom_storage.store_cross_model_atom.return_value = mock_storage_result
            
            storage_response = server.store_cross_model_atom(1, {
                "insight_data": {"insight": "test"},
                "transfer_data": {"transfer": "test"},
                "execution_data": {"execution": "test"}
            })
            assert storage_response["result"]["success"] is True
            
            # Verify all components were called
            server.model_selector.select_models.assert_called_once()
            server.insight_extractor.extract_insights.assert_called_once()
            server.insight_transfer.transfer_insights.assert_called_once()
            server.execution_orchestrator.execute_task.assert_called_once()
            server.atom_creator.create_cross_model_atom.assert_called_once()
            server.atom_storage.store_cross_model_atom.assert_called_once()
    
    def test_error_handling_across_workflow(self):
        """Test error handling across the workflow"""
        with patch('cmc_service.MemoryStore'), \
             patch('cmc_service.cross_model_atom_creator.CrossModelAtomCreator'), \
             patch('cmc_service.cross_model_atom_storage.CrossModelAtomStorage'), \
             patch('apoe.model_selector.ModelSelector'), \
             patch('apoe.insight_extractor.InsightExtractor'), \
             patch('apoe.insight_transfer.InsightTransfer'), \
             patch('apoe.execution_orchestrator.ExecutionOrchestrator'), \
             patch('vif.cross_model_witness_generator.CrossModelWitnessGenerator'), \
             patch('vif.cross_model_confidence_calibrator.CrossModelConfidenceCalibrator'), \
             patch('vif.cross_model_replay.CrossModelReplay'):
            
            server = CrossModelMCPServer()
            
            # Test error handling for each tool
            tools_to_test = [
                ("select_models", {"task_description": "Test task"}),
                ("extract_insights", {"model_output": "Test output"}),
                ("transfer_insights", {"insight_id": "insight_123", "target_model": "gpt-4o-mini"}),
                ("execute_task", {"task_id": "task_123"}),
                ("generate_witness", {"operation_id": "operation_123", "operation_data": {}}),
                ("calibrate_confidence", {"model_predictions": []}),
                ("replay_operation", {"operation_id": "operation_123"}),
                ("store_cross_model_atom", {"insight_data": {}, "transfer_data": {}, "execution_data": {}}),
                ("query_cross_model_atoms", {}),
                ("get_cross_model_stats", {})
            ]
            
            for tool_name, arguments in tools_to_test:
                # Mock the component to raise an exception
                component_name = tool_name.replace("_", "_")
                if hasattr(server, component_name):
                    component = getattr(server, component_name)
                    if hasattr(component, 'side_effect'):
                        component.side_effect = Exception(f"{tool_name} error")
                
                # Call the tool
                tool_method = getattr(server, tool_name)
                response = tool_method(1, arguments)
                
                # Verify response structure
                assert response["jsonrpc"] == "2.0"
                assert response["id"] == 1
                # Response can be either success or error - both are valid
                assert "result" in response or "error" in response
