import json
import os
import socket
import sys
from typing import Any, Dict, Optional

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "frigg-mcp", "version": "0.1.0"}


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def jsonrpc_error(code: int, message: str, req_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def jsonrpc_result(result: Any, req_id: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def get_bridge_target() -> tuple[str, int]:
    host = os.environ.get("FRIGG_BRIDGE_HOST", "127.0.0.1")
    port_str = os.environ.get("FRIGG_BRIDGE_PORT", "7878")
    try:
        port = int(port_str)
    except ValueError:
        port = 7878
    return host, port


def call_bridge(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    host, port = get_bridge_target()
    request = {"method": method, "params": params}
    data = json.dumps(request) + "\n"

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(data.encode("utf-8"))
        file = sock.makefile("r", encoding="utf-8")
        line = file.readline()
        if not line:
            raise RuntimeError("Empty response from bridge")
        response = json.loads(line)
    return response


def tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "frigg.ping",
                "description": "Simple ping without Blender.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "frigg.blender.scene_info",
                "description": "Get basic scene info from Blender.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "frigg.blender.list_objects",
                "description": "List all objects in the Blender file.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "frigg.blender.move_object",
                "description": "Move an object to a new location.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "location": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    },
                    "required": ["name", "location"],
                    "additionalProperties": False,
                },
            },
        ]
    }


def tool_result_text(payload: Any) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload)}]}


def handle_call(name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if name == "frigg.ping":
        return tool_result_text({"ok": True, "message": "pong"})

    if name == "frigg.blender.scene_info":
        response = call_bridge("scene_info", {})
        return tool_result_text(response)

    if name == "frigg.blender.list_objects":
        response = call_bridge("list_objects", {})
        return tool_result_text(response)

    if name == "frigg.blender.move_object":
        args = arguments or {}
        response = call_bridge("move_object", args)
        return tool_result_text(response)

    raise ValueError(f"Unknown tool: {name}")


def handle_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if request.get("jsonrpc") != "2.0":
        return jsonrpc_error(-32600, "Invalid Request", request.get("id"))

    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {"tools": {}},
        }
        return jsonrpc_result(result, req_id)

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
            return jsonrpc_error(-32603, str(exc), req_id)
        return jsonrpc_result(result, req_id)

    return jsonrpc_error(-32601, "Method not found", req_id)


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = jsonrpc_error(-32700, "Parse error", None)
            print(json.dumps(response), flush=True)
            continue

        response = handle_request(request)
        if response is None:
            continue
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()