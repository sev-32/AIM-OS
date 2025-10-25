#!/usr/bin/env python3
"""
Minimal MCP Server - No AI, No API Keys, No Backend Systems
Pure MCP protocol test to isolate Cursor integration issues
"""
import sys
import json
import os

class MinimalMCPNoAI:
    """Minimal MCP Server with no AI dependencies"""
    
    def __init__(self):
        """Initialize the minimal server"""
        def log(msg: str):
            print(f"[MCP-MINIMAL-NO-AI] {msg}", file=sys.stderr, flush=True)
        
        self.log = log
        self.log("Initializing Minimal MCP Server (No AI)...")
        self.log("Ready to receive MCP requests")
    
    def handle_request(self, request: dict) -> dict:
        """Handle an MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "tools/list":
                return self.list_tools()
            elif method == "tools/call":
                return self.call_tool(params)
            elif method == "resources/list":
                return {"resources": []}
            elif method == "prompts/list":
                return {"prompts": []}
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            self.log(f"Error handling {method}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def list_tools(self) -> dict:
        """List available MCP tools"""
        return {
            "tools": [
                {
                    "name": "echo",
                    "description": "Echo back the input message",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to echo back"
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "get_status",
                    "description": "Get server status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def call_tool(self, params: dict) -> dict:
        """Call a tool"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "echo":
            message = args.get("message", "Hello")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Echo: {message}"
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "get_status":
            status = {
                "server": "minimal-mcp-no-ai",
                "status": "running",
                "tools": 2,
                "ai_systems": 0,
                "api_keys": 0,
                "backend_systems": 0
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(status, indent=2)
                    }
                ],
                "isError": False
            }
        
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }
                ],
                "isError": True
            }
    
    def run(self):
        """Run the server loop (stdio)"""
        self.log("Starting stdio loop...")
        
        # Read from stdin line by line
        while True:
            try:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break
                    
                request = json.loads(line.strip())
                self.log(f"Received: {request.get('method')}")
                
                response = self.handle_request(request)
                
                # Add request ID if present
                if "id" in request:
                    response["id"] = request["id"]
                
                # Send response to stdout with explicit flush
                response_json = json.dumps(response)
                sys.stdout.write(response_json + '\n')
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON: {e}")
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
            except Exception as e:
                self.log(f"Error: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    try:
        server = MinimalMCPNoAI()
        server.run()
    except Exception as e:
        print(f"[MCP-MINIMAL-NO-AI] FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

