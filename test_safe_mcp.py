#!/usr/bin/env python3
"""
Test the safe MCP server
"""

import subprocess
import sys
import json
import time

def test_safe_server():
    """
    Test the safe MCP server
    """
    print("Testing Safe MCP Server...")
    print("=" * 50)
    
    try:
        # Start the safe server
        print("Starting safe server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_stdio_safe.py"],
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
                print("[PASS] Safe server working!")
                print(f"Found {len(response['tools'])} tools")
                for tool in response['tools']:
                    print(f"  - {tool['name']}: {tool['description']}")
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
        print(f"[ERROR] Error testing safe server: {e}")
        return False

if __name__ == "__main__":
    test_safe_server()

