#!/usr/bin/env python3
"""
Test the advanced MCP server with 16 tools - simplified version
"""

import subprocess
import sys
import json
import time
import os

def test_advanced_mcp_server():
    """
    Test the advanced MCP server with 16 tools
    """
    print("Testing Advanced MCP Server (16 Tools)...")
    print("=" * 60)
    
    # Set up environment
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
    env["CEREBRAS_API_KEY"] = "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
    env["PYTHONPATH"] = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    try:
        # Start the advanced server
        print("Starting advanced server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_cross_model.py"],
            cwd="C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        print("Server started, waiting for initialization...")
        time.sleep(3)
        
        # Test tools/list directly
        print("Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        tools_request_json = json.dumps(tools_request) + "\n"
        process.stdin.write(tools_request_json)
        process.stdin.flush()
        
        time.sleep(3)
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Response: {response}")
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"[PASS] Advanced server working!")
                print(f"Found {len(tools)} tools")
                
                # List all tools
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
                
                # Check for expected tools
                tool_names = [tool["name"] for tool in tools]
                
                # Expected tools
                expected_tools = [
                    "store_memory", "get_memory_stats", "retrieve_memory",
                    "create_plan", "track_confidence", "synthesize_knowledge",
                    "select_models", "extract_insights", "transfer_insights",
                    "execute_task", "generate_witness", "calibrate_confidence",
                    "replay_operation", "store_cross_model_atom", "query_cross_model_atoms",
                    "get_cross_model_stats"
                ]
                
                print(f"\nExpected tools: {len(expected_tools)}")
                print(f"Found tools: {len(tools)}")
                
                missing_tools = [tool for tool in expected_tools if tool not in tool_names]
                if missing_tools:
                    print(f"Missing tools: {missing_tools}")
                else:
                    print("[PASS] All expected tools found!")
                
            else:
                print("[FAIL] No tools found in response")
                print(f"Response structure: {list(response.keys())}")
        else:
            print("[FAIL] No response received")
        
        # Clean up
        process.terminate()
        process.wait()
        
        print("\nTest complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing advanced server: {e}")
        return False

if __name__ == "__main__":
    test_advanced_mcp_server()
