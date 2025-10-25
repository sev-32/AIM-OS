#!/usr/bin/env node

// Simple Node.js MCP server for AIM-OS
// This might work better with Cursor than the Python version

const { spawn } = require('child_process');
const path = require('path');

console.error('[MCP-NODE] Starting AIM-OS MCP Server...');

// Spawn the Python MCP server
const pythonServer = spawn('python', ['-u', 'run_mcp_aimos.py'], {
  cwd: __dirname,
  stdio: ['inherit', 'inherit', 'inherit']
});

pythonServer.on('error', (error) => {
  console.error('[MCP-NODE] Error starting Python server:', error);
  process.exit(1);
});

pythonServer.on('exit', (code) => {
  console.error(`[MCP-NODE] Python server exited with code ${code}`);
  process.exit(code);
});

// Handle process termination
process.on('SIGINT', () => {
  console.error('[MCP-NODE] Shutting down...');
  pythonServer.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('[MCP-NODE] Shutting down...');
  pythonServer.kill();
  process.exit(0);
});

