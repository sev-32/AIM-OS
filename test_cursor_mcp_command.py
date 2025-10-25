#!/usr/bin/env python3
"""
Test the exact command that Cursor will use to start the MCP server
"""

import subprocess
import sys
import os
import json
import time

def test_cursor_command():
    """
    Test the exact command that Cursor will use
    """
    print("Testing Cursor MCP Command...")
    print("=" * 50)
    
    # Set up environment
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
    env["CEREBRAS_API_KEY"] = "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
    env["PYTHONPATH"] = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    # Change to the correct directory
    cwd = "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    
    # The exact command Cursor will use
    cmd = ["python", "-u", "run_mcp_stdio_clean.py"]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Working Directory: {cwd}")
    print(f"Environment: GEMINI_API_KEY and CEREBRAS_API_KEY set")
    print()
    
    try:
        # Start the server
        print("Starting MCP server...")
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
        
        # Send a simple test request
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        print("Sending test request...")
        request_json = json.dumps(test_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        print("Waiting for response...")
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server is running and responsive")
            print("✅ MCP server should work with Cursor")
        else:
            print("❌ Server process ended unexpectedly")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
        
        # Clean up
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False
    
    print("\nTest complete!")
    return True

if __name__ == "__main__":
    test_cursor_command()
