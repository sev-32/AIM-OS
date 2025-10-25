#!/usr/bin/env python3
"""
Minimal stdio test - just test the protocol without full agent
"""
import subprocess
import json
import time
import sys

def test_minimal():
    """Test minimal stdio communication"""
    print("=" * 60)
    print("MINIMAL STDIO TEST")
    print("=" * 60)
    
    # Create a minimal server that just echoes
    minimal_server = '''
import sys
import json

print("Minimal server starting...", file=sys.stderr)
while True:
    line = sys.stdin.readline()
    if not line:
        break
    try:
        request = json.loads(line.strip())
        response = {"echo": request, "status": "ok"}
        print(json.dumps(response), flush=True)
    except Exception as e:
        error = {"error": str(e)}
        print(json.dumps(error), flush=True)
'''
    
    # Write minimal server
    with open("minimal_server.py", "w") as f:
        f.write(minimal_server)
    
    print("\n[1] Testing minimal echo server...")
    proc = subprocess.Popen(
        [sys.executable, "-u", "minimal_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    time.sleep(1)
    
    if proc.poll() is not None:
        print("    [FAIL] Minimal server died!")
        return False
    
    print("    [OK] Minimal server running")
    
    # Test echo
    test_msg = {"test": "hello", "id": 1}
    print(f"\n[2] Sending: {test_msg}")
    
    proc.stdin.write(json.dumps(test_msg) + '\n')
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    if response_line:
        response = json.loads(response_line)
        print(f"    Received: {response}")
        if response.get("echo") == test_msg:
            print("    [OK] Echo test passed!")
        else:
            print("    [FAIL] Echo mismatch")
    else:
        print("    [FAIL] No response")
    
    # Cleanup
    proc.terminate()
    proc.wait()
    
    print("\n" + "=" * 60)
    print("MINIMAL TEST COMPLETE")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_minimal()
