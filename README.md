# Frigg MCP Blender Standard v0

Minimal MCP stdio server that forwards Blender tool calls to a TCP bridge.

## v0.1 notes
- Timer-based keepalive (no blocking loop in Blender).
- Added `bridge_ping` for lightweight bridge health checks.

## v0.2 notes
- MCP tool results now return structured JSON directly.
- Added `get_object_transform` and `set_object_location`.

## Quick start
1) Start the Blender bridge:
   pwsh -File .\tools\frigg-bridge.ps1 -UI

2) Start the MCP stdio server:
   python -m frigg_mcp.server.stdio

3) Run the smoke test (bridge must be running):
   python .\tools\mcp_smoke_test_stdio.py
