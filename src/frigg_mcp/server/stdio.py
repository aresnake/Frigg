import json
import os
import signal
import socket
import sys
import traceback
from typing import Any, Dict, Optional, Tuple

from frigg_mcp import __version__ as FRIGG_VERSION

from frigg_mcp.tools import core_tools
from frigg_mcp.tools.search_tools import handle_search_tools

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "frigg-mcp", "version": FRIGG_VERSION}
# Track if we're shutting down
_SHUTTING_DOWN = False

def log(message: str) -> None:
    """Log to stderr and optionally to a log file"""
    print(message, file=sys.stderr, flush=True)

    # Also log to file for persistent debugging
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "frigg_mcp_server.log")

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Don't fail if we can't write to log file
        pass


def jsonrpc_error(code: int, message: str, req_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def jsonrpc_result(result: Any, req_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _state_file_path() -> str:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    return os.path.join(repo_root, ".frigg_bridge.json")


def _read_state_file() -> Optional[Dict[str, Any]]:
    path = _state_file_path()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError:
        return None
    except json.JSONDecodeError:
        return None


def get_bridge_target() -> Tuple[str, int]:
    host_env = os.environ.get("FRIGG_BRIDGE_HOST")
    port_env = os.environ.get("FRIGG_BRIDGE_PORT")
    host = host_env or None

    port = None
    if port_env:
        try:
            port = int(port_env)
        except ValueError:
            port = None

    if port is not None:
        return host or "127.0.0.1", port

    state = _read_state_file()
    if state:
        state_host = state.get("host")
        state_port = state.get("port")
        try:
            state_port = int(state_port)
        except (TypeError, ValueError):
            state_port = None
        if state_port is not None:
            # Log the bridge info for debugging
            log(f"Using Blender bridge from state file: {state_host or '127.0.0.1'}:{state_port}")
            return host or state_host or "127.0.0.1", state_port

    # No state file found
    log("No bridge state file found. Using default port 8765.")
    return host or "127.0.0.1", 8765


def call_bridge(method: str, params: Dict[str, Any], retry: int = 0) -> Dict[str, Any]:
    host, port = get_bridge_target()
    request = {"method": method, "params": params}
    data = json.dumps(request) + "\n"

    try:
        with socket.create_connection((host, port), timeout=30) as sock:
            sock.sendall(data.encode("utf-8"))
            file = sock.makefile("r", encoding="utf-8")
            line = file.readline()
            if not line:
                raise RuntimeError("Empty response from bridge")
            response = json.loads(line)
    except ConnectionRefusedError:
        # If this is a bridge_ping and it's the first try, maybe the bridge is still starting
        if method == "bridge_ping" and retry < 2:
            import time
            log(f"Bridge not ready yet, retrying in 1 second... (attempt {retry + 1}/3)")
            time.sleep(1)
            return call_bridge(method, params, retry + 1)

        raise RuntimeError(
            f"Cannot connect to Blender bridge at {host}:{port}. "
            "Make sure to run frigg-bridge.ps1 first to start Blender with the bridge server."
        )
    except socket.timeout:
        raise RuntimeError(
            f"Blender bridge at {host}:{port} timed out. "
            "The operation may be taking too long or Blender may be frozen."
        )
    except OSError as e:
        raise RuntimeError(f"Network error connecting to Blender bridge: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON response from Blender bridge: {e}")

    if not isinstance(response, dict):
        raise RuntimeError("Invalid bridge response: expected object")
    if "ok" not in response:
        raise RuntimeError("Invalid bridge response: missing ok")
    if response.get("ok") is True:
        if "result" not in response:
            raise RuntimeError("Invalid bridge response: missing result")
        return {"ok": True, "result": response.get("result")}
    error_msg = response.get("error") or "Unknown bridge error"
    if isinstance(error_msg, dict) and "code" in error_msg and "message" in error_msg:
        return {"ok": False, "error": error_msg}
    return {
        "ok": False,
        "error": {"code": "bridge_error", "message": str(error_msg)},
    }


def tools_list() -> Dict[str, Any]:
    return core_tools.tools_list()


def handle_call(name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if name in core_tools.CORE_TOOL_NAMES:
        return core_tools.handle_core_call(name, arguments, call_bridge)

    if name == "frigg_search_tools":
        return handle_search_tools(arguments or {})

    return core_tools.error_result("unknown_tool", f"Unknown tool: {name}")


def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if request.get("jsonrpc") != "2.0":
        return jsonrpc_error(-32600, "Invalid Request", request.get("id"))

    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    # Handle notifications (requests without an id) - they should not get a response
    if req_id is None:
        if method == "initialized":
            # This is a notification that initialization is complete
            return None
        if method == "notifications/cancelled":
            # Handle cancellation notification
            return None
        if method == "notifications/progress":
            # Handle progress notification
            return None
        # Ignore other notifications
        log(f"Ignoring unknown notification: {method}")
        return None

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {"tools": {}},
        }
        return jsonrpc_result(result, req_id)

    if method == "ping":
        # Handle ping method from MCP protocol
        return jsonrpc_result({}, req_id)

    if method == "tools/list":
        return jsonrpc_result(tools_list(), req_id)

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments")
        if not name:
            return jsonrpc_error(-32602, "Missing tool name", req_id)
        try:
            result = handle_call(name, arguments)
        except Exception as exc:
            log(f"Tool call error: {exc}")
            log(traceback.format_exc())
            result = core_tools.error_result("internal_error", str(exc))

        # Convert internal result format to MCP format
        if isinstance(result, dict):
            if result.get("ok") is True:
                # Success: wrap result in MCP content format
                inner_result = result.get("result", {})
                import json
                mcp_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(inner_result, indent=2)
                        }
                    ]
                }
                return jsonrpc_result(mcp_result, req_id)
            else:
                # Error: return as MCP error with content
                error_info = result.get("error", {})
                error_message = error_info.get("message", "Unknown error") if isinstance(error_info, dict) else str(error_info)
                mcp_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: {error_message}"
                        }
                    ],
                    "isError": True
                }
                return jsonrpc_result(mcp_result, req_id)

        # Fallback for unexpected format
        return jsonrpc_result({"content": [{"type": "text", "text": str(result)}]}, req_id)

    # Handle methods we don't support yet but shouldn't error on
    if method in ("resources/list", "prompts/list"):
        # Return empty lists for unsupported capabilities
        return jsonrpc_result({method.split("/")[0]: []}, req_id)

    log(f"Unknown method: {method}")
    return jsonrpc_error(-32601, "Method not found", req_id)


