#!/usr/bin/env python3
import subprocess
import json
import time

# Start the server
print("Starting run_mcp_cross_model.py...")
process = subprocess.Popen(
    ["python", "-u", "run_mcp_cross_model.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=0
)

time.sleep(3)

# Send tools/list request
print("Requesting tools list...")
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}

process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

time.sleep(2)

# Read response
response = process.stdout.readline()
print(f"Response: {response}")

if response:
    data = json.loads(response)
    if "result" in data and "tools" in data["result"]:
        tools = data["result"]["tools"]
        print(f"\n✅ Found {len(tools)} tools:")
        for i, tool in enumerate(tools[:6], 1):
            print(f"{i}. {tool['name']}")
        
        if len(tools) > 6:
            print(f"\n... and {len(tools) - 6} more tools")
    else:
        print(f"❌ No tools found. Response: {data}")

process.terminate()
process.wait()

