# Frigg MCP Server - Troubleshooting Guide

## Quick Diagnostics

### 1. Test the MCP Server
Run the test suite to verify the server works correctly:
```powershell
cd D:\Frigg
.\tools\test_mcp_server.ps1
```

### 2. Check Server Logs
The MCP server logs to a persistent file:
```powershell
cat D:\Frigg\logs\frigg_mcp_server.log
```

### 3. Check Claude Desktop Logs
Claude Desktop logs are located at:
```
%APPDATA%\Claude\logs\mcp-server-frigg.log
```

View recent logs:
```powershell
cat "$env:APPDATA\Claude\logs\mcp-server-frigg.log" | Select-Object -Last 50
```

## Common Issues

### Issue: MCP server fails to start in Claude Desktop

**Symptoms:**
- No Frigg tools appear in Claude Desktop
- Error in Claude Desktop logs

**Solutions:**
1. Restart Claude Desktop completely
2. Check that the virtual environment exists: `Test-Path D:\Frigg\.venv`
3. Verify Python is installed: `D:\Frigg\.venv\Scripts\python.exe --version`
4. Run the test suite: `.\tools\test_mcp_server.ps1`

### Issue: Cannot connect to Blender bridge

**Symptoms:**
- Error: "Cannot connect to Blender bridge at 127.0.0.1:8765"
- Tool calls fail

**Solutions:**
1. Start the Blender bridge first:
   ```powershell
   cd D:\Frigg
   .\tools\frigg-bridge.ps1 -UI
   ```
2. Wait for "READY" message
3. Verify bridge is running:
   ```powershell
   cat D:\Frigg\.frigg_bridge.json
   ```

### Issue: Blender bridge times out

**Symptoms:**
- Error: "Blender bridge at 127.0.0.1:8765 timed out"

**Solutions:**
1. Check if Blender is frozen or busy
2. Try the operation again (timeout is 30 seconds)
3. Restart Blender bridge if needed

### Issue: Tools not appearing in Claude Desktop

**Symptoms:**
- Frigg server connected but no tools available

**Solutions:**
1. Check MCP server logs for errors
2. Verify tools/list response:
   ```powershell
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | D:\Frigg\.venv\Scripts\python.exe -m frigg_mcp.server.stdio
   ```

## Debug Mode

To enable detailed logging:

1. Check the server log file: `D:\Frigg\logs\frigg_mcp_server.log`
2. All operations are logged with timestamps
3. Errors include full stack traces

## Configuration Files

### Claude Desktop Config
Location: `%APPDATA%\Claude\claude_desktop_config.json`

Current config:
```json
{
  "mcpServers": {
    "frigg": {
      "command": "D:\\Frigg\\.venv\\Scripts\\pythonw.exe",
      "args": ["-m", "frigg_mcp.server.stdio"],
      "cwd": "D:\\Frigg"
    }
  }
}
```

### Bridge State File
Location: `D:\Frigg\.frigg_bridge.json`

Contains:
- Bridge host and port
- Process ID
- Start time

## Manual Testing

### Test MCP Server Directly
```powershell
cd D:\Frigg
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | .venv\Scripts\python.exe -m frigg_mcp.server.stdio
```

### Test Blender Bridge Connection
```powershell
cd D:\Frigg
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"frigg.blender.bridge_ping","arguments":{}}}' | .venv\Scripts\python.exe -m frigg_mcp.server.stdio
```

## Known Limitations

1. **Single Blender Instance**: Only one Blender bridge can run at a time
2. **Windows Only**: Currently only tested on Windows
3. **Blender 5.0**: Requires Blender 5.0 (configurable via BLENDER_EXE)

## Getting Help

If issues persist:
1. Run the test suite and save output
2. Check all log files (server + Claude Desktop)
3. Include Blender and Python versions
4. Include error messages and stack traces
