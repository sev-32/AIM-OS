#!/usr/bin/env python3
"""
Test the extended AIM-OS MCP server with all tools
"""
import subprocess
import json
import time
import os

def test_extended_server():
    """Test the extended MCP server with all tools"""
    print("Testing extended AIM-OS MCP server...")
    
    # Start the server
    process = subprocess.Popen(
        ["python", "-u", "run_mcp_aimos_fixed.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Test 1: Initialize
        print("\n[1/6] Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if response.get("result", {}).get("serverInfo", {}).get("name") == "aimos-mcp-fixed":
                print("SUCCESS: Server initialized")
            else:
                print(f"FAILED: Unexpected response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 2: List tools
        print("\n[2/6] Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            if len(tools) == 6 and any(tool["name"] == "create_plan" for tool in tools):
                print("SUCCESS: All 6 tools listed correctly")
            else:
                print(f"FAILED: Expected 6 tools, got {len(tools)}: {[tool['name'] for tool in tools]}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 3: Create plan
        print("\n[3/6] Testing create_plan...")
        plan_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_plan",
                "arguments": {
                    "goal": "Test APOE plan creation",
                    "context": "Testing environment",
                    "priority": "high"
                }
            }
        }
        
        process.stdin.write(json.dumps(plan_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                print("SUCCESS: Plan created")
            else:
                print(f"FAILED: Error response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 4: Track confidence
        print("\n[4/6] Testing track_confidence...")
        confidence_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "track_confidence",
                "arguments": {
                    "task": "Test VIF confidence tracking",
                    "confidence": 0.85,
                    "reasoning": "Testing the system",
                    "evidence": ["Test evidence 1", "Test evidence 2"]
                }
            }
        }
        
        process.stdin.write(json.dumps(confidence_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                print("SUCCESS: Confidence tracked")
            else:
                print(f"FAILED: Error response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 5: Synthesize knowledge
        print("\n[5/6] Testing synthesize_knowledge...")
        synthesis_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "synthesize_knowledge",
                "arguments": {
                    "topics": ["AI consciousness", "MCP integration"],
                    "depth": "medium",
                    "format": "summary"
                }
            }
        }
        
        process.stdin.write(json.dumps(synthesis_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                print("SUCCESS: Knowledge synthesized")
            else:
                print(f"FAILED: Error response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 6: Store memory
        print("\n[6/6] Testing store_memory...")
        store_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "Extended AIM-OS MCP server test completed successfully",
                    "tags": {"test": 1, "extended": 1, "success": 1}
                }
            }
        }
        
        process.stdin.write(json.dumps(store_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                print("SUCCESS: Memory stored")
            else:
                print(f"FAILED: Error response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        print("\nSUCCESS: ALL 6 TESTS PASSED - Extended server works!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_extended_server()
    if success:
        print("\nSUCCESS: Extended AIM-OS MCP server is ready for Cursor!")
    else:
        print("\nERROR: Extended server has issues")
