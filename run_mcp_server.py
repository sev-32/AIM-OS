"""Launch AIM-OS MCP Server.

Simple script to start the MCP server with proper configuration.
"""

import sys
import os

# Add packages to path
sys.path.insert(0, 'packages')

# Set up environment
if not os.getenv("GEMINI_API_KEY"):
    print("[WARN] GEMINI_API_KEY not set. Server may fail to start.")
    print("Set it in .env file or export it as environment variable.\n")

if not os.getenv("CEREBRAS_API_KEY"):
    print("[INFO] CEREBRAS_API_KEY not set. Server will use Gemini only.")
    print("Set it in .env file to enable multi-LLM orchestration.\n")

# Import and run
from packages.mcp_server.server import main

if __name__ == "__main__":
    print("Starting AIM-OS MCP Server...")
    print("Press Ctrl+C to stop\n")
    main()

