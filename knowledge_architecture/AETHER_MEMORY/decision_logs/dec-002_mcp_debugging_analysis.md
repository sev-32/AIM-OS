# MCP Debugging Analysis - Finding the Root Cause

**Time:** Current Session  
**Type:** SYSTEMATIC DEBUGGING  
**Confidence:** 0.80  

---

## 🔍 **PROBLEM ANALYSIS**

**Symptoms:**
- Cursor app resets completely when MCP server enabled
- Chat history lost
- Authentication lost
- Settings lost
- Red dot beside MCP in settings (indicates failure)

**Paradox:** 
- MCP server works perfectly when run manually
- BUT fails when integrated with Cursor

---

## 📊 **EVIDENCE GATHERED**

### **Configuration File Status:**
**Location:** `C:\Users\bombe\.cursor\mcp.json`
**Current Content:**
```json
{
  "mcp": {
    "servers": {
      "aimos": {
        "command": "python",
        "args": ["-u", "run_mcp_stdio_clean.py"],
        "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
        "env": {
          "CEREBRAS_API_KEY": "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
        }
      }
    }
  }
}
```

### **CRITICAL ISSUE FOUND:**
**Missing GEMINI_API_KEY in configuration!**

The server code requires:
```python
# Line 76 in run_mcp_stdio_clean.py
if not gemini_key:
    self.log("WARNING: GEMINI_API_KEY not set!")

# Line 90-92
self.llm = self.gemini or self.cerebras
if not self.llm:
    raise ValueError("No LLM client available!")
```

**Current flow:**
1. Cursor starts MCP server
2. Server tries to initialize
3. GEMINI_API_KEY not in env
4. Cerebras initialization might be failing
5. If both fail, server crashes during initialization
6. Cursor detects crash and resets

---

## 🎯 **HYPOTHESIS**

**Primary Theory:** Server initialization is failing silently, causing Cursor to crash

**Evidence:**
- Configuration only has CEREBRAS_API_KEY
- Server requires at least ONE working LLM client
- If Cerebras init fails (network, API, etc.) → server crashes
- Cursor can't handle server crash gracefully → resets everything

**Secondary Theory:** Configuration format mismatch

**Evidence from docs:**
- Some sources show `"mcpServers"` (camelCase)
- Current config shows `"mcp.servers"` (nested object)
- This might be causing parsing issues

---

## 🛠️ **DEBUGGING PLAN**

### **Step 1: Test Minimal Server (NO dependencies)**
**File:** `minimal_mcp_server.py`
**Purpose:** Verify Cursor can start ANY MCP server
**Test:**
```json
{
  "mcpServers": {
    "test": {
      "command": "python",
      "args": ["-u", "minimal_mcp_server.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
    }
  }
}
```

**Expected Result:**
- If this works → Problem is in our complex server
- If this fails → Cursor MCP integration is broken

### **Step 2: Add GEMINI_API_KEY**
**Update config:**
```json
{
  "mcpServers": {
    "aimos": {
      "command": "python",
      "args": ["-u", "run_mcp_stdio_clean.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "GEMINI_API_KEY": "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY",
        "CEREBRAS_API_KEY": "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
      }
    }
  }
}
```

**Purpose:** Ensure at least ONE LLM client initializes successfully

### **Step 3: Add Error Logging**
**Create:** `run_mcp_stdio_debug.py`
**Purpose:** Log every step of initialization to file
**Approach:**
```python
# Write to debug log file (not stdout/stderr)
with open("C:\\Users\\bombe\\Desktop\\mcp_debug.log", "a") as f:
    f.write(f"{datetime.now()}: Server starting...\n")
    f.flush()
```

### **Step 4: Test Server Manually First**
**Command:**
```bash
python -u run_mcp_stdio_clean.py
```

**Send test request:**
```json
{"id": 1, "method": "tools/list", "params": {}}
```

**Expected:** Should return tools list without crashing

---

## 🚨 **CRITICAL RISKS**

**Testing Risk:**
- Each test might cause Cursor to reset
- Could lose chat history
- Could lose settings

**Mitigation:**
1. Backup Cursor settings before each test
2. Test minimal server FIRST (safest)
3. Document every single test result
4. Only test ONE change at a time

---

## 💡 **LIKELY ROOT CAUSES (Ranked)**

**1. Missing GEMINI_API_KEY + Cerebras Failure** (80% probability)
- Configuration only has Cerebras key
- If Cerebras init fails, server has NO LLM
- Server crashes during initialization
- Cursor can't handle crash gracefully

**2. Configuration Format Mismatch** (60% probability)
- `"mcp.servers"` vs `"mcpServers"`
- Might need camelCase format

**3. Initialization Timeout** (40% probability)
- AIM-OS systems take ~3 seconds to initialize
- Cursor might have timeout for server startup
- Server killed before ready

**4. Path/Permission Issues** (20% probability)
- Python not in PATH when Cursor spawns process
- Working directory permissions
- Database file permissions

---

## 🎯 **IMMEDIATE ACTION**

**Test 1: Minimal Server**
- Update config to use `minimal_mcp_server.py`
- Restart Cursor
- Check if green dot appears
- Document result

**If Test 1 Succeeds:**
→ Problem is in our complex server initialization
→ Proceed to debug complex server

**If Test 1 Fails:**
→ Cursor MCP integration broken
→ Need to check Cursor version/settings

---

**Written with systematic debugging rigor**  
**By Aether, determined to solve this** 💙  
**Status: READY TO DEBUG**


