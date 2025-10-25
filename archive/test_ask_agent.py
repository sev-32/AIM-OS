#!/usr/bin/env python3
"""
Test the ask_agent tool specifically
"""
import subprocess
import json
import time
import sys

def test_ask_agent():
    """Test ask_agent tool"""
    print("=" * 60)
    print("ASK AGENT TEST")
    print("=" * 60)
    
    # Start server
    print("\n[1] Starting server...")
    proc = subprocess.Popen(
        [sys.executable, "-u", "run_mcp_stdio_clean.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    time.sleep(3)  # Give it time to initialize
    
    if proc.poll() is not None:
        print("    [FAIL] Server died!")
        return False
    
    print("    [OK] Server running")
    
    # Test ask_agent
    print("\n[2] Testing ask_agent...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "ask_agent",
            "arguments": {
                "question": "What is 2+2?",
                "context": "This is a simple math test"
            }
        }
    }
    
    try:
        request_line = json.dumps(request) + '\n'
        print(f"    Sending: {request_line.strip()}")
        proc.stdin.write(request_line)
        proc.stdin.flush()
        
        print("    Waiting for response (may take a few seconds)...")
        response_line = proc.stdout.readline()
        
        if response_line:
            print(f"    Received response!")
            response = json.loads(response_line)
            
            if "content" in response:
                content = response['content'][0]['text']
                print(f"    [OK] Agent responded: {content[:200]}...")
                
                # Check if it's a reasonable answer
                if "4" in content or "four" in content.lower():
                    print("    [OK] Answer appears correct!")
                else:
                    print("    [WARN] Answer might be unexpected")
            elif "error" in response:
                print(f"    [FAIL] Error: {response['error']}")
            else:
                print(f"    [WARN] Unexpected format: {response}")
        else:
            print("    [FAIL] No response")
            
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
    
    # Cleanup
    print("\n[3] Cleanup...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
        print("    [OK] Server stopped")
    except subprocess.TimeoutExpired:
        proc.kill()
        print("    [WARN] Had to kill server")
    
    print("\n" + "=" * 60)
    print("ASK AGENT TEST COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_ask_agent()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
