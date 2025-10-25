# MCP Troubleshooting Guide

**Issue:** AIM-OS MCP showing red dot in Cursor  
**Status:** Server working correctly, configuration updated  

---

## 🔍 **DIAGNOSIS COMPLETE**

### **✅ What's Working:**
- **MCP Server:** `run_mcp_stdio_clean.py` - Fully functional
- **All 3 Tools:** ask_agent, retrieve_memory, get_agent_stats
- **Windows Compatibility:** Stdio buffering issues resolved
- **Configuration:** Updated and correct
- **Test Results:** All tests passing

### **📊 Test Results:**
```
[PASS] Server starts successfully
[PASS] Found 3 tools: ask_agent, retrieve_memory, get_agent_stats
[PASS] Got stats response with system status
[PASS] Agent responded: 2 + 2 = 4
[PASS] 8 memories stored and retrievable
[PASS] CMC, HHNI, VIF, SEG all active
[PASS] Clean protocol communication
[PASS] Both Gemini and Cerebras initialized
```

---

## 🛠️ **SOLUTION STEPS**

### **Step 1: Restart Cursor Completely**
**The red dot indicates Cursor hasn't picked up the new configuration yet.**

1. **Close Cursor completely** (all windows)
2. **Wait 5 seconds**
3. **Restart Cursor**
4. **Check MCP status** - should show green dot

### **Step 2: Verify Configuration**
**Current configuration is correct:**
```json
{
  "mcpServers": {
    "aimos": {
      "command": "python",
      "args": ["-u", "run_mcp_stdio_clean.py"],
      "cwd": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS",
      "env": {
        "GEMINI_API_KEY": "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY",
        "CEREBRAS_API_KEY": "csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty",
        "PYTHONPATH": "C:\\Users\\bombe\\OneDrive\\Desktop\\AIM-OS"
      }
    }
  }
}
```

### **Step 3: Check MCP Status**
**After restart, look for:**
- **Green dot** next to "aimos" in MCP panel
- **3 tools available:** ask_agent, retrieve_memory, get_agent_stats
- **No error messages** in Cursor output

---

## 🚨 **IF STILL RED DOT**

### **Check Cursor Version**
**MCP support may be recent:**
- Update Cursor to latest version
- Check Cursor release notes for MCP support

### **Check Configuration File**
**Verify the configuration file exists and is valid:**
```bash
# Check if file exists
Test-Path "C:\Users\bombe\.cursor\mcp.json"

# Check if JSON is valid
Get-Content "C:\Users\bombe\.cursor\mcp.json" | ConvertFrom-Json
```

### **Check Server Manually**
**Test the server directly:**
```bash
# Set environment variables
$env:GEMINI_API_KEY="AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
$env:CEREBRAS_API_KEY="csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"

# Test server
python test_cursor_mcp_simple.py
```

---

## 🎯 **EXPECTED BEHAVIOR AFTER RESTART**

### **Green Dot Status:**
- **MCP server connected** and ready
- **Tools available** in Cursor interface
- **No error messages** in output

### **Usage:**
- **Type:** `@aimos ask_agent "What is 2+2?"`
- **Expected:** Agent responds with "2 + 2 = 4"
- **Memory:** Interaction stored for future reference

---

## 📊 **TECHNICAL DETAILS**

### **Server Status:**
- **File:** `run_mcp_stdio_clean.py` ✅
- **Windows Compatibility:** Fixed ✅
- **API Keys:** Configured ✅
- **Environment:** Set correctly ✅

### **Configuration:**
- **File:** `C:\Users\bombe\.cursor\mcp.json` ✅
- **JSON Format:** Valid ✅
- **Paths:** Correct ✅
- **Environment Variables:** Set ✅

### **Test Results:**
- **Server Startup:** ✅
- **Tools List:** ✅
- **Agent Response:** ✅
- **Memory Persistence:** ✅

---

## 💡 **WHY RED DOT APPEARED**

### **Most Likely Cause:**
**Cursor needs to be restarted to pick up the new MCP configuration.**

### **Other Possible Causes:**
1. **Cursor version** doesn't support MCP yet
2. **Configuration file** has syntax errors
3. **Server process** not starting correctly
4. **Environment variables** not set properly

### **Our Diagnosis:**
**All technical components are working correctly. The issue is likely that Cursor needs to be restarted to pick up the updated configuration.**

---

## 🚀 **NEXT STEPS**

### **Immediate:**
1. **Restart Cursor completely**
2. **Check for green dot** in MCP panel
3. **Test with:** `@aimos ask_agent "Hello"`

### **If Still Issues:**
1. **Update Cursor** to latest version
2. **Check Cursor logs** for error messages
3. **Verify configuration** file syntax
4. **Test server manually** with our test script

---

## 📞 **SUPPORT**

### **Files Created for Troubleshooting:**
- `test_cursor_mcp_simple.py` - Test MCP server
- `cursor_mcp_config_fixed.json` - Correct configuration
- `MCP_TROUBLESHOOTING_GUIDE.md` - This guide

### **Test Commands:**
```bash
# Test server
python test_cursor_mcp_simple.py

# Test with environment
$env:GEMINI_API_KEY="AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
$env:CEREBRAS_API_KEY="csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty"
python test_stdio_simple.py
```

---

**The MCP server is working perfectly. The red dot should turn green after restarting Cursor!** 🚀

**Troubleshooting Guide by Aether**  
**Date:** 2025-01-23  
**Status:** MCP Server Working, Configuration Updated  
**Solution:** Restart Cursor to pick up new configuration ✨
