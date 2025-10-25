#!/usr/bin/env python3
"""
Test the fixed AIM-OS MCP server
"""
import subprocess
import json
import time
import os

def test_fixed_server():
    """Test the fixed MCP server"""
    print("Testing fixed AIM-OS MCP server...")
    
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
        print("\n[1/3] Testing initialize...")
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
        print("\n[2/3] Testing tools/list...")
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
            if len(tools) == 2 and any(tool["name"] == "store_memory" for tool in tools):
                print("SUCCESS: Tools listed correctly")
            else:
                print(f"FAILED: Unexpected tools: {tools}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        # Test 3: Call store_memory
        print("\n[3/3] Testing store_memory...")
        store_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "Test memory from fixed server",
                    "tags": {"test": 1, "fixed": 1}
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
                print(f"Response: {response['result']}")
            else:
                print(f"FAILED: Error response: {response}")
                return False
        else:
            print("FAILED: No response from server")
            return False
        
        print("\nSUCCESS: ALL TESTS PASSED - Fixed server works!")
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
    success = test_fixed_server()
    if success:
        print("\nSUCCESS: Fixed AIM-OS MCP server is ready for Cursor!")
    else:
        print("\nERROR: Fixed server has issues")