def _handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    global _SHUTTING_DOWN
    log(f"Received signal {signum}, shutting down gracefully...")
    _SHUTTING_DOWN = True
    sys.exit(0)


def main() -> None:
    # Register signal handlers for graceful shutdown
    try:
        signal.signal(signal.SIGTERM, _handle_shutdown)
        signal.signal(signal.SIGINT, _handle_shutdown)
    except (AttributeError, ValueError):
        # signal.SIGTERM might not be available on all platforms
        log("Warning: Could not register signal handlers")

    log("Frigg MCP server starting...")
    log(f"Python version: {sys.version}")
    log(f"Protocol version: {PROTOCOL_VERSION}")

    try:
        for line in sys.stdin:
            if _SHUTTING_DOWN:
                break
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                # Don't send parse errors as they can't have a valid id anyway
                # Just log and continue
                log(f"JSON parse error: {e}")
                continue

            try:
                response = handle_request(request)
            except Exception as e:
                # Catch any unexpected errors in request handling
                log(f"Unexpected error handling request: {e}")
                log(traceback.format_exc())
                # Try to send an error response if we have an id
                req_id = request.get("id") if isinstance(request, dict) else None
                if req_id is not None:
                    response = jsonrpc_error(-32603, f"Internal error: {str(e)}", req_id)
                    print(json.dumps(response), flush=True)
                continue

            if response is None:
                continue
            print(json.dumps(response), flush=True)
    except KeyboardInterrupt:
        log("Received KeyboardInterrupt, shutting down...")
    except Exception as e:
        log(f"Fatal error in main loop: {e}")
        log(traceback.format_exc())
        sys.exit(1)
    finally:
        log("Frigg MCP server stopped.")


if __name__ == "__main__":
    main()
