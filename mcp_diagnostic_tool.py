#!/usr/bin/env python3
"""
MCP Diagnostic Tool - Standalone version for quick debugging
"""

import json
import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

def run_mcp_diagnostic():
    """Run comprehensive MCP diagnostic"""
    print("🔍 MCP Diagnostic Tool Starting...")
    print("=" * 60)
    
    results = []
    start_time = time.time()
    
    # Test 1: Environment
    print("🌍 Testing Environment...")
    results.append(test_python_version())
    results.append(test_required_packages())
    results.append(test_environment_variables())
    
    # Test 2: Configuration
    print("⚙️ Testing Configuration...")
    config_path = find_cursor_config()
    results.append(test_config_file_exists(config_path))
    results.append(test_config_file_valid_json(config_path))
    results.append(test_config_file_structure(config_path))
    results.append(test_config_file_paths(config_path))
    
    # Test 3: Server
    print("🚀 Testing Server...")
    results.append(test_server_file_exists(config_path))
    results.append(test_server_can_start(config_path))
    results.append(test_server_responds(config_path))
    results.append(test_server_tools_list(config_path))
    
    # Test 4: Protocol
    print("📡 Testing Protocol...")
    results.append(test_jsonrpc_format(config_path))
    results.append(test_mcp_protocol_compliance(config_path))
    results.append(test_tool_calling(config_path))
    
    # Display results
    display_results(results, start_time)
    
    # Save report
    save_report(results, start_time)

