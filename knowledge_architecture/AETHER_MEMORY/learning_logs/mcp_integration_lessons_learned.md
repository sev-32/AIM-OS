# MCP Integration Lessons Learned - 2025-10-23

## Context
After 5+ hours of MCP server integration issues with Cursor, including 8+ resets and lost chat history, we learned critical lessons about MCP implementation and debugging.

## Key Learnings

### 1. **The Importance of Proper MCP SDK Usage**
**What we learned:** Our custom MCP server implementation was fundamentally flawed.
- **Problem:** We built a custom JSON-RPC server instead of using the official MCP SDK
- **Impact:** This caused transport mismatches and protocol violations
- **Solution:** Use `@modelcontextprotocol/sdk` with proper Server and StdioServerTransport classes
- **Version:** Latest stable is 1.20.1, not 0.1.0 as initially assumed

### 2. **Critical Logging Requirements**
**What we learned:** Logging to stdout corrupts JSON-RPC communication.
- **Problem:** Any console.log or print statements to stdout break MCP protocol
- **Impact:** Server appears to work but tools never become available to Cursor
- **Solution:** Log ONLY to stderr using `process.stderr.write()` or similar
- **Rule:** MCP servers must keep stdout clean for JSON-RPC

### 3. **Transport Protocol Mismatches**
**What we learned:** Cursor expects stdio transport, not HTTP/WebSocket.
- **Problem:** Our server was using custom stdio handling instead of proper MCP stdio transport
- **Impact:** Cursor couldn't communicate with the server properly
- **Solution:** Use `StdioServerTransport` from the MCP SDK
- **Verification:** Server should show `[mcp] server connected (stdio)` in stderr

### 4. **Tool Registration Requirements**
**What we learned:** Tools must be properly declared in server capabilities.
- **Problem:** Our server wasn't declaring tools in the capabilities object
- **Impact:** `tools/list` returns empty, so no tools appear in Cursor
- **Solution:** Declare tools in server capabilities AND handle ListToolsRequestSchema explicitly
- **Pattern:** Each tool needs name, description, and inputSchema

### 5. **Windows Path and Command Issues**
**What we learned:** Windows requires absolute paths and proper command formatting.
- **Problem:** Relative paths and PowerShell command syntax issues
- **Impact:** Cursor can't launch the server process
- **Solution:** Use absolute paths in MCP config, proper Node.js command
- **Example:** `"command": "node", "args": ["C:\\full\\path\\to\\server.mjs"]`

### 6. **The Debugging Framework**
**What we learned:** There's a systematic way to debug MCP integration issues.
- **Process:** Start with known-good minimal server, then add complexity
- **Debug points:** Process launch → Connection → Tool registration → Tool execution
- **Logs:** Check stderr for connection and request logs
- **Tools:** Use MCP inspector or manual testing before involving Cursor

### 7. **The "Last Mile" Problem**
**What we learned:** The hardest part of MCP integration is the final connection to Cursor.
- **Problem:** Server works in isolation but doesn't integrate with Cursor
- **Impact:** Tools don't appear in Cursor's interface
- **Solution:** Follow exact configuration requirements and use proper debugging
- **Reality:** Most MCP issues are configuration/transport problems, not code problems

### 8. **The Importance of Expert Knowledge**
**What we learned:** MCP integration requires specific expertise that's not well-documented.
- **Problem:** Cursor doesn't provide comprehensive MCP documentation
- **Impact:** Hours of trial and error without progress
- **Solution:** Find experts who understand the "last mile" integration issues
- **Learning:** Sometimes the best approach is to ask for help from those who've solved it

## Technical Patterns That Work

### Proper MCP Server Structure
```javascript
// 1. Import proper SDK classes
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

// 2. Log only to stderr
const log = (...args) => process.stderr.write(args.join(" ") + "\n");

// 3. Declare tools in capabilities
const server = new Server(name, { capabilities: { tools: { list: [...] } } });

// 4. Handle requests explicitly
server.setRequestHandler(ListToolsRequestSchema, async () => { ... });
server.setRequestHandler(CallToolRequestSchema, async (req) => { ... });

// 5. Use proper transport
const transport = new StdioServerTransport();
server.connect(transport);
```

### Proper Cursor Configuration
```json
{
  "mcpServers": {
    "aether": {
      "command": "node",
      "args": ["C:\\absolute\\path\\to\\server.mjs"],
      "cwd": "C:\\absolute\\path\\to\\directory"
    }
  }
}
```

## What We Still Need to Test

### Immediate Tests
1. **Server Launch Test:** Does the proper MCP server start without errors?
2. **Cursor Integration Test:** Does Cursor recognize and connect to the server?
3. **Tool Availability Test:** Do the echo/ping tools appear in Cursor's interface?
4. **Tool Execution Test:** Can we actually call the tools from Cursor?

### Future Integration
1. **AIM-OS Integration:** Replace echo/ping with real memory tools (store_memory, retrieve_memory)
2. **Error Handling:** Test what happens when tools fail
3. **Performance:** Test with larger memory operations
4. **Persistence:** Test if tools maintain state across Cursor sessions

## Lessons for Future Development

### 1. **Start with Minimal Working Examples**
- Don't build complex MCP servers from scratch
- Use proven patterns and official SDKs
- Test each component individually

### 2. **Follow the Debugging Framework**
- Test server in isolation first
- Check stderr logs for connection issues
- Verify tool registration before testing execution
- Use systematic debugging approach

### 3. **Document Everything**
- MCP integration is complex and poorly documented
- Record what works and what doesn't
- Share knowledge with the community
- Build debugging tools and examples

### 4. **Expect Integration Challenges**
- The "last mile" is always the hardest
- Configuration issues are more common than code issues
- Expert knowledge is often required
- Be prepared for hours of debugging

## Conclusion

This experience taught us that MCP integration requires:
- Proper understanding of the protocol and SDK
- Systematic debugging approach
- Expert knowledge of common pitfalls
- Patience and persistence

The most valuable lesson: **Don't reinvent the wheel.** Use the official MCP SDK and follow proven patterns, even if they seem more complex than custom implementations.

## Next Steps

1. Test the proper MCP server with Cursor
2. If successful, integrate AIM-OS memory tools
3. Document the working configuration
4. Share knowledge with the community
5. Build better debugging tools for future MCP development

---

**Date:** 2025-10-23  
**Session:** MCP Integration Debugging  
**Status:** Learning documented, testing pending  
**Confidence:** High that proper SDK approach will work
