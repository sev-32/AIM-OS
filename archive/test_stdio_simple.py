#!/usr/bin/env python3
"""
Simple stdio MCP test - validates basic communication
"""
import subprocess
import json
import time
import sys

def test_stdio():
    """Test stdio MCP server communication"""
    print("=" * 70)
    print("STDIO MCP SERVER TEST")
    print("=" * 70)
    
    # Start server with unbuffered flag
    print("\n[1] Starting server (unbuffered mode)...")
    proc = subprocess.Popen(
        [sys.executable, "-u", "run_mcp_stdio_clean.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    print("    Waiting for initialization...")
    time.sleep(3)  # Give it time to initialize
    
    # Check if alive
    if proc.poll() is not None:
        print("    [FAIL] Server died!")
        stderr = proc.stderr.read()
        print(f"\n{stderr}")
        return False
    
    print("    [OK] Server running")
    
    # Test 1: List tools
    print("\n[2] Testing tools/list...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        # Send request
        request_line = json.dumps(request) + '\n'
        print(f"    Sending: {request_line.strip()}")
        proc.stdin.write(request_line)
        proc.stdin.flush()
        
        # Wait for response
        print("    Waiting for response...")
        response_line = proc.stdout.readline()
        
        if response_line:
            print(f"    Received: {response_line.strip()[:100]}...")
            response = json.loads(response_line)
            
            if "tools" in response:
                print(f"    [OK] Found {len(response['tools'])} tools:")
                for tool in response['tools']:
                    print(f"         - {tool['name']}")
            elif "error" in response:
                print(f"    [FAIL] Error response: {response['error']}")
            else:
                print(f"    [WARN] Unexpected response format")
        else:
            print("    [FAIL] No response (timeout/buffering issue)")
            
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Get stats (lightweight test)
    print("\n[3] Testing get_agent_stats (quick test)...")
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_agent_stats",
            "arguments": {}
        }
    }
    
    try:
        request_line = json.dumps(request) + '\n'
        print(f"    Sending: {request_line.strip()}")
        proc.stdin.write(request_line)
        proc.stdin.flush()
        
        print("    Waiting for response...")
        response_line = proc.stdout.readline()
        
        if response_line:
            print(f"    Received: {response_line.strip()[:100]}...")
            response = json.loads(response_line)
            
            if "content" in response:
                print(f"    [OK] Got stats response")
                content = response['content'][0]['text']
                print(f"    Stats: {content[:200]}")
            elif "error" in response:
                print(f"    [FAIL] Error: {response['error']}")
            else:
                print(f"    [WARN] Unexpected format")
        else:
            print("    [FAIL] No response")
            
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
    
    # Cleanup
    print("\n[4] Cleanup...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
        print("    [OK] Server stopped cleanly")
    except subprocess.TimeoutExpired:
        proc.kill()
        print("    [WARN] Had to kill server")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    # Check stderr for any issues
    stderr = proc.stderr.read()
    if stderr:
        print("\nServer logs (stderr):")
        print(stderr[:500])
    
    return True

if __name__ == "__main__":
    try:
        test_stdio()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

