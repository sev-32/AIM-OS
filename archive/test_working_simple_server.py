#!/usr/bin/env python3
"""
Test the working simple MCP server that had green dot
"""

import subprocess
import sys
import json
import time
import os

def test_working_simple_server():
    """
    Test the working simple MCP server
    """
    print("Testing Working Simple MCP Server...")
    print("=" * 60)
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    try:
        # Start the working server
        print("Starting working simple server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_aimos_simple.py"],
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
        
        # Test tools/list
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
                print(f"[PASS] Working simple server working!")
                print(f"Found {len(tools)} tools")
                
                # List all tools
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
                
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
        print(f"[ERROR] Error testing working simple server: {e}")
        return False

if __name__ == "__main__":
    test_working_simple_server()