def find_cursor_config():
    """Find Cursor MCP configuration file"""
    possible_paths = [
        os.path.expanduser("~/.cursor/mcp.json"),
        os.path.expanduser("~/AppData/Roaming/Cursor/mcp.json"),
        os.path.expanduser("~/AppData/Local/Cursor/mcp.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return possible_paths[0]  # Default to first path

def test_python_version():
    """Test Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return {
            "test": "python_version",
            "status": "PASS",
            "message": f"Python {version.major}.{version.minor}.{version.micro} is compatible"
        }
    else:
        return {
            "test": "python_version",
            "status": "FAIL",
            "message": f"Python {version.major}.{version.minor}.{version.micro} is not compatible (need 3.8+)"
        }

def test_required_packages():
    """Test required packages"""
    required_packages = ["json", "subprocess", "pathlib"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        return {
            "test": "required_packages",
            "status": "PASS",
            "message": "All required packages are available"
        }
    else:
        return {
            "test": "required_packages",
            "status": "FAIL",
            "message": f"Missing packages: {', '.join(missing_packages)}"
        }

def test_environment_variables():
    """Test environment variables"""
    required_vars = ["GEMINI_API_KEY", "CEREBRAS_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        return {
            "test": "environment_variables",
            "status": "PASS",
            "message": "All required environment variables are set"
        }
    else:
        return {
            "test": "environment_variables",
            "status": "WARN",
            "message": f"Missing environment variables: {', '.join(missing_vars)}"
        }

def test_config_file_exists(config_path):
    """Test if config file exists"""
    if os.path.exists(config_path):
        return {
            "test": "config_file_exists",
            "status": "PASS",
            "message": f"Config file exists: {config_path}"
        }
    else:
        return {
            "test": "config_file_exists",
            "status": "FAIL",
            "message": f"Config file does not exist: {config_path}"
        }

def test_config_file_valid_json(config_path):
    """Test if config file is valid JSON"""
    try:
        with open(config_path, 'r') as f:
            json.load(f)
        return {
            "test": "config_file_valid_json",
            "status": "PASS",
            "message": "Config file is valid JSON"
        }
    except json.JSONDecodeError as e:
        return {
            "test": "config_file_valid_json",
            "status": "FAIL",
            "message": f"Config file is not valid JSON: {e}"
        }
    except Exception as e:
        return {
            "test": "config_file_valid_json",
            "status": "FAIL",
            "message": f"Error reading config file: {e}"
        }

def test_config_file_structure(config_path):
    """Test config file structure"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ["mcpServers"]
        missing_keys = [key for key in required_keys if key not in config]
        
        if not missing_keys:
            return {
                "test": "config_file_structure",
                "status": "PASS",
                "message": "Config file has required structure"
            }
        else:
            return {
                "test": "config_file_structure",
                "status": "FAIL",
                "message": f"Config file missing required keys: {', '.join(missing_keys)}"
            }
    except Exception as e:
        return {
            "test": "config_file_structure",
            "status": "FAIL",
            "message": f"Error checking config structure: {e}"
        }

def test_config_file_paths(config_path):
    """Test config file paths"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        path_issues = []
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            if cwd and not os.path.exists(cwd):
                path_issues.append(f"Working directory does not exist: {cwd}")
            
            args = server_config.get("args", [])
            if args and len(args) > 0:
                server_file = os.path.join(cwd or "", args[0])
                if not os.path.exists(server_file):
                    path_issues.append(f"Server file does not exist: {server_file}")
        
        if not path_issues:
            return {
                "test": "config_file_paths",
                "status": "PASS",
                "message": "All config file paths are valid"
            }
        else:
            return {
                "test": "config_file_paths",
                "status": "FAIL",
                "message": f"Path issues found: {'; '.join(path_issues)}"
            }
    except Exception as e:
        return {
            "test": "config_file_paths",
            "status": "FAIL",
            "message": f"Error checking config paths: {e}"
        }

def test_server_file_exists(config_path):
    """Test if server file exists"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            if args and len(args) > 0:
                server_file = os.path.join(cwd or "", args[0])
                if os.path.exists(server_file):
                    return {
                        "test": "server_file_exists",
                        "status": "PASS",
                        "message": f"Server file exists: {server_file}"
                    }
        
        return {
            "test": "server_file_exists",
            "status": "FAIL",
            "message": "No server file found in configuration"
        }
    except Exception as e:
        return {
            "test": "server_file_exists",
            "status": "FAIL",
            "message": f"Error checking server file: {e}"
        }

def test_server_can_start(config_path):
    """Test if server can start"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
                if process.poll() is None:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "server_can_start",
                        "status": "PASS",
                        "message": f"Server can start successfully: {server_name}"
                    }
                else:
                    stdout, stderr = process.communicate()
                    return {
                        "test": "server_can_start",
                        "status": "FAIL",
                        "message": f"Server failed to start: {server_name}",
                        "details": {"stderr": stderr, "stdout": stdout}
                    }
        
        return {
            "test": "server_can_start",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "server_can_start",
            "status": "FAIL",
            "message": f"Error testing server startup: {e}"
        }

def test_server_responds(config_path):
    """Test if server responds to requests"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
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
                    process.terminate()
                    process.wait()
                    
                    if "tools" in response:
                        return {
                            "test": "server_responds",
                            "status": "PASS",
                            "message": f"Server responds correctly: {server_name}"
                        }
                    else:
                        return {
                            "test": "server_responds",
                            "status": "FAIL",
                            "message": f"Server response invalid: {server_name}"
                        }
                else:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "server_responds",
                        "status": "FAIL",
                        "message": f"Server no response: {server_name}"
                    }
        
        return {
            "test": "server_responds",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "server_responds",
            "status": "FAIL",
            "message": f"Error testing server response: {e}"
        }

def test_server_tools_list(config_path):
    """Test if server tools list works"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
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
                    process.terminate()
                    process.wait()
                    
                    if "tools" in response and len(response["tools"]) > 0:
                        return {
                            "test": "server_tools_list",
                            "status": "PASS",
                            "message": f"Server tools list works: {server_name}",
                            "details": {"tools": response["tools"]}
                        }
                    else:
                        return {
                            "test": "server_tools_list",
                            "status": "FAIL",
                            "message": f"Server tools list empty: {server_name}"
                        }
                else:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "server_tools_list",
                        "status": "FAIL",
                        "message": f"Server tools list no response: {server_name}"
                    }
        
        return {
            "test": "server_tools_list",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "server_tools_list",
            "status": "FAIL",
            "message": f"Error testing server tools list: {e}"
        }

def test_jsonrpc_format(config_path):
    """Test JSON-RPC format"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
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
                    process.terminate()
                    process.wait()
                    
                    if "jsonrpc" in response and response["jsonrpc"] == "2.0":
                        return {
                            "test": "jsonrpc_format",
                            "status": "PASS",
                            "message": f"JSON-RPC format correct: {server_name}"
                        }
                    else:
                        return {
                            "test": "jsonrpc_format",
                            "status": "FAIL",
                            "message": f"JSON-RPC format incorrect: {server_name}"
                        }
                else:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "jsonrpc_format",
                        "status": "FAIL",
                        "message": f"JSON-RPC no response: {server_name}"
                    }
        
        return {
            "test": "jsonrpc_format",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "jsonrpc_format",
            "status": "FAIL",
            "message": f"Error testing JSON-RPC format: {e}"
        }

