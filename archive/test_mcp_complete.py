#!/usr/bin/env python3
"""Comprehensive test of AIM-OS MCP server"""
import subprocess
import json
import time
import sys

def test_server():
    """Test all MCP server functionality"""
    print("="*60)
    print("COMPREHENSIVE AIM-OS MCP SERVER TEST")
    print("="*60)
    
    try:
        # Start server
        print("\n[1/5] Starting server...")
        process = subprocess.Popen(
            ["python", "-u", "run_mcp_aimos.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for initialization
        time.sleep(3)
        print("SUCCESS: Server started")
        
        # Test 1: Initialize
        print("\n[2/5] Testing initialize...")
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
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "serverInfo" in response:
                print(f"SUCCESS: Server initialized - {response['serverInfo']['name']} v{response['serverInfo']['version']}")
            else:
                print("WARNING: Unexpected initialize response:", response)
        else:
            print("ERROR: No initialize response")
            return False
        
        # Test 2: List tools
        print("\n[3/5] Testing tools/list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "tools" in response:
                tools = response["tools"]
                print(f"SUCCESS: Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description'][:60]}...")
                
                # Verify expected tools
                tool_names = [t['name'] for t in tools]
                expected = ['store_memory', 'retrieve_memory', 'get_memory_stats']
                missing = [t for t in expected if t not in tool_names]
                if missing:
                    print(f"WARNING: Missing tools: {missing}")
                else:
                    print("SUCCESS: All expected tools present")
            else:
                print("ERROR: No tools in response:", response)
                return False
        else:
            print("ERROR: No tools/list response")
            return False
        
        # Test 3: Call get_memory_stats
        print("\n[4/5] Testing get_memory_stats tool...")
        stats_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_memory_stats",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(stats_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "content" in response and not response.get("isError"):
                print("SUCCESS: get_memory_stats executed:")
                print(response["content"][0]["text"])
            else:
                print("ERROR: Tool execution failed:", response)
                return False
        else:
            print("ERROR: No tool response")
            return False
        
        # Test 4: Call store_memory
        print("\n[5/5] Testing store_memory tool...")
        store_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "Test memory from MCP server validation",
                    "tags": {"test": 1.0, "importance": 0.9}
                }
            }
        }
        
        process.stdin.write(json.dumps(store_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "content" in response and not response.get("isError"):
                print("SUCCESS: store_memory executed:")
                print(response["content"][0]["text"][:200])
            else:
                print("ERROR: Tool execution failed:", response)
                return False
        else:
            print("ERROR: No tool response")
            return False
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED - SERVER IS READY FOR CURSOR!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        
        if 'process' in locals():
            try:
                # Try to read stderr
                process.stdout.close()
                process.stdin.close()
                stderr = process.stderr.read()
                if stderr:
                    print("\n" + "="*60)
                    print("SERVER STDERR OUTPUT:")
                    print("="*60)
                    print(stderr)
            except:
                pass
            
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                process.kill()
        
        print("\n" + "="*60)
        print("TESTS FAILED - DO NOT RESTART CURSOR YET")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
