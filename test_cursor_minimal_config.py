#!/usr/bin/env python3
"""
Test the exact configuration that Cursor will use for the minimal server
"""

import subprocess
import sys
import json
import time
import os

def test_cursor_minimal_config():
    """
    Test the exact configuration that Cursor will use
    """
    print("Testing Cursor Minimal Configuration...")
    print("=" * 50)
    
    # Set up environment exactly as Cursor will
    env = os.environ.copy()
    env["PYTHONPATH"] = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    # The exact command Cursor will use
    cwd = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    cmd = ["python", "-u", "minimal_mcp_no_ai.py"]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Working Directory: {cwd}")
    print(f"Environment: PYTHONPATH set")
    print()
    
    try:
        # Start the server exactly as Cursor will
        print("Starting minimal server...")
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        print("Server started, waiting for initialization...")
        time.sleep(2)
        
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
        time.sleep(2)
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"Response: {response}")
            
            if "tools" in response:
                print("[PASS] Minimal server working with Cursor config!")
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
                        "name": "get_status",
                        "arguments": {}
                    }
                }
                
                tool_request_json = json.dumps(tool_request) + "\n"
                process.stdin.write(tool_request_json)
                process.stdin.flush()
                
                time.sleep(2)
                
                tool_response_line = process.stdout.readline()
                if tool_response_line:
                    tool_response = json.loads(tool_response_line.strip())
                    print(f"Tool response: {tool_response}")
                    
                    if "content" in tool_response:
                        print("[PASS] Tool calling works with Cursor config!")
                        
                        # Parse status response
                        status_text = tool_response['content'][0]['text']
                        status = json.loads(status_text)
                        print(f"Server status: {status}")
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
    test_cursor_minimal_config()