def test_mcp_protocol_compliance(config_path):
    """Test MCP protocol compliance"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
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
                    process.terminate()
                    process.wait()
                    
                    if "tools" in response and isinstance(response["tools"], list):
                        return {
                            "test": "mcp_protocol_compliance",
                            "status": "PASS",
                            "message": f"MCP protocol compliance correct: {server_name}"
                        }
                    else:
                        return {
                            "test": "mcp_protocol_compliance",
                            "status": "FAIL",
                            "message": f"MCP protocol compliance incorrect: {server_name}"
                        }
                else:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "mcp_protocol_compliance",
                        "status": "FAIL",
                        "message": f"MCP protocol no response: {server_name}"
                    }
        
        return {
            "test": "mcp_protocol_compliance",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "mcp_protocol_compliance",
            "status": "FAIL",
            "message": f"Error testing MCP protocol compliance: {e}"
        }

def test_tool_calling(config_path):
    """Test tool calling functionality"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        for server_name, server_config in config.get("mcpServers", {}).items():
            cwd = server_config.get("cwd")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            if args and len(args) > 0:
                server_file = args[0]
                command = ["python", "-u", server_file]
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env={**os.environ, **env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                time.sleep(2)
                
                test_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "test_connection",
                        "arguments": {"message": "test"}
                    }
                }
                
                request_json = json.dumps(test_request) + "\n"
                process.stdin.write(request_json)
                process.stdin.flush()
                
                time.sleep(2)
                
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    process.terminate()
                    process.wait()
                    
                    if "content" in response:
                        return {
                            "test": "tool_calling",
                            "status": "PASS",
                            "message": f"Tool calling works: {server_name}"
                        }
                    else:
                        return {
                            "test": "tool_calling",
                            "status": "FAIL",
                            "message": f"Tool calling failed: {server_name}"
                        }
                else:
                    process.terminate()
                    process.wait()
                    return {
                        "test": "tool_calling",
                        "status": "FAIL",
                        "message": f"Tool calling no response: {server_name}"
                    }
        
        return {
            "test": "tool_calling",
            "status": "FAIL",
            "message": "No server configuration found"
        }
    except Exception as e:
        return {
            "test": "tool_calling",
            "status": "FAIL",
            "message": f"Error testing tool calling: {e}"
        }

def display_results(results, start_time):
    """Display diagnostic results"""
    print("\n" + "=" * 60)
    print("📊 MCP DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    passed = len([r for r in results if r["status"] == "PASS"])
    failed = len([r for r in results if r["status"] == "FAIL"])
    warnings = len([r for r in results if r["status"] == "WARN"])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    
    print(f"\n📋 Test Details:")
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
        print(f"  {status_icon} {result['test']}: {result['message']}")
    
    if failed > 0:
        print(f"\n🚨 Failed Tests:")
        for result in results:
            if result["status"] == "FAIL":
                print(f"  ❌ {result['test']}: {result['message']}")
    
    if warnings > 0:
        print(f"\n⚠️ Warnings:")
        for result in results:
            if result["status"] == "WARN":
                print(f"  ⚠️ {result['test']}: {result['message']}")
    
    print(f"\n⏱️ Total Time: {(time.time() - start_time):.2f} seconds")
    print("=" * 60)

def save_report(results, start_time):
    """Save diagnostic report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mcp_diagnostic_report_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "results": results,
        "summary": {
            "total_tests": len(results),
            "passed": len([r for r in results if r["status"] == "PASS"]),
            "failed": len([r for r in results if r["status"] == "FAIL"]),
            "warnings": len([r for r in results if r["status"] == "WARN"]),
            "duration_seconds": time.time() - start_time
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"📄 Diagnostic report saved to: {filename}")

if __name__ == "__main__":
    run_mcp_diagnostic()

