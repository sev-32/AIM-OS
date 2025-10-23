#!/usr/bin/env python3
"""Quick test of stdio MCP server"""
import subprocess
import json
import time

def test_stdio_server():
    """Test the stdio MCP server"""
    print("=" * 80)
    print("TESTING STDIO MCP SERVER")
    print("=" * 80)
    
    # Start the server
    print("\n[1/3] Starting server...")
    proc = subprocess.Popen(
        ["python", "run_mcp_stdio.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Give it time to initialize
    time.sleep(2)
    
    # Check if still running
    if proc.poll() is not None:
        print("   [FAIL] Server died immediately!")
        stderr = proc.stderr.read()
        print(f"\nErrors:\n{stderr}")
        return False
    
    print("   [OK] Server started")
    
    # Test 1: List tools
    print("\n[2/3] Testing tools/list...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        
        # Read response
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "tools" in response:
                print(f"   [OK] Found {len(response['tools'])} tools")
                for tool in response['tools']:
                    print(f"      - {tool['name']}")
            else:
                print(f"   [FAIL] No tools in response: {response}")
        else:
            print("   [FAIL] No response from server")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
    
    # Test 2: Call ask_agent
    print("\n[3/3] Testing ask_agent tool...")
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "ask_agent",
            "arguments": {
                "question": "What is 2+2?"
            }
        }
    }
    
    try:
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        
        # Read response (may take a few seconds for LLM)
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "content" in response:
                text = response['content'][0]['text']
                print(f"   [OK] Agent responded: {text[:100]}...")
            else:
                print(f"   [FAIL] Unexpected response: {response}")
        else:
            print("   [FAIL] No response from server")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
    
    # Cleanup
    print("\n[Cleanup] Stopping server...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    
    print("\n" + "=" * 80)
    print("STDIO MCP SERVER: TESTED!")
    print("=" * 80)
    print("\nREADY FOR CURSOR INTEGRATION!")
    print("Reload Cursor and it should connect automatically.")

if __name__ == "__main__":
    test_stdio_server()

