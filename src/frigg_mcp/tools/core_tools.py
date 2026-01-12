from typing import Any, Callable, Dict, List, Optional


def ok_result(result: Any) -> Dict[str, Any]:
    return {"ok": True, "result": result}


def error_result(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    error = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"ok": False, "error": error}


def _empty_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }


CORE_TOOL_DEFS: List[Dict[str, Any]] = [
    {
        "name": "frigg.ping",
        "description": "Simple ping without Blender.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "frigg.blender.bridge_ping",
        "description": "Ping the Blender bridge server.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "frigg.blender.get_scene_info",
        "description": "Get basic scene info from Blender.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "frigg.blender.list_objects",
        "description": "List all objects in the Blender file.",
        "inputSchema": _empty_schema(),
    },
    {
        "name": "frigg.blender.create_primitive",
        "description": "Create a primitive object (cube, sphere, cylinder, cone, torus, plane, monkey).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE", "MONKEY"],
                    "description": "Primitive type to create.",
                },
                "name": {"type": "string", "description": "Optional custom name."},
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Optional location [x, y, z].",
                },
                "rotation": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Optional rotation [x, y, z] in degrees.",
                },
                "scale": {
                    "description": "Optional scale (number for uniform, or [x, y, z]).",
                    "oneOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    ],
                },
                "size": {"type": "number", "minimum": 0, "description": "Optional size parameter."},
            },
            "required": ["type"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.delete_object",
        "description": "Delete an object from the scene.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Object to delete."}},
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.select_object",
        "description": "Select an object with a selection action.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object to select."},
                "action": {
                    "type": "string",
                    "enum": ["SET", "ADD", "REMOVE", "TOGGLE"],
                    "description": "Selection action.",
                    "default": "SET",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.get_transform",
        "description": "Get object transform (location, rotation, scale).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object name."},
                "space": {
                    "type": "string",
                    "enum": ["LOCAL", "WORLD"],
                    "description": "Transform space.",
                    "default": "LOCAL",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.set_transform",
        "description": "Set object transform (location, rotation, scale).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object name."},
                "space": {
                    "type": "string",
                    "enum": ["LOCAL", "WORLD"],
                    "description": "Transform space.",
                    "default": "LOCAL",
                },
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Location [x, y, z].",
                },
                "rotation": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Rotation [x, y, z].",
                },
                "rotation_mode": {
                    "type": "string",
                    "enum": ["DEGREES", "RADIANS"],
                    "description": "Rotation units.",
                    "default": "DEGREES",
                },
                "scale": {
                    "description": "Scale (number for uniform, or [x, y, z]).",
                    "oneOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                    ],
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.apply_transform",
        "description": "Apply transforms to an object (location, rotation, scale).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Object name."},
                "apply_location": {"type": "boolean", "default": True},
                "apply_rotation": {"type": "boolean", "default": True},
                "apply_scale": {"type": "boolean", "default": True},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.create_camera",
        "description": "Create a camera object.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Optional camera name."},
                "location": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Camera location [x, y, z].",
                },
                "rotation": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Camera rotation [x, y, z] in degrees.",
                },
                "projection": {
                    "type": "string",
                    "enum": ["PERSP", "ORTHO"],
                    "description": "Camera projection type.",
                    "default": "PERSP",
                },
                "focal_length": {"type": "number", "minimum": 0, "description": "Lens focal length."},
                "ortho_scale": {"type": "number", "minimum": 0, "description": "Orthographic scale."},
            },
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.set_active_camera",
        "description": "Set the active scene camera by name.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Camera object name."}},
            "required": ["name"],
            "additionalProperties": False,
        },
    },
]

CORE_TOOL_NAMES = {tool["name"] for tool in CORE_TOOL_DEFS}


def tools_list() -> Dict[str, Any]:
    return {"tools": CORE_TOOL_DEFS}


def _bridge_call(
    call_bridge: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    method: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        response = call_bridge(method, params)
    except Exception as exc:
        return error_result("bridge_error", str(exc))
    if response.get("ok") is True:
        return ok_result(response.get("result"))
    error = response.get("error")
    if isinstance(error, dict) and "code" in error and "message" in error:
        return {"ok": False, "error": error}
    return error_result("bridge_error", str(error) if error else "Unknown bridge error")


def handle_core_call(
    name: str,
    arguments: Optional[Dict[str, Any]],
    call_bridge: Callable[[str, Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    args = arguments or {}

    if name == "frigg.ping":
        return ok_result({"message": "pong"})

    if name == "frigg.blender.bridge_ping":
        return _bridge_call(call_bridge, "bridge_ping", {})

    if name == "frigg.blender.get_scene_info":
        return _bridge_call(call_bridge, "scene_info", {})

    if name == "frigg.blender.list_objects":
        return _bridge_call(call_bridge, "list_objects", {})

    if name == "frigg.blender.create_primitive":
        primitive_type = args.get("type")
        payload = {
            "primitive_type": primitive_type.lower() if isinstance(primitive_type, str) else primitive_type,
        }
        if args.get("name") is not None:
            payload["name"] = args.get("name")
        if args.get("location") is not None:
            payload["location"] = args.get("location")
        if args.get("rotation") is not None:
            payload["rotation"] = args.get("rotation")
        if args.get("scale") is not None:
            payload["scale"] = args.get("scale")
        if args.get("size") is not None:
            payload["size"] = args.get("size")
        return _bridge_call(call_bridge, "create_primitive", payload)

    if name == "frigg.blender.delete_object":
        return _bridge_call(call_bridge, "delete_object", {"object_name": args.get("name")})

    if name == "frigg.blender.select_object":
        payload = {"name": args.get("name"), "action": args.get("action", "SET")}
        return _bridge_call(call_bridge, "select_object", payload)

    if name == "frigg.blender.get_transform":
        payload = {"name": args.get("name"), "space": args.get("space", "LOCAL")}
        return _bridge_call(call_bridge, "get_transform", payload)

    if name == "frigg.blender.set_transform":
        payload = {
            "name": args.get("name"),
            "space": args.get("space", "LOCAL"),
            "location": args.get("location"),
            "rotation": args.get("rotation"),
            "rotation_mode": args.get("rotation_mode", "DEGREES"),
            "scale": args.get("scale"),
        }
        return _bridge_call(call_bridge, "set_transform", payload)

    if name == "frigg.blender.apply_transform":
        payload = {
            "name": args.get("name"),
            "apply_location": args.get("apply_location", True),
            "apply_rotation": args.get("apply_rotation", True),
            "apply_scale": args.get("apply_scale", True),
        }
        return _bridge_call(call_bridge, "apply_transform", payload)

    if name == "frigg.blender.create_camera":
        payload = {"projection": args.get("projection", "PERSP")}
        if args.get("name") is not None:
            payload["name"] = args.get("name")
        if args.get("location") is not None:
            payload["location"] = args.get("location")
        if args.get("rotation") is not None:
            payload["rotation"] = args.get("rotation")
        if args.get("focal_length") is not None:
            payload["focal_length"] = args.get("focal_length")
        if args.get("ortho_scale") is not None:
            payload["ortho_scale"] = args.get("ortho_scale")
        return _bridge_call(call_bridge, "create_camera", payload)

    if name == "frigg.blender.set_active_camera":
        return _bridge_call(call_bridge, "set_active_camera", {"name": args.get("name")})

    return error_result("unknown_tool", f"Unknown core tool: {name}")
