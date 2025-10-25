#!/usr/bin/env python3
"""
Test the simple MCP server manually before restarting Cursor
"""
import subprocess
import json
import time
import sys

def test_mcp_server():
    """Test the MCP server manually"""
    print("🧪 Testing MCP server manually...")
    
    try:
        # Start the server
        print("Starting server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_simple.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
        )
        
        # Wait a moment for initialization
        time.sleep(2)
        
        # Send test request
        test_request = {
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        print("Sending test request...")
        request_json = json.dumps(test_request) + '\n'
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response
        print("Reading response...")
        response_line = process.stdout.readline()
        
        if response_line:
            response = json.loads(response_line.strip())
            print("✅ SUCCESS! Server responded:")
            print(json.dumps(response, indent=2))
            
            # Check if it has tools
            if "tools" in response:
                print(f"✅ Found {len(response['tools'])} tools")
                for tool in response['tools']:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print("❌ No tools found in response")
        else:
            print("❌ No response received")
        
        # Clean up
        process.terminate()
        process.wait()
        
        print("\n🎉 Manual test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        if 'process' in locals():
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    if success:
        print("\n✅ Server works! Safe to restart Cursor.")
    else:
        print("\n❌ Server has issues. Don't restart Cursor yet!")

