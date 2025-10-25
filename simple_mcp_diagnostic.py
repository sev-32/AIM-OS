#!/usr/bin/env python3
"""
Simple MCP Diagnostic - Fast debugging for immediate issues
"""

import json
import subprocess
import sys
import os
import time

def simple_diagnostic():
    """Run simple MCP diagnostic"""
    print("MCP Diagnostic Tool")
    print("=" * 40)
    
    issues = []
    
    # Check 1: Config file exists
    config_path = os.path.expanduser("~/.cursor/mcp.json")
    if not os.path.exists(config_path):
        issues.append(f"Config file missing: {config_path}")
    else:
        print(f"Config file exists: {config_path}")
    
    # Check 2: Config file valid JSON
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("Config file is valid JSON")
            
            # Check 3: Config has mcpServers
            if "mcpServers" in config:
                print("Config has mcpServers section")
                
                # Check 4: Server file exists
                for server_name, server_config in config["mcpServers"].items():
                    cwd = server_config.get("cwd")
                    args = server_config.get("args", [])
                    if args and len(args) > 0:
                        # Skip the "-u" flag and get the actual server file
                        server_file = os.path.join(cwd or "", args[1] if len(args) > 1 else args[0])
                        if os.path.exists(server_file):
                            print(f"Server file exists: {server_file}")
                            
                            # Check 5: Server can start
                            print(f"Testing server startup: {server_name}")
                            try:
                                process = subprocess.Popen(
                                    ["python", "-u", args[0]],
                                    cwd=cwd,
                                    env={**os.environ, **server_config.get("env", {})},
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    bufsize=0
                                )
                                
                                time.sleep(2)
                                
                                if process.poll() is None:
                                    print(f"Server can start: {server_name}")
                                    
                                    # Check 6: Server responds
                                    test_request = {
                                        "jsonrpc": "2.0",
                                        "id": 1,
                                        "method": "tools/list",
                                        "params": {}
                                    }
                                    
                                    request_json = json.dumps(test_request) + "\n"
                                    process.stdin.write(request_json)
                                    process.stdin.flush()
                                    
                                    time.sleep(2)
                                    
                                    response_line = process.stdout.readline()
                                    if response_line:
                                        response = json.loads(response_line.strip())
                                        if "tools" in response:
                                            print(f"Server responds correctly: {server_name}")
                                            print(f"Found {len(response['tools'])} tools")
                                        else:
                                            issues.append(f"Server response invalid: {server_name}")
                                    else:
                                        issues.append(f"Server no response: {server_name}")
                                    
                                    process.terminate()
                                    process.wait()
                                else:
                                    stdout, stderr = process.communicate()
                                    issues.append(f"Server failed to start: {server_name}")
                                    if stderr:
                                        issues.append(f"Error: {stderr}")
                            except Exception as e:
                                issues.append(f"Server test error: {e}")
                        else:
                            issues.append(f"Server file missing: {server_file}")
                    else:
                        issues.append(f"No server args in config: {server_name}")
            else:
                issues.append("Config missing mcpServers section")
        except json.JSONDecodeError as e:
            issues.append(f"Config file not valid JSON: {e}")
        except Exception as e:
            issues.append(f"Error reading config: {e}")
    
    # Check 7: Environment variables
    required_vars = ["GEMINI_API_KEY", "CEREBRAS_API_KEY"]
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
    else:
        print("Environment variables set")
    
    # Display results
    print("\n" + "=" * 40)
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("ALL CHECKS PASSED!")
        print("MCP server should be working correctly.")
    
    print("=" * 40)
    
    # Recommendations
    if issues:
        print("\nRECOMMENDATIONS:")
        if any("Config file missing" in issue for issue in issues):
            print("  1. Create MCP configuration file")
        if any("Server file missing" in issue for issue in issues):
            print("  2. Check server file paths in configuration")
        if any("Server failed to start" in issue for issue in issues):
            print("  3. Check server file syntax and dependencies")
        if any("Missing environment variables" in issue for issue in issues):
            print("  4. Set required environment variables")
        if any("Server no response" in issue for issue in issues):
            print("  5. Check server implementation and protocol")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = simple_diagnostic()
    sys.exit(0 if success else 1)
