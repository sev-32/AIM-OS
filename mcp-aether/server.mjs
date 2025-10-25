// Minimal MCP server over STDIO with two tools: echo & ping
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

// Helper: log ONLY to stderr so we don't corrupt stdout JSON-RPC
const log = (...args) => process.stderr.write(args.join(" ") + "\n");

// 1) Create server & declare capabilities
const server = new Server(
  { name: "aether-mcp", version: "0.1.0" },
  {
    capabilities: {
      tools: {
        // declare the tool surface so `tools/list` isn't empty
        list: [
          {
            name: "echo",
            description: "Echo text back.",
            inputSchema: {
              type: "object",
              properties: { text: { type: "string" } },
              required: ["text"]
            }
          },
          {
            name: "ping",
            description: "Return 'pong' with a timestamp.",
            inputSchema: { type: "object", properties: {} }
          }
        ]
      }
    }
  }
);

// 2) Handle tools/list explicitly (some SDKs auto-provide it, we'll be explicit)
server.setRequestHandler(ListToolsRequestSchema, async () => {
  log("[mcp] tools/list");
  return {
    tools: server.getCapabilities().tools.list
  };
});

// 3) Handle tools/call for our two tools
server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args = {} } = req.params;
  log(`[mcp] tools/call ${name}`);

  if (name === "echo") {
    const text = String(args.text ?? "");
    return {
      content: [{ type: "text", text }]
    };
  }

  if (name === "ping") {
    return {
      content: [{
        type: "text",
        text: `pong @ ${new Date().toISOString()}`
      }]
    };
  }

  // Unknown tool
  return {
    isError: true,
    content: [{ type: "text", text: `Unknown tool: ${name}` }]
  };
});

// 4) Connect over stdio
const transport = new StdioServerTransport();
server.connect(transport).then(() => log("[mcp] server connected (stdio)"));
