#!/usr/bin/env python3
"""
Test the working stdio MCP server that had 3 tools and was working
"""

import subprocess
import sys
import json
import time
import os

def test_working_stdio_server():
    """
    Test the working stdio MCP server
    """
    print("Testing Working Stdio MCP Server...")
    print("=" * 60)
    
    # Set up environment
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
    env["CEREBRAS_API_KEY"] = "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
    env["PYTHONPATH"] = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    try:
        # Start the working server
        print("Starting working stdio server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_stdio_clean.py"],
            cwd="C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        print("Server started, waiting for initialization...")
        time.sleep(5)  # Give more time for initialization
        
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
        
        protocols = []
        while True:
            try:
                response_line = process.stdout.readline()
                if not response_line:
                    break
                response = json.loads(response_line.strip())
                protocols.append(response)
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"[PASS] Working stdio server working!")
                    print(f"Found {len(tools)} tools")
                    
                    # List all tools
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                    
                    # Check for expected tools
                    tool_names = [tool["name"] for tool in tools]
                    expected_tools = ["ask_agent", "retrieve_memory", "get_agent_stats"]
                    
                    print(f"\nExpected tools: {expected_tools}")
                    print(f"Found tools: {tool_names}")
                    
                    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
                    if missing_tools:
                        print(f"Missing tools: {missing_tools}")
                    else:
                        print("[PASS] All expected tools found!")
                    
                    break
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error parsing response: {e}")
                break
        
        if not protocols:
            print("[FAIL] No response received")
        
        # Clean up
        process.terminate()
        process.wait()
        
        print("\nTest complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing working stdio server: {e}")
        return False

if __name__ == "__main__":
    test_working_stdio_server()
