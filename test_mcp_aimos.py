#!/usr/bin/env python3
"""Test the AIM-OS MCP server"""
import subprocess
import json
import time

def test_server():
    """Test MCP server startup and basic functionality"""
    print("Testing AIM-OS MCP Server...")
    
    try:
        # Start server
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_aimos.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for initialization
        time.sleep(2)
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("SUCCESS: Initialize response:", json.dumps(response, indent=2))
        else:
            print("ERROR: No response received")
            # Check stderr for errors
            stderr_output = process.stderr.read()
            if stderr_output:
                print("STDERR:", stderr_output)
        
        # Send tools/list request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nSending tools/list request...")
        process.stdin.write(json.dumps(list_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print("SUCCESS: Tools list response:")
            if "tools" in response:
                for tool in response["tools"]:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print(json.dumps(response, indent=2))
        
        # Clean up
        process.terminate()
        process.wait(timeout=2)
        
        print("\nSUCCESS: Server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        if 'process' in locals():
            try:
                stderr = process.stderr.read()
                if stderr:
                    print("\nServer STDERR:")
                    print(stderr)
            except:
                pass
            process.terminate()
        return False

if __name__ == "__main__":
    test_server()
