import json
import os
import signal
import socket
import sys
import traceback
from typing import Any, Dict, Optional, Tuple

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "frigg-mcp", "version": "0.1.3"}

# Track if we're shutting down
_SHUTTING_DOWN = False

# Tool metadata catalog for search/discovery
TOOL_METADATA = {
    # CORE
    "scene_info": {
        "category": "core",
        "visibility": "visible",
        "tags": ["scene", "info", "basics"],
        "description": "Get basic scene information",
        "complexity": "simple"
    },
    "list_objects": {
        "category": "core",
        "visibility": "visible",
        "tags": ["list", "objects", "scene"],
        "description": "List all objects in scene",
        "complexity": "simple"
    },
    # TRANSFORMS
    "set_object_location": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["move", "position", "location", "transform"],
        "description": "Set object location/position",
        "complexity": "simple"
    },
    "set_object_rotation": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["rotate", "rotation", "angle", "transform"],
        "description": "Set object rotation",
        "complexity": "simple"
    },
    "set_object_scale": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["scale", "size", "resize", "transform"],
        "description": "Set object scale",
        "complexity": "simple"
    },
    "get_object_transform": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["get", "read", "transform", "position"],
        "description": "Get object transform (location/rotation/scale)",
        "complexity": "simple"
    },
    # VISION
    "viewport_snapshot": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["view", "screenshot", "image", "render", "vision"],
        "description": "Capture viewport as image",
        "complexity": "simple"
    },
    "get_bounding_box": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["measure", "dimensions", "size", "bounds"],
        "description": "Get object bounding box and dimensions",
        "complexity": "simple"
    },
    "get_spatial_relationships": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["spatial", "position", "relationship", "above", "below"],
        "description": "Determine spatial relationships between objects",
        "complexity": "simple"
    },
    # CREATION (will be added as implemented)
    "create_primitive": {
        "category": "creation",
        "visibility": "visible",
        "tags": ["create", "primitive", "cube", "sphere", "cylinder", "new"],
        "description": "Create primitive objects (cube, sphere, cylinder, etc.)",
        "complexity": "simple"
    },
    "duplicate_object": {
        "category": "creation",
        "visibility": "visible",
        "tags": ["duplicate", "copy"],
        "description": "Duplicate object",
        "complexity": "simple"
    },
    "delete_object": {
        "category": "operations",
        "visibility": "visible",
        "tags": ["delete", "remove"],
        "description": "Delete object",
        "complexity": "simple"
    },
    "rename_object": {
        "category": "operations",
        "visibility": "visible",
        "tags": ["rename", "name"],
        "description": "Rename object",
        "complexity": "simple"
    },
    "set_material": {
        "category": "materials",
        "visibility": "visible",
        "tags": ["material", "color", "shader"],
        "description": "Set material",
        "complexity": "simple"
    },
    "set_parent": {
        "category": "hierarchy",
        "visibility": "visible",
        "tags": ["parent", "hierarchy"],
        "description": "Parent objects",
        "complexity": "simple"
    },
    "set_smooth_shading": {
        "category": "materials",
        "visibility": "visible",
        "tags": ["smooth", "shading"],
        "description": "Smooth shading",
        "complexity": "simple"
    },
}


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
    return {"ok": False, "error": str(error_msg)}


def tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "frigg.ping",
                "description": "Simple ping without Blender.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "frigg.search_tools",
                "description": "Search and discover available Frigg tools by keyword, category, or capability. Use this to find tools for specific tasks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keyword to search for (searches in tool names, tags, and descriptions)"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["core", "transforms", "vision", "creation", "materials", "modifiers", "lighting", "camera", "animation"],
                            "description": "Filter by tool category"
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include hidden/advanced tools in results"
                        }
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.bridge_ping",
                "description": "Ping the Blender bridge server.",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "frigg.blender.get_object_transform",
                "description": "Get object transform by name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.set_object_location",
                "description": "Set object location by name.",
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
            {
                "name": "frigg.blender.set_object_rotation",
                "description": "Set object rotation. Supports degrees (default), radians, or quaternion. Returns rotation in both degrees and radians.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of the object to rotate"
                        },
                        "rotation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                            "description": "Rotation as [x, y, z] angles"
                        },
                        "rotation_mode": {
                            "type": "string",
                            "enum": ["degrees", "radians", "quaternion"],
                            "default": "degrees",
                            "description": "Input format for rotation values"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"],
                            "default": "XYZ",
                            "description": "Euler rotation order"
                        }
                    },
                    "required": ["object_name", "rotation"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.set_object_scale",
                "description": "Set object scale. Supports uniform scale (single number) or per-axis scale ([x, y, z]). Returns current scale and transform.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of the object to scale"
                        },
                        "scale": {
                            "description": "Scale factor: number for uniform, or [x, y, z] array for per-axis",
                            "oneOf": [
                                {"type": "number"},
                                {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 3,
                                    "maxItems": 3
                                }
                            ]
                        }
                    },
                    "required": ["object_name", "scale"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.create_primitive",
                "description": "Create a primitive object (cube, sphere, cylinder, cone, torus, plane, monkey). Unified creation tool.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "primitive_type": {
                            "type": "string",
                            "enum": ["cube", "sphere", "cylinder", "cone", "torus", "plane", "monkey"],
                            "description": "Type of primitive to create"
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional custom name for the object"
                        },
                        "location": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                            "description": "Optional location [x, y, z]",
                            "default": [0, 0, 0]
                        },
                        "rotation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                            "description": "Optional rotation [x, y, z] in degrees",
                            "default": [0, 0, 0]
                        },
                        "scale": {
                            "description": "Optional scale (number for uniform, or [x, y, z])",
                            "oneOf": [
                                {"type": "number"},
                                {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 3,
                                    "maxItems": 3
                                }
                            ],
                            "default": 1.0
                        },
                        "size": {
                            "type": "number",
                            "description": "Optional size parameter",
                            "default": 2.0
                        }
                    },
                    "required": ["primitive_type"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.duplicate_object",
                "description": "Duplicate an object with optional new name and offset.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {"type": "string", "description": "Object to duplicate"},
                        "new_name": {"type": "string", "description": "Optional new name"},
                        "offset": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                            "default": [0, 0, 0]
                        }
                    },
                    "required": ["object_name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "frigg.blender.delete_object",
                "description": "Delete an object from the scene.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {"type": "string", "description": "Object to delete"}
                    },
                    "required": ["object_name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "frigg.blender.rename_object",
                "description": "Rename an object.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {"type": "string", "description": "Current name"},
                        "new_name": {"type": "string", "description": "New name"}
                    },
                    "required": ["object_name", "new_name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "frigg.blender.set_material",
                "description": "Create and assign material with color and PBR properties.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {"type": "string"},
                        "material_name": {"type": "string", "default": "Material"},
                        "color": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 4,
                            "maxItems": 4,
                            "default": [0.8, 0.8, 0.8, 1.0]
                        },
                        "metallic": {"type": "number", "default": 0.0, "minimum": 0, "maximum": 1},
                        "roughness": {"type": "number", "default": 0.5, "minimum": 0, "maximum": 1}
                    },
                    "required": ["object_name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "frigg.blender.set_parent",
                "description": "Set parent-child relationship between objects.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "child": {"type": "string"},
                        "parent": {"type": "string"},
                        "keep_transform": {"type": "boolean", "default": True}
                    },
                    "required": ["child", "parent"],
                    "additionalProperties": False
                }
            },
            {
                "name": "frigg.blender.set_smooth_shading",
                "description": "Set smooth or flat shading on mesh object.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {"type": "string"},
                        "smooth": {"type": "boolean", "default": True}
                    },
                    "required": ["object_name"],
                    "additionalProperties": False
                }
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
            {
                "name": "frigg.blender.viewport_snapshot",
                "description": "Capture a viewport snapshot from the UI as base64 PNG image.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "shading": {
                            "type": "string",
                            "enum": ["solid", "wireframe"],
                            "description": "Shading mode for the viewport",
                            "default": "solid"
                        },
                        "projection": {
                            "type": "string",
                            "enum": ["persp", "ortho"],
                            "description": "Projection mode",
                            "default": "persp"
                        },
                        "view": {
                            "type": "string",
                            "enum": ["current", "front", "back", "left", "right", "top", "bottom"],
                            "description": "View orientation (current uses viewport, others set specific angles)",
                            "default": "current"
                        },
                        "width": {
                            "type": "integer",
                            "description": "Image width in pixels",
                            "default": 512,
                            "minimum": 64,
                            "maximum": 2048
                        },
                        "height": {
                            "type": "integer",
                            "description": "Image height in pixels",
                            "default": 512,
                            "minimum": 64,
                            "maximum": 2048
                        },
                        "return_base64": {
                            "type": "boolean",
                            "description": "Include base64-encoded image in the response",
                            "default": False
                        },
                        "filename": {
                            "type": "string",
                            "description": "Optional output filename (defaults to timestamped PNG)"
                        }
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.get_bounding_box",
                "description": "Get bounding box dimensions, world bounds, and volume of an object. Critical for understanding object sizes and spatial relationships.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of the object to get bounding box for"
                        }
                    },
                    "required": ["object_name"],
                    "additionalProperties": False,
                },
            },
            {
                "name": "frigg.blender.get_spatial_relationships",
                "description": "Determine spatial relationships between two objects (above/below, left_of/right_of, in_front_of/behind). Returns the primary relationship and all applicable relationships based on relative positions in 3D space.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object1": {
                            "type": "string",
                            "description": "First object name"
                        },
                        "object2": {
                            "type": "string",
                            "description": "Second object name (reference point)"
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Minimum distance threshold to consider a relationship (default 0.1)",
                            "default": 0.1
                        }
                    },
                    "required": ["object1", "object2"],
                    "additionalProperties": False,
                },
            },
        ]
    }


