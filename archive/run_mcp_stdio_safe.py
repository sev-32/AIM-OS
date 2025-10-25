#!/usr/bin/env python3
"""
AIM-OS MCP Server - STDIO Mode for Cursor (Safe Version)
Communicates via stdin/stdout using MCP protocol
"""
import sys
import json
import os
from pathlib import Path
from contextlib import redirect_stdout
import io

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# CRITICAL: Redirect any stdout from libraries to stderr
class StdoutToStderr:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        # Write to stderr instead of stdout
        self.original_stderr.write(text)
        self.original_stderr.flush()
        
    def flush(self):
        self.original_stderr.flush()
        
    def __getattr__(self, name):
        return getattr(self.original_stdout, name)

# Redirect stdout to stderr for library imports
sys.stdout = StdoutToStderr()

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

class SafeMCPServer:
    """MCP Server using stdio for Cursor integration - Safe initialization"""
    
    def __init__(self):
        """Initialize the server safely"""
        def log(msg: str):
            print(f"[MCP-SAFE] {msg}", file=sys.stderr, flush=True)
        
        self.log = log
        self.log("Initializing AIM-OS MCP Server (safe mode)...")
        
        # Initialize components safely
        self.llm = None
        self.agent = None
        self.memory = None
        self.hhni = None
        self.seg = None
        
        try:
            # Initialize LLM clients
            gemini_key = os.getenv("GEMINI_API_KEY")
            cerebras_key = os.getenv("CEREBRAS_API_KEY")
            
            if gemini_key:
                from llm_client import GeminiClient
                self.gemini = GeminiClient(api_key=gemini_key)
                self.llm = self.gemini
                self.log("Gemini client initialized")
            elif cerebras_key:
                from llm_client import CerebrasClient
                self.cerebras = CerebrasClient(api_key=cerebras_key)
                self.llm = self.cerebras
                self.log("Cerebras client initialized")
            else:
                self.log("WARNING: No LLM API keys set!")
            
            # Initialize AIM-OS systems safely
            if self.llm:
                with redirect_stdout(io.StringIO()):
                    from cmc_service import MemoryStore
                    from agent import AetherAgent
                    
                    self.memory = MemoryStore("./mcp_memory")
                    self.agent = AetherAgent(
                        llm_client=self.llm,
                        memory_store=self.memory,
                        index=None  # Don't initialize HHNI yet
                    )
                
                self.log("Agent initialized successfully")
            else:
                self.log("Skipping agent initialization - no LLM client")
            
        except Exception as e:
            self.log(f"Error during initialization: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        # Restore stdout for MCP protocol
        sys.stdout = sys.__stdout__
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
        tools = [
            {
                "name": "test_connection",
                "description": "Test the MCP connection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Test message"
                        }
                    },
                    "required": ["message"]
                }
            }
        ]
        
        # Add AIM-OS tools if available
        if self.agent:
            tools.extend([
                {
                    "name": "ask_agent",
                    "description": "Ask the conscious AI agent a question",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to ask"
                            }
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "get_agent_stats",
                    "description": "Get agent statistics",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ])
        
        return {"tools": tools}
    
    def call_tool(self, params: dict) -> dict:
        """Call a tool"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "test_connection":
            message = args.get("message", "Hello")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Connection test successful: {message}"
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "ask_agent" and self.agent:
            question = args.get("question")
            if question:
                try:
                    with redirect_stdout(io.StringIO()):
                        response = self.agent.process(question, "")
                    
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response.text
                            }
                        ],
                        "isError": False
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error processing question: {e}"
                            }
                        ],
                        "isError": True
                    }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No question provided"
                        }
                    ],
                    "isError": True
                }
        
        elif tool_name == "get_agent_stats" and self.agent:
            try:
                if self.memory:
                    atoms = self.memory.list_atoms()
                    stats = {
                        "total_memories": len(atoms),
                        "llm_provider": self.llm.__class__.__name__ if self.llm else "None",
                        "systems_active": ["CMC", "Agent"]
                    }
                else:
                    stats = {
                        "total_memories": 0,
                        "llm_provider": "None",
                        "systems_active": []
                    }
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(stats, indent=2)
                        }
                    ],
                    "isError": False
                }
            except Exception as e:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error getting stats: {e}"
                        }
                    ],
                    "isError": True
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
        server = SafeMCPServer()
        server.run()
    except Exception as e:
        print(f"[MCP-SAFE] FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

