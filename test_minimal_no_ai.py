#!/usr/bin/env python3
"""
Test the minimal MCP server with no AI dependencies
"""

import subprocess
import sys
import json
import time

def test_minimal_no_ai():
    """
    Test the minimal MCP server with no AI
    """
    print("Testing Minimal MCP Server (No AI)...")
    print("=" * 50)
    
    try:
        # Start the minimal server
        print("Starting minimal server...")
        process = subprocess.Popen(
            ["python", "-u", "minimal_mcp_no_ai.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        print("Server started, waiting for initialization...")
        time.sleep(1)
        
        # Test tools/list
        print("Testing tools/list...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        print("Waiting for response...")
        time.sleep(1)
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Response: {response}")
            
            if "tools" in response:
                print("[PASS] Minimal server working!")
                print(f"Found {len(response['tools'])} tools")
                for tool in response['tools']:
                    print(f"  - {tool['name']}: {tool['description']}")
                
                # Test tool calling
                print("\nTesting tool calling...")
                tool_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "echo",
                        "arguments": {"message": "Hello World"}
                    }
                }
                
                tool_request_json = json.dumps(tool_request) + "\n"
                process.stdin.write(tool_request_json)
                process.stdin.flush()
                
                time.sleep(1)
                
                tool_response_line = process.stdout.readline()
                if tool_response_line:
                    tool_response = json.loads(tool_response_line.strip())
                    print(f"Tool response: {tool_response}")
                    
                    if "content" in tool_response:
                        print("[PASS] Tool calling works!")
                    else:
                        print("[FAIL] Tool calling failed")
                else:
                    print("[FAIL] No tool response")
            else:
                print("[FAIL] No tools found in response")
        else:
            print("[FAIL] No response received")
        
        # Clean up
        process.terminate()
        process.wait()
        
        print("\nTest complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing minimal server: {e}")
        return False

if __name__ == "__main__":
    test_minimal_no_ai()