def handle_call(name: str, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if name == "frigg.ping":
        return {"ok": True, "result": {"message": "pong"}}

    if name == "frigg.search_tools":
        # Local tool - no bridge needed
        args = arguments or {}
        query = args.get("query", "").lower()
        category_filter = args.get("category", "").lower()
        show_hidden = args.get("show_hidden", False)

        results = []
        categories_found = set()

        for tool_name, metadata in TOOL_METADATA.items():
            # Filter by visibility
            if not show_hidden and metadata["visibility"] != "visible":
                continue

            # Filter by category
            if category_filter and metadata["category"] != category_filter:
                continue

            # Filter by query (search in name, tags, description)
            if query:
                searchable = (
                    tool_name.lower() + " " +
                    " ".join(metadata["tags"]) + " " +
                    metadata["description"].lower()
                )
                if query not in searchable:
                    continue

            # Match found
            results.append({
                "name": f"frigg.blender.{tool_name}",
                "category": metadata["category"],
                "description": metadata["description"],
                "visibility": metadata["visibility"],
                "tags": metadata["tags"],
                "complexity": metadata["complexity"]
            })
            categories_found.add(metadata["category"])

        return {
            "ok": True,
            "result": {
                "tools": results,
                "total_found": len(results),
                "categories_found": sorted(list(categories_found))
            }
        }

    if name == "frigg.blender.scene_info":
        response = call_bridge("scene_info", {})
        return response

    if name == "frigg.blender.bridge_ping":
        response = call_bridge("bridge_ping", {})
        return response

    if name == "frigg.blender.get_object_transform":
        args = arguments or {}
        response = call_bridge("get_object_transform", args)
        return response

    if name == "frigg.blender.set_object_location":
        args = arguments or {}
        response = call_bridge("set_object_location", args)
        return response

    if name == "frigg.blender.set_object_rotation":
        args = arguments or {}
        response = call_bridge("set_object_rotation", args)
        return response

    if name == "frigg.blender.set_object_scale":
        args = arguments or {}
        response = call_bridge("set_object_scale", args)
        return response

    if name == "frigg.blender.create_primitive":
        args = arguments or {}
        response = call_bridge("create_primitive", args)
        return response

    if name == "frigg.blender.duplicate_object":
        args = arguments or {}
        response = call_bridge("duplicate_object", args)
        return response

    if name == "frigg.blender.delete_object":
        args = arguments or {}
        response = call_bridge("delete_object", args)
        return response

    if name == "frigg.blender.rename_object":
        args = arguments or {}
        response = call_bridge("rename_object", args)
        return response

    if name == "frigg.blender.set_material":
        args = arguments or {}
        response = call_bridge("set_material", args)
        return response

    if name == "frigg.blender.set_parent":
        args = arguments or {}
        response = call_bridge("set_parent", args)
        return response

    if name == "frigg.blender.set_smooth_shading":
        args = arguments or {}
        response = call_bridge("set_smooth_shading", args)
        return response

    if name == "frigg.blender.list_objects":
        response = call_bridge("list_objects", {})
        return response

    if name == "frigg.blender.move_object":
        args = arguments or {}
        response = call_bridge("move_object", args)
        return response

    if name == "frigg.blender.viewport_snapshot":
        args = arguments or {}
        response = call_bridge("viewport_snapshot", args)
        return response

    if name == "frigg.blender.get_bounding_box":
        args = arguments or {}
        response = call_bridge("get_bounding_box", args)
        return response

    if name == "frigg.blender.get_spatial_relationships":
        args = arguments or {}
        response = call_bridge("get_spatial_relationships", args)
        return response

    raise ValueError(f"Unknown tool: {name}")


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
            result = {"ok": False, "error": str(exc)}
        return jsonrpc_result(result, req_id)

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
