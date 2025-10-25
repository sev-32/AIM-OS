#!/usr/bin/env python3
"""
MCP Diagnostic Framework - Comprehensive debugging system for MCP issues
"""

import json
import subprocess
import sys
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import psutil

@dataclass
class DiagnosticResult:
    """Result of a diagnostic test"""
    test_name: str
    status: str  # "PASS", "FAIL", "WARN", "SKIP"
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration_ms: float

@dataclass
class MCPDiagnosticReport:
    """Complete diagnostic report"""
    timestamp: datetime
    cursor_version: Optional[str]
    python_version: str
    platform: str
    config_file_path: str
    config_valid: bool
    config_content: Dict[str, Any]
    server_tests: List[DiagnosticResult]
    environment_tests: List[DiagnosticResult]
    connectivity_tests: List[DiagnosticResult]
    protocol_tests: List[DiagnosticResult]
    overall_status: str
    recommendations: List[str]

class MCPDiagnosticFramework:
    """Comprehensive MCP debugging framework"""
    
    def __init__(self, config_file_path: str = None):
        """Initialize the diagnostic framework"""
        self.config_file_path = config_file_path or self._find_cursor_config()
        self.results: List[DiagnosticResult] = []
        self.start_time = time.time()
        
    def _find_cursor_config(self) -> str:
        """Find the Cursor MCP configuration file"""
        possible_paths = [
            os.path.expanduser("~/.cursor/mcp.json"),
            os.path.expanduser("~/AppData/Roaming/Cursor/mcp.json"),
            os.path.expanduser("~/AppData/Local/Cursor/mcp.json"),
            os.path.expanduser("~/.cursor/mcp.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return possible_paths[0]  # Default to first path
    
    def run_complete_diagnostic(self) -> MCPDiagnosticReport:
        """Run complete diagnostic suite"""
        print("🔍 MCP Diagnostic Framework Starting...")
        print("=" * 60)
        
        # Run all diagnostic tests
        self._test_environment()
        self._test_configuration()
        self._test_server_startup()
        self._test_protocol_communication()
        self._test_cursor_integration()
        
        # Generate report
        report = self._generate_report()
        
        # Display results
        self._display_results(report)
        
        return report
    
    def _test_environment(self):
        """Test environment setup"""
        print("🌍 Testing Environment...")
        
        # Test Python version
        self._run_test(
            "python_version",
            self._check_python_version,
            "Check Python version compatibility"
        )
        
        # Test required packages
        self._run_test(
            "required_packages",
            self._check_required_packages,
            "Check required Python packages"
        )
        
        # Test environment variables
        self._run_test(
            "environment_variables",
            self._check_environment_variables,
            "Check environment variables"
        )
        
        # Test file permissions
        self._run_test(
            "file_permissions",
            self._check_file_permissions,
            "Check file permissions"
        )
    
    def _test_configuration(self):
        """Test configuration file"""
        print("⚙️ Testing Configuration...")
        
        # Test config file exists
        self._run_test(
            "config_file_exists",
            self._check_config_file_exists,
            "Check if MCP config file exists"
        )
        
        # Test config file valid JSON
        self._run_test(
            "config_file_valid_json",
            self._check_config_file_valid_json,
            "Check if config file is valid JSON"
        )
        
        # Test config file structure
        self._run_test(
            "config_file_structure",
            self._check_config_file_structure,
            "Check config file structure"
        )
        
        # Test config file paths
        self._run_test(
            "config_file_paths",
            self._check_config_file_paths,
            "Check config file paths"
        )
    
    def _test_server_startup(self):
        """Test server startup"""
        print("🚀 Testing Server Startup...")
        
        # Test server file exists
        self._run_test(
            "server_file_exists",
            self._check_server_file_exists,
            "Check if server file exists"
        )
        
        # Test server can start
        self._run_test(
            "server_can_start",
            self._check_server_can_start,
            "Check if server can start"
        )
        
        # Test server responds to requests
        self._run_test(
            "server_responds",
            self._check_server_responds,
            "Check if server responds to requests"
        )
        
        # Test server tools list
        self._run_test(
            "server_tools_list",
            self._check_server_tools_list,
            "Check if server tools list works"
        )
    
    def _test_protocol_communication(self):
        """Test MCP protocol communication"""
        print("📡 Testing Protocol Communication...")
        
        # Test JSON-RPC format
        self._run_test(
            "jsonrpc_format",
            self._check_jsonrpc_format,
            "Check JSON-RPC format"
        )
        
        # Test MCP protocol compliance
        self._run_test(
            "mcp_protocol_compliance",
            self._check_mcp_protocol_compliance,
            "Check MCP protocol compliance"
        )
        
        # Test tool calling
        self._run_test(
            "tool_calling",
            self._check_tool_calling,
            "Check tool calling functionality"
        )
    
    def _test_cursor_integration(self):
        """Test Cursor integration"""
        print("🎯 Testing Cursor Integration...")
        
        # Test Cursor version
        self._run_test(
            "cursor_version",
            self._check_cursor_version,
            "Check Cursor version"
        )
        
        # Test Cursor MCP support
        self._run_test(
            "cursor_mcp_support",
            self._check_cursor_mcp_support,
            "Check Cursor MCP support"
        )
        
        # Test Cursor configuration loading
        self._run_test(
            "cursor_config_loading",
            self._check_cursor_config_loading,
            "Check Cursor configuration loading"
        )
    
    def _run_test(self, test_name: str, test_func, description: str):
        """Run a single test"""
        start_time = time.time()
        try:
            result = test_func()
            duration = (time.time() - start_time) * 1000
            
            if result["status"] == "PASS":
                print(f"  ✅ {test_name}: {result['message']}")
            elif result["status"] == "FAIL":
                print(f"  ❌ {test_name}: {result['message']}")
            elif result["status"] == "WARN":
                print(f"  ⚠️ {test_name}: {result['message']}")
            else:
                print(f"  ⏭️ {test_name}: {result['message']}")
            
            self.results.append(DiagnosticResult(
                test_name=test_name,
                status=result["status"],
                message=result["message"],
                details=result.get("details", {}),
                timestamp=datetime.now(),
                duration_ms=duration
            ))
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f"  💥 {test_name}: Error - {e}")
            self.results.append(DiagnosticResult(
                test_name=test_name,
                status="FAIL",
                message=f"Error: {e}",
                details={"error": str(e), "traceback": traceback.format_exc()},
                timestamp=datetime.now(),
                duration_ms=duration
            ))
    
    def _check_python_version(self) -> Dict[str, Any]:
        """Check Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            return {
                "status": "PASS",
                "message": f"Python {version.major}.{version.minor}.{version.micro} is compatible",
                "details": {"version": f"{version.major}.{version.minor}.{version.micro}"}
            }
        else:
            return {
                "status": "FAIL",
                "message": f"Python {version.major}.{version.minor}.{version.micro} is not compatible (need 3.8+)",
                "details": {"version": f"{version.major}.{version.minor}.{version.micro}"}
            }
    
    def _check_required_packages(self) -> Dict[str, Any]:
        """Check required packages"""
        required_packages = ["json", "subprocess", "pathlib", "psutil"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            return {
                "status": "PASS",
                "message": "All required packages are available",
                "details": {"packages": required_packages}
            }
        else:
            return {
                "status": "FAIL",
                "message": f"Missing packages: {', '.join(missing_packages)}",
                "details": {"missing": missing_packages}
            }
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """Check environment variables"""
        required_vars = ["GEMINI_API_KEY", "CEREBRAS_API_KEY"]
        missing_vars = []
        present_vars = []
        
        for var in required_vars:
            if os.getenv(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)
        
        if not missing_vars:
            return {
                "status": "PASS",
                "message": "All required environment variables are set",
                "details": {"variables": present_vars}
            }
        else:
            return {
                "status": "WARN",
                "message": f"Missing environment variables: {', '.join(missing_vars)}",
                "details": {"missing": missing_vars, "present": present_vars}
            }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions"""
        config_dir = os.path.dirname(self.config_file_path)
        
        if os.path.exists(config_dir):
            if os.access(config_dir, os.R_OK):
                return {
                    "status": "PASS",
                    "message": "Configuration directory is readable",
                    "details": {"directory": config_dir}
                }
            else:
                return {
                    "status": "FAIL",
                    "message": "Configuration directory is not readable",
                    "details": {"directory": config_dir}
                }
        else:
            return {
                "status": "FAIL",
                "message": "Configuration directory does not exist",
                "details": {"directory": config_dir}
            }
    
    def _check_config_file_exists(self) -> Dict[str, Any]:
        """Check if config file exists"""
        if os.path.exists(self.config_file_path):
            return {
                "status": "PASS",
                "message": f"Config file exists: {self.config_file_path}",
                "details": {"path": self.config_file_path}
            }
        else:
            return {
                "status": "FAIL",
                "message": f"Config file does not exist: {self.config_file_path}",
                "details": {"path": self.config_file_path}
            }
    
    def _check_config_file_valid_json(self) -> Dict[str, Any]:
        """Check if config file is valid JSON"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            return {
                "status": "PASS",
                "message": "Config file is valid JSON",
                "details": {"config": config}
            }
        except json.JSONDecodeError as e:
            return {
                "status": "FAIL",
                "message": f"Config file is not valid JSON: {e}",
                "details": {"error": str(e)}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error reading config file: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_config_file_structure(self) -> Dict[str, Any]:
        """Check config file structure"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            required_keys = ["mcpServers"]
            missing_keys = [key for key in required_keys if key not in config]
            
            if not missing_keys:
                return {
                    "status": "PASS",
                    "message": "Config file has required structure",
                    "details": {"structure": config}
                }
            else:
                return {
                    "status": "FAIL",
                    "message": f"Config file missing required keys: {', '.join(missing_keys)}",
                    "details": {"missing": missing_keys, "config": config}
                }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error checking config structure: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_config_file_paths(self) -> Dict[str, Any]:
        """Check config file paths"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            path_issues = []
            for server_name, server_config in config.get("mcpServers", {}).items():
                # Check working directory
                cwd = server_config.get("cwd")
                if cwd and not os.path.exists(cwd):
                    path_issues.append(f"Working directory does not exist: {cwd}")
                
                # Check server file
                args = server_config.get("args", [])
                if args and len(args) > 0:
                    server_file = os.path.join(cwd or "", args[0])
                    if not os.path.exists(server_file):
                        path_issues.append(f"Server file does not exist: {server_file}")
            
            if not path_issues:
                return {
                    "status": "PASS",
                    "message": "All config file paths are valid",
                    "details": {"paths": "All valid"}
                }
            else:
                return {
                    "status": "FAIL",
                    "message": f"Path issues found: {'; '.join(path_issues)}",
                    "details": {"issues": path_issues}
                }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error checking config paths: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_server_file_exists(self) -> Dict[str, Any]:
        """Check if server file exists"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                if args and len(args) > 0:
                    server_file = os.path.join(cwd or "", args[0])
                    if os.path.exists(server_file):
                        return {
                            "status": "PASS",
                            "message": f"Server file exists: {server_file}",
                            "details": {"file": server_file}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server file found in configuration",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error checking server file: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_server_can_start(self) -> Dict[str, Any]:
        """Check if server can start"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait a bit for startup
                    time.sleep(2)
                    
                    # Check if process is still running
                    if process.poll() is None:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "PASS",
                            "message": f"Server can start successfully: {server_name}",
                            "details": {"server": server_name, "command": command}
                        }
                    else:
                        stdout, stderr = process.communicate()
                        return {
                            "status": "FAIL",
                            "message": f"Server failed to start: {server_name}",
                            "details": {"server": server_name, "stderr": stderr, "stdout": stdout}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing server startup: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_server_responds(self) -> Dict[str, Any]:
        """Check if server responds to requests"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait for startup
                    time.sleep(2)
                    
                    # Send test request
                    test_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    request_json = json.dumps(test_request) + "\n"
                    process.stdin.write(request_json)
                    process.stdin.flush()
                    
                    # Wait for response
                    time.sleep(2)
                    
                    # Check response
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        process.terminate()
                        process.wait()
                        
                        if "tools" in response:
                            return {
                                "status": "PASS",
                                "message": f"Server responds correctly: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": f"Server response invalid: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                    else:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "FAIL",
                            "message": f"Server no response: {server_name}",
                            "details": {"server": server_name}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing server response: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_server_tools_list(self) -> Dict[str, Any]:
        """Check if server tools list works"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait for startup
                    time.sleep(2)
                    
                    # Send tools/list request
                    test_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    request_json = json.dumps(test_request) + "\n"
                    process.stdin.write(request_json)
                    process.stdin.flush()
                    
                    # Wait for response
                    time.sleep(2)
                    
                    # Check response
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        process.terminate()
                        process.wait()
                        
                        if "tools" in response and len(response["tools"]) > 0:
                            return {
                                "status": "PASS",
                                "message": f"Server tools list works: {server_name}",
                                "details": {"server": server_name, "tools": response["tools"]}
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": f"Server tools list empty: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                    else:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "FAIL",
                            "message": f"Server tools list no response: {server_name}",
                            "details": {"server": server_name}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing server tools list: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_jsonrpc_format(self) -> Dict[str, Any]:
        """Check JSON-RPC format"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait for startup
                    time.sleep(2)
                    
                    # Send JSON-RPC request
                    test_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    request_json = json.dumps(test_request) + "\n"
                    process.stdin.write(request_json)
                    process.stdin.flush()
                    
                    # Wait for response
                    time.sleep(2)
                    
                    # Check response
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        process.terminate()
                        process.wait()
                        
                        if "jsonrpc" in response and response["jsonrpc"] == "2.0":
                            return {
                                "status": "PASS",
                                "message": f"JSON-RPC format correct: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": f"JSON-RPC format incorrect: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                    else:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "FAIL",
                            "message": f"JSON-RPC no response: {server_name}",
                            "details": {"server": server_name}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing JSON-RPC format: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_mcp_protocol_compliance(self) -> Dict[str, Any]:
        """Check MCP protocol compliance"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait for startup
                    time.sleep(2)
                    
                    # Send MCP request
                    test_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    request_json = json.dumps(test_request) + "\n"
                    process.stdin.write(request_json)
                    process.stdin.flush()
                    
                    # Wait for response
                    time.sleep(2)
                    
                    # Check response
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        process.terminate()
                        process.wait()
                        
                        if "tools" in response and isinstance(response["tools"], list):
                            return {
                                "status": "PASS",
                                "message": f"MCP protocol compliance correct: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": f"MCP protocol compliance incorrect: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                    else:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "FAIL",
                            "message": f"MCP protocol no response: {server_name}",
                            "details": {"server": server_name}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing MCP protocol compliance: {e}",
                "message": f"Error testing MCP protocol compliance: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_tool_calling(self) -> Dict[str, Any]:
        """Check tool calling functionality"""
        try:
            with open(self.config_file_path, 'r') as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("mcpServers", {}).items():
                cwd = server_config.get("cwd")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                if args and len(args) > 0:
                    server_file = args[0]
                    command = ["python", "-u", server_file]
                    
                    # Start server process
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
                    
                    # Wait for startup
                    time.sleep(2)
                    
                    # Send tool call request
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
                    
                    # Wait for response
                    time.sleep(2)
                    
                    # Check response
                    response_line = process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        process.terminate()
                        process.wait()
                        
                        if "content" in response:
                            return {
                                "status": "PASS",
                                "message": f"Tool calling works: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": f"Tool calling failed: {server_name}",
                                "details": {"server": server_name, "response": response}
                            }
                    else:
                        process.terminate()
                        process.wait()
                        return {
                            "status": "FAIL",
                            "message": f"Tool calling no response: {server_name}",
                            "details": {"server": server_name}
                        }
            
            return {
                "status": "FAIL",
                "message": "No server configuration found",
                "details": {"config": config}
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Error testing tool calling: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_cursor_version(self) -> Dict[str, Any]:
        """Check Cursor version"""
        try:
            # Try to find Cursor executable
            cursor_paths = [
                "cursor",
                "cursor.exe",
                "C:\\Users\\bombe\\AppData\\Local\\Programs\\cursor\\Cursor.exe",
                "C:\\Program Files\\Cursor\\Cursor.exe"
            ]
            
            for path in cursor_paths:
                try:
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        return {
                            "status": "PASS",
                            "message": f"Cursor version found: {version}",
                            "details": {"version": version, "path": path}
                        }
                except:
                    continue
            
            return {
                "status": "WARN",
                "message": "Cursor version not found",
                "details": {"paths_checked": cursor_paths}
            }
        except Exception as e:
            return {
                "status": "WARN",
                "message": f"Error checking Cursor version: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_cursor_mcp_support(self) -> Dict[str, Any]:
        """Check Cursor MCP support"""
        # This is a placeholder - we can't easily detect MCP support
        return {
            "status": "WARN",
            "message": "Cannot determine Cursor MCP support automatically",
            "details": {"note": "Check Cursor documentation for MCP support"}
        }
    
    def _check_cursor_config_loading(self) -> Dict[str, Any]:
        """Check Cursor configuration loading"""
        # This is a placeholder - we can't easily test if Cursor loads our config
        return {
            "status": "WARN",
            "message": "Cannot test Cursor configuration loading automatically",
            "details": {"note": "Check Cursor MCP panel for server status"}
        }
    
    def _generate_report(self) -> MCPDiagnosticReport:
        """Generate comprehensive diagnostic report"""
        config_content = {}
        config_valid = False
        
        try:
            with open(self.config_file_path, 'r') as f:
                config_content = json.load(f)
            config_valid = True
        except:
            pass
        
        # Categorize results
        server_tests = [r for r in self.results if "server" in r.test_name]
        environment_tests = [r for r in self.results if r.test_name in ["python_version", "required_packages", "environment_variables", "file_permissions"]]
        connectivity_tests = [r for r in self.results if "responds" in r.test_name or "communication" in r.test_name]
        protocol_tests = [r for r in self.results if "jsonrpc" in r.test_name or "protocol" in r.test_name or "tool" in r.test_name]
        
        # Determine overall status
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        if failed_tests:
            overall_status = "FAIL"
        else:
            warning_tests = [r for r in self.results if r.status == "WARN"]
            if warning_tests:
                overall_status = "WARN"
            else:
                overall_status = "PASS"
        
        # Generate recommendations
        recommendations = []
        if overall_status == "FAIL":
            recommendations.append("Fix failed tests before proceeding")
        if any(r.status == "WARN" for r in self.results):
            recommendations.append("Address warnings for optimal performance")
        if not config_valid:
            recommendations.append("Fix configuration file issues")
        if not any(r.status == "PASS" for r in server_tests):
            recommendations.append("Fix server startup issues")
        
        return MCPDiagnosticReport(
            timestamp=datetime.now(),
            cursor_version=None,  # We can't easily detect this
            python_version=sys.version,
            platform=sys.platform,
            config_file_path=self.config_file_path,
            config_valid=config_valid,
            config_content=config_content,
            server_tests=server_tests,
            environment_tests=environment_tests,
            connectivity_tests=connectivity_tests,
            protocol_tests=protocol_tests,
            overall_status=overall_status,
            recommendations=recommendations
        )
    
    def _display_results(self, report: MCPDiagnosticReport):
        """Display diagnostic results"""
        print("\n" + "=" * 60)
        print("📊 MCP DIAGNOSTIC RESULTS")
        print("=" * 60)
        
        print(f"Overall Status: {report.overall_status}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Python Version: {report.python_version}")
        print(f"Platform: {report.platform}")
        print(f"Config File: {report.config_file_path}")
        print(f"Config Valid: {report.config_valid}")
        
        print(f"\n📋 Test Summary:")
        print(f"  Total Tests: {len(self.results)}")
        print(f"  Passed: {len([r for r in self.results if r.status == 'PASS'])}")
        print(f"  Failed: {len([r for r in self.results if r.status == 'FAIL'])}")
        print(f"  Warnings: {len([r for r in self.results if r.status == 'WARN'])}")
        print(f"  Skipped: {len([r for r in self.results if r.status == 'SKIP'])}")
        
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n⏱️ Total Diagnostic Time: {(time.time() - self.start_time):.2f} seconds")
        print("=" * 60)
    
    def save_report(self, report: MCPDiagnosticReport, filename: str = None):
        """Save diagnostic report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_diagnostic_report_{timestamp}.json"
        
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "cursor_version": report.cursor_version,
            "python_version": report.python_version,
            "platform": report.platform,
            "config_file_path": report.config_file_path,
            "config_valid": report.config_valid,
            "config_content": report.config_content,
            "server_tests": [asdict(r) for r in report.server_tests],
            "environment_tests": [asdict(r) for r in report.environment_tests],
            "connectivity_tests": [asdict(r) for r in report.connectivity_tests],
            "protocol_tests": [asdict(r) for r in report.protocol_tests],
            "overall_status": report.overall_status,
            "recommendations": report.recommendations
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Diagnostic report saved to: {filename}")

if __name__ == "__main__":
    # Run diagnostic framework
    framework = MCPDiagnosticFramework()
    report = framework.run_complete_diagnostic()
    framework.save_report(report)

